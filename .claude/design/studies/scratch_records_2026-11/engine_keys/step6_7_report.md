# Steps 6 and 7 of the big recipe change: BUILT, CONTROLS NOT RUN (saved by the coordinator from the builder's last message, 2026-11-18)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`. Nothing uncommitted. No process left running.

## Commits
- 5531732b feat(cache): the engine of a tier is an argument of its key, the plot engine is in no table key, cache version 5
- 5456c3ab feat(export): effective_run.yaml records the engine per tier and plot, the theme as applied and the library versions

## Step 6, cache keys
Tests: `app/tests/test_engine_keys.py` (27), `app/tests/test_cache_version_5.py` (22), `libs/utils/tests/test_recipe_tiers.py`, `libs/transformer/tests/test_anchor_version_sweep.py`. Break-once: 22 of 22 caught (`tmpAI/breakonce6.py` in the worktree).
- The tier-1 key takes the effective tier-1 data engine of every table and join (the tier's own, else the recipe's; the same function the orchestrator runs with: `utils.engines.tier_engine`).
- The tier-2 key is `tier2_key(tier1_key, steps, engine)`, chained on the tier-1 key; `collection_tier2_key` is the one place that makes it (orchestrator and export use it). An empty tier 2 gives no key.
- The plot engine is in no table key.
- The written `data_engine` text is left out of the tier-1 material, so a tier that writes the recipe's engine has the SAME key as one that inherits it (PROVISIONAL: the plan says "the effective data engine"; no decision says it in words).
- A later stage's engine does not move an earlier key. Same recipe and data give the same keys twice.
- `ENGINE_CACHE_VERSION` is "5". The session key and the recipe hash are NOT changed by this step.
- A stored table whose key does not match is deleted before the rebuild (also when the rebuild then fails). At app start every stored table without the version-5 mark is deleted (`transformer.anchor.remove_tables_of_other_version`); other files are left alone.

## The one notice (PROVISIONAL wording, constant `STORED_TABLES_REBUILT_NOTICE`)
"The tables of your recipes are rebuilt once because the app changed how it names what it stored. Your results do not change."
- When: at an app start that removed at least one stored table of another version. Where: the first browser session of that start (a notification of 20 s) and the Alerts log; the console lists the removed files. How often: once (a second start finds none). Nothing is shown when nothing was stored.
- PROVISIONAL, needs a decision: "once" needed a new field in each stored table (`sparmvet_cache_version` in the parquet footer). Options: (a) built: footer mark, sweep at start, notice; (b) no sweep: remove each table when it is next read, no notice; (c) sweep with no notice. Known limit of (a): the notice is lost if the app is stopped before any browser session connects (the files are still removed).

## Old sessions and old bundles
- A session record holds no table key and no table path; a Restore brings back the audit steps and the tables are rebuilt by the key check.
- A bundle written under version 4 is imported; its engine leg reports "mismatch" with both fingerprints and the existing plain text about a software change; the data leg is unaffected. (Rebuilt with a plain message, not refused.)
- A bundle with the new `engines` key imports with the same four legs; one without it imports as before.

## Step 7, the export record
Tests: `app/tests/test_engine_record.py` (22; the real export generator run headless), `libs/viz_factory/tests/test_applied_theme.py` (9), additions to `libs/utils/tests/test_engine_table.py`. Break-once: 24 of 24 caught.
- `effective_run.yaml` has one new key, `engines`; no other key changed.
- One source: tier engines from `utils.engines.tier_engine`; plot engine and theme from `PlotEngines.record_of`, taken from the plot just drawn; versions read from the installed packages.
- A failed plot: `drawn: false`, `theme: null`, the first line of the reason. An unknown plot engine: recorded as written, not drawn. No theme: `plotnine_default {applies: true, name: theme_gray}` (read from plotnine at run time). An own theme: the component, its values and where it came from.
- Example (scratch run on a tiny test recipe):
```
engines:
  recipe_default: {data_engine: python-polars, plot_engine: python-plotnine}
  tables:
    C: {kind: join, tier1: python-polars, tier2: python-polars}
    T: {kind: table, tier1: python-polars}
  plots:
    p: {plot_engine: python-plotnine, drawn: true,
        theme: {components: [{component: theme_bw, params: {base_size: 14}, from: the plot entry}],
                plotnine_default: {applies: false, name: theme_gray}}}
    q: {plot_engine: python-plotnine, drawn: true,
        theme: {components: [], plotnine_default: {applies: true, name: theme_gray}}}
    bad: {plot_engine: python-plotnine, drawn: false, theme: null, not_drawn_because: "..."}
  library_versions:
    python-polars: {polars: 1.40.1, transformer: 0.1.0}
    python-plotnine: {plotnine: 0.15.4, matplotlib: 3.10.9, viz_factory: 0.1.0}
```

## Tests run (all passed)
- 17 key, orchestrator, session, import and export files: 281 passed (after step 6).
- All `test_export_*.py` except `test_export_download.py`, plus `test_engine_record`, `test_bundle_importer`, `test_cache_version_5`: 303 passed, 4 skipped (after step 7).
- New pure tests: `test_engine_keys` 27; `test_applied_theme` and `test_engine_table` 27 together.

## NOT DONE
- `libs/utils` full run (started, stopped); `libs/transformer` and `libs/viz_factory` suites (only the new files ran; `test_action_engine_field`, `test_component_engine_field` not re-run after the change to the plotnine entry file).
- The qa browser files `test_export_download.py` (it has a new assertion on `engines` that has never run), `test_shiny_smoke.py`, `test_shiny_session_restore.py`.
- The three proofs (pictures, golden, gallery previews). Whether the golden check compares keys: unknown.
- The dependency index regeneration; `@deps` of the orchestrator does not yet name `collection_tier2_key`.

## Open choices and missing decisions
1. The tier-1 key is ONE key per recipe (ADR-089 as built). So the engine of one table also moves the key every other table of the recipe is stored under. A key per table is ADR-101, not built. A test pins today's behaviour. Accept until ADR-101, or build now.
2. Same engine written on a tier or inherited gives the same key (PROVISIONAL).
3. The notice wording and the footer version mark (PROVISIONAL).
4. Tier 3 (the audit) is not in the engine record; no decision says whether it should appear per plot.
5. The package lists behind each engine's versions (polars + transformer; plotnine + matplotlib + viz_factory) are the builder's choice (PROVISIONAL).
6. The record lists the versions of every engine that appears in a table or a plot, also for a plot that failed.
7. Unchecked, outside the task: the `plot_defaults` keys `legend_position`, `facet_panel_spacing`, `default_font_family` seem to be read by the resolver but not applied when drawing.
