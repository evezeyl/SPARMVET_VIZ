# TESTLAB-REVIEW-1, step 1a: the sources on the Test Lab

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396: "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)"). It builds nothing and decides nothing.

**Summary.** The Test Lab is described in one long design file (`spaces/TEST_LAB.md`, mostly of May 2026, status line of 2026-11-07, example updated 2026-11-20), one rule file, one ADR (ADR-084, marked partly stale) and five other ADRs that touch it, the producer-workflow design, two user docs, the in-app help and the four UML diagrams. One earlier review exists (`.claude/design/exploration/2026-11-18_test_lab_review.md`, 15 fixes and 9 questions); it is the best single source and is partly out of date (section 6). The owner's decisions about the Test Lab are few: the order of work (D-0048, D-0271, D-0272), the side panels (D-0381) and this review (D-0396). The code is two libraries (`libs/test_lab`, `libs/id_reconciliation`), one shared module in `libs/utils`, one module and one handler file in `app/`.

**Labels.** "read" = I read it now in this worktree (branch `task/lab-review` at `52c4bcfa`), with file:line. "document" = taken from a text, not re-checked. "run" = I ran it (command given in `02_planned_vs_existing.md`). The status of a source is what the text says about itself, plus a note where the code says otherwise.

---

## 1. The design files

| Path | Date | Status | What it says |
|---|---|---|---|
| `.claude/design/spaces/TEST_LAB.md` (971 lines) | "Last updated: 2026-05-05" (line 8); status line "Built (checked 2026-11-07)" (line 4); file last committed 2026-11-20 | design file; stale in places (read) | The Test Lab is "a collection of small, focused utilities that help users prepare data for the app and test the app itself" (line 14), for data stewards, developers and recipe authors (lines 16-19). Five tool groups with their functionalities (lines 23-80); a long design of the ID reconciliation (lines 83-320: certainty per pair, a YAML transformation with an audit log, chunked review, many-to-many with a written reason, recode workflow, multi-file sequencing); the scaffolding with key selection and an example boilerplate (lines 324-510; the example was refreshed to format 1 and says it is "the real output of `DataAnalysisRecipeScaffolder.scaffold`", line 359); anonymisation (lines 514-653); synthetic data with demo and stress modes and named scenarios (lines 657-810); non-goals and constraints (lines 814-830). Lines 844-849 mark the "Current State" and "Build Tasks (Phase 34)" sections HISTORICAL. Line 3-7 says "all six tools are implemented and wired": not true for the Excel extractor (read, see `02` section F) |
| `.claude/design/developer_workflow.md` (250 lines) | "Last updated: 2026-05-22" (line 4) | design (LAB-WORKFLOW-1); stale in places (read) | The producer journey TEST_LAB, BLUEPRINT, GALLERY, HOME (lines 53-102); every tool stands alone (lines 34-51); advisory orders (reconcile before anonymising several files or scaffolding with joins; reformat before reconciling; lines 104-120); hand-offs are file-based, no in-app crossing (lines 157-187); one in-space convenience: the scaffolding may take the steps of a reconciliation run in the same session (lines 136-141). Line 89 still says `final_contract` is "the developer's job in BLUEPRINT" (removed, ADR-100) |
| `.claude/design/exploration/2026-11-18_test_lab_review.md` (201 lines) | 2026-11-18, read at commit `cd0a11d8` | exploration; "Nothing here is decided" (line 3) | The earlier review (her request M271: "we will need to fix the lab anyway and review how its functioning"). What each tool does, what is wrong (scaffold names tables after the upload numbers, silent `sample_id` default, delimiter by file ending, synthetic data placeholders, anonymiser crash, cleaning step breaks matched ids, panels that say more than the tools do), 15 fixes in order, 9 questions with defaults. Ran library functions on small files. Section 6 of this file says which of its points changed since |
| `.claude/design/exploration/2026-11-17_author_manifest.md` | 2026-11-17 | exploration | Mentions the Test Lab in passing (a contact field, the Test Lab to BLUEPRINT hand-off). Not read in full here |
| `.claude/design/outdated/id_reconciliation_module_sketch.md` | before 2026-05-22 | outdated (history) | The first sketch of the ID reconciliation library; named by `TEST_LAB.md:840` as "outdated, history". Not read |
| `.claude/design/functionality_dependency_map.md` section 8 (line 125) | not stated | design | "TEST LAB - Synthetic data and data analysis recipe scaffolding": one flag `test_lab_enabled` (line 129). Not read in full |
| `.claude/design/app_features_capability_matrix.md` (lines 94, 135), `app_features_scoping_guide.md` | not stated | design | `test_lab_enabled` is Y only for developer and qa (read line 94) |
| `.claude/design/ui_reachability_map.md` | 2026-11-08 | design | Test Lab's alerts moved to the left sidebar; the nav item is gated. Not read in full |
| `.claude/design/uml_model_plan.md` (lines 80-84, 138-139) | 2026-11-07, 2026-11-08 | design | Four TEST_LAB diagrams exist (UC, UI, C4-COMP, COM-REACTIVE), marked done (read) |
| `.claude/design/recipe_format_spec.md` | "DRAFT, cleaned on 2026-11-13" | specification of recipe format 1 | What the Test Lab writers must write. R4 (line 205): one constants module for action names in `libs/utils` "so `test_lab` and `id_reconciliation` can read it" (built: `utils/action_names.py`). DEC52 (line 179): the `label` of `info`, a table, a join and a field "stays `label` for now (PENDING Eve ...)" (read) |
| `.claude/design/decisions_2026-11-14/rule_file_proposals/rules_test_lab.md.proposal.md` and rows R077 to R086 of `RULE_FILE_CHANGES.md` (lines 146-155) | 2026-11-14 | proposals for her double confirmation; "No rule file was edited" | Corrections of `rules_test_lab.md` to format 1 (table 4a, the known-bugs paragraph as HISTORICAL, the action names of 4c). Status "proposed" (read) |
| `.claude/design/lab_revision/ORDER.md` | 2026-11-20 night | the owner's order, relayed (blocks M422, M423) | Her words: "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format"; "also a preparation without details"; and (M423) "yes it will have to explore what we had planned, what is existing, many things will need to be anyway verified and updated". The rest of the block is the relaying session's text |

## 2. The ADRs that name the Test Lab

Source: `.claude/knowledge/architecture_decisions.md` (read by section, lines given).

| ADR | Date, status | What it decides for the Test Lab | State |
|---|---|---|---|
| ADR-084 TEST_LAB Toolbox Architecture (line 4004) | 2026-05-21, "ACCEPTED"; banner (line 4006): "Partly stale (2026-11-14, ADR-SYNC-1): the bootstrapper output named here ... is format 0 ... Test Lab is to be adapted later (Eve 2026-11-14: Blueprint and Test Lab last)" | Six decisions: (1) a stateless toolbox, the only saved files are named transformations and named scenarios; (2) `libs/id_reconciliation` a separate library importing only `utils`, polars and the standard library; (3) the pattern helper in `libs/utils/id_patterns.py`, "imported by both `libs/id_reconciliation/` and `libs/blueprint_arch/join_designer.py`"; (4) the synthetic config is an archive record, never a recipe; (5) single-key reconciliation, BLUEPRINT designs joins; (6) the boilerplate writes structure, types, key hints, `joins: {}` (an empty stub) and ID cleaning steps only; "It does NOT generate ... join recipes beyond primary-key cleaning". Implementation decisions of 2026-05-22: rapidfuzz, no reuse caching, `reconciler.py` deleted | (1), (2), (4), (5) built (read). (3) half built: `join_designer.py` does not import `id_patterns` (read, a grep finds no import). (6) contradicted by the scaffolder, which writes an inner join (read, `scaffolder.py:129-138, 177-189`). Words of format 0 (`join_manifests`, `ManifestBootstrapper`, `type:`) |
| ADR-068 Extract `libs/test_lab/` (line 2123) | 2026-05-05 | `generator_utils` absorbed into `libs/test_lab`; `dev_studio.py` renamed `test_lab_studio.py`, class `TestLabStudio` | built (read). The handler still takes a keyword `dev_studio` (`test_lab_handlers.py:36`; `server.py:122`) |
| ADR-052 point 52-6 (line 1557), ADR-056 (line 1742) | 2026-05-01, 2026-05-02 | "Dev Studio" renamed "Test Lab" in user text; the view title banner | built (read: `test_lab_studio.py:93-101`) |
| ADR-071 Positive inclusion (line 2250) | 2026-05-05 | A space is mounted only when its flag is on | built (read: `home_theater.py:1835-1836`, `server.py:122, 191-193`) |
| ADR-073 Sidebar slot registry (line 2380) | 2026-05-09, notes of 2026-11-08 and 2026-11-10 | The Test Lab sidebars come from `config/ui/sidebars/testlab_standard_{left,right}.yaml`; panel types `test_lab_info` (left) and `test_lab_right_info` (right) | built (read). A third panel type `test_lab` is registered and used by no sidebar file (`sidebar_registry.py:95-101`, its own comment) |
| ADR-076 BLUEPRINT AI agent (line 2911, table line 3000) | 2026-05-09 | The agent's schema summary tool "Reuses extraction logic from `AquaSynthesizer`" | not checked (the agent is out of this review) |
| ADR-082 BLUEPRINT feature set (lines 3853, 3913) | 2026-05-20 | "Pattern helper - reuse the TEST_LAB component if feasible"; and "Pattern helper sharing with TEST_LAB - each space keeps its own implementation until a clear duplication emerges (separate ADR)" | contradicts ADR-084 point 3 (listed in `02` section K) |
| ADR-091 (line 4491), ADR-092 (lines 4519, 4527) | 2026-11-07 | `test_lab_enabled` alone controls the Test Lab; the recipe `id:` equals the file name (`rules_test_lab.md` 3a cited) | built for the flag (read) |
| ADR-093, ADR-094 (lines 4574, 4615) | 2026-11-08 | No interactive hand-off between spaces; with no usable recipe HOME names "Blueprint/Test Lab" as the place to make one | built (read: `home_theater.py:1068-1069`) |
| ADR-097 point 8 (line 4991) | 2026-11-09 | "the user guide gets a new section recommending anonymisation before data ever reaches the app, with any de-anonymisation key kept outside it entirely" | in tension with the Test Lab anonymiser, which runs inside the app and puts the mapping into the same download as the anonymised file (listed in `02` section K) |
| ADR-099 point 16 (line 5143) | 2026-11-12 | (d) a primitive needed by two domain libraries goes to `libs/utils` "by the existing rule (`rules_test_lab.md` 2c)"; (a) a wrong recipe is corrected, never protected by a shim | applies to the shim `pattern_detector.py` (task PATTERN-DETECTOR-SHIM-1) |

## 3. Rule files

| Path | Date | What it says about the Test Lab | State |
|---|---|---|---|
| `.claude/rules/rules_test_lab.md` (300 lines) | "ACTIVE ... (2026-05-21, ADR-084)"; file last committed 2026-11-20 | Eight absolute prohibitions (lines 10-19); stateless tools (section 1); the boundary of `id_reconciliation` (section 2) with the shim `pattern_detector.py` named as such (line 64); the synthetic config firewall (section 3); the bootstrapper scope (section 4, table 4a) with "Known bugs" (section 4b, line 145); the single-key boundary (section 5); the Two-Category Law (section 6); the flag (section 7); the file layout (section 8); the test protocol (section 9) and the audit greps (section 10) | stale in places (read): section 4b lists three bugs that are fixed; section 4c lists four injected actions, the code writes six; section 3d names `load_scenario()`, the code has `load_config()`; section 8 lists `steps.py`, which does not exist, and leaves out `recipe_steps.py` and three test files; section 9 line 271 asks that the boilerplate pass `ConfigManager.load()`, which it cannot (see `02`). The proposals of 2026-11-14 (section 1 above) are not applied |
| `.claude/rules/rules_runtime_environment.md` section 4 | not dated | `libs/test_lab` is a named exception: it may compose `id_reconciliation` and `ingestion` (uses neither); every import of `libs/utils` "MUST" be declared in the library's `pyproject.toml` | the `test_lab` library imports `utils` and does not declare it (read; `02` section H) |
| `.claude/rules/rules_app_features_flags.md` Group D | not dated | `test_lab_enabled` gates the Test Lab; true in developer and qa only (flag matrix) | current (read: `config/app_features/*.yaml`) |
| `.claude/rules/ui_implementation_contract.md` section 11d | updated 2026-11-20 | `test_lab_info` (left; "static placeholder text, never the open data analysis recipe's `info:` block", issue #33) and `test_lab_right_info` (right, reachable since issue #55) | current (read) |
| `.claude/rules/rules_toolchain.md` | 2026-11-07 | `scripts/install_libs.sh` installs "every `libs/*` package as editable" | the script's list has no `id_reconciliation` (read, `scripts/install_libs.sh:23-32`) |
| `.claude/rules/rules_verification_testing.md` sections 1, 9 | 2026-11-06, 2026-11-14 | Tests that can fail, edge cases; `id_reconciliation` has a CLI integrity suite | current |

## 4. The owner's decisions about the Test Lab (ledger)

Source: `.claude/knowledge/decision_ledger.md` (523 lines; a grep for test lab, scaffold, anonymis, synthetic, reconcil and bootstrap). All lines below are taken by EVE and DECIDED. Where the decision text of a line is a reviewer's or coordinator's wording, the ledger says so and I say so.

| Number | Date | Decision (quoted from the line) | Note |
|---|---|---|---|
| D-0048 | 2026-11-14 | "Order of work HOME, then Gallery, Blueprint and Test Lab last" | |
| D-0271 | 2026-11-18 | "(2) Blueprint and Test Lab only where the big recipe change forces it, kept minimal; everything else of them waits until after the demo" | her words in the evidence field: "we do changes to blueprint and lab after - we focus on home and gallery" |
| D-0272 | 2026-11-18 | "The demo comes AFTER the big recipe change." | `tasks.md:621` adds "No Test Lab scaffolding in the demo" (a task line; not found as a ledger line) |
| D-0381 | 2026-11-20 | "BLUEPRINT, GALLERY and TEST_LAB use the same width and drag mechanism for their side panels as HOME (D-0375); their side panels are likely always visible" | the line says "Coordinator's wording, not her words" for the decision text |
| D-0396 | 2026-11-20 | "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)" | the line says "Review session's summary, not her words; her words are in the evidence field" (quoted in `ORDER.md`) |

Decisions that are not about the Test Lab but that its tools must follow (also EVE, DECIDED):

| Number | Decision (quoted) | Why it matters to the Test Lab |
|---|---|---|
| D-0050 | "No silent error: that is the rule" | the silent defaults of the handler (`02` section A) |
| D-0067, D-0225 | D-0225: "The sample id is a string or a categorical, never a number" | the scaffold declares a numeric-looking id `Int64` (run, `02` section B) |
| D-0007 | "recipe `id` = file name" | the scaffold's recipe id is free text (`02` section B) |
| D-0390, D-0391 | D-0390: "A recipe file name is name_date, exactly." | the scaffold writes `<id>/<id>.yaml` with no date (read); D-0392 limits the rule to production recipes |
| D-0374 | "Informing about undeclared file columns belongs to the user space BLUEPRINT." | the scaffold declares every column of the file, so it never meets that case (read) |
| D-0250 to D-0253 | the tier as its own key; `ui_label` for groups and plots | the writers already follow them (`02` section B) |

Nothing in the "Asked, not decided" part of the ledger names the Test Lab (grep).

## 5. Tasks in `.claude/tasks/tasks.md` (924 lines)

| Task | Line | State in the file | Check |
|---|---|---|---|
| TESTLAB-REVIEW-1 | 347 | open, "Not started" (this review); holds the three ideas: "extract a pilot recipe (reconstruct a lineage), a tool-specific recipe (for example a single-sheet variant), combine recipes (format detection, common datasets, branching)" | - |
| TESTLAB-REVIEW-1 | 677 | "`[done: report]` - review DONE 2026-11-18" (the earlier review); "The fixes wait for Eve's reading ... After the demo (Eve, 2026-11-18, D-0271)" | the same task id twice with two states: a contradiction in the records (`02` section K) |
| TESTLAB-EMPTY-KEY-DEFAULT | 647 | "waits for Eve": `sample_id` when the join key field is empty | still in the code (read, `test_lab_handlers.py:422, 424`) |
| ID-RECON-STEPS-1 | 221-222 | done; "DECISION FOR EVE: three defects are recorded as strict xfail tests" (delimiter step always `_` to `-`; prefix step empties a short id; a step changes the whole column) | the three xfail tests exist (read, `libs/id_reconciliation/tests/test_suggested_steps.py:87-112`); two confirmed by a run (`02` section A) |
| WRITERS-W8-1 | 219-220 | done; "DECISIONS FOR EVE: (1) a new Blueprint draft has no plot, and the app's loader refuses a recipe without a plot" | applies to every Test Lab scaffold too (run, `02` section B) |
| PATTERN-DETECTOR-SHIM-1 | 452 | open: remove the shim `pattern_detector.py` | the shim is there (read) |
| FORMULA-SAFETY-1, SECURITY-DEPLOY-1, SECURITY-REVIEW-END-1 | 123, 272, 133 | the ID reconciliation `mutate` is one of three formula sites | `apply_recode_step` now checks the formula (`core.py:286-289`, `utils.formula_check`); her confirmation is open (document) |
| DOCKER-RELEASE-1 (issue #90) | 271 | the Dockerfile leaves out `test_lab` and `id_reconciliation` | confirmed: no line names them in `assets/containers/Dockerfile` (read) |
| UTILS-REUSE-REVIEW-1 | 179 | code to move to `libs/utils` | cites `rules_test_lab.md` 2c |
| HELP-FROM-DOCS-1 | 282 | the in-app help files are "current for gallery, blueprint and tes[t lab]" | the Test Lab help is not current (read, `02` section G) |
| UML-DOCS-1 | 317 | `docs/workflows/test_lab_sdk.qmd` still carries a Mermaid diagram | not checked |
| CONFIG-REVIEW-1 | 196 | the target app features: "no Test Lab" in `pipeline-exploration-advanced` | consistent with the flag matrix |
| RECIPE-MIGRATE-1 | 174 | the writers of recipes follow the format | the Test Lab writers are format 1 (`02` section B) |
| Archive `tasks_archive_2026-05-22.md` | 5, 121, 147-160 | Phase 34 (the build of all TL-* tasks) done; LAB-WORKFLOW-1 done; DROPPED: LAB-SEND-TO-1 (a "Send to scaffolding" button), LAB-OPEN-BLUEPRINT-1 (an "Open in BLUEPRINT" button), both for space independence | read |

No TL-* task is open in `tasks.md` (grep); the TL-* ids live in `TEST_LAB.md` lines 879-971 (HISTORICAL) and in the archive.

## 6. User documentation, in-app help, library readmes

| Path | Last commit | Status | Note |
|---|---|---|---|
| `docs/workflows/test_lab_sdk.qmd` (65 lines) | 2026-11-14 | partly stale (read) | "renamed from `generator_utils` in ADR-084" (it was ADR-068); presents the extractor as "Stage A" of an automation path, while no screen uses it; says the handler has "990 lines" (1007 today) |
| `docs/appendix/test_lab_rationale.qmd` (51 lines) | 2026-11-08 | partly stale (read) | "Test Lab never authors `tier1`/`tier2` wrangling logic" against the scaffold, which writes ID cleaning steps and a join into `tier1`; the mapping lets the substitution "be traced (but not reversed by a reader who only has the anonymised file)" |
| `docs/workflows/developer_workflow.qmd` (104 lines) | 2026-11-08 | partly stale (read) | the user version of `developer_workflow.md`; says the de-anonymising step is "printed in the Anonymiser's own output" (not on the screen, `02` section E) and "open it in BLUEPRINT like any data analysis recipe" (BLUEPRINT's upload takes one `.yaml`, `02` section I) |
| `docs/reference/debugging_pipelines.qmd`, `developer_how_to.qmd`, `testing.qmd`, `ui_style_guide.qmd`, `docs/workflows/ui_app_features.qmd`, `audit_scripts.qmd`, `docs/foundations/core_architecture*.qmd`, `docs/deployment/deployment_guide.qmd`, `docs/index.qmd`, `docs/appendix/Terminology.qmd`, `docs/user_guide/glossary_and_feedback.qmd`, `understanding_your_export.qmd` | 2026-11-07 to 2026-11-21 | not read line by line | name the Test Lab once to 18 times each (grep count) |
| `docs/UML/risks_and_technical_debt.md` (lines 23, 25) | 2026-11-18 | current (read) | two resolved findings (F-01, F-03/F-17) |
| `app/src/help/test_lab.md` (21 lines) | not checked | stale (read) | "save the result as a named ID transformation" (the screen offers a download, no name); "including named error scenarios" (not on the screen); "empty wrangling/plot stubs" (no plot stub is written; a join is) |
| `libs/test_lab/README.md` | not checked | stale in places (read) | line 14: the bootstrapper is "Not wired into any handler yet - integration is pending known-bug fixes" (the bugs are fixed; the scaffolder uses it inside); line 52: "No cross-lib imports" (it imports `utils`) |
| `libs/id_reconciliation/README.md` | 2026-11-14 (task DOCS-SYNC-IDRECON-1) | not read in full | the tables of both step languages (cited by `test_lab_sdk.qmd`) |

## 7. The UML model

`docs/UML/diagrams/`: `UC-TESTLAB_What_a_user_does.png`, `UI-TESTLAB_The_screen.png`, `C4-COMP-TESTLAB_Inside_TEST_LAB.png`, `COM-REACTIVE-TESTLAB_Reactive_wiring_of_TEST_LAB.png` (read: the file names). The plan marks them done (2026-11-07). Not checked: whether they match the code; `audit_uml_model.py` was not run; the pictures were not opened.

## 8. The code (pointers; the facts are in `02`)

| Path | Lines | Role |
|---|---|---|
| `libs/test_lab/src/test_lab/scaffolder.py` | 217 | the recipe ZIP (on screen) |
| `libs/test_lab/src/test_lab/bootstrapper.py` | 198 | type guessing and a recipe folder; `bootstrap()` used only by tests |
| `libs/test_lab/src/test_lab/aqua_synthesizer.py` | 462 | synthetic data (class and a legacy CLI) |
| `libs/test_lab/src/test_lab/anonymiser.py` | 360 | anonymisation |
| `libs/test_lab/src/test_lab/reformatter.py` | 175 | XLSX and delimited text to TSV |
| `libs/test_lab/src/test_lab/extractor.py` | 73 | XLSX to TSV with a key renamed `id` (no screen) |
| `libs/id_reconciliation/src/id_reconciliation/` | 589 in 7 files | matching, patterns, the step language, `recipe_steps` |
| `libs/utils/src/utils/id_patterns.py` | 132 | the pattern primitives |
| `app/modules/test_lab_studio.py` | 131 | the screen shell and `scaffold_from_uploads` |
| `app/handlers/test_lab_handlers.py` | 1007 | the reactive wiring of the five panels |
| `app/handlers/home_theater.py` | lines 1051-1054, 1835-1836, 1954-1966, 2126-2127, 2248-2301, 2358-2360 | the nav item, the theater, the left and right sidebars |
| `config/ui/sidebars/testlab_standard_{left,right}.yaml` | - | the two sidebars |
| Tests | `libs/test_lab/tests/` 6 files, 111 test functions; `libs/id_reconciliation/tests/` 7 files, 56 test functions plus a CLI integrity suite; `app/tests/test_id_cleaning_steps_reach_a_recipe.py` (16), `test_click_reads_visible.py` (2 of 5 on the Test Lab), `test_shiny_smoke.py` (one right-sidebar test), `test_writers_emit_format_one.py` (names the Test Lab writers, line 11) | counts by `grep -c '^\s*def test'`; not run |

## 9. Prior work in the main tree (git-ignored; listed, not copied)

| Path (main tree `tmpAI/`) | Date | What it is |
|---|---|---|
| `panel/test_lab_review/` (`run1.py`, `run2.py`, `up/`, `ref/`, `out_sample_id/`, `out_Sample_ID/`) | 2026-11-18 | the runs behind the earlier review |
| `rename/issues/testlab.md` | 2026-11-07 | a short issue note of the rename work (842 bytes); not read |
| `audit_lib_tests/id_reconciliation/id_reconciliation_integrity_report.md` | 2026-11-08 | the CLI integrity report (210 bytes); not read |
| `engine_keys/step4c_report.md`, `step4_REVIEW.md`, `step4_fixes_report.md`, `FINAL_REVIEW_and_CONTROLS.md`, `RULE_SENTENCES_for_eve_2026-11-19.md`, `RULE_SENTENCES_OUT_OF_DATE_after_merge.md`, `merge_dev_report.md`, `review2_fixes_report.md`, `step1_report.md` to `step5_report.md`; `coordinator/briefs/ENGINE_KEYS_facts_2026-11-18.md` | 2026-11-18, 2026-11-19 | the big recipe change; step 4c rewrote the Test Lab writers (handoff line 165: "step 4c (Blueprint, Test Lab, scripts)"); they name the Test Lab; not read |
| `home_review_2026-11-10/05_testlab.png`, `rename/shot_testlab.png`, `rename/final_testlab.png`, `coordinator/panel_widths_review/testlab_1100.png`, `testlab_1366.png` | 2026-11-07 to 2026-11-20 | screenshots of the Test Lab screen; the only pictures of it that exist; not opened |

Recommendation to the coordinator (as for BLUEPRINT): have a scribe copy the earlier review's run scripts and the step 4c report into `prior_work/` of this folder, so that a cleaning of `tmpAI/` loses nothing.

## 10. What I did not find

- An older Test Lab specification than `spaces/TEST_LAB.md` (the archive names the "Dev Studio" era only through ADR-052, ADR-056, ADR-068).
- A ledger line that says what the owner wants the Test Lab to be beyond her words of M422 and M423.
- A written description of the three ideas of the task (pilot recipe, tool-specific recipe, combined recipes) beyond `tasks.md:347`.

## Not verified

- The docs listed without "read" in section 6, the UML pictures, `id_reconciliation/README.md`, the prior work of section 9.
- Whether `docs/workflows/test_lab_sdk.qmd` renders (Mermaid include `_sdk_mermaid.mmd` not checked).
- The dates "last committed" of files I did not log one by one.
