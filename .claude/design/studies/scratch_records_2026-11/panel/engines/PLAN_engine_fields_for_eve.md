# Plan: the engine fields are used, overrides, keys, the dead keys, named themes

Written 2026-11-17 for Eve by the architect and developer viewpoint. This is a proposal. Nothing is built, no repository file is changed. You decide.

Labels: **verified** (read at file:line, or run; the small scripts are in `tmpAI/panel/engines/plan/`), **reasoned**, **assumed**. Tags: DECIDED, CONFIRM (a reading of mine that needs your yes), OPEN, MINE (my proposal).

## 0. Read this first

### What was decided (the ledger lines exist now; the scout report said they did not)

- **DECIDED, D-0219:** "the engine would be determined in the correct tier or plot recipe if changed from the default of the recipe". The engine fields are used, the code chooses the engine.
- **DECIDED, D-0220:** "Its dead code - if a key in recipe does nothing its more or less equivalent than deadcode - so we remove that from the recipe structure".
- **Not her words, so CONFIRM:** in D-0219 the sentences "any other value is refused with a plain message until a library exists" and "a data-engine override per tier is a plan owed to her". In D-0220 the sentences about migrating the shipped recipes. The cache-key check is a verification, not a decision.
- **OPEN:** named default themes (yours as an idea only), a second engine, an R snippet (all three NOT decided, nothing here builds them).

### What the recipe author and the user see first

- **A recipe of today:** nothing changes except the seven recipes that set a dead key (section 5). Those are refused with a plain message and the migration tool fixes them.
- **The recipe author** may add one optional line to a plot entry (`plot_engine`) or to a table's step container (`data_engine` per tier). Today the only value that passes is the default's own name. Any other value stops with: *"plot_engine "r-ggplot2" has no library in this app."* and a line starting *"Suggestion:"*.
- **HOME:** the engine of a plot is shown with the plot (one small line), so the key is never invisible. With one engine this line reads the same everywhere.
- **After the update:** every stored table is rebuilt once (the cache version changes, section 3). The user is told in one sentence.
- **The export** records the engine per plot and per table tier (today it records none, section 3).

### What I found today that you did not ask for (all verified)

1. **The export does not hand `plot_engine` to the plot library.** HOME hands it on (`app/handlers/home_theater.py:466`, `:571`) and the Blueprint preview does (`app/modules/wrangle_studio.py:691`); the export builds its own small recipe without it (`app/handlers/export_handlers.py:1144-1147`). The factory then skips its check (`libs/viz_factory/src/viz_factory/viz_factory.py:119-120`). The test that guards this says the export is "not listed here until the line is added" (`app/tests/test_plot_engine_reaches_the_factory.py:5-6`). So "one code path" is three places that build the same dictionary by hand, one of them wrong.
2. **A plot entry's own keys do not reach the draw.** Loading keeps only `spec` (and `info`) of a plot entry in the flat `plots` section (`libs/utils/src/utils/config_loader.py:243-256`). The Blueprint preview reads that flat section first (`wrangle_studio.py:677-679`). A `plot_engine` written next to `spec` would be lost there. The reader must go to `analysis_groups`.
3. **The four dead keys really do nothing** (ran): a plot drawn with `default_font_family`, `facet_panel_spacing`, `legend_position` or `optimisation` in `plot_defaults` gives the same picture, byte for byte (hash `7b337b1b1b7c`), as with `plot_defaults: {}`. `theme: theme_minimal` gives another picture (`1ce16e059ff8`). Script: `tmpAI/panel/engines/plan/dead_keys.py`.
4. **What those keys wanted already works through a theme layer** (ran): `plot_defaults.layers: [{name: theme_bw, params: {base_family: DejaVu Serif}}]` changes the font; `params: {legend_position: bottom, panel_spacing: 0.3}` changes legend and panel spacing (hashes `889ef9754faa`, `96a2d37a526b`). A plot that writes its own complete `theme:` replaces the whole default theme, font included (`1ce16e059ff8` equals plain `theme_minimal`). Script: `plan/theme_via_layers.py`. The theme rule that decides this is marked "to be confirmed by Eve" in `libs/viz_factory/README.md` (section "Theme rule").
5. **A bug in Blueprint's plot-defaults form** (read, not run in a browser; no test mentions the form, grep for `bp_pd_`). The Apply button replaces the whole `plot_defaults` with only what the form holds (`app/handlers/blueprint_handlers.py:1901`). So `random_state` and `layers` of the recipe are dropped. It also always writes a theme: when the recipe has none the form shows and writes `theme_light` (`:1837`, `:1877`) while the library default is `theme_bw` (`plot_config_resolver.py:63`). The export reads the same dictionary (`export_handlers.py:1146`), so a pressed Apply can change the seed and the theme of an export without any record in the recipe file. Class: software bug that changes a result silently. **Suggestion:** fix it in the same change that removes the dead keys (section 5), not later.
6. **Two lists of allowed `plot_defaults` keys** that can disagree: `plot_config_resolver.py:67-70` and `libs/utils/src/utils/recipe_spec.yaml:43`. The checker refuses an unknown key (check PD01, ran: `foo` and `height` are refused), the factory only prints a warning (`viz_factory.py:272-280`), and the rule text says "Non-fatal — experimental keys are allowed" (`.claude/rules/rules_data_analysis_recipe_structure.md`, section 10a). Three statements, two behaviours.
7. **The cache keys already contain the engine names, by accident** (ran, section 3), and the spec says they will later.

## 1. The dispatch with today's two engines

### 1.1 Where the code chooses (MINE, fits ADR-089, ADR-100 point 1, D-0036, D-0219)

Two parts. One names the engines. One joins the libraries. This is the Clear Lines rule (`.claude/rules/rules_runtime_environment.md` section 4: a domain library never imports another; only `app/` joins them).

**Part A, `libs/utils/src/utils/engines.py` (Tier 1, names only, imports no library).** One table, keyed by the engine name:

```python
ENGINES = {
    "python-polars":   Engine(role="data", action_prefix="polars_",   module="engine_python_polars"),
    "python-plotnine": Engine(role="plot", component_prefix="plotnine_", module="engine_python_plotnine"),
}
```

- The allowed values of `data_engine` and `plot_engine` are derived from it (today `ENGINES` is keyed by the recipe key, `engines.py:25`).
- The checker, the recipe writers (`recipe_factory.py:163-164`, `recipe_migration.py:42`, test_lab `bootstrapper.py:169`, `scaffolder.py:209`, `example_recipe.py:136`) and the libraries read it. Nobody types `plotnine_` in a second place.
- A later `r-ggplot2` is one more row and one more library. The prefix `ggplot2_` and the engine come from the same row.
- Two pure functions live here too, like `recipe_tiers.py`: `plot_engine_of(raw, plot_id)` (the plot entry's own value, else the top-level one) and `data_engine_of(raw, collection_id, tier)`. Everything that needs "which engine here" calls them. They read `analysis_groups`, not the flat `plots` section (finding 2).

**Part B, `app/modules/engine_registry.py` (Tier 3, the only place that imports two libraries).** It maps the name to the library's entry:

```python
from transformer.engine_python_polars import ENTRY as _polars
from viz_factory.engine_python_plotnine import ENTRY as _plotnine
REGISTRY = {"python-polars": _polars, "python-plotnine": _plotnine}
```

- Explicit imports, not `importlib` by name: a grep or an audit sees them.
- This sits next to the existing `checker_catalogs()` (`app/modules/data_analysis_recipe_validator.py:112-120`), which already says "Built here because only the app layer may read two libraries". The checker can then get the components of each engine from the same place.

### 1.2 The plot side: one dispatcher, one helper

- **One helper** `render_recipe_for(raw_config, plot_id)` builds the small dictionary for the draw: the plot's spec, `plot_defaults`, and the **effective** plot engine. Today three places build it by hand (`home_theater.py:463` and `:568`, `wrangle_studio.py:688`) and the export builds a fourth without the engine (finding 1). After this there is one.
- **One dispatcher** `render_plot(...)` in `app/` reads the engine from that dictionary, takes the entry from the registry and calls it. An engine without an entry stops with the plain message (section 2.3). There is no fall-back to plotnine, ever.
- **The call sites** that change: `home_theater.py:522` and `:594`, `export_handlers.py:1172`, `wrangle_studio.py:707`, `gallery_examples.py:119` and `assets/scripts/golden_baseline.py:117`. The last two build `VizFactory()` themselves, without the deployment's palettes (`server.py:105`), so they also differ from HOME in the palette today (reasoned from the constructor; not run).
- **The library keeps its own check** (`viz_factory.py:113-126`): a library called directly still refuses an engine it does not build. Two layers, one list (`utils.engines`).
- **What comes back** stays today's object (a `CheckedPlot`, `viz_factory/checked_plot.py:286`) with `save` and the draw. A file-returning engine (R) would change that contract for every plot; that is the first thing to settle for a second engine and is not touched now.

### 1.3 The data side: how `data_engine` gets a real reader

Today nothing reads it except the checker, the writers and tests (grep over `app`, `libs/*/src`, `assets/scripts`). The orchestrator builds Polars classes by hand:

- `app/modules/orchestrator.py:63` (ingestor), `:138-139` and `:391` (`DataWrangler().run`), `:297` and `:313` (`DataAssembler`).
- `DataWrangler._resolve_tier` is also called in `data_analysis_recipe_validator.py:336` and `wrangle_studio.py:574`.

**MINE:** the Polars entry holds exactly these calls (`ingest`, `wrangle`, `assemble`, `tier_steps`). The orchestrator asks `data_engine_of(raw, collection, tier)` and calls the entry. Anchors stay Parquet, which is also the hand-over format between tiers.

**Honest limit:** with one engine the lookup always returns the Polars entry. No user can see a difference. What makes it real is (a) the value is read, (b) an unknown value stops, (c) a test with a stand-in engine proves that the value selects the code (section 7). I flag this to you as question 3.

### 1.4 "Engine-specific code chunked per engine", without moving the code base

- **Now:** one small module per engine, inside the library that already holds its code:
  - `libs/transformer/src/transformer/engine_python_polars.py`
  - `libs/viz_factory/src/viz_factory/engine_python_plotnine.py`
  - Each is a few lines: it names the engine and exposes `ENTRY`. No file moves.
- **The rule for the name:** the module is `engine_` plus the engine value with `-` turned into `_`: `python-polars` gives `engine_python_polars`, `r-ggplot2` gives `engine_r_ggplot2`. These are your own example names. A test checks every row of the table.
- **Later (not now):** a second engine is its own installable library, `libs/engine_r_ggplot2/`, with the same module name and the same `ENTRY`, one more line in the registry. The plotnine library is not touched.
- **Component and action names:** `plotnine_` and `polars_` come from the table. `modif_` and `step_` (D-0091) carry no engine in their name. With a second engine `modif_geom_point` would be ambiguous. **MINE:** every registry entry gets a field `engine`; the checker reads the field, the prefix is for people. This is question 9. It must be in the rename brief now, because the rename is about to touch every registration (D-0210 to D-0214, D-0218).

### 1.5 What a checker can and cannot see here

- **Point of no return:** the draw (a picture is made) and the table write (a Parquet is stored with its key). The strongest check is the load gate (the checker, one list), then the dispatcher and the orchestrator refuse again. A recipe written by hand into a script still meets the library's own check.
- **Not caught by any audit or test I know of:** a seventh call site added later that builds `VizFactory()` itself; a script under `assets/scripts` (they are not in `app/tests`); a real second engine's behaviour. **Suggestion:** a test that reads the source of `app/` and `assets/scripts` and fails on any `VizFactory(`, `DataWrangler(`, `DataAssembler(` or `DataIngestor(` outside the registry modules and the libraries' own tests. The existing test does the same job with a text search for one dictionary and has already missed the export.

## 2. Where an override is written

### 2.1 On a plot entry (MINE; CONFIRM that this is what "plot recipe" means)

The key is `plot_engine`, next to `spec`, not inside it. Reason: `spec` is read by the library the engine selects, so the engine cannot sit in what it reads (the factory refuses unknown spec keys, `viz_factory.py:218-225`).

```yaml
data_engine: python-polars          # default for every table
plot_engine: python-plotnine        # default for every plot
...
analysis_groups:
  Overview:
    label: Overview
    plots:
      st_by_source:
        label: ST by source
        spec: {...}                 # no override: drawn by the default
      tree_by_source:
        label: Tree by source
        plot_engine: r-ggplot2      # this plot only. Refused today: no library for it.
        spec: {...}                 # would use that engine's own component names
```

Today the checker refuses the line as an unknown key (check P01, ran). After the change the checker accepts `python-plotnine` and refuses the rest with the message in 2.3.

### 2.2 On a tier of a table (MINE; CONFIRM)

A tier is a list (ADR-041: ordered logic is a list), so the key cannot sit inside the list. It sits in the step container next to the lists, as a mapping tier to engine:

```yaml
data_schemas:
  primary_data:
    wrangling:
      data_engine: {tier1: python-polars}     # only the tiers named; the others use the recipe default
      tier1: [...]
      tier2: [...]
joins:
  Master_Collection:
    steps:
      data_engine: {tier2: python-polars}
      tier1: [...]
      tier2: [...]
```

- One way only (no scalar form next to the mapping), so a later per-tier use needs no second format change.
- **Tier 3 has no key.** Message: *"tier 3 has no engine key: the audit writes Polars steps, so tier 3 always runs with python-polars."* The plot's `steps:` container (`recipe_spec.yaml`, `tiers: plot: [tier3]`) stays as it is.
- Today the checker refuses such a key (check S06, ran).
- A per-table shorthand (the same key at the schema or join level) is not offered: it would be a second way to write the same thing.

### 2.3 The messages

- Unknown value, any place: *`<path>`: "r-ggplot2" has no library in this app.* / *Suggestion: write python-plotnine (the only plot engine this app has), or remove the line to use the plot_engine at the top of the recipe.*
- A plot engine in a data slot (or the reverse): the existing check T06 says it; it gets the path.
- A layer of another engine (only possible once a second engine exists; tested now with a stand-in): *the layer "plotnine_geom_point" belongs to python-plotnine, but this plot is drawn by r-ggplot2.* / *Suggestion: use a layer of r-ggplot2, or set plot_engine: python-plotnine on this plot.*

### 2.4 What a data-engine override per tier would need later (not built, not decided)

- **A hand-over through Parquet** between tiers. It already exists: T1 is an anchor Parquet and T2 is `<name>__T2.parquet` (`orchestrator.py:26-29`). Each side must read the other's types (Enum, Categorical, Decimal, Datetime with time zone). Not run: R has no `arrow` here.
- **A key per tier** (section 3), and per-tier version records in the export.
- **The audit writes Polars steps** ("remove from all tables", `modif_filter`), so **T3 stays Polars**; a table whose T2 was made by another engine is audited by Polars on its Parquet.
- **The recipe's types are Polars names** (spec 7.4). Another engine needs its own type vocabulary, and the checker needs its action catalogue.
- **What would change a result silently** (the two I re-ran today: `round(2.675, 2)` is 2.68 in Polars and 2.67 in R 4.5.3; `NaN > 2` is true in Polars and NA, so dropped by dplyr's filter, in R. The others in the earlier report, sorting, join on a missing key, random samples, ids above 2^53, were not re-run by me): each step would need its rule written in the recipe. A seeded step can never be equal across engines.
- **`plot_defaults` is written in plotnine's names.** A plot drawn by another engine would not take it. The checker must say so per plot, never skip silently. OPEN, for the day a second engine exists.
- **Cost:** large. Parked by three of four viewpoints in the earlier report. The lighter route stays: prepare the table outside the app and give it to the recipe as a dataset, with the honest limit that the audit and the export do not cover that step.

### 2.5 Flags: what could change a result silently

1. A change of the **top-level default** moves every plot without an override to the other engine at once. **Suggestion:** the checker refuses a plot whose layers belong to another engine (loud), and the export records the engine per plot.
2. A **silent fall-back** (asked R, drawn by plotnine) must not exist. The dispatcher has no default branch: a test for that.
3. The **Blueprint form** (finding 5) already changes plot defaults without a trace. Same fix.

## 3. The cache keys

### 3.1 What the code does today (ran: `plan/keys_probe.py`)

| Change | Tier 1 material changes? |
|---|---|
| top-level `plot_engine` | **yes** |
| top-level `data_engine` | **yes** |
| `plot_engine` on a plot entry | no (`analysis_groups` is downstream, `app/modules/cache_keys.py:51`) |
| a `data_engine` key in a step container | yes (the container stays in Tier 1 material; `without_tier2` removes only the `tier2` list, `libs/utils/src/utils/recipe_tiers.py:94-115`) |

- The key functions take no engine: `tier1_key(material_hash, data_batch_hash)` and `tier2_key(tier1_key, steps)` (`cache_keys.py:93-98`).
- `engine_fingerprint()` holds the cache version, polars and transformer, no plotnine and no engine name (`:70-72`).
- The two engine keys are in Tier 1 only because "everything not listed as downstream is Tier 1" (the fail-safe rule, ADR-089 point 3), not because anyone decided it.
- A picture has no key at all: grep for `plot_key|figure_key|render_key|plot_hash` in `app/` finds nothing. ADR-089 draws one ("plot input = hash(tier2_key, plot spec, plot_defaults, palette), not stored") and no code builds it.

### 3.2 The contradiction and how to resolve it

`.claude/design/recipe_format_spec.md:226-227` says both engines are executed or shown by "checker now; fingerprint and export later". The code already puts both names into every Tier 1 key (above) and nothing into the export. The text is wrong about the code, and no audit caught it (the docs audit does not compare a spec sentence with code behaviour).

**MINE, one rule:** *a key contains the engine of what it stores, and nothing else.*

| Stage | Key | Contains |
|---|---|---|
| Tier 1 table | `tier1_key` | the effective data engine of every tier-1 list (the default and any override) |
| Tier 2 table | `tier2_key(tier1_key, steps, engine)` | the effective data engine of that collection's tier 2, as an argument, so no text change can forget it |
| Tier 3 | not stored; DEC17's key is `hash(tier2 key, steps)` | Polars always |
| Picture | no key today | the plot engine goes into the picture key if one is ever built; today it goes into the export record |

- **The plot engine leaves Tier 1 material** (add `plot_engine` to `_DOWNSTREAM_TOP_LEVEL`, `cache_keys.py:51`). Today a change of the plot engine rebuilds every table for nothing; with an override on a plot entry it would behave differently from the top-level value. One rule is better.
- **The tier-2 engine key is removed from Tier 1 material** (extend `without_tier2`), so changing it rebuilds Tier 2 only.
- **No case where two engines give the same key:** the engine is an argument of the function that makes the key. A property test goes through every (key function, engine pair) with stand-in engines.
- **The recipe bytes also differ.** Your point holds as a second protection: the file-set hash (`cache_keys.py:101-112`) changes for any edit. It does not replace the rule, because the keys are made from the resolved content, not from the bytes (ADR-089 point 4).
- **A new cache version** (`ENGINE_CACHE_VERSION` 4 to 5, `cache_keys.py:47`), as its own comment demands when key rules change. Every stored table is rebuilt once. The message to the user: *"The tables of your recipes are rebuilt once because the app changed how it names what it stored. Your results do not change."*
- **Export record (MINE):** `effective_run.yaml` (`export_handlers.py:1453-1474`) gets the engine per plot and per table tier, and the library versions of the engines used. Today it holds the fingerprint and `software_versions` (polars, shiny, plotnine, `export_handlers.py:105`) and no engine name. In the Publication export the recipe is not in the bundle (only the hash; the recipe file is written only with the reproducibility box, `export_handlers.py:1375-1386`), so the record is the only place the engine is written.
- **Spec text to change (needs your yes):** rows `:226-227` (the "executed or shown by" cell), DEC05 (`:92`), section 4.1 (`:243`, the "closed vocabulary (the engine names)" clause), the check T06 row (`:595`), sections 7.5 and 7.6 (container key), 7.7 (plot entry key), 7.8 (the `plot_defaults` sentence, `:473`).

## 4. Is this a change of the recipe format?

**Yes, as the specification is written** (section 4.1, `:243`): "a key added, removed or renamed ... a change of a closed vocabulary (the engine names)" changes the format number. This plan adds two optional keys and removes four. A recipe written with the new keys is refused by today's checker as an unknown key (ran), so there is no "compatible" change.

Two ways, your choice (question 4):

| | Bump to format 2 | Amend format 1 |
|---|---|---|
| What happens | One migration run: `spec_version: 2`, the four keys removed and listed. Format-1 recipes are refused with "run the migration tool" (check V02). | Edit only the seven recipes; no number changes. |
| Files | 122 recipe files carry `spec_version: 1` today (grep): 16 shipped (7 pipelines, 5 templates, 4 retest), 34 gallery bundles, 4 equality recipes, 68 transformer test recipes. 28 Python files mention `spec_version`; the hard-coded `1` is in `bootstrapper.py:168`, `scaffolder.py:208`, `recipe_migration.py:42`. | 7 files. |
| For | The spec's own rule; a loud, explicit change; exports made under format 1 are told they need migration. | Format 1 was never released: the Dockerfile is not ready and "nothing is deployed yet" (`tasks.md:271`). No migration of 115 files. |
| Against | Work, and every exported bundle of format 1 needs its recipe migrated before a re-run (spec 4.1 consequence b). | Reconsiders the spec's rule that any key change bumps. A recipe or bundle made by you outside this repository under "format 1 as of yesterday" is refused by an unknown key, not by a version message. I did not check whether such files exist. |

**Engine names as an open list (CONFIRM, the coordinator's earlier option 2):** one sentence in 4.1 and DEC05: a new engine name ships with an app release; an app without the library refuses the value with "no library for this engine in this app". Adding `r-ggplot2` later is then a table row, not a format change. With the keys already in the format (this plan), the later feature changes no format.

**Migration (`assets/scripts/migrate_recipe_format.py`, runs A to D today, `:62`):** a new run E that does what is mechanical and says what is not: sets the number (if you choose the bump); removes the four keys from `plot_defaults` and **prints each removed key with its old value and the recipe**; changes nothing else. Safe to run twice. It does not convert a font into a theme layer by itself (question 7).

## 5. Removing the four dead `plot_defaults` keys

Keys: `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`. DECIDED (D-0220); the wording below is mine.

### 5.1 Every place (the scout's list, re-checked by grep)

| Place | What changes |
|---|---|
| `libs/utils/src/utils/recipe_spec.yaml:43` | the four names leave `plot_defaults.optional` |
| `recipe_spec.yaml` (section `renamed`, `plot_defaults`, now `height` and `show_legend`) | the four are added with the removal text; the checker's unknown-key path already prints it (`recipe_check.py:158-159`) |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:67-70` and `:583-585` | the four leave the allowed set; the line that stores them as L2 goes. **Suggestion:** one list: the resolver reads the spec's list from `utils`, or a test compares the two |
| `libs/viz_factory/src/viz_factory/viz_factory.py:272-280` | the warning text names the valid keys; it must say the new set |
| `app/handlers/blueprint_handlers.py:1812-1813`, `:1838-1840`, `:1895-1899`, and the three inputs and the legend list (`:1816`, `:1849-1855`) | the form loses font, spacing and legend; Apply stops replacing the whole dictionary (finding 5). **Suggestion:** move the form's logic into a pure function (`values` and `current defaults` give new defaults) so it is tested without a browser. The hard-coded five theme names (`:1814`) will not survive the rename (D-0214); read them from the registry |
| Recipes: `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:412`, `2_test_data_ST22_dummy.yaml:72`, `stress_test_master.yaml:29`, `app/tests/equality/recipes/2_test_data_ST22_dummy_{dirty,dirty_no_null_text,emptied,fractional_year}.yaml:67` | seven files, all `default_font_family` only (grep over `config docs libs app assets`) |
| Tests: `libs/viz_factory/tests/test_plot_text_runs_no_code.py:222` | two of its four inputs (`default_font_family`, `legend_position`) become refused keys; the test keeps its point with `palette` and `theme`. `app/tests/test_shipped_recipes_hygiene.py:39` passes by itself once the recipes are fixed, and fails if one is missed |
| Docs | `docs/appendix/data_analysis_recipe_structure.yaml:68-76`; `libs/viz_factory/README.md:63` (says L3 does "panel spacing"; the code does axis text only, `plot_config_resolver.py:431-` has no panel code); `docs/appendix/viz_factory_components.qmd:447` is a theme argument and stays |
| Design files | `.claude/design/recipe_format_spec.md:473`; `.claude/design/plot_config_cascade.md` sections 1c (`:45`), 5c (`:162-170`), 7a (`:216-240`), 7b |
| Rule files (your yes first) | see 5.3 |
| Not edited | `docs/_site/` (generated), `libs/utils/build/` (build output), archives and old logs (history) |

`legend_position` inside `theme_bw` params in the test data (`guide_legend_test.yaml:27`, `guide_nrow_test.yaml:24`) is a theme argument, not a `plot_defaults` key. It stays.

### 5.2 The checker's refusal (MINE, plain words)

For each key, at `plot_defaults.<key>`:

- *"default_font_family never changed a picture and is no longer a key of plot_defaults."*
- *Suggestion: to set a font for all plots, write a theme layer with `base_family` in `plot_defaults.layers` (the docs show an example). The migration tool removes the key and prints its value.*
- For `optimisation`: *"the automatic axis-text adjustment still runs for every plot and has no switch. The key `optimisation` was never read."*

### 5.3 Rule text that needs your yes (the sentences)

1. `.claude/rules/rules_data_analysis_recipe_structure.md` section 10: "Individual plot specs may override any key." (false today: a spec refuses these keys, `viz_factory.py:218-225`); the whole block 10a (font, spacing, legend, the four `optimisation` lines); "Unknown key warning: ... Non-fatal — experimental keys are allowed" (the checker refuses them, ran).
2. `.claude/rules/rules_viz_factory.md`: the parenthesis at section 6b ("palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation toggles"); the line "Unknown keys in `plot_defaults` emit `PipelineError(severity: warning ...)` ... Non-fatal"; the L3 line that lists "panel spacing, density-aware positions" as allowed (they are designed, not built).
3. `.claude/rules/rules_runtime_environment.md` section 4: one new sentence (MINE): "An engine library exposes one entry module named `engine_<engine>`; `app/` registers it; `utils.engines` names it."
4. The prefix rule you accepted in D-0218 (rules_viz_factory sections 1, 2 and 7): one clause "the engine of a component is a field of its registry entry".

### 5.4 Conflict with the plot configuration cascade design (`.claude/design/plot_config_cascade.md`)

**Yes, a real one, in intent.** The design lists the three layout keys as allowed `plot_defaults` keys (section 7a) and says the spec "accepts the same keys" (7b). The code never did (the spec refuses them). `optimisation` is a block of toggles "reserved, not implemented" (5c) with three heuristics (jitter, panel spacing, legend columns) that nobody built.

- Your rule (D-0220) wins over a design that was never built; the design file is changed to match, and its section 5c stays as a note, not a key.
- **What stays:** L3 is still the automatic axis-text adjustment. It runs for every plot and can't be switched off. That is a change of a picture the author did not write. **Suggestion:** state it in the user documentation, and decide later whether it needs a switch (question 8).
- ADR-079 (unknown key warning) and ADR-081 (the palette block, the allowed-keys list marked "extend by ADR amendment only") are the ADRs whose text mentions the list; an amendment line is needed, which is your yes.

## 6. Named default themes: a proposal (OPEN, not decided)

### 6.1 What a theme holds

What the removed keys wanted, as typed values: font family, base size, legend position, panel spacing, and the base theme (white or grey background, gridlines). Facts to know:

- A complete theme replaces a complete theme; a partial one is added (`libs/viz_factory/README.md`, "Theme rule (to be confirmed by Eve)", code in `_dedupe_layers`). **A plot that writes its own complete `theme:` loses the default's font and legend** (ran, finding 4). The user of a lab default must be told this.
- `theme_bw`, `theme_gray` and the others already accept `base_size`, `base_family` and any `theme()` setting as parameters (`themes/core.py:20-35`, ran).
- `theme_dashboard` says in its description that it is "the default theme in SPARMVET data analysis recipes" (`themes/core.py:251-265`), but the default is `theme_bw` size 11 (`plot_config_resolver.py:63`). One of the two is wrong.
- The export records no theme (grep `theme` in `export_handlers.py`: only the audit-override line and a report line). With any option below, **MINE:** `effective_run.yaml` records, per plot, the theme as applied (component names and values). The resolver already knows the layers and their tier.

### 6.2 Three options

**Option 1. A copy-in block of the existing layer form.** A named default theme is a ready snippet that Blueprint (or "new recipe") copies into the recipe:

```yaml
plot_defaults:
  layers:
    - name: theme_bw            # after the rename: plotnine_theme_bw
      params: {base_family: "Liberation Sans", base_size: 12, legend_position: bottom, panel_spacing: 0.1}
```

- For: no new key, nothing hidden, the hash and the forked recipe carry it, works today (ran). This is "create default themes and add those to the recipes".
- Against: copied, not linked (a lab change does not reach old recipes; this is the reproducible reading). Two ways to set the default theme (`theme:` string and a layer): the decided change of the `theme:` key (D-0214) has to settle that first.
- Depends on: D-0214 (the new shape of `theme:`), the theme rule. Depends on the open research on arguments (how a recipe passes arguments, nested objects such as `element_text`) **only for nested values**; font, size, position and spacing are plain values.

**Option 2. A theme file of the deployment, used by name** (the palette precedent, `config/palettes.yaml`, ADR-081).

```yaml
plot_defaults:
  theme_profile: lab_default     # looked up in config/themes.yaml
```

- For: one place for the whole lab; short recipes; a picker in Blueprint.
- Against: the recipe alone no longer decides the picture. Same data and recipe give another result if the file differs. The palette registry has the same gap today: no export module mentions a palette (grep over `app/` found the word only in server, ui, bootloader, wrangle_studio and blueprint handlers), so a deployment palette is not in the bundle (reasoned from the grep; not run). Two stores that can disagree. This is the option that most weakens your reproducibility rule.
- Depends on: the same record rule (the export must write the resolved values and a hash of the file); on the arguments research for nested values.

**Option 3. A typed `theme` block with a small fixed vocabulary, translated by each engine.**

```yaml
plot_defaults:
  theme_settings: {base: white, font_family: "Liberation Sans", legend_position: bottom, panel_spacing: 0.1}
```

- For: the same words for every plot engine; the checker can validate every value; no dependency on the arguments research.
- Against: it is the four removed keys again, this time with a reader. A translator per engine, and you said the engines have no 1:1 correspondence. A second way beside the theme layers. More code in the library than option 1.
- Depends on: nothing open; but it adds a structure to the format (a format change of its own).

**A fourth way, not offered:** a registered component with fixed values (`theme_dashboard` is one). D-0211 removes components that an exact one already does, so this reconsiders D-0211 and hides the values in code.

**MINE, not a decision:** option 1 first. It needs no new structure and keeps every value in the recipe. Option 2 only with the export record and the file hash. Option 3 only if you want one vocabulary across engines.

## 7. Order, effort, risks, tests

### 7.1 What can start as soon as you confirm this plan (no other answer needed)

Estimates are mine, labelled **estimate**, not measured, in working days of one builder plus review.

| # | Piece | Estimate | Depends on |
|---|---|---|---|
| A | Remove the four keys: checker, resolver, warning text, the seven recipes, tests, docs, the form fix (finding 5), the theme example in docs | 2 to 3 days | your yes on the rule sentences (5.3); the number in question 4 for the migration |
| B | `utils.engines` table, `plot_engine_of` and `data_engine_of`, checker keys, messages, spec data, format change and migration run E | 2 days | questions 1, 2, 4, 5 |
| C | `render_recipe_for`, the dispatcher, six call sites, the export record, the bypass test | 2 days | B |
| D | Data registry, the orchestrator reads it, the stand-in test | 2 days | B |
| E | Key functions with the engine argument, cache version 5, the stand-in property test, the spec sentence | 1 day | B, question 6 |
| F | Export record of engine and theme per plot and tier; the forked recipe keeps the keys | 1 day | C, D |
| G | Themes (option 1) | 1 day, if option 1 | D-0214 settled, the theme rule |
| | **A to F together** | **about 10 to 12 days** | |

### 7.2 Order

1. **Spec text and ledger lines** from your answers (half a day).
2. **A** first: it makes `plot_defaults` clean before anything is built on it (the architect's request in the earlier report), and A has the most results touched (seven recipes, the form).
3. **B**, so the plotnine rename (D-0210 to D-0214, D-0218) can read the engine table and add the registry field `engine`. **Do not run A, B and the rename on the same files at once:** all three touch `plot_config_resolver.py`, `viz_factory.py`, the recipes and the theme key. Order them, or merge between.
4. **C and D** (independent of each other).
5. **E** after C and D, **F** last, **G** when the theme key is settled.

### 7.3 Risks

- **Conflict with the rename** (same files; order above).
- **The cache rebuild once** after the update; the message above.
- **A migration that drops an author's intent** (the font): the run prints it; the conversion into a theme layer changes pictures, so it is not automatic (question 7).
- **Keys that can only hold the default** are read but make no visible difference until a second engine exists. Tested by a stand-in only. You may see that as the half step you refuse (question 3).
- **The picture contract:** a file-returning engine changes what every call site receives. Not touched here; settle before an R engine.
- **The Blueprint form** has no browser test. The pure function in 5.1 is the way to test it.

### 7.4 Tests that must exist (each decided behaviour tested; each can fail)

All run without a browser.

1. **An engine value selects code** (plot). A registry with a stand-in engine `test-plot-engine` whose entry records the call. The recipe default is the stand-in: the stand-in draws, plotnine does not. A plot entry override: only that plot is drawn by the stand-in. Run over each of the six call sites through the helper. **Break check:** make the dispatcher ignore the value; this test must fail.
2. **An engine value selects code** (data). A stand-in data entry; `data_engine` at the top and `{tier2: stand-in}` on a container; the orchestrator calls the stand-in for exactly that tier. **Break check:** make the orchestrator call the Polars classes directly; fail.
3. **No fall-back:** an engine without an entry raises the plain message and draws nothing (no plotnine call recorded).
4. **The messages:** unknown value at the top, on a plot entry, on a container tier; the role mismatch; tier 3 key; a layer of the other engine (stand-in catalogue).
5. **Keys:** for each key function and every pair of stand-in engines, the key differs; keys of earlier stages do not change; a change of `plot_engine` does not change any table key; a change of the tier-2 engine changes only `tier2_key`; the cache version is 5.
6. **The export:** `effective_run.yaml` has the engine per plot and per table tier, from a real bundle written as the app writes it (as the recent contact test does); the reproducibility recipe keeps `plot_engine` and the container key (`build_mode2_recipe` deep-copies, `t3_translator.py`); a forked join keeps its container key.
7. **Bypass:** the source scan in 1.5; also that `render_recipe_for` is the only builder (replaces the text test that missed the export).
8. **Dead keys:** each of the four is refused with its message, at the checker; the resolver no longer stores them; no shipped recipe, template, retest or gallery recipe has one; the form function keeps `random_state` and `layers` and writes no theme the recipe did not have; the migration prints each removed key with its value, is idempotent, and the **picture before and after is identical** for the seven recipes (pixel hash, as in my run).
9. **One list:** the resolver's allowed keys equal the spec's (or the resolver reads the spec).
10. **Naming rule:** every row of the engine table has its module and an `ENTRY` with the same engine name.
11. **Spec against code:** a test that the engine keys named in the spec's key table are all read somewhere (the contradiction at `:226-227` passed every audit).

**What these would not catch:** a real second engine's pictures, fonts and random numbers (the stand-in proves selection, not behaviour); a deployment whose installed package versions drift; the Parquet type round trip with R (no `arrow` here).

## 8. What you are asked

1. Plot override: the key `plot_engine` next to `spec` on the plot entry (2.1), not inside `spec`. Is that what you meant by "plot recipe"?
2. Tier override: a mapping tier to engine, `data_engine: {tier2: ...}`, in the step container of a schema or join (2.2); no key for tier 3. Yes, or another form?
3. With one engine per role the override keys can only hold the default's name. They are read and tested with a stand-in engine, but no user sees an effect until a second engine exists. Do you accept that as "used", or do you want the tier key left out until a second data engine exists (the plot key and the top-level readers are built either way)?
4. Format number: bump to format 2 with one migration of 122 files, or amend format 1 because nothing is deployed (section 4)?
5. Engine names an open list in the spec (4.1 and DEC05): a new name is a table row, not a format change?
6. The key rule (3.2): the plot engine leaves the table keys; the tier-2 engine is an argument of the tier-2 key; one rebuild of every stored table at the update. Yes?
7. Migration of the seven recipes: only remove the dead key and print its old value (pictures unchanged, verified), or turn the font into a theme layer (the font then takes effect and the pictures of those recipes change)?
8. Dead keys: remove all four, including `optimisation`. The automatic axis-text adjustment then runs always with no switch and is described in the docs. Yes? Do you want a switch later?
9. `modif_` and `step_` carry no engine in the name; every registry entry has a field `engine` that the checker reads. Yes? (The rename brief needs this answer.)
10. Themes: which option (6.2), and confirm the theme rule (a complete theme replaces a complete theme, so a plot's own theme drops the default's font).
11. Blueprint's plot-defaults form: fix the bug (finding 5) in the same change and keep only palette and theme?
12. The folder rule (1.4): a module `engine_<name>` in each existing library now, a separate library for a second engine later. Yes?
13. Record the engine per plot and per tier, and the theme per plot, in `effective_run.yaml`? (The Publication export carries no recipe, so this is the only record.)
14. May the rule and spec sentences in 3.2 and 5.3 be changed?

## Not checked

- The checker's own check of a plot entry beyond `P01` (ran only the cases above), and every profile (`run`, `build`, `gallery`, `audit`).
- Whether `active_cfg()` in the Blueprint form and in HOME is the same object (reasoned from the code, not run in a browser).
- Whether the font `Liberation Sans` exists on the machines that draw the seven recipes. Nothing falls back silently in my run (I used `DejaVu Serif`).
- `audited_frame`'s return type and `checked_plot.py` internals beyond the class line; `gallery_examples.py` and `golden_baseline.py` beyond the call lines.
- Whether the Galaxy and Docker images need changes for the engine modules (no new dependency, reasoned).
- Any recipe or bundle outside this repository written under format 1.
- Anything with R packages (none installed); all effort figures are estimates.
- No test suite was run; only the small scripts in `tmpAI/panel/engines/plan/` (`dead_keys.py`, `theme_via_layers.py`, `keys_probe.py`, `checker_probe.py`, `pd_probe.py`) and two one-line R and Polars comparisons.
