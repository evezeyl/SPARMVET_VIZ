# @deps
# provides: app (Shiny App instance, entry point), docs_available (bool flag for conditional docs link)
# consumes: shiny, app.src.ui, app.src.server
# consumed_by: Shiny runner (uvicorn/shiny run), __main__, help modal handlers
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

# HELP-DOCS-1: Conditional docs bundling (ADR-061)
# Pre-deployment: run `quarto render docs/` to generate docs/_site/
# When docs/_site exists, it is mounted as static content accessible at /docs/
# and a "Full documentation" link is shown in help modals (handlers use docs_available flag).
_docs_site = Path(__file__).parent.parent.parent / "docs" / "_site"
docs_available = _docs_site.exists()

if __name__ == "__main__":
    # Internal execution hook
    import os
    print(f"--- SPARMVET DASHBOARD INITIALIZED ---")
    print(f"Mode: pipeline")
    print(f"Venv: ./.venv/bin/python")
    if docs_available:
        print(f"✅ Documentation available at /docs/")
    else:
        print(f"ℹ️  Documentation not bundled (run 'quarto render docs/' before deployment)")
