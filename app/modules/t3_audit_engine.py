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
# provides: function:_apply_filter_rows, function:filter_rows_from_nodes, function:staged_filter_row, function:audit_params_from_row, function:inapplicable_filter_rows, function:describe_filter, function:op_choice_label
# consumes: polars, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py
# consumed_by: app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/export_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

import polars as pl

from utils.filter_values import filter_condition
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


def describe_filter(column: str, op: str, value, na: str | None = None, closed: str | None = None) -> str:
    """One-line text of a filter row. A one-value set reads as equality ('sequence_type = 101'),
    several values read 'any of' / 'none of' (issue #57). With `na` ("keep" or "remove") the line ends with what
    happens to the rows with no value in the column (NA-RULE-63). `closed` "none" of a `between` is said, never silent."""
    text = _describe_condition(column, op, value)
    if op == "between" and closed == "none":
        text += ", ends not included"
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
