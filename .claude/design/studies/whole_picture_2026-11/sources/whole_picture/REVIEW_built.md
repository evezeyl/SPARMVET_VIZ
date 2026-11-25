# Review of WHOLE_PICTURE.md: the claims about the code, and the run (2026-11-22)

VERDICT: FIX FIRST (small edits, not a redesign). About 120 claims checked. The run is sound and was reproduced with three entities. Scratch: `../SPARMVET_VIZ_wt_whole_picture/tmpAI/review_built/` (`rerun.py`, `out_<sample>.txt`, `scan_t2_meta.py`).

## 1. Claims NOT TRUE, or true at another place
| # | Place and sentence of the document | What the code or the run says | Evidence |
|---|---|---|---|
| 1 | Flag 7, 3.14, row N2, slice 2: "the HOME upload replaces a recipe of the same name without a word" | DEAD CODE. The handler exists but NO user space mounts its button or its file input (`btn_ingest`, `file_ingest` appear only in the handler and in a CSS selector). HOME cannot replace a recipe this way. `app/tests/test_ingestion_handler_reachability.py` records it ("dead code") and that the handler would exit if it ran. The copy line is real but unreachable. REMOVE it from the things wrong today; state it as: an unreachable handler that would overwrite if it were ever mounted. | `app/handlers/ingestion_handlers.py:38-55`; grep over `app libs config assets`; the test file lines 1-37 |
| 2 | Slice 2 "uploading the demo recipe again is refused ... NO ANSWER NEEDED" | The test cannot be written: no upload exists. The real choice (remove the dead handler, or mount an upload correctly under the deployment's upload place, D-0417, D-0418, D-0440) is NOT decided. Not "no answer needed". | as row 1 |
| 3 | Flag 3, 3.3, row I1: the held branch `task/remove-from-all-ticked` "adds `stays_by_choice`"; "16 stays by your choice" | STALE. The branch tip (`95b6285e`) replaced it by `unticked_places` with three kinds (stays, removed upstream, cannot say), read from the join kinds. A second review found that version false too: see `EVIDENCE_untick_branch_reviews.md` (a false "stays" on the demo with the real engine: `ST22_Anchor`; a false "removed upstream"). Describe the branch at its tip and cite that evidence. | `git show 95b6285e` |
| 4 | Flag 2 and the table of 4.1: under reading (a) the entity stays in 3 quality plots "with its `source`, `year` and `country` emptied" | True for `qc_reads_horizontal_barplot` only. For `assembly_quality_dotplot` and `miaou` only `source` and `country` are emptied: their table `Quast_with_metadata` has no `year` column. The consequence for `miaou` (it draws `source`) stands. | `out_*.txt`; `wrangling/Quast_Metadata_wrangling.yaml` |
| 5 | Flag 4, 3.13, rows X4, X6: the export has "no original recipe, no audit log and no audit record" | OVERSTATED. `t3_steps.yaml` holds each step's `reason` and `committed_at`; `effective_run.yaml` carries a hash of HOME's own step list. Truly absent: the audit recipe; its record with its hash (D-0333); the log of added and removed steps, initials, the warnings shown (D-0478). With NO audit step the reproducibility recipe IS the original recipe plus the baked seeds: "no original recipe in any part" is true only when an audit exists. | `export_handlers.py:1510-1546, 1561-1570` |
| 6 | 3.12, row R7: `session_handlers.py:556` | The warning is at lines 594-602 (556 is another notice). The behaviour (warns and opens) is true. | `session_handlers.py:594-602` |
| 7 | 3.5: the button title "...cannot be silently discarded once committed" is "untrue" | Arguable: the removal shows a notification, so it is not silent. The "applies only to T3" part is true. | `filter_and_audit_handlers.py:674-676`; `audit_stack.py:675-682` |
| 8 | Row S10: "called from `home_theater.py:2513`" | True through `define_opening_server(...)` of `app/handlers/opening_handlers.py`; `opening_build` is imported at `home_theater.py:58`. | |
Also: `app/modules/bundle_importer.py:252-273` never overwrites: it builds a new unique id (`<id>_imported_<time>`); "refuses an existing name" is not what it does.

## 2. Verified TRUE (so they can stay)
- Flag 1: `_can_write_audit_step()` is `_in_audit() and data_view == "T3"` (`filter_and_audit_handlers.py:152-155`); the text "Audit steps apply to the plot's table (T3) for now." (`home_theater.py:1479`).
- Flag 4, the three forms: HOME's node list (`session_manager.py:56-106`); `libs/utils/src/utils/audit_copy.py` whose only callers are `remove_from_all.py` and `plan_composer.compose_candidate_plan_book`, themselves called only by tests; `audit_run.py` has no non-test importer; the export's fork `build_mode2_recipe` named `<join>__t3_<plot>` (`t3_translator.py:197-290`, `export_handlers.py:1561-1564`).
- Flag 5: `view_key` = (recipe, mode, data choice, source table, open plot) (`t3_audit_engine.py:69-73`).
- Flag 6: T1, T2, T3 are those of the open plot's target table; Source is one raw file (`home_theater.py:327-348, 485-518`).
- Flag 8 (behaviour). Flag 9: the code clears the filters on a mode switch (as D-0361 says).
- Sections 3.1, 3.2, 3.4, 3.6, 3.8, 3.9, 3.10, 3.11, 3.15, 3.16, the stale texts of 3.5 and 3.18; all 19 rows of kind CONTRADICTS, BUILT BUT OLD, BUILT BUT PROVISIONAL (row I1 true for `dev`, stale for the branch); 30 random rows AGREES and NOT BUILT.

## 3. The run on "the earliest place": reproduced with three entities
Entities: 10668076 (the author's), 51573804 (in all 11 files), 52676003 (absent from ResFinder). The author's output was reproduced exactly; the two others give the same pattern.
| Statement | Reproduced? |
|---|---|
| (a) from `mlst_bar` (the removal at tier 1 of `MLST` and of `metadata_schema`): 2 steps; 13 plots change; the entity STAYS in 7 plots (6 for the entity absent from ResFinder) | yes |
| (a): metadata columns emptied in the three quality tables and plots | partly: `source`, `year`, `country` in one plot; `source`, `country` in the two others (finding 4) |
| (b) narrow (the end of tier 1 of `MLST_with_metadata` only): 1 step; 2 plots change | yes |
| (b) wide (the end of tier 1 of every table that joins the metadata): 13 steps; 13 plots change; 4 plots keep the entity (3 for the one absent from ResFinder); nothing emptied | yes |
| "Remove from all the data": (a) 11 steps, the entity in no plot; (b) 19 steps, in no plot, and 8 original tables still hold it | yes |
| Her case (keep the entity in the quality results only): under (a) 4 plots keep it WITHOUT its metadata (9 plots when the metadata is also unticked); under (b), with `QC_Reads_Anchor` and `Quast_with_metadata` unticked: 17 steps, the entity stays in exactly the 3 quality plots WITH its metadata | yes |
WHY the metadata is emptied under (a): a LEFT join whose second table lost the row. In `FastP_with_metadata`, `Quast_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `MLST_with_metadata` the data table is first and `metadata_schema` second (`how: left`); in `QC_Reads_Anchor` FastP is the base and the metadata is the last of three left joins; in `AR1_MLST_Serotype_Virulence` MLST is the base. Under (a) from `mlst_bar` the entity is removed from `MLST` and `metadata_schema` only; `FastP`, `Quast`, `Bracken` still hold it, so the left join keeps the row with empty metadata columns. In `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore` the metadata is the FIRST table, so removing it there removes the row.
Limits of the run to state: the place lists (a) and (b) are written by hand in the script, not derived by a rule; "the plot holds the entity" is counted for the 16 of 17 plots that have the key column (`qa_aggregated_no_key` has none); it uses the library's run of the audit copy, not HOME's screen; three entities. The z-score case (-1.254 against -1.336) comes from the trial's synthetic recipe and was not rerun; on the demo, computations across entities sit in tier 2 (true).

## 4. The demo facts: all TRUE
13 tables join `metadata_schema`, all in tier 1. Four plots read a table that never meets the metadata: `amr_heatmap` (`ResFinder`), `phenotype_genome_length_fragmentation`, `qa_sequence_type_missing`, `qa_l50_integer`. `Quality_metrics` and `Detailed_summary` are read by no plot and no join. Six tables no plot reads. `VirulenceFinder` is under `additional_datasets_schemas` and carries the entity key; `APEC_STEC_virulence_genes` has no entity key and is read by `ST22_Anchor` and `AR1_...`. 11 original tables with the key + 16 joins = 27 tables. A scan of 141 loadable recipe files (14 with joins): NONE joins the metadata in tier 2, so the rule of D-0510 breaks no shipped recipe.

## 5. The slices
- Slice 0 (records): true; add the correction of the `stays_by_choice` description.
- Slice 1 (the filters follow the table): buildable from D-0505 and D-0506; the notice cause 4 ("you opened another plot") needs the same edit; same files as the "between" branch.
- Slice 2: NOT "no answer needed" (dead code; see 1 and 2).
- Slice 3 (one representation of an audit step): it is BIGGER than "points today's dialog at the new representation": HOME's plot and table would move from the in-memory `audited_frame` to an engine run of the audit copy (`audit_run` and `compose_candidate_plan_book` have no running caller today). Unstated consequence: the session file format number changes, and by D-0312 sessions saved in the older format are refused: users lose their saved sessions. Say so.
- Slices 3 and 4 both change `filter_and_audit_handlers.py`, `audit_stack.py`, `session_manager.py`: the order 3 then 4 is forced; say why. Slices 5 and 6 both change `export_handlers.py`. Slice 6 stops reading `ui_title` and slice 7 (the names pass) touches those keys: 6 before 7, or one pass.
- Slice 10: "no answer needed" holds for the shipped recipes (the scan above).

## 6. "What the document did not check" misses
The reachability of the ingest handler; the branch read at an older commit; that the kinds of the branch may fall under D-0501; that the count "the plot holds the entity" excludes one plot.

## Not checked by this review
The ledger text; any browser behaviour; the z-score trial; whether the numbers hold from HOME's screen rather than the library's run.
