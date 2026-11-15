"""The Gallery in a real browser leaves out an example that failed the check, says why, and never opens it.

The gallery folder is a temporary copy with one example broken (an unknown plot component), started with its own
deployment file; the repository is not touched. Browser test: needs Playwright, about 30 s.
Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_gallery_left_out.py -q
"""
import re
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
from app.tests.subprocess_env import app_env
from playwright.sync_api import Page, expect

REPO = Path(__file__).resolve().parents[2]
BROKEN = "area_simple"
GOOD = "bar_simple"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def broken_gallery_app(tmp_path_factory):
    work = tmp_path_factory.mktemp("gallery_left_out")
    gallery = work / "gallery_data"
    shutil.copytree(REPO / "assets" / "gallery_data", gallery)
    recipe = gallery / BROKEN / "data_analysis_recipe.yaml"
    text = recipe.read_text()
    assert "name: geom_" in text
    recipe.write_text(text.replace("name: geom_", "name: not_a_real_component_", 1))
    deployment = (REPO / "config/deployment/local/local.yaml").read_text()
    deployment, n = re.subn(r"(?m)^(\s*gallery:\s*).*$", lambda m: f'{m.group(1)}"{gallery}/"', deployment)
    assert n == 1
    # Read-only folder: the old index stays and still lists the broken example, so the handlers must filter it
    # themselves (a handler that reads the stored index directly would open it).
    index = gallery / "gallery_index.json"
    assert BROKEN in index.read_text()
    index.chmod(0o444)
    gallery.chmod(0o555)
    dep_file = work / "deployment.yaml"
    dep_file.write_text(deployment)
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(dep_file))
    with open(work / "server.log", "w") as out:
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
            gallery.chmod(0o755)
            shutil.rmtree(work, ignore_errors=True)


def _open_gallery(page: Page, url: str):
    page.goto(url)
    page.wait_for_selector("#sidebar_nav", timeout=30_000)
    page.get_by_text("Gallery", exact=True).first.click()
    page.wait_for_selector("#gallery_example_select", state="attached", timeout=30_000)


def test_the_block_names_the_broken_example_and_the_reason(page: Page, broken_gallery_app):
    _open_gallery(page, broken_gallery_app)
    block = page.locator(".gallery-left-out")
    expect(block).to_be_visible(timeout=20_000)
    expect(block).to_contain_text("not shown, failed the check")
    expect(block).to_contain_text("read-only")
    expect(block).to_contain_text(BROKEN)
    expect(block.locator(".gallery-left-out-line").first).not_to_be_empty()


def test_the_select_has_no_option_for_the_broken_example(page: Page, broken_gallery_app):
    _open_gallery(page, broken_gallery_app)
    expect(page.locator(".gallery-left-out")).to_be_visible(timeout=20_000)
    # the options are pushed by an effect after the first render
    page.wait_for_function(
        "id => document.querySelector('#gallery_example_select').querySelectorAll('option').length > 0", arg=GOOD)
    options = page.eval_on_selector_all("#gallery_example_select option", "els => els.map(e => e.value)")
    assert GOOD in options
    assert BROKEN not in options


def test_asking_for_the_broken_examples_preview_shows_nothing(page: Page, broken_gallery_app):
    _open_gallery(page, broken_gallery_app)
    expect(page.locator(".gallery-left-out")).to_be_visible(timeout=20_000)
    page.evaluate("id => Shiny.setInputValue('gallery_example_select', id)", BROKEN)
    # "Select an example" is also the text before the request, so give the server time to answer first;
    # without this wait the check passes at once and cannot fail.
    page.wait_for_timeout(3_000)
    page.wait_for_function("!document.documentElement.classList.contains('shiny-busy')")
    expect(page.locator("#gallery_preview_img")).to_contain_text("Select an example")
    assert page.locator("#gallery_preview_img img").count() == 0
    # a good example still opens, so the empty answer above is not a page that never answers
    page.evaluate("id => Shiny.setInputValue('gallery_example_select', id)", GOOD)
    expect(page.locator("#gallery_preview_img img")).to_be_visible(timeout=15_000)
