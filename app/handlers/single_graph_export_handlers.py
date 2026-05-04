"""app/handlers/single_graph_export_handlers.py
Single Graph Export panel — exports the active plot as a .zip bundle.

New in Phase 25-H (ADR-052). Reuses helpers from home_theater.define_server()
(passed in as closures) so the export sees the same plot spec, T3 stack and
filter pipeline that the on-screen render sees.

Bundle contents
---------------
- plot.<png|svg|pdf>          — rendered figure for the active plot
- data.tsv                    — T1 + applied filters + T3 stack data slice
- manifest_fragment.yaml      — the active plot's spec section
- t3_recipe.json              — committed T3 RecipeNodes for this plot
- README.txt                  — bundle metadata

Two-Category Law (ADR-045): this module contains @render.* / @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_single_graph_export_server, output:single_graph_export_ui, output:export_single_graph
# consumes: app/src/bootloader.py, libs/viz_factory/src/viz_factory/viz_factory.py, polars, shiny
# consumed_by: app/handlers/home_theater.py
# doc: .antigravity/knowledge/architecture_decisions.md#ADR-045, .antigravity/knowledge/architecture_decisions.md#ADR-052
# @end_deps

import copy
from pathlib import Path

from shiny import render, ui

from app.src.bootloader import bootloader


def define_single_graph_export_server(input, output, session, *,
                                      viz_factory, active_cfg, active_home_subtab,
                                      applied_filters, home_state, safe_input,
                                      _resolve_active_spec, _resolve_active_lf,
                                      _resolve_t1_lf,
                                      _t3_filter_rows, _t3_drop_columns,
                                      _active_plot_t3_nodes,
                                      notification_log=None):
    """Register the Single Graph Export panel + download handler.

    All reactive helpers are passed as closures from home_theater.define_server
    so this module sees the same view of the active plot's spec, data, and T3
    stack that the on-screen render uses.
    """
    from app.handlers.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    @output
    @render.ui
    def single_graph_export_ui():
        if not bootloader.is_enabled("export_graph_enabled"):
            return ui.div()

        subtab = active_home_subtab.get()
        active_label = subtab.removeprefix("subtab_") if subtab else "(none)"

        return ui.div(
            ui.tags.small(
                f"Active plot: {active_label}",
                class_="text-muted d-block mb-1",
                style="font-size:0.7em;",
            ),
            ui.input_radio_buttons(
                "export_graph_format",
                label="Format",
                choices={"png": "PNG", "svg": "SVG", "pdf": "PDF"},
                selected="png",
                inline=True,
            ),
            ui.download_button(
                "export_single_graph",
                "💾 Export Active Graph",
                class_="btn-outline-success btn-sm w-100 mt-1",
            ),
            class_="mb-2 px-2",
            style="font-size:0.8em;",
        )

    @render.download(filename=lambda: _single_graph_filename())
    async def export_single_graph():
        """Stream a .zip containing: plot, data slice, manifest fragment, T3 stack."""
        import datetime
        import io
        import json
        import tempfile
        import zipfile
        import yaml

        if not bootloader.is_enabled("export_graph_enabled"):
            yield b""
            return

        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        if not p_id:
            _notify(
                "No active plot subtab — open a plot before exporting.",
                type="warning", duration=5,
            )
            yield b""
            return

        spec = _resolve_active_spec(p_id)
        if spec is None:
            _notify(
                f"No spec found for plot '{p_id}'.", type="error", duration=5
            )
            yield b""
            return

        fmt = safe_input(input, "export_graph_format", "png")
        now = datetime.datetime.now()
        plot_spec = copy.deepcopy(spec)

        cfg = active_cfg()
        synthetic_manifest = {
            "plots": {p_id: plot_spec},
            "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
        }

        # Build tier LazyFrames:
        #  lf_t1 — raw T1 (parquet scan / materialize, no tier2 applied)
        #  lf_t2 — T1 + tier2 steps (None if no tier2 recipe steps exist)
        #  lf    — active tier + T3 drops (what the rendered plot uses)
        try:
            from transformer.data_wrangler import DataWrangler as _DW
            lf_t1 = _resolve_t1_lf(spec)
            target_ds = (spec or {}).get("target_dataset", "")
            recipe_raw = (
                active_cfg().raw_config
                .get("join_manifests", {})
                .get(target_ds, {})
                .get("recipe", [])
            )
            t2_steps = _DW._resolve_tier(recipe_raw, "tier2")
            lf_t2 = _DW(data_schema={}).run(lf_t1, t2_steps) if t2_steps else None
            lf_active = lf_t2 if lf_t2 is not None else lf_t1
            t3_nodes = _active_plot_t3_nodes(subtab) if home_state is not None else []
            has_t3 = bool(t3_nodes)
            t3_drops = [c for c in _t3_drop_columns(subtab) if c in lf_active.collect_schema().names()]
            lf = lf_active.drop(t3_drops) if t3_drops else lf_active
        except Exception as e:
            _notify(f"❌ Data error: {e}", type="error", duration=8)
            yield b""
            return

        import hashlib
        import re as _re
        safe_pid = _re.sub(r"[^A-Za-z0-9_-]", "_", p_id)[:40]

        # Read reproducibility hashes from home_state (same values as session key)
        _hs = home_state.get() if home_state is not None else {}
        _manifest_sha256 = _hs.get("manifest_sha256") or ""
        _data_batch_hash = _hs.get("data_batch_hash") or ""

        buf = io.BytesIO()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                # 1. Plot — rendered from active tier + T3
                try:
                    fig = viz_factory.render(lf, synthetic_manifest, p_id)
                    plot_path = tmp / f"{safe_pid}.{fmt}"
                    if fmt == "png":
                        fig.save(str(plot_path), dpi=300, verbose=False)
                    else:
                        fig.save(str(plot_path), format=fmt, verbose=False)
                    zf.write(plot_path, arcname=plot_path.name)
                except Exception as e:
                    zf.writestr("plot_ERROR.txt", f"Plot render failed:\n{e}")

                # 2. Data by tier
                data_hash = ""
                # T1 — always
                try:
                    df_t1 = lf_t1.collect()
                    p = tmp / f"{safe_pid}_T1_data.tsv"
                    df_t1.write_csv(str(p), separator="\t")
                    zf.write(p, arcname=p.name)
                    data_hash = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                except Exception as e:
                    zf.writestr("T1_data_ERROR.txt", f"T1 data export failed:\n{e}")
                # T2 — only when tier2 recipe steps exist
                if lf_t2 is not None:
                    try:
                        df_t2 = lf_t2.collect()
                        p = tmp / f"{safe_pid}_T2_data.tsv"
                        df_t2.write_csv(str(p), separator="\t")
                        zf.write(p, arcname=p.name)
                    except Exception as e:
                        zf.writestr("T2_data_ERROR.txt", f"T2 data export failed:\n{e}")
                # T3 — only when nodes are committed
                if has_t3:
                    try:
                        df_t3 = lf.collect()
                        p = tmp / f"{safe_pid}_T3_data.tsv"
                        df_t3.write_csv(str(p), separator="\t")
                        zf.write(p, arcname=p.name)
                    except Exception as e:
                        zf.writestr("T3_data_ERROR.txt", f"T3 data export failed:\n{e}")

                # 3. Manifest fragment — plot spec only (kept for backwards compat)
                manifest_bytes = yaml.safe_dump(
                    {"plots": {p_id: spec}}, sort_keys=False
                ).encode()
                zf.writestr("manifest_fragment.yaml", manifest_bytes.decode())

                # 4. T3 nodes committed for this plot (already computed above as t3_nodes)
                zf.writestr("t3_recipe.json", json.dumps(t3_nodes, indent=2))

                # 5. Full lineage recipe — T1/T2 assembly + T3 nodes + plot spec (EXPORT-SGE-2)
                raw = cfg.raw_config
                full_recipe = {
                    "plot_id": p_id,
                    "target_dataset": target_ds,
                    "data_schema": raw.get("data_schemas", {}).get(target_ds, {}),
                    "join": raw.get("join_manifests", {}).get(target_ds, {}),
                    "t3_nodes": t3_nodes,
                    "plot_spec": spec,
                }
                zf.writestr("full_recipe.yaml", yaml.safe_dump(full_recipe, sort_keys=False))

                # 6. README
                proj_id = safe_input(input, "project_id", "")
                data_files = [f"  {safe_pid}_T1_data.tsv     — T1 assembled data"]
                if lf_t2 is not None:
                    data_files.append(f"  {safe_pid}_T2_data.tsv     — T2 transformed data")
                if has_t3:
                    data_files.append(f"  {safe_pid}_T3_data.tsv     — T3 data (filters + drops applied)")
                readme = [
                    "SPARMVET-VIZ Single Graph Export",
                    "=" * 40,
                    f"Generated      : {now.isoformat()}",
                    f"Project        : {proj_id}",
                    f"Plot           : {p_id}",
                    f"Format         : {fmt}",
                    f"T3 nodes       : {len(t3_nodes)} committed",
                    "",
                    "Reproducibility",
                    "-" * 40,
                    f"Manifest SHA256  : {_manifest_sha256 or 'n/a'}",
                    f"Data SHA256      : {_data_batch_hash or 'n/a'}",
                    f"  (Manifest SHA256 = SHA256 of manifest YAML file bytes)",
                    f"  (Data SHA256     = SHA256 of all raw source file bytes, sorted by dataset id)",
                    f"  (Recipe hash / decision_hash: see Parquet metadata — not yet exported here)",
                    "",
                    "Files",
                    "-" * 40,
                    f"  {safe_pid}.{fmt}              — rendered plot",
                    *data_files,
                    "  full_recipe.yaml              — complete lineage (T1/T2 assembly + T3 nodes + plot spec)",
                    "  manifest_fragment.yaml        — plot spec only (legacy)",
                    "  t3_recipe.json                — committed T3 transformation nodes (also in full_recipe.yaml)",
                ]
                zf.writestr("README.txt", "\n".join(readme))

        yield buf.getvalue()

    def _single_graph_filename() -> str:
        import datetime, re
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        subtab = active_home_subtab.get() or ""
        p_id = subtab.removeprefix("subtab_") or "plot"
        safe_pid = re.sub(r"[^A-Za-z0-9_-]", "_", p_id)[:40]
        return f"{ts}_{safe_pid}_graph.zip"
