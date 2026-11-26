# Flake report: test_shiny_session_keep_both (worktree session-import)

Commit: 8ac4277a (test only). No app file changed.

## Cause (one sentence)
The test clicked Delete about 170 ms after it opened the session group, while the group was still opening (class `collapsing`); the click landed on the card behind the button, so the page never sent it and no notice came. Not a click lost in the app.

## Method
Diagnostic copy in `tmpAI/scratch/test_flake_diag.py` (not committed) plus a scratch trace in the handler (reverted; copy in `tmpAI/scratch/flake/session_handlers_traced.py`). Records per click: button connected and visible, redraws of the panel, every `sendInput` of a Restore/Delete id, a capture-phase click listener (target and its parents), notices with add and remove time, server lines (render, effect run, click count, ACT, NOTIFY), folder on disk. 26 diag runs, one at a time, load 0.7 to 3.5.

## Classification (all failures seen: 4 in 26 diag runs)
| Run | Failure | Class | Evidence |
|---|---|---|---|
| 2 | no "Session deleted" | click never reached the server (never left the page) | no `sendInput` of the delete id; no server line for it; button connected and visible, panel not redrawn (render count 2 before and after); folder still there |
| 10 | same | click landed on another element | click event target = a DIV (x 110, y 648), button never got it; `$inputValues` of the button 0 after the click; server shows no click |
| 11 | same | same | same pattern |
| 30 | same (with the extended probe) | same, with the cause visible | click target chain `DIV.spv-panel > DIV.accordion-body > DIV.accordion-collapse.collapsing`; `collapsing` also seen in the "before" probe; header click 170 ms earlier; no `sendInput`; no server line |
Not seen in my runs: "action happened, notice missed" (0), "click reached the server, effect did nothing" (0), redraw detaching the button (0: `connected_after` true every time, render count unchanged).
The earlier "Restore notice not seen" failures of the review: I did not reproduce one (the restore click in my 26 runs always worked, also mid-animation). The same early click after opening a group is the likely cause; NOT proven.
The earlier "Keep both stored []": test race (read of the store before the server wrote the copy); fixed.

## Notices
They are recorded by an observer on the page, so a short notice cannot be missed by the test. Shown for 4 s (delete), 6 s (restore); in the traces they are added within 3 to 50 ms of the click arriving.

## Can a real user lose a click?
No evidence of it. A user clicks where the button is drawn; the test clicked at the moment the card was still sliding open and hit the card instead, an ordinary mis-click on a moving target, visible to the user (the button does not react, he clicks again). Nothing was lost on the server side: every click that reached Shiny was handled once (counts 1, then 0 after redraw). Not checked: a real user clicking within 200 ms of opening a group on a slow machine.

## Changes (test only, `app/tests/test_shiny_session_keep_both.py`)
- A: `_wait_for_copies` polls the store (15 s, message names the wait) before asserting the copy.
- C: local `_show_card` = the shared one, then waits until no group of `#session_groups_accordion` has class `collapsing` (10 s, clear message). Used for every click on a card button (also in the look-alike test).
- Not changed: `test_shiny_session_restore._show_card` has the same weakness (click right after opening a group); other tests that use it may flake the same way. Suggest the same wait there (not done: outside the brief's file list, and I may not run that test).

## 15 final runs (real test file, qa, 2 tests each, one at a time)
final 1 load 1.64 pass | 2 load 2.17 pass | 3 load 2.37 pass | 4 load 2.69 pass | 5 load 2.25 pass | 6 load 2.12 pass | 7 load 2.58 pass | 8 load 2.51 pass | 9 load 2.35 pass | 10 load 2.80 pass | 11 load 3.31 pass | 12 load 4.13 pass | 13 load 3.64 pass | 14 load 3.24 pass | 15 load 3.66 pass. 15 of 15, each 36 to 43 s. No retry, no fixed sleep added.

## Limits
- Without the fix the rate was 4 in 26 (15%); 15 clean runs have about 9% chance to occur by luck at that rate. The mechanism (the click lands on the card while `collapsing`) is shown in the logs, so the result does not rest on the count alone.
- I did not run the fixed test under the diag probe, so "no `collapsing` at click time" is true by construction of the wait, not measured.
- The break-once for A/C is by the logs of the unfixed runs, not by a deliberate re-break of the committed file.
- Not run: the other session tests (the handler was not changed).
- Left: scratch files in `tmpAI/scratch/flake/` (git-ignored). `tmp/UI_TEST/user/_sessions` holds only the two older folders that were there before.
