# Wave 1: `.claude/design/studies/` (manifest, 2026-11-26)

Order: the owner's, channel block M704 ("one source of truth; what is old goes to outdated; studies that are no longer actual are removed from the live tree"). Plan: `tmpAI/status/SOURCE_OF_TRUTH_CLEANUP_PLAN_2026-11-26.md`. Written before any move; the moves follow in later commits.

## The rule of this wave
- A study whose result is in the ledger or a design file, and that nothing current rests on as its only copy, is OUTDATED and moves to `.claude/outdated/design/studies/<same path>`. History: `git log --follow <path>`.
- A study that is ongoing, that a handoff or a task still waits on, or that a live file, the code or the ledger cites as the place of its content, is KEPT.
- A file that a live file I may not edit cites by path gets a one-line pointer at the old path (removed when the citing file is actualised in wave 2). A folder cited as a folder gets a `README.md` pointer.
- Nothing is moved on a guess; what I cannot judge is listed for the owner.

## Verdicts per study folder
| Folder | Files | Verdict | Reason | Replaced by | Who still links to it |
|---|---|---|---|---|---|
| `staruml_text_practice/` | 1 | KEEP | Written 2026-11-26, living practice page | (itself) | the page names itself |
| `whole_picture_2026-11/` (8 documents at the top) | 8 | KEEP | `WHOLE_PICTURE.md` is the one actualised document (D-0605) and says which of the other seven are current; code (`id_completion.py`, `id_log.py`, `audit_places.py`, `test_id_completion.py`), the dependency index, `demo_deliberate_oddities.md`, `agent_dispatch_howto.md` and ledger D-05xx cite them. UPDATE (not done here, listed): `DESIGN_AGREED_AND_QUESTIONS.md` is superseded in part by the recheck table of `PATHS_AND_DERIVED_AGREED.md` (its own header and `WHOLE_PICTURE.md` line 24 say so); `GOALS_REVIEW.md` is historical for its dialog and questions (`WHOLE_PICTURE.md` line 21); `RECIPE_PROPOSAL_refined.md` is a proposal NOT confirmed (D-0496) | the ledger, `WHOLE_PICTURE.md` | code, knowledge, workflows, ledger |
| `whole_picture_2026-11/sources/` | 115 | KEEP | The evidence (run registers, tables, retest outputs) that the kept documents name by path in their own text (for example `sources/design_dialogue/RUN_REGISTER_*.md`, `sources/whole_picture/RETEST_her_scope.md`); moving it would break the kept study. Revisit when the kept study is next actualised | | the kept documents; `knowledge/demo_deliberate_oddities.md` cites `sources/tmp_2026-11-23/dry_run_big_move_report.md` |
| `lineage_scope_2026-11/` | 78 | KEEP | The lineage research the handoff lists as "RESEARCH DONE, waiting for the owner" (open state, lines 13, 73) and ledger D-0507 names; the demo work on the lineage is running. Revisit after the demo | decisions D-0627 to D-0637 are in the ledger; the pages stay as the evidence | handoff, ledger |
| `scratch_records_2026-11/` | 657 | PARTLY OUTDATED, see the next two sections: 155 files moved, 502 kept because an open task waits on them | Scratch copied on 2026-11-25 from `tmpAI` and `tmp`. The README of the folder says nothing in it is a decision. A group is kept when an unchecked task of `tasks.md` names its folder or pages and waits on it, studies it or builds from it; the rest is history | the ledger, the ADR log, the rules, git history | see below |

The three folders marked KEEP are checked again in a later wave (after the demo): the lineage research and the whole-picture evidence move when their decisions are built and the handoff no longer waits on them.

## Kept because an open task waits on it (502 files, moved back in the fix round)
The first round moved all 657 files. The check found that open tasks of `.claude/tasks/tasks.md` (unchecked `- [ ]` lines) wait on, study or build from many of the groups, so they came back to `.claude/design/studies/scratch_records_2026-11/`. The rule, applied by script: a group returns when an unchecked task whose text says it waits, is a study, is blocked or is "not decided" names the group's folder as a path (`panel/<name>`, `coordinator/<name>`, `tmpAI/<name>`) or one of its main page names; a task that names more than six groups at once (`DEPLOYMENT-READ-WRITE-STUDY`) does not count by itself; the ten the coordinator listed return in any case. The README of the kept folder lists every folder with its task. The rule is broad: it kept 71 groups. When a task is done its folder moves to the archive.

| Folder or file (under `scratch_records_2026-11/`) | Files | Open task(s) |
|---|---|---|
| `controls_8f951761` | 3 | JOIN-GROWTH-CAUTION-1, ST22-DUPLICATE-ROWS-1 |
| `coordinator/QUESTIONS_FOR_THE_STOP.md` | 1 | AUDIT-QUESTIONS-FOR-THE-STOP |
| `coordinator/WHAT_BLOCKS_THE_BUILD.md` | 1 | (named by the coordinator; ledger names it) |
| `coordinator/app_features_name` | 4 | NAMES-UI-LABEL-EVERYWHERE |
| `coordinator/blueprint_verify` | 7 | BLUEPRINT-VERIFY-SEVEN-POINTS |
| `coordinator/data_file_cut` | 1 | DATA-FILE-CUT-ACCEPTED |
| `coordinator/data_import_check` | 1 | DATA-IMPORT-OVERWRITE |
| `coordinator/data_import_questions` | 1 | CONNECT-TEMPLATE-DATA-LOOKUP |
| `coordinator/default_data` | 3 | RECIPE-DEFAULT-DATA-FALLBACK-TEST |
| `coordinator/gallery_fixes_review` | 4 | GALLERY-TWO-NAMES |
| `coordinator/gallery_picture_key_review` | 40 | MAP-A-GALLERY-1 |
| `coordinator/home_data_picker` | 2 | DATA-IMPORT-OVERWRITE |
| `coordinator/ledger_words_check` | 2 | LEDGER-WORDS-CHECK, NAMES-UI-LABEL-EVERYWHERE |
| `coordinator/names_pass_plan` | 4 | NAMES-UI-LABEL-EVERYWHERE |
| `coordinator/panel_statistician_draft` | 1 | PANEL-STATISTICIAN-AGENT |
| `coordinator/permanent_documents` | 1 | PERMANENT-DOCUMENTS-OUT-OF-TMP |
| `coordinator/plot_rows_dropped` | 1 | PLOT-ROWS-NOT-DRAWN |
| `coordinator/recipe_name_rule` | 1 | DEPLOYMENT-STANDARD, RECIPE-NAME-RULE |
| `coordinator/remove_from_all_review` | 1 | AUDIT-REMOVE-FROM-ALL-DATA |
| `coordinator/remove_from_all_review2` | 1 | AUDIT-REMOVE-FROM-ALL-DATA |
| `coordinator/report_by_group` | 1 | NAMES-UI-LABEL-EVERYWHERE |
| `coordinator/uncertainty_catalogue` | 1 | AUDIT-LIMITS-DOCUMENTED, AUDIT-UNCERTAINTY-CATALOGUE |
| `engine_keys` | 29 | BLUEPRINT-PLOT-PREVIEW-NOT-MOUNTED-1, BLUEPRINT-REMOVED-BUTTON-AND-HINT-1, ENGINE-KEYS, JOIN-KEY-PROTECTION-CHECK-1, LOADER-WRAPPER-UNWRAP-1, QUESTIONS-PARKED-UNTIL-REFACTOR-STEP, RECIPE-ORPHAN-FILES-1, TIER3-READER-AND-TEXTS-1, TIER3-WORDS-MIXUP-CHECK-1 |
| `panel/adr` | 4 | ADRS-FOR-DECISIONS-WITHOUT-ONE |
| `panel/adr_history` | 110 | ADRS-FOR-DECISIONS-WITHOUT-ONE |
| `panel/audit_docs` | 1 | AUDIT-HELP-TEXT |
| `panel/audit_model` | 22 | AUDIT-RULES, READING-ERRORS-1 |
| `panel/audit_redesign` | 3 | HOME-AUDIT-REDESIGN-SLICES-1 |
| `panel/audit_rules` | 1 | AUDIT-RULES, SESSIONS-MANY-DATASETS |
| `panel/author_manifest` | 1 | CONTACT-AUTHOR-MANIFEST-1 |
| `panel/axis_text` | 3 | FORMULA-BUILD-D-1]** , PATH-BASE-1]** , PATH-CHECK-1]** , DATA-IMPORT-OVERWRITE |
| `panel/check_on_select` | 1 | CHECK-ON-SELECT |
| `panel/data_ids` | 4 | ID-TEST-REFERENCE-TABLES-1 |
| `panel/data_import_words` | 1 | DATA-IMPORT-SILENT-FACTS, HOME-DATA-IMPORT-MESSAGES-WORDS |
| `panel/deployment_io` | 13 | DEPLOYMENT-STANDARD |
| `panel/deployment_no_user` | 9 | DATA-FILE-CUT-ACCEPTED, DEPLOYMENT-NO-USER-STUDY |
| `panel/deployment_standard` | 6 | DEPLOYMENT-STANDARD, PERMANENT-DOCUMENTS-OUT-OF-TMP |
| `panel/dialog_preview` | 2 | AUDIT-DIALOG-PREVIEWS |
| `panel/engine_boundary` | 6 | ENGINE-BOUNDARY-STUDY |
| `panel/engines` | 8 | ENGINES-PLAN-1, ENTITY-DECL-SHIPPED-1, LOOKUP-TABLE-1, PLOT-DEFAULTS-DEAD-KEYS-1 |
| `panel/export_modes` | 2 | EXP-MODES-DIAGRAM |
| `panel/export_simplify` | 8 | REVIEW2-OPEN-POINTS-FOR-EVE |
| `panel/formula_d` | 11 | FORMULA-BUILD-D-1]** , FORMULA-RULE-TESTS-1]** , PATH-BASE-1]** , PATH-CHECK-1]** , ROW-ORDER-PROJECTION-1]** , DATA-IMPORT-OVERWRITE, FORMULA-BUILD-D-1, FORMULA-D-STUDY-1 |
| `panel/formula_night` | 2 | FORMULA-BUILD-D-1 (named by the coordinator) |
| `panel/formula_safety` | 3 | FORMULA-D-STUDY-1 |
| `panel/gallery_check` | 3 | GALLERY-LEFTOVERS-1]**  |
| `panel/gallery_study` | 9 | GALLERY-CHART-TYPE-AXIS, GALLERY-CONTENT-CORRECTIONS, GALLERY-NAMES-HEADINGS, GALLERY-PICTURE-PROOF, GALLERY-STUDY-RECHECK |
| `panel/gallery_taxonomy` | 5 | GALLERY-TAXONOMY-REVIEW, TEXTS-FOLLOW-UP |
| `panel/gallery_verify` | 9 | GALLERY-CONTENT-CORRECTIONS, GALLERY-VERIFY-ALL-34 |
| `panel/help_beside` | 8 | HELP-BESIDE-THE-SCREEN-STUDY |
| `panel/id_vs_key` | 1 | ENTITY-DECL-SHIPPED-1, PLOT-DEFAULTS-DEAD-KEYS-1 |
| `panel/key_types` | 2 | KEY-WORDING-OPTIONS-1, LOOKUP-TABLE-1 |
| `panel/label_trace` | 6 | JOIN-LABEL-REBUILD-1]** , JOIN-KEY-PROTECTION-CHECK-1, LABEL-TRACE-1 |
| `panel/lookup_table` | 1 | LOOKUP-TABLE-1 |
| `panel/name_fields` | 1 | NAME-FIELDS-PURPOSE-TABLE |
| `panel/names_whole_app` | 8 | NAMES-ACROSS-THE-APP-STUDY, NAMES-UI-LABEL-EVERYWHERE, TEXTS-FOLLOW-UP |
| `panel/one_python` | 4 | OTHER-PYTHON-PATHS-1]** , ONE-PYTHON-RULE-WORDING-1 |
| `panel/path_use_cases` | 4 | FORMULA-BUILD-D-1]** , PATH-BASE-1]** , PATH-CHECK-1]** , DATA-IMPORT-OVERWRITE, PATH-USE-CASES-STUDY-1 |
| `panel/recipe_arguments` | 6 | ENTITY-DECL-SHIPPED-1, LOOKUP-TABLE-1, PLOT-DEFAULTS-DEAD-KEYS-1, SECURITY-FINDINGS-2026-11-17, SILENT-DEFAULTS-2026-11-17, VIZ-SEED-DICT-POSITION-1 |
| `panel/recipe_places` | 6 | RECIPE-NAME-DATE-RULE, STUDY-RECIPE-PLACES |
| `panel/recipe_versions` | 7 | STUDY-RECIPE-VERSIONS |
| `panel/round7` | 46 | AGENT-PROBE-1, FILTER-PICKERS-1, READING-ERRORS-1 |
| `panel/session_import` | 7 | SESSION-IMPORT-KEY-EXISTS-1 |
| `panel/sessions` | 2 | AUDIT-RULES, SESSIONS-MANY-DATASETS |
| `panel/steps_position_help` | 1 | VIEWPOINTS-O13-O14 |
| `panel/test_speed` | 1 | TEST-SPEED-STUDY-1 |
| `panel/uploaded_data_place` | 4 | DATA-IMPORT-OVERWRITE, DEPLOYMENT-STANDARD |
| `panel/verification` | 18 | FILTER-RESET-ON-STAGE, RULE-EDITS-15 |
| `panel/viz` | 4 | VIZ-NOT-ADDABLE-15-1, VIZ-OWN-22-1 |
| `panel/viz_rename` | 5 | VIZ-NOT-ADDABLE-15-1, VIZ-OWN-22-1 |
| `panel/write_test_at_start` | 2 | DEPLOYMENT-STANDARD, WRITE-TEST-AT-START |

## Moved to the archive (155 files; in `.claude/outdated/design/studies/scratch_records_2026-11/`)
No open task names these groups. Groups and files: MAP.tsv 1 | README.md 1 | coordinator 17 | coordinator/audit_folder_name 1 | coordinator/briefs 2 | coordinator/browser_tests_cause 1 | coordinator/data_import_review 1 | coordinator/data_import_review2 1 | coordinator/drop_uncertain 2 | coordinator/gallery_walk_2026-11-20 1 | coordinator/gate_gap_cause 1 | coordinator/lbfb_review_1 1 | coordinator/lbfb_review_3 1 | coordinator/opening_build_control 10 | coordinator/opening_build_control2 4 | coordinator/panel_widths_review 1 | coordinator/picture_tests 1 | coordinator/slice_b_final2 2 | coordinator/slice_c1_final 1 | coordinator/slice_c1_final3 7 | coordinator/smoke_preview_filter 1 | doc_worktree_section.md 1 | panel 5 | panel/audit_recipe_file 4 | panel/blueprint_gap 8 | panel/blueprint_step4 5 | panel/column_labels 1 | panel/column_tracking 5 | panel/default_ticks 4 | panel/export_box 7 | panel/export_ready 3 | panel/export_value 1 | panel/lab_step4 5 | panel/lbfb 6 | panel/na_rule 1 | panel/panel_widths 4 | panel/polars_catch 1 | panel/recipe_error_place 1 | panel/records 1 | panel/round5 7 | panel/seed_ops 6 | panel/seed_step 2 | panel/stat_function_polars 3 | panel/step_order 1 | panel/uml_sync 2 | panel/validate 2 | panel/verify 1 | panel/wide_split 1 | switch_check 9.

## Pointers that this wave leaves (OUTDATED files that a live file cites)
At the old path of each file in the list `pointer_files` below (only the ones still moved: after the fix round 30 pointers remain; the others were removed when their file came back), one line: "Moved to `.claude/outdated/...`". A `README.md` of the same kind stands at the old folder path for the cited folders. They are removed as wave 2 actualises the citing files in `.claude/design/` (the blocks `blueprint_revision`, `lab_revision`, `exploration`, `decisions_2026-11-14`, `engine_boundary_map.md`, `home_redesign_intent_and_consequences.md`, `uml_model_plan.md`).

Cited folders that still hold a pointer README: `panel/{blueprint_step4,lab_step4,wide_split}/`. The cited folders `engine_boundary`, `formula_safety`, `key_types`, `recipe_places`, `viz` and `verify` came back with their files.

### pointer_files
- `coordinator/briefs/ENGINE_KEYS_facts_2026-11-18.md`
- `engine_keys/BLUEPRINT_T1_T2_PROOF.md`
- `engine_keys/TIER3_facts_2026-11-18.md`
- `engine_keys/step4_REVIEW.md`
- `engine_keys/step4c_report.md`
- `panel/adr/ledger.md`
- `panel/adr/review_corrections.md`
- `panel/audit_docs/intent_text_draft.md`
- `panel/audit_model/scenarios_report.md`
- `panel/audit_model/scenarios_report_round2.md`
- `panel/audit_rules/PROPOSALS_for_eve.md`
- `panel/author_manifest/REPORT_for_eve.md`
- `panel/blueprint_gap/GAP_DIGEST_for_eve.md`
- `panel/blueprint_gap/GAP_REPORT_full_part1.md`
- `panel/blueprint_gap/GAP_REPORT_full_part2.md`
- `panel/blueprint_gap/GAP_REPORT_full_part3.md`
- `panel/blueprint_gap/GAP_REPORT_full_part4.md`
- `panel/blueprint_gap/GLOBAL_PICTURE.md`
- `panel/blueprint_gap/GLOBAL_PICTURE_sources.md`
- `panel/blueprint_gap/progress_global_picture.md`
- `panel/blueprint_step4/BRIEF.md`
- `panel/blueprint_step4/architect.md`
- `panel/blueprint_step4/developer.md`
- `panel/blueprint_step4/scientist.md`
- `panel/blueprint_step4/user.md`
- `panel/brief_joins_gallery.md`
- `panel/brief_na_default_formulas.md`
- `panel/brief_view_vs_export.md`
- `panel/dialog_preview/PROPOSAL_for_eve.md`
- `panel/dialog_preview/facts_and_times.md`
- `panel/engine_boundary/FACTS.md`
- `panel/engine_boundary/TABLE_FOR_THE_OWNER.md`
- `panel/engines/PLAN_engine_fields_for_eve.md`
- `panel/engines/REPORT_for_eve.md`
- `panel/export_value/findings.md`
- `panel/key_types/viewpoint_scientist.md`
- `panel/lab_step4/BRIEF.md`
- `panel/lab_step4/architect.md`
- `panel/lab_step4/developer.md`
- `panel/lab_step4/scientist.md`
- `panel/lab_step4/user.md`
- `panel/na_rule/gap.md`
- `panel/recipe_arguments/REPORT_for_eve.md`
- `panel/recipe_places/BRIEF.md`
- `panel/recipe_places/TABLE_FOR_THE_OWNER.md`
- `panel/recipe_places/architect.md`
- `panel/recipe_places/scientist.md`
- `panel/recipe_places/user.md`
- `panel/recipe_versions/FACTS_NAME_DATE.md`
- `panel/records/corrections.md`
- `panel/round7/original_vs_audit_recipe.md`
- `panel/sessions/PROPOSALS_for_eve.md`
- `panel/sessions/scout_what_is_decided.md`
- `panel/step_order/findings.md`
- `panel/steps_position_help/PROPOSAL_for_eve.md`
- `panel/verify/results.md`
- `panel/viz/brief_viz_standard.md`
- `panel/viz/survey_impact.md`
- `panel/viz/survey_state.md`
- `panel/viz/verify/results.md`
- `panel/viz_rename/q6_the_15_objects.md`

## What the live ledger, tasks, rules and handoff cite
They cite `design/studies/` as the place where studies live (rule), the three kept study folders, and the text names of scratch pages (for example `uncertainty_catalogue`, `permanent_documents`) without a path. No citation of a path in `scratch_records_2026-11/` exists in the ledger, the tasks, the rules, the handoff or the code, except the folder-level mention in handoff line 53 (the account of the copy of 2026-11-25), which stays true: the folder is now at `.claude/outdated/design/studies/scratch_records_2026-11/` and the old folder holds a pointer README.

## Left for the owner (cannot judge)
1. Is `whole_picture_2026-11/sources/` (115 files, evidence of kept documents) to be moved once the whole picture is built? Needs: her reading of whether the run registers and tables are still wanted at hand.
2. Should `lineage_scope_2026-11/` (78 files, including 42 files of check scripts and drawings under `scratch/` and `review_text_style/`) move after the lineage decisions are built?

## Totals (after the fix round, 2026-11-26)
| | Files |
|---|---|
| Studies before | 859 |
| Kept in place (staruml 1, whole_picture 8 + 115, lineage_scope 78) | 202 |
| Kept because an open task waits on it (scratch_records) | 502 |
| Moved to `.claude/outdated/design/studies/` | 155 |
| Pointer files left at old paths | 30 (plus the README of the kept scratch folder) |
| Files in `.claude/design/studies/` now | 735 |
Check: 1 + 8 + 115 + 78 + 657 = 859; 502 + 155 = 657.
