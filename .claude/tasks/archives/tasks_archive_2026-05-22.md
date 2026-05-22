# Task Archive — 2026-05-22

**Archived from:** `tasks.md`
**Date:** 2026-05-22
**Contents:** Phase 34 (TEST_LAB Build) · Blueprint In-App Help Enrichment · audit-detected fixes · legacy removal · LAB-WORKFLOW-1 design · UX-APPLY-IMPROVE-1 · Decisions NOT implemented (LAB-SEND-TO-1, LAB-OPEN-BLUEPRINT-1, UX-DEVINSP-1).

---

## Completed Tasks

### Audit-Detected Fixes

- [x] **ADR-045-ANCHOR-SET-1** ✅ 2026-05-22 `[sonnet/medium]` `[adr-violation]`: `app/handlers/home_theater.py` — removed `anchor_path.set(str(out_path))` from inside `@render.ui dynamic_tabs()`. Extracted to new `@reactive.Effect _sync_anchor_path()` with idempotent guard. Import check + Playwright smoke suite pass.

- [x] **VIZFAC-SUITE-TIMEOUT-1** ✅ 2026-05-22 `[sonnet/low]` `[test-infra]`: Bumped `TIMEOUT_SECONDS` from 300 to 600 in `scripts/audit_library_tests.py`. viz_factory integrity suite renders 191 PNGs; 300s was structurally insufficient.

- [x] **DOC-SYNC-PLATFORM-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Marked `gallery.qmd` reference as `[PLANNED]` in `docs/vision/platform_evolution.qmd` line 115.

- [x] **DOC-SYNC-TESTING-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Updated `docs/reference/testing.qmd` line 65 — replaced `create_test_data.py` reference with `AquaSynthesizer` (`libs/test_lab/src/test_lab/aqua_synthesizer.py`).

- [x] **PERSONA-DATAIMPORT-FLAG-DOC-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Confirmed vestigial — `data_import_panel_visible` is never read by `is_enabled()` in app code. Superseded by ADR-073 sidebar slot registry. Added note to `rules_persona_feature_flags.md`. Removal tracked as LEGACY-DATAIMPORT-FLAG-1.

- [x] **LEGACY-DATAIMPORT-FLAG-1** ✅ 2026-05-22 `[haiku/low]` `[legacy]`: Removed `data_import_panel_visible` from all 8 persona templates and `bootloader._FEATURES_DEFAULT_TRUE`. Import check clean.

- [x] **DOC-BLUEPRINT-PANELS-1** ✅ 2026-05-22 `[haiku/low]` `[doc-sync]`: Updated Blueprint IDE panel table in `docs/user_guide/blueprint_manifest_authoring.qmd`. Verified against wrangle_studio.py nav_panels. Actual panels: TubeMap accordion + 4 center nav_panels (1. Focus, 2. Interface, 3. YAML Raw Source, 4. Joint Designer). "Master Manifest" and "External Exchange" do not exist in code — audit claim was spurious. "YAML" renamed to "3. YAML (Raw Source)". Inline reference at §277 updated to match.

---

### Blueprint In-App Help Enrichment

> **Design settled 2026-05-22.** All four tasks unblocked and sequenced.
>
> **Context:** `@register_action` and `@register_plot_component` carry a `ui_schema` dict read at runtime by `schema_registry.py` and rendered in `bp_help_panel_ui`. ADR-075 §4 specifies that 1:1 Polars/Plotnine wrappers should resolve the real library `__doc__` via the `wraps` field (importlib, air-gap safe, zero maintenance). State at task start: transformer had 1/63 actions with `wraps`; viz_factory had 191/192. Neither library had `description` or `yaml_example` fields.
>
> **Build order:** BP-HELP-ADR-1 → BP-HELP-RENDER-1 (parallel-safe after ADR) → BP-HELP-TRANSFORMER-1 → BP-HELP-VIZFACTORY-1.

- [x] **BP-HELP-ADR-1** `[sonnet/low]`: Extended ADR-075 to canonicalize two new optional `ui_schema` fields: `description` (one developer-oriented sentence) and `yaml_example` (minimal correct YAML snippet). Updated `rules_data_engine.md §2` and `rules_persona_bioscientist.md §8`. No code changes.

- [x] **BP-HELP-RENDER-1** `[haiku/low]`: Added render support: `bp_help_panel_ui` renders `yaml_example` as `.bp-help-docstring` code block; `help_registry.py` description column added. Additive — no-op when field absent. Gate: import clean, smoke pass.

- [x] **BP-HELP-TRANSFORMER-1** `[sonnet/high]`: Content sweep — all 60 transformer `@register_action` entries. Added `description` + `yaml_example` to all 60; `wraps` added to 35 actions that are 1:1 Polars wrappers. Dep-sweep clean. 97 tests pass. ✅ 2026-05-22

- [x] **BP-HELP-VIZFACTORY-1** `[sonnet/medium]`: Content sweep — 191 active viz_factory `@register_plot_component` entries. Added `description` + `yaml_example` to all 191 across 7 files. `wraps` already present for all active components. 97 tests pass. ✅ 2026-05-22

---

### Phase 34 — TEST_LAB Build

> **Design:** `.claude/design/spaces/TEST_LAB.md` — all design decisions locked 2026-05-21.
> **Build order:** 34-A (library) → 34-B (utils) → 34-C (bootstrapper) → 34-D (scaffold) → 34-E (synth) → 34-F (anon) → 34-G (reformat) → 34-H (UI last).
> **Note:** `UX-DEVINSP-1` (Deferred — TEST_LAB sidebar redesign) was superseded by TL-UI-SHELL-1.

#### 34-A — ID Reconciliation Library

- [x] **TL-IDLIB-1** `[haiku/low]`: Scaffold `libs/id_reconciliation/` — `pyproject.toml` (deps: `polars`, `utils`, `rapidfuzz`), module structure (`__init__.py`, empty module files), editable install, empty `tests/conftest.py`. Gate: `from id_reconciliation import IDReconciliationEngine` succeeds. ✅ 2026-05-22

- [x] **TL-IDLIB-MATCH-1** `[sonnet/high]`: Core matching — `data_structures.py` (`IDPair`, `MatchResult`, `PatternSuggestion`, `TransformationRecipe`) + `matcher.py` (exact 1.0; `rapidfuzz` token-set ratio with `_/-`→space normalization for fuzzy 0.0–0.99; unmatched 0.0). Gate: `test_exact_match` ✅ `test_fuzzy_match` ✅ boundary-aware (001_ABCD↔ABCD_001) ✅ — 2026-05-22

- [x] **TL-IDLIB-PATTERN-1** `[sonnet/high]`: `pattern_detector.py` — prefix/suffix removal (scan 1–16 chars, best-hits wins), delimiter swap, case normalization; `suggest_regex` ported from `reconciler.py`. Primitives extracted to `libs/utils/id_patterns.py` in TL-UTILS-PATTERN-1. Gate: `test_pattern_suggestion_prefix_sample` ✅ prefix "sample_" ranked first, match_count=5 ✅ — 2026-05-22

- [x] **TL-IDLIB-RECIPE-1** `[sonnet/medium]`: All 7 recode actions + `TransformationRecipe.to_yaml()`/`from_yaml()`. Gate: `test_recipe_persistence` ✅ `test_recode_workflow_prefix_removal` ✅ `test_recode_workflow_delimiter_extraction` ✅ — 2026-05-22

- [x] **TL-IDLIB-CORE-1** `[sonnet/high]`: `IDReconciliationEngine` orchestrator — `core.py`. Progressive matching via Polars LazyFrame, chunks default 50 rows. Recode threshold: 50 unmatched triggers "clean first". Gate: `test_many_to_many_detection` ✅ progressive chunking ✅ — 2026-05-22

- [x] **TL-IDLIB-TESTS-1** `[sonnet/medium]`: Full test suite — unit tests per module + `id_reconciliation_integrity_suite.py`. Gate: `pytest libs/id_reconciliation/tests/ -q` 28/28 pass ✅ `reconciler.py` deleted — 2026-05-22

#### 34-B — Pattern Helper in `libs/utils/`

- [x] **TL-UTILS-PATTERN-1** `[sonnet/low]`: Extracted all pattern primitives (`PatternSuggestion`, `detect_patterns`, `apply_pattern`, `suggest_regex`) to `libs/utils/src/utils/id_patterns.py`. `pattern_detector.py` → thin re-export shim. Gate: 28/28 tests pass ✅ `from utils.id_patterns import PatternSuggestion` works ✅ — 2026-05-22

#### 34-C — ManifestBootstrapper Fixes

- [x] **TL-BOOTSTRAP-FIX-1** `[sonnet/low]`: Fixed `libs/test_lab/src/test_lab/bootstrapper.py`: (1) `"plotting"` → `"analysis_groups"`, (2) removed hardcoded spurious `metadata_schema:`, (3) added `join_manifests: {}` stub, (4) accepts optional `id_cleaning_recipes: dict`. Gate: 10/10 gate tests pass. ✅ 2026-05-22

#### 34-D — Manifest Scaffolding ZIP

- [x] **TL-SCAFFOLD-1** `[sonnet/medium]`: ZIP boilerplate output — `libs/test_lab/src/test_lab/scaffolder.py`. Input: TSV paths + `TransformationRecipe` objects. Output: ZIP with master YAML + fragment files. Gate: 15/15 gate tests pass. ✅ 2026-05-22

#### 34-E — Synthetic Data Upgrade

- [x] **TL-SYNTH-1** `[sonnet/high]`: Upgraded `libs/test_lab/src/test_lab/aqua_synthesizer.py` — `propose_config(source)` + `generate(config)` two-step flow; `mode: demo | stress_test`; `error_injection` block; YAML archive config output with "NOT a pipeline manifest" header; named scenario save/load/list. Gate: 21/21 gate tests pass. ✅ 2026-05-22

#### 34-F — Anonymisation Tool

- [x] **TL-ANON-1** `[sonnet/medium]`: `libs/test_lab/src/test_lab/anonymiser.py` — `anonymise` + `anonymise_batch` (multi-file consistency). Patterns: sequential, hash, custom. Gate: 22/22 gate tests pass. ✅ 2026-05-22

#### 34-G — Reformatting Tools

- [x] **TL-REFORMAT-1** `[haiku/low]`: `libs/test_lab/src/test_lab/reformatter.py` — `DataReformatter` class with `convert_xlsx`, `convert_csv`, `convert_folder`. Gate: 20/20 tests pass; full test_lab suite 88/88. ✅ 2026-05-22

#### 34-H — UI (gates on library tasks)

- [x] **TL-UI-SHELL-1** `[sonnet/medium]`: TEST_LAB UI shell in `test_lab_studio.py` — left sidebar accordion (ID Reconciliation, Manifest Scaffolding, Synthetic Data, Anonymisation, Reformatting); `test_lab_enabled` persona flag gate. Gate: 213/213 tests pass. ✅ 2026-05-22

- [x] **TL-UI-REFORMAT-1** `[haiku/low]`: Reformatting panel — file upload, sheet assignment UI (XLSX), convert button, TSV download. ✅ 2026-05-22

- [x] **TL-UI-RECONCILE-1** `[sonnet/high]`: ID Reconciliation panel — multi-file upload, PRE-CHECK, pairwise match table, pattern suggestion, M2M dialog, certainty threshold slider, recipe YAML download. ✅ 2026-05-22

- [x] **TL-UI-SCAFFOLD-1** `[sonnet/medium]`: Manifest Scaffolding panel — file upload, join key selection, optional metadata TSV, "Bake in ID Reconciliation steps" checkbox (opt-in carry-over from Reconcile panel — reads `_recon_results()` calc, stateless, within one space), boilerplate ZIP download. ✅ 2026-05-22

- [x] **TL-UI-SYNTH-1** `[sonnet/medium]`: Synthetic Data panel — schema/file upload, proposed config review, mode toggle, error injection block, scenario save/load, TSV + YAML download. ✅ 2026-05-22

- [x] **TL-UI-ANON-1** `[sonnet/medium]`: Anonymisation panel — multi-file upload, ID/personal column selectors, pattern picker, ZIP download (anonymised + mapping + config). ✅ 2026-05-22

---

### Legacy Removal (rules_legacy_management.md §6)

- [x] **LEGACY-FLAT-PLOTS-1** `[sonnet/medium]`: Full removal of flat `plots:` authoring key. ConfigManager raises `DeploymentError` if root-level `plots:` found. `stress_test_master.yaml` cleaned. Error-path + happy-path tests added. `rules_manifest_structure.md §8` REMOVED tombstone (expires Phase 36). ✅ 2026-05-22

- [x] **LEGACY-AUDIT-FLAG-1** `[haiku/low]`: Full removal of `audit_report_enabled` flag from `persona_validator.py`, `bootloader.py`, and all 8 templates. Tests updated (21 pass). Tombstones in rules files (expire Phase 36). ✅ 2026-05-22

- [x] **LEGACY-TYPE-ALIASES-1** `[sonnet/low]`: Removed deprecated type aliases `character` / `string`. Migrated 6 manifest files (`string` → `categorical`). Engine raises `TransformationError` for both aliases. 4 new tests added. REMOVED tombstone in `rules_manifest_structure.md §9` (expires Phase 36). ✅ 2026-05-22

- [x] **LEGACY-FLAT-WRANGLING-1** `[sonnet/low]`: Removed engine acceptance of flat `wrangling: []` list. Migrated 2 manifests. `_resolve_tier()` raises `ManifestError` for flat lists with actionable tip. 8 new tests added. `rules_data_engine.md §3` updated. `Standards_yaml.qmd` tombstone (expires Phase 36). ✅ 2026-05-22

---

### Needs Discussion — Closed (implemented)

- [x] **LAB-WORKFLOW-1** `[opus/high]`: Delivered `.claude/design/developer_workflow.md` — producer journey across TEST_LAB → BLUEPRINT → GALLERY → HOME; module-independence first principle ("map, not a wizard"); advisory-only orderings (reconcile-before-anonymise/scaffold); file-based linking only (no in-app handoffs). Key decision with Eve (2026-05-22): keep app simple, keep spaces independent — linking is file-based (export → choose), workflow explained in documentation. Spawned: LAB-WORKFLOW-QMD-1 (active, Do Now). LAB-SEND-TO-1 and LAB-OPEN-BLUEPRINT-1 both DROPPED (see Decisions section below). ✅ 2026-05-22

- [x] **UX-APPLY-IMPROVE-1** `[sonnet/low]`: Propagation modal — "apply to all except…" selection-by-exclusion. `propagation_except` selectize hidden by default, revealed only when "All plots except…" radio selected via inline `<script>` listening on `propagation_choice`. No handler changes. ✅ 2026-05-22

---

## Deferred Indefinitely — Future Nice-to-Have

Items that are real, valid ideas but not scheduled. Not dropped — just parked until the moment is right. Functional need is already met by existing implementation.

### PROP-3 — Propagation TubeMap (deferred indefinitely, 2026-05-22)

**What it is:** A graph/TubeMap-style visualization of audit blast radius — plot nodes with edges showing which T3 audit decisions propagated where. The spec also includes an "Applied to N plots" badge on each audit card.

**Why deferred:** The functional need is already served. The propagation modal already shows a full blast-radius preview ("✅ 3 apply · ⚠️ 1 skip · ❓ 1 unknown" with a details list) and column-presence checks per plot. `_handle_propagation_confirm` commits to `t3_recipe_by_plot` with shared IDs. The graph visualization would be `[opus/high]` polish on top of working functionality.

**If revisited:** Needs its own ADR. Key design questions: where it lives (audit sidebar? modal? tab?), whether it's reactive/live or on-demand, and whether to reuse the Cytoscape.js already in the Blueprint TubeMap.

**Reference:** `app/handlers/filter_and_audit_handlers.py` (`_open_propagation_modal`, `_handle_propagation_confirm`), `ui_implementation_contract.md §12g`.

---

## Decisions — NOT IMPLEMENTED

Items explicitly considered and rejected. Kept here to document the reasoning.

### LAB-SEND-TO-1 — DROPPED (2026-05-22)

**What it was:** In-app "Send to Manifest Scaffolding" button on the ID Reconciliation panel output.

**Why dropped:** Breaks module independence. Each Lab tool must be a standalone module — choose input files, export outputs — exactly like any independent module. An in-app "Send to" injection would mean the Scaffolding panel couldn't function independently. The pre-existing Reconcile→Scaffold recipe carry-over (opt-in checkbox in Scaffolding) is the right scope: it reads a reactive calc, not an injection, and Scaffolding still works fully standalone without it.

**Reference:** `developer_workflow.md §5`, `feedback_app_simplicity.md`, `feedback_space_independence.md`.

### LAB-OPEN-BLUEPRINT-1 — DROPPED (2026-05-22)

**What it was:** "Open in BLUEPRINT" button inside TEST_LAB to load a scaffolded manifest ZIP directly into the Blueprint Architect.

**Why dropped:** Cross-space in-app coupling violates space independence. `test_lab_enabled` and `blueprint_enabled` are **independent** persona flags — a persona can grant TEST_LAB without BLUEPRINT. An in-app handoff would break the instant BLUEPRINT is disabled (ADR-071 positive-inclusion). Handoff stays file-based: export the manifest ZIP from TEST_LAB → load it in BLUEPRINT if/when the user has it enabled.

**Reference:** `developer_workflow.md §7`, `feedback_space_independence.md`.

### UX-DEVINSP-1 — SUPERSEDED (2026-05-21)

**What it was:** TEST_LAB sidebar redesign (originally "Dev Studio" sidebar redesign).

**Why closed:** Superseded by TL-UI-SHELL-1 (Phase 34-H). Design locked 2026-05-21 in `.claude/design/spaces/TEST_LAB.md`.

### GREAT-DOCS-1 — DROPPED (2026-05-22)

**What it was:** Evaluate `great-docs` (https://github.com/posit-dev/great-docs) for auto-generating a static Quarto/website reference from the codebase.

**Why dropped:** The use case is already solved in-app, better than a static site could. `bp_help_panel_ui` (`app/modules/wrangle_studio.py`) already renders context-aware help for the selected action: `description` (developer sentence), `yaml_example` (copy-paste YAML), and real Polars/Plotnine `__doc__` resolved at runtime via `importlib` through the `wraps` field (`_resolve_action_doc()`). Coverage: all 60 transformer actions + all 191 viz_factory components. `great-docs` reads Python docstrings and generates a static site — a separate browseable directory adds no value when the help is already context-aware and in-app. Additionally, `great-docs` does not integrate with Quarto, and the `CODE-DOCS-RETROSPECTIVE` prerequisite (function-level docstrings) is deferred to the pre-deployment sprint.

**Reference:** `app/modules/wrangle_studio.py:94` (`_resolve_action_doc`), `app/modules/wrangle_studio.py:1007` (`bp_help_panel_ui`), ADR-075 §4 (`wraps` resolution spec).
