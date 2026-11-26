# Caches and stored results made from the old demo data (D-0206), NOT removed yet (DATA-IDS-FIX-1 part 6)

Paths are relative to the MAIN tree `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ`. Found by RAN `grep -a` for `SYN_<8 digits>`, `demo_abromics`, `demo_join` in `tmp/`, `tmpAI/`, `agent_sessions/` and by reading the deployment files that name where the app stores results (`config/deployment/*`: `tmp/UI_TEST/`, `tmp/pipeline_test/`, `tmp/DEMO/`, `tmp/RETEST/`; `parquet_data/` folders do not exist). Only the demo data changed (MLST and ResFinder demo files); the ST22, figshare and retest data did NOT change (their data hash `a1ae45bde9f0` etc. is the same), so their stored results are still correct. The app compares a stored table's key (recipe plus data hash) with the current one and never serves an old table for new data; the files below are leftovers.

## A. Safe: rebuilt by the app or by a script (nothing of the user's is lost)

| Path | Size | What made it |
|---|---|---|
| `tmp/UI_TEST/user/anchors/demo_join.parquet` | 2.4 KB | the app (Tier 1 anchor of `demo_abromics`, old 40-row table) |
| `tmp/pipeline_test/user/anchors/demo_join.parquet` | 2.3 KB | the app (same, deployment `pipeline_test`) |
| `tmp/UI_TEST/user/_sessions/076137b0a0eb:97e260818d24/` (`assembly.json` only, 811 B) | 1 KB | the app: record of the assembly of `demo_abromics` on the old data (session key ends with the old data hash `97e260818d24`) |
| `tmp/pipeline_test/user/_sessions/b98f603ac5f7:97e260818d24/` (`assembly.json` only, 772 B) | 1 KB | the app: same, deployment `pipeline_test` |
| `tmpAI/audit_manifest_integrity/demo_abromics/` and the loose `tmpAI/audit_manifest_integrity/EVE_*_demo_join.{parquet,tsv}` | part of 70 MB (the folder also holds ST22 and figshare results; remove only the demo files) | the audit script `audit_manifest_integrity` (rerun by `./scripts/run_audits.sh`), 2026-11-06 |
| `tmpAI/audit_recheck/demo_abromics/` | part of 636 KB | the same audit, 2026-11-06 |
| `tmpAI/audit_data_analysis_recipe_integrity/demo_abromics/` | part of 35 MB | the recipe integrity audit, 2026-11-14 |

Total of section A: 7 stored files in `tmp/` (about 6 KB) and 3 demo folders / 6 demo files in `tmpAI/`.

## B. Not sure (agent evidence of earlier decisions, or the user's own work: look before removing)

| Path | Size | What it is | Why not sure |
|---|---|---|---|
| `tmpAI/panel/round5/dump_old/demo_abromics__00{1,2}.parquet`, `tmpAI/panel/round5/dump_new/demo_abromics__00{1,2,3}.parquet` | 1.4 MB each folder (all recipes) | table dumps of the categorical migration comparison, Eve's round 5 | they document a comparison that was decided; reports may point at them |
| `tmpAI/panel/verification/dump/{all_2ac83ddb,all_ce373923,wt_9490490d,wt_9490490d_pre,wt_99a14148,wt_99a14148_pre}/demo_abromics/*.parquet` | 3.9 MB (all recipes) | the verification session's table dumps (check_5_baseline.md) | evidence of an earlier check |
| `tmpAI/panel/round5/pics_new*/demo_abromics__demo_st_by_source.png`, `tmpAI/panel/round5/python_recipe/png/demo_abromics.*.png`, `tmpAI/panel/round5/*.json` that hold demo rows (`render2..6.json`, `b0.json`, `old_baseline.json`, `dump_*/names.json`, `pics_*/hashes.json`), `tmpAI/panel/round7/{cmp_*.json,table_b.json,values.json,fields.json}` (2.4 to 2.7 MB each), `tmpAI/panel/round4/string.json` | about 10 MB | pictures and comparison records of the panel rounds that hold the old demo table | evidence, not caches; a rerun would give other numbers |
| `tmpAI/golden_now.json`, `tmpAI/golden_baseline_a.json`, `tmpAI/golden_baseline_b.json` | 22 to 27 KB each | copies of the golden baseline made by agents | scratch copies, but they hold the old demo hashes |
| `tmpAI/qa_work/`, `tmpAI/mig_try/`, `tmpAI/panel/round4/pipes_string/`, `tmpAI/panel/round7/recipe_fixes/`, `tmpAI/panel/round7/w/` (copies of `demo_abromics.yaml` and of the data) | small | scratch copies of recipes | they do not hold results; the old demo data is in git history in any case |
| `tmpAI/panel/data_ids/` (my predecessor's check of the ids: `demo.py`, `demo_out.txt`, `data_id_consistency.md`) | small | the evidence of this defect | KEEP: it documents why the data was changed |
| Saved sessions of other recipes in `tmp/UI_TEST/user/_sessions/`, `tmp/pipeline_test/user/_sessions/`, `tmp/DEMO/user/_sessions/`, `tmp/RETEST/user/_sessions/` (ST22 `a1ae45bde9f0`, retest, figshare) | 1 to 3 KB per session, 45 sessions in all (2 of them demo, in section A) | the app | NOT made from the changed data; if she wants "all cached data" removed (D-0206 wording), these and the other anchors are the rest: `tmp/UI_TEST/user/anchors/` (28 files, 400 KB), `tmp/pipeline_test/user/anchors/`, `tmp/DEMO/user/anchors/`, `tmp/RETEST/user/anchors/`. They would be rebuilt; any saved T3 file (`t3_*.json`) would not: none exists today (RAN: `find -name "t3_*.json"` finds nothing under `tmp/`) |
| Older exports `tmp/test_exports/*.zip`, `tmp/audit_exports/` | few MB | exports of earlier test runs (ST22 data) | not made from the demo data |

## Never touched: source data, recipes, tests, tracked files, `assets/gallery_data/` previews (no gallery bundle reads the demo data: RAN grep).
