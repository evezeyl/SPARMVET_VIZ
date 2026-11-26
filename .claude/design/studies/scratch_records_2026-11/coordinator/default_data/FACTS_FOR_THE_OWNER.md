# Which data file a recipe reads today, per deployment (builder of the default-data test, 2026-11-21; filed by the coordinator)

For your decisions D-0425 (the paths of the shipped recipes are an optional default), D-0426 (the user selects the data where the default is not there) and D-0427 (the opening stops where no data can be selected). RUN = run headless by the builder; READ = read at file:line. Nothing in the app was changed.

## Your requirement is met today, and now tested
"We need to ensure that the recipe read the test data as a default fallback": with the local development deployment, each of the 7 shipped recipes reads, for each of its 26 tables that declare a path, exactly the file its own `source.path` names (RUN; test `app/tests/test_recipe_default_data.py`, 18 cases, on branch `task/default-data-test`). No case was found where it does not.

## How the file of a table is chosen today (READ, `app/modules/orchestrator.py:172-195`)
1. A recipe imported from a bundle reads only the data that came with its bundle.
2. Otherwise, a table that declares a path reads that file. If that file is missing, nothing else is read in its place: the recipe is refused with a reason that names the table and the file (RUN).
3. A table with no declared path reads `<table name>.tsv` in the data folder of the deployment.
4. A deployment that sets `data_lookup: by_dataset_id` (only the pipeline test deployment does) ignores the declared paths: every table reads `<table name>.tsv` in the deployment's data folder.

## What the demo recipe reads, per deployment (RUN)
| Deployment | What it reads | What the user is told |
|---|---|---|
| local development | its own declared files in the test data | nothing needed |
| the two demo deployments | the same files | nothing needed |
| the pipeline test deployment | NOT its declared files: the files with the tables' names in the pipeline's data folder (today byte-identical copies) | nothing: no screen says the data is not the declared one |
| a pipeline-style deployment with an empty data folder | nothing; the recipe is refused | 12 problems; the tip says to check the recipe's `source.path`, which is wrong there, because that deployment ignores it |

## Findings
1. **One case where a recipe runs on other data than its declared path without a word:** the pipeline-style lookup. This is the decided delivery path for pipelines (the pipeline puts the files there), so it is reported, not called a defect. For D-0426 and D-0427 it matters: the screen never says which data file a table was read from.
2. **There is no "select the data" step.** A user's file wins only by REPLACING the recipe's file in place through HOME's Data Import, with no copy of the old file (already known: task DATA-IMPORT-OVERWRITE). `testing_mode` only decides whether Data Import shows its upload slots; it does not change which file is read (READ `app/handlers/data_import_handlers.py:83, 131`).
3. **The default paths work only when the app is started from the repository folder.** The recipes write `./assets/test_data/...` and the path is used as written, relative to the folder the app was started in (READ `orchestrator.py:195`).
4. **A wrong tip** in the refusal for the pipeline-style lookup (see the table).

## Questions these raise (yours; not asked yet)
- Should the screen say, per table, which file was read (the declared default, a file the user selected, a file the pipeline delivered)?
- Should a recipe's relative data path be read from the deployment's place, not from the folder the app was started in? (This is part of "the deployment file decides what may be read", D-0425.)
- The wording of the refusal tip for a pipeline deployment.

## Not verified
The browser and HOME's screens; the retest deployment; a pipeline run where the delivered file differs from the declared one (only identical copies exist today).
