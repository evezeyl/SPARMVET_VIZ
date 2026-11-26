# HOME data picker: git facts (2026-11-21, from git log and git show, read only)

1. Was a data picker ever in HOME: NO, not found.
- Searched app/ history for data_selector, data_source_select, raw_data_select, select_data, choose_data, data_import_dir, home_data_source: zero hits.
- Every input_select, input_text, input_selectize, input_radio_buttons added in app/ with data, dir, path, folder, source or location in its id was checked. None picks a data file or data folder. They pick: a recipe (data_analysis_recipe_id, earlier project_id, label "Project Selection", from 2026-04-18 a89bc218, rewritten 2026-04-23 8b285410), a pipeline of a recipe (dataset_pipeline_selector, 2026-04-19 a179eef0), a stored recipe (stored_data_analysis_recipe_selector), a secondary dataset in Blueprint, and a source_table.
- Commit 29bf346c (2026-05-01, "feat(25-F): Data Import panel") added only the Data Import panel: a read-only list of the data paths of the active recipe (code with the file path as text) and, in testing mode, upload slots (ui.input_file, 2 of them). Its files: app/handlers/data_import_handlers.py (new, 158 lines) and app/handlers/home_theater.py. No select, no text field for a path.
- The archive plan (tasks_archive_phase25.md) names a commit F2 "active data selector ... User can override". No commit with that message exists in git (grep for "active data" and "F2" gives nothing relevant). It was planned, never committed as such. The 25-F row of the archive gives only 29bf346.
- Nothing was removed, so there is no removal commit. The only data-path controls since then are the Data Import panel and its uploads (commits 173471e9 2026-05-02 assignment table; 41c656cc, 07bdc883 2026-11-21 upload checks).
- Docs commit de05eaab (2026-11-13) records "data selector T1/T2/T3" as DECIDED, not built.

2. What exists today (from the scout's report): the recipe selector lists the one declared recipes folder; Data Import shows the data paths as text and has a browser upload. No control picks a data file or folder from a place.

3. What the owner's sentence most likely refers to (REASONED): the recipe selector in HOME (Manifest/Recipe Choice, "Project Selection" since 2026-04), which does pick from one declared place (the recipes folder) and has worked since April. The owner probably means that pattern: pick from a declared place, with one place today, now wanted for data. It is not a removed data control.

4. Not verified: git history before the squashed or renamed paths (git log -S sees only strings, a control built through a helper or a different widget name could be missed); whether an uncommitted branch or stash had an F2 selector (searched --all branches only); the behavior of the controls (not run); the archive lines 17 and 229-243 were read, nothing else of the archive.
