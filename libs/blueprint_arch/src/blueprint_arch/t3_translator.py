"""
T3 -> recipe-action translator (ADR-097 decision 4, REPRO-TRANSLATOR-1, issue #47).

Translates a plot's committed T3 audit steps into real, registered wrangling actions,
appended to a plot-private FORK of its join — never into the live, shared recipe. T2 is
shared across every plot using a given join (rules_data_engine.md's Bifurcation Point
Rule); T3 steps are per-plot, so they can only be made replayable by the headless engine
via a copy of the join that only this plot uses, not by writing into the shared `tier2:`
list directly.

Pure and stdlib-only (+ PyYAML, already a project dependency) — Two-Category Law, no
Shiny, no polars. Caller (export/#45, via app/handlers/export_handlers.py) supplies the
recipe's `raw_config` and each plot's own ordered, already-active T3 nodes
(`t3_audit_steps_by_plot`, the same shape already extracted there) and gets back a frozen,
export-only copy — the live recipe on disk is never touched.

Engine-coverage gap found while building this (not approximated — filed as an issue
instead): the registered wrangling actions only cover `eq` (filter_eq), inclusive
`ge`/`le` (filter_range), and `in` (is_in). There is no registered action for `ne`,
strict `gt`/`lt`, or `not_in` — checked directly in
libs/transformer/src/transformer/actions/cleaning/{core,analytical}.py, not assumed.
Approximating e.g. strict `gt` as inclusive `ge` would silently include one extra
boundary value — a real correctness bug, not a translator detail — so a plot whose T3
steps use an untranslatable op is skipped (named in the returned `skipped` dict) rather
than exported as falsely "fully reproducible".

Marker convention for translated-vs-native steps (left undecided in the original design
discussion): a structured `_t3_origin` key on the forked join dict, not a YAML comment —
round-trips through plain `yaml.safe_dump`/`safe_load` with no special library, and is
directly machine-readable on read-back (Eve: "we do not read T3" — a comment would still
leave that true; a dict key does not). Confirmed tolerated by the real engine: both
`app/modules/orchestrator.py` and `libs/transformer/tests/debug_assembler.py` read a join
spec with plain `.get("steps")`/`.get("ingredients")` — an extra sibling key is ignored,
not rejected.

See .claude/design/reproducible_export_design.md §4D/§6a and ADR-097 decision 4 for the
full design history (fork rationale, multi-plot propagation correctness).
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

import yaml

# @deps
# provides: function:translate_t3_node, function:translate_plot_steps, function:build_mode2_recipe, class:UntranslatableNode
# consumes: stdlib (copy, hashlib, json), PyYAML (developer_raw_yaml fragment parsing only)
# consumed_by: app/handlers/export_handlers.py (REPRO-TRANSLATOR-1 wiring, #45/#48), libs/blueprint_arch/tests/test_t3_translator.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-097, .claude/design/reproducible_export_design.md#4D
# @end_deps


class UntranslatableNode(Exception):
    """A T3 node whose type/op has no registered-action equivalent today.

    Callers must treat this as "skip this plot, surface why" — never as a cue to
    approximate. Carries the plain-text reason in its message.
    """


# Ops the registered action set can represent EXACTLY — checked directly against
# libs/transformer/src/transformer/actions/cleaning/core.py (filter_eq, filter_range)
# and analytical.py (is_in). `ne`, strict `gt`/`lt`, and `not_in` have no equivalent.
_TRANSLATABLE_OPS = {"eq", "ge", "le", "in"}


def _canonical_hash(obj: Any) -> str:
    """SHA256 of a JSON form with sorted keys — independent of key order.

    Deliberately duplicated from app/modules/cache_keys.py's canonical_hash() rather than
    imported: this library may not import from app/ (Clear Lines policy,
    rules_runtime_environment.md §4) — app/ is Tier 3 orchestration, this is a Tier 2
    domain library. The algorithm is three lines and is not expected to drift.
    """
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def translate_t3_node(node: dict) -> list[dict]:
    """One T3 audit node -> one or more canonical wrangling actions (`action:` key
    format, rules_data_analysis_recipe_structure.md §7).

    Raises UntranslatableNode when the node's type/op has no registered-action
    equivalent today. `aesthetic_override` nodes must be filtered out by the caller
    before this is reached — they are cosmetic, never translated (ADR-097 decision 4);
    passing one here raises, it is not silently skipped at this level.
    """
    node_type = node.get("node_type")
    params = node.get("params", {}) or {}

    if node_type in ("filter_row", "exclusion_row"):
        column = params.get("column")
        op = params.get("op", "eq")
        value = params.get("value")
        if not column:
            raise UntranslatableNode(f"{node_type} node has no column: {node!r}")
        # Same auto-promotion viz_factory.render() applies at render time (eq/in -> in,
        # ne/not_in -> not_in, when the stored value is a list) — a committed node can
        # carry op="eq" with a list value and only be promoted at render time, so this
        # translator must apply the identical rule or it would mistranslate it as a
        # single-value filter_eq on a list, which polars would not evaluate as intended.
        if isinstance(value, list):
            if op in ("eq", "in"):
                op = "in"
            elif op in ("ne", "not_in"):
                op = "not_in"
        if op not in _TRANSLATABLE_OPS:
            raise UntranslatableNode(
                f"op '{op}' has no registered wrangling action yet (only eq/ge/le/in are "
                f"representable today — see issue filed for ne/gt/lt/not_in) — node: {node!r}"
            )
        if op == "eq":
            return [{"action": "filter_eq", "column": column, "value": value}]
        if op == "ge":
            return [{"action": "filter_range", "columns": [column], "min": value}]
        if op == "le":
            return [{"action": "filter_range", "columns": [column], "max": value}]
        if op == "in":
            values = value if isinstance(value, list) else [value]
            return [{"action": "is_in", "column": column, "values": values}]

    if node_type == "drop_column":
        column = params.get("column")
        if not column:
            raise UntranslatableNode(f"drop_column node has no column: {node!r}")
        return [{"action": "drop_columns", "columns": [column]}]

    if node_type == "developer_raw_yaml":
        fragment = params.get("yaml_fragment", "")
        try:
            parsed = yaml.safe_load(fragment)
        except yaml.YAMLError as exc:
            raise UntranslatableNode(f"developer_raw_yaml fragment is not valid YAML: {exc}") from exc
        if not isinstance(parsed, list) or not all(
            isinstance(step, dict) and "action" in step for step in parsed
        ):
            raise UntranslatableNode(
                f"developer_raw_yaml fragment is not a list of canonical action steps "
                f"(each needs an 'action:' key, rules_data_analysis_recipe_structure.md §7): {fragment!r}"
            )
        return parsed

    raise UntranslatableNode(f"node_type {node_type!r} is not translatable: {node!r}")


def translate_plot_steps(nodes: list[dict]) -> list[dict]:
    """All of one plot's own committed T3 nodes, in that plot's own order (never a
    merged/inferred order — ADR-097 decision 4), to one flat ordered action list.

    `aesthetic_override` nodes are skipped here (cosmetic, not translated). Raises
    UntranslatableNode (naming the first node it can't translate) if any remaining node
    can't be represented — never a partial, silently-incomplete result.
    """
    actions: list[dict] = []
    for node in nodes:
        if node.get("node_type") == "aesthetic_override":
            continue
        actions.extend(translate_t3_node(node))
    return actions


def _find_plot_spec(raw_config: dict, plot_id: str) -> dict | None:
    """Same lookup order as home_theater.py's plot-spec resolution: analysis_groups
    first, then top-level `plots:` (the Path-A fallback). Returns the actual nested
    dict reference inside `raw_config`, so a caller mutating it (e.g. repointing
    target_dataset) mutates `raw_config` itself, not a copy.
    """
    for group in (raw_config.get("analysis_groups") or {}).values():
        plot_entry = (group.get("plots") or {}).get(plot_id)
        if plot_entry is not None:
            return plot_entry.get("spec")
    return (raw_config.get("plots") or {}).get(plot_id)


def build_mode2_recipe(
    raw_config: dict, t3_by_plot: dict[str, list[dict]]
) -> tuple[dict, dict[str, str]]:
    """Build a frozen, export-only copy of `raw_config` with each translatable plot's
    T3 steps baked into a plot-private fork of its join.

    Parameters
    ----------
    raw_config : dict
        The ORIGINAL recipe's raw_config. Never mutated — a deep copy is returned.
    t3_by_plot : dict[str, list[dict]]
        {plot_id: [that plot's own active T3 nodes, in that plot's own order]} — the
        same shape export_handlers.py already extracts as `_t3_by_plot`.

    Returns
    -------
    (new_raw_config, skipped)
        new_raw_config : the deep copy, with forked joins added under
            "<target_dataset>__t3_<plot_id>" and translatable plots' `target_dataset`
            repointed at their fork. Each fork carries a `_t3_origin` marker dict
            (forked_from, source_plot, node_ids) — not a YAML comment, see module
            docstring.
        skipped : {plot_id: human-readable reason} for every plot whose T3 content
            could not be translated. Those plots keep their ORIGINAL target_dataset,
            completely unchanged (never partially forked) — the caller (#45/#48) must
            surface this to the user rather than claim full reproducibility for them.

    Two or more plots targeting the same join, whose fully-resolved translated action
    sequences turn out byte-identical, share one fork (deduplication AFTER independent
    per-plot computation — never grouped by T3 propagation scope directly, ADR-097
    decision 4: a node shared via "all plots" can still need different forks per plot,
    e.g. when those plots use different joins, or one plot carries an extra node on top).
    """
    new_config = copy.deepcopy(raw_config)
    # ConfigManager injects a root-level `plots:` key into raw_config as an internal
    # convenience mirror of analysis_groups (config_loader.py: "Flatten analysis_groups
    # into top-level 'plots' for VizFactory (engine detail only..."). Confirmed live: a
    # recipe dumped with this key present fails to reload (LEGACY-FLAT-PLOTS-1's fatal
    # check on a root `plots:` key, rules_data_analysis_recipe_structure.md §8) — not a
    # hypothetical, reproduced by writing one such raw_config straight to YAML and
    # reloading it. Any caller re-loading this output (the Mode 2 writer, #45; Import,
    # #48) needs this gone, not just this translator's own test fixtures.
    new_config.pop("plots", None)
    joins = new_config.setdefault("joins", {})
    skipped: dict[str, str] = {}
    fork_cache: dict[tuple, str] = {}

    for plot_id, nodes in t3_by_plot.items():
        if not nodes:
            continue
        spec = _find_plot_spec(new_config, plot_id)
        if spec is None:
            skipped[plot_id] = "plot spec not found in this recipe"
            continue
        target_dataset = spec.get("target_dataset")
        if not target_dataset:
            # §6a: a bare-schema plot (no target_dataset, "Path A") has no join to
            # fork — narrow, documented edge case, not silently mishandled.
            skipped[plot_id] = "plot has no target_dataset (bare data_schema) — no join to fork"
            continue
        original_join = joins.get(target_dataset)
        if original_join is None:
            skipped[plot_id] = f"'{target_dataset}' is not a join at the engine level (bare schema)"
            continue
        try:
            translated = translate_plot_steps(nodes)
        except UntranslatableNode as exc:
            skipped[plot_id] = str(exc)
            continue
        if not translated:
            continue  # only aesthetic_override nodes — nothing data-affecting to fork

        fork_key = (target_dataset, _canonical_hash(translated))
        fork_id = fork_cache.get(fork_key)
        if fork_id is None:
            fork_id = f"{target_dataset}__t3_{plot_id}"
            forked_join = copy.deepcopy(original_join)
            steps = forked_join.setdefault("steps", {})
            tier2 = list(steps.get("tier2") or [])
            tier2.extend(translated)
            steps["tier2"] = tier2
            forked_join["_t3_origin"] = {
                "forked_from": target_dataset,
                "source_plot": plot_id,
                "node_ids": [n.get("id") for n in nodes if n.get("id")],
            }
            joins[fork_id] = forked_join
            fork_cache[fork_key] = fork_id
        spec["target_dataset"] = fork_id

    return new_config, skipped
