# Recipe switching in HOME: check on dev d6c46cc7 (2026-11-18)

## Verdict
Yes with these cautions. Switching between all 7 offered recipes works: no error, no traceback from the switch, every recipe shows its own tabs, plot, banner, Info text and its own audit stack. But the filters you built on one recipe stay on the next recipe, and so do "My view" and the Export panel fields. A filter on a column both recipes have (for example sample_id) silently filters the other recipe. Demo advice: switch only with no filters in the Filters panel (press Reset first), and set "Result" for plot and data after switching.

## Offered recipes (qa, developer, pipeline-exploration-advanced: same list, no rejected recipe, the notes under the selector are empty)
1_Abromics_general_pipeline (opens first), 3_test_no_joins, figshare_integration, stress_test_master, 1_test_data_ST22_dummy, 2_test_data_ST22_dummy, demo_abromics. The selector is hidden in the other app features (visible: false).

## Findings (most likely to be hit first)
1. Exploration filters stay on the next recipe (staged and applied).
   Steps: open 1_test_data_ST22_dummy, tab "AMR and Virulence" / "MLST Bar", add a filter (year < 2050), Apply, add a second one (staged), choose My view; switch to 2_test_data_ST22_dummy. Result: both rows are still in the Filters panel, "Apply (2)", "Send to Audit (2)", and the right panel lists "Active Filters year < 2050". Same after switching back (qa2_S2_02_B_filters_open.png, qa2_S2_03_back_A.json).
   Worse case (qa3_run.out, qa3_S3_01_B_with_leak.png): on recipe 1 filter sample_id = 10668076, switch to recipe 2: its table is now only that sample (data preview changed from the 37-line baseline, plot image changed), no message that the filter came from another recipe. Only a small "Active Filters" line in the right panel and the filter row show it. With a column that the other recipe lacks (year vs Year) the filter does nothing and says nothing.
   Also: "Send to Audit" is offered on the leaked filter and would put recipe 1's filter into recipe 2's audit.
   Code: nothing clears `applied_filters` / `_pending_filters` on a recipe change. They are created at app/handlers/home_theater.py:218-219; the recipe-change effects at home_theater.py:203-226 only notify and remember the id. Resets exist only at filter_and_audit_handlers.py:690-698 (Send to audit, Reset button) and :1077 (INFERRED place: add an effect on `input.data_analysis_recipe_id` there or in home_theater.py:223).
   Decided: yes. ADR-099 point 1 (architecture_decisions.md:5078-5082): exploration filters "are cleared on a view or recipe change (reason: a filter is built against one stage's columns, names and types)". Design file .claude/design/home_preview_filters.md:101 ("Clear on view and recipe change, with a message and a WHY code comment") and the edge case list line 98 ("recipe switch with filters on"). I found no ledger line with the same words; the ADR text is the source. Whether the "view change" clearing is built was not checked.
   Suggestion: clear both lists on recipe change and tell the user in one notification. [sonnet/low] plus a browser test (see 5).

2. "My view" stays selected on the next recipe (plot and data).
   Steps: choose My view for plot and data on recipe 1, switch: the new recipe opens in My view (badge "Viewing: My view T3=T2=T1"; qa_10_to_*.json: plot_view T3, tier_toggle T3). Not harmful (empty audit shows the same data) but not the "both start on Result" default of ui_implementation_contract.md section 2. The README of an export made on 2_test_data_ST22_dummy says "Active tier: T3".
   Code: tier_toggle set at home_theater.py:1201 (INFERRED: the switch does not reset it; plot_view the same).
   Decided: not for a recipe switch. Contract section 13 says tab changes clear pending nodes; it says nothing of the tier choice on a recipe change. Options: reset both to Result on a recipe change, or keep (user's choice) and show it.
   Suggestion: reset to Result on a recipe change (a new recipe is a new analysis), one-line notice not needed. [sonnet/low] after Eve confirms.

3. Export panel fields stay (label, format, size, report format, preset, "reproducibility" box).
   Steps: label "labelFromA", format svg, reproducibility ticked on recipe 1, switch to recipe 2, export: the bundle is recipe 2's, but named "..._labelFromA", svg, and README says "Reproducibility: included (the box ... was ticked)". The scope is reset with a notification when the choice is not valid on the new tab ("The export scope 'Active group' is not available on this plot tab, so the scope was set ..."); on returning to recipe 1 the scope was back to "group" in some runs and "global" in others (depends on which tab the new recipe opened on: qa_12_*.json).
   Decided: not found (D-0165). The user ticked the box; keeping settings may be wanted. Options: keep and show the values, or reset all fields on a recipe change.
   Suggestion: Eve decides. Keep is simplest. The reproducibility tick staying silently is the one I would mention in the demo script.

4. Return to the first recipe: what is restored.
   Restored: the audited step and its stack (qa: dev4_S4_03: "My Adjustments (Tier 3) mlst_bar: year < 2050" back after A -> B -> A). Audited steps of recipe 1 never showed on recipe 2 (audit stack, plot, export checked). Lost: the active group tab and plot tab (always back on the first group / first plot), exploration filters are NOT lost (they leaked, finding 1), Export fields kept. No notice says "your tabs were reset".
   Decided: contract section 13 says tab changes clear pending items; nothing says to restore the tab. Not a bug; mention in the demo.

5. Fast A -> B -> A -> B -> A (250 ms steps): ended on A, correct tabs, plot visible, no error, two "loaded" notifications (qa_20_quick_ABAB_end_A.json). Passed.

6. Side finding, not caused by switching: Send to Audit on "MLST Bar" with a year filter writes a Traceback to the server log: `KeyError: "column 'year' is not in the table"` from libs/utils/src/utils/missing_values.py:71 via dialog_lines:138, message "filter dialog: the counts of column 'year' could not be computed" (server_qa.log:499, server_dev.log:231). The dialog still opens and works (counts missing). Not shown to the user as an error, so it is an unannounced loss of the count text (D-0050 "No silent error that is the rule"). Cause INFERRED: the frame passed to the dialog is a different stage/dataset than the filter column's. [sonnet/medium] to find which frame.

## Existing tests for switching
- app/tests/test_shiny_smoke.py:404 `TestRecipeSwitchPlotRender` (first plot renders after a switch).
- app/tests/test_export_scope_choices.py (scope choices on a plot tab or recipe change).
- app/tests/test_shiny_gate_gap.py (recipe edited on disk / hidden selector).
None checks that filters, My view or Export fields are cleared or kept on a recipe switch.

## What was checked and passed
- All 7 recipes: banner, tabs, plot image, data preview, Info panel, group of tabs are the new recipe's; no red output, "Render error" or "Traceback" in the page, no browser console error (only bootstrap-datepicker DEPRECATED warnings), no traceback in the server log caused by a switch.
- Same results under qa, developer (ghost save on) and pipeline-exploration-advanced.
- Audit stack: A's audited node does not appear on B and comes back on A; the export on B holds B's recipe (README: recipe 2_test_data_ST22_dummy, 3 plots of B, T1 data of B, reproducibility files of B, no T3 files).
- Export after the switch (A -> B, export on B): bundle is B's. Waited more than 1 s.
- The "Alerts" count grows with each load (1 -> 3): informational.

## What was not checked
- pipeline-static, simple, web-demo, demo-vetinst (no selector).
- Gallery, Blueprint, Test Lab switching; Compare mode; session restore panel (Restore/Import); column selector drops (only the number of selected columns after a switch: always the new recipe's).
- Whether a leaked filter on the same column type changes the exported plot (export ignores exploration filters by rule; not run).
- A staged-but-not-sent filter next to a recipe with a column of the same name and another type.

## What I left on disk (all under git-ignored tmp/, not deleted)
- tmp/UI_TEST/user/_sessions/*/assembly.json (one per recipe opened; some existed before), two t3_20261118T0801/0803*.json ghost files in tmp/UI_TEST/user/_sessions/24a5de944f39:a1ae45bde9f0/ (written by the developer pass; the first was probably not mine, INFERRED from the clock), 5 new files in tmp/UI_TEST/user/anchors/.
- Ghost files go to `<user_data location>/_sessions/<recipe sha:data sha>/` = tmp/UI_TEST/user/_sessions/ (local.yaml deployment). qa has ghost save off (it still writes assembly.json).
- Scratch and evidence: tmpAI/switch_check/ (drive*.py, *.png, *.json, *_run.out, server_*.log, qa_export_B.zip, progress.md).
- Servers started by PID and stopped by PID (pid_qa, pid_dev, pid_adv).
