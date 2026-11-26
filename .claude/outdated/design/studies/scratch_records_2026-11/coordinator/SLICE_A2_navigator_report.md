# Piece A2: Blueprint's navigator, the tube map and the app's recipe check on the recipe graph (builder report, digest by the coordinator, 2026-11-19)

Branch `task/navigator-on-graph` (worktree `.claude/worktrees/navigator-on-graph`), base `20e67837`, commits `41dc085b` (validator runs J08 from the graph), `fb37c514` (navigator and tube map on the graph), `20ad0582` (deps block).
Files: `app/modules/data_analysis_recipe_validator.py`, `app/tests/test_validator_runs_column_checks.py` (new), `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py`, `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py`, `libs/blueprint_arch/tests/test_navigator_on_graph.py` (new).

## Result
- Outputs byte-identical before and after on all 54 recipes that have `analysis_groups`: the five navigator functions, `resolve_fields_for_schema`, the tube map (cytoscape per active node, mermaid). 2.7 MB of JSON. Scratch in the worktree: `tmpAI/char_dump.py`, `tmpAI/baseline.json`.
- On the graph now: `build_sibling_map`, `build_schema_registry`, `build_plot_lineage`, `BlueprintMapper` (edges). Not changed: `get_plot_ids_in_group` (the graph has no groups), `build_lineage_chain` (works on the map; its input now comes from the graph).
- J08 (a non-key column in both ingredients of a join): checker with and without the graph over 54 recipes x profiles (142 checks): identical findings, no recipe newly refused. So it is WIRED in the app's check. `"columns"` added to `REQUIRED_COVERAGE`.
- Tests (RAN): `libs/blueprint_arch/tests` 616 passed; with `libs/utils/tests` 2984 passed; new validator test 8 passed; six validator/load-gate files 144 passed; 6 mutations of the navigator each caught; Blueprint browser files under qa 41 passed. Headless whole: 11726 passed, 2 failed + 9 errors, all in browser files not on the ignore list (two passed alone; the 9 are the tier test that was repaired on dev after this branch was cut).

## What changed for a BROKEN recipe in Blueprint (the builder's choice; PROVISIONAL)
New at the navigator's edge: `recipe_structure(raw)` returns `RecipeStructure(graph, left_out)`: when the graph refuses a recipe, the elements it names are taken out of a copy and the graph is built again; each place left out is listed with the graph's reason. Nothing in the app shows `left_out` yet. Seen differences from before, only on broken recipes: an unknown ingredient is no longer listed nor drawn as a dangling edge; a plot naming an unknown table gets the warning node (before: a dangling edge); the legacy plot key `join_id` is no longer read as a table; a repeated or string ingredient is dropped; a cycle of joins is drawn without ingredients; a file the loader cannot read gives no ingredients and no plot targets (before it navigated fully; Validate reports it).

## Cost: time per call (a regression to repair before the slice is called done)
The navigator now reads all fragments through the strict loader: about 0.35 s per call on the demo recipe (the graph itself 0.001 s). In the EXPORT that is about 0.4 s per plot: about 8 s more for 18 plots (reasoned from the per-call time). In Blueprint about 0.7 s per refresh. Options: the callers build the structure once and pass it in (handler change), or a cache keyed by the files read.

## Facts for the audit redesign
`session_manager.extract_primary_keys` and the graph's `key_families` do NOT agree: 15 of 54 recipes differ. `extract` = every column used as a key by any join step; `key_families` = only columns declared `is_entity_key`, linked by joins. Recipes with no declared entity key give no family; recipes that also join on `Gene_name` / `VF_gene` list those only in `extract`; recipes with a declared key and no join appear only in the graph.

## Open choices reported
1. What Blueprint shows for a recipe the graph cannot draw: as built / refuse the whole map with the plain error / a partial mode in the graph.
2. `build_lineage_chain` not on the graph (its signature takes the map).
3. A groups query on the graph (`group_of`).
4. `includes_map` argument of `build_schema_registry` is dead, kept for the callers.
5. The time per call (above).
Other callers of the checker still pass no graph: `libs/viz_gallery/src/viz_gallery/gallery_manager.py:85`, `:196`; `assets/scripts/convert_gallery_examples.py:156`; `assets/scripts/create_data_analysis_recipe.py:212`.
