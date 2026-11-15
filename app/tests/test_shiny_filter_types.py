"""The HOME filter dialog keeps the real value and shows the type (ADR-104 point 7, Eve 2026-11-14), in the browser.

A table of 600 rows with a whole-number column `year` that the plot uses as a discrete axis; the value 1900 appears only in
the last row (after row 500, the rows the old dialog read). The dialog:
  - says what the column holds ("year holds whole numbers (Int64).");
  - lists the late value 1900 (the list comes from the whole column);
  - offers "> 1999 and < 2003" on that discrete year, with number boxes, and the filter leaves the right rows;
  - offers the four ends of a range.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_filter_types.py -q
"""
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect

from app.tests.test_shiny_smoke import _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_typed_values"
YEARS = [1950 + i % 100 for i in range(599)] + [1900]
PREVIEW = 100  # the data preview shows at most 100 rows


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def typed_app():
    """The app on a deployment of its own (a recipe of one table with an integer year on a discrete axis)."""
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "years.tsv").write_text("sample_id\tyear\n" + "".join(f"s{i}\t{y}\n" for i, y in enumerate(YEARS)), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_typed_values/years.tsv", {"sample_id": "String", "year": "Int64"}, entity_key="sample_id")
    schema["description"] = "One row per sample."
    plot = minimal_plot("years", {"x": "year"}, [{"name": "geom_bar", "params": {}}, {"name": "scale_x_discrete", "params": {}}], label="Samples per year")
    plot["description"] = "Count of samples per year."
    recipe = minimal_recipe("years", label="Years", schemas={"years": schema}, plots={"years_plot": plot})
    recipe["info"]["description"] = "A table with an integer year, for a browser test."
    group = recipe["analysis_groups"].pop("main")
    group.update({"label": "Years", "description": "The one group."})
    recipe["analysis_groups"] = {"years_group": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "years.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "typed values", "locations": locations,
                                          "default_data_analysis_recipe": "years", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    pythonpath = os.pathsep.join(["."] + [p for p in [os.environ.get("PYTHONPATH")] if p])
    env = {**os.environ, "PYTHONPATH": pythonpath, "SPARMVET_APP_FEATURES": "qa", "SPARMVET_DEPLOYMENT": str(deployment)}
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


def _wait_rows(page: Page, n: int) -> None:
    """Wait until the data preview shows n rows: its summary says "of n" when it pages, else the rows are counted."""
    page.wait_for_function(
        """([sel, n]) => {
            const grid = document.querySelector(sel);
            if (!grid) return false;
            const summary = grid.querySelector('.shiny-data-grid-summary');
            if (summary) return summary.innerText.includes('of ' + n);
            return grid.querySelectorAll('tbody tr').length === n;
        }""", arg=["#home_data_preview", n], timeout=15_000)


def _set_number(page: Page, selector: str, value: int) -> None:
    page.locator(selector).fill(str(value))
    page.locator(selector).press("Tab")
    _wait_shiny(page)


def _open_dialog(page: Page, url: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('Years')").first.click()
    _wait_shiny(page)
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, "year")
    page.locator("#fb_col").select_option("year")
    _wait_shiny(page)


def test_the_dialog_shows_the_type_lists_the_late_value_and_compares_on_a_discrete_year(page: Page, typed_app):
    _open_dialog(page, typed_app)
    _wait_rows(page, PREVIEW)

    # the type is shown next to the column, in plain words
    expect(page.locator("#fb_col_type")).to_have_text("year holds whole numbers (Int64).", timeout=10_000)

    # the year is a discrete axis: the list operators come first, the comparisons are offered too
    ops = page.locator("#fb_op option").evaluate_all("els => els.map(e => e.value)")
    assert ops == ["in", "not_in", "eq", "ne", "gt", "ge", "lt", "le", "between"]

    # 1900 appears only in the last row, after row 500: it is offered and picks that one row
    page.locator("#fb_value-selectized").fill("1900")
    page.keyboard.press("Enter")
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("year = 1900", timeout=5_000)
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    _wait_rows(page, 1)
    page.locator("#filter_remove_0").click()
    _wait_shiny(page)
    _wait_rows(page, PREVIEW)

    # "> 1999 and < 2003" on the discrete year: number boxes, the right rows
    page.locator("#fb_op").select_option("gt")
    _wait_shiny(page)
    expect(page.locator("#fb_value")).to_have_attribute("type", "number", timeout=5_000)
    _set_number(page, "#fb_value", 1999)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("year > 1999", timeout=5_000)
    page.locator("#fb_op").select_option("lt")
    _wait_shiny(page)
    _set_number(page, "#fb_value", 2003)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("year < 2003", timeout=5_000)
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    _wait_rows(page, sum(1 for y in YEARS if 1999 < y < 2003))
    page.locator("#filter_remove_1").click()
    _wait_shiny(page)
    page.locator("#filter_remove_0").click()
    _wait_shiny(page)
    _wait_rows(page, PREVIEW)


def test_between_offers_the_four_ends_and_each_gives_its_rows(page: Page, typed_app):
    _open_dialog(page, typed_app)
    page.locator("#fb_op").select_option("between")
    _wait_shiny(page)
    labels = page.locator("input[name=fb_closed]").evaluate_all("els => els.map(e => e.value)")
    assert labels == ["both", "left", "right", "none"]
    _set_number(page, "#fb_value_lo", 2000)
    _set_number(page, "#fb_value_hi", 2002)
    expected = {"both": (2000, 2002), "left": (2000, 2001), "right": (2001, 2002), "none": (2001, 2001)}
    for closed, (lo, hi) in expected.items():
        page.locator(f"input[name=fb_closed][value={closed}]").check()
        _wait_shiny(page)
        page.locator("#filter_add_row").click()
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        _wait_rows(page, sum(1 for y in YEARS if lo <= y <= hi))
        page.locator("#filter_remove_0").click()
        _wait_shiny(page)
        _wait_rows(page, PREVIEW)


def test_on_a_discrete_year_equal_picks_from_the_list_and_greater_than_uses_the_number_box(page: Page, typed_app):
    """The widget follows the operator: eq and ne use the list, a comparison uses one number box (Eve, 2026-11-14)."""
    _open_dialog(page, typed_app)
    for op in ("eq", "ne", "in", "not_in"):
        page.locator("#fb_op").select_option(op)
        _wait_shiny(page)
        expect(page.locator("#fb_value-selectized")).to_be_visible(timeout=5_000)
        assert page.locator("input#fb_value[type=number]").count() == 0, op
    for op in ("gt", "ge", "lt", "le"):
        page.locator("#fb_op").select_option(op)
        _wait_shiny(page)
        expect(page.locator("input#fb_value[type=number]")).to_be_visible(timeout=5_000)
        assert page.locator("#fb_value-selectized").count() == 0, op
