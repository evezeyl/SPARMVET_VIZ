"""issue #38 — with zero usable data analysis recipes the app must still render an empty
state, not crash. Repro steps from the issue: point locations.data_analysis_recipes of a
deployment at an empty folder, with no default_data_analysis_recipe set, and launch.

Modelled on test_every_app_features_starts.py's subprocess + log-scan pattern.
Browser test: needs Playwright and takes about 15 s.
"""
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect

REPO = Path(__file__).resolve().parents[2]
SERVER_ERRORS = ("Unhandled error", "Traceback", "ReactiveWarning")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _empty_deployment(tmp_path) -> Path:
    """A deployment whose data_analysis_recipes folder exists and is empty — no recipe
    on disk at all, no default_data_analysis_recipe named."""
    root = tmp_path / "data"
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    body = {
        "deployment_type": "filesystem",
        "deployment_name": "empty-recipes-test",
        "default_app_features": "qa",  # selector visible, so this is the non-fatal path
        "locations": locations,
    }
    dep = tmp_path / "dep.yaml"
    dep.write_text(yaml.safe_dump(body))
    return dep


def test_zero_recipes_renders_empty_state_without_server_error(page: Page, tmp_path):
    dep = _empty_deployment(tmp_path)
    log = tmp_path / "server.log"
    port = _free_port()
    env = {**os.environ, "PYTHONPATH": ".", "SPARMVET_APP_FEATURES": "qa", "SPARMVET_DEPLOYMENT": str(dep)}
    with open(log, "w") as out:
        proc = subprocess.Popen(
            [str(REPO / ".venv/bin/shiny"), "run", "app/src/main.py", "--port", str(port)],
            cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT,
        )
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(60):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            page.goto(url)
            # The empty-state message proves Home rendered instead of leaving a blank page.
            expect(page.get_by_text("No data analysis recipes yet")).to_be_visible(timeout=40_000)
            # Blueprint (where recipes are authored) must still be reachable and usable —
            # the issue is explicit that BLUEPRINT/Test Lab are not expected to need a recipe.
            page.get_by_text("Blueprint Architect", exact=True).first.click()
            expect(page.get_by_text("Blueprint Architect Flight Deck")).to_be_visible(timeout=20_000)
        finally:
            proc.terminate()
            proc.wait(timeout=20)
    text = log.read_text()
    assert not any(marker in text for marker in SERVER_ERRORS), text[-1500:]
