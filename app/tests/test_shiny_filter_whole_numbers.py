"""The HOME filter form refuses a decimal for a column of whole numbers, in the browser (D-0376).

# @deps
# consumes: app/handlers/filter_and_audit_handlers.py (filter_whole_number_ui, _filter_add_row), app/modules/t3_audit_engine.py (refuse_decimal_for_whole_numbers)
# @end_deps

A table of five rows with a whole-number column `n` (not a plot axis) and a decimal column `w`. Typing 12.5 for `n` with `>` and with
`=` shows the plain line under the box and adds no row to the staged filters; 12 adds the row; a decimal column takes 12.5.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_filter_whole_numbers.py -q
"""
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect

from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_whole_numbers"
LINE = "This column holds whole numbers (Int64); type a whole number."


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def whole_app():
    WORK.mkdir(parents=True, exist_ok=True)
    rows = [("s1", 10, 1.5), ("s2", 12, 2.5), ("s3", 13, 3.5), ("s4", 15, 4.5), ("s5", 20, 5.5)]
    (WORK / "t.tsv").write_text("sample_id\tn\tw\n" + "".join(f"{a}\t{b}\t{c}\n" for a, b, c in rows), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_whole_numbers/t.tsv", {"sample_id": "String", "n": "Int64", "w": "Float64"}, entity_key="sample_id")
    schema["description"] = "One row per sample."
    plot = minimal_plot("t", {"x": "sample_id"}, [{"name": "geom_bar", "params": {}}], label="Samples")
    plot["description"] = "Samples."
    recipe = minimal_recipe("whole", label="Whole", schemas={"t": schema}, plots={"whole_plot": plot})
    recipe["info"]["description"] = "A table with a whole-number column, for a browser test."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "Whole", "description": "The one group."})
    recipe["analysis_groups"] = {"whole_group": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "whole.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "whole numbers", "locations": locations,
                                          "default_data_analysis_recipe": "whole", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment))
    with open(WORK / "server.log", "w") as out:
        proc = subprocess.Popen(app_command(port), cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)
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


def _open_form(page: Page, url: str, column: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('Whole')").first.click()
    _wait_shiny(page)
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, column)
    page.locator("#fb_col").select_option(column)
    _wait_shiny(page)


def _type(page: Page, selector: str, text: str) -> None:
    page.locator(selector).fill(text)
    page.locator(selector).press("Tab")
    _wait_shiny(page)


@pytest.mark.parametrize("op, symbol", [("gt", ">"), ("eq", "=")])
def test_a_decimal_for_a_whole_number_column_shows_the_line_and_adds_nothing(page: Page, whole_app, op, symbol):
    _open_form(page, whole_app, "n")
    page.locator("#fb_op").select_option(op)
    _wait_shiny(page)
    expect(page.locator("input#fb_value[type=number]")).to_be_visible(timeout=5_000)
    _type(page, "#fb_value", "12.5")
    expect(page.locator("#fb_whole_number_line")).to_have_text(LINE, timeout=5_000)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    assert "12.5" not in page.locator("#filter_rows_ui").inner_text()
    assert page.locator("[id^=filter_remove_]").count() == 0      # nothing staged
    # a whole number: the line goes, the row is added
    _type(page, "#fb_value", "12")
    expect(page.locator("#fb_whole_number_line")).to_have_text("", timeout=5_000)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text(f"n {symbol} 12", timeout=5_000)
    assert page.locator("[id^=filter_remove_]").count() == 1


def test_between_refuses_a_decimal_end(page: Page, whole_app):
    _open_form(page, whole_app, "n")
    page.locator("#fb_op").select_option("between")
    _wait_shiny(page)
    _type(page, "#fb_value_lo", "11.5")
    expect(page.locator("#fb_whole_number_line")).to_have_text(LINE, timeout=5_000)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    assert page.locator("[id^=filter_remove_]").count() == 0


def test_a_decimal_column_takes_a_decimal(page: Page, whole_app):
    _open_form(page, whole_app, "w")
    page.locator("#fb_op").select_option("gt")
    _wait_shiny(page)
    _type(page, "#fb_value", "2.5")
    assert page.locator("#fb_whole_number_line").inner_text() == ""
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("w > 2.5", timeout=5_000)
