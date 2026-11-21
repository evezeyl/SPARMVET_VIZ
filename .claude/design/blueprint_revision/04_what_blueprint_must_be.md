# BLUEPRINT-REVIEW-1, step 2: what BLUEPRINT must be

Written 2026-11-21 by a worker of BLUEPRINT-REVIEW-1 (D-0395). It builds nothing and decides nothing.

## Summary (10 lines)

1. BLUEPRINT is meant to be a visual IDE where a person who knows the data builds a whole recipe for production, with no code, from the actions and parameters of the engine in use (D-0306, the order).
2. The decided journey is: start a recipe, add tables, tier 1, tier 2, tier 3, the plots, check, save; the tool advises and never chooses (D-0308).
3. Today a user can edit the steps of an existing tier file and of an existing plot; most other steps of the journey have no control, or have one that the user cannot reach.
4. Four built parts are unreachable for a user: the Save button (hidden), the plot preview (never mounted), undo (no caller) and, in the `standalone` setup, about ten controls that answer only when the AI agent switch is on.
5. The save path writes the shape of recipe format 1 (tiers as own keys, prefixed actions, `ui_label`), but it drops comments, overwrites in place, writes into a fixed folder, refuses joins, and cannot write tier 3.
6. New since the step-1 reading: the engine now reads tier 3 of a plot (the checker no longer refuses it), so the missing tier-3 form is a gap of BLUEPRINT only.
7. BLUEPRINT's Validate checks with HOME's profile `run`, while the format says BLUEPRINT uses `build`; a fresh "new recipe" passes `build` and fails `run`.
8. Column pickers offer the declared input columns of the table only; the app already has code that knows the columns after each step (the plan of HOME's audit), unused by BLUEPRINT.
9. The boundaries are clear in the decisions: BLUEPRINT edits the original recipe, never an audit recipe; Test Lab and Gallery hand over through files only.
10. The rebuild must start with a short list of checks (section 6): many texts and tasks say "done" for things that are not reachable.

## How to read this file

Labels on every fact:

- **read**: I read the code at that file:line on 2026-11-21 (tree `dev` at `8cd699f7`).
- **read-1**: read in step 1 (`02_planned_vs_existing.md`, tree `4bc3ebac`); the BLUEPRINT files did not change since (`git diff --stat 4bc3ebac HEAD` on `blueprint_handlers.py`, `wrangle_studio.py`, `libs/blueprint_arch`, the engine and agent files shows no change; run 2026-11-21). Not re-read line by line.
- **run**: I ran it; the command is given. All runs are read-only one-liners with the main venv; the editable packages of the main tree were imported (same code as this branch for these files).
- **document**: taken from a text, not re-checked.
- **reading of this review, not decided**: my own reading.

Short names: `H` = `app/handlers/blueprint_handlers.py`, `W` = `app/modules/wrangle_studio.py`, `N` = `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py`.

What the owner wants is quoted only from `ORDER.md` or from a DECIDED ledger line taken by EVE (number and words). Anything else is "document" or my reading.

---

## 1. What the owner asked (her words)

| Source | Her words |
|---|---|
| `ORDER.md` (M421) | "that it is an ide (visual) that help the user create recipes for production : with the actions and parameters available (depending on the engine used ...)" and "see how it is possible to use the wrangling engine and plotting engine to help a user to write recipes, with the lineage" |
| `ORDER.md` (M423) | "explore what we had planned, what is existing, many things will need to be anyway verified and updated" |
| D-0306 (EVE, DECIDED) | Decision text: "Blueprint is the UI IDE for building the recipes and must be able to build the WHOLE recipe; it was never finished as it should have been. Tier 1 AND tier 2 must be buildable." |
| D-0308 (EVE, DECIDED) | "Blueprint must be able to build as the recipe specification says; the normal logic of building is to start with tier 1, then tier 2, then tier 3, then the plot; the tool builds a functional recipe and advises the user against mistakes; the user needs to be able to see, for each step of the recipes, where it sits." |
| D-0309 (EVE, DECIDED) | "The Blueprint design is revisited before Blueprint is built: the lineage and the tube map are also to be leveraged" |
| D-0063 (EVE, DECIDED) | "The T3 is the data that goes to the plot BUT not the plot recipe" (Blueprint may author the plot entry's tier 3) |
| D-0143 (EVE, DECIDED) | "Blueprint edits recipes for creation. Audit add steps to a copy of an original_recipe : the audit_recipe" |
| D-0102 (EVE, DECIDED) | "Full recipe edit is only in blueprint" |
| D-0348 (EVE, DECIDED) | "we take blueprint afterwards - that will also be easier because then we know what we can reuse from the home design" |

---

## 2. The user's journey in plain words

**Who.** A person who knows the data and the question, not a programmer ("a user who understands their data and what they want to do with it can build a complete data analysis recipe with zero Python/R knowledge", `spaces/BLUEPRINT.md`, document). In the app BLUEPRINT exists only where `blueprint_enabled` is on: the setups `standalone`, `developer` and `qa` (read: `config/app_features/*.yaml`, flags at lines 11 to 29).

**Starting from what.** One of three starts (document: `developer_workflow.md:180-183`, ADR-082):
- an existing recipe from the recipe list;
- an empty recipe made by "+ New" in BLUEPRINT;
- a boilerplate made by Test Lab (a zip of a recipe with tables and declared fields), opened in BLUEPRINT; or a Gallery example copied by hand.

**Ending with what file.** A recipe of format 1: one main YAML file (`<id>.yaml`, the `id` equals the file name, D-0007) plus a folder of the same name with the included files (tier files, plot files, field files). For a production recipe the file name is `name_date` (D-0390: "A recipe file name is name_date, exactly."; D-0393: "The new dated file is for a final save").

**Saved where.** Decided: "A place where the user can read and write is needed, possibly different from the common recipes place" and "Only specific users may modify the common recipes" (D-0393). Today: BLUEPRINT reads and writes the fixed folder `config/data_analysis_recipes/pipelines` (read: `H:975`, `H:2685`), not the deployment's recipes location; it overwrites files in place with no backup (read-1: `H:1188`). The places are under study (D-0394; `prior_work/recipe_places/`).

**The steps, with what BLUEPRINT does today.**

| # | What the user wants to do | Today | Label |
|---|---|---|---|
| 1 | Start a recipe: name, description, engines, entity | "+ New" asks id, name, description, author and writes a stub with `info.label`, the two default engines, no table, no join, no plot (`H:2638-2722`, `new_recipe.py`). The stub passes profile `build` with one advice (no contact) and fails profile `run` (T09: no plot), so HOME cannot open it yet. "+ New" answers only when the agent switch is on (section 3). No control for engines, entity, contact | read-1; run: `new_recipe_draft("demo_x", "Demo", description=..., author=..., created=...)` then `check_recipe(..., "build")` and `"run"` |
| 2 | Add a table: its file, its fields and types, the entity key | No control. A table comes from Test Lab's boilerplate, a branch copy, or is written by hand | read-1 (`02` F1) |
| 3 | Tier 1 of each table | Pick an action, fill the form, Apply, see the data; works on an existing tier file. No visible Save; one step cannot be removed or moved (only "Clear All nodes"); no undo control | read (Save hidden: `W:248-258`; `_undo` no caller: `H:376`, grep); run 2026-11-18 (document: `prior_work/BLUEPRINT_T1_T2_PROOF.md`) |
| 4 | Joins | The Joint Designer previews a key match on real data and adds a `polars_join` step to the list in memory; the join file cannot be saved ("Editable roles: plot_spec, wrangling") | read (`H:608-611`) |
| 5 | Tier 2 | Editable only when the tier-2 file exists (reached from the lineage rail); no control creates a tier-2 file except a branch | read-1 (`02` B, F1) |
| 6 | Tier 3 (data steps for one plot) | No control. BLUEPRINT keeps a plot entry's `tier3` when it saves the plot (`H:574-579`) but cannot show or edit it. New since step 1: the engine reads tier 3 (`orchestrator.py:669`, `materialize_tier3`) and the checker no longer refuses it ("P05 is retired: the engine reads `tier3`", `recipe_check.py:1136-1137`); so the gap is BLUEPRINT's only. The button "Add plot wrangling" of D-0305 is not in the code (grep in `app/`: none) | read |
| 7 | Groups (the HOME tabs) | "+ Group", delete an empty group, move and delete a plot; agent switch needed | read-1 (`H:2280-2523`) |
| 8 | Plots: target table, mapping, layers, labels, theme | "+ Plot" writes an empty plot file; mapping and layer forms exist for an opened plot; no control for the target table, `ui_title`, the plot engine. No picture of the plot (section 3) | read-1; read (`W:714`, no `output_plot` in BLUEPRINT) |
| 9 | Plot defaults | Palette and theme, "Apply to session"; never written to the file; agent switch needed | read-1 (`H:1716-1771`) |
| 10 | Check | "Run validation": three checks merged into pass or fail, with profile `run` | read (`H:2843-2845`, `data_analysis_recipe_validator.py:401`) |
| 11 | Save | See step 3 and section 4 | read |
| 12 | See it run in HOME | After a save, HOME's gate is run again for that recipe and the author is told (`tell_save_outcome`, `H:279-293`) | read-1 |

Reading of this review, not decided: the journey that the decisions describe (D-0306, D-0308) and the journey the code allows overlap only at steps 3, 8 (editing what exists) and 12.

---

## 3. The parts of the IDE

State words: **planned** (a text says it should exist; nothing built), **reachable** (built and a user can use it), **unreachable** (built but no user can reach it), **missing** (planned and not built), **partly** (built with a gap named).

### 3.1 How BLUEPRINT is mounted (it touches every part)

- In `H.define_server`, the line `if not bootloader.is_enabled("blueprint_agent_enabled"): return` stops the registration of everything after it (read: `H:1690-1691`). After it come: the plot-defaults form, the agent chat, the whole Joint Designer, the groups and plots inventory, the info form, the "+ New" dialog, Validate, the draft status and the import error panel (read-1: `H:1716` to `H:2933`).
- Effect: in `standalone` (BLUEPRINT on, agent off; read: `config/app_features/standalone.yaml:13-17`) these panels are mounted by `W` and stay empty. Not seen on a screen (not run).
- The rule says "All BLUEPRINT capability remains gated by `blueprint_enabled`" (ADR-082, document). Contradiction L18 of `02`.

### 3.2 The parts

| Part | What it is for the user | Planned by | State | Evidence |
|---|---|---|---|---|
| TubeMap | The map of the recipe: tables, a "Wrangle" node per table, joins, plots; click to open | ADR-039, ADR-082 L1 | reachable; partly: empty places, tier 3 and a table's tier 2 are not drawn; clicking a source table may load another table's data | read-1 (`M:41-45`, `H:1029-1075`); run 2026-11-18 (document) |
| Lineage rail | The chain of the selected part, source to plot | ADR-040 | reachable, in tab 2 (not in the right sidebar the UX spec names); some tables twice | read-1 (`W:1431`); run 2026-11-18 (document) |
| Contract viewer | Upstream, component, downstream columns | ADR-040 | partly: downstream is always empty ("No downstream contract.") | read-1 (`H:679-755`, `W:1612`) |
| Field gap analysis | Trace a field through the loaded tiers | ADR-082 | reachable (not examined) | read-1 |
| Action picker | Search and pick an action; filter by context | ADR-075 | reachable; contexts offered: t1, t2, assembly, plot; the registry gives actions the contexts t1 (46), t2 (65), assembly (36), none "t3"; the picker does not filter by engine (section 4 and `05`) | read (`W:333-359`); run: catalog filled as `app/src/server.py:39-42` does, then counted |
| Tier of a new step | Where the step goes | D-0308 ("see ... where it sits") | partly: chosen by the context list ("T2" gives tier 2, all else tier 1), not shown on the step card; a step of the wrong tier is refused at Save (provisional, D-0308) | read (`W:802-808`, `H:589-592`) |
| Form renderer | A form per action, built from the registry's `ui_schema` | ADR-075 | reachable: 58 of 68 actions carry parameters, all 68 a `yaml_example`; 188 of 191 components carry parameters | run (same catalog count) |
| Column pickers | Offer the columns available at that place | ORDER (parked item), D-0308 | partly: they offer the declared `input_fields` of the table, not the columns after earlier steps, not the right table after a join | read-1 (`W:1979-2003`, `H:677-759`) |
| Typed values `{name, params}` | A parameter that is a library object | D-0277 | missing | read-1 |
| Joint Designer | Two tables side by side, key match on real data, a join step | ADR-082 Q5 | partly: preview and Apply work; the join cannot be saved; agent switch needed | read (`H:608-611`); read-1 (`H:1924-2277`) |
| Groups and plots inventory | Create, move, delete groups and plots | ADR-082 Q6 | partly: no rename, no order; agent switch needed | read-1 |
| Info form | Recipe name, description, author | ADR-082 | partly: reads and writes `info.name`; format 1 uses `info.label`; the checker accepts `info.name` without a word, so the form's edit does not change the label the app shows | read (`H:2542`, `H:2610`); run: `check_recipe` of the draft with `info.name` added, profile `build`: only I02 |
| Plot defaults form | Palette and theme of all plots | VIZFAC-BLUEPRINT-FORM-1; D-0246 | partly: session only, never saved; agent switch needed | read-1 |
| Tier 3 form and the "Add plot wrangling" button | Data steps for one plot | D-0063, D-0305 | missing | read (grep) |
| Data glimpse | The table after the step, on Apply | ADR-082 Q1, Q7 | reachable (may show another table's data on some clicks) | read-1; run 2026-11-18 (document) |
| Plot preview | The picture of the plot being built | ADR-082 L3 "DONE", UX spec zone C | unreachable: the render function `architect_active_plot` exists (`W:714`) and no `ui.output_plot` mounts it (grep: `output_plot(` only in `home_theater.py`) | read |
| Validate | Check before saving | ADR-082, ADR-094, ADR-100 | partly: three checks in one pass or fail, with HOME's profile `run`; one check parses markdown text of a child process; no mark on the map nodes; agent switch needed | read (`H:2843-2868`) |
| Warnings distinct from errors | "Blueprint shows all warnings" | D-0079 | not checked | - |
| Open a failing recipe, point to each fix | Asked by the owner, "investigate, no build yet" | ledger, asked not decided | partly: the view is blanked and the problems listed; no fix list | read-1 (`H:389-400`) |
| Save of a step list | Write the tier file | ADR-082 | unreachable: the Save button sits in a `display:none` box (`W:248-258`); tests press it by script | read |
| Save of info, groups, plots | Write the main file | ADR-082 | reachable (agent switch needed); rewrites the file, no backup | read-1 |
| New recipe | "+ New" | ADR-082 BP-NEW-1 | reachable (agent switch needed); refuses a hyphen in the name (`H:2636`) | read |
| Branch | Split a lineage at a node | ADR-082 Q3 | reachable only with `data_analysis_recipe_edit_enabled` (developer, qa); writes empty tier-1 fragments | read-1 (`H:1470-1665`, `N:914`) |
| Undo | Take back the last change | ADR-075, ADR-082 "DONE" | unreachable: `_undo` (`H:376`) has no caller | read |
| Remove or move one step | Edit the list | ADR-040, ADR-075 | missing (only "Clear All nodes") | read-1 (`W:379`); run 2026-11-18 (document) |
| YAML escape hatch | See the YAML; edit it in developer setups | ADR-075 | partly: its own Save writes nothing to disk | read-1 (`H:1424-1462`) |
| Autosave of a draft | Restore after a reload | ADR-082 §2a | reachable where `automation.ghost_save.enabled` (off in `qa`) | read-1 |
| Download and upload | A zip of the recipe; upload replaces | ADR-082 | reachable; upload "would replace silently" (study, document) | read-1 |
| AI agent chat | Ask the agent | ADR-076 | see `07_ai_agent_planned_vs_existing.md`: the panel is reachable in `developer`, but every message fails today | read, run |
| Undeclared file columns | Tell the recipe maker which file columns the recipe leaves out | D-0374 ("informing here I think needs to be done for blueprint") | missing in BLUEPRINT; the ingestion already computes the list and prints a console warning (`libs/ingestion/src/ingestion/ingestor.py:147`, seen when the app module is imported) | read; run (import of `app.src.server` printed it) |
| Warning on a cast to integer | Warn the recipe maker | D-0376 ("the recipe maker gets at least a warning") | missing | read-1 |

---

## 4. What a production recipe requires today, and what BLUEPRINT respects

The format is recipe format 1 (`recipe_format_spec.md`; amended 2026-11-17, D-0236: "Format 1 is amended before its first release; no format 2"). Profiles of the one checker: `run` (HOME), `build` (BLUEPRINT and data-only recipes; empty placeholders accepted), `gallery`, `audit` (read: `libs/utils/src/utils/recipe_check.py:60`; document: spec line 230 "`build` | Blueprint (building step by step)").

| Requirement of format 1 | Source | BLUEPRINT today | Label |
|---|---|---|---|
| `spec_version: 1`, `id` equal to the file name | DEC, D-0007 | New recipe writes both; the id is typed (snake case only) | run (draft keys) |
| `data_engine` and `plot_engine` at the top | D-0029, D-0219 | New recipe writes the first engine of each list; no control to choose | run; read (`recipe_factory.py:161-162`) |
| A tier is its own key: optional `data_engine`, then `steps` | D-0250 | Save writes `{data_engine (kept if the file had it), steps}` | read (`H:603-607`) |
| Prefixed action names (`polars_`, `modif_`, `step_`) | D-0036 | Respected: the picker lists the registry, all 68 names prefixed (65 `polars_`, 2 `modif_`, 1 `step_`) | run |
| Canonical step: `action:` key, quoted `'on'`, `right_ingredient` | rules | Save writes `{"action": ..., params...}`; the join step is built by `join_designer.build_join_step` but cannot be saved | read (`H:593-594`); read-1 |
| Published columns: the last step of tier 1 is a plain `polars_select` | D-0034 | Not known to BLUEPRINT: no hint, no check at Save; the user adds `polars_select` like any action | read-1 (no such logic found) |
| `info.label` required; `description`, `contact` advised | spec, checker I01, I02 | New recipe writes `label`; the info form writes `name` (accepted by the checker, ignored by the app) | read; run |
| `entity`, `is_entity_key` on the sample id; the id is text | D-0029, D-0225 | No control | read-1 |
| `input_fields` with Polars type names | D-0035, D-0057 | No control (no field editor) | read-1 |
| `ui_label` on groups and plots; `ui_title` optional | D-0253 | Groups and plots made by BLUEPRINT get `ui_label`; no `ui_title` control | read-1 (`group_plot_manager.py:95`) |
| Figure text only in the `labs` layer | D-0253 | The layer form can add `labs`; no guidance | read-1 |
| A plot entry has no `spec:` key | DEC51, D-0252 | Save writes the entry's own keys, then the content | read (`H:574-579`) |
| Plot component names `plotnine_`, `modif_`, `step_` | D-0091, D-0210 | Not built anywhere yet: 191 components, none prefixed; BLUEPRINT writes the old names like everything else | run |
| Typed values `{name, params}` | D-0277 | No widget | read-1 |
| Comments kept by every tool | D-0174 ("a)": keep the comments) | Violated: Save rewrites the file from the step list | read-1 (`H:1188`) |
| A step `comment` key is text | checker CM01 (`recipe_check.py:711`) | Save writes `comment` when not empty; the run of 2026-11-18 saw the file name written as the comment of untouched steps | read; document |
| No `audit_steps` / `audit_comment` in an original recipe | D-0332 (checker `audit` profile) | Save refuses a file that holds audit steps | read (`H:600-602`) |
| A recipe that runs in HOME has at least one plot | checker T09 (`run`) | A new recipe has none and cannot be opened in HOME until a plot is added | run |
| File name `name_date` for a final save; upload under an existing name refused | D-0390 to D-0393 | No dated save; the new-recipe name refuses a hyphen | read (`H:2636`) |

Reading of this review, not decided: the save path follows the decided shape for the parts it can write; what it cannot write (joins, tier 3, fields, entity, engines, `ui_title`, typed values, the dated final file) is the larger gap, and the comment loss is the one place it changes a file against a decision.

---

## 5. The boundaries to the other user spaces

| Boundary | What is decided or written | What the code does | Label |
|---|---|---|---|
| HOME: BLUEPRINT never authors an audit | D-0143: "Blueprint edits recipes for creation. Audit add steps to a copy of an original_recipe : the audit_recipe"; D-0102 "Full recipe edit is only in blueprint" | Save refuses a file with audit steps; nothing in BLUEPRINT writes `audit_steps` | read (`H:600-602`, comment at `H:623`) |
| HOME: the recipe's tier 3 is not HOME's audit | D-0305 (reading of the review session in the line: the button text must keep "tier 3 (the last data step before the plot)" apart from HOME's audit), D-0306 "T3 : data plot specific" | Not applicable yet (no tier-3 form) | read |
| HOME: what happens after a save | GATE-GAP-1 (document) | HOME's gate is rerun for the saved recipe and the author is told | read-1 |
| HOME: a recipe changed while in use | S2-3-Q, investigation only (document) | Nothing locked | read-1 |
| Test Lab | Stateless toolbox; the boilerplate is a zip opened in BLUEPRINT (`developer_workflow.md:180`); single-key matching only, composite keys belong to BLUEPRINT's Joint Designer (`rules_test_lab.md` section 5) | BLUEPRINT opens a recipe from the list or an upload; no direct hand-off | document |
| Gallery | No in-app hand-off; copy the YAML by hand (ADR-093); a gallery example is a recipe in profile `gallery` | No Gallery code in BLUEPRINT | document |
| The pattern helper | Shared with Test Lab (`libs/utils/src/utils/id_patterns.py`) | Not used by BLUEPRINT | read-1 |

---

## 6. What must be verified and updated before any rebuild

Each line: what, why, how to verify. Nothing here was changed.

| # | What | Why | How to verify |
|---|---|---|---|
| V1 | Which controls work with the agent switch off | `H:1690` stops their registration; never seen on a screen | Start the app with `SPARMVET_APP_FEATURES=standalone`, open BLUEPRINT, press each left-sidebar control; or a browser test |
| V2 | The Save of a step list as a user would do it | Hidden button; run of 2026-11-18 only by script | Browser: open a tier file, change a step, look for a Save control; compare the file before and after (comments, added `comment:` lines, `data_engine`) |
| V3 | What a save changes in a file with no edit | D-0174 asks to keep comments; the 2026-11-18 run saw changes | Save an untouched tier file; `git diff` the file |
| V4 | The node click that loads another table's data | Known defect, not re-checked (BLUEPRINT-NODE-CLICK-WRONG-TABLE-1) | Click each source node of `1_test_data_ST22_dummy`; compare the glimpse with the file |
| V5 | Whether the Validate profile should be `build` | Spec says `build`; code uses `run` (`H:2844`) | Read `recipe_format_spec.md` section on profiles with the owner's decisions; run Validate on the new-recipe stub |
| V6 | The count of components with parameter forms, by kind of parameter | ADR-082 says 7 of 191 in May; today 188 carry `params` (run), but whether each form can be filled without code is unknown | Open a form per component family in the browser; list params with no widget |
| V7 | Whether the picker's "plot" context lists components and where a component step goes | "Plot" gives tier 1 for actions (`W:807`) | Read `get_components_for_context` and the add-node path; browser |
| V8 | The second load path and the Apply handler | Not read (`H:845-894`, `H:1199-1385`) | Read them |
| V9 | The text documents that say "done" or "never tier 3" | Stale texts mislead the rebuild | Re-read `app/src/help/blueprint.md`, `docs/workflows/blueprint_architect.qmd`, `rules_ui_dashboard.md` section 7, ADR-082 state column, `spaces/BLUEPRINT.md` "Current State" against this file (list in `03` section 3) |
| V10 | The UML diagrams of BLUEPRINT | Never compared with the code | `./.venv/bin/python assets/scripts/audit_uml_model.py --project-root .`, then compare the four BLUEPRINT diagrams with sections 3 and 4 |
| V11 | The tests that pin BLUEPRINT's known defects | `test_shiny_blueprint_known_defects.py` records defects as tests | Read the test file and list which defects it pins |
| V12 | The recipe list of BLUEPRINT against the deployment's recipes location | Fixed folder (`H:975`) | Start with a deployment whose recipes location is elsewhere; compare HOME's list and BLUEPRINT's |
| V13 | The upload that "would replace silently" | D-0390 refuses an upload under an existing name | Upload a recipe with an existing name in BLUEPRINT |
| V14 | Which parts of HOME's new design BLUEPRINT can reuse | D-0348 ("we know what we can reuse from the home design") | After the HOME refactoring: list HOME's shared modules (lineage walk, plan composer, side-panel mechanism D-0381, the message forms) and match each with a part of section 3 |
| V15 | That a hyphen in a recipe name works through the whole app | D-0391 ("To verify before building") | The study verified discovery, gate, checker, tiers, cache names (document); still to run: browser, sessions, export, audit folder |

---

## Not verified

- Nothing was seen on a screen in this review; the only browser runs are of 2026-11-18 (`prior_work/BLUEPRINT_T1_T2_PROOF.md`), on a tree that has changed since.
- Rows marked read-1 rely on the step-1 reading; the files did not change, but I did not re-read every line.
- Whether the plot preview, undo or a visible Save exist under another id or in JavaScript: I searched the Python of `app/` only.
- Warnings and errors looking distinct in Validate (D-0079): not checked.
- The count "58 of 68 actions carry parameters" counts entries with a non-empty `params`; actions without parameters may need none.

## To decide (for the guide)

Each is open; the options are those the records name, plus mine where marked.

| # | Choice | Options | Pros | Cons |
|---|---|---|---|---|
| 1 | How a whole recipe starts and how a table enters it | (a) Test Lab boilerplate, then BLUEPRINT; (b) a table and field editor in BLUEPRINT; (c) a branch copy of a table | (a) exists, one tool per job; (b) the whole recipe in one place (D-0306); (c) exists | (a) two spaces, a file hand-off; (b) new work, overlaps Test Lab's inference; (c) only copies |
| 2 | Which controls may depend on the agent switch | (a) only the chat (ADR-082, flag rule); (b) as built | (a) matches the rule and the "switch off with no effect" wish recorded in the options document | (b) hides most of BLUEPRINT in `standalone` |
| 3 | Which profile BLUEPRINT's checks use | (a) `build` (spec); (b) `run` (code); (c) both, shown apart (my reading) | (a) lets a recipe be built step by step; (b) says whether HOME will open it; (c) both answers | (a) does not say HOME will refuse it; (b) flags every unfinished recipe as failing; (c) two lists to read |
| 4 | What a step of the wrong tier does | refuse (provisional today), two files, no tier picker, guide the order (D-0308 reading) | see `02` K6 | see `02` K6 |
| 5 | Whether BLUEPRINT ever blocks | ADR-100 "never blocks building" against the Save refusal and ADR-075 "invalid positions blocked" | - | - |
| 6 | Where the columns of a picker come from | (a) declared fields (today); (b) the plan of every place (HOME's `plan_composer`, D-0325 excluded BLUEPRINT from that choice); (c) the stored tables | (b) the real names and types after each step, no build | (b) needs the data files and a recipe that runs up to that place; (c) needs a build |
| 7 | The tier-3 form | build it, with the button text of D-0305 | the engine now reads tier 3 | the text must keep it apart from HOME's audit |
| 8 | Where BLUEPRINT reads and writes recipes, and what a final save is | the models M1, M2, M3 of the study; P1 to P11 (D-0394) | - | - |
| 9 | What a save may change in a file | keep comments (D-0174 decided; needs a writer that keeps them, a library question) | decided | a new library needs her yes |
| 10 | The info key the form edits | `label` (format) against `name` (form) | - | - |
| 11 | Where the user sees the tier and the file of each step, empty places, tier 3 | map nodes per tier, a tier word on each card, the rail (no option written in the records; `prior_work/GLOBAL_PICTURE.md` section D) | D-0308 asks for it | - |
| 12 | How the plot is built in BLUEPRINT: target, title, engine, picture | open (D-0305: "a need stated, NOT decided") | - | - |
| 13 | Where the undeclared columns and the cast warning are shown | step form, Validate, the glimpse (D-0374, D-0376 say where is not decided) | the ingestion already computes the undeclared list | a cast warning needs the data |
| 14 | The names: "BLUEPRINT", "Blueprint Architect", "Wrangle Studio", `WrangleStudio` | one word for the space (CLAUDE.md section 1 asks to keep space and module words apart) | - | a rename touches tests and ids |
