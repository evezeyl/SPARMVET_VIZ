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

# ADR-096: Conditional docs bundling. Pre-deployment: `quarto render docs/` writes
# docs/_site/ (project.output-dir in docs/_quarto.yml). When present, it's mounted as
# static content at /docs/ and the "Full Documentation" link in sidebar_nav_ui (gated
# on docs_available) opens /docs/index.html in a new tab. A deployment that skips the
# render simply shows no link — fails closed, never a broken link.
_docs_site = Path(__file__).parent.parent.parent / "docs" / "_site"
docs_available = _docs_site.exists()

_static_assets = {"/": _www}
if docs_available:
    _static_assets["/docs"] = _docs_site

app = App(app_ui, server, static_assets=_static_assets)

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
