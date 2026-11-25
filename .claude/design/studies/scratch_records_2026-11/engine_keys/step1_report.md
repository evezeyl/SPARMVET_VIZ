# ENGINE-KEYS, part A and step 1: report

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`. No push, no merge.

## Commits

| commit | what |
|---|---|
| `21a2a95c` | part A: `assets/scripts/recipe_pictures.py` (+ its test file) |
| `c8889c2c` | step 1 rules: `recipe_spec.yaml`, `recipe_check.py`, `recipe_loader.py` (docstring only), `config_loader.py`, `recipe_tiers.py`, `recipe_factory.py` |
| `a62c9c54` | step 1 tests: new `test_recipe_engine_keys.py` and the adapted tests of `libs/utils/tests` |

## PART A: the picture check now draws with this checkout's libraries

Verified first (ran, `__file__` of each package from the script's process): with `PYTHONPATH=.` only `app` came from the worktree; `utils, transformer, viz_factory, viz_gallery, blueprint_arch, ingestion, connector, id_reconciliation, test_lab` all came from the MAIN folder (`/.../SPARMVET_VIZ/libs/*/src`). With the checkout's `libs/*/src` first on `PYTHONPATH` all came from the worktree (viz_gallery is a namespace package: its search path lists both, the first one decides). The step 0 claim is right.

What the script does now:
- before it draws it asks, without importing (`find_spec`), where `app` and every package of `libs/*/src` of its own checkout would be imported from; it prints the folder of each, and writes them to the manifest under `libraries`;
- if one comes from outside the checkout the script lives in, it stops (exit code 2) with a plain message naming the packages and the remedy, unless `--allow-outside-checkout` is given (then it prints a WARNING and the manifest records it) (D-0050);
- `--help` documents the exact command (below). No change to `pyproject.toml` or the pytest configuration: pytest already uses the `pythonpath` setting, the script uses the same idea through the command.

### THE COMMAND (every later step uses it; run it from the worktree root)

```
PYTHONHASHSEED=0 PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)" \
  /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.venv/bin/python \
  assets/scripts/recipe_pictures.py --check \
  /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/engine_keys/picture_baseline_15394ef5 \
  --out <where the check output goes>
```

Result with this command, run twice at the part A commit (libraries still unchanged): `identical: 51`, `PICTURES IDENTICAL`, both times (output in `tmpAI/engine_keys/picture_check_step1_partA/`, 43 s). With the plain `PYTHONPATH=.` command the tool now stops with the STOPPED message (checked).

### FINDING (science, reported at once): one plot is not reproducible across runs

Why `PYTHONHASHSEED=0` is in the command: the first run with the corrected command gave `different: 1` for `complex_template::Overview::gene_presence_by_country` (26288 pixels). Same command again: identical. So I tested seeds 0 to 5: seed 4 differs, 0, 1, 2, 3, 5 give the same picture as the baseline. The picture differs in where the stack of the missing-value group (`nan`) sits in the bar (bottom or top, Denmark). Evidence (ran, `tmpAI/` scratch): the table of that plot (T2 `master_assembly`, 74 rows) has the same hash under seed 0 and 4, and the pandas frame given to the plot has the same dtypes. So the difference is in the drawing step (plotnine or pandas, with a missing-value group in a fill), not in the recipe path and not in this tool. This is a case of "the same data and recipe give the same result" not holding for the picture. Not fixed, not in my task. Until it is decided what to do, the documented command fixes the seed so that a check is repeatable; the tool prints the seed it ran with, writes it to the manifest (`python_hash_seed`), and a check made with another seed says so. The step 0 baseline manifest has no seed record (it was written before); it matches seed 0 (and 1, 2, 3, 5).

Tests (part A): `app/tests/test_recipe_pictures.py` 19 tests (was 10), they passed at the commit. Break-once: `outside_checkout` forced to return nothing: 4 tests failed; restored. (They are red now for another reason, see "red outside libs/utils".)

## STEP 1: the format rules

### The new shape (one example for each place)

```yaml
data_engine: python-polars            # defaults for the whole recipe (unchanged)
plot_engine: python-plotnine
data_schemas:                         # a table; metadata_schema and additional_datasets_schemas the same
  T:
    label: T                          # PENDING Eve (M271): stays `label` for now
    source: {type: local_tsv, path: data/T.tsv}
    null_values: []
    strip: true
    input_fields: {...}
    tier1:                            # a tier is its own key (no `wrangling:`); required in a table and in a join
      data_engine: python-polars      # optional, FIRST key
      steps: []                       # the list; inline here
    tier2:                            # optional; or `tier2: !include T_tier2.yaml` (the file root holds data_engine/steps)
      steps: [...]
joins:
  J:
    label: J
    ingredients: [{dataset_id: T}, {dataset_id: U}]
    tier1:                            # no `steps:` container
      steps: [{action: polars_join, ...}]
analysis_groups:
  g:
    ui_label: G                       # required (was label)
    ui_title: A longer name           # optional, used by the report
    plots:
      p:                              # a plot entry, inline: no `spec:`
        plot_engine: python-plotnine  # optional, FIRST key
        ui_label: P                   # required
        ui_title: Longer name         # optional
        description: ...
        comment: ...
        taxonomy: {...}
        target_dataset: J             # the plot content, written in the entry (title: is refused)
        mapping: {x: a}
        layers: [{name: geom_bar}, {name: labs, params: {title: ...}}]
        theme: theme_bw
        tier3:                        # optional, at the entry
          data_engine: python-polars
          steps: []
      q: !include plots/q.yaml        # the WHOLE entry is in its own file; the include sits at the entry
```
`plots/q.yaml` holds the entry's own content: `ui_label: Q`, `target_dataset: J`, `mapping: ...`, `layers: ...` (optional `plot_engine` first). A file whose root is the key it is included under (`q:` or `tier1:`) is a wrapper: F01.

### Checker codes (message text is exact, from a run)

OLD SHAPES, refused with the key (the `path`), the new form and the tool; `Problem.text("my.yaml")` prefixes the file name:

- `S06 data_schemas.A.wrangling`: "wrangling is not a key of this element any more (the form of the recipe changed). Fix: write tier1 (and tier2) directly in the table, each as a mapping with steps: [...] (and an optional data_engine); there is no wrangling key now. Rewrite tool: assets/scripts/migrate_recipe_engine_keys.py (it rewrites a recipe file and says what it changed)"
- `J07 joins.AB.steps`: the same with "in the join" and "there is no steps container now".
- `P04 analysis_groups.g.plots.p.steps`: "... write tier3 directly in the plot entry as a mapping with steps: [...]; there is no steps container now. Rewrite tool: ..."
- `P01 ...plots.p.spec`: "spec is not a key of this element any more ... write the content of the plot (target_dataset, mapping, layers, theme, palette, ...) directly in the plot entry; there is no spec key now. Rewrite tool: ..."
- `P01 ...plots.p.title`: "title is not a key of this element any more ... Fix: removed from the plot (D-0253): write the figure title in a labs layer (its title argument) and the name used by the report in ui_title. Rewrite tool: ..."
- `S06/J07/P04 <path>.tier1` written as a list or empty: "tier1 is written as a mapping with steps, not as a list (the form of the recipe changed). Fix: write tier1: {steps: [...]}. Rewrite tool: ..."
- `G01 ...g.label`, `P01 ...p.label`: "label is not a key of this element. Fix: renamed ui_label (the short name of the tab and of the lists); write ui_title for a longer name used by the report". When only the old `label` is there the "ui_label is missing" message is not added (told once).
- When an old container (`wrangling`, `steps`) or `spec` is present, "tier1 is required" and the plot-content errors are not added (told once).

NEW TIER RULES (codes S06 table, J07 join, P04 plot entry): tier is a mapping; keys `data_engine`, `steps` only; `steps` required and a list ("tier1 has no steps. Fix: write tier1: {steps: []} ..."); `tier1` required in a table and a join; a tier key inside a tier (an old two-tier fragment included under one tier) is refused with the tool named; a step in any tier is judged like before, with the path `data_schemas.A.tier2.steps[1].na`.

ENGINES:
- `T06` at every level (top, `tier*.data_engine`, `plot_engine` of an entry, `tier3.data_engine`): "'python-pandas' is not a built data_engine: no library for this engine in this app (the engines of this app: python-polars). Fix: write one of python-polars" (D-0239 words; the top-level message got them too).
- `EN02` (new): "the step 'polars_filter_demo' belongs to the engine python-other, but this block is written for the engine python-polars. Fix: move it to a block of the engine python-other, or write the engine of this block as python-other". Same for a layer ("the layer ..."). The engine of a block: the tier's own `data_engine`, else the recipe's; for a layer, the entry's `plot_engine` else the recipe's.
- `EN03` (new): "the registry gives no engine for the step '...', so the check cannot tell which engine runs it. This is a fault of the app, not of the recipe." (a registered name that the engine table lacks).
- Catalogue keys the checker reads (PROVISIONAL names, step 5 may rename): `action_engines`, `component_engines` (name -> engine). With both, `coverage` has `engines`; without them `coverage` lacks `engines` and nothing about engines is judged. Nothing is imported from another library. The app's load gate still has to put `engines` into its required coverage and fill the two maps from the registry field `engine`: step 5.

TOMBSTONES `PD02`, one per dead key (`default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`), form of `rules_legacy_management.md` 2c: "default_font_family was removed from plot_defaults (REMOVED, D-0242, 2026-11-17): the key did nothing, and a key that does nothing is removed from the recipe (D-0220). The font, like the text size, is set through a theme layer. Fix: Remove the key. Rewrite tool: assets/scripts/migrate_recipe_engine_keys.py removes it and prints its old value. Tombstone expires: two phases after this change is merged (delete the text then; the removal task is made with the merge)". The text lives in `recipe_spec.yaml` under `removed:` (the rewrite tool can read the same table). The live keys `palette, theme, layers, random_state` are still accepted (the `plot_defaults.layers` check that was merged earlier is kept).

Retired code: `PS01` (unknown key of a spec). An unknown key of the plot entry is `P01` now (with the renamed hints that were `spec.*`). The catalogue in the spec file (section 11) lists PS01: step 8.

Changed texts: `P05` says "tier3" (no longer "steps.tier3"); `J14`, `S07`, `J08`, `ST*` paths follow the new place.

### Rule F01 (`recipe_loader.py`)
No code change was needed: the existing rule (an included file whose root is the one key it is included under) already finds `tier1: !include f` with a file that starts with `tier1:`, and `p: !include plots/p.yaml` with a file that starts with `p:`. Tested for both, plus an inline tier, an included tier, an included whole plot entry. A file with two tier keys included under one tier (the old 54-file fragment shape) is found by the checker (tier key inside a tier, with the tool named). Only the docstring of the loader says how F01 covers the new forms.

### The pending `label` places (one table)
`recipe_spec.yaml` has a top table `label_keys: {info: label, schema: label, join: label, field: label}` (PENDING, channel M271) and the checker reads the key of each of these four places from it (I01, S03, J02 and the field property). Her answer is one line per place. Tested: with the table changed to `ui_label` the same recipe written with `ui_label` is accepted and `label` is the unknown key. The three places she asked about are `info`, table+join (`schema`, `join`) and the `input_fields` entries (`field`).

### Other changes in `libs/utils` that the brief did not list, and why
- `recipe_tiers.py` (reads the tier 2 of a table or a join): the checker asks it which tier 2 runs nowhere (S07, J14); with the old reading S07 and J14 would have been silently off. It now reads `tier2.steps` and the plot entry's `target_dataset`. Its consumers outside `libs/utils` (`cache_keys`, `orchestrator`, the navigator) now see the new shape too.
- `recipe_factory.py` (the writer of minimal recipes used by tests): its output must pass the new checker. It writes `tier1: {steps: ...}`, the plot content in the entry, `ui_label`; the parameter name `label` of `minimal_plot` is kept (written as `ui_label`).
- `config_loader.py`: the two un-nest sites of `spec` are removed (the entry is the plot config; no shim: a `spec` key is not unnested), `wrangling` and `spec` are removed from the wrapper keys the tolerant loader unwraps.

## Tests

- `libs/utils/tests`: **1995 passed** (before: 1919). New file `test_recipe_engine_keys.py`: 63 tests: accepted case and refused case for each rule; 7 old shapes (key, path, tool in the message, file name through `text()`); a whole old recipe; 7 wrong tier mappings; engine values at 8 places (refused and accepted); the engine of step and layer, coverage with and without engine information, EN02, EN03, tier3, one tier's engine not reaching the next; title refused; `label` refused as renamed at group and plot; `ui_label` required; the pending table and its one-line change; 4 tombstones and the live keys; gallery profile (GP01, GP02, GP03, old shape refused); include forms (inline tier, included tier, included whole plot entry, wrapper F01 for a tier and for an entry, old two-tier fragment, old `wrangling:` and `spec:` includes); an empty tier and empty steps; two tiers kept separate.
- Adapted (not deleted, not skipped), they pinned the old shape: `test_recipe_check.py` (the model recipe `valid()` and the catalogue cases: S06, S07, ST05, J05, J07, J14, G01, P01, P04, P05, PD01 and new PD02, PS01 cases now P01), `test_recipe_check_{entity_key_type,filter_values,join_keys,join_tier1_only,order_advice,sum_advice,ties_advice,time_joins}.py`, `test_advice_texts.py`, `test_self_join_rule.py`, `test_with_fix_one_period.py`, `test_recipe_factory.py`, `test_recipe_tiers.py`, `test_recipe_loader.py`, `test_config_loader.py` (+1 new test), `test_include_confinement.py`.
- Not touched and still green: `test_recipe_migration.py`, `test_strict_form_migration.py`, `test_contract_migration.py` (they test the text edits of the old tools, see "needs a decision").

### Break-once (13 breakages, each fails a test; every file restored; script `tmpAI/breakonce.py` in the worktree)
old-shape refusal off; `steps` no longer required in a tier; tier `data_engine` not checked; plot `plot_engine` not checked; EN02 off; EN03 off; `title` no longer an old shape; old `label` no longer told as renamed; PD02 tombstones off; the schema label read from a fixed word instead of the table; `recipe_tiers` no longer reads a schema's tier2; `recipe_tiers` no longer reads the plot target from the entry; `config_loader` unnests `spec` again. Each of them gave at least one failed test (named in the run: e.g. `test_each_row_of_the_catalogue...[S06-44]`, `test_an_unknown_engine_value_is_refused_at_each_level[...]`, `test_a_title_in_the_plot_is_refused...`).

## Red outside `libs/utils` after this step (listed, not fixed, no xfail)

Run per folder in parallel (the whole run did not finish inside 10 minutes, so I ran it in pieces; labels: ran). Reason for all of them: the recipes, templates, gallery bundles and the test recipes are still in the OLD shape and the checker refuses them (S06/J07/P01...), or the code reads `wrangling`, `steps` or `spec`: they turn green when steps 3 and 4 have run.

- `libs/transformer`, `libs/viz_factory`, `libs/connector`, `libs/ingestion`, `libs/id_reconciliation`, `libs/test_lab`: all green (2247, 2252+27 xfailed, 27, 59, 81, 103 passed).
- `libs/blueprint_arch/tests`: 14 failed (test_agent_tools 1, test_branch_plan 8, test_lineage_nav 2, test_t3_translator 3: the branch and the fork write the old shape, the checker refuses it; `test_t3_translator.py:305` reads `spec()["elements"]["join"]`).
- `libs/viz_gallery/tests`: 42 failed (test_gallery_bundle 6, test_gallery_examples_are_recipes 36: the 34 bundles are old shape; the reader reads `spec`).
- `app/tests` (browser tests of the 4 files named in the baseline command not run, as in it): test_checker_names_the_new_action (64), test_every_self_join_gets_a_message (37), test_gallery_app_path (35), test_categorical_migration (35), test_step_order (27), test_data_analysis_recipe_validator (27), test_render_every_plot (23), test_advice_one_sentence (18), test_shipped_recipes_pass_the_checker (16), test_writers_emit_format_one (15), test_blueprint_failed_load (13), test_convert_gallery_examples (12), test_demo_join_keeps_every_sample (11), test_schema_tier2 (10), test_retest_data_analysis_recipes (9), **test_recipe_pictures (8)**, test_gate_gap (8), test_checker_reads_every_formula_place (8), test_bootloader_launch (8), test_plot_text_gate (7), test_na_choice (7), test_qa_canaries (6), test_gallery_full_check (6), test_stale_key_store (5), test_data_analysis_recipe_load_gate (5), test_gallery_check_at_start (4), test_export_inputs_survive_plot_tab (4), test_export_view_consistency (3), and with 1 or 2 failures each: test_resfinder_abromics_fragment, test_left_join_lesson, test_join_key_one_pin, test_golden_baseline, test_complex_template_runs, test_column_names_through_the_steps, test_checker_advice_visible, test_cache_keys, test_build_change_callers, test_wrangler_upload_step_numbering, test_view_badge, test_ui_app_features_masking, test_tier2_store, test_suggestion_label, test_step_numbering, test_select_order, test_seed_refusal_text, test_scripts_need_the_app_path, test_plot_callers_are_checked, test_gallery_listing, test_export_report_links, test_checker_names_what_a_component_is, test_cache_chain.
- `app/tests/test_shiny_*.py` (13 files, browser tests): the run was cut (each failure takes about a minute); every result seen was a failure (reasoned: the app starts on shipped recipes that the load gate now refuses); the exact list is not complete. A reviewer should run them after step 4.
- `test_recipe_pictures.py` is MINE: its small temporary recipes are in the old shape and `plots_of()` of the tool reads `spec`. IMPORTANT for the next worker: until the recipes are migrated (step 3) the picture check on this branch rejects every recipe at the load gate, so it cannot be used as proof between step 1 and step 3; the proof is the comparison of the migrated recipes with the baseline, after `plots_of()` and `collections_of()` of the tool read the new shape (the one place that knows the recipe shape, step 0 report).

## Needs a decision (D-0165): built nothing for these

1. Key order: D-0237 and the brief say `data_engine` / `plot_engine` is the first key, then `ui_label`, and so on. The checker does NOT enforce the order (YAML mappings have none). Options: no check; an advice (A) when the first key is not the engine; an error. Not chosen.
2. The three pending `label` places (M271): `info.label`, `label` of tables and joins, `label` of `input_fields` entries. One-line change each in `label_keys` once she answers (the checker, not the migration tool, follows the table; the migration tool and the readers (`home_theater`, `gallery_manager`) are later steps).
3. What the rewrite tool does with the old `title:` text of the 26 live plots (D-0253 says it is not decided). The message for `title` names the tool and says what to write by hand; it does not promise a conversion.
4. The three legacy tools `recipe_migration.py`, `strict_form_migration.py`, `contract_migration.py` (format 0 to format 1) write the OLD format-1 shape (`wrangling: {tier1: []}`, `steps:`, `spec:`); their tests are green but a recipe they write is refused by the new checker. Options: adapt them to write the new shape; or retire them (no format-0 recipe is left in the repository?, not checked); or leave them and run the new rewrite tool after them. Not chosen.
5. Which tombstone expiry (a phase number) and the `tasks.md` removal task (`rules_legacy_management.md` 2c and section 4 require a task entry with the deprecation): I wrote "two phases after this change is merged" in the message; a scribe must add the task and fix the number with Eve.
6. `plot_defaults.layers` are checked against the recipe's `plot_engine` (a plot with another `plot_engine` still gets those defaults). Whether defaults are per engine is not decided.
7. The `engines.py` wording (`engine_problem`, used by the viz library) still says "is not built": D-0239 words are in the checker only; `engines.py` is not in my files (step 5).
8. The picture finding above: what to do about a plot whose picture depends on the hash seed (fix in the drawing step, or keep the seed fixed in the check)? Eve decides; it touches "same data and recipe give the same result".

## PROVISIONAL (my own choices)

- The code names `EN02`, `EN03`, `PD02`; the catalogue keys `action_engines` and `component_engines`; the `engines` coverage item.
- The spec data layout: `label_keys`, `old_shapes` (with `tool`), `removed`, element `tier`; format_version stays 1 (D-0236).
- Messages and fixes of the new codes (texts above).
- `PYTHONHASHSEED=0` in the documented picture command; the tool prints the seed and records it.
- Retiring `PS01` (merged into `P01`).
- Adapting `recipe_tiers.py` and `recipe_factory.py` (utils files outside the list).

## Decisions table

| decision | how the code complies | where | test |
|---|---|---|---|
| D-0250 tier is its own key, optional `data_engine`, `steps` | `tiers()`, `tier()`; spec element `tier` | `recipe_check.py` `tiers`, `tier`; `recipe_spec.yaml` elements `tier`, `schema`, `join` | `test_every_tier_form_is_accepted...`, `TIER_CASES` |
| D-0255 one change, every file | nothing is skipped or special-cased; no recipe rewritten here (step 3) | n/a | n/a |
| D-0251 gallery bundles same shape | same checker, gallery profile reads the entry | `recipe_check.py` `gallery`, `plot` | `test_gallery_*` (3) |
| D-0252 whole entry in the plot file; engines planned | include at the entry (F01 for a wrapper); `plot_engine` per entry | `recipe_loader.py` (rule unchanged, doc), `recipe_check.py` `plot` | `test_a_whole_plot_entry_in_its_own_file...`, `test_an_included_plot_entry_whose_file_repeats...` |
| D-0253 `ui_label`, `ui_title`, `title` removed, `labs` | `elements.group/plot`, `old_shapes.plot.title`, `renamed.group/plot.label` | `recipe_spec.yaml` | `test_the_ui_names_are_accepted...`, `test_a_title_in_the_plot_is_refused...` |
| D-0237 no `spec:`, content in the entry, tier at the entry | `plot_content`, `old_shapes.plot.spec`, tier3 key | `recipe_check.py` `plot`, `plot_content` | `OLD_SHAPES`, `test_the_plot_content_is_judged_where_it_is_now...` |
| D-0242 / D-0220 the four dead keys removed | `PD02` from `removed.plot_defaults` | `recipe_check.py` `plot_defaults` | `test_a_dead_plot_defaults_key_is_refused_with_a_tombstone` (4) |
| D-0258 | not in this step (the migration writes `theme_bw`, steps 3 and 5) | n/a | n/a |
| D-0050 no silent error | part A stops instead of drawing with another copy; no silent skip of engine checks (coverage + EN03); old shapes refused with the tool | see above | tests above |
| D-0165 | section "Needs a decision" | | |

Consequence the brief asked for in the compliance sense ("what happens to X after this change?"): an old-shape recipe on this branch is refused whole by the checker, so HOME's load gate rejects every shipped recipe until step 3 runs: the app shows them as rejected with the tool named; nothing is half read.

## Not done

- No recipe file, readers or writers outside `libs/utils` (steps 3, 4); no rewrite tool (step 2); no `engine` field in the registries (step 5); no spec text, rules, docs, `@deps` of other files, dependency index, UML (step 8). `.claude/rules/rules_toolchain.md` row for `recipe_pictures.py` still waits for Eve's yes (step 0 report).
- `docs`: the `@deps` and doc links of the files I touched are unchanged; the dependency index is a later step.
- Stale directory `libs/utils/build/lib/` (an old build copy of the library, git-ignored) exists; I did not touch it.
