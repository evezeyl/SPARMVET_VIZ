# Opening build, second control (branch task/opening-build-fixes, head cc618b58; dev 67c38ea9)

Method: worktree imports proven (`import app, utils` resolve under the worktree; `import.out`). Decisions read: D-0326, D-0343, D-0335, D-0334, D-0336, D-0327, D-0363 (ledger, all EVE, DECIDED).
Load: headless started at 4.9; browser at 9.2; others' sessions raised it to 15-30 at times (not mine alone).

## VERDICT: FIT TO MERGE (with the non-blocking items below; docs line is a rule-E4 item for a scribe)
Gate: headless 3 failed (all `test_decision_ledger.py`, header counts 361 vs 365, same failures on dev, ledger file identical to dev); browser 3 failed + 273 passed, the 3 are one hung test killed by me (see runs), passed alone 4 of 4. Results identical to dev (golden, 51 pictures, 334 keys).

## Part 1: the nine findings of the first control
1 headless 3 failed (factory guard x2, callback test): FIXED at the cause. The two guards now follow `opening_build.plot_render_recipe` and a new test checks HOME calls it twice and builds no dictionary of its own (test_plot_engine_reaches_the_factory.py:48); the callback test uses the real `materialize_tier3`.
2 browser 11 failed: FIXED by changing fixtures, none weakened to pass:
  - plot_errors: the old `alpha: lots` fixture is no longer reachable (refused at opening, D-0327); the failure is now made by an audit step (filter leaves no table under a log scale). Kept: other plots draw, one alert, export stub, Compare original pane draws.
  - GAP: nothing in the browser protects any more that a failing plot is shown as the red message picture. The only test for it is the STRICT xfail (build-step failure) and it fails by design. A draw-step failure (the old case) now has no browser test.
  - GAP: years fixtures cast year to text in the plot's own tier 3; tests read the dialog in T1/T2 (year is a number). The change of view T3<->T2 (number column becomes text) is no longer cycled (`test_filter_form_survives_rerender.py` loop now ("T2","T1")); T3 view of the dialog is unprotected.
  - tier3 broken test: now proves refusal at opening with plot and step named (D-0327 wording); the old data-preview error text is gone with the old path.
3 no fall-back notice on first screen: FIXED (`shown_recipe` written by the opening; unit test + browser assertion in `test_opening_browser.py`, passed in the full run).
4 environmental failure refused the recipe: FIXED (`failure_kind`, `check_store`; see point 3 facts).
5 timing: NOT changed, measured below (29 s first open).
6 test that could not fail (sources read): tests added (`test_opening_build.py`: reads only the sources used, second opening reads none); not mutated by me.
7 PROVISIONAL markers: added in opening_handlers.py, bootloader.py, home_theater.py.
8 docs stale: NOT fixed. `.claude/rules/rules_data_engine.md:33` still says "not stored"; `docs/foundations/data_tiering_adr.qmd:32` lists only T2; the diff touches no .md/.qmd except ledger, handoff, tasks. `opening_build.py` stale "D-0363 is being written" comment is fixed.
9 flaky export_race: passed in the full run this time.
10 repeated hashing: FIXED (`orchestrator._plot_key_now`).

## Part 1 points asked
2. Defect "failing plot shows Shiny raw error, not the picture": REPRODUCED headless (`p2.py`, `p2.out`) and in the browser (`bad_plot_after_audit.png`). A plot that fails in plotnine BUILD (empty table, `scale_y_log10`): `CheckedPlot.draw` (libs/viz_factory/.../checked_plot.py:293-307) returns the error figure, then Shiny calls `get_coordmap_plotnine` (shiny/render/_try_render_plot.py:389) which does `p._build()` on a copy (shiny/render/_coordmap.py:134) and raises IndexError (mizani/breaks.py:399). Not new: identical on dev code (`p2_dev.out`; libs/viz_factory has no diff between dev and head; the home render path changed by 7 lines unrelated). User sees: red text "Error: index 0 is out of bounds for axis 0 with size 0" where the plot is; the plain message with layer and fix appears in the left Alerts and Processing issues panels. For a failure in draw only, the picture shows (not tested any more in the browser, see gap).
3. Machine or recipe (`p3.py`, `p3.out`): 
   - Polars missing data file, real: Python FileNotFoundError "(os error 2)" -> UNKNOWN (opening stops, recipe not refused, "open it again, report it"). A PolarsError whose text holds "(os error 2)" -> RECIPE (ENOENT not in the machine list), refused. Wrapped in IngestionError from FileNotFoundError -> RECIPE.
   - PermissionError(EACCES) on a DATA file (Python/ingestion) -> MACHINE: stopped, not refused, text says "free space or fix the rights of the folder where the tables are stored" (misleading for a data file). Real Polars permission error on a data file has no errno -> UNKNOWN.
   - Column missing (ColumnNotFoundError), plot error (VisualizationError; and any failure in the draw stage) -> RECIPE, refused. KeyError/ValueError/TypeError raised in step code -> UNKNOWN: stopped, not refused; a real recipe bug of that type is never refused, HOME builds when asked and shows the error. MemoryError, ENOSPC -> MACHINE.
   - Stopped opening: signature is stored per session, so no loop in a session; each new session repeats the whole opening (no cross-session memory). In practice a missing data file is caught earlier by the key hashing / gate, so the real path to ENOENT in the opening is rare.
4. `shown_recipe` (read opening_handlers.py:88-93, recipe_gate_handlers.py:153-168): written only in `reactive.isolate()` with an equality guard; read only in `_follow` under isolate and in `_remember_choice` (writes only on input change); no render writes; no loop seen (server.log clean in test_opening_browser; `server errors: []`). Complies with ui_implementation_contract section 14 R1-R3.
5. Orphan sweep (`p5.py`, `p5.out`): two recipes sharing table name C in one store: opening tiny2 swept `C__T3_p_steps.parquet`, which was valid for tiny; opening tiny again rebuilt it. YES it deletes another recipe's valid file when a table name is shared (cost: one rebuild, never a wrong result; Tier 1/2 files of the same name already evict each other in that shared folder: `Tier 1 'C' DONE` rebuilt on each switch). It did not delete a valid file of the open recipe (owned names include every plan item; test_sweep_leaves_the_files_it_must_leave).
6. `_plot_key_now` narrowing: cannot make a stale table: the key function itself reads only `parts.datasets` (cache_keys.py:287), so a file outside it cannot change the key; coarse tables read all files. Proof: 28 plots of every shipped pipeline recipe, `_plot_key_now == compute_data_analysis_recipe_keys(...).plot_key_of` for all, 0 different (`p6.out`).
7. server.py 278 lines against "about 250" (rules_app_structure.md section 3): reported only.

## Part 2 runs (flags: qa; resolved flags in flags.out; ghost_save false in qa.yaml:49-51)
| # | run | result |
|---|---|---|
| 1 | `from app.src.main import app` | OK |
| 2 | headless `pytest libs app/tests -n 4`, ignoring the 31 browser files of `browser_list.txt` (incl. test_opening_browser, test_every_app_features_starts) | 3 failed, 12900 passed, 14 skipped, 31 xfailed in 706 s. The 3 = test_decision_ledger.py (3 of its tests; header counts 361 vs 365). Alone: same 3. On dev (git archive 67c38ea9): 4 failed (same + one needing git). Ledger file identical on head and dev: old defect of dev. Last numbers: dev 12681 passed; first control of the branch 3 failed, 12745 passed |
| 3 | browser 30 files, `SPARMVET_APP_FEATURES=qa -n 3 --dist loadfile` | 3 failed, 273 passed, 3 skipped, 2 xfailed in 3518 s. A worker (gw0) hung 55 min in `test_shiny_smoke_blueprint.py::TestBlueprintNodeClick::...[plot]` (call 3287 s); its chromium process was gone (not killed by me; cause not found); I killed my own playwright driver by PID and the 3 tests of that file failed with TargetClosedError. Rerun of the file alone: 21 passed (75 s); the `[plot]` test alone 3 more times: pass (46, 65, 82 s). Not reproduced. 2 xfailed = the strict plot_errors xfail and BP-GLIMPSE-ANCHOR-1 (known defect, test_shiny_blueprint_known_defects.py) |
| 4 | `test_every_app_features_starts.py`, variable unset | 9 passed (247 s) |
| 5 | golden dev 67c38ea9 vs head `--check`, PYTHONHASHSEED=0 | result-identical (7 recipes, 76 tables) |
| 6 | pictures dev vs head | identical: 51 |
| 7 | keys dev vs head | 54 recipes, 334 keys, cmp identical |
| 8 | `validate_app_features_config.py --all --strict` | 8 templates, 0 errors, 0 warnings, PASS |
Slowest browser tests: [plot] hung 3287 s (above); export_download exploration_filters 227; seed_places reshuffle 220, seed in recipe 174, no seed 148, reshuffle not offered 101; export_download mode2 85; seed_places default seed 81; export_inputs_survive 76; gate_gap 71; export_fields_per_session 71. test_opening_browser's refused-recipe test 51 s.

## Timings (`timing.out`, empty store, 17-plot demo recipe staged; load 6.9 at start, 10 at end)
First open: sidebar and tabs 29.3 s, first plot 35.0 s. A second session that connected 2.5 s later: sidebar after 32.2 s, first plot 34.1 s (blocked until the first opening ended; the whole server is single threaded). Second open (same store, new page): tabs 3.4 s, first plot 5.7 s. First control: 22.5 / 26.4 / 23.6 / 3.0 / 4.3 s at load 5: not comparable (load), no sign of improvement.

## Other findings (non-blocking)
- LOW, test gaps named above (red picture, year in T3 view); strict xfail keeps the build-step defect visible (it will flip red when fixed, as designed).
- LOW, docs stale (point 8). Rule E4 asks a scribe: rules_data_engine.md:33, data_tiering_adr.qmd:32, dependency index.
- LOW, sweep and shared names; wording for a data-file permission error.
- Not new: decision_ledger header counts (dev).

## NOT covered
Ghost save; other app features than qa except the start test; large data and the x30 figures; two sessions opening at the same moment beyond one probe; a recipe change during an opening; websocket drop in a long block (31-35 s); the cause of the vanished chromium; mutation of the new tests; ADR text, `audit_old_words`, `check_doc_links`, UML audit; Blueprint/Gallery/Test Lab opening paths; the full browser suite was run once and not repeated after the hang.
