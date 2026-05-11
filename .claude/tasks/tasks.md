# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-11 (DEPLOY-CONNECT-1, UX-DEBUG-* complete) by @dasharch

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

> Status: COMPLETED. All 7 items (DOC-DRIFT-1, DOC-DRIFT-EMOJI, DOC-GAP-1 through DOC-GAP-5) archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Audit Fixes — ADR Compliance (2026-05-09)

> Status: COMPLETED. All items (ADR-078-ACTIONS-1, TRANSFORMER-SUITE-FIX) archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Deployment

> DEPLOY-CONNECT-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### UI Debugging

> UX-DEBUG-EXPORT-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)
> UX-DEBUG-GHOST-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)
> UX-DEBUG-IMPORT-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Runtime Error Discipline

> DIAG-RUNTIME-BASE-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-AUDIT-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-INGESTION-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-ASSEMBLER-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-WRANGLER-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-VIZFACTORY-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-T3APPLY-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> DIAG-RUNTIME-BLUEPRINT-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Blueprint Architect

> BP-LINEAGE-NAV-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> BP-VISUAL-FORK-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Gallery & Visualization

> GALLERY-CLONE-DECOUPLE-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> 22-J-10: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### VizFactory Cascade — Unblocked 2026-05-11

> VIZFAC-RENDER-WIRE-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)
> VIZFAC-DEFAULTS-DOCS-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Audit Fixes — Library Tests & Dependencies (2026-05-09)

> Status: COMPLETED. All 4 items (LIB-TESTS-BLUEPRINT-1, LIB-TESTS-VIZ-TIMEOUT-1, PKG-PLOTNINE-PATCH-1, PKG-IMPORTLIB-MAJOR-1) archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Infrastructure & Housekeeping

> AUDIT-FIRST-TRIAGE-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)
> HELP-INLINE-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] Can we leverage python great docs to improve the documentation? particularly for the UI - but also for the rest of the libraries and for developers? <>https://github.com/posit-dev/great-docs>

- [ ] **ADR045-REFACTOR** `[opus/high]`: Several files in `app/modules/` import `shiny` directly, violating the Two-Category Law. Decision needed: scope and migration plan before touching live handlers. [Not sure if wrong — it's part of the app itself]

#### Cascade implementation (derived from VIZFAC-PLOT-CASCADE-1 design — spec at `.claude/design/plot_config_cascade.md`)

> VIZFAC-RESOLVER-1: COMPLETED 2026-05-11. VIZFAC-RENDER-WIRE-1 + VIZFAC-DEFAULTS-DOCS-1 moved to **Do Now**. VIZFAC-T3-OVERRIDE-1, VIZFAC-T3-EXPORT-1, VIZFAC-BLUEPRINT-FORM-1 moved to **Deferred/Blocked**. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

- [ ] **LAB-WORKFLOW-1** `[opus/high]`: Collect all developer workflow info from Test Lab, Blueprint, and Gallery into a coherent end-to-end developer workflow. Needs dedicated design session before implementation.
- [ ] **UX-APPLY-IMPROVE-1** `[sonnet/medium]`: Audit Apply improvement — "apply to all except…" selection-by-exclusion mode. Needs design pass before scoping.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Easy lookup / search in-app (cross-manifest, cross-recipe). Scope undefined — needs concrete use case first.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR before implementation.

---

## ⏳ Deferred / Blocked

### Blocked by DIAG-RUNTIME-BASE-1 (Phase 1 base class — see ADR-079)

> Status: COMPLETED. DIAG-RUNTIME-BASE-1 done 2026-05-11. All Phase 2 tasks moved to **Do Now → Runtime Error Discipline**. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

### Blocked by library limitations

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — library limitation]`: Register `geom_map` component in VizFactory. Blocked: plotnine has no native GeoDataFrame/spatial support; requires geopandas integration and a spatial manifest format design. Unblocks: GALLERY-MAP.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred — library limitation]`: Map chart types in Gallery. Blocked by VIZ-GEOM-MAP-1.
- [ ] **GALLERY-FLOW** `[sonnet/medium]` `[deferred — library limitation]`: Flow / network chart types. Blocked: plotnine has no native network/Sankey/flow support. Requires feasibility study — candidate libs: `networkx` + custom geom, or external renderer.

### Blocked by other tasks

> VIZFAC-T3-OVERRIDE-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> VIZFAC-T3-EXPORT-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> VIZFAC-BLUEPRINT-FORM-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)

> PROP-2: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)
- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.

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
> ACTION-RENAME-1: COMPLETED 2026-05-11. Archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md)
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
| May-11 hygiene | Doc/ADR/lib-test audit fixes, Blueprint IDE features, ADR-079 design, cascade design, T3 threading, repo hygiene | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-11 session | BP-LINEAGE-NAV-1 (lineage rail race fix), GALLERY-CLONE-DECOUPLE-1 (T3 transplant decouple + ADR-071 gate), VIZFAC-RESOLVER-1 (cascade resolver + 75 tests), DIAG-RUNTIME-BASE-1 (PipelineError Phase 1) | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |

---

## Archive Pointers

- [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) — May-11: DOC-DRIFT/GAP batch, ADR-078-ACTIONS/TRANSFORMER-SUITE-FIX, DIAG-RUNTIME-ADR, Blueprint IDE (BP-DEBUG/ACTION-PARITY/FIELD-GAP/FWD-HINT), VIZ-DISCRETE/GALLERY-THUMB, lib-test/pkg fixes, TECH-T3-THREAD-1, PYPROJECT-DEPS-1; **session**: DIAG-RUNTIME-BASE-1, BP-LINEAGE-NAV-1, GALLERY-CLONE-DECOUPLE-1, VIZFAC-RESOLVER-1
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
