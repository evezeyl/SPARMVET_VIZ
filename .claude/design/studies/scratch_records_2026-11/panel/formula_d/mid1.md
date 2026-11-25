
## A2. Today's check and evaluation on the real data (RAN: `a2_run_real.py`, `a2_output.txt`, `a2_summary.json`)

Method: the 11 recipes (7 shipped pipelines, 4 equality recipes) were built with the app's own path (`DataOrchestrator.materialize_tier1/2`, `VizFactory().render`, as `assets/scripts/golden_baseline.py` does). A hook on `transformer.actions.polars_calls.evaluate_formula` caught every formula the engine evaluated. For each: today's check, today's evaluation, D's build, the same plan (`Expr.meta.eq` and the text of the plan), and the column on the table the step receives (rows, type, missing values, hash of the values).

Results:
- 113 formula evaluations, 17 distinct texts. Check: accepted 113. Today's evaluation: 0 errors. D: 0 errors.
- Same plan (`meta.eq`): 113 of 113. Same column (type, missing values, values): 113 of 113.
- 102 table records (tier 1, tier 2, the table of each plot) built with today's evaluation: equal to `app/tests/golden/baseline.json` for all 7 shipped pipelines. Built with D in place of `evaluate_formula`: identical to today's for all 11 recipes.
- One recipe, `2_test_data_ST22_dummy_fractional_year`, refuses the cast on purpose (the data has a decimal Year); tier 2 and one plot are absent, the same for both ways.
- Not run on data: the 3 orphan lines and the template line. For them only the plan was compared (equal).

A finding that is not about formulas (RAN: `a2b_order_probe.py`): in my first version I took the column with `lf.select(expr)`. For the formula `resistance_points` the values came out in a different order at each collect (10 collects: 10 different hashes, 1 hash after sorting; the full table: 1 hash in 10). The optimized plan shows `UNIQUE[maintain_order: false]` where the step wrote `maintain_order: true` (`a2b_plan_optimized.txt`). It happens only when the plan is cut to one column. The app's own path (the whole table) is stable and equal to the baseline. I changed my probe to `with_columns` and the difference went away. I did not investigate Polars further. See "Found outside the task".

