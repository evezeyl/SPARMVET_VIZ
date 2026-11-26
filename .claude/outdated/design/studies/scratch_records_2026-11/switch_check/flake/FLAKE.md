# Flake check, task/switch-fixes 1a0d1532
10 full-file runs: 4 passed (3,4,7,8), 6 failed (1,2,5,6,9,10). Only test_table_of_the_other_recipe_is_not_filtered ever failed.
test_audited_step_of_recipe_a_is_back_after_returning passed 10/10; "FORM RESET" printed 0 times in 10 runs.
Failures 2,5,6,9,10: line 137 `assert 33 == 70`. Failure 1: line 54 `#filter_remove_0` not visible after Add.
Cause (proved with a probe, tmpAI/switch_check/flake/probe/): the first read of A's table (unfiltered_a) sometimes returns the table of A's FIRST sub-tab
(ResFinder, columns sample_id/gene/predicted_phenotype, 70 rows) before the preview has switched to MLST Bar (MLST_with_metadata T2, 33 rows).
70 is then taken as "unfiltered A"; the later correct read is 33. Logs: run_N.log, loads.txt, alone.txt, probe/.
