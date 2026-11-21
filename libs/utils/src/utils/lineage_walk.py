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
- P9 a line is ticked when ANY path from the chosen place to it is certain (the path with the fewest uncertain links is taken); grey only when every path is uncertain.
- P10 the GROUP of a place (lineage, join_linked) is the smallest group that reaches it, so the split depends on where the user looked from; the union of the groups does not.
- P11 `Gone.removed_by` is the FIRST removing step in data-flow order (graph order of the node, then the step number) among the steps that removed the column on the way to the place.
- P12 a join other than left or inner, and a column written under its own name from another column, are not told apart from the readable cases (see P3 and P7).
- P13 a source line next to a tier 1 without steps is the same table: it stays grey `no_step_list` and carries `duplicates` (the tier 1 place), so that a caller shows one line.
- P14 a walk that selects no place says so (`Walk.nothing`); which levels the column exists at is `Walk.held_at_levels`.

A DROP (`kind="drop"`, step 4, D-0358 and D-0297): the lines are the places of a filter. A drop at a place is REFUSED, by place and not by name, when a join step later (in a
table built from the place) reads the column as a key, followed forward by the links of the walk (`DropFacts`, `drop_facts`: ONE function, also the gate of `audit_copy`, the
integrity check and the checker, through `utils.key_drop`); a refused line is grey with `refusal` (the join steps that need it, as data). Where no later join needs the column it can be
dropped. A column that a later step or a plot uses without being a key is NOT refused: the line carries what it breaks (`Line.consequences`), from the steps the walk reads and,
when the caller gives the engine's plan of the candidate recipe for a place (`candidates`), from that plan, each reading checked against it (a disagreement is grey with both facts).
P15 a declared entity key that no later join uses is not refused for being declared (decided, D-0448: "Her answer: B"; D-0297 names join keys, D-0358 says by place): the line
says so as information (`declared_entity_key` note); P16 a column the walk cannot follow to the end (a plan failure, an unfollowed step) is grey on a drop line (the reason says why) and the gate
ALLOWS the drop with a warning (D-0449, "Right now od go for B": `key_drop.DropGate.warning`; `DropFacts.uncertain`; it replaced the builder's earlier rule "not written"). PROVISIONAL, for the screen: whether a
grey line of this kind can be chosen, and how the warning shows on it, is not decided (D-0449: "to be looked at again when the walk has its one use on screen"); this module still gives the line grey; P17 without a candidate plan the consequences hold only what the steps the walk reads and the
plot mapping say (`consequences_checked` False, stated, never silent).

Consumed by: libs/utils/src/utils/key_drop.py (the gate of a drop), libs/utils/tests/test_lineage_walk.py (the dialog of HOME calls the walk later).
If deleted: the audit dialog has no way to list its places.

# @deps
# provides: function:walk, function:LineageIndex.drop_facts, function:LineageIndex.drop_consequences, function:LineageIndex.certainty_from, function:LineageIndex.uncertain_ends, class:LineageIndex, class:LineageError, class:ColumnNotFound, class:StartPlanFailed
# consumes: libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/join_keys.py (JOIN_ACTIONS, key_columns), libs/utils/src/utils/step_effects.py, libs/utils/src/utils/plan_book.py, libs/utils/src/utils/lineage_records.py
# consumed_by: libs/utils/src/utils/key_drop.py, libs/utils/src/utils/remove_from_all.py (certainty_from, uncertain_ends), libs/utils/tests/test_lineage_walk.py, libs/utils/tests/test_lineage_walk_follow.py, libs/utils/tests/test_lineage_walk_properties.py, libs/utils/tests/test_lineage_drop.py
# doc: .claude/knowledge/decision_ledger.md (D-0347, D-0346, D-0351, D-0195, D-0353, D-0352, D-0357, D-0337, D-0356, D-0355, D-0358, D-0297), .claude/design/home_audit_steps.md
# @end_deps
"""
from __future__ import annotations

import collections
import dataclasses
import heapq
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Union

from utils import action_names, join_keys, step_effects as fx
from utils.lineage_records import (
    Certainty, AGGREGATED, CANNOT_FOLLOW, CAST, CONSEQUENCE_DISAGREES, CREATED, FROM_PLAN, FROM_READING, GREY, GROUPED, JOIN_LINKED, KEY_NEEDED_LATER, LEVELS, LINEAGE,
    BUILD_FAILS, CLASH_NO_LONGER, NO_STEP_LIST, NOTE_AGGREGATED, NOTE_ANOTHER_TYPE, NOTE_DECLARED_ENTITY_KEY, NOTE_ONE_ROW_PER_GROUP, NOTE_RECOMPUTED, NOTE_UNREAD_STEP_PASSED,
    PLAN_FAILED, PLOT_USES_COLUMN, READING_DISAGREES, RE_CREATED, RECOMPUTED, RENAMED, SEVERAL_COLUMNS, SOURCE, STEP_NAMES_COLUMN, STEP_NOT_READ, T1, T2, T3,
    TICK, UNCHANGED, UNKNOWN, WHY_DECLARED_KEY_NOT_REACHED, Consequence, DropFacts, Gone, Hop, KeyNeed, Line, Note, Occurrence, Outside, Reach, Reason, SourceColumn,
    Start, StepRef, Unread, Walk,
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
Cost = int                          # the number of uncertain links on a path


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


@dataclass(frozen=True)
class _Dead:
    """An occurrence that no step carries on: the column vanishes (certain: the plan or a drop shows it) or the walk cannot say (uncertain)."""
    occ: Occ
    in_node: str                             # the node whose step or whose start the column does not cross
    certain: bool
    reason: Optional[Reason]
    ref: Optional[StepRef]


@dataclass(frozen=True)
class _KeyUse:
    """A join step reads a column as one of its keys: the step, the side (`base` = the table at the step, `right` = the table it reads) and the name at the join."""
    ref: StepRef
    side: str
    name: str


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
        self._key_uses: Dict[Occ, List[_KeyUse]] = collections.defaultdict(list)
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
        if action in join_keys.JOIN_ACTIONS:
            self._record_key_uses(nid, k, ref, step)
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

    def _record_key_uses(self, nid: str, k: int, ref: StepRef, step: Any) -> None:
        """The key columns a join step reads, whether or not the step can be followed: the left names at the table before the step, the right names at the end of the
        table the step reads (D-0358: the drop of a key is refused by place, so every join step that names a key is known here)."""
        left, right = join_keys.key_columns(step)
        right_node = self._right_of(step)
        for name in left:
            self._key_uses[(nid, k - 1, name)].append(_KeyUse(ref, "base", name))
        if right_node is not None:
            end = self.end(right_node)
            for name in right:
                self._key_uses[(end[0], end[1], name)].append(_KeyUse(ref, "right", name))

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
                                 join_how=effect.how if is_join else None, join_side=("base" if left else "right") if is_join else None, note=note))
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
                # PROVISIONAL (P3): a step the walk does not read keeps the name and the type, but the walk cannot know whether the values changed there
                note = (Note(NOTE_UNREAD_STEP_PASSED, (("node", nid), ("step", k), ("action", ref.action), ("knows_source_of_values", False)))
                        if passes_certain else None)
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
        """Least cost of a path from the start inside `allowed`, either direction: for each column the number of uncertain links on the cheapest path, the last link
        used and the column before it on that path. Neighbours are visited in a fixed order, so the paths are the same every run. A column is certain when a path
        without an uncertain link reaches it (PROVISIONAL, P9). The links between the columns of one recipe form no diamond (a column has one way back to each
        source), so the path, and the notes on it, do not depend on which cheapest path is taken."""
        best: Dict[Occ, Tuple[Cost, Optional[_Link], Optional[Occ]]] = {start: (0, None, None)}
        heap: List[Tuple[Cost, Tuple[int, int, str], Occ]] = [(0, self._sort_key(start), start)]
        while heap:
            cost, _key, occ = heapq.heappop(heap)
            if cost != best[occ][0]:
                continue
            neighbours = [(link.dst, link) for link in self._succ.get(occ, ())] + [(link.src, link) for link in self._pred.get(occ, ())]
            for other, link in sorted(neighbours, key=lambda x: (self._sort_key(x[0]), not x[1].certain)):
                if other not in allowed:
                    continue
                step = cost + (0 if link.certain else 1)
                if other not in best or step < best[other][0]:
                    best[other] = (step, link, occ)
                    heapq.heappush(heap, (step, self._sort_key(other), other))
        return best

    def certainty_from(self, seeds: Iterable[Occ], within: Set[Occ]) -> Dict[Occ, Certainty]:
        """For every column of `within` that is linked to a seed: how surely (`Certainty`: the fewest uncertain links on the best path from any seed, the reason of the first uncertain link,
        the notes on that path). The same costs and paths as the walk uses for its lines; a public question so that a caller (`utils.remove_from_all`) need not read the protected
        members. `within` is a set of columns the caller got from `component` or `lineage_set`; a column outside it is not asked about. Changes nothing."""
        best: Dict[Occ, Certainty] = {}
        for seed in seeds:
            costs = self._costs(seed, within)
            for occ, (cost, _link, _before) in costs.items():
                if occ in best and best[occ].cost <= cost:
                    continue
                path = self._path(occ, costs)
                reason = next((l.reason for l, _ in path if not l.certain and l.reason is not None), None) if cost else None
                notes = tuple(Note(l.note.code, l.note.params + (("direction", "forward" if forward else "backward"),)) for l, forward in path if l.note is not None)
                best[occ] = Certainty(cost, reason, notes)
        return best

    def uncertain_ends(self, within: Set[Occ]) -> List[_Dead]:
        """The columns of `within` that a step the walk cannot read leaves without saying where they went (a column that vanishes with no certain cause): the walk cannot follow them further."""
        return [d for d in self._dead if d.occ in within and not d.certain]

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
    def walk(self, start: Start, *, levels: Iterable[str], kind: str = "filter", candidates: Optional[Mapping[str, PlanBook]] = None) -> Walk:
        g = self.graph
        chosen_levels = tuple(level for level in LEVELS if level in set(levels))
        if not chosen_levels or set(levels) - set(LEVELS):
            raise LineageError(f"the levels are some of {list(LEVELS)}; the caller must name at least one (got {sorted(set(levels), key=str)})")
        if kind not in STEP_KINDS:
            raise LineageError(f"the kind of step is {kind!r}; it is one of {list(STEP_KINDS)}")
        if candidates is not None and kind != "drop":
            raise LineageError("the candidate plans are for a drop: a filter changes no plan (D-0325)")
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
            if kind == "drop" and isinstance(line, Line) and len(line.occurrences) == 1 and line.tier != "DS":
                line = self._drop_line(line, self.at_end(place, linked)[0], (candidates or {}).get(place))
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
            if costs[occ][0] > 0:
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

    # ------------------------------------------------------------------ a drop: by place (D-0358)
    def _forward_costs(self, start: Occ) -> Dict[Occ, Cost]:
        """Every column that comes from `start` by the links, forward only, with the least number of uncertain links on a path to it (0: certain). Fixed order."""
        best: Dict[Occ, Cost] = {start: 0}
        heap: List[Tuple[Cost, Tuple[int, int, str], Occ]] = [(0, self._sort_key(start), start)]
        while heap:
            cost, _key, occ = heapq.heappop(heap)
            if cost != best[occ]:
                continue
            for link in sorted(self._succ.get(occ, ()), key=lambda l: (self._sort_key(l.dst), not l.certain)):
                step = cost + (0 if link.certain else 1)
                if link.dst not in best or step < best[link.dst]:
                    best[link.dst] = step
                    heapq.heappush(heap, (step, self._sort_key(link.dst), link.dst))
        return best

    def drop_facts(self, node_id: str, column: str) -> DropFacts:
        """Whether the column `column` of the table at the END of `node_id` can be dropped there, by place (D-0358, D-0297): the join steps that need it as a key,
        the facts that stop the walk, and whether it comes from a declared entity key. ONE function: the lines of a drop walk, `audit_copy.add_step`, the integrity
        check and the checker all ask it (through `utils.key_drop`).

        A join step needs the column when the column, followed forward by the links of the walk (a rename, a key under another name and the suffix of a clash included,
        never the name alone), is one of its keys: in a join step later in a table built from this one, or in the table a join reads. A join step of the node itself is
        before the end of the node and does not count. Where nothing later reads the column as a key it can be dropped (an aggregation by count in a plot, her
        example). A column the node does not have, or a node whose plan failed, gives no need: the plan failure is a fact `unfollowed`, never silence."""
        end = self.end(node_id)
        plan = self._plan[end]
        place = node_id
        if isinstance(plan, PlanFailure):
            if not self.forward(node_id):
                return DropFacts(place, column)                      # nothing is built from this node (a plot): no join can need the column, whatever the plan says
            return DropFacts(place, column, (), (Reason(PLAN_FAILED, (("sentence", plan.sentence), ("node", node_id), ("step", end[1]))),))
        if not plan.has(column):
            return DropFacts(place, column)
        return self._facts_at((end[0], end[1], column), place)

    def drop_consequences(self, node_id: str, column: str) -> List[Consequence]:
        """What the steps the walk reads say a drop of `column` at the end of `node_id` breaks downstream: a later step that names the column (it fails), a plot that draws
        it, a join that had given the other table's same-named column a suffix (that column keeps its own name now). The same readings as a drop line (`_drop_line`), with no
        plan of the candidate: a step that uses the column inside a formula is not seen (only names are read, D-0356). Empty for a column the node does not have or a node whose
        plan failed (the plan failure is a fact of `drop_facts`, never silence). `utils.key_drop` words them in the warning of a drop the walk cannot follow (D-0449)."""
        end = self.end(node_id)
        plan = self._plan[end]
        if isinstance(plan, PlanFailure) or not plan.has(column):
            return []
        return self._reading_consequences(self._forward_costs((end[0], end[1], column)))

    def _facts_at(self, occ: Occ, place: str) -> DropFacts:
        reached = self._forward_costs(occ)
        needs: List[KeyNeed] = []
        for other in sorted(reached, key=self._sort_key):
            for use in self._key_uses.get(other, ()):
                found = KeyNeed(use.ref, use.side, use.name, reached[other] == 0)
                if found not in needs:
                    needs.append(found)
        stops: List[Reason] = []
        for dead in self._dead:
            if not dead.certain and dead.occ in reached:
                reason = dead.reason or Reason(CANNOT_FOLLOW, (("node", dead.in_node),))
                if reason not in stops:
                    stops.append(reason)
        back = self._reach_set([occ], forward=False, backward=True)
        declared = tuple(sc for sc in self._sources(occ, back) if sc.name in self.graph.declared_entity_keys(sc.table))
        return DropFacts(place, occ[2], tuple(needs), tuple(stops), declared)

    @staticmethod
    def _reads_of(effect: fx.Effect) -> Tuple[str, ...]:
        """The column names a step reads in an argument the walk may read (D-0351): the old names of a rename, the columns of a drop, a select, a cast and the group columns
        of a group-by. The names a compute step or an aggregate WRITES are not read; the keys of a join are judged by the key rule, not here."""
        if effect.kind == fx.RENAME:
            return tuple(old for old, _ in effect.pairs)
        if effect.kind in (fx.DROP, fx.SELECT, fx.CAST, fx.GROUP):
            return effect.columns
        return ()

    def _reading_consequences(self, reached: Iterable[Occ]) -> List[Consequence]:
        """What the steps the walk reads say a drop breaks: a later step that names the column (it fails), a plot that draws it (it cannot be drawn), a join
        that gave the other table's same-named column a suffix because of it (that column now keeps its own name, and a step that names the suffixed name fails). A step that uses
        the column inside a formula is not seen here (only names are read, D-0356); the engine's plan of the candidate sees it."""
        found: List[Consequence] = []
        g = self.graph
        for occ in sorted(reached, key=self._sort_key):
            nid, k0, name = occ
            node = g.node(nid)
            if k0 < len(node.steps):
                step = node.steps[k0]
                effect = fx.effect_of(step)
                if name in self._reads_of(effect):
                    ref = StepRef(nid, k0 + 1, effect.action, f"{node.steps_path}[{k0 + 1}]", step.get("id") if isinstance(step, dict) and isinstance(step.get("id"), str) else None)
                    found.append(Consequence(STEP_NAMES_COLUMN, self.place_of[nid], ref, FROM_READING, (("name", name), ("node", nid), ("step", k0 + 1), ("action", effect.action))))
                if effect.kind == fx.JOIN and name not in effect.left_keys:
                    right_node = self._right_of(step)
                    right = self._plan[self.end(right_node)] if right_node else None
                    if isinstance(right, Plan) and right.has(name) and name not in effect.right_keys:       # the join gave the right table's `name` the suffix because this column was there
                        ref = StepRef(nid, k0 + 1, effect.action, f"{node.steps_path}[{k0 + 1}]", step.get("id") if isinstance(step, dict) and isinstance(step.get("id"), str) else None)
                        found.append(Consequence(CLASH_NO_LONGER, self.place_of[nid], ref, FROM_READING,
                                                 (("name", name), ("was_called", name + effect.suffix), ("table", g.node(right_node).name), ("node", nid), ("step", k0 + 1))))
            if node.kind == "T3" and k0 == len(node.steps) and name in g.plot_columns(node.name):
                found.append(Consequence(PLOT_USES_COLUMN, self.place_of[nid], None, FROM_READING, (("plot", node.name), ("name", name), ("node", nid))))
        return found

    def _candidate_end(self, book: PlanBook, written: str, node_id: str) -> PlanOrFailure:
        """The plan at the end of a node in the candidate recipe: the candidate is the recipe with ONE step added at the end of the list of `written`."""
        return book.get(node_id, len(self.graph.node(node_id).steps) + (1 if node_id == written else 0))

    def _plan_consequences(self, written: str, book: PlanBook) -> List[Consequence]:
        """What the engine's plan of the candidate recipe says a drop breaks: a place that builds as the recipe is and does not build with the drop (the engine's own
        sentence, once per origin, not again for every table built from a failing one), and a plot whose column the table no longer has."""
        g = self.graph
        found: List[Consequence] = []
        for nid in [written] + self.forward(written):
            node = g.node(nid)
            end_k = len(node.steps) + (1 if nid == written else 0)
            first_k = len(node.steps) + 1 if nid == written else 0
            for k in range(first_k, end_k + 1):
                cand = book.get(nid, k)
                base = self._plan[(nid, k)] if k <= len(node.steps) else None
                if isinstance(cand, PlanFailure) and not isinstance(base, PlanFailure):
                    if k == 0 and any(isinstance(self._candidate_end(book, written, p), PlanFailure) for p in g.parents(nid)):
                        break                                        # the table above fails already: not an origin
                    ref = None
                    if 1 <= k <= len(node.steps):
                        step = node.steps[k - 1]
                        ref = StepRef(nid, k, step.get("action", "") if isinstance(step, dict) else "", f"{node.steps_path}[{k}]",
                                      step.get("id") if isinstance(step, dict) and isinstance(step.get("id"), str) else None)
                    found.append(Consequence(BUILD_FAILS, self.place_of[nid], ref, FROM_PLAN, (("sentence", cand.sentence), ("node", nid), ("step", k))))
                    break
            if node.kind == "T3":
                cand_end, base_end = self._candidate_end(book, written, nid), self.plan_end(nid)
                if isinstance(cand_end, Plan) and isinstance(base_end, Plan):
                    for name in g.plot_columns(node.name):
                        if base_end.has(name) and not cand_end.has(name):
                            found.append(Consequence(PLOT_USES_COLUMN, self.place_of[nid], None, FROM_PLAN, (("plot", node.name), ("name", name), ("node", nid))))
        return found

    def _disagreements(self, written: str, book: PlanBook, reading: Sequence[Consequence]) -> List[Consequence]:
        """The readings the engine's plan of the candidate does not confirm (D-0351: shown grey with both facts): a step that names the column where the candidate still
        builds, a plot that draws the column where the candidate's table still has it."""
        wrong: List[Consequence] = []
        for c in reading:
            if c.code == CLASH_NO_LONGER:
                after_join = book.get(c.step.node, c.step.step)                  # steps before the one added keep their numbers in the candidate
                if isinstance(after_join, Plan) and after_join.has(c.get("was_called")):
                    wrong.append(c)
                continue
            node = c.get("node")
            if node is None and c.step is not None:
                node = c.step.node
            cand = self._candidate_end(book, written, node)
            if c.code == STEP_NAMES_COLUMN and isinstance(cand, Plan):
                wrong.append(c)
            elif c.code == PLOT_USES_COLUMN and isinstance(cand, Plan) and cand.has(c.get("name")):
                wrong.append(c)
        return wrong

    def _drop_line(self, line: Line, occ: Occ, candidate: Optional[PlanBook]) -> Line:
        """The facts a drop adds to a line: the refusal by place (a join step later needs the column as a key), the declared entity key as information, what the drop
        breaks downstream (from the readings, and from the engine's plan of the candidate when the caller gave one for this place)."""
        facts = self._facts_at(occ, line.place)
        notes = list(line.notes) + [Note(NOTE_DECLARED_ENTITY_KEY, (("table", sc.table), ("name", sc.name), ("column", occ[2]))) for sc in facts.declared]
        state, reason, refusal = line.state, line.reason, None
        if facts.refused:
            refusal = Reason(KEY_NEEDED_LATER, (("column", occ[2]), ("place", line.place), ("needs", tuple(n for n in facts.needs if n.certain))))
            state, reason = GREY, (reason if line.state == GREY and reason is not None else refusal)
        elif facts.uncertain and state == TICK:
            maybe = next((n for n in facts.needs if not n.certain), None)          # a join that reads the column only if an uncertain link is the right one
            state, reason = GREY, (facts.unfollowed[0] if facts.unfollowed else Reason(CANNOT_FOLLOW, (("node", maybe.step.node if maybe else occ[0]), ("step", maybe.step.step if maybe else 0))))
        consequences = self._reading_consequences(self._forward_costs(occ))
        if candidate is not None:
            plan = self._plan_consequences(self.place_first[line.place], candidate)
            wrong = self._disagreements(self.place_first[line.place], candidate, consequences)
            if wrong and state == TICK:
                state, reason = GREY, Reason(CONSEQUENCE_DISAGREES, (("reading", tuple(wrong)), ("plan", tuple(plan))))
            consequences = consequences + plan
        return dataclasses.replace(line, notes=tuple(notes), state=state, reason=reason, refusal=refusal, consequences=tuple(consequences),
                                   consequences_checked=candidate is not None)

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


def walk(graph: RecipeGraph, plans: PlanBook, start: Start, *, levels: Iterable[str], kind: str = "filter", candidates: Optional[Mapping[str, PlanBook]] = None) -> Walk:
    """The places of the chosen levels where a step on the column `start.column` of `start.node` can be written, with what each reaches, each with its group.

    `levels` (some of `LEVELS`: source, T1, T2, T3) has no default: the user chooses which levels are offered (owner, D-0355). A place that covers several
    tiers (an empty tier is no place) belongs to each of them. `kind` is `filter` or `drop` (a drop adds the refusal by place and the consequences; `candidates` maps a place to the plan book of the candidate recipe, drop only). Raises
    `ColumnNotFound` for a column the node does not have and `StartPlanFailed` when the engine could not give the plan of the node; every place of the
    chosen levels that the lineage reaches is a line, a note under a line, or a place no plot reads. For many walks on one recipe build `LineageIndex` once."""
    return LineageIndex(graph, plans).walk(start, levels=levels, kind=kind, candidates=candidates)
