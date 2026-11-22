# The whole picture: how HOME is meant to work (2026-11-22, version 2)

A study, not a decision: nothing is built from it before you answer (D-0507). Version 2 was rewritten after three reviews and your words of the same evening. Other files in this folder: `DIFFERENCES.md` (every difference between the app and your decisions, and where your decisions meet), `PARTS_TABLES.md` (the full tables, part by part), `RECIPE_REDESIGN_REVIEW.md` (the details of part 7), `BUILD_ORDER.md` (for the builders).

---

## 1. How to read this

1. Parts 2 to 5 are the short picture (about 15 minutes). Parts 6 to 9 hold the double readings, the recipe redesign and your questions.
2. Your words are between quotation marks, exactly as you wrote them. The number after a sentence, for example (D-0508), is its line in the decision ledger.
3. "As the review session read it" marks a reading of your words, not your words. "Recommendation (mine)" is mine. "My wording" marks a definition that no decision of yours gives.
4. The app is data agnostic. On the demo recipe the entity is a sample and the entity key is `sample_id`. Everywhere else this document says "the entity".
5. Where I only read the code, or ran something on the demo recipe only, I say so. Nothing here was seen on a screen.

---

## 2. The words

- **Original data file:** a file as the app reads it, for example the MLST results of the demo. The app never changes it (D-0509).
- **The three blocks of a recipe, the three kinds of table:** `data_schemas` hold results of analysis about the entities; `metadata_schema` holds the information about the entities, one table; `additional_datasets_schemas` hold look-up tables, such as a list of genes of interest, used in later joins (D-0513; the link of each block to a kind is the review session's reading).
- **Tier 1:** clean each table, and join it with the metadata where that is needed (my wording; the join with the metadata in tier 1 is yours, D-0523).
- **Tier 2:** compute, for example add a column or count (my wording).
- **Tier 3:** the table a result is made from. It is still data, never the plot (D-0514). With no steps of its own it is the same table as tier 2 (D-0343).
- **A join:** a table made by putting several tables side by side on a key column.
- **A result:** what a group shows: a plot or a table (D-0485).
- **The lineage, or the story of the data:** the path from the original data files to a result (my wording).
- **A place:** one table at one tier, where an audit step can be written (my wording).
- **The reach of a place:** how many tables and plots depend on it (D-0346).
- **Exploration and Audit:** the two modes of HOME. In Exploration nothing is saved. In Audit mode you write steps, each with a reason (D-0016).
- **An audit step:** a filter, a column drop or a removal by the entity key, with a reason (D-0322).
- **The audit recipe:** a copy of the recipe that holds your audit steps. The original recipe is never changed (D-0143).
- **The audit log:** the list of steps added and removed, with who, when, the reason and the warnings shown (D-0478; the list of what it holds is the review session's reading).
- **The audit record:** a short file beside the audit recipe with its fingerprint (a hash), so that a hand edit is seen (D-0333).

---

## 3. One diagram and one sketch

**The stages, on the demo path that ends in the plot `mlst_bar`.**

```text
ORIGINAL DATA FILES (read as they are; never changed)
   MLST results file                      metadata file
          |                                     |
TIER 1 of each table (clean)
   MLST: keep 3 columns;                  metadata_schema:
   "Non Determined" for an unknown type     no step
          |                                     |
          +------------------+------------------+
                             |
TIER 1 of the joined table: the join with the metadata is always here
   MLST_with_metadata: MLST joined with the metadata on the entity key
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

**The audit dialog, as decided.** Nothing in this sketch is built. The lines that start ticked are question 1.

```text
+-- Create audit step -----------------------------------------------------+
| Remove the rows where sample_id = 10668076    (the entity key, demo)     |
| Reason: [ sequencing failed, lab notes of 12 April                    ]  |
|                                                                          |
| Where the step is written (one line per distinct table):                 |
|  [x] <the earliest place>              reach: N tables, M plots          |
|        rows with this value here: ...           (question 7)             |
|  [ ] <a later place>      (a line, or only a drawing: question 3)        |
|  [ ] this plot only: mlst_bar                   reach: 1 plot            |
|  [-] <a place the app cannot follow YET>    (red, no tick box)           |
|                                                                          |
| Plots:  mlst_bar           table changed      picture changed            |
|         year_distribution  table changed      picture changed            |
| Notes: only where the app can follow a silent case                       |
|                                                                          |
|  [ ] Remove from all the data   (off by default; its list opens first)   |
|                                              [ Cancel ]   [ Confirm ]    |
+--------------------------------------------------------------------------+
```

---

## 4. The picture

**The story of the data, on `mlst_bar`.**
1. When a recipe opens, the app builds every table and draws every plot once (D-0326).
2. The original data files are read as they are, and "Source" in HOME shows a file as read (D-0310).
3. Tier 1 cleans each table: `MLST` keeps three columns.
4. Still in tier 1, the joined table `MLST_with_metadata` joins the MLST results with the metadata on the entity key (D-0523).
5. Tier 2 computes: it adds an era and keeps the years 2023 to 2025.
6. Tier 3 is the table the result is made from; `mlst_bar` has no steps of its own, so it is the same table as tier 2 (D-0343).
7. The result is the plot `mlst_bar`; a result may also be a table (D-0485; decided, not built).

**Looking, in Exploration.**
- You see one plot, the result, and under it the table you choose; a filter changes only that table, is never saved and never exported (D-0327).
- A filter belongs to the table you view, not to the plot (D-0506; decided, not built), and it is cleared when the table you view changes (D-0311).
- It is also cleared when you switch between Exploration and Audit (D-0361).

**One audit, on `mlst_bar`.**
1. In `mlst_bar` you see an unexpected sequence type, and the table under it shows the sample (the entity of the demo) that carries it; your lab notes say its sequencing failed.
2. You switch to Audit mode, and the right panel opens (D-0375).
3. You open the table where you see the entity key and ask to remove this value, with a reason (not decided: question 13 asks from which tables a step can start).
4. The dialog lists the places where the step can be written, one line per distinct table, with its reach (D-0346; decided, not built).
5. The earliest places start ticked (D-0508; not decided which: question 1).
6. For each ticked place you see the rows concerned, and for each plot "table changed" and "picture changed" (D-0318; decided, not built; the number is question 7).
7. You get no warning about what happens further down; a note appears only where the app can follow a silent case, and a red line where it cannot follow it YET (D-0501; decided, not built).
8. For an entity that must leave everything, a separate choice, "Remove from all the data", is off by default, lists every table first, and lets you untick one (D-0499; decided, not built).
9. You confirm, and the step is written into the audit recipe; the original recipe never changes (D-0102; decided, not built).
10. Only the tables that changed are run again (D-0325; decided, not built).
11. You see the audited plot, and Compare shows the original and the audited plot side by side (D-0147).
12. You can take any one step out again with "Remove step" (D-0314; decided, not built).
13. Your session keeps the audit recipe, its record and the audit log in a folder `audit/` (D-0319; decided, not built).
14. The export holds the audited results, the original and the audit recipe, the record and the log; exploration is never in it (D-0490; decided, not built, except that exploration is already never exported).

---

## 5. What is wrong today: the four things that matter most

All four were checked in the code.

**1. Where an audit step is written.**
Today the app writes an audit step only at the table of the open plot (tier 3), and its dialog asks "This plot only / All plots / All plots except…", not where in the story the step goes.
You decided: "We had said we can send at each tier - so we need to send the correct tier" (D-0507).
The difference for a user is that she cannot remove an entity before a join or from a table no plot reads, and a step for several plots is written once per plot.

**2. What you can see before you write a step.**
Today HOME shows, for the open plot, the original files as read and the stages of the plot's own table only.
You decided: "YES the story of is what I want to show - this is why I wanted the lineages" (D-0508), and that a table no plot reads "Must be and yes must be viewabøenin the data preview" (D-0457).
The difference for a user is that on the demo she cannot open tier 1 of `MLST` or the 6 tables no plot reads, so she cannot look at the table where a step would be written.

**3. What an export of an audit holds.**
Today, when an audit exists, the export holds the steps with their reasons and, if its reproducibility box is ticked, a copy of the recipe in which each plot's join is forked with the steps added; it holds no original recipe, no audit recipe, no audit record with a fingerprint, and no log of added and removed steps with the warnings shown.
You decided: "when audit steps have been added the audit recipe is the truth - so the export must contain the recipe of the audit" (D-0324), the original recipe "1. yes must." (D-0389), and "it is then actually not optional anymore to add the log for the audit to the export" (D-0478).
The difference for a user is that an export of an audit cannot be re-run from the original recipe, and nothing in it proves that its recipe was not edited by hand or shows what she was warned of.

**4. A session saved before its recipe was edited.**
Today the app opens such a session with a warning, and applies the old audit steps to the changed recipe.
You decided: "so I would refuse - I would explain that the original recipe has been modified and that it needs to reanalyze and add the audit steps where they are done" (D-0362).
The difference for a user is that old steps can act on columns and rows that are no longer what they were when she wrote them.

The full list of 27 differences is in `DIFFERENCES.md`.

**One consequence for your saved work.** When the audit steps move to the audit recipe, the session file gets a new form. The app refuses a session file of an older form, as you decided for the redesign: "A - best to clean all old sessions" (D-0312). So the sessions you keep today will not open after that change.

---

## 6. Where two of your sentences can be read in two ways

### 6.1 The earliest place

Your sentences:
- "the earliest place of each branch - which is the original data basically" (D-0501);
- "we tick low (early) near the original table - so by default it is propagated in the lineage" (D-0508);
- "no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" (D-0509);
- "T has been removed - because we join all data sets with metadata in T1 when necesary (and not in other tiers) - and if No metadata join is needed. As we said the other data tables can be used in later joins." (D-0523).

**Reading A:** the default tick is tier 1 of each original table. For `mlst_bar`: `MLST` and `metadata_schema`.
**Reading B:** the default tick is the end of tier 1 of each table that joins the metadata. For `mlst_bar`: `MLST_with_metadata` and the 12 other tables that join the metadata. The original tables stay as read.

**What was run.** Three runs on the demo recipe, one entity each: two entities that are in every original file, and one that is not in the ResFinder file. They used the real data and the real engine, through the library's run of the audit copy, not HOME's screen. Version 1 of this document made the first run; a review reproduced it with the two other entities. All three show the same pattern.

| Removing one entity, on the demo | Reading A | Reading B |
|---|---|---|
| Started from `mlst_bar` | 2 lines ticked. 13 plots change. The entity stays in 7 plots: in 4 that never meet MLST or the metadata, and in 3 with its metadata emptied. | 13 lines ticked. 13 plots change. The entity stays only in the 4 plots that never meet the metadata. No metadata is emptied. |
| "Remove from all the data" | 11 places. The entity is in no plot. | 19 places. The entity is in no plot. 8 of the 11 original tables keep it at tier 1. |
| Your case: keep it in the quality results only (D-0499) | Untick FastP, Quast and Bracken: it stays in the 3 quality plots without its metadata, and in one more plot. | Untick 2 tables: it stays in exactly the 3 quality plots, with its metadata. |

The entity that is not in ResFinder stays in one plot fewer (6 and 3). The 3 quality plots are `qc_reads_horizontal_barplot` (it loses the source, the year and the country), `assembly_quality_dotplot` and `miaou`, a plot that draws the source (both lose the source and the country).

**Why they differ.** A left join keeps every row of its first table. In five joins of the demo the results table comes first and the metadata second; in two more a results table is the base and the metadata comes later in the left joins. Under reading A, from `mlst_bar`, the entity leaves the metadata but not FastP, Quast or Bracken, so their rows stay, with empty metadata. Under reading B the removal comes after the join, so the row leaves with its metadata.

**Limits.** The places of each reading were listed by hand: the lineage of `mlst_bar` back to its original tables, then forward from them. If the dialog also ticked the other original tables that meet the metadata in a join (FastP, Quast, Bracken, ResFinder, VirulenceFinder), reading A would empty no metadata (reasoned, not run). Whether those tables belong to the lineage of `mlst_bar` is not decided; as I read your words "So basic lineage is up to it can only go backwards when on its way up or forward when on its way backwards" (D-0451), they do not.

Question 1 asks you to choose.

### 6.2 The filters on a switch of mode: an error in the records, not a question

Your decision of 20 November stands: "8 - No we had decided to clear them- Only the steps applied in the audit are kept -> but then they are writen in the recipe" (D-0361). Two lines of 22 November (D-0505, D-0506) say, in the review session's words, "NOT decided: what a change of mode does to the filters". That is an error of the records, to be corrected. The app clears the filters on a switch, as you decided. No question, unless you want to change it.

### 6.3 The original recipe in the export

- 20 November, the later line: "1. yes must." to the question whether the export always contains the original recipe, because "if you need to redo the analysis then you will need to re-upload the recipe" (D-0389).
- 16 November: "I think that would be best to add the recipe to the reproducibility mode 2 - And I suggest to remove the recipe from the mode 1", and "when in audit it will be added anyway (via the audit_recipe)" (D-0192). Mode 1 became the Publication tick, as I read the later line D-0298.

**Reading A:** "always" means every export, the Publication part included.
**Reading B:** "always" means every export that holds the Reproducibility part, where you put the recipe on 16 November.

Question 15 asks you to choose.

---

## 7. How the recipe redesign fits the whole picture

You asked me to review the proposal for the recipe form (`tmpAI/panel/tables_as_results/refined/PROPOSAL_FOR_THE_OWNER.md`) from the whole picture (D-0526). The form stays your choice (D-0496). The details and the evidence are in `RECIPE_REDESIGN_REVIEW.md`.

**7.1 What you asked, in your words.**
- "No Tier 3 is not a plot - T3 is the data that goes into a plot ... its still data" (D-0514).
- A result is a plot or a table: "a plot entry actually should be a result_entry with either plot or table no?", and "yes result is the last stage (the tier that has the latest instructions in the recipe)" (D-0485).
- "Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before" (D-0516).
- "yes we need the `from:` this clarifies but still the hiearchy is unclear of where to place it" (D-0517).
- Your case: "one final result could be used on T2a but T2a could be used to produce one T3a for another final result - what would be done in this case ?" (D-0517).
- "I want the examples on how it would like like with all the tiers and both plot and data as result" (D-0517).
- Arguments of good practice and good data science, "not economical in term of changes to do" (D-0516).
- The table that is a result is exported: "so we shuold be able to export the table that is as result also" (D-0487).

**7.2 Does the proposal meet them?** Its recommended form is form 3. You set forms 4 and 5 aside, as the review session reported it ("we can exclude form 4 and I guess 5", D-0496).

| What you asked | Form 3 | Where in the proposal |
|---|---|---|
| Tier 3 is data | Yes: every data step is in the data part; a result only names a table | Part 1, Part 2.2 |
| A result is a plot or a table, at its last stage | Yes: `result: plot` or `result: table`; `from:` reads the table at its last stage | Part 1, Part 8 |
| Tier 3 defined like tiers 1 and 2, before the results | In shape yes, in name no: what you would write as a tier 3 becomes a table of its own (a derived table), with its own tier 1 and tier 2, defined before the results. The author no longer writes a "tier 3"; the word stays only for the audit's "this result only" | Part 1, Part 2.2, Part 8 |
| The place of `from:` | Yes: in a derived table, after its name, before its tier 1; in a result, in place of today's `target_dataset` | Part 1 |
| Your case T2a, then T3a, then another result | Yes, walked through on the demo with real numbers | Part 3 |
| Complete examples with all tiers, a plot and a table as results | Yes, on a part of the demo recipe | Part 2.2 |
| Good practice, not economy | Yes: the cost is shown as information only | Part 7 |
| The table result exported | Not in the proposal: it rests on your decisions D-0487 and D-0490 | not covered |

**7.3 The hierarchy, as one complete small example on the demo (form 3).** Shortened from the proposal: fewer columns, and the head of the file (`id`, the engines, `info`) left out. The names `derived_tables`, `results`, `result:` and `from:` are the proposal's; they are not decided (D-0487).

```text
1  source tables   data_schemas, metadata_schema,   tier 1, tier 2          read from a file
                   additional_datasets_schemas
2  joins           joins                            tier 1, tier 2          each ingredient read after its tier 1
3  derived tables  derived_tables                   from: ONE table;        that table read at its last stage
                                                    tier 1, tier 2
-  plot defaults   plot_defaults
4  results         analysis_groups -> results       result: plot | table;   a plot adds its drawing (mapping, layers)
                                                    from: ONE table
4a "this result only": written by the audit only, in the audit recipe
```

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
- *The places of an audit step.* A derived table is one more table, so one more place: its tier 1, and its tier 2 only while the entity key still exists there. For a removal by the entity key the earliest place is always further up (question 1), so the default ticks do not change (my assumption; asked to the authors of the proposal). New: a step written at a derived table changes only the results made from it, and "this result only" stays possible (D-0346).
- *The join with the metadata.* It stays a tier 1 step of a join of raw data tables (D-0523). A derived table is made from a table that already has the metadata ("derived tables should already have the metadata joined", D-0511), so it never joins it (as I read D-0511; whether a derived table may join anything is asked to the authors).
- *The story of the data.* Every summary gets a name and one definition, so the story is clearer, and one table longer. But "Table to view" (Source, T1, T2, T3) cannot show the whole chain of a result made from a derived table: the join's tier 2 that it reads is not among the four choices. This is your question of D-0518: "I am just wondering of how to make it navigate". The picker (question 13) would answer it; the proposal leaves it open.
- *A table as a result, and its export.* A table result is simply the last stage of one table, so the table on screen and the file exported are the same object. The proposal does not say how the export names it (your "Part 1 -A" of D-0490 names it from the result's id), nor what happens when a plot and a table read the same derived table.
- *The two parts of the reproducibility bundle.* Not changed: both parts hold recipes of the same form.
- *The comparison of original and audited (D-0489).* Easier: the result is one table at its last stage, the same for a plot and its table, so the pair to compare is clear.
- *The lineage picker.* A derived table has one parent (`from:`), so it is easy to draw in an outline.
- *The one move of the demo recipes (D-0525).* The form decides which keys every recipe and every Gallery example gets. The move, the names pass and the move of `VirulenceFinder` are one pass.
- *BLUEPRINT.* It must write this format without replacing a recipe by mistake and without losing comments (D-0495). Its map knows sources, joins and plots today; it needs a derived table and a table result.

**7.5 Where the proposal and the whole picture disagree, or leave a hole.**
1. The proposal's dialog walk-through ticks every place (D-0316). Your later default is "tick low" (D-0508), and which place is earliest is still open (question 1). The walk-through should be redone.
2. Two reading rules in one recipe: a join reads its ingredients after tier 1; `from:` reads its table after its last stage. Both are needed (the proposal shows that making joins read tier 2 would change results silently), so the recipe documentation must say both plainly.
3. "Table to view" for a result made from a derived table: what "Source" means there is open in the proposal (three readings), and the full chain is not reachable (7.4).
4. The export of a table result by its id, and of two results that read one table, is not in the proposal.
5. A table read only by a derived table: the recipe check refuses its tier 2 today. The proposal says the check must count a derived table as a reader. This meets question 21 (the tiers of a table no plot reads).
6. A result id written in two groups is not refused today: the second silently replaces the first (the proposal's flag 6). This is a defect of today, whatever the form.
7. The proposal's examples still use `ui_title` and `label`, which your names decisions remove or rename (D-0484, D-0468).

**7.6 What could be simpler, seen from the whole.**
- One level of derived tables for now: a derived table made from a source table or a join, not from another derived table. The story of the data then stays at most one table longer than today. Suggestion: the same "revisit if needed" as for joins of joins (D-0344).
- A join that takes a derived table as an ingredient would reopen "a named join takes only source tables" (D-0344). The proposal leaves it open (its point 10); nothing in your case needs it. Information.
- On screen, the last stage of a result could be called "Result" rather than "T3", as in the badge you accepted ("I like the badge that says result or earlier stage this is accepted", D-0487). "T3" would then need no explanation.

Recommendation (mine): form 3, with one level of derived tables for now, and the walk-through of the dialog redone with your default of D-0508. It meets what you asked on your own criteria (one table, one definition; a definition before its use; a plot and its table show the same numbers by construction), and the proposal's runs on a part of the demo recipe support it.

---

## 8. What stays yours to choose

You asked for the questions that block the most work first (D-0519). Questions 1 and 2 block the most: question 1 the audit dialog, question 2 the one move of the demo recipes and with it the names. Questions 3 to 12 complete the audit dialog and its log; most of them depend on question 1. Questions 13 to 25 are an annex.

### A. The two questions on the critical path

#### 1. Where is "the earliest place" that the dialog ticks?
- **Situation:** you decided that the dialog ticks the earliest places by default (D-0508), and your sentences can be read in two ways (part 6.1).
- **Today:** there is no such dialog; a step is written only at the table of the open plot.
- **Question:** is the earliest place tier 1 of each original table, or the end of tier 1 of each table that joins it with the metadata?
- **(a) Tier 1 of each original table.**
  - What you would see, removing one entity from `mlst_bar`: two ticked lines, "MLST, tier 1" and "metadata_schema, tier 1". After Apply, 13 plots change; the entity stays in 7, and in 3 of them with its metadata emptied (`miaou`, which draws the source, among them).
  - For: the step is written where the data enter, and a computation over all entities never sees the removed one.
  - Against: three plots change in a way you did not ask for (empty metadata); your case of D-0499 keeps the entity in the quality plots without its metadata.
  - Reopens: nothing (it is the literal reading of "which is the original data basically", D-0501).
- **(b) The end of tier 1 of each table that joins the metadata** (on a branch that never meets the metadata: the end of tier 1 of the first table its results read).
  - What you would see: 13 ticked lines, one per table that joins the metadata, for example "MLST_with_metadata, end of tier 1 (after the join with the metadata)". After Apply, 13 plots change; the entity stays only in the 4 plots that never meet the metadata; no metadata is emptied.
  - For: the step comes after the join with the metadata, as you wrote ("join with metadata must be done at T1 that would simplify removing of samples by key no", D-0510); the original tables stay as read; your case of D-0499 keeps the entity in exactly the 3 quality plots, with its metadata.
  - Against: 13 lines to read before you confirm, and the audit recipe shows the same step 13 times; a computation over all entities written in tier 1 after the join would run before the removal (not the case on the demo).
  - Reopens: nothing written; it departs from the literal words "which is the original data basically" (D-0501) and "near the original table" (D-0508).

Recommendation (mine): (b). It is the reading in which your reason of D-0510 holds, it empties no metadata on the demo, and it gives your case of D-0499 exactly. You may have meant (a): "near the original table" (D-0508) points to it. The evidence is three runs on the demo, with places listed by hand (part 6.1).

#### 2. The recipe form: do you confirm form 3?
- **Situation:** you asked for tier 3 defined like tiers 1 and 2 and before the results, a result that is a plot or a table, and the place of `from:` (D-0516, D-0517); the demo recipes are moved once, after this design is final (D-0525).
- **Today:** a result is a plot only, and its own tier 3 steps sit in the plot entry, after everything else.
- **Question:** do you confirm form 3, shown in part 7.3: every table defined in the data part (source tables, joins, then derived tables made with `from:` from ONE table), and results that only name one table?
- **(a) Yes, form 3.**
  - What you would see: the file of part 7.3; in HOME, the plot `mlst_bar` and the table `samples_per_country_year` as results; the summary has one definition, so its plot and its table show the same 6 rows.
  - For: one table, one definition; a definition before its use; to know which results a step changes you search one name.
  - Against: a step that only one figure needs (a sort, a filter) must become a named table; the author no longer writes a "tier 3"; a result made from a derived table cannot show its whole chain in "Table to view".
  - Reopens: D-0306 ("T3 : data plot specific (better explained)") and D-0063 ("The T3 is the data that goes to the plot BUT not the plot recipe"), because the author no longer writes a tier 3 in a result.
- **(b) Form 3, with one level of derived tables for now.**
  - What you would see: the same file (it has one level); a derived table made from another derived table is refused by the recipe check with a plain line.
  - For: the story of the data stays at most one table longer than today.
  - Against: a summary of a summary must be written in one derived table.
  - Reopens: as (a).
- **(c) Not yet.** You first settle how a user reaches the tables before a result (your question of D-0518, and question 13).
  - What you would see: no change; the one move of the demo recipes waits.
  - For: you choose the form with the navigation in front of you.
  - Against: the one move, and with it the names pass, waits (D-0525).
  - Reopens: nothing.

Recommendation (mine): (b). The evidence of the proposal (its runs on a part of the demo recipe) favours form 3 on your own criteria, and one level keeps the story short. Forms 4 and 5 are left out because you set them aside, as the review session reported it; say so if you want them back. After this question come the names of the keys and when a table result opens on the result: they are listed in `RECIPE_REDESIGN_REVIEW.md`.

### B. The other questions that block the audit dialog and its log

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
  - Reopens: D-0093 ("the user need to choose at which point (node) to apply") and D-0355 ("That is the choice of the user - because the user decide the scope").
- **(c) As (b), with one control "choose other places" that opens the lines of (a).**
  - For: the drawing first, and every place one click away. Against: two views of the same list. Reopens: nothing.

Recommendation (mine): (c). It shows the propagation as you described it, and keeps the choice of every place that D-0093 and D-0355 give you.

#### 4. A filter that belongs to one plot only: which places start ticked?
- **Situation:** your example: a year with so few entities that you hide it from one plot only, "but then it will do the filter in T3 and not T1" (D-0199). Depends on questions 1 and 3.
- **Today:** every step is written at the open plot's table, so this case works today.
- **Question:** does a filter on a column other than the entity key start with the same default ticks as a removal of an entity?
- **(a) One default for every step: the earliest places.**
  - What you would see, hiding the year 2023 from `mlst_bar`: the earliest places ticked; 13 plots lose 2023 unless you untick them and tick "this plot only".
  - For: one rule. Against: your year case needs unticking every time. Reopens: nothing.
- **(b) The default depends on the kind of step:** a removal by the entity key starts at the earliest places; any other filter starts at the place where you started it.
  - What you would see: "[x] this plot only: mlst_bar"; 1 plot changes.
  - For: it follows both of your cases: "my most frequent use case is the sample is bad" (D-0194) and your year case (D-0199). Against: two rules to learn.
  - Reopens: D-0508 in part: "we tick low" would hold for a removal by the entity key only.
- **(c) Always the place where you started; the earliest places are one click away.**
  - For: you see first what you touched. Against: a bad entity is removed from one plot unless you click. Reopens: D-0508 ("we tick low (early) near the original table").

Recommendation (mine): (b), because it follows both of your use cases.

#### 5. A place where the entity key is made again: ticked, or only a note?
- **Situation:** you listed the cases where the propagation does not work, "except keys recomputation, key under another column name weiht no join, key rewritten by a step", and asked "could we detect those cases and inform about the possible got you" (D-0508). Depends on question 1.
- **Today:** the library's walk of the lineage marks such a place with a note; no screen shows it; the demo has no such place.
- **Question:** when a step makes the entity key again (for example a join that computes it from another column), is that place ticked by default?
- **(a) Ticked, with the line "the entity key is made again here".**
  - What you would see: one more ticked line, with that sentence. In a small test recipe of the review, the entity then leaves that table; without the tick it stayed.
  - For: for the key, that place is the start of a branch, so it is "the earliest place of each branch" (D-0501). Against: the app ticks a place further down than where you started.
- **(b) Not ticked; a note on its line:** "the entity key is made again here: a removal at the earlier places may not reach this table".
  - For: your words "inform about the possible got you". Against: unless you tick it, the entity stays there.
- Reopens: nothing.

Recommendation (mine): (a). It is the earliest place of that branch for the key, and its line still says why it is ticked.

#### 6. A table that no plot reads, reached by the dialog: ticked like the others?
- **Situation:** you answered "Yes" when asked whether such a table is "a tickable line in the normal dialog, ticked by default, like the others" (D-0451; the question's words are the review session's). Since then the default became "tick low" (D-0508). Depends on question 1.
- **Today:** no such dialog; the library's walk returns such a table as a line and marks that no plot reads it.
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
- **Situation:** some tables compute values over all entities (on the demo, a z-score in tier 2 of `QA_population_zscore`). You do not want warnings about natural effects further down: "If then there is an aggregation its normal that the count differ because it has less data" (D-0501).
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

### C. Annex: the other questions

#### 13. Does HOME get a lineage picker, and where does an audit step start?
- **Situation:** you wished for "an independent lineage picker ... so you can pick every original data and see all lineages that goes from there" (D-0496), wrote "I like the idea of outline at the base" (D-0508), and asked "imaging the case where there is something to remove (filter) that is not seen at the mlst_bar level ... I am just wondering of how to make it navigate" (D-0518). Whether a picker is built is not decided (D-0496).
- **Today:** HOME shows only the stages of the open plot's table.
- **Question:** does HOME get a picker that opens any table at any stage, and does "Send to Audit" start from the table you view?
- **(a) Yes:** an outline that starts at the original data files; any table, any stage; a step starts from the table you view. You would open `MLST` after tier 1, or a table no plot reads. For: your wish; it is how a table no plot reads can be viewed (D-0457); a step starts where you see the column ("to select the user must be in a view of Tx that has the column", D-0175). Against: one more view to learn.
- **(b) A picker for viewing only;** a step starts from the open plot's table, and the dialog reaches the earlier places. For: one way to start a step. Against: a wrong row seen in tier 1 of `MLST` is removed by starting from `mlst_bar`.
- **(c) No picker;** a table no plot reads opens by its name in the data preview. For: no new view. Against: the story from the original files is not shown, against your words "YES the story of is what I want to show" (D-0508).
- Reopens: nothing for (a) and (b).

Recommendation (mine): (a).

#### 14. Where does the picker open? (only if 13 is (a) or (b))
- **(a) A window over HOME that can stay open beside the figure**, as you said: "it can be in a popup window" (D-0496). Reopens: nothing.
- **(b) The right panel in Exploration,** so the figure stays in sight (the user viewpoint of the review). Reopens: D-0383 ("yes (but it will be empty at least for now)"), D-0375 ("so ok to hide the right side panel in home when the audit mode is inactive") and D-0385 (your "yes" to "will it close back if I move from audit to exploration?").
- **(c) Both, with one switch:** "it can be coded so its easier to change place" (D-0084). Reopens: as (b) for the panel.

Recommendation (mine): (a), your proposal, which reopens nothing.

#### 15. Does an export with only the Publication part hold the original recipe? (part 6.3)
- **Today:** when an audit exists, the original recipe is in no part.
- **(a) No;** it is in the Reproducibility part, with the audit recipe (D-0490). Reopens: D-0389 in part ("1. yes must.").
- **(b) Yes;** every export holds it, with one line saying why. What you would see: the Publication zip of the demo holds `1_test_data_ST22_dummy.yaml` beside the plots and the report. Reopens: D-0192 in part ("And I suggest to remove the recipe from the mode 1").
- **(c) When an audit exists, the Reproducibility tick cannot be turned off.** Reopens: D-0298 in part (one or both ticks: your answer was "A"; the words of the option are the review session's).

No recommendation: it depends on what you meant by "always"; D-0389 is the later line.

#### 16. Does the export show the original plot beside the audited one?
- **Situation:** "10. In the export we need to be able to see original and modified plot." (D-0147).
- **Today:** every exported plot is the audited one.
- **(a) Both pictures in the Publication part when an audit exists,** for example `mlst_bar_original.png` and `mlst_bar.png`. Reopens: nothing.
- **(b) The original only by re-running the original recipe of the Reproducibility part.** Reopens: D-0147 in part.
- **(c) Both pictures in the Reproducibility part only.** Reopens: nothing.

Recommendation (mine): (a). A reader of the Publication part then sees both without running anything.

#### 17. The Reshuffle: how is its seed step written?
- **Situation:** you decided "A - but then we need to be able to add it as a step at the correct place in audit", and "when the user is happy with the reshuffle a seed step with the reshuffling needs to be written"; "this reshuffling is not critical for now" (D-0341).
- **Today:** in Audit mode a click writes a new seed for the plot, with no reason and no Apply, and it is exported.
- **Question:** how is the seed step written in the audit recipe?
- **(a) A new kind of audit step at the plot's own place, with a reason.** Reopens: D-0322 in part ("A : for now yes only filter and drops").
- **(b) A second list in the plot entry of the audit recipe, run after the author's layers,** like the second list of a tier (my idea, not studied). Reopens: nothing.

No recommendation: the study you asked for in D-0341 has not been made.

#### 18. The defaults when a recipe opens
- **Today:** Exploration, and the data choice on T3 (a builder's choice). You wrote "the plot by default was showing T3 but we could choose earlier T for preview" (D-0508).
- **(a) As built:** under `mlst_bar`, the table it is drawn from (33 rows).
- **(b) Exploration and Source:** the MLST file as read.
- **(c) The mode and the table last used in this session.**
- Reopens: nothing.

Recommendation (mine): (a). The table under the figure is the one it is drawn from, and the earlier stages stay one click away, as you wrote.

#### 19. The words on screen for the stages
- **Today:** "Source", "T1", "T2", "T3" (a builder's choice).
- **(a) As built.** **(b) Plain words:** "Original data files", "Joined tables", "Result". **(c) Plain words with the stage:** "Joined table (T1)".
- Reopens: nothing.

Recommendation (mine): (c). A user who is not a developer reads the words, and the stage names link the screen to the recipe.

#### 20. Comparisons on dates in the Filters panel
- **Situation:** you decided "I think we will not need greater less than comparison for text ... I would go for not offered" (D-0061); dates were not named.
- **Today:** a date column gets every comparison and "between" (a builder's choice); the rule file says "not offered".
- **(a) As built.** **(b) A list of values only.**
- Reopens: nothing.

Recommendation (mine): (a). Dates have an order, and "between two dates" is a common filter.

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

#### 23. Which colour means what in a lineage?
- **Situation:** you allowed new colours and wrote "i like green as good" (D-0463); red is for what the app cannot follow (D-0460).
- **(a) Green = "this table does not change"**, red = "the app cannot follow this YET", and every colour with a word or a symbol beside it (the review session's reading of D-0463).
- **(b) Green = "the step is written here"**, red as in (a).
- **(c) You choose from a picture with two or three sets** before anything is built.
- Reopens: nothing.

Recommendation (mine): (c).

#### 24. The recipe upload code that no screen offers
- **Situation:** the app holds code that would copy an uploaded recipe over a recipe of the same name, but no screen offers it. You decided "upload under same name refused" (D-0390) and "Yes off unless deployment place required it." (D-0440).
- **Today:** nothing happens; the code cannot be reached.
- **(a) Remove the code now;** an upload is built when a deployment declares an upload place, with your rules (an existing name refused; "a warning if trying to write on a file name name - the user delete in his file system or choose a new name", D-0437).
- **(b) Rebuild it now,** offered only where a deployment declares an upload place, with the same rules.
- Reopens: nothing.

Recommendation (mine): (a). No deployment declares an upload place today, and code that no screen offers is the kind of old thing a builder takes again (D-0507).

#### 25. The audit log: its file name and form in the bundle
- **(a) A plain text file a person reads.** **(b) A structured file beside the audit recipe that a person can still read.** **(c) Both.**
- Reopens: nothing.

Recommendation (mine): (b). One file, readable by a person and searchable by table (question 10).

---

## 9. What nobody checked

- No browser was used, and no screen of the dialog or of a picker exists: every "what you would see" is described, not shown.
- The runs on "the earliest place" are three runs on the demo recipe, one entity each, through the library and not HOME's screen, with the places listed by hand.
- The recipe redesign was read, not run by me; its own runs are on a part of the demo recipe. The details of what was and was not checked are at the end of `BUILD_ORDER.md` and `RECIPE_REDESIGN_REVIEW.md`.
