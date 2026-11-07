"""The Info panel shows whatever the data analysis data analysis recipe author wrote under `info:`, with its structure."""
import pytest

from app.modules.data_analysis_recipe_info import info_lines


def test_flat_keys_are_shown_as_label_and_value():
    assert info_lines({"display_name": "AMR", "version": "1.0"}) == [(0, "display_name", "AMR"), (0, "version", "1.0")]


def test_any_key_the_author_adds_is_shown():
    lines = info_lines({"contact": "eve@example.org", "funder": "NFR"})
    assert (0, "contact", "eve@example.org") in lines and (0, "funder", "NFR") in lines


def test_nested_mapping_keeps_its_structure():
    assert info_lines({"study": {"name": "S1", "year": 2024}}) == [(0, "study", None), (1, "name", "S1"), (1, "year", "2024")]


def test_list_of_values_and_list_of_mappings():
    assert info_lines({"tags": ["a", "b"]}) == [(0, "tags", None), (1, "-", "a"), (1, "-", "b")]
    assert info_lines({"people": [{"name": "A"}, {"name": "B"}]}) == [(0, "people", None), (1, "name", "A"), (1, "name", "B")]


@pytest.mark.parametrize("empty", [None, {}, [], ""])
def test_missing_or_empty_info_gives_no_lines(empty):
    assert info_lines(empty) == []


def test_empty_value_does_not_crash_and_keeps_the_label():
    assert info_lines({"description": None, "notes": []}) == [(0, "description", ""), (0, "notes", "")]


def _template(panel_type):
    return {"name": "x", "flags": {}, "workspaces": {"home": {"left_sidebar": {"visible": True, "panels": [{"type": panel_type}]}}}}


def test_old_panel_type_is_refused_with_the_new_name():
    from app.modules.sidebar_validator import SidebarValidator
    errors = SidebarValidator().validate(_template("project_info"), "x.yaml")  # audit:allow-old-word
    assert len(errors) == 1
    assert "data_analysis_recipe_info" in errors[0].problem


def test_new_panel_type_is_accepted():
    from app.modules.sidebar_validator import SidebarValidator
    assert SidebarValidator().validate(_template("data_analysis_recipe_info"), "x.yaml") == []
