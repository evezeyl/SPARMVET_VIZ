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
    ("Datetime", "eq", "01/01/2020", "dates and times"), ("Datetime", "in", [5], "dates and times"),
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


import datetime as _dt

import polars as pl

from utils.filter_values import FilterValueError, check_filter, filter_condition

RULE_CASES = [
    ("gt", 5, pl.Int64), ("gt", "5", pl.Int64), ("in", [1, 2.5], pl.Float64), ("in", ["x", 1], pl.String), ("eq", True, pl.Boolean),
    ("gt", True, pl.Boolean), ("between", [False, True], pl.Boolean), ("between", ["a", "b"], pl.String),
    ("eq", 5, pl.Date), ("eq", _dt.date(2020, 1, 1), pl.Date), ("between", [_dt.date(2020, 1, 1), _dt.date(2020, 1, 2)], pl.Date),
    ("eq", "2020-01-01 10:00:00.000000007", pl.Datetime("ns")), ("eq", "01/01/2020", pl.Datetime("ns")), ("in", [1], pl.Categorical),
    ("in", ["x"], pl.Categorical), ("eq", "10:30:00", pl.Time), ("in", ["5"], pl.Duration),
]


@pytest.mark.parametrize("op, value, dtype", RULE_CASES)
def test_the_checker_and_the_engine_give_the_same_verdict_with_the_same_words(op, value, dtype):
    """One rule set: `check_filter` (checker) and `filter_condition(strict=True)` (the recipe action) refuse the same filters, in the same words."""
    def verdict(call):
        try:
            call()
        except FilterValueError as exc:
            return str(exc)
        return None
    checked = verdict(lambda: check_filter(op, value, dtype))
    built = verdict(lambda: filter_condition("c", op, value, dtype, strict=True))
    assert checked == built


@pytest.mark.parametrize("column_type, op, value, holds", [
    ("Boolean", "gt", True, "true or false"), ("Boolean", "between", [False, True], "true or false"),
    ("String", "between", ["a", "b"], "text"), ("Categorical", "in", [1, 2], "categories"),
    ("Time", "eq", "10:30:00", "not offered"), ("Duration", "in", ["5"], "not offered"),
])
def test_the_checker_refuses_an_operator_that_does_not_fit_the_type_like_the_engine(column_type, op, value, holds):
    p = st12(with_schema_step(filter_step("n", op, value, **({"closed": "both"} if op == "between" else {})), column_type=column_type))
    assert len(p) == 1 and holds in p[0].message and p[0].fix


def test_an_exact_datetime_text_is_accepted_by_the_checker():
    assert st12(with_schema_step(filter_step("n", "eq", "2020-01-01 10:00:00.000000007"), column_type="Datetime")) == []
