"""Which layers of a plot are random (SEED-HOLDS-1, ADR-104).

One rule for two readers: the plot factory seeds exactly these layers, and the recipe checker accepts the argument
`random_state` on exactly these layers (code PS04). A layer is random when

- its component draws random numbers by itself (`ALWAYS_RANDOM`: found by drawing every registered component twice,
  `libs/viz_factory/tests/test_every_component_randomness.py`), or
- it places its points with `position: jitter` or `jitterdodge` (any geom), or
- it computes the `sina` statistic (`stat: sina` on any geom), or
- it summarises with a bootstrapped function in a summary stat, written as the component `stat_summary` /
  `stat_summary_bin` or as `stat: summary` / `summary_bin` on a geom. plotnine's default `fun_data` of
  `stat_summary` is the bootstrap (`mean_cl_boot`), so a `summary` that names no function is random; the default of
  `stat_summary_bin` is not (it is random only with `fun_data: mean_cl_boot`); a named `mean_se`, `mean_cl_normal`,
  `mean_sdl` or `median_hilow` is never random.

A `position` or a `stat` written as text is read the way plotnine reads it: `jitter` and `position_jitter`, `sina` and
`stat_sina` are the same (`position_of`, `stat_of`: the one place that does it).

Found by drawing: every plotnine statistic and position with a geom, and every geom with each random statistic and
position (`libs/viz_factory/tests/test_every_component_randomness.py`).

# @deps
# provides: constant:ALWAYS_RANDOM, function:is_random_layer, function:is_seed_value, function:position_of, function:stat_of
# consumed_by: libs/viz_factory/src/viz_factory/plot_config_resolver.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/utils/src/utils/recipe_check.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104
# @end_deps
"""
from __future__ import annotations

ALWAYS_RANDOM = ("geom_jitter", "position_jitter", "position_jitterdodge", "geom_sina", "stat_sina")
JITTER_POSITIONS = ("position_jitter", "position_jitterdodge")
RANDOM_STATS = ("stat_sina",)
SUMMARY_STATS = ("stat_summary", "stat_summary_bin")
BOOTSTRAP_FUNCTIONS = ("mean_cl_boot",)
DEFAULT_SUMMARY_FUNCTION = "mean_cl_boot"   # plotnine's default fun_data of stat_summary


def _plotnine_name(value, prefix: str) -> str | None:
    """The name plotnine looks up for a `position` or a `stat` given as text: the text itself when it starts with the
    prefix, else the prefix is added (`jitter` and `position_jitter` are the same position). Exactly plotnine's
    rule (`position.from_geom`, `stat.from_geom`): no case change, no trimming. What is not text (a class, an object,
    a mapping) has no name here; a recipe cannot hold a class, and plotnine refuses a mapping."""
    if not isinstance(value, str):
        return None
    return value if value.startswith(prefix) else prefix + value


def position_of(params: dict | None) -> str | None:
    """The full plotnine name of the layer's `position` parameter (`position_jitter`), or None."""
    return _plotnine_name((params or {}).get("position"), "position_")


def stat_of(params: dict | None) -> str | None:
    """The full plotnine name of the layer's `stat` parameter (`stat_sina`), or None."""
    return _plotnine_name((params or {}).get("stat"), "stat_")


def is_random_layer(name: str | None, params: dict | None) -> bool:
    """True when drawing this layer uses random numbers, so it needs a seed to be reproducible."""
    params = params or {}
    stat = stat_of(params)
    if name in ALWAYS_RANDOM or position_of(params) in JITTER_POSITIONS or stat in RANDOM_STATS:
        return True
    if name not in SUMMARY_STATS and stat not in SUMMARY_STATS:
        return False
    binned = name == "stat_summary_bin" or stat == "stat_summary_bin"
    default = None if binned else DEFAULT_SUMMARY_FUNCTION
    return (params.get("fun_data") or default) in BOOTSTRAP_FUNCTIONS


def is_seed_value(value) -> bool:
    """True for a seed: a whole number (not a bool), or the text of one ("7"). null, the word random, other text, a
    float and a list are not seeds; the checker and the factory refuse them with the same plain message."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, str):
        try:
            int(value.strip())
        except ValueError:
            return False
        return True
    return False
