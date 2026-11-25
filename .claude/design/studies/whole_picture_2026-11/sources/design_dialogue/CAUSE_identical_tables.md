# Why two tables stayed identical, and a catalogue of solutions for the join that starts from the metadata (v1)

Orders: D-0563 (find the cause), D-0564 ("the join should not start with the medata or we need a solution we do not have yet"), D-0565 ("H1, H2 appear to be a consequence of that - so I think we need to find solution for that and then retest"), D-0566 ("no need to test that now then"). Written by the Sonnet agent. The Opus agent checks it point by point before it goes to her. NOT confirmed by her. Nothing is built; no recipe is edited.

**NO RUN was made for this file** on the cause or on the solutions. The register `RUN_REGISTER_sonnet_cause.md` says which runs were registered and cancelled (none had started). What this file rests on is a hand count of the source files (`cause/sonnet_hand23.py`, output `cause/hand23.out`: polars on the raw TSV files, no recipe code, no engine), a read of the recipe files by a script that parses YAML (`cause/sonnet_C6.py`, output `cause/C6.out`), code and recipe files READ, and results already established and committed.

Tags: [HER WORDS D-n] / [RECIPE FILE] / [CODE READ file:line] / [ESTABLISHED: file, point] (a result of earlier runs, rebuilt from scratch, committed in `PATHS_AND_DERIVED_AGREED.md` or in `RECIPES_AGREED_AND_OPEN_v1.md`, the latter signed by Opus only after its check) / [HAND COUNT] / [READ SCAN] / [REASONED, not run].

---

## HALF PAGE FOR HER

**What happened.** You remove an entity at the ResFinder table. Two tables below it stay exactly as they were: the table `QA_fanout_exhibit` (its second tier) and its plot `qa_fanout_rows_per_sample`. The number for the entity stays 23.

**The cause, in one sentence.** The 23 are 23 virulence-gene rows of the entity, and they come from the VirulenceFinder table, not from ResFinder: a step at ResFinder does not reach them, and the entity is still in the table because the metadata is the first table of the join. [HAND COUNT: the entity has 1 ResFinder row, 23 VirulenceFinder gene rows, 1 metadata row; 1 x 1 x 23 = 23 before and 1 x 1 x 23 = 23 after; the plot counts the non-empty virulence genes] [RECIPE FILE: `QA_fanout_exhibit` tier 2, `pl.col('VF_gene').count()`]

**Which of the four.**
- The recipe: it is not a mistake of the author. The table is written on purpose as a known defect (its own description says "EXHIBIT of a known defect - two long tables joined on one key"). [RECIPE FILE]
- The join direction: yes. The metadata is first, so the entity stays in the table with empty ResFinder values. This is the same direction that gives the zeros in the plot `qa_amr_genes_per_sample`, which is meant to show every entity, some with 0 genes. [RECIPE FILE; HER WORDS D-0564, D-0565]
- The place chosen: yes. The entity's rows in this table come by three paths (the metadata, ResFinder, VirulenceFinder). The first place of ResFinder covers one of them. [READ: the join lists three ingredients]
- The app: not shown to be at fault. Twelve of the 14 tables below the ResFinder table changed in the earlier runs, every one rebuilt from scratch, so the step was applied. [ESTABLISHED: PATHS G8] I did not make a new check (D-0566).

**Why it matters for you.** Where the metadata is the first table, a removal at the data table leaves the entity in the table with an empty value, and a count of values shows 0. A 0 that means "analysed, nothing found" and a 0 that means "you removed it" look the same. [ESTABLISHED: RECIPES_AGREED_AND_OPEN_v1 G6, G7]

**The core fact about the solutions (section g).** A zero is an entity that has no data row. An entity that you removed at the data table also has no data row. The two are the same state of the table. Only the path that carries the population (the metadata) tells them apart. So no solution can give "entities with no data row appear with 0" and, at the same time, "a removal at the data table takes the entity out completely". The choice is between where the removal is written (the join place, or "Remove from all the data") and what the user is told. [REASONED from the established runs]

**Solutions looked at, none chosen:** (a) count per entity first, then join; (b) keep the metadata first and write the step at the join place, saying how many paths it covers; (c) a completion of the population declared in the recipe (does not exist); (d) a derived table (not accepted today, and alone it changes nothing); (e) a right or full join, or an anti-join plus a union (the engine runs the joins; the audit does not follow them yet; there is no union step); (f) others. The question in the form it would be put to you is at the end of section (g).

---

## (a) The 14 tables below the ResFinder table: NOT done, by order

Not done (D-0565: "the solution first"; D-0566: no run on the cause). What exists already and is kept as it stands: the list of the 14 tables and which two stayed identical [ESTABLISHED: PATHS G8]. The 14 are `T2:ResFinder`, `T1` and `T2` of `ResFinder_with_metadata`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `ST22_Anchor`, and the plots `amr_heatmap`, `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `virulence_bar`, `virulence_variants`. [READ: my own graph of the demo recipe: 14 nodes below `T1:ResFinder`]

## (b) What the "23" is (by hand; no run)

[HAND COUNT, `cause/hand23.out`; the steps are those of `wrangling/VirulenceFinder_wrangling.yaml` written again by hand with polars on the raw file]
- The entity `10668076` has 1 row in the metadata, 1 row in ResFinder (gene `blaTEM-1C`) and 29 raw lines in the VirulenceFinder file.
- After the tier-1 steps of VirulenceFinder (split the text at the commas, one row per virulence gene, strip, split at ": ", unique) the entity has 23 rows, 23 distinct `VF_gene`, none empty.
- `QA_fanout_exhibit` tier 1: metadata (1 row) left join ResFinder (1 row) left join VirulenceFinder (23 rows) = 23 rows. After a step that removes the entity at ResFinder: metadata (1) left join ResFinder (no row, so one row with empty columns) left join VirulenceFinder (23) = 23 rows. The 23 is **rows from VirulenceFinder, multiplied by 1 ResFinder row (before) or by one row with empty ResFinder columns (after)**.
- Tier 2: `rows_per_sample = pl.col('VF_gene').count()`, a count of non-empty values of the VirulenceFinder gene. 23 before and after. It is not a count of rows with empty data values: the ResFinder columns are not counted at all. [RECIPE FILE `QA_fanout_exhibit_tier2.yaml`]
- Compared with the finding: "a count of rows per entity stays 23" [ESTABLISHED: PATHS G8]. The hand count gives the same number, 23, and says where it comes from. Not established without a run: that the engine's table holds exactly these 23 rows; the equality of the number is the evidence.
- For the other table the same hand count gives: `QA_AMR_per_sample` tier 2 `n_amr_genes = pl.col('gene').count()`: 1 before the step, 0 after, and the entity's one row stays (it comes from the metadata). [HAND COUNT; RECIPE FILE]

## (c) Is the unchanged plot wrong or right?

[RECIPE FILE: the plot's own text] The plot `qa_fanout_rows_per_sample` is titled "QA EXHIBIT: rows per sample after joining two long tables"; its description says "EXHIBIT of a known defect (issue 68) - rows are inflated on purpose ... a sample with no AMR gene hit counts as one hit, so a sample with more hits weighs more. The defect is shown on purpose."
- **Right for what it counts.** It counts virulence-gene rows after a join with a long ResFinder table. The entity's virulence genes did not change, so its count does not change. The removal at ResFinder removed only the ResFinder row; the count already counted a missing ResFinder row as one. [HAND COUNT]
- **Possibly wrong for a user.** A user who removed the entity at ResFinder and looks at this plot sees the same bar as before. The user could wrongly conclude that the removal did not work, or that the entity is still in "the ResFinder analysis". The ResFinder columns of its 23 rows are empty; the plot does not show them. [REASONED]
- The plot is a deliberate exhibit, not a result for a scientist. The same behaviour in a real recipe (a count that comes from another original than the one the user removed) would be the problem. This is for you to decide; I do not decide.

## (d) Scan of the demo and the shipped recipes for the same patterns

[READ SCAN, `cause/sonnet_C6.py`, output `cause/C6.out`: PyYAML only, no engine, no repository code. 14 recipes with joins, 31 joined tables.] Cause class: H1 a count of rows after a join (empty data rows counted), H2 the join direction keeps the entity (by the population), H4 rows that come by another path than the place, other. Effect on an audit: from the established runs where there is one, otherwise "reasoned" (the demo has the data; the others were not run, by order).

**Joined tables that start from the metadata (first ingredient `metadata_schema`): 7** (6 in the demo recipe; 1 in another recipe).

| Recipe :: table | Ingredients (first = base) | Aggregate after the join | Cause class | What it does to an audit |
|---|---|---|---|---|
| `1_test_data_ST22_dummy` :: `QA_AMR_per_sample` | metadata, ResFinder | tier 2 `gene.count()` (non-empty values) | H2 by design: the plot expects the 4 entities with 0 genes | A step at `T1:ResFinder` leaves the entity with 1 row and count 0 (a false zero); at the join place the entity is gone [ESTABLISHED: PATHS G8; RECIPES G6] |
| same :: `QA_fanout_exhibit` | metadata, ResFinder, VirulenceFinder | tier 2 `VF_gene.count()` | H4 (rows from another original) and H2; an exhibit | A step at ResFinder: nothing changes in the count (the 23); at VirulenceFinder the count would fall to 0 and the entity would stay by the metadata [REASONED: arithmetic of (b)] |
| same :: `ST22_Anchor` | metadata, FastP, ResFinder, MLST, VirulenceFinder, APEC list (inner) | tier 2 `pl.len().over(sample_id)`, a ROW count | H1 in form (a row count where a count of values may be meant; the plot says "counting table rows ... a sample with more AMR hits weighs more") and H4 (rows from VirulenceFinder); the inner join with the APEC list drops the rows with no virulence match, including the metadata-only row | A step at ResFinder: the entity's 7 rows stay with the ResFinder columns empty [ESTABLISHED: PATHS G8]. The metadata being first does NOT keep an entity with no matching virulence gene here: the inner join removes it [RECIPE FILE; REASONED] |
| same :: `QA_population_zscore` | metadata, Quast | tier 2 z-score over all rows (`mean`, `std`) | H2: the entity stays with an empty n50; `mean` and `std` ignore empty values | A step at Quast removes the entity's n50 and changes the z-score of every other entity (the plot's purpose, its description says so). The entity stays with an empty z-score [REASONED] |
| same :: `QA_year_types`, `QA_aggregated_no_key` | metadata only (no data join) | `QA_aggregated_no_key`: count of `sample_id` per country and year | none (no data table) | A step by the entity at the metadata place removes it; `QA_aggregated_no_key` tier 2 has no `sample_id`, so a removal cannot reach it [RECIPE FILE; ESTABLISHED: RECIPES G8] |
| `demo_abromics` :: `demo_join` | metadata, MLST | none | H2 (the entity stays with empty MLST values) | not run |

**Other aggregates after a join (the table does not start from the metadata):** `Summary_phenotype_length_fragmentation` (sum of `resistance_points` per sample and sequence type, base `Summary`, 623 rows at tier 1 for 42 entities, [ESTABLISHED: RECIPES G12]); `2_test_data_ST22_dummy` :: `AMR_Profile_Joint` (a distinct count per sample, inner join with the metadata). [READ SCAN]
**Inner joins (they can remove entities without a step): 5:** the two joins with the APEC list in the demo (`ST22_Anchor`, `AR1_MLST_Serotype_Virulence`; 1114 of 1731 rows leave in `ST22_Anchor`, [ESTABLISHED: RECIPES G14]), the same join in `1_Abromics_general_pipeline`, and two joins with the metadata in `2_test_data_ST22_dummy`. [READ SCAN]
**A right side that repeats the entity id before an aggregate:** the data tables `ResFinder` and `VirulenceFinder` on the right of a metadata-first join in `QA_fanout_exhibit` and `ST22_Anchor` (rows multiply, 42 to 1731 and 617) [ESTABLISHED: RECIPES G9]; whether the right tables of the other recipes repeat the entity id is not established (it needs their data).
**Counts of the scan:** 31 joined tables; 7 start from the metadata; 5 of them have an aggregate; 7 joined tables in all have an aggregate (3 count values, 1 counts rows, 1 distinct, 1 sum, 1 mean); 5 have an inner join. In the shipped recipes the pattern "metadata first, then an aggregate" is only in the demo recipe. [READ SCAN]

## (e) What the author could write instead, and what can be checked

The suggestions are the candidates of section (g); none was run (D-0566), so none is "verified on a scratch copy". What the recipe check could verify and what only a good-practice page can say:
- **The check could verify (reading the recipe only):** that the first ingredient of a join is the metadata and that a tier 2 or a later tier 1 step counts rows (`pl.len()`) or windows over the entity id: an advice "this counts rows, not values; the table starts from the metadata". [CODE READ: the check already gives advices of this kind, J12, J13, S04] It could name two data tables in one join (the multiplication) as an advice. It cannot know that a table repeats the entity id: that needs the data (the data check). [CODE READ `recipe_check.py` takes the recipe dictionary; `validate_data_analysis_recipe_data` reads the files]
- **Only the good-practice page can say:** that a result per observation is written with the data first and the metadata second, and that a result per entity with zeros keeps the metadata as the retained side, with the join place as the place of a removal. [HER WORDS D-0547, D-0549]

## (f) What she may be missing

1. **The zero and the removal are the same state.** Said in the half page. Why: a table cannot hold "no data row" and "removed" as two different things unless a column records it. How you see it: the same bar of 0. Alternatives: write the step at the join place or use "Remove from all the data" (both remove the entity from the population path); let the dialog say how many paths a step covers; add a column that records "had a data row".
2. **In this data, "analysed, nothing found" is not in the file.** The ResFinder file lists only the genes found: an entity analysed with no gene and an entity not analysed are both absent. So the zeros of `qa_amr_genes_per_sample` already mean "not in the file", and the plot's subtitle says "4 with 0 genes" by hand. [RECIPE FILE: `qa_amr_genes_per_sample.yaml` subtitle; HAND COUNT: 1 row of the entity in 70 rows of ResFinder] To tell the two apart, a second table that lists the analysed entities is needed (for example a quality table with one row per analysed entity), and the recipe has to say so. [REASONED]
3. **"Metadata second" is not the point; "which side is kept" is.** A join with the data first and the metadata second but of kind `right` or `full` keeps the metadata's rows, so the entity stays by the population exactly as with the metadata first. What matters for the audit is which table supplies the population, not the order in the file. [REASONED from the join semantics; Polars `how`]
4. **The inner join with the APEC list loses the population too.** In `ST22_Anchor` the metadata is first, but the inner join with a reference list removes every entity with no matching virulence gene, so there the metadata-first direction gives no zeros and still leaves the entity in rows from VirulenceFinder. [RECIPE FILE; ESTABLISHED: PATHS G8]
5. **A multi-grain table.** `ST22_Anchor` joins tables that have one row per entity (FastP, MLST) with long tables (ResFinder, VirulenceFinder). Its row count weighs an entity by the product of its ResFinder rows and its VirulenceFinder rows (the plot description says so). Counting per entity first is the way to avoid it, and it is candidate (a). [RECIPE FILE; ESTABLISHED: RECIPES G9]
6. **The retest is cheap to prepare and must follow her choice.** Each candidate needs its own scratch chain; section (g) describes it.

---

## (g) A CATALOGUE OF SOLUTIONS for "entities with no data row must still appear, with a count of zero" without the metadata as the first table of the data join

Her rules this stays inside: every join is in tier 1 [CODE READ `recipe_check.py:715`, `action_names.py:66`]; at most one chosen place on a path [HER WORDS D-0553]; the default place is where the original and the metadata are joined [HER WORDS D-0549]; every table below a change is recalculated [HER WORDS D-0560]. The chain in question: `qa_amr_genes_per_sample` reads `QA_AMR_per_sample` = metadata, left join ResFinder, select; tier 2 groups by the entity and counts the genes; the plot's own text: "A sample without any AMR gene must appear at 0, not disappear. T1 is long (74 rows), T2 has one row per sample (42)" and "Expect 42 samples: 4 with 0 genes, 70 genes in total". [RECIPE FILE]

**The rule behind all candidates.** To show an entity with no data row, the table must take the entity from a table that holds all entities. That table is the retained side of a join. Written first with `left`, or second with `right` or `full`, the audit sees the same thing: a table that reads the metadata as one of its incoming paths. [REASONED] A removal that covers only the data original cannot remove the entity from the population path (k of n paths, k < n). [ESTABLISHED: PATHS G8 "~ means below, not gone"]

For each candidate: what the author writes; what the audit does (default place; removal at the data table's first place; removal at the join place); what it prevents and what it does not; what the user sees; whether today's check and engine accept it; whether a zero "analysed, nothing found" can be told from "removed by an audit step". Feasibility is judged without a run; where it cannot be, the entry says so.

### (a) Count per entity first, then join with the metadata

**Author writes** (a fragment; not run). A second table on the same file (her reimport idea, D-0556) that counts per entity, and a join with the metadata:
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
One row per entity on each side: no multiplication. The per-observation table stays as it is (`ResFinder_with_metadata`, data first, metadata second) for results per observation.
**Which side the metadata must be on:** the retained side. With `left` it is the first table; with the data first it would have to be `right` or `full` (candidate (e)). With the data first and `left`, the 4 entities with no ResFinder row are not in the table and there are no zeros. Plainly: yes, it is again "metadata first" for the audit. [ESTABLISHED: RECIPES G5, G6; REASONED]
**Audit.** Default place (D-0549): the join place `T1:AMR_per_entity`: the entity is gone from the table and the plot. [ESTABLISHED: RECIPES G6, Opus RR4] First place of the data table, `T1:ResFinder_per_entity`: the entity has no row on the data side, the left join keeps the metadata row, the zero is filled: the entity stays with 0, a **false zero** [ESTABLISHED: Opus RR4 (2 genes to 0), my `world2.full` (3 to 0)]. A step at `T1:ResFinder` does not reach this table at all (a second table on the same file is not below the first) [ESTABLISHED: RECIPES G6]. Paths covered at the data first place: 1 of 2.
**Prevents:** row multiplication; the long table's rows no longer weigh the entity (it fixes the `ST22_Anchor` pattern when applied to its long tables). **Does not prevent:** the false zero. [ESTABLISHED]
**User sees:** one bar per entity, 42 bars; after a removal at the data table the entity's bar shows 0, like the 4 entities that have no row in the file.
**Today:** accepted by the check and run by the engine (a second table on the same file and a left join with a fill). [ESTABLISHED: RECIPES G18; Opus RR4]
**Zero "nothing found" vs "removed":** not distinguishable in the table. They differ in the audit record (the step names the entity). A column `n_rows_seen` or "had a data row" written before the fill would tell "no data row" from "0 found", not "removed" from "never there". [REASONED]
**Feasible:** yes today; the false zero stays. **Retest after her choice (not run):** (1) requirement: a removal at each place of this chain (first place of the data table, the join place, the metadata) on the scratch copy; (2) expected, stated now: first place of the data table: entity stays with 0 (false zero); join place: gone; metadata: gone; a step at `T1:ResFinder`: no change in this table (the other table); (3) independence: scratch recipe built from the demo's ResFinder and metadata schemas in empty folders, steps written by hand, no lineage code, every table rebuilt from scratch.

### (b) Keep the metadata first, write the step at the join place, show "k of n paths covered", and put the pattern on the good-practice page

**Author writes:** today's recipe, unchanged (`QA_AMR_per_sample` as it is). [RECIPE FILE]
**Audit.** Default place: the join place `T1:QA_AMR_per_sample` (D-0549): the entity leaves the table and the plot. First place of ResFinder: the entity stays with 0, because the metadata path is not covered: **1 of 2 incoming paths covered** [ESTABLISHED: PATHS G8: "1 row"]. The app can say this before Apply (this is Q6 of the paths file: "can remain"; hers to decide). Join place: gone.
**Prevents:** nothing in the table. It makes the false zero visible and puts the default where it does not arise. **Does not prevent:** the false zero when the user chooses the data place.
**User sees:** in the dialog, the place with "covers 1 of 2 paths: the entity can remain in this table with empty values" and the default ticked at the join (words PROVISIONAL, hers); in the plot, a 0.
**Today:** the recipe is accepted; the sentence "can remain" is DECIDED as a question only (PATHS Q6), not built. [ESTABLISHED: PATHS Q6]
**Zero distinction:** the dialog's sentence and the audit record. The table cannot.
**Feasible:** yes; nothing to change in the recipe or the engine. **Retest (not run):** (1) the same as (a) on the demo's own chain copied to a scratch recipe; (2) expected: first place of ResFinder: stays with 0; join place: gone; "k of n" read off the graph is 1 of 2 and 2 of 2; (3) independent as in (a).

### (c) A completion of the population declared in the recipe

**What it would be (does not exist today).** A way to say, in the recipe, "this result is per entity; complete it with the entities of the population, with 0 for the counts". The key `entity.population` (a table that holds the entities) exists, but it is only checked (E02): it completes nothing. [CODE READ `recipe_check.py:341-348`, `recipe_spec.yaml:30`] A possible form (invented, to be refused today as an unknown key, J01/T03):
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
**Prevents:** the metadata as a visible first table; the author states the intent in one line. **Does not prevent:** the false zero. What it adds: the app would KNOW which rows come from the completion, so the dialog could say so and the table could carry a mark. That is the only candidate in which the "filled" zero can be told from a counted zero by the app itself. [REASONED]
**Today:** not accepted (unknown key), the engine has no such step. **Cannot be judged without a run:** whether a tier-2 completion can be built in the engine (tier 2 receives the table, not the population). Run to ask after her choice: its three points: (1) requirement: build the completion on a scratch copy and read the entity's rows after a removal at the data place; (2) expected: false zero, unless the rule above is added; (3) independence: scratch copy, hand-written steps, engine from scratch.
**Feasible:** not today; it is a new key and a new step in the check, the engine and the graph.

### (d) A derived table that reads the data table and the metadata separately (her words D-0514 to D-0518; form 3 not confirmed, D-0496)

**Author writes** (invented; form 3 is refused today with T03 for `derived_tables` and J01 for `from:`, [ESTABLISHED: RECIPES G11, G18]):
```yaml
derived_tables:
  AMR_counts:
    from: QA_AMR_per_sample        # ONE table; D-0517 "yes we need the from:"
    tier1: {steps: [polars_group_by by [sample_id, country] ... gene.count()]}
```
**What the form can and cannot do.** A derived table reads ONE table and holds no join step: the join with the metadata is written before it, as a join of source tables. [ESTABLISHED: RECIPE_PROPOSAL_answers, answer 2; her words D-0511 "derived tables should already have the metadata joined"] So a derived table moves the aggregation out of the join's tier 2; the table it reads is still the join of the metadata with the data, which must keep the metadata as the retained side to show zeros. Alone, (d) does not remove the pattern. A derived table that reads the data table and the metadata separately would be a join of two tables in a new place: that reopens "a join takes only source tables" [HER WORDS D-0344: "Yes, revisit if needed"] and the rule that every join is in tier 1.
**Audit.** One more node in the graph (the derived table, one parent). Where the metadata is first in the join it reads, the result is that of (b). [REASONED]
**Today:** not accepted. **Feasible:** not as a solution of zeros; it can carry (a) or (b) with a clearer hierarchy. No run needed to say so; a run to ask after her choice would test the form itself (the three points belong to the form's retest, not to this question).

### (e) A right or full join kind; an anti-join then a union

**Author writes** (a fragment; not run), the data first and the metadata second with the retained side the metadata:
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
**Followed and allowed today? (code read).** The join action passes `how` to Polars: the engine accepts `left`, `inner`, `semi`, and `anti`, `right`, `full`, `cross` as well. [CODE READ `libs/utils/src/utils/step_effects.py:71-73`: "every kind the engine's join action accepts that is not in FOLLOWED_JOINS"] The audit's reading of steps follows only `left`, `inner` and `semi` (`FOLLOWED_JOINS`, line 68); the others are "not followed YET" (D-0452): the walk gives such a line the reason `join_not_yet_followed` and the line cannot be ticked. [CODE READ `step_effects.py:30-34, 68, 73`] Her words: "B; if needed we try to find a solution later" (D-0460). Whether the check accepts `how: right` without a message: the parameter check reads the form of `polars_join`; I have not run it and cannot judge it without a run. Whether the engine builds it with `maintain_order: left_right` and which key column it keeps: cannot be judged without a run.
**An anti-join then a union:** an anti join of the metadata against the data gives the entities with no data row (`how: anti`: engine accepts, audit does not follow). A union (appending rows) has no registered action: the 68 registered actions have no concat or union. [CODE READ `rules_agent_role_bioscientist.md` §8; `libs/transformer/src/transformer/actions/` has none] So the union cannot be written today.
**Audit (reasoned).** The default place is the join place. A removal at the first place of the data table: the right join keeps the metadata row, the entity stays with an empty value, filled 0: the same false zero as (a). The graph (D-0553) does not need the kind of join: the parents of the join are the same two tables. What the old walk cannot follow is the columns' origin, not the place. [REASONED; the second sentence is a reading of my graph rules and of `step_effects.py`, to be checked by Opus]
**Prevents:** it writes "the metadata second" literally, as the best practice of D-0549 says ("the metadata should be the right table"). **Does not prevent:** the false zero; and "right table" and "the retained side" are then the same table, so the population effect is the same as metadata first. [REASONED]
**Feasible:** partly: the engine runs it, the check probably accepts it, the audit's walk does not follow it. **Retest after her choice (not run):** (1) requirement: build the chain with `how: right` and with `how: full`; (2) expected: 42 rows with 4 entities at 0 (as the plot's subtitle expects); a removal at the data place: false zero; join place: gone; the walk gives `join_not_yet_followed` for the line; (3) independence: scratch recipe, hand-written steps, engine from scratch in empty folders, the walk not used.

### (f) Others

**(f1) No zeros: say the population in words.** The plot counts only the entities that have a data row and the recipe states the population ("Expect 42 samples: 4 with 0 genes" is already written by hand in the plot's subtitle). [RECIPE FILE] Audit: the data first, the metadata second (left): a removal at the data table or at the join removes the entity completely; no false zero. User sees: 38 bars, a caption "4 of 42 entities have no ResFinder row" written by the author. Prevents: the false zero. Does not give: the zeros of `qa_amr_genes_per_sample`, which the plot is built to show. Today: accepted. Zero distinction: there is no zero.
**(f2) A table of the analysed entities.** A table (for example one row per analysed entity in a quality table) joined with the metadata gives a column "analysed" next to the count. The zero then reads "analysed, 0 genes" or "not analysed". A removal at the data table leaves "analysed, 0 genes": it still looks like "nothing found". [REASONED] Today: accepted (a join of source tables). It tells "nothing found" from "not analysed"; it does not tell "removed". It needs a table of the analysed entities in the recipe (the demo has FastP or Summary_quality with one row per entity: [ESTABLISHED: RECIPES, the demo's one-row-per-entity tables]).
**(f3) The app completes at the plot, not the recipe.** HOME shows the entities of `entity.population` that have no row of a per-entity result as 0, with a mark. Audit: a removal at the data place leaves the entity in the population: false zero, but the app KNOWS the zero is filled and can mark it. Today: not built; it is an app behaviour, not a recipe form. [REASONED]
**(f4) "Remove from all the data" as the default for a result per entity.** The audit writes the removal at every place that carries the entity (27 places on the demo, D-0416; in two steps) when the user removes an entity for a result per entity. The entity is gone from the population path as well; no false zero. [HER WORDS D-0416; ESTABLISHED: PATHS G9, the 27 places in two steps] This is not a form of the recipe: it is what the dialog offers. Today: decided as an option, 27 places not valid in one step, written in two. [ESTABLISHED: PATHS G9]

### Which candidate would apply to each demo table that starts from the metadata (candidates for the one big move only; D-0525; no edit)

| Table | Cause class | Candidate that would apply | Why |
|---|---|---|---|
| `QA_AMR_per_sample` | H2, by design (the plot expects 0) | (b), or (a) if the author wants the multiplication gone and the data table's own place separate | The plot needs zeros: the metadata must be the retained side. |
| `QA_fanout_exhibit` | H4 and H2, an exhibit of a known defect | (a) applied to each long table (aggregate each before the join), or leave it as an exhibit with a caption | It is written to show the multiplication. If it stays, nothing changes. |
| `ST22_Anchor` | H1 (row count), H4, inner join with the APEC list | (a) for ResFinder and VirulenceFinder (aggregate before), and a decision on the inner join (see RECIPES (vii)) | A multi-grain table: counting rows weighs an entity by the product of two long tables. |
| `QA_population_zscore` | H2, only an empty value for the entity with no Quast row | data first and the metadata second, `left` (pattern 1), or (b) | No zeros are expected; the z-score of an entity with no n50 is empty. |
| `QA_year_types`, `QA_aggregated_no_key` | none (no data table) | none | They are made from the metadata alone. |

(Verified by the scan: the four tables with a data join that start from the metadata are exactly `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; two more demo tables start from the metadata alone. [READ SCAN])

### The question for her, as it would be put

**Plainly.** You said: the join should not start with the metadata, or we need a solution we do not have yet [D-0564]. Here is what is true. For a result that shows one entry per observation (for example every gene found), the data first and the metadata second works today and removes the entity completely wherever you write the step. For a result that must show every entity with a zero, there is no way to write it in which the data table's own place also takes the entity out: the zero and the removal are the same state of the table. So the question is about the zero.
**On the demo you would SEE** (the plot `qa_amr_genes_per_sample`, 42 entities, 4 with 0 genes): you remove one entity at the ResFinder table. Today (and with (a), (c), (e)) the entity stays in the plot with 0 genes, like the 4 others. With (b) it is the same, but the dialog says before you apply that the step covers 1 of 2 paths and the entity can remain. With the step written at the join place, or with "Remove from all the data", the entity is gone from the plot and the plot shows 41 entities. With (f1) the plot shows 38 entities and no zeros, and a caption says 4 entities have no ResFinder row.
**Options**
- **A.** Keep the zeros; the default place is the join; the dialog says how many paths a step covers (b). The pattern goes on the good-practice page. Nothing to change in the recipe.
- **B.** Keep the zeros and write the data per entity first (a), so that long tables do not weigh the entity. It needs a second table on the same file. The false zero stays when the data table's place is chosen; the dialog says so.
- **C.** A new way to declare the completion of the population in the recipe (c), or the app completes it (f3), so that the app knows which zeros are filled. Needs building: a new key or an app behaviour.
- **D.** No zeros: data first, metadata second, and a caption states the population (f1). Removal is complete everywhere. The plot `qa_amr_genes_per_sample` would change its meaning.
- **E.** A right or full join so that the metadata is written second (e). The engine runs it; the audit does not follow these joins yet.
- **Neither: say what you meant.**
**My lean, as a lean:** A for the default and the information, with B for the demo tables that multiply rows (`QA_fanout_exhibit`, `ST22_Anchor`) and D for results that do not need zeros (`QA_population_zscore`). Reason: it needs nothing new in the check or the engine, it removes the entity completely at the default place, and it tells the user the one thing that can surprise. C and E are open if you want the app, not the user, to know which zeros are filled. [REASONED]
**Reopens (information):** D reopens the plot's own purpose (a sample without a gene must appear at 0). E asks the audit to follow `right` and `full` joins (D-0452, D-0460 "B; if needed we try to find a solution later"). C touches the same question as her question 27 (a step reading another table in tier 2).
**Links:** Q6 of `PATHS_AND_DERIVED_AGREED.md` (the sentence "can remain"), (iv) the side of the metadata and (ii) the result with zeros of `RECIPES_AGREED_AND_OPEN_v1.md`; both are answered, in part, by this choice.

---

## The retest after her choice (described, NOT run)

One entry per candidate; the same step on the adapted chain, in a scratch copy (the demo changes only in the one big move, D-0525). Each run is registered before it runs (D-0561), and the three points are written now:

| Candidate | 1. Requirement | 2. Result expected if the candidate works as described | 3. Independence |
|---|---|---|---|
| (a) | A removal at each place of the adapted chain (first place of the data table, join place, metadata, `T1:ResFinder`) | first place of the data table: false zero; join place: gone; metadata: gone; `T1:ResFinder`: no change in the per-entity table | scratch recipe from the demo's ResFinder and metadata schemas, hand-written steps, every table rebuilt in its own empty folder, no lineage code |
| (b) | The same removals on the unchanged chain, and the "k of n" read from my own graph | first place of ResFinder: false zero, 1 of 2; join place: gone, 2 of 2; the 4 entities with no row keep 0 | as (a) |
| (c) | Build the completion on a scratch copy and remove at the data place | false zero, unless the rule that removes from the population is added; whether tier 2 can read the population is the thing asked | as (a); the completion written by hand as a join in tier 1 first, then as the new step |
| (d) | Build a derived table from the join that holds the metadata | as (b) for the same removals; the check refuses the form (T03/J01) | as (a); the engine's reading of the `from:` key is unknown (fact F1 of the recipes file) |
| (e) | Build the chain with `how: right` and `how: full` and remove at each place | 42 rows with 4 at 0; false zero at the data place; the walk marks the line "not followed" | as (a); the walk used only to read its message |
| (f1) | Data first, metadata second, `left`; remove at each place | 38 entities, entity gone at every place, no zeros | as (a) |
| (f2) | A join with a table of analysed entities, plus a column "analysed" | zero with "analysed" after a removal at the data place (still looks like nothing found) | as (a) |
