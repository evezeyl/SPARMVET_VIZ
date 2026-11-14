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
# provides: function:_apply_filter_rows, function:filter_rows_from_nodes, function:inapplicable_filter_rows, function:describe_filter, function:op_choice_label
# consumes: polars, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py
# consumed_by: app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/export_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

import polars as pl

from utils.filter_values import coerce_filter_value
from utils.missing_values import keep_missing
from utils.na_choice import na_of


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


def describe_filter(column: str, op: str, value, na: str | None = None) -> str:
    """One-line text of a filter row. A one-value set reads as equality ('sequence_type = 101'),
    several values read 'any of' / 'none of' (issue #57). With `na` ("keep" or "remove") the line ends with what
    happens to the rows with no value in the column (NA-RULE-63)."""
    text = _describe_condition(column, op, value)
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
        rows.append({
            "column": p.get("column"),
            "op": p.get("op", "eq"),
            "value": p.get("value"),
            "dtype": p.get("dtype", "Utf8"),
            "na": na_of(p),
        })
    return rows


def _apply_filter_rows(lf, filter_rows: list) -> "pl.LazyFrame":
    """
    Apply a list of {column, op, value, dtype, na} dicts to a LazyFrame.

    Type strategy (DEMO-3):
    - The filter row's stored 'dtype' field can be stale or absent. We
      re-read the actual column dtype from the LazyFrame schema each call
      and cast accordingly — this is the source of truth.
    - Numeric scalar ops (gt/ge/lt/le/eq/ne): coerce string value to
      column dtype before comparison.
    - Set ops (in/not_in) with list of values: always cast both sides to
      Utf8 for the comparison (selectize returns strings regardless of
      column dtype, so the safest path is string-equality).
    - Auto-promotes eq/ne to in/not_in when value is a list.
    """
    # Source-of-truth dtype map from the actual LazyFrame schema
    try:
        schema = lf.collect_schema()
        actual_dtypes = {name: schema[name] for name in schema.names()}
    except Exception:
        actual_dtypes = {}

    def _is_numeric(dt) -> bool:
        return dt is not None and any(
            t in str(dt) for t in ("Int", "UInt", "Float", "Decimal")
        )

    for f in filter_rows:
        col = f.get("column")
        op = f.get("op", "eq")
        val = f.get("value")
        na = na_of(f)  # NA-RULE-63: "keep" adds the rows with no value; a row without `na` removes them
        if col is None:
            continue
        # Issue #56: T1 is wide and T2 may be long, so a filter built on one view can name a
        # column the active view does not have. Skip it (see inapplicable_filter_rows) rather than crash.
        if actual_dtypes and col not in actual_dtypes:
            continue

        actual_dt = actual_dtypes.get(col)
        is_numeric = _is_numeric(actual_dt)
        is_list_val = isinstance(val, list)

        # Auto-promote eq/ne to in/not_in when value is a list
        if is_list_val:
            if op in ("eq", "in"):
                op = "in"
            elif op in ("ne", "not_in"):
                op = "not_in"

        if op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
            lo, hi = val
            if is_numeric:
                lo = coerce_filter_value(lo, actual_dt)
                hi = coerce_filter_value(hi, actual_dt)
            bt_closed = f.get("closed", "both")
            lf = lf.filter(keep_missing(pl.col(col).is_between(lo, hi, closed=bt_closed), col, na))
            continue

        if op in ("in", "not_in"):
            vals = val if is_list_val else [val]
            if is_numeric:
                # Coerce values to the column's native dtype — avoids the
                # Float64→Utf8 mismatch ("2022.0" != "2022") that occurs when
                # the column is cast to string instead of the values.
                coerced_vals = [coerce_filter_value(v, actual_dt) for v in vals]
                expr = pl.col(col).is_in(coerced_vals)
            else:
                str_vals = [str(v) for v in vals]
                expr = pl.col(col).cast(pl.Utf8).is_in(str_vals)
            lf = lf.filter(keep_missing(expr if op == "in" else ~expr, col, na))
        else:
            # Scalar ops: coerce value to column dtype before compare.
            # If the widget already emitted a native numeric, the coercion
            # is a no-op. We log a warning when a string sneaks in on a
            # numeric column so we can spot bypasses (UX-FILTER-1 / DEMO-3).
            if is_numeric and isinstance(val, str):
                print(
                    f"[filter] ⚠️ string operand on numeric column "
                    f"{col!r} ({actual_dt}); coercing {val!r}"
                )
            if is_numeric:
                val = coerce_filter_value(val, actual_dt)
            if op == "eq":
                lf = lf.filter(keep_missing(pl.col(col) == val, col, na))
            elif op == "ne":
                lf = lf.filter(keep_missing(pl.col(col) != val, col, na))
            elif op == "gt":
                lf = lf.filter(keep_missing(pl.col(col) > val, col, na))
            elif op == "ge":
                lf = lf.filter(keep_missing(pl.col(col) >= val, col, na))
            elif op == "lt":
                lf = lf.filter(keep_missing(pl.col(col) < val, col, na))
            elif op == "le":
                lf = lf.filter(keep_missing(pl.col(col) <= val, col, na))
    return lf
