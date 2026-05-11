# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-09 (restructured: Do Now / Discuss / Deferred tiers; inline Completed noise removed) by @dasharch

---

## Task Organization Protocol (read before adding or moving items)

| Section | What belongs here |
|---|---|
| **🟢 Do Now** | Immediately actionable — no blocker, no design decision pending. Audit-detected problems that need no user discussion go **at the top of this section**, above all other items. |
| **🤔 Needs Discussion / Decision** | Requires a design pass, ADR authoring, or explicit scoping before any code. No implementation until resolved. |
| **⏳ Deferred / Blocked** | Blocked by library limitation, another task, or large-scale planned work. Sub-group by what is blocking. |
| **🟡 Bio-Scientist Enhancements** | `[ENHANCEMENT REQUEST]` items from manifest design sessions only (see `rules_persona_bioscientist.md §4-A`). |
| **👤 User Required** | Needs user action, decision, or explicit discussion. No agent progress until user responds. |

**Inline `> Completed:` pointers inside sections are FORBIDDEN** — they break the actionability view. When items are done, move them to the archive file and update the archive table + pointers at the bottom. Never leave a `> Completed:` line inside an active section.

---

## 🟢 Do Now

Items with no blockers — can be started immediately.

### Audit Fixes — Documentation (2026-05-09)

*Findings from `audit_documentation_2026-05-09_*.md` — triage per protocol. Mechanical items being fixed in-session; gaps requiring new content tracked here.*

- [x] **DOC-DRIFT-1** `[AUDIT]` `[haiku/low]`: Fix mechanical doc drift — 6 files. *(Fixed in-session 2026-05-09)*
  - `docs/workflows/dashboard_app.qmd:69` — stale path `app/modules/manifest_navigator.py` → `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` (ADR-067)
  - `docs/workflows/dashboard_app.qmd:55` — underscore persona IDs → hyphens
  - `README.md:78` — persona list incomplete; add `demo-vetinst`, `web-demo`
  - `libs/utils/README.md` — remove phantom GalleryManager entry (belongs in viz_gallery)
  - `libs/transformer/README.md:19-25` — phantom debugger class names → plain CLI script descriptions
  - `docs/appendix/manifest_structure.yaml:14` — `assembly:` → `join:` (matches `rules_manifest_structure.md §2`)
- [x] **DOC-DRIFT-EMOJI** `[AUDIT]` `[haiku/low]`: Fix 9 emoji violations in production Python source (active enforcement per `rules_code_quality.md §1`). *(Fixed in-session 2026-05-09)*
  - `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py:239` — `ℹ️` in Mermaid label f-string
  - `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py:456` — `⚠` in Cytoscape label f-string
  - `libs/ingestion/src/ingestion/ingestor.py:102` — `⚠️` in print f-string
  - `libs/transformer/src/transformer/actions/persistence/anchor.py:33` — `💾` in print f-string
  - `libs/transformer/src/transformer/data_assembler.py:126` — `🗲` in print f-string
  - `libs/transformer/src/transformer/data_assembler.py:132` — `⚠️` in print f-string
  - `libs/transformer/src/transformer/data_assembler.py:165` — `⚠️` in print f-string
  - `libs/viz_factory/src/viz_factory/viz_factory.py:108` — `🍃` in print f-string
  - `libs/viz_factory/src/viz_factory/viz_factory.py:171` — `⚠️` in print f-string
- [x] **DOC-GAP-1** `[AUDIT]` `[sonnet/medium]`: Expand `docs/workflows/ui_persona.qmd` with 4 missing items. ✅ All 4 gaps addressed: eight personas table (+ demo-vetinst, web-demo, qa), ADR-076 blueprint_agent_enabled flag + config block, ADR-077 fatal cascade entries in dependency table, blueprint_agent_chat panel type added to §11d table.
- [x] **DOC-GAP-2** `[AUDIT]` `[haiku/low]`: Add `demo-vetinst` and `web-demo` rows to `.claude/knowledge/persona_traceability_matrix.md`. ✅ Added to all three tables (Persona Capability Matrix, Right Sidebar Visibility, Filter Behavior).
- [x] **DOC-GAP-3** `[AUDIT]` `[haiku/low]`: ✅ Added Section 9 to deployment guide with ADR-074 lineage API import path and two usage examples (`build_plot_lineage`, `get_plot_ids_in_group`).
- [x] **DOC-GAP-4** `[AUDIT]` `[haiku/low]`: Triage 8 orphaned `.qmd` files. ✅ Added 2 to nav (`deployment_guide.qmd`, `ui_persona.qmd`), deleted 3 redundant duplicates, archived 3 with `draft: true`.
- [x] **DOC-GAP-5** `[AUDIT]` `[haiku/low]`: Fix 2 semantic drift items — ✅ both READMEs updated:
  1. `libs/ingestion/README.md` — Replaced "ExcelHandler class" with accurate "Excel-to-TSV CLI (excel_handler.py)" description.
  2. `libs/transformer/README.md` — Replaced "Comparison Theater" with "Comparison Mode (T2 reference vs T3 active)".

### Audit Fixes — ADR Compliance (2026-05-09)

*Findings from `audit_adr_compliance_2026-05-09.md` (Routine 18).*

- [x] **ADR-078-ACTIONS-1** `[AUDIT]` `[sonnet/medium]`: Retrofit `TransformationError` into transformer actions that silently pass through on invalid input. Fixed 24 silent `return lf` pass-throughs across `expressions.py`, `analytical.py`, and `advanced.py`. (Note: the audit report incorrectly named the error class `SPARMVET_DiagnosticError` — actual class is `TransformationError` from `utils.errors`.)

- [x] **TRANSFORMER-SUITE-FIX** `[sonnet/medium]`: Fixed transformer integrity suite failing 60/60 after ADR-078 fix. Root cause: `debug_wrangler.py` and `debug_assembler.py` used `ConfigManager` unconditionally, which enforces `analysis_groups:` presence (a full-pipeline requirement). Standalone wrangling test manifests don't have `analysis_groups:`, so validation fired before any test ran. Fix: bypass `ConfigManager` for manifests without `analysis_groups:`, use `yaml.safe_load()` directly instead. Also fixed missing `--data` argument in the suite's `subprocess` call to `debug_wrangler.py`. Result: 62/62 clean (60 wrangler PASSED, relational_audit PASSED).

### Deployment

- [ ] **DEPLOY-CONNECT-1** `[sonnet/medium]` `[deferred — Connect adoption TBD]`: Posit Connect deployment — editable library install handling. Keep code Connect-ready to avoid heavy refactoring when the time comes.
  - [ ] Add each editable lib as relative path entry in `requirements.txt`: `-e ./libs/ingestion`, `-e ./libs/transformer`, etc.
  - [ ] Document `app/src/main.py` as entry point for `rsconnect-python` bundle.
  - [ ] Deployment profile via `SPARMVET_PROFILE` env var; add `config/deployment/connect/connect_profile.yaml` template.
  - [ ] Smoke test: clean venv from scratch, run `scripts/install_libs.sh`, verify no import errors.

### UI Debugging

- [ ] **UX-DEBUG-EXPORT-1** `[sonnet/medium]`: Retest and debug the export pipeline end-to-end against a real data session.
- [ ] **UX-DEBUG-GHOST-1** `[sonnet/medium]`: Define and test the session ghost save/restore flow when Tier 3 is activated — confirm T3 state survives a page refresh.
- [ ] **UX-DEBUG-IMPORT-1** `[sonnet/medium]`: Test file import and schema mapping from user-uploaded files through to manifest association.

### Runtime Error Discipline

- [x] **DIAG-RUNTIME-ADR** `[opus/high]`: ✅ ADR-079 authored 2026-05-10 (replaces placeholder). Decisions: `PipelineError` sits alongside `DeploymentError` (shared 5-field shape, no inheritance); render surface is per-category (`plot_overlay`/`notification`/`audit_panel`/`data_import_panel`/`blueprint_inline`); `evidence` dict carries sample rows + offending values + schema diff (5-row / 50-col cap); audit-trail capture via new `session_pipeline_errors` reactive value, written to `report.qmd` "Pipeline Issues During Session" section and into T3 Ghost. Audience model adds `analyst` / `data_provider` / `manifest_author` to ADR-078's `operator` / `developer`.
- [ ] **DIAG-RUNTIME-BASE-1** `[sonnet/medium]`: Phase 1 — `PipelineError` dataclass + helpers + per-surface renderers. Files: `libs/utils/src/utils/pipeline_error.py` (dataclass, `format()`, `to_audit_row()`, `make_render_payload()`); `app/src/render/pipeline_error_renderers.py` (one renderer per `surface` value). Plus unit tests asserting field shape and render-payload structure per surface. Unblocks all DIAG-RUNTIME-* retrofits.
- [ ] **DIAG-RUNTIME-AUDIT-1** `[sonnet/medium]`: Phase 3 — `session_pipeline_errors` reactive value in `server.py` + audit panel "Pipeline Issues" sub-section + `report.qmd` "Pipeline Issues During Session" section + T3 Ghost `pipeline_errors:` extension. Depends on DIAG-RUNTIME-BASE-1.

### Blueprint Architect

- [x] **BP-DEBUG-1** `[sonnet/high]`: Full Blueprint Architect debug pass — field contracts rendering, lineage rail accuracy, Zone C layout stability. ✅ Committed ee05ea0.
  - [x] Fixed `architect_active_plot` — now resolves plot specs from `analysis_groups` for pipeline manifests (was silently returning None since ADR-043). Builds synthetic flat manifest before `VizFactory.render()` call.
  - [x] Fixed 8 emoji violations in `blueprint_handlers.py` `print()` calls (`rules_code_quality.md §1`).
  - [x] Zone C layout stability reviewed — `bp_action_form_ui` 4-way dependency is intentional, no Rule R4 violation. `ui.js_eval` click-simulation in `handle_lineage_node_click` (wrangle_studio.py:1207) is fragile UX but not a crash risk; tracked as BP-LINEAGE-NAV-1.
- [ ] **BP-LINEAGE-NAV-1** `[sonnet/medium]`: Replace `ui.js_eval("document.getElementById('btn_import_manifest').click()")` in `handle_lineage_node_click` with a shared `reactive.Value(selected_lineage_rel)` that both lineage rail clicks and the Import button write to; a single `@reactive.Effect` watches it and calls `_do_load_component()` directly. Eliminates race condition and DOM-dependency.
- [x] **BP-ACTION-PARITY-1** `[sonnet/medium]`: Expose `@register_action` entries in Blueprint IDE UI (18-F). ✅ Committed acb27ce. Added search + context filter to action picker; choices grouped into "Rich form" (19 with ui_schema) and "YAML fallback" (43 without); reactive via `_update_action_picker()` effect.
- [ ] **BP-VISUAL-FORK-1** `[sonnet/high]`: Visual Forking — select node → initiate new branch → YAML additions (18-F).
- [x] **BP-FIELD-GAP-1** `[sonnet/medium]`: Field Gap Analysis tool — field name → walk lineage to earliest insertion point. ✅ Committed c41488c. Input + Find button added to Interface tab; field_gap_ui checks active_upstream/downstream and provides Rail navigation hints when field not found at current tier.
- [x] **BP-FWD-HINT-1** `[sonnet/medium]`: Forward propagation hint — show which output_fields / final_contract files need updating when a field is added or renamed. ✅ Committed 29300a2. Integrated into field_gap_ui: scans downstream chain nodes for explicit output_fields contracts that exclude the queried field; inline contracts checked directly, file-linked ones emit manual-verify warning.

### Gallery & Visualization

- [ ] **GALLERY-CLONE-DECOUPLE-1** `[sonnet/high]`: Decouple gallery clone from WrangleStudio. Two bugs to fix together:
  1. **ADR-071 violation:** `WrangleStudio` instantiated unconditionally in `server.py` — must be gated on `developer_mode_enabled`.
  2. **Broken clone for `project-independent` persona:** clone silently writes to WrangleStudio with no UI.
  **Fix:** Replace `wrangle_studio.logic_stack.set(valid_nodes)` in `gallery_handlers.py` with a Home T3 transplant — insert a `developer_raw_yaml` RecipeNode into `_pending_t3_nodes` in `home_state`. Gate "Send to T3" on `bootloader.is_enabled("t3_sandbox_enabled")` (§12e). Remove `wrangle_studio` kwarg from `gallery_handlers.define_server()`. Gate `WrangleStudio` instantiation in `server.py`.
  **Unblocks:** 22-J-10 (aesthetic propagation).
- [x] **VIZ-DISCRETE-SCALE-1** `[sonnet/low]`: ✅ Audited all pipeline plot specs. Added `scale_x_discrete` to 3 specs missing it (`MLST_counts_bar.yaml`, `abromics_st_by_country`, `abromics_st_by_source`). 2_test_data_ST22_dummy plots already correct; `year_distribution.yaml` intentionally keeps `scale_x_continuous` (year is numeric).
- [x] **VIZ-GALLERY-THUMB-1** `[sonnet/low]`: ✅ `generate_previews.py` now saves `preview_thumb.png` (100px wide, aspect-ratio preserved, LANCZOS) after each full preview render. Handles thumb-only generation from existing full plots. `gallery_manager.py` adds `has_thumb` + `has_preview` fields to index registry. Pre-generated 32 thumbs for existing recipes.

### Audit Fixes — Library Tests & Dependencies (2026-05-09)

*Findings from `audit_library_tests_2026-05-09.md` (Routine 10) and `audit_package_deps_2026-05-09.md` (Routine 11).*

- [x] **LIB-TESTS-BLUEPRINT-1** `[AUDIT]` `[sonnet/medium]`: ✅ Fixed 188 pytest failures in `libs/blueprint_arch/tests/test_schema_registry.py` (194 total tests now pass). Root cause: test file was importing `AVAILABLE_WRANGLING_ACTIONS` (function dict) instead of `ACTION_SCHEMAS` (schema dict). Changed imports and `register()` call in test file. All 58 action catalog tests + 36 component catalog tests + semantic rules / filtering / search tests now pass.
- [x] **LIB-TESTS-VIZ-TIMEOUT-1** `[AUDIT]` `[haiku/low]`: ✅ Increased `TIMEOUT_SECONDS` in `scripts/audit_library_tests.py` from 120 → 300 (5 min) to allow viz_factory integrity suite (193+ components) to complete.
- [x] **PKG-PLOTNINE-PATCH-1** `[AUDIT]` `[haiku/low]`: ✅ Upgraded plotnine 0.15.3 → 0.15.4 and pinned version in pyproject.toml (>=0.15.4,<0.16.0). Re-ran parity audit: 222 plotnine symbols, 168 registered (75% coverage). Identified new components in 0.15.4 (geom_bin2d, stat_bin2d, stat_pointdensity) — registration deferred to BP-ACTION-PARITY-1. No breaking changes affecting current registrations.
- [x] **PKG-IMPORTLIB-MAJOR-1** `[AUDIT]` `[sonnet/low]`: ✅ Investigated importlib_metadata 9.0.0 MAJOR upgrade. Found: transitive dependency via shiny → opentelemetry-api 1.41.1. opentelemetry-api 1.41.1 requires importlib-metadata<8.8.0, so upgrade to 9.0.0 is BREAKING. Solution: Pinned importlib_metadata to >=6.0,<9.0.0 in pyproject.toml. Verified with `pip check` — no broken requirements.

### Infrastructure & Housekeeping

- [ ] **AUDIT-FIRST-TRIAGE-1** `[haiku/low]`: After first scheduled audit runs fire, triage all unprocessed reports per `audit_triage_protocol.md`. Run `grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md` to find them.
- [x] **TECH-DEBUG-MATERIALIZE-1** `[haiku/low]`: ✅ `debug_wrangler.py` and `debug_assembler.py` already had dated `tmpAI/{date}/{lineage}/` defaults. Fixed `debug_gallery.py` which still defaulted to fixed `tmp/` paths — now all three scripts share the same dated-path convention.
- [ ] **HELP-INLINE-1** `[sonnet/medium]`: Per-workspace contextual help modals. `?` button → `ui.modal_show()` with content from `app/src/help/<workspace>.md`. Write initial help content for Home and Blueprint.

---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law. Decision needed: scope and migration plan before touching live handlers. [Not sure if wrong — it's part of the app itself]
- [x] **VIZFAC-PLOT-CASCADE-1** `[opus/high]` `[design-thinking]`: ✅ Design spec authored 2026-05-10 at [.claude/design/plot_config_cascade.md](../design/plot_config_cascade.md). Five-tier cascade L5(T3 override) > L4(spec) > L3(optimisation) > L2(plot_defaults) > L1(built-ins) resolved at one merge point via new `resolve_plot_config()` pure function. Closes the silent gap where T3 `aesthetic_override` nodes are recorded/exported but never rendered. Locks `plot_defaults:` schema (§7a) and reserves L3 hooks (§5c) for future optimisation heuristics. Six concrete implementation tasks emitted below (VIZFAC-RESOLVER-1 through VIZFAC-BLUEPRINT-FORM-1).

#### Cascade implementation (derived from VIZFAC-PLOT-CASCADE-1 design)

- [ ] **VIZFAC-RESOLVER-1** `[sonnet/high]`: Create `libs/viz_factory/src/viz_factory/plot_config_resolver.py` with `resolve_plot_config()`, `compute_optimisation_layer()`, `_dedupe_layers()`, `_BUILTIN_DEFAULTS`. Pure functions, no plotnine import. Unit tests assert provenance per key for all 5 tiers + dedup order on `theme_*`/`coord_*`/`facet_*`/`scale_*_*`/`element_text` per cascade truth table (design §11).
- [ ] **VIZFAC-RENDER-WIRE-1** `[sonnet/medium]` `[blocked: VIZFAC-RESOLVER-1]`: Refactor `VizFactory.render()` to use `resolve_plot_config()`. Move `factory_id` normalisation, flat-aesthetic promotion, and `_auto_adjust_axis_labels()` into the resolver. `viz_factory_integrity_suite` MUST pass unchanged.
- [ ] **VIZFAC-T3-OVERRIDE-1** `[sonnet/medium]` `[blocked: VIZFAC-RENDER-WIRE-1, DIAG-RUNTIME-BASE-1]`: Wire `aesthetic_override` into `home_theater.py` plot renders — extract `home_state["t3_plot_overrides"].get(plot_id)`, pass as `aesthetic_override=` kwarg. Schema validation per design §6 (mutex check on `fill_color`/`fill_palette`, key whitelist) emits `PipelineError`.
- [ ] **VIZFAC-T3-EXPORT-1** `[sonnet/medium]` `[blocked: VIZFAC-T3-OVERRIDE-1]`: Same wiring in `export_handlers.py` so exported plots reflect T3 overrides. Subsumes part of TECH-T3-THREAD-1 scope.
- [ ] **VIZFAC-DEFAULTS-DOCS-1** `[sonnet/low]` `[blocked: VIZFAC-RESOLVER-1]`: Document `plot_defaults:` allowed keys (design §7a) in `rules_manifest_structure.md §10`, `rules_viz_factory.md §6`, `docs/appendix/manifest_structure.yaml`. Unknown-key warning machinery emits `PipelineError(who: manifest_author, surface: notification)`.
- [ ] **VIZFAC-BLUEPRINT-FORM-1** `[sonnet/medium]` `[blocked: VIZFAC-DEFAULTS-DOCS-1]`: Blueprint IDE — mount `plot_defaults` editor form in BLUEPRINT logic sidebar when active node is the manifest root. Form fields driven by §7a allowed keys + their `ui_schema` (mirror action-picker pattern).

- [ ] **LAB-WORKFLOW-1** `[opus/high]`: Collect all developer workflow info from Test Lab, Blueprint, and Gallery into a coherent end-to-end developer workflow. Needs dedicated design session before implementation.
- [ ] **UX-APPLY-IMPROVE-1** `[sonnet/medium]`: Audit Apply improvement — "apply to all except…" selection-by-exclusion mode. Needs design pass before scoping.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR before implementation.

---

## ⏳ Deferred / Blocked

### Blocked by DIAG-RUNTIME-BASE-1 (Phase 1 base class — see ADR-079)

- [ ] **DIAG-RUNTIME-INGESTION-1** `[sonnet/medium]` `[blocked: DIAG-RUNTIME-BASE-1]`: Retrofit `libs/ingestion/src/ingestion/ingestor.py` — file-not-found, encoding errors, delimiter mismatch, schema mismatches, sanitization rejections. `who: data_provider` for content errors, `who: analyst` for upload errors. `surface: data_import_panel`. ADR-079 Phase 2.
- [ ] **DIAG-RUNTIME-ASSEMBLER-1** `[sonnet/medium]` `[blocked: DIAG-RUNTIME-BASE-1]`: Retrofit `libs/transformer/src/transformer/data_assembler.py` — `ColumnNotFoundError`, `SchemaError` on join, dtype mismatches, empty result frames, Cartesian-product blowups. `who: manifest_author`. `surface: plot_overlay` (with `plot_scope` populated). ADR-079 Phase 2.
- [ ] **DIAG-RUNTIME-WRANGLER-1** `[sonnet/medium]` `[blocked: DIAG-RUNTIME-BASE-1]`: Retrofit `libs/transformer/src/transformer/data_wrangler.py` — action-name not registered, action arg validation against `ui_schema`. `who: manifest_author` for manifest-source nodes, `who: analyst` for T3 sandbox nodes. `surface: plot_overlay` or `audit_panel` depending on origin. ADR-079 Phase 2.
- [ ] **DIAG-RUNTIME-VIZFACTORY-1** `[sonnet/medium]` `[blocked: DIAG-RUNTIME-BASE-1]`: Retrofit `libs/viz_factory/src/viz_factory/viz_factory.py` — component not registered, missing required aesthetic, plotnine render exceptions. `who: manifest_author` for spec issues, `who: developer` for plotnine internals. `surface: plot_overlay`. ADR-079 Phase 2.
- [ ] **DIAG-RUNTIME-T3APPLY-1** `[sonnet/medium]` `[blocked: DIAG-RUNTIME-BASE-1]`: T3 Apply path failures in `app/handlers/audit_stack.py` — downstream invalidation, comment-gate violations. `who: analyst`. `surface: audit_panel`. ADR-079 Phase 2.
- [ ] **DIAG-RUNTIME-BLUEPRINT-1** `[sonnet/medium]` `[blocked: DIAG-RUNTIME-BASE-1]`: Manifest fragment validation failures during BLUEPRINT IDE editing. `who: manifest_author`. `surface: blueprint_inline`. ADR-079 Phase 2.

### Blocked by library limitations

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — library limitation]`: Register `geom_map` component in VizFactory. Blocked: plotnine has no native GeoDataFrame/spatial support; requires geopandas integration and a spatial manifest format design. Unblocks: GALLERY-MAP.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred — library limitation]`: Map chart types in Gallery. Blocked by VIZ-GEOM-MAP-1.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[deferred — library limitation]`: Flow / network chart types. Blocked: plotnine has no native network/Sankey/flow support. Requires feasibility study — candidate libs: `networkx` + custom geom, or external renderer.

### Blocked by other tasks

- [ ] **22-J-10** `[sonnet/medium]`: Aesthetic propagation (color/shape/fill) — deferred until GALLERY-CLONE-DECOUPLE-1 ships.
- [ ] **PROP-2** `[sonnet/medium]`: Filter inventory panel — effective filter set per plot with per-filter tooltip.
- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.
- [x] **TECH-T3-THREAD-1** `[sonnet/medium]`: `t3_plot_overrides` (aesthetic override state) now collected and included in export bundle: `t3_steps.yaml` gains `t3_aesthetic_overrides:` key; `_build_methods_section()` extended with aesthetic override prose; design doc updated. Rendering gap (L5 cascade) blocked by VIZFAC-RESOLVER-1 and tracked as VIZFAC-T3-OVERRIDE-1.

### Planned / Large-scale backlog

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).
- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — manifest hashes + data hashes in DB; LIMS link in audit report; configurable output path per persona.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.
- [ ] **UX-DEVINSP-1** `[sonnet/medium]`: Test Lab right sidebar + left sidebar redesign — functionality TBD.

### Repo hygiene / tech debt

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
- [x] **PYPROJECT-DEPS-1** `[haiku/low]` `[repo-hygiene]`: All libs that import utils (`blueprint_arch`, `connector`, `transformer`, `viz_factory`) already declare `"libs/utils"` in their `pyproject.toml`. `ingestion`, `test_lab`, `viz_gallery` have zero utils imports — no changes needed.
- [ ] **ACTION-RENAME-1** `[sonnet/medium]` `[repo-hygiene]`: Audit `@register_action` and `@register_plot_component` names for alignment with Polars/Plotnine naming. Provide compatibility shims and write `scripts/migrate_manifests.py` (script does not exist yet — separate from `assets/scripts/normalize_manifest_fields.py` which normalizes field dict format, not action names).
- [ ] **ADR-011 cross-lib violations** `[opus/high]` `[repo-hygiene]`: Remaining cross-lib import violations — `blueprint_arch/blueprint_mapper.py` → `utils.config_loader`, `transformer/pipeline.py` → `utils.config_loader` + `ingestion.ingestor`, `transformer/data_assembler.py` → `utils.hashing`, `transformer/data_wrangler.py` + `metadata_validator.py` → `utils.errors`, `viz_factory/viz_factory.py` → `utils.errors`.
- [ ] **CODE-COMMENT-STANDARD** `[sonnet/low]` `[active]`: Enforce commenting standard across `libs/` + `app/` — Emoji ban (§1) + WHY-not-WHAT comment philosophy (§2). No script needed. Run `grep -rE '(#.*[✅❌🔧🚀]|# TODO)' libs/ app/` to find violations. Note: do NOT add docstring tiers yet — that is CODE-DOCS-RETROSPECTIVE below.
- [ ] **CODE-DOCS-RETROSPECTIVE** `[deferred — pre-deployment review sprint]`: Developer-level docstrings across all `libs/` + `app/`. Tier A (module header) + Tier B (public functions) + Tier C (`@register_action` / `@register_plot_component`). Implementation order: `libs/transformer/` → `libs/viz_factory/` → `app/handlers/` → remaining libs → `app/src/`. Write `scripts/audit_code_quality.py` first (see `rules_code_quality.md §4-§5`). Do not start until pre-deployment sprint begins.

---

## 🟡 Pending Bio-Scientist Enhancements

_No current enhancement requests. Append items here using the `[ENHANCEMENT REQUEST]` protocol (`rules_persona_bioscientist.md §4-A`) when a manifest design session exposes a missing action or plot component._

---

## 👤 User Required

Tasks requiring user decision, user action, or explicit discussion before implementation can proceed.

- [ ] Discuss - Aesthetics / automation visuals -> capture and adding to T3 audit ? possibilities ? Consequences ? Gating ?  
- [ ] **[@user] Taxonomy Data Audit**: Verify/correct tags in `assets/gallery_data/*/recipe_manifest.yaml` against `assets/gallery_data/TAXONOMY_CHEATSHEET.md`.
- [ ] **[@user] UX-CSS-DEMO**: Review `assets/demo/demo_vetinst.css` after default theme is finalised.
- [ ] **[FEATURE]** Label x/y axis adjustment module — edit title, policy change, color changes, points display — registered in audit. Large feature, grant-exploration candidate.
- [ ] **[TO DISCUSS]** Lab script: Extract pilot manifest (reconstitution of lineage) — improve reusability.
- [ ] **[TO DISCUSS]** Lab script: Create tool-specific manifest (e.g. single-sheet variant).
- [ ] **[TO DISCUSS]** Lab script: Combine manifests — format detection, common datasets, branching.
- [ ] **[TO DISCUSS] BP-ADR-FULL-1** (ADR-082) — see `.claude/design/blueprint_full_feature_set_research.md` §6. Eve's input needed on Q1 (preview trigger), Q2 (T3 boundary), Q5 (joint UI), Q7 (data inspection scope) before authoring.
  - **Research & discussion prep:** [.claude/design/blueprint_full_feature_set_research.md](../../.claude/design/blueprint_full_feature_set_research.md) — read TL;DR (§0), then §6 (7 open decision points)
  - **Pre-discussion reading:** `.claude/design/spaces/BLUEPRINT.md` (~5 min) + `.claude/knowledge/blueprint_architect_ux_spec.md` (~10 min) + research doc §6 (~10 min)

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
| Phase 30 | Agent infra + deployment hardening | 2026-05-05 | commits `891f157`, `2dcd1c2` |
| Phase 31 | Sidebar Slot Registry (ADR-073) + Diagnostic Error Discipline (ADR-078) + Blueprint schema (ADR-075) + ADR-076 flag (ADR-077) | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |
| Phase 32 / May-09 hygiene | Export enhancements (EXPORT-2/3/4), UX-NOTIF-2, ADR-076 MVP-1 complete, BP-COLOR-1/2/3, all Open Issues + CSS batch | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |

---

## Archive Pointers

- [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) — Phase 31 + 32: all ADR-076 MVP-1, EXPORT-2/3/4, UX-NOTIF-2, CSS hygiene, Open Issues Export/Session/UX/Sidebar batch, Blueprint IDE Forms batch (BP-COLOR-1/2/3)
- [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) — Wave 1 remediation + Phase 22 bug resolutions
- [tasks_archive_2026-04-14.md](archives/tasks_archive_2026-04-14.md) — Phase 21-C–I, IU-1–7
- [tasks_archive_2026-04-10.md](archives/tasks_archive_2026-04-10.md) — Phases 16–18, 21-A–B
- [tasks_archive_phase14.md](archives/tasks_archive_phase14.md)
- [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) — Phases 23-A/B + 24
- [tasks_archive_phase25.md](archives/tasks_archive_phase25.md) — Phase 25 (A–O)
- [tasks_archive_documentation.md](archives/tasks_archive_documentation.md)
- [tasks_archive_infrastructure.md](archives/tasks_archive_infrastructure.md)
- [tasks_archive_integration_qa.md](archives/tasks_archive_integration_qa.md)
- [tasks_archive_viz_factory.md](archives/tasks_archive_viz_factory.md)
- [tasks_test_ui_current.md](tasks_test_ui_current.md) — current UI test checklist
