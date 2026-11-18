"""A test-only copy of the app whose switch to one recipe takes a long time on the server (D-0270, D-0050).

Why: the Export button must stay grey while the server is still working on a recipe switch, however long that takes. A real
recipe needs about 5 s at most on a test machine, so the case "the server is busy longer than the page's 5 s fallback" needs a
server made slow on purpose. This file changes no shipped file: it wraps the real server function and adds one effect that
blocks for SLOW_SECONDS when the recipe selector gets SLOW_RECIPE. The work holds Shiny's reactive lock as the real work does.

Run by `app/tests/test_export_ready_busy_wait.py` (it starts this file as its app).
"""
import time

from shiny import App, reactive

from app.src import main as _main
from app.src.server import server as _real_server
from app.src.ui import app_ui

SLOW_RECIPE = "3_test_no_joins"
SLOW_SECONDS = 7.0


def server(input, output, session):
    _real_server(input, output, session)
    seen = {"first": True}

    @reactive.effect
    def _slow_switch():
        value = input.data_analysis_recipe_id()
        if seen["first"]:
            seen["first"] = False
            return
        if value == SLOW_RECIPE:
            time.sleep(SLOW_SECONDS)


app = App(app_ui, server, static_assets=_main._static_assets)
