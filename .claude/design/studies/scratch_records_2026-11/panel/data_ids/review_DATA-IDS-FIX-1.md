REVIEW of task/data-ids (4 commits on 5d3acf1d). I ran the checks myself. I did not push, merge, switch branches or edit tracked files. My scratch is under the worktree's tmpAI/rev1/.

VERDICT: PASS, with 2 small fixes before merge and 3 choices for Eve. The data and the code do what D-0205 and D-0167 say. The fixes are stale documentation only. The choices are not decided, so I do not approve or reject them.

FIXES (small, not blocking the science)
F1. Stale statements about the generator remain:
  - README.md:181 says "Generate synthetic demo data via AquaSynthesizer". The script no longer uses it.
  - .claude/knowledge/dependency_index.md:391-395 still says the script "writes synthetic TSVs" into demo_high_integrity. That file is auto-generated; the fix is to re-run build_dep_graph.py. Now the script defaults to tmp/demo_data_generated.
  - libs/test_lab/src/test_lab/aqua_synthesizer.py:6 still lists the script as its consumer (verified by read, grep).
F2. The test name test_the_row_count_is_one_row_per_mlst_result_plus_one_per_sample_without_one in test_demo_join_keeps_every_sample.py is now misleading. The recipe is now one row per sample. Rename it.

CHOICES FOR EVE (D-0165: no decision exists, so I report them)
C1. Which MLST row stays (see B9).
C2. The committed demo files are the old files corrected by hand. They are NOT the generator's output (the generator with its default seed gives other bytes). So the script is a tool, not the source of the committed data. The script's docstring does say how to replace the shipped files, but nothing links the two. Decide: keep as is, or replace the shipped files with generator output (every value changes and the golden hashes move again).
C3. complex_template keeps 2 genomics ids (ACC0029, ACC0030) that are not in its metadata, as a declared exception. D-0205 says one set of ids for all datasets. This is not decided. Options: keep the exception, or make the data one set (the left-join teaching example then needs another way).

COMPLIANCE TABLE
| Decision | How the change complies | Where | Test | My check |
| D-0205 "The same set of ids is used across all the datasets of the recipes..." | demo MLST and ResFinder hold only metadata ids; the generator draws all tables from one set | assets/test_data/demo_high_integrity/*; assets/scripts/generate_demo_data.py generate() and check_one_set() | test_recipe_data_one_set_of_ids.py; test_demo_data_generator.py | verified (run): my own count of the old and new files shows 0 foreign ids now (B7). ST22 recipe data counted too (B11). One exception, complex_template, see C3. |
| D-0205 "An agent fixes the data ids." | data fixed by the builder, by seeded script and by hand | the 4 commits | same-seed byte test | verified (run): generator twice gives identical md5; another seed differs |
| D-0206 "All cached data will need to be removed; the tests that produced weird results will need to be re-run" | the cache list is written, nothing deleted (that is for the coordinator). Odd tests re-run in the report's part 7 | tmpAI/caches_to_remove.md | none (a list) | verified (run) for the list: see B12. Re-run results of part 7: verified by the golden check and the full suite, not by me re-running each item. |
| D-0167 "Those 12 samples should not be gone. Raws without sample id must go. Must be a warning" | 12 samples without MLST stay (27 rows, 27 samples); 3 no-id metadata lines stay in the file and the recipe step removes them; the recipe text states the numbers | demo_abromics.yaml (steps untouched, only descriptions) | test_demo_join_keeps_every_sample.py (13 pass) | verified (run, read). The replaced test asserts one row per sample and scheme and 27 rows, and the recipe text is checked against the data. That matches D-0205 and D-0167. |
| D-0050 "No silent error that is the rule." | the generator stops with exit 1 and names the problem; the test fails with file and ids named | generate_demo_data.py main() | test_demo_data_generator.py; the new test | verified (run). The app itself still says nothing at run time about a foreign or repeated id (builder admits it, choice 6 of its report, no decision exists, M196 point 3). That is a gap, not a violation of this task. |
| D-0165 report what is not decided | builder lists 6 open choices | report | | verified (read). I add C2 and the bad ResFinder content (B8). |

PART A
A1. Files. verified (run) git diff --stat 5d3acf1d..HEAD: 13 files. All are named in the report or follow from it: golden baseline, 2 categorical JSON fixtures, 4 test files, the two docs, the recipe, the MLST and ResFinder TSVs, the generator. Metadata file unchanged. Nothing foreign.
A2. Generator. verified (run):
  - argparse and --help work; description is the module docstring.
  - Output default tmp/demo_data_generated, never a data root. Refuses to replace existing files without --overwrite (exit 2).
  - Default seed 20261117 written in the code and printed.
  - Run twice into scratch folders: identical md5 for all 3 files. A different seed (5) gives different bytes.
  - Break check: in a scratch copy under tmpAI/rev1/ I changed the MLST draw from rng.sample to rng.choices (with repeat). It printed "The generated data is not consistent: mlst: sample and scheme repeated: [...]", exit code 1, and wrote no files.
  - Emoji/non-ASCII: grep found none. Comments explain why (the module docstring explains the AquaSynthesizer choice). OK.
  - Limit: when --overwrite is given, existing files are replaced without a backup. That is what the flag says.
A3. New test test_recipe_data_one_set_of_ids.py. 14 tests, pass. verified (read + run). Can it fail: it has its own tests on a copy of the demo data that add a foreign id, a repeated (sample, scheme) and a repeated metadata id, and each assertion names the file and the id. I did not mutate it a second time myself; I read the logic: foreign ids = ids(table) minus common set minus allowed, so any extra id fails. The exception is narrow: ALLOWED_OUTSIDE holds exactly {ACC0029, ACC0030} for (complex_template, genomics), and test_the_allowed_outside_ids_are_only_the_declared_ones shows a narrower allow list fails with ACC0030 named (reasoned: a third id would also fail, because it is a set subtraction by id, not a count). The test also guards that a recipe cannot silently drop out (EXPECTED_CHECKED) and that a missing set table is reported. Blind spots: it reads raw files by plain text only; it does not see ids that are changed by wrangling; a table not in UNIQUE_BY is checked for foreign ids only; the VirulenceFinder file of 2_test_data_ST22 is not in UNIQUE_BY (it is a long table, fine).
A4. Changed tests and fixtures. verified (read). Numbers moved 40 -> 27 and 7 -> 2 missing years (and the 33 -> 25 filter counts) with reasons in the diff and commit text. No assertion removed without a replacement: the old "sample keeps 6 rows" test (which locked the defect in) became "one row per sample and scheme, one row per sample"; the "2 MLST-only samples" test became "no MLST-only sample and the text does not talk of removed MLST rows". The recipe text assertions were changed to check that the old sentences are gone. Weak points: (a) the two categorical JSON fixtures (categorical_content_before.json, categorical_counts_before.json) are now recorded from current code, so they no longer document the pre-migration demo table. The builder says so in the note and lists it as its choice 3. (b) the browser test test_shiny_na_tick.py was edited but I did not run it (browser file excluded). The edits are consistent with the new counts by arithmetic.
A5. Golden baseline. verified (run) PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json prints "result-identical". The diff of baseline.json shows only three entries moved (demo_abromics t1 demo_join, t2 demo_join, plots demo_st_by_source): rows 40 -> 27, sha256 861adfae... -> c3070a3d.... Note: without PYTHONPATH=. the script fails with "No module named 'app'". That is the environment, not the branch.
A6. Tests run in the worktree. verified (run):
  - test_recipe_data_one_set_of_ids.py + test_demo_data_generator.py + test_demo_join_keeps_every_sample.py: 43 passed.
  - Headless suite (libs + app/tests, the 4 browser files ignored, -q): 9817 passed, 5 skipped, 15 xfailed, 2 warnings, 0 failed, in 29:45. The 2 warnings are a plotnine colorbar warning. (The builder said 9816; one more test, no difference of substance.)

PART B (data)
B7. Counts (my script tmpAI/rev1/scan.py, raw files, old = git show 5d3acf1d:, now = disk). verified (run):
  - Metadata: 30 lines, 27 distinct ids, 3 lines without id (empty, "-", ""), no repeated id. Unchanged.
  - MLST old: 30 rows, 17 distinct ids, 2 ids outside the set (SYN_38282317, SYN_67199832), 8 repeated (sample, scheme) pairs, 12 metadata samples without MLST. MLST now: 15 rows, 15 distinct ids, 0 outside, 0 repeated pairs, 12 samples without MLST.
  - ResFinder old: 30 rows, 22 distinct ids, outside the set: "-", SYN_67199832, SYN_98093093. Now: 30 rows, 21 distinct, 0 outside, 6 samples without a ResFinder row.
  - These equal the report (27 / 27 / 12; MLST 30 -> 15 rows).
B8. Plausibility, remaining oddities. verified (read the files):
  - Metadata: no species column; Year is 2024 for all but two samples that have no Year (SYN_86102363, SYN_74255382). Plausible.
  - MLST has one scheme only (ecoli_achtman_4), with messy values: SYN_92436648 has Scheme "N/A" with ST 57; SYN_78540144 has an empty Scheme and an empty ST; SYN_26040571 has an empty ST; SYN_38371839 has ST "unknown". All are deliberate messy values.
  - MLST: allele profiles do not determine the ST. ST 1674 appears for SYN_34324619 (adk20,fumC38,gyrB19...), SYN_74255382 (adk43,fumC11,gyrB87...) and SYN_32804061 (adk21,fumC38,gyrB10...) with 3 different profiles. In real MLST one profile gives one ST. Pre-existing scramble of the source rows. It contradicts itself inside the table.
  - ResFinder: gene and phenotype columns do not agree. Examples: SYN_10481154 aac(3)-VIa -> "ampicillin"; SYN_23672090 sul2 -> phenotype "" (quote marks) with Sulfamethoxazole; SYN_70655914 sul2 -> "trimethoprim"; SYN_99643781 sul2 -> trimethoprim; SYN_70655914 has blaTEM-1C twice with two different phenotypes; SYN_74255382 has a row with no gene; %Identity empty for SYN_32804061, SYN_87929678 and SYN_99643781 (sul2 row). Not caused by this task, but the file is called "analyses of the same samples" and it is not a real analysis. It is read by no recipe (B10), so no user sees it.
  - The id correspondence itself is fine. The values per row are random mixes of the ground-truth rows.
B9. The deleted MLST rows. Not decided. Facts (verified run, tmpAI/rev1/opts.py and old file read):
  What is removed: 13 rows of repeated samples (8 samples) and 2 rows of samples outside the metadata (SYN_67199832 ST 1674, SYN_38282317 ST 154). The kept row is simply the FIRST in file order. Nothing supports it better:
  - SYN_74255382 had 6 rows: ST 1674, 538, 135, 57, 2040, 2040. Kept: 1674. The six have different allele profiles, so no row is better supported than another by the data (the 2040 twice is not a duplicate: two different profiles).
  - SYN_38371839 had "unknown" and 57. The kept row is the "unknown" one, so a real ST is lost, and this sample counts as Non Determined. It is the only case where the kept row is uninformative while another row has an ST.
  - SYN_56337687 had 371, 88 and "-" (kept 371); SYN_34324619 had 1674 and "unknown" (kept 1674).
  - 15 non-determined rows now (12 without MLST + 3 unknown/empty: SYN_38371839, SYN_78540144, SYN_26040571). 10 distinct STs. ST 1674: 3 samples.
  Options and what each does to numbers the user sees (table = 27 rows in all, one per sample, unless said):
  - X (chosen, first row): Non Determined 15; ST 1674 = 3; ST 57 = 1; 2040 = 0.
  - X' (last row of each sample): Non Determined 16; 1674 = 0; 57 = 4; 2040 = 1; 8 distinct STs (computed). Shows that the picture of the sequence-type plot depends on an arbitrary pick.
  - X'' (first row with a determined ST, else first): Non Determined 14 (SYN_38371839 gets 57). Needs a written rule in the script.
  - Y (the 2 foreign rows get 2 of the 12 free ids; 13 extras deleted): 27 rows, only 10 samples without MLST instead of 12, which moves the "12" Eve quoted.
  - Z (reassign the 13 extras to free ids): 12 free ids, 13 extras (+2 foreign): not all fit; no sample left without MLST, so the "Non Determined" bar from missing MLST is not shown any more. The report says this too.
  - Regenerate (committed files = generator output): all values change.
  - Keep several rows per sample and change the recipe: contradicts D-0205's logic of one sequence type per sample and scheme; not recommended by data, but it is a choice.
B10. Demo ResFinder file. verified (run, grep): no recipe, test or doc reads the demo ResFinder file as data, except the new test test_the_shipped_demo_folder_is_one_consistent_set and the generator. The 4 changed rows (verified by git diff: ids "-", SYN_98093093, SYN_67199832, "-" replaced with SYN_23244607, SYN_10481154, SYN_26040571, SYN_23672090) keep their values. Traceable: seed 20261117 is named in the report and in tmpAI/scan/ (untracked); the one-off correction script is NOT in git, so the pick can be redone only from the report. A note in the commit text names it. A small gap in traceability, not a defect for the data.
B11. Other recipes. verified (run, my own count): 1_test_data_ST22_dummy folder: metadata 42 ids, 42 rows; Bracken, FastP, MLST, Quality_metrics, Quast, Summary each 42 distinct and 0 foreign; Detailed_Summary 280 rows, 42 distinct; PlasmidFinder 163 rows, 41 distinct (1 missing); ResFinder 70 rows, 38 distinct (4 missing, no foreign). 2_VIGAS-P VirulenceFinder: 42 distinct ids, 0 foreign, 0 missing (1315 rows of which 984 distinct: duplicated rows, not judged here, the builder's note 7 says 583 exact duplicates). figshare and 1_Abromics_general_pipeline: not counted by me (the test passes and the report counts 980 ids / 42 ids); I relied on the new test, which passed for them. That is reasoned, not run by hand.
B12. Cache list. verified (run). Section A files exist in the MAIN folder and none is tracked by git (git ls-files returns nothing for tmp/ and the three tmpAI audit folders). My find in tmp/ and tmpAI/ found the same demo_join files, the same two sessions ending in 97e260818d24, and nothing the list misses outside tmpAI/panel (not scanned by me beyond the list). The sessions are folders named "<hash>:97e260818d24" with an assembly.json. Not checked: the other worktrees' own tmp/ folders (.claude/worktrees/*/tmp) and the agent_sessions folder contents (it exists); I did not scan them for old demo results. I deleted nothing.

WHAT I DID NOT CHECK
- The four browser files (test_shiny_smoke*, test_export_download, test_every_app_features_starts) and test_shiny_na_tick.py (browser): not run. The edits there follow the new numbers by arithmetic only.
- That figshare and 1_Abromics_general counts match: relied on the passing test, not my own count.
- Gallery previews (report says 34 identical): not run.
- Whether the app shows the right text and counts in a browser for demo_abromics.
- Other worktrees' tmp/ caches.
- Mutation of the new test by me (I read the break tests and ran the generator break; the builder's claim that putting the old MLST file back makes 5 tests fail I did not repeat).
- The builder's part 7 "odd items re-run" table: not re-run by me item by item.
