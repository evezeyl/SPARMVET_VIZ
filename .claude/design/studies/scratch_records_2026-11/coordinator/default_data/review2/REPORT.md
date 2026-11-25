# Second review: task/default-data-test (a5ed409d on bab4cc33), D-0425 "The paths in the shipped recipes are examples only"

Verdict: FIX FIRST (one point). The skip is gone and works; the content test is weaker than its docstring says.

## 1. Skip gone, discovered = checked
- `test_each_table_reads_the_file_its_source_path_names` now calls pytest.fail with the gate's first 3 problems (diff, line ~73). Proven by my mutation (point 3): the recipe was rejected and that test FAILED with the gate's reason, where before it was skipped.
- New `test_every_discovered_recipe_is_available_to_the_checks` asserts checked == discovered (7 recipes). It failed in the mutation too ("left out: ['1_test_data_ST22_dummy']").
- Stale comment: lines 25-26 still say a rejected recipe "is skipped below with the gate's reason". Fix the words (small).

## 2. Content test: multiset of the first text column
The reason is legitimate (fields declare texts that mean missing, e.g. dash or empty quotes; those rows read as missing). Only missing values are dropped (`if v`), so that part is no wider than needed. But the test compares only row count and ONE column, and it checks "values read are contained in the declared file's values" (a subset test, not equality).
Pairs of declared files of one recipe with the same row count and the same first-text-column (all key `sample_id`, 42 rows; I computed that each table's read passes against the other file's column):
- Recipe 1_test_data_ST22_dummy: Summary, Summary_quality (same file), Quality_metrics, FastP, Quast, Bracken, MLST, metadata_schema: 7 distinct files, all 42 rows, all keyed by sample_id: every one of the 21 pairs is indistinguishable by this test.
- Recipe 1_Abromics_general_pipeline: MLST and metadata_schema (42 rows each): 1 pair.
- No pair in 2_test_data_ST22_dummy (70/163/42), 3_test_no_joins, demo_abromics (15/30), figshare_integration (980/18437/10839), stress_test_master.
Said plainly: the content test cannot tell those files apart. In practice a swap between them is still caught, but by the load gate (each file lacks the columns the other declares, so the read fails), not by the content test. A swap to a file with the same declared columns and the same ids (an older version of the same table) would pass.
FIX FIRST: compare all declared columns, after the declared null handling and strip, as a whole (equality of the frame read by the app with an independent read of the declared file restricted to the declared columns, or of a hash of those frames, sorted by all columns). Then equality, not subset, and the "weak" multiset goes away. Smallest version if the null handling is hard to repeat: compare a hash of 2 to 3 declared columns per table plus the height.

## 3. Own mutation
Plugin (scratch, not in the tree): locate_dataset_file returns the FastP file for table Quality_metrics of the demo recipe only. Result: 3 failed, 23 passed: per-recipe path test [1_test_data_ST22_dummy], content test [1_test_data_ST22_dummy], and recipes-checked-equal-discovered. Caught, via the gate's rejection. Worktree `git status` clean after.

## 4. Runs
Load average before runs 8.8 (below 10). New file alone: 26 passed (10.2 s). With test_dataset_lookup_one, test_data_import_check, test_data_analysis_recipe_data_check, test_shipped_deployments, `-n 2`: 122 passed (21 s). Imports came from the worktree (app from .../worktrees/default-data-test). sha256 of assets/test_data (main tree) identical before and after (e583ac7e...); worktree status clean. `git merge-tree --write-tree dev task/default-data-test`: tree 281bf1cb..., no conflict.

## Not verified
- Browser tests and the full suite.
- That the proposed full-column comparison passes on every shipped recipe (not tried).
- Part 2 of D-0425 / D-0426 (deployment without the place) is still not tested (as in review 1).
- Pair detection used first-text-column values and heights only; other-column equality between files was not checked (files differ in headers, see the gate).
