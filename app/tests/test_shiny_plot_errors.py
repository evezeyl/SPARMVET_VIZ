"""A plot that cannot be drawn, in the browser (VIZ-STANDARD-1, V7): the message in the plot's place, ONE alert, the rest works.

# @deps
# consumes: app/handlers/home_theater.py, app/modules/plot_issue_reporter.py, app/handlers/export_handlers.py, app/modules/wrangle_studio.py
# @end_deps

A staged recipe of one table and three plots in one group; the middle one has `alpha: lots` in `geom_bar`, a value plotnine
refuses only when it draws (a shipped file is not touched). What must hold, in the qa app features:

- the message is drawn in the failing plot's place (a red-text picture, not a Shiny error box) and the other two plots draw;
- the Alerts panel holds ONE entry for it however often the plot is drawn again (tab changes, the Compare view);
- the session goes on: the Export panel opens and a bundle downloads, with the message once in `plots/<id>_ERROR.txt` and
  a report that says the plot was not drawn, with no link to a picture that is not there;
- the Compare pane shows the message too.

The Blueprint plot preview (`architect_active_plot` in `wrangle_studio.py`) is not mounted in the page today (no `output_plot` of it
exists), so it cannot be seen in a browser; its draw error is shown in the plot's place by the same `show_draw_errors` call, which
`test_plot_callers_are_checked.py` guards.

The first version of this report read a reactive value outside a reactive context in `session.on_flushed`: the alert was lost,
the other plots stayed blank and the Export panel opened empty.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_plot_errors.py -q
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

from app.tests.browser_view import set_compare, set_mode
from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_plot_errors"
GOOD_A, BAD, GOOD_B = "plot_good_a", "plot_bad", "plot_good_b"
LABELS = {GOOD_A: "Good A", BAD: "Bad plot", GOOD_B: "Good B"}
ROWS = [("s1", "a", 1.0), ("s2", "a", 2.0), ("s3", "b", 3.0), ("s4", "b", 4.0), ("s5", "c", 5.0)]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def staged_app():
    """The app on a deployment of its own, with a recipe whose second plot fails when it is drawn."""
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "table.tsv").write_text("sample_id\tgroup\tvalue\n" + "".join(f"{a}\t{b}\t{c}\n" for a, b, c in ROWS), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_plot_errors/table.tsv", {"sample_id": "String", "group": "String", "value": "Float64"},
                            entity_key="sample_id")
    schema["description"] = "One row per sample."
    plots = {
        GOOD_A: minimal_plot("table", {"x": "group"}, [{"name": "geom_bar", "params": {}}], label=LABELS[GOOD_A]),
        BAD: minimal_plot("table", {"x": "group"}, [{"name": "geom_bar", "params": {"alpha": "lots"}}], label=LABELS[BAD]),
        GOOD_B: minimal_plot("table", {"x": "group", "y": "value"}, [{"name": "geom_col", "params": {}}], label=LABELS[GOOD_B]),
    }
    for plot in plots.values():
        plot["description"] = "A plot of the staged table."
    recipe = minimal_recipe("staged", label="Staged", schemas={"table": schema}, plots=plots)
    recipe["info"]["description"] = "A table and three plots, one of which cannot be drawn, for a browser test."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "Plots", "description": "The one group."})
    recipe["analysis_groups"] = {"plots_group": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "staged.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot errors", "locations": locations,
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


def _alerts(page: Page) -> list:
    header = page.locator("#notification_log_accordion .accordion-button")
    if "collapsed" in (header.get_attribute("class") or ""):
        header.click()
        page.wait_for_timeout(400)
    return page.locator("#notification_log_accordion .spv-tag-row").all_inner_texts()


def _mentions_the_bad_plot(alerts: list) -> list:
    return [a for a in alerts if "Plot 'plot_bad'" in a]


def test_the_message_is_in_the_failing_plots_place_and_the_other_plots_draw(page: Page, staged_app):
    _open_home(page, staged_app)
    _show_plot(page, GOOD_A)
    good_a = _image_of(page, f"#plot_group_{GOOD_A}")
    assert _nonblank(good_a) and _red_pixels(good_a) == 0
    _show_plot(page, BAD)
    bad = _image_of(page, f"#plot_group_{BAD}")
    assert _red_pixels(bad) > 100, "the message (red text) is drawn where the plot would be"
    expect(page.locator(f"#plot_group_{BAD}.shiny-output-error")).to_have_count(0)
    _show_plot(page, GOOD_B)
    good_b = _image_of(page, f"#plot_group_{GOOD_B}")
    assert _nonblank(good_b) and _red_pixels(good_b) == 0, "a failing plot does not blank the others"
    assert "No current reactive context" not in _server_log()


def test_the_alerts_panel_holds_one_entry_however_often_the_plot_is_drawn(page: Page, staged_app):
    _open_home(page, staged_app)
    for _ in range(3):   # draw it again: other tabs and back
        _show_plot(page, GOOD_A)
        _show_plot(page, BAD)
    found = _mentions_the_bad_plot(_alerts(page))
    assert len(found) == 1, found
    assert "'alpha'" in found[0] and "Fix:" in found[0], found
    assert "No current reactive context" not in _server_log()


def test_the_compare_pane_shows_the_message_too_and_the_alert_stays_one(page: Page, staged_app):
    _open_home(page, staged_app)
    _show_plot(page, BAD)
    set_mode(page, "audit")
    set_compare(page, True)
    reference = _image_of(page, f"#plot_group_{BAD}_cmp_base")
    assert _red_pixels(reference) > 100, "the original pane of Compare shows the message"
    assert _red_pixels(_image_of(page, f"#plot_group_{BAD}")) > 100, "and so does the audited plot"
    assert len(_mentions_the_bad_plot(_alerts(page))) <= 2, "one entry for the plot, one for its original pane (a different place)"
    set_compare(page, False)
    set_mode(page, "exploration")


def test_the_export_panel_opens_and_the_bundle_says_the_plot_was_not_drawn(page: Page, staged_app):
    _open_home(page, staged_app)
    _show_plot(page, BAD)
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion").get_by_text("Export").first.click()
        _wait_shiny(page)
    expect(page.locator("#export_bundle_download")).to_be_visible(timeout=10_000)
    page.locator("#export_user_name").fill("autotest")
    with page.expect_download(timeout=120_000) as info:
        page.locator("#export_bundle_download").click()
    z = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
    names = z.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
    stub = next(n for n in names if n.endswith(f"plots/{BAD}_ERROR.txt"))
    text = z.read(stub).decode()
    assert text.count("Fix:") == 1 and "'alpha'" in text, text
    drawn = [n for n in names if "/plots/" in n and not n.endswith("_ERROR.txt")]
    assert any(GOOD_A in n for n in drawn) and any(GOOD_B in n for n in drawn), names
    assert not any(BAD in n for n in drawn), "no picture of the plot that failed"
    report = z.read(next(n for n in names if n.endswith("report.qmd"))).decode()
    assert "This plot was not drawn." in report
    assert f"_render/{BAD}." not in report, "the report links no picture that is not in the bundle"
    assert f"_render/{GOOD_A}." in report
