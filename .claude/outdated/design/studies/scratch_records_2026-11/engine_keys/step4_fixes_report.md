# Step 4 named fixes: report
Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`, from `cd06d045` to `ba7b60a6`. Everything committed; no process left.

## Commits
- bbe315fe test: upload and scaffold tests use the tier file shape (fix 1)
- 57c03944 docs(blueprint): agent instruction text (fix 2)
- 3daf60a3 fix(utils): loader no longer unwraps `output_fields` (fix 3)
- 2dda0fc7 fix(blueprint): click on an old-shape join tells the user (fix 4a, 4b)
- b04b130b test(blueprint): browser test (fix 4c)
- 3d55b00e test(home): join keys (fix 4d)
- ba7b60a6 docs(deps): @deps lines and the regenerated index (fix 5)

## Per fix
1. 10 tests were red at this head: 5 in `test_id_cleaning_steps_reach_a_recipe.py` (a fragment is `{steps: [...]}`), 4 in `test_upload_recipe_check.py` and 1 in `test_upload_load_never_exits.py`. Adapted to `{steps: [...]}` for a tier file and `tier1: {steps}` for the tiers of a table. New test `test_old_shape_upload_is_refused_with_UP02_and_nothing_is_read` (three old shapes: `wrangling` mapping, `wrangling` list, `tier1` as a list: one line each, `[UP02]`, no step checked). Fail-once: with the old-shape detection switched off the new test fails (1 failed); restored.
2. `config/ui/agents/blueprint_default.md`: rewrote the shape passage (tier under its key with `steps:`, tier file, join with `polars_join`, group `ui_label`, plot entry directly with `ui_label`/`ui_title`/`layers`, `<contact>`), the action names (`polars_cast`, `modif_filter`, `polars_with_columns`, `polars_join`), the tool text (no `output_fields`) and the plot components (`geom_bar`, `geom_tile` instead of `bar_logic`, `heatmap_logic`). Examples copied from the migrated ST22 recipe. New test `app/tests/test_blueprint_agent_instructions_shape.py` (31 tests). The check chosen: the examples are fragments (no data), so the full checker cannot run on them. The test checks, for each yaml block: valid yaml; keys of table, join, group, plot entry and layer against `recipe_spec.yaml`; no old key (`wrangling`, `spec`, `output_fields`, `label` on group or plot); every step has a registered action and fits its form (the upload check); every layer is a registered component. It does not check that an example draws a figure. Fail-once: old `wrangling:` plus old action name gave 9 failures; `label:` on the plot gave 2; restored.
3. `config_loader.py`: `redundant_keys` is now `{"input_fields", "source"}`. What happens now to a file that holds only `output_fields`: ConfigManager leaves it as written (double nesting `output_fields: {output_fields: ...}`, nothing reads it), and the strict loader (HOME's gate) refuses it with `F01` ("the included file starts with output_fields, the key it is included under"). Verified by a probe and by the new test in `libs/utils/tests/test_config_loader.py`. Grep and a yaml scan of config, assets, libs, app and docs: no file whose only key is `output_fields` (or `input_fields`, or `source`). Fail-once: putting the key back makes the new test fail. Run after the change: libs/utils, libs/test_lab, libs/blueprint_arch (2645 passed) and the writers, load gate, data check, retest files (81 passed, 1 xfailed).
   - What the `input_fields` and `source` unwraps do: ConfigManager's `!include` handler removes a single top key when it is `input_fields` or `source`, so a file written as `input_fields: {...}` loads as if written without the wrapper. The strict loader reports the same file as `F01`. The navigator's `load_fields_file` does the same for `input_fields` only. Who relies on it: no shipped file (scan: 0). Callers of ConfigManager that would see the effect: scripts, Blueprint (`load_config_or_problems`), the engine outside HOME's gate. Tests: `test_a_tier_file_that_holds_only_steps...` keeps `input_fields` unwrapped on purpose. Left unchanged as asked. DECISION NEEDED (Eve): remove both unwraps too (a hand-written old file would then load double nested and be refused by the checker), or keep them as a tolerance.
4a. `wrangle_studio.py` `handle_node_selection`: the call `DataWrangler.tier_steps` is now in a try; a `DataAnalysisRecipeError` gives an error notification in plain words ("The steps of the join 'J' cannot be shown: <message> <tip>", 12 s), an empty stack, and no raise. New `app/tests/test_blueprint_node_selection.py` (5 tests: new-shape join shows its tier 1 steps; empty tier; not a join; old `steps:` container; tier written as a list). The closure is cut out by `ast`. Fail-once: with `except KeyError` instead the 2 old-shape tests fail; with a bare `.get("steps")` instead of `tier_steps` 3 fail; restored.
4b. New `app/tests/test_blueprint_plot_preview_engine.py` (3 tests): the dict given to `VizFactory.render` holds `plots`, `plot_defaults`, `plot_engine`; the entry's own engine wins over the recipe's; an engine the app does not build is told in the place of the plot (real factory behind a recorder). Fail-once: removing `**plot_engine_slot(...)` fails 3; swapping its arguments fails 2; restored.
4c. Browser test `TestBlueprintNodeClick` in `test_shiny_smoke_blueprint.py` (2 cases): taps a join node and a plot node of the TubeMap (cytoscape `tap`, the same bridge as a click) and checks the data status line says "N rows" and no error shows. Fail-once: renaming the input in `ui.py` makes both fail; restored. Two findings, see "Findings".
4d. New `app/tests/test_home_join_keys.py` (7 tests): demo keys `Gene_name, VF_gene, sample_id`; dropping a key column is refused with "Cannot drop join key column(s): ..." and nothing is sent; all deselected keys are named; dropping a non-key goes to the dialog; with no keys nothing is refused (the state before 4b); a filter on a key is allowed, stays `filter_row` and carries `primary_key_warning=True`; a filter on another column does not. The closures `_col_drop_to_audit` and `_filter_send_to_audit` are cut out by `ast`. Fail-once (3 breaks): refusal off (2 fail), warning off (2 fail), key reading off (5 fail); restored.
5. `@deps` `consumes` added: blueprint_handlers (`utils.recipe_check` plot_keys, `utils.recipe_tiers` step_list), wrangle_studio (`utils.engines`, `utils.errors`, `DataWrangler.tier_steps`), home_theater and export_handlers (`utils.engines`), session_manager (`utils.join_keys`, `utils.recipe_tiers`); navigator `provides` names the new `tier` key and the changed sibling keys. Only imports that each file really has (checked by grep). `build_dep_graph.py --root <worktree>` writes `tmp/dep_graph.json` (git-ignored) and `.claude/knowledge/dependency_index.md` (tracked, owned by the script): regenerated and committed (it also picked up older drift: new test files, `recipe_pictures.py`, `engine_keys_migration.py`, `DataWrangler.tier_steps`).

## Orphan recipe files (fix 6, report only)
Script `tmpAI/orphans.py`: 109 yaml files under `config/data_analysis_recipes/`, 16 masters, 6 files that no yaml `!include`s (includes resolved against every parent folder). No code or test names them as a file to load (only `app/tests/test_resfinder_abromics_fragment.py` lists two as "found 2026-11-15, not decided", and old docs/tombstones name paths).
| file | shape |
|---|---|
| `experimental/test_logic.yaml` | empty (0 bytes) |
| `pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml` | OLD plot: `title`, `family`, `pattern`, `difficulty`, no `ui_label` |
| `pipelines/stress_test_master/plots/final_plot.yaml` | OLD plot: `title`, no `ui_label` |
| `pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml` | OLD: a bare list of steps |
| `pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml` | OLD: field definitions (`is_primary_key`, `type: numeric`), in the wrangling folder; the review did not name it |
| `pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml` | NEW shape (`steps:`, converted by step 3), included by no recipe by design (its header says so) |
So 5 are old or empty, 1 is new. Not touched.

## Findings (not fixed, outside the named fixes)
- The Blueprint plot preview `architect_active_plot` is not mounted in the page (no `output_plot`): no browser test can see a drawn plot. The test for 4c checks the data status line instead; the preview dict is covered headless (4b). Open choice: mount it, or remove the dead preview code.
- Tapping a SOURCE table node (TubeMap roles `trunk`, `add`, `meta`, and the `wrangle` node of a table) loads no data ("No data loaded"), and the server logs `ColumnNotFoundError: unable to find column "scheme"` in `architect_active_table`: the clicked node's steps are applied to the data of another table (`processed_data` fallback). SAME on dev `81980e0c` (I ran the same browser test in a temporary detached worktree of dev, removed after): pre-existing, not from this branch. A join node and a plot node load data. Needs a decision or a task.
- `handle_node_selection` starts with `yaml.safe_load(raw_yaml)` of the master text, which fails on an `!include` tag; for a recipe whose join tier is an include (the demo) it returns early and shows nothing (as before). Only inline joins reach `tier_steps`.
- The yaml scan found `PlasmidFinder_wrangling.yaml` in an old field shape (above).

## Test counts
- libs/utils + libs/blueprint_arch: 2534 passed (with libs/test_lab 2645 passed in the fix 3 run).
- Adapted files, new files, `test_writers_emit_format_one.py`, `test_no_old_recipe_keys_read.py`, `test_blueprint_tier_files.py`: 181 passed, 1 xfailed.
- Browser, qa, `test_shiny_smoke_blueprint.py`: 19 passed (17 old + 2 new).
- Pictures: `PYTHONHASHSEED=0 ... recipe_pictures.py --check picture_baseline_15394ef5`: `identical: 51`, `PICTURES IDENTICAL`.
- `utils.__file__` = the worktree's `libs/utils/src/utils/__init__.py`. Machine load was 1.4 to 3.2 before every run.

## Not done / not checked
- Full `app/tests` (as told). The other browser files (smoke, gate gap, export, every_app_features) were not rerun; none of the changes touch them except `wrangle_studio.py` (covered by the Blueprint smoke).
- The Shiny click itself for fix 4a (the closure is run, not the live effect); the browser test taps a join node of the demo, whose join tier is an include, so it does not reach the new `except` (covered by the headless test).
- No change to rule files, ADRs, CLAUDE.md, settings, pyproject, ledger, tasks, knowledge or design docs (except the regenerated dependency index, which the script owns). PROVISIONAL choices of 4c untouched.
- `dev` not merged, no push.
