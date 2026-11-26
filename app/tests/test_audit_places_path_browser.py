"""The places of the audit dialog along the path of the lineage, in the browser (HOME audit, small step after demo step 7; D-0553, D-0346).

Run (qa app features): PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_places_path_browser.py -q

What a person sees on the demo `1_test_data_ST22_dummy`, plot "AMR Heatmap", filter `identity < 99` sent to audit, choice "At a table this plot is built from":
- the lines read as a path, indented by depth: Table ResFinder (tier 1), Table ResFinder (tier 2), Plot amr_heatmap (tier 3);
- ticking tier 1: the two lines below it are greyed, cannot be ticked, and say "~ follows from the place chosen above"; unticking frees them;
- ticking the plot's own line: the places above it cannot be ticked; ticking tier 2: tier 1 cannot be ticked, the plot's line is derived;
- with tier 1 ticked, a reason and Apply: the step is written at that place (the audit panel says so).

Mutation index (each seen failing): MUTATION D1 the script does not disable the derived places (the greyed line stays tickable).
"""
import re

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_mode, set_view
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_audit_places_browser import REASON, _amr_plot, _send_filter, _tick
from app.tests.test_shiny_smoke import _load_data_analysis_recipe, _open_filters_panel, _wait_shiny

T1, T2, OWN = "T1:ResFinder", "T2:ResFinder", "T3:amr_heatmap"


def _box(page: Page, place: str):
    return page.locator(f"#propagation_places input[value='{place}']")


def _row(page: Page, place: str):
    return page.locator(f"#propagation_places .spv-place-row:has(input[value='{place}'])")


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    _amr_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    yield page
    set_mode(page, "exploration")


def test_the_places_read_as_a_path_and_the_derived_places_follow_the_tick(ready: Page):
    page = ready
    _send_filter(page)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    # the order and the depth: original table first, the plot's own line last, each one deeper than the one above
    values = page.locator("#propagation_places input").evaluate_all("els => els.map(e => e.value)")
    assert values == [T1, T2, OWN], values
    depths = page.locator("#propagation_places .spv-place-row").evaluate_all("els => els.map(e => e.style.getPropertyValue('--spv-depth'))")
    assert depths == ["0", "1", "2"], depths
    text = page.locator("#propagation_places_wrapper").inner_text()
    assert "Table ResFinder (tier 1)" in text and "Table ResFinder (tier 2)" in text and "Plot amr_heatmap (tier 3)" in text
    for place in (T1, T2, OWN):
        expect(_box(page, place)).to_be_enabled()
    # tier 1 ticked: everything below is derived, shown with "~", cannot be ticked
    _tick(page, T1)
    for place in (T2, OWN):
        expect(_box(page, place)).to_be_disabled()
        expect(_row(page, place)).to_have_class(re.compile("spv-place-derived"))
        expect(_row(page, place)).to_contain_text("~ follows from the place chosen above")
    expect(_box(page, T1)).to_be_enabled()
    # untick: all free again, no note
    _tick(page, T1, False)
    for place in (T1, T2, OWN):
        expect(_box(page, place)).to_be_enabled()
    assert "follows from" not in page.locator("#propagation_places_wrapper").inner_text()
    # the plot's own line ticked: the places above it cannot be chosen
    _tick(page, OWN)
    for place in (T1, T2):
        expect(_box(page, place)).to_be_disabled()
        expect(_row(page, place)).to_contain_text("one place on a path")
    _tick(page, OWN, False)
    # tier 2 ticked: tier 1 cannot be ticked, the plot's line is derived
    _tick(page, T2)
    expect(_box(page, T1)).to_be_disabled()
    expect(_box(page, OWN)).to_be_disabled()
    expect(_row(page, OWN)).to_contain_text("~")
    # the list was not drawn again by the clicks: the same boxes are still there
    assert page.locator("#propagation_places input").count() == 3
    _tick(page, T2, False)
    page.keyboard.press("Escape")
    expect(page.locator("#propagation_confirm")).to_have_count(0, timeout=5_000)


def test_confirm_writes_the_step_at_the_chosen_place(ready: Page):
    page = ready
    _send_filter(page)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    _tick(page, T1)
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=15_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at ResFinder: Table, T1", timeout=10_000)
    page.locator('input[id^="t3_reason_"]').first.fill(REASON)
    page.wait_for_timeout(300)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at ResFinder: Table, T1")
    # leave nothing behind for the next test: remove the step (the bin of the card)
    page.locator("[id^='t3_delete_']").first.click()
    _wait_shiny(page)
