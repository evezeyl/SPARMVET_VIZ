"""An audit step written at a table upstream of the plot, in the browser (HOME audit, demo step 3): the dialog, the audit panel, the plots, Compare, Remove.

Run (qa app features: every flag on, ghost save off):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_places_browser.py -q

What a person does on the demo `1_test_data_ST22_dummy`, and sees (D-0535: "the user must be able to choose, through the scope, where the step is added"):
- on the plot "AMR Heatmap" (built from the ResFinder table) in Audit mode, T3: a filter `identity < 99` is sent to audit; the dialog offers, besides the three
  plot-level choices, "At a table this plot is built from", with the table ResFinder at tier 1 and tier 2 and how many tables and plots are built from each;
- a choice that breaks the rule (the tier 1 and the tier 2 of the same table: one below the other) is refused in one plain line and the dialog stays open; no table ticked is refused;
- with the tier 1 of ResFinder ticked, a reason, Apply: the audit panel says "Written at Table ResFinder (tier 1)"; the data table of the plot has fewer rows than before; the plot's badge
  says the step was written upstream and that its table changed;
- the plot "MLST Bar" (a plot beside ResFinder) has no audited step and the same rows as before; its badge says so;
- Compare shows the Original and the Audited pane of the AMR plot; the data table of the AMR plot in T1 shows the original (it is not audited);
- "Remove step" (the bin of the card) gives every plot its original table back.

Mutation index (each seen failing): MUTATION B1 `_audited_t3_lf` returns None (HOME never reads the audited table: the rows do not drop); MUTATION B2 `choice_problem` skips the rule (the nested choice is accepted).
"""
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import preview_rows, set_compare, set_mode, set_view, wait_preview_rows, wait_preview_rows_below
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_shiny_smoke import (_load_data_analysis_recipe, _navigate_to_mlst_plot, _open_filters_panel, _choose_fb_op, _wait_shiny)

NOTICE = "#shiny-notification-panel"
REASON = "keep only the hits with an identity below 99 for this check"


@pytest.fixture(scope="module")
def expected(tmp_path_factory):
    """The rows the data tables must have, computed in this process from the same recipe and data (the engine builds the original tables)."""
    import polars as pl
    from pathlib import Path
    from app.modules.orchestrator import DataOrchestrator
    root = Path(__file__).resolve().parents[2]
    orch = DataOrchestrator(root / "config" / "data_analysis_recipes" / "pipelines", root / "assets" / "test_data")
    folder = tmp_path_factory.mktemp("expected")
    amr = orch.materialize_tier3("1_test_data_ST22_dummy", "amr_heatmap", folder).collect()
    mlst = orch.materialize_tier3("1_test_data_ST22_dummy", "mlst_bar", folder).collect()
    return {"amr_before": amr.height, "amr_after": amr.filter(pl.col("identity") < 99).height, "mlst": mlst.height}


def _amr_plot(page: Page) -> None:
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)


def _close_notices(page: Page) -> None:
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


def _send_filter(page: Page) -> None:
    _choose_column_firmly(page, "identity")
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill("99")
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)


def _tick(page: Page, place: str, on: bool = True) -> None:
    page.locator(f"#propagation_places input[value='{place}']").set_checked(on, force=True)


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    _amr_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    yield page
    set_mode(page, "exploration")


def test_the_dialog_offers_the_tables_the_plot_is_built_from_and_refuses_a_nested_choice(ready: Page, expected):
    page = ready
    assert preview_rows(page) > 50
    _send_filter(page)
    expect(page.locator("#propagation_choice input[value=place]")).to_have_count(1)
    labels = page.locator("#propagation_choice").inner_text()
    assert "This plot only" in labels and "All plots" in labels and "At a table this plot is built from" in labels
    assert page.locator("#propagation_choice input[value=this]").is_checked(), "it opens on 'This plot only', as before"
    expect(page.locator("#propagation_places_wrapper")).to_be_hidden()
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    text = page.locator("#propagation_places_wrapper").inner_text()
    assert "Table ResFinder (tier 1)" in text and "Table ResFinder (tier 2)" in text
    assert "built from it" in text and "changed" not in text.split("Choose one table")[-1], text
    assert page.locator("#propagation_places input[value='T1:ResFinder']").count() == 1
    # nothing ticked: refused
    page.locator("#propagation_confirm").click()
    expect(page.locator(NOTICE)).to_contain_text("Choose at least one table", timeout=10_000)
    expect(page.locator("#propagation_confirm")).to_be_visible()
    _close_notices(page)
    # the tier 1 and the tier 2 of one table: one below the other, refused in one line, the dialog stays
    _tick(page, "T1:ResFinder")
    _tick(page, "T2:ResFinder")
    page.locator("#propagation_confirm").click()
    expect(page.locator(NOTICE)).to_contain_text("lies below", timeout=10_000)
    expect(page.locator("#propagation_confirm")).to_be_visible()
    assert page.locator('input[id^="t3_reason_"]').count() == 0, "nothing was staged"
    _close_notices(page)
    page.keyboard.press("Escape")
    expect(page.locator("#propagation_confirm")).to_have_count(0, timeout=5_000)


def test_a_filter_at_tier1_of_resfinder_changes_the_plots_below_and_not_the_plot_beside_and_remove_gives_it_back(ready: Page, expected):
    page = ready
    rows_before = expected["amr_before"]
    wait_preview_rows(page, rows_before, timeout=30_000)
    _send_filter(page)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    _tick(page, "T1:ResFinder")
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    # staged, with the place named, waiting for its reason
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=15_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at Table ResFinder (tier 1)", timeout=10_000)
    expect(page.locator("#btn_apply").first).to_be_disabled()
    box = page.locator('input[id^="t3_reason_"]').first
    box.fill(REASON)
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    # the plot and its table are the audited ones
    wait_preview_rows(page, expected["amr_after"], timeout=60_000)
    rows_after = expected["amr_after"]
    assert 0 < rows_after < rows_before
    expect(page.locator("#plot_cell_amr_heatmap, [id^='plot_badge_amr_heatmap']").first).to_be_attached()
    expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("written at a table this plot is built from", timeout=20_000)
    expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("its table changed")
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("plot(s) are built from there")
    # the table views other than T3 show the originals in Audit mode
    set_view(page, "T1")
    wait_preview_rows(page, rows_before, timeout=30_000)
    set_view(page, "T3")
    wait_preview_rows(page, rows_after, timeout=30_000)
    # Compare: the Original and the Audited pane
    set_compare(page, True)
    expect(page.locator("[id$='_cmp_base'].shiny-plot-output").first).to_be_visible(timeout=30_000)
    set_compare(page, False)
    # a plot beside ResFinder: no step on it, its table is its original
    page.locator(".nav-link:has-text('AMR')").first.click()
    page.locator("[id^='subtabs_'] .nav-link:has-text('MLST Bar')").first.click()
    _wait_shiny(page)
    mlst_rows = expected["mlst"]
    wait_preview_rows(page, mlst_rows, timeout=30_000)
    expect(page.locator("#plot_badge_mlst_bar")).to_contain_text("no audited step for this plot yet", timeout=20_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("No T3 adjustments")
    # back to the AMR plot: remove the step (the bin of its card) and every plot reads its original table
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)
    expect(page.locator("[id^='t3_delete_']")).to_have_count(1, timeout=15_000)
    page.locator("[id^='t3_delete_']").first.click()
    _wait_shiny(page)
    wait_preview_rows(page, rows_before, timeout=60_000)
    expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("no audited step for this plot yet", timeout=20_000)
    page.locator("[id^='subtabs_'] .nav-link:has-text('MLST Bar')").first.click()
    _wait_shiny(page)
    wait_preview_rows(page, mlst_rows, timeout=30_000)
