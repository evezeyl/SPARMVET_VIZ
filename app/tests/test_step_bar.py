"""The step bar of HOME in Audit mode: its rules (`app/modules/step_bar.py`) and its outputs (`app/handlers/step_bar_handlers.py`) on the real reactive graph, without a browser (D-0663, D-0672).

What the design expects: the bar is the one entry that creates a step; it exists in Audit mode only; one kind of step at a time (a condition or a column drop), one button Try that is off with a plain
sentence when the step cannot be tried; the bar draws its inside only when the mode changes (R4: typing, choosing columns, staging rows never draw it again, only the two small outputs beside the
switch read them); the drop names the columns the chooser does not select.

# @deps
# consumes: app/modules/step_bar.py, app/handlers/step_bar_handlers.py
# @end_deps

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_step_bar.py -q
MUTATION (seen failing, then restored): `step_bar_ui` reads the staged rows (the draw-count test fails); `try_state` ignores the kind (the kind tests fail).
"""
import asyncio
from types import SimpleNamespace

from shiny import reactive, render

import app.handlers.step_bar_handlers as step_bar_handlers
from app.modules.audit_try import KIND_DROP, KIND_FILTER
from app.modules.step_bar import (CONDITION_HINT, NEEDS_CONDITION, NEEDS_DESELECTED, NEEDS_T3_FOR_DROP, STEP_BAR_LABEL, drop_words, kind_of_input, try_state)
from app.tests.test_session_clicks_once import LiveInput

ROW = {"column": "identity", "op": "lt", "value": 99.0, "dtype": "Float64", "na": "remove"}
COLUMNS = ["identity", "length", "gene"]


# ── the rules ─────────────────────────────────────────────────────────────────────────────────────────────────────

def test_the_kind_is_the_condition_unless_the_switch_says_drop():
    assert kind_of_input(KIND_DROP) == KIND_DROP
    for value in (KIND_FILTER, None, "", "anything", 0):
        assert kind_of_input(value) == KIND_FILTER


def test_a_condition_can_be_tried_with_at_least_one_staged_row_and_says_why_not_without():
    assert try_state(KIND_FILTER, 0, "T3:p", COLUMNS, None) == (False, NEEDS_CONDITION, ())
    assert try_state(KIND_FILTER, 2, "T1:t", COLUMNS, None) == (True, "", ()), "a condition is tried at a table shown too"


def test_a_drop_needs_the_result_data_of_a_plot_shown_and_a_deselected_column():
    assert try_state(KIND_DROP, 0, None, COLUMNS, ["gene"]) == (False, NEEDS_T3_FOR_DROP, ())
    assert try_state(KIND_DROP, 0, "T1:t", COLUMNS, ["gene"]) == (False, NEEDS_T3_FOR_DROP, ())
    assert try_state(KIND_DROP, 0, "T3:p", COLUMNS, COLUMNS) == (False, NEEDS_DESELECTED, ()), "every column selected: nothing to drop"
    assert try_state(KIND_DROP, 0, "T3:p", COLUMNS, None) == (False, NEEDS_DESELECTED, ()), "no chooser on the page: nothing is deselected"
    assert try_state(KIND_DROP, 5, "T3:p", COLUMNS, ["identity", "gene"]) == (True, "", ("length",)), "the staged rows are another step: a drop reads the chooser only"


def test_the_drop_is_told_in_words_with_the_columns_named():
    assert drop_words(()) == "No column is deselected: nothing to drop yet."
    assert drop_words(("length",)) == "Drop the column: length. No row is removed."
    assert drop_words(("length", "gene")) == "Drop the 2 columns: length, gene. No row is removed."


# ── the outputs ─────────────────────────────────────────────────────────────────────────────────────────────────

def _flush(times=4):
    async def go():
        for _ in range(times):
            await reactive.flush()
    asyncio.run(go())


def _world(monkeypatch, shown="T3:p"):
    found = {}
    monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
    live = LiveInput()
    for name in ("step_kind", "preview_col_selector"):
        live.set(name, None)
    pending, mode, place = reactive.Value([]), reactive.Value(True), reactive.Value(shown)

    def output(fn):
        found[fn.__name__] = fn
        return fn
    step_bar_handlers.define_step_bar_server(
        live, output, SimpleNamespace(), in_audit=lambda: mode.get(),
        safe_input=lambda i, k, d: (live.values[k].get() if k in live.values and live.values[k].get() is not LiveInput.MISSING else d),
        pending_filters=pending, shown_place=lambda: place.get(), columns_at=lambda p: [(c, "String") for c in COLUMNS] if p else None)
    return SimpleNamespace(found=found, live=live, pending=pending, mode=mode, place=place)


def _html(w, name):
    with reactive.isolate():
        return str(w.found[name]())


def test_the_bar_is_empty_in_exploration_and_a_labelled_region_in_audit_mode(monkeypatch):
    w = _world(monkeypatch)
    html = _html(w, "step_bar_ui")
    assert f'aria-label="{STEP_BAR_LABEL}"' in html and 'role="region"' in html and 'id="shown_band_ui"' in html, "the band that names the item shown is the first line of the bar"
    assert 'name="step_kind"' in html and 'value="filter" checked' in html and "Condition on rows" in html and "Drop columns" in html, "one plain switch, the condition by default"
    assert 'id="trial_panel_ui"' in html and "Counting the rows each place loses..." in html
    w.mode.set(False)
    for name in ("step_bar_ui", "step_bar_actions_ui", "step_bar_drop_ui", "step_bar_condition_ui"):
        assert "<" not in _html(w, name).replace("<div></div>", ""), f"{name} draws nothing in Exploration"


def test_try_is_off_with_its_reason_and_on_once_the_step_can_be_tried(monkeypatch):
    w = _world(monkeypatch)
    off = _html(w, "step_bar_actions_ui")
    assert 'id="step_try"' in off and "disabled" in off and NEEDS_CONDITION in off, "never a silent grey"
    with reactive.isolate():
        w.pending.set([dict(ROW)])
    on = _html(w, "step_bar_actions_ui")
    assert "disabled" not in on and NEEDS_CONDITION not in on


def test_the_kind_drop_reads_the_column_chooser_and_names_the_columns(monkeypatch):
    w = _world(monkeypatch)
    w.live.set("step_kind", KIND_DROP)
    assert NEEDS_DESELECTED in _html(w, "step_bar_actions_ui") and NEEDS_DESELECTED in _html(w, "step_bar_drop_ui")
    w.live.set("preview_col_selector", ["identity", "gene"])
    assert "Drop the column: length." in _html(w, "step_bar_drop_ui") and "disabled" not in _html(w, "step_bar_actions_ui")
    with reactive.isolate():
        w.place.set("T1:t")
    assert NEEDS_T3_FOR_DROP in _html(w, "step_bar_drop_ui") and "disabled" in _html(w, "step_bar_actions_ui")


def test_the_condition_part_names_the_staged_rows_or_says_how_to_build_one(monkeypatch):
    w = _world(monkeypatch)
    assert CONDITION_HINT in _html(w, "step_bar_condition_ui")
    with reactive.isolate():
        w.pending.set([dict(ROW)])
    html = _html(w, "step_bar_condition_ui")
    assert "identity" in html and CONDITION_HINT not in html


def test_the_inside_of_the_bar_is_drawn_when_the_mode_changes_and_never_while_the_user_builds_a_step(monkeypatch):
    """R4: the bar mounts the switch and the fold-out; typing, staging rows, choosing columns and the switch itself must not draw it again (the switch would be put back, the fold-out lost).
    MUTATION: `step_bar_ui` reads `pending_filters` (or the chooser, or the switch): the count below grows."""
    w = _world(monkeypatch)
    draws = []

    @reactive.Effect
    def _watch():
        w.found["step_bar_ui"]()
        draws.append(1)
    _flush()
    assert len(draws) == 1
    with reactive.isolate():
        w.pending.set([dict(ROW)])
    w.live.set("step_kind", KIND_DROP)
    w.live.set("preview_col_selector", ["gene"])
    with reactive.isolate():
        w.place.set("T1:t")
    _flush()
    assert len(draws) == 1, "building a step does not draw the bar"
    with reactive.isolate():
        w.mode.set(False)
    _flush()
    assert len(draws) == 2, "a change of the mode does"
