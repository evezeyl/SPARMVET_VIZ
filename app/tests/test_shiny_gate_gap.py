"""GATE-GAP-1 in the browser: a recipe that fails the load gate after the app started is not used by HOME.

Three ways to break the recipe, one test each:
  1. through Blueprint's save (a step), then HOME;
  2. behind the app's back (a file edited on disk, no Blueprint save) while HOME has the recipe open: the selector follows;
  3. with a hidden selector (pipeline-static): HOME says the recipe is not available and shows nothing of it; the export
     is refused with a plain EXPORT_NOT_CREATED.txt, for a missing include and for a YAML syntax error.

The recipe is a staged copy (`app/tests/gate_stage.py`, removed at the end): no shipped file changes. Its label is unique, so
"nothing of it is shown" is checked on the text of the page.
Run under qa: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_gate_gap.py -q
Browser tests: about 3 minutes.
"""
import io
import zipfile
from pathlib import Path

from playwright.sync_api import Page, expect

from app.tests import gate_stage as g
from app.tests.gate_stage import wait_shiny


def _open_home(page: Page, url: str):
    page.goto(url)
    page.wait_for_selector("#sidebar_nav", timeout=60_000)
    wait_shiny(page, timeout=120_000)


def test_a_step_saved_in_blueprint_that_fails_the_gate_is_not_used_by_home(page: Page, tmp_path):
    with g.running_app(tmp_path, blueprint=True) as (url, log):
        _open_home(page, url)
        page.wait_for_function("() => document.querySelector('#data_analysis_recipe_id') !== null", timeout=30_000)
        assert g.STAGE in g.selector_options(page)
        expect(page.locator("body")).to_contain_text(g.LABEL, timeout=30_000)  # the control: the label is on the page while it passes

        # Blueprint: open the recipe, load a wrangling component, break one step and save
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
        page.locator(".bp-node-card").nth(2).click()
        limit = page.locator("#bp_form_limit")
        expect(limit).to_be_visible(timeout=15_000)
        limit.fill("banana")  # the limit of a fill is a number
        page.locator("#btn_bp_apply_node").click()
        expect(page.locator(".shiny-notification").filter(has_text="updated")).to_have_count(1, timeout=15_000)
        page.evaluate("() => document.querySelector('#btn_save_internal').click()")

        # the save is not blocked, and Blueprint says what it means for HOME
        expect(page.locator(".shiny-notification").filter(has_text=f"Saved. HOME will not use '{g.STAGE}'")).to_have_count(1, timeout=60_000)
        assert "banana" in g.FRAGMENT.read_text()

        # HOME: not offered, listed as unavailable with its reason, nothing of it shown
        page.locator("#sidebar_nav").get_by_text("Home").first.click()
        page.wait_for_function("() => document.querySelector('#data_analysis_recipe_id') !== null", timeout=60_000)
        wait_shiny(page, timeout=120_000)
        assert g.STAGE not in g.selector_options(page)
        assert g.selector_value(page) != g.STAGE
        sidebar = page.locator("#nav_sidebar")
        expect(sidebar).to_contain_text("unavailable", timeout=30_000)
        expect(sidebar).to_contain_text(g.STAGE, timeout=30_000)
        expect(sidebar).to_contain_text("no longer passes its checks", timeout=30_000)
        assert g.LABEL not in page.locator("body").inner_text(), "something of the failing recipe is still shown"

        # the user is informed and never silently switched (ADR-104): the notice names both recipes, outlives several polls
        # (CONTROLS-FIX-1: it used to go at the next poll) and is written once to the Alerts log
        page.wait_for_timeout(3 * 2_000 + 500)
        expect(sidebar).to_contain_text(f"'{g.STAGE}' was open and no longer passes its checks", timeout=5_000)
        expect(sidebar).to_contain_text(f"HOME shows '{g.selector_value(page)}' instead", timeout=5_000)
        assert (page.locator("#notification_log_panel_ui").text_content() or "").count(f"'{g.STAGE}' was open and no longer passes") == 1
    assert g.server_errors(log) == [], g.server_errors(log)


def test_a_recipe_edited_on_disk_while_home_shows_it_is_dropped_from_the_selector_and_comes_back(page: Page, tmp_path):
    """No Blueprint save here: the poll of the gate must see the change by itself."""
    with g.running_app(tmp_path) as (url, log):
        _open_home(page, url)
        page.wait_for_function("() => document.querySelector('#data_analysis_recipe_id') !== null", timeout=30_000)
        assert g.selector_value(page) == g.STAGE
        for kind in ("missing_include", "yaml_syntax"):
            good = g.break_on_disk(kind)
            page.wait_for_function(f"() => !Array.from(document.querySelectorAll('#data_analysis_recipe_id option')).some(o => o.value == '{g.STAGE}')",
                                   timeout=15_000)
            assert g.selector_value(page) != g.STAGE, kind
            sidebar = page.locator("#nav_sidebar")
            expect(sidebar).to_contain_text(g.STAGE, timeout=15_000)
            expect(sidebar).to_contain_text("no longer passes its checks", timeout=15_000)
            wait_shiny(page, timeout=60_000)
            assert g.LABEL not in page.locator("body").inner_text(), f"{kind}: something of the failing recipe is still shown"
            g.repair(good)
            page.wait_for_function(f"() => Array.from(document.querySelectorAll('#data_analysis_recipe_id option')).some(o => o.value == '{g.STAGE}')",
                                   timeout=15_000)
            page.locator("#data_analysis_recipe_id").select_option(g.STAGE)   # open it again: HOME takes it back
            wait_shiny(page, timeout=120_000)
            expect(page.locator("body")).to_contain_text(g.LABEL, timeout=30_000)
    assert g.server_errors(log) == [], g.server_errors(log)


def test_with_a_hidden_selector_home_says_the_recipe_is_not_available_and_the_export_is_refused(page: Page, tmp_path):
    with g.running_app(tmp_path, features="pipeline-static") as (url, log):
        _open_home(page, url)
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=120_000)
        assert page.locator("#data_analysis_recipe_id").count() == 0  # the control: there is no selector, the recipe is named
        for kind in ("missing_include", "yaml_syntax"):
            good = g.break_on_disk(kind)
            panel = page.locator("#dynamic_tabs .alert", has_text="This data analysis recipe is not available")
            expect(panel).to_be_visible(timeout=15_000)
            expect(panel).to_contain_text(g.STAGE)
            expect(panel).to_contain_text("does not use it")
            assert g.theater_shows_content_of_a_recipe(page) == {"tabs": 0, "tables": 0, "plots": 0}, kind
            assert g.LABEL not in page.locator("body").inner_text(), kind

            # the export says so plainly instead of failing
            if not page.locator("#export_bundle_download").is_visible():
                page.locator("#nav_accordion").get_by_text("Export").first.click()
                wait_shiny(page)
            with page.expect_download(timeout=60_000) as info:
                page.locator("#export_bundle_download").click()
            z = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
            refused = [n for n in z.namelist() if n.endswith("EXPORT_NOT_CREATED.txt")]
            assert refused and len(z.namelist()) == 1, (kind, z.namelist())
            text = z.read(refused[0]).decode()
            assert g.STAGE in text and "not available" in text and "nothing was exported" in text.lower(), text

            g.repair(good)
            expect(page.locator("#dynamic_tabs .nav-link").first).to_be_visible(timeout=30_000)
            assert page.locator("#dynamic_tabs .alert", has_text="not available").count() == 0
    assert g.server_errors(log) == [], g.server_errors(log)
