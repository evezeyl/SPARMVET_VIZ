"""app/handlers/data_import_handlers.py
Data Import accordion panel — testing_mode-aware data path display + ingestion slots.

New in Phase 25-F (ADR-052). Replaces the data ingestion slots that previously
lived in system_tools_ui.

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.

Display rules
-------------
- testing_mode == False  (pipeline-static, pipeline-exploration-simple):
    Read-only display of the configured/injected data paths derived from
    the active manifest's data_schemas. The user cannot override paths;
    they are fixed by the deployment configuration.
- testing_mode == True   (developer, qa, pipeline-exploration-advanced,
    project-independent):
    Same listing but framed as the *current default* and accompanied by
    the manifest replacement upload (gated by metadata_ingestion_enabled)
    and the multi-file ingestion slot (gated by data_ingestion_enabled).

Reactive value passed in: active_cfg (so the listing refreshes on project
switch).
"""

from __future__ import annotations

# @deps
# provides: function:define_data_import_server, output:data_import_ui, output:data_import_assignment_ui
# consumes: app/modules/orchestrator.py, app/src/bootloader.py, transformer.metadata_validator, shiny
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-052
# @end_deps

import shutil
from pathlib import Path

import polars as pl
from shiny import reactive, render, ui

from app.src.bootloader import bootloader


def define_data_import_server(input, output, session, *,
                              orchestrator, active_cfg, safe_input,
                              data_refresh_trigger=None,
                              notification_log=None):
    """Register the Data Import panel render handler.

    Parameters
    ----------
    orchestrator : DataOrchestrator
    active_cfg : reactive.Calc
    safe_input : callable
    data_refresh_trigger : reactive.Value[int] | None
        Increment after a successful import to invalidate plot renders.
    """
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    # Pending upload state: list of {name, tmp_path, ds_id, error}
    _import_pending: reactive.Value[list] = reactive.Value([])

    # ── Main panel UI (stable — refreshes only on project switch) ────────────

    @output
    @render.ui
    def data_import_ui():
        cfg = active_cfg()  # subscribe to project switches
        proj_id = safe_input(input, "project_id", bootloader.get_default_project())
        testing_mode = bootloader.get_testing_mode()
        prefer_discovery = bootloader.connector_config.get("prefer_discovery", False)

        # ── Source-file listing ─────────────────────────────────────────────
        if prefer_discovery:
            raw_data_dir = bootloader.get_location("raw_data")
            files_block = ui.div(
                ui.tags.small(
                    "Data location (provided by deployment):",
                    class_="text-muted fw-semibold d-block mb-1",
                    style="font-size:0.7em;",
                ),
                ui.tags.code(
                    str(raw_data_dir),
                    style="font-size:0.7em; word-break:break-all;",
                ),
                class_="px-2",
            )
        else:
            try:
                source_files = orchestrator.get_source_files(proj_id) if proj_id else {}
            except Exception:
                source_files = {}

            if source_files:
                file_rows = [
                    ui.div(
                        ui.tags.small(
                            f"{ds_id}: ",
                            class_="text-muted fw-semibold",
                            style="font-size:0.7em;",
                        ),
                        ui.tags.code(
                            str(path),
                            style="font-size:0.7em; word-break:break-all;",
                        ),
                        class_="mb-1",
                    )
                    for ds_id, path in sorted(source_files.items())
                ]
                files_block = ui.div(
                    *file_rows,
                    class_="px-2",
                    style="max-height:80px; overflow-y:auto;",
                )
            else:
                files_block = ui.tags.small(
                    "No source files resolved for this manifest.",
                    class_="text-muted px-2 d-block",
                    style="font-size:0.7em;",
                )

        if not testing_mode:
            return ui.div(
                ui.tags.small(
                    "🔒 Data paths are set by the deployment configuration (read-only).",
                    class_="text-info d-block mb-1 px-2",
                    style="font-size:0.7em;",
                ),
                files_block,
                class_="mb-2",
                style="font-size:0.8em;",
            )

        # ── Testing mode: listing + upload slots + assignment table ──────────
        upload_blocks: list = []

        if bootloader.is_enabled("metadata_ingestion_enabled"):
            upload_blocks.append(
                ui.div(
                    ui.tags.small(
                        "Metadata replacement (TSV)",
                        class_="text-muted fw-semibold d-block mb-1",
                        style="font-size:0.72em;",
                    ),
                    ui.input_file(
                        "data_import_metadata_upload", None,
                        accept=[".tsv", ".csv"], multiple=False,
                    ),
                    class_="mb-2 px-2",
                )
            )

        if bootloader.is_enabled("data_ingestion_enabled"):
            upload_blocks.append(
                ui.div(
                    ui.tags.small(
                        "Multi-file / Excel ingestion",
                        class_="text-muted fw-semibold d-block mb-1",
                        style="font-size:0.72em;",
                    ),
                    ui.input_file(
                        "data_import_multi_upload", None,
                        accept=[".tsv", ".csv", ".xlsx", ".xls"], multiple=True,
                    ),
                    ui.tags.small(
                        "💡 Hold Ctrl (Windows/Linux) or ⌘ Cmd (Mac) while clicking to select multiple files at once.",
                        class_="text-muted d-block",
                        style="font-size:0.65em;",
                    ),
                    # Assignment table + Apply rendered separately (doesn't reset upload widget)
                    ui.output_ui("data_import_assignment_ui"),
                    class_="mb-2 px-2",
                )
            )

        return ui.div(
            ui.tags.small(
                "Current default data paths (override below for testing):",
                class_="text-muted d-block mb-1 px-2",
                style="font-size:0.7em;",
            ),
            files_block,
            ui.hr(style="margin:6px 0;") if upload_blocks else ui.div(),
            *upload_blocks,
            class_="mb-2",
            style="font-size:0.8em;",
        )

    # ── Assignment table (dynamic — reacts to uploads and validation state) ──

    @output
    @render.ui
    def data_import_assignment_ui():
        pending = _import_pending.get()
        if not pending:
            return ui.div()

        cfg = active_cfg()
        raw = cfg.raw_config
        ds_ids = list(raw.get("data_schemas", {}).keys())
        if "metadata_schema" in raw:
            ds_ids = ["metadata_schema"] + ds_ids
        ds_ids = sorted(set(ds_ids))
        ds_choices = {d: d for d in ds_ids}

        rows = []
        for i, entry in enumerate(pending):
            fname = entry["name"]
            error = entry.get("error", "")
            rows.append(
                ui.div(
                    ui.div(
                        ui.tags.small(fname, class_="text-dark fw-semibold",
                                      style="font-size:0.72em; word-break:break-all;"),
                        ui.input_select(
                            f"data_import_assign_{i}", label=None,
                            choices={"": "— select dataset —", **ds_choices},
                            selected=entry.get("ds_id", ""),
                        ),
                        ui.div(
                            ui.tags.small(f"❌ {error}",
                                          class_="text-danger d-block",
                                          style="font-size:0.68em;"),
                        ) if error else ui.div(),
                        class_="flex-grow-1",
                    ),
                    class_="d-flex flex-column mb-2 p-2 border rounded",
                    style="background:#fafafa;",
                )
            )

        return ui.div(
            ui.hr(style="margin:4px 0 6px 0;"),
            ui.tags.small("Assign each file to a dataset:",
                          class_="text-muted fw-semibold d-block mb-1",
                          style="font-size:0.72em;"),
            *rows,
            ui.input_action_button(
                "data_import_apply", "✅ Validate & Apply",
                class_="btn-success btn-sm w-100 mt-1",
            ),
            style="font-size:0.8em;",
        )

    # ── Reactive: capture uploaded files ────────────────────────────────────

    @reactive.Effect
    @reactive.event(input.data_import_multi_upload)
    def _handle_multi_upload():
        files = input.data_import_multi_upload()
        if not files:
            return
        entries = [
            {"name": f["name"], "tmp_path": f["datapath"], "ds_id": "", "error": ""}
            for f in files
        ]
        _import_pending.set(entries)

    # ── Reactive: validate + write on Apply ──────────────────────────────────

    @reactive.Effect
    @reactive.event(input.data_import_apply)
    def _handle_apply():
        pending = list(_import_pending.get())
        if not pending:
            return

        _notify(
            f"⏳ Validating and importing {len(pending)} file(s) — please wait…",
            type="message", duration=8,
        )

        cfg = active_cfg()
        raw = cfg.raw_config
        proj_id = safe_input(input, "project_id", bootloader.get_default_project())
        anchor_dir = bootloader.get_location("user_sessions") / "anchors"

        from transformer.metadata_validator import MetadataValidator
        validator = MetadataValidator()

        any_error = False
        updated = []

        for i, entry in enumerate(pending):
            ds_id = safe_input(input, f"data_import_assign_{i}", "")
            entry = dict(entry, ds_id=ds_id, error="")

            if not ds_id:
                entry["error"] = "No dataset selected."
                any_error = True
                updated.append(entry)
                continue

            # Resolve input_fields contract for this dataset
            all_schemas = {}
            all_schemas.update(raw.get("data_schemas", {}))
            if "metadata_schema" in raw:
                all_schemas["metadata_schema"] = raw["metadata_schema"]
            ds_schema = all_schemas.get(ds_id, {})
            input_fields = ds_schema.get("input_fields", {})

            # Read uploaded file
            tmp = Path(entry["tmp_path"])
            try:
                name_lower = entry["name"].lower()
                if name_lower.endswith((".xlsx", ".xls")):
                    lf = pl.read_excel(tmp).lazy()
                else:
                    sep = "\t" if name_lower.endswith(".tsv") else ","
                    lf = pl.scan_csv(tmp, separator=sep)
            except Exception as e:
                entry["error"] = f"Could not read file: {e}"
                any_error = True
                updated.append(entry)
                continue

            # Validate against contract
            try:
                validator.validate(lf, input_fields, context=f"[{ds_id}]")
            except Exception as e:
                tip = getattr(e, "tip", "")
                entry["error"] = str(e) + (f" — {tip}" if tip else "")
                any_error = True
                updated.append(entry)
                continue

            # Determine target write path
            source = ds_schema.get("source", {})
            source_path = source.get("path")
            if source_path:
                target = Path(source_path)
            else:
                raw_data_dir = bootloader.get_location("raw_data")
                ext = Path(entry["name"]).suffix or ".tsv"
                target = raw_data_dir / f"{ds_id}{ext}"

            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(tmp, target)
            except Exception as e:
                entry["error"] = f"Could not write to {target}: {e}"
                any_error = True
                updated.append(entry)
                continue

            # Bust the parquet cache so next render re-materializes
            parquet_cache = anchor_dir / f"{ds_id}.parquet"
            if parquet_cache.exists():
                parquet_cache.unlink()
            bootloader.set_cached_asset(proj_id, ds_id, "anchor", "lf", None)

            entry["error"] = ""
            updated.append(entry)

        _import_pending.set(updated)

        if any_error:
            n_err = sum(1 for e in updated if e.get("error"))
            _notify(
                f"⚠️ {n_err} file(s) failed validation — see errors above. "
                "Fix and re-upload the failing files.",
                type="warning", duration=8,
            )
        else:
            n = len(updated)
            _import_pending.set([])
            if data_refresh_trigger is not None:
                data_refresh_trigger.set(data_refresh_trigger.get() + 1)
            _notify(
                f"✅ {n} file(s) imported — plots are refreshing now.",
                type="success", duration=6,
            )
