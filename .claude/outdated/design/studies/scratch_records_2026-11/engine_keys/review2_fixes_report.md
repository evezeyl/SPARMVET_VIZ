# Review 2 fixes (F1, F2, F4, F6, F7, F8) on task/engine-keys

Head after the fixes: `64d99e3f`. Six commits, one per fix, each with the Co-Authored-By line. Nothing uncommitted.

## Commits
- `648e3622` F1 fix(messages)
- `3af87c15` F2 docs(rules): keep only the sentences D-0249 allows; four passages wait for Eve
- `c66a8f91` F4 refactor(engines)
- `3b468eee` F6 fix(check) (PROVISIONAL)
- `a62145c4` F7 docs(deps)
- `64d99e3f` F8 docs(design)

## F1 (messages that named a refusing script)
Changed: `plot_config_resolver.py` (two tips), `scripts/audit_data_analysis_recipe_coherence.py` (two places), `libs/viz_factory/README.md`, `docs/workflows/blueprint_architect.qmd`. They now say: write an explicit `geom_*` layer in `layers:` and the aesthetics under `mapping:` by hand; no script converts it (and the README names `migrate_recipe_engine_keys.py` for an older file shape).
Test: `app/tests/test_no_message_names_the_refusing_script.py` (3 tests: no non-comment line in `app/`, `libs/*/src`, `scripts/` names `migrate_plot_specs`; the scan sees files; the scan can fail). Fail-once: I put `X = "Run assets/scripts/migrate_plot_specs.py --apply"` into the resolver, the test failed, I restored it.
Rule files, NOT changed, for Eve: `.claude/rules/rules_legacy_management.md:58` and `:126`, `.claude/rules/rules_agent_role_bioscientist.md:152`, `.claude/rules/rules_data_analysis_recipe_structure.md:171` (all name `migrate_plot_specs.py --apply` as the migration tool, a DEPRECATED marker that points to a script that refuses). Also not touched: `libs/blueprint_arch/.../group_plot_manager.py:6` (a comment "mirrors migrate_plot_specs.py", not an instruction) and the built site under `docs/_site`.

## F2 (four rule passages)
Page for Eve: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/engine_keys/RULE_PASSAGES_for_eve.md` (written before the edit: per item the file and section, the text on `dev`, the proposed text, why true today with the code place, the decision).
As they now stand (files `rules_data_analysis_recipe_structure.md`, `rules_viz_factory.md`, `rules_agent_role_bioscientist.md`):
1. Visible labels: chain back to `label:` ("1. `label:` field if set"), "All three ... any icons in `label:`", "use `label:` for short emoji-rich tab text", no `ui_title` sentence; both "(there is no `title:` key)" comments removed. Kept (D-0249, no `spec:`): the example of that section without `spec:`.
2. Section 10: "Individual plot specs may override any key." Kept: "L4 plot entry" in the cascade sentence after it.
3. 10a, 6b, 7: the `dev` warning sentence is back ("emit `PipelineError(severity: warning, ...)`. Non-fatal ..."; in 7 "per ADR-079. Non-fatal."), followed by one allowed sentence: the four removed keys are refused with a tombstone text (PD02).
4. Section 7 L3 bullet: "Allowed: axis text rotation/size, panel spacing, density-aware positions." The removal of `optimisation` stays in 10a.
Things Eve must know (also on the page): (a) the rule text now says `label:` in the label chain while the examples and the checker use `ui_label:`; (b) the `ui_title:` line in the plot example of the structure file ("Optional - the longer name the report uses") was not in the list and was left as built: it is a fifth passage of the same kind (D-0253); (c) the restored warning sentence for unknown `plot_defaults` keys is true of the plot library at run time (`viz_factory.py:277-291`) and untrue of the checker (PD01 refuses, `recipe_check.py:1104`).

## F4 (the plot engine, one way)
Single way chosen: `utils.engines.plot_engine_slot(recipe)` carries ONLY the recipe's default `plot_engine`; the dispatcher `PlotEngines.render` alone chooses between the plot entry's own engine (it travels in `plots[plot_id]`) and that default. Why this one: no signature change of `render`, the four callers (HOME x2, export, Blueprint) lose their half, and a single place decides.
Test: `app/tests/test_plot_own_engine_over_recipe.py`: HOME's two builders (the `synthetic_data_analysis_recipe = {...}` expressions cut from the source with `ast`, evaluated, then through the real `PlotEngines` with a stand-in engine) and the export's real generator (the harness of `test_export_download_path.py`): recipe says python-plotnine, entry says python-stand-in: the stand-in draws. Fail-once: I made the dispatcher ignore the entry's own engine (`plot_entry(None, ...)`): the two new tests failed, and 8 others (`test_engine_registry` x5, `test_blueprint_plot_preview_engine` x2); restored.
Adapted: `libs/utils/tests/test_engines.py` (slot tests: only the recipe's, empty when none, an empty value is kept), `app/tests/test_blueprint_plot_preview_engine.py` (its recorder now wraps the real dispatcher; the dict carries the recipe's default, the entry's engine wins), `app/tests/test_plot_engine_reaches_the_factory.py` (docstring).

## F6 (the message flood) - PROVISIONAL (no decision names it; plain-message rule), marked in the code comment (`recipe_check.py`, `check_engine_of`) and the spec row EN02
Rule: when the engine of a block is no engine of the app at all, T06 says it once and its steps and layers get no EN02. A known engine (also a plot engine written in a data slot) keeps its EN02.
Counts on the demo recipe (T06 / EN02), before then after: unknown data_engine at the top 1 / 79 -> 1 / 0; unknown plot_engine at the top 1 / 50 -> 1 / 0; unknown on one tier 1 / 5 -> 1 / 0; unknown on one plot 1 / 3 -> 1 / 0; a plot engine named in a data tier (a known engine): 1 / 5 -> 1 / 5 (unchanged); clean recipe: none.
Tests: `libs/utils/tests/test_recipe_engine_keys.py` (+4: top, tier, plot, and the real EN02 case with 5+2 lines) and one in `app/tests/test_engine_registry.py`. Fail-once: guard disabled, the three unknown-engine tests failed; restored.

## F7
`consumed_by` of `libs/utils/src/utils/engines.py` now names `app/handlers/export_handlers.py`, `app/handlers/home_theater.py`, `app/modules/wrangle_studio.py` (plot_engine_slot). `consumed_by` of `app/modules/session_manager.py` names `app/handlers/filter_and_audit_handlers.py`. Dependency index regenerated (`build_dep_graph.py --root .`). Not added, but true: `session_manager` is also imported by `bundle_importer.py` and `orchestrator.py` (not in its `consumed_by`; not in the brief).

## F8
`.claude/design/spaces/TEST_LAB.md`: the example is the real output of `DataAnalysisRecipeScaffolder.scaffold` for two small tables with `id_reconciliation.recipe_steps` cleaning (scratch under the worktree `tmpAI/f8/`), only the two source paths shown as `data/...`. The six files extracted from the page pass `checker_problems(..., "build")` with no problem. Key points rewritten (polars_ actions, Polars dtype names, no `description:` in fields). FINDING stated on the page: the checker accepts `analysis_groups: {}` but the engine's own load refuses a recipe with no analysis group ("missing the required 'analysis_groups:' block") until the first plot is added.

## Test counts (one process at a time, load 2 to 5)
- `libs/utils`: 2132 passed.
- `libs/viz_factory`: 2296 passed, 27 xfailed.
- The named app tests (engine_registry, engine_record, export_plot_engine, plot_engine_reaches_the_factory, home_reads_the_plot_entry, my 2 new files, blueprint_plot_preview_engine) plus the doc and rule readers of the step 8-9 report (audit_old_words, build_dep_graph, flag_matrix_doc, decision_compliance_files, blueprint_agent_instructions_shape, decision_ledger, transformer test_docs_action_page): 295 passed.
- qa `app/tests/test_shiny_smoke.py`: 37 passed, 3 skipped.

## The three proofs
- Pictures: `error-changed: 1, identical: 50`, PICTURES NOT IDENTICAL (exit 1) because of the one known row, `experimental/test_logic.yaml`. Row before F6 (stored in the baseline): "rejected test_logic.yaml: check: the recipe check did not cover: actions, components. Tip: This is a fault of the app, not of the data analysis recipe: report it." Row now: the same with "actions, components, engines." F6 did NOT change this text again (it is the coverage message, not an EN02); it is the same difference the review saw. No other difference.
- Golden baseline: `result-identical` (exit 0).
- Gallery previews: `identical: 34; size only: 0; differs: 0; new: 0; error: 0`.
Output under the worktree `tmpAI/proof_f/`.

## Not checked / open
- Not run: the full `app/tests`, the other browser files, the other `libs/*` suites, the docs link and launch-command audits.
- F3 of the review (the orphan file and its baseline row) is not mine and is still open; F5 (removal task in `tasks.md`) not mine.
- Other processes seen on the machine (a pytest of the `export-ready` worktree) are not mine; I left no process running.
