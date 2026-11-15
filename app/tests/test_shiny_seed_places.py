"""SEED-HOLDS-1 (ADR-104): the seed lines of the real handlers, in a real app (browser).

The pure functions are tested in test_plot_seeds.py; what only a running app can show is that the handlers
CALL them and put nothing between (a flag, a replaced number, a dropped argument):

  1. a seed written in the recipe holds in HOME (two sessions show the same picture; a session that drew over
     it would show a different one), in the comparison reference pane, in the export and its record
  2. a plot whose recipe writes no seed: the reference pane shows the same arrangement as My view
  3. with the audit trail off (`pipeline-exploration-simple`: t3_sandbox_enabled false) the Reshuffle pin reaches
     HOME and the export (the export once read it behind that flag)

Each scenario starts its own app (the first edits a recipe file, restored afterwards).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_shiny_seed_places.py -q
"""
import io
import socket
import subprocess
import time
import urllib.request
import zipfile
from contextlib import contextmanager
from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageChops
from playwright.sync_api import Page, expect

from app.tests.conftest import browser  # noqa: F401
from app.tests.subprocess_env import app_env
from app.tests.test_shiny_smoke import _navigate_to_phenotype_plot, _wait_shiny

REPO = Path(__file__).resolve().parents[2]
PID = "phenotype_genome_length_fragmentation"
PLOT_FILE = REPO / "config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml"
# `random_state` is accepted by geom_jitter, not by geom_point (checker rule PS04): the test swaps the layer
JITTER_LAYER = '  - name: "geom_point"\n    params: {alpha: 0.6, size: 2.5, position: "jitter"}'
SEEDED_LAYER = '  - name: "geom_jitter"\n    params: {alpha: 0.6, size: 2.5, random_state: 123}'
LOCAL = "config/deployment/local/local.yaml"
PIPELINE = "config/deployment/pipeline_test/pipeline_test.yaml"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextmanager
def running_app(app_features: str, deployment: str, tmp_path):
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES=app_features, SPARMVET_DEPLOYMENT=deployment)
    Path(REPO / "tmpAI").mkdir(exist_ok=True)
    with open(REPO / "tmpAI" / f"seed_places_{app_features}.log", "w") as out:
        proc = subprocess.Popen([str(REPO / ".venv/bin/shiny"), "run", "app/src/main.py", "--port", str(port)],
                                cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(90):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            yield url
        finally:
            proc.terminate()
            proc.wait(timeout=20)


def settle(page: Page, *ids: str) -> None:
    """Wait until every plot is drawn (an image in it) and the spinners are gone: a screenshot taken while a plot
    is still being drawn shows the spinner, not the picture."""
    for plot_id in ids:
        page.wait_for_selector(f"#{plot_id} img", timeout=60_000)
    page.wait_for_timeout(8_000)


def open_phenotype_plot(page: Page, url: str, choose_recipe: bool) -> None:
    page.goto(url)
    if choose_recipe:
        page.wait_for_selector("#data_analysis_recipe_id", timeout=90_000)
        _wait_shiny(page, 60_000)
        page.locator("#data_analysis_recipe_id").select_option("1_test_data_ST22_dummy")
        _wait_shiny(page, 30_000)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=90_000)
    _wait_shiny(page, 60_000)
    _navigate_to_phenotype_plot(page)
    expect(page.locator(f"#plot_group_{PID}")).to_be_visible(timeout=30_000)
    settle(page, f"plot_group_{PID}")


def open_export_panel(page: Page) -> None:
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        _wait_shiny(page)


def export_run_and_png(page: Page, with_recipe: bool = False):
    open_export_panel(page)
    box = page.locator("#export_include_reproducibility")
    if with_recipe:
        box.check(force=True)
    _wait_shiny(page)
    page.locator("#export_user_name").fill("autotest")
    with page.expect_download(timeout=120_000) as info:
        page.locator("#export_bundle_download").click()
    z = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
    if with_recipe:
        box.uncheck(force=True)
        _wait_shiny(page)
    run = yaml.safe_load(z.read(next(n for n in z.namelist() if n.endswith("effective_run.yaml"))).decode())
    png = next(z.read(n) for n in z.namelist() if n.endswith(f"/plots/{PID}.png"))
    return run, png, z


def same_picture(a: bytes, b: bytes) -> bool:
    return ImageChops.difference(Image.open(io.BytesIO(a)).convert("RGB"),
                                 Image.open(io.BytesIO(b)).convert("RGB")).getbbox() is None


def test_a_seed_written_in_the_recipe_holds_in_home_the_reference_pane_and_the_export(browser, tmp_path):
    original = PLOT_FILE.read_text()
    assert JITTER_LAYER in original, "the plot file changed: update this test"
    PLOT_FILE.write_text(original.replace(JITTER_LAYER, SEEDED_LAYER))
    try:
        with running_app("qa", LOCAL, tmp_path) as url:
            shots, runs = [], []
            for _ in range(2):                     # two sessions: each would draw its own seed if HOME drew over the recipe
                context = browser.new_context()
                page = context.new_page()
                try:
                    open_phenotype_plot(page, url, choose_recipe=True)
                    shots.append(page.locator(f"#plot_group_{PID}").screenshot())
                    if len(shots) == 1:
                        page.locator("#plot_view input[value=CMP]").check(force=True)
                        _wait_shiny(page)
                        settle(page, f"plot_group_{PID}", f"plot_group_{PID}_cmp_base")
                        reference = page.locator(f"#plot_group_{PID}_cmp_base").screenshot()
                        mine = page.locator(f"#plot_group_{PID}").screenshot()
                        assert same_picture(reference, mine), "the reference pane does not show the recipe's seed"
                    run, png, z = export_run_and_png(page, with_recipe=len(runs) == 0)
                    runs.append((run, png, z))
                finally:
                    context.close()
        assert same_picture(shots[0], shots[1]), "two sessions show different pictures: HOME drew over the recipe's seed"
        for run, _png, _z in runs:
            assert run["seeds_per_plot"][PID] == 123 and run["seed_source_per_plot"][PID] == "recipe"
            assert [r["seed"] for r in run["seeds_per_layer"][PID]] == [123]
        assert same_picture(runs[0][1], runs[1][1]), "the export of two sessions differs although the recipe fixes the seed"
        assert run["seeds_added_to_recipe"] == []
        z = runs[0][2]
        recipe_name = next(n for n in z.namelist() if "/data_analysis_recipes_reproducibility/" in n and n.endswith(f"1_test_data_ST22_dummy.yaml"))
        recipe = yaml.safe_load(z.read(recipe_name).decode())
        spec = next(g["plots"][PID]["spec"] for g in recipe["analysis_groups"].values() if PID in g["plots"])
        assert {l["params"].get("random_state") for l in spec["layers"] if l.get("name") == "geom_jitter"} == {123}
    finally:
        PLOT_FILE.write_text(original)


def test_without_a_seed_in_the_recipe_the_reference_pane_shows_the_same_arrangement_as_my_view(browser, tmp_path):
    with running_app("qa", LOCAL, tmp_path) as url:
        page = browser.new_page()
        try:
            open_phenotype_plot(page, url, choose_recipe=True)
            page.locator("#plot_view input[value=CMP]").check(force=True)
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}", f"plot_group_{PID}_cmp_base")
            reference = page.locator(f"#plot_group_{PID}_cmp_base").screenshot()
            mine = page.locator(f"#plot_group_{PID}").screenshot()
            assert same_picture(reference, mine), "the reference pane was drawn with another seed than My view"
        finally:
            page.close()


def test_the_reshuffle_pin_reaches_home_and_the_export_when_the_audit_trail_is_off(browser, tmp_path):
    with running_app("pipeline-exploration-simple", PIPELINE, tmp_path) as url:
        page = browser.new_page()
        try:
            open_phenotype_plot(page, url, choose_recipe=False)
            run_a, png_a, _ = export_run_and_png(page)
            assert run_a["seed_source_per_plot"][PID] == "drawn"
            shown = page.locator(f"#plot_group_{PID}")
            before = shown.screenshot()
            btn = page.locator(f"#plot_reshuffle_btn_{PID}")
            expect(btn).to_be_visible(timeout=10_000)
            btn.click()
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}")
            assert not same_picture(shown.screenshot(), before), "HOME ignored the pinned seed (audit trail off)"
            run_b, png_b, _ = export_run_and_png(page)
            assert run_b["seed_source_per_plot"][PID] == "audit", "the export ignored the pinned seed (audit trail off)"
            assert run_b["seeds_per_plot"][PID] != run_a["seeds_per_plot"][PID]
            assert not same_picture(png_b, png_a)
        finally:
            page.close()
