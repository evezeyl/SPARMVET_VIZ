# DATA-IDS-FIX-1: report

Worktree `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/worktrees/data-ids`, branch `task/data-ids`. `git status --short` is clean. 4 commits on `5d3acf1d`, no push:
- `2967c805` generator (part 2)
- `7bf346d6` data (part 3)
- `83699544` numbers, descriptions, golden entries (part 4)
- `44daa5ec` the new consistency test (part 5)

Files that I wrote in the worktree and that git ignores (`tmpAI/`):
- `tmpAI/data_ids_before.md`
- `tmpAI/data_ids_after.md`
- `tmpAI/caches_to_remove.md`
- `tmpAI/progress.md`
- scratch under `tmpAI/scan/` (scan, numbers before and after, the one-off id correction script)

## Answer first
**After this change, can a dataset of a shipped recipe hold a sample id that the recipe's other datasets do not know?** Not by accident, with one declared exception.
- The exception is `complex_template`, a template (not run in HOME): its `genomics` data holds ACC0029 and ACC0030, which are not in its metadata, on purpose (see open choice 5).
- What tells us: `app/tests/test_recipe_data_one_set_of_ids.py`. It reads the raw files of every shipped recipe with two or more datasets that have a sample id. It fails and names the file and the ids when:
  - a table holds an id outside the set of the metadata;
  - the metadata table repeats an id;
  - a table meant to have one row per sample (and scheme) repeats it.
- I ran the same test on the old demo MLST file. It named the 2 foreign samples (SYN_38282317, SYN_67199832) and the 8 repeated (sample, scheme) pairs.
- **The app itself still says nothing at run time.** No check in the app warns on such an id (that is M196 point 3, not built).
- Limit: a NEW recipe with two or more id tables and no `metadata_schema` fails the test with "name the right table in COMMON_SET_TABLE", so it cannot slip through. A new table that is not in `UNIQUE_BY` is checked for foreign ids only.

## Part 1, facts before (`tmpAI/data_ids_before.md`, RAN with a raw-TSV script)
| Recipe | Result |
|---|---|
| demo_abromics | NOT one set: MLST has 2 ids outside the metadata (2 rows), 8 ids repeat (13 extra rows). The metadata has 27 ids and 3 lines without id; 12 of its ids have no MLST row. |
| 1_test_data_ST22_dummy | one set: union 42 = metadata 42. ResFinder lacks 4 ids (a long table, samples without a hit). |
| 2_test_data_ST22_dummy | one set. ResFinder lacks 4 ids, PlasmidFinder lacks 1. |
| 1_Abromics_general_pipeline | one set: all 3 tables hold the same 42 ids. |
| figshare_integration | one set: the same 980 ids in 3 tables. |
| complex_template | NOT one set: genomics has ACC0029 and ACC0030, which are not in the metadata; the metadata has ACC9999, which is not in genomics. Deliberate (see open choice 5). |
| 3_test_no_joins, stress_test_master, retest_*, templates simple/e_coli/audit | one dataset, or the data files do not exist. Not part of this task. |

The earlier check file said `complex_template` had "no sample id". That was wrong: its key is `Accession` in genomics and `ID` in the metadata, and they do not match.

The ST22 data and figshare satisfy one common set, so I did not touch them.

## Part 2, generator (`assets/scripts/generate_demo_data.py`)
- I used plain `random.Random(seed)` and text reading, not `AquaSynthesizer`. That tool builds one table at a time from a column config and keeps no shared id set, so it cannot guarantee a common set or one row per sample and scheme.
- What it writes:
  - one set of ids `SYN_<8 digits>`;
  - metadata: one row per sample;
  - MLST: one row per sample and scheme, a random pick of the set;
  - ResFinder: 1 to 4 rows per sample;
  - messy values at 5 percent in the other columns, never in the id or scheme column.
- It checks its own output and stops on a failure.
- Command: `./.venv/bin/python assets/scripts/generate_demo_data.py --seed 20261117 --out-dir tmp/demo_data_generated`. Default seed 20261117, default output `tmp/demo_data_generated` (rule: suggestive tools never write to default data roots). Existing files are not replaced without `--overwrite`.
- Two runs give identical md5 on all 3 files (also a pytest). `--help` runs.
- Docs updated: `assets/scripts/README.md` and `docs/appendix/running_helper_scripts.qmd` still described the old script.
- 16 tests in `app/tests/test_demo_data_generator.py`. I broke it once (MLST drawn with replacement, check disabled) and a test failed.
- Choice (a), the 3 metadata lines without a sample id: kept, as the review session's default, and the generator can add them (`--metadata-lines-without-id`, default 3, ids empty, `-`, two quote marks).
- Choice (b), the other messy values: kept as they are in the existing files; the generator adds the same kinds (empty, `-`, unknown, N/A) at 5 percent.

## Part 3, data: option chosen and why
**Pure id correction inside the set is impossible.** 15 MLST rows need a new place (13 extras and 2 foreign), but only 12 metadata ids have no MLST row. Uniqueness per (sample, scheme) therefore cannot be met by changing ids alone.

| Option | Demo table (rows / samples / samples without MLST) | Values changed |
|---|---|---|
| **X, chosen**: delete the 15 rows (first row of each sample stays) | 27 / 27 / 12 (the 12 and 27 Eve referred to are unchanged) | 0 changed, 15 rows removed |
| Y: give the 2 foreign rows 2 of the free ids, delete the 13 extras | 27 / 27 / 10 | 2 ids changed, 13 rows removed |
| Z: reassign 12 rows to the 12 free ids | no sample without MLST, so "Non Determined" is no longer exercised | |
| Regenerate (generator defaults, seed 20261117) | 27 / 27 / 12 | all values |

I chose X because the user-visible numbers stay the same as in her words and it changes no value.

Other changes to the data:
- **MLST file:** 30 -> 15 rows, 17 -> 15 ids, 8 repeating ids -> 0, 2 ids outside the set -> 0.
- **Demo ResFinder file** (read by no recipe): 4 ids outside the set (2 dashes, SYN_98093093, SYN_67199832) now hold ids of the set, by a seeded pick (seed 20261117). 22 -> 21 distinct ids.
- **Metadata file:** unchanged.
- **Open point on X:** which row of a repeated sample stays is arbitrary (the data cannot tell). The committed files are the existing files corrected, not the generator's output.

## Part 4, numbers
- **Recipe text** (`demo_abromics.yaml`): says "27 rows for 27 samples". The sentences about several MLST results, the repeated sample and the 2 foreign MLST rows are gone. The decided behaviour is unchanged (left join, "Non Determined", the step that removes lines without a sample id).
- **Golden baseline**, entries that moved (all follow D-0205, and the commit message says so):
  - `demo_abromics t1 demo_join`
  - `demo_abromics t2 demo_join`
  - `demo_abromics plots demo_st_by_source`
  - each: rows 40 -> 27, sha256 `861adfae...` -> `c3070a3d...`.
  - No other recipe moved. `--check` reports result-identical.
- **Tests changed:**
  - `test_demo_join_keeps_every_sample.py`: the test of a sample that keeps 6 rows (it locked the defect in) is replaced by one row per sample and scheme; the numbers are now (27, 12, 27).
  - `test_shiny_na_tick.py`: 27 rows, 2 without year, 25 for 2024. The browser run passed (1 passed).
  - `categorical_counts_before.json` and `categorical_content_before.json`: the demo entries are re-recorded (open choice 3).
- **Mutation check:** I put the old MLST file back once and 5 tests failed.

## Part 5
`app/tests/test_recipe_data_one_set_of_ids.py` has 14 tests. Break checks on a copy of the demo data (foreign id, repeated sample and scheme, repeated metadata id) each fail with the file and the ids named.

## Part 6
`tmpAI/caches_to_remove.md`, nothing deleted.
- **Safe, rebuilt by the app or the audit scripts:**
  - `tmp/UI_TEST/user/anchors/demo_join.parquet`
  - `tmp/pipeline_test/user/anchors/demo_join.parquet`
  - the two demo sessions `076137b0a0eb:97e260818d24` (UI_TEST) and `b98f603ac5f7:97e260818d24` (pipeline_test), `assembly.json` only
  - the demo files of the audit folders `tmpAI/audit_manifest_integrity/`, `tmpAI/audit_recheck/` and `tmpAI/audit_data_analysis_recipe_integrity/`.
- **Not sure:**
  - agent evidence dumps and pictures under `tmpAI/panel/` (round5, round7, verification);
  - the golden copies `tmpAI/golden_*.json`;
  - scratch copies of the recipe;
  - and, if D-0206's "all cached data" means all, the other 45 sessions and anchors of ST22, retest and figshare. They were not made from changed data, and no `t3_*.json` exists anywhere under `tmp/`.
- Never touched: source data, recipes, tests, tracked files. No gallery bundle reads the demo data.
- Orphan processes from other worktrees (not mine, not stopped): `shiny run` from `recipe-small`, `self-join-warn` and `verif-fix-2`, running for hours.

## Part 7: odd items re-run on the new data
| Item | Before | After | Verdict |
|---|---|---|---|
| demo join, the old inner-join view | 28 rows, 15 samples | 15 rows, 15 samples | solved: the 13-row gap is gone |
| demo join, current left join | 40 rows, 27 samples | 27 rows, 27 samples | solved by the id fix |
| the sample with 6 rows (SYN_74255382) | 6 rows, 6 sequence types under one scheme | 1 row (ST 1674) | solved |
| plot that counts rows | 40 | 27; bars now count samples | solved |
| "Non Determined" rows | 17 | 15 (12 samples without MLST + 3 unknown results) | changed because the repeats are gone |
| the 2 MLST-only samples | 2 rows of 2 samples | 0 | solved |
| rows with a missing year | 7 | 2 | solved: 2 genuine empty Year values (SYN_86102363, SYN_74255382); the other 5 were repeats of the second one |
| build output | no warning | no warning (no caution) | still nothing tells the user of a repeated key |
| the join warnings with row numbers, the attrition counts, the multi-resistance count of M199 | | | not re-run, outside the brief |

The data-scientist plausibility review of M199 point 3 was not done. A scientist's view is still open, in particular on the choice of which MLST row stays (open choice 1).

## Runs
| Run | Result |
|---|---|
| New tests: generator 16, one-set 14 | pass |
| Demo join, categorical migration, golden baseline, shipped recipes pass the checker | 118 passed together with the two new files |
| Headless suite (`libs` + `app/tests`, browser files left out) | 9816 passed, 5 skipped, 15 xfailed, 0 failed (30 min) |
| `test_shiny_na_tick.py` (browser, qa) | 1 passed |
| Golden check | result-identical |
| Gallery previews | 34 identical, 0 differs |

I did not run the four browser files left out of the baseline command (`test_shiny_smoke*`, `test_export_download`, `test_every_app_features_starts`); none names the demo recipe.

## Not decided, for Eve (each with options)
1. **Which MLST rows go** (open choice A above): X (chosen, 27 samples and 12 without MLST kept), Y (10 without MLST), or regenerate. Also whether the committed files should equal the generator's output.
2. **Metadata lines without a sample id:** kept (3), the recipe still removes them. Option: none.
3. **The two "before" JSON fixtures:** I re-recorded only the demo entries from the current code, as on 2026-11-16 (`d2ebef31`), and the note in the file says so. The demo entries no longer document the table before the migration. Options: (a) as done; (b) remove the demo entries, so the test no longer covers the demo; (c) keep the old entries against a frozen copy of the old demo data.
4. **Messy values** (empty year, `-`, `unknown`, `N/A`): kept, nothing removed. The 2 missing years are such values.
5. **complex_template:** its data holds 2 ids in genomics (ACC0029, ACC0030) and 1 in the metadata (ACC9999) on purpose, to teach the left join (`make_complex_template_data.py`, `test_complex_template_runs.py`). D-0205 says one set of ids for all datasets. I did not change the data and I declared the 2 genomics ids as an exception, with the reason, in the new test. Options: keep the exception; or make the data one set (the test of the left join then needs another example).
6. **A warning in the app for a repeated key or a foreign id** (M196 point 3): no decision exists, nothing built.
7. **Not mine, found:**
   - the ST22 VirulenceFinder file has 583 exact duplicate rows (not judged);
   - the templates simple/e_coli/audit point to missing data files.

## Decisions table
| Decision | How the change complies | Where | Test |
|---|---|---|---|
| D-0205 "The same set of ids is used across all the datasets of the recipes" | demo MLST and ResFinder hold only ids of the metadata; the generator draws every table from one set; ST22 and figshare checked as already consistent | `assets/test_data/demo_high_integrity/*`, `assets/scripts/generate_demo_data.py:109` (`generate`) and `:136` (`check_one_set`) | `test_recipe_data_one_set_of_ids.py`, `test_demo_data_generator.py` |
| D-0205 "random pick of ids on the same set ... An agent fixes the data ids" | generator picks by a written seed; data fixed by an agent | generator `--seed`; the 4 commits | same-seed test: byte for byte |
| D-0206 "All cached data will need to be removed; the tests that produced weird results will need to be re-run" | cache list written, not deleted (the coordinator removes it); odd results re-run, see Part 7 | `tmpAI/caches_to_remove.md` | part 7 table |
| D-0167 "Those 12 samples should not be gone. Raws without sample id must go. Must be a warning" | 12 samples without MLST stay (27 and 12 unchanged), 3 lines without id stay and the recipe step removes them, descriptions state the numbers | `demo_abromics.yaml`, steps untouched | `test_demo_join_keeps_every_sample.py` (13 pass) |
| D-0165 "Where no decision exists and one is needed, that must be reported to her." | choices 1 to 6 above | | |

Co-Authored-By trailers are on every commit.
