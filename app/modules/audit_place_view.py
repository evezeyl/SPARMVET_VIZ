"""The one reader of "what table is on screen" for HOME's data preview, as pure code (HOME audit, demo slice 2; nothing on screen reads it yet).

Today the answer is spread over HOME's data choice: `_resolve_active_lf` (which table, original or audited), `_current_view_key` (the identity of the view for the filters),
`_audit_view_state` (audited or original, for the badge). The design of 2026-11-26 (`tmpAI/panel/header_strip_audit/DESIGN_FOR_THE_OWNER.md`) makes the preview in Audit mode follow the
place chosen in the lineage panel. This module is the one place that says, for a mode and a choice:

1. `viewed(...)`: what is on screen (`Viewed`): the mode, the tier, the table, the place, whether it is the default (Audit mode with no place chosen shows the table the open plot reads), and
   whether the open plot is built from it (a place outside the open plot: a step there does not change the figure, and the screen must say so).
2. `table_for(viewed, readers)`: the lazy table and its facts (`TableFacts`): its state (original, audited or trial), and in plain words why it is the original. The readers are handed in (`Readers`: the
   orchestrator's reads and the audit copy's reads), so this file imports no handler and no engine.
3. `view_identity(viewed, ...)`: the key of the view for the filters. It is the key HOME uses today (`t3_audit_engine.view_key`, `viewed_table`), built from what is shown: two places that show
   the same table keep a filter built on it, another table clears it (D-0311, D-0505, D-0506).
4. `condition_fits(place, column, dtype, lineage)`: a condition built on the table shown fits another place only when the column is there with the same type, by the engine's plan
   (the lineage holds the plan's columns, D-0630).

RULES FROM THE DECISIONS (names only; read the ledger): the table shown in Audit mode is the AUDITED one where an audit step changes it and the original where none does, and the badge says
which (D-0622); a table no plot reads can be chosen in the lineage and is then shown (D-0457, D-0630); the metadata is never a place (D-0632); a filter belongs to the table it was built
on, not to the plot (D-0505, D-0506), and is cleared when the viewed table changes (D-0311).

THE PLACE ALONE DRIVES THE VIEW IN AUDIT MODE (owner, 2026-11-26): an open plot is not needed. A table no plot reads, a recipe with no plot at all and no plot open are all reachable: the place chosen in
"Path of the data" is shown (`from_open_plot` is None without an open plot; `no_plot_reads` says that no plot is built from it, from the lineage). With NO valid place: the table the open plot reads
(the default, as built); with no open plot either, the "nothing chosen" state (`Viewed.nothing_chosen`, `table` None, `note` "Choose a place in Path of the data to see a table."), never a table picked for the
user. PROVISIONAL: the owner allowed "the first table of the lineage" or an empty state; the empty state is the coordinator's choice because the app does not choose for the user.
EXPLORATION WITH NO OPEN PLOT: today's code takes the first plot of the recipe (`_resolve_active_spec`, home_theater.py:311-316) and shows its table; with a recipe with no plot, the T1, T2 and T3 choices read the
app's open anchor (`_resolve_t1_lf`, home_theater.py:341-342; `tier1_anchor`, server.py:178-191: an empty table when none is open, no table of the recipe) and the Source choice raises "The plot of this view is
not a plot of the open data analysis recipe" (`_read_source_lf`). `viewed` returns the table the first plot reads in the first case and the nothing-chosen state in the second (the anchor is no table of the recipe).

WORDS (the owner, 2026-11-26): the last table is "Result data (T3)"; the table a plot shows is "the table the plot reads (T1, T2 or T3)"; never "plot data" or "the plot's table".

PROVISIONAL (the builder's choices, not decided by the owner): the words returned (plain, for the screen to show or reword); that with several places chosen the FIRST valid one in the order
given is shown and the others are counted (`others`), not shown (header-strip question 4 asks the owner to confirm "first clicked"); that a chosen place that is not valid is skipped and told
(`refused`) while the next valid one is shown, and the default is shown when none is valid; that `from_open_plot` is None when no plot is open; that in Exploration the identity keeps
today's rule (the data choice is in the key, so T1 and T2 of a table with no tier-2 steps are different views, which the contract marks PROVISIONAL); that the identity does not hold the state (original, audited, trial) but, when the caller gives the
columns of the table shown, a digest of them (a column drop changes the columns); that `condition_fits` takes the lineage (which already holds the plan's columns) and not the plan book; that a place
whose columns are not known answers "does not fit" with the reason.

Raises: `viewed` raises KeyError for an open plot the recipe does not have (a bug of the caller, as `source_tables_of_plot`); `table_for` raises what the readers raise (an audit step that cannot
run, a table that cannot be built: HOME shows it in the table's place, never a table of another tier in its stead), and `NothingToShow` only for a fault (a view with no table that is not the nothing-chosen state).

Pure of Shiny and of any engine: no reactive value, no file, no global state.

WHAT THE CALLER (SLICE 3) MUST DO
- `viewed` needs the graph and the lineage of the OPEN recipe; an open plot that is not in the recipe is a caller bug (KeyError).
- Pass the effective source table for the Source choice (`source_table`); with none, the value `nothing_chosen` with its note comes back (a plot that reads no source table).
- Pass `plot_has_own_steps` to `view_identity` for `shown.shown_plot` (the plot whose table is shown), not for the open plot: with no tab open they differ.
- In Audit mode pass `columns` (the schema of the table shown) to `view_identity`, and `columns` (the table present at the place, in the state the step will meet) to `condition_fits`.
- The readers must raise for an audit step that cannot run, and the screen shows that error in the table's place: this module never turns an error into another table.
- Show `TableFacts.words` in the title, and `Viewed.note`, `no_plot_reads` and `from_open_plot` as the design says.

Consumed by: app/tests/test_audit_place_view.py (slice 3 wires it into app/handlers/home_theater.py). If deleted: nothing, until slice 3.

# @deps
# provides: function:viewed, function:table_for, function:view_identity, function:condition_fits, class:Viewed, class:TableFacts, class:Readers, class:NothingToShow, constant:SOURCE
# consumes: libs/utils/src/utils/recipe_graph.py (RecipeGraph), libs/utils/src/utils/lineage_data.py (Lineage), app/modules/t3_audit_engine.py (view_key, viewed_table)
# consumed_by: app/tests/test_audit_place_view.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0311, D-0457, D-0505, D-0506, D-0622, D-0630, D-0632)
# @end_deps
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Tuple

from app.modules.t3_audit_engine import view_key, viewed_table
from utils.lineage_data import Lineage
from utils.recipe_graph import RecipeGraph

SOURCE = "Source"
# The three states of a table or a plot on screen (the design study of 2026-11-26): the original, the audited (the applied steps) and the trial (a step being tried, not applied).
ORIGINAL, AUDITED, TRIAL = "original", "audited", "trial"
STATE_WORDS = {ORIGINAL: "Original (as read)",
               AUDITED: "Audited: your applied steps",
               TRIAL: "TRIAL: with the step you are trying. Not applied, not saved, not exported."}   # PROVISIONAL words
NO_SOURCE_NOTE = "This plot reads no source table, so there is no file to show as read."   # PROVISIONAL words
CHOOSE_A_PLACE = "Choose a place in Path of the data to see a table."
NO_PLOT_NOTE = "The recipe has no plot, so there is no table to show here. In Audit mode, choose a place in Path of the data."
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
    None when no plot is open. others: how many OTHER valid places are chosen and not shown. refused: (place id, plain reason) for every chosen place that is not valid, in the order given.
    no_plot_reads: True when no plot is built from what is shown (a table no plot reads, chosen in the lineage): the title can say so; computed from the lineage, not from the open plot.
    nothing_chosen: the state "there is nothing to show yet" (Audit mode with no valid place and no open plot; Exploration with no plot in the recipe): `table` is None and `note` says what to do. It is a
    value, not an exception: the app does not choose a table for the user."""
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
    no_plot_reads: bool = False
    nothing_chosen: bool = False
    note: str = ""


@dataclass(frozen=True)
class TableFacts:
    """What is true of the table `table_for` returned. state: "original", "audited" (the table of the audit copy: the applied steps) or "trial" (a step being tried, not applied); `words` is its plain
    sentence (`STATE_WORDS`). why_original: in plain words why it is the original (empty when audited or trial, and in Exploration where the original is the rule). mode, tier, table, place: as in `Viewed`."""
    mode: str
    tier: str
    table: Optional[str]
    place: Optional[str]
    state: str
    why_original: str
    no_plot_reads: bool = False

    @property
    def words(self) -> str:
        """The plain words of the state, for the title of the table."""
        return STATE_WORDS[self.state]


@dataclass(frozen=True)
class Readers:
    """The reads the caller hands in (so that this file imports no handler and no engine). Every one returns a lazy table; an error is raised, never turned into another table.

    source(table): the table as read from its file. tier1(table), tier2(table): the original tables (tier2 gives the tier 1 table when the table has no tier-2 steps, as the orchestrator does).
    plot(plot_id): the original table the plot reads. audited_table(table, tier) with tier "T1" or "T2": the audit copy's table, or None when no committed audit step changes it
    (`PlaceAudit.table_lazy`). audited_plot(plot_id): the audit copy's table the plot reads, or None (`PlaceAudit.plot_lazy`). committed_steps: how many audit steps are committed (for the words).
    trial_table(table, tier) and trial_plot(plot_id): optional (None by default). When given and they return a table, `table_for` returns it with the state "trial" (Audit mode only: a step being tried,
    not applied); when they return None (the tried step does not change this item) the audited or the original answer is given as before. This module computes no trial: it only reads what it is handed."""
    source: Callable[[str], Any]
    tier1: Callable[[str], Any]
    tier2: Callable[[str], Any]
    plot: Callable[[str], Any]
    audited_table: Callable[[str, str], Optional[Any]]
    audited_plot: Callable[[str], Optional[Any]]
    committed_steps: int = 0
    trial_table: Optional[Callable[[str, str], Optional[Any]]] = None
    trial_plot: Optional[Callable[[str], Optional[Any]]] = None


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
        plot = open_plot
        if plot is None and graph.plots():
            plot = graph.plots()[0]          # what HOME does today with no tab open: `_resolve_active_spec` takes the first plot of the recipe (home_theater.py:311-316)
        if plot is None:
            return Viewed(EXPLORATION, tier, None, None, None, None, False, None, nothing_chosen=True, note=NO_PLOT_NOTE)
        if tier == SOURCE and not source_table:
            # a plot that reads no source table is a normal case (HOME says so in plain words today, `_read_source_lf`): a value, not an exception
            return Viewed(EXPLORATION, tier, None, None, open_plot, None, False, True if open_plot else None, nothing_chosen=True, note=NO_SOURCE_NOTE)
        table = source_table if tier == SOURCE else graph.plot_target(plot)
        return Viewed(EXPLORATION, tier, table, None, open_plot, plot if tier == "T3" else None, False, True if open_plot else None)
    refused = []
    valid = []
    for place in dict.fromkeys(chosen_places):
        problem = _refusal(graph, lineage, place)
        (refused if problem else valid).append((place, problem) if problem else place)
    if not valid:
        if open_plot is None:
            return Viewed(AUDIT, "", None, None, None, None, False, None, 0, tuple(refused), nothing_chosen=True, note=CHOOSE_A_PLACE)
        return Viewed(AUDIT, "T3", open_target, open_node, open_plot, open_plot, True, True, 0, tuple(refused))
    place = valid[0]
    node = graph.node(place)
    tier = node.kind
    shown_plot = node.name if tier == "T3" else None
    table = graph.plot_target(node.name) if tier == "T3" else node.name
    from_open = None if open_node is None else (place == open_node or open_node in graph.below(place))
    no_plot = not any(lineage.node(r).kind == "T3" for r in lineage.reach[place].results)
    return Viewed(AUDIT, tier, table, place, open_plot, shown_plot, False, from_open, len(valid) - 1, tuple(refused), no_plot_reads=no_plot)


def table_for(shown: Viewed, readers: Readers) -> Tuple[Any, TableFacts]:
    """The ONE reader: the lazy table of what is on screen and its facts.

    Exploration: the original of the data choice (Source, T1, T2 or the table the plot reads), as today. Audit: the TRIAL table when the caller hands in a trial reader that answers for this item,
    else the audit copy's table at the place where an applied audit step changes it, else the original; the facts say which (`state`) and why. A table with no tier-2 steps asked at T2 is its tier 1 (the reader does it, as the orchestrator does). Raises what the readers raise, and
    `NothingToShow` only for a view that names no table although it is not the nothing-chosen state (a bug). For the nothing-chosen state it returns (None, facts) with the note in `why_original`."""
    if shown.nothing_chosen:
        return None, TableFacts(shown.mode, shown.tier, None, None, ORIGINAL, shown.note, False)
    if shown.table is None or (shown.tier == "T3" and shown.shown_plot is None):
        raise NothingToShow("This view names no table although it is not the nothing-chosen state: a bug of the caller.")
    mode, tier, table, plot = shown.mode, shown.tier, shown.table, shown.shown_plot

    def facts(state: str, why: str) -> TableFacts:
        return TableFacts(mode, tier, table, shown.place, state, why, shown.no_plot_reads)

    if tier == SOURCE:
        return readers.source(table), facts(ORIGINAL, "This is the file as read, before any step of the recipe.")
    if mode == EXPLORATION:
        original = readers.tier1(table) if tier == "T1" else readers.tier2(table) if tier == "T2" else readers.plot(plot)
        return original, facts(ORIGINAL, "In Exploration the tables are the originals: audit steps are only shown in Audit mode.")
    trial = None
    if tier == "T3" and readers.trial_plot is not None:
        trial = readers.trial_plot(plot)
    elif tier != "T3" and readers.trial_table is not None:
        trial = readers.trial_table(table, tier)
    if trial is not None:
        return trial, facts(TRIAL, "")
    audited = readers.audited_plot(plot) if tier == "T3" else readers.audited_table(table, tier)
    if audited is not None:
        return audited, facts(AUDITED, "")
    original = readers.tier1(table) if tier == "T1" else readers.tier2(table) if tier == "T2" else readers.plot(plot)
    why = ("No audit step has been added yet, so this is the original table." if readers.committed_steps <= 0
           else "No audit step changes this table, so this is the original table.")
    return original, facts(ORIGINAL, why)


def columns_digest(columns: Sequence[Tuple[str, Any]]) -> str:
    """A stable digest of the names and types of a table's columns (type text as the engine prints it), independent of the order of the columns: the same columns in another order give the same digest."""
    pairs = sorted((str(name), str(kind)) for name, kind in columns)
    return hashlib.sha256(json.dumps(pairs).encode("utf-8")).hexdigest()[:16]


def view_identity(shown: Viewed, recipe_id: str, plot_has_own_steps: bool = False, columns: Optional[Sequence[Tuple[str, Any]]] = None) -> tuple:
    """The key of the view for the filters (`t3_audit_engine.view_key`, built from what is shown): a filter is built on this table, and when it changes the filters are cleared (D-0311).

    It holds the TABLE shown, not the place: two places that show the same table (the tier 3 of two plots that read one table and have no tier-3 steps of their own) give the same key, so a
    filter built on it is kept (D-0505, D-0506); another table, another tier, another mode or the file as read gives another key. `plot_has_own_steps`: whether the recipe writes tier-3 steps for
    `shown.shown_plot` (`view_badge.has_plot_steps`), the plot whose table is shown: with no plot tab open that is the plot the view falls back to, NOT the open plot (which is None). Such a plot reads a
    table of its own and keeps its own key. Between T1 and T2 of one table the key differs, also when the table has no tier-2 steps (today's rule, PROVISIONAL in the contract); in Audit mode a
    table without tier-2 steps has no T2 place, so only Exploration can meet it.

    THE COLUMNS. `columns` is the names and types of the table SHOWN, as the caller reads them from that table's schema (a sequence of (name, type) pairs). When it is given, the key holds a digest of
    them (`columns_digest`: sorted, so the order of the columns alone changes nothing), and a change of the shown table's columns or types gives another key, so the filters are cleared: an applied
    column drop removes a column from the audited table, and a filter row built on that column must not survive. When it is not given, the key is exactly HOME's `view_key` of today. Slice 3 passes
    `columns` in Audit mode, where the audit steps can change the columns; Exploration shows the original tables and passes nothing, so its key stays equal to HOME's current key.

    The key does NOT hold the state (original, audited or trial) by itself: an applied row filter leaves the columns as they are, so a filter built on the original stays valid when the audited table is
    shown, and nothing is cleared by the state alone. A step that changes the columns (a column drop) does change them, and then `columns` changes the key. The caller shows the state in the title
    (`TableFacts.words`)."""
    if shown.tier == SOURCE:
        key = view_key(recipe_id, shown.mode, "SRC", shown.table, None)
    else:
        key = view_key(recipe_id, shown.mode, shown.tier, None, viewed_table(shown.tier, shown.table, shown.shown_plot, plot_has_own_steps))
    return key if columns is None else key + (columns_digest(columns),)


def _where(node) -> str:
    if node.kind == "T3":
        return f"the Result data (T3) of the plot {node.name}"
    return f"the table {node.name} after its tier {node.tier}"


def condition_fits(place: str, column: str, dtype: Any, lineage: Lineage, columns: Optional[Sequence[Tuple[str, Any]]] = None) -> Tuple[bool, str]:
    """Whether a condition built on `column` (of type `dtype`, the text the engine prints or the type itself) fits `place`: the column must be there with the same type.

    `columns` (optional) is the names and types of the table actually present at that place in the state the step will meet (the schema of the audited or tried table, as the caller reads it): when
    given it decides. Without it the lineage decides, and the lineage holds the engine's plan of the ORIGINAL recipe: a column dropped by an applied or tried audit step still "fits" there. The caller
    must therefore pass `columns` whenever audit steps exist. Returns (True, "") or (False, one plain sentence): the place is not in the lineage, its columns are not known (the sentence says why), the
    column is not there, or it has another type (both types named)."""
    try:
        node = lineage.node(place)
    except KeyError:
        return False, f"'{place}' is not a place of the path of the data of this recipe."
    if columns is None:
        if node.columns is None:
            return False, f"The columns of {_where(node)} are not known ({node.columns_note}), so the condition cannot be checked there."
        columns = node.columns
        where = _where(node)
    else:
        where = f"{_where(node)} as it is with the steps now applied or tried"
    found = {str(name): str(kind) for name, kind in columns}
    if column not in found:
        return False, f"The column {column} is not in {where}."
    if found[column] != str(dtype):
        return False, f"The column {column} holds {found[column]} in {where}, not {dtype} as in the table the condition was built on."
    return True, ""
