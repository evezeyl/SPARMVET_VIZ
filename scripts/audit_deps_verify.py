#!/usr/bin/env python3
"""Audit: @deps block verification.

Scans all load-bearing Python files in libs/ and app/ to verify that each
carries a current @deps annotation block (ADR Session Law, workspace_standard.md §5).

A file is considered "load-bearing" if it contains @register_action,
@register_plot_component, or is a core module (data_assembler.py,
data_wrangler.py, ingestor.py, orchestrator.py, metadata_validator.py,
manifest_navigator.py, schema_registry.py, bootloader.py, sidebar_registry.py).

Usage:
  .venv/bin/python scripts/audit_deps_verify.py
  .venv/bin/python scripts/audit_deps_verify.py --output .claude/logs/audits/audit_deps_2026-05-12.md
  .venv/bin/python scripts/audit_deps_verify.py --project-root /path/to/project --output report.md
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

CORE_MODULES = {
    "data_assembler.py",
    "data_wrangler.py",
    "ingestor.py",
    "orchestrator.py",
    "metadata_validator.py",
    "manifest_navigator.py",
    "schema_registry.py",
    "bootloader.py",
    "sidebar_registry.py",
    "viz_factory.py",
}

REGISTRATION_MARKERS = [
    "@register_action(",
    "@register_plot_component(",
]

SEARCH_ROOTS = ["libs", "app"]
EXCLUDE_DIRS = {"__pycache__", ".venv", "tests", "tmp", "tmpAI", "assets"}


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def is_load_bearing(filepath: Path) -> bool:
    if filepath.name in CORE_MODULES:
        return True
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return any(marker in text for marker in REGISTRATION_MARKERS)


def has_deps_block(filepath: Path) -> bool:
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return "@deps" in text and "@end_deps" in text


def scan(project_root: Path) -> tuple[list[dict], list[dict]]:
    missing = []
    present = []

    for root_name in SEARCH_ROOTS:
        root = project_root / root_name
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if any(part in EXCLUDE_DIRS for part in py_file.parts):
                continue
            if not is_load_bearing(py_file):
                continue
            rel = py_file.relative_to(project_root)
            entry = {"file": str(rel)}
            if has_deps_block(py_file):
                present.append(entry)
            else:
                missing.append(entry)

    return missing, present


def render_report(missing: list[dict], present: list[dict], project_root: Path) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    total = len(missing) + len(present)

    lines = [
        "# Audit Report: @deps Block Verification",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Rule: workspace_standard.md §5 — @deps Session Law (Mandatory Maintenance Protocol)",
        "",
    ]

    if not missing:
        lines += [
            "## Result: ✅ PASS",
            "",
            f"All {total} load-bearing file(s) carry a @deps block.",
            "",
        ]
    else:
        lines += [
            "## Result: ❌ FAIL",
            "",
            f"- Load-bearing files scanned: {total}",
            f"- Files WITH @deps block: {len(present)}",
            f"- Files MISSING @deps block: {len(missing)}",
            "",
            "## ❌ Files Missing @deps Block (must fix)",
            "",
        ]
        for entry in missing:
            lines += [
                f"### {entry['file']}",
                "- **Action required:** Add a `@deps` block at module top (after imports).",
                "- **Format:**",
                "  ```",
                "  # @deps",
                "  # provides: <registration names or contracts exported>",
                "  # consumes: <dependencies>",
                "  # consumed_by: <files that import this>",
                "  # @end_deps",
                "  ```",
                "- See `workspace_standard.md §5-B` for full format by file type.",
                "",
            ]

    if present:
        lines += ["## ✅ Files With @deps Block", ""]
        for entry in present:
            lines += [f"- `{entry['file']}`"]
        lines += [""]

    lines += [
        "## References",
        "- `workspace_standard.md §5` — @deps annotation format, coupling keywords, maintenance protocol",
        "- `workspace_standard.md §5-E` — Mandatory Maintenance Protocol (SESSION LAW)",
        "- `.claude/knowledge/dependency_index.md` — Auto-generated from @deps by `build_dep_graph.py`",
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
    missing, present = scan(project_root)
    report = render_report(missing, present, project_root)

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
