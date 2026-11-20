"""The load gate never passes a recipe on a check that read fewer steps than the recipe writes (D-0050).

After the recipe form changed (tiers as keys, D-0250) the gate looked for the old keys, found no step, checked nothing and
passed `retest_bad_select_column`, a recipe that is broken on purpose. These tests hold the gate to the count of steps
written in the recipe: a check that read fewer is a fault of the app, reported loudly, never a pass.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gate_reads_every_step.py -q
"""
from pathlib import Path

import pytest
import yaml

from app.modules import data_analysis_recipe_validator as validator
from app.modules.data_analysis_recipe_validator import (
    count_steps_written, engine_load_problems, unread_steps_problem, validate_data_analysis_recipe_data)
from transformer.data_wrangler import DataWrangler
from utils.recipe_factory import minimal_recipe

ROOT = Path(__file__).resolve().parents[2]
RETEST = ROOT / "config" / "data_analysis_recipes" / "retest"
RAW = ROOT / "assets" / "test_data"

STEP = {"action": "polars_drop_nulls", "subset": ["value"]}


# -- the count of steps written, which does not know the tiers ---------------------------------------------------

def test_the_count_finds_steps_in_the_new_shape_and_in_the_old_shapes():
    assert count_steps_written({"tier1": {"steps": [STEP, STEP]}, "tier2": {"steps": [STEP]}}) == 3
    assert count_steps_written({"wrangling": {"tier1": [STEP], "tier2": []}}) == 1
    assert count_steps_written({"steps": {"tier1": [STEP]}}) == 1
    assert count_steps_written({"a": [{"b": [STEP]}]}) == 1


def test_the_count_is_zero_where_nothing_is_a_step():
    assert count_steps_written({}) == 0
    assert count_steps_written({"layers": [{"name": "geom_point"}], "input_fields": {"a": {"type": "String"}}}) == 0
    assert count_steps_written("action") == 0
    assert count_steps_written([{"name": "x"}, "action"]) == 0


def test_a_mapping_that_is_not_in_a_list_is_not_counted_as_a_step():
    assert count_steps_written({"action": "polars_cast"}) == 0


# -- the problem ----------------------------------------------------------------------------------------------

def test_no_problem_when_the_check_read_every_step():
    assert unread_steps_problem("r.yaml", "recipe", 4, 4) is None
    assert unread_steps_problem("r.yaml", "recipe", 0, 0) is None


def test_a_check_that_read_fewer_steps_is_a_problem_of_the_app_with_the_numbers():
    problem = unread_steps_problem("r.yaml", "recipe", 5, 0)
    assert problem is not None
    assert "read 0 of the 5 steps" in problem.problem and "5 step(s) were not checked" in problem.problem
    assert "fault of the app" in problem.tip


# -- the structure half: engine_load_problems -------------------------------------------------------------------

def _write(tmp_path, recipe):
    path = tmp_path / f"{recipe['id']}.yaml"
    path.write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    return path


def _recipe_with_steps():
    recipe = minimal_recipe("with_steps")
    schema = next(iter(recipe["data_schemas"].values()))
    schema["tier1"] = {"steps": [dict(STEP)]}
    return recipe


def test_a_recipe_whose_steps_are_read_gives_no_problem(tmp_path):
    assert engine_load_problems(_write(tmp_path, _recipe_with_steps())) == []


def test_a_reader_that_finds_no_step_in_a_recipe_that_has_steps_is_a_problem_not_a_pass(tmp_path, monkeypatch):
    """The failure of the changeover: the reader looked in the wrong place and returned nothing."""
    monkeypatch.setattr(DataWrangler, "tier_steps", staticmethod(lambda body, tier, audit=False: []))
    problems = engine_load_problems(_write(tmp_path, _recipe_with_steps()))
    assert [p.location for p in problems] == ["recipe"]
    assert "read 0 of the 1 steps" in problems[0].problem
    assert "fault of the app" in problems[0].tip


def test_a_recipe_with_no_steps_is_not_blamed_when_the_reader_finds_none(tmp_path, monkeypatch):
    monkeypatch.setattr(DataWrangler, "tier_steps", staticmethod(lambda body, tier, audit=False: []))
    assert engine_load_problems(_write(tmp_path, minimal_recipe("no_steps"))) == []


def test_a_tier_in_an_old_shape_is_one_problem_at_its_place_and_no_second_one(tmp_path):
    recipe = _recipe_with_steps()
    schema = next(iter(recipe["data_schemas"].values()))
    schema["tier1"] = [dict(STEP)]  # written as a list: the old shape
    problems = engine_load_problems(_write(tmp_path, recipe))
    assert len(problems) == 1 and problems[0].location.endswith(".tier1")
    assert "list" in problems[0].problem


# -- the data half: validate_data_analysis_recipe_data --------------------------------------------------------

def test_retest_bad_select_column_is_rejected_for_its_real_reason():
    """The recipe that passed the gate when the readers looked for `wrangling`: its select step names a column that does not exist."""
    problems = validate_data_analysis_recipe_data(RETEST / "retest_bad_select_column.yaml", RAW)
    assert len(problems) == 1
    assert 'unable to find column "phenotype"' in str(problems[0])


def test_a_data_check_that_ran_none_of_the_written_steps_is_a_problem_not_a_pass(monkeypatch):
    monkeypatch.setattr(DataWrangler, "tier_steps", staticmethod(lambda body, tier, audit=False: []))
    problems = validate_data_analysis_recipe_data(RETEST / "retest_bad_select_column.yaml", RAW)
    assert problems, "the gate must not pass a recipe whose steps it did not run"
    assert any("were not checked" in p.problem and "fault of the app" in (p.tip or "") for p in problems)


def test_the_check_of_a_good_recipe_with_steps_is_still_clean():
    assert validate_data_analysis_recipe_data(RETEST / "retest_tier2.yaml", RAW) == []


def test_the_validator_uses_the_one_reader_of_the_engine():
    """The count is held against `DataWrangler.tier_steps`, the reader the orchestrator calls (`prepare_ingredient`)."""
    import inspect
    from app.modules import orchestrator
    from app.modules.engine_registry import REGISTRY
    from transformer import DataWrangler
    # the orchestrator reaches the reader through the entry of the data engine (D-0219); the entry's class is the validator's
    assert "wrangler.tier_steps(ds_schema" in inspect.getsource(orchestrator.DataOrchestrator.prepare_ingredient)
    assert REGISTRY["python-polars"].wrangler is DataWrangler
    assert "DataWrangler.tier_steps" in inspect.getsource(validator.validate_data_analysis_recipe_data)
