# @deps
# provides: function:run_structure_check, function:could_not_run_result, class:StructureCheckError
# consumes: app/modules/error_notice.py, scripts/audit_data_analysis_recipe_coherence.py
# consumed_by: app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/decision_ledger.md (D-0050 no silent error), .claude/rules/rules_runtime_environment.md#5
# @end_deps
"""Runs the static structure check of Blueprint's "Validate" in a child process, and says so when it cannot run.

The child is started with the interpreter that runs the app (`sys.executable`), never with a path into `.venv`: a git
worktree, a container or a server install has no `.venv` in the working folder. The child imports the libraries of the
same checkout as the app (PYTHONPATH built from `libs/*/src` next to this file), and the script is found from the
location of this code, not from the current folder.

A check that could not run is not a check that failed (D-0050): `StructureCheckError` carries the plain text for the
user (what could not run, the reason, a "Suggestion:" line) and `could_not_run_result` turns it into the panel content.
Headless-safe: no Shiny imports.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.modules.error_notice import notice

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "audit_data_analysis_recipe_coherence.py"
PASS_MARK = "## Result:"
WHAT = "The structure check of the recipe could not run, so the recipe was neither passed nor failed"


class StructureCheckError(Exception):
    """The structure check did not run to the end. `str(error)` is the text the user reads."""


def child_env() -> dict:
    """os.environ with PYTHONPATH set to this checkout's sources (a caller's PYTHONPATH is kept after them)."""
    paths = [str(REPO), *(str(p) for p in sorted((REPO / "libs").glob("*/src")))]
    inherited = os.environ.get("PYTHONPATH")
    if inherited:
        paths.append(inherited)
    return {**os.environ, "PYTHONPATH": os.pathsep.join(paths)}


def structure_check_command(recipe_path: str) -> list:
    return [sys.executable, str(SCRIPT), "--data-analysis-recipe", str(recipe_path), "--skip-tsv"]


def run_structure_check(recipe_path: str, timeout: int = 30) -> str:
    """The report text of the check; raises StructureCheckError when it cannot start, times out or gives no report."""
    try:
        proc = subprocess.run(structure_check_command(recipe_path), capture_output=True, text=True,
                              timeout=timeout, cwd=str(REPO), env=child_env())
    except subprocess.TimeoutExpired as exc:
        raise StructureCheckError(notice(
            WHAT, f"run Validate again; if it keeps timing out after {timeout} seconds, check the recipe for a very "
                  "large include or ask the person who runs the app", f"timed out after {timeout} seconds")) from exc
    except OSError as exc:
        raise StructureCheckError(notice(
            WHAT, "check that the app was installed completely (the file scripts/audit_data_analysis_recipe_coherence.py "
                  "and the Python that runs the app), then run Validate again", exc)) from exc
    stdout = proc.stdout or ""
    if PASS_MARK not in stdout:
        tail = " ".join((proc.stderr or "").split())[-300:] or "it printed no report"
        raise StructureCheckError(notice(
            WHAT, "read the reason and fix it; if it names a missing package, the app installation is incomplete",
            f"the check ended with code {proc.returncode} and no readable report: {tail}"))
    return stdout


def could_not_run_result(recipe_path: str, error: StructureCheckError) -> dict:
    """The panel content for a check that could not run (not the content of a failed recipe)."""
    return {"pass": False, "could_not_run": str(error), "checks": [],
            "data_analysis_recipe_name": Path(recipe_path).name, "raw_text": "", "data_problems": []}
