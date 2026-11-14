"""Count the missing values of a column and say, in plain words, what a filter does with them (NA-RULE-63).

Decided by Eve on 2026-11-14: the engine follows Polars, so every comparison removes a row with a missing value (null);
`na: keep` adds those rows back. A NaN (a failed calculation) is a number, larger than every number, and `na` never
touches it, so it has its own count and its own sentence. Pure functions, no Shiny, no app import: the filter dialog,
the Blueprint form and the data check call the same two functions.

Also `keep_missing` (adds the null rows to a filter condition), used by the HOME table and the plot. The choice itself
(`na_of`, `default_na`, `with_na`) is in `na_choice.py`, which needs no Polars so the audit translator can use it.

Consumed by: app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py,
app/handlers/filter_and_audit_handlers.py.
If deleted: HOME and the plot cannot apply the choice `na`, and the dialog shows no counts.
"""
# @deps
# provides: function:count_missing, function:missing_sentences, function:keep_missing, function:dialog_missing_lines, function:na_choice_texts
# consumes: polars, libs/utils/src/utils/na_choice.py
# consumed_by: libs/utils/tests/test_missing_values.py, app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py, app/handlers/filter_and_audit_handlers.py
# doc: .claude/tasks/tasks.md#NA-RULE-63
# @end_deps
from dataclasses import dataclass
from typing import Optional, Union

import polars as pl

from utils.na_choice import NA_CHOICES

_WARNING_OPERATORS = ("ne", "not_in")


def keep_missing(condition: pl.Expr, column: str, na: str) -> pl.Expr:
    """Return `condition` as is for "remove"; for "keep" also true on the rows where `column` is null.

    NaN is a number and is never touched by `na`.
    """
    if na not in NA_CHOICES:
        raise ValueError(f"na must be one of {NA_CHOICES}, not {na!r}")
    return condition | pl.col(column).is_null() if na == "keep" else condition


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


def dialog_missing_lines(column: str, op: str, na: str, counts: MissingCounts) -> list[str]:
    """The lines the HOME filter dialog shows under the tick: the counts (missing values and NaN apart) and the warning.

    Says so when no row has a missing value, so the user sees that the choice changes nothing here.
    """
    s = missing_sentences(column, op, na, counts)
    lines = [s.missing or f"No row has a missing value in {column}."]
    if s.nan:
        lines.append(f"{s.nan} (NaN): not changed by this choice")
    if s.warning:
        lines.append(s.warning)
    return lines


def na_choice_texts(op_words: str) -> tuple[str, str]:
    """The label of the tick and the one-line help for an operator (`op_words`: "not equal", "any of", ...)."""
    label = "Keep the rows with no value in this column"
    help_ = (f"With '{op_words}', a row with no value does not match. "
             "Tick: these rows are kept anyway. Untick: they are removed.")
    return label, help_
