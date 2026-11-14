"""The 1:1:1 naming law, enforced (ACTION-RECIPES-1, Eve 2026-11-14: "proposal yes").

`rules_data_engine.md` section 2: every `@register_action("name")` has a recipe `name_data_analysis_recipe.yaml` and a
data file `name_test.tsv` in `libs/transformer/tests/data/`. This file checks the law and runs every pair through the
real path (ingestion with declared types, then the wrangler), so the files cannot rot unseen the way the old pairs did
(65 recipes in the old format, with four runners that could not even start).

What each test proves:
  - the pair exists for every registered action, and nothing stale is left (a pair of an action that is gone);
  - the recipe is format 1 and its id is the action name;
  - the pair runs, and the recipe really uses the action it is named after;
  - the action acts: the result differs from what ingestion gave (a pair that passes through unchanged proves nothing);
  - for a pair without a setup step the result equals the direct Polars call of the equality test, so the file layer
    (TSV, declared types, `null_values`) loses nothing between the file and the action.

`polars_join` has no pair: a join needs a second ingredient and runs in the assembler (`test_polars_actions_equal_polars.py`
and the assembler tests cover it); the old suite skipped it too.

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
from transformer.data_wrangler import DataWrangler

import test_polars_actions_equal_polars as eq

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "libs/transformer/tests/data"
NO_PAIR = {"polars_join"}
PAIRED = sorted(set(AVAILABLE_WRANGLING_ACTIONS) - NO_PAIR)

# the direct Polars call of the two actions that are not plain Polars cases (a filter on the same column)
OWN_EXPECTED = {"modif_filter": lambda lf: lf.filter(pl.col("n") > 1)}


def _recipe(action):
    return yaml.safe_load((DATA / f"{action}_data_analysis_recipe.yaml").read_text())


def _ingest(action):
    """The pair through the real ingestion; the source path in the recipe is relative to the project root."""
    recipe = _recipe(action)
    lf, _ = DataIngestor(str(DATA)).ingest(action, recipe)
    return recipe, lf


def _steps(recipe):
    return recipe["wrangling"]["tier1"]


# -- the law ----------------------------------------------------------------------------------

@pytest.mark.parametrize("action", PAIRED)
def test_every_registered_action_has_its_pair(action):
    assert (DATA / f"{action}_data_analysis_recipe.yaml").exists(), f"no recipe for {action}"
    assert (DATA / f"{action}_test.tsv").exists(), f"no data file for {action}"


def test_no_pair_is_left_for_an_action_that_does_not_exist():
    names = {re.sub(r"_(data_analysis_recipe\.yaml|test\.tsv)$", "", p.name)
             for p in DATA.iterdir() if p.name.endswith(("_data_analysis_recipe.yaml", "_test.tsv"))}
    assert names - set(AVAILABLE_WRANGLING_ACTIONS) == set(), "stale pairs: " + ", ".join(sorted(names - set(AVAILABLE_WRANGLING_ACTIONS)))


def test_the_only_action_without_a_pair_is_the_join():
    assert NO_PAIR == {"polars_join"}


@pytest.mark.parametrize("action", PAIRED)
def test_the_recipe_is_format_1_and_its_id_is_the_action(action):
    recipe = _recipe(action)
    assert recipe["spec_version"] == 1 and recipe["id"] == action


# -- the pair runs ----------------------------------------------------------------------------

@pytest.mark.parametrize("action", PAIRED)
def test_the_pair_runs_through_ingestion_and_the_wrangler_and_the_action_acts(action, monkeypatch):
    monkeypatch.chdir(ROOT)
    recipe, lf = _ingest(action)
    assert action in [s["action"] for s in _steps(recipe)], "the recipe does not use the action it is named after"
    before = lf.collect()
    after = DataWrangler().run(before.lazy(), _steps(recipe)).collect()
    assert not (after.shape == before.shape and after.schema == before.schema and after.equals(before)), \
        "the pair passes through unchanged: it proves nothing"


# -- the file layer loses nothing -------------------------------------------------------------

FIRST = {}  # the first case of an action is the one its pair holds
for _c in eq.CASES:
    FIRST.setdefault(_c.action, _c)


@pytest.mark.parametrize("action", sorted(a for a in FIRST if a != "polars_join" and FIRST[a].frame is not eq.LISTS and FIRST[a].frame is not eq.STRUCTS))
def test_the_ingested_file_is_the_frame_of_the_case_and_the_result_equals_polars(action, monkeypatch):
    monkeypatch.chdir(ROOT)
    case = FIRST[action]
    recipe, lf = _ingest(action)
    ingested = lf.collect()
    assert_frame_equal(ingested, case.frame)  # the TSV, the declared types and null_values lose nothing
    got = DataWrangler().run(ingested.lazy(), _steps(recipe)).collect()
    assert_frame_equal(got, eq.eager(case.polars(case.frame.lazy())))


def test_the_filter_pair_equals_the_polars_filter(monkeypatch):
    monkeypatch.chdir(ROOT)
    recipe, lf = _ingest("modif_filter")
    ingested = lf.collect()
    got = DataWrangler().run(ingested.lazy(), _steps(recipe)).collect()
    assert_frame_equal(got, eq.eager(OWN_EXPECTED["modif_filter"](ingested.lazy())))
