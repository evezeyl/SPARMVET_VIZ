"""app/handlers/ingestion_handlers.py
Ingestion Shiny wiring (ADR-045).

Entry point: define_server(input, output, session, *, bootloader, current_app_features, safe_input)

Concern: data analysis recipe file ingestion (btn_ingest).
Two-Category Law (ADR-045): This file contains @reactive.* decorators only.
It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (ingestion_handlers)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045
# @end_deps

import shutil
from pathlib import Path

from shiny import reactive, ui


def define_server(input, output, session, *, bootloader, current_app_features, safe_input):
    """Register ingestion and app features reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority instance (ADR-031). Reinitialised on ingest/app features change.
    current_app_features : reactive.Value[str]
        Shared app features reactive value (read/written here and by home_theater).
    safe_input : callable
        Shared utility: safe_input(input_obj, key, default) → value.
    """

    @reactive.Effect
    @reactive.event(input.btn_ingest)
    def handle_ingest():
        files = safe_input(input, "file_ingest", None)
        if not files:
            return
        ui.notification_show("⏳ Ingesting...", type="message")
        data_analysis_recipe_dir = bootloader.get_location("data_analysis_recipes")
        for f in files:
            name = f['name']
            path = Path(f['datapath'])
            if name.endswith(".yaml"):
                shutil.copy(path, data_analysis_recipe_dir / name)
        bootloader.__init__(app_features=current_app_features.get())
        ui.update_select("project_id", choices=list(
            bootloader.available_projects.keys()))
        ui.notification_show("✅ Ingestion complete.", type="success")

