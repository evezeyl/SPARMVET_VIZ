# REVIEW2: task/export-ready, diff 73ba5390..1c9cdeb2 (dab8b232, b6bed286, bbbb3deb, 1c9cdeb2)

VERDICT: MERGE. F1 and F2 are closed. One test gap and two points for the owner are named below; none blocks the merge.

Decisions block of the brief checked: D-0270, D-0288, D-0296, D-0291, D-0303, D-0050, D-0285 (see the table at the end).

## 1. F1 closed (ran, own browser run, qa, worktree code; scripts and results in tmpAI/panel/export_simplify/review2/)
- 20 recipe switches A/B, each followed at once (0 ms) by a press: 20 of 20 refused, 0 bundles, 0 stuck grey (button open at the end 20 of 20).
- 20 more with the press after 0, 0, 50, 100, 150, 200, 300, 450, 700, 1000 ms (twice): 13 refused, 7 gave a bundle, 7 of 7 consistent (recipe and values of the same session), 0 mixed, 0 stuck grey. Final fields after every round were the right session's.
- Read: `export_ready.js` greys at the selector's own change event (watched field, `export_handlers.py` EXPORT_WATCHED_FIELDS); `export_session {key, values}` is applied and the key taken in one JS step (`onSession`); an echo opens the button only if `ping >= pingCount`, key == pageKey, the selector and every field equal the screen (`onEcho`). Effect order: `_tell_the_page_its_session` priority -50, echo `_confirm_export_inputs` priority -100, so in one flush the page is told first.
- Not covered: a press already on its way at the switch (exports the recipe left, with its own values, consistent: builder's note); a download request sent not by the page (no server-side check at download time).

## 2. F2 closed (ran)
A, B, A at gaps 0, 30, 60 ms, each gap twice (6 rounds): A's remembered choices kept 6 of 6, B's kept 6 of 6 (read back by returning to each recipe).

## 3. Store only under announced keys (read, export_fields_store.py `remember`, `begin_session`; export_handlers.py `_remember_what_the_page_shows`)
- One `ExportFieldsStore` per page session (made inside `define_export_server`, called once per Shiny session). `_issued` holds the keys this page was told.
- Another tab = another Shiny session = another store: a value sent from tab 2 for a key only tab 1 was told is dropped (empty or unknown key -> `remember` returns False, a warning notice is shown for a non-empty unknown key).
- Within one page session a report under an EARLIER announced key of the same page is accepted and stored under that key (this is the F2 design: a value belongs to the session the page showed). So: no leak between users or tabs. Within one page it can only reach a session that page itself showed. The value is not type-checked (a forged client could store a wrong type under its own session; the download reads the inputs, not the store, so no bundle is affected).
- Not run as a two-tab test; headless test of the store passed (see 8).

## 4. Busy wait (read export_ready.js, 1c9cdeb2)
- Fallback timer arms only when `pending` and the page is not `shiny-busy`; `shiny:busy` clears it, `shiny:idle` re-arms it (needs 5 s without busy). Test 2 of `test_export_ready_busy_wait.py` samples the page every 50 ms during a 7 s switch: no gap without `shiny-busy`.
- Path where the button opens on old fields: found none. An echo of the old session is refused by ping number (onSession raises pingCount) and by key; the selector is in the compared fields, so an echo made before the switch arrived does not match. The fallback needs 5 s of idle without confirmation.
- NEW CONSEQUENCE, a point for the owner (not decided by me): if the server never becomes idle (hung or endless work) the button stays grey for ever. D-0270 (ledger line 302): "If the confirmation does not come, the button does not stay grey for ever: after a wait it is active again with a plain notice." Read plainly, a hung server is a case where the confirmation does not come and the button stays grey; the code says so in a comment "PROVISIONAL". In a hung server the whole page is frozen anyway (no input, no output answers); I did not run a hung server. Options for the owner: accept; or an upper limit even when busy (with a notice such as "the app is still working"); or the other option named in the code, a check at download time. Open: which of these she wants, and whether "for ever" in her words covers a hung server.

## 5. Test-only app `app/tests/slow_switch_app.py` (read, ran)
Not collected: pytest collect-only lists nothing from it (name does not start with test_, no python_files setting). Imported only by `test_export_ready_busy_wait.py` (grep over app and libs: no other user); nothing in app/src imports app.tests. No conftest fixture starts it; the module fixture `slow_app` exists only in the busy-wait test file. Its import runs `app.src.main` inside the test process (extra import time, only in that test). It sleeps 7 s on the server when recipe 3_test_no_joins is chosen: test-only.

## 6. Label never remembered, fields in memory only (read, grep)
`remember` raises for any field not in EXPORT_FIELD_DEFAULTS, the label `export_user_name` is not in it; the JS reports only `data-remember-fields` (REMEMBERED_EXPORT_FIELDS, no label); the server sets the label to "" with each session message. No reference to the store in session_manager.py or session_handlers.py (grep). Store has no file access.

## 7. Reactive discipline (read)
No `.set` in a render: `system_tools_ui` reads the store inside `reactive.isolate()`. `_key_now.set` is in an effect with an equality guard. `_tell_the_page_its_session` (priority -50) depends on `_key_now`, the selector and `export_page_ready`, writes only plain dicts and the store, sends one message; no loop. `_remember_what_the_page_shows` is an event effect on `export_field_change`. Echo effect priority -100.

## 8. Tests run (one process at a time, qa, loadavg before each 1.6 to 6.3, always under 10)
- test_shiny_export_race.py: 13 passed (209 s)
- test_export_ready_busy_wait.py: 2 passed (49 s)
- test_export_ready_button.py: 18 passed (362 s)
- test_shiny_export_fields_per_session.py: 3 passed (108 s)
- test_export_download.py: 9 passed (340 s)
- test_export_inputs_survive_plot_tab.py: 3 passed (85 s)
- all test_export_*.py once (my --ignore options did not exclude the files I also named, so this run also ran the browser files, the environment was not set to qa for this run): 251 passed, 4 skipped, 1197 s. The 4 skipped were not looked at.
- BREAK-ONCE on a scratch copy (tmpAI/review/sb2 of the worktree, never a tracked edit): removed the echo's key check (`if ((message.key || "") !== pageKey) return;`). I checked the broken JS was the one served (the marker was in the served file). `test_shiny_export_race.py`: 13 passed. So NO test fails without the echo key check. Reading shows the check is defence in depth (the selector is also compared and the server tells the page first); it is the only guard for an echo of another session when the key changes without a selector change (for example a data change). A test that sends a stale-key echo to the page does not exist. This is a gap in the tests, named, not blocking.
- Merge conflict check: `git merge-tree --write-tree dev HEAD` (dev 9d4c7c68): exit 0, a tree id, no conflict lines.

## 9. Flags
qa (config/app_features/qa.yaml and bootloader under SPARMVET_APP_FEATURES=qa): export_enabled true, interactivity_enabled true, session_management_enabled true, t3_sandbox_enabled true, comparison_mode_enabled true, testing_mode true in the yaml (is_enabled("testing_mode") printed False: it is not a flag read that way), automation.ghost_save.enabled false (yaml comment: disabled in qa), data_analysis_recipe_selector.visible true.
NOT covered by the browser tests of the branch: selector hidden (pipeline-static, pipeline-exploration-simple, web-demo), session_management false, t3_sandbox false, interactivity false (pipeline-static), ghost save on, export_enabled false.
Covered by my run (scratch scripts hid.py, hid2.py): pipeline-exploration-simple (export on, interactivity on, session mgmt off, t3 off, selector hidden, deployment pipeline_test, recipe 1_test_data_ST22_dummy) and pipeline-static (export on, interactivity off, selector hidden). In both the selector is not in the page (0 elements), the Export panel is present, one field change greys the button (about 30 ms) and opens it again (about 50 ms) without the fallback notice, button open at the end; in pipeline-exploration-simple one export gave a bundle (17 plots, png, preset publication, README matches, no EXPORT_NOT_CREATED). The page script skips a watched field that is not in the page. Not covered: recipe switch in a setup with a selector but without session management or t3; ghost save on; export_enabled false.

## 11. Texts a user sees, changed or added (the builder said none changed: two are new)
- Unchanged: "Getting ready ..." and "Your last change may not have been received. Check the box and the label, then press Export." (EXPORT_READY_TEXTS).
- New (export_handlers.py, `_remember_what_the_page_shows`): warning "An Export choice was made for a session this app did not announce and was not remembered: check the Export fields before you export." Plain enough, but "session" is a technical word (D-0270: no technical word).
- New: error "An Export choice could not be remembered: <the message of the ValueError>". The message names fields of the code ("'x' is not an Export field that is remembered per session (remembered: export_include_reproducibility, ...)"): technical. It can only appear if the page sends an unknown field name, which the shipped page never does.
- A dropped report with an EMPTY key (page without session yet) shows nothing, the server then sets the fields; I checked by reading only, not by a run (D-0050: the screen then shows what the server holds).

## Decisions table
| Decision | Complied | Where |
|---|---|---|
| D-0270 "The Export button is greyed from each change of the Export panel until the server confirms that it holds the values" | complied; the "does not stay grey for ever" half has the hung-server exception (point 4) | export_ready.js onEcho, armTimer; export_handlers.py _confirm_export_inputs |
| D-0288 "I think the export should be lined to the active recipe read - and then active session" | complied | export_handlers.py _tell_the_page_its_session; point 1 bundles |
| D-0296 "the user can rewrite no problem so we do not need to rememver it" | complied | export_fields_store.py remember (label raises); point 6 |
| D-0291 "I do not think it needs to be saved" | complied (memory only) | point 6 grep |
| D-0303 "if the coordinator uses the qa for testing it needs to ensure it does what he thinks he is testing" | done: flags printed, uncovered cases listed, 2 run | point 9 |
| D-0050 "No silent error: that is the rule" | complied except the empty-key drop, which is silent but then corrected on screen (read only) | _remember_what_the_page_shows |
| D-0285 "do not run the same tests that also cost time" | my headless run repeated the browser files by mistake (20 min); noted | point 8 |

## What I did not check
Firefox/Safari; a hung server; two real tabs; a data change under the same recipe; session restore/import; ghost save on; the 4 skipped tests; the docs, ADRs and @deps lines beyond the diff's own header lines; export_enabled false.
