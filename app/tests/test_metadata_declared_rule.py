"""Every recipe the repository holds that declares a metadata table also has a table of data (S10; D-0636).

Scans every `.yaml` file of `config/`, `assets/`, `libs/` and `app/tests/` that has a top-level `metadata_schema:` and runs the recipe check; S10 must not be found. The first
test pins that the scan finds recipes (a scan that finds none proves nothing); the last turns the figshare recipe back to its old form (its metadata as an ordinary data table
is the case the check cannot see; the opposite, a metadata declared alone, is what the check finds) and sees S10.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_metadata_declared_rule.py -q

# @deps
# consumes: libs/utils/src/utils/recipe_check.py, config/data_analysis_recipes, app/tests/equality/recipes
# doc: .claude/design/recipe_format_spec.md (S10), .claude/rules/rules_data_analysis_recipe_structure.md
# @end_deps
"""
import re
from pathlib import Path

import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.data_analysis_recipe_validator import checker_catalogs
from utils.recipe_check import check_recipe
from utils.recipe_loader import check_recipe_file

ROOT = Path(__file__).resolve().parents[2]
CATALOGS = checker_catalogs()
FOLDERS = [ROOT / "config", ROOT / "assets", ROOT / "libs", ROOT / "app/tests"]
TOP_LEVEL = re.compile(r"^metadata_schema:", re.MULTILINE)


def _with_metadata():
    found = []
    for folder in FOLDERS:
        for path in sorted(folder.rglob("*.yaml")):
            if "build" in path.parts:
                continue
            if TOP_LEVEL.search(path.read_text(encoding="utf-8", errors="replace")):
                found.append(path)
    return found


RECIPES = _with_metadata()


def test_recipes_with_a_metadata_table_are_found():
    names = {p.name for p in RECIPES}
    assert {"2_test_data_ST22_dummy.yaml", "demo_abromics.yaml", "figshare_integration.yaml"} <= names and len(RECIPES) >= 10


@pytest.mark.parametrize("path", RECIPES, ids=lambda p: str(p.relative_to(ROOT)))
def test_a_recipe_with_a_metadata_table_has_a_table_of_data(path):
    result = check_recipe_file(path, "run", catalogs=CATALOGS)
    assert [p.text(path.name) for p in result.problems if p.code == "S10"] == []


def test_figshare_declares_its_metadata_as_the_metadata_and_joins_it_left_from_the_data():
    raw = load_data_analysis_recipe(ROOT / "config/data_analysis_recipes/pipelines/figshare_integration.yaml").raw
    assert "fg_metadata" not in raw["data_schemas"] and "metadata_schema" in raw and set(raw["data_schemas"]) == {"fg_phenotypes", "fg_genotypes"}
    steps = raw["joins"]["figshare_triple_join"]["tier1"]["steps"]
    assert [i["dataset_id"] for i in raw["joins"]["figshare_triple_join"]["ingredients"]][0] != "metadata_schema"
    assert [(s["right_ingredient"], s["how"]) for s in steps] == [("fg_genotypes", "left"), ("metadata_schema", "left")]


def test_the_metadata_declared_alone_is_found_in_a_real_recipe():
    raw = load_data_analysis_recipe(ROOT / "config/data_analysis_recipes/pipelines/figshare_integration.yaml").raw
    raw = {k: v for k, v in raw.items() if k not in ("joins", "analysis_groups")}
    raw["data_schemas"] = {}
    raw["joins"], raw["analysis_groups"] = {}, {}
    assert "S10" in [p.code for p in check_recipe(raw, "run", catalogs=CATALOGS).problems]
