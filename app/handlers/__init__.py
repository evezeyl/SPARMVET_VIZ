# @deps
# provides: Shiny handler package (ADR-045 Two-Category Law); exposes define_server() entry points for all handler modules
# consumed_by: app/src/server.py
# doc: ADR-045
# @end_deps
"""app/handlers — Shiny Wiring Layer (ADR-045).

Each module in this package exposes a single entry point:

    define_server(input, output, session, *, <keyword-only dependencies>)

Constraints (Two-Category Law — ADR-045):
- Every file in this package MUST contain @render.* or @reactive.* decorators.
- These files MUST NOT be imported by non-Shiny contexts (headless scripts,
  test suites, CLI tools). Import hazard: importing a handler registers
  reactive side-effects that require an active Shiny session.
- Pure logic belongs in app/modules/ (importable anywhere, zero Shiny dep).

Handler modules
---------------
home_theater.py    — Home Theater: dynamic_tabs, sidebar_nav_ui, filters, plots, tables
audit_stack.py     — Pipeline Audit: T2/T3 nodes, btn_apply, track_audit_step_changes
blueprint_handlers.py — Blueprint Architect: data analysis recipe import, TubeMap, Lineage Rail
gallery_handlers.py — Gallery: filtering, preview, clone, submission
ingestion_handlers.py — Ingestion & app features switching
"""
