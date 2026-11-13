"""The widget vocabulary of the registries and the value shape each widget stands for (spec section 8).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_ui_schema.py -q
"""
import pytest

from utils.ui_schema import WIDGETS, expected_shape, shape_problem


def test_the_vocabulary_has_the_widgets_of_the_form_renderer_and_the_two_structured_ones():
    assert {"column_selector", "expression", "enum", "dtype_picker", "number", "string", "color",
            "column_or_literal", "bool"} <= set(WIDGETS)
    assert {"list", "mapping"} <= set(WIDGETS)


@pytest.mark.parametrize("param_def, shape", [
    ({"widget": "string"}, "scalar"),
    ({"widget": "number"}, "scalar"),
    ({"widget": "column_selector", "multi": False}, "scalar"),
    ({"widget": "column_selector", "multi": True}, "list"),
    ({"widget": "enum", "multi": True}, "list"),
    ({"widget": "enum"}, "scalar"),
    ({"widget": "list"}, "list"),
    ({"widget": "list", "items": "mapping"}, "list_of_mapping"),
    ({"widget": "mapping"}, "mapping"),
])
def test_expected_shape(param_def, shape):
    assert expected_shape(param_def) == shape


def test_a_list_widget_wants_a_list():
    assert shape_problem({"widget": "list"}, ["a", "b"]) is None
    assert "list" in shape_problem({"widget": "list"}, "a")
    assert "list" in shape_problem({"widget": "list"}, {"a": "b"})


def test_a_mapping_widget_wants_a_mapping():
    assert shape_problem({"widget": "mapping"}, {"old": "new"}) is None
    assert "mapping" in shape_problem({"widget": "mapping"}, ["old", "new"])
    assert "mapping" in shape_problem({"widget": "mapping"}, "old: new")


def test_a_list_of_mappings_wants_mappings_as_items():
    param = {"widget": "list", "items": "mapping"}
    assert shape_problem(param, [{"matches": "S", "value": 0}, {"default": 1}]) is None
    assert "mapping" in shape_problem(param, ["S", "R"])
    assert "list" in shape_problem(param, {"matches": "S"})


def test_a_scalar_widget_has_no_shape_problem_here():
    """Scalar and column-selector shapes are the checker's (ST07, ST10); this helper only covers the structured widgets."""
    assert shape_problem({"widget": "string"}, "anything") is None
