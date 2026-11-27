"""The step bar of HOME in Audit mode, in the browser (D-0663, D-0672; qa app features).

# @deps
# consumes: app/handlers/step_bar_handlers.py, app/handlers/trial_handlers.py, app/handlers/filter_and_audit_handlers.py, app/modules/step_bar.py, app/src/www/step_bar.js, config/ui/theme.css (section 33)
# @end_deps

What the design expects (and what is tested):
- the bar exists in Audit mode only, is a region labelled "Create an audit step", and its first line names the item shown (not the tab Exploration had); `pipeline-exploration-simple` has none;
- the form of a condition is mounted ONCE in the page in both modes (the ids `fb_col`, `fb_op`, `filter_rows_ui`, ... exist once): no duplicate id, which Shiny reports as a client error;
- one button Try for both kinds of step; the plain switch shows one part of the bar at a time; Try is off with a plain sentence when the step cannot be tried;
- a value typed in the form is kept across a Try and across the typing of the reason (neither draws the form again), and the trial survives the reason being typed;
- Discard folds the answer away; the fold-out can be folded and the table stays visible under it;
- at 1100 px with both side panels open the bar lies between the two panels' drag handles (no overlap) and its parts wrap;
- keyboard: the controls of the bar come in reading order (switch, Try, then the fold-out's controls).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_step_bar_browser.py -q
MUTATION (seen failing, then restored): the bar names the open Exploration tab instead of the item shown; `trial_handlers._try_step` ignores the kind (a drop is tried as a condition).
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import add_to_pipeline, choose_kind, set_mode, show_place, stage_condition, try_staged, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_audit_one_plot_browser import RECIPE, _enter_audit, ready  # noqa: F401  (the fixture that opens the demo recipe on the AMR heatmap)
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _wait_shiny

LAUNCH = os.environ.get("SPARMVET_APP_FEATURES", "developer")
NEEDS_AUDIT = pytest.mark.skipif(LAUNCH not in _INTERACTIVE_APP_FEATURES or LAUNCH == "pipeline-exploration-simple", reason="needs the audit")
NO_AUDIT = pytest.mark.skipif(LAUNCH != "pipeline-exploration-simple", reason="pipeline-exploration-simple only")
FORM_IDS = ("fb_col", "fb_op", "filter_rows_ui", "filter_form_ui", "filter_controls_ui", "filter_add_row", "filter_reset")


def _count_ids(page: Page, ids=FORM_IDS) -> dict:
    return page.evaluate("(ids) => Object.fromEntries(ids.map(i => [i, document.querySelectorAll('#' + i).length]))", list(ids))


@pytest.fixture(autouse=True)
def back_to_exploration(request):
    yield
    if "ready" in request.fixturenames:
        page = request.getfixturevalue("ready")
        try:
            if page.locator("#trial_discard").count():
                page.locator("#trial_discard").click()
                wait_shiny(page)
            set_mode(page, "exploration")
        except Exception:
            pass


@NEEDS_AUDIT
def test_the_bar_exists_in_audit_mode_only_is_a_labelled_region_and_names_the_item_shown(ready: Page):
    page = ready
    set_mode(page, "exploration")
    expect(page.locator(".spv-stepbar")).to_have_count(0)
    _enter_audit(page)
    bar = page.locator(".spv-stepbar")
    expect(bar).to_have_count(1, timeout=15_000)
    assert bar.get_attribute("role") == "region" and bar.get_attribute("aria-label") == "Create an audit step"
    show_place(page, "T1:ResFinder", keep_chosen=False)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: ResFinder: Table, T1", timeout=30_000)   # the item shown, not the open plot's tab
    assert page.locator("#shown_band_ui").evaluate("(e) => !!e.closest('.spv-stepbar')"), "the band is the first line of the bar"
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST Bar: Result data, T3", timeout=30_000)
    set_mode(page, "exploration")
    expect(page.locator(".spv-stepbar")).to_have_count(0, timeout=15_000)


@NEEDS_AUDIT
def test_the_form_is_mounted_once_in_both_modes_and_the_bar_holds_one_button_try(ready: Page):
    page = ready
    set_mode(page, "exploration")
    assert set(_count_ids(page).values()) == {1}, _count_ids(page)
    assert page.locator("#sidebar_filters #fb_col").count() == 1
    _enter_audit(page)
    expect(page.locator("#step_try")).to_have_count(1, timeout=15_000)
    assert set(_count_ids(page).values()) == {1}, f"an id of the form is mounted twice: {_count_ids(page)}"
    assert page.locator("#step_try, #filter_try, #col_drop_try").count() == 1, "one button Try"
    assert page.locator(".spv-stepbar #fb_col").count() == 0, "the form is in the Filters panel (the bar names the condition in words)"
    set_mode(page, "exploration")
    assert set(_count_ids(page).values()) == {1}, _count_ids(page)


@NEEDS_AUDIT
def test_the_switch_shows_one_kind_at_a_time_and_try_says_why_it_is_off(ready: Page):
    page = ready
    _enter_audit(page)
    inner = page.locator(".spv-stepbar-inner")
    expect(inner).to_have_attribute("data-kind", "filter", timeout=15_000)
    expect(page.locator(".spv-stepbar-condition")).to_be_visible()
    expect(page.locator(".spv-stepbar-drop")).to_be_hidden()
    expect(page.locator("#step_try")).to_be_disabled()
    expect(page.locator(".spv-stepbar-why")).to_contain_text("Add a condition row first")
    choose_kind(page, "drop")
    expect(page.locator(".spv-stepbar-condition")).to_be_hidden()
    expect(page.locator(".spv-stepbar-drop")).to_be_visible()
    expect(page.locator("#step_try")).to_be_disabled()
    expect(page.locator(".spv-stepbar-why")).to_contain_text("Deselect the columns to drop", timeout=15_000)    # the plot's Result data is shown on entering Audit: a drop is possible, nothing deselected yet
    show_place(page, "T1:ResFinder", keep_chosen=False)
    expect(page.locator(".spv-stepbar-why")).to_contain_text("Result data (T3) of a plot", timeout=30_000)     # a table is shown: a drop is tried at a plot's Result data only
    choose_kind(page, "filter")
    expect(page.locator(".spv-stepbar-condition")).to_be_visible()


@NEEDS_AUDIT
def test_a_drop_is_tried_and_added_from_the_bar_at_the_result_data_of_the_plot_shown(ready: Page):
    page = ready
    _enter_audit(page)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST Bar: Result data, T3", timeout=30_000)
    wait_shiny(page)
    page.evaluate("() => { const s = document.getElementById('preview_col_selector').selectize; s.removeItem(Object.keys(s.options)[0]); }")
    choose_kind(page, "drop")
    expect(page.locator(".spv-stepbar-drop")).to_contain_text("Drop the column", timeout=15_000)
    expect(page.locator("#step_try")).to_be_enabled(timeout=15_000)
    page.locator("#step_try").click()
    wait_shiny(page, 90_000)
    expect(page.locator(".spv-trial-panel")).to_contain_text("drops 1 column", timeout=60_000)
    add_to_pipeline(page, "a column nobody reads", expected_places=1)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Drop Column", timeout=20_000)


@NEEDS_AUDIT
def test_the_typed_value_and_the_trial_survive_a_try_and_the_typing_of_the_reason_and_the_fold_out_folds(ready: Page):
    """R4 in the browser: neither a Try nor typing the reason draws the form again, so the value typed in the Filters panel stays; folding the answer leaves the table visible."""
    page = ready
    _enter_audit(page)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST Bar: Result data, T3", timeout=30_000)
    stage_condition(page, "year", "gt", 2000)
    page.locator("#fb_value").fill("1234")                  # a value typed and not added: it must still be there after the Try and the reason
    page.wait_for_timeout(300)
    wait_shiny(page)
    choose_kind(page, "filter")
    page.locator("#step_try").click()
    wait_shiny(page, 90_000)
    panel = page.locator(".spv-trial-panel")
    expect(panel).to_be_visible(timeout=60_000)
    expect(page.locator("#fb_value")).to_have_value("1234")
    box = page.locator("input[id^='trial_reason_']")
    box.fill("because")
    box.press("Tab")
    wait_shiny(page)
    expect(page.locator("#fb_value")).to_have_value("1234")
    expect(panel).to_be_visible()                           # typing the reason keeps the trial
    expect(page.locator("#trial_add")).to_be_enabled(timeout=10_000)
    # the fold-out folds and the table under it stays visible
    page.locator(".spv-trial-panel > summary").click()
    expect(page.locator(".spv-trial-body")).to_be_hidden()
    expect(page.locator("#home_data_preview")).to_be_visible()
    # Discard ends the trial
    page.locator(".spv-trial-panel > summary").click()
    page.locator("#trial_discard").click()
    wait_shiny(page)
    expect(panel).to_have_count(0, timeout=15_000)


@NEEDS_AUDIT
def test_at_1100_px_the_bar_lies_between_the_two_panels_and_its_parts_do_not_overlap(ready: Page):
    page = ready
    page.set_viewport_size({"width": 1100, "height": 900})
    _enter_audit(page)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST Bar: Result data, T3", timeout=30_000)
    stage_condition(page, "year", "gt", 2000)
    try_staged(page)
    geometry = page.evaluate("""() => {
      const box = (e) => { const r = e.getBoundingClientRect(); return {l: r.left, r: r.right, t: r.top, b: r.bottom}; };
      const bar = box(document.querySelector('.spv-stepbar'));
      const handles = [...document.querySelectorAll('.bslib-sidebar-resize-handle')].map(box);
      const parts = ['#shown_band_ui', '.spv-stepbar-kind', '.spv-stepbar-condition', '.spv-stepbar-actions', '.spv-trial-panel'].map(s => document.querySelector(s)).filter(Boolean).map(box);
      return {bar, handles, parts, width: window.innerWidth, scrollW: document.documentElement.scrollWidth};
    }""")
    assert geometry["scrollW"] <= geometry["width"] + 1, "no horizontal page scroll"
    for h in geometry["handles"]:
        assert not (h["l"] < geometry["bar"]["r"] and h["r"] > geometry["bar"]["l"] and h["t"] < geometry["bar"]["b"] and h["b"] > geometry["bar"]["t"]), (h, geometry["bar"])
    for a, b in zip(geometry["parts"], geometry["parts"][1:]):
        assert a["b"] <= b["t"] + 1, f"the parts of the bar stack without overlap: {a} then {b}"
    page.set_viewport_size({"width": 1280, "height": 720})


@NEEDS_AUDIT
def test_the_controls_of_the_bar_come_in_reading_order_by_the_keyboard(ready: Page):
    page = ready
    _enter_audit(page)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST Bar: Result data, T3", timeout=30_000)
    stage_condition(page, "year", "gt", 2000)
    wait_shiny(page)
    order = page.evaluate("""() => [...document.querySelectorAll('.spv-stepbar input, .spv-stepbar button, .spv-stepbar summary')]
        .filter(e => e.offsetParent !== null && !e.disabled).map(e => e.id || e.name || e.tagName)""")
    assert order[:3] == ["step_kind", "step_kind", "step_try"], order        # the switch (both radios) comes before Try
    try_staged(page)
    order = page.evaluate("""() => [...document.querySelectorAll('.spv-stepbar input, .spv-stepbar button, .spv-stepbar summary')]
        .filter(e => e.offsetParent !== null && !e.disabled).map(e => e.id || e.name || e.tagName)""")
    assert order.index("step_try") < order.index("SUMMARY") < order.index("trial_discard"), order    # Try, then the fold-out, then its controls
    labels = page.evaluate("() => [...document.querySelectorAll('.spv-stepbar input[type=radio], .spv-stepbar input[type=text]')].every(e => !!(e.labels && e.labels.length) || !!e.getAttribute('aria-label'))")
    assert labels, "every control of the bar has a label"


@NO_AUDIT
def test_without_the_audit_there_is_no_bar(page: Page, shiny_app: ShinyAppProc):
    page.goto(shiny_app.url)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=90_000)
    _wait_shiny(page, 60_000)
    assert page.locator(".spv-stepbar").count() == 0 and page.locator("#step_try").count() == 0
