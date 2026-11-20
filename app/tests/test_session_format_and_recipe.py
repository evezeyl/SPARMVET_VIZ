"""One format number for session files (D-0312) and a Restore that refuses a session of another recipe (D-0317).

D-0312: every writer writes `schema_version` (SESSION_FORMAT_VERSION) and every reader compares it: a file with no number, a lower
one or a higher one is refused as a whole with a plain line, nothing is converted. D-0317: a session whose recipe is not the open
recipe is refused on Restore, nothing is applied. The same recipe with another content hash (b) or another data batch (c) keeps
the warning and restores (not covered by D-0317, tested as unchanged).

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION F1  `_read_current_json` does not compare the number
  MUTATION F2  the zip import does not compare the number before extraction
  MUTATION F3  `write_assembly_ghost` writes over a refused record
  MUTATION F4  `write_t3_ghost` writes `tier_toggle` again
  MUTATION R1  `_restore_session` does not refuse a session of another recipe

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_format_and_recipe.py -q
"""
import io
import json
import zipfile

import pytest
from shiny import reactive

from app.modules.session_manager import (
    SESSION_FORMAT_VERSION, LegacySessionError, SessionManager, make_audit_step, session_input_id_parts)
from app.tests.test_session_errors_visible import KEY, RESTORE, Screen

OLDER = "was saved by an older version of the app and cannot be opened. Delete it and start a new session."
NEWER = "was saved by a newer version of the app and cannot be opened. Delete it and start a new session."
VARIANTS = [("no number", None, OLDER), ("lower number", 2, OLDER), ("higher number", SESSION_FORMAT_VERSION + 1, NEWER)]


def _assembly(key=KEY, version=SESSION_FORMAT_VERSION, recipe="tiny", sha="a" * 64, batch="b" * 64):
    data = {"session_key": key, "data_analysis_recipe_id": recipe, "data_analysis_recipe_sha256": sha, "data_batch_hash": batch,
            "assembled_at": "2026-11-01T10:00:00", "label": "", "source_files": {}, "parquet_paths": {}}
    if version is not None:
        data["schema_version"] = version
    return data


def _t3(key=KEY, version=SESSION_FORMAT_VERSION):
    data = {"session_key": key, "saved_at": "2026-11-02T10:00:00", "label": "", "t3_audit_steps": [],
            "t3_audit_steps_by_plot": {}, "t3_plot_overrides": {}}
    if version is not None:
        data["schema_version"] = version
    return data


def _put(sm, key, name, data):
    path = sm.session_dir(key) / name
    path.write_text(json.dumps(data))
    return path


def _zip(members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in members:
            zf.writestr(name, json.dumps(data))
    return buf.getvalue()


@pytest.fixture
def sm(tmp_path):
    return SessionManager(tmp_path / "user")


# --- writers -------------------------------------------------------------------------------------------------------------

def test_both_writers_write_the_number_and_no_view_value(sm):
    """MUTATION F4 fails here."""
    a = sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    t = sm.write_t3_ghost(KEY, "tiny", "a" * 64, "b" * 64, t3_audit_steps_by_plot={"subtab_p": []})
    assert json.loads(a.read_text())["schema_version"] == SESSION_FORMAT_VERSION
    raw = json.loads(t.read_text())
    assert raw["schema_version"] == SESSION_FORMAT_VERSION
    assert "tier_toggle" not in raw and "tier_toggle" not in sm.list_t3_ghosts(KEY)[0]


def test_a_current_file_round_trips(sm):
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, label="run")
    step = make_audit_step("filter_row", {"column": "x", "op": "eq", "value": 1}, reason="r")
    sm.write_t3_ghost(KEY, "tiny", "a" * 64, "b" * 64, t3_audit_steps_by_plot={"subtab_p": [step]})
    assert sm.read_assembly_ghost(KEY)["label"] == "run"
    assert len(sm.list_t3_ghosts(KEY)[0]["t3_audit_steps_by_plot"]["subtab_p"]) == 1
    assert [s["session_key"] for s in sm.list_all_sessions()] == [KEY]


# --- every reader refuses -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_the_direct_read_refuses_an_assembly_file(sm, name, version, text):
    """MUTATION F1 fails here."""
    _put(sm, KEY, "assembly.json", _assembly(version=version))
    with pytest.raises(LegacySessionError) as exc:
        sm.read_assembly_ghost(KEY)
    assert str(exc.value) == f"Session {KEY} (assembly.json) {text}"
    assert "convert" not in str(exc.value).lower() and "migrate" not in str(exc.value).lower()


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_the_direct_read_refuses_a_save(sm, name, version, text):
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    _put(sm, KEY, "t3_20261102T100000.json", _t3(version=version))
    with pytest.raises(LegacySessionError) as exc:
        sm.scan_t3_ghosts(KEY)
    assert text in str(exc.value) and "t3_20261102T100000.json" in str(exc.value)


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_the_session_list_shows_the_refused_session_with_the_line(sm, name, version, text):
    _put(sm, KEY, "assembly.json", _assembly(version=version))
    listed = sm.list_all_sessions()
    assert len(listed) == 1 and listed[0]["legacy_problem"].endswith(text)


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_a_current_assembly_with_a_refused_save_is_refused_as_a_whole(sm, name, version, text):
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    _put(sm, KEY, "t3_20261102T100000.json", _t3(version=version))
    listed = sm.list_all_sessions()
    assert len(listed) == 1 and listed[0]["legacy_problem"].endswith(text)


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_the_start_up_check_for_a_stored_assembly_refuses(sm, tmp_path, name, version, text):
    recipe = tmp_path / "r.yaml"
    recipe.write_text("id: r\ndata_schemas: {}\njoins: {}\nanalysis_groups: {g: {plots: {}}}\n")
    data = tmp_path / "d.tsv"
    data.write_text("a\n1\n")
    key = SessionManager.compute_session_key(sm.compute_data_analysis_recipe_sha256(recipe), sm.compute_data_batch_hash({"d": data}))
    _put(sm, key, "assembly.json", _assembly(key=key, version=version))
    with pytest.raises(LegacySessionError) as exc:
        sm.restore_t1t2(recipe, {"d": data})
    assert str(exc.value).endswith(text)


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_the_zip_import_refuses_before_extraction_and_writes_nothing(sm, name, version, text):
    """MUTATION F2 fails here."""
    zip_bytes = _zip([(f"{KEY}/assembly.json", _assembly(version=version))])
    with pytest.raises(LegacySessionError) as exc:
        sm.import_session_zip(zip_bytes)
    assert text in str(exc.value)
    assert not sm.root.exists() or not [p for p in sm.root.rglob("*")]


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_the_zip_import_refuses_an_old_save_in_a_current_zip(sm, name, version, text):
    zip_bytes = _zip([(f"{KEY}/assembly.json", _assembly()), (f"{KEY}/t3_20261102T100000.json", _t3(version=version))])
    with pytest.raises(LegacySessionError):
        sm.import_session_zip(zip_bytes)
    assert not sm.root.exists() or not [p for p in sm.root.rglob("*")]


def test_the_zip_of_a_current_session_is_imported(sm):
    assert sm.import_session_zip(_zip([(f"{KEY}/assembly.json", _assembly())])) == KEY


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_a_refused_record_is_never_written_over_silently(sm, name, version, text):
    """MUTATION F3 fails here: the new session of the same key and data is not written over the refused file."""
    path = _put(sm, KEY, "assembly.json", _assembly(version=version))
    before = path.read_bytes()
    with pytest.raises(LegacySessionError) as exc:
        sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    assert text in str(exc.value)
    assert path.read_bytes() == before


def test_a_label_is_not_written_into_a_refused_file(sm):
    path = _put(sm, KEY, "assembly.json", _assembly(version=None))
    before = path.read_bytes()
    with pytest.raises(LegacySessionError):
        sm.set_session_label(KEY, "new")
    assert path.read_bytes() == before


def test_old_and_new_sessions_side_by_side_then_the_old_one_is_deleted_and_a_new_one_is_created(sm):
    old_key = "cccccccccccc:dddddddddddd"
    _put(sm, old_key, "assembly.json", _assembly(key=old_key, version=None))
    _put(sm, old_key, "t3_20261102T100000.json", _t3(key=old_key, version=2))
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    listed = {s["session_key"]: s for s in sm.list_all_sessions()}
    assert set(listed) == {KEY, old_key}
    assert "legacy_problem" in listed[old_key] and "legacy_problem" not in listed[KEY]
    assert sm.read_assembly_ghost(KEY) is not None
    sm.delete_session(old_key)
    assert [s["session_key"] for s in sm.list_all_sessions()] == [KEY]
    sm.write_assembly_ghost(old_key, "tiny", "c" * 64, "d" * 64, {}, {})   # the same key is free again
    assert sm.read_assembly_ghost(old_key)["schema_version"] == SESSION_FORMAT_VERSION


def test_the_panel_deletes_a_refused_session(tmp_path, monkeypatch):
    from app.tests.test_session_errors_visible import SAFE
    old_key = "cccccccccccc:dddddddddddd"
    screen = Screen(tmp_path, monkeypatch, {f"session_delete_{old_key.replace(':', '_')}": 1})
    _put(screen.manager, old_key, "assembly.json", _assembly(key=old_key, version=None))
    assert session_input_id_parts([old_key, KEY])[old_key] == old_key.replace(":", "_")
    screen.run("_handle_session_actions")
    assert not (screen.manager.root / old_key).exists()
    assert (screen.manager.root / KEY).exists()


# --- the Restore of the screen ------------------------------------------------------------------------------------------------

def _state(screen):
    with reactive.isolate():
        return dict(screen.home_state.get())


def _save_step(manager, key=KEY):
    step = make_audit_step("filter_row", {"column": "x", "op": "eq", "value": 1}, reason="r")
    manager.write_t3_ghost(key, "tiny", "a" * 64, "b" * 64, t3_audit_steps_by_plot={"subtab_p": [step]})


@pytest.mark.parametrize("name, version, text", VARIANTS)
def test_a_restore_of_a_refused_session_says_so_and_changes_nothing(tmp_path, monkeypatch, name, version, text):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _put(screen.manager, KEY, "assembly.json", _assembly(version=version))
    before = _state(screen)
    screen.run("_handle_session_actions")
    errors = screen.texts("error")
    assert len(errors) == 1 and errors[0].endswith(text), screen.notes
    assert _state(screen) == before


# D-0317 (a): another recipe id is refused and nothing is applied
def test_a_session_of_another_recipe_is_refused_and_nothing_is_applied(tmp_path, monkeypatch):
    """MUTATION R1 fails here."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1}, open_recipe="other_recipe")
    _save_step(screen.manager)
    before = _state(screen)
    screen.run("_handle_session_actions")
    assert screen.texts("error") == [f"❌ Session {KEY} belongs to another recipe (tiny). Open that recipe first, then restore the session."]
    assert screen.texts("warning") == [] and screen.texts("message") == []
    assert _state(screen) == before and "t3_audit_steps_by_plot" not in before


def test_the_refusal_names_the_label_when_there_is_one(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1}, open_recipe="other_recipe")
    screen.manager.set_session_label(KEY, "my run")
    screen.run("_handle_session_actions")
    assert "Session my run belongs to another recipe (tiny)." in screen.texts("error")[0]


def test_no_open_recipe_refuses_too_and_applies_nothing(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1}, open_recipe="")
    _save_step(screen.manager)
    before = _state(screen)
    screen.run("_handle_session_actions")
    assert "no recipe is open" in screen.texts("error")[0]
    assert _state(screen) == before


# D-0317 (b): the same recipe id with another content hash is NOT covered: today's warning, then the restore
def test_the_same_recipe_with_another_content_hash_keeps_the_warning_and_restores(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save_step(screen.manager)
    with reactive.isolate():
        screen.home_state.set({**screen.home_state.get(), "data_analysis_recipe_sha256": "e" * 64})
    screen.run("_handle_session_actions")
    assert any("different data analysis recipe version" in w for w in screen.texts("warning")), screen.notes
    assert screen.texts("error") == []
    assert _state(screen)["t3_audit_steps_by_plot"]["subtab_p"]


# D-0317 (c): the same recipe, another data batch: the warning stays, non-blocking
def test_the_same_recipe_with_another_data_batch_keeps_the_warning_and_restores(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save_step(screen.manager)
    with reactive.isolate():
        screen.home_state.set({**screen.home_state.get(), "data_batch_hash": "f" * 64})
    screen.run("_handle_session_actions")
    assert any("different data batch" in w for w in screen.texts("warning")), screen.notes
    assert screen.texts("error") == []
    assert _state(screen)["t3_audit_steps_by_plot"]["subtab_p"]


def test_the_session_list_still_lists_a_session_of_another_recipe(sm):
    sm.write_assembly_ghost(KEY, "recipe_a", "a" * 64, "b" * 64, {}, {})
    listed = sm.list_all_sessions()
    assert [(s["session_key"], s["data_analysis_recipe_id"]) for s in listed] == [(KEY, "recipe_a")]


def test_the_app_start_with_an_old_assembly_for_the_opened_recipe_does_not_crash_and_writes_nothing(sm):
    """HOME writes the record of the session at every change; with a refused record of the same key it is refused and told
    (the caller of write_assembly_ghost in home_theater.py catches and tells), the old file stays until the user deletes it."""
    path = _put(sm, KEY, "assembly.json", _assembly(version=None))
    before = path.read_bytes()
    with pytest.raises(LegacySessionError):
        sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    assert path.read_bytes() == before
    assert [s["session_key"] for s in sm.list_all_sessions()] == [KEY]


# --- a session file whose JSON is not a mapping (a list, a number, text): refused as unreadable, plain line, no traceback ---

NOT_MAPPINGS = [("a list", [1, 2]), ("a number", 7), ("text", "hello")]


@pytest.mark.parametrize("name, value", NOT_MAPPINGS)
def test_the_direct_read_of_a_non_mapping_file_says_which_file_in_plain_words(sm, name, value):
    path = sm.session_dir(KEY) / "assembly.json"
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError) as exc:
        sm.read_assembly_ghost(KEY)
    text = str(exc.value)
    assert text.startswith(f"Session {KEY} (assembly.json) is not a session file: it holds {name}")
    assert not isinstance(exc.value, (AttributeError, LegacySessionError)) and "Traceback" not in text


@pytest.mark.parametrize("name, value", NOT_MAPPINGS)
def test_the_list_names_such_an_assembly_file_as_unreadable_not_as_a_crash(sm, name, value):
    (sm.session_dir(KEY) / "assembly.json").write_text(json.dumps(value))
    sessions, unreadable = sm.scan_sessions()
    assert sessions == [] and len(unreadable) == 1
    assert unreadable[0]["kind"] == "session" and "is not a session file" in unreadable[0]["reason"]


@pytest.mark.parametrize("name, value", NOT_MAPPINGS)
def test_a_non_mapping_save_is_named_as_skipped(sm, name, value):
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    bad = sm.session_dir(KEY) / "t3_20261102T100000.json"
    bad.write_text(json.dumps(value))
    saves, skipped = sm.scan_t3_ghosts(KEY)
    assert saves == [] and [s["name"] for s in skipped] == [bad.name] and "is not a session file" in skipped[0]["reason"]


@pytest.mark.parametrize("name, value", NOT_MAPPINGS)
def test_the_zip_import_refuses_a_non_mapping_file_and_extracts_nothing(sm, name, value):
    from app.modules.session_manager import SessionImportRefused
    for members in ([(f"{KEY}/assembly.json", value)],
                    [(f"{KEY}/assembly.json", _assembly()), (f"{KEY}/t3_20261102T100000.json", value)]):
        with pytest.raises(SessionImportRefused) as exc:
            sm.import_session_zip(_zip(members))
        assert "nothing was written" in str(exc.value) and "is not a session file" in str(exc.value)
        assert "assembly.json" in str(exc.value) or "t3_20261102T100000.json" in str(exc.value)
        assert not sm.root.exists() or not [p for p in sm.root.rglob("*")]


@pytest.mark.parametrize("name, value", NOT_MAPPINGS)
def test_writing_over_a_non_mapping_record_tells_the_user_like_a_truncated_one(sm, name, value):
    path = sm.session_dir(KEY) / "assembly.json"
    path.write_text(json.dumps(value))
    problems = []
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, on_problem=problems.append)
    assert len(problems) == 1
    assert "could not be read, so it was written again" in problems[0] and "is not a session file" in problems[0]
    assert sm.read_assembly_ghost(KEY)["schema_version"] == SESSION_FORMAT_VERSION


def test_writing_over_a_truncated_record_still_tells_the_user_and_a_readable_one_does_not(sm):
    path = sm.session_dir(KEY) / "assembly.json"
    path.write_text("{ truncated")
    problems = []
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, on_problem=problems.append)
    assert len(problems) == 1
    sm.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, on_problem=problems.append)
    assert len(problems) == 1
