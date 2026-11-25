# OPUS position on paths, version 2 (restarted after the owner's stop, M612)

Written by the Opus design agent, blind (the Sonnet file of this topic is not read). Replaces `OPUS_paths_1.md`, which holds only the stop line: nothing else had been written in it when the stop came.

**Tags.** Every statement carries one: [HER WORDS D-n] / [RECIPE FILE path:line] / [MY GRAPH SCRIPT] / [ENGINE RUN script, output] / [REASONED, not run] / [UNVERIFIED: passed through old lineage code]. I add one tag, [CODE READ file:line], for a fact read in the code of the repository (a reading, not a run). Paths of library code are relative to the worktree `SPARMVET_VIZ_wt_goals` (commit `0744cafb`); scripts and outputs are in `tmpAI/coordinator/design_dialogue/` of the main tree.

---

## 0. WHAT I HAD USED BEFORE THE STOP

### 0.1 Library functions, scripts and results, marked

| What | Used where (before the stop) | Mark | Why |
|---|---|---|---|
| `utils.lineage_walk` (`walk`, `Walk`, `Line`, `LineageIndex`, the fold `lineage_walk.py:394-395`, the reach `:407-417`, `Hop.join_side`) and `utils.lineage_records` (`Reach`, notes, codes) | Not called by my scripts. Cited in P7, P19, S1, S4, S16, G1, G10, G25, G28, X2, X4. Reached indirectly through `remove_from_all` (next row). | OLD LINEAGE CODE | By definition (M611, M612). |
| `utils.remove_from_all.describe` (the 27 places, the key column per place) and `apply` | `opus_runs.py:47` (the 27 places), `:121` (ALL27, UPPER, A3, B3 written by `apply`); the whole retest (`RETEST_her_scope.md:7`); `opus_paths_map.py:103-104` (ALL27 read from the retest's results) | OLD LINEAGE CODE | `describe` builds the list from the walk (`remove_from_all.py:71`, `:195-210`); `apply` writes `removal_step(place.column, ...)` with the walk's column at each place (`remove_from_all.py:308-344`, `KeyPlace` `:101-113`) [CODE READ]. |
| `remove_from_all.removal_step` | `opus_runs.py:106` (R2) | INDEPENDENT as a value | It only returns the dict `{modif_filter, not_in, [values], na: keep}` (`remove_from_all.py:277-280`); no walk is called [CODE READ]. |
| `app.modules.plan_composer.compose_plan_book` | `opus_runs.py` (the `plans` handed to `describe`, `apply`, `add_step`, `loaded_from_resolved`) | NOT SURE | It is the engine's own plan after each step, composed over `recipe_graph`'s nodes (`plan_composer.py:342-356`), and it is the input the walk reads (`plan_composer.py:5`). For a filter step it changes nothing: `add_step` asks the key rule only for a drop (`audit_copy.py:204-209`) [CODE READ]. |
| `utils.recipe_graph` (`build_graph`, `lineage_forward`, `lineage_back`, `parents`, `plots`, `plot_target`) | All of `opus_paths_map.py`; `opus_runs.py:45`; the retest's map (`RETEST_her_scope.md:32`); Sonnet's tree-property script; points P1-P3, P5, P10, P14, S3, S6, S14, J1-J3, A3, A15, G3, G15 and DESIGN G3-G6, G14-G16, G18, G29, G31 | NOT SURE | For: it imports no walk module (`recipe_graph.py:70-75`); its nodes and edges are read straight from the recipe keys: the blocks of schemas, `ingredients[].dataset_id` in order (base first), `target_dataset` (`recipe_graph.py:576-589`, `594-601`, `648-663`, `676-707`); it has no fold, no places, no reach [CODE READ]. Against: it is the model the walk was built on (its header names `home_stage2_mechanism_spec.md` section 2, `recipe_graph.py:10`), it carries the builder's provisional choices (`:45-53`), and the cache keys read it (`cache_keys.py:73`). From now on it is used only as a labelled cross-check of my own parse (section 1.3). |
| `utils.audit_copy.start_audit`, `add_step` (for a filter step) | `opus_runs.py:108` (R2); `opus_b1_run.py:52`; inside `apply` | INDEPENDENT (for a filter) | It parses the place text, finds the tier, refuses an action that is not allowed and a tier 2 that no plot reads, and appends the step to `audit_steps` (`audit_copy.py:166-189`, `212-233`). The key rule (`key_drop`, which uses `LineageIndex`) is asked only for a drop (`:204-209`) [CODE READ]. Validated against a hand-written step in section 1.4. |
| `utils.recipe_tiers.step_list` | Inside the engine and `recipe_graph` | INDEPENDENT | The author's `steps`, then `audit_steps` (`recipe_tiers.py:65-69`) [CODE READ]. |
| `app.modules.audit_run.run_audit` | `opus_runs.py:55`; `opus_b1_run.py:53` (J's table read from its stored file); the retest | NOT SURE | It builds with the engine, but it skips a plot whose cache key did not change (`audit_run.py:262-264`) and reuses a stored table whose key matches. The keys read `recipe_graph` (`cache_keys.py:73`). A key that missed an upstream change would give "unchanged" with no build [CODE READ, REASONED]. Not used from now on. |
| `DataOrchestrator.materialize_tier1/2/3` | All runs | INDEPENDENT of the walk, with one caveat | No walk module is imported (`orchestrator.py:14-20`). A join's T1 is built from each listed ingredient read from its file and run through its tier 1 (`prepare_ingredient`, `orchestrator.py:269-283`; the base is the first declared ingredient). Caveat: a stored table is reused when its key matches (`read_anchor_if_key`). In `opus_runs.py:60-64` I read a plot's table from the ORIGINAL's stored tables when the target's T1 key had not changed. From now on every variant is built in its own empty folder [CODE READ]. |
| `app.modules.cache_keys` (`load_data_analysis_recipe`, `loaded_from_resolved`, `compute_data_analysis_recipe_keys`) | All runs | Engine; INDEPENDENT of the walk; reads `recipe_graph` for the parts of a key | Needed to call the engine; with one empty folder per variant, a key only names a file [CODE READ]. |
| `app.tests.test_table_keys.Staged` | `opus_b1_run.py` (the staged world) | INDEPENDENT | A test helper that writes a recipe and its data. |
| My `opus_paths_map.py` and its output | The stopped paths position | Mixed | Its graph facts rest on `recipe_graph` (NOT SURE); its "places: 52" applies the walk's fold rule, which I copied from `lineage_walk.py:394-395` (OLD); every set judged against "the 27 offered places" uses `describe`'s list (OLD). The key flag of a root was read from `input_fields` / `is_entity_key` in the recipe body (independent). Superseded by section 1. |

### 0.2 My earlier conclusions, point by point

"Wrong because of it": could the conclusion be wrong because it passed through old lineage code (yes / no / not known). Points not listed in a row rest only on her words, the recipe files or the checker's code: no.

| File | Points that rest on no old code (her words, recipe file, checker code, a reading) : wrong because of it = no |
|---|---|
| `OPUS_position_1.md` | P4, P6, P8, P9, P15, P16 (with the option "S2" written inside it), P17, P18, P20, P25, P27, P28, P29, P30 |
| `OPUS_round_2.md` | S2, S5, S7, S8, S9, S11, S12, S13, S15, S19, J4, J5, J6, J8, A1, A2, A4-A9, A12, A13, A14, A17, A18, O2, O4, O6, O7 |
| `OPUS_signs_v1.md` | G2, G4-G9, G12-G14, G16, G18-G24, X3, Q2, Q3, Q5, Q6, Q7 |
| `OPUS_signs_v2.md` | R1-R5 (wordings; R2 is a code read, `audit_stack.py:531-533`), B2 (not run) |
| `DESIGN_AGREED_AND_QUESTIONS.md` | G2, G7, G8, G9, G12, G13, G21, G22, G23, G30 |

| Point | Rests on | Wrong because of it? | Recheck (section) |
|---|---|---|---|
| P1, S2 and A2 of round 2, G2 of signs v1, DESIGN G2 (original table = a schema block) | recipe file; the name `DS:` from `recipe_graph` | no | my parse (1.2) |
| P2, P5, S3, J1, J2, J3, A3, G3 of signs v1, DESIGN G3, G4 (history = the tree below an original; derived = below the chosen place; shared = in two trees) | `recipe_graph` edges | not known | my parse (1.2), engine (1.5) |
| J7, A10, DESIGN G10 ("the column's fate, from the walk and the engine's plan") | the walk | not known; as a design source it is void under D-0558 | outside this topic: the column's fate needs its own independent source |
| P3, S14, J5, DESIGN G14 (a join reads its ingredients' T1) | `recipe_graph:15-16`; the engine's own text `orchestrator.py:269-283` | no for the engine text; not known for the graph | engine (1.5) |
| P7, S16, DESIGN G6 (the side of the metadata in a join; a step at the non-base side keeps the base's rows) | recipe file (first ingredient, `right_ingredient`); `lineage_walk.py:203`, `Hop.join_side` | no for the sides (recipe file); not known for the effect | my parse (1.2), engine row check (1.5) |
| P10, P14, S6, A15, G15, DESIGN G5, G15, G16, G18 (who shares with whom; which branches meet the metadata; ResFinder in 4 joins; tables of the metadata alone) | `recipe_graph` (my map, the retest's map) | not known | my parse (1.2) |
| P11, P12, P13, O1 (readings of her unit, with B3 / R2) | her words; B3, R2 runs | no for the readings; the run numbers inside are UNVERIFIED | section 10 |
| P19, G25, X2, DESIGN G25, G28, S1, S4, G1 of signs v1, DESIGN G1 (what the walk does today; the fold) | describe the old code | no as descriptions (they say what the code does); every proposal to keep a part of the walk is void under D-0558; G1's engine facts (a T2 with no steps is T1; a T2 no plot reads runs nowhere) stand on `recipe_tiers.py:196-210` and `audit_copy.py:177-179` | engine (1.5: a step at `T2:ResFinder`) |
| P21, S18, O5, G26, DESIGN G26, Q1, Q4, Q8, the run table of `OPUS_signs_v1.md` (the three forms of "remove from all": ALL27 = UPPER = A3, the entity in no plot) | `describe` (the 27 places); `apply` (the column per place); reads of stored tables by key (`opus_runs.py:60-64`) | not known: equal plot tables are exactly what a stale stored table would also give | section 10 (independent lists, fresh builds) |
| X1 of signs v1 (R2 gives the same 17 plot tables as B3) | `apply` for B3; `add_step` for R2; reads by key | not known | section 10 |
| P22, P23, P24, P26, S10, S17, S20, A11, A16, G11, G17, DESIGN G11, G17, G19, G24 (facts of the retest: MLST in 3 join places; branches with no metadata keep the entity; metadata as base empties columns; the count 19 to 18) | the retest: places and columns by `apply`, tables by `run_audit` and reads by key | not known for the effects (the counts of joins are recipe facts: no) | engine (1.5), section 10 |
| G20, DESIGN G20 (APEC is "not offered") | "offered" is `describe`'s behaviour; that APEC declares no key is a recipe fact | no for the recipe fact; the "offered" part describes old code | my parse (1.2) |
| X4, DESIGN G29, B3-of-signs-v2, DESIGN G31 (counts: 7 tables rewritten under "one trunk"; the smallest number of steps 5 or 11) | counted by hand from the recipe and my map (`recipe_graph`) | not known | my parse (1.2) |
| G27, DESIGN G27, B1 of `OPUS_signs_v2.md` (a calculation between two nested places: upper 30, lower 25, both 30) | `add_step` (independent) and `run_audit` (J's table read from its stored file) | not known, unlikely: the three results differ, which a stale stored table would not give | section 10 (a hand-written small recipe) |
| Sonnet's tree property (all shipped recipes are trees from each original) | `recipe_graph` | not known | section 10 (my parse on all shipped recipes) |
| `opus_paths_map.out` (the stopped work): roots, pairs, joins, leaves, per-parent results | `recipe_graph`; "places: 52" with the walk's fold; sets judged against the 27 | not known (graph); yes possible (places, the 27) | replaced by section 1 |

---

## 1. The evidence base of this position

### 1.1 What I use, and only this
- **My graph** (`opus2_graph.py`): the recipe through the YAML loader `utils.config_loader.ConfigManager` (it resolves the `!include` files; its own imports are `yaml`, `os`, `pathlib`, `utils.deployment_error`, `utils.legacy_keys`) and my own reading of the recipe's keys: the schema blocks, `ingredients[].dataset_id` in order (the first is the base), the steps of each tier (`steps`, then `audit_steps`), the join steps (`right_ingredient`, `how`, the keys), the plots' `target_dataset`. Edges: `DS:s -> T1:s`; `T1:i -> T1:j` for each ingredient i of a join j; `T1:t -> T2:t`; `T2:target -> T3:plot`. The script fails if one of the forbidden modules is loaded (it checks `sys.modules`). [CODE READ `libs/utils/src/utils/config_loader.py:8-13`]
- **The engine** (`opus2_engine.py`): `DataOrchestrator.materialize_tier1/2/3`, each variant in its own new empty folder, every table rebuilt; tables compared with the original by exact equality. [CODE READ `app/modules/orchestrator.py:431-436`, `:589-592`, `:690-694`]
- **Writing a step**: by hand at the end of the tier's `steps` in a scratch copy of the recipe, and by `audit_copy.add_step` (for a filter, no `plans`), run as an audit copy through `cache_keys.loaded_from_resolved`. The two are compared in 1.4; `add_step` is used only where they agree.
- **Not used**: `lineage_walk`, `lineage_records`, `remove_from_all` (except, labelled, the old list of 27 places as a thing to compare with), `run_audit`, `plan_composer`, `key_drop`, `step_effects`, HOME's audit code; `recipe_graph` only in the labelled cross-check 1.3.

Every run was written in `RUN_REGISTER_opus.md` before it was made (requirement, expected result, why it is independent), as the owner asked (D-0561). Thirteen runs: R1 to R13. Each AGREES with its stated expectation, except one part of R5, which CONTRADICTS my stated explanation (1.5).

### 1.2 My graph of the demo (R1)
12 original tables, 16 joined tables, 17 plots, 85 nodes (DS, T1, T2 of every table, T3 of every plot). The demo's facts used below are in section 5. Forbidden modules loaded: none. [MY GRAPH SCRIPT `opus2_graph.py`, output `opus2_graph_demo.out`]
Side finding: the retest's map wrote "17 joined or derived tables" (`RETEST_her_scope.md:32`); my parse and `recipe_graph` both give 16.

### 1.3 The labelled cross-check, and the tree property (R3, R2)
- `recipe_graph` gives the same parents as my parse, order included, for every node of every shipped recipe both can read: 50 of 50 (93 files skipped: not a recipe with data schemas, or not loadable). So the cache keys, which follow `recipe_graph`'s lineage, follow my edges on every shipped recipe. [cross-check `opus2_crosscheck.py`, output `opus2_crosscheck.out`; labelled, no conclusion rests on it alone]
- Below each original table, every shipped recipe is a tree (no node with two parents inside it) and no join reads a join: 50 of 50. [MY GRAPH SCRIPT `--trees`, output `opus2_trees.out`]

### 1.4 Writing a step: `add_step` against a step written by hand (R4)
At `T1:MLST` and at `T2:ResFinder`, all 52 tables of the copy written by `add_step` equal those of a scratch recipe where the same filter is the last of the tier's `steps`. [ENGINE RUN `opus2_engine.py`, output `opus2_runA.out`]

### 1.5 My graph against the engine (R5)
- A step at `T1:MLST` changes 10 tables, `T2:ResFinder` 2, `T1:ResFinder` 12; none of them lies outside the place and what lies below it in my graph. [ENGINE RUN `opus2_runA.out`]
- The rows of the entity after a step at `T1:ResFinder`: they leave `ResFinder_with_metadata` (ResFinder is its base); they stay in `QA_AMR_per_sample` (1 row), `ST22_Anchor` (7) and `QA_fanout_exhibit` (23), where the metadata is the base and ResFinder a side of a left join, with ResFinder's columns emptied (`gene`, and `predicted_phenotype` or `phenotype`, `status`). After a step at `T1:MLST`: they leave `AR1_MLST_Serotype_Virulence` (MLST is its base) and stay in `ST22_Anchor` (MLST a side). [ENGINE RUN]
- **Contradiction (a finding).** `T2:QA_fanout_exhibit` and the plot `qa_fanout_rows_per_sample` lie below `T1:ResFinder`, hold the entity, and did NOT change: the left join kept the entity's 23 rows (only ResFinder's `gene` emptied) and the tier 2 counts the non-empty virulence genes per sample (`pl.col('VF_gene').count()`), the same 23 before and after. [CORRECTED 2026-11-23 by RR11: I had written "counts rows per sample".] I had expected a place below to stay unchanged only where the entity has no row. So "~" says "below the step"; it says neither "changed" nor "gone". [ENGINE RUN; it agrees with D-0545: the effect is known after Apply]

---

## 2. (a) What an independent path is

Her words. "Q1 - yes the user chooses at most one place =node (with the exception of the original parents where all can be choosed) then all paths are derived (~) and cannot be choosen. yes R2 rule. We need review of what is independent path and what is then derived." and "its more a directional graph with Tx at nodes and branches gives the directions" [HER WORDS D-0553]. "The only exception is if the user wants to one or several eg all FIRST T1 (right after the original data) to speed up things. So the step must be duplicated in all those T1 - this because of independent histories. But the user can only choose one scope per history" [HER WORDS D-0547]. "the only way to choose several places must be the case of the independent history - the original T1 steps of independent histories" [HER WORDS D-0549]. "each independent history is like an independent tree graph" [HER WORDS D-0550].

Words used below. A **path** is a chain of edges from an original table's file to a result (a plot). A place lies **below** another when a path goes from the other to it.

| # | Candidate definition | Computable? | Fits her words? | How sure |
|---|---|---|---|---|
| U1 | Two places are **independent** when neither lies below the other. A set of chosen places is allowed when its places are pairwise independent. | Yes: one walk down from each chosen place [MY GRAPH SCRIPT, function `sets`]. | It is "at most one place on a path" exactly: two chosen places on one path means one lies below the other, and the converse [REASONED, not run]. It fits D-0553. It fits "the original parents where all can be choosed" with no special case: the first place of an original table has only its file above it, so no original's first place lies below another's [REASONED; the set of all of them is valid, section 5]. | High |
| U2 | Two **original tables** are independent when no place lies below both. | Yes [MY GRAPH SCRIPT, pairs]. | No for D-0547's example "all FIRST T1": the metadata shares joined tables with almost every analysis table, so almost no two analyses would be independent (section 5) and the step could not go to "all FIRST T1". | High that it does not fit |
| U3 | An **independent history** is everything below one original table: one "tree graph" per original [D-0550]. | Yes. | It fits D-0550 as a VIEW. As a rule it is "one place per original's tree" (stricter than U1: two join places of MLST would be refused); her answer to Q1 chose the rule on paths (D-0553). | Medium: D-0550 and D-0553 are both hers; I read D-0553 as the rule and D-0550 as the view |
| U4 | Paths, in the words of the display: they split where a table feeds several children and meet where a joined table has several parents. | Yes. | It is how D-0553's "directional graph" reads on screen. | High, as words |

My position: U1 is the rule the app can check; U3 and U4 are how the graph is shown. "Independent" is a relation between two places, not between two original tables. [REASONED, not run]

---

## 3. (b) What is derived ("~")

- **The rule as a check.** Given the chosen places S of one step: S is valid when no place of S lies below another place of S. The derived places are every place below at least one place of S, the places of S excluded. A derived place cannot be chosen in the same step ("then all paths are derived (~) and cannot be choosen", D-0553). A later step may choose one ("if he want another choice he must add another step audit step later - choosing a different scope", D-0547). [HER WORDS D-0553, D-0547; the check: MY GRAPH SCRIPT]
- **What "~" says and does not say.** It says that a chosen place lies above, through at least one parent. It does not say that the entity is gone there: where the chosen place is a side of a left join, the base's rows stay (runs in 1.5 and 10).
- **Valid and invalid sets on the demo**: the table of section 5.3, from my script. The cases asked: all original parents; her quality case; `T1:MLST` with the three MLST join places; `T1:ResFinder` with `T1:QA_AMR_per_sample`.
- **How she removes the row that comes from the metadata side** (in `QA_AMR_per_sample` the metadata is the base and ResFinder a side, section 5.1), three ways, each valid under U1:
  1. choose `T1:QA_AMR_per_sample` instead of `T1:ResFinder` for that branch, with the join places of ResFinder's other branches and `T2:ResFinder` for the plot that reads ResFinder directly: one step, nothing nested;
  2. choose `T1:ResFinder` and `T1:metadata_schema` (two original parents): the entity then leaves every table built from the metadata ("If the user wants to remove from metada it must choose the T1 of metadata and remove there (not advised)", D-0547);
  3. keep `T1:ResFinder` and add a second audit step later at `T1:QA_AMR_per_sample` (D-0547, as quoted above).
  [HER WORDS D-0547; validity: MY GRAPH SCRIPT, section 5.3]

---

## 4. (c) How the app shows it

- **One graph**, from the files (left) to the results (right). A node is a place: the T1 of a table, the T2 of a table that a plot reads, a plot. An edge shows what goes into the next node ("the branches shows what goes into next node"; "Results (final tables and plots) are leaves no ?"). It is computed from the recipe alone, so it is shown before Apply; the effect only after Apply ("you cannot see effect if you do not recalculate"). [HER WORDS D-0553, D-0545]
- **What a node shows**: the table and its tier; its kind (original table, joined table, plot); its state: chosen, "~" (below a chosen place) or free; for a joined table, its parents in their order with the base marked, and the join kind written in the recipe (`left`, `inner`); "no plot reads this table; it is exported" where so (D-0457). My script gives each of these. [MY GRAPH SCRIPT]
- **A joined node that is "~" through one parent only** says which parent, and whether it is the base or a side: `QA_AMR_per_sample` "~ through ResFinder, a side of a left join; the base is the metadata". What follows from it is known by run (the entity's row stays, ResFinder's columns emptied, 1.5); whether the app may SAY so before Apply is Q5, open. [MY GRAPH SCRIPT; ENGINE RUN R5; Q5 OPEN]
- **MLST part**, with `T1:MLST` chosen (every place below it is "~"):

```
DS:MLST -> T1:MLST [CHOSEN] -+-> T1:MLST_with_metadata ~ (base MLST; + metadata, left) -> T2 ~ (2 steps) -+-> mlst_bar ~
                             |                                                                            +-> year_distribution ~
                             +-> T1:ST22_Anchor ~ (MLST a side; base metadata; + FastP, ResFinder,
                             |                     VirulenceFinder left; APEC inner)  -> T2 ~ (2 steps) --+-> virulence_bar ~
                             |                                                                            +-> virulence_variants ~
                             +-> T1:AR1_MLST_Serotype_Virulence ~ (base MLST; + metadata, VirulenceFinder left; APEC inner)
                                                                    no plot reads it: exported
```
  With the three join places chosen instead (valid, 5.3): `T1:MLST` free, the three joined tables CHOSEN, their T2 and the four plots "~". [MY GRAPH SCRIPT]
- **Quast part**, with `T1:Quast` chosen; its results lie in three groups:

```
DS:Quast -> T1:Quast [CHOSEN] -+-> T1:Quast_with_metadata ~ (base Quast; + metadata, left) -+-> assembly_quality_dotplot ~  (Quality Control)
                               |                                                            +-> miaou ~                     (Cat)
                               +-> T1:QC_Reads_Anchor ~ (Quast a side; base FastP; + Bracken, metadata, left) -> qc_reads_horizontal_barplot ~ (Quality Control)
                               +-> T1:QA_L50_integer ~ (Quast its only parent) -> qa_l50_integer ~   (QA canaries)
                               +-> T1:QA_population_zscore ~ (Quast a side; base metadata, left) -> T2 ~ (1 step) -> qa_population_zscore ~ (QA canaries)
```
  [MY GRAPH SCRIPT]

---

## 5. (d) The demo mapped by my script

### 5.1 Original tables [MY GRAPH SCRIPT R1]
| Original | Read by (base or side) | Plot on its own T2 | Plots below, by group |
|---|---|---|---|
| Summary | `Summary_phenotype_length_fragmentation` (base) | - | Curiosity 1 |
| Summary_quality (same file as Summary) | `Summary_phenotype_length_fragmentation` (side), `QA_ST_with_NA` (only parent) | - | Curiosity 1, QA canaries 1 |
| Quality_metrics, Detailed_summary | no table | - | none |
| FastP | `FastP_with_metadata`, `QC_Reads_Anchor` (base), `ST22_Anchor` (side) | - | Quality Control 1, AMR and Virulence 2 |
| Quast | `Quast_with_metadata`, `QA_L50_integer` (base), `QC_Reads_Anchor`, `QA_population_zscore` (side) | - | Quality Control 2, Cat 1, QA canaries 2 |
| Bracken | `Bracken_with_metadata` (base), `QC_Reads_Anchor` (side) | - | Quality Control 1 |
| ResFinder | `ResFinder_with_metadata` (base), `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit` (side) | `amr_heatmap` | AMR and Virulence 3, QA canaries 2 |
| MLST | `MLST_with_metadata`, `AR1_MLST_Serotype_Virulence` (base), `ST22_Anchor` (side) | - | AMR and Virulence 4 |
| VirulenceFinder | `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_fanout_exhibit` (side) | - | AMR and Virulence 2, QA canaries 1 |
| APEC_STEC_virulence_genes (declares no key) | `ST22_Anchor`, `AR1_MLST_Serotype_Virulence` (side, inner join) | - | AMR and Virulence 2 |
| metadata_schema | 13 tables: a side in 7 (`FastP_`, `Quast_`, `Bracken_`, `ResFinder_`, `MLST_with_metadata`, `QC_Reads_Anchor`, `AR1_...`), the base in 6 (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, and `QA_year_types`, `QA_aggregated_no_key`, which it alone feeds) | - | 13 of the 17 plots, in 4 groups (not below it: `amr_heatmap`, `phenotype_genome_length_fragmentation`, `qa_l50_integer`, `qa_sequence_type_missing`) |

### 5.2 Other facts [MY GRAPH SCRIPT R1]
- Joined tables with several parents: 12 (listed, base first, in `opus2_graph_demo.out`). Joins are `left`, except the joins with `APEC_STEC_virulence_genes` (`inner`, on `VF_gene` = `Gene_name`).
- Tables with one parent: `QA_ST_with_NA` (Summary_quality), `QA_L50_integer` (Quast), `QA_year_types`, `QA_aggregated_no_key` (metadata).
- Tables with no plot below them (exported, D-0457): `AR1_MLST_Serotype_Virulence`, `Bracken_with_metadata`, `FastP_with_metadata`, `ResFinder_with_metadata`, `Detailed_summary`, `Quality_metrics`.
- Of the 66 pairs of originals, 21 share a node below them and 45 share none; the four that never meet the metadata (Summary, Summary_quality, Quality_metrics, Detailed_summary) share nothing with any other original except Summary with Summary_quality.

### 5.3 Sets of chosen places [MY GRAPH SCRIPT R1, R10]
| Set | Places | Valid (no chosen place below another) | Pairs upper -> lower | Plots below | Plots outside |
|---|---|---|---|---|---|
| All original first places that declare the key (UPPER) | 11 | yes | 0 | 17 | none |
| "Remove from all the data" as decided (ALLKEY) | 27 | no | 35 | 17 | none |
| The retest's defaults (A3) | 19 | no | 4 (`T1:ResFinder` above its 4 joined tables) | 17 | none |
| Her case as run in the retest (B3) | 17 | no | 4 (the same) | 14 | the 3 quality plots |
| Her case with `T2:ResFinder` (R2) | 17 | yes | 0 | 14 | `assembly_quality_dotplot`, `miaou`, `qc_reads_horizontal_barplot` |
| `T1:MLST` with its 3 join places | 4 | no | 3 | 4 | 13 |
| The 3 MLST join places | 3 | yes | 0 | 4 | 13 |
| `T1:MLST` alone | 1 | yes | 0 | 4 | 13 |
| `T1:ResFinder` with `T1:QA_AMR_per_sample` | 2 | no | 1 | 5 | 12 |
| `T1:ResFinder` with `T1:metadata_schema` | 2 | yes | 0 | 14 | `phenotype_genome_length_fragmentation`, `qa_l50_integer`, `qa_sequence_type_missing` |
| `T2:ResFinder` with `T1:QA_AMR_per_sample` | 2 | yes | 0 | 2 | 15 |

---

## 6. (e) Consequences for Q2, Q4, Q5 (not answered)

- **Q2, the default where her rule says nothing.** Her words: "in manycase I would select the scope of where original T1+ metadata are joined" [HER WORDS D-0549]; "the first T1 of the lineage when no metadata join" [HER WORDS D-0550]. Fact: for an original that has join places with the metadata AND a branch that never meets the metadata (ResFinder with `amr_heatmap`; Quast with `qa_l50_integer`), "the first T1 of the lineage" read as the original's own first place lies above its own join places, so the defaults together are not valid (A3, 5.3) [MY GRAPH SCRIPT]. The first place that only that branch reads (`T2:ResFinder`; `T1:QA_L50_integer`) keeps them valid and gives the same 17 plot tables (R8) [ENGINE RUN]. Q2 has to say which place "the first T1 of the lineage" is for such a branch.
- **Q4, "remove from all the data".** The decided form (tier 1 of every table that holds the key, D-0416 as decided) is 27 places on the demo, the same set as the old list, and is not valid as one step under the rule of one place on a path (35 pairs) [MY GRAPH SCRIPT R10; ENGINE RUN R7]. The 11 original first places are valid (the exception of D-0553). The three forms give the same 17 plot tables, rebuilt from scratch, for two entities, the entity in none [ENGINE RUN R7]. They do not leave the same tier-1 tables: UPPER and ALLKEY leave the same 28; the defaults (A3) leave the entity in the tier 1 of Bracken, FastP, MLST, Quast, VirulenceFinder and the metadata, which the export writes (D-0457) [ENGINE RUN R11]. Reopens (information only): D-0416 as decided and D-0553 cannot both hold for one step.
- **Q5, saying before Apply that the entity can remain.** The structure says, for a joined node below a chosen place, through which parent it is "~", whether that parent is the base or a side, and the join kind [MY GRAPH SCRIPT]. The runs: through a side of a left join the entity's rows stay, with that parent's columns emptied; through the base they leave; and a place below can stay exactly equal [ENGINE RUN R5, R12]. Whether the app may say it is hers (Q5, open).

---

## 7. (f) What she may be missing

1. **The rule on paths allows more than "one scope per history".** The three MLST join places in one step are valid (5.3); under "the user can only choose one scope per history" (D-0547) they would not be. Her answer "the user chooses at most one place =node" (D-0553) and her earlier words differ on this case. [HER WORDS D-0547, D-0553; MY GRAPH SCRIPT]
2. **The exception of the original parents needs no special case** in the check (U1, section 2). [REASONED; MY GRAPH SCRIPT]
3. **"~" is not "changed", and not "gone".** [ENGINE RUN R5]
4. **The same intention gives different tables at different places.** Removing the entity at `T1:MLST` keeps its 7 rows in `ST22_Anchor` (MLST is a side) with MLST's columns emptied, and they still feed both virulence plots; removing it at the three join places takes those rows out; `T1:MLST` itself (exported) then keeps the entity. [ENGINE RUN R12]
5. **A joined table read by several plots is a shared node too**: `ST22_Anchor`, `MLST_with_metadata`, `Quast_with_metadata` (its two plots are in two groups, Quality Control and Cat), `QA_year_types`. The gotcha of D-0555 is not only at the original parents. [MY GRAPH SCRIPT]
6. **The metadata lies above 13 of the 17 plots**, in 4 groups. [MY GRAPH SCRIPT]
7. **Removing one entity changes the values of the others** where a calculation over all entities lies below the step: all 41 other z-scores in `QA_population_zscore`, one count in `QA_aggregated_no_key`. [ENGINE RUN R13]
8. **Two nested places in one step: the upper decides** a calculation that lies between them (R9); the rule of one place on a path keeps one step free of it. [ENGINE RUN R9]
9. **Six tables have no plot below them** and are still reached and exported (5.2). [MY GRAPH SCRIPT]

**"Maybe the demo recipe is wrongly done": facts only; the demo is not changed by agents.**
- Shapes that make the rule harder: the metadata is the base of 4 joined tables with analyses (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`), against "T1 original -> left_join -> metadata" (D-0547) and "The metadata should be the right table -- best practice" (D-0549); originals read by several joined tables (5.1); one joined table of six originals (`ST22_Anchor`) and two of four; a plot on an original's own tier 2 next to that original's joins (`amr_heatmap`); two tables on one file; six tables with no plot below. [MY GRAPH SCRIPT; HER WORDS D-0547, D-0549]
- What an author can write differently today, within today's format: the metadata as the right table of every join (`right_ingredient: metadata_schema`, as 7 joins already do); one join of an original with the metadata read by all the plots of that original (several plots can target one join, as `mlst_bar` and `year_distribution` do); a second source table on the same file for a second use (her reimport idea; R6: all plot tables stay equal). [RECIPE FILE `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:163-260`; ENGINE RUN R6]

---

## 8. (g) A parent reused in another graph (D-0555)

Her words: "A note : if several parents are choosen the step applied must be applied in each T1 comming from the parent - and that is where it can be a got you if the parent is reused in another directed graph - so we need here to have the 2 directed graphs that go from the same parents - because both will be affected ." [HER WORDS D-0555]

- **g.1 Two readings of "each T1 comming from the parent"** (not chosen here). (i) The parent's own first place (`T1:MLST`): one step that reaches every graph below the parent. (ii) The first place of each table that reads the parent (`T1:MLST_with_metadata`, `T1:ST22_Anchor`, `T1:AR1_MLST_Serotype_Virulence`): one step per graph; for a plot that reads the parent's own tier 2 (`amr_heatmap` reads ResFinder) there is no reading table, and its first place is `T2:ResFinder`. The two give different tables: 5 differ on the demo (`T1:MLST`; `ST22_Anchor` T1 and T2; both virulence plots). [ENGINE RUN R12]
- **g.2 A computable definition.** For a chosen original P, its reading tables are the joined tables that list P in `ingredients`, plus P's own tier 2 when a plot targets P. "The directed graphs that go from the same parent" are one per reading table: that table and everything below it. Today these graphs never meet below (a join reads original tables only, J04; every shipped recipe is a tree below each original, R2). Two results share "only the metadata" when the metadata is the only original above both (for example `mlst_bar` and `qc_reads_horizontal_barplot`); they are reached together only by a step at the metadata's first place. [MY GRAPH SCRIPT R1, R2; CODE READ `recipe_check.py:867-869`]
- **g.3 The demo.** Per parent: 5.1. Parents whose plots lie in more than one group: Summary_quality, FastP, Quast, ResFinder, VirulenceFinder, metadata_schema. Starting from one plot, the other plots below its originals:

| Start | Its originals | Other plots below them | Without the metadata |
|---|---|---|---|
| `mlst_bar` | MLST, metadata | 12, in 4 groups | 3: `virulence_bar`, `virulence_variants`, `year_distribution` |
| `amr_heatmap` | ResFinder | 4: `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `virulence_bar`, `virulence_variants` | the same 4 |
| `qc_reads_horizontal_barplot` | FastP, Quast, Bracken, metadata | 13, in 4 groups | 6: `assembly_quality_dotplot`, `miaou`, `qa_l50_integer`, `qa_population_zscore`, `virulence_bar`, `virulence_variants` |
| `virulence_bar` | 6 originals | 13 | 7 |
  [MY GRAPH SCRIPT R1]
- **g.4 Shown before Apply.** For each chosen parent, one block per reading table: the reading table (base or side; join kind), its plots by analysis group, its tables no plot reads (exported); the plots outside the one the user started from are marked. Today's library has, per place, a list of reached tables and plots (`lineage_records.py:238-247`); it is old code, described here only, not used; it is not grouped by reading table or by analysis group. [CODE READ, old code]
- **g.5 Consequences.** Q4: reading (i) at the original first places reaches every graph at once (UPPER); reading (ii) leaves the entity in the originals' own tier-1 tables, which are exported (R11, R12). Q5: under (i), in a joined table where the parent is a side, the entity's rows stay (R5, R12): the case "can remain".
- **Gotcha wording for the good-practice page (PROPOSAL, mine, not decided).** For authors: "A table that several tables read puts all of them under one step: a step at its first place reaches every result built from it, in every group." For users: "A step at a table that other tables read changes every result built from it, also in other groups: look at all of them before you confirm."

---

## 9. (h) The investigation: how to avoid the errors of a parent reused in another graph (D-0556)

Her words: "I think this needs to be investigated by the reviewer, and what would be the possibilities to avoid errors - and if possible to avoid errors in complex solutions then fine but we need to be sure what can be done before we choose"; her idea: "or one rule could be that if we need this we need to reimport the original data - so that the original parents -> T1 cannot be shared - can cost a bit of recompute (because we have duplicated steps) but can avoid headeaches - and those cases are likely not to occur often" [HER WORDS D-0556]; "they can do some tests if necessary" [HER WORDS D-0557].

### 9.1 What can go wrong
| # | What goes wrong | On the demo | Basis |
|---|---|---|---|
| E1 | A step at a shared parent changes results outside the graph the user started from | from `mlst_bar`, a step at `T1:MLST` also changes `virulence_bar`, `virulence_variants` and `AR1_MLST_Serotype_Virulence` (exported) | ENGINE RUN R5, R12 |
| E2 | The user does not see those results when she decides | the plot she starts from shows its own lineage only | REASONED |
| E3 | The metadata is a parent of almost every analysis | 13 tables, 13 of 17 plots | MY GRAPH SCRIPT |
| E4 | One step does different things in different graphs | base of a left join: rows leave; side: rows stay, columns emptied; a count per sample did not move | ENGINE RUN R5 |
| E5 | The values of OTHER entities change below the step | all 41 other z-scores; one count in a table with no key | ENGINE RUN R13 |
| E6 | Two places one below the other in one step: the upper decides | B1 | ENGINE RUN R9 |
| E7 | A stored table of a graph the user did not touch is served stale | not seen: keys chain through every parent (reading, section 11, j.2); the edges of the keys equal my parse on 50 of 50 recipes (R3) and my parse equals the engine at 3 places (R5); the stale probe is the Sonnet partner's run | CODE READ; R3, R5 |
| E8 | Two tables on one file: a step at one does not reach the other | Summary and Summary_quality are separate parents | MY GRAPH SCRIPT (run: Sonnet's share) |
| E9 | Same plots, different exported tables | A3 against UPPER: 6 original tier-1 tables | ENGINE RUN R11 |
| E10 | The two readings of D-0555 give different joined tables | `ST22_Anchor` and both virulence plots | ENGINE RUN R12 |

### 9.2 The possibilities, what each prevents and what not
| # | Possibility | Prevents | Does not prevent | The author sees | The user of the audit sees | In complex recipes (six originals; a parent in several joins; the metadata first; a table computing over all entities) |
|---|---|---|---|---|---|---|
| X | Before Apply, show every graph that goes from each chosen parent (structure only) | E1 and E2 as a silent change: she sees every reached result | the choice itself (it stays hers: D-0543, D-0544); E4, E5 as effects (known after Apply) | nothing new | a block per reading table, its plots by group (MLST: 3 blocks, 4 plots; the metadata: 13 blocks, 13 plots) | works: computed from the recipe; the list grows with the recipe |
| Y-a | Her rule as an advice: a parent read by several tables is flagged; the author may read the file again as a second table | E1 at the original level, where the author follows it | E1 one level down (a joined table read by several plots); E3 unless the metadata is also split; E4, E5 inside one graph | an advice per shared original (on the demo: 8 originals and the metadata) | after the author's change, smaller blocks | works for originals; does not split a joined table of six originals that feeds two plots |
| Y-r | Her rule as a refusal by the recipe check | as Y-a, for every recipe that loads | as Y-a; and every shipped recipe that shares a parent stops loading until rewritten (the demo shares 8 originals and the metadata) | a refusal with the tables to split | as Y-a | as Y-a |
| Z | X and Y together | X's and Y's | as X | as Y | as X | as X and Y |
| W1 | The confirmation names every graph and result the step reaches; the log keeps the list | E2 | the choice | nothing new | one list to confirm | works |
| W2 | After Apply, a check by run names the results changed outside the graph she started from; she can remove the step ("the can still remove a step from the audit after apply", D-0545) | E1, E4, E5 left unnoticed | the change before she sees it | nothing new | after Apply: "also changed: virulence_bar, virulence_variants, AR1 (exported)" | works: a rebuild of what lies below and a comparison per table |
| W3 | A step is written only at a place whose whole reach was shown and confirmed | writing without having seen | the choice | nothing new | a gate on W1 | works |
| W4 | Per-graph ticks: each reading table of a chosen parent is a line, all ticked; unticking one writes the step at the first places of the ticked graphs instead (reading (ii)) | E1 for a graph she unticks | E4 (the two readings differ, R12), E5 | nothing new | ticks per reading table | works while the graphs from one parent never meet below (true today, R2) |
| W5 | Choose by result: she ticks results; the app proposes the highest places whose reach lies inside them | E1 by construction | E5 inside the chosen results | nothing new | ticks on results; places proposed | works; reopens D-0022 ("only automatic placement 'remove from all tables'") and touches D-0531 ("the app cannot decide the scope"): information |
| W6 | The recipe check tells the author, as information, which tables several tables read and what lies below them | an author's surprise | the user's choice | a list per shared table | nothing | works |

### 9.3 What can be done
| # | Feasible? | Evidence |
|---|---|---|
| X | feasible | my script computes every block from the recipe alone (8, g.3) [MY GRAPH SCRIPT] |
| Y-a, Y-r | partly | the format and the engine take a second table on the same file, and every plot table stays equal (R6) [ENGINE RUN]; Data Import already treats tables that share a file (`app/modules/data_import_check.py:83`, `:91`, `:177-178`, `:222`) and the keys hash the file once per table (`app/modules/cache_keys.py:139-147`) [CODE READ]; but a deployment that finds files by table name (`by_dataset_id`) needs a file for each table name (`app/modules/orchestrator.py:173-190`) [CODE READ]; the details of two tables on one file are the Sonnet partner's runs. The author writes, per extra use, one schema entry (10 lines with the same includes) and changes the ingredient and its `right_ingredient` (R6). The rebuild of the demo took about 1 s with or without the split; the split builds one more tier-1 table per extra use, and each joined table already reads its ingredients from their files (`orchestrator.py:269-283`), so that is what the user waits for, as a fact. The metadata: read by 13 tables; under the rule, 12 more tables on the metadata file, or the metadata as the one exception (a step at its first place then still reaches 13 of 17 plots, and her own advice calls that place "not advised", D-0547). |
| Z | as X and Y | |
| W1, W3 | feasible | structure only [MY GRAPH SCRIPT] |
| W2 | feasible | a rebuild and a comparison per table is what every run here did (R4-R12) [ENGINE RUN]; the effect after Apply is hers (D-0545, D-0546) |
| W4 | feasible | the step at the first places of the reading tables is R12 [ENGINE RUN] |
| W5 | feasible to compute; a decision | reopens D-0022 |
| W6 | feasible | per-original lists of 5.1 [MY GRAPH SCRIPT] |

### 9.4 The question for her, as it would be put
"A table that several tables read can carry a step into results you are not looking at. On the demo, a step at MLST also changes the two virulence plots and the exported table AR1; a step at the metadata reaches 13 of the 17 plots. Which of these should the app do?
- X: before you confirm, show every graph that starts from the table you chose, with its results by group (MLST: 3 graphs, 4 plots).
- Y: your rule: a table read by several tables gets a warning from the recipe check (advice), or the recipe is refused until each use reads the file as its own table (refusal). On the demo 8 tables and the metadata would be split; the plots stay the same (we ran it for MLST). Does it apply to the metadata (12 more copies), or is the metadata the one exception?
- Z: both.
- W4 (with X): you can untick a graph; the step is then written lower, at the first place of each graph you keep (the tables differ: on the demo the virulence plots lose the entity's rows instead of keeping them with empty MLST columns).
- W2 (with any): after Apply, the app names the results that changed outside the plot you started from, and you can remove the step.
- Neither."
**My lean, as a lean:** X with W4 and W2; Y as an advice (Y-a), not a refusal. Reasons, on what each prevents: X and W2 cover a parent shared at every level (an original, the metadata, a joined table read by several plots); Y does not split a joined table read by several plots, nor the metadata unless it is copied 13 times, nor E4 and E5, which happen inside one graph. Cost is not my reason. [REASONED]

---

## 10. (i) The recheck of earlier points

| Earlier point | What rested on old code | Recheck | Result now |
|---|---|---|---|
| Tree below each original (Sonnet's script; A3, DESIGN G3) | `recipe_graph` | my parse on every shipped recipe (R2) | CONFIRMED: 50 of 50 |
| The graph points (P2, P5, S3, J1-J3, DESIGN G3-G5, G14-G16, G18) | `recipe_graph` | my parse (R1); `recipe_graph` against my parse (R3); my parse against the engine (R5) | CONFIRMED; the counts of shared places now count nodes, not the walk's places |
| The 27 places of "remove from all" as decided (G26 (a), Q4, Q8) | `remove_from_all.describe` | the tables whose engine-built T1 holds the key (R7) | CONFIRMED: the same 27 |
| The three forms give the same 17 plot tables (G26, P21, S18, O5) | `apply`, reads of stored tables by key | rebuilt from scratch, two entities (R7) | CONFIRMED |
| "The exported tier 1 files would differ" (G26, B2 "not run") | reasoned | R11 | CONFIRMED for A3 against UPPER and ALLKEY (6 tables); UPPER and ALLKEY leave the same tier-1 tables |
| R2 gives the same plot tables as B3 (X1) | `apply`, reads by key | rebuilt (R8) | CONFIRMED |
| Nested pair: upper 30, lower 25, both 30 (G27, B1) | `run_audit` | steps written by hand (R9) | CONFIRMED |
| Rows stay where the metadata is the base; "~" is not "gone" (G11, G17, G24, P23, P24, A11) | the retest (`apply`, `run_audit`) | R5 rows | CONFIRMED, and stronger: a place below can stay exactly equal (R5 finding) |
| A step at T2 reaches only the plots that read that T2 (G1's engine fact, G15) | the walk's fold | R5 (`T2:ResFinder`: 2 tables) | CONFIRMED |
| "17 joined or derived tables" (`RETEST_her_scope.md:32`) | the retest's map | R1, R3 | CORRECTED: 16 |
| The count 19 -> 18 in `qa_aggregated_no_key` (P26) | the retest | R13 | CONFIRMED that one count changes (the value itself not reread) |
| The column's fate "from the walk" (J7, A10, DESIGN G10) | the walk | not rechecked | void as a design source (D-0558); needs its own source |
| "7 tables rewritten under one trunk" (G29), the smallest number of steps (G31) | counted by hand with `recipe_graph` | not rechecked | G31 rests on the reading "one place per tree", which D-0553 replaced; G29 to be recounted if "one trunk" comes back |

---

## 11. (j) Every place below a change is computed again (her requirement, D-0560)

Her words, as the coordinator quoted them (M613): "we need to ensure that everystep after a change in a place is recalculated - that would otherwise produce errors indeed ..." [HER WORDS D-0560]

### j.1 The evidence rule in this position
- Every variant of my runs is built in its own new, empty folder: `opus2_engine.py`, function `build`, `folder.mkdir(parents=True)` fails when the folder exists; tier 1 of every table, tier 2 of every table with tier-2 steps that a plot reads, then every plot. A label "rebuilt" means exactly that. [ENGINE RUN opus2_engine.py]
- The earlier equalities ("0 of 17 plot tables differ" in `opus_runs.out` and the retest) were NOT rebuilt: a plot's table was read from the original's stored tables when its target's key had not changed (`opus_runs.py:60-64`). Section 0 marks them "not known"; section 10 rebuilds them.

### j.2 What today's keys hold, by reading
- A table's T1 key = `E . rC . dC . [a1]`; its T2 key = its T1 key `. [s2] . [a2]`; a plot's key = the T2 key of its target `. [s3] . [a3]`; a part is left out when its tier has no step, and the key is then the key before it. [CODE READ `app/modules/cache_keys.py:14-16`, `:284-330`, `:465-472`]
- `rC` holds the definition of the table and of every table above it, each with the tables it reads (its parents), plus the top-level parts shared by all tables. "Above" is `recipe_graph.lineage_back` over the T1 nodes. [CODE READ `cache_keys.py:262-273`]
- `dC` holds the content of the data files of every original table above it; `a1` holds the tier-1 audit operations (without id and reason) of the table and of every table above it. [CODE READ `cache_keys.py:223-231`, `:266`, `:274-275`, `:284-290`]
- So a joined table's T1 key is built from ALL its ingredients (base and sides): the T1 of each ingredient is a parent of the join (`recipe_graph.py:583`) and so in its lineage. A plot's key is built from its target's T2 key and its own tier-3 steps. [CODE READ, as above]
- When can a plot's key stay the same although an audit step exists above it? By reading, four cases:
  1. The step is in the tier 2 of an ingredient of the plot's target. The join reads the T1 of its ingredients (`orchestrator.py:269-283`), so the engine does not run that step for this plot; the key rightly stays. [CODE READ]
  2. The engine reads a parent that the key's lineage does not hold (two readings of one fact: what the engine reads, `orchestrator.py` `ingredients`; what `recipe_graph` says the table reads). Then the key stays and a stored table can be served stale. This is the case a test must catch. [REASONED, not run]
  3. The graph cannot be drawn: every key is coarse (the whole recipe, every data file, every tier-1 audit step), so keys move more, never less. [CODE READ `cache_keys.py:242-247`, `:255-258`]
  4. Two audit steps differ only by id or reason: the keys are equal, and so are the tables. [CODE READ `cache_keys.py:223-231`]
- `run_audit` builds no plot whose key did not change (`audit_run.py:262-264`). By reading, this is safe exactly when case 2 cannot happen. Whether it happens: the parents in `recipe_graph` equal my own parse, order included, on 50 of 50 shipped recipes (R3, section 1.3), and on the demo nothing outside "the place and below" in my parse changed in the engine at 3 places (R5). So case 2 was not seen; this is not a proof for every future recipe, which is why j.3 asks for one reading of the edges and the tests T-1 to T-3. The Sonnet partner runs the key check and the stale probe itself (M613); I do not repeat them. [cross-check R3; ENGINE RUN R5]

### j.3 The requirement, as proposed text for the design (the rule is hers; the wording and the "how" are my proposal)
- **Requirement.** After a change at a place, every place below it is computed again from its parents. A table stored before the change is never read for a place below the change.
- **How the app can guarantee it under the directed graph.** The key of each node is made of its own content (its steps and audit steps and its engine; for an original table, the content of its file) and of the keys of ALL its parents, in their order (the base first). For a joined node that means the T1 key of every ingredient. A change at a node then changes its key and, through the chain, the key of every node below it, and no other key. "Below" for the keys is "below" in the graph, so the edges used for the keys must be the edges the engine reads: one function says what a node reads, and both the engine and the keys use it (or a test checks on every shipped recipe that the two agree). A stored table is read only under its full key, never by its name.
- **Tests that prove it, each able to fail.**
  - T-1, the keys follow the graph: on a small recipe with a join of three parents (the metadata as the base), a tier 2 and a tier 3, write a step at each node in turn; the keys of exactly the nodes below it change, and no other key.
  - T-2, a stale probe: build the original into a folder; add a step at a SIDE ingredient of a join; build the copy into the SAME folder; every table below equals a build from scratch in an empty folder, and differs from the original's stored table. Then break the key on purpose once (leave out the audit part, or one parent): the test must fail, because the stale table is served.
  - T-3, the skip is safe: the run that skips a plot whose key did not change gives the same plot tables as a build of every plot from scratch.

### j.4 For `AUDIT_FIRST_BUILD.md`, later (not now)
When the design is agreed, its first slice verifies by a run that an audit step at any place changes the keys of every table and plot below it (T-1, T-2), and says whether the skip at `audit_run.py:262-264` is safe (T-3).
