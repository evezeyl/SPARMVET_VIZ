"""HOME draws a plot from the plot's own table, the Tier 2 plus the plot's tier-3 steps of the recipe, in the browser (piece A4, slice A of
the HOME audit redesign; review item M1).

# @deps
# consumes: app/handlers/opening_handlers.py (the refusal at the opening), app/handlers/home_theater.py (the plot render, Compare's left pane, the data preview), app/modules/orchestrator.py (materialize_tier3,
#   plot_read_error_text), app/modules/view_badge.py
# @end_deps

A staged recipe in a work folder of `tmpAI/` (no tracked file is touched), validated at once with `validate_data_analysis_recipe`: one table of
30 samples (sample_id, year, score = 1..30) and three plots of it that draw the same thing (a bar per year):

- `kept`: the recipe writes tier-3 steps for it, a filter `score >= 16` (15 of the 30 rows stay);
- `full`: no tier-3 steps;
- `broken` (a second app, only for the last test): a tier-3 step that fails on the values only (a cast of the sample names to a number). The opening
  refuses a recipe with such a plot (D-0327), so the app with `broken` shows the reason and none of its plots; the failure can no longer be seen in the data
  preview of a recipe that is open.

In the qa app features, with no audit step and no filter of the user, what a person can see:

- the data preview: on T3 the plot `kept` holds 15 rows and `full` 30; on T2 both hold the 30 rows of the stored Tier 2 (slice B: T3 is the table
  the plot shows, T2 the table after tier 2);
- the plot picture (one image per plot): `kept` and `full` are drawn from the same mapping, so equal pictures mean equal rows; they are
  different, in Exploration, in Audit mode and in the original pane of Compare, because every plot is drawn from its own table (a picture
  of `kept` equal to that of `full` is the old reader: the plot drawn from the Tier 2 of its target);
- no error text for `kept` and `full`; a recipe with `broken` is refused at the opening and the page names the plot and the step.

The staged recipe is checked with `validate_data_analysis_recipe` before the app starts (the load gate counts a plot's tier-3 steps once as
written and as read, `test_gate_accepts_tier3.py`); the fixture asserts it passes. The render itself is also covered headless by
`test_home_reads_the_plots_table.py::test_the_plot_and_the_original_pane_of_compare_are_drawn_from_the_plots_table_in_every_data_choice`.

Mutations (each seen failing, restored; the headless test for M1a and M1b): MUTATION M1a the plot render reads tier "T2" (`home_theater.py`, the line `_resolve_active_lf(spec, tier="T3")` of
`_group_plot_handler`); MUTATION M1b the same line of the Compare reference handler; MUTATION M1c `plot_read_error_text` returns the error as it is.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_plot_tier3.py -q
"""
import base64
import contextlib
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
from app.tests.browser_view import set_compare, set_mode, set_view, wait_preview_rows
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


@contextlib.contextmanager
def _running(work: Path, with_broken: bool):
    """The app on a deployment of its own: one table of 30 rows and the plots of it (the third, `broken`, only when asked), the second without tier-3 steps."""
    work.mkdir(parents=True, exist_ok=True)
    (work / "t.tsv").write_text("sample_id\tyear\tscore\n" + "".join(f"s{i}\t{2000 + i % 3}\t{i}\n" for i in range(1, N + 1)), encoding="utf-8")
    schema = minimal_schema(f"./{work.relative_to(REPO)}/t.tsv", {"sample_id": "String", "year": "Int64", "score": "Int64"}, entity_key="sample_id")
    schema["description"] = "One row per sample."
    plots = {}
    for plot_id, label, tier3, text in (
            (KEPT, "kept plot", [KEEP], "The plot whose recipe keeps the scores from 16."),
            (FULL, "full plot", None, "The same plot with no tier-3 steps."),
            (BROKEN, "broken plot", [CAST_NAMES], "The same plot whose tier-3 step fails on the values.")):
        if plot_id == BROKEN and not with_broken:
            continue
        plot = minimal_plot("t", {"x": "year"}, [{"name": "geom_bar", "params": {}}], label=label, tier3=tier3)
        plot["description"] = text
        plots[plot_id] = plot
    recipe = minimal_recipe("t", label="T", schemas={"t": schema}, plots=plots)
    recipe["info"]["description"] = "A table of 30 samples and the plots of it, for a browser test of the table a plot reads."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "TG", "description": "The one group."})
    recipe["analysis_groups"] = {"tg": group}
    recipes = work / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "t.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    problems = validate_data_analysis_recipe(recipes / "t.yaml")
    assert not problems, f"the staged recipe is refused by the load gate: {problems}"
    locations = {"raw_data": str(work), "data_analysis_recipes": str(recipes), "cache": str(work / "cache"),
                 "user_data": str(work / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = work / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "locations": locations,
                                          "default_data_analysis_recipe": "t", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    with open(work / "server.log", "w") as out:
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


@pytest.fixture(scope="module")
def staged_app():
    """The two plots a person can read: `kept` (tier-3 steps) and `full` (none)."""
    with _running(WORK, with_broken=False) as url:
        yield url


@pytest.fixture
def broken_app():
    """A recipe with a third plot whose tier-3 step fails on the values: the opening refuses it (D-0327)."""
    with _running(WORK / "broken", with_broken=True) as url:
        yield url


def _rows(page: Page, n: int) -> None:
    """The data table says it holds n rows ("... of 15"): a retrying assertion on the app's state."""
    wait_preview_rows(page, n)


def _plot_tab(page: Page, plot_id: str) -> None:
    page.locator(f".nav-link:has-text('{plot_id} plot')").first.click()
    _wait_shiny(page, 30_000)


def _data_view(page: Page, tier: str) -> None:
    set_view(page, tier)


def _plot_mode(page: Page, mode: str) -> None:
    """"exploration" (the Result plot), "audit" (the audited plot) or "compare" (Audit mode with Compare on)."""
    set_mode(page, "exploration" if mode == "exploration" else "audit")
    if mode != "exploration":
        set_compare(page, mode == "compare")


def _right_panel_open_by_hand(page: Page) -> None:
    """The right panel is closed in Exploration and open in Audit mode, so the main panel (and the picture of a plot, which follows its width) is
    wider in Exploration. To compare pictures of the modes the user opens the panel by hand in Exploration (it is empty there, D-0383): the
    two panes then have the same width."""
    width = "() => { const e = document.getElementById('audit_sidebar'); return e ? e.getBoundingClientRect().width : 0; }"
    if page.evaluate(width) < 1:
        page.locator(".bslib-sidebar-layout:has(> #audit_sidebar) > .collapse-toggle").click()
    page.wait_for_function(f"() => ({width})() > 50", timeout=15_000)
    page.wait_for_timeout(800)                           # the plot is drawn again for its new width
    _wait_shiny(page, 30_000)


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
    _rows(page, N - THRESHOLD + 1)                       # T3 of the plot with tier-3 steps: the 15 kept rows
    _plot_tab(page, FULL)
    _rows(page, N)                                       # the plot without: the 30 rows
    _data_view(page, "T2")
    _rows(page, N)                                       # T2: the stored Tier 2, 30 rows
    _plot_tab(page, KEPT)
    _rows(page, N)
    assert not [a for a in _alerts(page) if "error" in a.lower()], "no error for the plots that can be read"


def test_every_plot_is_drawn_from_its_own_table_in_exploration_in_audit_mode_and_in_compare(page: Page, staged_app):
    _start(page, staged_app)
    pictures = {}
    for view in ("exploration", "audit"):
        _plot_mode(page, view)
        _right_panel_open_by_hand(page)                  # the same pane width in both modes: pictures of different widths are never the same picture
        for plot_id in (KEPT, FULL):
            _plot_tab(page, plot_id)
            pictures[(view, plot_id)] = _picture(page, f"plot_group_{plot_id}")
            assert _red_pixels(pictures[(view, plot_id)]) == 0, f"the plot {plot_id} in view {view} is an error picture"
        assert not _same_picture(pictures[(view, KEPT)], pictures[(view, FULL)]), (
            f"view {view}: the plot with tier-3 steps is drawn like the plot without: it was drawn from the Tier 2 of its target")
    # with no audit step of the user, the audited plot is the plot's table: the same picture as the Result
    assert _same_picture(pictures[("exploration", KEPT)], pictures[("audit", KEPT)])
    assert _same_picture(pictures[("exploration", FULL)], pictures[("audit", FULL)])
    # Compare: the left pane is the original (Result) plot, the plot's table (D-0147), and differs between the two plots as well
    _plot_mode(page, "compare")
    left = {}
    for plot_id in (KEPT, FULL):
        _plot_tab(page, plot_id)
        left[plot_id] = _picture(page, f"plot_group_{plot_id}_cmp_base")
        assert _red_pixels(left[plot_id]) == 0
    assert not _same_picture(left[KEPT], left[FULL]), "Compare's left pane draws the plot with tier-3 steps from the Tier 2 of its target"
    assert np.asarray(left[KEPT]).shape == np.asarray(left[FULL]).shape


def test_a_tier3_step_that_fails_on_the_values_refuses_the_recipe_at_the_opening_and_names_the_plot_and_the_step(page: Page, broken_app):
    """D-0327: a recipe whose plot cannot be built is refused when it is opened, with a plain reason. Before the opening existed the failure showed in the data
    preview of that plot; after it, no recipe that fails reaches a view, so the reason is shown where HOME says the recipe is not used (here the only recipe)."""
    page.goto(broken_app)
    page.wait_for_selector("#sidebar_nav", timeout=60_000)
    _wait_shiny(page, 240_000)
    theater = page.locator("#dynamic_tabs")
    expect(theater).to_contain_text("could not be opened", timeout=60_000)
    expect(theater).to_contain_text(f"'{BROKEN}'", timeout=10_000)
    expect(theater).to_contain_text("step 1", timeout=10_000)
    expect(page.locator(".nav-link:has-text('TG')")).to_have_count(0)   # no plot of this recipe is shown: nothing of it is used
