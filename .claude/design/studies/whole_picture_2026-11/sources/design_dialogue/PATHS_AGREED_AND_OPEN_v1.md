# Paths, derived places and parents reused: what the two agents agree on, and what only you can decide (v1, Sonnet agent, for the Opus agent to sign)

Written after both restarts. Sources: `SONNET_paths_2.md` with `RUN_REGISTER_sonnet.md`; `OPUS_paths_2.md` with `RUN_REGISTER_opus.md` and its outputs. Every number below comes from a run in which each table was rebuilt from scratch in its own empty folder, from a graph parsed from the recipe's own keys by a script that imports no lineage code, or from her words. Tags: [HER WORDS D-n] / [RECIPE FILE] / [GRAPH SCRIPT, both] / [ENGINE RUN, which] / [CODE READ] / [REASONED, not run].

## HALF PAGE FOR HER

What the two agents agree on after the restart:
1. Working apart, each of us built the graph of the demo from the recipe with an own script, and every number matched: 12 original tables, 16 joined tables, 17 plots, 85 nodes, 12 joined tables with several parents. We also found one error in the earlier test: it counted 17 joined tables; there are 16.
2. The graph is directed. A node is a place (a table at a tier). The roots are the first places of the original tables. The leaves are the results. A joined table is a node with several parents. In all 50 shipped recipes that can be read, what lies below one original table is a tree.
3. Your rule is a check the app can compute: in one step, no chosen place lies below another chosen place. That is the same as "at most one chosen place on any path". Choosing the first place of every original table is valid by this rule; it needs no special case.
4. "~" means "below a chosen place". It does not mean "changed" and it does not mean "gone". Example from the runs: a step at the ResFinder table has 14 tables below it and changes 12. Where the metadata is the first table of a left join, the entity's rows stay, with the ResFinder columns empty. Two tables below it stay exactly identical although the entity is in them.
5. Everything below a changed place is recalculated. We checked it for 55 places of the demo: the tables whose key changes are exactly the tables below the place, the tables whose content changes are among them, and a wrong stored table is never served when it carries the old key.
6. Your case "all analyses but the quality ones", written with 17 places and nothing nested, changes 14 plots and keeps the entity in exactly the 3 quality plots. The same tables come out when `T1:ResFinder` (nested) is used instead of `T2:ResFinder`.
7. The three forms of "Remove from all the data" give the same 17 plot tables and leave the entity in none. They differ in the exported tier 1 files: two forms remove the entity from every original table; the form that writes only defaults leaves it in 7 original tables.
8. Your reimport rule works on the demo for MLST: all 17 plot tables stay equal, the three MLST graphs are separate, and a step at MLST changes 5 tables instead of 10. It does not split a joined table read by several plots, and the metadata would need 13 copies or be the one exception.
9. The two readings of "each T1 coming from the parent" give different tables (5 differ). Both are valid steps.
10. Only you can decide the questions below.

The questions, in order:
- Q1 "Each T1 coming from the parent": the parent's own first place, or the first place of each table that reads it?
- Q2 A parent reused in another graph: what should the app do (show every graph, your reimport rule as advice or refusal, check after Apply, other)?
- Q3 Which place is the default where your rule says nothing?
- Q4 What does "Remove from all the data" write: the 27 places in two steps, the 11 first places, or the defaults?
- Q5 May the app say before Apply that the entity can remain in a place below?
- Q6 How must the recipe be written (today's form, "one trunk", or a declared default)?
- Q7 The earlier questions on "Remove step", the side of the metadata and the entity key: what the runs changed.

---

## 0. THE RUNS DONE BY BOTH, SIDE BY SIDE

| Question | Sonnet run | Opus run | Same result? | Difference or finding |
|---|---|---|---|---|
| Graph of the demo | own graph script (YAML only) | R1 own graph (YAML loader) | YES | 12 originals, 16 joined tables, 17 plots, 85 nodes, 12 joined nodes with several parents; 21 of 66 pairs of originals share a node below. FINDING: the retest wrote "17 joined or derived tables"; both counts give 16. The analysis group the plots call "Results" by id is called "AMR and Virulence" in the Opus text (its label): the same group. |
| Tree below each original | graph script on the demo (0 nodes with two parents); earlier script on 50 recipes through `recipe_graph` | R2 own parse on all shipped recipes | YES | 50 of 50 recipes load; all are trees below each original; no join reads a join; 93 files are not recipes. |
| Parse and graph against `recipe_graph` | X1 (the demo) | R3 (every shipped recipe) | YES | Same parents for all 85 nodes; the only difference of my parse and the loader's recipe is a derived `plots` index the loader adds. |
| Step by `add_step` against a step written by hand | V: 3 cases (a schema's tier 1, a join's tier 1, a join's tier 2) | R4: 2 cases (`T1:MLST`, `T2:ResFinder`) | YES | 0 tables differ in all 5 cases; `T1:MLST` changes 10 nodes in both. |
| The engine against my graph | A: 7 places | R5: 3 places | YES | Changed nodes always lie inside the nodes below the place: 0 outside in 10 places. |
| A place below that stays identical although the entity is in it | seen in run C (`T1:ResFinder`: `qa_fanout_rows_per_sample`; `T1:FastP`: `virulence_bar`, `virulence_variants`) and RD2 | R5 finding: `T2:QA_fanout_exhibit` and `qa_fanout_rows_per_sample` (the left join keeps the entity's 23 rows, a count per sample stays 23) | YES, same plot | I expected an unchanged place below only where the entity has no row (my register entry A): the run contradicts that, in both our runs. A second instance (mine): `T1:FastP` has 3 plots below and changes 1; `ST22_Anchor` and the two virulence plots stay identical [REASONED: the FastP columns are not in the final columns of that table]. |
| Her case, nothing nested, against nested | D1 (one entity) | R8 (two entities) | YES | 14 plots change, the entity stays in `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`; the plot tables of `T2:ResFinder` and `T1:ResFinder` are equal. |
| The forms of "remove from all" | D2, D4 (one entity; valid defaults with `T2:ResFinder`, UPPER, 27) | R7 (two entities; the nested defaults) | YES | UPPER, the defaults (valid or nested) and the 27 places give the same 17 plot tables, 17 changed, the entity in none. The engine's own list of 27 = every table but `APEC_STEC_virulence_genes`. |
| Exported tier 1 under the forms | T1X (valid defaults) | R11 (nested defaults) | YES, complementary | UPPER = the 27 places: the entity in no original table. Nested defaults: it stays in 6 original tables (FastP, Quast, Bracken, MLST, VirulenceFinder, metadata). Valid defaults (`T2:ResFinder`): 7 (also ResFinder). Both are engine runs. |
| A calculation over all entities between places | Z (the z-score on the demo) | R9 (small recipe by hand: 30 / 25 / 30) and R13 (the demo) | YES | A step before the calculation changes the `n50_zscore` of 41 of 41 other entities (largest difference 0.064); a step after it, 0 of 41 (mine). One count in a table with no key changes (Opus). |
| The reimport rule on MLST | RI (Opus's scratch recipe rebuilt by my script) | R6 | YES | 17 of 17 plot tables equal; the T1 of the new tables equals `T1:MLST`; a step at `T1:MLST`: 10 nodes on the original, 5 on the copy. |
| Two readings of D-0555 | RD1 (ResFinder) | R12 (MLST) | YES, different parents | Both show the readings differ: MLST 5 tables; ResFinder 11 nodes. COUNTING FINDING: I counted a tier 2 as a node for every table (13 and 14 nodes changed for ResFinder); the Opus runs count a tier 2 only where the table has tier 2 steps (12 and 13). The text uses the Opus convention. |
| D-0560: keys, content, below | R1 (5 places), RD2 (58 places), R2 (probe), R0 (`run_audit`) | cross-check R3; reading of `cache_keys` | YES | No finding and no defect; see G22. |
| Timing | 14 s for 13 rebuilds; 33 s for 22 | 1.0 to 1.3 s per rebuild | YES | About 1 s for one from-scratch rebuild of the whole demo (small data). Real data: not measured. |

---

## 1. THE POINTS OF THE OPUS POSITION: AGREE / DISAGREE / CHANGE

Verified by reading its outputs (`opus2_runA.out`, `opus2_runB.out`, `opus2_more.out`, `opus2_r13.out`): each says what its register says. I reran one run with my script (RI for R6).

| Opus point | Verdict | Evidence or change |
|---|---|---|
| 0 What it used before the stop, and its marks | AGREE | Same judgments as mine on `lineage_walk`, `remove_from_all.describe`/`apply`, `recipe_graph`, `run_audit`, `add_step`, `materialize_*`. |
| 1.1 to 1.5 Evidence base, graph, cross-check, `add_step` validation, graph against engine | AGREE | Mine: 85 nodes, X1, V, A. |
| 2 Independence: U1 (neither lies below the other), U2, U3, U4 | AGREE | Same as my I1 to I4. U3 (a history is a view, the rule is on paths): same reading. |
| 3 Derived and the check | AGREE | "Derived" there is node level ("below at least one chosen place"); mine adds a per-path count (section 2b). The two are compatible. |
| 4 How it is shown | CHANGE | Add to each joined node: "incoming root paths covered k of n" (mine, section 2b). |
| 5.1 to 5.3 Demo mapped, sets table | AGREE | Every row of its sets table equals mine (valid or not; pairs; plots below and outside). |
| 6 Q2, Q4, Q5 consequences | AGREE | |
| 7 What she may be missing (items 1 to 9), demo shapes | AGREE | Item 1: three MLST join places are one valid step, not "one scope per history" of D-0547: same as my reading. |
| 8 g.1 to g.5 (D-0555) | AGREE | g.1 two readings; g.2 the graphs from one parent are one per reading table; g.3 numbers (12, 4, 13 other plots) equal mine. |
| 9.1 E1 to E10 | AGREE | E7 and E8 are now run (RD2, B): the old-key wrong table is not served; two tables on one file give separate graphs. |
| 9.2 X, Y-a, Y-r, Z, W1 to W6 | AGREE | My G (coverage) is added to X; my A is W2; my K is W3; W4 to W6 are new to me and feasible by its R12 and the recipe. W5 reopens D-0022 ("only automatic placement 'remove from all tables'"): information. |
| 9.3 What can be done | AGREE | Y: feasible for the recipe and the engine (R6, RI); partly because a deployment that finds files by table name needs one file per name (`orchestrator.py:173-190`). |
| 10 Recheck | AGREE, one CHANGE | G29 ("7 tables rewritten under one trunk") is recounted by my parse: 7 (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_L50_integer`): CONFIRMED. G31 (5 or 11 steps) is void: it rests on "one place per tree", which D-0553 replaced. |
| 11 D-0560 (j.1 to j.4) | AGREE | Its case 2 ("the engine reads a parent the key does not hold") was "not seen": confirmed on 55 places by my RD2. Its tests T-1 to T-3 and my four tests are merged in G24. |

---

## 2. AGREED (each one sentence for the design, in a wording both can sign)

**G1 The graph.** Nodes are places (the tier 1 of a table, the tier 2 of a table that a plot reads, the tier 3 of a plot); an edge shows what goes into the next node; the roots are the first places of the original tables; the leaves are the results; a joined table is a node with several parents. [HER WORDS D-0553: "its more a directional graph with Tx at nodes and branches gives the directions"; "Results (final tables and plots) are leaves no ?"] [GRAPH SCRIPT, both]

**G2 The edges are the ones the engine runs.** A join reads the tier 1 of each of its ingredients (the first is the base); a table's tier 2 follows its tier 1; a plot reads the tier 2 of its target. [RECIPE FILE; CODE READ `orchestrator.py:269-283`] [ENGINE RUN: in 10 places (Sonnet A, 7; Opus R5, 3) every node the engine changed lay inside the nodes below the place]

**G3 The demo.** 12 original tables, 16 joined tables, 17 plots, 85 nodes, 12 joined nodes with several parents (`ST22_Anchor` 6 parents, `QC_Reads_Anchor` 4, `AR1_MLST_Serotype_Virulence` 4, `QA_fanout_exhibit` 3, eight with 2); the metadata is read by 13 tables (the first table in `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; the only one in `QA_year_types` and `QA_aggregated_no_key`; a later one in 7); 6 tables have no plot below them (`Quality_metrics`, `Detailed_summary`, `FastP_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `AR1_MLST_Serotype_Virulence`). The earlier "17 joined or derived tables" is corrected to 16. [GRAPH SCRIPT, both]

**G4 What lies below one original table is a tree** in each of the 50 shipped recipes that load, and no join reads a join; it stays so while joins read source tables only (D-0344) and a derived table reads one table. [GRAPH SCRIPT, both; ENGINE-free] [HER WORDS D-0550: "each independent history is like an independent tree graph"]

**G5 Independence and the valid set.** Two places are independent when neither lies below the other; a set of chosen places is valid in one step when its places are pairwise independent; that is the same as "at most one chosen place on any path". [HER WORDS D-0553: "the user chooses at most one place =node ... then all paths are derived (~) and cannot be choosen. yes R2 rule"] [GRAPH SCRIPT, both; the equivalence REASONED]

**G6 The exception of the original parents follows from G5.** The first places of the original tables have only their files above them, so no one lies below another and the set of all of them is valid (11 places that declare the key; `APEC_STEC_virulence_genes` declares none). [HER WORDS D-0553: "(with the exception of the original parents where all can be choosed)"; D-0547: "The only exception is if the user wants to one or several eg all FIRST T1"] [GRAPH SCRIPT, both]

**G7 Derived.** A place is derived when it lies below a chosen place; it is shown with "~" and cannot be chosen in the same step; a later step may choose it ("he must add another step audit step later - choosing a different scope"). [HER WORDS D-0547, D-0553]

**G8 "~" means "below", not "changed" and not "gone".** At `T1:ResFinder`: 14 tables below, 12 changed; the entity's rows stay in `QA_AMR_per_sample` (1 row), `ST22_Anchor` (7) and `QA_fanout_exhibit` (23) with ResFinder's columns emptied, because the metadata is the first table of those left joins; `T2:QA_fanout_exhibit` and the plot `qa_fanout_rows_per_sample` stay identical (a count per sample stays 23); at `T1:MLST` the entity's rows leave `AR1_MLST_Serotype_Virulence` (MLST is its first table) and stay in `ST22_Anchor` (7). At `T1:FastP` 3 plots lie below and 1 changes. [ENGINE RUN: Opus R5, R12; Sonnet C, RD1, RD2] [HER WORDS D-0545: the effect is known after Apply]

**G9 Sets on the demo (valid in one step or not).** The 11 first places: valid. The 27 places of "Remove from all the data" as decided: not valid (35 nested pairs: from `T1:metadata_schema` 13, `T1:Quast` 4, `T1:ResFinder` 4, `T1:FastP` 3, `T1:MLST` 3, `T1:VirulenceFinder` 3, `T1:Bracken` 2, `T1:Summary_quality` 2, `T1:Summary` 1); they can be written in 2 steps (the first places, then the joined tables). The 19 defaults with `T1:ResFinder`: not valid (4 pairs); with `T2:ResFinder`: valid. Her case with `T1:ResFinder`: not valid; with `T2:ResFinder`: valid (17 places). `T1:MLST` with its three join places: not valid; the three join places: valid. `T1:ResFinder` with `T1:QA_AMR_per_sample`: not valid; `T1:ResFinder` with `T1:metadata_schema`: valid; `T2:ResFinder` with `T1:QA_AMR_per_sample`: valid. [GRAPH SCRIPT, both: every row equal]

**G10 How she removes the row that comes from the metadata side** (in `QA_AMR_per_sample` the metadata is the first table): choose `T1:QA_AMR_per_sample` instead of `T1:ResFinder` for that branch; or choose `T1:ResFinder` and `T1:metadata_schema` (two first places; the metadata place is "not advised", D-0547); or keep `T1:ResFinder` and add a second step later at `T1:QA_AMR_per_sample`. All valid. [HER WORDS D-0547; GRAPH SCRIPT, both] [ENGINE RUN: the valid defaults with `T1:QA_AMR_per_sample` and `T2:ResFinder` leave the entity in no plot (Sonnet D2, Opus R7)]

**G11 Her case, nothing nested, rebuilt from scratch.** 17 places (9 joined tables with the metadata, 2 tables made from the metadata alone, the 4 originals with no metadata join, `T2:ResFinder`, `T1:QA_L50_integer`): 14 plots change; the entity stays in exactly `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`; the plot tables equal those of the nested form with `T1:ResFinder`. [ENGINE RUN: Sonnet D1 (1 entity); Opus R8 (2 entities)] [HER WORDS D-0549: "remove the samples from all analyses BUT the ones that show the bad quality"]

**G12 The three forms of "Remove from all the data" give the same 17 plot tables**, 17 changed, the entity in none (two entities); the list of 27 places the engine's tier 1 tables give (every table but `APEC_STEC_virulence_genes`, which has no `sample_id`) equals the old list. [ENGINE RUN: Sonnet D2/D4/E; Opus R7]

**G13 What the exported tier 1 files hold.** The 11 first places and the 27 places leave the entity in no original table; the nested defaults (19 with `T1:ResFinder`) leave it in 6 (FastP, Quast, Bracken, MLST, VirulenceFinder, metadata); the valid defaults (19 with `T2:ResFinder`) leave it in 7 (also ResFinder). The export writes these files (D-0457). [ENGINE RUN: Opus R11; Sonnet T1X]

**G14 The set of the first T1 of every original except the metadata** removes the entity from the 4 plots whose every incoming root path holds a chosen place, and leaves it in 5 (`qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `qa_population_zscore`, `qa_year_label`, `qa_facet_by_mapping`), where the metadata is the first table of the join or the only one. [ENGINE RUN: Sonnet D3; same numbers as the earlier retest] [HER WORDS D-0549: "The metadata should be the right table -- best practice"]

**G15 Two chosen places, one below the other: the upper decides a calculation that lies between them.** On a small recipe (values 10, 20, 30, 40; a mean over all rows between the places): the upper place alone gives mean 30, the lower alone 25, both 30 (the upper's table). On the demo: a step before the z-score changes the `n50_zscore` of 41 of 41 other entities (largest 0.064), a step after it 0 of 41; one count in a table with no key changes. The lower place can still remove a row that came from another table of a join (set E against the valid defaults, G13 and G14). [ENGINE RUN: Opus R9, R13; Sonnet Z] [HER WORDS D-0501: "things cannot be the same because we changed earlier in the recipe"]

**G16 The two readings of "each T1 coming from the parent" give different tables.** MLST: step at `T1:MLST` changes 10 tables and leaves the entity's 7 rows in `ST22_Anchor` and both virulence plots with MLST's columns empty; steps at the three join places change 9 tables and remove those rows, and `T1:MLST` keeps the entity; 5 tables differ (`T1:MLST`, `T1:ST22_Anchor`, `T2:ST22_Anchor`, `virulence_bar`, `virulence_variants`). ResFinder: 12 tables change under `T1:ResFinder`, 13 under the four join places and `T2:ResFinder` (a tier 2 is counted only where the table has tier 2 steps: the same convention as the Opus runs; my own count with every tier 2 as a node is 13 and 14); the entity leaves `QA_AMR_per_sample`, `ST22_Anchor`, `QA_fanout_exhibit` only under the second; 11 nodes differ. [ENGINE RUN: Opus R12; Sonnet RD1] [HER WORDS D-0555]

**G17 The graphs that go from the same parent** are one per reading table (the joined tables that list the parent as an ingredient, and the parent's own tier 2 when a plot reads it): that table and everything below it; today they never meet below (a join reads original tables only). Two results share only the metadata when it is the only original above both (45 of the 97 pairs of results in different analysis groups; 17 pairs share another original). Six parents feed results in more than one group: `Summary_quality`, `FastP`, `Quast`, `ResFinder`, `VirulenceFinder`, `metadata_schema`. From one plot, the other plots below its originals: `mlst_bar` 12, `amr_heatmap` 4, `qc_reads_horizontal_barplot` 13. [GRAPH SCRIPT, both] [HER WORDS D-0555: "so we need here to have the 2 directed graphs that go from the same parents - because both will be affected"]

**G18 A joined table read by several plots is a shared node too** (`ST22_Anchor`, `MLST_with_metadata`, `Quast_with_metadata`: its two plots are in two groups; `QA_year_types`): the gotcha is not only at the original parents. [GRAPH SCRIPT, both]

**G19 Two source tables on one file stay separate.** `Summary` and `Summary_quality` read one file: a step at `T1:Summary` changes 1 plot, at `T1:Summary_quality` 2, at both 2. [ENGINE RUN: Sonnet B]

**G20 Her reimport rule applied to MLST** (three source tables on one file, each read by one table): 17 of 17 plot tables equal the original's (rebuilt), the T1 of the new tables equals `T1:MLST`, a step at `T1:MLST` changes 5 tables instead of 10; the author wrote 2 new schema entries (10 lines each, the same includes), changed 2 ingredient lines and 1 `right_ingredient`; the whole rebuild took about 1 s either way (demo data). What it does not split: a joined table read by several plots; a joined table of several originals; a calculation over all entities; the metadata unless it is copied (13 tables read it). In a deployment that finds files by table name each copy needs its own file named by its table id. [ENGINE RUN: Opus R6; Sonnet RI; CODE READ `orchestrator.py:173-190`, `data_import_check.py:83, 177-178`] [HER WORDS D-0556]

**G21 What can go wrong when a parent or a shared node feeds several graphs** (E1 to E10): results change outside the graph the user started from; the user does not see them; the metadata is a parent of 13 tables and 13 of 17 plots in 4 groups; one step does different things in different graphs (first table of a left join: rows leave; side: rows stay, columns empty); the values of other entities change where a calculation over all entities lies below; two chosen places in one step (the upper decides); two tables on one file are separate; the two readings of D-0555 differ; the same plots can leave different exported tables; tables no plot reads receive the step too. [ENGINE RUN and GRAPH SCRIPT as in G8, G13, G15, G16, G19; E2 REASONED]

**G22 Everything below a change is recalculated (D-0560).** A table's tier 1 key holds the engine, the definition of the table and of every table above it, the content of the data files, and the audit steps of the table and of everything above it; the tier 2 key is the tier 1 key plus its own steps; a plot's key is the tier 2 key of its target plus its own steps. [CODE READ `cache_keys.py:14-28`] For the 55 writable places of the demo that the engine accepts (T1 of 28 tables, T2 of the 13 tables a plot reads, T3 of 17 plots; the engine refuses a removal where the column `sample_id` is absent: `T1:APEC_STEC_virulence_genes`, `T2:QA_aggregated_no_key`, `T3:qa_aggregated_no_key`): no node below the place kept its key, no node whose content changed kept its key, no key changed outside the nodes below. `run_audit`'s skip of a plot with an unchanged key gave the same plot tables as a from-scratch build (`T1:MLST`: 0 of 17 differ; the plots it calls affected are exactly the plots that differ). The edges the keys follow equal my parse on 50 of 50 recipes. [ENGINE RUN: Sonnet R1, RD2, R0; Opus R3, R5] This is shown for one entity on the demo, not for every recipe.

**G23 A wrong stored table is served exactly when its footer key equals the current key.** A wrong table with the old key (the original's table, or one row removed) at the audited table's name is refused (`read_anchor_if_key`) and rebuilt, by a normal build and by `run_audit`; a wrong table stamped with the new key is served by both. So a stale table can be served only if a key fails to change when it should, or if a table is written with a key that is not its own. [ENGINE RUN: Sonnet R2; CODE READ `transformer/anchor.py:109-118`]

**G24 Requirement (D-0560) and its tests.** After a change at a place, every place below it is recomputed from its parents; a table stored before the change is never read for a place below it unless the app can prove it was built from the same definition, the same data and the same audit steps. The tests of the new structure: (1) for EVERY place of a recipe, write an audit step, rebuild from scratch in empty folders and assert that every node below has a changed key, every node whose content changed has a changed key, and no key changes outside "below", with "below" computed from the recipe's own keys; (2) store a table built before the step, stamped with the old key, under the name of a table below the step: the audit must equal the from-scratch table, and the test must fail when the audit part of the key is left out; (3) the skip of an unchanged plot gives the same plot tables as building every plot from scratch; (4) recipes with a join of several originals, a table read by joins and by a plot, a plot with its own tier 3, and a calculation over all entities; (5) an equality "0 of n differ" counts as evidence only when both sides were rebuilt in separate empty folders. [HER WORDS D-0560: "we need to ensure that everystep after a change in a place is recalculated - that would otherwise produce errors indeed"] [REASONED; ENGINE RUN G22, G23]

**G25 What the app can show before Apply, and what only after.** Before Apply, structure only: the graph; each place's table and tier; its kind (original, joined, plot); its parents with the base marked and the join kind; its state (chosen, "~", free); for each chosen place the results below it by analysis group, with the results outside the plot the user started from marked, and the tables no plot reads (they are exported); for a joined node, through which parent it is below. After Apply: which results changed, the entity's rows, the values of other entities. [HER WORDS D-0545: "you cannot see effect if you do not recalculate"; D-0546: "again after apply"; D-0457] [GRAPH SCRIPT]

**G26 Facts of the demo that make the rule harder (facts only; the demo is not changed by agents).** The metadata is the first table of 4 joined tables with analyses; originals are read by several joined tables; one joined table has 6 originals and two have 4; a plot reads an original's own tier 2 next to that original's joins (`amr_heatmap`); two tables read one file; 6 tables have no plot below them. What an author can write today within today's format: the metadata as the right table of every join; one join of an original with the metadata read by all the plots of that original (several plots can target one join, as `mlst_bar` and `year_distribution` do); a second source table on the same file for a second use (G20). [RECIPE FILE `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`; HER WORDS D-0547: "T1 original -> left_join -> metadata"; D-0549]

**G27 The earlier signed points (G1 to G31 of `DESIGN_AGREED_AND_QUESTIONS.md`) after the restart.**
| Earlier point | Now |
|---|---|
| G1 place; G2 original table; G7, G9, G12, G13, G21, G22, G23, G30 (her words, recipe keys) | stand (no old code) |
| G3 tree; G4 derived; G5 shared place counts (6, 4, 4); G14 shared tiers today; G15 `T1:ResFinder` has 5 children; G18 metadata-alone tables; G19 join places per original; G29 "7 tables" | CONFIRMED by own parses and engine runs (G3, G4, G17, G18 here) |
| G6 join with the metadata, ST05 | stands (checker code) |
| G8 no nesting in one step | stands, now computed (G5, G9 here) |
| G10 "the column's fate from the walk" | VOID as a design source (D-0558); the walk is not used |
| G11, G15 (run part), G16, G17, G24, G26, G27 (demo claim) | CONFIRMED from scratch (G8, G11, G12, G14, G15 here); the number "stays in 5 plots" of run E and "equal plot tables" now rebuilt |
| G25 what is on screen today | stands (grep of `app/`); "27 places" confirmed by the engine's tier 1 tables (G12) |
| G28 the fold of an empty tier 2 | describes the old walk; not used |
| G31 smallest number of steps (5, 11) | VOID: it rests on "one place per tree"; D-0553 chose "at most one place on a path" (the smallest number for her case is now 1 step with 17 places, G11) |
| Q5 "certain only at a join on the entity key" | VOID (rested on the walk's `Hop`); replaced by G8 and the structure of G25 |

---

## 2b. ONE SIDE ONLY (Sonnet; the Opus agent signs or objects)

**X1 Coverage per incoming path.** For a joined node, "incoming root paths that hold a chosen place: k of n", with the uncovered parents named; it is structure, not a claim about the entity. After `T1:MLST`: `MLST_with_metadata` 1 of 2, `ST22_Anchor` 1 of 6, `AR1_MLST_Serotype_Virulence` 1 of 4. It is a necessary sign, not a sufficient one: in the set of the first T1 of every original except the metadata the entity stayed in 5 plots, all among the 13 plots with an uncovered incoming path (8 flagged plots lost it). [GRAPH SCRIPT + ENGINE RUN Sonnet D3; REASONED: a row can reach a table only through an incoming path]

---

## 3. STILL DISAGREED BETWEEN THE TWO AGENTS

None found. Two points of wording are settled in the text: "derived" is node level (below at least one chosen place) and the coverage per path is shown beside it (X1); "13 copies" or "12 more tables" for the metadata under the reimport rule are the same count (13 tables read it, so 13 copies in all).

---

## 4. FOR YOU

Most blocking first. Each question stands alone. What the screen shows today: a step is written at the finished table of one plot ("this plot only / all plots / all plots except"); the place list, the tree view, "Remove from all the data" and the audit copy exist only as code that no screen calls, except the rule that refuses to drop a key column, which HOME calls.

### Q1 "Each T1 coming from the parent": which place?
**The situation.** You wrote: "if several parents are choosen the step applied must be applied in each T1 comming from the parent". On the demo the MLST table is read by three joined tables (`MLST_with_metadata`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`).
**Option 1: the parent's own first place** (`T1:MLST`). One step. The entity leaves the MLST table, `MLST_with_metadata` and its two plots, and `AR1_MLST_Serotype_Virulence` (exported). It stays in `ST22_Anchor` (7 rows, with MLST's columns empty) and so in both virulence plots (7 rows each). 10 tables change. For ResFinder the same reading changes 12 tables; the entity stays in `QA_AMR_per_sample` (1 row), `ST22_Anchor` (7) and `QA_fanout_exhibit` (23) with ResFinder's columns empty.
**Option 2: the first place of each table that reads the parent.** MLST: three steps at the three join places. The entity leaves the three joined tables and the four plots below them, and stays in the MLST table itself, which is exported (1 row). 9 tables change. For ResFinder: four join places and `T2:ResFinder` (read by `amr_heatmap`): 13 tables change; the entity leaves all of `QA_AMR_per_sample`, `ST22_Anchor`, `QA_fanout_exhibit` and stays in the ResFinder table. The two options differ in 5 tables for MLST (`T1:MLST`, `T1:ST22_Anchor`, `T2:ST22_Anchor`, `virulence_bar`, `virulence_variants`) and 11 nodes for ResFinder. Both are valid steps.
**Option 3: both are offered, you choose for each parent.** **Option 4: neither, say what you meant.**
**What the two agents think.** Sonnet: option 2 is the set of the join places that your default of D-0549 already names, and it removes the entity from the large joined tables; the parent's own table then keeps it until a later step at `T1:MLST`; as a lean, not a decision. Opus gives no lean on the two readings; its per-graph ticks (Q2) build on option 2. [D-0555, D-0549, D-0547]

### Q2 A parent reused in another graph: what should the app do?
**The situation.** A table that several tables read can carry a step into results you are not looking at. On the demo, a step at the MLST table also changes `virulence_bar`, `virulence_variants` and the exported `AR1_MLST_Serotype_Virulence`; a step at the metadata changes 13 of the 17 plots in 4 groups; six parents feed results in more than one group. Starting from `mlst_bar`, 12 other plots lie below its originals; from `amr_heatmap`, 4; from `qc_reads_horizontal_barplot`, 13.
**Your reimport rule, run on MLST.** MLST becomes three source tables reading the same file, each read by one table. Result: all 17 plot tables equal the original's; the three graphs are separate; a step at MLST changes 5 tables instead of 10. The author writes 2 new schema entries (10 lines, the same includes) and changes 3 ingredient lines; the rebuild of the demo took about 1 s either way. It does not split: a joined table read by several plots (`Quast_with_metadata`'s two plots are in two groups), `ST22_Anchor` (6 originals), a calculation over all entities. The metadata is read by 13 tables: 13 copies, or the one exception (then a step at its first place still reaches 13 of the 17 plots, and you call that place "not advised"). In a deployment that finds files by table name, each copy needs its own file named by its table.
**The options:**
| # | Option | What it prevents | What it does not | What the author sees | What the user sees | Complex recipes | Can it be done |
|---|---|---|---|---|---|---|---|
| X | Before Apply, show every graph that goes from each chosen place, results by group, and for each joined table how many incoming paths hold a chosen place | surprise from results you did not open | the choice stays yours; the effect is known after Apply | nothing new | a block per reading table: MLST 3 blocks, 4 plots; metadata 13 blocks, 13 plots | works; the list grows with the recipe | yes: computed from the recipe |
| Y-a | Your rule as an advice of the recipe check: a source table read by several tables is flagged | the reuse at the original level | the reuse one level down (a joined table read by several plots), the metadata unless copied, steps inside one graph | an advice per shared original (8 originals and the metadata on the demo) | smaller graphs after the author splits | works for originals only | yes; in a deployment that finds files by name, one file per table name |
| Y-r | Your rule as a refusal | the same, forced | the same; the demo itself would stop loading until 8 originals and the metadata are split | a refusal naming the tables | the same | the same | partly |
| Z | X and Y | both | as X | as Y | as X plus the advice | as X and Y | partly |
| W1 | The confirmation names every graph and result the step reaches; the log keeps the list | writing without reading | a wrong confirmation | nothing | one list to confirm | works | yes |
| W2 | After Apply, the app names the results that changed outside the plot you started from; you can remove the step | an unnoticed change | the change before you see it | nothing | "also changed: ..." | works | yes (a rebuild and a comparison per table) |
| W3 | A step is written only at a place whose whole reach was shown and confirmed | an unseen reach | | nothing | a gate on W1 | works | yes |
| W4 | Per-graph ticks: each reading table of a chosen parent is a line, all ticked; unticking one writes the step at the first places of the graphs you keep | a graph you do not want reached | the two readings differ (Q1); other entities' values | nothing | ticks per reading table | works while the graphs from one parent never meet below (true today) | yes |
| W5 | You tick results; the app proposes the highest places whose reach lies inside them | reach beyond the results you chose | other entities' values | nothing | ticks on results; places proposed | works | computable; reopens D-0022 |
| W6 | The recipe check tells the author which tables several tables read and what lies below them | an author's surprise | the user's choice | a list per shared table | nothing | works | yes |
Also: **neither, say what you meant.**
**What the two agents think.** Both lean to X with W4 and W2, and to Y as an advice rather than a refusal: X and W2 cover a parent shared at every level (an original, the metadata, a joined table read by several plots); Y splits only originals and leaves steps inside one graph and values of other entities. The recompute of Y is a fact of that option: each copy is ingested and its tier 1 is run again at the first opening; on the demo this cost nothing measurable; on real data it is not measured. Both agents say it is yours to decide. [D-0555, D-0556, D-0557, D-0545, D-0543]

### Q3 Which place is the default where your rule says nothing?
**The situation.** Your rule: the default is where the original table and the metadata are joined; with no metadata join, "the first T1 of the lineage when no metadata join (so same level except there is no metadata joined)". On the demo some branches have no metadata join: `amr_heatmap` reads ResFinder itself; `qa_l50_integer` reads a table made from Quast alone; `QA_year_types` and `QA_aggregated_no_key` are made from the metadata alone; the Summary tables have no metadata. In ResFinder and Quast the same original has both kinds of branch. The first place of an original lies above every join place of that original, so by your rule of "at most one place on a path" the two together are not valid in one step.
**Options.**
- (a) The first place of the original (`T1:ResFinder`, `T1:Quast`; `T1:metadata_schema` for the metadata-only tables). Valid alone: it then covers every path of that original. On the demo: `T1:Quast` removes the entity from the quality plots too; the first place of every original except the metadata leaves the entity in 5 plots (G14).
- (b) The first place that only that branch reads: `T2:ResFinder` for `amr_heatmap`, `T1:QA_L50_integer`, `T1:QA_year_types`, `T1:QA_aggregated_no_key`. Valid together with the join places; the 19 defaults give the same 17 plot tables (entity in none).
- (c) No default ticked on these branches; you choose with the graph.
**Neither: say what you meant.**
**What the two agents think.** Both leave it to you. Sonnet leans to (b) as a named default where a branch has no metadata join, and none where unsure. Opus: your words "same level" point to `T1:QA_L50_integer`; for `amr_heatmap` no table at that level exists, so the choice is yours. [D-0549, D-0550, D-0553]

### Q4 What does "Remove from all the data" write?
**The situation.** Decided: tier 1 of every table that holds the key (27 places on the demo). Under your rule it holds nested pairs (35), so it is not one valid step.
**Options, from our runs (two entities).**
- (a) The 27 places in two steps: the first places, then the joined tables (valid across steps). 17 plots change, the entity in none. The exported tier 1 files lose the entity everywhere.
- (b) The 11 first places that declare the key, one step. Same plots and the same exported files as (a).
- (c) The defaults, valid form (19 places with `T2:ResFinder`), one step. Same 17 plot tables, entity in none. The exported tier 1 files of 7 original tables (FastP, Quast, Bracken, ResFinder, MLST, VirulenceFinder, the metadata) keep the entity (engine run). With the nested form (`T1:ResFinder`) it is 6 (engine run).
- The plot tables are identical in all forms; the difference is where the steps are written and what the export holds.
**Neither: say what you meant.**
**What the two agents think.** Neither agent chooses. (c) is the review session's reading and was not decided ("to be asked once when the plan is checked", ledger D-0550, not her words). (a) keeps the form you decided. [reopens D-0416; D-0553, D-0549, D-0457]

### Q5 May the app say, before Apply, that the entity can remain in a place below?
**The situation.** "~" is not "changed". At `T1:ResFinder`, `qa_fanout_rows_per_sample` and its table lie below and stay identical although the entity is in them (23 rows, a count per sample); at `T1:FastP`, 3 plots lie below and 1 changes. Where the metadata is the first table of a left join, the entity's rows stay with the columns of the chosen table empty.
**Options.**
- (a) Nothing before Apply; after Apply, the list of results that changed and did not.
- (b) Before Apply, a plain note on a place below a chosen place through the side of a left join: "this table is built from <parent> as the side of a left join; the entity's rows may stay with that parent's columns empty".
- (c) Before Apply, structure only: for each joined table, through which parent it lies below, whether that parent is the first table or a side, and how many incoming paths hold a chosen place; no sentence about the entity.
- (d) (c) before Apply and (a) after.
**Neither: say what you meant.**
**What the two agents think.** Neither decides. For a note: your words "eg. left join keeps the rows of the second table - ensure you removed in second table if this is what you want (or something similar)" and "try to give as clear information as possible - so the user has elements it needs to be able to make a good decision". Against warnings: "I would just shows the differents where applied and no per table warnings about downstream effects"; "again after apply". Sonnet leans to (d): the structure is information, the entity's fate belongs after Apply. Opus gives no lean; it shows what the structure and the runs say. [D-0477, D-0543, D-0501, D-0545, D-0546]

### Q6 How must the recipe be written so that the place is clear?
**The situation.** The graph and the rule of "at most one place on a path" are computed from today's recipe; no new key is needed. On the demo each data table meets the metadata in several joined tables, and one joined table is made from 6 originals. Your best practice: original, left join, metadata (the data is the left table); in 4 demo joins the metadata is the first table.
**Options.** (a) Today's form; the app computes the join places per branch. (b) "One trunk": each data table joined with the metadata once, every other table of that history made from it; 7 demo tables would be rewritten (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_L50_integer`), `VirulenceFinder` has no such table, and it needs a join that reads a joined table, or derived tables; your case still needs places below the trunk [reopens D-0344]. (c) The recipe author names the default place of each original (a new key) [reopens D-0549]. (d) Neither.
**What the two agents think.** Both: the rule does not depend on this choice; (a) with documentation of the practice (the metadata as the right table; one join per original read by all its plots) is enough to define the rule; (b) makes the default unique and does not make your quality case one choice. Her note on "T2a and T3a" (D-0517) needs the decision on derived tables only for results that are tables. [D-0344, D-0496, D-0517, D-0547, D-0549]

### Q7 The earlier questions on "Remove step", the side of the metadata and the entity key
- "Remove step" (one step or the whole decision): unchanged. One decision written at several places stays one event in the audit log (provisional). [D-0314, D-0315, D-0478]
- The side of the metadata (a rule, an advice or documentation): the runs add a fact. Where the metadata is the first table of a left join, a step at the data table leaves the entity's rows (`QA_AMR_per_sample` 1 row, `ST22_Anchor` 7, `QA_fanout_exhibit` 23). A rule "the metadata is the right table" would make the 4 demo joins with the metadata first be rewritten. [D-0547, D-0549, D-0550]
- The entity key declared: unchanged; the engine confirms that every table but `APEC_STEC_virulence_genes` holds `sample_id` and refuses a removal step where the column is absent. [D-0313, D-0511]

---

## 5. FACTS STILL TO RUN (each with its three points written in the registers)
- Reading (ii) of D-0555 for the Quast and metadata parents (what each reading changes): same three points as RD1; not run.
- The value of the `QA_aggregated_no_key` count (19 to 18); the emptied columns of `qc_reads_horizontal_barplot` under `T1:Quast`: neither bears on a question; not run.
- The tests of G24 as general tests over every place of every recipe: they belong to the build of the new structure.
- Timing on real data: not measured.

AGREED v1 (Sonnet): G1 to G27, X1 one-sided; open between us: none; for the owner: Q1 to Q7. To be signed by the Opus agent.
