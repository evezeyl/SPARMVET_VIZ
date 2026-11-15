"""The checker refuses, before any data is read, the empty value that an action refuses at run time (min_items).

`MUST_NOT_BE_EMPTY` (transformer/actions/min_items.py) lists the list or mapping parameters that carry `min_items: 1`.
Each one was found by running the action with the empty value: it stopped at run time. This file proves, for each:
  - the schema carries `min_items: 1` and is a valid declaration;
  - `step_problems` refuses the empty value with ST10 (no data involved) and accepts one item;
  - the engine still refuses the step when it runs (the run-time line of defence stays);
  - the registry holds no other `min_items` (a new one must be listed, with its run-time refusal checked here).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_min_items.py -q
"""
from pathlib import Path

import pytest
import yaml

import transformer.actions  # noqa: F401
from ingestion.ingestor import DataIngestor
from transformer.actions.base import ACTION_SCHEMAS
from transformer.data_assembler import DataAssembler
from transformer.data_wrangler import DataWrangler
from transformer.actions.min_items import EMPTY_HAS_A_MEANING, MUST_NOT_BE_EMPTY
from utils.errors import TransformationError
from utils.ui_schema import expected_shape, schema_declaration_problems, step_problems

DATA = Path(__file__).resolve().parent / "data"
JOINS = ("polars_join", "polars_join_asof", "polars_join_where")
CASES = [(a, p) for a, names in sorted(MUST_NOT_BE_EMPTY.items()) for p in names]


def _empty(action, name):
    return {} if expected_shape(ACTION_SCHEMAS[action]["params"][name]) == "mapping" else []


def _one(action, name):
    return {"a": "pl.len()"} if expected_shape(ACTION_SCHEMAS[action]["params"][name]) == "mapping" else ["a"]


@pytest.mark.parametrize("action, name", CASES)
def test_the_schema_carries_min_items_and_is_a_valid_declaration(action, name):
    assert ACTION_SCHEMAS[action]["params"][name]["min_items"] == 1
    assert schema_declaration_problems(ACTION_SCHEMAS[action]) == []


@pytest.mark.parametrize("action, name", CASES)
def test_the_checker_refuses_the_empty_value_with_st10_and_accepts_one_item(action, name):
    schema = ACTION_SCHEMAS[action]
    empty = [p for p in step_problems(action, {"action": action, name: _empty(action, name)}, schema) if p.param == name]
    assert [p.code for p in empty] == ["ST10"], empty
    assert "at least 1" in empty[0].fix
    one = [p for p in step_problems(action, {"action": action, name: _one(action, name)}, schema) if p.param == name]
    assert one == []


def _run_pair_with(action, name, value):
    """The action's own 1:1:1 pair, with one parameter replaced, run through the real path (ingestion, wrangler or assembler)."""
    recipe = yaml.safe_load((DATA / f"{action}_data_analysis_recipe.yaml").read_text())
    joins = action in JOINS
    steps = next(iter(recipe["joins"].values()))["steps"]["tier1"] if joins else recipe["wrangling"]["tier1"]
    step = next(s for s in steps if s["action"] == action)
    step[name] = value
    # a left/right/by pair is an alternative to `on`/`by`: drop the one it replaces so the empty value is the only fault
    for plain, sides in (("on", ("left_on", "right_on")), ("by", ("by_left", "by_right"))):
        if name in sides:
            step.pop(plain, None)
            step.setdefault(sides[1] if name == sides[0] else sides[0], step.get(name))
    ingestor = DataIngestor(str(DATA))
    if joins:
        ingredients = {n: ingestor.ingest(n, s)[0] for n, s in recipe["data_schemas"].items()}
        return DataAssembler(ingredients, recipe_id=action, join_id=next(iter(recipe["joins"]))).assemble(steps).collect(), ingredients[action].collect()
    before = ingestor.ingest(action, recipe)[0].collect()
    return DataWrangler().run(before.lazy(), steps).collect(), before


@pytest.mark.parametrize("action, name", CASES)
def test_the_engine_refuses_the_empty_value_when_the_step_runs(action, name):
    with pytest.raises(TransformationError):
        _run_pair_with(action, name, _empty(action, name))


# ---- the sweep as a test: no empty list or mapping may be a silent no-op ------------------------------------

LIST_OR_MAPPING = [(a, n) for a, s in sorted(ACTION_SCHEMAS.items()) for n, d in s["params"].items()
                   if expected_shape(d) in ("list", "list_of_mapping", "mapping")]


@pytest.mark.parametrize("action, name", LIST_OR_MAPPING)
def test_an_empty_list_or_mapping_is_refused_or_has_a_declared_meaning(action, name):
    if (action, name) in EMPTY_HAS_A_MEANING:
        assert "min_items" not in ACTION_SCHEMAS[action]["params"][name]
        return
    spec = {"action": action, name: _empty(action, name)}
    refused = [p for p in step_problems(action, spec, ACTION_SCHEMAS[action]) if p.param == name and p.code == "ST10"]
    assert refused and "is empty, so the step would do nothing" in refused[0].message, f"{action}.{name}: an empty value would be accepted by the checker"


def test_the_description_of_each_meaning_says_what_an_empty_value_gives():
    for (action, name), meaning in EMPTY_HAS_A_MEANING.items():
        assert f"An empty `{name}` gives {meaning}." in ACTION_SCHEMAS[action]["description"]


def test_no_action_carries_a_min_items_that_is_not_listed():
    found = {(a, n) for a, s in ACTION_SCHEMAS.items() for n, d in s["params"].items() if "min_items" in d}
    assert found == set(CASES)
