# Final review and controls of task/engine-keys (2026-11-18)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`, head found: `5d9d540467d062e04500b588f33544ef05693ac6` (`5d9d5404`). `git status --short`: empty (clean).
Interpreter: main `.venv/bin/python`, PYTHONPATH = worktree `.` plus `libs/*/src`. PROVED: `utils.__file__` = `<worktree>/libs/utils/src/utils/__init__.py`; `app.src.main.__file__` = `<worktree>/app/src/main.py` (both inside the worktree).
Evidence labels: read / ran / reasoned.

## PART A: reading review (status: done)

Range read: `64d99e3f..HEAD` = branch-only commits `5892a872`, `ade69f0b`, `b6b40c40`, `fa7f856b` (Blueprint), the merge `514a54a4` and the five follow-ups `e1dc05eb`, `d4baef25`, `98d37ad5`, `9f08d931`, `5d9d5404`. (The raw range diff also shows dev's own 71 files; I judged the branch part only.)

### A1. Merge resolution (read: `git diff efd1cd5f HEAD -- <file>` = what the branch adds to dev; `git diff fa7f856b HEAD -- <file>` = what dev added to the branch)
- `app/handlers/export_handlers.py`: dev kept (the `EXPORT_*` constants, `export_fields_store`, `export_ready.js`, `plot_warnings`/`_warnings_unreadable`/`_plot_warning_rows`, no `export_scope`, `all_plots` once). Branch kept: `plot_engine_slot`, `engine_record`, `failed_plot_record`, `drawn_records` (set after `viz_factory.render`, before dev's warnings `try`; the `except` sets it again with `failed_plot_record(cfg.raw_config, spec, e)` where `spec` is the loop variable, line 1210), `collection_tier2_key`, `"engines"` in `effective_run`. Both sets stand in the same `try`. Nothing lost on either side.
- `home_theater.py`: dev's removals are intact (`fix_label` import, `active_home_subtab` argument, the issue-reporter import move). Branch's `plot_engine_slot`, tab labels (`ui_label`) intact.
- `session_handlers.py`: one import block holds `SessionDeleteError, key_drop_notice, normalise_audit_steps, session_id_collisions, session_input_id_parts, split_key_drops`; dev's keyed-session/import code present (the removed lines of the branch in that file are only the old `safe_sk` and `import_session_zip` code that dev replaced).
- `session_manager.py`: dev's `SessionImportLimits`, `session_import_limits_from`, `session_input_id_part(s)`, `SessionImportRefused`, `SessionKeyExists` present; branch's `split_key_drops`, `key_drop_notice`, `extract_primary_keys` (join keys) present. The only removed lines are dev's old `import_session_zip` (replaced by dev).
- `bootloader.py`: `get_session_import_limits` (dev) and `take_stored_tables_notice` + the sweep (branch) both present.
- Verdict A1: nothing of dev lost, nothing of the branch lost (read).

### A2. Adapted tests: weakened?
- `test_export_all_plots_and_defaults.py`, `test_export_plot_warnings.py`: only the shape of the recipe text changed (old `label:`/`spec:` indent to the new plot entry); asserts unchanged in meaning. Not weakened.
- `test_engine_record.py`: `OLD_KEYS` gets `plot_warnings`, `plot_warnings_unreadable`. Both keys are written unconditionally (`export_handlers.py:1585-1586`), so `OLD_KEYS <= set(run) and set(run)-OLD_KEYS == {"engines"}` (line 127) still fails if a key is dropped or a second new key appears. Not weakened.
- `test_plot_seeds.py`: reads the plot entry directly (`...["plots"].values())` instead of `["spec"]`; the assert on `random_state` is the same. Not weakened.
- `test_export_download.py` (strengthened, not broken-once by the builder): new asserts (lines 82-87): `set(pictures) == set(record["plots"])` and more than one plot; `set(pictures.values()) == {"svg"}`; no `export_scope` in README or `effective_run`. Can they fail? Reasoned: yes. A missing picture, a png/pdf picture, or an `export_scope` text each makes one fail; the regex counts only `.png/.svg/.pdf`, so `_ERROR.txt` is not a picture and a failed plot would leave `record["plots"]` larger than `pictures`. Weak spot: a bundle that holds a picture for a plot that is not in the record also fails (good), but the test reads the record that the same code wrote, so it cannot see a plot that both the record and the pictures left out. I did not break-once it (read-only role); the first browser run in Part C shows it passes.
- Verdict A2: no assertion weakened.

### A3. Rule files vs dev (ran `git diff efd1cd5f...HEAD --stat -- .claude/rules CLAUDE.md .claude/settings.json pyproject.toml libs/*/pyproject.toml`)
Exactly six files differ (138 insertions, 133 deletions): `rules_agent_role_bioscientist.md`, `rules_data_analysis_recipe_structure.md`, `rules_data_engine.md`, `rules_gallery_standards.md`, `rules_test_lab.md`, `rules_viz_factory.md`. `CLAUDE.md`, `.claude/settings.json`, `pyproject.toml`, `libs/*/pyproject.toml`, the other rule files, `architecture_decisions.md`, `decision_ledger.md` and `.claude/tasks/*` do NOT differ from dev. The six files are the branch's rule commits `724c83ce`, `43f06c0d` (deps blocks), `3af87c15` (F2 fix). Dev changed no rule file since. The four passages the review wanted Eve's yes for (F2) were cut back by `3af87c15`; the page for her is `tmpAI/engine_keys/RULE_PASSAGES_for_eve.md` (still her decision).
Still open from the earlier review (not repeated): F5, the removal task for the tombstones of the four removed `plot_defaults` keys is not in `tasks.md` (`tasks.md` is identical to dev). F3, the orphan files (see the picture check in Part C).

### A4. Silent errors: `except` added in the range
- `64d99e3f..fa7f856b` (branch-only, non-test code): zero `except` added (grep over the diff). `include_paths` raises `yaml.YAMLError` on text that is not YAML; its three callers sit in `try` blocks that tell the user: `blueprint_handlers.py` `_fail_load` (line ~488), "Could not load node" notification (line 1070), the agent tool returns `{"status": "error", "message": ...}` (`agent_tools.py:277`). Told, not swallowed.
- The merge itself added no `except` (read the diff of the five conflict files vs dev). Dev's `except Exception: _found = []` in the export names the plot in `_warnings_unreadable` (dev's code, told in the bundle).
- Branch-vs-dev list of added `except` over the whole branch (not only this range) has 25 lines; the earlier review covered them; I spot-checked none beyond the range. Not checked: the ones at `libs/utils` and `scripts` of the earlier steps.
- Verdict A4: no new silent `except` in the range.

### A5. Other reading notes on the Blueprint repair (`5892a872`, `ade69f0b`, `b6b40c40`)
- `include_paths` reads the YAML with a loader that only records `!include` scalars: correct for quoted and unquoted; it throws for an `!include` on a non-scalar (ConstructorError, a YAMLError: told, see A4). Test `libs/blueprint_arch/tests/test_include_paths.py` (59 lines) and `app/tests/test_blueprint_plot_open.py` (301 lines) exist; they run in Part C.
- The refusal text of the tier is PROVISIONAL (marked in code, D-0308 mentioned): it goes to Eve with the texts. `test_blueprint_tier_files.py` changed its regex to `made for tier 2.*is tier 1.*nothing was saved` (still names step, both tiers, nothing saved).
- The new browser test asserts 17 plots (`assert len(plots) == 17`): a hard number tied to the demo recipe; it fails loudly if the demo recipe changes (acceptable, labelled).

## PART B: THE FLAGS (ran: parsed the eight files of `config/app_features/` of this worktree)

| flag | developer | qa | standalone | pipe-adv | pipe-simple | pipe-static | demo-vetinst | web-demo |
|---|---|---|---|---|---|---|---|---|
| interactivity_enabled | T | T | T | T | T | F | F | T |
| t3_sandbox_enabled | T | T | T | T | F | F | F | F |
| comparison_mode_enabled | T | T | T | T | T | F | F | F |
| session_management_enabled | T | T | T | T | F | F | F | F |
| export_enabled | T | T | T | T | T | T | F | F |
| metadata_ingestion_enabled | T | T | T | T | F | F | F | F |
| import_helper_enabled / data_ingestion_enabled | T/T | T/T | T/T | F/F | F/F | F/F | F/F | F/F |
| gallery_enabled | T | T | T | F | F | F | F | F |
| blueprint_enabled | T | T | T | F | F | F | F | F |
| data_analysis_recipe_edit_enabled | T | T | F | F | F | F | F | F |
| blueprint_agent_enabled (backend) | T (claude_cli) | T (disabled) | F | F | F | F | F | F |
| test_lab_enabled | T | T | F | F | F | F | F | F |
| testing_mode | T | T | T | T | F | F | F | F |
| data_analysis_recipe_selector.visible | T | T | T | T | F | F | F | F |
| automation.ghost_save.enabled | T | **F** | T | T | F | F | F | F |

(T = true, F = false. Pipe-adv = pipeline-exploration-advanced; pipe-simple = pipeline-exploration-simple. The last two rows were read file by file with grep: selector.visible / ghost_save.enabled = developer T/T, qa T/**F**, standalone T/T, pipe-adv T/T, pipe-simple F/F, pipe-static F/F, demo-vetinst F/F, web-demo F/F. The table row "data_analysis_recipe_selector.visible" above is therefore: T T T T F F F F, and the ghost-save row: T F T T F F F F.)

What the browser tests do NOT cover (a test whose setup does not set the flag it needs is NOT covered, never "passed"):
1. All browser files except `test_every_app_features_starts.py` and `test_shiny_seed_places.py` (which sets an app features per case) run under `qa` only. So: ghost save ON (qa: `automation.ghost_save.enabled: false`): the T3 ghost written at Apply and on leaving Home, and Blueprint's draft autosave, are NOT exercised by the qa runs. The session restore test builds its files by hand.
2. The recipe selector hidden (pipe-simple, pipe-static, demo, web-demo): the pages with no selector are only started and looked at once (`test_every_app_features_starts.py`: Home renders, Processing Issues and Alerts mounted, Blueprint tab present only where `blueprint_enabled`). Export, filters, the session panel and the audit are not driven there.
3. `export_enabled: false` (demo-vetinst, web-demo) and `interactivity_enabled: false` (pipe-static, demo-vetinst): only the start of the app is tested. No export test under them.
4. `t3_sandbox_enabled: false` with `interactivity_enabled: true` (pipe-simple, web-demo): "My view" without audit, not driven in the browser except by whatever `test_every_app_features_starts.py` renders (Home start only).
5. `blueprint_agent_enabled` with a working backend (`claude_cli`, developer): qa says backend `disabled`; the agent chat is never driven.
6. `standalone` (no `data_analysis_recipe_edit_enabled`, no `test_lab_enabled`): start only.
7. Browsers other than Chromium; a second user session at the same time (except the race files that open two pages).
8. The browser tests start the app with `SPARMVET_DEPLOYMENT` of their own choice (a temporary deployment file in several files); the real production deployments (Posit Connect, container) are not started.

## PART C: controls (each suite once, one process at a time; the other reviewer ran the dev suite in the main folder at the same time)

### C1. Headless (status: done)
Browser files (27 listed by `grep` for `playwright`/`shiny_app` imports; list saved in `tmpAI/engine_keys/final_check/browser_files.txt`; 26 test files + `conftest.py`): these were ignored in the headless run. `app/tests/test_export_report_texts.py` is NOT ignored: it launches a Chromium once (one test, not the app) and renders with quarto (about 10 s per case); it is in the headless count.
Command: `<main .venv python> -m pytest libs app/tests --ignore=<the 26 browser files> -q --durations=25 -p no:cacheprovider`, serial. Load before: 2.80.
Result: **3 failed, 11242 passed, 5 skipped, 31 xfailed, 2 warnings in 1018.71 s (16 min 58 s)**. Output: `tmpAI/engine_keys/final_check/headless.txt`.

| # | Test | First error lines | Class | Evidence |
|---|---|---|---|---|
| 1 | `app/tests/test_engine_registry.py::test_every_registered_name_has_an_engine_in_the_tables_given_to_the_checker` | `assert {'annotate', ...} == {...}  Extra items in the left set: 'geom_point_registration_probe'` | caused by the branch earlier (a test leak, order dependent), not by the merge, not on dev | Passes alone 3 times (44 passed each). Fails when `libs/viz_factory/tests/test_registration_errors.py` runs first in the same process (ran: the two files in that order = 1 failed, 55 passed; in the other order = 56 passed). Cause (read): that test registers a probe component and cleans `PLOT_COMPONENTS` and `COMPONENT_SCHEMAS` (lines 46-48 of the file) but the branch added a third registry, `COMPONENT_ENGINES` (`registry.py:29,81`), which the cleanup and the `registries_untouched` fixture do not know. The probe name stays in the engine table the checker reads. Product code is right; the test's cleanup is incomplete. The test `test_engine_registry` is a branch file (not on dev), so dev cannot show it. |
| 2 | `app/tests/test_plot_callers_are_checked.py::test_a_file_is_saved_from_the_checked_plot[app/handlers/export_handlers.py]` | `export_handlers.py:1246 renders a plot and does not save it with plot.save` | SAME ON DEV | Ran in the main folder (dev `efd1cd5f`): fails the same (`render` at line 1230, first `.save(` at 1245, the test looks at 14 lines). Dev's own export change put the warning reading between render and save. The merge made the gap 2 lines longer (1246 to 1263) but the test fails on dev already. |
| 3 | `app/tests/test_suggestion_label.py::test_home_prints_its_alerts_and_warnings_through_the_same_function` | `assert '{fix_label(warning.fix)}' in home` fails | SAME ON DEV | Ran in the main folder (dev): fails the same. Dev removed `fix_label` from `home_theater.py` (uses `plot_warning_text` now: dev line 213) and left the test asking for the old text. Neither test file was changed by the branch for this assertion. |

What C1 does not prove: the 5 skipped and 31 xfailed are not listed here (the skips are quarto/jupyter or app-features conditions; the xfailed are marked known). Order dependence: the full run is one process, so another leak of the same kind can only be seen in a full run like this one.

### C2. Browser files, one at a time under `SPARMVET_APP_FEATURES=qa`, each with `timeout 1200` (status: done)
25 files + `test_every_app_features_starts.py` without the variable. Load before each run 0.97 to 3.34 (never above 10, no wait). None hung, none timed out. Driver and per-file output: `tmpAI/engine_keys/final_check/browser/` (`summary.tsv`, one `.txt` per file).

| file | passed | time |
|---|---|---|
| test_empty_data_analysis_recipe_startup | 1 | 6 s |
| test_export_download | 9 | 326 s |
| test_export_inputs_survive_plot_tab | 3 | 78 s |
| test_export_ready_busy_wait | 2 | 49 s |
| test_export_ready_button | 18 | 339 s |
| test_filters_cleared_on_recipe_change | 13 | 79 s |
| test_join_preview_session_alive | 2 | 22 s |
| test_shiny_apply_blocked | 1 | 21 s |
| test_shiny_blueprint_known_defects | 1 xfailed (known) | 15 s |
| test_shiny_export_fields_per_session | 3 | 102 s |
| test_shiny_export_race | 13 | 167 s |
| test_shiny_filter_pickers | 43 | 150 s |
| test_shiny_filter_types | 3 | 18 s |
| test_shiny_filter_value_list | 2 | 17 s |
| test_shiny_gallery_left_out | 3 | 19 s |
| test_shiny_gate_gap | 3 | 57 s |
| test_shiny_na_tick | 1 | 12 s |
| test_shiny_plot_errors | 4 | 40 s |
| test_shiny_plot_warnings | 1 | 9 s |
| test_shiny_seed_places | 4 | 359 s |
| test_shiny_session_keep_both | 2 | 37 s |
| test_shiny_session_restore | 1 | 38 s |
| test_shiny_smoke_blueprint | 21 | 71 s |
| test_shiny_smoke | 37 (3 skipped) | 123 s |
| test_shiny_step_order | 6 | 69 s |
| test_every_app_features_starts (no qa variable) | 9 | 100 s |

Totals: 196 passed + 9 = 205 passed, 3 skipped, 1 xfailed, 0 failed. Wall time about 2258 s (37.6 min) under qa, plus 100 s.
Skips (read at `test_shiny_smoke.py:220,232,625`): "right sidebar hidden only for pipeline-static", "Gallery/DevStudio hidden for simple/static", "recipe choice absent for pipeline app features": they run only when the app is launched with pipeline-static or pipeline-exploration-simple, which nobody does here. NOT COVERED, not passed.
The dev control (other reviewer) had one flaky failure `test_shiny_apply_blocked` (passes alone 3 times); in my run it passed at the first try. No browser failure here, so no re-run was needed.

### C3. `python -c "from app.src.main import app; print('OK')"`: OK.

### C4. The three proofs (ran on head `5d9d5404`)
- Pictures (`PYTHONHASHSEED=0 ... recipe_pictures.py --check picture_baseline_15394ef5`, 43 s): the tool printed that `app` and every `libs/*/src` package come from the worktree. Result `error-changed: 1, identical: 50`, "PICTURES NOT IDENTICAL", exit 1. The ONE changed row is `test_logic::::` (the empty orphan `config/data_analysis_recipes/experimental/test_logic.yaml`): stored "the recipe check did not cover: actions, components" now "... actions, components, engines". Not a picture. Nothing else differs. Baseline untouched. This is the open F3 (D-0255 wants the control to pass: decision on the orphan file or the stored text).
- Golden baseline (`golden_baseline.py --check app/tests/golden/baseline.json`, 5 s): `result-identical`, exit 0.
- Gallery previews (`gallery_previews.py --out final_check/gallery_previews`, no `--apply`, 23 s): `identical: 34; size only: 0; differs: 0; new: 0; error: 0`. No preview rewritten.

### C5. Quick audits
- `audit_old_words.py --check`: exit 1, "retired words remain" (also exit 1 on dev). Counts branch vs dev: manifest 59 vs 29 content, recipe 10115 vs 8873, persona 61 vs 60, connector 5 vs 4. New uses by the branch: `manifest` x19 in `assets/scripts` and x11 in `app/tests` (the picture check's own `manifest.json`, a different meaning than the retired one), one more `SPARMVET_PERSONA`/`SPARMVET_CONNECTOR` in `app/tests/test_cache_version_5.py:219` (a list of old variable names that the test clears, as four other tests do). Not new failures, but the count rises.
- `audit_uml_model.py --project-root .`: 8 violations (5 PKG_EDGE_MISSING, 2 PKG_EDGE_STALE, 1 TEST_BROKEN `test_audited_rows_and_drops_are_exported`). The same 8 lines on dev (ran the audit in the main folder and compared the lists). The new recipe shape added none. No tag points to something the branch deleted without replacement.
- `check_doc_links.py`: branch 11 problems, dev 19. No problem new on the branch (the list differs from dev's only by line numbers and by 8 entries the branch fixed). One dangling name that both trees share: `libs/viz_factory/tests/test_stat_function_names_drawn.py` (deleted by dev) still named in the `consumed_by` of `libs/utils/src/utils/formula_check.py:37` and in the dependency index (dev has it too).
- `audit_deps_verify.py`: exit 0 (PASS). It only checks that a block exists.

### C6. Compared with the dev control run (`tmpAI/coordinator/CONTROL_RUN_dev_2026-11-18.md`, dev `efd1cd5f`, read after my runs)
- Dev headless: 2 failed, 10549 passed. Mine: 3 failed, 11242 passed (about 690 more tests on the branch). The two dev failures are my failures 2 and 3. Dev's fix branch `task/dev-control-fixes` (`41a8068d`, tests only, in `tmpAI/coordinator/dev_control_fixes_report.md`) repairs both; its report says this branch must take that version of the two test files once it is merged.
- Dev browser: all pass; one flaky `test_shiny_apply_blocked` (passed alone 3 times). Mine: all pass. Dev smoke_blueprint 17, branch 21 (4 more; two of them are the plot-open class, I did not trace the other two).
- Dev flag table equals mine (qa ghost_save false, selector visible true, ...).
- Failure 1 (the probe leak) is only on this branch.

## D-0307 (tier 1 and tier 2 can still be built) on this head
What I have as evidence (ran): HOME's tables of tier 1 and tier 2 for every shipped recipe: golden `result-identical`; the 17 plots of the demo recipe and the other 33 drawn from those tables: pictures identical (50); the export holds `T1_data.tsv` and `ResFinder/T2_data.tsv` (`test_export_download.py`, 9 passed); Blueprint: the 21 smoke tests pass, among them all 17 plots open with mapping, layers and a data glimpse with a row count; `test_blueprint_tier_files.py` (headless, passed) writes steps into the right tier file and refuses another tier's step.
NOT re-run: the browser gesture "pick a tier-1 step, Apply, Save, reload, HOME draws" on THIS head. That proof was run on `64d99e3f` (`tmpAI/engine_keys/BLUEPRINT_T1_T2_PROOF.md`: worked for tables, failed for joins on both trees). Since `64d99e3f` the Blueprint code changed in three small places (plot view, tier refusal text, join step name, `include_paths`), each with its own tests that pass; nothing in a table's Apply and Save path changed. A re-run of that gesture is still the only way to say "ran" for the merged head.

## VERDICT
**Not yet** at `5d9d5404`. The product code is sound in everything I read and ran; no silent result change, nothing lost in the merge, all browser files pass. What stands in the way (small):
1. One test leak caused by this branch: `libs/viz_factory/tests/test_registration_errors.py` cleans two registries and not the new `COMPONENT_ENGINES` (`registry.py:29,81`), so a full serial `pytest libs app/tests` fails `test_engine_registry.py::test_every_registered_name_has_an_engine_in_the_tables_given_to_the_checker`. Fix in the test: pop the probe from `COMPONENT_ENGINES` and add that registry to the `registries_untouched` fixture. After it, the full headless run should have only the two dev failures.
2. The two dev failures (`test_plot_callers_are_checked[export_handlers]`, `test_suggestion_label::test_home_prints_...`) are stale tests of dev. They go away when `task/dev-control-fixes` is merged into dev and taken by this branch; if this branch merges first, they fail on dev as they do today.
3. Still open from the earlier review, needing Eve or a scribe: F2 (four rule passages, her page `RULE_PASSAGES_for_eve.md`), F3 (the orphan `experimental/test_logic.yaml` and its stored row: the picture check exits 1 until decided; D-0255), F5 (the removal task for the tombstones of the four `plot_defaults` keys is not in `tasks.md`; `tasks.md` is identical to dev).
Not blockers but to know: `audit_old_words --check` fails on both trees and its counts rise on the branch; the 3 skipped smoke tests and the flag combinations of Part B are not covered.

## What this run does not prove
- Anything under an app features other than `qa` except that each of the eight starts and shows Home (`test_every_app_features_starts`): ghost save on, selector hidden, export off, `interactivity` off, agent with a real backend.
- The Blueprint "pick a step, Apply, Save, reload" gesture on this head (above).
- Two users at once, other browsers, a real deployment (container, Posit Connect), real user data (all data is the shipped test data).
- That the tests can fail: I did not break any code once (read-only role). I judged by reading that the new `test_export_download.py` asserts can fail. The picture check compares pictures drawn by this code with pictures drawn before the change: it cannot see a plot that failed in both.
- The 5 skipped and 31 xfailed headless tests were not listed one by one.
- Order effects beyond the one full serial run (a leak like failure 1 shows only when two files run in one process).
- Merge text conflicts with `task/dev-control-fixes` (not tried).

## Files
Report: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/engine_keys/FINAL_REVIEW_and_CONTROLS.md`. Raw outputs: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/engine_keys/final_check/` (`headless.txt`, `browser/`, `pictures_check_output.txt`, `golden_check_output.txt`, `gallery_previews_output.txt`, `audit_*.txt`, `doc_links*.txt`, `deps_verify.txt`). The worktree is clean; no app or browser of mine is running.
