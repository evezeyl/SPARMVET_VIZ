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

### Deployment

- [ ] **DEPLOY-CONNECT-1** `[sonnet/medium]`: Posit Connect deployment — editable library install handling.
  - [ ] Add each editable lib as relative path entry in `requirements.txt`: `-e ./libs/ingestion`, `-e ./libs/transformer`, etc.
  - [ ] Document `app/src/main.py` as entry point for `rsconnect-python` bundle.
  - [ ] Deployment profile via `SPARMVET_PROFILE` env var; add `config/deployment/connect/connect_profile.yaml` template.
  - [ ] Smoke test: clean venv from scratch, run `scripts/install_libs.sh`, verify no import errors.

### UI Debugging

- [ ] **UX-DEBUG-EXPORT-1** `[sonnet/medium]`: Retest and debug the export pipeline end-to-end against a real data session.
- [ ] **UX-DEBUG-GHOST-1** `[sonnet/medium]`: Define and test the session ghost save/restore flow when Tier 3 is activated — confirm T3 state survives a page refresh.
- [ ] **UX-DEBUG-IMPORT-1** `[sonnet/medium]`: Test file import and schema mapping from user-uploaded files through to manifest association.

### Runtime Error Discipline

- [ ] **DIAG-RUNTIME-ADR** `[opus/high]`: Author ADR-079. Open questions: separate class vs extend `DeploymentError`; render path per category; how user discovers what caused the failure; whether errors are captured in export audit trail.

### Blueprint Architect

- [ ] **BP-DEBUG-1** `[sonnet/high]`: Full Blueprint Architect debug pass — field contracts rendering, lineage rail accuracy, Zone C layout stability.
- [ ] **BP-ACTION-PARITY-1** `[sonnet/high]`: Expose 175+ `@register_action` entries in Blueprint IDE UI (18-F).
- [ ] **BP-VISUAL-FORK-1** `[sonnet/high]`: Visual Forking — select node → initiate new branch → YAML additions (18-F).
- [ ] **BP-FIELD-GAP-1** `[sonnet/medium]`: Field Gap Analysis tool — field name → walk lineage to earliest insertion point.
- [ ] **BP-FWD-HINT-1** `[sonnet/medium]`: Forward propagation hint — show which output_fields / final_contract files need updating when a field is added or renamed.

### Gallery & Visualization

- [ ] **GALLERY-CLONE-DECOUPLE-1** `[sonnet/high]`: Decouple gallery clone from WrangleStudio. Two bugs to fix together:
  1. **ADR-071 violation:** `WrangleStudio` instantiated unconditionally in `server.py` — must be gated on `developer_mode_enabled`.
  2. **Broken clone for `project-independent` persona:** clone silently writes to WrangleStudio with no UI.
  **Fix:** Replace `wrangle_studio.logic_stack.set(valid_nodes)` in `gallery_handlers.py` with a Home T3 transplant — insert a `developer_raw_yaml` RecipeNode into `_pending_t3_nodes` in `home_state`. Gate "Send to T3" on `bootloader.is_enabled("t3_sandbox_enabled")` (§12e). Remove `wrangle_studio` kwarg from `gallery_handlers.define_server()`. Gate `WrangleStudio` instantiation in `server.py`.
  **Unblocks:** 22-J-10 (aesthetic propagation).
- [ ] **VIZ-DISCRETE-SCALE-1** `[sonnet/low]`: Add `scale_x_discrete` / `scale_y_discrete` layers to existing manifests where Year or Sequence Type columns are used as categorical x/y axes (currently render as continuous). Audit all `analysis_groups` plot specs in `config/manifests/pipelines/`.
- [ ] **VIZ-GALLERY-THUMB-1** `[sonnet/low]`: Pre-render gallery thumbnails at index build time (`refresh_gallery.py`) for faster visual scanning. Store as `preview_thumb.png` (100×75px) alongside `preview_plot.png`.

### Infrastructure & Housekeeping

- [ ] **AUDIT-FIRST-TRIAGE-1** `[haiku/low]`: After first scheduled audit runs fire, triage all unprocessed reports per `audit_triage_protocol.md`. Run `grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md` to find them.
- [ ] **TECH-DEBUG-MATERIALIZE-1** `[haiku/low]`: `debug_wrangler.py` / `debug_assembler.py` — auto-create dated `tmpAI/{date}/{lineage}/` subfolders so output paths don't collide across days.
- [ ] **HELP-INLINE-1** `[sonnet/medium]`: Per-workspace contextual help modals. `?` button → `ui.modal_show()` with content from `app/src/help/<workspace>.md`. Write initial help content for Home and Blueprint.

---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law. Decision needed: scope and migration plan before touching live handlers. [Not sure if wrong — it's part of the app itself]
- [ ] **VIZFAC-PLOT-CASCADE-1** `[opus/high]` `[design-thinking]`: Design the plot configuration priority cascade.

  **Proposed priority order (highest wins):**
  1. `spec:` — explicit per-plot settings in `analysis_groups.<group>.plots.<id>.spec`
  2. Optimization layer — computed at render time from data (auto-label sizing, axis rotation, density-aware positioning).
  3. `plot_defaults:` — manifest-level fallback block.
  4. VizFactory built-in defaults.

  **Open questions:** schema for `plot_defaults:`; merge point (`VizFactory.render()`); T3 `aesthetic_override` interaction (T3 > spec > optimization > plot_defaults > built-ins); Blueprint IDE surface for `plot_defaults`.

  **Decided:** Optimization layer = purely visual/aesthetic; Path B (two-pass render) correct long-term; current `_auto_adjust_axis_labels()` stays as-is until designed.

  **Next step:** `.claude/design/plot_config_cascade.md` spec doc, then concrete implementation tasks.

- [ ] **LAB-WORKFLOW-1** `[opus/high]`: Collect all developer workflow info from Test Lab, Blueprint, and Gallery into a coherent end-to-end developer workflow. Needs dedicated design session before implementation.
- [ ] **UX-APPLY-IMPROVE-1** `[sonnet/medium]`: Audit Apply improvement — "apply to all except…" selection-by-exclusion mode. Needs design pass before scoping.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR before implementation.

---

## ⏳ Deferred / Blocked

### Blocked by DIAG-RUNTIME-ADR (author ADR-079 first)

- [ ] **DIAG-RUNTIME-INGESTION-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/ingestion/src/ingestion/ingestor.py` — file-not-found, encoding errors, schema mismatches, sanitization rejections.
- [ ] **DIAG-RUNTIME-ASSEMBLER-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/transformer/src/transformer/data_assembler.py` — `ColumnNotFoundError`, `SchemaError` on join, dtype mismatches, empty result frames, Cartesian-product blowups.
- [ ] **DIAG-RUNTIME-WRANGLER-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/transformer/src/transformer/data_wrangler.py` — action-name not registered, action arg validation against `ui_schema`.
- [ ] **DIAG-RUNTIME-VIZFACTORY-1** `[deferred until DIAG-RUNTIME-ADR]`: Retrofit `libs/viz_factory/src/viz_factory/viz_factory.py` — component not registered, missing required aesthetic, plotnine render exceptions.
- [ ] **DIAG-RUNTIME-T3APPLY-1** `[deferred until DIAG-RUNTIME-ADR]`: T3 Apply path failures in `app/handlers/audit_stack.py`.
- [ ] **DIAG-RUNTIME-BLUEPRINT-1** `[deferred until DIAG-RUNTIME-ADR]`: Manifest fragment validation failures during BLUEPRINT IDE editing.

### Blocked by library limitations

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — library limitation]`: Register `geom_map` component in VizFactory. Blocked: plotnine has no native GeoDataFrame/spatial support; requires geopandas integration and a spatial manifest format design. Unblocks: GALLERY-MAP.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred — library limitation]`: Map chart types in Gallery. Blocked by VIZ-GEOM-MAP-1.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[deferred — library limitation]`: Flow / network chart types. Blocked: plotnine has no native network/Sankey/flow support. Requires feasibility study — candidate libs: `networkx` + custom geom, or external renderer.

### Blocked by other tasks

- [ ] **22-J-10** `[sonnet/medium]`: Aesthetic propagation (color/shape/fill) — deferred until GALLERY-CLONE-DECOUPLE-1 ships.
- [ ] **PROP-2** `[sonnet/medium]`: Filter inventory panel — effective filter set per plot with per-filter tooltip.
- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.
- [ ] **TECH-T3-THREAD-1** `[sonnet/medium]`: When new T3 node types are added, thread them through `_apply_t3_to_lf`. Design spec in `.claude/tasks/design_sge_lineage_t3.md`.

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
