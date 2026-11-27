# Guardrails of HOME and the audit

**What this page is.** The one place (Eve, 2026-11-27, ledger D-0696) that lists every guardrail that protects the user from a wrong result in HOME and the audit: what it protects from, what the user sees, where it is in the code, which test proves it, which decision it comes from, and whether it is built. A guardrail that is only decided, and a known hole, are rows too (state column).
**Who keeps it.** Every agent that adds, changes or removes a guardrail updates its row in the same change. Known holes are also on `current_limits.md` (the limits of the app): this page points there, it does not copy the text.
**Last check:** 2026-11-27, on `dev` at 8d32cf1e. Every "Where" was opened; every test was found by grep and its name read, not run again (the suites were run by the reviewers of the merges). Words quoted are PROVISIONAL unless a decision says otherwise.
**State words:** built / decided, not built / a known gap. "No test found" is a task, not a pass.

## 1. A stored table is only served under its key

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| A stale or foreign table (old recipe, old data) shown as the current one | Nothing; the table is built again. If it cannot be built under its key: "The audited table ... was changed by another session on the same recipe and data and could not be built again here. Reload the page and look again." | `app/modules/cache_keys.py` (keys); `orchestrator.py:568` (`read_anchor_if_key`); `audit_run.py:139` (`_stored_scan`: the key in the file must equal the key wanted) | `test_stale_key_store.py::test_the_author_changes_the_recipe_back_and_the_table_of_the_other_recipe_is_not_served`; `test_cache_chain.py` (data / included-file / step change rebuilds); `test_audit_shared_folder.py::test_session_b_never_reads_the_table_session_a_stored_in_the_shared_folder` | ADR-089, ADR-101, D-0025 | built |
| A table stored by one browser tab served to another tab (two tabs on one recipe) | Nothing | same `_stored_scan` | same last test | D-0025 | built (the shared folder itself is a known gap, G8) |
| A table of an audit trial taken as an applied one | Nothing; a trial table moves to the audit folder only when the key in its file equals the key now wanted | `app/modules/audit_trial.py:341` (`apply_trial`) | `test_audit_trial.py::test_a_stored_table_moves_only_when_its_key_is_the_key_now_wanted_never_by_name` | D-0656 | built |

## 2. The export holds what the user validated

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| Exporting from other files than the ones looked at | No export; a zip with only `EXPORT_NOT_CREATED.txt`, a notice, "reload (F5), check, export again" | `app/handlers/export_handlers.py:263` (`changed_since_view`), `:290` (`blocked_export_notice`), `:327` | `test_export_view_consistency.py::test_a_data_change_after_the_view_is_reported`, `::test_the_refusal_text_explains_what_it_means_and_what_to_do` | ADR-089; contract 7.2 rule 1 | built |
| Exporting a recipe that is no longer available | The same file, with the reason and the contact | `app/modules/export_refusal.py:22` | `test_export_refusal.py::test_a_recipe_rejected_by_the_gate_is_refused_with_its_problems_and_contact` | ADR-094 | built |
| An exploration filter or a trial reaching the export | The export is the same whatever the screen shows; the README says the mode and the view | `export_handlers.py` (exploration is never an argument; `:1549`) ; trial folder never read (section 7) | `test_export_unchanged_by_the_view.py::test_the_content_does_not_depend_on_the_view` | D-0327, D-0005 | built |
| An audit step that cannot be written as a recipe step being lost silently | No audit recipe; `audit_recipe/ERROR.txt` and a notice; the rest of the bundle is complete | `app/modules/audit_places.py` (`audit_recipe_of`); contract 7.2 rule 10 | `test_audit_recipe_runs_alone.py`; `test_audit_places_export.py` | D-0622, D-0535 | built |

## 3. The view the user looks at is the view the step is made on

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| A column drop that did not change the key of the view (a stale table shown after a drop) | The table shown follows the columns kept | `app/modules/audit_place_view.py:254` (`columns_digest`), `:260` (`view_identity`) | `test_audit_place_view.py::test_a_column_drop_changes_the_identity_when_the_columns_are_given_and_a_row_filter_does_not` | D-0662 | built |
| A condition built on one table tried or added on another | "This condition was built on another table than the one shown. Show that table, or build the condition again here. Nothing was tried." | `app/modules/t3_audit_engine.py:688-691` (`BUILT_ELSEWHERE_LINE`, `rows_built_elsewhere`); `app/handlers/trial_handlers.py:184` | `test_audit_try.py::test_a_condition_is_never_used_on_a_table_other_than_the_one_it_was_built_on` | D-0178, D-0311 | built |
| A condition tried at a place where its column is absent or of another type | The place is named with the reason; nothing is tried; no place is dropped silently | `app/modules/audit_try.py:77` (`fit_problem`); `audit_place_view.py:290` (`condition_fits`) | `test_audit_try.py::test_a_condition_that_does_not_fit_a_place_chosen_is_named_and_nothing_is_tried`; `test_audit_place_view.py::test_a_condition_fits_a_place_only_when_the_column_is_there_with_the_same_type` | D-0351, D-0352 | built |
| A selection that does not hold the table shown | "Show your selection first" (a refusal, nothing is tried) | `audit_try.py:54` (`trial_places`) | `test_audit_try.py::test_a_selection_that_does_not_hold_the_place_shown_is_refused_in_the_words_of_show_your_selection_first` | D-0655 | built |
| Exploration filters changing a plot, or staying after the table changed | Exploration changes only the data table viewed; staged and applied filters are cleared with a notice when the viewed table or the mode changes; they stay when a plot reads the same table | `app/handlers/filter_and_audit_handlers.py:168` (`_clear_exploration_filters`), `:190` | `test_filters_cleared_on_view_change.py::test_a_change_of_the_view_clears_the_staged_and_the_applied_filters_and_says_so`, `::test_a_plot_on_the_same_table_keeps_the_staged_and_the_applied_filters_and_says_nothing` | D-0311, D-0327, D-0361, D-0505, D-0506 | built |

## 4. Where a step may be written

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| Two places on one path (the step applied twice, rows counted twice); a place that is not allowed | A plain line naming both places; nothing is tried. The first places of several original tables may be chosen together | `libs/utils/src/utils/recipe_graph.py:467` (`chosen_places_problem`); `audit_try.py:54` | `libs/utils/tests/test_rule_of_places.py::test_one_place_below_another_is_refused_with_both_named_in_either_order`, `::test_the_tier1_places_of_the_original_tables_together_are_valid` | D-0553, D-0662 | built |
| A step written at the metadata (personal data, the ids of the study) | "The metadata table is not a place for an audit step: no audit operation is made on it ..." (also for a stored step at read) | `libs/utils/src/utils/recipe_tiers.py:37` (`METADATA_NOT_A_PLACE`) | `test_audit_try.py::test_two_places_on_one_path_the_metadata_and_nothing_shown_are_refused_in_plain_words` | D-0632 | built |
| Dropping a key column that a later join reads (the join would fail or lose rows) | "Cannot drop ... A join needs its key column ... Use a row filter or a removal by key instead, or drop the column after the join ..." (refused at Try; also by the audit check AU04) | `libs/utils/src/utils/key_drop.py:125-136`; `recipe_check.py:606` (AU04); `app/handlers/trial_handlers.py:206` | `libs/utils/tests/test_key_drop.py::test_the_gate_refuses_where_a_join_is_later_and_allows_where_it_is_not_with_the_sentence_of_the_rule`; `test_audit_check_with_registry.py` | D-0358, D-0371, D-0448 | built |
| A removal written in a form the engine does not know (an old step type taken as a no-op) | The recipe or session is refused and the step is named; never skipped | `libs/utils/src/utils/audit_copy.py:354` (`integrity_errors`) | `test_removed_audit_step_type.py::test_an_audit_list_with_the_removed_type_is_refused_and_names_the_step`, `::test_the_removed_type_is_never_ignored_even_as_the_only_step` | D-0665 | built (a bundle import with an unknown type: no test found, task) |
| A step that cannot run being skipped silently | One plain error that names the step and its place, at every plot it breaks | `app/modules/audit_run.py` (`AuditRunError`) | `test_audit_step_refused_not_skipped.py`; `test_audit_error_names_the_plot.py` | contract section 12a | built |

## 5. A trial changes nothing; an added step needs a reason

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| A tried step leaking into the session, the export, the audit folder or a stored key | Nothing; the trial lives in a folder of its own, emptied at discard, apply, every change, leaving Audit mode, restore, change of recipe and at app start | `app/modules/audit_trial.py:153` (`clean_trials`); `bootloader` start | `test_audit_trial.py::test_the_placeholder_reason_is_in_no_file_no_session_no_export_and_the_callers_nodes_are_not_changed`, `::test_discard_and_apply_and_a_failed_trial_leave_no_trial_folder`, `::test_the_start_of_the_app_removes_every_trial_folder_a_killed_process_left_and_touches_nothing_else` | D-0656, D-0302 | built |
| A failed "Add to audit pipeline" leaving a half step | Nothing is applied, the trial ends, a plain line says so | `audit_trial.py:341` | `test_trial_add_dependencies.py::test_a_failed_apply_leaves_nothing_applied_ends_the_trial_and_says_so` | D-0672 | built |
| A step added with no reason | The button is disabled: "Write a reason to add this step. A step is never added without one." | `app/modules/audit_add.py:30` | `test_trial_add_dependencies.py::test_add_without_a_reason_applies_nothing_and_keeps_the_trial` | contract section 3 (the gatekeeper) | built |
| A second click adding the step twice | Nothing is added | `app/handlers/trial_handlers.py` | `test_trial_add_dependencies.py::test_a_second_click_adds_nothing` | D-0672 | built |
| "User verified" taken as a guarantee | The mark is advice; it blocks nothing; each node records whether its place was marked; who marked is not recorded | `audit_add.py:26` | `test_audit_add.py` | D-0662, D-0669, D-0670 | built (who: a known gap, G11) |

## 6. Sessions

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| Steps of one recipe applied to another recipe with a table of the same name | The steps are set aside per recipe; they come back with their recipe | `app/handlers/home_theater.py:1834` (`_steps_set_aside`) | `test_audit_steps_survive_recipe_change.py::test_the_steps_of_one_recipe_are_not_applied_to_another_recipe_with_a_table_of_the_same_name` | D-0317 | built |
| A session of another recipe restored | "Session ... belongs to the recipe ..." ; nothing is applied | `app/modules/session_manager.py:233`; `app/handlers/session_handlers.py:605` | `test_session_format_and_recipe.py::test_a_session_of_another_recipe_is_refused_and_nothing_is_applied` | D-0317 | built |
| A session file of another format read and converted wrongly | "... was saved by an older version of the app and cannot be opened. Delete it and start a new session." (the whole file, never converted; format 6) | `session_manager.py:215`, `:218` | `test_session_format_and_recipe.py::test_the_direct_read_refuses_a_save` | D-0312, D-0665 | built |
| A bundle audit checksum under the old structure being compared | The leg says it cannot be compared; the other legs are checked | `app/modules/bundle_importer.py` (`steps_detail`) | `test_bundle_importer.py` | ADR-097 | built |
| Steps made on other data applied to the data now loaded (Restore of a session saved on other data) | Only the warning "Session was saved against a different data batch ..." then the steps are applied | `session_handlers.py` (restore); `home_theater.py:2013-2075` | no test of a guard | D-0317 (decided: warn only for the same recipe) | a known gap, G1 (slice D5) |

## 7. The ids

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| Tables whose entity ids differ giving silent wrong joins | Missing ids are added as lines with a yes/no marker (nothing removed or changed); three checks are warnings, written to the log of the ids | `libs/utils/src/utils/id_completion.py:272` (`complete_table`), `:363` (`build_report`); `app/modules/id_check_run.py` | `libs/utils/tests/test_id_completion.py`; `test_id_checks_log.py::test_the_log_is_written_in_a_folder_of_the_user_folder_with_the_numbers_and_the_unmatched_ids` | D-0572 to D-0599, D-0613 | built |
| The warning being unseen | A red block above the tabs with "I have read this"; the click is written in the log with no person; the export says what was found | `app/handlers/id_warning_handlers.py` | `test_id_warning.py::test_a_click_is_written_in_the_log_with_the_date_and_no_person_and_is_read_back_for_the_same_recipe_and_data`; `test_id_warning_browser.py` | D-0582, D-0585, D-0613 | built |
| A recipe that declares the ids wrongly | Recipe check codes E03 (id of a number type), E04 to E07 (the completion block), S10 (metadata with no data table), J16 (the metadata must be joined onto a data table with a left join), J17 (metadata listed in a join with no join step) | `recipe_check.py:483, 401, 942, 964`; `id_completion.py:130-134` | `libs/utils/tests/test_recipe_check_entity_key_type.py`; `test_recipe_check_metadata_declared.py`; `test_recipe_check_metadata_join.py`; `test_id_completion.py` | D-0225, D-0586, D-0633, D-0636, D-0637 | built |
| The audit copy being taken for a clash of plot ids; the original named wrongly | I04 (`info.audit_of` must name an existing original), GP07 (a Gallery example may not carry it), P07 (one plot id in two groups of one recipe), X5 (one plot id in two recipes) | `recipe_check.py:334, 1336, 1189, 1394` | `libs/utils/tests/test_recipe_check.py` (I04, GP07; `test_the_same_plot_id_in_two_recipes_is_x5`, the audit recipe sets) | D-0534, D-0690 | built (X5 is not run by the app at start: G7) |

## 8. Opening a recipe and bringing in data

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| A broken recipe being selectable | It is listed under "rejected" with the problems and a contact; it can never be the default | `app/src/bootloader.py:191-199` (the load gate) | `test_data_analysis_recipe_load_gate.py::test_a_recipe_that_fails_structure_is_excluded_and_recorded`, `::test_a_recipe_that_fails_data_contract_is_excluded_and_recorded` | ADR-094 | built (the split of the two checks: decided, not built, D-0698) |
| A recipe with a plot that cannot be drawn being opened | The recipe is refused at opening with a sentence naming the plot | `app/modules/opening_build.py:146` (`draw_plot_proof`) | `test_opening_build.py::test_a_plot_that_cannot_be_drawn_refuses_the_recipe_with_a_sentence_that_names_it` | D-0326, D-0327, D-0335 | built |
| A plot of very many rows hanging the browser unannounced | "The plot '...' receives N rows (more than 1,000,000). ... nothing is refused. Suggestion: count or aggregate in the recipe first ..." | `opening_build.py:114` (`large_plot_warning`) | `test_opening_build.py::test_the_warning_is_above_the_number_not_at_it_and_nothing_is_refused` | D-0336, D-0363 | built |
| An upload that the app cannot read later | A file is accepted only if the ingestion reads ALL of it; all files or none; the refusal is the ingestion's own reason | `app/modules/data_import_check.py` (the check), `:163` (a deployment that finds data by table name is refused), `:47` (an imported recipe is refused) | `test_data_import_check.py::test_the_file_with_slug_headers_is_refused_with_the_ingestions_reason_and_nothing_is_written`, `::test_store_all_refuses_a_refused_verdict`, `::test_a_recipe_imported_from_a_bundle_is_refused_and_nothing_changes`, `::test_a_csv_with_the_recipes_own_headers_is_refused_not_copied_raw_over_the_tsv` | D-0034, D-0434 | built (the refusals of a deployment by table name and an import are PROVISIONAL, D-0439, D-0440) |

## 9. Reproducibility

| Protects the user from | The user sees | Where | Test | Decision | State |
|---|---|---|---|---|---|
| A random plot layer giving another picture each time | A layer with `random_state: null` or the word `random` is refused; every seed used is written in the recipe or the audit recipe | `libs/viz_factory/src/viz_factory/viz_factory.py:86` (`_refuse_unseeded_layer`); the checker (PS04, PD01) | `test_plot_seeds.py::test_every_place_draws_the_picture_of_the_seeds_each_layer_must_get`; `libs/viz_factory/tests/test_reproducible_render.py`; `libs/utils/tests/test_random_layers.py` | ADR-090, D-0056 | built |
| A Reshuffle that changes the picture without a record | Offered only in Audit mode; hidden when the recipe fixes the seed; the pin is recorded | `app/modules/plot_seeds.py` (`reshuffle_offered`); `plot_config_resolver.py:226` (`fixed_seed_of`) | `test_reshuffle_audit_only.py::test_with_a_pin_stored_the_exploration_plot_is_drawn_without_it_and_the_audited_plot_with_it` | D-0341, D-0052 | built |
| Rows in another order after a group-by, a join or a sort | A rule per action (`maintain_order`, `keep="first"`) | `libs/transformer` actions | `libs/transformer/tests/test_deterministic_order.py` | ADR-090 | built |

## 10. Known gaps (each also on `current_limits.md`; a row there says what the user sees)

| Id | The gap | Where it is | Test | Decision / task | State |
|---|---|---|---|---|---|
| G1 | At Restore of a session saved on other data the app warns and then applies the steps; new steps are saved under the key of the current data: steps can mix across datasets | `session_handlers.py`; `home_theater.py:2013-2075` | none | slice D5 of HOME-DEMO-UPLOAD | a known gap |
| G2 | An upload replaces the recipe's data file with no copy and no record of the name; it makes a new session by itself without asking | `data_import_check.py`; `home_theater.py:_sync_session_provenance` | none | D1 to D4 of HOME-DEMO-UPLOAD; SESSIONS-OPTIONS-PAGE | a known gap |
| G3 | A file with CR-only line endings reads as zero rows, no message (RAN in scratch, 2026-11-27) | the ingestion reader | none | D6; SESSIONS-OPTIONS-PAGE (refuse or warn) | a known gap |
| G4 | A non-breaking space inside an id is not removed by `strip`: the id is reported missing, with no hint | the ingestion reader | none | D6 | a known gap |
| G5 | The id rules read ONE id column per table (the first declared); a pair table with one declared id gets a false added line | `id_completion.py:211` | none | ID-LIST-OF-ID-COLUMNS (option A) | a known gap |
| G6 | Ids are checked and completed only before tier 1; a table whose id appears at tier 2 gets no check | `id_completion.py:8` | none | ID-AT-THE-TIER-IT-COMES-INTO-BEING | a known gap |
| G7 | The plot-id check across recipes (X5) is not run by the app at start (only the Gallery manager calls it) | `gallery_manager.py:114` | the check has tests, the app call has none | not decided | a known gap |
| G8 | Two app processes on one user place empty each other's trial folders; two tabs share one audit folder | `audit_trial.py:147-160` | none | not decided | a known gap |
| G9 | A one-row table joined by a cross join: 2 rows double every row, 0 rows empty the table, nothing warns. RAN at the Polars level (3 rows crossed with 0, 1, 2 rows gave 0, 3, 6); NOT run through the app | the engine | none | RECIPE-ROW-COUNT-ASSERT (after the demo) | a known gap (app path not run yet) |
| G10 | A recipe step runs a formula with `eval` after a check against a list of names and with no builtins: mechanism READ at `formula_check.py:508-518`; the risk is NOT re-verified | `formula_check.py` | the checker has tests; no test of an escape | PROTOTYPE-SAFE-SHARING-STUDY | a known gap (not re-verified) |
| G11 | Who marked "User verified" is not recorded (no user identity) | `audit_add.py` | none | D-0677, D-0670; AUDIT-WHO-IN-USER-VERIFIED | decided, not built |
| G12 | The audit log with its size warnings is not built; the audit log is not in the export | none | none | D-0478, D-0679, D-0682, D-0689 | decided, not built |
| G13 | The split of the structure and data checks (D1); no recipe selected at start (D2); the record of each upload (D3); the choice at upload (D4) | none | none | D-0698 to D-0701 | decided, not built |
