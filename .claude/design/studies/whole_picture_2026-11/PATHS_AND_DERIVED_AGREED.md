# Paths, derived places and a parent reused in another graph: what the two agents agree on, and the questions only the owner can answer

**What this file is.** The review that the owner ordered of what an independent path is and what is derived (ledger D-0553), with her note on several chosen parents (D-0555), the investigation of how to avoid the errors of a parent reused in another graph (D-0556, D-0557), and the evidence rules she gave (D-0558 to D-0561). It was made by two design agents, one Opus and one Sonnet, who agreed on every point before it was written, as she ordered (D-0552). Nothing here is decided by the agents. The design documents are written after her answers.
**Date:** 2026-11-23.
**Signed by both agents:** see the last line.
**Where the evidence lives.** In the scratch folder `tmpAI/coordinator/design_dialogue/` (not in git): the two run registers `RUN_REGISTER_sonnet.md` and `RUN_REGISTER_opus.md` (every run has its requirement, its expected result and its reason of independence, written before the run); the two positions `SONNET_paths_2.md` and `OPUS_paths_2.md`; the merged list `PATHS_AGREED_AND_OPEN_v1.md` with the Opus replacements `OPUS_signs_paths_v1.md`; the scripts and outputs under `paths2/` (Sonnet: `sonnet_graph2.py`, `sonnet_partR.py`, `sonnet_engine_run1_V_R0.py`, `sonnet_engine_run2_A_to_E.py`, `sonnet_runZ.py`, `sonnet_T1X.py`, `sonnet_RD.py`, `sonnet_RD2.py`, `sonnet_check_reimport.py`, `sonnet_CK.py` and their `.out` files) and `opus2_*.py` with `opus2_*.out` (Opus). The retest with her scope is `tmpAI/coordinator/whole_picture/RETEST_her_scope.md`.
**The limits.** One recipe (the demo `1_test_data_ST22_dummy`), one entity for most runs and two for the others, small data. Timing on real data is not measured.
**How every number was made.** Each table was rebuilt from scratch in its own empty folder, so a stored table cannot make two results look equal. The graph was read from the recipe's own keys by a script that imports no lineage code. Where a point is only reasoned, it says so.

> **Note of 2026-11-23:** four places of this file say or imply that a count of rows per entity stays 23 or that a row with empty values is counted. They are not rewritten; each is followed by a correction (the half page item 4, the paragraph of question Q6, the bullet of the side of the metadata, and G8). See `CAUSE_AND_SOLUTIONS_ZEROS.md`.

---

## HALF PAGE FOR HER

What the two agents agree on after the restart:
1. Working apart, each of us built the graph of the demo from the recipe with an own script, and every number matched: 12 original tables, 16 joined tables, 17 plots, 85 nodes, 12 joined tables with several parents. The earlier test counted 17 joined tables; there are 16.
2. The graph is directed. A node is a table at a tier, or a plot. The roots are the original data files; the leaves are the results. A joined table has several parents. In all 50 shipped recipes that can be read, what lies below one original table is a tree.
3. Your rule is a check the app can compute: in one step, no chosen place lies below another chosen place. That is the same as "at most one chosen place on any path". Choosing the first place of every original table is valid by this rule; it needs no special case.
4. "~" means "below a chosen place". It does not mean "changed" and it does not mean "gone". Example from the runs: a step at the ResFinder table has 14 tables below it and changes 12. Where the metadata is the first table of a left join, the entity's rows stay, with the ResFinder columns empty. Two tables below it stay exactly identical although the entity is in them.
   > **Correction of 2026-11-23 (ledger D-0563; see `CAUSE_AND_SOLUTIONS_ZEROS.md`):** the 23 are the entity's 23 virulence genes, which come from the VirulenceFinder table and which a step at the ResFinder table does not touch; the table counts the genes that are present, not rows. The two tables stay identical because the place chosen does not cover that path and because the join starts from the metadata; it is not a count of an empty row.
5. Everything below a changed place is recalculated. One of us checked it on the demo, with one entity, at each of the 55 places where the engine accepts a step: the tables whose key changes are exactly the tables below the place, and the tables whose content changes are among them. A wrong stored table that carries the old key is never served.
6. Your case "all analyses but the quality ones", written with 17 places and nothing nested, changes 14 plots and keeps the entity in exactly the 3 quality plots. The same tables come out when `T1:ResFinder` (nested) is used instead of `T2:ResFinder`.
7. The three forms of "Remove from all the data" give the same 17 plot tables and leave the entity in none. They differ in the exported tier 1 files: two forms clear every original table; the form that writes only defaults leaves the entity in 7 original tables (6 when `T1:ResFinder` is used instead of `T2:ResFinder`).
8. Your reimport rule works on the demo for MLST: all 17 plot tables stay equal, the three MLST graphs are separate, and a step at MLST changes 5 tables instead of 10. It does not split a joined table read by several plots, and the metadata would need 13 copies or be the one exception.
9. The two readings of "each T1 coming from the parent" give different tables (5 tables differ for MLST, 11 for ResFinder). Both are valid steps.
10. Only you can decide the questions below.

The questions, in the order that the two agents propose (each answer changes the next):
- Q1 A parent reused in another graph: what should the app do (show every graph, your reimport rule as advice or refusal, a check after Apply, other)?
- Q2 "Each T1 coming from the parent": the parent's own first place, or the first place of each table that reads it?
- Q3 How must the recipe be written (today's form, "one trunk", or a declared default)?
- Q4 Which place is the default where your rule says nothing?
- Q5 What does "Remove from all the data" write: the 27 places in two steps, the 11 first places, or the defaults?
- Q6 May the app say before Apply that the entity can remain in a place below?
- Q7 The earlier questions on "Remove step", the side of the metadata and the entity key: what the runs changed.

---

## HER QUESTIONS

What the screen shows today: a step is written at the finished table of one plot ("this plot only / all plots / all plots except"). The place list, the tree view, "Remove from all the data" and the audit copy exist only as code that no screen calls, except the rule that refuses to drop a key column, which HOME calls.

### Q1 A parent reused in another graph: what should the app do?
**The situation.** A table that several tables read can carry a step into results you are not looking at. On the demo, a step at the MLST table also changes `virulence_bar`, `virulence_variants` and the exported `AR1_MLST_Serotype_Virulence`; a step at the metadata changes 13 of the 17 plots in 4 groups; six parents feed results in more than one analysis group. Starting from `mlst_bar`, 12 other plots lie below its originals; from `amr_heatmap`, 4; from `qc_reads_horizontal_barplot`, 13.
**Your reimport rule, run on MLST.** MLST becomes three source tables that read the same file, each read by one table. Result: all 17 plot tables equal the original's; the three graphs are separate; a step at MLST changes 5 tables instead of 10. The author writes 2 new schema entries (10 lines each, the same includes) and changes 2 ingredient lines and 1 `right_ingredient` line; the rebuild of the demo took about 1 s either way. It does not split: a joined table read by several plots (`Quast_with_metadata`'s two plots are in two groups), `ST22_Anchor` (6 originals), a calculation over all entities. The metadata is read by 13 tables: 13 copies, or the one exception (then a step at its first place still reaches 13 of the 17 plots, and you call that place "not advised"). In a deployment that finds files by table name, each copy needs its own file named by its table.
**The options:**
- X. Before Apply, show every graph that goes from each chosen place, with its results by analysis group, and for each joined table how many incoming paths from tables that hold the key hold a chosen place. You would see for MLST: 3 blocks, 4 plots; for the metadata: 13 blocks, 13 plots.
- Y-a. Your rule as an advice of the recipe check: a source table read by several tables is flagged (8 originals and the metadata on the demo).
- Y-r. Your rule as a refusal: the demo itself would stop loading until 8 originals and the metadata are split.
- Z. X and Y together.
- W1. The confirmation names every graph and result the step reaches; the log keeps the list.
- W2. After Apply, the app names the results that changed outside the plot you started from; you can remove the step.
- W3. A step is written only at a place whose whole reach was shown and confirmed.
- W4. Per-graph ticks: each table that reads a chosen parent is a line, all ticked; unticking one writes the step at the first places of the graphs you keep.
- W5. You tick results; the app proposes the highest places whose reach lies inside them.
- W6. The recipe check tells the author which tables several tables read and what lies below them.
- Neither: say what you meant.
(What each option prevents and does not prevent, what the author and the user see, whether it works in complex recipes and whether it can be done: the table in the section "The merged table of possibilities" below.)
**What the two agents think.** Both lean to X with W4 and W2, and to Y as an advice rather than a refusal: X and W2 cover a parent shared at every level (an original, the metadata, a joined table read by several plots); Y splits only originals and leaves steps inside one graph and the values of other entities. The recompute of Y is a fact of that option: each copy is ingested and its tier 1 is run again at the first opening; on the demo this cost nothing measurable, on real data it is not measured. Both agents say it is yours to decide. [D-0555, D-0556, D-0557, D-0545, D-0543]

### Q2 "Each T1 coming from the parent": which place?
**The situation.** You wrote: "if several parents are choosen the step applied must be applied in each T1 comming from the parent". On the demo the MLST table is read by three joined tables (`MLST_with_metadata`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`).
**Option 1: the parent's own first place** (`T1:MLST`). One step. The entity leaves the MLST table, `MLST_with_metadata` and its two plots, and `AR1_MLST_Serotype_Virulence` (exported). It stays in `ST22_Anchor` (7 rows, with MLST's columns empty) and so in both virulence plots (7 rows each). 10 tables change. For ResFinder the same reading changes 12 tables; the entity stays in `QA_AMR_per_sample` (1 row), `ST22_Anchor` (7) and `QA_fanout_exhibit` (23) with ResFinder's columns empty.
**Option 2: the first place of each table that reads the parent.** MLST: three steps at the three join places. The entity leaves the three joined tables and the four plots below them, and stays in the MLST table itself, which is exported (1 row). 9 tables change. For ResFinder: four join places and `T2:ResFinder` (read by `amr_heatmap`): 13 tables change; the entity leaves all of `QA_AMR_per_sample`, `ST22_Anchor`, `QA_fanout_exhibit` and stays in the ResFinder table. The two options differ in 5 tables for MLST (`T1:MLST`, `T1:ST22_Anchor`, `T2:ST22_Anchor`, `virulence_bar`, `virulence_variants`) and 11 nodes for ResFinder. Both are valid steps.
**Option 3: both are offered, you choose for each parent.** **Option 4: neither, say what you meant.**
**What the two agents think.** Sonnet: option 2 is the set of the join places that your default of D-0549 already names, and it removes the entity from the large joined tables; the parent's own table then keeps it until a later step at `T1:MLST`; as a lean, not a decision. Opus gives no lean on the two readings; its per-graph ticks (Q1, W4) build on option 2. [D-0555, D-0549, D-0547]

### Q3 How must the recipe be written so that the place is clear?
**The situation.** The graph and the rule of "at most one place on a path" are computed from today's recipe; no new key is needed. On the demo each data table meets the metadata in several joined tables, and one joined table is made from 6 originals. Your best practice: original, left join, metadata (the data is the left table); in 4 demo joins the metadata is the first table. A join reads original tables only (decided, D-0344: "revisit if needed").
**Options.** (a) Today's form; the app computes the join places per branch. (b) "One trunk": each data table joined with the metadata once, every other table of that history made from it; 7 demo tables would be rewritten (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_L50_integer`), `VirulenceFinder` has no such table, and it needs a join that reads a joined table, or derived tables; your case still needs places below the trunk [reopens D-0344]. (c) The recipe author names the default place of each original (a new key): you would see one more key in each recipe and the recipe check refusing a named place that is not in that original's tree (12 originals on the demo) [reopens D-0549]. (d) Neither: say what you meant.
**What the two agents think.** Both: the rule does not depend on this choice; as a lean, (a) with documentation of the practice (the metadata as the right table; one join per original read by all its plots) is enough to define the rule; (b) makes the default unique and does not make your quality case one choice. Your note on "T2a and T3a" (D-0517) needs the decision on derived tables only for results that are tables. [D-0344, D-0496, D-0517, D-0547, D-0549]

### Q4 Which place is the default where your rule says nothing?
**The situation.** Your rule: the default is where the original table and the metadata are joined; with no metadata join, "the first T1 of the lineage when no metadata join (so same level except there is no metadata joined)". On the demo some branches have no metadata join: `amr_heatmap` reads ResFinder itself; `qa_l50_integer` reads a table made from Quast alone; `QA_year_types` and `QA_aggregated_no_key` are made from the metadata alone; the Summary tables have no metadata. In ResFinder and Quast the same original has both kinds of branch. The first place of an original lies above every join place of that original, so by your rule of "at most one place on a path" the two together are not valid in one step.
**Options.**
- (a) The first place of the original (`T1:ResFinder`, `T1:Quast`). Valid alone: it then covers every path of that original. On the demo `T1:Quast` removes the entity from the quality plots too; the first place of every original except the metadata leaves the entity in 5 plots. For the two tables made from the metadata alone, (a) is `T1:metadata_schema`: it lies above every join with the metadata, so it cannot be chosen in one step with your default of D-0549, and it is the place you call "not advised" (D-0547).
- (b) The first place that only that branch reads: `T2:ResFinder` for `amr_heatmap`, `T1:QA_L50_integer`, `T1:QA_year_types`, `T1:QA_aggregated_no_key`. Valid together with the join places; the 19 defaults give the same 17 plot tables (entity in none).
- (c) No default ticked on these branches; you choose with the graph.
**Neither: say what you meant.**
**What the two agents think.** Both leave it to you. Sonnet leans to (b) as a named default where a branch has no metadata join, and none where unsure. Opus: "same level" read as the level of a joined table points to `T1:QA_L50_integer` (a table made from Quast alone, at the level of `Quast_with_metadata`); for `amr_heatmap` there is no table at that level, only ResFinder's own tier 2, so (b) is the nearest reading of your words there; a reading, not a lean. [D-0549, D-0550, D-0553, D-0547]

### Q5 What does "Remove from all the data" write?
**The situation.** Decided: tier 1 of every table that holds the key (27 places on the demo). Under your rule it holds nested pairs (35), so it is not one valid step.
**Options, from our runs (two entities; the valid form of (c): one entity).**
- (a) The 27 places in two steps: the first places, then the joined tables. 17 plots change, the entity in none. The exported tier 1 files lose the entity everywhere. [the two steps: reasoned, not run; the same places in one list: run]
- (b) The 11 first places that declare the key, one step. Same plots and the same exported files as (a).
- (c) The defaults, valid form (19 places with `T2:ResFinder`), one step. Same 17 plot tables, entity in none. The exported tier 1 files of 7 original tables (FastP, Quast, Bracken, ResFinder, MLST, VirulenceFinder, the metadata) keep the entity. With the nested form (`T1:ResFinder`) it is 6.
- The plot tables are identical in all forms; the difference is where the steps are written and what the export holds.
**Neither: say what you meant.**
**Reopens (information).** Your decided form, the tier 1 of every table that holds the key (D-0416), and your rule of at most one place on a path (D-0553) cannot both hold in ONE step: as one step the 27 places hold 35 pairs one below the other. (a) keeps the places of D-0416 and writes them as two steps; (b) and (c) change the places of D-0416.
**What the two agents think.** Neither agent chooses. (c) is the review session's reading and was not decided ("to be asked once when the plan is checked", ledger D-0550, not her words). [D-0416, D-0553, D-0549, D-0457]

### Q6 May the app say, before Apply, that the entity can remain in a place below?
**The situation.** "~" is not "changed". At `T1:ResFinder`, `qa_fanout_rows_per_sample` and its table lie below and stay identical although the entity is in them (23 rows, a count per sample); at `T1:FastP`, 3 plots lie below and 1 changes. Where the metadata is the first table of a left join, the entity's rows stay with the columns of the chosen table empty.

> **Correction of 2026-11-23 (ledger D-0563; see `CAUSE_AND_SOLUTIONS_ZEROS.md`):** the 23 are the entity's 23 virulence genes, which come from the VirulenceFinder table and which a step at the ResFinder table does not touch; the table counts the genes that are present, not rows. The two tables stay identical because the place chosen does not cover that path and because the join starts from the metadata; it is not a count of an empty row.
**Options.**
- (a) Nothing before Apply; after Apply, the list of results that changed and did not.
- (b) Before Apply, a plain note on a place below a chosen place through the side of a left join: "this table is built from <parent> as the side of a left join; the entity's rows may stay with that parent's columns empty".
- (c) Before Apply, structure only: for each joined table, through which parent it lies below, whether that parent is the first table or a side, and how many incoming paths from tables that hold the key hold a chosen place (after the first place of MLST: `MLST_with_metadata` 1 of 2, `ST22_Anchor` 1 of 5 and 1 path from a table without the key, `AR1_MLST_Serotype_Virulence` 1 of 3 and 1 without). No sentence about the entity.
- (d) (c) before Apply and (a) after.
**Neither: say what you meant.**
**What the two agents think.** Neither decides. For a note: your words "eg. left join keeps the rows of the second table - ensure you removed in second table if this is what you want (or something similar)" and "try to give as clear information as possible - so the user has elements it needs to be able to make a good decision". Against warnings: "I would just shows the differents where applied and no per table warnings about downstream effects"; "again after apply". "1 of 2" alone does not tell the entity's fate: with the first place of every original except the metadata chosen, `MLST_with_metadata` and `QA_AMR_per_sample` both show 1 of 2; the entity is gone from the first (the covered table is its first table) and stays in the second (the uncovered metadata is its first table). Sonnet leans to (d): the structure is information, the entity's fate belongs after Apply. Opus gives no lean; it shows what the structure and the runs say. [D-0477, D-0543, D-0501, D-0545, D-0546]

### Q7 The earlier questions on "Remove step", the side of the metadata and the entity key
- "Remove step" (one step or the whole decision): unchanged. One decision written at several places stays one event in the audit log (provisional). [D-0314, D-0315, D-0478]
- The side of the metadata (a rule, an advice or documentation): the runs add a fact. Where the metadata is the first table of a left join, a step at the data table leaves the entity's rows (`QA_AMR_per_sample` 1 row, `ST22_Anchor` 7, `QA_fanout_exhibit` 23). A rule "the metadata is the right table" would make the 4 demo joins with the metadata first be rewritten. [D-0547, D-0549, D-0550]
  > **Correction of 2026-11-23 (ledger D-0563; see `CAUSE_AND_SOLUTIONS_ZEROS.md`):** the 23 are the entity's 23 virulence genes, which come from the VirulenceFinder table and which a step at the ResFinder table does not touch; the table counts the genes that are present, not rows. The two tables stay identical because the place chosen does not cover that path and because the join starts from the metadata; it is not a count of an empty row.
- The entity key declared: unchanged; the engine confirms that every table but `APEC_STEC_virulence_genes` holds `sample_id` and refuses a removal step where the column is absent. [D-0313, D-0511]

---

## THE AGREED POINTS, with their basis

Tags: [HER WORDS D-n] / [RECIPE FILE] / [GRAPH SCRIPT, both] / [ENGINE RUN, which] / [CODE READ] / [REASONED, not run]. "Sonnet" and "Opus" name the agent whose run it is; "both" means two independent scripts.

**G1 The graph.** The nodes are the original data files (the roots), the tier 1 and the tier 2 of every table, and the plots (the leaves); an edge shows what goes into the next node; the tier 1 of a joined table has several parents. A place, where a step can be written, is the tier 1 of a table, the tier 2 of a table that a plot reads, or the tier 3 of a plot: 58 places on the demo (85 nodes with the 12 files and the tier 2 of every table: 12 + 28 + 28 + 17). [HER WORDS D-0553: "its more a directional graph with Tx at nodes and branches gives the directions"; "Results (final tables and plots) are leaves no ?"] [GRAPH SCRIPT, both]

**G2 The edges are the ones the engine runs.** A join reads the tier 1 of each of its ingredients (the first is the base); a table's tier 2 follows its tier 1; a plot reads the tier 2 of its target. [RECIPE FILE; CODE READ `orchestrator.py:269-283`] [ENGINE RUN: in 10 places (Sonnet 7, Opus 3) every node the engine changed lay inside the nodes below the place]

**G3 The demo.** 12 original tables, 16 joined tables, 17 plots, 85 nodes, 12 joined nodes with several parents (`ST22_Anchor` 6 parents, `QC_Reads_Anchor` 4, `AR1_MLST_Serotype_Virulence` 4, `QA_fanout_exhibit` 3, eight with 2); the metadata is read by 13 tables (the first table in `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; the only one in `QA_year_types` and `QA_aggregated_no_key`; a later one in 7); 6 tables have no plot below them (`Quality_metrics`, `Detailed_summary`, `FastP_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `AR1_MLST_Serotype_Virulence`). The earlier "17 joined or derived tables" is corrected to 16. [GRAPH SCRIPT, both]

**G4 What lies below one original table is a tree** in each of the 50 shipped recipes that load, and no join reads a join [GRAPH SCRIPT, both]. It stays so while a join reads original tables only (D-0344) [REASONED, not run]; with derived tables, which are not in today's format, it must be checked again. [HER WORDS D-0550: "each independent history is like an independent tree graph"]

**G5 Independence and the valid set.** Two places are independent when neither lies below the other; a set of chosen places is valid in one step when its places are pairwise independent; that is the same as "at most one chosen place on any path". [HER WORDS D-0553: "the user chooses at most one place =node ... then all paths are derived (~) and cannot be choosen. yes R2 rule"] [GRAPH SCRIPT, both; the equivalence REASONED]

**G6 The exception of the original parents follows from G5.** The first places of the original tables have only their files above them, so none lies below another and the set of all of them is valid (11 places that declare the key; `APEC_STEC_virulence_genes` declares none). [HER WORDS D-0553: "(with the exception of the original parents where all can be choosed)"; D-0547: "The only exception is if the user wants to one or several eg all FIRST T1"] [GRAPH SCRIPT, both]

**G7 Derived.** A place is derived when it lies below a chosen place; it is shown with "~" and cannot be chosen in the same step; a later step may choose it ("he must add another step audit step later - choosing a different scope"). [HER WORDS D-0547, D-0553]

**G8 "~" means "below", not "changed" and not "gone".** At `T1:ResFinder`: 14 tables below, 12 changed; the entity's rows stay in `QA_AMR_per_sample` (1 row), `ST22_Anchor` (7) and `QA_fanout_exhibit` (23) with ResFinder's columns emptied, because the metadata is the first table of those left joins; `T2:QA_fanout_exhibit` and the plot `qa_fanout_rows_per_sample` stay identical (a count per sample stays 23); at `T1:MLST` the entity's rows leave `AR1_MLST_Serotype_Virulence` (MLST is its first table) and stay in `ST22_Anchor` (7). At `T1:FastP` 3 plots lie below and 1 changes. [ENGINE RUN: ResFinder and MLST: Opus R5, R12 and Sonnet C, RD1, RD2; the `T1:FastP` instance: Sonnet RD2 only, its reason (the FastP columns are not among the final columns of `ST22_Anchor`) REASONED, not run] [HER WORDS D-0545: the effect is known after Apply]

> **Correction of 2026-11-23 (ledger D-0563; see `CAUSE_AND_SOLUTIONS_ZEROS.md`):** the 23 are the entity's 23 virulence genes, which come from the VirulenceFinder table and which a step at the ResFinder table does not touch; the table counts the genes that are present, not rows. The two tables stay identical because the place chosen does not cover that path and because the join starts from the metadata; it is not a count of an empty row.

**G9 Sets on the demo (valid in one step or not).** The 11 first places: valid. The 27 places of "Remove from all the data" as decided: not valid (35 nested pairs: from `T1:metadata_schema` 13, `T1:Quast` 4, `T1:ResFinder` 4, `T1:FastP` 3, `T1:MLST` 3, `T1:VirulenceFinder` 3, `T1:Bracken` 2, `T1:Summary_quality` 2, `T1:Summary` 1); they can be written in 2 steps (the first places, then the joined tables) [REASONED, not run: the joined tables never lie below one another, since a join reads original tables only; the audit copy is the same as the one-list copy of Sonnet D4 and Opus R7, so the tables are the same]. The 19 defaults with `T1:ResFinder`: not valid (4 pairs); with `T2:ResFinder`: valid. Her case with `T1:ResFinder`: not valid; with `T2:ResFinder`: valid (17 places). `T1:MLST` with its three join places: not valid; the three join places: valid. `T1:ResFinder` with `T1:QA_AMR_per_sample`: not valid; `T1:ResFinder` with `T1:metadata_schema`: valid; `T2:ResFinder` with `T1:QA_AMR_per_sample`: valid. [GRAPH SCRIPT, both: every row equal]

**G10 How she removes the row that comes from the metadata side** (in `QA_AMR_per_sample` the metadata is the first table): choose `T1:QA_AMR_per_sample` instead of `T1:ResFinder` for that branch; or choose `T1:ResFinder` and `T1:metadata_schema` (two first places; the metadata place is "not advised", D-0547); or keep `T1:ResFinder` and add a second step later at `T1:QA_AMR_per_sample`. All valid. [HER WORDS D-0547; GRAPH SCRIPT, both] [ENGINE RUN: the valid defaults with `T1:QA_AMR_per_sample` and `T2:ResFinder`: Sonnet D2 only; the nested defaults with `T1:ResFinder`: Opus R7; both leave the entity in no plot]

**G11 Her case, nothing nested, rebuilt from scratch.** 17 places (9 joined tables with the metadata, 2 tables made from the metadata alone, the 4 originals with no metadata join, `T2:ResFinder`, `T1:QA_L50_integer`): 14 plots change; the entity stays in exactly `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`; the plot tables equal those of the nested form with `T1:ResFinder`. [ENGINE RUN: Sonnet D1 (1 entity); Opus R8 (2 entities)] [HER WORDS D-0549: "remove the samples from all analyses BUT the ones that show the bad quality"]

**G12 The three forms of "Remove from all the data" give the same 17 plot tables**, 17 changed, the entity in none; the list of 27 places that the engine's tier 1 tables give (every table but `APEC_STEC_virulence_genes`, which has no `sample_id`) equals the old list. [ENGINE RUN: Opus R7, two entities, the nested defaults; Sonnet D2, D4, E, one entity, the valid defaults]

**G13 What the exported tier 1 files hold.** The 11 first places and the 27 places leave the entity in no original table; the nested defaults (19 with `T1:ResFinder`) leave it in 6 (FastP, Quast, Bracken, MLST, VirulenceFinder, metadata); the valid defaults (19 with `T2:ResFinder`) leave it in 7 (also ResFinder): two different sets, both right. The export writes these files (D-0457). [ENGINE RUN: Opus R11; Sonnet T1X]

**G14 The set of the first T1 of every original except the metadata** removes the entity from 11 of the 16 plots that hold it: the 4 whose every incoming root path holds a chosen place, and 7 of the 12 that have a path without one; it stays in 5 (`qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `qa_population_zscore`, `qa_year_label`, `qa_facet_by_mapping`), where the metadata is the first table of the join or the only one. The 17th plot, `qa_aggregated_no_key`, has no key column. [ENGINE RUN: Sonnet D3 only] [HER WORDS D-0549: "The metadata should be the right table -- best practice"]

**G15 Two chosen places, one below the other: the upper decides a calculation that lies between them.** On a small recipe (values 10, 20, 30, 40; a mean over all rows between the places): the upper place alone gives mean 30, the lower alone 25, both 30 (the upper's table). On the demo: a step before the z-score changes the `n50_zscore` of 41 of 41 other entities (largest 0.064), a step after it 0 of 41; one count in a table with no key changes. The lower place can still remove a row that came from another table of a join (set E against the valid defaults, G13 and G14). [ENGINE RUN: Opus R9, R13 (before: also Sonnet Z); Sonnet Z (after)] [HER WORDS D-0501: "things cannot be the same because we changed earlier in the recipe"]

**G16 The two readings of "each T1 coming from the parent" give different tables.** MLST: a step at `T1:MLST` changes 10 tables and leaves the entity's 7 rows in `ST22_Anchor` and both virulence plots with MLST's columns empty; steps at the three join places change 9 tables and remove those rows, and `T1:MLST` keeps the entity; 5 tables differ (`T1:MLST`, `T1:ST22_Anchor`, `T2:ST22_Anchor`, `virulence_bar`, `virulence_variants`). ResFinder: 12 tables change under `T1:ResFinder`, 13 under the four join places and `T2:ResFinder`; the entity leaves `QA_AMR_per_sample`, `ST22_Anchor`, `QA_fanout_exhibit` only under the second; 11 nodes differ. [ENGINE RUN: MLST: Opus R12 only; ResFinder: Sonnet RD1 only] (Sonnet's 13 and 14 also count `T2:ResFinder_with_metadata`, a tier 2 with no steps that no plot reads; the 11 nodes that differ are the same in both ways of counting: `paths2/RD.out`.) [HER WORDS D-0555]

**G17 The graphs that go from the same parent** are one per reading table (the joined tables that list the parent as an ingredient, and the parent's own tier 2 when a plot reads it): that table and everything below it; today they never meet below (a join reads original tables only). Two results share only the metadata when it is the only original above both (45 of the 97 pairs of results in different analysis groups; 17 pairs share another original; 35 share none). Six parents feed results in more than one group: `Summary_quality`, `FastP`, `Quast`, `ResFinder`, `VirulenceFinder`, `metadata_schema`. From one plot, the other plots below its originals: `mlst_bar` 12, `amr_heatmap` 4, `qc_reads_horizontal_barplot` 13. [GRAPH SCRIPT, both: Sonnet; Opus R1, R14] [HER WORDS D-0555: "so we need here to have the 2 directed graphs that go from the same parents - because both will be affected"]

**G18 A joined table read by several plots is a shared node too** (`ST22_Anchor`, `MLST_with_metadata`, `Quast_with_metadata`: its two plots are in two groups; `QA_year_types`): the gotcha is not only at the original parents. [GRAPH SCRIPT, both]

**G19 Two source tables on one file stay separate.** `Summary` and `Summary_quality` read one file: a step at `T1:Summary` changes 1 plot, at `T1:Summary_quality` 2, at both 2. [ENGINE RUN: Sonnet B only]

**G20 Her reimport rule applied to MLST** (three source tables on one file, each read by one table): 17 of 17 plot tables equal the original's (rebuilt), the T1 of the new tables equals `T1:MLST`, a step at `T1:MLST` changes 5 tables instead of 10; the author wrote 2 new schema entries (10 lines each, the same includes), changed 2 ingredient lines and 1 `right_ingredient`; the whole rebuild took about 1 s either way (demo data). What it does not split: a joined table read by several plots; a joined table of several originals; a calculation over all entities; the metadata unless it is copied (13 tables read it). In a deployment that finds files by table name each copy needs its own file named by its table id. [ENGINE RUN: Opus R6; Sonnet RI; CODE READ `orchestrator.py:173-190`, `data_import_check.py:83, 177-178`] [HER WORDS D-0556]

**G21 What can go wrong when a parent or a shared node feeds several graphs** (E1 to E10): results change outside the graph the user started from; the user does not see them; the metadata is a parent of 13 tables and 13 of 17 plots in 4 groups; one step does different things in different graphs (first table of a left join: rows leave; side: rows stay, columns empty); the values of other entities change where a calculation over all entities lies below; two chosen places in one step (the upper decides); two tables on one file are separate; the two readings of D-0555 differ; the same plots can leave different exported tables; tables no plot reads receive the step too. [ENGINE RUN and GRAPH SCRIPT as in G8, G13, G15, G16, G19; the first two items REASONED]

**G22 Everything below a change is recalculated (D-0560): what the engine does today.** A table's tier 1 key holds the engine, the definition of the table and of every table above it, the content of the data files, and the audit steps of the table and of everything above it; the tier 2 key is the tier 1 key plus its own steps; a plot's key is the tier 2 key of its target plus its own steps. [CODE READ `cache_keys.py:14-28`] For the 55 writable places of the demo that the engine accepts (T1 of 28 tables, T2 of the 13 tables a plot reads, T3 of 17 plots; the engine refuses a removal where the column `sample_id` is absent: `T1:APEC_STEC_virulence_genes`, `T2:QA_aggregated_no_key`, `T3:qa_aggregated_no_key`): no node below the place kept its key, no node whose content changed kept its key, no key changed outside the nodes below. `run_audit`'s skip of a plot with an unchanged key gave the same plot tables as a from-scratch build (`T1:MLST`: 0 of 17 differ; the plots it calls affected are exactly the plots that differ). The edges the keys follow equal my parse on 50 of 50 recipes. [ENGINE RUN: the 55 places, keys and content: Sonnet RD2 only; the skip of `run_audit`: Sonnet R0 only; the edges of the keys equal Opus's parse on 50 recipes: Opus R3; the content changes inside "below" at 3 places: Opus R5] This is shown for one entity on the demo, not for every recipe.

**G23 A wrong stored table is served exactly when its footer key equals the current key.** A wrong table with the old key (the original's table, or one row removed) at the audited table's name is refused (`read_anchor_if_key`) and rebuilt, by a normal build and by `run_audit`; a wrong table stamped with the new key is served by both. So a stale table can be served only if a key fails to change when it should, or if a table is written with a key that is not its own. [ENGINE RUN: Sonnet R2 only; CODE READ `transformer/anchor.py:109-118`]

**G24 The requirement of D-0560, as proposed text.** After a change at a place, every place below it is computed again from its parents. A stored table is read only under its full key, and the key of every place below the change differs from its key before the change, because it is built from the keys of all its parents (definitions, data and audit steps). [HER WORDS D-0560: "we need to ensure that everystep after a change in a place is recalculated - that would otherwise produce errors indeed"] [CODE READ; ENGINE RUN G22, G23] The tests that prove it are in the section "The requirement and its tests".

**G25 What the app can show before Apply, and what only after.** Before Apply, structure only: the graph; each place's table and tier; its kind (original, joined, plot); its parents with the base marked and the join kind; its state (chosen, "~", free); for each chosen place the results below it by analysis group, with the results outside the plot the user started from marked, and the tables no plot reads (they are exported); for a joined node, through which parent it is below. After Apply: which results changed, the entity's rows, the values of other entities. [HER WORDS D-0545: "you cannot see effect if you do not recalculate"; D-0546: "again after apply"; D-0457] [GRAPH SCRIPT]

**G26 Facts of the demo that make the rule harder (facts only; the demo is not changed by agents).** The metadata is the first table of 4 joined tables with analyses; originals are read by several joined tables; one joined table has 6 originals and two have 4; a plot reads an original's own tier 2 next to that original's joins (`amr_heatmap`); two tables read one file; 6 tables have no plot below them. What an author can write today within today's format: the metadata as the right table of every join; one join of an original with the metadata read by all the plots of that original (several plots can target one join, as `mlst_bar` and `year_distribution` do); a second source table on the same file for a second use (G20). [RECIPE FILE `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`; HER WORDS D-0547: "T1 original -> left_join -> metadata"; D-0549]

**G27 Coverage per incoming path.** For a joined node: "incoming paths from tables that hold the key with a chosen place: k of n", the uncovered tables named, and the paths from tables without the key counted apart (no removal by key can be written there: the engine refuses it). After `T1:MLST`: `MLST_with_metadata` 1 of 2; `ST22_Anchor` 1 of 5 (and 1 table without the key); `AR1_MLST_Serotype_Virulence` 1 of 3 (and 1 without). After the 11 first places every joined table shows n of n (and `ST22_Anchor`, `AR1_MLST_Serotype_Virulence` keep one path from a table without the key). It is structure, not a statement about the entity: k < n is necessary for the entity to remain below a removal, not sufficient (set E: the entity stayed in 5 plots, all among the 12 plots that hold the entity and have a path without a chosen place; 7 of those 12 lost it). [GRAPH SCRIPT (Sonnet CK; Opus R14); ENGINE RUN Sonnet D3; REASONED: a row reaches a table only through an incoming path]

---

## THE RECHECK OF THE FIRST SIGNED LIST (so that the note at the top of `DESIGN_AGREED_AND_QUESTIONS.md` can be closed)

Statuses: STANDS (her words, recipe keys or checker code: no old lineage code); CONFIRMED (by which run); VOID (rested on the old lineage code or on a reading she replaced); UNVERIFIED.

| Point of the first list | Status | Basis |
|---|---|---|
| G1 place (and an empty tier 2) | STANDS | her words D-0541, D-0346; the empty tier 2 now rests on the engine and the step writer (`recipe_tiers.py:196-210`, `audit_copy.py:177-179`, Opus R5 at `T2:ResFinder`), not on the walk |
| G2 original table | STANDS | recipe keys |
| G3 history is a tree | CONFIRMED | own parses; 50 of 50 recipes (both) |
| G4 derived | CONFIRMED | computed "below" matches the engine in 10 places (Sonnet A, Opus R5) |
| G5 shared place (6, 4, 4) | CONFIRMED | own parses |
| G6 join with the metadata, ST05 | STANDS | checker code |
| G7 default place | STANDS | her words D-0549, D-0550 |
| G8 no nesting in one step | STANDS | her words D-0553; now computed (G5, G9 above) |
| G9 effect after Apply | STANDS | her words D-0545, D-0546 |
| G10 two functions; "the column's fate from the walk" | VOID as a design source | D-0558; the walk is not used |
| G11 "~" is not "gone" | CONFIRMED | G8 above |
| G12 no new recipe key | STANDS | recipe keys |
| G13 results | STANDS | her words D-0485, D-0487 |
| G14 shared tiers today | CONFIRMED | own parses |
| G15 the first place only one branch reads (`T2:ResFinder`) | CONFIRMED | own parses; runs R2 / D1 |
| G16 a branch that never meets the metadata | CONFIRMED | graph (G9) and set E (G14 above) |
| G17 the first T1 of an original | CONFIRMED in part | `T1:Quast` changes 5 plots in 3 groups (Sonnet C); the emptied columns of `qc_reads_horizontal_barplot` not rechecked |
| G18 metadata-alone tables | CONFIRMED | recipe keys, own parses |
| G19 one place per multi-ingredient join; join places per original | CONFIRMED | own parses (FastP 3, Quast 3 and `QA_L50_integer`, MLST 3, ResFinder 4) |
| G20 a look-up table without the key | STANDS in substance | it declares no key; its tier 1 has no `sample_id` (Opus R7, Sonnet E); the engine refuses a removal there (Sonnet RD2); "offered" described the old code |
| G21 a later step | STANDS | her words D-0547 |
| G22 the tree view | STANDS | her words D-0547, D-0550 |
| G23 several steps of one decision | STANDS (provisional) | code reading |
| G24 retest facts | CONFIRMED in part | MLST: 4 plots, 1 group (Sonnet C); `T1:Quast`: 5 plots, 3 groups; z-score 41 of 41 (Sonnet Z; Opus R13); the count 19 to 18: one count changes (Opus R13), its values not reread; the emptied columns under `T1:Quast`: not rechecked |
| G25 what is on screen today; the 27 places | STANDS; the 27 CONFIRMED | grep of `app/`; the engine's tier 1 tables (Opus R7, Sonnet E) |
| G26 three forms of "remove from all" | CONFIRMED | rebuilt, two entities (G12 above) |
| G27 nested pair | CONFIRMED | arithmetic and hand-written small recipe (Opus R9); the demo claim: `T2:ResFinder` equals `T1:ResFinder` (Opus R8, Sonnet D1) |
| G28 the fold of an empty tier 2 | VOID | it describes the old walk |
| G29 "7 tables rewritten under one trunk" | CONFIRMED by one parse (Sonnet); not redone by Opus | G3's tables |
| G30 a declared default | STANDS | her words D-0500, D-0549 (as an option) |
| G31 smallest number of steps (5, 11) | VOID | it rests on "one place per tree", which D-0553 replaced |
| Q1 numbers | the 5 and 11 steps VOID; "14 changed, stays in 3, 17 plot tables equal" CONFIRMED | |
| Q2 numbers | CONFIRMED | `T1:Quast` hits the quality plots; 17 places and nothing nested |
| Q3 numbers | CONFIRMED | 7 tables; 12 originals; the join count by own parses |
| Q4 numbers | CONFIRMED | 27 places, 35 pairs, 11 and 19 places; the exported tables |
| Q5 sentence "certain only at a join on the entity key" | VOID | it rested on the walk; replaced by G8 and G27 |
| Q6 | STANDS | |
| Q7 numbers (metadata first in 4 joins, right in 7, alone in 2) | CONFIRMED | own parses |
| Q8 | STANDS; the key fact CONFIRMED | only `APEC_STEC_virulence_genes` has no `sample_id` in tier 1 (Opus R7, Sonnet E) |
| The answer to Q1 of that file | REPLACED by her answer | D-0553: at most one place on a path; the original parents may all be chosen |

---

## THE MERGED TABLE OF POSSIBILITIES FOR A PARENT REUSED IN ANOTHER GRAPH

| # | Possibility | What it prevents | What it does not | The author sees | The user of the audit sees | In complex recipes (six originals; a parent in several joins; the metadata first; a table computing over all entities) | Can it be done (basis) |
|---|---|---|---|---|---|---|---|
| X | Before Apply, show every graph that goes from each chosen place (results by group, and for each joined table the coverage of G27) | surprise from results she did not open | the choice stays hers (D-0543, D-0544); the effect is known after Apply | nothing new | a block per reading table: MLST 3 blocks, 4 plots; metadata 13 blocks, 13 plots | works; the list grows with the recipe | yes [GRAPH SCRIPT, both] |
| Y-a | Her rule as an advice of the recipe check | the reuse at the original level, where the author follows it | a joined table read by several plots; the metadata unless copied; steps inside one graph; values of other entities | an advice per shared original (8 originals and the metadata on the demo) | smaller graphs after the author's change | works for originals; does not split `ST22_Anchor` | yes for the recipe and the engine [ENGINE RUN Opus R6, Sonnet RI]; a deployment that finds files by table name needs one file per name [CODE READ] |
| Y-r | Her rule as a refusal | as Y-a, forced | as Y-a; the demo stops loading until split | a refusal with the tables to split | as Y-a | as Y-a | partly (same) |
| Z | X and Y | both | as X | as Y | as X plus advice | as X and Y | partly |
| W1 | The confirmation names every graph and result it reaches; the log keeps the list | writing without reading | a wrong confirmation (D-0543) | nothing | one list to confirm | works | yes [GRAPH SCRIPT] |
| W2 | After Apply, a check names the results changed outside the plot she started from; she can remove the step (D-0545) | an unnoticed change | the change before she sees it | nothing | "also changed: ..." | works | yes: a rebuild and a comparison per table is what every run here did [ENGINE RUN, both] |
| W3 | A step is written only at a place whose whole reach was shown and confirmed | writing without having seen | the choice | nothing | a gate on W1 | works | yes [REASONED] |
| W4 | Per-graph ticks: each reading table of a chosen parent is a line, all ticked; unticking one writes the step at the first places of the graphs she keeps | a graph she does not want reached | the two readings differ (G16); other entities' values | nothing | ticks per reading table | works while the graphs from one parent never meet below (true today, G17) | yes [ENGINE RUN Opus R12, Sonnet RD1] |
| W5 | She ticks results; the app proposes the highest places whose reach lies inside them | reach beyond the results she chose | other entities' values | nothing | ticks on results; places proposed | works | computable; reopens D-0022 ("only automatic placement 'remove from all tables'") and touches D-0531 (the app cannot decide the scope): information |
| W6 | The recipe check tells the author which tables several tables read and what lies below | an author's surprise | the user's choice | a list per shared table | nothing | works | yes [GRAPH SCRIPT] |

---

## THE REQUIREMENT AND ITS TESTS (D-0560)

**Requirement.** After a change at a place, every place below it is computed again from its parents; a stored table is read only under its full key, and the key of every place below the change differs from its key before the change. [HER WORDS D-0560]
**The three tests the product must have, each able to fail.**
1. For EVERY place of a recipe (not five), write an audit step, rebuild from scratch in empty folders, and assert: every node below the place has a changed key; every node whose content changed has a changed key; no key changes outside "below", with "below" computed from the recipe's own keys. The test must fail when a part of the key is left out (for example the audit part).
2. A stale probe: store, under the audited key's file name, a table built before the step and stamped with the old key; the audit must equal the from-scratch table; the same test must fail when the key is not changed for a place below.
3. The skip of a plot whose key did not change gives the same plot tables as building every plot from scratch.
**Conditions of every test.** Recipes in the tests have a join of several originals, a table read by joins and by a plot, a plot with its own tier 3, and a calculation over all entities. An equality ("0 of n differ") counts as evidence only when both sides were rebuilt in separate empty folders; the test says so. [REASONED; the demo evidence is G22, G23]

---

## FACTS STILL TO RUN (each with its three points)

| Run | (1) Requirement or hypothesis | (2) Expected | (3) Independence |
|---|---|---|---|
| Reading (ii) of D-0555 for Quast and the metadata | D-0555 | under the first places of the reading tables, the entity leaves all the joined tables and stays in the parent's own tier 1; under the parent's own first place, it stays in the joined tables where the parent is a side | engine from scratch, `add_step` for filters |
| The same intention at the three join places and at `T1:MLST` | D-0555, D-0547 | as G16 | as above |
| The two steps of "Remove from all the data" (a) in Q5 (first places, then joined tables) | D-0416 and D-0553 | the same 17 plot tables as the one-list form | engine from scratch |
| The tests of the requirement as general tests over every place of every recipe | D-0560 | as the three tests above | the recipe's own keys; the engine |
| The value of the `QA_aggregated_no_key` count; the emptied columns of `qc_reads_horizontal_barplot` under `T1:Quast` | D-0501 (other entities' values; "the 0") | one count changes; Quast columns empty | engine from scratch |
| Timing on real data | D-0556 ("can cost a bit of recompute") | longer than the 1 s of the demo; not known | not measured |

---

## OPEN BETWEEN THE TWO AGENTS

None. The one difference of number in G14 (11 plots, not 12) was confirmed by Opus: the plot `qa_aggregated_no_key` never held the entity.

Signed by both agents: Sonnet (this file) and Opus (OPUS_signs_paths_v1.md and OPUS_signs_paths_v2.md; all replacements applied; C7 with the number 11, confirmed by Opus)
