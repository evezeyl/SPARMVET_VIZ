"""Tests for IDReconciliationEngine and public API functions (TL-IDLIB-CORE-1)."""
import pytest
import polars as pl
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
    recipe = TransformationRecipe(
        ref_column="id", target_column="id",
        steps=[{"action": "strip_whitespace"}],
    )
    df = pl.DataFrame({"id": [" A ", "B ", " C"]})
    result = apply_recode_step(df, "id", recipe)
    assert result["id"].to_list() == ["A", "B", "C"]


# ── gate tests: TL-IDLIB-CORE-1 ──────────────────────────────────────────────

def test_format_match_table_columns():
    """format_match_table returns DataFrame with exactly the expected 5 columns."""
    engine = IDReconciliationEngine()
    results = engine.reconcile(["A"], ["A"])
    df = format_match_table(results)
    assert df.columns == ["ref_id", "target_id", "match_type", "certainty", "transform_applied"]


def test_many_to_many_detection():
    """detect_many_to_many identifies refs with multiple target matches."""
    from id_reconciliation.data_structures import MatchResult
    results = [
        MatchResult(ref_id="A", target_id="A1", match_type="fuzzy", certainty=0.85),
        MatchResult(ref_id="A", target_id="A2", match_type="fuzzy", certainty=0.80),
        MatchResult(ref_id="B", target_id="B1", match_type="exact", certainty=1.0),
    ]
    m2m = detect_many_to_many(results)
    assert "A" in m2m
    assert set(m2m["A"]) == {"A1", "A2"}
    assert "B" not in m2m


def test_match_pair_from_lazyframe():
    """match_pair reads IDs from LazyFrames and returns reconciliation results."""
    ref_df = pl.DataFrame({"sample_id": ["001", "002", "003"]})
    target_df = pl.DataFrame({"ID": ["001", "002", "003"]})
    engine = IDReconciliationEngine()
    results = engine.match_pair(
        ref_df.lazy(), target_df.lazy(), "sample_id", "ID"
    )
    assert len(results) == 3
    assert all(r.match_type == "exact" for r in results)


def test_precheck_compatibility_flags_cleaning():
    """precheck_compatibility sets needs_cleaning=True when unmatched > threshold."""
    engine = IDReconciliationEngine(fuzzy_cutoff=99.0)
    refs = [f"sample_{i:03d}" for i in range(100)]
    targets = ["unrelated_X", "unrelated_Y"]
    result = engine.precheck_compatibility(refs, targets, recode_threshold=50)
    assert result["total_ref"] == 100
    assert result["needs_cleaning"] is True
    assert "overlap_pct" in result
    assert "top_suggestions" in result


def test_precheck_compatibility_no_cleaning_needed():
    """precheck_compatibility sets needs_cleaning=False when overlap is high."""
    engine = IDReconciliationEngine()
    ids = [f"{i:03d}" for i in range(30)]
    result = engine.precheck_compatibility(ids, ids, recode_threshold=50)
    assert result["overlap_count"] == 30
    assert result["needs_cleaning"] is False


def test_generate_recipe_infers_prefix_step():
    """generate_recipe produces a regex_replace step for a prefix-removal pattern."""
    refs = [f"sample_{i:03d}" for i in range(1, 6)]
    targets = [f"{i:03d}" for i in range(1, 6)]
    engine = IDReconciliationEngine()
    results = engine.reconcile(refs, targets)
    recipe = engine.generate_recipe(results, "sample_id", "ID")
    assert recipe.ref_column == "sample_id"
    assert recipe.target_column == "ID"
    assert any(s.get("action") == "regex_replace" for s in recipe.steps)


def test_format_match_table_progressive_chunks():
    """format_match_table output can be sliced by chunk_size."""
    refs = [f"id_{i}" for i in range(20)]
    targets = [f"id_{i}" for i in range(20)]
    engine = IDReconciliationEngine(chunk_size=5)
    results = engine.reconcile(refs, targets)
    df = format_match_table(results)
    chunk = df.slice(0, engine.chunk_size)
    assert len(chunk) == 5
    assert chunk["certainty"].to_list() == sorted(chunk["certainty"].to_list(), reverse=True)
