"""Every recipe the repository holds follows the metadata join rule (J16; D-0586, D-0633): the data table first, the metadata joined left in tier 1.

Scans every `.yaml` file of `config/`, `assets/` (shipped recipes, Gallery bundles, templates) and of the staged recipes of the equality check, and checks the ones that
declare joins and a `metadata_schema` with the recipe check. A scan finds nothing when a rule is broken only if it cannot find a recipe, so the first test pins that
recipes with a metadata join are found, and the last turns one back to the old form and sees J16.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_metadata_join_rule.py -q

# @deps
# consumes: libs/utils/src/utils/recipe_check.py, config/data_analysis_recipes, assets/gallery_data, app/tests/equality/recipes
# doc: .claude/rules/rules_data_analysis_recipe_structure.md
# @end_deps
"""
from pathlib import Path

import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.data_analysis_recipe_validator import checker_catalogs
from utils.recipe_loader import check_recipe_file

ROOT = Path(__file__).resolve().parents[2]
CATALOGS = checker_catalogs()
FOLDERS = [ROOT / "config", ROOT / "assets", ROOT / "app/tests/equality/recipes"]


def _with_metadata_joins():
    found = []
    for folder in FOLDERS:
        for path in sorted(folder.rglob("*.yaml")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "joins:" in text and "metadata_schema" in text and "analysis_groups:" in text:
                found.append(path)
    return found


RECIPES = _with_metadata_joins()


def _j15(path, base=None):
    result = check_recipe_file(path, "run", catalogs=CATALOGS)
    return [p.text(path.name) for p in result.problems if p.code == "J16"]


def test_recipes_with_a_metadata_join_are_found():
    names = {p.name for p in RECIPES}
    assert {"2_test_data_ST22_dummy.yaml", "demo_abromics.yaml"} <= names
    assert any("equality" in p.parts for p in RECIPES)


@pytest.mark.parametrize("path", RECIPES, ids=[str(p.relative_to(ROOT)) for p in RECIPES])
def test_the_recipe_joins_the_metadata_left_from_a_data_table(path):
    assert _j15(path) == []


def test_the_scan_can_fail_when_a_shipped_recipe_goes_back_to_an_inner_join(tmp_path):
    import shutil
    source = ROOT / "config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml"
    work = tmp_path / "pipelines"
    work.mkdir()
    shutil.copy(source, work / source.name)
    shutil.copytree(source.with_suffix(""), work / source.stem)
    step = work / source.stem / "assembly/Plasmid_Profile_Joint.yaml"
    text = step.read_text()
    assert "how: left" in text
    step.write_text(text.replace("how: left", "how: inner"))
    found = _j15(work / source.name)
    assert len(found) == 1 and "Plasmid_Profile_Joint" in found[0]
