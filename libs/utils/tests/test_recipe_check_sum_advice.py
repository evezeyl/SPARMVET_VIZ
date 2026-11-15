"""ST15 (advice, never blocks): a sum on a column declared Int32 or UInt32 (D43, PROVISIONAL, Eve 2026-11-15).

A sum of a 32-bit whole-number column wraps around above about 2 thousand million (4 for UInt32) with no error; the
checker says so where it KNOWS the declared type: a step of the schema's own wrangling (polars_sum, polars_cum_sum, a `.sum()` of
`pl.col('x')` in the aggregations of polars_group_by) on a column of that schema's input_fields, as long as no earlier step
could have changed the column. It cannot see a sum inside another formula (with_columns, mutate), nor a type that a step
earlier made 32-bit, nor a join result. A polars_cast to Int64 before the sum silences it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_sum_advice.py -q
"""
import copy

import pytest

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

CATALOG = {**CATALOGS, "actions": {**CATALOGS["actions"], **{n: {"context": ["t1", "t2"], "params": {}} for n in
           ("polars_sum", "polars_cum_sum", "polars_group_by", "polars_cast", "polars_select")}}}


def recipe(steps, kind="Int32"):
    raw = copy.deepcopy(valid())
    raw["data_schemas"]["A"]["input_fields"]["n"] = {"type": kind}
    raw["data_schemas"]["A"]["wrangling"] = {"tier1": steps}
    return raw


def advice(steps, kind="Int32"):
    return [p for p in check_recipe(recipe(steps, kind), "run", catalogs=CATALOG).advices if p.code == "ST15"]


@pytest.mark.parametrize("kind", ["Int32", "UInt32"])
@pytest.mark.parametrize("step", [
    {"action": "polars_sum"},
    {"action": "polars_cum_sum", "columns": ["n"]},
    {"action": "polars_group_by", "by": ["id"], "named_aggs": {"total": "pl.col('n').sum()"}},
], ids=["sum", "cum_sum", "group_by"])
def test_a_sum_on_a_32_bit_column_gets_the_advice(step, kind):
    found = advice([step], kind)
    assert len(found) == 1 and found[0].severity == "A"
    assert "wraps around" in found[0].message and "'n'" in found[0].message and "Int64" in found[0].fix


@pytest.mark.parametrize("kind", ["Int64", "Float64", "Int16", "UInt64"])
def test_a_wider_or_other_type_gets_none(kind):
    assert advice([{"action": "polars_sum"}], kind) == []


def test_a_cast_to_int64_before_the_sum_silences_it_and_a_cast_to_int32_brings_it_back():
    assert advice([{"action": "polars_cast", "columns": ["n"], "dtype": "Int64"}, {"action": "polars_sum"}]) == []
    assert len(advice([{"action": "polars_cast", "columns": ["n"], "dtype": "Int32"}, {"action": "polars_sum"}], "Int64")) == 1


def test_a_step_that_may_change_the_columns_stops_the_check_and_the_sum_of_another_column_gets_none():
    assert advice([{"action": "polars_select"}, {"action": "polars_sum"}]) == []
    assert advice([{"action": "polars_cum_sum", "columns": ["v"]}]) == []


def test_it_never_blocks():
    result = check_recipe(recipe([{"action": "polars_sum"}]), "run", catalogs=CATALOG)
    assert "ST15" not in [p.code for p in result.errors]


def test_it_is_shown_to_the_author():
    from app.modules.data_analysis_recipe_validator import SHOWN_ADVICES
    assert "ST15" in SHOWN_ADVICES
