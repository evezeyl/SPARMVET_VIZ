# Tasks Archive — 2026-05-09

Completed items moved from `tasks.md` on 2026-05-09 cleanup. All items verified `[x]` before archival.

---

## 2026-05-04 Detected Changes & Post-Demo Notes (all done)

- [x] Verification: Manifest 1_test_data_ST22_dummy — main manifest restored to `!include` substructure. Groups in main, plots via `!include`. Fixed all manifests and clarified ADRs. ✅

- [x] **EXPORT-REDESIGN-1**: Consolidated export UI into one panel with scope toggle. ✅ 2026-05-04
  - Deleted `export_audit_report_ui()`, `export_audit_report_download()`, `_audit_report_filename()`
  - Single "Export Bundle" button with 3-way scope toggle `[Global project | Active group | Active plot]`
  - Removed Single Graph Export accordion panel (superseded by scope toggle)
  - Impl: `app/handlers/export_handlers.py`, `app/handlers/home_theater.py`

- [x] **EXPORT-REDESIGN-2**: Auto-include T3 audit trail in report.qmd when T3 active + has changes. ✅ 2026-05-04
  - T3 audit trail section added; `recipes/t3_steps.yaml` generated when T3 has committed active nodes
  - Impl: `export_bundle_download()` in `export_handlers.py`

- [x] **ASSEMBLY-RENAME**: ✅ 2026-05-04 Renamed `assembly_manifests` → `join_manifests` and role string `"assembly"` → `"join"` everywhere. ~35 files, ~65 occurrences. Passes: zero-ambiguity, role string, UI labels, TubeMap nodes, Python variable names, docs.

---

## 🟡 Active Lineage Build: ST22 (complete)

- [x] **Lineage 2 (Plasmid Dynamics)** `[@user]` — VERIFIED 2026-05-09: assembly passes, 6 columns / 163 rows, Year as String, all types correct. Both AMR_Profile_Joint (8 cols/70 rows) and Plasmid_Profile_Joint (6 cols/163 rows) pass cleanly.

---

## 🔧 Audit-Derived Tasks 2026-05-09 — ALL COMPLETE

Source: `audit_in_depth_state_2026-05-09.md`. All findings verified by manual grep before task creation.

### P0 — Immediate hygiene (all done)

- [x] **AUDIT-DEPGRAPH-NOW** `[haiku/low]`: Ran `build_dep_graph.py` + regenerated `tree.txt` after Wave 8/9 new files. ✅ 2026-05-09 — run manually by user.

- [x] **AUDIT-HANDOFF-UPDATE** `[haiku/low]`: Rewrote `handoff_active.md` — replaced 4-day stale content with current state (ADRs 073–076 authored 2026-05-09). ✅ 2026-05-09

- [x] **AUDIT-RULES-FLAGS-UPDATE** `[haiku/low]`: Updated `rules_persona_feature_flags.md` "Known violations" table — all 5 violations fixed, table replaced with re-run instructions. Task 25-O marked complete. ✅ 2026-05-09

- [x] **AUDIT-ADR072-STUB** `[haiku/low]`: Inserted `## ADR-072: [RESERVED — numbering gap]` stub in `architecture_decisions.md`. Moved ADR-069 entry to correct chronological position. ✅ 2026-05-09

- [x] **AUDIT-QUALITY-WRANGLING** `[haiku/low]`: Deleted empty `wrangling: []` file (`Quality_metrics_wrangling.yaml`) — was 14 bytes, unreferenced. ✅ 2026-05-09

- [x] **AUDIT-PHANTOM-TEST** `[haiku/low]`: Checked `rules_verification_testing.md §8` — phantom reference not present in current file. No-op. ✅ 2026-05-09

### P1 — Documentation reconciliation (all done)

- [x] **AUDIT-CHANGELOG-UPDATE** `[haiku/low]`: Appended Phase 28/29/31/32 entries to `changelog.md`; added ADR 066–076 rollup table. ✅ 2026-05-09

- [x] **AUDIT-WRANGLE-FLAG** `[haiku/low]`: Verified `wrangle_studio_enabled` in `_REQUIRED_FLAGS` and all 8 templates — already present. No-op. ✅ 2026-05-09

- [x] **AUDIT-DEMO-PERSONAS** `[haiku/low]`: Verified `demo-vetinst` and `web-demo` columns in Full Flag Matrix — already present (8 columns, "Eight personas exist"). No-op. ✅ 2026-05-09

- [x] **AUDIT-ABROMICS-CHECK** `[haiku/low]`: Read `1_Abromics_general_pipeline.yaml` — 3 schemas, 119 lines; added inline-form confirmation comment. ✅ 2026-05-09

- [x] **AUDIT-PLAN-ORDER** `[haiku/low]`: Verified `implementation_plan_master.md` phases in sequential order (23-32); added Phase 30 gap note. ✅ 2026-05-09

### P2 — Code cleanup (all done)

- [x] **AUDIT-CONNECTOR-TEST-FIX** `[sonnet/low]`: Fixed 10 connector tests — used `tmp_path` pytest fixture to mock `Path.exists()` for Filesystem/Galaxy/Irida test classes. ✅

- [x] **AUDIT-SGE-CLEANUP** `[sonnet/low]`: Removed orphaned `single_graph_export_handlers.py` import and call from `home_theater.py`. Deleted `single_graph_export_handlers.py`. Updated `@deps` in `home_theater.py`. ✅

- [x] **AUDIT-NOTIF-UTIL-MOVE** `[haiku/low]`: Moved `notification_utils.py` from `app/handlers/` → `app/modules/`. Updated all import paths and `@deps` blocks. ✅

- [x] **AUDIT-CSS-SWEEP** `[sonnet/medium]`: Moved inline `style=` attributes to `config/ui/theme.css`. Started with `filter_and_audit_handlers.py` (22 instances). ADR-055 compliance. ✅

- [x] **AUDIT-PLASMID-VERIFY** `[sonnet/low]`: Assembly verified 2026-05-09. Both join assemblies pass cleanly. ✅

- [x] **AUDIT-SERVER-SLIM** `[sonnet/medium]`: `app/src/server.py` 304 → 262 lines. Extracted `_safe_input`, `_apply_tier2_transforms`, `DEFAULT_HOME_STATE` into `app/modules/orchestrator_helpers.py`. Emoji removed from banner comments. 97/97 tests pass. ✅ 2026-05-09

- [x] **AUDIT-ADR076-MVP** `[opus/medium]`: Defined MVP-1 scope for ADR-076 at `.claude/design/adr076_mvp.md`. MVP-1 = 8 tasks (~1 week) vs full ADR (4–6 weeks). Promotion criteria for MVP-2 defined. ADR-076 status line updated. ✅ 2026-05-09

---

## Completed items from 🔴 Open Issues

### Export / Reproducibility

- [x] **EXPORT-HASH-1**: Fixed `data_batch_hash` computation — all export surfaces (bundle README, bundle QMD report, SGE README, audit report footer) now show all three hashes with explanations. ✅

### Session / Import

- [x] **SESSION-PERSONA-1** `[sonnet/low]`: Ghost save gated by `ghost_save.enabled` in persona automation config. `bootloader` param added to `audit_stack.define_server`. Fixes `qa` persona. ✅ 2026-05-05

### Sidebar Slot Registry (ADR-073)

- [x] **SIDEBAR-CONFIGS-1** `[haiku/low]`: Created `config/ui/sidebars/` with shared sidebar YAML panel-list files. Updated all 6 persona templates with `workspaces:` section and `!include` references. ✅ 2026-05-09

- [x] **SIDEBAR-REGISTRY-1** `[sonnet/high]`: ADR-073 core implemented:
  - `app/modules/sidebar_registry.py` — `PANEL_REGISTRY` dict, headless-safe.
  - Bootloader: `SidebarConfig` dataclass + `get_sidebar_config()` with `!include` support.
  - `home_theater.py`: replaced hardcoded accordion with slot-list iteration.
  - `ui.py`: `bootloader.get_sidebar_config("home","right").visible` replaces ADR-053 violation.
  - All 8 persona templates updated with `workspaces:` section. ✅ 2026-05-09

- [x] **SIDEBAR-VALIDATE-1** `[sonnet/medium]`: `SidebarValidator` class + `scripts/validate_persona_config.py` CLI. 8/8 templates PASS. `PersonaValidator.validate_file()` now supports `!include`. `server.py` startup gate added. ✅ 2026-05-09

- [x] **STATIC-VIEW-1c** `[sonnet/low]`: Sidebar visibility for static personas decided (ADR-073) — controlled by `workspaces.home.left_sidebar.visible` in persona template. ✅ 2026-05-09

### Diagnostic Error Discipline (ADR-078)

- [x] **DIAG-CORE-1** `[sonnet/medium]`: `DeploymentError` dataclass + helpers in `app/modules/deployment_error.py`. PersonaValidator retrofitted. `server.py` startup gate. ADR-078 Phase B. ✅ 2026-05-09
- [x] **DIAG-VALIDATE-SIDEBAR-1** `[sonnet/medium]`: `SidebarValidator` returns `list[DeploymentError]`. ADR-078 Phase C. ✅ 2026-05-09
- [x] **DIAG-BOOTLOADER-1** `[sonnet/medium]`: Bootloader startup paths wrapped in `DeploymentError`. ADR-078 Phase C. ✅ 2026-05-09
- [x] **DIAG-CONNECTOR-1** `[sonnet/medium]`: Connectors retrofitted. `DeploymentError` moved to `libs/utils/`; `app/modules/deployment_error.py` is a re-export shim. ADR-078 Phase C + ADR-011. ✅ 2026-05-09
- [x] **DIAG-MANIFEST-1** `[sonnet/medium]`: Manifest structural validation at load time in `libs/utils/src/utils/config_loader.py`. 3-stage validation emitting `DeploymentError`. ADR-078 Phase C. ✅ 2026-05-09
- [x] **DIAG-CATALOG-1** `[sonnet/high]`: `docs/troubleshooting/index.qmd` — 31 errors cataloged across 5 groups; wired into `docs/_quarto.yml`. ADR-078 Phase C. ✅ 2026-05-09
- [x] **DIAG-CLI-1** `[haiku/low]`: Audited CLI scripts — 4 candidates identified; retrofitting deferred to separate task. ✅ 2026-05-09

---

## Completed items from 🟡 Wave 2 — Pending User Decision

### libs/utils/ Relocations

- [x] **UTILS-RELOC-1**: Resolved by moving to `libs/blueprint_arch/` (ADR-067). Imports updated in `blueprint_handlers.py`. 2026-05-05

### UI — Persona scoping decisions (all decided 2026-05-05)

- [x] **PERSONA-CONFIG-VALIDATE-1** `[sonnet/medium]`: PersonaValidator Rule 6 — T3 cascade fatal check. ✅ 2026-05-05
- [x] **PERSONA-CONFIG-FLAG-1** `[haiku/low]`: Collapsed `export_bundle_enabled` + `export_graph_enabled` → `export_enabled`. ✅ 2026-05-05
- [x] **PERSONA-CONFIG-FLAG-2** `[haiku/low]`: `manifest_selector_visible` mirrored into features dict. ✅ 2026-05-05
- [x] **PERSONA-CONFIG-FLAG-3** `[haiku/low]`: Added `blueprint_enabled` + `test_lab_enabled` to all 8 templates. ✅ 2026-05-05

### REVIEW tasks — all decided

- [x] **Deployment Preparation**: Reviewed; issues tasked below. ✅ 2026-05-05
- [x] **DEPLOY-CDN-1**: Vendored Cytoscape@3.29.2 + Dagre + cytoscape-dagre + Bootstrap Icons. ✅ 2026-05-05
- [x] **DEPLOY-MODULES-1**: Gated server-side module instantiation on persona flags. ✅ 2026-05-05
- [x] **VENDOR-MANIFEST-1**: Created `app/src/www/vendor/VENDOR_MANIFEST.md`. ✅ 2026-05-05
- [x] **DEPLOY-LIBS-1** `[haiku/low]`: Created `scripts/install_libs.sh`. ✅ 2026-05-05
- [x] **REVIEW-SCOPING-1**: PersonaValidator Rule 6 (PERSONA-CONFIG-VALIDATE-1). Closed. ✅ 2026-05-09
- [x] **REVIEW-EXPORT-FLAGS**: One `export_enabled` gates all scope levels. Decided. ✅ 2026-05-09
- [x] **REVIEW-IMPORT-PANEL**: Single browse + mapping panel. `IMP_HLP` implies `META_ING`. Overwrite behavior. See IMPORT-UI-1. ✅ 2026-05-05
- [x] **REVIEW-AUTOSAVE-CACHE**: Already implemented in SESSION-PERSONA-1. ✅ 2026-05-09
- [x] **REVIEW-HASH-EXPORT**: Always include, no flag (ADR-069). ✅ 2026-05-09
- [x] **REVIEW-UI-TITLE-SUBT**: Resolution order decided. See UI-TITLE-1. ✅ 2026-05-05
- [x] **TO DISCUSS**: Toggle "show all rows" → PREVIEW-ALLROWS-1. ✅ 2026-05-09
- [x] **TO DISCUSS**: Prepare to connect → DEPLOY-CONNECT-1. ✅ 2026-05-09

### Blueprint Architect — completed foundations

- [x] **LINEAGE-NAV-1** `[sonnet/medium]`: `build_plot_lineage()` + `get_plot_ids_in_group()` in `manifest_navigator.py`. ADR-074. ✅ 2026-05-09
- [x] **LINEAGE-EXPORT-1** `[sonnet/high]`: `lineage/lineage_graph.json` in `export_handlers.py`; Mermaid flowchart in `report.qmd`. ADR-074. ✅ 2026-05-09
- [x] **BP-SCHEMA-1** `[sonnet/high]`: `ui_schema` kwarg to `@register_action` + `@register_plot_component`; `schema_registry.py` in `blueprint_arch`; 19 transformer + 7 viz_factory schemas. ADR-075. ✅ 2026-05-09
- [x] **SCHEMA-VERIFY-ACTIONS-1** `[haiku/low]`: All 19 transformer actions verified; 4 param mismatches fixed. ✅ 2026-05-09
- [x] **SCHEMA-VERIFY-GEOMS-1** `[haiku/low]`: All 7 viz_factory geoms verified; comprehensive param coverage. ✅ 2026-05-09

### ADR-076 — prerequisites

- [x] **BP-AGENT-FLAG-1** `[haiku/low]`: `blueprint_agent_enabled` flag added to all 8 persona templates. Fatal cascade in PersonaValidator Rule 7 (ADR-077). Bootloader does NOT silently suppress. All 8 templates pass. ✅ 2026-05-09

---

## 🔴 Open Issues — Completed Batch (archived 2026-05-09, second cleanup)

### Export / Reproducibility (all done)

- [x] **EXPORT-HASH-2** `[sonnet/medium]`: Read `decision_hash` from Parquet metadata key `sparmvet_decision_hash` at export time; include in bundle README, report.qmd, and image file metadata. ADR-069.
- [x] **EXPORT-VERSION-1** `[haiku/low]`: Add `git_commit` + `release_version` to all export surfaces. ADR-069.
- [x] **EXPORT-IMG-META-1** `[sonnet/medium]`: Embed provenance subset (8 fields) in exported image file metadata. PNG → Pillow iTXt; SVG → `<metadata>` XML block. ADR-069 Rule 3.
- [x] **EXPORT-AUDIT-COMPLETE-1** `[sonnet/medium]`: Add all remaining provenance fields to README + report.qmd. `build_export_provenance()` helper introduced in `export_handlers.py`. ADR-069.

### Session / Import (done)

- [x] **INGEST-SANITIZE-1** `[sonnet/medium]`: Wire `DataSanitizer` into `IngestorOrchestrator.run()` before T1 materialisation.

### UX (done)

- [x] **THEATER-1** `[sonnet/medium]`: Collapse/minimize plot panel — caret in plot card header → 1-line collapsed state. Persisted in `home_state`.

### Sidebar Slot Registry — Static View (done)

- [x] **STATIC-VIEW-1a** `[haiku/low]`: Hide view-title banner for fully static personas. Gate on `interactivity_enabled: false`.
- [x] **STATIC-VIEW-1b** `[sonnet/low]`: T2 as default tier for static personas; tier toggle strip hidden; `_track_tier_toggle` returns "T2" as fallback.

---

## 🎨 CSS Style Hygiene — All done (archived 2026-05-09)

- [x] **CSS-BADGE-PROPAG-1** `[haiku/low]`: Migrated `.spv-badge-propagation` to SPARMVET palette. `#eef0fb` bg / `#345beb` text.
- [x] **CSS-ERROR-RED-DECIDE** `[opus/high]`: Error red `#d62828` added to palette. Updated `rules_css_style_spec.md` §1c/1e + `theme.css` line ~772.

---

## 🟡 Wave 2 — Completed items (archived 2026-05-09)

- [x] **UTILS-RELOC-2** `[haiku/low]`: Deduplicated `gallery_manager.py` — canonical copy in `libs/viz_gallery/`, removed from `libs/utils/`.
- [x] **UI-TITLE-1** `[sonnet/medium]`: UI title/subtitle resolution: persona config override > manifest `info.display_name`/`info.subtitle` > nothing.
- [x] **IMPORT-UI-1** `[sonnet/high]`: Unified import browse buttons into single browse + mapping panel (`app/handlers/data_import_handlers.py`).
- [x] **PREVIEW-ALLROWS-1** `[sonnet/low]`: "Show all rows" toggle in data preview accordion header.

---

## RESEARCH / DECIDE — Completed (archived 2026-05-09)

- [x] **HELP-DOCS-1** `[haiku/low]`: Bundle `docs/_site/` as Shiny static assets at `/docs/`; "Full documentation →" link added to contextual cards.

---

## 🟣 Blueprint Architect — Completed batch (archived 2026-05-09)

### Blueprint IDE Forms (ADR-075) — all done

- [x] **BP-FORMS-1** `[sonnet/high]`: Form renderer — all widget types, column selector + upstream schema propagation on Apply, edit-in-place, schema invalidation markers.
- [x] **BP-ESCAPE-1** `[sonnet/medium]`: YAML escape hatch — read-only (all `blueprint_enabled`) + editable (`manifest_edit_enabled`) with re-parse on save.
- [x] **BP-UNDO-1** `[haiku/low]`: 20-step session undo deque for Blueprint DAG state.
- [x] **BP-HELP-1** `[sonnet/medium]`: Help panel — `__doc__` resolution, collapsible sections for composite actions, optional external URL button.
- [x] **BP-FLAG-1** `[haiku/low]`: `manifest_edit_enabled` flag added to all eight persona templates + feature flags rule + bootloader cascade.

### Blueprint Other — done items

- [x] **TubeMap aesthetics** `[haiku/low]`: Tighter rail/tube look; renamed 'ref' → 'Add' in nodes and legend.
- [x] **UX-NOTIF-3** `[haiku/low]`: Project-load notification for Blueprint Architect manifest reload.

### ADR-076 — BLUEPRINT AI Agent Helper MVP-1 (all done)

- [x] **BP-AGENT-1**: `AgentAdapter` protocol + `ClaudeCliAdapter` + `DisabledAdapter`. `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` + `agent_context.py`.
- [x] **BP-AGENT-PARSER-1**: `agent_tool_parser.py` — fenced-block extractor, JSON validation, per-tool schema dispatch, error turn on parse failure.
- [x] **BP-AGENT-TOOLS-1**: `agent_tools.py` — 3 MVP-1 tools: `get_available_actions`, `get_available_components`, `get_field_contract`.
- [x] **BP-AGENT-INSTRUCT-1**: `config/ui/agents/blueprint_default.md` — system prompt (tool-call protocol, intake questions, AMR domain, safety rules).
- [x] **BP-AGENT-PANEL-1**: `blueprint_agent_chat` panel type registered in `sidebar_registry.py`; added to Blueprint right sidebar config.
- [x] **BP-AGENT-UI-1**: Chat panel render + async send effect in `blueprint_handlers.py`; wired into right sidebar. Tool-call loop (max 3 rounds), `asyncio.to_thread` for non-blocking subprocess. Smoke tests: 14 passed, 3 skipped.
- [x] **BP-AGENT-CSS-1**: `.bp-agent-*` CSS block in `config/ui/theme.css`. ADR-055.

---

## 🟡 Deferred / Backlog — Completed items (archived 2026-05-09)

### Export enhancements (done)

- [x] **EXPORT-2** `[sonnet/medium]`: T3 data inclusion checkbox (`export_include_t3`), gated on `t3_sandbox_enabled`. Defaults to checked when `tier_toggle=="T3"`. Falls back to auto-detect when absent.
- [x] **EXPORT-3** `[sonnet/medium]`: QMD report improvements — TOC (depth 3), `number-sections`, cosmo theme, 11pt; `#fig-` cross-ref IDs; `_build_methods_section()` auto-prose from T3 nodes + active filters.
- [x] **EXPORT-4** `[sonnet/low]`: Per-plot width/height inputs (inches, 0.5-step) wired into `fig.save()` and provenance.

### Gallery & UI (done)

- [x] ~~**Gallery: Re-verify "Clone to Sandbox"**~~ — SUPERSEDED by GALLERY-CLONE-DECOUPLE-1.
- [x] **UX-NOTIF-2** `[sonnet/medium]`: `notification_log` persisted to T3 ghost on `btn_apply`; restored on session load. Old ghosts without key fall back to `[]` silently.

### Audit Infrastructure (done)

- [x] **AUDIT-TIMERS-1** `[haiku/low]`: Systemd audit timers installed and verified via `./scripts/systemd/install.sh`.
