"""One plot area in Audit mode, no plot tabs (slice 3b of the new Audit flow; D-0657, D-0655, D-0634, D-0341, D-0302).

Run (qa app features: every flag on, ghost save off; the file runs about five minutes on an idle machine):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_one_plot_browser.py -q

# @deps
# consumes: app/handlers/home_theater.py (home_plots_area_ui, the open plot, compare_switch_ui), app/handlers/audit_stack.py (the right panel), app/modules/audit_shown.py (the words), app/handlers/lineage_handlers.py (Show), app/tests/browser_view.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0657, D-0655, D-0634, D-0341, D-0302, D-0327)
# @end_deps

The design expects (header-strip design page of 2026-11-26, second update, decision 5): in Audit mode there are no group tabs and no plot tabs. ONE plot area shows the item shown: a plot is
drawn (the audited plot, with the Compare switch above it and, for a plot with a random layer, its Reshuffle button); a table is not a figure: the area says so, names the plots built from it
and has no Compare. Exploration keeps its tabs, and has the tab it had when Audit mode is left. The plot shown IS the open plot: a step written from the screen is written at it, whatever tab
Exploration had. The right panel (Pipeline Audit) follows the item shown.

What a person does and sees, on the demo `1_test_data_ST22_dummy` (Exploration is left on the tab "AMR Heatmap"):
- Audit mode: no tab navigation is on the page; the plot of the tab Exploration had is drawn, named "Plot shown: AMR Heatmap"; leaving Audit gives the tabs back, on "AMR Heatmap";
- Show of another plot swaps the figure: the first plot is no longer on the page (it is not drawn), the second is; Compare labels the panes of the plot shown;
- Show of a table: no figure, a note that says it is a table and names the plots built from it, no Compare switch; showing a plot again brings both back;
- the right panel names the item shown and lists the steps written at that table or above it; for a plot the steps it is built from;
- a step added (Try, then Add to audit pipeline) goes to the plot SHOWN (which was not the tab of Exploration), and not to the tab's plot;
- a table shown offers a Try on a staged condition, but no drop (a drop is tried at a plot's Result data (T3)) (no plot is open);
- a restored session opens in Audit mode with the open plot of the tab shown.

Mutation index (each seen failing): MUTATION C1 `_audit_default_plot` and the open plot ignore the shown item (the first test of Show); MUTATION C2 `_sync_open_plot` writes the tab of Exploration
in Audit mode (the test of the step added at the plot shown).
"""
import os
import re
from pathlib import Path

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import add_to_pipeline, preview_rows, set_compare, set_mode, show_place, try_staged, wait_preview_rows, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_lineage_view_browser import _clear_choice, _line, _open_panel
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _choose_fb_op, _load_data_analysis_recipe, _open_filters_panel, _wait_shiny

LAUNCH = os.environ.get("SPARMVET_APP_FEATURES", "developer")
NEEDS_AUDIT = pytest.mark.skipif(LAUNCH not in _INTERACTIVE_APP_FEATURES or LAUNCH == "pipeline-exploration-simple", reason="needs the audit")
RECIPE = "1_test_data_ST22_dummy"
ROOT = Path(__file__).resolve().parents[2]
AREA = ".spv-audit-plot-area"


@pytest.fixture(scope="module")
def tables(tmp_path_factory):
    """The tables the test looks at, from the engine's own reads (computed here, not typed in)."""
    from app.modules.orchestrator import DataOrchestrator
    orch = DataOrchestrator(ROOT / "config" / "data_analysis_recipes" / "pipelines", ROOT / "assets" / "test_data")
    where = tmp_path_factory.mktemp("one_plot")
    return {"amr_heatmap": orch.materialize_tier3(RECIPE, "amr_heatmap", where).collect(),
            "mlst_bar": orch.materialize_tier3(RECIPE, "mlst_bar", where).collect(),
            "ResFinder": orch.materialize_tier1(RECIPE, "ResFinder", where / "ResFinder.parquet").collect()}


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url, RECIPE)
    _open_filters_panel(page)
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)
    yield page


@pytest.fixture(autouse=True)
def back_to_exploration(request):
    """Every test leaves the page in Exploration, so that the next one starts from the same place."""
    yield
    if "ready" in request.fixturenames:
        page = request.getfixturevalue("ready")
        try:
            if page.locator("#trial_discard").count():
                page.locator("#trial_discard").click()
                wait_shiny(page)
            for b in page.locator("[id^='t3_delete_']").all():
                b.click()
                wait_shiny(page)
            set_mode(page, "exploration")
        except Exception:
            pass


def _enter_audit(page: Page) -> None:
    set_mode(page, "audit")
    _open_panel(page)
    _clear_choice(page)
    wait_shiny(page)


def _no_tabs(page: Page) -> None:
    expect(page.locator("#home_groups_nav")).to_have_count(0, timeout=15_000)
    expect(page.locator("[id^='subtabs_']")).to_have_count(0)


def _stage_year_filter(page: Page, threshold: float) -> None:
    _choose_column_firmly(page, "year")
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill(repr(threshold))
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)


@NEEDS_AUDIT
def test_audit_mode_has_no_tabs_and_exploration_gets_its_tab_back(ready: Page):
    page = ready
    expect(page.locator("#home_groups_nav")).to_have_count(1)
    set_mode(page, "audit")
    _no_tabs(page)
    expect(page.locator(AREA)).to_contain_text("Plot shown: AMR Heatmap", timeout=30_000)
    expect(page.locator("#plot_group_amr_heatmap")).to_be_visible(timeout=30_000)
    set_mode(page, "exploration")
    expect(page.locator("#home_groups_nav")).to_have_count(1, timeout=15_000)
    expect(page.locator(AREA)).to_have_count(0)
    active = page.locator("[id^='subtabs_'] .nav-link.active:visible")
    expect(active.first).to_contain_text("AMR Heatmap", timeout=15_000)
    expect(page.locator("#plot_group_amr_heatmap")).to_be_visible(timeout=30_000)


@NEEDS_AUDIT
def test_the_exploration_tab_is_kept_when_audit_mode_showed_other_plots(ready: Page):
    page = ready
    _enter_audit(page)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator(AREA)).to_contain_text("Plot shown: MLST Bar", timeout=30_000)
    set_mode(page, "exploration")
    expect(page.locator("[id^='subtabs_'] .nav-link.active:visible").first).to_contain_text("AMR Heatmap", timeout=15_000)
    expect(page.locator("#plot_group_mlst_bar")).not_to_be_visible()          # a tab that is not open: its pane may hold what was drawn before, it is not on screen
    set_mode(page, "audit")
    expect(page.locator(AREA)).to_contain_text("Plot shown: AMR Heatmap", timeout=30_000)     # entering Audit again: nothing shown, the default plot


@NEEDS_AUDIT
def test_show_of_another_plot_swaps_the_figure_and_compare_labels_the_plot_shown(ready: Page, tables):
    page = ready
    _enter_audit(page)
    expect(page.locator("#plot_group_amr_heatmap")).to_be_visible(timeout=30_000)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#plot_group_mlst_bar")).to_be_visible(timeout=30_000)
    expect(page.locator("#plot_group_amr_heatmap")).to_have_count(0, timeout=15_000)          # the plot not shown is not on the page: it is not drawn
    wait_preview_rows(page, tables["mlst_bar"].height, timeout=60_000)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST Bar: Result data, T3", timeout=30_000)
    set_compare(page, True)
    expect(page.locator("[id='plot_group_mlst_bar_cmp_base']")).to_be_visible(timeout=30_000)
    expect(page.locator(AREA)).to_contain_text("Original (before your audit steps)")
    expect(page.locator(AREA)).to_contain_text("Audited (no steps yet)")
    show_place(page, "T3:amr_heatmap", keep_chosen=False)
    expect(page.locator("[id='plot_group_amr_heatmap_cmp_base']")).to_be_visible(timeout=30_000)
    expect(page.locator("#plot_group_mlst_bar_cmp_base")).to_have_count(0, timeout=15_000)
    set_compare(page, False)


@NEEDS_AUDIT
def test_a_table_shown_gives_a_note_no_figure_and_no_compare(ready: Page, tables):
    page = ready
    _enter_audit(page)
    expect(page.locator("#audit_compare")).to_be_attached(timeout=15_000)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    wait_preview_rows(page, tables["ResFinder"].height, timeout=60_000)
    area = page.locator(AREA)
    expect(area).to_contain_text("No figure: ResFinder: Table, T1 is a table", timeout=30_000)
    expect(area).to_contain_text("AMR Heatmap")                                                # the plots built from it, as information
    expect(page.locator("[id^='plot_group_']")).to_have_count(0)
    expect(page.locator("#audit_compare")).to_have_count(0, timeout=15_000)                    # absent, not greyed
    assert page.locator(f"{AREA} button").count() == 0, "the names are information, not buttons to tick"
    show_place(page, "T3:amr_heatmap", keep_chosen=False)
    expect(page.locator("#plot_group_amr_heatmap")).to_be_visible(timeout=30_000)
    expect(page.locator("#audit_compare")).to_be_attached(timeout=15_000)


@NEEDS_AUDIT
def test_a_table_no_plot_reads_says_that_no_plot_is_built_from_it(ready: Page):
    page = ready
    _enter_audit(page)
    show_place(page, "T1:Quality_metrics", keep_chosen=False)
    expect(page.locator(AREA)).to_contain_text("No plot is built from it.", timeout=30_000)
    expect(page.locator("[id^='plot_group_']")).to_have_count(0)


@NEEDS_AUDIT
def test_a_table_shown_offers_a_condition_try_and_no_drop_and_the_plot_shown_offers_both(ready: Page):
    """The one button Try of the step bar: with a table shown a column drop is refused in a plain line (it is tried at the Result data (T3) of a plot only); with the plot's Result data shown it is offered."""
    from app.tests.browser_view import choose_kind
    page = ready
    _enter_audit(page)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    assert page.locator("#filter_send_to_audit").count() == 0
    expect(page.locator("#filter_controls_ui")).to_contain_text("press Try", timeout=15_000)
    choose_kind(page, "drop")
    expect(page.locator("#step_try")).to_be_disabled(timeout=15_000)
    expect(page.locator(".spv-stepbar-why")).to_contain_text("Result data (T3) of a plot", timeout=15_000)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator(".spv-stepbar-why")).to_contain_text("Deselect the columns to drop", timeout=15_000)      # offered; nothing deselected yet
    page.evaluate("() => { const s = document.getElementById('preview_col_selector').selectize; s.removeItem(Object.keys(s.options)[0]); }")
    expect(page.locator("#step_try")).to_be_enabled(timeout=15_000)


@NEEDS_AUDIT
def test_a_step_is_added_at_the_plot_shown_not_at_the_tab_exploration_had(ready: Page, tables):
    page = ready
    _enter_audit(page)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    wait_preview_rows(page, tables["mlst_bar"].height, timeout=60_000)
    year = tables["mlst_bar"]["year"].drop_nulls()
    threshold = float(year.unique().sort()[len(year.unique()) // 2])
    kept = tables["mlst_bar"].filter(pl.col("year") < threshold).height
    assert 0 < kept < tables["mlst_bar"].height
    _stage_year_filter(page, threshold)
    try_staged(page)
    add_to_pipeline(page, "one plot: the plot shown, not the tab", expected_places=1)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at MLST Bar: Result data, T3", timeout=20_000)
    wait_preview_rows(page, kept, timeout=60_000)                                              # the rows of the plot shown went down by the rows the filter removes
    show_place(page, "T3:amr_heatmap", keep_chosen=False)
    wait_preview_rows(page, tables["amr_heatmap"].height, timeout=60_000)                       # the plot of the tab of Exploration is untouched
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("No T3 adjustments", timeout=15_000)
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at MLST Bar: Result data, T3", timeout=15_000)


@NEEDS_AUDIT
def test_the_right_panel_follows_the_item_shown_for_a_plot_and_for_a_table(ready: Page, tables):
    page = ready
    _enter_audit(page)
    panel = page.locator("#audit_nodes_tier3")
    expect(panel).to_contain_text("My Adjustments", timeout=15_000)
    expect(panel).to_contain_text("AMR Heatmap")
    show_place(page, "T1:ResFinder", keep_chosen=False)
    expect(panel).to_contain_text("ResFinder: Table, T1", timeout=15_000)                        # the heading names the table as the lineage does
    expect(panel).to_contain_text("No audit steps are written at ResFinder: Table, T1 or above it yet")
    expect(page.locator("#audit_nodes_header_ui")).to_contain_text("Collection: ResFinder")
    show_place(page, "T3:mlst_bar", keep_chosen=False)
    expect(panel).to_contain_text("MLST Bar", timeout=15_000)
    assert "ResFinder" not in panel.inner_text()
