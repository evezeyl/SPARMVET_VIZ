"""The wiring of HOME's left sidebar render to `open_panels_after_redraw` (D-0502): the user's open and closed panels survive a redraw.

# @deps
# consumes: app/tests/home_harness.py (Home, ViewWorld), app/handlers/home_theater.py (sidebar_tools_ui, _sync_active_space), app/modules/sidebar_open_panels.py
# doc: .claude/rules/ui_implementation_contract.md#11e
# @end_deps

Runs the real `home_theater.define_server` headless. The accordion input is a stand-in the test sets. The pure rule has its own tests
(`test_sidebar_open_panels.py`); these show that the render calls it with the right facts: the accordion value read under `isolate`
(section 14, R4), the previous space, and that "the user closed everything" is not read as "first draw".

The panels the render builds also give their names through the private `AccordionPanel._data_value`; the last test pins that attribute
to the title the app passes, so a library upgrade that renames it fails here and not on a user's screen.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_left_sidebar_redraw_wiring.py -q
"""
import re
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from shiny import reactive, ui
from shiny.types import SilentException

from app.modules import sidebar_open_panels
from app.tests.home_harness import Home, ViewWorld
from app.handlers import home_theater

CHOICE = "Data analysis recipe Choice"
EXPORT = "Export / Import"
INFO = "Info"
PANELS = [{"type": "data_analysis_recipe_info"}, {"type": "data_analysis_recipe_choice"}, {"type": "export"}]


class FakeInput:
    """`input.nav_accordion()`: a value, None (a page that says nothing is open) or absent (SilentException: not sent yet)."""

    ABSENT = object()

    def __init__(self):
        self.value = self.ABSENT
        self.reads = []

    def __getattr__(self, name):
        # every other input of HOME: the handlers only register on it, nothing here reads them
        return MagicMock()

    def nav_accordion(self):
        self.reads.append(self.value)
        if self.value is self.ABSENT:
            raise SilentException()
        return self.value


@pytest.fixture
def home(tmp_path, monkeypatch):
    world = ViewWorld(tmp_path)
    fake = FakeInput()
    h = Home(world, monkeypatch, flags=("interactivity_enabled", "export_enabled", "data_analysis_recipe_selector_visible"), inputs={"sidebar_nav": "Home"}, input_=fake)
    h.fake = fake
    h.bootloader.get_sidebar_config.side_effect = lambda ws, side: SimpleNamespace(
        panels=PANELS if ws == "home" else [], visible=True)
    h.bootloader.get_data_analysis_recipe_selector.return_value = {"visible": True}
    return h


def open_names(rendered) -> list:
    """The titles of the panels drawn open, read from the HTML the render returns."""
    html = str(rendered)
    names = []
    for item in re.findall(r'<div class="accordion-item".*?</div>\s*</div>\s*</div>', html, flags=re.S):
        if re.search(r'accordion-collapse collapse show', item):
            names.append(re.search(r'data-value="([^"]+)"', item).group(1))
    return names


REAL_ISOLATE = reactive.isolate  # `draw` must not go through a test's wrapped isolate


def draw(home):
    with REAL_ISOLATE():
        return home.outputs["sidebar_tools_ui"]()


def go_to(home, space):
    home.inputs["sidebar_nav"] = space
    with reactive.isolate():
        home.effects["_sync_active_space"]()


def test_first_draw_uses_the_fixed_list(home):
    assert open_names(draw(home)) == [CHOICE]


def test_the_helper_to_read_the_html_sees_open_and_closed(home):
    """The reader of these tests must be able to tell: with the user's choice [] nothing is open, with [Export] only that one."""
    draw(home)
    home.fake.value = []
    assert open_names(draw(home)) == []
    home.fake.value = [EXPORT]
    assert open_names(draw(home)) == [EXPORT]


def test_a_redraw_in_the_same_space_keeps_what_the_user_opened(home):
    draw(home)
    home.fake.value = [CHOICE, EXPORT]
    assert open_names(draw(home)) == [CHOICE, EXPORT]


def test_a_redraw_in_the_same_space_keeps_what_the_user_closed(home):
    draw(home)
    home.fake.value = [EXPORT]
    assert open_names(draw(home)) == [EXPORT]


@pytest.mark.parametrize("answer", [[], None])
def test_everything_closed_by_the_user_stays_closed_and_is_not_a_first_draw(home, answer):
    draw(home)
    home.fake.value = answer
    assert open_names(draw(home)) == []


def test_a_single_open_panel_arrives_as_text_and_is_kept(home):
    draw(home)
    home.fake.value = EXPORT
    assert open_names(draw(home)) == [EXPORT]


def test_the_page_has_not_answered_yet_uses_the_fixed_list(home):
    draw(home)
    home.fake.value = FakeInput.ABSENT
    assert open_names(draw(home)) == [CHOICE]


def test_a_change_of_space_and_back_uses_the_fixed_list_again(home):
    draw(home)
    home.fake.value = [EXPORT]
    go_to(home, "Gallery")
    draw(home)
    go_to(home, "Home")
    assert open_names(draw(home)) == [CHOICE]


def test_the_accordion_is_read_under_isolate(home, monkeypatch):
    """Reading it tracked would make a click on a panel draw the sidebar again and undo the click (section 14, R4)."""
    inside = []
    real = REAL_ISOLATE

    @contextmanager
    def tracking():
        inside.append(1)
        try:
            with real():
                yield
        finally:
            inside.pop()

    monkeypatch.setattr(reactive, "isolate", tracking)
    seen = []
    original = home.fake.nav_accordion
    home.fake.nav_accordion = lambda: (seen.append(bool(inside)), original())[1]
    draw(home)
    home.fake.value = [EXPORT]
    draw(home)
    assert seen and all(seen), seen


def test_the_render_hands_the_pure_rule_the_previous_space_and_the_fixed_list(home, monkeypatch):
    calls = []
    real = sidebar_open_panels.open_panels_after_redraw
    monkeypatch.setattr(home_theater, "open_panels_after_redraw", lambda *a: (calls.append(a), real(*a))[1])
    draw(home)
    home.fake.value = [EXPORT]
    draw(home)
    first, second = calls
    assert first[0] == [CHOICE] and first[2] is None and first[3] is None
    assert second[0] == [CHOICE] and second[2] == first[1] and second[3] == [EXPORT]


def test_the_private_attribute_that_names_a_panel_is_its_title():
    """The render lists the panels it built through `AccordionPanel._data_value` (the library has no public name for it)."""
    panel = ui.accordion_panel("Some title", ui.p("body"))
    assert panel._data_value == "Some title"
