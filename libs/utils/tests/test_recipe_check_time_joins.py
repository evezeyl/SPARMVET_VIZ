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
WHERE = {
    "context": ["assembly"],
    "params": {"right_ingredient": {"widget": "string", "required": True},
               "predicates": {"widget": "list", "required": True}, "suffix": {"widget": "string", "required": False}},
}
CATALOG = {**CATALOGS, "actions": {**CATALOGS["actions"], "polars_join_asof": ASOF, "modif_join_where": WHERE}}


def asof_recipe():
    raw = copy.deepcopy(valid())
    for table in ("A", "B"):
        raw["data_schemas"][table].pop("completion")   # these tables declare no entity id below, so nothing is completed (E07 otherwise)
    raw["data_schemas"]["A"]["input_fields"] = {"id": {"type": "String"}, "t": {"type": "Int64"}, "site": {"type": "String"}}
    raw["data_schemas"]["B"]["input_fields"] = {"t": {"type": "Int64"}, "site": {"type": "String"}, "w": {"type": "Int64"}}
    raw["joins"]["AB"]["tier1"]["steps"] = [{"action": "polars_join_asof", "right_ingredient": "B", "on": "t", "by": ["site"], "strategy": "backward"}]
    raw["analysis_groups"]["g"]["plots"]["p"]["mapping"] = {"x": "id", "y": "t"}
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
    raw["joins"]["AB"]["tier1"]["steps"][0].pop("by")
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
    step = raw["joins"]["AB"]["tier1"]["steps"][0]
    raw["joins"]["AB"]["tier2"] = {"steps": [dict(step)]}
    assert "ST05" in codes(raw)


def where_recipe():
    raw = asof_recipe()
    raw["joins"]["AB"]["tier1"]["steps"] = [{"action": "modif_join_where", "right_ingredient": "B", "predicates": ["pl.col('w') > pl.col('t')"]}]
    return raw


def test_a_join_on_conditions_needs_no_key_and_is_not_reported_as_missing_one():
    """J05 asks for `on`, or `left_on` with `right_on`, of every step with a right_ingredient; a join on conditions has neither."""
    assert "J05" not in codes(where_recipe())


def test_a_join_on_conditions_still_needs_an_ingredient_of_the_join():
    raw = where_recipe()
    raw["joins"]["AB"]["tier1"]["steps"][0]["right_ingredient"] = "Ghost"
    assert "J05" in codes(raw)


def test_a_join_on_conditions_in_tier_2_of_the_join_is_refused():
    raw = where_recipe()
    raw["joins"]["AB"]["tier2"] = {"steps": [dict(raw["joins"]["AB"]["tier1"]["steps"][0])]}
    assert "ST05" in codes(raw)


def test_the_key_check_still_asks_a_plain_join_for_its_key():
    raw = asof_recipe()
    raw["joins"]["AB"]["tier1"]["steps"] = [{"action": "polars_join", "right_ingredient": "B", "how": "left"}]
    assert "J05" in codes(raw)


def test_the_old_name_polars_join_where_is_refused_and_the_message_names_the_new_one_and_why():
    """A removed name is refused with its replacement (no alias, it does not run): the action fixes the order, so it is not exactly Polars."""
    from utils.action_names import REMOVED_ACTIONS
    raw = where_recipe()
    raw["joins"]["AB"]["tier1"]["steps"][0]["action"] = "polars_join_where"
    result = check_recipe(raw, "run", catalogs={**CATALOG, "old_action_names": dict(REMOVED_ACTIONS)}, graph=Graph())
    problems = [p for p in result.problems if p.code == "ST02"]
    assert problems and problems[0].severity == "E"
    assert problems[0].fix == "Suggestion: use modif_join_where." and "not exactly Polars" in problems[0].message
