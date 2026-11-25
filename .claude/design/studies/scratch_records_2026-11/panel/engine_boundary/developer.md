# Engine boundary: developer viewpoint (2026-11-21)

Weight: question 7 (her time question), then 2 and 6. Questions 1, 3, 4, 5, 8 only where the build depends on them.
Labels: RUN (I ran a command), READ (file:line), REASONED. Where I am not sure I say so.
I built nothing. Scratch: `tmpAI/panel/engine_boundary/developer_scratch/` (empty; I wrote no scratch file).

## 0. Summary for the owner (8 lines)
1. Nothing in this study changes a result silently. The first stage is marks and a test only. Every later stage that moves code must pass the golden baseline (`assets/scripts/golden_baseline.py`) with identical results, or it does not merge.
2. One risk to name: moving filter, missing-value and type code (stage 5) is the only stage that could change a result by accident (what a "missing" is). It is also the stage with the most to gain from a test written first.
3. Recommended boundary (developer view): each engine provides a small fixed set of services through its entry file; the app and the neutral libraries call only those. The neutral table handle (V3) is a later, separate decision.
4. Half of this already exists: one registry (`engine_registry.py`), one table of engines, `action_names.py` (21 files already read action names from one place), `READINGS` in `step_effects.py` as one list. So the rewrite is smaller than the 60-file Polars count suggests.
5. Time, honest: marks plus the guard test: 2 sessions, 0 behaviour change, safe before the demo. Everything else: about 18 more sessions (range 14 to 22), in 7 stages, none needed for the demo.
6. Before the demo: stage 0 (marks and the test) only. After the demo: stages 1 to 7, in the order given in section 7.
7. What waits for what: the join warning, the uncertain drop and the audit dialog can go on now if their engine-specific facts go through one named place (section 7.5). Nothing in flight needs a stop.
8. Deciding fast costs nothing if stage 0 is all that is done; waiting costs more work per line written (her point 3), but only the lines that spell Polars; the count is in section 7.6.

## 1. Facts I counted (RUN, today, `dev` at c568cada)
| What | Command (short) | Result |
|---|---|---|
| Source files that import Polars (no tests, no build dir) | `grep -rlE "^\s*(import polars\|from polars)" --include=*.py app libs assets/scripts` minus tests | 60 including assets/scripts; by directory: utils 12, transformer 12, ingestion 3, test_lab 6, id_reconciliation 2, viz_gallery 2, viz_factory 1, app/modules 8, app/handlers 4, app/src 1 (FACTS says 54; my count differs because it includes scripts and files with `from polars`; not important) |
| Test files that import Polars | same, tests only | 176 (of 429 test files). Tests are NOT a problem for stage 0; for stages 3 and 5 the tests that spell Polars stay valid, because the engine stays Polars |
| `pl.` uses in source | `grep -rE "\bpl\.[A-Za-z_]+"` | 441 |
| `LazyFrame` mentions | `grep -rn LazyFrame` | 147 in 29 files |
| `PolarsError` / `pl.exceptions` | grep | 22 mentions, files: `app/modules/build_failure.py`, `orchestrator.py`, `t3_audit_engine.py`, `data_analysis_recipe_validator.py`, `app/handlers/blueprint_handlers.py`, and 5 in `libs/transformer` (which is allowed) |
| plotnine importers | grep | 10 files, all in `libs/viz_factory` |
| plotnine or matplotlib users in app | grep | 9 files: `plot_defaults_form.py`, `engine_registry.py`, `data_analysis_recipe_validator.py`, `gallery_examples.py`, `opening_build.py`, `wrangle_studio.py`, `server.py`, `export_handlers.py`, `home_theater.py` (not all import it; some only mention it) |
| Action names spelled as strings outside the transformer registry | grep `"(polars\|modif\|step)_..."` | `step_migration.py` 62, `action_names.py` 28, `data_assembler.py` 3, `lineage_records.py` 2, `data_wrangler.py` 2, 3 others with 1. So the "one place" rule already holds. READ `libs/utils/src/utils/action_names.py:1-14`: a test in `libs/transformer` fails when a name is spelled outside |
| Files that consume `action_names` | grep | 21 |
| Lineage files and who calls them | grep | callers of `step_effects`, `lineage_walk`, `join_keys`, `key_drop`, `remove_from_all`: 13 source files (`session_handlers.py`, `session_manager.py`, `filter_and_audit_handlers.py`, `data_assembler.py`, `audit_copy.py`, `declared_plans.py`, `recipe_graph.py`, `recipe_check.py`, `join_designer.py` and the five themselves); 29 test files |
| Polars action-name or `modif_` literals inside the 5 lineage files | grep | `join_keys.py` 4, `step_effects.py` 7, `key_drop.py` 1, `remove_from_all.py` 2, `lineage_walk.py` 0 |
| Texts that name Polars or plotnine inside quoted strings in source | `grep -E "\"[^\"]*(Polars\|plotnine)"` | 730 lines in app/libs including docstrings and test-like strings (rough; FACTS gives 104 + 62 + 41 user-facing lines; I trust FACTS for the user-facing count) |
| Size of the hard files | `wc -l` | `lineage_walk.py` 795, `filter_values.py` 418, `formula_check.py` 871, `recipe_check.py` 1323, `missing_values.py` 150, `join_keys.py` 320, `step_effects.py` 242, `orchestrator.py` 820, `t3_audit_engine.py` 881, `viz_factory.py` 541 |
| `libs/utils` files importing Polars | grep | exactly 6: `hashing.py`, `formula_check.py`, `polars_types.py`, `filter_values.py`, `recipe_check.py`, `missing_values.py` |

Observation (READ, `step_effects.py:1-30`): the lineage walk's own file says "Pure: step dictionaries and plans in, small records out. No Polars, no file, no engine." So the walk is already neutral in IMPORTS. What is Polars in it is DATA: the action names it reads, the argument names, and the join kinds it follows. That is a smaller job than moving code: it is to declare that data as the engine's.

## 2. The recommended boundary, as the builder needs it
I recommend V2 built stage by stage, with the marks (V1) first as stage 0. V3 (neutral table handle) is not needed to add a SECOND plot engine or an R engine that exchanges Parquet; it is needed only for an in-memory second data engine. I would keep V3 as a separate decision after V2 (reasoned; not sure).

Why not V1 alone: V1 only says where the engine lives. It does not make a new engine possible without editing `recipe_check.py`, `filter_values.py`, `lineage_walk` and `orchestrator`. A mark that stays in place tells her what to rewrite later; it does not remove the rewrite. It IS the right first stage.

The shape: the entry file already exists (`DataEngineEntry` has `wrangler` and `assembler`; `PlotEngineEntry` has `factory` and `applied_theme`; READ `engines.py:80-140`, `engine_registry.py`). V2 means these entries grow fields. Each new field is a service. The app asks `data_entry(...)` and gets the service.

## 3. Question 2: what a new engine adds, and what must change
Assuming V2 is done (stages 1 to 6):
| New engine | Adds | Existing code still to change (honest) |
|---|---|---|
| Second plot engine in Python (for example Altair) | one library `libs/<lib>/`; entry file `engine_python_<name>.py` with ENTRY; one row in `ENGINE_TABLE`; one line in `REGISTRY`; component registry rows with `engine`; texts (plot engine names list); tests of the library; export record service (`applied_theme`, bytes) | `engine_registry.py:118-124` the default seed (OPEN, named in FACTS); `home_theater.py:690-802` placeholder figures (drawn by the app with matplotlib; must be a plot-engine service or marked); export bytes at `export_handlers.py:388-451, 1277-1280` today reads a plotnine object (stage 6 fixes it); `plot_config_resolver.py:466-495` pandas dtype checks |
| R backend (`r_backend.md`) | all above, plus a process boundary (Parquet in, picture or table out), an environment (see `rules_runtime_environment.md` section 4 for the tiers; not read by me) | the parts of the app that hold `LazyFrame` for plots (the plot gets a Parquet path instead, which needs a neutral table handle = V3 for plots only); seed and font rules; lineage services must say "unread" for its steps |
| SQL or pandas data engine | library with wrangler and assembler; actions with `engine` field and prefix; filter and NA service; type service; formula grammar service; plan service (`collect_schema` equivalent); stored format service; error translation | `orchestrator.py` (types everything as LazyFrame, catches PolarsError); `t3_audit_engine.py` (casts, drop_nans, filter expressions); `anchor.py` Parquet through Polars; `ingestion` (Polars reader). Without V3 this is the largest remaining rewrite |
| A tier with another engine than its neighbours | nothing new in the registry (D-0240 puts the tier's engine in its cache key; READ `cache_keys.py:36-40`) | the hand-over between tiers: today a LazyFrame passes from tier to tier. A different engine needs a conversion at the tier edge. That needs the stored format as the neutral hand-over (Parquet: already used for anchors). Decision needed: is a tier edge always a Parquet write? (cost and reproducibility: I think yes; REASONED) |

## 4. Question 6: the standing rule and its test (developer view)
How to mark a part (three marks, all small, one source):
1. Module header: add one line in the `@deps` block, `# engine: python-polars` or `# engine: neutral` or `# engine: python-plotnine` or `# engine: mixed (stage N removes it)`. Not sure: `assets/scripts/build_dep_graph.py` and `audit_code_quality` parse the header; I did not run them to see whether an unknown key breaks them. First check, 10 minutes.
2. A list of allowed import places: a data file, `libs/utils/src/utils/engine_boundary.json` (or a Python dict next to `engines.py`): for each engine, the files that may `import polars` / `import plotnine` / `import matplotlib` / `import pandas`. The registry fields already say which actions and components are engine-owned (`ACTION_ENGINES`, `COMPONENT_ENGINES`).
3. The test, in `app/tests/`, with three checks that can fail: (a) every `.py` under `app` and `libs` (not tests, not build) that imports an engine library is in the allowed list or the test fails with the file name; (b) every file in the allowed list has the `# engine:` mark and the mark names the same engine as the list; (c) a file with an `# engine:` mark of Polars that is not in the allowed list fails. Break it once to prove it: add `import polars` to a neutral file and see it fail.

The list on day one has to contain the 60 files that import Polars today (and the 10 plotnine files and the matplotlib places). That is a grandfathered list. It is not a shim only if every `mixed` entry carries the stage that removes it and the test refuses an entry without it, and the list can only shrink (the test fails when a file leaves the true set without leaving the list, and when a new file is added to it without a new decision). This is the place where "no half fix" is at risk: if stage 3 to 5 are never done the list stays. State it to her.

User-facing texts that name an engine (FACTS: 104 + 62 + 41 lines in code, 602 in 38 docs pages): a text may name an engine only if it takes the name from the entry (`engine_versions`, `ENGINE_TABLE`) or sits in a file marked with that engine. The test for texts is a grep for the words "Polars" and "plotnine" in string literals outside the allowed files; today that returns the 207 lines. I would not try to make those 207 lines engine-neutral before the demo. In docs, the 602 lines get an engine tag in the page front matter or a box; after the demo (stage 7).

## 5. Question 7: the stages (the main answer)
Size unit: a session = one agent builder run of about one work package with tests; "sure" is how sure I am of the size. Model/effort tags use the CLAUDE.md section 2 table as I know it (opus/high for logic with risk, sonnet/high for mechanical with tests, sonnet/medium for marks and docs). I did not re-read section 2; the owner or coordinator should check the tag names.

| Stage | What | Files touched | Behaviour change | How tested | Risk to demo | Size (sure?) |
|---|---|---|---|---|---|---|
| 0 | Marks and the guard test (section 4). Plus a one-page `engine_boundary` map: for each of the ten hardest places, owner engine and the stage that moves it. This is exactly her words in D-0455: "recorded as such now" | 60 source files get one header line; 1 new data file; 1 new test; docs 1; header parsers checked (`build_dep_graph.py`) | NO (comments and a test) | the guard test, broken once; the full suite; the dep graph script runs | very low: only comments. The danger is a header parser breaking; check first | 2 sessions, sonnet/medium for the header lines, opus/medium for the test and the map; sure |
| 1 | One translation point for engine errors (D-0260, goal DECIDED, design OPEN). The app catches a neutral `EngineError` carrying the plain message; the Polars library raises it | `transformer` (5 files raise/translate), `orchestrator.py`, `build_failure.py`, `t3_audit_engine.py`, `data_analysis_recipe_validator.py`, `blueprint_handlers.py` (8 to 10 files); the message texts | YES in the risky sense: the message the user reads may change; keep every existing message identical and say where it changes | tests that provoke each Polars error class and compare the text before and after (record the texts first from the current code, adapt tests first) | medium if done before the demo: HOME and Gallery build failures are shown by these code paths | 2 sessions; fairly sure (22 mentions; but how many tests assert the type `PolarsError` I did not count) |
| 2 | Services on the entries, the small ones: `stored_format` (Parquet read/write, `anchor.py`, `hashing.py`), `read_file` (ingestion), `engine_versions` already exists | `anchor.py`, `hashing.py`, `libs/ingestion` (3), `orchestrator.py:31-39`, `export_handlers.py:1258` ; ~8 files | NO if done as a move | golden baseline identical; hash tests (hash value must not change: cache keys) | medium (hashes decide caches; a changed hash silently rebuilds or, worse, reuses) | 2 sessions; medium sure |
| 3 | The lineage as engine data: `READINGS`, `FOLLOWED_JOINS`, the row-step list, the join kinds, "what a step writes" become the data engine's `step_profile`, handed to the walk as an argument; `action_names.py` stays the one place of names | `step_effects.py`, `join_keys.py`, `key_drop.py`, `remove_from_all.py`, `lineage_walk.py`, `recipe_graph.py`, `declared_plans.py`, `plan_book.py`, and their 13 callers; `remove_from_all.py:333` writes `modif_filter`: must ask the engine for "the filter step"; 29 test files read these | NO (same data, different place) | the 29 lineage test files stay green; add a test with a FAKE second profile (another action name set) to prove the walk takes the profile and nothing else (this is the test that proves neutrality) | high if done before the demo: lineage work is in flight and the demo is HOME | 3 sessions; medium sure (the arguments of every lineage function change, callers 13) |
| 4 | Plan of columns: `plan_composer.py` (`collect_schema()`) and `plan_book.py` get the engine's plan service; types (`polars_types.py`) as the engine's type vocabulary | `plan_composer.py`, `plan_book.py`, `polars_types.py`, `recipe_check.py` (type check), `ingestion/declared.py`; ~6 files | NO | golden baseline; checker tests | medium | 2 sessions; medium sure |
| 5 | Filters, missing values, formulas: `filter_values.py` (418), `missing_values.py` (150), `formula_check.py` (871) become services of the data engine; `recipe_check.py` asks them; app HOME filters and the T3 translator call the service | those 3 files plus `recipe_check.py` (1323, Polars row-order rule at `:649-672, 944`), `t3_audit_engine.py` (881), `t3_translator.py`, `home` filter handlers; libraries may not import each other, so utils cannot import transformer: the checker must receive the service as an argument from the app (`engine_tables()` already does this for the action table) | NO if moved; this is where a silent change is possible (what counts as missing: D-0042, ADR-103) | tests FIRST: freeze what each filter returns for every NA case (D-0042 "every filter states `na`") on a table with nulls and NaN, for all operators; golden baseline; mutation check (flip one NA rule, see a test fail) | high; do after the demo | 4 to 5 sessions; NOT sure (formula_check is the largest file; the plotnine function grammar at `checked_plot.py:43-49` is on the plot side and is stage 6) |
| 6 | Plot side: `VizFactory.render` takes a table handle instead of a Polars frame converted to pandas inside; the picture as bytes service (`to_bytes`) so `export_handlers.py` stops reading a plotnine object; placeholder pictures of `home_theater.py:690-802` become a plot-engine service; seeds and fonts per engine; `plot_config_resolver.py:466-495` pandas checks move | `viz_factory.py`, `engine_registry.py`, `export_handlers.py`, `home_theater.py`, `plot_config_resolver.py`, `random_layers.py`, `plot_text_check.py`, `signature_params.py`, `checked_plot.py`; ~9 files | NO if the picture stays identical | picture tests and the golden pictures (`golden_baseline.py`, `recipe_pictures.py`); byte-identical SVG/PNG where possible; font check | high (the picture is the demo) | 3 sessions; medium sure |
| 7 | Texts and docs: engine names in user-facing lines come from the entry; the 602 doc lines get an engine tag; docs say what is engine-specific | 207 code lines (ca. 40 files), 38 doc pages | texts change (wording) | the text grep test of section 4; docs build | low risk, big count | 2 sessions mechanical; sure |
| V3 (optional) | Neutral table handle: the app never holds a LazyFrame | 29 files with LazyFrame, 441 `pl.` sites | YES in many small ways (laziness, collect points) | everything | very high | large; 8 or more sessions; NOT sure. Separate decision, not part of the above |

Totals: stages 0 to 7 without V3: 2 + 2 + 2 + 3 + 2 + 4.5 + 3 + 2 = about 20 sessions; about 18 after stage 0 (range 14 to 22; not sure within a third).

### 5.1 Order and what can run in parallel
Risky logic first, screen last, tests adapted to the design first:
1. Stage 0 (before demo). Then, after the demo:
2. Stage 1 (errors). Needs the message texts frozen first.
3. Stage 2 and stage 3 in parallel (own files, own worktrees; they share only `orchestrator.py` lines 31-39 for stage 2 and none for stage 3; check conflicts on `recipe_graph.py`/`declared_plans.py`).
4. Stage 4, then stage 5 (stage 5 needs the type service of stage 4, REASONED). Stage 5: freeze-tests first, alone, one builder.
5. Stage 6 can run in parallel with stages 3 to 5 (plot side is its own library plus 3 app files; shares `export_handlers.py` with nothing in 3 to 5). Opus/high for the render and export contract, sonnet/high for the seed/font moves.
6. Stage 7 last; sonnet/medium; parallel within itself (code texts vs docs).
7. A review step per stage: reviewer (opus/high) checks every decision of the block with line numbers, as `decision_compliance.md` rule E3 asks; golden baseline must be run by the reviewer, not trusted from the builder.

### 5.2 Which stages fit BEFORE the demo without risk
- Stage 0 only. It changes no runtime line. The cost is a header line in 60 files (merge conflicts with work in flight: the lineage files in utils get a header line change; conflict risk is small but real, so do it in one merge when the in-flight branches are merged).
- Stage 1 could fit if she wants the plain Polars error message before the demo (D-0260 is a goal). I would not: the build-failure texts of HOME are what the demo may show.
- Everything else after. None of stages 1 to 7 is needed to show `1_test_data_ST22_dummy`.

### 5.3 What of the work in flight waits, what goes on
| Work in flight | Waits for | Goes on now if |
|---|---|---|
| Lineage walk (`step_effects.py`, `lineage_walk.py`, `join_keys.py`, `key_drop.py`, `remove_from_all.py`) | stage 3 for any change that adds a NEW action name or join kind to `READINGS`/`FOLLOWED_JOINS` (that data moves) | the change only uses `action_names` and `READINGS`, the places that already exist, and the file header says `# engine: python-polars` for the data |
| Join warning (D-0452 to D-0454) | stage 3 only for where the "followed join kinds" list is (the sentence names "anti, right, full or self-join": Polars words) | it reads `FOLLOWED_JOINS` and does not add a second list. The warning sentence is app text: keep the join kinds in the sentence from the list, not typed, so stage 3 does not need to edit the text |
| Uncertain drop (`key_drop.py`) | nothing | the neutral logic (a drop of a key the walk cannot follow) is engine-neutral; mark `columns` of `polars_drop` as the Polars reading |
| Tables no plot reads | nothing | certainly neutral (a graph question over the recipe); `recipe_graph.py` already reads the engine action names; it should call `action_names` only |
| Audit dialog (not built) | stage 3 for step writing (`modif_filter` written by `remove_from_all.py:333`, `t3_translator.py:74-75, 117-118, 143`) | the dialog is UI and is neutral; the step it writes goes through ONE function that names the engine's filter step; build that function now (small), the move later |
| Names pass | nothing (names live in `action_names.py` and the registry) | go on; a name change is one place and a test that nothing is spelled outside |
| Deployment specification | nothing | neutral |
| Plot rename `plotnine_` prefix (D-0254, "not built") | stage 6 is easier after it, not blocked | do before or with stage 6 |

Rule for the builders in flight, one sentence: "Any new line that names a Polars action, a Polars dtype or a join kind sits in a file marked `# engine: python-polars`, or reads the name from `action_names` / `READINGS` / `ENGINE_TABLE`." That costs a builder nothing, and it makes every new line either neutral or listed.

### 5.4 What is lost by deciding fast and by waiting
| | Lost |
|---|---|
| Deciding fast (the boundary shape now) | If V2 is chosen and V3 later turns out to be needed, the services of stage 5 and 6 get a second pass for the table handle. Small. If she decides V1 only, the rewrite is paid later in one block |
| Waiting | Each new line that spells Polars outside a marked place adds to stage 3 to 5. The in-flight lineage and audit work is the main source (it is Polars action names and join kinds): the join warning, the uncertain drop and the dialog all add readings. Stage 0 makes this visible at once at nearly no cost, which is why I would do it now regardless of the larger decision |
| Not doing stage 0 | the 60-file list is not drawn, so nobody can say "what is engine-specific": her point 1 stays unanswered |

### 5.5 Is "rewrite" the right word
For stages 0 to 4 and 6: it is a move of existing code behind a service, with identical results. For stage 5: it is the only one that is a genuine rewrite risk, and I would first write the tests that freeze today's behaviour. I would not call any of it a rewrite of the app; the lineage walk, the HOME code and the recipe format stay.

## 6. Question 6 continued: what I would NOT do
- No `if engine == "python-polars"` branch anywhere in neutral code (a branch is a shim, and it spreads). The service is asked from the entry or it is not asked.
- No allow-list entry without a stage number.
- No table-handle type alias (`TableHandle = pl.LazyFrame`) as "neutral": that is a half fix, it renames and changes nothing.

## 7. The table asked for
| point | DECIDED / CONFIRM / OPEN | proposal | reconsiders a decision? (information) |
|---|---|---|---|
| Engines chosen by the code from the recipe, no fallback | DECIDED | keep | none |
| One entry file per library, libraries do not import each other | DECIDED | services are fields of ENTRY; utils receives them as arguments | none; extends D-0247 |
| Mark every engine place now (her words) | DECIDED (D-0455 order of the study) | stage 0 | none |
| Allowed-imports test | OPEN | section 4 | none |
| Allow-list of grandfathered files with a removal stage | OPEN | yes, only with the stage per entry | none |
| Engine error in one place (goal DECIDED, design OPEN) | OPEN | stage 1: one `EngineError` | refines D-0260 |
| Lineage data (readings, followed joins) as the data engine's profile | OPEN | stage 3 | touches D-0351 (the closed list stays closed, only its home moves), D-0356 |
| Filters and NA as an engine service | OPEN | stage 5, tests first | touches D-0042, ADR-103 information only: rule "missing follows Polars" is then the Polars engine's rule; a second engine would need its own statement |
| Seed per plot engine (`engine_registry.py:118-124`) | OPEN | with stage 6 | D-0056 vs ADR-090/106 (the contradiction FACTS names) |
| V3 neutral table handle | OPEN | separate decision, after V2 | none |
| Tier-edge hand-over as Parquet | OPEN | proposal | none |
| Texts naming an engine | OPEN | stage 7 | none |

## 8. To decide first (ranked)
1. Before the demo do stage 0 only (marks, list, guard test, map): yes or no. Options: (a) stage 0 only; (b) stage 0 and the one-sentence rule for the builders in flight (my reading is that this is part of (a)); (c) nothing before the demo.
2. The boundary: V1 only, V2 stage by stage (my recommendation), or V2 with V3 later. A consequence she must read: V1 alone leaves the rewrite for the day a second engine comes.
3. The grandfathered list: allowed only with a removal stage per entry? Alternative is a permanent list (then it is not a boundary, only a map).
4. Lineage data (stage 3) as the data engine's declared profile: it touches the D-0351 closed list (the list stays closed, its home changes).
5. Filters and missing values as an engine service (stage 5): who states what a missing value means for another engine (D-0042, ADR-103).
6. Errors in one place (D-0260): the wording of every message stays or may change.

## 9. Not verified
- I did not run the test suite or the golden baseline; "identical results" is a requirement for each stage, not a result.
- I did not check whether `build_dep_graph.py` or the code-quality audit accept a new header key (`# engine:`).
- I did not read the model/effort table (CLAUDE.md section 2); the tags are from memory of the normal pattern and should be checked.
- I did not read `r_backend.md`, ADR-010/089/090/100/103/106 or the ledger lines beyond D-0452 to D-0456 in full; the R row of section 3 is REASONED.
- Session sizes are my estimate; the range for stage 5 and V3 is wide on purpose.
- The count of 60 Polars importers includes `assets/scripts`; FACTS' 54 may count differently.
