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
    # an empty value returned the table unchanged (DEC36: nothing returns the table unchanged; ADR-104: no silent error)
    "polars_cast": ("columns",), "polars_cum_count": ("columns",), "polars_cum_sum": ("columns",),
    "polars_drop": ("columns",), "polars_drop_nans": ("subset",), "polars_drop_nulls": ("subset",),
    "polars_dt_truncate": ("columns",), "polars_fill_nan": ("columns",), "polars_fill_null": ("columns",),
    "polars_interpolate": ("columns",), "polars_list_join": ("columns",), "polars_list_slice": ("columns",),
    "polars_rename": ("mapping",), "polars_round": ("columns",), "polars_shift": ("columns",), "polars_sort": ("by",),
    "polars_str_extract": ("columns",), "polars_str_replace_all": ("columns",), "polars_str_split": ("columns",),
    "polars_str_splitn": ("columns",), "polars_str_strip_chars": ("columns",), "polars_unnest": ("columns",),
    "polars_with_columns": ("named_exprs",),
}

# An empty value that Polars itself gives a result other than "do nothing": not refused, and stated in the description.
EMPTY_HAS_A_MEANING = {
    ("polars_select", "exprs"): "an empty table (Polars select with nothing)",
    ("polars_unpivot", "on"): "no value columns, so no rows",
    ("polars_unpivot", "index"): "no id columns: every column is unpivoted",
    ("polars_group_by", "named_aggs"): "the distinct groups only",
    ("polars_group_by", "by"): "one row for the whole table",
    ("polars_group_by_dynamic", "group_by"): "no grouping: the windows of the whole table",
    ("polars_rolling", "group_by"): "no grouping: the windows of the whole table",
    ("polars_top_k", "by"): "the first k rows in table order",
    ("polars_bottom_k", "by"): "the first k rows in table order",
    ("polars_describe", "percentiles"): "the statistics without percentiles",
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
    for (action, name), meaning in EMPTY_HAS_A_MEANING.items():
        schema = ACTION_SCHEMAS[action]
        assert name in schema["params"], f"{action} has no parameter {name}"
        schema["description"] = schema["description"].rstrip() + f" An empty `{name}` gives {meaning}."


apply()
