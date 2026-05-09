#!/usr/bin/env python3
"""Audit: Library test coverage and testability check.

For each library in libs/, verifies that the test infrastructure is complete
and that all tests pass. Reports three things:

  1. Infrastructure completeness — does the library have unit tests (pytest),
     an integrity suite (*_integrity_suite.py), and debug scripts (debug_*.py)?
  2. pytest results — runs pytest on the library's tests/ directory
  3. Integrity suite results — runs the *_integrity_suite.py wrapper if present

A library is FULLY TESTABLE when it has at least one pytest file AND at least
one integrity suite or debug script, and all of them pass.

Libraries missing test infrastructure are flagged as PARTIAL or MISSING — these
require a @dasharch handoff to add the missing layer before the library can be
considered production-ready.

This audit is intentionally slow (it runs the full test suite). Run on-demand
before releases or after significant library changes, not on every commit.

Usage:
  .venv/bin/python scripts/audit_library_tests.py
  .venv/bin/python scripts/audit_library_tests.py --output .claude/logs/audits/audit_library_tests_2026-05-12.md
  .venv/bin/python scripts/audit_library_tests.py --lib transformer   # single library only
  .venv/bin/python scripts/audit_library_tests.py --skip-suites       # pytest only (faster)
  .venv/bin/python scripts/audit_library_tests.py --skip-pytest       # infra check only (fastest)
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LIBS_DIR = "libs"
PYTEST_TIMEOUT = 120   # seconds per library
SUITE_TIMEOUT = 180    # integrity suites can be slower


def find_project_root(start: Path) -> Path:
    for parent in [start] + list(start.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".venv").exists():
            return parent
    return start


# ── Infrastructure check ──────────────────────────────────────────────────────

def assess_infrastructure(lib_dir: Path) -> dict:
    tests_dir = lib_dir / "tests"
    pytest_files = sorted(tests_dir.glob("test_*.py")) if tests_dir.exists() else []
    debug_scripts = sorted(tests_dir.glob("debug_*.py")) if tests_dir.exists() else []
    suite_files = sorted(tests_dir.glob("*_integrity_suite.py")) if tests_dir.exists() else []

    has_tests_dir = tests_dir.exists()
    has_pytest = len(pytest_files) > 0
    has_suite = len(suite_files) > 0
    has_debug = len(debug_scripts) > 0

    if has_pytest and (has_suite or has_debug):
        coverage_level = "FULL"
    elif has_pytest or has_suite or has_debug:
        coverage_level = "PARTIAL"
    else:
        coverage_level = "MISSING"

    missing_layers = []
    if not has_pytest:
        missing_layers.append("pytest unit tests (test_*.py)")
    if not has_suite:
        missing_layers.append("integrity suite (*_integrity_suite.py)")
    if not has_debug:
        missing_layers.append("debug scripts (debug_*.py)")

    return {
        "has_tests_dir": has_tests_dir,
        "pytest_files": [str(f.relative_to(lib_dir)) for f in pytest_files],
        "debug_scripts": [str(f.relative_to(lib_dir)) for f in debug_scripts],
        "suite_files": [str(f.relative_to(lib_dir)) for f in suite_files],
        "coverage_level": coverage_level,
        "missing_layers": missing_layers,
    }


# ── pytest run ────────────────────────────────────────────────────────────────

def run_pytest(python_bin: Path, lib_dir: Path, project_root: Path) -> tuple[int, str]:
    tests_dir = lib_dir / "tests"
    if not tests_dir.exists() or not list(tests_dir.glob("test_*.py")):
        return -1, "No pytest files found — skipped"

    result = subprocess.run(
        [
            str(python_bin), "-m", "pytest",
            str(tests_dir),
            "-q", "--tb=short", "--no-header",
            f"--timeout={PYTEST_TIMEOUT}",
        ],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=PYTEST_TIMEOUT + 30,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


# ── Integrity suite run ────────────────────────────────────────────────────────

def run_suite(python_bin: Path, suite_path: Path, project_root: Path) -> tuple[int, str]:
    result = subprocess.run(
        [str(python_bin), str(suite_path)],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=SUITE_TIMEOUT + 30,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output[-3000:] if len(output) > 3000 else output


# ── Report ────────────────────────────────────────────────────────────────────

def status_icon(code: int) -> str:
    if code == -1:
        return "⬜ SKIP"
    return "✅ PASS" if code == 0 else "❌ FAIL"


def render_report(
    results: list[dict],
    project_root: Path,
    skip_suites: bool,
    skip_pytest: bool,
) -> str:
    now = datetime.now().isoformat(timespec="seconds")

    full_infra = [r for r in results if r["infra"]["coverage_level"] == "FULL"]
    partial_infra = [r for r in results if r["infra"]["coverage_level"] == "PARTIAL"]
    missing_infra = [r for r in results if r["infra"]["coverage_level"] == "MISSING"]

    pytest_failures = [r for r in results if r.get("pytest_code", -1) == 1]
    suite_failures = [r for r in results if r.get("suite_code", -1) == 1]

    overall_pass = not pytest_failures and not suite_failures and not missing_infra

    lines = [
        "# Audit Report: Library Test Coverage and Testability",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: rules_verification_testing.md §1 — Standardized Test Architecture",
        "",
        f"- Libraries assessed: {len(results)}",
        f"- FULL test infrastructure: {len(full_infra)}",
        f"- PARTIAL test infrastructure: {len(partial_infra)}",
        f"- MISSING test infrastructure: {len(missing_infra)}",
        "",
    ]

    if not skip_pytest:
        lines += [
            f"- pytest failures: {len(pytest_failures)}",
        ]
    if not skip_suites:
        lines += [
            f"- Integrity suite failures: {len(suite_failures)}",
        ]
    lines += [""]

    lines += [f"## Result: {'✅ PASS' if overall_pass else '❌ FAIL'}", ""]

    # Infrastructure matrix
    lines += [
        "## Infrastructure Matrix",
        "",
        "| Library | pytest | Integrity Suite | Debug Scripts | Level |",
        "|---------|--------|----------------|---------------|-------|",
    ]
    for r in results:
        infra = r["infra"]
        pytest_count = len(infra["pytest_files"])
        suite_count = len(infra["suite_files"])
        debug_count = len(infra["debug_scripts"])
        level_icon = {"FULL": "✅", "PARTIAL": "⚠️", "MISSING": "❌"}[infra["coverage_level"]]
        lines.append(
            f"| `{r['lib']}` "
            f"| {'✅' if pytest_count else '❌'} {pytest_count} file(s) "
            f"| {'✅' if suite_count else '❌'} {suite_count} suite(s) "
            f"| {'✅' if debug_count else '❌'} {debug_count} script(s) "
            f"| {level_icon} {infra['coverage_level']} |"
        )
    lines += [""]

    # Missing infrastructure tasks
    if missing_infra or partial_infra:
        lines += ["## ⚠️ Missing Test Infrastructure", ""]
        for r in missing_infra + partial_infra:
            infra = r["infra"]
            lines += [
                f"### `{r['lib']}` — {infra['coverage_level']}",
                "Missing layers:",
            ]
            for layer in infra["missing_layers"]:
                lines += [f"- {layer}"]
            lines += [
                "",
                "**Action:** File a `@dasharch` handoff in `tasks.md` to add the missing layer.",
                "See `rules_verification_testing.md §1` for the naming standard.",
                "",
            ]

    # Test run results
    if not skip_pytest:
        lines += ["## pytest Results", ""]
        for r in results:
            code = r.get("pytest_code", -1)
            icon = status_icon(code)
            lines += [f"### `{r['lib']}` — {icon}"]
            if code not in (-1,) and r.get("pytest_output"):
                lines += ["```", r["pytest_output"][-1500:], "```"]
            lines += [""]

    if not skip_suites:
        lines += ["## Integrity Suite Results", ""]
        for r in results:
            code = r.get("suite_code", -1)
            icon = status_icon(code)
            suite_name = r["infra"]["suite_files"][0] if r["infra"]["suite_files"] else "—"
            lines += [f"### `{r['lib']}` — {icon} ({suite_name})"]
            if code not in (-1,) and r.get("suite_output"):
                lines += ["```", r["suite_output"][-2000:], "```"]
            lines += [""]

    lines += [
        "## References",
        "- `rules_verification_testing.md §1` — Standardized Test Naming & Architecture",
        "- `rules_verification_testing.md §3` — @verify Protocol & Phase-Gating",
        "- `rules_verification_testing.md §7` — Failure Test Mandate (ADR-034)",
        "- Routine 10 (Library test coverage) in `.claude/workflows/audit_routine_registry.md`",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--lib", default=None, help="Run against a single library only")
    parser.add_argument("--skip-suites", action="store_true", help="Skip integrity suite runs")
    parser.add_argument("--skip-pytest", action="store_true", help="Infrastructure check only, no test execution")
    args = parser.parse_args()

    project_root = (
        Path(args.project_root) if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )
    python_bin = project_root / ".venv" / "bin" / "python"
    libs_dir = project_root / LIBS_DIR

    lib_dirs = (
        [libs_dir / args.lib] if args.lib
        else sorted(d for d in libs_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
    )

    results = []
    for lib_dir in lib_dirs:
        lib_name = lib_dir.name
        print(f"Assessing {lib_name} ...", file=sys.stderr)
        entry: dict = {"lib": lib_name, "infra": assess_infrastructure(lib_dir)}

        if not args.skip_pytest:
            print(f"  Running pytest for {lib_name} ...", file=sys.stderr)
            try:
                code, output = run_pytest(python_bin, lib_dir, project_root)
            except subprocess.TimeoutExpired:
                code, output = 1, "TIMEOUT — pytest exceeded limit"
            entry["pytest_code"] = code
            entry["pytest_output"] = output

        if not args.skip_suites:
            suite_files = list((lib_dir / "tests").glob("*_integrity_suite.py")) if (lib_dir / "tests").exists() else []
            if suite_files:
                print(f"  Running integrity suite for {lib_name} ...", file=sys.stderr)
                try:
                    code, output = run_suite(python_bin, suite_files[0], project_root)
                except subprocess.TimeoutExpired:
                    code, output = 1, "TIMEOUT — suite exceeded limit"
                entry["suite_code"] = code
                entry["suite_output"] = output
            else:
                entry["suite_code"] = -1
                entry["suite_output"] = ""

        results.append(entry)

    report = render_report(results, project_root, args.skip_suites, args.skip_pytest)
    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {output_path}", file=sys.stderr)

    has_failures = any(
        r.get("pytest_code", 0) == 1 or r.get("suite_code", 0) == 1
        for r in results
    )
    has_missing = any(r["infra"]["coverage_level"] == "MISSING" for r in results)
    return 1 if (has_failures or has_missing) else 0


if __name__ == "__main__":
    sys.exit(main())
