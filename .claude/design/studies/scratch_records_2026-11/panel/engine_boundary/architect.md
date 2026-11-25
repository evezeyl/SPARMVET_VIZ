# The engine boundary: the software architect's viewpoint (panel, 2026-11-21)

Status: a study. Nothing is built and nothing is decided by it. The owner decides.
Order of the study: ledger D-0455 (the study), D-0456 (high priority). Brief: `tmpAI/panel/engine_boundary/BRIEF.md`.
Labels: RUN = I ran it (scripts in `tmpAI/panel/engine_boundary/architect_scratch/`), READ = seen at file:line, REASONED = my inference.
My weight: questions 1, 2, 3, 4, 6, 7. Question 5 belongs to the scientist; I give only what the architecture needs from it.

---

## Summary for the owner (8 lines)

1. Silent result changes first: none of the stages below changes a result for today's two engines (each is guarded by the golden baseline). But four places matter for a later engine: the plot engine gets the table through pandas today, where an integer column with a missing value becomes decimal and "missing" and NaN become the same NaN (RUN); a filter previewed in Polars and run by another engine could keep other rows; a hand-off between engines must refuse a type it cannot keep, never convert it; the plot engine still holds a dead data-filter path (READ).
2. The boundary I recommend: each engine is reached only through its entry file, which gives a fixed list of services (run steps, the plan of columns, what a step writes, write a filter step, check a formula, explain an error, draw a picture, the catalogues). Polars keeps a second, separate role as the app's own table library (reading sources, storing Parquet, the preview), so most of the app does not change when a data engine is added.
3. Between engines only neutral things cross: a table in Arrow form (Parquet when stored, which is already the case) and a drawn picture (bytes plus warnings plus the theme record).
4. Her time question: the rewrite is about 11 to 18 agent sessions in 6 stages (medium confidence, plus or minus 40 %).
5. BEFORE the demo, only two stages, with no risk: stage 0, mark every engine-specific file and add a test that fails when Polars or plotnine is used in an unmarked place (this stops the debt from growing today); stage 1, write the contract (the list of services, as types and tests) without changing any running code.
6. AFTER the demo: stage 2 (one door: the 17 app files that reach into the engine libraries go through the entry), stage 3 (engine knowledge out of `libs/utils`, which holds the lineage and the audit), stage 4 (the neutral table and picture at the seam; HOME's plot display changes visibly), stage 5 (texts and docs).
7. Work in flight: the join warning, the uncertain drop and the tables no plot reads can go on now; the audit dialog should wait only for stage 1 (the contract), so that it is written against services and not against Polars names.
8. To decide first: the target boundary, and whether Polars is named as the app's host table library apart from Polars the data engine (this reconsiders ADR-010 in part: information).

---

## Flags first: anything that could change a result silently

| # | What | Evidence | Today | What the boundary must do |
|---|---|---|---|---|
| F1 | The plot engine receives the table as pandas: `df.collect().to_pandas()` | READ `libs/viz_factory/src/viz_factory/viz_factory.py:267`; RUN `architect_scratch/arrow_roundtrip.py`: an `Int64` column with a null becomes `float64`; null and NaN both become NaN; Boolean with null becomes `object` | This is how the plotnine engine works today. Not a change made by this study. The scientist should know that inside today's plots "missing" and NaN are not told apart (D-0042 keeps them apart in the data). | The neutral input of a plot engine is the Arrow table. Each plot engine converts inside itself, and the conversion it does is stated in its documentation and tested. |
| F2 | A filter tried in the preview and the same filter run as an audit step by another engine could keep different rows (missing values, NaN, ties, string comparison) | REASONED. Today both are Polars, so the question does not arise. The preview filters run in app code with Polars (`app/modules/t3_audit_engine.py:212, 256, 480, 585, 630-654`, READ via FACTS). | No difference today. | The rows shown before the user confirms an audit step (D-0316) are computed by the engine that will run it, never by the host. |
| F3 | A table handed from one engine to another | RUN: Polars to Arrow to Polars kept all 11 types tested (String, Categorical, Enum, Int64 with null, Float64 with NaN, Decimal, Datetime with zone, Duration, Boolean, List, Struct), polars 1.40.1. The Enum's fixed category list travels only as Polars metadata in Arrow (`dictionary<...>` with no list of allowed values); another engine may see a plain category column (REASONED, not checked in any other engine). | No hand-off today (one data engine). | A hand-off that cannot keep a type is refused with a plain message naming the column and the two types; never converted silently (D-0050). Tested with every type of the host vocabulary. |
| F4 | The plot engine still contains a data filter path (`filters` key) | READ `viz_factory.py:236-262`; refused in recipes by check P06 (`libs/utils/src/utils/recipe_check.py:1166-1167`) | Dead for recipes. Whether a test or the gallery still feeds it: NOT VERIFIED. | Removed (no shim) before any second plot engine, so that no plot engine filters data in its own way. |

None of the stages of question 7 changes rows or pictures for the two engines of today. Each stage is checked with the golden baseline (spec DEC43: the content hash of every collection and every plot data of every shipped recipe) and the picture baseline.

---

## Question 1. The target: where neutral code lives and where engine code lives

### What exists (READ)
- One table of engines, names only: `libs/utils/src/utils/engines.py:45-48` (`python-polars`, `python-plotnine`), with `DataEngineEntry` (`wrangler`, `assembler`, `:81-87`) and `PlotEngineEntry` (`factory`, `applied_theme`, `:90-97`).
- One entry file per library (D-0247): `libs/transformer/src/transformer/engine_python_polars.py:22`, `libs/viz_factory/src/viz_factory/engine_python_plotnine.py:22`.
- One chooser: `app/modules/engine_registry.py:35-61`, and the plot dispatcher `:78-99`. Its header says it is "the one place that joins the libraries" (`:1`, `:10-11`).
- That claim is only partly true. RUN (`architect_scratch/scan_imports.py`, AST of the source files, no tests): besides `engine_registry.py`, 7 app files import `transformer` internals (`audit_run.py`, `data_analysis_recipe_validator.py`, `help_registry.py`, `orchestrator.py`, `wrangle_studio.py`, `bootloader.py`, `server.py`) and 11 app files import `viz_factory` internals (`blueprint_handlers.py`, `export_handlers.py`, `home_theater.py`, `blueprint_plot_view.py`, `build_failure.py`, `data_analysis_recipe_validator.py`, `help_registry.py`, `opening_build.py`, `plot_seeds.py`, `wrangle_studio.py`, `server.py`). Polars is imported by 13 app files, 6 `libs/utils` files, and 54 source files in all (the scout's count, confirmed by the same scan).
- A pattern that already works and is neutral: the recipe checker's core imports neither engine library; each caller hands it the registries as plain data (spec section 14, READ `.claude/design/recipe_format_spec.md:534-536`; `engine_registry.engine_tables`, `:64-75`). The plan book is neutral too: a plan is (column name, type as text), a failure is a value (`libs/utils/src/utils/plan_book.py:1-10, 30-59`).

### Three variants

| | V1 Mark only | V2 Adapter per engine | V3 V2 plus neutral objects at the seam |
|---|---|---|---|
| What | Every file and every user-facing text says which engine it belongs to (or neutral, or host). A test guards the imports. No code moves. | Each engine's entry gives a fixed list of services. Everything else calls only those services. Engine objects (LazyFrame, plotnine plot) may still pass through the app, untouched, as opaque values. | As V2, and what crosses between engines and to the screen is neutral: a table handle (Arrow in memory, Parquet when stored) and a drawn result (picture bytes on demand, warnings, theme record). The app never holds a LazyFrame or a plotnine object. |
| Answers "what must change for a new engine" | It lists the places. Each place still has to be rewritten when the engine comes. | The services are the list. A new engine implements them; neutral code does not change. | Same as V2, and also a tier of another engine and a plot engine outside Python (R by subprocess) work without app changes. |
| Rewrite now | Smallest (comments and one test). | Medium to large (stages 2 and 3). | Largest (stages 2, 3 and 4). |
| Risk of drift | High: marks rot unless the test is strict. | Low: the test plus the interface. | Lowest. |
| Weak points | Marks are not design. "Neutral" code in `libs/utils` still holds Polars meaning (filters, NA, types, readings of steps). | An engine object passed through the app ties the app to Python engines that produce such objects (a plotnine plot for Shiny's `render.plot`). | HOME's plot display changes (picture instead of a plot object); Arrow conversion at each engine change costs time; an Enum or similar type needs a refusal rule (F3). |
| Decisions touched (information only) | none | ADR-010 "Polars is the mandatory library for all Wrangling, Ingestion, and Selection" (`architecture_decisions.md:101-107`) in part; D-0247 is kept and the entry grows | as V2; spec DEC42 (scan and sink are "engine functions") would become host functions: the point of DEC42 (not recipe actions) is kept |

### Recommendation: V3, reached in stages through V1 and V2, with Polars named in two roles

Recommended target (REASONED, built on the facts above):

1. **Three kinds of code, each file marked with one:**
   - `neutral`: no engine library. The recipe skeleton, the recipe graph, cache keys, the lineage walk, the audit logic, the checker core, the export record, the UI.
   - `host`: the app's own table library. Polars has two roles today and they should be named apart. As **host** it reads the source files with the declared types, stores and reads Parquet, hashes, shows the data preview, runs the exploration filters (which never change a plot or an export, D-0327). There is ONE host; it is not plural. As **data engine** (`python-polars`) it runs recipe steps; data engines are plural.
   - `<engine value>` (`python-polars`, `python-plotnine`): the dialect. Only the engine's library and its entry file.
2. **One door:** the app and `libs/utils` reach an engine only through its `ENTRY` (D-0247 already names this file). The entry offers services (lists below). What a service returns is plain data or a neutral object.
3. **Neutral objects:** a `TableHandle` (engine value plus the engine's own object, opaque to the app; `to_arrow()` and `from_arrow()` are services of the engine) and a `Drawn` result (picture bytes in a format and size asked, warnings, the theme as applied). Inside one engine, from one tier to the next, the engine may keep its own lazy object (no Arrow conversion when the engine does not change: no cost for today's recipes). At a change of engine the hand-off is Arrow; when a tier is stored it is Parquet, as today.
4. **Plain data instead of names:** what neutral code needs to know about a step (what it writes, which join kind it is, whether it is a row-only step, whether its result depends on row position) is declared by the action in its registry entry, as data, like `ui_schema` and the `engine` field today (D-0238). The walk and the audit read those declarations, never a Polars action name.
5. **Reference semantics and conformance tests:** today's Polars meaning (missing values D-0042 and ADR-103, row order ADR-090, types) is the reference written once as neutral tests. Every engine entry must pass the same conformance tests, or declare each difference, which the app then shows to the user (this is for the scientist and the owner to weigh: question 5, decision 4 below).

Why V3 and not V2: the R backend of `.claude/design/feature_extension/r_backend.md:45-55` (READ) is a subprocess that reads Arrow and returns an image. Under V2 the app would need an R plot object, which does not exist in Python; under V3 it gets a `Drawn` like any engine. And a tier with another data engine needs a hand-off object anyway. Why staged: V1 (stage 0) gives the inventory and stops the growth at once; V2 and V3 follow after the demo.

### The services of a data engine (recommended), where each lives today, where it would live

| Service | What it gives | Today (READ) | Target |
|---|---|---|---|
| D1 Catalogue of actions | names, schemas, engine field, prefix, `wraps` | `transformer/actions/base.py:26, 29`; read directly by `app/src/server.py:40`, `app/modules/help_registry.py:10`, `wrangle_studio.py:27`, `data_analysis_recipe_validator.py:145-149`; partly through `engine_registry.engine_tables` `:64-75` | `ENTRY.catalogue()` returns plain data; the app reads only that |
| D2 Run a tier; assemble a join | the table after the steps | `ENTRY.wrangler`, `ENTRY.assembler` (`engine_python_polars.py:22`), called at `app/modules/orchestrator.py:282, 427-428, 674, 743` with a `pl.LazyFrame` | `ENTRY.run(handle, steps)`, `ENTRY.join(handles, steps)` with `TableHandle`s |
| D3 Table hand-off | Arrow in and out | none; `pl.LazyFrame` typed everywhere in the orchestrator (`orchestrator.py:9, 127, 245, 268, 285, 297, 433, 591, 692`) | `ENTRY.to_arrow(handle)`, `ENTRY.from_arrow(table)`; refusal of a type it cannot keep (F3) |
| D4 Plan of columns | (name, type) after k steps; a failure as a value | `app/modules/plan_composer.py:83` (`collect_schema()`); type is Polars text | `ENTRY.plan(handle)`; each column carries the engine's type text (shown to the user) AND a neutral type (Arrow name) that the walk compares across engines |
| D5 Type vocabulary | type names in casts and in `input_fields.type` | `libs/utils/src/utils/polars_types.py:17-68`; `recipe_check.py:33, 944` | `input_fields.type` stays the HOST vocabulary (the host reads the sources: decision 2); casts inside steps use the engine's names, given in its catalogue |
| D6 Formula grammar | check a formula of a compute step | `libs/utils/src/utils/formula_check.py:7-18, 180-197, 508` (Polars expression grammar) | `ENTRY.check_formula(text)`; the checker calls the one of the block's engine |
| D7 Filter step for an intent | from (column, op, value, na) to a step of this engine | `remove_from_all.py:333` and `blueprint_arch/t3_translator.py:74-75, 117-118, 143` write `modif_filter`; conditions built in `filter_values.py:30, 374-411`, NA in `missing_values.py:26, 45, 75` | the INTENT (column, op, value, na) is neutral, in `utils`; `ENTRY.step_for(intent)` writes the engine's step; the condition builder and NA meaning move into the engine; a copy stays in the host for the preview (F2: the audit dialog shows the engine's result, not the host's) |
| D8 What a step writes (effects) | rename, drop, select, writes names, cast, group, row-only, join (kind, keys, suffix), unread | `libs/utils/src/utils/step_effects.py:55-64` (`READINGS` keyed by Polars names), `join_keys.py:33-40, 161-169` | a field `effect` in each action's registry entry, plain data; the walk reads it (question 3) |
| D9 Join kinds | which kind a join step is | `join_keys.py:36, 240`; `step_effects.py:64` (Polars `how` values) | a neutral list of kinds (left, inner, right, full, semi, anti, cross, as-of, on conditions, self) in `utils`; each engine maps its own words to it in the `effect` field |
| D10 Writing recipe steps for other tools | the bootstrapper, ID reconciliation, migrations | `id_reconciliation/recipe_steps.py:58, 77` (Polars formula text), `utils/step_migration.py:30-316`, `utils/action_names.py:22-73`, `AUDIT_ACTIONS :67` | `ENTRY.step_for(intent)` for each intent these tools need (strip, cast to text, lower case, filter, drop); `action_names.py` becomes the Polars engine's own table |
| D11 Order and determinism advice | which actions depend on row position, which need an order rule, and the advice text | `action_names.py:61` (`POSITION_ACTIONS`); `recipe_check.py:644-672` (texts name `polars_sort`, `polars_with_row_index`) | flags in the `effect` field; advice texts in the engine's message table |
| D12 Error to plain words | the one place of D-0260 | `orchestrator.py:556, 581, 679, 773` catch `pl.exceptions.PolarsError`; `app/modules/build_failure.py:24` | the one place stays in the app; it asks `ENTRY.explain(exc)` (what, where, Suggestion); the raw text is logged |
| D13 Reading the sources | declared types, null tokens | `libs/ingestion/src/ingestion/ingestor.py:139-211` (FACTS) | HOST (recommended; decision 2): one reader for every engine, so a recipe reads its data the same way whatever engine runs it |
| D14 Stored format, hashing | Parquet, metadata | `transformer/anchor.py:1-12` (READ), `utils/hashing.py:28-36` (READ: imports Polars but uses pyarrow) | HOST |
| D15 Versions for the export record | library versions (D-0248) | `engines.engine_versions` `:60-73` (Python package metadata only) | `ENTRY.versions()`: an R engine gives R and package versions |
| D16 The preview and exploration filters | the data table shown | `app/modules/t3_audit_engine.py`, `home_theater.py:1669-1708` (DataGrid) | HOST |

### The services of a plot engine (recommended)

| Service | Today (READ) | Target |
|---|---|---|
| P1 Catalogue of components and their arguments | `viz_factory/registry.py:29, 49`; read directly by `data_analysis_recipe_validator.py:148-149` (`argument_catalog`, `COMPONENT_SCHEMAS`, `PLOT_COMPONENTS`), `help_registry.py:86`, `server.py:41` | `ENTRY.catalogue()`, plain data |
| P2 Normalise and resolve the plot entry (the cascade) | `viz_factory/plot_config_resolver.py`, imported by `app/modules/blueprint_plot_view.py:17`, `plot_seeds.py:28`, `blueprint_handlers.py:100` | stays in the engine; reached through the entry. Whether the five-tier cascade is neutral or plotnine's: NOT DECIDED; I would keep its rule (which tier wins) neutral and its content (layer kinds) in the engine |
| P3 Draw | `VizFactory.render` returns a plotnine object (`viz_factory.py:176`); HOME hands it to Shiny `@render.plot` (`home_theater.py:638`, `:730-733`); the export calls `fig.save` (`export_handlers.py:1294, 1313`); warnings read from the object (`export_handlers.py:36`, `home_theater.py:62`); the opening's proof (`opening_build.py:150`) | `ENTRY.draw(table, entry, seeds, overrides) -> Drawn` with `.picture(format, width, height, dpi)`, `.warnings`, `.applied_theme` |
| P4 The input table | Polars frame, filtered then converted to pandas inside (`viz_factory.py:236-267`) | an Arrow table (from the host or the data engine); the conversion is the engine's own (F1); the `filters` path is removed (F4) |
| P5 Seeds | `engine_registry.py:116-124` (one default seed, PROVISIONAL for a second engine); `utils/random_layers.py`; `recipe_check.py:1202-1239` (FACTS); readers `app/modules/plot_seeds.py:81, 238` | the RULE stays neutral (a seed is written, D-0056); which layers are random and the default seed come from `ENTRY.catalogue()`; the readers take the plot's engine |
| P6 Themes, fonts, palettes | palettes are deployment data injected into the factory (`engine_registry.py:81-93`); themes are components | palettes stay neutral data; themes and fonts are the engine's; the export records the theme as applied (D-0248, already a service: `applied_theme`) |
| P7 Text checks | `utils/plot_text_check.py`, `utils/signature_params.py` (plotnine knowledge in the neutral base, FACTS) | moved into the plotnine engine, reached through the catalogue |
| P8 Error to plain words | `checked_plot.py:368-383` (`show_draw_errors`), `build_failure.py:34` | `ENTRY.explain(exc)` |
| P9 Versions | as D15 | `ENTRY.versions()` |
| P10 The error placeholders of HOME | the app draws its own red matplotlib figures (`home_theater.py:690-693, 705-711, 737-741, 784-787, 802-805`): a second drawing path | not a picture at all: the error text is shown in the plot's place as UI text (neutral) |

---

## Question 2. What a new engine adds, and what still changes

With the target reached (stages 0 to 4 done).

| New engine | What is ADDED | What still CHANGES in existing code (honest) |
|---|---|---|
| A second plot engine in Python (for example a static plotly or lets-plot library) | a library `libs/<name>/` with `engine_python_<name>.py` and its `ENTRY` (P1-P9); its components with prefix `<name>_` and the `engine` field; one row in `ENGINE_TABLE` (`engines.py:45-48`); its message table; the conformance tests run against it; a docs page marked with its engine | 1. one line in `engine_registry.REGISTRY` (`:35`; explicit on purpose, no discovery). 2. The seed readers `seed_in_use`, `export_seed_plan` (`plot_seeds.py:81, 238`) must take the plot's engine: today one default seed for every plot (`engine_registry.py:116-124`, marked PROVISIONAL). 3. BLUEPRINT's forms by engine: OPEN (D-0395). 4. The gallery taxonomy derives `geom` from the first `geom_*` or `stat_*` layer (`rules_gallery_standards.md` 2): grammar words of ggplot; another grammar needs its own rule. 5. If the five-tier cascade is plotnine's content and not neutral (P2), it is copied, not shared. |
| The R backend (`r_backend.md`: subprocess `Rscript`, Arrow in, picture out) | as above, as `engine_r_ggplot2.py` (her own example name in D-0219); the entry calls `Rscript`; `ENTRY.versions()` reads R and package versions; the container gets R (deployment specification) | 1. to 5. as above. 6. Seeds: R's random numbers differ from numpy's; the same seed gives another jitter (the scientist: never promised equal pictures across engines). 7. Fonts on the server differ (the picture differs). 8. A Python test run needs R installed, or the R conformance tests are skipped with a visible reason (never silently). |
| A SQL (DuckDB) or pandas data engine | a library with `engine_python_duckdb.py` (or `_pandas`) and its `ENTRY` (D1-D12, D15); its actions with prefix `duckdb_` (or `pandas_`) and the `engine` and `effect` fields; its formula grammar check; its `step_for` intents (filter, drop, strip, cast to text, lower case); its join-kind mapping; its message table; conformance tests | 1. one line in `REGISTRY`. 2. BLUEPRINT's action picker by engine (OPEN). 3. The id reconciliation and the bootstrapper ask which engine to write for (today they write Polars steps: `id_reconciliation/recipe_steps.py:58, 77`; after stage 3 they call `step_for`, and the only change is which engine they ask). Before stage 3, `utils` filter, NA, formula, readings and the audit writers would all need changing. |
| A tier whose engine differs from its neighbours (for example tier 2 in DuckDB, tier 1 in Polars) | nothing beyond the engine itself: the cache keys already carry each tier's engine (D-0240, READ `app/modules/cache_keys.py:36-40, 80, 171-186` via FACTS); the hand-off is Arrow (D3); the plan book compares the neutral type at the boundary (D4) | 1. The orchestrator's hand-off at an engine change is new code in stage 4, not before. 2. The plan composer (`plan_composer.py:228, 308`) composes per engine and joins at the boundary. 3. Whether such recipes are allowed at all is her plan question (M215: "a data-engine override per tier is a plan owed to her"); the format allows it today. 4. Her view M216: such a recipe has other names and tiers, so its keys differ: consistent with D-0240. |

What can never be added without a change, whatever the variant: a new kind of SERVICE (for example a plot engine that is interactive in the browser, `dashboard_frontend_topology.md`, needs the screen to show HTML, not a picture). That is a new service on the interface and a change in HOME. The boundary makes that change visible and small; it does not remove it.

---

## Question 3. The lineage and the audit

**Is "what a step writes" a service of the data engine?** Yes, but declared as data, not computed by a call. READ: the walk reads a closed list `READINGS` keyed by Polars action names (`libs/utils/src/utils/step_effects.py:55-64`), and `join_keys.py:33-40` lists row-only steps by Polars name; `FOLLOWED_JOINS = ("left", "inner")` (`step_effects.py:64`) and `_KEEPS_LEFT_KEYS` (`join_keys.py:36`) are Polars `how` values. The rule of what may be read (D-0351, D-0356, D-0444: names only, never the formula, always checked against the engine's plan) is neutral. Only the mapping from an action and its arguments to an effect is the engine's.

**How the walk stays neutral (recommended):**
1. A neutral vocabulary in `libs/utils` (one module): effect kinds `keeps`, `rows_only`, `rename`, `drop`, `select`, `writes_names`, `cast`, `group`, `join`, `unread` (the kinds `step_effects.py:66` already uses), the join kinds of D9, and the meaning of each argument role (`mapping`, `columns`, `keys`, `suffix`, `written_names`, `group_columns`).
2. Each registered action declares its `effect` in its registry entry: `effect: {kind: rename, mapping: "mapping"}`, `effect: {kind: join, join_kind_from: "how", kinds: {left: left, inner: inner, semi: semi, anti: anti, right: right, full: full}, keys: [...], suffix: "suffix"}`. Plain data, read through the catalogue (D1), like `ui_schema`. An action without the field is `unread` (the walk greys what depends on it, as today).
3. The walk receives the catalogue's effect table as an argument (the pattern of the checker core, spec section 14). It imports no engine library and no action name.
4. Which join kinds the walk FOLLOWS is a neutral rule over neutral kinds ("left and inner are followed"), not a list of Polars words. A new engine that maps its own join words to `left` is followed with no change in the walk.
5. The plan book carries, per column, the engine's type text (for the user) and a neutral type (for the comparison across an engine change). Within one engine nothing changes (types compared as text, `plan_book.py:5-8`).
6. A test: every registered action of every engine either declares an `effect` or is listed as `unread` with a reason; the test that `READINGS` holds nothing else (`step_effects.py:17-18`) becomes a test over the declarations.

**The audit.** Two paths exist today (READ): the HOME audit applies audit nodes by app code in Polars (`app/modules/t3_audit_engine.py:754`, `audited_frame`, used by HOME and the export), and the target path runs the audit copy through the engine itself (`app/modules/audit_run.py:1-30`: "the engine runs the author's `steps`, then the `audit_steps` of the tier"; not wired to the screen). The second is engine-neutral by construction: the audit steps are recipe steps run by the tier's engine. Recommendation: do not extend `audited_frame`; it is the path to remove when the audit copy is on screen (D-0324). The audit steps are written by `step_for(intent)` of the engine of the tier they go to (D7), so an audit at a DuckDB tier writes a DuckDB filter. The allowed audit intents (filter, column drop, removal by key: D-0322) stay neutral; `AUDIT_ACTIONS` (`action_names.py:67`) becomes "the engine's step for each allowed intent".

**What today's new work must be marked with from the start:**

| New work | Neutral part | Engine part (mark `python-polars`) |
|---|---|---|
| The join warning (D-0452, D-0453, D-0454) | the sentence with YET; the rule "kinds not followed get the red line"; the kind names in the sentence (anti, right, full, self-join) are relational words, neutral | which Polars `how` value is which kind (`step_effects.py:64`, `join_keys.py:36, 240`); the semi-join study is a reading of POLARS semantics: its result is the Polars engine's declaration, not a neutral law |
| The uncertain drop after an unpivot (D-0449) | "the walk could follow X and not Y", the warning, the plain error on failure | that `polars_unpivot` is `unread` (or later declares its effect) |
| Tables no plot reads | entirely neutral (the recipe graph) | none |
| The audit dialog (not built) | the tick lines, the reach, the rows-affected display, the reason | the filter step written (D7), the rows affected computed by the engine that will run the step (F2) |

---

## Question 4. The recipe

**Is the block enough?** For STEPS, yes: a step belongs to the engine of its block (D-0219, D-0238), the registry field says which engine an action belongs to, and the checker refuses a step under another engine's block (EN02, spec `:417`, READ). Nothing needs a per-step engine key; it would be a second source of truth.

**What is neutral and what is dialect (READ spec and FACTS; classification REASONED):**

| Part of the format | Neutral | Engine dialect | Host vocabulary |
|---|---|---|---|
| `id`, `info`, `data_schemas`, `joins`, `analysis_groups`, plot ids, `ui_label`, `ui_title`, `description`, `comment`, `labels`, `taxonomy` (except `geom`) | yes | | |
| tier keys (`tier1`, `tier2`, `tier3`), `steps`, `audit_steps`, `audit_comment`, `data_engine`, `plot_engine` | yes | | |
| `source` (path, format), `input_fields` slugs, `original_name`, `null_values`, `is_entity_key` | yes | | |
| `input_fields.type` | | | yes, if the host reads the sources (decision 2); otherwise it is the dialect of the tier-1 engine |
| action names, their parameters, `named_exprs` formulas, `how`, `maintain_order`, cast dtypes, filter operators of `modif_filter` | | data engine | |
| `mapping` keys, `layers` names and parameters, `theme`, `plot_defaults.layers`, `random_state` | | plot engine | |
| `palette` names | yes (deployment palettes, `config/palettes.yaml`), except matplotlib or brewer names, which are the engine's | | |
| `plot_defaults.random_state` | the rule "a seed is written" (D-0056) is neutral; the number's meaning is the engine's | | |

Her view (M216, not decided): a recipe for another engine has other names and tiers. This agrees with the table: the skeleton stays, the steps and layers change. So a recipe written for Polars does not run under DuckDB by changing `data_engine`; it is refused at every step (EN02), which is correct (D-0050). A translation tool between engines would be a separate, explicit tool, never a fallback.

**What the checker does (recommended):** the core stays neutral and receives, per engine, its catalogue as plain data (already so for names and parameters). Two pieces move out of the core into the catalogue: the formula grammar (`formula_check.py`) and the engine-specific advice texts (`recipe_check.py:628-672, 1041`). The core then calls "the formula check of the engine of this block". The type names of `input_fields` are checked against the host vocabulary.

---

## Question 5. The science (short, from the architecture side only)

The scientist answers this. What the architecture needs from the answer:
- A written reference semantics: Polars as today (D-0042, ADR-103 for missing values; ADR-090 and DEC34 for order; types). Every engine entry runs the same conformance tests (the existing "a `polars_` action equals Polars" tests are the start of it, `rules_verification_testing.md` section 1).
- A rule for a difference: refused, or allowed and shown and recorded. The export already records the engine per tier and plot and the library versions (D-0248); a declared difference would be recorded the same way.
- What can never be promised (REASONED): the same picture from two plot engines (fonts, layout, random numbers); the same floating-point last digits from two data engines (summation order).

---

## Question 6. The standing rule and its test

**How a part is marked (recommended).** One field in the existing `@deps` block of every source file: `# engine: neutral | host | python-polars | python-plotnine`. The `@deps` block is already the project's machine-read header (`workspace_standard.md` section 5, read by `build_dep_graph.py`), so no second header form. A registry entry already carries `engine` (D-0238). A docs page gets `engine:` in its front matter.

**The tests (in `libs/utils/tests/` and `app/tests/`, AST like `architect_scratch/scan_imports.py`, which runs in under a second):**
1. A file that imports `polars` or `pyarrow` must be marked `host` or `python-polars`. A file that imports `plotnine`, `matplotlib`, `pandas` or `mizani` must be marked `python-plotnine` (or a future plot engine). Otherwise the test fails and names the file and the import.
2. A file marked `neutral` imports none of them, and no internal module of an engine library (`transformer.*`, `viz_factory.*` except the entry files). Only `app/modules/engine_registry.py` imports the entry files.
3. Every source file has the field (`engine:` missing fails).
4. A neutral file holds no string that is a registered action or component name (extends `test_action_names.py`, which already fails on a registered name spelled outside the registry for some names, `action_names.py:3-5`).
5. **The ratchet.** Stage 0 cannot fix everything at once, so the test holds an explicit list of today's exceptions (file, import, and the stage that removes it), like a deprecation with its removal task (`rules_legacy_management.md` section 4). A NEW exception fails. Removing a file from the list is part of the stage that fixes it. The list only shrinks. This is not a half fix: it is the inventory, tested.
6. A test can fail: break it once (add `import polars` to a neutral file in a scratch copy) and see it fail.

**User-facing texts that name an engine** (FACTS: about 104 lines in libs, 62 in `app/modules`, 41 in `app/handlers`; 602 occurrences in 38 docs pages). Three kinds:
- the engine's own advice ("write a `polars_cast` step", `recipe_check.py:628`): goes to the engine's message table (stage 5); correct as long as the block's engine is Polars;
- neutral sentences that happen to name Polars ("the engine follows Polars for missing values"): reworded to "the data engine of this table (python-polars)" when a second engine exists, not before;
- docs: each page marked with its engine; the pages about Polars actions are the Polars engine's manual.
Stage 0 makes the inventory (the ratchet counts lines per file); stage 5 moves them.

---

## Question 7. Her time question: the rewrite for today's two engines, in stages

Sizes are in agent builder sessions. Confidence: medium (plus or minus 40 %). They are information for ordering, not an argument.

| Stage | What it does | Touches | Changes behaviour? | Tested by | Risk to the demo | Size |
|---|---|---|---|---|---|---|
| 0 Mark and guard | the `engine:` field in every source file; the import test with the ratchet list; the inventory of engine words in texts and docs | about 75 to 80 files, one comment line each (54 import Polars, 11 plotnine, 17 app files reach into engine libraries, overlapping; RUN scan); 1 to 2 new test files | no (comments and tests only) | the new tests; break once | none | small to medium, 1 session (sonnet) |
| 1 The contract | the service interfaces as types in `utils/engines.py` (no caller changed); the neutral vocabularies (effect kinds, join kinds, filter intent, neutral type); the conformance test skeleton run against the Polars and plotnine entries (thin delegations to existing code); the design file in `.claude/design/studies/` (D-0421) | `utils/engines.py`, 2 entry files, new test files, one design file | no (no running path calls the new methods yet) | conformance tests pass on today's engines | none | medium, 1 opus + 1 sonnet session |
| 2 One door | the 17 app files that import `transformer` or `viz_factory` internals go through `ENTRY` services (catalogues, normalise, draw checks, warnings, anchors, seeds) | the 17 files listed in question 1, the two entry files | no (same calls, another route) | full headless suite, browser suite, golden and picture baselines, the import test (ratchet shrinks) | medium if before (HOME, export, BLUEPRINT, server) | medium, 2 sessions (sonnet, high) |
| 3 Engine knowledge out of the neutral base | the `effect` field on every action; the walk and the audit read it; filter conditions and NA, types, formula grammar, advice texts, join kinds, step writers move into the engine; the checker core takes them from the catalogue | about 20 files: `utils` (`filter_values`, `missing_values`, `polars_types`, `formula_check`, `recipe_check` parts, `step_effects`, `join_keys`, `key_drop`, `recipe_graph`, `remove_from_all`, `audit_copy`, `action_names`, `random_layers`, `plot_text_check`, `signature_params`, `step_migration`), `blueprint_arch/t3_translator.py`, `id_reconciliation/recipe_steps.py`, `app/modules/t3_audit_engine.py` | no by design (same results) | the lineage, audit and checker suites (large today), golden baseline, a test that every action declares its effect | high if before (the lineage and audit work is in flight in these files) | large, 4 to 6 sessions (one opus for the effect vocabulary) |
| 4 Neutral objects at the seam | `TableHandle` and Arrow at an engine change; `Drawn` for every picture; HOME shows a picture of the asked size; the error placeholders become text; the plot engine's dead `filters` path removed (F4) | `orchestrator.py` (820 lines), `plan_composer.py`, `opening_build.py`, `audit_run.py`, `home_theater.py`, `export_handlers.py`, `wrangle_studio.py`, `gallery_examples.py`, `viz_factory.py`, the picture and golden scripts: about 12 to 15 files | yes, visible: how a plot is sized in HOME; errors shown as text instead of a red figure. Results: no | browser suite, picture baseline, her eyes on HOME | high | large, 3 to 5 sessions |
| 5 Texts and docs | engine words in messages go to each engine's message table; docs pages marked; neutral sentences reworded where needed | about 207 code lines, 38 docs pages | wording only | the text ratchet; docs link check | low, but not useful before | medium, 2 to 3 sessions (sonnet or haiku) |

Total: about 11 to 18 sessions.

**Before the demo (no risk): stages 0 and 1.** They touch no running path. Stage 0 alone answers her first words in D-0455 ("recorded as such right now and clear") and stops new debt the day it lands: every new file must say its engine, and no new neutral file may import Polars. Stage 1 gives the audit dialog and the join warning a contract to be written against.

**After the demo: stages 2 to 5,** in that order. Stage 2 and stage 3 can run in parallel only on separate files (stage 3 is in `libs/utils`, stage 2 in `app/`), but both touch the checker and the validator, so I would run them one after the other. Stage 4 waits for her eyes on HOME.

**Work in flight:**

| Work | Can go on now? | Condition |
|---|---|---|
| Join warning (D-0452 to D-0454) and the semi-join study | yes | the kind list stays in `step_effects.py:64` / `join_keys.py:36` (marked `python-polars` in stage 0); the sentence uses the neutral kind words |
| Uncertain drop (D-0449) | yes | neutral logic over the readings |
| Tables no plot reads | yes | graph only |
| The names pass (plotnine rename, D-0091, D-0210) | yes | entirely inside the plotnine dialect; it does not touch the boundary |
| Deployment specification | yes | add one line: which engines (and runtimes, for example R) a deployment installs; the export already records versions |
| The audit dialog (not built) | after stage 1 | written against `plan`, `effect` and `step_for` (as thin Polars delegations at first), not against `modif_filter` and Polars names |
| Anything new on `audited_frame` (`t3_audit_engine.py:754`) | no | this app path is replaced by the audit copy run (`audit_run.py`); extending it adds Polars code in the app |

**What is lost by deciding fast:** little for stages 0 and 1 (reversible: comments, tests, unused interfaces). Deciding the service details fast without the scientist (types, missing values, the host reading the sources) could fix a wrong contract; that is why stage 1 should include the scientist's answer to question 5.
**What is lost by waiting:** every new feature in `libs/utils` and `app/` that names Polars actions or types adds to stage 3. The lineage and audit work of this week adds to exactly the files stage 3 moves. Stage 0 stops that growth at a cost of one session.

---

## Question 8 and the table for the owner

| Point | Status | Proposal | Reconsiders a decision? (information only) |
|---|---|---|---|
| The recipe names `data_engine`, `plot_engine`; a tier or plot overrides; the code chooses (D-0029, D-0219) | DECIDED, built | keep; it is the base of the boundary | no |
| Open list of engine names; refusal words (D-0239) | DECIDED, built | keep | no |
| `engine` field on every action and component (D-0238) | DECIDED, built | extend the registry entry with an `effect` field (question 3) | extends D-0238 (adds a field), no reversal |
| One entry file per library; libraries do not import each other (D-0247) | DECIDED, built | the entry becomes the ONE door, with services; the app's 17 other imports of engine internals go through it | consistent; its "one place" is made true |
| Cache keys by tier engine (D-0240) | DECIDED, built | keep; mixed-engine tiers need no key change | no |
| Export records engines and versions (D-0248) | DECIDED | versions become an entry service (R has no Python package metadata) | no |
| Missing values follow Polars (D-0042, ADR-103); row order (ADR-090) | DECIDED | Polars stays the REFERENCE semantics, written as conformance tests that every engine runs | extends them to several engines: the owner says if a declared difference is allowed |
| Polars is "the mandatory library for all Wrangling, Ingestion, and Selection" (ADR-010) | DECIDED (ADR) | name two roles: Polars as host (one) and `python-polars` as a data engine (one of several) | yes, in part: ADR-010 |
| scan and sink are engine functions (spec DEC42) | DECIDED | storing Parquet becomes a host function; the point of DEC42 (not a recipe action) holds | in part, wording |
| One place for engine crashes (D-0260) | goal DECIDED, design OPEN | the one place asks `ENTRY.explain(exc)` | no |
| Target boundary (V1, V2, V3) | OPEN | V3 in stages through V1 and V2 | ADR-010 (above) |
| Who reads the sources: host or each engine | OPEN | host | ADR-010 (above) |
| The `effect` declaration for the walk | OPEN | in the registry entry, plain data | none; replaces the `READINGS` table built under D-0351 (the content D-0351 allows is kept) |
| HOME shows a picture instead of a plot object | OPEN | yes, in stage 4, with her eyes | none |
| Error placeholders as text, not a red figure | OPEN | yes, in stage 4 | none |
| Seed per plot engine (`engine_registry.py:116-124`) | OPEN (PROVISIONAL in code) | decide when a second plot engine is planned | the contradiction FACTS lists (D-0056 vs ADR-090, ADR-106 V11) is a records issue for a scribe, not this study |
| A tier with another engine than its neighbours (M215 plan owed) | OPEN | allowed in the format; built only in stage 4; offered only when a recipe needs it | no |
| Engine selectable in BLUEPRINT (D-0395) | OPEN | the catalogue service is what BLUEPRINT's forms read, per engine | no |
| Stage 0 and 1 before the demo | OPEN | yes | no |

## To decide first (ranked)

1. **The target boundary.** Options: (a) V1 mark only; (b) V2 adapter with services; (c) V3, V2 plus neutral table and picture at the seam, reached in stages. Recommendation: (c). Information: it reconsiders ADR-010 in part.
2. **Polars in two roles.** Options: (a) Polars is the app's single host library (reads sources with declared types, stores Parquet, the preview, exploration filters) and `python-polars` is one data engine among future ones; (b) each data engine reads its own sources and makes its own preview; (c) no host, everything through the engine of the table. Recommendation: (a): one reader means the same data is read the same way whatever engine runs the steps; the preview is exploration and never a result (D-0327). Pitfall to show: F2 (the audit dialog must show the rows of the engine that will run the step).
3. **Stage 0 now, before the demo.** Options: (a) yes, mark and guard with the ratchet list; (b) after the demo. Recommendation: (a): no running code changes, and it stops the growth she worries about.
4. **The reference semantics for other engines** (with the scientist). Options: (a) every engine must match Polars on the conformance tests, or the action is not offered; (b) a difference is allowed when it is declared, shown to the user and recorded in the export; (c) no rule. Recommendation: (a) for filters, missing values and row order; (b) only for what can never be equal (floating-point last digits, pictures).
5. **Where the walk's knowledge of a step lives.** Options: (a) an `effect` field in each action's registry entry (plain data); (b) one table per engine in `libs/utils`; (c) no readings, the plan only. Recommendation: (a), the pattern of `ui_schema` and `engine`.
6. **Order after the demo** (stages 2 to 5) and that the audit dialog waits for stage 1. Recommendation: as in question 7.
7. **HOME's plot display and error placeholders** (stage 4, needs her eyes): picture of the asked size, errors as text.
8. Later, when a second engine is planned: the seed per plot engine; mixed-engine tiers; BLUEPRINT by engine.

## Not verified

- Whether anything still feeds the plot engine's `filters` path (`viz_factory.py:236-262`) other than recipes (tests, gallery).
- That Shiny's `render.image` (or another output) sized from the client gives the same look as `render.plot` today: REASONED, not tried.
- The type behaviour of Arrow in any other engine (R `arrow`, DuckDB, pandas beyond the one conversion run).
- The exact count of user-facing lines naming an engine: taken from FACTS (grep counts), not re-counted.
- The sizes of the stages: estimates from file counts, not from a prototype.
- That the five-tier plot cascade (`plot_config_resolver.py`) splits cleanly into a neutral rule and plotnine content.
- Whether the checker profile of an audit recipe already gets the registries as plain data in every path (`audit_run.py` header says it uses `integrity_errors`, not the checker's audit profile).
- I did not run the test suites (read-only study).
