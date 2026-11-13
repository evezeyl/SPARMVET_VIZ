"""The Blueprint form shows a list or a mapping parameter as YAML text, not as a Python repr (spec section 8, R1; issue #87).

Before the widgets `list` and `mapping` existed, `rename.mapping` and `recode_values.rules` were declared `string`: the
form showed `{'old': 'new'}` (a Python repr) and the save handler kept the typed text as a string.
The text-to-value step itself is tested in libs/blueprint_arch/tests/test_widget_text.py.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_widget_forms.py -q
"""
import re

import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.wrangle_studio import WrangleStudio
from transformer.actions.base import ACTION_SCHEMAS


def _textarea_text(widgets):
    return re.findall(r"<textarea[^>]*>([^<]*)</textarea>", "".join(str(w) for w in widgets))


@pytest.fixture
def studio():
    return WrangleStudio("test-session")


def test_a_mapping_is_shown_as_flow_yaml(studio):
    widgets = studio._render_action_form(
        "rename", ACTION_SCHEMAS["polars_rename"], {"mapping": {"old col": "new_col", "b": "c"}}, {"old col": "categorical"})
    assert _textarea_text(widgets) == ["{old col: new_col, b: c}"]


def test_a_list_of_mappings_is_shown_as_flow_yaml(studio):
    # no registered action takes a list of mappings any more (recode_values became a formula), so the widget is
    # exercised with a schema written for the test
    schema = {"label": "x", "category": "x", "context": ["t1"], "params": {
        "rules": {"widget": "list", "items": "mapping", "label": "Rules", "required": True}}}
    widgets = studio._render_action_form("x", schema, {"rules": [{"matches": "S", "value": 0}, {"default": 1}]}, {"resistance": "Categorical"})
    assert "[{matches: S, value: 0}, {default: 1}]" in _textarea_text(widgets)


def test_a_list_is_shown_as_flow_yaml(studio):
    widgets = studio._render_action_form(
        "modif_filter", ACTION_SCHEMAS["modif_filter"], {"column": "country", "op": "in", "value": ["Norway", "Sweden"], "na": "remove"}, {"country": "Categorical"})
    assert "[Norway, Sweden]" in _textarea_text(widgets)


def test_no_value_gives_an_empty_text_area_with_the_hint(studio):
    widgets = studio._render_action_form("rename", ACTION_SCHEMAS["polars_rename"], {}, {"a": "categorical"})
    html = "".join(str(w) for w in widgets)
    assert _textarea_text(widgets) == [""] and "{old_name: new_name" in html
