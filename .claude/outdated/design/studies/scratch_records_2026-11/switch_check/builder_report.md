# builder report: switch-fixes (branch task/switch-fixes)

Commit: see `git log -1` on task/switch-fixes (fix(home): clear exploration filters on a recipe change...). Files: app/handlers/filter_and_audit_handlers.py, app/modules/t3_audit_engine.py, app/tests/test_filters_cleared_on_recipe_change.py.

## What the user sees now
- Switch recipe with staged or applied filters: both lists are emptied (Filters panel, "Apply (n)", right panel "Active Filters"), the table/plot of the new recipe are not filtered, and ONE warning notice says: "The filters of the previous recipe were removed because the recipe changed (a filter is built on one recipe's columns). Audited steps are kept."
- No filters: no notice. Audited steps are not cleared and are back on return to the first recipe.
- Filter form after the switch: column list is the new recipe's; a new filter can be staged (row index 0).
- Fix B: after a switch, the form's missing-value text no longer flashes "The counts could not be computed." and no KeyError goes to the server log.

## Fix A
One reset function `_clear_exploration_filters()` now used by Send to Audit, the Reset button, the T3-apply clear, and the new recipe-change effect (no second mechanism). The effect writes only inside a `@reactive.Effect`, with a guard: it acts only when the recipe id really differs from the last seen one (the selector is re-created and reports the same id when the user comes back from another space; that clears nothing). Pure rule `filters_cleared_notice(n_pending, n_applied)` in t3_audit_engine.py (None when nothing was cleared).
View-change part of ADR-099 point 1: NOT built and NOT built here. ADR-099 point 10 lists "one global list -> one list per (view, dataset)" as a change still to make, and no code clears on a view change (checked: no such effect). Needs its own task.

## Fix B: cause (fact, reproduced with tmpAI/repro/repro_b.py)
`filter_na_text_ui` asks `dialog_lines(_active_frame(), fb_col, ...)`. After a recipe change the frame is the new recipe's but `fb_col` still holds the old recipe's column ("year"; recipe 2 has "Year") for one reactive round, until the column box is rebuilt from the new table. `count_missing` raised KeyError, `dialog_lines` logged the traceback and the form showed "The counts could not be computed." for that moment. Without a switch (MLST Bar, year > 2050 stage and Send to Audit) the error did NOT occur. The final text was always right.
Fix: `column_is_in_frame(frame, col)`; if the column is absent from a built frame the output returns empty (it runs again when the box is rebuilt). A frame that is None (table cannot be built) still goes to `dialog_lines`, so a real failure is still logged and shown. This is one correct behaviour, so I did not need a choice.

## Tests (file app/tests/test_filters_cleared_on_recipe_change.py, 12 tests)
- 4 pure notice tests, 2 `column_is_in_frame` tests.
- Browser (qa): applied filter on sample_id then switch 1_test -> 2_test (no rows, no "(1)", no Active Filters, notice once); staged-only; no filters no notice (both directions); form usable after switch; audited step of recipe 1 not cleared, no notice, back on return ("year < 2050"); log check for fix B using its own server.
- Results: file 12 passed (several runs); with TestRecipeSwitchPlotRender + test_shiny_filter_value_list: 14 passed, 1 failed once (the audited-step test, timing, passed in 4 other runs; I raised its last wait to 20 s, not re-run after that). Headless neighbours: test_filter_operators, test_filter_defects, test_filter_dialog_after_audit, test_filter_dialog_values, test_imports_from_checkout, libs/utils test_missing_values: 274 passed.
- Break once: recipe-change clear disabled -> 2 browser tests failed (applied, staged), restored. `column_is_in_frame` guard disabled -> the log test failed; function returning True -> pure test failed; restored.
- Weak spot: the "table of recipe 2 is not filtered" is shown through the empty filter lists ("Apply" count, Active Filters), not by counting table rows.

## Not done / notes
- Findings 2, 3, 4 untouched. pyproject, pytest config, rule files, ADR text untouched. `@deps` of the two modules updated; build_dep_graph.py not run (dependency_index.md is generated; leave to the merge records step).
- No PROVISIONAL choices except the notice wording (plain, mine; Eve may reword) and its type "warning", 10 s.
- Decision check: D-0050 complied (no silent error: notice for the clear, the stale-column moment is no longer an error). D-0165: ADR-099 point 1 exists for recipe change; none for view change (reported above).
