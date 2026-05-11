# Tasks Archive — 2026-05-11

Completed items moved from `tasks.md` on 2026-05-11 cleanup. All items verified `[x]` before archival.

---

## Audit Fixes — Documentation (2026-05-09)

*Findings from `audit_documentation_2026-05-09_*.md` — all resolved in-session 2026-05-09.*

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

---

## Audit Fixes — ADR Compliance (2026-05-09)

*Findings from `audit_adr_compliance_2026-05-09.md` (Routine 18).*

- [x] **ADR-078-ACTIONS-1** `[AUDIT]` `[sonnet/medium]`: Retrofit `TransformationError` into transformer actions that silently pass through on invalid input. Fixed 24 silent `return lf` pass-throughs across `expressions.py`, `analytical.py`, and `advanced.py`. (Note: the audit report incorrectly named the error class `SPARMVET_DiagnosticError` — actual class is `TransformationError` from `utils.errors`.)

- [x] **TRANSFORMER-SUITE-FIX** `[sonnet/medium]`: Fixed transformer integrity suite failing 60/60 after ADR-078 fix. Root cause: `debug_wrangler.py` and `debug_assembler.py` used `ConfigManager` unconditionally, which enforces `analysis_groups:` presence (a full-pipeline requirement). Standalone wrangling test manifests don't have `analysis_groups:`, so validation fired before any test ran. Fix: bypass `ConfigManager` for manifests without `analysis_groups:`, use `yaml.safe_load()` directly instead. Also fixed missing `--data` argument in the suite's `subprocess` call to `debug_wrangler.py`. Result: 62/62 clean (60 wrangler PASSED, relational_audit PASSED).

---

## Audit Fixes — Library Tests & Dependencies (2026-05-09)

*Findings from `audit_library_tests_2026-05-09.md` (Routine 10) and `audit_package_deps_2026-05-09.md` (Routine 11).*

- [x] **LIB-TESTS-BLUEPRINT-1** `[AUDIT]` `[sonnet/medium]`: ✅ Fixed 188 pytest failures in `libs/blueprint_arch/tests/test_schema_registry.py` (194 total tests now pass). Root cause: test file was importing `AVAILABLE_WRANGLING_ACTIONS` (function dict) instead of `ACTION_SCHEMAS` (schema dict). Changed imports and `register()` call in test file. All 58 action catalog tests + 36 component catalog tests + semantic rules / filtering / search tests now pass.

- [x] **LIB-TESTS-VIZ-TIMEOUT-1** `[AUDIT]` `[haiku/low]`: ✅ Increased `TIMEOUT_SECONDS` in `scripts/audit_library_tests.py` from 120 → 300 (5 min) to allow viz_factory integrity suite (193+ components) to complete.

- [x] **PKG-PLOTNINE-PATCH-1** `[AUDIT]` `[haiku/low]`: ✅ Upgraded plotnine 0.15.3 → 0.15.4 and pinned version in pyproject.toml (>=0.15.4,<0.16.0). Re-ran parity audit: 222 plotnine symbols, 168 registered (75% coverage). Identified new components in 0.15.4 (geom_bin2d, stat_bin2d, stat_pointdensity) — registration deferred to BP-ACTION-PARITY-1. No breaking changes affecting current registrations.

- [x] **PKG-IMPORTLIB-MAJOR-1** `[AUDIT]` `[sonnet/low]`: ✅ Investigated importlib_metadata 9.0.0 MAJOR upgrade. Found: transitive dependency via shiny → opentelemetry-api 1.41.1. opentelemetry-api 1.41.1 requires importlib-metadata<8.8.0, so upgrade to 9.0.0 is BREAKING. Solution: Pinned importlib_metadata to >=6.0,<9.0.0 in pyproject.toml. Verified with `pip check` — no broken requirements.

---

## Runtime Error Discipline (ADR-079 design phase)

- [x] **DIAG-RUNTIME-ADR** `[opus/high]`: ✅ ADR-079 authored 2026-05-10 (replaces placeholder). Decisions: `PipelineError` sits alongside `DeploymentError` (shared 5-field shape, no inheritance); render surface is per-category (`plot_overlay`/`notification`/`audit_panel`/`data_import_panel`/`blueprint_inline`); `evidence` dict carries sample rows + offending values + schema diff (5-row / 50-col cap); audit-trail capture via new `session_pipeline_errors` reactive value, written to `report.qmd` "Pipeline Issues During Session" section and into T3 Ghost. Audience model adds `analyst` / `data_provider` / `manifest_author` to ADR-078's `operator` / `developer`.

---

## Blueprint Architect

- [x] **BP-DEBUG-1** `[sonnet/high]`: Full Blueprint Architect debug pass — field contracts rendering, lineage rail accuracy, Zone C layout stability. ✅ Committed ee05ea0.
  - [x] Fixed `architect_active_plot` — now resolves plot specs from `analysis_groups` for pipeline manifests (was silently returning None since ADR-043). Builds synthetic flat manifest before `VizFactory.render()` call.
  - [x] Fixed 8 emoji violations in `blueprint_handlers.py` `print()` calls (`rules_code_quality.md §1`).
  - [x] Zone C layout stability reviewed — `bp_action_form_ui` 4-way dependency is intentional, no Rule R4 violation. `ui.js_eval` click-simulation in `handle_lineage_node_click` (wrangle_studio.py:1207) is fragile UX but not a crash risk; tracked as BP-LINEAGE-NAV-1.

- [x] **BP-ACTION-PARITY-1** `[sonnet/medium]`: Expose `@register_action` entries in Blueprint IDE UI (18-F). ✅ Committed acb27ce. Added search + context filter to action picker; choices grouped into "Rich form" (19 with ui_schema) and "YAML fallback" (43 without); reactive via `_update_action_picker()` effect.

- [x] **BP-FIELD-GAP-1** `[sonnet/medium]`: Field Gap Analysis tool — field name → walk lineage to earliest insertion point. ✅ Committed c41488c. Input + Find button added to Interface tab; field_gap_ui checks active_upstream/downstream and provides Rail navigation hints when field not found at current tier.

- [x] **BP-FWD-HINT-1** `[sonnet/medium]`: Forward propagation hint — show which output_fields / final_contract files need updating when a field is added or renamed. ✅ Committed 29300a2. Integrated into field_gap_ui: scans downstream chain nodes for explicit output_fields contracts that exclude the queried field; inline contracts checked directly, file-linked ones emit manual-verify warning.

---

## Gallery & Visualization

- [x] **VIZ-DISCRETE-SCALE-1** `[sonnet/low]`: ✅ Audited all pipeline plot specs. Added `scale_x_discrete` to 3 specs missing it (`MLST_counts_bar.yaml`, `abromics_st_by_country`, `abromics_st_by_source`). 2_test_data_ST22_dummy plots already correct; `year_distribution.yaml` intentionally keeps `scale_x_continuous` (year is numeric).

- [x] **VIZ-GALLERY-THUMB-1** `[sonnet/low]`: ✅ `generate_previews.py` now saves `preview_thumb.png` (100px wide, aspect-ratio preserved, LANCZOS) after each full preview render. Handles thumb-only generation from existing full plots. `gallery_manager.py` adds `has_thumb` + `has_preview` fields to index registry. Pre-generated 32 thumbs for existing recipes.

---

## Infrastructure & Housekeeping

- [x] **TECH-DEBUG-MATERIALIZE-1** `[haiku/low]`: ✅ `debug_wrangler.py` and `debug_assembler.py` already had dated `tmpAI/{date}/{lineage}/` defaults. Fixed `debug_gallery.py` which still defaulted to fixed `tmp/` paths — now all three scripts share the same dated-path convention.

---

## Design Decisions (Needs Discussion → resolved)

- [x] **VIZFAC-PLOT-CASCADE-1** `[opus/high]` `[design-thinking]`: ✅ Design spec authored 2026-05-10 at [.claude/design/plot_config_cascade.md](../../design/plot_config_cascade.md). Five-tier cascade L5(T3 override) > L4(spec) > L3(optimisation) > L2(plot_defaults) > L1(built-ins) resolved at one merge point via new `resolve_plot_config()` pure function. Closes the silent gap where T3 `aesthetic_override` nodes are recorded/exported but never rendered. Locks `plot_defaults:` schema (§7a) and reserves L3 hooks (§5c) for future optimisation heuristics. Six concrete implementation tasks emitted (VIZFAC-RESOLVER-1 through VIZFAC-BLUEPRINT-FORM-1).

---

## T3 Threading & Repo Hygiene (2026-05-11)

- [x] **TECH-T3-THREAD-1** `[sonnet/medium]`: `t3_plot_overrides` (aesthetic override state) now collected and included in export bundle: `t3_steps.yaml` gains `t3_aesthetic_overrides:` key; `_build_methods_section()` extended with aesthetic override prose; design doc updated. Rendering gap (L5 cascade) blocked by VIZFAC-RESOLVER-1 and tracked as VIZFAC-T3-OVERRIDE-1.

- [x] **PYPROJECT-DEPS-1** `[haiku/low]` `[repo-hygiene]`: All libs that import utils (`blueprint_arch`, `connector`, `transformer`, `viz_factory`) already declare `"libs/utils"` in their `pyproject.toml`. `ingestion`, `test_lab`, `viz_gallery` have zero utils imports — no changes needed.

---

## Runtime Error Discipline — DIAG-RUNTIME-BASE-1 (2026-05-11)

- [x] **DIAG-RUNTIME-BASE-1** `[sonnet/medium]`: Phase 1 complete. `libs/utils/src/utils/pipeline_error.py` (PipelineError dataclass + format/to_audit_row/with_timestamp + make_render_payload + _format_evidence_md); `app/src/render/pipeline_error_renderers.py` (5 surface renderers + dispatch_pipeline_error); `libs/utils/tests/test_pipeline_error.py` (55/55 tests pass). **Unblocks all DIAG-RUNTIME-* Phase 2 retrofits.**

---

## Blueprint Architect — BP-LINEAGE-NAV-1 (2026-05-11)

- [x] **BP-LINEAGE-NAV-1** `[sonnet/medium]`: Replace `ui.js_eval("document.getElementById('btn_import_manifest').click()")` in `handle_lineage_node_click` with a shared `reactive.Value(selected_lineage_rel)` that both lineage rail clicks and the Import button write to; a single `@reactive.Effect` watches it and calls `_do_load_component()` directly. Eliminates race condition and DOM-dependency. **DONE 2026-05-11**
  - `app/modules/wrangle_studio.py` — replaced js_eval with `selected_lineage_rel.set(rel)`; added `selected_lineage_rel=None` param to `define_server()`
  - `app/handlers/blueprint_handlers.py` — `_handle_manifest_import` writes to signal; new `_load_component_from_selection` is sole `_do_load_component()` call site, watching `@reactive.event(selected_lineage_rel)`
  - `app/src/server.py` — declared `_selected_lineage_rel = reactive.Value(None)`; passed to both handlers; `@deps` updated

---

## Gallery — GALLERY-CLONE-DECOUPLE-1 (2026-05-11)

- [x] **GALLERY-CLONE-DECOUPLE-1** `[sonnet/high]`: Decoupled gallery clone from WrangleStudio. Fixed both bugs: (1) `WrangleStudio` now gated on `developer_mode_enabled` in `server.py` (ADR-071 positive inclusion); (2) clone replaced with T3 transplant — inserts `developer_raw_yaml` RecipeNode into `home_state._pending_t3_nodes`, gated on `t3_sandbox_enabled`. Removed `wrangle_studio` kwarg from `gallery_handlers.define_server()`. App import clean for both developer and project-independent personas. 97 fast tests pass. **Unblocks:** 22-J-10 (aesthetic propagation).

---

## VizFactory Cascade — VIZFAC-RESOLVER-1 (2026-05-11)

- [x] **VIZFAC-RESOLVER-1** `[sonnet/high]`: Created `libs/viz_factory/src/viz_factory/plot_config_resolver.py` — `resolve_plot_config()`, `compute_optimisation_layer()`, `_dedupe_layers()`, `_normalise_spec()`, `_BUILTIN_DEFAULTS`. Pure functions, no plotnine import. 75 unit tests in `libs/viz_factory/tests/test_plot_config_resolver.py` — all pass. Full cascade truth table (L1→L5 theme/palette provenance, L3 axis-text emit + L4 dedup suppression, L5 mutex warn, geom accumulation, layer dedup). **Unblocks:** VIZFAC-RENDER-WIRE-1, VIZFAC-DEFAULTS-DOCS-1.

---

## VizFactory Cascade — VIZFAC-DEFAULTS-DOCS-1 (2026-05-11)

- [x] **VIZFAC-DEFAULTS-DOCS-1** `[sonnet/low]`: Documented `plot_defaults:` allowed keys (design §7a) across three files:
  - `rules_manifest_structure.md §10` — expanded from `{palette, theme}` stubs to full schema: `palette`, `theme`, `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation{auto_axis_text, density_jitter, panel_spacing, legend_ncol}`. Removed VIZFAC-DEFAULTS-DOCS-1 placeholder note. Added §10a/§10b/§10c sub-headings.
  - `rules_viz_factory.md §6b` — added cross-reference to `rules_manifest_structure.md §10` for full schema; noted unknown-key PipelineError. Updated §7 implementation task list (struck through completed tasks).
  - `docs/appendix/manifest_structure.yaml` `plot_defaults_block` — expanded comment to reference cascade + unknown-key warning; added all §7a keys with inline comments. **Unblocks:** VIZFAC-BLUEPRINT-FORM-1.

---

## VizFactory Cascade — VIZFAC-RENDER-WIRE-1 (2026-05-11)

- [x] **VIZFAC-RENDER-WIRE-1** `[sonnet/medium]`: Refactored `VizFactory.render()` to use `resolve_plot_config()` as the single merge point for the five-tier cascade (VIZFAC-PLOT-CASCADE-1).
  - **Files changed:** `libs/viz_factory/src/viz_factory/viz_factory.py`
  - **What changed:** render() now calls `resolve_plot_config(raw_spec, plot_defaults, df_pandas)` after filter pushdown and a single `df.collect().to_pandas()` call. Walks `resolved["layers"]` to apply components; batches `element_text` layers into one `theme()` call. Derives `has_fill_scale`/`has_color_scale` from `resolved["palette_scope"]`. Emits print warnings (ADR-079 marker) for `_unknown_plot_defaults_keys` and `_l5_mutex_warn`.
  - **Removed from render() path:** `_standardize_config()`, separate theme/coord/facet injection guards, `_auto_adjust_axis_labels()` (all now handled by `_normalise_spec()` + `compute_optimisation_layer()` in the resolver). Methods kept as private deprecated members.
  - **New import:** `from viz_factory.plot_config_resolver import resolve_plot_config`
  - **Verification:** 195/195 viz_factory tests pass; 97/97 fast regression baseline green.
  - **Unblocks:** VIZFAC-T3-OVERRIDE-1 (L5 aesthetic_override now flows through resolved["layers"]).

---

## ADR-079 Phase 2 — DIAG-RUNTIME-ASSEMBLER-1 (2026-05-11)

- [x] **DIAG-RUNTIME-ASSEMBLER-1** `[sonnet/medium]`: Retrofitted `libs/transformer/src/transformer/data_assembler.py` with structured PipelineError diagnostics (ADR-079 Phase 2).
  - **Files changed:** `libs/transformer/src/transformer/data_assembler.py`
  - **What changed:** All 4 error paths converted from bare `ValueError`/`print`+`continue` to `PipelineError` + `raise TransformationError`:
    1. No recipe / no ingredients: `ValueError` → `PipelineError(category="assembly", who="manifest_author") + TransformationError`
    2. Missing `right_ingredient`: `ValueError` → structured PipelineError with available ingredient list
    3. Missing join key: was `print("WARNING...") + continue` (silent skip, bad data produced) → now `PipelineError + raise TransformationError` (behavior fix — no longer silently skips!)
    4. Action execution: wrapped `get_action_function()` + `action_func()` in try/except catching `ValueError`, `ColumnNotFoundError`, `SchemaError`, generic `Exception` → PipelineError + TransformationError for each
  - **New imports:** `from utils.pipeline_error import PipelineError` (already had `TransformationError`)
  - **Updated `@deps` block:** added `pipeline_error.py` to `consumes:`
  - **Verification:** 168/168 transformer tests pass.
  - **Key behavior fix:** Missing join key previously silently continued with no error (wrong data produced). Now raises immediately with a diagnostic that identifies the affected step and available keys.

---

## ADR-079 Phase 2 — DIAG-RUNTIME-WRANGLER-1 (2026-05-11)

- [x] **DIAG-RUNTIME-WRANGLER-1** `[sonnet/medium]`: Retrofitted `libs/transformer/src/transformer/data_wrangler.py` with structured PipelineError diagnostics (ADR-079 Phase 2).
  - **Files changed:** `libs/transformer/src/transformer/data_wrangler.py`
  - **What changed:**
    1. Added `from utils.pipeline_error import PipelineError` import
    2. Updated `@deps` block to document `pipeline_error.py` dependency
    3. Changed `for rule in wrangling_rules:` → `for step_idx, rule in enumerate(wrangling_rules):` for step-level location reporting in PipelineError
    4. Missing `action` key: `raise ValueError` → `PipelineError(category="wrangling") + raise TransformationError` with `evidence={"step_keys": str(list(rule.keys()))}`
    5. Missing columns: upgraded existing bare `TransformationError` to emit `PipelineError` first with full evidence dict (`missing_columns`, `near_match`, `available_columns[:20]`)
    6. Unregistered action: `ValueError` from registry → `PipelineError + raise TransformationError from exc`
    7. `action_func()` execution: try/except for `ColumnNotFoundError` and generic `Exception` → PipelineError + TransformationError for each
  - **Verification:** 168/168 transformer tests pass.
  - **Unblocks:** DIAG-RUNTIME-AUDIT-1 (Phase 3 — UI sink for structured errors).
