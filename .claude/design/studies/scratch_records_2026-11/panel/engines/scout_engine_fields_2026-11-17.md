**Survey report: engines, plot drawing, cache keys, dead `plot_defaults` keys, themes (read-only, 2026-11-17)**

Root `R` = `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ`. Every path below is relative to `R`. Labels: **V** = read or grepped by me at `file:line`; **S** = taken from the earlier survey files (`tmpAI/panel/engines/`), not re-read by me; **R** = reasoned from code I read.

**Brief note:** the brief has no "Decisions" block. I took the decisions from `.claude/knowledge/decision_ledger.md` directly. Today's words from Eve (`MUST choose`, `place holders`, `dead code`) are not in any `.claude` file (grep for "otherwise why would we" gave no hit). They are therefore not recorded decisions yet.

---

### 1. Every reader of `data_engine` / `plot_engine`

| Where | What it does with the key | Status |
|---|---|---|
| `libs/utils/src/utils/engines.py:21-34` | Defines `DATA_ENGINE`, `PLOT_ENGINE`, `ENGINES`; `engine_problem()` checks a value against the allowed list. | V |
| `libs/utils/src/utils/recipe_check.py:218-221` | `engines()` refuses a value not in `spec["engines"]`. Call site not read. | V (def); call site not read |
| `libs/utils/src/utils/recipe_spec.yaml:10` | Both keys are required at top level. | V |
| `libs/utils/src/utils/recipe_factory.py:163-164`, `recipe_migration.py:42`, `libs/test_lab/src/test_lab/bootstrapper.py:169-170`, `scaffolder.py:209-210`, `libs/viz_gallery/src/viz_gallery/example_recipe.py:136-137` | Write the keys into new recipes. | V (grep); S for the line list |
| `libs/viz_factory/src/viz_factory/viz_factory.py:113-126` | `plot_engine` only: refuses a value the library does not build. Called at `:192`. | V |
| `app/handlers/home_theater.py:466`, `:571` | Copies `plot_engine` into the render dict when present. | V |
| `app/modules/wrangle_studio.py:691` | Same hand-on. | V |
| `libs/utils/src/utils/recipe_spec.yaml:6-8`, `docs/…`, `.claude/design/…` | Text only. | V (grep) |
| `app/`, `libs/*/src` (non-test) | No other code reads either key. Grep over `app`, `libs/utils/src` and the viz/transformer sources found nothing else. | V |

**Your claims, checked:**
- **Confirmed:** `plot_engine` is only checked (`viz_factory.py:113-126`) and handed on (`home_theater.py:466, 571`; `wrangle_studio.py:691`). Nothing selects a library by it. plotnine is always imported.
- **Confirmed:** `data_engine` has no reader outside the checker, the writers and the tests. Polars is not switched by the key.
- **Test readers (V):** `libs/utils/tests/test_engines.py:18-42`, `libs/viz_factory/tests/test_plot_engine.py:30-48`, `test_one_error_form.py:76-78`, `libs/utils/tests/test_recipe_check.py:115-124`, `app/tests/test_plot_engine_reaches_the_factory.py:32-37`.
- **Docs and rules (V):** `.claude/design/recipe_format_spec.md:27-28, 92, 226-227, 530-531`. `app/tests/test_writers_emit_format_one.py:236`.
- **Shipped recipes (V, grep):** 16 in `config/data_analysis_recipes/`, 34 in `assets/gallery_data/`, and the test recipes. All set `python-polars` and `python-plotnine`. Only the values exist. No recipe sets anything else.

### 2. Where plots are drawn, and where tiers are computed

**Draw sites (V, the six from the earlier report):**

| `file:line` | Enclosing function | Calls | Object returned |
|---|---|---|---|
| `app/handlers/home_theater.py:522` | `_group_plot_handler` (`:421`) | `viz_factory.render(lf, …, aesthetic_override=…)` | `CheckedPlot` (a `ggplot` subclass, `libs/viz_factory/src/viz_factory/checked_plot.py:286`); `render` ends at `viz_factory.py:520`. |
| `app/handlers/home_theater.py:594` | `_make_plot_cell_handler` (`:628`) | `show_draw_errors(viz_factory.render(…))` | same |
| `app/handlers/export_handlers.py:1172` | export bundle loop | `viz_factory.render(lf, …)` | `fig` |
| `app/modules/wrangle_studio.py:707` | `architect_active_plot` (`:716`) | `show_draw_errors(viz_factory.render(…))` | `plt` |
| `app/modules/gallery_examples.py:119` | not read | `VizFactory().render(table, raw, plot_id)` | `plot` |
| `assets/scripts/golden_baseline.py:117` | not read | `VizFactory().render(…)` | `plot` |

The developer viewpoint also cites `checked_plot.py:200` (S, not re-read).

**Tiers (V unless marked):**

| Function | Caller | Returns |
|---|---|---|
| `orchestrator.materialize_tier1` (`app/modules/orchestrator.py:169-171`) | `_materialize_tier1` (`:189`) | `pl.LazyFrame`; writes the anchor parquet (S: `:282`, `:318`) |
| `orchestrator.materialize_tier2` (`:324-326`) | `home_theater._resolve_active_lf` (`:298-318`) | `pl.LazyFrame`; the stored file is `<name>__T2.parquet` (`tier2_path_for`, `:26-29`; write `:393`, S) |
| `home_theater._resolve_active_lf` (`:298-319`) | plot handlers, `tier="T2"` | `LazyFrame`: T2 from the orchestrator, else `_resolve_t1_lf(spec)` |
| `t3_audit_engine.audited_frame` (`app/modules/t3_audit_engine.py:654`) | the T3 path | return type not read |
| `libs/utils/src/utils/recipe_tiers.py:48, 94` | `tier2_steps`, `without_tier2` | lists and dicts of steps |

**Dispatcher location (R):** the cleanest seam is `VizFactory.render` (`viz_factory.py:175-192`), where `_refuse_plot_engine_not_built` already sits. Otherwise the six call sites above are the alternatives. The `CheckedPlot` return type is the reason a second engine would change the caller contract (S, developer viewpoint).

### 3. Where an engine key on a plot or tier would be refused today

- **On a plot entry:** `viz_factory.py:218-225` refuses any key not in `_CANONICAL_SPEC_KEYS` (`plot_config_resolver.py:74-77`: `target_dataset, mapping, layers, theme, facet_by, palette, labels, guides, filters, title, _meta`). Message: `"'<key>' is not a key of a plot spec"`, fix `remove it, or write one of …`. The checker's own plot-entry check was not read.
- **In `plot_defaults`:** `plot_config_resolver.py:586-587` sends an unknown key to `unknown_pd_keys`. `viz_factory.py:272-280` then prints a warning `"Unknown plot_defaults key '…' — ignored."`. It is a warning, not a refusal, and the plot still draws.
- **Top level, wrong value:** `recipe_check.py:221` → `"<value>" is not a built <key>`, fix `write one of python-polars` (`engines.py:33-34`). `viz_factory.py:125` → `it cannot be drawn: … (recipe key plot_engine)`.
- **Tier level:** no tier-level engine key exists, so none is refused by name. An unknown key in a collection's tier list is not checked here (not read).

### 4. Cache keys and hashes

Code (`app/modules/cache_keys.py`, V):
- `:51` `_DOWNSTREAM_TOP_LEVEL = ("info", "analysis_groups", "plot_defaults", "plots")`.
- `:70-72` `engine_fingerprint()` = `f"{ENGINE_CACHE_VERSION}|polars=…|transformer=…"`. **No plot or data engine name.**
- `:80-85` `tier1_material(raw)` = everything not in `_DOWNSTREAM_TOP_LEVEL`, then `without_tier2`. **So `data_engine` and `plot_engine` are inside Tier 1 material.**
- `:93-94` `tier1_key = hash_text("\n".join(["tier1", engine_fingerprint(), material_hash, data_batch_hash]))`.
- `:97-98` `tier2_key = hash_text("\n".join(["tier2", tier1_key_value, canonical_hash(steps)]))`.
- `:197` `data_analysis_recipe_sha256` = file-set hash (`:101-112`, `relative_path:sha256` lines).
- `:198` `material_hash = canonical_hash(tier1_material(config.raw_config))`.

**Consequences (R):**
- Changing the top-level `data_engine` or `plot_engine` value changes `material_hash`, so **`tier1_key`** changes, so **every `tier2_key`** changes, and the **file-set hash** changes (any byte change does). The export's `stage_keys` (`export_handlers.py:1046-1053`) and the provenance (`:197`) therefore change too.
- The key rebuilds everything although Polars and plotnine do not change. That is a rebuild with no effect on the result.
- A per-plot override would **not** change any key today: `plots` is excluded (`:51`), and no plot-level key exists (grep for `plot_key|figure_key|render_key|plot_hash` in `app/`: no hit).
- A per-collection or per-tier override: `tier2_key` already hashes the tier steps (`:98`), so it would change `tier2_key` for that collection. `without_tier2` (`recipe_tiers.py:94`) removes tier lists from Tier 1 material. Which key would have to include the override: `tier2_key` for a tier, `tier1_key` for the top level.
- Export records: `effective_run.yaml` holds `data_analysis_recipe_sha256`, `engine_fingerprint`, `software_versions` (`export_handlers.py:1453-1474`); no engine name. `software_versions` lists `polars`, `shiny`, `plotnine` (`export_handlers.py:105`). `plot_engine` is not exported (tasks.md:365, S).

**Contradiction (rule H):** `recipe_format_spec.md:226-227` says the engines are "checker now; fingerprint and export later". The code already puts both keys in Tier 1 material (`cache_keys.py:51, 80-85`). Reported, not resolved.

### 5. The four dead `plot_defaults` keys

Keys: `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`.

**Accepted (V):**
- `libs/viz_factory/src/viz_factory/plot_config_resolver.py:67-70` `_VALID_PLOT_DEFAULTS_KEYS` (the four keys plus `palette, theme, layers, random_state`).
- `resolver:583-585` stores each into `seed[key]` with provenance `L2`.
- `libs/utils/src/utils/recipe_spec.yaml:43` (the checker's list).
- `libs/viz_factory/src/viz_factory/viz_factory.py:279-280` (the warning text lists them as "Valid keys").
- `.claude/rules/rules_data_analysis_recipe_structure.md:220-241` (section 10 per S; the keys are at `:229-236`).
- `.claude/design/plot_config_cascade.md:45, 222-229`; `.claude/design/recipe_format_spec.md:473`.
- `.claude/rules/rules_viz_factory.md:76`.
- `docs/appendix/data_analysis_recipe_structure.yaml:71-74`.

**Writers and readers in the app (V):**
- `app/handlers/blueprint_handlers.py:1812-1813` (the form's key list), read `:1838-1840`, write `:1895-1899`. Blueprint writes `default_font_family`, `facet_panel_spacing`, `legend_position` into the recipe. **It writes them; no render code reads them.**

**Shipped recipes that set one (V grep unless marked):**
- `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:72`: `default_font_family: "Liberation Sans"`.
- `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:412`: same value.
- `config/data_analysis_recipes/pipelines/stress_test_master.yaml:29`: `Liberation Sans`.
- `app/tests/equality/recipes/2_test_data_ST22_dummy_{dirty,dirty_no_null_text,emptied,fractional_year}.yaml:67`: `"Liberation Sans"`.
- S (not re-read): `templates/e_coli.yaml:95` and `templates/audit.yaml:42` set `theme_minimal`; the gallery sets none.

**Tests that set one (V):** `libs/viz_factory/tests/test_plot_text_runs_no_code.py:222` (uses `default_font_family` and `legend_position` as input values).

**Do they have an effect? (V, the render path)**
- `default_font_family`, `facet_panel_spacing`, `legend_position`: **no effect.** No code outside the allowed-key lists and the Blueprint form reads them (grep over `app/` and `libs/` non-test).
- `optimisation`: **no effect.** Grep for `optimisation` as a key found no reader (only `resolver:69` and `recipe_spec.yaml:43`). The docs example `optimisation.auto_axis_text` is not read anywhere.
- The L3 axis-text heuristic runs by itself: `compute_optimisation_layer` (`resolver:431`, called `:590`) reads the data and the spec, not the `optimisation` key.

**Silent-effect issue:** the key is accepted, stored, and then nothing happens. The only signal is the "valid keys" text in the warning for unknown keys, which does not fire for these four.

### 6. Themes

- **Registered components (V):** 17 in `libs/viz_factory/src/viz_factory/themes/core.py`: `theme_gray` (`:43`), `theme_bw` (`:59`), `theme_linedraw`, `theme_light`, `theme_minimal` (`:107`), `theme_classic`, `theme_void`, `theme_dark`, `theme_538`, `theme_matplotlib`, `theme_seaborn`, `theme_tufte`, `theme_xkcd`, `theme_dashboard` (`:251`), `theme_publication` (`:271`), `theme_legend_position` (`:291`), `theme_custom` (`:311`).
- **Default:** `theme_bw` (`plot_config_resolver.py:63`; `viz_factory.py:135`).
- **Resolution (V):**
  - `plot_defaults.theme` is a string; it becomes a layer with `params: {}` (`resolver:579-582`).
  - A spec `theme:` string also becomes a layer with `params: {}` at L4 (`resolver:644-647`).
  - A plot `theme` overrides the default. The spec `layers:` list takes `name` plus `params` (`resolver:650-652`).
  - `plot_defaults.layers` is accepted at L2 (`resolver:573-575`, allowed by `:69`). So **a theme with arguments can be written in `plot_defaults` today, through `layers:`**, not through `theme:`.
- **Themes with arguments:** `theme_legend_position` takes `position` (`core.py:291-308`, example at `:304`). `theme_custom` takes a dict of element parameters (`core.py:311-324`). No facet or font argument exists as a named theme.
- **Export (V):** `effective_run.yaml` (`export_handlers.py:1453-1474`) has no theme field. The theme is visible only through the recipe text, which the bundle carries through its file-set hash (not checked whether the recipe file is in the bundle).

### 7. What is DECIDED (ledger and ADR)

| Tag | Where | Her words or the record |
|---|---|---|
| **DECIDED** | D-0029 (`decision_ledger.md:58`) | `data_engine`/`plot_engine` required. Engine words not quoted. |
| **DECIDED** | D-0033 (`:62`) | DEC01-12, "unknown keys fail, no compat default", engines required. |
| **DECIDED** | D-0036 (`:65`) | "`polars_` action is exactly Polars; no hidden choice; … no silent no-op" (Eve, 2026-11-13). |
| **DECIDED** | D-0051 (`:80`) | "V1-10 ok": "factory refuses an engine it lacks" (2026-11-15). Partly replaced by D-0091. |
| **DECIDED** | D-0054 (`:83`) | "Every engine operator must be usable from the screens" (2026-11-15). |
| **DECIDED** | D-0091 (`:120`) | Plotnine names `plotnine_<name>`, `modif_<name>`, `step_<name>`; "that is the price of transparency and reproducibility". Rename not built. |
| **DECIDED** | D-0210 to D-0214 (`:239-243`, 2026-11-17) | Rename the 22 own components to real plotnine names; remove shortcuts that an exact component does (D-0211, "yes; only functional modifications that are important could eventually be kept"); full parity (D-0212); both spellings (D-0213). **D-0214:** "the `theme:` key of a plot spec and of `plot_defaults` changes, because it is a component call." |
| **DECIDED** | ADR-100 point 1 (`architecture_decisions.md:5197`) | "an unknown engine fails". |
| **CONFIRM** | ADR-106 V8 (`:5363`) | Status line `:5348` says "BUILT: V5 only"; code has V8 (`viz_factory.py:113-126`). Stale. |
| **OPEN** | the 2026-11-17 words (`MUST choose`, place holders, dead keys removed) | Not in any ledger line. Rule B needs a line. |
| **OPEN** | a plot-level engine override | Only agent text: `.claude/design/home_observations_and_future.md:37-38` (not Eve's words). |
| **OPEN** | the theme order | `.claude/tasks/tasks.md:365` "Kept out (need Eve's yes): … the theme order". |
| **OPEN** | a second engine (R, ggplot2) | No ledger line mentions R, ggplot2 or a second engine (S, grep). |
| **OPEN** | `modif_` / `step_` naming with an engine | `D-0036`'s prefix question (S, developer and architect viewpoints). |

### Not checked
- The checker's plot-entry key list and the call site of `engines()` (`recipe_check.py`).
- The full rest of the gallery and template theme settings (S only).
- `audited_frame`'s return type; `checked_plot.py:200`; `gallery_examples.py` and `golden_baseline.py` contents.
- Whether the recipe file is inside the export bundle.
- Whether the Blueprint writer emits the four keys when unchanged (`blueprint_handlers.py:1896-1899`).
- Ledger lines omitted by tool output (`:24, 62, 65-66, 68, 80, 120, 125, 140, 168, 179, 205, 233-240`); D-0033, D-0036 and D-0051 were read directly.
- Nothing was run. No tests were executed. `tmp.md` was not read.
- Everything marked S comes from `tmpAI/panel/engines/scout_what_exists.md` and the two viewpoint files. I did not re-verify it beyond what is marked V.
Survey complete (read-only, 2026-11-17). Full report is in the content above; key points for the plan:

1. Engine keys. `plot_engine` is only checked (libs/viz_factory/src/viz_factory/viz_factory.py:113-126, called at :192) and handed on (app/handlers/home_theater.py:466, 571; app/modules/wrangle_studio.py:691). `data_engine` has no reader outside the checker, writers and tests (libs/utils/src/utils/recipe_factory.py:163; recipe_migration.py:42; test_lab bootstrapper.py:169). Nothing selects a library by either key. Confirmed.

2. Draw sites: home_theater.py:522 and :594; export_handlers.py:1172; wrangle_studio.py:707; gallery_examples.py:119; golden_baseline.py:117. All call VizFactory.render, which returns a CheckedPlot (checked_plot.py:286). Tiers: orchestrator.py:169 materialize_tier1 and :324 materialize_tier2 return pl.LazyFrame; T2 file is <name>__T2.parquet (orchestrator.py:26-29). Dispatcher seam: viz_factory.py:175-192.

3. Refusals: engines.py:33-34; recipe_check.py:221 ("is not a built <key>"); viz_factory.py:125; a plot-entry engine key is refused at viz_factory.py:218-225 ("is not a key of a plot spec"). A plot_defaults engine key is only a warning (viz_factory.py:272-280).

4. Cache: cache_keys.py:51 and :80-85 put both engine keys into tier1 material, so changing either changes tier1_key, every tier2_key and the file-set hash. engine_fingerprint (:70-72) has no engine name. Plot entries are excluded (:51), so a per-plot override changes no key today. Contradicts recipe_format_spec.md:226-227 ("fingerprint later").

5. Dead keys: default_font_family, facet_panel_spacing, legend_position, optimisation are accepted (plot_config_resolver.py:67-70, stored at :583-585), listed in recipe_spec.yaml:43, and documented. Only Blueprint reads or writes them (blueprint_handlers.py:1812-1899). No render effect. optimisation.auto_axis_text is read nowhere. Set in shipped recipes: pipelines/1_test_data_ST22_dummy.yaml:412, pipelines/2_test_data_ST22_dummy.yaml:72, pipelines/stress_test_master.yaml:29, app/tests/equality/recipes/*.yaml:67.

6. Themes: 17 registered (themes/core.py:43-311). plot_defaults.theme and spec theme are strings with empty params (resolver:579-582, :644-647). A theme with arguments can be written today through layers (spec or plot_defaults), e.g. theme_legend_position position, theme_custom dict. Export records no theme field (export_handlers.py:1453-1474).

7. Decisions: DECIDED D-0029, D-0033, D-0036, D-0051, D-0054, D-0091, D-0210 to D-0214 (D-0214 says the theme key changes because it is a component call). OPEN: a per-plot engine override, the theme order (tasks.md:365), a second engine, and today's 2026-11-17 words (not in the ledger yet).

Brief had no Decisions block; decisions were taken from the ledger directly. Not checked: checker plot-entry key list, the engines() call site, audited_frame return type, export bundle contents, Blueprint writer output for unchanged keys, and nothing was run. Items from the earlier survey are marked S (not re-read).
