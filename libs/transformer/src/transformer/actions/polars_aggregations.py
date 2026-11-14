"""The `polars_` table aggregations: the whole table in, one row out (W6, Eve's yes 2026-11-14).

Why this module exists: Polars `LazyFrame` has twelve methods that summarise every column of the table into one row
(`sum`, `min`, `max`, `mean`, `median`, `std`, `var`, `quantile`, `count`, `null_count`, `first`, `last`). They are the
"real gaps" of `actions_and_polars_2026-11-13.md` section 19 that Eve asked to add. Each is the exact Polars call
(`polars_calls._frame`: the same parameters and defaults as Polars 1.40.1, read from the signature), so they follow
every rule of `polars_calls.py` (required parameters, a step judged before it runs, DEC33 and DEC34).

What a recipe maker must know, and what every description says in one sentence (verified by running Polars 1.40.1,
proved by `test_polars_aggregations_equal_polars.py`): the engine follows Polars for missing values and NaN (Eve,
2026-11-14). A null is skipped by every aggregation except `first`, `last` and `null_count`. A NaN is a number: it makes
`sum`, `mean`, `std` and `var` NaN, it is ignored by `min` and `max`, it counts as a value larger than every number in
`median` and `quantile`. A text column gives null in `sum`, `mean`, `median`, `std`, `var` and `quantile` (no error, the
column stays in the result); `min` and `max` order text alphabetically.

`polars_first` and `polars_last` depend on the row order of the table (ADR-090): they take the first and the last row as
the previous steps left them; write a `polars_sort` with `maintain_order` before them when the row they pick matters.

The `quantile` of Polars may be a number or an expression; a recipe writes a number (an expression cannot be written
as a parameter). Its `interpolation` has the Polars default, `nearest`, which differs from the linear interpolation of R
and numpy: write `interpolation` in the step.

Consumed by: the action registry (`AVAILABLE_WRANGLING_ACTIONS`), the checker, Blueprint's form catalogue.
If deleted: no recipe can use a `polars_` table aggregation.
"""
import typing

from polars._typing import QuantileMethod

from transformer.actions.base import ACTION_SCHEMAS
from transformer.actions.polars_calls import PICKER, T2ASM, _frame

# @deps
# provides: action:polars_sum, action:polars_min, action:polars_max, action:polars_mean, action:polars_median, action:polars_std, action:polars_var, action:polars_quantile, action:polars_count, action:polars_null_count, action:polars_first, action:polars_last
# consumes: libs/transformer/src/transformer/actions/polars_calls.py (_frame, PICKER)
# consumed_by: libs/transformer/tests/test_polars_aggregations_equal_polars.py, libs/transformer/tests/test_registry_polars_rules.py
# doc: .claude/design/home_evidence/actions_and_polars_2026-11-13.md#19
# @end_deps

AGGREGATIONS = ["sum", "min", "max", "mean", "median", "std", "var", "quantile", "count", "null_count", "first", "last"]

# the Blueprint picker: the same place as `polars_group_by` (a whole-table aggregation is not a shared trunk step)
PICKER.update({name: ("aggregation", T2ASM) for name in AGGREGATIONS})

_frame("polars_sum", "sum",
       "Sum of each column, one row (Polars LazyFrame.sum). A null is skipped (a column with only nulls gives 0), a NaN makes the sum NaN, "
       "a Boolean column counts its true values, a text column gives null.",
       "- action: polars_sum")
_frame("polars_min", "min",
       "Smallest value of each column, one row (Polars LazyFrame.min). A null is skipped (only nulls gives null), a NaN is ignored (only NaN gives NaN), "
       "a text column gives its first value in alphabetical order.",
       "- action: polars_min")
_frame("polars_max", "max",
       "Largest value of each column, one row (Polars LazyFrame.max). A null is skipped (only nulls gives null), a NaN is ignored (only NaN gives NaN), "
       "a text column gives its last value in alphabetical order.",
       "- action: polars_max")
_frame("polars_mean", "mean",
       "Mean of each column, one row (Polars LazyFrame.mean). A null is skipped, a NaN makes the mean NaN, a text column gives null.",
       "- action: polars_mean")
_frame("polars_median", "median",
       "Median of each column, one row (Polars LazyFrame.median). A null is skipped; a NaN is not skipped, it counts as a value larger than every number "
       "(it does not make the median NaN unless it is the middle value); a text column gives null.",
       "- action: polars_median")
_frame("polars_std", "std",
       "Standard deviation of each column, one row (Polars LazyFrame.std); `ddof` is the delta degrees of freedom, 1 in Polars (the sample standard deviation). "
       "A null is skipped, a NaN makes the result NaN, fewer than `ddof` + 1 values give null, a text column gives null.",
       "- action: polars_std\n  ddof: 1")
_frame("polars_var", "var",
       "Variance of each column, one row (Polars LazyFrame.var); `ddof` is the delta degrees of freedom, 1 in Polars (the sample variance). "
       "A null is skipped, a NaN makes the result NaN, fewer than `ddof` + 1 values give null, a text column gives null.",
       "- action: polars_var\n  ddof: 1")
_frame("polars_quantile", "quantile",
       "The quantile (0 to 1) of each column, one row (Polars LazyFrame.quantile); `interpolation` is `nearest` in Polars, not linear: write it in the step. "
       "A null is skipped; a NaN is not skipped, it counts as a value larger than every number; a text or Boolean column gives null.",
       "- action: polars_quantile\n  quantile: 0.5\n  interpolation: linear")
_frame("polars_count", "count",
       "Number of values that are not null in each column, one row (Polars LazyFrame.count). A null is not counted, a NaN is counted (it is a value), "
       "every type of column can be counted.",
       "- action: polars_count")
_frame("polars_null_count", "null_count",
       "Number of nulls in each column, one row (Polars LazyFrame.null_count). Only a null is counted, a NaN is not a null, every type of column can be counted.",
       "- action: polars_null_count")
_frame("polars_first", "first",
       "The first row of the table, one row (Polars LazyFrame.first). It takes the row the previous steps left first: the order of the rows decides the result "
       "(ADR-090), so write a polars_sort with `maintain_order` before it when the row matters. A null in that row stays null (it is not skipped); an empty table gives no row.",
       "- action: polars_first")
_frame("polars_last", "last",
       "The last row of the table, one row (Polars LazyFrame.last). It takes the row the previous steps left last: the order of the rows decides the result "
       "(ADR-090), so write a polars_sort with `maintain_order` before it when the row matters. A null in that row stays null (it is not skipped); an empty table gives no row.",
       "- action: polars_last")


# Two parameters whose form Polars types as something a recipe cannot write: a number or an expression (`quantile`), and
# the list of the interpolation methods, which the shared hint of `polars_calls` does not hold completely.
_QUANTILE = ACTION_SCHEMAS["polars_quantile"]["params"]
_QUANTILE["quantile"] = {**_QUANTILE["quantile"], "widget": "number", "label": "Quantile, from 0 to 1 (0.5 is the median)"}
_QUANTILE["interpolation"] = {**_QUANTILE["interpolation"], "options": list(typing.get_args(QuantileMethod))}
