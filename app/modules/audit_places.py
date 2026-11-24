"""The places where an audit step can be written for an open plot, and the check of a choice (HOME audit, demo steps 1 to 3).

Pure: no Shiny, no file, no engine call. Input: the recipe graph (`utils.recipe_graph`), the engine's plan book of the ORIGINAL recipe
(`utils.plan_book`, composed by `app.modules.plan_composer`), the open plot and the column(s) the step is about. Output: the lines of the dialog.

WHAT A LINE IS (D-0346: "only distinct tables are lines"). A line is the tier 1 of a table upstream of the plot, or the tier 2 of such a table when a
plot reads it and it has tier-2 steps of its own (a tier 2 with no steps is the same table as its tier 1, so it is not a second line). The plot's own place (its tier 3)
is not a line here (`own_place_line` is: the dialog adds it beside them, so that the rule covers all three tiers). A place is offered only where
the engine's plan HOLDS the column(s) of the step at the end of that place; where the plan failed, the place is listed apart (`unknown`), never guessed.

THE RULE (D-0535, D-0553): the user chooses at most one place on a path; the first places of several original tables may be chosen together. The check is
`RecipeGraph.chosen_places_problem` (written once, in `utils.recipe_graph`), asked here with the extra rule that every chosen place is one of the lines offered.

THE REACH (what the user is told before choosing): the other tables and the plots that lie below the place (`RecipeGraph.below`). "Below" is not "changed"
(G8 of PATHS_AND_DERIVED_AGREED.md): the sentence says "built from it", never "changed".

PROVISIONAL (the builder's choices, not decided by the owner): the words of `reach_sentence` and `line_label`; that the tier-2 line is offered only when the table has tier-2 steps
of its own; that a place whose plan failed is not offered and is returned in `unknown`.

THE NODES THAT ARE WRITTEN AT A PLACE (`place_nodes`, `audit_copy_for`, `nodes_signature`): the audit node of HOME (`session_manager.make_audit_step`) with a `place` (`T1:<table>`,
`T2:<table>` or `T3:<plot>`: the three tiers are ONE mechanism) and the plot it was started from (`started_from`), kept in the bucket `PLACES_BUCKET`. A decision written for several plots or
tables is one node per place, all with the id of the decision (removal by that id removes them all). The audit copy of the recipe (`utils.audit_copy`) is made from them, in the
order they were committed, by the translation of the node into the registered action (`blueprint_arch.t3_translator`, the one translation of the export too); the reason of the
node is the `audit_comment` of the step (D-0329). The copy is the original plus audit steps and nothing else (`add_step` refuses an action that is not a filter or a column drop,
a key dropped where a later join reads it, a place that does not exist).

Consumed by: app/handlers/filter_and_audit_handlers.py (the dialog), app/modules/audit_view.py (the run of the copy), app/tests/test_audit_places.py. If deleted: the dialog offers no place upstream.

# @deps
# provides: function:place_lines, function:own_place_line, function:path_rows, class:PathRow, function:reach_sentence, function:line_label, function:choice_problem, function:plots_below, function:nodes_reaching_plot, function:steps_changing_table, function:own_plot_place, function:place_nodes, function:audit_copy_for, function:nodes_signature, function:place_words, function:place_step_records, function:bake_place_steps, constant:PLACES_BUCKET, class:PlaceLine, class:PlaceLines
# consumes: libs/utils/src/utils/recipe_graph.py (RecipeGraph: places, below, chosen_places_problem, lineage_back), libs/utils/src/utils/plan_book.py (PlanBook, Plan), libs/utils/src/utils/audit_copy.py (start_audit, add_step), libs/utils/src/utils/recipe_tiers.py (collection_body, plot_entry), libs/blueprint_arch/src/blueprint_arch/t3_translator.py (translate_t3_node), app/modules/renamed_keys.py (audit_step_defect, FIX_IN_APP)
# consumed_by: app/handlers/filter_and_audit_handlers.py, app/handlers/audit_stack.py, app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/session_manager.py, app/modules/audit_view.py, app/tests/test_audit_places.py
# doc: .claude/rules/ui_implementation_contract.md#12g, .claude/design/studies/whole_picture_2026-11/PATHS_AND_DERIVED_AGREED.md
# @end_deps
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from blueprint_arch.t3_translator import translate_t3_node
from utils import recipe_tiers
from app.modules.renamed_keys import FIX_IN_APP, audit_step_defect
from utils.audit_copy import AuditCopy, AuditCopyError, add_step, start_audit
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
    depth: int = 0


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
    # the lines read as the path of the lineage: from the original tables down (graph order is parents first), each at its depth on the path
    order = {nid: k for k, nid in enumerate(graph.nodes())}
    lines.sort(key=lambda line: order[line.place])
    offered = {line.place for line in lines}
    depth: Dict[str, int] = {}
    for line in lines:
        above = [depth[a] for a in graph.lineage_back(line.place) if a in offered]
        depth[line.place] = 1 + max(above) if above else 0
    lines = [PlaceLine(l.place, l.table, l.tier, l.kind, l.other_tables, l.plots, l.types, depth[l.place]) for l in lines]
    return PlaceLines(tuple(lines), tuple(unknown))


@dataclass(frozen=True)
class PathRow:
    """One row of the dialog's path: `place` (a node id), `depth` (indent), `derived` (the offered places below it: they follow if it is chosen) and `blocked`
    (the offered places above it: one place on a path, so they cannot be chosen with it)."""
    place: str
    depth: int
    derived: Tuple[str, ...]
    blocked: Tuple[str, ...]


def path_rows(graph: RecipeGraph, lines: Sequence[PlaceLine], own_place: str = "") -> List[PathRow]:
    """The rows of the path, in order, the plot's own place (`own_place`, if given) last; for each row what ticking it derives and blocks. Both come from
    `RecipeGraph.derived_places` and `lineage_back` (one rule, `chosen_places_problem`); the dialog's script only combines them for several ticks
    (the first places of several original tables stay tickable together). Pure; PROVISIONAL name."""
    ids = [l.place for l in lines] + ([own_place] if own_place else [])
    offered = set(ids)
    depth = {l.place: l.depth for l in lines}
    if own_place:
        above = [depth[a] for a in graph.lineage_back(own_place) if a in depth]
        depth[own_place] = 1 + max(above) if above else 0
    rows = []
    for nid in ids:
        derived = tuple(p for p in graph.derived_places([nid]) if p in offered)
        blocked = tuple(p for p in graph.lineage_back(nid) if p in offered)
        rows.append(PathRow(nid, depth[nid], derived, blocked))
    return rows


def plots_below(graph: RecipeGraph, places: Iterable[str]) -> List[str]:
    """The plots that are built from any of the places, each once, in the order of the recipe: the plots below a table's place, and the plot of a `T3:<plot>` place itself
    (its own tier 3 is where it reads). KeyError for an id that is not a node."""
    reached = set()
    for nid in places:
        reached.update(graph.below(nid))
        if graph.node(nid).kind == "T3":
            reached.add(nid)
    return [graph.node(n).name for n in graph.nodes() if n in reached and graph.node(n).kind == "T3"]


def steps_changing_table(graph: RecipeGraph, nodes: Iterable[dict], table: str, tier: str) -> List[dict]:
    """The audit nodes whose place makes the table `table` differ at `tier` (`T1` or `T2`): a step at the tier 1 of the table or of a table it is built from, and (for `T2`) a
    step at its own tier 2. A step at a plot's tier 3 changes no table; a table beside the place is changed by none. In the order given (the export says which steps made the
    audited file differ from the original)."""
    if tier not in ("T1", "T2"):
        raise ValueError("tier is T1 or T2")
    here = f"T1:{table}"
    places = {here} | {n for n in graph.lineage_back(here) if graph.node(n).kind == "T1"}
    if tier == "T2":
        places.add(f"T2:{table}")
    return [n for n in nodes if (n.get("place") or "") in places]


def own_plot_place(plot_id: str) -> str:
    """The place of a plot's own tier 3: `T3:<plot>`."""
    return f"T3:{plot_id}"


def nodes_reaching_plot(graph: RecipeGraph, nodes: Iterable[dict], plot_id: str) -> List[dict]:
    """The audit nodes (committed or pending) whose place the plot is built from: a place of its own tier 3, or a table place above it. In the order given; a node whose place the
    graph does not have reaches no plot."""
    plot_node = own_plot_place(plot_id)
    found: List[dict] = []
    for node in nodes:
        place = node.get("place") or ""
        if place == plot_node or (graph.has_node(place) and plot_node in graph.below(place)):
            found.append(node)
    return found


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


def own_place_line(plot_id: str) -> str:
    """The words of the line for the plot's own tier 3 in the dialog's list of places (PROVISIONAL words)."""
    return f"Plot {plot_id} (tier 3): only this plot is built from it"


def choice_problem(graph: RecipeGraph, offered: Sequence[PlaceLine], chosen: Iterable[str], extra_offered: Iterable[str] = ()) -> Optional[str]:
    """None when the chosen places may be written in one step, else ONE plain sentence. Nothing chosen is a problem here. Every chosen place must be a line offered (or one of
    `extra_offered`, the plot's own place); the rest of the rule is `RecipeGraph.chosen_places_problem`, the same for a table and for a plot below it."""
    ids = list(dict.fromkeys(chosen))
    if not ids:
        return "Choose at least one place."
    offered_ids = {line.place for line in offered} | set(extra_offered)
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
    recipe, for the rule of a key drop (`add_step`). Raises `AuditCopyError` (a step the app cannot apply: a type it does not know or a step that lacks what it needs, see `renamed_keys.audit_step_defect`; a place that does not exist, an action an audit may not use, a key dropped where a later join reads
    it, a node without a reason) or `UntranslatableNode` (a node that has no registered action), each with a plain sentence, and builds nothing then."""
    listed = list(nodes)
    label = hashlib.sha256("|".join(str(n.get("id")) for n in listed).encode("utf-8")).hexdigest()[:8]
    audit = start_audit(original_raw, label)
    for number, node in enumerate(listed, start=1):
        defect = audit_step_defect(node)
        if defect:                                   # a step the app cannot apply is refused with a plain message, never skipped (the one rule of the list and the files)
            reason = f', reason: "{node["reason"]}"' if node.get("reason") else ""
            raise AuditCopyError(f"The audit step {number} (id {node.get('id', '?')}{reason}) at {place_words(node.get('place', ''))} is refused: {defect}. Fix: {FIX_IN_APP}.")
        for step in translate_t3_node(node):
            add_step(audit, node["place"], step, node.get("reason") or "", plans)
    return audit


# ---------------------------------------------------------------------------------------------------------------------
# What the export says and writes of these steps (demo step 4)
# ---------------------------------------------------------------------------------------------------------------------


def place_words(place: str) -> str:
    """A place in plain words: `T1:ResFinder` is "Table ResFinder (tier 1)", `T3:amr_heatmap` is "Plot amr_heatmap (tier 3)"."""
    tier, _, name = (place or "").partition(":")
    if tier in ("T1", "T2") and name:
        return f"Table {name} (tier {tier[1:]})"
    return f"Plot {name} (tier 3)" if tier == "T3" and name else str(place)


def t3_file_sentence(folder: str, plot_id: str, audited: bool, recipe_steps: bool) -> str:
    """One plain sentence for a `T3_data_<plot>.tsv` file of the export: which table it is. A plot is drawn from this table, so it is part of the Result; a recipe's own tier-3 steps are
    never called audit steps (PROVISIONAL words). `audited`: an audit step reaches the plot; `recipe_steps`: the recipe writes tier-3 steps of its own for the plot."""
    path = f"{folder}/T3_data_{plot_id}.tsv"
    if audited and recipe_steps:
        what = "the table of this plot after its own steps of the recipe and after the audit steps"
    elif audited:
        what = "the table of this plot after the audit steps (the recipe writes no tier-3 step of its own for this plot)"
    else:
        what = "the table of this plot after its own steps of the recipe (no audit step reaches this plot; this is the Result, not audited content)"
    return f"{path}: {what}."


def place_step_records(graph: RecipeGraph, nodes: Iterable[dict]) -> List[Dict[str, Any]]:
    """One record per committed node written at a place, in commit order, for `t3_steps.yaml`, the README and the report: id, place (as a node id and in words), the plot it was
    started from, the action it is (`node_type`) with its parameters, the reason, the date and the plots built from the place (`plots`). A place the graph does not have lists no plot."""
    records: List[Dict[str, Any]] = []
    for node in nodes:
        place = node.get("place") or ""
        records.append({
            "id": node.get("id"), "place": place, "place_words": place_words(place), "started_from": (node.get("started_from") or "").removeprefix("subtab_"),
            "action": node.get("node_type", "unknown"), "params": dict(node.get("params") or {}), "reason": node.get("reason", ""),
            "committed_at": node.get("created_at", ""),
            "plots": plots_below(graph, [place]) if graph.has_node(place) else [],
        })
    return records


def bake_place_steps(raw: dict, nodes: Iterable[dict]) -> dict:
    """A deep copy of the recipe in which each node written at a place is a plain step at the END of that tier (`tier1.steps` or `tier2.steps` of its table, `tier3.steps` of its plot), so
    that the recipe alone, run by the engine with no audit machinery, builds the audited tables and plots (the reproducibility part of the export). The table or plot says so in its `comment`, with
    the ids of the audit steps (the reasons are in `t3_steps.yaml`). The argument is not changed; the loader's root-level `plots` mirror is left out. Raises `UntranslatableNode` for a node with no registered action and `KeyError` for a table or plot
    the recipe does not have."""
    baked = copy.deepcopy(raw)
    # The loader's own root-level `plots` is an internal mirror of `analysis_groups` (config_loader.py); a recipe written with it does not load again (a root `plots:` is refused),
    # so the baked recipe, which is written to a file, never carries it. (The fork of a join that this replaces dropped it too.)
    baked.pop("plots", None)
    written: Dict[Tuple[str, str], List[str]] = {}
    for node in nodes:
        tier, name = (node.get("place") or "").split(":", 1)
        tier_key = {"T1": "tier1", "T2": "tier2", "T3": "tier3"}[tier]
        body = _body_of(baked, tier, name)
        held = body.get(tier_key) if isinstance(body.get(tier_key), dict) else {}
        body[tier_key] = {**held, "steps": list(held.get("steps") or []) + translate_t3_node(node)}
        written.setdefault((f"{tier}:{name}", tier_key), []).append(str(node.get("id")))
    for (place, tier_key), ids in written.items():
        tier, name = place.split(":", 1)
        body = _body_of(baked, tier, name)
        note = f"Written by the export: the audit steps {', '.join(ids)} are added at the end of {tier_key}."
        body["comment"] = f"{body['comment']} {note}" if body.get("comment") else note
    return baked


def _body_of(recipe: dict, tier: str, name: str) -> dict:
    """The table, join or plot entry (the live dictionary of `recipe`) that a place names; KeyError in plain words when the recipe has none."""
    if tier == "T3":
        body = recipe_tiers.plot_entry(recipe, name)
        if not isinstance(body, dict):
            raise KeyError(f"the recipe has no plot '{name}'")
        return body
    body = recipe_tiers.collection_body(recipe, name)
    if not isinstance(body, dict):
        raise KeyError(f"the recipe has no table or join '{name}'")
    return body
