# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-09 (task hygiene — all [x] blocks archived; sections reorganised) by @dasharch

---

## 🔴 Open Issues

### Runtime Error Discipline (ADR-079, placeholder)

**Why separate from ADR-078:** runtime errors have a different audience (analyst, not operator), different fix surface (data/manifest, not config), and different render path (Shiny notification / plot overlay, not stderr).

- [ ] **DIAG-RUNTIME-ADR** `[opus/high]`: Author ADR-079. Open questions: separate class vs extend `DeploymentError`; render path per category; how user discovers what caused the failure; whether errors are captured in export audit trail. **Trigger:** when Phase C largely complete OR first runtime-error pain point becomes blocking.
- [ ] **DIAG-RUNTIME-INGESTION-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/ingestion/src/ingestion/ingestor.py` — file-not-found, encoding errors, schema mismatches, sanitization rejections.
- [ ] **DIAG-RUNTIME-ASSEMBLER-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/transformer/src/transformer/data_assembler.py` — `ColumnNotFoundError`, `SchemaError` on join, dtype mismatches, empty result frames, Cartesian-product blowups.
- [ ] **DIAG-RUNTIME-WRANGLER-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/transformer/src/transformer/data_wrangler.py` — action-name not registered, action arg validation against `ui_schema`.
- [ ] **DIAG-RUNTIME-VIZFACTORY-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/viz_factory/src/viz_factory/viz_factory.py` — component not registered, missing required aesthetic, plotnine render exceptions.
- [ ] **DIAG-RUNTIME-T3APPLY-1** `[deferred until DIAG-RUNTIME-ADR]`: T3 Apply path failures in `app/handlers/audit_stack.py`.
- [ ] **DIAG-RUNTIME-BLUEPRINT-1** `[deferred until DIAG-RUNTIME-ADR]`: Manifest fragment validation failures during BLUEPRINT IDE editing.

> Completed: EXPORT-HASH-2, EXPORT-VERSION-1, EXPORT-IMG-META-1, EXPORT-AUDIT-COMPLETE-1, INGEST-SANITIZE-1, THEATER-1, STATIC-VIEW-1a, STATIC-VIEW-1b, CSS-BADGE-PROPAG-1, CSS-ERROR-RED-DECIDE. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

---

## 🟡 Wave 2 — Pending / Open

### app/modules/ Two-Category Law Refactor (ADR-045)

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law. Decision needed: scope and migration plan before touching live handlers. See audit §4A. [Not sure if wrong — it's part of the app itself]

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

> Completed: UTILS-RELOC-2, UI-TITLE-1, IMPORT-UI-1, PREVIEW-ALLROWS-1, THEATER-1. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

---

## RESEARCH / DECIDE

- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — manifest hashes + data hashes in DB associated with results; LIMS link in audit report; configurable output path per persona. ADR decision deferred until pilot funding identifies a concrete LIMS target.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search functionality in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] Improve the lab functionalities → collect all info disseminated across Test Lab, Blueprint, and Gallery into a coherent developer workflow. Needs dedicated design session.
- [ ] Audit apply improvement: apply to everything except those… to facilitate selection by exclusion.
- [ ] **HELP-INLINE-1** `[sonnet/medium]`: Per-workspace contextual help modals. `?` button → `ui.modal_show()` with content from `app/src/help/<workspace>.md`. Write initial help content for Home and Blueprint.

> Completed: HELP-DOCS-1. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

---

## 🟣 Blueprint Architect — Open Tasks

> Completed: all ADR-076 MVP-1 items (BP-AGENT-1 through BP-AGENT-CSS-1), BP-FORMS-1, BP-ESCAPE-1, BP-UNDO-1, BP-HELP-1, BP-FLAG-1, TubeMap aesthetics, UX-NOTIF-3, LINEAGE-NAV-1, LINEAGE-EXPORT-1, BP-SCHEMA-1, SCHEMA-VERIFY-ACTIONS-1, SCHEMA-VERIFY-GEOMS-1, BP-AGENT-FLAG-1. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

### Blueprint IDE Forms (ADR-075) — remaining

- [ ] **BP-COLOR-1** `[sonnet/medium]`: Color widget — column mapping toggle, palette library picker, hex picker, `from_project_colors` slot reserved as v2 placeholder.

### Blueprint Architect — Other

- [ ] Full Blueprint Architect debug pass (field contracts, lineage rail, Zone C layout).
- [ ] **Action Registry Parity** `[sonnet/high]` (18-F): Expose 175+ `@register_action` entries in UI.
- [ ] **Visual Forking** `[sonnet/high]` (18-F): Select node → initiate new branch → YAML additions.
- [ ] **Field Gap Analysis tool** `[sonnet/medium]`: Field name → walk lineage to earliest insertion point.
- [ ] **Forward propagation hint** `[sonnet/medium]`: Show which output_fields / final_contract files need updating.
- [ ] **Define** `[opus/high]` **[NEEDS DISCUSSION WITH USER — research ready]**: ADR for Blueprint Architect full feature set — functionalities, help develop without code, input/output contracts, action insertions, update data view for selected lineage, improved data inspection, joint definitions, work in T1/T2/T3, definition of groups and plot recipe.
  - **Research & discussion prep:** [.claude/design/blueprint_full_feature_set_research.md](../../.claude/design/blueprint_full_feature_set_research.md) — read TL;DR (§0), then §6 (7 open decision points)
  - **Proposed ADR ID:** ADR-082 — "BLUEPRINT Full Feature Set & Build-Mode Contract"
  - **Eve's input needed on:** Q1 (preview trigger), Q2 (T3 boundary), Q5 (joint UI), Q7 (data inspection scope) — others have clear leans
  - **Pre-discussion reading:** `.claude/design/spaces/BLUEPRINT.md` (18 functionalities, ~5 min) + `.claude/knowledge/blueprint_architect_ux_spec.md` (~10 min) + research doc §6 (~10 min)

---

## 🟡 Deferred / Backlog

### Multi-System Deployment (Phase 23 C–E)

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).

### Filter / Propagation

- [ ] **PROP-2** `[sonnet/medium]`: Filter inventory panel — effective filter set per plot with per-filter tooltip.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR.
- [ ] **22-J-10** `[sonnet/medium]`: Aesthetic propagation (color/shape/fill) — deferred until GALLERY-CLONE-DECOUPLE-1 ships.

### Export

- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Depends on Blueprint Architect stability.

> Completed: EXPORT-2, EXPORT-3, EXPORT-4. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

### Gallery & UI

- [ ] **GALLERY-CLONE-DECOUPLE-1** `[sonnet/high]`: Decouple gallery clone from WrangleStudio. Two bugs to fix together:
  1. **ADR-071 violation:** `WrangleStudio` instantiated unconditionally in `server.py` — must be gated on `developer_mode_enabled`.
  2. **Broken clone for `project-independent` persona:** clone silently writes to WrangleStudio with no UI.
  **Fix:** Replace `wrangle_studio.logic_stack.set(valid_nodes)` in `gallery_handlers.py` with a Home T3 transplant — insert a `developer_raw_yaml` RecipeNode into `_pending_t3_nodes` in `home_state`. Gate "Send to T3" on `bootloader.is_enabled("t3_sandbox_enabled")` (§12e). Remove `wrangle_studio` kwarg from `gallery_handlers.define_server()`. Gate `WrangleStudio` instantiation in `server.py`.
  **Unblocks:** 22-J-10 (aesthetic propagation).
- [ ] **GALLERY-MAP** `[opus/high]` `[investigation]`: Map chart types. Blocked — `geom_map` requires GeoDataFrame; needs spatial manifest format + geopandas integration design.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[investigation]`: Flow / network chart types. Blocked — plotnine has no native support; needs feasibility study.
- [ ] Gallery thumbnails for faster visual scanning.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.
- [ ] **UX-DEVINSP-1** `[sonnet/medium]`: Test Lab right sidebar + left sidebar redesign — functionality TBD.

> Completed: UX-NOTIF-2, Gallery Re-verify (superseded). See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

### VizFactory

- [ ] `geom_map` — deferred; requires spatial data (GeoDataFrame).
- [ ] **21-F-7**: Add `scale_x_discrete` / `scale_y_discrete` to manifests where Year/ST columns are categorical.
- [ ] **VIZFAC-PLOT-CASCADE-1** `[opus/high]` `[design-thinking]`: Design the plot configuration priority cascade. Open questions to resolve before any implementation:

  **Proposed priority order (highest wins):**
  1. `spec:` — explicit per-plot settings in `analysis_groups.<group>.plots.<id>.spec`
  2. Optimization layer — computed at render time from data (auto-label sizing, axis rotation, density-aware positioning).
  3. `plot_defaults:` — manifest-level fallback block.
  4. VizFactory built-in defaults.

  **Design questions:**
  - What exact keys belong in `plot_defaults:`? Define schema before wiring.
  - Where does the merge happen? `VizFactory.render()` is the natural merge point.
  - **Optimization layer scope (DECIDED):** purely visual/aesthetic adaptation — no data transformation, no filtering.
  - **Optimization approach (DECIDED):** Path B (two-pass render) is correct long-term; Path A (data-aware pre-pass) is acceptable MVP. Both deferred — current `_auto_adjust_axis_labels()` stays as-is.
  - How does T3 `aesthetic_override` interact? T3 > spec > optimization > plot_defaults > built-ins.
  - Blueprint IDE: `plot_defaults` should be a manifest-level settings panel, not per-plot.

  **Suggested output:** `.claude/design/plot_config_cascade.md` spec doc, then concrete implementation tasks.

### Audit Infrastructure

- [ ] **AUDIT-FIRST-TRIAGE-1** `[haiku/low]`: After first scheduled audit runs fire, triage all unprocessed reports per `audit_triage_protocol.md`. Run `grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md` to find them.

> Completed: AUDIT-TIMERS-1. See [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md).

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
- [ ] **CODE-DOCS-RETROSPECTIVE** `[deferred — pre-deployment review sprint]`: Developer-level docstrings across all `libs/` + `app/`. Tier A (module header) + Tier B (public functions) + Tier C (`@register_action` / `@register_plot_component`). Implementation order: `libs/transformer/` → `libs/viz_factory/` → `app/handlers/` → remaining libs → `app/src/`. Write `scripts/audit_code_quality.py` first.

---

## 🟡 Pending Bio-Scientist Enhancements

_No current enhancement requests. Append items here using the `[ENHANCEMENT REQUEST]` protocol (`rules_persona_bioscientist.md §4-A`) when a manifest design session exposes a missing action or plot component._

---

## 👤 User Required

Tasks requiring user decision, user action, or explicit discussion before implementation can proceed.

- [ ] **[@user] Taxonomy Data Audit**: Verify/correct tags in `assets/gallery_data/*/recipe_manifest.yaml` against `assets/gallery_data/TAXONOMY_CHEATSHEET.md`.
- [ ] **[@user] UX-CSS-DEMO**: Review `assets/demo/demo_vetinst.css` after default theme is finalised.
- [ ] **[FEATURE]** Label x/y axis adjustment module — edit title, policy change, color changes, points display — registered in audit. Large feature, grant-exploration candidate.
- [ ] **[TO DISCUSS]** Lab script: Extract pilot manifest (reconstitution of lineage) — improve reusability.
- [ ] **[TO DISCUSS]** Lab script: Create tool-specific manifest (e.g. single-sheet variant).
- [ ] **[TO DISCUSS]** Lab script: Combine manifests — format detection, common datasets, branching.
- [ ] **[TO DISCUSS]** Blueprint full feature ADR (ADR-082) — see `.claude/design/blueprint_full_feature_set_research.md` §6. Eve's input needed on Q1 (preview trigger), Q2 (T3 boundary), Q5 (joint UI), Q7 (data inspection scope) before authoring.

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
| Phase 32 / May-09 hygiene | Export enhancements (EXPORT-2/3/4), UX-NOTIF-2 ghost persistence, ADR-076 MVP-1 complete, Open Issues + CSS batch archived | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |

---

## Archive Pointers

- [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) — Phase 31 + 32: all ADR-076 MVP-1, EXPORT-2/3/4, UX-NOTIF-2, CSS hygiene, Open Issues Export/Session/UX/Sidebar batch, Blueprint IDE Forms batch
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
