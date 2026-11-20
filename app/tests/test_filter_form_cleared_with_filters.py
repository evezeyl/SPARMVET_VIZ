"""HOME-WALK C (D-0311, D-0361): when the exploration filters are cleared because the view changed (the mode, the table you view), the add-row form is
cleared with them: the column goes back to the first one, the operator to its first, the value box is empty.

The defect (found by the walk of 2026-11-20): after Exploration -> Audit -> Exploration the notice said the filters were removed, but the value box still
held the old pick ("Broiler"), so the next pick became "any of Broiler, Layer".

Browser, qa app features (every flag on, ghost save off), the shared app of `conftest.shiny_app`. NOT covered: a number or date value box (the same
re-mount; the text list is the case of the walk), a change of recipe (its own tests clear the form by the column check of `filter_form_ui`).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filter_form_cleared_with_filters.py -q
"""
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_mode, set_view
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly, _choose_operator, _fresh
from app.tests.test_shiny_smoke import _open_filters_panel, _wait_shiny


def _pick_a_value(page: Page) -> str:
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }", timeout=10_000)
    value = page.evaluate("() => { const s = document.getElementById('fb_value').selectize; const v = Object.keys(s.options)[0]; s.addItem(v); return v; }")
    page.wait_for_function("(v) => document.getElementById('fb_value').selectize.items.includes(v)", arg=value, timeout=5_000)
    _wait_shiny(page)
    return value


def _form_state(page: Page) -> dict:
    return page.evaluate("""() => ({col: document.getElementById('fb_col').value,
        first: document.querySelector('#fb_col option').value,
        items: (document.getElementById('fb_value') && document.getElementById('fb_value').selectize) ? document.getElementById('fb_value').selectize.items : null})""")


def test_the_form_is_cleared_with_the_filters_by_a_mode_round_trip(page: Page, shiny_app: ShinyAppProc):
    _fresh(page, shiny_app.url)
    _open_filters_panel(page)
    columns = page.evaluate("() => Array.from(document.querySelectorAll('#fb_col option')).map(o => o.value)")
    not_first = columns[-1]
    assert not_first != columns[0]
    _choose_column_firmly(page, not_first)
    _choose_operator(page, "in")
    picked = _pick_a_value(page)
    assert _form_state(page)["items"] == [picked]
    set_mode(page, "audit")
    set_mode(page, "exploration")
    _open_filters_panel(page)
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return !e || !e.selectize || e.selectize.items.length === 0; }", timeout=10_000)
    page.wait_for_function("() => document.getElementById('fb_col').value === document.querySelector('#fb_col option').value", timeout=10_000)
    state = _form_state(page)
    assert state["col"] == state["first"] and not state["items"], state


def test_the_form_is_cleared_when_the_viewed_table_changes(page: Page, shiny_app: ShinyAppProc):
    _fresh(page, shiny_app.url)
    _open_filters_panel(page)
    _choose_column_firmly(page, "sample_id")
    _choose_operator(page, "in")
    _pick_a_value(page)
    set_view(page, "T1")
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return !e || !e.selectize || e.selectize.items.length === 0; }", timeout=10_000)
    expect(page.locator("#fb_col")).to_have_value(page.evaluate("() => document.querySelector('#fb_col option').value"))
