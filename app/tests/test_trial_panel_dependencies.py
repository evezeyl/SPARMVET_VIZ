"""The trial panel and the effects of `trial_handlers`, on the real reactive graph without a browser (FLOW-1; ui_implementation_contract.md section 14, R1 to R4).

What the design expects: the panel only READS the trial (a render never writes, R1); a trial that cannot run shows its plain error and the button Discard and nothing else; Discard ends the trial and its
folder is emptied with no notice; a change of what the trial was made for ends it with ONE notice; a trial that exists is not drawn again by an unrelated write of `home_state` (the panel is its own output).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_trial_panel_dependencies.py -q

MUTATION (seen failing, then restored): the watcher ignores the staged rows (a changed condition no longer ends the trial).
"""
import asyncio
from types import SimpleNamespace

import pytest
from shiny import reactive, render, ui

import app.handlers.trial_handlers as trial_handlers
from app.modules.audit_trial import PlaceEffect, ReachItem, TrialResult
from app.modules.audit_try import TrialRecord, condition_lines, world_of
from app.tests.test_session_clicks_once import LiveInput

ROW = {"column": "identity", "op": "lt", "value": 99.0, "dtype": "Float64", "na": "remove"}


class _Trial:
    def __init__(self):
        self.discards = 0

    def discard(self):
        self.discards += 1


def _world(monkeypatch, trial=None, save_session=None, committed=None, extra_inputs=()):
    found, notes = {}, []
    monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
    monkeypatch.setattr(ui, "notification_show", lambda message, **k: notes.append(str(message)))
    live = LiveInput()
    for name in ("filter_try", "trial_discard", "filter_send_to_audit", "lineage_create", "col_drop_to_audit", "lineage_step_add", "lineage_chosen", "trial_show", "trial_add", *extra_inputs):
        live.set(name, None)
    live.set("lineage_chosen", [])
    pending = reactive.Value([dict(ROW)])
    home_state = reactive.Value({"t3_ghost_file": ""})
    trial_state, left = reactive.Value(None), reactive.Value(False)
    mode = reactive.Value(True)
    trial = trial or _Trial()

    def output(fn):
        found[fn.__name__] = fn
        return fn
    trial_handlers.define_trial_server(
        live, output, SimpleNamespace(on_ended=lambda fn: None), trial_state=trial_state, trial_left_original=left, in_audit=lambda: mode.get(), home_state=home_state,
        pending_filters=pending, safe_input=lambda i, k, d: (live.values[k].get() if k in live.values and live.values[k].get() is not LiveInput.MISSING else d),
        recipe_id=lambda: "r", recipe_keys=lambda: ("a", "b"), open_graph=lambda: None, lineage_calc=lambda: (None, "x"), recipe_plans=lambda: None,
        shown_place=lambda: "T3:p", committed_nodes=(committed if committed is not None else (lambda: [])), columns_at=lambda p: None, place_name=lambda n: f"name of {n}", get_trial=lambda: trial,
        notification_log=reactive.Value([]), save_session=save_session)
    return SimpleNamespace(found=found, notes=notes, live=live, pending=pending, home_state=home_state, trial_state=trial_state, mode=mode, trial=trial)


def _set(w, value):
    with reactive.isolate():
        w.trial_state.set(value)


def _flush(times=4):
    async def go():
        for _ in range(times):
            await reactive.flush()
    asyncio.run(go())


def _peek(value):
    with reactive.isolate():
        return value.get()


def _record(w, error=None):
    rows = _peek(w.pending)
    world = world_of("audit", "r", ("a", "b"), rows, [], ())
    result = TrialResult(("sig",), error=error) if error else TrialResult(("sig",), (PlaceEffect("T3:p", "Plot p", 10, 4, "table changed"),), (ReachItem("T3:q", "Plot q", "plot", "no row changed"),))
    return TrialRecord(world, ("T3:p",), (), result, condition_lines(rows))


def _html(world):
    with reactive.isolate():
        return str(world.found["trial_panel_ui"]())


def test_the_panel_shows_the_words_the_counts_and_a_discard_button_and_only_reads(monkeypatch):
    w = _world(monkeypatch)
    _flush()
    assert _html(w).count("spv-trial-panel") == 0, "no trial, no panel"
    _set(w, _record(w))
    html = _html(w)
    assert "TRIAL: with the step you are trying. Not applied, not saved, not exported." in html
    assert "name of T3:p: the step removes 6 rows of 10 here (table changed)." in html
    assert "name of T3:q: no row changed" in html and "To apply this step use Send to Audit" not in html, "the line of FLOW-1 is gone: the step is added here now"
    assert 'id="trial_discard"' in html and "Discard" in html
    assert 'id="trial_verified_0_0"' in html and "User verified" in html, "one mark for the one place (the number of the Try is in the id)"
    assert 'id="trial_reason_0"' in html and "Reason (required)" in html and 'id="trial_marks_summary_ui"' in html and 'id="trial_add_ui"' in html
    assert w.trial.discards == 0, "rendering never ends a trial"


def test_a_step_that_cannot_run_shows_its_plain_error_the_heading_and_discard_only(monkeypatch):
    w = _world(monkeypatch)
    _set(w, _record(w, error="The audit step 1 (id x) at Plot p (tier 3) cannot run: no such column."))
    html = _html(w)
    assert "This step cannot be tried: The audit step 1" in html and "TRIAL: with the step you are trying" in html and 'id="trial_discard"' in html
    assert "the step removes" not in html and "What these places reach" not in html


def test_discard_ends_the_trial_empties_its_folder_and_says_nothing(monkeypatch):
    w = _world(monkeypatch)
    _flush()
    _set(w, _record(w))
    w.live.set("trial_discard", 1)
    _flush()
    with reactive.isolate():
        assert w.trial_state.get() is None
    assert w.trial.discards == 1 and w.notes == []


def test_a_changed_condition_ends_the_trial_with_one_notice_and_an_unrelated_write_does_not(monkeypatch):
    w = _world(monkeypatch)
    _flush()
    _set(w, _record(w))
    _flush()
    with reactive.isolate():
        w.home_state.set({**w.home_state.get(), "active_plot_subtab": "subtab_other", "audit_shown_place": "T1:x"})
    _flush()
    with reactive.isolate():
        assert w.trial_state.get() is not None, "showing another item or a tab does not end a trial"
    assert w.notes == []
    with reactive.isolate():
        w.pending.set([])
    _flush()
    with reactive.isolate():
        assert w.trial_state.get() is None
    assert len(w.notes) == 1 and "The condition changed. The trial ended" in w.notes[0] and w.trial.discards == 1


def test_leaving_audit_mode_and_using_an_old_entry_end_the_trial_each_with_its_notice(monkeypatch):
    w = _world(monkeypatch)
    _flush()
    _set(w, _record(w))
    _flush()
    with reactive.isolate():
        w.mode.set(False)
    _flush()
    assert len(w.notes) == 1 and "You left Audit mode" in w.notes[0]
    with reactive.isolate():
        w.mode.set(True)
    _flush()
    _set(w, _record(w))
    _flush()
    w.live.set("filter_send_to_audit", 1)
    _flush()
    assert len(w.notes) == 2 and "You used Send to Audit. The trial ended" in w.notes[1]
    with reactive.isolate():
        assert w.trial_state.get() is None
