"""A kept copy of an imported session must not break the Session Management panel, and the zip names are checked (D-0281, D-0050).

Before the fix "Keep both" stored the copy as `<key>~imported-<time>`; the panel built its Shiny input ids from the key, Shiny refused
the `~` and `-`, and the whole panel showed one error until the folder was removed by hand. The panel ids now come from one function
(`session_input_id_part`); the copy is named with letters, digits, `_` and `:` only; a zip whose folder holds any other character, or
whose `session_key` inside `assembly.json` differs from the folder, is refused whole before anything is written.
D-0050: "No silent error: that is the rule" (each refusal names the member and says what is allowed).

Mutation index (each seen failing): MUTATION M1 the panel builds ids with the old ":" replacement only (test_the_panel_renders_with_a_kept_copy);
MUTATION M2 the folder-name check is removed (test_a_folder_name_with_another_character_is_refused).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_import_copy_panel.py -q

# @deps
# provides: test:session_import_copy_panel
# consumes: app/modules/session_manager.py, app/handlers/session_handlers.py, app/tests/test_session_import_safety.py
# consumed_by: CI
# doc: .claude/rules/ui_implementation_contract.md#12d
# @end_deps
"""
import json
import re
import warnings

import pytest

from app.modules.session_manager import SessionImportRefused, SessionManager, session_input_id_part
from app.tests.test_session_import_safety import BIG, GOOD, KEY, Screen, _session_zip, _tree, _zip_of

VALID_ID = re.compile(r"[A-Za-z0-9_]+")


def _ids(html: str) -> list[str]:
    return re.findall(r'\bid="([^"]+)"', html)


def test_the_panel_renders_with_a_kept_copy(tmp_path, monkeypatch):
    """MUTATION M1 fails here: the id of the copy would hold a character Shiny refuses."""
    screen = Screen(tmp_path, monkeypatch)
    screen.upload_zip(_session_zip("original"))
    screen.upload_zip(_session_zip("incoming"))
    screen.run("_handle_import_keep")
    keys = sorted(s["session_key"] for s in screen.manager.list_all_sessions())
    assert len(keys) == 2
    html = str(screen.run("session_management_ui"))
    ids = _ids(html)
    for key in keys:
        part = session_input_id_part(key)
        for kind in ("session_restore_", "session_delete_", "session_label_input_"):
            assert kind + part in ids, f"{kind}{part} is missing from the panel"
    assert all(VALID_ID.fullmatch(i.removesuffix("-label")) for i in ids if i.startswith("session_")), ids
    assert len(set(ids)) == len(ids), "two controls share one id"


def test_the_copy_name_holds_only_plain_characters(sm):
    sm.import_session_zip(_session_zip(), limits=BIG)
    copy = sm.import_session_zip(_session_zip(), limits=BIG, on_exists="keep_both")
    assert re.fullmatch(r"[A-Za-z0-9_:]+", copy), copy
    assert copy.startswith(KEY + "_imported_")


@pytest.fixture()
def sm(tmp_path):
    return SessionManager(tmp_path / "user")


@pytest.mark.parametrize("key", ["a1:b2", "a1_b2", f"{KEY}_imported_20261118T135226477164", "weird-name~x y"])
def test_the_id_part_is_always_a_valid_id_part(key):
    assert VALID_ID.fullmatch(session_input_id_part(key))


def test_the_usual_key_keeps_the_old_id_form():
    assert session_input_id_part(KEY) == KEY.replace(":", "_")


def _refused(sm, members, tmp_path):
    before = _tree(sm.root) if sm.root.exists() else []
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(_zip_of(members), limits=BIG)
    after = _tree(sm.root) if sm.root.exists() else []
    assert after == before and not (sm.root.exists() and [p for p in sm.root.iterdir() if p.name.startswith(".")])
    return str(err.value)


@pytest.mark.parametrize("folder", ["my-session", "a~b", "with space", "dot.name"])
def test_a_folder_name_with_another_character_is_refused(sm, tmp_path, folder):
    """MUTATION M2 fails here."""
    text = _refused(sm, [(f"{folder}/assembly.json", json.dumps({"session_key": folder}))], tmp_path)
    assert folder in text and "letters, digits" in text and "nothing was written" in text


def test_a_session_key_inside_that_differs_from_the_folder_is_refused(sm, tmp_path):
    text = _refused(sm, [("aaa:bbb/assembly.json", json.dumps({"session_key": "ccc:ddd", "schema_version": 3}))], tmp_path)
    assert "aaa:bbb" in text and "ccc:ddd" in text and "must be the same" in text


def test_two_folder_names_that_look_the_same_on_the_screen_are_refused(sm, tmp_path):
    sm.import_session_zip(_zip_of([("aa:bb/assembly.json", json.dumps({"session_key": "aa:bb", "schema_version": 3}))]), limits=BIG)
    text = _refused(sm, [("aa_bb/assembly.json", json.dumps({"session_key": "aa_bb", "schema_version": 3}))], tmp_path)
    assert "aa_bb" in text and "aa:bb" in text


def test_a_backslash_member_is_refused_in_words(sm, tmp_path):
    text = _refused(sm, [GOOD, (f"{KEY}\\assembly.json", "x")], tmp_path)
    assert "backslash" in text and f"{KEY}\\assembly.json" in text


def test_a_very_long_member_name_is_refused_in_words_and_shortened(sm, tmp_path):
    long_name = f"{KEY}/" + "x" * 5000
    text = _refused(sm, [GOOD, (long_name, "x")], tmp_path)
    assert "too long" in text and "shortened" in text and len(text) < 600


def test_a_name_that_appears_twice_is_refused(sm, tmp_path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        text = _refused(sm, [GOOD, GOOD], tmp_path)
    assert "twice" in text and GOOD[0] in text


def test_the_dotdot_message_ends_cleanly(sm, tmp_path):
    text = _refused(sm, [GOOD, (f"{KEY}/../x", "x")], tmp_path)
    assert "'..' part that goes up. A session zip" in text
