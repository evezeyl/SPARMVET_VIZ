# @deps
# provides: app (Shiny App instance, entry point)
# consumes: shiny, app.src.ui, app.src.server
# consumed_by: Shiny runner (uvicorn/shiny run), __main__
# @end_deps
# app/src/app.py
from pathlib import Path
from shiny import App
from app.src.ui import app_ui
from app.src.server import server

# Vendored static assets (JS/CSS) served locally — no CDN dependency (air-gap safe).
# www/ contains: vendor/{cytoscape,dagre,cytoscape-dagre,bootstrap-icons} at pinned versions.
_www = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=_www)

if __name__ == "__main__":
    # Internal execution hook
    import os
    print(f"--- SPARMVET DASHBOARD INITIALIZED ---")
    print(f"Mode: pipeline")
    print(f"Venv: ./.venv/bin/python")
