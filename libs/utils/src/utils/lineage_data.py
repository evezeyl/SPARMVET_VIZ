"""The lineage of a recipe as plain data: the nodes, the arrows, what is built from each place, the steps between a place and each result (LINEAGE-DATA-FUNCTION).

One pure function, `lineage_of(raw, plans=None)`, for any later drawing (the view G of HOME, D-0629, D-0634). No Shiny, no file, no engine call: it reads the resolved recipe
(through `utils.recipe_graph`, the one graph of the app) and, for the columns, the engine's plan book that the CALLER composed (`app/modules/plan_composer.compose_plan_book`).
The columns are never guessed from the graph (D-0630): a node holds the plan's (name, type) pairs, or says in `columns_note` why it does not.

WHAT IS DRAWN (D-0631):
- the graph starts at the tier 1 of the original tables. The original file (`DS:<table>`) is never a place and is not a node. The metadata table (`metadata_schema`) is not a node and is
  not a place (D-0632); a table whose ingredients or steps use it carries `brings_metadata` and has no arrow from it.
- a node is `T1` (a table after its tier 1; an original table or a joined one: `table_kind`), `T2` (after its tier 2, only when the table has tier-2 steps of its own: an empty tier is the
  same table as the one before it, so it is no node and the arrow goes from the tier 1 straight on, as `audit_places.place_lines` does, D-0346), `T3` (a plot, after its own tier 3), or
  `result` (the tier 1 of a table that nothing is built from: no other table reads it and no plot reads it; a leaf that can be chosen as a place, D-0627, D-0630).
- a tier 2 with steps that no plot reads is drawn but is not a place (the recipe check refuses such steps, S07 for a table and J14 for a join: the steps would run nowhere); its
  `not_choosable_reason` says so.
- arrows run from parent to child. A joined table has ALL its parents (every ingredient except the metadata).

FOR EACH PLACE (a node that can be chosen): `reach[place]` holds the nodes built from it (`built_from`), the results below it (`results`: the plots and the leaf tables; a plot or a leaf is its own
result) and, for each result, EVERY path from the place to it with the steps that run on the way (the steps of the nodes after the place; a join has two parents, so there can be several paths).
Each step is a short readable line (the action and the essential of its parameters).

INDEPENDENT GRAPHS: `components` lists the connected parts of the drawn graph, each with its original parents (`parents`: the nodes with no arrow in) and `first_places` (the ones among them that
can be chosen): "all parents" of the view is one chosen place on each of those (D-0634).

PROVISIONAL (the builder's choices, not decided by the owner): the words of `what` and of the not-choosable reasons; that a leaf is any tier 1 with no child, original or joined (`table_kind` says which);
that a tier 2 with steps that no plot reads is drawn and not choosable; that a plot that targets the metadata table is a node with no arrow in; that the number of paths is not capped.

Consumed by: app/tests/test_lineage_data.py, libs/utils/tests/test_lineage_data.py (the view G is the next task). If deleted: no view of the lineage can be drawn from data.

# @deps
# provides: function:lineage_of, function:step_line, class:Lineage, class:LineageNode, class:StepLine, class:LinePath, class:PlaceReach, class:Component
# consumes: libs/utils/src/utils/display_names.py (shown_names: the name of each node), libs/utils/src/utils/recipe_graph.py (build_graph, RecipeGraph), libs/utils/src/utils/recipe_tiers.py (METADATA_SCHEMA, collection_body, plot_entry), libs/utils/src/utils/plan_book.py (PlanBook, Plan, PlanFailure), libs/utils/src/utils/join_keys.py (JOIN_ACTIONS, key_columns), libs/utils/src/utils/action_names.py
# consumed_by: libs/utils/tests/test_lineage_data.py
# doc: .claude/knowledge/decision_ledger.md (D-0627, D-0629 to D-0634), .claude/rules/ui_implementation_contract.md#2
# @end_deps
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from utils import action_names, display_names, join_keys, recipe_tiers
from utils.plan_book import Plan, PlanBook, PlanBookIncomplete, PlanFailure
from utils.recipe_graph import RecipeGraph, build_graph

METADATA = recipe_tiers.METADATA_SCHEMA
_SHORT = 48


@dataclass(frozen=True)
class LineageNode:
    """One node. id: the graph's id (`T1:<table>`, `T2:<table>`, `T3:<plot>`). kind: `T1`, `T2`, `T3` or `result` (a leaf table). tier: 1, 2 or 3. name: the table or plot id.
    table_kind: `original`, `joined` or `plot`. what: one plain sentence. ui_label, description: the recipe's own words for the table or plot ("" when it gives none).
    choosable: whether an audit step can be written here; if not, `not_choosable_reason`. brings_metadata: a joined table that takes the metadata in (no arrow is drawn for it).
    shown: the name the app shows for the table or plot (`utils.display_names`: the ui_label, else the id with spaces; the id in brackets when two would be equal). n_steps: the steps of this node's own tier. columns: the engine's (name, type) pairs after the node's steps, or None; then `columns_note` says why (never guessed from the graph)."""
    id: str
    kind: str
    tier: int
    name: str
    table_kind: str
    what: str
    ui_label: str
    description: str
    choosable: bool
    not_choosable_reason: str
    brings_metadata: bool
    n_steps: int
    columns: Optional[Tuple[Tuple[str, str], ...]]
    columns_note: str
    shown: str


@dataclass(frozen=True)
class StepLine:
    """One step that runs on a path: the node it is written at, its number there (1-based, as in the recipe's list) and a short readable line."""
    node: str
    number: int
    text: str


@dataclass(frozen=True)
class LinePath:
    """One path from a place to a result: the nodes after the place (the result last; empty when the place is the result) and the steps that run on it, in order."""
    nodes: Tuple[str, ...]
    steps: Tuple[StepLine, ...]


@dataclass(frozen=True)
class PlaceReach:
    """What is built from a place: the nodes below it, the results among them (the place itself when it is a plot or a leaf) and every path to each result."""
    place: str
    built_from: Tuple[str, ...]
    results: Tuple[str, ...]
    paths: Mapping[str, Tuple[LinePath, ...]]


@dataclass(frozen=True)
class Component:
    """An independent graph: its nodes, its original parents (the nodes with no arrow in) and the ones of them that can be chosen (the first places of "all parents")."""
    id: int
    nodes: Tuple[str, ...]
    parents: Tuple[str, ...]
    first_places: Tuple[str, ...]


@dataclass(frozen=True)
class Lineage:
    """The lineage of a recipe. nodes: in graph order. edges: (parent, child) pairs. reach: for every choosable node. metadata_table: the id of the metadata table the recipe has, or None
    (it is not drawn). `to_dict()` is JSON-serialisable."""
    nodes: Tuple[LineageNode, ...]
    edges: Tuple[Tuple[str, str], ...]
    reach: Mapping[str, PlaceReach]
    components: Tuple[Component, ...]
    metadata_table: Optional[str]

    def node(self, node_id: str) -> LineageNode:
        """The node of an id; KeyError with a plain message when the lineage has none."""
        for item in self.nodes:
            if item.id == node_id:
                return item
        raise KeyError(f"no node {node_id!r} in the lineage")

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


def _short(value: Any) -> str:
    text = value if isinstance(value, str) else repr(value)
    return text if len(text) <= _SHORT else text[: _SHORT - 3] + "..."


def _names(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(_short(v) for v in value[:4]) + (", ..." if len(value) > 4 else "")
    return _short(value)


def step_line(step: Any) -> str:
    """A short readable line for one step: the action and the essential of its parameters (a join: the kind, the other table and the keys; a filter: the column, the operator and the value;
    a select or a drop: the columns; any other: up to two plain parameters). A step that is not a mapping with an action is said so, never hidden."""
    if not isinstance(step, dict) or not isinstance(step.get("action"), str):
        return "a step the app cannot read (no action)"
    action = step["action"]
    if action in join_keys.JOIN_ACTIONS:
        left, right = join_keys.key_columns(step)
        keys = ", ".join(left) if left == right else f"{', '.join(left)} = {', '.join(right)}"
        how = step.get("how")
        return f"{action}: {how + ' ' if how else ''}with {step.get('right_ingredient', '?')}" + (f" on {keys}" if left else "")
    if action == action_names.FILTER:
        return f"{action}: {step.get('column', '?')} {step.get('op', '?')} {_names(step.get('value'))}"
    if action == action_names.SELECT:
        return f"{action}: keeps {_names(step.get('exprs'))}"
    if action == action_names.DROP:
        return f"{action}: removes {_names(step.get('columns'))}"
    shown = [f"{k}={_names(v)}" for k, v in step.items() if k not in ("action", "comment", "id", "audit_comment") and isinstance(v, (str, int, float, bool, list))][:2]
    return f"{action}" + (f": {', '.join(shown)}" if shown else "")


def _count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def _columns_of(plans: Optional[PlanBook], node_id: str, n_steps: int) -> Tuple[Optional[Tuple[Tuple[str, str], ...]], str]:
    if plans is None:
        return None, "no plan was given, so the columns are not known (they are never guessed from the recipe)"
    try:
        plan = plans.get(node_id, n_steps)
    except PlanBookIncomplete:
        return None, "the plan book has no entry for this place, so the columns are not known"
    if isinstance(plan, Plan):
        return plan.columns, ""
    if isinstance(plan, PlanFailure):
        return None, f"the engine could not give the columns here: {plan.sentence}"
    return None, "the plan of this place is not readable"


def lineage_of(raw: Union[dict, RecipeGraph], plans: Optional[PlanBook] = None) -> Lineage:
    """The lineage of a resolved recipe (a dictionary, as `utils.recipe_graph.build_graph` reads it), with the engine's plan book for the columns (None: the columns are not given and
    each node says so). Raises `RecipeGraphError` for a recipe that cannot be drawn as a graph. Pure and deterministic: the same input gives the same output in the same order."""
    if isinstance(raw, RecipeGraph):
        raise TypeError("lineage_of reads the resolved recipe (a dictionary): it also needs the labels and the descriptions the graph does not keep")
    graph = build_graph(raw)
    all_ids = graph.nodes()
    hidden = {nid for nid in all_ids if graph.node(nid).kind == "DS" or (graph.node(nid).kind in ("T1", "T2") and graph.node(nid).name == METADATA)}
    has_metadata = f"T1:{METADATA}" in all_ids

    def drawn(nid: str) -> bool:
        node = graph.node(nid)
        return nid not in hidden and (node.kind != "T2" or bool(node.steps))

    def resolve(parent: str) -> Optional[str]:
        """The drawn node a parent stands for: itself, the tier 1 when its tier 2 is empty, None when it is not drawn (a file, the metadata)."""
        if parent in hidden:
            return None
        node = graph.node(parent)
        if node.kind == "T2" and not node.steps:
            return resolve(graph.parents(parent)[0])
        return parent

    ids = [nid for nid in all_ids if drawn(nid)]
    parents: Dict[str, List[str]] = {}
    for nid in ids:
        found = [resolve(p) for p in graph.parents(nid)]
        parents[nid] = list(dict.fromkeys(p for p in found if p is not None))
    children: Dict[str, List[str]] = {nid: [] for nid in ids}
    for nid in ids:
        for p in parents[nid]:
            children[p].append(nid)

    def brings_metadata(nid: str) -> bool:
        node = graph.node(nid)
        if node.kind != "T1" or node.collection_kind != "join":
            return False
        if METADATA in [graph.node(p).name for p in graph.parents(nid) if graph.node(p).kind == "T1"]:
            return True
        return any(isinstance(s, dict) and s.get("right_ingredient") == METADATA for s in node.steps)

    names = display_names.shown_names(raw)

    def shown_of(nid: str) -> str:
        g = graph.node(nid)
        return display_names.shown_name(names, display_names.PLOT if g.kind == "T3" else display_names.TABLE, g.name)

    nodes: List[LineageNode] = []
    for nid in ids:
        node = graph.node(nid)
        n = len(node.steps)
        columns, note = _columns_of(plans, nid, n)
        body = recipe_tiers.plot_entry(raw, node.name) if node.kind == "T3" else recipe_tiers.collection_body(raw, node.name)
        label = str(body.get("ui_label") or "") if isinstance(body, dict) else ""
        text = str(body.get("description") or "") if isinstance(body, dict) else ""
        choosable, reason = True, ""
        if node.kind == "T3":
            kind, table_kind, tier = "T3", "plot", 3
            target = shown_of(graph.parents(nid)[0])
            what = f"Result data of plot {shown_of(nid)} (T3): it reads table {target}" + (f" and has {_count(n, 'step', 'steps')} of its own." if n else " as it is.")
        else:
            table_kind = "original" if node.collection_kind == "schema" else "joined"
            tier = 1 if node.kind == "T1" else 2
            kind = node.kind
            if node.kind == "T1" and not children[nid]:
                kind = "result"
            steps_words = _count(n, "step", "steps") if n else "no step"
            if node.kind == "T2":
                what = f"Table {shown_of(nid)} after its tier 2 ({steps_words})."
                if not node.read_by_plot:
                    choosable, reason = False, "no plot reads this tier 2, so its steps run nowhere and no audit step can be written here (recipe check S07 for a table, J14 for a join)"
            elif table_kind == "original":
                what = f"Original table {shown_of(nid)}, after its tier 1 ({steps_words})."
            else:
                made_of = [shown_of(p) for p in graph.parents(nid) if graph.node(p).name != METADATA]
                what = f"Table {shown_of(nid)}, built by joining {', '.join(made_of) or 'no other table'}" + (" and the metadata" if brings_metadata(nid) else "") + f", after its tier 1 ({steps_words})."
            if kind == "result":
                what += " Nothing is built from it: it is a result table of its own."
        nodes.append(LineageNode(nid, kind, tier, node.name, table_kind, what, label, text, choosable, reason, brings_metadata(nid), n, columns, note, shown_of(nid)))
    by_id = {n.id: n for n in nodes}
    edges = tuple((p, nid) for nid in ids for p in parents[nid])

    def below(nid: str) -> List[str]:
        seen, stack = set(), list(children[nid])
        while stack:
            cur = stack.pop()
            if cur not in seen:
                seen.add(cur)
                stack.extend(children[cur])
        return [x for x in ids if x in seen]

    def is_result(nid: str) -> bool:
        return by_id[nid].kind in ("T3", "result")

    def paths_to(place: str, result: str) -> List[List[str]]:
        found: List[List[str]] = []

        def walk(cur: str, trail: List[str]) -> None:
            if cur == result:
                found.append(trail)
                return
            for child in children[cur]:
                walk(child, trail + [child])

        walk(place, [])
        return found

    reach: Dict[str, PlaceReach] = {}
    for nid in ids:
        if not by_id[nid].choosable:
            continue
        built = below(nid)
        results = tuple(([nid] if is_result(nid) else []) + [x for x in built if is_result(x)])
        found: Dict[str, Tuple[LinePath, ...]] = {}
        for result in results:
            lines = []
            for trail in paths_to(nid, result):
                steps = tuple(StepLine(n, k, step_line(s)) for n in trail for k, s in enumerate(graph.node(n).steps, start=1))
                lines.append(LinePath(tuple(trail), steps))
            found[result] = tuple(lines)
        reach[nid] = PlaceReach(nid, tuple(built), results, found)

    # the independent graphs: connected parts of the drawn graph, in graph order
    group = {nid: nid for nid in ids}

    def find(x: str) -> str:
        while group[x] != x:
            group[x] = group[group[x]]
            x = group[x]
        return x

    for p, c in edges:
        group[find(p)] = find(c)
    parts: Dict[str, List[str]] = {}
    for nid in ids:
        parts.setdefault(find(nid), []).append(nid)
    components = []
    for k, members in enumerate(parts.values()):
        roots = tuple(n for n in members if not parents[n])
        components.append(Component(k, tuple(members), roots, tuple(n for n in roots if by_id[n].choosable)))
    return Lineage(tuple(nodes), edges, reach, tuple(components), METADATA if has_metadata else None)
