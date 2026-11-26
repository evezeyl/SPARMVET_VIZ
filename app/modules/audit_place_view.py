"""The one reader of "what table is on screen" for HOME's data preview, as pure code (HOME audit, demo slice 2; nothing on screen reads it yet).

Today the answer is spread over HOME's data choice: `_resolve_active_lf` (which table, original or audited), `_current_view_key` (the identity of the view for the filters),
`_audit_view_state` (audited or original, for the badge). The design of 2026-11-26 (`tmpAI/panel/header_strip_audit/DESIGN_FOR_THE_OWNER.md`) makes the preview in Audit mode follow the
place chosen in the lineage panel. This module is the one place that says, for a mode and a choice:

1. `viewed(...)`: what is on screen (`Viewed`): the mode, the tier, the table, the place, whether it is the default (Audit mode with no place chosen shows the table the open plot reads), and
   whether the open plot is built from it (a place outside the open plot: a step there does not change the figure, and the screen must say so).
2. `table_for(viewed, readers)`: the lazy table and its facts (`TableFacts`): audited or original, and in plain words why it is the original. The readers are handed in (`Readers`: the
   orchestrator's reads and the audit copy's reads), so this file imports no handler and no engine.
3. `view_identity(viewed, ...)`: the key of the view for the filters. It is the key HOME uses today (`t3_audit_engine.view_key`, `viewed_table`), built from what is shown: two places that show
   the same table keep a filter built on it, another table clears it (D-0311, D-0505, D-0506).
4. `condition_fits(place, column, dtype, lineage)`: a condition built on the table shown fits another place only when the column is there with the same type, by the engine's plan
   (the lineage holds the plan's columns, D-0630).

RULES FROM THE DECISIONS (names only; read the ledger): the table shown in Audit mode is the AUDITED one where an audit step changes it and the original where none does, and the badge says
which (D-0622); a table no plot reads can be chosen in the lineage and is then shown (D-0457, D-0630); the metadata is never a place (D-0632); a filter belongs to the table it was built
on, not to the plot (D-0505, D-0506), and is cleared when the viewed table changes (D-0311).

WORDS (the owner, 2026-11-26): the last table is "Result data (T3)"; the table a plot shows is "the table the plot reads (T1, T2 or T3)"; never "plot data" or "the plot's table".

PROVISIONAL (the builder's choices, not decided by the owner): the words returned (plain, for the screen to show or reword); that with several places chosen the FIRST valid one in the order
given is shown and the others are counted (`others`), not shown (header-strip question 4 asks the owner to confirm "first clicked"); that a chosen place that is not valid is skipped and told
(`refused`) while the next valid one is shown, and the default is shown when none is valid; that `from_open_plot` is None when no plot is open; that in Exploration the identity keeps
today's rule (the data choice is in the key, so T1 and T2 of a table with no tier-2 steps are different views, which the contract marks PROVISIONAL); that the identity does not hold whether
the table shown is audited or original (the columns are the same); that `condition_fits` takes the lineage (which already holds the plan's columns) and not the plan book; that a place
whose columns are not known answers "does not fit" with the reason.

Raises: `viewed` raises KeyError for an open plot the recipe does not have (a bug of the caller, as `source_tables_of_plot`); `table_for` raises what the readers raise (an audit step that cannot
run, a table that cannot be built: HOME shows it in the table's place, never a table of another tier in its stead), and `NothingToShow` when no table can be named (no plot open and no place chosen).

Pure of Shiny and of any engine: no reactive value, no file, no global state.

Consumed by: app/tests/test_audit_place_view.py (slice 3 wires it into app/handlers/home_theater.py). If deleted: nothing, until slice 3.

# @deps
# provides: function:viewed, function:table_for, function:view_identity, function:condition_fits, class:Viewed, class:TableFacts, class:Readers, class:NothingToShow, constant:SOURCE
# consumes: libs/utils/src/utils/recipe_graph.py (RecipeGraph), libs/utils/src/utils/lineage_data.py (Lineage), app/modules/t3_audit_engine.py (view_key, viewed_table)
# consumed_by: app/tests/test_audit_place_view.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0311, D-0457, D-0505, D-0506, D-0622, D-0630, D-0632)
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Tuple

from app.modules.t3_audit_engine import view_key, viewed_table
from utils.lineage_data import Lineage
from utils.recipe_graph import RecipeGraph

SOURCE = "Source"
EXPLORATION = "exploration"
AUDIT = "audit"

# HOME's data choice: the value of `data_view` ("SRC" is the file as read) and the word of a tier shown.
_TIER_OF_CHOICE = {"SRC": SOURCE, "T1": "T1", "T2": "T2", "T3": "T3"}


class NothingToShow(LookupError):
    """No table can be named: no plot is open and no place is chosen. The message is plain."""


@dataclass(frozen=True)
class Viewed:
    """What is on screen.

    mode: "exploration" or "audit". tier: "Source", "T1", "T2" or "T3". table: the table shown (for T3, the table the plot reads; for Source, the source table); None when none can be named.
    place: the lineage node shown (`T1:<table>`, `T2:<table>`, `T3:<plot>`) in Audit mode, None in Exploration (the data choice is the tier). plot: the open plot. shown_plot: the plot whose table
    is shown at tier T3 (the open plot, or the plot of the place); None for the other tiers. is_default: Audit mode with no valid place chosen (the table the open plot reads is shown).
    from_open_plot: True when the open plot is built from what is shown (always in Exploration and for the default), False when it is not (a step written there does not change the open figure),
    None when no plot is open. others: how many OTHER valid places are chosen and not shown. refused: (place id, plain reason) for every chosen place that is not valid, in the order given."""
    mode: str
    tier: str
    table: Optional[str]
    place: Optional[str]
    plot: Optional[str]
    shown_plot: Optional[str]
    is_default: bool
    from_open_plot: Optional[bool]
    others: int = 0
    refused: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class TableFacts:
    """What is true of the table `table_for` returned. audited: True when it is the table of the audit copy. why_original: in plain words why it is the original (empty when audited, and in
    Exploration where the original is the rule). mode, tier, table, place: as in `Viewed`."""
    mode: str
    tier: str
    table: Optional[str]
    place: Optional[str]
    audited: bool
    why_original: str


@dataclass(frozen=True)
class Readers:
    """The reads the caller hands in (so that this file imports no handler and no engine). Every one returns a lazy table; an error is raised, never turned into another table.

    source(table): the table as read from its file. tier1(table), tier2(table): the original tables (tier2 gives the tier 1 table when the table has no tier-2 steps, as the orchestrator does).
    plot(plot_id): the original table the plot reads. audited_table(table, tier) with tier "T1" or "T2": the audit copy's table, or None when no committed audit step changes it
    (`PlaceAudit.table_lazy`). audited_plot(plot_id): the audit copy's table the plot reads, or None (`PlaceAudit.plot_lazy`). committed_steps: how many audit steps are committed (for the words)."""
    source: Callable[[str], Any]
    tier1: Callable[[str], Any]
    tier2: Callable[[str], Any]
    plot: Callable[[str], Any]
    audited_table: Callable[[str, str], Optional[Any]]
    audited_plot: Callable[[str], Optional[Any]]
    committed_steps: int = 0


def _refusal(graph: RecipeGraph, lineage: Lineage, place: str) -> Optional[str]:
    """None when `place` is a place of the lineage panel that can be chosen; else one plain sentence (never an exception: a stale id after a change of recipe is a normal case)."""
    ids = {n.id: n for n in lineage.nodes}
    if place in ids:
        return None if ids[place].choosable else (ids[place].not_choosable_reason or "No audit step can be written at that place.")
    if not graph.has_node(place):
        return f"'{place}' is not a place of this recipe (it may belong to the recipe that was open before)."
    node = graph.node(place)
    if node.kind == "T2" and not node.steps and not graph.is_metadata_node(place):
        return f"The table {node.name} has no tier-2 steps: its tier 2 is its tier 1. Choose its tier 1."
    problem = graph.chosen_places_problem([place])
    if problem:
        return problem
    return f"'{place}' is not a place of the path of the data."


def viewed(mode: str, data_view: str, source_table: Optional[str], open_plot: Optional[str], chosen_places: Sequence[str], graph: RecipeGraph, lineage: Lineage) -> Viewed:
    """What is on screen for HOME's mode, data choice (`data_view`: "SRC", "T1", "T2" or "T3", used in Exploration only), source table (the one the Source choice shows), open plot and the
    places chosen in the lineage panel, in the order they were chosen (used in Audit mode only). `graph` is `build_graph(raw)` and `lineage` is `lineage_of(raw, plans)` of the open recipe.

    Exploration: the data choice, as today. Audit: the first valid chosen place; with none, the table the open plot reads (is_default). Raises KeyError for an open plot that is not in the recipe."""
    if mode not in (EXPLORATION, AUDIT):
        raise ValueError(f"mode is '{EXPLORATION}' or '{AUDIT}', not {mode!r}")
    if open_plot is not None:
        open_node = f"T3:{open_plot}"
        if not graph.has_node(open_node):
            raise KeyError(f"The recipe has no plot '{open_plot}'.")
        open_target = graph.plot_target(open_plot)
    else:
        open_node, open_target = None, None
    if mode == EXPLORATION:
        if data_view not in _TIER_OF_CHOICE:
            raise ValueError(f"data_view is one of {sorted(_TIER_OF_CHOICE)}, not {data_view!r}")
        tier = _TIER_OF_CHOICE[data_view]
        table = source_table if tier == SOURCE else open_target
        return Viewed(EXPLORATION, tier, table, None, open_plot, open_plot if tier == "T3" else None, False, True if open_plot else None)
    refused = []
    valid = []
    for place in dict.fromkeys(chosen_places):
        problem = _refusal(graph, lineage, place)
        (refused if problem else valid).append((place, problem) if problem else place)
    if not valid:
        return Viewed(AUDIT, "T3", open_target, open_node, open_plot, open_plot, True, True if open_plot else None, 0, tuple(refused))
    place = valid[0]
    node = graph.node(place)
    tier = node.kind
    shown_plot = node.name if tier == "T3" else None
    table = graph.plot_target(node.name) if tier == "T3" else node.name
    if open_node is None:
        from_open = None
    else:
        from_open = place == open_node or open_node in graph.below(place)
    return Viewed(AUDIT, tier, table, place, open_plot, shown_plot, False, from_open, len(valid) - 1, tuple(refused))


def table_for(shown: Viewed, readers: Readers) -> Tuple[Any, TableFacts]:
    """The ONE reader: the lazy table of what is on screen and its facts.

    Exploration: the original of the data choice (Source, T1, T2 or the table the plot reads), as today. Audit: the audit copy's table at the place where an audit step changes it, else the
    original; the facts say which and why. A table with no tier-2 steps asked at T2 is its tier 1 (the reader does it, as the orchestrator does). Raises what the readers raise, and
    `NothingToShow` when no table can be named."""
    if shown.table is None or (shown.tier == "T3" and shown.shown_plot is None):
        raise NothingToShow("No plot is open and no place is chosen, so there is no table to show.")
    mode, tier, table, plot = shown.mode, shown.tier, shown.table, shown.shown_plot

    def facts(audited: bool, why: str) -> TableFacts:
        return TableFacts(mode, tier, table, shown.place, audited, why)

    if tier == SOURCE:
        return readers.source(table), facts(False, "This is the file as read, before any step of the recipe.")
    if mode == EXPLORATION:
        original = readers.tier1(table) if tier == "T1" else readers.tier2(table) if tier == "T2" else readers.plot(plot)
        return original, facts(False, "In Exploration the tables are the originals: audit steps are only shown in Audit mode.")
    audited = readers.audited_plot(plot) if tier == "T3" else readers.audited_table(table, tier)
    if audited is not None:
        return audited, facts(True, "")
    original = readers.tier1(table) if tier == "T1" else readers.tier2(table) if tier == "T2" else readers.plot(plot)
    why = ("No audit step has been added yet, so this is the original table." if readers.committed_steps <= 0
           else "No audit step changes this table, so this is the original table.")
    return original, facts(False, why)


def view_identity(shown: Viewed, recipe_id: str, plot_has_own_steps: bool = False) -> tuple:
    """The key of the view for the filters (`t3_audit_engine.view_key`, built from what is shown): a filter is built on this table, and when it changes the filters are cleared (D-0311).

    It holds the TABLE shown, not the place: two places that show the same table (the tier 3 of two plots that read one table and have no tier-3 steps of their own) give the same key, so a
    filter built on it is kept (D-0505, D-0506); another table, another tier, another mode or the file as read gives another key. `plot_has_own_steps`: whether the recipe writes tier-3 steps for
    `shown.shown_plot` (`view_badge.has_plot_steps`): such a plot reads a table of its own and keeps its own key. Between T1 and T2 of one table the key differs, also when the table has no tier-2
    steps (today's rule, PROVISIONAL in the contract); in Audit mode a table without tier-2 steps has no T2 place, so only Exploration can meet it."""
    if shown.tier == SOURCE:
        return view_key(recipe_id, shown.mode, "SRC", shown.table, None)
    return view_key(recipe_id, shown.mode, shown.tier, None, viewed_table(shown.tier, shown.table, shown.shown_plot, plot_has_own_steps))


def _where(node) -> str:
    if node.kind == "T3":
        return f"the Result data (T3) of the plot {node.name}"
    return f"the table {node.name} after its tier {node.tier}"


def condition_fits(place: str, column: str, dtype: Any, lineage: Lineage) -> Tuple[bool, str]:
    """Whether a condition built on `column` (of type `dtype`, the text the engine prints or the type itself) fits `place`: the column must be there with the same type (the lineage holds the
    engine's plan: never guessed from the recipe). Returns (True, "") or (False, one plain sentence): the place is not in the lineage, its columns are not known (the sentence says why), the column is
    not there, or it has another type (both types named)."""
    try:
        node = lineage.node(place)
    except KeyError:
        return False, f"'{place}' is not a place of the path of the data of this recipe."
    if node.columns is None:
        return False, f"The columns of {_where(node)} are not known ({node.columns_note}), so the condition cannot be checked there."
    found = {name: kind for name, kind in node.columns}
    if column not in found:
        return False, f"The column {column} is not in {_where(node)}."
    if found[column] != str(dtype):
        return False, f"The column {column} holds {found[column]} in {_where(node)}, not {dtype} as in the table the condition was built on."
    return True, ""
