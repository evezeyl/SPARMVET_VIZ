"""Every data analysis recipe that ships passes the strict checker `check_recipe` (profile run), with the registries.

After migration run D (labels, descriptions, taxonomy on the plot entry, no wrapper line in a fragment) no shipped
recipe, retest recipe or template has an error. This test keeps it so: a recipe that falls back to an old form, or a
new recipe that is not in format 1, fails here before it reaches the app.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_shipped_recipes_pass_the_checker.py -q
"""
from pathlib import Path

import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.data_analysis_recipe_validator import checker_catalogs
from utils.recipe_loader import check_recipe_file

ROOT = Path(__file__).resolve().parents[2]
RECIPES = sorted(p for folder in ("pipelines", "retest", "templates")
                 for p in (ROOT / "config/data_analysis_recipes" / folder).glob("*.yaml"))
CATALOGS = checker_catalogs()


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


# -- no shipped pipeline step is without a description (advice S04 schema, J03 join, G02 group, P02 plot)

PIPELINES = sorted((ROOT / "config/data_analysis_recipes/pipelines").glob("*.yaml"))
DESCRIPTION_ADVICE = {"S04", "J03", "G02", "P02"}


def _missing_descriptions(path, base=None):
    result = check_recipe_file(path, "run", catalogs=CATALOGS, **({"base": base} if base else {}))
    return [p.text(path.name) for p in result.problems if p.code in DESCRIPTION_ADVICE]


def test_there_are_pipelines_to_check():
    assert len(PIPELINES) == 7


@pytest.mark.parametrize("path", PIPELINES, ids=[p.stem for p in PIPELINES])
def test_no_shipped_pipeline_step_lacks_a_description(path):
    assert _missing_descriptions(path) == []


def test_the_description_check_can_fail(tmp_path):
    """The same recipe without one description (the plot of 3_test_no_joins) is reported."""
    import shutil
    source = ROOT / "config/data_analysis_recipes/pipelines/3_test_no_joins.yaml"
    work = tmp_path / "pipelines"
    shutil.copytree(source.parent, work)
    target = work / source.name
    lines = target.read_text().split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith("        description:"))
    target.write_text("\n".join(lines[:first] + lines[first + 1:]))
    assert _missing_descriptions(target, base=ROOT) != []
