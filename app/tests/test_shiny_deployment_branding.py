"""What the two customized deployments SHOW in a browser (demo-vetinst and web-demo).

TODAY'S BEHAVIOUR, RECORDED BEFORE THE RENAME OF D-0411. The rename of the deployment banner keys
(`title` -> `ui_label`, `subtitle` -> `description`; owner decision, not built) must keep this file green: the VALUES
shown stay the same. The keys are read through `deployment_branding_keys` (one place to change).
Browser test: each deployment is started with the app features it declares as its default, about 20-40 s each.
"""
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect

from app.tests.deployment_branding_keys import banner_line, banner_title
from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _wait_shiny

REPO = Path(__file__).resolve().parents[2]
CASES = {
    "demo-vetinst": "config/deployment/demo/demo-vetinst.yaml",
    "web-demo": "config/deployment/demo/web-demo.yaml",
}
# the banner colour each deployment's own stylesheet sets (assets/demo/*.css, section 1); the base theme sets none
BANNER_BACKGROUND = {"demo-vetinst": "rgb(0, 79, 110)", "web-demo": "rgb(0, 245, 200)"}
# the recipe banner of the default recipe 1_test_data_ST22_dummy (its info: label and subtitle)
RECIPE_TITLE = "ST22 Dummy Dataset"
RECIPE_LINE = "E. coli ST22 — AMR & Virulence Research (demo)"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.parametrize("name", CASES)
def test_customized_deployment_shows_what_its_file_sets(page: Page, tmp_path, name):
    deployment = CASES[name]
    file_data = yaml.safe_load((REPO / deployment).read_text(encoding="utf-8"))
    banner = file_data["branding"]["banner"]
    app_features = file_data["default_app_features"]
    log = tmp_path / "server.log"
    port = _free_port()
    env = app_env(SPARMVET_DEPLOYMENT=deployment, SPARMVET_APP_FEATURES=app_features)
    with open(log, "w") as out:
        proc = subprocess.Popen(app_command(port), cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(60):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            page.goto(url)
            bar = page.locator(".sparmvet-banner")
            expect(bar).to_have_count(1, timeout=40_000)
            _wait_shiny(page, 60_000)

            # today's behaviour, recorded before the rename of D-0411: the banner title and line are the file's values
            title, line = banner_title(banner), banner_line(banner)
            if title:
                expect(bar.locator(".sparmvet-banner-title")).to_have_text(title)
            else:
                expect(bar.locator(".sparmvet-banner-title")).to_have_count(0)
            if line:
                expect(bar.locator(".sparmvet-banner-subtitle")).to_have_text(line)
            else:
                expect(bar.locator(".sparmvet-banner-subtitle")).to_have_count(0)

            # today's behaviour: the logo image is in the banner and loaded
            logo = bar.locator("img.sparmvet-banner-logo")
            expect(logo).to_have_count(1)
            assert logo.evaluate("e => e.complete && e.naturalWidth > 0"), "the banner logo did not load"

            # today's behaviour: the deployment's stylesheet is applied (the base theme sets no banner colour)
            background = bar.evaluate("e => getComputedStyle(e).backgroundColor")
            assert background == BANNER_BACKGROUND[name]

            # today's behaviour: HOME shows the recipe banner of the default recipe
            recipe_title = page.locator(".view-title-banner .banner-title")
            expect(recipe_title).to_have_text(RECIPE_TITLE, timeout=60_000)
            expect(page.locator(".view-title-banner .banner-subtitle")).to_have_text(RECIPE_LINE)
        finally:
            proc.terminate()
            proc.wait(timeout=20)
