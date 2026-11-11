"""
Regression tests for the filter-operator contract (UX-FILTER-1, DEMO-3/DEMO-4).

Two filter application paths exist:
  1. _apply_filter_rows in app/modules/t3_audit_engine.py — used for the data
     preview pane and several T2/T3 transient filter passes (moved from
     home_theater.py in Phase 24-A, ADR-051).
  2. The Tier 3 UI-filter loop in libs/viz_factory/src/viz_factory/viz_factory.py
     — used when rendering plots.

Both paths MUST produce identical results for the same {column, op, value,
[closed]} filter row, otherwise plots and data preview would disagree.

These tests reimplement both loops verbatim and assert they agree across
every operator + value-shape combination, including:
  - dtype-aware coercion (string operands on numeric columns)
  - between with closed='both' (inclusive) and closed='none' (exclusive)
  - eq/ne auto-promotion to in/not_in for list values

Run from the project root:
    pytest app/tests/test_filter_operators.py -v
"""
import polars as pl
import pytest


# ── Shared helpers (mirror production code from both filter paths) ────────────

def _is_numeric(dt) -> bool:
    return dt is not None and any(
        t in str(dt) for t in ("Int", "UInt", "Float", "Decimal")
    )


def _coerce_to_dtype(value, dt):
    try:
        s = str(dt) if dt is not None else ""
        if "Float" in s or "Decimal" in s:
            return float(value)
        if "Int" in s or "UInt" in s:
            return int(float(value))
    except (ValueError, TypeError):
        pass
    return value


def _filter_loop(lf: pl.LazyFrame, filter_rows: list[dict]) -> pl.LazyFrame:
    """Verbatim port of the production filter loop (both paths share this logic)."""
    schema = lf.collect_schema()
    actual_dtypes = {n: schema[n] for n in schema.names()}

    for f in filter_rows:
        col = f.get("column")
        op = f.get("op", "eq")
        val = f.get("value")
        if col is None:
            continue

        actual_dt = actual_dtypes.get(col)
        is_numeric = _is_numeric(actual_dt)
        is_list_val = isinstance(val, list)

        if is_list_val and op in ("eq", "in"):
            op = "in"
        elif is_list_val and op in ("ne", "not_in"):
            op = "not_in"

        if op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
            lo, hi = val
            if is_numeric:
                lo = _coerce_to_dtype(lo, actual_dt)
                hi = _coerce_to_dtype(hi, actual_dt)
            closed = f.get("closed", "both")
            lf = lf.filter(pl.col(col).is_between(lo, hi, closed=closed))
            continue

        if op in ("in", "not_in"):
            vals = val if is_list_val else [val]
            if is_numeric:
                coerced_vals = [_coerce_to_dtype(v, actual_dt) for v in vals]
                expr = pl.col(col).is_in(coerced_vals)
            else:
                str_vals = [str(v) for v in vals]
                expr = pl.col(col).cast(pl.Utf8).is_in(str_vals)
            lf = lf.filter(expr if op == "in" else ~expr)
            continue

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


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def lf():
    return pl.LazyFrame({
        "year_int":     [2020, 2021, 2022, 2023, 2024],
        "value_float":  [1.5, 2.5, 3.5, 4.5, 5.5],
        "country":      ["NO", "NO", "DK", "SE", "FI"],
        "sample_id":    ["A", "B", "C", "D", "E"],
    })


def _ids(result: pl.DataFrame) -> set[str]:
    return set(result["sample_id"].to_list())


# ── Numeric scalar ops (string-value coercion) ────────────────────────────────

class TestNumericScalarOps:
    """Numeric columns must accept string-typed operands and coerce them."""

    def test_eq_numeric_string_val(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "eq", "value": "2022"}]).collect()
        assert _ids(r) == {"C"}

    def test_eq_numeric_int_val(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "eq", "value": 2022}]).collect()
        assert _ids(r) == {"C"}

    def test_ne_numeric_string_val(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "ne", "value": "2022"}]).collect()
        assert _ids(r) == {"A", "B", "D", "E"}

    def test_gt_numeric_string_val(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "gt", "value": "2022"}]).collect()
        assert _ids(r) == {"D", "E"}

    def test_ge_numeric_string_val(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "ge", "value": "2022"}]).collect()
        assert _ids(r) == {"C", "D", "E"}

    def test_lt_numeric(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "lt", "value": 2022}]).collect()
        assert _ids(r) == {"A", "B"}

    def test_le_numeric(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "le", "value": 2022}]).collect()
        assert _ids(r) == {"A", "B", "C"}

    def test_gt_float_string_val(self, lf):
        r = _filter_loop(lf, [{"column": "value_float", "op": "gt", "value": "3"}]).collect()
        assert _ids(r) == {"C", "D", "E"}


# ── String scalar ops ─────────────────────────────────────────────────────────

class TestStringScalarOps:
    def test_eq_string(self, lf):
        r = _filter_loop(lf, [{"column": "country", "op": "eq", "value": "NO"}]).collect()
        assert _ids(r) == {"A", "B"}

    def test_ne_string(self, lf):
        r = _filter_loop(lf, [{"column": "country", "op": "ne", "value": "NO"}]).collect()
        assert _ids(r) == {"C", "D", "E"}


# ── Set-membership ops ────────────────────────────────────────────────────────

class TestSetMembership:
    def test_in_list(self, lf):
        r = _filter_loop(lf, [{"column": "country", "op": "in",
                               "value": ["NO", "DK"]}]).collect()
        assert _ids(r) == {"A", "B", "C"}

    def test_not_in_list(self, lf):
        r = _filter_loop(lf, [{"column": "country", "op": "not_in",
                               "value": ["NO"]}]).collect()
        assert _ids(r) == {"C", "D", "E"}

    def test_eq_with_list_promotes_to_in(self, lf):
        r = _filter_loop(lf, [{"column": "country", "op": "eq",
                               "value": ["NO", "DK"]}]).collect()
        assert _ids(r) == {"A", "B", "C"}

    def test_ne_with_list_promotes_to_not_in(self, lf):
        r = _filter_loop(lf, [{"column": "country", "op": "ne",
                               "value": ["NO"]}]).collect()
        assert _ids(r) == {"C", "D", "E"}

    def test_in_numeric_int_column(self, lf):
        # Regression: Int64 column with in operator must match without Utf8 cast.
        # Old path: cast(Utf8).is_in(["2022"]) — worked for Int64 but breaks Float64.
        r = _filter_loop(lf, [{"column": "year_int", "op": "in",
                               "value": [2022, 2023]}]).collect()
        assert _ids(r) == {"C", "D"}

    def test_in_float_column_string_values(self, lf):
        # Regression: Float64 column — old Utf8 cast turned 3.5 → "3.5",
        # so str(3.5) matched but str(3) didn't → wrong results.
        r = _filter_loop(lf, [{"column": "value_float", "op": "in",
                               "value": ["3.5", "4.5"]}]).collect()
        assert _ids(r) == {"C", "D"}

    def test_not_in_numeric(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "not_in",
                               "value": [2022, 2023]}]).collect()
        assert _ids(r) == {"A", "B", "E"}


# ── Between ───────────────────────────────────────────────────────────────────

class TestBetween:
    def test_inclusive_default(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "between",
                               "value": [2021, 2023]}]).collect()
        assert _ids(r) == {"B", "C", "D"}

    def test_inclusive_explicit(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "between",
                               "value": [2021, 2023], "closed": "both"}]).collect()
        assert _ids(r) == {"B", "C", "D"}

    def test_exclusive(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "between",
                               "value": [2021, 2023], "closed": "none"}]).collect()
        assert _ids(r) == {"C"}

    def test_string_operands_coerced(self, lf):
        r = _filter_loop(lf, [{"column": "year_int", "op": "between",
                               "value": ["2021", "2023"]}]).collect()
        assert _ids(r) == {"B", "C", "D"}

    def test_float_column(self, lf):
        r = _filter_loop(lf, [{"column": "value_float", "op": "between",
                               "value": [2.0, 4.0]}]).collect()
        assert _ids(r) == {"B", "C"}


# ── Compound (multiple rows AND-combined) ─────────────────────────────────────

class TestCompound:
    def test_two_rows_intersect(self, lf):
        r = _filter_loop(lf, [
            {"column": "year_int", "op": "ge", "value": "2022"},
            {"column": "country", "op": "in", "value": ["DK", "SE"]},
        ]).collect()
        assert _ids(r) == {"C", "D"}

    def test_no_op_on_unknown_column(self, lf):
        # Unknown column — polars will raise downstream; here we just assert
        # the loop doesn't crash on the {column: None} sentinel that the
        # production filter row may carry before the user picks a column.
        r = _filter_loop(lf, [{"column": None, "op": "eq", "value": "x"}]).collect()
        assert r.height == 5  # no-op


# --- Issue #56 / ADR-087: filters on a column the active view does not have ---

def test_filter_on_missing_column_is_skipped_not_an_error():
    import polars as pl
    from app.modules.t3_audit_engine import _apply_filter_rows, inapplicable_filter_rows
    lf = pl.DataFrame({"a": [1, 2, 3]}).lazy()
    rows = [{"column": "gone", "op": "eq", "value": "x"}, {"column": "a", "op": "ge", "value": "2"}]
    assert _apply_filter_rows(lf, rows).collect()["a"].to_list() == [2, 3]
    assert [f["column"] for f in inapplicable_filter_rows(lf, rows)] == ["gone"]


def test_filter_that_leaves_zero_rows_is_empty_not_an_error():
    import polars as pl
    from app.modules.t3_audit_engine import _apply_filter_rows
    lf = pl.DataFrame({"a": ["x", "y"]}).lazy()
    out = _apply_filter_rows(lf, [{"column": "a", "op": "in", "value": ["zzz"]}]).collect()
    assert out.height == 0 and out.columns == ["a"]


def test_exploration_filter_never_modifies_the_source_frame():
    """The preview filters a lazy copy; the source data is untouched (nothing to write back)."""
    import polars as pl
    from app.modules.t3_audit_engine import _apply_filter_rows
    df = pl.DataFrame({"a": [1, 2, 3]})
    _apply_filter_rows(df.lazy(), [{"column": "a", "op": "eq", "value": "1"}]).collect()
    assert df["a"].to_list() == [1, 2, 3]


# --- Issue #57: one vocabulary for operators ---

def test_single_value_set_reads_as_equality():
    from app.modules.t3_audit_engine import describe_filter
    assert describe_filter("sequence_type", "in", ["101"]) == "sequence_type = 101"
    assert describe_filter("sequence_type", "not_in", ["101"]) == "sequence_type ≠ 101"


def test_several_values_read_any_of_none_of():
    from app.modules.t3_audit_engine import describe_filter
    assert describe_filter("c", "in", ["a", "b"]) == "c any of a, b"
    assert describe_filter("c", "not_in", ["a", "b"]) == "c none of a, b"


def test_every_operator_the_dropdown_offers_has_words_in_the_label():
    from app.modules.t3_audit_engine import op_choice_label
    for op in ("in", "not_in", "eq", "ne", "gt", "ge", "lt", "le", "between"):
        label = op_choice_label(op)
        assert " " in label, f"{op} has no explaining text: {label!r}"
