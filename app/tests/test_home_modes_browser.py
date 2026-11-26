"""The header strip of HOME in the browser (slice B): the two modes, the four-value data choice, the Source list, the clearing notice.

Run (qa app features: every flag on, ghost save off):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_home_modes_browser.py -q

What a person sees:
- Exploration is the start: a mode switch with Exploration and Audit; the data choice Source, T1, T2, T3 starting on T3; no Compare switch;
- Source shows a second list with the source tables that feed the open plot, the table as read from its file, and a badge that says so;
- a filter applied in Exploration changes the table only; changing the table to view clears the filter and says so; changing nothing says nothing;
- in Audit mode Compare appears (the original and the audited plot), and "Send to Audit" is offered only while T3 is viewed, with one plain
  line on the other tables; switching the mode removes exploration filters, with the notice.
"""
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_compare, set_mode, set_source, set_view, show_place
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _load_data_analysis_recipe, _open_filters_panel, _wait_shiny

NOTICE = "#shiny-notification-panel"
PLOT_TAB = ".nav-link:has-text('QC Reads Horizontal Barplot')"


def _ready(page: Page, url: str) -> None:
    _load_data_analysis_recipe(page, url)
    _open_filters_panel(page)
    page.locator(PLOT_TAB).first.click()
    _wait_shiny(page)
    set_mode(page, "exploration")
    set_view(page, "T3")
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


def _apply_a_filter(page: Page) -> None:
    page.locator("#fb_col").select_option(index=1)
    _wait_shiny(page)
    page.locator("#fb_op").select_option("ne")
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    expect(page.locator("#home_data_preview_badge .spv-view-note", has_text="preview filter")).to_be_visible(timeout=15_000)


def _close_notices(page: Page) -> None:
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


def test_the_strip_starts_in_exploration_on_t3_with_no_compare(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    expect(page.locator("#home_mode input[value=exploration]")).to_be_checked()
    expect(page.locator("#data_view input[value=T3]")).to_be_checked()
    assert [e for e in page.locator("#data_view input").evaluate_all("els => els.map(e => e.value)")] == ["SRC", "T1", "T2", "T3"]
    assert page.locator("#audit_compare").count() == 0, "Compare lives in Audit mode only"
    assert page.locator("#plot_view, #tier_toggle").count() == 0, "the two old choices are gone"
    body = page.locator("body").inner_text()
    for old in ("My view", "Plot to show", "Data to show"):
        assert old not in body, old


def test_source_lists_the_tables_that_feed_the_plot_and_shows_the_table_as_read(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    expect(page.locator("#source_table")).to_have_count(0, timeout=10_000)   # "the second list appears only with Source" (the removal after a change of view is not instant)
    set_view(page, "SRC")
    expect(page.locator("#source_table")).to_be_visible(timeout=10_000)
    tables = page.locator("#source_table option").evaluate_all("els => els.map(e => e.value)")
    assert tables, "at least one source table feeds the plot"
    for table in tables:
        set_source(page, table)
        expect(page.locator("#home_data_preview_badge .spv-view-badge")).to_have_text("Viewing: Source", timeout=15_000)
        expect(page.locator("#home_data_preview_badge")).to_contain_text(f"table '{table}'")
        expect(page.locator("#home_data_preview tbody tr").first).to_be_visible(timeout=20_000)
    set_view(page, "T3")
    expect(page.locator("#source_table")).to_have_count(0, timeout=10_000)


@pytest.mark.parametrize("change", ["data", "plot", "mode"])
def test_a_filter_is_cleared_with_a_notice_when_the_viewed_table_changes(page: Page, shiny_app: ShinyAppProc, change):
    _ready(page, shiny_app.url)
    _apply_a_filter(page)
    _close_notices(page)
    if change == "data":
        set_view(page, "T1")
    elif change == "plot":
        other = page.locator("[id^='subtabs_'] .nav-link:visible").filter(has_not_text="QC Reads Horizontal Barplot").first
        expect(other).to_be_visible(timeout=10_000)   # another plot tab of the same group
        other.click()
        _wait_shiny(page)
    else:
        set_mode(page, "audit")
    expect(page.locator(NOTICE)).to_contain_text("The filters were removed", timeout=15_000)
    expect(page.locator("#filter_remove_0")).to_have_count(0)
    set_mode(page, "exploration")
    set_view(page, "T3")


def test_no_notice_when_there_is_no_filter_to_clear(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    _close_notices(page)
    for view in ("T1", "T2", "SRC", "T3"):
        set_view(page, view)
    set_mode(page, "audit")
    set_mode(page, "exploration")
    page.wait_for_timeout(1_000)   # the absence of a notice needs a time window: a notice would come with the change
    shown = page.evaluate("() => (document.getElementById('shiny-notification-panel') || {innerText: ''}).innerText")
    assert "The filters were removed" not in shown, shown


def test_audit_mode_has_compare_and_offers_send_to_audit_on_t3_only(page: Page, shiny_app: ShinyAppProc):
    _ready(page, shiny_app.url)
    set_mode(page, "audit")
    try:
        expect(page.locator("#audit_compare")).to_be_attached(timeout=10_000)
        expect(page.locator("body")).not_to_contain_text("Audit steps apply to the plot's table (T3) for now.")
        # Compare on: the original and the audited plot side by side; off: the audited plot alone
        set_compare(page, True)
        expect(page.locator("[id$='_cmp_base'].shiny-plot-output").first).to_be_visible(timeout=20_000)
        set_compare(page, False)
        expect(page.locator("[id$='_cmp_base'].shiny-plot-output")).to_have_count(0, timeout=15_000)
        # the form builds audit steps: no Apply; Send to Audit only while T3 is viewed
        set_view(page, "T3")
        expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
        expect(page.locator("#filter_apply")).to_have_count(0)
        # Audit mode has no "Table to view" (slice 3a): another table is shown from Path of the data
        expect(page.locator("#data_view")).to_have_count(0)
        page.wait_for_selector("#lineage_root .spv-lin-line", timeout=30_000)
        a_table = page.locator("#lineage_root .spv-lin-line[data-id^='T1:']:not(.not-choosable)").first.get_attribute("data-id")
        show_place(page, a_table)
        expect(page.locator("#filter_send_to_audit")).to_have_count(0, timeout=10_000)
        expect(page.locator("#filter_controls_ui")).to_contain_text("To create an audit step, show the Result data (T3) of the open plot")
    finally:
        set_mode(page, "exploration")
        set_view(page, "T3")


def test_no_reshuffle_button_in_exploration(page: Page, shiny_app: ShinyAppProc):
    """D-0341: Reshuffle belongs to Audit mode. In Exploration no plot offers it, whatever is stored. The positive side, with a plot that has a
    random layer and no written seed, and the stored pin that Exploration ignores, is `test_shiny_seed_places.py`."""
    _ready(page, shiny_app.url)
    set_mode(page, "exploration")
    expect(page.locator("[id^='plot_reshuffle_btn_']")).to_have_count(0)
