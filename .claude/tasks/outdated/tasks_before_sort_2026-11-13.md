> **OUTDATED (2026-11-13): archive copy of `tasks.md` before it was sorted.** It keeps the superseded tasks, the session notes and the old completed-phases table. Nothing here is an instruction. The live list is `.claude/tasks/tasks.md`.

# Tasks (SOLE SOURCE OF TRUTH)

**Workspace ID:** SPARMVET_VIZ
**Last Updated:** 2026-11-13 (cleanup: done items archived, ACTIVE MAP added; earlier: 2026-05-22 Phase 34 sweep) by @dasharch

---

## ACTIVE MAP (2026-11-13): read this first

What is current, what is superseded and what is older. The redesign period starts on 2026-11-11. Tasks are not renumbered; this map points to them. The plan behind the HOME tasks is `.claude/design/home_stage2_mechanism_spec.md` section 5 (packages P0-P12; milestone M1 = the walking skeleton); the order of work and the decisions are in `.claude/design/home_audit_reading_guide.md`.

| Track | Tasks (in the block "HOME Exploration and engine fixes" below) | Status |
|---|---|---|
| **1. HOME audit build** | STAGE2-SPEC-1, TEST-ADAPT-1, TEST-ORDER-1, TEST-SHAPES-1, NA-RULE-63, FILTER-DTYPES-1, RECIPE-GRAPH-UTILS-1, KEYS-NODE-1, AUDIT-VIEW-1, AUDIT-RAWYAML-REMOVE-1, AUDIT-REPLACE-1, AUDIT-USABILITY-1, UML-HOME-REDRAW-1, HOME-DESIGN-REVIEW-1 | design agreed; waits for Eve's reading, then P0 |
| **2. Filters, Exploration, engine fixes** (issues #56, #61, #62, #63, #66, #68, #72) | HOME-EXPLORE-1, 2, 3a, 3b, 4, 5, 6, 8, 10; TEST-FLAKY-1 | folded into packages P1 (filters), P3 (#61 with the graph), P8 (Exploration); the brief `home_exploration_build_brief.md` is detail input, ON HOLD as a plan |
| **3. Recipe format** (the recipe session; parent issue #73) | RECIPE-SPEC-1, RECIPE-TESTS-1, RECIPE-FORMAT-VERSION-1, RECIPE-MIGRATE-1, GALLERY-RECIPES-1, UTILS-REUSE-REVIEW-1, RECIPE-ORDER-IDS-1, RECIPE-REGISTRY-1, RECIPE-TYPES-1, RECIPE-DOCS-1, RECIPE-FORMULAS-1, RECIPE-AUDIT-REFRESH-1, ENTITY-DECL-1, RECIPE-FORMAT-1, UNKNOWN-KEYS-1, RECIPE-DATASET-TIER2-1, DOC-RECIPE-PLACEMENT-1, RECIPE-ST22-FIX-1 | in progress in the recipe session; spec `.claude/design/recipe_format_spec.md` |
| **4. Configuration stage (last)** | CONFIG-REVIEW-1; HOME-GATING-DECIDE-1 (paused) | after the build |
| **5. Superseded by the redesign** (kept until you confirm; each line says by what) | AUDIT-DECIDE-1, AUDIT-CUT-1, NEXT-SESSION-1, AUDIT-FORENSICS-1, AUDIT-ARCH-DECIDE-1, HOME-DESIGN-FIRST-1, STM-NODE, RECIPE-ST22-2, RECIPE-ST22-4 | superseded |
| **6. Older tasks, from before 2026-11-11, not triaged** | the sections "Clean-up recheck", "Export consistency", "Configuration vocabulary", "Maps", "HOME audit redesign: waiting for Eve", "Deferred / Blocked", "Planned / Large-scale", "Explicitly deferred", "User Required" (about 50 open items) | still valid unless a line says otherwise; to triage with Eve |

Done items of November were moved to `archives/tasks_archive_2026-11-13_done_since_nov.md` (pointer at the bottom).

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
- [ ] **RECIPE-ST22-2** `[opus/high]` — waits for Eve: what `ST22_Anchor` answers (#67: fan-out ResFinder x VirulenceFinder, wrong `virulence_count`, AMR "status" as virulence fill, missing `phenotype` in the contract), score of samples without usable phenotype (#70), MLST title and demo filter. Then fix the recipe, look at every picture, update the contract. **SUPERSEDED (2026-11-13): answered: R1-R4 (`recipe_review_st22_2026-11-11.md` 3b), applied by `RECIPE-ST22-FIX-1`.**
- [ ] **HOME-EXPLORE-8** `[sonnet/medium]` — #66 warning for plot-spec keys dropped to `_meta` (same surface as unknown `plot_defaults` keys). See brief WP8.
- [ ] **HOME-EXPLORE-10** `[sonnet/medium]` — #68 many-to-many join warning (rows before/after). Edits `libs/transformer` (frozen): needs Eve's OK. See brief WP10.
- [ ] **AUDIT-CUT-1** `[opus/high]` — Eve reviews the proposal `.claude/design/outdated/home_audit_first_cut.md` (a smaller first audit version) with the agenda `outdated/home_audit_review_agenda_2026-11-12.md`; then the accepted cut becomes work packages and sub-issues of #60. Depends: AUDIT-DECIDE-1 (group 1 of the agenda). **SUPERSEDED (2026-11-13): replaced by the walking skeleton M1 of `home_stage2_mechanism_spec.md`.**
- [ ] **NEXT-SESSION-1** — builders and the design review start from `.claude/tasks/outdated/next_session_start.md` (tracks A, B, D; file ownership; traps; paste-ready prompts). **SUPERSEDED (2026-11-13): the build plan is `home_stage2_mechanism_spec.md` section 5.**
- [ ] **AUDIT-FORENSICS-1** `[opus/high]` — Eve reads `.claude/design/home_evidence/home_audit_forensics_2026-11-12.md` (13 forensic findings, options and recommendations per undecided item) in the review; decisions go into the design files. Notable: no shipped recipe can show the central flaw of #60 (add a canary), an audit state can run as a forked recipe through a second orchestrator (alternative to a bespoke cache, proof of concept passed), `pipeline-exploration-simple` and `web-demo` would lose plot-changing views, stale wording and "never" in 8 HOME diagrams. **SUPERSEDED (2026-11-13): the findings are decided (guide section 2).**
- [ ] **RECIPE-ST22-4** `[sonnet/medium]` — the recipe review steps for 2026-11-12 are in section 5 of `recipe_review_st22_2026-11-11.md` (after Eve answers R1-R4). **SUPERSEDED (2026-11-13): see `RECIPE-ST22-FIX-1` and the recipe session.**
- [ ] **HOME-DESIGN-FIRST-1** `[opus/high]` — Eve's correction 2026-11-12: design first. She answers Q1-Q5 of `.claude/design/outdated/home_design_first_roadmap_2026-11-12.md` (behaviour table by kind of configuration). Then I write the agreed table into `home_preview_filters.md`, `home_audit_steps.md`, ADR-099, correct the contract 7.1, add columns A and D to HOME-VIEW-MATRIX (her OK for the UML first). Only after: mechanism (stage 2), build plan (stage 3). **SUPERSEDED (2026-11-13): stage 1 is done; see the guide.**
- [ ] **CONFIG-REVIEW-1** `[sonnet/medium]` — stage 5, after the design is coded (Eve, 2026-11-12; targets in `home_audit_reading_guide.md` section 0c): rename `pipeline-exploration-simple` to `pipeline-simple-exploration` (audit off, comparison off); `pipeline-exploration-advanced` = Exploration + Audit (+Compare, sessions, export), no Test Lab, Blueprint, Gallery; `developer` everything; `demo-vetinst` -> `web-demo-vetinst`; `web-demo` renamed once Eve decides static or Exploration only (earlier idea `static-web`); `standalone`, `qa` and others are Claude's test configurations, replaceable; `pipeline-static` unchanged (hyphen, validator Rule 2; also `demo-vetinst`; touches README, `docs/appendix/Terminology.qmd`, `docs/workflows/ui_app_features.qmd`, `app/tests/test_flag_matrix_doc.py`, `app/tests/test_every_app_features_starts.py`, the flag matrix of `rules_app_features_flags.md`, `docs/UML/app.mdj`, `assets/scripts/audit_old_words.py`, the deployment file under `config/deployment/demo/`). Not before the design and the build.
- [ ] **HOME-GATING-DECIDE-1** `[opus/high]` — **PAUSED** (stage 5, derived from the behaviour table): capability resolver, test configurations, companion rule, the two small defects. Do not start before HOME-DESIGN-FIRST-1 is agreed.
- [ ] **AUDIT-ARCH-DECIDE-1** `[opus/high]` — Eve decides after reading (status map in forensics section 0): first the interim of the header strip for features without the sandbox flag (forensics 3.7, F8) and "Raw has no plot (NA)" (F14); then N2 (what to do with the `developer_raw_yaml` step type: no code creates it; recommended display-only), N3 (trust levels for recipe text, AR1), N4 (how to hold the decided flag rules), N5 (architecture rules as tests), N6 (stored stages of the original anchors, needs her OK for `libs/transformer`), and the places where the forensics reconsider something decided (R1-R6). Candidate issues are listed in section 6 of the architect review; none is filed. **SUPERSEDED (2026-11-13): decided (guide section 2, O1-O8).**
- [ ] **HOME-DESIGN-REVIEW-1** `[opus/high]` — independent review of the decided design done 2026-11-12 (`.claude/design/home_evidence/home_design_review_2026-11-12.md`, guide problem P10). Eve decides, in order: SC1 (check on the plotted variable into the first set), SC2 (caption count for plots without a key), SC4 (remove by attribute), AR4 (entity noun field), SC5 (exclusion list), the wordings SC3/DS1/DS2, AR2 (oracle test for the action registry), AR1 (special datasets such as `metadata_schema`, stage 2). AR3/AR5/AR6 are build rules. Then the list of changed sections to read and the rewrite of `spaces/HOME.md`.
- [ ] **RECIPE-SPEC-1** `[opus/high]` — Eve 2026-11-13, tracking evezeyl/SPARMVET_VIZ#73 (parent of this block): the complete recipe format specification. Draft v0.1 written and committed (`.claude/design/recipe_format_spec.md`, ST22 worked example `recipe_format_st22_draft.yaml`, review `recipe_format_review_2026-11-13.md`); Eve reviews and answers section 13 (14 points). Then the text moves to its homes (rule file with double confirmation, appendix, user docs). Issue #74.
- [ ] **RECIPE-FORMAT-VERSION-1** `[opus/high]` — Eve 2026-11-13 (idea from her review of the app changes with another agent; accepted as good): every recipe declares `format_version: 1` (integer; today's unversioned recipes are format 0); the app reads one version; other versions are refused in both profiles (checks V01-V04) with a message that names the migration tool; `assets/scripts/migrate_recipe_format.py --from 0 --to 1` (dry run by default, `--apply`, safe twice, text-level so `#` comments are kept; precedent `migrate_config_vocabulary.py`); every writer emits it; `effective_run.yaml` records it; spec 4b. Name and form to confirm (spec section 13, point 16). Issue #83. The shipped recipes are converted with this tool in RECIPE-MIGRATE-1.
- [ ] **RECIPE-TESTS-1** `[opus/high]` — Eve 2026-11-13 + ADR-099 16(c): tests first, one per rule of the check catalogue (spec section 8), per replacement (9) and per tolerated form (11), over every kind of recipe file (pipelines, templates, retest, transformer test recipes, gallery, legacy, writers, inline test recipes); shared `make_recipe` helper; adapt the tests that encode superseded behaviour first (`wrangling: []` valid, inline recipes without engines); each fails for the right reason on today's code (recorded). Includes TEST-SHAPES-1. **Container forms (spec 4c, Eve 2026-11-13): a dictionary where ADR-041 says so, refused with a message that contains the corrected text, in the app and in the tests; the HOME plan (P2, P3 rows of `home_stage2_mechanism_spec.md`) and the reading guide carry it.** Issue #75. Depends on RECIPE-SPEC-1.
- [ ] **RECIPE-MIGRATE-1** `[sonnet/medium]` (ST22 and Abromics descriptions `[opus/high]`) — Eve 2026-11-13: every recipe follows the format: ST22 first, then the other pipelines, templates, retest, the 68 transformer test recipes (flat form -> one data schema with `source`), the 34 gallery bundles (moved to GALLERY-RECIPES-1, #82), the 2 legacy files (keep or remove: Eve), the writers (Blueprint form, bootstrapper, scaffolder, `create_data_analysis_recipe.py`). Collection hashes must not change except the named tier-2 change; fragment comments kept (text-level edits, spec 5b). **Order for ST22 (Eve 2026-11-13: science errors must be fixed): RECIPE-ST22-FIX-1 (R1-R4, #67 #69 #70) first, then the format migration and the final descriptions.** The gallery is GALLERY-RECIPES-1 (#82). Issue #78. Depends on RECIPE-CHECKER (UNKNOWN-KEYS-1).
- [ ] **GALLERY-RECIPES-1** `[opus/high]` — Eve 2026-11-13: the gallery examples follow the same spec as every recipe (with `format_version`), are checked by the same code as the app (one source of truth), carry a **required** `taxonomy` key, and their allowed terms go into the specification itself (one place instead of two). All eight findings G1-G8 are fixed, each by a named package and proved by a test. **Planned now, done later** (after the checker #76 and the pipeline-recipe migration #78). Plan GAL-0..GAL-9 with dependencies and tags: `.claude/design/recipe_format_gallery_options_2026-11-13.md` (version 2) section 7. **Decide now: D1 (standard recipe), D2 (`taxonomy` on the plot entry, required in the gallery profile), D3 (the specification as a data file, terms included), key name** — they shape the checker. D4-D7 when the work starts. Proof of concept: all 34 examples render as standard recipes through the app's path. Issue #82. Replaces the gallery part of RECIPE-MIGRATE-1.
- [ ] **UTILS-REUSE-REVIEW-1** `[opus/medium]` — Eve 2026-11-13 (a note, no overview yet): some code of the libraries may need to move to `libs/utils` to be reusable; that is what `utils` is for (`rules_test_lab.md` 2c). Candidates already met while reading, with evidence, in `recipe_format_spec.md` section 0b (the field-type vocabulary, the plot-spec key sets, reading a step container, the shape of a `ui_schema`, two renamed-key mechanisms, the lineage helpers). **Nothing is moved.** A review of the whole of `libs/` for more candidates, when Eve wants it; each move follows the Tier rules and its own tests-first package.
- [ ] **RECIPE-ORDER-IDS-1** `[opus/high]` — Eve 2026-11-13 (after the HOME analysis: "design our specs based on what depends on it"; #85, #86): the form of a container follows what depends on it (spec 4c, 4d). Steps stay lists with an optional `id`; the app writes `audit_` ids; named things are dictionaries; `final_contract`, `analysis_groups`, `plots` are ordered dictionaries with safeguards (loader keeps order and refuses a repeated key T10; writers `sort_keys=False` with a scan test; ordered key material for hashes). Fix #86 first (stored T2 keeps the old column order after a `final_contract` reorder): test first, needs permission for `cache_keys.py` and `orchestrator.py`. To confirm with Eve: `id` optional or required, `audit_` prefix, `final_contract` key order = column order, tab order = key order (spec 13.18).
- [ ] **RECIPE-REGISTRY-1** `[opus/high]` — Eve 2026-11-13 ("check how each operation for the data and plot is registered"; #87, spec 6.10): the registries are the checker's source and have gaps: 9 parameters declared `string`/multi enum whose example is a list or dictionary (add widgets `list`, `mapping`, `rules`), alias reads hidden in function bodies (`rename`, `split_column`), engine-internal `__keys__` (ST09), 2 actions without schema, all 191 components open to extra parameters (check against the wrapped plotnine arguments). Tests AR2 to AR6 first; each library exports its registry as plain data for the `utils` checker. Needs Eve's OK for the vocabulary (spec 13.20) and for edits in `libs/transformer` and `libs/viz_factory`.
- [ ] **RECIPE-TYPES-1** `[opus/medium]` — Eve 2026-11-13 ("unify, read in one place"): the field-type vocabulary is listed in four places that disagree (rule file section 9, user docs, the ingestor's cast, `MetadataValidator.DTYPE_MAP`); `utf8` is not cast by the ingestor (verified: digits stay Int64), `string` is accepted by the ingestor but refused by `enforce_schema`, 4 fixtures declare `i64`. The reason `string` was removed is only "deprecated alias" on record (LEGACY-TYPE-ALIASES-1). One list in the specification file with a one-line meaning per type, read by all; the content (options A to D, recommended A) waits for Eve (spec 6.4, point 10). Issue #84.
- [ ] **RECIPE-DOCS-1** `[sonnet/medium]` — Eve 2026-11-13: documentation and rule files follow the format (about 50 files mention `is_primary_key`, 32 `display_name`); rule files need Eve's double confirmation (diff first); ADR-099 16(g) sentence "unknown keys are warnings" corrected. Issue #79.
- [ ] **RECIPE-FORMULAS-1** `[opus/high]` — P9: formulas in recipes only from an allowed list of Polars operations, by function name, in `check_recipe` (check ST06); the list is derived from all recipes and approved by Eve before it is enforced. Issue #80.
- [ ] **RECIPE-AUDIT-REFRESH-1** `[sonnet/medium]` — Eve 2026-11-13 ("the audits are old"): the two recipe audits call `check_recipe` over every kind of recipe file (they pass 7 of 7 pipelines today while none has the engine keys); registry rows and `schedule_commands.md` updated. Issue #81. Depends on the checker.
- [ ] **ENTITY-DECL-1** `[sonnet/high]` — the recipe key `entity:` (`noun`, `plural`, `population`), 5a point 17: loader, validator (the population table must exist and carry the key), docs appendix, Blueprint form; unknown top-level keys **fail** (Eve 2026-11-13, not warn). Part of the checker, issue evezeyl/SPARMVET_VIZ#76. Stage 4.
- [ ] **RECIPE-FORMAT-1** `[opus/high]` — the recipe-format step, after UNKNOWN-KEYS-1 (otherwise new keys are ignored silently): required `data_engine` and `plot_engine` (5a point 21), `entity:` (ENTITY-DECL-1), the explicit optional T3 container at the plot entry, `is_primary_key` -> `is_entity_key` (**refuse at once**, Eve 2026-11-13; `legacy_keys.py` only names the replacement), a dataset's own tier-2 applied (RECIPE-DATASET-TIER2-1). The T3 container is in the schema now (Eve 2026-11-13). Sweep: every shipped recipe, template, gallery bundle, the Blueprint new-recipe form and navigator, `docs/appendix/data_analysis_recipe_structure.yaml`, `rules_data_analysis_recipe_structure.md` (double confirmation). Tests first. **Eve 2026-11-13: scope is every recipe, in the app and in tests (transformer test recipes included).** Split into RECIPE-SPEC-1, RECIPE-TESTS-1, UNKNOWN-KEYS-1 (checker, issue evezeyl/SPARMVET_VIZ#76), RECIPE-MIGRATE-1, RECIPE-DOCS-1. **UPDATE 2026-11-13: now tracked by RECIPE-SPEC-1 and RECIPE-TESTS-1 (the recipe session, `.claude/design/recipe_format_spec.md`); do not start it separately.**
- [ ] **KEYS-NODE-1** `[opus/high]` — stage 2, amends ADR-089 (Eve 2026-11-12): node keys for T1, T2, T3 (`hash(previous key, steps)`, an empty list keeps the previous key); the T1 key includes the collection (today one key for the whole recipe, verified by `tmpAI/architect/key_identity.py`); "affected" by content; the property tests listed in `home_audit_steps.md` 5a point 15. Tests first (TEST-ADAPT-1). Full model, inventory and open points: `.claude/design/home_evidence/home_hash_model_2026-11-12.md` (three families: identity hashes, node keys, content hash; retire the older `decision_hash`; the plot input key was never built; update `docs/foundations/reproducibility_hash_schema.qmd`).
- [ ] **TEST-SHAPES-1** `[opus/high]` — Eve 2026-11-12: the audit must work for any recipe. For every shipped recipe shape (`home_audit_steps.md` 5a point 18: joins with key, no joins, no key declared, another key name, no population table, long format, plotted table that is also an input) the recipe graph builds and a removal by key either applies or states why not; fixtures are the shipped recipes (`tmpAI/architect/recipe_shapes.py` is the scan). Written before the build (TEST-ADAPT-1). Part of RECIPE-TESTS-1, issue evezeyl/SPARMVET_VIZ#75.
- [ ] **FILTER-DTYPES-1** `[opus/high]` — Eve 2026-11-13: the audit and preview filters must work on any field of any content type. Verified today (`app/modules/t3_audit_engine.py`, `_coerce_to_dtype`): numbers (integers, decimals) and true/false are converted; dates, times, durations, lists, structs and categorical columns are compared as text or not at all. Write a table of column types with the operators, the value conversion and the dialog widget for each, one shared filter implementation for preview, audit and VizFactory, and tests per type including missing values (the NA rule, NA-RULE-63, and #62). Tests first.
- [ ] **STAGE2-SPEC-1** `[opus/high]` — draft v0.1 of the mechanism and build plan written 2026-11-13 (`.claude/design/home_stage2_mechanism_spec.md`): Eve reads and confirms; then the packages P0-P12 become tasks one by one, tests first; milestone M1 = P5 (the walking skeleton, headless). **Point 7 (2026-11-13): if the recipe steps become dictionaries (decided by Eve, investigated by the recipe session): refuse duplicate keys in the loader, convert to an ordered list in one place before hashing and running, writers keep the order (`sort_keys=False`, scanned by a test).**
- [ ] **AUDIT-VIEW-1** `[opus/high]` — stage 2 (Eve 2026-11-13): in audit mode the data and plots come from the copy of the recipe: one view recipe and one view orchestrator replace `active_cfg` and `orchestrator` at about 35 and 12 call sites; a test that no handler reads the original in audit mode; the copy file, its header (original hash, recipe format version), the origin marker (with the recipe session, spec 6.6), re-base after a change of the original, the badge "audit view of <recipe>". See `home_evidence/home_audit_view_from_copy_2026-11-13.md`. **DECIDED 2026-11-13 (Eve): the copy is the source of truth; invariant, original steps cannot be modified in the copy: property test `copy minus marked steps == original resolved`, checked at load, Apply, export and import; the node popup and the screen have no edit of an original step.**
- [ ] **RECIPE-DATASET-TIER2-1** `[opus/high]` — DECIDED by Eve 2026-11-12: every table has T1, T2, T3 with or without a join, T2 and T3 can be empty; a data schema plotted directly is a collection and its own tier-2 list is its T2 (today silently ignored, verified on `ResFinder` of `1_test_data_ST22_dummy`: `prepare_ingredient` runs tier1 only, `tier2_steps()` reads joins only). A tier-2 list on a dataset that is only an ingredient is a failure (`home_audit_steps.md` 5a point 19). Engine, graph, validator, tests first. Issue evezeyl/SPARMVET_VIZ#77; fix confirmed by Eve 2026-11-13 (the `amr_heatmap` changes: shown to her before and after for @verify).
- [ ] **AUDIT-RAWYAML-REMOVE-1** `[sonnet/medium]` — Eve 2026-11-12 (O3): remove the audit step type `developer_raw_yaml` (nothing creates it). Dependency sweep found it in `app/modules/exporter.py`, `app/modules/session_manager.py`, `app/handlers/audit_stack.py`, `app/handlers/export_handlers.py`, `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`, plus tests, the contract (`ui_implementation_contract.md` section 12), `rules_ui_dashboard.md`, ADR-093 mentions and the docs. Follow `rules_legacy_management.md` section 6 (marker, removal, tests, documentation sweep). Part of the audit build, after the step compiler.
- [ ] **UNKNOWN-KEYS-1** `[opus/high]` — Eve 2026-11-12: unknown keys must be reported. Verified (`tmpAI/architect/unknown_keys.py`): the validator reports nothing for an unknown top-level key, a typo key, unknown step parameters, or a forked T3 recipe (all 0 problems); plot-spec keys are dropped silently too (#66). Proposal: one schema of the allowed keys per level (top level, data schema, join, step lists with the parameters of each action from its `ui_schema`, plot entry, plot spec, `plot_defaults`, `info`, `entity`) in `libs/utils`; the validator reports unknown keys as warnings with a did-you-mean (never a block); the loader stays thin and only refuses retired or renamed keys (`legacy_keys.py`, existing). **Roles, to confirm with Eve:** one rule set `check_recipe(resolved recipe) -> problems with a severity` in `libs/utils`; the loader builds the recipe (parse, includes) and stops when the checks return errors; the validator reports every problem without running anything (HOME load gate, Blueprint, import screen); the data check (needs the data files) stays separate. Today the loader judges content (`config_loader.py` structural errors, retired keys) and the validator wraps the loader and adds id and step-list checks. Tests first (TEST-ADAPT-1). **UPDATE 2026-11-12 (Eve, 5a point 19):** fail instead of warn: in HOME the load gate rejects the recipe with the reason; in BLUEPRINT the problems are shown and never block building (empty placeholders accepted). Fails: a step list never applied, an unknown action, key or parameter, a column missing at that node (dry run on the column names), a step that fails on the data. A missing description stays an advice. One test recipe per failure. **UPDATE 2026-11-13 (Eve): unknown keys FAIL** (the sentence "reports unknown keys as warnings" above and ADR-099 16(g) are superseded: recipes can be verified first, in Blueprint); no backward-compatible default; old names refused at once, `legacy_keys.py` is kept only to suggest the replacement. Check catalogue: `.claude/design/recipe_format_spec.md` section 8. Issue evezeyl/SPARMVET_VIZ#76 (folds #66).
- [ ] **RECIPE-ST22-FIX-1** `[opus/high]` — apply R1-R4 (agreed by Eve 2026-11-12, `recipe_review_st22_2026-11-11.md` 3b) to the ST22 test recipe: `ST22_Anchor` without ResFinder, "none detected" explicit, descriptions with the grain and the treatment of missing values on every plotted table, the phenotype score without unknown, the MLST title with the years, the virulence tiles. Tests first, written to fail for the right reason (TEST-ADAPT-1); pictures checked. The entity declaration is decided (5a point 17); until ENTITY-DECL-1 is built the recipes carry descriptions only (the `entity:` key would be ignored). One problem at a time: R1 first. **2026-11-13:** descriptions for the tables as they are today are drafted in `.claude/design/recipe_format_st22_draft.yaml` with `REVISE` markers on the three tables and four plots that R1-R4 change; R1-R4 stay with issues #67, #69, #70. **UPDATE 2026-11-13: coordinate with the recipe session (RECIPE-SPEC-1, spec section 15, data-science errors in recipes) before starting.**
- [ ] **DOC-RECIPE-PLACEMENT-1** `[opus/high]` — Eve 2026-11-12: guidelines for recipe authors on where to put what (a change that must reach everything goes early, at T1; an exclusion added late is likely one that was missed), in the recipe structure rules, the docs appendix and the help. Rule files need Eve's double confirmation.
- [ ] **TEST-ORDER-1** `[opus/high]` — Eve 2026-11-12: specific tests for step order: the order of steps is the order of the lineage; steps at one node commute only when row-local; the z-score canary (`QA_population_zscore`) must show that the order changes the result and that the recorded order is the one run; the exported recipe re-run equals the audit data. Written before the build (TEST-ADAPT-1).
- [ ] **TEST-ADAPT-1** `[opus/high]` — Eve's rule 2026-11-12 (ADR-099 point 16): before any build step, inventory the tests that encode superseded behaviour (My view, Compare, the propagation dialog, per-plot reach, filters that drop missing values) and adapt or replace them to the decided design; each new or adapted test must fail for the right reason on the current code before the code is written. No test is run as evidence before that.
- [ ] **RECIPE-GRAPH-UTILS-1** `[opus/high]` — (2026-11-13: the builder relies on the container forms of ADR-041 and reports a wrong form with the checker's message; it feeds check J08, the silent `_right` suffix) stage 2: specification of `utils.recipe_graph` (nodes: datasets, T1, T2 and T3 nodes; edges; ID column present per node; plots per table; tables with the same T1 definition; the list of steps that summarise rows) and its tests; Blueprint's navigator is rebuilt on it (decided by Eve 2026-11-12: one source of truth; the graph also carries the include file of each node; the navigator tests are the regression oracle, adapted first; supersedes in part ADR-067/074).
- [ ] **NA-RULE-63** `[sonnet/high]` — Eve gave the rule 2026-11-12 (`home_audit_steps.md` section 19, "Meaning of the filters"): a missing value is a value; `!=` and none-of keep it, `==`, one-of and comparisons remove it, always counted and reported. Prerequisite of audit mode (the translated actions must do what the dialog says). `filter_ne` and `not_in` drop missing values today (verified); no shipped recipe uses them. Issue #63 WP3b was blocked on this rule: confirm with Eve, then unblock.
- [ ] **UML-HOME-REDRAW-1** `[opus/high]` — after the open review items are decided: redraw the HOME diagrams listed in `home_evidence/home_uml_review_2026-11-12.md` (3 contradicted, 8 partly outdated, 4 missing). Each UML edit needs Eve's OK; optional interim banner on the three contradicted diagrams. Run `assets/scripts/audit_uml_model.py` after each edit. The hash-model diagrams (`DM-KEYS` and its three details, and the changes to `STM-STAGE`, `HOME-AUDIT-CACHE`, `EXP-MODES`, `SEQ-EXPORT`) were done 2026-11-12. Also missing (Eve 2026-11-13): a diagram of the audit view (the view recipe and view orchestrator, original or copy, Compare, the integrity invariant) and the lineage tree as the navigator of nodes; the existing `HOME-AUDIT-CACHE`, `HOME-AUDIT-COMPONENTS` and `DM-KEYS-USE` mention the audit recipe but do not draw the switch.
- [ ] **TEST-FLAKY-1** `[sonnet/medium]` — #72: harden the browser tests (wait for connected and idle before selecting the recipe and check it took effect; poll the disk in the label test; stable grid read; server log in the failure output; `--durations`). Evidence in the forensics file, section 5.

### Manual-testing findings, 2026-11-10 (issues #53/#54/#55)

Eve's own first manual pass through Home/Blueprint/Export surfaced three real gaps code
reading alone had not caught. All three fixed same session; Home re-verification for
tomorrow's testing session is the remaining blocker.


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


### Audit Fixes — ADR Compliance (ADR behavioural audit 2026-11-06)


### Clean-up recheck 2026-11-06 (dead code, old tests, documentation)

Done 2026-11-06: removed `lookup.py` (`lookup_anchor_rows`), `DataWrangler.run_tier1/run_tier2`, `peek_data_analysis_recipe`, the `placeholder/` folders of `ingestion` and `transformer`, unused imports, `test_reactive_shell.py`, the app features benchmark scripts, and the broken `test_lab` demos (`debug_sdk`, `debug_ambiguity`, `debug_reconciler`, `demo_reconciler`; covered by `libs/id_reconciliation/tests`, `test_synthesizer`, `test_bootstrapper`, new `test_extractor`). Repaired `debug_pipeline_connector.py`, `debug_pipeline.py` + `PipelineExecutor` (tiered data analysis recipes, `join_id`), `libs/viz_gallery/tests/debug_gallery_submission.py`. The `generator_utils` name is gone from deployments and docs. Headless baseline: 1197 passed.

- [ ] **LEGACY-MATERIALIZE-SHIM-REMOVE-1** `[haiku/low]`: `assets/scripts/materialize_data_analysis_recipe_plots.py` is a thin forwarding shim to `libs/viz_factory/tests/debug_gallery.py`, marked "DEPRECATED SHIM" in its own docstring/`@deps` since before this audit but with no removal task (found 2026-11-07, DOC-RECHECK-2, `rules_legacy_management.md §4` — "a deprecation with no removal task is forbidden"). Still referenced by 6 doc files (`docs/appendix/FAQ.qmd`, `running_helper_scripts.qmd`, `docs/workflows/visualisation_factory.qmd`, `libs/viz_factory/README.md`, `assets/scripts/README.md`, plus two `.claude/tasks/` records) — check none of them need the shim for a still-valid reason before deleting; update each to the canonical `debug_gallery.py` command and delete the shim.
- [ ] **UNDO-WIRE-1** `[sonnet/medium]`: wire `app/handlers/blueprint_handlers.py`'s `_undo()` to a real "Undo" button in the BLUEPRINT IDE (found while resolving `DEAD-CODE-REVIEW-1`). The capture/persist side (20-step deque, draft save/restore) already works; only the trigger is missing. Needs Eve's call on where the button goes (toolbar? keyboard shortcut?) and whether it should also need the standard audit/reason gate or not (it reverts `logic_stack`, not T3 audit nodes, so probably not).
- [ ] **GALLERY-SUBMIT-SCHEMA-1** `[sonnet/low]` (found 2026-11-08, incidentally, during the library-README audit — not a doc issue): `libs/viz_gallery/src/viz_gallery/gallery_manager.py::submit_example()` writes gallery-bundle `data_analysis_recipe.yaml` files with a root-level `plots:` key (fatal `ConfigurationError` per LEGACY-FLAT-PLOTS-1, `rules_data_analysis_recipe_structure.md §8`) and a `wrangling: {tier1, tier2, tier3: example}` block (`tier3` is not a valid wrangling-tier key — only `tier1`/`tier2` exist, `rules_data_engine.md §3`). Any recipe this function generates would be rejected by the engine. Not yet reproduced live or confirmed as still-reachable code (README audit found it by reading the function, not by running it) — verify first, then fix the generated shape to `analysis_groups:`/`tier1`+`tier2` only.
- [ ] **PIPELINE-WARNING-SURFACE-1** `[sonnet/medium]`: the 4 `severity="warning"` `PipelineError` constructions that never raise (`ingestor.py` ×2 incl. the documented "Silent Skip Warning", `viz_factory.py` ×2) print to console and nowhere else — found while closing `PIPELINE-ERROR-WIRE-2` (ADR-095 §7, deliberately scoped out). No exception to catch, so `capture_entry()`'s pattern doesn't apply; needs `DataIngestor.ingest()`/`VizFactory.render()` to return or collect warnings instead, then a caller to surface them (likely `data_import_panel` / `notification` surfaces per their own `surface=` field). Needs a design pass on the return-value shape before implementing — not a quick fix.

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


### Configuration vocabulary and launch variables (ADR-091, proposed 2026-11-07, revised: one pass, no hybrid)

Names agreed: `deployment` (`SPARMVET_DEPLOYMENT`), `app features` (`SPARMVET_APP_FEATURES`), `data analysis recipe` (`SPARMVET_DATA_ANALYSIS_RECIPE`, today still called data analysis recipe). "App features" is retired for the application; it stays only for the two AI agent files. Everything with an old word (folders, files, classes, keys, labels, docs, tests) is renamed in ONE scripted run; a hybrid state must not reach a shared branch. Issue: evezeyl/SPARMVET_VIZ#27 (IRIDA check: #28). Implementation plan: `.claude/tasks/outdated/config_rename_strategy.md`.

- [ ] **CONFIG-PIPELINE-RENAME-1** `[sonnet/high]` (Eve, 2026-11-08, found live while testing — a miss from the CONFIG-RENAME-1/ADR-091 pass): the three `pipeline-*` app features names (`pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`) collide with the project's other, established meaning of "pipeline" — `CTX-1`'s "Analysis pipeline" external actor (the upstream bioinformatics system, e.g. Galaxy/IRIDA, that produces the data files). These three names actually mean "this deployment receives data pushed by an automated pipeline," which is a different thing — same shape of collision as the "Pipeline Issues" panel rename this session (F-26). Scoped as **Phase 2** (deployment-limitations testing), not mid-HOME-testing: touches 3 app features filenames, `rules_app_features_flags.md`'s full matrix, every launch command referencing them, deployment configs, docs, and `test_plan_2026-06.md` §2's CFG section. Needs a name decision first (e.g. `auto-static`/`auto-exploration-simple`/`auto-exploration-advanced`, or `fed-*`, or something naming the "data pushed automatically" property without using "pipeline") before any rename executes.
- [ ] **DEPS-REVIEW-1** (issue evezeyl/SPARMVET_VIZ#35) `[opus/medium]`: 61 outdated packages, 11 major (polars 1.40 to 2.1, pyarrow 24 to 26, pillow 12 to 13 ...) from `audit_package_deps.py`. Polars 2 first: ADR-035 parity audit of `libs/transformer/src/transformer/actions/`, run the full suites on a branch, then the others.
- [ ] **CONFIG-AGENT-BACKENDS-1** `[opus/medium]`: implement the `claude_api` and `local` backends of the BLUEPRINT agent (ADR-076 phase 2); until then `blueprint_agent.model`, `.endpoint`, `.api_key_env`, `.gallery_awareness` stay in the templates marked "reserved, not implemented".
- [ ] **CONFIG-STEPS-WRITE-1** `[sonnet/high]`: BLUEPRINT writes into the step lists location while the deployment guide says it is read-only, and overwrites files in place. Interim: warning and timestamped backup before overwriting. Target: BLUEPRINT edits a draft copy in `user_data`, validation (#26) runs on it, an explicit publish copies it into the step lists location; the location can stay read-only in production. See ADR-091 gaps. Depends: #26.
- [ ] **CONFIG-APP-RESOURCES-1** `[opus/high]`: application resources (app features folder, `theme.css`, sidebars, development fallback) are found relative to the working directory; locate them from the code root so a container or an installed copy works. Design first, see ADR-091 gaps. Depends: CONFIG-RENAME-1 (new folder names).
- [ ] **CONFIG-CACHE-LOCATION-1** `[sonnet/high]`: the deployment location `cache` (formerly `curated_data`, documented as the place of the Tier 1 and Tier 2 parquet caches) is required by the bootloader but read by no code; the anchors are written under `user_data/anchors/` instead. Decide: use `cache` for the anchors (cache is rebuildable, user data is work) or drop the location. Found in phase 5 of the rename. BLUEPRINT drafts already live in `user_data/_blueprint_drafts` (see CONFIG-STEPS-WRITE-1).
- [ ] **CONFIG-IRIDA-CHECK-1** (evezeyl/SPARMVET_VIZ#28) `[opus/medium]`: check ADR-048's IRIDA token assumption with someone who knows IRIDA before the IRIDA connector is built.

### LAB-WORKFLOW follow-up


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

- [ ] **AUDIT-DECIDE-1** `[opus/high]` — Eve answers the questions of the reading guide section 3 (stage and reach, NA default, reason categories, caption, key source, reach selector, audit table selector, trial computation, event log, lineage map, guard-rail list, D1-D14, legacy names); then redraw `HOME-AUDIT-LINEAGE` and `HOME-AUDIT-EFFECT`, update ADR-099, write the build plan. **SUPERSEDED (2026-11-13): the 13 questions are answered (guide section 2).**
- [ ] **AUDIT-REPLACE-1** `[sonnet/medium]` — tracking item so nothing becomes orphaned: when audit mode is built, replace (do not leave behind) My view, Compare and "Plot to show" in the strip, the propagation dialog, per-plot `t3_audit_steps_by_plot` (old sessions map to plot-level steps), the pending badge / filter inventory / Apply gate of the right panel, and update `UC-HOME`, `SEQ-AUDIT`, `COM-REACTIVE`, `C4-COMP-HOME`, `UI-HOME as built today`, the amendment notes in ADR-024, 044, 049, 085, 086, 089, 097, 098, the contract and the help. Depends: AUDIT-DECIDE-1.
- [ ] **AUDIT-USABILITY-1** `[sonnet/low]` — before the dialog wording is final: 2-3 scientists who did not write the design use it on the ST22 recipe, thinking aloud (persona 5 of `design_review_personas.md`). Depends: dialog built.

Items where a design pass, ADR authoring, or explicit scoping is needed before code can be written.

- [ ] **TEST-INGESTION-1** `[sonnet/medium]`: `libs/ingestion/tests/` has zero pytest-discoverable tests — only `debug_ingestor.py` (an argparse CLI debugger, not pytest-named) and `ingestion_integrity_suite.py`. `pytest libs` silently runs nothing for this library; every other lib has real `test_*.py` files (found while resolving finding F-11, `.claude/tasks/uml_findings.md`). Needs a design pass on what `IngestorFactory`/`ConfigManager` test coverage should look like before writing it — not a quick fix.
- [ ] **STM-NODE** `[sonnet/medium]`: T3 audit node "Disable" (Power icon / `active: false`) is designed in `ui_implementation_contract.md` §1/§12c but never implemented — `audit_stack.py` reads `node.get("active", True)` for strikethrough styling and `export_handlers.py` filters on it, but nothing in the running app ever sets it to `False`; deletion is real list removal instead (found while resolving finding F-07, `.claude/tasks/uml_findings.md`). Decide: (a) build the Power-icon toggle so strikethrough/deactivate becomes real, matching the designed Export warning + Appendix behaviour, or (b) drop the dead `active` read/filter code and the unreachable Export-warning/Appendix text, keeping only real deletion. Needs Eve's call — changes user-facing audit UX either way. **SUPERSEDED (2026-11-13): the node 'disable' toggle belongs to the old model; removed with `AUDIT-REPLACE-1`.**

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

- [ ] **DEMO-USERS-1** `[sonnet/medium]`: functionality demo for users, most of them not developers (Eve, 2026-11-07; work on it after the fixes). Show the interface and what they can do: get the graphs, filter data, navigate the plots of one data analysis recipe, select another data analysis recipe and see the UI build itself. Briefly show what can be switched on and off: (1) fully static with a custom logo (`pipeline-static` plus a deployment with branding), (2) possibly a pipeline with some data exploration (`pipeline-exploration-simple`), (3) everything else, audit and so on, with the full configuration Eve uses for development (`developer`). A separate short demo for interested developers is possible. Check first that each of the three starts with the logo and data wanted.
- [ ] **DOCKER-RELEASE-1** `[sonnet/medium]`: later (Eve, 2026-11-07). There has been no Docker release yet. `assets/containers/Dockerfile` uses Python 3.12 while development is on 3.14 (finding F-19). Build and run the image, rootless, and add it to DEP-APP when it works. **Eve 2026-11-13: the Dockerfile is not ready and must be updated; nothing is deployed yet, so nothing is urgent.** **Found 2026-11-13 (reading, not yet built):** `Dockerfile:79` installs `libs/generator_utils` (renamed `test_lab`, ADR-084; the folder does not exist, so that `RUN` fails) and does not install `blueprint_arch`, `test_lab` or `id_reconciliation`; the libs are installed non-editable, so any data file in a library (for example the recipe specification file planned in `libs/utils`) needs `[tool.setuptools.package-data]` and a packaging test.
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

- [tasks_archive_2026-11-13_done_since_nov.md](archives/tasks_archive_2026-11-13_done_since_nov.md) — 52 done items of the November work (HOME exploration, reproducible export and import, configuration vocabulary, manual-testing findings, clean-up recheck), moved out of this file on 2026-11-13
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
- [tasks_test_ui_current.md](outdated/tasks_test_ui_current.md) — OUTDATED (moved 2026-11-12, now in `outdated/`), superseded Phase-26 UI checklist (items folded into the plan above)
