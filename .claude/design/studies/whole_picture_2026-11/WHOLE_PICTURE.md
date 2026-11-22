# The whole picture: how HOME is meant to work (2026-11-22, version 5: built backwards from your goals, second pass)

A study, not a decision: nothing is built from it before you answer (D-0507, D-0528).

> **START HERE**
>
> 1. Read part 0: your goals, whether each is reached, the path, the route of the work, what must be modified, what the evidence shows, and your questions now. About twelve minutes, with one table and one sketch.
> 2. Then answer question 28, then 1, 29, 17 and 4 (part 8, group "Now, from your goals"). Each is written so that you can answer it without reading the rest.
> 3. Question 2 (the recipe form) when you want tables as results and the one move of the demo recipes. It does not block the audit.
> 4. Everything else can wait.
>
> Parts 1 to 9 are the earlier study (version 3), kept as background: they describe the dialog as decided, which is option (c) of question 28. The detail and the evidence of part 0 are in `GOALS_REVIEW.md`.

---

## 0. Your goals, and how to get there (the goals review, second pass)

**How to read this part.** Your words are between quotation marks, exactly as you typed them; the number after them is their line in the decision ledger. "My reading" and "mine" mark what is not yours. "Suggestion:" comes before a remedy.

**Words used here.**
- The **entity**: what one value of the entity key names. On the demo recipe it is a sample, and the key is `sample_id`.
- An **observation**: a row of a table (my reading of your word).
- A **tier**: a stage of a table in the recipe. Tier 1 cleans a table (and joins it with the metadata); tier 2 computes; tier 3 is the table a result is made from.
- The **lineage**: the path of a table, from the original data files to the results.
- A **place**: one table at one tier, where an audit step can be written. Its **reach**: the tables and results that depend on it.
- The **audit recipe**: the copy of the recipe that holds your audit steps; the original recipe never changes.

The detail is in `GOALS_REVIEW.md`. It also covers the six places you agreed to add (D-0529): trust in the whole result, the author and the user, BLUEPRINT, the help, where the app runs, and how you will know a goal is reached.

### 0.1 Your passage (D-0528)

> "What i want is to make allow the user to make audits in an clear, scientifically correct , reproducible and transparent way, 7 want to provide a tool the user can use to do good data science and help provide visualisations it can use for publication (incl. Tables an plot) it can trust, and audit is done to allow making small correction to results where some "observations" must be removed. I want to know how to get there, and then our current code needs to be adapted, which implies reviewing decisions or changing strategy that hoder to get there. This includes recipe structure and how we perform the audit steps and how it is presented clearly with the necessary information so the user can make informed and good choices. Our role is to provide the tool, the reproducibility, transparency, reliability - however we cannot take choices for the user because it depends on the user context. I want the whole picture to be reviewed again and adapted to my goals. I want to go how to succeed at making the app to reach my objectives and then i need to know what needs to be modified (from our plans already planned and from current code - eg. What build are ok and what needs to be adjusted)"

### 0.2 Your goals, and whether they are reached

From your passage (the review session read six goals in it; I checked each against your words):
- **G1.** Audits that are clear, scientifically correct, reproducible and transparent.
- **G2.** A tool for good data science.
- **G3.** Results for publication, plots and tables, that the user can trust.
- **G4.** The audit is for small corrections: removing some observations.
- **G5.** Each choice shown clearly, with the information needed to choose well.
- **G6.** The app gives the tool, the reproducibility, the transparency and the reliability; the choice is the user's, "because it depends on the user context" (D-0528). And since: "We cannot choose for him..the app cannot decide the scope" (D-0531).

From earlier decisions, one line each:
- **E1.** "No silent error that is the rule." (D-0050)
- **E2.** "Sorry do not get wrong results because we did not select the correct scope" (D-0450)
- **E3.** "remember we are data agnostic so sample id is the example" (D-0512)
- **E4.** "well the problem is that the user might not be the author" (D-0500)
- **E5.** "YES the story of is what I want to show - this is why I wanted the lineages" (D-0508)
- **E6.** "We aim for one source of truth." (D-0065)
- **E7.** "I would prefer to have the big line done as fast as possible" (D-0521)

Some of your goals pull against each other; I do not resolve them (`GOALS_REVIEW.md` 2.4).

**Is each goal reached?** "Today" is the app on `dev` on 22 November. "As decided" is your decisions, once built. The last column is my reading.

| Goal | Today you see | As decided, once built, you would see | Still missing (my reading) |
|---|---|---|---|
| G1 | A step only at the open plot's table; the export has no original and no audit recipe. | Each step in the audit recipe, at the places you tick; a fingerprint; an export with an original and an audited part. | The effect on each result, before you confirm (0.6, point 1). |
| G2 | A step always comes after everything: a removed entity still counts in a mean computed earlier. | You can tick a place before such a computation. | A line that says which places come before it. |
| G3 | What you see is exported. Plots only. Only the audited picture is exported. | Tables as results; the original and the audited picture both exported. | How many observations each result lost. |
| G4 | Filters and column drops; a Reshuffle button with no reason. | The same; the Reshuffle becomes a step (how: not decided). | Drops and the Reshuffle remove no observation (questions 29, 17). |
| G5 | "This plot only / All plots / All plots except"; no lineage. | The lineage as a propagation; a line per place with its reach; "table changed" and "picture changed" per plot. | The effect as a number; the screen words (question 19). |
| G6 | Starts on "This plot only": a builder's choice. | You tick places; your default is named. | Which places are "the earliest" (question 1). |
| E1, E2 | A plot whose table lacks the column is skipped, with a line. | Red lines where the app cannot follow a column. | A removal that misses a result is seen only if measured (0.6). |

### 0.3 The path (mine): the scope stays yours, and the app measures the effect

**The principle.** You choose the scope: the places in the lineage where a step is written. The app does not choose it (D-0531). The app shows you the lineage, what each place reaches, and the effect of your ticks on each result, measured before you confirm. A default is named as a default, with its reason, and you can change it. The only place the app fills in by itself is "Remove from all the data", and only when you ask for it.

**The path, on the demo recipe.**
1. Open the recipe: every table is built and every result drawn once. [built]
2. Look, in Exploration: a result, its table, its earlier stages, and any table by its name. Nothing is saved. [built, except "any table by name"]
3. Find a bad entity: on the demo, sample `10668076`, whose sequencing failed.
4. In Audit mode, from the table where you see it, ask to remove it, with a reason.
5. The dialog shows the lineage as a propagation, one line per place with its reach. Your default, the earliest places, starts ticked and is named on screen (question 1).
6. Under the lines, the measured effect on each result: "n observations removed" or "unchanged"; where it happens, "still found here" or "the values of other observations change here". Each change of a tick is measured again.
7. Confirm. The step goes into the audit recipe at the places you ticked, with its reason. The log keeps the places, ticked by default or by you, and the effects shown.
8. Check with Compare; take any one step out with "Remove step".
9. Export: the audited results with the originals beside them; a report with the observations removed from each result, and why; the log; the original and the audited reproducibility parts.

```text
+-- Create audit step -----------------------------------------------------+
| Remove the rows where sample_id = 10668076                               |
| Reason: [ sequencing failed, lab notes of 12 April                     ] |
|                                                                          |
| Where the step is written (ticked: your default, the earliest places)    |
|   original files -> tier 1 -> tier 2 -> results                          |
|  [x] MLST, tier 1                             reach: n tables, n results |
|  [x] metadata_schema, tier 1                  reach: n tables, n results |
|  [ ] MLST_with_metadata, end of tier 1        reach: n tables, n results |
|  [ ] this result only: mlst_bar               reach: 1 result            |
|  ... one line per place of the lineage                                   |
|  [ ] Remove from all the data (off; it lists every table first)          |
|                                                                          |
| Effect on each result, measured on the audit recipe:                     |
|  mlst_bar                      n observations removed                    |
|  year_distribution             n observations removed                    |
|  qc_reads_horizontal_barplot   still found: 1 observation, with its      |
|                                source, year and country now empty        |
|  ... one line per result that changes                                    |
|                                              [ Cancel ]   [ Confirm ]    |
+--------------------------------------------------------------------------+
```

This screen does not exist yet; "n" is a number the app would count. The effect lines come from three runs on the demo, one entity each, with the places listed by hand (part 6.1): with this default the entity stayed in 7 plots, and in 3 of them its source and country were emptied, because a left join keeps the row of its first table.

**The choices that are yours:** question 28 (places first, results first, or as decided without the measured effect); question 1 (the default); questions 29 and 17 (what an audit step may be); question 4 (the default for a filter on another column).

### 0.4 The route of the work: what you can do after each step

In order. Each step replaces one part completely; nothing is built before you answer the question it needs.
1. **The records agree.** No change on screen. No question.
2. **Filters follow the table you view.** On the demo, filters set under `mlst_bar` stay when you open `year_distribution`, which reads the same table. Built on a branch, in review. No question.
3. **Any table, also one that no result reads.** You open `FastP_with_metadata` in the data preview. Needs question 13: how you reach such a table (a picker, or a list of tables by name).
4. **One form of an audit step: the audit recipe.** Your session holds an audit recipe you can read; a hand edit is refused at reopening; "Remove step" takes out one step. Needs question 26, and questions 29 and 17 for what a step may be.
5. **The dialog of places, with the measured effect.** You remove `10668076` at the places you tick and see the effect on each result before you confirm. Needs questions 28 and 1, then 3 to 9 as they remain.
6. **The export of an audit.** The export holds the original and the audited part, the fingerprint and the log; the report counts the observations removed from each result. Needs question 15.
7. **The report by groups.** The report reads by the groups you see in HOME. No question.
8. **Tables as results, and the one move of the demo recipes.** A summary table can be a result, exported under its name. Needs question 2 and the names.
9. **Later:** the lineage picker that tells the story from the original files; BLUEPRINT's rebuild.

The December demo: `GOALS_REVIEW.md` 4.11 proposes steps 1 to 7, and a check you can do yourself for each goal.

### 0.5 What must be modified (in short; the full lists are in `GOALS_REVIEW.md` section 5)

**(i) Your plans.** My reading; you may object to any line.
- **Keep:** the audit recipe, a copy that never changes the original; its fingerprint and its folder; the log, always exported; the two export parts; "Remove step"; the places you tick, with your default; "Remove from all the data" as the one automatic placement, off until you ask; the join with the metadata in tier 1; tables as results; the names pass.
- **Change, if you agree:** the effect on each result, measured, beside "table changed" and "picture changed" (question 28); the audit removes observations only (question 29); no Reshuffle in HOME (question 17).
- **Later:** the lineage picker, unless question 13 asks for it now; question 27.
- My reading of your goals answers questions 10 to 12, 16, 18 to 22, 24 and 25; the table at the start of part 8 says how. You may object to any of them.

**(ii) The code on `dev`, in what you see.** [read] = I read the code; [inventory] = the inventory of 22 November, not re-read by me.
- **Stays:** the mode switch, "Table to view", the filter panel, the sentences under the preview, the build at opening, Compare, the export's refusal when a file changed since you looked. [inventory]
- **Adjusted:** filters kept while the table is the same (a branch, in review); "Send to Audit" from any table, not only T3; four pieces built this month that no screen reaches yet (the listing of places, the audit recipe builder, its run, the comparison of two tables) connected to the dialog; a plain message when Audit mode opens if your folder cannot be written. [read; the fact check of 22 November]
- **Replaced:** the dialog "This plot only / All plots" by the dialog of places; the bin that removes a step from every plot by "Remove step"; the warning that opens a session whose recipe was edited, by a refusal; the export's one tick box by two ticks. [read]
- **Removed:** the copy of a join that the export writes with the steps baked in; the old forms in the session file; column drops if question 29 is (a); the Reshuffle if question 17 is (c). If you agree: code that no screen reaches (the plot styles, kept unused on purpose since 5 November; the recipe upload, question 24). The held branch of "remove from all the data" is not merged as it is: its sentences about unticked tables were false on the demo. [read; two reviews]

**(iii) Need not be touched:** the tiers, the fixed random seed, the rule that every join is in tier 1, the three kinds of table, Exploration, the Gallery. [inventory]

### 0.6 What the evidence shows, and what I think you may be missing

You asked: "So if i miss something i want a good argumentation of why and how .." (D-0532). Each point says what the evidence shows, why it matters, how it would work, the alternatives, and the question that is yours.

**1. The effect at a place does not tell the effect at the results.**
- Evidence: two reviews wrote sentences about tables where no step is written ("stays", "removed upstream"); each kind was false somewhere, on the demo or on small test recipes [two reviews]. In three runs on the demo, one entity each, with the places listed by hand, the earliest places read as "tier 1 of each original table" left the entity in 7 plots; in 3 of them its source and country were emptied [run].
- Why it matters: a user learns the effect of a choice only from effects that are true (G1, G5). The rows counted at a place cannot show a row that a left join keeps further down.
- How: before you confirm, the app builds the audit recipe with your ticks (the dialog you decided already builds it, to say "picture changed") and compares each result with the original: the observations removed, and the two signals where they occur.
- Alternatives: (a) this measured effect; (b) as decided: the rows at each place, and "table changed" and "picture changed" for each plot; (c) a count after Apply only (question 9).
- Your choice: question 28. It reopens in part your decision to remove the count at the plot (D-0501) and your preference for the check where the step is applied (D-0508).

**2. The default.** Read as tier 1 of each original table, "the earliest" empties metadata in 3 plots; read as the end of tier 1 of each table that joins the metadata, it empties none [run]. With the measured effect, either is seen before you confirm. Your choice: question 1.

**3. Column drops.** My reading: a column is not an observation (G4); drops bring a check and five decisions of their own. Your choice: question 29.

**4. The Reshuffle.** My reading: a new random arrangement removes no observation (G4), and a reader cannot tell whether it was picked among several (G3). The audit recipe you decided cannot yet hold its seed, so an audited reshuffle cannot be re-run to the same picture [read]. Your choice: question 17.

**5. Sentences read from the recipe** (a choice of the builders, not yours): the code of "remove from all the data" lists tables where the entity "may stay"; on the demo all six were false alarms [run]. Suggestion: show only measured effects.

### 0.7 Your questions now

In this order. Each is written in full in part 8, with what you would see for each answer.
1. **Question 28:** do you start from the places (as decided) or from the results (the app proposes places that you see and can change)? And is the effect on each result measured before you confirm?
2. **Question 1:** which places are "the earliest", the ones that start ticked?
3. **Question 29:** does the audit keep column drops?
4. **Question 17:** how is a Reshuffle written, or is it removed from HOME?
5. **Question 4:** does a filter on another column than the entity key start with the same default?
6. **Question 2:** the recipe form, for tables as results and the one move of the demo recipes.
7. **Question 13** (before step 3 of the route: how you open a table that no result reads), **question 26** (before step 4) and **question 15** (before step 6).

After these: questions 3 and 5 to 9, the details of the dialog. Later: 27 and 14. Which of your decisions and builds already match your goals, and can go on: `MATCH_LIST.md`.

---

## 1. How to read this

1. Your words are between quotation marks. Your words are quoted exactly as you typed them, so that nothing is changed. The number after a sentence, for example (D-0508), is its line in the decision ledger.
2. "As the review session read it" marks a reading of your words, not your words. "Recommendation (mine)" is mine. "My wording" marks a definition that no decision of yours gives. "Suggestion:" comes before a remedy.
3. Under each option of a question, "Reopens:" names an earlier decision of yours that this option would change.
4. The app is data agnostic. On the demo recipe the entity is a sample and the entity key is `sample_id`. Everywhere else this document says "the entity".
5. Where I only read the code, or ran something on the demo recipe only, I say so. Nothing here was seen on a screen.
6. The other files of this folder are for the builders (`GOALS_REVIEW.md`, `DIFFERENCES.md`, `PARTS_TABLES.md`, `BUILD_ORDER.md`, `RECIPE_REDESIGN_REVIEW.md`, `RECIPE_PROPOSAL_refined.md`, `RECIPE_PROPOSAL_answers.md`, `RECIPE_PROPOSAL_dialog_walkthrough.md`). You do not need them to answer. `GOALS_REVIEW.md` holds the detail of part 0, if you want it.

---

## 2. The words

- **Original data file:** a file as the app reads it, for example the MLST results of the demo. The app never changes it (D-0509).
- **The three blocks of a recipe** are the three kinds of table (D-0513; the link of each block to a kind is the review session's reading):
  - `data_schemas`: results of analysis about the entities;
  - `metadata_schema`: the information about the entities, one table;
  - `additional_datasets_schemas`: look-up tables, such as a list of genes of interest, used in later joins.
- **Tier 1:** clean each table, and join it with the metadata where that is needed (my wording; the join with the metadata in tier 1 is yours, D-0523). The app already enforces it: the recipe check refuses every join written in tier 2 or tier 3, for every table (part 6.4).
- **Tier 2:** compute, for example add a column or count (my wording).
- **Tier 3:** the table a result is made from. It is still data, never the plot (D-0514). With no steps of its own it is the same table as tier 2 (D-0343).
- **A join:** a table made by putting several tables side by side on a key column. A left join keeps every row of its first table, even when the second table has nothing for it.
- **A result:** what a group shows: a plot or a table (D-0485).
- **The lineage, or the story of the data:** the path from the original data files to a result (my wording).
- **A place:** one table at one tier, where an audit step can be written (my wording).
- **The reach of a place:** how many tables and plots depend on it (D-0346).
- **Exploration and Audit:** the two modes of HOME. In Exploration nothing is saved. In Audit mode you write steps, each with a reason (D-0016).
- **Table to view:** the choice above the data preview in HOME: Source (a file as read), T1, T2 or T3 (D-0310).
- **Compare:** the switch of Audit mode that shows the original and the audited plot side by side (D-0147).
- **An audit step:** a filter, a column drop or a removal by the entity key, with a reason (D-0322).
- **The audit recipe:** a copy of the recipe that holds your audit steps. The original recipe is never changed (D-0143).
- **The audit log:** the list of steps added and removed, with who, when, the reason and the warnings shown (D-0478; the list of what it holds is the review session's reading).
- **The audit record:** a short file beside the audit recipe with its fingerprint (a hash), so that a hand edit is seen (D-0333).
- **A silent case:** a place where a removal by the entity key does not reach a table, and nothing on screen says so. Three kinds: the key is made again by a step; the key is held under another column name with no join; the key is rewritten by a step (for example put in lower case). You call them "got you" (D-0508).
- **A z-score:** a value written as its distance from the mean of all entities. It is computed over all entities, so removing one entity changes the values of the others.
- **BLUEPRINT:** the part of the app where a recipe is written and edited.

---

## 3. The big line, one diagram and one sketch

**The big line.** The app builds each table in stages, from the original data files to the result. You are meant to be able to look at any stage: that is the story of the data you asked for (D-0508); it is not built yet. When you find a bad entity, you write one audit step at the right stage, with a reason (D-0507, D-0322). The original recipe never changes: your steps go into a copy, the audit recipe (D-0102, D-0143). The export holds both recipes and the data, so that the analysis can be repeated (D-0490, D-0492).

**The stages, on the demo path that ends in the plot `mlst_bar`.** "A here" and "B here" show where the two readings of question 1 put a removal by the entity key.

```text
ORIGINAL DATA FILES (read as they are; never changed)
   MLST results file                      metadata file
          |                                     |
TIER 1 of each original table (clean)                       <- A here
   MLST: keep 3 columns;                  metadata_schema:
   "Non Determined" for an unknown type     no step
          |                                     |
          +------------------+------------------+
                             |
STILL TIER 1, in the joined table: the join with the metadata
   MLST_with_metadata: MLST joined with the metadata on the entity key
   (a join with the metadata, when needed, is done here and never
    in another tier, D-0523; the recipe check already refuses
    a join in any other tier)                               <- B here (end of tier 1)
                             |
TIER 2 (compute)
   MLST_with_metadata: add an era; keep the years 2023 to 2025
                             |
TIER 3 (the table the result is made from)
   mlst_bar has no steps of its own: the same table as tier 2
                             |
RESULT
   the plot mlst_bar
```

**The audit dialog: drawn from your decisions; not built.** This is the dialog as decided, option (c) of question 28; part 0.3 adds the effect measured on each result, option (a). It holds open points (questions 1, 3 and 7). Demo values, reading B of question 1, removing one entity from `mlst_bar`.

```text
+-- Create audit step ----------------------------------------------------------+
| Remove the rows where sample_id = 10668076                                    |
| Reason: [ sequencing failed, lab notes of 12 April                        ]  |
|                                                                               |
| Where the step is written (one line per distinct table):                      |
|  [x] MLST_with_metadata, end of tier 1          reach: 2 plots               |
|        rows with this value here: 1                                           |
|  [x] FastP_with_metadata, end of tier 1                                       |
|        rows with this value here: 1                                           |
|  [x] ST22_Anchor, end of tier 1                                               |
|        rows with this value here: 7                                           |
|  [x] ... 10 more lines, one per table that joins the metadata                |
|  [ ] this plot only: mlst_bar                   reach: 1 plot                 |
|                                                                               |
| Plots:  mlst_bar           table changed      picture changed                 |
|         year_distribution  table changed      picture changed                 |
|         ... 11 more plots                                                     |
|                                                                               |
|  [ ] Remove from all the data   (off by default; its list opens first)       |
|                                              [ Cancel ]   [ Confirm ]         |
+-------------------------------------------------------------------------------+
```

- Under reading A of question 1, the ticked lines would be only "MLST, tier 1 (rows: 1)" and "metadata_schema, tier 1 (rows: 1)".
- "Table changed": the table the plot is drawn from has other rows. "Picture changed": the drawn plot is different (D-0318).
- A place the app cannot follow yet would be a red line with no tick box (D-0460). On this path of the demo there is none, and there is no silent case.
- Where the numbers come from: the 13 lines and the 13 plots from the runs of part 6.1; the rows and the reach of `MLST_with_metadata` from my own count on the same tables of that run. Whether each picture changes was not checked.

---

## 4. The picture

**The story of the data, on `mlst_bar`.** Steps 2 to 6 work today; steps 1 and 7 are decided and not built.
1. When a recipe opens, the app builds every table and draws every plot once (D-0326).
2. The original data files are read as they are, and "Source" in HOME shows a file as read (D-0310).
3. Tier 1 cleans each table: `MLST` keeps three columns.
4. Still in tier 1, the joined table `MLST_with_metadata` joins the MLST results with the metadata on the entity key (D-0523). This already works as you decided: the recipe check refuses a join written in another tier.
5. Tier 2 computes: it adds an era and keeps the years 2023 to 2025.
6. Tier 3 is the table the result is made from; `mlst_bar` has no steps of its own, so it is the same table as tier 2 (D-0343).
7. The result is the plot `mlst_bar`; a result may also be a table (D-0485).

**Looking, in Exploration.**
- You see one plot, the result, and under it the table you choose in "Table to view"; a filter changes only that table, is never saved and never exported (D-0327).
- A filter belongs to the table you view, not to the plot (D-0506; decided, not built), and it is cleared when the table you view changes (D-0311).
- It is also cleared when you switch between Exploration and Audit (D-0361).

**One audit, on `mlst_bar`.** This is the audit as decided, option (c) of question 28; part 0.3 adds the effect measured on each result, option (a). Steps 9 to 14 hold under every option. Steps 1, 2 and 11 work today. Step 3 is not decided (question 13). Steps 4 to 10 and 12 to 14 are decided and not built.
1. In `mlst_bar` you see an unexpected sequence type, and the table under it shows the sample (the entity of the demo) that carries it; your lab notes say its sequencing failed.
2. You switch to Audit mode, and the right panel opens (D-0375).
3. You open the table where you see the entity key and ask to remove this value, with a reason.
4. The dialog lists the places where the step can be written, one line per distinct table, with its reach (D-0346).
5. The earliest places start ticked: "we tick low (early) near the original table" (D-0508). Which places are the earliest is question 1.
6. For each ticked place you see the rows concerned, and for each plot "table changed" and "picture changed" (D-0318). Which number a line shows is question 7.
7. The dialog shows the difference only where the step is written: "I would just shows the differents where applied and no per table warnings about downstream effects" (D-0501). The count of rows removed at the plot is not shown: "so I think I would removing it" (D-0501). A place the app cannot follow yet is a red line with no tick box (D-0460). Whether the app can find a silent case and say so on its line is your own question: "could we detect those cases and inform about the possible got you" (D-0508); the review session read it as "detected where the app can" (its reading); question 5 asks one part of it.
8. For an entity that must leave everything, a separate choice, "Remove from all the data", is off by default, lists every table first, and lets you untick one (D-0499).
   - The entity key there is the declared key and a column that a join equates with it: "Id go as B" (D-0500; the option's words are the review session's).
   - A table that only holds a column of the same name, with no declared key and no join, is listed, not ticked, and you may tick it: "C" (D-0498).
   - Your rule for writing recipes, from the same answer: "do not use same column names for different meanings - declare what is ID key" (D-0498).
9. You confirm, and the step is written into the audit recipe; the original recipe never changes (D-0102).
10. Only the tables that changed are run again (D-0325).
11. You see the audited plot, and Compare shows the original and the audited plot side by side (D-0147).
    - Decided, not built: for a result that is a table, the comparison has three layers: a line above the table, always; the full-row difference, only on request; the paired view, only where a key is verified. There is no layer per audit step: "I do not think I want layer 4 - its too much" (D-0489; the layers are the review session's words).
12. You can take any one step out again with "Remove step" (D-0314).
13. Your session keeps the audit recipe, its record and the audit log in a folder `audit/` (D-0319).
14. The export of an audit (exploration is never in it: that part works today):
    - The reproducibility part has two parts, the original and the final audited, each with its recipe; the data is stored once beside them (D-0490, D-0492). Your words: "it needs to be really clear which one is the orginal and which one is the audit_result" (D-0492).
    - The audit record and the audit log are always there (D-0333, D-0478).
    - The file of a result is named from its id: "Part 1 -A" (D-0490; the option's words are the review session's).
    - Whether the publication part also holds the original recipe is question 15.
    - The report has two parts, results first: "yes # Results  before # Technical" (D-0491).
    - The app features file is named with its label and its file name, for example "Web Demo (web-demo)": your answer "C" (D-0497; the form of the text is the review session's).

---

## 5. What is wrong today: the four things that matter most

All four were checked in the code.

**1. Where an audit step is written.**
Today the app writes an audit step only at the table of the open plot (tier 3), and its dialog asks "This plot only / All plots / All plots except…", not where in the story the step goes.
You decided: "We had said we can send at each tier - so we need to send the correct tier" (D-0507).
The difference for you: you cannot remove an entity before a join or from a table no plot reads, and a step for several plots is written once per plot.

**2. What you can see before you write a step.**
Today HOME shows, for the open plot, the original files as read and the stages of the plot's own table only.
You decided: "YES the story of is what I want to show - this is why I wanted the lineages" (D-0508), and that a table no plot reads "Must be and yes must be viewabøenin the data preview" (D-0457).
The difference for you: on the demo you cannot open tier 1 of `MLST` or the 6 tables no plot reads, so you cannot look at the table where a step would be written.

**3. What an export of an audit holds.**
Today an export of an audit holds the steps and their reasons. It holds no original recipe, no audit recipe, no fingerprint file and no log of the warnings. If its reproducibility box is ticked, it also holds a copy of the recipe with the steps written into it, which is neither the original nor the audit recipe of your decisions.
You decided: "when audit steps have been added the audit recipe is the truth - so the export must contain the recipe of the audit" (D-0324), the original recipe "1. yes must." (D-0389), and "it is then actually not optional anymore to add the log for the audit to the export" (D-0478).
The difference for you: an export of an audit cannot be re-run from the original recipe, and nothing in it proves that its recipe was not edited by hand or shows what you were warned of.

**4. A session saved before its recipe was edited.**
Today the app opens such a session with a warning, and applies the old audit steps to the changed recipe.
You decided: "so I would refuse - I would explain that the original recipe has been modified and that it needs to reanalyze and add the audit steps where they are done" (D-0362).
The difference for you: old steps can act on columns and rows that are no longer what they were when you wrote them.

The full list of 27 differences is in `DIFFERENCES.md`.

**One consequence for your saved work.** When the audit steps move to the audit recipe, the session file gets a new form. You decided once, for sessions that held "My view", that they are refused and removed: "A - best to clean all old sessions" (D-0312). Whether the same holds for this change is not decided. Question 26 asks you.

---

## 6. Where two of your sentences can be read in two ways

### 6.1 The earliest place

Your sentences:
- "the earliest place of each branch - which is the original data basically" (D-0501);
- "we tick low (early) near the original table - so by default it is propagated in the lineage" (D-0508);
- "no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" (D-0509);
- "T has been removed - because we join all data sets with metadata in T1 when necesary (and not in other tiers) - and if No metadata join is needed. As we said the other data tables can be used in later joins." (D-0523).

The join with the metadata in tier 1 is already what the app enforces: the recipe check refuses every join written in tier 2 or tier 3 (part 6.4).

**Reading A:** the default tick is tier 1 of each original table. For `mlst_bar`: `MLST` and `metadata_schema`.
**Reading B:** the default tick is the end of tier 1 of each table that joins the metadata. For `mlst_bar`: `MLST_with_metadata` and the 12 other tables that join the metadata. The Source view stays as read in both readings.

**What was run.** Three runs on the demo recipe, one entity each: two entities that are in every original file, and one that is not in the ResFinder file. They used the real data and the real engine, through code that builds the audited tables without a screen, not through HOME. Version 1 of this document made the first run; a review reproduced it with the two other entities. All three show the same pattern.

| Removing one entity, on the demo | Reading A | Reading B |
|---|---|---|
| Started from `mlst_bar` | 2 lines ticked. 13 plots change. The entity stays in 7 plots: in 4 that never meet MLST or the metadata, and in 3 with no source and no country. | 13 lines ticked. 13 plots change. The entity stays only in the 4 plots that never meet the metadata. No metadata is emptied. |
| "Remove from all the data" | 11 places. The entity is in no plot. | 19 places. The entity is in no plot. 8 of the 11 original tables keep it at tier 1. |
| Your case: keep it in the quality results only (D-0499) | Untick FastP, Quast and Bracken: it stays in the 3 quality plots without its metadata, and in one more plot. | Untick 2 tables: it stays in exactly the 3 quality plots, with its metadata. |
| A summary table made from a join (the recipe proposal's form, part 7), on a small part of the demo | The removed entity appears in the summary of reads as a new group with an empty country and an empty year: 10 rows instead of 9, the total still 42. Nobody ticked that summary. | 9 rows, total 41: the entity leaves the summary with its metadata. |

The entity that is not in ResFinder stays in one plot fewer (6 and 3). The 3 quality plots are `qc_reads_horizontal_barplot` (it loses the source, the year and the country), `assembly_quality_dotplot` and `miaou`, a plot that draws the source (both lose the source and the country).

**Why they differ.** A left join keeps every row of its first table, even when the second table has nothing for it. In five joins of the demo the results table comes first and the metadata second; in two more a results table is the base and the metadata comes later. Under reading A, from `mlst_bar`, the entity leaves the metadata but not the FastP, Quast or Bracken results. So its rows stay in the tables that join those results with the metadata, and in the three quality plots they show no source and no country (and no year in one of them). Under reading B the removal comes after the join, so the row leaves with its metadata.

**Limits.** The places of each reading were listed by hand: the lineage of `mlst_bar` back to its original tables, then forward from them. If the dialog also ticked the other original tables that meet the metadata in a join (FastP, Quast, Bracken, ResFinder, VirulenceFinder), reading A would empty no metadata (reasoned, not run). Whether those tables belong to the lineage of `mlst_bar` is not decided; as I read your words "So basic lineage is up to it can only go backwards when on its way up or forward when on its way backwards" (D-0451), they do not.

The last row of the table was run by the authors of the recipe proposal, with the real engine, on a small part of the demo: two joins with the metadata (MLST and FastP), not the 13 of the demo. The summary table does not exist in the app yet, so its steps were run in its place on the joined table (a route the proposal checked: it gives the same rows as a direct computation). I ran their script again and got the same numbers. Details: `RECIPE_PROPOSAL_dialog_walkthrough.md`, part 3.

Question 1 asks you to choose.

### 6.2 The filters on a switch of mode: an error in the records, not a question

Your decision of 20 November stands: "8 - No we had decided to clear them- Only the steps applied in the audit are kept -> but then they are writen in the recipe" (D-0361). Two lines of 22 November (D-0505, D-0506) say, in the review session's words, "NOT decided: what a change of mode does to the filters". That is an error of the records, to be corrected. The app clears the filters on a switch, as you decided. No question, unless you want to change it.

### 6.3 The original recipe in the export

- 20 November, the later line: "1. yes must." to the question whether the export always contains the original recipe, because "if you need to redo the analysis then you will need to re-upload the recipe" (D-0389).
- 16 November: "I think that would be best to add the recipe to the reproducibility mode 2 - And I suggest to remove the recipe from the mode 1", and "when in audit it will be added anyway (via the audit_recipe)" (D-0192). Mode 1 became the Publication tick, as I read the later line D-0298.

**Reading A:** "always" means every export, the Publication part included.
**Reading B:** "always" means every export that holds the Reproducibility part, where you put the recipe on 16 November.

Question 15 asks you to choose.

### 6.4 "Other joins could be used after": in which tier?

Your sentences:
- "metada is a certain type of data - other joins could be used after but join with metadata must be done at T1 that would simplify removing of samples by key no" (D-0510);
- "As we said the other data tables can be used in later joins." (D-0523).

As the review session read the first one then: "joins of other tables may be in tier 2 or later" (its reading, not your words).

What the app does today: the recipe check refuses every join written in tier 2 or tier 3, for every table, look-up tables included. A join of a look-up table (a table of `additional_datasets_schemas`, for example a list of genes of interest) is written in tier 1 of a join today. On the demo, `ST22_Anchor` does exactly this: it starts from the metadata, joins four more tables to it (left joins), then the list of genes (an inner join, which keeps only the genes of the list), all in tier 1.

**Reading A:** "after" means later steps of tier 1: the metadata join first, then the other joins, all in tier 1. This is what the app enforces today.
**Reading B:** "after" means a later tier: a join of another table may be written in tier 2. The app refuses that today.

Question 27 asks you to choose.

---

## 7. How the recipe redesign fits the whole picture

You asked me to review the proposal for the recipe form from the whole picture (D-0526). The proposal is copied into this folder as `RECIPE_PROPOSAL_refined.md`. The form stays your choice (D-0496). The details and the evidence are in `RECIPE_REDESIGN_REVIEW.md`. I asked the authors of the proposal eleven questions (you allowed the exchange, D-0526); their answers and their new walk-through of the audit dialog are copied into this folder as `RECIPE_PROPOSAL_answers.md` and `RECIPE_PROPOSAL_dialog_walkthrough.md` (not confirmed by you). Parts 7.4 to 7.6 below use them.

To answer question 2 you need only part 7.3. Parts 7.1, 7.2 and 7.4 to 7.6 are the background.

**7.1 What you asked, in your words.**
- "No Tier 3 is not a plot - T3 is the data that goes into a plot ... its still data" (D-0514).
- A result is a plot or a table: "a plot entry actually should be a result_entry with either plot or table no?", and "yes result is the last stage (the tier that has the latest instructions in the recipe)" (D-0485).
- "Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before" (D-0516).
- "yes we need the `from:` this clarifies but still the hiearchy is unclear of where to place it" (D-0517).
- Your case: "one final result could be used on T2a but T2a could be used to produce one T3a for another final result - what would be done in this case ?" (D-0517).
- "I want the examples on how it would like like with all the tiers and both plot and data as result" (D-0517).
- Arguments of good practice and good data science, "not economical in term of changes to do" (D-0516).
- The table that is a result is exported: "so we shuold be able to export the table that is as result also" (D-0487).

**7.2 Does the proposal meet them?** Its recommended form is form 3. As the review session reported it, you wrote "we can exclude form 4 and I guess 5" (D-0496): form 4 is set aside; form 5 may still be open for you.

| What you asked | Form 3 | Where in the proposal |
|---|---|---|
| Tier 3 is data | Yes: every data step is in the data part; a result only names a table | Part 1, Part 2.2 |
| A result is a plot or a table, at its last stage | Yes: `result: plot` or `result: table`; `from:` reads the table at its last stage | Part 1, Part 8 |
| Tier 3 defined like tiers 1 and 2, before the results | Your tier 3 exists under another name: a "derived table". It has its own tier 1 and tier 2 and is written before the results. The person who writes the recipe no longer writes a "tier 3"; the word stays only for the audit's "this result only" | Part 1, Part 2.2, Part 8 |
| The place of `from:` | Yes: in a derived table, after its name, before its tier 1; in a result, in place of today's `target_dataset` | Part 1 |
| Your case T2a, then T3a, then another result | Yes, walked through on the demo with real numbers | Part 3 |
| Complete examples with all tiers, a plot and a table as results | Yes, on a part of the demo recipe | Part 2.2 |
| Good practice, not economy | Yes: the cost is shown as information only | Part 7 |
| The table result exported | Not in the proposal: it rests on your decisions D-0487 and D-0490 | not covered |

> **This is a proposal. Nothing is confirmed. You confirm or refuse it in question 2.** Form 3 is not confirmed (D-0496).

**7.3 The hierarchy, as one complete small example on the demo (form 3).** Shortened from the proposal: fewer columns. Left out to keep it short: the head of the file (`id`, the engines, `info`), and the keys `null_values` and `strip`, which every source table must have; as written here, the example would not pass the recipe check. The names `derived_tables`, `results`, `result:` and `from:` are the proposal's; they are not decided (D-0487).

| Order | Block | Tiers | What it reads |
|---|---|---|---|
| 1 | source tables: `data_schemas`, `metadata_schema`, `additional_datasets_schemas` | tier 1, tier 2 | a file |
| 2 | joins: `joins` | tier 1, tier 2 | each ingredient after its tier 1 |
| 3 | derived tables: `derived_tables` | `from:` ONE table; tier 1, tier 2 | that table at its last stage |
| - | plot defaults: `plot_defaults` | none | nothing |
| 4 | results: `analysis_groups`, then `results` | `result: plot` or `result: table`; `from:` ONE table | that table at its last stage; a plot adds its drawing (`mapping`, `layers`) |
| 4a | "this result only" | written by the audit only, in the audit recipe | the result's table |

There is no block called tier 3. Your "T3a" is a derived table (block 3), with its own tier 1 and tier 2. The words "tier 3" stay only for the audit's place "this result only" (4a).

```yaml
# 1. Source tables, read from files
data_schemas:                          # results of analysis about the entities
  MLST:
    source: {type: local_tsv, path: ./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv}
    input_fields:
      sample_id: {original_name: sample_id, type: String, is_entity_key: true}
      sequence_type: {original_name: "Sequence Type", type: String}
    tier1:                             # clean
      steps:
        - action: polars_select
          exprs: [sample_id, sequence_type]
    tier2:
      steps: []                        # empty: T2 = T1
metadata_schema:                       # the information about the entities
  source: {type: local_tsv, path: ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv}
  input_fields:
    sample_id: {original_name: sample_id, type: String, is_entity_key: true}
    year: {original_name: Year, type: Float64}
    country: {original_name: Country, type: String}
  tier1:
    steps: []

# 2. Joins
joins:
  MLST_with_metadata:                  # your "T1a" and "T2a"
    ingredients:
      - dataset_id: MLST
      - dataset_id: metadata_schema
    tier1:                             # the join with the metadata is a tier 1 step
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: left
          maintain_order: left_right
    tier2:                             # compute: keep the years 2023 to 2025
      steps:
        - action: modif_filter
          column: year
          op: between
          value: [2023, 2025]
          na: remove

# 3. Derived tables: a table made from ONE table
# There is no block called tier 3: your T3a is this derived table, with its own tier 1 and tier 2.
derived_tables:
  MLST_samples_per_country_year:       # your "T3a"
    from: MLST_with_metadata           # read after its tier 2
    tier1:                             # still one row per entity
      steps:
        - action: polars_with_columns
          named_exprs:
            year_label: "pl.col('year').cast(pl.Int64).cast(pl.String)"
    tier2:                             # the count: one row per country and year
      steps:
        - action: polars_group_by
          by: [country, year_label]
          maintain_order: true
          named_aggs:
            n_samples: "pl.col('sample_id').count()"

plot_defaults:
  theme: theme_minimal

# 4. Results: each names ONE table and shows its last stage; no data steps here
analysis_groups:
  Results:
    ui_label: "AMR and Virulence"
    results:
      mlst_bar:                        # a plot: your "result A"
        ui_label: "MLST Bar"
        result: plot
        from: MLST_with_metadata
        mapping: {x: sequence_type, fill: country}
        layers:
          - name: geom_bar
            params: {}
      samples_per_country_year:        # a table: your "result B"
        ui_label: "Samples per country and year"
        result: table
        from: MLST_samples_per_country_year
```

On the demo data (the proposal's run): `mlst_bar` shows 33 rows; the table result shows 6 rows (Norway 2024: 19, and five more). A plot of the same derived table would show the same 6 rows.

**7.4 What form 3 makes easier or harder in the rest of the picture.**
- *The places of an audit step.* A derived table is one more table, so one more place: its tier 1, and its tier 2 only while the entity key still exists there. For a removal by the entity key the earliest place is always further up (question 1), so the default ticks do not change (run on the demo slice by the authors of the proposal). On a derived table, reading A has a visible effect: the removed entity stays in a reads summary as a group with an empty country and year (10 rows instead of 9, total still 42), because the left join keeps the row of the first table; reading B does not do that (part 6.1, last row of the table). For a column the derived table makes itself (for example the year written as text) the earliest-place rule is not defined. New: a step written at a derived table changes only the results made from it, and "this result only" stays possible (D-0346).
- *The join with the metadata.* It stays a tier 1 step of a join of raw data tables (D-0523); the app already enforces this (part 6.4). A derived table is made from a table that already has the metadata ("derived tables should already have the metadata joined", D-0511), so it never joins it (as I read D-0511; a derived table cannot join anything: the recipe check refuses a join outside tier 1 of a join, and a derived table has no list of tables to join). A join with a look-up table is written before the derived table. A look-up join after a count would need either a join that takes a derived table, which reopens "a named join takes only source tables" (D-0344), or a join in tier 2 (question 27).
- *The story of the data.* Every summary gets a name and one definition, so the story is clearer, and one table longer. But "Table to view" (Source, T1, T2, T3) cannot show the whole chain of a result made from a derived table: the join's tier 2 that it reads is not among the four choices. This is your question of D-0518: "I am just wondering of how to make it navigate". The entity column does not exist at the derived table's tier 2 or at a table result of an aggregate (run): to remove an entity the user starts from the derived table's T1, or from a Source line, not from the result. The picker (question 13) would answer it; the proposal leaves it open.
- *A table as a result, and its export.* A table result is simply the last stage of one table, so the table on screen and the file exported are the same object. The proposal does not say it; the authors answer: a file named from the result's id for each TABLE result, with the same rows as the derived table's own `T2_data.tsv` (a plot result keeps the table's file, and gets `T3_data_<id>.tsv` only when audited). Options for you: that, or only a line in the README that maps the id to the table's file, or an id file for every result (`RECIPE_PROPOSAL_answers.md`, question 3). The export loop, the key check's scope and the list of tables no plot reads look only at the plots' tables today, and must count derived tables and table results.
- *The two parts of the reproducibility bundle.* Not changed: both parts hold recipes of the same form.
- *The comparison of original and audited (D-0489).* Easier: the result is one table at its last stage, the same for a plot and its table, so the pair to compare is clear.
- *The lineage picker.* A derived table has one parent (`from:`), so it is easy to draw in an outline.
- *The one move of the demo recipes (D-0525).* The form decides which keys every recipe and every Gallery example gets. The move, the names pass and the move of `VirulenceFinder` are one pass.
- *BLUEPRINT.* It must write this format without replacing a recipe by mistake and without losing comments (D-0495). Its map knows sources, joins and plots today; it needs a derived table and a table result.

**7.5 Where the proposal and the whole picture disagree, or leave a hole.**
1. The proposal's dialog walk-through ticks every place (D-0316). Your later default is "tick low" (D-0508), and which place is earliest is still open (question 1). The walk-through was redone (`RECIPE_PROPOSAL_dialog_walkthrough.md`).
2. Two reading rules in one recipe: a join reads its ingredients after tier 1; `from:` reads its table after its last stage. Both are needed (the proposal shows that making joins read tier 2 would change results silently), so the recipe documentation must say both plainly.
3. "Table to view" for a result made from a derived table: what "Source" means there is open in the proposal (three readings), and the full chain is not reachable (7.4).
4. The export of a table result by its id, and of two results that read one table, is not in the proposal.
5. A table read only by a derived table, or only by a table result: today the app counts only plots as readers of a table. So such a table would get its tier 2 refused by the recipe check, and the export would not write its tier 2, although a result is made from it. The app already builds that tier 2 (run by the authors of the proposal). The places of the app that count readers must also count derived tables and table results (details for the builders: `RECIPE_REDESIGN_REVIEW.md` 4.10). This meets question 21 (the tiers of a table no plot reads).
6. A result id written in two groups is not refused today: the second silently replaces the first (the proposal's flag 6). This is a defect of today, whatever the form; it is already filed to be fixed.
7. The proposal's examples still use `ui_title` and `label`, which your names decisions remove or rename (D-0484, D-0468).

**7.6 What could be simpler, seen from the whole.**
- One level of derived tables for now: a derived table made from a source table or a join, not from another derived table. The story of the data then stays at most one table longer than today. Suggestion: the same "revisit if needed" as for joins of joins (D-0344).
- A join that takes a derived table as an ingredient would reopen "a named join takes only source tables" (D-0344). The proposal leaves it open (its point 10); nothing in your case needs it. Information.
- On screen, the last stage of a result could be called "Result" rather than "T3", as in the badge you accepted ("I like the badge that says result or earlier stage this is accepted", D-0487). "T3" would then need no explanation.

Recommendation (mine): form 3, with one level of derived tables for now (the walk-through of the dialog has been redone with your default of D-0508, readings A and B). It meets what you asked on your own criteria (one table, one definition; a definition before its use; a plot and its table show the same numbers by construction), and the proposal's runs on a part of the demo recipe support it.

---

## 8. What stays yours to choose

### Seen from your goals (second pass, 22 November)

Your passage (D-0528) and your words of D-0531 change which questions come first. Two questions are new (28, 29); questions 4 and 17 got an added option. The numbers do not change.

| Question | Status |
|---|---|
| **28** (new) | **Now, first.** Where you start in the dialog (places or results), and whether the effect on each result is measured before you confirm. |
| **1** | **Now, after 28.** Which places are "the earliest", the ones ticked by default. |
| **29** (new) | **Now.** Column drops in the audit. |
| **17** | **Now.** The Reshuffle: an option (c), no Reshuffle in HOME, was added. |
| **4** | **Now.** The default for a filter on another column than the entity key. |
| **2** | Needed for tables as results and the one move of the demo recipes; not for the audit. |
| **26** | Before the audit steps move to the audit recipe. |
| **15** | Before the export of an audit. |
| 3, 5, 6, 7, 8 | After 28 and 1: the details of the dialog. With 28 (a) or (b), a removal that misses a result (5) and a computation over all observations (8) also show in the measured effects. |
| 9 | With 28 (a) or (b), the effect is measured before you confirm, so a count after Apply is not needed. With 28 (c), the question stays. |
| 10, 11, 12, 25 | My reading of your goals and of D-0478 ("so we can show that the user has been warned and that is is a user decision"): 10 (c), 11 (a), 12 (a), 25 (b). You may object. |
| 16 | My reading of G3 and of D-0147: (a), both pictures in the Publication part. You may object. |
| 18, 19, 20 | My reading of G3 and G5: 18 (a), 19 (c), 20 (a). You may object. |
| 21 | My reading of G2 and of "Why Tier 2 refuses ? its still data wrangling" (D-0514): (b). You may object. |
| 22 | My reading of E4 and of D-0498: (a), an advice, never a refusal. You may object. |
| 24 | My reading of E6: (a), remove the code that no screen reaches. You may object. |
| 23 | Later, with the lineage picker. |
| 27 | Later: no goal needs it now; today's rule, every join in tier 1, stays until a recipe needs a look-up join after a count. |
| 13 | Before step 3 of the route (part 0.4): how you open a table that no result reads (a picker, or a list of tables by name; D-0457 leaves the way in open). |
| 14 | Later, if question 13 gives a picker. |

### Now, from your goals: questions 28 and 29

#### 28. Where do you start in the dialog, and is the effect on each result measured before you confirm?
- **Situation:** you decided that the scope is the user's: "We cannot choose for him..the app cannot decide the scope" (D-0531). The user ticks the places in the lineage (D-0093, D-0355), with the earliest places ticked by default (D-0508). Before you confirm, the dialog you decided shows the rows at each place, and for each plot "table changed" and "picture changed" (D-0316, D-0318). Two reviews and three runs on the demo found that what happens at a result cannot be read from the place (part 0.6, point 1).
- **Withdrawn:** the first version of this question proposed that the app choose the places from the results you tick. Your words of D-0531 rule it out, and a check found cases it could not write: before or after a join with the same results; "year xx not shown" at one plot against removing the entities at tier 1; one intermediate table only. It is not an option any more.
- **Today:** "This plot only / All plots / All plots except…"; a step is written only at the table of the open plot.
- **Question:** which dialog do you want?
- **(a) Places, as decided, with the effect on each result measured.**
  - What you would see: the sketch of part 0.3. The lineage as a propagation; one line per place, with its reach; your default ticked and named. Under the lines, for each result: "n observations removed" or "unchanged"; and "still found here" or "the values of other observations change here" where it happens. When you change a tick, the effects are measured again.
  - For: every intention can be written: before or after a join, one table only, one result only. You see the effect of each tick on what you publish before you confirm.
  - Against: you think in places. For "keep the entity in the quality results only" you find the places to untick yourself, guided by the effects.
  - Reopens: D-0501 in part ("The count of rows removed at the plot ... so I think I would removing it": a count is shown again, measured); D-0508 in part ("Id rather the check is more where you apply it": the check is also made at each result). It extends D-0318: counts beside "changed".
- **(b) Results first: the app proposes places that you see and change.**
  - What you would see: above the lineage, the list of results with ticks. When you tick results, the app ticks the places that reach exactly them, marked "proposed"; you can change any place; the effects are measured as in (a). If a place you changed no longer matches a result you ticked, the dialog names that result.
  - For: a case said in results, such as "keep the entity in the quality results only", is one untick per result; the places stay yours to change.
  - Against: two lists to keep in agreement; a proposal can steer the choice, even when it is named.
  - Reopens: as (a); and in part D-0508 ("we tick low (early) near the original table": the default ticks come from the results you tick); D-0194 and D-0316 (all places ticked "so it show clearly the extend of where it will be removed": the extent is shown by the effects instead); D-0415 part A ("I mean we need the lineage of where it was selected (eg. T3) then all ticks by default"); D-0022 in part (the ledger records, without your words, that the only automatic placement is "remove from all tables": here the app proposes and you confirm).
- **(c) As decided, without the measured effect.**
  - What you would see: the sketch of part 3: the place lines, the rows at each place, and "table changed" and "picture changed" for each plot.
  - For: the dialog you decided, with nothing added.
  - Against: a removal that does not reach a result, for example a row kept by a left join, is not shown before you confirm; you see it after Apply, with Compare.
  - Reopens: nothing.
- **(d) Neither: say what you mean.**
- **Not reopened by any option:** the place stays yours (D-0093, D-0355; "we go back the lineage and forward and the user choose which data it affects", D-0053); a table that no result reads is a line (D-0451); nothing is written that you did not tick (D-0022).

Recommendation (mine): (a). It keeps every place yours, and only a measured effect is true at the results (part 0.6, point 1).

#### 29. Does the audit keep column drops?
- **Situation:** an audit step is a filter, a removal by the entity key, or a column drop: "A : for now yes only filter and drops" (D-0322). My reading: a column is a variable, not an observation, and the audit is for removing observations (G4).
- **Today:** in Audit mode, while you view T3, a column chooser under the data preview can send "drop these columns" to the audit, for the open plot.
- **Question:** does the audit keep column drops?
- **(a) No: the audit removes observations only.**
  - What you would see: no column control that writes an audit step. The column chooser still hides columns from your view. A column that must not appear in a result is removed by the author of the recipe, in the step that selects the columns of that table.
  - For: the audit stays a correction of observations; the check of key columns and its rules are no longer needed for the audit.
  - Against: you cannot remove a column from a published table without the author.
  - Reopens: D-0322 in part. The decisions about dropping a key column stay as they are; the audit no longer uses them.
- **(b) Yes, as decided.**
  - What you would see: the column chooser in Audit mode; a drop is refused, with a plain line, where a later join needs the column.
  - For: you can remove a column without the author.
  - Against: a check and rules of their own, for something that is not a removal of observations.
  - Reopens: nothing.
- **(c) Neither: say what you mean.**

Recommendation (mine): (a). The audit then holds only removals of observations, and one check with its own rules is no longer needed.

### Version 3's grouping (before your goals)

You asked for the questions that block the most work first (D-0519). The questions keep the numbers of the earlier version, so that the other files still point at the right question; here they are grouped by when you need them.

- **Now: questions 1, 2 and 27.** Question 1 shapes the audit dialog; question 2 shapes the one move of the demo recipes, and with it the names; question 27 decides where a join with a look-up table may be written, which is part of the recipe form that question 2 confirms (part 7.4: a derived table cannot join anything).
- **Next, because they shape the screens: questions 3, 13, 15 and 26.** Question 3 is the shape of the dialog; 13 is the lineage picker (option (c) of question 2 depends on it); 15 is a conflict between two of your own sentences about the export; 26 must be answered before the audit steps move to the audit recipe.
- **Can wait until that part is built; my recommendation stands unless you object.** 18 questions, in five groups: the rest of the dialog (4 to 9), the audit log (10, 11, 12, 25), the export (16), the words and defaults on screen (18, 19, 20, 23), clean-up (21, 22, 24). Two more come later: 14 follows 13, and 17 is the Reshuffle, which you said "is not critical for now" (D-0341).

You can accept all my recommendations of a group in one answer, for example "the audit log: accept". Questions 15, 17, 26 and 27 have no recommendation (version 3; the goals review now recommends (c) for question 17).

### Version 3's "Now": the three questions that blocked the most (see the table above for their status now)

#### 1. Where is "the earliest place" that the dialog ticks?
- **Situation:** you decided that the dialog ticks the earliest places by default (D-0508), and your sentences can be read in two ways (part 6.1).
- **Why it matters:** a left join keeps every row of its first table, even when the second table has nothing for it. On the demo, if the removal is written before the joins with the metadata, the entity leaves the metadata but not the quality results. The removed entity then still shows in 3 quality plots, as rows with no source and no country (and no year in one of them).
- **Today:** there is no such dialog; a step is written only at the table of the open plot.
- **Question:** is the earliest place tier 1 of each original table, or the end of tier 1 of each table that joins the metadata?
- **(a) Tier 1 of each original table.**
  - Your sentences that point here: "the earliest place of each branch - which is the original data basically" (D-0501); "we tick low (early) near the original table" (D-0508).
  - What you would see, removing one entity from `mlst_bar`: two ticked lines, "MLST, tier 1" and "metadata_schema, tier 1". After Apply, 13 plots change. The entity stays in 7 plots: in 4 that never meet MLST or the metadata, and in the 3 quality plots as rows with no source and no country (`miaou`, which draws the source, among them).
  - Also run, on a small part of the demo with a summary table made from a join (the recipe proposal's form, part 7): the removed entity appears in that summary as a new group with an empty country and year, 10 rows instead of 9, the total still 42, although nobody ticked it. Under (b) it does not. Limits: two joins with the metadata, not the 13 of the demo; the summary table was emulated, because the app does not have it yet (part 6.1).
  - For: the step is written where the data enter, and a computation over all entities never sees the removed one.
  - Against: three plots change in a way you did not ask for; in your case of D-0499 the entity stays in the quality plots without its metadata.
  - Reopens: nothing.
- **(b) The end of tier 1 of each table that joins the metadata** (on a branch that never meets the metadata: the end of tier 1 of the first table its results read).
  - Your sentence that points here: "the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" (D-0509).
  - What you would see: 13 ticked lines, one per table that joins the metadata, for example "MLST_with_metadata, end of tier 1 (after the join with the metadata)" (the sketch of part 3). After Apply, 13 plots change; the entity stays only in the 4 plots that never meet the metadata; no row is left without its metadata.
  - For: the row leaves with its metadata; your case of D-0499 keeps the entity in exactly the 3 quality plots, with its metadata.
  - Against: 13 lines to read before you confirm, and the audit recipe shows the same step 13 times; a computation over all entities written in tier 1 after the join would run before the removal (not the case on the demo).
  - Reopens: nothing written. It reads "near the original table" (D-0508) as: just after the original table is joined with its metadata.
- **(c) Neither: say what you meant.**

The Source view stays as read in both readings.

Recommendation (mine): (b). On the demo it leaves no row without its metadata, and it gives your case of D-0499 exactly. You may have meant (a): "near the original table" (D-0508) points to it. The evidence is three runs on the demo, with places listed by hand (part 6.1).

#### 2. The recipe form: do you confirm form 3?
- **Situation:** you asked for tier 3 defined like tiers 1 and 2 and before the results, a result that is a plot or a table, and the place of `from:` (D-0516, D-0517). "Form 3" is the proposal's name for this form: every table is defined in the data part (the source tables, the joins, then "derived tables", each made with `from:` from ONE table), and a result only names one table. You have not confirmed it (D-0496). By your own order, the demo recipes are moved once, after the recipe design is final (D-0525).
- **Today:** a result is a plot only, and its own tier 3 steps sit in the plot entry, after everything else.
- **Question:** do you confirm form 3, shown in part 7.3?
- **(a) Yes, form 3.**
  - What you would see: the file of part 7.3; in HOME, the plot `mlst_bar` and the table `samples_per_country_year` as results; the summary has one definition, so its plot and its table show the same 6 rows.
  - For: one table, one definition; a definition before its use; to know which results a step changes you search one name.
  - Against: a step that only one figure needs (a sort, a filter) must become a named table; the person who writes the recipe no longer writes a "tier 3"; a result made from a derived table cannot show its whole chain in "Table to view".
  - Reopens: D-0306 ("T3 : data plot specific (better explained)") and D-0063 ("The T3 is the data that goes to the plot BUT not the plot recipe"); D-0237 and D-0250, which put tier 3 at the plot entry as a tier of its own (your "B for both ... Cleaner" and "B"); and D-0485 point 3, "tier 3 = tier 2 plus the entry's own steps" (the review session's words, which you approved with "yes"). All because a result no longer holds data steps of its own.
- **(b) No, another form.** Say which. The proposal also shows forms 4 and 5; as the review session reported it, you wrote "we can exclude form 4 and I guess 5" (D-0496), so form 5 may still be open for you. Or a form of your own.
  - Reopens: nothing.
- **(c) Not yet.** You first settle how a user reaches the tables before a result (your question of D-0518, and question 13).
  - What you would see: no change now; the one move of the demo recipes comes after your answer, as you ordered (D-0525).
  - For: you choose the form with the navigation in front of you.
  - Against: nothing in the data or the results; the form stays open until then.
  - Reopens: nothing.

**An extra choice, only if (a): one level of derived tables for now?**
- **(a1) One level:** a derived table is made from a source table or a join, not from another derived table. What you would see: the same file as part 7.3 (it has one level); a derived table made from another derived table is refused by the recipe check with a plain line. For: the story of the data stays at most one table longer than today. Against: a summary of a summary must be written in one derived table. Reopens: nothing.
- **(a2) Any number of levels.** For: a summary of a summary can be its own table. Against: the story of a result can grow by several tables. Reopens: nothing.

Recommendation (mine): (a) with (a1). The proposal's runs on a part of the demo recipe favour form 3 on your own criteria, and one level keeps the story short. Nine more questions come only after the form (the names of the keys, and when a table result opens on the result); none of them blocks today; they are listed in `RECIPE_REDESIGN_REVIEW.md` part 7.

#### 27. Joins after the join with the metadata: only in tier 1, or also in tier 2? (part 6.4)
- **Situation:** you decided that the join with the metadata is done in tier 1, and you wrote "other joins could be used after" (D-0510) and "the other data tables can be used in later joins" (D-0523). When you decided D-0510, the facts put to you spoke of a rule of the recipe check that refuses a join in tier 2. You were told that the check has no such rule. It has one. I am sorry for the wrong fact.
- **Today:** the recipe check refuses every join written in tier 2 or tier 3, for every table: the metadata, a results table and a look-up table alike. The refusal says to move the join to tier 1. So your rule for the metadata is already enforced, and a join with a look-up table (a table of `additional_datasets_schemas`, for example a list of genes of interest) can only be a tier 1 step of a join. This rule was written in the recipe format specification ("`polars_join` only in tier1", not your words) and follows the architecture decision on the three tiers of April 2026 ("tier1 (Tidy/Relational): Logic applied to wide data (Join, Clean, Rename, Filter)"; "tier2 (Plot-Prep): Visual-specific transformations (Unpivot/Long-format, Summarize, Aggregate)", not your words). No line of your decision ledger states it. A result never holds a join in any option: it has no list of tables to join.
- **Question:** does "after" mean later steps within tier 1, or may a join of another table be written in tier 2?
- **(a) Keep today's rule: every join is a tier 1 step.** "After" means later steps within tier 1: the join with the metadata first, then the joins with look-up tables.
  - What you would see on the demo: no change. `ST22_Anchor` starts from the metadata, joins four more tables (left joins), then the list of genes (an inner join, which keeps only the genes of the list), all in tier 1, as today. A look-up join after a count needs the count first in tier 1 of the join, or, under form 3 (question 2), a join that takes a derived table, which reopens "a named join takes only source tables" (D-0344).
  - For: one rule for every join; every table a join brings in is there from the end of tier 1, so an audit step at a later place always sees the joined columns.
  - Against: tier 1 then holds cleaning, joins and any count that a later look-up join needs, so "tier 1 cleans, tier 2 computes" (part 2) is not true for every recipe.
  - Reopens: nothing.
- **(b) Allow a join with a look-up table in tier 2 of a join; keep the refusal for the metadata.**
  - What you would see on the demo: nothing has to change; the inner join with the list of genes of `ST22_Anchor` may stay in tier 1 or move to its tier 2. A recipe could count genes in tier 2 and then join the count with the list of genes of interest in the same tier, with no derived table. A join with any other table (the metadata or a results table) written in tier 2 is still refused, with a plain line.
  - For: it reads "later joins" (D-0523) as a later tier, as the review session read D-0510 ("joins of other tables may be in tier 2 or later", its reading); a look-up join after a count needs no extra table.
  - Against: a join in tier 2 adds a table to the story of the data at tier 2. On screen, the look-up table enters the lineage after the computations, and an inner join there removes rows after every place of tier 1 (on the demo, the genes not in the list).
  - Reopens: no line of your ledger. It changes the rule of the recipe format specification and of the architecture decision on the three tiers quoted above. "A named join takes only source tables" (D-0344) is not reopened: a look-up table is a source table, listed among the join's tables.
- **(c) Neither: say what you meant.**

No recommendation: your two sentences fit both readings, and the demo needs neither change.

### Next: the questions that shape the screens

#### 3. With the earliest places ticked, is a later place a line you can tick, or only a drawing?
- **Situation:** you wrote "so maybe lineage should be represented as a propagation eg. original -> T1 -> T2 so the user sees that it affect the next one" (D-0508). Depends on question 1.
- **Today:** no such dialog.
- **Question:** in the dialog, is each later place a line with a tick box, or only part of a drawing under the ticked line?
- **(a) Every place is a line; the later ones start unticked.**
  - What you would see (under 1 b): the 13 ticked lines, and below each, unticked lines such as "MLST_with_metadata, end of tier 2".
  - For: every choice is one click away.
  - Against: in the review of the default ticks, the user viewpoint read unticked lines as "the entity stays there", the opposite of the truth.
  - Reopens: nothing. It is the option as it was put to you on 22 November (D-0501). The review session read your answer of D-0508 as "no unticked lines for the later tables" (its reading, not your words).
- **(b) Only the ticked places are lines; under each, its propagation is drawn, with no tick box.**
  - What you would see: "[x] MLST_with_metadata, end of tier 1", then "→ tier 2 → mlst_bar, year_distribution".
  - For: your words "represented as a propagation"; a short dialog.
  - Against: to write at a later place you must start the step from that table.
  - Reopens: D-0093 ("the user need to choose at which point (node) to apply") and D-0355 ("That is the choice of the user - because the user decide the scope"); D-0316 in part (your "A": every place the step can reach is a tick line, in the review session's words) and D-0346 in part (one tick line per distinct table: your "Tick").
- **(c) As (b), with one control "choose other places" that opens the lines of (a).**
  - For: the drawing first, and every place one click away. Against: two views of the same list. Reopens: nothing.

Recommendation (mine): (c). It shows the propagation as you described it, and keeps the choice of every place that D-0093 and D-0355 give you.

#### 13. Does HOME get a lineage picker, and where does an audit step start?
- **Situation:** you wished for "an independent lineage picker ... so you can pick every original data and see all lineages that goes from there" (D-0496), wrote "I like the idea of outline at the base" (D-0508), and asked "imaging the case where there is something to remove (filter) that is not seen at the mlst_bar level ... I am just wondering of how to make it navigate" (D-0518). Whether a picker is built is not decided (D-0496).
- **Today:** HOME shows only the stages of the open plot's table.
- **Question:** does HOME get a picker that opens any table at any stage, and does "Send to Audit" start from the table you view?
- **(a) Yes:** an outline that starts at the original data files; any table, any stage; a step starts from the table you view. You would open `MLST` after tier 1, or a table no plot reads. For: your wish; it is how a table no plot reads can be viewed (D-0457); a step starts where you see the column ("to select the user must be in a view of Tx that has the column", D-0175). Against: one more view to learn.
- **(b) A picker for viewing only;** a step starts from the open plot's table, and the dialog reaches the earlier places. For: one way to start a step. Against: a wrong row seen in tier 1 of `MLST` is removed by starting from `mlst_bar`.
- **(c) No picker;** a table no plot reads opens by its name in the data preview. For: no new view. Against: the story from the original files is not shown, against your words "YES the story of is what I want to show" (D-0508).
- Reopens: nothing for (a) and (b).

Recommendation (mine): (a).

#### 15. Does an export with only the Publication part hold the original recipe? (part 6.3)
- **Today:** when an audit exists, the original recipe is in no part.
- **(a) No;** it is in the Reproducibility part, with the audit recipe (D-0490). Reopens: D-0389 in part ("1. yes must.").
- **(b) Yes;** every export holds it, with one line saying why. What you would see: the Publication zip of the demo holds `1_test_data_ST22_dummy.yaml` beside the plots and the report. Reopens: D-0192 in part ("And I suggest to remove the recipe from the mode 1").
- **(c) When an audit exists, the Reproducibility tick cannot be turned off.** Reopens: D-0298 in part (one or both ticks: your answer was "A"; the words of the option are the review session's).

No recommendation: it depends on what you meant by "always"; D-0389 is the later line.

#### 26. Sessions saved before the change to one form of an audit step: refused and removed, or kept?
- **Situation:** when the audit steps move to the audit recipe, the session file gets a new form. You decided once, for sessions that held "My view": "A - best to clean all old sessions" (D-0312). That decision was about "My view". No decision of yours covers this change: it is a decision that is needed and does not exist yet.
- **Today:** a session file holds the audit steps in the app's own list, at the table of each plot; the app refuses a file of an older form with a plain line (D-0312).
- **Question:** after the change, what does the app do with a session file of today's form?
- **(a) Refused and removed, as for "My view".**
  - What you would see: opening it gives a plain line: it was saved by an older version of the app and cannot be opened. The list of old session files is shown before they are removed, and what was removed is reported.
  - For: one form only; nothing is converted.
  - Against: the audit steps and reasons of those sessions are lost, unless you exported them before.
  - Reopens: nothing.
- **(b) Converted once into the new form.**
  - What you would see: the session opens; each old step appears as a "this plot only" step, with its reason, at the same place it was written; a line says the session was converted.
  - For: nothing is lost.
  - Against: the log of a converted step has no warnings, because none were recorded when it was written, although the log must hold the warnings shown (D-0478).
  - Reopens: nothing written; it differs from the way you chose for "My view" (D-0312).
- **(c) Refused, but not removed.**
  - What you would see: the same plain line as (a); the file stays where it is, so that you can export it or delete it yourself.
  - For: nothing is deleted without you.
  - Against: a file the app cannot open stays in the list of sessions.
  - Reopens: nothing.

No recommendation: it depends on whether the sessions you keep today hold audits you need. Suggestion: whatever you choose, export an audit you want to keep before the change.

### Can wait: the rest of the audit dialog (9 depends on question 1)

#### 4. A filter that belongs to one plot only: which places start ticked?
- **Situation:** your example: a year with so few entities that you hide it from one plot only, "but then it will do the filter in T3 and not T1" (D-0199). Depends on questions 1 and 3.
- **Today:** every step is written at the open plot's table, so this case works today.
- **Question:** does a filter on a column other than the entity key start with the same default ticks as a removal of an entity?
- **(a) One default for every step: the earliest places.**
  - What you would see, hiding the year 2023 from `mlst_bar`: the earliest places ticked; 13 plots lose 2023 unless you untick them and tick "this plot only".
  - For: one rule. Against: your year case needs unticking every time. Reopens: D-0199 in part ("but then it will do the filter in T3 and not T1"): by default the step would go to the earliest places, not to the plot's own table.
- **(b) The default depends on the kind of step:** a removal by the entity key starts at the earliest places; any other filter starts at the place where you started it.
  - What you would see: "[x] this plot only: mlst_bar"; 1 plot changes.
  - For: it follows both of your cases: "my most frequent use case is the sample is bad" (D-0194) and your year case (D-0199). Against: two rules to learn.
  - Reopens: D-0508 in part: "we tick low" would hold for a removal by the entity key only.
- **(c) Always the place where you started; the earliest places are one click away.**
  - What you would see, removing the entity `10668076` from `mlst_bar`: "[x] this result only: mlst_bar" ticked; the earliest places listed, unticked.
  - For: you see first what you touched. Against: a bad entity is removed from one plot unless you click. Reopens: D-0508 ("we tick low (early) near the original table").
- **(d) Neither: say what you mean.**

Recommendation (mine): (b). A removal of an entity then reaches what depends on it, and a filter on a value stays where you built it, unless you tick more.

Added by the goals review: this question holds as written under options (a) and (c) of question 28. Under (b) of question 28, the same choice is made in results: for an entity, every result that holds it starts ticked; for a condition on another column, the result where you started.

#### 5. A place where the entity key is made again: ticked, or only a note?
- **Situation:** you listed the cases where the propagation does not work, "except keys recomputation, key under another column name weiht no join, key rewritten by a step", and asked "could we detect those cases and inform about the possible got you" (D-0508). Depends on question 1.
- **Today:** code that follows the lineage, built but used on no screen yet, marks such a place with a note; the demo has no such place.
- **Question:** when a step makes the entity key again (for example a join that computes it from another column), is that place ticked by default?
- **(a) Ticked, with the line "the entity key is made again here".**
  - What you would see: one more ticked line, with that sentence. In a small test recipe of the review, the entity then leaves that table; without the tick it stayed.
  - For: for the key, that place is the start of a branch, so it is "the earliest place of each branch" (D-0501). Against: the app ticks a place further down than where you started.
- **(b) Not ticked; a note on its line:** "the entity key is made again here: a removal at the earlier places may not reach this table".
  - For: your words "inform about the possible got you". Against: unless you tick it, the entity stays there.
- Reopens: nothing for (a); for (b), D-0501 in part ("the default will need to include the earliest place of each branch").

Recommendation (mine): (a). It is the earliest place of that branch for the key, and its line still says why it is ticked.

#### 6. A table that no plot reads, reached by the dialog: ticked like the others?
- **Situation:** you answered "Yes" when asked whether such a table is "a tickable line in the normal dialog, ticked by default, like the others" (D-0451; the question's words are the review session's). Since then the default became "tick low" (D-0508). Depends on question 1.
- **Today:** no such dialog; the code that follows the lineage (used on no screen yet) returns such a table as a line and marks that no plot reads it.
- **Question:** does such a table follow the same default as any other table, and does its line say that no plot reads it?
- **(a) The same default; its line adds "no plot reads this table; it is in the export".**
  - What you would see (under 1 b, from `mlst_bar`): the 4 joins that no plot reads (`FastP_with_metadata` and three others) among the 13 ticked lines, each with that sentence.
  - For: it is what you answered; the export of that table follows your step. Against: a line about a table you cannot open today (question 13).
- **(b) Never ticked by default; listed with the same sentence.**
  - For: nothing changes where you cannot look. Against: the export of that table keeps the entity unless you tick it.
- Reopens: (b) goes against your "Yes" of D-0451.

Recommendation (mine): (a), as you answered.

#### 7. Which number does each ticked line show?
- **Situation:** the dialog shows the rows concerned before you confirm (D-0316); you wrote "so 0 means it does not find the value" (D-0508); the number itself is not decided (D-0508).
- **Today:** no such dialog.
- **Question:** which number does a ticked line show?
- **(a) A pair:** "Rows with this value here: 1 before, 0 after."
  - For: true at every place, also at a place you tick by hand after an earlier one; "0 before" says exactly "it does not find the value". Against: two numbers per line.
- **(b) One number:** "Rows removed here: 1."
  - For: one number, true at every place ticked by default. Against: at a place you tick by hand after an earlier one it reads "Rows removed here: 0", although the value was there before the earlier step removed it.
- Reopens: nothing.

Recommendation (mine): (a). It stays true wherever you tick.

#### 8. A step written after a computation over all entities: does its line say so?
- **Situation:** some tables compute values over all entities (on the demo, a z-score in tier 2 of `QA_population_zscore`; a z-score is explained in part 2). You do not want warnings about natural effects further down: "If then there is an aggregation its normal that the count differ because it has less data" (D-0501). The review session read that answer as settling the tables further down that compute across entities: no warning about them (its reading, not your words). This question is only about the place where the step is written.
- **Today:** no such dialog.
- **Question:** when a step is written AFTER such a computation in the same table, so that the other entities' values were computed with the removed one, does that line say so?
- **(a) One plain line at that place:** "The values of this table were computed with this entity included; the step removes it after."
  - What you would see: on the demo, only if you tick by hand the end of tier 2 of `QA_population_zscore`.
  - For: otherwise the remaining values carry the removed entity without a word; it is a check where the step is applied, as you prefer (D-0508). Against: one more line, rarely.
- **(b) No line;** the good-practice page explains it. For: a shorter dialog. Against: you must know it yourself.
- Reopens: nothing; it speaks of the place where the step is written, not of a table further down.

Recommendation (mine): (a).

#### 9. After Apply: does the app count where the removed value is still found?
- **Situation:** only a run can tell what happens in the tables after the place where a step is written (two reviews, 22 November). You wrote "Id rather the check is more where you apply it - knowing it will affect the downward recipe than actually trying to capture the removal of something that by default should not exist" (D-0508). Depends on question 1.
- **Today:** nothing.
- **Question:** after Apply, does the app count the rows where the removed value is still found?
- **(a) No count;** you check with the audited results, Compare and the row counts of the data preview. This is your stated preference.
- **(b) One count after the build, shown only where the value is still found:** "Still found after the audit: the table of `miaou`, 3 rows." This goes against your stated preference.
- **(c) As (b), plus a second count that ignores upper and lower case and spaces** (it finds a key rewritten by a step). This also goes against your stated preference.
- What you would see on the demo: under 1 (a), (b) names the 3 quality tables where the entity stays with empty metadata; under 1 (b), nothing for a default removal.
- Reopens: nothing written; (b) and (c) go against your words of D-0508 quoted above.

Recommendation (mine): (a) if you choose (b) in question 1; (b) if you choose (a) in question 1, because then three plots keep the entity with empty metadata and nothing else tells you.

### Can wait: the audit log

#### 10. The audit log: what does it keep of a warning?
- **Situation:** the log always goes into the export, with the warnings shown, "so we can show that the user has been warned and that is is a user decision" (D-0478).
- **Today:** there is no audit log.
- **Question:** does the log keep the words of a warning as you saw them, the facts behind it, or both?
- **(a) The words as shown**, for example "A left join keeps the rows of its first table; the metadata is not ticked." For: a reader sees what you saw. Against: hard to search by table or number.
- **(b) The facts**: the kind of note, the table, the numbers. For: easy to search. Against: the words you read are not kept.
- **(c) Both.**
- Reopens: nothing.

Recommendation (mine): (c). Your two reasons need both: "so we can show that the user has been warned" and "That will also allow us reviewing if there are complains what is not working and where" (D-0478).

#### 11. The audit log: does it mark how each place was chosen?
- **Situation:** a reader of the log must tell your choice from the app's default; this is not decided (D-0508).
- **Today:** there is no audit log.
- **Question:** does the log say, for each place, how it was chosen?
- **(a) Every place, marked** "ticked by default", "ticked by you", "unticked by you" or "left unticked by default". A log line: "MLST_with_metadata, end of tier 1: ticked by default; written."
- **(b) Only the places where a step was written**, marked "ticked by default" or "ticked by you".
- **(c) No marks;** the log lists where steps were written.
- For (a): it shows "that is is a user decision" (D-0478) also for what you left out. Against (a): a longer log.
- Reopens: nothing.

Recommendation (mine): (a).

#### 12. The audit log: a step you cancel before confirming?
- **Situation:** you asked the log to hold "information for all the steps that are applied" (D-0478); a cancelled step is not decided.
- **Today:** there is no audit log.
- **Question:** does the log keep a step you cancelled before confirming?
- **(a) No.** For: your words name the steps that are applied. Against: a warning that made you change your mind is not recorded.
- **(b) Yes, one line:** the step, the warnings shown, "cancelled". For: a reviewer sees what made you change your mind. Against: the log holds steps that are in no result.
- Reopens: nothing.

Recommendation (mine): (a), by your words "all the steps that are applied".

#### 25. The audit log: its file name and form in the bundle
- **(a) A plain text file a person reads.** **(b) A structured file beside the audit recipe that a person can still read.** **(c) Both.**
- Reopens: nothing.

Recommendation (mine): (b). One file, readable by a person and searchable by table (question 10).

### Can wait: the export

#### 16. Where does the export show the original plot?
- **Situation:** you decided that the export shows both: "10. In the export we need to be able to see original and modified plot." (D-0147). Only WHERE is open.
- **Today:** every exported plot is the audited one.
- **(a) Both pictures in the Publication part when an audit exists,** for example `mlst_bar_original.png` and `mlst_bar.png`. Reopens: nothing.
- **(b) The original only by re-running the original recipe of the Reproducibility part.** Reopens: D-0147 in part.
- **(c) Both pictures in the Reproducibility part only.** Reopens: nothing.

Recommendation (mine): (a). A reader of the Publication part then sees both without running anything.

### Can wait: the words and the defaults on screen

#### 18. The defaults when a recipe opens
- **Today:** Exploration, and the data choice on T3 (a builder's choice). You wrote "the plot by default was showing T3 but we could choose earlier T for preview" (D-0508).
- **(a) As built:** under `mlst_bar`, the table it is drawn from (33 rows).
- **(b) Exploration and Source:** the MLST file as read.
- **(c) The mode and the table last used in this session.**
- Reopens: nothing.

Recommendation (mine): (a). The table under the figure is the one it is drawn from, and the earlier stages stay one click away, as you wrote.

#### 19. The words on screen for the stages
- **Situation:** you decided the choices Source, T1, T2 and T3 (your "B", D-0310); the words shown on screen for them were not decided.
- **Today:** "Source", "T1", "T2", "T3".
- **(a) As built.** What you would see: the four short names, as in the recipe.
- **(b) Plain words:** "Original data files", "Cleaned tables", "Computed tables", "Result". What you would see: words a user who is not a developer reads at once; the link to the tiers of the recipe is not shown.
- **(c) Plain words with the stage:** "Cleaned table (T1)". What you would see: both.
- Reopens: nothing for (a); for (b) and (c), D-0310 in part: the names Source, T1, T2 and T3 were part of the option you chose.

Recommendation (mine): (c). A user who is not a developer reads the words, and the stage names link the screen to the recipe.

#### 20. Comparisons on dates in the Filters panel
- **Situation:** you decided "I think we will not need greater less than comparison for text ... I would go for not offered", and "the pickers adjust to the type of the column" (D-0061); the ledger records a date picker as part of that decision. Comparisons on dates were not named.
- **Today:** a date column gets every comparison and "between" (a builder's choice); the rule file says "not offered".
- **(a) As built.** **(b) A list of values only.**
- Reopens: nothing.

Recommendation (mine): (a). Dates have an order, and "between two dates" is a common filter.

#### 23. Which colour means what in a lineage?
- **Situation:** you allowed new colours and wrote "i like green as good" (D-0463); red is for what the app cannot follow (D-0460).
- **(a) Green = "this table does not change"**, red = "the app cannot follow this YET", and every colour with a word or a symbol beside it (the review session's reading of D-0463).
- **(b) Green = "the step is written here"**, red as in (a).
- **(c) You choose from a picture with two or three sets** before anything is built.
- Reopens: nothing.

Recommendation (mine): (c).

### Can wait: clean-up

#### 21. Which tiers may a table that no plot reads have?
- **Situation:** "I should have considered tables that no plot read at least t1 is also part of a lineage - T1+T2 and T1+T2+T3" (D-0451), and "Why Tier 2 refuses ? its still data wrangling" (D-0514).
- **Today:** the recipe check refuses tier 2 steps on such a table, because nothing would run them.
- **(a) Tier 1 only, as built.** Reopens: it goes against your words above.
- **(b) Tier 2 allowed: built, shown in the data preview and exported.** Reopens: nothing.
- Under form 3 (question 2), a table read only by a derived table is read, so its tier 2 runs anyway.

Recommendation (mine): (b).

#### 22. A look-up table with an entity key column: should the recipe check advise?
- **Situation:** the three blocks are the three kinds of table (D-0513); you decided that `VirulenceFinder` moves to `data_schemas` ("VirulenceFinder moves", D-0523), and the move waits for the one move of the demo recipes (D-0525).
- **Today:** no advice.
- **(a) An advice, never a refusal:** "Suggestion: this look-up table has an entity key; if it holds results about the entities, move it to data_schemas." On the demo today it would name `VirulenceFinder`.
- **(b) No advice;** the good-practice page only.
- Reopens: nothing.

Recommendation (mine): (a). It is an exact fact of the recipe, and it would have found the demo's case by itself.

#### 24. The recipe upload code that no screen offers
- **Situation:** the app holds code that would copy an uploaded recipe over a recipe of the same name, but no screen offers it. You decided "upload under same name refused" (D-0390) and "Yes off unless deployment place required it." (D-0440).
- **Today:** nothing happens; the code cannot be reached.
- **(a) Remove the code now;** an upload is built when a deployment declares an upload place, with your rules (an existing name refused; "a warning if trying to write on a file name name - the user delete in his file system or choose a new name", D-0437).
- **(b) Rebuild it now,** offered only where a deployment declares an upload place, with the same rules.
- Reopens: nothing.

Recommendation (mine): (a). No deployment declares an upload place today, so no user can reach this code; and you named the risk yourself: "the old things that exist are taken again because they are not build and this mixes with the decisions" (D-0507).

### Later

#### 14. Where does the picker open? (only if 13 is (a) or (b))
- **(a) A window over HOME that can stay open beside the figure**, as you said: "it can be in a popup window" (D-0496). Reopens: nothing.
- **(b) The right panel in Exploration,** so the figure stays in sight (the user viewpoint of the review). Reopens: D-0383 ("yes (but it will be empty at least for now)"), D-0375 ("so ok to hide the right side panel in home when the audit mode is inactive") and D-0385 (your "yes" to "will it close back if I move from audit to exploration?").
- **(c) Both, with one switch:** "it can be coded so its easier to change place" (D-0084). Reopens: as (b) for the panel.

Recommendation (mine): (a), your proposal, which reopens nothing.

#### 17. The Reshuffle: how is its seed step written, or is it removed from HOME?
- **Situation:** you decided "A - but then we need to be able to add it as a step at the correct place in audit", and "when the user is happy with the reshuffle a seed step with the reshuffling needs to be written"; "this reshuffling is not critical for now" (D-0341).
- **Today:** in Audit mode a click writes a new seed for the plot (the number that fixes the random placement of points), with no reason and no Apply, and it is exported.
- **Question:** how is the seed step written in the audit recipe?
- **(a) A new kind of audit step at the plot's own place, with a reason.**
  - What you would see: after a Reshuffle, a step "new arrangement of the random points of this plot" in the list of audit steps, with a reason, like a filter.
  - For: the new arrangement is recorded and exported with its reason. Against: an audit step that removes no observation. Reopens: D-0322 in part ("A : for now yes only filter and drops").
- **(b) A second list in the plot entry of the audit recipe, run after the layers written in the recipe,** like the second list of a tier (my idea, not studied).
  - What you would see: the same as (a) on screen; the difference is only in the file.
  - For: the plot's own part of the recipe stays untouched. Against: not studied. Reopens: nothing.
- **(c) No Reshuffle in HOME** (added by the goals review).
  - What you would see: no Reshuffle button; the random points of a plot are always placed as the recipe says, with its seed ("Fixed 0 by default fixed and simple", D-0056).
  - For: the figure a reader sees is the one the recipe fixes, not one picked among several arrangements (G3); no new kind of step; the audit stays a removal of observations (G4).
  - Against: a user who finds an arrangement unclear asks the author to change the seed in the recipe.
  - Reopens: D-0341 ("A - but then we need to be able to add it as a step at the correct place in audit").
- **(d) Neither: say what you mean.**
- A fact for (a) and (b): today the export carries a new seed by writing it into the plot's own part of the recipe copy it exports. The audit recipe you decided keeps the author's parts untouched (D-0332), so it cannot hold the seed there. Until (a) or (b) is built, an audited reshuffle cannot be re-run to the same picture from the audited part of an export. (The code lines are in `GOALS_REVIEW.md` section 3.)

Version 3 gave no recommendation, because the study you asked for in D-0341 had not been made. Recommendation of the goals review (mine): (c), for the reasons under (c); it replaces "no recommendation" for this question.

---

## 9. What nobody checked

- No browser was used, and no screen of the dialog or of a picker exists: every "what you would see" is described, not shown.
- The goals review (part 0 and `GOALS_REVIEW.md`) ran nothing new: its path is a design, its dialog does not exist, and its numbers on the demo are the runs of this study (part 6.1). Its section 9 lists the ledger lines and the code lines it read.
- The runs on "the earliest place" are three runs on the demo recipe, one entity each, through code without a screen and not through HOME, with the places listed by hand.
- The recipe redesign was read, not run by me; its own runs are on a part of the demo recipe. The details of what was and was not checked are at the end of `BUILD_ORDER.md` and `RECIPE_REDESIGN_REVIEW.md`. The authors of the proposal ran the dialog walk-through again for me on the demo slice and the reads summary (`RECIPE_PROPOSAL_dialog_walkthrough.md`); the real lineage walk was not run on it (it does not know derived tables), and the lines of the dialog are reasoned from the columns of each place. I ran their walk-through script once more and got the same numbers for the reads summary.
- The fact that the recipe check refuses every join outside tier 1 was read in the code, and its test was run in this pass (it passes: a join in tier 2 of a join, in tier 2 of a source table and in tier 3 of a plot are refused). The authors of the proposal also ran it with a join of the metadata in those three places.
