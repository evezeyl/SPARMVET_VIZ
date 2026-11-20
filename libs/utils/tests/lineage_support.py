"""Helpers shared by the lineage walk tests: the setup of a walk, and an independent count of the places of a recipe (from the recipe text, not
from the graph, so a wrong collapse in the walk cannot hide in the expected value).
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Set, Tuple

import lineage_oracle as oracle

from utils.lineage_records import Scope, Start, Walk
from utils.lineage_walk import LineageIndex
from utils.plan_book import PlanBook
from utils.recipe_graph import RecipeGraph, build_graph


def setup(recipe: Mapping[str, Any], tables: Mapping[str, Any]) -> Tuple[RecipeGraph, PlanBook]:
    return build_graph(recipe), oracle.replay(recipe, tables).plans


def run(recipe: Mapping[str, Any], tables: Mapping[str, Any], node: str, column: str, scope: Scope = Scope.JOIN_LINKED, kind: str = "filter") -> Walk:
    graph, plans = setup(recipe, tables)
    return LineageIndex(graph, plans).walk(Start(node, column), scope=scope, kind=kind)


def places(walk: Walk) -> List[str]:
    return [line.place for line in walk.lines]


def ticked(walk: Walk) -> List[str]:
    return [line.place for line in walk.lines if line.state == "tick"]


def independent_places(recipe: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    """The places of a recipe as the owner decided them (D-0346), counted from the recipe text: {place: {"last": node, "plots": set of plots below}}.
    A table (schema or join) is always a place at its tier 1; its tier 2 is a place only when it has steps and a plot reads the table directly;
    a plot is always a place."""
    schemas: Set[str] = set()
    for section in ("data_schemas", "additional_datasets_schemas"):
        schemas |= set(recipe.get(section) or {})
    joins = dict(recipe.get("joins") or {})
    plots: Dict[str, Any] = {}
    for group in (recipe.get("analysis_groups") or {}).values():
        plots.update(group.get("plots") or {})
    read_directly = {pid: e["target_dataset"] for pid, e in plots.items()}

    def steps(body: Any, tier: str) -> list:
        held = (body or {}).get(tier) or {}
        return list(held.get("steps") or [])

    bodies = {**{s: (recipe.get("data_schemas") or {}).get(s) or (recipe.get("additional_datasets_schemas") or {}).get(s) for s in schemas}, **joins}
    result: Dict[str, Dict[str, Any]] = {}
    for table, body in bodies.items():
        readers = {pid for pid, t in read_directly.items() if t == table}
        through_joins = {pid for j, jb in joins.items() if table in [i["dataset_id"] for i in jb.get("ingredients", [])] for pid, t in read_directly.items() if t == j}
        result[f"T1:{table}"] = {"last": f"T1:{table}", "plots": readers | through_joins}
        if steps(body, "tier2") and readers:
            result[f"T2:{table}"] = {"last": f"T2:{table}", "plots": readers}
    for pid in plots:
        result[f"T3:{pid}"] = {"last": f"T3:{pid}", "plots": {pid}}
    return result
