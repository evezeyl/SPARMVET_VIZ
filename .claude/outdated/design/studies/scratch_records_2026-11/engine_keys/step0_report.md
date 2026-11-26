# Step 0 report: recipe_pictures (picture identity tool)

Commit: d57c4bac on task/engine-keys (script + tests, one commit).
Files: assets/scripts/recipe_pictures.py, app/tests/test_recipe_pictures.py (10 tests, pass, ~10 s).

Commands (from the worktree root, PYTHONPATH=., venv python of the main folder):
  assets/scripts/recipe_pictures.py --write <dir>     (all recipe folders, data root assets/test_data)
  assets/scripts/recipe_pictures.py --check <dir> --out <dir2>
  pytest app/tests/test_recipe_pictures.py -q
Baseline: tmpAI/engine_keys/picture_baseline_15394ef5/ (manifest.json + 41 PNG, 960x600). --write took 1 min 32 s (each plot drawn twice). --check took 48 s: 51 identical, rc 0 (PICTURES IDENTICAL). Check output in tmpAI/engine_keys/picture_check_15394ef5/.

Coverage (51 manifest entries; recipes with *.yaml directly in the folder; the 5 folders: pipelines, templates, retest, experimental, app/tests/equality/recipes):
 drawn 41 plots: 1_Abromics_general_pipeline 2, 1_test_data_ST22_dummy 17, 2_test_data_ST22_dummy 3, ..._dirty 3, ..._dirty_no_null_text 3, ..._emptied 2, 3_test_no_joins 1, complex_template 1, demo_abromics 1, figshare_integration 3, left_join_lesson 1, retest_tier2 2, retest_top_n_other 1, stress_test_master 1.
 plots that cannot be drawn today (4, findings, not fixed):
  - 2_test_data_ST22_dummy_emptied / plasmid_prevalence_by_country: VisualizationError, facet_wrap '~Country' needs at least one value (data emptied on purpose).
  - 2_test_data_ST22_dummy_fractional_year, 3 plots: no table, TransformationError polars_cast on Year with decimals (2023.5) (on purpose).
 recipes rejected by the load gate (6, listed with reason, not drawn):
  - audit: data file assets/audit_data/submission_logs.tsv missing.
  - e_coli: data file assets/pipeline_output/ecoli_amr_results.tsv missing.
  - simple_template: data file assets/test_data/simple_data.tsv missing.
  (these three data files are absent in the main folder too: finding; their pictures are NOT covered)
  - retest_bad_select_column, retest_broken_header: broken on purpose (retest).
  - test_logic (experimental): "the recipe check did not cover: actions, components. This is a fault of the app" (finding).
 skipped (9 entries): sub-folders holding fragments/plot files, each listed with the reason. No non-.yaml files, no duplicate ids.
 Not covered: any plot of the 3 missing-data recipes and test_logic, so the migration cannot be proven picture-identical for them.

Unstable plots: none. Two draws inside --write are identical for all 41 plots, and the separate --check run (new process) is identical too.

Break-once evidence: with differing_pixels forced to return 0, 3 tests failed (changed title, changed theme, test_the_comparison_can_fail); restored, all 10 pass. Unstable-detection test uses a forced difference.
Tests (small temp recipes): identical passes; title change; theme change; plot missing; new plot; recipe that no longer loads (error-changed); plot that errors at draw time (error-changed, recorded with error text, same error again = identical); unstable named; skipped listed.

Notes:
- Plot identity is recipe id :: group id :: plot id. The only place that knows the recipe shape is plots_of()/collections_of() in the script; after the migration change those two functions.
- libs/ are installed editable from the main folder; only app/ and assets/ come from the worktree (test_imports_from_checkout passes). No library code changed.
- A recipe's data path is relative to the project root; absolute data paths are refused by the checker (PA01), so tests chdir into a temp folder.

PROVISIONAL choices (mine): size 8x5 in at 120 dpi (same as gallery); palettes read from config/palettes.yaml as the app does; plot drawn without aesthetic_override; --repeat 2 default for the stability test; an "unstable" plot in the stored set is named but does not fail --check; same error stored and now counts as identical; the default recipe folders list; data root assets/test_data.

Row to add to .claude/rules/rules_toolchain.md (not edited, needs Eve's yes):
| `assets/scripts/recipe_pictures.py` | Draws every plot of every recipe (HOME's path) and compares pictures pixel by pixel; plots identified by recipe, group, plot id | `PYTHONPATH=. ./.venv/bin/python assets/scripts/recipe_pictures.py --write DIR` then `--check DIR` | before and after a change of the recipe format |

Decisions table: D-0255 build started (done); D-0253 n/a; D-0050 no silent error: errors, rejected recipes, skipped folders, missing/new plots all listed, never dropped (script main/compare); D-0125 followed.
