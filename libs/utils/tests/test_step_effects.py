"""The closed list of what the walk may read from a step (D-0351, LBFB step 0c, limited): exactly four readings, each checked against the plan."""
import inspect

import pytest

from utils import action_names, join_keys, step_effects as fx
from utils.plan_book import Plan

BEFORE = Plan.of([("sample_id", "String"), ("country", "String"), ("val", "Float64")])
RIGHT = Plan.of([("isolate", "String"), ("val", "Float64"), ("lab", "String")])


def test_the_list_holds_exactly_the_four_readings_of_d_0351():
    # a mutant that adds a reading (with_columns, cast, group_by) fails here: reading more than the owner decided is a decision
    assert set(fx.READINGS) == {action_names.RENAME, action_names.JOIN, action_names.DROP, action_names.SELECT}
    assert fx.READINGS[action_names.RENAME] == ("mapping",) and fx.READINGS[action_names.DROP] == ("columns",)
    assert fx.READINGS[action_names.SELECT] == ("exprs",) and "suffix" in fx.READINGS[action_names.JOIN]


def test_row_steps_are_imported_not_copied():
    assert "ROW_STEPS" in inspect.getsource(fx) and "join_keys.ROW_STEPS" in inspect.getsource(fx)
    for action in join_keys.ROW_STEPS:
        assert fx.effect_of({"action": action}).kind == fx.KEEPS


@pytest.mark.parametrize("step", [
    {"action": action_names.WITH_COLUMNS, "named_exprs": {"x": "pl.col('a')"}}, {"action": action_names.CAST, "columns": ["a"], "dtype": "String"},
    {"action": action_names.GROUP_BY, "by": ["a"]}, {"action": "polars_unpivot"}, {"action": action_names.JOIN_ASOF, "right_ingredient": "B", "on": "a"},
    {"action": action_names.JOIN, "right_ingredient": "B", "on": "a", "how": "full"}, {"action": action_names.JOIN, "right_ingredient": "B", "on": "a", "how": "anti"},
    {"action": action_names.SELECT, "exprs": ["pl.col('a')"]}, {"action": action_names.SELECT, "exprs": ["*"]}, {"action": action_names.DROP, "columns": "a"},
    {"action": action_names.RENAME, "mapping": ["a"]}, {"action": action_names.JOIN, "right_ingredient": "B", "how": "left"}, {}, "not a step",
])
def test_everything_else_is_unread_with_a_reason(step):
    effect = fx.effect_of(step)
    assert effect.kind == fx.UNREAD and effect.why


def test_rename_drop_select_join_are_read():
    assert fx.effect_of({"action": action_names.RENAME, "mapping": {"a": "b"}}).pairs == (("a", "b"),)
    assert fx.effect_of({"action": action_names.DROP, "columns": ["a", "b"]}).columns == ("a", "b")
    assert fx.effect_of({"action": action_names.SELECT, "exprs": ["b", "a"]}).columns == ("b", "a")
    join = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "left_on": "sample_id", "right_on": "isolate", "suffix": "_b"})
    assert (join.kind, join.how, join.suffix, join.right, join.left_keys, join.right_keys) == (fx.JOIN, "left", "_b", "B", ("sample_id",), ("isolate",))
    assert fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "x"}).suffix == "_right"     # the default is written once, in join_keys


def test_suffix_default_is_one_place():
    assert join_keys.suffix_of({}) == "_right" and join_keys.suffix_of({"suffix": "_b"}) == "_b" and join_keys.suffix_of({"suffix": ""}) == "_right"


def test_a_rename_is_simultaneous_and_a_swap_agrees_with_an_equal_type_plan():
    effect = fx.effect_of({"action": action_names.RENAME, "mapping": {"country": "val", "val": "country"}})
    predicted = fx.predict(effect, Plan.of([("country", "Float64"), ("val", "Float64")]), None)
    assert [(p.name, p.sources[0].name) for p in predicted] == [("val", "country"), ("country", "val")]
    # with equal types the plan cannot tell a swap from nothing: it agrees; the walk must not follow it (every changed name is a change)
    assert fx.agreement_problem(effect, predicted, Plan.of([("country", "Float64"), ("val", "Float64")]), None, Plan.of([("country", "Float64"), ("val", "Float64")])) is None
    assert all(p.change == fx.CHANGE_RENAME for p in predicted)


def test_join_prediction_keys_suffix_and_disagreement():
    effect = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "left_on": "sample_id", "right_on": "isolate"})
    predicted = fx.predict(effect, BEFORE, RIGHT)
    assert [(p.name, p.change) for p in predicted] == [("sample_id", fx.CHANGE_KEY_OTHER_NAME), ("country", None), ("val", None), ("val_right", fx.CHANGE_SUFFIX), ("lab", None)]
    good = Plan.of([("sample_id", "String"), ("country", "String"), ("val", "Float64"), ("val_right", "Float64"), ("lab", "String")])
    assert fx.agreement_problem(effect, predicted, BEFORE, RIGHT, good) is None
    assert "val_right" in fx.agreement_problem(effect, predicted, BEFORE, RIGHT, Plan.of([("sample_id", "String"), ("country", "String"), ("val", "Float64"), ("lab", "String")]))
    wrong_type = Plan.of([("sample_id", "String"), ("country", "String"), ("val", "Float64"), ("val_right", "Int64"), ("lab", "String")])
    assert "val_right" in fx.agreement_problem(effect, predicted, BEFORE, RIGHT, wrong_type)
    missing = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "nope"})
    assert "nope" in fx.agreement_problem(missing, fx.predict(missing, BEFORE, RIGHT), BEFORE, RIGHT, good)


def test_unread_pairs_say_only_what_the_plan_shows():
    after = Plan.of([("sample_id", "String"), ("country", "Categorical"), ("era", "String")])
    assert fx.unread_pairs(BEFORE, after) == (("sample_id",), ("country",), ("val",), ("era",))
