"""The demo walk W: the demo recipe in Audit mode, from opening to export, as a user does it (first version, 2026-11-26).

Run (qa app features: every flag on, ghost save off; about two minutes on an idle machine):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_demo_walk_audit.py -q

# @deps
# consumes: app/handlers/home_theater.py (the mode row, Compare, the data preview), app/handlers/lineage_handlers.py (the panel "Path of the data"), app/handlers/trial_handlers.py (Try, the marks, the reason, Add to audit pipeline), app/handlers/audit_stack.py (the step card, the bin), app/handlers/export_handlers.py (the bundle), app/tests/browser_view.py
# doc: .claude/workflows/ (the demo build plan, tmpAI/status/DEMO_BUILD_PLAN_2026-11-26.md: the walk is run at every fall-back point)
# @end_deps

The recipe is `1_test_data_ST22_dummy`, the one the lineage tests call the demo (`app/tests/test_lineage_view_browser.py`, `test_audit_places_browser.py`) and the one
`app/tests/test_id_completion_in_the_app.py` names DEMO: it is the shipped recipe with the most tables (ResFinder, MLST, the quality tables) and plots built from them.

The walk (each stage is a small function, so that a later slice changes one stage only):
  1 open          the recipe opens in Exploration, with the mode row and no Compare
  2 audit mode    switch to Audit: the Compare switch appears, the lineage panel can be opened; no group tabs and no plot tabs (slice 3b): one plot area, "Plot shown: AMR Heatmap"
  2a try          (FLOW-1) a condition on the plot shown is tried: the rows the step removes, the trial shown in words, Discard (nothing is applied)
  3 lineage       open "Path of the data" (it is open on entering Audit mode); choose the place: the first table, tier 1 (ResFinder): nothing changes on screen; Show it and see its table (slice 3a);
                  (the plot area says "No figure: ResFinder ... is a table" and the Compare switch is absent while the table is shown)
  4 add table     (FLOW-3: the one way) a condition on the table shown (ResFinder, tier 1), a value taken from the data (never a fixed count): Try, look, mark "User verified", reason, "Add to audit
                  pipeline": the card says where it was written, the place is marked in the lineage, the plot built from it is the audited one, the rows are the independent count
  5 add plot      (the same way) a second condition on the Result data (T3) of the plot shown (already audited by the first step): Try, look at the table, mark the place "User verified", a reason,
                  "Add to audit pipeline": the notice, the card with its mark, the rows equal an independent count of BOTH steps
  5a drop         (the same way) a column drop at the Result data (T3) of the plot: Try the drop, reason, Add: the column is gone from the table, no row changed
  6 compare       Compare shows the two panes with their labels (three steps now)
  7 export        an export made in Audit mode holds the audited table file, the audit recipe, the mark of the added step in t3_steps.yaml and its sentence in README.txt
The steps are removed at the end (the bin of their cards) and the mode goes back to Exploration, so that the next test finds the page as it was.

The expected rows are computed in the test with polars from the same recipe and data (the engine's own tables), never typed in.

MUTATION (seen failing, then restored): the stage 4 count assertion fails when `PlaceAudit` hands back the original table (HOME never reads the audited table: the rows do not drop).
"""
import io
import zipfile
from pathlib import Path

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import add_to_pipeline, preview_rows, set_compare, set_mode, set_view, show_place, try_staged, wait_preview_rows
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_lineage_view_browser import _clear_choice, _line, _open_panel
from app.tests.test_shiny_smoke import _choose_fb_op, _load_data_analysis_recipe, _open_filters_panel, _wait_shiny

RECIPE = "1_test_data_ST22_dummy"
PLOT = "amr_heatmap"
PLACE = "T1:ResFinder"
REASON = "walk: keep only the hits below the median identity"
REASON_NEW = "walk: and then only the lower half of what remains"
REASON_DROP = "walk: overlap is not needed for this figure"
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
    audited = table.filter(pl.col("identity") < threshold)["identity"].drop_nulls()
    threshold2 = float(audited.unique().sort()[len(audited.unique()) // 2])         # the second step (the new way) cuts the audited table again
    kept2 = table.filter(pl.col("identity") < threshold).filter(pl.col("identity") < threshold2).height
    assert 0 < kept2 < kept, "the walk needs a second value that removes some of the remaining rows and keeps others"
    return {"before": table.height, "after": kept, "removed": table.height - kept, "threshold": threshold, "resfinder": resfinder_rows,
            "threshold2": threshold2, "after2": kept2, "removed2": kept - kept2}


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


def stage_try(page: Page, expected: dict) -> None:
    """FLOW-1: a condition built on the Result data (T3) of the plot shown is TRIED before anything is written: the panel says how many rows the step removes, the preview shows the trial and says so,
    and Discard puts the audited-or-original table back. Nothing is applied: the next stages still start from an empty audit."""
    _choose_column_firmly(page, "identity")
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill(repr(expected["threshold"]))
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#step_try")).to_be_visible(timeout=10_000)
    page.locator("#step_try").click()
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=90_000)
    panel = page.locator(".spv-trial-panel")
    expect(panel).to_contain_text("TRIAL: with the step you are trying", timeout=60_000)
    expect(panel).to_contain_text(f"the step removes {expected['removed']} rows of {expected['before']} here")
    wait_preview_rows(page, expected["after"], timeout=60_000)
    expect(page.locator("#shown_band_ui")).to_contain_text("TRIAL: with the step you are trying")
    page.locator("#trial_discard").click()
    _wait_shiny(page)
    expect(panel).to_have_count(0, timeout=15_000)
    wait_preview_rows(page, expected["before"], timeout=60_000)
    page.locator("#filter_reset").click()
    _wait_shiny(page)


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


def stage_add_table(page: Page, expected: dict) -> None:
    """FLOW-3, the one way, at a TABLE: the condition is built on the table shown (ResFinder, tier 1), tried, marked, given its reason and added. The step reaches the plot built from it."""
    from app.tests.browser_view import stage_condition
    stage_condition(page, "identity", "lt", expected["threshold"])
    try_staged(page)
    expect(page.locator(".spv-trial-panel")).to_contain_text("TRIAL: with the step you are trying", timeout=30_000)
    add_to_pipeline(page, REASON, mark=True, expected_places=1)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at ResFinder: Table, T1", timeout=20_000)
    expect(_line(page, PLACE).locator(".spv-lin-mark")).to_contain_text("audit step", timeout=15_000)
    show_place(page, f"T3:{PLOT}", keep_chosen=False)
    expect(page.locator(f"#plot_badge_{PLOT}")).to_contain_text("its table changed", timeout=20_000)
    wait_preview_rows(page, expected["after"], timeout=60_000)           # the rows went down by exactly the rows the filter removes
    assert expected["before"] - expected["after"] == expected["removed"] > 0


def stage_add_plot(page: Page, expected: dict) -> None:
    """The same way at the Result data (T3) of the plot shown (already audited by the first step): the rows are the independent count of both steps."""
    show_place(page, f"T3:{PLOT}", keep_chosen=False)
    wait_preview_rows(page, expected["after"], timeout=60_000)
    _choose_column_firmly(page, "identity")
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill(repr(expected["threshold2"]))
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    page.locator("#step_try").click()
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=90_000)
    panel = page.locator(".spv-trial-panel")
    expect(panel).to_contain_text(f"the step removes {expected['removed2']} rows of {expected['after']} here", timeout=60_000)
    wait_preview_rows(page, expected["after2"], timeout=60_000)
    expect(panel).to_contain_text("0 of 1 place user verified")
    expect(page.locator("#trial_add")).to_be_disabled()
    page.locator("input[id^='trial_verified_']").check()
    _wait_shiny(page)
    expect(panel).to_contain_text("1 of 1 place user verified")
    page.locator("input[id^='trial_reason_']").fill(REASON_NEW)
    page.locator("input[id^='trial_reason_']").press("Tab")
    expect(page.locator("#trial_add")).to_be_enabled(timeout=15_000)
    page.locator("#trial_add").click()
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=60_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("Step added to the audit pipeline at 1 place (1 of 1 place user verified).", timeout=30_000)
    expect(panel).to_have_count(0, timeout=15_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("User verified", timeout=20_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at AMR Heatmap: Result data, T3")
    wait_preview_rows(page, expected["after2"], timeout=60_000)
    assert expected["after"] - expected["after2"] == expected["removed2"] > 0
    expect(page.locator("#shown_band_ui")).to_contain_text("Audited: your applied steps")


def stage_drop(page: Page, expected: dict) -> None:
    """FLOW-3: a column drop at the Result data (T3) of the plot shown goes the one way: deselect it in the column chooser, Try the drop, reason, Add. A drop changes columns and no row."""
    from app.tests.browser_view import drop_columns
    show_place(page, f"T3:{PLOT}", keep_chosen=False)
    wait_preview_rows(page, expected["after2"], timeout=60_000)
    assert page.evaluate("() => Object.keys(document.getElementById('preview_col_selector').selectize.options).includes('overlap')")
    drop_columns(page, ["overlap"], REASON_DROP, mark=True)
    page.wait_for_function("() => !Object.keys(document.getElementById('preview_col_selector').selectize.options).includes('overlap')", timeout=30_000)
    wait_preview_rows(page, expected["after2"], timeout=60_000)             # no row changed
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Drop Column", timeout=20_000)


def stage_compare(page: Page) -> None:
    set_compare(page, True)
    expect(page.locator("[id$='_cmp_base'].shiny-plot-output").first).to_be_visible(timeout=30_000)
    expect(page.locator(f"#plot_group_{PLOT}")).to_be_visible(timeout=30_000)
    body = page.locator("body")
    expect(body).to_contain_text("Original (before your audit steps)")
    expect(body).to_contain_text("Audited (after 3 steps)")
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
    assert len(plot_table.strip().splitlines()) - 1 == expected["after2"], "the data file of the plot is the audited table HOME shows (the rows of both filters)"
    assert "overlap" not in plot_table.splitlines()[0].split("\t"), "the data file of the plot lacks the dropped column, as the table HOME shows"
    import yaml
    steps = yaml.safe_load(z.read(next(n for n in names if n.endswith("/t3_steps.yaml"))))["steps_by_place"]
    by_reason = {r["reason"]: r for r in steps}
    assert set(by_reason) == {REASON, REASON_NEW, REASON_DROP}, "one record for each added step, at its place"
    assert all(r["user_verified"] is True and r["verified_at"] for r in by_reason.values()), "the mark of every added step is in t3_steps.yaml (all three were marked)"
    assert by_reason[REASON_DROP]["action"] == "drop_column" and by_reason[REASON_DROP]["written_at"] == f"T3:{PLOT}"
    readme = z.read(next(n for n in names if n.endswith("/README.txt"))).decode()
    assert "1 of 1 place user verified" in readme, "README says how many places of the added step were user verified"
    report = z.read(next(n for n in names if n.endswith("report.qmd"))).decode()
    assert "1 of 1 place user verified" in report
    recipes = [n for n in names if "/audit_recipe/" in n and n.endswith("_audited.yaml")]
    assert len(recipes) == 1, f"the audit recipe is in the bundle: {recipes}"


def stage_clean_up(page: Page, expected: dict) -> None:
    for _ in range(6):
        bins = page.locator("[id^='t3_delete_']")
        if not bins.count():
            break
        try:
            bins.first.click(timeout=5_000)
        except Exception:        # the panel was drawn again between the count and the click: look again
            pass
        _wait_shiny(page)
    if page.locator("#trial_discard").count():
        page.locator("#trial_discard").click()
        _wait_shiny(page)
    _clear_choice(page)
    set_mode(page, "exploration")


# -- the walk -----------------------------------------------------------------------------------------------------

def test_the_demo_recipe_in_audit_mode_from_opening_to_export(page: Page, shiny_app: ShinyAppProc, expected):
    stage_open(page, shiny_app.url)
    try:
        stage_audit_mode(page)
        wait_preview_rows(page, expected["before"], timeout=60_000)
        stage_try(page, expected)
        stage_lineage(page, expected)
        stage_add_table(page, expected)
        stage_add_plot(page, expected)
        stage_drop(page, expected)
        stage_compare(page)
        stage_export(page, expected)
    finally:
        stage_clean_up(page, expected)
