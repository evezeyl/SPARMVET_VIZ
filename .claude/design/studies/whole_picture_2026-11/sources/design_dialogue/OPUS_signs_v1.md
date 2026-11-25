# Opus signs v1: my answer to AGREED_AND_OPEN_v1 (G1 to G26, X1 to X4, D1 to D4, Q1 to Q8)

Read on `dev` `febc506f`. A signature means: I would put the sentence in the design as it stands, and I have checked its evidence (by reading code at file:line, by the ledger's evidence field, or by a run named below). Her words are copied only from the evidence fields. The runs of section 5 used the app's own audit copy and audit run (`opus_runs.py`, output in `opus_runs.out` and `opus_runs_out/results.json`, this folder).

## 1. G1 to G26

- **G1. SIGN WITH THIS WORDING.** "A place is `T1:<table>`, `T2:<table>` or `T3:<plot>`. Its audit steps go in `audit_steps` after the author's steps of that tier, and the author's steps never change (D-0541). An empty tier 2 is the same place as tier 1 (D-0346; `lineage_walk.py:394-395`), except in the latent case of X2. A plot's own tier 3 is always a place. A source file holds no steps (D-0332)."
  - Why: the fold applies to tier 2 only. A plot's tier 3 is offered even when it is empty (the walk's P8, "a tier 3 is always a line"), and that place is what keeps X2 from being a hole for a single plot.
- **G2. SIGN.**
- **G3. SIGN.** I verified the construction by reading: a join's parents are the T1 of its ingredients (`recipe_graph.py:579-580`); J04 refuses an ingredient that is not a schema, or one listed twice (`recipe_check.py:867, 869`). Your run (50 of 50 shipped recipes give a tree) adds the evidence.
- **G4. SIGN.**
- **G5. SIGN**, with the merged wording of D1 (section 3).
- **G6. SIGN.** Verified: TIER1_ONLY (`action_names.py:66`) and ST05 (`recipe_check.py:714-715`). For "a join with the metadata", use the wording of D2.
- **G7. SIGN WITH THIS WORDING.** "Where a branch meets the metadata, her default place is the end of tier 1 of the table that joins them (D-0549: "in manycase I would select the scope of where original T1+ metadata are joined"; D-0550 point 1: "(original step/T1 where metadata join)"). It is named as a default and can be changed. That is the review session's reading, which she confirmed: "What I read in your comments - was correct" (D-0550). The app cannot choose the scope: "the app cannot decide the scope" (D-0531)."
  - Why: "named as a default and changeable" is not in D-0531's words. It is in the reading she confirmed.
- **G8. SIGN.** `QC_Reads_Anchor` has FastP as its first ingredient, so `T1:FastP` with `T1:QC_Reads_Anchor` is nested (my map).
- **G9. SIGN.**
- **G10. SIGN.**
- **G11. SIGN WITH THIS WORDING** of the evidence: "Retest run E (the first T1 of each original): the entity stays in 5 plots. In 3 of them the table has the metadata as the base of a join (`qa_population_zscore` with `n50` and `n50_zscore` empty). The other 2 are made from the metadata alone." Why: the retest lists those 5 plots, and 2 of them are metadata-only tables, not "the metadata as the base of a join".
- **G12. SIGN.** Verified: the entity check (E01, E02) is at `recipe_check.py:332-348`.
- **G13. SIGN.** These are my words of round 2, from the evidence field of D-0485.
- **G14. SIGN.**
- **G15. SIGN.** Verified by my map: ResFinder is an ingredient of 4 joins, and only `amr_heatmap` targets it.
- **G16. SIGN.**
- **G17. SIGN WITH THIS WORDING.** "A step at the first T1 of an original does not remove the entity's row where the metadata is the base of a left join: the row comes from the metadata, and only the data columns turn empty. In `ST22_Anchor` the row still disappears, by coincidence: a later inner join by gene drops it. A step there also hits the quality plots where one original feeds both (retest B2). The join place of each table has neither problem." Why: run E shows `ST22_Anchor` as an exception, and the retest itself gives the reason.
- **G18. SIGN.**
- **G19. SIGN.**
- **G20. SIGN.**
- **G21. SIGN.**
- **G22. SIGN.**
- **G23. SIGN (PROVISIONAL).**
- **G24. SIGN.**
- **G25. SIGN.** Verified: `remove_from_all.py:292-307`.
- **G26. SIGN.** My run of section 5 gives the numbers.

## 2. X1 to X4

- **X1. OBJECT to the general claim; SIGN this wording.** "On the demo, run B3 gives the same 17 plot tables as S6. B3 nests `T1:ResFinder` above the four ResFinder joins. In general, a nested upper place changes every computation across entities that lies between it and the lower place: an aggregation or a window inside the tier 1 of a join before its end, or a computation in a tier 2. So nesting can change tables. A removal filter is idempotent only on the same table."
  - On the demo no step that computes across entities lies between a nested pair. I checked the one grouping inside a join's tier 1: `Summary_phenotype_length_fragmentation` groups by `[sample_id, ST]` (its assembly file), which is per entity. That is why B3 equals S6.
  - The general case is reasoned, not run. A join whose tier 1 computes a mean over all entities before its end would give different tables for "nested" and "lower place only".
  - My run R2 (section 5) checks the demo case without nesting.
- **X2. SIGN, with this precision.**
  - The case is real in the walk: an empty tier 2, or one that no plot reads, is folded into tier 1 (`lineage_walk.py:394-395`).
  - For a source table read directly by plots AND by joins, with an empty tier 2, the walk offers `T1:<table>`, which reaches the joins too, and the plots' own `T3:<plot>`, one per plot. It does not offer `T2:<table>`.
  - What the user would see: for ONE such plot, nothing is missing (its T3 reaches that plot alone). For TWO or more plots on such a source, there is no single place that covers those plots without the joins.
  - The audit copy already accepts `T2:<table>` when a plot reads it (`audit_copy.py:177-179`) and creates the tier (:33-37). So the fix would be in the walk's fold, which is PROVISIONAL (the walk's P6; not a decision of hers).
  - Not on the demo: ResFinder's tier 2 has 2 steps.
- **X3. Judged on merit: a fair third option for Q3, with these points.**
  - For: the author states the default, nothing is guessed, and D-0344 stays. It helps a user who is not the author ("well the problem is that the user might not be the author", D-0500).
  - Against:
    - It is a new key that the author must keep right whenever the recipe changes.
    - The app must still check it against the structure (the place must lie in that original's tree), so it does not remove the computation.
    - It turns her rule of D-0549 into a per-recipe setting (reopens D-0549: information only).
  - Under reading R1 it names one default per tree. It does not make her quality case one step.
- **X4. SIGN WITH THIS WORDING.** "Under 'one trunk', 7 demo tables would be rewritten (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_L50_integer`). One trunk would be added: VirulenceFinder has no table that joins it alone with the metadata, and after D-0523 it is a data table."

## 3. D1 to D4

- **D1. SIGN the merged wording.** "A shared place is a place with two or more originals upstream (the graph alone). For a removal by key, the dialog counts only the originals whose key reaches the place (the walk)." I know no case where the graph-only definition gives a wrong tree. A look-up table without the key (APEC) only adds a tree that a removal by key does not reach.
- **D2. SIGN your wording.** "A join with the metadata is a join whose ingredients include `metadata_schema` and at least one other original table." `QA_year_types` and `QA_aggregated_no_key` have the metadata as their only ingredient and no join step (my map).
- **D3. A wording we can both sign; the rest stays open for the owner.**
  - Her words (D-0517, evidence field): "a) well one final result could be used on T2a but T2a could be used to produce one T3a for another final result - what would be done in this case ? yes we need the `from:` this clarifies but still the hiearchy is unclear of where to place it. I want the examples on how it would like like with all the tiers and both plot and data as result". And: "where would go T3 for the reads summary for example ? where would be the from: located".
  - What her words require: a way to write "T3a made from T2a" for a result that may be a PLOT OR A TABLE, with `from:` as she was shown it.
  - What exists: for plots it works today (two plots target one table, and one has its own tier 3 steps; `recipe_graph.py:582-585`). For tables nothing exists, because a table as a result has no form yet (G13).
  - What stays open: whether that need is met by derived tables (form 3) or by a result entry that holds its own tier 3 (reading 1 against reading 2 of D-0516). D-0496: "wait for the panel".
  - Wording: "Her note N2 is met today for plot results (G14). Her requests of D-0516 and D-0517 ('yes we need the `from:`') need the decision on the form (D-0496); that decision also says whether one table's T1 may feed two T2." Stays open for the owner (Q3).
- **D4 (= X2).** Settled by reading, as in X2. The run you describe would only confirm the offer; no run is needed for the design.

## 4. Q1 to Q8: fairness and exact changes

- **Q1.**
  - (i) Change "What the app does today" to: "On screen today a step is written only at the table of the open plot ('This plot only / All plots / All plots except'). The library that lists the places is not on screen: it offers every place that holds the column, nested or not. 'Remove from all the data' is a library step with no screen; it offers 27 places on the demo."
  - (ii) Option R2 cites run B3, but B3 nests `T1:ResFinder` above the four ResFinder joins, so it is not an R2 set. Change it to the non-nested set of my run R2 (B3 with `T2:ResFinder` instead of `T1:ResFinder`). Its result: 14 plots change, the entity stays in exactly the 3 quality plots, and the tables equal B3's (0 of 17 differ), for both entities (section 5).
  - (iii) The step counts are right. Places per tree for her case (no place nested): the ResFinder tree holds 5, so at least 5 steps if the metadata tree does not count. Eleven places hold the metadata in their tree, so at least 11 steps if it does; the places of other trees fit into those 11 steps. Add: "the tables do not depend on how the places are split into steps, when every step removes the same entity".
  - (iv) My lean, said truly: "Opus does not lean. It reads your words as R1, and holds both readings as coherent. A property of R1: a shared place uses the one place of every tree it is in." Not "cost".
- **Q2.**
  - (a) Your text says "your literal rule: the first T1 of the original". Add: "your words 'same level' (D-0550) may also point to `T1:QA_L50_integer` for Quast, which is option (b)".
  - (b) Your text says "same 17 plot tables as run B3". Change it to: "with `T2:ResFinder` for `amr_heatmap` (nothing nested), the same 17 plot tables as run B3: run R2, for two entities (section 5)".
  - Otherwise fair.
- **Q3.**
  - Add the VirulenceFinder trunk to option (b).
  - Write option (c) with X3's points for and against.
  - In the related question, add the fact first: "for plots, a T3a made from a T2a that another result also uses works today; for tables nothing exists yet".
  - My lean, as written, is true.
- **Q4.**
  - Replace "Not run: we do not know yet" and "until then nobody can say" with the numbers of section 5. (a) ALL27, (b) A3 and (c) UPPER all leave the entity in 0 of 17 plots, with identical plot tables, for two entities.
  - Add what differs:
    - (a) and (c) write a step in the metadata table and in the original tables; (b) does not.
    - So the exported T1 files of the tables that no plot reads (D-0457) keep the entity under (b) and lose it under (a) and (c). This is by construction; those tables were not compared in the run.
    - (a) writes 27 places, nested ones included; (c) writes 11; (b) writes 19 (with `T1:ResFinder`) or the same with `T2:ResFinder`.
  - (b) must also say which place stands in for the `amr_heatmap` branch.
- **Q5.** Quote her words exactly:
  - D-0477: "eg. left join keeps the rows of the second table - ensure you removed in second table if this is what you want (or something similar)".
  - D-0501: "I would just shows the differents where applied and no per table warnings about downstream effects". "No warnings about the natural consequences downstream" is the title of the ledger line, not her words.
  - Otherwise fair.
- **Q6.** Add what she would see for each option:
  - (a) 17 lines in the list of steps for one decision, each removable;
  - (b) one line per decision, which opens to show its places;
  - (c) at removal, a choice between "this place" and "the whole decision".
- **Q7.** Add what she would see for each option:
  - (a) the recipe check refuses the 4 demo joins until they are rewritten (in the one move, D-0525);
  - (b) one advice line in the check report, and the recipe runs;
  - (c) a paragraph of the good-practice page.
- **Q8.** Add what she would see for each option:
  - (a) a recipe without a declared key offers no removal by key and no "remove from all the data";
  - (b) the check refuses a recipe that has a metadata table but no declared key;
  - (c) every recipe must declare the key to run.

## 5. Facts run (my runs; read-only; the load was 10 or less when they started)

**How it was run.** Script `opus_runs.py`, output `opus_runs.out`, results in `opus_runs_out/results.json` (this folder).
- Load at start: 9.99.
- Code: my worktree (`SPARMVET_VIZ_wt_goals`, `dev` `febc506f` merged); `app` and `utils` were printed from it.
- Method: the app's own functions. `remove_from_all.apply` writes the places for the runs at tier 1. `audit_copy.add_step` writes `T2:ResFinder` for run R2. Then `run_audit`, and each plot's table read with `materialize_tier3`, as in the retest.
- The second entity was chosen by a rule fixed in the script: the entity found in the most plots of the baseline, the smallest id on a tie. That is `11843673`, in 16 plots, like `10668076`.

**The runs.**
- ALL27: "remove from all the data" as decided (D-0416). All 27 offered places: tier 1 of every table that holds the key, the metadata included.
- UPPER: option (c) of Q4. The first T1 of every original that holds the key, the metadata included. Nothing nested.
- A3: the retest's run. The defaults of the reading of D-0550, nothing at the metadata. It nests `T1:ResFinder` above the four ResFinder joins.
- B3: her case. It also nests `T1:ResFinder`.
- R2: B3 with `T2:ResFinder` instead of `T1:ResFinder`. Nothing nested.

The pattern is the same for both entities:

| Run | Places | Plots changed (of 17) | The entity stays in | Columns emptied |
|---|---|---|---|---|
| ALL27 | 27 | 17 | none | none |
| UPPER | 11 | 17 | none | none |
| A3 | 19 | 17 | none | none |
| B3 | 17 | 14 | the 3 quality plots | none |
| R2 | 17 | 14 | the same 3 | none |

**The comparisons**, by hash of each plot's table:
- ALL27 = UPPER = A3: 0 of 17 plot tables differ, for both entities.
- R2 = B3: 0 of 17 differ, for both entities.

**What this settles, and what not.**
- On the demo, for these two entities, the three forms of "remove from all the data" give the same 17 plot tables.
- They differ in three ways:
  - where the steps are written: 27, 11 or 19 places;
  - whether the metadata table and the original tables carry a step: yes under ALL27 and UPPER, no under A3;
  - so, in the T1 files of the tables that no plot reads. The export writes those files (D-0457). Under A3, the metadata's and the originals' own T1 files keep the entity. This holds by construction (no step there); my run did not compare these tables.
- Her case, with no place nested (R2), gives exactly the tables of B3, in one step.
- Q4 must state both facts: the same plot tables, and different exported T1 files.

**Checked by grep.** No code passes a `tier1_only` catalogue to the recipe check (`recipe_check.py:693` reads the default). So the tier-1-only list of `action_names.py:66` applies wherever the check runs. That holds G6.

**Still to run, by others.**
- The dry run of "one trunk": it needs the check relaxed in a scratch copy, after Q3.
- The structure function against all places and the 10 retest runs: after that function exists.
- The X2 fold: not needed for the design (settled by reading).

## 6. One line

AGREED v1: I sign G1 to G26 (G1, G7, G11, G17 with my wording), X2 (with its precision), X3 (as option (c) of Q3), X4 (with the VirulenceFinder trunk), D1, D2, D3 (its wording), D4 (= X2); open between us: X1 as a general claim (my wording proposed); for the owner: Q1 to Q8, with the fixes of section 4 and the numbers of section 5.
