# Review of task/switch-fixes (fb2ed369 on dev cd0a11d8)

Reviewer run, 2026-11-18. Worktree stayed clean (git status empty). Logs in this folder.

## Verdict: MERGE

Both fixes do what is decided. No contradiction found with ADR-099 point 1, D-0050. Two follow-ups for Eve or the next task, none blocks the merge (findings 1 and 2).

## Findings, by weight

1. MEDIUM, test gap (does not block). The test "the table of the new recipe is not filtered" never counts rows; it only checks empty filter lists (`app/tests/test_filters_cleared_on_recipe_change.py:79-98`). I checked the real thing in a browser (probe in `scratch/probe.py`, output in the table below): `1_test_data_ST22_dummy` unfiltered 42 rows; `sample_id in [first value]` applied: 1 row; switch to `2_test_data_ST22_dummy`: 70 rows = its unfiltered count (70); back to recipe 1: 42 rows. So the behaviour is right. A test should assert the count ("of 70" in `#home_data_preview .shiny-data-grid-summary`, as `test_shiny_step_order.py:111` does), because the empty-list check would still pass if a stale filter list were cleared in the panel but the table kept an old copy. Verified (run).
2. MEDIUM, existing defect found by the flake check, not caused by this branch. After the user switches to "My view" (T3) and picks a column in the filter form, a late re-render of the form can put the column back to the first one (`filter_form_ui`, `filter_and_audit_handlers.py:~300`, not in the diff). Evidence: my diagnostic copy of the test printed `fb_col= sample_id` right after `select_option("year")` in the failing runs, and an operator list that did not hold `lt`. The same failure happens on the dev handler without any of this branch's code (4 failures in 10 runs, `devdiag_*.log`). The user sees the column snap back. This is a new problem that needs Eve's decision (D-0165); the new test should at least wait for the form to settle (wait for the `lt` option before choosing it).
3. LOW. `previous == rid` in the guard of `_clear_filters_on_recipe_change` (`filter_and_audit_handlers.py:~182`) is not needed in the cases I could build. I removed it in a scratch copy and ran the Gallery and back round trip with an applied filter: filter kept, no notice, same result (`probe2`). Shiny does not re-send an equal value. The code comment ("the selector is re-created and reports the same id") is not shown by any test. The guard is harmless; the comment is unproven. Also no test breaks if `previous is None` is removed (first load has no filters, so nothing to clear and no notice).
4. LOW, Fix B and D-0050. `column_is_in_frame` returns an empty div without a log when the column is not in a built table (`filter_and_audit_handlers.py:~501-507`). I could find no way this stays empty for good: the column box (`filter_form_ui`) and the type, operator and value outputs are all built from the same table (`_dialog_table`) and fall back to the first column when `fb_col` is stale (`_selected_column`, line ~287), so the box is rebuilt and the counts output runs again. Ways the column can be absent and what the user sees: (a) stale `fb_col` after a recipe or plot change: one round empty, then the right text; (b) a column dropped by an audited step in My view: the box is rebuilt from `dialog_frame` too, same as (a); (c) table cannot be built (frame None): still goes to `dialog_lines`, logged and shown as "counts could not be computed"; (d) audit steps of the plot cannot run: `_active_frame` returns None, logged warning, as before; (e) table with no columns: `fb_col` empty, early return as before. Not checked: a table whose schema itself raises inside `column_is_in_frame` (no try there; it would show Shiny's red output error, not silence). Reasoned plus tests.
5. LOW, docs. `.claude/rules/ui_implementation_contract.md` section 8 does not say that exploration filters are cleared on a recipe change (ADR-099 point 1 does). `app/modules/t3_audit_engine.py` `consumed_by:` does not list the new test file (other tests are listed). The part of ADR-099 point 1 "cleared on a view change" is not built (the builder says so; I confirmed no effect clears on a view change). A decided behaviour not built: for Eve and the task list.
6. INFO. The T3-apply effect (`_clear_filters_on_t3_apply`, line ~1100) now reads `_pending_filters` and `_applied_filters` inside its `if`, so it gets a dependency for one extra run (the next run takes the other branch). Same values cleared, same order, no loop.

## Part 1 answers

1. Exactly what is decided? Yes. One function `_clear_exploration_filters` (`filter_and_audit_handlers.py:155-165`) sets staged then applied to `[]`, the order of the old code in all three callers: Send to Audit (`~729`), Reset button (`~735`, the two selectize/text updates after it are unchanged), T3 apply (`~1114`, same `if cnt > last` guard). The old callers raised no notice and still raise none; only the new effect notifies. Evidence: the diff; existing tests `test_filter_defects`, `test_filter_dialog_after_audit`, `test_shiny_filter_*` and `test_shiny_apply_blocked` pass in my runs. Nothing else in the diff (3 files: handler, engine, new test).
2. Reactive write discipline (`ui_implementation_contract.md` section 14): the write is only in `@reactive.Effect`; the read of the selector is outside `isolate`, the filter lists and `_seen_recipe` are read and written inside `reactive.isolate()`; no render writes. Cases:
   - first load: `previous is None`, nothing cleared, no notice. Probe: no notice at start.
   - reload of the same recipe: no input change, nothing. Probe (A to Gallery to Home, A selected): filter kept ("Apply (1)"), 1 row, 0 notices.
   - Gallery and back: same probe, filter kept.
   - fast A-B-A: the server sees each change that reaches it; B clears (correct, the filter was built on A); A has nothing to clear. If only the last value reaches it (A), nothing changed for the app. Reasoned, not run as a separate fast sequence.
   - recipe rejected by the load gate: the gate cannot select it. When the gate drops the open recipe it calls `update_select` (`recipe_gate_handlers.py:173`), which is a real change: filters cleared and the notice is shown next to the gate's own notice. Reasoned from code; not run.
   - session restore/import: `_restore_session` (`session_handlers.py:439-560`) sets only `home_state`, never the selector and never `applied_filters`; it did not touch the exploration filters before and does not now. Restored audited steps survive (not cleared by the new effect). Read.
   - metadata upload (`data_import_handlers.py`): does not change the selector; the filters of the same recipe survive the rebuild (as before; a filter on a column the new file lacks is the existing behaviour). Read, not run.
   - selector input missing (hidden by app features): `safe_input` gives None, effect returns; no change is possible there. Read.
3. Audited steps and `_pending_t3_nodes`: untouched (they live in `home_state`, not in the two lists). Test `test_audited_step_of_recipe_a_is_back_after_returning` passes 5 of 6 times (see 7). Column selector, tier choice, Export fields: no line of the diff touches them. Verified (diff).
4. See finding 4.
5. Notice: "The filters of the previous recipe were removed because the recipe changed (a filter is built on one recipe's columns). Audited steps are kept." Plain and true: the lists are emptied and audited steps are kept (tested). Shown once, never on first load, never when nothing was cleared (`filters_cleared_notice(0,0)` is None; test `test_no_filters_no_notice`). It also appears when the load gate switches the recipe (true, see 2). One sentence longer than needed; the wording is the builder's PROVISIONAL and is Eve's to reword.
6. Tests can fail: I broke the code in a scratch copy outside the worktree. (a) Clear disabled: `test_applied_filter_is_removed_and_noticed_once` fails. (b) `column_is_in_frame` always True: `TestColumnIsInFrame::test_present_and_absent` and `test_recipe_switch_with_a_column_chosen_logs_no_counts_error` fail. (c) Guard `previous == rid` removed: no test fails (finding 3). Row count check: finding 1.
7. Flaky test: 5 runs of the new file under qa: run 1 failed (1 failed, 11 passed), runs 2 to 5 passed (12 passed each). Failing test `TestRecipeSwitchClearsFilters::test_audited_step_of_recipe_a_is_back_after_returning`, assertion: `Locator.select_option: Timeout 30000ms` waiting for `lt` in `#fb_op` (`new_run_1.log:56-74`). Cause: the form column box was put back to another column by a late re-render after the T3 toggle (diagnostic: `fb_col= sample_id` after selecting `year`), so the operator list had no `lt`. It is both the test's wait (it does not wait for the form to settle) and a real form race of the existing app (finding 2). Not from this branch: the same single test, run 10 times against the dev handler, failed 4 times (`devdiag_*.log`); against the branch handler 1 of 8 in my diagnostic runs (`diag_*.log`) plus 1 of 5 above.
8. `@deps`: the handler `consumes:` and the engine `provides:` match the new names (`filters_cleared_notice`, `column_is_in_frame`). Missing: new test in the engine `consumed_by:` (finding 5). `build_dep_graph.py` not run by the builder (it says so). Nothing beyond the two fixes in the diff except the merge of four resets into one function.

## Part 2, the controls on fb2ed369 (python `.venv`, run from the worktree)

| Control | Result | Reference | Difference explained |
|---|---|---|---|
| `app/tests/test_imports_from_checkout.py` | 12 passed (code under test is the worktree's) | n/a | none |
| Headless, documented command (4 browser files ignored) | 10483 passed, 5 skipped, 32 xfailed, 2 warnings, 35m57 | 10471 / 5 / 32 | +12 = the 12 tests of the new file `test_filters_cleared_on_recipe_change.py` (see note) |
| Browser, qa: 15 `test_shiny_*.py`, `test_export_download.py`, `test_empty_data_analysis_recipe_startup.py`, new file | 147 passed, 1 failed, 3 skipped, 1 xfailed, 24m51 (152 collected) | 140 passed, 3 skipped, 1 xfailed | The failure is the known seed test of `test_export_download.py` (below). Collected without the new file: 140 = the 140 of the earlier report `controls_night` (136+3+1); I could not find which file makes the brief's 144; with the new file 12 more |
| `test_every_app_features_starts.py` alone | 9 passed, 1m43 | 9 starts | none |
| Seed test alone, 3 runs | pass, fail, pass | known flaky | `StopIteration` at `test_export_download.py:329` (no reproducibility recipe in the zip), same line as in the combined run. Not counted against the branch |
| `golden_baseline.py --check app/tests/golden/baseline.json` | `result-identical`, rc 0 | identical | none |
| `gallery_previews.py` (no `--apply`, out to this folder) | identical 34, size only 0, differs 0, new 0, error 0, rc 0 | 34 identical | none |
| `python -c "from app.src.main import app; print('OK')"` | OK, rc 0 | OK | none |

Note on the +12: the headless command does not ignore the new file, so its 12 tests ran there (headless +12 = 10471 to 10483, nothing else changed). The same file ran again in the browser command under qa (+12 there).

## Not checked

- A fast A-B-A switch and the load-gate-driven switch were not run, only read.
- The metadata upload path was read, not run.
- A table whose schema raises inside `column_is_in_frame` was not built.
- The view-change clearing (ADR-099 point 1, second half) is not built, so not tested.
- I did not read tmp.md. No installs. Scratch copy (outside the worktree) is `scratch/copy`; the seed flake cause was not investigated.
