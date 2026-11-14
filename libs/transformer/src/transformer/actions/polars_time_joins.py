"""The `polars_` actions of the group "rank, time and special joins": rank, join_asof, join_where, group_by_dynamic, rolling.

Why this module exists: these Polars methods depend on row order or on sorted keys, so each one states what it needs
and refuses a table that does not meet it (ADR-090: the same input gives the same rows in the same order; DEC33, DEC34).
They follow the form of `polars_calls.py` (Polars names and defaults read from the signature, `REQUIRED` for a choice
that changes the result, `NOT_EXPOSED` with a reason) and are kept apart from it so that several people can add actions
to the group without editing the same lines. The registration tables of `polars_calls.py` (PICKER, REQUIRED, OVERRIDE,
NOT_EXPOSED) are completed here, before the actions are defined.

What each action does when its precondition is not met (every case has a test):
  polars_rank              `method: random` without `seed`, and a `seed` with any other method, fail (Polars would run
                           with a different result every time, or ignore the seed silently).
  polars_join_asof         keys not sorted ascending, in either table and within each group of `by`, fail (Polars checks
                           only without `by`; with `by` it returns a wrong result without a word).
  polars_join_where        the row order, which Polars does not promise, is fixed: left row, then right row.
  polars_group_by_dynamic  the index column not sorted ascending (within each group when `group_by`), or holding a null, fails.
  polars_rolling           the same.

Consumed by: the action registry (`AVAILABLE_WRANGLING_ACTIONS`), the checker, Blueprint's form catalogue.
If deleted: no recipe can use these five actions.
"""
import polars as pl

from transformer.actions import polars_calls as calls
from utils.errors import TransformationError

# @deps
# provides: action:polars_rank
# consumes: libs/transformer/src/transformer/actions/polars_calls.py (the generator of the polars_ actions)
# consumed_by: libs/transformer/tests/test_polars_time_joins_equal_polars.py
# doc: .claude/design/recipe_format_spec.md#7.5.1, .claude/design/home_evidence/actions_and_polars_2026-11-13.md#19
# @end_deps

RANK_METHODS = ["average", "min", "max", "dense", "ordinal", "random"]

calls.PICKER.update({"rank": ("analytical", calls.T12)})
# the tie rule changes the result, so it is written in the step (DEC34)
calls.REQUIRED.update({"polars_rank": {"method"}})
calls.OVERRIDE.update({
    ("polars_rank", "method"): {"widget": "enum", "options": RANK_METHODS, "label": "How tied values are ranked"},
    ("polars_rank", "seed"): {"widget": "number", "label": "Seed of the random tie order (only with method random)"},
})


def _rank(lf: pl.LazyFrame, spec: dict, target) -> pl.LazyFrame:
    """Rank the listed columns; the seed is a whole number (Polars raises a Python TypeError or OverflowError otherwise)."""
    seed = spec.get("seed")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2 ** 64):
        raise TransformationError(f"step polars_rank: seed {seed!r} is not a whole number from 0 up",
                                  tip="Write the seed as a whole number such as 1")
    columns = spec["columns"]
    target_column = spec.get("target_column")
    if target_column and len(columns) != 1:
        raise TransformationError("step polars_rank: target_column needs exactly one column in `columns`",
                                  tip="Write one column, or leave target_column out to work in place")
    expression = pl.col(columns).rank(**calls._kwargs(spec, target, "polars_rank"))
    return lf.with_columns(expression.alias(target_column) if target_column else expression)


calls._define(
    "polars_rank", calls.EXPR, ("Expr", "rank"), _rank,
    "Rank the values of the listed columns, 1 for the smallest (Polars Expr.rank). `method` says how tied values rank and is written in the step; "
    "`ordinal` numbers ties in row order, so sort first; `random` needs a `seed` and every other method refuses one. "
    "A null stays null and is not counted; a NaN ranks above every number and NaNs tie with each other.",
    "- action: polars_rank\n  columns: [identity]\n  method: min\n  descending: true\n  target_column: identity_rank",
    rules=[{"when": {"method": "random"}, "require": ["seed"]},
           {"when": {"method": [m for m in RANK_METHODS if m != "random"]}, "forbid": ["seed"]}])
