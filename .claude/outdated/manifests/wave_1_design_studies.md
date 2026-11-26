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
| `whole_picture_2026-11/` (8 documents at the top) | 9 | KEEP | `WHOLE_PICTURE.md` is the one actualised document (D-0605) and says which of the other seven are current; code (`id_completion.py`, `id_log.py`, `audit_places.py`, `test_id_completion.py`), the dependency index, `demo_deliberate_oddities.md`, `agent_dispatch_howto.md` and ledger D-05xx cite them. UPDATE (not done here, listed): `DESIGN_AGREED_AND_QUESTIONS.md` is superseded in part by the recheck table of `PATHS_AND_DERIVED_AGREED.md` (its own header and `WHOLE_PICTURE.md` line 24 say so); `GOALS_REVIEW.md` is historical for its dialog and questions (`WHOLE_PICTURE.md` line 21); `RECIPE_PROPOSAL_refined.md` is a proposal NOT confirmed (D-0496) | the ledger, `WHOLE_PICTURE.md` | code, knowledge, workflows, ledger |
| `whole_picture_2026-11/sources/` | 115 | KEEP | The evidence (run registers, tables, retest outputs) that the kept documents name by path in their own text (for example `sources/design_dialogue/RUN_REGISTER_*.md`, `sources/whole_picture/RETEST_her_scope.md`); moving it would break the kept study. Revisit when the kept study is next actualised | | the kept documents; `knowledge/demo_deliberate_oddities.md` cites `sources/tmp_2026-11-23/dry_run_big_move_report.md` |
| `lineage_scope_2026-11/` | 78 | KEEP | The lineage research the handoff lists as "RESEARCH DONE, waiting for the owner" (open state, lines 13, 73) and ledger D-0507 names; the demo work on the lineage is running. Revisit after the demo | decisions D-0627 to D-0637 are in the ledger; the pages stay as the evidence | handoff, ledger |
| `scratch_records_2026-11/` | 657 | OUTDATED | Scratch copied on 2026-11-25 from `tmpAI` and `tmp` (panel answers, builder and reviewer reports, briefs, progress notes of closed slices). The README of the folder says: nothing here is a decision. The decisions are ledger lines; the built behaviour is in the code, the rules and the ADRs. The only live citations are by 61 files in `.claude/design/` (wave 2) | the ledger (D-0001 to D-0637), `.claude/knowledge/architecture_decisions.md`, the rules, git history | 61 files and 10 folders, below |

The three folders marked KEEP are checked again in a later wave (after the demo): the lineage research and the whole-picture evidence move when their decisions are built and the handoff no longer waits on them.

## `scratch_records_2026-11/` by group (all OUTDATED)
| Group (under `scratch_records_2026-11/`) | Files | Verdict | Who still links to it |
|---|---|---|---|
| `(top-level files)` | 3 | OUTDATED | no live link |
| `controls_8f951761/` | 3 | OUTDATED | no live link |
| `coordinator/` | 19 | OUTDATED | no live link |
| `coordinator/app_features_name` | 4 | OUTDATED | no live link |
| `coordinator/audit_folder_name` | 1 | OUTDATED | no live link |
| `coordinator/blueprint_verify` | 7 | OUTDATED | no live link |
| `coordinator/briefs` | 2 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-18_test_lab_review.md` |
| `coordinator/browser_tests_cause` | 1 | OUTDATED | no live link |
| `coordinator/data_file_cut` | 1 | OUTDATED | no live link |
| `coordinator/data_import_check` | 1 | OUTDATED | no live link |
| `coordinator/data_import_questions` | 1 | OUTDATED | no live link |
| `coordinator/data_import_review` | 1 | OUTDATED | no live link |
| `coordinator/data_import_review2` | 1 | OUTDATED | no live link |
| `coordinator/default_data` | 3 | OUTDATED | no live link |
| `coordinator/drop_uncertain` | 2 | OUTDATED | no live link |
| `coordinator/gallery_fixes_review` | 4 | OUTDATED | no live link |
| `coordinator/gallery_picture_key_review` | 40 | OUTDATED | no live link |
| `coordinator/gallery_walk_2026-11-20` | 1 | OUTDATED | no live link |
| `coordinator/gate_gap_cause` | 1 | OUTDATED | no live link |
| `coordinator/home_data_picker` | 2 | OUTDATED | no live link |
| `coordinator/lbfb_review_1` | 1 | OUTDATED | no live link |
| `coordinator/lbfb_review_3` | 1 | OUTDATED | no live link |
| `coordinator/ledger_words_check` | 2 | OUTDATED | no live link |
| `coordinator/names_pass_plan` | 4 | OUTDATED | no live link |
| `coordinator/opening_build_control` | 10 | OUTDATED | no live link |
| `coordinator/opening_build_control2` | 4 | OUTDATED | no live link |
| `coordinator/panel_statistician_draft` | 1 | OUTDATED | no live link |
| `coordinator/panel_widths_review` | 1 | OUTDATED | no live link |
| `coordinator/permanent_documents` | 1 | OUTDATED | no live link |
| `coordinator/picture_tests` | 1 | OUTDATED | no live link |
| `coordinator/plot_rows_dropped` | 1 | OUTDATED | no live link |
| `coordinator/recipe_name_rule` | 1 | OUTDATED | no live link |
| `coordinator/remove_from_all_review` | 1 | OUTDATED | no live link |
| `coordinator/remove_from_all_review2` | 1 | OUTDATED | no live link |
| `coordinator/report_by_group` | 1 | OUTDATED | no live link |
| `coordinator/slice_b_final2` | 2 | OUTDATED | no live link |
| `coordinator/slice_c1_final` | 1 | OUTDATED | no live link |
| `coordinator/slice_c1_final3` | 7 | OUTDATED | no live link |
| `coordinator/smoke_preview_filter` | 1 | OUTDATED | no live link |
| `coordinator/uncertainty_catalogue` | 1 | OUTDATED | no live link |
| `engine_keys/` | 29 | OUTDATED | cited by 4 file(s): `design/blueprint_revision/01_sources.md`, `design/blueprint_revision/02_planned_vs_existing.md`, `design/blueprint_revision/03_parked_items_and_known_gaps.md`, `design/blueprint_revision/prior_work/BLUEPRINT_T1_T2_PROOF.md`, `design/blueprint_revision/prior_work/GLOBAL_PICTURE_sources.md`, `design/blueprint_revision/prior_work/TIER3_facts_2026-11-18.md`, `design/blueprint_revision/prior_work/step4_REVIEW.md`, `design/lab_revision/prior_work/README.md`, `design/lab_revision/prior_work/step4c_report.md` |
| `panel/` | 5 | OUTDATED | cited by 3 file(s): `design/decisions_2026-11-14/proposals_for_eve.md` |
| `panel/adr` | 4 | OUTDATED | cited by 2 file(s): `design/decisions_2026-11-14/adr_sync_changes.md`, `design/home_redesign_intent_and_consequences.md` |
| `panel/adr_history` | 110 | OUTDATED | no live link |
| `panel/audit_docs` | 1 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-16_audit_step_position_and_dialog_help.md` |
| `panel/audit_model` | 22 | OUTDATED | cited by 2 file(s): `design/exploration/2026-11-16_audit_rules.md` |
| `panel/audit_recipe_file` | 4 | OUTDATED | no live link |
| `panel/audit_redesign` | 3 | OUTDATED | no live link |
| `panel/audit_rules` | 1 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-16_audit_rules.md` |
| `panel/author_manifest` | 1 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-17_author_manifest.md` |
| `panel/axis_text` | 3 | OUTDATED | no live link |
| `panel/blueprint_gap` | 8 | OUTDATED | cited by 8 file(s): `design/blueprint_revision/01_sources.md`, `design/blueprint_revision/prior_work/GAP_DIGEST_for_eve.md`, `design/blueprint_revision/prior_work/GAP_REPORT_full_part1.md`, `design/blueprint_revision/prior_work/GAP_REPORT_full_part2.md`, `design/blueprint_revision/prior_work/GAP_REPORT_full_part3.md`, `design/blueprint_revision/prior_work/GAP_REPORT_full_part4.md`, `design/blueprint_revision/prior_work/GLOBAL_PICTURE.md`, `design/blueprint_revision/prior_work/GLOBAL_PICTURE_sources.md`, `design/blueprint_revision/prior_work/progress_global_picture.md` |
| `panel/blueprint_step4` | 5 | OUTDATED | cited by 5 file(s): `design/blueprint_revision/06_panel_brief.md`, `design/blueprint_revision/06_proposal_architect.md`, `design/blueprint_revision/06_proposal_developer.md`, `design/blueprint_revision/06_proposal_scientist.md`, `design/blueprint_revision/06_proposal_user.md` |
| `panel/check_on_select` | 1 | OUTDATED | no live link |
| `panel/column_labels` | 1 | OUTDATED | no live link |
| `panel/column_tracking` | 5 | OUTDATED | no live link |
| `panel/data_ids` | 4 | OUTDATED | no live link |
| `panel/data_import_words` | 1 | OUTDATED | no live link |
| `panel/default_ticks` | 4 | OUTDATED | no live link |
| `panel/deployment_io` | 13 | OUTDATED | no live link |
| `panel/deployment_no_user` | 9 | OUTDATED | no live link |
| `panel/deployment_standard` | 6 | OUTDATED | no live link |
| `panel/dialog_preview` | 2 | OUTDATED | cited by 2 file(s): `design/exploration/2026-11-16_dialog_preview_other_plots.md` |
| `panel/engine_boundary` | 6 | OUTDATED | cited by 2 file(s): `design/engine_boundary_map.md` |
| `panel/engines` | 8 | OUTDATED | cited by 2 file(s): `design/exploration/2026-11-17_engine_fields_plan.md`, `design/exploration/2026-11-17_engines_default_and_override.md` |
| `panel/export_box` | 7 | OUTDATED | no live link |
| `panel/export_modes` | 2 | OUTDATED | no live link |
| `panel/export_ready` | 3 | OUTDATED | no live link |
| `panel/export_simplify` | 8 | OUTDATED | no live link |
| `panel/export_value` | 1 | OUTDATED | cited by 1 file(s): `design/decisions_2026-11-14/briefs/brief_view_vs_export.md`, `design/decisions_2026-11-14/evidence/records_corrections.md`, `design/decisions_2026-11-14/proposals_for_eve.md` |
| `panel/formula_d` | 11 | OUTDATED | no live link |
| `panel/formula_night` | 2 | OUTDATED | no live link |
| `panel/formula_safety` | 3 | OUTDATED | no live link |
| `panel/gallery_check` | 3 | OUTDATED | no live link |
| `panel/gallery_study` | 9 | OUTDATED | no live link |
| `panel/gallery_taxonomy` | 5 | OUTDATED | no live link |
| `panel/gallery_verify` | 9 | OUTDATED | no live link |
| `panel/help_beside` | 8 | OUTDATED | no live link |
| `panel/id_vs_key` | 1 | OUTDATED | no live link |
| `panel/key_types` | 2 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-18_date_keys_and_joins.md` |
| `panel/lab_step4` | 5 | OUTDATED | cited by 5 file(s): `design/lab_revision/06_panel_brief.md`, `design/lab_revision/06_proposal_architect.md`, `design/lab_revision/06_proposal_developer.md`, `design/lab_revision/06_proposal_scientist.md`, `design/lab_revision/06_proposal_user.md` |
| `panel/label_trace` | 6 | OUTDATED | no live link |
| `panel/lbfb` | 6 | OUTDATED | no live link |
| `panel/lookup_table` | 1 | OUTDATED | no live link |
| `panel/na_rule` | 1 | OUTDATED | cited by 1 file(s): `design/decisions_2026-11-14/proposals_for_eve.md` |
| `panel/name_fields` | 1 | OUTDATED | no live link |
| `panel/names_whole_app` | 8 | OUTDATED | no live link |
| `panel/one_python` | 4 | OUTDATED | no live link |
| `panel/panel_widths` | 4 | OUTDATED | no live link |
| `panel/path_use_cases` | 4 | OUTDATED | no live link |
| `panel/polars_catch` | 1 | OUTDATED | no live link |
| `panel/recipe_arguments` | 6 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-17_recipe_arguments_without_code.md` |
| `panel/recipe_error_place` | 1 | OUTDATED | no live link |
| `panel/recipe_places` | 6 | OUTDATED | cited by 5 file(s): `design/blueprint_revision/01_sources.md`, `design/blueprint_revision/03_parked_items_and_known_gaps.md`, `design/blueprint_revision/prior_work/recipe_places/BRIEF.md`, `design/blueprint_revision/prior_work/recipe_places/TABLE_FOR_THE_OWNER.md`, `design/blueprint_revision/prior_work/recipe_places/architect.md`, `design/blueprint_revision/prior_work/recipe_places/scientist.md`, `design/blueprint_revision/prior_work/recipe_places/user.md`, `design/lab_revision/06_panel_brief.md` |
| `panel/recipe_versions` | 7 | OUTDATED | cited by 1 file(s): `design/blueprint_revision/prior_work/recipe_places/BRIEF.md` |
| `panel/records` | 1 | OUTDATED | cited by 1 file(s): `design/decisions_2026-11-14/proposals_for_eve.md` |
| `panel/round5` | 7 | OUTDATED | no live link |
| `panel/round7` | 46 | OUTDATED | cited by 1 file(s): `design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md`, `design/home_redesign_intent_and_consequences.md` |
| `panel/seed_ops` | 6 | OUTDATED | no live link |
| `panel/seed_step` | 2 | OUTDATED | no live link |
| `panel/session_import` | 7 | OUTDATED | no live link |
| `panel/sessions` | 2 | OUTDATED | cited by 2 file(s): `design/exploration/2026-11-16_one_recipe_many_datasets_sessions.md` |
| `panel/stat_function_polars` | 3 | OUTDATED | no live link |
| `panel/step_order` | 1 | OUTDATED | cited by 1 file(s): `design/decisions_2026-11-14/README.md`, `design/decisions_2026-11-14/briefs/brief_view_vs_export.md`, `design/decisions_2026-11-14/proposals_for_eve.md` |
| `panel/steps_position_help` | 1 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-16_audit_step_position_and_dialog_help.md` |
| `panel/test_speed` | 1 | OUTDATED | no live link |
| `panel/uml_sync` | 2 | OUTDATED | no live link |
| `panel/uploaded_data_place` | 4 | OUTDATED | no live link |
| `panel/validate` | 2 | OUTDATED | no live link |
| `panel/verification` | 18 | OUTDATED | no live link |
| `panel/verify` | 1 | OUTDATED | cited by 1 file(s): `design/decisions_2026-11-14/proposals_for_eve.md` |
| `panel/viz` | 4 | OUTDATED | cited by 4 file(s): `design/decisions_2026-11-14/briefs/brief_viz_standard.md`, `design/decisions_2026-11-14/viz_plan_for_eve.md` |
| `panel/viz_rename` | 5 | OUTDATED | cited by 1 file(s): `design/exploration/2026-11-17_recipe_arguments_without_code.md` |
| `panel/wide_split` | 1 | OUTDATED | no live link |
| `panel/write_test_at_start` | 2 | OUTDATED | no live link |
| `switch_check/` | 9 | OUTDATED | no live link |

## Pointers that this wave leaves (OUTDATED files that a live file cites)
At the old path of each file in the list `pointer_files` below, one line: "Moved to `.claude/outdated/...`". A `README.md` of the same kind stands at the old folder path for the cited folders. They are removed as wave 2 actualises the citing files in `.claude/design/` (the blocks `blueprint_revision`, `lab_revision`, `exploration`, `decisions_2026-11-14`, `engine_boundary_map.md`, `home_redesign_intent_and_consequences.md`, `uml_model_plan.md`).

Cited folders: the root of `scratch_records_2026-11/` and `panel/{blueprint_step4,engine_boundary,formula_safety,key_types,lab_step4,recipe_places,verify,viz,wide_split}/`.

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
