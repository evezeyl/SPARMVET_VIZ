"""Tests for TransformationRecipe YAML persistence and recode workflow (TL-IDLIB-RECIPE-1)."""
import pytest
import polars as pl
from pathlib import Path
from id_reconciliation import TransformationRecipe, apply_recode_step
from id_reconciliation.recipe import save_recipe, load_recipe


# ── gate test: test_recipe_persistence ────────────────────────────────────────

def test_recipe_roundtrip_file(tmp_path: Path):
    """save_recipe / load_recipe file roundtrip."""
    recipe = TransformationRecipe(
        ref_column="sample_id",
        target_column="ID",
        steps=[{"action": "strip_whitespace"}, {"action": "lowercase"}],
        metadata={"created_by": "test"},
    )
    out = tmp_path / "recipe.yaml"
    save_recipe(recipe, out)
    loaded = load_recipe(out)

    assert loaded.ref_column == recipe.ref_column
    assert loaded.target_column == recipe.target_column
    assert loaded.steps == recipe.steps
    assert loaded.metadata == recipe.metadata


def test_recipe_to_from_yaml_methods():
    """TransformationRecipe.to_yaml() / from_yaml() instance method roundtrip."""
    recipe = TransformationRecipe(
        ref_column="ref_id",
        target_column="target_id",
        steps=[{"action": "regex_replace", "pattern": "^sample_", "replacement": ""}],
        metadata={"version": "1"},
    )
    text = recipe.to_yaml()
    loaded = TransformationRecipe.from_yaml(text)

    assert loaded.ref_column == recipe.ref_column
    assert loaded.steps == recipe.steps
    assert loaded.metadata == recipe.metadata


# ── gate test: test_recode_workflow ───────────────────────────────────────────

def test_recode_workflow_prefix_removal():
    """Prefix removal via regex_replace produces correct IDs."""
    recipe = TransformationRecipe(
        ref_column="sample_id", target_column="ID",
        steps=[{"action": "regex_replace", "pattern": r"^sample_", "replacement": ""}],
    )
    df = pl.DataFrame({"sample_id": ["sample_001", "sample_002", "sample_003"]})
    result = apply_recode_step(df, "sample_id", recipe)
    assert result["sample_id"].to_list() == ["001", "002", "003"]


def test_recode_workflow_delimiter_extraction():
    """Delimiter swap via regex_replace produces correct IDs."""
    recipe = TransformationRecipe(
        ref_column="id", target_column="id",
        steps=[{"action": "regex_replace", "pattern": "_", "replacement": "-"}],
    )
    df = pl.DataFrame({"id": ["A_001", "B_002"]})
    result = apply_recode_step(df, "id", recipe)
    assert result["id"].to_list() == ["A-001", "B-002"]


def test_recode_action_drop_duplicates():
    recipe = TransformationRecipe(
        ref_column="id", target_column="id",
        steps=[{"action": "drop_duplicates"}],
    )
    df = pl.DataFrame({"id": ["A", "A", "B"]})
    result = apply_recode_step(df, "id", recipe)
    assert sorted(result["id"].to_list()) == ["A", "B"]


def test_recode_action_null_if():
    recipe = TransformationRecipe(
        ref_column="id", target_column="id",
        steps=[{"action": "null_if", "value": "NA"}],
    )
    df = pl.DataFrame({"id": ["001", "NA", "003"]})
    result = apply_recode_step(df, "id", recipe)
    assert result["id"].to_list() == ["001", None, "003"]


def test_recode_action_drop_nulls():
    recipe = TransformationRecipe(
        ref_column="id", target_column="id",
        steps=[{"action": "drop_nulls"}],
    )
    df = pl.DataFrame({"id": ["001", None, "003"]})
    result = apply_recode_step(df, "id", recipe)
    assert result["id"].to_list() == ["001", "003"]
