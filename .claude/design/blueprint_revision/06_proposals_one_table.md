# BLUEPRINT-REVIEW-1, step 4: the four viewpoints in one table

Written 2026-11-21 by a worker of BLUEPRINT-REVIEW-1 (D-0395). It builds nothing and decides nothing. The viewpoints recommend; the owner decides.

Sources: the four proposals of this folder (`06_proposal_scientist.md`, `06_proposal_architect.md`, `06_proposal_developer.md`, `06_proposal_user.md`) and the brief they answered (`06_panel_brief.md`). The question: how the wrangling engine, the plotting engine and the lineage can help a user write a recipe in BLUEPRINT (the order, `ORDER.md`: "see how it is possible to use the wrangling engine and plotting engine to help a user to write recipes, with the lineage").

The four approaches:

- **A. Forms first**, with a check on Apply and on Save (today's design, completed).
- **B. A live plan after every step**: the columns and their types after each step, from the engine, without reading the data; rows and the effects of a step on demand.
- **C. Lineage first**: the map is the editor; a step is added at a place of the map.
- **D. Text first with assistance**: the YAML text is the editor; the engines check and complete it.

Labels used below: **read now** = re-read once by this worker on 2026-11-21 at the file:line given (worktree at `2c70694e`); **as reported** = as the viewpoint reported it, not re-read here; **reasoned** = a reading, not a fact of the code.

`H` = `app/handlers/blueprint_handlers.py`, `W` = `app/modules/wrangle_studio.py`.

---

## Flagged first

Each point changes a result silently, hides a step from the user, or reconsiders a decision. Points 1 to 8 are facts of today's BLUEPRINT that the viewpoints found or confirmed. Points 9 to 12 are pitfalls of the proposals themselves.

| # | What | Kind | Part of BLUEPRINT | Evidence and label |
|---|---|---|---|---|
| 1 | **Save rewrites the whole file from its in-memory form.** The file is opened with `"w"` and written by `yaml.safe_dump` of a dictionary, so every `#` comment is lost. A decision says the opposite (D-0174, taken by EVE, DECIDED; decision text: "A Blueprint save keeps the comments of the recipe file (option a)."; her words: "a)"). | changes the saved recipe silently; against a decision | Save of a step list or a plot | read now: `H:1187-1189` (open `"w"`, `safe_dump_recipe`), `H:114-116` (`yaml.safe_dump`). As reported, not re-read: a save also writes `comment: <file name>` into untouched steps (task BLUEPRINT-SAVE-COMMENTS-1 and the browser run of 2026-11-18), and so a save with no edit changes the file and with it the keys of the stored tables (`03` section 1.5; architect section 4) |
| 2 | **BLUEPRINT runs its steps with its own runner**, not the engine's. It skips an action it does not know and only prints the error of a step that fails, then goes on. The engine's runner raises an error that names the step. So the data glimpse can omit a step without a word, and what BLUEPRINT shows can differ from what the build makes. | changes what the user sees as the result, silently | Data glimpse (Apply) | read now: `W:2316-2328` (`apply_logic`: `if func:` ... `except Exception as e: print(...)`); `libs/transformer/src/transformer/data_wrangler.py:93` (`run`) and `:123-176` (raises `TransformationError`). The glimpse applies it on a stored table for a wrangling part: read now `W:625-630` |
| 3 | **The glimpse may apply the saved steps twice.** It takes the stored tier-1 table (already built from the saved file) and applies the in-memory step list on top. Whether the in-memory list repeats the saved steps was not traced. | would change the result shown, if true | Data glimpse | read now: `W:604-636` (the code's own comment says re-applying "would double-transform" for the other roles). Not verified for the wrangling role (the scientist's point 6.2, the architect's F8) |
| 4 | **The glimpse shows the first 10 rows, and a row count of the stored file**, not of the table after the edited steps. | hides what a step did to the rows | Data glimpse | read now: `W:735-737` (count of the stored parquet), `W:755` (`df.head(10)`) |
| 5 | **The Joint Designer offers `how = outer`**, a value that the join action does not have (its list is inner, left, right, full, semi, anti, cross). The step built with it is refused by the shared step check. A test pins the wrong list. | a choice offered that fails later (refused, not silent) | Joint Designer | read now: `libs/blueprint_arch/src/blueprint_arch/join_designer.py:27` (and its comment "mirrors the `how` enum"), `libs/transformer/src/transformer/actions/polars_calls.py:84`, `libs/blueprint_arch/tests/test_join_designer.py` (`test_join_how_options_match_action_enum`, the set with "outer"). The refusal code ST10 exists (`libs/utils/src/utils/ui_schema.py:251-255`, read now); the refusal of this very step: as reported (the architect's run `join_check.py`), not re-run |
| 6 | **The AI agent switch hides most of BLUEPRINT.** When `blueprint_agent_enabled` is off, the handler stops registering: the Joint Designer, the groups and plots, "+ New", Validate, the plot defaults, the info form are mounted and empty. | hides controls from the user | the whole space (setup `standalone`) | read now: `H:1690-1691`. Not seen on a screen |
| 7 | **Validate checks with HOME's profile `run`**, while the format says BLUEPRINT uses `build`. Every unfinished recipe "fails"; a "pass" means HOME's gate, and the user is not told which gate it is. | hides which check was made | Validate | read now: `H:2843-2845`, `app/modules/data_analysis_recipe_validator.py:401` (`profile: str = "run"`); the spec line "`build` \| Blueprint (building step by step)": read now `.claude/design/recipe_format_spec.md:230` |
| 8 | **The column pickers offer the declared fields only.** A column made by an earlier step, or the right table's columns after a join, cannot be picked. | hides columns that exist | Step forms | as reported (`W:1979-2003`, `H:677-759`; `03` section 1.1), not re-read |
| 9 | **Using the engine's plan in BLUEPRINT is to confirm, not decided.** All four viewpoints build on it. The decision text of D-0325 (the review session's wording of option B, not her words) says: "Blueprint is out of this choice (HOME and GALLERY first; Blueprint's needs go to its later design pass)." So the plan in BLUEPRINT is the design pass that the line leaves open. | reconsiders nothing; extends a decision to a space it left out | Column pickers, step cards, plot picker | read now: the ledger line D-0325 (taken by EVE, DECIDED), field "decision" |
| 10 | **Text first (D) reconsiders ADR-075 section 7.** ADR-075 makes the YAML escape hatch read-only for every setup with BLUEPRINT and editable only with the edit flag (today `data_analysis_recipe_edit_enabled`, on in `developer` and `qa`). D as the main surface for every user changes that rule, and the order's word "an ide (visual)". | reconsiders a decision | YAML escape hatch | read now: `.claude/knowledge/architecture_decisions.md:2864`, `:2868-2870` |
| 11 | **A preview of rows taken on a sample of the input, or with a row limit placed before a group-by, a join or a unique, changes the answer** and looks like the real one. The scientist asks for counts on the whole table; the architect for a limit only at the end of the plan, labelled; the developer and the user for a labelled sample. | would change a result silently (a pitfall of B) | the "show rows" of approach B | reasoned (scientist section 6 points 6, architect approach B, user section "Warnings") |
| 12 | **Any helper that writes a step for the user** (adds the final `polars_select`, a sort, a cast to fix a plan failure) **or translates steps when an engine changes** chooses for the user, and a translation changes results silently. | would change a result silently; against "the tool informs and the user chooses" | every approach; the engine choice | reasoned (scientist section 6 points 3 and 7; user summary point 5; `05_engines_in_blueprint.md` options R4 and P4) |
| 13 | **A lineage line "this column comes from table X" built from names only would mislead.** The walk reads the names a step writes, never the formula; a join is read only for left and inner. | would hide where values come from | Lineage (approach C) | read now: `libs/utils/src/utils/step_effects.py:1-30` (module text: "only names are read, never the formula", `knows_source_of_values` False, "A join is read only for `how` = left or inner") |

---

## The table: approach by viewpoint

| Approach | Viewpoint | Pro | Con | Evidence (as the viewpoint gave it) |
|---|---|---|---|---|
| A forms first | Scientist | Smallest change from what exists; a beginner sees one thing at a time | The user learns what a step did to the rows only by looking at the first 10 rows; the check is about structure, it cannot know that a filter dropped 4 samples; pickers stay on the declared fields | 68 actions with `ui_schema` (`04` section 3.2); glimpse `W:755`; `03` section 1.1 |
| A forms first | Architect | Every piece exists: `step_problems` is the one judge of one step, `check_recipe` is pure; testable without a browser once the form-to-step is a function | Apply today calls neither the step judge nor the checker; a step stored by a form can be refused later in another place; BLUEPRINT stays blind to the columns earlier steps make | `ui_schema.py:216`; `H:1199-1385` (grep: no `step_problems`); F5, F6 |
| A forms first | Developer | Low risk; every part small and shippable alone; reuses all of today's code | Does not answer the order ("engine and lineage help write"); the glimpse on a stored table can show data the edited recipe would no longer make | `W:597-632` (F6); comparison table section 3 |
| A forms first | User | "I fill a form and press Apply" is easy to understand | The error comes after the work, with a coded message; a lost sample is found in HOME; risk of a wrong choice: high | `H:2843-2845`; `04` section 3 |
| B live plan | Scientist | Catches a type mismatch or an absent column with no data read; pickers follow the real columns; same code as the build, so the picture equals the run | The plan has names and types only: a filter that keeps NaN, a join that multiplies rows, a whole-table count need a collect; pivot, sample and describe read rows to plan, so the columns offered can depend on the data file | ran: `scientist_scratch/t.py` (NaN kept by `x > 2`, 3 rows become 4 on a duplicate key, `SchemaError` on Int64 against String); `plan_composer.py:1-30` |
| B live plan | Architect | One authority for names and types (the one HOME uses); no second description of what a step does; a failure is a value, so the screen can say where it fails | Needs the data file and a recipe that gets to that place; the plan exists only for a recipe that passes HOME's loader (BLUEPRINT's own new-recipe stub is refused); the plan producer calls a Polars function, so a second engine needs the plan in its entry contract | `plan_composer.py:104-118`, `:322-338`; run `arch_check.py` (the loader refuses the stub, `SystemExit`); `plan_composer.py:83` (`collect_schema`) |
| B live plan | Developer | Reuses one tested mechanism (35 tests against the real build) with one new constructor and one new function; each part ships alone; writes no step for the user | Time of one replan on a real recipe not measured; a half-built recipe may have no plan at all (`RecipeGraphError`); "rows after step k" is missing (only the end of each place is kept) | `app/tests/test_plan_composer.py`; `plan_composer.py:225-237`, `:325-326`; `cache_keys.py:414` |
| B live plan | User | One sentence ("after each step, here is your table") and one picture (columns with types, new ones marked, removed ones struck); the consequence is seen at the moment of choice | False comfort from a sample; "types are right" can be read as "data are right"; when a step fails the screen must say why and not show a stale list | `02` section I; `03` section 1.1 |
| C lineage first | Scientist | Answers "where am I" and "what depends on this step" before a deletion | Shows names, not values or rows; "recomputed" is known, "from which column" is not; joins other than left and inner are grey | `step_effects.py` (`knows_source_of_values` False); `recipe_graph.py` |
| C lineage first | Architect | The structure is what the recipe is (no second model); the place gives the tier and the file, which ends the wrong-tier refusal; uses the lineage she asked to leverage (D-0309) | For most of the 68 actions the column-level lineage is "cannot follow" (7 read); the walk answers HOME's question ("where can an audit step go"), not "what feeds this step"; a crowded map for a large recipe; highest long-term cost | `recipe_graph.py:14-21`, `:195-240`; `blueprint_mapper.py:41-45`; `step_effects.py:56-70` |
| C lineage first | Developer | Matches D-0308 and D-0309 | Largest; the map becomes the single door, so a defect there blocks all work; a 1151-line navigator to rework; needs all of B first | `03` section 5; `04` row TubeMap |
| C lineage first | User | Good for seeing what feeds what | A beginner meets the map before knowing what a tier is; one picture cannot carry a recipe of many tables and plots | `04` section 2 |
| D text first | Scientist | The recipe seen is exactly the recipe saved; good for a maintainer | Not "no code" for a bioscientist (D-0306); the user still needs the effect of steps on rows; a default inserted by completion would choose for the user | `04` section 3.2 (the hatch's Save writes nothing) |
| D text first | Architect | The file is the one store, so comments are kept with no new library and no serialiser can lose a key | Not the visual IDE of the order; YAML by hand; `!include` makes "the text" several files; reconsiders ADR-075 section 7 | `recipe_check.py:120` (a problem has a path, not a line); `utils.strict_yaml` |
| D text first | Developer | Cheapest to start; comments and layout kept by construction | Needs an editor library (her yes), a mapping from a problem's path to a line; weakest for the non-developer user | `H:1424-1462`; `04` item 25 |
| D text first | User | Fine for a recipe maintainer | Highest risk for beginners: `'on'` quoting, prefixed names, `ui_label` unaided; refusals in coded words | `rules_agent_role_bioscientist.md` (prohibitions) |

---

## Where the four agree

1. **B is the spine.** All four put the live plan after every step (approach B) at the centre: the columns and types after each step, from the engine's plan that HOME's audit already uses (`app/modules/plan_composer.py`).
2. **A's forms stay the way to write a step**; D (the YAML) stays the existing escape hatch, read-only for most setups; C (the map) is a frame or a view, not the first thing built.
3. **The main new piece is a plan of a draft.** Today the plan is made only for a recipe that loads in HOME; BLUEPRINT needs it for an unsaved edit and for a recipe that has no plot yet. All four say it was not tested.
4. **A plan shows names and types, never rows.** What a step did to the rows (rows in and out, null and NaN, a join that multiplies rows) needs a collect, and the label must say what was counted.
5. **The check must be shown in two parts**, "is it well built so far" (`build`) and "can HOME open it" (`run`), or the profile chosen first (all four rank it in their first three).
6. **The agent switch must gate only the chat** (architect, developer, user say it plainly; the scientist does not discuss it).
7. **Nothing is written for the user and nothing is translated** when an engine changes: show the consequence, keep the steps, mark them.
8. **Today's Save is the point of no return** (overwrite in place, no backup, comments lost): no new editing feature before what a save may change is settled.
9. **With a second engine**, the plan, the readings of the lineage (`READINGS`), the widgets and type names, and the help are per engine; the layout, the checker and the graph stay generic.

## Where they differ

| Point | Scientist | Architect | Developer | User |
|---|---|---|---|---|
| What comes first | What the user is shown about rows before saving | One draft in memory and the "draft evaluation seam" (one draft, check, graph, plan, the engine's runner, one catalog, a form-to-step function) | The approach, then the repair of today's unreachable parts, then the plan of a draft | Whether the column list after each step is the backbone |
| Rows on demand | Counts on the whole table, always labelled; a full list of unmatched keys | A limit only at the end of the lazy plan, labelled "first N rows of the result"; counts only when really counted | A sample, labelled as a sample | "The first 100 of the file", with a "count all rows" button |
| Role of the lineage | Navigation and "what breaks if I remove this" | The frame: empty places on the map; the place gives the tier; node-level dependence first | A view of B only, no map editing | The way to move around |
| HOME's lineage walk | Useful, with its limit said in words | Reuse its data, but a new small query for "what feeds this step" | Not needed for writing a recipe (it answers HOME's audit question) | Not discussed |
| A note of the data a recipe was tested on | Raised as "to decide" (history in the recipe against BLUEPRINT never writing an audit) | Not raised | Not raised | Not raised |
| Today's `apply_logic` and the second catalog | Not discussed beyond the glimpse | Must go: one authoritative way (the engine's runner, one catalog with the engine field) | The pickers keep today's code and change their source | Not discussed |
| Effort as an argument | Not used | Long-term cost shown | Shown as information for ordering (rule 10: effort is never the argument) | Not used |

## The combination each recommends

| Viewpoint | Recommendation (theirs, not decided) |
|---|---|
| Scientist | B as the spine (types by plan, rows by a count, a "step effect card" for filter, join, cast and plot mapping), C as navigation, D as a read-only view of what will be saved, A's forms as the way to write each step. Not A alone |
| Architect | Build one core first (one draft, the evaluation of the draft, the engine's runner, one catalog, forms as a pure function), then the plan on the draft (B) under every step and picker, then the map with empty places (C) as the frame; A is the editing widget; D stays the escape hatch. Not C before the core |
| Developer | A repaired as the base, then B in small parts (the plan of a draft, rows after step k, a column provider fed by the plan, a plan line on each card); C only as a view fed by B; D only as the developer escape hatch |
| User | B as the backbone with plain sentences under each step; the map only to move; forms underneath; YAML read-only. Both checks shown apart; only the chat behind the agent switch |

Reading of this review, not decided: the four recommendations are one combination seen from four sides. The combination is "B on top of forms, with the map as a view, the YAML read-only"; they differ on what comes first (rows shown to the user, one draft, the repair) and on how rows are previewed.

---

## Not verified (by this worker)

- Nothing was run here; no browser. The runs named above are the viewpoints' own (`tmpAI/panel/blueprint_step4/`, git-ignored).
- Point 3 of the flags (a double application in the glimpse): read, not traced.
- The refusal of the `outer` join step by the step check: not re-run.
- The rows labelled "as reported" in the flags.
