"""What the lineage panel of HOME hands to the browser: the plain data of `utils.lineage_data.lineage_of`, with the layout and the words (LINEAGE-VIEW-G, D-0629, D-0634).

Pure: no Shiny, no file, no engine call. The panel is a list (the reader and the text twin of every dot) and a map of dots (one small dot per node, arrows left to right). This
module decides everything the browser only has to draw: the level of each node (the longest path from a root), the position of each dot, the dots that remain when the user asks for
"around my selection" (the lineage back and forward of the chosen place) and the plain sentences of the text area. The browser script (`app/src/www/lineage_view.js`) keeps no rule
of its own except "one chosen place for each independent graph" and the control "all original tables of this group" (the first places of the group); the server checks every choice
again at confirm (`RecipeGraph.chosen_places_problem`), so a case where the two differ is refused there, never accepted.

THE LAYOUT (`layout`): level = the longest path from a node with no arrow in, counted within the nodes shown; inside a level the nodes keep the order of the graph, grouped by
independent graph, then ordered by the mean place of their parents in the level before (a plain barycentre pass, ties by graph order), so that arrows cross little and the same input
gives the same picture. A dot sits at x = level * DX, y = place in the level * DY (all in pixels of the map's own coordinates). No two dots share a position (a test).

THE TIER WORDS and the classes: `tier1` (a table after its tier 1), `tier2` (after its tier 2), `result` (a plot, or a result table nothing is built from). The colour of a class is
in `config/ui/theme.css` section 29; the words and the colours are PROVISIONAL (D-0634: "NOT decided: the exact colours and words").

Consumed by: app/handlers/lineage_handlers.py (the panel), app/tests/test_lineage_view.py. If deleted: HOME's Audit mode has no lineage panel.

# @deps
# provides: function:layout, function:view_data, function:around_ids, function:built_from_sentence, function:node_detail, function:tier_class, constant:DX, constant:DY, constant:MARGIN
# consumes: libs/utils/src/utils/lineage_data.py (Lineage, LineageNode)
# consumed_by: app/handlers/lineage_handlers.py, app/tests/test_lineage_view.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0629, D-0634)
# @end_deps
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from utils.lineage_data import Lineage, LineageNode

DX = 78          # pixels between two levels
DY = 17          # pixels between two dots of one level
MARGIN = 14      # pixels around the map

TIER_WORDS = {"T1": "table after its tier 1", "T2": "table after its tier 2", "T3": "plot (tier 3)", "result": "result table (tier 1), no plot reads it"}


def tier_class(node: LineageNode) -> str:
    """The colour class of a node: `tier1`, `tier2` or `result` (a plot or a leaf table)."""
    if node.kind == "T1":
        return "tier1"
    if node.kind == "T2":
        return "tier2"
    return "result"


def layout(ids: Sequence[str], edges: Sequence[Tuple[str, str]], group_of: Optional[Dict[str, int]] = None) -> Tuple[Dict[str, Tuple[int, int]], Tuple[int, int]]:
    """The place of each node of `ids` (in graph order) as pixels, and the size of the map: `({id: (x, y)}, (width, height))`.

    Only the arrows between nodes of `ids` count. A node with no arrow in is at level 0. Within a level the nodes are grouped by `group_of` (the independent graph, in the order of
    their first node), then ordered by the mean position of their parents (a stable sort: a tie keeps the order of `ids`). Deterministic. An empty `ids` gives an empty map of size (0, 0)."""
    shown = list(ids)
    if not shown:
        return {}, (0, 0)
    inside = set(shown)
    parents: Dict[str, List[str]] = {i: [] for i in shown}
    for p, c in edges:
        if p in inside and c in inside:
            parents[c].append(p)
    level: Dict[str, int] = {}
    for i in shown:                                             # graph order lists a parent before its children
        level[i] = 1 + max((level[p] for p in parents[i]), default=-1)
    order = {i: k for k, i in enumerate(shown)}
    group_rank: Dict[int, int] = {}
    for i in shown:
        g = (group_of or {}).get(i, 0)
        group_rank.setdefault(g, len(group_rank))
    slot: Dict[str, int] = {}
    by_level: Dict[int, List[str]] = {}
    for i in shown:
        by_level.setdefault(level[i], []).append(i)
    for lv in sorted(by_level):
        members = by_level[lv]
        def key(i: str) -> Tuple[int, float, int]:
            mean = sum(slot[p] for p in parents[i]) / len(parents[i]) if parents[i] else float(order[i])
            return (group_rank[(group_of or {}).get(i, 0)], mean, order[i])
        for k, i in enumerate(sorted(members, key=key)):
            slot[i] = k
    pos = {i: (MARGIN + level[i] * DX, MARGIN + slot[i] * DY) for i in shown}
    width = MARGIN * 2 + max(level.values()) * DX
    height = MARGIN * 2 + max(slot.values()) * DY
    return pos, (width, height)


def around_ids(lineage: Lineage, place: str) -> List[str]:
    """The nodes of "around my selection": the lineage back from the place (everything it is built from), the place, and everything built from it (`reach[place].built_from`),
    in graph order. KeyError for an id that is not a node."""
    lineage.node(place)
    parents: Dict[str, List[str]] = {}
    for p, c in lineage.edges:
        parents.setdefault(c, []).append(p)
    back, stack = set(), list(parents.get(place, []))
    while stack:
        cur = stack.pop()
        if cur not in back:
            back.add(cur)
            stack.extend(parents.get(cur, []))
    forward = set(lineage.reach[place].built_from) if place in lineage.reach else set()
    keep = back | forward | {place}
    return [n.id for n in lineage.nodes if n.id in keep]


def _count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def built_from_sentence(lineage: Lineage, place: str) -> str:
    """What is built from a chosen place, in plain words, with the caution that "built from" is not "changed" (PROVISIONAL words)."""
    reach = lineage.reach[place]
    names = {n.id: n for n in lineage.nodes}
    tables = {names[i].name for i in reach.built_from if names[i].kind != "T3"}
    plots = [i for i in reach.built_from if names[i].kind == "T3"]
    if names[place].kind == "T3":
        return "This is a plot: a step written here changes this plot only. Nothing is built from it."
    if not tables and not plots:
        return "Nothing else is built from here: this table is a result of its own, no plot reads it. A step written here changes this table, and no figure changes."
    parts = ([_count(len(tables), "other table", "other tables")] if tables else []) + ([_count(len(plots), "plot", "plots")] if plots else [])
    return (f"Built from here: {' and '.join(parts)}. They are built again from this place; a step does not necessarily change the entity in each of them.")


def node_detail(lineage: Lineage, node: LineageNode, shown_steps: int = 6) -> List[str]:
    """The plain lines of the text area for a node (the same for a hover, a focus and a choice): name and tier, what it is, the columns, the metadata tag, why it cannot be chosen,
    and, for a node that can be chosen, what is built from it with the steps between it and each result on every path. `shown_steps`: how many steps of a path are listed before "..."."""
    names = {n.id: n for n in lineage.nodes}
    lines = [f"{node.name}: {TIER_WORDS[node.kind]}", node.what]
    if node.ui_label:
        lines.append(f"Name in the recipe: {node.ui_label}")
    if node.columns is not None:
        lines.append(f"{len(node.columns)} columns at this place (the engine's plan).")
    elif node.columns_note:
        lines.append(f"Columns: {node.columns_note}.")
    if node.brings_metadata:
        lines.append("+ meta: this table takes the metadata in (the metadata is not drawn and cannot be chosen).")
    if not node.choosable:
        lines.append(f"Cannot be chosen: {node.not_choosable_reason}.")
        return lines
    lines.append(built_from_sentence(lineage, node.id))
    reach = lineage.reach[node.id]
    for result in reach.results:
        target = names[result]
        label = f"{target.name} ({'plot' if target.kind == 'T3' else 'result table'})"
        paths = reach.paths.get(result, ())
        for k, path in enumerate(paths, start=1):
            via = " -> ".join(names[n].name for n in path.nodes) if path.nodes else "itself"
            head = f"To {label}" + (f", path {k} of {len(paths)}" if len(paths) > 1 else "") + f": {via}; "
            if not path.steps:
                lines.append(head + "no step on the way.")
            else:
                shown = [f"{names[s.node].name} #{s.number}: {s.text}" for s in path.steps[:shown_steps]]
                lines.append(head + _count(len(path.steps), "step", "steps") + ": " + "; ".join(shown) + (" ..." if len(path.steps) > shown_steps else ""))
    return lines


def _line_text(node: LineageNode) -> str:
    head = node.name + (f" ({node.ui_label})" if node.ui_label and node.ui_label != node.name else "")
    return f"{head}: {TIER_WORDS[node.kind]}" + (" [+ meta]" if node.brings_metadata else "")


def view_data(lineage: Lineage) -> Dict[str, Any]:
    """The JSON of the panel: nodes (with their words and the dots they keep when the lineage is cut around them), arrows, groups (the independent graphs), and one layout for the
    whole recipe (key "") and one for each node that can be chosen (key: its id; the nodes of "around my selection"). Deterministic and JSON-serialisable."""
    ids = [n.id for n in lineage.nodes]
    group_of = {i: c.id for c in lineage.components for i in c.nodes}
    edges = [list(e) for e in lineage.edges]
    layouts: Dict[str, Dict[str, List[int]]] = {}
    sizes: Dict[str, List[int]] = {}
    pos, size = layout(ids, lineage.edges, group_of)
    layouts[""] = {i: list(p) for i, p in pos.items()}
    sizes[""] = list(size)
    nodes = []
    for n in lineage.nodes:
        around: List[str] = []
        if n.choosable:
            around = around_ids(lineage, n.id)
            p2, s2 = layout(around, lineage.edges, group_of)
            layouts[n.id] = {i: list(p) for i, p in p2.items()}
            sizes[n.id] = list(s2)
        nodes.append({
            "id": n.id, "name": n.name, "kind": n.kind, "cls": tier_class(n), "tier": n.tier, "tier_word": TIER_WORDS[n.kind], "table_kind": n.table_kind,
            "label": n.ui_label, "line": _line_text(n), "meta": n.brings_metadata, "choosable": n.choosable, "reason": n.not_choosable_reason,
            "no_plot": n.kind == "result", "group": group_of[n.id], "detail": node_detail(lineage, n),
            "summary": built_from_sentence(lineage, n.id) if n.choosable else "",
            "built_from": list(lineage.reach[n.id].built_from) if n.choosable else [],
            "around": around,
        })
    groups = [{"id": c.id, "nodes": list(c.nodes), "parents": list(c.parents), "first_places": list(c.first_places)} for c in lineage.components]
    return {"nodes": nodes, "edges": edges, "groups": groups, "layouts": layouts, "sizes": sizes, "metadata_table": lineage.metadata_table}
