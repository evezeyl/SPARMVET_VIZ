"""Which list or mapping parameters of an action must not be empty (`min_items: 1` in the form schema).

Why: each of these actions already refuses the empty value when the recipe runs (found by running every action with
every list or mapping parameter empty, 2026-11-15). Writing it in the schema lets the recipe checker refuse the same
step before anything runs, with the one message of `utils.ui_schema.step_problems` (DEC03: one checker for every user
of recipes; ADR-104: no silent error). Only what is refused today is listed: an empty value that runs and returns the
table unchanged is a finding against DEC36, not a thing to hide here.

This module is imported last by `transformer.actions`, after every action has registered its schema.
"""
from transformer.actions.base import ACTION_SCHEMAS

# action -> the parameters that need at least one item
MUST_NOT_BE_EMPTY = {
    "polars_all_horizontal": ("exprs",),
    "polars_any_horizontal": ("exprs",),
    "polars_max_horizontal": ("exprs",),
    "polars_mean_horizontal": ("exprs",),
    "polars_min_horizontal": ("exprs",),
    "polars_sum_horizontal": ("exprs",),
    "polars_coalesce": ("exprs",),
    "polars_explode": ("columns",),
    "polars_group_by_dynamic": ("named_aggs",),
    "polars_rolling": ("named_aggs",),
    "polars_pivot": ("on", "index", "values"),
    "polars_rank": ("columns",),
    "polars_remove": ("predicates",),
    "polars_join_where": ("predicates",),
    "polars_join_asof": ("by", "by_left", "by_right"),
    "polars_join": ("on", "left_on", "right_on"),
    "polars_unique": ("subset",),
}


# what the author can write instead of an empty value (the plain advice the actions gave before the checker said it)
HINTS = {
    ("polars_join_asof", "by"): "leave it out to match on the key alone",
    ("polars_join_asof", "by_left"): "leave it out to match on the key alone",
    ("polars_join_asof", "by_right"): "leave it out to match on the key alone",
    ("polars_join_where", "predicates"): "write one or more formulas, for example \"pl.col('year') >= pl.col('start_year')\"",
}


def apply() -> None:
    """Write `min_items: 1` on each listed parameter; a listed name the registry does not hold is an error."""
    for action, names in MUST_NOT_BE_EMPTY.items():
        params = ACTION_SCHEMAS[action]["params"]
        for name in names:
            params[name]["min_items"] = 1
            if (action, name) in HINTS:
                params[name]["min_items_hint"] = HINTS[(action, name)]


apply()
