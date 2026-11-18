"""A WARNING of a plot in the browser (VIZ-FOLLOWUPS-1): the plot is drawn, and the Alerts panel holds the warning as a warning.

# @deps
# consumes: app/handlers/home_theater.py, app/modules/plot_issue_reporter.py, libs/viz_factory/src/viz_factory/viz_factory.py
# @end_deps

A staged recipe of one table and one plot whose `plot_defaults:` block names a palette that exists nowhere
(`no_such_palette`; an unknown KEY of the block is refused by the recipe check, so it never reaches the plot): the factory
draws the plot in the default colours and warns the author. In the qa app features the plot must be drawn
(no red error text in its place), and the Alerts panel must hold ONE entry about the palette, in the warning colour, however
often the plot is drawn again.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_plot_warnings.py -q
"""
import io
import os
import socket
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pytest
import yaml
from PIL import Image
from playwright.sync_api import Page, expect

from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_plot_warnings"
PLOT = "plot_warned"
LABELS = {PLOT: "Warned plot"}
ROWS = [("s1", "a", 1.0), ("s2", "a", 2.0), ("s3", "b", 3.0), ("s4", "b", 4.0), ("s5", "c", 5.0)]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def staged_app():
    """The app on a deployment of its own, with a recipe whose plot_defaults names a palette that does not exist."""
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "table.tsv").write_text("sample_id\tgroup\tvalue\n" + "".join(f"{a}\t{b}\t{c}\n" for a, b, c in ROWS), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_plot_warnings/table.tsv", {"sample_id": "String", "group": "String", "value": "Float64"},
                            entity_key="sample_id")
    schema["description"] = "One row per sample."
    plots = {PLOT: minimal_plot("table", {"x": "group", "fill": "group"}, [{"name": "geom_bar", "params": {}}], label=LABELS[PLOT])}
    for plot in plots.values():
        plot["description"] = "A plot of the staged table."
    recipe = minimal_recipe("staged", label="Staged", schemas={"table": schema}, plots=plots)
    recipe["info"]["description"] = "A table and one plot whose plot_defaults names an unknown palette, for a browser test."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "Plots", "description": "The one group."})
    recipe["analysis_groups"] = {"plots_group": group}
    recipe["plot_defaults"] = {"palette": "no_such_palette"}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "staged.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot warnings", "locations": locations,
                                          "default_data_analysis_recipe": "staged", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment))
    with open(WORK / "server.log", "w") as out:
        proc = subprocess.Popen(app_command(port),
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


def _server_log() -> str:
    return (WORK / "server.log").read_text(errors="replace")


def _show_plot(page: Page, plot_id: str) -> None:
    page.locator(f".nav-link:has-text('{LABELS[plot_id]}')").first.click()
    _wait_shiny(page, 20_000)


def _image_of(page: Page, selector: str) -> Image.Image:
    box = page.locator(selector)
    expect(box.locator("img")).to_be_visible(timeout=20_000)
    return Image.open(io.BytesIO(box.locator("img").screenshot())).convert("RGB")


def _red_pixels(image: Image.Image) -> int:
    """Pixels of the error colour (#d62828, anti-aliased); a good plot of this recipe has none."""
    pixels = np.asarray(image)
    return int(((pixels[..., 0] > 170) & (pixels[..., 1] < 100) & (pixels[..., 2] < 100)).sum())


def _nonblank(image: Image.Image) -> bool:
    return len(np.unique(np.asarray(image).reshape(-1, 3), axis=0)) > 3


def _open_home(page: Page, url: str) -> None:
    _open_app(page, url)
    page.wait_for_selector(".nav-link:has-text('Plots')", timeout=60_000)
    _wait_shiny(page, 30_000)


def _alert_rows(page: Page) -> list:
    header = page.locator("#notification_log_accordion .accordion-button")
    if "collapsed" in (header.get_attribute("class") or ""):
        header.click()
        page.wait_for_timeout(400)
    return page.locator("#notification_log_accordion .spv-tag-row").all()


def _about_the_palette(rows: list) -> list:
    return [r for r in rows if "no_such_palette" in r.inner_text()]


def test_the_plot_is_drawn_and_the_warning_is_in_the_alerts_as_a_warning(page: Page, staged_app):
    _open_home(page, staged_app)
    for _ in range(3):   # drawn again: the warning stays one entry
        _show_plot(page, PLOT)
    image = _image_of(page, f"#plot_group_{PLOT}")
    assert _nonblank(image) and _red_pixels(image) == 0, "the plot is drawn, no error text in its place"
    found = _about_the_palette(_alert_rows(page))
    assert len(found) == 1, [r.inner_text() for r in _alert_rows(page)]
    message_colour = found[0].locator("span").nth(1).evaluate("e => getComputedStyle(e).color")
    assert message_colour == "rgb(202, 111, 0)", f"the warning colour (#ca6f00), not the error colour: {message_colour}"
    assert "No current reactive context" not in _server_log()
