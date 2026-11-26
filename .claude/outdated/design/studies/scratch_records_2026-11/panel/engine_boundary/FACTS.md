# The engine boundary today: facts (scout survey, 2026-11-21; filed and shortened by the coordinator)

Read-only; no test run. READ = seen at file:line; REASONED = inferred. Paths from the repository root. Source files only (no tests).

## Counts
- Files that import Polars: 54 (libs 32, app 13, assets/scripts 9). Of them 34 are Polars-specific, 19 mixed with app logic, 1 neutral with a Polars type name.
- Files that import plotnine: 11 (10 in `libs/viz_factory`, 1 script). matplotlib: 8. pandas: 4. mizani: 0.
- The engine is chosen in ONE module, `app/modules/engine_registry.py` (REGISTRY :35, data_entry :38, plot_entry :52, PlotEngines.render :78-99), from a two-row table `libs/utils/src/utils/engines.py:45-48` (`python-polars`, `python-plotnine`).
- Texts a user reads that name an engine or its words: about 104 lines in libs, 62 in app/modules, 41 in app/handlers, 602 occurrences in 38 docs pages.
- Tests guard: every action and component has an engine field; prefix and field agree; unknown engine refused; the engine table; cache keys by engine. NOT FOUND: a test that a library does not import Polars or plotnine outside allowed places.

## What is already decided (ledger numbers; read each before relying on it)
| Point | Status |
|---|---|
| The recipe names `data_engine` and `plot_engine`; a tier or a plot may override (D-0029, D-0219) | DECIDED, built |
| The code chooses the engine; no silent fallback (D-0219: "The code MUST choose the engine") | DECIDED, built |
| Engine names are an open list; an unknown one is refused with "no library for this engine in this app" (D-0239) | DECIDED, built |
| Every registered action and plot component carries an `engine` field; a step under another engine's block is refused (D-0238) | DECIDED, built |
| Prefixes `polars_`, `modif_`, `step_`; `plotnine_` for plot components (D-0036, D-0091, D-0210, D-0254) | DECIDED; the plot rename is not built |
| One entry file per library, `engine_<value>.py` with ENTRY; libraries do not import each other (D-0247) | DECIDED, built (`libs/transformer/src/transformer/engine_python_polars.py`, `libs/viz_factory/src/viz_factory/engine_python_plotnine.py`) |
| Cache: the plot engine is in no table key; a tier's engine is an argument of its key (D-0240) | DECIDED, built (`app/modules/cache_keys.py:36-40, 80, 171-186`) |
| The export records engine per plot and tier and library versions (D-0248) | DECIDED |
| Missing values follow Polars; every filter states `na` (D-0042, ADR-103); row order rules (ADR-090) | DECIDED |
| Any Polars crash shown as a plain message at one place (D-0260) | goal DECIDED, design OPEN |
| The engine "language" selectable in BLUEPRINT (her remark, D-0395) | OPEN |
| Future engines: R backend, ggtree, maps, a JS interactive plot (`.claude/design/feature_extension/`: `r_backend.md`, `bioinformatics_viz.md`, `composite_dashboard_home2.md`, `dashboard_frontend_topology.md`, `sankey_flow_geoms.md`) | OPEN, nothing decided |
| Per-tier engine override plan; her view that a recipe for another engine has other names and tiers (ledger M215, M216) | OPEN |
| Whose seed a plot's random layers use when a second plot engine exists (`engine_registry.py:118-124`) | OPEN |
Contradictions for her (not resolved): the default plot seed is decided (D-0056) but ADR-090 (`architecture_decisions.md:4359`) and ADR-106 V11 (`:5387`) still say open.

## The seams that exist (what passes through)
| Seam | Where | Passes |
|---|---|---|
| Engine choice | `app/modules/engine_registry.py:35-61` | the recipe and a block; returns an entry |
| Run of a tier | `app/modules/orchestrator.py:282, 427-428, 674, 743` (`engine.wrangler().run(lf, rules)`) | a Polars LazyFrame in and out |
| Action registry | `libs/transformer/src/transformer/actions/base.py:26, 29` | a function on a LazyFrame |
| Component registry | `libs/viz_factory/src/viz_factory/registry.py:29, 49` | a schema dict |
| Plot dispatcher | `engine_registry.py:78-99`; built in `app/src/server.py:111` | the table, the recipe, the plot id; returns the factory's result |
| `VizFactory.render` | `libs/viz_factory/src/viz_factory/viz_factory.py:176-177, 267` | a Polars frame in, converted to pandas, a plotnine object out |
| Export | `app/handlers/export_handlers.py:1277-1280, 388-451` | a plotnine object in, PNG or SVG bytes out |
So the dispatch exists for RUNNING a tier and DRAWING a plot. What crosses the seam is still the engine's own object (LazyFrame, plotnine plot), not a neutral one.

## Engine knowledge outside the engine libraries (the part a rewrite must move or mark)
In `libs/utils` (meant to be the neutral base):
- `filter_values.py:30, 374-411` builds Polars conditions; `missing_values.py:26, 45, 75` Polars null and NaN rules; `polars_types.py:17-68` dtype names; `formula_check.py:7-18, 180-197, 508` the Polars formula grammar; `hashing.py:28-36` Parquet metadata through Polars; `recipe_check.py:33, 649-672, 944` one Polars type, a Polars row-order rule and message.
- The lineage walk and the audit read Polars action names and join kinds: `step_effects.py:7-13, 55, 64, 153`; `join_keys.py:36, 124, 161-169, 240`; `key_drop.py:82`; `recipe_graph.py:30-49, 116, 299`; `remove_from_all.py:22, 333` (writes `modif_filter`); `plan_book.py:3, 54` (column name plus the ENGINE's type; the engine's failure sentence); `app/modules/plan_composer.py:9` (the plan from `collect_schema()`).
- Plot side: `random_layers.py`, `plot_text_check.py`, `signature_params.py` (plotnine knowledge); the seed rule `recipe_check.py:1202-1239`.
In `app/`:
- `app/modules/orchestrator.py:9, 556, 581, 679, 773` (LazyFrame types, catches PolarsError); `t3_audit_engine.py:212, 256, 480, 585, 630-654` (casts, drop_nans, "Utf8", filter expressions); `wrangle_studio.py:1302, 2316`; `audit_run.py:45`; `build_failure.py:24`; `opening_build.py:35, 153`; `gallery_examples.py:29, 123`; `data_analysis_recipe_validator.py:41, 157`; handlers `home_theater.py:46, 690-802` (matplotlib placeholder figures drawn by the app itself: a second drawing path), `blueprint_handlers.py:60, 188, 2117`, `gallery_handlers.py:32`, `test_lab_handlers.py:23`; `app/src/server.py:14`.
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:74-75, 117-118, 143` (writes `modif_filter`).
Other libraries that use Polars with no mark: `libs/ingestion` (3 files: `ingestor.py:8, 139-211`, `declared.py:15`, `excel_handler.py:4`), `libs/test_lab` (6), `libs/id_reconciliation` (2; `recipe_steps.py:58, 77` writes Polars formula text into recipes), `libs/viz_gallery` (2), `libs/transformer/src/transformer/anchor.py` (the stored tables: Parquet through Polars), `libs/utils/src/utils/step_migration.py:30-316`.
Stored format: Parquet everywhere (`anchor.py:1-6`, `orchestrator.py:31-39`, `export_handlers.py:1258`).

## The recipe format
Neutral: `id`, `info`, `data_schemas`, `joins`, `analysis_groups`, tiers, `steps`, `audit_steps`, labels.
An engine's own: action names (by prefix), `named_exprs` formulas (Polars expression text), `how` values, `maintain_order` values, `type` dtype names, filter operators, layer and geom names, mapping keys, theme and palette names, `random_state`.
How a part says its engine today: by the block it sits in (`data_engine` / `plot_engine` of the tier, table or plot, else of the recipe top). A step does not name its engine; the checker reads it from the registry field.

## Hardest to separate (facts)
1. `app/modules/orchestrator.py`: runs Polars steps, types everything as LazyFrame, catches PolarsError, and picks the engine entry.
2. `viz_factory.py:176-516`: takes Polars, converts to pandas, draws with plotnine, handles palettes.
3. `plot_config_resolver.py:466-495`: pandas dtype checks inside the neutral config cascade.
4. `formula_check.py` with `checked_plot.py:43-49`: the Polars formula grammar and the plotnine function grammar.
5. `filter_values.py` and `missing_values.py`: Polars conditions and NA meaning in the base library; HOME filters, the T3 translator and the audit depend on them.
6. `recipe_check.py`: called neutral, holds Polars pieces.
7. `join_keys.py`, `step_effects.py`: the lineage holds Polars join kinds and per-action readings.
8. `id_reconciliation/recipe_steps.py`, `step_migration.py`: write Polars formula text into recipes.
9. `home_theater.py:690-802`: the app draws its own matplotlib placeholder figures.
10. `t3_audit_engine.py`: casts, drop_nans and filter expressions in the app.

## Not verified
The build status of each decision; the purpose of every import (many are grep counts; about 20 headers read); the texts of docs and handlers (counts only); `.claude/design/maps_advanced_geo.md` not read; no test run.
