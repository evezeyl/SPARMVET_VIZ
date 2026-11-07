# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-22 (Phase 34 + BP-HELP sweep + audit fixes + legacy removal archived; tasks hygiene) by @dasharch

---

## Task Organization Protocol (read before adding or moving items)

| Section | What belongs here |
|---|---|
| **🟢 Do Now** | Immediately actionable — no blocker, no design decision pending. Audit-detected problems that need no user discussion go **at the top of this section**, above all other items. |
| **🤔 Needs Discussion / Decision** | Requires a design pass, ADR authoring, or explicit scoping before any code. No implementation until resolved. |
| **⏳ Deferred / Blocked** | Blocked by library limitation, another task, or large-scale planned work. Sub-group by what is blocking. |
| **🟡 Bio-Scientist Enhancements** | `[ENHANCEMENT REQUEST]` items from data analysis recipe design sessions only (see `rules_agent_role_bioscientist.md §4-A`). |
| **👤 User Required** | Needs user action, decision, or explicit discussion. No agent progress until user responds. |

**Rules for keeping the file clean:**
- **Empty sections stay empty.** If Do Now has no items, leave it blank — no placeholder text, no status lines.
- **`> Completed:` / `> Status: COMPLETED` inline pointers inside sections are FORBIDDEN.** When items are done, move them to the archive file and update the archive table + pointers at the bottom.
- **Context and session notes go at the bottom** — in the `## 📋 Session Notes` section, not inside active task sections.

---

## 🟢 Do Now

Items with no blockers — can be started immediately.

### Audit Fixes — ADR Compliance (ADR behavioural audit 2026-11-06)

- [x] **ADR-045-PLOTERR-1** `[AUDIT]` `[sonnet/low]`: `architect_active_plot` (`@render.plot`, `app/modules/wrangle_studio.py` lines 552-607) calls `_plot_error.set(...)` six times. This breaks the reactive write rule R1 (`ui_implementation_contract.md §14`): renders are read-only. Fix: compute the error text in a `@reactive.Calc` (or write it from a `@reactive.Effect` with an idempotent guard) and let the render only read it. Affects BLUEPRINT (demo scope). Add a Playwright or unit check that the Blueprint plot still shows its error banner. DONE 2026-11-06: the error text is computed in the `_plot_outcome` Calc; `app/tests/test_render_purity.py` fails if any render in `app/` writes a reactive value. The error banner itself is not covered by an automated test (check by hand in BLUEPRINT).
- [x] **ADR-045-SERVER-SIZE-1** `[AUDIT]` `[sonnet/medium]`: `app/src/server.py` has 287 lines; `rules_app_structure.md §3` sets a hard limit of ~250. Find what is not shared state, a shared calc or a `define_server` call, and move it to a handler or module. DONE 2026-11-06: the excess was dead code (`tier_reference`, `tier3_leaf`, `apply_tier2_transforms` and the unmounted outputs `plot_reference`, `table_reference`, `plot_leaf`, `table_leaf`, `handle_plot_brush`), removed; `server.py` is 237 lines.

### Clean-up recheck 2026-11-06 (dead code, old tests, documentation)

Done 2026-11-06: removed `lookup.py` (`lookup_anchor_rows`), `DataWrangler.run_tier1/run_tier2`, `peek_data_analysis_recipe`, the `placeholder/` folders of `ingestion` and `transformer`, unused imports, `test_reactive_shell.py`, the app features benchmark scripts, and the broken `test_lab` demos (`debug_sdk`, `debug_ambiguity`, `debug_reconciler`, `demo_reconciler`; covered by `libs/id_reconciliation/tests`, `test_synthesizer`, `test_bootstrapper`, new `test_extractor`). Repaired `debug_pipeline_connector.py`, `debug_pipeline.py` + `PipelineExecutor` (tiered data analysis recipes, `join_id`), `libs/viz_gallery/tests/debug_gallery_submission.py`. The `generator_utils` name is gone from deployments and docs. Headless baseline: 1197 passed.

- [ ] **DEAD-CODE-REVIEW-1** `[sonnet/medium]`: each item below has no caller in `app/`, `libs/`, `assets/scripts/` or `scripts/` (scan 2026-11-06). Do the dependency sweep of `rules_legacy_management.md` §6 for each, then delete or keep with a reason. Some are unfinished features, ask Eve first for those marked (?).
  - `app/handlers/blueprint_handlers.py:203 _undo` (?), `app/modules/wrangle_studio.py` `_fields_table`, `_parse_fields_safe` (cited in ADR text and the UX spec), `app/modules/help_registry.py` (`help_registry_ui`, `help_registry_server`: whole module unused?) (?)
  - `app/modules/exporter.py` `bundle_package`, `render_audit_report` (the Export Audit Report button was removed 2026-05-04), `app/modules/gallery_viewer.py` `submission_modal_ui`, `autofill_meta_from_audit` (gallery submission, check against GALLERY plans) (?)
  - `app/src/bootloader.py` `get_script_path`, `get_python_path` (the `scripts:` block of the deployments exists only for these), `app/src/render/pipeline_error_renderers.py` `dispatch_pipeline_error`, `libs/utils/src/utils/debug_output.py` `get_debug_out_dir`
  - `libs/ingestion/.../ingestor.py` `validate_schema`, `libs/id_reconciliation/.../core.py` `suggest_patterns`, `libs/viz_gallery/.../gallery_manager.py` `list_submissions`, `rebuild_index`, `libs/connector/.../galaxy_connector.py` (`fetch_history_dataset`, `list_histories`: Galaxy plans) (?)
  - `libs/blueprint_arch/.../agent_adapter.py`, `agent_context.py`, `agent_tool_parser.py` (ADR-076 AI agent, not wired yet) (?)
- [ ] **DOC-RECHECK-2** `[sonnet/medium]`: still to do after the 2026-11-06 pass. (1) "Comparison Theater" wording (`docs/index.qmd`, `docs/appendix/data_lifecycle_theater.qmd`, `docs/workflows/visualisation_factory.qmd`, `docs/reference/ui_style_guide.qmd`, `Terminology.qmd`) to the ADR-086 terms ("Compare Result vs My view"). (2) `docs/vision/platform_evolution.qmd` still shows `joins` (vision document: mark HISTORICAL or update). (3) `.claude/design/ui_panel_map_current.md`, `export_specification.md` still say "Global Export" (design records: add a HISTORICAL note). (4) `project_conventions.md` §E says the plot config cascade is "not yet implemented" but `rules_viz_factory.md` lists the resolver and render wiring as done. (5) DOC-GAP-2, 3 and 5 from May (app features matrix rows, ADR-074 note in the deployment guide, README claims about `ExcelHandler` and "Comparison Theater"). (6) `docs/_freeze/` is generated output with old text: re-render or ignore. (7) Run the legacy audit greps of `rules_legacy_management.md` §5.
- [ ] **AUDIT-GATE-UI-1** `[sonnet/medium]`: a Playwright test of the Apply gate: add a T3 node without a reason, the button reads "Apply ⛔" and shows the blocked count; add the reason, it reads "Apply". Replaces the removed `test_reactive_shell.py::test_reactive_audit_gate` (the gate logic itself is covered by `test_session_manager.py::test_gatekeeper_blocked`).
- [ ] **VALIDATE-UI-1** `[sonnet/medium]`: issue #26 (Eve 2026-11-06: a BLUEPRINT button is needed before the demo). `validate_data_analysis_recipe_data()` (issue #18) has no screen yet, only tests. Add the BLUEPRINT "Validate data analysis recipe" action (BP-VALIDATE-1), also run on data analysis recipe upload.

### Export consistency (the export holds the Result plus the audited steps; exploration is never exported), added 2026-11-06

Done 2026-11-06 (issue #10): export reads T1 and T2 through the key-checked orchestrator, renders plots from T2 (as HOME), records data analysis recipe file-set hash, data hash and the Tier 1/Tier 2 keys in README, `report.qmd` and PNG/SVG metadata. Headless tests: `app/tests/test_export_provenance.py`, `app/tests/test_tier2_store.py`.

- [ ] **EXPORT-CHECK-1** `[sonnet/medium]`: Export test by hand in the app. Automated since 2026-11-06 (`app/tests/test_export_download.py`, real download in the qa app features): keys recorded in README (points 3), data files exist, no `_ERROR.txt`, no My view content on Result (7 partly), export refused after a data change. Still by hand: points 1, 2 (compare with the screen), 4-6, 8, 9. What to look for, with the data analysis recipe and a data analysis recipe with a `tier2` step:
  1. Plot in the bundle equals the plot in HOME "Result (T2)": same rows, same picture. With a `tier2` step the bundle plot must NOT look like T1.
  2. `data/<ds>/T1_data.tsv` equals the Raw view; `T2_data.tsv` exists only when the join has `tier2` steps and equals the Result view (row count, columns).
  3. README and `report.qmd` show: data analysis recipe SHA256 (file set), data batch hash, `tier1_key` and `tier2_key` per dataset ("none (T2 equals T1)" when no tier2). The PNG metadata has `sparmvet:tier1_key` / `tier2_key`.
  4. Same keys as the stored parquet files (`sparmvet_tier1_key`, `sparmvet_tier2_key` in the metadata of `anchors/*.parquet`).
  5. Change one thing and export again: a Tier 2 step (only tier2_key changes, plot changes), an included file (tier1_key and data analysis recipe hash change), a data file (data hash and tier1_key change). Nothing exported may come from before the change.
  6. Move a step from tier2 to tier1, export: no `T2_data.tsv`, no `anchors/<ds>__T2.parquet` left.
  7. Exploration filters (Apply, not sent to audit): never in the bundle, from any view; audited steps: always (see RT-15 to RT-17).
  8. App features without `interactivity_enabled` (pipeline-static): export works and shows the Result.
  9. Edge: join with no tier2 steps; data analysis recipe with two datasets (each its own keys); a failing plot writes an `_ERROR.txt` and the other plots are still exported.
- [x] **EXPORT-KEYCHECK-1** `[opus/high]` (done 2026-11-06, Eve: block, never better safe than sorry): the export compares the keys the open view was built on with the keys now. If the data analysis recipe (any file) or the data changed, nothing is exported: an error notification explains it and the download holds only `EXPORT_NOT_CREATED.txt` (what it means, reload with F5, check, export again, both sets of keys). Tests: `test_export_view_consistency.py`, `test_export_download.py`.
- [x] **EXPORT-T3-1** `[sonnet/medium]` (done 2026-11-06, corrected after Eve's clarification, issue #25): build rule T3 > T2 > T1 (stored Tier 2, which is Tier 1 without tier2 steps). The export is the Result plus the AUDITED T3 steps (rows, drops, aesthetic overrides, trail), always applied to the exported plot and its data; exploration (filters tried in T1/T2/My view, not sent to audit) is a sandbox and is never exported, from any view (no checkbox, no `FILTERS.txt`). T3 data is one file per plot with audited steps (`T3_data_<plot>.tsv`), built by `audited_frame`. `tier3_leaf` is gone (ADR-045-SERVER-SIZE-1). Still open: a hash of the audit steps in the report.

- [x] **EXPORT-T3-UX-1** (decided 2026-11-06, Eve): no message about left-out T3 steps is needed, because audited steps are never left out. What is not audited is a sandbox: a reminder says so (Export panel, and under the filter buttons in My view). Done in issue #25.

### Configuration vocabulary and launch variables (ADR-091, proposed 2026-11-07, revised: one pass, no hybrid)

Names agreed: `deployment` (`SPARMVET_DEPLOYMENT`), `app features` (`SPARMVET_APP_FEATURES`), `data analysis recipe` (`SPARMVET_DATA_ANALYSIS_RECIPE`, today still called data analysis recipe). "App features" is retired for the application; it stays only for the two AI agent files. Everything with an old word (folders, files, classes, keys, labels, docs, tests) is renamed in ONE scripted run; a hybrid state must not reach a shared branch. Issue: evezeyl/SPARMVET_VIZ#27 (IRIDA check: #28). Implementation plan: `.claude/tasks/config_rename_strategy.md`.

- [x] **CONFIG-VOCAB-REVIEW-1** (done 2026-11-07, decisions in ADR-091) `[opus/high]`: Eve reviews ADR-091 and the issue draft and decides open points 1 to 5 of the ADR (key renames, launcher, operator lock, "agent role" wording, IRIDA check). Issue #27 is created.
- [x] **CONFIG-INVENTORY-1** (done 2026-11-07) `[sonnet/medium]`: read-only inventory of every key in `config/deployment/*` and `config/app_features/*` (used / unused / wrong home, with the line that reads it), output in `.claude/logs/`; Eve reviews. Depends: CONFIG-VOCAB-REVIEW-1.
- [x] **CONFIG-MAPPING-1** (done 2026-11-07, rules and table in assets/scripts/rename_vocabulary*) `[sonnet/high]`: script output of every word, path and key containing app features, data analysis recipe or step list, with meaning and new name; Eve approves. Depends: CONFIG-INVENTORY-1.
- [x] **CONFIG-RENAME-1** (done on branch rename/config-vocabulary 2026-11-07, merge after the retest) `[sonnet/high]`: dry run, real run with `git mv`, startup errors for old variables and keys, `default_data_analysis_recipe` takes effect, `~` and `${VAR}` expansion, delete `logic_access`, `app_features_name`, `data_import_panel_visible` (absorbs LEGACY-DATAIMPORT-FLAG-1), migration script for files and sessions, old-words audit added to the audit registry, docs and launch commands updated. Depends: CONFIG-MAPPING-1.
- [x] **CONFIG-PROJECT-WORD-1** (done 2026-11-07) audit:allow-old-word (issue evezeyl/SPARMVET_VIZ#29, mapping in `.claude/tasks/project_word_mapping.md`) `[sonnet/high]`: one name for the recipe, no "project" for it; Info panel shows `info:`; remove recipe `type:`; "Deployment palette"; `standalone` -> `standalone`; rewrite Terminology.qmd. Gate: retest of #27 done or folded in.
- [x] **CONFIG-BLUEPRINT-FLAG-1** (done 2026-11-07, ADR-092, issue evezeyl/SPARMVET_VIZ#30) `[sonnet/high]`: `blueprint_enabled` alone controls the Blueprint Architect; `developer_mode_enabled` and `wrangle_studio_enabled` retired; blank page of standalone and advanced fixed.
- [x] **CONFIG-DATA-ANALYSIS-RECIPE-ID-1** (done 2026-11-07, ADR-092, issue evezeyl/SPARMVET_VIZ#31) `[sonnet/medium]`: the `id:` key equals the file name; validator, test, rule, files corrected.
- [ ] **CONFIG-TESTLAB-DATA-ANALYSIS-RECIPE-CHOICE-1** (issue evezeyl/SPARMVET_VIZ#33) `[sonnet/medium]`: investigate. The Test Lab left panel lists the panels `Info` and `Data analysis recipe Choice` (sidebar file `config/ui/sidebars/testlab_standard_left.yaml`), although the Test Lab tools do not use the open data analysis recipe. Decide with Eve: keep (context), keep only Info, or remove; check the same for Gallery and Blueprint sidebars; update the sidebar files and `ui_implementation_contract.md` §11.
- [ ] **CONFIG-BLUEPRINT-ID-DISPLAY-1** (issue evezeyl/SPARMVET_VIZ#34) `[sonnet/low]`: the Blueprint selector ("Master Data Analysis Recipe") lists file paths (`config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml`) while the Home selector lists ids. Show the data analysis recipe id (file name) in both, keep the path as the value.
- [x] **CONFIG-AUDIT-FIXES-1** (done 2026-11-07, steps 1 to 7, issue evezeyl/SPARMVET_VIZ#32) `[sonnet/medium]`: plan in `.claude/tasks/audit_findings_2026-11-07.md` (the failures of the scheduled audits that the rename did not cause: missing `@deps` block, placeholder paths in docs, stale Violet Law references, missing `rules_toolchain.md`, `complex_template` that does not load, no load test of templates).
- [ ] **DEPS-REVIEW-1** (issue evezeyl/SPARMVET_VIZ#35) `[opus/medium]`: 61 outdated packages, 11 major (polars 1.40 to 2.1, pyarrow 24 to 26, pillow 12 to 13 ...) from `audit_package_deps.py`. Polars 2 first: ADR-035 parity audit of `libs/transformer/src/transformer/actions/`, run the full suites on a branch, then the others.
- [x] **ADR-037-GAP-1** (done 2026-11-07, finding F-21, `.claude/tasks/uml_findings.md`; found by `assets/scripts/audit_uml_model.py`'s first run) `[sonnet/low]`: "ADR-037" was cited in 4 places for the Gallery index-only-filtering rule with no `## ADR-037` heading ever written (git history traces the dangling citation to commit `cdb2b7a`, 2026-04-19). Wrote the missing entry from the already-consistent citing text.
- [x] **CONFIG-GHOST-DOC-1** (done 2026-11-07: user_preferences.qmd describes the event-driven saving) `[sonnet/low]`: `docs/workflows/user_preferences.qmd` (Quarto page) promises a debounced autosave every 2 minutes (`ghost_save_trigger`) that was never built; the saving is event-driven (Apply, leaving Home, assembly). Correct the page, delete `ghost_save.frequency_minutes`. Part of the docs phase.
- [ ] **CONFIG-AGENT-BACKENDS-1** `[opus/medium]`: implement the `claude_api` and `local` backends of the BLUEPRINT agent (ADR-076 phase 2); until then `blueprint_agent.model`, `.endpoint`, `.api_key_env`, `.gallery_awareness` stay in the templates marked "reserved, not implemented".
- [x] **CONFIG-SETTINGS-CLEAN-1** (done 2026-11-07) `[haiku/low]`: remove the stale allow-list entries (old commands and paths) from `.claude/settings.json`; review the diff.
- [ ] **CONFIG-STEPS-WRITE-1** `[sonnet/high]`: BLUEPRINT writes into the step lists location while the deployment guide says it is read-only, and overwrites files in place. Interim: warning and timestamped backup before overwriting. Target: BLUEPRINT edits a draft copy in `user_data`, validation (#26) runs on it, an explicit publish copies it into the step lists location; the location can stay read-only in production. See ADR-091 gaps. Depends: #26.
- [ ] **CONFIG-APP-RESOURCES-1** `[opus/high]`: application resources (app features folder, `theme.css`, sidebars, development fallback) are found relative to the working directory; locate them from the code root so a container or an installed copy works. Design first, see ADR-091 gaps. Depends: CONFIG-RENAME-1 (new folder names).
- [x] **CONFIG-BRANDING-1** (done 2026-11-07 (branding block in the deployment file)) `[sonnet/medium]`: move `theme_css` and the banner (`logo_url`, title) from the app features files to a `branding:` block in the deployment file; the base stylesheet always loads from the code root and the deployment stylesheet holds only the differences. Behaviour phase of the rename (phase 9), with an error for the old keys.
- [ ] **CONFIG-CACHE-LOCATION-1** `[sonnet/high]`: the deployment location `cache` (formerly `curated_data`, documented as the place of the Tier 1 and Tier 2 parquet caches) is required by the bootloader but read by no code; the anchors are written under `user_data/anchors/` instead. Decide: use `cache` for the anchors (cache is rebuildable, user data is work) or drop the location. Found in phase 5 of the rename. BLUEPRINT drafts already live in `user_data/_blueprint_drafts` (see CONFIG-STEPS-WRITE-1).
- [ ] **CONFIG-IRIDA-CHECK-1** (evezeyl/SPARMVET_VIZ#28) `[opus/medium]`: check ADR-048's IRIDA token assumption with someone who knows IRIDA before the IRIDA connector is built.

### LAB-WORKFLOW follow-up

- [ ] **LAB-WORKFLOW-QMD-1** `[sonnet/low]` `[doc-sync]`: User-facing Quarto mirror of `developer_workflow.md` in `docs/workflows/` — explains the *logic* of the producer workflow for end users (DRY: link, do not duplicate per `rules_documentation_aesthetics.md §4`). Focus on workflow logic + module independence, not app mechanics. Can be written now (logic is settled).

### Maps — Solution A (choropleth via geom_polygon, no new deps)

> Design context: `.claude/design/maps_advanced_geo.md` (Solution B is the deferred geopandas path; A is this).
> Key fact (verified 2026-05-22): `geom_polygon`, `coord_equal`, `coord_fixed` are **already registered** in VizFactory. Solution A needs **no new viz component and no new dependency** — geometry is plain x/y/group numeric columns flowing through the existing tabular pipeline. ggplot2 analogue: `geom_polygon(aes(long, lat, group)) + map_data()`.

- [ ] **MAP-A-BOUNDARY-ASSET-1** `[sonnet/medium]`: Boundary-fortification asset script `assets/scripts/fortify_boundaries.py`. Pure-Python (json module only — **no geopandas/shapely**) GeoJSON → long-format Parquet with columns `region_id, region_name, poly_group, vertex_order, long, lat` (one row per polygon vertex; `poly_group` disambiguates multi-part regions and holes). `argparse` CLI per `rules_asset_scripts.md §2` (input GeoJSON path, output Parquet path, region-name property key — no hardcoded paths). Output to `assets/geo_boundaries/`.
  - Sub-step: source first boundary sets (Norway counties + Europe countries) from a public-domain provider (Natural Earth — public domain; **avoid GADM**, non-redistributable). Record provenance + licence in `assets/geo_boundaries/PROVENANCE.md`.
  - Verify: fortified Parquet round-trips to a plottable frame; vertex counts plausible; multi-part regions keep distinct `poly_group`.
- [ ] **MAP-A-DATA-ANALYSIS-RECIPE-PATTERN-1** `[sonnet/medium]`: Author one end-to-end choropleth data analysis recipe as the canonical pattern. Tier 1 join: analytical data (rate/count per region) → boundary Parquet on region key. Plot spec: `geom_polygon` with `mapping: {x: long, y: lat, group: poly_group, fill: <metric>}` + `coord_equal` + a continuous fill scale. Verify via `debug_assembler.py` then `debug_gallery.py`; route evidence to `tmp/<date>/<lineage_id>/` per `rules_agent_role_bioscientist.md §7`. Halt for `@verify`.
  - Watch: `group` must be the vertex `poly_group` (not region) or polygons cross-link; fill is per-region so the join must broadcast the metric to every vertex row.
- [ ] **MAP-A-GALLERY-1** `[sonnet/medium]`: Gallery bundle for the choropleth (Scientific Triplet + preview PNG per `rules_gallery_standards.md`). **Blocked on a taxonomy decision** (shared with Solution B open-question #3): choropleth `family` — extend `TAXONOMY_CHEATSHEET.md` with a spatial value, or fold into `Comparison`/`Distribution`? Resolve with Eve before authoring the `info:` block.
- [ ] **MAP-A-DOCS-1** `[haiku/low]` `[doc-sync]`: Document the choropleth pattern — `libs/viz_factory/README.md` (geom_polygon-as-map step list) + `docs/appendix/data_analysis_recipe_structure.yaml` (boundary-join + geom_polygon spec). DRY: link the design doc, do not duplicate.

> **Do NOT** uncomment `geom_map` at `geoms/core.py:822` for Solution A — that geom belongs to Solution B (needs the geo extra + a render branch; see design doc §11). Registering it now would expose a geom that errors on use.


---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Gallery keyword enrichment + AND/OR search. **Design settled (2026-05-22):** add `keywords: [list]` to `info:` block in each `data_analysis_recipe.yaml` (35 examples); update `refresh_gallery.py` to include keywords in `gallery_index.json` pivot entries; add a text search input to the Gallery UI (split on spaces → AND-intersect tokens across keywords + existing taxonomy fields). Three keyword layers: (1) statistical/methodological synonyms (`median`, `quartile`, `IQR`, `spread`, `beeswarm`, `ridge`, `dumbbell`, `before after`, `cumulative`, `paired`, `stacked`, `proportional`, `small multiples`, `faceted`, `overlay`, `individual points`, `raw data`, `regression`, `fit`, `confidence interval`…); (2) data/use-case terms (`time series`, `temporal`, `longitudinal`, `rate`, `prevalence`, `incidence`, `frequency`, `quality control`, `normality`, `heterogeneity`, `exploration`…); (3) domain terms (`AMR`, `antimicrobial`, `resistance`, `MIC`, `susceptibility`, `surveillance`, `epidemiology`, `pathogen`, `species comparison`…). No fuzzy matching needed — AND/OR on exact tokens is sufficient for this gallery size. Step 1: enrich all 35 example `info:` blocks. Step 2: one-line `refresh_gallery.py` change. Step 3: gallery UI search widget.

---

## ⏳ Deferred / Blocked

### Deferred by architecture choice (NOT hard library blocks — premises corrected 2026-05-22)

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — architecture choice, NOT a library block]`: Register `geom_map` (Solution B — real geo). Premise corrected 2026-05-22: plotnine 0.15.4 **does** ship `geom_map` (`REQUIRED_AES={'geometry'}`); not blocked by the library. Deferred because it needs geopandas/shapely + a geometry-aware data path. Full design: `.claude/design/maps_advanced_geo.md` (recommended sub-option B1 = sidecar GeoDataFrame merged at render time). Choropleths ship sooner via Solution A (`MAP-A-*`, Do Now) with zero new deps. Do not uncomment `geoms/core.py:822` until this is scheduled.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred]`: Map chart types in Gallery. Solution A choropleths arrive via `MAP-A-GALLERY-1`; advanced (projected/CRS) maps wait on VIZ-GEOM-MAP-1 / Solution B.
- [ ] **GALLERY-FLOW** `[opus/high]` `[deferred — needs layout-precompute helper, NOT a hard library block]`: Flow / network chart types. Premise corrected 2026-05-22: same pattern as maps — plotnine has no high-level `geom_sankey`/`geom_net`, but the **primitives exist and are registered** (`geom_segment`, `geom_path`, `geom_polygon`, `geom_rect`, `geom_ribbon`). Feasible by precomputing layout/flow coordinates into a tabular form, then drawing with existing geoms. Needs: (1) a layout/coordinate-precompute helper (network: node x/y + edge endpoints; Sankey: stage rects + ribbon polygon vertices via pure-Python sigmoid interpolation), (2) a decision on whether to add `networkx` (NOT installed) for graph layout or hand-roll with `scipy` (installed). Note: `geom_curve` is **absent** in plotnine 0.15.4 (use `geom_segment`/`geom_path`); `matplotlib.sankey.Sankey` exists but draws its own figure and breaks the grammar-of-graphics model (escape-hatch only, not preferred). Needs own design pass + ADR before scheduling.

### Blocked by other tasks

- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.

### Blocked until live app testing is finished (TOOLS / UML chain, added 2026-11-04)

Goal: this repo is self-contained. Every tool the agent needs to build the app is declared in the repo (not only in Eve's global `~/.claude/` setup), and architecture diagrams (UML / SysML / C4) live in the repo and are visible in the GitHub docs. Do ONE task at a time, in order; each ends with a halt for Eve. Eve's learning context: `my-mentoring` competencies DES-02..04 (offer Eve to draw parts herself).

- [x] **TOOLS-TOOLCHAIN-1** (done 2026-11-07: `.claude/rules/rules_toolchain.md`, linked from CLAUDE.md 3.2 and the master index) `[sonnet/low]`: Create `.claude/rules/rules_toolchain.md` = tools needed to build SPARMVET_VIZ (uv, `./.venv`, pytest, Playwright, Quarto, Mermaid CLI, podman/docker, git/gh, StarUML marked "pending TOOLS-UML-1"), with what each is for and how to call it. Link it from `CLAUDE.md` section 3.2 (rules table) and `workspace_standard.md` master index. Must not depend on `~/.claude/CLAUDE.md` or `my-mentoring/toolbox.md` (collaborators and CI do not have them). Personal tools (Gmail, Zotero, YouTrack, bio-research plugin) stay out. Done when: a fresh clone's agent can list the build tools from repo files alone.
- [x] **TOOLS-UML-1** (done 2026-11-07: shared tool in `OBSWORK/_bin/staruml/`, MCP servers `staruml` and `staruml-bridge` at user scope, not per repo) `[sonnet/medium]`: StarUML MCP setup. Depends on `[@user] TOOLS-UML-0` (licence decided and StarUML installed). Add repo `.mcp.json` entry for the StarUML MCP server, add `mcp__staruml__*` permissions to `.claude/settings.json`, update `rules_toolchain.md` (remove "pending"). Check first: StarUML >= 7.0.0 and Node >= 22 (Node 25 is installed); which MCP package is the official one (`staruml-mcp-server` listing vs community `staruml-mcp`); transport (stdio vs HTTP). Done when: agent can create one test element in a running StarUML and Eve sees it.
- [ ] **DEMO-USERS-1** `[sonnet/medium]`: functionality demo for users, most of them not developers (Eve, 2026-11-07; work on it after the fixes). Show the interface and what they can do: get the graphs, filter data, navigate the plots of one data analysis recipe, select another data analysis recipe and see the UI build itself. Briefly show what can be switched on and off: (1) fully static with a custom logo (`pipeline-static` plus a deployment with branding), (2) possibly a pipeline with some data exploration (`pipeline-exploration-simple`), (3) everything else, audit and so on, with the full configuration Eve uses for development (`developer`). A separate short demo for interested developers is possible. Check first that each of the three starts with the logo and data wanted.
- [ ] **DOCKER-RELEASE-1** `[sonnet/medium]`: later (Eve, 2026-11-07). There has been no Docker release yet. `assets/containers/Dockerfile` uses Python 3.12 while development is on 3.14 (finding F-19). Build and run the image, rootless, and add it to DEP-APP when it works.
- [ ] **HELP-FROM-DOCS-1** `[sonnet/medium]`: later (Eve, 2026-11-07). The help is not built yet; it is to be built from the documentation (there was an earlier discussion, find it first). `app/modules/help_registry.py` is imported by nothing today (finding F-20): wire it in or remove it as part of this.
- [ ] **SECURITY-DEPLOY-1** `[opus/high]`: think through security before official deployment (Eve, 2026-11-07). Start from: `eval` on data analysis recipe text (finding F-13, `expressions.py:221`, `geoms/core.py:1335`, `id_reconciliation/core.py:239`), no login in the app, session zip import, which paths a user can write, rootless container. Eve's starting point: who launches the app controls the paths, and a rootless container limits the damage. To check: on a shared server the browser user is not the person who launched it, and a data analysis recipe upload or BLUEPRINT would run code as the app's account, with access to all mounted data. Done when: a written threat model and a decision per point.
- [ ] **TOOLS-UML-4** `[sonnet/medium]`: replace the Mermaid diagrams in the 8 `docs/` pages by StarUML images, and change the Mermaid line of `rules_documentation_aesthetics.md`. After the licence is bought (the trial puts a watermark on images). Decided by Eve 2026-11-07.
- [ ] **TOOLS-UML-2** (decided in `.claude/design/uml_model_plan.md` D1: all in StarUML, `docs/UML/app.mdj`; write it into the rules with TOOLS-UML-4) `[sonnet/low]`: Diagram location policy. Decide and write into `rules_documentation_aesthetics.md`: `.staruml` source files and exports (SVG, PNG) under `docs/` (suggest `docs/diagrams/`), exports referenced from the `.qmd` docs so GitHub shows them (GitHub does not render `.staruml`); Mermaid stays for small inline diagrams (existing `::: {.lightbox}` rule). Add `.staruml` handling to `.gitignore`/`.aiignore` only if needed.
- [ ] **TOOLS-UML-3** (plan: `.claude/design/uml_model_plan.md`, findings: `.claude/tasks/uml_findings.md`; plan accepted, in progress) `[opus/high]` then `[sonnet/high]`: First diagrams of SPARMVET_VIZ with StarUML MCP, one at a time, Eve reviews each: (1) C4 context + container, (2) activity diagram of the yes/no decision logic, (3) sequence (user click -> filter -> plot), (4) SysML requirement diagram linked to requirement IDs. Export to `docs/diagrams/`, reference in docs. Reference: `OBSWORK/60_ME/CAREER_TRANSITION/00_context/Learning_UML_for_SPARMVET_VIZ.md` (read only if Eve grants access).

### Planned / Large-scale backlog

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle deployment YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).
- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — data analysis recipe hashes + data hashes in DB; LIMS link in audit report; configurable output path per app features.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.
- [ ] **UX-PLOTSTYLE-1** `[sonnet/medium]` `[deferred — eventual enhancement]`: The **Plot Style** panel (T3 `aesthetic_override`, `audit_stack.py` `aesthetic_style_panel_ui`, added 2026-05-11) is **not mounted** in HOME since 2026-11-05 (fork issue #15): letting users change in HOME what the data analysis recipe defines is too much for now, and using it broke the plot (test plan HOM-47). Code kept, unused, with a pointer comment at the mount point (`home_theater.py`). Later: find why it broke the plot, then decide whether to bring it back. Plot style that belongs to the data analysis recipe is authored in BLUEPRINT (separate). ADR-082 unchanged.
- [ ] **BP-VALIDATE-1** `[sonnet/medium]`: "Validate data analysis recipe" button in BLUEPRINT (BLUEPRINT.md, Validate row; known gap) and optionally on TEST_LAB scaffold output. Calls `app/modules/data_analysis_recipe_validator.py` (`validate_data_analysis_recipe` for step lists, `validate_data_analysis_recipe_data` for declared fields vs real columns, issue #18), the same headless functions used by the shipped-data analysis recipes contract test and the weekly data analysis recipe audit (one rule, no copies). Libs stay isolated (ADR-011/016): the validator lives in the app orchestration layer, which may import utils + transformer. Also run it on a data analysis recipe the user uploads in BLUEPRINT (`data_analysis_recipe_uploader` handlers currently load the temporary file without validating step lists). Depends: shipped-data analysis recipes contract test (fork issue).

### Explicitly deferred (scheduled)

- [ ] **DEPS-UPGRADE-1** `[sonnet/low]` `[deferred - monitor only, decided by Eve 2026-11-05]`: Dependency upgrades are frozen until the app is at a more advanced stage (no minor-version change before then). Monitor, do not apply. Known: plotnine 0.15.4 installed, 0.15.9 available (patch releases within the allowed range `>=0.15.4,<0.16.0`; still no pie or polar coordinates, see fork issue #19); matplotlib 3.10.9 -> 3.11.2 and mizani 0.14.4 -> 0.14.6 also available. When the freeze ends: upgrade one library at a time, run the full test suite and the plot render test (`app/tests/test_render_every_plot.py`), and compare the images. Open point: there is no lockfile for the main app, so a fresh install may already pick a newer patch version than the one tested (a lockfile, for example `uv.lock`, would pin it; packaging is Eve's to do by hand).

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

_No current enhancement requests. Append items here using the `[ENHANCEMENT REQUEST]` protocol (`rules_agent_role_bioscientist.md §4-A`) when a data analysis recipe design session exposes a missing action or plot component._

---

## 👤 User Required

Tasks requiring user decision, user action, or explicit discussion before implementation can proceed.

- [ ] **[@user] TOOLS-UML-0** (after live app testing; first step of the TOOLS / UML chain): Decide the StarUML licence before TOOLS-UML-1. Check: (a) official StarUML price and edition (a third-party site listed Professional at about 199 USD per user, VAT excluded; unverified); (b) whether the StarUML MCP server works on the free trial or needs the paid licence (not found in docs, unverified); (c) the 30-day trial may NOT have started yet (Eve has not opened the app; notes in `my-mentoring` say 2026-10-08, probably wrong); start it only when ready to do TOOLS-UML-1; (d) install StarUML >= 7.0.0 and confirm Node >= 22. Eve decided in principle to buy, because the MCP lets the agent and Eve draw diagrams together.
- [ ] Discuss - Aesthetics / automation visuals -> capture and adding to T3 audit ? possibilities ? Consequences ? Gating ?  
- [ ] **[@user] Taxonomy Data Audit**: Verify/correct tags in `assets/gallery_data/*/data_analysis_recipe.yaml` against `assets/gallery_data/TAXONOMY_CHEATSHEET.md`.
- [ ] **[@user] UX-CSS-DEMO**: Review `assets/demo/demo_vetinst.css` after default theme is finalised.
- [ ] **[FEATURE]** Label x/y axis adjustment module — edit title, policy change, color changes, points display — registered in audit. Large feature, grant-exploration candidate.
- [ ] **[TO DISCUSS]** Lab script: Extract pilot data analysis recipe (reconstitution of lineage) — improve reusability.
- [ ] **[TO DISCUSS]** Lab script: Create tool-specific data analysis recipe (e.g. single-sheet variant).
- [ ] **[TO DISCUSS]** Lab script: Combine data analysis recipes — format detection, common datasets, branching.

---

## 🟣 Completed Phases — Archived

| Phase | Description | Completed | Archive |
|---|---|---|---|
| Phases 16–18, 21-A–B | Nav/routing, data analysis recipe-driven tabs, tier toggle, layout | 2026-04-23 | [tasks_archive_2026-04-10.md](archives/tasks_archive_2026-04-10.md) |
| Phase 21-C–I, IU-1–7 | Comparison mode, filters, right sidebar, export bundle, VizFactory | 2026-04-23–30 | [tasks_archive_2026-04-14.md](archives/tasks_archive_2026-04-14.md) |
| Phase 22 (A–J) | Session mgmt, T3 audit, per-plot scoping, propagation | 2026-04-25 | [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) |
| Phase 23-A/B | Deployment, connector library | 2026-04-30 | [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) |
| Phase 24 | `home_theater.py` decomposition (ADR-051) | 2026-05-01 | [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) |
| Phase 25 (A–O) | Left sidebar restructure, app features flag gating, ADR-052+053 | 2026-05-01 | [tasks_archive_phase25.md](archives/tasks_archive_phase25.md) |
| Phase 26 CSS | UI harmonisation: view banners, button colours, Gallery sidebar refactor | 2026-05-02 | ADR-056, ADR-057 |
| DEMO-1..4 | Monday demo render/filter bugs — all fixed | 2026-04-30 | commits `55ab1c5` `33afa1b` etc. |
| Phase 28/29 | Export redesign + assembly→join rename + lib extraction | 2026-05-04/05 | ADR-066, ADR-067, ADR-068 |
| Phase 30 | Agent infra + deployment hardening | 2026-05-05 | commits `891f157`, `2dcd1c2` |
| Phase 31 | Sidebar Slot Registry (ADR-073) + Diagnostic Error Discipline (ADR-078) + Blueprint schema (ADR-075) + ADR-076 flag (ADR-077) | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |
| Phase 32 / May-09 hygiene | Export enhancements (EXPORT-2/3/4), UX-NOTIF-2, ADR-076 MVP-1 complete, BP-COLOR-1/2/3, all Open Issues + CSS batch | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |
| May-11 hygiene | Doc/ADR/lib-test audit fixes, Blueprint IDE features, ADR-079 design, cascade design, T3 threading, repo hygiene | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-11 session | BP-LINEAGE-NAV-1, GALLERY-CLONE-DECOUPLE-1, VIZFAC-RESOLVER-1, DIAG-RUNTIME-BASE-1 + full audit (EMOJI-DOCSTRING-1, VIZ-README-COUNT-1) | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-12 hygiene | Audit script fixes (CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1) | 2026-05-12 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| Phase 18-F, 32, 32-cont, audit-fixes | ACTION-UISCHEMA-1, BP-FORMS-1/ESCAPE/UNDO/HELP, ACTION-RENAME-1, all ADR-082 spawned BP-* tasks, DATA-ANALYSIS-RECIPE-INCLUDE-1 | 2026-05-21 | [tasks_archive_phase32.md](archives/tasks_archive_phase32.md) |
| Phase 33 | BP-AGENT-PARSER-1/TOOLS/INSTRUCT/PANEL/UI/CSS — all ADR-076 MVP-1 agent tasks | 2026-05-21 | [tasks_archive_phase33.md](archives/tasks_archive_phase33.md) |
| Documentation & Hygiene Sprint | DOC-BLUEPRINT-1/USER-1, DOC-LIBREADME-*, TASK-ARCHIVE-1, AUDIT-PASS-1, BP-ADR-FULL-1 | 2026-05-21 | [tasks_archive_hygiene_2026-05-21.md](archives/tasks_archive_hygiene_2026-05-21.md) |
| Phase 34 + May-22 hygiene | TEST_LAB Build (all TL-*), BP-HELP-*, audit fixes, legacy removal (FLAT-PLOTS/AUDIT-FLAG/TYPE-ALIASES/FLAT-WRANGLING), LAB-WORKFLOW-1, UX-APPLY-IMPROVE-1 | 2026-05-22 | [tasks_archive_2026-05-22.md](archives/tasks_archive_2026-05-22.md) |

---

## 📋 Session Notes

Context and status notes from recent sessions. Add here instead of inside active task sections.

- **2026-05-21 (@sync — Phase 33 / BP-BRANCH-NODE-1)** — BP-BRANCH-NODE-1 completed and committed (`99e6b19`). Also discovered all 6 Phase 33 tasks (BP-AGENT-PARSER-1 through BP-AGENT-CSS-1) were already fully implemented (shipped 2026-05-09, tasks not marked done). Verified headless: all agent modules import OK, 3 tools dispatch (51 actions at runtime), sidebar registration + app features files + CSS all in place. Marked done. Added BP-BRANCH-UX-1 (data_schema branch guidance callout).
- **2026-05-21 (BP-JOINT-1 — Joint Designer pane)** — Implemented the dedicated Joint Designer (ADR-082 Q5). New pure stdlib module `libs/blueprint_arch/src/blueprint_arch/join_designer.py` (`compute_key_match` real-overlap stats incl. composite keys + dtype-family advisory; `build_join_step` sym `on` / asym `left_on`+`right_on`, scalar-vs-list; `parse_join_step` inverse w/ YAML boolean-trap guard) + 26 unit tests (all pass). New `4. Joint Designer` nav_panel in `wrangle_studio.render_ui`. Wiring in `blueprint_handlers.define_server`: R4-safe ingredient/key pickers, **real-data** preview (materialises each ingredient via `orchestrator.materialize_tier1`, String-cast key overlap mirroring the assembler), comment-gated Apply → logic_stack append/replace, edit pre-fill on join-node select. Removed the fabricated `show_join_modal`/`confirm_join`/`update_secondary_datasets` + dead picker selectors (clean break, no orphaned refs). Verified: 26/26 logic tests, both app modules import clean. Decisions taken with Eve: center pane · real-data overlap · composite/multi-key · edit+create. **Follow-up:** join-component Save (`_serialise_component_for_save` role `join`) must quote `on:` (pre-existing gap — join-role save not yet implemented). **Live UI smoke pending → BP-SMOKE-1** (no BLUEPRINT Playwright infra yet). Session triage: 3 audit reports PROCESSED (coherence PASS 6/6, integrity FAIL = known DATA-ANALYSIS-RECIPE-INCLUDE-1 false positive, 1 narrative log).
- **2026-05-20 (BLUEPRINT feature lock)** — Verified BP-FORMS-1 against the running implementation: all 60 transformer action forms render headless (zero failures, all 8 widget types). Found the form layer is half-built (add-node primitive vs edit-node rich; no component form path; 7/191 components schemed) + 2 ADR-075 widget gaps (enum preview, expression editor). Authored **ADR-082 (BLUEPRINT Full Feature Set & Build-Mode Contract)** — locked 4-layer model, 7 decision points, MVP/v2 inventory, T1/T2-vs-T3 boundary. Key decision with Eve: **branch = node-level lineage bifurcation** (shared upstream by reference, divergent downstream fragment-per-component `!include`) — NOT whole-data analysis recipe duplication; terminology fix (graph fan-out ≠ data analysis recipe branch). Spawned 12 Phase 32 (cont.) tasks. Research draft → RESOLVED.
- **2026-05-20** — Triaged 11 unprocessed audit files from 2026-05-13/18. 10 PASS (marked PROCESSED). 1 actionable finding: `audit_data_analysis_recipe_integrity.py` reports 6/6 data analysis recipes FAIL because `debug_assembler.py` uses `yaml.safe_load()` — `!include` not supported. All data analysis recipes are structurally fine (coherence audit PASS). Task added: DATA-ANALYSIS-RECIPE-INCLUDE-1 in Do Now.
- **2026-05-12** — All recent work (CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1, EMOJI-DOCSTRING-1, VIZ-README-COUNT-1) archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md).

---

## Archive Pointers

- [tasks_archive_2026-05-22.md](archives/tasks_archive_2026-05-22.md) — Phase 34 (TEST_LAB Build) + BP-HELP sweep + audit fixes + legacy removal + LAB-WORKFLOW-1 + UX-APPLY-IMPROVE-1; also records DROPPED decisions (LAB-SEND-TO-1, LAB-OPEN-BLUEPRINT-1, UX-DEVINSP-1)
- [tasks_archive_phase33.md](archives/tasks_archive_phase33.md) — Phase 33: all ADR-076 MVP-1 Blueprint AI Agent tasks (BP-AGENT-*)
- [tasks_archive_phase32.md](archives/tasks_archive_phase32.md) — Phase 18-F, 32, 32-cont (ADR-082), audit script fixes: ACTION-UISCHEMA-1, all BP-* IDE/plot-model/branch/autosave tasks, DATA-ANALYSIS-RECIPE-INCLUDE-1
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
- [test_plan_2026-06.md](test_plan_2026-06.md) — **current** live app test plan (Phase 34 baseline; all 4 spaces + app features files)
- [tasks_test_ui_current.md](tasks_test_ui_current.md) — superseded Phase-26 UI checklist (items folded into the plan above)
