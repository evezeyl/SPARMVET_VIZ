# The browser tests that fail now and then: the causes (builder investigation, night of 2026-11-21 to 22; filed by the coordinator)

Her rule (D-0466): retest on suspicion and identify the cause. Each cause below was found with a timeline recorded in the page over 20 repeats, and proven by removing it in a probe copy. Probe copies and raw results: worktree `../SPARMVET_VIZ_wt_flaky_probe/tmpAI/probe/`. No line of the app was changed.

## For the owner: two things a real user can meet
1. **HOME, the Filters panel: a typed value can be lost, silently.** After the user picks the operator (for example "value >="), the value box is drawn again by the server. If the user types the number before that redraw arrives, the typed number is thrown away and the box shows its minimum again ("1"). Nothing says so. If the user then presses "+ Add row", the row is added with the wrong value ("value >= 1" instead of "value >= 100"). The redraw arrived 1.2 to 3.2 seconds after the operator change on the busy machine; on a quiet machine it is much faster, so by hand it is unlikely there, and likely on a slow or shared server.
   Where: `app/handlers/filter_and_audit_handlers.py:424-441` (the value box is drawn again at every operator change, also when its kind does not change) and `:496` (a fresh box starts at the column's minimum).
   This is the same family as the known defect "a typed audit reason is lost during a redraw" (task HOME-REASON-LOST-DURING-REDRAW), on another box.
2. **HOME, the left panels: a panel the user opens during the first seconds can close again.** While a recipe is still opening, the whole left side is drawn once more with a fixed list of open panels (`app/handlers/home_theater.py:2137`); what the user had opened is not kept. What triggers that late redraw was not traced.

## Per test
| Tests | Reproduced | Cause | Kind | Done |
|---|---|---|---|---|
| A, B: four tests of `app/tests/test_shiny_plot_errors.py` (they share one helper), and the step-order export test (same message: a typed 16 added as 1) | 6 of 20 | the test types into the OLD value box; the redraw then resets it. In all 6 failures the typing came before the redraw; in all 14 passes after | the test acts too early AND a user can meet it (point 1) | nothing changed: fixing only the test would hide the defect. With a wait for the redraw the probe passes 20 of 20 |
| C: `test_session_label_saves_on_blur` and its neighbours | 1 of 20 under load | the click opens the panel; 300 to 500 ms later the left side is redrawn and the panel closes (point 2) | both | nothing changed |
| C: `test_import_a_bundle_block_is_findable_above_export_form` | not reproduced | not found | - | - |
| D: `app/tests/test_panel_widths_browser.py::test_the_handles_cover_no_first_control_in_every_user_space` | 1 of 6; 9 of 10 with a short wait | the test sleeps a fixed 3 seconds; the right panel slides open later under load, and its handle has no width until then | the test only: a user meets nothing | FIXED in the test: it waits until both handles have a width. 40 of 40 passes. Commit `37b9075c` (in review) |
One more test of that file has the same fixed sleep and was not touched (it did not fail).

## For you to decide
1. Point 1 (a typed filter value lost): the fix in the app. Options: (a) the value box is not drawn again when its kind does not change (number box to number box), and keeps what was typed; (b) it is drawn again but the typed value is carried over when it still fits the new box; (c) "+ Add row" is disabled until the box has settled. The coordinator treats this as a defect, not a design choice (a filter is added with another value than the one typed, with no word), and has the fix prepared tests-first; say if you want one option over the others.
2. Point 2 (an opened panel closes): (a) the redraw keeps what the user has open; (b) accept it and only make the tests wait for the opened recipe.
3. The tests A and B: repaired with the wait once the app defect is fixed, plus a new test "type right after choosing the operator: the value stays".

## Not done
B's two named tests were not isolated (same helper, same message). The cause of the late redraw of the left side was not traced. The full suite was not run by the investigation.
