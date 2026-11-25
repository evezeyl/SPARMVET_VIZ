# HOME, Data Import: facts for the owner's questions a and b (2026-11-21; from a scout's read of `dev` 45e539a5; nothing was run)

"read" = read at the file and line given. "reasoned" = follows from the code, not run.

## a. A recipe imported from a bundle: why is the upload refused?

**It is refused by choice, not because a replacement would fail.** The refusal is an agent's provisional choice (`app/modules/data_import_check.py:43-46`, read).

- The refusal: constant `IMPORTED_REFUSAL`, `data_import_check.py:47-49`; the condition is `data_import_check.py:213-215` (the place of the file is "none" for an import, on purpose: `app/modules/orchestrator.py:204-205`).
- Where the data of an import lives: `<user data>/_imports/<recipe id>/data/<table>.<ext>` (`app/modules/bundle_importer.py:16-18, 261-266`). The app reads that folder first and ignores the recipe's own path (`orchestrator.py:182-184`).
- The hashes: the "data" hash of the bundle is compared once, at import. It records match or mismatch and never refuses (`bundle_importer.py:24-25, 302-304, 343`). It is not run again inside that file at a later open.
- If a replacement were allowed (reasoned): two places must change (`orchestrator.py:204-205` and `data_import_check.py:213-215`); the app would then read the new file; the full check of the file would apply as for any table; the stored tables would be rebuilt, because their keys hold the content of the data files (`app/modules/cache_keys.py:462-474`); the hash recorded at import would not be compared again, so the import would no longer be what the bundle verified; the old file would be overwritten with no copy.
- HOME already recomputes the data hash from the current files and warns when it changed (`app/handlers/home_theater.py:1528-1550`, read).
- Not known by reading: how an export or a saved session would show the change.

## b. How each shipped deployment finds its data files today

Two ways exist (`orchestrator.py:159, 177-195`; default `app/src/bootloader.py:121`):
- **By the recipe's path** (`data_analysis_recipe_paths`, the default): the file is the one the recipe names (`source.path`); without a path, the file named after the table in the raw data folder.
- **By table name** (`by_dataset_id`): the recipe's path is ignored; the file is `<table>.tsv` or `.parquet` in the raw data folder. Meant for data delivered by a pipeline.
- A recipe imported from a bundle overrides both: its data is always the folder of its import.

One more fact: the upload control of Data Import appears only when the app features have `testing_mode` true. Otherwise the panel shows a read-only list of paths (`app/handlers/data_import_handlers.py:131-139`).

| Deployment file | What it is for | How data is found | Where the data is | Who delivers it | Default app features | Data Import shown | What Data Import does today |
|---|---|---|---|---|---|---|---|
| `local/local.yaml` | development | by the recipe's path (default) | `assets/test_data/` | test data of the repository | developer | upload | accepted after the check; the recipe's file is overwritten, no copy |
| `local/retest.yaml` | the retest | by the recipe's path (default) | `assets/test_data/` | test data | developer | upload | same as local |
| `demo/web-demo.yaml` | web demo | by the recipe's path (default) | `assets/test_data/` | test data | web-demo | read-only list | nothing written |
| `demo/demo-vetinst.yaml` | institute demo | by the recipe's path (default) | `assets/test_data/` | test data | demo-vetinst | read-only list | nothing written |
| `pipeline_test/pipeline_test.yaml` | headless test of a pipeline delivery | **by table name** (line 19) | `assets/test_data/duplicated_1_test_data_ST22_dummy/` | a simulated pipeline | none in the file (set at launch) | read-only with pipeline-static; upload of metadata with pipeline-exploration-advanced | **refused** (`BY_DATASET_ID_REFUSAL`, `data_import_check.py:207-208`) |
| `connect/connect_template.yaml` | Posit Connect template | by the recipe's path (default; no key in the file) | `inputs/`, "populated by your pipeline" | the pipeline | pipeline-static | read-only list | nothing written |
| `templates/deployment_template.yaml` | template of all keys | not in the file | `inputs/`, "populated by the pipeline or by an admin" | pipeline or admin | pipeline-static | depends on the app features | depends |

Points to look at together:
- Only ONE shipped deployment finds data by table name: the pipeline test. The refusal I chose applies only there today.
- The Connect template says the pipeline fills `inputs/`, but it does not set "by table name". With the default, the app reads the recipe's own path, not `inputs/` (reasoned from `orchestrator.py:185-195`). The template and its use case may not agree.
- The docs (`docs/workflows/connector.qmd:170-190`, `docs/reference/environment_variables.qmd:174-186`) list pipeline test, Galaxy and IRIDA as "by table name". No Galaxy or IRIDA deployment file is shipped.
- `config/deployment/README.md` does not mention the data lookup.

## Not verified
Nothing was run. Whether the session code checks the bundle hash at open; whether the Connect template works as its comments say; the scripts `bundle_connect.sh` and `create_test_deployment.py`; whether the test data files named exist.
