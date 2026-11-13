"""The Blueprint form shows a list or a mapping as one line of YAML text and reads it back as a list or a mapping.

Before this, `rename.mapping`, `recode_values.rules` and six more parameters were declared `string`: the form showed
the Python repr of the value and saved the typed text as a string.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_widget_text.py -q
"""
import pytest

from blueprint_arch.widget_text import text_to_value, value_to_text

LIST = {"widget": "list", "label": "Values"}
MAPPING = {"widget": "mapping", "label": "Mapping", "hint": "{old_name: new_name}"}
RULES = {"widget": "list", "items": "mapping", "label": "Rules"}


def test_a_list_is_shown_as_flow_yaml():
    assert value_to_text(LIST, ["Calf", "calf"]) == "[Calf, calf]"


def test_a_mapping_is_shown_as_flow_yaml_in_its_order():
    assert value_to_text(MAPPING, {"b_old": "b", "a_old": "a"}) == "{b_old: b, a_old: a}"


def test_a_list_of_mappings_is_shown_as_flow_yaml():
    text = value_to_text(RULES, [{"matches": "S", "value": 0}, {"default": 1}])
    assert text == "[{matches: S, value: 0}, {default: 1}]"


def test_nothing_is_shown_as_empty_text():
    assert value_to_text(LIST, None) == "" and value_to_text(MAPPING, {}) == "{}"


@pytest.mark.parametrize("param_def, value", [
    (LIST, ["Calf", "calf"]),
    (LIST, [1, 2, 3]),
    (MAPPING, {"old col": "new_col", "x": "y"}),
    (RULES, [{"matches": "S", "value": 0}, {"matches_any": ["R", "I"], "value": 1}, {"default": None}]),
])
def test_what_is_shown_reads_back_as_the_same_value(param_def, value):
    assert text_to_value(param_def, value_to_text(param_def, value)) == value


def test_blank_text_is_no_value():
    assert text_to_value(LIST, "   ") is None and text_to_value(MAPPING, "") is None


def test_a_scalar_where_a_list_belongs_says_what_to_write():
    with pytest.raises(ValueError) as err:
        text_to_value(LIST, "Calf")
    assert "list" in str(err.value) and "[" in str(err.value)


def test_a_list_where_a_mapping_belongs_says_what_to_write():
    with pytest.raises(ValueError) as err:
        text_to_value(MAPPING, "[a, b]")
    assert "mapping" in str(err.value) and "{old_name: new_name}" in str(err.value)


def test_invalid_yaml_is_an_error_with_the_expected_form():
    with pytest.raises(ValueError) as err:
        text_to_value(LIST, "[a, b")
    assert "YAML" in str(err.value)


def test_a_repeated_key_in_a_mapping_is_refused_not_silently_dropped():
    with pytest.raises(ValueError) as err:
        text_to_value(MAPPING, "{old: x, old: y}")
    assert "'old'" in str(err.value)


def test_items_that_are_not_mappings_are_refused_for_a_list_of_mappings():
    with pytest.raises(ValueError):
        text_to_value(RULES, "[S, R]")
