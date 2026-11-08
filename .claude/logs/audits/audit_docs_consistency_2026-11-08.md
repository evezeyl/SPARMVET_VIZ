Status: PROCESSED 2026-11-08 — all ~55 findings fixed directly (6 parallel fix agents, one per audit
area), plus 2 incidental findings caught during final verification (a wrong `refresh_gallery.py` path
introduced by one fix agent, a remaining `audit_template_flags.py` stale name outside docs/ scope,
fixed as a bonus since it was the same already-identified bug). 0 false positives, 0 accepted debt.
Verified: full `quarto render docs --no-execute` (58/58 clean, 0 warnings), `check_doc_links.py`
(87 problems, down from the 88 pre-existing baseline — all remaining are unrelated pre-existing
issues), `audit_uml_model.py` (0 violations).

# Audit Report: Documentation Consistency (docs/ Quarto book vs ADR log, UML model, code)

Date: 2026-11-08
Scope: all 56 `docs/**/*.qmd` files, cross-checked against `.claude/knowledge/architecture_decisions.md`,
`docs/UML/app.mdj`, and the real code (`app/`, `libs/`, `config/`, `assets/scripts/`) via grep/find.
Method: 6 parallel read-only agents, one per doc area, each instructed to confirm every claim against
code before reporting (not just compare doc text to doc text). No edits made — reconnaissance only.
Excluded from scope: `.claude/rules/*.md` (agent operating instructions, not the shipped book).

## How to read this report

Findings are grouped by **systemic issue** first (the same problem repeated across many files — fix
once, apply everywhere), then by **file**, most severe first. Each finding has a category:
- **BROKEN** — a worked example/command that would actually fail if run, or a UI label that's wrong
- **FABRICATED** — describes a class/feature/directory/button that does not exist anywhere in the code
- **STALE VOCAB** — uses terminology/behavior that was renamed or restructured (ADR exists)
- **UNMARKED HISTORICAL** — the content is obsolete but has no `HISTORICAL`/`ARCHIVED` banner
  (`rules_legacy_management.md`), so a reader can't tell it's not current

---

## A. Systemic issues (same problem, many files — fix the pattern once)

### A1. Single Tier 1/2/3 toggle framing, superseded by ADR-085/086's two independent choices
The current HOME header strip is **two** independent selectors — "Plot to show" (Result / My view /
Compare) and "Data to show" (Raw / Result / My view) — not one combined T1/T2/T3 toggle. Also the T3
label is **"My view"**, not "My adjustments" (only survives in a stale test helper,
`app/tests/debug_home_theater.py:179`).
Files affected: `docs/foundations/data_tiering_adr.qmd`, `docs/appendix/data_lifecycle_theater.qmd`
(already flagged, tracked as `DOC-TIER-PROSE-REFRESH-1`), `docs/workflows/ui_app_features.qmd`,
`docs/workflows/dashboard_app.qmd`, `docs/reference/ui_style_guide.qmd` (internally inconsistent — cites
ADR-086 correctly elsewhere in the same file), `docs/user_guide/audit_pipeline.qmd`,
`docs/user_guide/system_transparency.qmd` (sections 1-3 stale, section 4 already correct).

### A2. `DataContractError` — cited as the standard exception, doesn't exist
`docs/reference/development_rules.qmd` and `docs/reference/testing.qmd` both tell developers to
`raise DataContractError(...)`. No such class exists anywhere (`grep -rn DataContractError` → zero
hits). Real hierarchy: `SPARMVET_Error` → `IngestionError` / `TransformationError` /
`VisualizationError` / `DataAnalysisRecipeError` (`libs/utils/src/utils/errors.py`), plus
`PipelineError` (`libs/utils/src/utils/pipeline_error.py`).

### A3. Stale "Workspace Standard Section 8 / Section 10" citations
`workspace_standard.md` only has sections 0-5. `docs/reference/decorator_testing.qmd` and
`docs/reference/development_rules.qmd` cite "Section 8" and "Section 10" respectively for content
that actually lives in `rules_data_engine.md §2` (1:1:1 Naming Law) and
`rules_verification_testing.md` (Integrity Suite Mandate).

### A4. Registered action/component counts, stale everywhere they're quoted
Every quoted count is out of date: "25+", "19", "62/60 tested" actions (real: 63 registered,
`grep -c '^@register_action('`); "7", "120+", "172", "191/194" plot components (real: ~190-194,
`grep -c '^@register_plot_component('`). Appears in `docs/workflows/wrangling.qmd`,
`docs/workflows/transformer_integrity.qmd`, `docs/workflows/visualisation_factory.qmd`,
`docs/reference/developer_how_to.qmd`, `docs/reference/testing.qmd`,
`docs/appendix/viz_factory_components.qmd`, `docs/appendix/transformer_actions.qmd`. Low severity
individually (numbers naturally drift as the registry grows per ADR-035/036), but worth a single pass
— or better, phrase these as "see the registry" instead of a number that will drift again.

### A5. Unquoted `on:` shown as the canonical join-key example
The YAML boolean trap (`on:` parses as `True` unless quoted `'on':`) is a documented, explicit,
repeatedly-warned-about hazard (`rules_data_analysis_recipe_structure.md §7`,
`rules_agent_role_bioscientist.md` absolute prohibition #3) — yet `docs/foundations/data_contracts_adr.qmd`
and `docs/appendix/Standards_yaml.qmd` both show **unquoted** `on: sample_id` as their flagship worked
example, self-contradicting other sections of the same files that correctly warn against it.

### A6. "Clone to Sandbox" / Gallery-to-other-space handoff, fabricated or lingering (ADR-093)
Gallery has zero interactive handoff anywhere (ADR-093, this session). `docs/user_guide/viz_gallery.qmd`
fabricates an entirely different nonexistent feature (an in-app "Upload Data/DataAnalysisRecipes"
submission flow with admin review) in the same spot where the old Clone-to-Sandbox language used to be.
`docs/appendix/test_lab_rationale.qmd` separately describes "ghost-loading" Gallery examples into Test
Lab, also removed/never-real.

### A7. Non-existent directories/paths cited as real
`config/connectors/`, `config/ui/` (claimed to hold app-features flags — it actually holds
`theme.css`/`sidebars/`/`agents/`), `config/deployments/` (plural — real is `config/deployment/`,
singular), `libs/wrangling/` (real: `libs/transformer/`), `assets/template_data_analysis_recipes/`
(doesn't exist — also a known code-side bug, `.claude/tasks/uml_findings.md` F-10), `tmp/reconciler/`,
`tmp/decorator_suite_results/` (real: `tmp/wrapper/`). Each cited once in a different foundations/
reference file — see per-file list below.

### A8. Non-existent classes/concepts cited as real
`Summarizer` (performance/aggregation.py has no such class, only `action_summarize`/
`action_count_by_group`), `plot_archetypes` library, a "Python Configuration Registry" class,
`ConfigRegistry`, a "Species Dropdown" UI element — none exist anywhere in `app/` or `libs/`.
All in `docs/foundations/core_architecture.qmd` and `docs/foundations/data_tiering_adr.qmd` (which
also now contradicts its sibling `reproducibility_hash_schema.qmd` on how Tier 1/2 caching actually
works — that file is correct, this one is stale).

### A9. Non-existent action names / wrong params (would silently do nothing or crash if copy-pasted)
`conditional_mutate` (not registered — real: `label_if`/`mutate`), `select_columns` (real:
`keep_columns`), `unpivot` using `id_vars`/`value_vars` (real: `index`/`on`), `pivot` using `columns:`
(real: `on:`), `derive_categories` using `source_column:` (real: `columns:`). In
`docs/user_guide/data_literacy.qmd`, `docs/appendix/transformer_actions.qmd`,
`docs/appendix/Standards_yaml.qmd`.

### A10. `docs/appendix/viz_factory_components.qmd` — entire worked-example schema is obsolete
Every example in sections 1-5 uses a `components: [{type: "geom_point", ...}]` shape. The engine has
never read `"components"` or `"type"` for plot layers in the current code — current canonical is
`layers: [{name: geom_point, params: {...}}]` (ADR-083). This is not a few stale lines, it's the
file's entire teaching content.

### A11. `docs/appendix/test_lab_rationale.qmd` — describes a different, older product
Frames Test Lab as an interactive sandbox with an action-picker, a "Triple-Tier Grid," and
Gallery-ghost-loading. Current Test Lab (ADR-084) is a stateless toolbox with zero persistent state
and explicitly **no action-picker UI**. The file even subtitles itself "(Wrangle Studio)" — but
`Terminology.qmd` (same doc set) correctly says Wrangle Studio *is* Blueprint Architect, a separate
space. Needs a rewrite, not a patch.

---

## B. Per-file findings not covered by a systemic issue above

### docs/index.qmd
- **BROKEN** link `./appendix/user_guide_gallery.qmd` doesn't exist — real file is
  `docs/user_guide/viz_gallery.qmd`.

### docs/foundations/core_architecture.qmd
- **FABRICATED** "Mode A (General Dashboard)" / "Mode B (Fixed Pipeline)" driven by a `run_config.yaml`
  that doesn't exist — real mechanism is `config/deployment/*.yaml` + `SPARMVET_DEPLOYMENT`.
- **STALE VOCAB** gallery handler table cell says "filtering, preview, **clone, submission**" — both
  removed/never-wired (clone: ADR-093; submission: `SubmissionExporter` imported only by tests, F-20).

### docs/foundations/data_contracts_adr.qmd
- (see A5) otherwise clean — Rich Dictionary format, tiered wrangling, `final_contract` whitelist all
  verified current.

### docs/foundations/verification_protocol.qmd
- **STALE VOCAB** routes all debug evidence straight to `tmp/`, with no mention of `tmpAI/`. Current
  rule (`rules_verification_testing.md §6`): agent-internal runs go to `tmpAI/` first, only promoted to
  `tmp/` at the `@verify` halt. CLI flag names themselves are still correct.

### docs/workflows/wrangling.qmd
- **BROKEN** flagship "Standard YAML Format" example is a **flat** `wrangling:` list — the engine
  rejects this with `DataAnalysisRecipeError` (LEGACY-FLAT-WRANGLING-1).
- **BROKEN** import path `from libs.transformer.src.actions.base import register_action` — real:
  `from transformer.actions.base import register_action`.

### docs/workflows/transformer_integrity.qmd
- **FABRICATED** path `assets/template_data_analysis_recipes/` (also a known code-side bug, F-10 in
  `uml_findings.md` — the script itself references the wrong path too).

### docs/workflows/audit_scripts.qmd
- **BROKEN** `audit_template_flags.py` doesn't exist (renamed `audit_app_features_flags.py`), referenced
  4+ times. Same stale name also in `.claude/workflows/audit_routine_registry.md` — repo-wide, not
  unique to this doc.

### docs/workflows/ui_app_features.qmd
- **BROKEN** `export_enabled:` declared twice in the same sample YAML block (invalid YAML).
- **STALE VOCAB** "Export Active Graph" described as a current feature — removed, replaced by the
  3-way scope toggle in the Export panel (2026-05-04 redesign).
- **STALE VOCAB** "Test Lab (Wrangle Studio)" — mislabeled; Wrangle Studio is Blueprint Architect.

### docs/workflows/dashboard_app.qmd
- Minor: "Thin orchestrator (~228 lines)" vs actual 240 lines in `server.py` — negligible, not worth a
  dedicated fix.

### docs/workflows/ingestion.qmd
- **BROKEN** `handle_ingest (server.py)` — actually lives in `app/handlers/ingestion_handlers.py`
  (moved by the ADR-045 decomposition).
- **STALE VOCAB** "External Ingestion" helper → current name "Data Import" (sidebar panel type
  `data_import`). Whole file reads as an early draft; worth a broader rewrite pass beyond these two.

### docs/workflows/test_lab_sdk.qmd
- **STALE VOCAB** calls Blueprint Architect a "future Visual Pipeline Designer" — it already shipped.
- **STALE VOCAB** "GUI Forward-Compatibility" section frames `AquaSynthesizer`/Bootstrapper GUI wiring
  as future work — `app/handlers/test_lab_handlers.py` (990 lines) already wires all of it.

### docs/workflows/user_preferences.qmd
- **FABRICATED** describes a working "User preferences" feature (per-session style config, DI into
  VizFactory) with zero trace in code. `ui_implementation_contract.md` itself marks this
  "[Implementation Deferred] ... Not implemented yet." Needs a deferred banner or removal.

### docs/workflows/visualisation_factory.qmd
- clean apart from the stale count (A4).

### docs/reference/debugging_pipelines.qmd
- **FABRICATED** `tmp/reconciler/full_audit_map.tsv` — nothing writes this file; the real API returns
  an in-memory DataFrame (`format_match_table()`).

### docs/reference/decorator_testing.qmd
- **BROKEN** results path `tmp/decorator_suite_results/` — real: `tmp/wrapper/`.

### docs/reference/developer_how_to.qmd
- **FABRICATED** `test_sdk.py` under `libs/id_reconciliation/` doesn't exist — real tests are
  `libs/test_lab/tests/test_synthesizer.py`/`test_extractor.py`.

### docs/reference/development_rules.qmd
- **FABRICATED** instructs logging unhandled exceptions to a `dashboard.log` file — no such
  logging infrastructure exists anywhere.
- **BROKEN** `pytest app/src/` (no tests there) and `pytest tests/` (no such top-level directory).
- Minor: ADR-016 mislabeled "Clear Lines" (that's ADR-011) — but the ADR log itself is ambiguous on
  this in one place too; flagged low-confidence, worth a `@sync` check rather than a blind fix.
- `libs/wrangling/` cited, doesn't exist (real: `libs/transformer/`) — see A7.

### docs/reference/environment_variables.qmd
- **BROKEN** claims the app features YAML key is `app_features_id` — real key is `name:`.

### docs/reference/testing.qmd
- **BROKEN** `pytest libs/ingestion/` collects zero tests (no `test_*.py` files there, only debug/
  integrity scripts) — verified by actually running it.
- **FABRICATED** "Species Dropdown," "ConfigRegistry" — don't exist; reads like leftover pre-rename
  content.

### docs/reference/ui_style_guide.qmd
- (see A1) — internally inconsistent, correct elsewhere in the same file.

### docs/user_guide/audit_pipeline.qmd
- **BROKEN** quotes the Apply button as "➜ Audit (N)" — real label: "➜ Send to Audit (N)".
- (see A1 for the tier-toggle framing)

### docs/user_guide/viz_gallery.qmd
- (see A6) — fabricated upload/submission workflow; real path is file-based
  (`assets/gallery_data/` + `refresh_gallery.py`, per `rules_gallery_standards.md`).
- **STALE VOCAB** conflates BLUEPRINT wrangling-node comments with T3's mandatory `reason` field — these
  are different mechanisms in different spaces.

### docs/user_guide/data_literacy.qmd
- (see A9) — two nonexistent actions.
- **STALE VOCAB** conflates BLUEPRINT (authors T1/T2 YAML) with T3 (audit-only, no wrangling UI).

### docs/user_guide/glossary_and_feedback.qmd
- **STALE VOCAB / self-contradiction** defines "Leaf" as a joined supplementary dataset, then two
  bullets later correctly defines Tier 3 as "the Leaf" — the file disagrees with itself.
- Minor: T3 scope description omits column-drop and row-exclusion node types (undersells current scope).

### docs/user_guide/system_transparency.qmd
- (see A1 for sections 1-3) — also wrongly calls the (fully shipped) Send-to-Audit button
  "feature in progress," and describes a re-upload error-loop workflow superseded by ADR-094's
  automatic load gate. Section 4 is correct and current.

### docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd
- **BROKEN** "click Branch Node" — no such single button; real flow is "Preview branch" / "Create
  branch" in the sidebar form.
- **FABRICATED** "+ Schema" toolbar button — doesn't exist; adding a `data_schema` node is YAML-panel-
  only today.
- Minor: "Validate" button is actually labelled "Run validation".

### docs/deployment/deployment_guide.qmd
- **STALE VOCAB** "dev studio" in the `developer` app-features row — renamed "Test Lab" (Phase 25-A);
  `dev_studio` only survives as an internal Python variable name.

### docs/troubleshooting/index.qmd
- **BROKEN, undermines the page's whole premise** — claims every startup error prints a lookup
  `slug`. `DeploymentError` has no `slug` field; the slug is purely a documentation-authoring
  convention, never printed by the running app. The individual error entries themselves are accurate.
- Minor: several anchor ids contain literal spaces (e.g. `{#app features t3-companions-missing}`),
  inconsistent with the page's own stated kebab-case convention.

### docs/vision/platform_evolution.qmd
- **UNMARKED HISTORICAL** — reads as a live roadmap, frozen at "Phase 9" language while the repo is at
  Phase 34+. Calls Blueprint Architect a "future... Shiny UI YAML text area" (it shipped, and is far
  beyond that) and calls Gallery a "planned... Quarto page" (it shipped as an in-app Shiny browser).
  Needs a `HISTORICAL` banner per `rules_legacy_management.md §2b`, not a word-level fix.

### docs/appendix/data_types_philosophy.qmd
- **FABRICATED** "Critical Rule: joins MUST occur within a `pl.StringCache()` context" — no
  `StringCache` usage anywhere in the codebase; real mechanism is an explicit `cast` step.

### docs/appendix/DashBoard_Architect_v1.qmd
- **UNMARKED HISTORICAL** — recommends Shinylive/WASM, directly contradicting the live, active
  `dasharch.md §4` ban ("STRICT: NO WASM/SHINYLIVE"). No archival banner, unlike its siblings
  `data_flow_analogy.qmd`/`data_lifecycle_theater.qmd` which do have one.
- Minor: `draw_barplot(df, x_var, y_var, color_var)` — current mandated signature is
  `draw_plot(df, x, y, color)`.

### docs/appendix/running_helper_scripts.qmd
- **BROKEN**, 5 separate documented commands fail as written (wrong flag names/hyphens, missing
  required args) for `create_test_deployment.py`, `create_data_analysis_recipe.py`,
  `SF_create_data_analysis_recipe.py`, `debug_apply_data_analysis_recipe_standards.py`, and the
  claimed replacement script for the deprecated materialize shim (real: `debug_gallery.py`, not
  `debug_assembler.py`).

### docs/appendix/viz_factory_rationale.qmd
- **FABRICATED** example uses root-level `plots:` (removed, LEGACY-FLAT-PLOTS-1).
- **UNMARKED HISTORICAL** describes a "PROPOSED" Gallery CLI flag (`--gallery` on
  `viz_factory_integrity_suite.py`) that was superseded years ago by the real, differently-built
  Gallery — presented with no marker that the plan changed.
- Minor: cites Plotnine 0.16.x and a personal `/home/evezeyl/Downloads/...` path; pinned version is
  0.15.4.

### docs/appendix/Terminology.qmd
- Good shape overall (the highest-risk file, checked most thoroughly, held up well). One thing worth
  confirming with you directly rather than auto-fixing: "Record"/"Record ID" ("formerly Sample")
  appears nowhere else in the codebase, rules, or ADRs — every other site says `sample_id`. Possibly
  an abstraction that was never actually adopted — your call whether to keep, change, or drop it.

### Already known / already fixed this session (no new action needed)
`docs/appendix/data_lifecycle_theater.qmd` (tracked as `DOC-TIER-PROSE-REFRESH-1`),
`docs/workflows/blueprint_architect.qmd` prose (reviewed clean beyond the diagrams already redrawn
today).

### Clean files (no issues found)
`docs/front_page.qmd`, `docs/foundations/core_architecture_code.qmd`,
`docs/foundations/reproducibility_hash_schema.qmd`,
`docs/foundations/reproducibility_same_input_same_output.qmd`, `docs/workflows/connector.qmd`,
`docs/workflows/developer_workflow.qmd`, `docs/user_guide/understanding_your_export.qmd`,
`docs/user_guide/reproducible_plots.qmd`, `docs/user_guide/yaml_101.qmd` (one low-priority nit only),
`docs/appendix/audit_benchmarks_st22.qmd`, `docs/appendix/data_flow_analogy.qmd` (properly archived),
`docs/appendix/AI_and_development_process.qmd`, `docs/appendix/Libraries_choices.qmd`,
`docs/appendix/External_ressources.qmd`, `docs/appendix/FAQ.qmd`,
`docs/appendix/python_environment.qmd`, `docs/appendix/Shiny_flavors.qmd`,
`docs/appendix/Unknowns_and_Expansion.qmd`, `docs/reference/wrangling_guide.qmd` (properly archived).

---

## Severity summary

- **BROKEN / FABRICATED** (would mislead a reader into writing something that fails, or claims a
  feature that isn't there): ~35 findings across ~20 files. Highest-impact single items: A10 (whole
  `viz_factory_components.qmd` example set), A11 (whole `test_lab_rationale.qmd`), A2
  (`DataContractError`), `troubleshooting/index.qmd`'s slug-lookup premise, `running_helper_scripts.qmd`
  (5 broken commands), A6/A9.
- **STALE VOCAB** (correct-ish but uses superseded terms/framing): ~20 findings, dominated by A1 (the
  Tier-toggle framing, 7 files) and A4 (stale counts, 7 files).
- **UNMARKED HISTORICAL**: 3 files need a banner, not a rewrite (`platform_evolution.qmd`,
  `DashBoard_Architect_v1.qmd`, part of `viz_factory_rationale.qmd`).
- **Clean**: 19 files needed no changes at all.

No `Status:` line yet — this report is UNPROCESSED per `audit_triage_protocol.md`.
