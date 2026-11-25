# SONNET round 2: answer to OPUS position 1 (P1 to P31). Not for the owner; no design document yet.

Labels: [V] I read it or ran it myself in this round; [R] reasoned; [P] proposal. Her words are quoted from the evidence field of the ledger.
Checks I made now (read-only; the worktree `SPARMVET_VIZ_wt_good_practice` stays clean; `utils` proved to come from it):
- C1 `recipe_graph.py:579-580`: a join's parents are `T1:<ingredient>` for each ingredient (first = base); `:584-585`: a plot's parent is `T2:<target>`. [V]
- C2 `recipe_check.py:867`: J04 refuses an ingredient that is "not a schema of this recipe" (`self.schema_ids`, which includes `metadata_schema`, :382). But the graph builder accepts a join as ingredient (`recipe_graph.py:~659`: `name not in schemas and name not in joins`). So graph and checker disagree today; the checker is the rule. Ledger D-0344 (her words: "Yes but the lineages are independent no? ... we need to be able to join metadata for example to any other original data" and "Yes, revisit if needed"): DECIDED, "a named join takes only source tables ... to revisit only if a real recipe needs it". Opus's reading of J04 and D-0344 is right. [V]
- C3 NEW, changes what I said in round 1 (S7, S13a): `recipe_check.py:714-715` (ST05) + `action_names.py:66` (`TIER1_ONLY = {JOIN, JOIN_ASOF, JOIN_WHERE}`) refuse ANY join step in tier 2 or tier 3 of a table, a join or a plot. So the tier-1 rule of D-0510 for the metadata join is already in force (through every join action), not "not built". What D-0510 adds beyond ST05 is nothing I can find; I withdraw my S13(a). [V; default catalog; a caller can override `tier1_only`]
- C4 Retest B3 = S6: from `out/results.json` I compared `B3.plots` with `S6.plots` (17 plots, each record with `frame_hash`, `changed`, `emptied`): 0 differences. [V] Caveat: B3's 17 written places include `T1:ResFinder` AND four joins below it (`ResFinder_with_metadata`, `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`): nested places give the same tables, because a removal filter is idempotent. So a "no nesting" rule is about what "one scope" means and what the log says, not about the correctness of the result.
- C5 Demo graph (my run): `T1:ResFinder` has 5 children: `T2:ResFinder` and 4 joins. `T2:ResFinder` has 2 steps and is read by `amr_heatmap` only. So `T2:ResFinder` is a real, separate place, private to that branch (Opus P12 is right). `T2:Quast` is empty and read by no plot. [V]
- C6 Demo joins (my run): 5 data originals already have the trunk of "one trunk" (`FastP/Quast/Bracken/ResFinder/MLST_with_metadata`: data base, metadata right). 4 joins have the metadata as base (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`); `QA_year_types` and `QA_aggregated_no_key` have the metadata as their ONLY ingredient. [V]

## 1. Point by point

| P | Verdict | Evidence / wording |
|---|---|---|
| P1 | AGREE | `recipe_tiers.py:34-35`; D-0513, D-0523. `APEC_STEC_virulence_genes` has no key column (retest). |
| P2 | AGREE, one condition | "each independent history is like an independent tree graph" (D-0550). My run (12 originals): every set reachable from an original is a true tree. That is true only while D-0344/J04 stand (C2). |
| P3 | AGREE | C1. One doubt that stays open (O7): her N2 "t1 can have common steps for different t2" is more than today's form if it means two T2 on one T1 of one table. |
| P4 | AGREE | D-0541; `audit_copy.py:106,129`; D-0346 collapse. |
| P5 | AGREE | Derived = downstream; computed, never stored; "~" is display. D-0547 "All the derived steps must get a "~"". |
| P6 | CHANGE | Structure must not depend on the column. Wording: "a shared place is a place with two or more originals upstream". Whether those originals hold the key at that place is column fate (the existing walk). Demo: `ST22_Anchor` 6, `QC_Reads_Anchor` 4, `AR1` 4 [V]. |
| P7 | CHANGE | Add: a metadata join needs the metadata AND at least one other original among its ingredients. `QA_year_types` and `QA_aggregated_no_key` (C6) have the metadata as sole ingredient and no join step: by Opus's second clause ("first ingredient is `metadata_schema`") they would be called metadata joins. They are not (they are branches of the metadata's own tree, P18). Tier rule: C3 (already enforced by ST05). Side: not a rule (D-0550 "NOT decided"). |
| P8 | AGREE | Computable per path (branch). Her words: "where original T1+ metadata are joined" (D-0549); "the first T1 of the lineage when no metadata join (so same level except there is no metadata joined)" (D-0550). Not unique per tree in the demo (C6, retest section 2). |
| P9 | AGREE | A result is a plot today. D-0485 (her design: "A plot entry should be a result entry with either a plot or a table") is her design, the form is open (D-0496). My round-1 S9 said "not decided": the design is hers, the format is not built. |
| P10 | AGREE | Retest section 2 [V]. |
| P11 | AGREE (both readings are real) | See O1. Strongest words for U1: D-0549 "the only way to choose several places must be the case of the independent history - the original T1 steps of independent histories"; D-0547 "one scope per original T1". |
| P12 | AGREE, with C4/C5 | `T2:ResFinder` as the private place of `amr_heatmap` is better than my `T3:amr_heatmap` (it is a place with steps, one table, reach 1 plot). B3 = S6 [V]. One walk change is needed: `lineage_walk.py:38` (P6 of the walk) folds a table's empty tier 2 into its tier 1 "also when plots read the table directly and joins read it too". That fold is wrong for a table that feeds both joins (they read T1) and plots (they read T2): the two places have different reaches. For `ResFinder` it does not bite (tier 2 has steps); for a table with an empty tier 2 read by a plot and by a join it would. |
| P13 | AGREE | It is hers. I withdraw my round-1 S11 ("R2 wins") as a position: it is my lean, and O1 argues both. |
| P14 | AGREE | Retest A [V]: `amr_heatmap`, `qa_l50_integer` keep the entity complete. |
| P15 | AGREE, add | Also `entity.population` and `is_entity_key` (`recipe_check.py:332-348`). |
| P16 | CHANGE | Three structures, not two: see section 3 and O2. Facts C2, C6. |
| P17 | AGREE | Her case needs places below the trunk (the quality plots read `Quast_with_metadata` directly). |
| P18 | AGREE | Their own first place is the table itself (`T1:QA_year_types`). |
| P19 | CHANGE | "Goes: several ticks along one lineage" is true only under U1. Under U2 ticks in independent branches stay; what goes under both is a tick on a nested place. Stays: everything of column fate. Changes: add the structure function (trees, derived, shared, default, nesting check) and the fold of `lineage_walk` P6 (P12). The lineage/join-linked groups as an offer: the groups can stay as information ("other tables the key is linked to") but are not the unit of the dialog any more. I cannot verify Opus's remark on slice 4b (I did not read `AUDIT_FIRST_BUILD.md`). |
| P20 | AGREE | D-0545 "you cannot see effect if you do not recalculate", D-0546 "again after apply". |
| P21 | CHANGE | The facts are right for the default set. The claim "on the demo both leave the entity in 0 plots" is verified only for A3 (19 places, nothing at the metadata). A run of D-0416 as decided (every table that holds the key, 27 places) was NOT done: label it unverified. A check I can still do (O5). |
| P22 | AGREE | Retest C [V]: one place, 2 plots change, 14 keep the entity. |
| P23 | AGREE | Retest B2. |
| P24 | AGREE | Retest E. |
| P25 | AGREE | Retest: 41 of 41 z-scores differ, max 0.064. A natural consequence (D-0501), not a gap. |
| P26 | AGREE | Retest: count 19 to 18; the plot names no entity. |
| P27 | AGREE | `modified.py:76-79`: `na: keep` ORs `is_null`. It concerns a filter on a metadata column, not a key removal. |
| P28 | OPEN (O3) | Her words are ambiguous: "same level" can mean the original's own T1 or the table at the level of the join place. |
| P29 | OPEN (O1) | Both readings have her words. |
| P30 | CHANGE to a statement | "Chosen" is a property of the place (one table), so it is chosen in every tree that holds it and is that tree's one place. Reasoned [R]; the display is a design question. |
| P31 | DONE | C2 and C4. |

## 2. Same thing, one wording we could both sign

- **History**: the tree of one original table: every place reachable from its `DS:` node (D-0550). **Branch**: one path of that tree from its root to a result (word of both of us, not hers).
- **Place**: `T1:<table>`, `T2:<table>` or `T3:<plot>`, with its `audit_steps` after the author's steps; an empty tier is the same place as the tier below it (D-0346), except that the fold must not join a T2 read by plots to the T1 read by joins (P12).
- **Derived place** of a chosen place: every place downstream of it. Computed from the graph, never stored, shown "~", not chosen.
- **Shared place**: a place with two or more originals upstream. One table, one step written once; "duplicated" means only the first T1 of several originals (different tables).
- **Metadata join**: a join with `metadata_schema` and at least one other original among its `ingredients`; its place is the end of its tier 1. Base = first ingredient.
- **Default place**: a named, changeable start (D-0531), per branch, computed from the recipe.
- **Result**: a plot (`T3:<plot>`) today.

## 3. "One trunk" (Opus S2) against today's form

What it is: each data table joined with the metadata once (data left, metadata right); every other table of that history made from that joined table.
- **What it changes for the demo.** For 5 originals the trunk already exists (C6). About 11 other tables (`QC_Reads_Anchor`, `ST22_Anchor`, `AR1`, `QA_*`, `QA_L50_integer`, `QA_population_zscore`) would read a trunk instead of the original; the 4 tables with the metadata as base would become data-base (row set depends on the data: [R], a data-left join keeps only what the data holds, which is her own wish in D-0549 "join what really is in T1 without the extra in metadata").
- **What the author writes.** Joins whose ingredients are joins, or derived tables with `from:`.
- **What the lineage could then recognise.** One default place per original, with no ambiguity; "default = the end of the trunk" stated by the structure.
- **What it breaks.** (a) J04 and D-0344 (C2); the engine takes source tables only. (b) A table made from several originals (`ST22_Anchor`, 6) would join several trunks, each carrying the metadata columns: either the author drops the duplicate columns (extra steps) or reads one trunk and the other originals directly, and then those originals have no trunk before this table. So "each data table joined once" cannot hold for a multi-original table. (c) Metadata-only branches and look-up tables still have no trunk (P18). (d) Her case still needs places below the trunk (P17). (e) Whether trunks are advice, rule or documentation is not decided (D-0550).
- **A third structure (S3), mine, not an endorsement:** keep today's form and let the recipe author NAME the default place of an original in the recipe (a declared key). Nothing is guessed; D-0344 stays. It is a new key, so a format decision.
My view: "data left, metadata right" is a good-practice pattern for authors (D-0547, D-0549), not a structure the format must force; whether the format should force it is her question (O2).

## 4. The proposed lists

### AGREED (one sentence each, for the design)
- A1 A history is the tree of one original table (every place reachable from its `DS:` node); it is a tree because joins read source tables only (D-0344, C2); form 3 could create diamonds (D-0496, not confirmed).
- A2 A place is `T1:<table>`, `T2:<table>` or `T3:<plot>`, written in `audit_steps` after the author's steps (D-0541, D-0332); original steps are never changed.
- A3 A derived place is any place downstream of a chosen one; it is computed from the graph, never stored, shown "~", and cannot be chosen (D-0547).
- A4 A shared place has two or more originals upstream; it is one table and one written step.
- A5 The kind of an original table is its block (D-0513, D-0523); a metadata join is recognised from `ingredients` (metadata plus at least one other original), its place is the end of tier 1, base = first ingredient.
- A6 Any join step must be in tier 1 today (ST05, C3); the side of the metadata is not a rule (D-0550).
- A7 No new key is needed to compute trees, derived and shared places and the join places; the recipe already declares blocks, ingredients, tiers, plot targets, `entity` and `is_entity_key`.
- A8 The structure (trees, derived, shared, defaults, check of a chosen set) must be computed from the graph alone, with no engine plan; column fate (key survives, renamed, cast, red "YET" lines) stays in the existing walk.
- A9 The walk's fold of an empty tier 2 into the tier 1 must not join a T2 read by plots to a T1 read by joins (P12, `lineage_walk.py:38`).
- A10 The effect of an audit step is known after Apply (D-0545, D-0546); before it, only structure is shown.
- A11 Branches that never meet the metadata (`amr_heatmap`, `qa_l50_integer`, Summary histories) are not covered by "the join place": a default is needed for them (retest A).
- A12 A first-T1 place of an original does not remove the entity from a result where the metadata is the base of a left join (retest E) and does remove the entity from quality plots that read it (retest B2); the join place does not have that problem (retest B3 = S6, C4).
- A13 Nested places give the same tables as the non-nested ones (C4): nesting is a question of meaning and of the log, not of correctness.
- A14 A second step in the same branch is another audit step with another scope (D-0547); its derived places are computed for its own place.
- A15 The z-score and no-key aggregate effects (retest) are natural consequences of the rerun (D-0501), shown by the measure after Apply (D-0536).
- A16 "Chosen" belongs to the place: a shared place chosen is that place in every tree that holds it.

### OPEN
- **O1 The unit of "one scope per history": tree (U1) or branch (U2). Question for HER; neither of us decides.**
  - U1 (one place per original's tree per step). For: D-0547 "the user can only chose one scope per original T1 on where to apply the step"; D-0549 "the only way to choose several places must be the case of the independent history - the original T1 steps of independent histories"; D-0550 "each independent history is like an independent tree graph". Cost: "all but the quality ones" takes several steps (D-0547 "he must add another step audit step later"); B3 writes 5 places in the ResFinder tree alone [V], so up to 5 steps for one decision; the tree's only place that covers all branches is T1 of the original, which fails with the metadata as base (E) and hits the quality plots (B2); MLST needs 3 steps (retest C).
  - U2 (one place per branch per step; chosen places not nested). For: her case "remove the samples from all analyses BUT the ones that show the bad quality" (D-0549) is one decision and one step; B3 17 places = S6. Against: contradicts her literal words; valid on diamonds.
  - Picture for her: the MLST tree (3 join places) and the Quast tree (4 branches, two wanted, two not).
- **O2 Structure: today's form + per-branch computation, "one trunk" (Opus S2), or a declared default (my S3).** Question for her (it reopens D-0344 for S2, information only; it adds a key for S3). A check we can still do: how many demo tables break under S2 (a dry run on a scratch copy; I have not done it).
- **O3 The default where her rule is silent: mixed trees (ResFinder, Quast), metadata-only branches, and what "the first T1 of the lineage ... same level" means (P28).** Candidate (both of us): the first place that no other branch reads (`T2:ResFinder`, `T1:QA_L50_integer`, `T1:QA_year_types`). Hers: it is a default, she must confirm. No default where unsure.
- **O4 What "~" means; whether "can remain here" may be shown before Apply.** For showing: D-0543 "try to give as clear information as possible - so the user has elements it needs to be able to make a good decision"; D-0531; D-0549 itself is built on the base-side fact; D-0478 asks that warnings shown be logged (so a shown warning is also recorded). Against: D-0501 "no warnings about the natural consequences downstream"; D-0545/D-0546 "again after apply". The distinction I draw: "the entity may stay" is not a downstream natural consequence but whether the step does what was asked. Hers. Fact still to settle by a check (O8): is the static reading of join kind and side exact on the demo against the measured retest runs?
- **O5 "Remove from all the data".** D-0416 as decided (every table that holds the key, metadata included) against the review session's reading (default place per branch, nothing at the metadata; D-0550 "NOT decided"). Both leave the entity in 0 plots only if the demo run is done: not done for D-0416 (P21). A check I can do: run all 27 places and compare. Question for her once.
- **O6 How several written steps of one decision are held together.** Today `remove_from_all.apply` writes one step per place, each with its own id and one shared reason; nothing in the recipe says they are one decision. Options: a decision id in each step; the audit record; derive from equal operation and reason (fragile). D-0315 and D-0478 require the log to keep who, when, reason, scope, warnings. The form of the record is NOT decided (D-0536/D-0537). Can partly be settled between us (what must the record hold), the form is hers.
- **O7 Does N2 ("t1 can have common steps for differents t2") need form 3?** Today a table has one T2. Hers (D-0496, D-0517).
- **O8 Facts we can still check:** the static join-side reading against the retest (O4); all 27 places (O5); a dry run of S2 (O2); whether `tier1_only` is overridden in any shipped catalog (C3).
