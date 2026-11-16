"""An old action name is refused with the new action named (D-0099, D-0050).

About 67 names of the old recipe format are not actions any more. The refusal said "not a registered action" and left the
author to find the new name. Where the repository knows the new name (the migration writes it), the refusal says
"Suggestion: use <new>"; where it knows nothing, it says why the name left and invents nothing.

What each test proves:
  - the table of new names (`NEW_ACTIONS`) is what the converters really write, case by case, so it cannot drift;
  - every name in it is a registered action;
  - the names with no replacement are exactly the two engine functions, listed here so that a change is visible;
  - the four places that refuse a name (checker ST02, registry, wrangler, assembler) say the new name.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_old_action_names_are_named.py -q
"""
import copy

import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from test_step_conversion import ALL_CASES, TEXT_COLUMNS
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as REGISTERED
from transformer.data_assembler import DataAssembler
from transformer.data_wrangler import DataWrangler
from transformer.registry import get_action_function
from utils.errors import TransformationError
from utils.step_migration import CONVERTERS, NEW_ACTIONS, REMOVED_ACTIONS, convert_step, old_action_hint, removed_action_catalog

# the old actions that no test case of test_step_conversion.py converts, with a step that the converter reads
EXTRA_STEPS = {
    "null_if": {"action": "null_if", "columns": ["a"], "value": "x"},
    "split_column_to_parts": {"action": "split_column_to_parts", "column": "p", "new_columns": ["a", "b"]},
}
OLD_NAMES = set(CONVERTERS) | {"keep_columns", "drop_columns", "strip_whitespace"} | set(REMOVED_ACTIONS)


def actions_written(step, **options):
    return sorted({new["action"] for new in convert_step(copy.deepcopy(step), strings=TEXT_COLUMNS, **options)})


def test_every_old_action_name_has_an_entry_in_the_catalog():
    assert set(removed_action_catalog()) >= OLD_NAMES
    assert len(OLD_NAMES) >= 60  # about 67: if it drops, a name was lost


def test_the_new_names_are_what_the_converters_write():
    written = {}
    for _, step, _ in ALL_CASES:
        written.setdefault(step["action"], set()).update(actions_written(step))
    for name, step in EXTRA_STEPS.items():
        written[name] = set(actions_written(step))
    written["keep_columns"] = set(actions_written({"action": "keep_columns", "columns": ["a"]}, run="B", keys=[]))
    written["drop_columns"] = set(actions_written({"action": "drop_columns", "columns": ["a"]}, run="B", keys=[]))
    assert set(NEW_ACTIONS) == set(written)
    for name, actions in written.items():
        assert sorted(part.strip() for part in NEW_ACTIONS[name].split(",")) == sorted(actions), name


def test_every_new_name_is_a_registered_action():
    for old, new in NEW_ACTIONS.items():
        for part in new.split(","):
            assert part.strip() in REGISTERED, (old, part)


def test_the_names_with_no_replacement_are_the_two_engine_functions():
    nothing = sorted(name for name, entry in removed_action_catalog().items() if not entry["use"])
    assert nothing == ["scan_parquet", "sink_parquet"]
    for name in nothing:
        assert old_action_hint(name) is None and removed_action_catalog()[name]["why"]


@pytest.mark.parametrize("old", sorted(NEW_ACTIONS))
def test_the_registry_names_the_new_action(old):
    with pytest.raises(ValueError) as refused:
        get_action_function(old)
    assert f"Suggestion: use {NEW_ACTIONS[old]}." in str(refused.value)


def test_the_registry_refuses_a_name_with_no_replacement_without_inventing_one():
    with pytest.raises(ValueError) as refused:
        get_action_function("sink_parquet")
    assert "Suggestion" not in str(refused.value) and "engine function" in str(refused.value)


def test_a_name_that_never_existed_is_refused_as_before():
    with pytest.raises(ValueError, match="is not registered"):
        get_action_function("no_such_action_at_all")


def test_the_assembler_says_the_new_action_in_the_refusal():
    import polars as pl
    assembler = DataAssembler({"A": pl.LazyFrame({"k": [1]})}, recipe_id="r", join_id="j")
    with pytest.raises(TransformationError) as refused:
        assembler.assemble([{"action": "mutate", "column": "z", "expression": "pl.col('k')"}])
    assert "Suggestion: use polars_with_columns." in refused.value.tip


def test_the_wrangler_says_the_new_action_in_the_refusal():
    import polars as pl
    with pytest.raises(TransformationError) as refused:
        DataWrangler().run(pl.LazyFrame({"k": [1]}), [{"action": "keep_columns", "columns": ["k"]}])
    assert "Suggestion: use polars_select." in refused.value.tip
