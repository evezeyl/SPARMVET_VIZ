"""Every shipped app features file starts the app and renders the Home page without a server error.

Why: until 2026-11-07 the two app features meant for researchers (standalone, pipeline-exploration-advanced)
ended on a blank page because a state object was only created in developer mode; the browser suite ran
under `qa` only, so nothing noticed. Each app features is launched here with a deployment that suits it.
Browser test: needs Playwright and takes about 15 s per app features.
"""
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

REPO = Path(__file__).resolve().parents[2]
LOCAL = "config/deployment/local/local.yaml"
PIPELINE = "config/deployment/pipeline_test/pipeline_test.yaml"
CASES = [
    ("developer", LOCAL),
    ("qa", LOCAL),
    ("standalone", LOCAL),
    ("pipeline-exploration-advanced", PIPELINE),
    ("pipeline-exploration-simple", PIPELINE),
    ("pipeline-static", PIPELINE),
    ("demo-vetinst", "config/deployment/demo/demo-vetinst.yaml"),
    ("web-demo", "config/deployment/demo/web-demo.yaml"),
]
# app features whose blueprint_enabled flag is on: the Blueprint Architect tab must exist and open
WITH_BLUEPRINT = {"developer", "qa", "standalone"}
SERVER_ERRORS = ("Unhandled error", "Traceback", "ReactiveWarning")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_every_shipped_app_features_is_covered():
    shipped = {p.stem for p in (REPO / "config/app_features").glob("*.yaml")}
    assert shipped == {name for name, _ in CASES}


@pytest.mark.parametrize("app_features, deployment", CASES)
def test_app_features_renders_home_without_server_error(page: Page, tmp_path, app_features, deployment):
    log = tmp_path / "server.log"
    port = _free_port()
    env = {**os.environ, "PYTHONPATH": ".", "SPARMVET_APP_FEATURES": app_features, "SPARMVET_DEPLOYMENT": deployment}
    with open(log, "w") as out:
        proc = subprocess.Popen([str(REPO / ".venv/bin/shiny"), "run", "app/src/main.py", "--port", str(port)],
                                cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(60):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            page.goto(url)
            # the data analysis recipe title banner or a plot group tab proves that Home was built
            expect(page.locator(".view-title-banner, .nav-link").first).to_be_visible(timeout=40_000)
            # F-26 / PROCESSING-ISSUES-RENAME-1: the regression this guards against is a real one —
            # processing_issues_ui (then pipeline_issues_ui) was defined but never mounted in any
            # app features, for every app features, since the original commit. Left sidebar, not
            # right, so this must hold even for pipeline-static (no right sidebar at all).
            assert page.locator("#processing_issues_ui").count() == 1, \
                "Processing Issues output must be mounted in every app features (left sidebar, never gated)"
            time.sleep(4)
            tab = page.get_by_text("Blueprint Architect", exact=True)
            if app_features in WITH_BLUEPRINT:
                tab.first.click()
                expect(page.get_by_text("Blueprint Architect Flight Deck")).to_be_visible(timeout=20_000)
                time.sleep(3)
            else:
                assert tab.count() == 0, "the Blueprint Architect tab is shown although blueprint_enabled is off"
        finally:
            proc.terminate()
            proc.wait(timeout=20)
    text = log.read_text()
    assert not any(marker in text for marker in SERVER_ERRORS), text[-1500:]
