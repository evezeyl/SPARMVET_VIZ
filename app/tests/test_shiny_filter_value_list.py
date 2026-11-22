"""A long list of values is served on demand while typing, and the dialog says so (PROVISIONAL (L10), FILTER-PICKERS-1), in the browser.

A staged recipe in a temporary folder of `tmpAI/` (no tracked file is touched): a table of 100000 rows, a text column `name` with
100000 different values and a small column `grp` that the plot uses. Before the change the dialog wrote the 100000 values into the
page (10000 values took 6.6 s, 30000 values 87 s). In the qa app features:

- the list of `name` appears (waiting on the box, not on time) and the dialog says how many values exist and that a search shows
  at most 1000 matches ("type more letters");
- typing a few letters shows the matches, at most 1000; typing a whole value finds that value (every value can be found);
- a value picked is staged as the real text and Apply leaves exactly that row;
- a short column (`grp`, 3 values) keeps the whole list in the page and has no note.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_filter_value_list.py -q
"""
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect

from app.tests.browser_view import wait_preview_rows
from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_filter_value_list"
N = 100_000


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def long_app():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "long.tsv").write_text("sample_id\tgrp\tname\n" + "".join(f"s{i}\tg{i % 3}\tname_{i:06d}\n" for i in range(N)), encoding="utf-8")
    schema = minimal_schema("./tmpAI/browser_filter_value_list/long.tsv", {"sample_id": "String", "grp": "String", "name": "String"},
                            entity_key="sample_id")
    schema["description"] = "One row per sample, a name that is different for every row."
    plot = minimal_plot("long", {"x": "grp"}, [{"name": "geom_bar", "params": {}}], label="Per group")
    plot["description"] = "The number of samples per group."
    recipe = minimal_recipe("long", label="Long", schemas={"long": schema}, plots={"long_plot": plot})
    recipe["info"]["description"] = "A table of 100000 different names, for a browser test."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "Long", "description": "The one group."})
    recipe["analysis_groups"] = {"long_group": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "long.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "long list", "locations": locations,
                                          "default_data_analysis_recipe": "long", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment))
    with open(WORK / "server.log", "w") as out:
        proc = subprocess.Popen(app_command(port),
                                cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(180):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            yield url
        finally:
            proc.terminate()
            proc.wait(timeout=30)


def _open_dialog(page: Page, url: str, column: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('Long')").first.click()
    _wait_shiny(page, 60_000)
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, column)
    page.locator("#fb_col").select_option(column)
    _wait_shiny(page, 60_000)
    expect(page.locator("#fb_col_type")).to_contain_text(f"{column} holds", timeout=60_000)


_SHOWN = "() => Array.from(document.querySelector('#fb_value').selectize.$dropdown[0].querySelectorAll('.option')).map(o => o.innerText.trim())"


def _shown(page: Page) -> list:
    """The values the list of the dialog shows now (its own dropdown, not another box of the page)."""
    return page.evaluate(_SHOWN)


def _wait_shown(page: Page, predicate_js: str) -> None:
    """Wait until what the list shows satisfies a JS predicate on the array of the shown texts, on the state of the box, not on time."""
    page.wait_for_function(f"() => ({predicate_js})(({_SHOWN})())", timeout=20_000)


def test_a_list_of_100000_values_is_served_on_demand_and_every_value_is_found(page: Page, long_app):
    started = time.time()
    _open_dialog(page, long_app, "name")
    _choose = page.locator("#fb_op")
    _choose.select_option("in")
    _wait_shiny(page, 60_000)
    expect(page.locator("#fb_value-selectized")).to_be_visible(timeout=30_000)
    print(f"\nTIMING dialog of 100000 values ready after {time.time() - started:.1f} s (from the start of the page)")
    # the dialog says how many values exist and that a search shows at most 1000 matches
    note = page.locator("#fb_value_note")
    expect(note).to_contain_text("100,000 different values", timeout=10_000)
    expect(note).to_contain_text("at most 1,000 matches")
    expect(note).to_contain_text("type more letters")
    # a few letters: matches, at most 1000 shown
    # the server has handed the box its list (the on-demand loader is set), then the user clicks: the first load (an empty search) comes
    page.wait_for_function("() => { const s = document.querySelector('#fb_value')?.selectize; return !!(s && typeof s.settings.load === 'function'); }",
                           timeout=30_000)
    box = page.locator("#fb_value-selectized")
    box.click()
    page.wait_for_function("() => { const s = document.querySelector('#fb_value').selectize; return Object.keys(s.options).length > 0; }",
                           timeout=30_000)
    box.press_sequentially("name_0")
    _wait_shown(page, "t => t.length >= 1 && t.every(x => x.includes('name_0'))")
    page.wait_for_load_state("networkidle")
    assert 1 <= len(_shown(page)) <= 1001, "a search shows at most 1000 matches"
    # a longer text narrows the list; the last value of the column is found by its text
    box.press_sequentially("99999")
    page.wait_for_function("() => document.querySelector('#fb_value').selectize.lastQuery === 'name_099999'", timeout=20_000)
    page.wait_for_load_state("networkidle")   # every answer of the server has arrived: the last search decides what is shown
    _wait_shown(page, "t => t.length === 1 && t[0] === 'name_099999'")
    box.press("Enter")
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("name = name_099999", timeout=10_000)
    page.locator("#filter_apply").click()
    _wait_shiny(page, 60_000)
    wait_preview_rows(page, 1, 30_000)
    expect(page.locator("#home_data_preview")).to_contain_text("name_099999")


def test_a_short_column_keeps_the_whole_list_and_has_no_note(page: Page, long_app):
    _open_dialog(page, long_app, "grp")
    expect(page.locator("#fb_col_type")).to_contain_text("grp holds text", timeout=30_000)   # the dialog is on grp, not on the first column
    page.locator("#fb_op").select_option("in")
    _wait_shiny(page)
    expect(page.locator("#fb_value-selectized")).to_be_visible(timeout=10_000)
    assert page.locator("#fb_value_note").count() == 0
    page.locator("#fb_value-selectized").click()
    _wait_shown(page, "t => t.length === 3")
