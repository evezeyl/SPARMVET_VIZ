# LBFB review 1 (branch task/lbfb, 4 commits on 6f30944f) - reviewer, 2026-11-20

VERDICT: MERGE AFTER FIXES (bring it up to dev first; 2 mechanical fixes, then 5 small ones the owner or the builder can order).

## Evidence labels
RAN = I ran it; READ = I read file:line. Scratch: this folder (hand.py, silent.py, steps.py, unread2.py, two_stores.py, seeds.py, demo_spot.py, run_mut.py, mut_results.json, merged/ = dev + branch overlay).

## Baseline
- `libs/utils/tests` on the branch, worktree first on PYTHONPATH (RAN: utils.__file__ = .claude/worktrees/lbfb/libs/utils/src/utils/__init__.py): 2599 passed, 1 skipped (15.6 s, -n 4).
- Demo rerun (RAN `run_demo.py 1_test_data_ST22_dummy`): 85 nodes, 523 columns, 0 failures, 3.3 s. Fresh numbers (join_linked): 6586 lines, 5407 tick, 1179 grey (no_step_list 741, step_not_read 267, change_not_followed 171), gone notes 1554, unread 950.

## Merge readiness (RAN git merge-tree HEAD dev)
Two conflicts, both text only: `libs/utils/src/utils/join_keys.py` (the @deps `provides`/`consumed_by` lines: dev added recipe_join_keys and key_drop_problem, the branch added suffix_of and the step_effects consumer; keep the union) and `libs/utils/tests/test_recipe_graph.py` (both sides appended tests; keep both).
After a scratch resolution (merged/): all 58 tests of test_lineage_walk*.py pass except ONE, confirmed: `test_lineage_walk_properties.py:69-70` `test_I1_...` calls `audit_copy.audit_recipe_of(recipe)` (no longer exists) and `audit_copy.add_step(copy_, place, step, "audit_1a2b3c4d_1")`. On dev: `copy_ = audit_copy.start_audit(recipe)` (returns AuditCopy) and `audit_copy.add_step(copy_, place, step, "reason text")` (4th argument is now the reason, a non-empty text; the id is written by the copy and returned). With these two edits the test passes on the merged tree (RAN, 58 passed). Other failures in my scratch run came from `app/` and `config` not being in the overlay (not the branch).

## Findings by weight
### Must fix before merge
F1. test_I1 uses the old audit_copy API (above). F2. @deps conflict in join_keys.py (above).

### Should fix (decided lines not met or a checker that cannot see)
F3. D-0357, D-0352, D-0353, D-0337 are decided and NOT built: a rename across tiers (a to b in T1, b back to a in T2), a cast, a recompute and a group-by aggregate make every line on the other side of the change GREY `change_not_followed` instead of ticked with a note (RAN steps.py: "RN a->b T1, b->a T2; start a at P": DS:S and T1:S grey, T2:S and T3:P tick; start b at T1:S: T2:S and T3:P grey; "cast J1 only", "groupby", "one-path rename": same). Disclosed by the builder as P3 and marked in `lineage_walk.py:25-27`; but until it is built the dialog cannot offer what D-0357 ("one column") and D-0353 ("the place is offered and ticked") say. In the demo 171 of the grey lines are of this kind. Decision status: not covered; do not merge as "LBFB done", only as "step 1".
F4. `step_effects.READINGS` is not the source of truth the docstring says. `effect_of` hardcodes every reading; nothing reads `READINGS` except one test. RAN mutant R8 (effect_of reads `polars_explode` as KEEPS, READINGS untouched): 87 tests pass, SURVIVED. The test `test_everything_else_is_unread_with_a_reason` only checks 16 listed shapes. Fix: a test that every registered action outside READINGS and ROW_STEPS gives `UNREAD`, or make `effect_of` look the action up in READINGS.
F5. `Unread.holds` is not tested. RAN mutant R2 (`holds` always True): SURVIVED. A join no plot reads that dropped the column must say `holds=False`.
F6. Source lines. D-0355 words ("all_raw data ... a way to choose") and D-0359 ("every place starts ticked") against D-0332 (a source file holds no step list): the walk returns a DS line for every source and it is ALWAYS grey `no_step_list` (P1b, marked PROVISIONAL), so choosing level "source" never gives a tickable line. In R2 of my recipes (S with no tier 1 steps) the DS:S line and T1:S line are the same table, which D-0346 says is not offered twice ("only distinct tables are lines"). This is a question for Eve, not a fix.
F7. A start that selects nothing gives an empty Walk with no word: start `junk` at T1:U (a table no plot reads), levels=(T3,) returns lines=(), gone=(), unread=() (RAN silent.py "e U start levels T3"). D-0195 "no silent failure": the Walk carries `levels` but nothing says "the column exists at places of the other levels". Low risk, but the dialog needs a way to say it; no test.

### Small
F8. Unmarked behaviours (the builder lists P1-P8; these are not marked): (a) a line is ticked when ANY path from the start is certain (0-1 cost search, `_costs`, lineage_walk.py:~278): grey only if every path is uncertain; (b) a DS line next to the T1 line when T1 has no steps (F6); (c) the place at level T2 can be the T1 line (covers) - supported by D-0346 and the owner's fall-back words, but not marked; (d) a group is the smallest group that reaches the place (`setdefault` order) - the split lineage/join_linked depends on where the user clicked while the union does not (demo: sample_id from mlst_bar and from amr_heatmap give the same 7 DS + 17 T1 + 16 T2 + 14 T3 lines, with the l/j letters swapped), marked P1 but the consequence for L014 is only in the test name; (e) `Gone.removed_by` is the nearest removing step by graph order, an arbitrary choice when two paths remove it.
F9. Two stores of "what a step does to the columns": `RecipeGraph._flow` (recipe_graph.py:321-350) and `step_effects`. RAN two_stores.py: `polars_select exprs=[]`: graph says no columns, reading says unread; `polars_select` with an extra key `strict:false`: graph says unknown, reading reads it; a join: graph unknown, reading follows it. No harm today (the walk does not call `columns_provider`/`column_info`), but the two can disagree the day both are used.
F10. `Reach` holds frozensets: iteration order and repr change with PYTHONHASHSEED (RAN seeds.py with 4 seeds: identical once sets are sorted, different raw). The builder's seed test sorts the sets (`plain`) so it cannot see this. A dialog must sort.
F11. `test_lineage_walk_properties.py:205` writes `sys.path.insert(0, ...)` in a subprocess snippet: `rules_runtime_environment.md` section 3 forbids it in tests, including test code.
F12. No `tasks.md`, ledger, dependency-index or UML entry in the diff (workspace_standard 5-E and the UML/ADR sync law). Acceptable for a function nothing calls yet; the scribe step after merge.
F13. `join_keys.py` @deps `consumed_by` lists `step_effects.py (suffix_of, key_columns, ROW_STEPS)` but `provides` does not list ROW_STEPS (old omission).

## Decisions: complied / contradicted / not covered
- D-0347 back-forth-back: complied (lineage_walk.py:`lineage_set` then `_classify`; RAN hand recipes 1-5, 0 differences from my hand work). Third move (say what is true there): only partly, see F3.
- D-0346: complied for the collapse and the reach (`_build_places`, `_build`; RAN R4: T2 level returns the T1 line with covers T1,T2); the "only this plot" line always (P8). Tension noted in F6.
- D-0351 / D-0356: complied: READINGS = rename, join, drop, select + with_columns, cast, group_by (7), names only; each reading checked (`agreement_problem`); disagreement is grey READING_DISAGREES. No expression is parsed (grep: no eval/ast/re in the four modules; `_plain_names` only refuses a string with space, dot, bracket or `pl.` as "not a name"). F4 is the weakness.
- D-0195: complied in my probes (see below).
- D-0355: complied for the choice of levels (no default, `LineageError` for none or a wrong level); no group by name alone (`Outside` is information, M26 killed).
- D-0357, D-0353, D-0352, D-0337: NOT covered (F3).
- D-0358 (key drop refused by place) and D-0359 (all ticked), D-0332 (audit_steps): not in this branch (disclosed: step 4); `kind="drop"` gives the same lines as a filter; D-0359 is only "state == tick" and the dialog does not exist.

## Hand-worked recipes (RAN hand.py, steps.py; every line compared with a prediction made before the run)
R1 chain A->J(B)->P with rename y->z in A: x from P at levels all: DS:A grey no_step_list, T1:A, T1:J, T3:P tick; B absent; reach T1:A = 2 tables 1 plot. Levels T1: T1:A, T1:J; T2: same two (covers); T3: T3:P only; source: DS:A only. `z` from P: DS:A grey change_not_followed(rename) with occurrence `y`, T1:A tick `z`. As predicted.
R2 A table read by two joins (J1, J2 both S+M, plots P1, P2): `c` from P1: DS:S, T1:S (reach 3 tables 2 plots), T1:J1, T1:J2, T3:P1, T3:P2 all in the lineage group; `id`: also DS:M and T1:M (key equated). As predicted.
R3 plot P2 with own tier 3 steps, P1 without, both read S: levels T3 from P1 or P2: both T3 lines (tick, reach 1 plot each); levels T2: T1:S (reach 2 plots). As predicted.
R4 join with empty tier 2 read by two plots: levels T2: T1:S and T1:J (covers T1,T2); T3: P1, P2. As predicted.
R5 column dropped in T2 of S (still in T1), S read by P, J (S+B) read by Q: d from T1:S: lines T1:S, T1:J, T3:Q tick; Gone T2:S and T3:P (removed_by `data_schemas.S.tier2.steps[1]`). As predicted. Extra: for a drop at T1:S the T2 `drop d` step will then fail in the engine; the walk does not warn (D-0358, step 4).
Differences from my hand work: none. Only places where the builder's design differs from what the owner wrote: F3, F6.

## No silent loss (RAN silent.py, unread2.py)
Missing plan entry: `PlanBookIncomplete` at index build (loud). Failure mid path: the failing table and everything below grey `plan_failed` with the engine's sentence, the table above stays tick. Failure at the start: `StartPlanFailed`. Step the readings do not know (unpivot): column vanishing -> grey step_not_read, never a Gone; unchanged same-type column passes with a note `unread_step_passed`. Column twice (self join): grey `several_columns`, both occurrences listed. Levels none / wrong: `LineageError`. Levels that select nothing: F7. Start at an empty tier (`T2:J`): same lines as `T1:J`. Start node unknown or column absent: `LineageError` / `ColumnNotFound`.

## The four cases of point 4 (what the code does)
1. Only T3 chosen, no plot has tier 3 steps: one tick line `T3:<plot>` for every plot in the lineage of the start, each reach 1 plot, none for tables. Supported by D-0346 ("there is also a line for one plot only ... even when the recipe has no tier 3 steps"); the other D-0346 sentence ("the line is the lowest level of the lineage that really has steps") would give the T2 line instead.
2. Only T2 chosen and the join has no tier 2 steps: the T1 line is returned (its `covers` holds T2:J); supported by D-0346 ("a join without tier 2 steps is the same table as its tier 1") and the owner's "Tier fall back". Same for a source with no tier 2.
3. "Only this plot" line for a plot with an empty tier 3: always returned (lineage_walk.py `_build_places` never collapses T3; P8).
4. Only level T2 and T2 has steps and a plot reads it: the T2 place (own line).

## Readings (point 5): names only; no formula string is parsed or evaluated (grep). Shape not expected -> `unread` with a reason (16 shapes tested). Not one source of truth: F4, F9.

## Purity (point 6): `lineage_walk`, `step_effects`, `plan_book`, `lineage_records` import only `utils.*` and the standard library (grep); no Polars, no Shiny. Determinism: 4 other seeds (11, 222, 3333, 4): identical after sorting the sets; raw sets differ (F10).

## Mutants (RAN, my runner copy, results in mut_results.json)
Builder's 43, I reran 9: M3, M8, M14, M17, M25, M26, M29, M36, M42 - all KILLED (1 to 11 tests each). Mine: R1 (reach forgets plots of a sibling join) KILLED (36 tests; may be killed by a crash of my patch, not proven semantic); R3 (levels filter lines but not gone/unread) KILLED (2); R4 (`_outside` returns nothing) KILLED (3); R5 (`found` counts grey) KILLED (2); R6 (note names no line) KILLED (1); R7 (an empty tier 2 read by a plot is a place) KILLED (37); R2 (`Unread.holds` always True) SURVIVED; R8 (unlisted action read in effect_of) SURVIVED. Two survivors = F4, F5.

## Demo spot-check (RAN demo_spot.py; read against config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml)
sample_id from mlst_bar (reads MLST_with_metadata = MLST + metadata_schema) and from amr_heatmap (reads ResFinder directly): both give the same 7 sources, 17 T1, 16 T2, 14 T3 lines; right: (1) T1:MLST, T1:metadata_schema, T1:MLST_with_metadata lineage group from mlst_bar; (2) T1:FastP/Quast/Bracken/ResFinder/VirulenceFinder join_linked from mlst_bar (linked through metadata_schema joins); (3) T1:QC_Reads_Anchor, T1:ST22_Anchor, T1:QA_AMR_per_sample forward from metadata_schema: lineage; (4) T1:ResFinder, T2:ResFinder both lines (T2 has 2 steps, plot amr_heatmap reads it); (5) T2:ST22_Anchor, T2:MLST_with_metadata, T2:QA_fanout_exhibit places with steps; (6) T1:FastP_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, AR1_MLST_Serotype_Virulence are `unread` (no plot targets them: grep target_dataset); (7) T2:QA_aggregated_no_key and T3:qa_aggregated_no_key are Gone (T2 groups by country and year_label, sample_id vanishes: the wrangling file says so) while T1:QA_aggregated_no_key is a tick; (8) Summary, Summary_quality, Quality_metrics, Detailed_summary, QA_ST_with_NA are not lines (no join links them; listed as `outside`); (9) 14 T3 lines each; (10) T1:QA_L50_integer join_linked: reads Quast + metadata. No wrong line found.

## NOT covered
The 40 other mutants of the builder; the other four shipped recipes (the builder's JSON only read); the plan composer (`m.py`, outside the diff); pytest on the full repo (app/ tests, browser tests); the sentences (no words are built); whether the engine plan used in the demo equals a real run (not rerun); R1 semantics; the rest of the 90 DESIGN cases read one by one; Q-A17 and the other open questions of DESIGN section 5.
