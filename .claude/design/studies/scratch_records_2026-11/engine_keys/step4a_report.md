# ENGINE-KEYS step 4a: report (worktree .claude/worktrees/engine-keys, branch task/engine-keys)

Status: step 4a is DONE and committed (nothing uncommitted). What is not done is listed below. No push, no merge into dev.

## Merge of dev
`git merge dev` (30be8958): clean, NO conflicts (commit ed543caf). `libs/utils` after it: 2095 passed. The picture tool needs no `--allow-outside-checkout` any more (the libraries and `viz_gallery` come from the checkout: the run prints the checkout path for all 10).

## Commits (after b55fc55c)
ed543caf merge dev; 6ec6a805 transformer `DataWrangler.tier_steps` (replaces `_resolve_tier`) + 68 pair fixtures + debug scripts; 2e609e3a viz_factory (entry keys, no title seed, no built-in theme) + `utils.recipe_check.plot_keys` + spec key `entry_keys`; b4975b63 orchestrator, validator + guard, server, gallery_examples, viz_gallery writer, golden_baseline, retest_walkthrough, `test_gate_reads_every_step.py`; bda106c6 tests of app/ adapted.

## THE PROOF (command of the step 1 report, no --allow-outside-checkout, PYTHONHASHSEED=0)
Result `identical: 51, PICTURES IDENTICAL` (output `tmpAI/engine_keys/picture_check_step4a_output.txt`, pictures `picture_check_step4a/`). The 51 baseline entries are: 41 drawn (pixel-identical), 4 errors (same error text), 6 rejected recipes (same reason; `retest_bad_select_column` is rejected again for its real reason: `unable to find column "phenotype"`; before this step it passed the gate). No plot differed, so no tool fix was needed (the rewrite tool is unchanged).
Sensitivity (break once): theme line removed from `3_test_no_joins` -> `different: 1 (213804 pixels)`; restored.
- Golden baseline `--check app/tests/golden/baseline.json`: `result-identical`.
- Gallery previews: `identical: 34; size only: 0; differs: 0; new: 0; error: 0`.

## What changed (read the code at these places)
- `libs/transformer/src/transformer/data_wrangler.py`: `tier_steps(body, tier)`; refuses `wrangling`, a join `steps` container, a tier as list/None, a tier without `steps`, extra keys; join in tier2 still refused. No reader accepts the old shape.
- `app/modules/orchestrator.py` (T1 of a table and of a join), `app/src/server.py`, `app/modules/gallery_examples.py`, `assets/scripts/golden_baseline.py`, `assets/scripts/retest_walkthrough.py`, debug scripts of transformer and viz_factory: new shape.
- viz_factory: `plot_config_resolver.py` reads the entry keys and content keys from `utils.recipe_check.plot_keys()` (new key `entry_keys` under `elements.plot` of `recipe_spec.yaml`, one list shared with the checker); entry keys ignored, an unknown key and `title` refused (message names the labs layer). Title seed removed. `theme_bw` removed (`_L1_LAYERS`, `_BUILTIN_DEFAULTS`, fallback name `theme_gray` = only a name; docstring). `theme_dashboard` description no longer says it is the default.
- `libs/viz_gallery` `example_recipe.py` (writer), `taxonomy.py` (reader): new shape.
- Gate guard (D-0050): `app/modules/data_analysis_recipe_validator.py`: `_tiered_bodies`, `count_steps_written` (count that does not know the tiers), `unread_steps_problem`. `engine_load_problems` and `validate_data_analysis_recipe_data` report "the check read N of the M steps written here ... fault of the app" instead of passing. Limit: in the data check the "ran" number is the count of the engine's reader (`DataWrangler.tier_steps`, the same call `prepare_ingredient` makes), not a count taken inside the run.
- 68 transformer test-pair recipes (`libs/transformer/tests/data/*_data_analysis_recipe.yaml`, standalone fixtures, not recipes) converted to the new shape (scratch tool `tmpAI/scratch/convert_pairs.py`, data-level oracle: 68 compared, 0 differ).

## Tests (ran)
- libs: utils 2098, transformer 2256, viz_factory 2266 passed + 27 xfailed, viz_gallery 70 passed + 1 skipped, ingestion 59, connector 27, id_reconciliation 81 + 3 xfailed, test_lab 103: all green.
- `libs/blueprint_arch`: 17 red (as allowed): test_agent_tools 1, test_branch_plan 8, test_lineage_nav 5, test_t3_translator 3 (writers/readers of `wrangling`, `spec`, `steps`).
- `app/tests` without browser files: 30 failed, 3273 passed, 4 skipped, 1 xfailed (`tmpAI/engine_keys/red_after_step4a_app.txt`, ids in `red_after_step4a_app_ids.txt`). Red (all need a writer or HOME code of 4b/4c):
  - test_writers_emit_format_one 14: fork of an export (`libs/blueprint_arch/.../t3_translator.py` `build_mode2_recipe`), Blueprint branch (`branch_plan`, navigator), the scaffold script `assets/scripts/create_data_analysis_recipe.py:166,187` (writes group `label` and `wrangling`).
  - test_step_order 13: all use `build_mode2_recipe` (the fork), already adapted to the new shape.
  - test_scripts_need_the_app_path 1: same scaffold script.
  - test_wrangler_upload_step_numbering 1: `_fragment_report` of the validator and the Blueprint upload read a `wrangling` fragment (old shape): Blueprint upload, 4c.
  - test_export_inputs_survive_plot_tab 1: HOME/Export read `spec`.
- Browser tests (test_shiny_*, test_export_download, test_every_app_features_starts): NOT run (as ordered). Their fixtures that build recipes (`group.update({"ui_label"...})`, reads of `["spec"]`) were adapted but are unverified.
- Break-once (`tmpAI/breakonce4a.py` in the worktree, output `breakonce4a_out.txt`): 8 breakages, 8 caught, files restored: tier_steps accepts `wrangling`; guard never reports; theme_bw back; `title` canonical again; entry keys refused; gallery writer writes `spec`; `entry_keys` without taxonomy; orchestrator reads tier2.

## Starting points for 4b (HOME, Export, audit, sessions) - read `spec`/`steps` today
`app/handlers/home_theater.py:106,246,253,429,555`; `audit_stack.py:289`; `export_handlers.py:948` (also the `plot_engine` hand-over, `:1144-1147`, and the lineage graph through `build_plot_lineage`); `app/modules/plot_seeds.py:167`; `session_manager.py:135` (`join_def.get("steps")`); `wrangle_studio.py:572,685` is 4c. Tests that still pin the old shape because their code is 4b/4c and unchanged (they pass today, they will go red when the code moves): test_plot_seeds, test_old_session_typed_values, test_rename_context, test_blueprint_known_defects, test_blueprint_save_roundtrip, test_upload_recipe_check, test_upload_load_never_exits.
## Starting points for 4c (Blueprint, Test Lab writers)
`libs/blueprint_arch`: `data_analysis_recipe_navigator.py` (135-141,185,271-335,456-458,485,692-701,738-797,1057), `blueprint_mapper.py` (121-411), `t3_translator.py:183`, `group_plot_manager.py`, `agent_tools.py:330`, `branch_plan`; `app/handlers/blueprint_handlers.py` (489-640,663-678,823-913,1227-1245); `libs/test_lab/src/test_lab/bootstrapper.py:162,187`, `scaffolder.py:203,226`; scripts `assets/scripts/create_data_analysis_recipe.py`, `SF_create_data_analysis_recipe.py`, `debug_bootstrap_viz_yamls.py`; the validator `_fragment_report` (old `wrangling` fragment upload) and its tests.

## Needs a decision (D-0165)
1. D-0253 says figure text only in `labs`; the plot content still has the flat keys `labels:` and `guides:` (spec `elements.plot`, resolver applies them after the layers). Not decided what happens to `labels:`. Left unchanged.
2. `PYTHONHASHSEED` finding (plot `complex_template::Overview::gene_presence_by_country` depends on the seed) is still open; the check uses seed 0.
3. Other built-in defaults that are an app choice (D-0258: report, change none): `coord_cartesian` and `facet_null` still injected at L1 (they equal plotnine's defaults); the L3 automatic rotation of long axis text (`optimisation.auto_axis_text`) changes pictures without a recipe key; the random seed default stays (decided).
4. `data_engine` inside a tier is checked by the checker but not read by the engine yet (step 5).
5. The ~165 YAML files in `libs/viz_factory/tests/test_data/` (plot contents of an integrity suite that already does not run: it uses the pre-format-1 shape): not touched; 32 name `theme_bw`, 100 name no theme; no pytest test draws them, so no test relied on the built-in theme there. Whether to delete or convert them is not decided.

## PROVISIONAL (mine)
`entry_keys` key in the spec; function names `plot_keys`, `count_steps_written`, `unread_steps_problem`; provenance word "plotnine" for the theme; `PLOTNINE_DEFAULT_THEME = "theme_gray"` as a reported name only; the test-pair fixtures converted instead of left; the title hint text; the correction of the `theme_dashboard` description (D-0256 will correct descriptions anyway).
## Decisions table
D-0250 tier as key: `tier_steps`, `recipe_tiers` (test_data_wrangler, test_gate_reads_every_step). D-0237 no spec: viz_factory entry reading, server, gallery_examples, golden_baseline (test_no_silent_error, test_plot_config_resolver). D-0253 title/labs: title seed removed, `title` refused (TestTitleIsNotSeededFromTheSpec, test_title_key_is_refused). D-0258 theme: theme_bw removed (test_theme_slots 3 new tests, test_theme_settings_reach_the_figure route b adapted). D-0251/D-0255: gallery bundles and every recipe identical by picture, golden and previews. D-0050: gate guard (test_gate_reads_every_step 11 tests). D-0271: HOME, Export, Blueprint, Test Lab not touched.
## Exact next action
Step 4b: make HOME/Export/audit/sessions read the entry directly (starting points above), then run the picture check and the 30 red tests that belong to 4b; step 4c: writers (fork, branch, Test Lab, scaffold scripts, fragment upload). Run: command of step 1 report from the worktree root.
