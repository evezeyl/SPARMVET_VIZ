# Leftovers of the engine-keys change (worker report, 2026-11-18)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`. Everything committed.

## Commits (on top of 43f06c0d)
1. fix(viz_factory): the plot library reads the plot_defaults keys from the recipe specification and refuses a removed key (D-0220, D-0242)
2. fix(blueprint): the plot-defaults form writes only accepted keys and keeps the seed, the layers and the theme it did not touch (D-0246)
3. fix(utils): the default tip of a recipe error names the required keys of a recipe
4. fix(scripts): migrate_plot_specs.py refuses to run and names migrate_recipe_engine_keys.py
5. docs(uml): the data-check page says what the check does now
6. docs(deps): index regenerated

## A. The four removed plot_defaults keys
- New `utils.recipe_check.plot_defaults_keys()` returns (allowed, removed) read from `recipe_spec.yaml`. The resolver (`plot_config_resolver.py` ~71) takes both sets from it: ONE list for checker and library. Test: `libs/viz_factory/tests/test_plot_defaults_keys.py` (12 with the utils test `libs/utils/tests/test_recipe_check_plot_defaults_keys.py`).
- A removed key that reaches `resolve_plot_config` (script, Blueprint preview) raises `VisualizationError` with the key name and the remedy (theme layer; element_text per axis). Not ignored.
- The warning text for an unknown key (`viz_factory.py` ~284) lists the real keys from the same set.
- Fail-once: set removed-set empty and allow two removed keys: 10 tests failed; restored.
- **A.3 finding:** before this change the resolver did `seed[key] = val` for the four keys (`plot_config_resolver.py` old lines 593-595) and nothing read `seed["default_font_family"]` etc. afterwards: grep over `libs/*/src` and `app` shows no reader. `compute_optimisation_layer` (~439) never reads `seed["optimisation"]` (its axis-text rule runs always). So none of the four had an effect on a picture. This agrees with the picture proof (50 identical). No key to stop on.

## B. Blueprint plot-defaults form (D-0246 first part only)
- New pure module `app/modules/plot_defaults_form.py` (`form_values`, `theme_choices`, `merged_plot_defaults`, `FORM_KEYS`, `NO_THEME`); handler `blueprint_handlers.py` (~1715-1770) uses it.
- Form fields now: **Palette** (text) and **Theme** (select). PROVISIONAL choices: the Theme select has a first choice "(none: plotnine's default)" that writes no theme; the shipped list (theme_light, theme_bw, theme_minimal, theme_classic, theme_dashboard) is unchanged; a theme the block already holds that is not in the list is offered and kept. An empty palette removes the key.
- A save keeps every other key (seed, layers, any accepted key not shown); the block is not rebuilt. If the result is empty the `plot_defaults` key is removed.
- A removed key already in a block is not hidden or removed by the form (the checker names it: D-0050).
- Tests `app/tests/test_blueprint_plot_defaults_form.py` (15): same block after untouched save; seed+layers survive; one field changes one key; no theme writes none; saved block passes the checker (PD codes absent on the ST22 recipe); checker still gives PD02 on a removed key; form fields hold none of the four; handler source names none. Fail-once: merge function rebuilding the block and defaulting to theme_light: 7 failed; handler test failed before the edit.
- **Left for the user to see:** only palette and theme. The new fields (common theme settings) wait for Eve.
- **Finding (not fixed):** in `blueprint_handlers.py` the form's render and effect are placed after `if not bootloader.is_enabled("blueprint_agent_enabled"): return` (~line 1690), so with the agent flag off the form output is not registered. Needs a decision on where the form belongs.

## C. Other leftovers
- `errors.py:63`: tip now names id, spec_version, data_engine, plot_engine, info, data_schemas, analysis_groups. Test `libs/utils/tests/test_default_recipe_error_tip.py` (reads the list from the spec). Fail-once: failed.
- `migrate_plot_specs.py`: one-time migration of ADR-083 (2026-05-20); its output has `spec:` which the checker refuses, and it patches generator scripts. It now exits 2 after argument parsing with a message naming `assets/scripts/migrate_recipe_engine_keys.py` and the by-hand rewrite for factory_id; `--help` still works. Test `app/tests/test_migrate_plot_specs_refuses.py` (3). Fail-once: apply test failed. **Listed for a removal decision.** Docs/rules that still say "run migrate_plot_specs.py" (rule files, `docs/workflows/blueprint_architect.qmd:279`, ADR text) were not touched (not mine).
- `debug_bootstrap_viz_yamls.py:170`: NOT changed. Checked: the files it writes (root `plots:`, `wrangling: []`, `input_fields: []`, `data_path`) are refused as a whole by ConfigManager since Phase 21-B (LEGACY-FLAT-PLOTS-1): `libs/viz_factory/tests/debug_runner.py` on a freshly bootstrapped file and on the shipped `libs/viz_factory/tests/test_data/coord_cartesian_test.yaml` stops with "Root-level 'plots:' key is not a valid authoring format". So removing `output_fields` alone would be a half fix; the whole format is the open decision (3) of `.claude/tasks/tasks.md:220`.
- `docs/UML/data_contract_and_failures.md`: ran `validate_data_analysis_recipe_data` on `demo_abromics.yaml`: no problem. With one `original_name` misspelled in a scratch copy: "dataset cannot be loaded: Column(s) ['sequence_type'] declared in input_fields for 'MLST' not found in the source file (expected file headers: ['Sequence Typ'])" plus the tip. The page said a wrong input_fields name is silently skipped and showed an `output_fields` example: both rewritten (input_fields now stops the load; no `output_fields`; a step naming a missing column is found because the check runs each table's steps on one row: that last claim I read in the code, `data_analysis_recipe_validator.py:468-477`, not run on a polars_select example).

## D. Greps again (step 9)
`default_font_family|facet_panel_spacing|legend_position|optimisation`: 39 lines (saved `tmpAI/scratch/grep1_after.txt` in the worktree). Remaining, with reason:
- `recipe_spec.yaml` (tombstones), `app/tests/test_migrate_recipe_engine_keys.py`, `docs/appendix/data_analysis_recipe_structure.yaml:78` (tombstone note), my new test `test_blueprint_plot_defaults_form.py` (names the removed keys on purpose, and `legend_position` as an argument of `theme_custom`): by design.
- `themes/core.py`, `assets/scripts/figshare_plot_integration.py`, `viz_factory_components.qmd`, `VirulenceFinder_counts_bar.yaml:26`, `visualisation_factory.qmd:103`: `legend_position` is the plotnine theme argument, `theme_legend_position` a component.
- `plot_config_resolver.py` (L3 "optimisation" layer, real), `viz_factory.py:183`, `checked_plot.py:340`, `blueprint_architect.qmd:284`: the word for the L3 layer.
- GONE: `plot_config_resolver.py:72-73`, `viz_factory.py:284`, the form in `blueprint_handlers.py`.

`spec:`: `recipe_spec.yaml:134` (refusal text), `test_migrate_recipe_engine_keys.py:41` and `test_no_old_recipe_keys_read.py:79` (test inputs), `aqua_synthesizer.py:145` (a variable), `engine_keys_migration.py:434,448,799` (the rewrite tool reads the old shape), `migrate_plot_specs.py:224-230` (dead code behind the refusal, listed for removal). No recipe, bundle or doc has `spec:` under a plot.

## Tests (one process at a time)
- libs/viz_factory: 2296 passed, 27 xfailed. libs/utils: 2128 passed. libs/blueprint_arch: 432 passed.
- app: my new/changed files + test_writers_emit_format_one, test_no_old_recipe_keys_read, the Blueprint headless files (failed_load, handlers_names, node_selection, plot_preview_engine, save_roundtrip, tier_files, widget_forms, agent_instructions_shape) + shipped_recipes_hygiene: 170 passed, 1 xfailed.
- qa browser `test_shiny_smoke_blueprint.py`: 19 passed.
- Proofs: pictures `error-changed: 1, identical: 50` (the one row is `test_logic::::`, the empty orphan file, an error text, not a picture; same as before); golden `result-identical`; gallery previews `identical: 34`.

## Needs a decision
1. Remove `assets/scripts/migrate_plot_specs.py` (and update the rule/doc lines that name it)?
2. Where the plot-defaults form belongs (today only registered when `blueprint_agent_enabled` is on).
3. `debug_bootstrap_viz_yamls.py` and `libs/viz_factory/tests/test_data` format (tasks.md:220 (3)).
4. The new form fields (theme settings) wait for Eve (D-0246 second part).

## Not checked
Not run: the full `app/tests`, the other browser files, `libs/transformer` and other libs (no change there). The form was not opened in a browser (it is registered only with the agent flag; the smoke run does not show it). `plot_defaults_form` tests use the checker on the ST22 recipe only, structure level.
