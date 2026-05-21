# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-21 (TASK-ARCHIVE-1 — archived Phase 18-F, 32, 33, audit-script-fixes + DOC-BLUEPRINT-1) by @dasharch

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

### Phase 18-F — Action Registry ui_schema Parity

> Status: COMPLETED. Detailed history moved to: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md)

### Phase 32 — Blueprint IDE Build Mode (ADR-075 / ADR-082)

> Status: COMPLETED. Detailed history moved to: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md)

### Phase 32 (cont.) — ADR-082 Spawned Tasks (BLUEPRINT Feature Set)

> Status: COMPLETED. Detailed history moved to: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md)

### Phase 33 — Blueprint AI Agent MVP-1 (ADR-076)

> Status: COMPLETED. Detailed history moved to: [tasks_archive_phase33.md](archives/tasks_archive_phase33.md)

### Audit script fixes

> Status: COMPLETED. Detailed history moved to: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md)

### Documentation & Hygiene Sprint (pre-build-continuation gate)

> **2026-05-21 decision.** Pause building. Document what has been built, run audits, clean task file.
> Moving `.claude/knowledge/` content into `docs/` is deferred to near-end-of-build.
> All docs go under `docs/` (user-facing + developer-facing). Each lib also gets its own `README.md`.
>
> **OPUS constraint:** Must verify all claims against actual code before writing. Do NOT invent or extrapolate.
> Check the file, then describe it. Every claim about a function signature, file path, or behaviour
> must be confirmed with a `Read` or `grep` before it appears in any doc.

- ~~**DOC-BLUEPRINT-1**~~ `[opus/high]` — **DONE 2026-05-21.** `docs/workflows/blueprint_architect.qmd` (9 sections). History: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md).

- [x] **DOC-BLUEPRINT-USER-1** `[sonnet/medium]`: Write `docs/user_guide/blueprint_manifest_authoring.qmd` — user-facing (non-developer) guide for manifest authoring in BLUEPRINT. Audience: bioscientist who wants to build or modify a pipeline manifest. Cover: the 3-step canonical YAML authoring flow (data_schema → join → plot); how to use the form UI vs YAML escape hatch; the branching decision guide (plain-English version of the branching rules); validation and what PASS/FAIL means; when to call for developer help. Keep concrete, use examples from existing manifests under `config/manifests/`.

- [x] **DOC-LIBREADME-BLUEPRINT-ARCH-1** `[sonnet/medium]`: Write/update `libs/blueprint_arch/README.md` — done 2026-05-21. Added: `generate_branch_plan` to manifest_navigator API; `search_components` to schema_registry API; new sections for `group_plot_manager.py`, `agent_tools.py`, `agent_tool_parser.py`, `join_designer.py`; updated tests table listing all 4 test files.

- [x] **DOC-LIBREADME-TRANSFORMER-1** `[sonnet/medium]`: Update `libs/transformer/README.md` — done 2026-05-21. Added: full action registry table (all 8 categories, 50+ actions); detection-based manifest loading explanation for `debug_assembler.py`. Existing sections (tiered wrangling, ui_schema, widget vocab, tests) were already current.

- [x] **DOC-LIBREADME-VIZFACTORY-1** `[sonnet/medium]`: Update `libs/viz_factory/README.md` — done 2026-05-21. Added: ADR-083 canonical plot spec section with factory_id removal note and migrate_plot_specs.py; five-tier cascade table with normalise_plot_spec/serialise_plot_spec/resolve_plot_config public API; palette injection table.

- [ ] **DOC-LIBREADME-OTHERS-1** `[haiku/low]`: Check READMEs exist and are not stale for `libs/ingestion/`, `libs/utils/`, `libs/connector/`, `libs/test_lab/`. If a README is absent, create a one-page stub with: purpose, public API summary, editable install, how to run tests. If present and recent, skip.

- [x] **TASK-ARCHIVE-1** `[haiku/low]`: Archive all completed `[x]` items from Phase 32 and Phase 33 sections — done 2026-05-21. Archives: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md), [tasks_archive_phase33.md](archives/tasks_archive_phase33.md).

- [x] **AUDIT-PASS-1** `[sonnet/low]`: Run the full audit suite + test suites. Done 2026-05-21. Results: all 10 scheduled audits PASS; 26/26 Playwright smoke tests pass (3 persona-skipped expected); dep graph regenerated (134 nodes, 259 edges). Task-drift FAIL: 3 items — DOC-BLUEPRINT-USER-1 (pending, expected), task_archive_phase33 (false positive — file exists), `scripts/build_dep_graph.py` (false positive — actual path is `assets/scripts/build_dep_graph.py`). No new actionable tasks.

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
| Phase 18-F, 32, 32-cont, audit-fixes | ACTION-UISCHEMA-1, BP-FORMS-1/ESCAPE/UNDO/HELP, ACTION-RENAME-1, all ADR-082 spawned BP-* tasks, MANIFEST-INCLUDE-1 | 2026-05-21 | [tasks_archive_phase32.md](archives/tasks_archive_phase32.md) |
| Phase 33 | BP-AGENT-PARSER-1/TOOLS/INSTRUCT/PANEL/UI/CSS — all ADR-076 MVP-1 agent tasks | 2026-05-21 | [tasks_archive_phase33.md](archives/tasks_archive_phase33.md) |

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

- [tasks_archive_phase33.md](archives/tasks_archive_phase33.md) — Phase 33: all ADR-076 MVP-1 Blueprint AI Agent tasks (BP-AGENT-*)
- [tasks_archive_phase32.md](archives/tasks_archive_phase32.md) — Phase 18-F, 32, 32-cont (ADR-082), audit script fixes: ACTION-UISCHEMA-1, all BP-* IDE/plot-model/branch/autosave tasks, MANIFEST-INCLUDE-1
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
