"""The controls of the audit are shown in Audit mode only (D-0377), and a reason typed and not added is not lost silently (D-0050), in the browser.

# @deps
# consumes: app/handlers/audit_stack.py (the cards of the right panel), app/handlers/trial_handlers.py (the trial panel, the reason draft), app/handlers/filter_and_audit_handlers.py (the button Try), app/src/server.py (home_mode)
# @end_deps

FLOW-3 (2026-11-27): the "Pending" badge and the Apply button of the old way are gone (a step is tried, then added with its reason). What stays true, and is tested here:
- in Exploration neither Try nor the panel of a trial nor the Pipeline Audit card is in the page (they do nothing there); in Audit mode a staged condition has its Try and, once tried, its panel;
- the reason typed in the panel of a trial and not added is a DRAFT: leaving Audit mode ends the trial (one plain notice, nothing applied), and the next trial has the draft in its reason box, so the text
  is never dropped silently; a trip to the Gallery and back keeps the trial and its reason.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_audit_controls_by_mode.py -q
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.browser_view import set_mode, set_view, stage_condition, try_staged
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _navigate_to_mlst_plot, _open_filters_panel, _wait_shiny

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
pytestmark = pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="needs the audit panel")


def _a_tried_step_with_a_typed_reason(page: Page, url: str, reason: str) -> None:
    """A condition tried in Audit mode and its reason typed and NOT added (in a new session: the page of this module is shared by its tests)."""
    page.goto(url)
    page.wait_for_selector("#nav_sidebar", timeout=60_000)
    _load_data_analysis_recipe(page, url)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    stage_condition(page, "year", "gt", 2000)
    try_staged(page)
    expect(page.locator("#trial_add")).to_be_disabled(timeout=10_000)         # no reason yet
    box = page.locator("input[id^='trial_reason_']")
    box.fill(reason)
    box.press("Tab")                                                           # the box sends its text when it is left
    _wait_shiny(page)
    expect(page.locator("#trial_add")).to_be_enabled(timeout=10_000)


def test_the_controls_of_a_step_are_in_audit_mode_only(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)

    # Exploration: nothing that does nothing, and nothing of the old way
    set_mode(page, "exploration")
    for gone in ("#btn_apply", ".audit-pending-badge", "#filter_send_to_audit", "#propagation_confirm", "#filter_try", ".spv-trial-panel", "#col_drop_try"):
        expect(page.locator(gone)).to_have_count(0)

    # Audit: Try comes with a staged condition, the panel of the trial with the Try; the old controls are not there either
    set_mode(page, "audit")
    set_view(page, "T3")
    for gone in ("#btn_apply", ".audit-pending-badge", "#filter_send_to_audit"):
        expect(page.locator(gone)).to_have_count(0)
    expect(page.locator("#filter_try")).to_have_count(0)                       # nothing staged yet
    stage_condition(page, "year", "gt", 2000)
    expect(page.locator("#filter_try")).to_have_count(1, timeout=10_000)
    try_staged(page)
    expect(page.locator(".spv-trial-panel")).to_have_count(1)

    # back to Exploration: the controls are gone, the trial ended with ONE notice and nothing was applied
    set_mode(page, "exploration")
    expect(page.locator(".spv-trial-panel")).to_have_count(0, timeout=10_000)
    expect(page.locator("#filter_try")).to_have_count(0)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("You left Audit mode. The trial ended", timeout=10_000)
    set_mode(page, "audit")
    expect(page.locator("[id^='t3_delete_']")).to_have_count(0)                # nothing was added by the trip


def test_a_reason_typed_and_not_added_is_kept_when_the_user_goes_to_exploration_and_back(page: Page, shiny_app: ShinyAppProc):
    """Leaving Audit mode ends the trial, but the text the user typed is a draft kept for the next trial: it must not be dropped silently (review 2026-11-21, FLOW-2)."""
    _a_tried_step_with_a_typed_reason(page, shiny_app.url, "poor quality, notebook 12")
    set_mode(page, "exploration")
    expect(page.locator("input[id^='trial_reason_']")).to_have_count(0, timeout=10_000)
    set_mode(page, "audit")
    set_view(page, "T3")
    stage_condition(page, "year", "gt", 2000)                                  # a change of mode clears the staged condition (D-0361): it is built again
    try_staged(page)
    expect(page.locator("input[id^='trial_reason_']")).to_have_value("poor quality, notebook 12", timeout=10_000)
    expect(page.locator("#trial_add")).to_be_enabled(timeout=10_000)


def test_a_reason_typed_and_not_added_is_kept_when_the_user_goes_to_the_gallery_and_back(page: Page, shiny_app: ShinyAppProc):
    _a_tried_step_with_a_typed_reason(page, shiny_app.url, "outlier, see log")
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    _wait_shiny(page)
    expect(page.locator("input[id^='trial_reason_']")).to_have_count(0, timeout=10_000)
    page.locator("#sidebar_nav").get_by_text("Home", exact=True).first.click()
    _wait_shiny(page)
    box = page.locator("input[id^='trial_reason_']")
    expect(box).to_have_count(1, timeout=15_000)
    expect(box).to_have_value("outlier, see log", timeout=10_000)
    expect(page.locator("#trial_add")).to_be_enabled(timeout=10_000)
