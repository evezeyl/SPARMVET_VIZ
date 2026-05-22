"""Tests for TransformationRecipe YAML persistence (roundtrip)."""
import pytest
from pathlib import Path
from id_reconciliation import TransformationRecipe
from id_reconciliation.recipe import save_recipe, load_recipe


def test_recipe_roundtrip(tmp_path: Path):
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
