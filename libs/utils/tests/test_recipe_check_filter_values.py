"""Check ST12: a `modif_filter` value does not have the type its column is declared with (ADR-104 point 7, Eve 2026-11-14).

The engine stays strict (a value of another type stops the step with a plain error); the checker says so before the run,
where the declarations tell the type of the column. It stays silent when they cannot: a step before the filter may create,
rename or cast the column.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_filter_values.py -q
"""
import pytest

from test_recipe_check import check, valid


def filter_step(column, op, value, **extra):
    return {"action": "modif_filter", "column": column, "op": op, "value": value, "na": "remove", **extra}


def st12(raw):
    return [p for p in check(raw).problems if p.code == "ST12"]


def with_schema_step(step, column_type="Int64"):
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["n"] = {"type": column_type}
    raw["data_schemas"]["A"]["wrangling"]["tier1"] = [step]
    return raw


@pytest.mark.parametrize("op, value", [("gt", "5"), ("eq", "5"), ("in", ["1", "2"]), ("not_in", [1, "2"]), ("between", ["1", 5])])
def test_text_on_a_number_column_is_refused_in_a_schema(op, value):
    problems = st12(with_schema_step(filter_step("n", op, value)))
    assert len(problems) == 1
    p = problems[0]
    assert p.severity == "E" and p.path == "data_schemas.A.wrangling.tier1[1].value"
    assert "'n'" in p.message and "whole numbers" in p.message and "Int64" in p.message and "text" in p.message
    assert p.fix


@pytest.mark.parametrize("op, value", [("gt", 5), ("in", [1, 2]), ("between", [1, 5]), ("gt", 5.5)])
def test_a_number_on_a_number_column_is_accepted(op, value):
    assert st12(with_schema_step(filter_step("n", op, value))) == []


def test_a_number_on_a_text_column_is_refused():
    raw = valid()
    raw["data_schemas"]["A"]["wrangling"]["tier1"] = [filter_step("id", "eq", 5)]
    p = st12(raw)
    assert len(p) == 1 and "text" in p[0].message and "'id'" in p[0].message


def test_text_on_a_true_false_column_is_refused():
    p = st12(with_schema_step(filter_step("n", "eq", "true"), column_type="Boolean"))
    assert len(p) == 1 and "true or false" in p[0].message


@pytest.mark.parametrize("column_type, op, value, holds", [
    ("Date", "eq", "2020-01-01", "dates"), ("Date", "eq", 5, "dates"), ("Date", "in", ["2020-01-01"], "dates"),
    ("Date", "between", ["2020-01-01", "2020-01-03"], "dates"),
    ("Datetime", "eq", "2020-01-01 10:00:00", "dates and times"), ("Datetime", "in", [5], "dates and times"),
    ("Categorical", "eq", 5, "categories"), ("Boolean", "eq", "true", "true or false"),
])
def test_the_checker_judges_dates_datetimes_and_categories_with_the_rule_of_the_engine(column_type, op, value, holds):
    p = st12(with_schema_step(filter_step("n", op, value, **({"closed": "both"} if op == "between" else {})), column_type=column_type))
    assert len(p) == 1 and holds in p[0].message and p[0].fix


def test_a_date_written_as_a_date_is_accepted():
    import datetime
    assert st12(with_schema_step(filter_step("n", "eq", datetime.date(2020, 1, 1)), column_type="Date")) == []
    assert st12(with_schema_step(filter_step("n", "in", [datetime.datetime(2020, 1, 1, 10)]), column_type="Datetime")) == []
    assert st12(with_schema_step(filter_step("n", "eq", "x"), column_type="Categorical")) == []


def test_the_checker_and_the_engine_share_one_rule():
    """The checker calls `utils.filter_values.check_filter_value`; the engine's strict mode calls the same function."""
    import inspect
    import utils.recipe_check as recipe_check
    assert "check_filter_value" in inspect.getsource(recipe_check) and recipe_check.check_filter_value.__module__ == "utils.filter_values"


def test_tier2_of_a_schema_is_checked_when_tier1_keeps_the_columns():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["n"] = {"type": "Int64"}
    raw["data_schemas"]["A"]["wrangling"] = {"tier1": [filter_step("n", "gt", 1)], "tier2": [filter_step("n", "gt", "2")]}
    p = st12(raw)
    assert len(p) == 1 and p[0].path == "data_schemas.A.wrangling.tier2[1].value"


def test_silent_when_a_step_before_may_change_the_column():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["n"] = {"type": "String"}
    raw["data_schemas"]["A"]["wrangling"]["tier1"] = [{"action": "polars_cast"}, filter_step("n", "gt", "5")]
    assert st12(raw) == []


def test_silent_when_the_column_is_not_declared():
    assert st12(with_schema_step(filter_step("created_later", "gt", "5"))) == []


def test_silent_when_input_fields_is_empty_the_file_decides():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"] = {}
    raw["data_schemas"]["A"]["wrangling"]["tier1"] = [filter_step("n", "gt", "5")]
    assert st12(raw) == []


def test_a_filter_after_other_row_filters_is_still_checked():
    raw = valid()
    raw["data_schemas"]["A"]["input_fields"]["n"] = {"type": "Int64"}
    raw["data_schemas"]["A"]["wrangling"]["tier1"] = [filter_step("n", "gt", 1), filter_step("n", "lt", "9")]
    p = st12(raw)
    assert len(p) == 1 and p[0].path.endswith("tier1[2].value")


def test_a_join_step_filter_reads_the_declared_type_of_the_left_table_and_of_a_joined_table():
    raw = valid()
    raw["joins"]["AB"]["steps"]["tier1"].append(filter_step("w", "gt", "3"))     # w is Int64 in B, joined before
    raw["joins"]["AB"]["steps"]["tier1"].append(filter_step("v", "gt", "3"))     # v is Float64 in A
    problems = st12(raw)
    assert [p.path for p in problems] == ["joins.AB.steps.tier1[2].value", "joins.AB.steps.tier1[3].value"]
    assert "whole numbers" in problems[0].message and "decimal numbers" in problems[1].message


def test_a_join_tier2_filter_is_checked():
    raw = valid()
    raw["joins"]["AB"]["steps"]["tier2"] = [filter_step("w", "gt", "3")]
    assert [p.path for p in st12(raw)] == ["joins.AB.steps.tier2[1].value"]


def test_silent_in_a_join_when_a_step_may_change_the_table():
    raw = valid()
    raw["joins"]["AB"]["steps"]["tier1"] = [{"action": "polars_cast"}] + raw["joins"]["AB"]["steps"]["tier1"] + [filter_step("w", "gt", "3")]
    assert st12(raw) == []


def test_other_actions_are_not_judged():
    raw = with_schema_step({"action": "polars_filter_demo", "column": "n", "value": "5"})
    assert st12(raw) == []
