# ENGINE-KEYS, steps 2 and 3: report

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`. No push, no merge, `dev` not merged into the branch.
Labels: **ran** = I ran it and saw the result; **read** = I read the code at file:line; **reasoned**.

## Commits (after step 1, `a62c9c54`)

| commit | what |
|---|---|
| `39e429fb` | STEP 2: the rewrite tool: `libs/utils/src/utils/engine_keys_migration.py` (logic), `assets/scripts/migrate_recipe_engine_keys.py` (thin command), `libs/utils/tests/test_engine_keys_migration.py`, `app/tests/test_migrate_recipe_engine_keys.py` |
| `8bbd41ca` | the flag `--orphan-fragments` |
| `8ca530fe` | the tool knows a tier file of the new shape (root `steps`) and does not report it as an unknown file |
| `c97c59ed` | STEP 3, recipes: `config/data_analysis_recipes` (91 files: changed, created, removed), including the commented tier-3 example in `templates/left_join_lesson.yaml` |
| `e2ba2c91` | STEP 3, the 34 gallery bundles |
| `e7bad0eb` | STEP 3, `app/tests/equality/recipes` (4 recipes and their fragments, 32 files) |
| `6d5aae21` | `assets/scripts/recipe_pictures.py` `plots_of()` reads `target_dataset` from the entry; the small recipes of `app/tests/test_recipe_pictures.py` are in the new shape |
| `add2620e` | `docs/appendix/data_analysis_recipe_structure.yaml`: HAND EDIT (it is a document, not a recipe) |
| `133d9a6e` | the tool names a recipe by its `id` in its messages (a bundle file is always `data_analysis_recipe.yaml`) |
| `b55fc55c` | `libs/utils/src/utils/config_loader.py`: FIX found by the picture check, see "A bug found" |

## How the tool edits files, and why

It edits the TEXT at the positions the YAML parser reports (`yaml.compose` marks), the same way as the earlier tools
(`recipe_migration.py`, `strict_form_migration.py`: read at `libs/utils/src/utils/`). The earlier tools do not use a round-trip
loader; I did the same so that every comment, blank line and `!include` line stays and a file with nothing to change is not touched.
The plan is built in memory (an overlay of texts); the caller writes (`--apply`) or only prints (`--check`). Every text change is
checked to still parse as YAML (a result that does not parse is refused as a fault of the tool). A second, independent check is the
oracle in `tmpAI/engine_keys/step2_3_tools/oracle2.py`: it edits the loaded DATA of the old recipe (git HEAD before the migration) and compares
with the loaded data of the new files: **54 recipes compared, 0 differ** (ran). The same idea is a test (`expected_new` in the test file).

Modes: `--check` (default; nothing written) and `--apply`. Exit code: check 0 nothing to change / 1 would change; apply 0; 2 when
something was refused. What it cannot place it refuses with a plain message and leaves as it was. A lone file of unknown kind is
refused ("the kind of this file cannot be known from its keys; nothing changed"); a lone tier fragment or plot file is refused
("give that recipe (or its folder)") because its includer must change with it.

Command used (from the worktree root):
`PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" <main .venv python> assets/scripts/migrate_recipe_engine_keys.py --apply --orphan-fragments config/data_analysis_recipes assets/gallery_data app/tests/equality/recipes`

## Rules as built (each is tested, each break-once shown below)

a. Tiers (D-0250). Block, flow, empty and comment-only tiers become `tier1:` / `tier2:` with `steps:`; a join's `steps` container and
   a plot entry's `steps: {tier3}` likewise. Empty tiers are KEPT, written `tier1: {steps: []}` (the checker accepts an empty tier);
   a table or join with no `tier1` gets `tier1: {steps: []}` (required) and the tool says so. Fragments: one include per tier; a
   one-tier fragment keeps its name and its root key becomes `steps`; a two-tier fragment is split into `<name>_tier1.yaml` and
   `<name>_tier2.yaml` (PROVISIONAL naming) and the old file is removed; a shared fragment is rewritten once and every includer follows;
   quotes of an include are kept.
b. Plot entry (D-0237, D-0252): no `spec:`; a plot in its own file: the whole entry moves into that file, the master keeps
   `plot: !include file`. Written order: plot_engine, ui_label, ui_title, description, comment, taxonomy, the content, tier3.
c. `label` -> `ui_label` at groups and plot entries. The pending places (info, table and join, field) are renamed only when the table
   `label_keys` of `recipe_spec.yaml` says `ui_label` for them (tested for each of the four, also for an included `input_fields` file).
d. Title (PROVISIONAL, the coordinator's reading): the old `title:` text goes into the `title` argument of the `labs` layer (added at
   the end of the layers when there is none, set when there is one) AND as `ui_title`. Read: `plot_config_resolver.py:629-634` seeds
   `labels.title` from the root title, `viz_factory.py:373-379` applies the flat labels AFTER all layers, so the root title wins today;
   a labs layer at any place gives the same final title (reasoned from that code, not yet drawn: see "what I could not prove").
   A labs title that differs from the root title is replaced and the old labs text is printed (tested; the live data has none, only the
   orphan `final_plot.yaml` has both). Refused (title left in place) when `plot_defaults` holds a `labs` layer and the plot has none (a new
   labs layer would replace it), or when the plot has no layers list.
e. The four dead `plot_defaults` keys: removed, each printed with its old value and the recipe id; the font is not turned into a theme.
   A `plot_defaults` block that holds nothing after that is removed.
f. Theme (D-0258). Rule applied: when at least one plot of the recipe has no complete theme of its own and `plot_defaults` has none,
   `theme: theme_bw` is written ONCE as the first key of `plot_defaults` (the block is created before `analysis_groups` when there is none).
   One line is both the shortest form and the same picture: a plot's own theme (L4) wins over `plot_defaults` (L2), a partial theme layer
   (`theme_custom`, `theme_legend_position`) does not count as a theme because the base still comes from the built-in
   (`plot_config_resolver.py:117-122,308-318`, read), "partial" is the answer of `viz_factory.plot_config_resolver.is_partial_theme` (the
   script imports it; the library takes it as a parameter). Per-plot writing is never needed. The built-in is NOT removed from the code.

## Summary of the run (`tmpAI/engine_keys/migration_output.txt`; `--check` before: `migration_check_before.txt`; `--check` after: `migration_check_after.txt`)

| what | count |
|---|---|
| files written (git: 150 files in the three commits) | 136 changed, 14 created, 7 removed |
| `config/data_analysis_recipes` files changed: pipelines (recipes, fragments, plot files) / templates / retest | 66 (59 changed, 7 renamed by the split) / 7 / 4; plus 7 created and 7 removed by the split |
| `assets/gallery_data` bundles | 34 |
| `app/tests/equality/recipes` | 32 files (4 recipes + their fragments and plot files) |
| events: tier (table/join containers) | 124 |
| events: tier fragments rewritten | 54 (53 + 1 orphan) |
| events: plot entries rewritten / plot files that now hold the whole entry | 51 / 35 |
| events: `label` -> `ui_label` | 64 (groups and plots) |
| events: titles moved | 25 (15 labs layer added, 10 existing labs layer extended) |
| events: dead keys removed | 7 (all `default_font_family`) |
| events: theme written | 35 (12 config recipes, 23 gallery bundles, 0 equality) |
| refused / listed and left | 4 files (below) |

Dead keys removed with old value (recipe: value): `1_test_data_ST22_dummy`: "Liberation Sans"; `2_test_data_ST22_dummy`: "Liberation Sans";
`stress_test_master`: Liberation Sans; the four equality recipes (`2_test_data_ST22_dummy_dirty`, `_dirty_no_null_text`, `_emptied`,
`_fractional_year`): "Liberation Sans". No recipe held `facet_panel_spacing`, `legend_position` or `optimisation`.

Titles moved (recipe | plot | form): `1_test_data_ST22_dummy`: amr_heatmap, assembly_quality_dotplot, miaou, mlst_bar, qc_reads_horizontal_barplot,
virulence_variants, year_distribution (labs added); phenotype_genome_length_fragmentation, qa_aggregated_no_key, qa_amr_genes_per_sample,
qa_facet_by_mapping, qa_fanout_rows_per_sample, qa_l50_integer, qa_population_zscore, qa_sequence_type_missing, qa_year_label, virulence_bar
(labs extended); `audit`: submission_status, tat_distribution; `e_coli`: growth_rate_by_st, serotype_dist; `figshare_integration`:
plot_a_phenotype_bar, plot_b_genotype_bar, plot_c_resistance_class; `simple_template`: value_by_group (labs added). Total 25: 15 added, 10 extended.

Themes written (recipe: plots drawn with the built-in theme_bw until now): `1_Abromics_general_pipeline`: abromics_st_by_country,
abromics_st_by_source; `3_test_no_joins`: sequence_type_counts; `demo_abromics`: demo_st_by_source; `figshare_integration`: plot_a_phenotype_bar,
plot_b_genotype_bar, plot_c_resistance_class; `stress_test_master`: stress_species_amr; `retest_bad_select_column`: genes_bar; `retest_broken_header`:
genes_bar; `retest_tier2`: value_by_group, samples_per_year; `retest_top_n_other`: variants_bar; `complex_template`: gene_presence_by_country;
`left_join_lesson`: samples_by_country; `simple_template`: value_by_group. Gallery bundles (23 of 34): bar_grouped, bar_simple, beeswarm_sina,
boxplot_faceted, boxplot_simple, connected_scatter, density_2d_bin, density_simple, dumbbell, ecdf, error_bar, freqpoly, histogram_simple,
point_faceted, point_simple, qq_plot, scatter_smooth, stacked_area, step_chart, tile_simple, violin_boxplot, violin_faceted, violin_simple (the other
11 bundles name a theme already). The recipes that already name a theme in `plot_defaults` or in every plot (`1_test_data_ST22_dummy`: theme_minimal in
`plot_defaults`; `2_test_data_ST22_dummy`: every plot has a theme; `e_coli`, `audit`: theme_minimal) got none.

Files created (14): the split of 7 two-tier fragments in `pipelines/1_test_data_ST22_dummy/wrangling/`: `ST22_Anchor_wrangling`, `MLST_Metadata_wrangling`,
`ResFinder_wrangling`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_aggregated_no_key`, `QA_population_zscore`, each into `_tier1.yaml` and `_tier2.yaml`;
the 7 old files are removed. Provisional naming. (In git `ResFinder_wrangling_tier1` and some others show as renames.)

Listed and left (4, the run exits 2 because of them; none is a recipe):
- `config/data_analysis_recipes/experimental/test_logic.yaml`: an EMPTY file (kind unknown).
- `pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml`: a bare list of old format-0 steps (`action: "join"`, a removed action); no recipe includes it.
- `pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml` and `pipelines/stress_test_master/plots/final_plot.yaml`: plot CONTENT files that no recipe includes. They have no entry name (`ui_label`), so the tool cannot write the entry without inventing a name. Both carry an old root `title:`; `FastP_reads_boxplot` also has the stray taxonomy keys; `final_plot` has a root title AND a different labs title (the root text is what was drawn: "Master Proof: 10,000 Rows Distribution" vs the labs text "STRESS TEST: Species x AMR Distribution").
The test `app/tests/test_resfinder_abromics_fragment.py` lists exactly these (and `PlasmidFinder_wrangling.yaml`, which is included) as "found 2026-11-15, not decided". One orphan WAS rewritten, with `--orphan-fragments`: `ResFinder_Abromics_wrangling.yaml` (Eve 2026-11-15: convert, do not delete): its root key is `steps` now.

## The checker over everything (ran)

`tmpAI/engine_keys/step2_3_tools/check_all.py`: `check_recipe_file` with the app catalogs (`checker_catalogs()`): **20 recipes (16 under config, 4 equality) and 34 bundles (profile gallery): no problem at all**. The second run of the tool (`--check`): "nothing to change". A tier-3 example is written as a COMMENT in `left_join_lesson.yaml` (D-0237 item 6), because the checker refuses a real tier3 today (P05, the engine does not read it yet).

## Tests

- `libs/utils/tests/test_engine_keys_migration.py`: 68 tests, `app/tests/test_migrate_recipe_engine_keys.py`: 9 tests: all pass (ran). Each rule a to g, the second run, byte-identical files, comments kept, shared fragment, two-tier fragment, one-tier fragment, quoted include, only-tier2 fragment, join fragment, the title cases (no labs, labs without title, labs in flow style, other labs title, quoted title, title in a plot file, labs in `plot_defaults`, no layers), the dead keys with old values, the theme cases (none, in defaults, in one plot, partial theme, complete theme layer, comment above `analysis_groups`, other keys in defaults), the pending label places by the table, lone files of unknown/known kind, orphans (default and flag), `--check` writes nothing, exit codes, the real plot library's answer for a partial theme, and the independent data-level expectation on a recipe with every rule.
- `libs/utils/tests` all: 2064 passed (ran, after the `config_loader` fix and its test).
- Break-once (ran, `tmpAI/engine_keys/step2_3_tools/breakonce2.py`): 23 breakages of the code, each made one at a time and restored; each made at least one named test fail: tail dropped from a tier; tier1 not added; split overwrites a file; shared fragment rewritten again; entry key order reversed; plot file content not written; group label not renamed; pending info label always renamed; title pair kept; labs title kept when present; ui_title not written; dead keys not removed; old value not printed; partial theme counted as complete; theme written although `plot_defaults` has one; untouched files reported as changed; lone unknown file silently skipped; include quotes dropped; shared plot file guard off; orphans not listed; orphan flag ignored; script `--check` writes; script exit code of check always 0. Also for `config_loader`: the `steps` key put back made `test_a_tier_file_that_holds_only_steps_is_not_unnested_into_a_bare_list` fail.

## A bug found while running the picture check (fixed, `b55fc55c`)

`libs/utils/src/utils/config_loader.py:120` (read) had `redundant_keys = {"input_fields", "output_fields", "source", "steps"}`: an included file that holds only one of these keys is unwrapped. A new tier file (`tier1: !include f.yaml`, file `steps: [...]`) lost its `steps` key and became a bare list, and the assembler said "No step list and no ingredients" (ran: it was the error of 34 plots). Step 1 had removed `wrangling` and `spec` from that set and missed `steps`. Fixed in `libs/utils` (in my allowed area), with the test above.

## What I could and could not prove

Proved (ran):
- Every shipped recipe, the four equality recipes and the 34 bundles pass the checker, with the app catalogs.
- The text rewrite equals an independent data-level expectation on all 54 recipes (oracle).
- The tool is idempotent on the real tree (second `--check`: nothing to change) and on fixtures; untouched files are byte-identical.
- The load path works as far as `ConfigManager` and the load gate: `test_recipe_pictures` reaches the draw step, and the picture check starts.

NOT proved: that the pictures are identical. The picture check (the command of step 1, `--allow-outside-checkout`, because of the finding below) gave
`error-changed: 45, identical: 5, missing: 1, new: 1`, output in `tmpAI/engine_keys/picture_check_step3_output.txt` and `picture_check_step3/`. All 45 errors are readers of the old shape, none is a picture difference:
- 34 plots: `no table for collection ...: TransformationError: No step list and no ingredients — cannot assemble`: `app/modules/orchestrator.py:296` reads `collection_spec.get("steps", [])` (a join's old container) and `:138` reads `ds_schema.get("wrangling")`; the error is raised at `orchestrator.py:290`.
- 11 plots: `VisualizationError: ... 'ui_label' is not a key of a plot spec` (and `description`...): `libs/viz_factory/src/viz_factory/viz_factory.py:210-224`. `viz_factory.py:210` reads `data_analysis_recipe.get('plots')`, which `ConfigManager` builds from the entries; the entry now holds `ui_label`, `ui_title`, `description`, `taxonomy` that the factory refuses (`unknown_spec_keys`, `viz_factory.py:219-224`). The entry's app-side keys must not reach the factory.
- the title/labs equivalence and the theme equivalence are therefore still only read from the code, not drawn.

### FINDING, science (D-0050): the load gate checks LESS until step 4

The picture check shows `retest_bad_select_column` as "new: drawn now; the stored set had the whole recipe as rejected". The baseline rejected it because the data check ran the tier-1 steps of the schema and found the missing column "phenotype". Now `validate_data_analysis_recipe` and `validate_data_analysis_recipe_data` both return NO problem (ran, `tmpAI` scratch), because the data check still looks for `wrangling` (`app/modules/data_analysis_recipe_validator.py:85-103`, `_step_blocks`) and the ingestion reads `wrangling`: the steps are not found, so nothing is checked and nothing is said. A recipe broken on purpose passes. The branch must not be merged before step 4 puts the readers right; a test that fails if a gate reads zero step blocks of a recipe that has steps would stop this silent skip (suggestion, not built).
`retest_broken_header` is still rejected (the header check does not depend on the tiers).

### FINDING: viz_gallery comes from the MAIN folder in this checkout

`libs/viz_gallery/src/viz_gallery/__init__.py` exists on `dev` (commit `ca1a2246`, D-0234, merged after this branch started) and not on this branch. In this checkout `viz_gallery` is a namespace package and the editable install of the main folder (`.venv/.../__editable__.viz_gallery-0.1.0.pth`) wins: the libraries tests of `libs/viz_gallery` (and `gallery_manager.py:201`, `taxonomy.py`) run the MAIN folder's code, and `recipe_pictures.py` (part A) STOPS with its plain message. I did not merge `dev` (instruction). Needs a decision: merge dev into the branch, or cherry-pick that one commit, before step 4.

## What is red now, and why (ran; lists in `tmpAI/engine_keys/red_after_step3_app.txt`)

`app/tests` without the browser files (`test_shiny_*`, `test_export_download`, `test_every_app_features_starts`): **451 failed, 67 errors, 2748 passed** (12 min 40 s).
`libs/viz_gallery` + `libs/blueprint_arch` tests: 24 failed, 441 passed. Other libraries (ran): `libs/utils` 2064 passed; `libs/transformer` 1 failed, 2246 passed (`test_debug_assembler.py::test_a_shipped_pipeline_recipe_is_assembled_for_every_join`: the runner `libs/transformer/tests/debug_assembler.py` reads the join's old `steps`; the assembler says "No step list"); `libs/viz_factory` 2252 passed, 27 xfailed; `libs/connector` 27, `libs/ingestion` 59, `libs/id_reconciliation` 81 (+3 xfailed), `libs/test_lab` 103: all passed.
Why: readers and writers of the old shape (below), and tests whose own fixtures index the old shape. The browser tests were not run (each failure takes about a minute; they need the readers first).

## STARTING POINTS FOR STEP 4 (from the failing tests and from the code, file:line, ran/read)

Readers of the recipe tree that still read the old shape (these decide the red tests):
- `app/modules/orchestrator.py:138` (`ds_schema.get("wrangling", [])` -> `tier1` of a table); `:290-297` (`collection_spec.get("steps", [])` -> `tier1`/`tier2` of a join). 34 plots of the picture check and the `app/tests/equality/*` fail here (`app/tests/equality/checks.py:81-106`, 47 tests).
- `libs/transformer/src/transformer/data_assembler.py:211` (11 tests) and `data_wrangler.py:66`/`:37` (`_resolve_tier` gets "the raw value under the 'wrangling' YAML key").
- `libs/viz_factory/src/viz_factory/viz_factory.py:210-224` (plot spec from `plots`, unknown keys refused) and the engine of the plot (`:114-127` reads only the top-level `plot_engine`).
- `app/modules/data_analysis_recipe_validator.py:85-103` (`_step_blocks`, the silent skip above) and `app/modules/gallery_examples.py:92` (`entry["spec"]["target_dataset"]`; 38 tests: `test_gallery_app_path`, `test_convert_gallery_examples`...).
- `app/src/server.py:78`, `app/handlers/home_theater.py:106,246,253,429,555`, `app/handlers/audit_stack.py:289`, `app/handlers/export_handlers.py:948`, `app/modules/plot_seeds.py:167`, `app/modules/wrangle_studio.py:572,685`, `app/modules/session_manager.py:135`, `assets/scripts/golden_baseline.py:57,68`: they read `["spec"]` or `["steps"]`.
- `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py:135-141,185,271-335,456-458,485,692-701,738-797,1057` (`wrangling`, `steps`, `spec`), `blueprint_mapper.py:121-411` (`wrangling` or `steps`), `t3_translator.py:183`, `group_plot_manager.py:151-156` (writes `spec` and `label`), `agent_tools.py:330`; `app/handlers/blueprint_handlers.py:489-610,640,824,905-913` (and the form writers).
- `libs/viz_gallery/src/viz_gallery/example_recipe.py:119-132,177-204` (WRITES `wrangling`, `spec`, `steps`), `taxonomy.py:64`; `libs/test_lab/src/test_lab/bootstrapper.py:162,187`, `scaffolder.py:203,226` (WRITE `wrangling`).
- `assets/scripts/retest_walkthrough.py:53` (a text replace on a retest recipe: "the retest recipe was reworded ... found 0 times": the migrated retest text changed), `app/src/bootloader.py:565` (4 tests: no usable recipe in a test deployment folder: their small recipes are old shape).
- the three older tools `libs/utils/src/utils/recipe_migration.py`, `strict_form_migration.py`, `contract_migration.py` still write the old format-1 shape (step 1 report, needs a decision 4).

Tests whose own fixtures read or write the old shape (fix them with the readers; counts are failing tests): `app/tests/test_checker_names_the_new_action.py:26` (64), `test_every_self_join_gets_a_message.py:73` (39), `test_categorical_migration.py` (37), `test_step_order.py:128,201,241,295` (34), `test_checker_reads_every_formula_place.py:100` (13), `test_blueprint_failed_load.py:147` (13), `test_gate_gap.py:47` (8), `test_plot_text_gate.py:18` (7), `test_data_analysis_recipe_validator.py:198`, `test_suggestion_label.py:62`, `test_amr_multiresistance_formula.py:26` (reads `["tier1"]` of a fragment that is `steps` now), `test_resfinder_abromics_fragment.py` (reads `["tier1"]` of `ResFinder_Abromics_wrangling.yaml`, and its helper writes old shape), `test_writers_emit_format_one.py` (15: the writers), `test_na_choice.py:265`, `test_view_badge.py:42`; `libs/blueprint_arch/tests` (14), `libs/viz_gallery/tests` (10). `test_left_join_lesson.py` (4), `test_retest_data_analysis_recipes.py` (6), `test_complex_template_runs.py` (2), `test_golden_baseline.py` (2) fail because of the readers above.

Not recipes, not touched (reader checked): `libs/transformer/tests/data/*_data_analysis_recipe.yaml` (70 files): single-table fixtures with `wrangling:` at the root, read by `yaml.safe_load` in `libs/transformer/tests/test_action_recipe_pairs.py:65` (no recipe loader, no checker); `libs/viz_factory/tests/test_data/*_test.yaml` (about 165): old plot-spec test data of `viz_factory_integrity_suite.py:84` (a CLI report, an even older shape: `plots:` and `data_path`); `libs/viz_gallery/tests/data/data_analysis_recipe.yaml`: a stub with `wrangling.tier3` for a viz_gallery test; `.claude/design/outdated/recipe_format_st22_draft.yaml`: an outdated design file. Whether they change is for the worker that changes their readers.

## Needs a decision (D-0165)

1. The four listed files (above): delete, keep as they are, or give the two plot files an entry (who writes their `ui_label`)? The test already lists them as "not decided".
2. Merge `dev` (or cherry-pick `ca1a2246`) into the branch before step 4 (viz_gallery comes from the main folder; the picture tool stops).
3. The pending `label` places (info; table and join; field): still `label`. One line each in `label_keys` of `recipe_spec.yaml`, then re-run the tool (it renames only where the table says `ui_label`; tested).
4. Names of the split fragments (`<name>_tier1.yaml`, `<name>_tier2.yaml`): PROVISIONAL.
5. The key order is not enforced by the checker (step 1 decision 1); the tool writes the decided order.
6. `plot_defaults` theme: `theme_bw` was written as the first key of `plot_defaults`, in 35 recipes and bundles (list above). A recipe that has one plot with a theme and others without has the default and the plot's own theme; correct, but she may prefer to see it per plot.
7. Whether a gate that reads zero step blocks of a recipe that has steps must raise (see the finding).

## PROVISIONAL choices (mine or the coordinator's, not Eve's words)

- The title rule (labs and `ui_title`), the split naming, the `--orphan-fragments` flag and its default (listed, not rewritten), empty tiers kept as `steps: []`, `tier1: {steps: []}` added where required, the single-line theme rule, the events and exit codes of the tool, the class names (`classify`: recipe, tier_fragment, tier, plot_content, input_fields, unknown), the hand edit of the appendix.

## Decisions table

| decision | how the code complies | where | test |
|---|---|---|---|
| D-0250 tier is its own key, optional `data_engine`, `steps` | tiers rewritten at table, join and entry; includes per tier | `engine_keys_migration.py` `convert_container`, `tier_fragment` | `test_a_table_wrangling_with_two_tiers...`, fragment tests |
| D-0251 gallery bundles in the same pass | 34 bundles migrated by the same tool | commit `e2ba2c91` | `check_all.py` (34 pass) |
| D-0252 the plot file holds the whole entry | `p: !include f`, the file holds the entry | `assemble_entry`, `entry` | `test_a_plot_whose_spec_is_in_its_own_file...` |
| D-0253 `ui_label`, `ui_title`, no `title:`, figure text only in `labs` | label rename, title moved to labs and ui_title | `names`, `move_title` | title tests (8), label tests (4) |
| D-0237 no `spec:`, content in the entry, key order | restructure with the decided order | `assemble_entry` | `test_an_inline_spec_is_removed...` |
| D-0241, D-0242 dead keys removed, values printed, no font theme | `plot_defaults` | `plot_defaults` | `test_the_four_dead_keys...` |
| D-0258 `theme_bw` written where none is named, files listed | one line in `plot_defaults`, the list printed | `plot_defaults`, `_complete_theme` | theme tests (7) |
| D-0255 one change, every recipe and bundle, nothing special-cased | 16 + 4 + 34 recipes, no file treated specially; 4 non-recipe files listed | commits above | `check_all.py` |
| D-0050 no silent error | refusals with plain messages; a result that does not parse is refused; orphans listed; the finding on the gate | tool and report | refusal tests |
| D-0165 | "Needs a decision" | | |

Consequence the brief asked about ("what happens to X after this change?"): a recipe given to the tool that it cannot place in one spot is left as it was in that spot and the run exits 2; a recipe the tool fully rewrites passes the checker, but the APP cannot run it yet (readers above) and the load gate checks less (finding): do not merge before step 4.

## Not done

- No reader or writer outside `libs/utils` and the two tools, except the one line of `recipe_pictures.py` and the `config_loader.py` fix (inside `libs/utils`). The built-in `theme_bw` is still in the code (`plot_config_resolver.py:47,63`).
- No `@deps` of other files, no dependency index, no UML, no docs other than the appendix YAML (step 8).
- The browser tests were not run.
