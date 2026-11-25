# Merge of dev into task/engine-keys (2026-11-18)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`. Start head `fa7f856b`, dev `efd1cd5f`. Worktree is clean after the last commit.

## Commits
- `514a54a4` merge: take dev into task/engine-keys (the Export changes, the session import, the Gallery fixes)
- `e1dc05eb` test(export): the new export tests of dev write their recipes in the new shape
- `d4baef25` test(engine-record): the keys of the effective run before the engines include the plot warnings of dev
- `98d37ad5` test(plot-seeds): read the baked plot entry directly (the entry is the plot)
- `9f08d931` test(export): the real download holds every plot as SVG and no export_scope
- `5d9d5404` docs(deps): regenerate the dependency index after the merge of dev

## Conflicts (7 files) and how they were resolved
1. `libs/utils/tests/test_recipe_check.py`: kept this branch's new-shape ST lines; re-added dev's extra ST06 case (`pl.col('v').shuffle(seed=1)`) in the new shape (`["data_schemas"]["A"]["tier1"]["steps"]`). No other dev line of that file used the old shape (the file passes in full).
2. `app/handlers/session_handlers.py`: import is now one block holding `SessionDeleteError, key_drop_notice, normalise_audit_steps, session_id_collisions, session_input_id_parts, split_key_drops`. The `@deps` consumes line holds `get_session_import_limits` (dev) and `split_key_drops, key_drop_notice` (this branch).
3. `app/modules/session_manager.py` (header only): union. provides: `extract_primary_keys, split_key_drops, key_drop_notice` (this branch) + `SessionImportLimits, session_import_limits_from, session_input_id_part(s), SessionImportRefused, SessionKeyExists` (dev); consumes: both (join_keys, recipe_tiers, `re`); consumed_by: both.
4. `app/src/bootloader.py` (header only): union. provides + `get_session_import_limits`; consumes keeps `cache_keys` (CACHE_VERSION_META ...), `anchor.py` and adds `session_manager (session_import_limits_from)`.
5. `app/handlers/home_theater.py` (imports): kept `from utils.engines import plot_engine_slot`; dropped `fix_label` (dev removed its only use; `grep fix_label` finds nothing). The call of `define_export_server` has no `active_home_subtab` (dev's removal; auto-merged and checked: the argument is not in the call and not in the function signature; the other use of `active_home_subtab` in `define_filter_audit_server` is unchanged).
6. `app/tests/test_export_download_path.py`: `SimpleNamespace(import_bundle_upload=None, export_field_change=None)` (dev) + `viz_factory=PlotEngines()` (this branch).
7. `app/handlers/export_handlers.py`:
   - Header: dev's provides (the `EXPORT_*` constants) and dev's consumes, with `collection_tier2_key` (this branch) added to the `cache_keys.py` entry; this branch's `engines.py` / `engine_record.py` consumes line kept.
   - Plot loop, after `fig = viz_factory.render(...)`: both additions stand one after the other in the same `try`: first `drawn_records[p_id] = viz_factory.record_of(...)`, then dev's reading of `plot_warnings(fig)` (with `_warnings_unreadable` and `_plot_warning_rows`).
   - Auto-merged parts, checked by `git diff dev -- app/handlers/export_handlers.py` (this branch's changes on top of dev are only: the engine imports, `export_plot_entries`, `plot_report_name`, `collection_tier2_key`, `drawn_records` and `failed_plot_record`, `**plot_engine_slot(...)`, `"engines": engine_record(...)`, the README engines line) and `git diff HEAD~1^ ...`: dev's scope removal, `export_fields_store`, the echo and the keyed session message are all present. `grep` finds no `export_scope`, `scope_label`, `active_pid` in the handler; `all_plots` is defined once (`export_plot_entries(cfg.raw_config)`, line 1008) and used consistently. The file compiles, the app imports (`from app.src.main import app` prints OK), and the headless download tests pass.

## Tests adapted (never weakened)
- `app/tests/test_export_all_plots_and_defaults.py`: its three-plot recipe was written in dev's old shape (`label:`, `spec:` under a plot, plot content two levels deeper). Now `ui_label` and the plot content in the plot entry. 2 failures before, pass after.
- `app/tests/test_export_plot_warnings.py`: the missing-font test searched the old indentation of the layer (14 spaces) and added a theme layer at it. Now the new indentation. 1 failure before, pass after.
- `app/tests/test_engine_record.py`: `OLD_KEYS` ("the record adds one key and changes none of the others") lacked dev's `plot_warnings`, `plot_warnings_unreadable` keys. They are dev's, not this branch's: added to the set; the assertion (exactly one new key, `engines`) is unchanged.
- `app/tests/test_plot_seeds.py`: dev's new test read `plots[...]["spec"]`; in the new shape the entry is the plot. 3 failures before, pass after. (Dev's other new tests of that file pass unchanged.)
- `app/tests/test_export_download.py`: strengthened (not adapted): the first test now asserts that the bundle holds one picture per plot of the `engines` record, all `.svg`, and no `export_scope` in README or `effective_run.yaml`. Reason: the brief asks to say from the result that the bundle holds all plots as SVG, and the test did not check it (the owner's rule: D-0303, check that the test tests what we think).
- Not changed because already fine: `test_export_download_path.py` handler call (`PlotEngines()`), `test_session_keys_missing_told.py` (passes a `MagicMock`: it passes, run it: 304 ok in the set below), `slow_switch_app.py` and the session/gallery/UML tests (no recipe in the old shape; checked by grep and by the runs).

## Compiled but wrong: what I found
Nothing in the handler. The three wrong places were all test code written for dev's old shape (above), found by running the headless export set (3 failures) and the seed and record tests (4 more). The first full run of the export set took 6 min 42 s because `test_export_report_texts.py` renders with quarto.

## Records, rules, pyproject
- Records (`decision_ledger.md`, `tasks.md`, `.claude/logs`), `pyproject.toml`, `CLAUDE.md`, `.claude/settings.json`: identical to dev (`git diff dev --stat` empty). The branch never edited the records (`git diff <merge-base>..fa7f856b --stat` empty).
- Rule files: `git diff dev...HEAD --stat -- .claude/rules` lists six files only: `rules_agent_role_bioscientist.md`, `rules_data_analysis_recipe_structure.md`, `rules_data_engine.md`, `rules_gallery_standards.md`, `rules_test_lab.md`, `rules_viz_factory.md` (138 insertions, 133 deletions): the branch's rule commit `724c83ce`. Dev changed no rule file since. Not touched.
- Dependency index regenerated with `assets/scripts/build_dep_graph.py --root <worktree>` (commit `5d9d5404`). `scripts/audit_deps_verify.py`: PASS (21 files).

## The flags of `qa` (read from `config/app_features/qa.yaml` of the merged tree)
- export_enabled: true
- interactivity_enabled: true
- session_management_enabled: true
- t3_sandbox_enabled: true
- blueprint_enabled: true
- blueprint_agent_enabled: true; `blueprint_agent.backend`: `disabled` (the agent switch is on, the backend is off)
- testing_mode: true
- automation.ghost_save.enabled: false
- also: `data_analysis_recipe_selector.visible: true`, `data_analysis_recipe_edit_enabled: true`, `gallery_enabled`, `test_lab_enabled`, `comparison_mode_enabled`: true

NOT covered by these runs: ghost save on (the save at Apply of the audit and Blueprint's draft autosave); a setup with the recipe selector hidden (pipeline-static, pipeline-exploration-simple, web-demo: the watched selector is then absent from the page); `export_enabled` false and `interactivity_enabled` false; the agent with a working backend (`claude_cli`); Firefox/Safari.

## Test counts (one process at a time; load 2 to 4 before each run; another session ran a full suite in the main folder at the same time)
Headless:
- `libs/utils`: 2247 passed.
- `libs/id_reconciliation`, transformer `test_polars_actions_equal_polars.py`, viz_factory `test_stat_function_formula.py`, `test_registry_audit_vs_plotnine.py` (the files dev changed): 514 passed, 11 xfailed.
- `app/tests/test_export_*.py` except the four browser ones (`download`, `ready_button`, `busy_wait`, `inputs_survive_plot_tab`): first run 243 passed, 4 skipped, 3 failed (the two files above); after the fix `test_export_all_plots_and_defaults.py` + `test_export_plot_warnings.py`: 13 passed.
- The named session, engine, key, gallery, UML, old-keys and writers files (`test_session_import_safety`, `test_session_import_copy_panel`, `test_session_id_collisions`, `test_session_manager`, `test_session_keys_missing_told`, `test_audit_join_key_drops`, `test_home_join_keys`, `test_engine_record`, `test_engine_registry`, `test_engine_keys`, `test_cache_version_5`, `test_gallery_texts_and_links`, `test_audit_uml_model`, `test_no_old_recipe_keys_read`, `test_writers_emit_format_one`): 304 passed, 1 xfailed, 1 failed (`test_engine_record`, fixed: then 21 passed).
- `test_plot_seeds.py`: 84 passed after the fix; `test_import_errors_visible.py` and `test_gallery_texts_and_links.py` passed.
- `python -c "from app.src.main import app; print('OK')"`: OK.

Browser (qa, one file at a time):
- `test_shiny_smoke.py`: 37 passed, 3 skipped (same as before the merge).
- `test_export_download.py`: 9 passed; after my added assertions the first test alone: 1 passed, and its printout `EXPORT_PLOTS=17 FORMATS=['svg']` (see below).
- `test_export_ready_button.py`: 18 passed (5 min 57 s).
- `test_shiny_export_race.py`: 13 passed (2 min 59 s).
- `test_shiny_export_fields_per_session.py`: 3 passed.
- `test_shiny_session_keep_both.py`: 2 passed.
- Also run: `test_shiny_session_restore.py` 1 passed; `test_export_inputs_survive_plot_tab.py` 3 passed; `test_export_ready_busy_wait.py` 2 passed (uses `slow_switch_app.py`).

## The three proofs (run on the merged head `5d9d5404`)
- Pictures: `identical: 50`, `error-changed: 1` (the known row, the empty orphan `experimental/test_logic.yaml`: "the recipe check did not cover: actions, components" now "... actions, components, engines"); exit 1 by that row only. No other difference.
- Golden baseline: `result-identical` (exit 0).
- Gallery previews: `identical: 34; size only: 0; differs: 0; new: 0; error: 0`.

## The real export on the merged branch
From `test_export_download.py` (qa, the demo recipe, no format chosen by the test): the bundle holds 17 plots (`EXPORT_PLOTS=17`), all `.svg` (`FORMATS=['svg']`), the set of pictures equals the plots of the `engines` record (`record["plots"]`, each `plot_engine: python-plotnine`, `drawn: true`), `record["tables"]` all `tier1: python-polars`, `library_versions` for `python-polars` and `python-plotnine`; `export_scope` is in neither the README nor `effective_run.yaml`. I did not break-once the new assertions (they read the same values the test already reads; the headless `test_export_all_plots_and_defaults.py` has the fail-able version of the same rule).

## What I did not run
The full `app/tests` and `libs` suites (the reviewer's next step), `test_shiny_smoke_blueprint.py` and the other Blueprint browser files, `test_every_app_features_starts.py`, any setup other than qa, and the docs/link audits (`check_doc_links.py`, `audit_old_words.py`).

## Open points
- None needing a decision. Note for the reviewer: dev's `test_export_report_texts.py` renders with quarto and makes a headless export run take about 6 minutes.
- Mixed-version note: the three failing tests I fixed show the pattern to look for when dev adds new tests: any recipe text written with `label:`/`spec:`/`wrangling:` or `["spec"]` is in the old shape.
