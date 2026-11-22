"""Exploration filters follow the TABLE, not the plot (D-0505, D-0506; cleared when the table changes, D-0311) - the real app.

# @deps
# consumes: app/handlers/filter_and_audit_handlers.py (_clear_filters_on_view_change), app/handlers/home_theater.py (_current_view_key), app/modules/t3_audit_engine.py (viewed_table, view_key), app/tests/test_filters_cleared_on_recipe_change.py (the helpers), app/tests/browser_view.py
# doc: .claude/rules/ui_implementation_contract.md#4
# @end_deps

The demo recipe: `mlst_bar` ("MLST Bar") and `year_distribution` ("Year Distribution") both read `MLST_with_metadata`; `virulence_bar`
("Virulence Bar") reads `ST22_Anchor`. On the table of the first, the user stages a row, picks a value in the form, applies a filter; opening the
second plot keeps all of it and tells nothing; opening the third clears all of it and says why.

On `dev` before this change the first part fails (opening another plot cleared the staged row).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filters_kept_on_same_table.py -q
"""
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_view
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import (
    A, _choose_column_firmly, _choose_operator, _count_settled, _count_settled_below, _fresh, _row_count, _stage_sample_filter)
from app.tests.test_shiny_smoke import _open_filters_panel, _wait_shiny

GROUP = "AMR and"
SAME_TABLE_A, SAME_TABLE_B, OTHER_TABLE = "MLST Bar", "Year Distribution", "Virulence Bar"
CAUSE = "reads another table"


def _open_plot_tab(page: Page, plot: str) -> None:
    link = page.locator(f".nav-link:has-text('{plot}')").first
    expect(link).to_be_visible(timeout=10_000)
    link.click()
    page.wait_for_function("(p) => Array.from(document.querySelectorAll('.nav-link.active')).some(t => t.innerText.includes(p))", arg=plot, timeout=15_000)
    _wait_shiny(page, 30_000)


def _start(page: Page, url: str) -> None:
    _fresh(page, url, A)
    group = page.locator(f".nav-link:has-text('{GROUP}')").first
    group.click()
    _open_plot_tab(page, SAME_TABLE_A)
    _open_filters_panel(page)
    set_view(page, "T3")
    _wait_shiny(page, 30_000)


def _notice(page: Page):
    return page.locator(f".shiny-notification:has-text('{CAUSE}')")


def _pick_value_in_the_form(page: Page) -> str:
    """Choose sample_id, `in`, and pick one value in the box WITHOUT adding the row: what the user is in the middle of typing."""
    _choose_column_firmly(page, "sample_id")
    _choose_operator(page, "in")
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 1; }", timeout=10_000)
    value = page.evaluate("() => { const s = document.getElementById('fb_value').selectize; const v = Object.keys(s.options)[1]; s.addItem(v); return v; }")
    page.wait_for_function("(v) => document.getElementById('fb_value').selectize.items.includes(v)", arg=value, timeout=5_000)
    _wait_shiny(page)
    return value


def test_a_plot_on_the_same_table_keeps_the_staged_row_the_typed_value_and_says_nothing(page: Page, shiny_app: ShinyAppProc):
    _start(page, shiny_app.url)
    _stage_sample_filter(page)
    typed = _pick_value_in_the_form(page)
    _open_plot_tab(page, SAME_TABLE_B)
    expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)          # the staged row is still there
    items = page.evaluate("() => document.getElementById('fb_value').selectize.items")
    assert typed in items, "the value picked in the form is still in the box"
    expect(page.locator("#fb_col")).to_have_value("sample_id")
    assert _notice(page).count() == 0, "no notice: nothing was removed"


def test_an_applied_filter_still_filters_a_plot_on_the_same_table_and_a_plot_on_another_table_clears_it(page: Page, shiny_app: ShinyAppProc):
    _start(page, shiny_app.url)
    unfiltered = _row_count(page)
    _stage_sample_filter(page)
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    filtered = _count_settled_below(page, unfiltered)
    assert 1 <= filtered < unfiltered, "the filter did not change the table: the scenario proves nothing"
    _open_plot_tab(page, SAME_TABLE_B)
    assert _count_settled(page, filtered) == filtered, "the same table, so the same filter"
    assert _notice(page).count() == 0
    _open_plot_tab(page, OTHER_TABLE)
    expect(_notice(page).first).to_be_visible(timeout=10_000)
    expect(page.locator("#filter_remove_0")).to_have_count(0)
    _open_plot_tab(page, SAME_TABLE_A)
    assert _count_settled(page, unfiltered) == unfiltered, "back on the first table: the cleared filter does not come back"
