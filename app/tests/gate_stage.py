"""Staging for the browser tests of the HOME load gate (GATE-GAP-1): a staged copy of a shipped recipe, a running app, breaks and repairs.

The copy is `zz_gate_gap_stage` in a work folder of its own under `tmpAI/gate_stage/<unique name>/` (recipes, data, cache and
user data, and a deployment file that points at them); the app is started on that deployment. No tracked folder is written, so
a test that lists `assets/test_data` or `config/` in parallel never sees it. The folder is removed at the end.
One exception, forced by the app: Blueprint lists its recipes from `config/data_analysis_recipes/pipelines` of the working
folder and ignores the deployment's recipes location, so a test that drives Blueprint (`blueprint=True`) must put the staged
RECIPE there; only its recipe files go there (its data, cache and user data stay in the work folder) and they are removed at the end.
Its `info.label` is unique, so a test can see whether anything of the recipe is still on the page.
"""
import contextlib
import os
import shutil
import socket
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

import yaml

from app.tests.subprocess_env import app_command, app_env

REPO = Path(__file__).resolve().parents[2]
PIPELINES = REPO / "config" / "data_analysis_recipes" / "pipelines"
TEST_DATA = REPO / "assets" / "test_data"
SOURCE = "1_test_data_ST22_dummy"
STAGE = "zz_gate_gap_stage"
OTHER = "zz_gate_gap_other"
LABEL = "ZZ Gate Gap Stage Label"
LABEL_OF_SOURCE = "ST22 Dummy Dataset"
WORK_ROOT = REPO / "tmpAI" / "gate_stage"

# set by stage(): the work folder of the running app and the fragment a test breaks (one app per process at a time)
WORK: Path | None = None
FRAGMENT: Path | None = None


def stage(blueprint: bool = False) -> Path:
    """Build the staged recipe, its data and a deployment of their own in a new folder under tmpAI; returns the deployment file."""
    global WORK, FRAGMENT
    WORK = WORK_ROOT / uuid.uuid4().hex[:12]
    recipes, data = (PIPELINES if blueprint else WORK / "recipes"), WORK / "data"
    unstage_recipes()
    WORK.mkdir(parents=True)
    recipes.mkdir(exist_ok=True)
    shutil.copytree(PIPELINES / SOURCE, recipes / STAGE)
    shutil.copytree(TEST_DATA / SOURCE, data / STAGE)
    rel_data = "./" + os.path.relpath(data, REPO)
    text = (PIPELINES / f"{SOURCE}.yaml").read_text()
    text = text.replace(f"./assets/test_data/{SOURCE}/", f"{rel_data}/{STAGE}/")
    text = text.replace(f"{SOURCE}/", f"{STAGE}/")
    text = text.replace(f"id: {SOURCE}", f"id: {STAGE}", 1).replace(f"label: {LABEL_OF_SOURCE}", f"label: {LABEL}", 1)
    (recipes / f"{STAGE}.yaml").write_text(text)
    if not blueprint:
        # a second, healthy recipe: when the open one is dropped by the gate, HOME shows another (the shipped folder has many)
        shutil.copytree(PIPELINES / SOURCE, recipes / OTHER)
        other = (PIPELINES / f"{SOURCE}.yaml").read_text().replace(f"./assets/test_data/{SOURCE}/", f"{rel_data}/{STAGE}/")
        other = other.replace(f"{SOURCE}/", f"{OTHER}/").replace(f"id: {SOURCE}", f"id: {OTHER}", 1)
        (recipes / f"{OTHER}.yaml").write_text(other)
    FRAGMENT = recipes / STAGE / "wrangling" / "MLST_wrangling.yaml"
    locations = {"raw_data": str(data), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir()
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "gate stage", "locations": locations,
                                          "default_data_analysis_recipe": STAGE, "default_app_features": "qa"}), encoding="utf-8")
    return deployment


def unstage_recipes():
    """Remove a staged recipe left in the shipped recipe folder (only the Blueprint mode puts one there)."""
    shutil.rmtree(PIPELINES / STAGE, ignore_errors=True)
    (PIPELINES / f"{STAGE}.yaml").unlink(missing_ok=True)


def unstage():
    unstage_recipes()
    if WORK is not None:
        shutil.rmtree(WORK, ignore_errors=True)


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
def running_app(tmp_path, features: str = "qa", recipe: str = STAGE, blueprint: bool = False):
    """The app on the staged recipe (named by SPARMVET_DATA_ANALYSIS_RECIPE); yields (url, log path). Always removes its work folder."""
    deployment = stage(blueprint)
    log = tmp_path / "server.log"
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES=features, SPARMVET_DATA_ANALYSIS_RECIPE=recipe, SPARMVET_DEPLOYMENT=str(deployment))
    try:
        with open(log, "w") as out:
            proc = subprocess.Popen(app_command(port),
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
