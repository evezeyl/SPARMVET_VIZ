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
import re
from typing import Any, Dict, List, Optional, Tuple

import polars as pl

from transformer.actions import polars_calls as calls
from transformer.actions.base import register_action
from utils.action_names import JOIN_ASOF, JOIN_WHERE
from utils.errors import TransformationError

# @deps
# provides: action:polars_rank, action:polars_join_asof, action:polars_join_where, action:polars_group_by_dynamic
# consumes: libs/transformer/src/transformer/actions/polars_calls.py (the generator of the polars_ actions)
# consumed_by: libs/transformer/tests/test_polars_time_joins_equal_polars.py
# doc: .claude/design/recipe_format_spec.md#7.5.1, .claude/design/home_evidence/actions_and_polars_2026-11-13.md#19
# @end_deps

RANK_METHODS = ["average", "min", "max", "dense", "ordinal", "random"]

calls.PICKER.update({"rank": ("analytical", calls.T12), "join_asof": ("relational", calls.ASSEMBLY),
                    "join_where": ("relational", calls.ASSEMBLY),
                    "group_by_dynamic": ("aggregation", calls.T2ASM)})
# the tie rule changes the result, so it is written in the step (DEC34)
calls.REQUIRED.update({"polars_rank": {"method"}, "polars_join_asof": {"strategy"}, "polars_join_where": {"predicates"},
                       "polars_group_by_dynamic": {"closed"}})
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


# =========================================================================================================
# helpers shared by the actions that need sorted keys
# =========================================================================================================

def _not_ascending(lf: pl.LazyFrame, index: str, groups: Optional[List[str]] = None) -> bool:
    """True when `index` does not go up in the order of the rows, within each group of `groups` when given.

    Nulls are allowed before the values and nowhere else, which is the order Polars sorts them in and the one its own
    check of an as-of join accepts. A NaN is above every number. One pass that collects a single boolean.
    """
    previous = pl.col(index).shift(1)
    if groups:
        previous = previous.over(groups)
    violation = (pl.col(index) < previous) | (pl.col(index).is_null() & previous.is_not_null())
    return bool(lf.select(violation.fill_null(False).any()).collect().item())


def _require_sorted(lf: pl.LazyFrame, index: str, groups: Optional[List[str]], action: str, where: str, fix: str) -> None:
    schema = lf.collect_schema()
    missing = [c for c in [index, *(groups or [])] if c not in schema]
    if missing:
        raise TransformationError(f"step {action}: the column {missing[0]!r} is not in {where} (its columns: {list(schema)})",
                                  tip="Write the column names as they are in the table at this step")
    if _not_ascending(lf, index, groups):
        within = f" within each group of {groups}" if groups else ""
        raise TransformationError(f"step {action}: the column {index!r} of {where} is not sorted ascending{within}",
                                  tip=fix)


# =========================================================================================================
# polars_join_asof
# =========================================================================================================

ASOF_STRATEGIES = ["backward", "forward", "nearest"]
_DAYS_AND_WEEKS = re.compile(r"^(\d+[dw])+$")

calls.NOT_EXPOSED.update({"polars_join_asof": {
    "check_sortedness": "the action always checks that the keys are sorted, within each `by` group too; Polars checks only without `by` and "
                        "returns a wrong result without a word with `by`, so switching the check off would only allow a wrong result"}})
one_column = {"widget": "column_selector", "multi": False}
calls.OVERRIDE.update({
    ("polars_join_asof", "on"): {**one_column, "label": "Sorted key column, the same name in both tables"},
    ("polars_join_asof", "left_on"): {**one_column, "label": "Sorted key column of the first table"},
    ("polars_join_asof", "right_on"): {**one_column, "label": "Sorted key column of the second table"},
    ("polars_join_asof", "by_left"): {**calls.LIST_OF_COLUMNS, "label": "Columns that must be equal, of the first table"},
    ("polars_join_asof", "by_right"): {**calls.LIST_OF_COLUMNS, "label": "Columns that must be equal, of the second table"},
    ("polars_join_asof", "by"): {**calls.LIST_OF_COLUMNS, "label": "Columns that must be equal, the same names in both tables"},
    ("polars_join_asof", "strategy"): {"widget": "enum", "options": ASOF_STRATEGIES, "label": "Which row of the second table matches"},
    ("polars_join_asof", "tolerance"): {"widget": "any", "label": "Largest distance of a match: a duration text such as '2d' for a Date or Datetime key, a number for a numeric key"},
})


def _key_pair(spec: Dict[str, Any], shared: str, left: str, right: str, what: str, action: str) -> Tuple[Optional[Any], Optional[Any]]:
    """(left key, right key) from `shared`, or from `left` with `right`; a half pair is refused."""
    if spec.get(shared) is not None:
        return spec[shared], spec[shared]
    if (spec.get(left) is None) != (spec.get(right) is None):
        raise TransformationError(f"step {action}: {left} and {right} go together ({what}); only one was written",
                                  tip=f"Write both, or write {shared} when the column has the same name in both tables")
    return spec.get(left), spec.get(right)


def _check_tolerance(tolerance: Any, key_dtype: pl.DataType, key: str) -> None:
    """A tolerance the key can use; Polars panics (a Rust panic, not an error) on a duration text for a number key."""
    if isinstance(tolerance, bool) or not isinstance(tolerance, (str, int, float)):
        raise TransformationError(f"step polars_join_asof: tolerance {tolerance!r} is not a duration text or a number",
                                  tip="Write a duration text such as '2d' or '12h' for a Date or Datetime key, a number for a numeric key")
    if isinstance(tolerance, str):
        if not key_dtype.is_temporal():
            raise TransformationError(f"step polars_join_asof: the tolerance {tolerance!r} is a duration but the key {key!r} is {key_dtype}, not a date or a time",
                                      tip="Write the tolerance as a number in the unit of the key")
        if key_dtype == pl.Date and not _DAYS_AND_WEEKS.match(tolerance):
            raise TransformationError(f"step polars_join_asof: the tolerance {tolerance!r} cannot be finer than a day for the Date key {key!r}",
                                      tip="Write the tolerance in days or weeks, for example '2d'; for a time of day use a Datetime key")
        return
    if key_dtype.is_temporal():
        raise TransformationError(f"step polars_join_asof: a number as tolerance for the date or time key {key!r} would be read in the unit of the stored value "
                                  "(microseconds for a Datetime), not in seconds",
                                  tip="Write a duration text such as '2d' or '12h'")
    if tolerance < 0:
        raise TransformationError(f"step polars_join_asof: the tolerance {tolerance!r} is negative", tip="Write the largest distance as a positive number")


def _join_asof(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = calls._checked("polars_join_asof", spec)
    right = spec.get("__right_df__")
    if right is None:
        raise TransformationError("polars_join_asof needs the resolved right table (__right_df__)", tip="The assembler resolves `right_ingredient`")
    left_key, right_key = _key_pair(clean, "on", "left_on", "right_on", "the sorted key", "polars_join_asof")
    by_left, by_right = _key_pair(clean, "by", "by_left", "by_right", "the group columns", "polars_join_asof")
    fix = "Sort the table before the join with a polars_sort step (by: [{key}], maintain_order: true); the second table is sorted in its own wrangling"
    _require_sorted(lf, left_key, by_left, "polars_join_asof", "the table at this step", fix.format(key=left_key))
    _require_sorted(right, right_key, by_right, "polars_join_asof", f"'{clean['right_ingredient']}'", fix.format(key=right_key))
    if clean.get("tolerance") is not None:
        _check_tolerance(clean["tolerance"], lf.collect_schema()[left_key], left_key)
    kwargs = calls._kwargs(clean, pl.LazyFrame.join_asof, "polars_join_asof")
    kwargs.pop("other", None)
    if by_left:
        kwargs["check_sortedness"] = False  # Polars cannot check within groups and warns; the check above did it
    return lf.join_asof(right, **kwargs)


def _join_asof_schema() -> dict:
    schema = calls._schema(
        "polars_join_asof", calls.FRAME, pl.LazyFrame.join_asof, ("LazyFrame", "join_asof"),
        "Join each row of the table of the step with one row of the second table `right_ingredient`: the nearest one before it (backward), after it (forward) "
        "or closest (nearest) on a sorted key (Polars LazyFrame.join_asof); `strategy` is written in the step. Both tables must be sorted ascending on the key, "
        "within each `by` group too, or the step fails (Polars checks only without `by`, and with `by` it returns a wrong result without a word). "
        "The result keeps the rows and the order of the first table; a row without a match gets nulls. A null key never matches and a null in `by` never matches; "
        "a NaN key sorts last and matches a NaN. Without `tolerance` a match can be as far away as the data goes.",
        "- action: polars_join_asof\n  right_ingredient: weather\n  'on': sample_date\n  by: [site]\n  strategy: backward\n  tolerance: 2d",
        rules=[{"one_of": ["on", "left_on"]}, {"exclusive": ["on", "right_on"]}, {"exclusive": ["by", "by_left"]}, {"exclusive": ["by", "by_right"]}])
    schema["polars"] = "wrapper"
    return schema


register_action(JOIN_ASOF, ui_schema=_join_asof_schema())(_join_asof)


# =========================================================================================================
# polars_join_where
# =========================================================================================================

calls.OVERRIDE.update({
    ("polars_join_where", "predicates"): {"widget": "list", "value_widget": "expression",
                                          "label": "Predicates: Polars expressions as text, all of them must be true for a pair of rows"},
})


def _free_name(wanted: str, *frames: pl.LazyFrame) -> str:
    taken = {name for frame in frames for name in frame.collect_schema().names()}
    while wanted in taken:
        wanted = f"_{wanted}"
    return wanted


def _join_where(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = calls._checked("polars_join_where", spec)
    right = spec.get("__right_df__")
    if right is None:
        raise TransformationError("polars_join_where needs the resolved right table (__right_df__)", tip="The assembler resolves `right_ingredient`")
    predicates = clean["predicates"]
    if not predicates or not all(isinstance(text, str) for text in predicates):
        raise TransformationError("step polars_join_where: `predicates` is a list of one or more formulas written as text",
                                  tip="Write for example predicates: [\"pl.col('year') >= pl.col('start_year')\"]")
    expressions = [calls._formula(text) for text in predicates]
    # Polars returns the matching pairs in a different order on every run (a row index would be the only stable thing in
    # them): the pairs are put in the order of the first table, then of the second (ADR-090).
    left_row = _free_name("__row_of_first_table__", lf, right)
    right_row = _free_name("__row_of_second_table__", lf, right)
    options = {"suffix": clean["suffix"]} if clean.get("suffix") is not None else {}
    joined = lf.with_row_index(left_row).join_where(right.with_row_index(right_row), *expressions, **options)
    try:
        joined.collect_schema()  # Polars compares the types of the predicates when the plan is resolved: say it now, not at the collect
    except pl.exceptions.SchemaError as exc:
        raise TransformationError(f"step polars_join_where: {str(exc).splitlines()[0]}",
                                  tip="Compare columns of the same type: declare the same type in input_fields of both tables, or write a polars_cast step "
                                      "before the join for the first table (the second table is changed in its own input_fields or wrangling)") from exc
    return joined.sort([left_row, right_row]).drop([left_row, right_row])


def _join_where_schema() -> dict:
    schema = calls._schema(
        "polars_join_where", calls.FRAME, pl.LazyFrame.join_where, ("LazyFrame", "join_where"),
        "Join each row of the table of the step with every row of the second table `right_ingredient` for which all `predicates` are true: a join on conditions, "
        "not on equal keys (Polars LazyFrame.join_where). A predicate is a formula such as \"pl.col('v') >= pl.col('lo')\"; a column that has the same name in both tables "
        "is written with the suffix for the second table (`lo_right`). It is an inner join: a row can match several rows or none, and a row without a match is dropped. "
        "Polars returns the pairs in another order on every run; the action puts them in the order of the first table, then of the second, so the same input "
        "gives the same table. A predicate that is null for a pair (a null in a compared column) does not match; a NaN is larger than every number; "
        "columns of different number types (Int64 against Float64) cannot be compared and the step fails.",
        "- action: polars_join_where\n  right_ingredient: reference_ranges\n  predicates:\n    - \"pl.col('year') >= pl.col('start_year')\"\n    - \"pl.col('year') <= pl.col('end_year')\"")
    schema["polars"] = "wrapper"
    return schema


register_action(JOIN_WHERE, ui_schema=_join_where_schema())(_join_where)


# =========================================================================================================
# windows over a sorted index: polars_group_by_dynamic (and polars_rolling)
# =========================================================================================================

CLOSED = ["left", "right", "both", "none"]
LABELS = ["left", "right", "datapoint"]
START_BY = ["window", "datapoint", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
INDEX_INTEGERS = (pl.Int32, pl.Int64, pl.UInt32, pl.UInt64)


def _window_overrides(action: str) -> None:
    calls.OVERRIDE.update({
        (action, "index_column"): {**one_column, "label": "Index column: a date, a time or a whole number, sorted ascending"},
        (action, "group_by"): {**calls.LIST_OF_COLUMNS, "label": "Group columns: the windows are made within each group"},
        (action, "closed"): {"widget": "enum", "options": CLOSED, "label": "Which edges belong to the window"},
        (action, "label"): {"widget": "enum", "options": LABELS, "label": "Which value labels the window"},
        (action, "start_by"): {"widget": "enum", "options": START_BY, "label": "Where the first window starts"},
    })


def _duration_units(text: str) -> set:
    return set(re.findall(r"\d+([a-z]+)", text))


def _require_window_index(lf: pl.LazyFrame, clean: Dict[str, Any], action: str) -> None:
    """The index of a window is sorted ascending (within each group), has no null, and its type fits the written durations."""
    index, groups = clean["index_column"], clean.get("group_by")
    schema = lf.collect_schema()
    missing = [c for c in [index, *(groups or [])] if c not in schema]
    if missing:
        raise TransformationError(f"step {action}: the column {missing[0]!r} is not in the table at this step (its columns: {list(schema)})",
                                  tip="Write the column names as they are in the table at this step")
    dtype = schema[index]
    integer = dtype in INDEX_INTEGERS
    if not (integer or dtype.is_temporal()):
        raise TransformationError(f"step {action}: the index column {index!r} is {dtype}; windows need a date, a time or a whole number (Int32, Int64, UInt32, UInt64)",
                                  tip="Cast the column first with a polars_cast step")
    for key in ("every", "period", "offset"):
        text = clean.get(key)
        if text is None:
            continue
        if not isinstance(text, str):
            raise TransformationError(f"step {action}: {key} {text!r} is not a duration text", tip="Write a duration such as '1w', '30d' or '2i' (whole numbers use i)")
        units = _duration_units(text)
        if integer and units != {"i"}:
            raise TransformationError(f"step {action}: {key} {text!r} is a time duration but the index column {index!r} is {dtype}",
                                      tip="For a whole-number index write the duration with i, for example '2i'")
        if not integer and "i" in units:
            raise TransformationError(f"step {action}: {key} {text!r} counts whole numbers but the index column {index!r} is {dtype}",
                                      tip="For a date or a time write a duration such as '1w', '30d' or '12h'")
    if lf.select(pl.col(index).is_null().any()).collect().item():
        raise TransformationError(f"step {action}: the index column {index!r} holds null values, which Polars does not allow in windows",
                                  tip=f"Remove the rows without a value first with a polars_drop_nulls step (subset: [{index}])")
    if _not_ascending(lf, index, groups):
        within = f" within each group of {groups}" if groups else ""
        raise TransformationError(f"step {action}: the index column {index!r} is not sorted ascending{within}",
                                  tip=f"Sort first with a polars_sort step (by: [{index}], maintain_order: true)")


def _window_action(action: str, method: str):
    target = getattr(pl.LazyFrame, method)

    def run(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
        clean = calls._checked(action, spec)
        aggregations = {name: calls._formula(text) for name, text in clean["named_aggs"].items()}
        _require_window_index(lf, clean, action)
        try:
            result = getattr(lf, method)(**calls._kwargs(clean, target, action)).agg(**aggregations)
            result.collect_schema()  # the formulas are resolved now: a column that does not exist is said at this step
        except (pl.exceptions.PolarsError, ValueError) as exc:
            raise TransformationError(f"step {action}: {str(exc).splitlines()[0]}", tip="Check the durations, the column names and the formulas of the step") from exc
        return result

    run.__name__ = f"action_{action}"
    return run


def _window_schema(action: str, method: str, description: str, example: str) -> dict:
    schema = calls._schema(action, calls.FRAME, getattr(pl.LazyFrame, method), ("LazyFrame", method), description, example)
    schema["polars"] = "wrapper"
    schema["params"]["named_aggs"] = {"widget": "mapping", "label": "Result column: aggregation formula (a Polars expression as text)",
                                      "required": True, "value_widget": "expression"}
    return schema


# -- polars_group_by_dynamic -----------------------------------------------------------------------------

_window_overrides("polars_group_by_dynamic")
register_action("polars_group_by_dynamic", ui_schema=_window_schema(
    "polars_group_by_dynamic", "group_by_dynamic",
    "Cut a sorted index column (dates, times or whole numbers) into windows of the length `every` and aggregate each window with named formulas "
    "(Polars LazyFrame.group_by_dynamic(...).agg(...)). `closed`, which edges belong to a window, is written in the step because group_by_dynamic and rolling "
    "do not share a default. The index column must be sorted ascending, within each group when `group_by` is given, and must hold no null: the step fails otherwise. "
    "The result has one row per non-empty window, in the order of the groups (ascending, nulls last), then of the windows. In a window a null is skipped by "
    "sum, mean and count, a NaN makes a sum NaN, and the sum of a window that holds only nulls is 0.",
    "- action: polars_group_by_dynamic\n  index_column: collection_date\n  every: 1mo\n  closed: left\n  group_by: [country]\n  named_aggs:\n    isolates: \"pl.len()\""))(
    _window_action("polars_group_by_dynamic", "group_by_dynamic"))
