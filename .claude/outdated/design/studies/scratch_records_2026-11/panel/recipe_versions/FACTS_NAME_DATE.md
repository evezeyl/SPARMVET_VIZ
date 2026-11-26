# Facts for the six open points of the name_date rule (scout, 2026-11-20 night; compact copy by the coordinator)

Decided: D-0389 (export always holds the original recipe), D-0390 (recipe file name `name_date` exactly; upload under an existing name refused). Open points a to f: `M417_owner_decisions_and_open_points.md`. One at a time to the owner.

a. Date form
- Forms in use: export zip `%Y%m%d_%H%M%S_<label>` (export_handlers.py:2256-2260); session snapshot `%Y%m%dT%H%M%S%f` UTC (session_manager.py:1048); imported bundle recipe `<id>_imported_%Y%m%dT%H%M%S` (bundle_importer.py:255); Gallery `info.submission_date` `YYYY-MM-DD`.
- No character rule for a recipe id; only `id` == file stem (data_analysis_recipe_validator.py:436-442; ADR-092). No sanitising. Shipped names hold no hyphen. Plot ids must be snake_case (recipe_check.py:1121): plots only. Not run: whether a hyphen or dot in an id breaks anything.

b. Scope and counts
- `config/data_analysis_recipes/pipelines/`: 8 files (one is a leftover `zz_gate_gap_stage_*`); `retest/` 4; `templates/` 5; `experimental/` 1. Gallery: 35 bundles, file always `data_analysis_recipe.yaml`, id = folder name. Test recipes: 300+ yaml under tests.
- The demo recipe name `1_test_data_ST22_dummy` literally: 226 occurrences in 71 files (app 94 in 41, mostly tests; config 99 in 11; assets 16; libs 8; docs 7; rules 2). Deployment defaults naming it: demo-vetinst.yaml:7, web-demo.yaml:7, pipeline_test.yaml:22.
- The id is NOT in the session key (hash of file bytes + data hash), not in cache keys, not in the export file name. It is stored in the session record (`data_analysis_recipe_id`) and compared on restore.

c. Selector: list = glob of `*.yaml`, unsorted (bootloader.py:416-417); label = file name; default = env var, then deployment key, then first of the list (:587-602, :656). No notion of "latest".

d. Writers: BLUEPRINT save overwrites the loaded component file in place, no copy (blueprint_handlers.py:1187-1189); BLUEPRINT fragments (:1512-1517); upload `shutil.copy` with no existence check = silent replace (ingestion_handlers.py:44-51); scaffolder `write_recipe` (create_data_analysis_recipe.py:223; refusal of an existing file not read); TEST_LAB outputs not read; audit file writer not built.

e. D-0362: today the refusal compares the id only (session_manager.py:242-252); other content (hash of bytes) only warns (session_handlers.py:559-567; the ledger's citation :556 is the id refusal: off). With a dated name, a new version = another id = the "belongs to another recipe" refusal (D-0317); D-0362 then meets only an edit that keeps the name. A comment-only edit changes the hash.

f. No delete-recipe control in the app. Recipes live in `data_analysis_recipes/` of the deployment; whether writable / reachable by the user depends on the deployment (template says only user_data must be writable).

g. Audit recipe: no ledger line names its file or id (D-0324, D-0328, D-0332, D-0333, D-0339, D-0340, D-0354 read). `templates/audit.yaml` exists with id `audit` (relation not read). Study: V1' = the audit recipe file is the stored old version.

Discrepancies: D-0362's citation line; the scaffolder's default folder `assets/template_data_analysis_recipes/` does not exist.
