# N7 (4): removal "country = Norway" along the lineage of MLST_with_metadata (ST22 dummy recipe)

Marks: RUN = I ran it; READ = I read it in a file. Two independent computations each time: the engine (RUN, `engine.py`, `s3_engine.py`) and my own plain Polars from the raw files with no project function (RUN, `s4_indep.py`). Compare: `s5_compare.py`.

## 0. Result of the check
RUN: 989 table results (about 55 scenarios x tables, Tier 1 and Tier 2) compared on rows, distinct samples, the sample ids themselves, Norway rows, rows with country missing. **0 differences.** The three id lists are identical in both (21, 28, 28).
RUN: the comparison can fail: after I broke my own code on purpose (Germany instead of Norway) it reported 74 differences. The engine on a copy of the recipe with no step gives the same tables as the shipped recipe (20 tables, both tiers, `s6_basecheck.py`).
Not independent: for ST22_Anchor, AR1 and QA_AMR_per_sample I compare samples only, not rows (rows depend on the gene joins). Not checked: statistics computed between steps (QA_population_zscore) after a removal.

## 1. The table and its lineage
READ: `MLST_with_metadata` is a join (MLST file + metadata file, left join on sample_id), with a Tier 2 that adds `era` and keeps year 2023-2025 (rows with year missing are removed). Same name as Eve's.
RUN: `build_plot_lineage("mlst_bar")` and `("year_distribution")` give the same back chain: file MLST -> MLST wrangling -> file metadata -> metadata wrangling -> MLST_with_metadata -> the plot. It looks only backward. `utils.recipe_graph` (forward lineage) is planned, not built (READ, home_stage2_mechanism_spec.md:106), so the forward part is my reading of the recipe: after MLST_with_metadata come only the plots `mlst_bar` and `year_distribution`; a plot has no step of its own and reads Tier 2.
Nodes I call: MLST (dataset, no country), metadata_schema (dataset, has country), J1 = MLST_with_metadata Tier 1, J2 = MLST_with_metadata Tier 2, plots (read J2).
READ: the engine does not read plot steps (Tier 3): `recipe_check.py:46`, `:887`. A tick on a plot cannot be run today; a plot shows the J2 numbers.

## A. Numbers with no removal (RUN, engine = own computation)
| Node | rows | samples | Norway samples |
|---|---|---|---|
| file MLST / dataset MLST | 42 | 42 | no country column |
| file metadata / dataset metadata_schema | 42 | 42 | 28 |
| J1 MLST_with_metadata Tier 1 | 42 | 42 | 28 |
| J2 MLST_with_metadata Tier 2 = plots mlst_bar, year_distribution | 33 | 33 | 21 |

Yes: 28 at the roots, 21 after the year filter. The 7 that go are the 7 Norway samples collected in 2022 (ids 20545497, 29208527, 50677095, 66108847, 71729785, 79062032, 82707226). Year filter 2023-2025 removes all 9 samples of 2022 (7 Norway, 1 France, 1 Germany): 42 -> 33. They are removed by the recipe's own step, not by the user.

## B. One ticked node at a time (RUN; engine = own computation)
Lists: L_T2 = Norway samples at J2, what the plot shows (21); L_ROOT = Norway samples in the metadata file (28). L_T1 (28) equals L_ROOT here. Step written: `modif_filter column country op ne value Norway na keep` (by property) or `modif_filter column sample_id op not_in value [list] na keep` (by ids).
Cells: samples at the ticked table, J1, J2 (Norway left in brackets). Before: 42 / 42(28) / 33(21).

| Ticked node | Has country? | By property | By ids L_T2 (21) | By ids L_ROOT (28) |
|---|---|---|---|---|
| MLST dataset | NO | refused: "column 'country' is not in the table"; MLST, MLST_with_metadata, ST22_Anchor, AR1 all fail to build | MLST 21; J1 21 (7 Norway stay); J2 12 (0) | MLST 14; J1 14 (0); J2 12 (0) |
| metadata_schema dataset | yes | metadata 14 (0); J1 42 rows stay, 28 with country missing, Norway 0; J2 12 | metadata 21 (7 stay); J1 42 rows, 21 country missing, 7 Norway stay; J2 12 | same as property |
| J1 | yes | J1 14 (0); J2 12 | J1 21 (7 stay); J2 12 | J1 14 (0); J2 12 |
| J2 | yes | J1 42 (28 still there); J2 12 (0) | same | same |
Plots after J2: 33 -> 12 samples in every row above (both plots).
Where the two lists differ: only in T1 level tables (MLST, J1, metadata): L_T2 leaves the 7 Norway-2022 samples; L_ROOT removes them. At J2 and in the plots the result is the same (12), because the year filter already removed the 7. After Apply, "the same condition evaluated again" (home_audit_steps.md:120) would report 7 samples still matching with L_T2, none with L_ROOT.
RUN: ids typed with a space (" 32557144") remove nothing and say nothing (42 stay).

## C. Several ticks together (RUN; engine = own computation)
C1: property at J2, J1, metadata_schema + ids L_T2 at MLST. MLST 21; metadata 14 (0); J1 21 rows, 0 Norway, but 7 have country MISSING (the Norway-2022 samples); J2 12. Same numbers with the ticks in reverse order (C1r), and with two steps at the same node in either order (C5, C5r: J1 14).
C2 same with L_ROOT at MLST: 14 / 14 / 14 / 12. C3 all by ids L_T2: 21 / 21(7) / 21(7) / 12. C4 all by ids L_ROOT: 14 / 14 / 14 / 12.
Order of ticks does not matter: the engine places each step by its position (dataset, then T1, then T2).
Removed twice? Not in one table. Per step (prefix runs): the first tick at MLST takes J1 from 42 to 21 and J2 from 33 to 12; the ticks at J1 and J2 then remove 0 more rows. A tick can be fully redundant and nothing says so.
Empty table: no. RUN (E1): ids of all 42 samples at J1 give 0 rows at J1 and J2, no error, no warning.
C1 trap: after ids L_T2 at MLST and property at metadata, J1 holds 7 Norway-2022 samples with country missing. The property step at J1 with na keep keeps them (21 rows); with na remove drops them (14 rows). Same ticks, different tables.

## D. Tables not after the ticked node, and tables with two paths (RUN)
28 tables in the recipe (56 results, Tier 1 and 2).
- D1 tick J1 by property: only J1 and J2 change (54 of 56 results identical, including the datasets before it). Tables not after the node do not change.
- D3 tick MLST dataset by ids (28): MLST, MLST_with_metadata, AR1 change (AR1 42 -> 14 samples, 342 -> 116 rows). ST22_Anchor does NOT lose them: 42 samples stay, 28 of them with sequence_type missing (RUN, `s9_st.py`). MLST is the base of AR1, a lookup side of ST22_Anchor.
- D4 tick FastP dataset by ids: FastP_with_metadata and QC_Reads_Anchor 42 -> 14. ST22_Anchor (FastP a lookup side) unchanged in rows and samples.
- D2 tick metadata_schema by property: 14 of 28 tables change. Where metadata is the BASE (ST22_Anchor, the six QA tables that start from it): 42 -> 14 samples. Where metadata is the LOOKUP side (FastP_, Quast_, Bracken_, ResFinder_, MLST_with_metadata, QC_Reads_Anchor, AR1): all 42 samples stay, the 28 Norway ones with country missing (rows with country missing: Quast 84, ResFinder 45, AR1 226). In MLST_with_metadata Tier 2 the year filter then drops them (33 -> 12), only because their year is also missing.
- D7 tick FastP and metadata by ids: QC_Reads_Anchor (reached from both) 42 -> 14 samples; with only metadata ticked (D6) it stays 42 with 28 country missing; with only FastP ticked (D4) 14. Property and ids on metadata give the same tables (D2 = D6).

## E. What M111 does not settle (for Eve)
1. Where the ids come from for a ticked table without the column. Example: MLST dataset ticked: L_T2 -> 21 samples left (7 Norway-2022 stay in T1); L_ROOT -> 14 left (none). Plots and J2 are identical (12). Options: (a) the table where the selection was made (what the user saw, 21); (b) the root (28, the full meaning of "country = Norway"); (c) show both counts, user picks. Default I suggest: (b) shown with the count of (a), because the after-check then finds 0 Norway.
2. A removal by property keeps or drops rows with the property missing (`na`). Example: C1 J1 21 rows (na keep) or 14 (na remove). Options: keep (default, nothing removed silently), remove, ask with the count of rows concerned.
3. A tick on the lookup side of a join does not remove samples. Example: metadata ticked, FastP_with_metadata 42 samples stay with 28 country missing. Options: show per descendant "removed / stay with the value missing" (default); warn only; offer the ids at the base table.
4. A tick on a dataset reaches every table built from it, also far from the plot. Example: metadata ticked changes 14 of 28 tables. Options: list all of them with counts (default); list only the tables on the plot's lineage; ask.
5. The same samples removed at one place stay in another that uses the table as lookup. Example: MLST ids ticked, ST22_Anchor keeps 42 samples, 28 with sequence_type missing. Options: say so in the dialog (default); offer to tick ST22_Anchor by ids too.
6. T1 or T2 of the selection table. Example: tick J2: T1 still shows 42 samples with 28 Norway, T2 12; tick J1: T1 14. Options: user chooses with both shown (default); always T1.
7. A tick that removes nothing new (redundant) or removes everything (0 rows). Examples: C1 ticks at J1 and J2 after the MLST tick remove 0; E1 gives 0 rows silently. Options: show "removes 0 more" per tick (default); refuse an empty table; no check.
8. Ids typed or pasted with a space or another case remove nothing and say nothing. Options: report "n ids matched, m not found" (default); strip silently (not recommended: silent).
9. Plots cannot be ticked today (the engine has no reader of plot steps). Options: offer plots only as "read" information (default until the reader exists); build the reader first.
10. Defaults: sentences below say all places are ticked by default; M111 says the user ticks. Eve to say which default.

Sentences that say the app spreads or ticks by itself (READ):
- home_audit_steps.md:118 "ticked at every node that has that column (the default "everywhere")".
- home_audit_steps.md:134 "all are ticked by default, and the user unticks what must not change. "Everywhere" simply means every node where the field exists."
- home_audit_steps.md:135 "The only automatic placement is "remove these samples from all tables"."
- home_audit_steps.md:138 "Defaults: the place the user chose is ticked; for "remove from all tables" every table that has the ID is ticked; other places ... are listed unticked" (same line also says "there is no automatic spreading" and "Nothing is written that is not ticked and listed": consistent with M111).
- home_audit_steps.md:138 "lineage backwards from the chosen node to its roots ... and then forwards to every descendant": a display of effects, not a scope.
- home_stage2_mechanism_spec.md:128 "ticks default to all".
- home_stage2_mechanism_spec.md:129 "for each ticked node, one insertion" and :72 "each ticked table is filtered by your condition": consistent with M111.
- home_audit_steps.md:123 example: one ids filter with the 28 Norway samples written at T1 of six tables: uses the root list (28), not the selection list (21).
- home_audit_steps.md:119 "Nothing is automatic; the user decides with the information": consistent.

Files: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/round7/n7_4/` (engine.py, scenarios.py, s3_engine.py, s4_indep.py, s5_compare.py, engine.json, indep.json).
