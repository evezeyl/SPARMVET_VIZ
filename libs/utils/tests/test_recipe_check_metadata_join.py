"""J16 (D-0586, D-0633): a join that brings in the metadata has the data table first and a left join in tier 1.

Refused: the metadata as the first ingredient with a data table joined onto it; a join step with the metadata that is inner, full, right, semi, anti, cross,
has no `how`, or is the as-of or the on-conditions join. Not affected: the left join from the data table, a join of look-up tables, a join with no data table
(the metadata alone, or the metadata with a look-up). A metadata join in tier 2 is refused by ST05, not by J16 (the join is tier 1 only).
The wording of the refusal is PROVISIONAL (D-0633: not decided); the tests read the code and the words that name the table and the fix, not the whole sentence.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_metadata_join.py -q
"""
import copy

import pytest

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

META = "metadata_schema"
LEFT = {"action": "polars_join", "right_ingredient": META, "on": "id", "how": "left"}


def base():
    raw = copy.deepcopy(valid())
    raw[META] = copy.deepcopy(raw["data_schemas"]["B"])
    raw[META]["completion"] = {"marker": "metadata_not_in_original_data", "meaning": "no metadata for this entity"}
    raw["joins"]["AM"] = {"ui_label": "AM", "description": "One row per sample, A with its metadata.",
                          "ingredients": [{"dataset_id": "A"}, {"dataset_id": META}], "tier1": {"steps": [dict(LEFT)]}}
    return raw


def problems(raw):
    return [p for p in check_recipe(raw, "run", catalogs=CATALOGS).problems if p.code == "J16"]


def test_the_data_table_first_and_a_left_join_with_the_metadata_is_accepted():
    assert problems(base()) == []


@pytest.mark.parametrize("how", ["inner", "full", "right", "semi", "anti", "cross"])
def test_a_join_of_the_metadata_with_another_how_is_refused(how):
    raw = base()
    raw["joins"]["AM"]["tier1"]["steps"][0]["how"] = how
    found = problems(raw)
    assert len(found) == 1 and how in found[0].message and "how: left" in found[0].fix
    assert "joins.AM.tier1.steps[1]" in found[0].path


def test_a_metadata_join_with_no_how_is_refused_because_polars_then_joins_inner():
    raw = base()
    del raw["joins"]["AM"]["tier1"]["steps"][0]["how"]
    assert len(problems(raw)) == 1


def test_the_as_of_join_with_the_metadata_is_refused():
    raw = base()
    raw["joins"]["AM"]["tier1"]["steps"][0] = {"action": "polars_join_asof", "right_ingredient": META, "on": "id", "strategy": "backward"}
    assert len(problems(raw)) == 1


def test_a_join_that_starts_from_the_metadata_is_refused_even_with_a_left_join():
    raw = base()
    raw["joins"]["AM"]["ingredients"] = [{"dataset_id": META}, {"dataset_id": "A"}]
    raw["joins"]["AM"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "A", "on": "id", "how": "left"}]
    found = problems(raw)
    assert len(found) == 1 and found[0].path == "joins.AM.ingredients" and "data table" in found[0].fix


def test_the_start_from_the_metadata_and_a_wrong_how_give_two_problems():
    raw = base()
    raw["joins"]["AM"]["ingredients"] = [{"dataset_id": META}, {"dataset_id": "A"}]
    raw["joins"]["AM"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "A", "on": "id", "how": "left"}]
    raw["joins"]["AM"]["tier1"]["steps"].append({"action": "polars_join", "right_ingredient": META, "on": "id", "how": "inner"})
    assert len(problems(raw)) == 2


def test_a_look_up_join_with_how_inner_is_not_affected():
    raw = base()
    raw["additional_datasets_schemas"] = {"L": copy.deepcopy(raw["data_schemas"]["B"])}
    raw["additional_datasets_schemas"]["L"].pop("completion")
    raw["additional_datasets_schemas"]["L"]["input_fields"]["id"].pop("is_entity_id")
    raw["joins"]["AL"] = {"ui_label": "AL", "description": "A with a look-up list.",
                          "ingredients": [{"dataset_id": "A"}, {"dataset_id": "L"}],
                          "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "L", "on": "id", "how": "inner"}]}}
    assert problems(raw) == []


def test_a_table_made_from_the_metadata_with_a_look_up_only_is_not_affected():
    raw = base()
    raw["additional_datasets_schemas"] = {"L": copy.deepcopy(raw["data_schemas"]["B"])}
    raw["joins"]["ML"] = {"ui_label": "ML", "description": "The metadata with a look-up list.",
                          "ingredients": [{"dataset_id": META}, {"dataset_id": "L"}],
                          "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "L", "on": "id", "how": "inner"}]}}
    assert problems(raw) == []


def test_a_recipe_with_no_metadata_is_not_affected():
    assert problems(valid()) == []


def test_a_metadata_join_in_tier2_is_refused_by_st05_and_not_by_j15():
    raw = base()
    raw["joins"]["AM"]["tier2"] = {"steps": [dict(LEFT, how="inner")]}
    codes = [p.code for p in check_recipe(raw, "run", catalogs=CATALOGS).problems]
    assert "ST05" in codes and "J16" not in codes


def test_an_audit_copy_inherits_the_rule():
    raw = base()
    raw["joins"]["AM"]["tier1"]["steps"][0]["how"] = "inner"
    found = [p for p in check_recipe(raw, "audit", catalogs=CATALOGS).problems if p.code == "J16"]
    assert len(found) == 1


# J17 (D-0637): a joined table that lists the metadata but does not join it is refused. The wording is PROVISIONAL; the tests read the code, the path and the words
# that name the table and the way out.

def problems17(raw):
    return [p for p in check_recipe(raw, "run", catalogs=CATALOGS).problems if p.code == "J17"]


def test_j17_a_join_that_lists_the_metadata_and_joins_it_is_accepted():
    assert problems17(base()) == []


def test_j17_a_join_that_lists_the_metadata_and_does_not_join_it_is_refused():
    raw = base()
    raw["joins"]["AM"]["tier1"]["steps"] = []
    found = problems17(raw)
    assert len(found) == 1 and found[0].path == "joins.AM.ingredients"
    assert META in found[0].message and "left join" in found[0].fix and "remove it" in found[0].fix


def test_j17_a_step_that_joins_another_table_does_not_count_as_joining_the_metadata():
    raw = base()
    raw["joins"]["AM"]["ingredients"].append({"dataset_id": "B"})
    raw["joins"]["AM"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]
    assert len(problems17(raw)) == 1


def test_j17_a_join_that_does_not_list_the_metadata_is_not_affected():
    assert problems17(valid()) == []


def test_j17_a_look_up_listed_and_not_joined_is_not_this_checks_business():
    raw = base()
    raw["additional_datasets_schemas"] = {"L": copy.deepcopy(raw["data_schemas"]["B"])}
    raw["joins"]["AM"]["ingredients"].append({"dataset_id": "L"})
    assert problems17(raw) == []


def test_j17_the_metadata_as_the_first_ingredient_with_no_join_is_the_base_and_accepted():
    raw = base()
    raw["joins"]["AM"]["ingredients"] = [{"dataset_id": META}]
    raw["joins"]["AM"]["tier1"]["steps"] = []
    assert problems17(raw) == []


def test_j17_the_metadata_first_with_a_data_table_is_left_to_j16():
    raw = base()
    raw["joins"]["AM"]["ingredients"] = [{"dataset_id": META}, {"dataset_id": "A"}]
    raw["joins"]["AM"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "A", "on": "id", "how": "left"}]
    assert problems17(raw) == []
    assert len(problems(raw)) == 1
