"""The two scripts that judge recipes with the catalogs of the app work with and without `PYTHONPATH=.` (D-0050, D-0099).

They read the actions and plot components from the app layer, which Python finds only from the project root with
`PYTHONPATH=.`. Without it a raw `ModuleNotFoundError: No module named 'app'` was shown, even for `--help`. Now `--help`
works without it, and a run without it says what is missing and the command to type ("what happens, then Suggestion:").
Each script is run as a real subprocess. The hint that the gallery check prints names a command that works.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_scripts_need_the_app_path.py -q
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from viz_gallery.gallery_manager import CONVERT_HINT

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = {
    "convert_gallery_examples": ["--gallery", "{gallery}", "--root", "{root}"],
    "create_data_analysis_recipe": ["--data_files", "{data}", "--primary_key_data", "sample_id", "--out_file", "{out}"],
}


def run(script, arguments, *, with_path, cwd=ROOT):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    if with_path:
        env["PYTHONPATH"] = os.environ.get("PYTHONPATH") or str(ROOT)
    return subprocess.run([sys.executable, str(ROOT / "assets" / "scripts" / f"{script}.py"), *arguments],
                          capture_output=True, text=True, cwd=cwd, env=env, timeout=120)


@pytest.fixture
def project():
    """A folder inside the project (the recipe script refuses data outside it), removed afterwards."""
    folder = ROOT / "tmpAI" / "scripts_path_test"
    shutil.rmtree(folder, ignore_errors=True)
    (folder / "gallery").mkdir(parents=True)
    (folder / "samples.tsv").write_text("sample_id\tcountry\ns1\tNO\ns2\tSE\n")
    yield folder
    shutil.rmtree(folder, ignore_errors=True)


def arguments_for(script, project):
    return [a.format(gallery=project / "gallery", root=project, data=project / "samples.tsv", out=project / "r" / "scaffold.yaml")
            for a in SCRIPTS[script]]


@pytest.mark.parametrize("script", sorted(SCRIPTS))
@pytest.mark.parametrize("with_path", [False, True], ids=["without-path", "with-path"])
def test_help_works_with_and_without_the_path(script, with_path):
    result = run(script, ["--help"], with_path=with_path)
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout and "Traceback" not in result.stderr


@pytest.mark.parametrize("script", sorted(SCRIPTS))
def test_a_run_without_the_path_says_what_is_missing_and_what_to_type(script, project):
    result = run(script, arguments_for(script, project), with_path=False)
    text = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Traceback" not in text and "ModuleNotFoundError" not in text
    assert "cannot find the folder `app`" in text
    assert f"Suggestion: run it from the project root with PYTHONPATH=., for example: PYTHONPATH=. ./.venv/bin/python assets/scripts/{script}.py" in text
    assert not (project / "r").exists()


def test_a_run_with_the_path_works(project):
    result = run("create_data_analysis_recipe", arguments_for("create_data_analysis_recipe", project), with_path=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "r" / "scaffold.yaml").is_file()
    result = run("convert_gallery_examples", arguments_for("convert_gallery_examples", project), with_path=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_hint_of_the_gallery_check_is_the_command_that_works():
    hint = CONVERT_HINT.format(name="old_one")
    # the command is the end of the line, so that pasting it into a shell works: the words about the folder come before it
    assert hint == "From the project root run: PYTHONPATH=. ./.venv/bin/python assets/scripts/convert_gallery_examples.py --only old_one --apply"
    assert hint.endswith("--apply") and "(" not in hint
    assert (ROOT / "assets" / "scripts" / "convert_gallery_examples.py").is_file()
