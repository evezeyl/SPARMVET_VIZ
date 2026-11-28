"""KNOWN GAP (G1, the running session; Eve 2026-11-28: audit steps never mix across data; the guard of Restore is built, this one is not).

Today, when a DATA file changes on disk (a Data Import) while audit steps are in the view, `_sync_session_provenance` updates the data key and keeps the
steps in `home_state`; the set-aside of steps (`_set_audit_steps_aside_on_recipe_change`) is per RECIPE only. So the steps made on the old data stay and are
applied to the new data, and the next save writes them under the new data's key (RAN: `tmpAI/gaps/g1_live.py`).

This test PINS TODAY'S BEHAVIOUR so the gap is found by name. WHEN THE FIX IS BUILT (steps set aside for their own data, keyed by recipe AND data, an empty
audit on the new data, one notice; a metadata-only change keeps the steps), INVERT the assertion of the first test. The fix is its own slice (see the report).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_steps_stay_when_data_changes_known_gap.py -q
"""
from shiny import reactive

from app.modules.session_manager import make_audit_step
from app.tests.test_session_keys_missing_told import Home


def test_steps_stay_in_the_view_when_a_data_file_changes_KNOWN_GAP(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch)
    home.sync()
    step = make_audit_step("filter_row", {"column": "a", "op": "eq", "value": 1, "dtype": "Int64"}, "made on the first data", place="T3:p")
    with reactive.isolate():
        home.home_state.set({**home.home_state.get(), "audit_pipeline": [step]})
        first_key = home.home_state.get()["data_batch_hash"]
    home.world.data_file.write_text(home.world.data_file.read_text() + "z\t9\n")      # the data on disk change
    home.sync()
    with reactive.isolate():
        state = home.home_state.get()
    assert state["data_batch_hash"] != first_key, "the control: the app noticed the new data"
    assert [n["reason"] for n in state["audit_pipeline"]] == ["made on the first data"], "KNOWN GAP: the steps of the old data are still in the view"
