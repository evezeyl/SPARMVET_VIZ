# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-03 (Wave 1 remediation complete; Wave 2 registered) by @dasharch

---

## 2026-05-04 Detected changes & after demo notes - to review

- [x] Verification: Manifest 1_test_data_ST22_dummy: seems that the main manifest became a huge chunk instead of using the !include Tag. We need to ensure that main manifest links to appropriate directory and file substructure - no huge chunk. Can you verify this ? Create additional directories. The goal is to provide a human redeable structure of the main manifest, so it can understand the general idea of what the manifest does. Eg. Groups in main, plots definitions via !include. Fixed all manifests and Clarified ADRs good. 

- [x] **EXPORT-REDESIGN-1**: Consolidate export UI into one panel with scope toggle. ✅ 2026-05-04
  **Design agreed 2026-05-04 — spec:** `.antigravity/design/export_specification.md`
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


- [ ] **ASSEMBLY-RENAME**: Rename `assembly_manifests` → `join_manifests` and role string `"assembly"` → `"join"` everywhere. Use VSCode find-and-replace across files.
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
  - ⭐ TubeMap node labels (what the boss sees in Cytoscape) — `libs/utils/src/utils/blueprint_mapper.py`:
    - line ~167: `"{asid}\\nAssembly"` → `"{asid}\\nJoin"`
    - line ~189: `"{asid}\\nAssembly Wrangling"` → `"{asid}\\nJoin Wrangling"`

  **Pass 4 — variable names in Python scripts (rename carefully):**
  - ⚠️ NEVER use bare `join` as a variable name — shadows `str.join()` and is confusing next to Polars
  - `assemblies` → `join_defs` or `join_specs`
  - `asm_block` → `join_block`
  - `is_assembly` → `is_join_step`
  - `assembly_rels` → `join_rels`

  **Pass 5 — docs (.antigravity/*.md):**
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

- [ ] **EXPORT-HASH-2**: `decision_hash` (wrangling recipe SHA256, stored in `sparmvet_decision_hash` Parquet metadata key) is referenced in exports but not yet read out and printed as a value. Currently exports say "see Parquet metadata". Fix: at export time, read `get_parquet_metadata_hash(path)` for each materialized T1/T2 Parquet file and include the values in README and report. Requires knowing the Parquet file paths at export time — accessible via `bootloader.get_location("anchors")` + per-dataset naming convention.

### Session / Import

- [ ] **SESSION-PERSONA-1**: Autosave (`ghost_save`) must be gated on `t3_sandbox_enabled`. The save/export/import UI is already hidden for non-T3 personas. The open question is whether the `ghost_save` timer fires regardless — if so, it would write empty or meaningless session files for static/pipeline personas. Fix: before triggering `ghost_save`, check that `t3_sandbox_enabled` is true in the active persona config. If not, skip the write entirely.

- [ ] **INGEST-SANITIZE-1**: Ghost sanitization logic (`libs/ingestion/`) is partially implemented — the sanitizer class exists but is not wired into the main ingestion pipeline. `IngestorOrchestrator` calls raw loaders directly; sanitization is only triggered in isolated debug runners. Wire `DataSanitizer` into `IngestorOrchestrator.run()` before T1 materialisation so ghost values (empty strings, whitespace-only, sentinel nulls) are stripped on every ingestion. See audit §1A (`audit_final_exhaustive_2026-05-03.md`).

### UX

- [ ] **THEATER-1**: Collapse/minimize plot panel — ▼/▲ caret in plot card header → 1-line collapsed state. Per-plot, persisted in `home_state`.

- [ ] **STATIC-VIEW-1**: "Zero functionality" static persona polish — three sub-items, pending input from demo (2026-05-04):
  - [ ] **STATIC-VIEW-1a**: Hide the view-title banner (central plot-group header strip) in fully static personas — it adds no value when there are no controls and may clutter a clean presentation layout. Gate on a new persona flag or reuse `interactivity_enabled: false`.
  - [ ] **STATIC-VIEW-1b**: T2 as default displayed tier — in static personas, T2 (analysis-ready) should be shown on first render instead of T1 raw. T1 toggle should not be exposed. Decide: force `active_tier=T2` in bootloader for `interactivity_enabled: false` personas, or add an explicit `default_tier` field to the persona template.
  - [ ] **STATIC-VIEW-1c**: Left sidebar treatment for static view — sidebar still renders (manifest choice, possibly empty accordion). Options: hide entirely, collapse to a narrow icon rail, or show only a fixed project-name label. **Needs user input after demo — may get stakeholder feedback on what makes sense for a Galaxy/IRIDA deployment.**

---

## 🟡 Wave 2 — Pending User Decision

These items require a design decision or scope confirmation before implementation starts.

### libs/utils/ Relocations (Pattern B)

- [ ] **UTILS-RELOC-1**: Move `blueprint_mapper.py` from `libs/utils/` → `app/modules/` — it consumes Shiny-adjacent logic and should not live in a headless-safe lib. Decision needed: confirm move won't break connector or transformer imports.
- [ ] **UTILS-RELOC-2**: `gallery_manager.py` appears in both `libs/utils/src/utils/` and `libs/viz_gallery/src/viz_gallery/` — deduplicate. Decision needed: which copy is canonical? Delete the other and fix all imports.

### app/modules/ Two-Category Law Refactor (ADR-045)

- [ ] **ADR045-REFACTOR**: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law (modules must be headless-safe; Shiny wiring belongs in `app/handlers/`). Decision needed: scope and migration plan before touching live handlers. See audit §4A.


### UI - Persona scoping [TODO Define exactly - USER/AI discussion]

- [ ] "simple view" - Allow eg. hide left sidebar, allow hiding the tiers pannel
- [ ] Allow T1 hiding (default T2) for static personas - hidign the banner
- [ ] Allow side bar functionalities defined in different scripts ? would that allow to eg. have special configuration UI for specific deployments ?
- [ ] Import metadata - VS import all data scoping - ensure can add one by one eg if different directory ? 
- [ ] Ensure can fix project selector to project while being "autonomous" and add metadata update / choose data for the specific manifest. Choosen 


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

- [ ] **23-C**: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D**: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E**: Per-system quick-start guides (Galaxy / IRIDA / server / local).

### Filter / Propagation (enhancements)

- [ ] **PROP-2**: "Filter inventory" panel — effective filter set per plot with per-filter tooltip (affected/skipped plots).
- [ ] **PROP-3**: Propagation TubeMap — graph viz of audit blast radius, nodes ✅/⚠️/❌. Needs own design pass + ADR.
- [ ] **22-J-10**: Aesthetic propagation (color/shape/fill) — deferred until gallery-clone or wrangling surface supports aesthetic overrides.

### Export (enhancements)

- [ ] **EXPORT-2**: Selective export — per-tier checkboxes (T1/T2/T3 data, recipes, filter trace, Quarto report, README).
- [ ] **EXPORT-3**: Quarto HTML report — typography, plot placement, methods section, TOC polish.
- [ ] **EXPORT-4**: Global export — per-plot height/width control before bundling.
- [ ] **EXPORT-TUBEMAP**: Embed static tube map SVG in global export Quarto report. Requires headless/static render path for `BlueprintMapper.generate_cy_elements()`. Depends on Blueprint Architect being stable.

### Gallery & UI

- [ ] Gallery: Re-verify "Clone to Sandbox" after ADR-057 sidebar refactor. Decide how. *(Deferred — Gallery needs dedicated work sprint before tackling clone flow.)*
- [ ] **GALLERY-MAP** `[investigation]`: Map chart types (choropleth, hexbin map, bubble map, cartogram). Blocked — `geom_map` requires GeoDataFrame. Needs: spatial manifest format + geopandas integration design.
- [ ] **GALLERY-FLOW** `[investigation]`: Flow / network chart types (Chord diagram, Sankey, network graph, arc diagram, edge bundling). Blocked — plotnine has no native support. Needs feasibility study.
- [ ] **Taxonomy Data Audit** `[@user]`: Verify/correct tags in `assets/gallery_data/*/recipe_manifest.yaml`.
- [ ] Gallery thumbnails for faster visual scanning.
- [ ] **UX-GALLEXP-1**: Gallery Explorer right sidebar — functionality TBD (currently static help text).
- [ ] **UX-DEVINSP-1**: Test Lab right sidebar + left sidebar redesign — functionality TBD.
- [ ] **UX-CSS-DEMO** `[@user]`: Review `assets/demo/demo_vetinst.css` after default theme finalised.
- [ ] **UX-NOTIF-2**: Persist `notification_log` to the T3 ghost so alerts survive a page refresh. Hook into `audit_stack.py` `_notify` calls; on session restore, reload into `notification_log` reactive. Linked to UX-NOTIF-1 (ADR-060).

### VizFactory

- [ ] `geom_map` — deferred; requires spatial data (GeoDataFrame). Uncomment when spatial manifests introduced.
- [ ] **21-F-7**: Add `scale_x_discrete` / `scale_y_discrete` to manifests where Year/ST columns are categorical.

### Technical Debt

- [ ] **Unified Materialization**: `debug_wrangler.py` / `debug_assembler.py` — auto-create dated `tmpAI/{date}/{lineage}/` subfolders (use `get_debug_out_dir()` from `libs/utils`).
- [ ] **T3 lf threading**: When new T3 node types (rename, derive, pivot) are added, thread them through `_apply_t3_to_lf`. Design in `.antigravity/tasks/design_sge_lineage_t3.md`.

### Blueprint Architect

- [ ] **TubeMap aesthetics** — tighter rail/tube look; rename 'ref' → 'Add' in nodes and legend.
- [ ] Full Blueprint Architect debug pass (field contracts, lineage rail, Zone C layout).
- [ ] **Action Registry Parity** (18-F): Expose 175+ `@register_action` entries in UI.
- [ ] **Visual Forking** (18-F): Select node → initiate new branch → YAML additions.
- [ ] **Field Gap Analysis tool**: Field name → walk lineage to earliest insertion point.
- [ ] **Forward propagation hint**: Show which output_fields / final_contract files need updating.
- [ ] **UX-NOTIF-3**: Project-load notification for Blueprint Architect manifest reload. Hook into `blueprint_handlers.py` after a successful manifest import (`btn_import_manifest` path). Low priority; tackle during Blueprint debug pass.


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

**Phase 24 commits:** `89bb5ef` `890b609` `f540cbf` `d50197e` `4c38f26` `18dbd46` `f0f7d92` `2393e50` `0b50fbd`
**Phase 25 commits:** `294814e` `9b66656` `72726df` `45591ac` `95b48ac` `dc4464c` `320f6bf`



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
