# How data reaches the app, and what checks a path today (study for question 8 of the recipe-arguments report)

Digest by the coordinator of a scout's survey, 2026-11-18. The scout READ the code; it ran nothing and made no link.
A trial on a copy (the folders passed to the check, a file-type block, the eight cases and a link run for real) is the next step, then the panel. Nothing is decided here.

## In one page: what a user does, and what the app does with the path

1. **A recipe of the repository names a development data file.** The checker accepts the path when it is relative and has no `..`. The app opens it as written, from the folder the app was started in. Nothing checks the file at the moment it is opened.
2. **The deployment names five folders** (raw data, recipes, cache, user data, gallery). They are resolved against `project_root` when it is set, else against the folder the app was started in. An absolute path or a `..` in them is accepted. A link is followed.
3. **The user uploads his own file in the Data Import panel.** If the recipe table has no path, the file is copied into the raw data folder under the table's id. If the recipe table HAS a path, the upload is copied OVER the file at that path, with no question and no notice. The recipe file is not changed. The docs say uploads go to the raw data folder.
4. **A pipeline deposits files.** The deployment says "find the data by the table's id"; the app looks for `<id>.tsv` or `<id>.parquet` in the raw data folder and ignores the recipe's path. The IRIDA fetch is a stub (not built). The Galaxy one does nothing beyond resolving folders.
5. **An API fetch:** not built. No network client in the app or the libraries.
6. **Piped or streamed data:** not supported.
7. **A default file beside the recipe (a lookup table):** not resolved against the recipe's folder. The checker resolves a data path against the project root; the run uses the start folder; only `!include` uses the recipe's folder. The gallery examples must name their data by the full path from the project root.
8. **A recipe moved to another machine:** its relative paths keep their text and are read from wherever the app runs. An imported bundle finds its data by table id in its own import folder; the recipe's paths are not touched.

## The check itself

- Shape check (code PA01), active: refuses an empty path, a web address, `~`, an absolute path, a Windows drive, any `..` (`libs/utils/src/utils/recipe_paths.py:22-38`).
- Folder check (code PA02), WRITTEN AND TESTED BUT OFF: the real path (links resolved) must lie inside an allowed folder (`recipe_paths.py:41-51`). It runs only when the caller passes the allowed folders (`recipe_check.py:358`), and no caller in the app does (`data_analysis_recipe_validator.py:247,258,277`; `gallery_manager.py:85,196`). So a link inside the project that points outside passes in the app today.
- Includes have their own rule, active: relative to the recipe file, real path, inside the project root (`recipe_loader.py:59-72`).
- At the moment a data file is OPENED there is no check at all (`ingestor.py:74-78`, `orchestrator.py:86-88`), and none where the upload writes (`data_import_handlers.py:326-336`).
- File types: the reader accepts `.tsv` and `.parquet` (`ingestor.py:15,76`); all 32 shipped tables are `local_tsv` (the review session's count).

## Three different bases for one relative path (the central fact)

| Who | Resolves a recipe's data path against | Where |
|---|---|---|
| The checker | the project root (nearest folder with a `pyproject.toml`) | `recipe_paths.py:46`, `recipe_loader.py:116` |
| The run | the folder the app was started in | `ingestor.py:74` |
| An include | the recipe file's folder | `recipe_loader.py:60,67` |

## Table of the eight cases

| Case | Path comes from | Resolved against | Checked | Gap today |
|---|---|---|---|---|
| 1 development data | recipe table | checker: project root; run: start folder | shape only | folder check off; link passes; two bases |
| 2 deployment folders | deployment file | `project_root`, else start folder | "exists" only | absolute and `..` accepted; docs disagree with the code |
| 3 upload | the browser's temporary file | the recipe's path if set, else raw data folder | none | overwrites the recipe's file silently |
| 4 pipeline deposit | raw data folder + table id | raw data folder | exact name; error if both types exist | IRIDA fetch not built |
| 5 API | - | - | - | not built |
| 6 pipe | - | - | - | not supported |
| 7 file beside the recipe | recipe table or include | project root / start folder / recipe folder | shape; include rule | a lookup table beside the recipe is not found by a path relative to the recipe |
| 8 moved recipe, bundle | recipe text; bundle by table id | start folder; import folder | shape | relative paths follow the start folder |

## What the folder check would do in each case, if the app passed folders

- Passing the deployment folders: case 1 allowed (under raw data); case 4 allowed; case 7 (a lookup beside the recipe) REFUSED unless it sits in the raw data folder.
- Passing the recipe's own folder: case 1 refused unless the recipe sits beside its data; case 7 still refused today, because the checker resolves against the project root, not the recipe folder.
- Passing both: cases 1 and 4 allowed; case 7 allowed only if the base for a recipe-relative path is decided.

## Records and docs that disagree (found, not resolved)

- The ledger line D-0035 says "no path engine change"; the format text (DEC30) says the app passes the allowed folders. Which is later was not settled by the scout.
- `docs/deployment/deployment_guide.qmd:57` says the app never uses absolute paths for data; the code keeps an absolute deployment folder (`filesystem.py:48`).
- `docs/workflows/connector.qmd:125` says all folders are relative to `project_root`; `:250` says they resolve against the start folder; the code does the second when `project_root` is not set.
- `connector.qmd:129` says uploads go to the raw data folder; the code writes to the recipe's path when it is set.

## What must be decided (plain questions; the panel proposes, Eve decides)

1. Is the folder check switched on (option A of question 8)?
2. Which folders may a recipe's data path name: the deployment's raw data folder, the recipe's own folder, the project root, several of these?
3. Is the path checked again at the moment the file is opened, or only when the recipe is loaded?
4. A link that leaves the allowed folder: refused, or followed?
5. The file-type layer (her addition): only `.tsv` and `.parquet` are opened, whatever the folder?
6. An uploaded file: always into the raw data folder under the table id, or over the recipe's path, or the user chooses each time? (Today: silently over the recipe's path.)
7. One base for a relative data path: project root, recipe folder or start folder?
8. A default lookup table: an include, a data path, or a new kind of reference with its own base?
9. An API fetch or a pipe: designed now, or only "deposit in the raw data folder" for now?
10. A moved recipe: are relative paths re-based at import, or do they stay as written?
11. The text a user reads on a refused path.
12. Docs corrected to the code, or code to the docs?
