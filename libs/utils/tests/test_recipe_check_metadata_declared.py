"""S10 (D-0636): a recipe cannot have a metadata table unless it has at least one other table of data.

A recipe with a single table declares it under `data_schemas`; the metadata (`metadata_schema`, the reserved id) describes the samples of the other tables. The check cannot
recognise an ordinary data table that is really the metadata: that half is a rule for the recipe maker (`rules_data_analysis_recipe_structure.md`).
PROVISIONAL (D-0636 does not say): a recipe with the metadata and only look-up tables (`additional_datasets_schemas`) is refused too, as a look-up is not a table of results.
The wording of the refusal is PROVISIONAL; the tests read the code, the path and the fix.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_metadata_declared.py -q
"""
import copy

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

META = "metadata_schema"


def with_meta(raw):
    raw[META] = copy.deepcopy(raw["data_schemas"]["B"])
    raw[META]["completion"] = {"marker": "metadata_not_in_original_data", "meaning": "no metadata for this entity"}
    return raw


def s10(raw):
    return [p for p in check_recipe(raw, "run", catalogs=CATALOGS).problems if p.code == "S10"]


def test_the_metadata_with_a_data_table_is_accepted():
    assert s10(with_meta(copy.deepcopy(valid()))) == []


def test_one_data_table_and_no_metadata_is_accepted():
    assert s10(copy.deepcopy(valid())) == []


def test_the_metadata_alone_is_refused_with_the_fix():
    raw = with_meta(copy.deepcopy(valid()))
    raw["data_schemas"] = {}
    found = s10(raw)
    assert len(found) == 1 and found[0].path == META and "data_schemas" in found[0].fix and found[0].severity == "E"


def test_the_metadata_with_only_a_look_up_table_is_refused_provisional():
    raw = with_meta(copy.deepcopy(valid()))
    raw["additional_datasets_schemas"] = {"L": raw["data_schemas"].pop("A")}
    raw["data_schemas"] = {}
    assert len(s10(raw)) == 1
