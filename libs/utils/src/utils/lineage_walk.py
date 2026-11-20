"""The lineage walk: back, forth, back (LBFB step 1, D-0347): the places where an audit step on one column can be written.

For the column the user looks at (a node and a name), the walk lists the places where a step can be written, what each place
reaches, and where the column no longer exists. It is one pure function of the recipe graph and of the engine's plan: no file,
no row, no engine call, no clock; the same input gives the same output in the same order.

The three moves (D-0347), as occurrences. An OCCURRENCE is (node, k, name): the column called `name` in the plan after k steps of a
node. Two occurrences are LINKED by a step the walk follows (the name is kept; a join key that both sides equate is one column), by the
edge from the end of a table to the start of the next node (T1 to T2, T2 to T3, the first ingredient to its join), or by a join step that
copies a column of the table it reads. Moves: BACK from the start along the links to the sources; FORWARD from there to every node that
depends on it (the reach is the graph's, whether or not the column survives, D-0346); BACK AGAIN along each path to read the name and
the type at each place and the steps that changed them.

What decides what. The engine's plan (D-0325) says where a column exists and its type. A step is read ONLY as D-0351 lists
(`step_effects.READINGS`), and every reading is checked against the plan after the step; a disagreement makes the column grey with the
reason, never a guess. A step outside the list is `unread`: the walk knows only what the plan shows across it.

PROVISIONAL behaviour (the owner has not decided; each place is marked in the code):
- P1 (O1) which GROUPS of places are offered. The user chooses the LEVELS (source, T1, T2, T3; D-0355) and ticks; every line carries its group
  (lineage: above and below the chosen place; join_linked: linked by a join on the key). There is no group for "the same key, no join links it" and a
  column is never matched by its name alone; tables that declare the same key and are not linked are listed as plain information (`Walk.outside`).
- P1b a line at the SOURCE level is returned and grey with `no_step_list` (a source file holds no list of steps, D-0332); how a step acts at that level is not decided.
- P2 a step outside the readings (`step_effects.READINGS`, D-0351 and the names of 2026-11-20): a column across it is ticked only when the plan alone
  proves the name and the type unchanged; any other path through it is grey (`step_not_read`).
- P3 a name that changes on the path (a rename, a key under another name, the suffix of a clash) is FOLLOWED: the line on the other side carries the name the column has
  THERE, with the source column and the hop (renamed from, to, by which step; D-0352, D-0357). A column that a step writes under its own name is the SAME column, ticked,
  with a note as data (D-0353, D-0337): a cast (`another_type_here`, with the types), a compute step (`recomputed_here`), a group-by aggregate (`aggregated_here`) and
  a group key (`one_row_per_group_after_this_step`). A column such a step does not name is untouched: it passes, with no note. PROVISIONAL (not stated by the owner): a recompute
  or an aggregate under the same name is ticked also when its values come from ANOTHER column, because the walk reads names only (D-0356) and cannot tell; the note says
  `knows_source_of_values` False. A cast to the type the column already has gives the hop but no note (no other type there).
- P4 (O7) a place no plot reads is not a line; it is returned in `Walk.unread`, counted apart (D-0346 says it of a join; the same for a source).
- P4b the record allows a rename in one tier and back in a later one as ONE column named as in each table (each occurrence has its own name; owner 2026-11-20).
- P5 (O4) a place of the reach where the column no longer exists is a `Gone` note, distinct from grey (the three viewpoints agree; not confirmed).
- P6 (Q4) a table whose tier 2 is empty is one place with its tier 1, also when plots read the table directly and joins read it too (D-0346 as written).
- P7 (O8) a column that exists twice at a place (a table joined with itself) is grey; joins that are not left or inner are not read.
- P8 (O3) an empty tier 2 or tier 2 of a table no plot reads is not a place; a tier 3 is always a line ("only this plot", D-0346).
- P9 a line is ticked when ANY path from the chosen place to it is certain (the path with the fewest uncertain links, then the fewest changes, is taken); grey only when every path is uncertain.
- P10 the GROUP of a place (lineage, join_linked) is the smallest group that reaches it, so the split depends on where the user looked from; the union of the groups does not.
- P11 `Gone.removed_by` is the FIRST removing step in data-flow order (graph order of the node, then the step number) among the steps that removed the column on the way to the place.
- P12 a join other than left or inner, and a column written under its own name from another column, are not told apart from the readable cases (see P3 and P7).
- P13 a source line next to a tier 1 without steps is the same table: it stays grey `no_step_list` and carries `duplicates` (the tier 1 place), so that a caller shows one line.
- P14 a walk that selects no place says so (`Walk.nothing`); which levels the column exists at is `Walk.held_at_levels`.

The key refusal (D-0297) and the choice of a drop are step 4, not built: `step_kind` is carried, the lines are the same for a filter and a drop.

Consumed by: libs/utils/tests/test_lineage_walk.py (the dialog of HOME calls it later; nothing in app/ yet).
If deleted: the audit dialog has no way to list its places.

# @deps
# provides: function:walk, class:LineageIndex, class:LineageError, class:ColumnNotFound, class:StartPlanFailed
# consumes: libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/step_effects.py, libs/utils/src/utils/plan_book.py, libs/utils/src/utils/lineage_records.py
# consumed_by: libs/utils/tests/test_lineage_walk.py, libs/utils/tests/test_lineage_walk_follow.py, libs/utils/tests/test_lineage_walk_properties.py
# doc: .claude/knowledge/decision_ledger.md (D-0347, D-0346, D-0351, D-0195, D-0353, D-0352, D-0357, D-0337, D-0356, D-0355), .claude/design/home_audit_steps.md
# @end_deps
"""
from __future__ import annotations

import collections
import heapq
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple, Union

from utils import action_names, step_effects as fx
from utils.lineage_records import (
    AGGREGATED, CANNOT_FOLLOW, CAST, CREATED, GREY, GROUPED, JOIN_LINKED, LEVELS, LINEAGE, NO_STEP_LIST, NOTE_AGGREGATED, NOTE_ANOTHER_TYPE, NOTE_ONE_ROW_PER_GROUP,
    NOTE_RECOMPUTED, NOTE_UNREAD_STEP_PASSED, PLAN_FAILED, READING_DISAGREES, RE_CREATED, RECOMPUTED, RENAMED, SEVERAL_COLUMNS, SOURCE, STEP_NOT_READ, T1, T2, T3,
    TICK, UNCHANGED, UNKNOWN, WHY_DECLARED_KEY_NOT_REACHED, Gone, Hop, Line, Note, Occurrence, Outside, Reach, Reason, SourceColumn, Start, StepRef, Unread, Walk,
)
from utils.plan_book import Plan, PlanBook, PlanFailure
from utils.recipe_graph import Node, RecipeGraph

Occ = Tuple[str, int, str]          # (node id, number of steps applied, column name)
PlanOrFailure = Union[Plan, PlanFailure]
STEP_KINDS = ("filter", "drop")
LEVEL_OF_KIND = {"DS": SOURCE, "T1": T1, "T2": T2, "T3": T3}
# What a hop says of a step that changes the name of a column or writes its type, values or rows; and the note a change puts under the line (data only)
HOW_OF_CHANGE = {fx.CHANGE_RENAME: RENAMED, fx.CHANGE_KEY_OTHER_NAME: RENAMED, fx.CHANGE_SUFFIX: RENAMED, fx.CHANGE_CAST: CAST,
                 fx.CHANGE_RECOMPUTE: RECOMPUTED, fx.CHANGE_AGGREGATE: AGGREGATED, fx.CHANGE_GROUP_KEY: GROUPED}
NOTE_OF_CHANGE = {fx.CHANGE_CAST: NOTE_ANOTHER_TYPE, fx.CHANGE_RECOMPUTE: NOTE_RECOMPUTED, fx.CHANGE_AGGREGATE: NOTE_AGGREGATED, fx.CHANGE_GROUP_KEY: NOTE_ONE_ROW_PER_GROUP}
HOW_PRIORITY = (UNKNOWN, RENAMED, CAST, RECOMPUTED, AGGREGATED, GROUPED)
Cost = Tuple[int, int]              # (uncertain links, links that change the name, type, values or rows) on a path: the least of both, in this order


class LineageError(ValueError):
    """The walk cannot start: a plain message says why."""


class ColumnNotFound(LineageError):
    """The column the user names is in no place of the recipe at the node given: a plain error, never an empty list."""


class StartPlanFailed(LineageError):
    """The engine could not give the plan of the node the walk starts from."""


@dataclass(frozen=True)
class _Link:
    src: Occ
    dst: Occ
    certain: bool
    how: str
    reason: Optional[Reason] = None
    ref: Optional[StepRef] = None            # the step of the link (None for the edge from one node to the next)
    hop: bool = False                        # whether the step is listed in the trail of an occurrence
    join_how: Optional[str] = None
    join_side: Optional[str] = None
    note: Optional[Note] = None
    changes: bool = False                    # the step changes the name, the type, the values or the rows of the column (a cost of a path, never a doubt)


@dataclass(frozen=True)
class _Dead:
    """An occurrence that no step carries on: the column vanishes (certain: the plan or a drop shows it) or the walk cannot say (uncertain)."""
    occ: Occ
    in_node: str                             # the node whose step or whose start the column does not cross
    certain: bool
    reason: Optional[Reason]
    ref: Optional[StepRef]


class LineageIndex:
    """The links between the columns of a recipe at every step, built once from the graph and the plan book. `walk` is then a function of the
    start only. The plan book is read once per place (a counting mapping can prove it)."""

    def __init__(self, graph: RecipeGraph, plans: PlanBook) -> None:
        self.graph = graph
        self._order = {nid: i for i, nid in enumerate(graph.nodes())}
        self._plan: Dict[Tuple[str, int], PlanOrFailure] = {}
        for nid in graph.nodes():
            node = graph.node(nid)
            for k in range(len(node.steps) + 1):
                self._plan[(nid, k)] = plans.get(nid, k)
        self._pred: Dict[Occ, List[_Link]] = collections.defaultdict(list)
        self._succ: Dict[Occ, List[_Link]] = collections.defaultdict(list)
        self._dead: List[_Dead] = []
        for nid in graph.nodes():
            node = graph.node(nid)
            if node.kind != "DS":
                self._edge_into(node)
            for k, step in enumerate(node.steps, start=1):
                self._step(node, k, step)
        self._fwd: Dict[str, Tuple[str, ...]] = {}
        self._build_places()

    # ------------------------------------------------------------------ plans
    def end(self, node_id: str) -> Tuple[str, int]:
        return node_id, len(self.graph.node(node_id).steps)

    def plan_end(self, node_id: str) -> PlanOrFailure:
        return self._plan[self.end(node_id)]

    @staticmethod
    def _names(plan: PlanOrFailure) -> Tuple[str, ...]:
        return plan.names if isinstance(plan, Plan) else ()

    def _link(self, link: _Link) -> None:
        self._succ[link.src].append(link)
        self._pred[link.dst].append(link)

    def _die(self, occ: Occ, in_node: str, certain: bool, reason: Optional[Reason] = None, ref: Optional[StepRef] = None) -> None:
        self._dead.append(_Dead(occ, in_node, certain, reason, ref))

    # ------------------------------------------------------------------ the edge from a table to the next node
    def _edge_into(self, node: Node) -> None:
        parents = self.graph.parents(node.id)
        if not parents:
            return
        parent = parents[0]                       # a join starts from its first ingredient; the others are read by its steps
        parent_end, child = self._plan[self.end(parent)], self._plan[(node.id, 0)]
        if not isinstance(parent_end, Plan):
            return
        pk = self.end(parent)
        for name in parent_end.names:
            src = (pk[0], pk[1], name)
            if isinstance(child, PlanFailure):
                self._die(src, node.id, False, Reason(PLAN_FAILED, (("sentence", child.sentence), ("node", node.id), ("step", 0))))
            elif child.has(name) and child.type_of(name) == parent_end.type_of(name):
                self._link(_Link(src, (node.id, 0, name), True, UNCHANGED))
            else:
                self._die(src, node.id, False, Reason(CANNOT_FOLLOW, (("node", node.id), ("step", 0), ("name", name))))

    # ------------------------------------------------------------------ one step
    def _right_of(self, step: Any) -> Optional[str]:
        right = step.get("right_ingredient") if isinstance(step, dict) else None
        return f"T1:{right}" if isinstance(right, str) and self.graph.has_node(f"T1:{right}") else None

    def _step(self, node: Node, k: int, step: Any) -> None:
        nid = node.id
        action = step.get("action") if isinstance(step, dict) and isinstance(step.get("action"), str) else ""
        ref = StepRef(nid, k, action, f"{node.steps_path}[{k}]", step.get("id") if isinstance(step, dict) and isinstance(step.get("id"), str) else None)
        before, after = self._plan[(nid, k - 1)], self._plan[(nid, k)]
        effect = fx.effect_of(step)
        right_node = self._right_of(step) if effect.kind in (fx.JOIN, fx.UNREAD) and action == action_names.JOIN else None
        right: Optional[PlanOrFailure] = self._plan[self.end(right_node)] if right_node else None
        if right_node is None and effect.kind == fx.JOIN:
            effect = fx.Effect(fx.UNREAD, action, why="the join reads a table the recipe does not have")
        failed = [p for p in (before, after, right) if isinstance(p, PlanFailure)]
        if failed:
            reason = Reason(PLAN_FAILED, (("sentence", failed[0].sentence), ("node", nid), ("step", k)))
            self._die_all(nid, k - 1, before, right_node, right, reason, ref)
            return
        assert isinstance(before, Plan) and isinstance(after, Plan)
        if effect.kind != fx.UNREAD:
            predicted = fx.predict(effect, before, right if isinstance(right, Plan) else None)
            problem = fx.agreement_problem(effect, predicted, before, right if isinstance(right, Plan) else None, after)
            if problem is None:
                self._read_links(nid, k, ref, effect, predicted, before, right_node, right)
                return
            reason = Reason(READING_DISAGREES, (("node", nid), ("step", k), ("action", action), ("problem", problem)))
            self._plan_links(nid, k, ref, before, after, right_node, right, reason, passes_certain=False)
            return
        reason = Reason(STEP_NOT_READ, (("node", nid), ("step", k), ("action", action), ("why", effect.why)))
        self._plan_links(nid, k, ref, before, after, right_node, right, reason, passes_certain=True)

    def _die_all(self, nid: str, k: int, before: PlanOrFailure, right_node: Optional[str], right: Optional[PlanOrFailure], reason: Reason, ref: StepRef) -> None:
        for name in self._names(before):
            self._die((nid, k, name), nid, False, reason, ref)
        if right_node and isinstance(right, Plan):
            for name in right.names:
                self._die((right_node, len(self.graph.node(right_node).steps), name), nid, False, reason, ref)

    def _read_links(self, nid: str, k: int, ref: StepRef, effect: fx.Effect, predicted: Sequence[fx.PredictedColumn], before: Plan,
                    right_node: Optional[str], right: Optional[PlanOrFailure]) -> None:
        is_join = effect.kind == fx.JOIN
        used_left: Set[str] = set()
        right_end = self.end(right_node) if right_node else ("", 0)
        after = self._plan[(nid, k)]
        for pc in predicted:
            dst = (nid, k, pc.name)
            for source in pc.sources:
                left = source.side == "left"
                src = (nid, k - 1, source.name) if left else (right_end[0], right_end[1], source.name)
                if left:
                    used_left.add(source.name)
                # The reading agrees with the plan (checked by the caller), so the link is certain: the column is the same one under the name it has after the step
                # (D-0351, D-0352, D-0357). A rename, a key under another name or the suffix of a clash changes the name (the hop says so); a step that writes the column
                # under its own name changes its type, values or rows (a note, D-0353, D-0337).
                kind_of = pc.change if (pc.change in fx.NOTE_CHANGES or source.name != pc.name) else None
                note = self._change_note(kind_of, nid, k, ref, source.name, pc.name, before, after, src, dst)
                self._link(_Link(src, dst, True, HOW_OF_CHANGE[kind_of] if kind_of else UNCHANGED, None, ref, hop=bool(kind_of) or is_join,
                                 join_how=effect.how if is_join else None, join_side=("base" if left else "right") if is_join else None, note=note,
                                 changes=bool(kind_of)))
        for name in before.names:
            if name not in used_left:                # dropped, or not selected: the plan and the reading agree that it is gone
                self._die((nid, k - 1, name), nid, True, None, ref)

    def _change_note(self, kind_of: Optional[str], nid: str, k: int, ref: StepRef, name_before: str, name_after: str, before: Plan, after: Plan,
                     src: Occ, dst: Occ) -> Optional[Note]:
        """The note a step puts under the lines it changes, as data: which step, the name and the type before and after. A rename, a key under another name and a
        suffix are in the hop, not a note. A cast to the type the column already had changes nothing the user can see: no note (PROVISIONAL, P3)."""
        if kind_of not in NOTE_OF_CHANGE:
            return None
        type_before = (self._plan[(src[0], src[1])].type_of(src[2]) if isinstance(self._plan[(src[0], src[1])], Plan) else None) or ""
        type_after = after.type_of(name_after) or ""
        if kind_of == fx.CHANGE_CAST and type_before == type_after:
            return None
        params: Tuple[Tuple[str, Any], ...] = (("node", nid), ("step", k), ("action", ref.action), ("name_before", name_before), ("name_after", name_after),
                                               ("type_before", type_before), ("type_after", type_after))
        if kind_of in (fx.CHANGE_RECOMPUTE, fx.CHANGE_AGGREGATE):
            params += (("knows_source_of_values", False),)                  # PROVISIONAL (P3): names only are read, so the walk cannot tell where the new values come from
        return Note(NOTE_OF_CHANGE[kind_of], params)

    def _plan_links(self, nid: str, k: int, ref: StepRef, before: Plan, after: Plan, right_node: Optional[str], right: Optional[PlanOrFailure],
                    reason: Reason, passes_certain: bool) -> None:
        """A step the walk may not read, or whose reading the plan contradicts: only what the plan shows is used. A column with the same name and
        type before and after passes (certain after an unread step, with a note; uncertain after a disagreement); anything else is uncertain."""
        for name in before.names:
            src = (nid, k - 1, name)
            if after.has(name) and after.type_of(name) == before.type_of(name):
                note = Note(NOTE_UNREAD_STEP_PASSED, (("node", nid), ("step", k), ("action", ref.action))) if passes_certain else None
                self._link(_Link(src, (nid, k, name), passes_certain, UNCHANGED if passes_certain else UNKNOWN, None if passes_certain else reason,
                                 ref, hop=True, note=note))
            elif after.has(name):
                self._link(_Link(src, (nid, k, name), False, UNKNOWN, reason, ref, hop=True))
            else:
                self._die(src, nid, False, reason, ref)
        if right_node and isinstance(right, Plan):
            re = self.end(right_node)
            for name in right.names:
                src = (re[0], re[1], name)
                if after.has(name) and not before.has(name) and after.type_of(name) == right.type_of(name):
                    self._link(_Link(src, (nid, k, name), False, UNKNOWN, reason, ref, hop=True, join_side="right"))
                else:
                    self._die(src, nid, False, reason, ref)

    # ------------------------------------------------------------------ places
    def _build_places(self) -> None:
        g = self.graph
        self.place_of: Dict[str, str] = {}
        self.place_first: Dict[str, str] = {}
        self.place_covers: Dict[str, List[str]] = {}
        for nid in g.nodes():
            node = g.node(nid)
            if node.kind == "T2" and not (node.steps and node.read_by_plot):
                place = self.place_of[f"T1:{node.name}"]       # an empty tier 2, or one no plot reads, is the table before it (D-0346)
            else:
                place = nid
                self.place_first[place] = nid
                self.place_covers[place] = []
            self.place_of[nid] = place
            self.place_covers[place].append(nid)
        # the node whose plan is the place's own table: the tier 1 for a table whose tier 2 is not a place, else the node itself
        self.place_last = {place: next(n for n in self.place_covers[place] if g.node(n).kind != "T2" or n == place) for place in self.place_first}
        self.place_order = sorted(self.place_first, key=lambda p: self._order[self.place_first[p]])
        self._plots_below: Dict[str, FrozenSet[str]] = {}
        self._reach: Dict[str, Reach] = {}
        for place in self.place_order:
            first = self.place_first[place]
            nodes = [first] + self.forward(first)
            plots = frozenset(g.node(n).name for n in nodes if g.node(n).kind == "T3")
            self._plots_below[place] = plots
        for place in self.place_order:
            first = self.place_first[place]
            nodes = [first] + self.forward(first)
            tables = {self.place_of[n] for n in nodes if g.node(n).kind in ("T1", "T2")}
            self._reach[place] = Reach(frozenset(p for p in tables if self._plots_below[p]), frozenset(p for p in tables if not self._plots_below[p]),
                                       self._plots_below[place])

    def forward(self, node_id: str) -> List[str]:
        if node_id not in self._fwd:
            self._fwd[node_id] = tuple(self.graph.lineage_forward(node_id))
        return list(self._fwd[node_id])

    def reach_of(self, place: str) -> Reach:
        return self._reach[place]

    # ------------------------------------------------------------------ closures
    def _sort_key(self, occ: Occ) -> Tuple[int, int, str]:
        return self._order[occ[0]], occ[1], occ[2]

    def _reach_set(self, seeds: Iterable[Occ], forward: bool, backward: bool) -> Set[Occ]:
        seen: Set[Occ] = set(seeds)
        stack = list(seen)
        while stack:
            occ = stack.pop()
            if forward:
                for link in self._succ.get(occ, ()):
                    if link.dst not in seen:
                        seen.add(link.dst)
                        stack.append(link.dst)
            if backward:
                for link in self._pred.get(occ, ()):
                    if link.src not in seen:
                        seen.add(link.src)
                        stack.append(link.src)
        return seen

    def lineage_set(self, start: Occ) -> Set[Occ]:
        """D-0347 as written: back to the sources of the start, then forward from every column found there."""
        back = self._reach_set([start], forward=False, backward=True)
        return self._reach_set(back, forward=True, backward=False)

    def component(self, seeds: Iterable[Occ]) -> Set[Occ]:
        """Every column linked to the seeds, in both directions, until nothing new comes (joins that equate the column are followed both ways)."""
        return self._reach_set(seeds, forward=True, backward=True)

    def _costs(self, start: Occ, allowed: Set[Occ]) -> Dict[Occ, Tuple[Cost, Optional[_Link], Optional[Occ]]]:
        """Least cost of a path from the start inside `allowed`, either direction: for each column the cost (the number of uncertain links, then the number of links
        that change the name, type, values or rows), the last link used and the column before it on that path. Neighbours are visited in a fixed order, so the paths
        are the same every run. A column is certain when a path without an uncertain link reaches it (PROVISIONAL, P9)."""
        best: Dict[Occ, Tuple[Cost, Optional[_Link], Optional[Occ]]] = {start: ((0, 0), None, None)}
        heap: List[Tuple[Cost, Tuple[int, int, str], Occ]] = [((0, 0), self._sort_key(start), start)]
        while heap:
            cost, _key, occ = heapq.heappop(heap)
            if cost != best[occ][0]:
                continue
            neighbours = [(link.dst, link) for link in self._succ.get(occ, ())] + [(link.src, link) for link in self._pred.get(occ, ())]
            for other, link in sorted(neighbours, key=lambda x: (self._sort_key(x[0]), not x[1].certain, x[1].changes)):
                if other not in allowed:
                    continue
                step = (cost[0] + (0 if link.certain else 1), cost[1] + (1 if link.changes else 0))
                if other not in best or step < best[other][0]:
                    best[other] = (step, link, occ)
                    heapq.heappush(heap, (step, self._sort_key(other), other))
        return best

    # ------------------------------------------------------------------ the trail of an occurrence
    def _trail(self, occ: Occ, within: Set[Occ]) -> Tuple[str, Tuple[Hop, ...], Tuple[SourceColumn, ...]]:
        """(how, the steps that matter from the source to here, the source columns), along one canonical path back inside `within`."""
        hops: List[Hop] = []
        how = UNCHANGED
        current = occ
        while True:
            preds = [link for link in self._pred.get(current, ()) if link.src in within]
            if not preds:
                break
            link = sorted(preds, key=lambda l: (not l.certain, self._sort_key(l.src)))[0]
            if link.hop and link.ref is not None:
                before_plan, after_plan = self._plan[(link.src[0], link.src[1])], self._plan[(link.dst[0], link.dst[1])]
                hops.append(Hop(link.ref, link.how, link.src[2], link.dst[2], before_plan.type_of(link.src[2]) if isinstance(before_plan, Plan) else None,
                                after_plan.type_of(link.dst[2]) if isinstance(after_plan, Plan) else "", link.join_how, link.join_side))
                how = next((h for h in HOW_PRIORITY if h in (link.how, how)), how)
            current = link.src
        sources = self._sources(occ, within)
        if not sources and self.graph.node(current[0]).kind != "DS":
            how = UNKNOWN if how == UNKNOWN else (RE_CREATED if self._existed_before(current) else CREATED)
        hops.reverse()
        return how, tuple(hops), sources

    def _existed_before(self, root: Occ) -> bool:
        node, k, name = root
        return any(isinstance(self._plan.get((node, j)), Plan) and self._plan[(node, j)].has(name) for j in range(0, max(k - 1, 0)))  # type: ignore[union-attr]

    def _sources(self, occ: Occ, within: Set[Occ]) -> Tuple[SourceColumn, ...]:
        seen, stack, found = {occ}, [occ], set()
        while stack:
            current = stack.pop()
            preds = [link.src for link in self._pred.get(current, ()) if link.src in within]
            if not preds and self.graph.node(current[0]).kind == "DS":
                found.add((self._order[current[0]], current[2], self.graph.node(current[0]).name))
            for p in preds:
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return tuple(SourceColumn(table, name) for _, name, table in sorted(found))

    def occurrence(self, occ: Occ, within: Set[Occ]) -> Occurrence:
        plan = self._plan[(occ[0], occ[1])]
        how, hops, sources = self._trail(occ, within)
        return Occurrence(occ[2], plan.type_of(occ[2]) or "", how, sources, hops)  # type: ignore[union-attr]

    def at_end(self, place: str, within: Set[Occ]) -> List[Occ]:
        node, k = self.end(self.place_last[place])
        plan = self._plan[(node, k)]
        return [(node, k, name) for name in self._names(plan) if (node, k, name) in within]

    # ------------------------------------------------------------------ the walk
    def walk(self, start: Start, *, levels: Iterable[str], kind: str = "filter") -> Walk:
        g = self.graph
        chosen_levels = tuple(level for level in LEVELS if level in set(levels))
        if not chosen_levels or set(levels) - set(LEVELS):
            raise LineageError(f"the levels are some of {list(LEVELS)}; the caller must name at least one (got {sorted(set(levels), key=str)})")
        if kind not in STEP_KINDS:
            raise LineageError(f"the kind of step is {kind!r}; it is one of {list(STEP_KINDS)}")
        if not g.has_node(start.node):
            raise LineageError(f"the recipe has no node {start.node!r}")
        plan = self.plan_end(start.node)
        if isinstance(plan, PlanFailure):
            raise StartPlanFailed(f"the engine could not give the columns of {start.node}: {plan.sentence}")
        if not plan.has(start.column):
            raise ColumnNotFound(f"the column {start.column!r} is not in {start.node} (it has {list(plan.names)})")
        begin: Occ = (start.node, *self.end(start.node)[1:], start.column)

        lineage, linked = self.lineage_set(begin), self.component([begin])
        costs = self._costs(begin, linked)                      # PROVISIONAL (O1): which groups are offered; the levels the user chooses decide what is shown
        region = {p: grp for p, grp in self._region_groups(lineage, linked).items()
                  if any(LEVEL_OF_KIND[g.node(n).kind] in chosen_levels for n in self.place_covers[p])}
        start_place = self.place_of.get(start.node)

        lines: List[Line] = []
        gone: List[Gone] = []
        unread: List[Unread] = []
        for place in [p for p in self.place_order if p in region]:
            reach = self.reach_of(place)
            covers = tuple(self.place_covers[place])
            if not reach.plots:
                unread.append(Unread(place, covers, bool(self.at_end(place, linked)), reach, region[place]))
                continue
            line = self._classify(place, covers, reach, linked, lineage, linked, costs, start_place, region[place])
            (lines if isinstance(line, Line) else gone).append(line)  # type: ignore[arg-type]
        gone = [Gone(x.place, x.covers, x.removed_by, tuple(l.place for l in lines if self._reaches(l.reach, x.place)), kind, kind == "filter", x.reach, x.scope_group) for x in gone]
        held = {LEVEL_OF_KIND[g.node(n).kind] for p in self._region_groups(lineage, linked) if self.at_end(p, linked) for n in self.place_covers[p]}
        return Walk(start, kind, chosen_levels, tuple(lines), tuple(gone), tuple(unread), self._outside(linked), start_type=plan.type_of(start.column) or "",
                    held_at_levels=tuple(level for level in LEVELS if level in held))

    def _region_groups(self, lineage: Set[Occ], linked: Set[Occ]) -> Dict[str, str]:
        """Every place that a group reaches (forward from the nodes that hold the column) with the smallest group that reaches it."""
        found: Dict[str, str] = {}
        for group, held in ((LINEAGE, lineage), (JOIN_LINKED, linked)):
            for h in sorted({occ[0] for occ in held}, key=self._order.__getitem__):
                for n in [h] + self.forward(h):
                    found.setdefault(self.place_of[n], group)
        return found

    @staticmethod
    def _reaches(reach: Reach, place: str) -> bool:
        return place in reach.tables_with_plot or place in reach.tables_no_plot or (place.startswith("T3:") and place[3:] in reach.plots)

    def _classify(self, place: str, covers: Tuple[str, ...], reach: Reach, chosen: Set[Occ], lineage: Set[Occ], linked: Set[Occ],
                  costs: Dict[Occ, Tuple[Cost, Optional[_Link], Optional[Occ]]], start_place: Optional[str], default_group: str) -> Union[Line, Gone]:
        last = self.place_last[place]
        tier = self.graph.node(self.place_first[place]).kind
        kind = "plot" if tier == "T3" else "table"
        end_plan = self.plan_end(last)
        if isinstance(end_plan, PlanFailure):
            reason = Reason(PLAN_FAILED, (("sentence", end_plan.sentence), ("node", end_plan.node or last), ("step", end_plan.step if end_plan.step is not None else -1)))
            return Line(place, covers, tier, kind, (), GREY, reason, (), default_group, place == start_place, reach)
        held = self.at_end(place, chosen)
        if not held:
            return self._without_column(place, covers, reach, chosen, default_group)
        group = LINEAGE if any(o in lineage for o in held) else JOIN_LINKED
        occurrences = tuple(self.occurrence(o, chosen) for o in held)
        notes: List[Note] = []
        reason: Optional[Reason] = None
        state = TICK
        if len(held) > 1:
            state, reason = GREY, Reason(SEVERAL_COLUMNS, (("names", tuple(o[2] for o in held)),))                 # PROVISIONAL P7
        else:
            occ = held[0]
            path = self._path(occ, costs)
            notes = [Note(l.note.code, l.note.params + (("direction", "forward" if forward else "backward"),)) for l, forward in path if l.note is not None]
            if costs[occ][0][0] > 0:
                state, reason = GREY, next((l.reason for l, _ in path if not l.certain and l.reason is not None), Reason(CANNOT_FOLLOW, (("node", occ[0]),)))
        duplicates: Optional[str] = None
        if tier == "DS":                                                                                              # PROVISIONAL (P1b, P13): a source holds no list of steps (D-0332)
            table = self.graph.node(self.place_first[place]).name
            if state == TICK:
                state, reason = GREY, Reason(NO_STEP_LIST, (("table", table),))
            first_tier = f"T1:{table}"
            if self.graph.has_node(first_tier) and not self.graph.node(first_tier).steps:
                duplicates = self.place_of[first_tier]                                                                # the same table as its tier 1: a caller shows one line
        return Line(place, covers, tier, kind, occurrences, state, reason, tuple(notes), group, place == start_place, reach, None, duplicates)

    @staticmethod
    def _path(occ: Occ, costs: Dict[Occ, Tuple[Cost, Optional[_Link], Optional[Occ]]]) -> List[Tuple[_Link, bool]]:
        """The links of the cheapest path from the start to a column, start first, each with whether the path crosses it with the data (`True`) or against it."""
        links: List[Tuple[_Link, bool]] = []
        while costs[occ][1] is not None:
            link, before = costs[occ][1], costs[occ][2]
            links.append((link, link.src == before))  # type: ignore[union-attr]
            occ = before  # type: ignore[assignment]
        links.reverse()
        return links

    def _without_column(self, place: str, covers: Tuple[str, ...], reach: Reach, chosen: Set[Occ], group: str) -> Union[Line, Gone]:
        """No occurrence at the end of a place of the reach: the column was removed (a note) or the walk cannot say (grey)."""
        last = self.place_last[place]
        below = {last} | set(self.graph.lineage_back(last))
        found = [d for d in self._dead if d.occ in chosen and d.in_node in below]
        tier = self.graph.node(self.place_first[place]).kind
        kind = "plot" if tier == "T3" else "table"
        uncertain = sorted((d for d in found if not d.certain), key=lambda d: (self._order[d.in_node], d.ref.step if d.ref else 0))
        if uncertain or not found:
            reason = uncertain[0].reason if uncertain else Reason(CANNOT_FOLLOW, (("node", last),))
            return Line(place, covers, tier, kind, (), GREY, reason, (), group, False, reach)
        return Gone(place, covers, self.first_removal(found).ref, (), "filter", True, reach, group)

    def first_removal(self, found: Sequence[_Dead]) -> _Dead:
        """PROVISIONAL (P11): when several steps removed the column on the way to a place, the one named is the FIRST in data-flow order: the earliest node
        in the order of the graph (sources, then tier 1 of tables and joins as they depend on each other, tier 2, then plots), then the lowest step number."""
        return sorted(found, key=lambda d: (self._order[d.in_node], d.ref.step if d.ref else 0))[0]

    # ------------------------------------------------------------------ what is not reached
    def _outside(self, linked: Set[Occ]) -> Tuple[Outside, ...]:
        """The source tables that declare a key of the same family as the lineage's and that no join links to it: plain information (never a line, never matched by
        the name alone: only `is_entity_key` declarations and the key pairs of joins are used)."""
        g = self.graph
        reached = {g.node(o[0]).name for o in linked if g.node(o[0]).kind == "DS"}
        names: Set[str] = set()
        for o in linked:
            if g.node(o[0]).kind == "DS":
                names |= set(g.key_family_of(o[2]) or ())
        found: List[Outside] = []
        for nid in g.nodes():
            node = g.node(nid)
            if node.kind == "DS" and node.name not in reached:
                found.extend(Outside(node.name, name, WHY_DECLARED_KEY_NOT_REACHED, self.reach_of(f"T1:{node.name}")) for name in g.declared_entity_keys(node.name) if name in names)
        return tuple(found)


def walk(graph: RecipeGraph, plans: PlanBook, start: Start, *, levels: Iterable[str], kind: str = "filter") -> Walk:
    """The places of the chosen levels where a step on the column `start.column` of `start.node` can be written, with what each reaches, each with its group.

    `levels` (some of `LEVELS`: source, T1, T2, T3) has no default: the user chooses which levels are offered (owner, D-0355). A place that covers several
    tiers (an empty tier is no place) belongs to each of them. `kind` is `filter` or `drop` (the join-key refusal of a drop is not built here). Raises
    `ColumnNotFound` for a column the node does not have and `StartPlanFailed` when the engine could not give the plan of the node; every place of the
    chosen levels that the lineage reaches is a line, a note under a line, or a place no plot reads. For many walks on one recipe build `LineageIndex` once."""
    return LineageIndex(graph, plans).walk(start, levels=levels, kind=kind)
