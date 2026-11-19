"""The tests of a process keep their sessions and cache in a folder of their own, not in the shared `tmp/UI_TEST/`.

Why: browser tests of different files seeded and deleted sessions in one folder; a delete-all of one file emptied the
sessions another file had just seeded (found in parallel runs). `conftest.py` points the process at a copy of the local
deployment with its own `user_data` and `cache`.
"""
import os
from pathlib import Path

import yaml

from app.tests.conftest import REPO


def test_the_process_has_a_deployment_with_state_folders_of_its_own():
    deployment = os.environ.get("SPARMVET_DEPLOYMENT")
    assert deployment, "conftest.py sets a deployment for the process when the caller sets none"
    locations = yaml.safe_load(Path(deployment).read_text(encoding="utf-8"))["locations"]
    shared = (REPO / "tmp" / "UI_TEST").resolve()
    for key in ("user_data", "cache"):
        folder = Path(locations[key]).resolve()
        assert shared not in folder.parents and folder != shared, (key, folder)
        assert folder.is_dir(), (key, folder)
