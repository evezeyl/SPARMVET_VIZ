# Opus round 2: my answer to SONNET_position_1 (S1 to S20), joint wordings, agreed and open lists

Read on `dev` `febc506f`. I could not run anything: the load was 17, then 35 (cap 10). Every check below is by reading code at file:line; where a fact needs a run, I say so. Her words come only from the evidence fields of the ledger. "Retest" = `tmpAI/coordinator/whole_picture/RETEST_her_scope.md`.

## 1. Point by point

**S1 (place) AGREE.** Verified:
- `parse_place` is at `audit_copy.py:106`.
- The refusal of tier 2 of a table no plot reads is at `audit_copy.py:177-179`.
- Empty tiers collapse (D-0346).
- A source file holds no step list (D-0332; `lineage_walk.py` header P1b).

**S2 (original table) AGREE.** Same as my P1.

**S3 (history = a tree) AGREE, one CHANGE.**
- Verified by reading: a join's T1 has the T1 of its ingredients as parents (`recipe_graph.py:579-580`). J04 refuses an ingredient that is not a schema (`recipe_check.py:867`) and an ingredient listed twice (:869). T2 and T3 have one parent each (:574-585).
- So inside the forward reach of one `DS:` node, every node has exactly one parent: a tree, for every recipe that passes the check.
- Your branch counts (`virulence_bar` 6, `qc_reads` 4, `mlst_bar` 2, `amr_heatmap` 1) match my map.
- CHANGE: "form 3 can create a diamond" holds only if a join may read a derived or joined table, which reopens D-0344. Form 3 as proposed (each derived table made `from:` ONE table; joins of source tables only) keeps the tree.

**S4 (derived place, computed, never stored) AGREE.** The library already follows this rule: counts are "never stored beside them, so two numbers cannot disagree" (`lineage_records.py:10`, citing D-0195 and D-0316).

**S5 (independent places) AGREE.** It is the rule both readings share; see J8.
- Under "one place per tree", a shared place consumes the one place of EVERY tree it belongs to.
- Example: `T1:QC_Reads_Anchor` would be the one place of the FastP, Quast, Bracken and metadata trees.
- So "one per tree" also needs the independence rule: `T1:FastP` (FastP tree) together with `T1:QC_Reads_Anchor` (chosen for the Quast tree) is nested.

**S6 (shared place) AGREE, one nuance.** A look-up table without the key (APEC) makes `ST22_Anchor` and `AR1` "shared" with a tree that a removal by key never reaches. For a removal by key, only the trees of originals that hold the key count.

**S7 (metadata join) CHANGE.**
- The tier rule is in force today. ST05 refuses every join action (`polars_join`, `join_asof`, `join_where`: `action_names.py:63-66`, TIER1_ONLY) in tier 2 or tier 3 (`recipe_check.py:714-715`). So a metadata join can only sit in tier 1.
- What is not built: a rule specific to the metadata (none is needed for the tier), and any rule on the side. Rule, advice or documentation for the side is NOT decided (D-0550).
- D-0510's own line holds the wrong fact "the recipe check ... has no rule that refuses a join step in tier 2". That is a records error (rule H); `WHOLE_PICTURE.md` question 27 already says so.
- The rest AGREES with my P7: the base is the first ingredient (`recipe_graph.py:27, 322`); the kind is read from `how`.

**S8 (default place) CHANGE of wording.**
- "Named as a default" is a reading (mine too), not D-0531's words. Her default comes from D-0549: "in manycase I would select the scope of where original T1+ metadata are joined". The second half comes from D-0550: "the first T1 of the lineage when no metadata join".
- "One default per branch, not per tree" is the R2 reading, which is open (O1).

**S9 (result) CHANGE.**
- The direction is decided, in her words: "so a plot entry actually should be a result_entry with either plot or table no?" and "yes the result is the last stage" (D-0485); D-0487 adds "we shuold be able to export the table that is as result also".
- The form and the keys are not decided (D-0496, D-0514 to D-0517).
- AGREE that a table no plot reads is a place (D-0451), not a result.

**S10 (test against the retest) AGREE on the facts, three CHANGES.**
- (i) Under R1 her case IS expressible, in several steps: "if he want another choice he must add another step audit step later" (D-0547). Read "not expressible in ONE step with R1".
- (ii) For `amr_heatmap` the place that belongs to that branch alone is `T2:ResFinder`. Plots read the T2 of their target and joins read the T1 of their ingredients (`recipe_graph.py:579-585`), and no other plot targets ResFinder (my map). `T3:amr_heatmap` is also a place (a plot's own line, D-0346). Both reach the same single plot.
- (iii) "The metadata tree has 42 places": 42 NODES (the DS node, 14 T1, 14 T2, 13 T3). There are fewer places, because empty tiers collapse (D-0346).

**S11 (the unit is the branch) PARTLY AGREE.**
- AGREE: J8 (no chosen place downstream of another) is the core rule. R2 is J8 alone; R1 is J8 plus "at most one place per tree".
- DISAGREE that the design adopts R2. Her literal words are R1: "the user can only choose one scope per original T1" (D-0547); "the only way to choose several places must be the case of the independent history - the original T1 steps of independent histories" (D-0549). This is O1, for her.
- Your question, "is there a reading of N10 where R1 is right?": yes, two arguments.
  - When a decision applies to a history as a whole (her resequenced case: "remove this sample everywhere", D-0415), R1 says it with one place per tree. A different treatment of some branches is then another step, by her own words.
  - R1 keeps "the lineage/history on the audit step" (D-0547) to one node per tree.
- Both readings are coherent.

**S12 (no new key) AGREE, with two conditions and one limit.**
- The conditions are rules on how a recipe is written, not new keys:
  - (a) the metadata must be declared in `metadata_schema`: the graph knows "the metadata" only by its block (D-0511: information about the entities held elsewhere is a recipe-making matter);
  - (b) a removal by key needs the declared entity key (`is_entity_key`).
- The limit, to your "a fact the graph cannot give": whether the entity's ROWS survive a step (an aggregation without the key; a key rewritten) is the column's fate (S15b, the engine's plan), not structure. S16's mark also needs the walk's key link at the join, not only the graph.

**S13 (rules, not keys)**
- (a) CHANGE, as S7: the tier rule holds through ST05.
- (b) AGREE: D-0523; the move waits for the one move (D-0525).
- (c) AGREE: the spec sentence is not decided (D-0513).
- (d) AGREE: a question for her.

**S14 (tiers as shared steps) AGREE, and I CHANGE my P3 to your precision.**
- Today a table's T2 is shared by several plots, and a source's T1 by the joins that read it. Several T2 on ONE table's T1 do not exist without derived tables.
- Your check, "does N2 require form 3?": no.
  - Her case of D-0517, "one final result could be used on T2a but T2a could be used to produce one T3a for another final result", is possible today: two plots target the same table, and one has its own tier 3 steps (`recipe_graph.py:582-585`).
  - So N2 does not require form 3, and the scope rule is designed on the general graph: AGREE.

**S15 (two pure functions) AGREE.** Add: the structure function also gives, per branch, the facts of each join on it (kind, side, the key link). S16, if she wants it, reads these with the column fate.

**S16 ("~" and "can remain") AGREE on the meaning, facts below, the showing is OPEN (O4).**
- AGREE: "~" means "the step is upstream of this place", not "the entity is gone here".
- Your check: `Hop.join_how` and `Hop.join_side` (`lineage_records.py:146-157`) give, per column hop, the kind and the side. For a join ON the entity key, the walk links both key columns (`lineage_walk.py` header P12). At such a join:
  - chosen place on the RIGHT side of a LEFT join: the entity's base rows stay, with the right columns empty (certain);
  - INNER or SEMI join: its rows are dropped (certain);
  - ANTI, RIGHT, FULL or self-join: not yet followed (red, D-0460).
- For a join not on the key (APEC, joined by gene) nothing is certain, so nothing is marked.
- A later step (an aggregation without the key) can still change what "remains". So "can remain" is certain only AT a join on the entity key, for left, inner and semi joins.
- Whether to SHOW it before Apply is hers (O4).

**S17 (default where her rule is silent) AGREE that it is silent, CHANGE on the default.**
- The facts: retest A (`amr_heatmap`, `qa_l50_integer` keep the entity complete); `QA_year_types` and `QA_aggregated_no_key` are made from the metadata alone.
- Her words "(so same level except there is no metadata joined)" (D-0550) point, for `qa_l50_integer`, to `T1:QA_L50_integer`: a table at the level of the joined tables. That is your candidate.
- For `amr_heatmap` there is no table at that level. Her literal "first T1 of the lineage" is `T1:ResFinder`, which is nested above the 4 join places.
- For metadata-only tables her literal rule gives `T1:metadata_schema`, which she calls "not advised" (D-0547).
- So the default there is hers: O3. Your candidate and "none ticked" are options, not a design.

**S18 ("remove from all the data") AGREE on the facts, CHANGE "redefine" into a question (O5).**
- Verified: `_chosen_places` has no check of nested places (`remove_from_all.py:292-307`); `ticked=None` writes every reached place (PROVISIONAL P8); 27 places are offered (retest, section 0).
- It conflicts with N10 when one step holds nested places.
- But the redefinition is explicitly NOT decided: "the redefinition of 'remove from all the data' (D-0416) in this direction is a reading of the review session, to be asked once when the plan is checked" (D-0550).

**S19 (one decision, several steps) AGREE, a proposal, and one question (O6).**
- Proposal: the grouping goes in the audit log, one event per decision with its places and the ids of the steps written. It does not go in the audit recipe, whose keys are decided (D-0332, D-0354; D-0542: "yes correct").
- Question: "Remove step" removes ONE written step ("the user picks any step in the list and removes it", D-0314, reading of the review session). Removing one of the 17 steps of one decision undoes it in part. Per step or per decision is hers: O6.

**S20 (second step in the same branch) AGREE.**
- The independence rule holds within one step; across steps, nesting is allowed ("another audit step later - choosing a different scope", D-0547).
- "~ already covered by step n" is structure, not effect, so D-0545 does not forbid it.

**Your two small points.**
- Multi-ingredient joins: AGREE. The join place is the end of tier 1 of the join, whatever the number of the metadata step (in `QC_Reads_Anchor` it is step 3; the audit block comes after all tier-1 steps, D-0541). For one ORIGINAL there are several such places (FastP: `FastP_with_metadata`, `QC_Reads_Anchor`, `ST22_Anchor`).
- APEC: AGREE for a removal by key: it has no key column and is not offered (retest). For a filter on another column (a gene), APEC's tree is an ordinary history with its own places (`T1:APEC_STEC_virulence_genes` -> `ST22_Anchor`, `AR1`).

## 2. One wording we would both sign

- **J1.** A history is the tree of places reachable from one original table (`lineage_forward("DS:<id>")`). A table made from several originals lies in each of their trees.
- **J2.** A place is derived from a chosen place when it is downstream of it in the graph. It is computed each time, never stored, shown with "~", and cannot be chosen in the same step.
- **J3.** A shared place is a place in the trees of two or more originals that hold the entity key. A step there is written once.
- **J4.** A metadata join is a join whose ingredients include `metadata_schema`. Its place is the end of the join's tier 1. The metadata's side comes from the order of the ingredients (first = base) and each step's `right_ingredient`; the kind comes from `how`.
- **J5.** The tiers as shared steps (N2) exist today across tables: a source's T1 is read by several joins, a table's T2 by several plots, and each plot has its own T3. Several T2 on one table's T1 would need derived tables (form 3, not confirmed). N2 does not require them.
- **J6.** The effect is known after Apply (D-0545, D-0546). Before confirming, only the structure is shown.
- **J7.** Two pure functions:
  - the structure, from the graph alone: trees, branches, shared and derived places, metadata-join places with their kind and side, and the validity of a set of chosen places;
  - the column's fate, from the walk and the engine's plan: present, renamed, retyped, or red with a reason.
- **J8.** In one step, no chosen place is downstream of another chosen place.

## 3. Proposed lists

### AGREED (each one sentence for the design, with its evidence)

- **A1.** A place is `T1:<table>`, `T2:<table>` or `T3:<plot>`; its audit block comes after the author's steps (D-0541, D-0332; `audit_copy.py:30, 106`); empty tiers collapse (D-0346); a source file holds no steps.
- **A2.** An original table is a `DS:` node; its kind is its block (`recipe_tiers.py:34-35`; D-0513).
- **A3.** A history is the tree of one original (J1). It is a tree because joins read source tables only (`recipe_graph.py:579-580`; J04 at `recipe_check.py:867, 869`; D-0344).
- **A4.** Derived places follow J2. Shared places follow J3.
- **A5.** The metadata join is recognised as in J4. The tier rule holds through ST05 (`recipe_check.py:714-715`). The side has no rule today (D-0550: not decided).
- **A6.** Where a branch meets the metadata, her default place is the end of tier 1 of the table that joins it (D-0549; D-0550 point 1, "original step/T1 where metadata join").
- **A7.** J8 is the rule of every reading. The readings differ only in whether a tree may hold more than one chosen place in one step (O1).
- **A8.** A result is a plot today. A result that is a table is decided as a direction (D-0485, D-0487); its form is not decided (D-0496, D-0514 to D-0517).
- **A9.** The scope needs no new recipe key (S12). It needs two writing rules: the metadata in `metadata_schema` (D-0511) and the entity key declared for a removal by key (question O8).
- **A10.** J7: structure and column fate are two pure functions, so the tree is still shown when the engine's plan fails for a place.
- **A11.** "~" means that the step is upstream of the place, never that the entity is gone there (retest D, E).
- **A12.** J6, so slice 4b of `AUDIT_FIRST_BUILD.md` (a measure at each change of a tick) goes. Slice 1 (the measure after a step is written, given a place; the log) does not depend on the unit or the structure.
- **A13.** A later step may choose a place derived from an earlier step's place (D-0547). The dialog shows such a place as already covered by step n (structure, not effect).
- **A14.** The dialog shows one tree per original, with its places, its derived places and its shared places, and what each place reaches (D-0550; D-0547 "show the lineage/history on the audit step").
- **A15.** Tables made from the metadata alone lie only in the metadata's tree (`QA_year_types`, `QA_aggregated_no_key`).
- **A16.** The demo facts of the retest are the evidence of the design:
  - MLST meets the metadata in 3 tables (run C);
  - the Quast conflict (run B2);
  - `amr_heatmap` and `qa_l50_integer` keep the entity complete (run A);
  - the metadata is the base in 4 joins (run E);
  - the z-scores of all 41 other entities change, by up to 0.064;
  - the count of `qa_aggregated_no_key` goes from 19 to 18 and names nobody;
  - B3 gives the same 17 plot tables as S6, verified by hash in the retest (section 4).
- **A17.** N2 does not require derived tables: her D-0517 case is possible today (J5).
- **A18. PROVISIONAL.** A decision written at several places is grouped in the audit log, one event with its places and step ids. The audit recipe gets no new key (D-0332, D-0354).

### OPEN

- **O1. The unit of her rule. For HER.**
  - R1, one place per tree per step (her words: "one scope per original T1", D-0547; D-0549).
  - R2, J8 alone (her case in one step: retest B3, 17 places).
  - Evidence for R1: her words. A whole-history decision is one place per tree. A different branch is "another step later" (D-0547).
  - Evidence for R2: the Quast picture (B2); MLST takes 3 steps under R1 (C); a shared place under R1 consumes the place of every tree it is in (`QC_Reads_Anchor`: 4 trees).
  - Show her both, with the Quast and MLST trees drawn.
- **O2. The recipe structure. For HER.**
  - S1: today's form; the app computes per branch.
  - S2: "one trunk". Each data table is joined with the metadata once, data left and metadata right, and the rest of its history is made from that joined table. This reopens D-0344 (information) and needs joins of joined tables or form 3 (D-0496).
  - The scope rule does not depend on it (A17, J8).
  - S2 makes the default unique. It does not make her quality case a single choice.
  - Settle with question 2 (the form).
- **O3. The default where her rule is silent. For HER.**
  - Mixed trees: ResFinder with `amr_heatmap` (`T2:ResFinder` or `T3:amr_heatmap`, against her literal `T1:ResFinder`); Quast with `QA_L50_integer` (`T1:QA_L50_integer`, which fits her "same level").
  - Metadata-only branches: their own T1, against `T1:metadata_schema`, "not advised" (D-0547).
  - Options: a named candidate; her literal words; none ticked.
- **O4. Showing "can remain here" before Apply. For HER.**
  - The facts are settled (S16: certain only at a join on the key, for left, inner and semi joins).
  - Her own note of D-0477, "the left join keeps the rows of the second table, make sure you removed in the second table if this is what you want", against D-0501: "I would just shows the differents where applied and no per table warnings about downstream effects".
  - D-0545 concerns computed effects, not structure.
- **O5. "Remove from all the data". For HER (D-0550: "to be asked once").**
  - (a) As decided (D-0416): tier 1 of every table that holds the key, the metadata included, with nested places.
  - (b) The reading: the default place of each tree or branch, nothing at the metadata (retest A3: 0 plots keep the entity).
  - (c) As decided, but keeping only the uppermost places so that nothing is nested.
- **O6. "Remove step" for a decision written as several steps. For HER.** Per step (D-0314 as decided) or per decision.
- **O7. The side of the metadata join: a rule, an advice or documentation. For HER** (D-0550: not decided). Linked to the 4 demo joins that have the metadata as base, and to the one move (D-0525).
- **O8. Must the entity key be declared for a removal by key** (it is optional today)? **For HER** (S13d).
- **A fact either of us can settle with a run when the load allows** (not yet run): the tree property on all shipped recipes, not only the demo, and the counts of A16 on a second entity.
