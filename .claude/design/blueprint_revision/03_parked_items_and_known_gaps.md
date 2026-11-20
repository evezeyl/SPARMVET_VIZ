# BLUEPRINT-REVIEW-1, step 1c: parked items and known gaps

Written 2026-11-20 night by a worker of BLUEPRINT-REVIEW-1. Reading only; builds nothing, decides nothing (D-0395). Labels as in `02_planned_vs_existing.md`: `[R]` read in the code at file:line (tree `dev` at `4bc3ebac`), `[D]` taken from a document. `H` = `app/handlers/blueprint_handlers.py`, `W` = `app/modules/wrangle_studio.py`.

The order (`ORDER.md`) says: "Also parked items about BLUEPRINT go into the guide (the column pickers that follow the lineage, the warning when values are cast to integer, the undeclared file columns D-0374)." The three are item 1 to 3 below, with the others the task named.

---

## 1. The parked items, one by one

### 1.1 The column pickers that follow the lineage

- **Source.** The sentence of the order above (the order's text, M421). I found no ledger line, no task and no design file that describes it further (grep of the ledger, `tasks.md`, the design folder, the handoff). The related decisions are: D-0308 ("the user needs to be able to see, for each step of the recipes, where it sits"), D-0309 ("the lineage and the tube map are also to be leveraged"), D-0325 (the columns of every place are found by the plan of the engine; "Blueprint is out of this choice") and the HOME audit's tick lines (D-0194, D-0316, D-0346, D-0347), which HOME already has.
- **What the code does today [R].** A column picker in a step form offers the columns of `active_upstream` (`W:1979-2003`, `_extract_upstream_cols`). `active_upstream` is set at load time by `_do_load_component` (`H:677-759`): for a table's tier file it is the declared `input_fields` of that table (`H:683-688`); for a join it is the list of ingredients with no fields (`H:691-697`, comment: "Recipe format 1 has no published-fields file of an ingredient ... the ingredients are listed without fields"); for a plot it is `resolve_fields_for_schema` of the target (`H:722-728`).
- **Consequence [reasoned from the code].** A step at tier 1 or tier 2 cannot pick a column that an earlier step made (a `polars_with_columns`, a `polars_rename`, a join), and a step after a join cannot pick the right table's columns. Two types of the same column name (before and after a cast) are not told apart; the type used for "numeric" or "categorical" is the declared one.
- **Not known.** How the tier 1, tier 2, tier 3 and the join pickers should show the columns of each place; whether the same plan composer as HOME (`app/modules/plan_composer.py`) should feed them (it needs the data files and builds lazy frames; BLUEPRINT works on a recipe that may not run yet). The choice is open (`02` K5).

### 1.2 A warning when values read from a file are cast to integer

- **Source.** D-0376 (2026-11-20), the note for BLUEPRINT: "when values of a data file that is read are cast to integer, the recipe maker gets at least a warning". Task `BLUEPRINT-CAST-TO-INTEGER-WARNING` (`tasks.md:885`): "not built (note of D-0376, for when BLUEPRINT is done)". The HOME part (the filter box takes whole numbers for an integer column) is a separate decision.
- **What the code does today [R].** No such warning. The cast steps (`polars_cast`) are ordinary steps of the form; a Polars cast of a decimal to an integer is a Polars behaviour (the project rule: "No hidden choice", D-0036). The "Validate" panel and the checker advices (J12, J13) do not mention it [R: `H:2897-2903` reads advices from `checker_advices`; the codes concerned are not about casts; I did not read all of the checker's advices].
- **Not known.** Where and in what words: at the step form, in Validate, in a data check against the file (a warning only when the data is read, because only the data tells whether a decimal is there). D-0376 says "at least a warning".

### 1.3 Informing about file columns the recipe does not declare

- **Source.** D-0374 (2026-11-20): "In HOME nothing is told to the user about columns of a data file that the recipe does not declare: the recipe imports only what it needs. Informing about undeclared file columns belongs to the user space BLUEPRINT. ... BLUEPRINT part: DECIDED, not built." Task `BLUEPRINT-UNDECLARED-COLUMNS` (`tasks.md:880`): "Not started; where and in what words is not decided." Her words are in the evidence field of the ledger line.
- **What the code does today [R].** The strict import in the loader refuses an `input_fields` slug that is not a column of the file (D-0034; `rules_agent_role_bioscientist.md` 3-A). The opposite direction (file columns the recipe leaves out) is not reported anywhere in BLUEPRINT's code: `validate_data_analysis_recipe_data` checks the declared against the file (`H:2884`); `load_fields_file` reads the declared fields only (`N:589`) [R].
- **Not known.** Where it is shown (the table's form, Validate, the data glimpse), and whether it is a list the user can turn into declarations (a table editor does not exist yet: `02` F1).

### 1.4 BLUEPRINT reads and writes a fixed recipe folder, not the deployment's

- **Source.** Task `BLUEPRINT-RECIPES-FOLDER-IGNORES-DEPLOYMENT` (`tasks.md:751`, recorded 2026-11-19, "Verified by reading (a reviewer)"), `BLUEPRINT-RECIPE-LOCATION` (`tasks.md:646`), `BLUEPRINT-SAVE-COMMENTS-1` (`tasks.md:697`, "Blueprint reads its recipe list from the fixed folder"); the study `tmpAI/panel/recipe_places/TABLE_FOR_THE_OWNER.md` (main tree, git-ignored, 2026-11-20 night), flag 5 and the architect's finding 2: "HOME reads the deployment's recipes location (`bootloader.get_location`, bootloader.py:185). BLUEPRINT lists and writes the hard-coded `config/data_analysis_recipes/pipelines`".
- **What the code does today [R].** The list of recipes: `Path("config/data_analysis_recipes/pipelines")` at `H:975`; a new recipe: the same folder at `H:2685`, created with `mkdir(parents=True, exist_ok=True)`. Relative paths: they depend on the folder the app starts in. HOME's list comes from the deployment (task lines; `bootloader.py:185` [D, not re-read here]). The upload and bundle import have their own paths (`H:1117-1150`).
- **What the study says [D].** The app cannot tell users apart (no login); the three models M1 (common place read-only for the app, own recipes in the user-data folder), M2 (M1 plus a dated final save into the common place by a maintainer's app), M3 (one place only); "M1 first, then M2 on top of it"; four steps that are safe whatever she chooses, the fourth being "BLUEPRINT reads the deployment's recipe folder instead of a fixed one". Her decisions P1 to P11 are open.
- **Also found [R].** The deployment guide says the recipes location is read-only for the app (ADR-091 gap 1, `docs/deployment/deployment_guide.qmd`), while BLUEPRINT writes there.

### 1.5 BLUEPRINT's save overwrites in place, against the dated final version and the user's own place

- **Source.** D-0390 (a recipe file name is `name_date`; an upload under an existing name is refused), D-0391 (ISO date; "To verify before building: that a hyphen in a recipe name works through the whole app"), D-0392 (production recipes only), D-0393 (the dated file is for a final save; a typo edit may replace the previous file; only specific users may modify the common recipes; a place the user can read and write is needed; "NOT decided: what counts as 'modified' for a session"), D-0394 (an overwrite control only in the user's own directory; one study). ADR-091 gap 1 and CONFIG-STEPS-WRITE-1 (backup, then a draft copy and an explicit publish).
- **What the code does today [R].** Save rewrites the component file with `open(comp_path, "w")` (`H:1188`), the info save rewrites the master file (`H:2630`), group and plot changes write the master; none keeps a backup or a dated copy. There is no "save final version" action, no copy to an own place, no overwrite warning. After a save the app re-runs HOME's gate for the changed recipe and says what it means for HOME (`tell_save_outcome`, `H:279-293`): a gate-gap fix (GATE-GAP-1), not a version rule.
- **What the study says [D].** A dated copy of an unchanged recipe is a new recipe for the machine (the fingerprint includes the file name); a recipe is several files, so a dated version must copy every file it reads; "remove the old file by hand" is possible only for someone who reaches the folder; "Save final version (dated)" is the words the user viewpoint proposes; the data of P7 (what identifies a recipe) and P8 (a dated version is self-contained) decide what a save must do. The default recipe is the first of an unsorted list (a small fix needed whatever is chosen).
- **Related decisions not built.** D-0174 (a save keeps the comments), with BP-COMMENTS-1 "not started" and a library question for the owner (ruamel.yaml); BLUEPRINT-SAVE-COMMENTS-1: a save also writes `comment: <file name>` into each step and drops the comment lines, so a save with no edit changes the recipe file and with it the stored tables' keys and the session (the owner's order: "never overwrite what matters silently", ADR-091 gap 1).

### 1.6 The new-recipe name rule refuses a hyphen

- **Source.** The study (flag; architect, line 20): "The one place that refuses a hyphen: BLUEPRINT's typed new-recipe slug `^[a-zA-Z_][a-zA-Z0-9_]*$` (blueprint_handlers.py:2636). It can STAY: the user types `amr`; the app adds `_YYYY-MM-DD` itself." D-0391 asks to verify that a hyphen works through the whole app.
- **What the code does today [R].** `_SLUG_RE_NEW` at `H:2636`; the message says "Data analysis recipe ID must be snake_case" (`H:2677-2682`). The slug is the recipe `id` and the file name (D-0007). A name with a date `name_2026-11-20` cannot be created by this dialog.
- **Verified by the study [D].** A hyphen works through discovery, the load gate, the checker, tier 1, a join, tier 3 and the cache file names. Not run: the browser, session save and restore, the export, the audit folder.
- **Not decided.** Whether the id (inside the file, "must equal the file name", ADR-092 / D-0007) carries the date; whether BLUEPRINT adds the date or the user types it (D-0390 to D-0392 say the rule covers the actions "final save" and "upload into the common place").

### 1.7 The old prefix-less plot component names

- **Source.** `rules_viz_factory.md` section 1a: "the rule is DECIDED (D-0091, D-0210, D-0218). The rename is NOT built yet. Today the registered names have no prefix. The examples in this file and in the recipes still show the old names until the rename task is done." Task V1-B-RENAME (`tasks.md:387`): "DECIDED in principle 2026-11-15 (M107); starts only after Eve has seen the impact list." ADR-106 and the note of 2026-11-15: no old name is accepted after the rename ("did you mean").
- **What the code does today [R].** 193 plot components are registered, none with the prefix `plotnine_` or `modif_` (a count of the registering lines in `libs/viz_factory/src`). BLUEPRINT's picker, the form headers, the plot nodes, the user guide (`geom_bar`, `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:297`) and the agent instructions (`config/ui/agents/blueprint_default.md:162`, `:187`) use the old names. The agent's tool `get_available_components` returns the registry's names, so it will follow the registry after the rename, while the instructions text will not.
- **What a rename costs BLUEPRINT [reasoned].** Every place that writes a component name: the picker, the serialiser of the plot (`H:553-570`), the plot defaults form (the theme names), the typed values `{name, params}` (D-0277), the help, the user doc, the agent text, the tests that name `geom_*` (e.g. `app/tests/test_blueprint_plot_preview_engine.py` not read). The impact list that the rename waits for ("starts only after Eve has seen the impact list") is `.claude/design/viz_rename_impact_2026-11-15.md` (exists; not read here).

### 1.8 Others named in the sources

- **Informing the user (all spaces):** join counts (JOIN-COUNTS-1, provisional), warnings that look different from errors (WARNINGS-LOOK-1; D-0059, D-0079); the 2026-11-1x channel note (main tree, `tmpAI/agent_channel.md`, "Warnings against errors, today (user viewpoint, READ)"): "in Blueprint's Validate an error row and an advice row use the same yellow box; only the heading differs" and "Advices other than J12 and J13 are hidden and the user is not told". Whether this is still so was not checked [D].
- **Open a recipe that fails and show each failing point as a point to fix** (her design wish, "investigate, no build yet"; BP-STALE-VIEW-1, options A, B, C; the choice not made).
- **The seed field linked to the steps that use jitter, changed only in audit and BLUEPRINT** (ledger "asked, not decided", line 436): open.
- **Named themes with a form in BLUEPRINT** (PROPOSAL-NAMED-THEMES-BLUEPRINT; D-0256 "Themes are code" narrows it); the plot-defaults theme fields (BP-FORM-THEME-FIELDS, after the demo).
- **A recipe changed while in use** (S2-3-Q): BLUEPRINT saves while HOME may have the recipe open; `tell_save_outcome` tells the author what the gate now says, nothing is locked.
- **Config review** (CONFIG-REVIEW-1, D-0303): the flags that BLUEPRINT depends on (the agent flag problem, `02` A) belong to it.
- **The recipe-to-Python research with the BLUEPRINT agent** (PY-RESEARCH, "start only after the visualisation library is done").

---

## 2. Known defects and gaps (from the tasks, the 2026-11-18 runs and my reading)

State: **R** = I confirmed it by reading in this tree; **D** = taken from a document, not re-checked; **fixed** = a later commit fixed it (name the commit).

| # | Defect or gap | State | Evidence |
|---|---|---|---|
| 1 | Most BLUEPRINT controls (Joint Designer, group inventory, info form, new recipe, Validate, plot defaults, draft status, import error panel) are registered only when `blueprint_agent_enabled` is on; in `standalone` the outputs are mounted and empty | R | `H:1690-1691`; `W:200-238, 451` |
| 2 | The Save button is in a `display:none` box; no visible Save for a step | R (the only mount I found); the run of 2026-11-18 saw no visible Save either | `W:248-258` |
| 3 | A join built in the Joint Designer stays in memory; a join file cannot be saved (the serialiser refuses the role) | R | `H:2266`, `H:609-611` |
| 4 | The plot preview output is not mounted in any page | R | `W:713`; `output_plot` only in `home_theater.py` |
| 5 | No control calls `_undo`; the in-app help and the rules say undo exists | R | `H:376`, no caller |
| 6 | One step cannot be removed or moved; the only control is "Clear All nodes" | D (run 2026-11-18); R: the single control found in `W:379` | `W:379` |
| 7 | A new step's tier comes from a dropdown "context" (t2 gives tier 2; assembly, plot and empty give tier 1); a step for the wrong file is refused at Save | R | `W:802-808`, `H:592` |
| 8 | The Save refusal contradicts "BLUEPRINT never blocks building" (ADR-100) and is "provisional" (D-0308) | R / D | `H:592`; `blueprint_tier_refusal.py` |
| 9 | Save drops `#` comments (and, by the task, writes `comment: <file name>` into each step); the info save and group/plot saves also rewrite whole files without a backup | R for the dump (`H:1188`, `H:2630`); D for the `comment:` part | `H:1188`, `H:2630` |
| 10 | The info form reads and writes `info.name`; the format and the new-recipe draft use `info.label` | R | `H:2544`, `new_recipe.py:23` |
| 11 | Validate uses the checker profile `run` (HOME's), not `build`; one of its checks parses markdown text and counts "factory_id key" violations (a removed concept) | R | `H:2844`, `H:2866`, `data_analysis_recipe_validator.py:401` |
| 12 | The three-column contract viewer's downstream column is empty (`out_fields = []`); the card says "No downstream contract." | R (paths read) | `H:679, 687, 695, 727, 755`; `W:1612` |
| 13 | The plot defaults form changes the session only; the in-app help still lists font, spacing and legend | R | `H:1742`, `app/src/help/blueprint.md:17-25` |
| 14 | The agent prompt names `propose_data_analysis_recipe_diff`, which no code registers | R | `agent_context.py:183-198` |
| 15 | The CLI adapter sets no restriction on the CLI's own tools; `claude_api` and `local` fall back to "disabled" | R | `agent_adapter.py:272-280`, `:398-403` |
| 16 | The agent probe at start may wait up to 40 seconds with no message | D | AGENT-PROBE-1 |
| 17 | Tapping a source table node loads another table's data (the steps of the clicked node are applied to another table's data) | D (run 2026-11-18, "also on dev") | BLUEPRINT-NODE-CLICK-WRONG-TABLE-1 |
| 18 | A fresh draft has no plot and the loader refuses a recipe without a plot; a new recipe cannot be opened in HOME | D (one strict xfail test records it) | task line 220 |
| 19 | The groups and plots can be created but not renamed or reordered; delete refused for a group with plots | D (digest 2026-11-18) | `group_plot_manager.py` |
| 20 | No control for: adding a table; a field's type, label or entity key; a plot's target table, title and engine; the recipe's `entity`; the engines; contact; creating a tier 2 file except through a branch | R by absence of any such input in `H` and `W`; D (the gap report lists the same) | `02` F1 |
| 21 | Tier 3 cannot be built or seen; the button "Add plot wrangling" of D-0305 is not there | R | no "tier3" input in `H`/`W`; `H:575-579` passes the key through |
| 22 | The action picker is not filtered by engine, and a plot step made under "plot" context is a tier 1 step | R | `schema_registry.py`; `W:802-808` |
| 23 | The in-app help for `step_` and `modif_` is not written (deferred by the owner, D-0266) | R | `app/src/help/blueprint.md` |
| 24 | `docs/workflows/blueprint_architect.qmd` has no prefixed action names, and states "BLUEPRINT never writes Tier 3" as a hard invariant | R | file lines 104, 146 |
| 25 | The expression code editor with autocomplete (BP-EXPR-EDITOR-1) was not found in `W` | R by a grep for "autocomplete" | - |
| 26 | The count of components with a `ui_schema` (7 of 191 in May) is not known now | not checked | - |
| 27 | The names: "Wrangle Studio", "WrangleStudio", "Blueprint Architect", "BLUEPRINT" are four words for one thing in the UI value, the class, the title and the rules | R | `H:972`, `W:114`, `home_theater.py:1811` |
| 28 | `app/tests/test_join_preview_parity.py` says the join rule "lives twice"; the code now has one function | R | test docstring lines 3-4 |
| 29 | Fixed since the 2026-11-18 reports | - | plot open: `5892a872`; the join step name: `b6b40c40`; the plot defaults form: `ea8c1738`; the navigator on the recipe graph: `fb37c514`, `ecd09fbd` |

---

## 3. Texts that are out of date (to verify and update; nothing was changed here)

| Text | What is wrong | Evidence |
|---|---|---|
| `app/src/help/blueprint.md` | plot defaults keys that no longer exist; an undo that has no control; an agent that "requests changes" | section 2 items 5, 13, 14 |
| `.claude/rules/rules_ui_dashboard.md` section 7 | "never authors T3" (line 188); the editable hatch "emits a `developer_raw_yaml` T3 node on save" (line 203); the edit/remove layers (line 202) | D-0063; AUDIT-RAWYAML-REMOVE-1; `_undo` |
| `.claude/knowledge/architecture_decisions.md` ADR-082 | state column of May; "60 actions"; "Q2 never authors T3" (marked superseded); "BLUEPRINT capability remains gated by `blueprint_enabled`" | `02` A, L |
| ADR-039 (status "PROPOSED"), ADR-040, ADR-075, ADR-076 | headers carry "Partly stale (2026-11-14)" notes; the ADR-040 viewer columns name removed keys | the files |
| `.claude/design/spaces/BLUEPRINT.md` "Current State (verified 2026-05-20)" | out of date; and "Gaps" list is of May | the file |
| `.claude/knowledge/blueprint_architect_ux_spec.md` | `output_fields`, `final_contract`, rail in the right sidebar | `02` L17 |
| `.claude/design/developer_workflow.md:89` | `final_contract` | ADR-100 |
| `docs/workflows/blueprint_architect.qmd` | see item 24 | - |
| `.claude/tasks/tasks.md` entries | BP-FORM-FIX, BLUEPRINT-PLOT-DEFAULTS-FORM-1 (fixed), BLUEPRINT-GLOBAL-PICTURE-1 and the plot-builder study (the products exist in `tmpAI`) | `01` section 5 |
| `docs/UML/app.mdj` BLUEPRINT diagrams | not checked against the code (the audit script was not run) | `01` section 8 |
| The agent text `config/ui/agents/blueprint_default.md` | plot component names; the missing tool | item 14, section 1.7 |
| `app/tests/test_join_preview_parity.py` docstring | one function now | item 28 |

---

## 4. Findings in the design-review and audit logs

- `.claude/logs/audits/` (406 files): the files that mention BLUEPRINT are routine audits (`audit_deps_*`, `audit_templates_weekly_*`, `audit_2026-04-19` to `2026-05-21`, `audit_uml_model_2026-11-08`) that name BLUEPRINT as a file, a flag or a node; I found none that is a design review of the space. I did not open all of them. [D]
- `.claude/design/exploration/`: the files that mention BLUEPRINT are `2026-11-17_engine_fields_plan.md` (finding 5: the plot-defaults form replaced the whole `plot_defaults` and lost seed, font, spacing, legend; fixed by `ea8c1738`; and finding 1: "The export does not hand `plot_engine` to the plot library", HOME and the BLUEPRINT preview do), `2026-11-17_engines_default_and_override.md` (an R snippet in a recipe: "all four say no" because the checker, BLUEPRINT and the audit could not see into it), `2026-11-17_recipe_arguments_without_code.md` (BLUEPRINT's object widget: "form code not read", 2 to 3 days a guess), `2026-11-17_theme_snippets_design_note.md`, `2026-11-16_one_recipe_many_datasets_sessions.md` ("Not checked by the viewpoints: ... the Blueprint side"), `2026-11-18_test_lab_review.md`, `2026-11-18_date_keys_and_joins.md`, `2026-11-18_step_split_wide_design.md`, `2026-11-17_author_manifest.md`. One line each was given in `01` section 1. [D]
- Main tree `tmpAI/` (git-ignored): the gap report and the global picture of 2026-11-18, the browser proof, the recipe places study, `agent_channel.md` (notes of the other sessions). `01` section 9 lists them. They hold the only runs of BLUEPRINT.

## 5. The size of the two modules against the rules [R]

| File | Lines | What the rule says |
|---|---|---|
| `app/handlers/blueprint_handlers.py` | 2941; one function `define_server` from line 310; 16 `@render.*` and 32 `@reactive.Effect` | `rules_app_structure.md` section 2: "(~2800 lines)", section 5: a handler exposes one entry point `define_server` and holds one concern ("One concern per file"); the only hard limit written is for `server.py` (about 250 lines). The file holds about twelve concerns: import, upload, selection, save, download, escape hatch, branch, agent chat, plot defaults, Joint Designer, groups inventory, info form, new recipe, Validate, draft status |
| `app/modules/wrangle_studio.py` | 2328; class `WrangleStudio`; its method `define_server` runs from line 543 to 1929 (about 1390 lines); 20 `@render.*` and 6 `@reactive.Effect` | The rule lists it in `app/modules/` ("~2360 lines, the largest module") where modules "may import Shiny for UI-helper classes (by design, app layer only)"; the Two-Category Law puts `@render.*` in `app/handlers/`. For the Test Lab the rule forbids exactly this in the module (`rules_test_lab.md` section 6); for `WrangleStudio` no sentence forbids or permits it |
| `libs/blueprint_arch/src/blueprint_arch/` | 4631 lines in 14 files; the navigator alone 1151 | pure logic, no Shiny: respected by the imports I saw; `blueprint_mapper` header says it consumes `utils.recipe_graph` |

For comparison [R: `wc -l`]: `app/handlers/home_theater.py` 2573, `app/handlers/export_handlers.py` 2260. The tests: `app/tests/test_blueprint_*.py` and `test_shiny_smoke_blueprint.py`, 2370 lines in 14 files; `libs/blueprint_arch/tests/` 13 test files.

## 6. What I could not find or verify

- A written line for "the column pickers that follow the lineage" beyond the order's sentence (1.1).
- The register that BLUEPRINT-AFTER-RECIPE-1 points to (`01` section 10).
- Whether a Save in the running app keeps or drops `comment` lines, and whether it adds `comment: <file name>` to each step: taken from the tasks and the 2026-11-18 run.
- The agent chat with the switch off or on, a real tool call, the second load path (`H:845-894`), the Apply handler body (`H:1199-1385`): not read in detail.
- The files `tmpAI/engine_keys/TIER3_facts_2026-11-18.md`, `step4_REVIEW.md`, `step4_fixes_report.md`, `blueprint_plot_open_report.md`, `.claude/design/viz_rename_impact_2026-11-15.md`: named, not read.
- Whether the UML diagrams of BLUEPRINT match the code.
