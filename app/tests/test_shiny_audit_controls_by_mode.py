"""The "Pending" badge and the Apply button of the audit panel are shown in Audit mode only (D-0377), in the browser.

# @deps
# consumes: app/handlers/audit_stack.py (audit_pending_badge_ui, audit_stack_tools_ui), app/src/server.py (home_mode)
# @end_deps

In Exploration neither is in the page (they do nothing there); in Audit mode both are as before; a step sent to audit and not yet
applied is still pending after a pass through Exploration, and the Apply button comes back with it.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_audit_controls_by_mode.py -q
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.browser_view import set_mode, set_view
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_shiny_smoke import (_INTERACTIVE_APP_FEATURES, _choose_fb_op, _load_data_analysis_recipe, _navigate_to_mlst_plot,
                                        _open_filters_panel, _wait_shiny)

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
pytestmark = pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="needs the audit panel")


def test_badge_and_apply_only_in_audit_mode_and_pending_nodes_survive(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)

    # Exploration: nothing that does nothing
    set_mode(page, "exploration")
    expect(page.locator("#btn_apply")).to_have_count(0)
    expect(page.locator(".audit-pending-badge")).to_have_count(0)

    # Audit: both, as before (the badge: the audit has never been applied in this session)
    set_mode(page, "audit")
    set_view(page, "T3")
    expect(page.locator("#btn_apply")).to_have_count(1, timeout=10_000)
    expect(page.locator(".audit-pending-badge")).to_have_count(1, timeout=10_000)

    # a step sent to audit, not applied
    _choose_column_firmly(page, "year")
    _choose_fb_op(page, "gt")
    _wait_shiny(page)
    page.locator("#fb_value").fill("2000")
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=15_000)

    # back to Exploration: the controls are gone, and so is the whole audit panel (D-0383: the right panel is empty in Exploration, it closes
    # again with the mode, D-0385); the pending node is not lost: it is in the state and comes back with the panel
    set_mode(page, "exploration")
    expect(page.locator("#btn_apply")).to_have_count(0, timeout=10_000)
    expect(page.locator(".audit-pending-badge")).to_have_count(0)
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(0)

    # and back to Audit: the node, the badge and the Apply button are there
    set_mode(page, "audit")
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=10_000)
    expect(page.locator(".audit-pending-badge")).to_have_count(1, timeout=10_000)
    expect(page.locator("#btn_apply")).to_have_count(1, timeout=10_000)


def _a_step_with_a_typed_reason(page: Page, url: str, reason: str) -> None:
    """A step sent to audit in Audit mode, its reason typed and NOT applied (in a new session: the page of this module is shared by its tests)."""
    page.goto(url)
    page.wait_for_selector("#nav_sidebar", timeout=60_000)
    _load_data_analysis_recipe(page, url)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    _choose_column_firmly(page, "year")
    _choose_fb_op(page, "gt")
    _wait_shiny(page)
    page.locator("#fb_value").fill("2000")
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]')
    expect(box).to_have_count(1, timeout=15_000)
    expect(page.locator("#btn_apply")).to_be_disabled(timeout=10_000)         # no reason yet
    box.fill(reason)
    box.press("Tab")                                                           # the box sends its text when it is left
    _wait_shiny(page)
    expect(page.locator("#btn_apply")).to_be_enabled(timeout=10_000)


def test_a_reason_typed_and_not_applied_is_kept_when_the_user_goes_to_exploration_and_back(page: Page, shiny_app: ShinyAppProc):
    """The panel is empty in Exploration (its boxes leave the page): the text the user typed must not be dropped silently (review 2026-11-21)."""
    _a_step_with_a_typed_reason(page, shiny_app.url, "poor quality, notebook 12")
    set_mode(page, "exploration")
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(0, timeout=10_000)
    set_mode(page, "audit")
    box = page.locator('input[id^="t3_reason_"]')
    expect(box).to_have_count(1, timeout=10_000)
    expect(box).to_have_value("poor quality, notebook 12", timeout=10_000)
    expect(page.locator("#btn_apply")).to_be_enabled(timeout=10_000)


def test_a_reason_typed_and_not_applied_is_kept_when_the_user_goes_to_the_gallery_and_back(page: Page, shiny_app: ShinyAppProc):
    _a_step_with_a_typed_reason(page, shiny_app.url, "outlier, see log")
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    _wait_shiny(page)
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(0, timeout=10_000)
    page.locator("#sidebar_nav").get_by_text("Home", exact=True).first.click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]')
    expect(box).to_have_count(1, timeout=15_000)
    expect(box).to_have_value("outlier, see log", timeout=10_000)
    expect(page.locator("#btn_apply")).to_be_enabled(timeout=10_000)
