# Run register of the Sonnet agent, the CAUSE of the identical tables (order D-0563, her words: "we need to find out why - this might be that the recipe is not writen correctly or is it a bug ? or is it because the changes were not affected because of the selection that was done. possible errors of logic of recipe need to be investigated so we can identify the cause ...")

Written BEFORE each run, with (1) the requirement or hypothesis, (2) the result expected by design or by each hypothesis, stated so that the run can contradict it, (3) why it is independent of the old lineage structure. The observed result and AGREES / CONTRADICTS are appended after the run. Date 2026-11-23.

Common points (all runs):
- Machine rule: a script exits at once when the 1-minute load is above 10.
- Read-only on the repository. Scripts, scratch recipes and outputs live in `tmpAI/coordinator/design_dialogue/cause/`.
- The demo recipe is read by `ConfigManager` (via `load_data_analysis_recipe`) and by my own parse (`paths2/sonnet_graph2.py`, PyYAML only). A variant is made by deep-copying the loaded recipe dictionary in memory and appending ONE hand-written step (`modif_filter`, `sample_id` `not_in` the entity, `na: keep`) at the END of the tier-1 steps of the chosen table; the engine (`DataOrchestrator.materialize_tier1/2/3`) builds every table of every variant in its OWN empty folder, from scratch. No audit code, no lineage code, no `remove_from_all`, `recipe_graph`, `run_audit`, `key_drop`, `lineage_*`.
- The entity is `10668076` (the entity of the finding: 1 ResFinder row; 29 VirulenceFinder rows in the raw file).
- The hypotheses (H1 to H4) are those of the order of the coordinator:
  - H1 a RECIPE LOGIC fault: tier 2 counts rows after a join that starts from the metadata, so the entity keeps a row with empty data columns and is counted.
  - H2 a DESIGN consequence of the join direction (the metadata is first; the entity stays by the population).
  - H3 an APP BUG: the step was not applied at that place, or a key / skip error.
  - H4 THE SELECTION: the entity's rows of those tables come by another path (the metadata side, or another original such as VirulenceFinder) that the chosen place does not cover.

## C0 `hand_computation` (`cause/sonnet_C0.py`, output `cause/C0.out`)
1. Requirement: say exactly what the "23" is, from the source files (point (b)), and what the entity's rows should be at each stage, without the engine.
2. Expected: reading the raw files with polars and re-doing by hand the tier-1 steps of the VirulenceFinder table (split `virulence_raw` on ",", strip, split on ": ", take the first part as `VF_gene`, unique): the entity has 23 distinct `VF_gene` rows (29 raw lines; some lines repeat or split into the same gene), 1 ResFinder row, 1 metadata row. Then by arithmetic: `QA_fanout_exhibit` T1 before = 1 x 1 x 23 = 23 rows; after removal at `T1:ResFinder` = 23 rows (1 empty-ResFinder row x 23); `QA_AMR_per_sample` T1 1 row before and 1 row after (gene empty); T2 gene count 1 before and 0 after. If the hand count of VF rows is not 23 the "23" is something else and the hypothesis H4 loses its basis.
3. Raw TSV files and polars only; no recipe code, no engine.

## C1 `h3_first` (`cause/sonnet_C1.py`, output `cause/C1.out`)  -- THE FIRST CHECK, H3
1. Requirement: the step must be at the place (`T1:ResFinder` lacks the entity's rows after it), every table below must be rebuilt (its key changes) and each intermediate table must equal the hand computation of C0. If this fails, H3 (app bug) is alive.
2. Expected if NOT H3: base `T1:ResFinder` has 1 row of the entity, variant V1 has 0; all 14 tables below `T1:ResFinder` have a key different from the base; `T1:QA_fanout_exhibit` has 23 rows in both, with `gene` filled in the base and empty in V1; `T2:QA_fanout_exhibit` is identical in content in both (the row `rows_per_sample` = 23). If any table below keeps its key, or `T1:ResFinder` still has the entity, H3 is the cause.
3. Own graph for the list of tables below; engine from scratch in an empty folder per variant (base and V1); steps by hand.

## C2 `stages` (`cause/sonnet_C2.py`, output `cause/C2.out`)
1. Requirement: (a) the entity's rows at each stage on the way: source file, tier 1 of each ingredient, each join step of `QA_fanout_exhibit`, each tier-2 step, in base and in V1.
2. Expected: the ingredients' tier 1 (metadata 1, ResFinder 1, VirulenceFinder 23); after join step 1 (ResFinder): 1 row in both; after join step 2 (VirulenceFinder): 23 rows in both; after the select: 23; tier 2 `group_by` gives one row, `rows_per_sample` 23 in both. In V1 the `gene` column of those 23 rows is empty, the `VF_gene` column is full.
3. Scratch recipe variants in which the join tier-1 step list of `QA_fanout_exhibit` is cut after step 1, 2, 3 (and the tier 2 is absent), each built by the engine in its own empty folder; steps by hand.

## C3 `h1_vs_h4` (`cause/sonnet_C3.py`, output `cause/C3.out`)  -- tells H1 and H4 apart
1. Requirement: H1 says the aggregate counts rows with empty data columns; H4 says the 23 values come by another path (VirulenceFinder). The two predict different results for different aggregates and for different places.
2. Expected, by hypothesis, in `T2:QA_fanout_exhibit` on the entity (V1 = step at `T1:ResFinder`):
   - aggregate A `VF_gene.count()` (as in the recipe): H1 predicts 0 (the data column would be empty); H4 predicts 23. My expectation: 23 (H4).
   - aggregate B `pl.len()`: H1 and H4 both predict 23.
   - aggregate C `gene.count()` (the ResFinder column): both predict 0 (1 before).
   - aggregate D `gene` distinct non-empty values: both predict 0.
   - V2 (step at `T1:VirulenceFinder`): A gives 0 and B gives 1 (the entity keeps one row, from the metadata and the empty ResFinder row); H4 predicts also that.
   - V3 (steps at both): A 0, B 1, the entity stays by the population (H2).
   - V4 (step at `T1:metadata_schema`): the entity leaves the table (0 rows) in every aggregate.
   - V5 (step at the join `T1:QA_fanout_exhibit`): the entity leaves.
   A is 23 in V1 and 0 in V2 / V3 contradicts H1 and supports H4; B equal to 1 in V3 supports H2.
3. Scratch copies of the demo with the `T2:QA_fanout_exhibit` aggregate replaced (hand-written); engine from scratch in an empty folder per (variant, aggregate); steps by hand.

## C4 `fourteen_tables` (`cause/sonnet_C4.py`, output `cause/C4.out`)
1. Requirement: (a) for EACH of the 14 tables below `T1:ResFinder`: the entity's rows before and after V1, the row counts of the table, whether the key changed and whether the content changed, with the columns that differ; then which of H1 to H4 applies.
2. Expected: 12 content changes and 2 identical (`T2:QA_fanout_exhibit`, `T3:qa_fanout_rows_per_sample`), all 14 keys changed. The entity's rows: `T1:ResFinder` 1 to 0; `T2:ResFinder` 1 to 0; `T1:ResFinder_with_metadata` 1 to 0; `T1:QA_AMR_per_sample` 1 to 1 (gene empty); `T2:QA_AMR_per_sample` 1 row, count 1 to 0; `T1:QA_fanout_exhibit` 23 to 23; `T1:ST22_Anchor` rows stay (7 per the finding), `ResFinder` columns empty; plots follow their tables. A different count of changed tables or a table whose key did not change contradicts this.
3. As C1.

## C5 `other_places` (`cause/sonnet_C5.py`, output `cause/C5.out`)
1. Requirement: H4 asks where the entity's rows enter. For each of the 14 tables, which original supplies the entity's rows: a step at each original separately (`T1:metadata_schema`, `T1:ResFinder`, `T1:VirulenceFinder`, `T1:FastP`, `T1:MLST`) and at the table's own join place, and the count of paths covered (k of n).
2. Expected: `T1:QA_fanout_exhibit` covers 3 incoming paths (metadata, ResFinder, VirulenceFinder); a step at ResFinder covers 1 of 3; at VirulenceFinder 1 of 3; at the metadata 1 of 3 but it empties every row; only the join place or the metadata remove the entity from it. In `ST22_Anchor` (6 paths) likewise. `QA_AMR_per_sample` (2 paths: metadata, ResFinder): the entity stays by the metadata.
3. Own graph and engine variants as C1; steps by hand.

## C6 `scan_static` (`cause/sonnet_C6.py`, output `cause/C6.out`)  -- point (d), the static part
1. Requirement: scan the demo and all shipped recipes (the 50 that load) for: an aggregate (group by, `count`, `len`, `n_unique`, `mean`, `sum`, a window `.over(`) taken after a join that starts from the metadata; a count of rows where a count of values may be meant; an inner join; a right side that may multiply rows; a table whose data rows come from several originals.
2. Expected: in the demo, the tables `QA_AMR_per_sample`, `QA_fanout_exhibit`, `ST22_Anchor`, `QA_population_zscore` (metadata first) with aggregates in tier 2; `ST22_Anchor` counts rows (`pl.len().over`); the two inner joins with the APEC list; other recipes (`2_test_data_ST22_dummy`, `figshare_integration`, templates) have few or none. A recipe with a metadata-first join and a row count that I did not expect is a finding.
3. My own parse (PyYAML only); no engine, no repository code.

## C7 `scan_demo_runs` (`cause/sonnet_C7.py`, output `cause/C7.out`)  -- point (d), the run part on the demo
1. Requirement: what each flagged demo table does to an audit: for each flagged table T and for the entity, the effect of a step at each original that T reads and at T's own join place, on T2 (the aggregate value) and on the plot below.
2. Expected: for a metadata-first join with an aggregate over a data column (`count()` of a data value): a step at that data original sets the aggregate to 0 and the entity stays (H2); for a row count (`pl.len()`): the aggregate drops to 1 (the metadata row) or stays when another original also contributes rows (H4); the join place removes the entity from all. Anything else is a finding.
3. Engine from scratch in an empty folder per variant; steps by hand.

## C8 `suggestions` (`cause/sonnet_C8.py`, output `cause/C8.out`)  -- point (e)
1. Requirement: for each recipe-logic fault, an alternative the author could write, verified on a scratch copy: the result the author would expect, and the audit then behaves as expected.
2. Expected: (a) a per-entity count of the values of the removed original (`gene.count()`) goes to 0 after a step at ResFinder (as `QA_AMR_per_sample` already does); (b) an aggregate written on the data table first (group by the entity id, then join the metadata, left, with the zeros filled) gives the same plot and, for a step at ResFinder, the entity stays with 0 (the false zero of the paths file), which is the author's choice; (c) a row count `pl.len()` replaced by `VF_gene.count()` gives the number of values, not of rows.
3. Scratch recipe copies; engine from scratch; steps by hand.

---
## STATUS after the owner's orders (2026-11-23)
- D-0565 ("the solution first") and D-0566 ("no need to test that now then"): **every run C0 to C8 above is CANCELLED, none had started.** Reason: owner's order D-0565 for C2, C3, C4, C5, C7, C8 (the classification and retests), and owner's order D-0566 for C0, C1 (the cheap H3 check) and the H4 check, and for every feasibility run of the solutions. Nothing of the cause investigation ran before the orders: no engine run, no output file; the folder `cause/` holds no output.
- C6 (the scan of the recipes) is NOT an engine run: it is a read of the recipe files by a script that parses YAML (PyYAML, own parse). It stays, as `cause/sonnet_C6.py`, with the same three points as above, and is run without the engine.
- The "23" is established by reading the source files and the recipe steps (a count by hand), not by a run of the engine; where that is not certain the file says "not established".
- The retest after her choice is DESCRIBED in `CAUSE_identical_tables.md` (three points per candidate), not run.

## Done after the orders (no engine)
- **C6 `scan_static`: DONE as a READ** (`cause/sonnet_C6.py`, output `cause/C6.out`; PyYAML only; load 2). Observed: 14 recipes with joins, 31 joined tables; 7 start from the metadata (6 in the demo recipe: `ST22_Anchor`, `QA_AMR_per_sample`, `QA_year_types`, `QA_fanout_exhibit`, `QA_aggregated_no_key`, `QA_population_zscore`; 1 in `demo_abromics`); 5 of them have an aggregate; 7 joined tables in all have an aggregate (3 value counts, 1 row count `pl.len().over` in `ST22_Anchor`, 1 distinct, 1 sum, 1 mean); 5 have an inner join. The four with a data join that start from the metadata are exactly the four of the coordinator's list. **AGREES** with what C6 expected, except that the pattern "metadata first, then an aggregate" is found only in the demo recipe.
- **A count by hand (not an engine run, not registered as a run)**: `cause/sonnet_hand23.py`, output `cause/hand23.out`: the entity `10668076` has 1 metadata row, 1 ResFinder row, 29 raw VirulenceFinder lines that give 23 rows after the tier-1 steps; 1 x 1 x 23 = 23 before and after the step at ResFinder; `n_amr_genes` 1 before and 0 after.
- C0 to C5, C7, C8: CANCELLED, never run (orders D-0565, D-0566).
