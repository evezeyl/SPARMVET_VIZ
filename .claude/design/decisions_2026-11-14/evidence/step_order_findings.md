# N13: why HOME and the exported recipe disagree (drop and filter on one column)
Labels: RUN = I ran it (scripts + raw output in this folder), READ = read at file:line, INFERRED = reasoned, not run.
Scripts: `repro.py` (output: `repro_output.txt`), `check_and_scopes.py`. Recipe: shipped `1_test_data_ST22_dummy`, join QA_population_zscore (T2 = 42 rows: sample_id, country, n50, n50_zscore). Threshold n50 >= 324189 keeps 21 of 42.

## 1. Answer to Eve: sequential or not?
- The EXPORT is sequential: steps in recorded order, one after the other (t3_translator.py:153-165 translate_plot_steps and :257-271 build_mode2_recipe keep the list order). The engine runs the list top to bottom.
- HOME is NOT sequential. It does not replay the recorded steps. Three places, three different orders (all READ, confirmed by RUN):
  - data table (home_theater.py:1346-1352) and results-bundle `T3_data_<plot>.tsv` (export_handlers.py:1172, `audited_frame` 220-230): ALL filters first, then ALL drops.
  - plot (home_theater.py:483-505 and 531-533) and the plot in the results bundle (export_handlers.py:1001-1035): ALL drops first; then VizFactory applies the filters (viz_factory.py:152-225).
  - Both HOME paths SKIP a filter whose column is not in the table, without a message (t3_audit_engine.py:112, viz_factory.py:173; issue #56 behaviour). The export has no such skip.
- Why it fails: NOT a Polars problem. Plain Polars in recorded order gives the same error (RUN: "unable to find column n50; valid columns: sample_id, country, n50_zscore"). A recipe is a linear list; "drop n50, then filter n50" is nonsense in any linear run. HOME hides the nonsense by regrouping (table) or by skipping (plot).

## 2. How a user records it (READ unless said)
- Filter panel offers the columns of `_resolve_active_lf(spec)` = stored T2 WITHOUT the audit drops (filter_and_audit_handlers.py:164; home_theater.py:270-291). So a dropped column is still offered. The drop selector hides already-dropped columns (home_theater.py:1388), the filter form does not.
- No check at recording: `_filter_add_row` (357), `_filter_send_to_audit` (443) and `_col_drop_to_audit` (522) never compare with the other steps. The design promises "adding a filter on a column already dropped is not possible" (home_audit_steps.md:326, DECIDED but not built).
- Storage: a drop is one node per plot (`drop_column`, propagation can copy it to other plots with the same id); stacks are per plot `t3_audit_steps_by_plot[plot_scope]`, new nodes appended in commit order (audit_stack.py:209-211). Order = order of Apply, within one Apply = order of creation (INFERRED for within-Apply).

## 3. Which export uses which path (RUN, cases A-B)
- Results bundle: `T3_data_<plot>.tsv` = same as the HOME table (filters, then drops). Its plots = same as the HOME plot (drops, then filters, filter skipped). So the results bundle disagrees WITH ITSELF: case B, TSV 21 rows, plot of the same bundle 42 rows.
- Reproducibility bundle: recipe with the steps in recorded order, re-run by the engine. It agrees with the table in case B and fails in case A. The bundle is written without running it or checking it (export_handlers.py:1223-1231); `check_recipe` (profile run) returns the same 7 advice codes for A and B and nothing about order (RUN).

## 4. Pairs, both paths vs export (RUN; "plot" = HOME plot = results-bundle plot, 42 rows in the base)
| Recorded steps (n50 not used by the plot) | HOME table / T3 TSV | HOME plot | Export re-run | Verdict |
|---|---|---|---|---|
| A drop n50, THEN filter n50>=thr | 21 rows | 42 rows (filter ignored) | ERROR "modif_filter: column 'n50' is not in the table" | export FAILS; table and plot differ SILENTLY |
| B filter n50>=thr, THEN drop n50 | 21 rows | 42 rows (filter ignored) | 21 rows, same as table | export OK; PLOT silently wrong (no filter) |
| E drop n50, THEN exclusion_row on n50 | 41 rows | 42 rows | ERROR same message | export FAILS; plot silent |
| H drop country, THEN filter country (plot uses country) | 28 rows | plot ERROR (x unknown) | ERROR | all three fail differently |
| I filter country, THEN drop country | 28 rows | plot ERROR | 28 rows | table = export; plot breaks |
| C filter, THEN filter (same column) | 21 | 21 | 21 | agree |
| D exclusion sample_id, THEN drop n50 | 41 | 41 | 41 | agree |
| F drop n50, THEN drop country | 42 rows, 2 cols | plot ERROR (x gone) | 42 rows, 2 cols | table = export |
| G drop n50 twice (not reachable: selector hides dropped cols; INFERRED) | 42 | 42 | ERROR (polars "n50 not found") | export fails |
- Different plot scopes (RUN): two plots on one join, plot 1 with a drop of n50, plot 2 with a filter on n50, give two separate forks, each with only its own steps. HOME reads the same per-plot stacks. No interference.
- SILENT differences (matter most): in cases A, B, E the plots in HOME and in the results bundle show ALL rows although a filter/exclusion was audited, while the table, the TSV and (B only) the reproducibility recipe have them applied. A second silent trap: any filter on a column absent from the plot's table is skipped by HOME with no message.
- No test covers a drop plus a filter on the same column through the plot path (grep of app/tests: drop_column only in test_step_order.py, test_session_manager.py, test_writers_emit_format_one.py; test_step_order.py uses `audited_frame` only, never the plot).

## 5. What is decided
- DECIDED `ui_implementation_contract.md:203` rule 3: "same steps and order as the HOME data preview" - true for the TSV, false for the plot and the export order. Rule 4 (line 204ff): audited steps are always applied to the exported plot.
- DECIDED home_audit_steps.md:142 (5a point 11) and :318: at the same node row filters and drops "commute", "order does not matter". This is false for a filter and a drop on the SAME column (RUN, A vs B). Not decided: that case (test_step_order.py header says so).
- DECIDED home_audit_steps.md:323-326: a step whose column is gone is "Broken", export refused; creating a filter on a dropped column "not possible". Not built (READ above). Design, not as built.
- DECIDED ADR-097 (architecture_decisions.md:4723): T3 reaches the engine through a forked recipe; order of the plot's own list kept (t3_translator.py:154-155 docstring). ADR-099 (:4956): not built, amends ADR-097; steps written at T1/T2/T3 in dataflow position.
- CONFIRM / not confirmed by Eve: home_stage2_mechanism_spec.md v0.1. Its P5 (line 61) replaces the per-plot fork by the audit copy of the recipe and "the audit view reads the copy" (line 49, :7 View). Then the HOME table/plot are read from the same copy the export writes, so one order, the recorded one, for all views. It does not itself say what to do with a filter on a dropped column (that stays the guard-rail registry, P6, line 62). Tests in test_step_order.py would move to that copy.
- OPEN: what a user should see when a filter targets a dropped column (refuse, warn, reorder); not decided anywhere I found.

## 6. Where a fix could live (facts only; what each does to sessions saved before)
1. Panel refuses/warns when recording (filter_and_audit_handlers.py:357/443/522, or filter form column list at :164). Old sessions: stored steps stay as they are; a saved drop-then-filter stack is untouched and still disagrees until edited.
2. HOME runs the recorded order (home_theater.py:483-533, :1346-1352; audited_frame 220-230; VizFactory filters at viz_factory.py:152-225). Old sessions: their views CHANGE (case A table would turn into an error/empty; case B plot would start showing the filter); no stored file is rewritten.
3. Translator reorders (t3_translator.py:153-165, 257-271). Old sessions: exports change; recorded list is not touched; frozen module (ADR-097) and contradicts "recorded order" (test_step_order.py:348).
4. Checker (export-time run of the written recipe, or `check_recipe` tracking columns). Old sessions: nothing changes in HOME; exports get refused or flagged. Today check_recipe does not look (RUN).
Not checked: the real Shiny panel by clicking (read-only analysis); gallery recipes other than the shipped one; steps pending (uncommitted); `developer_raw_yaml` nodes; the importer's verification legs.
