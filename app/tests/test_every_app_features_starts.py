"""Every shipped app features file starts the app and renders the Home page without a server error.

Why: until 2026-11-07 the two app features meant for researchers (standalone, pipeline-exploration-advanced)
ended on a blank page because a state object was only created in developer mode; the browser suite ran
under `qa` only, so nothing noticed. Each app features is launched here with a deployment that suits it.
Browser test: needs Playwright and takes about 15 s per app features.
"""
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from app.tests.subprocess_env import app_command, app_env
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


class _PlainLoader(yaml.SafeLoader):
    """Reads an app features file as it is: the `!include` of the sidebar files is not followed, the flags do not need it."""


_PlainLoader.add_multi_constructor("!", lambda loader, suffix, node: None)


def _flags(app_features: str) -> dict:
    return yaml.load((REPO / "config" / "app_features" / f"{app_features}.yaml").read_text(encoding="utf-8"), Loader=_PlainLoader)["flags"]


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
    env = app_env(SPARMVET_APP_FEATURES=app_features, SPARMVET_DEPLOYMENT=deployment)
    with open(log, "w") as out:
        proc = subprocess.Popen(app_command(port),
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
            # 2026-11-08: Alerts moved from the right sidebar to the left (between Navigation
            # and the accordion) for the same reason — pipeline-static/pipeline-exploration-simple
            # have no right sidebar at all.
            assert page.locator("#notification_log_panel_ui").count() == 1, \
                "Alerts output must be mounted in every app features (left sidebar, never gated)"
            # slice B: the header strip. The data choice exists with interactivity; the mode switch only with the audit on; Compare only in
            # Audit mode (so never in the first view of a setup). simple: Exploration without a switch; static: no strip.
            flags = _flags(app_features)
            interactive, audit = bool(flags.get("interactivity_enabled")), bool(flags.get("t3_sandbox_enabled"))
            expect(page.locator("#data_view")).to_have_count(1 if interactive else 0, timeout=20_000)
            assert page.locator("#home_mode").count() == (1 if interactive and audit else 0), "the mode switch follows the audit flag"
            assert page.locator("#audit_compare").count() == 0, "Compare is not shown in Exploration"
            print(f"HEADER {app_features}: data choice={interactive} mode switch={interactive and audit}")
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
