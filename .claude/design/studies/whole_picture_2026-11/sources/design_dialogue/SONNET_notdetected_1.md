# SONNET position 1 (blind): "count the entities of the population that have no detection, as a true result" (order of the owner, block M624; ledger D-0570)

Written without the Opus agent's text. Reading and reasoning only; NO RUN (D-0566). Nothing is edited in the study files; `WHOLE_PICTURE.md` is not touched. Data agnostic: "the entity" is what each row of the metadata is about (on the demo, a sample). Cost and effort are no argument here.

Tags: [HER WORDS] / [RECIPE FILE] / [CODE READ file:line] / [ESTABLISHED: file, point] (an earlier run, committed) / [REASONED, not run]. "NEEDS A RUN" marks what can be judged only after her choice, with its three points at the end.

---

## 0. Her case, in her words

"I think there is a bit of logical problem and that will depend on the join type we use with the metadata AND what a no result means. I do not understand what you mean by "metadata second keeps the zeros" the metadata itself should have id with non empty lines. But if results are 0 as no gene found for example then we should be able to complete the table - this can be done in the recipe but the problem we need the ids that were in metadata and are not in the data table - where we go back to your population example. So we need to have results for the initial population and information about what 0 or missing means." and "true not detect is a true result - So if we need eg. to see how many samples are not detected I need to make a later anti-join (which I would avoid as much as possible) or a join where metadata is on the left side ...and fill the blanks in the recipe ... can we investigate possible solutions for this case ?" [HER WORDS, block M624]

**What is asked, as I read it.** Two outputs, which may be wanted together or apart:
- **The number**: how many entities of the population were not detected (on the demo: 4 of 42 for ResFinder).
- **The list**: which ones.
And, beside them, **the information**: what a 0 or a missing value means for each result table (not detected, not analysed, removed).

**The facts the catalogue rests on**
1. On the demo: the metadata has 42 entities; `ResFinder` has 70 lines for 38 of them; 4 entities have no line. The ResFinder file lists the genes found only. [HAND COUNT; ESTABLISHED: OVERLAP_AND_POPULATION section 1]
2. An entity with no line in a result file is "not detected" only if the pipeline analysed it. The app cannot know that; the pipeline or the user decides. [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS, B3 (iv)]
3. The core fact: a "not detected" entity and an entity removed at the data table are the same state of a table that keeps the entity by the population path. [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS, the core fact]
4. **New for a headline number (reasoned):** for a per-entity zero the false zero is one bar at 0. For "how many entities are not detected" it moves the count: remove one DETECTED entity at the ResFinder table, and 38 detected / 4 not detected becomes 37 / 5, with the new "not detected" entity never having been shown not detected. At the join place (her default, D-0549) it becomes 37 / 4 out of 41. So the number is stable only if the removal is written where the population path is covered, or if the app can name the third class "removed". [REASONED from facts 1 and 3; the 38/4 and 41 figures from the files]
5. The sentence "metadata second keeps the zeros" was wrong as worded (hers: "I do not understand what you mean"): with the data table first and the metadata second with `left`, an entity with no row in the data table is absent. Zeros stay only where the first table already has a row for the entity: a result file that lists every analysed entity (B3), or a table of the analysed entities (B2). See section 4.

---

## 1. The candidates (one list, to be merged with A to E, B2, B3)

Naming: I keep the existing letters and add **N1 to N6** for what this case adds; where a candidate is an existing one it says so.

For every candidate: (a) what the author writes (a fragment, not run); (b) what the user and the audit see (default place at the join; a removal at the data table's own place; a removal at the join place); (c) what it prevents and does not; (d) the recipe check or data check that would help; (e) whether the false "not detected" remains; (f) what it asks of the pipeline or the files; (g) a worked example on the chain of `qa_amr_genes_per_sample` (the metadata, 42 entities; ResFinder, 38 with a line; 4 not detected).

### N1. Her route (ii): the metadata on the left, the blanks filled in the recipe, and the meaning written in a column (existing: A, with the meaning named)

(a) The author writes today's `QA_AMR_per_sample` (the metadata first, `left` join of ResFinder) and one more step that says what a blank means:
```yaml
joins:
  QA_AMR_per_sample:
    ingredients: [{dataset_id: metadata_schema}, {dataset_id: ResFinder}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: ResFinder, 'on': [sample_id], how: left, maintain_order: left_right}
        - action: polars_with_columns
          named_exprs:
            detection: "pl.when(pl.col('gene').is_null()).then(pl.lit('not detected')).otherwise(pl.lit('detected'))"
    tier2:
      steps:
        - {action: polars_group_by, by: [sample_id, country], maintain_order: true, named_aggs: {n_amr_genes: "pl.col('gene').count()", detection: "pl.col('detection').first()"}}
```
A plot of that table with `geom_bar` on `detection` shows two bars, 38 and 4: the number. [RECIPE FILE: today's `QA_AMR_per_sample` and its tier 2 `gene.count()`; the `when/then` form is accepted by the check as a named expression, not run]
**Pitfall:** filling the gene column itself with the words "not detected" (`polars_fill_null` on `gene`, as `demo_abromics` does for "Non Determined", [RECIPE FILE `demo_abromics.yaml:55`]) makes `gene.count()` count the word as a gene (1, not 0). A separate status column is safer. [REASONED]
(b) Default place: the join place: the entity is gone from the table and from the count (41 entities). A removal at the first place of ResFinder: the entity STAYS and is labelled "not detected" by the recipe's own step. A removal at the join place or at the metadata: gone. [ESTABLISHED: PATHS G8, RECIPES G6]
(c) Prevents: a bare 0 with no meaning; the zeros are explained in the table. Does not prevent the false "not detected"; it states it in words.
(d) The recipe check could say, as information, that a result per entity written from a left join with the metadata first has no step that names what a blank means (it reads the steps). The data check says, in both directions (decided: she approves it), "N ids of this file have no row in the metadata" and "N entities of the metadata have no line in this file". [REASONED; CODE READ `data_analysis_recipe_validator.py:485`]
(e) The false "not detected" remains: yes.
(f) Nothing of the pipeline. A statement in the recipe text that ResFinder lists only the genes found.
(g) 42 rows, 38 "detected", 4 "not detected". Remove one detected entity at `T1:ResFinder`: 42 / 37 / 5. At the join place: 41 / 37 / 4.
Run after her choice: no for the parts (established); yes for the whole chain with the status column.

### N2. Her route (i): an anti-join (the list of not detected entities)

(a) Not "later": a joined table of its own, next to the per-entity table, whose tier 1 is the anti-join:
```yaml
joins:
  ResFinder_not_detected:
    ingredients: [{dataset_id: metadata_schema}, {dataset_id: ResFinder}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: ResFinder, 'on': [sample_id], how: anti, maintain_order: left_right}
```
The result: the metadata lines of the entities with no ResFinder line (4 rows). The number is the row count; a plot or a table shows which. [REASONED]
What "later" costs today: an anti-join after the aggregation of the same table (in tier 2) is refused by the check (ST05: a join only in tier 1) and cannot be run (tier 2 receives the table, not the ingredients). The check refuses a join of a join (J04). [CODE READ `recipe_check.py:715, 867`; ESTABLISHED: RECIPES G18] So the anti-join exists today only as its own joined table (above). Her question 27 (a join after tier 1) is not needed for this case. [REASONED]
The kinds accepted: the form of `polars_join` lists `anti` (`how` options inner, left, right, full, semi, anti, cross) [CODE READ `polars_calls.py:85`]; the engine accepts it; the old reading code does not follow it (D-0452) [CODE READ `step_effects.py:68, 73`]; her graph model follows a join by its ingredients whatever `how` says [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS (e), Opus's reading].
(b) Default place: the join place of this table: the removal takes the entity out of the list. At the first place of ResFinder: the removed entity leaves ResFinder, so it APPEARS in the anti-join list (a false non-detection, in the list as well as in the count). At the metadata: gone.
(c) Prevents: zero-filling and row multiplication (one row per metadata line); gives the list. Does not prevent the false non-detection; needs a second table per question; it has no "detected" side, so a share needs the other table; the output of a table as a result is a direction, not confirmed (D-0487, D-0496).
(d) The check could verify that the `how: anti` step has the metadata (the population) as its first ingredient. [REASONED]
(e) The false non-detection remains: yes.
(f) Nothing of the pipeline.
(g) The list has 4 rows. Remove one detected entity at `T1:ResFinder`: 5 rows; at the join place: 4.
NEEDS A RUN: the engine's anti-join on the demo files (the columns it returns, `maintain_order`), the check's verdict, and the audit graph with an anti-join.

### N3. The recipe declares what a missing value means for each result table; the app completes and labels (a form of C)

(a) A new key on the result table (invented; refused today as an unknown key, S01):
```yaml
data_schemas:
  ResFinder:
    absence: {population: metadata_schema, means: not_detected}   # NEW: an entity of the population with no line here is not detected
```
The declaration is the author's promise: the pipeline analysed every entity of the population and the file lists detections only. [REASONED]
(b) The app can then: complete the per-entity result from the population (no join written by the author); write the number and the list; and tell three classes apart: detected, not detected (by the declaration), and **removed by an audit step**, because the audit record names the entities removed at this table. The default place stays the join; at the first place of ResFinder the entity is shown "removed (audit step)", not "not detected". [REASONED]
(c) Prevents: the false non-detection (the third class); the author's join. Does not prevent: a wrong declaration (the app cannot check it); a new key in the format, the check, the engine and the graph.
(d) The check can verify that the population table exists and carries the entity id (as E02 does today for `entity.population`) and that the declared table holds the result's entity id. The data check informs in both directions. [CODE READ `recipe_check.py:341-348`]
(e) The false "not detected" does not remain, if the app reads the audit record; it is the only form where the three classes can be told apart.
(f) The promise stated in the declaration.
(g) 42 entities: 38 detected, 4 not detected. Remove one detected entity at `T1:ResFinder`: 37 detected, 4 not detected, 1 removed (42). At the join place: 41 entities, 37, 4.
NEEDS A RUN and a design decision: whether a completion that reads the audit record is allowed by her rules (an audit step is a filter, a drop or a removal by key; this reads, it adds none) and where the app builds it.

### N4. A table of the analysed entities as the first table (B2 = (a2))

(a) As in the catalogue: the first table lists the entities this analysis ran on; the counts next, `left`; the metadata second. The "not detected" entities are the base entities with no ResFinder line.
(b) Default: the join place. Removal at the first place of ResFinder: the entity stays in the base: false non-detection. At the base's place: gone.
(c) Prevents: "not detected" for entities that were never analysed (they are not in the base); the join starting from the metadata. Does not prevent the false non-detection. The population is the ANALYSED entities, not the initial population: the entities of the initial population that are not in the base are "not analysed", a second number. [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS (a2)]
(d) The data check, other direction: "N entities of the metadata have no line in the base table" is exactly "not analysed". [REASONED]
(e) Remains: yes.
(f) A manifest of the analysis (or a result file with one row per analysed entity).
(g) On the demo the base (`FastP`, 42) equals the metadata: same 42 / 38 / 4, and the removal gives 42 / 37 / 5 at ResFinder, 41 / 37 / 4 at the join place; the difference with N1 appears only with a never-analysed entity.
NEEDS A RUN (one never-analysed entity).

### N5. The result files list every analysed entity (B3)

(a) The pipeline writes, for each analysed entity with no detection, a line with an explicit column "analysed: yes" and an empty gene. The recipe reads the column (a filter or a count on it).
(b) "Not detected" = analysed yes and no gene: a true result stored in the file. A removal at the first place of ResFinder removes ALL the entity's lines, including its "analysed" line: the entity is gone (neither detected nor not detected). Join place: gone.
(c) Prevents the false non-detection. Does not prevent: a wrong file; an empty gene read as a hit by steps that count rows or stamp a value (`total_gene_count`, `status` "Detected") unless the form of the file is agreed with the recipe. [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS, B3 (iii)]
(d) The data check, both directions, informs; the check cannot know whether a missing line means "not analysed".
(e) Remains: no.
(f) The pipeline must write the lines; or a Data Import helper; or the user.
(g) 42 entities in the file: 38 with genes, 4 with an "analysed" line and no gene. Remove one detected entity at `T1:ResFinder`: 41 entities, 37 / 4.
NEEDS A RUN (the empty cell read as missing; the steps on those lines).

### N6. The declared population gives information, not a result (the `entity` block, read by the app)

(a) The recipe already has `entity: {noun, plural, population}` (optional); a recipe declares `population: metadata_schema` and the entity id on both tables. [CODE READ `recipe_check.py:333-348`; today read by the check only]
(b) The app shows, with the table or the plot, one line from the data: "population 42 entities; with a line in ResFinder 38; without a line 4". After a removal at the first place of ResFinder it can say "with a line 37; without 5, of which 1 removed by an audit step". The default place is unchanged.
(c) Prevents: a silent false "not detected" (the third class is shown in words). Does not give: a result in the recipe (the number is not a table of the recipe, so not exported unless the export writes it); does not choose what the missing value means (the author says in the description).
(d) The data check already informs in both directions; this is the same note shown with the result.
(e) The false non-detection: the table can still contain it; the information line names it.
(f) Nothing of the pipeline.
(g) Line shown on the demo: 42 / 38 / 4; after the removal at ResFinder: 42 / 37 / 5 (1 removed by an audit step).
Needs an app feature; NEEDS A RUN once built (the three counts after a removal).

### Also considered

- **Fill with a word in the gene column** (precedent `demo_abromics`, "Non Determined"): see the pitfall in N1.
- **A right or full join, an anti-join then a union:** the metadata second with `right`/`full` keeps the metadata's rows like N1; there is no union action; the anti-join is N2. [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS (e)]
- **A count of entities by flag as a table result** ("detected 38, not detected 4" as a two-row table): the same as N1 with a group by in tier 2; the table as a result is a direction only (D-0487). [REASONED]

---

## 2. The candidates side by side

| | Number | List | Meaning of a missing value written by | False "not detected" at the data table's own place | Asks of the pipeline | New in the app, check or format | Needs a run after her choice |
|---|---|---|---|---|---|---|---|
| N1 left join and a status column (A) | yes (bar of the status) | the per-entity table | the author, in the recipe | remains | nothing | nothing | the whole chain |
| N2 anti-join as its own table | rows | yes | the author | remains | nothing | nothing (check could advise) | engine, check, audit graph |
| N3 declared meaning (C) | yes | yes | the declaration; the app labels | removed class shown | the promise | new key; completion; reads the audit record | yes, and a decision on the reading |
| N4 table of the analysed entities first (B2) | yes (for analysed) | yes | the author | remains | a manifest | nothing | one never-analysed entity |
| N5 files list every analysed entity (B3) | yes | yes | the pipeline, in the file | gone | writes the lines | data check informs | the file's empty cells |
| N6 declared population, information line | yes (info) | no | the author's description | named in words | nothing | an app line from the `entity` block | once built |

---

## 3. What each says about "the initial population"

- N1, N2, N3, N6 take the initial population as the metadata: 42 entities, whatever was analysed.
- N4 and N5 take the analysed entities as the population; the rest is "not analysed", which they report as a second number (through the data check or the line of N6).
- Her contract, one direction (result ids inside the metadata), holds on the demo files. [ESTABLISHED: OVERLAP_AND_POPULATION section 1]

---

## 4. Where a sentence in the study files must be corrected (not edited here)

The sentence "metadata second keeps the zeros" stands, in one form or another, at:
- `CAUSE_AND_SOLUTIONS_ZEROS.md` line 59 (option B3): "Then the data first and the metadata second keeps the zeros". It is the result file's row that keeps the zero, not the metadata second.
- `CAUSE_AND_SOLUTIONS_ZEROS.md` line 220 (the retest of B3) and the B3 entry's (vi): the chain "with the data first and the metadata second" gives zeros only if the file already holds the 4 lines.
- `OVERLAP_AND_POPULATION.md` lines 31, 125, 129 and `CAUSE_AND_SOLUTIONS_ZEROS.md` lines 58, 186 ((a2)): "Zeros appear for the analysed entities with no hit ... the metadata second" is true because the FIRST table lists the analysed entities, not because the metadata is second.
**Proposed replacement sentence (a proposal):** "With the data table first (left), an entity that has no row in the data table is absent. Zeros stay only where the first table already has a row for the entity: a result file that lists every analysed entity (B3), or a table of the analysed entities (B2)."
Places that are correct as they stand: the data first and metadata second for a result per observation (a removal takes the entity out); D (no zeros).

---

## 5. Her two new answers, to record in the overlap file (not edited here)

1. **The data check informs in BOTH directions**: "N ids of this file have no row in the metadata" (the contract) and "N entities of the metadata have no line in this file" (information; the app cannot tell "not analysed" from "analysed, nothing found"). To these I add, from her sentence "the metadata itself should have id with non empty lines", a third note about the metadata itself: "N lines of the metadata have no id" (on the demo recipe `demo_abromics`: 3 lines, deliberate). [HER WORDS; REASONED for the third]
2. **BLUEPRINT's Validate: yes.** The same note appears when the person who builds the recipe presses the check button. [HER WORDS, M624]

---

## 6. What needs a run after her choice (three points each)

1. **N1 whole chain.** Requirement: the status column and the plot of the status on a scratch copy of the chain. Expected: 42 rows, 38 / 4; removal at `T1:ResFinder`: 37 / 5; at the join place: 41 / 37 / 4. Independence: a scratch recipe from the demo's schemas, hand-written steps, every table rebuilt in an empty folder, no lineage code.
2. **N2 anti-join.** Requirement: the anti-join as its own joined table. Expected: 4 rows; the check accepts `how: anti`; the engine builds it; the audit graph shows the parents as the ingredients; removal at `T1:ResFinder`: 5 rows. Independence: as 1.
3. **N3 declared meaning.** Requirement: a completion that reads the declared population and the audit record. Expected: not buildable today (new key, tier 2 receives its table only); the three classes are possible only if the app reads the audit step. Independence: scratch copy; the completion written by hand as a join first.
4. **N4 (B2).** Requirement: one never-analysed entity in the metadata. Expected: absent with the analysed table as the base; shown as "not detected" with the metadata as the base. Independence: as 1.
5. **N5 (B3).** Requirement: a scratch ResFinder file with 4 lines with an explicit "analysed" column and an empty gene. Expected: 4 "not detected", 41 after a removal at `T1:ResFinder`; the steps `total_gene_count` and `status` read the empty line as a hit unless adapted. Independence: as 1.
6. **N6 information line.** Requirement: the three counts after a removal at the first place of ResFinder. Expected: 37 with a line, 5 without, 1 of them removed by an audit step. Independence: as 1; the audit record written by hand.

---

## 7. The question it leaves her, in one place (nothing chosen)

The existing list of `CAUSE_AND_SOLUTIONS_ZEROS.md` (A, B, B2, B3, C, D, E) grows by what this case adds; N1 is A with the meaning named, N4 is B2, N5 is B3, N3 is C with the audit-aware completion, N2 and N6 are new. What she would SEE on the demo for "how many entities are not detected": N1, N4, N5 and N3: a bar of 38 and a bar of 4 (N5 and N3 keep 4 after a removal at ResFinder; N1 and N4 move one entity from "detected" to "not detected"); N2: a list of the 4 entities; N6: a line "population 42, 38 with a line, 4 without". My lean, as a lean, is not stated here: the Opus agent's reading comes first (D-0552).
