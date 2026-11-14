"""Every data analysis recipe that ships passes the strict checker `check_recipe` (profile run), with the registries.

After migration run D (labels, descriptions, taxonomy on the plot entry, no wrapper line in a fragment) no shipped
recipe, retest recipe or template has an error. This test keeps it so: a recipe that falls back to an old form, or a
new recipe that is not in format 1, fails here before it reaches the app.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_shipped_recipes_pass_the_checker.py -q
"""
from pathlib import Path

import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.actions.base import ACTION_SCHEMAS
from utils.recipe_loader import check_recipe_file
from viz_factory.arguments import argument_catalog

ROOT = Path(__file__).resolve().parents[2]
RECIPES = sorted(p for folder in ("pipelines", "retest", "templates")
                 for p in (ROOT / "config/data_analysis_recipes" / folder).glob("*.yaml"))
CATALOGS = {"actions": dict(ACTION_SCHEMAS), "components": argument_catalog()}


def test_there_are_recipes_to_check():
    assert len(RECIPES) >= 14


@pytest.mark.parametrize("path", RECIPES, ids=[f"{p.parent.name}/{p.stem}" for p in RECIPES])
def test_the_recipe_has_no_error(path):
    result = check_recipe_file(path, "run", catalogs=CATALOGS)
    assert {"structure", "actions", "components"} <= result.coverage  # the checks of actions and plot components ran
    assert [p.text(path.name) for p in result.errors] == []


def test_the_checker_can_fail_on_a_shipped_recipe(tmp_path):
    """The guard is real: the same recipe without one label is refused."""
    import shutil
    source = ROOT / "config/data_analysis_recipes/pipelines/3_test_no_joins.yaml"
    work = tmp_path / "pipelines"
    shutil.copytree(source.parent, work)
    target = work / source.name
    text = target.read_text()
    assert "\n    label:" in text
    lines = text.split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith("    label:"))
    target.write_text("\n".join(lines[:first] + lines[first + 1:]))
    result = check_recipe_file(target, "run", catalogs=CATALOGS, base=ROOT)
    assert any("label" in p.message for p in result.errors)
