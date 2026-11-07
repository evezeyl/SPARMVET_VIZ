"""app/handlers/home_theater.py
Home Theater Shiny wiring (ADR-043 / ADR-044 / ADR-045).

Entry point:
    define_server(input, output, session, *,
                  bootloader, wrangle_studio, dev_studio,
                  orchestrator, viz_factory, gallery_viewer,
                  current_app_features, anchor_path, tier1_anchor,
                  active_cfg,
                  active_collection_id, safe_input, active_home_subtab, tier_toggle,
                  home_state=None, session_manager=None)

Concern: dynamic_tabs, sidebar_nav_ui, sidebar_tools_ui,
         right_sidebar_content_ui, home_data_preview/col_selector,
         col_drop_audit_btn_ui. (ADR-086: the plot_view radio replaces the old comparison_mode switch.)
         The legacy plot_reference/table_reference/plot_leaf/table_leaf outputs and the T3 brush modal
         were never mounted after ADR-043 and were removed 2026-11-06 (ADR-045-SERVER-SIZE-1).

Sub-handlers (Phase 24, ADR-051) — called from inside define_server():
  app/handlers/session_handlers.py            session management panel
  app/handlers/export_handlers.py             system tools + bundle + audit reports
  app/handlers/filter_and_audit_handlers.py   filter UI + T3 audit + propagation modal
  app/modules/t3_audit_engine.py             pure helpers (_apply_filter_rows, _op_label)

Two-Category Law (ADR-045): This file contains @render.* and @reactive.*
decorators only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (home_theater), output:dynamic_tabs, output:home_data_preview, output:home_col_selector_ui, output:col_drop_audit_btn_ui, output:sidebar_nav_ui, output:sidebar_tools_ui, output:right_sidebar_content_ui, output:plot_cell_{p_id} (per-plot); HELP-INLINE-1: btn_help_ws + _show_workspace_help; 22-J-10: mounts aesthetic_style_panel_ui slot; PROP-2: output:filter_inventory_ui
# consumes: app/modules/orchestrator.py, app/modules/wrangle_studio.py, app/modules/test_lab_studio.py, app/modules/gallery_viewer.py, libs/viz_factory/src/viz_factory/viz_factory.py, utils/config_loader.py, app/modules/t3_audit_engine.py, app/modules/sidebar_registry.py, app/handlers/session_handlers.py, app/handlers/export_handlers.py, app/handlers/filter_and_audit_handlers.py, app/handlers/data_import_handlers.py
#              libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-AUDIT-1, via session.on_flushed capture)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-043, .claude/knowledge/architecture_decisions.md#ADR-044, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-047, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-073, .claude/knowledge/architecture_decisions.md#ADR-085, .claude/rules/ui_implementation_contract.md#4, .claude/rules/ui_implementation_contract.md#5
# @end_deps

import re
from pathlib import Path

import polars as pl
from shiny import reactive, render, ui
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.view_badge import has_tier2_steps, view_badge

from app.modules.t3_audit_engine import _apply_filter_rows
from app.modules.sidebar_registry import is_panel_active
from app.handlers.session_handlers import define_session_server
from app.handlers.export_handlers import define_export_server
from app.handlers.filter_and_audit_handlers import define_filter_audit_server
from app.handlers.data_import_handlers import define_data_import_server

# ADR-036: Shiny input IDs must match ^[a-zA-Z0-9_]+$ — no spaces, emoji, or
# punctuation. This sanitiser strips anything outside that set so data analysis recipe
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
    for data_analysis_recipe_id, data_analysis_recipe_path in bootloader.available_data_analysis_recipes.items():
        try:
            cfg = load_data_analysis_recipe(data_analysis_recipe_path).config
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
            # into the Shiny connection handler — bad data analysis recipes are silently skipped here.
            pass
    return results


def define_server(input, output, session, *,
                  bootloader, wrangle_studio, dev_studio,
                  orchestrator, viz_factory, gallery_viewer,
                  current_app_features, anchor_path, tier1_anchor,
                  active_cfg,
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
    current_app_features : reactive.Value[str]
        Active app features (ADR-030).
    anchor_path : reactive.Value[str | None]
        Path to active Parquet anchor.
    tier1_anchor : reactive.Calc
        Tier 1 LazyFrame.
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
        Contains t3_audit_steps, applied_filters, tier_toggle, and navigation state.
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

    # ── Data analysis recipe load notification: fires on startup and on every switch of data analysis recipe ─
    @reactive.Effect
    @reactive.event(input.data_analysis_recipe_id)
    def _notify_data_analysis_recipe_loaded():
        proj = safe_input(input, "data_analysis_recipe_id", "")
        if proj:
            _notify(f"📂 Data analysis recipe '{proj}' loaded — plots are ready.", type="message", duration=5)

    # Track selected data analysis recipe across sidebar nav switches (data_analysis_recipe_id input is
    # absent from DOM while Gallery/Blueprint is active; without this, returning
    # to Home re-renders sidebar_tools_ui with the default data analysis recipe selected).
    _last_data_analysis_recipe_id = reactive.Value(bootloader.get_default_data_analysis_recipe())

    @reactive.Effect
    def _track_data_analysis_recipe_id():
        v = safe_input(input, "data_analysis_recipe_id", None)
        if v is not None:
            _last_data_analysis_recipe_id.set(v)

    # ── Phase 21-F: Filter builder state ────────────────────────────────
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

    @reactive.Calc
    def _data_analysis_recipe_keys():
        """Chained cache keys of the active data analysis recipe (ADR-089), computed once per session.

        Hashes the data files by content, so it re-runs only when the project or the
        imported data changes (data_refresh_trigger), not on every plot render.
        """
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
        return orchestrator.compute_data_analysis_recipe_keys(data_analysis_recipe_id)

    def _resolve_t1_lf(spec: dict | None):
        """Return the T1 LazyFrame for spec, always ignoring tier_toggle."""
        # Subscribe to data_refresh_trigger so imports invalidate this computation.
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        if spec is None:
            return tier1_anchor()
        target_ds = spec.get("target_dataset")
        if target_ds:
            anchor_dir = bootloader.get_location("user_data") / "anchors"
            out_path = anchor_dir / f"{target_ds}.parquet"
            data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
            # ADR-089: never reuse an anchor by file name. The orchestrator checks the chained
            # key stored in the file (a cheap metadata read) and rebuilds only when it differs.
            return orchestrator.materialize_tier1(
                data_analysis_recipe_id=data_analysis_recipe_id,
                collection_id=target_ds,
                output_path=out_path,
                keys=_data_analysis_recipe_keys(),
            )
        return tier1_anchor()

    def _resolve_active_lf(spec: dict | None, tier: str | None = None):
        """Return a LazyFrame for the dataset referenced by spec (or tier1_anchor).

        T2 and T3 both read the assembly's stored Tier 2 parquet (issue #10; equal to T1
        when the join has no tier2 steps). T3 adds per-plot audit nodes (filters, drops)
        on top of this base.

        `tier` defaults to the data view (tier_toggle). Plot handlers pass "T2"
        explicitly: plots never show T1 and follow plot_view, not tier_toggle (ADR-086).
        """
        if (tier or tier_toggle.get()) in ("T2", "T3") and (spec or {}).get("target_dataset"):
            target_ds = spec["target_dataset"]
            if data_refresh_trigger is not None:
                data_refresh_trigger.get()
            out_path = bootloader.get_location("user_data") / "anchors" / f"{target_ds}.parquet"
            data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
            # Issue #10 / ADR-089: T2 is read from its stored parquet (key-checked). An error is
            # not caught here: showing Tier 1 in place of a failed Tier 2 would be a false result.
            return orchestrator.materialize_tier2(
                data_analysis_recipe_id=data_analysis_recipe_id, collection_id=target_ds,
                tier1_path=out_path, keys=_data_analysis_recipe_keys())
        return _resolve_t1_lf(spec)

    def _active_plot_t3_nodes(plot_id: str | None = None) -> list[dict]:
        """Return the committed T3 AuditSteps for the active plot subtab.

        Phase 22-J / ADR-049: per-plot stacks. When `plot_id` is None, uses
        the currently active subtab. Empty list if no T3 nodes for that plot.
        """
        if home_state is None:
            return []
        state = home_state.get()
        by_plot = state.get("t3_audit_steps_by_plot", {}) or {}
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
        """Enumerate every plot subtab id available in the active data analysis recipe.

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

    # _apply_filter_rows moved to app/modules/t3_audit_engine.py (Phase 24-A, ADR-051)
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

            # Build synthetic data analysis recipe so viz_factory.render can be used.
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
            # ADR-085 (2026-08-10, amended): T1/T2 are always the untouched
            # reference — NEITHER exploration filters (applied_filters) NOR
            # committed audit nodes may affect them. Both only apply on
            # "My view" (T3). This is stricter than the original HOM-41 fix,
            # which gated only the committed audit nodes; testing showed
            # exploration filters had the identical leak.
            # ADR-086: plots follow "Plot to show" (plot_view), not the data view.
            # "T3" = My view, "CMP" = Compare (right pane is My view).
            in_my_view = safe_input(input, "plot_view", "T2") in ("T3", "CMP")
            filter_rows = (
                (list(applied_filters.get()) + _t3_filter_rows(this_subtab))
                if in_my_view else []
            )
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
            synthetic_data_analysis_recipe = {
                "plots": {p_id: plot_spec},
                "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
            }

            try:
                lf = _resolve_active_lf(spec, tier="T2")
            except Exception as e:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Data error: {e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9)
                ax.axis("off")
                return fig

            # Apply T3 drop_column nodes (audit-committed drops) — per-plot.
            # HOM-41 fix: T1/T2 must not see T3-committed drops either.
            if in_my_view:
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
                return viz_factory.render(lf, synthetic_data_analysis_recipe, p_id,
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

    # Phase 21-E / ADR-086: Baseline (T2) plot handlers for Comparison Mode.
    # Identical to the regular handlers but skip all exploration filters and T3
    # audit nodes — always shows the pure T2 result so the user can see what
    # their own changes did.
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
            # No exploration filters or T3 nodes — this is the T2 reference view
            synthetic_data_analysis_recipe = {
                "plots": {p_id: plot_spec},
                "plot_defaults": cfg.raw_config.get("plot_defaults", {}),
            }
            try:
                lf = _resolve_active_lf(spec, tier="T2")  # reference = T2 (ADR-086)
            except Exception as e:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Data error: {e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9)
                ax.axis("off")
                return fig

            try:
                return viz_factory.render(lf, synthetic_data_analysis_recipe, p_id)
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
    def _badge_ui(badge):
        """The view badge as HTML (issue #17): a small label, plus short remarks such as T2=T1.

        HTML next to the plot, never part of the image, so it is never exported.
        """
        return ui.div(
            ui.tags.span(badge.label, class_=f"badge spv-view-badge spv-view-badge-{badge.tier.lower()}"),
            *[ui.tags.span(note, class_="spv-view-note") for note in badge.notes],
            class_="spv-view-badge-row",
        )

    def _my_view_has_changes(subtab_id) -> bool:
        """An applied filter, or a committed filter or column drop for this plot (issue #17)."""
        return bool(applied_filters.get() or _t3_filter_rows(subtab_id) or _t3_drop_columns(subtab_id))

    def _make_plot_cell_handler(p_id: str):
        _acc_id = f"plot_acc_{p_id}"
        _panel_val = f"plot_panel_{p_id}"

        @output(id=f"plot_badge_{p_id}")
        @render.ui
        def _plot_badge_ui():
            """What the plot shows now (issue #17). Its own output, so that a filter change redraws only
            this small badge and never the plot. In Compare each pane already has its own label."""
            if not bootloader.is_enabled("interactivity_enabled"):
                return ui.div()
            view = safe_input(input, "plot_view", "T2")
            if view == "CMP":
                return ui.div()
            tier = "T3" if view == "T3" else "T2"
            spec = _resolve_active_spec(p_id)
            has_t2 = has_tier2_steps(active_cfg().raw_config, (spec or {}).get("target_dataset"))
            return _badge_ui(view_badge(tier, has_t2, _my_view_has_changes(f"subtab_{p_id}")))

        @output(id=f"plot_cell_{p_id}")
        @render.ui
        def _plot_cell_ui():
            # ADR-086: Compare is the third value of "Plot to show" (plot_view).
            in_comparison = (
                safe_input(input, "plot_view", "T2") == "CMP"
                and bootloader.is_enabled("comparison_mode_enabled")
            )

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
                            "T2 — Result (Reference)",
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
                content = ui.div(
                    ui.output_ui(f"plot_badge_{p_id}"),
                    ui.output_plot(f"plot_group_{p_id}", height="480px"),
                )

            return ui.accordion(
                ui.accordion_panel(
                    # No visible title (HOM-38): the tab above names the plot and the plot has its
                    # own title. The name stays for screen readers, visually hidden.
                    ui.span("Plot", class_="visually-hidden"),
                    content, value=_panel_val),
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
        Home renders exclusively from data analysis recipe analysis_groups.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")
        p = current_app_features.get()

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
            data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
            coll_id = active_collection_id()
            # ADR-024: Materialize to persistent session location
            anchor_dir = bootloader.get_location("user_data") / "anchors"
            if not anchor_dir.exists():
                anchor_dir.mkdir(parents=True, exist_ok=True)
            out_path = anchor_dir / f"{coll_id}.parquet"

            lf_full = orchestrator.materialize_tier1(
                data_analysis_recipe_id=data_analysis_recipe_id,
                collection_id=coll_id,
                output_path=out_path,
                keys=_data_analysis_recipe_keys(),
            )

        except Exception as e:
            return ui.div(ui.markdown(f"**Data Assembly Failed**: {e}"), class_="alert alert-danger")

        # Discover columns (retained for future filter scoping in Phase 21-F)
        all_cols = lf_full.collect_schema().names()  # noqa: F841

        cfg = active_cfg()
        groups = cfg.raw_config.get("analysis_groups", {})

        # --- UI-TITLE-1: data analysis recipe title banner ---
        # Resolution: app features ui_title.text override > data analysis recipe info.display_name > nothing.
        # If resolved title is empty or app features sets ui_title.visible=false: no banner.
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
                "In most data analysis recipes T1 = T2. Use this to compare against the processed result.",
            ),
            "T2": _tier_label(
                "Result",
                "T2 — Processed",
                "T2: Data with pipeline processing applied "
                "(e.g. range filters, long-format pivots, derived columns). "
                "Default view. If no processing steps are defined, T2 = T1.",
            ),
        }
        # ADR-085 amendment (2026-08-10): "My view" is now decoupled from audit
        # capability. It exists whenever Filters exist at all (interactivity_enabled,
        # checked by the caller of tier_choices below) — NOT gated on
        # t3_sandbox_enabled. Without t3_sandbox_enabled it's a pure scratchpad:
        # you can explore filters here, but there's no Send to Audit button and
        # no right sidebar to make anything permanent. With t3_sandbox_enabled,
        # the same view also gains the permanent-save path. Either way, T1 and
        # T2 stay untouched references — see the tier-isolation invariant.
        _my_view_desc = (
            "T3: Your personal adjustments — row filters and column drops "
            "applied on top of T2. Only affects your session."
            if bootloader.is_enabled("t3_sandbox_enabled") else
            "T3: Your personal adjustments — row filters and column drops "
            "applied on top of T2. Exploration only in this configuration — "
            "there is no audit trail to save changes permanently here."
        )
        tier_choices["T3"] = _tier_label("My view", "T3 — Filtered / Dropped", _my_view_desc)

        # STATIC-VIEW-1a: static app features files (interactivity_enabled=false) have no tier
        # switching — hide the strip entirely. T2 is the implicit default via the
        # _track_tier_toggle fallback (safe_input returns "T2" when input absent).
        if bootloader.is_enabled("interactivity_enabled"):
            # ADR-086: "Plot to show" is separate from "Data to show". Plots never show
            # T1; Compare (T2 vs My view) is the third value, gated by comparison_mode_enabled.
            plot_choices = {
                "T2": _tier_label(
                    "Result",
                    "T2 — Processed",
                    "Plots show the T2 result produced by the data analysis recipe. "
                    "If no processing steps are defined, T2 = T1.",
                ),
                "T3": _tier_label("My view", "T3 — Filtered / Dropped", _my_view_desc),
            }
            if bootloader.is_enabled("comparison_mode_enabled"):
                plot_choices["CMP"] = _tier_label(
                    "Compare",
                    "Result vs My view",
                    "Two plots side by side: the T2 result on the left, "
                    "your filtered view on the right.",
                )
            theater_header = ui.div(
                ui.div(
                    ui.tags.span(
                        "Plot to show:",
                        class_="fw-semibold me-3 spv-strip-label",
                    ),
                    ui.input_radio_buttons(
                        "plot_view",
                        label=None,
                        choices=plot_choices,
                        # Static default, as for tier_toggle: plot_view is read by the
                        # plot cells and handlers, never here, so changing it does not
                        # re-render dynamic_tabs.
                        selected="T2",
                        inline=True,
                    ),
                    class_="d-flex align-items-center",
                ),
                ui.div(
                    ui.tags.span(
                        "Data to show:",
                        class_="fw-semibold me-3 spv-strip-label",
                    ),
                    ui.input_radio_buttons(
                        "tier_toggle",
                        label=None,
                        choices=tier_choices,
                        # Default T2: in most data analysis recipes T2 = T1 so there is no cost,
                        # and data analysis recipes with processing steps show the intended result.
                        # Use static default — tier_toggle reactive value is NOT read here
                        # so that tier changes do NOT invalidate/re-render dynamic_tabs DOM.
                        # The _track_tier_toggle effect keeps tier_toggle reactive in sync.
                        selected="T2",
                        inline=True,
                    ),
                    class_="d-flex align-items-center",
                ),
                class_="theater-header-strip spv-header-strip-rows",
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
                            ui.output_text("home_data_preview_title", inline=True),
                            ui.output_ui("home_data_preview_badge", inline=True),
                            title="Preview the active plot dataset at the selected tier",
                            class_="me-3",
                        ),
                        # PREVIEW-ALLROWS-1: "Show all rows" toggle — off by default (100-row cap).
                        ui.input_switch("preview_all_rows", "All rows", value=False),
                        class_="d-flex align-items-center justify-content-between w-100 pe-3",
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
            # Attempt to fall back to top-level plots in the data analysis recipe
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
                    "Define analysis_groups (or top-level plots) in your data analysis recipe to populate this view.",
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

    # ADR-045 R1: anchor_path.set() must not live inside dynamic_tabs render.
    # This effect reacts to the same inputs and writes with an idempotent guard.
    @reactive.Effect
    def _sync_anchor_path():
        try:
            coll_id = active_collection_id()
            anchor_dir = bootloader.get_location("user_data") / "anchors"
            out_path = anchor_dir / f"{coll_id}.parquet"
            if out_path.exists():
                new_val = str(out_path)
                if anchor_path.get() != new_val:
                    anchor_path.set(new_val)
        except Exception:
            pass

    # Data change detection — runs as a side-effect separate from dynamic_tabs render.
    # Reads data_analysis_recipe_id to react when the user switches data analysis recipes; computes source file
    # hashes, compares to stored data_batch_hash, warns if changed, and always writes
    # data_analysis_recipe_sha256 + data_batch_hash into home_state for session_manager.
    @reactive.Effect
    def _sync_session_provenance():
        if home_state is None:
            return
        data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
        if not data_analysis_recipe_id:
            return
        try:
            from app.modules.session_manager import SessionManager as _SM
            from app.modules.session_manager import extract_primary_keys
            source_files = orchestrator.get_source_files(data_analysis_recipe_id)
            new_dbh = _SM.compute_data_batch_hash(source_files) if source_files else ""
            data_analysis_recipe_path = bootloader.get_location("data_analysis_recipes") / f"{data_analysis_recipe_id}.yaml"
            new_msig = _SM.compute_data_analysis_recipe_sha256(data_analysis_recipe_path) if data_analysis_recipe_path.exists() else ""
            new_pks = extract_primary_keys(active_cfg().raw_config)

            cur = home_state.get()
            prev_dbh = cur.get("data_batch_hash") or ""
            prev_msig = cur.get("data_analysis_recipe_sha256") or ""
            # Only warn if the SAME data analysis recipe's source files changed.
            # A data analysis recipe switch (different data_analysis_recipe_sha256) naturally has a
            # different data_batch_hash — that's expected, not an alert.
            same_data_analysis_recipe = prev_msig and prev_msig == new_msig
            if same_data_analysis_recipe and prev_dbh and prev_dbh != new_dbh:
                _notify(
                    "⚠️ Source data files for this project have changed — re-assembling.",
                    type="warning", duration=8,
                )
            needs_update = (
                cur.get("data_analysis_recipe_sha256") != new_msig
                or cur.get("data_batch_hash") != new_dbh
                or list(cur.get("primary_keys") or []) != list(new_pks)
            )
            if needs_update:
                home_state.set({
                    **cur,
                    "data_analysis_recipe_sha256": new_msig,
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
                        data_analysis_recipe_id=data_analysis_recipe_id,
                        data_analysis_recipe_sha256=new_msig,
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

    @output
    @render.ui
    def home_data_preview_badge():
        """What the data preview shows now (issue #17). Its own output: a filter change redraws only
        this badge, not the table. Reads the data view (tier_toggle) and the active plot."""
        if not bootloader.is_enabled("interactivity_enabled"):
            return ui.div()
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        has_t2 = has_tier2_steps(active_cfg().raw_config, (spec or {}).get("target_dataset"))
        return _badge_ui(view_badge(tier_toggle.get(), has_t2, _my_view_has_changes(subtab)))

    @output
    @render.text
    def home_data_preview_title():
        """Accordion title; states the 100-row cap unless 'All rows' is on. Reads only preview_all_rows (ADR-045 R4)."""
        if safe_input(input, "preview_all_rows", False):
            return "Data Preview"
        return "Data Preview (max. first 100 rows)"

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
            # ADR-085 (2026-08-10, amended): T1/T2 stay pure — neither exploration
            # filters nor committed audit nodes apply outside "My view" (T3).
            in_t3_preview = tier_toggle.get() == "T3"
            _preview_rows = (
                (list(applied_filters.get()) + _t3_filter_rows())
                if in_t3_preview else []
            )
            lf = _apply_filter_rows(lf, _preview_rows)
            # Apply T3 drop_column nodes — committed audit drops (T3 only).
            if in_t3_preview:
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
            # HOM-41 fix: T3-committed drops must not remove columns from the
            # T1/T2 selector — those tiers are unaffected by the audit trail.
            committed_drops = set(_t3_drop_columns()) if tier_toggle.get() == "T3" else set()
            cols = [c for c in lf.collect_schema().names() if c not in committed_drops]
            in_t3 = tier_toggle.get() == "T3"
            # Dropping via audit only exists with audit capability (ADR-085).
            label_text = (
                "Columns (drop unselected via audit):"
                if in_t3 and bootloader.is_enabled("t3_sandbox_enabled")
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
    def data_analysis_recipe_info_ui():
        """Info of the open data analysis recipe: its info: block as written, nested keys indented.
        Reads active_cfg only, so a switch of data analysis recipe refreshes this slot and not the sidebar."""
        from app.modules.data_analysis_recipe_info import info_lines
        try:
            lines = info_lines((active_cfg().raw_config or {}).get("info"))
        except Exception:
            lines = []
        if not lines:
            return ui.div(ui.tags.small("No info in this data analysis recipe.", class_="text-muted"), class_="p-1")
        return ui.div(
            *[
                ui.div(
                    ui.tags.small(label, class_="text-muted"),
                    *([ui.tags.small(": " + value)] if value is not None else []),
                    style=f"margin-left:{depth * 12}px;",
                    class_="data-analysis-recipe-info-line",
                )
                for depth, label, value in lines
            ],
            class_="p-1",
        )

    @output
    @render.ui
    def col_drop_audit_btn_ui():
        """Live count of deselected columns — re-renders on selection change.

        Kept SEPARATE from home_col_selector_ui so reading the selector input
        here does not invalidate the selectize component itself.
        """
        # ADR-085: without t3_sandbox_enabled, My view is a scratchpad with no audit
        # trail, so there is nothing to send drops to — no button.
        if tier_toggle.get() != "T3" or not bootloader.is_enabled("t3_sandbox_enabled"):
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
        perm = current_app_features.get()
        print(f"DEBUG: Rendering sidebar_nav_ui for App features: {perm}")

        nav_items = [ui.nav_panel("Home", value="Home")]

        # APP_FEATURES-1 (2026-04-30): gates consult the app features feature-flag system
        # via bootloader.is_enabled(...) instead of hardcoded app features names. This
        # matches the design intent of .claude/rules/rules_app_features_flags.md
        # — flags like gallery_enabled are documented as INDEPENDENT and can be
        # flipped per app features file in config/app_features/ without touching code here.
        if bootloader.is_enabled("blueprint_enabled"):
            nav_items.append(ui.nav_panel("Blueprint Architect", value="Wrangle Studio"))

        if bootloader.is_enabled("test_lab_enabled"):
            nav_items.append(ui.nav_panel("Test Lab", value="Test Lab"))

        if bootloader.is_enabled("gallery_enabled"):
            nav_items.append(ui.nav_panel("Gallery", value="Gallery"))

        badge = (
            ui.h6(f"Active: {perm.replace('_', ' ').title()}",
                  class_="text-muted px-2 py-1 mb-1 border-bottom spv-text-meta")
            if bootloader.is_enabled("show_app_features_badge")
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

    # 4. Sidebar Tools (Contextual Data analysis recipe Workbench)
    @output(id="sidebar_tools_ui")
    @render.ui
    def sidebar_tools_ui():
        """
        Relocated Sidebar Management (ADR-038).
        Enforces dedicated App features based control clusters.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")

        # Gallery (ADR-057: filter + example selector moved here from internal sidebar)
        # notification_log lives in the RIGHT sidebar only (ADR-073 slot registry) —
        # do not also mount it here, it duplicates the id and races with the right
        # sidebar's copy (REG-10).
        if active_sidebar == "Gallery":
            return ui.div(
                gallery_viewer.build_sidebar_ui(),
            )

        # Data analysis recipe Workbench (Wrangle Studio)
        if active_sidebar == "Wrangle Studio":
            return ui.div(
                ui.accordion(
                    ui.accordion_panel(
                        "🗂️ Master data analysis recipe",
                        ui.input_select("stored_data_analysis_recipe_selector", None,
                                        choices=["Scanning config/..."]),
                        ui.input_action_button(
                            "btn_bp_new_data_analysis_recipe", "+ New",
                            class_="btn-outline-primary btn-sm w-100 mt-1",
                        ),
                        ui.tags.small(
                            "Select a data analysis recipe. Click any node in the TubeMap to navigate.",
                            class_="text-muted d-block mt-1"),
                        ui.output_ui("bp_draft_status_ui"),
                        icon=ui.tags.i(class_="bi bi-diagram-3")
                    ),
                    ui.accordion_panel(
                        "📝 Data analysis recipe Info",
                        ui.output_ui("bp_meta_form_ui"),
                        icon=ui.tags.i(class_="bi bi-info-square")
                    ),
                    ui.accordion_panel(
                        "📋 Groups & Plots",
                        ui.output_ui("bp_groups_inventory_ui"),
                        icon=ui.tags.i(class_="bi bi-collection")
                    ),
                    ui.accordion_panel(
                        "📤 External Exchange",
                        ui.input_file("data_analysis_recipe_uploader", "Select YAML...",
                                      accept=[".yaml"], multiple=False),
                        ui.input_action_button("btn_upload_replace", "📥 Upload (Replace)",
                                               class_="btn-info btn-sm w-100 mb-1"),
                        ui.input_action_button("btn_upload_append", "➕ Upload & Append",
                                               class_="btn-outline-primary btn-sm w-100"),
                        ui.hr(),
                        ui.download_button("btn_download_data_analysis_recipe", "💾 Download/Export",
                                           class_="btn-outline-primary w-100"),
                        icon=ui.tags.i(class_="bi bi-cloud-arrow-up")
                    ),
                    ui.accordion_panel(
                        "🔍 Validate",
                        ui.output_ui("bp_validate_ui"),
                        icon=ui.tags.i(class_="bi bi-check-circle")
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
                    ui.input_action_button("btn_import_data_analysis_recipe", "Import",
                                           class_="btn-info btn-sm"),
                    ui.input_action_button("btn_save_internal", "Save",
                                           class_="btn-success btn-sm"),
                    style="display:none;",
                    id="blueprint_hidden_controls"
                ),
                # notification_log lives in the RIGHT sidebar only (ADR-073) — see REG-10.
            )

        # Standard Operation Sidebar (Home — ADR-043 / ADR-073)
        # Build data analysis recipe state needed by some panel renderers.
        try:
            data_analysis_recipe_choices = list(bootloader.available_data_analysis_recipes.keys())
            default_data_analysis_recipe = bootloader.get_default_data_analysis_recipe()
        except Exception:
            data_analysis_recipe_choices = []
            default_data_analysis_recipe = None

        with reactive.isolate():
            _current_data_analysis_recipe = _last_data_analysis_recipe_id.get() or default_data_analysis_recipe

        # Panel renderer map: type → callable() → accordion_panel | None
        # None means the panel type was handled (e.g. notification_log goes outside accordion).
        def _render_data_analysis_recipe_info():
            """Info panel shell. Only mounts a slot: the content is its own output so that reading the
            the data analysis recipe here would not re-render (and destroy) the whole sidebar (shell stability pattern)."""
            return ui.accordion_panel(
                "Info",
                ui.output_ui("data_analysis_recipe_info_ui"),
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

        def _render_data_analysis_recipe_choice():
            return ui.accordion_panel(
                "Data analysis recipe Choice",
                ui.div(
                    ui.input_select("data_analysis_recipe_id", "Data analysis recipe",
                                    choices=data_analysis_recipe_choices,
                                    selected=_current_data_analysis_recipe),
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

        _left_panel_renderers = {
            "data_analysis_recipe_info":       _render_data_analysis_recipe_info,
            "deployment_info":    _render_deployment_info,
            "data_analysis_recipe_choice":    _render_data_analysis_recipe_choice,
            "filters":            _render_filters,
            "data_import":        _render_data_import,
            "export":             _render_export,
            "session_management": _render_session_management,
        }

        def _build_left_sidebar(workspace_key: str, open_panels: list[str]):
            """Build the left sidebar accordion from a workspace's slot list (ADR-073).

            Shared by Home and Test Lab. Blueprint and Gallery still build their own
            sidebar directly (above) rather than going through the slot registry — see
            finding F-01 in .claude/tasks/uml_findings.md: that split is not yet settled.
            """
            sidebar_cfg = bootloader.get_sidebar_config(workspace_key, "left")
            panels = []
            include_notification_log = False
            for slot in sidebar_cfg.panels:
                ptype = slot.get("type", "")
                if ptype == "notification_log":
                    include_notification_log = True
                    continue
                if not is_panel_active(ptype, bootloader):
                    continue
                renderer = _left_panel_renderers.get(ptype)
                if renderer is None:
                    print(f"[home_theater] No renderer for panel type '{ptype}' — skipping.")
                    continue
                panel = renderer()
                if panel is not None:
                    panels.append(panel)
            return ui.div(
                ui.accordion(
                    *panels,
                    id="nav_accordion",
                    multiple=True,
                    open=open_panels,
                ),
                ui.output_ui("notification_log_panel_ui") if include_notification_log else ui.div(),
            )

        if active_sidebar == "Test Lab":
            return _build_left_sidebar("test_lab", open_panels=[])

        _has_data_analysis_recipe = bootloader.get_data_analysis_recipe_selector().get("visible", True)
        open_panels = ["Data analysis recipe Choice"] if _has_data_analysis_recipe else []
        return _build_left_sidebar("home", open_panels=open_panels)

    # --- Right Sidebar Context Matrix (ADR-039 / ADR-044) ---
    @output
    @render.ui
    def right_sidebar_content_ui():
        """
        Context-sensitive right sidebar (ADR-039).
        Switches content based on the active module.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")

        # --- Blueprint Architect (Wrangle Studio) ---
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
                # VIZFAC-BLUEPRINT-FORM-1: plot_defaults editor (data analysis recipe root node)
                ui.card(
                    ui.card_header(
                        ui.div(ui.h5("Plot Defaults", class_="mb-0"),
                               class_="d-flex justify-content-center w-100")
                    ),
                    ui.output_ui("bp_plot_defaults_form_ui"),
                    class_="mb-2 shadow-sm border-0"
                ),
            ]
            # BP-BRANCH-NODE-1: Branch Node card (data_analysis_recipe_edit_enabled only)
            if bootloader.is_enabled("data_analysis_recipe_edit_enabled"):
                parts.append(
                    ui.card(
                        ui.card_header(
                            ui.div(ui.h5("Branch Node", class_="mb-0"),
                                   class_="d-flex justify-content-center w-100")
                        ),
                        ui.output_ui("bp_branch_ui"),
                        class_="mb-2 shadow-sm border-0"
                    )
                )
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
            # REG-10 fix: notification_log sourced from the slot registry here
            # (blueprint_standard_right.yaml) — no longer hardcoded in the left sidebar.
            blueprint_right_cfg = bootloader.get_sidebar_config("blueprint", "right")
            blueprint_right_types = {s.get("type", "") for s in blueprint_right_cfg.panels}
            if "notification_log" in blueprint_right_types:
                parts.append(ui.output_ui("notification_log_panel_ui"))
            return ui.div(*parts, class_="sidebar-content p-0 d-flex flex-column h-100")

        # --- Home Theater (ADR-043 / ADR-044 / ADR-073) ---
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
                        ui.output_ui("audit_pending_badge_ui"),
                        ui.output_ui("audit_nodes_header_ui"),
                        # PROP-2: effective filter summary (sidebar + T3 nodes)
                        ui.output_ui("filter_inventory_ui"),
                        ui.h6("Inherited (Tier 2)", class_="text-muted spv-label-caps"),
                        ui.output_ui("audit_nodes_tier2"),
                        ui.hr(class_="spv-divider"),
                        ui.output_ui("audit_nodes_tier3"),
                        class_="p-2 spv-scroll-flex",
                    ),
                    class_="mb-2 shadow-sm border-0 d-flex flex-column spv-flex-1-auto",
                ))
                parts.append(ui.output_ui("audit_stack_tools_ui"))
                # The "Plot Style" panel (aesthetic_style_panel_ui, defined in audit_stack.py) is NOT
                # mounted: letting users change in HOME what the data analysis recipe defines is too much for
                # now, and using it broke the plot (test plan HOM-47). Its code is kept, unused, as
                # an eventual enhancement (fork issue #15). To bring it back, add
                # parts.append(ui.output_ui("aesthetic_style_panel_ui")) here, after fixing HOM-47.

            if "notification_log" in right_types:
                parts.append(ui.output_ui("notification_log_panel_ui"))

            if not parts:
                return ui.div(class_="sidebar-content p-0")

            return ui.div(*parts, class_="sidebar-content p-0 d-flex flex-column h-100")

        # --- Gallery ---
        if active_sidebar == "Gallery":
            gallery_parts = [
                ui.card(
                    ui.card_header(ui.h5("Gallery Explorer", class_="mb-0 text-center")),
                    ui.div(
                        ui.p("📚 Browse visual examples.", class_="text-muted small p-2"),
                        ui.p("Select an example to copy its YAML into the Architect sandbox.",
                             class_="text-muted small px-2"),
                        class_="p-1"
                    ),
                    class_="mb-2 shadow-sm border-0"
                ),
            ]
            # REG-10 fix: notification_log sourced from the slot registry here
            # (gallery_focus_right.yaml) — no longer hardcoded in the left sidebar.
            gallery_right_cfg = bootloader.get_sidebar_config("gallery", "right")
            gallery_right_types = {s.get("type", "") for s in gallery_right_cfg.panels}
            if "notification_log" in gallery_right_types:
                gallery_parts.append(ui.output_ui("notification_log_panel_ui"))
            return ui.div(*gallery_parts, class_="sidebar-content p-0")

        # --- Test Lab ---
        if active_sidebar == "Test Lab":
            return ui.div(
                ui.accordion(
                    ui.accordion_panel(
                        "ID Reconciliation",
                        ui.tags.small(
                            "Match and align ID columns across related files before "
                            "assembling a pipeline.",
                            class_="text-muted d-block p-1",
                        ),
                        icon=ui.tags.i(class_="bi bi-link-45deg"),
                    ),
                    ui.accordion_panel(
                        "Data analysis recipe Scaffolding",
                        ui.tags.small(
                            "Generate boilerplate pipeline data analysis recipe from uploaded files.",
                            class_="text-muted d-block p-1",
                        ),
                        icon=ui.tags.i(class_="bi bi-file-earmark-code"),
                    ),
                    ui.accordion_panel(
                        "Synthetic Data",
                        ui.tags.small(
                            "Generate demo or stress-test datasets from a schema or "
                            "example file.",
                            class_="text-muted d-block p-1",
                        ),
                        icon=ui.tags.i(class_="bi bi-table"),
                    ),
                    ui.accordion_panel(
                        "Anonymisation",
                        ui.tags.small(
                            "Replace real IDs with consistent synthetic equivalents. "
                            "Reversible via BLUEPRINT join.",
                            class_="text-muted d-block p-1",
                        ),
                        icon=ui.tags.i(class_="bi bi-person-lock"),
                    ),
                    ui.accordion_panel(
                        "File Reformatting",
                        ui.tags.small(
                            "Convert XLSX (multi-sheet) and CSV files to TSV.",
                            class_="text-muted d-block p-1",
                        ),
                        icon=ui.tags.i(class_="bi bi-arrow-left-right"),
                    ),
                    id="test_lab_sidebar_accordion",
                    open=False,
                ),
                class_="sidebar-content p-0",
            )

        # --- Default fallback ---
        return ui.div(
            ui.p("—", class_="text-muted p-3 text-center"),
            class_="sidebar-content p-0"
        )

    # ── PROP-2: Filter Inventory Panel ────────────────────────────────────────
    # Effective filter summary for the active plot: combines applied_filters
    # (global left-sidebar rows) with T3 filter/exclusion nodes for this plot.
    # Read-only — no state writes. Per-filter tooltips carry full detail.

    @output
    @render.ui
    def filter_inventory_ui():
        filters = applied_filters.get()
        t3_nodes: list[dict] = []
        active_sub = ""
        if home_state is not None:
            state = home_state.get()
            active_sub = state.get("active_plot_subtab", "")
            by_plot = state.get("t3_audit_steps_by_plot", {}) or {}
            t3_nodes = [
                n for n in by_plot.get(active_sub, [])
                if n.get("active", True)
                and n.get("node_type") in ("filter_row", "exclusion_row")
            ]

        if not filters and not t3_nodes:
            return ui.div()

        _OP = {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
               "lt": "<", "le": "≤", "in": "∈", "not_in": "∉"}

        def _fmt_val(v) -> str:
            if isinstance(v, (list, tuple)):
                items = [str(x) for x in v]
                suffix = f", +{len(items) - 3}" if len(items) > 3 else ""
                return "{" + ", ".join(items[:3]) + suffix + "}"
            s = str(v)
            return s if len(s) <= 24 else s[:24] + "…"

        _ROW = (
            "display:flex;align-items:center;gap:4px;"
            "font-size:0.75rem;padding:1px 4px;"
        )
        _BADGE_SB = (
            "font-size:0.65rem;padding:0 3px;border-radius:3px;"
            "background:#eef0fb;color:#345beb;margin-left:auto;white-space:nowrap;"
        )
        _BADGE_T3 = (
            "font-size:0.65rem;padding:0 3px;border-radius:3px;"
            "background:#e6f7f5;color:#0b6358;margin-left:auto;white-space:nowrap;"
        )
        _MONO = (
            "font-family:ui-monospace,SFMono-Regular,Menlo,monospace;"
            "flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
        )

        rows: list = [ui.div(
            "Active Filters",
            class_="spv-text-xs text-muted fw-bold",
            style="padding:2px 4px 1px;",
        )]
        for f in filters:
            col = f.get("column", "?")
            op  = _OP.get(f.get("op", "eq"), f.get("op", "eq"))
            val = _fmt_val(f.get("value", ""))
            rows.append(ui.tooltip(
                ui.div(
                    ui.span(f"🔍 {col} {op} {val}", style=_MONO),
                    ui.span("sidebar", style=_BADGE_SB),
                    style=_ROW,
                ),
                f"Source: sidebar | {col} {f.get('op')} {f.get('value')}",
                placement="left",
            ))
        for n in t3_nodes:
            nt  = n.get("node_type", "")
            p   = n.get("params", {})
            col = p.get("column", "?")
            op  = _OP.get(p.get("op", "eq"), p.get("op", "eq"))
            val = _fmt_val(p.get("value", ""))
            icon   = "🚫" if nt == "exclusion_row" else "🔍"
            pk_pfx = "⚠️" if n.get("primary_key_warning") else ""
            reason = (n.get("reason") or "").strip() or "no reason yet"
            rows.append(ui.tooltip(
                ui.div(
                    ui.span(f"{pk_pfx}{icon} {col} {op} {val}", style=_MONO),
                    ui.span("T3", style=_BADGE_T3),
                    style=_ROW,
                ),
                f"T3 audit | Reason: {reason}",
                placement="left",
            ))

        return ui.div(
            *rows,
            style="padding:2px 0 4px;border-bottom:1px solid #e9ecef;",
        )

    # ── UX-NOTIF-1: Persistent Alert Log ──────────────────────────────────────
    @output
    @render.ui
    def notification_log_panel_ui():
        """Render the last-20 notifications as a collapsible accordion in the right sidebar."""
        _type_color = {
            "success": "#10a395",
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
        current_app_features=current_app_features,
        active_cfg=active_cfg,
        tier1_anchor=tier1_anchor,
        tier_toggle=tier_toggle,
        home_state=home_state,
        safe_input=safe_input,
        active_home_subtab=active_home_subtab,
        notification_log=notification_log,
        session_pipeline_errors=session_pipeline_errors,
        t3_filter_rows=_t3_filter_rows,
        t3_drop_columns=_t3_drop_columns,
        view_keys=_data_analysis_recipe_keys,
    )

    # ── 22-D: Session Management Panel ────────────────────────────────────────
    # session_management_ui + _handle_session_import + _handle_session_actions
    # + _restore_session moved to app/handlers/session_handlers.py
    # (Phase 24-B, ADR-051). Imported at module top.
    define_session_server(
        input, output, session,
        session_manager=session_manager,
        current_app_features=current_app_features,
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

