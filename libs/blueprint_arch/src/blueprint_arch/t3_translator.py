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

Engine-coverage gap found while building this, closed in #52: the registered wrangling
actions originally only covered `eq` (filter_eq), inclusive `ge`/`le` (filter_range), and
`in` (is_in) — no action existed for `ne`, strict `gt`/`lt`, or `not_in`. Rather than
approximate (e.g. strict `gt` as inclusive `ge` would silently include one extra boundary
value — a real correctness bug, not a translator detail), the gap was closed by adding
`filter_ne`, `filter_gt`, `filter_lt` (cleaning/core.py) and `not_in`
(cleaning/analytical.py) actions, following the existing pattern. All eight T3 filter ops
(`eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `not_in`) are now translatable. A plot whose T3
steps use a node type with no translation at all (anything other than filter_row/
exclusion_row/drop_column/developer_raw_yaml) is still skipped (named in the returned
`skipped` dict) rather than exported as falsely "fully reproducible".

Where a fork says what it is (recipe format 1, work order W8): in its `comment` key, the
one place of a join for a note that people read and that is never executed (spec 6.2).
The text names the join it was copied from, the plot or plots it serves and the ids of
the audit steps. The former `_t3_origin` key is gone: format 1 refuses a key it does not
know (check J01), and nothing read it. What is native and what was added stays exact
without a marker: the original join is still in the recipe, and the fork's `tier2` is the
original `tier2` followed by the translated steps. The step marker of the audit copy
(`id: audit_<8 hex>_<k>`, spec 7.5, profile `audit`) is not written here: it belongs to
the audit copy of the HOME design, which is to replace this fork.

The forked recipe is format 1 when the recipe it starts from is: nothing is added outside
the format, so it passes `utils.recipe_check.check_recipe` in profile `run`.

See .claude/design/reproducible_export_design.md §4D/§6a and ADR-097 decision 4 for the
full design history (fork rationale, multi-plot propagation correctness).
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

import yaml

from utils import action_names

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


# Ops that `modif_filter` represents EXACTLY (libs/transformer/src/transformer/actions/modified.py): the audit dialog and the
# recipe filter share one vocabulary now (`between` has no audit operator).
FILTER, DROP = action_names.FILTER, action_names.DROP
_TRANSLATABLE_OPS = {"eq", "ne", "gt", "ge", "lt", "le", "in", "not_in"}


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
        # single-value eq filter on a list, which polars would not evaluate as intended.
        if isinstance(value, list):
            if op in ("eq", "in"):
                op = "in"
            elif op in ("ne", "not_in"):
                op = "not_in"
        if op not in _TRANSLATABLE_OPS:
            raise UntranslatableNode(
                f"op '{op}' has no registered wrangling action — not one of "
                f"{sorted(_TRANSLATABLE_OPS)} — node: {node!r}"
            )
        if op in ("in", "not_in"):
            value = value if isinstance(value, list) else [value]
        # `na: remove`: a missing value is dropped by every comparison, as the filters of HOME and the plot have always done
        return [{"action": FILTER, "column": column, "op": op, "value": value, "na": "remove"}]

    if node_type == "drop_column":
        column = params.get("column")
        if not column:
            raise UntranslatableNode(f"drop_column node has no column: {node!r}")
        return [{"action": DROP, "columns": [column]}]

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
    """The `spec` of a plot, looked up in `analysis_groups` (the only place of a plot in
    recipe format 1). Returns the actual nested dict reference inside `raw_config`, so a
    caller mutating it (e.g. repointing target_dataset) mutates `raw_config` itself, not
    a copy.
    """
    for group in (raw_config.get("analysis_groups") or {}).values():
        plot_entry = (group.get("plots") or {}).get(plot_id)
        if plot_entry is not None:
            return plot_entry.get("spec")
    return None


def _fork_comment(forked_from: str, plot_ids: list[str], node_ids: list[str]) -> str:
    """The note of a fork: where it comes from, in plain words (the `comment` key of a join)."""
    plots = f"the plot {plot_ids[0]}" if len(plot_ids) == 1 else "the plots " + ", ".join(plot_ids)
    steps = f" (audit step ids: {', '.join(node_ids)})" if node_ids else ""
    return (f"Written by the export. Copy of the join {forked_from} for {plots}: "
            f"the audit steps{steps} are added at the end of tier2.")


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
            repointed at their fork. Each fork says in its `comment` which join it
            copies, for which plot or plots, and the ids of the audit steps (see the
            module docstring). No key outside recipe format 1 is added.
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
    # fork id -> (the join it copies, the plots it serves, the ids of their audit steps): the text of its comment
    fork_origin: dict[str, tuple[str, list[str], list[str]]] = {}

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
            joins[fork_id] = forked_join
            fork_cache[fork_key] = fork_id
            fork_origin[fork_id] = (target_dataset, [], [])
        _, plot_ids, node_ids = fork_origin[fork_id]
        plot_ids.append(plot_id)
        node_ids.extend(str(n["id"]) for n in nodes if n.get("id") and str(n["id"]) not in node_ids)
        spec["target_dataset"] = fork_id

    for fork_id, (forked_from, plot_ids, node_ids) in fork_origin.items():
        joins[fork_id]["comment"] = _fork_comment(forked_from, plot_ids, node_ids)

    return new_config, skipped
