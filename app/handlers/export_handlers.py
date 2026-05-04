"""app/handlers/export_handlers.py
Export pipeline: results bundle (.zip) + audit report (HTML/DOCX) +
system tools sidebar UI.

Extracted from home_theater.py in Phase 24-C (ADR-051).

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_export_server, output:system_tools_ui, output:export_bundle_download
# consumes: app/modules/exporter.py, app/modules/session_manager.py, libs/viz_factory/src/viz_factory/viz_factory.py, polars, shiny
# consumed_by: app/handlers/home_theater.py
# doc: .antigravity/knowledge/architecture_decisions.md#ADR-045, .antigravity/knowledge/architecture_decisions.md#ADR-051, .antigravity/design/export_specification.md
# @end_deps

from pathlib import Path

import polars as pl
from shiny import reactive, render, ui

from app.modules.t3_recipe_engine import _op_label


def define_export_server(input, output, session, *,
                         bootloader, orchestrator, viz_factory,
                         current_persona, active_cfg,
                         tier1_anchor, tier_reference, tier3_leaf,
                         tier_toggle, applied_filters,
                         home_state, safe_input,
                         active_home_subtab=None,
                         notification_log=None):
    """Register export-bundle + system-tools handlers.

    Reactive deps (kwargs):
      bootloader         : Path Authority (ADR-031)
      orchestrator       : tier1/tier2 materialiser
      viz_factory        : plot renderer
      current_persona    : reactive.Value[str]
      active_cfg         : reactive.Calc[ConfigManager]
      tier1_anchor       : reactive.Calc[LazyFrame]
      tier_reference     : reactive.Calc[LazyFrame | None]
      tier3_leaf         : reactive.Calc[DataFrame | None]
      tier_toggle        : reactive.Value[str]   ("T1"|"T2"|"T3")
      applied_filters    : reactive.Value[list]
      home_state         : reactive.Value[dict] | None
      safe_input         : helper (input, key, default) → value
      active_home_subtab : reactive.Value[str] | None  — current plot subtab id
    """
    from app.handlers.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    @output
    @render.ui
    def system_tools_ui():
        if not bootloader.is_enabled("export_bundle_enabled"):
            return ui.div()

        n_active = len(applied_filters.get())
        filter_warning = ui.div()
        if n_active:
            filter_warning = ui.tags.small(
                f"⚠ {n_active} active filter(s) — a note will be embedded in the bundle.",
                class_="text-warning d-block mb-1",
                style="font-size:0.7em;"
            )

        # 3-way scope toggle — only when persona has BOTH export_bundle + export_graph
        scope_toggle = ui.div()
        if bootloader.is_enabled("export_graph_enabled") and active_home_subtab is not None:
            cfg = active_cfg()
            groups = cfg.raw_config.get("analysis_groups", {})
            has_groups = bool(groups)

            subtab = active_home_subtab.get() or ""
            active_pid = subtab.removeprefix("subtab_") if subtab.startswith("subtab_") else ""

            # Determine which group the active plot belongs to
            active_gid = None
            if active_pid and has_groups:
                for gid, gspec in groups.items():
                    if active_pid in gspec.get("plots", {}):
                        active_gid = gid
                        break

            scope_choices: dict = {
                "global": ui.span(
                    "Global project",
                    title="Export everything in the active project",
                )
            }
            # Active group: only shown when manifest has groups AND active plot has a group
            if has_groups and active_gid is not None:
                scope_choices["group"] = ui.span(
                    f"Active group ({active_gid})",
                    title="Export all plots in the current group (e.g. all Quality Control plots)",
                )
            elif has_groups and not active_pid:
                # Groups exist but no plot tab open — show disabled-looking label
                scope_choices["group"] = ui.span(
                    "Active group",
                    title="Switch to a plot tab to enable scoped export.",
                    style="opacity:0.45; cursor:not-allowed;",
                )
            # Active plot
            if active_pid:
                scope_choices["plot"] = ui.span(
                    f"Active plot ({active_pid})",
                    title="Export only the plot you are currently viewing",
                )
            else:
                scope_choices["plot"] = ui.span(
                    "Active plot",
                    title="Switch to a plot tab to enable scoped export.",
                    style="opacity:0.45; cursor:not-allowed;",
                )

            scope_toggle = ui.div(
                ui.input_radio_buttons(
                    "export_scope",
                    label="Scope",
                    choices=scope_choices,
                    selected="global",
                    inline=True,
                ),
                class_="mb-1",
            )

        return ui.div(
            ui.div(
                ui.input_text(
                    "export_user_name", label="Bundle label / name",
                    placeholder="label (no spaces, no special characters)…",
                    value="",
                ),
                scope_toggle,
                ui.input_radio_buttons(
                    "export_preset",
                    label="Quality",
                    choices={"web": "Web / Presentation", "publication": "Publication (≥600 DPI)"},
                    selected="web",
                    inline=False,
                ),
                ui.input_radio_buttons(
                    "export_plot_format",
                    label="Plot format",
                    choices={"png": "PNG", "svg": "SVG", "pdf": "PDF"},
                    selected="png",
                    inline=True,
                ),
                ui.tags.small(
                    "SVG is resolution-independent — rescale or convert to any dimension or format without quality loss.",
                    class_="text-muted d-block mb-1",
                    style="font-size:0.7em;",
                ),
                ui.input_radio_buttons(
                    "export_report_format",
                    label="Report format",
                    choices={"html": "HTML", "pdf": "PDF", "docx": "DOCX"},
                    selected="html",
                    inline=True,
                ),
                filter_warning,
                ui.download_button(
                    "export_bundle_download",
                    "💾 Export Bundle",
                    class_="btn-success btn-sm w-100 mt-1",
                ),
                class_="mb-2 px-2",
                style="font-size:0.8em;"
            ),
        )

    @render.download(filename=lambda: _export_bundle_filename())
    async def export_bundle_download():
        """
        Phase 21-I: Export Results Bundle.

        Produces a zip file containing:
        - plots/          SVG (web preset) or high-DPI PNG (publication preset) per plot
        - data/           T1 TSV for each dataset referenced by active plots
        - recipes/        YAML wrangling recipe(s) for the active project
        - FILTERS.txt     If any applied_filters exist ("No Trace No Export" compliance note)
        - report.qmd      Quarto source report embedding all plots and datasets
        - README.txt      Bundle manifest (timestamp, project, persona, preset)
        """
        import io
        import zipfile
        import tempfile
        import datetime
        import shutil
        import csv
        import copy

        now = datetime.datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        raw_name = safe_input(input, "export_user_name", "user").strip() or "user"
        # Sanitize: replace spaces/special chars with underscore, lowercase
        import re
        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", raw_name)[:40]
        preset = safe_input(input, "export_preset", "web")
        plot_fmt = safe_input(input, "export_plot_format", "png")
        report_fmt = safe_input(input, "export_report_format", "html")
        persona = current_persona.get()
        dpi = 300 if preset == "web" else 600

        cfg = active_cfg()
        proj_id = safe_input(input, "project_id", bootloader.get_default_project())
        groups = cfg.raw_config.get("analysis_groups", {})
        top_plots = cfg.raw_config.get("plots", {})
        active_filters = applied_filters.get()

        # Collect all (plot_id, spec) pairs for this export
        all_plots: list[tuple[str, dict]] = []
        for _gid, gspec in groups.items():
            for p_id, pentry in gspec.get("plots", {}).items():
                spec = pentry.get("spec")
                if spec:
                    all_plots.append((p_id, spec))
        if not all_plots:
            for p_id, spec in top_plots.items():
                all_plots.append((p_id, spec))

        # ── Apply export scope (Global / Active group / Active plot) ──────
        export_scope = safe_input(input, "export_scope", "global")
        scope_label = "global"
        _subtab = (active_home_subtab.get() or "") if active_home_subtab is not None else ""
        active_pid = _subtab.removeprefix("subtab_") if _subtab.startswith("subtab_") else ""

        if export_scope == "plot" and active_pid:
            _filtered = [(p, s) for p, s in all_plots if p == active_pid]
            if _filtered:
                all_plots = _filtered
                scope_label = active_pid
        elif export_scope == "group" and active_pid and groups:
            _active_gid = None
            for _gid, _gspec in groups.items():
                if active_pid in _gspec.get("plots", {}):
                    _active_gid = _gid
                    break
            if _active_gid:
                _gplot_ids = set(groups[_active_gid].get("plots", {}).keys())
                _filtered = [(p, s) for p, s in all_plots if p in _gplot_ids]
                if _filtered:
                    all_plots = _filtered
                    scope_label = _active_gid

        # ── Collect T3 audit data (per-plot active nodes) ─────────────────
        _t3_by_plot: dict[str, list[dict]] = {}
        if home_state is not None and bootloader.is_enabled("t3_sandbox_enabled"):
            _state = home_state.get()
            _rbp = _state.get("t3_recipe_by_plot", {}) or {}
            for _pid, _ in all_plots:
                _nodes = [n for n in _rbp.get(f"subtab_{_pid}", []) if n.get("active", True)]
                if _nodes:
                    _t3_by_plot[_pid] = _nodes

        # Dataset → plots mapping (used for folder structure + README + report)
        import re as _re
        def _safe_ds_name(ds_key: str) -> str:
            return _re.sub(r"[^A-Za-z0-9_-]", "_", ds_key)

        ds_to_plots: dict[str, list[str]] = {}
        for p_id, spec in all_plots:
            ds_key = spec.get("target_dataset") or "__anchor__"
            ds_to_plots.setdefault(ds_key, []).append(p_id)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            bundle_dir = f"{ts}_{safe_name}"

            # ── FILTERS.txt (No Trace No Export) ─────────────────────────
            if active_filters:
                lines = [
                    "FILTER TRACE — embedded per 'No Trace No Export' protocol.",
                    f"Exported at: {now.isoformat()}",
                    f"Project: {proj_id}",
                    "",
                    "Applied filters at time of export:",
                ]
                for i, f in enumerate(active_filters, 1):
                    col = f.get("column", "?")
                    op = _op_label(f.get("op", "eq"))
                    val = f.get("value", "")
                    val_str = ", ".join(str(v) for v in val) if isinstance(val, list) else str(val)
                    lines.append(f"  {i}. {col} {op} {val_str}")
                zf.writestr(f"{bundle_dir}/FILTERS.txt", "\n".join(lines))

            # ── Render and save plots ─────────────────────────────────────
            # plot_bytes  → zip's plots/   in the user's chosen format (always).
            # qmd_plot_bytes → _render/    in a Quarto-compatible format.
            #
            # _QUARTO_NATIVE_PLOT_FMTS is the extension point: when adding a new
            # output format (epub, revealjs, …) add one entry here.
            # SVG in PDF output depends on rsvg-convert being available at runtime.
            import shutil as _shutil
            _has_rsvg = _shutil.which("rsvg-convert") is not None
            _QUARTO_NATIVE_PLOT_FMTS: dict[str, set[str]] = {
                # report_fmt → plot formats Quarto can embed natively
                "html":  {"png", "svg", "jpg", "gif", "webp"},
                "pdf":   {"png", "jpg", "pdf"} | ({"svg"} if _has_rsvg else set()),
                "docx":  {"png", "svg", "jpg", "emf"},
            }
            # Per-output fallback format when the user's plot format isn't native.
            # DOCX uses SVG (vector, crisp at any zoom) instead of PNG.
            # PDF and HTML fall back to PNG.
            _QUARTO_PLOT_FALLBACK: dict[str, str] = {
                "html": "png",
                "pdf":  "png",
                "docx": "svg",
            }
            _native = _QUARTO_NATIVE_PLOT_FMTS.get(report_fmt, {plot_fmt})
            _fallback = _QUARTO_PLOT_FALLBACK.get(report_fmt, "png")
            qmd_plot_fmt = plot_fmt if plot_fmt in _native else _fallback
            plot_bytes: dict[str, bytes] = {}      # p_id → bytes (user format)
            qmd_plot_bytes: dict[str, bytes] = {}  # p_id → bytes for Quarto (_render/)
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)

                for p_id, spec in all_plots:
                    _ds_key = spec.get("target_dataset") or "__anchor__"
                    _safe_ds = _safe_ds_name(_ds_key)
                    try:
                        # Build synthetic manifest with applied filters
                        plot_spec = copy.deepcopy(spec)
                        if active_filters:
                            vf_filters = [
                                {k: v for k, v in f.items() if k != "dtype"}
                                for f in active_filters
                            ]
                            for vf in vf_filters:
                                if isinstance(vf.get("value"), list):
                                    vf["op"] = "in" if vf["op"] in ("eq", "in") else "not_in"
                            plot_spec["filters"] = vf_filters

                        synthetic_manifest = {
                            "plots": {p_id: plot_spec},
                            "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
                        }

                        # Resolve dataset
                        target_ds = spec.get("target_dataset")
                        if target_ds:
                            anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                            out_path = anchor_dir / f"{target_ds}.parquet"
                            if out_path.exists():
                                lf = pl.scan_parquet(out_path)
                            else:
                                lf = orchestrator.materialize_tier1(
                                    project_id=proj_id,
                                    collection_id=target_ds,
                                    output_path=out_path
                                )
                        else:
                            lf = tier1_anchor()

                        fig = viz_factory.render(lf, synthetic_manifest, p_id)

                        # Save user-chosen format → zip under {dataset}/plots/
                        plot_path = tmpdir_path / f"{p_id}.{plot_fmt}"
                        fig.save(str(plot_path), verbose=False,
                                 format=plot_fmt, dpi=dpi)

                        with open(plot_path, "rb") as f:
                            raw = f.read()
                        plot_bytes[p_id] = raw
                        zf.writestr(f"{bundle_dir}/{_safe_ds}/plots/{p_id}.{plot_fmt}", raw)

                        # When SVG plots + PDF report: also render PNG for Quarto
                        # (LuaLaTeX cannot embed SVGs without rsvg-convert)
                        if qmd_plot_fmt != plot_fmt:
                            qmd_path = tmpdir_path / f"{p_id}.{qmd_plot_fmt}"
                            fig.save(str(qmd_path), verbose=False,
                                     format=qmd_plot_fmt, dpi=dpi)
                            with open(qmd_path, "rb") as f:
                                qmd_plot_bytes[p_id] = f.read()
                        else:
                            qmd_plot_bytes[p_id] = raw

                    except Exception as e:
                        # Write error stub so bundle is still complete
                        zf.writestr(
                            f"{bundle_dir}/{_safe_ds}/plots/{p_id}_ERROR.txt",
                            f"Plot render failed:\n{e}"
                        )

                # ── Export data by tier ───────────────────────────────────
                # T1: always exported.
                # T2: skipped — _apply_tier2_transforms is currently a no-op (T2 == T1
                #     at dataset level; per-plot column transforms happen inside VizFactory).
                #     A note is added to README and report instead of a duplicate TSV.
                # T3: only for advanced+ personas, and only when tier_toggle == "T3".
                is_advanced = bootloader.is_enabled("t3_sandbox_enabled")
                active_tier = tier_toggle.get()  # "T1", "T2", "T3"
                export_t3 = is_advanced and active_tier == "T3"
                t2_equals_t1 = True  # Update when dataset-level T2 transforms are implemented

                exported_datasets: set[str] = set()
                exported_dfs: dict[str, "pl.DataFrame"] = {}  # ds_key → T1 DataFrame for report
                for p_id, spec in all_plots:
                    target_ds = spec.get("target_dataset")
                    ds_key = target_ds or "__tier1_anchor__"
                    if ds_key in exported_datasets:
                        continue
                    exported_datasets.add(ds_key)

                    safe_ds = _safe_ds_name(ds_key)

                    # ── T1 ────────────────────────────────────────────────
                    try:
                        if target_ds:
                            anchor_dir = bootloader.get_location("user_sessions") / "anchors"
                            out_path = anchor_dir / f"{target_ds}.parquet"
                            if out_path.exists():
                                lf_t1 = pl.scan_parquet(out_path)
                            else:
                                lf_t1 = orchestrator.materialize_tier1(
                                    project_id=proj_id,
                                    collection_id=target_ds,
                                    output_path=out_path
                                )
                        else:
                            lf_t1 = tier1_anchor()
                        df_t1 = lf_t1.collect()
                        exported_dfs[ds_key] = df_t1
                        tsv_path = tmpdir_path / f"{safe_ds}_T1.tsv"
                        df_t1.write_csv(str(tsv_path), separator="\t")
                        with open(tsv_path, "rb") as f:
                            zf.writestr(f"{bundle_dir}/{safe_ds}/T1_data.tsv", f.read())
                    except Exception as e:
                        zf.writestr(
                            f"{bundle_dir}/{safe_ds}/T1_data_ERROR.txt",
                            f"T1 data export failed:\n{e}"
                        )

                    # ── T2 (exported when tier2 recipe steps exist) ───────
                    try:
                        from transformer.data_wrangler import DataWrangler
                        collection_spec = (
                            active_cfg().raw_config
                            .get("join_manifests", {})
                            .get(target_ds or "", {})
                        )
                        recipe_raw = collection_spec.get("recipe", [])
                        t2_steps = DataWrangler._resolve_tier(recipe_raw, "tier2")
                        if t2_steps:
                            lf_t2 = DataWrangler(data_schema={}).run(lf_t1, t2_steps)
                            df_t2 = lf_t2.collect()
                            tsv_path = tmpdir_path / f"{safe_ds}_T2.tsv"
                            df_t2.write_csv(str(tsv_path), separator="\t")
                            with open(tsv_path, "rb") as f:
                                zf.writestr(f"{bundle_dir}/{safe_ds}/T2_data.tsv", f.read())
                    except Exception as e:
                        zf.writestr(
                            f"{bundle_dir}/{safe_ds}/T2_data_ERROR.txt",
                            f"T2 data export failed:\n{e}"
                        )

                    # ── T3 (advanced persona + T3 active only) ────────────
                    if export_t3:
                        try:
                            df_t3 = tier3_leaf()
                            if df_t3 is not None:
                                tsv_path = tmpdir_path / f"{safe_ds}_T3.tsv"
                                df_t3.write_csv(str(tsv_path), separator="\t")
                                with open(tsv_path, "rb") as f:
                                    zf.writestr(
                                        f"{bundle_dir}/{safe_ds}/T3_data.tsv", f.read()
                                    )
                        except Exception as e:
                            zf.writestr(
                                f"{bundle_dir}/{safe_ds}/T3_data_ERROR.txt",
                                f"T3 data export failed:\n{e}"
                            )

                # ── Copy YAML recipes (active project ONLY) ──────────────
                # EXPORT-BUG-2 (2026-04-30): the previous code did
                # proj_dir.rglob("*.yaml") on the parent directory, which
                # scooped up EVERY other project's manifest + their include
                # fragments into the bundle (cross-project leak). Now we copy:
                #   1. The active project's manifest itself
                #   2. Its `!include` subdirectory if one exists (named
                #      `{proj_id}/`) — that's where fragment files live per
                #      the basename-mirroring convention.
                try:
                    proj_manifest_path = bootloader.available_projects.get(proj_id)
                    if proj_manifest_path:
                        manifest_p = Path(str(proj_manifest_path))
                        proj_dir = manifest_p.parent
                        # 1. The active manifest itself
                        with open(manifest_p, "rb") as f:
                            zf.writestr(
                                f"{bundle_dir}/recipes/{manifest_p.name}",
                                f.read()
                            )
                        # 2. Includes subdirectory (if it exists for this project)
                        includes_dir = proj_dir / proj_id
                        if includes_dir.is_dir():
                            for yaml_file in includes_dir.rglob("*.yaml"):
                                rel = yaml_file.relative_to(proj_dir)
                                with open(yaml_file, "rb") as f:
                                    zf.writestr(
                                        f"{bundle_dir}/recipes/{rel}",
                                        f.read()
                                    )
                except Exception as e:
                    zf.writestr(f"{bundle_dir}/recipes/ERROR.txt", str(e))

                # ── t3_steps.yaml (when T3 has committed changes) ─────────
                if _t3_by_plot:
                    try:
                        import yaml as _yaml
                        t3_steps_data = {
                            "generated": now.isoformat(),
                            "export_scope": scope_label,
                            "t3_steps": {
                                _pid: [
                                    {
                                        "action": n.get("node_type", "unknown"),
                                        **n.get("params", {}),
                                        "reason": n.get("reason", ""),
                                        "committed_at": n.get("created_at", ""),
                                    }
                                    for n in _nodes
                                ]
                                for _pid, _nodes in _t3_by_plot.items()
                            },
                        }
                        zf.writestr(
                            f"{bundle_dir}/recipes/t3_steps.yaml",
                            _yaml.safe_dump(t3_steps_data, sort_keys=False, allow_unicode=True),
                        )
                    except Exception as e:
                        zf.writestr(f"{bundle_dir}/recipes/t3_steps_ERROR.txt", str(e))

            # ── Compute hashes for reproducibility ────────────────────────
            import hashlib as _hashlib
            manifest_sha = ""
            data_sha = ""
            try:
                proj_manifest_path = bootloader.available_projects.get(proj_id)
                if proj_manifest_path:
                    manifest_bytes = Path(str(proj_manifest_path)).read_bytes()
                    manifest_sha = _hashlib.sha256(manifest_bytes).hexdigest()
            except Exception:
                pass
            # Prefer the session data_batch_hash (SHA256 of raw source file bytes,
            # consistent with the session key). Fall back to a T1-content fingerprint
            # only when home_state is unavailable (e.g. headless export path).
            if home_state is not None:
                try:
                    data_sha = home_state.get().get("data_batch_hash") or ""
                except Exception:
                    pass
            if not data_sha:
                try:
                    anchor_lf = tier1_anchor()
                    df_anchor = anchor_lf.collect()
                    fingerprint = f"{df_anchor.columns}|{df_anchor.shape}|{df_anchor.head(500).write_csv()}"
                    data_sha = _hashlib.sha256(fingerprint.encode()).hexdigest()
                except Exception:
                    pass

            tiers_exported = ["T1"] + (["T3"] if export_t3 else [])

            # ── Generate Quarto .qmd report ───────────────────────────────
            # QMD image refs use qmd_plot_fmt (PNG when PDF+SVG mismatch)
            plot_ext = qmd_plot_fmt

            # Build mapping table rows for QMD and README
            mapping_rows = [
                (ds_key, _safe_ds_name(ds_key), plot_list)
                for ds_key, plot_list in ds_to_plots.items()
            ]

            qmd_lines = [
                "---",
                f'title: "Results Report — {proj_id}"',
                f'date: "{now.strftime("%Y-%m-%d")}"',
                f'author: "{safe_name}"',
                'format:',
                '  html:',
                '    self-contained: true',
                '  pdf:',
                '    documentclass: article',
                '  docx: default',
                "---",
                "",
                "## Overview",
                "",
                f"Project: **{proj_id}**  ",
                f"Persona: **{persona}**  ",
                f"Export preset: **{preset}**  ",
                f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}  ",
                "",
                "## Dataset → Plot Mapping",
                "",
                "| Dataset | Plots |",
                "|---------|-------|",
            ]
            for ds_key, safe_ds, plot_list in mapping_rows:
                plots_str = ", ".join(f"`{p}`" for p in plot_list)
                qmd_lines.append(f"| `{ds_key}` | {plots_str} |")
            qmd_lines.append("")

            qmd_lines += [
                "## Provenance",
                "",
                "| Hash | Value | Meaning |",
                "|------|-------|---------|",
                f"| Manifest SHA256 | `{manifest_sha or 'n/a'}` | SHA256 of manifest YAML file bytes |",
                f"| Data SHA256 | `{data_sha or 'n/a'}` | SHA256 of all raw source file bytes (sorted by dataset id) |",
                f"| Recipe hash | see Parquet metadata key `sparmvet_decision_hash` | SHA256 of wrangling recipe dict — one per T1/T2 Parquet file |",
                "",
                "> These three hashes allow independent verification that this report was generated",
                "> from the exact manifest, raw data, and wrangling recipe present at export time.",
                "> To recompute: `SHA256(manifest_yaml_bytes)`, `SHA256(sorted per-file SHA256s)`,",
                "> and read `sparmvet_decision_hash` from each Parquet metadata block.",
                "",
                "## About the data in this report",
                "",
                "The data behind these results exists in up to three versions, called **tiers**:",
                "",
                "| Tier | What it is |",
                "|------|------------|",
                "| **T1 — Raw data** | The original assembled dataset exactly as it came out of the analysis pipeline. Nothing has been changed. This is what you find in the `data/` folder. |",
                "| **T2 — Display-ready data** | The same data as T1, but with cosmetic adjustments applied when drawing each figure (e.g. renaming a column from an internal code to a readable label, or converting units for display). These adjustments exist only inside the figures — the underlying numbers are identical to T1. No separate T2 file is included because it would be a duplicate. |",
                "| **T3 — Filtered data** | T1 with one or more rows or columns removed by the analyst before export (e.g. excluding a sample that failed QC). When a T3 version exists it is exported separately alongside T1 so you can always compare. |",
                "",
            ]
            if active_filters:
                qmd_lines += [
                    "## Active Filters at Export",
                    "",
                    "| Column | Op | Value |",
                    "|--------|-----|-------|",
                ]
                for f in active_filters:
                    col = f.get("column", "?")
                    op = _op_label(f.get("op", "eq"))
                    val = f.get("value", "")
                    val_str = ", ".join(str(v) for v in val) if isinstance(val, list) else str(val)
                    qmd_lines.append(f"| {col} | {op} | {val_str} |")
                qmd_lines.append("")

            # QMD image paths point to _render/ (Quarto-compatible copies).
            # _render/ is written into the Quarto temp dir alongside report.qmd.
            # The user-facing plots/ folder in the zip keeps the chosen format.
            qmd_lines += ["## Plots", ""]
            for p_id, spec in all_plots:
                label = spec.get("title") or p_id.replace("_", " ").title()
                ds_note = spec.get("target_dataset") or "—"
                qmd_lines += [
                    f"### {label}",
                    "",
                    f"*Dataset: `{ds_note}`*  ",
                    "",
                    f"![{label}](_render/{p_id}.{plot_ext}){{width=100%}}",
                    "",
                ]

            qmd_lines += [
                "## Data files",
                "",
                "> **Keep the folder structure intact.**  ",
                "> Data files live under `<dataset>/` subfolders alongside their plots.",
                "> The links below are relative paths from the report file location.",
                "",
            ]
            for ds_key, safe_ds, plot_list in mapping_rows:
                df_preview = exported_dfs.get(ds_key)
                shape_note = (
                    f"{df_preview.height} rows × {len(df_preview.columns)} columns"
                    if df_preview is not None else ""
                )
                plots_str = ", ".join(f"`{p}`" for p in plot_list)
                qmd_lines += [f"### {ds_key}", ""]
                qmd_lines.append(f"*Used by: {plots_str}*  ")
                if shape_note:
                    qmd_lines.append(f"*{shape_note}*  ")
                qmd_lines.append("")
                for tier in tiers_exported:
                    tier_label = {
                        "T1": "Raw data (T1)",
                        "T3": "Analyst-filtered data (T3)",
                    }.get(tier, tier)
                    qmd_lines.append(
                        f"[{tier_label}]({safe_ds}/{tier}_data.tsv)"
                    )
                qmd_lines.append("")

            # ── T3 Audit Trail section ────────────────────────────────────
            if _t3_by_plot:
                qmd_lines += ["## T3 Audit Trail", ""]
                for _pid, _nodes in _t3_by_plot.items():
                    _spec_title = next(
                        (s.get("title") for p, s in all_plots if p == _pid), None
                    )
                    _section_label = _spec_title or _pid.replace("_", " ").title()
                    qmd_lines += [
                        f"### {_section_label}",
                        "",
                        "| Step | Action | Details | Justification |",
                        "|------|--------|---------|---------------|",
                    ]
                    for _i, _n in enumerate(_nodes, 1):
                        _action = _n.get("node_type", "?")
                        _params = _n.get("params", {})
                        _details = "; ".join(
                            f"{k}={v}" for k, v in _params.items()
                        ) if _params else "—"
                        _reason = (_n.get("reason") or "—").replace("|", "\\|")
                        qmd_lines.append(
                            f"| {_i} | `{_action}` | {_details} | {_reason} |"
                        )
                    qmd_lines.append("")

            qmd_lines += [
                "---",
                "",
                "> Report generated by SPARMVET-VIZ.",
                "> Recipes are in the `recipes/` folder.",
                f"> Manifest SHA256 (YAML file): {manifest_sha or 'n/a'}",
                f"> Data SHA256 (raw source files): {data_sha or 'n/a'}",
                f"> Recipe hash (wrangling recipe): see `sparmvet_decision_hash` in each Parquet metadata block.",
            ]

            qmd_source = "\n".join(qmd_lines)
            zf.writestr(f"{bundle_dir}/report.qmd", qmd_source)

            # ── Render report with Quarto ─────────────────────────────────
            import subprocess as _sp
            out_ext = {"html": "html", "pdf": "pdf", "docx": "docx"}.get(report_fmt, "html")
            rendered_report_bytes = None
            render_stderr = ""
            with tempfile.TemporaryDirectory() as report_tmp:
                report_tmp_path = Path(report_tmp)
                qmd_tmp = report_tmp_path / "report.qmd"
                qmd_tmp.write_text(qmd_source, encoding="utf-8")
                # Write Quarto-compatible plot copies to _render/ inside the temp dir.
                # _render/ is separate from the user-facing plots/ in the zip so
                # format conversions (e.g. SVG→PNG for PDF output) stay internal.
                render_tmp = report_tmp_path / "_render"
                render_tmp.mkdir()
                for p_id, raw in qmd_plot_bytes.items():
                    (render_tmp / f"{p_id}.{qmd_plot_fmt}").write_bytes(raw)
                try:
                    result = _sp.run(
                        ["quarto", "render", str(qmd_tmp),
                         "--to", out_ext,
                         "--output", f"report.{out_ext}"],
                        capture_output=True, text=True, timeout=120,
                        cwd=str(report_tmp_path),
                    )
                    render_stderr = result.stderr or ""
                    candidate = report_tmp_path / f"report.{out_ext}"
                    if candidate.exists():
                        rendered_report_bytes = candidate.read_bytes()
                except Exception as exc:
                    render_stderr = str(exc)

            if rendered_report_bytes:
                zf.writestr(f"{bundle_dir}/report.{out_ext}", rendered_report_bytes)
            else:
                zf.writestr(
                    f"{bundle_dir}/report_RENDER_FAILED.txt",
                    f"Quarto could not render report.{out_ext}.\n\n"
                    f"stderr:\n{render_stderr}\n\n"
                    "The report.qmd source is still included — run:\n"
                    f"  quarto render report.qmd --to {out_ext}\n",
                )

            # ── README.txt ────────────────────────────────────────────────
            rendered_note = (
                f"  report.{out_ext} — rendered report ({out_ext.upper()})"
                if rendered_report_bytes
                else "  (report rendering failed — see report_RENDER_FAILED.txt)"
            )
            # Dataset → plots mapping block for README
            mapping_block = ["Dataset → Plots", "-" * 20]
            for ds_key, safe_ds, plot_list in mapping_rows:
                mapping_block.append(f"  {ds_key}/")
                tier_files = ["T1_data.tsv"] \
                    + (["T2_data.tsv"] if ds_key in exported_datasets else []) \
                    + (["T3_data.tsv"] if export_t3 else [])
                mapping_block.append(f"    data : {', '.join(tier_files)}")
                mapping_block.append(f"    plots: {', '.join(plot_list)}")

            readme_lines = [
                "SPARMVET-VIZ Export Bundle",
                "=" * 40,
                f"Timestamp        : {now.isoformat()}",
                f"Project          : {proj_id}",
                f"User             : {safe_name}",
                f"Persona          : {persona}",
                f"Preset           : {preset} (DPI={dpi})",
                f"Plots            : {len(all_plots)}",
                f"Tiers            : {', '.join(tiers_exported)}",
                f"Filters          : {len(active_filters)} active",
                "",
                "Reproducibility",
                "-" * 40,
                f"Manifest SHA256  : {manifest_sha or 'n/a'}",
                f"  (SHA256 of manifest YAML file bytes)",
                f"Data SHA256      : {data_sha or 'n/a'}",
                f"  (SHA256 of all raw source file bytes, sorted by dataset id)",
                f"Recipe hash      : see Parquet metadata key 'sparmvet_decision_hash'",
                f"  (SHA256 of wrangling recipe dict — one per T1/T2 Parquet file)",
                "",
                *mapping_block,
                "",
                "Contents:",
                "  <dataset>/plots/  — rendered figures, grouped by source dataset",
                "  <dataset>/T1_data.tsv — raw assembled data (T1)",
                "  <dataset>/T2_data.tsv — processed data (T2, when steps defined)",
                "  <dataset>/T3_data.tsv — analyst-filtered data (T3, when active)",
                "  recipes/          — YAML wrangling recipes",
                "  report.qmd        — Quarto source (re-render: quarto render report.qmd)",
                rendered_note,
                "  FILTERS.txt       — filter trace (if filters were active)",
                "  README.txt        — this file",
                "",
                "IMPORTANT — keep the folder structure intact.",
                "  The report contains relative links to the dataset subfolders.",
                "  Always share or archive the full export folder.",
                "",
                "About data tiers:",
                "  T1 = raw assembled data, unchanged from the pipeline output.",
                "  T2 = T1 with pipeline processing steps applied (range filters,",
                "       derived columns, etc.). Exported when T2 steps are defined.",
                "  T3 = analyst-filtered subset (rows/columns removed before export).",
                "       Included as a separate file when active.",
            ]
            zf.writestr(f"{bundle_dir}/README.txt", "\n".join(readme_lines))

        buf.seek(0)
        yield buf.read()

    def _export_bundle_filename() -> str:
        """Generate timestamped zip filename for the export bundle."""
        import datetime, re
        now = datetime.datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        raw_name = safe_input(input, "export_user_name", "user").strip() or "user"
        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", raw_name)[:40]
        return f"{ts}_{safe_name}_results.zip"
