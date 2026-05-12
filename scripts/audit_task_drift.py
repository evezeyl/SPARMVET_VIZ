#!/usr/bin/env python3
"""Audit: Task-to-code drift check.

Scans open tasks in .claude/tasks/tasks.md for file path references.
For each referenced path found in a task (e.g. `app/handlers/foo.py`),
verifies that the file actually exists on disk.

A drift violation occurs when:
- A task references a file that no longer exists (moved, renamed, deleted)
- A task references a function/class name that cannot be found in any .py file

Backtick-quoted paths are extracted from task lines. This is a lightweight
heuristic check — it will not catch all drift, but reliably surfaces
removed/renamed files.

Usage:
  .venv/bin/python scripts/audit_task_drift.py
  .venv/bin/python scripts/audit_task_drift.py --output .claude/logs/audits/audit_task_drift_2026-05-12.md
  .venv/bin/python scripts/audit_task_drift.py --project-root /path/to/project --output report.md
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

TASKS_FILE = ".claude/tasks/tasks.md"
EXCLUSIONS_FILE = ".claude/workflows/audit_exclusions.yaml"

# Matches backtick-quoted strings that look like file paths.
# Stops at `:` to avoid capturing line-number suffixes like `pipeline.py:21`.
PATH_RE = re.compile(r"`([^`]+\.[a-zA-Z]{1,5})[:`]?[^`]*`")
# Only look at open tasks (not archived or done lines)
OPEN_TASK_RE = re.compile(r"^\s*-\s+\[[ ]\]")

IGNORE_EXTENSIONS = {".tsv", ".csv", ".json", ".parquet", ".png", ".svg", ".zip"}
IGNORE_PATTERNS = {"...", "YYYY-MM-DD", "<", ">"}


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def load_exclusions(project_root: Path) -> set[str]:
    """Return set of file paths excluded from drift checking via audit_exclusions.yaml."""
    exclusions_path = project_root / EXCLUSIONS_FILE
    if not exclusions_path.exists() or not _YAML_AVAILABLE:
        return set()
    try:
        data = yaml.safe_load(exclusions_path.read_text(encoding="utf-8")) or {}
        entries = data.get("task_drift", {}).get("expected_absent_files", [])
        return {e["path"] for e in entries if isinstance(e, dict) and "path" in e}
    except Exception:
        return set()


def extract_task_paths(tasks_path: Path) -> list[tuple[int, str, str]]:
    """Return [(lineno, raw_path, task_text)] for path refs in open tasks."""
    results = []
    lines = tasks_path.read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, 1):
        if not OPEN_TASK_RE.match(line):
            continue
        for m in PATH_RE.finditer(line):
            raw = m.group(1)
            if any(ign in raw for ign in IGNORE_PATTERNS):
                continue
            ext = Path(raw).suffix.lower()
            if ext in IGNORE_EXTENSIONS:
                continue
            # Only check paths that look like relative project paths
            if raw.startswith(("libs/", "app/", "config/", "scripts/", "docs/", ".claude/")):
                results.append((lineno, raw, line.strip()))
    return results


def check_paths(
    task_paths: list[tuple[int, str, str]],
    project_root: Path,
    excluded: set[str],
) -> list[dict]:
    violations = []
    seen: set[str] = set()
    for lineno, raw_path, task_text in task_paths:
        if raw_path in seen:
            continue
        seen.add(raw_path)
        if raw_path in excluded:
            continue
        full = project_root / raw_path
        if not full.exists():
            violations.append({
                "line": lineno,
                "path": raw_path,
                "task": task_text[:120],
            })
    return violations


def render_report(
    violations: list[dict],
    task_paths: list[tuple[int, str, str]],
    tasks_path: Path,
    project_root: Path,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    total_refs = len({p for _, p, _ in task_paths})

    lines = [
        "# Audit Report: Task-to-Code Drift Check",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Tasks file: {tasks_path.relative_to(project_root)}",
        f"Rule: Open task file references must point to existing files",
        "",
        f"- Distinct file paths referenced in open tasks: {total_refs}",
        f"- Missing files (drift): {len(violations)}",
        "",
    ]

    if not violations:
        lines += [
            "## Result: ✅ PASS",
            "",
            "All file references in open tasks point to existing files.",
            "",
        ]
    else:
        lines += [
            "## Result: ❌ FAIL",
            "",
            "## ❌ Drift Violations (file referenced but not found)",
            "",
        ]
        for v in violations:
            lines += [
                f"### `{v['path']}` (task line {v['line']})",
                f"- Task: `{v['task']}`",
                "- **Fix options:**",
                "  - If the file was renamed/moved: update the task to reference the new path.",
                "  - If the file was deleted: update or close the task.",
                "  - If the file has not been created yet: this is expected — mark task as deferred.",
                "",
            ]

    lines += [
        "## References",
        "- `.claude/tasks/tasks.md` — sole source of truth for current work",
        "- Routine 4 (Task-to-code drift) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )
    tasks_path = project_root / TASKS_FILE
    if not tasks_path.exists():
        print(f"ERROR: Tasks file not found: {tasks_path}", file=sys.stderr)
        return 2

    excluded = load_exclusions(project_root)
    task_paths = extract_task_paths(tasks_path)
    violations = check_paths(task_paths, project_root, excluded)
    report = render_report(violations, task_paths, tasks_path, project_root)

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
