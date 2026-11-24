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
    expect(page.locator(NOTICE)).to_contain_text("Choose at least one place", timeout=10_000)
    expect(page.locator("#propagation_confirm")).to_be_visible()
    _close_notices(page)
    # the tier 1 and the tier 2 of one table: one below the other, refused in one line, the dialog stays
    _tick(page, "T1:ResFinder")
    expect(page.locator("#propagation_places input[value='T2:ResFinder']")).to_be_disabled()   # the dialog already shows it as derived
    # the server's refusal is the safety net: force the second tick past the disabled box and confirm
    page.evaluate("() => { const i = document.querySelector(\"#propagation_places input[value='T2:ResFinder']\"); i.disabled = false; i.checked = true; "
                  "i.dispatchEvent(new Event('change', {bubbles: true})); }")
    page.wait_for_timeout(300)
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


def _stage_and_apply_step_at_resfinder(page: Page) -> None:
    _send_filter(page)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    _tick(page, "T1:ResFinder")
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]').first
    expect(box).to_be_visible(timeout=15_000)
    box.fill(REASON)
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)


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
    _choose_column_firmly(page, "ResFinder_not_in_original_data")
    _choose_fb_op(page, "eq")
    _wait_shiny(page)
    page.locator("#fb_value_ui input[value=false], #fb_value input[value=false]").first.check(force=True)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    _tick(page, "T1:ResFinder")
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]').first
    expect(box).to_be_visible(timeout=15_000)
    box.fill("the added lines are not results of the tool: left out of the analyses")
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    try:
        wait_preview_rows(page, expected["amr_no_added"], timeout=60_000)
        expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("its table changed", timeout=20_000)
        # a plot of another group, built from the same table, follows
        page.locator(".nav-link:has-text('QA canaries')").first.click()
        _wait_shiny(page)
        page.locator("[id^='subtabs_'] .nav-link:has-text('Qa Amr Genes Per Sample'), [id^='subtabs_'] .nav-link:has-text('QA AMR')").first.click()
        _wait_shiny(page)
        wait_preview_rows(page, expected["qa_no_added"], timeout=60_000)
        expect(page.locator("#plot_badge_qa_amr_genes_per_sample")).to_contain_text("its table changed", timeout=20_000)
        # a plot that is built from ResFinder through a join whose rows are the same count but whose ResFinder columns lose the added lines: its table changed too
        page.locator(".nav-link:has-text('AMR')").first.click()
        _wait_shiny(page)
        page.locator("[id^='subtabs_'] .nav-link:has-text('Virulence Bar')").first.click()
        _wait_shiny(page)
        expect(page.locator("#plot_badge_virulence_bar")).to_contain_text("its table changed", timeout=20_000)
        # the plot beside ResFinder is not touched
        page.locator("[id^='subtabs_'] .nav-link:has-text('MLST Bar')").first.click()
        _wait_shiny(page)
        expect(page.locator("#plot_badge_mlst_bar")).to_contain_text("no audited step for this plot yet", timeout=20_000)
    finally:
        _amr_plot(page)
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
            wait_preview_rows(page, expected["amr_before"], timeout=60_000)


def test_a_drop_of_a_key_column_at_a_table_whose_join_reads_it_is_refused_in_the_dialog_and_nothing_is_staged(ready: Page):
    """D-0358, D-0297 by place: `sample_id` is read as a key by the joins below ResFinder, so a drop of it written at the ResFinder table is refused with the sentence of the
    rule (the dialog stays open, nothing is staged); a drop of a column no join reads there (`overlap`) is accepted."""
    page = ready
    _amr_plot(page)
    set_view(page, "T3")
    expect(page.locator("#col_drop_to_audit")).to_have_count(1, timeout=15_000)
    # the column chooser: deselect sample_id, send the drop to audit
    page.locator("#preview_col_selector-selectized, #preview_col_selector").first.wait_for(state="attached", timeout=10_000)
    page.evaluate("""() => { const el = document.getElementById('preview_col_selector');
        const s = el.selectize; if (s) { s.removeItem('sample_id'); } }""")
    _wait_shiny(page)
    page.locator("#col_drop_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    _tick(page, "T1:ResFinder")
    page.locator("#propagation_confirm").click()
    expect(page.locator(NOTICE)).to_contain_text("sample_id", timeout=10_000)
    expect(page.locator("#propagation_confirm")).to_be_visible()
    assert page.locator('input[id^="t3_reason_"]').count() == 0, "nothing was staged"
    _close_notices(page)
    page.keyboard.press("Escape")
    expect(page.locator("#propagation_confirm")).to_have_count(0, timeout=5_000)


def test_a_filter_at_tier2_of_resfinder_changes_the_plot_that_reads_that_tier2_and_remove_gives_it_back(ready: Page, expected):
    """Demo step T2: the same mechanism at the tier 2 of a table that a plot reads. The dialog lists the tier 2 of ResFinder (it has tier-2 steps and the AMR Heatmap reads it);
    with it ticked, the audit card says "Table ResFinder (tier 2)", the plot and its T3 table are audited, the T1 and T2 views still show the original tables, and the bin
    gives the original back."""
    page = ready
    _amr_plot(page)
    set_view(page, "T3")
    wait_preview_rows(page, expected["amr_before"], timeout=30_000)
    _send_filter(page)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    _tick(page, "T2:ResFinder")
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]').first
    expect(box).to_be_visible(timeout=15_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at Table ResFinder (tier 2)", timeout=10_000)
    box.fill(REASON)
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    try:
        wait_preview_rows(page, expected["amr_after"], timeout=60_000)
        expect(page.locator("#plot_badge_amr_heatmap")).to_contain_text("its table changed", timeout=20_000)
        set_view(page, "T2")
        wait_preview_rows(page, expected["amr_before"], timeout=30_000)
        set_view(page, "T1")
        wait_preview_rows(page, expected["amr_before"], timeout=30_000)
        set_view(page, "T3")
        wait_preview_rows(page, expected["amr_after"], timeout=30_000)
    finally:
        _amr_plot(page)
        if page.locator("[id^='t3_delete_']").count():
            page.locator("[id^='t3_delete_']").first.click()
            _wait_shiny(page)
            wait_preview_rows(page, expected["amr_before"], timeout=60_000)
