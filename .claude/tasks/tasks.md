# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-12 (Task hygiene — stripped completed inline noise, archived CROSS-LIB-SCRIPT-1 + TASK-DRIFT-EXCLUSION-1) by @dasharch

---

## Task Organization Protocol (read before adding or moving items)

| Section | What belongs here |
|---|---|
| **🟢 Do Now** | Immediately actionable — no blocker, no design decision pending. Audit-detected problems that need no user discussion go **at the top of this section**, above all other items. |
| **🤔 Needs Discussion / Decision** | Requires a design pass, ADR authoring, or explicit scoping before any code. No implementation until resolved. |
| **⏳ Deferred / Blocked** | Blocked by library limitation, another task, or large-scale planned work. Sub-group by what is blocking. |
| **🟡 Bio-Scientist Enhancements** | `[ENHANCEMENT REQUEST]` items from manifest design sessions only (see `rules_persona_bioscientist.md §4-A`). |
| **👤 User Required** | Needs user action, decision, or explicit discussion. No agent progress until user responds. |

**Rules for keeping the file clean:**
- **Empty sections stay empty.** If Do Now has no items, leave it blank — no placeholder text, no status lines.
- **`> Completed:` / `> Status: COMPLETED` inline pointers inside sections are FORBIDDEN.** When items are done, move them to the archive file and update the archive table + pointers at the bottom.
- **Context and session notes go at the bottom** — in the `## 📋 Session Notes` section, not inside active task sections.

---

## 🟢 Do Now

Items with no blockers — can be started immediately.

### Phase 18-F — Action Registry ui_schema Parity (prerequisite for BP-FORMS-1)

- [x] **ACTION-UISCHEMA-1** `[sonnet/medium]`: Add `ui_schema` dicts to the **42 remaining `@register_action` decorators** that currently have none. The 2 engine-internal actions (`sink_parquet`, `scan_parquet`) are excluded — they are not user-facing and must not appear in the Blueprint form picker. All 8 widget types must be used as appropriate: `column_selector`, `expression`, `enum`, `dtype_picker`, `number`, `string`, `color`, `column_or_literal`. Context tags (`t1`/`t2`/`assembly`/`plot`) must reflect valid position rules. Use existing `ui_schema` examples in `cleaning/core.py`, `cleaning/expressions.py`, `relational/joins.py`, `reshaping/core.py` as canonical patterns. Missing actions (in order of BIOSCIENTIST §8 categories): `all_horizontal`, `any_horizontal`, `count_by_group`, `cum_count`, `cum_sum`, `date_extract`, `date_truncate`, `derive_categories`, `describe_stats`, `divide_columns`, `drop_duplicates`, `fill_nulls_direction`, `horizontal_stats`, `interpolate`, `join_filter`, `list_join`, `list_slice`, `null_if`, `percentile`, `pivot`, `recode_values`, `regex_replace`, `rename`, `replace_values`, `round_numeric`, `sample`, `sanitize_column_names`, `select_by_pattern`, `shift`, `split_and_explode`, `split_column`, `split_column_to_parts`, `split_to_list`, `summarize`, `to_struct`, `unique`, `unique_rows`, `unnest`, `value_counts`, `window_agg`, `z_score`. **Must complete before BP-FORMS-1.**

### Phase 32 — Blueprint IDE Build Mode (ADR-075 / ADR-082)

> **2026-05-20 verification + ADR-082 feature lock.** Verified this session: all 60 transformer
> action forms render headless (zero failures, all 8 widget types). BP-FORMS-1 (action-form
> rendering), BP-UNDO-1, BP-ESCAPE-1, BP-HELP-1 are implemented (commit `ab113c3` + later). The
> full BLUEPRINT feature set is now locked by **ADR-082**; remaining form/feature work is tracked
> as the new task IDs below.

- [x] **BP-FORMS-1** `[opus/high]`: Form renderer — all 8 widget types, column selector with upstream schema propagation on Apply, edit-in-place flow, schema invalidation markers. **Verified 2026-05-20** (60/60 action forms render headless). Component forms + add/edit unification split out to BP-COMPONENT-* / BP-FORMS-UNIFY-1 (ADR-082 §5).
- [x] **BP-ESCAPE-1** `[sonnet/medium]`: YAML escape hatch — read-only when `blueprint_enabled`; editable when `manifest_edit_enabled`. Implemented (`bp_save_yaml_hatch`). *Functional smoke pending → BP-SMOKE-1.*
- [x] **BP-UNDO-1** `[sonnet/medium]`: 20-step session undo deque (`_snapshot_state`/`_undo`). Implemented.
- [x] **BP-HELP-1** `[sonnet/medium]`: `__doc__` resolution via `importlib` + docstring block + optional `doc_url`. Implemented (`bp_help_panel_ui`, `_resolve_action_doc`). *Functional smoke pending → BP-SMOKE-1.*
- [ ] **ACTION-RENAME-1** `[haiku/low]`: `scripts/migrate_manifests.py` — scan all YAML for renamed action names; report + `--apply` flag. Spec: implementation plan §Phase 32, step 32-J.

### Phase 32 (cont.) — ADR-082 spawned tasks (BLUEPRINT feature set)

Implementation order locked by ADR-082 §Implementation Order. Each closes a gap from the 2026-05-20 verification or a Q5/Q6 decision.

- [x] **BP-FORMS-UNIFY-1** `[opus/high]`: Add-node now uses the same `ui_schema` rich form as edit-node. **Done 2026-05-20** — `add_node` creates a stub node (`{action, params:{}, comment:""}`), appends + selects it so `bp_action_form_ui` opens for configuration; user fills + Apply (`btn_bp_apply_node`) commits. Retired the primitive annotation modal (`_finalize_add_node`, `show_annotation_modal`, `handle_confirm_node`, `pending_node`) + `new_param_value`; moved `column_selector` into the join-only conditional (joins keep their modal until BP-JOINT-1). Verified: app imports, no dangling refs, all 60 forms render headless with empty (stub) params, smoke regression-checked (the 2 `fb_op` filter failures are pre-existing full-suite flakiness — pass in isolation with/without this change). **Live click-Add→form→Apply browser smoke pending → BP-SMOKE-1.** Gap #1, ADR-082 §5.
- [x] **BP-ENUM-PREVIEW-1** `[sonnet/medium]`: Implement `preview: true` in the enum widget renderer — visual sample for linetype/position/shape enums (currently ignored; renders plain dropdown). Gap #3, ADR-075 §2.
- [x] **BP-EXPR-EDITOR-1** `[sonnet/high]`: `expression` widget → schema-aware code editor with column autocomplete (currently plain textarea). Scope: `mutate.expression` (only expression-widget field). Vendor any JS locally (ADR-071, no CDN). Gap #4, ADR-075 §2.
- [x] **BP-COMPONENT-SCHEMA-1** `[sonnet/high]`: Component `ui_schema` parity pass — 191/191 schemed across 7 files (geoms, scales, themes, guides, facets, coords, positions). 5 shared param dicts added. **Done 2026-05-20.** Prereq for BP-COMPONENT-FORMS-1 now met. Gap #2.
#### Plot Authoring Model (ADR-083) — canonical grammar-of-graphics + clean removal of legacy sugar

> Design: `.claude/design/plot_authoring_model.md`. Clean break: `factory_id` + flat aesthetics are
> REMOVED, not kept. Removal (task 8) is gated on all producers emitting canonical (tasks 5+6+7).
> Build order: 1 → (2,4,5,6,7 parallelizable after 1) → 3 → 8 last.

- [x] **BP-PLOT-MODEL-1** `[sonnet/high]`: Foundation seam (ADR-083 §2-3, §6). In `libs/viz_factory/src/viz_factory/plot_config_resolver.py`:
  - Promote `_normalise_spec` → public `normalise_plot_spec(raw) -> canonical` (transitional: still expands factory_id + flat-aes during migration).
  - Add inverse `serialise_plot_spec(canonical) -> yaml_dict` (emit `mapping:` + explicit geom `layers:`; never factory_id/flat; re-attach `_meta`).
  - `_meta` passthrough: unknown + taxonomy keys (`family`, `pattern`, `difficulty`, author notes) preserved verbatim; per-layer `comment` preserved, stripped only before plotnine.
  - Canonical model = `{target_dataset, mapping, layers (geom=layers[0]), theme, facet_by, palette, labels, guides, _meta}`.
  - Tests: `libs/viz_factory/tests/test_plot_spec_roundtrip.py` — round-trip law `serialise(normalise(raw))` render-equivalent; `_meta` preservation; idempotency.
  - **Delete dead `_standardize_config`** (viz_factory.py:455 — docstring says resolver replaced it; confirmed uncalled).
  - Update `@deps` (provides: `normalise_plot_spec`, `serialise_plot_spec`). No Shiny, no render behaviour change.
- [x] **BP-PLOT-LOAD-1** `[sonnet/high]`: BLUEPRINT plot_spec load → populate mapping form + layer nodes (geom incl.) via `normalise_plot_spec`. The `plot_spec` branch (blueprint_handlers.py:264) currently only visualizes — never sets `logic_stack`. Read-only first (no commit). Depends BP-PLOT-MODEL-1. ADR-083 §4. **Done 2026-05-20** — plot_spec branch calls `normalise_plot_spec`, builds `plot_nodes` list (`__mapping__` + layer component nodes), sets `logic_stack`; `logic_stack_ui` renders kind badges (aes/geom); `bp_action_form_ui` returns read-only view for component nodes without Apply button.
- [x] **BP-COMPONENT-FORMS-1** `[opus/high]`: Component form path. Depends BP-PLOT-MODEL-1 + BP-PLOT-LOAD-1 + BP-COMPONENT-SCHEMA-1(done). ADR-082 §5, ADR-083 §4. **Done 2026-05-20.**
  - `schema_registry.py`: added `search_components(query)` (parallel to `search_actions`); `@deps` updated.
  - `wrangle_studio.py`: added `plot` ("Plot — Layers") option to `bp_action_context`; `_update_action_picker` branches on ctx==`plot` → `get_components_for_context("plot")` + `search_components`, grouped by category.
  - `add_node`: decides kind by `get_component_catalog()` membership → `{component: name, ...}` vs `{action: ...}`.
  - `bp_action_form_ui`: branches on `node.get("component")` → `get_component_catalog()` + same `_render_action_form` (Apply button + comment). `__mapping__` stays read-only (→ BP-MAPPING-FORM-1).
  - `logic_stack_ui`: already discriminates (BP-PLOT-LOAD-1) — geom/aes badges.
  - `blueprint_handlers.py` `_bp_apply_node_handler`: kind-branch via `node_kind_key`/`node_name`; rebuilds preserving `component`/`action`; component edits don't mark downstream stale; `__mapping__` guarded out.
  - **Robustness fix:** shared `number` widget crashed on explicit `default: null` (`stat_ecdf.n`) — now renders empty field. Verified: 191/191 component forms + 60/60 action forms render headless, 0 failures; 200 unit tests + 14 smoke pass.
- [x] **BP-MAPPING-FORM-1** `[sonnet/medium]`: Dedicated mapping form (x/y/fill/color/facet_by column pickers) — `mapping` is `aes()`, not a component; own widget set. Depends BP-PLOT-MODEL-1. ADR-083 §4.
- [x] **BP-PLOT-COMMIT-1** `[opus/high]`: Correct commit (ADR-083 §8). `serialise_plot_spec` → write plot spec file's `layers:`; route wrangling action nodes to their **source tier** (tier1/tier2 via `_tier` marker); **killed the tier3 dump** in `_handle_manifest_save_internal` + `btn_download_manifest`. Save now writes the loaded fragment file (`active_component_path`); Download emits the full multi-file manifest zip bundle (master + mirrored `basename/` tree). BLUEPRINT emits canonical only (no factory_id), never T3 (ADR-082 §4). **Fixed the pre-existing tier3 bug** flagged 2026-05-20.
- [x] **BP-PLOT-MIGRATE-1** `[sonnet/medium]`: `assets/scripts/migrate_plot_specs.py` (argparse, per rules_asset_scripts). Rewrote 21 legacy YAML files (15 plot-spec fragments + 6 master manifests with inline specs) to canonical: factory_id→explicit geom, flat aes→`mapping:`, heatmap color→fill. `_IncludeLoader`/`_IncludeDumper` custom Loader/Dumper subclasses preserve `!include` directives on round-trip. Patched `create_manifest.py:281`. 125/125 tests pass. **Done 2026-05-20.**
- [x] **BP-PLOT-DOCS-1** `[sonnet/medium]`: Rewrite plot-spec format authority to canonical, remove factory_id from: `rules_manifest_structure.md §8` (the `factory_id` table + plot-spec examples + the `factory_id` row in the registered-values table), `rules_persona_bioscientist.md §3-C` examples, `docs/appendix/manifest_structure.yaml`, `project_conventions.md`, `assets/template_manifests/1_test_data_ST22_dummy.yaml` (the §3 structural reference). Confirm `rules_gallery_standards.md` already canonical (it is — gallery uses `mapping:` + `name:` layers). Do before BP-PLOT-LEGACY-REMOVE-1. **DONE 2026-05-20**: Also cleaned `manifest_data_contract_rules.md` (3 instances) and `rules_viz_factory.md` §7 cascade constraint. Only tombstone "not supported" warnings and ADR-083 historical text remain.
- [x] **BP-PLOT-LEGACY-REMOVE-1** `[sonnet/high]`: **Clean break (ADR-083 §7a).** Removed from `normalise_plot_spec`: factory_id expansion, flat-aes promotion, `_FACTORY_GEOMS`, `bar_logic` y-check, `heatmap_logic` color→fill remap. Replaced with hard `VisualizationError` (factory_id/flat-aes → "use explicit geom layer + `mapping:`; run migrate_plot_specs.py"). Removed `_FLAT_AESTHETIC_KEYS` from public API (→ private `_LEGACY_FLAT_AES`); updated `_CANONICAL_SPEC_KEYS` (removed factory_id + flat aes keys). Updated `test_plot_config_resolver.py` and `test_plot_spec_roundtrip.py`: dropped all legacy factory_id/flat-aes expansion tests, rewrote with canonical inputs, added error-path tests. 219 tests pass. Gate verified: `grep factory_id libs/ app/ config/ tests/` returns only error-message code + error-path tests. **Done 2026-05-20.**
- [x] **BP-JOINT-1** `[opus/high]`: Dedicated Joint Designer pane — left + right ingredient schemas side-by-side, live key-match preview, emits canonical `join` recipe step. Q5, ADR-082. **Done 2026-05-21** — see Session Notes 2026-05-21. **Live UI smoke pending → BP-SMOKE-1.**
- [x] **BP-COMMENTS-1** `[sonnet/medium]`: Free-text **intent `comment` field** on every node/step/group/plot in the BLUEPRINT form (wrangling nodes already have one — extend to all). Written as a `comment:` data key (preserved by ingest, no new dep). Input MUST have a hover tooltip nudging good-comment practice (e.g. "Write your intent — *why*, not what"). Q4 (revised 2026-05-20), ADR-082. **Done 2026-05-21** — `ui.tooltip()` added to all 4 comment inputs (mapping, component/geom, wrangling, joint). Plot layer `comment` key now preserved in `_serialise_component_for_save`.
- [x] **BP-GROUPS-1** `[sonnet/high]`: Group/plot sidebar inventory — persistent list with create/delete/assign affordances (MVP). **Build the group/plot CRUD decoupled from the sidebar UI** so the v2 TubeMap context menu (Q6-C) is a pure addition with no refactor. Q6, ADR-082. **Done 2026-05-21** — pure CRUD in `libs/blueprint_arch/src/blueprint_arch/group_plot_manager.py` (26 unit tests); "📋 Groups & Plots" accordion panel in Blueprint sidebar; `_do_refresh_blueprint` helper extracted so CRUD Effects re-sync TubeMap/registry after mutations.
- [x] **BP-META-1** `[sonnet/medium]`: Form UI for manifest `info:` block (description/author/version/tags) — YAML-only today. Functionality #7, ADR-082. **Done 2026-05-21** — `bp_meta_form_ui` render (read-only for non-developer, editable for `manifest_edit_enabled`); `_handle_meta_save` Effect writes `info:` block back to disk using `_IncludeLoader`/`_IncludeDumper` (preserves `!include` directives). "📝 Manifest Info" accordion panel added to Blueprint sidebar in `home_theater.py`.
- [x] **BP-NEW-1** `[sonnet/medium]`: "Create new manifest from scratch" flow — currently only import exists. Functionality #2, ADR-082. **Done 2026-05-21** — `btn_bp_new_manifest` button added to "🗂️ Master Manifest" panel; `_handle_new_manifest_btn` opens modal (slug/name/desc/author fields); `_handle_new_manifest_submit` validates snake_case slug, writes minimal YAML stub (`info:/data_schemas/join_manifests/analysis_groups`) to `config/manifests/pipelines/{slug}.yaml`, refreshes `stored_manifest_selector` and selects the new file.
- [x] **BP-VALIDATE-1** `[sonnet/medium]`: Inline manifest validation surfacing in BLUEPRINT (validator exists; not wired to UI). Functionality #16, ADR-082. **Done 2026-05-21** — `bp_validate_ui` render (shows "Run validation" button + PASS/FAIL badge + per-check rows); `_handle_validate` Effect calls `scripts/audit_manifest_coherence.py` via subprocess (clean architectural separation — no sys.path hacking); parses `## Result: ✅ PASS` / `❌ FAIL` from stdout; "🔍 Validate" accordion panel added to Blueprint sidebar.
- [x] **BP-CSS-LEGEND-1** `[haiku/low]`: TubeMap legend uses forbidden Bootstrap colours (`#0d6efd`, `#198754`) — correct against `rules_css_style_spec.md §1c`. ADR-082 Consequences. **Done 2026-05-21** — `_CY_COLOURS` in `blueprint_mapper.py` corrected (trunk: `#345beb`/`#2a4bc4`; plot: `#10a395`/`#0d8a7e`; info: `#eef0fb`/`#345beb`); Cytoscape JS palette in `ui.py` mirrored; legend badges in `wrangle_studio.py` and notification colours in `home_theater.py` fixed.
- [x] **BP-SMOKE-1** `[sonnet/medium]`: Functional smoke pass in the running app (qa persona). **Done 2026-05-21** — new `app/tests/test_shiny_smoke_blueprint.py` (12 tests, 4 tiers): T1-BP navigation, T2-BP manifest load + sidebar panels, T3-BP YAML escape hatch round-trip + validate, T4-BP save + HOME round-trip. All 12 passed in 11.87s under `SPARMVET_PERSONA=qa`. Two fixes required post-initial-run: nav label was "Blueprint Architect" not "Wrangle Studio"; escape hatch needed `wait_for_function` poll (textarea value not captured by `inner_text()`).
- [x] **BP-AUTOSAVE-1** `[sonnet/high]`: Persist the in-progress BLUEPRINT manifest draft + undo history to disk; restore on reload/crash. Modeled on HOME ghost-save (ui_implementation_contract.md §12d) but persists manifest-draft state, not data-tier state. Decided 2026-05-20 (ADR-082 §2a). **Done 2026-05-21** — three pure helpers (`_draft_key`, `_write_bp_draft`, `_read_bp_draft`) in `blueprint_handlers.py`; one `@reactive.Effect` `_autosave_blueprint_draft` watches `logic_stack` and writes atomic JSON ghost to `user_sessions/_blueprint_drafts/`; restore in `_update_dataset_pipelines` (SHA256 guard — discards draft if manifest changed); `bp_draft_status_ui` timestamp badge in sidebar; gated on `automation.ghost_save.enabled` (disabled for qa persona, deterministic tests unaffected).
- [x] **BP-BRANCH-NODE-1** `[opus/high]` (was BP-FORK-FILES-1): Implement node-level **lineage bifurcation** (ADR-082 Q3, LOCKED). User picks a bifurcation node → BLUEPRINT creates a new divergent downstream fragment that **references shared upstream** and wires it into the master via `!include`. Canonical pattern: `Summary` / `Summary_quality`. Replaces the Visual Fork append-into-manifest behaviour. Whole-manifest duplication is a separate rare path (BP-DUPLICATE-1, deferred). **DONE 2026-05-21.** UX decisions (with Eve): bifurcation point = the **selected node** (no DAG auto-detect); divergent fragments seed **empty** (no prefill) — matches the Tier-1-shared / Tier-2-diverges mental model and the canonical `Summary_quality` (empty wrangling, own output_fields). Replaced `generate_fork_yaml` with pure `generate_branch_plan(master_path, schema_id, role, new_id)` in `manifest_navigator.py`: reads master with a non-resolving loader (preserves `!include` as strings), shares `source`+`input_fields` (data_schema) / `ingredients` (join) / `target_dataset` (plot) by reference, writes new empty `wrangling`+`output_fields` / `recipe`+`output_fields` fragments (plot copies spec — a leaf must render), and inserts the new master block by **text-level insertion** that leaves every existing `!include` untouched. Handler reworked (`bp_branch_ui`/`bp_branch_preview_ui`/`_handle_branch_preview`/`_handle_branch_write`/`_write_branch_plan`/`_clear_branch_preview_on_node_change`) — **now works WITH `!include` manifests** (old fork refused them); `_write_branch_plan` validates YAML, refuses to clobber existing fragments, rolls back on failure. UI card "Fork Node"→"Branch Node". Verified: headless `generate_branch_plan` (3 roles + error cases + full ConfigManager re-parse confirming `Summary_v2.input_fields == Summary.input_fields`), `server` import OK, `build_dep_graph` regenerated, BLUEPRINT Playwright smoke 12/12. **Deferred v2:** sharing the original's Tier 1 by sub-`!include` so a branch reuses the trunk's tier1 and only authors a new tier2 (Eve's "split & concatenate tiers" idea — not needed for the shallow branching expected now).

- [ ] **BP-BRANCH-UX-1** `[haiku/low]`: Add a contextual guidance note in `bp_branch_ui` (`blueprint_handlers.py`) when a `data_schema` node is selected. The note should explain: branching a `data_schema` is only appropriate when you genuinely need to split raw data into two *distinct processing units* (e.g., different QC thresholds on the same raw file, splitting results by instrument type, applying different reference databases to the same raw sequences — cases where the two halves diverge from raw input and follow entirely different paths). For most analytical variations (different aggregations, different visualizations, different filters of the same processed data), it is **better practice to branch at the assembly (`join`) or plot level**: those branches share the materialized Tier 1 anchor parquet at runtime with zero recompute, while data_schema branches each trigger a full independent assembly. Style: small `ui.div` callout with `#6c757d` muted text, `0.78rem` sub-secondary typography, no icon.

### Phase 33 — Blueprint AI Agent MVP-1 (ADR-076)

> **2026-05-21 @sync verification.** All 6 open tasks were already fully implemented (shipped with ADR-076 MVP-1, archived 2026-05-09 — but tasks were not marked done at the time). Verified 2026-05-21: all agent modules import clean, 3 tools dispatch correctly (51 actions returned at runtime), `blueprint_agent_chat` registered in sidebar registry + `blueprint_standard_right.yaml`, chat panel + send effect + tool-call loop in `blueprint_handlers.py`, `.bp-agent-*` CSS block in `theme.css`, system prompt at `config/ui/agents/blueprint_default.md` (156 lines).

- [x] **BP-AGENT-PARSER-1** `[sonnet/medium]`: Fenced-block extractor (`agent_tool_parser.py`) — parse structured tool-call blocks from agent text output. Spec: ADR-076, implementation plan §Phase 33, step 33-C. **Done (found 2026-05-21 @sync).**
- [x] **BP-AGENT-TOOLS-1** `[sonnet/medium]`: 3 MVP tools for the agent — `get_available_actions`, `get_available_components`, `get_field_contract`. Spec: ADR-076, step 33-D. **Done (found 2026-05-21 @sync).**
- [x] **BP-AGENT-INSTRUCT-1** `[sonnet/medium]`: System prompt file `config/ui/agents/blueprint_default.md`. Spec: ADR-076, step 33-E. **Done (found 2026-05-21 @sync).**
- [x] **BP-AGENT-PANEL-1** `[haiku/low]`: Register `blueprint_agent_chat` panel in sidebar registry + persona templates. Spec: ADR-076, step 33-F. **Done (found 2026-05-21 @sync).**
- [x] **BP-AGENT-UI-1** `[sonnet/medium]`: Chat panel render outputs in `app/handlers/blueprint_handlers.py`. Spec: ADR-076, step 33-G. **Done (found 2026-05-21 @sync).**
- [x] **BP-AGENT-CSS-1** `[haiku/low]`: `.bp-agent-*` CSS rule block in `config/ui/theme.css`. Spec: ADR-076 + `rules_css_style_spec.md §5` (Chat/Conversational Panel Pattern). **Done (found 2026-05-21 @sync).**

### Audit script fixes

- [x] **MANIFEST-INCLUDE-1** `[sonnet/low]`: Fixed `libs/transformer/tests/debug_assembler.py` — replaced two-pass `yaml.safe_load` + conditional `ConfigManager` pattern with a detection-based approach: read manifest text, use `ConfigManager` when `!include` present (pipeline manifests), `yaml.safe_load` otherwise (partial test manifests). Avoids triggering `ConfigManager`'s `sys.exit()` path for partial manifests. Verified: `audit_manifest_integrity.py` now reports 6/6 PASS (was all FAIL). Other files verified exempt: `debug_runner.py` already uses ConfigManager with safe_load fallback; `gallery_manager.py`, `generate_previews.py`, `debug_gallery_submission.py` load gallery recipe manifests (standalone, no `!include`). **Done 2026-05-21.**

---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] Can we leverage python great docs to improve the documentation? particularly for the UI - but also for the rest of the libraries and for developers? <>https://github.com/posit-dev/great-docs>

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law. Decision needed: scope and migration plan before touching live handlers. [Not sure if wrong — it's part of the app itself]

- [ ] **LAB-WORKFLOW-1** `[opus/high]`: Collect all developer workflow info from Test Lab, Blueprint, and Gallery into a coherent end-to-end developer workflow. Needs dedicated design session before implementation.
- [ ] **UX-APPLY-IMPROVE-1** `[sonnet/medium]`: Audit Apply improvement — "apply to all except…" selection-by-exclusion mode. Needs design pass before scoping.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR before implementation.

---

## ⏳ Deferred / Blocked

### Blocked by library limitations

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — library limitation]`: Register `geom_map` component in VizFactory. Blocked: plotnine has no native GeoDataFrame/spatial support; requires geopandas integration and a spatial manifest format design. Unblocks: GALLERY-MAP.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred — library limitation]`: Map chart types in Gallery. Blocked by VIZ-GEOM-MAP-1.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[deferred — library limitation]`: Flow / network chart types. Blocked: plotnine has no native network/Sankey/flow support. Requires feasibility study — candidate libs: `networkx` + custom geom, or external renderer.

### Blocked by other tasks

- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.

### Planned / Large-scale backlog

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).
- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — manifest hashes + data hashes in DB; LIMS link in audit report; configurable output path per persona.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.
- [ ] **UX-DEVINSP-1** `[sonnet/medium]`: Test Lab right sidebar + left sidebar redesign — functionality TBD.

### Legacy removal (tracked per rules_legacy_management.md §6)
> Protocol: dep-sweep → impact assessment → migration path → code removal → test sweep → doc consistency sweep → ADR record.
> All 7 steps required before a task is [DONE].

- [ ] **LEGACY-FLAT-PLOTS-1** `[sonnet/medium]`: Full removal of flat `plots:` authoring key.
  - **Dep sweep:** `grep -rn "\.get\('plots'" libs/ app/` — known hits: `config_loader.py:160,163,173,184`, `viz_factory.py:92,106`, `blueprint_mapper.py:195,200,208,212,421`
  - **Code:** Remove root-level `plots:` init in `config_loader.py`. Add `ConfigurationError` if `plots:` found at manifest root (not inside `analysis_groups`). Update VizFactory to read exclusively from the post-ConfigManager flattened dict, not from raw manifest.
  - **Tests:** `grep -rn "plots" libs/utils/tests/ libs/viz_factory/tests/` — remove any tests using flat `plots:` as authoring input; add error-path test.
  - **Doc sweep:** `rules_manifest_structure.md`, `docs/appendix/manifest_structure.yaml`, `docs/appendix/Standards_yaml.qmd`, `libs/utils/README.md`, `libs/viz_factory/README.md` — update tombstones to REMOVED.
  - **Gate:** `grep -rn "^plots:" config/manifests/` = zero hits. Full test suite passes.

- [ ] **LEGACY-AUDIT-FLAG-1** `[haiku/low]`: Full removal of `audit_report_enabled` flag.
  - **Dep sweep:** Known hits: `persona_validator.py:27,41,124`, `bootloader.py:441`, `test_persona_validator.py`, all 8 `config/ui/templates/*_template.yaml`
  - **Code:** Remove from `persona_validator.py` known-flags list and cascade check. Remove from `bootloader.py` interactivity cascade. Remove key from all 8 template YAMLs.
  - **Tests:** Update `test_persona_validator.py` — remove the `audit_report_enabled=True` cascade test (lines 147–152); confirm remaining tests still pass.
  - **Doc sweep:** `rules_persona_feature_flags.md` flag table, `ui_implementation_contract.md` §7.2 and §12f, `docs/workflows/ui_persona.qmd` if referenced — convert DEPRECATED markers to REMOVED tombstones with expiry Phase 35.
  - **ADR:** Note removal in ADR or session log.
  - **Gate:** `grep -rn "audit_report_enabled" app/ config/` = zero hits. Full test suite passes.

- [ ] **LEGACY-TYPE-ALIASES-1** `[sonnet/low]`: Remove deprecated type aliases `character` / `string` (→ `categorical`).
  - **Dep sweep:** `grep -rn "\"character\"\|\"string\"\|'character'\|'string'" libs/ingestion/ libs/transformer/ libs/utils/` — confirm exactly where aliases are accepted (may be ingestion schema validator or config_loader type coercion).
  - **Manifest scan:** `grep -rn "type: character\|type: string" config/manifests/` — if any hits, migrate them first before removing engine support.
  - **Code:** Remove alias acceptance. Raise `ConfigurationError`: `"Type 'character' is deprecated — use 'categorical'. See rules_manifest_structure.md §9."`.
  - **Tests:** Add error-path test for deprecated alias.
  - **Doc sweep:** `docs/appendix/Standards_yaml.qmd` DEPRECATED banner → REMOVED tombstone. `rules_manifest_structure.md §9`. Any README mentioning type values.
  - **Gate:** `grep -rn "type: character\|type: string" config/` = zero hits. Engine raises error on alias. Test suite passes.

- [ ] **LEGACY-FLAT-WRANGLING-1** `[sonnet/low]`: Remove engine acceptance of flat `wrangling: []` list.
  - **Dep sweep:** `grep -rn "wrangling" libs/transformer/src/ libs/utils/src/` — find exactly where flat list is tolerated vs tiered structure enforced.
  - **Manifest scan:** `grep -rn "^wrangling:" config/manifests/` — any flat (non-tiered) wrangling blocks must be migrated first. Run `debug_assembler.py` to verify after migration.
  - **Code:** Remove flat-list tolerance. Raise `ConfigurationError`: `"Flat 'wrangling:' list is deprecated — use tiered structure with 'tier1:' / 'tier2:'. See rules_data_engine.md §3."`.
  - **Tests:** Remove any tests using flat wrangling as valid input; add error-path test.
  - **Doc sweep:** `docs/appendix/Standards_yaml.qmd` DEPRECATED banner → REMOVED tombstone. `rules_data_engine.md §3` proactive-refactoring note → update to say engine rejects flat lists. `docs/appendix/manifest_structure.yaml`.
  - **Gate:** `grep -rn "^  wrangling:\s*\[" config/` = zero hits. Engine rejects flat lists. Test suite passes.

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
- [x] **BP-ADR-FULL-1** (ADR-082) — **RESOLVED 2026-05-20.** All 7 decision points settled with Eve; **ADR-082 (BLUEPRINT Full Feature Set & Build-Mode Contract)** authored in `architecture_decisions.md`. Research draft marked RESOLVED. Spawned Phase 32 (cont.) task slate above.

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
| May-11 hygiene | Doc/ADR/lib-test audit fixes, Blueprint IDE features, ADR-079 design, cascade design, T3 threading, repo hygiene | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-11 session | BP-LINEAGE-NAV-1, GALLERY-CLONE-DECOUPLE-1, VIZFAC-RESOLVER-1, DIAG-RUNTIME-BASE-1 + full audit (EMOJI-DOCSTRING-1, VIZ-README-COUNT-1) | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-12 hygiene | Audit script fixes (CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1) | 2026-05-12 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |

---

## 📋 Session Notes

Context and status notes from recent sessions. Add here instead of inside active task sections.

- **2026-05-21 (@sync — Phase 33 / BP-BRANCH-NODE-1)** — BP-BRANCH-NODE-1 completed and committed (`99e6b19`). Also discovered all 6 Phase 33 tasks (BP-AGENT-PARSER-1 through BP-AGENT-CSS-1) were already fully implemented (shipped 2026-05-09, tasks not marked done). Verified headless: all agent modules import OK, 3 tools dispatch (51 actions at runtime), sidebar registration + persona templates + CSS all in place. Marked done. Added BP-BRANCH-UX-1 (data_schema branch guidance callout).
- **2026-05-21 (BP-JOINT-1 — Joint Designer pane)** — Implemented the dedicated Joint Designer (ADR-082 Q5). New pure stdlib module `libs/blueprint_arch/src/blueprint_arch/join_designer.py` (`compute_key_match` real-overlap stats incl. composite keys + dtype-family advisory; `build_join_step` sym `on` / asym `left_on`+`right_on`, scalar-vs-list; `parse_join_step` inverse w/ YAML boolean-trap guard) + 26 unit tests (all pass). New `4. Joint Designer` nav_panel in `wrangle_studio.render_ui`. Wiring in `blueprint_handlers.define_server`: R4-safe ingredient/key pickers, **real-data** preview (materialises each ingredient via `orchestrator.materialize_tier1`, String-cast key overlap mirroring the assembler), comment-gated Apply → logic_stack append/replace, edit pre-fill on join-node select. Removed the fabricated `show_join_modal`/`confirm_join`/`update_secondary_datasets` + dead picker selectors (clean break, no orphaned refs). Verified: 26/26 logic tests, both app modules import clean. Decisions taken with Eve: center pane · real-data overlap · composite/multi-key · edit+create. **Follow-up:** join-component Save (`_serialise_component_for_save` role `join`) must quote `on:` (pre-existing gap — join-role save not yet implemented). **Live UI smoke pending → BP-SMOKE-1** (no BLUEPRINT Playwright infra yet). Session triage: 3 audit reports PROCESSED (coherence PASS 6/6, integrity FAIL = known MANIFEST-INCLUDE-1 false positive, 1 narrative log).
- **2026-05-20 (BLUEPRINT feature lock)** — Verified BP-FORMS-1 against the running implementation: all 60 transformer action forms render headless (zero failures, all 8 widget types). Found the form layer is half-built (add-node primitive vs edit-node rich; no component form path; 7/191 components schemed) + 2 ADR-075 widget gaps (enum preview, expression editor). Authored **ADR-082 (BLUEPRINT Full Feature Set & Build-Mode Contract)** — locked 4-layer model, 7 decision points, MVP/v2 inventory, T1/T2-vs-T3 boundary. Key decision with Eve: **branch = node-level lineage bifurcation** (shared upstream by reference, divergent downstream fragment-per-component `!include`) — NOT whole-manifest duplication; terminology fix (graph fan-out ≠ manifest branch). Spawned 12 Phase 32 (cont.) tasks. Research draft → RESOLVED.
- **2026-05-20** — Triaged 11 unprocessed audit files from 2026-05-13/18. 10 PASS (marked PROCESSED). 1 actionable finding: `audit_manifest_integrity.py` reports 6/6 manifests FAIL because `debug_assembler.py` uses `yaml.safe_load()` — `!include` not supported. All manifests are structurally fine (coherence audit PASS). Task added: MANIFEST-INCLUDE-1 in Do Now.
- **2026-05-12** — All recent work (CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1, EMOJI-DOCSTRING-1, VIZ-README-COUNT-1) archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md).

---

## Archive Pointers

- [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) — May-11/12: full audit batch + CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1, EMOJI-DOCSTRING-1, VIZ-README-COUNT-1
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
