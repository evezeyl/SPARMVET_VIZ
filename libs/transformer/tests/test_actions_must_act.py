"""An action must do something: a step that cannot act fails, it never returns the frame unchanged (P0, 2026-11-13).

Eve, 2026-11-13: "we need to ensure that the action does something". The rule is the one of ADR-099
(fail instead of warn, for anything declared but not applied) applied to the engine at run time, as a second
line behind the recipe checker (`check_recipe`, which refuses the same step before anything runs).

Measured on 2026-11-13 (`tmpAI/architect/silent_actions_probe.py` and the two helpers below), 67 registered
actions:
  - 17 declare required parameters and accept a step that lacks them: 13 return the frame UNCHANGED
    (drop_columns, explode, filter_eq, filter_gt, filter_lt, filter_ne, filter_range, recode_values,
    round_numeric, split_column, split_to_list, to_struct, unnest) and 4 CHANGE it although nothing was asked
    (count_by_group, keep_columns, summarize, unpivot);
  - 54 accept a key that they do not declare (a typo, a retired alias): for example `filter_gt` with `column`
    instead of `columns` returns every row;
  - drop_nulls, sanitize_column_names, strip_whitespace, unique_rows, sample and describe_stats have no required
    parameter: acting on all columns by default is their contract, not a defect.

These are the actions called directly. In a recipe a schema's wrangling goes through `DataWrangler`, which first
maps the aliases `column`, `source`, `source_column`, `target_column` to `columns`; a join's steps (`DataAssembler`) get no
such mapping. The recipe-level cases are in `app/tests/test_column_names_through_the_steps.py`.

The two tests below are `xfail(strict=True)`: they fail today, and the day the runtime guard exists (a check of
`required` and of unknown keys in `register_action`, planned for after the alias removal of the recipe
migration, #78, because shipped recipes still use aliases such as `source`) the marks fail and must be
removed in that commit. DECISION TO TAKE: the guard needs the aliases gone first (no compatibility shim,
`rules_legacy_management.md`); the order is set with the recipe session (channel message M9).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_actions_must_act.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS


def _frame() -> pl.LazyFrame:
    return pl.LazyFrame({"a": [1, 2, 3], "b": ["x", "y", "z"], "c": [1.5, 2.5, 3.5]})


def _required(name: str) -> list[str]:
    params = ACTION_SCHEMAS.get(name, {}).get("params", {})
    return [key for key, definition in params.items() if definition.get("required")]


def _actions_that_act_on_nothing() -> list[str]:
    """Actions with required parameters that accept a step without them and go on."""
    found = []
    for name, function in sorted(AVAILABLE_WRANGLING_ACTIONS.items()):
        if not _required(name):
            continue
        try:
            function(_frame(), {"action": name})
        except Exception:
            continue
        found.append(name)
    return found


def _actions_that_ignore_an_unknown_key() -> list[str]:
    """Actions that accept a key nobody declared (a typo, an alias) and go on."""
    found = []
    for name, function in sorted(AVAILABLE_WRANGLING_ACTIONS.items()):
        if name not in ACTION_SCHEMAS:
            continue
        spec = {"action": name, "zz_not_a_parameter": 1}
        for key in _required(name):
            definition = ACTION_SCHEMAS[name]["params"][key]
            spec[key] = ["a"] if definition.get("widget") in ("column_selector", "list") and definition.get("multi", True) else "a"
        try:
            function(_frame(), spec)
        except Exception:
            continue
        found.append(name)
    return found


def test_the_probe_sees_the_registry():
    """Guards the two tests below against passing because nothing was looked at."""
    assert len(AVAILABLE_WRANGLING_ACTIONS) > 50
    assert "filter_gt" in AVAILABLE_WRANGLING_ACTIONS and _required("filter_gt")


def test_a_wrong_key_makes_the_filter_do_nothing_today():
    """Pins the finding with the case Eve was shown: `column` instead of `columns` returns every row."""
    from transformer.actions.cleaning.core import action_filter_gt
    out = action_filter_gt(_frame(), {"column": "a", "value": 1}).collect()
    assert out.height == 3


@pytest.mark.xfail(strict=True, reason="no runtime guard yet: 17 actions accept a step without their required parameters")
def test_an_action_without_its_required_parameters_fails():
    assert _actions_that_act_on_nothing() == []


@pytest.mark.xfail(strict=True, reason="no runtime guard yet: an unknown key (typo, retired alias) is ignored silently")
def test_an_action_refuses_a_key_it_does_not_declare():
    assert _actions_that_ignore_an_unknown_key() == []
