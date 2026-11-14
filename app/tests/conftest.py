"""conftest.py — shared pytest fixtures for SPARMVET_VIZ tests.

Provides:
  - `shiny_app`: ShinyAppProc fixture for Playwright-based UI tests
  - `page`: module-scoped Playwright Page (one browser session per test module)

`page` is intentionally module-scoped (not the default function-scope) so all
tests in a module share one Shiny WebSocket session. This prevents session
accumulation on resource-constrained machines where 10+ concurrent sessions
cause T1 materialization timeouts.
"""

from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from shiny.pytest import create_app_fixture

APP_PATH = Path(__file__).parent.parent / "src" / "main.py"

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
