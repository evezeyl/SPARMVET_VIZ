# BLUEPRINT: a guide for the rebuild (larger decisions first)

Written 2026-11-21 by a worker of BLUEPRINT-REVIEW-1 (D-0395), step 6 of the review. It builds nothing and decides nothing. Every open choice below is "to decide". No question is put to the owner here.

Her order for this guide (`ORDER.md`): "prioritize larger decisions/questions to take first but no details - it will be a guide to help have an efficient and structured way to approach the rebuild of blueprint."

Inputs: every file of this folder (`01` to `05`, `07`, the `06` files, `prior_work/README.md` and the files it lists). The detail is there; this guide only points to it.

Labels: **read** = the code was read at that file:line by a worker of this review (the file and the section say when); **read now** = re-read on 2026-11-21 while writing `06_proposals_one_table.md`; **as reported** = taken from a viewpoint or a document, not re-read; **reasoned** = a reading, not a fact. `H` = `app/handlers/blueprint_handlers.py`, `W` = `app/modules/wrangle_studio.py`.

---

## 1. One page

### What BLUEPRINT is meant to be (her words)

- The order: "it is an ide (visual) that help the user create recipes for production : with the actions and parameters available (depending on the engine used ... now we have only one engine for the data and one engine for the plotting - but the engine "language" will need to be able to selected in the blueprint)" (`ORDER.md`, M421; the same words in D-0395).
- D-0306: "Blueprint is the ui ide for building our recipes." and "It needs to be able to build the whole recipe."
- D-0308: "We need to be able to build as the recipe specs - however for building the normal logic is to start by t1 then T2 then T3 then plot".
- D-0309: "we had the lineage/tube map also to leverage .. so we will need to have a global clear picture of how it need to work and then evaluate solutions"
- D-0348: "we take blueprint afterwards - that will also be easier because then we know what we can reuse from the home design"

(All five ledger lines are taken by EVE and DECIDED.)

### Where it stands today (ten lines)

1. A user can edit the steps of an existing tier file and of an existing plot; most other steps of the journey (add a table, its fields, a join file, tier 3, a plot's target) have no control (`04` section 2).
2. Four built parts cannot be reached: Save (in a hidden box), the plot preview (never mounted), undo (no caller), and, when the AI agent switch is off, about ten controls (`04` section 3.1; read now `H:1690-1691`, `W:248-258`, `W:713-716`).
3. Save rewrites the whole file: comments are lost, no backup, a fixed folder instead of the deployment's (`04` section 4; read now `H:1187-1189`).
4. The column pickers know only the declared input fields, not the columns that earlier steps make (`03` section 1.1).
5. Validate checks with HOME's profile `run`, so every unfinished recipe "fails" (read now `H:2843-2845`).
6. BLUEPRINT runs steps with its own runner, which skips a failing step with a printed line; the engine's runner raises (read now `W:2316-2328`).
7. The engine layer is decided and built (engine per recipe, tier, plot; refusal of an engine with no library); BLUEPRINT shows none of it and its catalog does not receive the engine (`05` sections 2 and 3).
8. The app already has the plan of every place (columns and types after each step, from the engine, no data built), made for HOME's audit; BLUEPRINT does not use it (`02` section G; read now `app/modules/plan_composer.py:1-12`).
9. The AI agent chat cannot work today: wrong call arguments, no session start, the instructions passed as the recipe path (`07` section 3.1).
10. Many texts (ADRs, rules, help, user doc) say "done" for parts that are not reachable (`03` section 3; contradictions in section 6 below).

### The panel's recommendation (a recommendation, not a decision)

The four viewpoints of step 4 recommend one combination: **a live plan after every step as the spine** (the columns and their types after each step, from the engine; what the step did to the rows on demand, labelled), **forms to write each step**, **the map and the rail as a view** (where a step sits, what depends on it), **the YAML read-only** except in the developer setups. They differ on what comes first and on how rows are previewed. Detail: `06_proposals_one_table.md`.

---

## 2. The larger decisions, ranked

Ranked by what each one blocks. Each line: the question, why at this rank, the options in a few words, the panel's recommendation when there is one, where the detail is. The smaller choices are grouped under the decision they depend on, by reference only.

### 1. What BLUEPRINT is, as a whole: which approach

- **Question.** Is BLUEPRINT built around forms (A), a live plan after every step (B), the lineage map as the editor (C), or the YAML text (D), or a combination?
- **Why first.** It decides the order of all work and what every screen shows.
- **Options.** A, B, C, D, or a combination (`06_proposals_one_table.md`, the table).
- **Panel.** All four: B as the spine, A's forms to write a step, C as a view, D read-only.
- **Detail.** `06_proposals_one_table.md`; the four `06_proposal_*.md`; `04` "To decide" 1 to 14 for the parts; `prior_work/GLOBAL_PICTURE.md` section F (15 open questions).

### 2. Where the columns of each place come from

- **Question.** Does BLUEPRINT ask the engine for the plan of each place (the code HOME's audit uses), and so read the data files, or stay on the declared fields?
- **Why second.** The column pickers, the line under each step, the plot's column choice and the parked items 7.1 and 7.3 depend on it. It is "to confirm": D-0325's decision text says "Blueprint is out of this choice (HOME and GALLERY first; Blueprint's needs go to its later design pass)".
- **Options.** The engine's plan; the declared fields (today); the stored tables. With the plan: what the screen shows without the data files, and for a draft that does not run yet (up to the first failure).
- **Panel.** The engine's plan, extended to an unsaved draft and to a recipe with no plot yet.
- **Detail.** `04` "To decide" 6; `02` sections G and I; architect F1 to F5 and approach B; developer section 2 B and "Not verified".
- **Grouped here.** Whether the plan becomes part of each engine's entry contract (architect section 6; with decision 10).

### 3. What the user is shown about rows before a step is kept

- **Question.** Is the user shown what a step did to the rows (rows in and out; null and NaN in the columns a filter reads; join counts and repeated keys; samples that left the table), and is a count made on the whole table or on a labelled part?
- **Why third.** It decides whether a recipe made in BLUEPRINT can be defended to a reviewer; the plan alone shows names and types, never rows. It also sets the cost of every preview.
- **Options.** Whole-table counts always; counts on demand; a limit at the end of the plan, labelled; a labelled sample (the viewpoints differ, `06_proposals_one_table.md` "Where they differ").
- **Panel.** The scientist ranks it first; all agree that a sample or a limit must say what it is, and that a limit before a group-by, join or unique changes the answer.
- **Detail.** `06_proposal_scientist.md` sections 2, 4, 6; parked item 7.4 (join counts).
- **Grouped here.** Whether a recipe carries a note of the data it was tested on (scientist section 5; it touches "BLUEPRINT never writes an audit", D-0143).

### 4. One draft, and what a save may do to the file

- **Question.** Is there one draft in memory that every view reads, written to the file only at Save; and what may a save change (comments, the `comment:` lines, backup, overwrite, the dated final file), and where does it write?
- **Why fourth.** Save is the point of no return; no new editing feature should be added before it is settled. The plan of a draft (decision 2) needs one draft.
- **Options.** For the writer: a writer that keeps comments (D-0174 decided; a new library needs her yes), or the text as the store (approach D). For the places: the study of where recipes live (P1 to P11).
- **Panel.** One draft first (architect); a test that an untouched file saves byte for byte; tell the user before a save what it changes (user).
- **Detail.** `04` "To decide" 8 and 9; `03` sections 1.4 to 1.6; architect section 1 (S1, S6) and section 4.
- **Grouped here, by reference only.** The recipe places P1 to P11 (`prior_work/recipe_places/TABLE_FOR_THE_OWNER.md`; a separate study, D-0394); the dated name and the final save (D-0390 to D-0393); the hyphen in a name (D-0391, "to verify before building").

### 5. Which check BLUEPRINT shows

- **Question.** Does BLUEPRINT check with `build` (is it well built so far), `run` (can HOME open it), or both shown apart?
- **Why fifth.** The word "passed" is the user's guarantee; the check also decides whether an unfinished draft can be judged and planned.
- **Options.** `build` (the format spec); `run` (the code today); both, shown apart.
- **Panel.** Both apart (user; the others rank it in their first three).
- **Detail.** `04` "To decide" 3; contradiction L19 (section 6).
- **Grouped here.** Warnings that look different from errors (D-0059, D-0079); results shown on the step and on the map node, not only in a list; how a recipe that fails to open is shown with each point to fix (`02` F4).

### 6. Where each step sits, and whether BLUEPRINT ever blocks

- **Question.** How does the user see the tier and the file of each step, the empty places and tier 3; and what happens to a step put in the wrong tier?
- **Why sixth.** D-0308 asks for it ("will need to be able to see for each step of the recipes..."), and the answer decides the map, the step card and the save refusal.
- **Options.** For the place: map nodes per tier with empty places, a tier word on each card, the rail. For a wrong tier: refuse (provisional today), two files, no tier picker (the place gives the tier), guide the order.
- **Panel.** The architect: the place on the map gives the tier, which ends the refusal; the user: one tier word on each card in plain words.
- **Detail.** `04` "To decide" 4, 5, 11; `02` K6, K7; contradictions L4, L14 (section 6).

### 7. Which controls depend on the AI agent switch

- **Question.** Does the agent switch gate only the chat, or (as built) most of BLUEPRINT?
- **Why seventh.** Small, independent, and every other part needs it settled: in the `standalone` setup most of BLUEPRINT is empty today.
- **Options.** Only the chat (the rule written in ADR-082 and the flag rule); as built.
- **Panel.** Only the chat (architect, developer, user).
- **Detail.** `04` "To decide" 2; `07` choice G; contradictions L18, L20.

### 8. How a whole recipe is built from empty

- **Question.** How does a table enter a recipe (its file, fields, types, entity key), how are tier files and a join file created and saved, and how is tier 3 written?
- **Why eighth.** D-0306 decided that the whole recipe is built in BLUEPRINT; how is open, and it is the bulk of the new forms.
- **Options.** A table from a Test Lab boilerplate, a field editor in BLUEPRINT, or a branch copy; tier 3 with the button text of D-0305.
- **Panel.** No common recommendation; the developer puts these forms after the plan of a draft.
- **Detail.** `04` "To decide" 1, 7, 10; `02` K3, K8; `prior_work/GLOBAL_PICTURE.md` section F, questions 1 to 3, 6, 8.

### 9. How a plot is built in BLUEPRINT

- **Question.** How does the user set a plot's target table, title, mapping, layers and theme, see the picture, and fill a parameter that is a library object?
- **Why ninth.** D-0305 states the need and decides nothing ("We will also need to have a way to build the plot recipe."); it waits for decisions 1 and 2 (the columns offered).
- **Options.** Not written in the records beyond the forms of today; a study first (D-0305).
- **Panel.** The scientist: show the type of each mapped column and whether the plot treats it as discrete or continuous.
- **Detail.** `04` "To decide" 12; `02` K13; parked items 7.7 and 7.8.
- **Grouped here.** Typed values `{name, params}` (D-0277); the component rename `plotnine_` (D-0091, decided, not built); the plot-defaults form and its theme fields (D-0246); where the picture is shown.

### 10. The engine "language" in BLUEPRINT

- **Question.** Where is the engine shown and chosen (recipe, tier, plot), and what happens to the steps already written when it changes?
- **Why tenth.** The order asks for it; with one engine today, only showing it is possible to judge (D-0252: "even if we will not add new engines now, we can plan for it"). A plan per engine (decision 2) and a picker filtered by engine (E4) are the parts that must not block a later engine.
- **Options.** `05` section 4: show only; choose at creation; change with the steps kept and marked; translate (excluded by the goal: a translation changes results silently).
- **Panel.** Show the engine now as a plain label; never translate; keep and mark.
- **Detail.** `05` "To decide" E1 to E7. Grouped here, by reference: E1 (show now), E2 (where chosen), E3 (written steps), E4 (the picker gets the engine field), E5 (a per-tier data engine wanted at all), E6 (which engine a join tier and tier 3 inherit), E7 (plot defaults across plot engines).

### 11. Rebuild on today's code, or on new shared seams

- **Question.** Is the rebuild done inside today's two large modules, or on a small set of shared pieces: one catalog with the engine field, the engine's runner instead of BLUEPRINT's own, the form turned into a pure function that checks a step, the parts of HOME's new design that can be reused?
- **Why eleventh.** It decides the build order and how much old code stays; most of it can only be answered after the HOME refactoring (D-0348, check V14).
- **Options.** Keep and extend today's code (developer: the pickers change their source only); build the seams first (architect: S1 to S5); a mix.
- **Panel.** The architect: the seams first, and remove the second ways (BLUEPRINT's runner, the second catalog, the stale join list) as "one authoritative way". The developer: keep today's code, change sources.
- **Detail.** architect sections 0 and 1; developer sections 1 and 5; `03` section 5 (the size of the modules).
- **Grouped here.** The one word for the space (`04` "To decide" 14); the texts to correct (section 6 below).

### 12. The AI agent

- **Question.** Is the existing chat repaired first, which backend comes next (the Claude API, the CLI hardened), what protects the app and the files, and when is the agent shown to scientists' setups?
- **Why last.** It is a helper on top of BLUEPRINT; every part of it depends on the forms and the checks above (a proposal tool needs the draft and the check), and nothing else depends on it except the switch (decision 7).
- **Options.** `07` section 5: F (repair or skip), A (API backend: A1, A2, A3), B (protection: B1, B2, B3), C (good-practice text), D (role file), E (API key), H (scientists' setups), I (offline backend), J (session folder).
- **Panel.** Not a subject of the panel. The options document recommends A1, C2, E1 (`07` section 5; a document, not a decision).
- **Detail.** `07` sections 4 to 6, "What blocks what".
- **Grouped here.** The eight privacy and security points of `07` section 6 (what leaves the machine, with which backend, real or synthetic data, the login probe at start, the session folder).

---

## 3. What must be verified before any rebuild starts

Each item says how. None was done in this review.

| # | What | How |
|---|---|---|
| 1 | What works today in the browser, with the agent switch off and on | Start the app with the `standalone` setup, then `developer`; open BLUEPRINT; press each control; note what is empty (`04` checks V1, V2, V7) |
| 2 | What a save changes in a file | Save an untouched tier file, then `git diff` it (comments, added `comment:` lines, `data_engine`) (`04` V3) |
| 3 | What the data glimpse shows | Compare the glimpse after one edit with a build of the same recipe saved; check a node click loads its own table (`04` V4; flags 2 to 4 of `06_proposals_one_table.md`) |
| 4 | The agent wiring, read and never run | Send one message in the `developer` setup with synthetic data only; this calls a model (cost; text leaves the machine), so it needs the owner's yes; check the `--system` flag on the installed CLI (`07` section 3.1, "Not verified") |
| 5 | The time of the plan on a real recipe | Time `plan_composer.compose` on the shipped `2_test_data_ST22_dummy` recipe, then again with `reuse=` after one changed step (developer F5) |
| 6 | The plan of a draft | Try `compose` on a draft with no plot, with a failing step, with no data file, and on a recipe never saved to disk (developer "Not verified"; architect F3) |
| 7 | The filter and cast cases through the registered actions | Re-run the scientist's NaN, null, cast and duplicate-key cases through `modif_filter`, `polars_cast`, `polars_join`, not raw Polars (scientist section 9) |
| 8 | The texts that say "done" | Re-read the help, the user doc, rule section 7 of `rules_ui_dashboard.md`, ADR-082 and the UML diagrams against `04` (V9, V10, V11) |
| 9 | What HOME's new design gives BLUEPRINT | After the HOME refactoring, list HOME's shared modules and match them with the parts of `04` section 3 (V14) |

---

## 4. A proposed order of the rebuild (proposal, not decided)

From the developer viewpoint (`06_proposal_developer.md` section 5), unchanged in substance. It starts only **after the refactoring of HOME and the Gallery** (D-0348; D-0271: "we do changes to blueprint and lab after - we focus on home and gallery"), and after decisions 1, 2, 5 and 7 above.

| Step | What | Can run in parallel with |
|---|---|---|
| 0 | The browser checks of section 3 (items 1 to 3): list what works | alone, first |
| 1 | The plan of a draft: build the input the plan needs from an unsaved recipe; tests: the plan of a draft equals the plan of the same recipe saved; a failing step gives a failure value, not an error; a draft with no data file | 2 and 3 (own files) |
| 2 | Rows after step k, labelled; tests against the build's rows | 1 and 3 |
| 3 | Repair what exists: the agent switch gates only the chat, a visible Save, an undo control, the plot preview mounted | 1 and 2 (different files; merged in order) |
| 4 | The engine field reaches the picker; the engine shown as a label | after 3 |
| 5 | The column pickers read the plan (a typed name stays allowed, marked "not found at this place") | after 1 |
| 6 | A plan line on each step card, failing places greyed, "show rows" | after 1, 2, 5 |
| 7 | Table and field forms, join save, tier-3 form, the check with the chosen profile | mostly independent of 5 and 6 |
| 8 | Map additions (empty tiers, tier 3, engine label), only if the map is chosen | last |
| 9 | Records: docs, UML, ADR text after each merge that changes behaviour | after each merge |

Rule for every step: tests adapted to the decided design first; break the code once and see a test fail (`agent_principles.md` point 5).

---

## 5. Defects found during the review (not fixed by this review)

Each: what, where, the part of BLUEPRINT, and its kind: **changes a result** (what the user sees or saves differs from what the recipe does, without a word), **hides** (something exists or happens that the user cannot see), **misleads** (a word on screen or in a text says something untrue), **cosmetic**.

| # | Defect | Where | Part | Kind | Label |
|---|---|---|---|---|---|
| 1 | Save rewrites the file from a dictionary: comments lost, no backup; reported to also write `comment: <file name>` into untouched steps | `H:1187-1189`, `H:114-116`; info save `H:2630` | Save | changes the saved recipe silently (against D-0174) | read now; the `comment:` part as reported |
| 2 | BLUEPRINT's step runner skips an unknown action and prints a failed step, then goes on | `W:2316-2328` | Data glimpse | changes a result shown | read now |
| 3 | The glimpse may apply the saved steps twice on the stored table | `W:604-636` | Data glimpse | changes a result shown, if true | read now; not traced (suspected) |
| 4 | The glimpse shows the first 10 rows and the row count of the stored file, not of the edited steps | `W:735-737`, `W:755` | Data glimpse | hides | read now |
| 5 | A node click on a source table loads another table's data | task BLUEPRINT-NODE-CLICK-WRONG-TABLE-1 | TubeMap, glimpse | changes a result shown | as reported (run of 2026-11-18) |
| 6 | The agent switch stops the registration of most controls | `H:1690-1691` | whole space | hides | read now |
| 7 | Save is in a hidden box | `W:248-258` | Save | hides | read now |
| 8 | The plot preview is never mounted | `W:713-716`; `output_plot` only in `home_theater.py` | Plot preview | hides | read now |
| 9 | Undo has no caller | `H:376` | Undo | hides (the help says it exists) | as reported (`04`) |
| 10 | One step cannot be removed or moved; only "Clear All nodes" | `W:379` | Step list | hides | as reported |
| 11 | A join built in the Joint Designer cannot be saved | `H:609-611` | Joint Designer, Save | hides (the work stays in memory) | read now |
| 12 | The Joint Designer offers `how = outer`, which the join action does not have; a test pins the wrong list | `join_designer.py:27`; `polars_calls.py:84`; `test_join_designer.py` | Joint Designer | misleads (the step is refused later) | read now |
| 13 | Validate uses HOME's profile `run`; one of its checks parses markdown text and counts a removed concept (`factory_id`) | `H:2843-2845`, `H:2866`; validator `:401` | Validate | misleads | read now (`H:2844`, `:401`); `H:2866` as reported |
| 14 | The column pickers offer the declared fields only | `W:1979-2003`, `H:677-759` | Step forms | hides | as reported |
| 15 | The info form reads and writes `info.name`; the format uses `info.label`, and the checker accepts `name` without a word | `H:2544`, `H:2606-2609` | Info form | hides (an edit with no visible effect) | as reported (`04` run) |
| 16 | The contract viewer's downstream column is always empty | `H:679`, `W:1612` | Contract viewer | hides | as reported |
| 17 | A step's tier comes from a context list; a step of the wrong tier is refused at Save (provisional) | `W:802-808`, `H:592` | Action picker, Save | blocks (against "never blocks building") | read now (`H:590-592`) |
| 18 | BLUEPRINT reads and writes a fixed recipe folder, not the deployment's | `H:975`, `H:2685` | Recipe list, "+ New" | hides (another place than HOME's) | as reported |
| 19 | The new-recipe name refuses a hyphen | `H:2636` | "+ New" | cosmetic today; blocks a dated name | as reported |
| 20 | The plot-defaults form changes the session only; the help lists removed keys | `H:1742`; `app/src/help/blueprint.md:17-25` | Plot defaults | hides (not saved); misleads (help) | as reported |
| 21 | The action picker is not filtered by engine; the catalog does not receive the engine field | `schema_registry.py`; `app/src/server.py:39-42` | Action picker | cosmetic with one engine | as reported (`05` run) |
| 22 | The agent chat: wrong call arguments, no session start, the instructions passed as the recipe path; the recipe context does not read `!include`; a `--system` flag the installed CLI does not list | `H:1859`, `H:1865-1870`; `agent_adapter.py:273`; `07` section 3.1 | AI agent | hides (every message fails) | as reported (`07`, run without a model) |
| 23 | The agent's prompt names seven tools; four do not exist, one of them "THE ONLY PATH to propose changes" | `agent_context.py:187-194` | AI agent | misleads (the model) | as reported |
| 24 | The CLI backend does not restrict the CLI's own file and command tools; `get_field_contract` reads any recipe path; the session folder is not git-ignored; the login probe calls the model at start | `agent_adapter.py:270-282`, `:175-180`; `agent_tools.py:234-260` | AI agent | hides (what leaves the machine) | as reported |
| 25 | Stale texts: the help, the user doc ("never writes Tier 3"), rule section 7, ADR-082 state column; a test docstring says the join rule "lives twice" | `03` section 3; `docs/workflows/blueprint_architect.qmd:146`; `app/tests/test_join_preview_parity.py:3-4` | documents | misleads | as reported |

---

## 6. Contradictions between sources (listed, not resolved)

- **L1 to L23** of `02_planned_vs_existing.md` section L (tier 3 in BLUEPRINT; audit and the plot spec; comments; blocking; figure text; info keys; one join-key rule; the "Add plot wrangling" button; "done" or not; the agent tool name; advise or enforce; the escape hatch and tier 3; `final_contract`; invalid positions; tier 2; what tier 3 is; where the rail is; what the agent switch gates; the Validate profile; the agent switch "with no effect"; the in-app help; the state of tasks; the counts in the rules). They extend G1 to G18 of `prior_work/GLOBAL_PICTURE.md` section G.
- **Added by step 2 (`04`).** The info form's `info.name` is accepted by the checker without a word, while the format and "+ New" write `info.label` (L6 seen from the checker's side).
- **Added by step 3 (`05`).** D-0219's line keeps "a data-engine override per tier is a plan owed to her, not decided" (the review session's words), while D-0250 built the optional `data_engine` key of a tier (`05` section 5, item 10). The number of plot components: 191 in `04` and `05` (run), 193 in `02` and `03` (a count of registering lines).
- **Added by step 5 (`07`).** ADR-076 records MVP-1 as "IMPLEMENTED" with smoke tests passed; no test sends a message through the panel, and the wiring cannot work (`07` section 3.1). ADR-076: "Existing BLUEPRINT IDE behaviour is unchanged when the flag is off"; the code: most of BLUEPRINT goes with the flag (L18, L20).
- **Added by step 4 (the viewpoints).** The Joint Designer's comment says its list "mirrors the `how` enum" of the join action; the enum has no `outer` (read now, `join_designer.py:26-27`, `polars_calls.py:84`). All four viewpoints build on the engine's plan in BLUEPRINT, while D-0325's decision text leaves BLUEPRINT out of that choice (not a conflict: to confirm, see decision 2).

---

## 7. Parked items about BLUEPRINT

| # | Item | Source | State |
|---|---|---|---|
| 7.1 | Column pickers that follow the lineage (the columns after each step, the right table after a join) | the order (M421); `03` 1.1 | not built; depends on decision 2 |
| 7.2 | A warning when values read from a file are cast to integer | D-0376 (her words: "ensure that if values in a data that is read that its casted to integer that there is a warning at least in the blueprint"); `03` 1.2 | not built; where and in what words not decided |
| 7.3 | Telling the recipe maker which file columns the recipe does not declare | D-0374 (her words: "informing here I think needs to be done for blueprint but not for HOME"); `03` 1.3 | not built; the ingestion already computes the list (console only) |
| 7.4 | Join counts (rows in, out, unmatched keys) | task JOIN-COUNTS-1 (provisional); `03` 1.8 | not built; with decision 3 |
| 7.5 | The dated name and the final save; replace only in the user's own place; the hyphen through the whole app | D-0390 to D-0394; `03` 1.4 to 1.6 | not built; with decision 4 and the places study |
| 7.6 | Warnings that look different from errors; all warnings shown in BLUEPRINT | D-0059, D-0079; `03` 1.8 | not checked; with decision 5 |
| 7.7 | The component names with the `plotnine_` prefix | D-0091 (decided, not built; task V1-B-RENAME waits for her look at the impact list); `03` 1.7 | not built; touches the picker, the plot save, the help, the agent text |
| 7.8 | The theme fields of the plot-defaults form; named themes | D-0246; `03` 1.8 | after the demo |
| 7.9 | Open a recipe that fails and show each failing point as a point to fix | her wish, "investigate, no build yet" (BP-STALE-VIEW-1) | open |
| 7.10 | The seed field linked to the steps that use jitter | ledger "asked, not decided" | open |
| 7.11 | A recipe changed in BLUEPRINT while HOME has it open | S2-3-Q, investigation only | open |
| 7.12 | The flags BLUEPRINT depends on (the agent switch) in the configuration review | CONFIG-REVIEW-1 | with decision 7 |
| 7.13 | The recipe-to-Python research with the BLUEPRINT agent | PY-RESEARCH ("start only after the visualisation library is done") | later |

---

## 8. Not verified

- Nothing in this review was seen on a screen. The only browser runs of BLUEPRINT are of 2026-11-18, on a tree that has changed (`prior_work/BLUEPRINT_T1_T2_PROOF.md`).
- No model was called; the agent's failure is read from the signatures, not seen.
- The plan of a draft, its time on a real recipe, and its behaviour on a recipe that does not run: not tried.
- The double application in the glimpse (defect 3): read, not traced.
- The scientist's data cases were run on raw Polars, not through the registered actions.
- The number of plot components with a usable form, and whether each parameter can be filled without code.
- The UML diagrams of BLUEPRINT against the code.
- Line numbers: the code moves with the HOME and GALLERY work in `dev`; re-read before relying on one. On 2026-11-21 the BLUEPRINT files were unchanged since `4bc3ebac` (`SUBTASKS.md`).
