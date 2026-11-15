"""The audited steps of a plot run in the order they were recorded, in the same way in the table, the plot and the export
(PLOT-TABLE-ORDER-1, Eve 2026-11-14 and 2026-11-15), in the browser.

# @deps
# consumes: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/t3_audit_engine.py, app/modules/plot_issue_reporter.py
# @end_deps

A staged recipe (one table of 30 rows: sample_id, year, score = 1..30; one plot of the number of samples per year) in a
temporary folder of `tmpAI/`; no tracked file is touched. In the qa app features, in "My view":

- order B (filter score >= 16, then drop score): the table and the plot both show the filtered rows (15). The plot differs
  from the Result plot, and the drop does not change it (the old plot path skipped the filter on the dropped column and drew
  all 30 rows);
- order A (drop score, then filter score >= 16): the table's place and the plot's place both show the error, naming the audit
  step, the column and the step that removed it; the Alerts panel holds it; the export is refused with `EXPORT_NOT_CREATED.txt`
  and the same reason.

Not tested here: that the filter dialog still offers a column that an earlier audit step dropped (it does; open point).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_step_order.py -q
"""
import base64
import io
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

from app.tests.subprocess_env import app_env
from app.tests.test_shiny_smoke import _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_step_order"
PLOT = "per_year"
N = 30
THRESHOLD = 16     # score >= 16 keeps 15 of the 30 rows


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def staged_app():
    """The app on a deployment of its own, with a table whose rows are 1..30 and a plot that counts samples per year."""
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "t.tsv").write_text("sample_id\tyear\tscore\n" + "".join(f"s{i}\t{2000 + i % 3}\t{i}\n" for i in range(1, N + 1)), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_step_order/t.tsv", {"sample_id": "String", "year": "Int64", "score": "Int64"}, entity_key="sample_id")
    schema["description"] = "One row per sample."
    plot = minimal_plot("t", {"x": "year"}, [{"name": "geom_bar", "params": {}}], label="per year")
    plot["description"] = "The number of samples per year."
    recipe = minimal_recipe("t", label="T", schemas={"t": schema}, plots={PLOT: plot})
    recipe["info"]["description"] = "A table of 30 samples and one plot, for a browser test of the audit step order."
    group = recipe["analysis_groups"].pop("main")
    group.update({"label": "TG", "description": "The one group."})
    recipe["analysis_groups"] = {"tg": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "t.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "step order", "locations": locations,
                                          "default_data_analysis_recipe": "t", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment))
    with open(WORK / "server.log", "w") as out:
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


def _table_text(page: Page) -> str:
    return page.locator("#home_data_preview").inner_text()


def _table_rows(page: Page) -> int:
    """Rows of the data table, from its summary ("Viewing rows 1 through 15 of 15")."""
    summary = page.locator("#home_data_preview .shiny-data-grid-summary")
    expect(summary).to_be_visible(timeout=15_000)
    return int(summary.inner_text().split(" of ")[-1].split()[0])


def _plot_image(page: Page) -> Image.Image:
    box = page.locator(f"#plot_group_{PLOT}")
    expect(box.locator("img")).to_be_visible(timeout=20_000)
    page.wait_for_timeout(500)
    # the image itself, not a screenshot of the screen (a notification can lie over the plot)
    data = page.evaluate("(sel) => document.querySelector(sel + ' img').src", f"#plot_group_{PLOT}")
    return Image.open(io.BytesIO(base64.b64decode(data.split(",", 1)[1]))).convert("RGB")


def _red_pixels(image: Image.Image) -> int:
    pixels = np.asarray(image)
    return int(((pixels[..., 0] > 170) & (pixels[..., 1] < 100) & (pixels[..., 2] < 100)).sum())


def _same_picture(a: Image.Image, b: Image.Image) -> bool:
    return a.size == b.size and np.array_equal(np.asarray(a), np.asarray(b))


def _confirm_and_apply(page: Page, reason: str) -> None:
    page.wait_for_timeout(800)
    if page.locator("#propagation_confirm").count() and page.locator("#propagation_confirm").is_visible():
        page.locator("#propagation_confirm").click()
        _wait_shiny(page)
    reasons = page.locator('input[id^="t3_reason_"]')
    for i in range(reasons.count()):
        if not reasons.nth(i).input_value():
            reasons.nth(i).fill(reason)
    _wait_shiny(page)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    page.wait_for_timeout(800)


def _start(page: Page, url: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('TG')").first.click()
    _wait_shiny(page)
    _open_filters_panel(page)
    page.locator("#tier_toggle input[value=T3]").check(force=True)   # the table shows My view
    _wait_shiny(page)
    _wait_for_fb_col_option(page, "score")
    assert _table_rows(page) == N


def _filter_step(page: Page) -> None:
    page.locator("#fb_col").select_option("score")
    _wait_shiny(page)
    page.locator("#fb_op").select_option("ge")
    _wait_shiny(page)
    page.locator("#fb_value").fill(str(THRESHOLD))
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    page.locator("#filter_send_to_audit").click()
    _wait_shiny(page)
    _confirm_and_apply(page, "keep the good scores")


def _drop_step(page: Page) -> None:
    page.evaluate("() => $('#preview_col_selector')[0].selectize.removeItem('score')")
    _wait_shiny(page)
    page.locator("#col_drop_to_audit").click()
    _wait_shiny(page)
    _confirm_and_apply(page, "score is not needed")


def _alerts(page: Page) -> list:
    header = page.locator("#notification_log_accordion .accordion-button")
    if "collapsed" in (header.get_attribute("class") or ""):
        header.click()
        page.wait_for_timeout(400)
    return page.locator("#notification_log_accordion .spv-tag-row").all_inner_texts()


def test_order_b_filter_then_drop_gives_the_same_rows_in_the_table_and_the_plot(page: Page, staged_app):
    _start(page, staged_app)
    page.locator("#plot_view input[value=T2]").check(force=True)
    _wait_shiny(page)
    result_plot = _plot_image(page)                       # the Result plot: all 30 rows
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _filter_step(page)
    assert _table_rows(page) == N - THRESHOLD + 1, "the table shows the filtered rows"
    filtered_plot = _plot_image(page)
    assert not _same_picture(filtered_plot, result_plot), "the plot of My view shows the filter"
    _drop_step(page)
    assert _table_rows(page) == N - THRESHOLD + 1, "the table keeps the filtered rows after the drop"
    assert "score" not in page.locator("#home_data_preview thead").inner_text()
    after_drop = _plot_image(page)
    assert _red_pixels(after_drop) == 0, "the plot is drawn, not an error"
    assert _same_picture(after_drop, filtered_plot), "the drop of a column the plot does not use must not change the plot"
    assert not _same_picture(after_drop, result_plot), "the old plot path ignored the filter once the column was dropped"
    assert not [a for a in _alerts(page) if "cannot run" in a], "no audit step error for an order that can run"


def test_order_a_drop_then_filter_shows_the_error_in_the_table_and_the_plot_and_blocks_the_export(page: Page, staged_app):
    _start(page, staged_app)
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _drop_step(page)
    assert "score" not in page.locator("#home_data_preview thead").inner_text()
    # the dialog still offers the dropped column (open point of PLOT-TABLE-ORDER-1): the user can record the second step
    _filter_step(page)
    expect(page.locator("#home_data_preview")).to_contain_text("audit step 2", timeout=15_000)
    table = _table_text(page)
    for needle in ("audit step 2", "score", "audit step 1", "removed it", "Fix"):
        assert needle in table, f"the table's place does not say {needle!r}: {table!r}"
    plot = _plot_image(page)
    assert _red_pixels(plot) > 100, "the error (red text) is drawn in the plot's place; the filter is not skipped"
    found = [a for a in _alerts(page) if "cannot run" in a]
    assert len(found) == 1, found
    # the export is checked before anything is written
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion .accordion-button:has-text('Export')").first.click()
        _wait_shiny(page)
    expect(page.locator("#export_bundle_download")).to_be_visible(timeout=10_000)
    page.locator("#export_user_name").fill("autotest")
    with page.expect_download(timeout=120_000) as info:
        page.locator("#export_bundle_download").click()
    archive = zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))
    assert archive.namelist() == ["EXPORT_NOT_CREATED.txt"], archive.namelist()
    notice = archive.read("EXPORT_NOT_CREATED.txt").decode()
    assert "audit step 2" in notice and "audit step 1" in notice and "'per_year'" in notice, notice
