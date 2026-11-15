"""Which layers of a plot are random (SEED-HOLDS-1, ADR-104).

One rule for two readers: the plot factory seeds exactly these layers, and the recipe checker accepts the argument
`random_state` on exactly these layers (code PS04). A layer is random when

- its component draws random numbers by itself (`ALWAYS_RANDOM`: found by drawing every registered component twice,
  `libs/viz_factory/tests/test_every_component_randomness.py`), or
- it places its points with `position: jitter` or `jitterdodge` (any geom), or
- it summarises with a bootstrapped function (`fun_data: mean_cl_boot`) in a summary stat, written as the component
  `stat_summary` / `stat_summary_bin` or as `stat: summary` / `summary_bin` on a geom.

# @deps
# provides: constant:ALWAYS_RANDOM, function:is_random_layer
# consumed_by: libs/viz_factory/src/viz_factory/plot_config_resolver.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/utils/src/utils/recipe_check.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104
# @end_deps
"""
from __future__ import annotations

ALWAYS_RANDOM = ("geom_jitter", "position_jitter", "position_jitterdodge", "geom_sina", "stat_sina")
JITTER_POSITIONS = ("jitter", "jitterdodge")
SUMMARY_STATS = ("stat_summary", "stat_summary_bin")
SUMMARY_STAT_NAMES = ("summary", "summary_bin")
BOOTSTRAP_FUNCTIONS = ("mean_cl_boot",)


def is_random_layer(name: str | None, params: dict | None) -> bool:
    """True when drawing this layer uses random numbers, so it needs a seed to be reproducible."""
    params = params or {}
    if name in ALWAYS_RANDOM or params.get("position") in JITTER_POSITIONS:
        return True
    summary = name in SUMMARY_STATS or params.get("stat") in SUMMARY_STAT_NAMES
    return summary and params.get("fun_data") in BOOTSTRAP_FUNCTIONS
