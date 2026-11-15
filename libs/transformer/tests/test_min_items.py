"""The checker refuses, before any data is read, the empty value that an action refuses at run time (min_items).

`MUST_NOT_BE_EMPTY` (transformer/actions/min_items.py) lists the list or mapping parameters that carry `min_items: 1`.
Each one was found by running the action with the empty value: it stopped at run time. This file proves, for each:
  - the schema carries `min_items: 1` and is a valid declaration;
  - `step_problems` refuses the empty value with ST10 (no data involved) and accepts one item;
  - the engine still refuses the step when it runs (the run-time line of defence stays);
  - the registry holds no other `min_items` (a new one must be listed, with its run-time refusal checked here).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_min_items.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from transformer.actions.min_items import MUST_NOT_BE_EMPTY
from utils.errors import TransformationError
from utils.ui_schema import expected_shape, schema_declaration_problems, step_problems

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


@pytest.mark.parametrize("action, name", CASES)
def test_the_engine_still_refuses_the_empty_value_when_it_runs(action, name):
    lf = pl.LazyFrame({"a": [1, 2], "b": [3, 4]})
    with pytest.raises(TransformationError):
        AVAILABLE_WRANGLING_ACTIONS[action](lf, {name: _empty(action, name)})


def test_no_action_carries_a_min_items_that_is_not_listed():
    found = {(a, n) for a, s in ACTION_SCHEMAS.items() for n, d in s["params"].items() if "min_items" in d}
    assert found == set(CASES)
