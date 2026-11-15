"""Staging for the browser tests of the HOME load gate (GATE-GAP-1): a staged copy of a shipped recipe, a running app, breaks and repairs.

The copy is `zz_gate_gap_stage` next to the shipped recipes (and its test data next to theirs); it is removed at the end,
so no shipped file changes. Its `info.label` is unique, so a test can see whether anything of the recipe is still on the page.
"""
import contextlib
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

from app.tests.subprocess_env import app_env

REPO = Path(__file__).resolve().parents[2]
PIPELINES = REPO / "config" / "data_analysis_recipes" / "pipelines"
TEST_DATA = REPO / "assets" / "test_data"
SOURCE = "1_test_data_ST22_dummy"
STAGE = "zz_gate_gap_stage"
LABEL = "ZZ Gate Gap Stage Label"
FRAGMENT = PIPELINES / STAGE / "wrangling" / "MLST_wrangling.yaml"
LABEL_OF_SOURCE = "ST22 Dummy Dataset"


def stage():
    unstage()
    shutil.copytree(PIPELINES / SOURCE, PIPELINES / STAGE)
    shutil.copytree(TEST_DATA / SOURCE, TEST_DATA / STAGE)
    text = (PIPELINES / f"{SOURCE}.yaml").read_text().replace(f"{SOURCE}/", f"{STAGE}/")
    text = text.replace(f"id: {SOURCE}", f"id: {STAGE}", 1).replace(f"label: {LABEL_OF_SOURCE}", f"label: {LABEL}", 1)
    (PIPELINES / f"{STAGE}.yaml").write_text(text)


def unstage():
    shutil.rmtree(PIPELINES / STAGE, ignore_errors=True)
    shutil.rmtree(TEST_DATA / STAGE, ignore_errors=True)
    (PIPELINES / f"{STAGE}.yaml").unlink(missing_ok=True)


def break_on_disk(kind: str) -> str:
    """Break the staged recipe behind the app's back; returns the text to restore with `repair`."""
    good = FRAGMENT.read_text()
    if kind == "missing_include":
        FRAGMENT.unlink()
    elif kind == "yaml_syntax":
        FRAGMENT.write_text(good + "\n  - [unclosed: {\n")
    elif kind == "unknown_action":
        FRAGMENT.write_text(good.replace("action: polars_fill_null", "action: zz_nope"))
    else:
        raise ValueError(kind)
    return good


def repair(good: str):
    FRAGMENT.write_text(good)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def running_app(tmp_path, features: str = "qa", recipe: str = STAGE):
    """The app on the staged recipe (named by SPARMVET_DATA_ANALYSIS_RECIPE); yields (url, log path). Always unstages."""
    stage()
    log = tmp_path / "server.log"
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES=features, SPARMVET_DATA_ANALYSIS_RECIPE=recipe)
    try:
        with open(log, "w") as out:
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
                yield url, log
            finally:
                proc.terminate()
                proc.wait(timeout=30)
    finally:
        unstage()


def wait_shiny(page, timeout: int = 20_000) -> None:
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=timeout)


def selector_options(page) -> list[str]:
    return page.evaluate("() => Array.from(document.querySelectorAll('#data_analysis_recipe_id option')).map(o => o.value)")


def selector_value(page):
    return page.evaluate("() => (document.querySelector('#data_analysis_recipe_id') || {}).value")


def theater_shows_content_of_a_recipe(page) -> dict:
    """What of a recipe is on the page: group tabs, tables, plots (the theater, not the sidebar)."""
    return page.evaluate("""() => ({
        tabs: document.querySelectorAll('#dynamic_tabs .nav-link').length,
        tables: document.querySelectorAll('#dynamic_tabs table, #dynamic_tabs .shiny-data-grid').length,
        plots: document.querySelectorAll('#dynamic_tabs img, #dynamic_tabs svg.main-svg, #dynamic_tabs .shiny-plot-output').length,
    })""")


SERVER_ERRORS = ("Exception in ASGI application", "SystemExit", "Unhandled error")


def server_errors(log: Path) -> list[str]:
    return [m for m in SERVER_ERRORS if m in log.read_text()]
