# Report export-ready (worktree .claude/worktrees/export-ready, branch task/export-ready)

Commits: d443f445 (task 1, D-0270), then task 2 (D-0269; hash: `git log` on the branch). No push, no merge.

## What the user sees (texts PROVISIONAL: Eve reads them before they ship)
All texts are in ONE place: `EXPORT_READY_TEXTS` in `app/handlers/export_handlers.py`.
- After any change in the Export panel the button turns grey and says: "Getting ready ..."
- When the server holds the values on the screen, the button is active again with its old text ("Export Bundle").
- If the confirmation is lost (after 5 s, `EXPORT_READY_TIMEOUT_MS`): the button is active again and a warning notice says: "Your last change may not have been received. Check the box and the label, then press Export."
- A press on the grey button does nothing (click, Enter, Space). The button stays reachable by keyboard (aria-disabled, no tabindex change). The user presses again when it says Export.
- Bundle (task 2): README.txt has one header line "Plot warnings    : none" or "Plot warnings    : N (listed under 'Plot warnings' below)", and a section "Plot warnings (these plots were drawn; read each warning before you rely on the plot):" with one line "  <plot id>: <same words as HOME's Alerts panel>". effective_run.yaml has `plot_warnings:` per plot (list of text, problem, fix, component, location; `{}` when none). I chose "none" as a positive line because the README's neighbouring lines say what was and was not done (D-0050); change if Eve prefers silence.

## Design (task 1) and why it closes the race
Cause (from the earlier review): Shiny applies input messages under the reactive lock; a download request is handled without it, so it can read inputs before earlier messages are applied.
- `app/src/www/export_ready.js` (local, no CDN, 130 lines, not a vendored asset): delegated listeners on `document` (survive any re-render) for `input`/`change` of the 8 fields listed in `EXPORT_PANEL_FIELDS`. On a change it greys the button at once (also while typing, before Shiny sends the text) and sends `export_client_ping` (event priority).
- Server effect `_confirm_export_inputs` reads the ping and all 8 fields and sends the custom message `export_ready_echo` {ping, values}. It runs after the input messages were applied.
- The script opens the button only when (a) the echo's ping is >= the last ping sent and (b) every echoed value equals the value on the screen now (read with Shiny's own input binding). An older value in the echo means a newer echo will come. So it is a real round trip proving server values = screen values, not a delay. A download pressed after that reads applied values.
- Timeout: after 5 s without a matching echo the button opens with the notice above.
- A MutationObserver puts the grey state on a button the server draws again. The fields list and texts come from Python through data attributes (one source).
- Found while testing and fixed: the browser fires `change` on a text field at the mouse-down on the Export button; that greyed the button between mouse-down and mouse-up and swallowed the click (2 existing tests failed with it). The script now ignores an event whose value equals the last seen/confirmed value. Test added.
- CSS in `config/ui/theme.css` (Type 5 grey #b0b0b0, text #1a1a1a, cursor not-allowed; no new colour). `ui.py` loads the script (mtime-versioned like the neighbour).

## Numbers (browser, qa, one process at a time)
Race test = tick the box and set the label, press Export in the same JS instant (faster than a person), 8 runs, bundle must hold both.
| | old code (30be8958) | new code |
|---|---|---|
| change + press at once, 8 runs | 1 of 8 failed (the first, cold run) | 0 of 8 failed |
| two quick changes (svg + publication) then press | 1 of 1 failed (README said png) | 1 of 1 passed |
| seed test of test_export_download.py, 8 runs | 8 of 8 passed | 8 of 8 passed |
The seed test was NOT flaky in my 8 old-code runs (the earlier report said about 1 in 3 under load), so it shows nothing either way; the race tests above are the evidence. The old-code window is narrow and warm-session dependent; one failure in 8 matches the review (1 in 24 warm).

## Tests
- `app/tests/test_export_ready_button.py`, 16 tests, all pass (7m31s): 8 runs change+press at once; two quick changes; grey then ready with plain text; plot tab changed during the wait (fields kept, bundle has the label); typing a label then a real mouse click gives the bundle; lost echo (the page's websocket drops the `export_ready_echo` frame via Playwright `route_web_socket`, no hook in production): button opens again + notice; grey on the input event before the field is sent; grey button not usable by Enter, Space, dispatched click, forced click, stays focusable; button replaced during the wait is grey again and comes back.
- Break once: click guard removed from the script -> 10 of 10 selected tests failed (8 race, two-quick, keyboard). Then restored.
- Neighbours: test_export_inputs_survive_plot_tab + test_export_download: 13 passed. Headless export tests (13 files) incl. task 2: 209 passed, 4 skipped. `python -c "from app.src.main import app"`: OK.
- `app/tests/test_export_plot_warnings.py`, 6 headless tests (real download generator): no warning; one; several on one plot; same warning on two plots (written for each); only the plot with a warning named (the export draws plots HOME never showed); the real missing-font warning of the library (no fake). Break once: `_found = []` -> 5 of 6 failed. Restored.

## Decisions table
| Decision | How complied | Where | Test |
|---|---|---|---|
| D-0270 "Time out will not be understood by my user so it needs to say activated when ready or something alike" | plain waiting text, ready text, no technical word; timeout opens the button with a plain notice | export_handlers.py EXPORT_READY_TEXTS; export_ready.js | test_export_ready_button.py |
| D-0269 "the export collects the warnings of the pictures it draws" | plot_warnings(fig) per plot, README + effective_run.yaml | export_handlers.py after render | test_export_plot_warnings.py |
| D-0271 "home and gallery as settled as possible" | no behaviour of HOME changed; HOME's warning text moved to one shared function | plot_issue_reporter.py plot_warning_text | test_export_plot_warnings (same text) |
| D-0050 "No silent error that is the rule." | a lost confirmation is told; warnings are written | as above | as above |
| D-0101 short plain sentences | texts above | | |

Consequence question: "what happens to a press on Export during the grey time?" Nothing happens; the user presses again when it says Export (not queued: a queued press could download values the user did not mean).

## Not covered / open
- Proof is by Playwright; not measured with a human. The window under old code is small.
- The echo covers the 8 fields of the Export panel only. The download also reads the recipe selector and the plot tab (outside the panel); those are not in the confirmation.
- Import file field, other user spaces: not in scope. Change of user space and back: the delegated script and the shell survive; not browser-tested by a dedicated test (only plot-tab change).
- Notice is a client notification: it is not written to the Alerts panel.
- Text inputs: each key press sends a ping (cheap).
- The warnings are not in `report.qmd` (README + effective_run only, as asked).
- PROVISIONAL choices: the 5 s wait, grey colour, "none" line, effective_run key `plot_warnings`. Needs decision: the three texts above (Eve to approve).
- I removed my nested git worktree tmpAI/old_code with `git worktree remove` (coordinator asked). No process left running. `tmpAI/` scratch files in the worktree are git-ignored.
