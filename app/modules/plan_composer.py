"""The plan of every place of a recipe, composed by the build's own code and never built or stored (LBFB step 0b, D-0325).

D-0325: "the list of places where a column exists is found by asking the engine for the plan of every place (names and types), in HOME and in the audit". This
module is that question. It returns the plan book (`utils.plan_book.PlanBook`) the lineage walk reads: for every node of the recipe graph (a source table,
the tier 1, the tier 2 of a table or a join, the tier 3 of a plot) and every k, the columns (name, engine type) after k steps.

HOW IT IS MADE. The build composes a table from lazy frames and then stores it; it never needed the composition apart from the storing. The pieces that choose and
run it are functions of `app/modules/orchestrator.py` (`ingredient_parts`, `join_parts`, `tier2_parts`, `tier3_parts`, `tier3_frames`) and the build calls
the same ones: this module calls them and reads `collect_schema()` of the lazy frame after each step. No table is collected, no file is written, no key is made
(only a pivot, a sample or a describe read rows while the plan is made, and a few checks of the assembler read some, as in the build). So "the plan equals the
real run" is true because there is one code, and a standing test (`app/tests/test_plan_composer.py`) compares it with the tables really built on every shipped
recipe. The order of the places comes from `opening_build.plan_places`; the sources and the tables that are not stored (a table that only a join reads, a tier 2
nobody has steps for) are composed where a later place needs them, memoised, so each place is composed once.

A FAILURE IS A VALUE (D-0176, D-0342). A step that cannot be planned gives a `PlanFailure` with the engine's own sentence (and the table, tier and step) as the
entry of that place and of every place below it (k and the places that read it), so the walk greys them and says why; nothing is raised for a fault of the recipe
or its data (a missing file, a step naming a column the table does not have, a refused engine, audit steps in a recipe that is not an audit copy). The book has an
entry for EVERY (node, k) of the graph: `compose_plan_book` raises `PlanComposerBug` (a bug of this module, never a fault of the recipe) if one is missing. A
recipe that cannot be drawn as a graph has no places: `RecipeGraphError` goes up (the walk needs the graph too).

TWO CHOICES OF THE BUILDER (PROVISIONAL, not decided):
1. a failure below a failing place keeps the engine's sentence and where it first failed (`PlanFailure.node`, `.step`), not the place it is read at;
2. a join with no step and more than one ingredient has no plan (the build says "No step list and no ingredients"): its entry is that failure.

Pure: no Shiny, no write. It reads the data files the way the build does (`DataOrchestrator._read_source`).

Consumed by: app/modules/audit_run.py (the gate of an audit step), app/modules/cache_keys.py, app/modules/session_manager.py, app/handlers/filter_and_audit_handlers.py, app/tests/test_plan_composer.py.
If deleted: the walk and the gate of a key drop have no engine plan, only the names the recipe declares.

# @deps
# provides: function:compose_plan_book, function:composition_order, function:compose_candidate_plan_book, class:PlanComposerBug
# consumes: app/modules/orchestrator.py (ingredient_parts, join_parts, tier2_parts, tier3_parts, tier3_frames, refuse_audit_steps_outside_an_audit), app/modules/opening_build.py (plan_places), app/modules/build_failure.py (step_failure_error), libs/utils/src/utils/plan_book.py, libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/audit_copy.py
# consumed_by: app/tests/test_plan_composer.py, app/modules/audit_run.py, app/modules/cache_keys.py, app/modules/session_manager.py, app/handlers/filter_and_audit_handlers.py
# doc: .claude/knowledge/decision_ledger.md (D-0325, D-0351, D-0358, D-0195, D-0326, D-0342, D-0176)
# @end_deps
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple, Union

from app.modules.build_failure import step_failure_error
from app.modules.opening_build import TIER1, TIER2, TIER3, plan_places
from app.modules.orchestrator import (DataOrchestrator, refuse_audit_steps_outside_an_audit, tier2_parts, tier3_frames, tier3_parts)
from utils import audit_copy
from utils.plan_book import Plan, PlanBook, PlanFailure
from utils.recipe_graph import RecipeGraph, build_graph

PlanOrFailure = Union[Plan, PlanFailure]
_NO_TIP = ""   # the sentence is data: the engine's words, no advice of ours


class PlanComposerBug(RuntimeError):
    """The book is not complete: a place of the graph was not composed. A bug of this module, never a fault of the recipe."""


def _plan_of(lf: Any) -> Plan:
    return Plan.of((name, str(kind)) for name, kind in lf.collect_schema().items())


def _failure(error: BaseException, node: str, step: Optional[int]) -> PlanFailure:
    """The engine's sentence as data: the plain error of the build when it is one (it names the table, tier and step), else the error's text."""
    text = str(error).strip()
    tip = getattr(error, "tip", None)
    return PlanFailure(f"{text} ({tip})" if tip and str(tip) not in text else text, node, step)


class _Composer:
    """The state of one composition: the orchestrator, the recipe, the graph, the frames at the end of every node already composed, the book."""

    def __init__(self, orchestrator: DataOrchestrator, recipe_id: str, loaded: Any, graph: RecipeGraph) -> None:
        self.orch = orchestrator
        self.recipe_id = recipe_id
        self.loaded = loaded
        self.raw = loaded.raw
        self.audit = loaded.is_audit_copy
        self.graph = graph
        self.schemas = orchestrator._schemas_of(self.raw)
        self.entries: Dict[Tuple[str, int], PlanOrFailure] = {}
        self.frames: Dict[str, Any] = {}               # node id -> the lazy table at the end of the node (only when its plan is a Plan)
        self.sources: Dict[str, Any] = {}              # schema id -> (lazy source table, engine, tier-1 steps) or the error of reading it

    # ------------------------------------------------------------------ the entries
    def _fail_from(self, nid: str, first: int, failure: PlanFailure) -> PlanFailure:
        """Entries `first`..n of `nid` are the failure; the engine's sentence and its first place are kept."""
        for k in range(first, len(self.graph.node(nid).steps) + 1):
            self.entries[(nid, k)] = failure
        return failure

    def _finish(self, nid: str, plan: PlanOrFailure, lf: Any = None) -> PlanOrFailure:
        if isinstance(plan, Plan) and lf is not None:
            self.frames[nid] = lf
        return plan

    def end(self, nid: str) -> PlanOrFailure:
        """The plan at the end of the node, composing the node (and what it reads) on the first ask."""
        n = len(self.graph.node(nid).steps)
        if (nid, n) not in self.entries:
            self._compose(nid)
        return self.entries[(nid, n)]

    def _compose(self, nid: str) -> None:
        node = self.graph.node(nid)
        try:
            if node.kind == "DS":
                self._source(node)
            elif node.kind == "T1" and node.collection_kind == "schema":
                self._tier1_schema(node)
            elif node.kind == "T1":
                self._tier1_join(node)
            elif node.kind == "T2":
                self._tier2(node)
            else:
                self._tier3(node)
        except Exception as error:   # a fault of the recipe or its data that no step of the code above owned: still a value of the book
            self._fail_from(nid, 0, _failure(error, nid, None))
        for k in range(len(node.steps) + 1):
            if (nid, k) not in self.entries:
                raise PlanComposerBug(f"no plan for {nid} after {k} step(s)")

    # ------------------------------------------------------------------ one place of each kind
    def _read(self, schema_id: str) -> Any:
        if schema_id not in self.sources:
            try:
                self.sources[schema_id] = self.orch.ingredient_parts(schema_id, self.schemas[schema_id], self.recipe_id, self.raw, audit=self.audit)
            except Exception as error:
                self.sources[schema_id] = error
        found = self.sources[schema_id]
        if isinstance(found, Exception):
            raise found
        return found

    def _source(self, node: Any) -> None:
        lf, _, _ = self._read(node.name)
        self.entries[(node.id, 0)] = self._finish(node.id, _plan_of(lf), lf)

    def _steps_agree(self, node: Any, steps: list) -> Optional[PlanFailure]:
        if len(steps) != len(node.steps):
            return PlanFailure(f"The build runs {len(steps)} step(s) at {node.id} and the recipe graph counts {len(node.steps)}; the plan of this place is not given.", node.id, None)
        return None

    def _tier1_schema(self, node: Any) -> None:
        nid = node.id
        before = self.end(f"DS:{node.name}")
        if isinstance(before, PlanFailure):
            self._fail_from(nid, 0, before)
            return
        _, engine, rules = self._read(node.name)
        mismatch = self._steps_agree(node, rules)
        if mismatch:
            self._fail_from(nid, 0, mismatch)
            return
        self.entries[(nid, 0)] = before
        self._steps(node, engine, self.frames[f"DS:{node.name}"], rules, f"The tier 1 of the table '{node.name}'")

    def _steps(self, node: Any, engine: Any, lf: Any, steps: list, where: str) -> None:
        """Run the steps of `node` one at a time through the build's runner and read the schema after each; the first that cannot be planned fails it and what is below."""
        nid = node.id
        runner = engine.wrangler()
        for k, step in enumerate(steps, start=1):
            try:
                lf = runner.run(lf, [copy.deepcopy(step)])
                plan = _plan_of(lf)
            except Exception as error:
                self._fail_from(nid, k, _failure(step_failure_error(where, steps, k, error, _NO_TIP), nid, k))
                return
            self.entries[(nid, k)] = plan
        self._finish(nid, self.entries[(nid, len(steps))], lf)

    def _tier1_join(self, node: Any) -> None:
        nid = node.id
        spec = self.raw.get("joins", {}).get(node.name)   # as the build reads it (`_materialize_tier1`)
        ingredient_ids = [i.get("dataset_id") if isinstance(i, dict) else i for i in (spec or {}).get("ingredients", []) if (i.get("dataset_id") if isinstance(i, dict) else i)]
        ingredients: Dict[str, Any] = {}
        for ds_id in dict.fromkeys(ingredient_ids):
            if ds_id not in self.schemas:
                continue
            end = self.end(f"T1:{ds_id}")
            if isinstance(end, PlanFailure):
                self._fail_from(nid, 0, end)
                return
            ingredients[ds_id] = self.frames[f"T1:{ds_id}"]
        parts = self.orch.join_parts(self.recipe_id, self.raw, node.name, spec, ingredients, self.schemas, audit=self.audit)
        mismatch = self._steps_agree(node, parts.steps)
        if mismatch:
            self._fail_from(nid, 0, mismatch)
            return
        where = f"The tier 1 of the join '{node.name}'"
        steps = parts.steps
        if not steps:   # an empty list: the build assembles nothing and fails unless one ingredient is the whole table
            try:
                lf = parts.new_assembler().assemble([])
                self.entries[(nid, 0)] = self._finish(nid, _plan_of(lf), lf)
            except Exception as error:
                self._fail_from(nid, 0, _failure(error, nid, None))
            return
        base = self.end(f"T1:{parts.ingredient_ids[0]}")
        self.entries[(nid, 0)] = base
        lf = None
        for k in range(1, len(steps) + 1):
            try:
                lf = parts.new_assembler().assemble(copy.deepcopy(steps[:k]))
                plan = _plan_of(lf)
            except Exception as error:
                self._fail_from(nid, k, _failure(step_failure_error(where, steps, k, error, _NO_TIP), nid, k))
                return
            self.entries[(nid, k)] = plan
        self._finish(nid, self.entries[(nid, len(steps))], lf)

    def _tier2(self, node: Any) -> None:
        nid = node.id
        before = self.end(f"T1:{node.name}")
        if isinstance(before, PlanFailure):
            self._fail_from(nid, 0, before)
            return
        engine, steps = tier2_parts(self.raw, node.name)
        mismatch = self._steps_agree(node, steps)
        if mismatch:
            self._fail_from(nid, 0, mismatch)
            return
        self.entries[(nid, 0)] = before
        self._steps(node, engine, self.frames[f"T1:{node.name}"], steps, f"The tier 2 of the table '{node.name}'")

    def _tier3(self, node: Any) -> None:
        nid = node.id
        target = self.graph.plot_target(node.name)
        before = self.end(f"T2:{target}")
        if isinstance(before, PlanFailure):
            self._fail_from(nid, 0, before)
            return
        _, _, engine, steps = tier3_parts(self.recipe_id, self.raw, node.name)
        mismatch = self._steps_agree(node, steps)
        if mismatch:
            self._fail_from(nid, 0, mismatch)
            return
        self.entries[(nid, 0)] = before
        lf = self.frames[f"T2:{target}"]
        done = 0
        frames = tier3_frames(engine.wrangler(), lf, steps, self.recipe_id, node.name)
        try:
            for done, lf in frames:
                self.entries[(nid, done)] = _plan_of(lf)
        except Exception as error:
            self._fail_from(nid, done + 1, _failure(error, nid, done + 1))
            return
        self._finish(nid, self.entries[(nid, len(steps))], lf)


def compose_plan_book(orchestrator: DataOrchestrator, recipe_id: str, loaded: Any, graph: Optional[RecipeGraph] = None) -> PlanBook:
    """The plan of every place of `loaded` (the original recipe, or an audit copy in the form `cache_keys.loaded_from_resolved` gives), as a `PlanBook`.

    `graph` is the graph of the same recipe when the caller has it (the walk needs it too); else it is built from `loaded.raw` (and `RecipeGraphError` goes up when
    the recipe cannot be drawn). Nothing is built, stored or keyed. A place that cannot be planned is a `PlanFailure` entry, with the places below it; nothing is
    raised for a fault of the recipe or its data."""
    graph = graph or build_graph(loaded.raw)
    composer = _Composer(orchestrator, recipe_id, loaded, graph)
    try:
        refuse_audit_steps_outside_an_audit(loaded, recipe_id)
    except Exception as error:   # the engine refuses every build of this recipe: every place is the same failure
        failure = _failure(error, "", None)
        return PlanBook({(nid, k): failure for nid in graph.nodes() for k in range(len(graph.node(nid).steps) + 1)})
    for nid in composition_order(loaded.raw, graph):
        composer.end(nid)
    return PlanBook(composer.entries)


def composition_order(raw: dict, graph: RecipeGraph) -> List[str]:
    """The nodes in the order they are composed: first the places the opening builds, in ITS order (`opening_build.plan_places`: tier 1 of every collection, then the tier 2 of those
    with steps, then the tier 3 of the plots with steps), then every other node of the graph (a source, a table only a join reads, an empty tier 2 or 3), so the book
    is complete. What a place reads is composed before it, once."""
    order: List[str] = []
    for kind, ident, _ in plan_places(raw):
        nid = {TIER1: f"T1:{ident}", TIER2: f"T2:{ident}", TIER3: f"T3:{ident}"}.get(kind)
        if nid and graph.has_node(nid) and nid not in order:
            order.append(nid)
    return order + [nid for nid in graph.nodes() if nid not in order]


def compose_candidate_plan_book(orchestrator: DataOrchestrator, recipe_id: str, original: Any, audit: audit_copy.AuditCopy, place: str, step: dict,
                                plans: Optional[PlanBook] = None, comment: str = "candidate") -> PlanBook:
    """The plan book of the recipe `audit` has with ONE more audit step, `step`, written at the end of `place` (the walk's `candidates={place: book}`, D-0358).

    The audit copy given is not changed (a deep copy takes the step); `add_step` is the one gate, so a step it refuses raises `audit_copy.AuditCopyError`. `original` is the
    `LoadedDataAnalysisRecipe` the audit was made from. The whole recipe is composed again (PROVISIONAL: measured by the demo script in `tmpAI/`; only the place and what is
    below it need it, but the saving is not taken here: one code path)."""
    from app.modules.cache_keys import loaded_from_resolved
    trial = audit_copy.AuditCopy(copy.deepcopy(audit.original), copy.deepcopy(audit.recipe), audit.audit_id, audit.created)
    audit_copy.add_step(trial, place, copy.deepcopy(step), comment, plans=plans)
    return compose_plan_book(orchestrator, recipe_id, loaded_from_resolved(original, trial.recipe, plans))
