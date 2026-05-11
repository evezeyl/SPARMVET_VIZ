"""app/handlers/home_theater.py
Home Theater Shiny wiring (ADR-043 / ADR-044 / ADR-045).

Entry point:
    define_server(input, output, session, *,
                  bootloader, wrangle_studio, dev_studio,
                  orchestrator, viz_factory, gallery_viewer,
                  current_persona, anchor_path, tier1_anchor,
                  tier_reference, tier3_leaf, active_cfg,
                  active_collection_id, safe_input, active_home_subtab, tier_toggle,
                  home_state=None, session_manager=None)

Concern: dynamic_tabs, sidebar_nav_ui, sidebar_tools_ui,
         right_sidebar_content_ui, home_data_preview/col_selector,
         col_drop_audit_btn_ui, plot_reference, table_reference,
         plot_leaf, table_leaf, handle_plot_brush, comparison_mode_toggle_ui.

Sub-handlers (Phase 24, ADR-051) — called from inside define_server():
  app/handlers/session_handlers.py            session management panel
  app/handlers/export_handlers.py             system tools + bundle + audit reports
  app/handlers/filter_and_audit_handlers.py   filter UI + T3 audit + propagation modal
  app/modules/t3_recipe_engine.py             pure helpers (_apply_filter_rows, _op_label)

Two-Category Law (ADR-045): This file contains @render.* and @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (home_theater), output:dynamic_tabs, output:home_data_preview, output:home_col_selector_ui, output:col_drop_audit_btn_ui, output:sidebar_nav_ui, output:sidebar_tools_ui, output:right_sidebar_content_ui, output:plot_reference, output:table_reference, output:plot_leaf, output:table_leaf, output:comparison_mode_toggle_ui, output:plot_cell_{p_id} (per-plot)
# consumes: app/modules/orchestrator.py, app/modules/wrangle_studio.py, app/modules/test_lab_studio.py, app/modules/gallery_viewer.py, libs/viz_factory/src/viz_factory/viz_factory.py, utils/config_loader.py, app/modules/t3_recipe_engine.py, app/modules/sidebar_registry.py, app/handlers/session_handlers.py, app/handlers/export_handlers.py, app/handlers/filter_and_audit_handlers.py, app/handlers/data_import_handlers.py
#              libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-AUDIT-1, via session.on_flushed capture)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-043, .claude/knowledge/architecture_decisions.md#ADR-044, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-047, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-073
# @end_deps

import re
from pathlib import Path

import polars as pl
from transformer.lookup import lookup_anchor_rows
from shiny import reactive, render, ui
from utils.config_loader import ConfigManager

from app.modules.t3_recipe_engine import _apply_filter_rows
from app.modules.sidebar_registry import is_panel_active
from app.handlers.session_handlers import define_session_server
from app.handlers.export_handlers import define_export_server
from app.handlers.filter_and_audit_handlers import define_filter_audit_server
from app.handlers.data_import_handlers import define_data_import_server

# ADR-036: Shiny input IDs must match ^[a-zA-Z0-9_]+$ — no spaces, emoji, or
# punctuation. This sanitiser strips anything outside that set so manifest
# group/plot labels can use any characters (including emoji) without breaking
# the input wiring. Collapses runs of stripped chars into a single underscore,
# trims leading/trailing underscores, lowercases, and falls back to "group" if
# the input was entirely non-id-safe.
_ID_SAFE_RE = re.compile(r"[^a-zA-Z0-9_]+")


def _safe_id(label: str) -> str:
    """Convert any human label into a Shiny-safe input id fragment."""
    if not label:
        return "group"
    out = _ID_SAFE_RE.sub("_", str(label)).strip("_").lower()
    return out or "group"


def _collect_all_group_plot_ids(bootloader) -> list[tuple[str, dict]]:
    """Enumerate all (plot_id, spec_dict) pairs from analysis_groups AND top-level plots.

    Called once at server init to register dynamic @render.plot handlers.
    Returns list of (p_id, spec) tuples (spec may be None for unresolved entries).
    """
    seen = set()
    results = []
    for proj_id, manifest_path in bootloader.available_projects.items():
        try:
            cfg = ConfigManager(str(manifest_path))
            # Collect from analysis_groups
            groups = cfg.raw_config.get("analysis_groups", {})
            for _gid, gspec in groups.items():
                for p_id, plot_entry in gspec.get("plots", {}).items():
                    if p_id not in seen:
                        seen.add(p_id)
                        results.append((p_id, plot_entry.get("spec")))
            # Collect from top-level plots (fallback when no analysis_groups)
            top_plots = cfg.raw_config.get("plots", {})
            for p_id, plot_spec in top_plots.items():
                if p_id not in seen:
                    seen.add(p_id)
                    results.append((p_id, plot_spec))
        except (Exception, SystemExit):
            # SystemExit from ConfigManager structural validation must not propagate
            # into the Shiny connection handler — bad manifests are silently skipped here.
            pass
    return results


def define_server(input, output, session, *,
                  bootloader, wrangle_studio, dev_studio,
                  orchestrator, viz_factory, gallery_viewer,
                  current_persona, anchor_path, tier1_anchor,
                  tier_reference, tier3_leaf, active_cfg,
                  active_collection_id, safe_input,
                  active_home_subtab, tier_toggle,
                  home_state=None, session_manager=None,
                  data_refresh_trigger=None,
                  notification_log=None,
                  session_pipeline_errors=None):
    """Register all Home Theater reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority (ADR-031).
    wrangle_studio : WrangleStudio
        Shared WrangleStudio state (for render_ui routing).
    dev_studio : TestLabStudio
        Shared TestLabStudio state.
    orchestrator : DataOrchestrator
        Used for Tier 1 materialization in dynamic_tabs.
    viz_factory : VizFactory
        Plotting engine.
    gallery_viewer : GalleryViewer
        Gallery explorer module.
    current_persona : reactive.Value[str]
        Active persona (ADR-030).
    anchor_path : reactive.Value[str | None]
        Path to active Parquet anchor.
    tier1_anchor : reactive.Calc
        Tier 1 LazyFrame.
    tier_reference : reactive.Calc
        Tier 2 reference LazyFrame.
    tier3_leaf : reactive.Calc
        Tier 3 user-modified DataFrame.
    active_cfg : reactive.Calc
        Active ConfigManager.
    active_collection_id : reactive.Calc
        Active collection ID string.
    safe_input : callable
        Shared utility: safe_input(input_obj, key, default) → value.
    active_home_subtab : reactive.Value[str]
        Phase 21-B: tracks the active plot sub-tab id across groups.
    tier_toggle : reactive.Value[str]
        Phase 21-C: active data tier selection ("T1", "T2", "T3").
    home_state : reactive.Value[dict] | None
        §13 Home Module State Object — survives all panel switches.
        Contains t3_recipe, applied_filters, tier_toggle, and navigation state.
    session_manager : SessionManager | None
        §12d Session ghost save/restore manager.
    session_pipeline_errors : reactive.Value[list] | None
        DIAG-RUNTIME-AUDIT-1: accumulates structured runtime error entries.
    """

    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    # ── Phase 21-B: Dynamic plot handlers for analysis_groups ─────────────────
    # Enumerate all plot IDs at server init time so Shiny can register each
    # @render.plot slot. Handlers read active_cfg() at render time, not init time.
    _all_group_plot_ids = _collect_all_group_plot_ids(bootloader)

    # ── Project load notification — fires on startup and on every project switch ─
    @reactive.Effect
    @reactive.event(input.project_id)
    def _notify_project_loaded():
        proj = safe_input(input, "project_id", "")
        if proj:
            _notify(f"📂 Project '{proj}' loaded — plots are ready.", type="message", duration=5)

    # Track selected project across sidebar nav switches (project_id input is
    # absent from DOM while Gallery/Blueprint is active; without this, returning
    # to Home re-renders sidebar_tools_ui with the default project selected).
    _last_project_id = reactive.Value(bootloader.get_default_project())

    @reactive.Effect
    def _track_project_id():
        v = safe_input(input, "project_id", None)
        if v is not None:
            _last_project_id.set(v)

    # ── Phase 21-F: Filter recipe builder state ────────────────────────────────
    # List of dicts: {column, op, value, dtype}  — consumed by plot handlers and data preview.
    # Separate from the sidebar_filters render so tier toggle / tab switches don't reset it.
    applied_filters = reactive.Value([])   # committed on Apply
    _pending_filters = reactive.Value([])  # staging area while user builds rows

    # Phase 22-J: scratch state holding nodes built during T3 promotion that
    # are awaiting the user's propagation choice (this/all/all-except).
    # The modal reads from this and writes plot_scopes_intent on confirm.
    _propagation_scratch = reactive.Value({"nodes": [], "kind": ""})

    def _resolve_active_spec(p_id: str | None) -> dict | None:
        """Return the plot spec dict for the active plot_id, searching groups then top-level."""
        cfg = active_cfg()
        groups = cfg.raw_config.get("analysis_groups", {})
        top_plots = cfg.raw_config.get("plots", {})
        spec = None
        for _gid, gspec in groups.items():
            if p_id and p_id in gspec.get("plots", {}):
                spec = gspec["plots"][p_id].get("spec")
                break
        if spec is None and p_id and p_id in top_plots:
            spec = top_plots[p_id]
        if spec is None:
            for _gid, gspec in groups.items():
                for _pid, pentry in gspec.get("plots", {}).items():
                    spec = pentry.get("spec")
                    break
                if spec:
                    break
        if spec is None:
            for _pid, pspec in top_plots.items():
                spec = pspec
                break
        return spec

    def _resolve_t1_lf(spec: dict | None):
        """Return the T1 LazyFrame for spec, always ignoring tier_toggle."""
        # Subscribe to data_refresh_trigger so imports invalidate this computation.
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        if spec is None:
            return tier1_anchor()
        target_ds = spec.get("target_dataset")
        if target_ds:
            anchor_dir = bootloader.get_location("user_sessions") / "anchors"
            out_path = anchor_dir / f"{target_ds}.parquet"
            if out_path.exists():
                return pl.scan_parquet(out_path)
            proj_id = safe_input(input, "project_id", bootloader.get_default_project())
            return orchestrator.materialize_tier1(
                project_id=proj_id,
                collection_id=target_ds,
                output_path=out_path,
            )
        return tier1_anchor()

    def _resolve_active_lf(spec: dict | None):
        """Return a LazyFrame for the dataset referenced by spec (or tier1_anchor).

        T2 and T3 both apply the assembly's tier2 wrangling steps on top of T1
        parquet — T1 parquet stays cached, T2/T3 are lazy transforms. T3 adds
        per-plot audit nodes (filters, drops) on top of this base.
        """
        lf = _resolve_t1_lf(spec)
        if tier_toggle.get() in ("T2", "T3"):
            target_ds = (spec or {}).get("target_dataset", "")
            try:
                from transformer.data_wrangler import DataWrangler
                recipe_raw = (
                    active_cfg().raw_config
                    .get("join_manifests", {})
                    .get(target_ds, {})
                    .get("recipe", [])
                )
                lf = DataWrangler(data_schema={}).run_tier2(lf, recipe_raw)
            except Exception:
                pass
        return lf

    def _active_plot_t3_nodes(plot_id: str | None = None) -> list[dict]:
        """Return the committed T3 RecipeNodes for the active plot subtab.

        Phase 22-J / ADR-049: per-plot stacks. When `plot_id` is None, uses
        the currently active subtab. Empty list if no T3 nodes for that plot.
        """
        if home_state is None:
            return []
        state = home_state.get()
        by_plot = state.get("t3_recipe_by_plot", {}) or {}
        if plot_id is None:
            plot_id = state.get("active_plot_subtab") or active_home_subtab.get()
        if not plot_id:
            return []
        return list(by_plot.get(plot_id, []))

    def _t3_drop_columns(plot_id: str | None = None) -> list[str]:
        """Active drop_column column names for the active plot's stack."""
        cols: list[str] = []
        for n in _active_plot_t3_nodes(plot_id):
            if not n.get("active", True):
                continue
            if n.get("node_type") != "drop_column":
                continue
            c = n.get("params", {}).get("column", "")
            if c:
                cols.append(c)
        return cols

    def _all_plot_subtab_ids() -> list[str]:
        """Enumerate every plot subtab id available in the active manifest.

        Used by the propagation dialog to populate the "All plots except…"
        multiselect and to expand "All plots" intent at btn_apply commit.
        """
        ids: list[str] = []
        try:
            cfg = active_cfg()
        except Exception:
            return ids
        groups = cfg.raw_config.get("analysis_groups", {}) or {}
        for _gid, gspec in groups.items():
            for p_id in (gspec.get("plots") or {}).keys():
                ids.append(f"subtab_{p_id}")
        # Top-level fallback plots (no group)
        for p_id in (cfg.raw_config.get("plots") or {}).keys():
            sid = f"subtab_{p_id}"
            if sid not in ids:
                ids.append(sid)
        return ids

    def _plot_label(subtab_id: str) -> str:
        """Pretty label for a subtab id — falls back to the bare id."""
        p_id = subtab_id.removeprefix("subtab_")
        try:
            cfg = active_cfg()
        except Exception:
            return p_id
        for gspec in (cfg.raw_config.get("analysis_groups") or {}).values():
            entry = (gspec.get("plots") or {}).get(p_id)
            if entry:
                return entry.get("label") or entry.get("name") or p_id
        return p_id

    def _t3_filter_rows(plot_id: str | None = None) -> list[dict]:
        """Active filter_row + exclusion_row nodes for the active plot.

        Both filter_row and exclusion_row are now applied via the same
        _apply_filter_rows path (an exclusion_row on a primary key is just
        a `not_in` filter once committed). The audit-trail distinction
        between the two node types is purely documentary — see ADR-049.
        """
        rows: list[dict] = []
        for n in _active_plot_t3_nodes(plot_id):
            if not n.get("active", True):
                continue
            nt = n.get("node_type")
            if nt not in ("filter_row", "exclusion_row"):
                continue
            p = n.get("params", {})
            if "column" not in p:
                continue
            rows.append({
                "column": p.get("column"),
                "op": p.get("op", "eq"),
                "value": p.get("value"),
                "dtype": p.get("dtype", "Utf8"),
            })
        return rows

    # _apply_filter_rows moved to app/modules/t3_recipe_engine.py (Phase 24-A, ADR-051)
    # Imported at module top.

    def _spec_discrete_axes(spec: dict | None) -> tuple[set[str], set[str]]:
        """
        Return (discrete_x_cols, discrete_y_cols) — columns declared as discrete
        by scale_x_discrete / scale_y_discrete layers in the plot spec.
        Used by the filter builder to choose widget type for numeric columns.
        """
        if spec is None:
            return set(), set()
        mapping = spec.get("mapping", {})
        x_col = mapping.get("x")
        y_col = mapping.get("y")
        layers = spec.get("layers", [])
        layer_names = {l.get("name", "") for l in layers}
        disc_x = {x_col} if x_col and "scale_x_discrete" in layer_names else set()
        disc_y = {y_col} if y_col and "scale_y_discrete" in layer_names else set()
        return disc_x, disc_y

    def _make_group_plot_handler(p_id: str):
        """Factory: returns a @render.plot fn that renders plot_group_{p_id}."""
        @output(id=f"plot_group_{p_id}")
        @render.plot(alt=f"Plot: {p_id}")
        def _group_plot_handler():
            cfg = active_cfg()
            groups = cfg.raw_config.get("analysis_groups", {})
            # Find the spec for this p_id across all groups
            spec = None
            for _gid, gspec in groups.items():
                plot_entry = gspec.get("plots", {}).get(p_id)
                if plot_entry is not None:
                    spec = plot_entry.get("spec")
                    break
            # Fall back to top-level plots if not found in any group
            if spec is None:
                top_plot = cfg.raw_config.get("plots", {}).get(p_id)
                if top_plot is not None:
                    spec = top_plot
            if spec is None:
                return None

            # Build synthetic manifest so viz_factory.render can be used.
            # Phase 21-F-2: Inject committed filters into plot spec.
            # _apply_filter_rows handles coercion and eq/ne→in/not_in promotion for lists.
            # Here we just strip the 'dtype' key before passing to VizFactory
            # (VizFactory filter dicts don't need it).
            import copy
            plot_spec = copy.deepcopy(spec)
            # Phase 22-J: per-plot T3 stack — query by this plot's subtab id,
            # not by the active subtab (this plot may not be the active one
            # when its render runs in re-renders).
            this_subtab = f"subtab_{p_id}"
            filter_rows = list(applied_filters.get()) + _t3_filter_rows(this_subtab)
            if filter_rows:
                vf_filters = [
                    {k: v for k, v in f.items() if k != "dtype"}
                    for f in filter_rows
                ]
                # Promote eq/ne to in/not_in when value is a list
                for vf in vf_filters:
                    if isinstance(vf.get("value"), list):
                        if vf["op"] in ("eq", "in"):
                            vf["op"] = "in"
                        elif vf["op"] in ("ne", "not_in"):
                            vf["op"] = "not_in"
                plot_spec["filters"] = vf_filters
            synthetic_manifest = {
                "plots": {p_id: plot_spec},
                "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
            }

            try:
                lf = _resolve_active_lf(spec)
            except Exception as e:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Data error: {e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9)
                ax.axis("off")
                return fig

            # Apply T3 drop_column nodes (audit-committed drops) — per-plot
            drops = [c for c in _t3_drop_columns(this_subtab) if c in lf.collect_schema().names()]
            if drops:
                lf = lf.drop(drops)

            # VIZFAC-T3-OVERRIDE-1: Extract L5 aesthetic_override from home_state.
            _t3_overrides = (
                (home_state.get() if home_state is not None else {})
                .get("t3_plot_overrides", {})
                .get(this_subtab)
            )

            try:
                return viz_factory.render(lf, synthetic_manifest, p_id,
                                          aesthetic_override=_t3_overrides)
            except Exception as e:
                # Capture error for session_pipeline_errors without violating R1
                # (cannot call reactive.Value.set inside @render.*).
                if session_pipeline_errors is not None:
                    from datetime import datetime
                    _entry = {
                        "timestamp": datetime.now().isoformat(),
                        "component": "VizFactory",
                        "problem": str(e)[:200],
                        "severity": "error",
                        "location": f"render(plot_id='{p_id}')",
                    }
                    def _append_render_error(entry=_entry):
                        current = session_pipeline_errors.get()
                        if len(current) < 50:
                            session_pipeline_errors.set(current + [entry])
                    session.on_flushed(_append_render_error, once=True)
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Render error:\n{e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9,
                        wrap=True)
                ax.axis("off")
                return fig

        return _group_plot_handler

    # Register one handler per discovered plot ID
    for _p_id, _spec in _all_group_plot_ids:
        _make_group_plot_handler(_p_id)

    # Phase 21-E: Baseline (T2) plot handlers for Comparison Mode.
    # Identical to the regular handlers but skip all T3 audit nodes — always
    # shows the pure T1 materialized data so the user can see what changed.
    def _make_cmp_baseline_handler(p_id: str):
        """Factory: renders plot_group_{p_id}_cmp_base WITHOUT T3 adjustments."""
        @output(id=f"plot_group_{p_id}_cmp_base")
        @render.plot(alt=f"Baseline: {p_id}")
        def _cmp_baseline_handler():
            cfg = active_cfg()
            groups = cfg.raw_config.get("analysis_groups", {})
            spec = None
            for _gid, gspec in groups.items():
                plot_entry = gspec.get("plots", {}).get(p_id)
                if plot_entry is not None:
                    spec = plot_entry.get("spec")
                    break
            if spec is None:
                top_plot = cfg.raw_config.get("plots", {}).get(p_id)
                if top_plot is not None:
                    spec = top_plot
            if spec is None:
                return None

            import copy
            plot_spec = copy.deepcopy(spec)
            # No T3 filters — this is the baseline view
            synthetic_manifest = {
                "plots": {p_id: plot_spec},
                "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
            }
            try:
                lf = _resolve_t1_lf(spec)  # baseline always shows pure T1
            except Exception as e:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Data error: {e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9)
                ax.axis("off")
                return fig

            try:
                return viz_factory.render(lf, synthetic_manifest, p_id)
            except Exception as e:
                if session_pipeline_errors is not None:
                    from datetime import datetime
                    _entry = {
                        "timestamp": datetime.now().isoformat(),
                        "component": "VizFactory",
                        "problem": str(e)[:200],
                        "severity": "error",
                        "location": f"render(plot_id='{p_id}', mode='cmp_base')",
                    }
                    def _append_cmp_error(entry=_entry):
                        current = session_pipeline_errors.get()
                        if len(current) < 50:
                            session_pipeline_errors.set(current + [entry])
                    session.on_flushed(_append_cmp_error, once=True)
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Render error:\n{e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9, wrap=True)
                ax.axis("off")
                return fig

        return _cmp_baseline_handler

    for _p_id, _spec in _all_group_plot_ids:
        _make_cmp_baseline_handler(_p_id)

    # Per-plot cell wrappers — own the single/comparison layout decision so that
    # dynamic_tabs never reads input.comparison_mode. Only the active plot_cell
    # re-renders when the compare switch toggles; the tab structure stays stable.
    def _make_plot_cell_handler(p_id: str):
        _acc_id = f"plot_acc_{p_id}"
        _panel_val = f"plot_panel_{p_id}"

        @output(id=f"plot_cell_{p_id}")
        @render.ui
        def _plot_cell_ui():
            in_comparison = bool(safe_input(input, "comparison_mode", False))

            # Read initial collapse state without creating a reactive dependency (Rule R4).
            # Client-side accordion preserves state across sub-tab switches; server state
            # is only used when the component is fully re-mounted (e.g. Home → Gallery → Home).
            with reactive.isolate():
                _hs = home_state.get() if home_state else {}
            _is_open = _hs.get("plot_collapse_state", {}).get(p_id, True)

            if in_comparison:
                content = ui.layout_columns(
                    ui.div(
                        ui.tags.div(
                            "T1 — Raw (Baseline)",
                            class_="badge bg-secondary mb-1 spv-text-xs",
                        ),
                        ui.output_plot(f"plot_group_{p_id}_cmp_base", height="440px"),
                    ),
                    ui.div(
                        ui.tags.div(
                            "T3 — My view (Filtered / Dropped)",
                            class_="badge mb-1 spv-text-xs",
                            style="background:#ffc107; color:#212529;",
                        ),
                        ui.output_plot(f"plot_group_{p_id}", height="440px"),
                    ),
                    col_widths=[6, 6],
                )
            else:
                content = ui.output_plot(f"plot_group_{p_id}", height="480px")

            return ui.accordion(
                ui.accordion_panel("Plot", content, value=_panel_val),
                id=_acc_id,
                open=_panel_val if _is_open else None,
                multiple=False,
                class_="spv-plot-accordion",
            )

        # Track per-plot accordion collapse → home_state (Rule R2: state writes in Effect)
        @reactive.Effect
        def _track_plot_collapse():
            val = safe_input(input, _acc_id, None)
            if home_state is None:
                return
            _hs = home_state.get()
            _state = dict(_hs.get("plot_collapse_state", {}))
            _now_open = val is not None
            if _state.get(p_id) != _now_open:  # idempotent guard (Rule R3)
                _state[p_id] = _now_open
                home_state.set({**_hs, "plot_collapse_state": _state})

        return _plot_cell_ui

    for _p_id, _spec in _all_group_plot_ids:
        _make_plot_cell_handler(_p_id)

    # 3. Reactive Tab Components (Discovery Architecture)
    @render.ui
    def dynamic_tabs():
        """
        Routes to WrangleStudio, TestLab, Gallery, or the Unified Home Theater.
        ADR-043 / Phase 21-A: 'Analysis Theater / Viz' nav mode eliminated.
        Home renders exclusively from manifest analysis_groups.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")
        p = current_persona.get()

        # 1. Module Routing (ADR-031 Compliance)
        if active_sidebar == "Wrangle Studio":
            return ui.div(wrangle_studio.render_ui(), class_="theater-container-main")
        if active_sidebar == "Test Lab":
            if dev_studio is None:
                return ui.div()
            return ui.div(dev_studio.render_ui(), class_="theater-container-main")
        if active_sidebar == "Gallery":
            return ui.div(gallery_viewer.render_explorer_ui(), class_="theater-container-main")

        # 2. Results Theater (Home) Logic — ADR-043 Unified Home Theater
        try:
            proj_id = safe_input(input, "project_id", bootloader.get_default_project())
            coll_id = active_collection_id()
            # ADR-024: Materialize to persistent session location
            anchor_dir = bootloader.get_location("user_sessions") / "anchors"
            if not anchor_dir.exists():
                anchor_dir.mkdir(parents=True, exist_ok=True)
            out_path = anchor_dir / f"{coll_id}.parquet"

            lf_full = orchestrator.materialize_tier1(
                project_id=proj_id,
                collection_id=coll_id,
                output_path=out_path
            )
            if out_path.exists():
                anchor_path.set(str(out_path))

        except Exception as e:
            return ui.div(ui.markdown(f"**Data Assembly Failed**: {e}"), class_="alert alert-danger")

        # Discover columns (retained for future filter scoping in Phase 21-F)
        all_cols = lf_full.collect_schema().names()  # noqa: F841

        cfg = active_cfg()
        groups = cfg.raw_config.get("analysis_groups", {})

        # --- UI-TITLE-1: manifest title banner ---
        # Resolution: persona ui_title.text override > manifest info.display_name > nothing.
        # If resolved title is empty or persona sets ui_title.visible=false: no banner.
        _ui_title_cfg = bootloader.config.get("ui_title", {})
        _title_visible = _ui_title_cfg.get("visible", True)
        _title_text = (
            _ui_title_cfg.get("text")
            or cfg.raw_config.get("info", {}).get("display_name", "")
        )
        _subtitle_text = (
            _ui_title_cfg.get("subtitle")
            or cfg.raw_config.get("info", {}).get("subtitle", "")
        )
        if _title_visible and _title_text:
            home_title_banner = ui.div(
                ui.tags.span(_title_text, class_="banner-title"),
                *([ui.tags.span(_subtitle_text, class_="banner-subtitle")] if _subtitle_text else []),
                class_="view-title-banner",
                style="margin-bottom: 8px;",
            )
        else:
            home_title_banner = ui.div()

        # --- Thin header: dataset label left, tier toggle right (Phase 21-C/D) ---
        def _tier_label(label: str, sub: str, tooltip: str) -> object:
            return ui.HTML(
                f'<span title="{tooltip}">'
                f'{label}<br>'
                f'<span style="font-size:0.65em;color:#9ca3af;font-weight:400">{sub}</span>'
                f'</span>'
            )

        tier_choices = {
            "T1": _tier_label(
                "Raw",
                "T1 — As assembled",
                "T1: Raw assembled data. No processing steps applied. "
                "In most projects T1 = T2. Use this to compare against the processed result.",
            ),
            "T2": _tier_label(
                "Result",
                "T2 — Processed",
                "T2: Data with pipeline processing applied "
                "(e.g. range filters, long-format pivots, derived columns). "
                "Default view. If no processing steps are defined, T2 = T1.",
            ),
        }
        if bootloader.is_enabled("t3_sandbox_enabled"):
            tier_choices["T3"] = _tier_label(
                "My view",
                "T3 — Filtered / Dropped",
                "T3: Your personal adjustments — row filters and column drops "
                "applied on top of T2. Only affects your session.",
            )

        # STATIC-VIEW-1a: static personas (interactivity_enabled=false) have no tier
        # switching — hide the strip entirely. T2 is the implicit default via the
        # _track_tier_toggle fallback (safe_input returns "T2" when input absent).
        if bootloader.is_enabled("interactivity_enabled"):
            theater_header = ui.div(
                ui.tags.span(
                    "Data to show:",
                    class_="fw-semibold me-3",
                    style="white-space: nowrap; color: #345beb;",
                ),
                ui.input_radio_buttons(
                    "tier_toggle",
                    label=None,
                    choices=tier_choices,
                    # Default T2: in most projects T2 = T1 so there is no cost,
                    # and projects with processing steps show the intended result.
                    # Use static default — tier_toggle reactive value is NOT read here
                    # so that tier changes do NOT invalidate/re-render dynamic_tabs DOM.
                    # The _track_tier_toggle effect keeps tier_toggle reactive in sync.
                    selected="T2",
                    inline=True,
                ),
                # Phase 21-E: Comparison Mode toggle — shown by comparison_mode_toggle_ui
                # render when persona is advanced+ and tier is T3.
                ui.output_ui("comparison_mode_toggle_ui"),
                class_="theater-header-strip",
            )
        else:
            theater_header = ui.div()

        # Data preview slot — always rendered regardless of groups presence
        # so the Shiny output ID is always mounted.
        data_preview_section = ui.div(
            ui.accordion(
                ui.accordion_panel(
                    ui.div(
                        ui.tags.span(
                            "Data Preview",
                            title="Preview the active plot dataset at the selected tier",
                            class_="me-3",
                        ),
                        # PREVIEW-ALLROWS-1: "Show all rows" toggle — off by default (100-row cap).
                        ui.input_switch("preview_all_rows", "All rows", value=False),
                        class_="d-flex align-items-center",
                    ),
                    # Phase 21-F-3: Column selector above the DataGrid
                    ui.output_ui("home_col_selector_ui"),
                    ui.output_data_frame("home_data_preview"),
                    value="data_panel",
                ),
                id="acc_home_data",
                open="data_panel",
            ),
            class_="spv-panel overflow-visible",
        )

        # --- No groups: fallback to top-level plots or show guidance ---
        if not groups:
            # Attempt to fall back to top-level plots in the manifest
            top_plots = cfg.raw_config.get("plots", {})
            if top_plots:
                # Wrap top-level plots in a synthetic single group
                plot_subtabs = []
                for p_id, plot_spec in top_plots.items():
                    tab_label = p_id.replace("_", " ").title()
                    plot_subtabs.append(
                        ui.nav_panel(
                            tab_label,
                            ui.output_plot(f"plot_group_{p_id}", height="480px"),
                            value=f"subtab_{p_id}"
                        )
                    )
                plots_card = ui.navset_card_tab(
                    *plot_subtabs, id="subtabs_default_group"
                )
                groups_nav = ui.div(plots_card, class_="spv-panel p-2")
            else:
                groups_nav = ui.p(
                    "Define analysis_groups (or top-level plots) in your manifest to populate this view.",
                    class_="text-muted p-4"
                )
            return ui.div(
                home_title_banner,
                theater_header,
                groups_nav,
                data_preview_section,
                class_="theater-container-main"
            )

        # --- Group nav panels — plots only inside each group (Option B) ---
        # Data preview lives OUTSIDE the group navset (single output ID, no duplicates).
        # Phase 21-E: Comparison Mode layout is owned by per-plot plot_cell_{p_id}
        # outputs (registered in _make_plot_cell_handler above). dynamic_tabs no
        # longer reads input.comparison_mode — only the active cell re-renders when
        # the compare switch toggles, leaving the tab structure (and all other plots)
        # untouched.

        # Restore active tab after Gallery/Blueprint nav switch (isolated read so
        # home_state changes — tier, filters, T3 nodes — never re-trigger this render)
        with reactive.isolate():
            _saved_hs = home_state.get() if home_state else {}
        _saved_subtab = _saved_hs.get("active_plot_subtab")  # e.g. "subtab_year_distribution"
        _saved_group = None
        if _saved_subtab:
            _saved_p_id = _saved_subtab.removeprefix("subtab_")
            for _gid, _gspec in groups.items():
                if _saved_p_id in _gspec.get("plots", {}):
                    _saved_group = f"group_{_safe_id(_gid)}"
                    break

        group_nav_panels = []
        for group_id, group_spec in groups.items():
            # ADR-036 ID sanitation
            safe_sub_id = _safe_id(group_id)
            group_label = group_spec.get("label") or group_spec.get("description", group_id)
            plot_ids = list(group_spec.get("plots", {}).keys())

            plot_subtabs = []
            for p_id in plot_ids:
                tab_label = (
                    group_spec["plots"][p_id].get("label")
                    or p_id.replace("_", " ").title()
                )
                plot_cell = ui.output_ui(f"plot_cell_{p_id}")

                plot_subtabs.append(
                    ui.nav_panel(
                        tab_label,
                        plot_cell,
                        value=f"subtab_{p_id}"
                    )
                )

            # navset_card_tab: gives the card border + built-in tab header — no extra label needed
            # selected= restores the previously active plot after a Gallery/Blueprint nav round-trip
            plots_card = (
                ui.navset_card_tab(*plot_subtabs, id=f"subtabs_{safe_sub_id}",
                                   selected=_saved_subtab)
                if plot_subtabs
                else ui.card(ui.p("No plots defined for this group.", class_="text-muted p-3"))
            )

            group_nav_panels.append(
                ui.nav_panel(group_label, ui.div(plots_card, class_="p-2"),
                             value=f"group_{safe_sub_id}")
            )

        # Group pill nav wrapped in spv-panel for consistent rounding
        groups_nav = ui.div(
            ui.navset_pill(
                *group_nav_panels,
                id="home_groups_nav",
                selected=_saved_group,
            ),
            class_="spv-panel",
            style="padding: 8px 10px 0 10px;",
        )

        return ui.div(
            home_title_banner,
            theater_header,
            groups_nav,
            data_preview_section,
            class_="theater-container-main"
        )

    # Phase 21-C: Sync tier_toggle input → reactive.Value so server.py calcs react.
    @reactive.Effect
    def _track_tier_toggle():
        val = safe_input(input, "tier_toggle", "T2")
        if val:
            tier_toggle.set(val)

    # Data change detection — runs as a side-effect separate from dynamic_tabs render.
    # Reads project_id to react when the user switches projects; computes source file
    # hashes, compares to stored data_batch_hash, warns if changed, and always writes
    # manifest_sha256 + data_batch_hash into home_state for session_manager.
    @reactive.Effect
    def _sync_session_provenance():
        if home_state is None:
            return
        proj_id = safe_input(input, "project_id", bootloader.get_default_project())
        if not proj_id:
            return
        try:
            from app.modules.session_manager import SessionManager as _SM
            from app.modules.session_manager import extract_primary_keys
            source_files = orchestrator.get_source_files(proj_id)
            new_dbh = _SM.compute_data_batch_hash(source_files) if source_files else ""
            manifest_path = bootloader.get_location("manifests") / f"{proj_id}.yaml"
            new_msig = _SM.compute_manifest_sha256(manifest_path) if manifest_path.exists() else ""
            new_pks = extract_primary_keys(active_cfg().raw_config)

            cur = home_state.get()
            prev_dbh = cur.get("data_batch_hash") or ""
            prev_msig = cur.get("manifest_sha256") or ""
            # Only warn if the SAME manifest's source files changed.
            # A project switch (different manifest_sha256) naturally has a
            # different data_batch_hash — that's expected, not an alert.
            same_manifest = prev_msig and prev_msig == new_msig
            if same_manifest and prev_dbh and prev_dbh != new_dbh:
                _notify(
                    "⚠️ Source data files for this project have changed — re-assembling.",
                    type="warning", duration=8,
                )
            needs_update = (
                cur.get("manifest_sha256") != new_msig
                or cur.get("data_batch_hash") != new_dbh
                or list(cur.get("primary_keys") or []) != list(new_pks)
            )
            if needs_update:
                home_state.set({
                    **cur,
                    "manifest_sha256": new_msig,
                    "data_batch_hash": new_dbh,
                    "primary_keys": new_pks,
                })

            # Write assembly ghost so export_session_zip includes provenance.
            # parquet_paths is empty — restore_t1t2 falls back to REASSEMBLE
            # when parquet is missing, so the session is still fully restorable.
            if new_msig and new_dbh and session_manager is not None:
                try:
                    session_key = _SM.compute_session_key(new_msig, new_dbh)
                    session_manager.write_assembly_ghost(
                        session_key=session_key,
                        manifest_id=proj_id,
                        manifest_sha256=new_msig,
                        data_batch_hash=new_dbh,
                        source_files={k: str(v) for k, v in source_files.items()},
                        parquet_paths={},
                    )
                except Exception:
                    pass
        except Exception:
            pass

    # Phase 21-B/D: Track active plot sub-tab across all group navsets.
    # Polls subtabs_{safe_sub_id} for the active group first, then all others.
    @reactive.Effect
    def _track_active_home_subtab():
        cfg = active_cfg()
        groups = cfg.raw_config.get("analysis_groups", {})
        active_group = safe_input(input, "home_groups_nav", None)

        def _set_active(val: str) -> None:
            """Write subtab to both the shim and home_state.active_plot_subtab.

            Phase 22-J: per-plot T3 stacks key off home_state.active_plot_subtab,
            so we mirror every shim update there. Idempotent guard avoids loops.
            """
            if active_home_subtab.get() != val:
                active_home_subtab.set(val)
            if home_state is not None:
                cur = home_state.get()
                if cur.get("active_plot_subtab") != val:
                    home_state.set({**cur, "active_plot_subtab": val})

        for group_id in groups:
            safe_sub_id = _safe_id(group_id)
            # Prioritise the active group's subtab
            if active_group and active_group != f"group_{safe_sub_id}":
                continue
            val = safe_input(input, f"subtabs_{safe_sub_id}", None)
            if val:
                _set_active(val)
                return
        # Fallback: accept any non-None subtab value from groups
        for group_id in groups:
            safe_sub_id = _safe_id(group_id)
            val = safe_input(input, f"subtabs_{safe_sub_id}", None)
            if val:
                _set_active(val)
                return
        # No-groups fallback: check the default synthetic group subtab
        val = safe_input(input, "subtabs_default_group", None)
        if val:
            _set_active(val)
            return

    # Phase 21-D/F: Data preview — scoped to active plot's dataset, with filters + col selector.
    @output
    @render.data_frame
    def home_data_preview():
        """Preview for the active plot's dataset. Applies committed filters + col selector.
        PREVIEW-ALLROWS-1: capped at 100 rows by default; toggle 'preview_all_rows' to uncap."""
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)

        try:
            lf = _resolve_active_lf(spec)
            lf = _apply_filter_rows(lf, list(applied_filters.get()) + _t3_filter_rows())
            # Apply T3 drop_column nodes — committed audit drops.
            drops = [c for c in _t3_drop_columns() if c in lf.collect_schema().names()]
            if drops:
                lf = lf.drop(drops)
            # PREVIEW-ALLROWS-1: respect the "Show all rows" toggle; default 100-row cap.
            show_all = safe_input(input, "preview_all_rows", False)
            df = lf.collect() if show_all else lf.head(100).collect()

            # Apply column visibility selection (Phase 21-F-4) — preview-only filter
            visible = safe_input(input, "preview_col_selector", None)
            if visible and isinstance(visible, (list, tuple)):
                visible_cols = [c for c in visible if c in df.columns]
                if visible_cols:
                    df = df.select(visible_cols)

            return render.DataGrid(df, filters=False, height="300px")
        except Exception as e:
            return render.DataGrid(
                pl.DataFrame({"Error": [str(e)]}),
                filters=False
            )

    # Phase 21-F-4: Column selector UI for data preview.
    # Split into two renders so the selectize component is NOT re-rendered on
    # every keystroke (which would reset the user's selection). The selectize
    # only re-renders when its data dependencies change (active subtab, the
    # set of columns, committed T3 drops) — not the user's transient selection.
    @output
    @render.ui
    def home_col_selector_ui():
        if not bootloader.is_enabled("interactivity_enabled"):
            return ui.div()
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        try:
            lf = _resolve_active_lf(spec)
            committed_drops = set(_t3_drop_columns())
            cols = [c for c in lf.collect_schema().names() if c not in committed_drops]
            in_t3 = tier_toggle.get() == "T3"
            label_text = (
                "Columns (drop unselected via audit):" if in_t3
                else "Table columns (view only — no effect on plot):"
            )

            return ui.div(
                # Header row: label left, audit-drop button right
                ui.div(
                    ui.tags.small(label_text,
                                  class_="text-muted fw-semibold"),
                    ui.output_ui("col_drop_audit_btn_ui"),
                    class_="spv-row-between",
                ),
                ui.input_selectize(
                    "preview_col_selector",
                    label=None,
                    choices=cols,
                    selected=cols,
                    multiple=True,
                    options={
                        "placeholder": "Select columns…",
                        "plugins": ["remove_button"],
                    },
                ),
                class_="mb-2 w-100 column-picker-container spv-text-xs",
            )
        except Exception:
            return ui.div()

    @output
    @render.ui
    def col_drop_audit_btn_ui():
        """Live count of deselected columns — re-renders on selection change.

        Kept SEPARATE from home_col_selector_ui so reading the selector input
        here does not invalidate the selectize component itself.
        """
        if tier_toggle.get() != "T3":
            return ui.span()
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        try:
            lf = _resolve_active_lf(spec)
        except Exception:
            return ui.span()
        committed = set(_t3_drop_columns())
        cols = [c for c in lf.collect_schema().names() if c not in committed]
        visible = safe_input(input, "preview_col_selector", cols)
        vis_set = set(visible) if isinstance(visible, (list, tuple)) else set(cols)
        n_drop = len([c for c in cols if c not in vis_set])
        return ui.input_action_button(
            "col_drop_to_audit", f"➜ Audit drops ({n_drop})",
            class_="btn-warning btn-sm spv-text-xxs",
            style="white-space:nowrap;",
            disabled=(n_drop == 0),
        )

    @render.ui
    def sidebar_nav_ui():
        perm = current_persona.get()
        print(f"DEBUG: Rendering sidebar_nav_ui for Persona: {perm}")

        nav_items = [ui.nav_panel("Home", value="Home")]

        # PERSONA-1 (2026-04-30): gates consult the persona feature-flag system
        # via bootloader.is_enabled(...) instead of hardcoded persona names. This
        # matches the design intent of .claude/rules/rules_persona_feature_flags.md
        # — flags like gallery_enabled are documented as INDEPENDENT and can be
        # flipped per-persona in config/ui/templates/ without touching code here.
        if bootloader.is_enabled("wrangle_studio_enabled"):
            nav_items.append(ui.nav_panel("Blueprint Architect", value="Wrangle Studio"))

        if bootloader.is_enabled("developer_mode_enabled"):
            nav_items.append(ui.nav_panel("Test Lab", value="Test Lab"))

        if bootloader.is_enabled("gallery_enabled"):
            nav_items.append(ui.nav_panel("Gallery", value="Gallery"))

        badge = (
            ui.h6(f"Active: {perm.replace('_', ' ').title()}",
                  class_="text-muted px-2 py-1 mb-1 border-bottom spv-text-meta")
            if bootloader.is_enabled("show_persona_badge")
            else None
        )
        help_btn = ui.input_action_button(
            "btn_help_ws", "? Help",
            class_="btn btn-outline-secondary btn-sm w-100 mt-2",
            style="font-size:0.75rem;",
        )
        return ui.div(
            ui.navset_pill(
                *nav_items,
                id="sidebar_nav",
                header=badge,
            ),
            help_btn,
        )

    # HELP-INLINE-1: workspace help modal
    _HELP_DIR = Path(__file__).parent.parent / "src" / "help"

    @reactive.Effect
    @reactive.event(input.btn_help_ws)
    def _show_workspace_help():
        ws = safe_input(input, "sidebar_nav", "Home")
        _ws_file_map = {
            "Home": "home.md",
            "Wrangle Studio": "blueprint.md",
            "Gallery": "gallery.md",
            "Test Lab": "test_lab.md",
        }
        md_file = _HELP_DIR / _ws_file_map.get(ws, "home.md")
        try:
            md_text = md_file.read_text(encoding="utf-8")
        except Exception:
            md_text = f"No help available for **{ws}**."
        m = ui.modal(
            ui.markdown(md_text),
            title=f"{ws} — Help",
            easy_close=True,
            footer=ui.modal_button("Close"),
            size="lg",
        )
        ui.modal_show(m)

    # 4. Sidebar Tools (Contextual Manifest Workbench)
    @output(id="sidebar_tools_ui")
    @render.ui
    def sidebar_tools_ui():
        """
        Relocated Sidebar Management (ADR-038).
        Enforces dedicated Persona-based control clusters.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")

        # 🟢 Gallery (ADR-057: filter + recipe selector moved here from internal sidebar)
        if active_sidebar == "Gallery":
            return ui.div(
                gallery_viewer.build_sidebar_ui(),
                ui.output_ui("notification_log_panel_ui"),
            )

        # 🔵 Manifest Workbench (Wrangle Studio)
        if active_sidebar == "Wrangle Studio":
            return ui.div(
                ui.accordion(
                    ui.accordion_panel(
                        "🗂️ Master Manifest",
                        ui.input_select("stored_manifest_selector", None,
                                        choices=["Scanning config/..."]),
                        ui.tags.small(
                            "Select a project manifest. Click any node in the TubeMap to navigate.",
                            class_="text-muted d-block mt-1"),
                        icon=ui.tags.i(class_="bi bi-diagram-3")
                    ),
                    ui.accordion_panel(
                        "📤 External Exchange",
                        ui.input_file("manifest_uploader", "Select YAML...",
                                      accept=[".yaml"], multiple=False),
                        ui.input_action_button("btn_upload_replace", "📥 Upload (Replace)",
                                               class_="btn-info btn-sm w-100 mb-1"),
                        ui.input_action_button("btn_upload_append", "➕ Upload & Append",
                                               class_="btn-outline-primary btn-sm w-100"),
                        ui.hr(),
                        ui.download_button("btn_download_manifest", "💾 Download/Export",
                                           class_="btn-outline-primary w-100"),
                        icon=ui.tags.i(class_="bi bi-cloud-arrow-up")
                    ),
                    ui.accordion_panel(
                        "🔤 YAML Escape Hatch",
                        ui.output_ui("bp_yaml_escape_ui"),
                        icon=ui.tags.i(class_="bi bi-code-slash")
                    ),
                    id="wrangle_sidebar_accordion"
                ),
                # Hidden controls — kept in DOM so Shiny bridge can programmatically
                # update the selection and fire the import trigger via js_eval.
                ui.div(
                    ui.input_select("dataset_pipeline_selector", None,
                                    choices=["Select a Master first"]),
                    ui.input_action_button("btn_import_manifest", "Import",
                                           class_="btn-info btn-sm"),
                    ui.input_action_button("btn_save_internal", "Save",
                                           class_="btn-success btn-sm"),
                    style="display:none;",
                    id="blueprint_hidden_controls"
                ),
                ui.output_ui("notification_log_panel_ui"),
            )

        # 🏠 Standard Operation Sidebar (Home — ADR-043 / ADR-073)
        # Build project state needed by some panel renderers.
        try:
            proj_choices = list(bootloader.available_projects.keys())
            def_proj = bootloader.get_default_project()
        except Exception:
            proj_choices = []
            def_proj = None

        with reactive.isolate():
            _current_proj = _last_project_id.get() or def_proj

        # Panel renderer map: type → callable() → accordion_panel | None
        # None means the panel type was handled (e.g. notification_log goes outside accordion).
        def _render_project_info():
            return ui.accordion_panel(
                "Project",
                ui.div(
                    ui.tags.small(
                        bootloader.deployment_name,
                        class_="text-muted d-block"
                    ),
                    class_="p-1"
                ),
                icon=ui.tags.i(class_="bi bi-info-circle-fill")
            )

        def _render_deployment_info():
            banner = bootloader.get_ui_banner()
            if not banner:
                return None
            return ui.accordion_panel(
                "Deployment",
                ui.div(
                    ui.tags.small(banner.get("title", ""), class_="fw-bold d-block"),
                    ui.tags.small(banner.get("subtitle", ""), class_="text-muted d-block"),
                    class_="p-1"
                ),
                icon=ui.tags.i(class_="bi bi-building")
            )

        def _render_manifest_choice():
            return ui.accordion_panel(
                "Manifest Choice",
                ui.div(
                    ui.input_select("project_id", "Project Selection",
                                    choices=proj_choices,
                                    selected=_current_proj),
                    class_="d-flex flex-column gap-1"
                ),
                icon=ui.tags.i(class_="bi bi-folder-fill")
            )

        def _render_filters():
            return ui.accordion_panel(
                "Filters",
                ui.div(
                    ui.output_ui("sidebar_filters"),
                    class_="d-flex flex-column gap-0"
                ),
                icon=ui.tags.i(class_="bi bi-filter-circle-fill")
            )

        def _render_data_import():
            return ui.accordion_panel(
                "Data Import",
                ui.div(
                    ui.output_ui("data_import_ui"),
                    class_="d-flex flex-column gap-0"
                ),
                icon=ui.tags.i(class_="bi bi-database-fill-down")
            )

        def _render_export():
            return ui.accordion_panel(
                "Export",
                ui.div(
                    ui.output_ui("system_tools_ui"),
                    class_="d-flex flex-column gap-1"
                ),
                icon=ui.tags.i(class_="bi bi-box-arrow-up")
            )

        def _render_session_management():
            return ui.accordion_panel(
                "Session Management",
                ui.div(
                    ui.output_ui("session_management_ui"),
                    class_="d-flex flex-column gap-1"
                ),
                icon=ui.tags.i(class_="bi bi-clock-history")
            )

        _home_panel_renderers = {
            "project_info":       _render_project_info,
            "deployment_info":    _render_deployment_info,
            "manifest_choice":    _render_manifest_choice,
            "filters":            _render_filters,
            "data_import":        _render_data_import,
            "export":             _render_export,
            "session_management": _render_session_management,
        }

        # Iterate slot list from persona template (ADR-073).
        sidebar_cfg = bootloader.get_sidebar_config("home", "left")
        panels = []
        include_notification_log = False
        for slot in sidebar_cfg.panels:
            ptype = slot.get("type", "")
            if ptype == "notification_log":
                include_notification_log = True
                continue
            if not is_panel_active(ptype, bootloader):
                continue
            renderer = _home_panel_renderers.get(ptype)
            if renderer is None:
                print(f"[home_theater] No renderer for panel type '{ptype}' — skipping.")
                continue
            panel = renderer()
            if panel is not None:
                panels.append(panel)

        _has_manifest = bootloader.get_manifest_selector().get("visible", True)
        open_panels = ["Manifest Choice"] if _has_manifest else []
        return ui.div(
            ui.accordion(
                *panels,
                id="nav_accordion",
                multiple=True,
                open=open_panels,
            ),
            ui.output_ui("notification_log_panel_ui") if include_notification_log else ui.div(),
        )

    # --- 📐 Right Sidebar Context Matrix (ADR-039 / ADR-044) ---
    @output
    @render.ui
    def right_sidebar_content_ui():
        """
        Context-sensitive right sidebar (ADR-039).
        Switches content based on the active module.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")

        # --- 🏗️ Blueprint Architect (Wrangle Studio) ---
        if active_sidebar == "Wrangle Studio":
            selected_node = safe_input(input, "blueprint_node_clicked", None)
            stack = wrangle_studio.logic_stack.get()
            step_count = len(stack)

            node_info = ui.div(
                ui.p("No node selected. Click a TubeMap node to begin surgical focus.",
                     class_="text-muted small italic"),
                class_="p-2"
            )
            if selected_node:
                node_info = ui.div(
                    ui.div(
                        ui.span("🔬 ", class_="me-1"),
                        ui.span(f"Focused: {selected_node}", class_="fw-bold"),
                        class_="mb-1"
                    ),
                    ui.div(f"Logic stack: {step_count} step(s)", class_="text-muted small"),
                    class_="p-2 bg-white border rounded shadow-sm mb-2"
                )

            parts = [
                ui.card(
                    ui.card_header(
                        ui.div(ui.h5("Blueprint Surgeon", class_="mb-0"),
                               class_="d-flex justify-content-center w-100")
                    ),
                    ui.div(
                        ui.output_ui("bp_action_form_ui"),
                        class_="p-2"
                    ),
                    class_="mb-2 shadow-sm border-0"
                ),
                ui.card(
                    ui.card_header(
                        ui.div(ui.h5("Action Help", class_="mb-0"),
                               class_="d-flex justify-content-center w-100")
                    ),
                    ui.output_ui("bp_help_panel_ui"),
                    class_="mb-2 shadow-sm border-0"
                ),
                # VIZFAC-BLUEPRINT-FORM-1: plot_defaults editor (manifest root node)
                ui.card(
                    ui.card_header(
                        ui.div(ui.h5("Plot Defaults", class_="mb-0"),
                               class_="d-flex justify-content-center w-100")
                    ),
                    ui.output_ui("bp_plot_defaults_form_ui"),
                    class_="mb-2 shadow-sm border-0"
                ),
            ]
            if bootloader.is_enabled("blueprint_agent_enabled"):
                parts.append(
                    ui.card(
                        ui.card_header(
                            ui.div(ui.h5("Blueprint Agent", class_="mb-0"),
                                   class_="d-flex justify-content-center w-100")
                        ),
                        ui.output_ui("blueprint_agent_panel_ui"),
                        class_="mb-2 shadow-sm border-0 d-flex flex-column spv-flex-1-auto"
                    )
                )
            return ui.div(*parts, class_="sidebar-content p-0 d-flex flex-column h-100")

        # --- 🏠 Home Theater (ADR-043 / ADR-044 / ADR-073) ---
        if active_sidebar in ("Home", None, ""):
            # Iterate right sidebar slot list for Home workspace.
            right_cfg = bootloader.get_sidebar_config("home", "right")
            right_types = {s.get("type", "") for s in right_cfg.panels}

            parts = []
            if "audit_stack" in right_types and is_panel_active("audit_stack", bootloader):
                parts.append(ui.card(
                    ui.card_header(
                        ui.div(ui.h5("Pipeline Audit", class_="mb-0 fw-bold"),
                               class_="d-flex justify-content-center w-100"),
                        style="background:#fffde7;"
                    ),
                    ui.div(
                        ui.output_ui("recipe_pending_badge_ui"),
                        ui.output_ui("audit_nodes_header_ui"),
                        ui.h6("Inherited (Tier 2)", class_="text-muted spv-label-caps"),
                        ui.output_ui("audit_nodes_tier2"),
                        ui.hr(class_="spv-divider"),
                        ui.output_ui("audit_nodes_tier3"),
                        class_="p-2 spv-scroll-flex",
                    ),
                    class_="mb-2 shadow-sm border-0 d-flex flex-column spv-flex-1-auto",
                ))
                parts.append(ui.output_ui("audit_stack_tools_ui"))

            if "notification_log" in right_types:
                parts.append(ui.output_ui("notification_log_panel_ui"))

            if not parts:
                return ui.div(class_="sidebar-content p-0")

            return ui.div(*parts, class_="sidebar-content p-0 d-flex flex-column h-100")

        # --- 🖼️ Gallery ---
        if active_sidebar == "Gallery":
            return ui.div(
                ui.card(
                    ui.card_header(ui.h5("Gallery Explorer", class_="mb-0 text-center")),
                    ui.div(
                        ui.p("📚 Browse visual recipes.", class_="text-muted small p-2"),
                        ui.p("Select a recipe to copy its YAML into the Architect sandbox.",
                             class_="text-muted small px-2"),
                        class_="p-1"
                    ),
                    class_="mb-2 shadow-sm border-0"
                ),
                class_="sidebar-content p-0"
            )

        # --- 🛠️ Test Lab ---
        if active_sidebar == "Test Lab":
            return ui.div(
                ui.card(
                    ui.card_header(ui.h5("Dev Inspector", class_="mb-0 text-center")),
                    ui.div(
                        ui.p("🔧 Developer diagnostic tools.", class_="text-muted small p-2"),
                        class_="p-1"
                    ),
                    class_="mb-2 shadow-sm border-0"
                ),
                class_="sidebar-content p-0"
            )

        # --- Default fallback ---
        return ui.div(
            ui.p("—", class_="text-muted p-3 text-center"),
            class_="sidebar-content p-0"
        )

    # ── UX-NOTIF-1: Persistent Alert Log ──────────────────────────────────────
    @output
    @render.ui
    def notification_log_panel_ui():
        """Render the last-20 notifications as a collapsible accordion in the right sidebar."""
        _type_color = {
            "success": "#198754",
            "warning": "#ca6f00",
            "error": "#dc3545",
            "message": "#345beb",
        }
        entries = notification_log.get() if notification_log is not None else []
        count = len(entries)
        rows = []
        for e in reversed(entries):
            color = _type_color.get(e.get("type", "message"), "#345beb")
            rows.append(
                ui.div(
                    ui.tags.span(
                        e.get("ts", ""),
                        class_="text-muted spv-text-meta",
                        style="white-space:nowrap; margin-right:6px;",
                    ),
                    ui.tags.span(
                        e.get("msg", ""),
                        class_="spv-text-xs",
                        style=f"color:{color};",
                    ),
                    class_="spv-tag-row",
                )
            )
        body = (
            ui.div(*rows, class_="spv-scroll-md")
            if rows
            else ui.tags.small("No alerts yet.", class_="text-muted", style="padding:4px;")
        )
        return ui.accordion(
            ui.accordion_panel(
                f"🔔 Alerts ({count})",
                body,
            ),
            id="notification_log_accordion",
            open=False,
        )

    # ── Export pipeline (system_tools_ui + bundle + audit reports) ────────────
    # Moved to app/handlers/export_handlers.py (Phase 24-C, ADR-051).
    define_export_server(
        input, output, session,
        bootloader=bootloader,
        orchestrator=orchestrator,
        viz_factory=viz_factory,
        current_persona=current_persona,
        active_cfg=active_cfg,
        tier1_anchor=tier1_anchor,
        tier_reference=tier_reference,
        tier3_leaf=tier3_leaf,
        tier_toggle=tier_toggle,
        applied_filters=applied_filters,
        home_state=home_state,
        safe_input=safe_input,
        active_home_subtab=active_home_subtab,
        notification_log=notification_log,
        session_pipeline_errors=session_pipeline_errors,
    )

    # ── 22-D: Session Management Panel ────────────────────────────────────────
    # session_management_ui + _handle_session_import + _handle_session_actions
    # + _restore_session moved to app/handlers/session_handlers.py
    # (Phase 24-B, ADR-051). Imported at module top.
    define_session_server(
        input, output, session,
        session_manager=session_manager,
        current_persona=current_persona,
        home_state=home_state,
        safe_input=safe_input,
        notification_log=notification_log,
    )

    # ── Phase 25-F: Data Import panel ────────────────────────────────────────
    define_data_import_server(
        input, output, session,
        orchestrator=orchestrator,
        active_cfg=active_cfg,
        safe_input=safe_input,
        data_refresh_trigger=data_refresh_trigger,
        notification_log=notification_log,
    )


    # ── Phase 21-F + 22-J: Filter UI + T3 audit + propagation modal ──────────
    # Moved to app/handlers/filter_and_audit_handlers.py (Phase 24-D, ADR-051).
    define_filter_audit_server(
        input, output, session,
        applied_filters=applied_filters,
        _pending_filters=_pending_filters,
        _propagation_scratch=_propagation_scratch,
        home_state=home_state,
        tier_toggle=tier_toggle,
        active_home_subtab=active_home_subtab,
        safe_input=safe_input,
        _resolve_active_spec=_resolve_active_spec,
        _resolve_active_lf=_resolve_active_lf,
        _spec_discrete_axes=_spec_discrete_axes,
        _t3_drop_columns=_t3_drop_columns,
        _all_plot_subtab_ids=_all_plot_subtab_ids,
        _plot_label=_plot_label,
        notification_log=notification_log,
    )

    @output
    @render.plot
    def plot_reference():
        cfg = active_cfg()
        plot_ids = list(cfg.raw_config.get("plots", {}).keys())
        if not plot_ids:
            return None
        plot_id = plot_ids[0]

        proj = cfg.raw_config.get("id", input.project_id())
        coll = active_collection_id()
        cached_plot = bootloader.get_cached_asset(proj, coll, plot_id, "ref_plot")
        if cached_plot is not None:
            return cached_plot

        plt = viz_factory.render(tier_reference(), cfg.raw_config, plot_id)
        bootloader.set_cached_asset(proj, coll, plot_id, "ref_plot", plt)
        return plt

    @output
    @render.table
    def table_reference():
        show_all = safe_input(input, "preview_all_rows", False)
        lf = tier_reference()
        return lf.collect() if show_all else lf.head(100).collect()

    @output
    @render.plot
    def plot_leaf():
        cfg = active_cfg()
        plot_ids = list(cfg.raw_config.get("plots", {}).keys())
        if not plot_ids:
            return None
        return viz_factory.render(tier3_leaf().lazy(), cfg.raw_config, plot_ids[0])

    @output
    @render.table
    def table_leaf():
        return tier3_leaf().head(5)

    @reactive.Effect
    @reactive.event(input.plot_leaf_brush)
    def handle_plot_brush():
        brush = input.plot_leaf_brush()
        if not brush:
            return
        cfg = active_cfg()
        plot_ids = list(cfg.raw_config.get("plots", {}).keys())
        if not plot_ids:
            return
        plot_id = plot_ids[0]
        mapping = cfg.raw_config["plots"][plot_id].get("mapping", {})
        x_col = mapping.get("x")
        y_col = mapping.get("y")

        outliers = lookup_anchor_rows(
            brush, anchor_path.get(), x_col=x_col, y_col=y_col)
        if outliers.is_empty():
            return

        m = ui.modal(
            ui.h4(f"Outlier Quick-View ({outliers.height} rows)"),
            ui.output_table("brush_results_table"),
            ui.modal_button("Close"),
            size="xl", easy_close=True
        )
        ui.modal_show(m)

        @output
        @render.table
        def brush_results_table():
            return outliers.head(20)

    @render.ui
    def comparison_mode_toggle_ui():
        """Phase 21-E / 25-C: Comparison Mode toggle — gated by comparison_mode_enabled flag.

        Always renders the switch (keeps input.comparison_mode registered in DOM)
        but hides it with CSS when not in T3. Avoids DOM removal on tier toggle,
        which previously caused dynamic_tabs to re-render via input.comparison_mode
        re-initialisation.
        """
        if not bootloader.is_enabled("comparison_mode_enabled"):
            return ui.div()
        in_t3 = tier_toggle.get() == "T3"
        return ui.div(
            ui.input_switch("comparison_mode", "⚖ Compare T2 vs T3", value=False),
            class_="d-flex align-items-center ms-3",
            style=(
                "height: 36px; padding-top: 4px; white-space: nowrap;"
                if in_t3 else
                "display: none;"
            ),
        )
