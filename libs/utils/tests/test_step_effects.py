"""The closed list of what the walk may read from a step (D-0351, LBFB step 0c, limited): exactly four readings, each checked against the plan."""
import inspect

import pytest

from utils import action_names, join_keys, step_effects as fx
from utils.plan_book import Plan

BEFORE = Plan.of([("sample_id", "String"), ("country", "String"), ("val", "Float64")])
RIGHT = Plan.of([("isolate", "String"), ("val", "Float64"), ("lab", "String")])


def test_the_list_holds_exactly_the_decided_readings():
    # a mutant that adds a reading (unpivot, fill_null, ...) fails here: reading more than the owner decided is a decision.
    # D-0351: rename mapping, join keys and suffix, drop columns, select columns. 2026-11-20: the NAMES a compute step, a group-by and a cast write.
    assert set(fx.READINGS) == {action_names.RENAME, action_names.JOIN, action_names.DROP, action_names.SELECT,
                                action_names.WITH_COLUMNS, action_names.CAST, action_names.GROUP_BY}
    assert fx.READINGS[action_names.RENAME] == ("mapping",) and fx.READINGS[action_names.DROP] == ("columns",)
    assert fx.READINGS[action_names.SELECT] == ("exprs",) and "suffix" in fx.READINGS[action_names.JOIN]
    assert fx.READINGS[action_names.WITH_COLUMNS] == ("named_exprs",) and fx.READINGS[action_names.CAST] == ("columns",)      # names only, never the formula or the type


def test_row_steps_are_imported_not_copied():
    assert "ROW_STEPS" in inspect.getsource(fx) and "join_keys.ROW_STEPS" in inspect.getsource(fx)
    for action in join_keys.ROW_STEPS:
        assert fx.effect_of({"action": action}).kind == fx.KEEPS


@pytest.mark.parametrize("step", [
    {"action": "polars_unpivot"}, {"action": "polars_fill_null", "columns": ["a"], "value": 0}, {"action": action_names.JOIN_ASOF, "right_ingredient": "B", "on": "a"},
    {"action": action_names.JOIN, "right_ingredient": "B", "on": "a", "how": "full"}, {"action": action_names.JOIN, "right_ingredient": "B", "on": "a", "how": "anti"},
    {"action": action_names.SELECT, "exprs": ["pl.col('a')"]}, {"action": action_names.SELECT, "exprs": ["*"]}, {"action": action_names.DROP, "columns": "a"},
    {"action": action_names.RENAME, "mapping": ["a"]}, {"action": action_names.JOIN, "right_ingredient": "B", "how": "left"},
    {"action": action_names.WITH_COLUMNS, "named_exprs": ["x"]}, {"action": action_names.CAST, "columns": ["pl.col('a')"], "dtype": "String"},
    {"action": action_names.GROUP_BY, "named_by": {"x": "pl.col('a')"}}, {"action": action_names.GROUP_BY, "by": ["a b"]}, {}, "not a step",
])
def test_everything_else_is_unread_with_a_reason(step):
    effect = fx.effect_of(step)
    assert effect.kind == fx.UNREAD and effect.why


def test_the_names_a_compute_step_a_cast_and_a_group_by_write_are_read_never_the_formula():
    compute = fx.effect_of({"action": action_names.WITH_COLUMNS, "named_exprs": {"era": "pl.col('year') > 2022", "val": "pl.col('val') * 2"}})
    assert (compute.kind, compute.written) == (fx.WRITES, ("era", "val"))
    assert fx.effect_of({"action": action_names.CAST, "columns": ["year"], "dtype": "String"}).columns == ("year",)
    group = fx.effect_of({"action": action_names.GROUP_BY, "by": ["sample_id"], "named_aggs": {"n": "pl.col('x').count()"}})
    assert (group.kind, group.columns, group.written) == (fx.GROUP, ("sample_id",), ("n",))


def test_a_compute_step_leaves_the_other_columns_untouched_and_the_plan_agrees():
    effect = fx.effect_of({"action": action_names.WITH_COLUMNS, "named_exprs": {"val": "x", "era": "y"}})
    predicted = fx.predict(effect, BEFORE, None)
    assert [(p.name, p.change, len(p.sources)) for p in predicted] == [("sample_id", None, 1), ("country", None, 1), ("val", fx.CHANGE_RECOMPUTE, 1), ("era", None, 0)]
    after = Plan.of([("sample_id", "String"), ("country", "String"), ("val", "Int64"), ("era", "Boolean")])        # a written column may have another type: the plan decides
    assert fx.agreement_problem(effect, predicted, BEFORE, None, after) is None
    changed = Plan.of([("sample_id", "Int64"), ("country", "String"), ("val", "Float64"), ("era", "Boolean")])      # but a column the step does not name may not
    assert "sample_id" in fx.agreement_problem(effect, predicted, BEFORE, None, changed)
    lost = Plan.of([("sample_id", "String"), ("val", "Float64"), ("era", "Boolean")])
    assert "country" in fx.agreement_problem(effect, predicted, BEFORE, None, lost)


def test_a_group_by_keeps_its_group_columns_aggregates_by_name_and_loses_the_rest():
    effect = fx.effect_of({"action": action_names.GROUP_BY, "by": ["country"], "named_aggs": {"val": "m", "n": "c"}})
    predicted = fx.predict(effect, BEFORE, None)
    assert [(p.name, p.change, len(p.sources)) for p in predicted] == [("country", fx.CHANGE_GROUP_KEY, 1), ("val", fx.CHANGE_AGGREGATE, 1), ("n", None, 0)]
    assert fx.agreement_problem(effect, predicted, BEFORE, None, Plan.of([("country", "String"), ("val", "Float64"), ("n", "UInt32")])) is None
    assert fx.agreement_problem(effect, predicted, BEFORE, None, Plan.of([("country", "String"), ("val", "Float64")])) is not None
    missing = fx.effect_of({"action": action_names.GROUP_BY, "by": ["nope"], "named_aggs": {}})
    assert "nope" in fx.agreement_problem(missing, fx.predict(missing, BEFORE, None), BEFORE, None, Plan.of([]))


def test_a_cast_changes_the_type_of_the_columns_it_names_only():
    effect = fx.effect_of({"action": action_names.CAST, "columns": ["val"], "dtype": "String"})
    predicted = fx.predict(effect, BEFORE, None)
    assert [p.change for p in predicted] == [None, None, fx.CHANGE_CAST]
    assert fx.agreement_problem(effect, predicted, BEFORE, None, Plan.of([("sample_id", "String"), ("country", "String"), ("val", "String")])) is None
    assert "country" in fx.agreement_problem(effect, predicted, BEFORE, None, Plan.of([("sample_id", "String"), ("country", "Int64"), ("val", "String")]))


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
