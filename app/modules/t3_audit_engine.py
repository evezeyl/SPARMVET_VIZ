"""app/modules/t3_audit_engine.py
Pure helpers extracted from home_theater.py (Phase 24-A, ADR-051).

Two-Category Law (ADR-045): this module is a non-Shiny module
(no @render.* / @reactive.* decorators) and may be imported from any
context — handlers, modules, scripts, tests.

Initial scope (24-A): _apply_filter_rows. Future steps will add
extract_t3_filter_rows / extract_t3_drop_columns.
"""

from __future__ import annotations

# @deps
# provides: function:dialog_value, function:column_types, function:value_choices, function:pick_values, function:number_range, function:typed_number, function:ops_for_column, function:value_widget_for, function:column_type_line, function:closed_phrase, function:between_prose, constant:CLOSED_CHOICES, function:_apply_filter_rows, function:filter_rows_from_nodes, function:staged_filter_row, function:audit_params_from_row, function:inapplicable_filter_rows, function:describe_filter, function:op_choice_label
# consumes: polars, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py
# consumed_by: app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/export_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

import math

import polars as pl

from utils.filter_values import FilterValueError, filter_condition, kind_of, read_filter_value, type_words
from utils.missing_values import keep_missing
from utils.na_choice import default_na, na_of


def _op_label(op: str) -> str:
    """Symbolic label for a filter operator (used in UI rendering and reports).

    Lives here (not in a UI module) so that both filter_and_audit_handlers and
    export_handlers can share one definition. ADR-045 compliant — pure, no Shiny.
    """
    return {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
            "lt": "<", "le": "≤", "in": "∈", "not_in": "∉"}.get(op, op)


# One vocabulary for every place an operator is shown: the operator dropdown, the staged filter
# list, the audit panel (issue #57). symbol = short form, words = what it means.
OP_WORDS = {
    "eq": ("=", "equals"), "ne": ("≠", "not equal"),
    "gt": (">", "greater than"), "ge": ("≥", "greater or equal"),
    "lt": ("<", "less than"), "le": ("≤", "less or equal"),
    "in": ("∈", "any of"), "not_in": ("∉", "none of"),
    "between": ("↔", "between"),
}


def op_choice_label(op: str) -> str:
    """Dropdown text for an operator: symbol plus words, e.g. '≠ not equal'."""
    sym, words = OP_WORDS.get(op, (op, op))
    return f"{sym} {words}"


# What a staged line adds for `between` when the ends are not both included (never silent).
_CLOSED_SUFFIX = {"left": ", lower end included, upper end not", "right": ", upper end included, lower end not", "none": ", ends not included"}


def describe_filter(column: str, op: str, value, na: str | None = None, closed: str | None = None) -> str:
    """One-line text of a filter row. A one-value set reads as equality ('sequence_type = 101'),
    several values read 'any of' / 'none of' (issue #57). With `na` ("keep" or "remove") the line ends with what
    happens to the rows with no value in the column (NA-RULE-63). an end that is not included in a `between` is said, never silent."""
    text = _describe_condition(column, op, value)
    if op == "between" and closed in _CLOSED_SUFFIX:
        text += _CLOSED_SUFFIX[closed]
    if na is None:
        return text
    return f"{text} ({na_phrase(na)})"


def na_phrase(na: str) -> str:
    """'rows with no value kept' / 'rows with no value removed': the choice `na` in a few words."""
    return "rows with no value kept" if na == "keep" else "rows with no value removed"


def _describe_condition(column: str, op: str, value) -> str:
    vals = value if isinstance(value, (list, tuple)) else None
    if vals is not None and len(vals) == 1:
        op, vals = {"in": "eq", "not_in": "ne"}.get(op, op), None
        value = value[0]
    if op == "between" and isinstance(value, (list, tuple)) and len(value) == 2:
        return f"{column} between {value[0]} and {value[1]}"
    sym, words = OP_WORDS.get(op, (op, op))
    if vals is not None:
        return f"{column} {words} {', '.join(str(v) for v in vals)}"
    return f"{column} {sym} {value}"


# -- the pure side of the HOME filter dialog (ADR-104 points 4, 7 and 8) ---------------------------------------------

# The four ends of `between`, as the dialog shows them (the words of the choice, in the order of the radio).
CLOSED_CHOICES = {
    "both": "both ends included (min ≤ value ≤ max)",
    "left": "min included, max not (min ≤ value < max)",
    "right": "max included, min not (min < value ≤ max)",
    "none": "neither end included (min < value < max)",
}
_CLOSED_PHRASE = {
    "both": "both ends included", "left": "the lower end included, the upper end not",
    "right": "the upper end included, the lower end not", "none": "neither end included",
}


def closed_phrase(closed: str) -> str:
    """The ends of a `between` in words, for a report: 'both ends included', 'neither end included', ..."""
    return _CLOSED_PHRASE[closed]


def between_prose(value, closed: str) -> str:
    """The report sentence of a `between`: 'between "89" and "91", both ends included'."""
    return f'between "{value[0]}" and "{value[1]}", {closed_phrase(closed)}'


def column_types(lf) -> dict:
    """Column name -> dtype, from the schema of the table (not from a sample of rows)."""
    schema = lf.collect_schema()
    return {name: schema[name] for name in schema.names()}


def column_type_line(column: str, dtype) -> str:
    """What the filter dialog shows next to the column: 'Year holds whole numbers (Int64).'"""
    return f"{column} holds {type_words(dtype)} ({dtype})."


def value_choices(lf, column: str) -> dict:
    """The values of the whole column as the dialog lists them: {text shown: real value}, sorted, no missing value.

    The real value is a number for a number column, True or False for a true/false column, text for the rest. A date is
    kept as its year-month-day text (a session file holds no date object; the export types it from the dtype). NaN is not
    listed: it is counted on its own and treated by its own steps (ADR-103).
    """
    kind = kind_of(column_types(lf).get(column))
    values = lf.select(pl.col(column).drop_nulls().unique()).collect()[column].to_list()
    if kind == "float":
        values = [float(v) for v in values if not (isinstance(v, float) and math.isnan(v))]
    if kind in ("int", "float", "bool", "date"):
        values = sorted(values)
    choices: dict = {}
    for v in values:
        label = v.isoformat() if kind == "date" else str(v)
        choices[label] = label if kind in ("date", "other") else v
    if kind in ("text", "other"):
        choices = dict(sorted(choices.items()))
    return choices


def pick_values(choices: dict, labels) -> list:
    """The real values of the texts the user picked, in the order picked; a text that is not in the column is reported."""
    missing = [label for label in labels if label not in choices]
    if missing:
        raise FilterValueError(f"The value {missing[0]!r} is not in the column any more",
                               "open the list again and pick the values from it")
    return [choices[label] for label in labels]


def number_range(lf, column: str):
    """(smallest, largest) of the whole column for the number box, or None when it has no number."""
    kind = kind_of(column_types(lf).get(column))
    expr = pl.col(column).drop_nans() if kind == "float" else pl.col(column)
    row = lf.select(expr.min().alias("lo"), expr.max().alias("hi")).collect().row(0)
    return None if row[0] is None else (row[0], row[1])


def typed_number(raw, dtype):
    """A number of the number box in the type of the column (an integer column keeps an integer, a decimal column a decimal)."""
    return read_filter_value(raw, dtype)


def ops_for_column(dtype, discrete_axis: bool) -> list:
    """The operators the dialog offers for a column of `dtype`.

    A number column offers the comparisons and `between`; when the plot uses it as a discrete axis it also offers the list
    operators first, so that a list can be picked and "> 1998 and < 2003" can still be written (Eve, 2026-11-14). Every
    other column offers the list operators. Comparisons on text, dates and true/false columns are not decided.
    """
    numbers = ["eq", "ne", "gt", "ge", "lt", "le", "between"]
    if kind_of(dtype) in ("int", "float"):
        return ["in", "not_in"] + numbers if discrete_axis else numbers
    return ["in", "not_in", "eq", "ne"]


def value_widget_for(dtype, discrete_axis: bool, op: str) -> str:
    """The widget of the value: "list" (pick values), "number" (one number box) or "range" (two number boxes, `between`)."""
    if kind_of(dtype) not in ("int", "float"):
        return "list"
    if op == "between":
        return "range"
    if op in ("in", "not_in") or (op in ("eq", "ne") and discrete_axis):
        return "list"
    return "number"


def dialog_value(lf, column: str, dtype, discrete_axis: bool, op: str, *, picked=(), number=None, low=None, high=None,
                 closed: str = "both", text: str = ""):
    """What "+ Add" writes into the filter row: (operator, real value, ends), or None when nothing is chosen yet.

    The value has the type of the column (ADR-104 point 7): values picked from a list are looked up in the map of the whole
    column, a number of a number box is typed from the dtype, the two bounds of `between` are typed and put in order. eq or ne
    on a list means in or not_in. Without a table (`dtype` None) the text is kept as written. Raises FilterValueError when a
    value cannot be read in the type of the column.
    """
    widget = value_widget_for(dtype, discrete_axis, op) if dtype is not None else "text"
    if widget == "range":
        if low is None or high is None:
            return None
        low, high = typed_number(low, dtype), typed_number(high, dtype)
        return op, ([high, low] if low > high else [low, high]), (closed if closed in CLOSED_CHOICES else "both")
    if widget == "list":
        labels = list(picked or ())
        if not labels:
            return None
        return {"eq": "in", "ne": "not_in"}.get(op, op), pick_values(value_choices(lf, column), labels), "both"
    if widget == "number":
        return (op, typed_number(number, dtype), "both") if number is not None else None
    text = (text or "").strip()
    return (op, text, "both") if text else None


def inapplicable_filter_rows(lf, filter_rows: list) -> list:
    """Filter rows whose column is absent from lf; they are skipped, not applied (issue #56)."""
    try:
        names = set(lf.collect_schema().names())
    except Exception:
        return []
    return [f for f in filter_rows if f.get("column") is not None and f.get("column") not in names]


def filter_rows_from_nodes(nodes: list) -> list[dict]:
    """The filter rows of the active `filter_row` and `exclusion_row` audit steps, with their `na` choice.

    A step written before the choice existed has no `na` and is carried as "remove", what it always did.
    """
    rows: list[dict] = []
    for n in nodes:
        if not n.get("active", True) or n.get("node_type") not in ("filter_row", "exclusion_row"):
            continue
        p = n.get("params", {})
        if "column" not in p:
            continue
        row = {
            "column": p.get("column"),
            "op": p.get("op", "eq"),
            "value": p.get("value"),
            "dtype": p.get("dtype", "Utf8"),
            "na": na_of(p),
        }
        if row["op"] == "between":
            row["closed"] = p.get("closed", "both")
        rows.append(row)
    return rows


def staged_filter_row(column: str, op: str, value, dtype: str, na_tick: bool | None, closed: str = "both") -> dict:
    """The filter row the "+ Add" button stages: the tick of the dialog is recorded, never dropped.

    `na_tick` True keeps the rows with no value, False removes them; None (the tick is not mounted) is the default of
    the operator. `closed` is written for `between` only.
    """
    keep = default_na(op) == "keep" if na_tick is None else bool(na_tick)
    row = {"column": column, "op": op, "value": value, "dtype": dtype, "na": "keep" if keep else "remove"}
    if op == "between":
        row["closed"] = closed
    return row


def audit_params_from_row(frow: dict) -> dict:
    """The params of the audit step built from a staged row on "Send to Audit": everything the user chose.

    `na` (keep or remove the rows with no value) and, for `between`, `closed` are carried exactly as chosen. A row of an
    older state without `na` is "remove".
    """
    params = {"column": frow.get("column", ""), "op": frow.get("op", "eq"), "value": frow.get("value", ""), "na": na_of(frow)}
    if frow.get("dtype"):
        params["dtype"] = frow["dtype"]
    if params["op"] == "between":
        params["closed"] = frow.get("closed", "both")
    return params


def _apply_filter_rows(lf, filter_rows: list) -> "pl.LazyFrame":
    """
    Apply a list of {column, op, value, dtype, na, closed} dicts to a LazyFrame.

    Type strategy (ADR-104 point 7): a value has the type of its column. The dtype of the column is read from the
    schema of the table each call (the stored 'dtype' of a row can be stale or absent). A value an older row holds as
    text is read as that type; a value that cannot be read stops with a plain `FilterValueError`, it is never guessed.
    The condition itself is `utils.filter_values.filter_condition`, shared with the plot and the recipe action
    (eq or ne with a list mean in or not_in; in and not_in compare typed values).
    """
    try:
        schema = lf.collect_schema()
        actual_dtypes = {name: schema[name] for name in schema.names()}
    except Exception:
        actual_dtypes = {}

    for f in filter_rows:
        col = f.get("column")
        if col is None:
            continue
        # Issue #56: T1 is wide and T2 may be long, so a filter built on one view can name a
        # column the active view does not have. Skip it (see inapplicable_filter_rows) rather than crash.
        if actual_dtypes and col not in actual_dtypes:
            continue
        dtype = actual_dtypes.get(col) or f.get("dtype")
        condition = filter_condition(col, f.get("op", "eq"), f.get("value"), dtype, f.get("closed", "both"))
        # NA-RULE-63: "keep" adds the rows with no value; a row without `na` removes them
        lf = lf.filter(keep_missing(condition, col, na_of(f)))
    return lf
