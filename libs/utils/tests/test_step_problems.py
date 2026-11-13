"""The one rule set that judges a step against its action's schema (spec checks ST03, ST04, ST07, ST09, ST10, ST11).

The checker and the engine both call `utils.ui_schema.step_problems`, so a recipe cannot pass one and fail the other.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_step_problems.py -q
"""
import pytest

from utils.ui_schema import StepProblem, schema_declaration_problems, step_problems

SCHEMA = {
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "required": True},
        "value": {"widget": "number", "required": True},
        "how": {"widget": "enum", "options": ["left", "inner"], "required": True},
        "keep": {"widget": "bool", "required": False},
        "note": {"widget": "string", "required": False},
        "mapping": {"widget": "mapping", "required": False},
        "values": {"widget": "list", "required": False},
    }
}


def codes(problems):
    return [p.code for p in problems]


def good(**over):
    step = {"action": "x", "columns": ["a"], "value": 1, "how": "left"}
    step.update(over)
    return step


def test_a_correct_step_has_no_problem():
    assert step_problems("x", good(), SCHEMA) == []


def test_action_id_and_comment_are_not_parameters():
    assert step_problems("x", good(id="audit_1234abcd_1", comment="why"), SCHEMA) == []


def test_unknown_parameter_is_st03_with_a_did_you_mean():
    problems = step_problems("x", good(valeu=3), SCHEMA)
    assert codes(problems) == ["ST03"]
    assert problems[0].param == "valeu"
    assert "value" in problems[0].fix


def test_an_old_spelling_of_columns_names_columns():
    step = good()
    del step["columns"]
    step["column"] = "a"
    problems = step_problems("x", step, SCHEMA)
    assert set(codes(problems)) == {"ST03", "ST04"}
    st03 = next(p for p in problems if p.code == "ST03")
    assert "columns" in st03.fix


def test_a_missing_required_parameter_is_st04_and_names_it():
    step = good()
    del step["how"]
    problems = step_problems("x", step, SCHEMA)
    assert codes(problems) == ["ST04"]
    assert problems[0].param == "how"


def test_a_required_parameter_set_to_null_counts_as_missing():
    assert codes(step_problems("x", good(how=None), SCHEMA)) == ["ST04"]


def test_a_reserved_engine_key_is_st09():
    problems = step_problems("x", good(__right_df__="boom", __metadata__={}), SCHEMA)
    assert codes(problems) == ["ST09", "ST09"]


def test_a_multi_selector_given_a_single_value_is_st07():
    problems = step_problems("x", good(columns="a"), SCHEMA)
    assert codes(problems) == ["ST07"]
    assert "[a]" in problems[0].fix


@pytest.mark.parametrize("param, bad, good_value", [
    ("mapping", ["a", "b"], {"a": "b"}),
    ("values", "a", ["a"]),
    ("note", ["a"], "a"),
    ("value", "ten", 10),
    ("keep", "yes", True),
])
def test_a_wrong_shape_or_type_is_st10(param, bad, good_value):
    assert codes(step_problems("x", good(**{param: bad}), SCHEMA)) == ["ST10"]
    assert step_problems("x", good(**{param: good_value}), SCHEMA) == []


def test_a_number_is_not_a_boolean():
    assert codes(step_problems("x", good(value=True), SCHEMA)) == ["ST10"]


def test_an_enum_value_outside_its_options_is_st10_and_lists_the_options():
    problems = step_problems("x", good(how="outer"), SCHEMA)
    assert codes(problems) == ["ST10"]
    assert "left" in problems[0].fix and "inner" in problems[0].fix


def test_extra_names_are_allowed_when_the_schema_says_so():
    schema = dict(SCHEMA, allowed_extra_names=["alpha"])
    assert step_problems("x", good(alpha=1), schema) == []
    assert codes(step_problems("x", good(beta=1), schema)) == ["ST03"]


def test_a_schema_is_required():
    with pytest.raises(ValueError):
        step_problems("x", good(), None)


# ---- conditional rules (ST11) ------------------------------------------------------------------------------

FILTER = {
    "params": {
        "column": {"widget": "column_selector", "required": True},
        "op": {"widget": "enum", "options": ["eq", "in", "between"], "required": True},
        "value": {"widget": "list", "required": False},
        "closed": {"widget": "enum", "options": ["both", "none"], "required": False},
    },
    "rules": [
        {"when": {"op": "eq"}, "require": ["value"]},
        {"when": {"op": ["in", "between"]}, "require": ["value"], "shape": {"value": "list"}},
        {"when": {"op": "between"}, "shape": {"value": "pair"}},
        {"when": {"op": ["eq", "in"]}, "forbid": ["closed"]},
    ],
}


def test_a_when_rule_that_does_not_apply_is_silent():
    assert step_problems("f", {"action": "f", "column": "c", "op": "eq", "value": ["x"]}, FILTER) == []


def test_a_when_rule_can_require_a_parameter():
    problems = step_problems("f", {"action": "f", "column": "c", "op": "in"}, FILTER)
    assert codes(problems) == ["ST11"]
    assert problems[0].param == "value"


def test_a_when_rule_can_forbid_a_parameter():
    problems = step_problems("f", {"action": "f", "column": "c", "op": "in", "value": ["a"], "closed": "both"}, FILTER)
    assert codes(problems) == ["ST11"]
    assert problems[0].param == "closed"


def test_the_shape_of_a_value_can_depend_on_another_parameter():
    ok = {"action": "f", "column": "c", "op": "between", "value": [1, 5]}
    assert step_problems("f", ok, FILTER) == []
    problems = step_problems("f", dict(ok, value=[1, 2, 3]), FILTER)
    assert codes(problems) == ["ST11"]
    assert "[low, high]" in problems[0].fix


FILL = {
    "params": {
        "value": {"widget": "string", "required": False},
        "strategy": {"widget": "enum", "options": ["forward", "backward"], "required": False},
        "limit": {"widget": "number", "required": False},
        "column": {"widget": "column_selector", "required": False},
    },
    "rules": [{"one_of": ["value", "strategy"]}, {"exclusive": ["limit", "column"]}],
}


def test_one_of_wants_exactly_one():
    assert step_problems("f", {"action": "f", "value": "0"}, FILL) == []
    assert step_problems("f", {"action": "f", "strategy": "forward"}, FILL) == []
    assert codes(step_problems("f", {"action": "f"}, FILL)) == ["ST11"]
    assert codes(step_problems("f", {"action": "f", "value": "0", "strategy": "forward"}, FILL)) == ["ST11"]


def test_exclusive_allows_at_most_one():
    assert step_problems("f", {"action": "f", "value": "0", "limit": 2}, FILL) == []
    assert codes(step_problems("f", {"action": "f", "value": "0", "limit": 2, "column": "a"}, FILL)) == ["ST11"]


def test_a_problem_reads_as_where_what_and_the_fix():
    problem = step_problems("x", good(how="outer"), SCHEMA)[0]
    assert isinstance(problem, StepProblem)
    text = problem.text()
    assert "how" in text and "Fix:" in text


# ---- the registry can check its own declarations ------------------------------------------------------------

def test_a_rule_naming_an_undeclared_parameter_is_a_declaration_problem():
    schema = {"params": {"a": {"widget": "string", "required": False}}, "rules": [{"one_of": ["a", "ghost"]}]}
    assert any("ghost" in p for p in schema_declaration_problems(schema))


def test_an_unknown_rule_form_is_a_declaration_problem():
    schema = {"params": {"a": {"widget": "string", "required": False}}, "rules": [{"sometimes": ["a"]}]}
    assert schema_declaration_problems(schema)


def test_a_sound_schema_has_no_declaration_problem():
    assert schema_declaration_problems(FILTER) == []
    assert schema_declaration_problems(FILL) == []


# -- the widget `any`: a value whose form the schema rules decide (added with modif_filter, 2026-11-13) -------

ANY_SCHEMA = {"params": {"op": {"widget": "enum", "options": ["eq", "in"], "required": True}, "value": {"widget": "any", "required": True}},
              "rules": [{"when": {"op": "in"}, "shape": {"value": "list"}}, {"when": {"op": "eq"}, "shape": {"value": "scalar"}}]}


def test_an_any_widget_takes_a_scalar_or_a_list_and_the_rules_decide():
    from utils.ui_schema import step_problems
    assert step_problems("x", {"op": "eq", "value": 3}, ANY_SCHEMA) == []
    assert step_problems("x", {"op": "in", "value": [1, 2]}, ANY_SCHEMA) == []
    assert step_problems("x", {"op": "in", "value": 1}, ANY_SCHEMA), "a list is needed for in"
    assert step_problems("x", {"op": "eq", "value": [1]}, ANY_SCHEMA), "a single value is needed for eq"


def test_any_is_a_known_widget_with_its_own_shape():
    from utils.ui_schema import WIDGETS, expected_shape
    assert "any" in WIDGETS and expected_shape({"widget": "any"}) == "any"
