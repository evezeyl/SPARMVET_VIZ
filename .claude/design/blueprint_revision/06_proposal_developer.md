<!-- copied unchanged on 2026-11-21 from .claude/design/studies/scratch_records_2026-11/panel/blueprint_step4/developer.md (not in git), written 2026-11-21 night in step 4 of the BLUEPRINT review; a viewpoint's proposal: it recommends, it decides nothing -->
# BLUEPRINT review step 4: DEVELOPER viewpoint (effort, risk, tests, build order)

Written 2026-11-21. Proposes; decides nothing. Effort and risk are facts for ordering, not reasons. Labels: verified (read at file:line), reasoned, assumed. Nothing was run except greps and `wc`; no test suite.

## Summary (6 lines)
1. Four approaches: A forms plus check on Apply; B live plan after every step (the plan of the engine as the spine); C lineage first (the map as editor); D text first with assistance.
2. The one new piece all of B, C and the column pickers need is the same: a plan of a DRAFT (unsaved edit) in BLUEPRINT. `compose` exists (`app/modules/plan_composer.py:322`) but takes a loaded recipe from disk; a draft constructor is missing.
3. A is the smallest and the safest, but it leaves the owner's "lineage" wish and the column pickers unmet; B is the best fit to her order and reuses the most; C is the largest; D is the cheapest to start and the weakest for the non-developer user.
4. Recommendation: A repaired as the base, then B built on it in small parts; C only as a view of B (not an editor); D only as the existing escape hatch. Reasons in section 6.
5. Before any of it, the unreachable parts of today's BLUEPRINT (hidden Save, unmounted preview, no undo caller, the agent switch gating ten controls) must be repaired: every approach needs them.
6. Biggest risks: the cost of composing a plan after each keystroke-level edit (not measured), and a plan of a recipe that does not load yet (not tested).

## 1. Facts from the code that the estimates rest on (verified unless marked)

| # | Fact | Source |
|---|---|---|
| F1 | The plan of every place (names and types after step k, no data collected, a failure is a value with the engine's own sentence) exists and is tested against the real build on every shipped recipe. 35 tests, 655 lines. | `app/modules/plan_composer.py:1-30, 322-338`; `app/tests/test_plan_composer.py` |
| F2 | `compose(orchestrator, recipe_id, loaded, graph, reuse)` needs a `LoadedDataAnalysisRecipe` (it reads `loaded.raw`, `loaded.is_audit_copy`) and a `DataOrchestrator`. BLUEPRINT's handlers already receive the orchestrator (`blueprint_handlers.py:6, 323`). The only way today to make a `loaded` from an edited dictionary is `cache_keys.loaded_from_resolved(original, raw)` (`cache_keys.py:414`), written for audit copies: it copies path, files and signature from the original. | read |
| F3 | `reuse=` takes an earlier `Composition`; a node whose definition is equal by value and whose inputs are reused is not planned again. This is the mechanism for "edit one step, replan only below it" (HOME uses it for candidates, `plan_composer.py:358-369`). | read |
| F4 | The plan book has an entry for every (node, k). Rows are not in it. `Composition.frames` keeps only the lazy table at the END of each node, not after each step (`plan_composer.py:225-237`). So "rows after step k, on demand" is missing: it needs a small function that re-runs the steps up to k and collects (the runner is `engine.wrangler().run(lf, [step])`, the same one). | read |
| F5 | The plan reads the data files the way the build does; only a pivot, a sample or a describe read rows. The time of one composition on a real recipe is not known (a measurement is quoted in a comment as `tmpAI/lbfb_0b/out_ST22.json`, not read). | read; not measured |
| F6 | BLUEPRINT's current preview does `apply_logic(lf).collect()` on the stored parquet of the anchor (`wrangle_studio.py:597-632`), its own path, not the plan. | read |
| F7 | The checker `check_recipe(raw, profile, catalogs=, graph=, plans=)` returns coded problems with path and fix (`recipe_check.py:1315`, `Problem` at `:120`). BLUEPRINT's Validate calls it through `data_analysis_recipe_validator` with profile `run` (`H:2844`). `checker_catalogs()` in `data_analysis_recipe_validator.py` already hands the actions, components and BOTH engine tables to the checker. So the engine field IS reachable from the app layer (E4 of `05` has a ready function; BLUEPRINT's own catalog does not use it). | read (grep) |
| F8 | `recipe_graph.build_graph(raw, columns_provider=None)`: a node's columns are asked from a provider; BLUEPRINT passes none (`N:122`). A provider backed by the plan book is the natural join point. | read (`recipe_graph.py:467-470`, `N:122` per `02` G) |
| F9 | Wrangle Studio's action picker, form renderer and step list are the `ui_schema` machinery; they work (`02`/`04` section 3). `blueprint_handlers.py` is 2941 lines with one `define_server`, `wrangle_studio.py` 2328 lines: adding to them adds risk. | `03` section 5 |
| F10 | HOME's lineage walk (`utils.lineage_walk`, 775 lines) answers "where can a step on column X be written"; it is not needed for writing a recipe (HOME's audit question). What a recipe writer needs from the lineage is: the columns after a step, who feeds whom (the graph), and what is below a step (the plan entries below it fail or change). | read |

## 2. The four approaches

### A. Forms first, check on Apply and on Save
**User sees.** As today, completed: a table is added by a form; a step by action picker and form; Apply shows a data glimpse; the check runs on Save and on a Check button. Columns offered are the declared fields.
**Engine facility.** Checker (exists, F7). Wrangling run on the stored table (exists, F6). Plan: not used. Lineage: the existing rail.
**Missing.** Table and field forms, join save, tier-3 form, visible Save, remove or move a step, undo caller, plot mount, `build` profile in Validate, comment-keeping writer. These are needed by every approach.
**Pros.** Smallest step from today; every part is small and shippable alone.
**Cons.** The user learns a step is wrong only at Apply or Save; a column made by an earlier step cannot be picked (parked item 1.1); the owner's "see how the engine and the lineage can help write" is not answered.
**Pitfalls for the user.** A glimpse on the stored table can show data that the edited recipe would no longer produce (the step list is applied to a stored table; F6): the user trusts a picture that is not the recipe's result.
**Selectable engine.** Generic: forms from `ui_schema`, the checker. Per engine: the entries and their schemas, filter by the engine field (F7 gives it).

### B. A live plan after every step (columns and types always current; rows on demand)
**User sees.**
- New recipe: the stub, with the engines shown.
- A table and its fields: the declared fields next to what the file really has (the ingestion already computes the undeclared list, `ingestor.py:147` per `04`).
- A step: below each step card, a plan line "N columns; added: a, b; removed: c; changed type: d (String to Int64)". The picker of a column lists the columns of that place with their types. A failing step shows the engine's own sentence at that card and greys the places below it (this is the PlanFailure already built).
- A join: the plan of both inputs and of the result; the key match and the row counts on demand.
- A plot: the plan of the table it reads, with discrete or continuous told from the engine type.
- Final check: the checker with `build`, plus the list of places that failed to plan.
- "Show rows" on a step: a collect of a sample, labelled as a sample.
**Engine facility.** Plan composer (exists, F1) for names and types; the same step runner for rows (exists, rows after k missing, F4); the checker (exists).
**Must be built.** (1) A plan of a draft (F2): a `loaded` made from an in-memory raw, with the original's path and files; the chosen way is a new small function beside `loaded_from_resolved`, not a flag on it. (2) A BLUEPRINT-side cache of the last `Composition` and a `reuse=` call after each edit (F3). (3) A `columns_provider` backed by the plan book (F8), so the existing picker code reads one source. (4) The rows-after-k function (F4). (5) Display: a plan line on a card; failing places greyed.
**Pros.** Answers the order directly (engine and lineage help the writer); the user sees what a step did to columns and types before saving (the scientist's weight); the plan equals the real run by one code and a standing test (F1), so the display cannot drift from the build; closes the parked items 1.1 (pickers), partly 1.2 (cast: a type change Float to Int is visible in the plan line, the loss of decimals is not; that needs rows) and 1.3 (undeclared columns).
**Cons.** Needs the data files on disk and a recipe whose earlier places plan; a recipe with no data shows only the declared fields (must be said, not hidden). Cost per edit unknown (F5). A plan shows no rows: a join that multiplies rows or a filter that removes all rows is invisible in names and types.
**Pitfalls for the user.** "Types are right" can be read as "data are right". A sample for the rows can hide rare values. A plan that failed at step 3 greys step 4 onward: the user may think step 4 is wrong.
**What would change a result silently.** Nothing in this approach writes a step for the user; a column picker that offers only planned columns must also allow a typed name (a column made later), shown as "not found at this place" and not blocked.
**Selectable engine.** Generic: the plan book, the `columns_provider`, the card line. Per engine: the composer's entry (D-0325 asks the engine for the plan; a second engine needs `collect_schema`'s equivalent and a runner), the type names, the expression widgets. If an engine cannot give a plan, B degrades to A for that tier, and the screen must say so.

### C. Lineage first (the map is the editor)
**User sees.** The tube map is the main surface: each node shows its tiers and engine; click a node to edit its steps; the rail shows the chain with the plan at each node; empty places are drawn and a click adds the first step; a column's path (born, renamed, dropped, recomputed) can be followed.
**Engine facility.** B's plan; the recipe graph (exists, structure only); `lineage_walk` (exists, written for HOME's audit; it answers "where can a step be written for column X", not "where was column X born"); a "born, renamed, dropped" trace is MISSING as a function (the plan entries can be diffed between k-1 and k, `step_effects.unread_pairs` at `step_effects.py:235` is the pairing code, reasoned).
**Must be built.** All of B; the draw of empty tiers and tier 3 (the graph has the nodes; the map does not draw them, `04` row TubeMap); a column-trace function; map editing (add, remove, move a node); the map refactor of a 1151-line navigator.
**Pros.** Matches D-0309 ("the lineage and the tube map are also to be leveraged") and D-0308 ("see where each step sits").
**Cons.** Largest; the map becomes the single entry for everything, so a defect there blocks all work; the lineage of HOME is for a different question (audit), so it is not a free reuse.
**Pitfalls.** A drawing that looks complete when places are empty or failed to plan.
**Selectable engine.** Generic: graph and map. Per engine: the plan.

### D. Text first with assistance (the YAML is the editor)
**User sees.** A YAML editor; beside it the check results at the line, the plan of each place, and completion of action names and parameters from the registry; forms open from a line.
**Engine facility.** Checker with path (exists; the path to a line number is missing); plan (needs a draft, as B); registry (exists).
**Must be built.** A code editor component with completion (not in `W`, `04` item 25); a text writer that keeps comments (the decided D-0174 needs it for every approach, and here the text IS the file, so comments are kept for free); line mapping of problems.
**Pros.** Comments and layout kept by construction; the maintainer's fastest way; the escape hatch exists in part (`H:1424-1462`, its Save writes nothing).
**Cons.** The user group is people who do not write code (D-0306, "zero Python/R knowledge"); a mistyped key is refused by format 1 only after the edit; the lib for the editor is new.
**Pitfalls.** A beginner pastes YAML from the Gallery without knowing the tiers.
**Selectable engine.** The completion list per engine is generic if it reads the registry's engine field.

## 3. Comparison (for ordering)

| | A | B | C | D |
|---|---|---|---|---|
| Effort beyond the common repair | small to medium | medium (new: draft plan, cache, provider, rows after k) | large (B plus map redesign plus column trace) | medium (editor component, line mapping) |
| Risk | low | medium: latency of replan; draft that does not load | high: map becomes the single door | medium: a new editor library needs the owner's yes |
| Test cost | forms and Save: browser plus unit | unit tests like `test_plan_composer.py` (35 tests exist to copy); plan of a draft equals the plan of the same recipe saved; a browser pass | B plus map tests | text-to-file roundtrip, line mapping |
| Can reuse today's BLUEPRINT code | all of it | all; the pickers change source only | the navigator, partly | the escape hatch only |
| Uses the engine facilities | checker only | plan, runner, checker, registry | plan, graph, walk | checker, registry |
| Meets her order ("engine and lineage help write") | weak | strong | strong | weak |

## 4. The common repair (every approach needs it; independent of the choice)

Reachable parts of today (from `04`): (1) the mount of controls behind `blueprint_agent_enabled` (`H:1690-1691`) split so that only the chat depends on it; (2) a visible Save; (3) a caller for undo; (4) the plot mount; (5) remove or move a step; (6) Validate with profile `build` (or both, shown apart; her choice); (7) the writer that keeps comments (library question). The audit of what works with the switch off (V1, V2, V3) comes first: it is a check, no code.
Tests: today 14 BLUEPRINT test files, 2426 lines; the known-defects file pins defects and must be adapted when a defect is fixed (rule 5).

## 5. Build order (model/effort tag per CLAUDE.md section 2 table as I understand it: opus/high for design-bearing logic, sonnet/medium for forms and wiring, haiku/low for mechanical)

| Step | What | Tag | Parallel? |
|---|---|---|---|
| 0 | V1 to V3 checks in a browser; list what works | sonnet/medium | alone, first |
| 1 | Plan of a draft: a function making a `loaded` from an in-memory raw (new file, pure), tests: plan of draft equals plan of the same saved recipe; a draft with a failing step gives a PlanFailure, not an exception; a draft with no data file | opus/high | after 0; own files, own worktree |
| 2 | Rows after step k, sample, labelled: new function beside the composer; tests: equals the build's rows for k = n; k = 0; empty table | opus/high | parallel with 1 (own file) |
| 3 | Split the agent switch (`H:1690`) and the visible Save, undo caller, plot mount | sonnet/medium | parallel with 1 and 2 (touches handlers; do in a different worktree and merge in order) |
| 4 | Bring in the engine tables from `checker_catalogs()` into the picker filter; show the engine as a label | sonnet/medium | after 3 |
| 5 | A `columns_provider` backed by the plan; the pickers read it; the typed name stays allowed | sonnet/high | after 1 |
| 6 | Plan line on each step card and the greyed places; "show rows" | sonnet/medium | after 1, 2, 5 |
| 7 | Table and field forms, join save, tier-3 form (with the text of D-0305), `build` check on the nodes | sonnet/medium each; the join save and tier-3 serialiser logic opus/high | independent of 5 and 6 except for tests |
| 8 | Map additions (empty tiers, tier 3, engine label) only if C is chosen | sonnet/high | last |
| 9 | A scribe step: docs, UML, ADR sync (decision_compliance E4) | haiku/low or scribe | after each merge that changes behaviour |

Rule 5: tests adapted to the decided design first, then code; break the code once and see a test fail.

## 6. Recommendation (mine; she decides)

A repaired, then B built in the order above; C only as a view fed by B (labels and empty places on the map, no map editing); D only as the existing developer escape hatch, completed later if she wants.
Why, from the code: B reuses one tested mechanism (F1) with one added constructor and one added function (F2, F4); it cannot disagree with the build; it keeps today's pickers and forms (F9) and changes their source; each step in section 5 ships and shows alone; and none of it writes a step for the user. A alone leaves the parked pickers and the lineage unanswered. C adds a second large piece before the first is proven.
This reconsiders no decided point. D-0325 says "Blueprint is out of this choice" about the plan: B uses it in BLUEPRINT, which D-0325 neither forbids nor decides: flag it to her as an OPEN reading, not a conflict.

## 7. What the user (Eve) must be told to choose well

1. Whether BLUEPRINT may read the data files to plan (B needs them; a recipe without data shows declared fields only). Consequence: a user without the data sees less.
2. That a plan shows names and types, not rows: a join that multiplies rows or a filter that empties a table does not show in a plan line. Rows need a sample, and a sample can hide rare values.
3. That the time of one replan on a real recipe is not measured.
4. That Validate today uses `run`, so every unfinished recipe fails; `build` says it is fine to continue; showing both is her choice.
5. That a library for comment-keeping save is needed (D-0174 decided, library not).
6. That the agent switch today hides most controls in `standalone`.

## To decide first (ranked)
1. Which approach, or the combination in section 6 (decides the order of work).
2. May BLUEPRINT read data files to plan (B), and what it shows when it cannot.
3. Which check profile BLUEPRINT uses (`build`, `run`, both apart).
4. The comment-keeping writer (library).
5. What a step in the wrong tier does (the refusal is provisional).
6. Where recipes are read and written (P1 to P11); can wait, independent.
Can wait: tier engine (E5), engine of tier 3 (E6), plot-defaults per engine (E7), the names of the space, the AI agent.

## Not verified
- The time of `compose` on a real recipe, and with `reuse=` after an edit (F5).
- That a draft recipe that does not yet load (no plot, T09) can be composed; `compose` raises `RecipeGraphError` when the graph cannot be drawn (`plan_composer.py:325-326`), so a half-built recipe may have no plan at all. Must be tested in step 1.
- That `LoadedDataAnalysisRecipe` can be built from a raw that was never on disk (F2 reads only the signature of the original's fields; a new unsaved recipe has no original).
- Whether the picker code can take a provider without rewriting `_extract_upstream_cols` (`W:1979-2003`), not read in detail.
- The checker's cost per edit; the lineage rail and map code beyond `02`/`04`.
- Nothing was seen on a screen.
