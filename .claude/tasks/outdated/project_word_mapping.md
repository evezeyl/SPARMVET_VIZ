> **OUTDATED (moved here on 2026-11-12; kept for history only, do not follow):** mapping of the word "project" for the configuration rename, which is done. Replaced by: ADR-091. Original path: `.claude/tasks/project_word_mapping.md`.

# Mapping: the word "project" (CONFIG-PROJECT-WORD-1)

Decided with Eve on 2026-11-07. "Project" was the generic word that replaced "species" (Terminology.qmd,
ADR-003/ADR-029b, February 2026). Today it is a second name for the data analysis recipe, and IRIDA and
Galaxy have their own "project". One meaning per word: the recipe is called the recipe; where the text
means the identifier, it says "recipe id".

## 1. Rename: "project" = the open recipe

| Where | Old | New |
|---|---|---|
| Dropdown input | `project_id`, label "Project Selection" | `data_analysis_recipe_id`, label "Data analysis recipe" |
| Bootloader | `get_default_project()`, `project_dir`, "No projects found" | `get_default_data_analysis_recipe()`, `data_analysis_recipes_dir` |
| Orchestrator, exporter, ingestion, export, data import, sessions, test_lab | `project_id`, `proj_id` | `data_analysis_recipe_id` |
| Cache keys | `compute_project_keys`, `ProjectKeys`, `_project_keys` | `compute_data_analysis_recipe_keys`, `DataAnalysisRecipeKeys` |
| Asset cache | `_asset_cache[project_id]` | `_asset_cache[data_analysis_recipe_id]` |
| Messages | "Project 'x' loaded", "Project data analysis recipe not found", "active project", "Project: x" | "Data analysis recipe ..." |
| test_lab field | "Project ID (snake_case)", `my_project` | "Data analysis recipe ID", `my_data_analysis_recipe` |
| Export folder | `data_analysis_recipes/<proj>/` | `data_analysis_recipes/<data_analysis_recipe_id>/` |
| Export scope | "Global project" | "Global" |
| Blueprint text | "Select a project to view its TubeMap" | "Select a data analysis recipe ..." |

## 2. Info panel

`project_info` panel (showed only the deployment name) becomes `data_analysis_recipe_info`, label "Info".
It renders the `info:` mapping of the open recipe generically: every key is a label, a nested mapping is
shown as nested lines, a list as a list. No fixed field list. `display_name` and `subtitle` also feed the
title banner. `info:` stays outside the cache keys (display only). Old panel type is refused by
`renamed_keys.py`.

## 3. Recipe files

Top-level `type:` (species / project / pipeline / audit) is read by no code: remove from all recipes and
templates, refuse it in `legacy_keys.py`. Templates named after species or projects (`example_species_config`,
`e_coli`, `simple_project_template`, `complex_project_template`) get neutral names after reading what each shows
(decided in the rename commit and recorded here).

## 4. Kept

IRIDA's project (`get_irida_project_id`, deployment guide sentences, ADR-048), `pyproject`, `project_root`,
"this project" (SPARMVET_VIZ itself). History (ADRs, archives, logs) keeps the word, marked as history.

## 5. Other names

- Palettes: "Project palette" -> "Deployment palette" (colour widget source `project` -> `deployment`,
  README, rules, `config/palettes.yaml` header).
- App features name `project-independent` -> `standalone` (files, README, docs, rules, tests). The docs say
  what it means: a researcher who manages their own data, not fed by a pipeline.

## Guards

Old-words audit counts "project" outside the allowed list; `renamed_keys.py` refuses `project_id` in
sessions, `project_info` and `project-independent`; `legacy_keys.py` refuses recipe `type:`.
