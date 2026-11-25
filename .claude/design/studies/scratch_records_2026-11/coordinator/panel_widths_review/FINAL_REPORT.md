# Review of task/panel-widths (head e5582932, base dev b429c632)

## Verdict: FIX FIRST (do not merge yet)
Merge is clean (git merge-tree against dev 9658e690: no conflicts). The widths, the named values, the mode-driven right panel and the safety of the stored value are good. Three real defects and two regressions in existing tests.

## Findings (by weight)
1. HIGH, all user spaces (drag): after ONE drag in a page load, no further drag works until reload or double click. Cause (reproduced, diagnosed, fix confirmed in a scratch copy): bslib fires window "resize" events during a drag (31 counted over two drags); `panel_widths.js` line `window.addEventListener("resize", applyShares)` puts the stored share back on every one, so the second drag is pinned (bslib reports moves to 312 but `end` reports 272). Dev baseline allows repeated drags. Builder tests miss it: every drag test reloads between drags. Fix tried: ignore resize while a drag is on (set a flag on bslib `start`, clear on `end`); six successive drags then work (40, 40, -30, 100, -200, 60). Add a test with two drags in one page load.
2. HIGH, HOME left panel: the new 16 px grab area of the handle covers the calendar of the date filter near the panel edge: `test_shiny_filter_pickers.py::test_a_date_picked_in_the_calendar_is_staged_as_picked` fails alone (click on day "15" intercepted by `div.bslib-sidebar-resize-handle`, 58 retries); passes on base b429c632. A user cannot click days under the handle.
3. MEDIUM, HOME: `test_shiny_plot_tier3.py::test_every_plot_is_drawn_from_its_own_table_in_exploration_in_audit_mode_and_in_compare` fails alone (`_same_picture` 958x480 vs 766x480); passes on base. The picture width now follows the pane width (wider main panel), so the test compares pictures of different panes. Adapt the test (equal width) or decide; not a result change by itself.
4. MEDIUM, HOME: a reason typed in the audit panel and not yet applied is lost when the user goes Exploration then back to Audit (probe: dev keeps "my reason typed", branch gives "" and Apply stays disabled). The step survives, the typed text does not (the panel is now empty in Exploration so its inputs are removed). Nothing is changed silently, but user input is dropped; D-0383 asks for an empty panel, so the text should be kept in the state (or the loss told).
5. LOW, HOME: opened in Audit mode the right panel is blank for about 1 to 2 s (width opens first, content renders after). Also at the 1100 px floor the panel text is cramped (below).
6. LOW: left toggle chevron overlaps the first title in the right panel (BLUEPRINT "Blueprint Surgeon", TEST_LAB items); in TEST_LAB the item chevrons are clipped at 170 px.
7. LOW, dead code: since the audit panel is not built in Exploration, the Exploration guards of D-0377 are unreachable: `audit_stack.py` `audit_pending_badge_ui` (home_mode == "audit") and `audit_stack_tools_ui` (home_mode != "audit"); they are mounted only inside the panel built for Audit. Harmless defence in depth; say so or remove. The adapted tests moved the protection to "the whole panel is empty" (the new test checks no card, no #btn_apply, no badge, empty text): protection moved, not lost.
8. LOW: `frame_widths.clamp_width` is used only by the Python tests; the real rule runs in the JS (a second copy of the half rule). Only browser tests cover the JS.
9. LOW, edge: user closes the panel by hand in Audit then goes to GALLERY: R3 sends nothing (answer unchanged), the panel stays closed (D-0381 says likely visible). Two tabs: last writer wins, the other tab keeps its width until reload (benign).
10. LOW, docs drift: `docs/reference/ui_style_guide.qmd:43` still says "~340 px fixed"; `ui_implementation_contract.md` section 2 not updated for the closed-in-Exploration panel; UML (`docs/UML/app.mdj`) not checked (UML sync law).
11. INFO: server.py 282 lines (same as base, over the ~250 limit already). No CDN. Hex audit: the section 26 of theme.css adds only #6c757d and #345beb (both in the spec); other off-spec hexes are old. Rules spec section 12 states built as built, values PROVISIONAL.

## Point-by-point
1. Named values: all in `app/modules/frame_widths.py`; grep finds no copy in `ui.py`, `theme.css`, `panel_widths.js` (only an unrelated 0.15s). The JS reads data attributes. Measured (px, left / main / right):
| Window | Exploration | Audit |
|---|---|---|
| 1100 | 190 / 910 / 0 | 190 / 740 / 170 (67 %) |
| 1366 | 232 / 1134 / 0 | 232 / 929 / 205 (68 %) |
| 1600 | 272 / 1328 / 0 | 272 / 1088 / 240 (68 %) |
| 1920 | 326 / 1594 / 0 | 326 / 1306 / 288 (68 %) |
Other spaces (right open): 1100: 190 / 740 / 170, no overflow in left or right panel in BLUEPRINT, GALLERY, TEST_LAB; 1366: 232 / 929 / 205. Compare at 1100: each plot 313 px wide (cramped; was 316 before).
2. Mode: closed in Exploration, opens in Audit, closes on leaving, Home from another space gives the mode's state (builder test passes, plus probe). Opened by hand in Exploration: empty text, no card/Apply/badge. pipeline-exploration-simple and pipeline-static (with SPARMVET_DATA_ANALYSIS_RECIPE set): `#audit_sidebar` absent, no browser console errors, left drag works. The static claim: `test_static_hides_right_sidebar` fails to start the app under pipeline-static WITHOUT the variable on both branch and base (fatal: selector hidden and no recipe named, ADR-091); WITH the variable `SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy` the app starts and the test still fails on both (waits for `#sidebar_nav`, not visible in 15 s): a stale test of dev, not caused by the branch; the assertion itself (no `#audit_sidebar`) holds in my probe. Restored session: `test_shiny_session_restore.py` passes except one flake (below); R1/R3 read: effect writes only a UI update and only when the answer changes, no write in a render.
3. Script: read line by line. Stored value used only if `typeof number`, finite, within 0.05 to 0.5; then built as `Math.round(px)+"px"` by the script; every storage access in try/catch; nothing sent to the server. Probes: stored text/NaN/1e308/true/`__proto__`/img tag give the default and the style never holds stored text; denied localStorage: no error, drag works; window 500 px (mobile): no error; stored 0.5 / 0.5 at 1100: left 380, right floors to 170, main stays half; resize to 1000 and 1920 keeps main at least half; drag past half-window stops at the limit (main 683 of 1366); double click resets and clears storage. Mutants in a scratch copy: event name `bslib.sidebar.resize` renamed: 2 drag tests fail; `--_sidebar-width` renamed: 2 tests fail (drag, stored share). Good guards. Defect 1 above.
4. Adapted tests: audit_controls (reason input count 0 in Exploration: moved protection, but hides finding 4); opening_browser (Audit mode set first: fine); na_tick (summary read in the left panel row, asserts the right panel summary absent: consistent with D-0383).
5. CSS: see 11.
6. Merge: no conflicts.

## Screenshots (tmpAI/coordinator/panel_widths_review/)
home_explo_1100, home_audit_1100, home_audit_1100_panel_late, home_compare_1100, home_explo_right_by_hand_1100, home_*_1366, gallery_1100/1366, blueprint_1100/1366, testlab_1100/1366, handle_grip_1366, narrow_500, pipeline-*_1366. In plain words at 1100 px: HOME Exploration is roomy (plot 910 px, left panel crowded but readable, file label cut). Audit leaves 740 px for the centre, readable; the right panel shows "Pipeline Audit" cards in 170 px with wrapped words ("horizontal_barplot" broken). Compare gives two plots of 313 px: small. BLUEPRINT right panel (170 px): inputs truncated ("e.g. nvi_officia", "theme_mi"), title overlapped by the toggle chevron; nothing overflows. GALLERY fine. TEST_LAB right panel: chevrons clipped. The handle grip is visible as a dark bar in the middle of each panel edge.

## Runs
| What | Command (worktree, PYTHONPATH worktree + libs/*/src, main venv) | Result |
|---|---|---|
| test_frame_widths | pytest app/tests/test_frame_widths.py | 22 passed |
| test_panel_widths_browser | SPARMVET_APP_FEATURES=qa | 12 passed, 1 failed (mode switch test, flake: passed alone) |
| all 40 playwright files (all test_shiny_*, opening, modes, strip, filters, export, panel widths) | qa, -n 3 --dist loadfile | 418 passed, 6 failed, 7 skipped, 2 xfailed (32 min) |
| the 6 failures alone | same, serial | 4 pass (flakes under load: delete-all-sessions, original pane of compare, opening previous recipe, restore of another recipe); 2 fail = real: filter_pickers date (finding 2) and plot_tier3 (finding 3); both pass on base |
| headless baseline (libs + app/tests without the browser files) | -n 4 | 13257 passed, 10 skipped, 31 xfailed |
| test_every_app_features_starts | variable unset | 9 passed |
| static smoke test | pipeline-static | fails on branch and base (see point 2) |
Scratch worktrees removed; no process of mine left.

## NOT covered
Other browsers than Chromium, touch, a window under 1000 px beyond the 500 px load check, bslib upgrades, keyboard resize, real two-machine storage, UML model, docs render, load-time first paint of a restored session (only by existing tests), the full-suite state of dev itself (not run).
