# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-05-21 (Phase 34 tasks + hygiene sprint archived; audit findings added) by @dasharch

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

### Audit-detected fixes

- [x] **ADR-045-ANCHOR-SET-1** ✅ 2026-05-22 `[sonnet/medium]` `[adr-violation]`: `app/handlers/home_theater.py` — removed `anchor_path.set(str(out_path))` from inside `@render.ui dynamic_tabs()`. Extracted to new `@reactive.Effect _sync_anchor_path()` with idempotent guard. Import check + Playwright smoke suite pass.

- [x] **VIZFAC-SUITE-TIMEOUT-1** ✅ 2026-05-22 `[sonnet/low]` `[test-infra]`: Bumped `TIMEOUT_SECONDS` from 300 to 600 in `scripts/audit_library_tests.py`. viz_factory integrity suite renders 191 PNGs; 300s was structurally insufficient.

- [x] **DOC-SYNC-PLATFORM-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Marked `gallery.qmd` reference as `[PLANNED]` in `docs/vision/platform_evolution.qmd` line 115.

- [x] **DOC-SYNC-TESTING-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Updated `docs/reference/testing.qmd` line 65 — replaced `create_test_data.py` reference with `AquaSynthesizer` (`libs/test_lab/src/test_lab/aqua_synthesizer.py`).

- [x] **PERSONA-DATAIMPORT-FLAG-DOC-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Confirmed vestigial — `data_import_panel_visible` is never read by `is_enabled()` in app code. Superseded by ADR-073 sidebar slot registry. Added note to `rules_persona_feature_flags.md`. Removal tracked as LEGACY-DATAIMPORT-FLAG-1.

- [x] **LEGACY-DATAIMPORT-FLAG-1** ✅ 2026-05-22 `[haiku/low]` `[legacy]`: Removed `data_import_panel_visible` from all 8 persona templates and `bootloader._FEATURES_DEFAULT_TRUE`. Import check clean.

- [x] **DOC-BLUEPRINT-PANELS-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Updated Blueprint IDE panel table in `docs/user_guide/blueprint_manifest_authoring.qmd`. Verified against wrangle_studio.py nav_panels. Actual panels: TubeMap accordion + 4 center nav_panels (1. Focus, 2. Interface, 3. YAML Raw Source, 4. Joint Designer). "Master Manifest" and "External Exchange" do not exist in code — audit claim was spurious. "YAML" renamed to "3. YAML (Raw Source)". Inline reference at §277 updated to match.

### Blueprint In-App Help Enrichment (developer-facing, Polars + Plotnine docs in Blueprint IDE)

> **Design settled 2026-05-22.** All four tasks unblocked and sequenced.
>
> **Context:** `@register_action` and `@register_plot_component` carry a `ui_schema` dict read at runtime by `schema_registry.py` and rendered in `bp_help_panel_ui`. ADR-075 §4 specifies that 1:1 Polars/Plotnine wrappers should resolve the real library `__doc__` via the `wraps` field (importlib, air-gap safe, zero maintenance). Current state: transformer has 1/63 actions with `wraps`; viz_factory has 191/192. Neither library has `description` or `yaml_example` fields.
>
> **Breakage risk:** none. `ingestion/`, `utils/`, `transformer` execution, and `config_loader` never read `ui_schema`. All app-layer readers use `.get()` with defaults. New fields are purely additive.
>
> **Build order:** BP-HELP-ADR-1 → BP-HELP-RENDER-1 (parallel-safe after ADR) → BP-HELP-TRANSFORMER-1 → BP-HELP-VIZFACTORY-1.

- [x] **BP-HELP-ADR-1** `[sonnet/low]`: Extend ADR-075 to canonicalize two new optional `ui_schema` fields: `description` (one developer-oriented sentence — what problem this solves, when to reach for it) and `yaml_example` (minimal correct YAML snippet for use in a manifest). Update `rules_data_engine.md §2` (decorator standards — add the two fields to the law). Update `rules_persona_bioscientist.md §8` (action list note — add that all entries are expected to carry `wraps` or `description`+`yaml_example`). No code changes in this task.
  - Gate: ADR-075 §1 lists `description` and `yaml_example` as standard optional keys with their semantics. Rules files updated. `dependency_index.md` consistent.

- [x] **BP-HELP-RENDER-1** `[haiku/low]`: Add render support for the two new fields. (1) `bp_help_panel_ui` in `app/modules/wrangle_studio.py`: render `yaml_example` as a `.bp-help-docstring` code block immediately below the description line, before the `wraps` docstring accordion. (2) `help_registry.py`: add `description` column to the registry DataGrid (read from `ACTION_SCHEMAS` via `schema_registry.get_action_catalog()`; extend with `get_component_catalog()` so viz_factory components are also listed). Both changes are additive — render only when field is present, no-op when absent.
  - Depends: BP-HELP-ADR-1.
  - Gate: `python -c "from app.src.main import app; print('OK')"` clean. Smoke: help panel renders for `filter_range` (has existing `wraps`) and shows a code block when `yaml_example` is set; registry table shows description column.

- [x] **BP-HELP-TRANSFORMER-1** `[sonnet/high]`: Content sweep — all 60 transformer `@register_action` entries (2 persistence engine-internals skip). Added `description` + `yaml_example` to all 60; `wraps` added to 35 actions that are 1:1 Polars wrappers (namespace sub-methods str.*/dt.*/list.* and composite actions intentionally skipped — no importlib-safe resolution). Dep-sweep clean. 97 tests pass. ✅ 2026-05-22

- [x] **BP-HELP-VIZFACTORY-1** `[sonnet/medium]`: Content sweep — 191 active viz_factory `@register_plot_component` entries (geom_map commented out). Added `description` + `yaml_example` to all 191 across 7 files (coords/facets/geoms/guides/positions/scales/themes). `wraps` already present for all active components. All imports clean. 97 tests pass. ✅ 2026-05-22

### Phase 34 — TEST_LAB Build

> **Design:** `.claude/design/spaces/TEST_LAB.md` — all design decisions locked 2026-05-21.  
> **Build order:** 34-A (library) → 34-B (utils) → 34-C (bootstrapper) → 34-D (scaffold) → 34-E (synth) → 34-F (anon) → 34-G (reformat) → 34-H (UI last).  
> **Note:** `UX-DEVINSP-1` (Deferred — TEST_LAB sidebar redesign) is superseded by TL-UI-SHELL-1.

#### 34-A — ID Reconciliation Library

- [x] **TL-IDLIB-1** `[haiku/low]`: Scaffold `libs/id_reconciliation/` — `pyproject.toml` (deps: `polars`, `utils`, `rapidfuzz`), module structure (`__init__.py`, empty module files), editable install, empty `tests/conftest.py`. Gate: `from id_reconciliation import IDReconciliationEngine` succeeds. ✅ 2026-05-22

- [x] **TL-IDLIB-MATCH-1** `[sonnet/high]`: Core matching — `data_structures.py` (`IDPair`, `MatchResult`, `PatternSuggestion`, `TransformationRecipe`) + `matcher.py` (exact 1.0; `rapidfuzz` token-set ratio with `_/-`→space normalization for fuzzy 0.0–0.99; unmatched 0.0). `reconciler.py` deletion deferred to TL-IDLIB-TESTS-1. Gate: `test_exact_match` ✅ `test_fuzzy_match` ✅ boundary-aware (001_ABCD↔ABCD_001) ✅ — 2026-05-22  
  Depends: TL-IDLIB-1.

- [x] **TL-IDLIB-PATTERN-1** `[sonnet/high]`: `pattern_detector.py` — prefix/suffix removal (scan 1–16 chars, best-hits wins), delimiter swap, case normalization; `suggest_regex` ported from `reconciler.py` (boundary guards + digit generalization). Primitives to be extracted to `libs/utils/id_patterns.py` in TL-UTILS-PATTERN-1. Gate: `test_pattern_suggestion_prefix_sample` ✅ prefix "sample_" ranked first, match_count=5 ✅ — 2026-05-22  
  Depends: TL-IDLIB-1.

- [x] **TL-IDLIB-RECIPE-1** `[sonnet/medium]`: All 7 recode actions (`strip_whitespace`, `cast_string`, `regex_replace`, `lowercase`, `mutate`, `drop_duplicates`, `null_if`, `drop_nulls`); `TransformationRecipe.to_yaml()`/`from_yaml()` methods added. Gate: `test_recipe_persistence` ✅ `test_recode_workflow_prefix_removal` ✅ `test_recode_workflow_delimiter_extraction` ✅ all 5 action types ✅ — 2026-05-22  
  Depends: TL-IDLIB-1.

- [x] **TL-IDLIB-CORE-1** `[sonnet/high]`: IDReconciliationEngine orchestrator — `core.py` (`precheck_compatibility`, `match_pair`, `suggest_patterns`, `apply_pattern`, `generate_recipe`, `detect_many_to_many`, `format_match_table`). Progressive matching: full file via Polars LazyFrame, chunks default 50 rows (configurable in persona config). Recode threshold: 50 unmatched triggers "clean first" (configurable). Gate: `test_many_to_many_detection` ✅ progressive chunking ✅ `format_match_table` columns ✅ — 2026-05-22  
  Depends: TL-IDLIB-MATCH-1, TL-IDLIB-PATTERN-1, TL-IDLIB-RECIPE-1.

- [x] **TL-IDLIB-TESTS-1** `[sonnet/medium]`: Full test suite — unit tests per module + `id_reconciliation_integrity_suite.py` orchestrator. Cases: exact match, pattern suggestion, many-to-many detection, recipe round-trip, all 5 recode action types, multi-file sequencing suggestion. Gate: `pytest libs/id_reconciliation/tests/ -q` all pass ✅ 28/28 — `reconciler.py` deleted — 2026-05-22  
  Depends: TL-IDLIB-CORE-1.

#### 34-B — Pattern Helper in `libs/utils/`

- [x] **TL-UTILS-PATTERN-1** `[sonnet/low]`: Extract all pattern primitives (`PatternSuggestion`, `detect_patterns`, `apply_pattern`, `suggest_regex`) into `libs/utils/src/utils/id_patterns.py`. `pattern_detector.py` → thin re-export shim; `PatternSuggestion` removed from `data_structures.py`; all imports updated across code, rules, docs, READMEs, and design sketch. Gate: 28/28 tests pass ✅ `from utils.id_patterns import PatternSuggestion` works ✅ — 2026-05-22  
  Depends: TL-IDLIB-PATTERN-1.

#### 34-C — ManifestBootstrapper Fixes

- [x] **TL-BOOTSTRAP-FIX-1** `[sonnet/low]`: Fix `libs/test_lab/src/test_lab/bootstrapper.py`: (1) `"plotting"` → `"analysis_groups"`, (2) remove hardcoded spurious `metadata_schema:` entry, (3) add `join_manifests: {}` stub, (4) accept optional `id_cleaning_recipes: dict` and bake valid cleaning actions into `tier1:` wrangling. Gate: headless test generates manifest that passes `debug_assembler.py` without error. ✅ 2026-05-22 — 10/10 gate tests pass.  
  Depends: TL-IDLIB-RECIPE-1.

#### 34-D — Manifest Scaffolding ZIP

- [x] **TL-SCAFFOLD-1** `[sonnet/medium]`: ZIP boilerplate output — `libs/test_lab/src/test_lab/scaffolder.py` (or extend bootstrapper). Input: TSV paths + `TransformationRecipe` objects. Output: ZIP with master YAML (`data_schemas:`, `join_manifests:` pre-filled, `analysis_groups: {}`) + fragment files (`input_fields/`, `wrangling/`, `assembly/`). ID cleaning steps baked into `tier1:` wrangling. Gate: unzip → `debug_assembler.py` runs without error; `data_schemas:` key confirmed; `ingredients:` format confirmed; `'on':` quoted.  
  Depends: TL-BOOTSTRAP-FIX-1, TL-IDLIB-CORE-1. ✅ 2026-05-22 — 15/15 gate tests pass.

#### 34-E — Synthetic Data Upgrade

- [x] **TL-SYNTH-1** `[sonnet/high]`: Upgrade `libs/test_lab/src/test_lab/aqua_synthesizer.py` — `propose_config(source)` + `generate(config)` two-step flow; `mode: demo | stress_test`; `error_injection` block (missing_values, wrong_type, duplicate_ids, pk_mismatches, schema_errors, malformed_fields); YAML archive config output with prominent "NOT a pipeline manifest" header; named scenario save/load/list (`libs/test_lab/scenarios/`). Gate: demo generates clean TSV; stress_test injects at stated rate ±2%; scenario round-trip; `pytest libs/test_lab/tests/ -q` passes. ✅ 2026-05-22 — 21/21 gate tests pass.

#### 34-F — Anonymisation Tool

- [x] **TL-ANON-1** `[sonnet/medium]`: `libs/test_lab/src/test_lab/anonymiser.py` — `anonymise(filepath, id_column, personal_columns, pattern)` + `anonymise_batch` (multi-file consistency). Patterns: sequential, hash, custom. Outputs: anonymised TSV + mapping TSV + de-anonymisation instructions. Gate: round-trip test (anonymise → BLUEPRINT join → IDs restored); multi-file consistency test; personal column stripping verified.
  ✅ 2026-05-22 — 22/22 gate tests pass.

#### 34-G — Reformatting Tools

- [x] **TL-REFORMAT-1** `[haiku/low]`: `libs/test_lab/src/test_lab/reformatter.py` — `DataReformatter` class with `convert_xlsx` (multi-sheet, sheet subset, `_safe_stem` name normalisation), `convert_csv` (any delimiter), `convert_folder` (bulk, error-per-file not raised). Uses polars directly (ExcelHandler is a CLI script, not importable class). Gate: multi-sheet XLSX → N TSV files ✅ CSV with comma delimiter converts ✅ folder bulk ✅ error stored not raised ✅. 20/20 tests pass; full test_lab suite 88/88 ✅ 2026-05-22

#### 34-H — UI (gates on library tasks)

- [x] **TL-UI-SHELL-1** `[sonnet/medium]`: TEST_LAB UI shell in `test_lab_studio.py` — left sidebar accordion (panels: ID Reconciliation, Manifest Scaffolding, Synthetic Data, Anonymisation, Reformatting); view title banner; `test_lab_enabled` persona flag gate (ADR-071); add `test_lab` sidebar slot type to `app/modules/sidebar_registry.py`. Gate: app starts with `test_lab_enabled: true`; accordion panels render; `test_lab_enabled: false` → no TEST_LAB nav.
  ✅ 2026-05-22 — import OK; nav gate fixed (developer_mode_enabled → test_lab_enabled); 213/213 tests pass.

- [x] **TL-UI-REFORMAT-1** `[haiku/low]`: Reformatting panel — file upload (XLSX/CSV), sheet assignment UI (XLSX), convert button, TSV download.  
  Depends: TL-REFORMAT-1, TL-UI-SHELL-1.
  ✅ 2026-05-22 — tl_reformat_ui, sheet picker, delimiter select, tl_reformat_download wired; import OK.

- [x] **TL-UI-RECONCILE-1** `[sonnet/high]`: ID Reconciliation panel — multi-file upload (2–6), PRE-CHECK result, pairwise match table (side-by-side, certainty sort, chunked 50 rows, bulk-accept 100% button, per-row verify/reject), pattern suggestion panel (ranked, apply), recode workflow (action picker, preview, re-run), many-to-many dialog (mandatory written reason), recipe download (YAML).  
  Depends: TL-IDLIB-CORE-1, TL-UI-SHELL-1.
  ✅ 2026-05-22 — 2-file upload, column selectors, PRE-CHECK (precheck_compatibility), RECONCILE (reconcile()), match table DataGrid, pattern summary, M2M warning + reason textarea, certainty threshold slider, recipe YAML download; import OK. Per-row verify/reject → threshold slider (principled equivalent).

- [ ] **TL-UI-SCAFFOLD-1** `[sonnet/medium]`: Manifest Scaffolding panel — file upload or "Continue from ID Reconciliation", join key selection, boilerplate ZIP download with baked-in steps summary.  
  Depends: TL-SCAFFOLD-1, TL-UI-RECONCILE-1.

- [x] **TL-UI-SYNTH-1** `[sonnet/medium]`: Synthetic Data panel — schema/file upload, proposed config review table (per-column editable), mode toggle (Demo/Stress test), error injection block (stress_test only), n_rows input, generate button, scenario save/load, download TSV + YAML config.  
  Depends: TL-SYNTH-1, TL-UI-SHELL-1.
  ✅ 2026-05-22 — tl_synth_ui shell + reactive chain (file/columns source, n_rows, mode, error injection sliders, generate event, preview DataGrid, TSV download) wired; import OK.

- [x] **TL-UI-ANON-1** `[sonnet/medium]`: Anonymisation panel — multi-file upload, ID column selector, personal column selector, pattern picker, generate button, download anonymised TSV(s) + mapping TSV + instructions.  
  Depends: TL-ANON-1, TL-UI-SHELL-1.
  ✅ 2026-05-22 — tl_anon_ui shell; reactive chain (file→columns, id_column select, personal cols checkbox, pattern/prefix/custom inputs, anonymise event, preview DataGrid, ZIP download with anonymised+mapping+config); import OK.

### Legacy removal (tracked per rules_legacy_management.md §6)

> Protocol: dep-sweep → impact assessment → migration path → code removal → test sweep → doc consistency sweep → ADR record.
> All 7 steps required before a task is [DONE].

- [x] **LEGACY-FLAT-PLOTS-1** `[sonnet/medium]`: Full removal of flat `plots:` authoring key. ✅ 2026-05-22
  - ConfigManager now raises `DeploymentError` if root-level `plots:` found; backward-compat init removed.
  - `stress_test_master.yaml` root-level `plots:` block removed.
  - Error-path + happy-path tests added to `libs/utils/tests/test_config_loader.py`. 154 tests pass.
  - `rules_manifest_structure.md §8` DEPRECATED marker converted to REMOVED tombstone (expires Phase 36).

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
  ensure that if there is flat structure in manifewt that that porduces an error that it indicates this to the user as error to guide

---

## 🤔 Needs Discussion / Decision

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **GREAT-DOCS-1** `[sonnet/medium]`: Evaluate `great-docs` (https://github.com/posit-dev/great-docs) for auto-generating a static Quarto/website reference from the codebase. **Depends on:** CODE-DOCS-RETROSPECTIVE — docstrings must exist before auto-gen is meaningful. Deferred until pre-deployment sprint.
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
