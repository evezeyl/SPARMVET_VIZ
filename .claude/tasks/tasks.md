# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-09 (tasks.md cleanup — all completed P0/P1/P2 audit tasks + completed foundation tasks archived to `tasks_archive_2026-05-09.md`) by @dasharch

---

## 2026-05-04 Detected Changes & ST22 Lineage Build

> Status: COMPLETED. Detailed history moved to: [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md)

---

## 🔧 Audit-Derived Tasks 2026-05-09

> Status: ALL COMPLETED. Detailed history moved to: [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md)

---

## 🔴 Open Issues

### Export / Reproducibility

- [x] **EXPORT-HASH-2** `[sonnet/medium]`: Read `decision_hash` from Parquet metadata key `sparmvet_decision_hash` at export time; include in bundle README, report.qmd, and image file metadata. Use `get_parquet_metadata_hash(path)` per materialized T1/T2 Parquet. Paths via `bootloader.get_location("anchors")` + naming convention. ADR-069 audit trail.

- [x] **EXPORT-VERSION-1** `[haiku/low]`: Add `git_commit` (`git rev-parse --short HEAD`) and `release_version` (`git describe --tags --always`) to all export surfaces: bundle README, report.qmd header, and image file metadata. ADR-069.

- [x] **EXPORT-IMG-META-1** `[sonnet/medium]`: Embed provenance subset (8 fields: `data_batch_hash`, `manifest_sha256`, `decision_hash`, `git_commit`, `release_version`, `created_at`, `plot_id`, `persona_id`) in exported image file metadata. PNG → Pillow `PngInfo` iTXt chunks (`sparmvet:` prefix). SVG → `<metadata>` XML block. ADR-069 Rule 3.

- [x] **EXPORT-AUDIT-COMPLETE-1** `[sonnet/medium]`: Add all remaining missing provenance fields to bundle README and report.qmd: `created_at`, `manifest_name`/path, `persona_id`, `active_tier`, `software_versions`, `data_source_paths`. Introduce `build_export_provenance()` helper in `export_handlers.py`. ADR-069.

### Session / Import

- [ ] **INGEST-SANITIZE-1** `[sonnet/medium]`: Wire `DataSanitizer` into `IngestorOrchestrator.run()` before T1 materialisation. Sanitizer class exists in `libs/ingestion/` but not called from main pipeline. See audit §1A (`audit_final_exhaustive_2026-05-03.md`).

### UX

- [ ] **THEATER-1** `[sonnet/medium]`: Collapse/minimize plot panel — caret in plot card header → 1-line collapsed state. Per-plot, persisted in `home_state`.

### Sidebar Slot Registry (ADR-073) — partial open

> Completed: SIDEBAR-CONFIGS-1, SIDEBAR-REGISTRY-1, SIDEBAR-VALIDATE-1, STATIC-VIEW-1c. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

- [x] **STATIC-VIEW-1a** `[haiku/low]`: Hide the view-title banner in fully static personas. Gate on `interactivity_enabled: false`.

- [x] **STATIC-VIEW-1b** `[sonnet/low]`: T2 as default displayed tier for static personas — tier toggle strip hidden when `interactivity_enabled: false`; `_track_tier_toggle` fallback returns "T2" when input is absent.

### Diagnostic Error Discipline (ADR-078)

> Completed: DIAG-CORE-1, DIAG-VALIDATE-SIDEBAR-1, DIAG-BOOTLOADER-1, DIAG-CONNECTOR-1, DIAG-MANIFEST-1, DIAG-CATALOG-1, DIAG-CLI-1. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

### Runtime Error Discipline (ADR-079, placeholder)

**Why separate from ADR-078:** runtime errors have a different audience (analyst, not operator), different fix surface (data/manifest, not config), and different render path (Shiny notification / plot overlay, not stderr).

- [ ] **DIAG-RUNTIME-ADR** `[opus/high]`: Author ADR-079. Open questions: separate class vs extend `DeploymentError`; render path per category; how user discovers what caused the failure; whether errors are captured in export audit trail. **Trigger:** when Phase C largely complete OR first runtime-error pain point becomes blocking.
- [ ] **DIAG-RUNTIME-INGESTION-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/ingestion/src/ingestion/ingestor.py` — file-not-found, encoding errors, schema mismatches, sanitization rejections.
- [ ] **DIAG-RUNTIME-ASSEMBLER-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/transformer/src/transformer/data_assembler.py` — `ColumnNotFoundError`, `SchemaError` on join, dtype mismatches, empty result frames, Cartesian-product blowups.
- [ ] **DIAG-RUNTIME-WRANGLER-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/transformer/src/transformer/data_wrangler.py` — action-name not registered, action arg validation against `ui_schema`.
- [ ] **DIAG-RUNTIME-VIZFACTORY-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/viz_factory/src/viz_factory/viz_factory.py` — component not registered, missing required aesthetic, plotnine render exceptions.
- [ ] **DIAG-RUNTIME-T3APPLY-1** `[deferred until DIAG-RUNTIME-ADR]`: T3 Apply path failures in `app/handlers/audit_stack.py`.
- [ ] **DIAG-RUNTIME-BLUEPRINT-1** `[deferred until DIAG-RUNTIME-ADR]`: Manifest fragment validation failures during BLUEPRINT IDE editing.

---

## 🟡 Wave 2 — Pending / Open

### libs/utils/ Relocations

- [ ] **UTILS-RELOC-2** `[haiku/low]`: `gallery_manager.py` exists in both `libs/utils/src/utils/` and `libs/viz_gallery/src/viz_gallery/` — deduplicate. Decide canonical copy; delete the other and fix all imports.

### app/modules/ Two-Category Law Refactor (ADR-045)

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law. Decision needed: scope and migration plan before touching live handlers. See audit §4A. [Not sure if wrong - because its part of the app itslef]

### UI — Implementation tasks from persona scoping decisions

> Completed decisions: see [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

- [ ] **UI-TITLE-1** `[sonnet/medium]`: Implement UI title/subtitle resolution: persona config override > manifest `info.display_name`/`info.subtitle` > nothing. `UI_TITLE` off hides both. Add `info.subtitle` field to manifest schema.

- [x] **IMPORT-UI-1** `[sonnet/high]`: Unify the two import browse buttons into a single browse + mapping panel. `IMP_HLP` on → all manifest data sources. `META_ING` on alone → metadata schema only. Import behavior: overwrite. Implemented in `app/handlers/data_import_handlers.py`.

### Deployment

- [ ] **DEPLOY-CONNECT-1** `[sonnet/medium]`: Posit Connect deployment — editable library install handling.
  - [ ] Add each editable lib as relative path entry in `requirements.txt`: `-e ./libs/ingestion`, `-e ./libs/transformer`, etc.
  - [ ] Document `app/src/main.py` as entry point for `rsconnect-python` bundle.
  - [ ] Deployment profile via `SPARMVET_PROFILE` env var; add `config/deployment/connect/connect_profile.yaml` template.
  - [ ] Smoke test: clean venv from scratch, run `scripts/install_libs.sh`, verify no import errors.
  - Pre-existing done: CDN vendoring, nav gating, vendor manifest, install script, no secrets in source.

### UI Functionality Debugging (user-facing)

- [ ] Exports → retest / debug
- [ ] Proper definition of the session ghost save and save function when Tier 3 activated
- [ ] Import and mapping of the files to the manifest
- [x] **PREVIEW-ALLROWS-1** `[sonnet/low]`: Add "Show all rows" toggle to data preview. Off by default (100-row cap). On = uncapped. Implemented via `preview_all_rows` switch in accordion header + wired into `home_data_preview` and `table_reference` renders.
- [ ] `[FEATURE]` Label x/y axis adjustment module — edit title, policy change, color changes, points display — registered in audit. Large feature, grant-exploration candidate.

---

## RESEARCH / DECIDE

- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — manifest hashes + data hashes in DB associated with results; LIMS link in audit report; configurable output path per persona. ADR decision deferred until pilot funding identifies a concrete LIMS target.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search functionality in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] Improve the lab functionalities → collect all info disseminated across Test Lab, Blueprint, and Gallery into a coherent developer workflow. Needs dedicated design session.
- [ ] Audit apply improvement: apply to everything except those... to facilitate selection by exclusion.
- [ ] **TO DISCUSS — lab script**: Extract pilot manifest (reconstitution of lineage) — improve reusability.
- [ ] **TO DISCUSS — lab script**: Create tool-specific manifest (e.g. single-sheet variant).
- [ ] **TO DISCUSS — lab script**: Combine manifests — format detection, common datasets, branching.

### In-app contextual help (DECIDED 2026-05-09)

Two-tier: air-gapped contextual cards per workspace + optional full manual served from `docs/_site/`.

- [ ] **HELP-INLINE-1** `[sonnet/medium]`: Per-workspace contextual help modals. `?` button → `ui.modal_show()` with content from `app/src/help/<workspace>.md`. Write initial help content for Home and Blueprint.
- [ ] **HELP-DOCS-1** `[haiku/low]`: Bundle `docs/_site/` as Shiny static assets at `/docs/`. Conditional on `_site/` existing. Add "Full documentation →" link to contextual cards.

---

## 🟣 Blueprint Architect — Open Tasks

> Completed: LINEAGE-NAV-1, LINEAGE-EXPORT-1, BP-SCHEMA-1, SCHEMA-VERIFY-ACTIONS-1, SCHEMA-VERIFY-GEOMS-1, BP-AGENT-FLAG-1. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

### Blueprint IDE Forms (ADR-075)

- [ ] **BP-FORMS-1** `[sonnet/high]`: Form renderer in BLUEPRINT IDE — all widget types, column selector with upstream schema propagation on Apply, edit-in-place flow, schema invalidation markers on downstream nodes.
- [ ] **BP-ESCAPE-1** `[sonnet/medium]`: YAML escape hatch — read-only view (all `blueprint_enabled` personas) + editable mode (`manifest_edit_enabled`) with re-parse on save.
- [ ] **BP-UNDO-1** `[haiku/low]`: 20-step session undo deque for BLUEPRINT DAG state.
- [ ] **BP-HELP-1** `[sonnet/medium]`: Help panel — `__doc__` resolution, collapsible sections for composite actions, optional external URL button disabled in isolated deployments.
- [ ] **BP-COLOR-1** `[sonnet/medium]`: Color widget — column mapping toggle, palette library picker, hex picker, `from_project_colors` slot reserved as v2 placeholder.
- [ ] **BP-FLAG-1** `[haiku/low]`: Add `manifest_edit_enabled` flag to all six persona templates + `rules_persona_feature_flags.md` + bootloader cascade rule. ADR-075.

### ADR-076 — BLUEPRINT AI Agent Helper (MVP-1)

MVP-1 scope: `.claude/design/adr076_mvp.md`. Order matters — each gate must close before next starts.

- [x] **BP-AGENT-1** `[sonnet/high]`: `AgentAdapter` protocol + `ClaudeCliAdapter` (§11 subprocess isolation + auth probe) + `DisabledAdapter`. Dedicated `cwd={project_root}/agent_sessions/{uuid}/` per session; `flock` single-flight lock; auth probe at init; system prompt builder + per-turn context builder. Location: `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` + `agent_context.py`. Headless-safe. All backends buffered.

- [ ] **BP-AGENT-PARSER-1** `[sonnet/medium]`: `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py` — fenced-block extractor for `<!-- AGENT_TOOL_CALL --> ... <!-- /AGENT_TOOL_CALL -->` protocol (ADR-076 §10.1). JSON validation, per-tool schema dispatch, structured error turn on parse failure. Headless-safe.

- [ ] **BP-AGENT-TOOLS-1** `[sonnet/medium]`: 3 MVP-1 tools in `libs/blueprint_arch/src/blueprint_arch/agent_tools.py`: `get_available_actions`, `get_available_components`, `get_field_contract`. Each wraps existing `manifest_navigator`/registry APIs. Headless-safe.

- [ ] **BP-AGENT-INSTRUCT-1** `[sonnet/medium]`: `config/ui/agents/blueprint_default.md` — system prompt: tool-call output format (ADR-076 §10.1), intake questions, data-science guidance (filter ordering, join key validation, two-step cast), AMR/biology domain section placeholder. Create `config/ui/agents/` directory.

- [ ] **BP-AGENT-PANEL-1** `[haiku/low]`: Register `blueprint_agent_chat` panel type in `app/modules/sidebar_registry.py` with `gate_flag: "blueprint_agent_enabled"`. Add to BLUEPRINT workspace `right_sidebar.panels` in `developer_template.yaml` + `qa_template.yaml`.

- [ ] **BP-AGENT-UI-1** `[sonnet/medium]`: Chat panel render outputs in `app/handlers/blueprint_handlers.py`: cold-start greeting, conversation log (buffered, "thinking…" indicator), adapter-status banner, single-flight UI gate. No decision accordion, no Apply gate, no data toggle (MVP-1 scope). No streaming.

- [ ] **BP-AGENT-CSS-1** `[haiku/low]`: `.bp-agent-*` block in `config/ui/theme.css` — conversation bubbles, input row, status banner. Dark Grey #c0c0c0 background, SPARMVET Blue #345beb. No inline styles (ADR-055).

### Blueprint Architect — Other

- [ ] **TubeMap aesthetics** `[haiku/low]`: Tighter rail/tube look; rename 'ref' → 'Add' in nodes and legend.
- [ ] Full Blueprint Architect debug pass (field contracts, lineage rail, Zone C layout).
- [ ] **Action Registry Parity** `[sonnet/high]` (18-F): Expose 175+ `@register_action` entries in UI.
- [ ] **Visual Forking** `[sonnet/high]` (18-F): Select node → initiate new branch → YAML additions.
- [ ] **Field Gap Analysis tool** `[sonnet/medium]`: Field name → walk lineage to earliest insertion point.
- [ ] **Forward propagation hint** `[sonnet/medium]`: Show which output_fields / final_contract files need updating.
- [ ] **UX-NOTIF-3** `[haiku/low]`: Project-load notification for Blueprint Architect manifest reload.
- [ ] **Define** `[opus/high]`: ADR for Blueprint Architect full feature set — functionalities, help develop without code, input/output contracts, action insertions, update data view for selected lineage, improved data inspection, joint definitions, work in T1/T2/T3, definition of groups and plot recipe.

---

## 🟡 Deferred / Backlog

### Multi-System Deployment (Phase 23 C–E)

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).

### Filter / Propagation

- [ ] **PROP-2** `[sonnet/medium]`: Filter inventory panel — effective filter set per plot with per-filter tooltip.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR.
- [ ] **22-J-10** `[sonnet/medium]`: Aesthetic propagation (color/shape/fill) — deferred until gallery-clone supports aesthetic overrides.

### Export (enhancements)

- [ ] **EXPORT-2** `[sonnet/medium]`: Selective export — per-tier checkboxes.
- [ ] **EXPORT-3** `[sonnet/medium]`: Quarto HTML report — typography, plot placement, methods section, TOC polish.
- [ ] **EXPORT-4** `[sonnet/low]`: Global export — per-plot height/width control before bundling.
- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Depends on Blueprint Architect stability.

### Gallery & UI

- [ ] Gallery: Re-verify "Clone to Sandbox" after ADR-057 sidebar refactor.
- [ ] **GALLERY-MAP** `[opus/high]` `[investigation]`: Map chart types. Blocked — `geom_map` requires GeoDataFrame; needs spatial manifest format + geopandas integration design.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[investigation]`: Flow / network chart types. Blocked — plotnine has no native support; needs feasibility study.
- [ ] **Taxonomy Data Audit** `[@user]`: Verify/correct tags in `assets/gallery_data/*/recipe_manifest.yaml`.
- [ ] Gallery thumbnails for faster visual scanning.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.
- [ ] **UX-DEVINSP-1** `[sonnet/medium]`: Test Lab right sidebar + left sidebar redesign — functionality TBD.
- [ ] **UX-CSS-DEMO** `[@user]`: Review `assets/demo/demo_vetinst.css` after default theme finalised.
- [ ] **UX-NOTIF-2** `[sonnet/medium]`: Persist `notification_log` to T3 ghost so alerts survive page refresh. Linked to UX-NOTIF-1 (ADR-060).

### VizFactory

- [ ] `geom_map` — deferred; requires spatial data (GeoDataFrame).
- [ ] **21-F-7**: Add `scale_x_discrete` / `scale_y_discrete` to manifests where Year/ST columns are categorical.

- [ ] **VIZFAC-PLOT-CASCADE-1** `[opus/high]` `[design-thinking]`: Design the plot configuration priority cascade. Open questions to resolve before any implementation:
  **Proposed priority order (highest wins):**
  1. `spec:` — explicit per-plot settings in `analysis_groups.<group>.plots.<id>.spec`
  2. Optimization layer — computed at render time from data (auto-label sizing, axis rotation, density-aware positioning). Currently partially implemented as `_auto_adjust_axis_labels()` in VizFactory as an unconditional post-pass.
  3. `plot_defaults:` — manifest-level fallback block (currently parsed into `raw_config` but not consumed by VizFactory).
  4. VizFactory built-in defaults — hardcoded fallbacks inside `viz_factory.py`.

  **Design questions:**
  - What exact keys belong in `plot_defaults:` (theme, font_family, height, width, label_size, legend_position, …)? Define the schema before wiring.
  - Where does the merge happen? `VizFactory.render()` is the natural merge point — receives `plot_config` dict; merges manifest defaults in before processing layers.
  - **Optimization layer scope (DECIDED):** purely visual/aesthetic adaptation — auto-adjusting how the rendered graph looks (label sizes, rotation, tick spacing, legend position). No data transformation, no layer addition/removal, no filtering. It only modifies rendering parameters of an already-assembled plot. This is distinct from T3 (data decisions with audit trail) and from the wrangling pipeline (data shape).
  - **Optimization approach (DECIDED):** Two candidate paths evaluated:
    - **Path A — data-aware pre-pass:** count distinct values on the mapped column (e.g. x-axis) from the LazyFrame before collect(); feed counts into parameter adjustments before rendering. Clean but adds a collect() round-trip.
    - **Path B — two-pass render:** render the plot once → inspect the plotnine object's tick/label positions → recompute parameters (rotation, size, spacing) → re-render with updated params. More accurate (reads actual rendered geometry) but doubles render cost and requires plotnine internals access.
    - **Decision:** Path B is the correct long-term approach (accurate to rendered output, no separate collect()); Path A is an acceptable MVP approximation. Both are **planned but deferred** — this is an advanced feature. Current `_auto_adjust_axis_labels()` is a schema-only heuristic and stays as-is until this cascade design is resolved.
  - How does this interact with the T3 `aesthetic_override` node? T3 overrides should win over everything (user's explicit session decision). Suggested position: T3 aesthetic_override > spec > optimization > plot_defaults > built-ins.
  - `_auto_adjust_axis_labels()` currently runs after all layers — must be repositioned as the "optimization" phase between steps 2 and 3 in the merge, or confirmed as a separate unconditional post-pass that only fills gaps.
  - Blueprint IDE implication: the form catalog (ADR-075) should surface `plot_defaults` as a manifest-level settings panel, not per-plot, so the user understands the cascade when editing.

  **Suggested output of the design session:** a short spec doc (`.claude/design/plot_config_cascade.md`) covering the merge function signature, key schema for `plot_defaults`, and the T3 override interaction. Then file concrete implementation tasks under VizFactory and manifests.

### Technical Debt

- [ ] **REPO-CLEAN-1** `[haiku/low]` `[repo-hygiene]`: Full git history purge — remove EVE_WORK/, session logs, .vscode user files from ALL past commits. Prerequisite: backup to external disc + gdrive sync.
  ```bash
  pip install git-filter-repo
  git filter-repo --path EVE_WORK/ --path .claude/logs/sessions/ \
    --path .claude/logs/handoffs/archive/ \
    --path .vscode/bookmarks.json --path .vscode/favorites/ \
    --path .vscode/settings.json --path .directory \
    --invert-paths
  git push origin dev --force
  ```

- [ ] **Unified Materialization** `[haiku/low]`: `debug_wrangler.py` / `debug_assembler.py` — auto-create dated `tmpAI/{date}/{lineage}/` subfolders.
- [ ] **T3 lf threading** `[sonnet/medium]`: When new T3 node types added, thread through `_apply_t3_to_lf`. Design in `.claude/tasks/design_sge_lineage_t3.md`.
- [ ] **PYPROJECT-DEPS-1** `[haiku/low]` `[repo-hygiene]`: Verify all 8 `libs/*/pyproject.toml` files declare `libs/utils` as explicit dependency wherever they import from it.
- [ ] **ACTION-RENAME-1** `[sonnet/medium]` `[repo-hygiene]`: Audit `@register_action` and `@register_plot_component` names for alignment with Polars/Plotnine naming. Provide compatibility shims + `scripts/migrate_manifests.py`.
- [ ] **ADR-011 cross-lib violations** `[opus/high]` `[repo-hygiene]`: Remaining cross-lib import violations — `blueprint_arch/blueprint_mapper.py` → `utils.config_loader`, `transformer/pipeline.py` → `utils.config_loader` + `ingestion.ingestor`, `transformer/data_assembler.py` → `utils.hashing`, `transformer/data_wrangler.py` + `metadata_validator.py` → `utils.errors`, `viz_factory/viz_factory.py` → `utils.errors`.
- [ ] **UTILS-RELOC-2** `[haiku/low]`: Deduplicate `gallery_manager.py` (exists in both `libs/utils/` and `libs/viz_gallery/`).
- [ ] **CODE-DOCS-RETROSPECTIVE** `[deferred — pre-deployment review sprint]`: Developer-level docstrings across all `libs/` + `app/`. Tier A (module header) + Tier B (public functions) + Tier C (`@register_action` / `@register_plot_component`). Implementation order: `libs/transformer/` → `libs/viz_factory/` → `app/handlers/` → remaining libs → `app/src/`. Write `scripts/audit_code_quality.py` first.

---

## 🟣 Completed Phases — Archived

| Phase | Description | Completed | Archive |
|---|---|---|---|
| Phases 16–18, 21-A–B | Nav/routing, manifest-driven tabs, tier toggle, layout | 2026-04-23 | [tasks_archive_2026-04-10.md](archives/tasks_archive_2026-04-10.md) |
| Phase 21-C–I, IU-1–7 | Comparison mode, filters, right sidebar, export bundle, VizFactory | 2026-04-23–30 | [tasks_archive_2026-04-14.md](archives/tasks_archive_2026-04-14.md) |
| Phase 22 (A–J) | Session mgmt, T3 audit, per-plot scoping, propagation | 2026-04-25 | [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) |
| Phase 23-A/B | Deployment profile, connector library | 2026-04-30 | [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) |
| Phase 24 | `home_theater.py` decomposition (ADR-051) | 2026-05-01 | [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) |
| Phase 25 (A–O) | Left sidebar restructure, persona flag gating, ADR-052+053 | 2026-05-01 | [tasks_archive_phase25.md](archives/tasks_archive_phase25.md) |
| Phase 26 CSS | UI harmonisation: view banners, button colours, Gallery sidebar refactor | 2026-05-02 | ADR-056, ADR-057 |
| DEMO-1..4 | Monday demo render/filter bugs — all fixed | 2026-04-30 | commits `55ab1c5` `33afa1b` etc. |
| Phase 28/29 | Export redesign + assembly→join rename + lib extraction | 2026-05-04/05 | ADR-066, ADR-067, ADR-068 |
| Phase 30 | Agent infra + deployment hardening | 2026-05-05 | commit `891f157`, `2dcd1c2` |
| Phase 31 | Sidebar Slot Registry (ADR-073) + Diagnostic Error Discipline (ADR-078) + Blueprint schema (ADR-075) + ADR-076 flag (ADR-077) | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |

---

**Archive Pointers:**
- [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) — Phase 31 complete tasks (audit P0/P1/P2, Sidebar, Diag-Error, Blueprint schema, ADR-076 flag)
- [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) — Wave 1 remediation + Phase 22 bug resolutions
- [tasks_archive_2026-04-10.md](archives/tasks_archive_2026-04-10.md)
- [tasks_archive_2026-04-14.md](archives/tasks_archive_2026-04-14.md)
- [tasks_archive_phase14.md](archives/tasks_archive_phase14.md)
- [tasks_archive_phase24.md](archives/tasks_archive_phase24.md)
- [tasks_archive_phase25.md](archives/tasks_archive_phase25.md)
- [tasks_archive_documentation.md](archives/tasks_archive_documentation.md)
- [tasks_archive_infrastructure.md](archives/tasks_archive_infrastructure.md)
- [tasks_archive_integration_qa.md](archives/tasks_archive_integration_qa.md)
- [tasks_archive_viz_factory.md](archives/tasks_archive_viz_factory.md)
- [tasks_test_ui_current.md](tasks_test_ui_current.md) — current UI test checklist
