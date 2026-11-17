"""A subprocess started by a test must run THIS checkout's code, not the main checkout's (editable installs).

In a git worktree the shared .venv resolves every `libs/*` package to the main checkout, so an app started with
`PYTHONPATH="."` would run other code than the test is about. `app_env()` builds the PYTHONPATH from the repository
root of the tests plus every `libs/*/src` under it; no `sys.path` change in the test process (ADR-011/016).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_subprocess_sources.py -q
"""
import subprocess
import sys
from pathlib import Path

from app.tests.subprocess_env import REPO, app_command, app_env, source_path


def test_source_path_holds_the_root_and_every_lib_src_of_this_checkout():
    parts = source_path().split(":")
    assert parts[0] == str(REPO)
    for src in sorted((REPO / "libs").glob("*/src")):
        assert str(src) in parts
    assert all(p.startswith(str(REPO)) for p in parts[: 1 + len(list((REPO / "libs").glob("*/src")))])


def test_a_subprocess_imports_the_libs_from_this_checkout():
    code = "import utils, transformer, viz_factory; print(utils.__file__); print(transformer.__file__); print(viz_factory.__file__)"
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO, env=app_env(), capture_output=True, text=True, check=True)
    files = out.stdout.split()
    assert len(files) == 3
    for f in files:
        assert Path(f).resolve().is_relative_to(REPO.resolve()), f"{f} is outside {REPO}"


def test_app_env_keeps_the_given_variables_and_a_caller_pythonpath():
    env = app_env(SPARMVET_APP_FEATURES="qa")
    assert env["SPARMVET_APP_FEATURES"] == "qa"
    assert source_path() in env["PYTHONPATH"]


def test_app_command_is_the_running_interpreter_and_no_venv_path():
    cmd = app_command(8123)
    assert cmd[0] == sys.executable
    assert cmd[1:4] == ["-m", "shiny", "run"]
    assert cmd[-2:] == ["--port", "8123"]
    assert ".venv" not in " ".join(cmd[1:])
    assert (REPO / cmd[4]).is_file(), "the app file named by the command must exist in this checkout"


def test_the_app_started_by_the_helper_imports_this_checkouts_code():
    """What `shiny run app/src/main.py` imports, started the way the helper starts it (interpreter, cwd, env).

    Not the whole server: the app has no endpoint that tells which code runs, and this task does not change the app.
    This runs the same interpreter, working folder and environment and imports the app module and the libs it uses.
    """
    code = ("import importlib\n"
            "for m in ('app.src.main', 'utils', 'transformer', 'viz_factory', 'blueprint_arch', 'ingestion'):\n"
            "    print('FILE=' + importlib.import_module(m).__file__)\n")
    cmd = app_command(8123)
    out = subprocess.run([cmd[0], "-c", code], cwd=REPO, env=app_env(), capture_output=True, text=True, check=True)
    files = [l[5:] for l in out.stdout.splitlines() if l.startswith('FILE=')]
    assert len(files) == 6
    for f in files:
        assert Path(f).resolve().is_relative_to(REPO.resolve()), f"{f} is outside {REPO}"
