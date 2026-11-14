"""The recipe checker and the as-of join: the key checks of a join apply to its key, and the `by` columns are not a clash.

J09, J10, J11 (key types, key columns, key lists) read `on`, or `left_on` with `right_on`, of any step that has a
`right_ingredient`; the as-of key is written the same way, so the checks hold for it. J08 (a column in both tables that
is not a key is renamed by Polars) must not fire for the `by` columns of an as-of join, which Polars merges.
`polars_join_asof` is allowed in tier 1 only (ST05), like `polars_join`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_time_joins.py -q
"""
import copy

from utils.recipe_check import check_recipe
from test_recipe_check import CATALOGS, valid

ASOF = {
    "context": ["assembly"],
    "params": {**{name: {"widget": "string", "required": name in ("right_ingredient", "strategy")}
                  for name in ("right_ingredient", "strategy", "on", "left_on", "right_on")},
               **{name: {"widget": "column_selector", "multi": True, "required": False} for name in ("by", "by_left", "by_right")}},
}
CATALOG = {**CATALOGS, "actions": {**CATALOGS["actions"], "polars_join_asof": ASOF}}


def asof_recipe():
    raw = copy.deepcopy(valid())
    raw["data_schemas"]["A"]["input_fields"] = {"id": {"type": "String"}, "t": {"type": "Int64"}, "site": {"type": "String"}}
    raw["data_schemas"]["B"]["input_fields"] = {"t": {"type": "Int64"}, "site": {"type": "String"}, "w": {"type": "Int64"}}
    raw["joins"]["AB"]["steps"]["tier1"] = [{"action": "polars_join_asof", "right_ingredient": "B", "on": "t", "by": ["site"], "strategy": "backward"}]
    raw["analysis_groups"]["g"]["plots"]["p"]["spec"]["mapping"] = {"x": "id", "y": "t"}
    return raw


class Graph:
    """The columns of each ingredient, as the recipe graph gives them (J08 needs them)."""

    def columns_of(self, dataset_id):
        return {"A": ["id", "t", "site"], "B": ["t", "site", "w"]}.get(dataset_id)


def codes(raw):
    return [p.code for p in check_recipe(raw, "run", catalogs=CATALOG, graph=Graph()).problems]


def test_a_correct_asof_recipe_has_no_problem_and_the_by_column_is_not_a_clash():
    assert codes(asof_recipe()) == []


def test_without_the_by_columns_in_the_key_set_the_same_recipe_would_report_a_clash():
    """The check can fail: the column `site` is in both tables, and only the `by` keeps it from being reported."""
    raw = asof_recipe()
    raw["joins"]["AB"]["steps"]["tier1"][0].pop("by")
    assert "J08" in codes(raw)


def test_an_asof_key_of_two_declared_types_is_refused():
    raw = asof_recipe()
    raw["data_schemas"]["B"]["input_fields"]["t"]["type"] = "Float64"
    assert "J09" in codes(raw) and "J10" not in codes(raw)  # (a Float64 key also gets the advice J13)


def test_an_asof_key_that_is_not_declared_is_refused():
    raw = asof_recipe()
    del raw["data_schemas"]["B"]["input_fields"]["t"]
    assert "J10" in codes(raw)


def test_an_asof_step_in_tier_2_of_the_join_is_refused():
    raw = asof_recipe()
    step = raw["joins"]["AB"]["steps"]["tier1"][0]
    raw["joins"]["AB"]["steps"]["tier2"] = [dict(step)]
    assert "ST05" in codes(raw)
