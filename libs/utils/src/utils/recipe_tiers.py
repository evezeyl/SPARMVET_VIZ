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

THE AUDIT LIST (D-0332, piece C-1). In an AUDIT recipe each tier body is `{steps: [...], audit_steps: [...]}`: `steps` is the author's list,
never touched; `audit_steps` is the second list, the steps of the audit. The engine runs `steps`, then `audit_steps`. `step_list(body, tier)` is
the ONE reading that RUNS a tier (the author's steps, then the audit steps); `author_steps` and `audit_steps_of` give each list apart (the keys of
the stored tables, the audit copy, the checker and the Blueprint writer need them apart). A reader that reads a tier's `steps` directly would
skip the audit steps silently: `app/tests/test_tier_steps_one_reader.py` fails when one does. The key name `audit_steps` is in ONE constant,
`AUDIT_STEPS`; the reason of an audit step is the step key `AUDIT_COMMENT` (D-0329); the id of an audit step has the form `AUDIT_ID`.

# @deps
# provides: constant:AUDIT_STEPS, constant:AUDIT_COMMENT, constant:AUDIT_ID, function:author_steps, function:audit_steps_of, function:tier2_parts, function:tier3_parts, function:without_audit_steps, function:audit_step_places, function:collection_body, function:tier2_steps, function:step_list, function:plot_entries, function:plot_entry, function:tier3_steps, function:plot_targets, function:unapplied_schema_tier2, function:unapplied_join_tier2, function:without_tier2, function:without_data_engines, function:collection_bodies, function:schema_bodies
# consumed_by: app/modules/cache_keys.py, app/modules/engine_record.py (collection_body, step_list), app/modules/orchestrator.py (plot_entry, tier3_steps; collection_body), libs/utils/src/utils/recipe_check.py, libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py, libs/utils/tests/test_recipe_tiers.py, app/tests/test_schema_tier2.py
# doc: .claude/design/recipe_format_spec.md (DEC16, line 357, S07, X4), .claude/knowledge/architecture_decisions.md#adr-089
# @end_deps
"""
import copy
import re
from typing import Any, Dict, List, Set, Tuple

# The sections that hold schemas. They share one id space with the joins (S02, X1).
SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")
METADATA_SCHEMA = "metadata_schema"


# The second list of a tier body, in an audit recipe only (D-0332). The decided name; written here and nowhere else.
AUDIT_STEPS = "audit_steps"
# The reason of an audit step: a step key of its own, free text (D-0329). The author's `comment` key is another thing.
AUDIT_COMMENT = "audit_comment"
# The id of an audit step: `audit_<8 hex>_<k>`, `k` counting the order in which the steps were created in that audit (D-0321).
AUDIT_ID = re.compile(r"^audit_[0-9a-f]{8}_\d+$")


def _list_of(body: Any, tier: str, key: str) -> list:
    held = body.get(tier) if isinstance(body, dict) else None
    steps = held.get(key) if isinstance(held, dict) else None
    return list(steps) if isinstance(steps, list) else []


def author_steps(body: Any, tier: str) -> list:
    """The author's steps of one tier of a schema or a join (`body[tier]["steps"]`, D-0250) as a new list; empty when absent.

    Only the mapping form is read: a tier written as a list is refused by the checker (S06, J07). The audit steps are NOT here:
    whatever RUNS steps reads `step_list`."""
    return _list_of(body, tier, "steps")


def audit_steps_of(body: Any, tier: str) -> list:
    """The audit steps of one tier (`body[tier]["audit_steps"]`) as a new list; empty when absent (every recipe that is not an audit recipe)."""
    return _list_of(body, tier, AUDIT_STEPS)


def step_list(body: Any, tier: str) -> list:
    """The steps one tier RUNS: the author's steps, then the audit steps, as a new list (D-0332). THE one reading of a tier for whatever
    runs, counts or follows steps (the engine, the recipe map, the badge, the export); empty when the tier is absent."""
    return author_steps(body, tier) + audit_steps_of(body, tier)


# Every tier name: `audit_step_places` looks in all of them, also where no tier is read (a tier 3 of a table, a tier 1 of a plot): the key is found wherever it is written.
_ALL_TIERS = ("tier1", "tier2", "tier3")


def audit_step_places(raw: Any) -> List[str]:
    """Where a recipe holds an `audit_steps` key at all (even an empty one, even where no tier reads it), as the path of each tier body, in the order of the recipe: tables, joins,
    then plots. Empty for an ordinary recipe. Lets a reader that is not the checker (the engine) refuse an audit key in a recipe that is not an audit recipe."""
    found: List[str] = []
    if not isinstance(raw, dict):
        return found
    for section in SCHEMA_SECTIONS:
        for sid, body in (raw.get(section) or {}).items() if isinstance(raw.get(section), dict) else []:
            found.extend(_tiers_with_audit(body, f"{section}.{sid}", _ALL_TIERS))
    if METADATA_SCHEMA in raw:
        found.extend(_tiers_with_audit(raw[METADATA_SCHEMA], METADATA_SCHEMA, _ALL_TIERS))
    for jid, body in (raw.get("joins") or {}).items() if isinstance(raw.get("joins"), dict) else []:
        found.extend(_tiers_with_audit(body, f"joins.{jid}", _ALL_TIERS))
    for pid, entry in plot_entries(raw).items():
        found.extend(_tiers_with_audit(entry, f"plot {pid}", _ALL_TIERS))
    return found


def _tiers_with_audit(body: Any, path: str, tiers: Tuple[str, ...]) -> List[str]:
    return [f"{path}.{tier}" for tier in tiers if isinstance(body, dict) and isinstance(body.get(tier), dict) and AUDIT_STEPS in body[tier]]


def without_audit_steps(raw: Any) -> Any:
    """A deep copy of the recipe without any `audit_steps` key: the recipe as the author wrote it (an audit recipe minus its audit steps is its
    original, D-0040). A tier body that holds nothing else is kept (`{steps: [...]}`); the recipe given is not changed."""
    stripped = copy.deepcopy(raw)
    if not isinstance(stripped, dict):
        return stripped
    bodies: List[Any] = list(collection_bodies(stripped).values()) + list(plot_entries(stripped).values())
    for body in bodies:
        if isinstance(body, dict):
            for tier in ("tier1", "tier2", "tier3"):
                if isinstance(body.get(tier), dict):
                    body[tier].pop(AUDIT_STEPS, None)
    return stripped


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
    """The tier-2 steps of one collection that RUN (the author's, then the audit steps); an empty list means T2 equals T1.

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


def tier2_parts(raw: dict, collection_id: str) -> Tuple[list, list]:
    """(the author's tier-2 steps, the audit tier-2 steps) of one collection, the two lists apart (the cache keys hold them in two parts)."""
    body = collection_body(raw, collection_id)
    return author_steps(body, "tier2"), audit_steps_of(body, "tier2")


def plot_entries(raw: dict) -> Dict[str, dict]:
    """{plot id: plot entry} of every plot of the recipe, in the order of the groups and of the plots in each group."""
    found: Dict[str, dict] = {}
    groups = raw.get("analysis_groups") if isinstance(raw, dict) else None
    for group in (groups or {}).values() if isinstance(groups, dict) else []:
        plots = group.get("plots") if isinstance(group, dict) else None
        for plot_id, plot in (plots or {}).items() if isinstance(plots, dict) else []:
            if isinstance(plot, dict):
                found[plot_id] = plot
    return found


def plot_entry(raw: dict, plot_id: str) -> Any:
    """The entry of one plot, or None when the recipe has no such plot."""
    return plot_entries(raw).get(plot_id)


def tier3_steps(raw: dict, plot_id: str) -> list:
    """The tier-3 steps of one plot entry that RUN (`tier3.steps`, DEC17, D-0250, then the audit steps); an empty list means the plot reads its table as it is.

    The same reading as the other tiers (`step_list`): only the mapping form is read, the checker refuses any other (P04)."""
    return step_list(plot_entry(raw, plot_id), "tier3")


def tier3_parts(raw: dict, plot_id: str) -> Tuple[list, list]:
    """(the author's tier-3 steps, the audit tier-3 steps) of one plot entry, apart."""
    entry = plot_entry(raw, plot_id)
    return author_steps(entry, "tier3"), audit_steps_of(entry, "tier3")


def plot_targets(raw: dict) -> Set[str]:
    """The collections the plots read (`target_dataset` of every plot entry)."""
    targets: Set[str] = set()
    groups = raw.get("analysis_groups") if isinstance(raw, dict) else None
    for group in (groups or {}).values() if isinstance(groups, dict) else []:
        plots = group.get("plots") if isinstance(group, dict) else None
        for plot in (plots or {}).values() if isinstance(plots, dict) else []:
            if isinstance(plot, dict):
                target = plot.get("target_dataset")
                if isinstance(target, str):  # a target that is not text is refused by the checker (PS02)
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
