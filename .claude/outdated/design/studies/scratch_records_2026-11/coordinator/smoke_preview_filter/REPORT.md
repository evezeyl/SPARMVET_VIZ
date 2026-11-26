# Report: test_a_preview_filter_never_changes_the_plot (HOME, dev 45e539a5)

## Verdict
TEST STALE (the way it compares), not the code. Confidence: high for the cause, medium-high for "the plot data did not change" (see "Not covered").
The HOME app obeys D-0327 and D-0311. The test compares the plot's `src` (a base64 PNG). That string changes when the picture is drawn at another width. Switching to Audit mode opens the right panel (D-0375, D-0385), so the plot column gets narrower and the plot is redrawn at the new width.

## What a HOME user sees today
- Exploration, filter applied: the plot is unchanged; the table changes; the note "preview filter(s) on, not saved" shows. (probe: picture 958x480 before and after apply, same bytes.)
- Switch to Audit mode: the notice "The filters were removed because you switched to Audit mode ..." appears (D-0311), the filters are gone (`#filter_remove_0` count 0), the right panel opens and the plot is drawn again, narrower (898x480, plot box 958 -> 766 px). Same plot, other width.
- Back to Exploration: width 766 after 2.5 s, picture bytes differ from the first one (the right panel was still open at that moment; not studied further).

## Failing assertion
app/tests/test_shiny_smoke.py:1024, the LAST assert of the test, after `set_mode(page, "audit")`:
`assert page.locator(".shiny-plot-output img").first.get_attribute("src") == src_before`
-> `AssertionError: assert 'data:image/p...AAElFTkSuQmCC' == 'data:image/p...JRU5ErkJggg=='` (full output: tmpAI/coordinator/smoke_preview_filter/run1.txt line 40).
All earlier asserts of the test pass (the plot is unchanged after Apply, with the "table only" badge, and on T1, T2, T3). The decided part (D-0327 exploration changes nothing of the plot; D-0311 filters cleared, with a notice) passes: the notice assert at line 1021 passes.

## Runs
Alone, qa features: run1 FAIL, run2 PASS, run3 FAIL, run4 FAIL, run5 FAIL (all at line 1024; files run1..run5.txt). The one pass is probably a race (the redraw at the new width not yet arrived after the 1.5 s wait); not proven. Load was about 5.

## Evidence (scratch probe: tmpAI/coordinator/smoke_preview_filter/probe.py, headless, own port 18765)
Image sizes decoded from the PNG header: before 958x480, after apply 958x480 (identical string), Audit 898x480 (plot box 766 px). Different string only because of the width.
Code: `app/handlers/home_theater.py:1408-1418` (`_drive_right_panel`: `ui.update_sidebar("audit_sidebar", show=wanted)`); `app/modules/frame_widths.py:69-77` (`right_panel_open`: HOME open only in Audit mode).

## Commit
- The last assert was written in 5478e33e (2026-11-20 08:18, "the browser tests follow the mode switch ..."), when the right panel was still always open in HOME.
- b1676bf4 (2026-11-20 22:47, "the right panel opens with Audit mode and closes when it is left", D-0375, D-0383, D-0385) made the plot width depend on the mode. It is the first commit after which the assert can fail. I did not run old commits (found by reading the two commits and the code, not by bisect).
- The failure was also seen before the Data Import merge: consistent (that merge did not touch this).

## Options (the owner decides)
- Suggestion: compare what the data says, not the pixels: assert the plot's own table/badge (the badge "Plot: Result"/"Plot: Audited" and the note text) or the plot data through the engine, instead of the `src` after the mode switch. Changes: the test only; keeps its intent.
- Suggestion: drop only the last assert and keep the T1/T2/T3 checks (same width there); add a separate test of the Audit-mode plot (D-0019). Changes: test only; loses nothing decided.
- Suggestion: fix the width in the test (wait for the sidebar to be open, then compare with a baseline taken in Audit mode without filters). Changes: test only; more steps, still pixel-bound.
- Suggestion: make the plot render at a fixed size independent of the panel. Changes: CODE and the look of HOME; not needed by any decision I read; I would not choose it for a test problem.

## Not covered
- I did not prove that the Audit-mode picture has the same data as the Exploration one (different widths cannot be diffed); the badge and the tests for T1/T2/T3 point to the same Result, and the code path (home_theater plot) was not read line by line.
- Why run2 passed (race assumed, not shown).
- Why the width is still 766 after returning to Exploration within 2.5 s (D-0385 says it closes; maybe slower than my wait, or a hand-opened rule at frame_widths.py:72).
- No old-commit runs, no full suite, no other test of the class (only this test was run).
