#!/usr/bin/env python3
"""Audit: Documentation and README sync check.

Verifies that human-facing documentation stays in sync with the codebase:

  1. README coverage  — every library in libs/ has a README.md
  2. @deps documents: links — rule/knowledge .md files that declare
     `documents: [path]` in their @deps frontmatter point to files that exist
  3. Doc backtick references — backtick-quoted Python identifiers and file
     paths in docs/**/*.qmd and libs/*/README.md that look like file paths
     are checked for existence on disk
  4. Violet Law references — `ClassName (filename.py)` patterns in .qmd files
     are checked: filename.py must exist somewhere under libs/ or app/

Run this after significant refactors, before releases, or when documentation
has not been touched for several weeks.

Usage:
  .venv/bin/python scripts/audit_docs_sync.py
  .venv/bin/python scripts/audit_docs_sync.py --output .claude/logs/audits/audit_docs_sync_2026-05-12.md
  .venv/bin/python scripts/audit_docs_sync.py --project-root /path/to/project --output report.md
  .venv/bin/python scripts/audit_docs_sync.py --skip-violet  # skip Violet Law check (slow on large doc trees)
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

LIBS_DIR = "libs"
DOCS_DIR = "docs"
RULES_DIR = ".claude/rules"
KNOWLEDGE_DIR = ".claude/knowledge"

# Pattern: backtick paths that look like project-relative file paths
BACKTICK_PATH_RE = re.compile(r"`([^`]+\.(?:py|yaml|yml|md|qmd|sh|json))`")

# Pattern: Violet Law references — "ClassName (filename.py)"
VIOLET_RE = re.compile(r"\b([A-Z][A-Za-z]+)\s+\(([a-z_][a-z0-9_]*\.py)\)")

# Pattern: @deps documents: entries in YAML frontmatter or inline @deps blocks
# Matches both frontmatter `documents: [path1, path2]` and inline `# documents: path`
DEPS_DOC_RE = re.compile(
    r"(?:documents:\s*\[([^\]]+)\]|#\s*documents:\s*(.+))"
)

IGNORE_PATH_PATTERNS = {
    "YYYY-MM-DD", "<", ">", "...", "example", "your_", "my_", "path/to",
    "name.py", "file.py",
}


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


# ── Check 1: README coverage ──────────────────────────────────────────────────

def check_readme_coverage(project_root: Path) -> list[dict]:
    libs_dir = project_root / LIBS_DIR
    missing = []
    for lib_dir in sorted(libs_dir.iterdir()):
        if not lib_dir.is_dir() or lib_dir.name.startswith("."):
            continue
        readme = lib_dir / "README.md"
        if not readme.exists():
            missing.append({
                "check": "README_MISSING",
                "path": str(lib_dir.relative_to(project_root)),
                "detail": f"libs/{lib_dir.name}/ has no README.md",
            })
    return missing


# ── Check 2: @deps documents: links ──────────────────────────────────────────

def check_deps_documents(project_root: Path) -> list[dict]:
    violations = []
    scan_dirs = [
        project_root / RULES_DIR,
        project_root / KNOWLEDGE_DIR,
    ]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            for m in DEPS_DOC_RE.finditer(text):
                raw = m.group(1) or m.group(2) or ""
                # Split on commas for list form
                entries = [e.strip().strip("'\"") for e in raw.split(",")]
                for entry in entries:
                    entry = entry.strip()
                    if not entry or entry == "—" or entry == "-":
                        continue
                    # Resolve relative to project root
                    target = project_root / entry
                    if not target.exists():
                        violations.append({
                            "check": "DEPS_DOC_BROKEN",
                            "path": str(md_file.relative_to(project_root)),
                            "detail": f"@deps `documents:` references missing file: `{entry}`",
                            "missing_file": entry,
                        })
    return violations


# ── Check 3: Backtick file path references in docs ───────────────────────────

def _is_ignorable(path_str: str) -> bool:
    return any(pat in path_str for pat in IGNORE_PATH_PATTERNS)


def check_doc_backtick_paths(project_root: Path) -> list[dict]:
    violations = []
    docs_dir = project_root / DOCS_DIR

    # Scan .qmd files and lib READMEs
    scan_files = list(docs_dir.rglob("*.qmd")) if docs_dir.exists() else []
    libs_dir = project_root / LIBS_DIR
    if libs_dir.exists():
        scan_files += [f for f in libs_dir.rglob("README.md")]

    seen = set()
    for doc_file in sorted(scan_files):
        try:
            text = doc_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in BACKTICK_PATH_RE.finditer(text):
            raw = m.group(1)
            if _is_ignorable(raw):
                continue
            # Only check paths that start with a known project root prefix
            if not any(raw.startswith(p) for p in (
                "libs/", "app/", "config/", "scripts/", "docs/",
                ".claude/", "assets/", "tests/"
            )):
                continue
            key = (str(doc_file.relative_to(project_root)), raw)
            if key in seen:
                continue
            seen.add(key)
            target = project_root / raw
            if not target.exists():
                violations.append({
                    "check": "DOC_PATH_BROKEN",
                    "path": str(doc_file.relative_to(project_root)),
                    "detail": f"Backtick path not found on disk: `{raw}`",
                    "missing_file": raw,
                })
    return violations


# ── Check 4: Violet Law references ───────────────────────────────────────────

def check_violet_law(project_root: Path) -> list[dict]:
    violations = []
    docs_dir = project_root / DOCS_DIR
    if not docs_dir.exists():
        return []

    # Build index of all .py filenames under libs/ and app/
    known_py_names: set[str] = set()
    for search_root in ["libs", "app"]:
        root = project_root / search_root
        if root.exists():
            for py_file in root.rglob("*.py"):
                known_py_names.add(py_file.name)

    seen = set()
    for qmd_file in sorted(docs_dir.rglob("*.qmd")):
        try:
            text = qmd_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in VIOLET_RE.finditer(text):
            class_name, filename = m.group(1), m.group(2)
            key = (str(qmd_file.relative_to(project_root)), filename)
            if key in seen:
                continue
            seen.add(key)
            if filename not in known_py_names:
                violations.append({
                    "check": "VIOLET_STALE",
                    "path": str(qmd_file.relative_to(project_root)),
                    "detail": (
                        f"Violet Law reference `{class_name} ({filename})` — "
                        f"`{filename}` not found under libs/ or app/"
                    ),
                    "missing_file": filename,
                })
    return violations


# ── Report ────────────────────────────────────────────────────────────────────

def render_report(
    readme_violations: list[dict],
    deps_violations: list[dict],
    path_violations: list[dict],
    violet_violations: list[dict],
    project_root: Path,
    skip_violet: bool,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    all_violations = readme_violations + deps_violations + path_violations + violet_violations
    total = len(all_violations)

    lines = [
        "# Audit Report: Documentation and README Sync",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: docs_documentation_aesthetics.md §1 — Code-Documentation Synchronization Mandate",
        "",
        f"- README coverage violations: {len(readme_violations)}",
        f"- @deps documents: broken links: {len(deps_violations)}",
        f"- Doc backtick path violations: {len(path_violations)}",
        f"- Violet Law stale references: {len(violet_violations)}"
        + (" (skipped)" if skip_violet else ""),
        f"- **Total violations: {total}**",
        "",
    ]

    if total == 0:
        lines += ["## Result: ✅ PASS", "", "All documentation checks pass.", ""]
    else:
        lines += ["## Result: ❌ FAIL", ""]

    def section(title: str, items: list[dict], fix_hint: str) -> list[str]:
        if not items:
            return [f"## ✅ {title} — No violations", ""]
        out = [f"## ❌ {title}", ""]
        for v in items:
            out += [
                f"- **`{v['path']}`**",
                f"  {v['detail']}",
                f"  *Fix: {fix_hint}*",
            ]
        return out + [""]

    lines += section(
        "README Coverage",
        readme_violations,
        "Add a README.md to the library directory. Use the Violet Law format for key components.",
    )
    lines += section(
        "@deps documents: Links",
        deps_violations,
        "Update the `documents:` entry in the @deps block to point to the correct (current) file path.",
    )
    lines += section(
        "Doc Backtick File Paths",
        path_violations,
        "Update the file reference in the doc. If the file was renamed, use the new path. "
        "If the file was deleted, remove or rewrite the paragraph.",
    )
    if not skip_violet:
        lines += section(
            "Violet Law Stale References",
            violet_violations,
            "Update `ClassName (filename.py)` to use the current filename. "
            "Violet Law applies to human-facing .qmd files only — not code.",
        )

    lines += [
        "## References",
        "- `rules_documentation_aesthetics.md §1` — Code-Documentation Synchronization Mandate",
        "- `rules_documentation_aesthetics.md §3` — The Violet Law",
        "- `workspace_standard.md §5` — @deps annotation format",
        "- Routine 9 (Documentation sync) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--skip-violet",
        action="store_true",
        help="Skip the Violet Law reference check (faster for large doc trees)",
    )
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )

    readme_v = check_readme_coverage(project_root)
    deps_v = check_deps_documents(project_root)
    path_v = check_doc_backtick_paths(project_root)
    violet_v = [] if args.skip_violet else check_violet_law(project_root)

    report = render_report(readme_v, deps_v, path_v, violet_v, project_root, args.skip_violet)
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    total = len(readme_v) + len(deps_v) + len(path_v) + len(violet_v)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
