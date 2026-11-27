"""TRYING an audit step on screen: the pure rules of the new Audit flow, FLOW-1 (no Shiny, no file, no engine; the screen is `app/handlers/trial_handlers.py`).

The model (ledger D-0656, D-0662, D-0669, D-0671; `.claude/design/home_audit_what_is_true_now.md`): in Audit mode the user builds a condition in the Filters panel on the table shown and
presses Try. The step is written at the place shown, plus the other places chosen in "Path of the data" when the place shown is among them (D-0669: all the places chosen). The engine
(`app/modules/audit_trial.py`, `PlaceTrial`) computes the effect: nothing is applied, saved or exported. This module decides what the screen needs around that:

- `trial_places(shown, chosen, graph, lineage)`: where the tried step is written, or why it cannot be tried (the rule of places, the metadata, "Show your selection first").
- `fit_problem(rows, places, lineage, columns_at)`: the condition must fit EVERY place (the column is there with the same type); a place where it does not is named and nothing is tried (never dropped
  silently).
- `tried_nodes(rows, places, primary_keys)`: the nodes handed to the engine: one decision for each staged row, written at each place with the id of the decision (the nodes of the dialog "Send to Audit").
- `world_of(...)` and `end_cause(then, now)`: what a trial was made for, and the first thing that changed since (the condition, the places chosen, the mode, the recipe or data, the applied steps, a restored
  session): the trial then ends with ONE plain notice.
- `panel_model(...)`: the lines of the trial panel (rows removed at each place; what the places reach, as information, never ticks).
- the words of the three states and of Compare beside a trial (`compare_left_label`, `compare_right_label`, `band_trial_line`).

PROVISIONAL (the builder's words and choices; the owner reads them): every sentence below; the button labels "Try" and "Discard"; that a trial is written at the places chosen only when the place shown is
among them (else the refusal "Show your selection first" of slice 3a); that with nothing chosen the place is the one shown (the open plot's Result data (T3) when nothing was shown); the order of the causes of
`end_cause` (the first that applies is told).

Consumed by: app/handlers/trial_handlers.py, app/handlers/home_theater.py, app/tests/test_audit_try.py. If deleted: HOME's Audit mode has no Try.

# @deps
# provides: class:TrialRecord, function:condition_lines, function:trial_places, function:fit_problem, function:tried_nodes, function:world_of, function:end_cause, function:panel_model, function:rows_signature, function:compare_left_label, function:compare_right_label, function:band_trial_line, function:trial_has_state, class:TrialWorld, class:PanelModel, constant:TRY_LABEL, constant:DISCARD_LABEL, constant:APPLY_NOTE
# consumes: app/modules/audit_shown.py (selection_problem, request_to_show), app/modules/audit_place_view.py (condition_fits, STATE_WORDS, TRIAL), app/modules/audit_trial.py (TrialResult: duck-typed, not imported), app/modules/lineage_step.py (stage_nodes), app/modules/lineage_view.py (line_text), app/modules/t3_audit_engine.py (audit_params_from_row), libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/lineage_data.py
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
from app.modules.lineage_step import stage_nodes, stage_sentence
from app.modules.t3_audit_engine import audit_params_from_row
from utils.lineage_data import Lineage
from utils.recipe_graph import RecipeGraph

TRY_LABEL = "Try"                     # PROVISIONAL
DISCARD_LABEL = "Discard"             # PROVISIONAL
APPLY_NOTE = "To apply this step use Send to Audit (the new way to add it comes next)."   # PROVISIONAL
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
        return (), problem.replace("Nothing was sent.", "Nothing was tried.")
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


def tried_nodes(rows: Sequence[dict], places: Sequence[str], primary_keys: Iterable[str] = (), started_from: str = "") -> List[dict]:
    """The nodes handed to the engine: one decision (one id) for each staged row, written at each place, in the order: the first row at every place, then the second row, and so on.

    The same nodes `Send to Audit` would stage (`lineage_step.stage_nodes`, `audit_params_from_row`): a trial and the step it stands for are the same step. No reason (the engine gives a
    placeholder inside the trial only); nothing is written to the state."""
    from app.modules.session_manager import make_audit_step
    keys = set(primary_keys)
    from app.modules.audit_places import PLACES_BUCKET
    placed: List[Tuple[dict, str]] = []
    for row in rows:
        scratch = make_audit_step("filter_row", audit_params_from_row(row), plot_scope=PLACES_BUCKET, reason="", primary_key_warning=row.get("column", "") in keys)
        placed.extend((scratch, place) for place in places)
    return list(stage_nodes({}, placed, started_from)["_pending_t3_nodes"])


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


def condition_lines(rows: Iterable[dict]) -> Tuple[str, ...]:
    """The staged conditions in words, one line each (`lineage_step.stage_sentence`: with what happens to the rows that have no value)."""
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
    apply_note: str = APPLY_NOTE
    effect_nodes: Tuple[str, ...] = ()      # the node of each line of `effects` (the panel offers "Show" beside it)
    reach_nodes: Tuple[str, ...] = ()       # the node of each item of `reach_items`


def _rows_words(removed: int, before: int) -> str:
    if removed == 0:
        return f"removes no row (of {before})"
    return f"removes {_count(removed, 'row', 'rows')} of {before}"


def panel_model(result: Any, condition_lines: Sequence[str], name_of: Callable[[str], str]) -> PanelModel:
    """The panel of a trial from the engine's `TrialResult` (duck-typed: `effects`, `reaches`, `error`). `condition_lines`: the staged conditions in words (`utils.filter_words`); `name_of(node id)`: the
    name of a place as the lineage panel writes it.

    Zero rows removed at a place is said plainly, as information (D-0501: it is the signal of a wrong place; the app does not judge). What the places reach is a count and a list with the state
    of each (`table changed`, `no row changed`): information, never ticks (D-0662)."""
    if result.error:
        return PanelModel(TRIAL_WORDS, tuple(condition_lines), (), "", (), error=f"This step cannot be tried: {result.error}")
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
