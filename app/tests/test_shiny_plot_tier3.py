"""HOME draws a plot from the plot's own table, the Tier 2 plus the plot's tier-3 steps of the recipe, in the browser (piece A4, slice A of
the HOME audit redesign; review item M1).

# @deps
# consumes: app/handlers/home_theater.py (the plot render, Compare's left pane, the data preview), app/modules/orchestrator.py (materialize_tier3,
#   plot_read_error_text), app/modules/view_badge.py
# @end_deps

A staged recipe in a work folder of `tmpAI/` (no tracked file is touched), validated at once with `validate_data_analysis_recipe`: one table of
30 samples (sample_id, year, score = 1..30) and three plots of it that draw the same thing (a bar per year):

- `kept`: the recipe writes tier-3 steps for it, a filter `score >= 16` (15 of the 30 rows stay);
- `full`: no tier-3 steps;
- `broken`: a tier-3 step that fails on the values only (a cast of the sample names to a number), so the table is returned but cannot be read.

In the qa app features, with no audit step and no filter of the user, what a person can see:

- the data preview: in "My view" the plot `kept` holds 15 rows and `full` 30; in "Result" both hold the 30 rows of the stored Tier 2
  (the views are not changed by this piece: it is the owner's question whether "Result" of `kept` should show its table);
- the plot picture (one image per plot): `kept` and `full` are drawn from the same mapping, so equal pictures mean equal rows; they are
  different, in "Result" and "My view" of the plot and in the left pane of Compare, because every plot is drawn from its own table (a picture
  of `kept` equal to that of `full` is the old reader: the plot drawn from the Tier 2 of its target);
- no error text for `kept` and `full`; for `broken` the data preview says an error and names the plot (a value-dependent failure shows at the
  read, and the plot's name is added by the consumer, `plot_read_error_text`).

The staged recipe is checked with `validate_data_analysis_recipe` before the app starts (the load gate counts a plot's tier-3 steps once as
written and as read, `test_gate_accepts_tier3.py`); the fixture asserts it passes. The render itself is also covered headless by
`test_home_reads_the_plots_table.py::test_the_plot_and_the_reference_pane_of_compare_are_drawn_from_the_plots_table_in_every_view`.

Mutations (each seen failing, restored; the headless test for M1a and M1b): MUTATION M1a the plot render reads tier "T2" (`home_theater.py`, the line `_resolve_active_lf(spec, tier="T3")` of
`_group_plot_handler`); MUTATION M1b the same line of the Compare reference handler; MUTATION M1c `plot_read_error_text` returns the error as it is.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_plot_tier3.py -q
"""
import base64
import io
import subprocess
import time
import urllib.request
from pathlib import Path

import numpy as np
import pytest
import yaml
from PIL import Image
from playwright.sync_api import Page, expect

from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _wait_shiny
from app.tests.test_shiny_step_order import N, _free_port, _red_pixels, _same_picture
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_plot_tier3"
KEPT, FULL, BROKEN = "kept", "full", "broken"
THRESHOLD = 16     # score >= 16 keeps 15 of the 30 rows
KEEP = {"action": "modif_filter", "column": "score", "op": "ge", "value": THRESHOLD, "na": "remove"}
CAST_NAMES = {"action": "polars_cast", "columns": ["sample_id"], "dtype": "Int64"}   # "s1" is not a number: fails on the values only


@pytest.fixture(scope="module")
def staged_app():
    """The app on a deployment of its own: one table of 30 rows and three plots of it, the second without tier-3 steps."""
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "t.tsv").write_text("sample_id\tyear\tscore\n" + "".join(f"s{i}\t{2000 + i % 3}\t{i}\n" for i in range(1, N + 1)), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_plot_tier3/t.tsv", {"sample_id": "String", "year": "Int64", "score": "Int64"}, entity_key="sample_id")
    schema["description"] = "One row per sample."
    plots = {}
    for plot_id, label, tier3, text in (
            (KEPT, "kept plot", [KEEP], "The plot whose recipe keeps the scores from 16."),
            (FULL, "full plot", None, "The same plot with no tier-3 steps."),
            (BROKEN, "broken plot", [CAST_NAMES], "The same plot whose tier-3 step fails on the values.")):
        plot = minimal_plot("t", {"x": "year"}, [{"name": "geom_bar", "params": {}}], label=label, tier3=tier3)
        plot["description"] = text
        plots[plot_id] = plot
    recipe = minimal_recipe("t", label="T", schemas={"t": schema}, plots=plots)
    recipe["info"]["description"] = "A table of 30 samples and three plots, for a browser test of the table a plot reads."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "TG", "description": "The one group."})
    recipe["analysis_groups"] = {"tg": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "t.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    problems = validate_data_analysis_recipe(recipes / "t.yaml")
    assert not problems, f"the staged recipe is refused by the load gate: {problems}"
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot tier3", "locations": locations,
                                          "default_data_analysis_recipe": "t", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    with open(WORK / "server.log", "w") as out:
        proc = subprocess.Popen(app_command(port), cwd=REPO, env=app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment)),
                                stdout=out, stderr=subprocess.STDOUT)
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


def _rows(page: Page, n: int) -> None:
    """The data table says it holds n rows ("... of 15"): a retrying assertion on the app's state."""
    expect(page.locator("#home_data_preview .shiny-data-grid-summary")).to_contain_text(f" of {n}", timeout=20_000)


def _plot_tab(page: Page, plot_id: str) -> None:
    page.locator(f".nav-link:has-text('{plot_id} plot')").first.click()
    _wait_shiny(page, 30_000)


def _data_view(page: Page, tier: str) -> None:
    page.locator(f"#tier_toggle input[value={tier}]").check(force=True)
    _wait_shiny(page)


def _plot_view(page: Page, view: str) -> None:
    page.locator(f"#plot_view input[value={view}]").check(force=True)
    _wait_shiny(page)


def _picture(page: Page, output_id: str) -> Image.Image:
    """The image the output shows now: the image itself (a notification can lie over a screenshot), after Shiny is idle."""
    _wait_shiny(page, 30_000)
    expect(page.locator(f"#{output_id} img")).to_be_visible(timeout=20_000)
    data = page.evaluate("(sel) => document.querySelector(sel + ' img').src", f"#{output_id}")
    return Image.open(io.BytesIO(base64.b64decode(data.split(",", 1)[1]))).convert("RGB")


def _start(page: Page, url: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('TG')").first.click()
    _wait_shiny(page)
    expect(page.locator(f"#plot_group_{KEPT} img")).to_be_visible(timeout=30_000)
    _wait_shiny(page, 30_000)


def _alerts(page: Page) -> list:
    header = page.locator("#notification_log_accordion .accordion-button")
    if "collapsed" in (header.get_attribute("class") or ""):
        header.click()
        page.wait_for_timeout(400)
    return page.locator("#notification_log_accordion .spv-tag-row").all_inner_texts()


def test_the_data_preview_of_each_plot_holds_the_rows_of_the_table_it_reads(page: Page, staged_app):
    _start(page, staged_app)
    _data_view(page, "T3")
    _plot_tab(page, KEPT)
    _rows(page, N - THRESHOLD + 1)                       # My view of the plot with tier-3 steps: the 15 kept rows
    _plot_tab(page, FULL)
    _rows(page, N)                                       # the plot without: the 30 rows
    _data_view(page, "T2")
    _rows(page, N)                                       # Result: the stored Tier 2, 30 rows (the view is unchanged by this piece)
    _plot_tab(page, KEPT)
    _rows(page, N)
    assert not [a for a in _alerts(page) if "error" in a.lower()], "no error for the plots that can be read"


def test_every_plot_is_drawn_from_its_own_table_in_result_in_my_view_and_in_compare(page: Page, staged_app):
    _start(page, staged_app)
    pictures = {}
    for view in ("T2", "T3"):
        _plot_view(page, view)
        for plot_id in (KEPT, FULL):
            _plot_tab(page, plot_id)
            pictures[(view, plot_id)] = _picture(page, f"plot_group_{plot_id}")
            assert _red_pixels(pictures[(view, plot_id)]) == 0, f"the plot {plot_id} in view {view} is an error picture"
        assert not _same_picture(pictures[(view, KEPT)], pictures[(view, FULL)]), (
            f"view {view}: the plot with tier-3 steps is drawn like the plot without: it was drawn from the Tier 2 of its target")
    # with no filter and no audit step of the user, My view is the plot's table: the same picture as Result
    assert _same_picture(pictures[("T2", KEPT)], pictures[("T3", KEPT)])
    assert _same_picture(pictures[("T2", FULL)], pictures[("T3", FULL)])
    # Compare: the left pane is the Result plot, the plot's table (ADR-086), and differs between the two plots as well
    _plot_view(page, "CMP")
    left = {}
    for plot_id in (KEPT, FULL):
        _plot_tab(page, plot_id)
        left[plot_id] = _picture(page, f"plot_group_{plot_id}_cmp_base")
        assert _red_pixels(left[plot_id]) == 0
    assert not _same_picture(left[KEPT], left[FULL]), "Compare's left pane draws the plot with tier-3 steps from the Tier 2 of its target"
    assert np.asarray(left[KEPT]).shape == np.asarray(left[FULL]).shape


def test_a_tier3_step_that_fails_on_the_values_is_named_with_its_plot_in_the_data_preview(page: Page, staged_app):
    _start(page, staged_app)
    _data_view(page, "T3")
    _plot_tab(page, BROKEN)
    expect(page.locator("#home_data_preview")).to_contain_text(f"'{BROKEN}'", timeout=20_000)
    expect(page.locator("#home_data_preview")).to_contain_text("tier-3 steps")
    # the other plots are not touched by it
    _plot_tab(page, KEPT)
    _rows(page, N - THRESHOLD + 1)
