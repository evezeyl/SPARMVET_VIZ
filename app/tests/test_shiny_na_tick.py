"""The tick "keep the rows with no value" of the HOME filter dialog (NA-RULE-63 part 2, Eve 2026-11-14), in the browser.

Recipe `demo_abromics`: its table has 28 rows, two of them with no value in `sequence_type`.
The tick is shown, preselected by operator (`!=` keeps, `=` removes), says what it does with the counts, and
flipping it changes the rows the filter leaves in the table.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_na_tick.py -q
"""
import re

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 - re-exports the fixture
from app.tests.test_shiny_smoke import (
    _choose_recipe, _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny,
)

SUMMARY = "#home_data_preview .shiny-data-grid-summary"


def _rows_in_grid(page: Page) -> int:
    page.wait_for_selector(SUMMARY, timeout=15_000)
    return int(re.search(r"of (\d+)", page.locator(SUMMARY).inner_text()).group(1))


def _pick_value(page: Page, value: str) -> None:
    page.locator("#fb_value-selectized").fill(value)
    page.keyboard.press("Enter")
    _wait_shiny(page)


def _wait_rows(page: Page, n: int) -> None:
    page.wait_for_function("([sel, n]) => (document.querySelector(sel)?.innerText || '').includes('of ' + n)",
                           arg=[SUMMARY, str(n)], timeout=15_000)


def test_the_tick_is_preselected_by_operator_and_flipping_it_changes_the_rows(page: Page, shiny_app: ShinyAppProc):
    _open_app(page, shiny_app.url)
    _choose_recipe(page, "demo_abromics")
    page.locator(".nav-link:has-text('Sequence Types by Source')").first.click()
    _wait_shiny(page)
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, "year")
    page.locator("#fb_col").select_option("year")
    _wait_shiny(page)
    assert _rows_in_grid(page) == 28

    # the tick is shown, preselected by operator: `!=` keeps, `=` removes; the counts are on the table the filter acts on
    page.locator("#fb_op").select_option("ne")
    _wait_shiny(page)
    expect(page.locator("#fb_na")).to_be_checked(timeout=5_000)
    expect(page.locator("#filter_na_text_ui")).to_contain_text("6 rows have no value in year: they are kept")
    expect(page.locator("#filter_na_text_ui")).to_contain_text("kept because the box is ticked")   # the warning for != on a column with missing values
    page.locator("#fb_op").select_option("eq")
    _wait_shiny(page)
    expect(page.locator("#fb_na")).not_to_be_checked(timeout=5_000)
    expect(page.locator("#filter_na_text_ui")).to_contain_text("6 rows have no value in year: they are removed")

    # `= 2024` with the preselected tick (remove): 22 rows; then the tick flipped (keep): 28 rows
    _pick_value(page, "2024")
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)
    expect(page.locator("#filter_rows_ui")).to_contain_text("rows with no value removed")
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    _wait_rows(page, 22)
    page.locator("#filter_remove_0").click()
    _wait_shiny(page)
    _wait_rows(page, 28)

    page.locator("#fb_na").check()
    _wait_shiny(page)
    expect(page.locator("#filter_na_text_ui")).to_contain_text("they are kept")
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("rows with no value kept", timeout=5_000)
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    # 22 rows equal 2024, 6 have no value: keep adds those 6, so the filter leaves all 28 and the badge says a filter is on
    expect(page.locator("#home_data_preview_badge .spv-view-note", has_text="preview filter")).to_be_visible(timeout=15_000)
    assert _rows_in_grid(page) == 28
    page.locator("#filter_remove_0").click()
    _wait_shiny(page)
