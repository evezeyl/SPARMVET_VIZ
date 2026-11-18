"""Exploration filters are emptied when the open recipe changes (ADR-099 point 1), and the user is told once.

Headless: the notice rule. Browser (qa app features): the real switch between two recipes that both have `sample_id`.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filters_cleared_on_recipe_change.py -q
"""
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

import re
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import polars as pl

from app.modules.t3_audit_engine import column_is_in_frame, filters_cleared_notice
from app.tests.subprocess_env import app_command, app_env
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _choose_recipe, _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny

A = "1_test_data_ST22_dummy"
B = "2_test_data_ST22_dummy"
NOTICE = "The filters of the previous recipe were removed"


class TestNoticeRule:
    def test_nothing_to_clear_gives_no_notice(self):
        assert filters_cleared_notice(0, 0) is None

    @pytest.mark.parametrize("pending,applied", [(1, 0), (0, 1), (2, 3)])
    def test_something_cleared_gives_one_plain_notice(self, pending, applied):
        text = filters_cleared_notice(pending, applied)
        assert text and text.startswith(NOTICE)
        assert "Audited steps are kept" in text


def _stage_sample_filter(page: Page) -> str:
    """Stage a `sample_id` in-list filter and return a value of it; the row is added to the staged list."""
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, "sample_id")
    page.locator("#fb_col").select_option("sample_id")
    _wait_shiny(page)
    page.locator("#fb_op").select_option("in")
    _wait_shiny(page)
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }", timeout=10_000)
    page.evaluate("() => { const s = document.getElementById('fb_value').selectize; s.addItem(Object.keys(s.options)[0]); }")
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)


def _choose_column_firmly(page: Page, column: str) -> None:
    """Choose a filter column and check the box really holds it once Shiny is idle: the form can re-render late and put
    the first column back (an app defect, reported). If that happens, choose again once and record it in the output."""
    _wait_for_fb_col_option(page, column)
    page.locator("#fb_col").select_option(column)
    _wait_shiny(page)
    if page.locator("#fb_col").input_value() != column:
        print(f"FORM RESET: the filter form put the column box back to {page.locator('#fb_col').input_value()!r}; choosing {column!r} again")
        page.locator("#fb_col").select_option(column)
        _wait_shiny(page)
    expect(page.locator("#fb_col")).to_have_value(column)


def _notices(page: Page):
    return page.locator(f".shiny-notification:has-text('{NOTICE}')")


def _fresh(page: Page, base_url: str, recipe: str = A):
    _open_app(page, base_url)
    _choose_recipe(page, recipe)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=20_000)
    _wait_shiny(page)


_PLOT_TABS = {A: ("AMR", "MLST Bar"), B: ("AMR Profiling Insight", "Multi-Resistance by Country")}


def _show_table(page: Page, recipe: str) -> None:
    """Open a plot sub-tab of the recipe so that the data preview is mounted."""
    group, plot = _PLOT_TABS[recipe]
    page.locator(f".nav-link:has-text('{group}')").first.click()
    _wait_shiny(page)
    page.locator(f".nav-link:has-text('{plot}')").first.click()
    _wait_shiny(page)
    _open_filters_panel(page)
    page.locator("#tier_toggle input[value=T3]").check(force=True)   # My view: the table shows the applied filters
    _wait_shiny(page)


def _row_count(page: Page) -> int:
    """Rows of the data preview ("Viewing rows 1 through 15 of 15"), read after Shiny is idle."""
    _wait_shiny(page, 30_000)
    grid = page.locator("#home_data_preview")
    expect(grid.locator("tbody tr").first).to_be_visible(timeout=20_000)
    summary = grid.locator(".shiny-data-grid-summary")
    if summary.count() == 0:                       # a table that fits one page has no summary line
        return grid.locator("tbody tr").count()
    return int(re.search(r" of (\d+)", summary.inner_text()).group(1))


def _count_settled(page: Page, expected: int) -> int:
    """The preview reaches `expected` rows (retrying read of the app state); returns the last count seen."""
    deadline = time.time() + 20
    count = _row_count(page)
    while count != expected and time.time() < deadline:
        page.wait_for_timeout(250)
        count = _row_count(page)
    return count


class TestRecipeSwitchClearsFilters:
    def test_table_of_the_other_recipe_is_not_filtered(self, page: Page, shiny_app: ShinyAppProc):
        """Real row counts: a filter applied on A must not shrink B's table, and A is unfiltered again on return."""
        _open_app(page, shiny_app.url)
        _choose_recipe(page, B)
        _show_table(page, B)
        unfiltered_b = _row_count(page)
        _choose_recipe(page, A)
        _show_table(page, A)
        unfiltered_a = _row_count(page)
        _stage_sample_filter(page)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        filtered_a = _row_count(page)
        assert filtered_a < unfiltered_a, "the filter did not change the table: the scenario proves nothing"
        _choose_recipe(page, B)
        _show_table(page, B)
        assert _count_settled(page, unfiltered_b) == unfiltered_b
        _choose_recipe(page, A)
        _show_table(page, A)
        assert _count_settled(page, unfiltered_a) == unfiltered_a

    def test_applied_filter_is_removed_and_noticed_once(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _stage_sample_filter(page)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        _choose_recipe(page, B)
        _wait_shiny(page)
        expect(_notices(page)).to_have_count(1, timeout=8_000)
        _open_filters_panel(page)
        expect(page.locator("#filter_remove_0")).to_have_count(0)
        expect(page.locator("#filter_apply")).not_to_contain_text("(1)")
        expect(page.locator("body")).not_to_contain_text("Active Filters")

    def test_staged_filter_is_removed_and_noticed(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _stage_sample_filter(page)
        _choose_recipe(page, B)
        expect(_notices(page)).to_have_count(1, timeout=8_000)
        _open_filters_panel(page)
        expect(page.locator("#filter_remove_0")).to_have_count(0)

    def test_no_filters_no_notice(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _choose_recipe(page, B)
        page.wait_for_timeout(1_000)
        expect(_notices(page)).to_have_count(0)
        _choose_recipe(page, A)
        page.wait_for_timeout(1_000)
        expect(_notices(page)).to_have_count(0)

    def test_filter_form_is_usable_after_the_switch(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _stage_sample_filter(page)
        _choose_recipe(page, B)
        _open_filters_panel(page)
        _wait_for_fb_col_option(page, "sample_id")
        expect(page.locator("#fb_col")).to_be_visible()
        # A new filter can be staged on the new recipe: the first row is index 0 again.
        _stage_sample_filter(page)

    def test_audited_step_of_recipe_a_is_back_after_returning(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _open_filters_panel(page)
        page.locator(".nav-link:has-text('AMR')").first.click()
        _wait_shiny(page)
        page.locator(".nav-link:has-text('MLST Bar')").first.click()
        _wait_shiny(page)
        page.locator("#tier_toggle input[value=T3]").check(force=True)
        _wait_shiny(page)
        _choose_column_firmly(page, "year")
        page.locator("#fb_op").select_option("lt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2050")
        page.wait_for_timeout(200)
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        page.locator("#filter_send_to_audit").click()
        _wait_shiny(page)
        page.locator("#propagation_confirm").click()
        _wait_shiny(page)
        reason = page.locator("textarea[id^='t3_reason_'], input[id^='t3_reason_']").first
        expect(reason).to_be_visible(timeout=8_000)
        reason.fill("test reason")
        _wait_shiny(page)
        page.locator("#btn_apply").click()
        _wait_shiny(page)
        expect(page.locator("body")).to_contain_text("year", timeout=5_000)
        _choose_recipe(page, B)
        # The audited step is not a staged filter: no notice for it, nothing cleared.
        expect(_notices(page)).to_have_count(0)
        _choose_recipe(page, A)
        page.wait_for_selector(".nav-link:has-text('AMR')", timeout=20_000)
        page.locator(".nav-link:has-text('AMR')").first.click()
        _wait_shiny(page)
        page.locator(".nav-link:has-text('MLST Bar')").first.click()
        _wait_shiny(page)
        expect(page.locator("body")).to_contain_text("year < 2050", timeout=20_000)


class TestColumnIsInFrame:
    def test_present_and_absent(self):
        lf = pl.DataFrame({"year": [1]}).lazy()
        assert column_is_in_frame(lf, "year")
        assert not column_is_in_frame(lf, "Year")        # case matters: recipe 2 has Year, recipe 1 has year
        assert not column_is_in_frame(pl.DataFrame({"a": [1]}), "year")

    def test_no_frame_stays_an_error_for_the_caller(self):
        assert column_is_in_frame(None, "year")


REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "tmpAI" / "browser_switch_filters" / "server.log"


def test_recipe_switch_with_a_column_chosen_logs_no_counts_error(page: Page):
    """Finding 5 of the switch check: after A -> B with `year` chosen in the filter form, the server log has no
    "counts ... could not be computed" and the form's text names B's own column."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with open(LOG, "w") as out:
        proc = subprocess.Popen(app_command(port), cwd=REPO, env=app_env(SPARMVET_APP_FEATURES="qa"), stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(90):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            _fresh(page, url)
            _open_filters_panel(page)
            _wait_for_fb_col_option(page, "year")
            page.locator("#fb_col").select_option("year")
            _wait_shiny(page)
            _choose_recipe(page, B)
            page.wait_for_timeout(2_000)
            expect(page.locator("#filter_na_text_ui")).not_to_contain_text("could not be computed")
            expect(page.locator("#filter_na_text_ui")).to_contain_text("Year")
        finally:
            proc.terminate()
            proc.wait(timeout=20)
    assert "could not be computed" not in LOG.read_text()
