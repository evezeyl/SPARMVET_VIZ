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
from app.tests.test_shiny_smoke import _choose_recipe, _load_data_analysis_recipe

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


ACC_BUTTON = "#acc_home_data .accordion-button"


def _open_data_panel(page: Page) -> None:
    """Open the data panel on purpose (not by luck of its last state) and wait until it has finished opening, so that nothing moves under a hover."""
    wait_shiny(page, 30_000)
    if page.locator(ACC_BUTTON).first.get_attribute("aria-expanded") != "true":
        page.locator(ACC_BUTTON).first.click()
    expect(page.locator(ACC_BUTTON).first).to_have_attribute("aria-expanded", "true", timeout=10_000)
    page.wait_for_function("() => !document.querySelector('#acc_home_data .accordion-collapse.collapsing')", timeout=10_000)
    wait_shiny(page, 30_000)


def test_the_all_rows_switch_does_not_fold_the_data_panel(page: Page, shiny_app: ShinyAppProc):
    """The switch sits in the header of the accordion panel; a click on it must change the switch only, never open or fold the panel."""
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_data_panel(page)
    for on in (True, False, True, False):
        page.locator("#preview_all_rows").click(force=True)
        page.wait_for_function("(on) => document.getElementById('preview_all_rows').checked === on", arg=on, timeout=10_000)
        wait_shiny(page, 30_000)
        page.wait_for_timeout(600)   # a folding animation takes about 350 ms
        expect(page.locator(ACC_BUTTON).first).to_have_attribute("aria-expanded", "true")
    # and the label text of the switch does the same
    page.locator("label[for=preview_all_rows]").click()
    page.wait_for_timeout(600)
    expect(page.locator(ACC_BUTTON).first).to_have_attribute("aria-expanded", "true")
    assert page.locator("#preview_all_rows").is_checked()
    page.locator("label[for=preview_all_rows]").click()   # leave it as found
    page.wait_for_function("() => !document.getElementById('preview_all_rows').checked", timeout=10_000)
    wait_shiny(page, 30_000)


def test_rows_all_rows_and_hidden_columns(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _switch_all_rows(page, False)   # the page is shared by the tests of this module: start from the default, whatever the test before left
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
    _open_data_panel(page)
    items = page.locator("#preview_col_selector + .selectize-control .item")
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


RECORD = """() => { const t = document.querySelector('#home_data_preview_badge'); window.__badge_texts = [];
  window.__badge_obs && window.__badge_obs.disconnect();
  const keep = () => { const x = t.textContent.trim(); const l = window.__badge_texts; if (!l.length || l[l.length - 1] !== x) l.push(x); };
  window.__badge_obs = new MutationObserver(keep);
  window.__badge_obs.observe(t, {childList: true, subtree: true, characterData: true}); keep(); }"""


def _recorded(page: Page) -> list[str]:
    return page.evaluate("window.__badge_texts")


def test_the_badge_never_says_hidden_columns_the_user_did_not_hide_while_the_table_changes(page: Page, shiny_app: ShinyAppProc):
    """Every text the badge shows is recorded (a MutationObserver) while the viewed table changes; the chooser needs one to two seconds to be
    rebuilt for the new table, and in that time the badge must not say that columns are hidden (D-0050)."""
    _load_data_analysis_recipe(page, shiny_app.url)
    _switch_all_rows(page, False)
    set_mode(page, "exploration")
    _open_data_panel(page)
    # (a) Source to T1, three times, nothing hidden by the user
    for _ in range(3):
        set_view(page, "SRC")
        page.wait_for_timeout(1500)
        page.evaluate(RECORD)
        set_view(page, "T1")
        page.wait_for_timeout(2500)
        texts = _recorded(page)
        assert texts and not any("hidden" in t for t in texts), texts
    # (b) hide one column in T1; the sentence is true there; then switch to T2: no "hidden" in anything recorded after the switch
    items = page.locator("#preview_col_selector + .selectize-control .item")
    expect(items.first).to_be_visible(timeout=10_000)
    items.first.hover()
    items.first.locator(".remove").click()
    wait_shiny(page, 30_000)
    expect(page.locator(BADGE)).to_contain_text("1 column hidden")
    page.evaluate(RECORD)
    set_view(page, "T2")
    page.wait_for_timeout(2500)
    texts = _recorded(page)
    assert texts and not any("hidden" in t for t in texts[1:]) , texts   # texts[0] is what the badge showed at the start of the recording (T1, true)
    expect(items.first).to_be_visible(timeout=10_000)
    assert "hidden" not in page.locator(BADGE).inner_text()
    set_view(page, "T3")   # leave the page as the other tests of the module expect it
    wait_shiny(page, 30_000)


# The badge element is replaced when the recipe is switched, so the observer sits on the document body and reads EVERY badge element in
# the page at each change. A text counts as untrue only when its element is VISIBLE (offsetParent), says "hidden" and differs from the
# text shown before the switch (the browser re-binds the old text for about 70 ms; the server does not send it).
RECORD_BODY = """() => { window.__seen = []; window.__before = [...document.querySelectorAll('#home_data_preview_badge')].map(t => t.textContent.trim());
  window.__badge_obs && window.__badge_obs.disconnect();
  const keep = () => { for (const t of document.querySelectorAll('#home_data_preview_badge')) {
    window.__seen.push([t.offsetParent !== null, t.textContent.trim()]); } };
  window.__badge_obs = new MutationObserver(keep);
  window.__badge_obs.observe(document.body, {childList: true, subtree: true, characterData: true, attributes: true}); keep(); }"""

R1, R2, R3 = "1_test_data_ST22_dummy", "2_test_data_ST22_dummy", "3_test_no_joins"


def test_the_badge_never_says_hidden_columns_after_a_switch_of_recipe(page: Page, shiny_app: ShinyAppProc):
    """This browser test is a GUARD that catches the flash only some of the time (it depends on timing: the flash was seen about once in
    two to four switches of recipe 2 to 3). The PROOF of the rule is the headless test
    `test_a_chooser_built_for_another_recipe_gives_no_hidden_sentence_even_when_plot_and_view_are_equal`.

    A column is hidden before each switch; the switches alternate 2 to 3 and 3 to 2 several times (and the other pairs). No VISIBLE badge
    text after a switch may say "hidden" unless it is what the badge showed before the switch (D-0050).
    This test is the last of the module: it leaves the app on the recipe `1_test_data_ST22_dummy`, view T3, as the others expect."""
    _load_data_analysis_recipe(page, shiny_app.url)
    _switch_all_rows(page, False)
    set_mode(page, "exploration")
    _open_data_panel(page)
    set_view(page, "T3")
    wait_shiny(page, 30_000)
    for target in (R2, R1, R3, R1, R2, R3, R2, R3, R2, R3, R2, R3, R2, R1):
        items = page.locator("#preview_col_selector + .selectize-control .item")
        expect(items.first).to_be_visible(timeout=20_000)
        items.first.hover()
        items.first.locator(".remove").click()
        wait_shiny(page, 30_000)
        expect(page.locator(BADGE)).to_contain_text("hidden")
        page.evaluate(RECORD_BODY)
        _choose_recipe(page, target)
        page.wait_for_timeout(3000)
        seen = page.evaluate("window.__seen")
        before = page.evaluate("window.__before")
        untrue = [t for vis, t in seen if vis and "hidden" in t and t not in before]
        assert not untrue, (target, untrue, before)
        set_mode(page, "exploration")
        _open_data_panel(page)
        set_view(page, "T3")
        wait_shiny(page, 30_000)
