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
| **🟡 Bio-Scientist Enhancements** | `[ENHANCEMENT REQUEST]` items from data analysis recipe design sessions only (see `rules_agent_role_bioscientist.md §4-A`). |
| **👤 User Required** | Needs user action, decision, or explicit discussion. No agent progress until user responds. |

**Rules for keeping the file clean:**
- **Empty sections stay empty.** If Do Now has no items, leave it blank — no placeholder text, no status lines.
- **`> Completed:` / `> Status: COMPLETED` inline pointers inside sections are FORBIDDEN.** When items are done, move them to the archive file and update the archive table + pointers at the bottom.
- **Context and session notes go at the bottom** — in the `## 📋 Session Notes` section, not inside active task sections.

---

## 🟢 Do Now

Items with no blockers — can be started immediately.

### HOME Exploration and engine fixes (issues #56, #61, #62, #63; brief: `home_exploration_build_brief.md`)

Compatible with the audit redesign (ADR-099), which is not decided yet; none of these touches the header strip, My view or the
audit steps. Order: WP1, WP2, WP3a, WP4 (with WP5), WP6. Safety protocol S1-S8 of the brief binds (baseline, one commit per package, frozen files, compatibility with the audit).

- [ ] **HOME-EXPLORE-1** `[sonnet/medium]` — #62 integer thresholds: one shared filter-value implementation (`libs/utils`), correct rounding by operator, equivalence test engine = VizFactory = translated recipe action (today the figure and the reproducibility bundle DISAGREE), tests from the table of #62, mutation check.
- [ ] **HOME-EXPLORE-2** `[sonnet/medium]` — #61 key extraction reads tiered join steps and `is_primary_key` (inferred when absent), works for recipes without joins; test in a collected `test_*.py` on the real `ConfigManager`; fix or retire `debug_home_theater.py` (IndentationError, not collected). Expect the PK safeguards of ADR-049 to start firing.
- [ ] **HOME-EXPLORE-3a** `[sonnet/medium]` — #63 step 1: inform only ("N rows have no value in this column and are removed by this filter"), no change of the rows.
- [ ] **HOME-EXPLORE-3b** `[sonnet/high]` — #63 step 2, the NA rule: **BLOCKED, do not start** (needs Eve's default and the audit step compiler; engine and registered actions must change together, backward compatible).
- [ ] **HOME-EXPLORE-4** `[sonnet/high]` — #56 preview lists per dataset (pure store), cleared on Data-to-show and recipe change with a message and a WHY comment, panel header names the target, reset-to-all-columns button, one operator vocabulary.
- [ ] **HOME-EXPLORE-5** `[sonnet/high]` — filter test suite with a data oracle (table text and "Viewing rows a through b of N"), edge cases of `home_preview_filters.md` section 9, screenshots in `tmpAI/`, mutation check per rule.
- [ ] **HOME-EXPLORE-6** `[haiku/low]` — help, user guide, FAQ, ADR-098 and contract text for the above.
- [x] **RECIPE-ST22-1** `[sonnet/medium]` (2026-11-11, `recipe_review_st22_2026-11-11.md`) — data-scientist review of `1_test_data_ST22_dummy`: plots with ignored `facet_by`/`facet_scales`/`labs`/`coordinate_flip` corrected with explicit layers, horizontal QC bars, unknown `plot_defaults` keys, `Detailed_summary` type, `sample_id` contract type, legacy `tier3` block removed; collections byte-identical; guard `app/tests/test_shipped_recipes_hygiene.py`. Issues #65-#71.
- [ ] **RECIPE-ST22-2** `[opus/high]` — waits for Eve: what `ST22_Anchor` answers (#67: fan-out ResFinder x VirulenceFinder, wrong `virulence_count`, AMR "status" as virulence fill, missing `phenotype` in the contract), score of samples without usable phenotype (#70), MLST title and demo filter. Then fix the recipe, look at every picture, update the contract.
- [x] **HOME-EXPLORE-7** `[sonnet/medium]` — DONE 2026-11-11 (`4f85ec2`): #65 `mapping.facet_by` honoured by the resolver; unit tests, `test_render_every_plot` asserts panels, six plots looked at, mutation-checked. `virulence_variants` kept unfaceted until Eve decides (#67).
- [ ] **HOME-EXPLORE-8** `[sonnet/medium]` — #66 warning for plot-spec keys dropped to `_meta` (same surface as unknown `plot_defaults` keys). See brief WP8.
- [x] **HOME-EXPLORE-9** `[sonnet/low]` — DONE 2026-11-11 (`af36dc9`): #71 the recipe data check runs the wrangling on one row (types, not values); two tests, mutation-checked.
- [ ] **HOME-EXPLORE-10** `[sonnet/medium]` — #68 many-to-many join warning (rows before/after). Edits `libs/transformer` (frozen): needs Eve's OK. See brief WP10.
- [x] **RECIPE-ST22-3** `[sonnet/high]` — DONE 2026-11-11 (`c2cb302`): group "QA Canaries" in `1_test_data_ST22_dummy` (6 plots, 5 collections, one failure mode each, answers computed from the raw files in `app/tests/test_qa_canaries.py`, expected numbers in the plot subtitles, one exhibit of a known defect). Canary map: brief section 0b. Extend it when you find a new failure mode.
- [ ] **AUDIT-CUT-1** `[opus/high]` — Eve reviews the proposal `.claude/design/home_audit_first_cut.md` (a smaller first audit version) with the agenda `home_audit_review_agenda_2026-11-12.md`; then the accepted cut becomes work packages and sub-issues of #60. Depends: AUDIT-DECIDE-1 (group 1 of the agenda).
- [ ] **NEXT-SESSION-1** — builders and the design review start from `.claude/tasks/next_session_start.md` (tracks A, B, D; file ownership; traps; paste-ready prompts).
- [ ] **AUDIT-FORENSICS-1** `[opus/high]` — Eve reads `.claude/design/home_evidence/home_audit_forensics_2026-11-12.md` (13 forensic findings, options and recommendations per undecided item) in the review; decisions go into the design files. Notable: no shipped recipe can show the central flaw of #60 (add a canary), an audit state can run as a forked recipe through a second orchestrator (alternative to a bespoke cache, proof of concept passed), `pipeline-exploration-simple` and `web-demo` would lose plot-changing views, stale wording and "never" in 8 HOME diagrams.
- [ ] **RECIPE-ST22-4** `[sonnet/medium]` — the recipe review steps for 2026-11-12 are in section 5 of `recipe_review_st22_2026-11-11.md` (after Eve answers R1-R4).
- [x] **QA-CANARY-AGG-1** `[sonnet/low]` — done 2026-11-12: canary `QA_aggregated_no_key` / `qa_aggregated_no_key` in `1_test_data_ST22_dummy` (T1 keeps `sample_id`, the T2 the plot reads has none; 9 country/year groups, 42 samples) and `test_aggregated_plot_data_has_no_sample_key` with a raw-file oracle. Mutation-checked (keeping `sample_id` in the aggregate fails the test), picture looked at (the first subtitle was cut off and said "9 bars" instead of 9 segments: fixed). Headless 1649 passed. Fixture for the audit reach (#60, forensics F1).
- [x] **AUDIT-ARCH-REVIEW-1** `[opus/high]` — done 2026-11-12: `.claude/design/home_evidence/home_audit_architect_review_2026-11-12.md` (findings AR1-AR10, undecided items seen by an architect, decisions N2-N6) and the cheaper engine explained with measurements in `.claude/design/home_evidence/home_audit_forensics_2026-11-12.md` 3.2b; F8 and 3.7 corrected (a feature without audit never changes a plot: Eve's rule, not a loss). Scratch scripts in `tmpAI/architect/`.
- [x] **HOME-GATING-PAPER-1** `[opus/high]` — done 2026-11-12: `.claude/design/home_evidence/home_gating_and_test_configs_2026-11-12.md` (how filters are gated by configuration, preview vs audit capabilities, options G1-G4, companion rule R-a..R-c, test configurations C1-C4, 8 questions). Verified by running: scratch configurations validate by path and launch; a no-audit configuration offers My view; the "Exploration only" notice is gated by a proxy flag; the Export panel says "steps sent to audit" where none can exist; Rule 6 makes audit without Compare fatal.
- [ ] **HOME-DESIGN-FIRST-1** `[opus/high]` — Eve's correction 2026-11-12: design first. She answers Q1-Q5 of `.claude/design/home_design_first_roadmap_2026-11-12.md` (behaviour table by kind of configuration). Then I write the agreed table into `home_preview_filters.md`, `home_audit_steps.md`, ADR-099, correct the contract 7.1, add columns A and D to HOME-VIEW-MATRIX (her OK for the UML first). Only after: mechanism (stage 2), build plan (stage 3).
- [ ] **CONFIG-REVIEW-1** `[sonnet/medium]` — stage 5, after the design is coded (Eve, 2026-11-12; targets in `home_audit_reading_guide.md` section 0c): rename `pipeline-exploration-simple` to `pipeline-simple-exploration` (audit off, comparison off); `pipeline-exploration-advanced` = Exploration + Audit (+Compare, sessions, export), no Test Lab, Blueprint, Gallery; `developer` everything; `demo-vetinst` -> `web-demo-vetinst`; `web-demo` renamed once Eve decides static or Exploration only (earlier idea `static-web`); `standalone`, `qa` and others are Claude's test configurations, replaceable; `pipeline-static` unchanged (hyphen, validator Rule 2; also `demo-vetinst`; touches README, `docs/appendix/Terminology.qmd`, `docs/workflows/ui_app_features.qmd`, `app/tests/test_flag_matrix_doc.py`, `app/tests/test_every_app_features_starts.py`, the flag matrix of `rules_app_features_flags.md`, `docs/UML/app.mdj`, `assets/scripts/audit_old_words.py`, the deployment file under `config/deployment/demo/`). Not before the design and the build.
- [ ] **HOME-GATING-DECIDE-1** `[opus/high]` — **PAUSED** (stage 5, derived from the behaviour table): capability resolver, test configurations, companion rule, the two small defects. Do not start before HOME-DESIGN-FIRST-1 is agreed.
- [ ] **AUDIT-ARCH-DECIDE-1** `[opus/high]` — Eve decides after reading (status map in forensics section 0): first the interim of the header strip for features without the sandbox flag (forensics 3.7, F8) and "Raw has no plot (NA)" (F14); then N2 (what to do with the `developer_raw_yaml` step type: no code creates it; recommended display-only), N3 (trust levels for recipe text, AR1), N4 (how to hold the decided flag rules), N5 (architecture rules as tests), N6 (stored stages of the original anchors, needs her OK for `libs/transformer`), and the places where the forensics reconsider something decided (R1-R6). Candidate issues are listed in section 6 of the architect review; none is filed.
- [ ] **HOME-DESIGN-REVIEW-1** `[opus/high]` — independent review of the decided design done 2026-11-12 (`.claude/design/home_evidence/home_design_review_2026-11-12.md`, guide problem P10). Eve decides, in order: SC1 (check on the plotted variable into the first set), SC2 (caption count for plots without a key), SC4 (remove by attribute), AR4 (entity noun field), SC5 (exclusion list), the wordings SC3/DS1/DS2, AR2 (oracle test for the action registry), AR1 (special datasets such as `metadata_schema`, stage 2). AR3/AR5/AR6 are build rules. Then the list of changed sections to read and the rewrite of `spaces/HOME.md`.
- [ ] **RECIPE-SPEC-1** `[opus/high]` — Eve 2026-11-13, tracking evezeyl/SPARMVET_VIZ#73 (parent of this block): the complete recipe format specification. Draft v0.1 written and committed (`.claude/design/recipe_format_spec.md`, ST22 worked example `recipe_format_st22_draft.yaml`, review `recipe_format_review_2026-11-13.md`); Eve reviews and answers section 13 (14 points). Then the text moves to its homes (rule file with double confirmation, appendix, user docs). Issue #74.
- [ ] **RECIPE-TESTS-1** `[opus/high]` — Eve 2026-11-13 + ADR-099 16(c): tests first, one per rule of the check catalogue (spec section 8), per replacement (9) and per tolerated form (11), over every kind of recipe file (pipelines, templates, retest, transformer test recipes, gallery, legacy, writers, inline test recipes); shared `make_recipe` helper; adapt the tests that encode superseded behaviour first (`wrangling: []` valid, inline recipes without engines); each fails for the right reason on today's code (recorded). Includes TEST-SHAPES-1. Issue #75. Depends on RECIPE-SPEC-1.
- [ ] **RECIPE-MIGRATE-1** `[sonnet/medium]` (ST22 and Abromics descriptions `[opus/high]`) — Eve 2026-11-13: every recipe follows the format: ST22 first, then the other pipelines, templates, retest, the 68 transformer test recipes (flat form -> one data schema with `source`), the 34 gallery bundles (example variant), the 2 legacy files (keep or remove: Eve), the writers (Blueprint form, bootstrapper, scaffolder, `create_data_analysis_recipe.py`). Collection hashes must not change except the named tier-2 change; fragment comments kept (text-level edits, spec 5b). **Order for ST22 (Eve 2026-11-13: science errors must be fixed): RECIPE-ST22-FIX-1 (R1-R4, #67 #69 #70) first, then the format migration and the final descriptions.** The gallery keeps its own shape (spec 6.9). Issue #78. Depends on RECIPE-CHECKER (UNKNOWN-KEYS-1).
- [ ] **RECIPE-DOCS-1** `[sonnet/medium]` — Eve 2026-11-13: documentation and rule files follow the format (about 50 files mention `is_primary_key`, 32 `display_name`); rule files need Eve's double confirmation (diff first); ADR-099 16(g) sentence "unknown keys are warnings" corrected. Issue #79.
- [ ] **RECIPE-FORMULAS-1** `[opus/high]` — P9: formulas in recipes only from an allowed list of Polars operations, by function name, in `check_recipe` (check ST06); the list is derived from all recipes and approved by Eve before it is enforced. Issue #80.
- [ ] **RECIPE-AUDIT-REFRESH-1** `[sonnet/medium]` — Eve 2026-11-13 ("the audits are old"): the two recipe audits call `check_recipe` over every kind of recipe file (they pass 7 of 7 pipelines today while none has the engine keys); registry rows and `schedule_commands.md` updated. Issue #81. Depends on the checker.
- [ ] **ENTITY-DECL-1** `[sonnet/high]` — the recipe key `entity:` (`noun`, `plural`, `population`), 5a point 17: loader, validator (the population table must exist and carry the key), docs appendix, Blueprint form; unknown top-level keys **fail** (Eve 2026-11-13, not warn). Part of the checker, issue evezeyl/SPARMVET_VIZ#76. Stage 4.
- [ ] **RECIPE-FORMAT-1** `[opus/high]` — the recipe-format step, after UNKNOWN-KEYS-1 (otherwise new keys are ignored silently): required `data_engine` and `plot_engine` (5a point 21), `entity:` (ENTITY-DECL-1), the explicit optional T3 container at the plot entry, `is_primary_key` -> `is_entity_key` (**refuse at once**, Eve 2026-11-13; `legacy_keys.py` only names the replacement), a dataset's own tier-2 applied (RECIPE-DATASET-TIER2-1). The T3 container is in the schema now (Eve 2026-11-13). Sweep: every shipped recipe, template, gallery bundle, the Blueprint new-recipe form and navigator, `docs/appendix/data_analysis_recipe_structure.yaml`, `rules_data_analysis_recipe_structure.md` (double confirmation). Tests first. **Eve 2026-11-13: scope is every recipe, in the app and in tests (transformer test recipes included).** Split into RECIPE-SPEC-1, RECIPE-TESTS-1, UNKNOWN-KEYS-1 (checker, issue evezeyl/SPARMVET_VIZ#76), RECIPE-MIGRATE-1, RECIPE-DOCS-1.
- [ ] **KEYS-NODE-1** `[opus/high]` — stage 2, amends ADR-089 (Eve 2026-11-12): node keys for T1, T2, T3 (`hash(previous key, steps)`, an empty list keeps the previous key); the T1 key includes the collection (today one key for the whole recipe, verified by `tmpAI/architect/key_identity.py`); "affected" by content; the property tests listed in `home_audit_steps.md` 5a point 15. Tests first (TEST-ADAPT-1). Full model, inventory and open points: `.claude/design/home_evidence/home_hash_model_2026-11-12.md` (three families: identity hashes, node keys, content hash; retire the older `decision_hash`; the plot input key was never built; update `docs/foundations/reproducibility_hash_schema.qmd`).
- [ ] **TEST-SHAPES-1** `[opus/high]` — Eve 2026-11-12: the audit must work for any recipe. For every shipped recipe shape (`home_audit_steps.md` 5a point 18: joins with key, no joins, no key declared, another key name, no population table, long format, plotted table that is also an input) the recipe graph builds and a removal by key either applies or states why not; fixtures are the shipped recipes (`tmpAI/architect/recipe_shapes.py` is the scan). Written before the build (TEST-ADAPT-1). Part of RECIPE-TESTS-1, issue evezeyl/SPARMVET_VIZ#75.
- [ ] **RECIPE-DATASET-TIER2-1** `[opus/high]` — DECIDED by Eve 2026-11-12: every table has T1, T2, T3 with or without a join, T2 and T3 can be empty; a data schema plotted directly is a collection and its own tier-2 list is its T2 (today silently ignored, verified on `ResFinder` of `1_test_data_ST22_dummy`: `prepare_ingredient` runs tier1 only, `tier2_steps()` reads joins only). A tier-2 list on a dataset that is only an ingredient is a failure (`home_audit_steps.md` 5a point 19). Engine, graph, validator, tests first. Issue evezeyl/SPARMVET_VIZ#77; fix confirmed by Eve 2026-11-13 (the `amr_heatmap` changes: shown to her before and after for @verify).
- [ ] **AUDIT-RAWYAML-REMOVE-1** `[sonnet/medium]` — Eve 2026-11-12 (O3): remove the audit step type `developer_raw_yaml` (nothing creates it). Dependency sweep found it in `app/modules/exporter.py`, `app/modules/session_manager.py`, `app/handlers/audit_stack.py`, `app/handlers/export_handlers.py`, `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`, plus tests, the contract (`ui_implementation_contract.md` section 12), `rules_ui_dashboard.md`, ADR-093 mentions and the docs. Follow `rules_legacy_management.md` section 6 (marker, removal, tests, documentation sweep). Part of the audit build, after the step compiler.
- [ ] **UNKNOWN-KEYS-1** `[opus/high]` — Eve 2026-11-12: unknown keys must be reported. Verified (`tmpAI/architect/unknown_keys.py`): the validator reports nothing for an unknown top-level key, a typo key, unknown step parameters, or a forked T3 recipe (all 0 problems); plot-spec keys are dropped silently too (#66). Proposal: one schema of the allowed keys per level (top level, data schema, join, step lists with the parameters of each action from its `ui_schema`, plot entry, plot spec, `plot_defaults`, `info`, `entity`) in `libs/utils`; the validator reports unknown keys as warnings with a did-you-mean (never a block); the loader stays thin and only refuses retired or renamed keys (`legacy_keys.py`, existing). **Roles, to confirm with Eve:** one rule set `check_recipe(resolved recipe) -> problems with a severity` in `libs/utils`; the loader builds the recipe (parse, includes) and stops when the checks return errors; the validator reports every problem without running anything (HOME load gate, Blueprint, import screen); the data check (needs the data files) stays separate. Today the loader judges content (`config_loader.py` structural errors, retired keys) and the validator wraps the loader and adds id and step-list checks. Tests first (TEST-ADAPT-1). **UPDATE 2026-11-12 (Eve, 5a point 19):** fail instead of warn: in HOME the load gate rejects the recipe with the reason; in BLUEPRINT the problems are shown and never block building (empty placeholders accepted). Fails: a step list never applied, an unknown action, key or parameter, a column missing at that node (dry run on the column names), a step that fails on the data. A missing description stays an advice. One test recipe per failure. **UPDATE 2026-11-13 (Eve): unknown keys FAIL** (the sentence "reports unknown keys as warnings" above and ADR-099 16(g) are superseded: recipes can be verified first, in Blueprint); no backward-compatible default; old names refused at once, `legacy_keys.py` is kept only to suggest the replacement. Check catalogue: `.claude/design/recipe_format_spec.md` section 8. Issue evezeyl/SPARMVET_VIZ#76 (folds #66).
- [ ] **RECIPE-ST22-FIX-1** `[opus/high]` — apply R1-R4 (agreed by Eve 2026-11-12, `recipe_review_st22_2026-11-11.md` 3b) to the ST22 test recipe: `ST22_Anchor` without ResFinder, "none detected" explicit, descriptions with the grain and the treatment of missing values on every plotted table, the phenotype score without unknown, the MLST title with the years, the virulence tiles. Tests first, written to fail for the right reason (TEST-ADAPT-1); pictures checked. The entity declaration is decided (5a point 17); until ENTITY-DECL-1 is built the recipes carry descriptions only (the `entity:` key would be ignored). One problem at a time: R1 first. **2026-11-13:** descriptions for the tables as they are today are drafted in `.claude/design/recipe_format_st22_draft.yaml` with `REVISE` markers on the three tables and four plots that R1-R4 change; R1-R4 stay with issues #67, #69, #70.
- [ ] **DOC-RECIPE-PLACEMENT-1** `[opus/high]` — Eve 2026-11-12: guidelines for recipe authors on where to put what (a change that must reach everything goes early, at T1; an exclusion added late is likely one that was missed), in the recipe structure rules, the docs appendix and the help. Rule files need Eve's double confirmation.
- [ ] **TEST-ORDER-1** `[opus/high]` — Eve 2026-11-12: specific tests for step order: the order of steps is the order of the lineage; steps at one node commute only when row-local; the z-score canary (`QA_population_zscore`) must show that the order changes the result and that the recorded order is the one run; the exported recipe re-run equals the audit data. Written before the build (TEST-ADAPT-1).
- [ ] **TEST-ADAPT-1** `[opus/high]` — Eve's rule 2026-11-12 (ADR-099 point 16): before any build step, inventory the tests that encode superseded behaviour (My view, Compare, the propagation dialog, per-plot reach, filters that drop missing values) and adapt or replace them to the decided design; each new or adapted test must fail for the right reason on the current code before the code is written. No test is run as evidence before that.
- [ ] **RECIPE-GRAPH-UTILS-1** `[opus/high]` — stage 2: specification of `utils.recipe_graph` (nodes: datasets, T1, T2 and T3 nodes; edges; ID column present per node; plots per table; tables with the same T1 definition; the list of steps that summarise rows) and its tests; Blueprint's navigator is rebuilt on it (decided by Eve 2026-11-12: one source of truth; the graph also carries the include file of each node; the navigator tests are the regression oracle, adapted first; supersedes in part ADR-067/074).
- [ ] **NA-RULE-63** `[sonnet/high]` — Eve gave the rule 2026-11-12 (`home_audit_steps.md` section 19, "Meaning of the filters"): a missing value is a value; `!=` and none-of keep it, `==`, one-of and comparisons remove it, always counted and reported. Prerequisite of audit mode (the translated actions must do what the dialog says). `filter_ne` and `not_in` drop missing values today (verified); no shipped recipe uses them. Issue #63 WP3b was blocked on this rule: confirm with Eve, then unblock.
- [ ] **UML-HOME-REDRAW-1** `[opus/high]` — after the open review items are decided: redraw the HOME diagrams listed in `home_evidence/home_uml_review_2026-11-12.md` (3 contradicted, 8 partly outdated, 4 missing). Each UML edit needs Eve's OK; optional interim banner on the three contradicted diagrams. Run `assets/scripts/audit_uml_model.py` after each edit. The hash-model diagrams (`DM-KEYS` and its three details, and the changes to `STM-STAGE`, `HOME-AUDIT-CACHE`, `EXP-MODES`, `SEQ-EXPORT`) were done 2026-11-12.
- [ ] **TEST-FLAKY-1** `[sonnet/medium]` — #72: harden the browser tests (wait for connected and idle before selecting the recipe and check it took effect; poll the disk in the label test; stable grid read; server log in the failure output; `--durations`). Evidence in the forensics file, section 5.

### Manual-testing findings, 2026-11-10 (issues #53/#54/#55)

Eve's own first manual pass through Home/Blueprint/Export surfaced three real gaps code
reading alone had not caught. All three fixed same session; Home re-verification for
tomorrow's testing session is the remaining blocker.

- [x] **#55** `[sonnet/low]` — Test Lab right sidebar showed nothing. Confirmed deliberate
  since #42 (2026-11-08), documented then as "a separate, smaller finding, out of scope,"
  but never turned into its own issue. The content (`_render_test_lab_right_info()`,
  `home_theater.py`) already existed and was already correct — only
  `config/ui/sidebars/testlab_standard_right.yaml` was stale (`visible: false, panels: []`).
  Flipped to `visible: true, panels: [{type: test_lab_right_info}]`. `SidebarValidator`:
  0 violations across all 8 app features templates.
- [x] **#53** `[sonnet/low]` — "I think the external exchange landed in blueprint and not in
  home panel." Real cause found: Blueprint's left sidebar has a panel literally titled
  "External Exchange" (recipe YAML upload/replace/append/download) — generic enough that
  Eve reasonably looked there first for the new reproducibility-bundle import (#48), which
  correctly lives in Home's Export panel (confirmed in code: no actual sidebar-config
  overlap). Renamed the Blueprint panel to "Recipe File Exchange" with an explicit note
  pointing at Home's Export panel for bundles (`wrangle_studio.py`). Also gave Home's
  `import_bundle_upload` file control a visible label (was `None`) and a one-line reminder
  of the same distinction. Updated the two active docs that still said "External Exchange"
  (`docs/reference/ui_style_guide.qmd`, `.claude/design/ui_panel_map_current.md`); left
  historical log/archive hits untouched.
- [x] **#54** `[sonnet/low]` — reproducibility bundle Import appeared to do nothing. Root
  cause: "Also include a reproducibility/reimport bundle" is unchecked by default at export
  time; importing a Mode-1-only bundle correctly refuses (`BundleImportError`, the 4-leg
  comparison table only renders on success) but the refusal rendered as small grey/red text
  under a long accordion — easy to read as "the feature does nothing." Added a hint at the
  checkbox itself ("check this now if you'll want to Import this bundle later"), reworded the
  file-control's help text to lead with the same requirement, and turned the error state into
  a proper red alert box instead of `ui.tags.small`. **Open:** whether "comparison to what
  was before" means something beyond the 4-leg hash table (e.g. a diff view against the
  currently-open recipe) — needs Eve's clarification, not assumed.
- [x] **Validate-button rule drift** `[sonnet/low]` — see the correction note under
  `VALIDATE-UI-1` below; `_handle_validate` now also runs `validate_data_analysis_recipe()`
  (the real `ConfigManager` load path) and surfaces the `factory_id` check row the coherence
  script already computed but the UI silently dropped.

All four: headless suite (1589) and the full Playwright gate (`test_shiny_smoke` +
`test_shiny_smoke_blueprint` + `test_export_download` + `test_every_app_features_starts`,
64 passed/3 skipped) re-run clean after the changes.

**Follow-up, 2026-11-10 (same day, Eve: "I can't see the External Exchange HOME — where do
we import it?"):** the #54 fix above gave Import a visible label but left it buried below
~10 export-form fields and an `<hr>` inside a collapsed "Export" accordion — still not
findable. Restructured `system_tools_ui` (`export_handlers.py`): Import now gets its own
bold-headed block ("⬇ Import a bundle") at the *top* of the panel, before the export form
("⬆ Export" heading added there too); accordion panel renamed "Export" → "Export / Import"
(`home_theater.py`). Also found and fixed, while re-running the full Playwright gate twice
to confirm the restructure was clean: `TestRecipeSwitchRendering::test_first_plot_renders_without_a_click_after_recipe_switch`
(committed 2026-11-08, predates this session) restores the shared page to the ST22 dummy
recipe at the end but only waited for the "Quality Control" tab label — which
`1_Abromics_general_pipeline` (the recipe it switches away from) also has, so a later test
relying on `_load_data_analysis_recipe`'s shared-session shortcut could run against the
wrong recipe if the restore was still in flight. Reproduced twice in the full suite (not a
one-off: `TestPhase25Panels::test_info_panel_shows_the_info_block_of_the_open_data_analysis_recipe`
failed both times, asserting "ST22 Dummy Dataset" but getting "Abromics General Pipeline"'s
info block) — fixed by waiting for a plot sub-tab name unique to ST22 dummy instead of a
tab label both recipes share. Full `test_shiny_smoke.py` re-run clean twice after the fix
(33 passed, 3 skipped both times, ~110s each — also notably faster than the two failing
runs, which each spent a timeout window on the race). Headless suite (1589) still clean.

**Evening review pass, 2026-11-10 (Eve: "review the testing suite... UML review...
revise the home panel scripts... set up comments... maximize catching problems before
me"):**

1. **Live Playwright walkthrough with screenshots** (`tmpAI/home_review_2026-11-10/`,
   gitignored scratch) of everything touched today: Home Export/Import restructure,
   Blueprint "Recipe File Exchange" rename, Blueprint Validate's 3-check PASS result,
   Test Lab right sidebar. All confirmed visually correct — this is the check that
   should have caught #54 the first time (structural checks passed; only an actual
   screenshot would have shown it was still unfindable).
2. **Test suite review** — found 3 real gaps where "does the element exist" tests had
   passed even though the thing a human experiences was broken, each now closed with a
   mutation-tested regression test (verified fails on the bug, passes on the fix, no
   leftover mutation code): `test_import_a_bundle_block_is_findable_above_export_form`
   (pixel-position assertion, not just visibility — the exact #54 miss), `test_test_lab_right_sidebar_shows_the_tool_descriptions`
   (no test existed for the right sidebar at all — the exact #55 gap), `test_validate_runs_the_real_engine_load_check`
   (asserts the `recipe rules` check row specifically, not just any PASS/FAIL badge).
   `test_global_export_panel_visible` updated for the new panel name.
3. **UML sync** — found one real gap beyond the earlier commit's fixes: UI-TESTLAB
   wireframe had no right-sidebar panel at all (consistent with it never having been
   reachable before today), so issue #55 made the model stale the moment it shipped.
   Added a "Right sidebar: ..." panel to UI-TESTLAB (widened the frame 940→1250 to fit
   it), re-exported all 30 diagrams. **Found broken while re-exporting:**
   `staruml_export_diagrams` reports success for every diagram but silently does not
   write any file to the given folder (confirmed: unchanged mtimes after two calls) —
   worked around by copying the already-fetched live preview image directly for the one
   diagram that actually changed; the other 29 were already current from the prior
   commit's export, so this didn't block anything tonight, but the export tool itself is
   unreliable and worth fixing or replacing before it's next needed for a bigger batch.
   `audit_uml_model.py`: 0 violations throughout.
4. **Intent comments** — added a `VOCAB NOTE` / `GUARDED` comment convention (grep-able)
   at the 4 places changed today that carry a non-obvious naming or reachability
   discrepancy: `home_theater.py` `_render_export` (label "Export / Import" vs. panel
   type key staying `"export"`), `export_handlers.py` `system_tools_ui` (the
   import-above-export ordering + which test guards it), `home_theater.py`
   `_render_test_lab_right_info` (correct code ≠ reachable code — check the sidebar
   slot config too), `wrangle_studio.py` Recipe File Exchange panel (why it's a
   separate feature from HOME's bundle import, not a naming accident). Each cross-
   references the relevant UML element and/or regression test, not just the issue
   number, so a future reader can verify current reality against both without re-
   deriving the history.
5. **Recipe for tomorrow verified**: `validate_data_analysis_recipe` +
   `validate_data_analysis_recipe_data` on `1_test_data_ST22_dummy.yaml` — 0 problems
   both. Session ghost store checked (`tmp/UI_TEST/user/_sessions/`) — only 2 entries,
   both from today's own test/review runs, not accumulated clutter; nothing to clear.

Full re-verification after all of the above: headless (1589), full Playwright gate —
**67 passed** (64 + the 3 new tests), 3 skipped, no flakes. `.playwright-mcp/` (tool
scratch dir created by the live walkthrough) added to `.gitignore`.

### Reproducible export & import (ADR-097, 2026-11-09) — implementation order

Design locked (`ADR-097`, `.claude/design/reproducible_export_design.md`), tracked by #44 +
sub-issues #39/#45/#46/#47/#48, related #49/#50. Order below follows the dependency chain
worked out during design: seed/hash recording first (nothing else needs it to exist, but
everything else needs it to be correct), then the translator (the real engine-facing risk),
then the export/import surfaces that assume the translator works, then the smaller/independent
pieces last.

- [x] **REPRO-SEED-1** `[sonnet/medium]` (#39/4A, part 1) — DONE 2026-11-09: `random_state`
  added as a recognised `aesthetic_override` key in `resolve_plot_config()`
  (`libs/viz_factory/src/viz_factory/plot_config_resolver.py`) — injected into every
  jitter-capable layer the resolved plot has (`geom_jitter`, `position_jitter`,
  `position_jitterdodge`, or any layer with `params.position` of `"jitter"`/`"jitterdodge"`),
  overriding any recipe-set `random_state` on that layer; a no-op when the plot has no jitter
  at all. 8 new unit tests (`TestResolvePlotConfigL5RandomState`) plus a live end-to-end check
  (same override seed → identical jitter across renders; different seed → different jitter).
  Full viz_factory suite (246) and full headless suite (1494) pass, no regressions.
- [x] **REPRO-SEED-2** `[sonnet/medium]` (#39/4A, part 2) — DONE 2026-11-09: automatic seed
  bookkeeping for the default case (`random_state: random`, no pinned override). Per plot,
  `_effective_random_state` (`@reactive.Calc`, `home_theater.py`) returns a pinned T3 override
  unchanged or draws one fresh `secrets.randbits(31)` seed; a separate idempotency-guarded
  `@reactive.Effect` (`_persist_drawn_seed`) is the only thing that writes it into
  `last_drawn_seeds` (new per-session `reactive.Value({})`, threaded through `server.py` →
  `home_theater.py` → `export_handlers.py`) — never inside the `@render.plot` itself (R1). The
  render reads the same Calc, so what's shown and what's bookkept always agree. Skips plots
  with no jitter at all (`layers_have_jitter`, factored out of REPRO-SEED-1's resolver code for
  reuse here) — verified against the real shipped `phenotype_genome_length_dotplot.yaml` plot
  (inline `position: jitter`), not just synthetic test data. Non-blocking notification added in
  `export_bundle_download` when any exported plot's seed is unpinned. `test_render_purity.py`
  (44, R1 check), full headless suite (1498), and the `qa` Playwright smoke suite (29) all pass.
- [x] **REPRO-PROV-1** `[sonnet/medium]` (#39/4A, part 3) — DONE 2026-11-09: consolidated
  provenance record (`build_export_provenance()`, `export_handlers.py`) now carries all four
  hash legs. Recipe/data unchanged (already existed). Engine leg is environment-aware,
  detected automatically, never asked of the user: containerized (`/.dockerenv` or `container`
  env var) → `image_ref` from `SPARMVET_IMAGE_REF` if set, `"not set"` if not (never a false
  pin); source install → existing `git_commit` + `uv_lock_sha256` (checked directly: this
  project has no `uv.lock` committed yet — recorded as `None`, a documented limitation, not a
  silent gap). New `t3_audit_steps_sha256` leg: `canonical_hash()` (`cache_keys.py`, reused,
  not reinvented) over `{t3_audit_steps_by_plot, t3_plot_overrides}` — confirmed missing before
  this (grep found zero hits, despite the field being named in the original
  `ui_implementation_contract.md §12f` spec). Surfaced in the existing README.txt
  "Reproducibility" section and report.qmd's hash table — no new UI. 13 provenance tests (6
  new) + full headless suite (1504) + real-download Playwright suite (4) all pass.
- [x] **REPRO-RESTORE-HASH-1** `[sonnet/low]` (#50, the hash-check half only — labels/multi-dataset
  distinction is separate, lower-priority UI work, not ordered here) — DONE 2026-11-09:
  `write_t3_ghost()` (`session_manager.py`) now computes and stores `t3_audit_steps_sha256`
  (via `cache_keys.canonical_hash`, same shape as export's leg) on every save;
  `list_t3_ghosts()` surfaces it (`""` for ghosts written before this field existed — "nothing
  to check", never a fabricated mismatch). `_restore_session()` (`session_handlers.py`)
  recomputes the hash from the ghost's own content and compares to its own stored value — a
  **self-consistency** check (the ghost file was corrupted/hand-edited), not a
  comparison-against-current (there is no independent "current" T3 before restore replaces
  it). While here, also fixed a second, adjacent gap found by the same read: the
  `data_batch_hash` mismatch warning was specified (`ui_implementation_contract.md §12d`) but,
  like the T3 hash, never actually implemented — only the recipe-sha check existed. Both are
  now checked, same non-blocking severity. 11 new/changed tests (`test_session_manager.py`),
  full headless suite (1508), `qa` Playwright smoke suite (29) all pass.
- [x] **REPRO-TRANSLATOR-1** `[sonnet/high]` (#47/4D) — DONE 2026-11-09:
  `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`. Per plot, computes the full
  ordered translated-action sequence for that plot's `target_dataset` join (`exclusion_row`/
  `filter_row` → `filter_eq`/`filter_range`/`is_in` with the same eq/ne+list auto-promotion
  viz_factory applies at render time; `drop_column` → `drop_columns`; `aesthetic_override`
  skipped, not translated; `developer_raw_yaml` parsed and passed through after validating it's
  a list of canonical `action:` steps); forks the join under a plot-specific id in the returned
  copy only, appends the sequence after the join's existing `tier2:` steps (T2-then-T3,
  matching live behaviour; empty original `tier2` → fork's `tier2` is just the translated
  actions). Dedupes to a shared fork only when two plots' resulting sequences for the same join
  are byte-identical, computed independently per plot first — never grouped by propagation scope
  directly (ADR-097 decision 4; covered by dedicated multi-plot propagation tests). Marker
  convention decided: a structured `_t3_origin` dict key on the forked join (not a YAML
  comment) — round-trips through plain `yaml.safe_dump`/`safe_load`, directly machine-readable
  on read-back. **Engine-coverage gap found, not approximated:** no registered action exists
  for `ne`/strict `gt`/strict `lt`/`not_in` — filed as #52; a plot using one of these ops is
  named in the `skipped` return dict rather than silently exported as falsely reproducible.
  **A second real gap found and fixed:** `ConfigManager` injects an internal `plots:` mirror
  key into `raw_config` that breaks reload (`LEGACY-FLAT-PLOTS-1`) — confirmed live, now
  stripped unconditionally by `build_mode2_recipe()`. 40 unit tests
  (`test_t3_translator.py`) + verified live end-to-end against the real engine (not a mock):
  materialized the forked join's actual Tier 2 output via `DataOrchestrator` against the real
  shipped `2_test_data_ST22_dummy` recipe/data and confirmed it byte-identical to manually
  filtering the original join's Tier 1 the same way. Full headless suite (1548) passes.
  **Not yet done:** wiring this into the actual Mode 2 export (#45) or Import (#48) — this
  task built the translator itself, standalone and tested, not its integration.
- [x] **REPRO-EXPORT-MODES-1** `[sonnet/medium]` (#45/4B) — DONE 2026-11-09, **corrected once
  already** after Eve's review of the first pass (see ADR-097's implementation-status note for
  the full before/after). First pass kept Mode 1's recipe copy unchanged and invented a
  combined "Analysis ID" — both wrong. Corrected, settled design (confirmed against a native
  StarUML diagram, `docs/UML/app.mdj` HOME package, `EXP-MODES Export bundle contents by mode`,
  built live with her before the fix): **Mode 1 never includes the recipe or raw data** — only
  `report.qmd`, `plots/`, `README.txt`, `t3_steps.yaml`. **`effective_run.yaml` is written
  unconditionally, identical content either way**, at the bundle root — not scattered hash
  values restated as prose; this is the actual mechanism for proving two *separately* exported
  bundles correspond (diff it field by field — not eyeball, not one collapsed code, #48's job).
  **Mode 2** (opt-in checkbox, forces `export_scope: global`) adds the translator's frozen
  recipe (`data_analysis_recipes_reproducibility/<id>.yaml`) and the actual data files
  (`data_reproducibility/<dataset>.<ext>` — "needs all to be fully reproducible"); nothing
  Mode-2-only duplicates into Mode 1. `t3_translation_skipped` is a dict when Mode 2 ran, else
  an explicit "not attempted" string — never a fabricated empty dict implying nothing was
  skipped. README/report trimmed to point at `effective_run.yaml` instead of repeating the
  hash table. Playwright tests (real browser download, `qa`) updated/added: confirms Mode 1
  alone never has the recipe, `effective_run.yaml` is present either way with matching
  recipe/data hashes across both downloads, Mode 2 adds the recipe/data additively, the frozen
  recipe reloads cleanly (no leftover ConfigManager `plots:` key). Full `test_export_download.py`
  suite (5) and full headless suite (1548) pass.
- [x] **REPRO-SENSITIVE-1** `[haiku/low]` (#46/4C): DONE 2026-11-09. Non-blocking
  `_notify(..., type="warning", duration=12)` fired inside `export_bundle_download()`'s
  `if wants_mode2:` block, right after the raw data files are copied into
  `data_reproducibility/` — names that the bundle now carries the actual data and points at
  the user guide. New guidance added to `docs/user_guide/understanding_your_export.qmd`
  (section "Before you include your raw data"): anonymise before loading into the app, not at
  export time, and keep any de-anonymisation mapping file outside the SPARMVET_VIZ project
  folders entirely. While touching this area, also corrected now-stale claims left over from
  before REPRO-EXPORT-MODES-1/REPRO-SEED-2 in both `understanding_your_export.qmd` (three
  fingerprints → five fields of `effective_run.yaml`, added `t3_audit_steps_sha256` and
  `engine_fingerprint`/`git_commit` as comparison fields, added "Two things your export can
  be" explaining Mode 1 vs. the opt-in add-on) and `reproducible_plots.qmd` (it said SPARMVET
  "does not yet record" a drawn random seed and that reshuffling was "not available" — both
  now done by REPRO-SEED-2; rewrote the seed table and "Coming later" section accordingly).
  Depends on REPRO-EXPORT-MODES-1 (done).
- [x] **REPRO-IMPORT-1** `[sonnet/high]` (#48/4E): DONE 2026-11-09. New pure module
  `app/modules/bundle_importer.py` (`import_bundle`, `read_effective_run`, `ImportResult`,
  `LegResult`, `BundleImportError`) — a parallel importer, confirmed distinct from
  `SessionManager.export_session_zip`/`import_session_zip` (those only ever zip ghost metadata
  + source *paths*, never the recipe or data itself). File-based only (ADR-093): extracts
  `data_reproducibility/` into `raw_data_dir/_imported/<id>_imported_<timestamp>/`, repoints the
  frozen recipe's `data_schemas.*.source.path` at the extracted files, writes it into the real
  recipes directory, and writes a `SessionManager` assembly ghost under `_sessions/` — never
  touches a live `wrangle_studio`/`home_state` object. The imported recipe only becomes
  selectable after a reload (`Bootloader` resolves `available_data_analysis_recipes` once per
  process, ADR-094) — the UI and docs say so plainly rather than pretending otherwise. Four
  legs, non-blocking (`status`: `match`/`mismatch`/`not_checked`, never a refusal): **data**
  (always checkable — rehashes the bundle's own `data_reproducibility/` files against the
  recorded `data_batch_hash`); **engine** (this machine's `engine_fingerprint()`/`git_commit`
  vs. recorded — explains "software changed, not your analysis" per ADR-097 decision 3);
  **recipe** (only checkable, to avoid a guaranteed false mismatch, when the *original*
  untranslated recipe is found locally by id in `bootloader.available_data_analysis_recipes` —
  the frozen copy has T3 baked in by design and never hashes the same as the original);
  **t3_steps** (reported for reference, `not_checked` — no independent local source once T3
  only existed in the exporting session; compare two `effective_run.yaml` files instead).
  Found and fixed live, not just in review: calling `ConfigManager` (via
  `SessionManager.compute_data_analysis_recipe_sha256`) directly on an untrusted, just-written
  recipe would `sys.exit(1)` the whole Shiny process on a broken bundle (ADR-077's fail-fast
  behaviour, correct at app startup, fatal from inside a running request) — caught by the
  module's own headless test suite, fixed by gating with
  `data_analysis_recipe_validator.validate_data_analysis_recipe()` first (the same
  `SystemExit`-catching wrapper ADR-094's HOME load gate already uses) and raising
  `BundleImportError` instead. Wired into the Export panel (`export_handlers.py`'s
  `system_tools_ui`/new `import_bundle_report` output), gated on `export_enabled` alone —
  reachable without `test_lab_enabled` or `blueprint_enabled`, per the issue's done-when.
  `app/tests/test_bundle_importer.py` (16 tests, headless: writes a real tiny recipe, runs it
  through the real `build_mode2_recipe`, round-trips a hand-built bundle through
  `import_bundle`, covers every leg's match/mismatch/not_checked path, source repointing, the
  `SystemExit`-safety fix, and skipped-T3-plot passthrough). `test_export_download.py` gained
  `test_import_a_bundle_reports_the_four_legs` (real browser: ticks the reproducibility
  checkbox, downloads a real Mode 2 bundle, uploads it back through `#import_bundle_upload`,
  asserts the rendered report; cleans up the real recipe/data files it writes into the
  project tree in a `finally` block — confirmed by checking `git status` before/after, since
  Import's whole point is writing outside `tmp_path`). Full suites green: headless 1566
  (`libs app/tests`, up from 1548), Playwright `test_export_download.py` 6/6 and
  `test_shiny_smoke.py` 34 passed/3 skipped. Docs: `understanding_your_export.qmd` gained
  "Importing someone else's reproducibility bundle".
- [x] **ACTIONS-FILTER-GAPS-1** `[sonnet/medium]` (#52): DONE 2026-11-09. Closed the
  engine-coverage gap REPRO-TRANSLATOR-1 found and refused to approximate: no registered
  action existed for `ne`, strict `gt`/`lt`, or `not_in`. Added `filter_ne`, `filter_gt`,
  `filter_lt` (`libs/transformer/src/transformer/actions/cleaning/core.py`, next to
  `filter_eq`/`filter_range`, same silent-no-op-on-missing-params idiom) and `not_in`
  (`cleaning/analytical.py`, next to `is_in`, same `TransformationError`-on-missing-params
  idiom) — all four follow the existing pattern exactly, including `ui_schema` for the
  BLUEPRINT form catalog. `t3_translator.py`'s `_TRANSLATABLE_OPS` extended from
  `{eq, ge, le, in}` to all eight T3 filter ops (`eq, ne, gt, ge, lt, le, in, not_in`,
  `ui_implementation_contract.md §8`'s full op list); `translate_t3_node()` maps each to
  its action. The `ne`-with-list-value case, previously asserted to still raise, now
  correctly promotes to `not_in` and translates. Kept one defensive
  "unrecognised op still raises, never approximates" test (`op: "regex"`, not a real T3
  op) since every real op is now translatable — the two downstream tests that had used
  `op: "ne"` as their "this op is untranslatable" example were switched to the same bogus
  op, since `ne` no longer demonstrates that. Updated the authoritative action list
  (`rules_agent_role_bioscientist.md §8`). New `libs/transformer/tests/test_filter_actions.py`
  (11 tests, includes an is_in/not_in exact-complement check). `test_t3_translator.py`
  rewritten for all 8 ops (52 tests total, up from 40). Full headless suite 1578 passed
  (up from 1566).
- [x] **REPRO-SESSION-LABELS-1** `[sonnet/low]` (#50, the UI half): DONE 2026-11-09. Found a
  real bug while implementing, not just adding UI: `set_session_label`/`get_session_label`
  only ever read/wrote the most-recent T3 ghost — a brand-new session (`assembly.json` only,
  before any Apply) had no T3 ghost yet, so it silently could not be labelled at all.
  Canonical storage moved to `assembly.json` (`write_assembly_ghost` gained a `label: str |
  None = None` param — `None`, every real caller's default, preserves whatever label is
  already on disk across a recipe/data-change rewrite rather than wiping it; an explicit
  string sets/clears it). `get_session_label` falls back to the legacy T3-ghost location for
  sessions labelled before this fix. `list_all_sessions()` now returns `label` directly (no
  extra per-card lookup). UI: the static italic label text in `session_handlers.py`'s session
  card replaced with `ui.input_text(..., update_on="blur")` — no separate Save button. The
  scanning `@reactive.Effect` (same one restore/delete already use) saves only when the
  blurred value differs from the STORED label (R3 idempotent guard,
  `ui_implementation_contract.md §14`) — without it, any unrelated session action anywhere
  would re-fire this effect and re-write every label to its current box value on every pass.
  Deliberately does not bump `_session_list_version` on save: nothing else in the panel reads
  the label, and forcing a re-render would reset any *other* session's box mid-edit (R4).
  Distinguishing sessions of the same recipe against different data batches (the second
  done-when) is served by the same free-text label, since a hash prefix alone isn't
  meaningfully distinguishable to a user. 8 new headless tests
  (`app/tests/test_session_manager.py`, including the before-any-T3-ghost case and the
  reassembly-preserves-label case) + 1 new Playwright test
  (`test_shiny_smoke.py::TestSessionListRefresh::test_session_label_saves_on_blur`, fills,
  tabs to blur, asserts the backend actually stored it). Full suites green: headless 1583
  (up from 1578).
- [x] **REPRO-RESHUFFLE-1** `[sonnet/medium]` (#49): DONE 2026-11-09. "🔀 Reshuffle
  arrangement" button (`app/handlers/home_theater.py`, `_make_plot_cell_handler`'s
  `_plot_reshuffle_ui`/`_handle_reshuffle`, registered per known plot id — not a scan over
  dynamic ids, plot ids are known upfront from the recipe) next to the plot badge, its own
  narrow output — never a revival of the Plot Style panel (stays unmounted, fork issue #15,
  `ui_implementation_contract.md §12g.9`). Visibility (new `recipe_pins_random_state()`,
  `libs/viz_factory/src/viz_factory/plot_config_resolver.py`, next to `layers_have_jitter`):
  hidden unless the plot has a jitter-capable layer AND neither the recipe itself (a fixed
  `random_state` number in the layer's own params) nor a T3 override has already pinned a
  seed. Click → draws `secrets.randbits(31)` and writes it into
  `home_state['t3_plot_overrides'][subtab]['random_state']` (an `@reactive.Effect`, R2) — the
  existing `_effective_random_state` Calc (REPRO-SEED-2) picks it up on its own, no new
  render-side plumbing needed, and the button then hides itself (nothing left to reshuffle
  from until the pin is removed some other way — no unpin control, not asked for). Found and
  fixed two real bugs via the Playwright test, not just in review: (1) the output wrapper's
  id and the button's own id were both `plot_reshuffle_{p_id}` — an invalid DOM id collision
  that made every selector match two elements; split into `plot_reshuffle_{p_id}` (wrapper)
  and `plot_reshuffle_btn_{p_id}` (button). (2) The visibility render wrapped its
  `home_state.get()` read in `reactive.isolate()` (copied from `_plot_cell_ui`'s *different*
  use of isolate, for collapse state) — this silently prevented the button from ever
  reacting to its own pin, so it never hid itself after a click; removed the isolate, this
  render must react to `home_state`. Checked against `COM-REACTIVE Reactive wiring of HOME`
  (`docs/UML/app.mdj`) before skipping a UML update: the diagram tracks
  `home_state → plot_group of each plot` at the whole-plot-cell granularity, already covers
  this addition, no new box needed. 6 new headless tests
  (`libs/viz_factory/tests/test_plot_config_resolver.py::TestRecipePinsRandomState`) + 3 new
  Playwright tests (`test_shiny_smoke.py::TestReshuffleControl`: shown when meaningful, absent
  on a non-jitter plot, click pins and hides). Docs: `reproducible_plots.qmd`'s "Coming
  later" section and `reproducibility_same_input_same_output.qmd`'s open question both
  updated — this was the feature either one described as not yet built. Full suites green:
  headless 1589 (up from 1583).

### Audit Fixes — ADR Compliance (ADR behavioural audit 2026-11-06)

- [x] **ADR-045-PLOTERR-1** `[AUDIT]` `[sonnet/low]`: `architect_active_plot` (`@render.plot`, `app/modules/wrangle_studio.py` lines 552-607) calls `_plot_error.set(...)` six times. This breaks the reactive write rule R1 (`ui_implementation_contract.md §14`): renders are read-only. Fix: compute the error text in a `@reactive.Calc` (or write it from a `@reactive.Effect` with an idempotent guard) and let the render only read it. Affects BLUEPRINT (demo scope). Add a Playwright or unit check that the Blueprint plot still shows its error banner. DONE 2026-11-06: the error text is computed in the `_plot_outcome` Calc; `app/tests/test_render_purity.py` fails if any render in `app/` writes a reactive value. The error banner itself is not covered by an automated test (check by hand in BLUEPRINT).
- [x] **ADR-045-SERVER-SIZE-1** `[AUDIT]` `[sonnet/medium]`: `app/src/server.py` has 287 lines; `rules_app_structure.md §3` sets a hard limit of ~250. Find what is not shared state, a shared calc or a `define_server` call, and move it to a handler or module. DONE 2026-11-06: the excess was dead code (`tier_reference`, `tier3_leaf`, `apply_tier2_transforms` and the unmounted outputs `plot_reference`, `table_reference`, `plot_leaf`, `table_leaf`, `handle_plot_brush`), removed; `server.py` is 237 lines.

### Clean-up recheck 2026-11-06 (dead code, old tests, documentation)

Done 2026-11-06: removed `lookup.py` (`lookup_anchor_rows`), `DataWrangler.run_tier1/run_tier2`, `peek_data_analysis_recipe`, the `placeholder/` folders of `ingestion` and `transformer`, unused imports, `test_reactive_shell.py`, the app features benchmark scripts, and the broken `test_lab` demos (`debug_sdk`, `debug_ambiguity`, `debug_reconciler`, `demo_reconciler`; covered by `libs/id_reconciliation/tests`, `test_synthesizer`, `test_bootstrapper`, new `test_extractor`). Repaired `debug_pipeline_connector.py`, `debug_pipeline.py` + `PipelineExecutor` (tiered data analysis recipes, `join_id`), `libs/viz_gallery/tests/debug_gallery_submission.py`. The `generator_utils` name is gone from deployments and docs. Headless baseline: 1197 passed.

- [ ] **LEGACY-MATERIALIZE-SHIM-REMOVE-1** `[haiku/low]`: `assets/scripts/materialize_data_analysis_recipe_plots.py` is a thin forwarding shim to `libs/viz_factory/tests/debug_gallery.py`, marked "DEPRECATED SHIM" in its own docstring/`@deps` since before this audit but with no removal task (found 2026-11-07, DOC-RECHECK-2, `rules_legacy_management.md §4` — "a deprecation with no removal task is forbidden"). Still referenced by 6 doc files (`docs/appendix/FAQ.qmd`, `running_helper_scripts.qmd`, `docs/workflows/visualisation_factory.qmd`, `libs/viz_factory/README.md`, `assets/scripts/README.md`, plus two `.claude/tasks/` records) — check none of them need the shim for a still-valid reason before deleting; update each to the canonical `debug_gallery.py` command and delete the shim.
- [x] **DEAD-CODE-REVIEW-1** `[sonnet/medium]` (done 2026-11-07, re-verified every item by grep, not relying on the 2026-11-06 scan): dependency sweep per `rules_legacy_management.md` §6 for each item.
  **Deleted (confirmed zero real callers anywhere, including tests):**
  - `app/modules/wrangle_studio.py` `_fields_table` (a "backward compat" alias with no caller) and `_parse_fields_safe` (a complete method, but superseded — `_fields_cards`, the one actually used, reimplements the same dict/list normalisation inline with the *opposite* legacy-format convention; `_parse_fields_safe` was never wired to anything).
  - `libs/ingestion/src/ingestion/ingestor.py` `validate_schema` — unused AND incomplete (`# For now, simply confirming we can read the raw columns. Strict validation... will occur here.` — never finished, never called).
  - `libs/connector/src/connector/galaxy_connector.py` — a **second, different** `GalaxyConnector` class (BioBlend-based, not the real `galaxy.py` GxIT wrapper `__init__.py` actually exports). A 37-line mock stub (`bioblend` isn't even installed; its own `@deps consumed_by:` claim of `connector/__init__.py`/`bootloader.py` was false, same false-claim pattern as the `adapter_*.py` files deleted for F-12). Deleted the whole file.
  Verified: `from app.src.server import server` clean, `libs/connector/tests` (27), `libs/ingestion`+`app/tests` headless (510), full headless suite (1444), Blueprint Playwright suite (12) all pass. `build_dep_graph.py` rerun.
  **Kept, unused but not dead** (complete, correct, zero cost to leave; deleting would remove sanctioned infrastructure nobody has adopted yet, not fix anything): `bootloader.py` `get_python_path()` (recommended by `audit_hardcoded_config.py`'s own warning text as the replacement for hardcoded `python3`, just not yet adopted anywhere), `libs/utils/src/utils/debug_output.py` `get_debug_out_dir()` (implements the `tmpAI/YYYY-MM-DD/[label]/` convention of `rules_verification_testing.md §6`, no debug script uses the helper yet), `libs/id_reconciliation/.../core.py` `suggest_patterns` and `libs/viz_gallery/.../gallery_manager.py` `list_submissions` (thin, correct, documented public methods on classes whose *other* methods — `precheck_compatibility`/`reconcile`, `rebuild_index`/`submit_example` — are actively used; `rebuild_index` itself turned out NOT dead, see F-18).
  **Already tracked elsewhere, no new action:** `app/modules/help_registry.py` (whole module unused) and `app/modules/exporter.py` (`bundle_package`, `render_audit_report`, imported only by tests) → `HELP-FROM-DOCS-1` (F-20). `app/modules/gallery_viewer.py` `submission_modal_ui`, `autofill_meta_from_audit` (gallery submission, unwired) → noted in `docs/UML/risks_and_technical_debt.md` (F-18). `libs/blueprint_arch/.../agent_adapter.py` etc. are **not dead** — ADR-076's `claude_cli` backend is wired and working; `claude_api`/`local` are the deliberate Phase-2 gap tracked at `CONFIG-AGENT-BACKENDS-1` and `BLUEPRINT-AGENT-API-1`.
  **Needs Eve's call, moved to Needs Discussion (not deleted — real, substantial work, just incomplete):**
  - `app/handlers/blueprint_handlers.py:203 _undo()` — the undo *capture* side (`_snapshot_state`, the 20-step deque, draft persistence/restore) is fully wired and working; the *restore* side (`_undo()` itself, which pops the deque and calls `wrangle_studio.logic_stack.set(...)`) has zero callers — no "Undo" button exists anywhere in the UI. BP-UNDO-1 (`rules_ui_dashboard.md §7`) was half-built. See `UNDO-WIRE-1` below.
  - `app/src/render/pipeline_error_renderers.py` (whole module: `dispatch_pipeline_error` + 5 surface renderers, ADR-079) — zero importers anywhere, but this is not simple dead code: `PipelineError` itself IS actively raised in 7 production files (`data_assembler.py`, `data_wrangler.py`, `ingestor.py`, `viz_factory.py`, `audit_stack.py`, `blueprint_handlers.py`) and nothing anywhere catches it — no `except PipelineError` exists in `app/`. The structured 5-surface rendering design (plot overlay, toast, audit panel row, data-import banner, Blueprint inline) was built and unit-tested on the producer side (`make_render_payload`, tested in isolation) but the consumer/dispatch side was never wired to any of those 7 raise points. See `PIPELINE-ERROR-WIRE-1` below.
- [ ] **UNDO-WIRE-1** `[sonnet/medium]`: wire `app/handlers/blueprint_handlers.py`'s `_undo()` to a real "Undo" button in the BLUEPRINT IDE (found while resolving `DEAD-CODE-REVIEW-1`). The capture/persist side (20-step deque, draft save/restore) already works; only the trigger is missing. Needs Eve's call on where the button goes (toolbar? keyboard shortcut?) and whether it should also need the standard audit/reason gate or not (it reverts `logic_stack`, not T3 audit nodes, so probably not).
- [x] **PIPELINE-ERROR-WIRE-1** `[opus/medium]` (decided 2026-11-08, Eve: wire it, not remove it — ADR-094). While wiring this, found the catch side was not pure zero: `home_theater.py`'s VizFactory render path (line ~475, `DIAG-RUNTIME-AUDIT-1`) already captured failures into `session_pipeline_errors`, and `audit_stack.py`'s `pipeline_issues_ui` already rendered them in the right sidebar — just with a hand-rolled dict shape, not `PipelineError`/`make_render_payload`/`dispatch_pipeline_error`, and only for that one catch point. Extended the same pattern to the data-materialization catch point (`_resolve_active_lf` failures in `_group_plot_handler`) — now PipelineError-aware (uses `.component`/`.problem`/`.fix`/`.who` when the caught exception is one). `app/src/render/pipeline_error_renderers.py`'s renderers (`dispatch_pipeline_error` etc.) are still not called by anything — the existing capture path renders its dict shape directly in `pipeline_issues_ui` rather than through them; reconciling the two is part of the remaining scope. See `PIPELINE-ERROR-WIRE-2` for what's left: the other 5 retrofit targets (VizFactory render failures beyond the existing capture, T3 Apply, Blueprint inline, Data Import panel) and reconciling the renderer module with the dict-shape capture already in use.
- [x] **PIPELINE-ERROR-WIRE-2** `[opus/medium]` (closed 2026-11-08, ADR-095). **(b) Blueprint inline done first** (Eve: "if it is built then it should be wired... the detection and guidance text need to reach the screen"): all 3 `blueprint_handlers.py` catch points now call `make_render_payload()` and render inline via `render_blueprint_inline()` (extended to include `fix_md`, which it previously omitted). **Then, finishing (b)'s other three targets, found a bigger problem:** every one of the 24 `PipelineError` construction sites across `ingestor.py`/`data_assembler.py`/`data_wrangler.py`/`viz_factory.py` built a rich `PipelineError`, printed it, then discarded it for a plain `SPARMVET_Error` carrying only message+tip — ADR-079's own `to_pipeline_error()` adapter was never implemented anywhere, so the `isinstance(e, PipelineError)` check added earlier today could never actually fire for a real library error. Fixed at the root (ADR-095): `errors.py`'s `SPARMVET_Error` now carries the original `PipelineError` via an optional kwarg (no breaking change), all 19 raising sites updated, new shared `capture_entry()` helper replaces the broken isinstance check everywhere. VizFactory ("beyond the one existing catch point" = `_cmp_baseline_handler`, the Comparison Mode twin, found with its data-materialization capture missing entirely) and T3 Apply (two silent `PipelineError`s found along the way: the gatekeeper-blocked message, now showing the fix text though the path is effectively unreachable since `btn_apply` is HTML-disabled while blocked; `_write_t3_ghost`'s failure, now a real reachable fix — ghost save failing silently meant T3 state lost on refresh with zero warning) are closed. Export's per-plot error stub also enriched. (a) Data Import panel target turned out to be based on an imprecise premise — real `IngestionError` already flows through the HOME data-materialization path already fixed; no separate catch point existed to wire. (c)/(d) unchanged from the 2026-11-08 earlier note: export report.qmd section already done; T3 Ghost `pipeline_errors:` list still not done. Proven: new unit tests in `test_pipeline_error.py` (carry-through + `capture_entry`) and `test_write_t3_ghost_warning.py`, both mutation-proven; headless suite 1459; full Playwright suite (HOME/Blueprint/export/every-app-features) run clean.
  **Still open, new scope from this pass:** `PIPELINE-WARNING-SURFACE-1` (4 non-raising "warning" PipelineError sites in ingestor.py/viz_factory.py print to console only — needs a return-value/callback mechanism, not an exception catch, since nothing raises); deciding whether `dispatch_pipeline_error()`'s surface renderers should replace the dict-capture pattern now used everywhere, or be reconciled to it; T3 Ghost `pipeline_errors:` list extension (ADR-079 Phase 3).
- [ ] **GALLERY-SUBMIT-SCHEMA-1** `[sonnet/low]` (found 2026-11-08, incidentally, during the library-README audit — not a doc issue): `libs/viz_gallery/src/viz_gallery/gallery_manager.py::submit_example()` writes gallery-bundle `data_analysis_recipe.yaml` files with a root-level `plots:` key (fatal `ConfigurationError` per LEGACY-FLAT-PLOTS-1, `rules_data_analysis_recipe_structure.md §8`) and a `wrangling: {tier1, tier2, tier3: example}` block (`tier3` is not a valid wrangling-tier key — only `tier1`/`tier2` exist, `rules_data_engine.md §3`). Any recipe this function generates would be rejected by the engine. Not yet reproduced live or confirmed as still-reachable code (README audit found it by reading the function, not by running it) — verify first, then fix the generated shape to `analysis_groups:`/`tier1`+`tier2` only.
- [ ] **PIPELINE-WARNING-SURFACE-1** `[sonnet/medium]`: the 4 `severity="warning"` `PipelineError` constructions that never raise (`ingestor.py` ×2 incl. the documented "Silent Skip Warning", `viz_factory.py` ×2) print to console and nowhere else — found while closing `PIPELINE-ERROR-WIRE-2` (ADR-095 §7, deliberately scoped out). No exception to catch, so `capture_entry()`'s pattern doesn't apply; needs `DataIngestor.ingest()`/`VizFactory.render()` to return or collect warnings instead, then a caller to surface them (likely `data_import_panel` / `notification` surfaces per their own `surface=` field). Needs a design pass on the return-value shape before implementing — not a quick fix.
- [x] **PROCESSING-ISSUES-RENAME-1** `[sonnet/medium]` (done 2026-11-08, finding F-26, `.claude/tasks/uml_findings.md`): `audit_stack.py`'s `pipeline_issues_ui` was built but never mounted in the DOM (traced to the original commit, predates this session). Renamed throughout — `pipeline_issues_ui` → `processing_issues_ui`, `session_pipeline_errors` → `session_processing_issues`, the `id="pipeline_issues_panel"` DOM id, the inner "Runtime issues" heading, every `@deps` block, ADR-079/ADR-094/ADR-095 text, `cross_cutting_concepts.md`, `data_contract_and_failures.md`, `project_conventions.md`, `report.qmd`'s section title, README.txt's count-line text — to resolve the collision with `CTX-1`'s "Analysis pipeline" C4 actor (external upstream Abromics/VIGAS-P system, a different thing from this app's own internal processing). Mounted on the **left** sidebar, not the right, per `.claude/design/ui_reachability_map.md` (new, this session): new `processing_issues` panel type in `sidebar_registry.py` (`gate_flag: None`), added to the shared `home_standard_left.yaml` used by all 8 app features files. Verified: app import clean, `test_shiny_smoke.py` (21 passed), `test_every_app_features_starts.py` with a new permanent regression assertion that the output is mounted in every app features (9 passed), mutation-tested (removed the slot, confirmed `pipeline-static` fails with the expected message, restored, confirmed it passes).
- [x] **DOC-RECHECK-2** `[sonnet/medium]` (done 2026-11-07, all 7 points checked):
  1. "Comparison Theater" → ADR-086 terms ("Compare Result vs My view" / "Comparison Mode") in `docs/index.qmd`, `docs/workflows/visualisation_factory.qmd`, `docs/reference/ui_style_guide.qmd`. `Terminology.qmd` never had the term (checked, clean) — also fixed a real bug there while at it: it described "Wrangle Studio" as "available within the Test Lab", which is wrong — Blueprint Architect and Test Lab are separate, independently-gated user spaces. The 3 links to the archived `docs/appendix/data_lifecycle_theater.qmd` redirected to its stated replacement, `docs/user_guide/audit_pipeline.qmd` (the archived file's own banner names it; left the archived file untouched, it's already correctly marked HISTORICAL).
  2. `docs/vision/platform_evolution.qmd`'s Figshare example used the old `joins: - anchor:/join: [...]` shorthand (forbidden since rules §7). Corrected to the real, canonical `action: join` / `right_ingredient:` / quoted `'on':` syntax actually used in `config/data_analysis_recipes/pipelines/figshare_integration/wrangling/figshare_triple_join_steps.yaml` (this gallery example is real and shipped, not hypothetical).
  3. `.claude/design/ui_panel_map_current.md` — one-line fix, "Global Export accordion" → "Export accordion (renamed... 2026-05-04)". `export_specification.md` — added a proper `**Status:** IMPLEMENTED` banner (was still "AGREED — pending implementation" despite the design being fully live); noted `single_graph_export_handlers.py` was deleted outright, not "merged" as the spec's own §8 implied.
  4. `project_conventions.md` §E corrected: L1-L4 of the plot config cascade are implemented (checked `resolve_plot_config()` is wired into `viz_factory.py`); only L5 (T3 `aesthetic_override`) remains open, matching `rules_viz_factory.md §7`'s per-task ✓/open status. Also fixed two adjacent stale "to be created" file-registry rows for files that already exist (`plot_config_resolver.py`, `pipeline_error.py`), and a wrong path (`viz_factory.py` missing its package directory).
  5. DOC-GAP-2/3/5 (May) are untraceable — no definition found anywhere outside this one line. Spot-checked their described content directly instead: README.md has no `ExcelHandler`/"Comparison Theater" claims (already clean), the ADR-074 Programmatic Lineage API section of the deployment guide matches the real public API (`rules_app_structure.md §4`). Nothing to fix.
  6. `docs/_freeze/` is git-ignored (`.gitignore:27`) — confirmed "ignore" is correct, not tracked so nothing to re-render for a commit.
  7. Ran the three `rules_legacy_management.md §5` audit greps. Check 1 (unmarked deprecated-sounding prose) is mostly past-tense documentation, not actionable — spot-checked the highest-signal hits. Check 2 found one genuine violation: `assets/scripts/materialize_data_analysis_recipe_plots.py`, marked "DEPRECATED SHIM" in its own docstring with no linked task — added a proper banner and opened `LEGACY-MATERIALIZE-SHIM-REMOVE-1`. The `architecture_decisions.md:58` hit is an ADR entry correctly pointing to its own superseding ADR (ADR-032) — that's the ADR log's built-in convention, not a violation. Check 3 (tombstone expiry) found nothing past its stated phase.
- [x] **AUDIT-GATE-UI-1** `[sonnet/medium]` (done 2026-11-07): `app/tests/test_shiny_smoke.py::TestAuditGate::test_unreasoned_node_blocks_apply_then_reason_unblocks_it` — switches to My view (T3), adds a filter row, sends it to audit (accepting the default propagation scope), asserts `#btn_apply` reads "Apply ⛔" and is disabled, fills the `t3_reason_*` input, asserts it flips to "Apply" and enabled. Proven by mutation: stubbing `gatekeeper_blocked()` to always return `[]` makes the test fail on the first assertion (button shows "Apply", not "Apply ⛔"); restoring it passes along with the rest of the smoke suite (21/21, +3 skipped).
- [x] **VALIDATE-UI-1** `[sonnet/medium]` (done 2026-11-08): issue #26. `validate_data_analysis_recipe_data()` (issue #18) was written and tested but called from nowhere in the running app — the one wired button, BP-VALIDATE-1, explicitly skipped it (`--skip-tsv`). Found while writing up the "process of failures" for Eve and confirmed against `rules_agent_role_bioscientist.md`'s own "Silent Skip Warning": a mismatched `input_fields`/`output_fields` column name was silently skipped with zero warning anywhere in the app. `_handle_validate` (`blueprint_handlers.py`) now runs both checks and merges them: structure (existing subprocess) + data-vs-contract (now wired), shown as a fifth check row plus a detail list (location, problem, "did you mean" tip) for any data-contract problem. Proven by mutation: disabling the new `checks.append` call makes `test_validate_runs_the_data_contract_check` fail (assertion on the "data vs contract" row text); restoring it, that test plus the full Blueprint Playwright suite (14/14) and the headless suite (1444) pass. **Not done:** auto-run on data analysis recipe upload (the structure subprocess check alone can take up to 30s — auto-firing it on every upload is a separate UX/perf decision, not bundled into this fix).
  **Correction, 2026-11-10 (issue #53):** this entry's "structure (existing subprocess)" phrase masked a real gap — the "structure" check was *only* `audit_data_analysis_recipe_coherence.py`, a hand-rolled static script that never calls `ConfigManager`. `validate_data_analysis_recipe()` (the function `VALIDATE-UI-1` names in its own id and that HOME's load gate, ADR-094, uses) was **never actually called from Validate** until now. This meant Validate could PASS a recipe with `id:` != file name (ADR-092) or a flat (non-tiered) wrangling list (LEGACY-FLAT-WRANGLING-1) — both hard rejections at real load time — because neither check path the button ran touches the real engine. Found via Eve's manual testing ("ensure it checks the recipe according to the latest rules... to ensure it does not validate something not working"). Fixed: `_handle_validate` now runs three checks (engine load via `validate_data_analysis_recipe`, the static coherence script, data-vs-contract), none superseding the others. Also fixed a second, smaller gap found while re-reading: the coherence script already computed and reported `factory_id_violations` (deprecated key, ADR-083) in its markdown output and in `overall_pass`, but the Blueprint UI's `_count()` calls never surfaced it as its own check row — added.

### Export consistency (the export holds the Result plus the audited steps; exploration is never exported), added 2026-11-06

Done 2026-11-06 (issue #10): export reads T1 and T2 through the key-checked orchestrator, renders plots from T2 (as HOME), records data analysis recipe file-set hash, data hash and the Tier 1/Tier 2 keys in README, `report.qmd` and PNG/SVG metadata. Headless tests: `app/tests/test_export_provenance.py`, `app/tests/test_tier2_store.py`.

- [ ] **EXPORT-CHECK-1** `[sonnet/medium]`: Export test by hand in the app. Automated since 2026-11-06 (`app/tests/test_export_download.py`, real download in the qa app features): keys recorded in README (points 3), data files exist, no `_ERROR.txt`, no My view content on Result (7 partly), export refused after a data change. Still by hand: points 1, 2 (compare with the screen), 4-6, 8, 9. What to look for, with the data analysis recipe and a data analysis recipe with a `tier2` step:
  1. Plot in the bundle equals the plot in HOME "Result (T2)": same rows, same picture. With a `tier2` step the bundle plot must NOT look like T1.
  2. `data/<ds>/T1_data.tsv` equals the Raw view; `T2_data.tsv` exists only when the join has `tier2` steps and equals the Result view (row count, columns).
  3. README and `report.qmd` show: data analysis recipe SHA256 (file set), data batch hash, `tier1_key` and `tier2_key` per dataset ("none (T2 equals T1)" when no tier2). The PNG metadata has `sparmvet:tier1_key` / `tier2_key`.
  4. Same keys as the stored parquet files (`sparmvet_tier1_key`, `sparmvet_tier2_key` in the metadata of `anchors/*.parquet`).
  5. Change one thing and export again: a Tier 2 step (only tier2_key changes, plot changes), an included file (tier1_key and data analysis recipe hash change), a data file (data hash and tier1_key change). Nothing exported may come from before the change.
  6. Move a step from tier2 to tier1, export: no `T2_data.tsv`, no `anchors/<ds>__T2.parquet` left.
  7. Exploration filters (Apply, not sent to audit): never in the bundle, from any view; audited steps: always (see RT-15 to RT-17).
  8. App features without `interactivity_enabled` (pipeline-static): export works and shows the Result.
  9. Edge: join with no tier2 steps; data analysis recipe with two datasets (each its own keys); a failing plot writes an `_ERROR.txt` and the other plots are still exported.
- [x] **EXPORT-KEYCHECK-1** `[opus/high]` (done 2026-11-06, Eve: block, never better safe than sorry): the export compares the keys the open view was built on with the keys now. If the data analysis recipe (any file) or the data changed, nothing is exported: an error notification explains it and the download holds only `EXPORT_NOT_CREATED.txt` (what it means, reload with F5, check, export again, both sets of keys). Tests: `test_export_view_consistency.py`, `test_export_download.py`.
- [x] **EXPORT-T3-1** `[sonnet/medium]` (done 2026-11-06, corrected after Eve's clarification, issue #25): build rule T3 > T2 > T1 (stored Tier 2, which is Tier 1 without tier2 steps). The export is the Result plus the AUDITED T3 steps (rows, drops, aesthetic overrides, trail), always applied to the exported plot and its data; exploration (filters tried in T1/T2/My view, not sent to audit) is a sandbox and is never exported, from any view (no checkbox, no `FILTERS.txt`). T3 data is one file per plot with audited steps (`T3_data_<plot>.tsv`), built by `audited_frame`. `tier3_leaf` is gone (ADR-045-SERVER-SIZE-1). Still open: a hash of the audit steps in the report.

- [x] **EXPORT-T3-UX-1** (decided 2026-11-06, Eve): no message about left-out T3 steps is needed, because audited steps are never left out. What is not audited is a sandbox: a reminder says so (Export panel, and under the filter buttons in My view). Done in issue #25.

### Configuration vocabulary and launch variables (ADR-091, proposed 2026-11-07, revised: one pass, no hybrid)

Names agreed: `deployment` (`SPARMVET_DEPLOYMENT`), `app features` (`SPARMVET_APP_FEATURES`), `data analysis recipe` (`SPARMVET_DATA_ANALYSIS_RECIPE`, today still called data analysis recipe). "App features" is retired for the application; it stays only for the two AI agent files. Everything with an old word (folders, files, classes, keys, labels, docs, tests) is renamed in ONE scripted run; a hybrid state must not reach a shared branch. Issue: evezeyl/SPARMVET_VIZ#27 (IRIDA check: #28). Implementation plan: `.claude/outdated/tasks/config_rename_strategy.md`.

- [x] **CONFIG-VOCAB-REVIEW-1** (done 2026-11-07, decisions in ADR-091) `[opus/high]`: Eve reviews ADR-091 and the issue draft and decides open points 1 to 5 of the ADR (key renames, launcher, operator lock, "agent role" wording, IRIDA check). Issue #27 is created.
- [x] **CONFIG-INVENTORY-1** (done 2026-11-07) `[sonnet/medium]`: read-only inventory of every key in `config/deployment/*` and `config/app_features/*` (used / unused / wrong home, with the line that reads it), output in `.claude/logs/`; Eve reviews. Depends: CONFIG-VOCAB-REVIEW-1.
- [x] **CONFIG-MAPPING-1** (done 2026-11-07, rules and table in assets/scripts/rename_vocabulary*) `[sonnet/high]`: script output of every word, path and key containing app features, data analysis recipe or step list, with meaning and new name; Eve approves. Depends: CONFIG-INVENTORY-1.
- [x] **CONFIG-RENAME-1** (done on branch rename/config-vocabulary 2026-11-07, merge after the retest) `[sonnet/high]`: dry run, real run with `git mv`, startup errors for old variables and keys, `default_data_analysis_recipe` takes effect, `~` and `${VAR}` expansion, delete `logic_access`, `app_features_name`, `data_import_panel_visible` (absorbs LEGACY-DATAIMPORT-FLAG-1), migration script for files and sessions, old-words audit added to the audit registry, docs and launch commands updated. Depends: CONFIG-MAPPING-1.
- [x] **CONFIG-PROJECT-WORD-1** (done 2026-11-07) audit:allow-old-word (issue evezeyl/SPARMVET_VIZ#29, mapping in `.claude/outdated/tasks/project_word_mapping.md`) `[sonnet/high]`: one name for the recipe, no "project" for it; Info panel shows `info:`; remove recipe `type:`; "Deployment palette"; `standalone` -> `standalone`; rewrite Terminology.qmd. Gate: retest of #27 done or folded in.
- [x] **CONFIG-BLUEPRINT-FLAG-1** (done 2026-11-07, ADR-092, issue evezeyl/SPARMVET_VIZ#30) `[sonnet/high]`: `blueprint_enabled` alone controls the Blueprint Architect; `developer_mode_enabled` and `wrangle_studio_enabled` retired; blank page of standalone and advanced fixed.
- [x] **CONFIG-DATA-ANALYSIS-RECIPE-ID-1** (done 2026-11-07, ADR-092, issue evezeyl/SPARMVET_VIZ#31) `[sonnet/medium]`: the `id:` key equals the file name; validator, test, rule, files corrected.
- [ ] **CONFIG-PIPELINE-RENAME-1** `[sonnet/high]` (Eve, 2026-11-08, found live while testing — a miss from the CONFIG-RENAME-1/ADR-091 pass): the three `pipeline-*` app features names (`pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`) collide with the project's other, established meaning of "pipeline" — `CTX-1`'s "Analysis pipeline" external actor (the upstream bioinformatics system, e.g. Galaxy/IRIDA, that produces the data files). These three names actually mean "this deployment receives data pushed by an automated pipeline," which is a different thing — same shape of collision as the "Pipeline Issues" panel rename this session (F-26). Scoped as **Phase 2** (deployment-limitations testing), not mid-HOME-testing: touches 3 app features filenames, `rules_app_features_flags.md`'s full matrix, every launch command referencing them, deployment configs, docs, and `test_plan_2026-06.md` §2's CFG section. Needs a name decision first (e.g. `auto-static`/`auto-exploration-simple`/`auto-exploration-advanced`, or `fed-*`, or something naming the "data pushed automatically" property without using "pipeline") before any rename executes.
- [x] **CONFIG-TESTLAB-DATA-ANALYSIS-RECIPE-CHOICE-1** (done 2026-11-07/08, issue evezeyl/SPARMVET_VIZ#33, closed) `[sonnet/medium]`: Test Lab's sidebar branch fixed (was falling through to Home's full panel set); Alerts moved to the left sidebar for Gallery/Blueprint/Test Lab; Test Lab got its own `test_lab_info` placeholder panel. The open question this entry used to track — migrate Gallery/Blueprint's sidebars onto the registry, or correct the yamls to admit they're bypassed — is decided: **migrate for real**. Eve, 2026-11-08, after walking through the tradeoffs: "makes it more separation of concerns and that means its the good choice." Tracked as its own issue, not re-opening #33: **issue evezeyl/SPARMVET_VIZ#42**.
- [x] **SIDEBAR-UNIFY-1** (done 2026-11-08/09, issue evezeyl/SPARMVET_VIZ#42, closed) `[sonnet/high]`: unified left AND right sidebar construction for all 4 workspaces through the slot registry. Phase 1: Gallery left (`gallery_main` freestanding panel). Phase 2: Blueprint left (~140 lines moved into `WrangleStudio.build_sidebar_ui()`, `blueprint_main` freestanding panel). Phase 3: right sidebar, all 4 workspaces (`_build_right_sidebar` + `_right_panel_renderers`; Blueprint decomposed into 5 real panels — found `blueprint_standard_right.yaml` had the exact same bypass-plus-stale-yaml bug as the left side, undetected until this phase). Phase 4: docs (`ui_implementation_contract.md §11d/e`, ADR-073 second amendment, `uml_findings.md` F-01), `PANEL_REGISTRY` cleanup (3 dead entries removed), `@deps`/dep-graph. Phase 5: full regression sweep — headless (1478), Playwright (49 + 9 every-app-features), strict validator, `audit_uml_model.py`, all clean; grep-confirmed zero hardcoded sidebar-construction branches remain in either `sidebar_tools_ui()` or `right_sidebar_content_ui()`. One new regression test closed a real coverage gap found along the way (`test_blueprint_right_sidebar_shows_its_panels` — nothing previously checked that panel's content). Every new wiring mutation-tested. Done overnight while Eve rested, one commit per phase, no behavior change anywhere.
- [x] **CONFIG-BLUEPRINT-ID-DISPLAY-1** (done 2026-11-07, issue evezeyl/SPARMVET_VIZ#34) `[sonnet/low]`: the Blueprint selector ("Master data analysis recipe") listed file paths while the Home selector already listed ids. Both `_init_wrangle_data_analysis_recipes()` and the "create new" refresh in `blueprint_handlers.py` now build `choices` as `{path: id}` (id = `Path(p).stem`, per ADR-092 "id equals file name") instead of a flat path list — the option value is still the path, only the visible label changed. Proven by mutation: reverting to the flat-list form makes the new Playwright test `test_data_analysis_recipe_selector_shows_id_not_path` fail with the full path visible; restoring it passes (13/13 Blueprint suite green).
- [x] **CONFIG-AUDIT-FIXES-1** (done 2026-11-07, steps 1 to 7, issue evezeyl/SPARMVET_VIZ#32) `[sonnet/medium]`: plan in `.claude/tasks/audit_findings_2026-11-07.md` (the failures of the scheduled audits that the rename did not cause: missing `@deps` block, placeholder paths in docs, stale Violet Law references, missing `rules_toolchain.md`, `complex_template` that does not load, no load test of templates).
- [ ] **DEPS-REVIEW-1** (issue evezeyl/SPARMVET_VIZ#35) `[opus/medium]`: 61 outdated packages, 11 major (polars 1.40 to 2.1, pyarrow 24 to 26, pillow 12 to 13 ...) from `audit_package_deps.py`. Polars 2 first: ADR-035 parity audit of `libs/transformer/src/transformer/actions/`, run the full suites on a branch, then the others.
- [x] **ADR-037-GAP-1** (done 2026-11-07, finding F-21, `.claude/tasks/uml_findings.md`; found by `assets/scripts/audit_uml_model.py`'s first run) `[sonnet/low]`: "ADR-037" was cited in 4 places for the Gallery index-only-filtering rule with no `## ADR-037` heading ever written (git history traces the dangling citation to commit `cdb2b7a`, 2026-04-19). Wrote the missing entry from the already-consistent citing text.
- [x] **CONFIG-GHOST-DOC-1** (done 2026-11-07: user_preferences.qmd describes the event-driven saving) `[sonnet/low]`: `docs/workflows/user_preferences.qmd` (Quarto page) promises a debounced autosave every 2 minutes (`ghost_save_trigger`) that was never built; the saving is event-driven (Apply, leaving Home, assembly). Correct the page, delete `ghost_save.frequency_minutes`. Part of the docs phase.
- [ ] **CONFIG-AGENT-BACKENDS-1** `[opus/medium]`: implement the `claude_api` and `local` backends of the BLUEPRINT agent (ADR-076 phase 2); until then `blueprint_agent.model`, `.endpoint`, `.api_key_env`, `.gallery_awareness` stay in the templates marked "reserved, not implemented".
- [x] **CONFIG-SETTINGS-CLEAN-1** (done 2026-11-07) `[haiku/low]`: remove the stale allow-list entries (old commands and paths) from `.claude/settings.json`; review the diff.
- [ ] **CONFIG-STEPS-WRITE-1** `[sonnet/high]`: BLUEPRINT writes into the step lists location while the deployment guide says it is read-only, and overwrites files in place. Interim: warning and timestamped backup before overwriting. Target: BLUEPRINT edits a draft copy in `user_data`, validation (#26) runs on it, an explicit publish copies it into the step lists location; the location can stay read-only in production. See ADR-091 gaps. Depends: #26.
- [ ] **CONFIG-APP-RESOURCES-1** `[opus/high]`: application resources (app features folder, `theme.css`, sidebars, development fallback) are found relative to the working directory; locate them from the code root so a container or an installed copy works. Design first, see ADR-091 gaps. Depends: CONFIG-RENAME-1 (new folder names).
- [x] **CONFIG-BRANDING-1** (done 2026-11-07 (branding block in the deployment file)) `[sonnet/medium]`: move `theme_css` and the banner (`logo_url`, title) from the app features files to a `branding:` block in the deployment file; the base stylesheet always loads from the code root and the deployment stylesheet holds only the differences. Behaviour phase of the rename (phase 9), with an error for the old keys.
- [ ] **CONFIG-CACHE-LOCATION-1** `[sonnet/high]`: the deployment location `cache` (formerly `curated_data`, documented as the place of the Tier 1 and Tier 2 parquet caches) is required by the bootloader but read by no code; the anchors are written under `user_data/anchors/` instead. Decide: use `cache` for the anchors (cache is rebuildable, user data is work) or drop the location. Found in phase 5 of the rename. BLUEPRINT drafts already live in `user_data/_blueprint_drafts` (see CONFIG-STEPS-WRITE-1).
- [ ] **CONFIG-IRIDA-CHECK-1** (evezeyl/SPARMVET_VIZ#28) `[opus/medium]`: check ADR-048's IRIDA token assumption with someone who knows IRIDA before the IRIDA connector is built.

### LAB-WORKFLOW follow-up

- [x] **LAB-WORKFLOW-QMD-1** `[sonnet/low]` `[doc-sync]` (done 2026-11-07): `docs/workflows/developer_workflow.qmd` — the four-stage producer journey (TEST_LAB prepare/scaffold → GALLERY inspiration → BLUEPRINT build → HOME run), recommended (never enforced) orderings, the export-then-choose linking model, and why cross-space handoffs stay file-based (independent app features flags). Links back to `.claude/design/developer_workflow.md` for the full design record rather than duplicating it, per `rules_documentation_aesthetics.md §4`. Added to `docs/_quarto.yml` Chapter 2 nav, between `workflows/wrangling.qmd` and `user_guide/system_transparency.qmd`. Verified: `check_doc_links.py` clean, `quarto render --no-execute` builds without error.

### Maps — Solution A (choropleth via geom_polygon, no new deps)

> Design context: `.claude/design/maps_advanced_geo.md` (Solution B is the deferred geopandas path; A is this).
> Key fact (verified 2026-05-22): `geom_polygon`, `coord_equal`, `coord_fixed` are **already registered** in VizFactory. Solution A needs **no new viz component and no new dependency** — geometry is plain x/y/group numeric columns flowing through the existing tabular pipeline. ggplot2 analogue: `geom_polygon(aes(long, lat, group)) + map_data()`.

- [ ] **MAP-A-BOUNDARY-ASSET-1** `[sonnet/medium]`: Boundary-fortification asset script `assets/scripts/fortify_boundaries.py`. Pure-Python (json module only — **no geopandas/shapely**) GeoJSON → long-format Parquet with columns `region_id, region_name, poly_group, vertex_order, long, lat` (one row per polygon vertex; `poly_group` disambiguates multi-part regions and holes). `argparse` CLI per `rules_asset_scripts.md §2` (input GeoJSON path, output Parquet path, region-name property key — no hardcoded paths). Output to `assets/geo_boundaries/`.
  - Sub-step: source first boundary sets (Norway counties + Europe countries) from a public-domain provider (Natural Earth — public domain; **avoid GADM**, non-redistributable). Record provenance + licence in `assets/geo_boundaries/PROVENANCE.md`.
  - Verify: fortified Parquet round-trips to a plottable frame; vertex counts plausible; multi-part regions keep distinct `poly_group`.
- [ ] **MAP-A-DATA-ANALYSIS-RECIPE-PATTERN-1** `[sonnet/medium]`: Author one end-to-end choropleth data analysis recipe as the canonical pattern. Tier 1 join: analytical data (rate/count per region) → boundary Parquet on region key. Plot spec: `geom_polygon` with `mapping: {x: long, y: lat, group: poly_group, fill: <metric>}` + `coord_equal` + a continuous fill scale. Verify via `debug_assembler.py` then `debug_gallery.py`; route evidence to `tmp/<date>/<lineage_id>/` per `rules_agent_role_bioscientist.md §7`. Halt for `@verify`.
  - Watch: `group` must be the vertex `poly_group` (not region) or polygons cross-link; fill is per-region so the join must broadcast the metric to every vertex row.
- [ ] **MAP-A-GALLERY-1** `[sonnet/medium]`: Gallery bundle for the choropleth (Scientific Triplet + preview PNG per `rules_gallery_standards.md`). **Blocked on a taxonomy decision** (shared with Solution B open-question #3): choropleth `family` — extend `TAXONOMY_CHEATSHEET.md` with a spatial value, or fold into `Comparison`/`Distribution`? Resolve with Eve before authoring the `info:` block.
- [ ] **MAP-A-DOCS-1** `[haiku/low]` `[doc-sync]`: Document the choropleth pattern — `libs/viz_factory/README.md` (geom_polygon-as-map step list) + `docs/appendix/data_analysis_recipe_structure.yaml` (boundary-join + geom_polygon spec). DRY: link the design doc, do not duplicate.

> **Do NOT** uncomment `geom_map` at `geoms/core.py:822` for Solution A — that geom belongs to Solution B (needs the geo extra + a render branch; see design doc §11). Registering it now would expose a geom that errors on use.


---

## 🤔 Needs Discussion / Decision

### HOME audit redesign (ADR-099, issues #60, #64): waiting for Eve's decisions

Read `.claude/design/home_audit_reading_guide.md` (section 3 lists the 13 questions). No code before the answers. Build order when
decided: `home_audit_steps.md` section 20 (D14).

- [ ] **AUDIT-DECIDE-1** `[opus/high]` — Eve answers the questions of the reading guide section 3 (stage and reach, NA default, reason categories, caption, key source, reach selector, audit table selector, trial computation, event log, lineage map, guard-rail list, D1-D14, legacy names); then redraw `HOME-AUDIT-LINEAGE` and `HOME-AUDIT-EFFECT`, update ADR-099, write the build plan.
- [ ] **AUDIT-REPLACE-1** `[sonnet/medium]` — tracking item so nothing becomes orphaned: when audit mode is built, replace (do not leave behind) My view, Compare and "Plot to show" in the strip, the propagation dialog, per-plot `t3_audit_steps_by_plot` (old sessions map to plot-level steps), the pending badge / filter inventory / Apply gate of the right panel, and update `UC-HOME`, `SEQ-AUDIT`, `COM-REACTIVE`, `C4-COMP-HOME`, `UI-HOME as built today`, the amendment notes in ADR-024, 044, 049, 085, 086, 089, 097, 098, the contract and the help. Depends: AUDIT-DECIDE-1.
- [ ] **AUDIT-USABILITY-1** `[sonnet/low]` — before the dialog wording is final: 2-3 scientists who did not write the design use it on the ST22 recipe, thinking aloud (persona 5 of `design_review_personas.md`). Depends: dialog built.

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **TEST-INGESTION-1** `[sonnet/medium]`: `libs/ingestion/tests/` has zero pytest-discoverable tests — only `debug_ingestor.py` (an argparse CLI debugger, not pytest-named) and `ingestion_integrity_suite.py`. `pytest libs` silently runs nothing for this library; every other lib has real `test_*.py` files (found while resolving finding F-11, `.claude/tasks/uml_findings.md`). Needs a design pass on what `IngestorFactory`/`ConfigManager` test coverage should look like before writing it — not a quick fix.
- [ ] **STM-NODE** `[sonnet/medium]`: T3 audit node "Disable" (Power icon / `active: false`) is designed in `ui_implementation_contract.md` §1/§12c but never implemented — `audit_stack.py` reads `node.get("active", True)` for strikethrough styling and `export_handlers.py` filters on it, but nothing in the running app ever sets it to `False`; deletion is real list removal instead (found while resolving finding F-07, `.claude/tasks/uml_findings.md`). Decide: (a) build the Power-icon toggle so strikethrough/deactivate becomes real, matching the designed Export warning + Appendix behaviour, or (b) drop the dead `active` read/filter code and the unreachable Export-warning/Appendix text, keeping only real deletion. Needs Eve's call — changes user-facing audit UX either way.

- [ ] **UML-FAQ-DIAGRAMS-1** `[opus/medium]` (Eve, conversation preserved from `issue-drafts/tmp.md`, 2026-11-08): wants a new UML section — a "FAQ"-style set of diagrams, more human-oriented than the existing packages, for explaining the app to colleagues. First candidate: a simple bubble-style diagram answering "what does maximizing efficiency actually mean" — light Shiny (keep reactivity thin), send computation to Polars not the UI layer, don't recompute when nothing changed (the fingerprint/cache-key check). If possible, link it to the real architecture diagrams (SEQ-OPEN already covers the mechanism precisely but reads as too technical/developer-facing for this purpose, per Eve: "a bit outside of the architecture and more for me to explain to my colleagues"). Needs a design pass: where does this package live in `app.mdj` (new top-level package, e.g. "FAQ" or "Explainers", separate from HOME/GALLERY/BLUEPRINT/TEST_LAB/Structure/Requirements/Behaviour/Data and configuration/Architecture), what diagram type fits a "bubble" visual (UML doesn't have a native bubble/mindmap type — closest options are a heavily-simplified Use Case diagram reusing ellipses non-technically, or a plain image/graphic embedded as a diagram asset), and how it links back to the technical diagrams (StarUML hyperlink tag, or just a caption cross-reference in the Quarto embed).
- [ ] **UML-MAIN-EMPTY-1** `[haiku/low]`: the top-level `Model` package's own diagram ("Main", `UMLClassDiagram`) has zero elements — it has been empty since the project was first inspected this session (confirmed again 2026-11-08). Eve asked: "should it contain something?" Needs her decision: delete the diagram (if `Model` is just a container with no content of its own, which matches the current structure — HOME/GALLERY/BLUEPRINT/TEST_LAB/Structure/etc. are themselves top-level packages, not children of `Model`), or give it a real purpose (e.g. a project-wide index/legend diagram, a C4 System Context pointer, or move it under `UML-FAQ-DIAGRAMS-1`'s new package as a landing page).
- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Gallery keyword enrichment + AND/OR search. **Design settled (2026-05-22):** add `keywords: [list]` to `info:` block in each `data_analysis_recipe.yaml` (35 examples); update `refresh_gallery.py` to include keywords in `gallery_index.json` pivot entries; add a text search input to the Gallery UI (split on spaces → AND-intersect tokens across keywords + existing taxonomy fields). Three keyword layers: (1) statistical/methodological synonyms (`median`, `quartile`, `IQR`, `spread`, `beeswarm`, `ridge`, `dumbbell`, `before after`, `cumulative`, `paired`, `stacked`, `proportional`, `small multiples`, `faceted`, `overlay`, `individual points`, `raw data`, `regression`, `fit`, `confidence interval`…); (2) data/use-case terms (`time series`, `temporal`, `longitudinal`, `rate`, `prevalence`, `incidence`, `frequency`, `quality control`, `normality`, `heterogeneity`, `exploration`…); (3) domain terms (`AMR`, `antimicrobial`, `resistance`, `MIC`, `susceptibility`, `surveillance`, `epidemiology`, `pathogen`, `species comparison`…). No fuzzy matching needed — AND/OR on exact tokens is sufficient for this gallery size. Step 1: enrich all 35 example `info:` blocks. Step 2: one-line `refresh_gallery.py` change. Step 3: gallery UI search widget.

---

## ⏳ Deferred / Blocked

### Deferred by architecture choice (NOT hard library blocks — premises corrected 2026-05-22)

- [ ] **VIZ-GEOM-MAP-1** `[opus/high]` `[deferred — architecture choice, NOT a library block]`: Register `geom_map` (Solution B — real geo). Premise corrected 2026-05-22: plotnine 0.15.4 **does** ship `geom_map` (`REQUIRED_AES={'geometry'}`); not blocked by the library. Deferred because it needs geopandas/shapely + a geometry-aware data path. Full design: `.claude/design/maps_advanced_geo.md` (recommended sub-option B1 = sidecar GeoDataFrame merged at render time). Choropleths ship sooner via Solution A (`MAP-A-*`, Do Now) with zero new deps. Do not uncomment `geoms/core.py:822` until this is scheduled.
- [ ] **GALLERY-MAP** `[opus/high]` `[deferred]`: Map chart types in Gallery. Solution A choropleths arrive via `MAP-A-GALLERY-1`; advanced (projected/CRS) maps wait on VIZ-GEOM-MAP-1 / Solution B.
- [ ] **GALLERY-FLOW** `[opus/high]` `[deferred — needs layout-precompute helper, NOT a hard library block]`: Flow / network chart types. Premise corrected 2026-05-22: same pattern as maps — plotnine has no high-level `geom_sankey`/`geom_net`, but the **primitives exist and are registered** (`geom_segment`, `geom_path`, `geom_polygon`, `geom_rect`, `geom_ribbon`). Feasible by precomputing layout/flow coordinates into a tabular form, then drawing with existing geoms. Needs: (1) a layout/coordinate-precompute helper (network: node x/y + edge endpoints; Sankey: stage rects + ribbon polygon vertices via pure-Python sigmoid interpolation), (2) a decision on whether to add `networkx` (NOT installed) for graph layout or hand-roll with `scipy` (installed). Note: `geom_curve` is **absent** in plotnine 0.15.4 (use `geom_segment`/`geom_path`); `matplotlib.sankey.Sankey` exists but draws its own figure and breaks the grammar-of-graphics model (escape-hatch only, not preferred). Needs own design pass + ADR before scheduling.

### Blocked by other tasks

- [ ] **EXPORT-TUBEMAP** `[sonnet/high]`: Embed static tube map SVG in global export Quarto report. Requires headless render path for `BlueprintMapper.generate_cy_elements()`. Blocked by Blueprint Architect stability + headless Cytoscape.js SVG capability.

### Blocked until live app testing is finished (TOOLS / UML chain, added 2026-11-04)

Goal: this repo is self-contained. Every tool the agent needs to build the app is declared in the repo (not only in Eve's global `~/.claude/` setup), and architecture diagrams (UML / SysML / C4) live in the repo and are visible in the GitHub docs. Do ONE task at a time, in order; each ends with a halt for Eve. Eve's learning context: `my-mentoring` competencies DES-02..04 (offer Eve to draw parts herself).

- [x] **TOOLS-TOOLCHAIN-1** (done 2026-11-07: `.claude/rules/rules_toolchain.md`, linked from CLAUDE.md 3.2 and the master index) `[sonnet/low]`: Create `.claude/rules/rules_toolchain.md` = tools needed to build SPARMVET_VIZ (uv, `./.venv`, pytest, Playwright, Quarto, Mermaid CLI, podman/docker, git/gh, StarUML marked "pending TOOLS-UML-1"), with what each is for and how to call it. Link it from `CLAUDE.md` section 3.2 (rules table) and `workspace_standard.md` master index. Must not depend on `~/.claude/CLAUDE.md` or `my-mentoring/toolbox.md` (collaborators and CI do not have them). Personal tools (Gmail, Zotero, YouTrack, bio-research plugin) stay out. Done when: a fresh clone's agent can list the build tools from repo files alone.
- [x] **TOOLS-UML-1** (done 2026-11-07: shared tool in `OBSWORK/_bin/staruml/`, MCP servers `staruml` and `staruml-bridge` at user scope, not per repo) `[sonnet/medium]`: StarUML MCP setup. Depends on `[@user] TOOLS-UML-0` (licence decided and StarUML installed). Add repo `.mcp.json` entry for the StarUML MCP server, add `mcp__staruml__*` permissions to `.claude/settings.json`, update `rules_toolchain.md` (remove "pending"). Check first: StarUML >= 7.0.0 and Node >= 22 (Node 25 is installed); which MCP package is the official one (`staruml-mcp-server` listing vs community `staruml-mcp`); transport (stdio vs HTTP). Done when: agent can create one test element in a running StarUML and Eve sees it.
- [ ] **DEMO-USERS-1** `[sonnet/medium]`: functionality demo for users, most of them not developers (Eve, 2026-11-07; work on it after the fixes). Show the interface and what they can do: get the graphs, filter data, navigate the plots of one data analysis recipe, select another data analysis recipe and see the UI build itself. Briefly show what can be switched on and off: (1) fully static with a custom logo (`pipeline-static` plus a deployment with branding), (2) possibly a pipeline with some data exploration (`pipeline-exploration-simple`), (3) everything else, audit and so on, with the full configuration Eve uses for development (`developer`). A separate short demo for interested developers is possible. Check first that each of the three starts with the logo and data wanted.
- [ ] **DOCKER-RELEASE-1** `[sonnet/medium]`: later (Eve, 2026-11-07). There has been no Docker release yet. `assets/containers/Dockerfile` uses Python 3.12 while development is on 3.14 (finding F-19). Build and run the image, rootless, and add it to DEP-APP when it works.
- [ ] **HELP-FROM-DOCS-1** `[sonnet/medium]`: later (Eve, 2026-11-07). The help is not built yet; it is to be built from the documentation (there was an earlier discussion, find it first). `app/modules/help_registry.py` is imported by nothing today (finding F-20): wire it in or remove it as part of this.
- [ ] **HELP-CONTENT-REFRESH-1** `[haiku/low]` `[doc-sync]` (found live by Eve, 2026-11-08, HOM-55 in `test_plan_home_2026-11.md`): all 4 of `app/src/help/*.md` (the `? Help` modal's quick-reference content, HELP-INLINE-1 — separate, simpler mechanism from `HELP-FROM-DOCS-1` above) are stale. `home.md` describes the pre-ADR-086 tier toggle (superseded by HOM-45's Plot-to-show/Data-to-show strip, months ago). `gallery.md` actively describes **"Send to Blueprint,"** removed this session (ADR-093) — actively misleading, not just outdated. `blueprint.md`/`test_lab.md` use pre-rename "pipeline" vocabulary; `test_lab.md` lists only 4 of the 8 real tools (missing Reformatter, ID Reconciliation, Scaffolding, Anonymiser). Rewrite all 4 to match current reality.
- [ ] **DOC-TIER-PROSE-REFRESH-1** `[haiku/low]` `[doc-sync]` (found 2026-11-08, ADR-096 work — replacing the 4 broken Mermaid diagrams with UML embeds surfaced this, didn't fix it): the **prose** around `docs/foundations/data_tiering_adr.qmd` and `docs/appendix/data_lifecycle_theater.qmd` is stale independent of their (now-fixed) diagrams — module names like `Summarizer (performance/aggregation.py)` and `Anchor (persistence/anchor.py)` don't match current code (`DataOrchestrator`/`DataAssembler`), and `data_lifecycle_theater.qmd`'s own "Tier 3 / Active Pane" terms predate ADR-085/086's "My view" naming. The two pages also substantially duplicate each other (same 3-tier concept, two different cooking-metaphor write-ups) — `rules_documentation_aesthetics.md`'s DRY rule says pick one. Rewrite the prose, and decide whether to merge the two pages or keep them distinct with a clear reason why.
- [ ] **SECURITY-DEPLOY-1** `[opus/high]`: think through security before official deployment (Eve, 2026-11-07). Start from: `eval` on data analysis recipe text (finding F-13, `expressions.py:221`, `geoms/core.py:1335`, `id_reconciliation/core.py:239`), no login in the app, session zip import, which paths a user can write, rootless container. Eve's starting point: who launches the app controls the paths, and a rootless container limits the damage. To check: on a shared server the browser user is not the person who launched it, and a data analysis recipe upload or BLUEPRINT would run code as the app's account, with access to all mounted data. Done when: a written threat model and a decision per point.
- [ ] **TOOLS-UML-4** `[sonnet/medium]`: replace the Mermaid diagrams in the 8 `docs/` pages by StarUML images, and change the Mermaid line of `rules_documentation_aesthetics.md`. After the licence is bought (the trial puts a watermark on images). Decided by Eve 2026-11-07.
- [ ] **TOOLS-UML-2** (decided in `.claude/design/uml_model_plan.md` D1: all in StarUML, `docs/UML/app.mdj`; write it into the rules with TOOLS-UML-4) `[sonnet/low]`: Diagram location policy. Decide and write into `rules_documentation_aesthetics.md`: `.staruml` source files and exports (SVG, PNG) under `docs/` (suggest `docs/diagrams/`), exports referenced from the `.qmd` docs so GitHub shows them (GitHub does not render `.staruml`); Mermaid stays for small inline diagrams (existing `::: {.lightbox}` rule). Add `.staruml` handling to `.gitignore`/`.aiignore` only if needed.
- [ ] **TOOLS-UML-3** (plan: `.claude/design/uml_model_plan.md`, findings: `.claude/tasks/uml_findings.md`; plan accepted, in progress) `[opus/high]` then `[sonnet/high]`: First diagrams of SPARMVET_VIZ with StarUML MCP, one at a time, Eve reviews each: (1) C4 context + container, (2) activity diagram of the yes/no decision logic, (3) sequence (user click -> filter -> plot), (4) SysML requirement diagram linked to requirement IDs. Export to `docs/diagrams/`, reference in docs. Reference: `OBSWORK/60_ME/CAREER_TRANSITION/00_context/Learning_UML_for_SPARMVET_VIZ.md` (read only if Eve grants access).

### Planned / Large-scale backlog

- [ ] **23-C** `[sonnet/high]`: Galaxy XML wrapper templates; bundle deployment YAMLs in Docker; Galaxy admin docs.
- [ ] **23-D** `[opus/high]`: IRIDA plugin/iframe launch + `IridaConnector.fetch_data()`; IRIDA admin docs.
- [ ] **23-E** `[sonnet/medium]`: Per-system quick-start guides (Galaxy / IRIDA / server / local).
- [ ] **RESEARCH-LIMS-1** `[opus/high]` `[deferred — awaiting LIMS project]`: Audit database / LIMS integration — data analysis recipe hashes + data hashes in DB; LIMS link in audit report; configurable output path per app features.
- [ ] **UX-GALLEXP-1** `[sonnet/medium]`: Gallery Explorer right sidebar — functionality TBD.
- [ ] **UX-PLOTSTYLE-1** `[sonnet/medium]` `[deferred — eventual enhancement]`: The **Plot Style** panel (T3 `aesthetic_override`, `audit_stack.py` `aesthetic_style_panel_ui`, added 2026-05-11) is **not mounted** in HOME since 2026-11-05 (fork issue #15): letting users change in HOME what the data analysis recipe defines is too much for now, and using it broke the plot (test plan HOM-47). Code kept, unused, with a pointer comment at the mount point (`home_theater.py`). Later: find why it broke the plot, then decide whether to bring it back. Plot style that belongs to the data analysis recipe is authored in BLUEPRINT (separate). ADR-082 unchanged.
- [ ] **BP-VALIDATE-1** `[sonnet/low]` (narrowed 2026-11-08, bookkeeping check while verifying independent tasks — the original scope is done via `VALIDATE-UI-1`: the "Validate data analysis recipe" button exists, runs both `validate_data_analysis_recipe` (structure) and `validate_data_analysis_recipe_data` (data vs contract)). **Still open:** `_handle_upload_replace`/`_handle_upload_append` in `blueprint_handlers.py` (~line 1051/1066) parse the uploaded file's wrangling nodes with zero validation — neither check runs on upload, only when the user later clicks Validate by hand. Wire the same two headless checks into both upload handlers before the nodes are added to `logic_stack`.

### Explicitly deferred (scheduled)

- [ ] **DEPS-UPGRADE-1** `[sonnet/low]` `[deferred - monitor only, decided by Eve 2026-11-05]`: Dependency upgrades are frozen until the app is at a more advanced stage (no minor-version change before then). Monitor, do not apply. Known: plotnine 0.15.4 installed, 0.15.9 available (patch releases within the allowed range `>=0.15.4,<0.16.0`; still no pie or polar coordinates, see fork issue #19); matplotlib 3.10.9 -> 3.11.2 and mizani 0.14.4 -> 0.14.6 also available. When the freeze ends: upgrade one library at a time, run the full test suite and the plot render test (`app/tests/test_render_every_plot.py`), and compare the images. Open point: there is no lockfile for the main app, so a fresh install may already pick a newer patch version than the one tested (a lockfile, for example `uv.lock`, would pin it; packaging is Eve's to do by hand).

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

_No current enhancement requests. Append items here using the `[ENHANCEMENT REQUEST]` protocol (`rules_agent_role_bioscientist.md §4-A`) when a data analysis recipe design session exposes a missing action or plot component._

---

## 👤 User Required

Tasks requiring user decision, user action, or explicit discussion before implementation can proceed.

- [ ] **[@user] BLUEPRINT-AGENT-API-1** (reminder set 2026-11-07, revisit around 2026-11-14 when Claude API credits are available): Set up the `claude_api` backend for the BLUEPRINT AI agent (ADR-076). Today only `claude_cli` and `disabled` are implemented — `make_adapter()` in `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:399-402` degrades any other backend (including `claude_api`) to `DisabledAdapter` with "not implemented in Phase 1". Once credits are available: implement the `claude_api` adapter path (uses `ANTHROPIC_API_KEY`, see `rules_app_features_flags.md` consequences table), so `developer`/`qa` app features can choose `claude_cli` (uses the subscription, via the installed Claude Code CLI) or `claude_api` (uses metered credits) depending on which is cheaper/available at the time.
- [ ] **[@user] TOOLS-UML-0** (after live app testing; first step of the TOOLS / UML chain): Decide the StarUML licence before TOOLS-UML-1. Check: (a) official StarUML price and edition (a third-party site listed Professional at about 199 USD per user, VAT excluded; unverified); (b) whether the StarUML MCP server works on the free trial or needs the paid licence (not found in docs, unverified); (c) the 30-day trial may NOT have started yet (Eve has not opened the app; notes in `my-mentoring` say 2026-10-08, probably wrong); start it only when ready to do TOOLS-UML-1; (d) install StarUML >= 7.0.0 and confirm Node >= 22. Eve decided in principle to buy, because the MCP lets the agent and Eve draw diagrams together.
- [ ] Discuss - Aesthetics / automation visuals -> capture and adding to T3 audit ? possibilities ? Consequences ? Gating ?  
- [ ] **[@user] Taxonomy Data Audit**: Verify/correct tags in `assets/gallery_data/*/data_analysis_recipe.yaml` against `assets/gallery_data/TAXONOMY_CHEATSHEET.md`.
- [ ] **[@user] UX-CSS-DEMO**: Review `assets/demo/demo_vetinst.css` after default theme is finalised.
- [ ] **[FEATURE]** Label x/y axis adjustment module — edit title, policy change, color changes, points display — registered in audit. Large feature, grant-exploration candidate.
- [ ] **[TO DISCUSS]** Lab script: Extract pilot data analysis recipe (reconstitution of lineage) — improve reusability.
- [ ] **[TO DISCUSS]** Lab script: Create tool-specific data analysis recipe (e.g. single-sheet variant).
- [ ] **[TO DISCUSS]** Lab script: Combine data analysis recipes — format detection, common datasets, branching.

---

## 🟣 Completed Phases — Archived

| Phase | Description | Completed | Archive |
|---|---|---|---|
| Phases 16–18, 21-A–B | Nav/routing, data analysis recipe-driven tabs, tier toggle, layout | 2026-04-23 | [tasks_archive_2026-04-10.md](archives/tasks_archive_2026-04-10.md) |
| Phase 21-C–I, IU-1–7 | Comparison mode, filters, right sidebar, export bundle, VizFactory | 2026-04-23–30 | [tasks_archive_2026-04-14.md](archives/tasks_archive_2026-04-14.md) |
| Phase 22 (A–J) | Session mgmt, T3 audit, per-plot scoping, propagation | 2026-04-25 | [tasks_archive_2026-05-03.md](archives/tasks_archive_2026-05-03.md) |
| Phase 23-A/B | Deployment, connector library | 2026-04-30 | [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) |
| Phase 24 | `home_theater.py` decomposition (ADR-051) | 2026-05-01 | [tasks_archive_phase24.md](archives/tasks_archive_phase24.md) |
| Phase 25 (A–O) | Left sidebar restructure, app features flag gating, ADR-052+053 | 2026-05-01 | [tasks_archive_phase25.md](archives/tasks_archive_phase25.md) |
| Phase 26 CSS | UI harmonisation: view banners, button colours, Gallery sidebar refactor | 2026-05-02 | ADR-056, ADR-057 |
| DEMO-1..4 | Monday demo render/filter bugs — all fixed | 2026-04-30 | commits `55ab1c5` `33afa1b` etc. |
| Phase 28/29 | Export redesign + assembly→join rename + lib extraction | 2026-05-04/05 | ADR-066, ADR-067, ADR-068 |
| Phase 30 | Agent infra + deployment hardening | 2026-05-05 | commits `891f157`, `2dcd1c2` |
| Phase 31 | Sidebar Slot Registry (ADR-073) + Diagnostic Error Discipline (ADR-078) + Blueprint schema (ADR-075) + ADR-076 flag (ADR-077) | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |
| Phase 32 / May-09 hygiene | Export enhancements (EXPORT-2/3/4), UX-NOTIF-2, ADR-076 MVP-1 complete, BP-COLOR-1/2/3, all Open Issues + CSS batch | 2026-05-09 | [tasks_archive_2026-05-09.md](archives/tasks_archive_2026-05-09.md) |
| May-11 hygiene | Doc/ADR/lib-test audit fixes, Blueprint IDE features, ADR-079 design, cascade design, T3 threading, repo hygiene | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-11 session | BP-LINEAGE-NAV-1, GALLERY-CLONE-DECOUPLE-1, VIZFAC-RESOLVER-1, DIAG-RUNTIME-BASE-1 + full audit (EMOJI-DOCSTRING-1, VIZ-README-COUNT-1) | 2026-05-11 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| May-12 hygiene | Audit script fixes (CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1) | 2026-05-12 | [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md) |
| Phase 18-F, 32, 32-cont, audit-fixes | ACTION-UISCHEMA-1, BP-FORMS-1/ESCAPE/UNDO/HELP, ACTION-RENAME-1, all ADR-082 spawned BP-* tasks, DATA-ANALYSIS-RECIPE-INCLUDE-1 | 2026-05-21 | [tasks_archive_phase32.md](archives/tasks_archive_phase32.md) |
| Phase 33 | BP-AGENT-PARSER-1/TOOLS/INSTRUCT/PANEL/UI/CSS — all ADR-076 MVP-1 agent tasks | 2026-05-21 | [tasks_archive_phase33.md](archives/tasks_archive_phase33.md) |
| Documentation & Hygiene Sprint | DOC-BLUEPRINT-1/USER-1, DOC-LIBREADME-*, TASK-ARCHIVE-1, AUDIT-PASS-1, BP-ADR-FULL-1 | 2026-05-21 | [tasks_archive_hygiene_2026-05-21.md](archives/tasks_archive_hygiene_2026-05-21.md) |
| Phase 34 + May-22 hygiene | TEST_LAB Build (all TL-*), BP-HELP-*, audit fixes, legacy removal (FLAT-PLOTS/AUDIT-FLAG/TYPE-ALIASES/FLAT-WRANGLING), LAB-WORKFLOW-1, UX-APPLY-IMPROVE-1 | 2026-05-22 | [tasks_archive_2026-05-22.md](archives/tasks_archive_2026-05-22.md) |

---

## 📋 Session Notes

Context and status notes from recent sessions. Add here instead of inside active task sections.

- **2026-11-07 (continued autonomous session, Eve resting)** — Picked up from the UML findings
  pass (F-01 through F-21 all resolved) and continued per Eve's request: build out the rest of
  the UML model, verify app logic end-to-end (code vs ADR vs UML vs docs vs tests vs audits vs
  READMEs), fix what's fixable, log what needs her. ~20 commits, all pushed to `dev`.
  **UML:** added C4 component diagrams + use case diagrams for GALLERY, BLUEPRINT, TEST_LAB
  (same detail level as the existing HOME ones) — `.claude/design/uml_model_plan.md` updated.
  Reviewed all 23 diagrams for layout problems: found and fixed a real content bug in CTX-1 (two
  relationships pointed at IRIDA/Galaxy but neither node had a view — invisible, contradicting
  the model's own "shown as not implemented" scope decision), fixed real overlaps in
  C4-COMP-APP via auto-layout, tried auto-layout on DEP-APP (broke the nested containment,
  reverted via `app.repository.undo()`). Exported all 23 diagrams to `docs/UML/diagrams/*.png`.
  **F-22 (biggest find):** `GALLERY.md` claimed the Gallery→T3 transplant was "removed", with
  "copy YAML → open in BLUEPRINT" as the real handoff — backwards. The transplant
  (`handle_gallery_clone`, "Clone to Sandbox") is alive and working; there is no
  GALLERY→BLUEPRINT path at all. Fixed `GALLERY.md`, `developer_workflow.md`, and its Quarto
  mirror (which I'd written earlier this same session and had faithfully mirrored the wrong
  claim). Cross-checked against the archived LAB-SEND-TO-1/LAB-OPEN-BLUEPRINT-1 decisions
  (`archives/tasks_archive_2026-05-22.md`) — those were about TEST_LAB→BLUEPRINT, a different,
  correctly-dropped feature; no conflict with this fix.
  **Dead code removed** (DEAD-CODE-REVIEW-1, re-verified every item by grep rather than trusting
  the 2026-11-06 scan): `_fields_table`/`_parse_fields_safe` (wrangle_studio.py, superseded),
  `validate_schema` (ingestor.py, unused and incomplete), `galaxy_connector.py` (a second, fake
  `GalaxyConnector` class nothing imports). Opened `UNDO-WIRE-1` and `PIPELINE-ERROR-WIRE-1` for
  two features whose capture/producer side is real and built but whose trigger/consumer side
  was never wired — not deleted, needs Eve's call on wire-it-up vs. drop-the-design.
  **Also:** `AUDIT-GATE-UI-1` (new Playwright test for the Apply gate), `CONFIG-BLUEPRINT-ID-DISPLAY-1`
  (Blueprint selector showed paths, now shows ids), `DOC-RECHECK-2` (7-point doc sync),
  `LAB-WORKFLOW-QMD-1` (new user-facing workflow guide), `TEST_LAB.md` status line and its whole
  stale "Build Tasks (Phase 34)" section marked HISTORICAL (described 6 tools as unbuilt; all 6
  are built, tested, wired), `libs/test_lab/README.md` (was missing 3 of 6 tools). Full audit
  suite (`run_audits.sh all`, 10 routines) run twice, clean both times. Headless suite steady at
  1444 passed throughout; full browser suite green (47 passed, 3 skipped) after every batch of
  UI-touching changes.
  **Still open, needs Eve:** `STM-NODE`, `PIPELINE-ERROR-WIRE-1`, `UNDO-WIRE-1`,
  `TEST-INGESTION-1`, the Gallery/Blueprint sidebar-registry-bypass question (part of
  `CONFIG-TESTLAB-DATA-ANALYSIS-RECIPE-CHOICE-1`), UI wireframes for GALLERY/BLUEPRINT/TEST_LAB
  (in progress 2026-11-08), `EXPORT-CHECK-1` (needs a human at the keyboard), the Maps
  tasks (need external boundary data sourced). `BLUEPRINT-AGENT-API-1` reminder set for
  ~2026-11-14 when Claude API credits are available. `VALIDATE-UI-1` done 2026-11-08.

- **2026-05-21 (@sync — Phase 33 / BP-BRANCH-NODE-1)** — BP-BRANCH-NODE-1 completed and committed (`99e6b19`). Also discovered all 6 Phase 33 tasks (BP-AGENT-PARSER-1 through BP-AGENT-CSS-1) were already fully implemented (shipped 2026-05-09, tasks not marked done). Verified headless: all agent modules import OK, 3 tools dispatch (51 actions at runtime), sidebar registration + app features files + CSS all in place. Marked done. Added BP-BRANCH-UX-1 (data_schema branch guidance callout).
- **2026-05-21 (BP-JOINT-1 — Joint Designer pane)** — Implemented the dedicated Joint Designer (ADR-082 Q5). New pure stdlib module `libs/blueprint_arch/src/blueprint_arch/join_designer.py` (`compute_key_match` real-overlap stats incl. composite keys + dtype-family advisory; `build_join_step` sym `on` / asym `left_on`+`right_on`, scalar-vs-list; `parse_join_step` inverse w/ YAML boolean-trap guard) + 26 unit tests (all pass). New `4. Joint Designer` nav_panel in `wrangle_studio.render_ui`. Wiring in `blueprint_handlers.define_server`: R4-safe ingredient/key pickers, **real-data** preview (materialises each ingredient via `orchestrator.materialize_tier1`, String-cast key overlap mirroring the assembler), comment-gated Apply → logic_stack append/replace, edit pre-fill on join-node select. Removed the fabricated `show_join_modal`/`confirm_join`/`update_secondary_datasets` + dead picker selectors (clean break, no orphaned refs). Verified: 26/26 logic tests, both app modules import clean. Decisions taken with Eve: center pane · real-data overlap · composite/multi-key · edit+create. **Follow-up:** join-component Save (`_serialise_component_for_save` role `join`) must quote `on:` (pre-existing gap — join-role save not yet implemented). **Live UI smoke pending → BP-SMOKE-1** (no BLUEPRINT Playwright infra yet). Session triage: 3 audit reports PROCESSED (coherence PASS 6/6, integrity FAIL = known DATA-ANALYSIS-RECIPE-INCLUDE-1 false positive, 1 narrative log).
- **2026-05-20 (BLUEPRINT feature lock)** — Verified BP-FORMS-1 against the running implementation: all 60 transformer action forms render headless (zero failures, all 8 widget types). Found the form layer is half-built (add-node primitive vs edit-node rich; no component form path; 7/191 components schemed) + 2 ADR-075 widget gaps (enum preview, expression editor). Authored **ADR-082 (BLUEPRINT Full Feature Set & Build-Mode Contract)** — locked 4-layer model, 7 decision points, MVP/v2 inventory, T1/T2-vs-T3 boundary. Key decision with Eve: **branch = node-level lineage bifurcation** (shared upstream by reference, divergent downstream fragment-per-component `!include`) — NOT whole-data analysis recipe duplication; terminology fix (graph fan-out ≠ data analysis recipe branch). Spawned 12 Phase 32 (cont.) tasks. Research draft → RESOLVED.
- **2026-05-20** — Triaged 11 unprocessed audit files from 2026-05-13/18. 10 PASS (marked PROCESSED). 1 actionable finding: `audit_data_analysis_recipe_integrity.py` reports 6/6 data analysis recipes FAIL because `debug_assembler.py` uses `yaml.safe_load()` — `!include` not supported. All data analysis recipes are structurally fine (coherence audit PASS). Task added: DATA-ANALYSIS-RECIPE-INCLUDE-1 in Do Now.
- **2026-05-12** — All recent work (CROSS-LIB-SCRIPT-1, TASK-DRIFT-EXCLUSION-1, EMOJI-DOCSTRING-1, VIZ-README-COUNT-1) archived → [tasks_archive_2026-05-11.md](archives/tasks_archive_2026-05-11.md).

---

## Archive Pointers

- [tasks_archive_2026-05-22.md](archives/tasks_archive_2026-05-22.md) — Phase 34 (TEST_LAB Build) + BP-HELP sweep + audit fixes + legacy removal + LAB-WORKFLOW-1 + UX-APPLY-IMPROVE-1; also records DROPPED decisions (LAB-SEND-TO-1, LAB-OPEN-BLUEPRINT-1, UX-DEVINSP-1)
- [tasks_archive_phase33.md](archives/tasks_archive_phase33.md) — Phase 33: all ADR-076 MVP-1 Blueprint AI Agent tasks (BP-AGENT-*)
- [tasks_archive_phase32.md](archives/tasks_archive_phase32.md) — Phase 18-F, 32, 32-cont (ADR-082), audit script fixes: ACTION-UISCHEMA-1, all BP-* IDE/plot-model/branch/autosave tasks, DATA-ANALYSIS-RECIPE-INCLUDE-1
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
- [test_plan_2026-06.md](test_plan_2026-06.md) — **current** live app test plan (Phase 34 baseline; all 4 spaces + app features files)
- [tasks_test_ui_current.md](../outdated/tasks/tasks_test_ui_current.md) — OUTDATED (moved 2026-11-12), superseded Phase-26 UI checklist (items folded into the plan above)
