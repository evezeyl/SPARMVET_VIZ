# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-21 (Phase 34 TEST_LAB tasks added; UX-DEVINSP-1 superseded) by @dasharch

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

- [x] **DOC-LIBREADME-OTHERS-1** `[haiku/low]`: Check READMEs for `libs/ingestion/`, `libs/utils/`, `libs/connector/`, `libs/test_lab/` — done 2026-05-21. All four exist with purpose, key components, install, and tests sections. No stubs needed; all current.

- [x] **TASK-ARCHIVE-1** `[haiku/low]`: Archive all completed `[x]` items from Phase 32 and Phase 33 sections — done 2026-05-21. Archives: [tasks_archive_phase32.md](archives/tasks_archive_phase32.md), [tasks_archive_phase33.md](archives/tasks_archive_phase33.md).

- [x] **AUDIT-PASS-1** `[sonnet/low]`: Run the full audit suite + test suites. Done 2026-05-21. Results: all 10 scheduled audits PASS; 26/26 Playwright smoke tests pass (3 persona-skipped expected); dep graph regenerated (134 nodes, 259 edges). Task-drift FAIL: 3 items — DOC-BLUEPRINT-USER-1 (pending, expected), task_archive_phase33 (false positive — file exists), `scripts/build_dep_graph.py` (false positive — actual path is `assets/scripts/build_dep_graph.py`). No new actionable tasks.

### Phase 34 — TEST_LAB Build

> **Design:** `.claude/design/spaces/TEST_LAB.md` — all design decisions locked 2026-05-21.  
> **Build order:** 34-A (library) → 34-B (utils) → 34-C (bootstrapper) → 34-D (scaffold) → 34-E (synth) → 34-F (anon) → 34-G (reformat) → 34-H (UI last).  
> **Note:** `UX-DEVINSP-1` (Deferred — TEST_LAB sidebar redesign) is superseded by TL-UI-SHELL-1.

#### 34-A — ID Reconciliation Library

- [ ] **TL-IDLIB-1** `[haiku/low]`: Scaffold `libs/id_reconciliation/` — `pyproject.toml` (deps: `polars`, `utils`), module structure (`__init__.py`, empty module files), editable install, empty `tests/conftest.py`. Gate: `from id_reconciliation import IDReconciliationEngine` succeeds.

- [ ] **TL-IDLIB-MATCH-1** `[sonnet/high]`: Core matching — `data_structures.py` (`IDPair`, `MatchResult`, `PatternSuggestion`, `TransformationRecipe`) + `matcher.py` (exact 1.0; fuzzy scored; unmatched 0.0). Port logic from `libs/test_lab/src/test_lab/reconciler.py` — do not duplicate. Gate: `test_exact_match` + `test_pattern_match` pass.  
  Depends: TL-IDLIB-1.

- [ ] **TL-IDLIB-PATTERN-1** `[sonnet/high]`: Pattern detector — `pattern_detector.py` (prefix/suffix removal, delimiter extraction, case normalisation, substring extraction, regex; ranked by `expected_matches DESC, expected_certainty DESC, simplicity ASC`). Builds on `suggest_regex` in `reconciler.py`. Gate: `test_pattern_suggestion` passes — prefix `"sample_"` detected and ranked first.  
  Depends: TL-IDLIB-1.

- [ ] **TL-IDLIB-RECIPE-1** `[sonnet/medium]`: Recode workflow + recipe persistence — `recipe.py` (`apply_recode_step` for: `regex_replace`, `mutate` via Polars expression, `drop_duplicates`, `null_if`, `drop_nulls`; `TransformationRecipe.to_yaml` / `from_yaml`). Gate: `test_recipe_persistence` (save+load round-trip) + `test_recode_workflow` (prefix removal + delimiter extraction) pass.  
  Depends: TL-IDLIB-1.

- [ ] **TL-IDLIB-CORE-1** `[sonnet/high]`: IDReconciliationEngine orchestrator — `core.py` (`precheck_compatibility`, `match_pair`, `suggest_patterns`, `apply_pattern`, `generate_recipe`, `detect_many_to_many`, `format_match_table`). Progressive matching: full file via Polars LazyFrame, chunks default 50 rows (configurable in persona config). Recode threshold: 50 unmatched triggers "clean first" (configurable). Gate: `test_many_to_many_detection` + progressive chunking test + `format_match_table` returns parseable string.  
  Depends: TL-IDLIB-MATCH-1, TL-IDLIB-PATTERN-1, TL-IDLIB-RECIPE-1.

- [ ] **TL-IDLIB-TESTS-1** `[sonnet/medium]`: Full test suite — unit tests per module + `id_reconciliation_integrity_suite.py` orchestrator. Cases: exact match, pattern suggestion, many-to-many detection, recipe round-trip, all 5 recode action types, multi-file sequencing suggestion. Gate: `pytest libs/id_reconciliation/tests/ -q` all pass.  
  Depends: TL-IDLIB-CORE-1.

#### 34-B — Pattern Helper in `libs/utils/`

- [ ] **TL-UTILS-PATTERN-1** `[sonnet/low]`: Extract ID pattern matching primitives (prefix/suffix detection, delimiter extraction, regex generalisation) into `libs/utils/src/utils/id_patterns.py`. Update `libs/id_reconciliation/` to import from there. Update `libs/blueprint_arch/join_designer.py` to also use this helper. Gate: both libs import cleanly; no pattern logic duplicated between them.  
  Depends: TL-IDLIB-PATTERN-1.

#### 34-C — ManifestBootstrapper Fixes

- [ ] **TL-BOOTSTRAP-FIX-1** `[sonnet/low]`: Fix `libs/test_lab/src/test_lab/bootstrapper.py`: (1) `"plotting"` → `"analysis_groups"`, (2) remove hardcoded spurious `metadata_schema:` entry, (3) add `join_manifests: {}` stub, (4) accept optional `id_cleaning_recipes: dict` and bake valid cleaning actions into `tier1:` wrangling. Gate: headless test generates manifest that passes `debug_assembler.py` without error.  
  Depends: TL-IDLIB-RECIPE-1.

#### 34-D — Manifest Scaffolding ZIP

- [ ] **TL-SCAFFOLD-1** `[sonnet/medium]`: ZIP boilerplate output — `libs/test_lab/src/test_lab/scaffolder.py` (or extend bootstrapper). Input: TSV paths + `TransformationRecipe` objects. Output: ZIP with master YAML (`data_schemas:`, `join_manifests:` pre-filled, `analysis_groups: {}`) + fragment files (`input_fields/`, `wrangling/`, `assembly/`). ID cleaning steps baked into `tier1:` wrangling. Gate: unzip → `debug_assembler.py` runs without error; `data_schemas:` key confirmed; `ingredients:` format confirmed; `'on':` quoted.  
  Depends: TL-BOOTSTRAP-FIX-1, TL-IDLIB-CORE-1.

#### 34-E — Synthetic Data Upgrade

- [ ] **TL-SYNTH-1** `[sonnet/high]`: Upgrade `libs/test_lab/src/test_lab/aqua_synthesizer.py` — `propose_config(source)` + `generate(config)` two-step flow; `mode: demo | stress_test`; `error_injection` block (missing_values, wrong_type, duplicate_ids, pk_mismatches, schema_errors, malformed_fields); YAML archive config output with prominent "NOT a pipeline manifest" header; named scenario save/load/list (`libs/test_lab/scenarios/`). Gate: demo generates clean TSV; stress_test injects at stated rate ±2%; scenario round-trip; `pytest libs/test_lab/tests/ -q` passes.

#### 34-F — Anonymisation Tool

- [ ] **TL-ANON-1** `[sonnet/medium]`: `libs/test_lab/src/test_lab/anonymiser.py` — `anonymise(filepath, id_column, personal_columns, pattern)` + `anonymise_batch` (multi-file consistency). Patterns: sequential, hash, custom. Outputs: anonymised TSV + mapping TSV + de-anonymisation instructions. Gate: round-trip test (anonymise → BLUEPRINT join → IDs restored); multi-file consistency test; personal column stripping verified.

#### 34-G — Reformatting Tools

- [ ] **TL-REFORMAT-1** `[haiku/low]`: `libs/test_lab/src/test_lab/reformatter.py` — wire `ExcelHandler` (already in `libs/ingestion/`) for XLSX → TSV (multi-sheet); add CSV → TSV (any delimiter); bulk folder processing. Gate: multi-sheet XLSX → N TSV files; CSV with comma delimiter converts correctly.

#### 34-H — UI (gates on library tasks)

- [ ] **TL-UI-SHELL-1** `[sonnet/medium]`: TEST_LAB UI shell in `test_lab_studio.py` — left sidebar accordion (panels: ID Reconciliation, Manifest Scaffolding, Synthetic Data, Anonymisation, Reformatting); view title banner; `test_lab_enabled` persona flag gate (ADR-071); add `test_lab` sidebar slot type to `app/modules/sidebar_registry.py`. Gate: app starts with `test_lab_enabled: true`; accordion panels render; `test_lab_enabled: false` → no TEST_LAB nav.

- [ ] **TL-UI-REFORMAT-1** `[haiku/low]`: Reformatting panel — file upload (XLSX/CSV), sheet assignment UI (XLSX), convert button, TSV download.  
  Depends: TL-REFORMAT-1, TL-UI-SHELL-1.

- [ ] **TL-UI-RECONCILE-1** `[sonnet/high]`: ID Reconciliation panel — multi-file upload (2–6), PRE-CHECK result, pairwise match table (side-by-side, certainty sort, chunked 50 rows, bulk-accept 100% button, per-row verify/reject), pattern suggestion panel (ranked, apply), recode workflow (action picker, preview, re-run), many-to-many dialog (mandatory written reason), recipe download (YAML).  
  Depends: TL-IDLIB-CORE-1, TL-UI-SHELL-1.

- [ ] **TL-UI-SCAFFOLD-1** `[sonnet/medium]`: Manifest Scaffolding panel — file upload or "Continue from ID Reconciliation", join key selection, boilerplate ZIP download with baked-in steps summary.  
  Depends: TL-SCAFFOLD-1, TL-UI-RECONCILE-1.

- [ ] **TL-UI-SYNTH-1** `[sonnet/medium]`: Synthetic Data panel — schema/file upload, proposed config review table (per-column editable), mode toggle (Demo/Stress test), error injection block (stress_test only), n_rows input, generate button, scenario save/load, download TSV + YAML config.  
  Depends: TL-SYNTH-1, TL-UI-SHELL-1.

- [ ] **TL-UI-ANON-1** `[sonnet/medium]`: Anonymisation panel — multi-file upload, ID column selector, personal column selector, pattern picker, generate button, download anonymised TSV(s) + mapping TSV + instructions.  
  Depends: TL-ANON-1, TL-UI-SHELL-1.

---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **GREAT-DOCS-1** `[sonnet/medium]`: Evaluate `great-docs` (https://github.com/posit-dev/great-docs) for auto-generating developer and UI documentation from the existing codebase. Needs discussion: which audiences/surfaces benefit most, how it fits the Quarto DRY workflow, and how it complements CODE-DOCS-RETROSPECTIVE docstrings. **Depends on:** CODE-DOCS-RETROSPECTIVE (docstrings must exist before auto-gen is meaningful). Start with a proof-of-concept on one library before scoping full adoption.


- [ ] **LAB-WORKFLOW-1** `[opus/high]`: Collect all developer workflow info from Test Lab, Blueprint, and Gallery into a coherent end-to-end developer workflow. Needs dedicated design session before implementation. **Note (2026-05-21):** TEST_LAB design (`.claude/design/spaces/TEST_LAB.md`) is almost finished — schedule this after Phase 34 is complete.
- [ ] **UX-APPLY-IMPROVE-1** `[sonnet/medium]`: Audit Apply improvement — "apply to all except…" selection-by-exclusion mode. Needs design pass before scoping.
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: In-app search for plot types, plot properties, and recipe components — cross-manifest, cross-recipe. Use case: scientist wants to find plots by what they show (e.g. "distribution", "trend"), by required data pattern, or by aesthetic mapping. Design questions: fuzzy search on plot definitions and taxonomy fields? Keyword index built from manifests at load time? How efficient can this be? Needs a concrete spike / prototype before scoping. Links to Gallery taxonomy (ADR-063) and recipe meta taxonomy fields.
- [ ] **PROP-3** `[opus/high]`: Propagation TubeMap — graph viz of audit blast radius. Needs own design pass + ADR before implementation.
  > **What "propagation" means here:** when a T3 audit node (filter, exclusion) is applied across multiple plots via the propagation dialog (scope: this plot / all plots / all except...), the Propagation TubeMap would be a graph showing which plots are affected — blast-radius visualization of that audit decision. This is **distinct from the Blueprint TubeMap** (pipeline DAG from manifest structure). The T3 propagation dialog itself is designed in `ui_implementation_contract.md §12g` but not yet implemented. PROP-3 is a further visualization layer on top of that, also not yet implemented.

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
- ~~**UX-DEVINSP-1**~~ — superseded by TL-UI-SHELL-1 (Phase 34-H). Design locked 2026-05-21 in `.claude/design/spaces/TEST_LAB.md`.

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

- [ ] **ADR-045-ANCHOR-SET-1** `[sonnet/medium]` `[adr-violation]`: `app/handlers/home_theater.py` — `anchor_path.set(str(out_path))` is called inside `@render.ui dynamic_tabs()`, violating ADR-045 Rule R1 (renders must be read-only). Extract to a dedicated `@reactive.Effect` with idempotent guard: `if anchor_path.get() != str(out_path): anchor_path.set(str(out_path))`. Audit report: `.claude/logs/audits/audit_adr_compliance_2026-05-21.md`.

- [ ] **DOC-BLUEPRINT-PANELS-1** `[haiku/low]` `[doc-sync]`: `docs/user_guide/blueprint_manifest_authoring.qmd` — Blueprint IDE panel table is missing "Master Manifest" and "External Exchange" panels; "YAML" should be "YAML Escape Hatch". Verify against `app/handlers/blueprint_handlers.py` blueprint panel construction code before fixing. Audit report: `.claude/logs/audits/audit_doc_sync_2026-05-21.md`.

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
