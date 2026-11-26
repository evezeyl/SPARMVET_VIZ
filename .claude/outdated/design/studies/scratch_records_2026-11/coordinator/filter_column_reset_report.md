# Report: the filter form puts the chosen column back (branch task/filter-column-reset)

Worktree `.claude/worktrees/filter-column-reset`, from dev `c21fbdc3`. Three commits: `082b0869` (fix), `593aac0d` (tests), `55bcc486` (dependency index). Worktree clean, no app running.
Labels: verified = I ran it or read it at file:line; reasoned = from reading only.

## What a user saw before
- In HOME, Filters panel: the user picks a column, and the box jumps back to the first column; the operator list follows. Nothing tells the user. Typing a value and pressing Add would then build a filter on the wrong column. (D-0050)
- When: right after a change of "Data to show" (Raw / Result / My view), when the column is chosen within about 0 to 40 ms of the change. How often (verified, scratch probe, qa): 10 of 30 tries before the fix (all three views toggled); 9 of 30 with only Result <-> My view toggled (the second series was run on the code with my fix switched off).
- Flags (qa.yaml): the form exists only with `interactivity_enabled` on; the defect does not depend on `t3_sandbox_enabled` or on ghost save (off in qa). Verified by running under qa only; I did not run another app features file.

## Cause (verified, file:line in the code before my change)
1. `filter_form_ui` read `_dialog_table()` directly (`app/handlers/filter_and_audit_handlers.py` ~303, 324, 333, 351). `_dialog_table` is a `reactive.Calc`. A Calc invalidates its readers every time one of its inputs invalidates, whether or not its result is the same (shiny 1.6.0 `reactive/_reactives.py` `_on_invalidate_cb`, read). So any recompute re-rendered the form.
2. The form keeps the user's column only if the server-side `input.fb_col` already holds it (isolated read, `filter_form_ui`). A render that starts before the server has received the user's click reads the old value and sends the old column back (reasoned from the code; shown by the 10/30 and 9/30 counts above).
3. Dependencies of `_dialog_table` (all verified by reading), and whether the re-render is NEEDED:
   - `active_home_subtab` (handler 276, 459): needed only if the new plot has other columns or types.
   - `tier_toggle` (handler 463; `home_theater.py` 311 via `_resolve_active_lf`): needed only when the table differs (Raw has no `era` column, Result has: real; Result <-> My view without audit steps: SPURIOUS).
   - `_dialog_audit_steps_changed` (handler 463): needed when the audited steps of the plot change.
   - `active_cfg()` (`home_theater.py` 238), recipe id input (273, 320), `data_refresh_trigger` (270, 319), the keys Calc (259): needed on a recipe or data change; spurious when the result has the same columns.
   Measured: a change of "Data to show" re-rendered `filter_form_ui`, `filter_type_ui`, `filter_op_ui`, `filter_value_ui` each time (probe counts).

## The fix
- `app/modules/t3_audit_engine.py`: two pure functions, `dialog_schema_signature(types, discrete)` (columns, types, order, discrete axes) and `dialog_rows_signature(lf, table_key)` (plan of the table plus the content key of the stored tables, ADR-089; a plan that cannot be read is never equal to another: a doubt means one more render, never a stale list).
- `filter_and_audit_handlers.py`: one Effect `_signal_dialog_table` sets two Values only when they differ (rule R3); `filter_form_ui`, `filter_type_ui`, `filter_op_ui` read the schema signal, `filter_value_ui` reads both, and all read the table fresh without subscribing (`_dialog_table_now`, same pattern as `test_dialog_mirror_window.py`). An error in the Effect is logged and shows as a changed signal, so the output re-reads and shows the error itself (no swallowed error).
- `home_theater.py`: one new keyword `_table_key` (the tier-1 key of the open recipe's keys). `@deps` of the handler and of `t3_audit_engine.py` updated; index regenerated (separate commit, see below).
- Rule R4 respected: the form does not read the widgets it mounts, apart from the existing isolated reads.

## What a user sees now
Changing "Data to show" between views that hold the same columns no longer mounts the form again. The column, operator and a staged value stay, and the element is the same one (checked by object identity in the browser). When the columns really change (Raw has no `era`), the form is built again and keeps the chosen column if it is still in the table. When the column is gone (another plot's table), it falls back to the first column, as before.

## Break-once evidence
- Fix switched off (outputs read the Calc again): the probe gave 9/30 resets; three new browser tests failed (mounted again; column put back to "source"; discrete year mounted again, 6 extra renders). Fix restored: all pass.
- Headless tests of the reactive pattern: the "reads the table" pattern renders on every recompute (asserted), the signal pattern renders 0 times for the same columns and once per real change.

## Counts (each once, qa, one process at a time, load checked before each run: all under 3)
- `test_filter_form_survives_rerender.py`: 20 passed (15 headless, 5 browser).
- `test_filters_cleared_on_recipe_change.py`: 13 passed. `test_shiny_apply_blocked.py`: 1. `test_shiny_filter_pickers.py`: 43. `test_shiny_filter_types.py`: 3. `test_shiny_filter_value_list.py`: 2. `test_shiny_na_tick.py`: 1. `test_shiny_session_restore.py`: 1. `test_export_inputs_survive_plot_tab.py`: 3. `test_export_download.py`: 9.
- `test_shiny_smoke.py` whole file: 37 passed, 3 skipped.
- `test_shiny_step_order.py`: first run 5 passed, 1 FAILED (`export_plot_format` radio "Clicking the checkbox did not change its state", an Export panel control, not the filter form); two more runs on my branch 6/6 and 6/6; one run on a copy of `c21fbdc3` 6/6. So: seen once, not reproduced, cause not investigated, probably unrelated (reasoned).
- A run of the smoke class `TestPreviewFiltersOnReferenceViews` selected alone with `-k` fails 3 tests on my branch AND on `c21fbdc3` (it needs the state left by earlier tests of the file); the whole file passes. Not mine, a property of the file.
- Ten runs in a row of the repaired sequence `test_shiny_apply_blocked.py` (uses `_choose_column_firmly`): 10 of 10 passed (20.3 to 21.0 s each). Ten runs of the new file: 10 of 10 passed (20 tests each).
- Headless: 682 passed (filter files, dialog, mirror window) and 921 passed (every other test file that imports `t3_audit_engine` or the handler and needs no browser). `from app.src.main import app` prints OK.
- `_choose_column_firmly` is now honest: one attempt, and on a reset it raises an AssertionError named "FORM RESET". No run printed or raised it.

## Decisions (builder's table)
| Decision | How the code complies | Where / test |
|---|---|---|
| D-0050 "No silent error: that is the rule" | The form no longer puts the column back silently for the spurious case; the helper no longer recovers silently; an Effect error is logged and shown by the output. The remaining case below is reported, not hidden. | handler `_signal_dialog_table`; `test_filter_form_survives_rerender.py`; `_choose_column_firmly` |
| D-0303 "if the coordinator uses the qa for testing it needs to ensure it does what he thinks he is testing" | qa flags named above; the new tests check the object identity of the select and the render counters, not only a value; the break-once run shows they fail. | `test_a_change_of_view_without_new_columns_...` |
| D-0285 "do not run the same tests that also cost time" | Each file run once; repeats only where asked (10 x) or to separate my change from the base (step_order, smoke subset). | counts above |

What happens to a staged value after this change (the consequence the brief names): it stays when the columns and rows do not change (verified in the browser: a list value on a text column, and on a discrete whole-number year both a list value and a typed number); it is dropped when the rows really change (the value widget is built from the rows).

## NOT fixed or not proven
1. **Remaining race, proven, not fixable cleanly on the server.** When the columns REALLY change (another plot, or Raw <-> Result) and the user picks a column while the server is still busy with that change, the server renders the new form with the column it knows (the old one) and the user's click is lost. Probe (scratch, before and after the fix, same result): switching the plot tab (QC <-> AMR group) and choosing `year` 0 to 300 ms later: reset in 15 of 15 tries; the plot change keeps the server busy for seconds. Cause (reasoned): the server cannot know a click that is queued behind its running flush. `update_select` without `selected` also resets to the first option, so changing the render into an update does not remove it (reasoned from Shiny's behaviour; not run). A client-side fix is excluded by the brief. This is the choice below.
2. A recompute that gives the same plan and the same tier-1 key but other rows (a table built in memory while its inputs changed, `_materialize_tier1` "returned, not stored") would not refresh the value list; the app already tells the user that inputs changed (reasoned, not run).
3. The Effect keeps `_dialog_table()` computed even when the Filters panel is not open (outputs are suspended when hidden, an Effect is not). The table is cached by key, so the cost is a read; I did not measure it.
4. Rule text: `ui_implementation_contract.md` section 14 (R4) has no line on the two signals. I did not edit rule files. Suggestion for the owner: add one line there.
5. The dependency index regeneration (commit `55bcc486`) also picked up entries that were stale before my change (export, session, gallery files); drop that commit and regenerate after the merge if it conflicts with another branch.
6. `ui_implementation_contract.md` / UML: I did not check `docs/UML/app.mdj` for a reactive-wiring diagram of the filter form (the sync law asks for it); not done.

## Choice left for the owner (it decides what the user sees)
When the columns really change and the user's pick is lost in the busy window (point 1), the options are:
- A. Accept it and tell the user in the documentation: the form is rebuilt after a plot change; choose the column after the plot has loaded.
- B. Make the window small: the server must not be busy for seconds on a plot change (a separate performance task; it shrinks the window, it does not remove it).
- C. Show a notice when the form was rebuilt and the column the server knew differs from the first column: the server cannot tell what the user clicked, so the notice would be a guess; I do not recommend it.
- D. A client-side hold of the user's last choice across the rebuild: removes the loss, but the brief and the project rule exclude client-side workarounds; only the owner can allow it.
Recommendation (reasoned): A with B as a task; D only if the owner accepts a client-side piece.

## Files
- `app/handlers/filter_and_audit_handlers.py`, `app/handlers/home_theater.py`, `app/modules/t3_audit_engine.py`
- `app/tests/test_filter_form_survives_rerender.py` (new), `app/tests/test_filters_cleared_on_recipe_change.py` (helper), `app/tests/test_shiny_apply_blocked.py` (comment)
- `.claude/knowledge/dependency_index.md` (regenerated)
- Scratch (not in git): `tmpAI/progress.md` in the worktree; run logs in the session scratchpad.
