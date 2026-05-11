# Implementation Plan Master: Dashboard Core & Plugin Validation

## Authority: @dasharch

## Source of Truth for SPARMVET_VIZ Architecture

## 1. Overview & Vision

Transition from "Scaffolding" to "Functional Prototype" by implementing missing transformer logic and validating it via the modular Shiny frontend. We utilize a **'Decorator-First'** development cycle to align the Python execution engine with the active YAML manifest logic verified in `./config/manifests/pipelines/`.

#### 🟢 Phase 19: Unified Manifest Standard & Hygiene (ADR-041) — COMPLETED 2026-04-20

- [x] **Formal ADR-041**: Registered the "Keyed Schema / Ordered Logic" hybrid standard.
- [x] **Standard Documentation**: Created `config/manifests/README.md` and updated `project_conventions.md`.
- [x] **Schema Normalization**: Converted legacy simple dicts and redundant fragments to **Rich Dictionary** standard.
- [x] **Wrangling Tiering**: Verified that all pipeline fragments adopt the `tier1`/`tier2` list structure.
- [x] **Fragment Flatness**: Stripped top-level anchoring keys from included files for recursive compatibility.

#### 🟢 Phase 20: Relational Manifest Stress Testing (COMPLETED 2026-03-07)

- [x] **Relational Audit**: Executed `debug_assembler.py` against the ST22 manifest.
- [x] **Resilience Hardening**: Fixed 'bool' attribute error in `DataAssembler` and `DataWrangler`.
- [x] **Contract Validation**: Unified Contract Guard projection to handle `original_name` mappings.
- [x] **Full Pipeline Pass**: Verified all 3 major assemblies materiality (Anchor, AR1, Summary).

---

**STATUS:** Manifest Structural Integrity Restored. 🏗️💎

## 2. Architectural Principles

- **Decorator-First:** Explicit decorator patterns for both Wrangling actions (`@register_action`) and Plotting factories (`@register_plot`).
- **YAML Data Contract:** Pursue **YAML-ONLY** validation. Phase out JSON schema dependencies for the core manifest logic.
- **Polars-First:** Mandatory use of **Polars LazyFrames** for all heavy lifting. Materialize only at the Presentation or Export layers.
- **Tidy Data Consistency:** Use **Plotnine** for the Presentation Layer to ensure seamless handoff from Polars-transformed dataframes.

## 3. Environment & Modular Standards

- **Root .venv:** All execution MUST occur within the root `.venv/` directory.
- **Modular package architecture:**
  - Each subdirectory in `libs/` (e.g., `libs/transformer`, `libs/viz_factory`) MUST be an independent package with its own `pyproject.toml`.
  - Installation in the root `.venv` MUST use the `-e` (editable) flag to maintain modularity and live-syncing of code changes.
- **CLI-argparse for Testing:** Every library in `libs/` must include a CLI-compatible test script. Hardcoded paths inside test logic are forbidden. Use `argparse` to handle data inputs (TSV), configuration manifests (YAML), and output destinations.

## 4. Technical Roadmap

### Phase A: 'Decorator-First' Logic (DONE)

- [x] Verify status of decorator-based plugin system.
- [x] Implement missing decorator-based actions (drop_duplicates, summarize).
- [x] Update ResFinder_wrangling.yaml.

### Phase B: Dynamic Plot Factory (DONE)

- [x] Implement `@register_plot(factory_id)` decorator in `libs/viz_factory/src/registry.py`.
- [x] Refactor `base.py` to replace Plotly placeholders with Plotnine templates.
- [x] Prototype Polars-to-Plotnine handoff. (ADR-010) [DONE]

### Phase 3: Atomic Layer Optimization (DONE)

- [x] **Decorator Expansion:** Implement `regex_extract`, `drop_columns`, `round_numeric`, and `filter_range`.
- [x] **M2 (Layer 1 Verification):** Universal Runner (`wrangler_debug.py`) and Automated Suite (`debug_decorator_suite.py`) verified against 17 atomic actions. [COMPLETED] 🚀
- [x] **Universal Runner Callability:** Confirm `wrangler_debug.py` can be imported as a library by the Orchestrator.
- [x] **Lazy Processing Audit:** Ensure atomic actions do not trigger premature Polars collection.

### Phase 4: The Assembly Factory (DONE)

- [x] **DataAssembler Core:** Implement Layer 2 orchestrator script.
- [x] **Multi-Source Loop:** Call the Wrangler for all datasets defined in the manifest.
- [x] **Cross-Dataset Joins:** Execute Polars `.join()` logic using manifest-defined `join_on`.
- [x] **Final Stage Wrangling:** Support a global wrangling pass across the joined LazyFrame.
- [x] **Relational Decorators:** Registered `join` and `join_filter` in the unified registry.

### Phase 5: Architectural Guardrails & Integration (DONE)

- [x] Implement **`libs/utils/src/data_executor.py`** to center the `.collect()` logic for the Orchestrator. [DONE]
- [x] Finalize YAML-only validation logic. [DONE]
- [x] Implement responsive UI adjustments for premium branding.

### Phase 6: Viz Factory Components [DONE]

- [x] Initialize library and `@register_plot_component` registry.
- [x] Implement core `geoms/`, `facets/`, `coords/`, `positions/` subdirectories.
- [x] Fully implement and verify `scales/` and `themes/` components with verification PNGs (35 components/86% verified).
- [x] Create `bulk_test_runner.py` for automated manifest-to-PNG generation/verification.
- [x] Resolve failed verifications (scale_color_cmap, facet_labeller, stat_ecdf, stat_function).
- [x] Implement "Filter vs. Anchor" reactivity logic (ADR-024).

### Phase 7: Orchestration Guardrails (DONE)

- [x] Implement **`libs/utils/src/data_executor.py`** to center the `.collect()` logic for the Orchestrator.
- [x] Finalize YAML-only validation logic.
- [x] Implement responsive UI adjustments for premium branding.

### Phase 8: Frontend Scaffolding (UI Heartbeat) (DONE)

- [x] **Asset Integration:** Materialized via `Bootloader` (ADR-031).
- [x] **UI Implementation (`app/src/ui.py`):** Sidebar for project/manifest discovery.
- [x] **Server Implementation (`app/src/server.py`):** Orchestrator materialization.

### Phase 9: Triple-Source AMR Integration (DONE)

- [x] **fg_metadata/phenotypes/genotypes** migration and normalization. [DONE]
- [x] **3-Way Assembly**: figshare_integration.yaml. [DONE]
- [x] **Integration Plots**: Verified via 1:1:1 evidence loop. [DONE]

### Phase 9-B: The Artist (Visual Pipeline Builder SDK) (DONE)

- [x] **Registry Initialization:** Established `@register_plot_component` in `libs/viz_factory`.
- [x] **Modular SDK:** Confirmed `generator_utils` autonomy and `AquaSynthesizer` logic.
- [x] **Visual Builder Core:** Implemented `WrangleStudio` manual node stack. [DONE]

### Phase 10: The Persistence & Tiering Layer (DONE)

- [x] **Implementation of ADR-024:** Integrate `pl.sink_parquet` into `DataAssembler`. [DONE]
- [x] **Checkpoint Logic:** Add a "Short-Circuit" to the Transformer to detect existing Parquet anchors.
  - [x] **Automated Freshness Check:** Implemented `mtime` comparison between manifest directory and parquet to invalidate stale caches. [DONE] (Phase 14 refinement)
- [x] **Tier 2 Summarizer:** Implement `@register_action("summarize")` for row reduction. [DONE]

## 5. Governing Authority (Authority Matrix)

This implementation plan is governed by the authoritative rulebooks and architectural decisions located in the project root. Refer to these files for the "How" and "Why" of any component implementation:

### Phase 19: Unified Manifest Standard & Hygiene (ADR-041) ✅ COMPLETED 2026-04-20

**Objective:** Standardize manifest structures to resolve the disconnect between UI contract viewers and backend data engines.

- [x] **ADR-041 Registration:** Formally document the "Keyed-Schema & Ordered-Logic" standard.
- [x] **Rules Synchronization:** Update `rules_data_engine.md` and `rules_manifest_structure.md`.
- [x] **Project Conventions Update:** Document the "Adequate Dictionary" format and fragment flatness.
- [x] **Manifest README:** Create `config/manifests/README.md` for associated documentation.
- [x] **Structural Hygiene:**
  - [x] Move all `input_fields` and `output_fields` to Rich Dictionary format.
  - [x] Ensure all `wrangling` blocks use mandatory tier nesting (`tier1`, `tier2`) as sequential lists.
  - [x] Remove redundant top-level keys from included `.yaml` fragments.
- [x] **Engine Alignment**: Verified that `DataIngestor` and `DataWrangler` are compatible with the Keyed Dict / Sequential List hybrid.

- **Verification & Testing Protocol**: [.claude/rules/rules_verification_testing.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/rules_verification_testing.md)
- **Architectural Decisions (ADR)**: [.claude/knowledge/architecture_decisions.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/architecture_decisions.md)
- **Data Engine Standards**: [.claude/rules/rules_data_engine.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/rules_data_engine.md)
- **Workspace Master Index**: [./.claude/rules/workspace_standard.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/workspace_standard.md)

---

### Phase 11: UI Persona & Reactive Integration (ADR-026/ADR-024)

> **Numbering note (2026-04-30):** Phase 11-B and Phases 13–15 are absent from this plan. These are historical gaps — the work was done but tracked directly in git commits and ADRs rather than this document. The plan numbering is non-sequential by design at those points, not missing work.

### Phase 11-A: Pipeline Demo Implementation (DONE)

- [x] **UI Bootloader**: Implement `ui_config.yaml` for Persona masking. [DONE]
- [x] **Dual-View Scaffolding**: Create `ui.navset_tab` with Tab A (Tier 2 Reference) and Tab B (Tier 3 Active). [DONE]
- [x] **Tier 3 Sidebar Connector**: Link Shiny inputs to `VizFactory` filters. [DONE]
- [ ] **Annotation Modal**: Implement mandatory 'User Note' popup. (ACTIVE)

### Phase 11-C: UI Shell & Module Integration (DONE)

- [x] **Persona Bootloader**: Implement `app/src/bootloader.py`.
- [x] **Library Hook-up**: Absolute imports of `libs/` packages into `app/modules/`.
- [x] **Shell Layout**: Build the 3-zone layout (Navigation, Theater, Audit Stack).

### Phase 11-D: Dynamic Discovery & Interaction (DONE)

- [x] **Discovery Engine:** Implement manifest-to-tab and Polars-schema-to-filter logic.
- [x] **Interactivity:** Build the column-picker and collapsible sidebars.

### Phase 11-E: Ingestion, Persistence & Gallery (ACTIVE)

- [x] **External Ingestion:** Build the YAML upload and Excel-to-TSV helper. [DONE]
- [x] **Ghost Saving:** Implement automatic background manifest versioning. [DONE]
- [ ] **Gallery Engine**: Build UI browser pointing to Connector Location 5.
- [x] **Join Preview Modal**: Implement PK validation check in WrangleStudio (ADR-012). [DONE]

### Phase 11-F: Ingestion, Persistence & Developer Studio (ACTIVE)

- [x] **Path Authority Engine:** [DONE]
- [x] **Library Internalization:** [DONE]
- [x] **WrangleStudio Core:** Visual chaining of Transformer nodes. [DONE]
- [x] **Synthetic Data GUI:** Wrapper for AquaSynthesizer. [DONE]
- [ ] **Outlier "Brush" Integration:** Map plot selection to Tier 1 Anchor data lookup.

## Phase 12: UI Orchestration & Aesthetics (ADR-027)

*IMPORTANT: The specific layout configurations, sandbox gating logic, and persona mappings are defined authoritatively in `[ui_implementation_contract.md](../../.claude/rules/ui_implementation_contract.md)`. This section serves only as an implementation tracker.*

### Phase 12-A: Comparison Theater & Persona Scaffolding (DONE)

- [x] **Comparison Theater Base**: Dual-column layout setup. [DONE]
- [x] **True 3-Column Navigation Shell (ADR-029a)**: Nested `layout_sidebar` structure with Left (Navigator), Center (Theater), and Right (Audit). [DONE]
- [x] **Dynamic Layout Grid**: Implement logic to shift between grid modes and handle maximized panes. [DONE]
- [x] **Analysis Theater Tabs**: Materialize manifest groups into dynamic tabsets with integrated controls. [DONE]
- [x] **Persona Reactivity Matrix Enforcement**: Link `app/src/ui.py` strictly to persona-based masking. [DONE]
- [x] **Visual vs Functional Pickers**: Connected schema pickers and column visibility controls. [DONE]

### Phase 12-B: Position-Aware Sandbox & Controls

- [ ] **Bifurcated Tier 3 (`t3_recipe`)**: Implement the distinction between `t3_recipe_prefill` (wide format exploration prior to blueprint steps) and `t3_recipe_complete` (final plot data including T2 blueprint).
- [ ] **Single Audit Stack**: Pre-fill with *Violet* properties, append *Yellow* properties. Position dictates execution order relative to the blueprint.
- [ ] **Validation & Revert Protocol**: Add `btn_revert` to wipe the user sandbox and reset to the unmodified T2 blueprint. Implement disable toggles and deletion warnings.
- [ ] **Comment Gatekeeper**: Tie `btn_apply` to validation of `comment_fields` across all active yellow/modified nodes.

### Phase 12-C: Headless UI Manifest Verification

- [ ] **Persona Gating Tests**: Implement headless test strategies (e.g., Shiny testing addons like `pytest-playwright`) to verify each persona's UI masking element by element, locking to one persona at a time per test suite.

### Phase 16: Gallery Taxonomy & Scaling (DONE 2026-04-19)

- [x] **Metadata indexing**: `gallery_index.json` pivot generation (ADR-037).
- [x] **UI Integration**: Split-pane viewer with isolated reactivity.
- [x] **Ergonomic Polish**: Promoted selector to top of sidebar, added Play-style Apply button.

## Phase 17: Contextual UI Masking & Focus Mode (DONE 2026-04-19)

- [x] **Contextual Masking (ADR-038)**: Implemented server-side reactive reification to hide Global Sidebar controls.
- [x] **Clone Post-Action**: Implemented automatic tab switching / Home signaling after recipe cloning.
- [x] **State Restoration**: Hardened session resume while in Gallery mode.

## Phase 18: Blueprint Architect — Bidirectional Lineage Navigation (ACTIVE)

Full design rationale in ADR-040 (`architecture_decisions.md`). Replaces the flat Interface (Fields) tab with a Bidirectional Lineage Rail + 3-column contract viewer.

### Phase 18-A: Field Materialization & Context Map ✅ COMPLETED 2026-04-20

- [x] `_build_sibling_map()` — file-path index with role, schema_id, siblings, ingredients.
- [x] `_build_schema_registry()` — schema-ID index capturing `!include` refs and inline YAML.
- [x] `_build_lineage_chain()` — ordered Rail node list for any selected component.
- [x] `_load_fields_file()` — ADR-014-aware field file reader.
- [x] `_component_ctx_map`, `_includes_map`, `_schema_registry` reactive values.
- [x] `normalize_manifest_fields.py` moved to `app/assets/` with importable API; `btn_normalize_fields` handler.
- [x] `_parse_fields_safe` handles rich `{col: {type, label}}` dict format.

### Phase 18-B: Lineage Rail UI ✅ COMPLETED 2026-04-20

- [x] `_build_lineage_chain()` helper — walks backward then forward through sibling map.
- [x] `active_lineage_chain` reactive populated on every component load.
- [x] `lineage_rail_ui` renders clickable `<button>` chain with role icons and active highlighting.
- [x] JS Rail node clicks set hidden `lineage_node_rel` input → `handle_lineage_node_click` effect.
- [x] **Rail node click full load**: `handle_lineage_node_click` triggers `btn_import_manifest` via `ui.js_eval`. Rail fully navigable.
- [ ] **Plot spec chain enrichment**: Prepend assembly node to plot_spec chain using `target_dataset`. *(DEFERRED)*
- [ ] **Branch selector**: One assembly → N plots; show branch tabs on Rail. *(DEFERRED)*

### Phase 18-B-fixes: Live Testing Fixes ✅ COMPLETED 2026-04-20 (Session 2)

- [x] **Sidebar display labels**: `_update_dataset_pipelines` shows `"{schema_id} — {role}"` instead of raw filenames.
- [x] **Plot spec upstream resolution**: `target_dataset` lookup broadened — covers `data_schemas` entries, not only `assembly_manifests`.
- [x] **Live View plot preview**: `active_manifest_path` reactive added; `architect_active_plot` uses full `ConfigManager` config; `active_viz_id` set on plot_spec load.
- [x] **TubeMap node click → full load**: `_sync_selector_from_node_click` fires `btn_import_manifest` via `ui.js_eval`.

### Phase 18-C: 3-Column Interface Panel ✅ COMPLETED 2026-04-20

- [x] Tab-3 rewritten: hidden `lineage_node_rel` input + `lineage_rail_ui` header + 3-column `layout_columns([4,4,4])`.
- [x] 7 new render outputs: `lineage_rail_ui`, `upstream_label_ui`, `lineage_upstream_ui`, `component_label_ui`, `lineage_component_ui`, `downstream_label_ui`, `lineage_downstream_ui`.
- [x] `_handle_manifest_import` full role dispatch: `input_fields`, `output_fields`, `wrangling`, `assembly`, `plot_spec`.
- [x] `wrangle_studio.define_server()` call extended with `get_schema_registry` and `get_includes_map` lambdas.

### Phase 18-D: Per-Plot Wrangling Support *(PENDING)*

- [ ] `pre_plot_wrangling` optional key in plot block (`!include` path).
- [ ] Lineage Rail shows intermediate node between assembly output and plot spec.
- [ ] "➕ Add plot wrangling" affordance when slot is absent.

### Phase 18-E: Reverse Navigation — Field Gap Analysis *(PENDING)*

- [ ] Enter desired field name → walk lineage backwards → show earliest insertion point.
- [ ] Highlight which `output_fields` and `final_contract` files need updating to carry the field forward.

### Phase 18-F: Full Interactive TubeMap (ADR-039) *(PARTIALLY COMPLETE)*

- [x] Clickable Cytoscape DAG nodes driving the Lineage Rail — **DONE** (implemented with Cytoscape + dagre, not Mermaid/SVG; `cy_tubemap` canvas, `initCyTubeMap` JS, node tap → lineage rail update).
- [ ] Action Registry parity in IDE forms — form UI infrastructure is done (`schema_registry.py`, `_render_action_form`, `bp_action_form_ui`); only ~20 of 65 registered actions have `ui_schema` metadata. Remaining ~45 actions need `ui_schema` added to their `@register_action` decorator before they appear in the Blueprint form picker.
- [x] Visual Forking: select node → initiate new branch → produce YAML additions. **DONE** (BP-VISUAL-FORK-1, 2026-05-11 — `generate_fork_yaml()` in `manifest_navigator.py`; fork UI in `blueprint_handlers.py`; "Fork Node" card in Blueprint right sidebar; gated on `manifest_edit_enabled`).

---

## Phase 21: Unified Home Theater (ADR-043 / ADR-044) ✅ COMPLETED 2026-04-30

**Objective:** Eliminate the redundant "Analysis Theater / Viz" nav mode, merge all results functionality into a single unified **Home** mode, implement persona-gated tier controls, context-reactive left sidebar filters, and right sidebar suppression for lower personas.

**Governing ADRs:** ADR-043 (Unified Home Theater), ADR-044 (Persona-Gated Audit Stack & Right Sidebar Visibility), ADR-047 (Export Bundle).

### Phase 21-A: Nav & Routing Simplification ✅ COMPLETED 2026-04-23

- [x] Removed `"Viz"` / `"Analysis Theater"` branch and nav item.
- [x] Removed `theater_state`, `btn_max_*`, `is_triple`/`triple_tier_mode`.

### Phase 21-B: Manifest-Driven Tab Structure ✅ COMPLETED 2026-04-23

- [x] Home renders exclusively from `analysis_groups` — no hardcoded tabs.
- [x] `active_home_subtab` reactive; `_track_active_home_subtab` effect.
- [x] Dynamic `@render.plot` handlers registered at init for all `plot_group_{p_id}`.

### Phase 21-C: Tier Toggle ✅ COMPLETED 2026-04-23

- [x] `tier_toggle` radio (T1/T2 always; T3 persona-gated advanced+).
- [x] `_track_tier_toggle` effect syncs input → `tier_toggle` reactive.Value.
- [x] `ref_tier_switch` and `view_toggle` removed.

### Phase 21-D: Home Layout Redesign & Collapsible Data Preview ✅ COMPLETED 2026-04-23

- [x] Thin header strip (dataset label + tier toggle). Groups as `navset_pill`. Plots in `navset_card_tab`. Data preview in independent accordion below.
- [x] `home_data_preview` scoped to active plot dataset. Column selector (`home_col_selector_ui`) above DataGrid.
- [x] `data_preview_section` always mounted in DOM (before no-groups early return).
- [x] No-groups fallback wraps top-level plots in synthetic `navset_card_tab`.
- [x] Tier toggle uses `selected="T1"` (static) to prevent `dynamic_tabs` DOM re-render on tier change.

### Phase 21-E: Comparison Mode ✅ COMPLETED 2026-04-30

- [x] `comparison_mode_toggle_ui` fixed: persona IDs use hyphens; tier gate (`tier_toggle != "T3"` early return); label "⚖ Compare T2 vs T3".
- [x] `ui.output_ui("comparison_mode_toggle_ui")` placed in `theater_header` inside `dynamic_tabs` (was defined but never mounted).
- [x] `_make_cmp_baseline_handler(p_id)` factory registered for all plot IDs — renders `plot_group_{p_id}_cmp_base` with T1 data, no T3 audit nodes.
- [x] `dynamic_tabs` reads `comparison_mode` input: 2-column layout (T2 baseline left / T3 adjusted right) when ON in T3 tier.

### Phase 21-F: Context-Reactive Filters + Column Selection ✅ COMPLETED 2026-04-23

- [x] Filter recipe builder UI: `_pending_filters` + `applied_filters` reactive.Values.
- [x] Shell stability pattern: `sidebar_filters` reads only `current_persona`; child outputs (`filter_rows_ui`, `filter_form_ui`, `filter_controls_ui`, `filter_t3_btn_ui`) independent.
- [x] `_apply_filter_rows` helper: auto-promotes eq/ne→in/not_in for list values; casts column to Utf8 for set ops; coerces scalar to numeric dtype.
- [x] `applied_filters` → plot handlers and `home_data_preview` (predicate pushdown).
- [x] `not_in` op added to VizFactory predicate pushdown.
- [x] Column selector (`selectize`) above DataGrid, preview-only.
- [ ] 21-F-5 (T3 Apply to recipe) — UI stub present; serialization deferred.
- [ ] 21-F-7 (add `scale_x_discrete` to manifests) — deferred to user.

### Phase 21-G: Persona-Gated Right Sidebar Suppression ✅ COMPLETED 2026-04-30

- [x] `hidden_personas = {"pipeline-static", "pipeline-exploration-simple"}` in `right_sidebar_content_ui`.
- [x] Returns `ui.div()` for suppressed personas — sidebar slot empty, theater expands to full width.
- [x] Full audit stack visible for ≥ `pipeline-exploration-advanced`.

### Phase 21-H: Headless Verification & @verify Gate ✅ COMPLETED 2026-04-30

- [x] `app/tests/debug_home_theater.py` created — 10 sections, 76/76 checks PASS.
- [x] Covers: persona feature flags, manifest tab structure, tier choices, sidebar suppression, comparison mode gating, PK extraction, session provenance SHA256, ghost round-trip, filter recipe schema, bootloader locations.
- [x] Output artifact: `tmpAI/home_theater_verify/results.json`.

### Phase 21-I: Export Results Bundle ✅ COMPLETED 2026-04-23

**Governing ADR:** ADR-047.

- [x] `system_tools_ui`: user-name field, preset radio (web/publication), filter warning, download button.
- [x] `@render.download export_bundle_download`: async generator yielding zip bytes.
- [x] Bundle: `plots/` (SVG/PNG), `data/` (T1+T2 always; T3 for advanced+T3), `recipes/`, `FILTERS.txt` (No Trace No Export), `report.qmd` (Quarto source), `README.txt`.
- [ ] Ghost save to `user_sessions` — deferred.
- [ ] Per-plot checkbox selection — deferred (all plots always exported).

---

## Phase 22: Server Decomposition (ADR-045) — COMPLETED 2026-04-23

**Objective:** Split the 2,362-line `app/src/server.py` monolith into a thin orchestrator (228 lines) plus five focused Shiny handler modules (`app/handlers/`) and a pure manifest introspection module (`app/modules/manifest_navigator.py`). **Zero behaviour change** — structural refactor only.

**Governing ADR:** ADR-045. **Completed:** 2026-04-23.

### Phase 22-A: Create `app/modules/manifest_navigator.py`

- [x] Created `app/modules/manifest_navigator.py` (~280 lines).
- [x] Moved 5 pure functions, renamed to public API (dropped `_` prefix): `build_sibling_map`, `build_schema_registry`, `build_lineage_chain`, `load_fields_file`, `resolve_fields_for_schema`.
- [x] Module docstring references ADR-045 and lists full public API.
- [x] `blueprint_handlers.py` imports from `manifest_navigator`; `server.py` no longer needs these imports.
- [x] Import check passed.

### Phase 22-B: Create `app/handlers/` directory and `__init__.py`

- [x] Created `app/handlers/__init__.py` with package docstring listing all 5 handler modules and Two-Category Law constraints.

### Phase 22-C: Extract `app/handlers/gallery_handlers.py`

- [x] Created with `define_server(input, output, session, *, bootloader, wrangle_studio, safe_input)`.
- [x] All gallery handlers moved: `_sync_family_all`, `_sync_pattern_all`, `_sync_difficulty_all`, `_init_gallery_selector`, `handle_gallery_clone`, `_gallery_active_metadata`, `gallery_preview_img`, `gallery_static_data`, `gallery_yaml_preview`, `gallery_md_content`, `_update_gallery_options`, `gallery_browser_anchor`.
- [x] Delegation call added to `server.py`.

### Phase 22-D: Extract `app/handlers/ingestion_handlers.py`

- [x] Created with `define_server(input, output, session, *, bootloader, current_persona, safe_input)`.
- [x] Handlers moved: `handle_ingest`, `update_persona_context`.

### Phase 22-E: Extract `app/handlers/audit_stack.py`

- [x] Created with `define_server(input, output, session, *, wrangle_studio, recipe_pending, snapshot_recipe, active_cfg, active_collection_id)`.
- [x] Handlers moved: `handle_apply`, `track_recipe_changes`, `recipe_pending_badge_ui`, `audit_nodes_tier2`, `audit_nodes_tier3`.

### Phase 22-F: Extract `app/handlers/blueprint_handlers.py`

- [x] Created with full keyword-only dependency injection signature.
- [x] All Phase 18 Shiny wiring moved; imports updated to use `manifest_navigator`.
- [x] `_includes_map`, `_component_ctx_map`, `_schema_registry` injected as `reactive.Value` instances from `server.py`.

### Phase 22-G: Extract `app/handlers/home_theater.py`

- [x] Created with `define_server(input, output, session, *, bootloader, wrangle_studio, dev_studio, orchestrator, viz_factory, gallery_viewer, current_persona, anchor_path, tier1_anchor, tier_reference, tier3_leaf, active_cfg, active_collection_id, safe_input)`.
- [x] All Home Theater handlers moved: `dynamic_tabs`, `sidebar_nav_ui`, `sidebar_tools_ui`, `right_sidebar_content_ui`, `system_tools_ui`, `sidebar_filters`, `plot_reference`, `table_reference`, `plot_leaf`, `table_leaf`, `handle_plot_brush`, `comparison_mode_toggle_ui`.

### Phase 22-H: Slim `server.py` to orchestrator only

- [x] Final `server.py`: 228 lines — shared state, shared calcs, shared utils, 5 delegation calls only.
- [x] `render` removed from shiny imports (no `@render.*` in server.py).

### Phase 22-I: @verify Gate

- [x] [HEADLESS] Import check passed.
- [x] [LIVE] Smoke test — no major regressions detected (user confirmed).
- [x] [@verify] Complete.

### Phase 22-J: Per-Plot T3 Audit Scoping & Join-Key Propagation ✅ COMPLETED 2026-04-25

- [x] `t3_recipe_by_plot: dict[plot_subtab_id, list[RecipeNode]]` replaces flat `t3_recipe` — per-plot stacks.
- [x] Propagation modal: 3-option scope dialog ("This plot only / All plots / All plots except…") at T3 promotion.
- [x] PK-touching nodes show ⚠️ warning banner in modal and on audit card.
- [x] Linked-id deletion: 🗑 delete removes a node and all copies sharing the same `id` across every plot stack.
- [x] Join-key propagation: orchestrator `per_ingredient_cast`/`base_cast` normalisation (Categorical ≠ String fix).
- [x] Live-UI verification checklist written: `tasks_test_22J.md`. Awaiting user sign-off.

---

## Phase 23: Scientific Audit Hardening (ACTIVE 2026-04-23)

**Objective**: Institutionalize the development-phase audit requirements: mandatory Tier 1 visibility, biological typing standards, and precision renaming.

- [x] **ADR-046**: Formalize the Scientific Audit Protocol (Tier 1 visibility, retention policy). [DONE]
- [x] **Rulebook Sync**: Update `rules_data_engine.md` and `rules_manifest_structure.md` with whitelisting and typing laws. [DONE]
- [ ] **Ingestor Diagnostics**: Implement non-breaking warnings for missing manifest columns in `DataIngestor`.
- [ ] **Audit Materialization**: Standardize the `debug_wrangler.py` and `debug_assembler.py` output paths to a unified `tmp/{date}/{lineage}/` folder structure.
- [ ] **Lineage 2 (Plasmids)**: Apply new renaming precision standards (`predicted_phenotype`) and verify via Tier 1 audit.

---

## Phase 24: `home_theater.py` Decomposition (ADR-051) — IMPLEMENTED 2026-05-01

**Objective:** Split `app/handlers/home_theater.py` (2,853 lines pre-flight) into a thin coordinator plus focused handler modules, following ADR-045 decomposition pattern. **Gate met (2026-04-30):** Phase 22-J live-UI test §1 PASSED. **Status (2026-05-01):** ALL STEPS LANDED ON `dev`. ADR-051 → IMPLEMENTED. `home_theater.py`: 2,853 → 1,278 lines (-55.2%).

**Governing ADR:** ADR-051. **Triggered by:** Post-Phase-21 growth past the 2,362-line threshold that triggered ADR-045. **Refactor protocol:** `.claude/knowledge/archive/refactor_protocol_phase24.md` (two-commit-per-step move + cleanup, verification gate after every commit, halt-and-ask on repeat failure).

### Implemented file map

| File | Owns | Step | LoC | Move | Cleanup |
|---|---|---|---|---|---|
| `app/handlers/home_theater.py` (slimmed) | `_safe_id`, `_collect_all_group_plot_ids`, `define_server` init + reactive helpers + closures (`_resolve_active_spec/_lf`, `_t3_filter_rows`, `_t3_drop_columns`, `_active_plot_t3_nodes`, `_all_plot_subtab_ids`, `_plot_label`, `_spec_discrete_axes`), `_make_group_plot_handler`, `_make_cmp_baseline_handler`, `dynamic_tabs`, `_track_tier_toggle`, `_sync_session_provenance`, `_track_active_home_subtab`, `home_data_preview`, `home_col_selector_ui`, `col_drop_audit_btn_ui`, `sidebar_nav_ui`, `sidebar_tools_ui`, `right_sidebar_content_ui`, plot/table renders + brush + comparison toggle, plus calls to the three sub-handlers | — | 1,278 | — | — |
| `app/modules/t3_recipe_engine.py` (new) | `_apply_filter_rows(lf, filter_rows)`, `_op_label(op)` — pure helpers (Two-Category Law). | 24-A | 133 | `89bb5ef` | `890b609` |
| `app/handlers/session_handlers.py` (new) | `define_session_server` registers `session_management_ui`, `_handle_session_import`, `_handle_session_actions`, `_restore_session`. | 24-B | 262 | `f540cbf` | `d50197e` |
| `app/handlers/export_handlers.py` (new) | `define_export_server` registers `system_tools_ui`, `export_bundle_download`, `export_audit_report_ui`, `export_audit_report_download`, `export_audit_docx`, `_audit_report_filename`, `_export_bundle_filename`. | 24-C | 597 | `4c38f26` | `18dbd46` |
| `app/handlers/filter_and_audit_handlers.py` (new) | `define_filter_audit_server` registers `sidebar_filters`, `filter_rows_ui`, `filter_form_ui`, `filter_controls_ui`, `_filter_add_row`, `_filter_apply`, `_filter_reset`, `_col_drop_to_audit`, `_column_presence_per_plot`, `_open_propagation_modal`, `_handle_propagation_confirm`, `_plot_has_column`, `_clear_filters_on_t3_apply`, `_make_remove_handler` (+ 50-row registry), private `_last_apply_count`. | 24-D | 811 | `f0f7d92` | `2393e50` |
| (24-E finalise — docs + @deps + ADR-051 status flip) | — | 24-E | — | `0b50fbd` | — |

### Decisions and deviations from the original plan

1. **Shared reactive state held inside `home_theater.define_server`.** `applied_filters`, `_pending_filters`, `_propagation_scratch` remain as `reactive.Value` instances created in `home_theater.define_server()` and passed as kwargs to `define_filter_audit_server(...)`. Same pattern as `server.py` → handlers for `tier1_anchor`/`active_cfg`. Not promoted to `server.py` — they are Home-scoped.

2. **`define_*_server` contract held.** Each sub-handler exposes `(input, output, session, *, ...)` with keyword-only args after the Shiny trio. Calls live inside `home_theater.define_server`, not `server.py` directly — ADR-045 only adds one delegation level; Phase 24 nests sub-delegation within the Home theater tier.

3. **Filter UI + T3 audit kept in ONE file.** ADR-051 originally proposed `t3_audit_handlers.py` separate from filter UI. Kept together as `filter_and_audit_handlers.py` because `_filter_apply`, `_col_drop_to_audit`, and `_handle_propagation_confirm` share `_propagation_scratch` and call into `_open_propagation_modal`. Splitting would force exposing scratch state across module boundaries — a worse architectural outcome than the larger file.

4. **`sidebar_filters` MOVED with the rest** (originally planned to stay). Once filter UI moved to `filter_and_audit_handlers.py`, keeping the static shell in `home_theater.py` would have introduced an awkward cross-file UI/effect boundary. Static shell + child renders + effects co-locate.

5. **`_op_label` lifted to `t3_recipe_engine.py` in 24-D.** During 24-C it was inlined in `export_handlers.py` (mechanical move). 24-D folded a prep step that lifted it to the canonical pure-helper module so both `export_handlers` and `filter_and_audit_handlers` import from one place.

6. **24-B kwarg surface narrower than planned.** Plan listed 7 reactive kwargs; actual session block reads only 3 (`session_manager`, `current_persona`, `home_state`). Final signature reflects the truth.

7. **24-D kwarg surface broader than planned.** 14 kwargs (4 reactive.Values, 6 closure callables from `define_server`, plus `input/output/session/tier_toggle/active_home_subtab/safe_input`). Recorded as a smell to revisit in a future cleanup pass.

### Verification (each step independently passed)

- **Unit:** `pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q` → 90/90 in ~1.2s. The 21-case filter regression is the single highest-signal gate for this refactor.
- **Import:** `python -c "from app.src.main import app; print('OK')"`.
- **Smoke (Playwright headless):** `SPARMVET_PERSONA=qa pytest app/tests/test_shiny_smoke.py -q` → 10 pass + 2 persona-skip in ~20s. Includes all 4 filter pipeline tests.

### Post-Phase 24 deliverables (all complete)

- [x] `@deps` header in `home_theater.py` rewritten — `provides` lists only what stayed; `consumes` adds the four new files.
- [x] ADR-051 status: DESIGNED → IMPLEMENTED. Actual file map documented in `architecture_decisions.md`.
- [x] `dependency_index.md` regenerated via `assets/scripts/build_dep_graph.py`.
- [x] `handoff_active.md` Session 13 entry appended.
- [x] `audit_2026-05-01.md` written.
- [x] `tasks_phase24.md` carries an executed-change manifest for each step.

---

## Phase 25: Left Sidebar Restructure — COMPLETE 2026-05-01

**ADR:** ADR-052
**Status:** COMPLETE. All 10 substeps (A–J) delivered. See `tasks_archive_phase25.md` and `audit_2026-05-01_phase25_complete.md`.
**Design doc:** `EVE_WORK/daily/2026-05-01/persona_functionality_side_bars_v3_clean.csv`
**Change manifests:** `.claude/tasks/tasks_phase25.md`

### Scope

Ten ordered substeps (A→J, risk-ascending):

| Step | Label | Model | Risk |
|---|---|---|---|
| 25-A | Config + renames (Test Lab, Gallery for project-independent) | Sonnet | Low |
| 25-B | Persona template new fields + PersonaValidator | Sonnet | Low-Med |
| 25-C | Persona gating + bug fixes (PERSONA-1, Gallery, comparison flag) | Sonnet | Med |
| 25-D | Right sidebar layout fix (exclude container for pipeline personas) | Sonnet | Med |
| 25-E | Accordion restructure (rename + move panels) | Sonnet | Med |
| 25-F | Data Import panel (new build, testing_mode-aware) | Opus | High |
| 25-G | Export: audit report format selector + Quarto render + session export .zip | Opus | Med-High |
| 25-H | Single Graph Export (un-deferred from Phase 22) | Opus | Med |
| 25-I | Visual fixes (trash icon, right sidebar header) | Sonnet | Low |
| 25-J | Smoke test coverage update | Sonnet | Low |

### Key decisions (ADR-052)

- **Right sidebar layout:** excluded at `ui.py` build time for pipeline personas (Option A — reads `SPARMVET_PERSONA` env var)
- **New persona template fields:** `manifest_selector.visible/fixed_manifest` + `testing_mode`
- **Pipeline personas always production:** `testing_mode=false` for static + simple — testing uses developer/advanced personas
- **Gallery for project-independent:** `gallery_enabled=true` added to template
- **Test Lab:** renamed from Dev Studio
- **Quarto:** replaces Pandoc for server-side report rendering (HTML + PDF + DOCX)
- **passive_exploration / t3_audit:** two new capability columns formalise existing but undocumented behaviour

### Protocol

Reuses `.claude/knowledge/archive/refactor_protocol_phase24.md` verbatim. Same verification gate. Same halt-and-ask conditions.

---

## Phase 26: UI Harmonisation + Filter fixes + IMPORT-1 — COMPLETE 2026-05-02

**ADRs:** ADR-055, ADR-056, ADR-057, ADR-058, ADR-059
**Status:** COMPLETE
**Audit log:** `.claude/logs/audit_2026-05-02.md`

### Delivered

- CSS theme externalised to `config/ui/theme.css`; per-persona override via `theme_css:` in persona template (ADR-055).
- View title banners (`.view-title-banner`) across Blueprint Architect, Test Lab, Gallery (ADR-056).
- Gallery internal sidebar → persistent left `#nav_sidebar` accordion (ADR-057).
- Sidebar collapse toggle cross-wiring fix; T3 modal radio spacing fix.
- VizFactory `breaks_integer: true` param for integer-only axis breaks (ADR-059).
- MetadataValidator dtype_map audit — added `numeric`, `character`, `date`, `integer`, `bool`, PascalCase aliases.
- Numeric `in`/`not_in` filter: coerce values to column native dtype (was casting to Utf8 → silent failure).
- Filter widget Int column: integer step/bounds (was always float).
- Filter `between` radio labels: `"≤ inclusive"` / `"< exclusive"` (was doubled).
- Filter reset: clears selectize and text widgets.
- Trash button CSS aligned between filter rows and audit panel.
- IMPORT-1: Data Import assignment table with `MetadataValidator` validation, parquet cache bust, `data_refresh_trigger` reactive (ADR-058).
- EXPORT-SGE-2: `full_recipe.yaml` (resolved assembly + T3 nodes + plot spec) in SGE ZIP bundle.
- EXPORT-SGE-4: multi-file Ctrl/⌘ hint in Data Import upload control.
- PROP-4: one-at-a-time workflow + reason writing guide in `docs/user_guide/audit_pipeline.qmd`.
- Task closures: STATE-1, STATE-2, BUG-PERF-1, AUDIT-2–4, UX-1/2, EXPORT-SGE-2/4, PROP-4, IMPORT-1.
- Test checklist sections 19 (Data Import), 20 (integer breaks), 21 (filter widget types) added.

### Still open

- ST22 Lineage 2 (Plasmids) — user task.
- THEATER-1, PROP-2/PROP-3, EXPORT-2/3/4 — deferred.
- UX-NOTIF-1 — DONE (2026-05-02). UX-NOTIF-2 (ghost persistence) deferred.
- Gallery Clone to Sandbox re-verify — deferred.

---

## Phase 27: Gallery Expansion + Accordion UI Harmonization — COMPLETE 2026-05-03

**ADRs:** ADR-061 (gallery panes, from Phase 26 continuation), ADR-062 (sidebar toggle), ADR-063 (6-axis taxonomy), ADR-064 (accordion-first harmonization)
**Status:** COMPLETE. CSS rounding verified; all open items resolved or deferred to future polish.
**Audit log:** `.claude/logs/audit_2026-05-03.md`

### Delivered

- Gallery sidebar: icon fix, select-all alignment, dynamic pivot choices (GALLERY-ICONS, GALLERY-SELECTALL, GALLERY-PIVOT — ADR-061).
- Gallery collapsible panes: Preview + Guidance both bslib accordion, open by default (GALLERY-PANES — ADR-061).
- `recipe_meta.md` standard 3-tier format: `##`/`>`/`###` for all 13 → 34 files (GALLERY-META — ADR-061).
- CSS §17 Educational Guidance Pane Content consolidated (CSS-SECTION17 — ADR-061).
- Sidebar toggle `position:fixed` removed — defer to bslib positioning (CSS-TOGGLE — ADR-062).
- 13 new gallery recipes with corrected VizFactory format (GALLERY-RECIPES-13 — ADR-063).
- 6-axis gallery taxonomy: `geom`/`show`/`sample_size` added end-to-end (GALLERY-TAXONOMY-6 — ADR-063).
- `TAXONOMY_CHEATSHEET.md` — canonical icon/axis/value reference (GALLERY-TAXONOMY-CHEAT).
- `generate_previews.py` — headless PNG generator; all 34 previews regenerated (GALLERY-PREVIEWS).
- All 34 `recipe_meta.md` tag strips extended to 6 fields (GALLERY-META-6AXIS).
- `_collapsible_panel()` helper; Home Plot Card + Data Preview collapsible (HOME-PLOT-COLLAPSE — ADR-064).
- Blueprint Work Area bslib accordion; Bootstrap cards styled (BLUEPRINT-WORK-COLLAPSE — ADR-064).
- CSS §18/18b accordion harmonization: bold text, `border-radius + overflow:hidden`, no grey borders (CSS-ACCORDION-HARM — ADR-064).

### Still open / ongoing

- CSS rounding verification in browser (Bootstrap cards top corners, accordion items).
- `tasks_test_ui_current.md` §12 Gallery UI tests need re-verification after taxonomy changes.
- UX-CSS-DEMO: review `assets/demo/demo_vetinst.css` after default theme finalised.
- Gallery Clone to Sandbox re-verify.

---

## Phase 28: Export Redesign + assembly→join Rename — COMPLETE 2026-05-04

**ADRs:** ADR-047 (§7 updated — scope toggle, T3 audit trail), ADR-051 (export_handlers new kwarg, deleted outputs), ADR-066 (assembly→join rename)
**Status:** COMPLETE.
**Audit log:** `.claude/logs/sessions/session_20260504.md`
**Changelog:** `.claude/knowledge/changelog.md`

### Delivered

- **Export redesign (EXPORT-REDESIGN-1, EXPORT-REDESIGN-2):**
  - Single "Export" accordion panel replaces "Global Project Export" + "Single Graph Export".
  - 3-way scope toggle `[Global project | Active group | Active plot]` gated on `export_enabled`.
  - `t3_steps.yaml` auto-included in bundle when T3 has committed nodes.
  - T3 Audit Trail auto-generated section in `report.qmd`.
  - Separate "Export Audit Report" button removed — audit trail is now part of the bundle.
  - `active_home_subtab` kwarg added to `define_export_server`.

- **assembly_manifests → join_manifests rename (ADR-066):**
  - YAML key, Python dict key, role string, TubeMap labels, UI labels all renamed.
  - ~35 files, ~65 occurrences across `app/`, `libs/`, `config/`.
  - Exception: `session_manager.py` + `debug_session_flow.py` Parquet path labels NOT renamed.
  - Variable name rule: never use bare `join` as Python variable; use `join_defs`, `join_block`.

- **Manifest modularisation:**
  - `1_test_data_ST22_dummy.yaml`: 1334 → ~290 lines via `!include` fragments.
  - `figshare_integration.yaml`: 224 → 69 lines.
  - Fragment threshold documented in `manifest_data_contract_rules.md` §6.

### Open / deferred

- `single_graph_export_handlers.py` still exists and is imported by `home_theater.py` but has no UI mount point (dead code after accordion removal). Decision needed: remove or keep.
- EXPORT-HASH-2: read `decision_hash` from Parquet metadata at export time.
- SESSION-PERSONA-1: gate ghost_save on `t3_sandbox_enabled`.

---

## Phase 29: Library Extraction + Rename — COMPLETE 2026-05-05

**ADRs:** ADR-067 (`libs/blueprint_arch/`), ADR-068 (`libs/test_lab/`)
**Status:** COMPLETE.

### Delivered

- **`libs/blueprint_arch/`** — new dedicated lib for Blueprint Architect pure-Python logic:
  - `blueprint_mapper.py` moved from `libs/utils/src/utils/` → `libs/blueprint_arch/src/blueprint_arch/`
  - `manifest_navigator.py` moved from `app/modules/` → `libs/blueprint_arch/src/blueprint_arch/`
  - `debug_blueprint_mapper.py` moved to `libs/blueprint_arch/tests/`
  - `blueprint_handlers.py` imports updated; installed as editable lib

- **`libs/test_lab/`** — new lib absorbing `generator_utils` (Option B):
  - All 4 source modules (`aqua_synthesizer`, `bootstrapper`, `extractor`, `reconciler`) migrated with updated headers
  - All 4 test scripts migrated with updated imports
  - `assets/scripts/generate_demo_data.py` import updated
  - `generator_utils` uninstalled and directory removed

- **`dev_studio.py` → `test_lab_studio.py` rename:**
  - Class `DevStudio` → `TestLabStudio`
  - All consumers updated (`server.py`, `home_theater.py`)

- **`workspace_standard.md` `@sync` guardrail** — added to §3 Operational Mandate

- **Documentation sweep:** `dependency_index.md`, `tasks.md`, `architecture_decisions.md` (ADR-067/068) updated

### Open / deferred

- `single_graph_export_handlers.py` dead code — still deferred (see Phase 28 open items)
- ADR-045 Two-Category Law refactor for remaining `app/modules/` files still pending (UTILS-RELOC-2, ADR045-REFACTOR)

---

> **Numbering note:** Phase 30 was skipped — same as the gaps at Phases 13–15 (see Phase 11 note). Work for that period was tracked directly in git commits and ADRs. Phases 31+ are PLANNED/IN-PROGRESS.

## Phase 31: Sidebar Slot Registry + Export Provenance (COMPLETED — 2026-05-09)

**ADRs:** ADR-073 (Configurable Sidebar Slot Registry), ADR-069 amendment (per-source-file hash table)
**Status:** COMPLETED. All substeps delivered (31-A through 31-H, plus IMPORT-UI-1).

### Objective

Replace the hardcoded left/right sidebar accordion sequence with a declarative slot registry configurable per-persona and per-workspace via persona template `workspaces:` section and `!include` shared sidebar config files. Also complete the ADR-069 export provenance cluster.

### Substeps (ordered)

| Step | Task ID | Label | Model | Risk |
|---|---|---|---|---|
| 31-A | SIDEBAR-CONFIGS-1 | `config/ui/sidebars/` shared YAML files + persona template `workspaces:` sections | haiku | Low |
| 31-B | SIDEBAR-REGISTRY-1 | Panel registry, bootloader `get_sidebar_config()`, `home_theater.py` slot iteration, `ui.py` ADR-053 fix | sonnet | Med-High |
| 31-C | SIDEBAR-VALIDATE-1 | `SidebarValidator` + `scripts/validate_persona_config.py --all --strict` | sonnet | Med |
| 31-D | UTILS-RELOC-2 | `gallery_manager.py` deduplicate → canonical copy in `libs/viz_gallery/` | haiku | Low |
| 31-E | EXPORT-AUDIT-COMPLETE-1 | `build_export_provenance()` helper + per-source-file hash table in README+report | sonnet | Med |
| 31-F | EXPORT-VERSION-1 | `git_commit` + `release_version` in all export surfaces | haiku | Low |
| 31-G | EXPORT-HASH-2 | `decision_hash` from Parquet metadata at export time | sonnet | Med |
| 31-H | EXPORT-IMG-META-1 | Provenance embedded in PNG/SVG/PDF file metadata | sonnet | Med |
| 31-I | DEPLOY-CONNECT-1 | Posit Connect editable lib install handling, entry point doc, Connect profile template, clean env smoke test | sonnet | Med |

### Key decisions (ADR-073)

- **Slot list controls layout; flags control capability** — fully independent layers
- **Per-workspace** — Home, Blueprint, Gallery, Test Lab each declare their own sidebar config
- **`!include` shared configs** in `config/ui/sidebars/` — personas share files, reduce duplication
- **`visible: false`** excludes the sidebar container from DOM (not CSS-hidden)
- **Right sidebar structural exclusion** moves from persona-name check in `ui.py` → `workspaces.home.right_sidebar.visible` in persona template (fixes ADR-053 violation, task 25-O)
- **`SidebarValidator`** runs alongside `PersonaValidator` at startup and in CI (`--strict` mode)

### Delivered

| Step | Task ID | Status |
|---|---|---|
| 31-A | SIDEBAR-CONFIGS-1 | ✅ |
| 31-B | SIDEBAR-REGISTRY-1 | ✅ |
| 31-C | SIDEBAR-VALIDATE-1 | ✅ |
| 31-D | UTILS-RELOC-2 | deferred |
| 31-E | EXPORT-AUDIT-COMPLETE-1 | ✅ |
| 31-F | EXPORT-VERSION-1 | ✅ |
| 31-G | EXPORT-HASH-2 | ✅ |
| 31-H | EXPORT-IMG-META-1 | ✅ |
| — | IMPORT-UI-1 | ✅ (unified import panel) |
| — | DEPLOY-CONNECT-1 | deferred |

### Open / deferred

- `ADR045-REFACTOR` (app/modules/ Two-Category Law violations) — deferred, needs separate scope discussion
- `UI-TITLE-1` (manifest-driven title/subtitle) — decided, implementation pending

---

## Phase 32: Lineage Infrastructure + BLUEPRINT IDE Build Mode (PLANNED — 2026-05-09)

**ADRs:** ADR-074 (Lineage Infrastructure as Shared Provision), ADR-075 (BLUEPRINT IDE Build Mode)
**Status:** PLANNED. Design complete. Tasks in `tasks.md`.
**Audit log:** `.claude/logs/audits/audit_2026-05-09.md` (Wave 7)

### ADR-074 — Lineage Infrastructure

| Step | Task ID | Label | Model | Risk |
|---|---|---|---|---|
| 32-A | LINEAGE-NAV-1 | Add `build_plot_lineage` + `get_plot_ids_in_group` to `manifest_navigator.py` | sonnet | Med |
| 32-B | LINEAGE-EXPORT-1 | Export bundle gains `lineage/lineage_graph.json` (shared-node DAG, no per-plot duplication); `report.qmd` gets Mermaid flowchart + step summary table + JSON note | sonnet | Med |

**Key decisions (ADR-074):**
- Lineage functions live in `libs/blueprint_arch/manifest_navigator.py` — formally shared infrastructure
- One shared-node DAG per export scope; T1/T2 nodes deduplicated across plots
- No lineage SVG in HOME export — documentation artifact; SVG/PNG of manifest DAG is BLUEPRINT-scoped (pipeline authors only)
- `report.qmd`: Mermaid flowchart + step summary table + JSON explanation note (not inline SVG)

### ADR-075 — BLUEPRINT IDE Build Mode

| Step | Task ID | Label | Model | Risk |
|---|---|---|---|---|
| 32-C | BP-SCHEMA-1 | `ui_schema` kwarg in `@register_action` + `@register_plot_component`; `schema_registry.py` in `blueprint_arch` | sonnet | Med |
| 32-D | BP-FORMS-1 | BLUEPRINT form builder — 8 widget types rendered from `ui_schema` dicts | opus | High |
| 32-E | BP-ESCAPE-1 | YAML escape hatch: read-only (`blueprint_enabled`); editable (`manifest_edit_enabled`) | sonnet | Med |
| 32-F | BP-UNDO-1 | 20-step session undo deque for BLUEPRINT node edits | sonnet | Med |
| 32-G | BP-HELP-1 | Python `__doc__` resolved at runtime via `importlib`; optional `doc_url` ("Open in browser", disabled in air-gapped deployments) | sonnet | Med |
| 32-H | BP-COLOR-1 | Color widget: column mapping \| set literal (palette library \| project palette \| custom hex) | sonnet | ✅ |
| 32-H2 | BP-COLOR-2 | Deployment palette registry `config/palettes.yaml`; `bootloader.get_palettes()`; color widget "Project palette" source | haiku | ✅ |
| 32-H3 | BP-COLOR-3 | `plot_defaults.palette` in manifest → VizFactory scale injection at render time | sonnet | ✅ |
| 32-I | BP-FLAG-1 | `manifest_edit_enabled` flag: add to all 6 persona templates (false/false/false/false/true/true); cascade in bootloader | haiku | Low |
| 32-J | ACTION-RENAME-1 | `scripts/migrate_manifests.py` — scan all YAML for renamed action names; report + `--apply` flag | haiku | Low |

**Key decisions (ADR-075):**
- `ui_schema` dict embedded directly in `@register_action` / `@register_plot_component` kwargs — no separate schema files
- `schema_registry.py` in `blueprint_arch`: reads `ui_schema` dicts at startup; headless-safe; zero Shiny imports
- 8 widget types: `column_selector`, `expression`, `enum`, `dtype_picker`, `number`, `string`, `color`, `column_or_literal`
- Color widget nested model: column mapping | set literal (palette library | project palette | custom hex)
- Help: Python `__doc__` at runtime via `importlib` — air-gap safe, version-matched. External `doc_url` optional
- Action naming: align `@register_action` names with Polars for 1:1 wrappers; composite actions keep descriptive names
- Position rules enforced via `context` tag in `ui_schema`: `t1` / `t2` / `assembly` / `plot`
- Apply gate: upstream schema propagates on Apply only (not continuously)
- Edit/remove: (1) edit in-place + re-Apply, (2) 20-step undo deque, (3) YAML escape hatch
- `manifest_edit_enabled`: default false all personas; true for developer and qa only

**Key decisions (ADR-081 — Palette Registry):**
- Project palettes live in `config/palettes.yaml` — operator config, not library code
- `bootloader.get_palettes()` is the sole reader; never empty (`sparmvet_brand` built-in always present)
- `libs/viz_factory/` does NOT read config files — palette registry injected at construction (ADR-011)
- `app/src/server.py`: `VizFactory(palette_registry=bootloader.get_palettes())`
- VizFactory `_apply_palette()`: project → manual scale; viridis family → viridis_d; other → brewer; guards: no double-inject, only for mapped aesthetics

---

## Phase 33: BLUEPRINT AI Agent MVP-1 (IN PROGRESS — 2026-05-09)

**ADRs:** ADR-076 (BLUEPRINT AI Agent Helper), ADR-077 (Fail-Fast Cascade Enforcement)
**Status:** IN PROGRESS. Adapter layer complete; UI wiring pending.
**Audit log:** `.claude/logs/audits/audit_2026-05-09.md`

### Objective

Embed a conversational AI helper in the BLUEPRINT right sidebar. The agent interviews the user about their analytical goal, inspects the loaded schema, and proposes manifest fragments via `propose_manifest_diff`. All changes require user Apply — the agent never modifies the manifest directly.

### Substeps

| Step | Task ID | Label | Model | Status |
|---|---|---|---|---|
| 33-A | BP-AGENT-FLAG-1 | `blueprint_agent_enabled` flag + `blueprint_agent:` config block in persona templates | haiku | ✅ (Phase 31) |
| 33-B | BP-AGENT-1 | `AgentAdapter` protocol + `ClaudeCliAdapter` + `DisabledAdapter` + `agent_context.py` | sonnet | ✅ |
| 33-C | BP-AGENT-PARSER-1 | Fenced-block extractor (`agent_tool_parser.py`) | sonnet | open |
| 33-D | BP-AGENT-TOOLS-1 | 3 MVP tools (`get_available_actions`, `get_available_components`, `get_field_contract`) | sonnet | open |
| 33-E | BP-AGENT-INSTRUCT-1 | System prompt file `config/ui/agents/blueprint_default.md` | sonnet | open |
| 33-F | BP-AGENT-PANEL-1 | Register `blueprint_agent_chat` panel in sidebar registry + persona templates | haiku | open |
| 33-G | BP-AGENT-UI-1 | Chat panel render outputs in `blueprint_handlers.py` | sonnet | open |
| 33-H | BP-AGENT-CSS-1 | `.bp-agent-*` rule block in `config/ui/theme.css` | haiku | open |

### Key decisions (ADR-076 implemented)

- `ClaudeCliAdapter` runs `claude -p` in isolated `agent_sessions/{uuid}/` dirs — Claude Code scopes conversation history per `cwd`, achieving full session isolation
- Auth probe (`--version` + trivial `-p "ok"`) at bootloader init; any failure → `DisabledAdapter` fallback, startup never blocked
- `--output-format text` used (not `json`) — simpler content extraction; spec said `json` but implementation deviation is harmless
- `--system` flag injects the Layer 1 system prompt on the first turn; `--continue` used for all subsequent turns
- `build_system_prompt()` assembles: instructions file + compressed action registry + project context + fenced-block protocol spec
- `build_turn_context()` emits Layer 3 context dict: workspace, active plot, manifest section, row counts, data visibility
- `bootloader.get_agent_adapter()` is the sole entry point — cached per Bootloader instance
- `bootloader.get_agent_config()` returns the `blueprint_agent:` block from the persona template
- `flock` single-flight on `lock` file in session dir — prevents concurrent subprocess calls

### Deferred (Phase 33 non-scope)

- `ClaudeApiAdapter`, `LocalModelAdapter` — Phase 2/3
- Token-by-token streaming — explicit non-decision; all backends buffered
- Gallery awareness (`gallery_awareness: true`) — reserved flag, Phase 1 = false
- MCP server exposing tools — Phase 2 upgrade path
