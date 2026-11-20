"""The notice told when the record of a session cannot be written names the remedy that helps for each cause (D-0312, the coordinator's addition).

`home_theater._sync_session_provenance` writes the assembly record of the session. When an OLD session file (another format number) is stored under
the same session key, `write_assembly_ghost` raises `LegacySessionError`: checking the folder would not help; deleting the old session in the
Session panel does. Every other failure keeps the existing notice (check that the user data folder can be written).

MUTATION N1 (the `except LegacySessionError` branch removed): the legacy test fails (it gets the generic text).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_record_notice.py -q
"""
from unittest import mock

import pytest
from shiny import reactive

from app.handlers.home_theater import LEGACY_RECORD_NOTICE
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.session_manager import LegacySessionError
from app.tests.home_harness import Home, ViewWorld


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _run(tmp_path, monkeypatch, error):
    manager = mock.MagicMock()
    manager.write_assembly_ghost.side_effect = error
    home = Home(ViewWorld(tmp_path), monkeypatch, session_manager=manager, home_state={})
    with reactive.isolate():
        home.effects["_sync_session_provenance"]()
    return [text for _kind, text in home.notes if "record of this session" in text or "cannot be recorded" in text]


def test_an_old_session_file_gets_the_remedy_that_deletes_it(tmp_path, monkeypatch):
    texts = _run(tmp_path, monkeypatch, LegacySessionError("Session x was saved by an older version of the app and cannot be opened. Delete it."))
    assert texts == ["⚠️ " + LEGACY_RECORD_NOTICE]
    assert "Session panel" in texts[0] and "delete the session marked as saved by an older version" in texts[0]
    assert "check that the user data folder" not in texts[0]


def test_any_other_cause_keeps_the_existing_notice(tmp_path, monkeypatch):
    [text] = _run(tmp_path, monkeypatch, PermissionError("read-only folder"))
    assert "could not be written" in text and "check that the user data folder can be written" in text
    assert "Session panel and delete" not in text and "older session" not in text
