"""
The lineage panel of HOME in Audit mode (LINEAGE-VIEW-G, D-0629, D-0634, D-0627).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.* only; the words and the layout are in app/modules/lineage_view.py.

WHAT THE USER SEES. In Audit mode, below the header strip of HOME, a collapsible panel "Path of the data" (open when Audit mode is entered). Inside: a list of the tables and plots of the recipe by
independent graph (the reader and the text twin of every dot) and a map of dots with arrows. The user chooses the places of an audit step in either, and shows one of them. The panel is drawn once for
a recipe; hover, focus, choice, the switch "Whole recipe / Around my selection" and the keyboard are the browser's (app/src/www/lineage_view.js), so a click never draws the panel again
(ui_implementation_contract.md section 14, R4). The browser tells the server the choice (`input.lineage_chosen`); the server's reading of it is the Try of a step (`trial_handlers.py`), which writes
the step at the places chosen. FLOW-3: the panel has no button that creates a step and no form (the step is created in ONE way: show an item, stage the step, Try, reason, Add to audit pipeline,
D-0662, D-0663, D-0672); a table no plot reads is shown with "Show" like any place and its condition is built in the Filters panel.

THE MARKS. Every place that holds a committed audit step gets a text mark in the list and a mark on its dot: sent to the browser as the custom message `lineage_marks`
(an effect that reads `home_state`; the panel is not drawn again).

PROVISIONAL (the builder's choices, not decided by the owner): the title and the words of the panel; that the panel is open when it is drawn (slice 3a).

# @deps
# provides: function:define_server (lineage_handlers), output:lineage_panel_ui, effect:_send_marks, effect:_send_shown, effect:_show_place
# consumes: app/modules/audit_shown.py (request_to_show), app/modules/lineage_view.py (view_data), libs/utils/src/utils/lineage_data.py (lineage_of), app/modules/audit_places.py (PLACES_BUCKET, place_words), app/src/www/lineage_view.js
# consumed_by: app/handlers/home_theater.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/rules/ui_implementation_contract.md#14, .claude/knowledge/decision_ledger.md (D-0627, D-0629, D-0634)
# @end_deps
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from shiny import reactive, render, ui

from app.modules.audit_places import PLACES_BUCKET
from app.modules.audit_shown import request_to_show
from app.modules.lineage_view import view_data
from app.modules.notification_utils import make_notifier
from app.modules.plan_composer import PlanComposerBug
from utils.lineage_data import Lineage, lineage_of
from utils.recipe_graph import RecipeGraphError

PANEL_TITLE = "Path of the data"   # PROVISIONAL


def _safe_json(data: Any) -> str:
    """JSON for a `<script type="application/json">` tag: the text cannot close the tag."""
    return json.dumps(data, separators=(",", ":")).replace("</", "<\\/")


def define_server(input, output, session, *,
                  active_cfg, in_audit, recipe_plans, home_state, safe_input,
                  notification_log=None, data_refresh_trigger=None,
                  lineage_calc=None, shown_item=None, restored_steps=None, effective_shown_place=None, open_graph=None):
    """Register the lineage panel and its marks.

    Parameters (kwargs):
      active_cfg()            the open recipe's config (`.raw_config` is the resolved dictionary)
      in_audit()              True in Audit mode (the one function of HOME)
      recipe_plans()          the engine's plan book of the open recipe, or None (`home_theater._recipe_plans`)
      home_state              reactive.Value of the audit steps and the rest of the HOME state
      safe_input(input, key, default)
      data_refresh_trigger    reactive.Value raised when data is imported (the plan book depends on the data files)
      lineage_calc            the reactive calc of the lineage of the open recipe, `(Lineage | None, reason)`, made in `home_theater` (the reader of the shown item uses it too);
                              without it the handler makes its own (the tests of the panel alone)
      shown_item              reactive.Value of the place shown in Audit mode (slice 3a); written here by the buttons "Show" and "Show selection"
      restored_steps          reactive.Value: the band's note of a restored session, cleared when the user shows something
      effective_shown_place() the place shown now, the open plot's node included (what the lineage marks as shown)
      open_graph()            the recipe graph of the open recipe (`utils.recipe_graph`)
    """
    _notify = make_notifier(notification_log)

    if lineage_calc is not None:
        _lineage = lineage_calc
    else:
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
            body = ui.div(ui.div(ui.tags.script(_safe_json(view_data(found)), type="application/json"), class_="spv-lineage", id="lineage_root"))
        return ui.div(
            ui.accordion(
                ui.accordion_panel(PANEL_TITLE, body, value="lineage_panel"),
                id="acc_lineage", open=True,
            ),
            class_="spv-panel overflow-visible spv-lin-panel",
        )

    def _chosen() -> List[str]:
        value = safe_input(input, "lineage_chosen", [])
        if isinstance(value, str):
            return [value]
        return [v for v in (value or []) if isinstance(v, str)]

    @reactive.Effect
    @reactive.event(input.lineage_show)
    def _show_place():
        """"Show" on a line of the chosen places, or "Show selection" (no place: the first place clicked): the place becomes the SHOWN ITEM (slice 3a, D-0655). A place that cannot be shown
        (a stale id, the metadata, a node that cannot be chosen) is told in plain words and nothing changes. Showing the place already shown changes nothing, so a condition being built
        on it is kept (D-0654)."""
        if shown_item is None or open_graph is None:
            return
        request = input.lineage_show()
        requested = request.get("place") if isinstance(request, dict) else None
        found, problem = _lineage()
        if found is None:
            _notify(problem or "The path of the data cannot be drawn, so nothing can be shown.", type="warning", duration=8)
            return
        try:
            outcome = request_to_show(requested, _chosen(), open_graph(), found)
        except Exception as exc:
            _notify(f"Nothing was shown: {exc}", type="warning", duration=8)
            return
        if outcome.place is None:
            _notify(outcome.problem, type="warning", duration=8)
            return
        if shown_item.get() != outcome.place:
            shown_item.set(outcome.place)
        if restored_steps is not None and restored_steps.get():
            restored_steps.set(0)

    @reactive.Effect
    async def _send_shown():
        """Tell the browser which place is shown (the open plot's node when nothing was shown yet), so that the list and the map mark it with a word and not only a colour. Follows the shown item,
        the open plot and the panel's redraw (`lineage_ready`); draws nothing itself."""
        safe_input(input, "lineage_ready", None)
        if effective_shown_place is None or not in_audit():
            return
        await session.send_custom_message("lineage_shown", {"place": effective_shown_place()})

    @reactive.Effect
    async def _send_marks():
        """Tell the browser which places hold an audit step: `{place: number of steps}`, a decision counted once at a place. Follows the steps and the panel's
        redraw (`lineage_ready`); draws nothing itself."""
        safe_input(input, "lineage_ready", None)
        if home_state is None or not in_audit():
            return
        state = home_state.get()
        seen: Dict[str, set] = {}
        for node in list((state.get("t3_audit_steps_by_plot", {}) or {}).get(PLACES_BUCKET, [])):
            place = node.get("place") or ""
            if place:
                seen.setdefault(place, set()).add(node.get("id"))
        await session.send_custom_message("lineage_marks", {place: len(ids) for place, ids in seen.items()})
