controls: one failure only. test_export_download.py::test_the_export_records_the_seed_the_recipe_writes... failed once in the full browser run (StopIteration at line 327, the known timing race). Run alone twice, it passed both times (3 runs: fail, pass, pass). Everything else passed. Branch dev, commit 8f951761 (checked). I changed no tracked file; `git status --short` is empty after all runs. No commit, no push, no stash.

PART 1, cache removal (D-0206)
- Removed 156 paths, 110,156,232 bytes (about 105 MB). All untracked: nothing under tmp/ or tmpAI/ is tracked by git.
- Paths removed:
  - the contents of `anchors/` and `_sessions/` under `tmp/UI_TEST/user/`, `tmp/pipeline_test/user/`, `tmp/DEMO/user/`, `tmp/RETEST/user/` (every recipe, not only the demo);
  - the contents of `tmpAI/audit_manifest_integrity/`, `tmpAI/audit_recheck/`, `tmpAI/audit_data_analysis_recipe_integrity/`.
- No `parquet_data/` folder exists. All deployment locations are inside the repository folder, so none were listed as outside.
- t3 files: none under `tmp/` or the three audit folders. 10 `t3_*.json` exist only under `tmpAI/panel/verification/scratch4b/` (panel evidence, not touched).
- Not sure, kept (full list in `tmpAI/controls_8f951761/caches_removed.md`):
  - `tmp/UI_TEST/user/_blueprint_drafts/76964f0f81b1_1_test_data_ST22_dummy.json` (a draft of the user, not a cache);
  - other `tmp/` test and audit evidence (sink_test.parquet, phase3_test_hash.parquet, app_logic_audit, ingestion_integrity, transformer, test_exports, audit_exports, Blueprint_Audit, gallery_preview_review);
  - `tmpAI/panel/**`;
  - other `tmpAI/audit_*` folders (audit_full, audit_lib_tests, audits, gallery_audit), outside the allowed list;
  - the "not sure" part B of `caches_to_remove.md` (panel dumps, `golden_*.json` copies).
- `.claude/worktrees/*` untouched.
- Left-over `shiny run` processes from old worktrees (the start time was not collected):
  - pid 104136, worktree `recipe-small`, port 59197
  - pid 248767, worktree `self-join-warn`, port 59399
  - pid 1171940, worktree `verif-fix-2`, port 9819
  They are still running; I did not stop them.

PART 2, controls (logs in `tmpAI/controls_8f951761/`)

| Control | Result | Counts | Log |
|---|---|---|---|
| 1 App import | OK | rc 0 | c1_import.log |
| 2 Headless suite | pass | 9834 passed, 5 skipped, 15 xfailed, 28m38s | c2_headless.log |
| 3 Golden baseline | pass | `result-identical`, rc 0 | c3_golden.log |
| 4 Gallery previews (default compare mode, output to `gallery_out/`, `--apply` not used) | pass | 34 identical, 0 size only, 0 differs, 0 new, 0 error | c4_gallery.log |
| 5 Browser gate (qa) | 1 failed | 71 passed, 3 skipped, 1 failed, 10m00s | c5_browser.log, c5_rerun1.log, c5_rerun2.log |
| 6a audit_cross_lib | PASS | no violations | c6a_cross_lib.log |
| 6b check_doc_links | rc 1 | 7 problems, the same 7 as known, no new one | c6b_doc_links.log |
| 6c audit_docs_sync | PASS | 0 violations | c6c_docs_sync.log |
| 6d audit_old_words --check | rc 1 | the same retired words and the same list of folders as `tmpAI/controls_79cdeab5/g4.log` | c6d_old_words.log |

- Control 5: the failure is `test_the_export_records_the_seed_the_recipe_writes_and_writes_it_into_the_reproducibility_recipe`, `app/tests/test_export_download.py:327`, `StopIteration`. The line is `recipe_name = next(n for n in z.namelist() if "/data_analysis_recipes_reproducibility/" in n and n.endswith(".yaml") and not n.endswith("effective_run.yaml"))`. In the full run the zip had no such file.
- Control 5 skips: the 3 skips come from the test files' own skipif conditions on app features ("Blueprint requires developer or qa", "Gallery only visible for developer/qa", and similar). I did not run `-rs`, so I cannot say which three.
- The 10 browser test files that need no `SPARMVET_APP_FEATURES` setting (test_shiny_filter_pickers, test_shiny_na_tick, test_shiny_plot_errors and others) ran inside control 2. They set their own env, so they were not skipped for lack of qa features.
- Control 6d: I did not compare with `36d1bd23` (the earlier log there is `79cdeab5`). Against `79cdeab5` the words are the same (persona, manifest, recipe, profile, project, connector). Only the "recipe" counts grew: paths 92 to 93, content 7665 to 7784. That growth matches the new files from this change, for example `left_join_lesson`.
- Control 7: after the runs the app rebuilt its caches (`tmp/UI_TEST/user/anchors` holds 24 files, `tmp/DEMO/user/_sessions` has a new session). `git status --short` shows no change to any tracked file.

PART 3, numbers through the real path (script `part3.py`, results `part3.json`; fresh anchors)

| Item | Number now | Verdict |
|---|---|---|
| a. demo_abromics joined table | 27 rows, 27 distinct samples, max 1 row per sample | solved by the id fix |
| a. "Non Determined" | 15 rows | consistent with the recipe text ("no MLST result or an unknown one": 12 samples with no MLST row, the other 3 an unknown result); not odd |
| a. missing year | 2 rows (two metadata lines with an empty Year) | not odd (it is in the data) |
| a. rows drawn by `demo_st_by_source` | 27 | solved by the id fix (equals the table) |
| b. join cautions (`DataAssembler.cautions`) | none, for every shipped recipe | no caution; the caution only fires for self-joins |
| c. joins that lose samples | none: samples before = samples after in every join of every recipe | no sample is lost |
| c. joins where rows grow (left joins, expected fan-out) | see below | flagged, not decided |
| d. recipe 2 multiresistant count | the plot counts rows (the recipe says so): 46 rows with `Multiresistant=Yes` of 70; as samples: 16 of 38 | counts rows, not samples |
| e. ST22 VirulenceFinder file | 1315 raw rows, 583 rows in exact-duplicate groups, 331 extra copies; the recipe removes them (`polars_unique`) before the join | do not reach the joined tables |

- Item c, row growth by join (rows before to after, samples stay the same):
  - recipe 1_Abromics_general_pipeline, `AR1_MLST_Serotype_Virulence`: the left join with VirulenceFinder takes 42 rows to 984, then the inner join with the APEC/STEC list takes 984 to 342.
  - recipe 1_test_data_ST22_dummy:
    - `ST22_Anchor`: the left join with ResFinder takes 42 to 74; with VirulenceFinder 74 to 1731; the inner join with the APEC/STEC list 1731 to 617.
    - `AR1_MLST_Serotype_Virulence`: the same VirulenceFinder fan-out as in recipe 1 (42 to 984), then 342.
    - `QA_AMR_per_sample` and `QA_fanout_exhibit`: the ResFinder join takes 42 to 74; `QA_fanout_exhibit` goes on to 1731 (by design, it is the exhibit).
  - recipe figshare_integration, `figshare_triple_join`: 980 to 18,437 to 203,146 rows.
  - recipes 2_test_data_ST22_dummy, demo_abromics, stress_test_master and the other joins: no growth.
- Item e: exact-duplicate rows reach two joined tables from another source. `ST22_Anchor` has 14 identical rows (7 gene hits listed twice for one sample) and `QA_fanout_exhibit` has 256. The VirulenceFinder file is not their cause. Plot `virulence_bar` draws all 617 rows of `ST22_Anchor`, so it counts those 14 rows. Plot `qa_fanout_rows_per_sample` reads `QA_fanout_exhibit`, whose T2 is already 42 rows, so the fan-out is gone there. Two more tables hold exact duplicates: `QA_AMR_per_sample` 2 and `Plasmid_Profile_Joint` 4.
- Item d: the multiresistant flag is computed per sample (`n_unique over sample_id` greater than 1), but the plots count hits (rows), which the plot description states.
- I do not know which results Eve found odd earlier. Verdicts are given against the id fix only. Item a is the only one with a clear "solved"; the rest of the table is "still the same by design".

Needs a decision from Eve (D-0165: no decision exists)
1. The fan-out of left joins (42 to 984 or 1731 rows, and figshare 980 to 203,146) raises no caution and no warning. Today a caution exists only for self-joins. Options: (a) leave it, since the recipe descriptions state it; (b) add a general "rows grew after a join" caution, which would be a new rule and needs her decision.
2. Exact-duplicate rows in `ST22_Anchor` (14) come from ResFinder gene hits listed twice. Options: (a) remove them in the ResFinder wrangling (a change of the data recipe); (b) keep them and say so in the plot description; (c) leave as is.

Not run: nothing from the brief was skipped. I did not run `-rs` to name the 3 skipped browser tests, and I did not run the old-words check on `36d1bd23` (not allowed).

Files: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/controls_8f951761/` (caches_removed.md, paths.txt, sizes.txt, c1 to c7 logs, c5_rerun1.log, c5_rerun2.log, part3.py, part3.json, progress.md, gallery_out/).
