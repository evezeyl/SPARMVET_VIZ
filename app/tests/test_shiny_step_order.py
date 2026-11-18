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
- order A (drop score, then filter score >= 16, the filter staged before the drop): the table's place and the plot's place
  both show the error, naming the plot, the audit step, the column and the step that removed it; the Alerts panel holds it;
  the export is refused with `EXPORT_NOT_CREATED.txt` and the same reason;
- the filter dialog does not offer a column that an earlier audit step dropped (DECIDED 2026-11-15, S2-1 (a));
- two exports that succeed with audited steps (a filter; a filter then a drop): the `T3_data_<plot>.tsv` of the bundle holds
  the rows and values of a reference built in plain Polars from the raw file, and the plot of the bundle is the picture of a
  direct render of that reference (so a bundle that took an unfiltered frame fails).

Waits are on the app's state (the "audit steps applied" count, the row summary, the option list), never on time.

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
import polars as pl
import pytest
import yaml
from PIL import Image
from playwright.sync_api import Page, expect

from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_step_order"
PLOT = "per_year"
OTHER_PLOT = "per_score"
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
    other = minimal_plot("t", {"x": "score"}, [{"name": "geom_bar", "params": {}}], label="per score")
    other["description"] = "The number of samples per score: a second plot of the same table, with no audit steps."
    recipe = minimal_recipe("t", label="T", schemas={"t": schema}, plots={PLOT: plot, OTHER_PLOT: other})
    recipe["info"]["description"] = "A table of 30 samples and one plot, for a browser test of the audit step order."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "TG", "description": "The one group."})
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


def _table_text(page: Page) -> str:
    return page.locator("#home_data_preview").inner_text()


def _expect_rows(page: Page, n: int) -> None:
    """The data table says it holds n rows ("Viewing rows 1 through 15 of 15"): a retrying assertion on the app's state."""
    expect(page.locator("#home_data_preview .shiny-data-grid-summary")).to_contain_text(f" of {n}", timeout=20_000)


def _plot_image(page: Page) -> Image.Image:
    """The picture the plot shows now: the image itself (a notification can lie over a screenshot), after Shiny is idle."""
    _wait_shiny(page, 30_000)
    expect(page.locator(f"#plot_group_{PLOT} img")).to_be_visible(timeout=20_000)
    data = page.evaluate("(sel) => document.querySelector(sel + ' img').src", f"#plot_group_{PLOT}")
    return Image.open(io.BytesIO(base64.b64decode(data.split(",", 1)[1]))).convert("RGB")


def _plot_until(page: Page, predicate, what: str) -> Image.Image:
    """Read the plot until `predicate(image)` holds (a retrying read of the app's state, at most 20 s)."""
    deadline = time.time() + 20
    image = _plot_image(page)
    while not predicate(image):
        assert time.time() < deadline, f"the plot never became: {what}"
        page.wait_for_timeout(250)
        image = _plot_image(page)
    return image


def _red_pixels(image: Image.Image) -> int:
    pixels = np.asarray(image)
    return int(((pixels[..., 0] > 170) & (pixels[..., 1] < 100) & (pixels[..., 2] < 100)).sum())


def _same_picture(a: Image.Image, b: Image.Image) -> bool:
    return a.size == b.size and np.array_equal(np.asarray(a), np.asarray(b))


def _press(page: Page, selector: str) -> None:
    """Press a Shiny action button once it is visible. The click is made in the page: a notification can lie over the button."""
    expect(page.locator(selector).first).to_be_visible(timeout=15_000)
    expect(page.locator(selector).first).to_be_enabled(timeout=15_000)   # Apply stays disabled until every reason is read by the app
    page.eval_on_selector(selector, "e => e.click()")


def _confirm_scope(page: Page) -> None:
    """The scope dialog (this plot only is the default); the step stays pending, its reason box appears after it."""
    _press(page, "#propagation_confirm")
    _wait_shiny(page)


def _reasons_and_apply(page: Page, reason: str, nodes: int) -> None:
    """Give every empty reason, press Apply, and wait until the app says `nodes` audit steps are applied.

    A reason box can appear a moment after another one: fill what is empty until the app enables Apply (it enables it only when
    it has read every reason), then press it."""
    page.wait_for_function("() => [...document.querySelectorAll('input[id^=t3_reason_]')].some(e => !e.value)", timeout=15_000)
    deadline = time.time() + 20
    apply = page.locator("#btn_apply").first
    while True:
        reasons = page.locator('input[id^="t3_reason_"]')
        for i in range(reasons.count()):
            if not reasons.nth(i).input_value():
                reasons.nth(i).fill(reason)
                reasons.nth(i).press("Tab")   # leaving the box sends the text now; a click sent before it would be refused by the Apply gate
        _wait_shiny(page)
        if apply.is_enabled():
            break
        assert time.time() < deadline, "Apply was never enabled: a reason is not read by the app"
        page.wait_for_timeout(250)
    _press(page, "#btn_apply")
    page.wait_for_function("(n) => document.body.textContent.includes('audit steps applied \u2014 ' + n + ' node(s)')",
                           arg=nodes, timeout=20_000)
    _wait_shiny(page, 30_000)


def _confirm_and_apply(page: Page, reason: str, nodes: int) -> None:
    _confirm_scope(page)
    _reasons_and_apply(page, reason, nodes)


def _start(page: Page, url: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('TG')").first.click()
    _wait_shiny(page)
    # The app tracks the open plot tab from the tab widget: a step recorded before it knows the tab would be filed under no plot.
    expect(page.locator(f"#plot_group_{PLOT} img")).to_be_visible(timeout=30_000)
    _wait_shiny(page, 30_000)
    _open_filters_panel(page)
    page.locator("#tier_toggle input[value=T3]").check(force=True)   # the table shows My view
    _wait_shiny(page)
    _wait_for_fb_col_option(page, "score")
    _expect_rows(page, N)


def _stage_filter(page: Page) -> None:
    page.locator("#fb_col").select_option("score")
    _wait_shiny(page)
    page.locator("#fb_op").select_option("ge")
    _wait_shiny(page)
    # The number box is mounted again after the operator changes, with the smallest value of the column (1) in it: a value typed
    # before that is lost (found in repeated runs: the staged row read "score >= 1"). Wait for the new box, then type.
    page.wait_for_function("() => document.querySelector('#fb_value')?.value === '1'", timeout=15_000)
    page.locator("#fb_value").fill(str(THRESHOLD))
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    _press(page, "#filter_add_row")
    _wait_shiny(page)
    # the staged row says what the app read: column and value (a value typed too late would stage another one)
    expect(page.locator("#filter_rows_ui")).to_contain_text(f"score \u2265 {THRESHOLD}", timeout=10_000)
    expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)


def _send_staged_filter(page: Page, nodes: int) -> None:
    _press(page, "#filter_send_to_audit")
    _wait_shiny(page)
    _confirm_and_apply(page, "keep the good scores", nodes)


def _filter_step(page: Page, nodes: int) -> None:
    _stage_filter(page)
    _send_staged_filter(page, nodes)


def _pending_drop(page: Page) -> None:
    """Deselect `score` and send the drop to audit; the scope dialog is confirmed, the step stays pending (no Apply yet)."""
    page.evaluate("() => $('#preview_col_selector')[0].selectize.removeItem('score')")
    _wait_shiny(page)
    _press(page, "#col_drop_to_audit")
    _wait_shiny(page)
    _confirm_scope(page)


def _drop_step(page: Page, nodes: int) -> None:
    _pending_drop(page)
    _reasons_and_apply(page, "score is not needed", nodes)


def _alerts(page: Page) -> list:
    header = page.locator("#notification_log_accordion .accordion-button")
    if "collapsed" in (header.get_attribute("class") or ""):
        header.click()
        page.wait_for_timeout(400)
    return page.locator("#notification_log_accordion .spv-tag-row").all_inner_texts()


def _export_bundle(page: Page) -> zipfile.ZipFile:
    if not page.locator("#export_bundle_download").is_visible():
        page.locator("#nav_accordion .accordion-button:has-text('Export')").first.click()
        _wait_shiny(page)
    expect(page.locator("#export_bundle_download")).to_be_visible(timeout=10_000)
    page.locator("#export_user_name").fill("autotest")
    with page.expect_download(timeout=240_000) as info:
        page.locator("#export_bundle_download").click()
    return zipfile.ZipFile(io.BytesIO(Path(info.value.path()).read_bytes()))


# -- the reference: plain Polars from the raw file, and a direct render of it --------------------------------------------------

def _raw() -> pl.DataFrame:
    return pl.read_csv(WORK / "t.tsv", separator="\t", schema_overrides={"sample_id": pl.String})


def _reference_png(frame: pl.DataFrame) -> Image.Image:
    """The plot of the staged recipe drawn directly from a frame (no app), saved like the export saves it (png, 300 dpi, 8 x 5)."""
    from viz_factory import VizFactory
    recipe = yaml.safe_load((WORK / "recipes" / "t.yaml").read_text(encoding="utf-8"))
    spec = recipe["analysis_groups"]["tg"]["plots"][PLOT]
    figure = VizFactory().render(frame.lazy(), {"plots": {PLOT: spec}, "plot_defaults": recipe.get("plot_defaults", {})}, PLOT)
    path = WORK / "reference.png"
    figure.save(str(path), verbose=False, format="png", dpi=300, width=8, height=5)
    return Image.open(path).convert("RGB")


def _bundle_file(archive: zipfile.ZipFile, suffix: str) -> bytes:
    names = [n for n in archive.namelist() if n.endswith(suffix)]
    assert len(names) == 1, (suffix, archive.namelist())
    return archive.read(names[0])


def _check_bundle(archive: zipfile.ZipFile, reference: pl.DataFrame, dropped: bool) -> None:
    """The T3 data file and the plot of the bundle are the reference, not the unfiltered table."""
    names = archive.namelist()
    assert not any(n.endswith("EXPORT_NOT_CREATED.txt") for n in names), "the export was refused"
    data = pl.read_csv(io.BytesIO(_bundle_file(archive, f"/T3_data_{PLOT}.tsv")), separator="\t", schema_overrides={"sample_id": pl.String})
    expected = reference.drop("score") if dropped else reference
    assert data.height == expected.height < N, f"the T3 data file has {data.height} rows, the reference {expected.height}"
    assert data.columns == expected.columns, (data.columns, expected.columns)
    assert data.sort("sample_id").equals(expected.sort("sample_id")), "rows or values differ from the reference"
    picture = Image.open(io.BytesIO(_bundle_file(archive, f"/plots/{PLOT}.png"))).convert("RGB")
    assert _red_pixels(picture) == 0, "the bundle plot is an error picture"
    assert _same_picture(picture, _reference_png(reference)), "the bundle plot is not the plot of the reference rows"
    assert not _same_picture(picture, _reference_png(_raw())), "the bundle plot shows the unfiltered table"


def test_order_b_filter_then_drop_gives_the_same_rows_in_the_table_and_the_plot(page: Page, staged_app):
    _start(page, staged_app)
    page.locator("#plot_view input[value=T2]").check(force=True)
    _wait_shiny(page)
    result_plot = _plot_image(page)                       # the Result plot: all 30 rows
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _filter_step(page, 1)
    _expect_rows(page, N - THRESHOLD + 1)                 # the table shows the filtered rows
    filtered_plot = _plot_until(page, lambda im: not _same_picture(im, result_plot), "different from the Result plot (the filter shown)")
    _drop_step(page, 2)
    expect(page.locator("#home_data_preview thead")).not_to_contain_text("score", timeout=20_000)
    _expect_rows(page, N - THRESHOLD + 1)                 # the table keeps the filtered rows after the drop
    after_drop = _plot_image(page)
    assert _red_pixels(after_drop) == 0, "the plot is drawn, not an error"
    assert _same_picture(after_drop, filtered_plot), "the drop of a column the plot does not use must not change the plot"
    assert not _same_picture(after_drop, result_plot), "the old plot path ignored the filter once the column was dropped"
    assert not [a for a in _alerts(page) if "cannot run" in a], "no audit step error for an order that can run"


def test_the_filter_dialog_does_not_offer_a_column_that_an_earlier_audit_step_dropped(page: Page, staged_app):
    _start(page, staged_app)
    assert "score" in page.locator("#fb_col option").evaluate_all("els => els.map(e => e.value)")
    _drop_step(page, 1)
    page.wait_for_function("() => ![...document.querySelectorAll('#fb_col option')].some(o => o.value === 'score')", timeout=20_000)
    assert page.locator("#fb_col option").evaluate_all("els => els.map(e => e.value)") == ["sample_id", "year"]
    # the other views are the tables as they are: Result still offers the column
    page.locator("#tier_toggle input[value=T2]").check(force=True)
    _wait_shiny(page)
    page.wait_for_function("() => [...document.querySelectorAll('#fb_col option')].some(o => o.value === 'score')", timeout=20_000)


def test_order_a_drop_then_filter_shows_the_error_in_the_table_and_the_plot_and_blocks_the_export(page: Page, staged_app):
    """Order A cannot be made by recording the drop first and then opening the dialog (it does not offer the dropped column and
    Apply clears the staged rows). It still can be made while the drop is pending: the dialog acts on the applied steps only. The
    engine must then refuse the list, never skip a step."""
    _start(page, staged_app)
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _pending_drop(page)                       # step 1, pending
    _stage_filter(page)                       # the dialog still offers `score`: the drop is not applied yet
    _press(page, "#filter_send_to_audit")
    _wait_shiny(page)
    _confirm_scope(page)                      # step 2, pending
    _reasons_and_apply(page, "recorded in this order", 2)
    expect(page.locator("#home_data_preview")).to_contain_text("audit step 2", timeout=20_000)
    table = _table_text(page)
    for needle in ("audit step 2 of the plot 'per_year'", "score", "audit step 1", "removed it", "Fix"):
        assert needle in table, f"the table's place does not say {needle!r}: {table!r}"
    plot = _plot_until(page, lambda im: _red_pixels(im) > 100, "the error text (red) in the plot's place; the filter is not skipped")
    assert _red_pixels(plot) > 100
    found = [a for a in _alerts(page) if "cannot run" in a]
    assert len(found) == 1 and "'per_year'" in found[0], found
    archive = _export_bundle(page)            # the export is checked before anything is written
    assert archive.namelist() == ["EXPORT_NOT_CREATED.txt"], archive.namelist()
    notice = archive.read("EXPORT_NOT_CREATED.txt").decode()
    assert "audit step 2" in notice and "audit step 1" in notice and "'per_year'" in notice, notice
    # two plots in scope, the second one sound: the export is refused as a whole, and the notice says so and names the failing plot only
    assert "nothing was exported" in notice and "Plot 'per_year':" in notice and f"Plot '{OTHER_PLOT}':" not in notice, notice


def test_an_export_with_an_audited_filter_holds_the_filtered_rows_and_plot(page: Page, staged_app):
    _start(page, staged_app)
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _filter_step(page, 1)
    _expect_rows(page, N - THRESHOLD + 1)
    reference = _raw().filter(pl.col("score") >= THRESHOLD)
    assert reference.height == N - THRESHOLD + 1
    _check_bundle(_export_bundle(page), reference, dropped=False)


def test_an_export_with_a_filter_then_a_drop_holds_the_filtered_rows_without_the_column(page: Page, staged_app):
    _start(page, staged_app)
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _filter_step(page, 1)
    _drop_step(page, 2)
    expect(page.locator("#home_data_preview thead")).not_to_contain_text("score", timeout=20_000)
    _expect_rows(page, N - THRESHOLD + 1)
    reference = _raw().filter(pl.col("score") >= THRESHOLD)
    _check_bundle(_export_bundle(page), reference, dropped=True)


def test_the_dialog_of_another_plot_is_not_emptied_by_a_drop_on_this_one(page: Page, staged_app):
    """A drop on plot A (this plot only) must not reach plot B's dialog, also not for a moment on the switch: B lists `score`
    in every state the page goes through after the click, and never an empty list (round 3, point 4)."""
    _start(page, staged_app)
    page.locator("#plot_view input[value=T3]").check(force=True)
    _wait_shiny(page)
    _drop_step(page, 1)
    page.wait_for_function("() => ![...document.querySelectorAll('#fb_col option')].some(o => o.value === 'score')", timeout=20_000)
    page.evaluate("""() => {
        window.__dialogStates = [];
        const record = () => window.__dialogStates.push([...document.querySelectorAll('#fb_col option')].map(o => o.value).join(','));
        new MutationObserver(record).observe(document.body, {childList: true, subtree: true});
    }""")
    page.locator(".nav-link:has-text('per score')").first.click()
    page.wait_for_function("() => [...document.querySelectorAll('#fb_col option')].some(o => o.value === 'score')", timeout=20_000)
    _wait_shiny(page, 30_000)
    states = page.evaluate("() => window.__dialogStates")
    assert states and states[-1] == "sample_id,year,score", states
    assert "" not in states, f"the dialog was empty for a moment: {states}"
    # and back: plot A still has the drop
    page.locator(".nav-link:has-text('per year')").first.click()
    page.wait_for_function("() => ![...document.querySelectorAll('#fb_col option')].some(o => o.value === 'score')", timeout=20_000)
