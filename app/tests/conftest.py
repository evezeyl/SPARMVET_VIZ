"""conftest.py — shared pytest fixtures for SPARMVET_VIZ tests.

Provides:
  - `shiny_app`: ShinyAppProc fixture for Playwright-based UI tests
  - `page`: module-scoped Playwright Page (one browser session per test module)

`page` is intentionally module-scoped (not the default function-scope) so all
tests in a module share one Shiny WebSocket session. This prevents session
accumulation on resource-constrained machines where 10+ concurrent sessions
cause T1 materialization timeouts.
"""

import os
from pathlib import Path

import pytest
import yaml

from app.tests.subprocess_env import app_env
from playwright.sync_api import sync_playwright
from shiny.pytest import create_app_fixture

APP_PATH = Path(__file__).parent.parent / "src" / "main.py"
REPO = Path(__file__).resolve().parents[2]


def _own_state_deployment() -> None:
    """Give each test process its own user data and cache folders (found in parallel runs: browser tests of different files
    seeded and deleted sessions in the one `tmp/UI_TEST/user/` of the local deployment, so a delete-all of one file emptied
    the sessions of another).

    The local deployment is copied with `user_data` and `cache` under `tmpAI/browser_state/<worker>/`; the in-process
    bootloader of the tests and the app they start (it inherits the variable) read the same file, so a test that seeds
    sessions through `bootloader.get_location("user_data")` still seeds what its app reads. Runs at import, before any
    test module imports the bootloader. A caller that sets SPARMVET_DEPLOYMENT keeps its own.
    """
    if os.environ.get("SPARMVET_DEPLOYMENT"):
        return
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    folder = REPO / "tmpAI" / "browser_state" / worker
    (folder / "user").mkdir(parents=True, exist_ok=True)
    (folder / "cache").mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load((REPO / "config" / "deployment" / "local" / "local.yaml").read_text(encoding="utf-8"))
    config["locations"]["user_data"] = str(folder / "user")
    config["locations"]["cache"] = str(folder / "cache")
    deployment = folder / "deployment.yaml"
    deployment.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    os.environ["SPARMVET_DEPLOYMENT"] = str(deployment)


_own_state_deployment()



@pytest.fixture(scope="session", autouse=True)
def _app_runs_this_checkouts_sources():
    """`create_app_fixture` starts the app with the environment of this process: give it this checkout's sources.

    Without it, in a git worktree the editable installs of the shared .venv make the app import the main checkout.
    """
    mp = pytest.MonkeyPatch()
    mp.setenv("PYTHONPATH", app_env()["PYTHONPATH"])
    yield
    mp.undo()


shiny_app = create_app_fixture(str(APP_PATH), scope="module")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Put the tail of the app process output (stdout and stderr) into the report of a failed browser test.

    `create_app_fixture` only logs the app output once, at fixture teardown, so a failure report never shows what the
    server did at that moment (error or nothing). A flaky failure must show which of the two it was.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    app = item.funcargs.get("shiny_app")
    if app is None:
        return
    for name in ("stdout", "stderr"):
        stream = getattr(app, name, None)
        lines = list(getattr(stream, "_lines", []))
        report.sections.append((f"app {name} (last 40 lines)", "".join(lines[-40:]) or "(no output)"))
