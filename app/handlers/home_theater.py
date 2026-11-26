# engine: python-plotnine+python-polars (the HOME handlers; draws placeholder figures with matplotlib itself and holds Polars tables)
"""app/handlers/home_theater.py
Home Theater Shiny wiring (ADR-043 / ADR-044 / ADR-045).

Entry point:
    define_server(input, output, session, *,
                  bootloader, wrangle_studio, dev_studio,
                  orchestrator, viz_factory, gallery_viewer,
                  current_app_features, anchor_path, tier1_anchor,
                  active_cfg,
                  active_collection_id, safe_input, active_home_subtab, home_mode, data_view, source_table,
                  home_state=None, session_manager=None)

Slice 3a (shown item): in Audit mode the table of the preview, its title, badge, column chooser, filter form and key is the item SHOWN from "Path of the data" (`shown_item`); "Table to view" is Exploration only.

Concern: dynamic_tabs, sidebar_nav_ui, sidebar_tools_ui,
         right_sidebar_content_ui, home_data_preview/col_selector,
         col_drop_audit_btn_ui. Slice B (D-0310, D-0311): the mode switch "Exploration | Audit" (only with the audit on) and the data
         choice "Source | T1 | T2 | T3" replace the two old choices of the header strip.
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
# provides: function:define_server (home_theater), output:dynamic_tabs, output:home_data_preview, output:home_col_selector_ui, output:col_drop_audit_btn_ui, output:sidebar_nav_ui, output:sidebar_tools_ui, output:right_sidebar_content_ui, output:plot_cell_{p_id} (per-plot); HELP-INLINE-1: btn_help_ws + _show_workspace_help; 22-J-10: mounts aesthetic_style_panel_ui slot; PROP-2: output:filter_inventory_ui, output:source_table_ui, output:mode_caption_ui, output:compare_switch_ui, output:plot_cmp_label_{p_id}, output:plot_badge_{p_id}, output:plot_reshuffle_{p_id} (Audit mode only, D-0341), output:data_strip_ui (Table to view, Exploration only, slice 3a), output:shown_band_ui (the band of the shown item, slice 3a), effect:_forget_shown_item, effect:_tab_shows_its_plot, effect:_track_view_inputs, effect:_drive_right_panel, effect:_open_audit_mode_after_restore, effect:_sync_active_space (the open user space as a value of its own, D-0502), constant:LEGACY_RECORD_NOTICE
# consumes: app/modules/audit_place_view.py (viewed, table_for, view_identity, Readers: the ONE reader of the table shown in Audit mode, slice 3a), app/modules/audit_shown.py (band_lines, others_chosen, shown_node_of_tab), app/modules/lineage_view.py (line_text: the name of a place), libs/utils/src/utils/lineage_data.py (lineage_of), libs/utils/src/utils/filter_words.py (value_text, no_value_words: the words of a filter step, one function), app/handlers/lineage_handlers.py (the lineage panel it mounts: output lineage_panel_ui), app/modules/plan_composer.py (compose_plan_book: the engine's plan of the open recipe, for the rule of a key drop), app/modules/orchestrator.py (plot_read_error_text, read_source: the Source view, D-0310), app/modules/wrangle_studio.py, app/modules/test_lab_studio.py, app/modules/gallery_viewer.py, libs/viz_factory/src/viz_factory/viz_factory.py (render, show_draw_errors), libs/utils/src/utils/config_loader.py, app/modules/t3_audit_engine.py (_apply_filter_rows, stored_table_identity, source_table_identity, rows_built_on, view_key, viewed_table), app/modules/audit_places.py (nodes_reaching_plot, own_plot_place, place_nodes: the audit steps of a plot at every tier), app/modules/audit_view.py (PlaceAudit, AUDIT_ERRORS: the audit copy that gives every audited table), app/modules/view_badge.py (view_badge, plot_badge, has_plot_steps, has_tier2_steps, PREVIEW_ROW_LIMIT), libs/utils/src/utils/recipe_graph.py (build_graph, source_tables_of_plot), app/modules/session_manager.py (LegacySessionError), app/modules/plot_seeds.py, app/modules/sidebar_registry.py, app/modules/sidebar_open_panels.py (open_panels_after_redraw: the left panels the user has open stay open, D-0502), app/handlers/session_handlers.py, app/handlers/export_handlers.py, app/handlers/filter_and_audit_handlers.py, app/handlers/data_import_handlers.py
#              libs/utils/src/utils/pipeline_error.py (PipelineError — DIAG-RUNTIME-AUDIT-1, via session.on_flushed capture)
# consumes: app/src/www/preview_switch.js (the "All rows" switch it mounts in the header of the data panel needs this script so that a click does not fold the panel; mounted by app/src/ui.py)
# consumes: app/modules/frame_widths.py (right_panel_open: the right panel follows the mode, D-0375, D-0385; HOME, BLUEPRINT: the nav values)
# consumes: app/handlers/opening_handlers.py (define_server: the opening of the recipe; opening_waits), app/handlers/id_warning_handlers.py (define_server: the red warning of the ids), app/modules/opening_build.py (opening_signature, plot_render_recipe: the recipe handed to the plot engine, D-0237, D-0239), libs/utils/src/utils/engines.py (plot_engine_slot, through it)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-043, .claude/knowledge/architecture_decisions.md#ADR-044, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/knowledge/architecture_decisions.md#ADR-047, .claude/knowledge/architecture_decisions.md#ADR-051, .claude/knowledge/architecture_decisions.md#ADR-073, .claude/knowledge/architecture_decisions.md#ADR-085, .claude/knowledge/architecture_decisions.md#ADR-094, .claude/knowledge/architecture_decisions.md#ADR-097, .claude/knowledge/architecture_decisions.md#ADR-099, .claude/rules/ui_implementation_contract.md#4, .claude/rules/ui_implementation_contract.md#5
# @end_deps

import re
import secrets
from pathlib import Path
from types import SimpleNamespace

import polars as pl
from shiny.types import SilentException
from shiny import reactive, render, ui
from shiny.session import session_context
from app.modules import frame_widths
from app.modules.error_notice import notice
from app.modules.recipe_banner import recipe_banner_title
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.data_change_notice import inputs_changed_during_build_notice, notice_after_data_change
from app.modules.data_analysis_recipe_validator import rejected_recipe_text
from app.modules.orchestrator import InputsChanged, plot_read_error_text
from app.modules.view_badge import PREVIEW_ROW_LIMIT, row_count_note, has_plot_steps, has_tier2_steps, plot_badge, view_badge
from app.modules.opening_build import opening_signature, plot_render_recipe
from app.modules.plan_composer import PlanComposerBug, compose_plan_book, plan_book_for_the_gate
from app.modules.audit_places import nodes_reaching_plot, nodes_signature, own_plot_place, place_nodes
from app.modules.audit_view import AUDIT_ERRORS, PlaceAudit
from app.modules.audit_place_view import AUDIT, AUDITED, Readers, Viewed, columns_digest, table_for, view_identity, viewed as viewed_item
from app.modules.audit_shown import band_lines, others_chosen, shown_node_of_tab
from app.modules.lineage_view import line_text
from app.handlers.id_warning_handlers import define_server as define_id_warning_server
from app.handlers.opening_handlers import define_server as define_opening_server, opening_cover_text, opening_waits
from utils.pipeline_error import capture_entry
from app.modules.plot_seeds import RESHUFFLE_TITLE, reshuffle_offered, seed_caption, seed_in_use
from viz_factory.viz_factory import show_draw_errors

from app.modules.t3_audit_engine import (
    _apply_filter_rows, rows_built_on, source_table_identity, stored_table_identity,
    view_key, viewed_table)
from utils.recipe_graph import RecipeGraphError, build_graph, source_tables_of_plot
from utils.lineage_data import lineage_of
from utils.filter_words import no_value_words, value_text
from utils.na_choice import na_of
from app.modules.sidebar_registry import is_panel_active
from app.modules.sidebar_open_panels import open_panels_after_redraw
from app.handlers.session_handlers import define_session_server
from app.handlers.export_handlers import define_export_server
from app.handlers.filter_and_audit_handlers import define_filter_audit_server
from app.handlers.lineage_handlers import define_server as define_lineage_server
from app.handlers.data_import_handlers import define_data_import_server

# ADR-096: same check as main.py's docs_available — duplicated here, not imported, to
# avoid a circular import (main.py imports server, which imports this module).
_DOCS_AVAILABLE = (Path(__file__).parent.parent.parent / "docs" / "_site").exists()
_GITHUB_REPO_URL = "https://github.com/evezeyl/SPARMVET_VIZ"

# PROVISIONAL (the coordinator's text, D-0312; the owner reads it): told when the record of a session cannot be written because an older session
# with the same recipe and data is stored (`LegacySessionError`). The old session is listed in the Session panel as refused, with a Delete button.
LEGACY_RECORD_NOTICE = (
    "This session cannot be recorded yet: an older session with the same recipe and data is stored. Open the Session panel and delete the "
    "session marked as saved by an older version, then change the recipe or data box again.")

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


def group_tab_label(group_id: str, group: dict) -> str:
    """The text of a group tab: its `ui_label`. The recipe check requires it (G01), so no other text is invented here (D-0409)."""
    return group["ui_label"]


def plot_tab_label(p_id: str, entry: dict) -> str:
    """The text of a plot tab: its `ui_label`. The recipe check requires it (P01), so no other text is invented here (D-0409)."""
    return entry["ui_label"]


def plot_list_label(p_id: str, entry: dict | None) -> str:
    """The name of a plot in a list of the audit dialogs: its `ui_label`, else the plot id as written (a plot that is not in the recipe has no entry)."""
    return (entry or {}).get("ui_label") or p_id


def _collect_all_group_plot_ids(bootloader) -> list[tuple[str, dict]]:
    """Enumerate all (plot_id, plot entry) pairs from analysis_groups AND top-level plots.

    The entry is the plot content (D-0237): `target_dataset`, `mapping`, `layers` are written in it, with the app-side keys beside them.
    Called once at server init to register dynamic @render.plot handlers.
    Returns list of (p_id, entry) tuples.
    """
    seen = set()
    results = []
    # every discovered recipe, not only the ones that passed the gate at start: one that fails now and is repaired later
    # must find its plot slots (GATE-GAP-1); a recipe that does not load is skipped below
    for data_analysis_recipe_id, data_analysis_recipe_path in bootloader.discovered_data_analysis_recipes.items():
        try:
            cfg = load_data_analysis_recipe(data_analysis_recipe_path).config
            # Collect from analysis_groups
            groups = cfg.raw_config.get("analysis_groups", {})
            for _gid, gspec in groups.items():
                for p_id, plot_entry in gspec.get("plots", {}).items():
                    if p_id not in seen:
                        seen.add(p_id)
                        results.append((p_id, plot_entry))
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
                  active_home_subtab, home_mode, data_view, source_table,
                  home_state=None, session_manager=None,
                  data_refresh_trigger=None,
                  notification_log=None,
                  session_processing_issues=None,
                  recipe_gate_version=None, shown_recipe=None,
                  gallery_state=None):
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
    home_mode : reactive.Value[str]
        "exploration" or "audit" (D-0016). Audit exists only with `t3_sandbox_enabled`; PROVISIONAL P-B7 (name).
    data_view : reactive.Value[str]
        The data choice: "SRC" (Source), "T1", "T2" or "T3" (D-0310). PROVISIONAL P-B1: it starts on "T3", the table the plot shows.
    source_table : reactive.Value[str | None]
        The source table the Source choice shows (one of the tables that feed the open plot); None until the user picks one.
    home_state : reactive.Value[dict] | None
        §13 Home Module State Object — survives all panel switches.
        Contains t3_audit_steps, applied_filters and navigation state. The mode and the data choice are not in it (D-0312).
    session_manager : SessionManager | None
        §12d Session ghost save/restore manager.
    session_processing_issues : reactive.Value[list] | None
        DIAG-RUNTIME-AUDIT-1: accumulates structured runtime error entries.
    recipe_gate_version : reactive.Value[int] | None
        The version of the load gate (GATE-GAP-1); the opening of a recipe moves it when it refuses the recipe (D-0326).
    shown_recipe : reactive.Value | None
        The recipe HOME shows in this session; the opening writes the recipe it opens, so the gate follower can name it when it is refused on the first screen.
    """

    from app.modules.notification_utils import make_notifier
    _notify = make_notifier(notification_log)

    # How many tables were built and returned without being stored since the app started (inputs changed during the build). A table
    # returned and not stored has no file that carries a key for it, so the filter form cannot tell its rows from another table's
    # by a key: the count is part of the identity it reads (`t3_audit_engine.stored_table_identity`), so a later table differs.
    _unstored_builds = [0]

    # What the opening of the open recipe finished: {"signature", "status"}; written by `opening_handlers` (an effect), read by `dynamic_tabs`.
    opening_state = reactive.Value({})
    # What the checks of the ids found for the open recipe (D-0582): written by `opening_handlers`, read by `id_warning_handlers` (the red warning of HOME).
    id_run_state = reactive.Value(None)

    def _tell_inputs_changed(change):
        """The orchestrator built a table while its recipe or data changed (STALE-KEY-STORE-1): say so, in the form of the
        data-change notice. Told after the flush, under isolate: the tables are built inside renders, which may not write
        the Alerts log (R1). Nothing is re-read and nothing is blocked."""
        _unstored_builds[0] += 1
        text = "⚠️ " + inputs_changed_during_build_notice(change.text)

        def show():
            with session_context(session), reactive.isolate():
                _notify(text, type="warning", duration=12)

        session.on_flushed(show, once=True)

    # A plot's error or warning goes to the Processing issues table and to the Alerts panel, once, after the flush and under
    # reactive.isolate() (a render may not write a reactive value; app/modules/plot_issue_reporter.py). VIZ-STANDARD-1, V7.
    from app.modules.plot_issue_reporter import make_issue_reporter, plot_warning_text
    _report_issue = make_issue_reporter(session, session_processing_issues, notification_log)

    def _report_plot_exception(exc, component, location):
        _report_issue(capture_entry(exc, component, location), str(exc), "error")

    def _report_plot_warning(warning):
        _report_issue(warning.with_timestamp().to_audit_row(), plot_warning_text(warning), "warning")

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
    # issue #38: get_default_data_analysis_recipe() raises when zero recipes are usable.
    # This line runs once per session, eagerly, outside any @render/@reactive try/except —
    # unlike every other call site below, an uncaught raise here kills session setup itself
    # (no page renders at all, only a terminal traceback). Use the _or_none variant so the
    # empty-recipes state reaches dynamic_tabs()/sidebar_tools_ui() as data, not an exception.
    _last_data_analysis_recipe_id = reactive.Value(bootloader.get_default_data_analysis_recipe_or_none())

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
                spec = gspec["plots"][p_id]
                break
        if spec is None and p_id and p_id in top_plots:
            spec = top_plots[p_id]
        if spec is None:
            for _gid, gspec in groups.items():
                for _pid, pentry in gspec.get("plots", {}).items():
                    spec = pentry
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
        """Return the T1 LazyFrame for spec, whatever the data choice."""
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
                on_inputs_changed=_tell_inputs_changed,
            )
        return tier1_anchor()

    def _plot_id_of(spec: dict | None) -> str | None:
        """The id of the plot entry `spec` is (the very entry of the open recipe), or None when it is no entry of it."""
        for gspec in active_cfg().raw_config.get("analysis_groups", {}).values():
            for pid, entry in (gspec.get("plots") or {}).items():
                if entry is spec:
                    return pid
        return None

    def _recipe_raw() -> dict:
        """The resolved dictionary of the open recipe, for the rule of a key drop (`utils.key_drop`, by place, D-0358). Read without a reactive dependency: the handlers that
        ask it run on an event."""
        with reactive.isolate():
            return active_cfg().raw_config

    _plans_memo: dict = {}

    def _recipe_plans():
        """The engine's plan book of the open recipe (the original, without audit steps), for the rule of a key drop (`utils.key_drop`, by place, D-0358): what every
        place of the recipe has as columns, asked of the engine's own plan without building anything (`plan_composer`, D-0325). Composed once per recipe, files and data (the
        handlers that ask it run on an event; no reactive dependency). None when the recipe cannot be drawn: the rule then reads the names the recipe declares and
        a drop it cannot follow is refused, "The app cannot YET follow ..." (D-0460, `utils.key_drop`), and a key that a join reads behind a step it cannot read is named only when the plan is there. A `PlanComposerBug` is not that case: it is notified and raised (`plan_book_for_the_gate`)."""
        def _compose():
            recipe_id = _open_recipe_id()
            loaded = load_data_analysis_recipe(orchestrator.data_analysis_recipes_dir / f"{recipe_id}.yaml")
            memo_key = (recipe_id, loaded.signature, _data_analysis_recipe_keys().data_batch_hash)
            if memo_key not in _plans_memo:
                _plans_memo.clear()
                _plans_memo[memo_key] = compose_plan_book(orchestrator, recipe_id, loaded)
            return _plans_memo[memo_key]

        with reactive.isolate():
            return plan_book_for_the_gate(_compose, lambda text: _notify("⚠️ " + text, type="error", duration=12))

    # ── Mode and data choice (slice B, D-0016, D-0310) ────────────────────────────────────────────────
    def _audit_available() -> bool:
        """True when the mode switch exists: the audit is on (`t3_sandbox_enabled`) and so is the interactive strip."""
        return bootloader.is_enabled("t3_sandbox_enabled") and bootloader.is_enabled("interactivity_enabled")

    def _in_audit() -> bool:
        """True in Audit mode. Without the audit flag the app is always in Exploration."""
        return _audit_available() and home_mode.get() == "audit"

    _graph_memo: dict = {}

    def _open_recipe_id() -> str:
        """The id of the recipe open in HOME. Raises a plain error when there is none (zero usable recipes, ADR-094 point 6): the start path
        never calls `get_default_data_analysis_recipe()`, which raises then."""
        recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe_or_none())
        if not recipe_id:
            raise RuntimeError("No data analysis recipe is open, so no source table can be read.")
        return recipe_id

    def _source_tables_of(p_id: str | None) -> list[str]:
        """The source tables (as the recipe names them) that feed the plot `p_id`, in graph order (`utils.recipe_graph`). Raises the plain error
        of the graph (`KeyError` for a plot the recipe does not have, `RecipeLoadError` or `RecipeGraphError` for a recipe that cannot be
        read or drawn): the caller shows it as the notice of the view, never as a traceback."""
        if not p_id:
            raise KeyError("No plot is open, so no source table can be listed.")
        return source_tables_of_plot(_open_graph(), p_id)

    def _open_graph():
        """The recipe graph of the open recipe (`utils.recipe_graph`), kept while the recipe file and id are the same. Raises what the load or the graph raises."""
        data_analysis_recipe_id = _open_recipe_id()
        loaded = load_data_analysis_recipe(orchestrator.data_analysis_recipes_dir / f"{data_analysis_recipe_id}.yaml")
        memo_key = (data_analysis_recipe_id, loaded.signature)
        if memo_key not in _graph_memo:
            _graph_memo.clear()
            _graph_memo[memo_key] = build_graph(loaded.raw)
        return _graph_memo[memo_key]

    def _audit_nodes_for(subtab_id: str | None) -> list[dict]:
        """The committed audit steps the plot `subtab_id` is built from, at any tier: written at its own tier 3 or at a table it is built from (`nodes_reaching_plot`), each
        decision once. THE one list every reader of the audited plot asks (HOME's plot and tables, the badge, the dialog); the table itself is the audit copy's (`_audited_t3_lf`)."""
        if home_state is None or not subtab_id:
            return []
        nodes = place_nodes(home_state.get().get("t3_audit_steps_by_plot", {}) or {})
        if not nodes:
            return []
        try:
            graph = _open_graph()
        except Exception:
            return []
        found = nodes_reaching_plot(graph, nodes, subtab_id.removeprefix("subtab_"))
        return list({n.get("id"): n for n in found}.values())

    def _effective_source_table(p_id: str | None) -> str | None:
        """The source table the Source choice shows for the plot `p_id`: the user's pick when it feeds this plot, else the first that does
        (a different plot has a different list, so the pick can fall out of it). None when no table feeds the plot. Raises as `_source_tables_of`."""
        tables = _source_tables_of(p_id)
        picked = source_table.get()
        return picked if picked in tables else (tables[0] if tables else None)

    def _open_plot_id() -> str | None:
        subtab = active_home_subtab.get()
        return subtab.removeprefix("subtab_") if subtab else None

    def _view_source_table() -> str | None:
        """The source table of the view on screen, for the filter handlers: None when the data choice is not Source or no table can be named
        (the error is then shown by the table itself)."""
        if _effective_view() != "SRC":
            return None
        try:
            return _effective_source_table(_open_plot_id())
        except Exception:
            return None

    def _current_view_key():
        """The view key of the view on screen (`view_key`: recipe, mode, data choice, source table, the table the open plot reads); None without an open recipe. The ONE
        definition: the clearing effect, the rows an exploration filter is stamped with and the preview all read it."""
        recipe_id = safe_input(input, "data_analysis_recipe_id", None)
        if recipe_id is None:
            return None
        if _in_audit():
            # Audit mode (slice 3a): the key of the TABLE SHOWN (`audit_place_view.view_identity`): two places that show the same table keep a staged condition, another table clears it
            # (D-0311, D-0505, D-0506), and so does a change of the columns of the table shown (a committed drop), by the digest of the columns the key ends with.
            shown = _audit_viewed_safe()
            if shown is None:
                return view_key(recipe_id, "audit", "T3", None, None) + (columns_digest([("?", "none")]),)
            try:
                lf, _facts, _ = _audit_shown_table()
            except SilentException:
                raise
            except Exception:
                lf = None
            return view_identity(shown, recipe_id, has_plot_steps(active_cfg().raw_config, shown.shown_plot), _shown_columns(lf))
        view = data_view.get()
        p_id = _open_plot_id()
        spec = _resolve_active_spec(p_id) if view != "SRC" else None
        # D-0505, D-0506: the key holds the table the open plot reads, not the plot: two plots on one table share it
        table = viewed_table(view, (spec or {}).get("target_dataset"), p_id, has_plot_steps(active_cfg().raw_config, p_id)) if view != "SRC" else None
        return view_key(recipe_id, "audit" if _in_audit() else "exploration", view, _view_source_table() if view == "SRC" else None, table)

    def _applied_for_view() -> list:
        """The applied exploration filters that were built on the view on screen: all the data preview and the badges may count (review F3)."""
        if _in_audit():
            return []      # exploration filters do not exist in Audit mode (D-0311, D-0361)
        return rows_built_on(list(applied_filters.get()), _current_view_key())

    def _screen_view_text() -> str:
        """The mode and the data choice on screen, in words, for the export record (P-B6): "Exploration mode, data view T3"."""
        with reactive.isolate():
            mode_word = "Audit" if _in_audit() else "Exploration"
            view = _effective_view()
            if view != "SRC":
                shown = _audit_viewed_safe() if _in_audit() else None
                named = f" (table '{shown.table}')" if shown is not None and shown.table and view in ("T1", "T2") else ""
                return f"{mode_word} mode, data view {view}{named}"
            table = _view_source_table()
            return f"{mode_word} mode, data view Source" + (f" (table '{table}')" if table else "")

    _source_memo: dict = {}

    def _read_source_lf(spec: dict | None):
        """One source table as read from its file, before any recipe step (`DataOrchestrator.read_source`, D-0310): the table the Source choice
        shows for the plot of `spec`. The call reads the file once to validate it, so the frame is kept per (recipe, table, data files hash) of
        the open view; a reload or an import (new keys) reads again. Errors are the plain `IngestionError` / `KeyError` texts, shown by the caller."""
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        plot_id = _plot_id_of(spec)
        if plot_id is None:
            raise RuntimeError("The plot of this view is not a plot of the open data analysis recipe, so its source tables cannot be listed.")
        table = _effective_source_table(plot_id)
        if table is None:
            raise RuntimeError(f"The plot '{plot_id}' reads no source table, so there is no Source view for it.")
        data_analysis_recipe_id = _open_recipe_id()
        # the key holds the recipe's own hash too (review F1): after an edit of how a source table is declared the table is read again
        keys = _data_analysis_recipe_keys()
        key = (data_analysis_recipe_id, table, keys.data_batch_hash, keys.data_analysis_recipe_sha256)
        if key not in _source_memo:
            if len(_source_memo) >= 8:
                _source_memo.clear()
            _source_memo[key] = orchestrator.read_source(data_analysis_recipe_id, table)
        return _source_memo[key]

    _place_audit: list = []      # [PlaceAudit] once made: it keeps the run of the audit copy between two reads

    def _the_place_audit() -> PlaceAudit:
        if not _place_audit:
            _place_audit.append(PlaceAudit(orchestrator, bootloader.get_location("user_data") / "anchors", bootloader.get_location("user_data") / "audit_anchors"))
        return _place_audit[0]

    def _committed_place_nodes() -> list[dict]:
        return place_nodes((home_state.get().get("t3_audit_steps_by_plot", {}) or {}) if home_state is not None else {})

    def _audited_t3_lf(plot_id: str, told=None):
        """The table `plot_id` reads in the audit copy made from the audit steps written at a place upstream (`audit_view.PlaceAudit`), lazy; None when no such step
        lies above the plot (it then reads its original table). Audit mode only: the caller asks `_in_audit()`. Raises what the run raises (an `AuditRunError` that names the
        step and its place, an `AuditCopyError`): the callers show it in the place of the plot, never skip a step."""
        nodes = _committed_place_nodes()
        return _the_place_audit().plot_lazy(_open_recipe_id(), plot_id, nodes, _recipe_plans() if nodes else None, told or _tell_inputs_changed)

    def _audit_run_for_export(told=None):
        """The run of the audit copy made from every committed audit step, for the export's audited table files; None when no step is committed. Raises what the run raises."""
        nodes = _committed_place_nodes()
        if not nodes:
            return None
        run = _the_place_audit().run_of(_open_recipe_id(), nodes, _recipe_plans())
        if run is not None and told is not None:
            for text in run.inputs_changed:
                told(InputsChanged(text))
        return run

    def _audited_view_lf(target_ds: str | None, tier: str):
        """The audited table of `target_ds` at `tier` ("T1" or "T2") for HOME's T1 and T2 views in Audit mode (D-0622): the table of the audit copy, lazy, the same one the export
        writes as `T<n>_data_audited.tsv`. None when it is not Audit mode, no step reaches this table at this tier, or the copy leaves the table as it is: the view then shows the
        original. Raises what the run raises (an audit step that cannot run: the preview shows it in the table's place, as for T3), only for a table a step reaches."""
        if not target_ds or not _in_audit():
            return None
        nodes = _committed_place_nodes()
        return _the_place_audit().table_lazy(_open_recipe_id(), target_ds, tier, nodes, _recipe_plans() if nodes else None, _tell_inputs_changed)

    def _audit_view_state(spec: dict | None, view: str) -> bool | None:
        """For the badge: in Audit mode on T1 or T2, True when the view shows the audited table and False when it shows the original (no audit step changes it); None for every
        other view, in Exploration, or when the table cannot be built (the table's place shows why)."""
        if view not in ("T1", "T2") or not _in_audit() or not (spec or {}).get("target_dataset"):
            return None
        try:
            return _audited_view_lf(spec["target_dataset"], view) is not None
        except Exception:
            return None

    def _plot_table_changed(plot_id: str) -> bool | None:
        """Whether the audit steps (at any tier) changed the CONTENT of the table of `plot_id` (a step that removes nothing moves a key and no row, ADR-101 point 6);
        None when it cannot be told (the run fails: the plot itself shows why)."""
        nodes = _committed_place_nodes()
        if not nodes:
            return None
        try:
            return plot_id in _the_place_audit().affected_plots(_open_recipe_id(), nodes, _recipe_plans())
        except Exception:
            return None

    # ── The shown item of Audit mode (slice 3a of the new Audit flow; D-0653, D-0654, D-0655, D-0657) ────────────────────────────────
    # Choosing a place in "Path of the data" only stages it. "Show" makes a place the SHOWN ITEM: the data preview, its title, its badge, the column chooser, the
    # filter form and the band read the table of the shown item, through `audit_place_view` (the one reader). None = nothing shown yet: the preview shows the table the open
    # plot reads (her answer 1, a). Written only by effects (`_forget_shown_item`, `_tab_shows_its_plot`, `_open_audit_mode_after_restore`) and by the handler of the Show
    # button (`lineage_handlers`); never inside a render (R1). Not saved in the session (D-0302).
    shown_item = reactive.Value(None)
    # The number of audit steps of a restored session, told by the band until the user shows something or leaves Audit mode (PROVISIONAL words).
    restored_steps = reactive.Value(0)

    @reactive.Calc
    def _lineage_calc():
        """The lineage of the open recipe (`utils.lineage_data.lineage_of`), or (None, the plain reason). Follows the recipe and the data; never reads the choice, the shown item or the
        audit steps. One calc for the panel "Path of the data" and for the reader of the shown item."""
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        raw = active_cfg().raw_config
        try:
            return lineage_of(raw, _recipe_plans()), ""
        except PlanComposerBug:
            return None, "The engine's plan of the recipe could not be made (it was reported)."
        except (RecipeGraphError, KeyError, TypeError, ValueError) as exc:
            return None, f"The recipe cannot be drawn as a lineage: {exc}"

    def _audit_open_plot(graph) -> str | None:
        """The plot open now, as the reader needs it: the tab's plot when the recipe has it, else the first plot of the recipe (what HOME does with no tab open), else None."""
        plot = _open_plot_id()
        if plot and graph.has_node(f"T3:{plot}"):
            return plot
        plots = graph.plots()
        return plots[0] if plots else None

    def _audit_viewed() -> Viewed:
        """What is on screen in Audit mode (`audit_place_view.viewed`): the shown item, or with none the table the open plot reads. Raises what the graph load raises."""
        graph = _open_graph()
        open_plot = _audit_open_plot(graph)
        lineage, problem = _lineage_calc()
        place = shown_item.get()
        if lineage is None:
            # the lineage cannot be drawn: the panel says why; the preview keeps the table the open plot reads, as before this slice
            if open_plot is None:
                raise RuntimeError(problem)
            return Viewed(AUDIT, "T3", graph.plot_target(open_plot), f"T3:{open_plot}", open_plot, open_plot, True, True)
        return viewed_item(AUDIT, "T3", None, open_plot, [place] if place else [], graph, lineage)

    def _audit_viewed_safe() -> Viewed | None:
        """`_audit_viewed`, or None when the recipe cannot be read (the table's place says why): for the readers that only need to know the tier or the place."""
        try:
            return _audit_viewed()
        except SilentException:
            raise
        except Exception:
            return None

    def _audit_readers() -> Readers:
        """The reads `audit_place_view.table_for` is handed: the orchestrator's original tables and the audit copy's tables (the same ones the export writes)."""
        if data_refresh_trigger is not None:
            data_refresh_trigger.get()
        recipe_id = _open_recipe_id()
        keys = _data_analysis_recipe_keys()
        anchors = bootloader.get_location("user_data") / "anchors"
        nodes = _committed_place_nodes()
        plans = _recipe_plans() if nodes else None
        audit = _the_place_audit()
        return Readers(
            source=lambda t: orchestrator.read_source(recipe_id, t),
            tier1=lambda t: orchestrator.materialize_tier1(data_analysis_recipe_id=recipe_id, collection_id=t, output_path=anchors / f"{t}.parquet",
                                                           keys=keys, on_inputs_changed=_tell_inputs_changed),
            tier2=lambda t: orchestrator.materialize_tier2(data_analysis_recipe_id=recipe_id, collection_id=t, tier1_path=anchors / f"{t}.parquet",
                                                           keys=keys, on_inputs_changed=_tell_inputs_changed),
            plot=lambda p: orchestrator.materialize_tier3(data_analysis_recipe_id=recipe_id, plot_id=p, anchors_dir=anchors, keys=keys,
                                                          on_inputs_changed=_tell_inputs_changed),
            audited_table=lambda t, tier: audit.table_lazy(recipe_id, t, tier, nodes, plans, _tell_inputs_changed),
            audited_plot=lambda p: audit.plot_lazy(recipe_id, p, nodes, plans, _tell_inputs_changed),
            committed_steps=len(nodes))

    def _audit_shown_table():
        """The ONE read of the table shown in Audit mode: (lazy table or None, its facts, the `Viewed`). The table is the audited one where a committed audit step changes it, the original
        otherwise (D-0622); the facts say which. Raises what the readers raise (an audit step that cannot run, a table that cannot be built): the callers show it in the table's place."""
        shown = _audit_viewed()
        lf, facts = table_for(shown, _audit_readers())
        return lf, facts, shown

    def _effective_view() -> str:
        """The data choice as the readers of the preview understand it: in Exploration the choice of "Table to view"; in Audit mode the tier of the item shown (the choice is hidden)."""
        if _in_audit():
            shown = _audit_viewed_safe()
            return shown.tier if shown is not None and shown.tier in ("T1", "T2", "T3") else "T3"
        return data_view.get()

    # a handle with the one method the filter handlers call on the data choice
    _view_for_handlers = SimpleNamespace(get=_effective_view)

    def _audit_write_ok() -> bool:
        """True when an audit step may be written from the screen as it is: the item shown is the Result data (T3) of the plot OPEN (the dialog and the drops write at the open plot).
        PROVISIONAL (slice 3a): the table shown is a plot's Result data and that plot is the open tab; a table shown, or another plot shown, offers no step until the step bar (next slices)."""
        shown = _audit_viewed_safe()
        return bool(shown is not None and not shown.nothing_chosen and shown.tier == "T3" and shown.shown_plot is not None and shown.shown_plot == shown.plot)

    def _effective_shown_place() -> str | None:
        """The place shown in Audit mode (the default open plot's node included): what the lineage marks as shown; None when nothing can be shown."""
        shown = _audit_viewed_safe()
        return shown.place if shown is not None and not shown.nothing_chosen else None

    def _shown_name(shown: Viewed) -> str:
        """The name of the item shown, as the lineage panel writes it (`lineage_view.line_text`)."""
        lineage, _ = _lineage_calc()
        if lineage is not None and shown.place and any(n.id == shown.place for n in lineage.nodes):
            return line_text(lineage.node(shown.place))
        return shown.table or ""

    def _shown_columns(lf) -> list:
        """The names and types of the table shown, for the key of the view (a column drop changes them, so a condition built before it is cleared). A table that cannot be read gives a
        fixed pair so that the key keeps its shape."""
        if lf is None:
            return [("?", "none")]
        try:
            schema = lf.collect_schema()
            return [(name, str(schema[name])) for name in schema.names()]
        except Exception:
            return [("?", "error")]

    def _resolve_active_lf(spec: dict | None, tier: str | None = None, original: bool = False):
        """Return a LazyFrame for the table the data choice names, for the plot of `spec` (or tier1_anchor).

        In Audit mode the T3 table is the AUDITED one when an audit step is written at the plot's own tier 3 or at a place upstream of it (`_audited_t3_lf`: the table of the audit
        copy, the same for the plot, the table, the dialog and the export); `original=True` asks for the plot's own table whatever the mode (the "Original" pane of Compare).

        "SRC" is one source table as read from its file (`_read_source_lf`). "T1" is the plot's table after tier 1. "T2" reads the assembly's
        stored Tier 2 parquet (issue #10; equal to T1 when the table has no tier2 steps). "T3" reads the table the plot reads
        (`materialize_tier3`: that Tier 2 plus the plot's own `tier3` steps of the recipe; the same table when the plot has none): the
        table the plot shows. The audit steps of Audit mode (filters, drops, at any tier) are in the audit copy's table, not applied on top by the callers.

        `tier` defaults to the data choice (`data_view`). Plot handlers and the audit write pass "T3" explicitly: a plot is drawn from the
        table it reads, in Exploration as in Audit mode (D-0310, D-0019), and audit steps are written at the plot's table.

        In Audit mode, with no `tier` asked (the data preview, the column chooser, the filter form), the table is the one of the item SHOWN (slice 3a, D-0655): `_audit_shown_table`,
        through `audit_place_view`, whatever `spec` the caller passes (the open plot's). The data choice is hidden in Audit mode.
        """
        if tier is None and not original and _in_audit():
            lf, facts, _shown = _audit_shown_table()
            if lf is None:
                raise RuntimeError(facts.why_original)
            return lf
        chosen = tier or data_view.get()
        if chosen == "SRC":
            return _read_source_lf(spec)
        if chosen in ("T1", "T2") and not original:
            # D-0622: in Audit mode the T1 and T2 views show the AUDITED tables (the audit copy's, the same the export writes) when an audit step changes them
            audited = _audited_view_lf((spec or {}).get("target_dataset"), chosen)
            if audited is not None:
                return audited
        if chosen in ("T2", "T3") and (spec or {}).get("target_dataset"):
            target_ds = spec["target_dataset"]
            if data_refresh_trigger is not None:
                data_refresh_trigger.get()
            anchor_dir = bootloader.get_location("user_data") / "anchors"
            data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
            if chosen == "T3":
                plot_id = _plot_id_of(spec)
                if plot_id is None:
                    raise RuntimeError(f"The plot of the dataset '{target_ds}' is not a plot of the open data analysis recipe, so the table it reads cannot be built.")
                if not original and _in_audit():
                    audited = _audited_t3_lf(plot_id)
                    if audited is not None:
                        return audited
                return orchestrator.materialize_tier3(
                    data_analysis_recipe_id=data_analysis_recipe_id, plot_id=plot_id, anchors_dir=anchor_dir,
                    keys=_data_analysis_recipe_keys(), on_inputs_changed=_tell_inputs_changed)
            # Issue #10 / ADR-089: T2 is read from its stored parquet (key-checked). An error is
            # not caught here: showing Tier 1 in place of a failed Tier 2 would be a false result.
            return orchestrator.materialize_tier2(
                data_analysis_recipe_id=data_analysis_recipe_id, collection_id=target_ds,
                tier1_path=anchor_dir / f"{target_ds}.parquet", keys=_data_analysis_recipe_keys(), on_inputs_changed=_tell_inputs_changed)
        return _resolve_t1_lf(spec)

    def _dialog_table_identity(spec: dict | None, tier: str):
        """Which table `_resolve_active_lf(spec, tier)` reads, for the filter form: the stored table (`stored_table_identity`), or for the
        Source choice the source table (`source_table_identity`); None when the plot names no collection (the table then comes from the app's
        open anchor, which no key of this view describes)."""
        if _in_audit():
            # Audit mode (slice 3a): the table is the one SHOWN, not the open plot's; the audit steps that change it are part of what identifies it
            shown = _audit_viewed_safe()
            if shown is None or shown.nothing_chosen or not shown.table:
                return None
            keys = _data_analysis_recipe_keys()
            base = stored_table_identity(
                shown.tier, shown.table, _open_recipe_id(), keys.tier1_key_of(shown.table),
                bootloader.get_location("user_data") / "anchors" / f"{shown.table}.parquet", _unstored_builds[0],
                keys.plot_key_of(shown.shown_plot) if shown.tier == "T3" and shown.shown_plot is not None else None, keys.tier2_key_of(shown.table))
            return None if base is None else (base, shown.place, repr(nodes_signature(_committed_place_nodes())))
        # Nothing is asked of the recipe or the keys until there is a plot to identify: with no plot (zero usable recipes) there is no table, so no
        # identity and no log line (found in review: the recipe id used to be read first, and with zero recipes that raised).
        plot_id = _plot_id_of(spec)
        target_ds = (spec or {}).get("target_dataset")
        if (tier == "SRC" and plot_id is None) or (tier != "SRC" and not target_ds):
            return None
        data_analysis_recipe_id = _open_recipe_id()
        keys = _data_analysis_recipe_keys()
        if tier == "SRC":
            table = _effective_source_table(plot_id)
            return None if table is None else source_table_identity(data_analysis_recipe_id, table, keys.data_analysis_recipe_sha256, keys.data_batch_hash)
        return stored_table_identity(
            tier, target_ds, data_analysis_recipe_id, keys.tier1_key_of(target_ds),
            bootloader.get_location("user_data") / "anchors" / f"{target_ds}.parquet", _unstored_builds[0],
            keys.plot_key_of(plot_id) if tier == "T3" and plot_id is not None else None, keys.tier2_key_of(target_ds))

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
                return plot_list_label(p_id, entry)
        return p_id

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
        this_subtab = f"subtab_{p_id}"

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
                    spec = plot_entry
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
            # Phase 22-J: per-plot T3 stack — query by this plot's subtab id,
            # not by the active subtab (this plot may not be the active one
            # when its render runs in re-renders). `this_subtab` comes from the
            # enclosing factory scope (shared with _effective_random_state above).
            # Slice B (D-0019, D-0180, D-0311): in Exploration there is ONE plot, the Result, drawn from the plot's own table
            # (T3 of the recipe) with no exploration filter and no audited step on it: preview filters (Apply) change the data
            # TABLE of the view shown and never a plot. In Audit mode the plot is the audited plot: the same table plus the plot's
            # audited steps (Apply-gated); Compare's left pane never carries them (its own handler).
            # GUARDED by test_filters_change_the_table_not_the_plot.py and test_shiny_smoke.py::TestPreviewFiltersOnReferenceViews.
            in_audit_plot = _in_audit()
            # PLOT-TABLE-ORDER-1: the plot gets its data from the same frame as the table of the audited T3 view: the table of the audit
            # copy (`_resolve_active_lf`), in which the audit steps of every tier run in one order (tier 1, tier 2, tier 3; inside a tier the order written).
            # Nothing is handed to the factory's `filters` key (that key is for what a recipe's plot spec writes), so the audited steps are
            # applied once, in one order, and a step that cannot run is an error, never a skip.
            # the recipe the plot engine draws from: the same call as the opening's proof of drawing (`opening_build.plot_render_recipe`)
            synthetic_data_analysis_recipe = plot_render_recipe(cfg.raw_config, p_id, spec)

            try:
                lf = _resolve_active_lf(spec, tier="T3")   # the table the plot reads (in Audit mode the audit copy's), in every data choice (D-0310)
            except AUDIT_ERRORS as e:
                # a step that cannot run is shown in the plot's place and in the Alerts panel, never skipped (D-0102)
                _report_plot_exception(e, "T3Audit", f"audit steps of plot '{p_id}'")
                import matplotlib.pyplot as plt
                import textwrap
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, "\n".join(textwrap.fill(line, 70) for line in f"Audit step error:\n{e}".splitlines()),
                        ha="center", va="center", transform=ax.transAxes, color="#d62828", fontsize=8)
                ax.axis("off")
                return fig
            except Exception as e:
                # ADR-094: data materialization (ingestion/assembly) failures get the same
                # session_processing_issues capture the VizFactory render path already has
                # (below) — same deferred-write pattern (R1-safe), same "Processing Issues"
                # panel (audit_stack.py:processing_issues_ui). capture_entry() reads the real
                # PipelineError the library already built (errors.py's pipeline_error= carry
                # kwarg, PIPELINE-ERROR-WIRE-2) when the exception has one; falls back to the
                # exception's own message otherwise — same as before this change.
                _report_plot_exception(e, "DataOrchestrator", f"materialize(plot_id='{p_id}')")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Data error: {e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9)
                ax.axis("off")
                return fig

            # VIZFAC-T3-OVERRIDE-1: Extract L5 aesthetic_override from home_state (the Reshuffle pin among them). D-0341: only the audited plot of
            # Audit mode carries it; the Exploration plot is the recipe's plot and equals the "Original" pane of Compare, whatever is stored.
            _t3_overrides = (
                (home_state.get() if home_state is not None else {})
                .get("t3_plot_overrides", {})
                .get(this_subtab)
            ) if in_audit_plot else None

            # SEED-HOLDS-1 (ADR-104): HOME draws no seed. A layer that writes a number keeps it, a layer that
            # writes none uses the factory's seed (0), an audit pin (Reshuffle) is in `_t3_overrides` and beats both:
            # the same seeds as the comparison reference pane, the gallery, Blueprint and the export.

            def _report_draw_error(e):
                _report_plot_exception(e, "VizFactory", f"render(plot_id='{p_id}')")

            try:
                # VIZ-STANDARD-1 V7: plotnine draws after this function returns, so a draw error used to escape the
                # try below and reach the user as a raw error. `show_draw_errors` draws the one-form message in the
                # place of the plot and reports it to the alerts panel; the plot itself is drawn once, by Shiny.
                return show_draw_errors(
                    viz_factory.render(lf, synthetic_data_analysis_recipe, p_id, aesthetic_override=_t3_overrides),
                    on_error=_report_draw_error, on_warning=_report_plot_warning)
            except Exception as e:
                _report_draw_error(e)
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Render error:\n{plot_read_error_text(cfg.raw_config, p_id, e)}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9,
                        wrap=True)
                ax.axis("off")
                return fig

        return _group_plot_handler

    # Register one handler per discovered plot ID
    for _p_id, _spec in _all_group_plot_ids:
        _make_group_plot_handler(_p_id)

    # Phase 21-E / slice B: the original plot (the Result) for Compare, in Audit mode.
    # Identical to the regular handlers but skips all T3 audit nodes: always the plot's own table,
    # so the user can see what the audited steps did.
    def _make_cmp_baseline_handler(p_id: str):
        """Factory: renders plot_group_{p_id}_cmp_base WITHOUT audited steps (the original plot of Compare)."""
        @output(id=f"plot_group_{p_id}_cmp_base")
        @render.plot(alt=f"Baseline: {p_id}")
        def _cmp_baseline_handler():
            cfg = active_cfg()
            groups = cfg.raw_config.get("analysis_groups", {})
            spec = None
            for _gid, gspec in groups.items():
                plot_entry = gspec.get("plots", {}).get(p_id)
                if plot_entry is not None:
                    spec = plot_entry
                    break
            if spec is None:
                top_plot = cfg.raw_config.get("plots", {}).get(p_id)
                if top_plot is not None:
                    spec = top_plot
            if spec is None:
                return None

            # No audited steps — this is the original plot (the Result)
            # the recipe the plot engine draws from: the same call as the opening's proof of drawing (`opening_build.plot_render_recipe`)
            synthetic_data_analysis_recipe = plot_render_recipe(cfg.raw_config, p_id, spec)
            try:
                lf = _resolve_active_lf(spec, tier="T3", original=True)  # original = the Result plot (D-0147): the table the plot reads, no exploration, no audit nodes
            except Exception as e:
                # ADR-094/PIPELINE-ERROR-WIRE-2: was silent (no session_processing_issues
                # capture at all) — the comparison-mode twin of _group_plot_handler's
                # already-fixed first except block, previously missed.
                _report_plot_exception(e, "DataOrchestrator", f"materialize(plot_id='{p_id}', mode='cmp_base')")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Data error: {e}", ha="center", va="center",
                        transform=ax.transAxes, color="red", fontsize=9)
                ax.axis("off")
                return fig

            # SEED-HOLDS-1: the original pane draws with the same seeds as the audited plot (recipe numbers, the factory's
            # seed); an audit pin is a change the user made and is not applied here.
            def _report_cmp_error(e):
                _report_plot_exception(e, "VizFactory", f"render(plot_id='{p_id}', mode='cmp_base')")

            try:
                # VIZ-STANDARD-1 V7: a draw error is shown in the plot's place, as in the main plot handler.
                return show_draw_errors(viz_factory.render(lf, synthetic_data_analysis_recipe, p_id),
                                        on_error=_report_cmp_error, on_warning=_report_plot_warning)
            except Exception as e:
                _report_cmp_error(e)
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"Render error:\n{plot_read_error_text(cfg.raw_config, p_id, e)}", ha="center", va="center",
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
            ui.tags.span(badge.label, class_=f"badge spv-view-badge spv-view-badge-{badge.tone}"),
            *[ui.tags.span(note, class_="spv-view-note") for note in badge.notes],
            class_="spv-view-badge-row",
        )

    def _audited_step_count(subtab_id) -> int:
        """How many audited steps (filters and column drops, at any tier) this plot is built from: what Audit mode puts on its T3 table and its plot (issue #17)."""
        return len(_audit_nodes_for(subtab_id))

    def _upstream_step_count(subtab_id) -> int:
        """How many of them were written at a table the plot is built from (not at its own tier 3)."""
        own = own_plot_place((subtab_id or "").removeprefix("subtab_"))
        return len([n for n in _audit_nodes_for(subtab_id) if n.get("place") != own])

    # Compare (Audit mode only, D-0147): a switch of the strip. Its value is kept here, so that a rebuild of the strip (a workspace switch)
    # or a stay in Exploration does not forget it. PROVISIONAL P-B7: the input is called `audit_compare`.
    _audit_compare = reactive.Value(False)

    def _make_plot_cell_handler(p_id: str):
        _acc_id = f"plot_acc_{p_id}"
        _panel_val = f"plot_panel_{p_id}"
        _this_subtab = f"subtab_{p_id}"
        _reshuffle_output_id = f"plot_reshuffle_{p_id}"
        _reshuffle_btn_id = f"plot_reshuffle_btn_{p_id}"
        _unpin_btn_id = f"plot_unpin_btn_{p_id}"

        def _seeds_in_use():
            """The seed of every random layer of this plot as it is drawn (plot_seeds.seed_in_use: the resolver's
            precedence, audit pin > the layer's number > plot_defaults.random_state > 0). Reads home_state, so the
            two outputs below re-render the moment a pin is set or removed."""
            spec = _resolve_active_spec(p_id)
            plot_defaults = (active_cfg().raw_config.get("plot_defaults") or {})
            # D-0341: the pin is applied by the audited plot only; in Exploration the seed shown is the one the plot is drawn with (no pin)
            return seed_in_use((spec or {}).get("layers", []), plot_defaults,
                               home_state.get() if home_state is not None and _in_audit() else None, p_id,
                               default=viz_factory.default_random_state)

        @output(id=_reshuffle_output_id)
        @render.ui
        def _plot_reshuffle_ui():
            """REPRO-RESHUFFLE-1 (#49): a UI control to deliberately redraw and pin a plot's random seed. Its own
            narrow output next to the badge, not a revival of the Plot Style panel (fork issue #15). Offered under
            the same precedence as the resolver (plot_seeds.reshuffle_offered): only where the plot has a random
            layer and no seed is written anywhere (no number on a layer, no plot_defaults.random_state) and no pin
            exists yet. A pin applies to every random layer of the plot. The way back is the seed line's
            "Remove the pinned seed" (below), which removes the pin.

            Deliberately NOT reactive.isolate() here: this output must re-render and hide itself the moment
            _handle_reshuffle pins the seed into home_state."""
            if not _in_audit() or not reshuffle_offered(_seeds_in_use()):
                return ui.div()   # D-0341: the button belongs to Audit mode; Exploration shows the recipe's plot
            return ui.input_action_button(
                _reshuffle_btn_id, "🔀 Reshuffle arrangement",
                class_="btn-outline-secondary btn-sm",
                style="font-size:0.7em; padding:1px 6px;",
                title=RESHUFFLE_TITLE,
            )

        @reactive.Effect
        @reactive.event(getattr(input, _reshuffle_btn_id, lambda: None))
        def _handle_reshuffle():
            if home_state is None or not _in_audit():
                return
            try:
                clicks = getattr(input, _reshuffle_btn_id)()
            except SilentException:
                return          # the button is not drawn yet: nothing was clicked
            except Exception as exc:
                _notify("⚠️ " + notice(
                    f"The Reshuffle click of the plot '{p_id}' could not be read, so the arrangement was not changed",
                    "reload the page (F5) and click Reshuffle again", exc), type="error", duration=10)
                return
            if not clicks:
                return
            new_seed = secrets.randbits(31)
            hs = home_state.get()
            overrides = dict(hs.get("t3_plot_overrides", {}))
            plot_overrides = dict(overrides.get(_this_subtab, {}))
            plot_overrides["random_state"] = new_seed
            overrides[_this_subtab] = plot_overrides
            home_state.set({**hs, "t3_plot_overrides": overrides})

        @output(id=f"plot_seed_{p_id}")
        @render.ui
        def _plot_seed_ui():
            """The seed this plot's random layers use and where it comes from, as one short line with the plot (HTML next
            to the plot, never part of the image, so never exported). Nothing for a plot without a random layer. With
            a pinned seed it also offers the way back: removing the pin."""
            seeds = _seeds_in_use()
            caption = seed_caption(seeds)
            if caption is None:
                return ui.div()
            parts = [ui.tags.span(caption, class_="spv-view-note")]
            if any(ls.source == "audit" for ls in seeds):
                parts.append(ui.input_action_button(
                    _unpin_btn_id, "Remove the pinned seed", class_="btn-link btn-sm spv-view-note",
                    style="padding:0 6px;",
                    title="Remove this audit step: the plot goes back to the seed of the recipe."))
            return ui.div(*parts, class_="spv-view-badge-row")

        @reactive.Effect
        @reactive.event(getattr(input, _unpin_btn_id, lambda: None))
        def _handle_unpin():
            """The way back from Reshuffle: remove the pinned seed (the audit step) of this plot."""
            if home_state is None:
                return
            try:
                clicks = getattr(input, _unpin_btn_id)()
            except SilentException:
                return          # the button is not drawn yet: nothing was clicked
            except Exception as exc:
                _notify("⚠️ " + notice(
                    f"The click on 'Remove the pinned seed' of the plot '{p_id}' could not be read, so the seed stays pinned",
                    "reload the page (F5) and click again", exc), type="error", duration=10)
                return
            if not clicks:
                return
            hs = home_state.get()
            overrides = dict(hs.get("t3_plot_overrides", {}))
            plot_overrides = {k: v for k, v in (overrides.get(_this_subtab) or {}).items() if k != "random_state"}
            if plot_overrides:
                overrides[_this_subtab] = plot_overrides
            else:
                overrides.pop(_this_subtab, None)
            home_state.set({**hs, "t3_plot_overrides": overrides})

        @output(id=f"plot_badge_{p_id}")
        @render.ui
        def _plot_badge_ui():
            """What the plot shows now (issue #17). Its own output, so that a filter change redraws only
            this small badge and never the plot. In Compare each pane already has its own label."""
            if not bootloader.is_enabled("interactivity_enabled"):
                return ui.div()
            audit = _in_audit()
            if audit and _audit_compare.get() and bootloader.is_enabled("comparison_mode_enabled"):
                return ui.div()
            spec = _resolve_active_spec(p_id)
            has_t2 = has_tier2_steps(active_cfg().raw_config, (spec or {}).get("target_dataset"))
            return _badge_ui(plot_badge("audit" if audit else "exploration", has_plot_steps(active_cfg().raw_config, p_id), has_t2,
                                        preview_filters=len(_applied_for_view()), audited_steps=_audited_step_count(f"subtab_{p_id}"),
                                        upstream_steps=_upstream_step_count(f"subtab_{p_id}"),
                                        table_changed=_plot_table_changed(p_id) if audit and _audited_step_count(f"subtab_{p_id}") else None))

        @output(id=f"plot_cmp_label_{p_id}")
        @render.ui
        def _plot_cmp_label_ui():
            """The label of the audited pane of Compare: "Audited (after N steps)", N = the committed audit steps that reach this plot (at its own
            tier 3 or at a table it is built from). Its own output, so that a new step relabels the pane and never redraws the plot."""
            n = _audited_step_count(f"subtab_{p_id}")
            words = "no steps yet" if n == 0 else ("after 1 step" if n == 1 else f"after {n} steps")
            return ui.tags.div(f"Audited ({words})", class_="badge mb-1 spv-text-xs", style="background:#ffc107; color:#212529;")

        @output(id=f"plot_cell_{p_id}")
        @render.ui
        def _plot_cell_ui():
            # Compare lives in Audit mode only (D-0016, D-0018): the original plot beside the audited plot.
            in_comparison = (
                _in_audit()
                and _audit_compare.get()
                and bootloader.is_enabled("comparison_mode_enabled")
            )

            # Read initial collapse state without creating a reactive dependency (Rule R4).
            # Client-side accordion preserves state across sub-tab switches; server state
            # is only used when the component is fully re-mounted (e.g. Home → Gallery → Home).
            with reactive.isolate():
                _hs = home_state.get() if home_state else {}
            _is_open = _hs.get("plot_collapse_state", {}).get(p_id, True)

            if in_comparison:
                content = ui.div(ui.output_ui(f"plot_seed_{p_id}"), ui.layout_columns(
                    ui.div(
                        ui.tags.div(
                            # PROVISIONAL (slice 1, 2026-11-26): the labels of the two panes of Compare
                            "Original (before your audit steps)",
                            class_="badge bg-secondary mb-1 spv-text-xs",
                        ),
                        ui.output_plot(f"plot_group_{p_id}_cmp_base", height="440px"),
                    ),
                    ui.div(
                        ui.output_ui(f"plot_cmp_label_{p_id}"),
                        ui.output_plot(f"plot_group_{p_id}", height="440px"),
                    ),
                    col_widths=[6, 6],
                    class_="spv-compare-panes",
                ))
            else:
                content = ui.div(
                    ui.div(
                        ui.output_ui(f"plot_badge_{p_id}"),
                        ui.output_ui(f"plot_reshuffle_{p_id}"),
                        class_="d-flex justify-content-between align-items-start",
                    ),
                    ui.output_ui(f"plot_seed_{p_id}"),
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
        if active_sidebar == frame_widths.BLUEPRINT:
            return ui.div(wrangle_studio.render_ui(), class_="theater-container-main")
        if active_sidebar == "Test Lab":
            if dev_studio is None:
                return ui.div()
            return ui.div(dev_studio.render_ui(), class_="theater-container-main")
        if active_sidebar == "Gallery":
            return ui.div(gallery_viewer.render_explorer_ui(), class_="theater-container-main")

        # issue #38: Home has nothing to run without at least one usable data analysis recipe
        # (ADR-094's explicitly-deferred all-rejected / zero-recipes case). Point the user at
        # whichever authoring workspaces this deployment actually enables, instead of either
        # crashing (the bug) or a generic "Data Assembly Failed" exception message (unhelpful —
        # there is no recipe to assemble yet, this is not a failure of one).
        active_cfg()  # GATE-GAP-1: depends on the gate answer, so this output redraws when a recipe passes or fails
        if not bootloader.has_usable_data_analysis_recipe:
            _next_steps = []
            if bootloader.is_enabled("blueprint_enabled"):
                _next_steps.append("**Blueprint** to build one")
            if bootloader.is_enabled("test_lab_enabled"):
                _next_steps.append("**Test Lab** to bootstrap one from a file")
            if _next_steps:
                _hint = " or ".join(_next_steps) + "."
            else:
                _hint = "Ask this deployment's operator to add one."
            _rejected = bootloader.rejected_data_analysis_recipes
            _why = (
                f"{len(_rejected)} data analysis recipe(s) exist but failed validation "
                "(also listed in Data analysis recipe Choice in the sidebar)."
                if _rejected else
                "No data analysis recipe files were found."
            )
            return ui.div(
                ui.tags.h5("No data analysis recipes yet", class_="mb-2"),
                ui.markdown(f"{_why} Open {_hint}"),
                *[ui.tags.p(rejected_recipe_text(_name, _rec), class_="small mb-1")
                  for _name, _rec in sorted(_rejected.items())],
                class_="alert alert-info m-3",
            )

        # GATE-GAP-1: the recipe open in HOME failed its checks after its files changed: say so, show nothing computed from it
        _open_recipe = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe_or_none())
        if _open_recipe in bootloader.rejected_data_analysis_recipes:
            return ui.div(
                ui.tags.h5("This data analysis recipe is not available", class_="mb-2"),
                ui.tags.p(rejected_recipe_text(_open_recipe, bootloader.rejected_data_analysis_recipes[_open_recipe])),
                class_="alert alert-warning m-3",
            )

        # D-0326: the tables of the recipe are built and stored by its opening (`opening_handlers`), in one place. This render waits for it and then only reads
        # the stored tables; a recipe the opening refuses is rejected like one the gate rejects and is shown by the branches above.
        try:
            _opening_signature = opening_signature(_open_recipe, _data_analysis_recipe_keys())
        except Exception:
            _opening_signature = None   # the recipe or its data cannot be read: the assembly below says why
        if recipe_gate_version is not None and _opening_signature is not None and opening_waits(opening_state.get(), bootloader.available_data_analysis_recipes, _open_recipe, _opening_signature):
            # PROVISIONAL (D-0334 asks for a progress line, not for this waiting sentence): the text of the alert that stands in the place of the theater while the
            # opening runs is the builder's
            return ui.div(ui.tags.p(opening_cover_text(_open_recipe), class_="mb-0"), class_="alert alert-info m-3")

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
                on_inputs_changed=_tell_inputs_changed,
            )

        except Exception as e:
            return ui.div(ui.markdown(f"**Data Assembly Failed**: {e}"), class_="alert alert-danger")

        # Discover columns (retained for future filter scoping in Phase 21-F)
        all_cols = lf_full.collect_schema().names()  # noqa: F841

        cfg = active_cfg()
        groups = cfg.raw_config.get("analysis_groups", {})

        # --- the recipe banner: info.ui_label (the file name when there is none), hidden by branding.show_recipe_name: false in the
        # deployment file (D-0410, D-0470, D-0474). It reads nothing from the app features file and not info.subtitle (D-0482).
        _title_text = recipe_banner_title(cfg.raw_config.get("info"), data_analysis_recipe_id, bootloader.show_recipe_name())

        # --- The mode row (slice 1, 2026-11-26, PROVISIONAL words): with the audit on, the title and the mode control "Exploration | Audit" sit in a
        # row of their own that exists also when the deployment hides the recipe name (the row then holds the toggle alone). Without the audit
        # (no `t3_sandbox_enabled`, or no interactivity) there is no toggle and the banner is the title alone, as it was.
        # HOM-08: the current mode is read isolated, so that a rebuild of this output (a workspace switch) does not forget it.
        with reactive.isolate():
            _cur_mode = home_mode.get()
        _title_span = ui.tags.span(_title_text, class_="banner-title", title=_title_text) if _title_text else None
        if bootloader.is_enabled("interactivity_enabled") and _audit_available():
            mode_choices = {
                "exploration": ui.HTML('<span title="Exploration: one plot, the Result. Filters change the table you view, never the plot. '
                                       'Nothing here is saved or exported.">Exploration</span>'),
                "audit": ui.HTML('<span title="Audit: filters and column drops become audit steps with a reason. They change the plot, '
                                 'are saved with the session and are exported.">Audit</span>'),
            }
            home_title_banner = ui.div(
                ui.div(
                    _title_span if _title_span is not None else ui.span(),
                    ui.input_radio_buttons(
                        "home_mode", label=ui.span("Mode", class_="visually-hidden"), choices=mode_choices,
                        selected=_cur_mode if _cur_mode in mode_choices else "exploration", inline=True),
                    class_="spv-mode-row-line",
                ),
                ui.output_ui("mode_caption_ui"),
                class_="view-title-banner spv-mode-row",
            )
        elif _title_span is not None:
            home_title_banner = ui.div(
                _title_span,
                class_="view-title-banner",
                style="margin-bottom: 8px;",
            )
        else:
            home_title_banner = ui.div()

        # --- Thin header: the data choice "Table to view" (slice B, D-0016, D-0310). It is its own output (`data_strip_ui`): it exists in Exploration only, because in
        # Audit mode the table shown is the one chosen in "Path of the data" (slice 3a, D-0652, D-0655). Without interactivity there is no strip at all (STATIC-VIEW-1a).
        theater_header = ui.output_ui("data_strip_ui") if bootloader.is_enabled("interactivity_enabled") else ui.div()

        # Data preview slot — always rendered regardless of groups presence
        # so the Shiny output ID is always mounted.
        data_preview_section = ui.div(
            ui.output_ui("shown_band_ui"),
            ui.accordion(
                ui.accordion_panel(
                    ui.div(
                        ui.tags.span(
                            ui.output_text("home_data_preview_title", inline=True),
                            ui.output_ui("home_data_preview_badge", inline=True),
                            title="Preview the Result data (T3) or the table of the selected tier of the open plot",
                            class_="me-3",
                        ),
                        # PREVIEW-ALLROWS-1: "Show all rows" toggle — off by default (100-row cap).
                        # the switch sits inside the panel's header button; app/src/www/preview_switch.js keeps its click from folding the panel
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
                    tab_label = plot_tab_label(p_id, plot_spec)
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
                ui.output_ui("compare_switch_ui"),
                ui.output_ui("lineage_panel_ui"),
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
            group_label = group_tab_label(group_id, group_spec)
            plot_ids = list(group_spec.get("plots", {}).keys())

            plot_subtabs = []
            for p_id in plot_ids:
                tab_label = plot_tab_label(p_id, group_spec["plots"][p_id])
                plot_cell = ui.output_ui(f"plot_cell_{p_id}")

                plot_subtabs.append(
                    ui.nav_panel(
                        tab_label,
                        plot_cell,
                        value=f"subtab_{p_id}"
                    )
                )

            # navset_card_tab: gives the card border + built-in tab header — no extra label needed
            # selected= restores the previously active plot after a Gallery/Blueprint nav round-trip.
            # Eve, 2026-11-08: guard it the same way _saved_group is guarded above (line ~964) —
            # on a data analysis recipe switch, _saved_subtab is the OLD recipe's plot id and will
            # not match any of THIS group's plot_ids. Passing it anyway hands Bootstrap/Shiny a
            # selected= value matching no real nav_panel: the first tab's header still looks active
            # (default styling) but no pane is genuinely marked shown server-side, so the plot output
            # never fires and stays blank until the user clicks a tab (forcing a real selection event).
            _subtab_valid = _saved_subtab in {f"subtab_{p}" for p in plot_ids}
            plots_card = (
                ui.navset_card_tab(*plot_subtabs, id=f"subtabs_{safe_sub_id}",
                                   selected=_saved_subtab if _subtab_valid else None)
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
            ui.output_ui("compare_switch_ui"),
            ui.output_ui("lineage_panel_ui"),
            groups_nav,
            data_preview_section,
            class_="theater-container-main"
        )

    @output
    @render.ui
    def data_strip_ui():
        """The data choice "Table to view: Source | T1 | T2 | T3" and the source-table list (slice B, D-0016, D-0310). Exploration only: in Audit mode this output is empty, because
        the table shown follows the place chosen in "Path of the data" (slice 3a). It reads the mode only; the choice itself is read isolated (R4), and Exploration keeps its choice
        while Audit mode is open (HOM-08: the value is the reactive `data_view`)."""
        if not bootloader.is_enabled("interactivity_enabled") or _in_audit():
            return ui.div()

        def _tier_label(label: str, sub: str, tooltip: str) -> object:
            return ui.HTML(
                f'<span title="{tooltip}">'
                f'{label}<br>'
                f'<span style="font-size:0.65em;color:#9ca3af;font-weight:400">{sub}</span>'
                f'</span>'
            )

        # PROVISIONAL (slice B, the coordinator's wording; the owner reads it): the texts of the data choice
        data_choices = {
            "SRC": _tier_label(
                "Source",
                "as read from the file",
                "Source: one source table as read from its file with its declared types, before any step of the recipe. "
                "A second list names the source tables that feed this plot.",
            ),
            "T1": _tier_label(
                "T1",
                "after tier 1",
                "T1: the table the open plot reads, after the tier-1 steps of the recipe (cleaning, joins).",
            ),
            "T2": _tier_label(
                "T2",
                "after tier 2",
                "T2: the same table after the tier-2 steps of the recipe. If the recipe has none, T2 = T1.",
            ),
            "T3": _tier_label(
                "T3",
                "the table the plot shows",
                "T3: the Result data, the table the plot is drawn from: T2 plus the plot's own tier-3 steps of the recipe. If it has none, T3 = T2.",
            ),
        }
        with reactive.isolate():
            _cur_data_view = data_view.get()
        return ui.div(
            ui.div(
                ui.tags.span("Table to view:", class_="fw-semibold me-3 spv-strip-label"),
                ui.input_radio_buttons(
                    "data_view", label=None, choices=data_choices,
                    selected=_cur_data_view if _cur_data_view in data_choices else "T3", inline=True),
                class_="d-flex align-items-center",
            ),
            ui.output_ui("source_table_ui"),
            class_="theater-header-strip spv-header-strip-rows",
        )

    # Slice B: what the radios and the switch of the header strip say is copied into the reactive values the handlers read
    # (`home_mode`, `data_view`, `source_table`, `_audit_compare`). An input that is not on the page (another workspace is open, or the
    # strip has no such row) reports nothing and changes nothing. The values are read isolated: this effect follows the inputs only, so a
    # value set from the server (a restored session, a rebuilt strip) is not undone by the older value of an input still on the page.
    @reactive.Effect
    def _track_view_inputs():
        mode = safe_input(input, "home_mode", None)
        view = safe_input(input, "data_view", None)
        pick = safe_input(input, "source_table", None)
        compare = safe_input(input, "audit_compare", None)
        with reactive.isolate():
            if mode in ("exploration", "audit") and (mode == "exploration" or _audit_available()) and home_mode.get() != mode:
                home_mode.set(mode)
            if view in ("SRC", "T1", "T2", "T3") and data_view.get() != view:
                data_view.set(view)
            if pick and source_table.get() != pick:
                source_table.set(pick)
            if compare is not None and _audit_compare.get() != bool(compare):
                _audit_compare.set(bool(compare))

    # The right panel follows the mode in HOME (D-0375, D-0385): closed in Exploration, open in Audit mode, closed again when the user leaves
    # Audit mode. The other user spaces keep it open (D-0381). The rule is the pure function `frame_widths.right_panel_open`. The effect
    # follows the user space and the mode only; it sends a change only when the answer differs from the one it sent last (R3), so a panel the
    # user opened by hand stays as she left it until the mode or the user space changes. Where the panel is not in the page (ADR-044) there
    # is nothing to drive.
    _right_panel_sent = {"open": None}

    @reactive.Effect
    def _drive_right_panel():
        space = safe_input(input, "sidebar_nav", frame_widths.HOME)
        mode = home_mode.get()
        if not bootloader.get_sidebar_config("home", "right").visible:
            return
        wanted = frame_widths.right_panel_open(space, mode, _audit_available())
        with reactive.isolate():
            if _right_panel_sent["open"] is wanted:
                return
            _right_panel_sent["open"] = wanted
        ui.update_sidebar("audit_sidebar", show=wanted)

    # P-B5 (PROVISIONAL, the coordinator's choice): a restored session that holds audit steps opens Audit mode, so that the user sees the
    # audited plot the steps were made for. The restore (`session_handlers._restore_session`) writes `t3_ghost_file` into `home_state`, and
    # only a restore does; this effect follows a change of it. A second restore of the same file does not change it, so it opens nothing.
    _seen_ghost_file = {"file": None}

    @reactive.Effect
    def _open_audit_mode_after_restore():
        if home_state is None:
            return
        ghost_file = home_state.get().get("t3_ghost_file")
        with reactive.isolate():
            previous, _seen_ghost_file["file"] = _seen_ghost_file["file"], ghost_file
            if not ghost_file or ghost_file == previous or not _audit_available():
                return
            restored = place_nodes(home_state.get().get("t3_audit_steps_by_plot", {}) or {})
            if restored and home_mode.get() != "audit":
                home_mode.set("audit")
                ui.update_radio_buttons("home_mode", selected="audit")
            if restored and _audit_available():
                # slice 3a (PROVISIONAL): a restored session shows what the open tab's plot reads (nothing shown yet, the default), so that Send to Audit keeps writing at the open plot, and the
                # band says that the restored steps are applied (the design page proposed the first plot of the recipe: the plot area shows the open tab's plot, so the two would disagree)
                shown_item.set(None)
                restored_steps.set(len({n.get("id") for n in restored}))

    # The shown item is forgotten when Audit mode is left or the recipe changes: it is not saved (D-0302), and a place of another recipe means nothing. Idempotent (R3).
    _shown_recipe = {"id": None, "mode": None}

    @reactive.Effect
    def _forget_shown_item():
        mode = safe_input(input, "home_mode", None)      # the control the user moves, not `home_mode`: see below
        recipe = safe_input(input, "data_analysis_recipe_id", None)
        with reactive.isolate():
            changed = _shown_recipe["id"] is not None and recipe is not None and recipe != _shown_recipe["id"]
            if recipe is not None:
                _shown_recipe["id"] = recipe
            # only the USER's leave of Audit mode forgets: the control goes from "audit" to "exploration". A restore sets `home_mode` and the shown item from the server, and the effect that
            # copies the control into `home_mode` puts "exploration" back for a moment before the control is updated: reading `home_mode` here took that moment for a leave and wiped the
            # shown item and the note of the restored session (found by `test_shiny_session_restore.py`)
            left = _shown_recipe["mode"] == "audit" and mode == "exploration"
            if mode is not None:
                _shown_recipe["mode"] = mode
            if left or changed:
                if shown_item.get() is not None:
                    shown_item.set(None)
                if restored_steps.get():
                    restored_steps.set(0)

    # AUDIT-STEPS-SURVIVE-RECIPE-CHANGE (found by `app/tests/test_audit_steps_survive_recipe_change.py`: the steps of recipe A showed in recipe B, 42 rows became 38): an audit step is written
    # at a table or plot BY NAME, so the steps of the recipe that was open must not stay in the state when another recipe is selected: the other recipe may hold a table or plot of the
    # same name, and its table would change without a word (D-0050). The steps are in the session of their own recipe (a step is saved when it is applied, D-0302) and Restore brings them
    # back (D-0317). The words are PROVISIONAL.
    _steps_recipe = {"id": None}

    @reactive.Effect
    def _drop_audit_steps_on_recipe_change():
        recipe = safe_input(input, "data_analysis_recipe_id", None)
        if home_state is None or recipe is None:
            return
        with reactive.isolate():
            previous, _steps_recipe["id"] = _steps_recipe["id"], recipe
            if previous is None or previous == recipe:
                return
            cur = home_state.get()
            n = len({n.get("id") for n in place_nodes(cur.get("t3_audit_steps_by_plot", {}) or {})}) + len({n.get("id") for n in cur.get("_pending_t3_nodes", []) or []})
            if not n:
                return
            home_state.set({**cur, "t3_audit_steps_by_plot": {}, "_pending_t3_nodes": []})
            _notify(f"The audit steps of the recipe '{previous}' ({n}) were not carried over to '{recipe}': a step is written at a table or a plot by name, and another recipe "
                    f"can hold one of the same name. They stay in the session of '{previous}': open that recipe and restore its session to get them back.", type="warning", duration=15)

    # A click on a plot tab in Audit mode shows that plot (interim: the tabs go in the next slice; D-0655 point 3, D-0657). The effect follows the open tab only, so entering
    # Audit mode on a tab shows that plot by default, and a click on the tab already open does nothing (a tab that does not change is not an event).
    @reactive.Effect
    def _tab_shows_its_plot():
        subtab = active_home_subtab.get()
        with reactive.isolate():
            if not subtab or not _in_audit():
                return
            node = shown_node_of_tab(subtab.removeprefix("subtab_"))
            if shown_item.get() != node:
                shown_item.set(node)

    @output
    @render.ui
    def shown_band_ui():
        """The band above the data preview in Audit mode: what is shown, original or audited, how many other places are chosen but not shown (slice 3a; PROVISIONAL words). Its own
        output (R4): it reads the shown item, the choice and the steps, and mounts no input."""
        if not _in_audit():
            return ui.div()
        chosen = safe_input(input, "lineage_chosen", [])
        chosen = [chosen] if isinstance(chosen, str) else [c for c in (chosen or []) if isinstance(c, str)]
        try:
            lf, facts, shown = _audit_shown_table()
        except SilentException:
            raise
        except Exception as exc:
            shown = _audit_viewed_safe()
            if shown is None:
                return ui.div(ui.tags.span("What is shown cannot be told: the recipe cannot be read.", class_="spv-shown-band-line"), class_="spv-shown-band")
            name = _shown_name(shown)
            return ui.div(ui.tags.span(f"Shown: {name}. This table cannot be built now (see the table below).", class_="spv-shown-band-line"), class_="spv-shown-band")
        others = others_chosen(chosen, shown.place)
        lines = band_lines(_shown_name(shown), facts, others, shown.from_open_plot, restored_steps.get())
        return ui.div(*[ui.tags.span(line, class_="spv-shown-band-line") for line in lines], class_="spv-shown-band", role="status")

    @output
    @render.ui
    def source_table_ui():
        """The second list of the strip: the source tables that feed the open plot, only while the Source choice is on. Reads the data choice, the
        open plot and the recipe; the pick itself is read isolated (R4: the list does not read what it mounts)."""
        if data_view.get() != "SRC":
            return ui.div()
        p_id = _open_plot_id()
        try:
            tables = _source_tables_of(p_id)
        except Exception as exc:
            _report_plot_exception(exc, "RecipeGraph", f"source tables of plot '{p_id}'")
            return ui.div(ui.tags.small(f"The source tables of this plot cannot be listed: {exc}", class_="text-danger"),
                          class_="d-flex align-items-center")
        if not tables:
            return ui.div(ui.tags.small("No source table feeds this plot.", class_="text-muted"), class_="d-flex align-items-center")
        with reactive.isolate():
            picked = source_table.get()
        return ui.div(
            ui.tags.span("Source table:", class_="fw-semibold me-3 spv-strip-label"),
            ui.input_select("source_table", label=None, choices=tables, selected=picked if picked in tables else tables[0]),
            class_="d-flex align-items-center",
        )

    @output
    @render.ui
    def mode_caption_ui():
        """One line under the title and the mode control that says what the open mode does. Its own output (R4): it reads the mode, which the
        control it sits beside feeds, and the control itself is not redrawn by it."""
        if _in_audit():
            text = "Audit: your steps change the plot and the export, and are saved with the session."
        else:
            text = "Exploration: look at the data. Filters change the table you view, never a plot. Nothing here is saved."
        return ui.tags.small(text, class_="text-muted spv-mode-caption", title=text)

    @output
    @render.ui
    def compare_switch_ui():
        """The Compare switch, ONE for the whole plot area (a line above the group tabs, shared by all plots; above the lineage panel too, because that panel draws
        a moment after the mode changes and would push a switch below it down while the user is clicking it): only in Audit mode and with
        `comparison_mode_enabled`; absent otherwise, never greyed. It is not in the per-plot cell: each cell reads the compare value, and one input
        id would be mounted once per plot (R4). The value is read isolated, so the switch does not redraw itself."""
        if not (_in_audit() and bootloader.is_enabled("comparison_mode_enabled")):
            return ui.div()
        with reactive.isolate():
            compare_on = _audit_compare.get()
        return ui.div(
            ui.input_switch("audit_compare", "Compare with the original", value=compare_on),
            class_="spv-compare-line",
        )

    # ADR-045 R1: anchor_path.set() must not live inside dynamic_tabs render.
    # This effect reacts to the same inputs and writes with an idempotent guard.
    @reactive.Effect
    def _sync_anchor_path():
        opening_state.get()   # the opening stores the first table: look again when it finished
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
    # What the effect told the user and has not told again (D-0050): it re-runs whenever a box it reads changes, so a failure
    # that lasts is told once; after a pass without it, the same failure is told again.
    _provenance_told: dict[str, str | None] = {"keys": None, "record": None}

    def _isolated_notify(text: str, type_: str, duration: int) -> None:
        with reactive.isolate():
            _notify(text, type=type_, duration=duration)

    def _tell_provenance_failure(stage: str, text: str) -> None:
        if _provenance_told[stage] != text:
            _provenance_told[stage] = text
            with reactive.isolate():      # `_notify` reads and sets the notification log: the effect must not depend on it
                _notify(text, type="error", duration=12)

    @reactive.Effect
    def _sync_session_provenance():
        if home_state is None:
            return
        # issue #38: this @reactive.Effect runs unconditionally once registered, regardless of
        # which workspace/accordion is visible — not gated behind the dynamic_tabs() Home
        # branch like most other calls here. Must not raise when there is no usable recipe.
        data_analysis_recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe_or_none())
        if not data_analysis_recipe_id:
            return
        try:
            from app.modules.session_manager import SessionManager as _SM
            from app.modules.session_manager import LegacySessionError, extract_primary_keys
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
                # The keys of the view are computed once (`_data_analysis_recipe_keys`): unless an import of this
                # session recomputed them, the tables on screen still come from the earlier files.
                try:
                    with reactive.isolate():
                        view_dbh = _data_analysis_recipe_keys().data_batch_hash
                except Exception:
                    view_dbh = None
                with reactive.isolate():
                    _notify("⚠️ " + notice_after_data_change(view_dbh, new_dbh), type="warning", duration=12)
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
                        on_problem=lambda text: _isolated_notify("⚠️ " + text, "warning", 10),
                    )
                    _provenance_told["record"] = None
                except LegacySessionError:
                    # PROVISIONAL (the coordinator's text, D-0312; the owner reads it): an older session with the same recipe and data is stored.
                    # The generic remedy below (check that the folder can be written) would be wrong: what helps is deleting the old session.
                    _tell_provenance_failure("record", "⚠️ " + LEGACY_RECORD_NOTICE)
                except Exception as exc:
                    _tell_provenance_failure("record", "⚠️ " + notice(
                        "The record of this session could not be written, so the session cannot be exported or restored "
                        "from the Session Management panel", "check that the user data folder can be written, then change "
                        "the recipe or data box again (the record is written again at every change)", exc))
            _provenance_told["keys"] = None
        except Exception as exc:
            _tell_provenance_failure("keys", "⚠️ " + notice(
                "The recipe and data keys of this session could not be computed, so audit steps cannot be saved and a saved "
                "session cannot be compared until they can", "check that the recipe file and the data files can be read, "
                "then pick the recipe again", exc))

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

    def _preview_lf(spec, p_id):
        """The lazy table the data preview shows the head of: the view's table, then (Audit mode, T3) the audited steps, or (Exploration) the
        filters built on this view. The grid and the badge's row count both read it, so the count is the count of what the grid is cut from
        (D-0488). Raises what the table raises (an audit step that cannot run, a read error): each caller decides what to show."""
        lf = _resolve_active_lf(spec)
        # ADR-098 (issue #56), D-0311: exploration filters change the table of the view shown (Source, T1, T2 or T3), never saved and
        # never a plot. They do not exist in Audit mode, where T3 is the audited table.
        # PLOT-TABLE-ORDER-1: in Audit mode the T3 table is the table of the audit copy (`_resolve_active_lf`): the plot's table after the audit steps of every tier,
        # the same table as the audited plot and the results bundle. A step that cannot run raises (`AUDIT_ERRORS`): it is shown below in the table's place and in the
        # Alerts panel, never skipped.
        if not _in_audit():
            # review F3: only the filters built on this very view; one built on another table is not applied, whatever the clearing effect did
            lf = _apply_filter_rows(lf, _applied_for_view())
        return lf

    def _dropped_columns(p_id: str | None) -> list[str]:
        """The columns the committed audit steps of this plot drop (a column drop written at any tier it is built from): what the audited table no longer has."""
        return [str((n.get("params") or {}).get("column")) for n in _audit_nodes_for(p_id) if n.get("node_type") == "drop_column" and (n.get("params") or {}).get("column")]

    def _chooser_key(p_id: str | None) -> str | None:
        """The key of the table the column chooser is built for: everything `home_col_selector_ui` depends on (the open recipe and the data it
        was built on, the plot, the data choice, the source table, the audited drops of Audit mode on T3). The chooser emits it with itself
        and the badge compares it with the key of the table now shown; one function gives both, so they cannot differ (D-0050). The recipe
        part is the id the keys are computed for and the two hashes of `_data_analysis_recipe_keys` (the same reactive source the tables are
        read through, so a recipe switch or a data refresh changes it and the chooser, which calls this function, depends on it): after a
        switch of recipe the old plot id and the old names must not be taken for the new table's. When the recipe keys cannot be read there
        is NO key (None): a failed key must never equal another key, or a hidden-columns sentence could be said about the wrong table
        (D-0050). The table's place shows why the recipe cannot be read."""
        try:
            keys = _data_analysis_recipe_keys()
            recipe_part = f"{safe_input(input, 'data_analysis_recipe_id', '')}@{keys.data_analysis_recipe_sha256[:12]}:{keys.data_batch_hash[:12]}"
        except Exception:
            return None
        if _in_audit():
            # Audit mode (slice 3a): the table is the one SHOWN. The key of the view holds the table, its tier and the digest of its columns; the signature of the audit steps is added so
            # that another set of steps (another table, maybe other columns) is another chooser.
            try:
                audited = repr(nodes_signature(_committed_place_nodes()))
            except Exception:
                audited = "?"
            # no quotation mark in the key: it travels in an HTML attribute (the chooser emits it with itself)
            return "|".join((recipe_part, "audit", repr(_current_view_key()).replace("'", ""), audited.replace("'", "")))
        view = data_view.get()
        try:
            table = _effective_source_table(p_id) if view == "SRC" else ""
        except Exception:
            table = ""
        audit_t3 = _in_audit() and view == "T3"
        # the columns the audit steps drop from this table: the chooser is built again when they change (a filter does not change its columns)
        drops = ",".join(sorted(_dropped_columns(p_id))) if audit_t3 else ""
        # in Audit mode the T1 and T2 views are the audit copy's tables: another set of audit steps is another table (and another list of columns)
        audited_view = ""
        if _in_audit() and view in ("T1", "T2"):
            try:
                audited_view = repr(nodes_signature(_committed_place_nodes()))
            except Exception:
                audited_view = "?"
        return "|".join((recipe_part, str(p_id), view, str(table), "audit" if audit_t3 else "view", drops, audited_view))

    @output
    @render.ui
    def home_data_preview_badge():
        """What the data preview shows now (issue #17). Its own output: a filter change redraws only
        this badge, not the table. Reads the data choice, the mode and the active plot."""
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        if not bootloader.is_enabled("interactivity_enabled"):
            # no view choice and no column chooser here, but the preview still says how many rows the table has (D-0488)
            try:
                note = row_count_note(int(_preview_lf(spec, p_id).select(pl.len()).collect().item()),
                                      bool(safe_input(input, "preview_all_rows", False)))
            except Exception:
                note = None
            return ui.div(ui.tags.span(note, class_="spv-view-note"), class_="spv-view-badge-row") if note else ui.div()
        shown_item_view = None
        audit_state = None          # Audit mode: True when the table shown is the audited one, False when it is the original (T1 and T2 only)
        audit_steps = _audited_step_count(subtab)
        has_plot_own_steps = has_plot_steps(active_cfg().raw_config, p_id)
        if _in_audit():
            # Audit mode (slice 3a): the badge describes the item SHOWN, not the open plot's table
            shown_item_view = _audit_viewed_safe()
            if shown_item_view is None or shown_item_view.nothing_chosen or not shown_item_view.table:
                return ui.div()
            has_t2 = has_tier2_steps(active_cfg().raw_config, shown_item_view.table)
            has_plot_own_steps = has_plot_steps(active_cfg().raw_config, shown_item_view.shown_plot)
            audit_steps = _audited_step_count(f"subtab_{shown_item_view.shown_plot}") if shown_item_view.shown_plot else 0
            view = shown_item_view.tier
            try:
                audit_state = (_audit_shown_table()[1].state == AUDITED) if view in ("T1", "T2") else None
            except Exception:
                audit_state = None
        else:
            has_t2 = has_tier2_steps(active_cfg().raw_config, (spec or {}).get("target_dataset"))
            view = data_view.get()
        try:
            table = _effective_source_table(p_id) if view == "SRC" else None
        except Exception:
            table = None   # the table itself says why it cannot be shown
        # D-0488: rows and hidden columns of exactly the table the grid is cut from. A table that cannot be built gives no sentence: the grid
        # shows (and reports) the error in the table's place, the badge stays quiet so that the error is neither hidden nor repeated.
        total_rows, hidden = None, 0
        try:
            lf = _preview_lf(spec, p_id)
            total_rows = int(lf.select(pl.len()).collect().item())   # a lazy count: the table is not held in memory
            chosen = safe_input(input, "preview_col_selector", None)
            # The chooser's value says nothing about the table it was built for, so the chooser carries the key of that table (a hidden input
            # that comes back with it, `_chooser_key`). Right after a switch of table or plot tab (one to two seconds) the chooser still
            # belongs to the PREVIOUS table: its names may all exist in the new one, and "N columns hidden" would say that the user hid columns
            # he did not hide (D-0050). Only a chooser built for the table now shown is read.
            built_for = safe_input(input, "preview_col_selector_key", None)
            now_key = _chooser_key(p_id)
            if chosen and isinstance(chosen, (list, tuple)) and now_key is not None and built_for == now_key:
                names = lf.collect_schema().names()
                kept = [c for c in names if c in chosen]
                # an empty choice shows every column, as the grid does
                hidden = 0 if not kept else len(names) - len(kept)
        except Exception:
            total_rows, hidden = None, 0
        return _badge_ui(view_badge(view, has_t2, has_plot_own_steps, len(_applied_for_view()),
                                   mode="audit" if _in_audit() else "exploration", audited_steps=audit_steps,
                                   source_table=table, total_rows=total_rows, all_rows=bool(safe_input(input, "preview_all_rows", False)),
                                   hidden_columns=hidden, audit_view=audit_state if _in_audit() else _audit_view_state(spec, view)))

    @output
    @render.text
    def home_data_preview_title():
        """Accordion title; states the 100-row cap unless 'All rows' is on. Reads only preview_all_rows (ADR-045 R4)."""
        caps = "" if safe_input(input, "preview_all_rows", False) else f" (max. first {PREVIEW_ROW_LIMIT} rows)"
        if _in_audit():
            # Audit mode: the title names the item shown (slice 3a), in the words of the lineage panel
            shown = _audit_viewed_safe()
            if shown is not None and not shown.nothing_chosen and shown.table:
                return f"Data Preview: {_shown_name(shown)}{caps}"
        return "Data Preview" + caps

    # Phase 21-D/F: Data preview — scoped to the table the active plot reads, with filters + col selector.
    @output
    @render.data_frame
    def home_data_preview():
        """Preview for the table the active plot reads. Applies committed filters + col selector.
        PREVIEW-ALLROWS-1: capped at 100 rows by default; toggle 'preview_all_rows' to uncap."""
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)

        try:
            lf = _preview_lf(spec, p_id)
            # PREVIEW-ALLROWS-1: respect the "Show all rows" toggle; default 100-row cap.
            show_all = safe_input(input, "preview_all_rows", False)
            df = lf.collect() if show_all else lf.head(PREVIEW_ROW_LIMIT).collect()

            # Apply column visibility selection (Phase 21-F-4) — preview-only filter
            visible = safe_input(input, "preview_col_selector", None)
            if visible and isinstance(visible, (list, tuple)):
                visible_cols = [c for c in visible if c in df.columns]
                if visible_cols:
                    df = df.select(visible_cols)

            # summary off: the grid counts the table it is handed (the first 100 rows), so "of 100" would read as the table's total; the badge says the size (D-0488)
            return render.DataGrid(df, filters=False, height="300px", summary=False)
        except Exception as e:
            if isinstance(e, AUDIT_ERRORS):
                _report_plot_exception(e, "T3Audit", "audit steps of the data preview")
            elif data_view.get() == "SRC":
                # the source table could not be read or listed: the plain text of the error, in the Alerts panel as well as in the table's place
                _report_plot_exception(e, "DataOrchestrator", f"read_source(plot_id='{p_id}')")
            return render.DataGrid(
                pl.DataFrame({"Error": [plot_read_error_text(active_cfg().raw_config, p_id, e) if p_id else str(e)]}),
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
            # HOM-41 fix: audited drops remove columns from the T3 table in Audit mode only — every other view is the table as it is. The table
            # of the audit copy already lacks them: the chooser lists the columns of the table it is shown with.
            audit_t3 = _in_audit() and _audit_write_ok()
            cols = list(lf.collect_schema().names())
            # Dropping via audit exists in Audit mode on T3 only.
            label_text = (
                "Columns (drop unselected via audit):"
                if audit_t3
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
                # the table this chooser was built for, read by the preview badge (see `_chooser_key`)
                ui.div(ui.input_text("preview_col_selector_key", None, value=_chooser_key(p_id) or ""), style="display:none;"),
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
        # Slice B (P-B3): a column drop is an audit step; it is offered in Audit mode while T3 is viewed (an audit step is written at the
        # plot's table). In Exploration there is nothing to send drops to - no button.
        if not (_in_audit() and _audit_write_ok()):
            return ui.span()
        subtab = active_home_subtab.get()
        p_id = subtab.removeprefix("subtab_") if subtab else None
        spec = _resolve_active_spec(p_id)
        try:
            lf = _resolve_active_lf(spec, tier="T3")
        except Exception:
            return ui.span()
        cols = list(lf.collect_schema().names())    # the audited table: a column an audit step dropped is not in it
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
            nav_items.append(ui.nav_panel("Blueprint Architect", value=frame_widths.BLUEPRINT))

        if bootloader.is_enabled("test_lab_enabled"):
            nav_items.append(ui.nav_panel("Test Lab", value="Test Lab"))

        if bootloader.is_enabled("gallery_enabled"):
            nav_items.append(ui.nav_panel("Gallery", value="Gallery"))

        badge = (
            ui.h6(f"Active: {perm}",
                  class_="text-muted px-2 py-1 mb-1 border-bottom spv-text-meta")
            if bootloader.is_enabled("show_app_features_badge")
            else None
        )
        # Eve, 2026-11-08: one compact icon row, not three stacked full-width buttons.
        # Tooltips (title=) carry the label instead of button text.
        help_btn = ui.input_action_button(
            "btn_help_ws", ui.tags.i(class_="bi bi-question-circle"),
            class_="btn btn-outline-secondary btn-sm flex-fill",
            title="Quick help for this workspace",
        )
        # ADR-096: gated independently of the modal above — on whether `quarto render
        # docs/` was run for this deployment, so quick help keeps working even when the
        # book wasn't built. Opens the book root, new tab.
        docs_link = (
            ui.tags.a(
                ui.tags.i(class_="bi bi-book"),
                href="/docs/index.html", target="_blank",
                title="Full documentation (opens in a new tab)",
                class_="btn btn-outline-secondary btn-sm flex-fill",
            )
            if _DOCS_AVAILABLE else None
        )
        # Left Navigation stack, not the right sidebar — same reachability reasoning as
        # ui_reachability_map.md. Links to Eve's fork (where issues are actually filed),
        # not the upstream org docs/_quarto.yml's repo-url points at.
        github_link = ui.tags.a(
            ui.tags.i(class_="bi bi-github"),
            href=_GITHUB_REPO_URL, target="_blank",
            title="SPARMVET_VIZ on GitHub — file an issue, browse the source",
            class_="btn btn-outline-secondary btn-sm flex-fill",
        )
        return ui.div(
            ui.navset_pill(
                *nav_items,
                id="sidebar_nav",
                header=badge,
            ),
            ui.div(help_btn, docs_link, github_link, class_="d-flex gap-1 mt-2"),
        )

    # HELP-INLINE-1: workspace help modal
    _HELP_DIR = Path(__file__).parent.parent / "src" / "help"

    @reactive.Effect
    @reactive.event(input.btn_help_ws)
    def _show_workspace_help():
        ws = safe_input(input, "sidebar_nav", "Home")
        _ws_file_map = {
            "Home": "home.md",
            frame_widths.BLUEPRINT: "blueprint.md",
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

    # The open user space as a value of its own (D-0502). Before the page has told the server its `sidebar_nav` the read gives the
    # default "Home"; when the input arrives with the same value the sidebar must not be drawn again. A render that reads the input
    # itself is invalidated by that first arrival and closes the panels the user opened in the meantime. The effect writes only
    # when the space really changes (section 14, R3), so the render below follows changes of the space and nothing else.
    _active_space = reactive.Value(frame_widths.HOME)

    @reactive.Effect
    def _sync_active_space():
        now = safe_input(input, "sidebar_nav", frame_widths.HOME)
        with reactive.isolate():
            if _active_space.get() != now:
                _active_space.set(now)

    # What the last draw of the left sidebar held (plain memory of the render, not a reactive value: nothing reads it reactively)
    _left_drawn = {"space": None, "existing": None}

    def _user_open_panels():
        """The panels the page says are open in the left accordion, or None when the page has not said yet.

        Read isolated: the answer is only kept, so a click on a panel must not draw the sidebar again (section 14, R4). The
        accordion input is absent before the page has sent it (SilentException); an empty selection is an answer (nothing open).
        """
        with reactive.isolate():
            try:
                value = input.nav_accordion()
            except SilentException:
                return None
        if value is None:
            return []
        return [value] if isinstance(value, str) else list(value)

    # 4. Sidebar Tools (Contextual Data analysis recipe Workbench)
    @output(id="sidebar_tools_ui")
    @render.ui
    def sidebar_tools_ui():
        """
        Relocated Sidebar Management (ADR-038).
        Enforces dedicated App features based control clusters.
        """
        active_sidebar = _active_space.get()

        # Gallery's left sidebar is now built via _build_left_sidebar("gallery", ...)
        # further down (issue #42, "gallery_main" freestanding panel type) — see the
        # `if active_sidebar == "Gallery":` branch below the registry helper.

        # Data analysis recipe Workbench (Wrangle Studio)
        # Blueprint's left sidebar is now built via _build_left_sidebar("blueprint", ...)
        # further down (issue #42, "blueprint_main" freestanding panel type, content
        # moved to WrangleStudio.build_sidebar_ui()) — see the
        # `if active_sidebar == frame_widths.BLUEPRINT:` branch below the registry helper.

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

        def _render_test_lab_info():
            """Test Lab's own Info panel — Eve, 2026-11-08: deliberately distinct from
            data_analysis_recipe_info. Test Lab tools don't operate on an open data
            analysis recipe at all, so showing recipe info: content here is actively
            wrong, not just unused. Empty placeholder for now — Test Lab's own panels
            aren't finished yet either, so this isn't filled in prematurely; reserved
            for Test-Lab-specific instructions once that's decided."""
            return ui.accordion_panel(
                "Info",
                ui.p("Test Lab tools — instructions coming soon.",
                     class_="text-muted small p-2 mb-0"),
                icon=ui.tags.i(class_="bi bi-info-circle-fill")
            )

        def _render_deployment_info():
            banner = bootloader.get_ui_banner()
            if not banner:
                return None
            return ui.accordion_panel(
                "Deployment",
                ui.div(
                    ui.tags.small(banner.get("ui_label", ""), class_="fw-bold d-block"),
                    ui.tags.small(banner.get("description", ""), class_="text-muted d-block"),
                    class_="p-1"
                ),
                icon=ui.tags.i(class_="bi bi-building")
            )

        def _render_data_analysis_recipe_choice():
            """The selector, and a slot for the notes under it (what is unavailable and why, advices). The notes follow the
            load gate (recipe_gate_handlers.py, GATE-GAP-1) without rebuilding the selector the user is using (R4)."""
            return ui.accordion_panel(
                "Data analysis recipe Choice",
                ui.div(
                    ui.input_select("data_analysis_recipe_id", "Data analysis recipe",
                                    choices=data_analysis_recipe_choices,
                                    selected=_current_data_analysis_recipe),
                    ui.output_ui("recipe_gate_notes_ui"),
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
            # VOCAB NOTE (issue #54, 2026-11-10): the visible label is "Export / Import" but the
            # panel TYPE key stays "export" everywhere else (sidebar_registry.py,
            # config/ui/sidebars/*.yaml `type: export`, this function's name, PANEL_REGISTRY's
            # gate flag export_enabled). Renaming the key too would be a larger, riskier config
            # migration across every app features template for a label-only change -- not worth
            # it. If you're hunting for "Export / Import" in code and only finding "export", this
            # is why. UML cross-reference: UI-HOME wireframe, the panel named
            # "Export / Import: ..." (docs/UML/app.mdj).
            return ui.accordion_panel(
                "Export / Import",
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
            "test_lab_info":      _render_test_lab_info,
            "deployment_info":    _render_deployment_info,
            "data_analysis_recipe_choice":    _render_data_analysis_recipe_choice,
            "filters":            _render_filters,
            "data_import":        _render_data_import,
            "export":             _render_export,
            "session_management": _render_session_management,
        }

        def _render_gallery_main():
            # Isolated: the shell must not re-render when the Gallery state changes (section 14, rule R4).
            with reactive.isolate():
                return gallery_viewer.build_sidebar_ui(gallery_state.get() if gallery_state is not None else None)

        def _render_blueprint_main():
            return wrangle_studio.build_sidebar_ui()

        # Freestanding panel types (issue #42): the renderer returns a complete,
        # already-formed UI block (its own accordion, its own id) rather than a
        # single ui.accordion_panel() to merge into the shared nav_accordion. Needed
        # for workspaces whose sidebar content is itself one cohesive, bespoke unit
        # (Gallery's taxonomy/search, Blueprint's recipe editor) rather than a list of
        # independent generic panels.
        _left_freestanding_renderers = {
            "gallery_main": _render_gallery_main,
            "blueprint_main": _render_blueprint_main,
        }

        def _build_left_sidebar(workspace_key: str, open_panels: list[str], keep_user_panels: bool = False):
            """Build the left sidebar from a workspace's slot list (ADR-073, extended
            issue #42 to cover every workspace, not just Home/Test Lab).

            keep_user_panels (HOME, D-0502): when the sidebar of the same user space is drawn again, the panels the user has open
            and closed stay as they are; `open_panels` (the fixed list) decides only the first draw after a change of space and
            the panels that are new."""
            sidebar_cfg = bootloader.get_sidebar_config(workspace_key, "left")
            panels = []
            freestanding = []
            include_notification_log = False
            include_processing_issues = False
            for slot in sidebar_cfg.panels:
                ptype = slot.get("type", "")
                if ptype == "notification_log":
                    include_notification_log = True
                    continue
                if ptype == "processing_issues":
                    include_processing_issues = True
                    continue
                if not is_panel_active(ptype, bootloader):
                    continue
                if ptype in _left_freestanding_renderers:
                    block = _left_freestanding_renderers[ptype]()
                    if block is not None:
                        freestanding.append(block)
                    continue
                renderer = _left_panel_renderers.get(ptype)
                if renderer is None:
                    print(f"[home_theater] No renderer for panel type '{ptype}' — skipping.")
                    continue
                panel = renderer()
                if panel is not None:
                    panels.append(panel)
            if keep_user_panels:
                existing = [p._data_value for p in panels]
                same_space = _left_drawn["space"] == workspace_key
                open_panels = open_panels_after_redraw(
                    open_panels,
                    existing,
                    _left_drawn["existing"] if same_space else None,
                    _user_open_panels() if same_space else None,
                )
                _left_drawn["space"], _left_drawn["existing"] = workspace_key, existing
            else:
                _left_drawn["space"], _left_drawn["existing"] = workspace_key, None
            return ui.div(
                # Eve, 2026-11-08: Alerts sits between Navigation (above this whole block,
                # see ui.py) and the accordion, not after it — so it's seen first, not
                # buried under everything else. Moved here from Home's right sidebar
                # config at the same time (ui_reachability_map.md §5), same reasoning as
                # F-26/Processing Issues: the right sidebar doesn't exist at all in
                # pipeline-static/pipeline-exploration-simple.
                ui.output_ui("notification_log_panel_ui") if include_notification_log else ui.div(),
                ui.accordion(
                    *panels,
                    id="nav_accordion",
                    multiple=True,
                    open=open_panels,
                ) if panels else ui.div(),
                *freestanding,
                # F-26 / PROCESSING-ISSUES-RENAME-1: left sidebar, not right — the right
                # sidebar is structurally absent in pipeline-static/pipeline-exploration-simple
                # (ui_reachability_map.md §2), the left sidebar never is.
                ui.output_ui("processing_issues_ui") if include_processing_issues else ui.div(),
            )

        if active_sidebar == "Test Lab":
            return _build_left_sidebar("test_lab", open_panels=[])

        if active_sidebar == "Gallery":
            return _build_left_sidebar("gallery", open_panels=[])

        if active_sidebar == frame_widths.BLUEPRINT:
            return _build_left_sidebar("blueprint", open_panels=[])

        _has_data_analysis_recipe = bootloader.get_data_analysis_recipe_selector().get("visible", True)
        open_panels = ["Data analysis recipe Choice"] if _has_data_analysis_recipe else []
        return _build_left_sidebar("home", open_panels=open_panels, keep_user_panels=True)

    # --- Right Sidebar Context Matrix (ADR-039 / ADR-044) ---
    @output
    @render.ui
    def right_sidebar_content_ui():
        """
        Context-sensitive right sidebar (ADR-039, extended issue #42 Phase 3: every
        workspace's right sidebar now goes through a shared panel registry, same
        mechanism as the left side (ADR-073). Not identical wrapping, though — each
        workspace's outer CSS class and empty-state fallback differ today and that
        difference is preserved exactly, not unified away; see _build_right_sidebar.
        """
        active_sidebar = safe_input(input, "sidebar_nav", "Home")

        def _render_blueprint_surgeon():
            return ui.card(
                ui.card_header(
                    ui.div(ui.h5("Blueprint Surgeon", class_="mb-0"),
                           class_="d-flex justify-content-center w-100")
                ),
                ui.div(
                    ui.output_ui("bp_action_form_ui"),
                    class_="p-2"
                ),
                class_="mb-2 shadow-sm border-0"
            )

        def _render_blueprint_action_help():
            return ui.card(
                ui.card_header(
                    ui.div(ui.h5("Action Help", class_="mb-0"),
                           class_="d-flex justify-content-center w-100")
                ),
                ui.output_ui("bp_help_panel_ui"),
                class_="mb-2 shadow-sm border-0"
            )

        def _render_blueprint_plot_defaults():
            # VIZFAC-BLUEPRINT-FORM-1: plot_defaults editor (data analysis recipe root node)
            return ui.card(
                ui.card_header(
                    ui.div(ui.h5("Plot Defaults", class_="mb-0"),
                           class_="d-flex justify-content-center w-100")
                ),
                ui.output_ui("bp_plot_defaults_form_ui"),
                class_="mb-2 shadow-sm border-0"
            )

        def _render_blueprint_branch_node():
            # BP-BRANCH-NODE-1
            return ui.card(
                ui.card_header(
                    ui.div(ui.h5("Branch Node", class_="mb-0"),
                           class_="d-flex justify-content-center w-100")
                ),
                ui.output_ui("bp_branch_ui"),
                class_="mb-2 shadow-sm border-0"
            )

        def _render_blueprint_agent_chat():
            return ui.card(
                ui.card_header(
                    ui.div(ui.h5("Blueprint Agent", class_="mb-0"),
                           class_="d-flex justify-content-center w-100")
                ),
                ui.output_ui("blueprint_agent_panel_ui"),
                class_="mb-2 shadow-sm border-0 d-flex flex-column spv-flex-1-auto"
            )

        def _render_audit_stack():
            return ui.TagList(
                ui.card(
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
                ),
                ui.output_ui("audit_stack_tools_ui"),
                # The "Plot Style" panel (aesthetic_style_panel_ui, defined in audit_stack.py) is NOT
                # mounted: letting users change in HOME what the data analysis recipe defines is too much for
                # now, and using it broke the plot (test plan HOM-47). Its code is kept, unused, as
                # an eventual enhancement (fork issue #15). To bring it back, add
                # ui.output_ui("aesthetic_style_panel_ui") here, after fixing HOM-47.
            )

        def _render_gallery_right_info():
            return ui.card(
                ui.card_header(ui.h5("Gallery Explorer", class_="mb-0 text-center")),
                ui.div(
                    ui.p("📚 Browse visual examples.", class_="text-muted small p-2"),
                    ui.p("Select an example to see its picture, its recipe and its guidance. To reuse it, copy the recipe text by hand.",
                         class_="text-muted small px-2"),
                    class_="p-1"
                ),
                class_="mb-2 shadow-sm border-0"
            )

        def _render_test_lab_right_info():
            # VOCAB NOTE (issue #55, 2026-11-10): this function existed and was correct for
            # some time before it was reachable — the only thing missing was the slot list in
            # config/ui/sidebars/testlab_standard_right.yaml (visible:false, panels:[]). A
            # renderer having correct code is NOT evidence a panel is live: always check the
            # sidebar config too. GUARDED: test_shiny_smoke.py::TestPhase25Panels::
            # test_test_lab_right_sidebar_shows_the_tool_descriptions (mutation-tested against
            # the slot-config-only regression, not just this function breaking). UML
            # cross-reference: UI-TESTLAB wireframe, the "Right sidebar: ..." panel.
            return ui.accordion(
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
            )

        _right_panel_renderers = {
            "audit_stack":             _render_audit_stack,
            "blueprint_surgeon":       _render_blueprint_surgeon,
            "blueprint_action_help":   _render_blueprint_action_help,
            "blueprint_plot_defaults": _render_blueprint_plot_defaults,
            "blueprint_branch_node":   _render_blueprint_branch_node,
            "blueprint_agent_chat":    _render_blueprint_agent_chat,
            "gallery_right_info":      _render_gallery_right_info,
            "test_lab_right_info":     _render_test_lab_right_info,
        }

        def _build_right_sidebar(workspace_key: str) -> list:
            """Build the right sidebar's flat part list from a workspace's slot list
            (ADR-073, issue #42 Phase 3). Returns a list for the caller to wrap --
            each workspace keeps its own outer class and empty-state fallback, which
            differ today (Home/Blueprint: flex-column h-100; Gallery/Test Lab: plain)
            and are preserved exactly, not unified away."""
            sidebar_cfg = bootloader.get_sidebar_config(workspace_key, "right")
            parts = []
            for slot in sidebar_cfg.panels:
                ptype = slot.get("type", "")
                if ptype == "notification_log":
                    parts.append(ui.output_ui("notification_log_panel_ui"))
                    continue
                if not is_panel_active(ptype, bootloader):
                    continue
                renderer = _right_panel_renderers.get(ptype)
                if renderer is None:
                    print(f"[home_theater] No right-sidebar renderer for panel type '{ptype}' — skipping.")
                    continue
                block = renderer()
                if block is not None:
                    parts.append(block)
            return parts

        # --- Blueprint Architect (Wrangle Studio) ---
        if active_sidebar == frame_widths.BLUEPRINT:
            return ui.div(*_build_right_sidebar("blueprint"),
                           class_="sidebar-content p-0 d-flex flex-column h-100")

        # --- Home Theater (ADR-043 / ADR-044 / ADR-073) ---
        if active_sidebar in ("Home", None, ""):
            # D-0383: in Exploration the right panel (open by hand) is EMPTY: nothing of the audit panel is rendered there, not the
            # filter summary either. The panel renders again when Audit mode is chosen (it reads the mode, so it is rebuilt then).
            parts = _build_right_sidebar("home") if _in_audit() else []
            if not parts:
                return ui.div(class_="sidebar-content p-0")
            return ui.div(*parts, class_="sidebar-content p-0 d-flex flex-column h-100")

        # --- Gallery ---
        if active_sidebar == "Gallery":
            return ui.div(*_build_right_sidebar("gallery"), class_="sidebar-content p-0")

        # --- Test Lab ---
        if active_sidebar == "Test Lab":
            return ui.div(*_build_right_sidebar("test_lab"), class_="sidebar-content p-0")

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
        filters = _applied_for_view()
        t3_nodes: list[dict] = []
        if home_state is not None:
            active_sub = home_state.get().get("active_plot_subtab", "")
            t3_nodes = [n for n in _audit_nodes_for(active_sub) if n.get("node_type") in ("filter_row", "exclusion_row")]

        if not filters and not t3_nodes:
            return ui.div()

        _OP = {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
               "lt": "<", "le": "≤", "in": "∈", "not_in": "∉", "between": "↔"}

        def _fmt_val(v) -> str:
            if isinstance(v, (list, tuple)):
                items = [value_text(x) for x in v]
                suffix = f", +{len(items) - 3}" if len(items) > 3 else ""
                return "{" + ", ".join(items[:3]) + suffix + "}"
            s = value_text(v)
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
                    ui.span(f"🔍 {col} {op} {val} · {no_value_words(na_of(f), col)}", style=_MONO),
                    ui.span("sidebar", style=_BADGE_SB),
                    style=_ROW,
                ),
                f"Source: sidebar | {col} {op} {val} | {no_value_words(na_of(f), col)}",
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
                    ui.span(f"{pk_pfx}{icon} {col} {op} {val} · {no_value_words(na_of(p), col)}", style=_MONO),
                    ui.span("T3", style=_BADGE_T3),
                    style=_ROW,
                ),
                f"T3 audit | {col} {op} {val} | {no_value_words(na_of(p), col)} | Reason: {reason}",
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
        """Render the last-20 notifications as a collapsible accordion in the left sidebar,
        between Navigation and the panel accordion (moved from the right sidebar 2026-11-08 —
        Eve: the right sidebar doesn't exist at all in pipeline-static/pipeline-exploration-simple,
        see ui_reachability_map.md §5)."""
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

    # ── The opening of the recipe (D-0326): build, store, draw once ────────────
    if recipe_gate_version is not None:
        define_opening_server(
            input, output, session,
            bootloader=bootloader,
            orchestrator=orchestrator,
            viz_factory=viz_factory,
            safe_input=safe_input,
            view_keys=_data_analysis_recipe_keys,
            recipe_gate_version=recipe_gate_version,
            opening_state=opening_state,
            notify=_notify,
            shown_recipe=shown_recipe,
            id_run_state=id_run_state,
        )
    define_id_warning_server(input, output, session, bootloader=bootloader, safe_input=safe_input, id_run_state=id_run_state)

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
        screen_view=_screen_view_text,
        home_state=home_state,
        safe_input=safe_input,
        notification_log=notification_log,
        session_processing_issues=session_processing_issues,
        view_keys=_data_analysis_recipe_keys,
        audited_plot_table=_audited_t3_lf,
        in_audit=_in_audit,
        audit_run=_audit_run_for_export,
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
        session_processing_issues=session_processing_issues,
        recipe_raw=_recipe_raw,
        recipe_plans=_recipe_plans,
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
        in_audit=_in_audit,
        data_view=_view_for_handlers,
        audit_write_ok=_audit_write_ok,
        shown_place=_effective_shown_place,
        view_source_table=_view_source_table,
        current_view_key=_current_view_key,
        active_home_subtab=active_home_subtab,
        safe_input=safe_input,
        _resolve_active_spec=_resolve_active_spec,
        _resolve_active_lf=_resolve_active_lf,
        _spec_discrete_axes=_spec_discrete_axes,
        audit_nodes_for=_audit_nodes_for,
        _all_plot_subtab_ids=_all_plot_subtab_ids,
        _plot_label=_plot_label,
        _table_identity=_dialog_table_identity,
        notification_log=notification_log,
        recipe_raw=_recipe_raw,
        recipe_plans=_recipe_plans,
    )

    # ── LINEAGE-VIEW-G: the lineage panel of Audit mode (list and map of dots to choose the place of an audit step, D-0629, D-0634) ──
    define_lineage_server(
        input, output, session,
        active_cfg=active_cfg,
        in_audit=_in_audit,
        recipe_plans=_recipe_plans,
        home_state=home_state,
        safe_input=safe_input,
        notification_log=notification_log,
        data_refresh_trigger=data_refresh_trigger,
        lineage_calc=_lineage_calc,
        shown_item=shown_item,
        restored_steps=restored_steps,
        effective_shown_place=_effective_shown_place,
        open_graph=_open_graph,
    )

