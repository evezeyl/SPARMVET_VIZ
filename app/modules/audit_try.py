"""TRYING an audit step on screen: the pure rules of the new Audit flow, FLOW-1 (no Shiny, no file, no engine; the screen is `app/handlers/trial_handlers.py`).

The model (ledger D-0656, D-0662, D-0669, D-0671; `.claude/design/home_audit_what_is_true_now.md`): in Audit mode the user builds a condition in the Filters panel on the table shown and
presses Try. The step is written at the place shown, plus the other places chosen in "Path of the data" when the place shown is among them (D-0669: all the places chosen). The engine
(`app/modules/audit_trial.py`, `PlaceTrial`) computes the effect: nothing is applied, saved or exported. This module decides what the screen needs around that:

- `trial_places(shown, chosen, graph, lineage)`: where the tried step is written, or why it cannot be tried (the rule of places, the metadata, "Show your selection first").
- `fit_problem(rows, places, lineage, columns_at)`: the condition must fit EVERY place (the column is there with the same type); a place where it does not is named and nothing is tried (never dropped
  silently).
- `tried_nodes(rows, places, primary_keys)`: the nodes handed to the engine: one decision for each staged row, written at each place with the id of the decision.
- `tried_drop_nodes(columns, places)`, `drop_fit_problem(...)`, `drop_condition_lines(columns)`: a column drop is tried like a condition (FLOW-3: the one way to create a step; the drop of the column
  chooser has no pop-up and no staging any more). `TrialRecord.kind` says which: "filter" or "drop".
- `world_of(...)` and `end_cause(then, now)`: what a trial was made for, and the first thing that changed since (the condition, the places chosen, the mode, the recipe or data, the applied steps, a restored
  session): the trial then ends with ONE plain notice.
- `panel_model(...)`: the lines of the trial panel (rows removed at each place; what the places reach, as information, never ticks).
- the words of the three states and of Compare beside a trial (`compare_left_label`, `compare_right_label`, `band_trial_line`).

PROVISIONAL (the builder's words and choices; the owner reads them): every sentence below; the button labels "Try" and "Discard"; that a trial is written at the places chosen only when the place shown is
among them (else the refusal "Show your selection first" of slice 3a); that with nothing chosen the place is the one shown (the open plot's Result data (T3) when nothing was shown); the order of the causes of
`end_cause` (the first that applies is told).

Consumed by: app/handlers/trial_handlers.py, app/handlers/home_theater.py, app/tests/test_audit_try.py. If deleted: HOME's Audit mode has no Try.

# @deps
# provides: class:TrialRecord, function:condition_lines, function:stage_sentence, function:tried_drop_nodes, function:drop_fit_problem, function:drop_condition_lines, function:drops_from_selection, constant:KIND_FILTER, constant:KIND_DROP, function:trial_places, function:fit_problem, function:tried_nodes, function:world_of, function:end_cause, function:panel_model, function:rows_signature, function:compare_left_label, function:compare_right_label, function:band_trial_line, function:trial_has_state, class:TrialWorld, class:PanelModel, constant:TRY_LABEL, constant:DISCARD_LABEL
# consumes: app/modules/audit_shown.py (selection_problem, request_to_show), app/modules/audit_place_view.py (condition_fits, STATE_WORDS, TRIAL), app/modules/audit_trial.py (TrialResult: duck-typed, not imported), app/modules/session_manager.py (make_audit_step), app/modules/audit_places.py (PLACES_BUCKET), app/modules/t3_audit_engine.py (audit_params_from_row, describe_filter), libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/lineage_data.py
# consumed_by: app/handlers/trial_handlers.py, app/handlers/home_theater.py, app/tests/test_audit_try.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0650, D-0656, D-0662, D-0669, D-0671)
# @end_deps
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from app.modules.audit_place_view import STATE_WORDS, TRIAL, condition_fits
from app.modules.audit_shown import request_to_show, selection_problem
from app.modules.audit_places import PLACES_BUCKET
from app.modules.t3_audit_engine import audit_params_from_row, describe_filter
from utils.lineage_data import Lineage
from utils.recipe_graph import RecipeGraph

KIND_FILTER = "filter"
KIND_DROP = "drop"
TRY_LABEL = "Try"                     # PROVISIONAL
DISCARD_LABEL = "Discard"             # PROVISIONAL
NOT_CHANGED = "The step you are trying does not change this."                              # PROVISIONAL
NO_CONDITION = "Build a condition first: add a row in the Filters panel, then press Try."  # PROVISIONAL
NOTHING_SHOWN = "Show an item first: the step is tried at the place shown. Nothing was tried."   # PROVISIONAL
TRIAL_WORDS = STATE_WORDS[TRIAL]
COUNTING = "Counting the rows each place loses..."                                         # PROVISIONAL (D-0650)


def trial_places(shown_place: Optional[str], chosen: Sequence[str], graph: RecipeGraph, lineage: Lineage) -> Tuple[Tuple[str, ...], str]:
    """(the places the tried step is written at, "") or ((), one plain sentence).

    With nothing chosen the place is the one shown. With places chosen the place shown must be among them (else "Show your selection first", slice 3a: the condition was built on the table shown);
    the places are then ALL the places chosen, in the order chosen (D-0669). Every place must be a place a step can be written at (the metadata is not, a table with no tier 2 has no tier 2, a node that
    cannot be chosen is not) and at most one place may lie on a path (D-0553). A place that fails is a plain sentence and nothing is tried."""
    picks = tuple(dict.fromkeys(c for c in chosen if c))
    if not shown_place and not picks:
        return (), NOTHING_SHOWN
    problem = selection_problem(picks, shown_place)
    if problem:
        return (), problem
    places = picks or (shown_place,)
    for place in places:
        outcome = request_to_show(place, [], graph, lineage)
        if outcome.place is None:
            return (), f"{outcome.problem} Nothing was tried."
    problem = graph.chosen_places_problem(places)
    if problem:
        return (), f"{problem} Nothing was tried."
    return tuple(places), ""


def fit_problem(rows: Sequence[dict], places: Sequence[str], lineage: Lineage, columns_at: Callable[[str], Optional[Sequence[Tuple[str, Any]]]],
                name_of: Callable[[str], str]) -> str:
    """"" when every staged row fits every place, else ONE plain sentence that names each place where a condition does not fit and why (the column is not there, or has another type).

    `columns_at(place)` gives the names and types of the table present at that place in the state the step will meet (the audited table), or None to let the lineage's plan decide
    (`audit_place_view.condition_fits`). A place is never dropped silently: one that does not fit stops the trial."""
    bad: List[str] = []
    for place in places:
        columns = columns_at(place)
        for row in rows:
            ok, why = condition_fits(place, row.get("column", ""), row.get("dtype", ""), lineage, columns)
            if not ok:
                bad.append(f"{name_of(place)}: {why}")
                break
    if not bad:
        return ""
    return "The condition does not fit every place chosen. " + " ".join(bad) + " Nothing was tried. Choose places where the column is, or build the condition on another table."


def _decisions(scratch_nodes: Sequence[dict], places: Sequence[str], started_from: str) -> List[dict]:
    """One node for each (decision, place), in the order: the first decision at every place, then the second, and so on; the nodes of one decision share its id; no reason (the engine gives a
    placeholder inside the trial only)."""
    from app.modules.session_manager import make_audit_step
    out: List[dict] = []
    for scratch in scratch_nodes:
        for place in places:
            out.append(make_audit_step(scratch["node_type"], dict(scratch.get("params", {})), plot_scope=PLACES_BUCKET, reason="",
                                       primary_key_warning=bool(scratch.get("primary_key_warning")), node_id=scratch["id"], place=place, started_from=started_from))
    return out


def tried_nodes(rows: Sequence[dict], places: Sequence[str], primary_keys: Iterable[str] = (), started_from: str = "") -> List[dict]:
    """The nodes handed to the engine: one decision (one id) for each staged row, written at each place, in the order: the first row at every place, then the second row, and so on.

    A trial and the step it stands for are the same step: these are the nodes "Add to audit pipeline" writes. No reason (the engine gives a placeholder inside the trial only); nothing is written to
    the state."""
    from app.modules.session_manager import make_audit_step
    keys = set(primary_keys)
    scratch = [make_audit_step("filter_row", audit_params_from_row(row), plot_scope=PLACES_BUCKET, reason="", primary_key_warning=row.get("column", "") in keys) for row in rows]
    return _decisions(scratch, places, started_from)


def tried_drop_nodes(columns: Sequence[str], places: Sequence[str], started_from: str = "") -> List[dict]:
    """The nodes of a column drop: one decision (one id) for each column, written at each place, the first column at every place, then the second, and so on (the same order as `tried_nodes`)."""
    from app.modules.session_manager import make_audit_step
    scratch = [make_audit_step("drop_column", {"column": c}, plot_scope=PLACES_BUCKET, reason="") for c in dict.fromkeys(columns)]
    return _decisions(scratch, places, started_from)


def drops_from_selection(columns: Sequence[str], selected: Any) -> List[str]:
    """The columns of the table shown that the column chooser has NOT selected, in the table's order: the columns to drop. `selected` is what the chooser reports; anything but a list or a tuple
    means no chooser is on the page (nothing is deselected)."""
    if not isinstance(selected, (list, tuple)):
        return []
    keep = set(selected)
    return [c for c in columns if c not in keep]


def drop_condition_lines(columns: Sequence[str]) -> Tuple[str, ...]:
    """The drop in words, one line (the rows are not changed by a drop; said, never silent). PROVISIONAL words."""
    names = ", ".join(columns)
    return (f"Drop {'the column' if len(columns) == 1 else 'the columns'}: {names}. No row is removed.",)


def drop_fit_problem(columns: Sequence[str], places: Sequence[str], lineage: Lineage, columns_at: Callable[[str], Optional[Sequence[Tuple[str, Any]]]],
                     name_of: Callable[[str], str]) -> str:
    """"" when every column to drop is in the table at every place, else ONE plain sentence that names each place and the columns that are not there. A drop does not need the same type at a
    place (a column is dropped whatever it holds); it needs the column. `columns_at(place)` is the names and types of the table present at that place in the audited state (None: the lineage's
    plan decides). A place is never dropped silently."""
    bad: List[str] = []
    for place in places:
        found = columns_at(place)
        if found is None:
            try:
                found = lineage.node(place).columns
            except KeyError:
                found = None
        if found is None:
            bad.append(f"{name_of(place)}: its columns are not known, so the drop cannot be checked there.")
            continue
        names = {str(name) for name, _ in found}
        missing = [c for c in columns if c not in names]
        if missing:
            bad.append(f"{name_of(place)}: {', '.join(missing)} {'is' if len(missing) == 1 else 'are'} not in the table there.")
    if not bad:
        return ""
    return "The drop does not fit every place. " + " ".join(bad) + " Nothing was tried. Choose places where the columns are, or deselect other columns."


def rows_signature(rows: Iterable[dict]) -> Tuple[str, ...]:
    """What the staged rows are, as the step they would make (column, operator, value, `na`, `closed`, type): a change of any of them is another condition."""
    return tuple(json.dumps(audit_params_from_row(r), sort_keys=True, default=str) for r in rows)


@dataclass(frozen=True)
class TrialWorld:
    """What a trial was made for. Two worlds that differ in any field are not the same trial."""
    mode: str                    # "audit" (a trial exists in Audit mode only)
    recipe: str
    keys: Tuple[str, ...]        # (recipe hash, data hash)
    rows: Tuple[str, ...]        # `rows_signature` of the staged rows
    chosen: Tuple[str, ...]      # the places chosen in the lineage, in the order chosen
    applied: tuple               # `audit_places.nodes_signature` of the applied steps
    session: str                 # the saved file of a restored session (a restore writes it), "" when none


def world_of(mode: str, recipe: str, keys: Sequence[str], rows: Iterable[dict], chosen: Sequence[str], applied: tuple, session: str = "") -> TrialWorld:
    return TrialWorld(mode, recipe or "", tuple(keys), rows_signature(rows), tuple(dict.fromkeys(c for c in chosen if c)), tuple(applied), session or "")


@dataclass(frozen=True)
class TrialRecord:
    """A trial that exists: the world it was made for, the places the step was tried at, the nodes tried, the engine's answer (`audit_trial.TrialResult`) and the condition in words. HOME keeps one
    (or none) in a reactive value; nothing of it is stored in the session, the export or the audit folder."""
    world: TrialWorld
    places: Tuple[str, ...]
    nodes: Tuple[dict, ...]
    result: Any
    condition: Tuple[str, ...]
    serial: int = 0              # the number of this Try (the ids of the marks and of the reason of its panel carry it: a new trial never inherits a stale value of an older one)
    kind: str = "filter"         # "filter" (a condition of the Filters panel) or "drop" (the columns the chooser did not select): the panel's words and the end causes differ


def stage_sentence(params: Dict[str, Any]) -> str:
    """The one line of a condition, with what happens to the rows with no value (never silent)."""
    return describe_filter(params["column"], params["op"], params["value"], params.get("na"))


def condition_lines(rows: Iterable[dict]) -> Tuple[str, ...]:
    """The staged conditions in words, one line each (`stage_sentence`: with what happens to the rows that have no value)."""
    return tuple(stage_sentence(audit_params_from_row(r)) for r in rows)


_END = "The trial ended: it was not applied, not saved and not exported."


def end_cause(then: TrialWorld, now: TrialWorld) -> Optional[str]:
    """None when nothing a trial depends on has changed, else ONE plain sentence for the first thing that did (the order: mode, recipe, data, restored session, applied steps, places chosen, condition).
    PROVISIONAL words."""
    if then.mode != now.mode:
        return f"You left Audit mode. {_END}"
    if then.recipe != now.recipe:
        return f"You opened another recipe. {_END}"
    if then.keys != now.keys:
        return f"The recipe or its data changed. {_END}"
    if then.session != now.session:
        return f"A session was restored. {_END}"
    if then.applied != now.applied:
        return f"An audit step was applied or removed. {_END}"
    if then.chosen != now.chosen:
        return f"The places chosen changed. {_END}"
    if then.rows != now.rows:
        return f"The condition changed. {_END}"
    return None


def _count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


@dataclass(frozen=True)
class PanelModel:
    """The trial panel as plain data: `heading` (the three-state words), `condition` (the condition in words), `effects` (one line for each place: the rows the step removes there), `reach_summary`
    and `reach_items` (what the places reach, as information: each built-from item with "table changed" or "no row changed"), `error` (the step cannot run: the only thing shown then besides the heading)."""
    heading: str
    condition: Tuple[str, ...]
    effects: Tuple[str, ...]
    reach_summary: str
    reach_items: Tuple[str, ...]
    error: str = ""
    effect_nodes: Tuple[str, ...] = ()      # the node of each line of `effects` (the panel offers "Show" beside it)
    reach_nodes: Tuple[str, ...] = ()       # the node of each item of `reach_items`


def _rows_words(removed: int, before: int) -> str:
    if removed == 0:
        return f"removes no row (of {before})"
    return f"removes {_count(removed, 'row', 'rows')} of {before}"


def _columns_words(removed: int, before: int) -> str:
    if removed == 0:
        return f"drops no column (of {before})"
    return f"drops {_count(removed, 'column', 'columns')} of {before}"


def panel_model(result: Any, condition_lines: Sequence[str], name_of: Callable[[str], str], kind: str = KIND_FILTER) -> PanelModel:
    """The panel of a trial from the engine's `TrialResult` (duck-typed: `effects`, `reaches`, `error`). `condition_lines`: the staged conditions in words (`utils.filter_words`); `name_of(node id)`: the
    name of a place as the lineage panel writes it.

    Zero rows removed at a place is said plainly, as information (D-0501: it is the signal of a wrong place; the app does not judge). What the places reach is a count and a list with the state
    of each (`table changed`, `no row changed`): information, never ticks (D-0662)."""
    if result.error:
        return PanelModel(TRIAL_WORDS, tuple(condition_lines), (), "", (), error=f"This step cannot be tried: {result.error}")
    if kind == KIND_DROP:
        effects = tuple(f"{name_of(e.place)}: the step {_columns_words(e.columns_removed, e.columns_before)} here ({e.state})." for e in result.effects)
    else:
        effects = tuple(f"{name_of(e.place)}: the step {_rows_words(e.rows_removed, e.rows_before)} here ({e.state})." for e in result.effects)
    reaches = list(result.reaches)
    tables = [r for r in reaches if r.kind == "table"]
    plots = [r for r in reaches if r.kind == "plot"]
    if reaches:
        summary = f"What these places reach: {_count(len(tables), 'table', 'tables')} and {_count(len(plots), 'plot', 'plots')} are built from them (information, not chosen)."
    else:
        summary = "No table or plot is built from these places."
    items = tuple(f"{name_of(r.node)}: {r.state}" for r in reaches)
    return PanelModel(TRIAL_WORDS, tuple(condition_lines), effects, summary, items, effect_nodes=tuple(e.place for e in result.effects), reach_nodes=tuple(r.node for r in reaches))


def compare_left_label(has_earlier_steps: bool, show_original: bool) -> str:
    """The label of the left pane of Compare beside a trial (D-0671): "before this step" (the audited state as it is now), or the original when the switch says so. With no earlier applied step the two
    are the same, and the label says so. PROVISIONAL words."""
    if show_original:
        return "Original (as read)"
    if has_earlier_steps:
        return "Before this step: your applied steps"
    return "Before this step: no earlier step, so the same as the original"


def compare_right_label() -> str:
    """The label of the right pane of Compare beside a trial: the trial."""
    return TRIAL_WORDS


def trial_has_state(record: Optional[TrialRecord]) -> bool:
    """True when a trial exists AND the step could be run: only then does an item have a trial state ("trial", "not changed"). A trial whose step cannot run (`result.error`) has no state on any item:
    the panel carries the error and the band and the plot label say nothing about a trial."""
    return record is not None and not getattr(record.result, "error", None)


def band_trial_line(state: str, trial_exists: bool) -> str:
    """The extra line of the band above the preview while a trial exists and the item shown is NOT the trial's table (the step does not change it): "" otherwise. When the item IS the trial the band
    already says it in the words of the state (`STATE_WORDS`)."""
    if trial_exists and state != TRIAL:
        return NOT_CHANGED
    return ""
