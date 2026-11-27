"""The demo walk W: the demo recipe in Audit mode, from opening to export, as a user does it (first version, 2026-11-26).

Run (qa app features: every flag on, ghost save off; about two minutes on an idle machine):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_demo_walk_audit.py -q

# @deps
# consumes: app/handlers/home_theater.py (the mode row, Compare, the data preview), app/handlers/lineage_handlers.py (the panel "Path of the data"), app/handlers/filter_and_audit_handlers.py (the dialog), app/handlers/audit_stack.py (the step card, Apply), app/handlers/export_handlers.py (the bundle), app/tests/browser_view.py
# doc: .claude/workflows/ (the demo build plan, tmpAI/status/DEMO_BUILD_PLAN_2026-11-26.md: the walk is run at every fall-back point)
# @end_deps

The recipe is `1_test_data_ST22_dummy`, the one the lineage tests call the demo (`app/tests/test_lineage_view_browser.py`, `test_audit_places_browser.py`) and the one
`app/tests/test_id_completion_in_the_app.py` names DEMO: it is the shipped recipe with the most tables (ResFinder, MLST, the quality tables) and plots built from them.

The walk (each stage is a small function, so that a later slice changes one stage only):
  1 open          the recipe opens in Exploration, with the mode row and no Compare
  2 audit mode    switch to Audit: the Compare switch appears, the lineage panel can be opened; no group tabs and no plot tabs (slice 3b): one plot area, "Plot shown: AMR Heatmap"
  3 lineage       open "Path of the data" (it is open on entering Audit mode); choose the place: the first table, tier 1 (ResFinder): nothing changes on screen; Show it and see its table (slice 3a);
                  (the plot area says "No figure: ResFinder ... is a table" and the Compare switch is absent while the table is shown);
                  show the Result data (T3) of the plot again, which the filter is built on, and choose ResFinder again, to write the step there
  4 filter        build a filter on a column of the table the open plot reads, a value taken from the data (never a fixed count), sent to audit at that place
  5 apply         a reason, Apply: the card says where it was written, the place is marked, the plot is the audited one, the data preview has the rows expected
  6 compare       Compare shows the two panes with their labels
  7 export        an export made in Audit mode holds the audited table file and the audit recipe
The step is removed at the end (the bin of its card) and the mode goes back to Exploration, so that the next test finds the page as it was.

The expected rows are computed in the test with polars from the same recipe and data (the engine's own tables), never typed in.

MUTATION (seen failing, then restored): the stage 5 count assertion fails when `PlaceAudit` hands back the original table (HOME never reads the audited table: the rows do not drop).
"""
import io
import zipfile
from pathlib import Path

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import preview_rows, set_compare, set_mode, set_view, show_place, wait_preview_rows
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_lineage_view_browser import _clear_choice, _line, _open_panel
from app.tests.test_shiny_smoke import _choose_fb_op, _load_data_analysis_recipe, _open_filters_panel, _wait_shiny

RECIPE = "1_test_data_ST22_dummy"
PLOT = "amr_heatmap"
PLACE = "T1:ResFinder"
REASON = "walk: keep only the hits below the median identity"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def expected(tmp_path_factory):
    """The rows the data preview must show before and after the step, from the engine's own table of the plot (computed here, not typed in)."""
    from app.modules.orchestrator import DataOrchestrator
    orch = DataOrchestrator(ROOT / "config" / "data_analysis_recipes" / "pipelines", ROOT / "assets" / "test_data")
    where = tmp_path_factory.mktemp("walk")
    table = orch.materialize_tier3(RECIPE, PLOT, where).collect()
    resfinder_rows = orch.materialize_tier1(RECIPE, "ResFinder", where / "ResFinder.parquet").collect().height
    identity = table["identity"].drop_nulls()
    threshold = float(identity.unique().sort()[len(identity.unique()) // 2])      # a value the data holds: some rows are below it, some are not
    kept = table.filter(pl.col("identity") < threshold).height
    assert 0 < kept < table.height, "the walk needs a value that removes some rows and keeps others"
    return {"before": table.height, "after": kept, "removed": table.height - kept, "threshold": threshold, "resfinder": resfinder_rows}


# -- the stages ---------------------------------------------------------------------------------------------------

def stage_open(page: Page, url: str) -> None:
    _load_data_analysis_recipe(page, url, RECIPE)
    _open_filters_panel(page)
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)
    set_mode(page, "exploration")
    expect(page.locator(".spv-mode-row")).to_be_visible()
    assert page.locator("#audit_compare").count() == 0, "no Compare in Exploration"


def stage_audit_mode(page: Page) -> None:
    set_mode(page, "audit")
    expect(page.locator("#audit_compare")).to_be_attached(timeout=15_000)
    expect(page.locator("#home_groups_nav")).to_have_count(0)                  # slice 3b: no group tabs and no plot tabs in Audit mode
    expect(page.locator("[id^='subtabs_']")).to_have_count(0)
    expect(page.locator(".spv-audit-plot-area")).to_contain_text(f"Plot shown: AMR Heatmap", timeout=30_000)
    set_view(page, "T3")


def stage_lineage(page: Page, expected: dict) -> None:
    _open_panel(page)
    _clear_choice(page)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: AMR Heatmap: Result data, T3")
    _line(page, PLACE).click()                      # choosing only stages the place: the table on screen is still the plot's Result data
    _wait_shiny(page)
    expect(page.locator("#lineage_root .spv-lin-chosen")).to_contain_text("ResFinder")
    assert preview_rows(page) == expected["before"], "choosing changed what is shown"
    page.locator(f"#lineage_root .spv-lin-show[data-place='{PLACE}']").click()                  # Show: the table of the place, original (no step yet)
    _wait_shiny(page)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: ResFinder: Table, T1")
    wait_preview_rows(page, expected["resfinder"], timeout=60_000)
    expect(page.locator(".spv-audit-plot-area")).to_contain_text("No figure: ResFinder: Table, T1 is a table")      # a table is not a figure
    expect(page.locator("#audit_compare")).to_have_count(0)                                                           # no Compare for a table
    show_place(page, f"T3:{PLOT}")                  # the filter below is built on the Result data (T3) of the open plot, so it is shown again
    wait_preview_rows(page, expected["before"], timeout=60_000)
    _line(page, PLACE).click()                      # the place the step is written at: chosen again, not shown
    _wait_shiny(page)
    expect(page.locator("#lineage_root .spv-lin-chosen")).to_contain_text("ResFinder")


def stage_filter(page: Page, expected: dict) -> None:
    """Build the filter on `identity` of the plot's table and send it to audit at the chosen place through the existing dialog."""
    _choose_column_firmly(page, "identity")
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill(repr(expected['threshold']))
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    page.locator("#lineage_root .spv-lin-create").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=15_000)
    expect(page.locator(f"#propagation_places input[value='{PLACE}']")).to_be_checked()
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)


def stage_apply(page: Page, expected: dict) -> None:
    box = page.locator('input[id^="t3_reason_"]').first
    expect(box).to_be_visible(timeout=15_000)
    box.fill(REASON)
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at ResFinder: Table, T1", timeout=20_000)
    expect(_line(page, PLACE).locator(".spv-lin-mark")).to_contain_text("audit step", timeout=15_000)
    expect(page.locator(f"#plot_badge_{PLOT}")).to_contain_text("its table changed", timeout=20_000)
    wait_preview_rows(page, expected["after"], timeout=60_000)           # the rows went down by exactly the rows the filter removes
    assert expected["before"] - expected["after"] == expected["removed"] > 0


def stage_compare(page: Page) -> None:
    set_compare(page, True)
    expect(page.locator("[id$='_cmp_base'].shiny-plot-output").first).to_be_visible(timeout=30_000)
    expect(page.locator(f"#plot_group_{PLOT}")).to_be_visible(timeout=30_000)
    body = page.locator("body")
    expect(body).to_contain_text("Original (before your audit steps)")
    expect(body).to_contain_text("Audited (after 1 step)")
    set_compare(page, False)
    expect(page.locator("[id$='_cmp_base'].shiny-plot-output")).to_have_count(0, timeout=15_000)


def stage_export(page: Page, expected: dict) -> None:
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion .accordion-button", has_text="Export").first.click()
        _wait_shiny(page)
    page.locator("#export_user_name").fill("walk")
    with page.expect_download(timeout=180_000) as info:
        page.locator("#export_bundle_download").click()
    z = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
    names = z.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
    assert not [n for n in names if n.endswith("_ERROR.txt")], [n for n in names if n.endswith("_ERROR.txt")]
    audited = next((n for n in names if n.endswith("/ResFinder/T1_data_audited.tsv")), None)
    assert audited, f"no audited table file of ResFinder in {names}"
    assert 0 < len(z.read(audited).decode().strip().splitlines()) - 1
    plot_table = next(z.read(n).decode() for n in names if n.endswith(f"/T3_data_{PLOT}.tsv"))
    assert len(plot_table.strip().splitlines()) - 1 == expected["after"], "the data file of the plot is the audited table HOME shows"
    recipes = [n for n in names if "/audit_recipe/" in n and n.endswith("_audited.yaml")]
    assert len(recipes) == 1, f"the audit recipe is in the bundle: {recipes}"


def stage_clean_up(page: Page, expected: dict) -> None:
    if page.locator("[id^='t3_delete_']").count():
        page.locator("[id^='t3_delete_']").first.click()
        _wait_shiny(page)
        wait_preview_rows(page, expected["before"], timeout=60_000)
    _clear_choice(page)
    set_mode(page, "exploration")


# -- the walk -----------------------------------------------------------------------------------------------------

def test_the_demo_recipe_in_audit_mode_from_opening_to_export(page: Page, shiny_app: ShinyAppProc, expected):
    stage_open(page, shiny_app.url)
    try:
        stage_audit_mode(page)
        wait_preview_rows(page, expected["before"], timeout=60_000)
        stage_lineage(page, expected)
        stage_filter(page, expected)
        stage_apply(page, expected)
        stage_compare(page)
        stage_export(page, expected)
    finally:
        stage_clean_up(page, expected)
