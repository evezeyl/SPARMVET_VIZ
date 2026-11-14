"""The 1:1:1 naming law, enforced (ACTION-RECIPES-1, Eve 2026-11-14: "proposal yes"; the join too).

`rules_data_engine.md` section 2: every `@register_action("name")` has a recipe `name_data_analysis_recipe.yaml` and a
data file `name_test.tsv` in `libs/transformer/tests/data/`. This file checks the law and runs every pair through the
real path (ingestion with declared types, then the wrangler, or the assembler for the join), so the files cannot rot
unseen the way the old pairs did (65 recipes in the old format, with four runners that could not even start).

What each test proves:
  - the pair exists for every registered action, and nothing stale is left (a pair of an action that is gone);
  - the recipe is format 1 and its id is the action name;
  - the pair runs, and the recipe really uses the action it is named after;
  - the action acts: the result differs from what ingestion gave (a pair that passes through unchanged proves nothing);
  - for a pair without a setup step the ingested file equals the frame of the equality test and the result equals the
    direct Polars call, so the file layer (TSV, declared types, `null_values`) loses nothing between file and action;
  - every registered action is also tested for its behaviour: a case in `test_polars_actions_equal_polars.py` or a
    test file of its own that names it (a new action without a test fails here).

`polars_join` has two ingredients: its pair is a recipe with two data schemas (`polars_join_test.tsv` is the left,
`polars_join_test_right.tsv` the right) and the join is run by the assembler, as the app runs it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_action_recipe_pairs.py -q
"""
import re
from pathlib import Path

import polars as pl
import pytest
import yaml
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401  (loads the registry)
from ingestion.ingestor import DataIngestor
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from transformer.data_assembler import DataAssembler
from transformer.data_wrangler import DataWrangler

import test_polars_actions_equal_polars as eq

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
JOIN = "polars_join"
PAIRED = sorted(AVAILABLE_WRANGLING_ACTIONS)

# the direct Polars call of the action that is not plain Polars (a filter on the same column)
OWN_EXPECTED = {"modif_filter": lambda lf: lf.filter(pl.col("n") > 1)}
# the actions that are not plain Polars calls: the test file that checks their behaviour
OWN_TESTS = {"modif_filter": "test_modif_filter.py", "step_top_n_other": "test_top_n_other.py"}

FIRST = {}  # the first case of an action is the one its pair holds
for _c in eq.CASES:
    FIRST.setdefault(_c.action, _c)


def _recipe(action):
    return yaml.safe_load((DATA / f"{action}_data_analysis_recipe.yaml").read_text())


def _run(action):
    """The pair through the real path: (ingested left table, result, the actions the recipe uses)."""
    recipe = _recipe(action)
    ingestor = DataIngestor(str(DATA))
    if action == JOIN:
        ingredients = {name: ingestor.ingest(name, schema)[0] for name, schema in recipe["data_schemas"].items()}
        steps = next(iter(recipe["joins"].values()))["steps"]["tier1"]
        left = ingredients[action].collect()
        return left, DataAssembler(ingredients, recipe_id=action, join_id=next(iter(recipe['joins']))).assemble(steps).collect(), [s["action"] for s in steps]
    steps = recipe["wrangling"]["tier1"]
    before = ingestor.ingest(action, recipe)[0].collect()
    return before, DataWrangler().run(before.lazy(), steps).collect(), [s["action"] for s in steps]


# -- the law ----------------------------------------------------------------------------------

@pytest.mark.parametrize("action", PAIRED)
def test_every_registered_action_has_its_pair(action):
    assert (DATA / f"{action}_data_analysis_recipe.yaml").exists(), f"no recipe for {action}"
    assert (DATA / f"{action}_test.tsv").exists(), f"no data file for {action}"


def test_the_join_has_the_data_of_its_second_ingredient():
    assert (DATA / f"{JOIN}_test_right.tsv").exists()


def test_no_pair_is_left_for_an_action_that_does_not_exist():
    names = {re.sub(r"_(data_analysis_recipe\.yaml|test\.tsv)$", "", p.name)
             for p in DATA.iterdir() if p.name.endswith(("_data_analysis_recipe.yaml", "_test.tsv"))}
    stale = names - set(AVAILABLE_WRANGLING_ACTIONS)
    assert stale == set(), "stale pairs: " + ", ".join(sorted(stale))


@pytest.mark.parametrize("action", PAIRED)
def test_the_recipe_is_format_1_and_its_id_is_the_action(action):
    recipe = _recipe(action)
    assert recipe["spec_version"] == 1 and recipe["id"] == action


# -- the pair runs ----------------------------------------------------------------------------

@pytest.mark.parametrize("action", PAIRED)
def test_the_pair_runs_through_the_real_path_and_the_action_acts(action, monkeypatch):
    monkeypatch.chdir(ROOT)  # the source paths in the recipes are relative to the project root
    before, after, used = _run(action)
    assert action in used, "the recipe does not use the action it is named after"
    assert not (after.shape == before.shape and after.schema == before.schema and after.equals(before)), \
        "the pair passes through unchanged: it proves nothing"


# -- the file layer loses nothing -------------------------------------------------------------

@pytest.mark.parametrize("action", sorted(a for a in FIRST if FIRST[a].frame is not eq.LISTS and FIRST[a].frame is not eq.STRUCTS))
def test_the_ingested_file_is_the_frame_of_the_case_and_the_result_equals_polars(action, monkeypatch):
    monkeypatch.chdir(ROOT)
    case = FIRST[action]
    ingested, got, _ = _run(action)
    assert_frame_equal(ingested, case.frame)  # the TSV, the declared types and null_values lose nothing
    assert_frame_equal(got, eq.eager(case.polars(case.frame.lazy())))


def test_the_filter_pair_equals_the_polars_filter(monkeypatch):
    monkeypatch.chdir(ROOT)
    ingested, got, _ = _run("modif_filter")
    assert_frame_equal(got, eq.eager(OWN_EXPECTED["modif_filter"](ingested.lazy())))


# -- every action is tested for its behaviour --------------------------------------------------

@pytest.mark.parametrize("action", PAIRED)
def test_every_registered_action_has_a_behaviour_test(action):
    if action in FIRST:
        return  # a case of the equality test with Polars
    assert action in OWN_TESTS, f"{action} has no case in test_polars_actions_equal_polars.py and no test file of its own in OWN_TESTS"
    text = (HERE / OWN_TESTS[action]).read_text()
    assert action in text, f"{OWN_TESTS[action]} does not name {action}"


def test_the_own_tests_list_has_no_action_that_is_gone():
    assert set(OWN_TESTS) <= set(AVAILABLE_WRANGLING_ACTIONS)
