"""The drop of a key column is refused BY PLACE, in one rule (LBFB step 4; D-0358 modulates D-0297).

Eve, 2026-11-20 (D-0358): "it should be refused by place because eg. we can have aggregations by count in a plot where the key does not matter ... it will depends where - so its
a modulation of ealier decisions - worth case if a user removes the wrong column then the dependent steps wont work and there will be error / no plot". Before, `join_keys`
refused a column by its NAME for the whole recipe (every column that any join reads as a key, at every place). Now a drop of column `c` at place `p` (the end of the node `p`:
`T1:<table>`, `T2:<table>` or `T3:<plot>`) is refused when a join step later, in a table built from `p`, reads that column as a key, the column being followed forward by the
links of the lineage walk (a rename, a key under another name and the suffix of a clash included, never the name alone: `LineageIndex.drop_facts`). Where no later join reads
it (a plot's own steps: nothing is built from a plot), the drop is allowed; if a later step needs the column all the same, that step fails at the build and the user is told
before confirming (the consequences of a drop, in the walk).

ONE rule: `audit_copy.add_step`, `audit_copy.integrity_errors`, the checker (AU04) and HOME's audit code ask this module; the walk of a drop asks the same `drop_facts`. The
rule needs the lineage of the columns: a caller that has the engine passes the engine's plan book of THE ORIGINAL recipe as `plans` (`app/modules/plan_composer.py`,
LBFB step 0b: what the audit run, the engine's own check of a copy, the session restore and HOME's column box do). The plan is the plan of the recipe WITHOUT its audit steps (an audit
step never changes which join reads which column; a plan composed with audit steps differs below them). A caller without the engine gets the lineage from the recipe alone
(`declared_plans.declared_plan_book`: names only): then a place behind a step the walk does not read (an unpivot, a fill of missing values, an explode: five places of the shipped
recipes, the review of 2026-11-20, finding F2) cannot be followed.

A drop the walk cannot follow to the end (`DropFacts.uncertain`: a step it does not read, a plan failure, a join it reaches only by an uncertain link) is NOT written: the line is red and
cannot be ticked, and every path that shares this gate refuses it with ONE plain sentence (D-0460: "B of needed we try to.fimd a.solutiom later"; it replaces D-0449, which allowed
such a drop with a warning, and the review of 2026-11-21 shows why that was not kept: the owner wants no step written at a place the app cannot follow, D-0450: "do not get wrong
results because we did not select the correct scope"). The user chooses another place; a place becomes tickable when its step kind is followed. The sentence says which column, at
which place, the step where the app loses it and why, what the walk can still read downstream (a step that names the column, a plot that draws it, a same-named column of a join
that a plot would read under the same name: `LineageIndex.drop_consequences`), that the app cannot YET follow it (the capital YET is decided for the join, D-0454), and "Suggestion:" with what can be done IN FACT, from the places after it that the walk knows
(`DropGate.ways_out`: a place where the column still exists, is followed and would build; or that no such place exists and why; never a fixed phrase). It promises nothing about the build. The WHOLE sentence is PROVISIONAL (the builder's wording; the owner reads it, D-0297: plain words). What the engine does with such a
drop if it were written is proved in `app/tests/test_uncertain_drop_engine.py` (the table meant, a plain error, or a different table).

A declared entity key (`is_entity_key`) is not refused for being declared: it is dropped by place like any key, refused only where a later join reads it (D-0448, "Her answer: B"; D-0297
names join keys, D-0358 says by place); the facts carry it as information.

Pure: a recipe dictionary in, facts or a sentence out. No file, no data, no engine.

Consumed by: libs/utils/src/utils/audit_copy.py, libs/utils/src/utils/recipe_check.py, app/modules/session_manager.py (restore), app/handlers/filter_and_audit_handlers.py (HOME's drop).
If deleted: no caller can refuse the drop of a key column by place.

# @deps
# provides: function:DropGate.ways_out, function:key_drop_problem, function:drop_facts, function:key_drop_sentence, function:key_drop_unfollowed_sentence, function:place_of_steps_path, class:DropGate
# consumes: libs/utils/src/utils/lineage_walk.py (LineageIndex.drop_facts), libs/utils/src/utils/declared_plans.py, libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/recipe_tiers.py (without_audit_steps)
# consumed_by: libs/utils/src/utils/audit_copy.py, libs/utils/src/utils/recipe_check.py, app/modules/session_manager.py, app/handlers/filter_and_audit_handlers.py, libs/utils/tests/test_key_drop.py
# doc: .claude/knowledge/decision_ledger.md (D-0358, D-0297, D-0322, D-0448, D-0460, D-0454, D-0450), .claude/design/home_audit_steps.md
# @end_deps
"""
from __future__ import annotations

from typing import Any, List, NamedTuple, Optional, Sequence, Tuple

from utils import recipe_tiers
from utils.declared_plans import declared_plan_book
from utils.lineage_records import (
    CLASH_NO_LONGER, Consequence, DropFacts, KeyNeed, PLAN_FAILED, PLOT_USES_COLUMN, STEP_NOT_READ, STEP_NAMES_COLUMN)
from utils.lineage_walk import LineageIndex
from utils.plan_book import PlanBook
from utils.recipe_graph import RecipeGraph, RecipeGraphError, build_graph


class WaysOut(NamedTuple):
    """The places where a refused drop could be written instead (`places`, node ids in the order of the lineage), whether the column is known to be gone from every later table
    (`known_absent`) and whether some later plan is unknown (`unknown`)."""
    places: Tuple[str, ...]
    known_absent: bool
    unknown: bool


class DropGate:
    """The rule for one recipe: the graph and the lineage links are built once, then any number of drops are asked. The recipe is read without its audit steps (the rule
    is about the recipe the author wrote: an audit step never changes which join reads which column). `plans`: the engine's plan book of that recipe, when the caller has it;
    else the plan the recipe declares (names only)."""

    def __init__(self, raw: Any, plans: Optional[PlanBook] = None) -> None:
        self.graph: Optional[RecipeGraph] = None
        self.error: Optional[str] = None
        self._index: Optional[LineageIndex] = None
        self._plot_targets = recipe_tiers.plot_targets(raw) if isinstance(raw, dict) else set()
        try:
            self.graph = build_graph(recipe_tiers.without_audit_steps(raw) if isinstance(raw, dict) else raw)
        except (RecipeGraphError, KeyError, TypeError, AttributeError) as error:
            self.error = str(error)
            return
        self._index = LineageIndex(self.graph, plans if plans is not None else declared_plan_book(self.graph))

    def place_of_steps_path(self, steps_path: str) -> Optional[str]:
        """The place (node id) whose step list is written at `steps_path` (for example `data_schemas.A.tier1.steps`), or None: the checker knows paths, the rule knows places."""
        if self.graph is None:
            return None
        return next((nid for nid in self.graph.nodes() if self.graph.node(nid).steps_path == steps_path), None)

    def has_place(self, place: str) -> bool:
        return self.graph is not None and self.graph.has_node(place)

    def facts(self, place: str, column: str) -> Optional[DropFacts]:
        """The facts of dropping `column` at the end of `place`; None when the recipe cannot be drawn or has no such place (nothing is judged then)."""
        if self._index is None or not self.has_place(place):
            return None
        return self._index.drop_facts(place, column)

    def problem(self, place: str, columns: Any) -> Optional[str]:
        """None, or the plain sentence that says why the audit may not drop these columns at this place: a join step later reads one as a key (`key_drop_sentence`), or the walk cannot
        follow one to the end (`key_drop_unfollowed_sentence`, D-0460: the drop is not written; PROVISIONAL wording). A certain need is said first and alone. `columns` is the list of
        a `polars_drop` step; anything that is not a list of names is not judged here (the checker reports it)."""
        if not isinstance(columns, list):
            return None
        every = [f for f in (self.facts(place, c) for c in columns if isinstance(c, str)) if f is not None]
        found = [f for f in every if f.refused]
        if found:
            return key_drop_sentence(found)
        unsure = [(f, self._index.drop_consequences(place, f.column) if self._index is not None else [], self.ways_out(place, f.column)) for f in every if f.uncertain]
        return key_drop_unfollowed_sentence(unsure) if unsure else None

    def ways_out(self, place: str, column: str) -> WaysOut:
        """Where else a drop of this column can be written and followed, from facts the walk has: the places built from `place` where the column still exists (the plan, by the
        links of the walk), where the gate would accept the drop (not refused, not uncertain), where the app writes a step (the tier 2 of a table no plot reads is not one) and where
        no later step that the walk reads names the column and no plot draws it (such a drop would fail at the build). `known_absent`: the plan is known at every later place and
        none holds the column (a step melted or removed it). `unknown`: a later plan is missing (a step the app cannot read)."""
        if self._index is None or self.graph is None:
            return WaysOut((), False, True)
        states = self._index.later_places(place, column)
        places: List[str] = []
        for nid, state in states:
            node = self.graph.node(nid)
            if state != "present" or (node.kind == "T2" and node.name not in self._plot_targets):
                continue
            there = self._index.drop_facts(nid, column)
            if there.refused or there.uncertain:
                continue
            if any(c.code in (STEP_NAMES_COLUMN, PLOT_USES_COLUMN) for c in self._index.drop_consequences(nid, column)):
                continue
            places.append(nid)
        return WaysOut(tuple(places), bool(states) and all(state == "absent" for _, state in states), any(state == "unknown" for _, state in states))


def drop_facts(raw: Any, place: str, column: str, plans: Optional[PlanBook] = None) -> Optional[DropFacts]:
    """The facts of dropping `column` at the end of the node `place` (None when the recipe cannot be drawn or has no such place)."""
    return DropGate(raw, plans).facts(place, column)


def key_drop_problem(raw: Any, place: str, columns: Any, plans: Optional[PlanBook] = None) -> Optional[str]:
    """None, or the plain sentence that says why a drop of these columns at `place` is refused: a join step later reads one of them as a key (D-0358, D-0297: "dropping a
    column that is a join key through the audit is refused, and the app says why in plain words", by place)."""
    return DropGate(raw, plans).problem(place, columns)


def _where(need: KeyNeed) -> str:
    name = f" (it is called {need.name!r} there)" if need.name else ""
    return f"step {need.step.step} of {need.step.node}{name}"


def key_drop_sentence(found: Sequence[DropFacts]) -> str:
    """The plain sentence for the refused drops: the column, the place, which join step needs it and what to do instead. PROVISIONAL wording (D-0297: plain words; the owner reads it)."""
    parts: List[str] = []
    for facts in found:
        joins = ", ".join(_where(n) for n in facts.needs if n.certain)
        parts.append(f"the column {facts.column!r} at {facts.place}: it is read as a join key by {joins}")
    return ("Cannot drop " + "; ".join(parts) + ". A join needs its key column, so a key column cannot be dropped before that join through the audit. "
            "Use a row filter or a removal by key instead, or drop the column after the join (a plot's own steps are after every join).")


_ENGINE_PLAN_MARKERS = ("Resolved plan until failure", "Error originated just after this operation", "This error occurred with the following context")


def _why_not_followed(facts: DropFacts) -> str:
    parts: List[str] = []
    for reason in facts.unfollowed:
        if reason.code == PLAN_FAILED:
            said = str(reason.get("sentence", ""))
            for marker in _ENGINE_PLAN_MARKERS:                          # the engine's own sentence, never its plan dump
                said = said.split(marker, 1)[0]
            said = " ".join(said.split()).rstrip(".")
            parts.append(f"the app could not work out the columns of {reason.get('node', facts.place)}" + (f": {said}" if said else ""))
        elif reason.code == STEP_NOT_READ:
            parts.append(f"it reaches step {reason.get('step', '?')} of {reason.get('node', '?')} ({reason.get('action', 'an unknown action')}), a step the app cannot read")
        else:
            parts.append(f"the app could not follow it ({reason.code})")
    parts += [f"step {n.step.step} of {n.step.node} may read it as a join key" for n in facts.needs if not n.certain]
    return "; ".join(dict.fromkeys(parts)) or "the app could not follow it"


def _consequence_sentence(found: Consequence) -> str:
    """One thing the walk reads downstream of the column, in plain words and without a promise (PROVISIONAL wording): a step that names it, a plot that draws it, a same-named column of a join."""
    name = found.get("name")
    if found.code == STEP_NAMES_COLUMN:
        return f"step {found.step.step} of {found.step.node} ({found.step.action}) names {name!r}"
    if found.code == PLOT_USES_COLUMN:
        return f"the plot {found.get('plot')!r} draws {name!r}"
    if found.code == CLASH_NO_LONGER:
        return (f"in step {found.step.step} of {found.step.node} the column {name!r} of the table {found.get('table')} is called {found.get('was_called')!r} because this column is there; "
                f"after the drop it is called {name!r}, so a plot or a step that reads {name!r} after that step would read the column of the table {found.get('table')} under the name {name!r}")
    return f"the app reads this downstream: {found.code}"


def _way_out_sentence(column: str, ways: WaysOut) -> str:
    """What can be done about one column, only from facts the walk has (D-0460, PROVISIONAL wording): a place where the column still exists and the app can follow it, or the plain
    fact that there is none and why. Nothing is offered that the app would refuse or that would fail at the build."""
    if ways.places:
        shown = ", ".join(ways.places[:3])
        return f"for {column!r} write the drop at a place where the column still exists and the app can follow it, for example {shown}"
    if ways.known_absent:
        return (f"for {column!r}: after that step it is no longer a column of any table, so a drop is only possible before it, and there the app cannot YET follow it; "
                "no drop of this column can be written for now")
    return f"for {column!r}: the app cannot tell where else this column could be dropped, so no drop of it can be written for now"


def key_drop_unfollowed_sentence(found: Sequence[Tuple[DropFacts, Sequence[Consequence], WaysOut]]) -> str:
    """Two short sentences for a drop the app cannot follow to the end (D-0460: the drop is not written; the line is red and cannot be ticked): the column and the place, the step where
    the app loses it and why, what the walk reads downstream, that the app cannot YET follow it (the capital word, D-0454); then "Suggestion:" and what can be done IN FACT, built from
    what the walk knows of the places after it (`DropGate.ways_out`), never a fixed phrase. No promise about the build. PROVISIONAL: the whole wording is the builder's; the owner reads it."""
    details: List[str] = []
    for facts, consequences, _ in found:
        text = f"{facts.column!r}: {_why_not_followed(facts)}"
        read = list(dict.fromkeys(_consequence_sentence(c) for c in consequences))
        details.append(text + ("; " + "; ".join(read) if read else ""))
    named = " and ".join(f"the column {f.column!r} at {f.place}" for f, _, _ in found)
    advice = "; ".join(_way_out_sentence(f.column, ways) for f, _, ways in found)
    return f"The app cannot YET follow {named} to the end ({'; '.join(details)}), so the drop is not written. Suggestion: {advice}."


def place_of_steps_path(raw: Any, steps_path: str) -> Optional[str]:
    """`DropGate.place_of_steps_path` for one call."""
    return DropGate(raw).place_of_steps_path(steps_path)
