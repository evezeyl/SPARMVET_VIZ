# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-09 (ADR-076 BLUEPRINT AI Agent Helper revised — added §10 tool-call mechanism + §11 subprocess isolation; streaming dropped; tasks expanded with BP-AGENT-PARSER-1, BP-AGENT-PANEL-1, BP-AGENT-CSS-1) by @dasharch

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

### Sidebar Slot Registry (ADR-073)

- [x] **SIDEBAR-CONFIGS-1** `[haiku/low]`: Create `config/ui/sidebars/` directory with shared sidebar YAML panel-list files for all workspace × persona-tier combinations (home_static_left, home_simple_left, home_advanced_left, home_advanced_right, blueprint_standard_left/right, gallery_focus_left, testlab_standard_left). Update all 6 persona templates to use `workspaces:` section with `!include` references. ✅ 2026-05-09

- [x] **SIDEBAR-REGISTRY-1** `[sonnet/high]`: Implement ADR-073 core:
  - `app/modules/sidebar_registry.py` — `PANEL_REGISTRY` dict (panel type → gate flag). Headless-safe, no Shiny imports.
  - `bootloader`: added `SidebarConfig` dataclass + `get_sidebar_config(workspace, side)` with `!include` support via subclass loader.
  - `home_theater.py`: replaced hardcoded accordion with slot-list iteration; added `project_info`, `deployment_info` panel renderers; right sidebar now iterates slot types too.
  - `ui.py`: replaced `bootloader.is_enabled("t3_sandbox_enabled")` with `bootloader.get_sidebar_config("home", "right").visible` — fixes ADR-053 violation (task 25-O).
  - All 8 persona templates updated with `workspaces:` section. ✅ 2026-05-09

- [x] **SIDEBAR-VALIDATE-1** `[sonnet/medium]`: Implement compatibility validation:
  - `app/modules/sidebar_validator.py` — `SidebarValidator` class: checks panel types against registry, `!include` targets exist, gate-flag consistency. Also fixed `PersonaValidator.validate_file()` to support `!include`.
  - `scripts/validate_persona_config.py` — CLI wrapper running both validators. Flags: `--persona <id>`, `--all`, `--strict`. 8/8 templates PASS.
  - `app/src/server.py` — `SidebarValidator` runs at startup alongside `PersonaValidator`; errors block startup. ✅ 2026-05-09

- [ ] **STATIC-VIEW-1** `[sonnet/low]`: "Zero functionality" static persona polish:
  - [ ] **STATIC-VIEW-1a** `[haiku/low]`: Hide the view-title banner (central plot-group header strip) in fully static personas — it adds no value when there are no controls and may clutter a clean presentation layout. Gate on a new persona flag or reuse `interactivity_enabled: false`.
  - [ ] **STATIC-VIEW-1b** `[sonnet/low]`: T2 as default displayed tier — in static personas, T2 (analysis-ready) should be shown on first render instead of T1 raw. T1 toggle should not be exposed. Decide: force `active_tier=T2` in bootloader for `interactivity_enabled: false` personas, or add an explicit `default_tier` field to the persona template.
  - [x] **STATIC-VIEW-1c** `[sonnet/low]`: Left sidebar treatment for static personas — **Decided 2026-05-09 (ADR-073).** Sidebar visibility is controlled by `workspaces.home.left_sidebar.visible` in persona template (not hardcoded). Static personas use `project_info` + `deployment_info` + `export` panel slots. Hiding is allowed when `export_enabled: false` AND no informational panels needed. ✅ 2026-05-09

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
- [x] **TO DISCUSS**: Toggle "show all data" — decided 2026-05-09 → **PREVIEW-ALLROWS-1** ✅
- [ ] **TO DISCUSS — lab script**: Extract pilot manifest (reconstitution of lineage) — improve reusability (e.g. manifest for results from a specific tool)
- [ ] **TO DISCUSS — lab script**: Create tool-specific manifest (e.g. single-sheet variant of above)
- [ ] **TO DISCUSS — lab script**: Combine manifests — format detection, common datasets, branching
- [x] **TO DISCUSS**: Prepare to connect — decided 2026-05-09 → **DEPLOY-CONNECT-1** below ✅

- [ ] **DEPLOY-CONNECT-1** `[sonnet/medium]`: Posit Connect deployment — editable library install handling.
  **Context (from `connect.md` + `considerations.md`):** Connect uses an isolated Python environment built from `requirements.txt` (or `manifest.json`). `pip install -e ./libs/xxx` (editable installs) do NOT transfer to Connect — the `./libs/` source tree is bundled and the env rebuilt. The `rsconnect-python` bundler must be told about each local lib.
  **Subtasks:**
  - [ ] Add each editable lib as a relative path entry in `requirements.txt`: `-e ./libs/ingestion`, `-e ./libs/transformer`, `-e ./libs/utils`, `-e ./libs/viz_factory`, `-e ./libs/viz_gallery`, `-e ./libs/connector`, `-e ./libs/blueprint_arch`, `-e ./libs/test_lab` — Connect will run `pip install -e ./libs/xxx` from the bundled source tree inside its isolated env.
  - [ ] Document `app/src/main.py` as the entry point for `rsconnect-python` bundle: `rsconnect deploy shiny . --entrypoint app/src/main.py`
  - [ ] Deployment profile path strategy: set `SPARMVET_PROFILE` as an environment variable in Connect's config, pointing to a profile YAML bundled in `config/deployment/connect/connect_profile.yaml`. Add a `connect_profile.yaml` template.
  - [ ] Smoke test: clean venv from scratch (no local `.venv`), run `scripts/install_libs.sh`, then `python app/src/main.py` — verify no import errors before pushing to Connect.
  - [ ] Update `scripts/install_libs.sh` if needed to support both editable (local dev) and Connect (bundled) install paths.
  **Pre-existing done:** CDN vendoring (DEPLOY-CDN-1 ✅), nav gating (DEPLOY-MODULES-1 ✅), vendor manifest (VENDOR-MANIFEST-1 ✅), install script (DEPLOY-LIBS-1 ✅), no secrets in source (ADR-071 rule 3 ✅).

- [x] **REVIEW-SCOPING-1 — T3 bundle dependency rule**: Already implemented as PersonaValidator Rule 6 (PERSONA-CONFIG-VALIDATE-1). Closed. ✅ 2026-05-09

- [x] **REVIEW-EXPORT-FLAGS — EXP_GROUP as separate persona flag**: **Decided 2026-05-09 — won't add separate flag.** One `export_enabled` gates all scope levels (global / group / plot). The 3-way scope toggle is already implemented. Per-scope lineage completeness (each plot's recipes + data + audit included) is governed by `EXPORT-AUDIT-COMPLETE-1`, not a flag. ✅ 2026-05-09

- [x] **REVIEW-IMPORT-PANEL — META_ING / IMP_HLP / single import UI**: ✅ 2026-05-05 **Decided.** Single browse + mapping panel. `IMP_HLP` on → mapping shows all manifest data sources (metadata included). `META_ING` on alone → mapping shows metadata schema only. `IMP_HLP` implies `META_ING` (superset). Metadata import behavior: **overwrite** (not merge). Two persona flags remain in config for scoping control; UI has one entry point. See **IMPORT-UI-1** for implementation.

- [x] **REVIEW-AUTOSAVE-CACHE — caching vs autosave separation**: **Decided — already implemented.** Parquet cache (T1 materialisation) always written for performance, independent of `autosave` flag. `autosave` flag controls ghost-save (session JSON) only. Implemented in SESSION-PERSONA-1. ✅ 2026-05-09

- [x] **REVIEW-HASH-EXPORT — hash visibility and export gating**: **Decided 2026-05-09 — always include, no flag.** Provenance has no reason to be optional (ADR-069 Rule 1). All hashes (manifest SHA256, per-source-file SHA256 table, data_batch_hash roll-up, decision_hash) always present in every export bundle. ADR-069 amended to clarify per-source-file table requirement. ✅ 2026-05-09

- [x] **REVIEW-UI-TITLE-SUBT — manifest-driven UI title/subtitle**: ✅ 2026-05-05 **Decided.** Resolution order: persona config override > manifest field > nothing shown. Manifest fields: `info.display_name` (title), `info.subtitle` (subtitle — new short dedicated field). `info.description` remains free-form long description, NOT shown in UI header. `UI_TITLE` off → both title and subtitle hidden (subtitle depends on title). See **UI-TITLE-1** for implementation.


### UI - Functionality debugging (TODO / User )
- [ ] Exports -> retest / debug
- [ ] proper definition of the session ghost save and save function when Tier 3 activated
- [ ] import and mapping of the files to the manifest 
- [ ] **PREVIEW-ALLROWS-1** `[sonnet/low]`: Add "Show all rows" toggle to data preview. **Decided 2026-05-09.** Spec:
  - Toggle button next to the preview row-count label. Off by default (100-row cap). On = uncapped (`.collect()` full frame).
  - Tooltip on hover: *"Showing all rows — may be slow for large datasets."*
  - Respects active tier (T1 / T2 / T3) — shows whichever frame the tier toggle selects, unfiltered.
  - Not persona-gated (useful for all users). Persisted in `home_state` per session.
  - Implementation: `app/handlers/home_theater.py` `home_data_preview` render — replace hardcoded `head(100)` with conditional on a `reactive.Value[bool]` toggled by a new `input.preview_show_all`.
- [ ][FEATURE] Label - x y axis adjustment module - Automation / User adjustment panel ? Including eg. some connectors to the visualisation layer on t3.
  Allow edit title, allow policy change, color changes, points display — all need to be registered in the audit → we need an edit palette menu. Problem: plots are not interactive so need to define the list of adjustable elements per plot type. Large feature, grant-exploration candidate.

---

## RESEARCH - HOW TO - DECIDE

- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — how to store manifest hashes + data hashes in a database associated with results; associate a LIMS with the audit report; configurable output path per persona. **ADR decision deferred** until pilot funding project advances and a concrete LIMS target is identified. Note for ADR when ready: likely needs a new deployment profile `locations` key (e.g. `audit_db`) + a new export surface (machine-readable JSON sidecar per bundle).
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search functionality in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] Improve the lab functionalities → collect all information that is disseminated across Test Lab, Blueprint, and Gallery into a coherent developer workflow. Needs dedicated design session when Test Lab is further along.
- [ ] audi apply: improvement e.g. apply to everything except those… to facilitate selection by exclusion.

### In-app contextual help — **DECIDED 2026-05-09**

**Decision:** Air-gapped first (works everywhere). Two-tier approach:
1. **Contextual cards** (per user space — `HELP-INLINE-1`): `?` button per workspace (Home, Blueprint, Gallery, Test Lab) → opens a `ui.modal_show()` with a short Markdown summary for that space. Content stored as `.md` files in `app/src/help/` (bundled with app, no internet required).
2. **Full manual** (optional, `HELP-DOCS-1`): `docs/_site/` Quarto-rendered HTML bundled with the app and served via Shiny static assets as `/docs/`. A "Full documentation →" link in each contextual card points to `/docs/index.html`. Works air-gapped. Only generated/served if `docs/_site/` is present at deployment time (build step, not always required).

**Consequence:** Air-gapped deployments always get contextual cards. Full manual is opt-in per deployment (run `quarto render docs/` first, include `_site/` in bundle).

- [ ] **HELP-INLINE-1** `[sonnet/medium]`: Implement per-workspace contextual help modals. `?` button in each workspace header → `ui.modal_show()` with content from `app/src/help/<workspace>.md`. Write initial help content for Home and Blueprint.
- [ ] **HELP-DOCS-1** `[haiku/low]`: Bundle `docs/_site/` as Shiny static assets served at `/docs/`. Conditional: only if `_site/` exists. Add "Full documentation →" link to each contextual card. CI note: add `quarto render docs/` to deployment checklist.

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

- [ ] **REPO-CLEAN-1** `[haiku/low]` `[soon — after backup]` `[repo-hygiene]`: Full git history purge — remove EVE_WORK/, session logs, .vscode user files from ALL past commits (not just HEAD). Prerequisite: backup to external disc + gdrive sync run overnight.
  ```bash
  # 1. Verify backup exists on external disc
  # 2. Install tool if needed:
  pip install git-filter-repo
  # 3. Rewrite history (removes the paths from every commit):
  git filter-repo --path EVE_WORK/ --path .claude/logs/sessions/ \
    --path .claude/logs/handoffs/archive/ \
    --path .vscode/bookmarks.json --path .vscode/favorites/ \
    --path .vscode/settings.json --path .directory \
    --invert-paths
  # 4. Force-push (only branch dev, no collaborators):
  git push origin dev --force
  # 5. Re-clone or hard-reset any other checkouts
  ```
  Note: rewrites all commit SHAs. Not blocking anything — defer until backup confirmed.

- [ ] **Unified Materialization** `[haiku/low]`: `debug_wrangler.py` / `debug_assembler.py` — auto-create dated `tmpAI/{date}/{lineage}/` subfolders (use `get_debug_out_dir()` from `libs/utils`).
- [ ] **T3 lf threading** `[sonnet/medium]`: When new T3 node types (rename, derive, pivot) are added, thread them through `_apply_t3_to_lf`. Design in `.claude/tasks/design_sge_lineage_t3.md`.
- [ ] **PYPROJECT-DEPS-1** `[haiku/low]` `[repo-hygiene]`: Verify all 8 `libs/*/pyproject.toml` files declare `libs/utils` as an explicit dependency wherever they import from it. Two-tier model (ADR-011 amendment 2026-05-09): any domain lib importing `utils` must list it in `[project.dependencies]`. Also add `pattern_helper` to `libs/utils/` public API once BP-PATTERN-1 is implemented.

- [ ] **ACTION-RENAME-1** `[sonnet/medium]` `[repo-hygiene]`: Audit all `@register_action` names in `libs/transformer/` and `@register_plot_component` names in `libs/viz_factory/` for alignment with Polars/Plotnine naming. For each rename: (1) record `{old_name → new_name}` in a migration table; (2) implement compatibility shim in the registry (old name logs a deprecation warning and delegates to new name); (3) provide `scripts/migrate_manifests.py` — scans all YAML manifests under `config/manifests/`, all persona templates, and gallery recipe files, replaces old action names with new, reports changes. Run scan as part of the task completion gate before removing shims.

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

- [x] **LINEAGE-NAV-1** `[sonnet/medium]`: Implement `build_plot_lineage(plot_id, manifest_path)` and `get_plot_ids_in_group(group_id, manifest_path)` in `libs/blueprint_arch/.../manifest_navigator.py`. Backward trace: data sources → T1 → T2 → join/assembly → plot spec, as ordered list of step dicts. Forward trace: reads `analysis_groups[group_id].plots`. T3 overlay appended by caller. ADR-074. ✅ 2026-05-09
- [x] **LINEAGE-EXPORT-1** `[sonnet/high]`: Implement `lineage/lineage_graph.json` generation in `export_handlers.py` (shared-node DAG, one file per export scope, no per-plot duplication); add to `report.qmd` template: Mermaid flowchart + step summary table + JSON explanation note. ADR-074. ✅ 2026-05-09
- [x] **BP-SCHEMA-1** `[sonnet/high]`: Add `ui_schema` kwarg to `@register_action` and `@register_plot_component`; implement `schema_registry.py` in `blueprint_arch`; populate schemas for 19 transformer actions and 7 viz_factory components as first pass. `allow_extra_params: True` + `wraps` on all geom schemas. ADR-075. ✅ 2026-05-09

- [x] **SCHEMA-VERIFY-ACTIONS-1** `[haiku/low]`: Verify all 19 annotated transformer action `ui_schema.params` against the actual function body. ✅ 2026-05-09
  **Result:** All 19 actions verified. Fixed 4 param mismatches:
  - `filter_eq`: added fallback `columns` param (function tries `columns[0]` as fallback)
  - `mutate`: added fallback `target_column` param (function accepts both `column` and `target_column`)
  - `sort`: added fallback `by` param (function tries `spec.get("by")` before `columns`)
  - `join`: confirmed `right_ingredient` correct (manifest-level param resolved by DataAssembler, not direct spec.get())
  Updated 3 files: `cleaning/core.py`, `cleaning/expressions.py`, `cleaning/analytical.py`.

- [x] **SCHEMA-VERIFY-GEOMS-1** `[haiku/low]`: Verify all 7 annotated viz_factory component `ui_schema.params` against the actual plotnine function signatures. ✅ 2026-05-09
  **Result:** All 7 geoms verified. Coverage:
  - `geom_boxplot`: 12 params (alpha, fill, colour, size, width, notch, outlier_colour, outlier_shape, outlier_size, linetype, position, stat) + `allow_extra_params: true`
  - `geom_point`: 9 params (alpha, colour, fill, size, shape, stroke, position, stat, na_rm) + `allow_extra_params: true`
  - `geom_line`: 9 params (alpha, colour, size, linetype, lineend, linejoin, position, stat, na_rm) + `allow_extra_params: true`
  - `geom_bar`: 9 params (alpha, fill, colour, size, linetype, width, stat, position, na_rm) + `allow_extra_params: true`
  - `geom_histogram`: 10 params (bins, binwidth, alpha, fill, colour, size, linetype, position, stat, na_rm) + `allow_extra_params: true`
  - `geom_tile`: 9 params (alpha, fill, colour, size, linetype, width, height, stat, na_rm) + `allow_extra_params: true`
  - `labs`: 12 params (title, subtitle, caption, x, y, fill, colour, color, size, shape, alpha, linetype) + `allow_extra_params: true`
  All 7 components verified against plotnine signatures with comprehensive param coverage and `allow_extra_params` for forward compat.
- [ ] **BP-FORMS-1** `[sonnet/high]`: Implement form renderer in BLUEPRINT IDE — all widget types, column selector with upstream schema propagation on Apply, edit-in-place flow, schema invalidation markers on downstream nodes. ADR-075.
- [ ] **BP-ESCAPE-1** `[sonnet/medium]`: YAML escape hatch — read-only view (all `blueprint_enabled` personas) + editable mode (`manifest_edit_enabled`) with re-parse on save. ADR-075.
- [ ] **BP-UNDO-1** `[haiku/low]`: 20-step session undo deque for BLUEPRINT DAG state. ADR-075.
- [ ] **BP-HELP-1** `[sonnet/medium]`: Help panel — `__doc__` resolution, collapsible sections for composite actions, optional external URL button disabled in isolated deployments. ADR-075.
- [ ] **BP-COLOR-1** `[sonnet/medium]`: Color widget — column mapping toggle, palette library picker, hex picker, `from_project_colors` slot reserved as v2 placeholder. ADR-075.
- [ ] **BP-FLAG-1** `[haiku/low]`: Add `manifest_edit_enabled` flag to all six persona templates + `rules_persona_feature_flags.md` + bootloader cascade rule. ADR-075.

#### ADR-076 — BLUEPRINT AI Agent Helper

- [ ] **BP-AGENT-FLAG-1** `[haiku/low]`: Add `blueprint_agent_enabled` flag to all 6 persona templates (Group D, depends on `blueprint_enabled`). Default `false` for static / simple / advanced / independent; `true` for developer / qa. Add `blueprint_agent:` config block (`enabled`, `backend`, `model`, `api_key_env`, `endpoint`, `instructions_file`, `gallery_awareness`) to developer and qa templates. Add cascade rule (`blueprint_enabled: false` → force `blueprint_agent_enabled: false`) to `bootloader._load_persona_config()` and document in `rules_persona_feature_flags.md` Group D. ADR-076 §6. *(Note: BP-FLAG-1 above is the ADR-075 `manifest_edit_enabled` flag — separate concern.)*
- [ ] **BP-AGENT-1** `[sonnet/high]`: Implement `AgentAdapter` protocol + `ClaudeCliAdapter` (Phase 1) + `ClaudeApiAdapter` (Phase 2 stub) + `LocalModelAdapter` (Phase 3 stub) + `DisabledAdapter`. **`ClaudeCliAdapter` MUST follow the §11 isolation discipline:** dedicated `cwd={project_root}/agent_sessions/{uuid}/` per session (NOT the project root — prevents `--continue` collision with the user's terminal Claude Code session); `flock`-based single-flight lock; auth probe at init (`claude --version` + `claude --status` or trivial print probe — fall back to `DisabledAdapter` on failure). Add system prompt builder + per-turn context builder (Layer 1 + Layer 3, ADR-076 §3). Location: `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` + `agent_context.py`. Headless-safe (Two-Category Law — no Shiny imports). All backends buffered (no streaming, ADR-076 §1).
- [ ] **BP-AGENT-PARSER-1** `[sonnet/medium]`: Implement `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py` — fenced-block extractor for the `<!-- AGENT_TOOL_CALL --> ... <!-- /AGENT_TOOL_CALL -->` protocol (ADR-076 §10.1). Parses JSON inside, validates against per-tool schema (Pydantic or dataclass), dispatches to `agent_tools.py`. On parse failure, emits a structured error turn so the agent retries. Pure module; headless-safe. Required by `ClaudeCliAdapter` and `LocalModelAdapter` fallback path.
- [ ] **BP-AGENT-TOOLS-1** `[sonnet/medium]`: Implement 7 agent tools in `libs/blueprint_arch/src/blueprint_arch/agent_tools.py`: `get_available_actions`, `get_available_components`, `get_field_contract`, `get_data_schema_summary` (reuse `AquaSynthesizer` extraction logic — privacy-preserving, no raw rows; respects data visibility mode from §4), `get_current_manifest_section`, `validate_manifest_fragment`, `propose_manifest_diff`. Each wraps existing `manifest_navigator` / registry APIs. Headless-safe. ADR-076 §3 (Layer 2).
- [ ] **BP-AGENT-INSTRUCT-1** `[sonnet/medium]`: Write `config/ui/agents/blueprint_default.md` — system prompt template covering: (a) **tool-call output format** per ADR-076 §10.1 (HTML-comment marker pair + fenced JSON, exact schema per tool); (b) intake questions (Data Grain, Metric Logic, Visual Mapping per `rules_persona_bioscientist.md` §2); (c) data-science guidance (filter ordering for UI responsiveness using `row_counts` context, join key validation, two-step cast for integer-as-category `Float64 → Int64 → String`); (d) AMR/biology domain section template (resistance phenotype, MLST, ST clustering — placeholders for deployment-specific content). Create `config/ui/agents/` directory.
- [ ] **BP-AGENT-PANEL-1** `[haiku/low]`: Register `blueprint_agent_chat` panel type in `app/modules/sidebar_registry.py` with `gate_flag: "blueprint_agent_enabled"`. Add to BLUEPRINT workspace `right_sidebar.panels` slot list in `developer_template.yaml` and `qa_template.yaml` (positioned after the existing `blueprint_logic` panel). ADR-073 + ADR-076 §8. *(Required for the chat panel to mount at all — without this, BP-AGENT-UI-1 has no slot.)*
- [ ] **BP-AGENT-UI-1** `[sonnet/high]`: Chat panel render outputs in `app/handlers/blueprint_handlers.py`: cold-start greeting (adapter status + data visibility + prompt — ADR-076 §5 cold-start), conversation log (buffered, "thinking…" indicator during in-flight turn), decision summary accordion (running list, persisted across panel switches), Apply button gated **exclusively** on a pending `propose_manifest_diff`, Reject/Revise button (sends agent a turn message), data visibility toggle (off / schema_summary / full_sample — `full_sample` developer-only), single-flight UI gate (input disabled during in-flight turn). No streaming. Mount target = `blueprint_agent_chat` panel slot from BP-AGENT-PANEL-1.
- [ ] **BP-AGENT-CSS-1** `[haiku/low]`: Add `.bp-agent-*` rule block to `config/ui/theme.css` covering: chat container, message bubbles (user vs agent), thinking indicator, decision accordion, pending-diff preview, Apply/Reject buttons, data visibility toggle. Honour the existing right sidebar palette (Dark Grey #c0c0c0 background, SPARMVET Blue #345beb for primary actions). No inline styles in handler code (ADR-055).
- [ ] **BP-AGENT-REPORT-1** `[sonnet/low]`: Manifest creation report bundle. The session directory `agent_sessions/{uuid}/` is already created by BP-AGENT-1 for subprocess isolation (§11) — this task adds the report writers: `conversation.jsonl` (one JSON turn per line — appended on each turn), `report.qmd` (Quarto: goal statement, data summary, decisions, final manifest YAML, agent backend metadata — written on `end_session`), `manifest_sha256.txt` (written on `end_session`). Bundle location configurable via deployment profile (default `{project_root}/agent_sessions/`). Add `agent_sessions/` to `.gitignore`. ADR-076 §7.

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
