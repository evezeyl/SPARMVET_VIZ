"""Tests for IdTransformation YAML persistence and recode workflow (TL-IDLIB-ID-TRANSFORMATION-1)."""
import pytest
import polars as pl
from pathlib import Path
from id_reconciliation import IdTransformation, apply_recode_step
from id_reconciliation.id_transformation import save_transformation, load_transformation


# ── gate test: test_transformation_persistence ────────────────────────────────────────

def test_transformation_roundtrip_file(tmp_path: Path):
    """save_transformation / load_transformation file roundtrip."""
    id_transformation = IdTransformation(
        ref_column="sample_id",
        target_column="ID",
        steps=[{"action": "strip_whitespace"}, {"action": "lowercase"}],
        metadata={"created_by": "test"},
    )
    out = tmp_path / "steps.yaml"
    save_transformation(id_transformation, out)
    loaded = load_transformation(out)

    assert loaded.ref_column == id_transformation.ref_column
    assert loaded.target_column == id_transformation.target_column
    assert loaded.steps == id_transformation.steps
    assert loaded.metadata == id_transformation.metadata


def test_transformation_to_from_yaml_methods():
    """IdTransformation.to_yaml() / from_yaml() instance method roundtrip."""
    id_transformation = IdTransformation(
        ref_column="ref_id",
        target_column="target_id",
        steps=[{"action": "regex_replace", "pattern": "^sample_", "replacement": ""}],
        metadata={"version": "1"},
    )
    text = id_transformation.to_yaml()
    loaded = IdTransformation.from_yaml(text)

    assert loaded.ref_column == id_transformation.ref_column
    assert loaded.steps == id_transformation.steps
    assert loaded.metadata == id_transformation.metadata


# ── gate test: test_recode_workflow ───────────────────────────────────────────

def test_recode_workflow_prefix_removal():
    """Prefix removal via regex_replace produces correct IDs."""
    id_transformation = IdTransformation(
        ref_column="sample_id", target_column="ID",
        steps=[{"action": "regex_replace", "pattern": r"^sample_", "replacement": ""}],
    )
    df = pl.DataFrame({"sample_id": ["sample_001", "sample_002", "sample_003"]})
    result = apply_recode_step(df, "sample_id", id_transformation)
    assert result["sample_id"].to_list() == ["001", "002", "003"]


def test_recode_workflow_delimiter_extraction():
    """Delimiter swap via regex_replace produces correct IDs."""
    id_transformation = IdTransformation(
        ref_column="id", target_column="id",
        steps=[{"action": "regex_replace", "pattern": "_", "replacement": "-"}],
    )
    df = pl.DataFrame({"id": ["A_001", "B_002"]})
    result = apply_recode_step(df, "id", id_transformation)
    assert result["id"].to_list() == ["A-001", "B-002"]


def test_recode_action_drop_duplicates():
    id_transformation = IdTransformation(
        ref_column="id", target_column="id",
        steps=[{"action": "drop_duplicates"}],
    )
    df = pl.DataFrame({"id": ["A", "A", "B"]})
    result = apply_recode_step(df, "id", id_transformation)
    assert sorted(result["id"].to_list()) == ["A", "B"]


def test_recode_action_null_if():
    id_transformation = IdTransformation(
        ref_column="id", target_column="id",
        steps=[{"action": "null_if", "value": "NA"}],
    )
    df = pl.DataFrame({"id": ["001", "NA", "003"]})
    result = apply_recode_step(df, "id", id_transformation)
    assert result["id"].to_list() == ["001", None, "003"]


def test_recode_action_drop_nulls():
    id_transformation = IdTransformation(
        ref_column="id", target_column="id",
        steps=[{"action": "drop_nulls"}],
    )
    df = pl.DataFrame({"id": ["001", None, "003"]})
    result = apply_recode_step(df, "id", id_transformation)
    assert result["id"].to_list() == ["001", "003"]
