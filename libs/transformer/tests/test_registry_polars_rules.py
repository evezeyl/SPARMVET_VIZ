"""The registry rules of the new action names (W6, tests first, 2026-11-13; `recipe_format_spec.md` 7.5.1, DEC31 to DEC35).

Rules, each executable:
  1. the prefix and the registry field `polars` say the same thing: `polars_` is `exact` or `wrapper`, `modif_` is
     `modified`, `step_` is `composite`; no action name without a prefix remains;
  2. no hidden choice: a `polars_` action exposes every parameter of the Polars call it wraps (`wraps`), and a
     parameter that has a default in Polars either is required or carries the SAME default; a `modif_` or `step_`
     parameter has a default only when it is marked `off_when_absent` (the parameter does nothing when absent);
  3. the schema rules of W1 (`rules`) of every action are sound (`schema_declaration_problems`).

The functions that judge a schema are tested here on schemas written for the test (they run today and can
fail: a missing parameter and a wrong default are caught). The registry tests are strict xfail until W6 builds
the actions; the day they pass, the marks fail and are removed in that commit.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_registry_polars_rules.py -q
"""
import inspect

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS
from utils.ui_schema import schema_declaration_problems

PREFIX_TO_FIELD = {"polars_": {"exact", "wrapper"}, "modif_": {"modified"}, "step_": {"composite"}}
# parameters that are ours, not Polars': where an expression is applied, a table by id, the engine's own keys
OURS = {"columns", "target_column", "right_ingredient"}
# Polars parameters that are written differently in a recipe because Polars takes them as *args or **kwargs
POLARS_NAME_FOR = {"more_exprs": "exprs", "named_exprs": "named_exprs", "args": "exprs", "kwargs": "named_exprs"}
# the data argument of a Polars function or method is the table the step works on, never a parameter
DATA_ARGUMENTS = {"self", "cls"}


def prefix_of(name):
    return next((p for p in PREFIX_TO_FIELD if name.startswith(p)), None)


def resolve_wrapped(schema):
    """The Polars object named by the first `wraps` entry, or None."""
    entries = schema.get("wraps") or []
    if not entries:
        return None
    obj = pl
    for attr in entries[0]["attr_path"]:
        obj = getattr(obj, attr)
    return obj


def polars_parameter_problems(schema):
    """Why a polars_ action does not expose its Polars call as it is (empty list: it does)."""
    target = resolve_wrapped(schema)
    if target is None:
        return ["a polars_ action must name the Polars call it wraps in `wraps`"]
    params = schema.get("params", {})
    problems = []
    for name, p in inspect.signature(target).parameters.items():
        if name in DATA_ARGUMENTS:
            continue
        ours = POLARS_NAME_FOR.get(name, name)
        if ours not in params:
            problems.append(f"Polars parameter {name!r} is not exposed (expected {ours!r})")
            continue
        if p.default is not inspect.Parameter.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            declared = params[ours]
            # no `default` key means "absent: Polars' own default applies", which is what we want
            if not declared.get("required") and "default" in declared and declared["default"] != p.default:
                problems.append(f"{ours!r}: default {declared['default']!r} differs from Polars' {p.default!r}; make it required or use Polars' default")
    return problems


def hidden_default_problems(schema):
    """modif_ and step_: a default is allowed only when the parameter is off when absent."""
    return [f"{name!r} has the default {d['default']!r} but is not marked off_when_absent"
            for name, d in schema.get("params", {}).items()
            if "default" in d and not d.get("off_when_absent") and not d.get("required")]


# -- the judging functions work (run today, and can fail) -------------------------------------

UNIQUE_OK = {"wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "unique"]}],
             "params": {"subset": {}, "keep": {"required": True}, "maintain_order": {"default": False}}}


def test_a_complete_polars_schema_has_no_problem():
    assert polars_parameter_problems(UNIQUE_OK) == []


def test_a_missing_polars_parameter_is_found():
    schema = {**UNIQUE_OK, "params": {k: v for k, v in UNIQUE_OK["params"].items() if k != "keep"}}
    assert any("'keep'" in p for p in polars_parameter_problems(schema))


def test_a_default_that_is_not_the_polars_default_is_found():
    schema = {**UNIQUE_OK, "params": {**UNIQUE_OK["params"], "maintain_order": {"default": True}}}
    assert any("maintain_order" in p for p in polars_parameter_problems(schema))


def test_a_polars_schema_without_wraps_is_found():
    assert polars_parameter_problems({"params": {}})


def test_a_hidden_default_in_a_modified_action_is_found():
    assert hidden_default_problems({"params": {"fraction": {"default": 0.1}}})
    assert not hidden_default_problems({"params": {"fraction": {"required": True}, "flag": {"default": False, "off_when_absent": True}}})


def test_the_prefix_table_is_complete():
    assert prefix_of("polars_select") == "polars_" and prefix_of("modif_filter") == "modif_" and prefix_of("step_x") == "step_"
    assert prefix_of("select") is None


# -- the registry (strict xfail until W6) -----------------------------------------------------

NOT_BUILT = "W6 not built: the registry still has the old action names"


def _actions():
    return sorted(AVAILABLE_WRANGLING_ACTIONS)


def test_the_registry_is_not_empty():
    assert len(_actions()) > 50


@pytest.mark.xfail(strict=True, reason=NOT_BUILT + " (no unprefixed name may remain)")
def test_every_action_name_has_one_of_the_three_prefixes():
    assert [n for n in _actions() if prefix_of(n) is None] == []


@pytest.mark.xfail(strict=True, reason=NOT_BUILT + " (the field `polars` does not exist yet)")
def test_the_registry_field_and_the_prefix_agree():
    bad = [n for n in _actions() if ACTION_SCHEMAS.get(n, {}).get("polars") not in PREFIX_TO_FIELD.get(prefix_of(n) or "", set())]
    assert bad == []


@pytest.mark.xfail(strict=True, reason=NOT_BUILT + " (there is no polars_ action yet)")
def test_every_polars_action_exposes_its_polars_call_with_polars_defaults():
    polars_actions = [n for n in _actions() if n.startswith("polars_")]
    assert len(polars_actions) >= 35, "the 37 planned polars_ actions are not all registered"
    problems = {n: polars_parameter_problems(ACTION_SCHEMAS[n]) for n in polars_actions}
    assert {n: p for n, p in problems.items() if p} == {}


@pytest.mark.xfail(strict=True, reason=NOT_BUILT + " (no modif_ or step_ action yet)")
def test_modified_and_composite_actions_hide_no_default():
    names = [n for n in _actions() if n.startswith(("modif_", "step_"))]
    assert names, "no modif_ or step_ action is registered"
    assert {n: hidden_default_problems(ACTION_SCHEMAS[n]) for n in names if hidden_default_problems(ACTION_SCHEMAS[n])} == {}


def test_the_schema_rules_of_every_action_are_sound():
    """W1's `rules` (when, require, one_of, exclusive) must name parameters the action declares. Passes today."""
    bad = {n: schema_declaration_problems(ACTION_SCHEMAS[n]) for n in _actions() if n in ACTION_SCHEMAS and schema_declaration_problems(ACTION_SCHEMAS[n])}
    assert bad == {}
