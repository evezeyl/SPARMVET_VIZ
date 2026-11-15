"""GATE-GAP-1 in the browser: a step saved from Blueprint that makes a recipe fail is not used by HOME.

Break a step in Blueprint and save; go to HOME: the recipe is no longer offered, it is listed as unavailable with its
reason, and HOME says that the recipe that was open is replaced. The save itself is not blocked (the file is written and
Blueprint says what it means for HOME).

The recipe is a staged copy (`zz_gate_gap_stage` next to the shipped ones, removed at the end): no shipped file changes.
Run under qa: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_gate_gap.py -q
Browser test: about 1 minute.
"""
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, expect

from app.tests.subprocess_env import app_env

REPO = Path(__file__).resolve().parents[2]
PIPELINES = REPO / "config" / "data_analysis_recipes" / "pipelines"
TEST_DATA = REPO / "assets" / "test_data"  # data of a recipe is found under a folder named like the recipe
SOURCE = "1_test_data_ST22_dummy"
STAGE = "zz_gate_gap_stage"
# What ends or breaks a session. Not "Traceback": Blueprint's live data glimpse prints its own column error after a component
# of another recipe is loaded onto the previous anchor (found 2026-11-15, not this task); the point here is that HOME and the
# session survive a recipe broken on disk (before GATE-GAP-1 ConfigManager's SystemExit ended the session).
SERVER_ERRORS = ("Exception in ASGI application", "SystemExit", "Unhandled error")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _stage():
    _unstage()
    shutil.copytree(PIPELINES / SOURCE, PIPELINES / STAGE)
    shutil.copytree(TEST_DATA / SOURCE, TEST_DATA / STAGE)
    text = (PIPELINES / f"{SOURCE}.yaml").read_text().replace(f"{SOURCE}/", f"{STAGE}/")
    (PIPELINES / f"{STAGE}.yaml").write_text(text.replace(f"id: {SOURCE}", f"id: {STAGE}", 1))


def _unstage():
    shutil.rmtree(PIPELINES / STAGE, ignore_errors=True)
    shutil.rmtree(TEST_DATA / STAGE, ignore_errors=True)
    (PIPELINES / f"{STAGE}.yaml").unlink(missing_ok=True)


def _wait_shiny(page: Page, timeout: int = 20_000) -> None:
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=timeout)


def _home_selector_options(page: Page) -> list[str]:
    return page.evaluate("() => Array.from(document.querySelectorAll('#data_analysis_recipe_id option')).map(o => o.value)")


def test_a_step_saved_in_blueprint_that_fails_the_gate_is_not_used_by_home(page: Page, tmp_path):
    _stage()
    log = tmp_path / "server.log"
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DATA_ANALYSIS_RECIPE=STAGE)
    try:
        with open(log, "w") as out:
            proc = subprocess.Popen(
                [str(REPO / ".venv/bin/shiny"), "run", "app/src/main.py", "--port", str(port)],
                cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT,
            )
            try:
                url = f"http://127.0.0.1:{port}/"
                for _ in range(90):
                    try:
                        urllib.request.urlopen(url, timeout=2)
                        break
                    except Exception:
                        time.sleep(1)
                page.goto(url)
                page.wait_for_selector("#sidebar_nav", timeout=60_000)
                _wait_shiny(page, timeout=120_000)

                # HOME starts on the staged recipe: it passes the gate and is offered
                page.wait_for_function("() => document.querySelector('#data_analysis_recipe_id') !== null", timeout=30_000)
                assert STAGE in _home_selector_options(page)

                # Blueprint: open the recipe, load a wrangling component, break one step and save
                page.locator("#sidebar_nav").get_by_text("Blueprint Architect").first.click()
                page.wait_for_function(
                    "() => { var s = document.querySelector('#stored_data_analysis_recipe_selector'); return s && s.options.length > 1; }",
                    timeout=30_000)
                page.evaluate(
                    """(name) => { var s = document.querySelector('#stored_data_analysis_recipe_selector');
                        for (var o of s.options) if (o.text == name) s.value = o.value;
                        s.dispatchEvent(new Event('change', {bubbles: true})); }""", STAGE)
                page.wait_for_function(
                    f"() => Array.from(document.querySelectorAll('#dataset_pipeline_selector option')).some(o => o.value.includes('{STAGE}/wrangling/MLST_wrangling'))",
                    timeout=30_000)
                page.evaluate(
                    """() => { var s = document.querySelector('#dataset_pipeline_selector');
                        for (var o of s.options) if (o.value.includes('wrangling/MLST_wrangling')) s.value = o.value;
                        s.dispatchEvent(new Event('change', {bubbles: true})); }""")
                _wait_shiny(page)
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
                expect(page.locator(".shiny-notification").filter(has_text=f"Saved. HOME will not use '{STAGE}'")).to_have_count(1, timeout=60_000)
                assert "banana" in (PIPELINES / STAGE / "wrangling" / "MLST_wrangling.yaml").read_text()

                # HOME: the recipe is not offered any more, it is listed as unavailable with its reason, and HOME says so
                page.locator("#sidebar_nav").get_by_text("Home").first.click()
                page.wait_for_function("() => document.querySelector('#data_analysis_recipe_id') !== null", timeout=60_000)
                _wait_shiny(page, timeout=120_000)
                assert STAGE not in _home_selector_options(page)
                sidebar = page.locator("#nav_sidebar")
                expect(sidebar).to_contain_text("unavailable", timeout=30_000)
                expect(sidebar).to_contain_text(STAGE, timeout=30_000)
                expect(sidebar).to_contain_text("no longer passes its checks", timeout=30_000)
                assert page.evaluate("() => document.querySelector('#data_analysis_recipe_id').value") != STAGE
            finally:
                proc.terminate()
                proc.wait(timeout=30)
    finally:
        _unstage()
    text = log.read_text()
    assert not any(marker in text for marker in SERVER_ERRORS), text[-1500:]
