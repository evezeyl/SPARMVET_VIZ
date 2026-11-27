"""An audit step written at a table upstream of the plot, in the browser (HOME audit, demo step 3): the trial, the audit panel, the plots, Compare, Remove, the export.

Run (qa app features: every flag on, ghost save off):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_places_browser.py -q

FLOW-3 (2026-11-27): the dialog of "Send to Audit" is gone, so a step at a table is written the one way: SHOW the table (Path of the data), build the condition on it, Try, reason,
Add to audit pipeline (`browser_view.add_condition_step`); the dialog's own test (the nested choice refused, the lines offered) is gone with it (the rule is tested headless:
`test_audit_try.py`, `libs/utils/tests/test_rule_of_places.py`).

What a person does on the demo `1_test_data_ST22_dummy`, and sees (D-0535: "the user must be able to choose, through the scope, where the step is added"):
- with the tier 1 of ResFinder shown, a filter `identity < 99` is added; the audit panel says "Written at ResFinder: Table, T1"; the data table of the plot built from it has fewer rows than before; the
  plot's badge says the step was written upstream and that its table changed;
- the plot "MLST Bar" (a plot beside ResFinder) has no audited step and the same rows as before; its badge says so;
- Compare shows the Original and the Audited pane of the AMR plot; the data table of the AMR plot in T1 shows the AUDITED table (D-0622: the same filter, written at tier 1 of ResFinder) and its badge says "audited";
- "Remove step" (the bin of the card) gives every plot its original table back;
- a column drop at the Result data (T3) of the plot is tried and added the same way.

Mutation index (each seen failing): MUTATION B1 `_audited_t3_lf` returns None (HOME never reads the audited table: the rows do not drop).
"""
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import add_condition_step, add_to_pipeline, drop_columns, try_staged, in_audit_mode, preview_rows, set_compare, set_mode, set_view, show_place, show_plot, wait_preview_rows, wait_preview_rows_below
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
    qa = orch.materialize_tier3("1_test_data_ST22_dummy", "qa_amr_genes_per_sample", folder).collect()
    marker = "ResFinder_not_in_original_data"
    # the plot of the QA group does not carry the marker column: its rows after a filter on the marker at tier 1 of ResFinder come from the engine's audit copy
    from app.modules.audit_places import PLACES_BUCKET
    from app.modules.audit_view import PlaceAudit
    from app.modules.session_manager import make_audit_step
    node = make_audit_step("filter_row", {"column": marker, "op": "eq", "value": False, "na": "remove"}, plot_scope=PLACES_BUCKET, reason="r",
                           place="T1:ResFinder", started_from="subtab_amr_heatmap")
    audit = PlaceAudit(orch, folder / "anchors_for_audit", folder / "audit_for_audit")
    qa_after = audit.plot_lazy("1_test_data_ST22_dummy", "qa_amr_genes_per_sample", [node]).collect().height
    return {"amr_before": amr.height, "amr_after": amr.filter(pl.col("identity") < 99).height, "mlst": mlst.height,
            "amr_no_added": amr.filter(~pl.col(marker)).height, "qa_before": qa.height, "qa_no_added": qa_after, "added": int(amr[marker].sum())}


def _amr_plot(page: Page) -> None:
    """The AMR Heatmap plot: its tab in Exploration; in Audit mode there are no plot tabs (slice 3b), the plot is shown from "Path of the data"."""
    if in_audit_mode(page):
        show_plot(page, "amr_heatmap")
        return
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)


def _close_notices(page: Page) -> None:
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


def _add_step_at(page: Page, place: str, column: str = "identity", op: str = "lt", value=99, reason: str = REASON) -> None:
    """FLOW-3: write a filter at `place` the one way: show the place (nothing else chosen), build the condition on the table shown, Try, mark "User verified", reason, Add to audit pipeline;
    then show the AMR plot again, as the old dialog left the page (the plot's Result data on screen)."""
    show_place(page, place, keep_chosen=False)
    add_condition_step(page, column, op, value, reason, mark=True, expected_places=1)
    _amr_plot(page)


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    _amr_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    yield page
    set_mode(page, "exploration")


def test_a_filter_at_tier1_of_resfinder_changes_the_plots_below_and_not_the_plot_beside_and_remove_gives_it_back(ready: Page, expected):
    page = ready
    rows_before = expected["amr_before"]
    wait_preview_rows(page, rows_before, timeout=30_000)
    _add_step_at(page, "T1:ResFinder")
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at ResFinder: Table, T1", timeout=10_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("User verified")
    # the plot and its table are the audited ones
    wait_preview_rows(page, expected["amr_after"], timeout=60_000)
    rows_after = expected["amr_after"]
    assert 0 < rows_after < rows_before
    expect(page.locator("#plot_cell_amr_heatmap, [id^='plot_badge_amr_heatmap']").first).to_be_attached()
    expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("written at a table this plot is built from", timeout=20_000)
    expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("its table changed")
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("plots are built from there")
    # D-0622: in Audit mode the T1 view of ResFinder shows the audited table (the step was written at its tier 1), and its badge says so
    show_place(page, "T1:ResFinder")      # slice 3a: in Audit mode the table shown is the place chosen in Path of the data and shown
    wait_preview_rows(page, rows_after, timeout=30_000)
    expect(page.locator("#home_data_preview_badge")).to_contain_text("Viewing: T1, audited", timeout=20_000)
    show_plot(page, "amr_heatmap")      # a table was shown: the plot's Result data is shown from the lineage (no plot tabs in Audit mode)
    wait_preview_rows(page, rows_after, timeout=30_000)
    # Compare: the Original and the Audited pane
    set_compare(page, True)
    expect(page.locator("[id$='_cmp_base'].shiny-plot-output").first).to_be_visible(timeout=30_000)
    set_compare(page, False)
    # a plot beside ResFinder: no step on it, its table is its original
    show_plot(page, "mlst_bar")
    mlst_rows = expected["mlst"]
    wait_preview_rows(page, mlst_rows, timeout=30_000)
    expect(page.locator("#plot_badge_mlst_bar")).to_contain_text("no audited step for this plot yet", timeout=20_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("No T3 adjustments")
    # back to the AMR plot: remove the step (the bin of its card) and every plot reads its original table
    show_plot(page, "amr_heatmap")
    expect(page.locator("[id^='t3_delete_']")).to_have_count(1, timeout=15_000)
    page.locator("[id^='t3_delete_']").first.click()
    _wait_shiny(page)
    wait_preview_rows(page, rows_before, timeout=60_000)
    expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("no audited step for this plot yet", timeout=20_000)
    show_plot(page, "mlst_bar")
    wait_preview_rows(page, mlst_rows, timeout=30_000)


def _stage_and_apply_step_at_resfinder(page: Page) -> None:
    _add_step_at(page, "T1:ResFinder")


def test_the_export_holds_the_audited_table_the_step_with_its_place_and_a_recipe_that_builds_it(ready: Page, expected):
    """Demo step 4: the exported data file of the plot is the audited table of HOME (same rows), t3_steps.yaml, README and report say where the step is written and why, the
    other plot has no T3 file, and the reproducibility recipe holds the step as a plain step at the end of the tier 1 of ResFinder."""
    import io
    import zipfile
    from pathlib import Path
    import yaml
    page = ready
    _amr_plot(page)
    set_view(page, "T3")
    _stage_and_apply_step_at_resfinder(page)
    wait_preview_rows(page, expected["amr_after"], timeout=60_000)
    try:
        if not page.locator("#export_bundle_download").is_visible():
            page.locator("#nav_accordion .accordion-button", has_text="Export").first.click()   # not get_by_text: the reminder of the Filters panel says "exported" too
            _wait_shiny(page)
        page.locator("#export_include_reproducibility").check(force=True)
        _wait_shiny(page)
        page.locator("#export_user_name").fill("autotest")
        with page.expect_download(timeout=180_000) as info:
            page.locator("#export_bundle_download").click()
        z = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
        names = z.namelist()
        assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
        errors = {n: z.read(n).decode() for n in names if n.endswith("_ERROR.txt")}
        assert not errors, errors
        table = next(z.read(n).decode() for n in names if n.endswith("/T3_data_amr_heatmap.tsv"))
        assert len(table.strip().splitlines()) - 1 == expected["amr_after"], "the data file of the plot is the audited table of HOME"
        assert not any(n.endswith("/T3_data_mlst_bar.tsv") for n in names), "a plot beside the place has no T3 file"
        original = next(z.read(n).decode() for n in names if n.endswith("/ResFinder/T1_data.tsv"))
        assert len(original.strip().splitlines()) - 1 == expected["amr_before"], "the T1 file of the table is the table as the recipe builds it"
        # owner, 2026-11-24 (PROVISIONAL form): an export made in Audit mode also writes the audited table beside the original, for the table the step changes
        audited_t1 = next(z.read(n).decode() for n in names if n.endswith("/ResFinder/T1_data_audited.tsv"))
        assert 0 < len(audited_t1.strip().splitlines()) - 1 < expected["amr_before"], "the audited T1 file of ResFinder holds fewer rows than the original"
        assert [n.split("/")[-2] for n in names if n.endswith("_audited.tsv")] and all(n.split("/")[-2] not in ("MLST",) for n in names if n.endswith("_audited.tsv")), "a table beside the place has no audited file"
        steps = yaml.safe_load(next(z.read(n).decode() for n in names if n.endswith("/t3_steps.yaml")))
        (record,) = steps["steps_by_place"]
        assert record["written_at"] == "T1:ResFinder" and record["written_at_words"] == "Table ResFinder (tier 1)" and record["reason"] == REASON
        assert record["column"] == "identity" and "amr_heatmap" in record["plots_built_from_it"] and "mlst_bar" not in record["plots_built_from_it"]
        readme = next(z.read(n).decode() for n in names if n.endswith("README.txt"))
        assert "Audit steps, each at the place it is written" in readme and "Table ResFinder (tier 1)" in readme and REASON in readme
        qmd = next(z.read(n).decode() for n in names if n.endswith("report.qmd"))
        assert "## Audit steps" in qmd and "Table ResFinder (tier 1)" in qmd and "it applies to every plot built from there" in qmd
        recipe = yaml.safe_load(next(z.read(n).decode() for n in names if "data_analysis_recipes_reproducibility/" in n and n.endswith(".yaml")))
        last = recipe["data_schemas"]["ResFinder"]["tier1"]["steps"][-1]
        assert last["action"] == "modif_filter" and last["column"] == "identity" and last["op"] == "lt"
        run = yaml.safe_load(next(z.read(n).decode() for n in names if n.endswith("effective_run.yaml")))
        assert len(run["t3_audit_steps_sha256"]) == 64
    finally:
        _amr_plot(page)
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
            wait_preview_rows(page, expected["amr_before"], timeout=60_000)


def test_the_added_lines_of_resfinder_are_removed_by_a_filter_on_its_marker_at_tier1_and_the_plots_below_follow(ready: Page, expected):
    """The marker case (D-0586, D-0613): the app adds a line "missing in original table" for an entity that has no ResFinder result (`ResFinder_not_in_original_data`
    is true on it). A user who does not want these lines in the analyses writes a filter on the marker at tier 1 of ResFinder, with a reason: the plot AMR Heatmap and
    the plot of the QA group that is built from the same table lose exactly those lines; the Virulence Bar plot, which is below ResFinder too, changes as well (its ResFinder columns
    lose the added lines); the plot beside (MLST Bar) is untouched."""
    page = ready
    assert expected["added"] == 4 and expected["amr_no_added"] == expected["amr_before"] - 4
    _amr_plot(page)
    set_view(page, "T3")
    wait_preview_rows(page, expected["amr_before"], timeout=30_000)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    _choose_column_firmly(page, "ResFinder_not_in_original_data")
    _choose_fb_op(page, "eq")
    _wait_shiny(page)
    page.locator("#fb_value_ui input[value=false], #fb_value input[value=false]").first.check(force=True)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    try_staged(page)
    add_to_pipeline(page, "the added lines are not results of the tool: left out of the analyses", mark=True, expected_places=1)
    _amr_plot(page)
    try:
        wait_preview_rows(page, expected["amr_no_added"], timeout=60_000)
        expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("its table changed", timeout=20_000)
        # a plot of another group, built from the same table, follows
        show_plot(page, "qa_amr_genes_per_sample")
        wait_preview_rows(page, expected["qa_no_added"], timeout=60_000)
        expect(page.locator("#plot_badge_qa_amr_genes_per_sample")).to_contain_text("its table changed", timeout=20_000)
        # a plot that is built from ResFinder through a join whose rows are the same count but whose ResFinder columns lose the added lines: its table changed too
        show_plot(page, "virulence_bar")
        expect(page.locator("#plot_badge_virulence_bar")).to_contain_text("its table changed", timeout=20_000)
        # the plot beside ResFinder is not touched
        show_plot(page, "mlst_bar")
        expect(page.locator("#plot_badge_mlst_bar")).to_contain_text("no audited step for this plot yet", timeout=20_000)
    finally:
        _amr_plot(page)
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
            wait_preview_rows(page, expected["amr_before"], timeout=60_000)


def test_a_column_drop_at_the_result_data_of_the_plot_is_tried_and_added_and_the_bin_gives_the_column_back(ready: Page, expected):
    """FLOW-3: the column drop has the one way in (the column chooser, "Try the drop", the same panel, reason, Add to audit pipeline). A drop is offered at the Result data (T3) of a plot only, so the
    refusal of a key a later join reads (D-0358, by place) has no route at a table here (it is tested headless: `test_audit_join_key_drops.py`, `libs/utils/tests/test_key_drop.py`, the engine's
    `test_audit_trial.py`)."""
    page = ready
    _amr_plot(page)
    set_view(page, "T3")
    wait_preview_rows(page, expected["amr_before"], timeout=30_000)
    expect(page.locator("#col_drop_try")).to_have_count(1, timeout=15_000)
    page.locator("#preview_col_selector-selectized, #preview_col_selector").first.wait_for(state="attached", timeout=10_000)
    before = page.evaluate("() => Object.keys(document.getElementById('preview_col_selector').selectize.options)")
    assert "overlap" in before
    drop_columns(page, ["overlap"], "overlap is not used by this check", mark=True)
    try:
        expect(page.locator("#audit_nodes_tier3")).to_contain_text("Drop Column", timeout=20_000)
        expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at AMR Heatmap: Result data, T3")
        wait_preview_rows(page, expected["amr_before"], timeout=60_000)          # a drop changes columns, never rows
        page.wait_for_function("() => !Object.keys(document.getElementById('preview_col_selector').selectize.options).includes('overlap')", timeout=20_000)
    finally:
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
    page.wait_for_function("() => Object.keys(document.getElementById('preview_col_selector').selectize.options).includes('overlap')", timeout=30_000)


def test_a_filter_at_tier2_of_resfinder_changes_the_plot_that_reads_that_tier2_and_remove_gives_it_back(ready: Page, expected):
    """Demo step T2: the same mechanism at the tier 2 of a table that a plot reads. The dialog lists the tier 2 of ResFinder (it has tier-2 steps and the AMR Heatmap reads it);
    with it ticked, the audit card says "Table ResFinder (tier 2)", the plot, its T3 table and the T2 view are audited, the T1 view still shows the original table (the step is at tier 2), and the bin
    gives the original back."""
    page = ready
    _amr_plot(page)
    set_view(page, "T3")
    wait_preview_rows(page, expected["amr_before"], timeout=30_000)
    _add_step_at(page, "T2:ResFinder")
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at ResFinder: Table, T2", timeout=10_000)
    try:
        wait_preview_rows(page, expected["amr_after"], timeout=60_000)
        expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("its table changed", timeout=20_000)
        show_place(page, "T2:ResFinder")
        wait_preview_rows(page, expected["amr_after"], timeout=30_000)       # D-0622: the T2 view shows the audited tier 2
        expect(page.locator("#home_data_preview_badge")).to_contain_text("Viewing: T2, audited", timeout=20_000)
        show_place(page, "T1:ResFinder")
        wait_preview_rows(page, expected["amr_before"], timeout=30_000)      # a step at tier 2 leaves tier 1 as it is
        expect(page.locator("#home_data_preview_badge")).to_contain_text("Viewing: T1, original", timeout=20_000)
        show_plot(page, "amr_heatmap")      # a table was shown: the plot's Result data is shown from the lineage (no plot tabs in Audit mode)
        wait_preview_rows(page, expected["amr_after"], timeout=30_000)
    finally:
        _amr_plot(page)
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
            wait_preview_rows(page, expected["amr_before"], timeout=60_000)
