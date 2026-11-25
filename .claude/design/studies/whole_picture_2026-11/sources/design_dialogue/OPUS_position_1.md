# Opus position 1: recipe structure, lineage, audit scope (for the Sonnet agent; a draft, not for the owner)

Read on `dev` `febc506f` (merged into my worktree). "Retest" = `tmpAI/coordinator/whole_picture/RETEST_her_scope.md`. "My map" = a read-only script on the demo recipe with `recipe_graph`. Sureness: H = verified, M = my reading, L = to check.

## 1. Concepts, and how the app recognises each

P1. **Original table** = a node `DS:<id>`: each schema of `data_schemas` and `additional_datasets_schemas`, and the block `metadata_schema` (`recipe_tiers.py:34-35`; `recipe_graph.py:575-579`). Its kind is its block (`Node.path`): "those 3 categories are defined in the recipes" (D-0513). Recognised today. H. In the demo, `VirulenceFinder` is in the wrong block (D-0523), and `APEC_STEC_virulence_genes` has no entity key.

P2. **History** = the tree of one original table: `lineage_forward("DS:<id>")` (`recipe_graph.py:200`). Her words: "each independent history is like an independent tree graph" (D-0550). A table made from several originals lies in several trees (`source_tables`, :235). Recognised today. H.

P3. **Tiers as shared steps** (D-0539) are already the graph's shape: a join reads its ingredients' T1 (:579-580), a plot reads its target's T2 (:584-585), T3 is per plot, a T2 no plot reads is refused (S07/J14). Nothing new to declare for N2. H.

P4. **Place** = a node `T1:<table>`, `T2:<table>` or `T3:<plot>`, plus its `audit_steps` block after the original steps (`audit_copy.py:30, 106`). Her words: "audit steps can be written at each tier after the original tier block" (D-0541). Empty tiers collapse into one place (D-0346). Recognised today. H.

P5. **Derived place** of a chosen place P = every place downstream of P (`lineage_forward`), in every tree that holds it. It is shown with "~" and cannot be chosen: "All the derived steps must get a "~"" (D-0547). Exact. H. The "~" is display only: the audit recipe holds the step at P, and the derived places only run again.

P6. **Shared place** = a place with two or more originals upstream that hold the entity key. Exact. H. Demo: `ST22_Anchor` has 6 originals, `QC_Reads_Anchor` 4, `AR1_MLST_Serotype_Virulence` 4.

P7. **Metadata join** = a tier-1 `polars_join` whose `right_ingredient` is `metadata_schema` (metadata right), or a join whose FIRST ingredient is `metadata_schema` (metadata is the base: `recipe_graph.py:27, 322`; `lineage_walk.py:203`). The join kind comes from `how`; ST05 keeps joins in tier 1 (`recipe_check.py:714-715`). Recognised today. H.
- The side is free today: in 4 demo joins the metadata is the base (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`). H.
- Her best practice, "T1 original -> left_join -> metadata" (D-0547), is not a rule. Rule, advice or documentation: NOT decided (D-0550).

P8. **Default place** (D-0549, D-0550): "where original T1+ metadata are joined"; "the first T1 of the lineage when no metadata join". Computable per path from an original to a result: the first node that holds both the original and the metadata, else a first T1. Exact per path, but not unique per tree in the demo (P10). H for the computation; M for "first T1" (P27).

P9. **Result** = a plot entry (`T3:<plot>`): recognised today. A table as a result is not in the format (D-0485; the form is open: D-0496, D-0515, D-0516). H.

## 2. The unit of "one scope per history"

P10. In the demo, originals and analyses are many-to-many (my map; retest section 2). H. MLST meets the metadata in 3 tables (`MLST_with_metadata`, `AR1`: MLST is the base; `ST22_Anchor`: metadata is the base); Quast in 3, and it also feeds `QA_L50_integer` alone; ResFinder in 4, and `amr_heatmap` reads ResFinder itself; FastP 3, Bracken 2, VirulenceFinder 3. Her model reads as one original -> one join with the metadata -> its results.

P11. **Reading U1: the unit is the tree of an original.** Her words: "the user can only choose one scope per original T1" (D-0547). M.
- One place per tree. "All analyses but the quality ones" then takes several audit steps ("if he want another choice he must add another step audit step later", D-0547).
- The only place that covers a whole tree is its trunk, `T1:<original>`. Two consequences:
  - Where the metadata is the base, it empties columns instead of removing the row (retest E: the entity stays in 5 plots; `qa_population_zscore` with `n50` and `n50_zscore` empty).
  - For Quast it also removes the entity from the quality plots (retest B2).

P12. **Reading U2: the unit is each branch (each path to a result).** M.
- Defaults: the join place of each branch, plus the branch's own first place where it never meets the metadata: `T1:QA_L50_integer`; `T2:ResFinder` for `amr_heatmap` (joins read `T1:ResFinder`, and no other plot targets ResFinder: my map, H).
- Her case is then ONE step. Retest B3 (17 places) leaves the entity in exactly the 3 quality plots, with their tables byte-identical to the baseline, and gives the same 17 plot tables as the library's six-unticked result.
- But U2 contradicts her literal "one scope per original T1".

P13. Her words point to U1. Her stated case, "remove the samples from all analyses BUT the ones that show the bad quality" (D-0549), is one step only under U2, or several steps under U1. Put both to her, with retest B3, C and E as what she would see. Do not decide. M.

P14. Branches that never meet the metadata (`amr_heatmap`, `qa_l50_integer`, and the Summary and Summary_quality histories) are not covered by "the join place": retest A leaves the entity complete in 2 plots. Any reading needs a default for them. H.

## 3. What the recipe must declare

P15. **Declared today** (H): the kinds by block; the base = the first ingredient; join steps (`right_ingredient`, `how`, `on`) in tier 1 only; tiers as keys (D-0250); each plot's target and tier 3; `audit_steps` in the audit profile only (`recipe_spec.yaml:59-63`, D-0354); `is_entity_key`.

P16. **Not declared, needed under U1:** which joined table is "the" join place of an original when there are several. Two structures. M.
- (S1) Keep today's form; the app computes per branch. U1's single default is then ambiguous, and the dialog must ask which branch.
- (S2) "One trunk": each data table is joined with the metadata ONCE (data left, metadata right), and every other table of its history is made from that joined table. The default becomes unique, and the side question disappears.
- S2 needs joins of joined tables or derived tables (`from:`). Today J04 refuses an ingredient that is not a schema (`recipe_check.py:867`; D-0344: "a named join takes only source tables"), and form 3 is not confirmed (D-0496). So S2 reopens D-0344 (information only).

P17. Even under S2, "all but the quality ones" still needs places below the trunk, because the quality tables would be made from the trunk. S2 makes the default unique; it does not make her case a single choice. H (reasoned).

P18. Tables made from the metadata alone (`QA_year_types`, `QA_aggregated_no_key`) are only in the metadata's tree. Their first place is their own T1; `T1:metadata_schema` is "not advised" (D-0547). H.

## 4. The lineage computation

P19. Today's walk (`lineage_walk.walk`; `Line`, `lineage_records.py:267-338`). M.
- **Stays:** columns followed through renames and type changes (D-0337, D-0352); red "YET" lines (D-0460, D-0454); `Gone` notes; reach sets; the drop gate.
- **Changes:** output grouped by tree (and branch under U2); a default place per tree (P8); places below the chosen one are "~"; `state` no longer means "one tickable line among many".
- **Goes:** the lineage/join-linked groups as an offer; several ticks along one lineage (D-0316, D-0346); the default-ticks question (D-0316 against D-0508), answered by D-0549 and D-0550.

## 5. The audit

P20. One place per unit (P11 or P12), with the default named and changeable, and derived places shown "~". Another scope in the same history is another step (D-0547). H.
- The effect is known AFTER Apply ("you cannot see effect if you do not recalculate", D-0545; D-0546). Before confirming, only the structure is shown.
- So slice 4b of my `AUDIT_FIRST_BUILD.md` ("measure at each change of the ticks") goes. Slice 1 (the measure given a place, after the step is written, and the log) stays.

P21. **"Remove from all the data".** Not decided; hers. H for the facts.
- As decided (D-0416): tier 1 of every table that holds the key, the metadata included.
- The review session's reading (D-0550, NOT decided): the default place of each history, not the metadata.
- On the demo both leave the entity in 0 plots (retest A3: 19 places, nothing at the metadata). They differ in whether the metadata table itself changes.

## 6. Where she may be missing something

P22. One original, several join places (MLST: 3). Under U1, "MLST removed" takes 3 steps. Retest C: one place changes 2 plots; 14 keep the entity.

P23. Branches with no metadata join keep the entity complete (retest A). Using `T1:Quast` as their default also removes the entity from the quality plots, or empties columns there (retest B2).

P24. Metadata as the base: a removal at the original empties columns instead of removing the row (retest E); only the joined table's own place removes it. Her best practice prevents this; whether it is a rule, an advice or documentation is hers.

P25. The z-score is computed in tier 2. The join place (end of tier 1) comes before it, so all 41 other z-scores change (largest change 0.064). This is an expected effect of the rerun. A place after tier 2 keeps the entity's contribution in the other values.

P26. A table aggregated without the key (`qa_aggregated_no_key`): its count goes from 19 to 18, and nothing in it names the entity. The log must say "cannot count here".

P27. A data-left join keeps entities that have no metadata row. A filter on a metadata column at the join place meets empty values, and its `na` choice decides (`modified.py:76-79`).

## 7. Not sure; please check

P28. Her phrase "the first T1 of the lineage when no metadata join (so same level except there is no metadata joined)" (D-0550): does it mean the original's own T1, or the first table of the branch at the joined-table level? M/L.

P29. Is an "independent history" one original's tree (my reading of D-0550, with D-0496: "pick every original data and see all lineages that goes from there"), or one analysis branch? M.

P30. A shared place chosen in one tree: is it shown as chosen (not "~") in its other trees, and does it count as their one place? L.

P31. Please verify my reading of J04 at `recipe_check.py:867` (P16), and that retest B3 equals S6 (retest section 4).
