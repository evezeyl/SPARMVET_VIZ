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
| **🟡 Bio-Scientist Enhancements** | `[ENHANCEMENT REQUEST]` items from manifest design sessions only (see `rules_persona_bioscientist.md §4-A`). |
| **👤 User Required** | Needs user action, decision, or explicit discussion. No agent progress until user responds. |

**Rules for keeping the file clean:**
- **Empty sections stay empty.** If Do Now has no items, leave it blank — no placeholder text, no status lines.
- **`> Completed:` / `> Status: COMPLETED` inline pointers inside sections are FORBIDDEN.** When items are done, move them to the archive file and update the archive table + pointers at the bottom.
- **Context and session notes go at the bottom** — in the `## 📋 Session Notes` section, not inside active task sections.

---

## 🟢 Do Now

Items with no blockers — can be started immediately.

### LAB-WORKFLOW follow-up

- [ ] **LAB-WORKFLOW-QMD-1** `[sonnet/low]` `[doc-sync]`: User-facing Quarto mirror of `developer_workflow.md` in `docs/workflows/` — explains the *logic* of the producer workflow for end users (DRY: link, do not duplicate per `rules_documentation_aesthetics.md §4`). Focus on workflow logic + module independence, not app mechanics. Can be written now (logic is settled).

### Maps — Solution A (choropleth via geom_polygon, no new deps)

> Design context: `.claude/design/maps_advanced_geo.md` (Solution B is the deferred geopandas path; A is this).
> Key fact (verified 2026-05-22): `geom_polygon`, `coord_equal`, `coord_fixed` are **already registered** in VizFactory. Solution A needs **no new viz component and no new dependency** — geometry is plain x/y/group numeric columns flowing through the existing tabular pipeline. ggplot2 analogue: `geom_polygon(aes(long, lat, group)) + map_data()`.

- [ ] **MAP-A-BOUNDARY-ASSET-1** `[sonnet/medium]`: Boundary-fortification asset script `assets/scripts/fortify_boundaries.py`. Pure-Python (json module only — **no geopandas/shapely**) GeoJSON → long-format Parquet with columns `region_id, region_name, poly_group, vertex_order, long, lat` (one row per polygon vertex; `poly_group` disambiguates multi-part regions and holes). `argparse` CLI per `rules_asset_scripts.md §2` (input GeoJSON path, output Parquet path, region-name property key — no hardcoded paths). Output to `assets/geo_boundaries/`.
  - Sub-step: source first boundary sets (Norway counties + Europe countries) from a public-domain provider (Natural Earth — public domain; **avoid GADM**, non-redistributable). Record provenance + licence in `assets/geo_boundaries/PROVENANCE.md`.
  - Verify: fortified Parquet round-trips to a plottable frame; vertex counts plausible; multi-part regions keep distinct `poly_group`.
- [ ] **MAP-A-MANIFEST-PATTERN-1** `[sonnet/medium]`: Author one end-to-end choropleth manifest as the canonical pattern. Tier 1 join: analytical data (rate/count per region) → boundary Parquet on region key. Plot spec: `geom_polygon` with `mapping: {x: long, y: lat, group: poly_group, fill: <metric>}` + `coord_equal` + a continuous fill scale. Verify via `debug_assembler.py` then `debug_gallery.py`; route evidence to `tmp/<date>/<lineage_id>/` per `rules_persona_bioscientist.md §7`. Halt for `@verify`.
  - Watch: `group` must be the vertex `poly_group` (not region) or polygons cross-link; fill is per-region so the join must broadcast the metric to every vertex row.
- [ ] **MAP-A-GALLERY-1** `[sonnet/medium]`: Gallery bundle for the choropleth (Scientific Triplet + preview PNG per `rules_gallery_standards.md`). **Blocked on a taxonomy decision** (shared with Solution B open-question #3): choropleth `family` — extend `TAXONOMY_CHEATSHEET.md` with a spatial value, or fold into `Comparison`/`Distribution`? Resolve with Eve before authoring the `info:` block.
- [ ] **MAP-A-DOCS-1** `[haiku/low]` `[doc-sync]`: Document the choropleth pattern — `libs/viz_factory/README.md` (geom_polygon-as-map recipe) + `docs/appendix/manifest_structure.yaml` (boundary-join + geom_polygon spec). DRY: link the design doc, do not duplicate.

> **Do NOT** uncomment `geom_map` at `geoms/core.py:822` for Solution A — that geom belongs to Solution B (needs the geo extra + a render branch; see design doc §11). Registering it now would expose a geom that errors on use.


---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Gallery keyword enrichment + AND/OR search. **Design settled (2026-05-22):** add `keywords: [list]` to `info:` block in each `recipe_manifest.yaml` (35 recipes); update `refresh_gallery.py` to include keywords in `gallery_index.json` pivot entries; add a text search input to the Gallery UI (split on spaces → AND-intersect tokens across keywords + existing taxonomy fields). Three keyword layers: (1) statistical/methodological synonyms (`median`, `quartile`, `IQR`, `spread`, `beeswarm`, `ridge`, `dumbbell`, `before after`, `cumulative`, `paired`, `stacked`, `proportional`, `small multiples`, `faceted`, `overlay`, `individual points`, `raw data`, `regression`, `fit`, `confidence interval`…); (2) data/use-case terms (`time series`, `temporal`, `longitudinal`, `rate`, `prevalence`, `incidence`, `frequency`, `quality control`, `normality`, `heterogeneity`, `exploration`…); (3) domain terms (`AMR`, `antimicrobial`, `resistance`, `MIC`, `susceptibility`, `surveillance`, `epidemiology`, `pathogen`, `species comparison`…). No fuzzy matching needed — AND/OR on exact tokens is sufficient for this gallery size. Step 1: enrich all 35 recipe `info:` blocks. Step 2: one-line `refresh_gallery.py` change. Step 3: gallery UI search widget.

---

## ⏳ Deferred / Blocked

### Deferred by architecture choice (NOT hard library blocks — premises corrected 2026-05-22)

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — architecture choice, NOT a library block]`: Register `geom_map` (Solution B — real geo). Premise corrected 2026-05-22: plotnine 0.15.4 **does** ship `geom_map` (`REQUIRED_AES={'geometry'}`); not blocked by the library. Deferred because it needs geopandas/shapely + a geometry-aware data path. Full design: `.claude/design/maps_advanced_geo.md` (recommended sub-option B1 = sidecar GeoDataFrame merged at render time). Choropleths ship sooner via Solution A (`MAP-A-*`, Do Now) with zero new deps. Do not uncomment `geoms/core.py:822` until this is scheduled.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred]`: Map chart types in Gallery. Solution A choropleths arrive via `MAP-A-GALLERY-1`; advanced (projected/CRS) maps wait on VIZ-GEOM-MAP-1 / Solution B.
- [ ] **GALLERY-FLOW** `[opus/high]` `[deferred — needs layout-precompute helper, NOT a hard library block]`: Flow / network chart types. Premise corrected 2026-05-22: same pattern as maps — plotnine has no high-level `geom_sankey`/`geom_net`, but the **primitives exist and are registered** (`geom_segment`, `geom_path`, `geom_polygon`, `geom_rect`, `geom_ribbon`). Feasible by precomputing layout/flow coordinates into a tabular form, then drawing with existing geoms. Needs: (1) a layout/coordinate-precompute helper (network: node x/y + edge endpoints; Sankey: stage rects + ribbon polygon vertices via pure-Python sigmoid interpolation), (2) a decision on whether to add `networkx` (NOT installed) for graph layout or hand-roll with `scipy` (installed). Note: `geom_curve` is **absent** in plotnine 0.15.4 (use `geom_segment`/`geom_path`); `matplotlib.sankey.Sankey` exists but draws its own figure and breaks the grammar-of-graphics model (escape-hatch only, not preferred). Needs own design pass + ADR before scheduling.

### Blocked by other tasks

- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.

### Planned / Large-scale backlog

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle profile YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).
- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — manifest hashes + data hashes in DB; LIMS link in audit report; configurable output path per persona.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.

### Explicitly deferred (scheduled)

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
| Documentation & Hygiene Sprint | DOC-BLUEPRINT-1/USER-1, DOC-LIBREADME-*, TASK-ARCHIVE-1, AUDIT-PASS-1, BP-ADR-FULL-1 | 2026-05-21 | [tasks_archive_hygiene_2026-05-21.md](archives/tasks_archive_hygiene_2026-05-21.md) |
| Phase 34 + May-22 hygiene | TEST_LAB Build (all TL-*), BP-HELP-*, audit fixes, legacy removal (FLAT-PLOTS/AUDIT-FLAG/TYPE-ALIASES/FLAT-WRANGLING), LAB-WORKFLOW-1, UX-APPLY-IMPROVE-1 | 2026-05-22 | [tasks_archive_2026-05-22.md](archives/tasks_archive_2026-05-22.md) |

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

- [tasks_archive_2026-05-22.md](archives/tasks_archive_2026-05-22.md) — Phase 34 (TEST_LAB Build) + BP-HELP sweep + audit fixes + legacy removal + LAB-WORKFLOW-1 + UX-APPLY-IMPROVE-1; also records DROPPED decisions (LAB-SEND-TO-1, LAB-OPEN-BLUEPRINT-1, UX-DEVINSP-1)
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
