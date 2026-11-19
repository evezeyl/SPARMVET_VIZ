"""Apply pressed before the button was drawn locked again: the page stays alive, the user is told, nothing is applied
(APPLY-BLOCKED-1; D-0050, D-0099).

Apply is disabled while a step has no reason. A click that arrives before the button is redrawn reached `handle_apply` with a step
that had no reason, and the branch that must tell the user raised AttributeError: the effect ended with "Unhandled error" and the
connection was closed. The click is forced here as a too-fast user would make it: the page removes the `disabled` attribute and
clicks.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_apply_blocked.py -q
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_shiny_session_restore import _RECORD_NOTICES, _free, _notices, _reasons, _seen
from app.tests.test_shiny_smoke import (_INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _navigate_to_mlst_plot,
                                        _open_filters_panel, _choose_fb_op, _wait_shiny)

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="needs the audit panel")
def test_a_forced_apply_on_a_step_without_a_reason_keeps_the_page_alive_and_applies_nothing(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    page.evaluate(_RECORD_NOTICES)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)
    page.locator("#tier_toggle input[value=T3]").check(force=True)
    _wait_shiny(page)
    _choose_column_firmly(page, "year") 
    _choose_fb_op(page, "gt")
    _wait_shiny(page)
    page.locator("#fb_value").fill("2000")
    page.wait_for_timeout(200)   # the number box is mounted again after the operator changes: a value typed in that moment is lost
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)

    # the contract: the step has no reason, so Apply is locked and says so
    apply = page.locator("#btn_apply").first
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=15_000)
    expect(apply).to_have_text("Apply ⛔", timeout=15_000)
    expect(apply).to_be_disabled()

    # a click that comes before the button is drawn again: the page removes `disabled` and clicks
    page.eval_on_selector("#btn_apply", "e => { e.disabled = false; e.click(); }")
    _notices(page, "forced Apply", "have no reason", 1)
    _free(page, "forced Apply")
    assert page.locator("#shiny-disconnected-overlay").count() == 0, "the connection was closed: the page is dead"
    text = page.evaluate("() => [...document.querySelectorAll('.shiny-notification')].map(n => n.textContent).join(' | ')")
    assert "Suggestion: write a reason for each step, then press Apply" in text or _seen(page, "Suggestion: write a reason") == 1, text
    assert _seen(page, "audit steps applied") == 0, "the step was applied without a reason"
    assert len(_reasons(page)) == 1, "the step is still pending in the audit panel"

    # the page is alive: a reason is typed and Apply now applies
    box = page.locator('input[id^="t3_reason_"]').first
    box.fill("the reason typed after the refusal")
    box.press("Tab")
    expect(apply).to_have_text("Apply", timeout=15_000)
    expect(apply).to_be_enabled()
    page.eval_on_selector("#btn_apply", "e => e.click()")
    _notices(page, "Apply with a reason", "audit steps applied", 1)
