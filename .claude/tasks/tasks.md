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

- [ ] **BP-FORMS-UNIFY-1** `[opus/high]`: Add-node MUST use the same `ui_schema` rich form as edit-node. Retire the primitive Focus-tab add UI (single column + one free-text param). New node created with default params, opened immediately in full form. Gap #1, ADR-082 §5.
- [ ] **BP-ENUM-PREVIEW-1** `[sonnet/medium]`: Implement `preview: true` in the enum widget renderer — visual sample for linetype/position/shape enums (currently ignored; renders plain dropdown). Gap #3, ADR-075 §2.
- [ ] **BP-EXPR-EDITOR-1** `[sonnet/high]`: `expression` widget → schema-aware code editor with column autocomplete (currently plain textarea). Scope: `mutate.expression` (only expression-widget field). Vendor any JS locally (ADR-071, no CDN). Gap #4, ADR-075 §2.
- [ ] **BP-COMPONENT-SCHEMA-1** `[sonnet/high]`: Component `ui_schema` parity pass — add schemas to remaining plot components (7/191 schemed today). Analogous to ACTION-UISCHEMA-1. Prereq for BP-COMPONENT-FORMS-1. Gap #2.
- [ ] **BP-COMPONENT-FORMS-1** `[opus/high]`: Component form path — configure plot/geom nodes via the shared 8-widget renderer driven by `COMPONENT_SCHEMAS`. Logic stack must handle plot nodes. Depends on BP-COMPONENT-SCHEMA-1. Gap #2, ADR-082 §5.
- [ ] **BP-JOINT-1** `[opus/high]`: Dedicated Joint Designer pane — left + right ingredient schemas side-by-side, live key-match preview, emits canonical `join` recipe step. Q5, ADR-082.
- [ ] **BP-GROUPS-1** `[sonnet/high]`: Group/plot sidebar inventory — persistent list with create/delete/assign affordances (MVP). v2: TubeMap context menu (Q6-C). Q6, ADR-082.
- [ ] **BP-META-1** `[sonnet/medium]`: Form UI for manifest `info:` block (description/author/version/tags) — YAML-only today. Functionality #7, ADR-082.
- [ ] **BP-NEW-1** `[sonnet/medium]`: "Create new manifest from scratch" flow — currently only import exists. Functionality #2, ADR-082.
- [ ] **BP-VALIDATE-1** `[sonnet/medium]`: Inline manifest validation surfacing in BLUEPRINT (validator exists; not wired to UI). Functionality #16, ADR-082.
- [ ] **BP-CSS-LEGEND-1** `[haiku/low]`: TubeMap legend uses forbidden Bootstrap colours (`#0d6efd`, `#198754`) — correct against `rules_css_style_spec.md §1c`. ADR-082 Consequences.
- [ ] **BP-SMOKE-1** `[sonnet/medium]`: Functional smoke pass for BP-ESCAPE-1 + BP-HELP-1 in the running app (qa persona) — confirm escape-hatch save round-trips and help panel resolves `__doc__`.
- [ ] **BP-AUTOSAVE-1** `[sonnet/high]`: Persist the in-progress BLUEPRINT manifest draft + undo history to disk; restore on reload/crash. Modeled on HOME ghost-save (ui_implementation_contract.md §12d) but persists manifest-draft state, not data-tier state. Decided 2026-05-20 (ADR-082 §2a).
- [ ] **BP-BRANCH-NODE-1** `[opus/high]` (was BP-FORK-FILES-1): Implement node-level **lineage bifurcation** (ADR-082 Q3, LOCKED). User picks a bifurcation node → BLUEPRINT creates a new divergent downstream fragment (`wrangling/`/`output_fields/`/`assembly/`/`plots/`) that **references shared upstream** (no recompute — upstream Tier 1 anchor stays materialized once) and wires it into the master via `!include`. Canonical pattern: `Summary` / `Summary_quality`. Replaces the current Visual Fork append-into-manifest behaviour. Open UX detail (decide at task time): auto-detect bifurcation point vs. explicit user choice. Whole-manifest duplication is a separate rare path (BP-DUPLICATE-1, deferred — only for genuinely new data).

### Phase 33 — Blueprint AI Agent MVP-1 (ADR-076)

- [ ] **BP-AGENT-PARSER-1** `[sonnet/medium]`: Fenced-block extractor (`agent_tool_parser.py`) — parse structured tool-call blocks from agent text output. Spec: ADR-076, implementation plan §Phase 33, step 33-C.
- [ ] **BP-AGENT-TOOLS-1** `[sonnet/medium]`: 3 MVP tools for the agent — `get_available_actions`, `get_available_components`, `get_field_contract`. Spec: ADR-076, step 33-D.
- [ ] **BP-AGENT-INSTRUCT-1** `[sonnet/medium]`: System prompt file `config/ui/agents/blueprint_default.md`. Spec: ADR-076, step 33-E.
- [ ] **BP-AGENT-PANEL-1** `[haiku/low]`: Register `blueprint_agent_chat` panel in sidebar registry + persona templates. Spec: ADR-076, step 33-F.
- [ ] **BP-AGENT-UI-1** `[sonnet/medium]`: Chat panel render outputs in `app/handlers/blueprint_handlers.py`. Spec: ADR-076, step 33-G.
- [ ] **BP-AGENT-CSS-1** `[haiku/low]`: `.bp-agent-*` CSS rule block in `config/ui/theme.css`. Spec: ADR-076 + `rules_css_style_spec.md §5` (Chat/Conversational Panel Pattern).

### Audit script fixes

- [ ] **MANIFEST-INCLUDE-1** `[sonnet/low]`: Any script that loads a **full pipeline manifest** (manifests with `analysis_groups`, modularised via `!include` in Phase 28) must use `ConfigManager` from `libs/utils/src/utils/config_loader.py`, not bare `yaml.safe_load()`. Standalone decorator/wrangling manifests (small fragments, no `!include`) are exempt. Confirmed broken: `libs/transformer/tests/debug_assembler.py:48` — causes `scripts/audit_manifest_integrity.py` to falsely report all 6 pipeline manifests as FAIL. Also check: `libs/viz_factory/tests/debug_runner.py:48` (fallback comment only, not fixed), `libs/viz_gallery/src/viz_gallery/gallery_manager.py:125` (gallery recipes are standalone — verify if any use `!include`), `libs/viz_gallery/assets/generate_previews.py:47`, `libs/viz_gallery/tests/debug_gallery_submission.py:50`. After fix, re-run `audit_manifest_integrity.py` → expect 6/6 PASS.

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
