# Review of cd06d045..b8d173ed: step 4 fixes, steps 5 to 9, leftovers (final)

Worktree `.claude/worktrees/engine-keys`, head `b8d173ed`. Interpreter: main `.venv`, `utils.__file__` printed = the worktree's `libs/utils/src/utils/__init__.py`. Load read before each run (1.9 to 2.4). No suite run (told). Targeted runs: `test_engine_keys`, `test_cache_version_5`, `test_engine_registry`, `test_engine_record`: **114 passed**. `scripts/audit_cross_lib.py`: PASS. `scripts/audit_deps_verify.py`: PASS (it only checks that a block exists). Scratch files: `.claude/worktrees/engine-keys/tmpAI/review5/`.

## VERDICT: FIX FIRST (small, named), then SOUND TO MERGE AFTER THE FULL CONTROLS

The engine and key work is sound and I found no silent result change. Five things must be done or decided before the merge:
1. **F1 (half fix, fix first).** User-visible errors still tell the user to run a script that now refuses to run: `libs/viz_factory/src/viz_factory/plot_config_resolver.py:352` and `:365` ("Run 'assets/scripts/migrate_plot_specs.py --apply'"); also `scripts/audit_data_analysis_recipe_coherence.py:439,503`, `libs/viz_factory/README.md:50`, `docs/workflows/blueprint_architect.qmd:279`, `.claude/rules/rules_legacy_management.md:58,126`. The script exits 2 (`migrate_plot_specs.py:325-334`) with dead code behind it. Text-only fix, or the removal decision the builder asks (Eve decides).
2. **F2 (needs Eve's yes before merge).** Rule sentences outside D-0249: list in point 6.
3. **F3 (the full controls will fail as it stands).** The picture check prints PICTURES NOT IDENTICAL and exits 1 because of ONE row, the empty orphan `config/data_analysis_recipes/experimental/test_logic.yaml` (its stored rejection text now names one more word, "engines"). D-0255 wants the controls to pass: either delete or migrate the orphan, or re-record that one baseline text, by decision. The same decision covers the 5 orphan files (step8 report 5.2) that the migration did not reach: D-0255 says "EVERY recipe under config/data_analysis_recipes ... nothing is skipped".
4. **F4 (small, tests).** Two layers for the plot engine: not dead, cannot disagree today, but one break goes uncaught (point 1). Name of the missing test below.
5. **F5.** The removal task of the tombstones (PD02, four keys) is not in `tasks.md` (nothing of `.claude/tasks` changed on the branch); `rules_legacy_management.md` section 2c and 4 want it when the tombstone is made. The builder says "made with the merge": a scribe must add it in the merge.

Merge with `dev`: 4 text conflicts (3 are only `@deps` header lines). With `task/export-ready`: 7. Details in point 10.

## Point 1: the engines (read, plus runs listed above)
- Every registry entry carries `engine`; an unknown engine raises `ValueError` and registers nothing (`utils/engines.py`, `actions/base.py`, `viz_factory/registry.py:71`). Both entry files expose `ENTRY`, import only their own library and `utils.engines`. `app/modules/engine_registry.py` is the only file that imports the two entry files (grep). No library imports another (cross-lib audit PASS).
- The code chooses. Tiers: orchestrator `data_entry` for tier 1 of a table, tier 1 of a join, tier 2, also when tier 2 has no steps. Plots: `PlotEngines.render` in HOME (`home_theater.py:540,612`), export (`export_handlers.py:1226`), Blueprint preview (`wrangle_studio.py:705`), gallery previews, golden and picture scripts. Grep for `DataWrangler(`, `DataAssembler(`, `VizFactory(` outside tests: only `assets/scripts/migrate_recipe_format.py:54` (the format 0 migration runs Polars on purpose).
- NOT through the registry, and where: `DataWrangler.tier_steps` (reads the written shape; validator `data_analysis_recipe_validator.py:395,460`, Blueprint `wrangle_studio.py:578`); tier 3 (the audit, Polars code in `t3_audit_engine.py`; a `data_engine` on tier 3 is only checked by T06, nothing reads it to run); `PlotEngines.default_random_state` uses the constant `engines.PLOT_ENGINE` (one-engine assumption, PROVISIONAL, the builder says so); the tier-1 key's version part `engine_fingerprint()` (`cache_keys.py:96`) names polars and transformer by hand, so a second data engine's version would not enter the key (`engines.engine_versions` exists and is not used there). All fine with one engine; each is a decision for the day of the second engine.
- Two layers for the plot's engine. `plot_engine_slot(spec, raw)` (home 484/589, export 1200, wrangle_studio 689) writes the entry's own engine, else the recipe's, into the small dict. The dispatcher reads the entry's own engine from `recipe["plots"][plot_id]`, else that dict value, and then OVERWRITES the dict value (`engine_registry.py:99`). So the slot is needed for the recipe-level default (the small dict has no other copy of it) and its "own entry" half is redundant. They give the same value for every caller today. Consequence: the library's own refusal `viz_factory.py:120-127` is unreachable through the dispatcher. Missing test: a dispatcher-level test through a caller dict where the slot is the recipe's engine and the entry names another (HOME or export), so that "the dispatcher ignores the plot's own engine" fails; today the export break is masked because the slot repeats the own engine. Cleanest fix: the slot returns only the recipe's engine (or `PlotEngines` takes the recipe default as an argument).

## Point 2: refusals (ran: `tmpAI/review5/refusals.py` on the demo recipe copied in memory)
Checker (codes T04 / T06 / EN02):
- No engine line: T04 twice: "data_engine is required | fix: add data_engine" and the same for plot_engine. No default.
- Unknown at the top (`python-pandas`): T06 "'python-pandas' is not a built data_engine: no library for this engine in this app (the engines of this app: python-polars) | fix: write one of python-polars". **But also 79 EN02 lines, one per step**: "the step 'polars_unpivot' belongs to the engine python-polars, but this block is written for the engine python-pandas". One real message hidden among 80 (a plot engine at the top: 51 lines). Suggestion: when the engine name is unknown, say T06 only (an EN02 for a block whose engine is unknown is noise).
- Unknown on one tier: T06 at `data_schemas.Summary.tier1.data_engine` plus EN02 per step of that tier (5 lines). On a tier 2: T06 only. On a plot: T06 + EN02 per layer. Step of another engine in a tier: T06 + EN02. Layer of another engine in a plot: same.
Run time (nothing stored; tested by `test_a_table_whose_tier_names_an_engine...nothing_is_stored`, passes):
- "The tier1 of the table 'A': the recipe key data_engine is 'python-pandas': no library for this engine in this app (the engines of this app: python-polars). | tip: write data_engine: python-polars"
- "The tier1 of the table 'A': the recipe names no data_engine (its value is None). | tip: write data_engine: python-polars"
- "Plot 'p': the recipe key plot_engine is 'r-ggplot2': no library for this engine in this app (the engines of this app: python-plotnine)." and "Plot 'p': the recipe names no plot_engine (its value is None)."
- A plot engine in a data slot: "The tier1 of the join 'J': the recipe key data_engine is 'python-plotnine': no library ...".
Weak words (PROVISIONAL): "the recipe key data_engine" is said also when the value is on a tier; "(its value is None)" is jargon.
All new user texts on this diff (all PROVISIONAL, only "no library for this engine in this app" and the list of engines are decided, D-0239): the four above; registration refusal "Action 'x' cannot be registered: ...."; the removed-key refusal (`plot_config_resolver.py`, "plot_defaults.<key> was removed from the recipe format: the key did nothing (D-0242)." with a tip); the notice "The tables of your recipes are rebuilt once because the app changed how it names what it stored. Your results do not change."; the restore notice "N step(s) of the saved session were not restored: dropping the column X (plot P, your reason was: \"...\"). A join key column cannot be dropped through the audit, because the tables are joined on it. The other M step(s) were restored. Suggestion: use a row filter or row exclusion instead; the saved file is not changed"; the migrate_plot_specs refusal; Blueprint "The steps of the join 'J' cannot be shown: ..."; the form choice "(none: plotnine's default)"; the unknown-key warning now lists the real keys.

## Point 3: the keys (read `cache_keys.py`, `orchestrator.py`, `anchor.py`; ran two probes)
- In the tier-1 key: engine fingerprint (cache version 5, polars and transformer versions), the resolved recipe minus downstream parts and minus written engines, data hash, and `tier1_engines` (the effective engine of every table and join, as an argument). Tier-2 key: tier-1 key, tier-2 steps, the tier-2 engine. The plot engine, `info`, `analysis_groups`, `plot_defaults`, `plots`, top `plot_engine` are out (`_DOWNSTREAM_TOP_LEVEL`). Ran: changing `info.label` and the top `plot_engine` do not change the material; changing the top `data_engine` text does not (the effective value does, as an argument).
- **Label still rebuilds everything (the finding of today is still true on this branch).** Ran `tmpAI/review5/keys_probe.py`: a change of the `label` of a join, the `description` of a join, the `label` of a table, the `description` of a table each change the tier-1 material hash. They are in the key because nothing removes them from the material (`tier1_material` removes only the downstream sections and the written engines). One key per recipe (ADR-089 as built), so any of these rebuilds every table of the recipe. This branch did not change it; it is not a wrong result, it is a rebuild.
- `remove_tables_of_other_version` (`anchor.py:59-88`): walks ONE folder, `<user_data>/anchors`, not recursively (bootloader: `self.get_location("user_data") / "anchors"`). A file is "a stored table" when its name ends `.parquet`, is not hidden, is a regular file, and its footer holds `sparmvet_decision_hash`; it is removed when its footer lacks `sparmvet_cache_version` = "5". Ran on a scratch folder (`tmpAI/review5/sweep_probe.py`): removed `v4.parquet` and `nomark.parquet` (a table with a hash and no version mark); left `v5.parquet`, `user_own.parquet` (a parquet with no hash: not ours), `notes.txt`, `.hidden.parquet`, `sub/v4_in_sub.parquet` (sub-folder not walked), `broken.parquet` (unreadable: left, printed "cannot be read and was left in place"). So it cannot delete a user's own parquet unless that file carries the app's footer key. Two points: a dev app and a branch app that share one `user_data/anchors` folder will fight (the branch removes dev's tables, dev rebuilds); and the folder is never walked recursively, so a table of an old version in a sub-folder stays (no sub-folder is written by the app today, I read the writers: tier 1 and 2 files only).
- The notice: kept in the `Bootloader` (`take_stored_tables_notice`), given to the FIRST browser session that asks (`recipe_gate_handlers.tell_tables_rebuilt`, a 20 s notification), to nobody after. Lost if the app stops before any session connects, and a second user of a multi-user deployment never sees it. The console lists the removed files. (Not run in a browser.)

## Point 4: the record (read `engine_record.py`, `checked_plot.applied_theme`; ran a real export)
- One source: tier engines from `utils.engines.tier_engine`, plot engine and theme from `PlotEngines.record_of` (taken from the drawn plot, calls `plot_entry`, the function `render` chose with), versions from `importlib.metadata` at the moment of the export. Theme cases are covered by `test_applied_theme.py` (9: no theme, plot theme, defaults theme, both complete, partial theme alone, audit override, plain values, not a factory plot, name read from plotnine) and `test_engine_record.py` (failed plot: `drawn: false`, `theme: null`, first line of the reason). I read the code for "a theme layer plus theme_* components": `steps` keeps names starting with `theme` or `element_`; "complete" is any `theme_*` that is not partial; correct. Note: "transformer: 0.1.0" and "viz_factory: 0.1.0" are the package versions of the repository, they do not move when the code moves; the record's `git_commit` field already says which code ran.
- Ran the real export generator headless on the demo recipe `1_test_data_ST22_dummy` (copy under `tmpAI/review5/world`, harness of `test_engine_record.py`; script `tmpAI/review5/export_demo.py`): bundle written, no `EXPORT_NOT_CREATED`, 17 plots `drawn: true`, 0 false, the only new key of `effective_run.yaml` is `engines`, no address appears. Start of the block (full block saved in `tmpAI/review5/engines_demo.yaml` of the worktree); every plot has the same shape, one example below:
```yaml
engines:
  recipe_default:
    data_engine: python-polars
    plot_engine: python-plotnine
  tables:
    QC_Reads_Anchor:
      kind: join
      tier1: python-polars
      tier2: none (T2 equals T1)
    Quast_with_metadata:
      kind: join
      tier1: python-polars
      tier2: none (T2 equals T1)
    Summary_phenotype_length_fragmentation:
      kind: join
      tier1: python-polars
      tier2: none (T2 equals T1)
    ResFinder:
      kind: table
      tier1: python-polars
      tier2: python-polars
    ST22_Anchor:
      kind: join
      tier1: python-polars
      tier2: python-polars
    MLST_with_metadata:
      kind: join
      tier1: python-polars
      tier2: python-polars
    QA_AMR_per_sample:
      kind: join
      tier1: python-polars
      tier2: python-polars
    QA_ST_with_NA:
      kind: join
      tier1: python-polars
      tier2: none (T2 equals T1)
    QA_year_types:
      kind: join
      tier1: python-polars
      tier2: none (T2 equals T1)
    QA_L50_integer:
      kind: join
      tier1: python-polars
      tier2: none (T2 equals T1)
    QA_fanout_exhibit:
      kind: join
      tier1: python-polars
...
  plots:                          # 17 entries; one example
    qa_year_label:
      plot_engine: python-plotnine
      drawn: true
      theme:
        components:
        - component: theme_minimal
          params: {}
          from: plot_defaults of the recipe
        plotnine_default: {applies: false, name: theme_gray}
  library_versions:
    python-polars: {polars: 1.40.1, transformer: 0.1.0}
    python-plotnine: {plotnine: 0.15.4, matplotlib: 3.10.9, viz_factory: 0.1.0}
```
- The record shows the theme-like `element_text` steps "from: the optimisation of the app (from the data)": true and useful (the app adds axis text; D-0242).

## Point 5: join keys (D-0297) (read, no run of the 27 new tests)
- The only creator of a column drop is `filter_and_audit_handlers.py:791` (grep `"drop_column"` over `app` and `libs/*/src`: the other hits read or display it; `t3_translator.py:149` translates). It refuses a key at `:778-786`. The restore (`session_handlers.py:533`) calls `split_key_drops(by_plot, state["primary_keys"])`: drops only `drop_column` steps whose column is a key, keeps the rest in order, tells the user, does not write the file (`session_manager.py:149-170`; the saved file is only read).
- Session of recipe A restored while recipe B is open: NOT refused. The restore warns (different recipe sha256, `session_handlers.py:457-463`) and goes on; the keys are those of the OPEN recipe. A step that drops a column that is a key in B is left out (right for B); a step that dropped a key of A that is not a key of B is restored and applied to B (right for B, and a missing column is then told by the audit). Consistent with "steps apply to the open recipe"; the saved recipe's keys are not stored.
- No key known: `primary_keys` is filled by `_sync_session_provenance` (`home_theater.py:1263-1297`) when the recipe is selected. Reachable only when the recipe has no join (nothing to protect) or when that effect failed before it set the keys; the restore also warns when the recipe key of the open view is missing ("could not be compared"), so a view with no recipe loaded is told. I found no reachable case where a key is known to the recipe, the restore runs and nothing is said, except an exception inside that effect. The builder pinned the silent case with a test.
- Text weak points (builder's own): the plots appear by internal id (`subtab_p1`); a decision propagated to several plots counts once.

## Point 6: the rule commit `724c83ce` (read the whole diff of the six files)
`CLAUDE.md`, `architecture_decisions.md`, `decision_ledger.md`, `.claude/settings.json`, `pyproject.toml`: **unchanged** (empty `git diff --stat`). No `.claude/tasks` change either.
Inside D-0249 (cache-key rule with the engine argument, removal of the four keys, open engine names, `spec:` and tier shape, theme rule, and the examples of those sections): `rules_data_engine.md` cache key and tier-2 persistence lines; the tier mapping sentences; the four-key removal in `rules_data_analysis_recipe_structure.md` §10a and `rules_viz_factory.md` §6b; the L4/L1 rows (true: `_L1_LAYERS` holds only `coord_cartesian` and `facet_null`, `plot_config_resolver.py:48-51`); the examples (`spec:` gone, tiers with `steps`); the `rules_test_lab.md` stub row; `rules_gallery_standards.md` examples.
**Outside D-0249: do not merge without Eve's yes:**
1. `rules_data_analysis_recipe_structure.md` "Visible labels": the label chain now starts with `ui_label` and the new sentence "`ui_title:` (optional) is a longer name that the report uses" (D-0253 is decided, but the rule files it touches are not in D-0249's list); also the comments "(there is no `title:` key)" in the examples of that file and of `rules_agent_role_bioscientist.md`.
2. `rules_data_analysis_recipe_structure.md` §10: "Individual plot specs may override any key" became "Individual plot entries may override `palette` and `theme`": a behaviour sentence, narrowed. (A plot entry also adds `layers`, per the spec's plot element.)
3. `rules_data_analysis_recipe_structure.md` §10a ("Unknown key warning ... Non-fatal — experimental keys are allowed" became "refused by the checker (PD01)"), `rules_viz_factory.md` §6b and §7 ("Non-fatal" became "refused"): a change from warning to refusal of an unknown key. True of the checker (`recipe_check.py:1104`); the plot library still only warns at run time (`viz_factory.py` unknown-key warning). Behaviour rule, not a key removal.
4. `rules_viz_factory.md` §7 L3 bullet: "Allowed: axis text rotation/size (built). Panel spacing and density-aware positions are designed, not built, and have no switch": a status claim about what L3 may do (borderline; D-0242 covers only the missing switch).
New text true? The statements I compared with code are true (PD01/PD02, L1 layers, the no-theme default, tier shape, `wrangling:` refusal in the old-shapes table of `recipe_spec.yaml`). Not changed and now untrue (the builder lists them, step8 report 3.1, 3.2): `rules_viz_factory.md:40` ("YAML `spec`"), `rules_app_structure.md` (no engine_registry), `ui_implementation_contract.md` 7.2 and 12g.3 text of the restore, and the `final_contract`/unprefixed action names in the bioscientist and structure rules (older decisions).

## Point 7: the spec and docs commit `e9aeeeec` (ran the checker on a seeded random sample)
Sample (seed 20261118) of 10 yaml blocks from the 147 in the changed docs: 3 are not recipes (a synthetic-data config, two app-features snippets). Of the 7 recipe blocks wrapped in a minimal recipe and checked (advice codes I02, S04, G02, P02, J03 ignored; `tmpAI/review5/doc_examples.py`): **6 accepted** (polars_unique steps, two input_fields blocks, theme_custom layer, the transformer README join, the blueprint-authoring null_values block; the Standards "NOT this" block is refused as it says, F01/FD01). **1 refused**: `.claude/design/spaces/TEST_LAB.md` from line 361: the recipe header was brought to the new shape but the fragment files under it still show `type: categorical`, `type: string`, `description:` in fields (checker: "'categorical' is not a Polars dtype ... the old word is no longer read", FD01/FD02) and a tier file written as `tier1:` followed by a flat list with unprefixed actions (`regex_replace`, `drop_duplicates`, `null_if`), while the header comment says "the file holds `steps`". Stale, not fatal (a design page).
Tombstone: the four removed keys have a tombstone text in the checker (PD02), the spec (DEC55), the rule files and the changelog ("expire two phases after this change is merged"), but **no removal task in `tasks.md`** (F5). The old shapes (`wrangling`, `steps` container, `spec:`) are refused by name with the rewrite tool, without an expiry.

## Point 8: the leftovers
- One list of `plot_defaults` keys: yes. `utils.recipe_check.plot_defaults_keys()` reads `recipe_spec.yaml`; `plot_config_resolver.py` builds `_VALID_PLOT_DEFAULTS_KEYS` and `_REMOVED_PLOT_DEFAULTS_KEYS` from it; the form asserts its keys are in it. A removed key reaching the resolver raises `VisualizationError` (not ignored).
- Form (`plot_defaults_form.py`, read): `merged_plot_defaults` copies the block and sets only palette and theme; with no theme chosen it removes the key. An untouched Save returns an equal block, with two micro edges: a stored palette with outer spaces is stripped, and a stored non-text theme would be shown as text and written back as text (the checker only accepts a name, so not reachable from a checked recipe). Tests ran in the builder's run, not in mine.
- Form only when the AI agent flag is on: **also so on `dev`** (main folder `app/handlers/blueprint_handlers.py:1789` is the `if not bootloader.is_enabled("blueprint_agent_enabled"): return` before the form at :1808/:1822; the same early return sits at `:1692` on this branch before the form at `:1718`). Not a regression of this branch. Eve decides where the form belongs.
- `migrate_plot_specs.py` callers (grep outside logs): the runtime tips in `plot_config_resolver.py:352,365` (**F1**), `scripts/audit_data_analysis_recipe_coherence.py:439,503`, `libs/viz_factory/README.md:50`, `docs/workflows/blueprint_architect.qmd:279`, `.claude/rules/rules_legacy_management.md`, `rules_agent_role_bioscientist.md:152`, `rules_data_analysis_recipe_structure.md:171` (the DEPRECATED marker of the rule file), `app/tests/test_no_old_recipe_keys_read.py:22`, the script's own docstring. No script or registry calls it automatically.

## Point 9: @deps (spot-check of 6)
OK: `viz_factory.py` consumed_by (now the entry file); `engine_python_polars.py` and `engine_python_plotnine.py` blocks; `engine_registry.py` consumes/consumed_by; `session_manager.py` (new consumes of `join_keys`, `recipe_tiers`, true); orchestrator consumes (no longer names wrangler/assembler, names registry and `collection_body`). Gap: `libs/utils/src/utils/engines.py` `consumed_by` does not name `export_handlers.py`, `home_theater.py`, `wrangle_studio.py`, which each name it in their own `consumes` (`plot_engine_slot`). Older gap: `session_manager` consumed_by lacks `filter_and_audit_handlers.py` (imports `make_audit_step`). The audit script only tests that a block exists.

## Point 10: merge with `dev` (`c7b817ce`) and with `task/export-ready` (`b6bed286`) (ran `git merge-tree --write-tree`)
With **dev**, 4 conflicts:
- `libs/utils/tests/test_recipe_check.py` (~line 174): dev still has the old shape (`["wrangling"]["tier1"]`, `["spec"]`) and ADDED one case: ST06 with `pl.col('v').shuffle(seed=1)`. Keep this branch's shape (`["tier1"]["steps"]`, `plots.p.update(...)`) and re-add dev's extra ST06 line in the new shape. Then run the file: other auto-merged lines of dev may still use the old shape.
- `app/handlers/session_handlers.py` (header `consumes` and the import line): keep both sides: `get_session_import_limits` (dev) and `key_drop_notice, split_key_drops` (this branch); the import line must hold `session_id_collisions, session_input_id_parts` AND `key_drop_notice, split_key_drops`.
- `app/modules/session_manager.py` (@deps header only): union of both provides (dev: `SessionImportLimits`, `session_import_limits_from`, `session_input_id_part...`; this branch: `extract_primary_keys`, `split_key_drops`, `key_drop_notice`) and both consumes.
- `app/src/bootloader.py` (@deps header only): union (dev's additions; this branch's `cache_keys` consumes and `take_stored_tables_notice`).
With **task/export-ready**, 7 conflicts: the 4 above (same resolutions) plus:
- `app/handlers/export_handlers.py`: header (@deps): union. Body (~line 1253): export-ready adds the reading of the plot warnings (`plot_warnings(fig)`, `_warnings_unreadable`, `_plot_warning_rows`); this branch adds `drawn_records[p_id] = viz_factory.record_of(fig, synthetic_data_analysis_recipe, p_id)`. KEEP BOTH, one after the other, inside the same `try` after `fig = viz_factory.render(...)`. Lines of this branch that must survive: the import `from utils.engines import plot_engine_slot` and `from app.modules.engine_record import engine_record, failed_plot_record`; `**plot_engine_slot(spec, cfg.raw_config)` in the synthetic recipe; `drawn_records` dict (defined before the plot loop) and its `failed_plot_record` line in the `except`; `collection_tier2_key` in the stage keys (~1115-1125); `"engines": engine_record(cfg.raw_config, all_plots, drawn_records)` in `effective_run` (~1588, it auto-merged; `all_plots` is now `export_plot_entries(cfg.raw_config)`, all plots, which is what the record wants); the README line about `engines`. `viz_factory` must stay the `PlotEngines` object (it has `render`, `record_of`, `default_random_state`, which export-ready's new line `default=viz_factory.default_random_state` uses: present).
- `app/handlers/home_theater.py` (imports): keep `from utils.engines import plot_engine_slot`; export-ready removed the `fix_label` import and nothing else in the merged file uses it, so drop it.
- `app/tests/test_export_download_path.py` (~line 89): keep export-ready's `SimpleNamespace(import_bundle_upload=None, export_field_change=None)` and this branch's `viz_factory=PlotEngines()`. Check the other export-ready tests that build the handler: `test_export_all_plots_and_defaults.py` passes `viz_factory=None` (fine if it never exports a plot), `test_session_keys_missing_told.py` passes a `MagicMock` (its `record_of` would return a mock: run it).
- Semantic risk for the worker: the export-ready tests that call `VizFactory().render(...)` directly (`audit_nodes.py`, `engine_black_box.py`, many `test_*.py`) keep working (the library is untouched); only the handler's `viz_factory=` argument must be the dispatcher.

## What I did not check
Browser behaviour (the notice, the Blueprint form, HOME with an unknown engine); the 27 join-key tests and the 114 others except the four files I ran; `docs/UML/app.mdj`; the ADR text (not touched by this branch; the builder's list 3.4 stands); each of the 34 passages against the builder's list (I read the whole diff of the six rule files instead); the migration tool's run; the step 4 fixes beyond reading their reports and `3daf60a3` (the tolerant loader still unwraps a lone `input_fields` or `source` wrapper, the strict loader refuses it, F01: two readers still differ); the documents under `docs/` other than the 10-block sample; the golden and picture scripts (not run).
