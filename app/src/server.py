# @deps
# provides: server (Shiny server function)
# consumes: shiny, polars, pathlib, app.src.bootloader, app.modules.orchestrator, app.modules.orchestrator_helpers, app.modules.session_manager, utils.config_loader, viz_factory.viz_factory, app.modules.wrangle_studio, app.modules.test_lab_studio, app.modules.gallery_viewer, app.modules.persona_validator, app.modules.sidebar_validator, app.modules.deployment_error, app.handlers.home_theater, app.handlers.audit_stack, app.handlers.blueprint_handlers, app.handlers.gallery_handlers, app.handlers.ingestion_handlers
# consumed_by: app.src.main
# doc: ADR-045, ADR-003
# @end_deps
# app/src/server.py — Thin Orchestrator (ADR-045, Phase 22)
# ≤ 150 lines: shared state, shared calcs, shared utils, five define_server() delegations.
# No business logic. No @render.* or @reactive.* here.
from shiny import reactive, ui
import polars as pl
from pathlib import Path

# Authority: Library Sovereignty (ADR-003)
from app.src.bootloader import bootloader
from app.modules.orchestrator import DataOrchestrator
from app.modules.session_manager import SessionManager
from utils.config_loader import ConfigManager
from viz_factory.viz_factory import VizFactory
from app.modules.wrangle_studio import WrangleStudio
from app.modules.test_lab_studio import TestLabStudio
from app.modules.gallery_viewer import gallery_viewer
from app.modules.persona_validator import PersonaValidator
from app.modules.sidebar_validator import SidebarValidator
from app.modules.deployment_error import DeploymentError, exit_if_errors
from app.modules.orchestrator_helpers import (
    safe_input as _safe_input,
    apply_tier2_transforms as _apply_tier2_transforms,
    DEFAULT_HOME_STATE,
)

# Inject action + component catalogs into blueprint_arch schema_registry (ADR-011).
# server.py is Tier 3 (orchestration) — the only layer allowed to import from multiple libs.
try:
    from transformer.actions.base import ACTION_SCHEMAS as _ACTION_SCHEMAS
    from viz_factory.registry import COMPONENT_SCHEMAS as _COMPONENT_SCHEMAS
    from blueprint_arch.schema_registry import register as _register_schema_catalogs
    _register_schema_catalogs(_ACTION_SCHEMAS, _COMPONENT_SCHEMAS)
except ImportError:
    pass



def server(input, output, session):

    # Startup validation gate (ADR-077, ADR-078). Both validators run; if either
    # produces errors, the formatted block goes to stderr and the process exits
    # with a non-zero code. The operator sees a single readable summary instead
    # of a stack trace.
    _all_errors: list[DeploymentError] = []
    _all_errors.extend(PersonaValidator().validate_file(str(bootloader.persona_path)))

    _all_errors.extend(SidebarValidator().validate_file(str(bootloader.persona_path)))

    exit_if_errors(_all_errors, header="SPARMVET startup blocked — persona configuration is invalid")

    @reactive.Calc
    def active_collection_id():
        """Agnostic Discovery: fetches the first collection in the manifest."""
        cfg = active_cfg()
        collections = list(cfg.raw_config.get("join_manifests", {}).keys())
        if not collections:
            return "Untitled_Collection"
        return collections[0]

    # 1. Reactive Manifest Authority (Universal Architecture)
    @reactive.Calc
    def active_cfg():
        # Use fixed_manifest when manifest selector is hidden (pipeline personas);
        # fall back to the project_id widget only when the selector is visible.
        project_id = _safe_input(input, "project_id", bootloader.get_default_project())
        cached = bootloader.get_cached_asset(
            project_id, "manifest", "raw", "cfg")
        if cached is not None:
            return cached

        path = bootloader.get_location("manifests") / f"{project_id}.yaml"
        cfg = ConfigManager(str(path))
        bootloader.set_cached_asset(project_id, "manifest", "raw", "cfg", cfg)
        return cfg

    orchestrator = DataOrchestrator(
        manifests_dir=bootloader.get_location("manifests"),
        raw_data_dir=bootloader.get_location("raw_data"),
        prefer_discovery=bootloader.connector_config.get("prefer_discovery", False),
    )
    # BP-COLOR-3: inject project palettes from deployment registry.
    # VizFactory works with built-ins alone when no registry is passed (library independence).
    viz_factory = VizFactory(palette_registry=bootloader.get_palettes())

    # Module Initialization (Phase 11-F / ADR-039)
    wrangle_studio = WrangleStudio(session.id)
    dev_studio = TestLabStudio() if bootloader.is_enabled("test_lab_enabled") else None

    # State Management
    anchor_path = reactive.Value(None)
    recipe_pending = reactive.Value(False)
    snapshot_recipe = reactive.Value([])
    gallery_refresh_trigger = reactive.Value(0)
    data_refresh_trigger = reactive.Value(0)   # incremented after data import to bust plot cache
    notification_log = reactive.Value([])      # UX-NOTIF-1: persistent alert log (last 20)

    # §13 Home Module State Object — see orchestrator_helpers.DEFAULT_HOME_STATE for schema
    home_state = reactive.Value(dict(DEFAULT_HOME_STATE))

    # Convenience shims — kept so existing home_theater.py code continues to work
    # while Phase 22-B wires everything through home_state.
    active_home_subtab = reactive.Value("")
    tier_toggle = reactive.Value("T1")

    # Session manager — Location 4 from connector
    session_manager = SessionManager(bootloader.get_location("user_sessions"))

    # Per-session Blueprint Architect state (declared here so wrangle_studio.define_server
    # can reference them via lambda before blueprint_handlers registers them)
    _includes_map: reactive.Value = reactive.Value({})      # rel_path → abs_path for !include files
    _component_ctx_map: reactive.Value = reactive.Value({}) # rel_path → {role, schema_id, ...}
    _schema_registry: reactive.Value = reactive.Value({})   # schema_id → structural entry

    print(f"DEBUG: Initializing Server with Persona: {bootloader.persona_display_name}")
    current_persona = reactive.Value(bootloader.persona_display_name)

    # Dependency Resolution: Data Tiers
    @reactive.Calc
    def tier1_anchor():
        """Scans the physical Parquet anchor (Predicate Pushdown ready)."""
        project_id = _safe_input(input, "project_id", "default")
        coll_id = active_collection_id()
        cached_lf = bootloader.get_cached_asset(
            project_id, coll_id, "anchor", "lf")
        if cached_lf is not None:
            return cached_lf
        path = anchor_path.get()
        if not path:
            return pl.DataFrame().lazy()
        lf = pl.scan_parquet(path)
        bootloader.set_cached_asset(project_id, coll_id, "anchor", "lf", lf)
        return lf

    @reactive.Calc
    def tier_reference():
        """Tier 2: T1 baseline + T2 transforms if tier_toggle is T2 or above."""
        lf = tier1_anchor()
        if tier_toggle.get() in ("T2", "T3"):
            lf = _apply_tier2_transforms(lf, active_cfg())
        return lf

    @reactive.Calc
    @reactive.event(input.btn_apply)
    def tier3_leaf():
        lf = tier1_anchor()
        cfg = active_cfg()
        recipe = snapshot_recipe.get()
        show_long = tier_toggle.get() == "T3"

        # Stage 1: Pre-transform filters
        pre_steps = [s for s in recipe if s.get("stage") == "pre_transform"]
        for step in pre_steps:
            action, col, val = step.get("action", ""), step.get(
                "column"), step.get("value")
            if action == "filter_eq" and col and val is not None:
                try:
                    lf = lf.filter(pl.col(col) == val)
                except Exception:
                    pass

        # Global Sidebar Filters
        for col in lf.collect_schema().names()[:10]:
            clean_col = col.replace(" ", "_").replace("(", "").replace(")", "")
            try:
                val = getattr(input, f"filter_{clean_col}")()
                if val and val != "All":
                    lf = lf.filter(pl.col(col) == val)
            except Exception:
                pass

        if show_long:
            lf = _apply_tier2_transforms(lf, cfg)

        result = lf.collect()
        if result.height == 0:
            ui.notification_show(
                "⚠️ No data. Adjust filters.", type="warning", duration=10)
        recipe_pending.set(False)
        return result


    # Module Server Definitions
    wrangle_studio.define_server(
        input, output, session, lambda: tier1_anchor().collect_schema().names(), tier1_anchor, viz_factory,
        get_schema_registry=lambda: _schema_registry.get(),
        get_includes_map=lambda: _includes_map.get(),
        bootloader=bootloader,
    )
    if bootloader.is_enabled("test_lab_enabled"):
        dev_studio.define_server(input, output, session)

    # ── Handler Delegations (ADR-045 — Two-Category Law) ──────────────────────

    # Home Theater: dynamic_tabs, sidebar_nav_ui, sidebar_tools_ui, right_sidebar, plots/tables
    from app.handlers.home_theater import define_server as _define_home_theater_server
    _define_home_theater_server(
        input, output, session,
        bootloader=bootloader,
        wrangle_studio=wrangle_studio,
        dev_studio=dev_studio,
        orchestrator=orchestrator,
        viz_factory=viz_factory,
        gallery_viewer=gallery_viewer,
        current_persona=current_persona,
        anchor_path=anchor_path,
        tier1_anchor=tier1_anchor,
        tier_reference=tier_reference,
        tier3_leaf=tier3_leaf,
        active_cfg=active_cfg,
        active_collection_id=active_collection_id,
        safe_input=_safe_input,
        active_home_subtab=active_home_subtab,
        tier_toggle=tier_toggle,
        home_state=home_state,
        session_manager=session_manager,
        data_refresh_trigger=data_refresh_trigger,
        notification_log=notification_log,
    )

    # Pipeline Audit: T2/T3 nodes, btn_apply, recipe_pending_badge (requires t3_sandbox_enabled)
    if bootloader.is_enabled("t3_sandbox_enabled"):
        from app.handlers.audit_stack import define_server as _define_audit_server
        _define_audit_server(
            input, output, session,
            wrangle_studio=wrangle_studio,
            recipe_pending=recipe_pending,
            snapshot_recipe=snapshot_recipe,
            active_cfg=active_cfg,
            active_collection_id=active_collection_id,
            home_state=home_state,
            session_manager=session_manager,
            notification_log=notification_log,
            bootloader=bootloader,
        )

    # Blueprint Architect: manifest import, TubeMap, Lineage Rail, upload/save/download
    if bootloader.is_enabled("blueprint_enabled"):
        from app.handlers.blueprint_handlers import define_server as _define_blueprint_server
        _define_blueprint_server(
            input, output, session,
            bootloader=bootloader,
            wrangle_studio=wrangle_studio,
            orchestrator=orchestrator,
            safe_input=_safe_input,
            includes_map=_includes_map,
            component_ctx_map=_component_ctx_map,
            schema_registry=_schema_registry,
        )

    # Gallery: filtering, preview, clone
    if bootloader.is_enabled("gallery_enabled"):
        from app.handlers.gallery_handlers import define_server as _define_gallery_server
        _define_gallery_server(
            input, output, session,
            bootloader=bootloader,
            wrangle_studio=wrangle_studio,
            safe_input=_safe_input,
            current_persona=current_persona,
            home_state=home_state,
        )

    # Ingestion & persona switching
    from app.handlers.ingestion_handlers import define_server as _define_ingestion_server
    _define_ingestion_server(
        input, output, session,
        bootloader=bootloader,
        current_persona=current_persona,
        safe_input=_safe_input,
    )
