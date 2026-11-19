"""The tests of a process keep their sessions and cache in a folder of their own, not in the shared `tmp/UI_TEST/`.

Why: browser tests of different files seeded and deleted sessions in one folder; a delete-all of one file emptied the
sessions another file had just seeded (found in parallel runs). `conftest.py` points the process at a copy of the local
deployment with its own `user_data` and `cache`.
"""
import os
from pathlib import Path

import pytest
import yaml

from app.tests.conftest import GENERATED_MARK, REPO

# these tests check the deployment file that conftest.py generates; a person who runs the tests with a SPARMVET_DEPLOYMENT of their own keeps it
uses_generated_deployment = pytest.mark.skipif(
    os.environ.get("SPARMVET_DEPLOYMENT") != os.environ.get(GENERATED_MARK) or not os.environ.get(GENERATED_MARK),
    reason="SPARMVET_DEPLOYMENT was set by the person running the tests, so the test deployment is not used; "
           "run without it to check the folders of the test process")


@uses_generated_deployment
def test_the_process_has_a_deployment_with_state_folders_of_its_own():
    deployment = os.environ.get("SPARMVET_DEPLOYMENT")
    assert deployment, "conftest.py sets a deployment for the process when the caller sets none"
    locations = yaml.safe_load(Path(deployment).read_text(encoding="utf-8"))["locations"]
    shared = (REPO / "tmp" / "UI_TEST").resolve()
    for key in ("user_data", "cache"):
        folder = Path(locations[key]).resolve()
        assert shared not in folder.parents and folder != shared, (key, folder)
        assert folder.is_dir(), (key, folder)


def _own_folder() -> Path:
    deployment = Path(os.environ["SPARMVET_DEPLOYMENT"])
    return deployment.parent


@uses_generated_deployment
def test_the_state_folder_is_named_after_the_worker():
    """Under pytest-xdist the folder is the worker's id (`gw0`, ...), without xdist it is `main`.

    Also records the folder in the file named by SPARMVET_RECORD_STATE_FOLDER when set (used by the test below).
    """
    folder = _own_folder()
    assert folder.parent == REPO / "tmpAI" / "browser_state", folder
    assert folder.name == os.environ.get("PYTEST_XDIST_WORKER", "main"), folder
    record = os.environ.get("SPARMVET_RECORD_STATE_FOLDER")
    if record:
        with open(record, "a", encoding="utf-8") as out:
            out.write(f"{os.environ.get('PYTEST_XDIST_WORKER', 'main')} {folder}\n")


@uses_generated_deployment
def test_two_workers_get_different_state_folders(tmp_path):
    """Run the test above on two real xdist workers (`--dist each`): the folders must differ.

    The workers inherit the controller's SPARMVET_DEPLOYMENT; on a conftest that trusts it every worker keeps the
    controller's `main` folder and the two lines name the same folder.
    """
    import subprocess
    import sys

    record = tmp_path / "folders.txt"
    env = dict(os.environ, SPARMVET_RECORD_STATE_FOLDER=str(record))
    target = f"{Path(__file__)}::test_the_state_folder_is_named_after_the_worker"
    result = subprocess.run([sys.executable, "-m", "pytest", target, "-n", "2", "--dist", "each", "-q", "-p", "no:cacheprovider"],
                            cwd=REPO, env=env, capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-1000:]
    lines = record.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, lines
    assert len({line.split(" ", 1)[1] for line in lines}) == 2, lines


def test_a_deployment_chosen_by_the_caller_is_kept(tmp_path, monkeypatch):
    """A SPARMVET_DEPLOYMENT that is not the generated one (no matching mark) is respected."""
    from app.tests import conftest

    chosen = tmp_path / "mine.yaml"
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(chosen))
    monkeypatch.setenv(conftest.GENERATED_MARK, str(tmp_path / "other.yaml"))
    conftest._own_state_deployment()
    assert os.environ["SPARMVET_DEPLOYMENT"] == str(chosen)
    monkeypatch.delenv(conftest.GENERATED_MARK)
    conftest._own_state_deployment()
    assert os.environ["SPARMVET_DEPLOYMENT"] == str(chosen)
