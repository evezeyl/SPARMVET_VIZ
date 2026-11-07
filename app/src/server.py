# @deps
# provides: server (Shiny server function)
# consumes: shiny, polars, pathlib, app.src.bootloader, app.modules.orchestrator, app.modules.orchestrator_helpers, app.modules.session_manager, utils.config_loader, viz_factory.viz_factory, app.modules.wrangle_studio (gated: developer_mode_enabled), app.modules.test_lab_studio (gated: test_lab_enabled), app.modules.gallery_viewer, app.modules.app_features_validator, app.modules.sidebar_validator, app.modules.deployment_error, app.handlers.home_theater, app.handlers.audit_stack, app.handlers.blueprint_handlers, app.handlers.gallery_handlers, app.handlers.ingestion_handlers
# provides: reactive.Value:_selected_lineage_rel (shared between wrangle_studio and blueprint_handlers — BP-LINEAGE-NAV-1)
# consumed_by: app.src.main
# doc: ADR-045, ADR-003
# @end_deps
# app/src/server.py — Thin Orchestrator (ADR-045, Phase 22)
# ~250 lines at most (rules_app_structure.md section 3): shared state, shared calcs, shared utils,
# five define_server() delegations.
# No business logic. No @render.* or @reactive.* here.
from shiny import reactive
import polars as pl

# Authority: Library Sovereignty (ADR-003)
from app.src.bootloader import bootloader
from app.modules.orchestrator import DataOrchestrator
from app.modules.session_manager import SessionManager
from app.modules.cache_keys import load_data_analysis_recipe
from viz_factory.viz_factory import VizFactory
from app.modules.wrangle_studio import WrangleStudio
from app.modules.test_lab_studio import TestLabStudio
from app.modules.gallery_viewer import gallery_viewer
from app.modules.app_features_validator import AppFeaturesValidator
from app.modules.sidebar_validator import SidebarValidator
from app.modules.deployment_error import DeploymentError, exit_if_errors
from app.modules.orchestrator_helpers import (
    safe_input as _safe_input,
    DEFAULT_HOME_STATE,
)

# Flags that need the WrangleStudio state object (see server()).
_WRANGLE_STUDIO_FLAGS = ("developer_mode_enabled", "blueprint_enabled", "t3_sandbox_enabled")

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
    _all_errors.extend(AppFeaturesValidator().validate_file(str(bootloader.app_features_path)))

    _all_errors.extend(SidebarValidator().validate_file(str(bootloader.app_features_path)))

    exit_if_errors(_all_errors, header="SPARMVET startup blocked — app features configuration is invalid")

    @reactive.Calc
    def active_collection_id():
        """Agnostic Discovery: fetches the first collection in the data analysis recipe."""
        cfg = active_cfg()
        collections = list(cfg.raw_config.get("joins", {}).keys())
        if not collections:
            return "Untitled_Collection"
        return collections[0]

    # 1. Reactive Data Analysis Recipe Authority (Universal Architecture)
    @reactive.Calc
    def active_cfg():
        # When the selector is hidden the deployment (or SPARMVET_DATA_ANALYSIS_RECIPE) names the data analysis recipe;
        # fall back to the data_analysis_recipe_id widget only when the selector is visible.
        data_analysis_recipe_id = _safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe())
        # ADR-089: the parsed data analysis recipe stays in memory only while none of its files changed on
        # disk (size and modification time are checked each time a session evaluates this).
        path = bootloader.get_location("data_analysis_recipes") / f"{data_analysis_recipe_id}.yaml"
        return load_data_analysis_recipe(path).config

    orchestrator = DataOrchestrator(
        data_analysis_recipes_dir=bootloader.get_location("data_analysis_recipes"),
        raw_data_dir=bootloader.get_location("raw_data"),
        data_lookup=bootloader.data_lookup,
    )
    # BP-COLOR-3: inject deployment palettes from deployment registry.
    # VizFactory works with built-ins alone when no registry is passed (library independence).
    viz_factory = VizFactory(palette_registry=bootloader.get_palettes())

    # Module Initialization (Phase 11-F / ADR-039 / ADR-071 positive inclusion)
    # WrangleStudio holds the Blueprint Architect state (logic stack, active component) that the
    # BLUEPRINT handlers and the Pipeline Audit panel read. It is created when any of them is on:
    # developer_mode_enabled, blueprint_enabled or t3_sandbox_enabled. (Until 2026-11-07 only
    # developer_mode_enabled created it, so every app features with the audit panel but without
    # developer mode, standalone and pipeline-exploration-advanced, ended on a blank page.)
    wrangle_studio = (WrangleStudio(session.id)
                      if any(bootloader.is_enabled(f) for f in _WRANGLE_STUDIO_FLAGS) else None)
    dev_studio = TestLabStudio() if bootloader.is_enabled("test_lab_enabled") else None

    # State Management
    anchor_path = reactive.Value(None)
    audit_pending = reactive.Value(False)
    snapshot_steps = reactive.Value([])
    gallery_refresh_trigger = reactive.Value(0)
    data_refresh_trigger = reactive.Value(0)   # incremented after data import to bust plot cache
    notification_log = reactive.Value([])      # UX-NOTIF-1: persistent alert log (last 20)
    session_pipeline_errors = reactive.Value([])  # DIAG-RUNTIME-AUDIT-1: structured PipelineError log

    # §13 Home Module State Object — see orchestrator_helpers.DEFAULT_HOME_STATE for schema
    home_state = reactive.Value(dict(DEFAULT_HOME_STATE))

    # Convenience shims — kept so existing home_theater.py code continues to work
    # while Phase 22-B wires everything through home_state.
    active_home_subtab = reactive.Value("")
    tier_toggle = reactive.Value("T1")

    # Session manager — Location 4 from connector
    session_manager = SessionManager(bootloader.get_location("user_data"))

    # Per-session Blueprint Architect state (declared here so wrangle_studio.define_server
    # can reference them via lambda before blueprint_handlers registers them)
    _includes_map: reactive.Value = reactive.Value({})      # rel_path → abs_path for !include files
    _component_ctx_map: reactive.Value = reactive.Value({}) # rel_path → {role, schema_id, ...}
    _schema_registry: reactive.Value = reactive.Value({})   # schema_id → structural entry
    # BP-LINEAGE-NAV-1: shared signal — both lineage rail clicks and btn_import_data_analysis_recipe write
    # here; a single @reactive.Effect in blueprint_handlers calls _do_load_component() directly,
    # eliminating the js_eval → DOM click → input race condition.
    _selected_lineage_rel: reactive.Value = reactive.Value(None)

    print(f"DEBUG: Initializing Server with App features: {bootloader.app_features_display_name}")
    current_app_features = reactive.Value(bootloader.app_features_display_name)

    # Dependency Resolution: Data Tiers
    @reactive.Calc
    def tier1_anchor():
        """Scans the physical Parquet anchor (Predicate Pushdown ready)."""
        data_analysis_recipe_id = _safe_input(input, "data_analysis_recipe_id", "default")
        coll_id = active_collection_id()
        cached_lf = bootloader.get_cached_asset(
            data_analysis_recipe_id, coll_id, "anchor", "lf")
        if cached_lf is not None:
            return cached_lf
        path = anchor_path.get()
        if not path:
            return pl.DataFrame().lazy()
        lf = pl.scan_parquet(path)
        bootloader.set_cached_asset(data_analysis_recipe_id, coll_id, "anchor", "lf", lf)
        return lf


    # Module Server Definitions
    if wrangle_studio is not None and any(bootloader.is_enabled(f) for f in ("developer_mode_enabled", "blueprint_enabled")):
        wrangle_studio.define_server(
            input, output, session, lambda: tier1_anchor().collect_schema().names(), tier1_anchor, viz_factory,
            get_schema_registry=lambda: _schema_registry.get(),
            get_includes_map=lambda: _includes_map.get(),
            bootloader=bootloader,
            selected_lineage_rel=_selected_lineage_rel,
        )
    if bootloader.is_enabled("test_lab_enabled"):
        from app.handlers.test_lab_handlers import define_server as _define_testlab_server
        _define_testlab_server(input, output, session, dev_studio=dev_studio, bootloader=bootloader)

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
        current_app_features=current_app_features,
        anchor_path=anchor_path,
        tier1_anchor=tier1_anchor,
        active_cfg=active_cfg,
        active_collection_id=active_collection_id,
        safe_input=_safe_input,
        active_home_subtab=active_home_subtab,
        tier_toggle=tier_toggle,
        home_state=home_state,
        session_manager=session_manager,
        data_refresh_trigger=data_refresh_trigger,
        notification_log=notification_log,
        session_pipeline_errors=session_pipeline_errors,
    )

    # Pipeline Audit: T2/T3 nodes, btn_apply, audit_pending_badge (requires t3_sandbox_enabled)
    if bootloader.is_enabled("t3_sandbox_enabled"):
        from app.handlers.audit_stack import define_server as _define_audit_server
        _define_audit_server(
            input, output, session,
            wrangle_studio=wrangle_studio,
            audit_pending=audit_pending,
            snapshot_steps=snapshot_steps,
            active_cfg=active_cfg,
            active_collection_id=active_collection_id,
            home_state=home_state,
            session_manager=session_manager,
            notification_log=notification_log,
            bootloader=bootloader,
            session_pipeline_errors=session_pipeline_errors,
        )

    # Blueprint Architect: data analysis recipe import, TubeMap, Lineage Rail, upload/save/download
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
            selected_lineage_rel=_selected_lineage_rel,
            active_cfg=active_cfg,
        )

    # Gallery: filtering, preview, clone → T3 transplant (GALLERY-CLONE-DECOUPLE-1)
    if bootloader.is_enabled("gallery_enabled"):
        from app.handlers.gallery_handlers import define_server as _define_gallery_server
        _define_gallery_server(
            input, output, session,
            bootloader=bootloader,
            safe_input=_safe_input,
            current_app_features=current_app_features,
            home_state=home_state,
        )

    # Ingestion & app features switching
    from app.handlers.ingestion_handlers import define_server as _define_ingestion_server
    _define_ingestion_server(
        input, output, session,
        bootloader=bootloader,
        current_app_features=current_app_features,
        safe_input=_safe_input,
    )
