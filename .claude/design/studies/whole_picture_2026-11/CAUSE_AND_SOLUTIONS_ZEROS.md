# Why two tables stayed identical, and solutions for entities that must appear with zero hits (2026-11-23)

**What this is.** The cause of the two tables that stayed identical below a step at the ResFinder table (ordered by her, ledger D-0563), and a catalogue of solutions for entities that must still appear with a count of zero without the metadata as the first table of the data join (her direction D-0564). Written by an Opus and a Sonnet design agent who compared their readings and agreed before this text was written (D-0552). It is written by reading and reasoning only. **No run was made for this file**, by her orders: "H1, H2 appear to be a consequence of that - so I think we need to find solution for that and then retest." (D-0565) and "no need to test that now then" (D-0566). The runs it cites were made earlier, under the evidence rules D-0558 to D-0561, and are named where they are used. NOT confirmed by her. Nothing is built; no recipe is edited.

**Where the evidence lives.** The registers `tmpAI/coordinator/design_dialogue/RUN_REGISTER_sonnet_cause.md` (every run of this investigation cancelled before it started), `RUN_REGISTER_sonnet_recipes.md`, `RUN_REGISTER_opus_recipes.md`, `RUN_REGISTER_opus.md`; the earlier runs it cites are in `PATHS_AND_DERIVED_AGREED.md` (G8) and `RECIPES_FROM_THE_MODEL_AGREED.md`. The reads made for this file are in the same scratch folder (not in git): the hand count `cause/hand23.out` (Sonnet), the scan `cause/C6.out` (Sonnet) and the readings RR11 and RR12 of Opus (`RUN_REGISTER_opus_recipes.md`; its stored tables from the earlier run read now, and a scan of the recipes with its own parse).

**The limits.** The demo recipe and, for the numbers, one entity (`10668076`). A hand count from the source files, not an engine run. The feasibility of the solutions is NOT run: it comes after her choice, in the retest described at the end.

Tags: [HER WORDS D-n] / [RECIPE FILE] / [CODE READ file:line] / [HAND COUNT] / [READ SCAN] / [ESTABLISHED: file, point] (a result of earlier runs, rebuilt from scratch, committed) / [STORED TABLES, Opus RR11] (the engine's tables of an earlier run, read now) / [REASONED, not run].

> **Update of 2026-11-23 (ledger D-0568; see `OVERLAP_AND_POPULATION.md`):** a further candidate, (a2), was found after this file was signed: a table of the analysed entities as the first table of the join, the metadata second. It keeps zeros for the analysed entities and follows your direction. The sentences below that say that every form with zeros keeps the metadata as the side whose rows stay, and that only option D follows your direction fully, are corrected where they stand.

---

## HALF PAGE FOR HER

**What happened.** You remove an entity at the ResFinder table. Two tables below it stay exactly as they were: the table `QA_fanout_exhibit` (its second tier) and its plot `qa_fanout_rows_per_sample`. The number for the entity stays 23.

**What the 23 is.** The entity has 23 virulence genes. They come from the VirulenceFinder table, not from ResFinder, so a step at ResFinder does not touch them. The table counts the genes that are present; it does not count an empty row. Before and after the step the entity has 23 rows in the table, with the virulence gene filled in all 23, and the ResFinder gene is there before and empty after. [HAND COUNT: 1 metadata row, 1 ResFinder row, 23 VirulenceFinder gene rows; 1 x 1 x 23 = 23 before and after] [STORED TABLES, Opus RR11] [RECIPE FILE: `QA_fanout_exhibit` tier 2 counts `VF_gene`]
(An earlier sentence in the review said "a count of rows per entity stays 23". That wording was wrong; the committed paths file now carries a correction at each place.)

**The cause, in plain sentences.**
- The place chosen: the entity's rows in this table come by three paths (the metadata, ResFinder, VirulenceFinder). The first place of ResFinder covers one of them.
- The join direction: the metadata is the first table of the join, so the entity stays in the table with empty ResFinder values. This is the same direction that gives the zeros in the plot `qa_amr_genes_per_sample`, which is built to show every entity, some with 0 genes.
- The recipe: not a mistake of the author. The table is written on purpose as a known defect (its own text says "EXHIBIT of a known defect").
- The app: not at fault in the evidence. The stored tables of the earlier run hold exactly the rows this reading predicts: the ResFinder column emptied, the 23 virulence genes intact. Twelve of the 14 tables below changed in that run. [STORED TABLES, Opus RR11; ESTABLISHED: PATHS G8]

**Is the unchanged plot right?** It is right for what it counts: the non-empty virulence genes of each entity after the join. On the demo this equals the rows, because every row has a virulence gene. A user who removed the entity at ResFinder and looks at this plot sees the same bar, and could wrongly conclude that the removal did nothing, or that the entity is still in the ResFinder analysis. After a removal at the VirulenceFinder table the entity would keep 1 row (from the metadata) and show 0. [RECIPE FILE; HAND COUNT; REASONED for the last sentence]

**The core fact.** A zero is an entity that has no data row. An entity removed at the data table also has no data row. The two are the same state of the table. So, within your rules (an audit step is a filter, a column drop or a removal by key, written after your steps), no solution can give "entities with no data row appear with 0" and, at the same time, "a removal at the data table takes the entity out completely". Only the path that carries the population, the metadata, tells them apart. [REASONED; her rules D-0322, D-0541]

> **Correction of 2026-11-23:** Only the path that carries the population tells them apart: the metadata, or a table of the analysed entities (a2). (The sentence above says "the metadata"; the Opus agent's replacement of the neighbouring sentences is below.)

**Your direction, and the fact that meets it.** You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564] The fact: to show an entity that has no data row, the table must keep the metadata's rows. So in every form with zeros the metadata is the side whose rows stay. Only the form without zeros follows your direction fully. The question is at the end of this half page and in the next section.

> **Correction of 2026-11-23:** In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros.

---

## THE QUESTION FOR HER, as it would be put

**Plainly.** You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564]. Here is what is true. For a result that shows one entry per observation (for example every gene found), the data first and the metadata second works today: a step at the data table or at the join place removes the entity completely; a step at the metadata place only empties its metadata columns. [ESTABLISHED: RECIPES G5] For a result that must show every entity with a zero, there is no way to write it in which the data table's own place also takes the entity out. The zero and the removal are the same state of the table. So the question is about the zero.
Your direction and the zeros cannot both hold. To show an entity that has no data row, the table must keep the metadata's rows. So in every form with zeros (A, B, C, E) the metadata is the kept side: first with a left join, or second with a right or full join. Only D follows your direction fully, and D has no zeros. Why: a row for an entity with no data can only come from the metadata. How you would see it: in A, B, C and E the plot keeps 42 bars, with 0 for an entity removed at the data table; in D it has 38 bars and no zeros. (E follows the order in your words, the metadata second, but not the reason you gave in D-0549, that the metadata's extra entities stay out of the table.) [REASONED]

> **Correction of 2026-11-23:** In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros.

**On the demo you would SEE** (the plot `qa_amr_genes_per_sample`: 42 entities in the metadata, 38 with a ResFinder row, so 4 with 0 genes). You remove one entity at the ResFinder table. Today [run] and with (a), (c), (e) [reasoned] the entity stays in the plot with 0 genes, like the 4 others. With (b) it is the same; if you allow the sentence of PATHS Q6, the dialog says before you apply that the step covers 1 of 2 paths and the entity can remain. With the step written at the join place, or with "Remove from all the data", the entity is gone and the plot shows 41 entities. With (f1) (option D) the plot shows 38 entities and no zeros, and a caption says 4 entities have no ResFinder row. [numbers: raw files and the earlier runs; ESTABLISHED: PATHS G8, RECIPES G6]

> **Correction of 2026-11-23:** **With (a2) (option B2)** the plot of the demo shows the same 42 bars, because every metadata id is in `FastP` (42 of 42), the table that stands for the analysed entities in this example. The difference appears only with an entity of the metadata that was never analysed: it is absent with (a2) and shows 0 with A.

**Options** (what each means is in the catalogue below; none is chosen)
- **A.** Keep the zeros; the default place for a removal is the join; the dialog says how many paths a step covers (b). "Remove from all the data" stays a choice (f4). The pattern goes on the good-practice page. Nothing to change in the recipe.
- **B.** Keep the zeros and write the data per entity first (a), so that long tables do not weigh the entity. It needs a second table on the same file. The false zero stays when the data table's place is chosen; the dialog says so.
- **B2.** Keep the zeros with a table of the analysed entities as the FIRST table of the join, the counts next, the metadata second (a2). It follows the order of your direction (the data first) and its reason (the metadata's extra entities stay out). It needs no new key; its parts run today, the whole chain is not run yet. The false zero stays when the counted data table's place is chosen, and "analysed" is relative to one analysis. [added 2026-11-23]
- **C.** The app, not the user, knows that the result is per entity (f5), or also which zeros are filled: the recipe declares the completion of the population (c), or the app completes it at the plot (f3). Needs a new key or an app behaviour.
- **D.** No zeros: data first, metadata second, and a caption states the population (f1). Removal is complete everywhere. The plot `qa_amr_genes_per_sample` changes its meaning.
- **E.** A right or full join, so that the metadata is written second (e). It still keeps the metadata's rows, so you would see the same as A: 42 bars, and 0 for an entity removed at the data table. Your graph model follows such a join like any other (its parents are the same tables). The old reading code does not follow these kinds (D-0452); the new one is not built. Whether the engine builds it as expected is a run after your choice.
- **Neither: say what you meant.**

**My lean, as a lean:** A for the default and the information, B for the demo tables that multiply rows (`QA_fanout_exhibit`, `ST22_Anchor`), D for results that do not need zeros (`QA_population_zscore`). Reason: at the default place it removes the entity completely; it tells the user the one thing that can surprise (the false zero at the data table); and it keeps the zeros the plot is written to show. `QA_fanout_exhibit` is a deliberate exhibit of a defect: changing it changes its purpose. C stays open if you want the app, not the user, to know which zeros are filled; E changes only the order in the file. [REASONED]

> **Correction of 2026-11-23:** Lean of the Sonnet agent with (a2) added: B2 where the recipe has a table that lists the entities this analysis ran on, A otherwise; B for the demo tables that multiply rows; D for results without zeros. Lean of the Opus agent, as a lean: the same as the Sonnet agent. B2 where the recipe has a table that lists the entities this analysis ran on, A otherwise; in both, the default place at the join and the dialog's information on the false zero. Reason: B2 is the only form with zeros that follows both the order and the reason of your direction, and its zeros mean "analysed, zero hits" for that analysis. The false zero at the counted table's own place remains in every form with zeros, so the default at the join and the information stay needed.
**Reopens (information):** D changes the purpose written in the plot itself (a sample without a gene must appear at 0); it reopens no decision of yours. E asks the audit to follow right and full joins (D-0452, D-0460 "B; if needed we try to find a solution later"). C touches the same question as her question 27 (a step reading another table in tier 2).
**Links:** Q6 of `PATHS_AND_DERIVED_AGREED.md` (the sentence "can remain"; its use depends on her answer to that question); (iv) the side of the metadata and (ii) the result with zeros of `RECIPES_FROM_THE_MODEL_AGREED.md`; both are answered, in part, by this choice.

---

## THE CAUSE, AND WHAT WAS FOUND

### The 14 tables below the ResFinder table: not classified, by order

Not done (D-0565: "the solution first"; D-0566: no run on the cause). What exists is kept as it stands: the list of the 14 tables and which two stayed identical [ESTABLISHED: PATHS G8]. The 14 are `T2:ResFinder`, `T1` and `T2` of `ResFinder_with_metadata`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `ST22_Anchor`, and the plots `amr_heatmap`, `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `virulence_bar`, `virulence_variants`. [my own graph of the demo recipe]

### What the "23" is

[HAND COUNT, `cause/hand23.out`; the steps are those of `wrangling/VirulenceFinder_wrangling.yaml` written again by hand with polars on the raw file; compared with the stored tables of the earlier run, [STORED TABLES, Opus RR11]]
- The entity has 1 metadata row, 1 ResFinder row (gene `blaTEM-1C`) and 29 raw lines in the VirulenceFinder file. After the tier-1 steps of VirulenceFinder (one row per virulence gene, strip, unique) it has 23 rows, 23 distinct `VF_gene`, none empty.
- `QA_fanout_exhibit` tier 1: metadata (1 row) left join ResFinder (1 row) left join VirulenceFinder (23 rows) = 23 rows. After a step that removes the entity at ResFinder: metadata (1) left join ResFinder (no row, so one row with empty columns) left join VirulenceFinder (23) = 23 rows. The 23 is VirulenceFinder's gene rows, multiplied by 1 ResFinder row (before) or by one row with empty ResFinder columns (after).
- Tier 2: `rows_per_sample = pl.col('VF_gene').count()`, a count of non-empty virulence genes: 23 before and after. It is not a count of rows with empty data values. [RECIPE FILE `QA_fanout_exhibit_tier2.yaml`]
- The stored tables of the earlier run show the same rows: before, the entity has 23 rows with `VF_gene` non-empty in all 23 and `gene` = `blaTEM-1C` in all 23; after the step at `T1:ResFinder`, 23 rows, `VF_gene` non-empty in all 23, `gene` empty in all 23. [STORED TABLES, Opus RR11]
- Not established without a new run: that a rebuilt engine table today holds exactly these rows. The equality of the number and the stored tables are the evidence.
- `QA_AMR_per_sample` tier 2: `n_amr_genes = pl.col('gene').count()`, 1 before the step and 0 after; the entity's one row stays (it comes from the metadata). [HAND COUNT; RECIPE FILE]

### Is the unchanged plot wrong or right?

[RECIPE FILE: the plot's own text] The plot `qa_fanout_rows_per_sample` is titled "QA EXHIBIT: rows per sample after joining two long tables"; its description says "EXHIBIT of a known defect (issue 68) - rows are inflated on purpose ... a sample with no AMR gene hit counts as one hit, so a sample with more hits weighs more. The defect is shown on purpose." The tier-1 file says "Do not copy this pattern".
- **Right for what it counts.** It counts the non-empty virulence genes of each sample after the join. On the demo this equals the rows, because every row has a virulence gene. The entity's virulence genes did not change, so its count does not change. [HAND COUNT; STORED TABLES]
- **Possibly wrong for a user.** A user who removed the entity at ResFinder and looks at this plot sees the same bar as before, and could wrongly conclude that the removal did not work, or that the entity is still in "the ResFinder analysis". The ResFinder columns of its 23 rows are empty; the plot does not show them. [REASONED]
- The plot is a deliberate exhibit, not a result for a scientist. The same behaviour in a real recipe (a count that comes from another original than the one the user removed) would be the problem. This is for you to decide.

### The scan of the demo and the shipped recipes for the same patterns

[READ SCAN, Sonnet `cause/C6.out` and Opus RR12, two parses that agree: 14 recipes with joins, 31 joined tables; no engine.] Cause class: H1 a count of rows after a join (empty data rows counted), H2 the join direction keeps the entity (by the population), H4 rows that come by another path than the place, other. Effect on an audit: from the established runs where there is one, otherwise "reasoned".

**Joined tables that start from the metadata (first ingredient `metadata_schema`): 7** (6 in the demo recipe; 1 in `demo_abromics`).

| Recipe :: table | Ingredients (first = base) | Aggregate after the join | Cause class | What it does to an audit |
|---|---|---|---|---|
| demo :: `QA_AMR_per_sample` | metadata, ResFinder | tier 2 `gene.count()` (non-empty values) | H2 by design: the plot expects the 4 entities with 0 genes | A step at `T1:ResFinder` leaves the entity with 1 row and count 0 (a false zero); at the join place the entity is gone [ESTABLISHED: PATHS G8; RECIPES G6] |
| demo :: `QA_fanout_exhibit` | metadata, ResFinder, VirulenceFinder | tier 2 `VF_gene.count()` | H4 (rows from another original) and H2; an exhibit | A step at ResFinder: the count does not change (the 23); at VirulenceFinder the count would fall to 0 and the entity would stay by the metadata [HAND COUNT; REASONED] |
| demo :: `ST22_Anchor` | metadata, FastP, ResFinder, MLST, VirulenceFinder, APEC list (inner) | tier 2 `pl.len().over(sample_id)`, a ROW count | H1 in form (a row count where a count of values may be meant; the plot says "counting table rows ... a sample with more AMR hits weighs more") and H4; the inner join with the APEC list drops the rows with no virulence match, including the metadata-only row | A step at ResFinder: the entity's 7 rows stay with the ResFinder columns empty [ESTABLISHED: PATHS G8]. The metadata being first does NOT keep an entity with no matching virulence gene here: the inner join removes it [RECIPE FILE; REASONED] |
| demo :: `QA_population_zscore` | metadata, Quast | tier 2 z-score over all rows (`mean`, `std`) | H2: the entity stays with an empty n50; `mean` and `std` ignore empty values | A step at Quast removes the entity's n50 and changes the z-score of every other entity (the plot's purpose). The entity stays with an empty z-score [REASONED] |
| demo :: `QA_year_types`, `QA_aggregated_no_key` | metadata only (no data join) | `QA_aggregated_no_key`: count of `sample_id` per country and year | none | A step by the entity at the metadata place removes it; `QA_aggregated_no_key` tier 2 has no `sample_id`, so a removal cannot reach it [RECIPE FILE; ESTABLISHED: RECIPES G8] |
| `demo_abromics` :: `demo_join` | metadata, MLST | none | H2 | not run |

**Other aggregates after a join (the table does not start from the metadata):** `Summary_phenotype_length_fragmentation` (sum of `resistance_points` per sample and sequence type, base `Summary`, 623 rows at tier 1 for 42 entities [ESTABLISHED: RECIPES G12]); `2_test_data_ST22_dummy` :: `AMR_Profile_Joint` (a distinct count per sample, inner join with the metadata). [READ SCAN]
**Inner joins (they can remove entities without a step): 5:** the two joins with the APEC list in the demo (`ST22_Anchor`, `AR1_MLST_Serotype_Virulence`; 1114 of 1731 rows leave in `ST22_Anchor` [ESTABLISHED: RECIPES G14, Sonnet's run only]), the same join in `1_Abromics_general_pipeline`, and two joins with the metadata in `2_test_data_ST22_dummy`. [READ SCAN]
**A right side that repeats the entity id before an aggregate:** `ResFinder` and `VirulenceFinder` on the right of a metadata-first join in `QA_fanout_exhibit` and `ST22_Anchor` (rows multiply, 42 to 1731 and 617) [ESTABLISHED: RECIPES G9]; whether the right tables of the other recipes repeat the entity id is not established (it needs their data).
**Counts of the scan:** 31 joined tables; 7 start from the metadata; 5 of them have an aggregate; 7 joined tables in all have an aggregate (3 count values, 1 counts rows (`ST22_Anchor` is the only one), 1 distinct, 1 sum, 1 mean); 5 have an inner join. In the shipped recipes the pattern "metadata first, then an aggregate" is only in the demo recipe. [READ SCAN]

### What the author could write instead, and what can be checked

None of it was run (D-0566), so none is "verified on a scratch copy": the candidates are in the catalogue below.
- **The check could verify (reading the recipe only):** that the first ingredient of a join is the metadata and that a later step counts rows (`pl.len()`) or windows over the entity id: an advice "this counts rows, not values; the table starts from the metadata". [CODE READ: the check already gives advices of this kind, J12, J13, S04] It could name two data tables in one join (the multiplication) as an advice. It cannot know that a table repeats the entity id: that needs the data (the data check). [CODE READ `recipe_check.py` takes the recipe dictionary; `validate_data_analysis_recipe_data` reads the files]
- **Only the good-practice page can say:** that a result per observation is written with the data first and the metadata second, and that a result per entity with zeros keeps the metadata as the side whose rows stay, with the join place as the place of a removal. [HER WORDS D-0547, D-0549]

> **Correction of 2026-11-23:** a result per entity with zeros keeps all the entities that should appear in one table that is not the counted data table: the metadata, or a table of the analysed entities (a2).

### What she may be missing

1. **The zero and the removal are the same state.** Why: a table cannot hold "no data row" and "removed" as two different things unless a column records it, and, within her rules (a filter, a column drop or a removal by key, written after the author's steps), no step can write that mark. How you see it: the same bar of 0. Alternatives: write the step at the join place or use "Remove from all the data" (both remove the entity from the population path); let the dialog say how many paths a step covers; add a column that records "had a data row". [REASONED; D-0322, D-0541]
2. **In this data, "analysed, nothing found" is not in the file.** The ResFinder file lists only the genes found: an entity analysed with no gene and an entity not analysed are both absent. So the zeros of `qa_amr_genes_per_sample` already mean "not in the file", and the plot's subtitle says "4 with 0 genes" by hand. [RECIPE FILE; HAND COUNT: 1 row of the entity in 70 rows of ResFinder] To tell the two apart, a second table that lists the analysed entities is needed, and the recipe has to say so. [REASONED]
3. **"Metadata second" is not the point; "which side is kept" is.** A join with the data first and the metadata second but of kind `right` or `full` keeps the metadata's rows, so the entity stays by the population exactly as with the metadata first. [REASONED from the join semantics]
4. **The inner join with the APEC list loses the population too.** In `ST22_Anchor` the metadata is first, but the inner join with a reference list removes every entity with no matching virulence gene, so there the metadata-first direction gives no zeros and still leaves the entity in rows from VirulenceFinder. [RECIPE FILE; ESTABLISHED: PATHS G8]
5. **A multi-grain table.** `ST22_Anchor` joins tables that have one row per entity (FastP, MLST) with long tables (ResFinder, VirulenceFinder). Its row count weighs an entity by the product of its ResFinder rows and its VirulenceFinder rows (the plot description says so). Counting per entity first is the way to avoid it, candidate (a). [RECIPE FILE; ESTABLISHED: RECIPES G9]
6. **The retest is cheap to prepare and must follow her choice.** It is described at the end.

---

## THE CATALOGUE OF SOLUTIONS

Her rules this stays inside: every join is in tier 1 [CODE READ `recipe_check.py:715`, `action_names.py:66`]; at most one chosen place on a path [HER WORDS D-0553]; the default place is where the original and the metadata are joined [HER WORDS D-0549]; every table below a change is recalculated [HER WORDS D-0560]. The chain: `qa_amr_genes_per_sample` reads `QA_AMR_per_sample` = metadata, left join ResFinder, select; tier 2 groups by the entity and counts the genes; the plot's own text: "A sample without any AMR gene must appear at 0, not disappear. T1 is long (74 rows), T2 has one row per sample (42)" and "Expect 42 samples: 4 with 0 genes, 70 genes in total". [RECIPE FILE]

**The rule behind all candidates.** To show an entity with no data row, the table must take the entity from a table that holds all entities. That table is the retained side of a join. Written first with `left`, or second with `right` or `full`, the audit sees the same thing: a table that reads the metadata as one of its incoming paths. A removal that covers only the data original cannot remove the entity from the population path (k of n paths, k < n). [REASONED; ESTABLISHED: PATHS G8 "~ means below, not gone"]

> **Correction of 2026-11-23:** the table that keeps all the rows is the metadata, or a table of the analysed entities (a2). In (a2) the joined table still reads the metadata as one of its incoming paths, but the metadata is not the side whose rows are all kept: it is joined second with `left` and adds no entity.

For each candidate: what the author writes; what the audit would do (default place; removal at the data table's first place; removal at the join place); what it prevents and what it does not; what the user sees; whether today's check and engine accept it (code read); whether a zero "analysed, nothing found" can be told from "removed by an audit step"; whether it can be judged without a run.

### (a) Count per entity first, then join with the metadata

**Author writes** (a fragment, not run). A second table on the same file (her reimport idea, D-0556) that counts per entity, and a join with the metadata:
```yaml
data_schemas:
  ResFinder_per_entity:             # same file and input_fields as ResFinder
    tier1:
      steps:
        - action: polars_group_by
          by: [sample_id]
          maintain_order: true
          named_aggs: {n_amr_genes: "pl.col('gene').count()"}
joins:
  AMR_per_entity:
    ingredients: [{dataset_id: metadata_schema}, {dataset_id: ResFinder_per_entity}]
    tier1:
      steps:
        - action: polars_join
          right_ingredient: ResFinder_per_entity
          'on': [sample_id]
          how: left
          maintain_order: left_right
        - action: polars_fill_null
          columns: [n_amr_genes]
          value: 0
```
One row per entity on each side: no multiplication. The per-observation table stays as it is (`ResFinder_with_metadata`, data first, metadata second).
**Which side the metadata must be on:** the retained side. With `left` it is the first table; with the data first it would have to be `right` or `full` (candidate (e)). With the data first and `left`, the 4 entities with no ResFinder row are not in the table and there are no zeros. Plainly: yes, it is again "metadata first" for the audit. [ESTABLISHED: RECIPES G5, G6; REASONED]

> **Correction of 2026-11-23:** with (a2) the retained side is the table of the analysed entities, and the metadata is second with `left`: the 4 entities with no ResFinder row stay (they are in the base) and the metadata adds no entity.
**Audit.** Default place (D-0549): the join place `T1:AMR_per_entity`: the entity is gone from the table and the plot. First place of the data table, `T1:ResFinder_per_entity`: the entity has no row on the data side, the left join keeps the metadata row, the zero is filled: the entity stays with 0, a **false zero** [ESTABLISHED: Opus RR4 (2 genes to 0), Sonnet `world2.full` (3 to 0)]. A step at `T1:ResFinder` does not reach this table at all (a second table on the same file is not below the first) [ESTABLISHED: RECIPES G6]. Paths covered at the data first place: 1 of 2.
**Prevents:** row multiplication; the long table's rows no longer weigh the entity (it fixes the `ST22_Anchor` pattern when applied to its long tables). **Does not prevent:** the false zero.
**User sees:** one bar per entity, 42 bars; after a removal at the data table the entity's bar shows 0, like the 4 entities that have no row in the file.
**Today:** accepted by the check and run by the engine (a second table on the same file and a left join with a fill). [ESTABLISHED: RECIPES G18; Opus RR4]
**Zero "nothing found" vs "removed":** not distinguishable in the table. They differ in the audit record. A column "had a data row" written before the fill would tell "no data row" from "0 found", not "removed" from "never there". [REASONED]
**Judged without a run?** Yes for the above (established runs). Run after her choice: see the retest.

### (a2) A table of the analysed entities as the FIRST table of the join, the metadata second (added 2026-11-23, after this file was signed; ledger D-0568, `OVERLAP_AND_POPULATION.md`)

**Author writes** (a fragment, not run). Candidate (a) with the table of (f2) as its base: a data table that has one row per entity the analysis ran on is the first table; the counts come next (left); the metadata is second (left):
```yaml
joins:
  AMR_per_entity:
    ingredients: [{dataset_id: FastP}, {dataset_id: ResFinder_per_entity}, {dataset_id: metadata_schema}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: ResFinder_per_entity, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_join, right_ingredient: metadata_schema, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_fill_null, columns: [n_amr_genes], value: 0}
```
(`FastP` stands for the table of the analysed entities; a manifest of the analysis is the right table, see below.)
**Audit (reasoned).** Default place: the join place: the entity is gone. First place of ResFinder (or of the counts): the entity is still in the first table, so it shows 0, a false zero; 1 of 3 paths covered. First place of the base table: the entity leaves the base and everything below: gone. [REASONED; ESTABLISHED: RECIPES G6]
**Prevents:** the join starts from a data table (the order of D-0564) and the metadata's extra entities stay out (the reason of D-0549); zeros for the entities that were analysed with no hit; the entities of the metadata that were never analysed do not appear. **Does not prevent:** the false zero at the counted data table's own place; and "analysed" is relative to ONE analysis: a read-quality table lists the sequenced entities, but an AMR run can fail for one of them, and its 0 would then mean "not analysed" again. The right first table is a manifest of the analysis, or one of its own result files with one row per analysed entity.
**User sees:** on the demo the same 42 bars as today, because every metadata id is in `FastP`, `Quast` and `Summary` (42 of 42). The difference appears only with an entity of the metadata that was never analysed: it is absent with (a2), and shows 0 with the metadata as the base.
**Today:** its parts are accepted by the check and run by the engine (a data table first, left joins, a fill); the whole chain is not run; the `entity` block is optional and only checked (E02). [CODE READ `recipe_check.py:333-348`]
**Zero distinction:** "analysed, zero hits" against "never analysed": yes, for one analysis. Against "removed at the data table": no.
**Judged without a run?** The parts, yes (established runs); the combination, no: the retest with one never-analysed entity (see `OVERLAP_AND_POPULATION.md`).


### (b) Keep the metadata first, write the step at the join place, show "k of n paths covered", and put the pattern on the good-practice page

**Author writes:** today's recipe, unchanged (`QA_AMR_per_sample`). [RECIPE FILE]
**Audit.** Default place: the join place `T1:QA_AMR_per_sample` (D-0549): the entity leaves the table and the plot. First place of ResFinder: the entity stays with 0, because the metadata path is not covered: **1 of 2 incoming paths covered** [ESTABLISHED: PATHS G8: "1 row"]. The app can say this before Apply if she allows the sentence "can remain" (PATHS Q6). Join place: gone.
**Prevents:** nothing in the table. It makes the false zero visible and puts the default where it does not arise. **Does not prevent:** the false zero when the user chooses the data place.
**User sees:** in the dialog, the place with "covers 1 of 2 paths: the entity can remain in this table with empty values" and the default ticked at the join (words PROVISIONAL, hers); in the plot, a 0.
**Today:** the recipe is accepted; the sentence "can remain" is an open question (PATHS Q6), not built.
**Zero distinction:** the dialog's sentence and the audit record. The table cannot.
**Judged without a run?** Yes (established runs); nothing to change in the recipe or the engine.

### (c) A completion of the population declared in the recipe

**What it would be (does not exist today).** A way to say, in the recipe, "this result is per entity; complete it with the entities of the population, with 0 for the counts". The key `entity.population` (a table that holds the entities) exists, but it is only checked (E02): it completes nothing. [CODE READ `recipe_check.py:341-348`, `recipe_spec.yaml:30`] A possible form (invented, refused today as an unknown key, J01 or T03):
```yaml
joins:
  QA_AMR_per_sample:
    ingredients: [{dataset_id: ResFinder}]     # the data first, no metadata join
    tier1: {steps: []}
    tier2:
      steps:
        - action: polars_group_by
          by: [sample_id]
          named_aggs: {n_amr_genes: "pl.col('gene').count()"}
    complete_population: {fill: {n_amr_genes: 0}}      # NEW: uses entity.population
```
**Audit (reasoned).** The completion reads the population after the aggregation, so there is an edge from the population's tier 1 into this table's tier 2: a new kind of edge (the same question as a look-up join in tier 2, her question 27). The default place: the join place or the population's place. A removal at the first place of the data table: the entity is still in the population, so it is completed with 0: a false zero again, unless the app is made to remove the entity from the population when a removal is written for "a result per entity" (a rule that does not exist). [REASONED]
**Prevents:** the metadata as a visible first table; the author states the intent in one line. **Does not prevent:** the false zero. What it adds: the app would KNOW which rows come from the completion, so the dialog could say so and the table could carry a mark. (c) and (f3) are the candidates in which the app itself can tell a filled zero from a counted zero. [REASONED]
**Today:** not accepted (unknown key); the engine has no such step.
**Judged without a run?** No: whether a tier-2 completion can be built in the engine (tier 2 receives the table, not the population). The run after her choice: requirement, build the completion on a scratch copy and read the entity's rows after a removal at the data place; expected, false zero unless the rule above is added; independence, scratch copy, hand-written steps, engine from scratch.

### (d) A derived table that reads the data table and the metadata separately (her words D-0514 to D-0518; form 3 not confirmed, D-0496)

**Author writes** (invented; form 3 is refused today with T03 for `derived_tables` and J01 for `from:`, [ESTABLISHED: RECIPES G11, G18]):
```yaml
derived_tables:
  AMR_counts:
    from: QA_AMR_per_sample        # ONE table; D-0517 "yes we need the from:"
    tier1: {steps: [polars_group_by by [sample_id, country] ... gene.count()]}
```
**What the form can and cannot do.** A derived table reads ONE table and holds no join step: the join with the metadata is written before it, as a join of source tables. [ESTABLISHED: RECIPE_PROPOSAL_answers, answer 2; her words D-0511 "derived tables should already have the metadata joined"] A derived table moves the aggregation out of the join's tier 2; the table it reads is still the join of the metadata with the data, which must keep the metadata as the retained side to show zeros. Alone, (d) does not remove the pattern. A derived table that reads the data table and the metadata separately would be a join of two tables in a new place: that reopens "a join takes only source tables" [HER WORDS D-0344: "Yes, revisit if needed"] and the rule that every join is in tier 1.
**Audit.** One more node in the graph (the derived table, one parent). Where the metadata is first in the join it reads, the result is that of (b). [REASONED]
**Today:** not accepted. **Judged without a run?** Yes, it does not give zeros alone; it can carry (a) or (b) with a clearer hierarchy. A run after her choice would test the form itself (fact F1 of the recipes file).

### (e) A right or full join kind; an anti-join then a union

**Author writes** (a fragment, not run), the data first and the metadata second with the retained side the metadata:
```yaml
joins:
  AMR_per_entity_right:
    ingredients: [{dataset_id: ResFinder_per_entity}, {dataset_id: metadata_schema}]
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: right
          maintain_order: left_right
        - action: polars_fill_null
          columns: [n_amr_genes]
          value: 0
```
**Followed and allowed today? (code read).** The join action passes `how` to Polars: the form of the action lists `right` and `full` [CODE READ `polars_calls.py:85`], and the engine accepts `anti` and `cross` as well. [CODE READ `libs/utils/src/utils/step_effects.py:71-73`] The old reading code (D-0452; `step_effects.py:68`) follows only `left`, `inner` and `semi`: a description of old code only. Whether the check accepts `how: right` without a message, and whether the engine builds it with `maintain_order: left_right` and which key column it keeps, cannot be judged without a run.
**An anti-join then a union:** an anti join of the metadata against the data gives the entities with no data row (`how: anti`). A union (appending rows) has no registered action: the 68 registered actions have no concat or union. [CODE READ `rules_agent_role_bioscientist.md` section 8; `libs/transformer/src/transformer/actions/`] So the union cannot be written today.
**Audit.** Her graph model (D-0553) follows a right or full join like any join: its parents are its ingredients, whatever `how` says, so the places, "below" and the rule of one place on a path are unchanged. What `how` changes is the kept side, which the display must name from `how` (right: the second table; full: both), not from the first ingredient. A removal at the first place of the data table: the right join keeps the metadata row, the entity stays with an empty value, filled 0: the same false zero as (a). [REASONED from the model; checked by Opus]
**Prevents:** it writes "the metadata second" literally (D-0549, "the metadata should be the right table"). **Does not prevent:** the false zero; and the retained side is still the metadata, so the population effect is the same as metadata first. [REASONED]
**Judged without a run?** No: the engine's build of `how: right` and `how: full`. Run after her choice: requirement, D-0564 with option E; expected, 42 rows, 4 at 0 after the fill, the key column present once, the order kept with `maintain_order: left_right`; independence, a scratch recipe, hand-written steps, the engine in empty folders.

### (f) Others

**(f1) No zeros: say the population in words.** The plot counts only the entities that have a data row and the recipe states the population ("Expect 42 samples: 4 with 0 genes" is already written by hand in the plot's subtitle). [RECIPE FILE] Audit: the data first, the metadata second (left): a removal at the data table or at the join removes the entity completely; no false zero. User sees: 38 bars, a caption "4 of 42 entities have no ResFinder row" written by the author. Prevents the false zero. Does not give the zeros of `qa_amr_genes_per_sample`, which the plot is built to show. Today: accepted. Zero distinction: there is no zero.
**(f2) A table of the analysed entities.** A table (for example one row per analysed entity in a quality table) joined with the metadata gives a column "analysed" next to the count. The zero then reads "analysed, 0 genes" or "not analysed". A removal at the data table leaves "analysed, 0 genes": it still looks like "nothing found". [REASONED] Today: accepted (a join of source tables). It tells "nothing found" from "not analysed"; it does not tell "removed". It needs a table of the analysed entities in the recipe (the demo has tables with one row per entity, [ESTABLISHED: RECIPES G12]).
**(f3) The app completes at the plot, not the recipe.** HOME shows the entities of `entity.population` that have no row of a per-entity result as 0, with a mark. Audit: a removal at the data place leaves the entity in the population: false zero, but the app KNOWS the zero is filled and can mark it. Today: not built; it is an app behaviour, not a recipe form. [REASONED]
**(f4) "Remove from all the data" as the default for a result per entity.** The audit writes the removal at every place that carries the entity when the user removes an entity for a result per entity. The entity is gone from the population path as well; no false zero. [HER WORDS D-0416] This is what the dialog offers, not a recipe form. Today: decided as an option (D-0416). As one step, its 27 places are not valid under D-0553 (35 pairs). Writing them in two steps is option (a) of PATHS Q5, hers to choose. [ESTABLISHED: PATHS G9]
**(f5) The recipe says that a result is per entity** (a new key; today refused as unknown, J01 or S01). The app then knows that a removal for this result must cover the population path: it offers the join place and warns at the data place. It does not prevent the false zero; it lets the app say it. Today: not accepted. [REASONED]

---

## THE DEMO'S TABLES THAT START FROM THE METADATA: the candidate that would apply (for the one big move only; D-0525; no edit)

| Table | Cause class | Candidate that would apply | Why |
|---|---|---|---|
| `QA_AMR_per_sample` | H2, by design (the plot expects 0) | (b), or (a) if the author wants the multiplication gone and the data table's own place separate | The plot needs zeros: the metadata must be the retained side. |
| `QA_fanout_exhibit` | H4 and H2, an exhibit of a known defect | (a) applied to each long table (aggregate each before the join), or leave it as an exhibit with a caption | It is written to show the multiplication. If it stays, nothing changes. |
| `ST22_Anchor` | H1 (row count), H4, inner join with the APEC list | (a) for ResFinder and VirulenceFinder (aggregate before), and a decision on the inner join (see RECIPES (vii)) | A multi-grain table: counting rows weighs an entity by the product of two long tables. |
| `QA_population_zscore` | H2, only an empty value for the entity with no Quast row | data first and the metadata second, `left`, or (b) | No zeros are expected; the z-score of an entity with no n50 is empty. |
| `QA_year_types`, `QA_aggregated_no_key` | none (no data table) | none | They are made from the metadata alone. |

The four tables with a data join that start from the metadata are exactly `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; two more demo tables start from the metadata alone. [READ SCAN, both agents]

---

## THE RETEST AFTER HER CHOICE (described, NOT run)

One entry per candidate: the same step on the adapted chain, in a scratch copy (the demo changes only in the one big move, D-0525). Each run is registered before it runs (D-0561); the three points are written now:

| Candidate | 1. Requirement | 2. Result expected if the candidate works as described | 3. Independence |
|---|---|---|---|
| (a) | A removal at each place of the adapted chain (first place of the data table, join place, metadata, `T1:ResFinder`) | first place of the data table: false zero; join place: gone; metadata: gone; `T1:ResFinder`: no change in the per-entity table | scratch recipe from the demo's ResFinder and metadata schemas, hand-written steps, every table rebuilt in its own empty folder, no lineage code |
| (b) | The same removals on the unchanged chain, and the "k of n" read from my own graph | first place of ResFinder: false zero, 1 of 2; join place: gone, 2 of 2; the 4 entities with no row keep 0 | as (a) |
| (c) | Build the completion on a scratch copy and remove at the data place | false zero, unless the rule that removes from the population is added; whether tier 2 can read the population is the thing asked | as (a); the completion written by hand as a join in tier 1 first, then as the new step |
| (d) | Build a derived table from the join that holds the metadata | as (b) for the same removals; the check refuses the form (T03/J01) | as (a); the engine's reading of the `from:` key is unknown (fact F1 of the recipes file) |
| (e) | Build the chain with `how: right` and with `how: full` and remove at each place | 42 rows with 4 at 0; false zero at the data place; the key column present once | as (a) |
| (f1) | Data first, metadata second, `left`; remove at each place | 38 entities, entity gone at every place, no zeros | as (a) |
| (f2) | A join with a table of analysed entities, plus a column "analysed" | zero with "analysed" after a removal at the data place (still looks like nothing found) | as (a) |
| (f5) | The recipe key that says the result is per entity, on a scratch copy | the app side cannot be run before it exists; the recipe side: accepted or refused by the check | as (a) |

---

## Open between the two agents

None.

**Signed by both agents: Sonnet (this file) and Opus (OPUS_checks_cause_v1.md and OPUS_signs_cause_v2.md; all replacements applied)**; updated 2026-11-23 with candidate (a2), both agents (OPUS_checks_overlap_v1.md and OPUS_signs_overlap_v2.md)
