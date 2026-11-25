# Cause of the intermittent browser test "a step saved in BLUEPRINT that fails the gate is not used by HOME" (builder ab723cdd1574aa2a1, 2026-11-22; filed by the coordinator)

Evidence files: worktree `../SPARMVET_VIZ_wt_gate_gap/tmpAI/probe/` (probe scripts, per-run logs `repro*.txt`, `base.txt`, `b2.txt`, `pa.txt`, `pb.txt`). No app or test file was changed by the search.

## For the owner
- The test is right. It found a real defect a user can meet.
- What the user does: in BLUEPRINT, change a step so that the recipe fails its checks, Save, then click HOME.
- What the user sees about one time in four on this machine (4 of 20 runs of the real test; 7 of 24 of the probe): HOME stays half updated and does not mend itself (looked up to 35 s). The centre says "This data analysis recipe is not available" and names the saved recipe; the selector already shows another recipe; the Alerts panel says HOME shows the other recipe instead; the list of unavailable recipes is empty; no tab, table or plot of the shown recipe appears.
- What stays true: the failing recipe is NOT used by HOME (ADR-094). What breaks: the reason shown and the switch to the replacement recipe (ADR-104).
- Cause: when HOME changes the recipe, a BLUEPRINT table output (`architect_active_table`, `app/modules/wrangle_studio.py:753`, calls `processed_data()` at `:605`) is computed once (it raises ColumnNotFoundError on a table of the OTHER recipe), is invalidated again and, being hidden, is not computed again. Its old result stays in the queue and is sent with HOME's new screen. The browser part of Shiny 1.6.0 (`shiny.js` `updateStateFromFlush_fn`, lines 6150-6210) refuses a message that names an output not "idle" and throws away the WHOLE message, HOME's screen included. The server does not send it again.

## Proof by removing the cause (probe copies only)
- Patch A: `architect_active_table` returns nothing unless BLUEPRINT is the open user space (`input.sidebar_nav() == "Wrangle Studio"`; the same guard the BLUEPRINT effects use, `app/handlers/blueprint_handlers.py:944, 973`): 20 of 20 pass.
- Patch B: inside Shiny, drop the queued result of a suspended output invalidated after it computed: 20 of 20 pass (fired in 6).

## Options
1. O1: BLUEPRINT's outputs compute only while BLUEPRINT is open (patch A, for every BLUEPRINT output that reads shared HOME state). In the app, existing pattern.
2. O2: a rule inside the Shiny library (patch B). A workaround of the library (against "no shims").
3. O3: a newer Shiny, if it fixes it. Not checked; nobody installs anything.
4. Not recommended: change only the test.

## Not checked
Longer than 35 s; an idle machine or a human's timing; other BLUEPRINT outputs; how exactly HOME's recipe change reaches the BLUEPRINT table (reasoned: the shared base data). Candidates of the same family, not shown to fail: `app/tests/test_shiny_export_fields_per_session.py:138-142`; the "left panel closes while a recipe opens" case of `tmpAI/coordinator/browser_tests_cause/REPORT.md` could be the same mechanism (a lost flush).
