# Control run, dev at efd1cd5f, 2026-11-18 (in progress)
Tree clean at start. Loadavg at start of step 1: 3.41.

## Flags (read from config/app_features/*.yaml)
| file | interactivity | t3_sandbox (audit) | sessions | comparison | export | blueprint | test_lab | gallery | testing_mode | ghost_save | selector visible |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qa | T | T | T | T | T | T | T | T | T | **F** | T |
| developer | T | T | T | T | T | T | T | T | T | T | T |
| pipeline-exploration-advanced | T | T | T | T | T | F | F | F | T | T | T |
| pipeline-exploration-simple | T | F | F | T | T | F | F | F | F | F | F |
| pipeline-static | F | F | F | F | T | F | F | F | F | F | F |
| standalone | T | T | T | T | T | T | F | T | T | T | T |
| demo-vetinst | F | F | F | F | F | F | F | F | F | F | F |
| web-demo | T | F | F | F | F | F | F | F | F | F | F |

## Step 1 headless: 2 failed, 10549 passed, 5 skipped, 31 xfailed, 975 s (16m15s)
Both failures caused by tonight's merge 4cbe9960 (D-0269, plot warnings in the export); stable 3/3 reruns.

## Step 2 browser (qa, one file at a time, 20 min limit each): 26 files, all finished, none hung
Passed: empty_recipe_startup 1; export_download 9 (331 s); export_inputs_survive 3; export_ready_busy_wait 2; export_ready_button 18 (358 s); filters_cleared 13; join_preview 2; blueprint_known_defects 1 xfailed; export_fields_per_session 3; export_race 13; filter_pickers 43; filter_types 3; filter_value_list 2; gallery_left_out 3; gate_gap 3; na_tick 1; plot_errors 4; plot_warnings 1; seed_places 4 (377 s); session_keep_both 2; session_restore 1; smoke_blueprint 17; smoke 37 passed 3 skipped; step_order 6; every_app_features_starts (no qa variable) 9 (102 s).
Failed once: test_shiny_apply_blocked (1 failed in 44 s; select_option("gt") on #fb_op timed out at 30 s "did not find some options"). Alone 3 times: passed, passed, passed (22/21/21 s). Flaky; the test last changed 2026-11-17 (b459c891), not by tonight's merges.
## Steps 3-6
3 import: OK. 4 golden baseline: result-identical (6 s). 5 gallery previews (no --apply): identical 34, differs 0, new 0, error 0 (24 s). 6 audits: see report.
