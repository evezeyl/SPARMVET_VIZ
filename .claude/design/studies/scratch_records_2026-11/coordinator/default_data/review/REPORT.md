# Review: task/default-data-test (bab4cc33), D-0425 "The paths in the shipped recipes are examples only"

Verdict: FIX FIRST (one small point; the rest is sound).

## Checks
1. Diff: only app/tests/test_recipe_default_data.py (+247). `git merge-tree dev branch` gives a tree id with no conflict: merges cleanly.
2. Content: 18 tests, 0 skipped today. 7 recipes discovered (find_data_analysis_recipes, not a hard-coded list). For each table with source.path (test file :84-96): located file == declared file, file exists, inside the repo, the session-key file list and Data Import's file_place name the same file. Content (not only paths) is asserted only for the demo table Summary_quality (:108-123: rows and sample ids equal the declared file, via read_source and prepare_ingredient). The other recipes are checked on paths only; Summary is only checked by path.
3. chdir: done with a module-scoped pytest.MonkeyPatch (:37-52), undone in teardown (mp.undo). Not per test, but it is restored at module end; fine in one process and with xdist (separate processes). Data Import replacement case writes only into tmp_path (:183-191). After the run `git status --short` is empty and the sha256 of assets/test_data is identical before and after.
4. Mutations (plugins outside the tree, nothing edited):
   - M1: locate_dataset_file returns raw_data/metadata.tsv instead of the declared file: only test_the_demo_table_really_reads_the_declared_file FAILS. The 7 per-recipe path tests were SKIPPED (the load gate rejected every recipe because of the mutation), not failed: 1 failed, 10 passed, 7 skipped. So skip-with-reason hid the failure; only the content test caught it.
   - M2: read_source for Summary_quality reads another file: only the same content test fails; 17 pass.
   Cases that do NOT detect M1: all 7 per-recipe cases (skipped), found, local-deployment, two-tables, and the 6 tmp_path cases (they build their own orchestrator and do not use the shipped recipes). Only 1 of 18 detects either mutation.
5. Runs: new file alone 18 passed (11 s). With the four other files and -n 2: 114 passed, 29.9 s; same in serial order with the new file last: 114 passed. No order effect or chdir leak seen. Imports come from the worktree (checked app, utils, transformer paths).
6. Style: no non-ASCII character and no sys.path in the file; test names say what is proved, except test_the_demo_recipe_in_the_shipped_folder_has_every_file_it_names, which loops over ALL shipped recipes (name is wrong).

## FIX FIRST
1. The per-recipe test turns a gate rejection into a skip (:72-74). A regression that makes recipes rejected hides the very failure D-0425 asks to catch (shown by M1). Replace the skip with a failure for a recipe the local deployment should accept (or assert that the number of skipped recipes is 0 and fail otherwise).
Smaller, may follow: (a) add a content assertion (row count equal to the declared file) for every shipped recipe, not only the demo; (b) rename the last test.

## Not verified
- Only part 1 of D-0425 is tested (local deployment reads its declared test data). The other half (a deployment without that place says in plain words that the default data is not available; D-0426 user selects data) has no test, and the branch docstring says so.
- Whether the module-scoped Bootloader is a process singleton that another test module imported earlier with another environment (not tried in a mixed order beyond the 4 files).
- Load average at runs was 8.8 to 10.9; two runs started at 10.26 and 10.87 (just over the limit of 10; I did not wait the second time). No full suite, no browser tests.
