"""The mode row of HOME and the Compare switch in the browser (slice 1 of the header strip, 2026-11-26, PROVISIONAL words).

Run (qa app features: every flag on, ghost save off; the two other app kinds start an app of their own):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_home_mode_row_browser.py -q

# @deps
# consumes: app/handlers/home_theater.py (the mode row in dynamic_tabs, output mode_caption_ui, output compare_switch_ui, output plot_cmp_label_{p_id}), config/ui/theme.css (section 30), app/tests/gate_stage.py
# doc: .claude/rules/ui_implementation_contract.md#2
# @end_deps

What a person sees:
- the title of the recipe and the control "Exploration | Audit" in one row of their own above the strip "Table to view"; the control is a labelled group of two
  radios, the open mode is told by a tick in text and by colour, the keyboard changes it; a caption says what the mode does;
- Compare is ONE switch above the plots, only in Audit mode (with the comparison flag), and a click on it changes nothing else: the open plot accordion keeps its
  state, the lineage panel and the "Table to view" radios are the same page elements before and after (R4);
- at 1100 px with both side panels open the control stays on the title's line; a title too long for the row is cut, the control does not wrap;
- an app whose deployment hides the recipe name has the row with the control alone; an app without the audit has no control and the title alone.
"""
import pytest
from playwright.sync_api import Browser, Page, expect
from shiny.run import ShinyAppProc

from app.tests import gate_stage as g
from app.tests.browser_view import set_compare, set_mode
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _load_data_analysis_recipe, _wait_shiny



def _ready(page: Page, url: str) -> None:
    _load_data_analysis_recipe(page, url)
    set_mode(page, "exploration")


def _mark(page: Page, selector: str) -> None:
    page.evaluate("(sel) => { document.querySelector(sel).__spv_mark = 'same'; }", selector)


def _still_marked(page: Page, selector: str) -> bool:
    return page.evaluate("(sel) => { const e = document.querySelector(sel); return !!e && e.__spv_mark === 'same'; }", selector)


def test_the_row_holds_the_title_and_a_labelled_two_state_control_above_the_strip(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    row = page.locator(".spv-mode-row")
    expect(row.locator(".banner-title")).to_be_visible()
    group = page.get_by_role("radiogroup", name="Mode")
    expect(group).to_be_visible()
    assert page.locator("#home_mode input[type=radio]").evaluate_all("els => els.map(e => e.value)") == ["exploration", "audit"]
    strip = page.locator(".theater-header-strip")
    assert row.bounding_box()["y"] + row.bounding_box()["height"] <= strip.bounding_box()["y"] + 1, "the row is above the strip"
    assert page.locator(".theater-header-strip #home_mode").count() == 0 and "Mode:" not in strip.inner_text(), "the radios left the strip"
    expect(page.locator("#data_view")).to_have_count(1)
    expect(row).to_contain_text("Nothing here is saved")
    assert page.locator("#audit_compare").count() == 0, "Compare is not in Exploration"


def test_the_open_mode_is_told_by_a_tick_and_the_keyboard_changes_it(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    ticks = "() => Array.from(document.querySelectorAll('#home_mode label.radio-inline > span')).map(s => getComputedStyle(s, '::before').content)"
    marks = page.evaluate(ticks)
    assert "✓" in marks[0] and "✓" not in marks[1], marks
    page.locator("#home_mode input[value=exploration]").focus()
    page.keyboard.press("ArrowRight")
    expect(page.locator("#home_mode input[value=audit]")).to_be_checked(timeout=10_000)
    _wait_shiny(page)
    marks = page.evaluate(ticks)
    assert "✓" in marks[1] and "✓" not in marks[0], marks
    expect(page.locator(".spv-mode-row")).to_contain_text("change the plot and the export")
    set_mode(page, "exploration")


def test_compare_is_one_switch_above_the_plots_in_audit_mode_only(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    expect(page.locator("#audit_compare")).to_have_count(0)
    set_mode(page, "audit")
    try:
        expect(page.locator("#audit_compare")).to_be_attached(timeout=10_000)
        assert page.locator("input#audit_compare").count() == 1, "one switch for the whole plot area, not one per plot"
        expect(page.locator(".spv-compare-line")).to_contain_text("Compare with the original")
        assert page.locator("body").inner_text().count("Audit steps apply to the plot's table") == 0
        line, tabs = page.locator(".spv-compare-line").bounding_box(), page.locator("#home_groups_nav").bounding_box()
        assert line["y"] + line["height"] <= tabs["y"] + 1, "the switch is above the group tabs"
        set_compare(page, True)
        expect(page.locator("[id$='_cmp_base'].shiny-plot-output").first).to_be_visible(timeout=20_000)
        body = page.locator("body")
        expect(body).to_contain_text("Original (before your audit steps)")
        expect(body).to_contain_text("Audited (no steps yet)")
        set_compare(page, False)
        expect(page.locator("[id$='_cmp_base'].shiny-plot-output")).to_have_count(0, timeout=15_000)
    finally:
        set_compare(page, False) if page.locator("#audit_compare").count() else None
        set_mode(page, "exploration")
    expect(page.locator("#audit_compare")).to_have_count(0, timeout=10_000)


def test_a_click_on_the_switch_or_the_mode_redraws_neither_the_strip_nor_the_lineage_nor_folds_the_plot(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    _mark(page, "#data_view")
    _mark(page, "#home_mode")
    set_mode(page, "audit")
    try:
        expect(page.locator("#lineage_root")).to_be_attached(timeout=20_000)
        _mark(page, "#lineage_root")
        _mark(page, "#audit_compare")
        opened = page.locator(".spv-plot-accordion .accordion-collapse.show").count()
        assert opened >= 1, "the open plot is unfolded"
        set_compare(page, True)
        _wait_shiny(page)
        set_compare(page, False)
        _wait_shiny(page)
        assert page.locator(".spv-plot-accordion .accordion-collapse.show").count() >= 1, "the plot stays unfolded"
        for selector in ("#data_view", "#home_mode", "#lineage_root", "#audit_compare"):
            assert _still_marked(page, selector), f"{selector} was drawn again"
    finally:
        set_mode(page, "exploration")
    assert _still_marked(page, "#data_view") and _still_marked(page, "#home_mode"), "the strip and the control survive a round trip of the mode"


@pytest.mark.parametrize("width", [1100, 1300])
def test_the_control_stays_on_the_title_line_and_a_long_title_is_cut(page: Page, shiny_app: ShinyAppProc, width):
    _ready(page, shiny_app.url)
    set_mode(page, "audit")     # the right panel is open in Audit mode: the narrowest centre
    original = page.viewport_size
    try:
        page.set_viewport_size({"width": width, "height": 1000})
        _wait_shiny(page)
        line = "() => { const t = document.querySelector('.spv-mode-row .banner-title').getBoundingClientRect(); const c = document.querySelector('#home_mode').getBoundingClientRect(); const r = document.querySelector('.spv-mode-row').getBoundingClientRect(); return {t, c, r, tm: (t.top + t.bottom) / 2, cm: (c.top + c.bottom) / 2}; }"
        got = page.evaluate(line)
        assert abs(got["tm"] - got["cm"]) < 14, f"the control is on the title's line: {got}"
        assert got["t"]["right"] <= got["c"]["left"] + 1 and got["c"]["right"] <= got["r"]["right"] + 1, got
        long_title = "A recipe title that is much too long for the row it sits in " * 4
        page.evaluate("(text) => { document.querySelector('.spv-mode-row .banner-title').textContent = text; }", long_title)
        cut = page.evaluate("() => { const e = document.querySelector('.spv-mode-row .banner-title'); const c = document.querySelector('#home_mode').getBoundingClientRect(); const r = document.querySelector('.spv-mode-row').getBoundingClientRect(); return {over: e.scrollWidth > e.clientWidth, ellipsis: getComputedStyle(e).textOverflow, cright: c.right, rright: r.right, ctop: c.top, etop: e.getBoundingClientRect().top, eh: e.getBoundingClientRect().height}; }")
        assert cut["over"] and cut["ellipsis"] == "ellipsis", cut
        assert cut["cright"] <= cut["rright"] + 1 and abs(cut["ctop"] - cut["etop"]) < 20, f"the control did not wrap below the cut title: {cut}"
    finally:
        page.set_viewport_size(original)
        set_mode(page, "exploration")


def test_with_the_recipe_name_hidden_the_row_holds_the_control_alone(browser: Browser, tmp_path):
    with g.running_app(tmp_path, deployment_extra={"branding": {"show_recipe_name": False}}) as (url, _log):
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        try:
            page.goto(url)
            page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
            _wait_shiny(page)
            expect(page.locator(".spv-mode-row #home_mode")).to_be_visible(timeout=30_000)
            assert page.locator(".banner-title").count() == 0, "no recipe name is shown"
            box, row = page.locator("#home_mode").bounding_box(), page.locator(".spv-mode-row").bounding_box()
            assert box["x"] + box["width"] > row["x"] + row["width"] - 60, "the control sits at the right of its row"
            set_mode(page, "audit")
            expect(page.locator("#audit_compare")).to_be_attached(timeout=10_000)
        finally:
            page.close()


def test_without_the_audit_there_is_no_control_and_the_title_stays(browser: Browser, tmp_path):
    with g.running_app(tmp_path, features="pipeline-exploration-simple") as (url, _log):
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        try:
            page.goto(url)
            page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
            _wait_shiny(page)
            expect(page.locator(".banner-title").first).to_be_visible(timeout=30_000)
            assert page.locator("#home_mode").count() == 0 and page.locator(".spv-mode-row").count() == 0, "no mode control without the audit"
            assert page.locator("#audit_compare").count() == 0 and page.locator(".spv-compare-line").count() == 0
            expect(page.locator("#data_view")).to_have_count(1)
        finally:
            page.close()
