"""HOME's T1 view in Audit mode shows the audited table (D-0622), in the browser.

Run (qa app features): PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_tier_views_browser.py -q

What a person sees on the demo `1_test_data_ST22_dummy`, plot "AMR Heatmap": a filter `identity < 99` written at tier 1 of ResFinder with a reason (Apply), then
- in Audit mode the T1 view shows the AUDITED table (fewer rows than the original) and its badge says "Viewing: T1, audited";
- a table the step does not change keeps the original: the badge of the MLST plot's T1 view says "Viewing: T1, original" and "no audit step changes this table";
- switching to Exploration shows the ORIGINAL table again (the original row count) and the old badge;
- back in Audit mode the audited table is shown again, and removing the step gives the original back in Audit mode too.

Mutation index (each seen failing): MUTATION V1 `_audited_view_lf` returns None in the handler (the T1 view stays the original in Audit mode).
"""
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_mode, set_view, wait_preview_rows
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_audit_places_browser import REASON, _amr_plot, _send_filter, _tick, expected  # noqa: F401
from app.tests.test_shiny_smoke import _load_data_analysis_recipe, _open_filters_panel, _wait_shiny


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    _amr_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    yield page
    set_mode(page, "exploration")


def test_the_t1_view_shows_the_audited_table_in_audit_mode_and_the_original_in_exploration(ready: Page, expected):  # noqa: F811
    page = ready
    before, after = expected["amr_before"], expected["amr_after"]
    wait_preview_rows(page, before, timeout=30_000)
    _send_filter(page)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    _tick(page, "T1:ResFinder")
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]').first
    expect(box).to_be_visible(timeout=15_000)
    box.fill(REASON)
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    try:
        wait_preview_rows(page, after, timeout=60_000)
        set_view(page, "T1")
        wait_preview_rows(page, after, timeout=30_000)
        expect(page.locator("#home_data_preview_badge")).to_contain_text("Viewing: T1, audited", timeout=20_000)
        # Exploration: the originals, whatever steps exist
        set_mode(page, "exploration")
        set_view(page, "T1")
        wait_preview_rows(page, before, timeout=30_000)
        expect(page.locator("#home_data_preview_badge")).not_to_contain_text("audited")
        # back in Audit mode: audited again
        set_mode(page, "audit")
        set_view(page, "T1")
        wait_preview_rows(page, after, timeout=30_000)
        # a plot beside ResFinder: its T1 view is the original and says so
        page.locator(".nav-link:has-text('AMR')").first.click()
        page.locator("[id^='subtabs_'] .nav-link:has-text('MLST Bar')").first.click()
        _wait_shiny(page)
        expect(page.locator("#home_data_preview_badge")).to_contain_text("Viewing: T1, original", timeout=20_000)
        expect(page.locator("#home_data_preview_badge")).to_contain_text("no audit step changes this table")
    finally:
        _amr_plot(page)
        set_mode(page, "audit")
        set_view(page, "T1")
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
            wait_preview_rows(page, before, timeout=60_000)
    expect(page.locator("#home_data_preview_badge")).to_contain_text("Viewing: T1, original", timeout=20_000)
    set_view(page, "T3")
