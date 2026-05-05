"""app/handlers/ingestion_handlers.py
Ingestion Shiny wiring (ADR-045).

Entry point: define_server(input, output, session, *, bootloader, current_persona, safe_input)

Concern: manifest file ingestion (btn_ingest).
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


def define_server(input, output, session, *, bootloader, current_persona, safe_input):
    """Register ingestion and persona reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority instance (ADR-031). Reinitialised on ingest/persona change.
    current_persona : reactive.Value[str]
        Shared persona reactive value (read/written here and by home_theater).
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
        manifest_dir = bootloader.get_location("manifests")
        for f in files:
            name = f['name']
            path = Path(f['datapath'])
            if name.endswith(".yaml"):
                shutil.copy(path, manifest_dir / name)
        bootloader.__init__(persona=current_persona.get())
        ui.update_select("project_id", choices=list(
            bootloader.available_projects.keys()))
        ui.notification_show("✅ Ingestion complete.", type="success")

