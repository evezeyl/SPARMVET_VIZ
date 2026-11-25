# SONNET position 1 (written blind: I read no Opus text). For the Opus agent, to answer point by point.

Labels: [V] = I ran or read it myself; [R] = reasoned; [P] = my proposal, not hers. Sure = high/medium/low.
Code = worktree `SPARMVET_VIZ_wt_good_practice` (873cae14). My read-only run: `tmpAI/.../scratchpad/trees.py` (builds the graph of the demo recipe, `utils` proved to come from that worktree).
Words are hers (ledger D-0547, D-0549, D-0550, D-0551) unless marked.

## 1. Concepts (exact; each recognised from the recipe with no guessing)

**S1 Place.** `T1:X`, `T2:X`, `T3:p`; the step goes in `audit_steps` after the author's steps of that tier (D-0541, D-0332; `audit_copy.parse_place` :106, `_holders` :129). An empty tier is not a place: it collapses into the lowest tier that has steps (D-0346). A tier 2 of a table no plot reads is refused (`audit_copy._target` :178). A source file (DS) holds no steps. [V] Sure: high.

**S2 Original table.** A table of the blocks `data_schemas`, `additional_datasets_schemas`, `metadata_schema` (`recipe_tiers.py:34-35`); node `DS:S`. Kind = block (D-0513, D-0523). Recognised by the block, never by meaning. [V] high.

**S3 History = the tree of an original** (her word, D-0550) = every place reachable from `DS:S`. **Branch** = one path of that tree from the root to a result (my word, not hers). [V] I ran it on the demo: in all 12 originals the reachable set is a true tree (no place has two parents inside it); 17 plots; a plot has one branch per original that feeds it (virulence_bar 6, qc_reads 4, mlst_bar 2, amr_heatmap 1). It is a tree only because joins read source tables only (D-0344, DECIDED) and a self-join is not followed. Form 3 (derived tables, D-0496, NOT confirmed) can create a diamond. High.

**S4 Chosen / derived place.** A place q is *derived from* a chosen place p when q is downstream of p in the graph (same tree). It is computed from the graph, never stored: only the chosen places are written (the step in `audit_steps`). [R] high. Reason: a stored derived set would silently go wrong when the recipe changes (D-0195: counts are derived, never stored).

**S5 Independent places.** Two places are independent when neither is downstream of the other. Her "independent histories": the first T1 of two originals are independent places. [R] high.

**S6 Shared place.** A place that is in the trees of two or more originals: every T1 of a join with 2+ ingredients and every place below it. One table = one step written once, not duplicated. "Duplicated" is only the case of choosing the first T1 of each original (different tables). [V] high.

**S7 Metadata join.** A join J whose `ingredients` list contains `metadata_schema`; its place is the END of `T1:J` (the join steps are in tier 1). Side: the first ingredient is the base/left (`recipe_graph.py:27`); `right_ingredient` of each `polars_join` step. Tier rule: D-0510 "A for now" (refuse a metadata join in tier 2): DECIDED, NOT built (`recipe_check.py` has no such rule: grep of "metadata" finds only the block's own handling, :356-384) [V]. Side (data left, metadata right) is advice or documentation: NOT decided (D-0550). High.

**S8 Default place** (a starting point named as a default, D-0531). Her rule: where the original and the metadata are joined; with no metadata join, the first T1 of the lineage (D-0549, D-0550). One default per branch, not per tree (see S10). Medium.

**S9 Result.** Today a plot (`T3:p`, `target_dataset`). A table as result is NOT decided (D-0514 to D-0517). A table no plot reads is a place with reach "no plot" (D-0451). I would not call it a result. Medium.

## 2. The unit of "one scope per history"

Three readings. R1: one place per tree per step. R2: one place per branch per step = the chosen places of a step are pairwise independent (no chosen place downstream of another). R3: one place per tree in total, a second place needs a second step.

**S10 Test against the retest** (`RETEST_her_scope.md`):
- MLST joined with the metadata in 3 tables (a join place on 3 branches): R1 gives 3 steps for ONE decision (the retest says so) or forces `T1:MLST`, which fails where the metadata is the base. R2 takes 3 sibling places in one step (none is above another). R2 wins.
- Quast (run B2): she wants the entity out of `qa_l50_integer` and `qa_population_zscore`, not out of the quality plots, all in the Quast tree. `T1:Quast` hits all four branches. R1/R3 cannot say it in one step; R2 chooses `T1:QA_L50_integer` and `T1:QA_population_zscore`; the two quality branches are neither chosen nor derived. R2 only.
- `amr_heatmap` (reads ResFinder directly) and `qa_l50_integer`: no metadata join on the branch. The first T1 of the tree (`T1:ResFinder`) is above the 4 join places, so R2 forbids mixing it with them. The private place `T3:amr_heatmap` or `T1:QA_L50_integer` is independent of them. R2 fits; her literal "first T1" does not (see S17).
- Four joined tables with the metadata as base (run E): the first T1 of the original is a valid place, but the entity stays (its row comes from the metadata side). R2 permits it; it is a question for S16, not for the unit.
- A joined table built from six originals: it is one place in six trees; choosing it once satisfies six branches (shared place, no duplication). R2 fine; R1 counts it once per tree: fine too.
- The metadata tree has 42 places, 14 T1, 13 plots [V]: R1 means "one place covers nearly everything"; R2 allows sibling joins.

What the user sees under R2: one tree per original, each place marked chosen / derived "~" / not reached, its reach (plots) beside it; she can choose a sibling place of another branch, not a place under a chosen one. Under R1 she sees the same tree with all other places greyed once one is chosen.

**S11 My claim: the unit is the BRANCH (R2), and the tree is what is shown.** Her rule exists so that a place and a place derived from it are not both chosen; R2 keeps exactly that. Her "one per original T1" is the special case where the chosen place is the first T1 of the original (an ancestor of every branch). R2 stays valid on a graph with diamonds (form 3); R1 needs a tree. Her own case ("all analyses but the quality ones", D-0549) is not expressible with R1. Reading R2 is MINE; her words allow R1; ask her with the Quast picture. Sure: medium-high.

## 3. What the recipe must declare

**Already declared (enough):** the kind of table by block (S2); the ingredients and their order (base first); `entity.population` and `is_entity_key` (`recipe_check.py:332-348`); `audit_steps` after each tier of a schema, a join, a plot's tier 3 (S1); plots with `target_dataset`. [V]
**S12 No new key is needed for the audit scope.** The trees, shared places, derived places and metadata-join places are all computed from `ingredients`, the blocks, the tiers and the plot targets. [R] Sure: medium-high. Check by Opus: is there one fact of her model the graph cannot give?
**S13 What is missing is rules, not keys:** (a) the metadata join in tier 1 (D-0510, decided, not built); (b) `VirulenceFinder` moves to `data_schemas` (D-0523, not made; by the demo-recipe rule D-0373); (c) `additional_datasets_schemas` has no meaning written in the spec (it says only "same shape"); (d) the entity must be declared for a "remove by key" (optional today; not declared = no remove-by-key): a possible rule, her decision.
**S14 Tiers as shared steps (N2):** today the shared tree is source T1 -> several joins -> T2 -> several plots, depth fixed (D-0344). "T1 common to several T2" within ONE table needs a second T2 on one T1 = derived tables (form 3). Whether N2 needs form 3, or only reads what exists, I do not know. Her D-0496 says form 3 is not confirmed. Position: design the scope rule (R2) on the general graph so that it does not depend on the answer. Low-medium.

## 4. What the lineage computation must give

Today (`lineage_walk.walk` :883, `Walk`, `Line` lineage_records.py:267): from a column at a start place it lists the places holding that column back to the sources then forward, each with `reach` (sets of places and plots), tick/grey, `scope_group`; `Gone`, `Outside`. It does NOT give: the tree per original, the order of places in a branch, derived-from, shared flag, the metadata-join place, the default, whether a set of chosen places is valid (no nesting). `Occurrence.sources` gives the source column(s) of a line, not the history. [V]

**S15 Split in two pure functions [P].** (a) STRUCTURE from the graph alone (no engine plan, no column): trees, branches, shared places, derived-from, metadata-join places, defaults per branch, the validity check of a chosen set. (b) COLUMN FATE (the existing walk): does the key exist at the place, renamed, retyped, grey/red with a reason. The dialog is (a) with the marks of (b). Reason: structure must not fail when a plan fails (the user still sees the tree). What the app cannot know: whether the key survives (plan), anti/right/full/self joins (`join_not_yet_followed`), a metadata block declared but never joined, the effect (only after Apply). The user then sees the place grey/red with the reason, the tree intact. [R] medium-high.

## 5. The audit under the structure

**S16 "~" means "the step is upstream of this place", not "the entity is gone here".** Retest D and E: a step on the right side of a left join keeps the base row (columns empty), a step upstream of a join where the metadata is the base leaves the entity. The recipe alone tells the join kind and side (`Hop.join_how`, `join_side`, lineage_records.py:146) [V as data, not checked end-to-end]. [P] Mark a derived place "the entity can remain here: the other table of the join is the base" where that is certain, from the recipe, before Apply (information, not a choice; N6). The measured effect stays after Apply (D-0545, D-0546, D-0536, D-0537). Medium.

**S17 Default per branch [P].** Her rule covers a tree where EVERY branch joins the metadata (default = join places) and a tree where NONE does (default = first T1). It is silent on a mixed tree (ResFinder: 4 join branches + `amr_heatmap`; Quast: 3 + `QA_L50_integer`) and on a branch of metadata only (`QA_year_types`: her literal rule gives `T1:metadata_schema`, which she calls not advised). Candidate rule (mine): per branch, the join place if the branch passes a metadata join; else the first place that only that branch (and the results below it) reads (`T3:amr_heatmap`, `T1:QA_L50_integer`, `T1:QA_year_types`). Where unsure, no default ticked. Medium-low.

**S18 "Remove from all the data".** D-0416 (DECIDED): tier 1 of EVERY table holding the key, metadata included, ticks chosen by the user (`remove_from_all.apply` :308 writes one step per ticked place, no check for nesting, 27 offered places in the demo [retest]). That contradicts N10 (T1:MLST and T1:MLST_with_metadata can both be ticked). The review session's reading (D-0550: the default place of each branch, not the metadata) is a READING, not decided. Position: redefine as "the defaults of S17, one per branch, nothing at the metadata unless she chooses it, unreached branches listed (the existing `NotReached`)". It reopens D-0416: information only; ask once.

**S19 One decision, several steps.** Several places = several written steps with own ids and one shared reason (`apply`); nothing in the recipe says they were one decision. The log (D-0315, D-0478) must. [R] Where (a decision id in the audit step, or the audit record) is OPEN; ask Opus.

**S20 Second step in the same branch.** Allowed (D-0547: "another audit step later - choosing a different scope"); its derived places are computed for its own place; a place derived from the first step is shown "~ already covered by step n" (information). Order: author steps, then audit steps, per tier (`recipe_tiers.step_list`). [R] medium.

## 6. Where she may be missing something

1. "~" can be read as "removed here" (S16). Why: join side/kind decide the effect (retest D, E). How: static mark where certain; measure after Apply.
2. "One per original T1" cannot express her own case (S10, Quast). Why: a tree has branches she wants treated differently. How: unit = branch (R2); the tree is the view.
3. Mixed trees and metadata-only branches have no rule (S17). Why: retest facts. How: per-branch default, none when unsure.
4. "First T1" of an original is above join places of the same tree; both ticked = nested (S18). How: the nesting check, shown not forced (N6: she can still choose it).
5. A place before tier 2 changes aggregates/z-scores of other entities (retest: 41 of 41 z-scores differ, max 0.064). Not a flaw; the measure after Apply (D-0536) is what shows it.

## 7. Not sure; for Opus to check

- S11 (R2 over R1): ask for the picture she would accept; is there a reading of N10 where R1 is right?
- S12: a fact of her model that the graph cannot give?
- S14: does N2 require form 3?
- S16: is `Hop.join_side/join_how` enough to say "can remain" certainly for left, inner, semi? Not checked end to end.
- S17: is my candidate rule "choosing for the user" (D-0531) or an acceptable named default?
- S19: where is the decision grouped?
- Multi-ingredient joins (QC_Reads_Anchor: 4 ingredients, metadata last): the "metadata join place" is `T1:J` whatever the step; is the join place per original really one place?
- The APEC look-up table has no key column (retest): its tree is "not reached" by a key removal; is that all?
