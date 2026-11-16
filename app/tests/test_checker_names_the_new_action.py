"""The checker names the new action when a recipe uses an old action name (D-0099), with the catalogs of the app.

The unit of the table is `libs/transformer/tests/test_old_action_names_are_named.py`; here the real catalogs go through the
real checker: the message says what happens, then each remedy starts with "Suggestion:". A name with no known
replacement is refused with its reason and no invented suggestion.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_checker_names_the_new_action.py -q
"""
import copy
from pathlib import Path

import pytest
import yaml

from app.modules.data_analysis_recipe_validator import checker_catalogs
from utils.recipe_check import check_recipe
from utils.step_migration import NEW_ACTIONS, REMOVED_ACTIONS

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = yaml.safe_load((ROOT / "config/data_analysis_recipes/templates/simple_template.yaml").read_text())
CATALOGS = checker_catalogs()


def refusal(name):
    raw = copy.deepcopy(TEMPLATE)
    raw["joins"]["main_collection"]["steps"]["tier1"].append({"action": name})
    return [p for p in check_recipe(raw, "run", file_stem="simple_template", catalogs=CATALOGS).errors if p.code == "ST02"]


@pytest.mark.parametrize("old", sorted(NEW_ACTIONS))
def test_an_old_name_is_refused_with_the_new_action_named(old):
    problems = refusal(old)
    assert len(problems) == 1
    assert problems[0].message.startswith(f"'{old}' is not a registered action")
    assert problems[0].fix == f"Suggestion: use {NEW_ACTIONS[old]}."


def test_an_old_name_with_no_replacement_gets_the_reason_and_no_invented_suggestion():
    for name in ("scan_parquet", "sink_parquet"):
        problem, = refusal(name)
        assert "engine function" in problem.message and "use " not in problem.fix
        assert problem.fix == "Suggestion: choose a registered action."


def test_a_misspelt_name_gets_the_closest_registered_action_as_a_suggestion():
    problem, = refusal("polars_sortt")
    assert problem.fix == "Suggestion: write polars_sort."


def test_the_removed_actions_of_the_older_table_still_name_their_replacement():
    problem, = refusal("polars_join_where")
    assert "Suggestion: use modif_join_where." == problem.fix
    assert set(REMOVED_ACTIONS) <= set(CATALOGS["old_action_names"])
