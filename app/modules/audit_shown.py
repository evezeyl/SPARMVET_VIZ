"""The shown item of HOME in Audit mode: what "Show" does, what the band says, when a selection is not the table shown (slice 3a of the new Audit flow; pure code, no Shiny).

THE RULE (D-0655, D-0653, D-0654, D-0657; the owner's words are in the ledger): in Audit mode, choosing a place in "Path of the data" only STAGES it. A button shows it: "Show" on a line
of the list of the chosen places, or "Show selection" (the first place clicked). The place shown is the SHOWN ITEM: the data preview, its title, its badge, the column chooser and the filter form read
its table through `app/modules/audit_place_view.py` (the one reader), nothing else. With no item shown the preview shows the table the open plot reads (her answer 1, a: `Viewed.is_default`).
In Audit mode there are no plot tabs (slice 3b, D-0657): the plot shown IS the open plot; a click on a plot tab in Exploration only says which plot is shown by default when Audit mode is entered.

This module holds the small decisions around that, so that they can be tested without a browser:

- `request_to_show(requested, chosen, graph, lineage)`: which place a "Show" or a "Show selection" shows, or why nothing is shown (`ShowOutcome`). A stale id, the metadata, a place that cannot be chosen
  never raises: it is a plain sentence (the same refusals as `audit_place_view.viewed`).
- `others_chosen(chosen, shown_place)`: how many chosen places are not the one shown (the band says "N other places chosen, not shown").
- `band_lines(...)`: the words of the band above the preview.
- `open_subtab_of(viewed)`: the open plot of Audit mode (the plot shown, "" while a table is shown), `plot_area_title(name)` and `table_shown_lines(name, plots)`: the words of the plot area; `table_shown_in_panel(place)` and `unlisted_pending_line(...)`: what the right panel needs.
- `selection_problem(chosen, shown_place)`: "Show your selection first" when the places chosen do not include the place shown (item 9 of the brief; PROVISIONAL, see the handler for where it is asked).

PROVISIONAL (the builder's words and choices; the owner reads them): every sentence below; that "Show selection" shows the first place clicked (header-strip question 4 says so; the browser keeps the
order of the clicks).

Consumed by: app/handlers/lineage_handlers.py, app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/audit_stack.py, app/tests/test_audit_shown.py. If deleted: HOME's Audit mode has no shown item.

# @deps
# provides: function:request_to_show, function:others_chosen, function:band_lines, function:selection_problem, function:open_subtab_of, function:table_shown_in_panel, function:plot_area_title, function:table_shown_lines, class:ShowOutcome, constant:CHOOSE_FIRST, constant:SHOW_SELECTION_FIRST
# consumes: app/modules/audit_place_view.py (viewed, TableFacts), libs/utils/src/utils/lineage_data.py (Lineage), libs/utils/src/utils/recipe_graph.py (RecipeGraph)
# consumed_by: app/handlers/lineage_handlers.py, app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/audit_stack.py, app/tests/test_audit_shown.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0653, D-0654, D-0655, D-0657)
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from app.modules.audit_place_view import AUDIT, TableFacts, Viewed, viewed
from utils.lineage_data import Lineage
from utils.recipe_graph import RecipeGraph

CHOOSE_FIRST = "Choose a place in Path of the data first. Nothing was shown."
SHOW_SELECTION_FIRST = ("Show your selection first: the place you chose is not the table shown, and the condition was built on the table shown. "
                        "Press Show beside the place, then build the condition on it. Nothing was tried.")


@dataclass(frozen=True)
class ShowOutcome:
    """What a request to show comes to: `place` (the id to show) or None with `problem` (one plain sentence). Exactly one of them is set."""
    place: Optional[str]
    problem: str = ""


def request_to_show(requested: Optional[str], chosen: Sequence[str], graph: RecipeGraph, lineage: Lineage) -> ShowOutcome:
    """The place a request shows. `requested` is the place of the "Show" that was pressed, None for "Show selection" (the first place chosen, in the order the user clicked). A place that is
    not valid (a stale id after a change of recipe, the metadata, a table with no tier 2, a node that cannot be chosen) gives its plain reason and shows nothing: the app never picks another
    place in its stead."""
    place = requested if requested else (chosen[0] if chosen else None)
    if not place:
        return ShowOutcome(None, CHOOSE_FIRST)
    state = viewed(AUDIT, "T3", None, None, [place], graph, lineage)
    if state.refused:
        return ShowOutcome(None, state.refused[0][1])
    return ShowOutcome(place)


def others_chosen(chosen: Sequence[str], shown_place: Optional[str]) -> int:
    """How many distinct chosen places are not the one shown (they are staged, not shown)."""
    return len([c for c in dict.fromkeys(chosen) if c != shown_place])


def band_lines(name: str, facts: TableFacts, others: int = 0, from_open_plot: Optional[bool] = None, restored_steps: int = 0,
               nothing_note: str = "") -> tuple:
    """The lines of the band above the preview, first line first. `name` is the text the lineage panel writes for the place (`lineage_view.line_text`); `facts` says original or audited and why
    (`audit_place_view.table_for`); `others`: the chosen places that are not shown; `from_open_plot`: False when the open plot is not built from what is shown (a step written there does not
    change the open figure); `restored_steps`: the number of audit steps of a restored session (the band says they are applied). A view with nothing to show gives its note."""
    lines = []
    if restored_steps > 0:
        lines.append(f"Restored session: {restored_steps} audit step{' is' if restored_steps == 1 else 's are'} applied.")
    if facts.table is None:
        lines.append(nothing_note or facts.why_original)
        if others:
            lines.append(_others_words(others))
        return tuple(lines)
    head = f"Shown: {name}. {facts.words}"
    lines.append(head)
    if facts.why_original:
        lines.append(facts.why_original)
    if facts.no_plot_reads:
        lines.append("No plot reads this table.")
    elif from_open_plot is False:
        lines.append("The open plot is not built from this table: a step written here does not change the open figure.")
    if others:
        lines.append(_others_words(others))
    return tuple(lines)


def _others_words(n: int) -> str:
    return f"{n} other place{'' if n == 1 else 's'} chosen, not shown."


def selection_problem(chosen: Sequence[str], shown_place: Optional[str]) -> Optional[str]:
    """None when the places chosen are consistent with the place shown (nothing chosen, or the shown place is among them); else `SHOW_SELECTION_FIRST`. A condition is built on the table
    shown, so a confirmation that names other places than the one shown asks the user to show them first (PROVISIONAL, the design page's recommendation (a): D-0655 point 5)."""
    chosen = [c for c in dict.fromkeys(chosen) if c]
    if not chosen or shown_place in chosen:
        return None
    return SHOW_SELECTION_FIRST



def open_subtab_of(shown: Optional[Viewed]) -> str:
    """The open plot of Audit mode, as the id of its tab ("subtab_<plot>"): the plot SHOWN (the default plot when nothing is shown). While a table is shown, or when nothing can be shown
    (`None`, the recipe cannot be read; the nothing-chosen state), no plot is open: "". Every reader of "the open plot" gets this in Audit mode (slice 3b, D-0657)."""
    if shown is None or shown.nothing_chosen or not shown.shown_plot:
        return ""
    return f"subtab_{shown.shown_plot}"


def plot_area_title(name: str) -> str:
    """The one line above the plot of Audit mode (it replaces the name the tab carried in Exploration). PROVISIONAL words."""
    return f"Plot shown: {name}"


def table_shown_lines(name: str, plot_names: Sequence[str]) -> tuple:
    """The lines of the plot area while a table is shown (D-0655 rule 1): the table is not a plot's final data, so there is no figure; the plots built from it are named, as information
    (not buttons to tick). `name` is the text the lineage panel writes for the table; `plot_names` the plots built from it. PROVISIONAL words."""
    lines = [f"No figure: {name} is a table, not the Result data (T3) of a plot."]
    if plot_names:
        n = len(plot_names)
        lines.append(f"{n} plot{'' if n == 1 else 's'} {'is' if n == 1 else 'are'} built from it: {', '.join(plot_names)}.")
        lines.append("To see a figure, choose a plot in Path of the data and press Show.")
    else:
        lines.append("No plot is built from it. To see a figure, choose a plot in Path of the data and press Show.")
    return tuple(lines)


def table_shown_in_panel(shown_place: Optional[str]) -> str:
    """The node of the table shown ("T1:<table>" or "T2:<table>"), or "" when a plot is shown or nothing is (Exploration, `audit_shown_place` None). The right panel (`audit_stack`) lists the
    steps of the TABLE then, not of a plot."""
    place = shown_place or ""
    return place if place[:3] in ("T1:", "T2:") else ""
