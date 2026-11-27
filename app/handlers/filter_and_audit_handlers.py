"""app/handlers/filter_and_audit_handlers.py
The filter builder of the Filters panel (HOME).

Extracted from home_theater.py in Phase 24-D (ADR-051). FLOW-3 (2026-11-27): the old way of creating an audit step is gone from this file (the pop-up that asked "This plot only / All plots /
All plots except" and the button "Send to Audit", the button of the lineage panel, the column drop of the old way): a step is created in ONE way, show an item, stage the step here, Try, (mark),
reason, "Add to audit pipeline" (`trial_handlers.py`, D-0662, D-0663, D-0672). This file builds the CONDITION (the staged rows) and applies it in Exploration. The form is mounted here in both modes; in Audit mode the step bar
(`step_bar_handlers.py`) names the staged condition and holds the one button Try.

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_filter_audit_server, function:form_slots (the slots of the one form, mounted by the Filters panel), output:filter_whole_number_ui (D-0376), effect:_clear_filters_on_view_change (replaces _clear_filters_on_recipe_change, slice B), output:sidebar_filters, output:filter_rows_ui, output:filter_form_ui, output:filter_type_ui, output:filter_op_ui, output:filter_value_ui, output:filter_closed_text_ui, output:filter_na_ui, output:filter_na_text_ui, output:filter_controls_ui, input:fb_na, input:filter_apply
# consumes: app/modules/t3_audit_engine.py (view_change_notice, column_is_in_frame, staged_filter_row (view=), describe_filter, op_choice_label, dialog_value, value_choices, column_types, ops_for_column, value_widget_for, value_box_kind, between_ends, BetweenIncomplete, number_range, column_type_line, closed_phrase, CLOSED_CHOICES, dialog_schema_signature, dialog_rows_signature, column_bounds, compose_date, compose_time, compose_datetime, compose_duration, control_hint, LIST_ON_DEMAND_FROM, list_note), libs/utils/src/utils/filter_values.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py, app/src/bootloader.py (is_enabled), shiny
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-049, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-085, .claude/rules/ui_implementation_contract.md#8
# @end_deps

import logging

from shiny import reactive, render, ui

from app.src.bootloader import bootloader
from app.modules.t3_audit_engine import (
    describe_filter, op_choice_label, OP_WORDS, staged_filter_row,
    CLOSED_CHOICES, closed_phrase, column_type_line, column_types, number_range, ops_for_column,
    dialog_value, not_offered_line, between_ends, BetweenIncomplete, value_box_kind, value_choices, value_widget_for, dialog_rows_signature, dialog_schema_signature,
    column_bounds, column_is_in_frame, refuse_decimal_for_whole_numbers, view_change_notice, compose_date, compose_datetime, compose_duration, compose_time, control_hint, LIST_ON_DEMAND_FROM, list_note,
)
from app.modules.audit_view import AUDIT_ERRORS
from utils.filter_values import UNIT_NS, FilterValueError, kind_of
from utils.missing_values import dialog_lines, na_choice_texts
from utils.na_choice import default_na, na_of

_log = logging.getLogger(__name__)


def _time_boxes(suffix: str, d: dict):
    """The three boxes of a time of day: hour, minute, second (the seconds take up to nine digits). `d` holds the defaults.

    PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 3: three number boxes for a time of day (Shiny for Python has no time input).
    """
    def box(label, id_, value, **kw):
        return ui.div(ui.tags.small(label, class_="text-muted"), ui.input_numeric(id_, label=None, value=value, **kw), class_="spv-flex-1")
    return ui.div(
        box("hour", f"fb_h{suffix}", d.get("h", 0), min=0, max=23, step=1),
        box("minute", f"fb_min{suffix}", d.get("min", 0), min=0, max=59, step=1),
        box("second", f"fb_s{suffix}", d.get("s", 0), min=0, step=1),
        class_="d-flex gap-1",
    )


# Sends the raw text of every date box of the filter dialog to the server beside the date the widget read (`fb_value_raw`, `fb_value_lo_raw`...):
# the widget "repairs" free text (today for a partial text, a rolled-over day for 2023-02-30), so `compose_date` reads the text itself, strictly.
# Registered once per page; it also sends the text at insertion, so a stale value of an earlier box is never compared with a new one.
_DATE_RAW_SCRIPT = """
(function () {
  function send(input) {
    var box = input.closest('.shiny-date-input');
    if (box && box.id && window.Shiny && Shiny.setInputValue) Shiny.setInputValue(box.id + '_raw', input.value, {priority: 'event'});
  }
  if (!window.__spvDateRaw) {
    window.__spvDateRaw = true;
    $(document).on('input change keyup blur changeDate', '.shiny-date-input[id^="fb_value"] input', function () { send(this); });
  }
  document.querySelectorAll('.shiny-date-input[id^="fb_value"] input').forEach(send);
})();
"""


def _date_picker(id_: str, value, empty: bool = False):
    """A date picker that never chooses a date for the user.

    The widget (bootstrap-datepicker) repairs what is typed: Enter in an empty box chooses the highlighted day (today), and with the
    default `forceParse` a partial text, a text that is not a date or 2023-02-30 is replaced by another date in the box. Keyboard
    navigation is off (no Enter that picks a day; the arrow keys of the calendar do not work, typing the date does) and `forceParse` is
    off (the box keeps what the user typed, so it can be corrected). The raw text is sent to the server (`_DATE_RAW_SCRIPT`) and read
    strictly by `compose_date`. The calendar stays for the mouse.

    PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 8: keep the calendar and read the typed text strictly (option: a plain text box with the calendar only as a helper).
    """
    # `empty` (an end of between): value "" writes an empty initial date; with None the widget fills in today, a date the user did not choose (D-0504)
    tag = ui.input_date(id_, label=None, value="" if empty else value, format="yyyy-mm-dd")
    for child in tag.children:
        if getattr(child, "name", None) == "input":
            child.attrs["data-date-keyboard-navigation"] = "false"
            child.attrs["data-date-force-parse"] = "false"
    return ui.TagList(tag, ui.tags.script(ui.HTML(_DATE_RAW_SCRIPT)))


# The ends of `between` start empty (D-0504): no default is a value the user chose. The keys are present with None so that the boxes read it.
_EMPTY_END = {"date": None, "h": None, "min": None, "s": None, "number": None}


def _control(kind: str, suffix: str, d: dict):
    """The control of one value of a date, date and time, time of day or duration; `suffix` is "" (one value), "_lo" or "_hi" (between)."""
    if kind == "date":
        return _date_picker(f"fb_value{suffix}", d.get("date"), empty=suffix != "")
    if kind == "datetime":
        # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 5: a date and time is a date picker plus the three boxes of a time.
        return ui.div(_date_picker(f"fb_value{suffix}", d.get("date"), empty=suffix != ""), _time_boxes(suffix, d))
    if kind == "time":
        return _time_boxes(suffix, d)
    # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 4: a duration is a number with a choice of 8 units (ns, us, ms, s, min, h, d, w).
    return ui.div(  # duration: a number and its unit
        ui.div(ui.input_numeric(f"fb_value{suffix}", label=None, value=d.get("number", 0), step=1), class_="spv-flex-1"),
        ui.div(ui.input_select(f"fb_unit{suffix}", label=None, choices=list(UNIT_NS), selected=d.get("unit", "s")), class_="spv-flex-1"),
        class_="d-flex gap-1",
    )


def form_slots() -> list:
    """The outputs of the ONE form of a condition: the staged rows, the add-row form, the choice for missing values and the buttons. The Filters panel mounts them (in both modes)."""
    return [
        ui.output_ui("filter_rows_ui"),
        ui.output_ui("filter_form_ui"),
        ui.output_ui("filter_na_ui"),
        ui.output_ui("filter_na_text_ui"),
        ui.div(ui.output_ui("filter_controls_ui"), class_="mt-2 px-1"),
    ]


def define_filter_audit_server(input, output, session, *,
                                applied_filters, _pending_filters,
                                home_state,
                                in_audit, data_view, view_source_table, current_view_key, active_home_subtab,
                                safe_input,
                                _resolve_active_spec, _resolve_active_lf,
                                _spec_discrete_axes, _table_identity,
                                notification_log=None,
                                audit_write_ok=None, trial_alive=None):
    """Register the filter UI (the condition builder, Exploration's Apply, the button Try of Audit mode).

    Reactive deps (kwargs) — all shared with home_theater.define_server:
      applied_filters       reactive.Value[list]   — committed transient filters (T1/T2 plot view)
      _pending_filters      reactive.Value[list]   — staging rows in the add-row form (the condition being built)
      home_state            reactive.Value[dict] | None — audit steps state, active subtab, etc. (read: the form is mounted again when the applied steps change)
      in_audit()            → bool                 — True in Audit mode: the ONE function of HOME (audit on, interactive, mode "audit"; review F4)
      current_view_key()    → tuple | None         — `view_key` of the view on screen (None without an open recipe): an exploration filter carries it
      data_view             reactive.Value[str]    — "SRC"|"T1"|"T2"|"T3": the table the data preview shows (D-0310)
      active_home_subtab    reactive.Value[str]    — current home plot subtab id
    Helpers (kwargs):
      safe_input(input, key, default) → value
    Closures from home_theater.define_server (kwargs):
      _resolve_active_spec(p_id) → spec dict | None
      view_source_table()        → str | None   — the source table of the Source choice (None for another choice)
      _resolve_active_lf(spec, tier=None) → LazyFrame — the table of the data choice, or of `tier`
      _spec_discrete_axes(spec)  → (set, set)  — discrete x, discrete y columns
      _table_identity(spec, tier) → tuple | None — which stored table the dialog reads (`stored_table_identity`); None when no
                                    key says which rows it holds (the rows signal is then never equal)
      audit_write_ok()           → bool — True when the item shown in Audit mode is the Result data (T3) of the plot OPEN (the form then reads the audited table); without it only the data choice counts
      trial_alive()              → bool — True while a step is being tried (`trial_handlers`): the staged condition is then the trial's condition, so a change of the item shown does NOT clear it
                                    (a trial may be looked at on every item it reaches); it is cleared, with the usual notice, when the trial ends and the table shown is another one
    """

    _in_audit = in_audit   # one function for HOME and these handlers: `home_theater._in_audit`

    def _audit_t3_shown() -> bool:
        """True in Audit mode while the Result data (T3) of the open plot is shown: the table the form reads is then the AUDITED one (the applied steps are in it)."""
        return _in_audit() and data_view.get() == "T3" and (audit_write_ok is None or audit_write_ok())

    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    def _clear_exploration_filters() -> tuple[int, int]:
        """The one reset of the exploration filters: empties the staged and the applied list, returns how many rows each held.

        Used by the Reset button and the change of view. Audited steps live elsewhere
        (home_state) and are never touched here.
        """
        n_pending = len(_pending_filters.get())
        n_applied = len(applied_filters.get())
        _pending_filters.set([])
        applied_filters.set([])
        return n_pending, n_applied

    # WHY: ADR-099 point 1 - exploration filters are cleared on a recipe change; a filter built on recipe A would
    # silently filter recipe B when it has a column of the same name (found 2026-11-18, switch check).
    # Slice B (D-0311, D-0178): a filter is built on the table of the view shown, so it is cleared, with a notice, when that table changes:
    # the data choice, the source table, the table the open plot reads (D-0505, D-0506: the filter belongs to the table, so a plot on the same table
    # clears nothing), the mode (D-0361; exploration filters do not exist in Audit mode) and the recipe. One view key (`view_key`) says what the view is; the notice names the first cause that changed.
    # Idempotent guard: only a real change of the key clears; the selector input is re-created when the user returns to
    # HOME from another space and then reports the same id again, which must not clear anything or notify.
    _seen_view = {"key": None}

    @reactive.Effect
    def _clear_filters_on_view_change():
        rid = safe_input(input, "data_analysis_recipe_id", None)
        if rid is None:
            return
        key = current_view_key()
        # FLOW-1 (PROVISIONAL, the builder's choice; D-0654 and D-0311 name a condition being BUILT): while a trial exists the staged condition is the trial's, and showing another item to look at
        # the trial must not clear it (that would end the trial the moment the user looks at what it changed). The effect reads the trial, so it runs again when the trial ends; `_seen_view` is
        # left alone meanwhile, so the clearing then happens against the view the condition was built on, with the usual notice.
        if trial_alive is not None and trial_alive():
            return
        with reactive.isolate():
            previous = _seen_view["key"]
            _seen_view["key"] = key
            if previous is None or previous == key:
                return
            n_pending, n_applied = _clear_exploration_filters()
            if n_pending or n_applied:
                # HOME-WALK C: the filters were removed and the notice says so: the form goes back to its start with them (its column, operator and value
                # would otherwise still name the pick of the removed filters). With nothing to remove the form is kept: a change of view that leaves the
                # columns as they are keeps what the user is choosing (`test_filter_form_survives_rerender.py`).
                _form_reset.set(_form_reset.get() + 1)
            text = view_change_notice(previous, key, n_pending, n_applied)
            if text:
                _notify(text, type="warning", duration=10)

    @output
    @render.ui
    def sidebar_filters():
        """
        Phase 21-F-1: Static shell — rendered once, never re-renders.
        Mounts stable output slots; child outputs re-render independently.
        Apply label and status are in filter_rows_ui to avoid shell re-renders.
        """
        # pipeline-static: no interactivity — static message, no filter UI
        if not bootloader.is_enabled("interactivity_enabled"):
            return ui.div(
                ui.tags.small(
                    "Filters are set by the pipeline configuration.",
                    class_="text-muted d-block px-1 spv-text-sm"
                )
            )
        # pipeline-exploration-simple: interactivity on but no T3 audit — show disclaimer
        # Proxy: metadata_ingestion_enabled=false identifies simple/passive-only app features files
        disclaimer = None
        if not bootloader.is_enabled("metadata_ingestion_enabled"):
            disclaimer = ui.div(
                ui.tags.small(
                    "Exploration only — filters are not saved and do not modify data permanently.",
                    class_="text-warning d-block px-1 mb-1 border-start border-warning ps-2 spv-text-xs"
                )
            )
        # The form is built here in both modes (one mount: the ids of its inputs exist once in the page). In Audit mode the step bar above the data preview (`step_bar_handlers`) names the staged
        # condition and holds the one button Try; the form could not be moved into the bar soundly (see step_bar_handlers.py, "WHY THE FORM STAYS IN THE FILTERS PANEL").
        return ui.div(
            disclaimer or ui.div(),
            *form_slots(),
            class_="spv-text-sm"
        )

    @output
    @render.ui
    def filter_rows_ui():
        """Pending filter rows. Reads _pending_filters only — re-renders on Add/Remove."""
        pending = _pending_filters.get()
        if not pending:
            return ui.tags.small(
                "No filters yet. Add rows below.", class_="text-muted d-block px-1 mb-1 spv-text-xs",
            )
        rows = []
        for i, f in enumerate(pending):
            col = f.get("column", "")
            op = f.get("op", "eq")
            val = f.get("value", "")
            dtype_str = f.get("dtype", "")
            rows.append(ui.div(
                ui.div(
                    ui.tags.small(
                        describe_filter(col, op, val, na_of(f), f.get("closed")),
                        class_="text-dark spv-filter-text",
                    ),
                    ui.tags.small(f" [{dtype_str}]", class_="text-muted spv-text-micro"),
                    class_="flex-grow-1"
                ),
                *([] if not bootloader.is_enabled("interactivity_enabled") else [
                    ui.input_action_button(
                        f"filter_remove_{i}", "🗑",
                        class_="btn btn-sm btn-link p-0 text-danger",
                    )
                ]),
                class_="d-flex align-items-center gap-2 mb-1 px-1 py-1 border rounded bg-light",
            ))
        return ui.div(*rows)

    def _discrete_columns(spec) -> set:
        """The columns the active plot uses as a discrete axis (a number column among them is picked from a list)."""
        disc_x, disc_y = _spec_discrete_axes(spec)
        return set(disc_x) | set(disc_y)

    @reactive.Calc
    def _dialog_table():
        """(table, {column: dtype}, discrete-axis columns) of the active plot, for the add-row form.

        The type comes from the schema of the table, never from a sample of rows (ADR-104 point 7). A table that cannot
        be built or read gives (None, {}, set()) and the error is logged, not swallowed.
        """
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        lf = _active_frame()
        try:
            types = column_types(lf) if lf is not None else {}
        except Exception:
            _log.exception("filter dialog: the columns of the table could not be read")
            return None, {}, set()
        return lf, types, _discrete_columns(spec)

    def _dialog_table_now():
        """The table of the dialog read fresh and without subscribing (the signal and fresh-read pattern of
        `app/tests/test_dialog_mirror_window.py`): the outputs depend on the signals below, never on the Calc, because a Calc
        invalidates its readers every time it recomputes, even when the result is the same."""
        with reactive.isolate():
            return _dialog_table()

    # WHY: found 2026-11-19 (FORM RESET). The form read `_dialog_table()` directly, so every recompute of the table (a change of the data choice,
    # a plot tab, a recipe load) mounted the column select again, even when the columns and the rows were the same. A render that
    # started before the server had received the user's new column put the first column back; nothing told the user (D-0050).
    # The two Values change only when the thing they stand for changes (R3, idempotent guard); `_signal_dialog_table` sets them.
    _dialog_schema_signal = reactive.Value(None)   # columns, types and discrete axes: what the form's selects are made of
    _dialog_rows_signal = reactive.Value(None)     # which rows the table holds: what the value widget is made of
    # HOME-WALK C (D-0311, D-0361): when the filters are cleared because the view changed, the form is cleared with them. The counter makes the form's
    # outputs mount again; each output that keeps a choice of the user (`fb_col`, `fb_op`) ignores it once for every new count (`_form_is_fresh`).
    _form_reset = reactive.Value(0)
    _form_seen: dict = {}

    def _form_is_fresh(output_name: str) -> bool:
        gen = _form_reset.get()
        fresh = _form_seen.get(output_name, 0) != gen
        _form_seen[output_name] = gen
        return fresh

    @reactive.Effect
    def _signal_dialog_table():
        # The Filters panel does not exist without interactivity (`sidebar_filters` shows a static message): nothing to signal.
        if not bootloader.is_enabled("interactivity_enabled"):
            return
        try:
            lf, types, disc = _dialog_table()
            schema = dialog_schema_signature(types, disc)
            subtab = active_home_subtab.get()
            tier = data_view.get()
            audit_t3 = _audit_t3_shown()
            identity = None
            if lf is not None:
                try:
                    identity = _table_identity(_resolve_active_spec(subtab.removeprefix("subtab_") if subtab else None), tier)
                except Exception:
                    # No identity, no way to tell two tables apart: the signature is never equal (one more render).
                    _log.exception("filter dialog: the stored table the form reads could not be identified")
            # The same condition as `_active_frame`: the audited steps apply on T3 in Audit mode only.
            rows = dialog_rows_signature(identity, _place_nodes_now() if audit_t3 else [])
        except Exception as exc:
            # The outputs read the table again and show the error themselves; this only makes them run again when it changes.
            _log.exception("filter dialog: the table of the form could not be read")
            schema = rows = ("error", f"{type(exc).__name__}: {exc}")
        with reactive.isolate():
            if _dialog_schema_signal.get() != schema:
                _dialog_schema_signal.set(schema)
            if _dialog_rows_signal.get() != rows:
                _dialog_rows_signal.set(rows)

    # WHY: found 2026-11-22 with timelines over 20 repeats. `filter_value_ui` read `fb_op`, so the value box was drawn again by the server at
    # every choice of the operator, also when the box did not change kind. A number typed before that redraw arrived was thrown away and
    # "+ Add row" then added the box's default (the column's minimum): a filter with another value than the typed one, and no word (D-0050).
    # This Value holds the kind of box (`value_box_kind`) and changes only when the kind changes (R3, idempotent guard). The Effect has a
    # higher priority than the outputs, so that on a new column the kind is up to date when the value box is drawn.
    _value_kind_signal = reactive.Value(None)

    @reactive.Effect(priority=10)
    def _signal_value_kind():
        if not bootloader.is_enabled("interactivity_enabled"):
            return
        _dialog_schema_signal.get()
        _form_reset.get()
        _lf, types, disc = _dialog_table_now()
        col = _selected_column(types)
        kind = value_box_kind(types.get(col), col in disc, safe_input(input, "fb_op", None))   # reads fb_col and fb_op: the dependencies
        with reactive.isolate():
            if _value_kind_signal.get() != kind:
                _value_kind_signal.set(kind)

    def _selected_column(types: dict):
        col = safe_input(input, "fb_col", next(iter(types), None))
        return col if col in types else next(iter(types), None)

    def _op_choices(dtype, discrete_axis: bool) -> dict:
        ops = ops_for_column(dtype, discrete_axis) if dtype is not None else ["in", "not_in", "eq", "ne"]
        return {o: op_choice_label(o) for o in ops}

    @output
    @render.ui
    def filter_form_ui():
        """Shell of the add-row form: the column select and the slots of its type line, operator and value.

        Reads the table the filter acts on only (R4, ui_implementation_contract.md section 14: it does not read the
        widgets it mounts, apart from an isolated read to keep the column the user chose when the plot changes).
        It depends on the schema signal, not on the table: a recompute that gives the same columns, types and discrete axes
        (a change of the data choice on a table without tier-2 steps, a plot tab with the same table) does not mount it again, so the
        column, operator and value the user has just chosen are not put back to the first column while the server has not yet
        received them.
        """
        _dialog_schema_signal.get()   # the dependency: the form is mounted again when its columns or types change, not when the table is rebuilt
        _form_reset.get()             # and when the filters are cleared by a change of view (HOME-WALK C)
        _lf, types, _disc = _dialog_table_now()
        col_choices = {c: f"{c}  [{types[c]}]" for c in types}
        with reactive.isolate():
            fresh = _form_is_fresh("form")
            kept = None if fresh else safe_input(input, "fb_col", None)
        selected = kept if kept in types else next(iter(types), None)
        return ui.div(
            ui.tags.small("Add filter row:", class_="fw-semibold text-muted d-block mb-1"),
            ui.input_select("fb_col", label=None, choices=col_choices, selected=selected),
            ui.output_ui("filter_type_ui"),
            ui.div(
                ui.output_ui("filter_op_ui"),
                ui.div(ui.output_ui("filter_value_ui"), ui.output_ui("filter_whole_number_ui"),
                       ui.output_ui("filter_add_reason_ui"), class_="spv-flex-1"),
                class_="d-flex gap-1 align-items-center"
            ),
            class_="mt-2 pt-2 border-top spv-text-sm",
        )

    @output
    @render.ui
    def filter_type_ui():
        """What the chosen column holds, in words ("Year holds whole numbers (Int64)."); reads fb_col and the schema signal."""
        _dialog_schema_signal.get()
        _form_reset.get()
        _lf, types, _disc = _dialog_table_now()
        col = _selected_column(types)
        text = column_type_line(col, types[col]) if col in types else ""
        return ui.tags.small(text, class_="text-muted d-block spv-text-meta", id="fb_col_type")

    @output
    @render.ui
    def filter_op_ui():
        """The operators of the chosen column; reads fb_col and the schema signal. The operator kept is read isolated."""
        _dialog_schema_signal.get()
        _form_reset.get()
        _lf, types, disc = _dialog_table_now()
        col = _selected_column(types)
        choices = _op_choices(types.get(col), col in disc)
        if not choices:
            return ui.tags.small(f"{not_offered_line(col, types.get(col))} Suggestion: filter another column.", class_="text-warning d-block")
        with reactive.isolate():
            kept = None if _form_is_fresh("op") else safe_input(input, "fb_op", None)
        return ui.input_select("fb_op", label=None, choices=choices, selected=kept if kept in choices else next(iter(choices)),
                               width="100px")

    @output
    @render.ui
    def filter_value_ui():
        """The value widget for the chosen column and operator; reads fb_col and fb_op, never the widget it mounts.

        List of values: from the whole column. Number box: the range of the whole column. Two number boxes and the four
        ends for `between`. A comparison on a number column that is a discrete axis uses the number box (Eve, 2026-11-14).
        It depends on the schema signal and the rows signal: a rebuilt table with the same rows does not mount the box again and
        wipe the value the user has typed. For the same reason it does not depend on the operator but on the KIND of box the operator
        needs (`_value_kind_signal`): a change of operator within one kind (">=" to ">") leaves the box, and what is typed in it,
        as it is; the operator is read here without subscribing (D-0050).
        """
        _dialog_schema_signal.get()
        _dialog_rows_signal.get()
        _form_reset.get()
        _value_kind_signal.get()   # the dependency: the box is mounted again when its kind changes, not when the operator does
        lf, types, disc = _dialog_table_now()
        col = _selected_column(types)
        dtype = types.get(col)
        with reactive.isolate():
            widget = value_box_kind(dtype, col in disc, safe_input(input, "fb_op", None))
        if widget is None:
            return ui.div()  # the operator slot says why (filter_op_ui)
        if widget == "list":
            try:
                labels = list(value_choices(lf, col))
                options = {"placeholder": "Select value(s)…", "plugins": ["remove_button"], "dropdownParent": "body"}
                if len(labels) <= LIST_ON_DEMAND_FROM:
                    return ui.input_selectize("fb_value", label=None, choices=labels, selected=[], multiple=True, options=options)
                # PROVISIONAL (L10): a long list is served on demand while typing (at most 1000 matches of a search); the
                # whole list in the page froze the dialog (10000 values 6.6 s, 30000 values 87 s). The note says that more values match.
                # The choices are sent after the page has the box (on_flushed): the update of an input made in the same flush is lost.
                session.on_flushed(
                    lambda: ui.update_selectize("fb_value", choices=labels, selected=None, server=True, session=session), once=True)
                return ui.div(
                    ui.input_selectize("fb_value", label=None, choices=[], selected=[], multiple=True,
                                       options={**options, "maxOptions": LIST_ON_DEMAND_FROM}),
                    ui.tags.small(list_note(len(labels)), class_="text-muted fst-italic d-block spv-text-meta", id="fb_value_note"),
                )
            except Exception:
                _log.exception("filter dialog: the values of column %r could not be listed", col)
                return ui.tags.small("The values of this column could not be listed.", class_="text-danger d-block")
        if widget == "bool":
            return ui.input_radio_buttons("fb_value", label=None, choices={"true": "true", "false": "false"}, selected="true", inline=True)
        if widget.removesuffix("_range") in ("date", "datetime", "time", "duration"):
            kind = widget.removesuffix("_range")
            try:
                bounds = column_bounds(lf, col, dtype)
            except Exception:
                _log.exception("filter dialog: the range of column %r could not be read", col)
                bounds = None
            lo, hi = bounds if bounds is not None else ({}, {})
            hint = control_hint(dtype)
            if widget.endswith("_range"):
                lo = hi = _EMPTY_END   # D-0504: the two ends of between start empty; the user gives both
            hint_ui = ui.tags.small(hint, class_="text-muted fst-italic d-block spv-text-meta") if hint else ui.div()
            if not widget.endswith("_range"):
                return ui.div(_control(kind, "", lo), hint_ui)
            return ui.div(
                ui.div(
                    ui.div(ui.tags.small("min", class_="text-muted"), _control(kind, "_lo", lo), class_="spv-flex-1"),
                    ui.div(ui.tags.small("max", class_="text-muted"), _control(kind, "_hi", hi), class_="spv-flex-1"),
                    class_="d-flex gap-1 flex-wrap",
                ),
                ui.input_radio_buttons("fb_closed", label=None, choices=CLOSED_CHOICES, selected="both"),
                ui.output_ui("filter_closed_text_ui"),
                hint_ui,
            )
        if widget in ("number", "range"):
            rng = number_range(lf, col)
            is_int_col = "Int" in str(dtype)
            col_min, col_max = rng if rng is not None else ((0, 1) if is_int_col else (0.0, 1.0))
            if col_min == col_max:  # all values equal: widen by 1 so the box works
                col_max = col_min + 1
            step = 1 if is_int_col else (col_max - col_min) / 100 or 0.01
            if widget == "number":
                return ui.input_numeric("fb_value", label=None, value=col_min, min=col_min, max=col_max, step=step)
            return ui.div(
                ui.div(
                    ui.div(ui.tags.small("min", class_="text-muted"),
                           ui.input_numeric("fb_value_lo", label=None, value=None, step=step), class_="spv-flex-1"),
                    ui.div(ui.tags.small("max", class_="text-muted"),
                           ui.input_numeric("fb_value_hi", label=None, value=None, step=step), class_="spv-flex-1"),
                    class_="d-flex gap-1",
                ),
                # D-0504: the ends start empty; the range of the column is information beside them, never a value in them
                ui.tags.small(f"The column runs from {col_min} to {col_max}.", class_="text-muted fst-italic d-block spv-text-meta"),
                ui.input_radio_buttons("fb_closed", label=None, choices=CLOSED_CHOICES, selected="both"),
                ui.output_ui("filter_closed_text_ui"),
            )
        return ui.input_text("fb_value", label=None, placeholder="Value…")

    @output
    @render.ui
    def filter_whole_number_ui():
        """The plain line under the value box when a decimal is typed for a whole-number column (D-0376); reads the boxes, mounts none.

        PROVISIONAL sentence: the same as the refusal of "+ Add" (the rule is `t3_audit_engine.refuse_decimal_for_whole_numbers`). Empty otherwise.
        """
        _dialog_schema_signal.get()
        _form_reset.get()
        _lf, types, _disc = _dialog_table_now()
        dtype = types.get(_selected_column(types))
        if kind_of(dtype) != "int":
            return ui.div(id="fb_whole_number_line")
        for box in ("fb_value", "fb_value_lo", "fb_value_hi"):
            raw = safe_input(input, box, None)
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                try:
                    refuse_decimal_for_whole_numbers(raw, dtype)
                except FilterValueError as exc:
                    return ui.tags.small(str(exc), class_="d-block spv-text-meta spv-field-error", id="fb_whole_number_line")
        return ui.div(id="fb_whole_number_line")

    # The reason "+ Add" added nothing for a `between` (D-0504, D-0050). A Value written by the add effect and by the Effect that
    # clears it; the line reads only it, so showing it never mounts a box again (section 14, R4).
    _add_reason = reactive.Value("")

    @output
    @render.ui
    def filter_add_reason_ui():
        """The plain line near the value boxes when "+ Add" refused a `between` without both ends; empty otherwise."""
        text = _add_reason.get()
        if not text:
            return ui.div(id="fb_add_reason")
        return ui.tags.small(text, class_="d-block spv-text-meta spv-field-error", id="fb_add_reason", role="alert")

    @reactive.Effect
    def _clear_add_reason():
        """The line goes when the user changes what it is about: the column, the operator or an end (R3: idempotent)."""
        _selected = (safe_input(input, "fb_col", None), safe_input(input, "fb_op", None),
                     safe_input(input, "fb_value_lo", None), safe_input(input, "fb_value_hi", None),
                     safe_input(input, "fb_value_lo_raw", None), safe_input(input, "fb_value_hi_raw", None))
        with reactive.isolate():
            if _add_reason.get():
                _add_reason.set("")

    @output
    @render.ui
    def filter_closed_text_ui():
        """The ends of the range in words; reads fb_closed only (the radio is mounted by filter_form_ui without reading it)."""
        closed = safe_input(input, "fb_closed", "both")
        return ui.tags.small(f"The range keeps the values with {closed_phrase(closed if closed in CLOSED_CHOICES else 'both')}.",
                             class_="text-muted fst-italic d-block spv-text-meta")

    # The audit steps of the open plot, as the dialog reads them. `_dialog_audit_steps_changed` is a Value with an idempotent guard (R3)
    # that only SIGNALS a change of these steps: the dialog depends on it, not on home_state, so a change of home_state that is not a
    # change of these steps (a ghost save, a seed) does not mount the form again and does not wipe what the user is typing (R4,
    # ui_implementation_contract.md section 14). The steps themselves are read fresh, for the plot open NOW, in the same step that
    # reads the plot's table (`_active_frame`): a mirror holding the steps would be one flush late on a plot switch (outputs
    # created before the mirror's effect run first, with the new plot's table and the old plot's steps; shown by
    # `app/tests/test_dialog_mirror_window.py`).
    _dialog_audit_steps_changed = reactive.Value([])

    def _place_nodes_now() -> list:
        """The committed audit steps, at every tier (the list `audit_pipeline`): the engine runs them in the audit copy. Only a SIGNAL of the form reads them (a change builds the dialog again)."""
        with reactive.isolate():
            steps = (home_state.get().get("audit_pipeline") or []) if home_state is not None else []
        return list(steps)

    @reactive.Effect
    def _signal_dialog_audit_steps():
        active_home_subtab.get()   # the plot open now: the table the form reads is its own
        steps = (home_state.get().get("audit_pipeline") or []) if home_state is not None else []   # the dependency
        nodes = list(steps)   # a step at any tier can change the table the form reads
        with reactive.isolate():
            if _dialog_audit_steps_changed.get() != nodes:
                _dialog_audit_steps_changed.set(nodes)

    def _active_frame():
        """The table the filter in the form acts on: the table of the view shown for the active plot (D-0178; None when it cannot be built)."""
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        try:
            lf = _resolve_active_lf(_resolve_active_spec(p_id))
        except AUDIT_ERRORS:
            # The audit steps cannot run: the table and the plot show why. The dialog offers nothing until a step is removed.
            _log.warning("filter dialog: the audit steps cannot run; no table is offered")
            return None
        except Exception:
            _log.exception("filter dialog: the table the filter acts on could not be built")
            return None
        # DECIDED 2026-11-15 (Eve, S2-1 (a)): in Audit mode on T3 the dialog acts on the table after the plot's audited steps, so a column
        # that an earlier step dropped is not offered. One source: `_resolve_active_lf` is the table of the audit copy in Audit mode, the same
        # as the table, the plot and the export; a step that cannot run raises there (below) and the dialog offers nothing until it is removed.
        _dialog_audit_steps_changed.get()   # the dependency: a change of the steps builds the dialog again
        return lf

    @output
    @render.ui
    def filter_na_ui():
        """The tick "keep the rows with no value", preselected by operator (NA-RULE-63).

        Reads the column and the operator, never its own value (ui_implementation_contract.md section 14, R4): a new
        column or operator re-mounts the tick on the default of that operator, a click on it re-renders nothing here.
        The counts under it are in filter_na_text_ui.
        """
        op = safe_input(input, "fb_op", "eq")
        label, help_ = na_choice_texts(OP_WORDS.get(op, (op, op))[1])
        return ui.div(
            ui.input_checkbox("fb_na", label, value=default_na(op) == "keep"),
            ui.tags.small(help_, class_="text-muted d-block spv-text-meta"),
            class_="mt-1 px-1",
        )

    @output
    @render.ui
    def filter_na_text_ui():
        """How many rows have no value in the chosen column, and what the tick does to them (counts from the table it acts on)."""
        col = safe_input(input, "fb_col", None)
        op = safe_input(input, "fb_op", "eq")
        na = "keep" if safe_input(input, "fb_na", default_na(op) == "keep") else "remove"
        if not col:
            return ui.div()
        frame = _active_frame()
        if not column_is_in_frame(frame, col):
            # Found 2026-11-18 (switch check, finding 5): after a recipe or plot change `fb_col` still holds the previous table's
            # column for one round; the box is rebuilt from the new table and this output runs again with the right column.
            # Asking the counts now logged a KeyError and showed "The counts could not be computed." for that moment.
            return ui.div()
        text = dialog_lines(frame, col, op, na)
        return ui.div(
            *[ui.tags.small(line, class_="d-block spv-text-meta " + ("text-warning" if line == text.warning else "text-muted"))
              for line in text.lines],
            class_="px-1 mb-1",
        )

    @output
    @render.ui
    def filter_controls_ui():
        """Apply / + Add / Reset buttons + status. Reads _pending_filters + applied_filters.

        Exploration and Audit mode are different. In Exploration the staged rows are tried on the table of the view shown with "Apply": they change that table only, never a plot, and nothing
        is saved or exported. In Audit mode the form builds the condition of an audit step: no Apply; the button "Try" is the step bar's (`step_bar_handlers`, one button for a condition and a
        drop), and the fold-out of the bar adds the step to the audit pipeline (FLOW-3, then the step bar: the one way to create a step).
        """
        n_applied = len(applied_filters.get())
        n_pending = len(_pending_filters.get())
        audit = _in_audit()
        status = (
            ui.tags.small(f"{n_applied} active", class_="text-success d-block mb-1 spv-text-xxs")
            if n_applied and not audit else ui.div()
        )
        buttons = []
        if not audit:
            buttons.append(
                ui.input_action_button(
                    "filter_apply", f"Apply ({n_pending})",
                    class_="btn-primary btn-sm spv-text-xs",
                    title="Applies these filters to the table you view (Source, T1, T2 or T3) for exploration. They change that "
                          "table only, never a plot. Not written to the audit log, and not exported.",
                ))
        buttons.append(
            ui.input_action_button(
                "filter_add_row", "+ Add",
                class_="btn-outline-primary btn-sm spv-text-xs",
            )
        )
        buttons.append(
            ui.input_action_button(
                "filter_reset", "Reset",
                class_="btn-outline-secondary btn-sm spv-text-xs",
            )
        )
        # Reminders (Eve, 2026-11-06): in Exploration a filter is a way to understand the data; only what is added to the audit pipeline (with a reason) is exported. PROVISIONAL words.
        if audit:
            reminder = ui.tags.small("Audit: build the condition here (+ Add), press Try in the bar above the table, then write the reason and add the step to the audit pipeline. An added step changes the plots built from its place and is exported.",
                                     class_="text-warning d-block mt-1 spv-text-xxs")
        else:
            reminder = ui.tags.small("Exploration: filters change this table only, never a plot. Nothing here is exported.",
                                     class_="text-muted d-block mt-1 spv-text-xxs")
        return ui.div(
            status,
            ui.div(*buttons, class_="d-flex gap-1 mt-1 flex-wrap"),
            reminder,
        )

    # ── Filter builder effects ─────────────────────────────────────────

    @reactive.Effect
    @reactive.event(input.filter_add_row)
    def _filter_add_row():
        """Append a new filter row to _pending_filters from the add-row form.

        ADR-104 point 7: the row holds the real value in the type of the column (schema of the table, not a sample of
        rows): the values picked from a list are looked up in a map built from the whole column, a number from a number
        box is typed from the dtype. The row also carries the dtype, so a later reader can check the value against it.
        """
        col = safe_input(input, "fb_col", None)
        op = safe_input(input, "fb_op", "eq")
        if not col:
            return
        lf, types, disc = _dialog_table()
        discrete_axis = col in disc
        dtype = types.get(col)
        dtype_str = str(dtype) if dtype is not None else "Utf8"
        raw = safe_input(input, "fb_value", None)  # a list of texts, a number or a text, by the widget that was mounted
        kind = kind_of(dtype)
        widget = value_widget_for(dtype, discrete_axis, op) if dtype is not None else "text"

        def _boxes(suffix: str):
            """What the controls of a date, date and time, time or duration hold, as the text the rule reads (an empty box is a plain error)."""
            value = safe_input(input, f"fb_value{suffix}", None)
            if kind == "time":
                return compose_time(*(safe_input(input, f"fb_{k}{suffix}", None) for k in ("h", "min", "s")))
            raw = safe_input(input, f"fb_value{suffix}_raw", None)   # the text of the date box (None: not sent yet, the date was not typed)
            if kind == "datetime":
                return compose_datetime(value, *(safe_input(input, f"fb_{k}{suffix}", None) for k in ("h", "min", "s")), typed=raw)
            if kind == "duration":
                return compose_duration(value, safe_input(input, f"fb_unit{suffix}", None))
            if kind == "date":
                return compose_date(value, raw)
            return value   # true/false

        try:
            if widget != "list" and kind in ("bool", "date", "datetime", "time", "duration"):
                ranged = widget.endswith("_range")
                low = high = None
                if ranged:
                    low, high = between_ends(lambda: _boxes("_lo"), lambda: _boxes("_hi"))   # D-0504: both ends from the user, or the line
                chosen = dialog_value(
                    lf, col, dtype, discrete_axis, op,
                    operand=None if ranged else _boxes(""), low=low, high=high, closed=safe_input(input, "fb_closed", "both"),
                )
            else:
                chosen = dialog_value(
                    lf, col, dtype, discrete_axis, op,
                    picked=raw if isinstance(raw, (list, tuple)) else (),
                    operand=raw if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None,
                    low=safe_input(input, "fb_value_lo", None), high=safe_input(input, "fb_value_hi", None),
                    closed=safe_input(input, "fb_closed", "both"), text=raw if isinstance(raw, str) else "",
                )
        except BetweenIncomplete as exc:
            _add_reason.set(str(exc))   # the line near the boxes says why nothing was added; no row (D-0504, D-0050)
            return
        except FilterValueError as exc:
            _notify(str(exc), type="error", duration=8)
            return
        _add_reason.set("")
        if chosen is None:
            return  # nothing chosen yet: do not add an empty filter
        op, value, bt_closed = chosen

        # NA-RULE-63: the tick of the dialog, never absent from a row (None: not mounted, the default of the operator)
        na_tick = safe_input(input, "fb_na", None)
        # review F3: the row carries the view key it was built on; the data preview applies a filter only while the view is that one
        new_row = staged_filter_row(col, op, value, dtype_str, na_tick, closed=bt_closed, view=current_view_key())
        current = list(_pending_filters.get())
        current.append(new_row)
        _pending_filters.set(current)

    @reactive.Effect
    @reactive.event(input.filter_apply)
    def _filter_apply():
        """Left-panel Apply — exploration only (HOM-43 + ADR-085, 2026-08-10; slice B, D-0311).

        Commits _pending_filters → applied_filters: a transient view filter,
        never written to the audit log. The data preview applies it to the table of
        the view shown; no plot ever does (home_theater.py). It does not exist in Audit
        mode (the button is not drawn there; the guard below is the second line).
        Making a step permanent is another path (Try, then "Add to audit pipeline", `trial_handlers`), so
        "look at it" and "make it permanent" are two distinct actions.
        """
        if _in_audit():
            return
        applied_filters.set(list(_pending_filters.get()))

    @reactive.Effect
    @reactive.event(input.filter_reset)
    def _filter_reset():
        """Clear all pending and applied filters, and reset the value widget."""
        _clear_exploration_filters()
        ui.update_selectize("fb_value", selected=[])
        ui.update_text("fb_value", value="")

    # Dynamic remove buttons — one effect per row index up to a generous cap
    def _make_remove_handler(idx: int):
        @reactive.Effect
        @reactive.event(getattr(input, f"filter_remove_{idx}", lambda: None))
        def _remove():
            try:
                _ = getattr(input, f"filter_remove_{idx}")()
            except Exception:
                return
            current = list(_pending_filters.get())
            if idx < len(current):
                removed = current.pop(idx)
                _pending_filters.set(current)
                # GUARDED (issue #56 retest, HOM-09): removing a row also takes it out of the applied
                # filters, so the view updates at once; Apply is for new rows, not for undoing one.
                applied = list(applied_filters.get())
                if removed in applied:
                    applied.remove(removed)
                    applied_filters.set(applied)
        return _remove

    # Register remove handlers for up to 50 filter rows
    _remove_handlers = [_make_remove_handler(i) for i in range(50)]
