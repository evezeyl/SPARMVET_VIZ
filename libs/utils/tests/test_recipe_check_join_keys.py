"""Checks J09, J10, J11: a join with keys of different declared types, an undeclared key or unequal key lists is refused at load.

The rule mirrors the build (DataAssembler._check_join_key_types, JOIN-KEY-TYPES-1). The checker stays silent when a step
before the join may change the type or the name of a key: the build check remains the judge there.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_join_keys.py -q
"""
import utils.recipe_check as recipe_check
from test_recipe_check import check, valid

KEY_CODES = {"J09", "J10", "J11"}


def codes(raw):
    return [p.code for p in check(raw).problems if p.code in KEY_CODES]


def join_step(raw):
    return raw["joins"]["AB"]["steps"]["tier1"][0]


def test_equal_types_are_accepted():
    assert check(valid()).problems == []


def test_different_types_with_on_are_refused_with_a_fix():
    raw = valid()
    raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Int64"
    problems = [p for p in check(raw).problems if p.code == "J09"]
    assert len(problems) == 1
    assert "String" in problems[0].message and "Int64" in problems[0].message and "'id'" in problems[0].message
    assert "input_fields of both tables" in problems[0].fix and "changes only the left table" in problems[0].fix
    assert problems[0].path == "joins.AB.steps.tier1[1]"


def test_different_types_with_left_on_and_right_on_are_refused():
    raw = valid()
    step = join_step(raw)
    step.pop("on")
    step.update(left_on="id", right_on="w")
    assert codes(raw) == ["J09"]


def test_left_on_and_right_on_of_equal_types_are_accepted():
    raw = valid()
    raw["data_schemas"]["B"]["input_fields"]["w"]["type"] = "String"
    step = join_step(raw)
    step.pop("on")
    step.update(left_on="id", right_on="w")
    assert codes(raw) == []


def test_several_keys_one_pair_differs():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["k2"] = {"type": "Int64"}
    raw["data_schemas"]["B"]["input_fields"]["k2"] = {"type": "Float64"}
    join_step(raw)["on"] = ["id", "k2"]
    problems = [p for p in check(raw).problems if p.code == "J09"]
    assert len(problems) == 1 and "'k2'" in problems[0].message


def test_parameters_of_the_dtype_count():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["id"] = {"type": "Enum", "categories": ["a"]}
    raw["data_schemas"]["B"]["input_fields"]["id"] = {"type": "Enum", "categories": ["a", "b"]}
    assert "J09" in codes(raw)


def test_a_key_missing_from_the_right_declaration_is_j10():
    raw = valid()
    del raw["data_schemas"]["B"]["input_fields"]["id"]
    problems = [p for p in check(raw).problems if p.code == "J10"]
    assert len(problems) == 1 and "'id'" in problems[0].message and "B" in problems[0].message and problems[0].fix


def test_a_key_missing_from_the_left_declaration_is_j10():
    raw = valid()
    join_step(raw).update(on="w")
    raw["data_schemas"]["A"]["input_fields"]["w"] = {"type": "Int64"}
    del raw["data_schemas"]["A"]["input_fields"]["w"]
    assert codes(raw) == ["J10"]


def test_a_left_key_brought_by_an_earlier_join_is_not_missing():
    raw = valid()
    raw["data_schemas"]["C"] = {**valid()["data_schemas"]["B"], "input_fields": {"id": {"type": "String"}, "c": {"type": "Int64"}}}
    raw["joins"]["AB"]["ingredients"].append({"dataset_id": "C"})
    raw["joins"]["AB"]["steps"]["tier1"].append({"action": "polars_join", "right_ingredient": "C", "on": "w", "how": "left"})
    raw["data_schemas"]["C"]["input_fields"]["w"] = {"type": "Int64"}
    assert codes(raw) == []
    raw["data_schemas"]["C"]["input_fields"]["w"] = {"type": "Float64"}
    assert codes(raw) == ["J09"]


def test_unequal_key_lists_are_j11():
    raw = valid()
    step = join_step(raw)
    step.pop("on")
    step.update(left_on=["id", "v"], right_on=["id"])
    problems = [p for p in check(raw).problems if p.code == "J11"]
    assert len(problems) == 1 and "2 column(s)" in problems[0].message and problems[0].fix
    assert [p.code for p in check(raw).problems if p.code in {"J09", "J10"}] == []


def test_a_step_before_the_join_in_the_schema_keeps_the_checker_silent():
    for action in ("polars_cast", "polars_rename", "polars_with_columns"):
        raw = valid()
        raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Int64"
        raw["data_schemas"]["A"]["wrangling"] = {"tier1": [{"action": action}]}
        assert "J09" not in [p.code for p in check(raw).problems], action
        raw = valid()
        raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Int64"
        raw["data_schemas"]["B"]["wrangling"] = {"tier1": [{"action": action}]}
        assert "J09" not in [p.code for p in check(raw).problems], action


def test_a_row_filter_in_the_schema_does_not_hide_a_difference():
    raw = valid()
    raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Int64"
    raw["data_schemas"]["B"]["wrangling"] = {"tier1": [{"action": "polars_filter_demo"}]}
    assert "J09" in codes(raw)


def test_a_step_before_the_join_in_the_join_keeps_the_checker_silent():
    raw = valid()
    raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Int64"
    raw["joins"]["AB"]["steps"]["tier1"].insert(0, {"action": "polars_with_columns", "exprs": {"id": "pl.col('id')"}})
    assert codes(raw) == []


def test_a_key_the_declaration_lacks_is_silent_when_a_step_may_create_it():
    raw = valid()
    del raw["data_schemas"]["B"]["input_fields"]["id"]
    raw["data_schemas"]["B"]["wrangling"] = {"tier1": [{"action": "polars_with_columns"}]}
    assert codes(raw) == []


def test_breaking_the_rule_makes_a_test_fail(monkeypatch):
    """The type rule is what reports the difference: with it disabled the first case of this file would pass wrongly."""
    raw = valid()
    raw["data_schemas"]["B"]["input_fields"]["id"]["type"] = "Int64"
    monkeypatch.setattr(recipe_check, "_declared_dtype", lambda field: None)
    assert "J09" not in codes(raw)
    monkeypatch.undo()
    assert "J09" in codes(raw)
