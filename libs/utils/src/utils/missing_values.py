"""Count the missing values of a column and say, in plain words, what a filter does with them (NA-RULE-63).

Decided by Eve on 2026-11-14: the engine follows Polars, so every comparison removes a row with a missing value (null);
`na: keep` adds those rows back. A NaN (a failed calculation) is a number, larger than every number, and `na` never
touches it, so it has its own count and its own sentence. Pure functions, no Shiny, no app import: the filter dialog,
the Blueprint form and the data check call the same two functions.

Consumed by: nothing yet (the wiring into the dialog, Blueprint and the data check is a later step of NA-RULE-63).
If deleted: nothing breaks today.
"""
# @deps
# provides: function:count_missing, function:missing_sentences
# consumes: —
# consumed_by: libs/utils/tests/test_missing_values.py
# doc: .claude/tasks/tasks.md#NA-RULE-63
# @end_deps
from dataclasses import dataclass
from typing import Optional, Union

import polars as pl

NA_CHOICES = ("keep", "remove")
_WARNING_OPERATORS = ("ne", "not_in")


@dataclass(frozen=True)
class MissingCounts:
    """Rows with no value (null) and rows with a failed calculation (NaN, float columns only) in one column."""
    null_rows: int
    nan_rows: int


@dataclass(frozen=True)
class MissingSentences:
    """The lines to show; a field is None when there is nothing to say."""
    missing: Optional[str]
    nan: Optional[str]
    warning: Optional[str]


def count_missing(frame: Union[pl.DataFrame, pl.LazyFrame], column: str) -> MissingCounts:
    """Return how many rows of `column` are null and, for a float column, how many are NaN (0 for any other type).

    A NaN is not counted as missing: the two counts never overlap. The text "NA" or an empty text is a value.
    """
    lf = frame.lazy()
    schema = lf.collect_schema()
    if column not in schema.names():
        raise KeyError(f"column {column!r} is not in the table")
    col = pl.col(column)
    exprs = [col.is_null().sum().alias("null_rows")]
    if schema[column].is_float():
        exprs.append(col.is_nan().fill_null(False).sum().alias("nan_rows"))
    row = lf.select(exprs).collect().row(0, named=True)
    return MissingCounts(null_rows=int(row["null_rows"]), nan_rows=int(row.get("nan_rows", 0)))


def _rows(n: int, verb_one: str, verb_many: str) -> str:
    return f"{n} row {verb_one}" if n == 1 else f"{n} rows {verb_many}"


def missing_sentences(column: str, op: str, na: str, counts: MissingCounts) -> MissingSentences:
    """Return the sentences for a filter on `column` with operator `op` and the choice `na` ("keep" or "remove").

    `missing`: "N rows have no value in <column>: they are kept / removed" (None when N is 0).
    `nan`: "N rows have a failed calculation" (None when N is 0); the same for keep and remove, na does not touch NaN.
    `warning`: only when the column has missing values and `op` is `ne` or `not_in`, where a reader expects the
    missing rows to stay; says what happens to them.
    """
    if na not in NA_CHOICES:
        raise ValueError(f"na must be one of {NA_CHOICES}, not {na!r}")
    fate = "kept" if na == "keep" else "removed"
    n, k = counts.null_rows, counts.nan_rows
    missing = None
    warning = None
    if n:
        head = _rows(n, "has", "have")
        missing = f"{head} no value in {column}: they are {fate}" if n > 1 else f"{head} no value in {column}: it is {fate}"
        if op in _WARNING_OPERATORS:
            label = "!=" if op == "ne" else "not in"
            warning = (f"{label} does not keep the rows with no value in {column} (Polars removes them too): "
                       f"here they are {fate}" + ("" if na == "keep" else "; choose na: keep to keep them"))
    nan = f"{_rows(k, 'has', 'have')} a failed calculation" if k else None
    return MissingSentences(missing=missing, nan=nan, warning=warning)
