#!/usr/bin/env python3
"""Audit: per-library test infrastructure completeness.

For each library in libs/ with a src/ subdirectory (proper editable package),
checks that the three test infrastructure layers are present and passing:
  1. pytest files (test_*.py)
  2. integrity suite (*_integrity_suite.py)
  3. debug runners (debug_*.py)

Reports per-library testability level:
  FULL    - all three layers present (and passing when tests are run)
  PARTIAL - has some test files but missing one or more layers (informational, not a blocker)
  MISSING - no tests/ directory or no test files at all (blocker)

Exit codes:
  0 - no MISSING libraries and no test failures
  1 - one or more MISSING libraries OR test failures detected

Usage:
  .venv/bin/python scripts/audit_library_tests.py
  .venv/bin/python scripts/audit_library_tests.py --output .claude/logs/audits/audit_library_tests_2026-05-09.md
  .venv/bin/python scripts/audit_library_tests.py --skip-suites
  .venv/bin/python scripts/audit_library_tests.py --skip-pytest
  .venv/bin/python scripts/audit_library_tests.py --lib transformer
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LIBS_DIR = "libs"
TIMEOUT_SECONDS = 120


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

    has_pytest = bool(pytest_files)
    has_suite = bool(suite_files)
    has_debug = bool(debug_scripts)

    if has_pytest and has_suite and has_debug:
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
        "has_tests_dir": tests_dir.exists(),
        "pytest_files": [f.name for f in pytest_files],
        "debug_scripts": [f.name for f in debug_scripts],
        "suite_files": [f.name for f in suite_files],
        "coverage_level": coverage_level,
        "missing_layers": missing_layers,
    }


# ── pytest run ────────────────────────────────────────────────────────────────

def run_pytest(python_bin: Path, lib_dir: Path, project_root: Path) -> tuple[int, str]:
    tests_dir = lib_dir / "tests"
    if not tests_dir.exists() or not list(tests_dir.glob("test_*.py")):
        return -1, "No pytest files found — skipped"

    try:
        result = subprocess.run(
            [str(python_bin), "-m", "pytest", str(tests_dir), "-q", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=TIMEOUT_SECONDS,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, f"TIMEOUT — pytest exceeded {TIMEOUT_SECONDS}s"


# ── Integrity suite run ────────────────────────────────────────────────────────

def run_suite(python_bin: Path, suite_path: Path, lib_name: str, project_root: Path) -> tuple[int, str]:
    out_dir = project_root / "tmpAI" / "audit_lib_tests" / lib_name
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [str(python_bin), str(suite_path), "--output", str(out_dir)],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=TIMEOUT_SECONDS,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output[-3000:] if len(output) > 3000 else output
    except subprocess.TimeoutExpired:
        return 1, f"TIMEOUT — integrity suite exceeded {TIMEOUT_SECONDS}s"


# ── Report ────────────────────────────────────────────────────────────────────

def status_icon(code: int) -> str:
    if code == -1:
        return "SKIP"
    return "PASS" if code == 0 else "FAIL"


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

    # A failure is a non-zero, non-skipped exit code
    pytest_failures = [r for r in results if r.get("pytest_code", -1) not in (-1, 0)]
    suite_failures = [r for r in results if r.get("suite_code", -1) not in (-1, 0)]

    overall_pass = not pytest_failures and not suite_failures and not missing_infra

    lines = [
        "# Audit Report: Library Test Infrastructure",
        f"Generated: {now}",
        f"Project root: {project_root}",
        "Rule: rules_verification_testing.md §1 — Standardized Test Naming and Architecture",
        "",
        f"- Libraries assessed: {len(results)}",
        f"- FULL (all three layers): {len(full_infra)}",
        f"- PARTIAL (missing one or more layers): {len(partial_infra)}",
        f"- MISSING (no tests at all): {len(missing_infra)}",
    ]

    if not skip_pytest:
        lines += [f"- pytest failures: {len(pytest_failures)}"]
    if not skip_suites:
        lines += [f"- Integrity suite failures: {len(suite_failures)}"]
    lines += [""]

    lines += [f"## Result: {'PASS' if overall_pass else 'FAIL'}", ""]

    # Infrastructure matrix
    lines += [
        "## Infrastructure Matrix",
        "",
        "| Library | pytest files | Integrity Suite | Debug Scripts | Level | pytest | Suite |",
        "|---------|-------------|-----------------|---------------|-------|--------|-------|",
    ]
    for r in results:
        infra = r["infra"]
        pytest_count = len(infra["pytest_files"])
        suite_count = len(infra["suite_files"])
        debug_count = len(infra["debug_scripts"])

        if skip_pytest:
            pytest_result = "skipped"
        else:
            pytest_result = status_icon(r.get("pytest_code", -1))

        if skip_suites:
            suite_result = "skipped"
        else:
            suite_result = status_icon(r.get("suite_code", -1))

        lines.append(
            f"| `{r['lib']}` "
            f"| {pytest_count} "
            f"| {suite_count} "
            f"| {debug_count} "
            f"| {infra['coverage_level']} "
            f"| {pytest_result} "
            f"| {suite_result} |"
        )
    lines += [""]

    # Per-library details
    lines += ["## Per-Library Details", ""]
    for r in results:
        infra = r["infra"]
        lines += [
            f"### {r['lib']}",
            "",
            f"- Level: **{infra['coverage_level']}**",
            f"- pytest files: {', '.join(infra['pytest_files']) if infra['pytest_files'] else 'none'}",
            f"- Integrity suites: {', '.join(infra['suite_files']) if infra['suite_files'] else 'none'}",
            f"- Debug scripts: {', '.join(infra['debug_scripts']) if infra['debug_scripts'] else 'none'}",
        ]
        if infra["missing_layers"]:
            lines += ["- Missing layers:"]
            for layer in infra["missing_layers"]:
                lines += [f"  - {layer}"]
        lines += [""]

        if not skip_pytest and "pytest_code" in r:
            code = r["pytest_code"]
            label = status_icon(code)
            lines += [f"#### pytest: {label}", ""]
            if r.get("pytest_output"):
                lines += ["```", r["pytest_output"][-1500:], "```", ""]

        if not skip_suites and "suite_code" in r:
            code = r["suite_code"]
            label = status_icon(code)
            suite_name = infra["suite_files"][0] if infra["suite_files"] else "none"
            lines += [f"#### Integrity suite `{suite_name}`: {label}", ""]
            if r.get("suite_output"):
                lines += ["```", r["suite_output"][-2000:], "```", ""]

    # Findings sections
    if missing_infra:
        lines += ["## MISSING Libraries (blockers)", ""]
        for r in missing_infra:
            lines += [
                f"- `{r['lib']}` — no test infrastructure found.",
                "  Add a `tests/` directory with at least one `test_*.py` file.",
            ]
        lines += [""]

    if partial_infra:
        lines += ["## PARTIAL Libraries (informational — not a blocker)", ""]
        for r in partial_infra:
            items = r["infra"]["missing_layers"]
            lines += [f"- `{r['lib']}`: {'; '.join(items)}"]
        lines += [
            "",
            "PARTIAL is informational only. File a `@dasharch` handoff in `tasks.md` to",
            "add missing layers when time allows. See `rules_verification_testing.md §1`.",
            "",
        ]

    if pytest_failures or suite_failures:
        lines += ["## Test Failures", ""]
        for r in pytest_failures:
            lines += [f"- `{r['lib']}`: pytest exited {r['pytest_code']}"]
        for r in suite_failures:
            lines += [f"- `{r['lib']}`: integrity suite exited {r['suite_code']}"]
        lines += [""]

    lines += [
        "## References",
        "- `.claude/rules/rules_verification_testing.md §1` — Standardized Test Naming and Architecture",
        "- `.claude/rules/rules_verification_testing.md §3` — @verify Protocol and Phase-Gating",
        "- `.claude/rules/rules_verification_testing.md §7` — Failure Test Mandate (ADR-034)",
        "- `.claude/workflows/audit_routine_registry.md` — scheduled audit registry",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root directory (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write report to this file in addition to stdout",
    )
    parser.add_argument(
        "--lib",
        default=None,
        metavar="NAME",
        help="Audit a single library by name (e.g. transformer)",
    )
    parser.add_argument(
        "--skip-suites",
        action="store_true",
        help="Check infrastructure only; do not execute integrity suites",
    )
    parser.add_argument(
        "--skip-pytest",
        action="store_true",
        help="Skip all test execution — infrastructure check only (fastest)",
    )
    args = parser.parse_args()

    project_root = (
        Path(args.project_root)
        if args.project_root
        else find_project_root(Path(__file__).resolve().parent)
    )
    python_bin = project_root / ".venv" / "bin" / "python"
    libs_dir = project_root / LIBS_DIR

    # Only scan directories with a src/ subdirectory (proper editable packages).
    if args.lib:
        lib_dirs = [libs_dir / args.lib]
    else:
        lib_dirs = sorted(
            d for d in libs_dir.iterdir()
            if d.is_dir() and (d / "src").is_dir()
        )

    results = []
    for lib_dir in lib_dirs:
        lib_name = lib_dir.name
        print(f"Assessing {lib_name} ...", file=sys.stderr)
        entry: dict = {"lib": lib_name, "infra": assess_infrastructure(lib_dir)}

        if not args.skip_pytest:
            print(f"  Running pytest for {lib_name} ...", file=sys.stderr)
            code, output = run_pytest(python_bin, lib_dir, project_root)
            entry["pytest_code"] = code
            entry["pytest_output"] = output

        if not args.skip_suites:
            suite_files = (
                list((lib_dir / "tests").glob("*_integrity_suite.py"))
                if (lib_dir / "tests").exists()
                else []
            )
            if suite_files:
                print(f"  Running integrity suite for {lib_name} ...", file=sys.stderr)
                code, output = run_suite(python_bin, suite_files[0], lib_name, project_root)
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
        r.get("pytest_code", -1) not in (-1, 0) or r.get("suite_code", -1) not in (-1, 0)
        for r in results
    )
    has_missing = any(r["infra"]["coverage_level"] == "MISSING" for r in results)
    return 1 if (has_failures or has_missing) else 0


if __name__ == "__main__":
    sys.exit(main())
