"""app/handlers/filter_and_audit_handlers.py
Filter builder UI + T3 audit promotion + propagation modal.

Extracted from home_theater.py in Phase 24-D (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.

Why filter UI and T3 audit live in one file:
    _filter_apply, _col_drop_to_audit, and _handle_propagation_confirm all
    share the _propagation_scratch reactive.Value and call into the same
    _open_propagation_modal helper. Splitting would force exposing the
    scratch state across module boundaries.
"""

from __future__ import annotations

# @deps
# provides: function:define_filter_audit_server, effect:_clear_filters_on_view_change (replaces _clear_filters_on_recipe_change, slice B), output:sidebar_filters, output:filter_rows_ui, output:filter_form_ui, output:filter_type_ui, output:filter_op_ui, output:filter_value_ui, output:filter_closed_text_ui, output:filter_na_ui, output:filter_na_text_ui, output:filter_controls_ui, input:fb_na, input:filter_apply, input:filter_send_to_audit
# consumes: app/modules/session_manager.py (make_audit_step), app/modules/t3_audit_engine.py (view_change_notice, column_is_in_frame, staged_filter_row (view=), describe_filter, op_choice_label, dialog_value, value_choices, column_types, ops_for_column, value_widget_for, number_range, column_type_line, closed_phrase, CLOSED_CHOICES, dialog_frame, dialog_schema_signature, dialog_rows_signature, AuditStepError, column_bounds, compose_date, compose_time, compose_datetime, compose_duration, control_hint, LIST_ON_DEMAND_FROM, list_note), libs/utils/src/utils/filter_values.py, libs/utils/src/utils/key_drop.py (DropGate: the drop of a key column by place, D-0358), libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py, app/src/bootloader.py (is_enabled), shiny
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-049, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-085, .claude/rules/ui_implementation_contract.md#8
# @end_deps

import logging

from shiny import reactive, render, ui

from app.src.bootloader import bootloader
from app.modules.t3_audit_engine import (
    describe_filter, op_choice_label, OP_WORDS, staged_filter_row, audit_params_from_row,
    CLOSED_CHOICES, closed_phrase, column_type_line, column_types, number_range, ops_for_column,
    dialog_value, not_offered_line, value_choices, value_widget_for, AuditStepError, dialog_frame, dialog_rows_signature, dialog_schema_signature,
    column_bounds, column_is_in_frame, view_change_notice, compose_date, compose_datetime, compose_duration, compose_time, control_hint, LIST_ON_DEMAND_FROM, list_note,
)
from utils import key_drop
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


def _date_picker(id_: str, value):
    """A date picker that never chooses a date for the user.

    The widget (bootstrap-datepicker) repairs what is typed: Enter in an empty box chooses the highlighted day (today), and with the
    default `forceParse` a partial text, a text that is not a date or 2023-02-30 is replaced by another date in the box. Keyboard
    navigation is off (no Enter that picks a day; the arrow keys of the calendar do not work, typing the date does) and `forceParse` is
    off (the box keeps what the user typed, so it can be corrected). The raw text is sent to the server (`_DATE_RAW_SCRIPT`) and read
    strictly by `compose_date`. The calendar stays for the mouse.

    PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 8: keep the calendar and read the typed text strictly (option: a plain text box with the calendar only as a helper).
    """
    tag = ui.input_date(id_, label=None, value=value, format="yyyy-mm-dd")
    for child in tag.children:
        if getattr(child, "name", None) == "input":
            child.attrs["data-date-keyboard-navigation"] = "false"
            child.attrs["data-date-force-parse"] = "false"
    return ui.TagList(tag, ui.tags.script(ui.HTML(_DATE_RAW_SCRIPT)))


def _control(kind: str, suffix: str, d: dict):
    """The control of one value of a date, date and time, time of day or duration; `suffix` is "" (one value), "_lo" or "_hi" (between)."""
    if kind == "date":
        return _date_picker(f"fb_value{suffix}", d.get("date"))
    if kind == "datetime":
        # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 5: a date and time is a date picker plus the three boxes of a time.
        return ui.div(_date_picker(f"fb_value{suffix}", d.get("date")), _time_boxes(suffix, d))
    if kind == "time":
        return _time_boxes(suffix, d)
    # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 4: a duration is a number with a choice of 8 units (ns, us, ms, s, min, h, d, w).
    return ui.div(  # duration: a number and its unit
        ui.div(ui.input_numeric(f"fb_value{suffix}", label=None, value=d.get("number", 0), step=1), class_="spv-flex-1"),
        ui.div(ui.input_select(f"fb_unit{suffix}", label=None, choices=list(UNIT_NS), selected=d.get("unit", "s")), class_="spv-flex-1"),
        class_="d-flex gap-1",
    )


def define_filter_audit_server(input, output, session, *,
                                applied_filters, _pending_filters,
                                _propagation_scratch, home_state,
                                in_audit, data_view, view_source_table, current_view_key, active_home_subtab,
                                safe_input,
                                _resolve_active_spec, _resolve_active_lf,
                                _spec_discrete_axes, _t3_drop_columns,
                                _all_plot_subtab_ids, _plot_label, _table_identity,
                                notification_log=None, recipe_raw=None):
    """Register filter UI + T3 audit propagation handlers.

    Reactive deps (kwargs) — all shared with home_theater.define_server:
      applied_filters       reactive.Value[list]   — committed transient filters (T1/T2 plot view)
      _pending_filters      reactive.Value[list]   — staging rows in the add-row form
      _propagation_scratch  reactive.Value[dict]   — scratch nodes between Apply/Drop and modal confirm
      home_state            reactive.Value[dict] | None — audit steps state, active subtab, etc.
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
      _t3_drop_columns()         → list[str]   — committed drop-column targets
      _all_plot_subtab_ids()     → list[str]   — every "subtab_<plot_id>" id
      _plot_label(subtab_id)     → str         — human-readable plot label
      _table_identity(spec, tier) → tuple | None — which stored table the dialog reads (`stored_table_identity`); None when no
                                    key says which rows it holds (the rows signal is then never equal)
      recipe_raw()               → dict | None — the resolved dictionary of the open recipe, for the rule of a key drop (`utils.key_drop`); None: no drop is refused
    """

    _in_audit = in_audit   # one function for HOME and these handlers: `home_theater._in_audit`

    def _can_write_audit_step() -> bool:
        """An audit step is written at the plot's table: Audit mode while T3 is viewed (P-B3, PROVISIONAL: the existing dialog writes at
        the plot's table only, so "a filter is built on the table of the view shown", D-0178, holds only there)."""
        return _in_audit() and data_view.get() == "T3"

    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    def _clear_exploration_filters() -> tuple[int, int]:
        """The one reset of the exploration filters: empties the staged and the applied list, returns how many rows each held.

        Used by Send to Audit, the Reset button, the T3 apply and the recipe change. Audited steps live elsewhere
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
    # the data choice, the source table, the open plot (P-B2, PROVISIONAL: it changes the table viewed), the mode (exploration filters do not
    # exist in Audit mode) and the recipe. One view key (`view_key`) says what the view is; the notice names the first cause that changed.
    # Idempotent guard: only a real change of the key clears; the selector input is re-created when the user returns to
    # HOME from another space and then reports the same id again, which must not clear anything or notify.
    _seen_view = {"key": None}

    @reactive.Effect
    def _clear_filters_on_view_change():
        rid = safe_input(input, "data_analysis_recipe_id", None)
        if rid is None:
            return
        key = current_view_key()
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
        # Left "Apply" is the single entry point: in T1/T2 it commits transient
        # filters; in T3 it pushes pending AuditSteps into home_state for the
        # right-sidebar audit panel. No separate "Apply to audit trail" button.
        return ui.div(
            disclaimer or ui.div(),
            ui.output_ui("filter_rows_ui"),
            ui.output_ui("filter_form_ui"),
            ui.output_ui("filter_na_ui"),
            ui.output_ui("filter_na_text_ui"),
            ui.div(
                ui.output_ui("filter_controls_ui"),
                class_="mt-2 px-1"
            ),
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
            audit_t3 = _can_write_audit_step()
            identity = None
            if lf is not None:
                try:
                    identity = _table_identity(_resolve_active_spec(subtab.removeprefix("subtab_") if subtab else None), tier)
                except Exception:
                    # No identity, no way to tell two tables apart: the signature is never equal (one more render).
                    _log.exception("filter dialog: the stored table the form reads could not be identified")
            # The same condition as `_active_frame`: the audited steps apply on T3 in Audit mode only.
            rows = dialog_rows_signature(identity, _audit_nodes_of(subtab) if audit_t3 else [])
        except Exception as exc:
            # The outputs read the table again and show the error themselves; this only makes them run again when it changes.
            _log.exception("filter dialog: the table of the form could not be read")
            schema = rows = ("error", f"{type(exc).__name__}: {exc}")
        with reactive.isolate():
            if _dialog_schema_signal.get() != schema:
                _dialog_schema_signal.set(schema)
            if _dialog_rows_signal.get() != rows:
                _dialog_rows_signal.set(rows)

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
                ui.div(ui.output_ui("filter_value_ui"), class_="spv-flex-1"),
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
        wipe the value the user has typed.
        """
        _dialog_schema_signal.get()
        _dialog_rows_signal.get()
        _form_reset.get()
        lf, types, disc = _dialog_table_now()
        col = _selected_column(types)
        dtype = types.get(col)
        choices = _op_choices(dtype, col in disc)
        if not choices:
            return ui.div()  # the operator slot says why (filter_op_ui)
        op = safe_input(input, "fb_op", next(iter(choices)))
        if op not in choices:
            op = next(iter(choices))
        widget = value_widget_for(dtype, col in disc, op) if dtype is not None else "text"
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
                           ui.input_numeric("fb_value_lo", label=None, value=col_min, step=step), class_="spv-flex-1"),
                    ui.div(ui.tags.small("max", class_="text-muted"),
                           ui.input_numeric("fb_value_hi", label=None, value=col_max, step=step), class_="spv-flex-1"),
                    class_="d-flex gap-1",
                ),
                ui.input_radio_buttons("fb_closed", label=None, choices=CLOSED_CHOICES, selected="both"),
                ui.output_ui("filter_closed_text_ui"),
            )
        return ui.input_text("fb_value", label=None, placeholder="Value…")

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
    # reads the plot's table (`_audit_nodes_of`): a mirror holding the steps would be one flush late on a plot switch (outputs
    # created before the mirror's effect run first, with the new plot's table and the old plot's steps; shown by
    # `app/tests/test_dialog_mirror_window.py`).
    _dialog_audit_steps_changed = reactive.Value([])

    def _audit_nodes_of(subtab) -> list:
        with reactive.isolate():
            by_plot = (home_state.get().get("t3_audit_steps_by_plot") or {}) if home_state is not None else {}
        return list(by_plot.get(subtab, [])) if subtab else []

    @reactive.Effect
    def _signal_dialog_audit_steps():
        subtab = active_home_subtab.get()
        by_plot = (home_state.get().get("t3_audit_steps_by_plot") or {}) if home_state is not None else {}   # the dependency
        nodes = list(by_plot.get(subtab, [])) if subtab else []
        with reactive.isolate():
            if _dialog_audit_steps_changed.get() != nodes:
                _dialog_audit_steps_changed.set(nodes)

    def _active_frame():
        """The table the filter in the form acts on: the table of the view shown for the active plot (D-0178; None when it cannot be built)."""
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        try:
            lf = _resolve_active_lf(_resolve_active_spec(p_id))
        except Exception:
            _log.exception("filter dialog: the table the filter acts on could not be built")
            return None
        # DECIDED 2026-11-15 (Eve, S2-1 (a)): in Audit mode on T3 the dialog acts on the table after the plot's audited steps, so a column
        # that an earlier step dropped is not offered. One source: the same function as the table, the plot and the export.
        try:
            _dialog_audit_steps_changed.get()   # the dependency: a change of this plot's steps builds the dialog again
            return dialog_frame(lf, _audit_nodes_of(subtab), _can_write_audit_step(), p_id)
        except AuditStepError:
            # The audit list of the plot cannot run: the table and the plot show why. The dialog offers nothing until a step is removed.
            _log.warning("filter dialog: the audit steps of the plot cannot run; no table is offered")
            return None

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
        """Apply / Send to Audit / Reset buttons + status. Reads _pending_filters
        + applied_filters.

        Slice B (D-0016, D-0311, D-0177): Exploration and Audit mode are different. In Exploration the staged rows are tried on the table
        of the view shown with "Apply": they change that table only, never a plot, and nothing is saved or exported. In Audit mode the form
        builds audit steps, not previews: no Apply (P-B4, PROVISIONAL); "Send to Audit" is offered while T3 is viewed (P-B3, PROVISIONAL),
        and on another view one plain line says why it is absent.
        """
        n_applied = len(applied_filters.get())
        n_pending = len(_pending_filters.get())
        audit = _in_audit()
        can_send = _can_write_audit_step()
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
        if can_send:
            buttons.append(
                ui.input_action_button(
                    "filter_send_to_audit", f"➜ Send to Audit ({n_pending})",
                    class_="btn-warning btn-sm spv-text-xs",
                    title="Writes these filters to the permanent audit log (with a "
                          "reason) — included in every export, applies only to T3, "
                          "and cannot be silently discarded once committed.",
                )
            )
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
        # Reminders (Eve, 2026-11-06; slice B): in Exploration a filter is a way to understand the data; only what is sent to audit (with a
        # reason) is exported. PROVISIONAL words (the coordinator's; the owner reads them).
        if audit and not can_send:
            reminder = ui.tags.small("To create an audit step, view T3.", class_="text-warning d-block mt-1 spv-text-xxs")
        elif audit:
            reminder = ui.tags.small("Audit: a step you send changes the plot and is exported.", class_="text-warning d-block mt-1 spv-text-xxs")
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
                chosen = dialog_value(
                    lf, col, dtype, discrete_axis, op,
                    operand=None if ranged else _boxes(""), low=_boxes("_lo") if ranged else None,
                    high=_boxes("_hi") if ranged else None, closed=safe_input(input, "fb_closed", "both"),
                )
            else:
                chosen = dialog_value(
                    lf, col, dtype, discrete_axis, op,
                    picked=raw if isinstance(raw, (list, tuple)) else (),
                    operand=raw if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None,
                    low=safe_input(input, "fb_value_lo", None), high=safe_input(input, "fb_value_hi", None),
                    closed=safe_input(input, "fb_closed", "both"), text=raw if isinstance(raw, str) else "",
                )
        except FilterValueError as exc:
            _notify(str(exc), type="error", duration=8)
            return
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
        The promotion path is the separate `filter_send_to_audit` button
        below, so "try it" and "make it permanent" are two distinct actions.
        """
        if _in_audit():
            return
        applied_filters.set(list(_pending_filters.get()))

    @reactive.Effect
    @reactive.event(input.filter_send_to_audit)
    def _filter_send_to_audit():
        """Promote staged filter rows into the permanent T3 audit pipeline.

        Slice B: an audit step is written in Audit mode while T3 is viewed (P-B3, PROVISIONAL). filter_controls_ui only renders this
        button then — the explicit re-check here matches the defensive-guard style already used
        by `_col_drop_to_audit` below.
        Formerly the T3 branch of `filter_apply` (HOM-43 split, 2026-08-10) —
        same logic, now its own explicit action:
          - Filter on a primary-key column → primary_key_warning=True stamped
            (§12g.3); the row itself is kept as filter_row, not silently
            converted (AUDIT-1).
          - Opens the propagation dialog so the user picks
            this-plot / all-plots / all-except.
        """
        if not _can_write_audit_step():
            return
        rows = list(_pending_filters.get())
        if not rows or home_state is None:
            _notify(
                "No filter rows to send. Add rows below first (the '+ Add' button).",
                type="warning", duration=5,
            )
            return

        from app.modules.session_manager import make_audit_step
        state = home_state.get()
        primary_keys = set(state.get("primary_keys") or [])
        active_subtab = state.get("active_plot_subtab") or active_home_subtab.get() or ""

        scratch_nodes: list[dict] = []
        for frow in rows:
            col = frow.get("column", "")
            params = audit_params_from_row(frow)

            is_pk = col in primary_keys
            # AUDIT-1 (ADR-049 amendment, 2026-04-30): filtering on a PK
            # column is now ALLOWED. Previously this silently converted to
            # exclusion_row with a negated op — that broke the user mental
            # model ("filter sample==X" should keep X, not exclude it).
            # Keep the row as filter_row; primary_key_warning=True still
            # raises the warning banner in the modal and audit panel.
            # Drop-column on a PK remains BLOCKED (handled at the drop
            # action site, not here).
            node_type = "filter_row"

            scratch_nodes.append(make_audit_step(
                node_type, params,
                plot_scope=active_subtab,
                reason="",
                primary_key_warning=is_pk,
            ))

        # Stash for the propagation dialog handler to consume.
        _propagation_scratch.set({"nodes": scratch_nodes, "kind": "filter"})
        _open_propagation_modal(scratch_nodes, active_subtab, kind="filter")

        # Clear the staged rows — they're now in the audit pipeline.
        _clear_exploration_filters()

    @reactive.Effect
    @reactive.event(input.filter_reset)
    def _filter_reset():
        """Clear all pending and applied filters, and reset the value widget."""
        _clear_exploration_filters()
        ui.update_selectize("fb_value", selected=[])
        ui.update_text("fb_value", value="")

    @reactive.Effect
    @reactive.event(input.col_drop_to_audit)
    def _col_drop_to_audit():
        """Promote deselected columns into the T3 audit pipeline.

        Phase 22-J / ADR-049, D-0358:
          - A column that a join step later reads as a key → BLOCKED with the sentence of the rule (`utils.key_drop`, by place; this drop is
            written in the plot's own steps, `T3:<plot>`, after every join).
          - Otherwise → build pending drop_column nodes and open the
            propagation dialog.
        """
        if home_state is None or not _can_write_audit_step():
            return

        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        try:
            lf = _resolve_active_lf(spec, tier="T3")
        except Exception:
            return

        state = home_state.get()
        committed = set(_t3_drop_columns())
        choosable = [c for c in lf.collect_schema().names() if c not in committed]
        visible = safe_input(input, "preview_col_selector", choosable)
        vis_set = set(visible) if isinstance(visible, (list, tuple)) else set(choosable)
        to_drop = [c for c in choosable if c not in vis_set]

        if not to_drop:
            _notify(
                "No deselected columns to drop. Uncheck columns above first.",
                type="warning", duration=4,
            )
            return

        # A column a join step later reads as a key is refused BY PLACE (D-0358, which modulates D-0297 and §12g.4): this drop is written in the plot's own steps (the
        # place `T3:<plot>`), after every join, so the rule finds nothing to refuse there today; it is asked all the same, with the place the step has.
        problem = key_drop.DropGate(recipe_raw()).problem(f"T3:{p_id}", to_drop) if recipe_raw is not None and p_id else None
        if problem:
            _notify(f"⛔ {problem}", type="error", duration=8)
            return

        from app.modules.session_manager import make_audit_step
        active_subtab = state.get("active_plot_subtab") or active_home_subtab.get() or ""
        scratch_nodes = [
            make_audit_step(
                "drop_column", {"column": col},
                plot_scope=active_subtab,
                reason="",
            )
            for col in to_drop
        ]
        _propagation_scratch.set({"nodes": scratch_nodes, "kind": "drop"})
        _open_propagation_modal(scratch_nodes, active_subtab, kind="drop")

        # Reset selectize to the kept columns so the user starts clean.
        remaining = [c for c in choosable if c in vis_set]
        ui.update_selectize("preview_col_selector",
                            choices=remaining, selected=remaining)

    # ── 22-J: Propagation modal (this/all/all-except) ─────────────────────────

    def _column_presence_per_plot(scratch_nodes: list[dict],
                                   plot_subtabs: list[str]) -> dict[str, str]:
        """For each subtab, report whether the scratch nodes' target columns
        are PRESENT in that plot's underlying dataset (PROP-1).

        Returns a dict mapping subtab_id → 'present' | 'absent' | 'unknown'.
        Plots whose target_dataset can't be resolved get 'unknown' (treated
        as a soft warning).
        Schema scans are memoised per PLOT: two plots on one table can read
        two different tables (a plot's own tier-3 steps of the recipe), so a
        table's schema is never shared between plots.
        """
        cols_needed = {
            n.get("params", {}).get("column", "")
            for n in scratch_nodes
        }
        cols_needed.discard("")
        if not cols_needed:
            return {sub: "present" for sub in plot_subtabs}

        result: dict[str, str] = {}
        schema_cache: dict[str, set[str]] = {}

        for sub in plot_subtabs:
            p_id = sub.removeprefix("subtab_")
            spec = _resolve_active_spec(p_id)
            if spec is None:
                result[sub] = "unknown"
                continue
            if p_id not in schema_cache:
                try:
                    lf = _resolve_active_lf(spec, tier="T3")
                    schema_cache[p_id] = set(lf.collect_schema().names())
                except Exception:
                    schema_cache[p_id] = set()
            ds_cols = schema_cache[p_id]
            if not ds_cols:
                result[sub] = "unknown"
            elif cols_needed.issubset(ds_cols):
                result[sub] = "present"
            else:
                result[sub] = "absent"
        return result

    def _open_propagation_modal(scratch_nodes: list[dict],
                                active_subtab: str,
                                kind: str) -> None:
        """Open a modal asking the user to choose propagation scope.

        Choices:
        - This plot only (default)
        - All plots
        - All plots except… (reveals a multiselect)

        On confirm, `_handle_propagation_confirm` reads the radio + multiselect
        and resolves the scratch nodes into one AuditStep per target plot
        (sharing `id`), then appends them to home_state._pending_t3_nodes.
        """
        all_subtabs = _all_plot_subtab_ids()
        others = [s for s in all_subtabs if s != active_subtab]
        n = len(scratch_nodes)
        first = scratch_nodes[0] if scratch_nodes else {}
        any_pk = any(node.get("primary_key_warning") for node in scratch_nodes)

        # Plain-language summary of what we're about to add
        if kind == "drop":
            header = f"Drop {n} column(s) — choose scope"
            cols = ", ".join(node.get("params", {}).get("column", "?")
                             for node in scratch_nodes)
            summary = f"Columns: {cols}"
        else:
            header = f"Add {n} filter/exclusion(s) — choose scope"
            col = first.get("params", {}).get("column", "?")
            summary = f"Targets column: {col}"

        warn = ui.span()
        if any_pk:
            warn = ui.div(
                "⚠️ One or more nodes target a join key. "
                "Removing rows here changes which samples appear in joined plots.",
                class_="alert alert-warning py-1 px-2 mb-2 spv-text-sm",
            )

        # PROP-1: per-target column presence — surface BEFORE the user confirms.
        presence = _column_presence_per_plot(scratch_nodes, all_subtabs)
        n_present = sum(1 for v in presence.values() if v == "present")
        n_absent = sum(1 for v in presence.values() if v == "absent")
        n_unknown = sum(1 for v in presence.values() if v == "unknown")

        absent_items = [
            ui.tags.li(f"⚠️ {_plot_label(sub)} — column not in plot data; will be SKIPPED")
            for sub, st in presence.items() if st == "absent"
        ]
        unknown_items = [
            ui.tags.li(f"❓ {_plot_label(sub)} — could not resolve dataset; verify manually")
            for sub, st in presence.items() if st == "unknown"
        ]
        propagation_preview = ui.div(
            ui.tags.small(
                f"📍 Propagation preview: ✅ {n_present} apply  •  "
                f"⚠️ {n_absent} skip (col missing)" +
                (f"  •  ❓ {n_unknown} unknown" if n_unknown else ""),
                class_="d-block fw-semibold mb-1",
            ),
            ui.tags.details(
                ui.tags.summary(
                    "Show details",
                    class_="text-muted spv-text-xs",
                    style="cursor:pointer;",
                ),
                ui.tags.ul(
                    *absent_items,
                    *unknown_items,
                    class_="mb-0 ps-3 spv-text-xs",
                ) if (absent_items or unknown_items)
                else ui.tags.div("All plots have this column.",
                                 class_="text-muted ps-3 spv-text-xs"),
            ),
            ui.tags.small(
                "👉 Apply filters one at a time and verify each plot before stacking. "
                "A skipped plot is NOT filtered — it shows the unfiltered data.",
                class_="text-muted d-block mt-1 fst-italic spv-text-meta",
            ),
            class_="alert alert-info py-1 px-2 mb-2 spv-text-sm",
        )

        m = ui.modal(
            warn,
            propagation_preview,
            ui.tags.small(summary, class_="text-muted d-block mb-2"),
            ui.input_radio_buttons(
                "propagation_choice",
                label="Apply to:",
                choices={
                    "this": "This plot only",
                    "all": "All plots",
                    "except": "All plots except…",
                },
                selected="this",
                inline=False,
            ),
            ui.div(
                ui.input_selectize(
                    "propagation_except",
                    label=ui.tags.small(
                        "Select plots to exclude — the rest will receive the filter.",
                        class_="text-muted",
                    ),
                    choices={s: _plot_label(s) for s in others} or {},
                    selected=[],
                    multiple=True,
                    options={"placeholder": "Pick plots to skip…",
                             "plugins": ["remove_button"]},
                ),
                id="propagation_except_wrapper",
                style="display:none;",
            ),
            ui.tags.script(
                """
                (function () {
                    function syncExcept() {
                        var checked = document.querySelector(
                            'input[name="propagation_choice"]:checked'
                        );
                        var wrapper = document.getElementById(
                            'propagation_except_wrapper'
                        );
                        if (wrapper) {
                            wrapper.style.display =
                                (checked && checked.value === 'except') ? '' : 'none';
                        }
                    }
                    document.addEventListener('change', function (e) {
                        if (e.target && e.target.name === 'propagation_choice') {
                            syncExcept();
                        }
                    });
                    syncExcept();
                })();
                """
            ),
            ui.input_action_button(
                "propagation_confirm", "Add to audit pipeline",
                class_="btn-warning w-100 mt-2",
            ),
            title=header,
            easy_close=True,
            footer=ui.modal_button("Cancel"),
            size="m",
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.propagation_confirm)
    def _handle_propagation_confirm():
        """Resolve the user's propagation choice and commit pending nodes."""
        if home_state is None:
            return
        scratch = _propagation_scratch.get() or {}
        scratch_nodes: list[dict] = list(scratch.get("nodes", []))
        if not scratch_nodes:
            ui.modal_remove()
            return

        choice = safe_input(input, "propagation_choice", "this")
        except_picks = safe_input(input, "propagation_except", []) or []
        if isinstance(except_picks, (list, tuple)):
            except_picks = list(except_picks)
        else:
            except_picks = [except_picks]

        all_subtabs = _all_plot_subtab_ids()
        state = home_state.get()
        active_subtab = state.get("active_plot_subtab") or active_home_subtab.get() or ""

        if choice == "this":
            target_plots = [active_subtab] if active_subtab else []
        elif choice == "all":
            target_plots = list(all_subtabs)
        elif choice == "except":
            target_plots = [s for s in all_subtabs if s not in set(except_picks)]
        else:
            target_plots = [active_subtab] if active_subtab else []

        if not target_plots:
            _notify(
                "No target plots selected. Audit pipeline unchanged.",
                type="warning", duration=4,
            )
            ui.modal_remove()
            return

        # §12g.7 — expand each scratch node into one copy per target plot,
        # sharing id (linked deletion). Skip plots whose schema lacks the
        # targeted column (§12g.9 / D9): collect skipped for a notification.
        from app.modules.session_manager import make_audit_step
        pending_nodes = list(state.get("_pending_t3_nodes", []))
        skipped: dict[str, list[str]] = {}  # plot → [columns skipped]
        applied_count = 0

        for scratch_node in scratch_nodes:
            shared_id = scratch_node.get("id")
            params = dict(scratch_node.get("params", {}))
            col = params.get("column", "")
            for plot_id in target_plots:
                # Schema check: does this plot's data have the column?
                if not _plot_has_column(plot_id, col):
                    skipped.setdefault(plot_id, []).append(col)
                    continue
                pending_nodes.append(make_audit_step(
                    scratch_node["node_type"], dict(params),
                    plot_scope=plot_id,
                    reason="",
                    primary_key_warning=bool(scratch_node.get("primary_key_warning")),
                    node_id=shared_id,  # SHARED id across copies
                ))
                applied_count += 1

        home_state.set({**state, "_pending_t3_nodes": pending_nodes})
        _propagation_scratch.set({"nodes": [], "kind": ""})
        ui.modal_remove()

        msg = f"✅ {applied_count} audit entry(ies) added across {len(target_plots)} plot(s)."
        if skipped:
            skipped_summary = "; ".join(
                f"{_plot_label(p)}: {', '.join(cs)}"
                for p, cs in skipped.items()
            )
            msg += f" Skipped (column not in plot data): {skipped_summary}."
        _notify(msg, type="message", duration=7)

    def _plot_has_column(subtab_id: str, column: str) -> bool:
        """Return True if the plot's resolved LazyFrame has the column.

        Used by the propagation expansion to skip plots whose schema doesn't
        carry the targeted column (§12g.9). Errors fail-safe to True so we
        don't silently drop nodes when schema lookup is flaky.
        """
        if not column or not subtab_id:
            return True
        p_id = subtab_id.removeprefix("subtab_")
        try:
            spec = _resolve_active_spec(p_id)
            lf = _resolve_active_lf(spec, tier="T3")
            return column in lf.collect_schema().names()
        except Exception:
            return True

    # When btn_apply commits the audit steps, clear the left-panel filter list:
    # those rows are now permanent T3 nodes and should not be re-applicable as
    # transient filters. Triggered via t3_apply_count bumps in audit_stack.
    _last_apply_count = reactive.Value(0)

    @reactive.Effect
    def _clear_filters_on_t3_apply():
        """After T3 apply, clear left-panel filter staging.

        Both _pending_filters (staging UI) and applied_filters (active plot view)
        are cleared because T3 AuditSteps now drive the plot via _t3_filter_rows
        (the legacy applied_filters path is no longer the source of truth once a
        node is committed to T3).
        """
        if home_state is None:
            return
        cnt = int(home_state.get().get("t3_apply_count", 0))
        if cnt > _last_apply_count.get():
            _last_apply_count.set(cnt)
            _clear_exploration_filters()

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
