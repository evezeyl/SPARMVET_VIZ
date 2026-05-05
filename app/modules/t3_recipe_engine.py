"""app/modules/t3_recipe_engine.py
Pure helpers extracted from home_theater.py (Phase 24-A, ADR-051).

Two-Category Law (ADR-045): this module is a non-Shiny module
(no @render.* / @reactive.* decorators) and may be imported from any
context — handlers, modules, scripts, tests.

Initial scope (24-A): _apply_filter_rows. Future steps will add
extract_t3_filter_rows / extract_t3_drop_columns.
"""

from __future__ import annotations

# @deps
# provides: function:_apply_filter_rows
# consumes: polars
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

import polars as pl


def _op_label(op: str) -> str:
    """Symbolic label for a filter operator (used in UI rendering and reports).

    Lives here (not in a UI module) so that both filter_and_audit_handlers and
    export_handlers can share one definition. ADR-045 compliant — pure, no Shiny.
    """
    return {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
            "lt": "<", "le": "≤", "in": "∈", "not_in": "∉"}.get(op, op)


def _apply_filter_rows(lf, filter_rows: list) -> "pl.LazyFrame":
    """
    Apply a list of {column, op, value, dtype} dicts to a LazyFrame.

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

    def _coerce_to_dtype(value, dt):
        """Best-effort string→native coercion based on actual column dtype."""
        try:
            s = str(dt) if dt is not None else ""
            if "Float" in s or "Decimal" in s:
                return float(value)
            if "Int" in s or "UInt" in s:
                return int(float(value))  # tolerate "90.0" → 90
            if "Boolean" in s:
                if isinstance(value, bool):
                    return value
                return str(value).strip().lower() in ("true", "1", "yes")
        except (ValueError, TypeError):
            pass
        return value

    for f in filter_rows:
        col = f.get("column")
        op = f.get("op", "eq")
        val = f.get("value")
        if col is None:
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
                lo = _coerce_to_dtype(lo, actual_dt)
                hi = _coerce_to_dtype(hi, actual_dt)
            bt_closed = f.get("closed", "both")
            lf = lf.filter(pl.col(col).is_between(lo, hi, closed=bt_closed))
            continue

        if op in ("in", "not_in"):
            vals = val if is_list_val else [val]
            if is_numeric:
                # Coerce values to the column's native dtype — avoids the
                # Float64→Utf8 mismatch ("2022.0" != "2022") that occurs when
                # the column is cast to string instead of the values.
                coerced_vals = [_coerce_to_dtype(v, actual_dt) for v in vals]
                expr = pl.col(col).is_in(coerced_vals)
            else:
                str_vals = [str(v) for v in vals]
                expr = pl.col(col).cast(pl.Utf8).is_in(str_vals)
            lf = lf.filter(expr if op == "in" else ~expr)
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
                val = _coerce_to_dtype(val, actual_dt)
            if op == "eq":
                lf = lf.filter(pl.col(col) == val)
            elif op == "ne":
                lf = lf.filter(pl.col(col) != val)
            elif op == "gt":
                lf = lf.filter(pl.col(col) > val)
            elif op == "ge":
                lf = lf.filter(pl.col(col) >= val)
            elif op == "lt":
                lf = lf.filter(pl.col(col) < val)
            elif op == "le":
                lf = lf.filter(pl.col(col) <= val)
    return lf
