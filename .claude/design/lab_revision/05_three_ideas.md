# TESTLAB-REVIEW-1, step 3: the three ideas of the task (pilot recipe, tool-specific recipe, combined recipes)

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396: "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)"). It studies what each idea could mean and how large a decision it is. It designs nothing and decides nothing.

## Summary (10 lines)

1. The three ideas are one line in `tasks.md:347`: "extract a pilot recipe (reconstruct a lineage), a tool-specific recipe (for example a single-sheet variant), combine recipes (format detection, common datasets, branching)". The order asks to place them in the guide "by size of decision" (the relaying session's sentence, `ORDER.md`).
2. They are older than the recipe format: first written on 2026-05-05 as three "TO DISCUSS: lab script" lines about "manifests" (the old word for a data analysis recipe), from the owner's own git account. No ledger line describes them. What she meant is not written anywhere; this file gives readings, not her intent.
3. Idea 1, "extract a pilot recipe": most likely reading, cut out of a large recipe the part one plot, one group or one tool's results need, by walking the lineage back, and write it as a smaller recipe to reuse. Other readings exist (section 2).
4. Idea 2, "a tool-specific recipe (single-sheet variant)": most likely reading, a recipe for the results of one bioinformatics tool (one table, or one sheet of a workbook); the shipped recipes already keep their fields per tool (`ResFinder_input_fields.yaml`, ...).
5. Idea 3, "combine recipes": merge two or more recipes into one, finding the tables they share, recognising which files have the same shape, and branching where they differ.
6. Much of what they would need exists: the recipe graph and its lineage queries, the export's frozen one-file recipe, BLUEPRINT's branch plan, the recipe writers, and a hand-made example (`1_Abromics_general_pipeline.yaml` reuses the fragment files of the ST22 recipe).
7. All three write NEW recipes. They meet the same open decisions: where a new recipe is saved and how it is named (D-0390 to D-0394), whether a copy shares or copies the fragment files (a shared fragment changes two recipes at once), and the rule that a plot id is unique over all recipes (checker X5).
8. By size: idea 2 is the smallest (it can be one more mode of the scaffold or a documented recipe pattern); idea 1 is medium (a new writer, the recipe places, the plot ids); idea 3 is the largest (name clashes, joins, entity keys, BLUEPRINT's role).
9. Ideas 1 and 3 are recipe authoring. D-0102 says "full recipe edit exists only in Blueprint"; whether writing a new recipe out of existing ones is "edit" is to decide, and so is whether they belong in the Test Lab, in BLUEPRINT, or in a script.
10. Nothing here asks the owner a question now; section 5 lists what is to decide.

## How to read this file

Labels: **read** = I read it now (2026-11-21), file:line, in this worktree (branch `task/lab-review`); **read-1** = from step 1 (`01`, `02`, `03` of this folder), not re-read; **document** = a text, not checked against the code; **git** = from the git history (command given); **reading** = my reading, not a fact and not decided. What the owner wants is quoted only from `ORDER.md` or from a ledger line that is DECIDED and taken by EVE.

---

## 1. Where the three ideas are written

| When | Where | Text | Label |
|---|---|---|---|
| 2026-05-05 06:39 | commit `652ee833`, file `.antigravity/tasks/tasks.md` (the task list of that time), under "REVIEW tasks - design discussions needed (2026-05-04)"; the commit's author is the owner's own git account | "TO DISCUSS: lab script : extract pilot manifest (reconstitution of lineage) - improve reusability (eg manifest for results from specific tool)" / "TO DISCUSS: [lab script] create tool specific manifest (eg a single sheet) variant of above" / "TO DISCUSS: lab script: combine manifest -> format - detection common datasets, branching..." | git: `git log -S "create tool specific manifest" --all`; `git show 652ee833` |
| 2026-05-05 07:13 | commit `835081f5` ("fix: tasks recovery") | rewritten: "Extract pilot manifest (reconstitution of lineage) — improve reusability (e.g. manifest for results from a specific tool)"; "Create tool-specific manifest (e.g. single-sheet variant of above)"; "Combine manifests — format detection, common datasets, branching" | git: `git show 835081f5` |
| 2026-11-13 | `tasks_before_sort_2026-11-13.md:347-349`; `tasks_backlog_details_2026-11-13.md:108-118` | "manifest" replaced by "data analysis recipe"; then the three lines "merged into TESTLAB-IDEAS-1" and into TESTLAB-REVIEW-1 | read |
| 2026-11-13 to now | `tasks.md:347` (TESTLAB-REVIEW-1) | "which of these ideas are wanted: extract a pilot recipe (reconstruct a lineage), a tool-specific recipe (for example a single-sheet variant), combine recipes (format detection, common datasets, branching)" | read |
| 2026-11-18 | `.claude/design/exploration/2026-11-18_test_lab_review.md:174` | names them, item 15, "After items 1 to 12, not before" | read |
| 2026-11-20 | `ORDER.md` (relaying session's text, not her words) | "The ideas already in the task (extract a pilot recipe, tool-specific recipe, combine recipes) are to be placed in the guide by size of decision." | read |

What these sources establish:
- "manifest" is the old word for a data analysis recipe (ADR-091 vocabulary note: "manifest -> **data analysis recipe**", `architecture_decisions.md:5`, read). So all three ideas are about recipes.
- "lab script" places them in the Test Lab, or in scripts of the lab, in May 2026 (reading: "script" may mean a command-line script, like those of `assets/scripts/`, not a screen).
- The May lines were committed from the owner's account, so they are likely her notes; they are not ledger lines, so they are quoted here as a document and never as her decision.
- "variant of above" ties idea 2 to idea 1: a tool-specific recipe is a kind of extracted recipe (reading).
- The parenthesis of idea 1 in May, "eg manifest for results from specific tool", ties idea 1 to idea 2 again.
- Nothing else in the repository describes them: no design file, no ledger line, no ADR (read-1: `01` section 10; grep now over `*.md`, `*.qmd`, `*.py`, `*.yaml` for "pilot recipe", "pilot data analysis recipe", "single-sheet", "tool-specific recipe", "combine recipes", "reconstruct a lineage" finds only `tasks.md`, the two outdated task files and the review of 2026-11-18).

---

## 2. Idea 1: extract a pilot recipe (reconstruct a lineage)

### 2.1 What it could mean (readings; her intent is not written)

| Reading | In plain words | Why it fits the words |
|---|---|---|
| 1a. Cut out | From a large recipe, keep only what one plot, one group of plots, or one tool's table needs: walk the lineage back from the plot to its source tables, keep those tables, their tiers, the joins on the way and the plot; write a smaller recipe that runs alone | "reconstitution of lineage", "improve reusability", "results from specific tool" |
| 1b. Rebuild from results | From the result files of a pipeline run, rebuild the recipe that would read them, using the fragments that already exist for each tool (the `input_fields` of ResFinder, MLST, ...) | "reconstitution", "results from specific tool" |
| 1c. Recover from an export | From an export bundle, recover the recipe that made a figure (the export already holds a frozen one-file recipe) | "reconstitution of lineage" |
| 1d. "Pilot" as a first trial | A small first recipe to try a new data set before the full one | the common meaning of "pilot" |

Reading 1a is the closest to the words "reconstruct a lineage"; 1b and 1d are possible; 1c is partly built already (2.2). The word "pilot" is not defined in any source.

### 2.2 What exists that it could use

| Part | What it does | Label |
|---|---|---|
| The recipe graph (`libs/utils/src/utils/recipe_graph.py`) | one model of a recipe; `lineage_back`, `lineage_forward`, `plots_reading`, `source_tables`, `source_tables_of_plot`; no file read, no data built | read: lines 1-30, 195-238, 448-467 |
| `build_plot_lineage` (`libs/blueprint_arch/.../data_analysis_recipe_navigator.py:694`) | the backward trace from a plot to its sources, as a list of steps; used by the export | read: lines 694-712; `export_handlers.py:1642` |
| The export's frozen recipe | with the reproducibility box ticked, the bundle holds `data_analysis_recipes_reproducibility/<id>.yaml`: the whole resolved recipe in one file, audit steps written in, the plot seeds written in | read: `export_handlers.py:1497-1509`, `960-966` |
| BLUEPRINT's branch plan (`generate_branch_plan`, navigator line 933) | splits one lineage in two at a node: upstream shared by the same `!include`, the new part written as new empty files | read: lines 933-975 |
| The recipe writers (`libs/utils/src/utils/recipe_factory.py`) | write recipe text in format 1, keys in order, `!include` kept; "A tool that changes an existing recipe file edits its text, so that every comment of the author is kept" | read: lines 1-20 |
| A hand-made example | `1_Abromics_general_pipeline.yaml` is a smaller recipe whose tables include the fragment files of the ST22 recipe (`!include '1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml'`) | read: lines 17-30 |
| The checker (`recipe_check.py`) | checks a recipe in profile `build` or `run`; X5: "a plot id must be unique over all of them (the app registers plots by id)" across the recipes of a folder | read: lines 1287-1296 |

### 2.3 What it would need

- A writer that takes a recipe, a chosen plot or group or table, and writes a new recipe with only the parts on the lineage (none exists; reading: the graph gives the parts, the factory gives the writer).
- A choice between COPY and SHARE of the fragment files. Sharing (as the Abromics example does) keeps one definition; but a change to the shared fragment changes both recipes, and their results, at once. Copying keeps each recipe fixed; two copies can drift. The goal text says "nothing changes a result silently"; a shared fragment edited for one recipe changes the other's result with no word to its users (reasoning).
- New plot ids, or a rule for them: the checker refuses the same plot id in two recipes of one folder (X5, read).
- A place and a name for the new recipe: D-0390 "A recipe file name is name_date, exactly."; D-0393 "A place where the user can read and write is needed, possibly different from the common recipes place"; D-0394 "ONE study by the architect, the data scientist and the user viewpoints covers together: the common recipe place against each user's own place" (decision fields, read). The study is in the BLUEPRINT review's prior work.
- The data: an extracted recipe points to the same source files; the data are not copied (reading).
- The entity key, the engines, `plot_defaults`, `info` (contact, version): carried over or asked.

### 2.4 Size of the decision

Medium. It touches: the recipe places and names (open study, D-0394); the plot-id rule (X5); share against copy (reproducibility); where it lives (Test Lab, BLUEPRINT, script). It does not need a change of the recipe format (reading: a cut-out recipe is a normal recipe of format 1).

### 2.5 Options

| Option | Pros | Cons |
|---|---|---|
| A. Not wanted | nothing to build or keep | a user who wants one plot of a large recipe copies files by hand, as was done for the Abromics recipe |
| B. A Test Lab tool: pick a recipe and a plot or group, download a smaller recipe (copies, new plot ids) | a file hand-off like the other tools; one job | the Test Lab then reads recipes (against the code comment of 2026-11-08, `home_theater.py:1955-1957`, read-1) |
| C. A BLUEPRINT action next to "branch" | BLUEPRINT already holds the lineage, the branch plan and D-0102's recipe edit | BLUEPRINT is not finished (its own review); a larger space |
| D. A command-line script in `assets/scripts/` | small; for developers; the scaffold scripts are already there | not for a scientist without a terminal |
| E. Document the export's frozen recipe as the way to "recover" a recipe (reading 1c) | exists | one file, the whole recipe, no cut-out |

---

## 3. Idea 2: a tool-specific recipe (for example a single-sheet variant)

### 3.1 What it could mean (readings)

| Reading | In plain words | Why it fits |
|---|---|---|
| 2a. One bioinformatics tool | A recipe for the results of ONE tool (ResFinder, MLST, Quast, ...): its table, its fields, its cleaning, a few standard plots; any user with that tool's output can use it | May text: "manifest for results from specific tool"; the shipped fragments are per tool |
| 2b. One sheet of a workbook | When a pipeline gives one Excel workbook with a sheet per tool, a recipe (or a recipe variant) that reads one sheet | "eg a single sheet" |
| 2c. One Test Lab tool | A recipe that a Test Lab tool writes for its own purpose (for example the recipe of a synthetic data set) | "tool-specific" inside a Test Lab task; weakest reading |

Readings 2a and 2b can be the same thing seen from two sides: one tool's results, delivered as one sheet.

### 3.2 What exists that it could use

| Part | Fact | Label |
|---|---|---|
| Fields kept per tool | `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/` holds `ResFinder_input_fields.yaml`, `MLST_input_fields.yaml`, `Quast_input_fields.yaml`, `Bracken_input_fields.yaml`, `FastP_input_fields.yaml`, `VirulenceFinder_input_fields.yaml` and others | read (`ls`) |
| A recipe reusing them | `1_Abromics_general_pipeline.yaml` (MLST, VirulenceFinder, a reference list, metadata) | read: lines 17-60 |
| Templates | `config/data_analysis_recipes/templates/` (`simple_template.yaml`, `complex_template.yaml`, `e_coli.yaml`, `left_join_lesson.yaml`, `audit.yaml`) | read (`ls`) |
| Sheets to TSV | the reformatter (one TSV per sheet), the extractor (a sheet, key renamed `id`), `ExcelHandler` | read-1: `02` F |
| Source types of the format | `local_tsv`, `local_parquet` only: a recipe cannot read an Excel sheet directly | read: `libs/utils/src/utils/recipe_spec.yaml:36-38` |
| The scaffold | writes a recipe from data files (one per table) | read-1 |

### 3.3 What it would need

- For 2a: a decision that per-tool recipes are a kind of recipe the project ships (a "library" of tool recipes, reading), where they live, how they are named (D-0390 to D-0394), who keeps them current when a tool changes its output columns.
- For 2b: the sheet must become a TSV first (the format reads no Excel, read); so a "single-sheet variant" is the reformatter or the extractor, then the scaffold or a tool recipe. Whether the format should read Excel directly is a format decision (`recipe_spec.yaml` source types), outside the Test Lab.
- For both: a way to recognise that a file IS a given tool's output (column names), which is the "format detection" of idea 3 (reading).

### 3.4 Size of the decision

Small to medium. 2b is small (a documented chain: reformat, then scaffold or apply a tool recipe). 2a is medium if it means shipping and maintaining recipes per tool (places, names, maintenance), small if it means a template pattern. Neither needs a change of the recipe format unless Excel is read directly.

### 3.5 Options

| Option | Pros | Cons |
|---|---|---|
| A. Not wanted | - | - |
| B. Templates per tool (recipes in `templates/`) built from the existing fragments | uses what exists; no new code | maintenance of each template; plot-id uniqueness across templates (X5) |
| C. A scaffold mode: "one tool's file" that writes the tool's known fields and checks the columns | the user starts from known fields, not guessed types | needs a list of known tools and their columns |
| D. Read an Excel sheet as a source in the recipe format | no conversion step | a format change; outside the Test Lab |
| E. Document the chain (reformat a sheet, then scaffold) | nothing to build | two tools, two downloads |

---

## 4. Idea 3: combine recipes (format detection, common datasets, branching)

### 4.1 What it could mean (readings)

| Reading | In plain words | Why it fits |
|---|---|---|
| 3a. Merge recipes | Put two or more recipes together into one: find the tables they share (for example the same metadata), keep one copy of each, and branch where they diverge | "combine", "common datasets", "branching" |
| 3b. Assemble from known parts | Given new data files, recognise each file's format (which tool made it), find the existing recipe parts that read that format, and put them together in one recipe | "format detection", "common datasets" |
| 3c. Combine data, not recipes | Join the data of several runs or several tools into one table | "common datasets"; weaker, because the words say "combine manifests" |

### 4.2 What exists that it could use

| Part | Fact | Label |
|---|---|---|
| Same table, as text | `RecipeGraph.same_t1_definition(table_a, table_b)`: "True when two tables have the same definition up to their tier 1, as the TEXT of the recipe"; it "says nothing about the content of the files, and it must never be used alone to share a stored table: the data hash decides that (D-0025)". Within one recipe today | read: `recipe_graph.py:240-256` |
| Branching | BLUEPRINT's branch plan (2.2) | read |
| Joins | BLUEPRINT's Joint Designer (key match on real data); the Test Lab's single-key ID reconciliation | read-1 |
| Type detection | the bootstrapper's guess from the first 100 rows; the reformatter's sheet and delimiter handling | read-1 |
| Recognising a tool's output | nothing (no list of tools and their columns in code) | reading: grep finds none |
| Lineage across tables | the recipe graph, the lineage walk of HOME's audit (`lineage_walk.py`, D-0347) | read: header of `lineage_walk.py` |

### 4.3 What it would need

- Names: table ids must be unique inside one recipe and plot ids unique over all recipes (X5): two merged recipes with a table `MLST` each, or the same plot ids, clash (reading from read X5).
- A rule for "the same table": same text (graph) and same data (hash, D-0025), or the user says so.
- Joins between the merged parts: on which key, of which type (the entity key is declared, D-0082 "Keys are declared in the recipe"; D-0225 "never a number"); joins are designed in BLUEPRINT (ADR-084 point 5, read-1).
- Format detection: a list of known formats (tools and their columns) to keep and update.
- A place and a name for the result (D-0390 to D-0394), and what happens to the sessions and audit recipes of the source recipes (a session belongs to one recipe: "Restore of a session saved against another recipe is refused", `ui_implementation_contract.md` section 12d, document).

### 4.4 Size of the decision

Large. It touches the recipe names and ids, the joins and keys (BLUEPRINT's domain), the recipe places and names, sessions and audits of the source recipes, and a new store of known formats. It is the most "recipe authoring" of the three, so D-0102 ("full recipe edit exists only in Blueprint") weighs most here.

### 4.5 Options

| Option | Pros | Cons |
|---|---|---|
| A. Not wanted | - | a user combines recipes by hand (copying fragments), as the Abromics recipe shows |
| B. A BLUEPRINT feature, after BLUEPRINT's rebuild | joins, branch and lineage live there | waits for BLUEPRINT; large |
| C. A Test Lab tool that only REPORTS (which tables two recipes share, which plot ids clash), and the user combines in BLUEPRINT | informs, does not choose (D-0015); small | does not write the combined recipe |
| D. A script for developers | small | not for scientists |
| E. Format detection alone (reading 3b) as a scaffold help: "this file looks like ResFinder output" | helps J5 of `04`; links to idea 2 | needs the list of known formats |

---

## 5. The three ideas side by side

| | Idea 2: tool-specific | Idea 1: extract a pilot | Idea 3: combine |
|---|---|---|---|
| Size | small to medium | medium | large |
| Recipe format change | no (yes only if Excel is read directly) | no | no, but names and keys clash |
| Recipe places and names (D-0390 to D-0394) | yes, if recipes are shipped per tool | yes | yes |
| Plot ids unique over all recipes (X5) | yes, for templates | yes | yes |
| BLUEPRINT | no | possibly (branch next door) | yes (joins, D-0102) |
| Share or copy fragments | yes (templates from fragments) | yes | yes |
| Uses what exists | fragments per tool, templates, reformatter | graph, plot lineage, export's frozen recipe, writers | graph `same_t1_definition`, branch plan, Joint Designer |
| Clearest reading | 2a or 2b | 1a | 3a |

Reading, not decided: idea 2 and the format-detection part of idea 3 help the Test Lab's own journeys (J1, J5 of `04`): they turn "files" into "a recipe that knows these files". Ideas 1 and 3 work on recipes that already exist, which is BLUEPRINT's ground by D-0102 and D-0306; the Test Lab could inform (report what two recipes share) without writing.

## Not verified

- What the owner meant by the three lines: nothing written says it. The readings are mine.
- Whether the May lines were typed by the owner or by an agent working under her git account (the author field is her account; the file was edited by hand and by agents at that time).
- Whether the recipe graph and `same_t1_definition` work on two recipes at once (written for one recipe; not run).
- Whether the export's frozen recipe opens in HOME or BLUEPRINT as it is (not run).
- Whether a recipe may `!include` fragments of another recipe's folder in every place the app reads recipes (the Abromics recipe does it and is shipped; the gate and BLUEPRINT were not run on it here).

## To decide (for the guide)

| # | Choice | Options | Pros | Cons |
|---|---|---|---|---|
| 1 | Which of the three ideas are wanted | none, some, all; in which order (by size: 2, 1, 3) | the order follows the size | - |
| 2 | Where recipe-making tools live | Test Lab, BLUEPRINT, scripts; or Test Lab reports and BLUEPRINT writes | Test Lab: file hand-off, one job; BLUEPRINT: recipe edit (D-0102) | Test Lab reading recipes reverses the 2026-11-08 choice in the code |
| 3 | Share or copy fragment files between recipes | share (one definition), copy (fixed recipe), or copy with a note of the origin | share: no drift; copy: no silent change of the other recipe | share: one edit changes two results; copy: drift |
| 4 | Plot ids in a derived recipe | new ids written by the tool; ids prefixed by the recipe; the X5 rule revisited | - | X5 exists because the app registers plots by id |
| 5 | Per-tool recipes shipped with the app (idea 2a) | yes, as templates; no | a scientist starts from known fields | maintenance per tool |
| 6 | Read an Excel sheet directly in the recipe format (idea 2b) | yes (format change); no (convert first) | no conversion | a format change, outside the Test Lab |
| 7 | A list of known formats (tools and their columns) for detection (ideas 2, 3) | keep one; none | helps the scaffold | must be kept current |
