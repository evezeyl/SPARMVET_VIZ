"""The plan of every place that the recipe alone can give: names only, no engine (LBFB step 4, D-0358).

The lineage walk (`utils.lineage_walk`) wants the engine's plan of every place. A caller that may not ask the engine (`audit_copy.add_step`, the integrity check, the checker:
they are pure functions of the recipe) still has to decide whether a drop is refused by place. For them this module builds a `PlanBook` from what the recipe says: the declared
`input_fields` of each source table, carried through the steps the walk reads (`step_effects.READINGS`, the same prediction the walk checks against the plan). The TYPES are not
known here: every type is the empty text, so a type is never compared across places. A step the walk does not read is a `PlanFailure` ("the recipe does not say what the step
does to the columns") and so is every place below it, so what lies behind it is never guessed: a caller that gets such a failure says "cannot follow", never "no key needs it".

It is the same function whatever the caller: a caller that HAS the engine's plan passes that plan book to `key_drop` and this module is not used.

Pure: a graph in, a plan book out. No Polars, no file, no engine.

Consumed by: libs/utils/src/utils/key_drop.py, libs/utils/tests/test_declared_plans.py.
If deleted: a drop cannot be judged by place without the engine's plan.

# @deps
# provides: function:declared_plan_book
# consumes: libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/step_effects.py, libs/utils/src/utils/plan_book.py
# consumed_by: libs/utils/src/utils/key_drop.py, libs/utils/tests/test_declared_plans.py
# doc: .claude/knowledge/decision_ledger.md (D-0358, D-0351, D-0325)
# @end_deps
"""
from __future__ import annotations

from typing import Any, Dict, Tuple, Union

from utils import step_effects as fx
from utils.plan_book import Plan, PlanBook, PlanFailure
from utils.recipe_graph import RecipeGraph

UNKNOWN_TYPE = ""


def declared_plan_book(graph: RecipeGraph) -> PlanBook:
    """A plan book with an entry for every (node, k) of the graph, from the declared columns of the sources and the steps the walk reads (names only, no types)."""
    entries: Dict[Tuple[str, int], Union[Plan, PlanFailure]] = {}
    ends: Dict[str, Union[Plan, PlanFailure]] = {}
    for nid in graph.nodes():
        node = graph.node(nid)
        if node.kind == "DS":
            names = graph.column_info(nid).names
            plan: Union[Plan, PlanFailure] = (Plan.of((n, UNKNOWN_TYPE) for n in names) if names is not None
                                              else PlanFailure(graph.column_info(nid).reason or "the recipe does not declare the columns of this source table", nid, 0))
            entries[(nid, 0)] = ends[nid] = plan
            continue
        parents = graph.parents(nid)
        start: Union[Plan, PlanFailure] = ends[parents[0]] if parents else PlanFailure(f"{node.path} has no table to start from", nid, 0)
        if isinstance(start, PlanFailure):
            start = PlanFailure(start.sentence, nid, 0)
        entries[(nid, 0)] = current = start
        for k, step in enumerate(node.steps, start=1):
            current = _after(graph, node.id, k, step, current, ends)
            entries[(nid, k)] = current
        ends[nid] = current
    return PlanBook(entries)


def _after(graph: RecipeGraph, nid: str, k: int, step: Any, before: Union[Plan, PlanFailure], ends: Dict[str, Union[Plan, PlanFailure]]) -> Union[Plan, PlanFailure]:
    """The plan after one step: what the reading predicts, checked like the walk checks it (a key the table does not have is a failure); a failure stays a failure."""
    if isinstance(before, PlanFailure):
        return PlanFailure(before.sentence, nid, k)
    effect = fx.effect_of(step)
    if effect.kind == fx.UNREAD:
        return PlanFailure(f"the recipe does not say what the step {effect.action or '?'} does to the columns ({effect.why}); only names are read here", nid, k)
    right = None
    if effect.kind == fx.JOIN:
        right = ends.get(f"T1:{effect.right}")
        if not isinstance(right, Plan):
            return PlanFailure(f"the join reads {effect.right!r}, whose columns the recipe does not give here", nid, k)
    predicted = fx.predict(effect, before, right)
    after = Plan.of((p.name, UNKNOWN_TYPE) for p in predicted)
    problem = fx.agreement_problem(effect, predicted, before, right, after)
    return PlanFailure(problem, nid, k) if problem else after
