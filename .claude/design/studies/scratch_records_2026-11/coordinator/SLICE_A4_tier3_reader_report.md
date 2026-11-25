# Piece A4: the engine reads tier 3 at the plot entry (builder report, digest by the coordinator, 2026-11-19)

Branch `task/tier3-reader` (worktree `.claude/worktrees/tier3-reader`), base dev `711bb40f`, head `4eb9032a` (commits `bb637d6e`, `5f1a5e00`, `4eb9032a`).

## Built
- Reader: `DataOrchestrator.materialize_tier3(data_analysis_recipe_id, plot_id, anchors_dir, keys=None, on_inputs_changed=None) -> LazyFrame` (`app/modules/orchestrator.py:414`). Name PROVISIONAL. The plot's target table at tier 2 (tier 1 when tier 2 is empty) plus the plot's `tier3.steps`, same step runner, one step at a time with a schema check after each; a step that cannot be applied raises naming plot and step.
- LAZY: nothing written on disk (the design files do not decide stored or lazy). PROVISIONAL.
- Keys (`app/modules/cache_keys.py:257-274`): `T3 = key(T2) . s3-<32>`; empty tier 3 = the key of the table; `collection_tier2_key` now returns the T1 key when tier 2 is empty (ADR-101 point 2; before: ""). Keys object gains `tier2_keys`, `plot_keys`, `tier2_key_of(table)`, `plot_key_of(plot_id)`. Export record keeps "none (T2 equals T1)".
- Checker: the constant `TIER3_READ_BY_ENGINE` and the P05 refusal are REMOVED (not switched); P06 (`filters` on a plot entry) is refused always. No YAML in the repository has `filters` on a plot entry (grep).
- Readers changed: HOME `home_theater.py:321-359` (`_resolve_active_lf`, tier "T3" reads the reader; the plot render and Compare's left pane pass T3), the filter form's table identity (plot key in T3), export (`_base_frame` ~1092, plots ~1253, T3 data ~1418; `T3_data_<plot>.tsv` also for plots with recipe tier 3; provenance `plot_keys` only for such plots), `assets/scripts/recipe_pictures.py`, `assets/scripts/golden_baseline.py`, `app/modules/gallery_examples.py`, `engine_record.py`.
- Not changed: `view_badge.py` (knows tier 2 only), Blueprint, `recipe_graph.py` (does not read tier 3 steps for columns; still reads plot `filters`), the export key check (the plot key is a function of what it already compares), `libs/viz_factory/tests/debug_gallery.py` (stale).

## Tests and controls (RAN by the builder)
`app/tests/test_tier3_reader.py` 77 passed, 1 skipped; `test_home_reads_the_plots_table.py` 4; adapted tests. Breaks: reader returns before the steps (10 failed); s3 part left out (4); export reads T2 (3); HOME's T3 branch off (2).
Headless whole: 11534 passed, 6 skipped, 31 xfailed, 1 failed (a count test of build sites 3 -> 4, then fixed). Golden identical. Pictures 50 identical + the known row. Keys of every shipped recipe identical before/after except one data part where the DATA FILE differs between the two checkouts (`assets/test_data/STRESS/STRESS_data.tsv`: 531128 bytes in the main checkout, 521127 in the worktree) -> to look at.
No browser run. HOME's plot render with T3 is REASONED, not run.

## What a user sees for a plot WITH recipe tier-3 steps (no shipped recipe has any)
Result plot, My view plot, Compare's left pane, export plot: from the plot's T3 table. "Raw (T1)" and "Result (T2)" data views: unchanged, so the Result plot and the Result table differ. "My view" data: the T3 table plus audit nodes. The panel badge would say "T3=T2", untrue for such a plot.

## User-visible text changed
- README contents line of the bundle: "... plus that plot's filters and column drops" became "... plus that plot's tier3 steps of the recipe and its audited filters and column drops" (every export).
- Report link label: new "Data of the plot (T3)" for a plot with recipe tier-3 steps only.
- New key lines only for plots with tier-3 steps.

## Open questions reported
1. T3 table stored or lazy. 2. Names `materialize_tier3`, `s3`. 3. Result view vs Result plot for a plot with recipe tier 3 (as now / Result data shows T3 / a fourth data view) and the badge. 4. `T3_data_<plot>.tsv` for plots with recipe tier 3 only (written now). 5. P05 retired and the constant removed; the spec still describes them.

## For the audit recipe piece (A5)
`plot_key_of`, `tier2_key_of`; the place for the audit parts is `collection_tier2_key` and `plot_tier3_key`; `materialize_tier3` reads tier 3 from the recipe object given, so a copy with audit steps at the end of its lists works as is if the checker accepts it; a copy needs its own folder of stored tables (files are named by the table only); the map does not read tier-3 steps for columns.
