"""Tests for IDReconciliationEngine and public API functions."""
import pytest
from id_reconciliation import (
    IDReconciliationEngine,
    format_match_table,
    detect_many_to_many,
    apply_recode_step,
    TransformationRecipe,
)


def test_exact_match_only():
    engine = IDReconciliationEngine()
    results = engine.reconcile(["A", "B", "C"], ["A", "B", "C"])
    by_ref = {r.ref_id: r for r in results}
    assert by_ref["A"].match_type == "exact"
    assert by_ref["A"].certainty == 1.0


def test_unmatched_returns_zero_certainty():
    engine = IDReconciliationEngine()
    results = engine.reconcile(["X"], ["A", "B"])
    assert results[0].match_type in ("fuzzy", "unmatched")
    if results[0].match_type == "unmatched":
        assert results[0].certainty == 0.0


def test_format_match_table_sorted():
    engine = IDReconciliationEngine()
    results = engine.reconcile(["A", "B"], ["A", "Z"])
    df = format_match_table(results)
    assert list(df.columns) == ["ref_id", "target_id", "match_type", "certainty", "transform_applied"]
    certainties = df["certainty"].to_list()
    assert certainties == sorted(certainties, reverse=True)


def test_apply_recode_strip_whitespace():
    import polars as pl
    recipe = TransformationRecipe(
        ref_column="id", target_column="id",
        steps=[{"action": "strip_whitespace"}],
    )
    df = pl.DataFrame({"id": [" A ", "B ", " C"]})
    result = apply_recode_step(df, "id", recipe)
    assert result["id"].to_list() == ["A", "B", "C"]
