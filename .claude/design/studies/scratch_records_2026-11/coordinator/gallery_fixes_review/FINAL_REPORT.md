# Review of task/gallery-walk-fixes (4 commits on dev 2e21fcea)

VERDICT: FIT TO MERGE (no blocking finding). Notes below are small: records and one size count.

Decisions block of the brief: D-0271 (HOME and GALLERY settled), D-0327, D-0310, D-0311, D-0326, D-0334, D-0361, D-0365 are HOME decisions; none is touched by this diff (diff touches home_theater.py only to hand the new state to the Gallery sidebar). Complied for D-0271: each of the six walk findings is fixed at its cause (read; ran).

## 1. Causes, rules (read at file:line of the diff; ran)
- Finding 9/6 (tick wiped after Select all): cause was the server answer `update_checkbox_group` arriving after the user's next tick. Fix: gallery_select_all.js does it in the page; server only remembers the box (`gallery_handlers.py` _track_all). Cause fixed, no shim. Race rerun: 30 fast and 30 slow, 0 deviations (`tmpAI/race.py`, own server, qa).
- Finding 2 (Apply drops a matching example): `_update_gallery_options` keeps `_current_rid()` when it is in the new list; else first match and a visible note ("... does not match the ticked filters").
- Finding 3 (first second): the empty select filled later is gone; the sidebar shell is built from the state, first paint holds the list; `_current_rid` is one rule shared by shell and panes.
- Finding 4: standing no-match line `gallery-no-match` in the preview pane.
- Finding 5: one sentence under the filters and in help (gallery.md:8).
- Finding 1: `gallery_state` rebuilt shell.
- ui_implementation_contract section 14: R1 no render writes (renders only read); `_remember` is idempotent (R3, `merged != current`); R4: shell reads the state inside `reactive.isolate()` (home_theater.py `_render_gallery_main`), so the shell does not re-render when state changes. `_track_selection` reads `_visible()` inside isolate. No loop found (state write -> `_current_rid` -> panes only; trackers write only when the value differs).
- rules_ui_dashboard section 5: Gallery computes nothing new, filters only from the index pivot (`matching_examples` in gallery_listing.py), no handoff. OK.
- CLAUDE.md section 8: script is local (`app/src/www/gallery_select_all.js`), loaded only if `gallery_enabled` (ui.py `gallery_script_tags`, test_gallery_script_loaded.py). VENDOR_MANIFEST: the rule (rule 5) says "vendored asset"; the manifest has no entry for the other own scripts (`export_ready.js`, `bp_expr_editor.js`: grep empty) so no entry needed (read).
- CSS: no new CSS (inline `style=` of two small lines, the same style as existing lines; not in theme.css: minor, rules_ui_implementation_contract says one-off inline allowed).
- server.py: 273 -> 276 lines (limit "about 250" already exceeded before). On a merge with opening-build it would be 277 (merge-tree). Reported, not decided.

## 2. gallery_state (read; ran)
- Created per session inside `server()`: no leak between sessions. Gallery handler only registered when the Gallery is on (server.py); with the Gallery off, the state exists and is never read (HOME default `gallery_state=None` handled).
- `test_every_app_features_starts.py` (variable unset): 9 passed, includes the files with the Gallery off (static, simple, demo, web-demo).
- Not checked: two browser tabs of one session at once.

## 3. Page script (ran, read)
- After a fast sequence (Select all, tick, Apply in one page task, 10 times in the test; 30 fast + 30 slow in race.py) the server holds the user's ticks. Evidence: 0 deviations.
- Ticking all values by hand: the Select all box does not follow. It was so before (the old `_sync_all` effect reacted only to the box, read in `git diff`). Existing, not made worse.
- The page script and the server both hold "all"; the box state is remembered by `_track_all`, restored on return: tested by the state test for ticks (not the box).

## 4. Tests (ran)
- Headless suite (section 8, browser files ignored incl. the new ones), `-n 4`, 27 min (machine loaded): 12880 passed, 14 skipped, 32 xfailed, 3 FAILED:
  `app/tests/test_decision_ledger.py::test_real_ledger_header_counts_equal_the_computed_counts` (x2 parametrisations) and `::test_mutations_of_a_copy_of_the_ledger_are_caught`:
  `AssertionError: ((361, 354, 1, 2, 4), (365, 358, 1, 2, 4))`: the header of the ledger says 361, the computed count is 365. The ledger is not in the diff: it is a dev defect (the ledger lines D-0362 to D-0365 were added without the header count). Not caused by this branch.
- New browser files + left_out (flags: SPARMVET_APP_FEATURES=qa; qa.yaml `automation.ghost_save.enabled: false`, `gallery_enabled: true`; read from the file): `test_shiny_gallery_filters.py`, `test_shiny_gallery_state.py`, `test_shiny_gallery_left_out.py`: 12 passed in 75 s. Smoke Gallery parts: 2 passed, 1 skipped. `test_gallery_*.py` in the headless run: passed. `test_every_app_features_starts.py`: 9 passed.
- Can the tests fail? Scratch copy (git archive HEAD under `scratch/`), four reverts, each run failed the named test:
  1. Apply forced to drop the example (`if False and before in choices`): `test_apply_keeps_a_still_matching_example` FAILED.
  2. No-match line removed: `test_no_match_shows_a_standing_line` FAILED.
  3. Shell built without the state: both tests of `test_shiny_gallery_state.py` FAILED.
  4. Script emptied: `test_tick_right_after_select_all_is_not_wiped` FAILED.
  What they cannot see: the visual look; a late server answer on a slower machine (the race tests rely on one page task); the first-paint test polls every 5 ms in the page and can miss a blank shorter than that.
- Not run: the full browser suite.

## 5. PROVISIONAL wordings (the builder marked) and @deps
- `gallery_listing.py` `APPLY_RULE_TEXT` ("Ticks act only after you press Apply.") and `NO_MATCH_TEXT` ("Nothing within this selection. ...").
- `gallery_handlers.py` (note on a dropped example: "... does not match the ticked filters, so it is not shown. Showing the first example that matches instead.").
- `app/src/help/gallery.md` line 8 (paragraph "Ticks act only after you press Apply").
- The notification "No matches found for these filters." was reworded (emoji removed).
- @deps blocks not updated: `app/handlers/gallery_handlers.py` (consumes `gallery_state`, `matching_examples`), `app/modules/gallery_viewer.py` (consumes `matching_examples`, state), `app/handlers/home_theater.py` (new kwarg `gallery_state`), `app/src/server.py` (new shared state), `app/modules/gallery_listing.py` (`consumed_by` lacks gallery_viewer.py). `gallery_select_all.js` has no @deps block. Docs: `rules_app_structure.md` section 3 (list of shared state) and `ui_implementation_contract.md` section 13 do not mention `gallery_state`; UML/ADR sync (workspace_standard) not checked by me.

## 6. Merge (git merge-tree)
- into dev: clean.
- into task/opening-build: ONE conflict, `app/handlers/home_theater.py` signature of `define_server`: HEAD adds `gallery_state=None):`, opening-build adds `recipe_gate_version=None):` on the same line (both lines are new kwargs after `session_processing_issues=None,`). Resolution: both, comma between. `app/src/server.py` merges without conflict (277 lines after merge).

## Findings, by severity
1. Medium (not this branch): ledger header count (3 failing tests on dev) must be fixed before any merge is judged on a green suite.
2. Low: records (section 5), inline `style=` in two places, server.py size, no test of the Select-all box when ticked by hand (existing).
3. Low: the dropped-example note shows in the preview tab only (read; not run on the other panes).
