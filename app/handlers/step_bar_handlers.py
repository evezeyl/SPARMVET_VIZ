"""The step bar of HOME in Audit mode: the screen of the ONE entry that creates an audit step (ledger D-0663, D-0672; built 2026-11-27, PROVISIONAL words and layout).

Two-Category Law (ADR-045): this module holds @render.* only. The words and the rules of the button are `app/modules/step_bar.py` (no Shiny); the effects of Try, Add and Discard are
`app/handlers/trial_handlers.py`; the form of a condition stays in the Filters panel (`app/handlers/filter_and_audit_handlers.py`; see "WHY THE FORM STAYS" below).

WHAT THE USER SEES (Audit mode only). A bar with the data preview, in a region labelled "Create an audit step", in the order the user meets it:
  1. what it acts on: the band `shown_band_ui`, mounted by the bar (the item shown with its tag as the lineage writes it, its state original / audited / TRIAL, "N other places chosen, not shown" with their names on hover);
  2. the plain switch "Step to create": Condition on rows | Drop columns (one kind at a time, D-0672);
  3. the step being built, in words: for a condition, the staged rows (built in the Filters panel of the left column); for a drop, the columns deselected in the column chooser, named;
  4. the button Try, with the one plain line that says why it is off when it is off;
  5. the fold-out of the answer (`trial_panel_ui`: the places, the marks "User verified", the reason, "Add to audit pipeline", "Discard"); it is folded with its summary line.
In Exploration the bar does not exist (its output is empty: no region, no landmark) and the Filters panel holds the form.

WHY THE FORM STAYS IN THE FILTERS PANEL (the brief asked to try to move it; the evidence says it cannot be moved soundly in this slice). The form's inputs and outputs (`fb_col`, `fb_op`,
`filter_rows_ui`, `filter_add_row`, ...) have ids, and an id must be mounted ONCE in the page. The server-side way (the Filters panel and the bar each mount the form's slots, chosen by the mode)
was built and run on 2026-11-27: on a mode switch the browser binds the new container's outputs before it unbinds the old one's in the same flush, and Shiny reports "Duplicate output ID was found"
(`filter_rows_ui`, `filter_form_ui`, `filter_op_ui`, `fb_op`, `fb_value`, 2 each; a client error panel in dev mode, a console warning otherwise). The alternatives are a two-phase mount with an
acknowledgment from the browser, or a script that moves one set of elements between containers that three outputs redraw (`dynamic_tabs`, the left sidebar, the bar) and that must unbind and bind
them again at every redraw: neither is sound enough for one slice. So the form is mounted once, in the Filters panel, in both modes; the bar names the condition staged there in words and holds
the one button Try. `app/tests/test_step_bar_browser.py` counts the ids of the form in both modes (one each).

R1 to R4 (ui_implementation_contract.md section 14): the outputs only read; `step_bar_ui` reads the mode and nothing else (the kind switch is mounted by it and read by the two small outputs beside it,
never by itself); the visibility of the condition and of the drop part follows the switch in the browser (`app/src/www/step_bar.js`, an attribute of the bar), so typing in the form never redraws it.

# @deps
# provides: function:define_step_bar_server, output:step_bar_ui, output:step_bar_condition_ui, output:step_bar_drop_ui, output:step_bar_actions_ui, input:step_kind, button:step_try
# consumes: app/modules/step_bar.py, app/modules/audit_try.py (COUNTING, drops_from_selection), app/handlers/trial_handlers.py (trial_panel_ui, mounted by id)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/rules/ui_implementation_contract.md#14, .claude/knowledge/decision_ledger.md (D-0663, D-0672)
# @end_deps
"""
from __future__ import annotations

from typing import Callable, Optional

from shiny import render, ui

from app.modules.audit_try import COUNTING, KIND_FILTER, condition_lines
from app.modules.step_bar import CONDITION_EDIT_HINT, CONDITION_HINT, KIND_CHOICES, KIND_LABEL, STEP_BAR_LABEL, TRY_BUTTON, drop_words, kind_of_input, try_state


def define_step_bar_server(input, output, session, *, in_audit: Callable[[], bool], safe_input, pending_filters, shown_place: Callable[[], Optional[str]],
                           columns_at):
    """Register the outputs of the step bar.

    Parameters (kwargs):
      in_audit()       True in Audit mode (the one function of HOME)
      safe_input       the HOME helper that reads an input with a default
      pending_filters  reactive.Value[list]: the staged rows (the condition); read by the button's state only
      shown_place()    the place shown (the open plot's node when nothing was shown), or None
      columns_at(p)    the names and types of the table present at place `p` in the AUDITED state, or None
    """

    def _columns_of_shown(place: Optional[str]) -> list:
        """The names of the columns of the table shown (the audited one: a column an applied step dropped is not in it); empty when there is none."""
        if not place:
            return []
        try:
            return [name for name, _ in (columns_at(place) or ())]
        except Exception:
            return []

    @output
    @render.ui
    def step_bar_ui():
        """The inside of the bar. Reads the mode and nothing else, so it is drawn when the mode changes and never while the user types or chooses (R4)."""
        if not in_audit():
            return ui.div()
        return ui.div(
            ui.output_ui("shown_band_ui"),
            ui.div(
                ui.tags.span("Step:", class_="spv-stepbar-kind-label", **{"aria-hidden": "true"}),
                ui.input_radio_buttons("step_kind", label=ui.span(KIND_LABEL, class_="visually-hidden"), choices=KIND_CHOICES, selected=KIND_FILTER, inline=True),
                class_="spv-stepbar-kind",
            ),
            ui.div(ui.output_ui("step_bar_condition_ui"), class_="spv-stepbar-condition"),
            ui.div(ui.output_ui("step_bar_drop_ui"), class_="spv-stepbar-drop"),
            ui.output_ui("step_bar_actions_ui"),
            ui.div(COUNTING, class_="spv-try-counting", role="status"),
            ui.output_ui("trial_panel_ui"),
            class_="spv-stepbar spv-stepbar-inner",
            role="region",
            **{"aria-label": STEP_BAR_LABEL, "data-kind": KIND_FILTER},
        )

    @output
    @render.ui
    def step_bar_condition_ui():
        """The step being built when it is a condition, in words: the staged rows (their remove buttons and the form are in the Filters panel of the left column). Reads the staged rows only."""
        if not in_audit():
            return ui.div()
        rows = list(pending_filters.get())
        if not rows:
            return ui.div(ui.div(CONDITION_HINT, class_="spv-stepbar-line", role="status"))
        return ui.div(*[ui.div(line, class_="spv-stepbar-line") for line in condition_lines(rows)], ui.div(CONDITION_EDIT_HINT, class_="spv-stepbar-why"))

    @output
    @render.ui
    def step_bar_drop_ui():
        """The step being built when it is a column drop: the columns the column chooser does not select, named (the chooser is mounted by `home_col_selector_ui`, read here only)."""
        if not in_audit():
            return ui.div()
        place = shown_place()
        enabled, why, columns = try_state("drop", 0, place, _columns_of_shown(place), safe_input(input, "preview_col_selector", None))
        return ui.div(ui.div(drop_words(columns) if enabled else why, class_="spv-stepbar-line", role="status"))

    @output
    @render.ui
    def step_bar_actions_ui():
        """The button Try and, when it is off, the one line that says why. It reads the switch, the staged rows and the chooser's choice (all mounted elsewhere) and mounts the button only."""
        if not in_audit():
            return ui.div()
        kind = kind_of_input(safe_input(input, "step_kind", KIND_FILTER))
        place = shown_place()
        enabled, why, _columns = try_state(kind, len(pending_filters.get()), place, _columns_of_shown(place), safe_input(input, "preview_col_selector", None))
        return ui.div(
            ui.input_action_button(
                "step_try", TRY_BUTTON, class_="btn-primary btn-sm spv-text-xs", disabled=not enabled,
                title="Computes what this step would do at the place shown (and the other places you chose in Path of the data): the rows or columns it removes at each place, and what is built "
                      "from them. Nothing is applied, saved or exported until you add it to the audit pipeline."),
            ui.div(why, class_="spv-stepbar-why", role="status") if why else ui.span(),
            class_="spv-stepbar-actions",
        )
