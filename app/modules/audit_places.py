"""The audit steps written at a place (HOME audit): the node, the bucket, the audit copy they make, the words of a place and the records of the export.

Pure: no Shiny, no file, no engine call.

FLOW-3 (2026-11-27): the dialog that offered the places of a step as tick lines ("At a table this plot is built from", with its path, its reach and its choice rule) is gone with the pop-up
(D-0662, D-0675): the places are chosen in "Path of the data" (`lineage_view`, `trial_handlers`), and the rule of places (at most one place on a path, the first places of several original tables
together) is `RecipeGraph.chosen_places_problem`, written once in `utils.recipe_graph`.

THE NODES THAT ARE WRITTEN AT A PLACE (`place_nodes`, `audit_copy_for`, `nodes_signature`): the audit node of HOME (`session_manager.make_audit_step`) with a `place` (`T1:<table>`,
`T2:<table>` or `T3:<plot>`: the three tiers are ONE mechanism) and the plot it was started from (`started_from`), kept in ONE flat list (`home_state["audit_pipeline"]`, FLOW-3 stage B; PROVISIONAL name). A decision written for several plots or
tables is one node per place, all with the id of the decision (removal by that id removes them all). The audit copy of the recipe (`utils.audit_copy`) is made from them, in the
order they were committed, by the translation of the node into the registered action (`blueprint_arch.t3_translator`, the one translation of the export too); the reason of the
node is the `audit_comment` of the step (D-0329). The copy is the original plus audit steps and nothing else (`add_step` refuses an action that is not a filter or a column drop,
a key dropped where a later join reads it, a place that does not exist).

Consumed by: app/handlers/audit_stack.py, app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/audit_view.py (the run of the copy), app/tests/test_audit_places.py. If deleted: no audit step can be written at a place.

# @deps
# provides: function:place_line, function:plots_below, function:nodes_reaching_plot, function:steps_changing_table, function:own_plot_place, function:place_nodes, function:audit_copy_for, function:nodes_signature, function:place_words, function:place_step_records, function:bake_place_steps, function:audit_recipe_of, function:audit_recipe_sentence, function:t3_file_sentence, function:nodes_reaching_node, class:PlaceLine, class:PlaceLines
# consumes: libs/utils/src/utils/display_names.py (place_line), libs/utils/src/utils/recipe_graph.py (RecipeGraph: places, below, chosen_places_problem, lineage_back), libs/utils/src/utils/plan_book.py (PlanBook, Plan), libs/utils/src/utils/audit_copy.py (start_audit, add_step), libs/utils/src/utils/recipe_tiers.py (collection_body, plot_entry), libs/blueprint_arch/src/blueprint_arch/t3_translator.py (translate_t3_node), app/modules/renamed_keys.py (audit_step_defect, FIX_IN_APP)
# consumed_by: app/handlers/audit_stack.py, app/handlers/trial_handlers.py, app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/session_manager.py, app/modules/audit_view.py, app/tests/test_audit_places.py
# doc: .claude/rules/ui_implementation_contract.md#12g, .claude/design/studies/whole_picture_2026-11/PATHS_AND_DERIVED_AGREED.md
# @end_deps
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from blueprint_arch.t3_translator import translate_t3_node
from utils import display_names, recipe_tiers
from app.modules.renamed_keys import FIX_IN_APP, audit_step_defect
from utils.audit_copy import AuditCopy, AuditCopyError, add_step, start_audit
from utils.plan_book import PlanBook
from utils.recipe_graph import RecipeGraph

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
    """The audit nodes whose place the plot is built from: a place of its own tier 3, or a table place above it. In the order given; a node whose place the
    graph does not have reaches no plot."""
    plot_node = own_plot_place(plot_id)
    found: List[dict] = []
    for node in nodes:
        place = node.get("place") or ""
        if place == plot_node or (graph.has_node(place) and plot_node in graph.below(place)):
            found.append(node)
    return found


def nodes_reaching_node(graph: RecipeGraph, nodes: Iterable[dict], node_id: str) -> List[dict]:
    """The audit nodes whose place the node `node_id` (a table's `T1:<table>` or `T2:<table>`) is built from: the place itself or a place above it. In the order given; a node
    whose place the graph does not have reaches nothing. HOME's T1 and T2 views ask it, so a step that cannot run elsewhere is not the error of a table it does not reach."""
    found: List[dict] = []
    for node in nodes:
        place = node.get("place") or ""
        if place == node_id or (graph.has_node(place) and node_id in graph.below(place)):
            found.append(node)
    return found


# ---------------------------------------------------------------------------------------------------------------------
# The nodes written at a place, and the audit copy they make
# ---------------------------------------------------------------------------------------------------------------------


def place_nodes(steps: Iterable[dict]) -> List[dict]:
    """The committed audit nodes written at a place (the flat list of the audit steps), the ones that are still active, in the order they were committed."""
    return [n for n in (steps or []) if n.get("place") and n.get("active", True)]


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


def place_line(place: str, raw: Any) -> str:
    """The place of an audit step as the lineage panel writes a node: "ResFinder: Table, T1", "Year Distribution: Result data, T3" (the same names, `utils.display_names`). A place the recipe does
    not have keeps its readable id; an empty or unreadable place is returned as it is. PROVISIONAL words."""
    tier, _, name = (place or "").partition(":")
    if not name or tier not in ("T1", "T2", "T3"):
        return str(place)
    kind = display_names.PLOT if tier == "T3" else display_names.TABLE
    return display_names.tagged_name(display_names.shown_name(display_names.shown_names(raw), kind, name), tier == "T3", int(tier[1]))


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
    started from, the action it is (`node_type`) with its parameters, the reason, the date it was APPLIED (`applied_at`; `created_at`, the staging time, for a step stored before that key existed) and the plots built from the place (`plots`), and, for a step added with "Add to audit pipeline", `user_verified` (and `verified_at` when it was). A place the graph does not have lists no plot."""
    records: List[Dict[str, Any]] = []
    for node in nodes:
        place = node.get("place") or ""
        records.append({
            "id": node.get("id"), "place": place, "place_words": place_words(place), "started_from": (node.get("started_from") or "").removeprefix("subtab_"),
            "action": node.get("node_type", "unknown"), "params": dict(node.get("params") or {}), "reason": node.get("reason", ""),
            "committed_at": node.get("applied_at") or node.get("created_at", ""),
            "plots": plots_below(graph, [place]) if graph.has_node(place) else [],
        })
        if "user_verified" in node:        # a step added with "Add to audit pipeline" says whether its place was user verified (FLOW-2, D-0670); a step of the old way carries nothing
            records[-1]["user_verified"] = bool(node["user_verified"])
            if node.get("verified_at"):
                records[-1]["verified_at"] = node["verified_at"]
    return records


def steps_by_place_yaml(records: Iterable[dict]) -> List[Dict[str, Any]]:
    """The `steps_by_place` list of `t3_steps.yaml` from the records of `place_step_records`: the parameters of a step sit in the step itself (flat), next to the action. The importer's check reads this shape (`renamed_keys.refused_audit_step_problem(..., type_key="action", flat=True)`): one function writes it, so the two cannot differ."""
    return [
        {"id": r["id"], "written_at": r["place"], "written_at_words": r["place_words"], "started_from_plot": r["started_from"],
         "action": r["action"], **r["params"], "reason": r["reason"], "committed_at": r["committed_at"],
         "plots_built_from_it": r["plots"],
         **({"user_verified": r["user_verified"], **({"verified_at": r["verified_at"]} if r.get("verified_at") else {})} if "user_verified" in r else {})}
        for r in records
    ]


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
        # each audit step stays visible in the recipe at its place with its reason (D-0622: the recipe is the audit recipe): the reason, the id and the date as the step's own `comment`
        note = _step_comment(node)
        body[tier_key] = {**held, "steps": list(held.get("steps") or []) + [{**step, "comment": note} for step in translate_t3_node(node)]}
        written.setdefault((f"{tier}:{name}", tier_key), []).append(str(node.get("id")))
    for (place, tier_key), ids in written.items():
        tier, name = place.split(":", 1)
        body = _body_of(baked, tier, name)
        note = f"Written by the export: the audit steps {', '.join(ids)} are added at the end of {tier_key}."
        body["comment"] = f"{body['comment']} {note}" if body.get("comment") else note
    return baked


def _step_comment(node: dict) -> str:
    """What a written audit step says of itself in the recipe: the reason, the id of the audit step and the day it was committed (PROVISIONAL words)."""
    when = str(node.get("applied_at") or node.get("created_at") or "")[:10]
    return f"Audit step {node.get('id')}" + (f", {when}" if when else "") + f": {node.get('reason', '')}"


def audit_recipe_of(raw: dict, nodes: Iterable[dict], original_id: str, made_on: str) -> dict:
    """The AUDIT RECIPE of an export made in Audit mode (D-0622; PROVISIONAL form): the original recipe with every audit step at its place (`bake_place_steps`, each step carrying its
    reason), under the id `<original id>_audited` (the id equals the file name, ADR-092) and an `info` that says in plain words that it is the audit recipe of the original and names it in `info.audit_of`. It is an
    ordinary recipe of format 1: the app opens it and runs it like any recipe, with the same data references as the original, and running it gives the audited tables and plots.
    The argument is not changed. Raises what `bake_place_steps` raises."""
    audit = bake_place_steps(raw, nodes)
    audit["id"] = f"{original_id}_audited"
    info = dict(audit.get("info") or {})
    label = str(info.get("ui_label") or original_id)
    info["ui_label"] = f"{label} (audited)"
    info["audit_of"] = original_id   # D-0354, D-0690: the audit recipe names its original; the set check then reads it as a copy of it (not a clash of plot ids)
    said = f"This is the audit recipe of '{original_id}', made on {made_on}: the original recipe with the audit steps written at their places, each with its reason in its own comment. Running it gives the audited tables and plots of the export it came with."
    info["description"] = f"{said} {info['description']}" if info.get("description") else said
    audit["info"] = info
    return audit


def audit_recipe_sentence(path: str, original_id: str) -> str:
    """One plain sentence for the README and the report: which folder holds the audit recipe, that the app opens it like any recipe and that running it gives the audited results (PROVISIONAL words)."""
    return (f"{path} is the audit recipe of '{original_id}': the original recipe with every audit step written at its place, each with its reason in its own comment. It is a recipe like any "
            f"other: the app opens it (put the file in the recipes folder, with the data it reads: its data references are the original's) and running it gives the audited tables and plots of this export.")


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
