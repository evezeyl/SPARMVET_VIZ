#!/usr/bin/env python3
"""Audit: ADR-011 cross-lib violation scan.

Detects peer-to-peer imports between domain libraries in libs/.
Each domain library must only import from libs/utils/ (Tier 1 base) or stdlib.
Importing from another domain library (e.g. transformer → ingestion) is a
Two-Tier Dependency Model violation (ADR-011, ADR-016).

Usage:
  .venv/bin/python scripts/audit_cross_lib.py
  .venv/bin/python scripts/audit_cross_lib.py --output .claude/logs/audits/audit_cross_lib_2026-05-12.md
  .venv/bin/python scripts/audit_cross_lib.py --project-root /path/to/project --output report.md
"""
import argparse
import ast
import sys
from datetime import datetime
from pathlib import Path


# Domain libraries: peer-to-peer imports between these are forbidden.
# libs/utils is the allowed Tier 1 base — any lib may import from it.
DOMAIN_LIBS = {
    "blueprint_arch",
    "connector",
    "ingestion",
    "test_lab",
    "transformer",
    "viz_factory",
    "viz_gallery",
}
TIER1_BASE = "utils"

# Known existing violations (tech debt — do not remove entries until fixed)
KNOWN_VIOLATIONS = {
    # ("from_lib", "to_lib", substring_in_import)
    ("transformer", "ingestion"),
    ("blueprint_arch", "utils"),  # utils imports are now allowed — re-check if this shows
}


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


def extract_imports(filepath: Path) -> list[tuple[int, str]]:
    """Return list of (line_number, module_string) for all imports in file."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                results.append((node.lineno, node.module))
    return results


def lib_from_path(path: Path, libs_dir: Path) -> str | None:
    """Return the library name (e.g. 'transformer') for a file inside libs/."""
    try:
        rel = path.relative_to(libs_dir)
        return rel.parts[0]
    except ValueError:
        return None


def module_targets_lib(module: str) -> str | None:
    """Return the domain lib name if a module string targets a domain lib, else None."""
    for lib in DOMAIN_LIBS:
        if module == lib or module.startswith(lib + "."):
            return lib
    return None


def scan(project_root: Path) -> list[dict]:
    libs_dir = project_root / "libs"
    violations = []

    for py_file in sorted(libs_dir.rglob("*.py")):
        from_lib = lib_from_path(py_file, libs_dir)
        if from_lib not in DOMAIN_LIBS:
            continue

        for lineno, module in extract_imports(py_file):
            to_lib = module_targets_lib(module)
            if to_lib is None:
                continue
            if to_lib == from_lib:
                continue  # self-import is fine
            if to_lib == TIER1_BASE:
                continue  # importing from utils is allowed

            is_known = (from_lib, to_lib) in KNOWN_VIOLATIONS
            violations.append({
                "file": str(py_file.relative_to(project_root)),
                "line": lineno,
                "from_lib": from_lib,
                "to_lib": to_lib,
                "import": module,
                "severity": "KNOWN_DEBT" if is_known else "BLOCKER",
            })

    return violations


def render_report(violations: list[dict], project_root: Path) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    new_violations = [v for v in violations if v["severity"] == "BLOCKER"]
    known = [v for v in violations if v["severity"] == "KNOWN_DEBT"]

    lines = [
        "# Audit Report: ADR-011 Cross-Lib Violation Scan",
        f"Generated: {now}",
        f"Project root: {project_root}",
        f"Rule: ADR-011 / ADR-016 — Two-Tier Dependency Model",
        "",
    ]

    if not violations:
        lines += ["## Result: ✅ PASS", "", "No cross-lib violations found.", ""]
    else:
        status = "❌ FAIL" if new_violations else "⚠️ KNOWN DEBT ONLY"
        lines += [
            f"## Result: {status}",
            f"",
            f"- New violations (blockers): {len(new_violations)}",
            f"- Known tech-debt violations: {len(known)}",
            "",
        ]

    if new_violations:
        lines += ["## ❌ New Violations (must fix before merge)", ""]
        for v in new_violations:
            lines += [
                f"### {v['file']}:{v['line']}",
                f"- **From:** `{v['from_lib']}`",
                f"- **Imports:** `{v['to_lib']}` via `{v['import']}`",
                f"- **Fix:** Remove or reroute this import. Domain libs must not import from peers.",
                f"  - If you need shared logic, move it to `libs/utils/`.",
                f"  - If this is orchestration, move the call to `app/`.",
                "",
            ]

    if known:
        lines += ["## ⚠️ Known Tech-Debt Violations (tracked, do not expand)", ""]
        for v in known:
            lines += [
                f"- `{v['file']}:{v['line']}` — `{v['from_lib']}` → `{v['to_lib']}` (`{v['import']}`)",
            ]
        lines += ["", "These are tracked in tasks.md. Do not add new violations to this category.", ""]

    lines += [
        "## References",
        "- `.claude/rules/rules_runtime_environment.md §4` — Two-Tier Dependency Model",
        "- `.claude/knowledge/architecture_decisions.md` ADR-011, ADR-016",
        "- `.claude/tasks/tasks.md` — `ADR-011 cross-lib violations` tech-debt block",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=None, help="Project root directory (default: auto-detect)")
    parser.add_argument("--output", default=None, help="Write report to this file (default: stdout only)")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else find_project_root(Path(__file__).resolve().parent)
    violations = scan(project_root)
    report = render_report(violations, project_root)

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    new_violations = [v for v in violations if v["severity"] == "BLOCKER"]
    return 1 if new_violations else 0


if __name__ == "__main__":
    sys.exit(main())
