# engine: python-polars (reads the engine's own type names from a plan book; no Polars call)
"""The places where an audit step can be written for an open plot, and the check of a choice (HOME audit, demo steps 1 to 3).

Pure: no Shiny, no file, no engine call. Input: the recipe graph (`utils.recipe_graph`), the engine's plan book of the ORIGINAL recipe
(`utils.plan_book`, composed by `app.modules.plan_composer`), the open plot and the column(s) the step is about. Output: the lines of the dialog.

WHAT A LINE IS (D-0346: "only distinct tables are lines"). A line is the tier 1 of a table upstream of the plot, or the tier 2 of such a table when a
plot reads it and it has tier-2 steps of its own (a tier 2 with no steps is the same table as its tier 1, so it is not a second line). The plot's own place (its tier 3)
is not a line here: "This plot only" is the plot's own place and is written as before (`audited_frame` on the table the plot reads). A place is offered only where
the engine's plan HOLDS the column(s) of the step at the end of that place; where the plan failed, the place is listed apart (`unknown`), never guessed.

THE RULE (D-0535, D-0553): the user chooses at most one place on a path; the first places of several original tables may be chosen together. The check is
`RecipeGraph.chosen_places_problem` (written once, in `utils.recipe_graph`), asked here with the extra rule that every chosen place is one of the lines offered.

THE REACH (what the user is told before choosing): the other tables and the plots that lie below the place (`RecipeGraph.below`). "Below" is not "changed"
(G8 of PATHS_AND_DERIVED_AGREED.md): the sentence says "built from it", never "changed".

PROVISIONAL (the builder's choices, not decided by the owner): the words of `reach_sentence` and `line_label`; that the tier-2 line is offered only when the table has tier-2 steps
of its own; that a place whose plan failed is not offered and is returned in `unknown`.

THE NODES THAT ARE WRITTEN AT A PLACE (`place_nodes`, `audit_copy_for`, `nodes_signature`): the audit node of HOME (`session_manager.make_audit_step`) with a `place` (`T1:<table>` or
`T2:<table>`) and the plot it was started from (`started_from`), kept in the bucket `PLACES_BUCKET`. The audit copy of the recipe (`utils.audit_copy`) is made from them, in the
order they were committed, by the translation of the node into the registered action (`blueprint_arch.t3_translator`, the one translation of the export too); the reason of the
node is the `audit_comment` of the step (D-0329). The copy is the original plus audit steps and nothing else (`add_step` refuses an action that is not a filter or a column drop,
a key dropped where a later join reads it, a place that does not exist).

Consumed by: app/handlers/filter_and_audit_handlers.py (the dialog), app/modules/audit_view.py (the run of the copy), app/tests/test_audit_places.py. If deleted: the dialog offers no place upstream.

# @deps
# provides: function:place_lines, function:reach_sentence, function:line_label, function:choice_problem, function:plots_below, function:place_nodes, function:audit_copy_for, function:nodes_signature, constant:PLACES_BUCKET, class:PlaceLine, class:PlaceLines
# consumes: libs/utils/src/utils/recipe_graph.py (RecipeGraph: places, below, chosen_places_problem, lineage_back), libs/utils/src/utils/plan_book.py (PlanBook, Plan), libs/utils/src/utils/audit_copy.py (start_audit, add_step), libs/blueprint_arch/src/blueprint_arch/t3_translator.py (translate_t3_node)
# consumed_by: app/handlers/filter_and_audit_handlers.py, app/modules/audit_view.py, app/tests/test_audit_places.py
# doc: .claude/rules/ui_implementation_contract.md#12g, .claude/design/studies/whole_picture_2026-11/PATHS_AND_DERIVED_AGREED.md
# @end_deps
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from blueprint_arch.t3_translator import translate_t3_node
from utils.audit_copy import AuditCopy, add_step, start_audit
from utils.plan_book import Plan, PlanBook
from utils.recipe_graph import RecipeGraph

# The bucket of `home_state["t3_audit_steps_by_plot"]` that holds the audit steps written at a place upstream of a plot (a node with a `place`): one step at one
# place is ONE node here, not one copy per plot. Every plot-level reader asks the bucket of its own plot, so none of them sees these nodes by mistake.
PLACES_BUCKET = "__places__"


@dataclass(frozen=True)
class PlaceLine:
    """One line of the dialog: a place upstream of the plot that holds every column of the step.

    place: the node id (`T1:<table>` or `T2:<table>`). table: the table id. tier: `T1` or `T2`. kind: `original` (a source table) or `joined`.
    other_tables: the other tables (tier 1 nodes) below it, in graph order. plots: the plots below it, in the order of the recipe.
    types: the engine's type of each column at the end of the place, in the order of the columns asked."""
    place: str
    table: str
    tier: str
    kind: str
    other_tables: Tuple[str, ...]
    plots: Tuple[str, ...]
    types: Tuple[str, ...]


@dataclass(frozen=True)
class PlaceLines:
    """The result: `lines` (offered, in graph order) and `unknown` (places upstream whose plan the engine could not give, with its sentence)."""
    lines: Tuple[PlaceLine, ...]
    unknown: Tuple[Tuple[str, str], ...] = ()


def _holds(plan, columns: Sequence[str]) -> Optional[Tuple[str, ...]]:
    """The types of the columns when the plan holds all of them, else None (also None for a failure, which the caller sees apart)."""
    if not isinstance(plan, Plan) or not all(plan.has(c) for c in columns):
        return None
    return tuple(plan.type_of(c) or "" for c in columns)


def place_lines(graph: RecipeGraph, plans: PlanBook, plot_id: str, columns: Iterable[str]) -> PlaceLines:
    """The places upstream of `plot_id` where a step on `columns` can be written, each with its reach. KeyError for a plot the recipe does not have.

    Only tier 1 and tier 2 places that are places of the graph (a tier 2 that no plot reads is no place) and, for a tier 2, only when its table has tier-2 steps of
    its own (otherwise it is its tier 1 again). The plot's own place is not a line."""
    wanted = [c for c in columns if c]
    plot_node = f"T3:{plot_id}"
    graph.node(plot_node)
    allowed = set(graph.places())
    lines: List[PlaceLine] = []
    unknown: List[Tuple[str, str]] = []
    for nid in graph.lineage_back(plot_node):
        node = graph.node(nid)
        if node.kind not in ("T1", "T2") or nid not in allowed:
            continue
        if node.kind == "T2" and not node.steps:
            continue                                             # the same table as its tier 1 (D-0346)
        plan = plans.get(nid, len(node.steps))
        types = _holds(plan, wanted)
        if types is None:
            if not isinstance(plan, Plan):
                unknown.append((nid, getattr(plan, "sentence", "")))
            continue
        below = graph.below(nid)
        other_tables = tuple(graph.node(n).name for n in below if graph.node(n).kind == "T1")
        plots = tuple(graph.node(n).name for n in below if graph.node(n).kind == "T3")
        lines.append(PlaceLine(nid, node.name, node.kind, "original" if node.collection_kind == "schema" else "joined", other_tables, plots, types))
    return PlaceLines(tuple(lines), tuple(unknown))


def plots_below(graph: RecipeGraph, places: Iterable[str]) -> List[str]:
    """The plots that lie below any of the places, each once, in the order of the recipe. KeyError for an id that is not a node."""
    reached = set()
    for nid in places:
        reached.update(graph.below(nid))
    return [graph.node(n).name for n in graph.nodes() if n in reached and graph.node(n).kind == "T3"]


def line_label(line: PlaceLine) -> str:
    """The name of a line: the table and its tier in plain words ("Table ResFinder (tier 1)")."""
    return f"Table {line.table} (tier {line.tier[1]})"


def _count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def reach_sentence(line: PlaceLine) -> str:
    """What lies below the line, in plain words: "6 other tables and 9 plots are built from it". "Below" is not "changed": the sentence says built from."""
    tables, plots = len(line.other_tables), len(line.plots)
    if not tables and not plots:
        return "nothing else is built from it."
    parts = ([_count(tables, "other table", "other tables")] if tables else []) + ([_count(plots, "plot", "plots")] if plots else [])
    return " and ".join(parts) + (" is" if tables + plots == 1 else " are") + " built from it."


def choice_problem(graph: RecipeGraph, offered: Sequence[PlaceLine], chosen: Iterable[str]) -> Optional[str]:
    """None when the chosen places may be written in one step, else ONE plain sentence. Nothing chosen is a problem here (the caller offers
    the plot's own place for that). Every chosen place must be a line offered; the rest of the rule is `RecipeGraph.chosen_places_problem`."""
    ids = list(dict.fromkeys(chosen))
    if not ids:
        return "Choose at least one table."
    offered_ids = {line.place for line in offered}
    for nid in ids:
        if nid not in offered_ids:
            return f"'{nid}' is not one of the places offered for this step."
    return graph.chosen_places_problem(ids)


# ---------------------------------------------------------------------------------------------------------------------
# The nodes written at a place, and the audit copy they make
# ---------------------------------------------------------------------------------------------------------------------


def place_nodes(by_plot: Dict[str, List[dict]]) -> List[dict]:
    """The committed audit nodes written at a place (the bucket `PLACES_BUCKET` of the per-plot stacks), the ones that are still active, in the order they were committed."""
    return [n for n in (by_plot or {}).get(PLACES_BUCKET, []) if n.get("place") and n.get("active", True)]


def nodes_signature(nodes: Iterable[dict]) -> Tuple[Any, ...]:
    """What decides the DATA of the audit copy: for each node its id, place, kind and parameters (not the reason, not the date). Two lists with the same signature build the same tables."""
    return tuple((n.get("id"), n.get("place"), n.get("node_type"), json.dumps(n.get("params") or {}, sort_keys=True, default=str)) for n in nodes)


def audit_copy_for(original_raw: dict, nodes: Iterable[dict], plans: Optional[PlanBook] = None) -> AuditCopy:
    """The audit copy of a recipe that holds one audit step for each action of each node, at the place of the node, in the order of the list.

    The 8 characters of the ids of the steps come from the ids of the nodes (a label, in no key: `audit_copy.start_audit`). `plans` is the engine's plan book of the ORIGINAL
    recipe, for the rule of a key drop (`add_step`). Raises `AuditCopyError` (a place that does not exist, an action an audit may not use, a key dropped where a later join reads
    it, a node without a reason) or `UntranslatableNode` (a node that has no registered action), each with a plain sentence, and builds nothing then."""
    listed = list(nodes)
    label = hashlib.sha256("|".join(str(n.get("id")) for n in listed).encode("utf-8")).hexdigest()[:8]
    audit = start_audit(original_raw, label)
    for node in listed:
        for step in translate_t3_node(node):
            add_step(audit, node["place"], step, node.get("reason") or "", plans)
    return audit
