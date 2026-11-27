"""The trial panel and the effects of `trial_handlers`, on the real reactive graph without a browser (FLOW-1; ui_implementation_contract.md section 14, R1 to R4).

FLOW-3: the old entries (the pop-up of "Send to Audit", the lineage button, the column drop of the old way, the small form) are gone, so a trial is no longer ended by them; a DROP is tried like a condition.

What the design expects: the panel only READS the trial (a render never writes, R1); a trial that cannot run shows its plain error and the button Discard and nothing else; Discard ends the trial and its
folder is emptied with no notice; a change of what the trial was made for ends it with ONE notice; a trial that exists is not drawn again by an unrelated write of `home_state` (the panel is its own output).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_trial_panel_dependencies.py -q

MUTATION (seen failing, then restored): the watcher ignores the staged rows (a changed condition no longer ends the trial); `_try_drop` does not ask the rule of a key drop (K4).
"""
import asyncio
from types import SimpleNamespace

import pytest
from shiny import reactive, render, ui

import app.handlers.trial_handlers as trial_handlers
from app.modules.audit_trial import PlaceEffect, ReachItem, TrialResult
from app.modules.audit_try import KIND_DROP, TrialRecord, condition_lines, drop_condition_lines, world_of
from app.tests.test_session_clicks_once import LiveInput

ROW = {"column": "identity", "op": "lt", "value": 99.0, "dtype": "Float64", "na": "remove"}


class _Trial:
    def __init__(self):
        self.discards = 0

    def discard(self):
        self.discards += 1


def _world(monkeypatch, trial=None, save_session=None, committed=None, extra_inputs=(), **overrides):
    found, notes = {}, []
    monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
    monkeypatch.setattr(ui, "notification_show", lambda message, **k: notes.append(str(message)))
    live = LiveInput()
    for name in ("step_try", "step_kind", "trial_discard", "preview_col_selector", "lineage_chosen", "trial_show", "trial_add", *extra_inputs):
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
    kwargs = dict(
        trial_state=trial_state, trial_left_original=left, in_audit=lambda: mode.get(), home_state=home_state,
        pending_filters=pending, safe_input=lambda i, k, d: (live.values[k].get() if k in live.values and live.values[k].get() is not LiveInput.MISSING else d),
        recipe_id=lambda: "r", recipe_keys=lambda: ("a", "b"), open_graph=lambda: None, lineage_calc=lambda: (None, "x"), recipe_plans=lambda: None,
        shown_place=lambda: "T3:p", committed_nodes=(committed if committed is not None else (lambda: [])), columns_at=lambda p: None, place_name=lambda n: f"name of {n}", get_trial=lambda: trial,
        notification_log=reactive.Value([]), save_session=save_session)
    kwargs.update(overrides)
    trial_handlers.define_trial_server(live, output, SimpleNamespace(on_ended=lambda fn: None), **kwargs)
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


def test_leaving_audit_mode_ends_the_trial_with_its_notice(monkeypatch):
    w = _world(monkeypatch)
    _flush()
    _set(w, _record(w))
    _flush()
    with reactive.isolate():
        w.mode.set(False)
    _flush()
    assert len(w.notes) == 1 and "You left Audit mode" in w.notes[0]
    with reactive.isolate():
        assert w.trial_state.get() is None


def test_the_trial_of_a_drop_says_columns_and_is_bound_to_the_columns_it_was_made_for(monkeypatch):
    """FLOW-3: a drop is tried like a condition; its panel says "drops N columns" and names the columns; the staged rows of the Filters panel are another step, so changing them does NOT end it."""
    w = _world(monkeypatch)
    _flush()
    drop_world = world_of("audit", "r", ("a", "b"), [], [], ())
    record = TrialRecord(drop_world, ("T3:p",), (), TrialResult(("sig",), (PlaceEffect("T3:p", "Plot p", 10, 10, "table changed", 8, 6),), ()), drop_condition_lines(["identity", "length"]), 0, KIND_DROP)
    _set(w, record)
    html = _html(w)
    assert "name of T3:p: the step drops 2 columns of 8 here (table changed)." in html and "Drop the columns: identity, length. No row is removed." in html
    assert "removes" not in html, "no word of rows in the panel of a drop"
    _flush()
    with reactive.isolate():
        w.pending.set([])                                   # the staged condition changes: a drop trial is not about it
    _flush()
    with reactive.isolate():
        assert w.trial_state.get() is not None and w.notes == [], "MUTATION: the world of a drop reads the staged rows"
        w.mode.set(False)
    _flush()
    assert len(w.notes) == 1 and "You left Audit mode" in w.notes[0], "the other causes still end it"


# -- the column drop is tried (FLOW-3) ----------------------------------------------------------------------------------
class _TrialThatCounts(_Trial):
    """Gives the engine's answer without an engine: one effect for each tried place."""

    def __init__(self):
        super().__init__()
        self.tried = []

    def try_step(self, recipe_id, applied, tried, plans=None):
        self.tried.append(list(tried))
        return TrialResult(("sig",), tuple(PlaceEffect(n["place"], n["place"], 10, 10, "table changed", 3, 2) for n in tried[:1]))


def _drop_world(monkeypatch, columns=(("identity", "Float64"), ("length", "Int64")), shown="T3:p", gate=None, places=(("T3:p",), "")):
    trial = _TrialThatCounts()
    monkeypatch.setattr(trial_handlers, "trial_places", lambda shown_place, chosen, graph, lineage: places)
    if gate is not None:
        monkeypatch.setattr(trial_handlers.key_drop, "DropGate", lambda raw, plans: SimpleNamespace(problem=gate))
    w = _world(monkeypatch, trial=trial, shown_place=lambda: shown, columns_at=lambda p: list(columns), open_graph=lambda: object(), lineage_calc=lambda: (object(), ""),
               recipe_raw=(lambda: {}) if gate is not None else None)
    _flush()
    return w


def _try_drop(w, selected):
    w.live.set("preview_col_selector", selected)
    w.live.set("step_kind", "drop")
    w.live.set("step_try", (_peek(w.live.values["step_try"]) or 0) + 1 if "step_try" in w.live.values and _peek(w.live.values["step_try"]) else 1)
    _flush()


def test_the_columns_the_chooser_does_not_select_are_tried_at_the_place_shown_as_a_drop_trial(monkeypatch):
    w = _drop_world(monkeypatch)
    _try_drop(w, ["length"])
    record = _peek(w.trial_state)
    assert record is not None and record.kind == KIND_DROP and record.places == ("T3:p",)
    assert [(n["node_type"], n["params"]["column"], n["place"]) for n in record.nodes] == [("drop_column", "identity", "T3:p")], "the deselected column, written at the place shown"
    assert record.condition == ("Drop the column: identity. No row is removed.",)
    assert w.notes and "The drop is tried" in w.notes[-1] and "bar above the table" in w.notes[-1], "the answer is in the bar: the notice says where to look"
    assert "the step drops 1 column of 3 here" in _html(w)


def test_nothing_deselected_or_no_result_data_shown_tries_nothing_and_says_why(monkeypatch):
    w = _drop_world(monkeypatch)
    _try_drop(w, ["identity", "length"])
    assert _peek(w.trial_state) is None and w.trial.tried == [] and "No column is deselected" in w.notes[-1]
    w2 = _drop_world(monkeypatch, shown="T1:ResFinder")
    _try_drop(w2, ["length"])
    assert _peek(w2.trial_state) is None and w2.trial.tried == [] and "Result data (T3) of a plot" in w2.notes[-1]


def test_a_column_that_is_not_in_the_table_at_a_place_is_named_and_nothing_is_tried(monkeypatch):
    w = _drop_world(monkeypatch, columns=(("identity", "Float64"),))
    _try_drop(w, [])
    assert _peek(w.trial_state) is not None, "the one column of the table is deselected: it is dropped"
    w2 = _drop_world(monkeypatch, columns=(("identity", "Float64"),), places=(("T3:p", "T3:q"), ""))
    w2.live.set("preview_col_selector", [])
    monkeypatch.setattr(trial_handlers, "drop_fit_problem", lambda *a, **k: "The drop does not fit every place. name of T3:q: identity is not in the table there. Nothing was tried.")
    w2.live.set("step_kind", "drop")
    w2.live.set("step_try", 5)
    _flush()
    assert _peek(w2.trial_state) is None and "does not fit every place" in w2.notes[-1]


def test_a_key_that_a_later_join_reads_is_refused_at_try_with_the_sentence_of_the_rule_and_nothing_is_tried(monkeypatch):
    """The rule is `utils.key_drop` (by place, D-0358, D-0371; its own tests are in libs/utils/tests/test_key_drop.py). HOME asks it for every place of the trial and follows its answer."""
    asked = []
    def gate(place, columns):
        asked.append((place, list(columns)))
        return "The column identity is read as a key by the join J later on, so it cannot be dropped here." if "identity" in columns else None
    w = _drop_world(monkeypatch, gate=gate)
    _try_drop(w, ["length"])
    assert asked == [("T3:p", ["identity"])] and _peek(w.trial_state) is None and w.trial.tried == []
    assert "read as a key by the join J" in w.notes[-1] and "Nothing was tried" in w.notes[-1]
    _try_drop(w, ["identity"])                                   # the other column is not a key: tried
    assert _peek(w.trial_state) is not None and asked[-1] == ("T3:p", ["length"])


def test_the_fold_out_says_which_kind_of_step_the_open_trial_is(monkeypatch):
    """The switch of the step bar may be moved while a trial is open: the trial stays what it was tried as, and its first line says so. MUTATION: the summary is a fixed text: the drop assert fails."""
    w = _world(monkeypatch)
    _flush()
    _set(w, _record(w))
    assert "Result of Try: a condition (not applied)" in _html(w)
    record = _record(w)
    _set(w, TrialRecord(record.world, record.places, record.nodes, record.result, record.condition, record.serial, KIND_DROP))
    html = _html(w)
    assert "Result of Try: a column drop (not applied)" in html and "a condition (not applied)" not in html
