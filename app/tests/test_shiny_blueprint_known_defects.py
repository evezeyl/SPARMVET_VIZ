"""BP-GLIMPSE-ANCHOR-1 (found while building GATE-GAP-1), pinned by a strict xfail until its own task fixes it.

Steps: open the app on a recipe (qa), go to Blueprint, pick the recipe, load the wrangling component `MLST_wrangling.yaml`
(its first step selects the column `scheme`). The "Live Data Glimpse" at the bottom says "No data loaded" and shows
`Error: unable to find column "scheme"; valid columns: ["sample_id", "total_reads", ...]`: the glimpse
(`architect_active_table` in app/modules/wrangle_studio.py) falls back from the component's own data (`processed_data_surgical`,
None when no anchor was materialised for it) to `processed_data`, which applies the component's steps to HOME's current
anchor, another dataset.
"""
import pytest
from playwright.sync_api import Page, expect

from app.tests import gate_stage as g
from app.tests.gate_stage import wait_shiny


@pytest.mark.xfail(strict=True, reason="BP-GLIMPSE-ANCHOR-1: the glimpse applies a component's steps to HOME's anchor")
def test_the_live_data_glimpse_does_not_apply_a_component_to_another_dataset(page: Page, tmp_path):
    with g.running_app(tmp_path) as (url, log):
        page.goto(url)
        page.wait_for_selector("#sidebar_nav", timeout=60_000)
        wait_shiny(page, timeout=120_000)
        page.locator("#sidebar_nav").get_by_text("Blueprint Architect").first.click()
        page.wait_for_function(
            "() => { var s = document.querySelector('#stored_data_analysis_recipe_selector'); return s && s.options.length > 1; }",
            timeout=30_000)
        page.evaluate(
            """(name) => { var s = document.querySelector('#stored_data_analysis_recipe_selector');
                for (var o of s.options) if (o.text == name) s.value = o.value;
                s.dispatchEvent(new Event('change', {bubbles: true})); }""", g.STAGE)
        page.wait_for_function(
            f"() => Array.from(document.querySelectorAll('#dataset_pipeline_selector option')).some(o => o.value.includes('{g.STAGE}/wrangling/MLST_wrangling'))",
            timeout=30_000)
        page.evaluate(
            """() => { var s = document.querySelector('#dataset_pipeline_selector');
                for (var o of s.options) if (o.value.includes('wrangling/MLST_wrangling')) s.value = o.value;
                s.dispatchEvent(new Event('change', {bubbles: true})); }""")
        wait_shiny(page)
        page.evaluate("() => document.querySelector('#btn_import_data_analysis_recipe').click()")
        expect(page.locator(".bp-node-card").nth(2)).to_be_visible(timeout=30_000)
        page.wait_for_timeout(3000)
        assert "unable to find column" not in page.locator("body").inner_text()
