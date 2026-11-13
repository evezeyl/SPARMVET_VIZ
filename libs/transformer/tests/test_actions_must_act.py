"""An action must do something: a step that cannot act fails, it never returns the frame unchanged (P0, 2026-11-13).

Eve, 2026-11-13: "we need to ensure that the action does something". The rule is the one of ADR-099 (fail instead of warn,
for anything declared but not applied) applied to the engine at run time, as a second line behind the recipe checker
(`check_recipe`, which refuses the same step before anything runs). Every action of the registry judges its step with
`utils.ui_schema.step_problems`; this file proves it for ALL registered actions, not for the ones somebody remembered.

Before the recipe format (measured 2026-11-13 over the 67 old actions): 13 returned the frame unchanged without their
required parameters, 4 changed it although nothing was asked, 54 accepted a key they did not declare (`filter_gt` with
`column` instead of `columns` returned every row).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_actions_must_act.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError


def _frame() -> pl.LazyFrame:
    return pl.LazyFrame({"a": [1, 2, 3], "b": ["x", "y", "z"], "c": [1.5, 2.5, 3.5]})


def _required(name: str) -> list:
    return [k for k, d in ACTION_SCHEMAS[name]["params"].items() if d.get("required")]


def _value_for(definition: dict):
    """A value of the right form for a required parameter (the content does not matter, the key does)."""
    widget = definition.get("widget")
    if widget in ("column_selector", "list") and definition.get("multi", True):
        return ["a"]
    if widget == "mapping":
        return {"a": "b"}
    if widget == "bool":
        return True
    if widget == "number":
        return 1
    if widget == "enum":
        return definition["options"][0]
    return "a"


def test_the_probe_sees_the_registry():
    assert len(AVAILABLE_WRANGLING_ACTIONS) >= 40 and _required("polars_sort")


ACTIONS_WITH_REQUIRED = [n for n in sorted(AVAILABLE_WRANGLING_ACTIONS) if _required(n)]


@pytest.mark.parametrize("name", ACTIONS_WITH_REQUIRED)
def test_an_action_without_its_required_parameters_fails(name):
    with pytest.raises(TransformationError, match="required"):
        AVAILABLE_WRANGLING_ACTIONS[name](_frame(), {})


@pytest.mark.parametrize("name", sorted(AVAILABLE_WRANGLING_ACTIONS))
def test_an_action_refuses_a_key_it_does_not_declare(name):
    spec = {k: _value_for(ACTION_SCHEMAS[name]["params"][k]) for k in _required(name)}
    spec["zz_not_a_parameter"] = 1
    with pytest.raises(TransformationError, match="zz_not_a_parameter"):
        AVAILABLE_WRANGLING_ACTIONS[name](_frame(), spec)


@pytest.mark.parametrize("old_key", ["column", "source", "source_column", "target_column"])
def test_the_old_column_aliases_are_not_guessed(old_key):
    with pytest.raises(TransformationError, match=old_key):
        AVAILABLE_WRANGLING_ACTIONS["polars_drop"](_frame(), {old_key: "a"})
