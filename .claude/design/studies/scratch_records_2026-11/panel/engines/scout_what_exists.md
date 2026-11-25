Read-only survey of SPARMVET_VIZ (branch dev, 2026-11-17). Nothing changed; tmp.md not read. Paths are under /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/ (abbreviated below). [V] = read or searched at file:line; [R] = reasoned from code read. Tags: DECIDED (ledger line by EVE), RECORDED (spec/ADR/rule, no ledger line), BUILT (code), OPEN.

1. ENGINE KEYS
- Spec .claude/design/recipe_format_spec.md:27-28 (example top), :91 DEC04 spec_version required, :92 DEC05 "data_engine (python-polars) and plot_engine (python-plotnine) are required | the engines are part of what a recipe means | 2026-11-13", :226-227 table "python-polars (the only value built) | checker now; fingerprint and export later" (same for plot_engine, python-plotnine). RECORDED; ledger D-0029 (decision_ledger.md:58) and D-0033 (:62) DECIDED, EVE (engine words not quoted in D-0029).
- Allowed values: one each. libs/utils/src/utils/engines.py:21-25; engine_problem :28-34. BUILT.
- Position: top level only. libs/utils/src/utils/recipe_spec.yaml:10 (required list); recipe_check.py:218-221 (T06 on raw top-level dict). Plot spec with engine key is refused as unknown key (libs/viz_factory/src/viz_factory/viz_factory.py:218-225; plot_config_resolver.py:74-77 has no engine key) [R].
- Readers: data_engine -> checker and writers only (recipe_factory.py:163, recipe_migration.py:42, test_lab bootstrapper.py:169, scaffolder.py:209, viz_gallery example_recipe.py:136); no reader in libs/transformer/src or app/modules [V grep]; so Polars is not switched by the key [R]. plot_engine -> viz_factory.py:113-126 refusal (V8), called at :192; app passes key into render dict at app/handlers/home_theater.py:466, 571 and app/modules/wrangle_studio.py:691 (only if present). BUILT.
- Cache: app/modules/cache_keys.py:70-72 engine_fingerprint = cache version + polars + transformer (no plotnine, no engine key). cache_keys.py:51 _DOWNSTREAM_TOP_LEVEL does not list data_engine/plot_engine/spec_version, and :80-85 tier1_material keeps all other top-level keys: so both keys are in Tier 1 material [R]. Differs from spec "fingerprint later".
- Export: app/handlers/export_handlers.py has no data_engine/plot_engine field [V grep]. data_analysis_recipe_sha256 (:197) = hash of file set (cache_keys.py:22-24) [R: covers key text]. plotnine version recorded: export_handlers.py:104 and software_versions :203 [V]. Export line for plot_engine: OPEN (.claude/tasks/tasks.md:365), not built.
- Shipped: config/data_analysis_recipes 16 recipes (5 templates, 7 pipelines, 4 retest), 32 lines; assets/gallery_data 34 recipes, 68 lines; all values python-polars / python-plotnine [V]. Test-only refusals of python-ggplot2: libs/utils/tests/test_engines.py:31, libs/viz_factory/tests/test_plot_engine.py:47, test_one_error_form.py:78.

2. DEFAULT THEME, plot_defaults
- Built-in default theme: theme_bw (plot_config_resolver.py:47 and :63; viz_factory.py:135). BUILT.
- Allowed keys differ across three places: rule .claude/rules/rules_data_analysis_recipe_structure.md:222-241 (palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation{auto_axis_text, density_jitter, panel_spacing, legend_ncol}); code plot_config_resolver.py:67-70 (adds layers, random_state); checker recipe_spec.yaml:43 (same as code). RECORDED.
- Plot override: spec palette beats plot_defaults.palette (resolver:617-620); spec theme beats default (resolver:644-647). BUILT; rules 10b/10c.
- Cascade .claude/design/plot_config_cascade.md line 3 "DESIGN — accepted 2026-05-10". Tiers built: L1 yes (resolver:563-569); L2 palette, theme, layers, random_state yes (:572-587; viz_factory.py:106-108); L2 default_font_family, facet_panel_spacing, legend_position, optimisation stored but no reader in libs/ [V grep] -> no effect [R]; L3 axis text only (:431-438); L4 yes (:594-660); L5 fill_palette, fill_color, theme, random_state yes (:675-710); L5 color/alpha/shape/size stored in _l5_geom_overrides (:695-702) with no reader outside resolver and tests [V grep] -> not applied [R]. L5 is wired from home_theater.py:503-522 and export_handlers.py:1168-1170.
- Shipped recipes with plot_defaults: config/data_analysis_recipes/templates/e_coli.yaml:95 (theme_minimal); templates/audit.yaml:42 (theme_minimal); pipelines/1_test_data_ST22_dummy.yaml:410 (theme_minimal, default_font_family); pipelines/2_test_data_ST22_dummy.yaml:71 (font); pipelines/stress_test_master.yaml:28 (font); app/tests/equality/recipes/2_test_data_ST22_dummy_{dirty,dirty_no_null_text,emptied,fractional_year}.yaml:66 (font). Gallery: none. No shipped recipe sets palette or random_state in plot_defaults [V].

3. EXISTING OVERRIDE PATTERNS (other than plot_defaults)
- Plot spec palette over plot_defaults palette (resolver:617-620). RECORDED (rules 10b).
- Plot spec theme over default (resolver:644-647). RECORDED (rules 10c).
- Layer random_state over recipe seed over factory seed (plot_config_resolver.py:263-285; viz_factory.py:77, 80; rules_viz_factory.md:120-121). RECORDED.
- VizFactory(random_state) default 0 (viz_factory.py:37, :163). RECORDED.
- T3 aesthetic_override per plot, L5 (resolver:664-710; app/modules/plot_seeds.py:40-68). BUILT in part.
- Deployment palette registry overrides built-in palette names on clash (viz_factory.py:166-168). RECORDED in docstring.
- Deployment data_lookup by_dataset_id ignores recipe source path (app/modules/orchestrator.py:77, :86). BUILT.
- Seed fixed in recipe holds: DECIDED D-0052 (decision_ledger.md:81).
- Not overrides, no default: null_values and strip (D-0035, :64); filter na (D-0042, :71).

4. DECISIONS, RECORDS, R/ggplot2/second engine/dplyr
- Ledger: no line mentions R, R backend, ggplot, ggplot2, rpy2, dplyr or second engine [V grep, zero hits]. Engine lines: D-0036 (:65, DECIDED, EVE, polars_/modif_/step_ prefixes, scan/sink engine-only); D-0051 (:80, DECIDED, EVE, "factory refuses an engine it lacks", "V1-10 ok"); D-0054 (:83); D-0091 (:120, DECIDED, EVE, plotnine_<name> prefix, "Same as we had done with polars" #1065; "The rename is not built"); D-0056 (:85, DECIDED, "Fixed 0 by default fixed and simple").
- Asked, not decided A03 (decision_ledger.md:244): recipe built from Python turned back into clean Python; her words "a research and proposal NOT a decision". OPEN. No research file found.
- ADR-100 architecture_decisions.md:5187-5227 (point 1 :5197 engines required, unknown engine fails; point 6 :5202 prefixes; point 7 :5204 Polars action only). RECORDED.
- ADR-106 V8 (:5363) "The factory refuses a plot engine it does not implement; the export records the plotnine version." Status :5348 "DECIDED ... 2026-11-14 ... BUILT: V5 only". Note :5370 V1-B plotnine_ prefix "Not built". RECORDED; V8 BUILT (viz_factory.py:113-126).
- ADR-071 (:2254-2261) "DECIDED + PARTIALLY IMPLEMENTED"; air-gap principle (:2260). RECORDED.
- No ADR on R or second engine [V grep]. Earliest: architecture_decisions.md:82-83 Plotnine primary engine for the Prototype.
- tasks.md:63 V1 and V8 merged (4525fcb1). tasks.md:365 VIZ-NIGHT-QUEUE, DECIDED 2026-11-15 (M97), export lines for plot_engine: OPEN. No R task.
- .claude/design/feature_extension/ files (status line 3; three findings):
  - r_backend.md: EXPLORATORY, nothing decided. (a) spec is ggplot2 grammar, second backend = transpiler (:18-28); (b) avoid rpy2, lean subprocess Rscript + Arrow (:49-55); (c) options A narrow R renderer, B full backend, C ggplot2 snippet escape hatch (:61-83); R choice gates Sankey/custom geoms (:87-96).
  - bioinformatics_viz.md: EXPLORATORY. (a) ggtree has no Python equal (:14); (b) input is a tree object (:34); (c) geom_fruit; plotnine rebuild "Not advisable" (:91).
  - sankey_flow_geoms.md: PROPOSAL, Sankey deferred. (a) leaning to real plotnine geoms if plotnine path taken (:7); (b) depends on R-backend question (:7); (c) ggalluvial is spec not source (:40-49).
  - composite_dashboard_home2.md: EXPLORATORY. (a) R ggtree opt-in backend (:28, :115, :158); (b) static vs interactive cannot share artifact (:175-180); (c) depends on survey (:210).
  - dashboard_frontend_topology.md: EXPLORATORY. (a) R backend and ggtree static panels usable in either frontend (:124); (b) lean Shiny for Python (:97); (c) "render backends: plotnine / R / geom_polygon" row (:78).
  - Maps (outside folder): .claude/design/maps_advanced_geo.md, "PROPOSAL — not scheduled" (:3). (a) Solution A choropleths geom_polygon, no new deps (:31, :188); (b) Solution B projections, B1 sidecar (:167, :173); (c) geom_map commented out at libs/viz_factory/src/viz_factory/geoms/core.py:822, keep it so (:190). r_backend.md:89 says sf maps come free with R.
- Closest record to per-plot engine question: .claude/design/home_observations_and_future.md:37-38 (agent text 2026-11-12, not Eve's words): "Another plot engine (for example r-ggplot2, r-ggtree) ... the declaration (plot_engine), overridable per plot entry later". Section 5 (:46-60) engine registry sketch, not built. OPEN.

5. DATA AT THE BOUNDARY
- Parquet: libs/transformer/src/transformer/anchor.py write_anchor :88-138 (frame.write_parquet :121; lf.sink_parquet :124); read_anchor :157-161 (pl.scan_parquet); read_anchor_if_key :76 [V]. Orchestrator: Tier 1 write app/modules/orchestrator.py:282, 318; Tier 2 path :26-29 (<name>__T2.parquet), write :393; reads :219, :356 [V]. scan/sink are engine functions (DEC42, recipe_format_spec.md:148).
- Plot receives: viz_factory.py:206-207 pl.DataFrame to lazy; :209-259 Polars filters; :262 df.collect().to_pandas(); :266 resolve_plot_config on pandas; plotnine draws [V]. Caller passes LazyFrame: home_theater.py:522 [V].
- Types: recipe type is a Polars dtype (D-0035; ADR-100 point 4). Filter values typed by column dtype (viz_factory.py:257-258). Palette choice uses pandas dtype checks (:470). Missing values keep_missing/na_of (:259). No explicit Polars-to-pandas handling of categoricals or dates in viz_factory.py [V grep]; pandas default conversion [R], not checked. Categorical vs String OPEN (ADR-100 :5211).

6. R ON MACHINE AND PROJECT
- rpy2, dplyr, ggplot2, r-base: no hit in any pyproject.toml, Dockerfile, *.yml/*.yaml/*.toml [V grep]. Root pyproject.toml:9 polars>=1.0.0, :14 plotnine>=0.15.4,<0.16.0; libs/viz_factory/pyproject.toml:10-11 [V].
- uv.lock: not found at root or libs/* [V glob].
- .venv/lib/python3.14/site-packages: glob rpy2* and plotnine* empty; polars* returns files under polars/ [V]. Venv listing not reliable.
- R scripts: none (only .venv statsmodels CH.r) [V].
- assets/containers/Dockerfile:32 FROM python:3.12-slim; apt :35-51 (TeX, librsvg, libgl); Quarto after :53. No R installed [V].
- config/deployment/: no R, Rscript, rpy2, ggplot2, dplyr [V grep].

7. NAMING RULE
- polars_ prefix: DEC31 recipe_format_spec.md:137; DEC32 :138; section 7.5.1 heading :409 "[DECIDED, DEC31 to DEC42]"; :703. Ledger D-0036 (decision_ledger.md:65, DECIDED EVE); ADR-100 point 6 (architecture_decisions.md:5202). DECIDED (D-0036), RECORDED (spec, ADR-100).
- Other engine prefix: D-0091 (decision_ledger.md:120) plotnine_<name>; ADR-106 note :5370 "Not built"; impact list .claude/design/viz_rename_impact_2026-11-15.md:19-20. OPEN until impact list seen. Spec has no plotnine_ text [V grep].
- Registry field: spec/ADR-100 name `polars` (DEC31); plot registry uses `plotnine` (libs/viz_factory/src/viz_factory/registry.py:53) [V].

CONTRADICTIONS BETWEEN RECORDS
1. ADR-106 "BUILT: V5 only" (architecture_decisions.md:5348) vs tasks.md:63 "V1 and V8 merged" and code viz_factory.py:113-126. ADR stale.
2. ADR-106 "DECIDED ... 2026-11-14" (:5348) vs D-0051 dated 2026-11-15 (decision_ledger.md:80) and tasks.md:365 "DECIDED 2026-11-15".
3. ADR-106 V1 "no component is renamed" (:5356) vs D-0091 plotnine_ prefix (ledger :120); handled by note :5370, V1 text not edited.
4. DEC05 "fingerprint and export later" (recipe_format_spec.md:226-227) vs both keys already in Tier 1 material (cache_keys.py:51, :80-85) [R].
5. plot_config_cascade.md:35 "Never read by VizFactory.render()" vs home_theater.py:503-522 and resolver:664-710. Cascade doc stale.
6. Rules 10a (rules_data_analysis_recipe_structure.md:222-241, "authoritative") and recipe_spec.yaml:43 accept default_font_family, facet_panel_spacing, legend_position, optimisation, which no code reads [V grep]; shipped recipes set default_font_family. Silent no-effect [R].
7. D-0035 "categorical refused ... replaced in part by D-0057" (decision_ledger.md:64) vs ADR-100 OPEN (architecture_decisions.md:5211).

NOT CHECKED
- uv.lock (not found); .venv beyond three globs; no app or test run.
- Ledger lines omitted by tool output (e.g. 159-171, 181, 213, 228, 275) not all read.
- tmp.md not read (as instructed); .claude/worktrees not checked.
- Polars-to-pandas type conversion: reasoned only, not run.
- plot_seeds.py body and recipe_check.py plot-entry key list not read in full.
- Dockerfile Python 3.12 (Dockerfile:32) vs .venv path 3.14: not checked further.
