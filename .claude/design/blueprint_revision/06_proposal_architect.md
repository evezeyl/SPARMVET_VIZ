<!-- copied unchanged on 2026-11-21 from .claude/design/studies/scratch_records_2026-11/panel/blueprint_step4/architect.md (not in git), written 2026-11-21 night in step 4 of the BLUEPRINT review; a viewpoint's proposal: it recommends, it decides nothing -->
# BLUEPRINT review, step 4: the architect's proposal (how the engines and the lineage can help write a recipe)

Viewpoint: software architect (boundaries, one source of truth, testability, long-term cost, ADRs). One round. It proposes; Eve decides. Tags: DECIDED / CONFIRM / OPEN / MINE. Evidence labels: verified (read at file:line or run), reasoned, assumed.
Scratch checks are in `.claude/design/studies/scratch_records_2026-11/panel/blueprint_step4/` (`arch_check.py`, `ctx_check.py`, `join_check.py`). Nothing in the repository was edited.

## Summary (6 lines)

1. The four approaches (forms, live plan, lineage map, text) are not four systems. They are four screens over the same three seams: one draft, one evaluation of the draft (check, graph, plan), one way to run a step list. Two of the three seams exist in HOME's code; BLUEPRINT uses neither today.
2. BLUEPRINT today has four stores of the recipe being edited, three column sources, three ways to run steps, and two assemblies of the action catalog. Three verified drifts follow (section 1).
3. The facility that gives "columns and types after every step without reading data" exists (`app/modules/plan_composer.py`) but only for a recipe that passes HOME's load gate (verified by run: the loader refuses BLUEPRINT's own new-recipe stub). It must be extended to a draft; this is the main build item.
4. Recommendation: one core (the draft evaluation seam), with the live plan (B) as the data and the lineage map (C) as the frame; forms (A) stay the editing widget; text (D) stays the escape hatch. Not four builds.
5. The point of no return is the Save (overwrite in place, no backup, comments lost). The test that guards it is a round trip, and it needs no browser.
6. The engine "language" must be a field of the entry, and the plan must become part of the engine entry contract (it is Polars-only today at `plan_composer.py:83`). Verified bug to report now: the Joint Designer offers `how = outer`, which the shared step check refuses (ST10).

---

## 0. Facts that the proposals rest on (all verified unless marked)

| # | Fact | Evidence |
|---|---|---|
| F1 | The plan of every place (name and engine type after k steps) is composed from the build's own `*_parts` functions and the lazy frames; no table is built or stored; a failure is a value (`PlanFailure`), never an exception; a standing test compares it with built tables on shipped recipes | `app/modules/plan_composer.py:1-30`, `utils/plan_book.py:1-30` |
| F2 | The composer takes a LOADED recipe (`loaded.raw`, `loaded.is_audit_copy`); the only way in for a changed recipe is `compose_candidate_plan_book`, which is for ONE audit step in an audit copy (`audit_copy.add_step`) | `plan_composer.py:104-118`, `:358-369` |
| F3 | The loader (`ConfigManager`) refuses BLUEPRINT's own empty new-recipe stub with `SystemExit` (no plot: profile `run`). So no plan can be composed for a draft that has no plot yet | run: `tmpAI/panel/blueprint_step4/arch_check.py` |
| F4 | `build_graph(raw)` is pure and takes any dict; BLUEPRINT's navigator already uses it for structure. Its `columns_provider` hook ("a dry run on column names, a stored schema") is passed by no caller | `recipe_graph.py:467`, `:33`; grep: no caller outside tests |
| F5 | Three sources of "which columns exist" that do not share code: (a) `RecipeGraph._flow` (declared fields; understands row steps, select, drop only), (b) `step_effects.READINGS` + `declared_plans` (names only; 7 actions read, the rest `unread`), (c) the engine plan (names and types) | `recipe_graph.py:325-350`, `step_effects.py:56-70`, `declared_plans.py:58-75`, `plan_composer.py:83` |
| F6 | `step_problems(action, spec, schema)` is the ONE judge of one step; the checker and the engine both call it. BLUEPRINT's Apply handler calls neither it nor the checker: Apply parses the inputs per widget inline in the handler and stores the step | `ui_schema.py:216`; `blueprint_handlers.py:1199-1385` (grep: no `step_problems`, no `check_recipe`) |
| F7 | BLUEPRINT's own runner of a step list, `WrangleStudio.apply_logic`, calls the registry function directly with `params` only, ignores the engine choice, skips an unknown action and PRINTS an error for a failed step instead of raising it. The engine's `DataWrangler.run` raises a plain error naming the step | `wrangle_studio.py:2316-2328`; `data_wrangler.py:95-175` |
| F8 | Four stores of "the recipe being edited": the file on disk (the plot preview reloads it from disk, `wrangle_studio.py:672-686`), the in-memory `logic_stack` (steps of ONE open component), the raw YAML text of the hatch, the autosaved draft (`H:126-190`). The glimpse data is a stored anchor built from the saved file (`H:706`) with the in-memory steps applied on top for a wrangling role (`wrangle_studio.py:606-634`) | read |
| F9 | Two assemblies of the same registry: `checker_catalogs()` (one place, with the engine tables, used by HOME, Validate and the gallery) and `server.py:39-42` (injects `ACTION_SCHEMAS` / `COMPONENT_SCHEMAS` into `blueprint_arch.schema_registry`, no engine field). The picker and the forms read the second | `data_analysis_recipe_validator.py:140-161`; `server.py:39-42`; `schema_registry.py:35-57` |
| F10 | A copy that drifted: `join_designer.JOIN_HOW_OPTIONS = [inner, left, outer, semi, anti, cross]`; the action's enum is `[inner, left, right, full, semi, anti, cross]`. The step the Designer builds with `outer` fails the shared step check (ST10). A test pins the stale literal (`test_join_designer.py:266`) | run: `join_check.py` |
| F11 | Which action may stand at which tier is stored twice and agrees today: registry `context` tags (picker) and `action_names.TIER1_ONLY` (checker). No registry context "t3" exists | run: `ctx_check.py` (3 TIER1_ONLY actions, none offered at t2, no other action missing at t2); tests exist for each side, none seen that holds them equal |
| F12 | The plot engine path is already engine-aware (`engine_registry.plot_entry`, `PlotEngines.render`); the data path of BLUEPRINT is not (F7). The plan composer is engine-aware in choosing the entry (`data_entry`) but reads the plan with `lf.collect_schema()`, a Polars API; `DataEngineEntry` has `wrangler` and `assembler` and no plan | `engine_registry.py:35-61`; `plan_composer.py:83`; `utils/engines.py` (`DataEngineEntry`) |
| F13 | The lineage walk (`utils/lineage_walk.py`) is column-centric (for a column, where a step can be written); node-level dependence ("which tables, joins, plots read this node") is `RecipeGraph.lineage_forward`, `plots_reading`, `source_tables` | `recipe_graph.py:195-240` |

What F1 to F13 mean together: "run a step list on real data" and "the plan after each step" exist as ONE code in the build and the plan composer, and BLUEPRINT uses a different code (F7, F8). Any approach that claims "what BLUEPRINT shows is what the engine does" is untrue until BLUEPRINT is moved onto the engine's path.

---

## 1. Common core: the "draft evaluation seam" (all four approaches need it; I build it once)

| Part | What | State | Where it would live |
|---|---|---|---|
| S1 One draft | The recipe being edited is one dict in memory; the file is written only at Save; every view reads the draft | missing (F8) | app layer (reactive value in the BLUEPRINT state object); the pure operations in `blueprint_arch` |
| S2a Check | `check_recipe(draft, "build", catalogs, graph)`: coded problems with paths | exists, pure (`recipe_check.py:1315`); BLUEPRINT calls it on the file with profile `run` | unchanged |
| S2b Graph | `build_graph(draft)` | exists, pure | unchanged |
| S2c Plan | `PlanBook` for the draft: columns and types after every step, a failure as a value | must be extended: a composition for a draft (F2, F3) | one small app module, a sibling of `plan_composer.py`, not a change of the audit's function; BLUEPRINT is a new consumer in its `@deps` |
| S3 Run | A step list on real data through `DataWrangler.run` and `data_entry` (the engine's path) | exists in the build; BLUEPRINT's `apply_logic` replaces it (F7) | app layer calls the engine; no new lib code |
| S4 Catalog | One assembly of actions and components WITH the engine field for picker, forms, checker | partly (F9) | `checker_catalogs()` becomes the source; `blueprint_arch.schema_registry` receives it instead of the raw dicts |
| S5 Form to step | A pure function: widget values in, step dict out, with `step_problems` run before the step is stored | missing as a function (inline in the handler, F6) | `blueprint_arch` (it already holds `widget_text.py`); tested without Shiny |
| S6 Writer | draft to file, lossless for what it holds, comments kept (D-0174), no silent change of an untouched file | missing (`H:1188`, `yaml.dump`) | `utils.recipe_factory` area; needs Eve's yes for a library (D-0174 text) |

Boundary check (Two-Category Law, ADR-011, ADR-099 16(d)): `blueprint_arch` is a lib and cannot import `app/`. So the producer of the plan (S2c) stays in `app/modules` (it reads data files through the orchestrator) and is INJECTED into the handler; `blueprint_arch` only consumes the pure type `utils.plan_book.PlanBook` and offers pure queries over it, for example "columns offered at place N after step k" and "what this step does to the column list". This is the same pattern as the catalog injection that exists (`server.py:39-42`). [MINE]

What it shares with HOME's audit (read only): `plan_composer`'s `*_parts` functions, `PlanBook`, `PlanFailure`, `step_effects.READINGS`, `lineage_walk`, `recipe_graph`. What BLUEPRINT must NOT share: `compose_candidate_plan_book`, `AuditCopy`, `audit_copy.add_step` (they write audit steps; HOME is the only place that writes an audit, D-0143, ADR-099). `refuse_audit_steps_outside_an_audit` already refuses audit steps in a non-audit draft, which matches "BLUEPRINT never authors an audit" (verified, `plan_composer.py:329`).

---

## 2. The approaches

### A. Forms first, check on Apply and on Save (today's design, made honest)

1. What the user sees. New recipe: the "+ New" dialog, then forms for the pieces. A step: pick an action, fill the form, Apply; on Apply the step is judged by `step_problems` and the problems are shown beside the field; on Save the whole draft is judged (profile `build`) and the problems are listed with their path. A join: the Joint Designer. A plot: the mapping and layer forms. Columns offered: the declared fields of the table (today).
2. Engine facility. `step_problems` (exists, pure, one judge, F6), `check_recipe` (exists), the registry `ui_schema` (exists). Missing: S1, S5 (the inline Apply logic must become a function), S4.
3. Pros: smallest change; every piece exists; all of it is testable without a browser once S5 exists. Cons: the user learns about a missing column only when the check runs, because the pickers know only declared fields (F5a); a step that makes a new column is invisible to the next step's picker; the plan is not used, so the "type after this step" is not shown. Pitfalls for the user: Apply says "OK" for a step that the whole recipe will refuse later (a wrong place, a column that does not exist at that tier). What would hide a step: the `apply_logic` swallowing of errors (F7) must go in every approach, otherwise the glimpse silently omits a failed step.
4. Engine selectable. Generic: the check, `step_problems`, the form renderer (built from `ui_schema`). Per engine: the registry entries with their `ui_schema`, the `expression` widget text, the dtype names (F12, `04`/`05` section 5).
5. Decide first: S1 (the single draft) and the profile of the check (`04` choice 3). Can wait: the plan.

### B. Live plan after every step (the engine is the oracle)

1. What the user sees. After each step card: the columns and types at that place, new ones marked, dropped ones marked; a failed step shows the engine's own sentence and everything below it is greyed (this is exactly `PlanFailure`'s contract, F1). Rows on demand: a button "show rows" collects the table at that place (limit applied at the END of the lazy plan, never a sample of the input). A join: both ingredient plans side by side, then the plan after the join (the key check `join_keys.join_key_problem` already shared). A plot: the columns and types of the target table at tier 3, and the picker for the aesthetics offers only those, with the type next to the name (a discrete or continuous reading is the user's choice, shown with the type, D-0036 spirit). Save: `check_recipe` build, plus "the plan reaches the end: yes or the first place where it fails".
2. Engine facility. Plan composer: exists for a loaded recipe (F1); must be extended to a draft (F2, F3: this needs a way to load a recipe WITHOUT the `run` gate; `utils.recipe_loader.load_recipe` reads a dict strictly with no profile, `recipe_loader.py:60`, so the input exists; the `LoadedDataAnalysisRecipe` envelope is what must be made for a draft). Rows: `DataWrangler.run` then `collect` (exists). Unknown today: a plan for a table with no data file (the composer reads the source file, `orchestrator._read_source`; a draft without data cannot be planned, only checked).
3. Pros: one authority for names and types (D-0325, already DECIDED for HOME); no second description of what a step does; exact "what a step did to the types before saving" (the scientist's wish) with no run of the data. Cons: needs the data file present and a recipe that gets to that place; types of a SOURCE table are the declared types, and whether the values fit them is known only when rows are read (`orchestrator.py:243-245`: the ingestion fails there and names the column and values), so the plan can say "int64" for a column that fails at the first read; the plan says nothing about row counts, NA counts or a join that multiplies rows (needs a collect; row multiplication is a data fact, not a plan fact). Pitfalls: a preview of rows on a limit looks like a result; a limit placed before a group-by, join or unique would change the answer, so the limit must be at the end and labelled "first N rows of the result", with the count shown only when really counted. What would change a result silently: a sample of the input; reusing `apply_logic` (F7). What would hide a step: showing the plan of the SAVED file while the user edits the draft (F8): the plan must read the draft or say "of the saved file".
4. Engine selectable. Generic: `Plan`, `PlanFailure`, `PlanBook` (types as text, `plan_book.py:27`), the graph, the display. Per engine: the producer of the plan. Today the producer calls `lf.collect_schema()` (F12). If the plan is not part of `DataEngineEntry`, a second data engine cannot be planned and BLUEPRINT's columns break for its tiers. So: add a `plan` capability to the entry contract [CONFIRM with D-0247 "each library has one small entry file"; D-0325 says "ask the engine for the plan" and does not say how an engine answers].
5. Decide first: S1, S2c scope (a draft that does not run: how far does the plan go: "up to the first failure", as `PlanFailure` already does), the engine contract for the plan. Can wait: rows on demand, caching.

### C. Lineage first (the map is the editor)

1. What the user sees. The tube map shows ALL places of the recipe, including empty tier 1, tier 2, tier 3 slots (the graph already has T1, T2, T3 for every table and plot, `recipe_graph.py:14-21`; the mapper today draws only places that hold a step, `blueprint_mapper.py:41-45`). The user clicks an empty slot to add a step there: the tier and the file are given by the place, not chosen from a context list (this ends the "wrong tier" refusal, D-0308 "see where it sits" and `04` choice 4). A step card shows what depends on it: the joins and plots that read this node (`graph.lineage_forward`, `plots_reading`: exist) and, for a column, where it comes from, where it is renamed, dropped or recomputed (`lineage_walk` with `step_effects`: exists for the 7 actions of `READINGS`; for every other action the walk says `unread` and greys, D-0351). A new recipe: the map starts with the slots a recipe must have; a table enters through its slot.
2. Engine facility. Graph: exists. Walk and plan book: exist for HOME's recipes; same extension as B for a draft. Missing: the mapper drawing empty slots; a "t3" context for the picker (F11); the node granularity of the picker (place gives context).
3. Pros: the structure is what the recipe IS (no second model); the order of building (tier 1, 2, 3, plot) becomes visible; it uses the lineage the owner asked to leverage (D-0309). Cons: for most of the 68 actions the column-level lineage is "cannot follow" (7 read, F5b); a user may read grey as "no problem" if the words are not plain; the walk is built for the question "where can an audit step go", not for "what feeds this step", so the second question must be a new, small query on the same data, not a bending of the walk [reasoned]; a map with every slot of a large recipe is crowded. Pitfalls: a map click that loads another table's data is a known defect (`03` item 17, not rechecked); a lineage drawn from the draft while the stored tables come from the saved file (F8).
4. Engine selectable. Generic: graph and slots (the recipe is engine-neutral at the structure level). Per engine: `step_effects.READINGS` is keyed by `polars_` action names (`action_names`), so the column-level reading is per engine and must be declared by each engine's library, or the walk says `unread` for all of its steps (an honest fallback, not a break) [reasoned].
5. Decide first: S1, where tier 3 and empty slots are drawn (`04` choice 11), whether node-level dependence is enough for a first version.

### D. Text first with assistance (the YAML is the editor)

1. What the user sees. The recipe text (the master file and the included files) in an editor; beside it a panel fed by the checker (problems at the line of their path), the graph (structure) and the plan (columns after the step under the cursor); completion of action names and parameter names from the registry. Save writes the text the user wrote.
2. Engine facility. Same S2, plus a path-to-line mapping from `Problem.path` (the checker reports a path in the recipe, `recipe_check.py:120`; the line is not given) and a strict reader that keeps `!include` and comments (`utils.strict_yaml`; `load_strict` exists). Missing: the editor widget, the completion, the line mapping.
3. Pros: the file is the single store, so S1 and S6 vanish: comments are kept (D-0174 met with no new library), no serialiser can lose a key, and "what is saved is what was typed". Cons: it is not the visual IDE the owner asked for (ORDER: "an ide (visual)"); a beginner writes YAML by hand; indentation errors; `!include` files make "the text" several files. Pitfalls: a text edit that is valid YAML but refused by the strict format shows an error only after the check; a hidden risk: ADR-075 section 7 says the hatch is editable only with `data_analysis_recipe_edit_enabled` (developer, qa).
4. Engine selectable. Generic: everything (the text is engine-neutral; the checker's EN02 marks a step in the wrong block). Per engine: the completion catalog (the registry).
5. Decide first: whether a text editor is the main surface or only the hatch (it reconsiders ADR-075 section 7 and the order's word "visual").

---

## 3. Comparison (architect's columns)

| | A forms + check | B live plan | C lineage first | D text first |
|---|---|---|---|---|
| New seams to build | S1, S4, S5 | A plus S2c, S3, a plan in the engine contract | B plus empty slots, a node-dependence query, a t3 context | S2, a text editor, a path-to-line map |
| New code in libs without Shiny (testable headless) | S5 | queries over a `PlanBook` | queries over graph and plan book | line map, completion |
| Single store | needs S1 | needs S1 | needs S1 | the file (already) |
| Comments kept (D-0174) | needs S6 and Eve's yes | needs S6 | needs S6 | yes, no library |
| Uses HOME's walk and plan | no | plan yes | plan, graph, walk | plan, graph |
| Amends / touches | ADR-082 (agent gating), ADR-100 pt 3 (BLUEPRINT never blocks) | D-0325 (extends it to BLUEPRINT: see section 5), ADR-099 16(i) (the graph knows the columns: realised) | ADR-039, ADR-040, D-0309 | ADR-075 section 7, ORDER ("visual") |
| Long-term cost | low, but BLUEPRINT stays blind to columns | medium; the plan contract per engine | highest (the map is a second UI to maintain) | low for the core, high for the user's learning |
| What an audit or a test would NOT catch | a form that stores a step the checker would refuse in another place | the plan of the draft differing from the build of the saved file (needs the round trip test, section 4) | grey read as "fine" by the user (a words problem) | a text edit that no test types |

---

## 4. Points of no return, checks, tests without a browser

- The point of no return is the Save: it overwrites in place, no backup, loses comments, and changes the key of the stored tables (the file hash is in it; `02` F2, `03` 1.5). Between Save and the user nothing stops a wrong recipe except the checker.
- What checks it: `check_recipe` on the draft (profile: OPEN, `04` choice 3), the plan reaching the end, and HOME's gate re-run after the save (`tell_save_outcome`, exists).
- Tests that need no browser and that can fail [MINE]:
  1. Round trip: `plan(draft) == plan(load(save(draft)))` and `check(draft) == check(load(save(draft)))`, and `save(load(file)) == file` byte for byte for an untouched file (guards D-0174 and the silent change; fails today, `H:1188`).
  2. Parity: the picker's offer at a place equals the set the checker accepts at that place (F11); the picker's enum for `how` equals the action's enum (would fail today: F10).
  3. Plan equals build: exists (`app/tests/test_plan_composer.py`); extend it to a draft built by the new function.
  4. A step stored by the forms always passes `step_problems` (S5 returns problems; the test feeds each of the 68 actions' `ui_schema` defaults).
  5. A failed step in a list is an error value, never a skipped step (replaces `apply_logic`'s print, F7).
- What a test would not catch: how the words read to a beginner (a grey "cannot follow"), the speed of a plan on a big recipe, and what the user does with a preview of N rows.

---

## 5. Fit with the decisions

| Point | Tag | Note |
|---|---|---|
| The plan of the engine is the authority for what exists and its type | DECIDED (D-0325) | The line also says "Blueprint is out of this choice (HOME and GALLERY first; Blueprint's needs go to its later design pass)". So USING the plan in BLUEPRINT is the later design pass the line leaves, not a breach, but it is not yet decided for BLUEPRINT: CONFIRM with Eve. |
| HOME is the only place that writes an audit; BLUEPRINT never does | DECIDED (D-0143, ADR-099) | Kept: BLUEPRINT consumes the plan book read-only and does not call the audit's candidate functions. |
| BLUEPRINT reports and never blocks building | DECIDED (ADR-100 pt 3) | A check on Apply informs; it must not forbid a step. The Save refusal of a wrong tier is PROVISIONAL (D-0308) and goes if C is chosen (the place gives the tier). |
| Engine is a field of the registry entry; no library, refused | DECIDED (D-0238, D-0239) | The picker must read the field (F9); it does not today. |
| The libraries do not import each other; the app joins them | DECIDED (D-0247) | The plan producer must be in the app layer (F2); a `plan` on the entry contract is MINE/CONFIRM. |
| A save keeps the comments | DECIDED (D-0174) | Not met today; a new library needs her yes (the ledger line). Only D avoids it. |
| One recipe graph for HOME and BLUEPRINT | DECIDED (ADR-099 16(d)) | Met for structure; not for columns (F4, F5). The three column sources (F5) must be reduced to one story: plan when the data exists, declared plan when it does not (`declared_plans` exists for exactly this: "a caller that may not ask the engine", D-0358). `RecipeGraph._flow` then duplicates `step_effects`; that duplicate should be removed on the HOME side, not copied into BLUEPRINT [OPEN, MINE]. |
| No shim, one authoritative way | rule | `apply_logic` (F7), the second catalog (F9) and `JOIN_HOW_OPTIONS` (F10) are the second ways to remove. |

Where an option reconsiders a decision: D reconsiders ADR-075 section 7 and the order's "visual"; C amends ADR-039 and ADR-040 (the map shows empty places); B extends D-0325 beyond HOME (CONFIRM). A and B reconsider nothing.

---

## 6. When the engine is selectable (all approaches)

Stays generic: the draft, the checker (EN02, T06), the graph, `Plan` and `PlanFailure`, the display, `effective_engine` and `tier_engine`, the cache key rule (the engine is in the key, D-0240).
Must exist per engine: the registry entries with `engine` and `ui_schema`; the entry file with `wrangler`, `assembler` and (to add) a `plan` and a `preview rows`; the readings of what a step does to the columns (`READINGS`, keyed by prefixed action names); the type names (`dtype_picker`, `input_fields` types) and the expression language (ST06, the `expression` widget); the help and the agent text. Until one more engine exists none of these can be tested, so the design must keep each of them behind ONE function (the engine's), so that a second engine fills a slot and the display never names Polars [MINE].
Also: a tier-3 or join tier takes the recipe's engine, not the engine of what it reads (`05` section 2); with two data engines the plan of such a tier needs a visible rule (E6, open).
The refusal "no library for this engine in this app" must reach the user at the moment they pick the engine, not at the first run (`engines.py:124-136`, exists).

---

## 7. Recommendation

One combination, built on one core: S1 to S5 first (the draft, the evaluation of the draft, the engine's run, one catalog, forms as a pure function), then the plan on the draft (B) as the data under every step and every picker, then the map with empty places (C) as the frame. Forms (A) are the editing widget throughout. Text (D) stays the existing escape hatch, read only unless the flag is on.
Why: (1) the three seams are common to all four, so building the core first keeps every later choice open (the owner's order of design-then-build); (2) B removes the biggest weakness of today's BLUEPRINT (it is blind to the columns that earlier steps make) with code that already exists for HOME, and it uses the one authority that Eve decided (D-0325); (3) C adds no new engine facility, only the display of what the graph already has, so it can come later or never without wasting the core; (4) D is the cheapest way to keep comments, but it gives up the visual IDE; keep it as the escape hatch and decide the writer (S6) separately.
Not recommended: starting with C (the map) before S1 and S2c: it would draw a lineage from one store while the data comes from another (F8).

---

## 8. What the user must be told to choose well (not what to choose)

- BLUEPRINT today shows the declared fields only; a step that makes a column is not seen by the next picker.
- The plan is exact on names and types and says nothing on values: counts, NA, a join that multiplies rows, a cast that loses decimals appear only when rows are read.
- A table of "first N rows" is the start of the result, not a sample of the input.
- A draft that does not run yet has a plan only up to its first failure.
- Saving overwrites the file, drops its comments and changes the key of stored tables (today).
- Text editing keeps comments and gives up the forms.

---

## To decide first (ranked)

1. One draft in memory, file written only at Save (S1), and whether BLUEPRINT may compose the plan of a draft that does not pass HOME's gate (D-0325 leaves BLUEPRINT's use to the design pass).
2. The profile of BLUEPRINT's check: `build` (spec) or `run` (code), or both shown apart (`04` choice 3). It decides whether a draft can be planned and judged while unfinished.
3. The writer and the comments (D-0174; a library needs her yes) against text first.
4. Whether the plan is part of the engine entry contract (D-0247) and who answers "rows" for another engine.
5. Where the user sees the tier, the file and the empty places (`04` choice 11); whether node-level dependence is enough at first.
Later: engine levels and what happens to steps when an engine changes (E2, E3, E5); t3 context; widgets per engine; plot defaults across plot engines (E7).

## To report now (verified, not a decision)

- BLUEPRINT's Joint Designer offers `how = outer`; the shared step check refuses it (ST10: "write one of inner, left, right, full, semi, anti, cross"); the test pins the stale list (`join_designer.py:27`, `test_join_designer.py:266`, run `join_check.py`).
- `WrangleStudio.apply_logic` prints and skips a failed step (`wrangle_studio.py:2316-2328`): the glimpse can omit a step without a word, against "nothing changes a result silently" [reasoned from the code; not seen on a screen].

## Not verified

- Nothing was seen on a screen; no browser run.
- That `compose` works on a draft once an envelope exists, with no data file, and its speed on a large recipe (the `reuse` argument exists; the measure it cites, `tmpAI/lbfb_0b/out_ST22.json`, was not read).
- Whether every action accepts the step shape that `apply_logic` hands it (params only, no `action` key) as the engine's (whole rule); not checked per action.
- Whether `ingest` is lazy for every file type (so that the plan reads no rows); the composer text says only a pivot, a sample or a describe read rows.
- The tier-3 plan of a plot on a draft; the plot picture of a draft (the preview reloads the file, F8).
- How `lineage_walk` could answer "what feeds this step" cheaply; I read its role from its header and `step_effects`, not its 775 lines.
- A comment-keeping writer (library, the test of D-0174): not examined.
