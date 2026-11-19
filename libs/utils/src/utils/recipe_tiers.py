"""The one reading of which steps are the Tier 2 of a collection (RECIPE-DATASET-TIER2-1, issue #77, DEC16).

Every table has T1, T2 and T3, with or without a join; T2 and T3 can be empty (Eve, 2026-11-12). A *collection* is a
join, or a schema that a plot reads directly (`target_dataset`). Its Tier 2 is:
- for a join: `joins.<id>.tier2.steps`;
- for a schema plotted directly: its own `tier2.steps`.
A join reads the Tier 1 of its ingredients, so the tier-2 list of a schema applies only where that schema is plotted
directly (spec line 357). A tier-2 list on a schema that no plot reads is run nowhere: the checker refuses it (S07). The same
holds for a join: its tier-2 list runs only when a plot reads the join (J14).
An empty or absent list means T2 equals T1 (ADR-089: nothing is stored).

Pure functions on the resolved recipe (a dictionary); no engine, no disk. The engine (`DataOrchestrator`), the cache
keys, the export, HOME's badge, the checker and the Blueprint lineage all read the tiers through this module, so the
rule exists once.

# @deps
# provides: function:collection_body, function:tier2_steps, function:step_list, function:plot_targets, function:unapplied_schema_tier2, function:unapplied_join_tier2, function:without_tier2, function:without_data_engines, function:collection_bodies, function:schema_bodies
# consumed_by: app/modules/cache_keys.py, app/modules/engine_record.py (collection_body, step_list), app/modules/orchestrator.py (through cache_keys), libs/utils/src/utils/recipe_check.py, libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py, libs/utils/tests/test_recipe_tiers.py, app/tests/test_schema_tier2.py
# doc: .claude/design/recipe_format_spec.md (DEC16, line 357, S07, X4), .claude/knowledge/architecture_decisions.md#adr-089
# @end_deps
"""
from typing import Any, Dict, List, Set

# The sections that hold schemas. They share one id space with the joins (S02, X1).
SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")
METADATA_SCHEMA = "metadata_schema"


def step_list(body: Any, tier: str) -> list:
    """The steps of one tier of a schema or a join (`body[tier]["steps"]`, D-0250) as a new list; empty when absent.

    Only the mapping form is read: a tier written as a list is refused by the checker (S06, J07)."""
    held = body.get(tier) if isinstance(body, dict) else None
    steps = held.get("steps") if isinstance(held, dict) else None
    return list(steps) if isinstance(steps, list) else []


def schema_bodies(raw: dict) -> Dict[str, Any]:
    """{schema id: schema} of every schema of the recipe: data schemas, additional datasets and the metadata schema."""
    found: Dict[str, Any] = {}
    for section in SCHEMA_SECTIONS:
        if isinstance(raw.get(section), dict):
            found.update(raw[section])
    if METADATA_SCHEMA in raw:
        found[METADATA_SCHEMA] = raw[METADATA_SCHEMA]
    return found


def collection_body(raw: dict, collection_id: str) -> Any:
    """The join or the schema a collection id names (a join first, the order the engine resolves it in), else None."""
    joins = raw.get("joins") if isinstance(raw, dict) else None
    if isinstance(joins, dict) and collection_id in joins:
        return joins[collection_id]
    return schema_bodies(raw).get(collection_id) if isinstance(raw, dict) else None


def tier2_steps(raw: dict, collection_id: str) -> list:
    """The tier-2 steps of one collection; an empty list means T2 equals T1.

    A join id is looked up first, then a schema id, the order the engine resolves a collection in
    (`DataOrchestrator.materialize_tier1`); one id naming both is refused by the checker (X1)."""
    joins = raw.get("joins") if isinstance(raw, dict) else None
    if isinstance(joins, dict) and collection_id in joins:
        join = joins[collection_id]
        return step_list(join, "tier2")
    schema = schema_bodies(raw).get(collection_id) if isinstance(raw, dict) else None
    if isinstance(schema, dict):
        return step_list(schema, "tier2")
    return []


def plot_targets(raw: dict) -> Set[str]:
    """The collections the plots read (`target_dataset` of every plot entry)."""
    targets: Set[str] = set()
    groups = raw.get("analysis_groups") if isinstance(raw, dict) else None
    for group in (groups or {}).values() if isinstance(groups, dict) else []:
        plots = group.get("plots") if isinstance(group, dict) else None
        for plot in (plots or {}).values() if isinstance(plots, dict) else []:
            if isinstance(plot, dict):
                target = plot.get("target_dataset")
                if target is not None:
                    targets.add(target)
    return targets


def unapplied_schema_tier2(raw: dict) -> List[str]:
    """The schemas whose non-empty tier-2 list is run nowhere: no plot reads the schema directly (S07)."""
    targets = plot_targets(raw)
    return [sid for sid, schema in schema_bodies(raw).items()
            if isinstance(schema, dict) and step_list(schema, "tier2") and sid not in targets]


def unapplied_join_tier2(raw: dict) -> List[str]:
    """The joins whose non-empty tier-2 list is run nowhere: no plot reads the join (J14)."""
    targets = plot_targets(raw)
    joins = raw.get("joins") if isinstance(raw, dict) else None
    if not isinstance(joins, dict):
        return []
    return [jid for jid, join in joins.items()
            if isinstance(join, dict) and step_list(join, "tier2") and jid not in targets]


def without_tier2(raw: dict) -> dict:
    """A shallow copy of the recipe without the tier-2 list of any collection (what Tier 1 depends on, ADR-089 point 3).

    The recipe itself is not changed. Every other part stays, so an unknown part is part of Tier 1 (fail-safe rule)."""
    material = dict(raw)
    joins = material.get("joins")
    if isinstance(joins, dict):
        material["joins"] = {jid: _drop_tier2(join) for jid, join in joins.items()}
    for section in SCHEMA_SECTIONS:
        if isinstance(material.get(section), dict):
            material[section] = {sid: _drop_tier2(schema) for sid, schema in material[section].items()}
    if METADATA_SCHEMA in material:
        material[METADATA_SCHEMA] = _drop_tier2(material[METADATA_SCHEMA])
    return material


def _drop_tier2(body: Any) -> Any:
    if not (isinstance(body, dict) and "tier2" in body):
        return body
    return {k: v for k, v in body.items() if k != "tier2"}


def collection_bodies(raw: dict) -> Dict[str, Any]:
    """{id: body} of every join and every schema of the recipe: the blocks that have a tier 1 (and may have a tier 2)."""
    found: Dict[str, Any] = dict(schema_bodies(raw)) if isinstance(raw, dict) else {}
    joins = raw.get("joins") if isinstance(raw, dict) else None
    if isinstance(joins, dict):
        found.update(joins)   # a join first, the order `collection_body` resolves an id in
    return found


def without_data_engines(raw: dict) -> dict:
    """A shallow copy of the recipe without the written data engines of Tier 1: the recipe's `data_engine` and the
    `data_engine` of the tier 1 of every table and join.

    The cache key holds the EFFECTIVE tier-1 engine of each table as its own argument (`cache_keys.tier1_engines`, D-0240), so the
    text is left out of the material: a table whose tier 1 writes the engine it would inherit anyway has the same key as one
    that writes nothing. The `data_engine` of a tier 2 leaves with the tier-2 list (`without_tier2`). The recipe itself is not changed."""
    material = {k: v for k, v in raw.items() if k != "data_engine"}
    joins = material.get("joins")
    if isinstance(joins, dict):
        material["joins"] = {jid: _drop_tier1_engine(join) for jid, join in joins.items()}
    for section in SCHEMA_SECTIONS:
        if isinstance(material.get(section), dict):
            material[section] = {sid: _drop_tier1_engine(schema) for sid, schema in material[section].items()}
    if METADATA_SCHEMA in material:
        material[METADATA_SCHEMA] = _drop_tier1_engine(material[METADATA_SCHEMA])
    return material


def _drop_tier1_engine(body: Any) -> Any:
    tier1 = body.get("tier1") if isinstance(body, dict) else None
    if not (isinstance(tier1, dict) and "data_engine" in tier1):
        return body
    return {**body, "tier1": {k: v for k, v in tier1.items() if k != "data_engine"}}
