"""The two facts of the HOME data preview in the browser (D-0488, PROVISIONAL words), on the ST22 demo recipe.

# @deps
# consumes: app/tests/browser_view.py, app/tests/test_shiny_smoke.py (_load_data_analysis_recipe, _wait_shiny), app/handlers/home_theater.py (home_data_preview_badge, preview_all_rows, preview_col_selector)
# @end_deps

Run (qa app features): PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_home_preview_lines_browser.py -q

What a person sees: a table of more than 100 rows says "Showing 100 of N rows" and nothing else on the screen gives 100 as the table's
rows (the grid's own "Viewing rows ... of 100" line is off); "All rows" changes the sentence to "N rows"; taking a column out of the
chooser says how many are hidden, and the chooser keeps what the user set (rule R4).
"""
import re

from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_mode, set_source, set_view, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _load_data_analysis_recipe

BADGE = "#home_data_preview_badge"
SHOWING = re.compile(r"Showing 100 of (\d+) rows")


def _badge_text(page: Page) -> str:
    wait_shiny(page, 30_000)
    return page.locator(BADGE).inner_text()


def _find_big_table(page: Page) -> int:
    """Walk the Source tables, T1, T2 and T3 of each plot tab until one has more than 100 rows; return its N."""
    set_mode(page, "exploration")
    tabs = page.locator("[id^='subtabs_'] .nav-link:visible")
    for i in range(tabs.count()):
        tabs.nth(i).click()
        wait_shiny(page, 30_000)
        for view in ("T1", "T2", "T3"):
            set_view(page, view)
            hit = SHOWING.search(_badge_text(page))
            if hit:
                return int(hit.group(1))
        set_view(page, "SRC")
        for table in page.locator("#source_table option").evaluate_all("els => els.map(e => e.value)"):
            set_source(page, table)
            hit = SHOWING.search(_badge_text(page))
            if hit:
                return int(hit.group(1))
    raise AssertionError("no table of more than 100 rows on the demo recipe")


def _switch_all_rows(page: Page, on: bool) -> None:
    """Flip the "All rows" switch with a plain click event and wait until it holds the wanted state and Shiny is idle: Playwright's own
    set_checked reports "did not change its state" when the header re-renders around the click."""
    wait_shiny(page, 30_000)
    if page.locator("#preview_all_rows").is_checked() != on:
        page.locator("#preview_all_rows").evaluate("e => e.click()")
    page.wait_for_function("(on) => document.getElementById('preview_all_rows').checked === on", arg=on, timeout=10_000)
    wait_shiny(page, 30_000)


def test_rows_all_rows_and_hidden_columns(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    n = _find_big_table(page)
    assert n > 100
    expect(page.locator(BADGE)).to_contain_text(f"Showing 100 of {n} rows")
    # one total on the screen: the grid's own summary line is off, and no text gives 100 as the number of rows of the table
    body = page.locator("body").inner_text()
    assert "Viewing rows" not in body
    assert not re.search(r"\b(of|total)\s+100\b(?! rows)", body.replace(f"Showing 100 of {n} rows", "")), "a second total on screen"
    # All rows: the sentence is the size
    _switch_all_rows(page, True)
    expect(page.locator(BADGE)).to_contain_text(f"{n} rows")
    assert "Showing" not in page.locator(BADGE).inner_text()
    _switch_all_rows(page, False)
    expect(page.locator(BADGE)).to_contain_text(f"Showing 100 of {n} rows")
    # no hidden column at the start; take one out: the count appears and the chooser keeps the user's choice
    assert "hidden" not in page.locator(BADGE).inner_text()
    items = page.locator("#preview_col_selector + .selectize-control .item")
    if not items.first.is_visible():
        # a click on the switch in the accordion header can also fold the panel (the header is one button): open it again
        page.locator("#acc_home_data .accordion-button").first.click()
        expect(items.first).to_be_visible(timeout=10_000)
    before = items.count()
    assert before >= 2
    items.first.hover()   # the remove link of a selectize item shows on hover
    items.first.locator(".remove").click()
    wait_shiny(page, 30_000)
    expect(page.locator(BADGE)).to_contain_text("1 column hidden; add it back in the column chooser")
    page.wait_for_timeout(500)   # a re-mounted chooser would snap back after the busy flag clears; the absence of a change needs a window
    wait_shiny(page, 30_000)
    assert page.locator("#preview_col_selector + .selectize-control .item").count() == before - 1
    expect(page.locator(BADGE)).to_contain_text("1 column hidden")
