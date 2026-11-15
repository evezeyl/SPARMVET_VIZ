"""SEED-HOLDS-1 (ADR-104): the seed lines of the real handlers, in a real app (browser).

The pure functions are tested in test_plot_seeds.py; what only a running app can show is that the handlers
CALL them and put nothing between (a flag, a replaced number, a dropped argument). HOME draws no seed
(Eve, 2026-11-15): a layer that writes a number keeps it, a layer that writes none uses 0, in every place.

  1. a seed written in the recipe (123) holds in HOME (two sessions show the same picture), in the comparison
     reference pane, in the export and its record
  2. a recipe that writes no seed: 0 in every place, so two sessions show the SAME arrangement, the reference
     pane shows the same as My view, and the export records seed 0 as `default` and writes it into the
     reproducibility recipe
  3. with the audit trail off (`pipeline-exploration-simple`: t3_sandbox_enabled false) the Reshuffle pin reaches
     HOME and the export, and the export lists it as a step (t3_steps.yaml, report)

Each scenario starts its own app on a STAGED COPY of the recipes folder (the tracked plot file is never edited).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_shiny_seed_places.py -q
"""
import io
import re
import shutil
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
RECIPES = REPO / "config/data_analysis_recipes/pipelines"
PLOT_FILE_IN_RECIPES = Path("1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml")
WRITTEN = 'position: "jitter", random_state: 0}'     # the shipped plot writes its seed (item 3 of SEED-HOLDS-1)
LOCAL = "config/deployment/local/local.yaml"
PIPELINE = "config/deployment/pipeline_test/pipeline_test.yaml"


def staged_deployment(deployment: str, layer_params: str, tmp_path: Path, recipe_seed: int | None = None) -> str:
    """A deployment file whose recipes folder is a COPY of the shipped one, with another written seed (or none) on the
    jitter layer of the phenotype plot. The repository is never edited, so a killed run leaves nothing behind."""
    recipes = tmp_path / "recipes"
    shutil.copytree(RECIPES, recipes)
    plot_file = recipes / PLOT_FILE_IN_RECIPES
    original = plot_file.read_text()
    assert WRITTEN in original, "the plot file changed: update this test"
    plot_file.write_text(original.replace(WRITTEN, layer_params))
    if recipe_seed is not None:                 # PROVISIONAL (S3): the one seed of the whole recipe
        recipe_file = recipes / "1_test_data_ST22_dummy.yaml"
        text = recipe_file.read_text()
        assert "plot_defaults:\n  theme: theme_minimal\n" in text
        recipe_file.write_text(text.replace("plot_defaults:\n  theme: theme_minimal\n",
                                            f"plot_defaults:\n  random_state: {recipe_seed}\n  theme: theme_minimal\n"))
    text = (REPO / deployment).read_text()
    text, n = re.subn(r'(?m)^(\s*data_analysis_recipes:\s*).*$', lambda m: f'{m.group(1)}"{recipes}/"', text)
    assert n == 1
    staged = tmp_path / "deployment.yaml"
    staged.write_text(text)
    return str(staged)


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


def recipe_seeds(z: zipfile.ZipFile) -> set:
    """The `random_state` written on the jitter layers of the plot in the bundle's reproducibility recipe."""
    name = next(n for n in z.namelist() if "/data_analysis_recipes_reproducibility/" in n and n.endswith("1_test_data_ST22_dummy.yaml"))
    recipe = yaml.safe_load(z.read(name).decode())
    spec = next(g["plots"][PID]["spec"] for g in recipe["analysis_groups"].values() if PID in g["plots"])
    return {l["params"].get("random_state") for l in spec["layers"] if (l.get("params") or {}).get("position") == "jitter"}


def seed_line(page: Page) -> str:
    """The seed line HOME shows with the phenotype plot (text only; it is never part of the picture)."""
    return " ".join(page.locator(f"#plot_seed_{PID}").inner_text().split())


def same_picture(a: bytes, b: bytes) -> bool:
    return ImageChops.difference(Image.open(io.BytesIO(a)).convert("RGB"),
                                 Image.open(io.BytesIO(b)).convert("RGB")).getbbox() is None


def test_a_seed_written_in_the_recipe_holds_in_home_the_reference_pane_and_the_export(browser, tmp_path):
    with running_app("qa", staged_deployment(LOCAL, 'position: "jitter", random_state: 123}', tmp_path), tmp_path) as url:
        shots, runs = [], []
        for _ in range(2):                     # two sessions: each would draw its own seed if HOME drew over the recipe
            context = browser.new_context()
            page = context.new_page()
            try:
                open_phenotype_plot(page, url, choose_recipe=True)
                shots.append(page.locator(f"#plot_group_{PID}").screenshot())
                assert seed_line(page) == "seed 123, written in the recipe"
                expect(page.locator(f"#plot_reshuffle_btn_{PID}")).to_have_count(0)
                if len(shots) == 1:
                    page.locator("#plot_view input[value=CMP]").check(force=True)
                    _wait_shiny(page)
                    settle(page, f"plot_group_{PID}", f"plot_group_{PID}_cmp_base")
                    reference = page.locator(f"#plot_group_{PID}_cmp_base").screenshot()
                    mine = page.locator(f"#plot_group_{PID}").screenshot()
                    assert same_picture(reference, mine), "the reference pane does not show the recipe's seed"
                runs.append(export_run_and_png(page, with_recipe=len(runs) == 0))
            finally:
                context.close()
    assert same_picture(shots[0], shots[1]), "two sessions show different pictures: HOME drew over the recipe's seed"
    for run, _png, _z in runs:
        assert run["seeds_per_plot"][PID] == 123 and run["seed_source_per_plot"][PID] == "recipe"
        assert [r["seed"] for r in run["seeds_per_layer"][PID]] == [123]
        assert run["seeds_added_to_recipe"] == []
    assert same_picture(runs[0][1], runs[1][1]), "the export of two sessions differs although the recipe fixes the seed"
    assert recipe_seeds(runs[0][2]) == {123}


def test_without_a_seed_in_the_recipe_every_place_uses_zero_and_two_sessions_show_the_same_arrangement(browser, tmp_path):
    with running_app("qa", staged_deployment(LOCAL, 'position: "jitter"}', tmp_path), tmp_path) as url:
        page = browser.new_page()
        try:
            open_phenotype_plot(page, url, choose_recipe=True)
            assert seed_line(page) == "seed 0, default (nothing written in the recipe)"
            page.locator("#plot_view input[value=CMP]").check(force=True)
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}", f"plot_group_{PID}_cmp_base")
            reference = page.locator(f"#plot_group_{PID}_cmp_base").screenshot()
            mine = page.locator(f"#plot_group_{PID}").screenshot()
            assert same_picture(reference, mine), "the reference pane was drawn with another seed than My view"
            # a second session shows the SAME arrangement: nothing is drawn per session any more
            other_context = browser.new_context()
            other = other_context.new_page()
            try:
                open_phenotype_plot(other, url, choose_recipe=True)
                other_view = other.locator(f"#plot_group_{PID}").screenshot()
            finally:
                other_context.close()
            page.locator("#plot_view input[value=T3]").check(force=True)
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}")
            assert same_picture(other_view, page.locator(f"#plot_group_{PID}").screenshot()), \
                "two sessions show different arrangements: HOME drew a seed"
            run, _png, z = export_run_and_png(page, with_recipe=True)
        finally:
            page.close()
    assert run["seeds_per_plot"][PID] == 0 and run["seed_source_per_plot"][PID] == "default"
    assert [(r["seed"], r["source"]) for r in run["seeds_per_layer"][PID]] == [(0, "default")]
    assert [(a["plot"], a["seed"], a["recipe_wrote"]) for a in run["seeds_added_to_recipe"]] == [(PID, 0, None)]
    assert recipe_seeds(z) == {0}, "every seed used is written in the reproducibility recipe"


def test_the_reshuffle_pin_reaches_home_and_the_export_when_the_audit_trail_is_off(browser, tmp_path):
    with running_app("pipeline-exploration-simple", staged_deployment(PIPELINE, 'position: "jitter"}', tmp_path), tmp_path) as url:
        page = browser.new_page()
        try:
            open_phenotype_plot(page, url, choose_recipe=False)
            run_a, png_a, _ = export_run_and_png(page)
            assert run_a["seed_source_per_plot"][PID] == "default" and run_a["seeds_per_plot"][PID] == 0
            assert seed_line(page) == "seed 0, default (nothing written in the recipe)"
            shown = page.locator(f"#plot_group_{PID}")
            before = shown.screenshot()
            btn = page.locator(f"#plot_reshuffle_btn_{PID}")
            expect(btn).to_be_visible(timeout=10_000)
            btn.click()
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}")
            assert not same_picture(shown.screenshot(), before), "HOME ignored the pinned seed (audit trail off)"
            # once pinned there is nothing left to reshuffle: the control disappears, and the plot shows no error
            expect(page.locator(f"#plot_reshuffle_btn_{PID}")).to_have_count(0, timeout=8_000)
            assert page.locator(".shiny-output-error").count() == 0
            pinned_line = seed_line(page)
            assert re.fullmatch(r"seed \d+, pinned in the audit Remove the pinned seed", pinned_line), pinned_line
            pinned_picture = shown.screenshot()
            # the way back: remove the pinned seed; the plot returns to the recipe's seed and Reshuffle is offered again
            page.locator(f"#plot_unpin_btn_{PID}").click()
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}")
            expect(page.locator(f"#plot_reshuffle_btn_{PID}")).to_be_visible(timeout=8_000)
            assert seed_line(page) == "seed 0, default (nothing written in the recipe)"
            assert same_picture(shown.screenshot(), before), "removing the pinned seed did not bring the plot back"
            assert not same_picture(shown.screenshot(), pinned_picture)
            # after the way back the export holds no trace of the pin: the recipe's seed, no step, no word in the report
            run_c, png_c, z_c = export_run_and_png(page)
            assert run_c["seed_source_per_plot"][PID] == "default" and run_c["seeds_per_plot"][PID] == 0
            assert same_picture(png_c, png_a), "the export after removing the pin is not the export before it"
            names = z_c.namelist()
            assert not any(n.endswith("t3_steps.yaml") for n in names), "a step file was written for a removed pin"
            report_c = z_c.read(next(n for n in names if n.endswith("report.qmd"))).decode()
            assert "random_seed" not in report_c and "pinned" not in report_c.lower()
            btn.click()                          # pin again for the export below
            _wait_shiny(page)
            settle(page, f"plot_group_{PID}")
            run_b, png_b, z = export_run_and_png(page)
        finally:
            page.close()
    assert run_b["seed_source_per_plot"][PID] == "audit", "the export ignored the pinned seed (audit trail off)"
    assert run_b["seeds_per_plot"][PID] != 0
    assert not same_picture(png_b, png_a)
    # the pin is a step of the audit trail: listed in t3_steps.yaml and in the report
    steps = yaml.safe_load(z.read(next(n for n in z.namelist() if n.endswith("t3_steps.yaml"))).decode())
    (step,) = steps["t3_steps"][PID]
    assert step["action"] == "random_seed" and step["seed"] == run_b["seeds_per_plot"][PID] and step["reason"]
    report = z.read(next(n for n in z.namelist() if n.endswith("report.qmd"))).decode()
    assert "random_seed" in report and str(step["seed"]) in report


def test_a_recipe_default_seed_is_shown_holds_and_hides_reshuffle(browser, tmp_path):
    """PROVISIONAL (S3): plot_defaults.random_state is the seed of a layer that writes none; HOME says so, Reshuffle is
    not offered (a click would override the recipe's seed) and the export records it as the recipe default."""
    with running_app("qa", staged_deployment(LOCAL, 'position: "jitter"}', tmp_path, recipe_seed=5), tmp_path) as url:
        page = browser.new_page()
        try:
            open_phenotype_plot(page, url, choose_recipe=True)
            assert seed_line(page) == "seed 5, recipe default (plot_defaults)"
            expect(page.locator(f"#plot_reshuffle_btn_{PID}")).to_have_count(0)
            run, _png, _z = export_run_and_png(page)
        finally:
            page.close()
    assert run["seeds_per_plot"][PID] == 5 and run["seed_source_per_plot"][PID] == "recipe default"
    assert run["seeds_added_to_recipe"] == []
