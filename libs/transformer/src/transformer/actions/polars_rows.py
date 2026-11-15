"""The `polars_` actions of the group "rows": pick, cut, number and drop rows (Polars 1.40.1 LazyFrame methods).

Why this module exists: a recipe maker needs the table-step methods that choose rows by position or by rank
(`head`, `tail`, `slice`, `limit`, `gather_every`, `top_k`, `bottom_k`), turn the row order around (`reverse`), number
the rows (`with_row_index`) and drop rows by a test (`remove`). Each one is an exact wrapper of the Polars method of the
same name, built with the helpers of `polars_calls.py` (parameters read from the Polars signature, the same step
judgement, the same formula check), so a Polars release that changes a signature shows up in the registry tests.

Row order (ADR-090). Polars promises no row order unless it is asked for, and these actions work on positions or ranks:
what they return depends on the order of the table at that step. Each description states its rule, and
`libs/transformer/tests/test_polars_rows_order.py` checks it on data large enough that a random order would show.
A recipe that needs a fixed result writes a `polars_sort` with `maintain_order: true` before the step.

Consumed by: the action registry (`AVAILABLE_WRANGLING_ACTIONS`), the checker, Blueprint's form catalogue.
If deleted: no recipe can use these ten actions.
"""
from typing import Any, Dict

import polars as pl

from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS, register_action
from transformer.actions.polars_calls import (FRAME, NOT_EXPOSED, OVERRIDE, PICKER, REQUIRED, _checked, _formula, _frame,
                                              _schema)
from utils.errors import TransformationError

# @deps
# provides: action:polars_head, action:polars_tail, action:polars_slice, action:polars_limit, action:polars_top_k, action:polars_bottom_k, action:polars_reverse, action:polars_gather_every, action:polars_with_row_index, action:polars_remove
# consumes: libs/transformer/src/transformer/actions/polars_calls.py (_frame, _schema, _checked, _formula), libs/utils/src/utils/ui_schema.py
# consumed_by: libs/transformer/tests/test_polars_rows_equal_polars.py, libs/transformer/tests/test_polars_rows_order.py, libs/transformer/tests/test_registry_polars_rules.py
# doc: .claude/design/home_evidence/actions_and_polars_2026-11-13.md#19
# @end_deps

ALL3, T12 = ["t1", "t2", "assembly"], ["t1", "t2"]
PICKER.update({
    "head": ("rows", T12), "tail": ("rows", T12), "slice": ("rows", T12), "limit": ("rows", T12),
    "top_k": ("rows", T12), "bottom_k": ("rows", T12), "reverse": ("rows", T12), "gather_every": ("rows", T12),
    "with_row_index": ("rows", ALL3), "remove": ("rows", T12),
})

# What Polars defaults and a recipe must say, because the default hides a choice that changes the result (DEC34):
# how many rows, the name of the new column. `offset` of with_row_index and gather_every defaults to 0 (the first row): same as Polars.
REQUIRED.update({
    "polars_head": {"n"}, "polars_tail": {"n"}, "polars_limit": {"n"},
    "polars_with_row_index": {"name"},
})
# `reverse` of top_k and bottom_k is a bool for all the columns or one bool per column (Polars): the form accepts both
REVERSE_FORM = {"widget": "any", "label": "Reverse: true or false for all columns, or a list with one value per column"}
OVERRIDE.update({("polars_top_k", "reverse"): REVERSE_FORM, ("polars_bottom_k", "reverse"): REVERSE_FORM})
# a count or a position is a number (the generic rule would make a parameter without a default a text field)
OVERRIDE.update({("polars_top_k", "k"): {"widget": "number", "label": "k: how many rows"},
                 ("polars_bottom_k", "k"): {"widget": "number", "label": "k: how many rows"},
                 ("polars_slice", "offset"): {"widget": "number", "label": "Offset: the first row kept (the first row of the table is 0)"},
                 ("polars_slice", "length"): {"widget": "number", "label": "Length: how many rows (absent: to the end)"},
                 ("polars_gather_every", "n"): {"widget": "number", "label": "n: keep every n-th row"}})
NOT_EXPOSED["polars_remove"] = {
    "constraints": "an equality written as a keyword (`remove(col=value)`) is the formula `pl.col('col') == value` in `predicates`; one way to write each test"}

TIE_RULE = ("It returns exactly `k` rows. When several rows are tied at the cut, only some of them are kept, and which ones is not fixed: "
            "Polars keeps the first tied rows on a small table, other rows on a large one, and in the low-memory (streaming) engine the kept rows can differ from run to run. "
            "A NaN (a failed calculation) counts as the largest value and comes first; a missing value is skipped, but rows with no value fill the `k` rows when the real values run out. "
            "To always keep the same rows, end `by` with a row number (write a polars_with_row_index step first and give its column last in `by`), "
            "or write polars_sort with maintain_order: true and then polars_head. "
            "To keep every row tied with the `k` best (possibly more than `k` rows), write polars_rank with method min, then a modif_filter on the rank.")
POSITION_RULE = "It works on the order of the table at this step: after an unsorted or reshaping step, write a polars_sort with maintain_order: true first."

_frame("polars_head", "head", f"Keep the first `n` rows (Polars LazyFrame.head). {POSITION_RULE} `n` is written in the step.",
       "- action: polars_head\n  n: 100")
_frame("polars_tail", "tail", f"Keep the last `n` rows, in the table order (Polars LazyFrame.tail). {POSITION_RULE} `n` is written in the step.",
       "- action: polars_tail\n  n: 100")
_frame("polars_limit", "limit", f"Keep the first `n` rows (Polars LazyFrame.limit, the same as head). {POSITION_RULE} `n` is written in the step.",
       "- action: polars_limit\n  n: 100")
_frame("polars_slice", "slice", f"Keep `length` rows from row `offset` on, to the end when `length` is absent (Polars LazyFrame.slice; the first row is 0, a negative offset counts from the end). {POSITION_RULE}",
       "- action: polars_slice\n  offset: 10\n  length: 5")
_frame("polars_gather_every", "gather_every", f"Keep every `n`-th row, starting at row `offset` (Polars LazyFrame.gather_every; the first row is 0). {POSITION_RULE}",
       "- action: polars_gather_every\n  n: 2\n  offset: 0")
_frame("polars_top_k", "top_k", f"Keep the `k` rows with the largest values of `by`, largest first (Polars LazyFrame.top_k). The order of the result is the order of the values; {TIE_RULE}",
       "- action: polars_top_k\n  k: 10\n  by: [identity, sample_row]\n  reverse: false")
_frame("polars_bottom_k", "bottom_k", f"Keep the `k` rows with the smallest values of `by`, smallest first (Polars LazyFrame.bottom_k). The order of the result is the order of the values; {TIE_RULE}",
       "- action: polars_bottom_k\n  k: 10\n  by: [identity, sample_row]\n  reverse: false")
_frame("polars_reverse", "reverse", "Turn the row order around: the last row becomes the first (Polars LazyFrame.reverse). The result is exactly the table of the step read from the end; it does not sort.",
       "- action: polars_reverse")
_frame("polars_with_row_index", "with_row_index",
       "Add a column that numbers the rows 0, 1, 2, ... as the first column (Polars LazyFrame.with_row_index; UInt32). The number is the position in the order of the table at this step. " + POSITION_RULE +
       " `name` is written in the step; a column of that name must not exist.",
       "- action: polars_with_row_index\n  name: sample_row\n  offset: 0")


def _require_columns(action: str, used, names) -> None:
    """A column that is not in the table at this step gives the plain message of the engine, not a Polars plan dump."""
    for column in used:
        if column not in names:
            raise TransformationError(f"step {action}: column {column!r} is not in the table",
                                      tip="Write a column that exists at this step; the action never skips a missing column")


def _ranking_checks_columns(action: str) -> None:
    inner = AVAILABLE_WRANGLING_ACTIONS[action]

    def checked(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
        by = spec.get("by")
        if isinstance(by, list):
            _require_columns(action, [c for c in by if isinstance(c, str)], lf.collect_schema().names())
        return inner(lf, spec)

    checked.__name__, checked.__doc__ = inner.__name__, inner.__doc__
    AVAILABLE_WRANGLING_ACTIONS[action] = checked


for _name in ("polars_top_k", "polars_bottom_k"):
    _ranking_checks_columns(_name)


def _remove_schema():
    schema = _schema("polars_remove", FRAME, pl.LazyFrame.remove, ("LazyFrame", "remove"),
                     "Drop the rows where every predicate is true, keep all others (Polars LazyFrame.remove, the opposite of filter). A row for which the predicate is null is KEPT "
                     "(a filter would drop it), so `remove` of `pl.col('x') > 1` keeps the rows where x is missing. Several predicates are combined with AND. Rows keep their order. "
                     "A predicate must be a true/false condition (a comparison such as `pl.col('x') > 0`); a number or text formula is refused.",
                     "- action: polars_remove\n  predicates:\n    - \"pl.col('identity') < 90\"")
    schema["polars"] = "wrapper"
    schema["params"]["predicates"] = {"widget": "list", "item_widget": "expression", "required": True,
                                      "label": "Rows to remove: one or more Polars boolean expressions as text, combined with AND"}
    return schema


def _remove_action(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = _checked("polars_remove", spec)
    if not clean["predicates"]:
        raise TransformationError("step polars_remove: `predicates` is empty, so no row would be tested",
                                  tip="Write at least one Polars boolean expression, for example pl.col('identity') < 90")
    names = lf.collect_schema().names()
    predicates = []
    for text in clean["predicates"]:
        predicate = _formula(text)
        _require_columns("polars_remove", predicate.meta.root_names(), names)
        dtype = lf.select(predicate.alias("_predicate")).collect_schema()["_predicate"]
        if dtype != pl.Boolean:
            raise TransformationError(f"step polars_remove: the predicate {text!r} is not a true/false condition (it gives {dtype}), so it would remove rows by accident",
                                      tip="Write a comparison, for example pl.col('a') > 0")
        predicates.append(predicate)
    return lf.remove(*predicates)


register_action("polars_remove", ui_schema=_remove_schema())(_remove_action)
