"""The one reading of which steps are the Tier 2 of a collection (RECIPE-DATASET-TIER2-1, issue #77, DEC16).

Every table has T1, T2 and T3, with or without a join; T2 and T3 can be empty (Eve, 2026-11-12). A *collection* is a
join, or a schema that a plot reads directly (`target_dataset`). Its Tier 2 is:
- for a join: `joins.<id>.steps.tier2`;
- for a schema plotted directly: its own `wrangling.tier2`.
A join reads the Tier 1 of its ingredients, so the tier-2 list of a schema applies only where that schema is plotted
directly (spec line 357). A tier-2 list on a schema that no plot reads is run nowhere: the checker refuses it (S07).
An empty or absent list means T2 equals T1 (ADR-089: nothing is stored).

Pure functions on the resolved recipe (a dictionary); no engine, no disk. The engine (`DataOrchestrator`), the cache
keys, the export, HOME's badge, the checker and the Blueprint lineage all read the tiers through this module, so the
rule exists once.

# @deps
# provides: function:tier2_steps, function:step_list, function:plot_targets, function:unapplied_schema_tier2, function:without_tier2, function:schema_bodies
# consumed_by: app/modules/cache_keys.py, app/modules/orchestrator.py (through cache_keys), libs/utils/src/utils/recipe_check.py, libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py, libs/utils/tests/test_recipe_tiers.py, app/tests/test_schema_tier2.py
# doc: .claude/design/recipe_format_spec.md (DEC16, line 357, S07, X4), .claude/knowledge/architecture_decisions.md#adr-089
# @end_deps
"""
from typing import Any, Dict, List, Set

# The sections that hold schemas. They share one id space with the joins (S02, X1).
SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")
METADATA_SCHEMA = "metadata_schema"


def step_list(container: Any, tier: str) -> list:
    """One tier of a step container (`wrangling` of a schema, `steps` of a join) as a new list; empty when absent.

    Only the mapping form is read: a flat list is not a step container and is refused by the checker (S06, J07)."""
    steps = container.get(tier) if isinstance(container, dict) else None
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


def tier2_steps(raw: dict, collection_id: str) -> list:
    """The tier-2 steps of one collection; an empty list means T2 equals T1.

    A join id is looked up first, then a schema id, the order the engine resolves a collection in
    (`DataOrchestrator.materialize_tier1`); one id naming both is refused by the checker (X1)."""
    joins = raw.get("joins") if isinstance(raw, dict) else None
    if isinstance(joins, dict) and collection_id in joins:
        join = joins[collection_id]
        return step_list(join.get("steps") if isinstance(join, dict) else None, "tier2")
    schema = schema_bodies(raw).get(collection_id) if isinstance(raw, dict) else None
    if isinstance(schema, dict):
        return step_list(schema.get("wrangling"), "tier2")
    return []


def plot_targets(raw: dict) -> Set[str]:
    """The collections the plots read (`target_dataset` of every plot spec)."""
    targets: Set[str] = set()
    groups = raw.get("analysis_groups") if isinstance(raw, dict) else None
    for group in (groups or {}).values() if isinstance(groups, dict) else []:
        plots = group.get("plots") if isinstance(group, dict) else None
        for plot in (plots or {}).values() if isinstance(plots, dict) else []:
            if isinstance(plot, dict) and isinstance(plot.get("spec"), dict):
                target = plot["spec"].get("target_dataset")
                if target is not None:
                    targets.add(target)
    return targets


def unapplied_schema_tier2(raw: dict) -> List[str]:
    """The schemas whose non-empty tier-2 list is run nowhere: no plot reads the schema directly (S07)."""
    targets = plot_targets(raw)
    return [sid for sid, schema in schema_bodies(raw).items()
            if isinstance(schema, dict) and step_list(schema.get("wrangling"), "tier2") and sid not in targets]


def without_tier2(raw: dict) -> dict:
    """A shallow copy of the recipe without the tier-2 list of any collection (what Tier 1 depends on, ADR-089 point 3).

    The recipe itself is not changed. Every other part stays, so an unknown part is part of Tier 1 (fail-safe rule)."""
    material = dict(raw)
    joins = material.get("joins")
    if isinstance(joins, dict):
        material["joins"] = {jid: _drop_tier2(join, "steps") for jid, join in joins.items()}
    for section in SCHEMA_SECTIONS:
        if isinstance(material.get(section), dict):
            material[section] = {sid: _drop_tier2(schema, "wrangling") for sid, schema in material[section].items()}
    if METADATA_SCHEMA in material:
        material[METADATA_SCHEMA] = _drop_tier2(material[METADATA_SCHEMA], "wrangling")
    return material


def _drop_tier2(body: Any, container_key: str) -> Any:
    container = body.get(container_key) if isinstance(body, dict) else None
    if not (isinstance(container, dict) and "tier2" in container):
        return body
    return {**body, container_key: {k: v for k, v in container.items() if k != "tier2"}}
