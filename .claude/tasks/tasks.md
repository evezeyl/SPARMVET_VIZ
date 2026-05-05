# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-03 (Wave 1 remediation complete; Wave 2 registered) by @dasharch

---

## 2026-05-04 Detected changes & after demo notes - to review

- [x] Verification: Manifest 1_test_data_ST22_dummy: seems that the main manifest became a huge chunk instead of using the !include Tag. We need to ensure that main manifest links to appropriate directory and file substructure - no huge chunk. Can you verify this ? Create additional directories. The goal is to provide a human redeable structure of the main manifest, so it can understand the general idea of what the manifest does. Eg. Groups in main, plots definitions via !include. Fixed all manifests and Clarified ADRs good. 

- [x] **EXPORT-REDESIGN-1**: Consolidate export UI into one panel with scope toggle. ✅ 2026-05-04
  **Design agreed 2026-05-04 — spec:** `.claude/design/export_specification.md`
  - Deleted `export_audit_report_ui()`, `export_audit_report_download()`, `_audit_report_filename()`
  - Single "💾 Export Bundle" button with presentation controls only
  - 3-way scope toggle `[Global project | Active group | Active plot]` — shown when persona has BOTH flags
  - Dynamic choices: Active group hidden when no analysis_groups or plot has no group
  - Removed Single Graph Export accordion panel from sidebar (superseded by scope toggle)
  - **Impl:** `app/handlers/export_handlers.py`, `app/handlers/home_theater.py`

- [x] **EXPORT-REDESIGN-2**: Auto-include T3 audit trail in report.qmd when T3 active + has changes. ✅ 2026-05-04
  - T3 audit trail section added to end of `report.qmd` — per-plot table (Step, Action, Details, Justification)
  - `recipes/t3_steps.yaml` generated when T3 has committed active nodes
  - Scope (global/group/plot) applied consistently to both the audit section and t3_steps.yaml
  - **Impl:** `export_bundle_download()` in `export_handlers.py`


- [x] **ASSEMBLY-RENAME**: ✅ 2026-05-04 Rename `assembly_manifests` → `join_manifests` and role string `"assembly"` → `"join"` everywhere. Use VSCode find-and-replace across files.
  **Agreed name:** `join_manifests` (checked: not a Polars keyword conflict at dict-key level)
  **Scope (~35 files, ~65 occurrences):**

  **Pass 1 — zero-ambiguity, replace-all:**
  - `assembly_manifests` → `join_manifests` (YAML key + all Python `.get()` calls)

  **Pass 2 — role string, replace with care:**
  - `"assembly"` → `"join"` (role string in blueprint_handlers, manifest_navigator, wrangle_studio)
  - ⚠️ EXCEPTION: `session_manager.py` line ~213 — `{"assembly": ..., "contracted": ...}` is a Parquet path label, NOT the manifest role — leave it as-is

  **Pass 3 — UI label strings (manual, ~7 hits):**
  - `"◆ Assembly"` → `"◆ Join"` (wrangle_studio.py)
  - `"Assembly Output (Input)"` → `"Join Output (Input)"` (wrangle_studio.py)
  - `f"{sid} — assembly"` → `f"{sid} — join"` (blueprint_handlers.py)
  - ⭐ TubeMap node labels (what the boss sees in Cytoscape) — `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py`:
    - line ~167: `"{asid}\\nAssembly"` → `"{asid}\\nJoin"`
    - line ~189: `"{asid}\\nAssembly Wrangling"` → `"{asid}\\nJoin Wrangling"`

  **Pass 4 — variable names in Python scripts (rename carefully):**
  - ⚠️ NEVER use bare `join` as a variable name — shadows `str.join()` and is confusing next to Polars
  - `assemblies` → `join_defs` or `join_specs`
  - `asm_block` → `join_block`
  - `is_assembly` → `is_join_step`
  - `assembly_rels` → `join_rels`

  **Pass 5 — docs (.claude/*.md):**
  - `architecture_decisions.md`, `manifest_data_contract_rules.md`, `blueprint_architect_ux_spec.md`, `handoff_session7.md`



## 🟡 Active Lineage Build: ST22

- [ ] **Lineage 2 (Plasmid Dynamics)** `[@user]`:
    - [ ] Create `2_test_data_ST22_dummy/input_fields/plasmid_data.yaml`
    - [ ] Implement Tier 1 filtering (min identity/overlap for PlasmidFinder)
    - [ ] Assemble with metadata and AMR results; verify via Tier 1 audit artifacts.

---

## 🔴 Open Issues

### Export / Reproducibility

- [x] **EXPORT-HASH-1**: Bundle README `Data SHA256` was computed from T1 Parquet content, inconsistent with the session key's `data_batch_hash` (raw source file hash). Fixed: both bundle export and SGE now read `data_batch_hash` from `home_state`. All export surfaces (bundle README, bundle QMD report, SGE README, audit report footer) now show all three hashes with human-readable explanations.

- [ ] **EXPORT-HASH-2** `[sonnet/medium]`: Read `decision_hash` from Parquet metadata key `sparmvet_decision_hash` at export time; include in bundle README, report.qmd, and image file metadata. Use `get_parquet_metadata_hash(path)` per materialized T1/T2 Parquet file. Paths via `bootloader.get_location("anchors")` + naming convention. **Part of ADR-069 audit trail.**

- [ ] **EXPORT-VERSION-1** `[haiku/low]`: Add `git_commit` (`git rev-parse --short HEAD`) and `release_version` (`git describe --tags --always`) to all export surfaces: bundle README, report.qmd header, and image file metadata. **ADR-069.**

- [ ] **EXPORT-IMG-META-1** `[sonnet/medium]`: Embed provenance subset (8 fields: `data_batch_hash`, `manifest_sha256`, `decision_hash`, `git_commit`, `release_version`, `created_at`, `plot_id`, `persona_id`) in exported image file metadata. PNG → Pillow `PngInfo` iTXt chunks (`sparmvet:` prefix). SVG → `<metadata>` XML block. PDF → XMP metadata. **ADR-069 Rule 3. Provenance must survive file extraction from bundle.**

- [ ] **EXPORT-AUDIT-COMPLETE-1** `[sonnet/medium]`: Add all remaining missing provenance fields to bundle README and report.qmd: `created_at` (ISO 8601 UTC), `manifest_name`/path, `persona_id`, `active_tier` (T1/T2/T3), `software_versions` (Python + plotnine + polars + SPARMVET), `data_source_paths` (relative paths of raw files loaded). Introduce `build_export_provenance()` helper in `export_handlers.py` to assemble the full provenance dict once and pass to all surfaces. **ADR-069.**

### Session / Import

- [x] **SESSION-PERSONA-1** `[sonnet/low]`: Ghost_save now gated by `ghost_save.enabled` in persona automation config. Added `bootloader` param to `audit_stack.define_server`; `_write_t3_ghost` only fires when `bootloader.get_automation_setting("ghost_save","enabled")` is truthy. Fixes `qa` persona (t3_sandbox=true but ghost_save=false). ✅ 2026-05-05

- [ ] **INGEST-SANITIZE-1** `[sonnet/medium]`: Ghost sanitization logic (`libs/ingestion/`) is partially implemented — the sanitizer class exists but is not wired into the main ingestion pipeline. `IngestorOrchestrator` calls raw loaders directly; sanitization is only triggered in isolated debug runners. Wire `DataSanitizer` into `IngestorOrchestrator.run()` before T1 materialisation so ghost values (empty strings, whitespace-only, sentinel nulls) are stripped on every ingestion. See audit §1A (`audit_final_exhaustive_2026-05-03.md`).

### UX

- [ ] **THEATER-1** `[sonnet/medium]`: Collapse/minimize plot panel — ▼/▲ caret in plot card header → 1-line collapsed state. Per-plot, persisted in `home_state`.

- [ ] **STATIC-VIEW-1** `[sonnet/low]`: "Zero functionality" static persona polish — three sub-items, pending input from demo (2026-05-04):
  - [ ] **STATIC-VIEW-1a** `[haiku/low]`: Hide the view-title banner (central plot-group header strip) in fully static personas — it adds no value when there are no controls and may clutter a clean presentation layout. Gate on a new persona flag or reuse `interactivity_enabled: false`.
  - [ ] **STATIC-VIEW-1b** `[sonnet/low]`: T2 as default displayed tier — in static personas, T2 (analysis-ready) should be shown on first render instead of T1 raw. T1 toggle should not be exposed. Decide: force `active_tier=T2` in bootloader for `interactivity_enabled: false` personas, or add an explicit `default_tier` field to the persona template.
  - [ ] **STATIC-VIEW-1c** `[sonnet/low]`: Left sidebar treatment for static view — sidebar still renders (manifest choice, possibly empty accordion). Options: hide entirely, collapse to a narrow icon rail, or show only a fixed project-name label. **Needs user input after demo — may get stakeholder feedback on what makes sense for a Galaxy/IRIDA deployment.**

---

## 🟡 Wave 2 — Pending User Decision

These items require a design decision or scope confirmation before implementation starts.

### libs/utils/ Relocations (Pattern B)

- [x] **UTILS-RELOC-1**: ~~Move `blueprint_mapper.py` from `libs/utils/` → `app/modules/`~~ — Resolved differently: moved to `libs/blueprint_arch/` (new dedicated lib, ADR-067). `manifest_navigator.py` also moved there from `app/modules/`. Imports updated in `blueprint_handlers.py`. (2026-05-05)
- [ ] **UTILS-RELOC-2** `[haiku/low]`: `gallery_manager.py` appears in both `libs/utils/src/utils/` and `libs/viz_gallery/src/viz_gallery/` — deduplicate. Decision needed: which copy is canonical? Delete the other and fix all imports.

### app/modules/ Two-Category Law Refactor (ADR-045)

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law (modules must be headless-safe; Shiny wiring belongs in `app/handlers/`). Decision needed: scope and migration plan before touching live handlers. See audit §4A.


### UI - Persona scoping [DECIDED 2026-05-05]

**Functionality dependency mapping — all agreed:**

- **PASSIVE_INTERACT**: `PASSIVE_INTERACT` + `HASHES_EXPORT` (always) + `TIER_TOG` T1/T2 (configurable). `AUTOSAVE` off.
- **ACTIVE_INTERACT (T3)**: Full cascade — T3 requires `CMP_MODE` + `AUD_RPT` + `SESS_MGT` + `AUTOSAVE` + `export_enabled` + `HASHES_EXPORT` + both `TIER_TOG`. Validation error at startup if T3 on and any co-flag missing.
- **EXPORT**: Single `export_enabled` flag. Scope by active context/toggle. `HASHES_EXPORT` always on (ADR-069). `EXP_BNDL`/`EXP_GROUP`/`EXP_GRF` are not separate flags — collapse to one.
- **IMPORT**: Single browse + mapping panel. `IMP_HLP` on → all manifest sources. `META_ING` on alone → metadata schema only. `IMP_HLP` implies `META_ING`. Overwrite behavior.
- **GALLERY / BLUEPRINT_ARCH / TEST_LAB**: Single on/off flag each. Sub-flags deferred until components mature (additive, non-breaking when introduced).
- **TIER_TOG T1/T2**: Configurable on/off; required if T3 active (cascade).
- **TIER_TOG T3/comparison**: Required if T3 active only.
- **PRS_BADGE**: On/off display preference, no functional dependency.
- **MAN_SEL / MAN_FIX**: Collapse to one flag `manifest_selector_visible: true/false`.
- **UI_TITLE**: On/off; resolution: persona `ui_title` > manifest `info.display_name` > nothing.
- **UI_SUBT**: On/off; depends on `UI_TITLE` (hidden if title off); resolution: persona `ui_subtitle` > manifest `info.subtitle` > nothing. `info.description` is free-form long description, not shown in header.
- **AUTOSAVE / ghost_save**: Parquet cache always written (performance, independent of flag). `autosave` flag controls ghost_save (session JSON) only. Off for passive personas.

**Implementation tasks from this mapping:**

- [x] **PERSONA-CONFIG-VALIDATE-1** `[sonnet/medium]`: PersonaValidator Rule 6 — T3 cascade: if `t3_sandbox_enabled=True` then `comparison_mode_enabled`, `audit_report_enabled`, `session_management_enabled`, `export_enabled` must all be True. Fatal error if violated. ✅ 2026-05-05
- [x] **PERSONA-CONFIG-FLAG-1** `[haiku/low]`: Collapsed `export_bundle_enabled` + `export_graph_enabled` → `export_enabled` in all 8 templates + bootloader backward compat + handler call sites. ✅ 2026-05-05
- [x] **PERSONA-CONFIG-FLAG-2** `[haiku/low]`: `manifest_selector_visible` mirrored into features dict by bootloader (`_load_persona_config`). `bootloader.is_enabled("manifest_selector_visible")` now works. ✅ 2026-05-05
- [x] **PERSONA-CONFIG-FLAG-3** `[haiku/low]`: Added `blueprint_enabled` + `test_lab_enabled` to all 8 templates and to `persona_validator._REQUIRED_FLAGS`. `gallery_enabled` was already present. ✅ 2026-05-05
- [ ] **UI-TITLE-1** `[sonnet/medium]`: Implement UI title/subtitle resolution: persona config override > manifest `info.display_name`/`info.subtitle` > nothing. Add `info.subtitle` field to manifest schema. `UI_TITLE` off hides both. Resolves REVIEW-UI-TITLE-SUBT.
- [ ] **IMPORT-UI-1** `[sonnet/high]`: Unify the two import browse buttons into a single browse + mapping panel. Mapping panel auto-filters available data sources based on active persona flag: `META_ING` only → metadata schema; `IMP_HLP` → all manifest data sources (metadata included). `IMP_HLP` implies `META_ING`. Import behavior: **overwrite** (not merge). Affects `app/handlers/ingestion_handlers.py` and import panel UI. 


### 🔵 REVIEW tasks — design discussions needed (2026-05-04)

- [x] **Deployment Preparation**: Reviewed deployment notes. Key issues identified and tasked below. ✅ 2026-05-05

- [x] **DEPLOY-CDN-1**: Vendor Cytoscape@3.29.2 + Dagre@0.8.5 + cytoscape-dagre@2.5.0 + Bootstrap Icons@1.11.1 into `app/src/www/vendor/`. Updated `main.py` to serve `www/` as static assets (`App(..., static_assets=_www)`). Updated `ui.py` to use `/vendor/*` local paths. App imports clean. 97/97 tests pass. ✅ 2026-05-05

- [x] **DEPLOY-MODULES-1**: Gate server-side module instantiation and handler registration in `server.py` on persona flags (positive inclusion). Gated: TestLabStudio (`test_lab_enabled`), audit_stack (`t3_sandbox_enabled`), blueprint_handlers (`blueprint_enabled`), gallery_handlers (`gallery_enabled`). Always-on: wrangle_studio, home_theater, ingestion_handlers. Also guarded `dev_studio.render_ui()` in home_theater.py against `None`. ✅ 2026-05-05

- [x] **VENDOR-MANIFEST-1**: Created `app/src/www/vendor/VENDOR_MANIFEST.md` — records all vendored assets with version, source URL, licence, and date. Must be updated whenever a vendor asset is added/upgraded. ✅ 2026-05-05

- [x] **DEPLOY-LIBS-1** `[haiku/low]`: Created `scripts/install_libs.sh` — installs all 8 editable libs in one command, VENV-overridable, exits on error, smoke-tested. ✅ 2026-05-05
- [ ] **TO DISCUSS**: Toggle "show all data" — data shown only abstract; discuss what is exposed and when
- [ ] **TO DISCUSS — lab script**: Extract pilot manifest (reconstitution of lineage) — improve reusability (e.g. manifest for results from a specific tool)
- [ ] **TO DISCUSS — lab script**: Create tool-specific manifest (e.g. single-sheet variant of above)
- [ ] **TO DISCUSS — lab script**: Combine manifests — format detection, common datasets, branching
- [ ] **TO DISCUSS**: Prepare to connect — icons local, verify legacy, cytoscape

- [ ] **REVIEW-SCOPING-1 — T3 bundle dependency rule** `[sonnet/low]`: Confirm the rule: if `t3_sandbox_enabled` is on, then `comparison_mode_enabled` + `audit_report_enabled` + `session_management_enabled` must also be on. These are the computer functionalities that must be activated together as a group when T3 is activated. Need to verify current persona templates enforce this and document it as a formal scoping rule. Related: `SESSION-PERSONA-1` (ghost_save gating).

- [ ] **REVIEW-EXPORT-FLAGS — EXP_GROUP as separate persona flag** `[sonnet/low]`: Currently `Active group` export scope is gated on `export_graph_enabled` (same as Active plot). The matrix lists `EXP_GROUP` as a distinct column from `EXP_GRF`. Decision: add a dedicated `export_group_enabled` persona flag, or keep current behaviour (lineage backtrace works for both → one flag is enough)? Eve's note: as long as lineage works for all scopes, activating all export types together is acceptable.

- [x] **REVIEW-IMPORT-PANEL — META_ING / IMP_HLP / single import UI**: ✅ 2026-05-05 **Decided.** Single browse + mapping panel. `IMP_HLP` on → mapping shows all manifest data sources (metadata included). `META_ING` on alone → mapping shows metadata schema only. `IMP_HLP` implies `META_ING` (superset). Metadata import behavior: **overwrite** (not merge). Two persona flags remain in config for scoping control; UI has one entry point. See **IMPORT-UI-1** for implementation.

- [ ] **REVIEW-AUTOSAVE-CACHE — caching vs autosave separation** `[sonnet/low]`: Is the Parquet cache (T1 materialisation) always written for performance, independent of the `autosave` flag? If yes: cache-write is always on; `autosave` flag only controls ghost-save (session JSON). If loaded once on same system, cached Parquet avoids recalculating wrangling + plots on tab switch — good for responsiveness. Need to decide separation before fixing `SESSION-PERSONA-1`.

- [ ] **REVIEW-HASH-EXPORT — hash visibility and export gating** `[sonnet/low]`: Hashes (manifest SHA256, data batch SHA256, recipe hash) are always computed. Question: should the export of all 3 hashes (in README + report) be gated by a flag, or always included in bundle? T3 recipe hash needs T3 active. Further discussion needed to clarify what Eve expects to see and when.

- [x] **REVIEW-UI-TITLE-SUBT — manifest-driven UI title/subtitle**: ✅ 2026-05-05 **Decided.** Resolution order: persona config override > manifest field > nothing shown. Manifest fields: `info.display_name` (title), `info.subtitle` (subtitle — new short dedicated field). `info.description` remains free-form long description, NOT shown in UI header. `UI_TITLE` off → both title and subtitle hidden (subtitle depends on title). See **UI-TITLE-1** for implementation.


### UI - Functionality debugging (TODO / User )
- [ ] Exports -> retest / debug
- [ ] proper definition of the session ghost save and save function when Tier 3 activated
- [ ] import and mapping of the files to the manifest 
- [ ][FEATURE] Label - x y axisis adjustment module - Automation / User adjustment panel ? Including eg. some connectors to the visualisation layer on t3 
Allow edit title, allow policy change, color changes, points display  ... all need to be able to be registered in the audit -> we need an edit palette menu possibility - problem that plots are not really interactive so need to make list of elements that can be changed and provide the possibilities - that will not be a small work this ! because it depends on the plot type and elements also ! Could be a good exploration for grant that also 

---

## 🟡 Deferred / Backlog

### Multi-System Deployment (Phase 23 C–E)

Phases 23-A/B done. 23-C/D/E deferred — not active sprint.

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).

### Filter / Propagation (enhancements)

- [ ] **PROP-2** `[sonnet/medium]`: "Filter inventory" panel — effective filter set per plot with per-filter tooltip (affected/skipped plots).
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius, nodes ✅/⚠️/❌. Needs own design pass + ADR.
- [ ] **22-J-10** `[sonnet/medium]`: Aesthetic propagation (color/shape/fill) — deferred until gallery-clone or wrangling surface supports aesthetic overrides.

### Export (enhancements)

- [ ] **EXPORT-2** `[sonnet/medium]`: Selective export — per-tier checkboxes (T1/T2/T3 data, recipes, filter trace, Quarto report, README).
- [ ] **EXPORT-3** `[sonnet/medium]`: Quarto HTML report — typography, plot placement, methods section, TOC polish.
- [ ] **EXPORT-4** `[sonnet/low]`: Global export — per-plot height/width control before bundling.
- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless/static render path for `BlueprintMapper.generate_cy_elements()`. Depends on Blueprint Architect being stable.

### Gallery & UI

- [ ] Gallery: Re-verify "Clone to Sandbox" after ADR-057 sidebar refactor. Decide how. *(Deferred — Gallery needs dedicated work sprint before tackling clone flow.)*
- [ ] **GALLERY-MAP** `[opus/high]` `[investigation]`: Map chart types (choropleth, hexbin map, bubble map, cartogram). Blocked — `geom_map` requires GeoDataFrame. Needs: spatial manifest format + geopandas integration design.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[investigation]`: Flow / network chart types (Chord diagram, Sankey, network graph, arc diagram, edge bundling). Blocked — plotnine has no native support. Needs feasibility study.
- [ ] **Taxonomy Data Audit** `[@user]`: Verify/correct tags in `assets/gallery_data/*/recipe_manifest.yaml`.
- [ ] Gallery thumbnails for faster visual scanning.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD (currently static help text).
- [ ] **UX-DEVINSP-1** `[sonnet/medium]`: Test Lab right sidebar + left sidebar redesign — functionality TBD.
- [ ] **UX-CSS-DEMO** `[@user]`: Review `assets/demo/demo_vetinst.css` after default theme finalised.
- [ ] **UX-NOTIF-2** `[sonnet/medium]`: Persist `notification_log` to the T3 ghost so alerts survive a page refresh. Hook into `audit_stack.py` `_notify` calls; on session restore, reload into `notification_log` reactive. Linked to UX-NOTIF-1 (ADR-060).

### VizFactory

- [ ] `geom_map` — deferred; requires spatial data (GeoDataFrame). Uncomment when spatial manifests introduced.
- [ ] **21-F-7**: Add `scale_x_discrete` / `scale_y_discrete` to manifests where Year/ST columns are categorical.

### Technical Debt

- [ ] **Unified Materialization** `[haiku/low]`: `debug_wrangler.py` / `debug_assembler.py` — auto-create dated `tmpAI/{date}/{lineage}/` subfolders (use `get_debug_out_dir()` from `libs/utils`).
- [ ] **T3 lf threading** `[sonnet/medium]`: When new T3 node types (rename, derive, pivot) are added, thread them through `_apply_t3_to_lf`. Design in `.claude/tasks/design_sge_lineage_t3.md`.
- [ ] **ADR-011 cross-lib violations** `[opus/high]` `[repo-hygiene]`: The following imports violate the "no cross-lib" rule and should be resolved (move shared types to `utils` or inject via app layer):
  - `libs/blueprint_arch/blueprint_mapper.py` → `utils.config_loader.ConfigManager`
  - `libs/transformer/pipeline.py` → `utils.config_loader.ConfigManager`, `ingestion.ingestor.DataIngestor`
  - `libs/transformer/data_assembler.py` → `utils.hashing`
  - `libs/transformer/data_wrangler.py`, `metadata_validator.py` → `utils.errors`
  - `libs/viz_factory/viz_factory.py` → `utils.errors`
  - Pragmatic note: `utils.errors` and `utils.hashing` could be promoted to a `libs/shared_types` mini-lib, or violations accepted as `utils` being a "base" lib with no upstream deps (no violations in `libs/utils/` itself).
- [ ] **UTILS-RELOC-2** `[haiku/low]`: `gallery_manager.py` exists in both `libs/utils/src/utils/` and `libs/viz_gallery/src/viz_gallery/` — deduplicate. Decide canonical copy; delete the other and fix all imports.
- [ ] **In-app contextual help** `[sonnet/high]` `[ux]` `[new]`: Each user space (HOME, BLUEPRINT, GALLERY, TEST_LAB) should have a help button that opens / links to the relevant documentation section. Design question unresolved: bundle docs with app (Quarto HTML rendered locally, served by Shiny static assets) vs. deploy docs separately (docs server or GitHub Pages) with deep-links. Options:
  1. Ship `docs/_site/` alongside app, serve via `ui.tags.iframe` or `ui.HTML()`.
  2. Deploy docs to GitHub Pages; link out from app (simple, but requires internet).
  3. Generate per-space summary markdown, render inline in a modal (`ui.modal_show()`).
  Decision gate: confirm deployment context (air-gapped Galaxy vs. internet-connected) before implementing.

### Blueprint Architect

- [ ] **TubeMap aesthetics** `[haiku/low]` — tighter rail/tube look; rename 'ref' → 'Add' in nodes and legend.
- [ ] Full Blueprint Architect debug pass (field contracts, lineage rail, Zone C layout).
- [ ] **Action Registry Parity** `[sonnet/high]` (18-F): Expose 175+ `@register_action` entries in UI.
- [ ] **Visual Forking** `[sonnet/high]` (18-F): Select node → initiate new branch → YAML additions.
- [ ] **Field Gap Analysis tool** `[sonnet/medium]`: Field name → walk lineage to earliest insertion point.
- [ ] **Forward propagation hint** `[sonnet/medium]`: Show which output_fields / final_contract files need updating.
- [ ] **UX-NOTIF-3** `[haiku/low]`: Project-load notification for Blueprint Architect manifest reload. Hook into `blueprint_handlers.py` after a successful manifest import (`btn_import_manifest` path). Low priority; tackle during Blueprint debug pass.
- [ ] **Define** `[opus/high]` development - ADR for blueprint architect : functionalities - help develop without code. Input output contracts, Actions insertions to manifest with parametres, update data view for selected lineage, improved data inspection, definition of joints, work in T1, branching, T2, definition of groups and plot recipe.  


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
| Phase 26 CSS | UI harmonisation: view banners, button colours, Gallery sidebar refactor, sidebar toggle, modal radio spacing | 2026-05-02 | ADR-056, ADR-057 |
| DEMO-1..4 | Monday demo render/filter bugs — all fixed | 2026-04-30 | commits `55ab1c5` `33afa1b` `b91dfc9` `4c962e6` `8b4f3a4` |
| AUDIT-1 | Allow PK-column filters with warning (ADR-049 amended) | 2026-04-30 | commit `3c6195f` |
| PROP-1 | Per-plot column-presence preview in propagation modal | 2026-04-30 | commit `b4dcd10` |
| UX-3/5 | Filter row 🗑 icon + right sidebar header bold/yellow | 2026-05-01 | commit `294814e` |
| UX-4 | "➜ Send to Audit (N)" rename in T3 mode | 2026-05-02 | `filter_and_audit_handlers.py` |
| UX-2 | Data preview selectize width — covered by `.column-picker-container` CSS | 2026-05-02 | `theme.css` Phase 26 |
| PERSONA-1b | Persona-name gate doc-drift | 2026-05-01 | commit `7344951` |
| STARTUP-SORT | Duplicate `sort` registration warning on startup | 2026-05-02 | commit `130f4f5` |
| SESSION-1 | Session reimport fails (no assembly.json) | 2026-05-02 | `session_manager.py`, `home_theater.py` |
| EXPORT-SGE-1/5/6 | Single graph export: plot/data filenames + README hashes | 2026-05-02 | `single_graph_export_handlers.py` |
| EXPORT-SGE-3 | Apply button vestigial — confirmed absent, closed | 2026-05-02 | no code change |
| UX-FONT-1 | `default_font_family: "Liberation Sans"` in test manifests | 2026-05-02 | `1/2_test_data_ST22_dummy`, `stress_test_master` |
| persona_selector orphan | Removed dead `update_persona_context` handler | 2026-05-02 | `ingestion_handlers.py` |
| VizFactory timedelta | `scale_x/y_timedelta` — works in plotnine 0.15.3, smoke-tested | 2026-05-01 | 42/42 pass |
| Bugs/Export/Import/UX resolved 2026-05-02 | STATE-T2, STATE-1/2, BUG-PERF-1, AUDIT-2/3/4, PROP-4, EXPORT-TIERS/SGE-2/4/7, IMPORT-1, UX-1, UX-NOTIF-1 | 2026-05-02 | [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) |
| Wave 1 Remediation | §1A §2B §3B §3D §5 §6A/B/C §7A/B §8 + test fixes | 2026-05-03 | [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) |
| CSS / Gallery Sprint 2026-05-03 | CSS-TOGGLE, GALLERY-ICONS/SELECTALL/PIVOT/PANES/META/RECIPES-13/TAXONOMY-6/CHEAT/PREVIEWS/META-6AXIS, CSS-ACCORDION-HARM, HOME-PLOT-COLLAPSE, BLUEPRINT-WORK-COLLAPSE, REVERT-ADR064-COLLAPSE, CSS-BLUE-HARM/FIXES, UI-STYLE-GUIDE | 2026-05-03 | ADR-056..065 |
| Phase 28/29: Export redesign + assembly→join rename + repo hygiene + lib extraction | Export scope toggle, assembly→join rename, .antigravity restructure, `libs/blueprint_arch/` + `libs/test_lab/` extracted, `dev_studio` → `test_lab_studio`, `@sync` guardrail | 2026-05-04/05 | ADR-066, ADR-067, ADR-068 |

**Phase 24 commits:** `89bb5ef` `890b609` `f540cbf` `d50197e` `4c38f26` `18dbd46` `f0f7d92` `2393e50` `0b50fbd`
**Phase 25 commits:** `294814e` `9b66656` `72726df` `45591ac` `95b48ac` `dc4464c` `320f6bf`
**Phase 30 — Agent infra + deployment hardening (2026-05-05):**
- `891f157` — agentic reorg: `.antigravity/` + `.agents/` → `.claude/`, `AGENT_GUIDE.md` → `CLAUDE.md`. **Recovery reference: if any path looks broken, `git show 891f157 --stat` lists every rename with similarity score.**
- `2dcd1c2` — DEPLOY-MODULES-1: persona-gated module registration, gallery→T3 dead code removed, ~2600 path refs updated.



---

**Archive Pointers:**
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
