"""A smallest valid data analysis recipe in format 1, for the tests that need a recipe file and nothing special in it.

`tiny_recipe()` returns the recipe as a dictionary (one table `A` with one text column `a`, one group, one bar plot);
a test changes what it is about and writes it with `write_tiny()`. Its data file is in the repository
(`assets/test_data/tiny/A.tsv`, three rows), so the recipe also passes the data check when the tests run from the project root. The recipe passes `check_recipe` in profile `run`
(`test_tiny_recipe_is_valid` in `test_data_analysis_recipe_validator.py` keeps it so).
"""
from pathlib import Path

import yaml


def tiny_recipe(recipe_id: str = "m", data_path: str = "./assets/test_data/tiny/A.tsv") -> dict:
    return {
        "id": recipe_id,
        "spec_version": 1,
        "data_engine": "python-polars",
        "plot_engine": "python-plotnine",
        "info": {"label": "Tiny", "description": "A smallest recipe, for a test."},
        "data_schemas": {"A": {
            "label": "A", "description": "One row per a.",
            "source": {"type": "local_tsv", "path": data_path},
            "null_values": [], "strip": False,
            "input_fields": {"a": {"type": "String", "label": "A"}},
            "wrangling": {"tier1": []},
        }},
        "analysis_groups": {"g": {"label": "G", "description": "The one group.", "plots": {"p": {
            "label": "P", "description": "Count of rows per a.",
            "spec": {"target_dataset": "A", "mapping": {"x": "a"}, "layers": [{"name": "geom_bar", "params": {}}]},
        }}}},
    }


def write_tiny(folder: Path, recipe: dict | None = None, name: str | None = None) -> Path:
    """Write the recipe (the tiny one by default) as `<id>.yaml` in the folder, keys in the order they were written."""
    recipe = recipe if recipe is not None else tiny_recipe()
    path = Path(folder) / (name or f"{recipe['id']}.yaml")
    path.write_text(yaml.safe_dump(recipe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path

