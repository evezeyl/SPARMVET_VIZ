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

PROVISIONAL (the builder's, not decided by the owner; it replaces the earlier P16 "allow when the walk cannot follow"): where the walk cannot follow the column to the end
(`DropFacts.uncertain`: a step it does not read, a plan failure, a join it reaches only by an uncertain link) the drop is NOT written and the sentence says so and why, in plain words:
no silent allow ("The software informs the user and does not choose for the user": the user is told the app could not follow the column, and what to do). The safe side is the one
that writes nothing. The wording of both sentences is the builder's: the first keeps the meaning of the sentence of D-0297 and adds which join needs the column.

A declared entity key (`is_entity_key`) is not refused for being declared (D-0297 names join keys, D-0358 says by place); the facts carry it as information.

Pure: a recipe dictionary in, facts or a sentence out. No file, no data, no engine.

Consumed by: libs/utils/src/utils/audit_copy.py, libs/utils/src/utils/recipe_check.py, app/modules/session_manager.py (restore), app/handlers/filter_and_audit_handlers.py (HOME's drop).
If deleted: no caller can refuse the drop of a key column by place.

# @deps
# provides: function:key_drop_problem, function:drop_facts, function:key_drop_sentence, function:key_drop_unfollowed_sentence, function:place_of_steps_path, class:DropGate
# consumes: libs/utils/src/utils/lineage_walk.py (LineageIndex.drop_facts), libs/utils/src/utils/declared_plans.py, libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/recipe_tiers.py (without_audit_steps)
# consumed_by: libs/utils/src/utils/audit_copy.py, libs/utils/src/utils/recipe_check.py, app/modules/session_manager.py, app/handlers/filter_and_audit_handlers.py, libs/utils/tests/test_key_drop.py
# doc: .claude/knowledge/decision_ledger.md (D-0358, D-0297, D-0322), .claude/design/home_audit_steps.md
# @end_deps
"""
from __future__ import annotations

from typing import Any, List, Optional, Sequence

from utils import recipe_tiers
from utils.declared_plans import declared_plan_book
from utils.lineage_records import DropFacts, KeyNeed, PLAN_FAILED, STEP_NOT_READ
from utils.lineage_walk import LineageIndex
from utils.plan_book import PlanBook
from utils.recipe_graph import RecipeGraph, RecipeGraphError, build_graph


class DropGate:
    """The rule for one recipe: the graph and the lineage links are built once, then any number of drops are asked. The recipe is read without its audit steps (the rule
    is about the recipe the author wrote: an audit step never changes which join reads which column). `plans`: the engine's plan book of that recipe, when the caller has it;
    else the plan the recipe declares (names only)."""

    def __init__(self, raw: Any, plans: Optional[PlanBook] = None) -> None:
        self.graph: Optional[RecipeGraph] = None
        self.error: Optional[str] = None
        self._index: Optional[LineageIndex] = None
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
        """None, or the plain sentence that says why the audit may not drop these columns at this place: a join step later reads one as a key (`key_drop_sentence`), or the
        walk cannot follow one to the end (`key_drop_unfollowed_sentence`, PROVISIONAL: not written). `columns` is the list of a `polars_drop` step; anything that is not a list of
        names is not judged here (the checker reports it)."""
        if not isinstance(columns, list):
            return None
        every = [f for f in (self.facts(place, c) for c in columns if isinstance(c, str)) if f is not None]
        found = [f for f in every if f.refused]
        if found:
            return key_drop_sentence(found)
        unsure = [f for f in every if f.uncertain]
        return key_drop_unfollowed_sentence(unsure) if unsure else None


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


def _why_not_followed(facts: DropFacts) -> str:
    parts: List[str] = []
    for reason in facts.unfollowed:
        if reason.code == PLAN_FAILED:
            said = str(reason.get("sentence", "")).strip()
            parts.append(f"the engine could not give the columns of {reason.get('node', facts.place)}" + (f" ({said})" if said else ""))
        elif reason.code == STEP_NOT_READ:
            parts.append(f"step {reason.get('step', '?')} of {reason.get('node', '?')} ({reason.get('action', 'an unknown action')}) is a step the app cannot follow")
        else:
            parts.append(f"the app could not follow it ({reason.code})")
    parts += [f"step {n.step.step} of {n.step.node} may read it as a join key" for n in facts.needs if not n.certain]
    return "; ".join(dict.fromkeys(parts)) or "the app could not follow it"


def key_drop_unfollowed_sentence(found: Sequence[DropFacts]) -> str:
    """The plain sentence for a drop the app cannot follow to the end: the column, the place, why, and that nothing is written. PROVISIONAL wording (the owner reads it): the
    safe side, no silent allow."""
    parts = [f"the column {f.column!r} at {f.place}: {_why_not_followed(f)}" for f in found]
    return ("Cannot tell whether a join later needs " + "; ".join(parts) + ". The drop is not written, because it may remove a key that a join reads. "
            "Suggestion: use a row filter or a removal by key instead, or drop the column in a plot's own steps (after every join).")


def place_of_steps_path(raw: Any, steps_path: str) -> Optional[str]:
    """`DropGate.place_of_steps_path` for one call."""
    return DropGate(raw).place_of_steps_path(steps_path)
