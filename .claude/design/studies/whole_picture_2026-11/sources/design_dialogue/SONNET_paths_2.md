# SONNET paths position 2 (restart, from an empty file, under the owner's evidence rules)

Her order (M612, D-0558): "well we cannot do on the old structure on the lineage true --- no point it would inject errors in conclusions"; and "if the agents test on wrong lineage structure their conclusions cannot be used in this case its better to stop them and to make them restart".
Evidence tags used in the whole file: [HER WORDS D-n] / [RECIPE FILE path:line] / [MY GRAPH SCRIPT] / [ENGINE RUN script, output] / [REASONED, not run] / [UNVERIFIED: passed through old lineage code].
State of the machine: the load was 12 to 50 while the first sections were written; the runs below were made at load 5.8 to 6.6, after the reviewers' test suites were stopped. Section 9 holds the results; every run is registered before it was made in `RUN_REGISTER_sonnet.md` with its requirement, expected result and independence.

## 0. WHAT I HAD USED BEFORE THE STOP

### 0.1 In the stopped work on the paths position (never completed; moved to `stopped/`)
| What | Label | Why |
|---|---|---|
| `sonnet_paths_map.py` first version: `utils.recipe_graph.build_graph` (children, parents, `lineage_forward`, `lineage_back`, `nodes`, `plots`, `plot_target`) | NOT SURE | The module reads only recipe keys (tables, ingredients, tiers, plot targets) and no decision about places; but it is shared with the old audit lineage (its own docstring: it serves HOME's audit, the lineage, the checker and the cache keys). It was never run in that version. |
| `sonnet_shared_run.py` first version: `run_audit`, `compose_plan_book`, `remove_from_all.removal_step`, `loaded_from_resolved(plans)` | NOT SURE / OLD | `run_audit` rebuilds only what its keys say changed (the keys use `recipe_graph`); `compose_plan_book` is the engine's plan used by the walk; `removal_step` lives in the old place-list module. Never run. |
| `sonnet_shared_run.py` second version: own graph, `materialize_tier1/2/3` into empty folders, `add_step` with `plans=None` | not yet judged (section 1) | Never run. |
| Reading of `lineage_walk.py` (header, `_build_places`, `reach_of`), `lineage_records.py` (`Line`, `Reach`, `Hop`), `remove_from_all.py` | OLD LINEAGE CODE (read only) | I read them to describe what the old code gives. No result of this restart may rest on them. |
| Retest `RETEST_her_scope.md` and the Opus runs `opus_runs.out` (cited as evidence) | OLD LINEAGE CODE | They wrote places with `remove_from_all.apply(..., ticked=...)`, the offered list (27) comes from `remove_from_all.describe` (the walk), and they measured with `run_audit` (judged in section 1). |

### 0.2 In my earlier files, point by point
"Could the conclusion be wrong because of it": yes / no / not known.

**My tree-property script (`sonnet_tree_property.py`, 50 of 50 recipes give a tree).** It used `utils.recipe_graph.build_graph`: NOT SURE. Could be wrong: not known (it reads only `ingredients` and plot targets; a cross-check with my own parse is needed; it is listed in section 8).

**`SONNET_position_1.md`.**
| Point | Rests on | Label | Could be wrong |
|---|---|---|---|
| S3 (history = tree; plot branch counts) | `recipe_graph` (`trees.py`) | NOT SURE | not known |
| S10 (counts, retest facts) | retest | OLD (place list) / run_audit | not known |
| S16 (`Hop.join_side`, `join_how` give the kind and side of a join) | `lineage_records.Hop` | OLD LINEAGE CODE | yes: the claim that the recipe alone certifies "can remain here" was reasoned through `Hop`; the kind (`how`) and the order of `ingredients` can be read from the recipe itself, the certainty rule cannot be taken over |
| S17 ("27 offered", `NotReached`) | `remove_from_all.describe` | OLD LINEAGE CODE | not known (27 = 28 tables minus APEC by arithmetic on the recipe keys; that each holds the key at the end of tier 1 is not checked) |
| S18, S19 (`remove_from_all.apply`, one step per place) | code reading of `remove_from_all` | OLD | no (a description of the old code) |

**`SONNET_round_2.md`.** C1, C2, C3 (code reading of `recipe_graph`, `recipe_check`: J04, ST05): the checker lines are not lineage code (INDEPENDENT); the graph lines NOT SURE; could be wrong: no for J04/ST05, not known for the graph. C4 (B3 = S6, 17 of 17 records equal in `results.json`): the records come from the retest (OLD place list, `run_audit`): not known. C5 (`T1:ResFinder` has five children): `recipe_graph`: NOT SURE, low risk. C6 (ingredients, base): read from the recipe keys: INDEPENDENT.

**`AGREED_AND_OPEN_v3.md` / `DESIGN_AGREED_AND_QUESTIONS.md` (G1 to G31, Q1 to Q8).**
| Point | Rests on | Label | Could be wrong because of old code |
|---|---|---|---|
| G1 place, fold | decisions D-0541, D-0346; `lineage_walk.py:394-395` | the fold is an OLD LINEAGE decision of the walk (a statement about that code) | not known (G28 is a defect of the old walk, not a claim about the recipe) |
| G2 original table, G12 no new key, G13 results, G21, G22, G7, G9 | ledger words, recipe keys | INDEPENDENT | no |
| G3 tree | `recipe_graph`, `recipe_check` J04 | NOT SURE | not known |
| G4, G8 definitions | reasoned | INDEPENDENT | no |
| G5 shared place counts (6, 4, 4) | recipe `ingredients` | INDEPENDENT | no |
| G6 join with the metadata, ST05 | checker code, recipe keys | INDEPENDENT | no |
| G10 two functions, what the walk gives | code reading | description of OLD code | no |
| G11 "~" is not "gone" (runs E, D) | retest | UNVERIFIED | yes (run_audit reuse by keys; place list by the walk) |
| G14 shared tiers | `recipe_graph.py:582-585` | NOT SURE | not known |
| G15 `T2:ResFinder`, run R2 | `recipe_graph` children; Opus run | UNVERIFIED | yes |
| G16, G17, G24 (runs A, B2, C, E, z-score 41 of 41, 19 to 18) | retest | UNVERIFIED | yes |
| G18 metadata-only tables | recipe `ingredients` | INDEPENDENT | no |
| G19 join places per original (3, 3, 3, 4) | retest map (graph `source_tables` and raw) | NOT SURE | not known |
| G20 APEC has no key | retest, input fields | INDEPENDENT (data columns) | no |
| G23 one step per place | `remove_from_all.apply` | OLD code description | no |
| G25 (on screen today; 27 places) | grep of `app/`; `describe` for 27 | grep INDEPENDENT; 27 OLD | the grep: no; the 27: not known |
| G26 three forms of "remove from all" (Opus runs) | `describe` (OFFER list), `apply`, `run_audit` | UNVERIFIED | yes |
| G27 nested pair B1 (mean 30 or 25) | Opus synthetic run; arithmetic | the numbers check by hand: INDEPENDENT; the demo claim (B3 = S6) UNVERIFIED | no for the arithmetic; yes for the demo claim |
| G29 one trunk (7 tables) | recipe `ingredients` | INDEPENDENT | no |
| G31 minimum steps (5, 11) | `ingredients` lists | INDEPENDENT (hand count) | no |
| Q5 "certain only at a join on the entity key (left, inner, semi)" | `lineage_walk` header P12, `Hop` | OLD LINEAGE CODE | yes |
| Q1 to Q4 demo numbers (14 changed, stays in 3, 17 plot tables) | retest and Opus runs | UNVERIFIED | yes |

**A second risk, found by the Opus partner and checked here:** the retest and the Opus runs read a plot's table from the ORIGINAL's stored tables when the target's tier 1 key did not change, and `run_audit` skips a plot whose cache key did not change (`audit_run.py:164-186`, the plot loop in `run`; the keys read `recipe_graph`). A stale stored table would give exactly "0 of 17 plot tables differ". So those equalities (the three forms of "remove from all", her case with nothing nested against run B3, G26, G27 demo claim, the numbers of Q1 to Q4) are NOT KNOWN until each variant is rebuilt in its own EMPTY folder. My runs do that: every variant, and the original, is built from scratch in its own empty folder, nothing is reused between runs; each run line below says so. Also not known until rechecked: the graph points G3 to G5, G14 to G16, G18, G19, G29, G31; the column's fate "from the walk" (G10 as a design source) is void.

So the conclusions that must be rechecked from the engine alone are G11, G15 (the run part), G16, G17, G24, G26, G27 (demo claim), Q1 to Q4 numbers, and the Q5 certainty sentence. The recheck is section (i) of this position; it needs runs, and the load is above the limit.

## 1. WHAT I USE NOW, JUDGED BY READING (nothing of the old lineage)
| Piece | Judgment | Why (read) |
|---|---|---|
| My graph script `paths2/sonnet_graph2.py` | INDEPENDENT | Imports only PyYAML. It parses the recipe's YAML with its own `!include` reader and reads the keys `data_schemas`, `additional_datasets_schemas`, `metadata_schema`, `joins.*.ingredients` (order kept), join steps (`right_ingredient`, `how`, `on`), tier step lists, `analysis_groups.*.plots.*.target_dataset`. Edges: `DS:S -> T1:S -> T2:S`; `T1:I -> T1:J` for each ingredient `I` of join `J`; `T2:X -> T3:p` for a plot targeting `X`. These edge rules are the ones the engine runs [RECIPE FILE `recipe_spec.yaml:34-60` for the keys; engine reading: `orchestrator.py:102-135` (`tier2_parts`, `tier3_parts`, the ingredients of a join)] and were checked against the engine in Part A (DONE, section 9: engine-changed nodes lie inside my "below" sets for 7 places). |
| `utils.recipe_graph` | NOT USED, except in a separate cross-check `paths2/sonnet_crosscheck.py` (DONE: no difference in the nodes and parents; see section 9) | Its docstring says it serves HOME's audit, the lineage, the checker and the cache keys; `cache_keys.py:73,256-265` calls it for the key parts. It reads only recipe keys, but it is shared with the old lineage. |
| `DataOrchestrator.materialize_tier1/2/3` | INDEPENDENT | grep of `orchestrator.py`: no import of `recipe_graph`, `lineage_walk`, `key_drop`, `plan_composer` (only comments name them). They build from the loaded recipe (`ingredient_parts`, `join_parts`, `tier2_parts`, `tier3_parts`). The `keys` argument (made by `compute_data_analysis_recipe_keys`, which uses the graph) decides only whether a STORED table is reused (`orchestrator.py:431-443`); in an EMPTY folder nothing is stored, so everything is built. |
| `recipe_tiers.step_list` | INDEPENDENT | `recipe_tiers.py:65-69`: author steps then `audit_steps`; "THE one reading of a tier for whatever runs"; reads the tier body only. |
| `audit_copy.start_audit`, `add_step` | INDEPENDENT for a `modif_filter` removal | `audit_copy.py:204-208`: the walk (`key_drop`) is consulted only when the step is a column DROP; `_target` (`:166-185`) uses `recipe_tiers` readers and the rule that a tier 2 is writable only if a plot reads the table (the checker's S07/J14, not the walk's fold). It encodes her decisions D-0332 and D-0541 only. It is validated below against a hand-written step. |
| `app/modules/audit_run.run_audit` | NOT independent: NOT USED | `audit_run.py:56,138` builds `recipe_graph` to list tables and plots; `copy_table` (`:164-186`) rebuilds only the tables whose KEY differs from the original and reads the others from the original's folder (`FROM_ORIGINAL`). A wrong key or graph would reuse a stale table and hide the error. |
| The loader `load_data_analysis_recipe` | INDEPENDENT of the lineage | The engine's own reader of the YAML (`config_loader.py`); used only for the engine runs and for the cross-check of my parse. |

**Validation against a step written by hand (V; DONE, result in section 9).** In a scratch copy of the recipe the step `modif_filter sample_id not_in [entity] na keep` is appended to the end of the `steps` list of a schema (MLST), of a join's tier 1 and of a join's tier 2 (files of the scratch copy). The recipe is run normally by the engine; every table and plot table must equal what the audit copy built by `add_step` gives. If not, I report it and use the hand-written form.

**State of the machine.** The runs were made at load 5.8 to 6.6 (section 9). My graph script is pure parsing (milliseconds, imports no repository code); I ran it (`paths2/sonnet_graph2.out`).

## (a) WHAT AN INDEPENDENT PATH IS
**Graph.** Nodes are places (a table at a tier); edges give the direction; roots are the first places of the original files (`T1:<original>`: a source file `DS:` holds no steps); leaves are the results (plots); a joined table is a node with several parents [HER WORDS D-0553: "its more a directional graph with Tx at nodes and branches gives the directions"; "Results (final tables and plots) are leaves no ?"]. [MY GRAPH SCRIPT] on the demo: 12 originals (roots), 16 joined tables, 12 nodes with several parents, 17 plots, 39 root-to-plot paths, 6 tables with no plot below them (`Quality_metrics`, `Detailed_summary`, `FastP_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `AR1_MLST_Serotype_Virulence`).

**A path** is a chain of places from a root to a sink. A plot has one path per original that feeds it. A table no plot reads ends a path too (D-0451: such a table is a place): "path to a result" in her words is a path to a plot; I take every path to a sink, so that a place on a table no plot reads is covered by the same rule [REASONED; her wording says "result"; to confirm].

**Candidate definitions of "independent".**
| Definition | Test on the demo [MY GRAPH SCRIPT] | Fits |
|---|---|---|
| I1: two places are independent iff neither lies below the other | all 12 roots are pairwise independent; two sibling joins of one parent (`T1:MLST_with_metadata`, `T1:ST22_Anchor`) are independent; `T1:ResFinder` and `T1:QA_AMR_per_sample` are not | D-0547 "all the steps after are the following history. and are derived"; D-0553 "at most one place =node ... all paths are derived (~) and cannot be choosen" |
| I2: two roots are independent iff they share no descendant | 21 of 66 pairs of roots share a descendant, so 45 pairs are independent (for example `Summary` and `MLST`); the metadata shares a descendant with 7 roots (`FastP`, `Quast`, `Bracken`, `ResFinder`, `MLST`, `VirulenceFinder`, `APEC`); only `Quality_metrics` and `Detailed_summary` share none with any root | not the exception: D-0547 lets her choose the first T1 of several originals "to speed up things" although they meet later |
| I3: two paths are independent iff they share no node | `MLST -> mlst_bar` and `FastP -> qc_reads_horizontal_barplot` share none; `FastP -> virulence_bar` and `MLST -> virulence_bar` share `T1:ST22_Anchor` and everything below | none of her sentences |
| I4: paths from different roots are independent until they meet at a join | the same pairs as I3, up to the first common joined node | D-0547 "...the step must be duplicated in all those T1 - this because of independent histories"; D-0550 "each independent history is like an independent tree graph" |

**My position [REASONED + MY GRAPH SCRIPT].** The rule the app needs is I1, which is the same thing as "at most one chosen place on any path": two comparable places always lie on one common path, two incomparable places never do. "Independent histories" in her words is I4 as a description: histories are independent where they have not met. Two roots are always I1-independent, so "the exception of the original parents where all can be choosed" is not a second rule: the set of all roots is valid (the script: valid, 0 nested pairs). The metadata's path is independent of a data path before their join (different roots) and meets it at each of the 13 joined tables that read it. Computable with no guessing: yes, from ingredients and plot targets only.

## (b) WHAT IS DERIVED ("~")
**Definition [REASONED].** A place is derived, on a path, when the path holds a chosen place above it. Derived is a property of a (path, place) pair. A joined node below a chosen place through ONE parent is derived on that path and not on its other incoming paths: it cannot be chosen in the same step (it lies below a chosen place, so two places would be on one path: invalid), and its other incoming paths hold no chosen place ("not covered" on those paths). It can still be chosen in a later step [HER WORDS D-0547: "if he want another choice he must add another step audit step later - choosing a different scope"] or, instead of the upper place, alone.
**The valid set, as a check the app can compute [MY GRAPH SCRIPT, own reachability]:** a set S of places is valid in one step iff no place of S lies below another place of S. Equivalent: every path holds at most one place of S.
**Demo [MY GRAPH SCRIPT `sonnet_graph2.out`]:**
| Set | Places | Valid in one step | Plots with every incoming root path covered / none / partly |
|---|---|---|---|
| all original parents with a key | 11 | yes | 15 / 0 / 2 (`virulence_bar`, `virulence_variants`: the APEC root is not in the set) |
| all original parents except the metadata (the first T1 of the retest's run E) | 10 | yes | 4 / 3 / 10 |
| every table but APEC ("remove from all" as decided) | 27 | NO: 35 nested pairs (for example `T1:Summary` above `T1:Summary_phenotype_length_fragmentation`) | 17 / 0 / 0; written in 2 steps at least |
| the 19 defaults with `T1:ResFinder` | 19 | NO: 4 nested pairs (`T1:ResFinder` above its four joins) | 17 / 0 / 0 |
| the same with `T2:ResFinder` | 19 | yes | 17 / 0 / 0 |
| her quality case with `T1:ResFinder` | 17 | NO: 4 nested pairs | 14 / 3 / 0 |
| her quality case, nothing nested (`T2:ResFinder`) | 17 | yes | 14 / 3 / 0 (the 3: `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`) |
| `T1:MLST` with the three MLST join places | 4 | NO: 3 nested pairs | |
| the three MLST join places | 3 | yes | 4 (`mlst_bar`, `year_distribution`, `virulence_bar`, `virulence_variants`) / 13 / 0 |
| `T1:ResFinder` with `T1:QA_AMR_per_sample` | 2 | NO: one below the other | |
| `T1:QA_AMR_per_sample` alone | 1 | yes | 1 / 16 / 0 |
| `T1:ResFinder` with `T1:metadata_schema` (two roots) | 2 | yes | 5 / 3 / 9 |
Minimum number of steps to write each set with no nesting inside a step [MY GRAPH SCRIPT]: the 27 places: 2; the 19 with `T1:ResFinder`: 2; her case with `T1:ResFinder`: 2; her case nothing nested: 1.
**How she removes the row that comes from the metadata side** (the case `T1:ResFinder` together with `T1:QA_AMR_per_sample`, where the metadata is the first table of `QA_AMR_per_sample`). Three valid ways [MY GRAPH SCRIPT for the validity; the fate of the row is UNVERIFIED until the engine runs]: (1) the lower place alone in the same step (it lies on both incoming paths of that joined table); (2) the upper place in one step and the lower in a later step (G21); (3) `T1:ResFinder` together with the metadata root `T1:metadata_schema` (two roots, both incoming paths of the joined table covered; the metadata root is the choice she calls not advised, D-0547).
**What the facts already run say about "derived".** With the first T1 of every original except the metadata (the retest's run E), rebuilt from scratch by the engine, the entity stays in 5 plots [ENGINE RUN run2 part D]; all five are among the 13 plots with an incoming root path that holds no chosen place [MY GRAPH SCRIPT]; 8 other flagged plots lost the entity. So "has an uncovered incoming path" is a necessary sign, not a sufficient one [REASONED: a row can reach a table only through an incoming path; whether it does depends on the join, the engine decides]. The B1 run (a mean over all rows between two nested places gives the table of the upper place alone) checks by hand: mean of 20, 30, 40 is 30, of 10, 20, 30, 40 is 25 [REASONED, arithmetic]. On the demo, rebuilt from scratch [ENGINE RUN `runZ`]: a step at `T1:QA_population_zscore` (before the z-score) changes the `n50_zscore` of 41 of 41 other entities (largest difference 0.064); a step at `T3:qa_population_zscore` (after it) changes 0 of 41.

## (c) HOW THE APP SHOWS IT (structure only, before Apply)
One graph from the roots to the results. A node shows: the table and its tier; its kind (original, joined, result); its parents in order (the first is the base); how many results lie below it and in which analysis groups; its state: chosen, "~" (derived through <parent path>), or none; and for a joined node, "incoming root paths covered: k of n" with the uncovered parents named. It states nothing about the entity [HER WORDS D-0545: only after Apply; D-0501: no warnings about natural consequences; Q5 is open].
```
MLST part (original MLST; the metadata also feeds each joined table)
T1:MLST --+--> T1:MLST_with_metadata (also from metadata)  -> T2 -> mlst_bar, year_distribution
          +--> T1:ST22_Anchor (also from metadata, FastP, ResFinder, VirulenceFinder, APEC) -> T2 -> virulence_bar, virulence_variants
          +--> T1:AR1_MLST_Serotype_Virulence (also from metadata, VirulenceFinder, APEC)   [no plot below]
Chosen: T1:MLST        -> the three joined tables are "~ via MLST"; 1 of 2, 1 of 6, 1 of 4 incoming root paths covered.
Chosen: the three join places -> each is chosen; their results are fully covered; T1:MLST stays free.
Quast part
T1:Quast --+--> T1:Quast_with_metadata (also metadata) -> assembly_quality_dotplot, miaou
           +--> T1:QC_Reads_Anchor (also FastP, Bracken, metadata) -> qc_reads_horizontal_barplot
           +--> T1:QA_L50_integer -> qa_l50_integer
           +--> T1:QA_population_zscore (also metadata) -> qa_population_zscore
Chosen: T1:QA_L50_integer and T1:QA_population_zscore (valid: independent) -> the two quality branches are neither chosen nor "~".
```
[MY GRAPH SCRIPT for the trees and counts.] **Compared with the old walk [OLD LINEAGE CODE, read only]:** `Line.reach` (`lineage_records.py:238-262`, built at `lineage_walk.py:407-417`, read at `:424`) already holds, for a place, the tables and plots below it in the whole recipe, so other analysis groups are in it; it holds no analysis group, no path, no coverage per incoming path and no check of a chosen set.

## (d) THE DEMO MAPPED [MY GRAPH SCRIPT, `paths2/sonnet_graph2.out`]
Roots 12; roots with a descendant shared with another root: all but `Quality_metrics` and `Detailed_summary`; joined nodes 12 with several parents (`ST22_Anchor` 6 parents, `QC_Reads_Anchor` 4, `AR1_MLST_Serotype_Virulence` 4, `QA_fanout_exhibit` 3, the others 2); the metadata is the first ingredient in 4 joins (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`) and a later one in 7; two joins read the metadata alone. Leaves 17. Valid sets for her quality case and for "all analyses": section (b); the quality case without nesting is 17 places (9 joined tables with the metadata, the 11 minus the two quality ones; 2 tables made from the metadata alone; the 4 originals with no metadata join; `T2:ResFinder`; `T1:QA_L50_integer`), "all analyses" with no nesting is 19 places; the 27 and 19-with-`T1:ResFinder` sets are invalid in one step.

## (e) CONSEQUENCES FOR Q2, Q4, Q5 (no answer given for her)
**Q2 (the default).** With her R2 rule a default must be a valid set. The join places of one original are siblings, so they are valid together [MY GRAPH SCRIPT]. Her literal "first T1 of the lineage" for a branch with no metadata join is a root, which lies above every join place of the same original: valid only alone (all paths of that original), not together with the join places. So option (a) of Q2 can only mean "the root, and nothing below it in the same step". Option (b) (the first place only that branch reads: `T2:ResFinder`, `T1:QA_L50_integer`) is valid together with the join places [MY GRAPH SCRIPT: the 19-place set with `T2:ResFinder` is valid and covers all 17 plots]. Option (c) is unchanged.
**Q4 (the three forms).** The 27 places as decided are NOT valid in one step (35 nested pairs); they can be written in 2 steps (the roots first, then the joined tables, which is allowed across steps) [MY GRAPH SCRIPT]. The 11 uppermost places are valid ("the exception" is a consequence of the rule). The 19 defaults are valid only with `T2:ResFinder`, not with `T1:ResFinder`. Her words: "the only way to choose several places must be the case of the independent history - the original T1 steps of independent histories" [HER WORDS D-0549]. The earlier statement that all three forms give identical plot tables [UNVERIFIED] is rechecked in Part D.
**Q5 (can remain here).** Her answer adds a structure-only fact the app can show without claiming anything about the entity: for a joined node, how many incoming root paths hold a chosen place and which do not. It needs no join kind and no `Hop`. Options become: (a) nothing before Apply; (b) the sentence "can remain here" from the kind and side of the join (rests on the old walk: UNVERIFIED); (c) after Apply only; (d) NEW: show the coverage per incoming path (structure only). Whether (d) breaks "no warnings about the natural consequences" (D-0501) is hers.

## (f) WHAT SHE MAY BE MISSING
1. **The exception is not complete coverage.** The set of all roots is valid, but without the metadata (not advised) it leaves the metadata paths uncovered: 4 plots fully covered, 3 none, 10 partly [MY GRAPH SCRIPT]. With all 11 roots and no APEC, 2 plots stay partly covered. Why: a joined table has several incoming paths and each root covers only its own. How: show the coverage per incoming path. She would see "1 of 2 covered" on `MLST_with_metadata` after choosing `T1:MLST`.
2. **Derived is per path, not per node** (section b). Alternative: a node is "~" only when all its incoming paths are covered, "partly" otherwise.
3. **Tables no plot reads** (6 on the demo) end paths; whether they count as "results" is not in her words.
4. **A parent feeds several graphs** (section g).
**Shapes of the demo that make the rule harder (facts only) and what an author can write differently TODAY, within today's format [RECIPE FILE]:**
| Shape | What an author can write today instead (no change proposed) |
|---|---|
| `ST22_Anchor` has 6 parents | a join may list fewer ingredients and each plot may target a smaller join; or keep it: the place is one node in 6 trees (one step, written once) |
| one original joined with the metadata in 2 to 4 tables (MLST 3, Quast 4) | several plots may target ONE joined table and give each plot its own `tier3` steps (`recipe_spec.yaml:54`: `tier3` is a plot key; `MLST_with_metadata` already serves 2 plots); then one metadata join per original |
| the metadata first in 4 joins | the author chooses the order of `ingredients`; the first is the base (`recipe_graph` docstring; engine: the first ingredient starts the join) |
| two tables made from the metadata alone | a plot may target the schema itself (`amr_heatmap` targets `ResFinder`), with a `tier2` on the schema (`ResFinder` has one) |
I do not propose changing the demo.

## (g) A PARENT REUSED IN ANOTHER GRAPH
Her note [HER WORDS D-0555]: "if several parents are choosen the step applied must be applied in each T1 comming from the parent - and that is where it can be a got you if the parent is reused in another directed graph - so we need here to have the 2 directed graphs that go from the same parents - because both will be affected."

**(1) "Each T1 coming from the parent": two readings (not chosen).** [MY GRAPH SCRIPT]
| Reading | What is written | MLST | ResFinder | Quast | metadata |
|---|---|---|---|---|---|
| 1: the parent's own first place | one step at `T1:<parent>`; every place below is derived | 1 place (`T1:MLST`) | 1 (`T1:ResFinder`) | 1 | 1 |
| 2: the first place of each table that reads the parent | one step at the end of tier 1 of each joined table that reads it, and at the tier 2 of the parent when a plot reads it | 3 (`MLST_with_metadata`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`) | 5 (4 joins and `T2:ResFinder`, read by `amr_heatmap`) | 4 | 13 |
Reading 2 is a valid set (the join places are siblings) and is the set of the join places of Q2. Both are valid in one step; they differ in what they cover when a joined table has another parent (section b).

**(2) "The directed graphs that go from the same parents" so that the app computes them [REASONED + MY GRAPH SCRIPT].** For a chosen set S: down(S) = every node reachable from a member of S in the WHOLE recipe; its results R(S) = the plots in down(S). One graph = down of one chosen place. "Another graph" than the one the user started from: any result of R(S) that is not the plot the user started from, shown by (i) another analysis group, (ii) another joined table, (iii) a part of the recipe the user did not open. Two graphs share a parent only through the metadata when their results share no root but the metadata: on the demo, of 97 pairs of results in different analysis groups, 45 share only the metadata and 17 share another parent.

**(3) The demo mapped [MY GRAPH SCRIPT, `sonnet_graph2.out`].** Results below each parent, by analysis group: `FastP` 3 results in 2 groups; `Quast` 5 in 3 (Quality Control, Cat, QA Canaries); `ResFinder` 5 in 2 (Results, QA Canaries); `MLST` 4 in 1; `VirulenceFinder` 3 in 2; `Summary_quality` 2 in 2; the metadata 13 in 4; `Quality_metrics` and `Detailed_summary` 0. Six parents feed results in more than one group: `Summary_quality`, `FastP`, `Quast`, `ResFinder`, `VirulenceFinder`, `metadata_schema`. From one plot: `mlst_bar` (parents `MLST`, the metadata): 12 other results lie below its parents, none inside its own lineage; `amr_heatmap` (parent `ResFinder`): 4 other results (`virulence_bar`, `virulence_variants`, `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`); `qc_reads_horizontal_barplot` (parents `Bracken`, `FastP`, `Quast`, the metadata): 13 other results.
What a step at each shared parent changes in each graph [ENGINE RUN `sonnet_engine_run2_A_to_E.py`, part C, each variant built from scratch in its own empty folder, entity 10668076]: `T1:MLST`: 4 plots change, all in group Results (below it: 4); `T1:ResFinder`: 4 change (`amr_heatmap`, `qa_amr_genes_per_sample`, `virulence_bar`, `virulence_variants`; groups Results and QA Canaries) of the 5 below it (`qa_fanout_rows_per_sample` keeps the entity: the metadata is the first table of `QA_fanout_exhibit`); `T1:FastP`: 1 changes (`qc_reads_horizontal_barplot`) of 3 below (`virulence_bar`, `virulence_variants` keep the entity: the metadata is the first table of `ST22_Anchor`); `T1:Quast`: 5 change in 3 groups (Quality Control, Cat, QA Canaries); `T1:VirulenceFinder`: 3 change in 2 groups; `T1:metadata_schema`: 13 change in 4 groups. No plot outside "below" changed in any run.

**(4) How the app shows it before Apply (structure only).** For every chosen place: the results below it in the whole recipe, grouped by analysis group, with the results outside the plot the user started from marked; for a joined node the coverage per incoming path. The old walk's `Line.reach` already holds the whole-recipe sets of tables and plots below a place (`lineage_walk.py:407-417`; OLD LINEAGE CODE, read only); it has no analysis group and no per-path coverage.

**(5) Consequences.** Q4: "Remove from all the data" writes at every original parent, so every graph from every parent is affected by definition; the list of results below each written place is the information. Q5: the coverage per incoming path is the structure that says where a parent's graph meets another parent's graph. **Gotcha wording (PROPOSAL, not decided).** For users: "A step written at an original table, or at a table that other tables read, changes every result below it in the whole recipe, also results in other groups that you did not open. Before you confirm, read the list of results below each chosen place." For authors: "When one original table feeds several joined tables or several groups of plots, a step written at that table reaches all of them. If some results must stay unchanged, give them a joined table of their own."

## (h) INVESTIGATION: PARENTS AND SHARED NODES FEEDING MORE THAN ONE GRAPH
Her order [HER WORDS D-0556]: "I think this needs to be investigated by the reviewer, and what would be the possibilities to avoid errors - and if possible to avoid errors in complex solutions then fine but we need to be sure what can be done before we choose". Her rule idea (as quoted by the review session): "or one rule could be that if we need this we need to reimport the original data - so that the original parents -> T1 cannot be shared - can cost a bit of recompute (because we have duplicated steps) but can avoid headeaches - and those cases are likely not to occur often". Nothing is chosen here.

**1. Catalogue of what can go wrong.**
| # | What | Evidence |
|---|---|---|
| E1 | A step at a shared parent reaches results in graphs the user did not start from | [MY GRAPH SCRIPT] 6 of 12 parents feed more than one group; from `mlst_bar` 12 other results; [ENGINE RUN part C] `T1:Quast` changes plots in 3 groups, `T1:metadata_schema` in 4 groups, none outside "below" |
| E2 | A joined node reached through one parent only still has uncovered incoming paths | [MY GRAPH SCRIPT] after `T1:MLST`: `MLST_with_metadata` 1 of 2 covered, `ST22_Anchor` 1 of 6, `AR1` 1 of 4; fate of the entity UNVERIFIED |
| E3 | A computation over all entities lies between two places: upper and lower give different results | [REASONED, arithmetic] mean 30 or 25 on the B1 recipe; the demo has `QA_population_zscore` (tier 2, mean over all rows) and `QA_aggregated_no_key` (tier 2, grouping by country and year) [RECIPE FILE tier 2 files]; their results change for every other entity when a step lies before tier 2 (retest: UNVERIFIED) |
| E4 | The metadata is a parent of 13 joined tables in 4 groups | [MY GRAPH SCRIPT] a step at its root reaches 13 results; she calls it not advised (D-0547) |
| E5 | Tables no plot reads receive the step too | [MY GRAPH SCRIPT] 6 on the demo; visible only in the export (D-0457) [REASONED] |
| E6 | Two source tables on one file: does a step at one reach the other's graph? | [ENGINE RUN part B] no: a step at `T1:Summary` changes 1 plot (`phenotype_genome_length_fragmentation`); at `T1:Summary_quality` 2 plots (that one and `qa_sequence_type_missing`); at both, the same 2: the two graphs stay separate although the file is the same |
| E7 | A parent without the key (APEC) cannot receive a removal by key; the joined tables it feeds keep an uncovered path | [MY GRAPH SCRIPT] with all 11 roots, `virulence_bar` and `virulence_variants` stay partly covered; [ENGINE RUN part E] `APEC_STEC_virulence_genes` is the only tier 1 without `sample_id` |

**2 and 3. Possibilities, each with what it prevents, does not prevent, what the author and the user see, and complex recipes.**
| Possibility | Prevents | Does NOT prevent | Author sees | User of the audit sees | Complex recipes (6 originals; a parent in several joins; metadata first; computation over all entities) |
|---|---|---|---|---|---|
| X: show every graph from the chosen parent before Apply (all results below, by group, the ones outside the start plot marked) | the surprise of E1, E4, E5 | E3 (a change whose effect depends on what lies between places); the fate of the entity | nothing new | the list of results below each chosen place | works for all four: it is a computation on the recipe |
| G: coverage per incoming path of each joined node | the unseen uncovered path (E2, E7) | E3 | nothing | "k of n incoming paths covered", named | works: it counts paths (a node of 6 parents shows 6) |
| K: a step is written only at a place whose whole reach was shown and confirmed | an unseen reach | a wrong confirmation (D-0543: the app cannot prevent a wrong decision) | nothing | one confirm step listing the reach | works; the list can be long (metadata: 13 results) |
| A: after Apply, a run names the results changed outside the graph the user started from | an unnoticed change (E1) after the fact | a change before Apply | nothing | a list of changed results with counts | works for all; it is the measure-and-log slice (D-0536) |
| Y-advice: a parent feeds one graph only; a second use is a reimport of the original data (a second source table reading the same file), as an advice of the recipe check | E1 and E2 by construction: each copy is a root of its own tree | E3; a joined table of several roots (its place is still one node in several trees); the metadata exception | a second source table per use, its own `input_fields` (the demo includes the same `input_fields` file twice: `1_test_data_ST22_dummy.yaml` lines 25 and 36), and its own tier 1 steps | more roots to choose: "remove from all" must choose every copy (valid: roots are independent) | 6 originals: six roots, one per use; parent in several joins: one copy per join (MLST 3, ResFinder 4+1, Quast 4, FastP 3, VirulenceFinder 3, metadata 13); metadata first: its own copy; computation over all entities: unchanged |
| Y-refusal: the same rule refused by the recipe check | the same, forced | the same | the check refuses a source table read by two tables | the same | the same; refusing the metadata (13 copies) is the question |
| Z: Y plus X | E1 shown for the cases the author did not split | E3 | as Y | as Y plus the list | as Y |
| Others found: N (the audit step names every graph and result it reaches before Apply, the same data as X, written into the audit record); an unchanged-result check after Apply (A) kept in the log | what X/A show, kept | | | | |

**The reimport facts, read [RECIPE FILE / code].** (i) The demo already has two tables on one file: `Summary` and `Summary_quality` both name `test_data_Summary_20260307_105756.tsv` (`1_test_data_ST22_dummy.yaml` lines 22 and 33). (ii) The engine finds the file of each table by its id: in the development lookup (`data_lookup: data_analysis_recipe_paths`) it reads the table's own `source.path`, so two tables may name one file; in the production lookup (`by_dataset_id`) the recipe's path is ignored and the table reads `<dataset id>.tsv` in the raw-data folder, so a second source table needs a second file named by its id, with the same content (`orchestrator.py:173-196`, `:178-180`; `config/deployment/pipeline_test/pipeline_test.yaml:19`). (iii) Cache keys: the content hash of a file is made per dataset id (`cache_keys.py:139-147`); two ids on one file give two equal content hashes, and two different table keys (the key holds the table's definition: `tier1_key`, `:284-289`). (iv) The batch hash lists every id (`cache_keys.py:150-153`): adding a copy changes it. (v) The Data Import panel treats tables on one file as one: replacing the file replaces it for every table that reads it, and a candidate is refused unless every such table can read it (`data_import_check.py:83, 177-178`). (vi) Recompute: each copy is ingested and its tier 1 is run separately; the user waits for as many builds as copies at the first opening (the progress line of D-0334). (vii) "Does the rule apply to the metadata": under Y it becomes 13 source tables on one file (one per joined table that reads it), or the one exception; with the exception a step at the metadata root reaches 13 results in 4 groups (E4).

**4. What can be done (feasible / partly / not), with evidence.**
| Possibility | Verdict | Evidence |
|---|---|---|
| X | feasible | everything it needs is computed by my script from the recipe keys [MY GRAPH SCRIPT] |
| G | feasible | same; counts paths [MY GRAPH SCRIPT] |
| K | feasible | a confirm step over the output of X [REASONED] |
| A | partly | the comparison of tables is what the engine runs give (Part C will show it); the slice is not built [REASONED] |
| Y as advice | feasible | the recipe check already has the ingredient lists; counting the readers of a source table needs nothing else [REASONED: `recipe_check.py` J04 reads `ingredients`]; copies are possible today (the demo's `Summary`, `Summary_quality`) |
| Y as refusal | partly | possible to write; it would refuse the demo itself (MLST in 3 joins) and needs an answer for the metadata and for a join of several originals |
| Z | partly | X is feasible, Y as above |
Which points were run and which are reasoned: E1, E6, E7 are ENGINE RUNS (parts B, C, E); the reimport facts (i) to (v) are read from code; the possibilities table and the verdicts are REASONED, except that X and G are computed by my graph script. Not run: the reimport rule applied to one original in a scratch copy (the Opus partner's share).

**5. The question for her as it would be put.**
"When one original table feeds several joined tables or several groups of plots, a step written at it changes all of them, also those you did not open. What do you want the app to do?
(a) Show, before Apply, every result below each chosen place, by group, and, for each joined table, how many of its incoming paths hold a chosen place. You would see, for `T1:ResFinder`: 5 results in 2 groups; for `T1:MLST`: `MLST_with_metadata` 1 of 2 incoming paths covered, `ST22_Anchor` 1 of 6, `AR1_MLST_Serotype_Virulence` 1 of 4.
(b) Your rule: a parent feeds one graph only; a second use is a second source table that reads the same file, written as an advice of the recipe check. You would see, on the demo, MLST read by 3 source tables, ResFinder by 5, the metadata by 13, and one root per copy in the tree; the first opening builds each copy; the recipe check says it for every source table read twice.
(c) Your rule as a refusal: the recipe check refuses a source table that two tables read. You would see the demo refused until MLST, ResFinder, Quast, FastP, VirulenceFinder and the metadata are split.
(d) (a) and (b) together.
(e) After Apply, a list of the results that changed outside the plot you started from (from the measure and the log).
(f) Neither: say what you meant."
**Lean (a lean, not a decision):** (a) with (e): they work in every shape of the demo, change no recipe and show the whole reach; (b) as an advice stays possible for authors who want separate graphs, but it does not remove the case where one joined table has several parents, and it does not remove a computation over all entities between two places. The recompute of (b) is a fact of that option: each copy is built once at the first opening; the user waits for that many builds.

## (i) RECHECK OF EARLIER POINTS (by the engine alone and my own graph)
Method for every row: the recipe is run by the engine (all tables and plot tables rebuilt FROM SCRATCH, each variant and the original in its OWN empty folder, no stored table reused, compared by hash), places are written with `add_step`, the graph is my own parse. Status DONE = run in section 9 (load 5.8 to 6.6).
| Point (agreed list) | Old-code dependence | Recheck | Status |
|---|---|---|---|
| G11 "~" is not "gone": run E leaves the entity in 5 plots | places by the old place list; `run_audit` | Part D, set E: plots where the entity stays, against the retest's 5; and against the 13 plots with an uncovered path in my graph | DONE: AGREES. Set E rebuilt from scratch: 14 plots changed, the entity stays in 5 (`qa_amr_genes_per_sample`, `qa_year_label`, `qa_facet_by_mapping`, `qa_fanout_rows_per_sample`, `qa_population_zscore`), all inside my 13 flagged plots [ENGINE RUN run2 D]. |
| G15 run R2 (her case, nothing nested): 14 changed, stays in 3, equal to B3 | `run_audit`; offered list | Part D: R2 and B3 plot tables equal | DONE: AGREES. The nothing-nested set: 14 changed, the entity stays in exactly the 3 quality plots; its plot tables equal those of the nested B3 [ENGINE RUN run2 D]. |
| G16 run A: entity stays in `amr_heatmap`, `qa_l50_integer` | `run_audit` | Part D, A3 with `T2:ResFinder` and Part A for `T1:Quast` | DONE: AGREES. The 19 defaults with `T2:ResFinder` remove the entity from all 17 plots; with the first T1 of every original except the metadata (set E) the 4 fully covered plots (`amr_heatmap`, `phenotype_genome_length_fragmentation`, `qa_sequence_type_missing`, `qa_l50_integer`) lose it [ENGINE RUN run2 D]. The retest's run A itself (without `amr_heatmap` and `qa_l50_integer` places) was not re-made: it served no stated hypothesis. |
| G17 `T1:Quast` hits the quality plots; run E | `run_audit` | Part C `T1:Quast`; Part D E | DONE: AGREES for `T1:Quast`: 5 plots change in 3 groups, including the quality plots and `miaou` [ENGINE RUN run2 C]; the emptied columns of `qc_reads_horizontal_barplot` were not re-checked (not registered). |
| G24 (MLST 3 places, z-score 41 of 41, 19 to 18) | `run_audit` | Part C `T1:MLST`; the z-score and count are tables of `QA_population_zscore` and `QA_aggregated_no_key` compared by the same hashes (extend Part C with the counts when run) | PARTLY DONE: `T1:MLST` changes 4 plots in 1 group (C); the z-score: 41 of 41 other entities change with the step before it and 0 after it (run Z, largest 0.064). The count 19 to 18 of `qa_aggregated_no_key` was not re-checked. |
| G26 three forms of "remove from all": identical plot tables | the OFFER list from `remove_from_all.describe`, `apply`, `run_audit` | Part D: UPPER, A3 with `T2:ResFinder`, ALL27 plot tables equal | DONE: AGREES. UPPER (11), the 19 defaults with `T2:ResFinder` and the 27 places in one list: 17 plots changed, entity in none, the 17 plot tables equal [ENGINE RUN run2 D, from scratch]. The differing exported tier 1 files stay by construction, not compared. |
| G27 demo claim "B3 = the six-place result" | retest | Part D: R2 equals B3 | DONE: AGREES. Her case with `T1:ResFinder` (nested) and with `T2:ResFinder` give equal plot tables [ENGINE RUN run2 D]. |
| Q1 to Q4 demo numbers | retest, Opus runs | Part D | DONE for 14 changed / stays in 3 / 17 plot tables equal; the other numbers of the questions that came from the retest and are not in this table are not re-checked. |
| Q5 "certain only at a join on the entity key" | `lineage_walk` P12, `Hop` | not rechecked: the sentence is withdrawn from this position; replaced by the coverage per incoming path (structure) | withdrawn |
| the count of 27 places and "each holds the key at the end of tier 1" | `remove_from_all.describe` | the count: 12 schemas + 16 joins - APEC = 27 by arithmetic on the recipe keys [MY GRAPH SCRIPT]; the key at the end of each tier 1: Part E, an engine run of every tier 1 (the columns of each stored frame) | count done; key DONE [ENGINE RUN run2 E]: only `APEC_STEC_virulence_genes` has no `sample_id` in its tier 1 |
| the tree property on 50 recipes | `recipe_graph` | demo: my own graph, 0 nodes with two parents inside the set reachable from one root [MY GRAPH SCRIPT, `sonnet_graph2.out`, line "TREE PROPERTY"]: DONE for the demo; the other 49 recipes: rerun `own_graph` on each (pure parse) | demo done; the other 49 recipes: not re-run (registered as planned after the cross-check) |
| G3 history is a tree; G5 shared place counts (6, 4, 4); G14 tiers shared today; G15 `T1:ResFinder` has 5 children; G18 two metadata-only tables; G19 join places per original; G29 "7 tables"; G31 5 and 11 steps | `recipe_graph` / retest map | recomputed from my own parse [MY GRAPH SCRIPT]: `ST22_Anchor` 6 parents, `QC_Reads_Anchor` 4, `AR1` 4 (and the node list of several parents); `T1:ResFinder` has 4 joined tables and `T2:ResFinder` as children; `QA_year_types` and `QA_aggregated_no_key` have the metadata as only ingredient; the 7 tables that read an original that has a `<original>_with_metadata` table (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_L50_integer`); the ResFinder tree holds 5 independent places and 11 joins read the metadata in her case; the joins that read the original with the metadata: FastP 3, Quast 3 (+ `QA_L50_integer` without it), MLST 3, ResFinder 4 | DONE [MY GRAPH SCRIPT]; cross-check DONE: the same 85 nodes and the same parents as `recipe_graph` (section 9) |
| the earlier claim that `run_audit` and a from-scratch build agree | `run_audit` reuses stored tables by keys | Part R of `sonnet_engine_runs.py`: one case (`T1:MLST`), `run_audit`'s route against a from-scratch build in an empty folder | DONE: AGREES for `T1:MLST`: 0 of 17 plot tables differ; `run_audit`'s affected plots are exactly the plots that differ (section 9) |

## (j) EVERY STEP AFTER A CHANGE IS RECOMPUTED (her requirement D-0560)
Her words: "we need to ensure that everystep after a change in a place is recalculated - that would otherwise produce errors indeed ...".

**REQUIREMENT (plain words, for the design).** Every place below a change is recomputed from its parents after the change. A table is never read from a table stored before the change unless the app can prove that the stored table was built from the same definition, the same data and the same audit steps. If it cannot prove it, it rebuilds.

**What the engine does today (the answer to "is the audit run's skip safe")** [ENGINE RUN `sonnet_partR.py`, each variant and the original built from scratch in its own empty folder; entity 10668076].
1. For one place of each kind the three sets are EQUAL: below (my graph), key changed (the app's key functions), content changed (from-scratch rebuild).
| Place | below | key changed | content changed | finding | defect | key changed, not below |
|---|---|---|---|---|---|---|
| `T1:MLST` (tier 1 of an original) | 12 | 12 | 12 | none | none | none |
| `T1:MLST_with_metadata` (tier 1 of a joined table) | 4 | 4 | 4 | none | none | none |
| `T2:MLST_with_metadata` (tier 2 of a joined table) | 3 | 3 | 3 | none | none | none |
| `T2:ResFinder` (tier 2 of an original that a plot reads) | 2 | 2 | 2 | none | none | none |
| `T3:mlst_bar` (a plot's own tier 3) | 1 | 1 | 1 | none | none | none |
Why it holds: the tier 1 key holds the audit steps of the table and of everything upstream (`a1`), the tier 2 key is the tier 1 key plus its own steps (`a2`), the plot key is the tier 2 key plus its own steps (`a3`) (`cache_keys.py` docstring lines 14-28). This is shown for 5 places on one entity on the demo; it is NOT shown for every place or every recipe.
2. `run_audit`'s skip of a plot with an unchanged key is safe in the case run (`T1:MLST`): its plot tables equal the from-scratch ones (0 of 17 differ), and its "affected" plots are exactly the plots that differ.
3. **Stale-table probe.** A wrong table with the OLD key at the audited table's name is never served: the key check (`transformer/anchor.py:109-118`, "never reused by file name alone") refuses it, and both the normal build and `run_audit` rebuild. A wrong table stamped with the NEW key IS served, by the normal build and by `run_audit` (it is read as "audit store"). So a wrong table is served exactly when (i) its footer key equals the current key and (ii) it lies at the path where the current key is looked up. That can happen only if a key does not change when it should (a dependency missing from a key part: the fail-safe in `cache_keys.py:42-47` makes a part COARSE, so an extra rebuild, when the graph cannot say), or if someone writes a table with a key that is not its own. A table written by the app itself is written under a temporary name and renamed (`anchor.py:129-135`), so a half-written table is not served.

**What the tests of the new structure must contain, to prove the requirement.**
1. For EVERY place of a recipe (not five), write an audit step, rebuild everything from scratch in empty folders, and assert: every node below the place has a changed key; every node whose rebuilt content differs has a changed key; no node outside "below" has a changed key. The "below" set is computed from the recipe's own keys by the new structure code, not from the code under test.
2. A stale probe in the test: store, under the audited key's file name, a table built BEFORE the step and stamped with the OLD key; run the audit; assert it equals the from-scratch table. A test that can fail: break the key (leave `a1` out of the tier 1 key) and the test must fail on a below node whose key did not change.
3. Recipes in the tests that have: a join of several originals, a table read by joins and by a plot, a plot with its own tier 3, a tier 2 that computes over all entities (the demo's z-score: a step before it changes the `n50_zscore` of 41 of 41 other entities, a step after it 0 of 41).
4. An equality ("0 of n differ") is accepted as evidence only when both sides were rebuilt from scratch in separate empty folders; the test says so.

## 8. WHAT REMAINS TO RUN
Not run: the tree property on the other 49 recipes with my own parse (pure parsing, registered as planned); the reimport rule applied to one original in a scratch copy (the Opus partner's share); the count 19 to 18 of `qa_aggregated_no_key`; the emptied columns of `qc_reads_horizontal_barplot` for `T1:Quast`; export of the tier 1 files under the three forms of "remove from all"; the tests of section (j) as general tests over every place of every recipe.

## 9. RESULTS OF THE RUNS (all registered before in `RUN_REGISTER_sonnet.md`, observed results added there; runs at load 5.8 to 6.6)
All from scratch, each variant in its own empty folder. R1, R2, R0, V, X1, A, B, C, D1 to D4, E and Z: AGREE with what the design expected; no contradiction, no finding. Details are in the register and in `paths2/sonnet_partR.out`, `run1.out`, `crosscheck.out`, `run2.out`, `runZ.out`. Time: 13 rebuilds of the whole demo (28 tables, 17 plots) took 14 s; 22 rebuilds 33 s: about 1 to 1.5 s for one from-scratch rebuild of the demo with its small data; the time on a user's data is not measured.
