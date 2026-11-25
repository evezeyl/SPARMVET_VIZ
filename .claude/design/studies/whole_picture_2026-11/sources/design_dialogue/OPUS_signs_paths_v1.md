# Opus signs `PATHS_AGREED_AND_OPEN_v1.md` (v1)

Read in full: `PATHS_AGREED_AND_OPEN_v1.md`, `RUN_REGISTER_sonnet.md`, and the outputs `paths2/RD.out`, `paths2/T1X.out` where numbers differ. One more run of mine, registered before it was made: R14 (`RUN_REGISTER_opus.md`; `opus2_r14.py`, output `opus2_r14.out`; my graph only). Her words checked against the evidence fields of the ledger: D-0477, D-0501, D-0543, D-0546, D-0547, D-0549, D-0550, D-0553, D-0555, D-0556, D-0560: every quotation in the file is an exact substring (G24 leaves out the closing "..." of D-0560, which is fine).

Changes are numbered C1 to C21.

---

## 1. G1 to G27

| Point | Verdict | Exact wording, reason, basis check |
|---|---|---|
| G1 | SIGN WITH THIS WORDING (C1) | "**G1 The graph.** The nodes are the original data files (the roots), the tier 1 and the tier 2 of every table, and the plots (the leaves); an edge shows what goes into the next node; the tier 1 of a joined table has several parents. A place, where a step can be written, is the tier 1 of a table, the tier 2 of a table that a plot reads, or the tier 3 of a plot: 58 places on the demo (85 nodes with the 12 files and the tier 2 of every table)." Reason: G1 says the nodes are places and the roots are first places, while G3 counts 85 nodes, which include the files and the tier 2 of tables no plot reads; one definition must serve both. Basis: [GRAPH SCRIPT, both]; 58 = 28 + 13 + 17 (Sonnet RD2; my parse). |
| G2 | SIGN | Both runs rebuilt from scratch (Sonnet A, Opus R5). |
| G3 | SIGN | Every number equals my R1. |
| G4 | SIGN WITH THIS WORDING (C2) | Replace the end with: "... and no join reads a join [GRAPH SCRIPT, both]. It stays so while a join reads original tables only (D-0344) [REASONED, not run]; with derived tables, which are not in today's format, it must be checked again." Reason: the condition on the future is reasoned, not run; "ENGINE-free" is not one of the tags. |
| G5, G6, G7 | SIGN | Quotations exact (D-0553, D-0547). |
| G8 | SIGN WITH THIS WORDING (C3) | Tag: "[ENGINE RUN: ResFinder and MLST: Opus R5, R12 and Sonnet C, RD1, RD2; the `T1:FastP` instance: Sonnet RD2 only, its reason (the FastP columns are not among the final columns of `ST22_Anchor`) REASONED, not run]". Reason: the FastP instance was run by one of us only. |
| G9 | SIGN WITH THIS WORDING (C4) | Add after "they can be written in 2 steps (the first places, then the joined tables)": "[REASONED, not run: the joined tables never lie below one another, since a join reads original tables only; the audit copy is the same as the one-list copy of Sonnet D4 and Opus R7, so the tables are the same]". |
| G10 | SIGN WITH THIS WORDING (C5) | Tag: "[ENGINE RUN: the valid defaults with `T1:QA_AMR_per_sample` and `T2:ResFinder`: Sonnet D2 only; the nested defaults with `T1:ResFinder`: Opus R7; both leave the entity in no plot]". Reason: R7 ran the nested form, not the valid one. |
| G11 | SIGN | Both rebuilt (Sonnet D1, Opus R8). |
| G12 | SIGN WITH THIS WORDING (C6) | Tag: "[ENGINE RUN: Opus R7, two entities, the nested defaults; Sonnet D2, D4, E, one entity, the valid defaults]". |
| G13 | SIGN | Settled in section 3: 6 and 7 are two different sets, both runs rebuilt. |
| G14 | SIGN WITH THIS WORDING (C7) | "**G14 The set of the first T1 of every original except the metadata** removes the entity from 12 plots: the 4 whose every incoming root path holds a chosen place, and 8 of the 13 that have a path without one; it stays in 5 (`qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `qa_population_zscore`, `qa_year_label`, `qa_facet_by_mapping`), where the metadata is the first table of the join or the only one. [ENGINE RUN: Sonnet D3 only]" Reason: as written it reads as if only 4 plots lose the entity (X1's own numbers say 8 more do); "same numbers as the earlier retest" goes, since the retest passed through old code. |
| G15 | SIGN | Both: the 41 of 41 "before" is in Sonnet Z and in my R13 (UPPER); "after" 0 of 41 is Sonnet Z only, tagged so. D-0501 quotation exact. |
| G16 | SIGN WITH THIS WORDING (C8) | Tag: "[ENGINE RUN: MLST: Opus R12 only; ResFinder: Sonnet RD1 only]". Replace the bracket on counting with: "(Sonnet's 13 and 14 also count `T2:ResFinder_with_metadata`, a tier 2 with no steps that no plot reads; the 11 nodes that differ are the same in both ways of counting: `paths2/RD.out`)". |
| G17 | SIGN | 45, 17 and 35 of 97 pairs are now from both scripts (my R14 agrees). Tag: "[GRAPH SCRIPT, both: Sonnet; Opus R1, R14]". |
| G18, G19, G20, G21 | SIGN | G19 is Sonnet B only and tagged so; G20 both (R6, RI). |
| G22 | SIGN WITH THIS WORDING (C9) | Tag: "[ENGINE RUN: the 55 places, keys and content: Sonnet RD2 only; the skip of `run_audit`: Sonnet R0 only; the edges of the keys equal my parse on 50 recipes: Opus R3; the content changes inside 'below' at 3 places: Opus R5]". |
| G23 | SIGN | Sonnet R2 only, tagged so. |
| G24 | SIGN WITH THIS WORDING (C10) | First sentence: "After a change at a place, every place below it is computed again from its parents. A stored table is read only under its full key, and the key of every place below the change differs from its key before the change, because it is built from the keys of all its parents (definitions, data and audit steps)." Reason: "never read ... unless the app can prove it was built from the same definition, the same data and the same audit steps" names an exception that can never hold for a place below a change (its audit steps above differ), so it reads like a loophole that does not exist; the key chain is what makes the rule true (my section j.3). The tests (1) to (5): sign. |
| G25, G26 | SIGN | |
| G27 | SIGN WITH THIS WORDING (C11) | Add one row: "G20 a look-up table without the key column is not offered: its recipe fact stands (it declares no key; its tier 1 has no `sample_id`: Opus R7, Sonnet E); the engine refuses a removal there (Sonnet RD2); 'offered' described the old code." In the row "G3 tree ... G29 '7 tables'", add: "(G29: Sonnet's parse only)". In the row "G1 place; ...", add: "(G1's sentence on an empty tier 2 now rests on the engine and the step writer: `recipe_tiers.py:196-210`, `audit_copy.py:177-179`, Opus R5 at `T2:ResFinder`; not on the walk)". |

Recheck of the earlier signed points of `DESIGN_AGREED_AND_QUESTIONS.md` (their numbers, written DESIGN Gn; the table of G27 and my `OPUS_paths_2.md` section 10): consistent. CONFIRMED by rebuilt runs or by both parses: DESIGN G3, G4, G5, G11, G14, G15, G16, G17, G18, G19, G24, G26, G27 (demo claim), and G20 in substance. Standing (her words, recipe keys, checker code): DESIGN G1, G2, G6, G7, G8, G9, G12, G13, G21, G22, G23, G25, G30. VOID: DESIGN G10 (the column's fate from the walk), G28 (it describes the walk), G31 (it rests on "one place per tree"), and the old Q5 sentence that rested on `Hop`. STILL UNVERIFIED by me: DESIGN G29 (Sonnet's count only).

---

## 2. X1, coverage per incoming path

**SIGN WITH THIS WORDING (C12).** "**X1 Coverage per incoming path.** For a joined node: 'incoming paths from tables that hold the key with a chosen place: k of n', the uncovered tables named, and the paths from tables without the key counted apart (no removal by key can be written there: the engine refuses it, Sonnet RD2). After `T1:MLST`: `MLST_with_metadata` 1 of 2; `ST22_Anchor` 1 of 5 (and 1 table without the key); `AR1_MLST_Serotype_Virulence` 1 of 3 (and 1 without). It is structure, not a statement about the entity: k < n is necessary for the entity to remain below a removal, not sufficient." Reason: without the split, the 11 first places would show `ST22_Anchor` "5 of 6" although no place is left to choose there. [GRAPH SCRIPT; REASONED: a row reaches a table only through an incoming path]
- **My finding and its second instance are consistent with X1.** X1 says whether the entity CAN remain; the finding says that a place below can stay identical. In both instances k < n (`QA_fanout_exhibit` 1 of 3 under `T1:ResFinder`; `ST22_Anchor` 1 of 5 under `T1:FastP`) and the entity remains; the tables did not change for reasons X1 does not speak of (a count per sample; columns not among the final columns).
- **Information or a claim about the entity (her Q5; not decided here).** "k of n" is information: it tells her which incoming tables the step does not filter. It does not tell her the entity's fate: with the same "1 of 2" under the set of G14, the entity is gone from `MLST_with_metadata` (the covered table is its first table; the uncovered metadata is the second table of a left join) and stays in `QA_AMR_per_sample` (the uncovered metadata is its first table) [ENGINE RUN: Opus R5 (steps at `T1:MLST` and at `T1:ResFinder`: `MLST_with_metadata` 1 -> 0 rows of the entity, `QA_AMR_per_sample` 1 -> 1) and Sonnet D3; the first and second table: RECIPE FILE]. With the first table marked and the join kind (G25) she can read the fate herself; whether the app says it in a sentence is Q5.

---

## 3. The numbers that differ, settled by reading the outputs

| Numbers | Settled | Read in |
|---|---|---|
| 7 original tables (Sonnet) against 6 (Opus) | Two different sets, both right: the valid defaults with `T2:ResFinder` keep the entity in 7 tier-1 tables of original tables (also ResFinder); the nested defaults with `T1:ResFinder` keep it in 6. | `paths2/T1X.out`; `opus2_more.out` R11 |
| 11 nodes (ResFinder, the two readings) | Sonnet RD1 only. The 11 are: `T1:ResFinder`, `T1:QA_AMR_per_sample`, `T2:QA_AMR_per_sample`, `T1:QA_fanout_exhibit`, `T2:QA_fanout_exhibit`, `T1:ST22_Anchor`, `T2:ST22_Anchor`, `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `virulence_bar`, `virulence_variants`. The same under both ways of counting. | `paths2/RD.out` |
| 13 and 14 (Sonnet) against 12 and 13 (Opus convention) | The extra node is `T2:ResFinder_with_metadata` (no tier-2 steps, no plot), listed under both readings in `RD.out`. The text uses my convention: right. | `paths2/RD.out` |
| 45 / 17 / 35 of 97 pairs (G17) | My R14, registered before, gives the same numbers. | `opus2_r14.out` |

No other rerun was needed.

---

## 4. The questions and the half page

**Half page.**
- C13, item 2: replace "A node is a place (a table at a tier). The roots are the first places of the original tables." with "A node is a table at a tier, or a plot. The roots are the original data files; the leaves are the results." (as G1)
- C14, item 5: replace "We checked it for 55 places of the demo:" with "One of us checked it on the demo, with one entity, at each of the 55 places where the engine accepts a step:".
- C15, item 7: replace "leaves it in 7 original tables." with "leaves it in 7 original tables (6 when `T1:ResFinder` is used instead of `T2:ResFinder`)."
- C16, item 9: replace "(5 differ)" with "(5 tables differ for MLST, 11 for ResFinder)".

**Q1.** True and fair; her words exact (D-0555). No change.

**Q2.**
- C17: replace "and changes 3 ingredient lines" with "and changes 2 ingredient lines and 1 `right_ingredient` line" (as G20 and my R6).
- C18: row X, "for each joined table how many incoming paths hold a chosen place" becomes "for each joined table how many incoming paths from tables that hold the key hold a chosen place (X1)"; row W5, "computable; reopens D-0022" becomes "computable; reopens D-0022 ('only automatic placement "remove from all tables"') and touches D-0531 (the app cannot decide the scope): information".

**Q3.**
- C19, option (a): add "For the two tables made from the metadata alone, (a) is `T1:metadata_schema`: it lies above every join with the metadata, so it cannot be chosen in one step with your default of D-0549, and it is the place you call 'not advised' (D-0547)."
- C20, "What the two agents think", the Opus sentence becomes: "Opus: 'same level' read as the level of a joined table points to `T1:QA_L50_integer` (a table made from Quast alone, at the level of `Quast_with_metadata`); for `amr_heatmap` there is no table at that level, only ResFinder's own tier 2, so (b) is the nearest reading of your words there; a reading, not a lean." Reason: the present sentence is not one I wrote; this is what my position says (section 6).

**Q4.** C21: replace the paragraph "What the two agents think" with: "**Reopens (information).** Your decided form, the tier 1 of every table that holds the key (D-0416), and your rule of at most one place on a path (D-0553) cannot both hold in ONE step: as one step the 27 places hold 35 pairs one below the other. (a) keeps the places of D-0416 and writes them as two steps; (b) and (c) change the places of D-0416. **What the two agents think.** Neither agent chooses. (c) is the review session's reading and was not decided ('to be asked once when the plan is checked', ledger D-0550, not her words). [D-0416, D-0553, D-0549, D-0457]"

**Q5, Q6, Q7.** True and fair; quotations exact (D-0477, D-0543, D-0501, D-0546). No change.

**Order: which answer changes the others.**
- Q2 changes Q1 and Q6. With Y as a refusal each original has one reading table, and Q1 then only decides whether the original's own exported tier 1 is included; Y is a way of writing the recipe, so it is part of Q6.
- Q6 changes Q3: a declared default (Q6 c) answers Q3.
- Q3 changes Q4: option (c) of Q4 is Q3's defaults.
- Q5 depends on what is shown (Q2, X and X1).
- My proposal, not a demand: **Q2, Q1, Q6, Q3, Q4, Q5, Q7.** Q2 is the investigation she ordered "before we choose" (D-0556), and its answer decides whether Q1 and Q6 come up in full.

---

## 5. Closing line

**I sign `PATHS_AGREED_AND_OPEN_v1.md` with these 21 replacements, C1 to C21:** G1, G4, G8, G9, G10, G12, G14, G16, G22, G24 and G27 (C1 to C11); X1 (C12); the half page, items 2, 5, 7 and 9 (C13 to C16); Q2 (C17, C18); Q3 (C19, C20); Q4 (C21). I also propose the order Q2, Q1, Q6, Q3, Q4, Q5, Q7. Open between us: only whether the Sonnet agent accepts C12 (paths from tables without the key counted apart) and the proposed order; no point of substance is disagreed.
