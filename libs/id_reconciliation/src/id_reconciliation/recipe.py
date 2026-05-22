from __future__ import annotations

import yaml
from pathlib import Path
from .data_structures import TransformationRecipe

# @deps
# provides: save_recipe, load_recipe
# consumes: libs/id_reconciliation/src/id_reconciliation/data_structures.py
# consumed_by: libs/id_reconciliation/src/id_reconciliation/core.py
# @end_deps


def save_recipe(recipe: TransformationRecipe, path: Path) -> None:
    """Persist a TransformationRecipe to YAML."""
    data = {
        "ref_column": recipe.ref_column,
        "target_column": recipe.target_column,
        "steps": recipe.steps,
        "metadata": recipe.metadata,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, allow_unicode=True)


def load_recipe(path: Path) -> TransformationRecipe:
    """Load a TransformationRecipe from YAML."""
    with Path(path).open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return TransformationRecipe(
        ref_column=data["ref_column"],
        target_column=data["target_column"],
        steps=data.get("steps", []),
        metadata=data.get("metadata", {}),
    )
