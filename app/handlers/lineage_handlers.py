"""
The lineage panel of HOME in Audit mode (LINEAGE-VIEW-G, D-0629, D-0634, D-0627).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.* only; the words, the layout and the staging are in app/modules/lineage_view.py and lineage_step.py.

WHAT THE USER SEES. In Audit mode, below the header strip of HOME, a collapsible panel "Path of the data" (collapsed). Inside: a list of the tables and plots of the recipe by
independent graph (the reader and the text twin of every dot) and a map of dots with arrows. The user chooses the place of an audit step in either. The panel is drawn once for a recipe;
hover, focus, choice, the switch "Whole recipe / Around my selection" and the keyboard are the browser's (app/src/www/lineage_view.js), so a click never draws the panel again
(ui_implementation_contract.md section 14, R4). The browser tells the server the choice (`input.lineage_chosen`); the server's one reading of it is the dialog of "Send to Audit"
(filter_and_audit_handlers.py, which ticks the places the user chose) and the small form below for a result table no plot reads.

THE SMALL FORM (step 3, D-0627). The Filters panel is built on the table of the open plot, so it cannot write a step at a table that no plot reads. When the choice is one such table, the
panel mounts a form for it: a column of THAT place (the engine's plan), an operator and a value. "Add the step" stages a pending step at the place (`lineage_step.stage_nodes`, the same
function as the dialog); its reason is typed in the Pipeline Audit panel and Apply commits it, as for every audit step. The audit panel shows it (it lists a step written at a table no plot
reads on every plot, with the words that no figure changes) and removes it with its bin.

THE MARKS. Every place that holds a committed or pending audit step gets a text mark in the list and a mark on its dot: sent to the browser as the custom message `lineage_marks`
(an effect that reads `home_state`; the panel is not drawn again).

PROVISIONAL (the builder's choices, not decided by the owner): the title and the words of the panel and of the form; that the panel is collapsed when it is drawn; that the form is
offered for ONE chosen result table no plot reads (not for several); that a step at a table no plot reads is listed in the audit panel of every plot.

# @deps
# provides: function:define_server (lineage_handlers), output:lineage_panel_ui, output:lineage_step_form_ui, output:lineage_step_op_ui, output:lineage_step_hint_ui, effect:_send_marks, effect:_add_step_at_leaf
# consumes: app/modules/lineage_view.py (view_data), app/modules/lineage_step.py (form_columns, form_ops, step_params, stage_nodes, stage_sentence, PENDING_NOTE), libs/utils/src/utils/lineage_data.py (lineage_of), app/modules/audit_places.py (PLACES_BUCKET, place_words), app/src/www/lineage_view.js, libs/utils/src/utils/filter_words.py (no_value_words)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/rules/ui_implementation_contract.md#14, .claude/knowledge/decision_ledger.md (D-0627, D-0629, D-0634)
# @end_deps
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from shiny import reactive, render, ui

from app.modules.audit_places import PLACES_BUCKET, place_words
from app.modules.lineage_step import PENDING_NOTE, form_columns, form_ops, stage_nodes, stage_sentence, step_params
from app.modules.lineage_view import view_data
from app.modules.notification_utils import make_notifier
from app.modules.plan_composer import PlanComposerBug
from utils.filter_values import FilterValueError
from utils.lineage_data import Lineage, lineage_of
from utils.recipe_graph import RecipeGraphError

PANEL_TITLE = "Path of the data"   # PROVISIONAL


def _safe_json(data: Any) -> str:
    """JSON for a `<script type="application/json">` tag: the text cannot close the tag."""
    return json.dumps(data, separators=(",", ":")).replace("</", "<\\/")


def define_server(input, output, session, *,
                  active_cfg, in_audit, recipe_plans, home_state, safe_input,
                  notification_log=None, data_refresh_trigger=None):
    """Register the lineage panel, its small form and its marks.

    Parameters (kwargs):
      active_cfg()            the open recipe's config (`.raw_config` is the resolved dictionary)
      in_audit()              True in Audit mode (the one function of HOME)
      recipe_plans()          the engine's plan book of the open recipe, or None (`home_theater._recipe_plans`)
      home_state              reactive.Value of the audit steps and the rest of the HOME state
      safe_input(input, key, default)
      data_refresh_trigger    reactive.Value raised when data is imported (the plan book depends on the data files)
    """
    _notify = make_notifier(notification_log)

    @reactive.Calc
    def _lineage() -> Tuple[Optional[Lineage], str]:
        """The lineage of the open recipe, or (None, the plain reason). Follows the recipe and the data; never reads the choice or the audit steps."""
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        raw = active_cfg().raw_config
        try:
            return lineage_of(raw, recipe_plans()), ""
        except PlanComposerBug:
            return None, "The engine's plan of the recipe could not be made (it was reported)."
        except (RecipeGraphError, KeyError, TypeError, ValueError) as exc:
            return None, f"The recipe cannot be drawn as a lineage: {exc}"

    @output
    @render.ui
    def lineage_panel_ui():
        """The container of the panel, in Audit mode only. Reads the mode and the recipe, nothing the panel itself writes (R4); the data goes to the browser as JSON."""
        if not in_audit():
            return ui.div()
        found, problem = _lineage()
        if found is None:
            body = ui.div(problem, class_="text-muted spv-lin-error")
        elif not found.nodes:
            body = ui.div("The recipe has no table or plot to draw.", class_="text-muted")
        else:
            body = ui.div(
                ui.div(ui.tags.script(_safe_json(view_data(found)), type="application/json"), class_="spv-lineage", id="lineage_root"),
                ui.output_ui("lineage_step_form_ui"),
            )
        return ui.div(
            ui.accordion(
                ui.accordion_panel(PANEL_TITLE, body, value="lineage_panel"),
                id="acc_lineage", open=False,
            ),
            class_="spv-panel overflow-visible spv-lin-panel",
        )

    def _chosen() -> List[str]:
        value = safe_input(input, "lineage_chosen", [])
        if isinstance(value, str):
            return [value]
        return [v for v in (value or []) if isinstance(v, str)]

    def _leaf() -> Optional[Any]:
        """The one chosen node when the choice is exactly one result table no plot reads, else None."""
        found, _ = _lineage()
        chosen = _chosen()
        if found is None or len(chosen) != 1:
            return None
        try:
            node = found.node(chosen[0])
        except KeyError:
            return None
        return node if node.kind == "result" and node.choosable else None

    @output
    @render.ui
    def lineage_step_form_ui():
        """The small form for a result table no plot reads: the column (of that place). Reads the choice only; the operator and the hint are outputs of their own (R4)."""
        node = _leaf()
        if node is None:
            return ui.div()
        offered, left_out = form_columns(node.columns)
        head = ui.tags.b(f"Audit step at {place_words(node.id)}")
        if node.columns is None:
            return ui.div(head, ui.div(f"The columns of this table are not known: {node.columns_note}. No step can be written here now.", class_="text-muted spv-text-sm"), class_="spv-lin-form")
        if not offered:
            return ui.div(head, ui.div("No column of this table can be filtered in this form.", class_="text-muted spv-text-sm"), class_="spv-lin-form")
        note = (f"{len(left_out)} column(s) of another type (date and time, time of day, duration, lists) are not offered in this form: {', '.join(left_out[:6])}"
                + (", ..." if len(left_out) > 6 else "") + ".") if left_out else ""
        return ui.div(
            head,
            ui.tags.small("No plot reads this table: a step written here changes the table and no figure. The reason is written in the Pipeline Audit panel, as for every step.",
                          class_="text-muted d-block mb-1"),
            ui.input_select("lineage_step_column", "Keep the rows where the column", choices={c: f"{c} ({t})" for c, t in offered}, selected=offered[0][0]),
            ui.output_ui("lineage_step_op_ui"),
            ui.input_text("lineage_step_value", "Value (several: separated by a comma)", value=""),
            ui.output_ui("lineage_step_hint_ui"),
            ui.input_action_button("lineage_step_add", "Add the step", class_="btn-primary"),
            ui.tags.small(note, class_="text-muted d-block mt-1") if note else ui.span(),
            class_="spv-lin-form",
        )

    def _dtype_of(node, column: str) -> Optional[str]:
        return next((t for c, t in (node.columns or ()) if c == column), None)

    @output
    @render.ui
    def lineage_step_op_ui():
        node = _leaf()
        if node is None:
            return ui.div()
        from app.modules.t3_audit_engine import op_choice_label
        column = safe_input(input, "lineage_step_column", None)
        dtype = _dtype_of(node, column) if column else None
        if dtype is None:
            return ui.div()
        ops = form_ops(dtype)
        return ui.input_select("lineage_step_op", "is", choices={o: op_choice_label(o) for o in ops}, selected=ops[0])

    @output
    @render.ui
    def lineage_step_hint_ui():
        node = _leaf()
        if node is None:
            return ui.div()
        from app.modules.t3_audit_engine import control_hint
        from utils.filter_words import no_value_words
        from utils.na_choice import default_na
        column = safe_input(input, "lineage_step_column", None)
        dtype = _dtype_of(node, column) if column else None
        op = safe_input(input, "lineage_step_op", None)
        if dtype is None:
            return ui.div()
        lines = [control_hint(dtype)] if control_hint(dtype) else []
        if op:
            lines.append(no_value_words(default_na(op), column).capitalize() + ".")
        return ui.tags.small(" ".join(line for line in lines if line), class_="text-muted d-block mb-1")

    @reactive.Effect
    @reactive.event(input.lineage_step_add)
    def _add_step_at_leaf():
        """Stage a pending step at the chosen result table: the value is read in the type of its column, refused in plain words when it cannot be; the step waits for its reason."""
        node = _leaf()
        if node is None or home_state is None:
            return
        column = safe_input(input, "lineage_step_column", None)
        op = safe_input(input, "lineage_step_op", None)
        text = safe_input(input, "lineage_step_value", "") or ""
        dtype = _dtype_of(node, column) if column else None
        if not column or not op or dtype is None:
            _notify("Choose the column and the operator first. Nothing was added.", type="warning", duration=6)
            return
        try:
            params = step_params(column, op, dtype, text)
        except FilterValueError as exc:
            _notify(f"{exc} Nothing was added.", type="error", duration=9)
            return
        from app.modules.session_manager import make_audit_step
        state = home_state.get()
        scratch = make_audit_step("filter_row", params, plot_scope=PLACES_BUCKET, reason="", primary_key_warning=column in set(state.get("primary_keys") or []))
        home_state.set(stage_nodes(state, [(scratch, node.id)], ""))
        ui.update_text("lineage_step_value", value="")
        _notify(f"Step staged at {place_words(node.id)}: {stage_sentence(params)}. No plot reads this table, so no figure changes; the table changes and its audited file is in the export "
                f"(made in Audit mode). {PENDING_NOTE}", type="message", duration=10)

    @reactive.Effect
    async def _send_marks():
        """Tell the browser which places hold an audit step (committed or pending): `{place: number of steps}`, a decision counted once at a place. Follows the steps and the panel's
        redraw (`lineage_ready`); draws nothing itself."""
        safe_input(input, "lineage_ready", None)
        if home_state is None or not in_audit():
            return
        state = home_state.get()
        seen: Dict[str, set] = {}
        for node in list((state.get("t3_audit_steps_by_plot", {}) or {}).get(PLACES_BUCKET, [])) + list(state.get("_pending_t3_nodes", [])):
            place = node.get("place") or ""
            if place:
                seen.setdefault(place, set()).add(node.get("id"))
        await session.send_custom_message("lineage_marks", {place: len(ids) for place, ids in seen.items()})
