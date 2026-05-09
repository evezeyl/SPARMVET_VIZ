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
# consumes: app/modules/exporter.py, app/modules/session_manager.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py, polars, shiny
# consumed_by: app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/design/export_specification.md
# @end_deps

from pathlib import Path

import polars as pl
from shiny import reactive, render, ui

from app.modules.t3_recipe_engine import _op_label


# ---------------------------------------------------------------------------
# Module-level provenance helpers (headless-safe — no Shiny imports)
# ---------------------------------------------------------------------------

def build_export_provenance(
    *,
    now,
    proj_id: str,
    safe_name: str,
    persona: str,
    preset: str,
    dpi: int,
    plot_width: float = 8.0,
    plot_height: float = 5.0,
    active_tier: str,
    scope_label: str,
    all_plots: list,
    tiers_exported: list,
    active_filters: list,
    manifest_sha: str,
    data_sha: str,
    bootloader,
    orchestrator=None,
    anchor_dir=None,
) -> dict:
    """Collect all export provenance fields for README, QMD, and image metadata.

    ADR-069: all 8 required provenance fields + git info + software versions.
    Headless-safe: takes plain Python objects, no Shiny imports.
    """
    import subprocess as _sp
    import sys

    # Git info (EXPORT-VERSION-1)
    git_commit = "n/a"
    release_version = "n/a"
    try:
        git_commit = _sp.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=_sp.DEVNULL, text=True,
        ).strip()
    except Exception:
        pass
    try:
        release_version = _sp.check_output(
            ["git", "describe", "--tags", "--always"],
            stderr=_sp.DEVNULL, text=True,
        ).strip()
    except Exception:
        pass

    # Software versions (EXPORT-AUDIT-COMPLETE-1)
    sw_versions: dict[str, str] = {"python": sys.version.split()[0]}
    for _pkg in ("polars", "shiny", "plotnine"):
        try:
            _mod = __import__(_pkg)
            sw_versions[_pkg] = getattr(_mod, "__version__", "unknown")
        except Exception:
            pass

    # Manifest info (EXPORT-AUDIT-COMPLETE-1)
    manifest_path_str = "n/a"
    manifest_name = "n/a"
    try:
        _mp = bootloader.available_projects.get(proj_id)
        if _mp:
            manifest_path_str = str(_mp)
            manifest_name = Path(str(_mp)).stem
    except Exception:
        pass

    # Data source paths (EXPORT-AUDIT-COMPLETE-1)
    data_source_paths: dict[str, str] = {}
    if orchestrator is not None:
        try:
            _src = orchestrator.get_source_files(proj_id)
            data_source_paths = {k: str(v) for k, v in (_src or {}).items()}
        except Exception:
            pass

    # Decision hashes per dataset from Parquet metadata (EXPORT-HASH-2)
    decision_hashes: dict[str, str] = {}
    if anchor_dir is not None:
        try:
            from utils.hashing import get_parquet_metadata_hash
            _seen: set[str] = set()
            for _pid, _spec in all_plots:
                _ds = _spec.get("target_dataset")
                if _ds and _ds not in _seen:
                    _seen.add(_ds)
                    _pq = Path(str(anchor_dir)) / f"{_ds}.parquet"
                    if _pq.exists():
                        _h = get_parquet_metadata_hash(str(_pq))
                        if _h:
                            decision_hashes[_ds] = _h
        except Exception:
            pass

    return {
        "created_at": now.isoformat(),
        "project_id": proj_id,
        "manifest_name": manifest_name,
        "manifest_path": manifest_path_str,
        "persona_id": persona,
        "active_tier": active_tier,
        "export_scope": scope_label,
        "bundle_label": safe_name,
        "preset": preset,
        "dpi": dpi,
        "plot_width": plot_width,
        "plot_height": plot_height,
        "plot_count": len(all_plots),
        "filter_count": len(active_filters),
        "tiers_exported": tiers_exported,
        "manifest_sha256": manifest_sha,
        "data_batch_hash": data_sha,
        "decision_hashes": decision_hashes,
        "git_commit": git_commit,
        "release_version": release_version,
        "software_versions": sw_versions,
        "data_source_paths": data_source_paths,
    }


def _embed_png_provenance(
    png_bytes: bytes, prov: dict, plot_id: str, dataset_key: str = ""
) -> bytes:
    """Embed provenance as iTXt chunks in PNG bytes (EXPORT-IMG-META-1)."""
    try:
        from PIL import Image, PngImagePlugin
        import io as _io
        img = Image.open(_io.BytesIO(png_bytes))
        info = PngImagePlugin.PngInfo()
        fields = {
            "sparmvet:plot_id": plot_id,
            "sparmvet:project_id": prov.get("project_id", ""),
            "sparmvet:persona_id": prov.get("persona_id", ""),
            "sparmvet:manifest_sha256": prov.get("manifest_sha256", ""),
            "sparmvet:data_batch_hash": prov.get("data_batch_hash", ""),
            "sparmvet:decision_hash": prov.get("decision_hashes", {}).get(dataset_key, ""),
            "sparmvet:git_commit": prov.get("git_commit", ""),
            "sparmvet:created_at": prov.get("created_at", ""),
        }
        for k, v in fields.items():
            if v:
                info.add_itxt(k, v)
        out = _io.BytesIO()
        img.save(out, format="PNG", pnginfo=info)
        return out.getvalue()
    except Exception:
        return png_bytes


def _embed_svg_provenance(
    svg_bytes: bytes, prov: dict, plot_id: str, dataset_key: str = ""
) -> bytes:
    """Embed provenance as SVG <metadata> XML block (EXPORT-IMG-META-1)."""
    try:
        import xml.etree.ElementTree as _ET
        _ET.register_namespace("", "http://www.w3.org/2000/svg")
        root = _ET.fromstring(svg_bytes)
        meta_el = _ET.SubElement(root, "metadata")
        meta_el.text = "\n".join([
            f"sparmvet:plot_id={plot_id}",
            f"sparmvet:project_id={prov.get('project_id', '')}",
            f"sparmvet:persona_id={prov.get('persona_id', '')}",
            f"sparmvet:manifest_sha256={prov.get('manifest_sha256', '')}",
            f"sparmvet:data_batch_hash={prov.get('data_batch_hash', '')}",
            f"sparmvet:decision_hash={prov.get('decision_hashes', {}).get(dataset_key, '')}",
            f"sparmvet:git_commit={prov.get('git_commit', '')}",
            f"sparmvet:created_at={prov.get('created_at', '')}",
        ])
        return _ET.tostring(root, encoding="unicode").encode("utf-8")
    except Exception:
        return svg_bytes


def _build_methods_section(
    all_plots: list,
    t3_by_plot: dict,
    active_filters: list,
    ds_to_plots: dict,
    tiers_exported: list,
) -> list[str]:
    """Return QMD lines for the auto-generated Methods section.

    Produces human-readable prose from T3 audit nodes and applied filters.
    Returns an empty list when nothing actionable exists so the section is
    omitted rather than appearing empty.
    """
    _op_prose = {
        "eq": "equal to", "ne": "not equal to",
        "gt": "greater than", "ge": "at least",
        "lt": "less than", "le": "at most",
        "in": "one of", "not_in": "not one of",
    }
    _node_verb = {
        "filter_row": "Rows were filtered",
        "exclusion_row": "Rows were explicitly excluded",
        "drop_column": "Column was permanently removed",
        "aesthetic_override": "Plot aesthetics were adjusted",
        "developer_raw_yaml": "A custom manifest fragment was applied",
    }

    prose_items: list[str] = []

    # Filter prose
    for f in active_filters:
        col = f.get("column", "?")
        op = _op_prose.get(f.get("op", "eq"), f.get("op", "eq"))
        val = f.get("value", "")
        val_str = (
            ", ".join(f'"{v}"' for v in val) if isinstance(val, list)
            else f'"{val}"'
        )
        prose_items.append(
            f'Rows were retained where **{col}** is {op} {val_str}.'
        )

    # T3 node prose
    for p_id, nodes in (t3_by_plot or {}).items():
        plot_label = next(
            (s.get("title") or p_id.replace("_", " ").title()
             for pid, s in all_plots if pid == p_id),
            p_id.replace("_", " ").title(),
        )
        for n in nodes:
            nt = n.get("node_type", "")
            params = n.get("params", {})
            reason = n.get("reason", "").strip()
            verb = _node_verb.get(nt, "An adjustment was applied")

            if nt in ("filter_row", "exclusion_row"):
                col = params.get("column", "?")
                op = _op_prose.get(params.get("op", "eq"), params.get("op", ""))
                val = params.get("value", "")
                val_str = (
                    ", ".join(f'"{v}"' for v in val) if isinstance(val, list)
                    else f'"{val}"'
                )
                detail = f"where **{col}** is {op} {val_str}"
                scope = f" (plot: *{plot_label}*)" if p_id != "__all__" else ""
                sentence = f"{verb} {detail}{scope}."
            elif nt == "drop_column":
                col = params.get("column", "?")
                scope = f" (plot: *{plot_label}*)" if p_id != "__all__" else ""
                sentence = f"Column **{col}** was permanently removed from the exported data{scope}."
            elif nt == "aesthetic_override":
                scope = f" for plot *{plot_label}*"
                sentence = f"Plot aesthetics were adjusted{scope}."
            else:
                scope = f" (plot: *{plot_label}*)" if p_id != "__all__" else ""
                sentence = f"{verb}{scope}."

            if reason:
                sentence += f" *Reason: {reason}*"
            prose_items.append(sentence)

    if not prose_items:
        return []

    lines = ["## Methods", ""]
    lines.append(
        "The following data preparation and analyst adjustments were applied "
        "prior to export:"
    )
    lines.append("")
    for item in prose_items:
        lines.append(f"- {item}")
    lines.append("")
    return lines


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
    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    @output
    @render.ui
    def system_tools_ui():
        if not bootloader.is_enabled("export_enabled"):
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
        if bootloader.is_enabled("export_enabled") and active_home_subtab is not None:
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

            t3_checkbox = ui.div()
            if bootloader.is_enabled("t3_sandbox_enabled"):
                t3_active = tier_toggle.get() == "T3"
                t3_checkbox = ui.div(
                    ui.input_checkbox(
                        "export_include_t3",
                        "Include T3 filtered data",
                        value=t3_active,
                    ),
                    ui.tags.small(
                        "Only available when T3 has committed nodes.",
                        class_="text-muted d-block",
                        style="font-size:0.7em; margin-top:-4px;",
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
                t3_checkbox,
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
                ui.div(
                    ui.tags.label("Plot size (inches)", class_="d-block mb-1"),
                    ui.div(
                        ui.input_numeric("export_plot_width",  "W", value=8,  min=2, max=30, step=0.5),
                        ui.input_numeric("export_plot_height", "H", value=5,  min=2, max=30, step=0.5),
                        class_="d-flex gap-2",
                    ),
                    class_="mb-1",
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
        plot_width  = float(safe_input(input, "export_plot_width",  8))
        plot_height = float(safe_input(input, "export_plot_height", 5))
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

            # ── Hashes + Provenance (before tmpdir so image embedding can use it) ──
            import hashlib as _hashlib
            manifest_sha = ""
            data_sha = ""
            try:
                _proj_mnf = bootloader.available_projects.get(proj_id)
                if _proj_mnf:
                    manifest_sha = _hashlib.sha256(
                        Path(str(_proj_mnf)).read_bytes()
                    ).hexdigest()
            except Exception:
                pass
            if home_state is not None:
                try:
                    data_sha = home_state.get().get("data_batch_hash") or ""
                except Exception:
                    pass
            if not data_sha:
                try:
                    _al = tier1_anchor()
                    _da = _al.collect()
                    _fp = f"{_da.columns}|{_da.shape}|{_da.head(500).write_csv()}"
                    data_sha = _hashlib.sha256(_fp.encode()).hexdigest()
                except Exception:
                    pass

            is_advanced = bootloader.is_enabled("t3_sandbox_enabled")
            active_tier = tier_toggle.get()
            # Respect explicit user checkbox; fall back to auto-detect when input absent
            # (e.g. personas without t3_sandbox_enabled never render the checkbox).
            include_t3_checked = safe_input(input, "export_include_t3", None)
            if include_t3_checked is None:
                export_t3 = is_advanced and active_tier == "T3"
            else:
                export_t3 = is_advanced and bool(include_t3_checked)
            tiers_exported = ["T1"] + (["T3"] if export_t3 else [])
            anchor_dir = bootloader.get_location("user_sessions") / "anchors"

            prov = build_export_provenance(
                now=now,
                proj_id=proj_id,
                safe_name=safe_name,
                persona=persona,
                preset=preset,
                dpi=dpi,
                plot_width=plot_width,
                plot_height=plot_height,
                active_tier=active_tier,
                scope_label=scope_label,
                all_plots=all_plots,
                tiers_exported=tiers_exported,
                active_filters=active_filters,
                manifest_sha=manifest_sha,
                data_sha=data_sha,
                bootloader=bootloader,
                orchestrator=orchestrator,
                anchor_dir=anchor_dir,
            )

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
                                 format=plot_fmt, dpi=dpi,
                                 width=plot_width, height=plot_height)

                        with open(plot_path, "rb") as f:
                            raw = f.read()
                        # EXPORT-IMG-META-1: embed provenance in image bytes
                        if plot_fmt == "png":
                            raw = _embed_png_provenance(raw, prov, p_id, _ds_key)
                        elif plot_fmt == "svg":
                            raw = _embed_svg_provenance(raw, prov, p_id, _ds_key)
                        plot_bytes[p_id] = raw
                        zf.writestr(f"{bundle_dir}/{_safe_ds}/plots/{p_id}.{plot_fmt}", raw)

                        # When SVG plots + PDF report: also render PNG for Quarto
                        # (LuaLaTeX cannot embed SVGs without rsvg-convert)
                        if qmd_plot_fmt != plot_fmt:
                            qmd_path = tmpdir_path / f"{p_id}.{qmd_plot_fmt}"
                            fig.save(str(qmd_path), verbose=False,
                                     format=qmd_plot_fmt, dpi=dpi,
                                     width=plot_width, height=plot_height)
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
                # is_advanced / active_tier / export_t3 already computed before tmpdir block.

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

            # manifest_sha, data_sha, tiers_exported, prov — all computed before tmpdir block.

            # ── Lineage graph (ADR-074) ───────────────────────────────────
            # Shared-node DAG: one lineage_graph.json per export scope.
            # Nodes are deduplicated by schema_id+type so datasets shared
            # across multiple plots appear only once.
            _lineage_nodes: dict[str, dict] = {}
            _lineage_edges: set[tuple[str, str]] = set()
            _lineage_per_plot: dict[str, list[str]] = {}
            _lineage_ok = False
            try:
                from blueprint_arch.manifest_navigator import (
                    build_plot_lineage as _bpl,
                )
                _mnf_path_obj = bootloader.available_projects.get(proj_id)
                if _mnf_path_obj:
                    _mnf_str = str(_mnf_path_obj)
                    for _pid, _pspec in all_plots:
                        _steps = _bpl(_pid, _mnf_str)
                        if not _steps:
                            continue
                        _plot_nids: list[str] = []
                        for _s in _steps:
                            _nid = f"{_s['schema_id']}__{_s['type']}"
                            if _nid not in _lineage_nodes:
                                _lineage_nodes[_nid] = {
                                    "id": _nid,
                                    "type": _s["type"],
                                    "schema_id": _s["schema_id"],
                                    "label": _s["label"],
                                    "rel": _s.get("rel", ""),
                                }
                            _plot_nids.append(_nid)
                        _lineage_per_plot[_pid] = _plot_nids
                        # Derive DAG edges from step sequence.
                        # Gateway = first join node (if present) else plot_spec.
                        # All data_source / wrangling nodes connect into the gateway.
                        _join_s = next(
                            (_s for _s in _steps if _s["type"] == "join"), None
                        )
                        _plot_s = next(
                            (_s for _s in _steps if _s["type"] == "plot_spec"), None
                        )
                        _gw = _join_s or _plot_s
                        _ei = 0
                        while _ei < len(_steps):
                            _es = _steps[_ei]
                            _en = f"{_es['schema_id']}__{_es['type']}"
                            if _es["type"] == "data_source":
                                _nxt = _steps[_ei + 1] if _ei + 1 < len(_steps) else None
                                if (
                                    _nxt
                                    and _nxt["type"] == "wrangling"
                                    and _nxt["schema_id"] == _es["schema_id"]
                                ):
                                    _wn = f"{_nxt['schema_id']}__{_nxt['type']}"
                                    _lineage_edges.add((_en, _wn))
                                    if _gw:
                                        _gwn = f"{_gw['schema_id']}__{_gw['type']}"
                                        if _wn != _gwn:
                                            _lineage_edges.add((_wn, _gwn))
                                    _ei += 2
                                else:
                                    if _gw:
                                        _gwn = f"{_gw['schema_id']}__{_gw['type']}"
                                        if _en != _gwn:
                                            _lineage_edges.add((_en, _gwn))
                                    _ei += 1
                            elif _es["type"] == "join" and _plot_s:
                                _lineage_edges.add(
                                    (_en, f"{_plot_s['schema_id']}__{_plot_s['type']}")
                                )
                                _ei += 1
                            else:
                                _ei += 1

                    if _lineage_nodes:
                        import json as _json
                        _graph_payload = {
                            "generated": now.isoformat(),
                            "export_scope": scope_label,
                            "nodes": list(_lineage_nodes.values()),
                            "edges": [
                                {"from": _f, "to": _t}
                                for _f, _t in sorted(_lineage_edges)
                            ],
                            "plot_ids": [_p for _p, _ in all_plots],
                            "lineage_per_plot": _lineage_per_plot,
                            "description": (
                                "Shared-node directed acyclic graph (DAG) of the data "
                                "lineage for this export scope. "
                                "Nodes are deduplicated by schema_id+type — a dataset "
                                "shared by multiple plots appears only once. "
                                "Edge direction: upstream → downstream "
                                "(data_source → wrangling → join → plot_spec)."
                            ),
                        }
                        zf.writestr(
                            f"{bundle_dir}/lineage/lineage_graph.json",
                            _json.dumps(_graph_payload, indent=2),
                        )
                        _lineage_ok = True
            except Exception as _le:
                zf.writestr(
                    f"{bundle_dir}/lineage/lineage_graph_ERROR.txt",
                    f"Lineage graph generation failed:\n{_le}",
                )

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
                '    toc: true',
                '    toc-depth: 3',
                '    toc-title: "Contents"',
                '    number-sections: true',
                '    theme: cosmo',
                '    fontsize: 11pt',
                '  pdf:',
                '    documentclass: article',
                '    toc: true',
                '    number-sections: true',
                '    fontsize: 11pt',
                '  docx:',
                '    toc: true',
                '    number-sections: true',
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

            # Decision hash rows for QMD provenance table
            _prov_dh = prov.get("decision_hashes", {})
            _dh_qmd_rows = []
            if _prov_dh:
                for _ds_k, _ds_h in _prov_dh.items():
                    _dh_qmd_rows.append(
                        f"| Decision hash ({_ds_k}) | `{_ds_h}` | "
                        f"SHA256 of wrangling recipe for `{_ds_k}` — read from Parquet metadata key `sparmvet_decision_hash` |"
                    )
            else:
                _dh_qmd_rows.append(
                    "| Decision hash | see Parquet metadata | "
                    "SHA256 of wrangling recipe dict — one per T1/T2 Parquet file |"
                )
            # Software version row
            _sw_qmd = prov.get("software_versions", {})
            _sw_qmd_str = "; ".join(f"{k}={v}" for k, v in _sw_qmd.items()) if _sw_qmd else "n/a"

            qmd_lines += [
                "## Provenance",
                "",
                f"**Git commit:** `{prov['git_commit']}`  ",
                f"**Release:** `{prov['release_version']}`  ",
                f"**Software:** {_sw_qmd_str}  ",
                f"**Manifest:** `{prov['manifest_name']}` — `{prov['manifest_path']}`  ",
                "",
                "| Hash | Value | Meaning |",
                "|------|-------|---------|",
                f"| Manifest SHA256 | `{prov['manifest_sha256'] or 'n/a'}` | SHA256 of manifest YAML file bytes |",
                f"| Data batch hash | `{prov['data_batch_hash'] or 'n/a'}` | SHA256 of all raw source file bytes (sorted by dataset id) |",
                *_dh_qmd_rows,
                "",
                "> These hashes allow independent verification that this report was generated",
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

            # ── Methods section (auto-generated from T3 nodes + filters) ───
            _methods_lines = _build_methods_section(
                all_plots=all_plots,
                t3_by_plot=_t3_by_plot,
                active_filters=active_filters,
                ds_to_plots=ds_to_plots,
                tiers_exported=tiers_exported,
            )
            qmd_lines += _methods_lines

            # QMD image paths point to _render/ (Quarto-compatible copies).
            # _render/ is written into the Quarto temp dir alongside report.qmd.
            # The user-facing plots/ folder in the zip keeps the chosen format.
            qmd_lines += ["## Plots", ""]
            for p_id, spec in all_plots:
                label = spec.get("title") or p_id.replace("_", " ").title()
                ds_note = spec.get("target_dataset") or "—"
                fig_id = f"fig-{_re.sub(r'[^A-Za-z0-9]', '-', p_id)}"
                caption = f"{label} — dataset: `{ds_note}`"
                qmd_lines += [
                    f"### {label}",
                    "",
                    f"![{caption}](_render/{p_id}.{plot_ext}){{#{fig_id} width=95%}}",
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

            # ── Data Lineage section ──────────────────────────────────────
            if _lineage_ok and _lineage_nodes:
                qmd_lines += ["## Data Lineage", ""]
                # Mermaid flowchart — cylinder=source, rounded=wrangling,
                # rhombus=join, rectangle=plot.
                _mmd_shapes = {
                    "data_source": ('[("', '")]'),
                    "wrangling": ('("', '")'),
                    "join": ('{"', '"}'),
                    "plot_spec": ('["', '"]'),
                }
                _mmd_type_labels = {
                    "data_source": "source",
                    "wrangling": "wrangling",
                    "join": "join",
                    "plot_spec": "plot",
                }

                def _mmd_id(nid: str) -> str:
                    return _re.sub(r"[^A-Za-z0-9_]", "_", nid)

                qmd_lines += ["```{mermaid}", "flowchart LR"]
                for _nid, _nd in _lineage_nodes.items():
                    _t = _nd["type"]
                    _lbl = _nd["label"].replace('"', "'")
                    _tlbl = _mmd_type_labels.get(_t, _t)
                    _open, _close = _mmd_shapes.get(_t, ('["', '"]'))
                    qmd_lines.append(
                        f"    {_mmd_id(_nid)}{_open}{_lbl} / {_tlbl}{_close}"
                    )
                for _ef, _et in sorted(_lineage_edges):
                    qmd_lines.append(f"    {_mmd_id(_ef)} --> {_mmd_id(_et)}")
                qmd_lines += ["```", ""]

                # Step summary table
                _ln_type_order = {
                    "data_source": 0, "wrangling": 1, "join": 2, "plot_spec": 3
                }
                qmd_lines += [
                    "### Lineage Step Summary",
                    "",
                    "| Type | Schema ID | Label | Path |",
                    "|------|-----------|-------|------|",
                ]
                for _nd in sorted(
                    _lineage_nodes.values(),
                    key=lambda x: (_ln_type_order.get(x["type"], 9), x["schema_id"]),
                ):
                    _nd_rel = _nd.get("rel") or "—"
                    qmd_lines.append(
                        f"| `{_nd['type']}` | `{_nd['schema_id']}` "
                        f"| {_nd['label']} | `{_nd_rel}` |"
                    )
                qmd_lines += [
                    "",
                    "> **`lineage/lineage_graph.json`** contains the full machine-readable DAG.",
                    "> Nodes are deduplicated — a dataset shared by multiple plots appears only once.",
                    "> Edge direction: upstream → downstream (source → wrangling → join → plot).",
                    "",
                ]

            qmd_lines += [
                "---",
                "",
                "> Report generated by SPARMVET-VIZ.",
                f"> Git commit: `{prov['git_commit']}` | Release: `{prov['release_version']}`",
                "> Recipes are in the `recipes/` folder.",
                f"> Manifest SHA256 (YAML file): {prov['manifest_sha256'] or 'n/a'}",
                f"> Data batch hash (raw source files): {prov['data_batch_hash'] or 'n/a'}",
                "> Decision hashes (wrangling recipe): see `sparmvet_decision_hash` in each Parquet metadata block.",
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

            # Decision hashes block for README
            _dh = prov.get("decision_hashes", {})
            _dsp = prov.get("data_source_paths", {})
            _sw = prov.get("software_versions", {})
            _sw_str = ", ".join(f"{k}={v}" for k, v in _sw.items()) if _sw else "n/a"
            _dh_lines = []
            if _dh:
                for _ds_k, _ds_h in _dh.items():
                    _dh_lines.append(f"  {_ds_k}: {_ds_h}")
            else:
                _dh_lines.append("  n/a (see Parquet metadata key 'sparmvet_decision_hash')")
            _dsp_lines = []
            for _ds_k, _ds_p in _dsp.items():
                _dsp_lines.append(f"  {_ds_k}: {_ds_p}")

            readme_lines = [
                "SPARMVET-VIZ Export Bundle",
                "=" * 40,
                f"Timestamp        : {prov['created_at']}",
                f"Project          : {prov['project_id']}",
                f"Manifest name    : {prov['manifest_name']}",
                f"Manifest path    : {prov['manifest_path']}",
                f"User             : {prov['bundle_label']}",
                f"Persona          : {prov['persona_id']}",
                f"Preset           : {prov['preset']} (DPI={prov['dpi']}, {prov['plot_width']}×{prov['plot_height']} in)",
                f"Active tier      : {prov['active_tier']}",
                f"Export scope     : {prov['export_scope']}",
                f"Plots            : {prov['plot_count']}",
                f"Tiers            : {', '.join(prov['tiers_exported'])}",
                f"Filters          : {prov['filter_count']} active",
                "",
                "Software",
                "-" * 40,
                f"Versions         : {_sw_str}",
                f"Git commit       : {prov['git_commit']}",
                f"Release version  : {prov['release_version']}",
                "",
                "Reproducibility",
                "-" * 40,
                f"Manifest SHA256  : {prov['manifest_sha256'] or 'n/a'}",
                f"  (SHA256 of manifest YAML file bytes)",
                f"Data batch hash  : {prov['data_batch_hash'] or 'n/a'}",
                f"  (SHA256 of all raw source file bytes, sorted by dataset id)",
                "Decision hashes (per dataset):",
                *_dh_lines,
                "",
                "Data source paths:",
                *(_dsp_lines if _dsp_lines else ["  n/a"]),
                "",
                *mapping_block,
                "",
                "Contents:",
                "  <dataset>/plots/  — rendered figures, grouped by source dataset",
                "  <dataset>/T1_data.tsv — raw assembled data (T1)",
                "  <dataset>/T2_data.tsv — processed data (T2, when steps defined)",
                "  <dataset>/T3_data.tsv — analyst-filtered data (T3, when active)",
                "  recipes/          — YAML wrangling recipes",
                "  lineage/          — lineage_graph.json (shared-node DAG, ADR-074)",
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
