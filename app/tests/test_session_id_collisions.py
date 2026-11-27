"""Two stored sessions never share a button (D-0050 "No silent error: that is the rule"; D-0281).

Two folders whose keys give one safe id part (`aa:bb` and `aa_bb`, put in the store by hand, by a copy or by older code) used to share
one Delete button: one click deleted both. The ids are now unique by construction for the LISTED sessions, and the screen says so.

Mutation index (each seen failing): MUTATION C1  `session_input_id_parts` returns the plain safe form always.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_id_collisions.py -q

# @deps
# provides: test:session_id_collisions
# consumes: app/handlers/session_handlers.py, app/modules/session_manager.py, app/tests/test_session_clicks_once.py, app/tests/test_session_import_safety.py
# consumed_by: CI
# @end_deps
"""
import asyncio
import json
import re

import pytest
from shiny import reactive

from app.modules.session_manager import (SESSION_FORMAT_VERSION, SessionImportRefused, SessionManager, make_audit_step, session_id_collisions,
                                         session_input_id_part, session_input_id_parts)
from app.tests.test_session_clicks_once import SAFE, KEY_A, KEY_B, _flush, _live
from app.tests.test_session_import_safety import BIG, Screen, _session_zip, _tree, _zip_of

X, Y, Z = "aa:bb", "aa_bb", "aa-bb"
VALID_ID = re.compile(r"[A-Za-z0-9_]+")


# --------------------------------------------------------------------------- (a) the pure mapping

def test_unique_keys_keep_the_plain_safe_form():
    assert session_input_id_parts([KEY_A, KEY_B]) == {KEY_A: SAFE(KEY_A), KEY_B: SAFE(KEY_B)}
    assert session_id_collisions([KEY_A, KEY_B]) == []


def test_two_colliding_keys_get_different_ids_and_the_others_do_not_change():
    parts = session_input_id_parts([X, Y, KEY_A])
    assert parts[KEY_A] == SAFE(KEY_A)
    assert parts[X] != parts[Y]
    assert all(p.startswith("aa_bb_") and VALID_ID.fullmatch(p) for p in (parts[X], parts[Y]))
    assert session_id_collisions([X, Y, KEY_A]) == [[X, Y]]


def test_three_colliding_keys_get_three_different_ids():
    parts = session_input_id_parts([X, Y, Z])
    assert len(set(parts.values())) == 3 and all(VALID_ID.fullmatch(p) for p in parts.values())


def test_a_kept_copy_never_collides_with_its_original():
    copy = f"{KEY_A}_imported_20261118T135226477164"
    parts = session_input_id_parts([KEY_A, copy])
    assert parts == {KEY_A: SAFE(KEY_A), copy: SAFE(copy)}


def test_the_mapping_does_not_depend_on_the_listing_order():
    assert session_input_id_parts([X, Y]) == session_input_id_parts([Y, X])


# --------------------------------------------------------------------------- (b) the real effect

def _step(reason):
    return make_audit_step("filter_row", {"column": "a", "op": "eq", "value": 1, "dtype": "Int64"}, reason, place="T3:p")


def _add_pair(live):
    for key, tag, reason in ((X, "x", "from x"), (Y, "y", "from y")):
        live.manager.write_assembly_ghost(key, "tiny", tag * 64, "b" * 64, {}, {})
        live.manager.write_t3_ghost(key, "tiny", tag * 64, "b" * 64, audit_steps=[_step(reason)])
    return session_input_id_parts([s["session_key"] for s in live.manager.list_all_sessions()])


def test_deleting_one_of_two_colliding_sessions_leaves_the_other(tmp_path, monkeypatch):
    """MUTATION C1 fails here: both folders are deleted by one click."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        parts = _add_pair(live)
        await _flush()
        live.input.set(f"session_label_input_{parts[X]}", "")
        live.input.set(f"session_label_input_{parts[Y]}", "")
        live.input.set(f"session_delete_{parts[X]}", 0)
        live.input.set(f"session_delete_{parts[Y]}", 0)
        await _flush(4)
        live.input.set(f"session_delete_{parts[X]}", 1)
        await _flush(6)
        await live.confirm_delete()
        assert not (live.manager.root / X).exists()
        assert (live.manager.root / Y).exists(), "the other session was deleted by the same click"
        assert (live.manager.root / KEY_A).exists()
    asyncio.run(scenario())


def test_restoring_one_of_two_colliding_sessions_restores_that_one(tmp_path, monkeypatch):
    """MUTATION C1 fails here: both are restored and the last wins."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        parts = _add_pair(live)
        await _flush()
        live.input.set(f"session_restore_{parts[X]}", 0)
        live.input.set(f"session_restore_{parts[Y]}", 0)
        await _flush(4)
        live.input.set(f"session_restore_{parts[X]}", 1)
        await _flush(6)
        assert len(live.texts("Session restored")) == 1, live.notes
        reasons = [n["reason"] for n in live.state()["audit_pipeline"]]
        assert reasons == ["from x"], reasons
    asyncio.run(scenario())


# --------------------------------------------------------------------------- (c) the panel

def test_the_panel_with_a_colliding_pair_has_two_ids_and_the_notice(tmp_path, monkeypatch):
    """MUTATION C1 fails here: one shared id and no way to tell the cards apart."""
    screen = Screen(tmp_path, monkeypatch)
    for key, tag in ((X, "x"), (Y, "y")):
        screen.manager.write_assembly_ghost(key, "tiny", tag * 64, "b" * 64, {}, {})
    html = str(screen.run("session_management_ui"))
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(set(ids)) == len(ids), "two controls share one id"
    parts = session_input_id_parts([X, Y])
    for key in (X, Y):
        assert f"session_delete_{parts[key]}" in ids and f"session_restore_{parts[key]}" in ids
    assert parts[X] != parts[Y]
    assert "differ only in a character the screen cannot tell apart" in html
    assert f"Folder: {X}" in html and f"Folder: {Y}" in html


def test_the_panel_without_a_collision_has_no_notice(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch)
    screen.manager.write_assembly_ghost(KEY_A, "tiny", "a" * 64, "b" * 64, {}, {})
    html = str(screen.run("session_management_ui"))
    assert "cannot tell apart" not in html and "Folder:" not in html
    assert f"session_delete_{SAFE(KEY_A)}" in html


# --------------------------------------------------------------------------- (d) a t3 file with another key

def test_a_zip_whose_t3_file_holds_another_key_is_refused_and_nothing_is_written(tmp_path):
    sm = SessionManager(tmp_path / "user")
    members = [(f"{KEY_A}/assembly.json", json.dumps({"session_key": KEY_A, "data_analysis_recipe_id": "t", "schema_version": SESSION_FORMAT_VERSION})),
               (f"{KEY_A}/t3_20261118T000000.json", json.dumps({"session_key": KEY_B, "schema_version": SESSION_FORMAT_VERSION}))]
    before = _tree(sm.root) if sm.root.exists() else []
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(_zip_of(members), limits=BIG)
    assert f"{KEY_A}/t3_20261118T000000.json" in str(err.value) and KEY_B in str(err.value) and "nothing was written" in str(err.value)
    assert (_tree(sm.root) if sm.root.exists() else []) == before
    assert not sm.root.exists() or not [p for p in sm.root.iterdir()]
