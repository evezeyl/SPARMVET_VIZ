"""Blueprint's Validate: the child process uses the running interpreter, and a check that cannot run says so (D-0050)."""
import subprocess
import sys
from pathlib import Path

import pytest

from app.modules import validate_runner as vr

RECIPE = Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes" / "pipelines"


def _any_recipe() -> str:
    found = sorted(RECIPE.glob("*.yaml"))
    assert found, "no shipped recipe to check"
    return str(found[0])


def test_command_uses_the_running_interpreter_not_a_venv_path():
    cmd = vr.structure_check_command("x.yaml")
    assert cmd[0] == sys.executable
    assert ".venv" not in cmd[0] or cmd[0] == sys.executable
    assert Path(cmd[1]).is_absolute() and Path(cmd[1]).exists()


def test_runs_from_a_folder_without_venv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no .venv, no scripts/ here
    out = vr.run_structure_check(_any_recipe())
    assert vr.PASS_MARK in out


def test_child_env_names_this_checkouts_libs():
    paths = vr.child_env()["PYTHONPATH"].split(":")
    assert str(vr.REPO) in paths
    assert str(vr.REPO / "libs" / "utils" / "src") in paths


def test_missing_script_is_reported_in_plain_words(monkeypatch):
    monkeypatch.setattr(vr, "structure_check_command", lambda p: ["/nonexistent/python", "x"])
    with pytest.raises(vr.StructureCheckError) as e:
        vr.run_structure_check("r.yaml")
    text = str(e.value)
    assert "could not run" in text and "neither passed nor failed" in text
    assert "Suggestion:" in text and "FileNotFoundError" in text


def test_timeout_is_reported(monkeypatch):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired("c", 1)
    monkeypatch.setattr(vr.subprocess, "run", boom)
    with pytest.raises(vr.StructureCheckError) as e:
        vr.run_structure_check("r.yaml", timeout=7)
    assert "timed out after 7 seconds" in str(e.value) and "Suggestion:" in str(e.value)


def test_unreadable_output_is_reported_with_the_reason(monkeypatch):
    done = subprocess.CompletedProcess([], 1, stdout="", stderr="ModuleNotFoundError: No module named 'transformer'")
    monkeypatch.setattr(vr.subprocess, "run", lambda *a, **k: done)
    with pytest.raises(vr.StructureCheckError) as e:
        vr.run_structure_check("r.yaml")
    assert "No module named 'transformer'" in str(e.value) and "Suggestion:" in str(e.value)


def test_panel_content_is_not_a_failed_recipe():
    err = vr.StructureCheckError("It could not run. Suggestion: do x")
    res = vr.could_not_run_result("/a/b/recipe.yaml", err)
    assert res["could_not_run"] == str(err) and res["checks"] == [] and res["data_analysis_recipe_name"] == "recipe.yaml"
