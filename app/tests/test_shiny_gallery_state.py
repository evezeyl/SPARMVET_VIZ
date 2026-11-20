"""The Gallery keeps its state when the user leaves for HOME and comes back (GALLERY-CHECK-1 finding 1).

The panel independence rule (ui_implementation_contract.md section 13): switching spaces never resets another space's
state. Eve, 2026-11-20: "maybe would be nice to keep what was selected if we need to navigate back and forth".
Browser test (flag: SPARMVET_APP_FEATURES=qa). NOT covered: the open/closed state of the filter groups after a return.
Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_gallery_state.py -q
"""
from app.tests.conftest import shiny_app  # noqa: F401 - re-exports the fixture
from app.tests.test_shiny_gallery_filters import (PIVOT, REGISTRY, _apply, _idle, _only, _open_gallery,
                                                  _options, _selected, _ticked)
from playwright.sync_api import Page



def _home_and_back(page: Page):
    page.locator("#sidebar_nav").get_by_text("Home", exact=True).first.click()
    _idle(page)
    page.wait_for_timeout(800)
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    page.wait_for_function("document.querySelectorAll('#gallery_example_select option').length>0", timeout=30_000)
    _idle(page)
    page.wait_for_timeout(800)


def _advanced_example() -> str:
    return sorted(PIVOT["by_difficulty"]["Advanced"])[-1]


def test_return_from_home_keeps_example_and_filters(page: Page, shiny_app):
    _open_gallery(page, shiny_app.url)
    _only(page, "difficulty", "Advanced")
    _apply(page)
    wanted = _advanced_example()
    assert wanted in _options(page)
    page.select_option("#gallery_example_select", wanted)
    _idle(page)
    n_before = len(_options(page))
    _home_and_back(page)
    assert _selected(page) == wanted
    assert len(_options(page)) == n_before == len(PIVOT["by_difficulty"]["Advanced"])
    assert _ticked(page, "difficulty") == ["Advanced"]
    assert f"{n_before} matched" in page.inner_text("label[for=gallery_example_select]")
    assert page.locator("#gallery_preview_img img").count() == 1


def test_return_keeps_ticks_that_were_not_applied(page: Page, shiny_app):
    _open_gallery(page, shiny_app.url)
    _only(page, "family", "Distribution")
    _home_and_back(page)
    assert _ticked(page, "family") == ["Distribution"]
    assert len(_options(page)) == len(REGISTRY)  # ticked but never applied: the list is still the whole list