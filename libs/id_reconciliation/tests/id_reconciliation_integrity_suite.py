"""
id_reconciliation integrity suite — orchestrator for all library modules.

Dispatches to module-specific test suites and reports a unified summary.

Usage:
    .venv/bin/python libs/id_reconciliation/tests/id_reconciliation_integrity_suite.py
    .venv/bin/python libs/id_reconciliation/tests/id_reconciliation_integrity_suite.py --module matcher
    .venv/bin/python libs/id_reconciliation/tests/id_reconciliation_integrity_suite.py --verbose
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
# Project root is 4 levels up from tests/: tests/ → id_reconciliation/ → src/ → libs/ → root
# But tests/ is directly under libs/id_reconciliation/, so root is parents[3]
VENV_PYTEST = Path(__file__).parents[3] / ".venv" / "bin" / "python"

MODULE_MAP = {
    "matcher": TESTS_DIR / "test_matcher.py",
    "pattern_detector": TESTS_DIR / "test_pattern_detector.py",
    "recipe": TESTS_DIR / "test_recipe.py",
    "core": TESTS_DIR / "test_core.py",
}


def run_module(name: str, path: Path, verbose: bool) -> bool:
    flags = ["-v"] if verbose else ["-q"]
    result = subprocess.run(
        [str(VENV_PYTEST), "-m", "pytest", str(path)] + flags,
        capture_output=not verbose,
        text=True,
    )
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"  {status}  {name}")
    if result.returncode != 0 and not verbose:
        print(result.stdout[-2000:] if result.stdout else "")
        print(result.stderr[-1000:] if result.stderr else "")
    return result.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "id_reconciliation integrity suite. Runs all module tests and "
            "reports pass/fail per module. Use --module to target one module."
        )
    )
    parser.add_argument(
        "--module",
        choices=list(MODULE_MAP),
        help="Run only this module's tests (default: all).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Pass -v to pytest for full test output.",
    )
    args = parser.parse_args()

    targets = (
        {args.module: MODULE_MAP[args.module]}
        if args.module
        else MODULE_MAP
    )

    print("\n=== id_reconciliation integrity suite ===")
    results = {name: run_module(name, path, args.verbose) for name, path in targets.items()}
    passed = sum(results.values())
    total = len(results)
    print(f"\n{passed}/{total} modules passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
