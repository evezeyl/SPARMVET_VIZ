# Names pass: dry run report (2026-11-22, second version: with D-0468 to D-0472 and the key of the banner switch)

Made by `assets/scripts/migrate_display_names.py` (branch `task/names-migration-dry-run`, worktree `SPARMVET_VIZ_wt_names_dryrun`, 5 commits on `dev` 934be492), run on the files of `dev` 934be492. Nothing was changed in the repository. The migration itself waits for the owner's remaining answers.

## In plain words

- The dry run would make 496 changes in 175 files. It renames keys, removes `ui_title` lines and `deployment_name` lines, and writes no new text, except the banner switch where one applies (0 shipped cases). Comments, blank lines, key order, quotes and `!include` lines stay byte for byte.
- By kind of file: recipes 211 changes, recipe templates 40, Gallery bundles 68, test fixtures 171 (68 action recipes in `libs/transformer/tests/data` and 4 in `app/tests/equality/recipes`), deployment files 6, deployment templates 0, app features files 0.
- By rule: `info.label` to `info.ui_label` 122 (D-0410); `label` of a table to `ui_label` 85, of a join 39, of an input field 219 (D-0468); a plot entry's `ui_title` removed 25 (D-0409; 17 in the demo recipe, 3 in figshare, 5 in three templates; the task text said "5 shipped recipes": it is 5 recipe files and 25 plot entries); a group's `ui_title` 0; `info.name` and `info.ui_title` 0; banner `title` to `ui_label` 2, `subtitle` to `description` 2, `deployment_name` removed 2 (demo-vetinst and web-demo only; D-0411); app features `ui_title` removed 0 (no shipped file sets it); banner switch written 0.
- A second run on the migrated copy finds 0 changes. Conflicts (a key in both spellings): 0. Changes the script cannot place by text: 0.
- THE SCRIPT STILL CANNOT DECIDE (listed, 16 places in 5 cases, nothing changed): OC07 `display_name` of the 8 app features files (8 places; D-0468 is about recipe files only); OC06 `deployment_name` in 5 deployment files that have no banner title to take it (kept); OC09 `info.subtitle` in 2 recipes; OC05 what the Gallery writes in `info` (34 bundles: `label`, `description`, `submission_date`; the key itself is renamed like any recipe's); OC10 one comment that names old banner keys. OC15 (the banner switch where an app features file hides the banner and the mapping to a deployment is not one to one) has 0 cases in the shipped files, because no shipped app features file sets `ui_title`.
- Decided, listed with counts only: OC02 the `"label"` strings of the Python code are not renamed (890 places in 22 files of `libs/*/src`, text match); OC03 format number stays 1 (122 master recipes say `spec_version: 1`); OC04 old session files are refused, not converted (0 session files in the repository; the script never touches sessions). Would get the advice (no recipe name, D-0470): 0 recipes today.
- On a migrated COPY the recipe check refuses EVERY recipe, because the check and the spec still say `label`: `I01` (info.label is required, 122 of 122 master recipes), and now also `S01` and `S03` (a table has `ui_label`, the check wants `label`), `FD01` (an input field has `ui_label`), `J01` and `J02` (a join). Counts on the 20 pipeline, template, retest and equality masters: I01 20, S01 51, S03 51, FD01 248, J01 39, J02 39; on the 34 Gallery bundles: I01 34, S01 34, S03 34. Before the migration the same files give 0 refusals. The engine load of the 20 non-Gallery masters accepts all of them, before and after (0 refusals). So the code part of the pass starts with the spec and the check; see the code places below.

## Where the rules rest (ledger lines read in the main tree at eaf95b85)

- D-0468 (her words: "2.I think yes because we need to differentiate the recipe and the python code."), D-0469 ("3 we are still in development so the same format can stay"), D-0470 ("ok, we can try H1 and C - worse case we change after ...at usage and wishes of users"), D-0472 ("I should sit in the deployement H1"). The bracketed readings in those lines are the review session's, not hers. D-0471 holds no words of hers for its four points: it says that questions 4, 6 and 7 rest on D-0312, D-0411 and D-0407; I applied D-0471 as the coordinator ordered, and the script touches no session.
- D-0474 (the key `branding.show_recipe_name`; her words "H1 proposal accepted.") was relayed by the coordinator and is not yet in the ledger: the rule table cites it as "D-0474 (to be written)". Replace the citation when the line exists.

## The switch key `branding.show_recipe_name` (checked as ordered)

- Clash with the present `branding` keys of every deployment file: none. The keys present today: `theme_css`, `banner` (`logo_url`, `title`, `subtitle`), `contact`; no deployment file and no app features file contains `show_recipe_name` (searched in `config/`, `app/`, `libs/`, `docs/`, rules and design files).
- The list of allowed deployment keys: it does not exist today. D-0412 asks for it; it comes with the deployment standard (task DEPLOYMENT-STANDARD; its survey is `tmpAI/panel/deployment_standard/FACTS.md`; the recipe analogue is `libs/utils/src/utils/recipe_spec.yaml`). What exists: `app/src/bootloader.py:324-358` (`_validate_deployment`: only `data_lookup`, `session_import` and the required `locations`), `app/modules/renamed_keys.py:17-22` and `:95-108` (refusal of listed OLD keys only), and the readers `app/src/bootloader.py:591` (`branding.contact`), `:874` (`branding.theme_css`), `:877-879` (`branding.banner`).
- A validator that would refuse the new key today: none. The consequence is the opposite pitfall: the key is accepted and silently IGNORED until a reader exists (nothing reads it; HOME's banner at `app/handlers/home_theater.py:1137-1158` does not look at the deployment). So the pass must add the reader, the test and the entry in the allowed-key list in the same step. Not changed in this branch.
- Where the script writes it: `show_recipe_name: false` at the end of the `branding` block, only where exactly one deployment names the app features file (that hides the banner) as `default_app_features`. Not one to one (zero or several deployments) is listed in OC15 and the `ui_title` is kept. It cannot know that a launch names another app features file than the default (`SPARMVET_APP_FEATURES`): that is stated in the constant's comment. A key already written in the deployment is a conflict and nothing is written.
- Facts for the owner (printed by the script, section "Facts to name the recipe banner switch"): no shipped app features file sets `ui_title`, so the recipe banner is shown today in every shipped deployment. The deployment files and what their banner shows: demo-vetinst (default app features demo-vetinst; branding `theme_css`, `banner`, `contact`; banner title "AMR Surveillance — Overview", line "Norwegian Veterinary Institute", a logo), web-demo (default web-demo; branding `theme_css`, `banner`; banner with a logo and empty text), local and retest (default developer; no banner), pipeline_test (no default app features; no banner), connect_template and deployment_template (default pipeline-static; no banner).

## What I did NOT apply (listed instead)

- `display_name` of app features files (OC07), `deployment_name` where no banner title can take it (OC06, 5 files: `local`, `retest`, `pipeline_test`, `connect_template`, `deployment_template`), `info.subtitle` (OC09), the Gallery generator and the description place (OC05).
- Every banner switch case that is not one to one (none in the shipped files).

## Proof on a copy (scratch, `tmpAI/names_copy` and `tmpAI/names_base` in the worktree)

- Copy of `config/`, `assets/gallery_data`, `assets/ref_data`, `assets/test_data`, `assets/demo`, `libs/transformer/tests/data`, `app/tests/equality`. The migrated copy differs from the base in 175 files; the diff holds only: 455 `ui_label` lines replacing 453 `label` and 2 banner `title`, 2 `description` replacing 2 `subtitle`, 25 removed `ui_title`, 2 removed `deployment_name` (the other changed lines in the diff are the field mappings written on one line, where the key `label` inside `{type: String, label: ...}` is renamed).
- Recipe check (`checker_problems`, profile `run`) on the 20 non-Gallery, non-fixture masters: base 0 refused; migrated 20 refused, codes above. Gallery bundles (`utils.recipe_loader.check_recipe_file`, profile `gallery`, as `gallery_manager.py:91`): base 0 of 34; migrated 34 of 34. The engine load (`engine_load_problems`) of the 20 masters: 0 refusals before and after.
- NOT run: the load gate in a started app; the browser tests of the two customized deployments. The tests that record today's values exist on `dev` (`app/tests/test_deployment_branding.py`, `test_shiny_deployment_branding.py`, `deployment_branding_keys.py`); the one place that changes is `app/tests/deployment_branding_keys.py:7-8`. Read, not run: `app/src/ui.py:351-357` would drop the banner title and line silently when the keys are `ui_label` and `description` (the guard `.get("title")` is false), and `app/src/bootloader.py:122` would take its default name.

## Code places the pass will have to change (read at file:line, not changed)

Spec and recipe check
- `libs/utils/src/utils/recipe_spec.yaml:6` (header names `ui_title`), `:8-17` (`label_keys`, PENDING M271: info, schema, join, field), `:25-28` (`info` optional keys; `subtitle` listed), `:44-47` (group optional `ui_title`), `:51-57` (plot optional `ui_title` and `entry_keys`), `:90` and `:96-97` (the renamed lists name `info.label` and `label`), `:115`, `:118`, `:140` (refusal texts that tell authors to write `ui_title`).
- `libs/utils/src/utils/recipe_check.py:98` (doc names `ui_title`), `:182` and `:203-209` (`label_keys_of`, `label_key`), `:313-318` (I01 reads `info.<label_key>` and says it is required: the D-0408 / D-0410 point), `:480` (field keys: S01, S03, FD01, J01, J02 refuse `ui_label` on a table, join or field today, see the proof), `:1103` and `:1128` (a group or plot with no `ui_label`; an old `label` is told as renamed).
- `libs/utils/src/utils/engine_keys_migration.py:13`, `:19`, `:50` (`_ENTRY_ORDER`), `:516`, `:599-610` (the old migration WRITES `ui_title` for a moved `title:`; the new rule removes the key), and `assets/scripts/migrate_recipe_engine_keys.py:12` (docstring), with its tests `libs/utils/tests/test_engine_keys_migration.py`, `test_recipe_engine_keys.py`, `app/tests/test_migrate_recipe_engine_keys.py`.
- `app/modules/renamed_keys.py:19-26` (`RENAMED_DEPLOYMENT_KEYS`: where `deployment_name` and the banner keys get their refusal with the new name), `:35-41` (`RENAMED_APP_FEATURES_KEYS`: where the app features `ui_title` gets its refusal). D-0412 asks for allowed-key lists for both files; `app/modules/app_features_validator.py` has no key list today (it reads `name` at `:79`); the deployment list comes with DEPLOYMENT-STANDARD.
- `libs/viz_factory/src/viz_factory/plot_config_resolver.py:77` (comment on the ENTRY keys), `libs/viz_factory/src/viz_factory/viz_factory.py:225` (the message tells the author that the report name is `ui_title`).
Banner switch `branding.show_recipe_name` (D-0472, D-0474 to be written): nothing reads it today. Add: a reader in `app/src/bootloader.py` beside `:591`, `:874`, `:877-879` (read as true when absent), the HOME banner at `app/handlers/home_theater.py:1137-1158`, a test, and the key in the allowed-key list of the deployment file (D-0412). No validator refuses it today and none would accept it by name: see the check in the section "The switch key" below.
Writers of recipes (they write the old keys today)
- `libs/utils/src/utils/recipe_factory.py:82`, `:102` (table and join `label`), `:164` (`"info": {"label": ...}`).
- `libs/blueprint_arch/src/blueprint_arch/new_recipe.py:19-27` (a new draft needs a `label`; "was `info.name`").
- `libs/viz_gallery/src/viz_gallery/example_recipe.py:104` (the Gallery generator writes `info = {"label": label}`), `:109` (table `label`). `assets/scripts/convert_gallery_examples.py:9`, `:86`, `:151`.
- `libs/test_lab/src/test_lab/bootstrapper.py:110`, `:178` (info label), `libs/test_lab/src/test_lab/scaffolder.py:204` (info label), `:136`, `:156` (join and field labels), `assets/scripts/SF_create_data_analysis_recipe.py:39`, `assets/scripts/create_data_analysis_recipe.py:121` (field label).
- `app/handlers/blueprint_handlers.py:2543`, `:2611` (the BLUEPRINT Info form reads and writes `info.name`; HOME reads `info.label`: the recorded defect of D-0406), `:535` and `app/modules/blueprint_plot_view.py:9` (comments that name `ui_title` as an entry key).
HOME banner chain and invented fallbacks
- `app/handlers/home_theater.py:1137-1158`: the banner reads the app features `ui_title` (`text`, `subtitle`, `visible`) from `bootloader.config`, then `info.label`, then `info.subtitle`. D-0411 (3) removes the first; D-0410 makes `info.ui_label` the one name; `info.subtitle` as the banner line has no decision (OC09, 2 recipes).
- `app/handlers/home_theater.py:102-105` (`group_tab_label`: `ui_label`, else `description`), `:108-110` (`plot_tab_label`: else the plot id in title case), `:113-116` (`plot_list_label`: else `name`): the invented fallbacks of D-0409 (3).
- `app/handlers/home_theater.py:1970-1977`: the deployment banner reads `title` and `subtitle`.
Export report
- `app/handlers/export_handlers.py:359`, `:368-373` (`plot_report_name`: `ui_title`, else `ui_label`, else the plot id in title case: the D-0409 (2) point); other readers of a group name in the report were not searched.
Bootloader, ui, server
- `app/src/bootloader.py:122` (`deployment_name` with default "SPARMVET_VIZ (Local Dev)"), `:398-406` (`app_features_display_name` reads `display_name`, else `name`), `:877-879` (`get_ui_banner`, docstring names `title`, `subtitle`), `app/src/ui.py:343-359` (banner reads `title`, `subtitle`, `logo_url`), `app/src/server.py:162-163` (`app_features_display_name`).
Connector
- `libs/connector/src/connector/base.py:64-66` (`get_deployment_name` reads `deployment_name`), `libs/connector/README.md:29`, `assets/scripts/create_test_deployment.py:68` (writes `deployment_name`).
Tests that name or build the old keys (found by text search; each must be read when the pass is built)
- `ui_title`: `app/tests/test_blueprint_plot_open.py`, `test_blueprint_tier_files.py`, `test_export_report_names.py`, `test_export_report_texts.py`, `test_home_reads_the_plot_entry.py`, `test_shipped_recipes_hygiene.py`, `libs/utils/tests/test_engine_keys_migration.py`, `test_recipe_engine_keys.py`, `libs/viz_factory/tests/test_no_silent_error.py`, `test_plot_config_resolver.py`.
- `deployment_name`: about 20 tests build a deployment with that key (for example `app/tests/test_bootloader_launch.py:37,58`, `test_deployment_branding.py:58,81,91` asserts `b.deployment_name`, `libs/connector/tests/test_connectors.py:44,111,151-157`, `libs/utils/tests/test_path_expansion.py:25-28`). Once an unknown key is refused (D-0412) they must be changed.
- banner keys: `app/tests/deployment_branding_keys.py:7-8` (the one place), `test_deployment_branding.py`, `test_shiny_deployment_branding.py`, `test_shipped_deployments.py`, `test_bootloader_launch.py`.
- `info.label` or `label` in built recipes: `app/tests/gate_stage.py`, `test_checker_names_what_a_component_is.py`, `test_join_key_one_pin.py`, `test_table_keys.py`, `test_writers_emit_format_one.py`, `uncertain_drop_world.py`, `libs/blueprint_arch/tests/test_new_recipe.py`, `libs/utils/tests/test_audit_copy.py`, `test_recipe_check.py`, `test_recipe_loader.py`, `test_recipe_migration.py`, `libs/viz_gallery/tests/test_gallery_bundle.py`.
- `display_name`: 12 files (for example `app/tests/test_data_analysis_recipe_info.py`, `libs/utils/tests/test_recipe_check.py`).
Docs and rule files (text search; the script does not edit them)
- `docs/appendix/data_analysis_recipe_structure.yaml:56`, `:85` (`ui_title`), `docs/appendix/viz_factory_components.qmd:125`, `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:302`, `docs/foundations/data_contracts_adr.qmd:24` (`info.label` is the only required key), `docs/workflows/connector.qmd:84`, `:255`, `docs/deployment/deployment_guide.qmd:39`, `:63`, `:92` (`deployment_name`), `docs/reference/environment_variables.qmd:167` (banner `title`, `subtitle`), 21 lines `label:` in `docs/` (six files).
- `.claude/rules/rules_data_analysis_recipe_structure.md:168`, `:181` (`ui_title`), `.claude/design/recipe_format_spec.md:77`, `:179` (DEC52), `:485`, `:498`, `:718`, `:751`, `:793-794`, `config/deployment/README.md`, `config/deployment/templates/deployment_template.yaml:23`, `:46`, `config/data_analysis_recipes/README.md`. Ledger and ADR text: not rewritten (D-0459; whether an ADR is updated is not settled).
- The comment that names old banner keys, found by the script: `config/deployment/templates/deployment_template.yaml:46`.

## Contradictions and gaps between the ledger lines (listed, nothing decided)

1. (Settled by D-0470: the name is optional, an advice.) D-0408 says the check I01 ("label required") "goes"; D-0410 says it "becomes the check for `info.ui_label`". The re-check shows the first was on her screen, the second added by the relay (row 11). Open case OC01. No shipped recipe lacks a name today (0 places), so the script meets no recipe without a name; the answer decides the checker.
2. (Settled by D-0468: they become `ui_label`.) D-0407 says "every display key carries the prefix `ui_` in every file kind"; `recipe_spec.yaml:8-17` still marks the `label` of tables, joins and input fields PENDING and D-0407 does not list them among the not-decided points. 350 places depend on the reading (OC08).
3. (Settled by D-0469: the format stays 1.) D-0236 says "Format 1 is amended before its first release; no format 2", and its date is 2026-11-17. D-0407 leaves "the format version" not decided for this pass, and D-0407 asks that old keys be "refused with the new name". Whether a second amendment of format 1 is allowed or this is format 2 is not stated (OC03; 122 master recipes say `spec_version: 1`).
4. D-0409 removes `ui_title` and says ui_label is kept short; 25 plot entries carry a longer `ui_title` text (listed with its text in the report, section NOTE-TEXT). Nothing says where that text goes (the labs title of the picture, `description`, or nowhere). The old migration of 2026-11-18 wrote some of these texts BECAUSE a `title:` was moved (`engine_keys_migration.py:599-610`).
5. D-0411 (4) removes `deployment_name`, and (1) says a banner is hidden by an empty `ui_label`. `web-demo` has an empty banner title: after the pass it has no name anywhere. Five other deployment files have a name and no banner (OC06).
6. D-0408 and D-0410 make `info` a free block, but the HOME banner also shows `info.subtitle` under the title (`home_theater.py:1146-1148`); no ledger line decides it (OC09, 2 recipes: `1_test_data_ST22_dummy`, `3_test_no_joins`).
7. D-0405 (the Gallery `info.label` and the plot's `ui_label` may differ) names a key that D-0410 renamed; the Gallery question Q8 (what the generator writes in `info`) stays open (OC05: 34 bundles with `info.label`, `description`, `submission_date`).
8. D-0411 says the deployments with customization "must still work" and the proof is a test that can fail. Such tests already exist on `dev` (`app/tests/test_deployment_branding.py` and others, recording today's values); the plan text says no test checks the banner today. They assert `b.deployment_name` (lines 58, 81, 91), which D-0411 (4) removes.
9. `.claude/tasks/tasks.md` says 5 shipped recipes have a plot `ui_title`; I count 25 plot entries in 5 recipe files.

## Not verified

- The list of tests is by text search, not read file by file; the docs list is by text search of `ui_title`, `deployment_name`, `info.label`, `banner` and `logo_url`, so a YAML example in a `.qmd` that writes `info:` and then `label:` on the next line is only counted (21 lines), not placed.
- The count of registry `label` keys (890 places in 22 files of `libs/*/src`, 814 of them in `viz_factory`) is a text match, not a parse.
- The load gate was not run on a started app; the browser tests of the two customized deployments were not run.
- Two short test runs (2 to 3 seconds each) started while the machine load was 13 to 15, above the limit of 10: the tests are tiny and the run was not repeated at lower load.

---

10. D-0471 says the four points "rest on" D-0312, D-0407 and D-0411 and that "no objection" is not a decision; a rule built on it (old sessions refused) rests on D-0312, which is a decision.
11. The task text and the ledger say "the app features `ui_title` is removed"; D-0470 keeps ONE switch, and D-0472 puts it in the deployment file. The HOME banner today reads the app features `ui_title` (`home_theater.py:1137-1158`): until the reader of `branding.show_recipe_name` is built, the removal would make the switch vanish.
12. D-0474 is cited in the script as "to be written": the ledger has no such line yet.

## Not verified

- The list of tests is by text search, not read file by file; the docs list is by text search of `ui_title`, `deployment_name`, `info.label`, `banner` and `logo_url`, so a YAML example in a `.qmd` that writes `info:` and then `label:` on the next line is only counted (21 lines), not placed.
- The count of registry `label` keys (890 places in 22 files, 814 of them in `viz_factory`) is a text match, not a parse.
- The load gate was not run on a started app; the browser tests of the two customized deployments were not run.
- Several short test runs of my own test file (2 to 4 seconds each) started while the machine load was above 10 (12 to 46, others were running); they were not repeated at lower load.

---

# The list the script printed (markdown, `--report`)

# Names pass: dry run report (DRY RUN: nothing is written. Root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ_wt_names_dryrun)

## Summary
496 change(s) in 175 file(s); 16 listed place(s) in 5 open case(s); 0 conflict(s); 0 change(s) the script cannot place; 0 recipe(s) would get the advice (no name).

| kind of file | files read | changes |
|---|---:|---:|
| recipes | 101 | 211 |
| recipe templates | 9 | 40 |
| Gallery bundles | 34 | 68 |
| test fixtures | 113 | 171 |
| deployment files | 5 | 6 |
| deployment templates | 2 | 0 |
| app features files | 8 | 0 |

by rule: R01 label->ui_label (D-0410) x122, R02 name->ui_label (D-0410) x0, R03 ui_title->ui_label (D-0410) x0, R04 ui_title->REMOVED (D-0409) x0, R05 ui_title->REMOVED (D-0409) x25, R06 title->ui_label (D-0411) x2, R07 subtitle->description (D-0411) x2, R08 deployment_name->REMOVED (D-0411) x2, R09 ui_title->REMOVED (D-0411) x0, R10 label->ui_label (D-0468) x85, R11 label->ui_label (D-0468) x39, R12 label->ui_label (D-0468) x219, R14 ui_title.visible: false->branding.show_recipe_name: false (D-0474 (to be written)) x0

## Changes the dry run would make

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**assets/gallery_data/area_simple/data_analysis_recipe.yaml**
- assets/gallery_data/area_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/area_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_grouped/data_analysis_recipe.yaml**
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml**
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_simple/data_analysis_recipe.yaml**
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml**
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml**
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bubble/data_analysis_recipe.yaml**
- assets/gallery_data/bubble/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bubble/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/connected_scatter/data_analysis_recipe.yaml**
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml**
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/density_simple/data_analysis_recipe.yaml**
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/dumbbell/data_analysis_recipe.yaml**
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/ecdf/data_analysis_recipe.yaml**
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/error_bar/data_analysis_recipe.yaml**
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/freqpoly/data_analysis_recipe.yaml**
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml**
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/histogram_simple/data_analysis_recipe.yaml**
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/jitter_strip/data_analysis_recipe.yaml**
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/line_grouped/data_analysis_recipe.yaml**
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/line_simple/data_analysis_recipe.yaml**
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml**
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/point_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/point_simple/data_analysis_recipe.yaml**
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/proportion_bar/data_analysis_recipe.yaml**
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/qq_plot/data_analysis_recipe.yaml**
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml**
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml**
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/stacked_area/data_analysis_recipe.yaml**
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/stacked_bar/data_analysis_recipe.yaml**
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/step_chart/data_analysis_recipe.yaml**
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/tile_simple/data_analysis_recipe.yaml**
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml**
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_simple/data_analysis_recipe.yaml**
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml**
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:4: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:8: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:12: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:16: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml**
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:20: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:30: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:44: R10 additional_datasets_schemas.VirulenceFinder.label -> additional_datasets_schemas.VirulenceFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:54: R10 additional_datasets_schemas.APEC_STEC_virulence_genes.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:67: R11 joins.AR1_MLST_Serotype_Virulence.label -> joins.AR1_MLST_Serotype_Virulence.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:18: R10 data_schemas.Summary.label -> data_schemas.Summary.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:29: R10 data_schemas.Summary_quality.label -> data_schemas.Summary_quality.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:43: R10 data_schemas.Quality_metrics.label -> data_schemas.Quality_metrics.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:54: R10 data_schemas.Detailed_summary.label -> data_schemas.Detailed_summary.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:66: R10 data_schemas.FastP.label -> data_schemas.FastP.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:77: R10 data_schemas.Quast.label -> data_schemas.Quast.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:88: R10 data_schemas.Bracken.label -> data_schemas.Bracken.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:99: R10 data_schemas.ResFinder.label -> data_schemas.ResFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:111: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:124: R10 additional_datasets_schemas.VirulenceFinder.label -> additional_datasets_schemas.VirulenceFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:135: R10 additional_datasets_schemas.APEC_STEC_virulence_genes.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:150: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:165: R11 joins.FastP_with_metadata.label -> joins.FastP_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:173: R11 joins.Quast_with_metadata.label -> joins.Quast_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:181: R11 joins.Bracken_with_metadata.label -> joins.Bracken_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:189: R11 joins.ResFinder_with_metadata.label -> joins.ResFinder_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:197: R11 joins.MLST_with_metadata.label -> joins.MLST_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:206: R11 joins.QC_Reads_Anchor.label -> joins.QC_Reads_Anchor.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:216: R11 joins.Summary_phenotype_length_fragmentation.label -> joins.Summary_phenotype_length_fragmentation.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:224: R11 joins.ST22_Anchor.label -> joins.ST22_Anchor.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:238: R11 joins.AR1_MLST_Serotype_Virulence.label -> joins.AR1_MLST_Serotype_Virulence.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:250: R11 joins.QA_AMR_per_sample.label -> joins.QA_AMR_per_sample.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:259: R11 joins.QA_ST_with_NA.label -> joins.QA_ST_with_NA.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:266: R11 joins.QA_year_types.label -> joins.QA_year_types.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:273: R11 joins.QA_L50_integer.label -> joins.QA_L50_integer.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:280: R11 joins.QA_fanout_exhibit.label -> joins.QA_fanout_exhibit.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:290: R11 joins.QA_aggregated_no_key.label -> joins.QA_aggregated_no_key.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:298: R11 joins.QA_population_zscore.label -> joins.QA_population_zscore.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:4: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:8: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:12: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:16: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:4: R12 data_schemas.Bracken.input_fields.sample_id.label -> data_schemas.Bracken.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:9: R12 data_schemas.Bracken.input_fields.taxon_1.label -> data_schemas.Bracken.input_fields.taxon_1.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:13: R12 data_schemas.Bracken.input_fields.proportion_1.label -> data_schemas.Bracken.input_fields.proportion_1.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:4: R12 data_schemas.Detailed_summary.input_fields.sample_id.label -> data_schemas.Detailed_summary.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:10: R12 data_schemas.Detailed_summary.input_fields.data.label -> data_schemas.Detailed_summary.input_fields.data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:14: R12 data_schemas.Detailed_summary.input_fields.data_type.label -> data_schemas.Detailed_summary.input_fields.data_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:18: R12 data_schemas.Detailed_summary.input_fields.predicted_phenotype.label -> data_schemas.Detailed_summary.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:22: R12 data_schemas.Detailed_summary.input_fields.cge_predicted_phenotype.label -> data_schemas.Detailed_summary.input_fields.cge_predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:26: R12 data_schemas.Detailed_summary.input_fields.identity.label -> data_schemas.Detailed_summary.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:30: R12 data_schemas.Detailed_summary.input_fields.overlap.label -> data_schemas.Detailed_summary.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:34: R12 data_schemas.Detailed_summary.input_fields.hsp_lengthtotal_length.label -> data_schemas.Detailed_summary.input_fields.hsp_lengthtotal_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:38: R12 data_schemas.Detailed_summary.input_fields.contig.label -> data_schemas.Detailed_summary.input_fields.contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:42: R12 data_schemas.Detailed_summary.input_fields.start.label -> data_schemas.Detailed_summary.input_fields.start.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:46: R12 data_schemas.Detailed_summary.input_fields.end.label -> data_schemas.Detailed_summary.input_fields.end.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:50: R12 data_schemas.Detailed_summary.input_fields.accession.label -> data_schemas.Detailed_summary.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:4: R12 data_schemas.FastP.input_fields.sample_id.label -> data_schemas.FastP.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:9: R12 data_schemas.FastP.input_fields.total_reads.label -> data_schemas.FastP.input_fields.total_reads.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:13: R12 data_schemas.FastP.input_fields.q30_rate.label -> data_schemas.FastP.input_fields.q30_rate.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:17: R12 data_schemas.FastP.input_fields.gc_content.label -> data_schemas.FastP.input_fields.gc_content.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:4: R12 data_schemas.MLST.input_fields.sample_id.label -> data_schemas.MLST.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:10: R12 data_schemas.MLST.input_fields.scheme.label -> data_schemas.MLST.input_fields.scheme.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:15: R12 data_schemas.MLST.input_fields.sequence_type.label -> data_schemas.MLST.input_fields.sequence_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:20: R12 data_schemas.MLST.input_fields.locus_1.label -> data_schemas.MLST.input_fields.locus_1.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:25: R12 data_schemas.MLST.input_fields.locus_2.label -> data_schemas.MLST.input_fields.locus_2.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:29: R12 data_schemas.MLST.input_fields.locus_3.label -> data_schemas.MLST.input_fields.locus_3.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:34: R12 data_schemas.MLST.input_fields.locus_4.label -> data_schemas.MLST.input_fields.locus_4.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:38: R12 data_schemas.MLST.input_fields.locus_5.label -> data_schemas.MLST.input_fields.locus_5.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:43: R12 data_schemas.MLST.input_fields.locus_6.label -> data_schemas.MLST.input_fields.locus_6.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:48: R12 data_schemas.MLST.input_fields.locus_7.label -> data_schemas.MLST.input_fields.locus_7.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:4: R12 data_schemas.Quality_metrics.input_fields.sample_id.label -> data_schemas.Quality_metrics.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:9: R12 data_schemas.Quality_metrics.input_fields.quality_module.label -> data_schemas.Quality_metrics.input_fields.quality_module.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:13: R12 data_schemas.Quality_metrics.input_fields.quality_feedback.label -> data_schemas.Quality_metrics.input_fields.quality_feedback.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:17: R12 data_schemas.Quality_metrics.input_fields.total_reads_after.label -> data_schemas.Quality_metrics.input_fields.total_reads_after.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:21: R12 data_schemas.Quality_metrics.input_fields.ratio_reads_after.label -> data_schemas.Quality_metrics.input_fields.ratio_reads_after.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:25: R12 data_schemas.Quality_metrics.input_fields.bracken_main_taxon.label -> data_schemas.Quality_metrics.input_fields.bracken_main_taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:29: R12 data_schemas.Quality_metrics.input_fields.proportion_of_main_taxon.label -> data_schemas.Quality_metrics.input_fields.proportion_of_main_taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:33: R12 data_schemas.Quality_metrics.input_fields.reads_gc_content.label -> data_schemas.Quality_metrics.input_fields.reads_gc_content.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:37: R12 data_schemas.Quality_metrics.input_fields.n50.label -> data_schemas.Quality_metrics.input_fields.n50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:41: R12 data_schemas.Quality_metrics.input_fields.total_length.label -> data_schemas.Quality_metrics.input_fields.total_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:45: R12 data_schemas.Quality_metrics.input_fields.largest_contig.label -> data_schemas.Quality_metrics.input_fields.largest_contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:49: R12 data_schemas.Quality_metrics.input_fields.num_contigs_500bp.label -> data_schemas.Quality_metrics.input_fields.num_contigs_500bp.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:53: R12 data_schemas.Quality_metrics.input_fields.num_contigs_0bp.label -> data_schemas.Quality_metrics.input_fields.num_contigs_0bp.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:4: R12 data_schemas.Quast.input_fields.sample_id.label -> data_schemas.Quast.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:9: R12 data_schemas.Quast.input_fields.n50.label -> data_schemas.Quast.input_fields.n50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:13: R12 data_schemas.Quast.input_fields.total_length.label -> data_schemas.Quast.input_fields.total_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:17: R12 data_schemas.Quast.input_fields.largest_contig.label -> data_schemas.Quast.input_fields.largest_contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:21: R12 data_schemas.Quast.input_fields.L50.label -> data_schemas.Quast.input_fields.L50.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:4: R12 data_schemas.ResFinder.input_fields.sample_id.label -> data_schemas.ResFinder.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:9: R12 data_schemas.ResFinder.input_fields.gene.label -> data_schemas.ResFinder.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:13: R12 data_schemas.ResFinder.input_fields.predicted_phenotype.label -> data_schemas.ResFinder.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:17: R12 data_schemas.ResFinder.input_fields.identity.label -> data_schemas.ResFinder.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:21: R12 data_schemas.ResFinder.input_fields.overlap.label -> data_schemas.ResFinder.input_fields.overlap.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:7: R12 data_schemas.Summary.input_fields.sample_id.label -> data_schemas.Summary.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:12: R12 data_schemas.Summary.input_fields.quality_module.label -> data_schemas.Summary.input_fields.quality_module.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:21: R12 data_schemas.Summary.input_fields.taxon.label -> data_schemas.Summary.input_fields.taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:59: R12 data_schemas.Summary.input_fields.ST.label -> data_schemas.Summary.input_fields.ST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:64: R12 data_schemas.Summary.input_fields.genome_length.label -> data_schemas.Summary.input_fields.genome_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:70: R12 data_schemas.Summary.input_fields.N50.label -> data_schemas.Summary.input_fields.N50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:75: R12 data_schemas.Summary.input_fields.contigs_sup300bp.label -> data_schemas.Summary.input_fields.contigs_sup300bp.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:4: R12 additional_datasets_schemas.VirulenceFinder.input_fields.sample_id.label -> additional_datasets_schemas.VirulenceFinder.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:9: R12 additional_datasets_schemas.VirulenceFinder.input_fields.serotype.label -> additional_datasets_schemas.VirulenceFinder.input_fields.serotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:13: R12 additional_datasets_schemas.VirulenceFinder.input_fields.virulence_raw.label -> additional_datasets_schemas.VirulenceFinder.input_fields.virulence_raw.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:5: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:10: R12 metadata_schema.input_fields.source.label -> metadata_schema.input_fields.source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:14: R12 metadata_schema.input_fields.year.label -> metadata_schema.input_fields.year.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:18: R12 metadata_schema.input_fields.country.label -> metadata_schema.input_fields.country.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml:2: R05 analysis_groups.Quality Control.plots.qc_reads_horizontal_barplot.ui_title REMOVED (value: Reads Quality & Taxonomy Proportion)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml:2: R05 analysis_groups.Results.plots.mlst_bar.ui_title REMOVED (value: MLST Sequence Type Distribution by Country)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml:2: R05 analysis_groups.Quality Control.plots.assembly_quality_dotplot.ui_title REMOVED (value: Assembly Quality Metrics (Quast))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:2: R05 analysis_groups.Results.plots.amr_heatmap.ui_title REMOVED (value: AMR Genes Presence by Category)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:2: R05 analysis_groups.Results.plots.virulence_bar.ui_title REMOVED (value: Selected Virulence Genes Count)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml:2: R05 analysis_groups.Results.plots.virulence_variants.ui_title REMOVED (value: Integrated Virulence & MLST Typing)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml:2: R05 analysis_groups.Cat 🐱.plots.miaou.ui_title REMOVED (value: 🐱 Miaou — Assembly Metric Distributions by Source)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml:2: R05 analysis_groups.Curiosity.plots.phenotype_genome_length_fragmentation.ui_title REMOVED (value: Phenotype Score correlation with Assembly Metrics)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_aggregated_no_key.ui_title REMOVED (value: QA: samples per country and year (aggregated, no sample_id))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_amr_genes_per_sample.ui_title REMOVED (value: QA: AMR genes per sample)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_facet_by_mapping.ui_title REMOVED (value: QA: facet_by written in mapping)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_fanout_rows_per_sample.ui_title REMOVED (value: QA EXHIBIT: rows per sample after joining two long tables)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_l50_integer.ui_title REMOVED (value: QA: samples per L50 (integer column))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_population_zscore.ui_title REMOVED (value: QA: N50 z-score per sample (depends on all samples))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_sequence_type_missing.ui_title REMOVED (value: QA: samples per sequence type)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_year_label.ui_title REMOVED (value: QA: samples per year (text label))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml:2: R05 analysis_groups.Results.plots.year_distribution.ui_title REMOVED (value: Sample Count by Year (T1 = all years, T2 = 2023–2025 only))  [D-0409]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:18: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:23: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:35: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:45: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:57: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:64: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/3_test_no_joins.yaml**
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:20: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/demo_abromics.yaml**
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:12: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:22: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:36: R11 joins.demo_join.label -> joins.demo_join.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:23: R10 data_schemas.fg_metadata.label -> data_schemas.fg_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:34: R10 data_schemas.fg_phenotypes.label -> data_schemas.fg_phenotypes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:45: R10 data_schemas.fg_genotypes.label -> data_schemas.fg_genotypes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:58: R11 joins.figshare_triple_join.label -> joins.figshare_triple_join.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:4: R12 data_schemas.fg_genotypes.input_fields.host_animal_common.label -> data_schemas.fg_genotypes.input_fields.host_animal_common.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:8: R12 data_schemas.fg_genotypes.input_fields.sample_id.label -> data_schemas.fg_genotypes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:12: R12 data_schemas.fg_genotypes.input_fields.gene.label -> data_schemas.fg_genotypes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:16: R12 data_schemas.fg_genotypes.input_fields.gene_type.label -> data_schemas.fg_genotypes.input_fields.gene_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:21: R12 data_schemas.fg_genotypes.input_fields.gene_identifier.label -> data_schemas.fg_genotypes.input_fields.gene_identifier.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:26: R12 data_schemas.fg_genotypes.input_fields.gene_name_family.label -> data_schemas.fg_genotypes.input_fields.gene_name_family.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:31: R12 data_schemas.fg_genotypes.input_fields.resistance_class.label -> data_schemas.fg_genotypes.input_fields.resistance_class.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:4: R12 data_schemas.fg_metadata.input_fields.sample_id.label -> data_schemas.fg_metadata.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:8: R12 data_schemas.fg_metadata.input_fields.host_animal_species.label -> data_schemas.fg_metadata.input_fields.host_animal_species.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:12: R12 data_schemas.fg_metadata.input_fields.host_animal_common.label -> data_schemas.fg_metadata.input_fields.host_animal_common.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:16: R12 data_schemas.fg_metadata.input_fields.specimen_source_tissue.label -> data_schemas.fg_metadata.input_fields.specimen_source_tissue.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:21: R12 data_schemas.fg_metadata.input_fields.final_diagnosis.label -> data_schemas.fg_metadata.input_fields.final_diagnosis.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:25: R12 data_schemas.fg_metadata.input_fields.animal_infection_site_uti.label -> data_schemas.fg_metadata.input_fields.animal_infection_site_uti.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:4: R12 data_schemas.fg_phenotypes.input_fields.sample_id.label -> data_schemas.fg_phenotypes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:8: R12 data_schemas.fg_phenotypes.input_fields.mic_id.label -> data_schemas.fg_phenotypes.input_fields.mic_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:14: R12 data_schemas.fg_phenotypes.input_fields.breakpoint.label -> data_schemas.fg_phenotypes.input_fields.breakpoint.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:20: R12 data_schemas.fg_phenotypes.input_fields.predicted_phenotype.label -> data_schemas.fg_phenotypes.input_fields.predicted_phenotype.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_a_phenotype_bar.ui_title REMOVED (value: Phenotypic Resistance per Antibiotic)  [D-0409]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_b_genotype_bar.ui_title REMOVED (value: Resistance Gene Families by Host)  [D-0409]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_c_resistance_class.ui_title REMOVED (value: Resistance Class by Host Animal)  [D-0409]

**config/data_analysis_recipes/pipelines/stress_test_master.yaml**
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:12: R10 data_schemas.Stress_Source.label -> data_schemas.Stress_Source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:23: R11 joins.Master_Collection.label -> joins.Master_Collection.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml**
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:5: R12 data_schemas.Stress_Source.input_fields.id.label -> data_schemas.Stress_Source.input_fields.id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:9: R12 data_schemas.Stress_Source.input_fields.species.label -> data_schemas.Stress_Source.input_fields.species.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:13: R12 data_schemas.Stress_Source.input_fields.amr_class.label -> data_schemas.Stress_Source.input_fields.amr_class.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:17: R12 data_schemas.Stress_Source.input_fields.collection_date.label -> data_schemas.Stress_Source.input_fields.collection_date.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:21: R12 data_schemas.Stress_Source.input_fields.value.label -> data_schemas.Stress_Source.input_fields.value.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_bad_select_column.yaml**
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:16: R10 data_schemas.Genes.label -> data_schemas.Genes.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:23: R12 data_schemas.Genes.input_fields.sample_id.label -> data_schemas.Genes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:24: R12 data_schemas.Genes.input_fields.gene.label -> data_schemas.Genes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:25: R12 data_schemas.Genes.input_fields.predicted_phenotype.label -> data_schemas.Genes.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:35: R11 joins.Genes_joined.label -> joins.Genes_joined.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_broken_header.yaml**
- config/data_analysis_recipes/retest/retest_broken_header.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:16: R10 data_schemas.Genes.label -> data_schemas.Genes.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:23: R12 data_schemas.Genes.input_fields.sample_id.label -> data_schemas.Genes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:24: R12 data_schemas.Genes.input_fields.gene.label -> data_schemas.Genes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:25: R12 data_schemas.Genes.input_fields.predicted_phenotype.label -> data_schemas.Genes.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:33: R11 joins.Genes_joined.label -> joins.Genes_joined.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_tier2.yaml**
- config/data_analysis_recipes/retest/retest_tier2.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_tier2.yaml:16: R10 data_schemas.Samples.label -> data_schemas.Samples.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:23: R12 data_schemas.Samples.input_fields.sample_id.label -> data_schemas.Samples.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:24: R12 data_schemas.Samples.input_fields.group.label -> data_schemas.Samples.input_fields.group.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:25: R12 data_schemas.Samples.input_fields.value.label -> data_schemas.Samples.input_fields.value.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:26: R12 data_schemas.Samples.input_fields.year.label -> data_schemas.Samples.input_fields.year.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:34: R11 joins.Result.label -> joins.Result.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:47: R11 joins.All_samples.label -> joins.All_samples.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_top_n_other.yaml**
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:16: R10 data_schemas.Variants.label -> data_schemas.Variants.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:23: R12 data_schemas.Variants.input_fields.sample_id.label -> data_schemas.Variants.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:24: R12 data_schemas.Variants.input_fields.variant.label -> data_schemas.Variants.input_fields.variant.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:38: R11 joins.Variants_joined.label -> joins.Variants_joined.ui_label  [D-0468]

**config/data_analysis_recipes/templates/audit.yaml**
- config/data_analysis_recipes/templates/audit.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/audit.yaml:13: R10 data_schemas.submission_logs.label -> data_schemas.submission_logs.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:26: R12 data_schemas.submission_logs.input_fields.lab_id.label -> data_schemas.submission_logs.input_fields.lab_id.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:30: R12 data_schemas.submission_logs.input_fields.submission_date.label -> data_schemas.submission_logs.input_fields.submission_date.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:34: R12 data_schemas.submission_logs.input_fields.status.label -> data_schemas.submission_logs.input_fields.status.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:38: R12 data_schemas.submission_logs.input_fields.turnaround_time.label -> data_schemas.submission_logs.input_fields.turnaround_time.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:51: R05 analysis_groups.Performance.plots.tat_distribution.ui_title REMOVED (value: Turnaround Time by Laboratory)  [D-0409]
- config/data_analysis_recipes/templates/audit.yaml:71: R05 analysis_groups.Volumes.plots.submission_status.ui_title REMOVED (value: Submissions by Current Status)  [D-0409]

**config/data_analysis_recipes/templates/complex_template.yaml**
- config/data_analysis_recipes/templates/complex_template.yaml:9: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/complex_template.yaml:15: R10 data_schemas.genomics.label -> data_schemas.genomics.ui_label  [D-0468]
- config/data_analysis_recipes/templates/complex_template.yaml:27: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/complex_template.yaml:40: R11 joins.master_assembly.label -> joins.master_assembly.ui_label  [D-0468]

**config/data_analysis_recipes/templates/e_coli.yaml**
- config/data_analysis_recipes/templates/e_coli.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/e_coli.yaml:12: R10 data_schemas.amr_results.label -> data_schemas.amr_results.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:25: R12 data_schemas.amr_results.input_fields.sample_id.label -> data_schemas.amr_results.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:29: R12 data_schemas.amr_results.input_fields.serotype.label -> data_schemas.amr_results.input_fields.serotype.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:33: R12 data_schemas.amr_results.input_fields.sequence_type.label -> data_schemas.amr_results.input_fields.sequence_type.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:37: R12 data_schemas.amr_results.input_fields.ctx_m_gene.label -> data_schemas.amr_results.input_fields.ctx_m_gene.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:41: R12 data_schemas.amr_results.input_fields.growth_rate.label -> data_schemas.amr_results.input_fields.growth_rate.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:46: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:62: R12 metadata_schema.input_fields.collection_date.label -> metadata_schema.input_fields.collection_date.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:66: R12 metadata_schema.input_fields.country_of_origin.label -> metadata_schema.input_fields.country_of_origin.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:70: R12 metadata_schema.input_fields.hospital_site.label -> metadata_schema.input_fields.hospital_site.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:74: R12 metadata_schema.input_fields.patient_age.label -> metadata_schema.input_fields.patient_age.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:78: R12 metadata_schema.input_fields.patient_outcome.label -> metadata_schema.input_fields.patient_outcome.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:83: R11 joins.amr_with_metadata.label -> joins.amr_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:104: R05 analysis_groups.AMR.plots.serotype_dist.ui_title REMOVED (value: Serotype Distribution by Country)  [D-0409]
- config/data_analysis_recipes/templates/e_coli.yaml:119: R05 analysis_groups.AMR.plots.growth_rate_by_st.ui_title REMOVED (value: Growth Rate by Sequence Type)  [D-0409]

**config/data_analysis_recipes/templates/left_join_lesson.yaml**
- config/data_analysis_recipes/templates/left_join_lesson.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:22: R10 data_schemas.sequenced.label -> data_schemas.sequenced.ui_label  [D-0468]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:41: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:61: R11 joins.lesson_assembly.label -> joins.lesson_assembly.ui_label  [D-0468]

**config/data_analysis_recipes/templates/simple_template.yaml**
- config/data_analysis_recipes/templates/simple_template.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/simple_template.yaml:12: R10 data_schemas.primary_data.label -> data_schemas.primary_data.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:28: R12 data_schemas.primary_data.input_fields.value.label -> data_schemas.primary_data.input_fields.value.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:32: R12 data_schemas.primary_data.input_fields.group.label -> data_schemas.primary_data.input_fields.group.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:37: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:53: R12 metadata_schema.input_fields.category.label -> metadata_schema.input_fields.category.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:58: R11 joins.main_collection.label -> joins.main_collection.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:80: R05 analysis_groups.Overview.plots.value_by_group.ui_title REMOVED (value: Measurement Values by Group)  [D-0409]

**config/deployment/demo/demo-vetinst.yaml**
- config/deployment/demo/demo-vetinst.yaml:5: R08 deployment_name REMOVED (value: SPARMVET demo (demo-vetinst))  [D-0411]
- config/deployment/demo/demo-vetinst.yaml:21: R06 branding.banner.title -> branding.banner.ui_label  [D-0411]
- config/deployment/demo/demo-vetinst.yaml:22: R07 branding.banner.subtitle -> branding.banner.description  [D-0411]

**config/deployment/demo/web-demo.yaml**
- config/deployment/demo/web-demo.yaml:5: R08 deployment_name REMOVED (value: SPARMVET demo (web-demo))  [D-0411]
- config/deployment/demo/web-demo.yaml:21: R06 branding.banner.title -> branding.banner.ui_label  [D-0411]
- config/deployment/demo/web-demo.yaml:22: R07 branding.banner.subtitle -> branding.banner.description  [D-0411]

**libs/transformer/tests/data/modif_filter_data_analysis_recipe.yaml**
- libs/transformer/tests/data/modif_filter_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml**
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:21: R12 data_schemas.modif_join_where.input_fields.id.label -> data_schemas.modif_join_where.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:24: R12 data_schemas.modif_join_where.input_fields.lo.label -> data_schemas.modif_join_where.input_fields.lo.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:27: R12 data_schemas.modif_join_where.input_fields.hi.label -> data_schemas.modif_join_where.input_fields.hi.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:41: R12 data_schemas.modif_join_where_right.input_fields.rid.label -> data_schemas.modif_join_where_right.input_fields.rid.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:44: R12 data_schemas.modif_join_where_right.input_fields.v.label -> data_schemas.modif_join_where_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_all_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_all_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_any_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_any_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_bottom_k_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_bottom_k_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_coalesce_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_coalesce_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cum_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cum_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cum_sum_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cum_sum_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_describe_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_describe_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_nans_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_nans_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_nulls_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_nulls_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_dt_truncate_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_dt_truncate_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_explode_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_explode_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_fill_nan_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_fill_nan_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_fill_null_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_fill_null_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_first_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_first_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_gather_every_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_gather_every_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_group_by_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_group_by_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_group_by_dynamic_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_group_by_dynamic_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_head_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_head_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_interpolate_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_interpolate_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:21: R12 data_schemas.polars_join_asof.input_fields.id.label -> data_schemas.polars_join_asof.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:24: R12 data_schemas.polars_join_asof.input_fields.site.label -> data_schemas.polars_join_asof.input_fields.site.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:27: R12 data_schemas.polars_join_asof.input_fields.t.label -> data_schemas.polars_join_asof.input_fields.t.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:30: R12 data_schemas.polars_join_asof.input_fields.x.label -> data_schemas.polars_join_asof.input_fields.x.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:44: R12 data_schemas.polars_join_asof_right.input_fields.site.label -> data_schemas.polars_join_asof_right.input_fields.site.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:47: R12 data_schemas.polars_join_asof_right.input_fields.t.label -> data_schemas.polars_join_asof_right.input_fields.t.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:50: R12 data_schemas.polars_join_asof_right.input_fields.v.label -> data_schemas.polars_join_asof_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:21: R12 data_schemas.polars_join.input_fields.id.label -> data_schemas.polars_join.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:24: R12 data_schemas.polars_join.input_fields.g.label -> data_schemas.polars_join.input_fields.g.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:27: R12 data_schemas.polars_join.input_fields.n.label -> data_schemas.polars_join.input_fields.n.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:30: R12 data_schemas.polars_join.input_fields.f.label -> data_schemas.polars_join.input_fields.f.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:33: R12 data_schemas.polars_join.input_fields.s.label -> data_schemas.polars_join.input_fields.s.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:47: R12 data_schemas.polars_join_right.input_fields.id.label -> data_schemas.polars_join_right.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:50: R12 data_schemas.polars_join_right.input_fields.v.label -> data_schemas.polars_join_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_last_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_last_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_limit_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_limit_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_list_join_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_list_join_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_list_slice_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_list_slice_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_max_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_max_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_max_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_max_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_mean_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_mean_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_mean_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_mean_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_median_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_median_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_min_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_min_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_min_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_min_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_null_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_null_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_pivot_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_pivot_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_quantile_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_quantile_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rank_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rank_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_remove_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_remove_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rename_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rename_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_reverse_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_reverse_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rolling_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rolling_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_round_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_round_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sample_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sample_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_select_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_select_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_shift_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_shift_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_slice_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_slice_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sort_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sort_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_std_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_std_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_extract_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_extract_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_replace_all_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_replace_all_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_split_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_split_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_splitn_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_splitn_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_strip_chars_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_strip_chars_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sum_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sum_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sum_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sum_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_tail_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_tail_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_top_k_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_top_k_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unique_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unique_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unnest_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unnest_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unpivot_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unpivot_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_var_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_var_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_with_columns_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_with_columns_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_with_row_index_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_with_row_index_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml**
- libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

## CANNOT BE DECIDED BY THE SCRIPT
(listed, never changed; each line is a place a person or the owner decides)

### OC07: The key `display_name` of app features files -- 8 place(s)
> D-0407: every display key carries the prefix; D-0411 names only the app features key `ui_title`; D-0412: the key lists are not decided.
- config/app_features/demo-vetinst.yaml:5: .display_name: VetInst Demo
- config/app_features/developer.yaml:3: .display_name: Workflow Developer
- config/app_features/pipeline-exploration-advanced.yaml:3: .display_name: Pipeline Exploration - Advanced
- config/app_features/pipeline-exploration-simple.yaml:3: .display_name: Pipeline Exploration - Simple
- config/app_features/pipeline-static.yaml:3: .display_name: Automated Pipeline - Static
- config/app_features/qa.yaml:18: .display_name: QA / Test Harness
- config/app_features/standalone.yaml:5: .display_name: Standalone User (own data)
- config/app_features/web-demo.yaml:5: .display_name: Web Demo

### OC09: Display-like keys that no decision names (for example `info.subtitle`) -- 2 place(s)
> D-0408: `info` is the free information block: every key written is shown. No line renames or removes these keys.
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:8: info.subtitle: E. coli ST22 — AMR & Virulence Research (demo)
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:8: info.subtitle: A single data schema with no joins at all — issue

### OC06: deployment_name with no banner title to take it -- 5 place(s)
> D-0411: `deployment_name` is REMOVED; the banner's `ui_label` is the deployment's name. With no banner title the name would be lost: the key is kept and listed. Give the deployment a banner, or accept that the name goes?
- config/deployment/connect/connect_template.yaml:21: deployment_name "SPARMVET — Production (Posit Connect)" has no banner title to take it; the key is kept
- config/deployment/local/local.yaml:5: deployment_name "SPARMVET_VIZ (Local Dev)" has no banner title to take it; the key is kept
- config/deployment/local/retest.yaml:5: deployment_name "SPARMVET RETEST" has no banner title to take it; the key is kept
- config/deployment/pipeline_test/pipeline_test.yaml:15: deployment_name "SPARMVET_VIZ (Pipeline Test)" has no banner title to take it; the key is kept
- config/deployment/templates/deployment_template.yaml:23: deployment_name "My Pipeline — Institution Name" has no banner title to take it; the key is kept

### OC05: What the Gallery writes in `info`, and where a Gallery description lives -- 0 place(s)
> D-0408: NOT decided: what the Gallery generator writes in `info` (Gallery question Q8). The KEY of a Gallery bundle is renamed like any recipe's (D-0407: `ui_` in every file kind; D-0468: the `label` of recipe files); what `info` is for in an example is open.
- 34 Gallery bundle(s); keys written in their `info`: description x34, label x34, submission_date x34; 34 bundle(s) with an example_meta.md (the guidance text)

### OC10: Comments that name an old key (a person must reword them) -- 1 place(s)
> D-0411: the one pass also covers the documentation and the recipe specification. The script never edits a comment.
- config/deployment/templates/deployment_template.yaml:46: branding.banner: optional {logo_url, title, subtitle} shown in the Deployment info panel.

## Facts to name the recipe banner switch (D-0472)
(per deployment file: its default app features file and the keys of its `branding` block; per app features file: what its `ui_title` sets today. The list of allowed deployment keys does not exist yet: D-0412 asks for it, it comes with the deployment standard; today the only refusal tables are app/modules/renamed_keys.py and the readers app/src/bootloader.py:591, 874, 877-879)
- config/deployment/connect/connect_template.yaml: default_app_features = pipeline-static; branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/demo/demo-vetinst.yaml: default_app_features = demo-vetinst; branding keys: theme_css, banner, contact; banner keys: logo_url, title, subtitle; the banner shows: title 'AMR Surveillance — Overview'; line 'Norwegian Veterinary Institute'; logo 'assets/demo/logo-no.svg'
- config/deployment/demo/web-demo.yaml: default_app_features = web-demo; branding keys: theme_css, banner; banner keys: logo_url, title, subtitle; the banner shows: logo 'assets/demo/logo-no.svg'
- config/deployment/local/local.yaml: default_app_features = developer; branding keys: contact; banner keys: (no banner); the banner shows: no banner
- config/deployment/local/retest.yaml: default_app_features = developer; branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/pipeline_test/pipeline_test.yaml: default_app_features = (none); branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/templates/deployment_template.yaml: default_app_features = pipeline-static; branding keys: contact; banner keys: (no banner); the banner shows: no banner
- config/app_features/demo-vetinst.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/developer.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-exploration-advanced.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-exploration-simple.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-static.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/qa.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/standalone.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/web-demo.yaml: does not set ui_title (the recipe banner is shown)

## WOULD GET THE ADVICE (no recipe name)
(not an error, D-0470: the file name is shown where a name is needed)

## DECIDED, nothing for the script to change (counts only)
(D-0468, D-0469, D-0471)

### OC02: DECIDED, not renamed: the `"label"` strings of the Python code (action forms, registries) -- 0 place(s)
> D-0468: the review session's reading (not her words): the `"label"` strings of the Python code are not recipe keys and are not renamed by this pass. Counted by text match, not a parse.
- 890 place(s) in 22 file(s) write a `"label"` key in libs/*/src (text match; blueprint_arch: 11, test_lab: 6, transformer: 53, utils: 3, viz_factory: 814, viz_gallery: 3)

### OC03: DECIDED: the recipe format number stays 1 -- 0 place(s)
> D-0469 (her words: we are still in development so the same format can stay): the recipe format number stays 1. The count shows the spec_version of every master recipe.
- spec_version found in 1 x122 master recipe(s)

### OC04: DECIDED: old session files are refused, not converted -- 0 place(s)
> D-0471 (the review session's reading, resting on D-0312; no words of hers confirm this point): old session files are refused with a plain line, no conversion. The script lists where a session holds a name key and never touches a session.
- 0 session file(s) found under a `_sessions` folder, 0 with an old name key. The session writer's own `label` is the user's label of the session, not a recipe name (app/modules/session_manager.py).

## Notes on the changes above
(consequences of rules that are applied)

### NOTE-NAME: Note: the text of a removed deployment_name differs from the banner title -- 2 place(s)
> D-0411 (4): the banner's `ui_label` is the deployment's name; the old name text is not kept.
- config/deployment/demo/demo-vetinst.yaml:5: deployment_name "SPARMVET demo (demo-vetinst)" is removed; the banner title is "AMR Surveillance — Overview"
- config/deployment/demo/web-demo.yaml:5: deployment_name "SPARMVET demo (web-demo)" is removed; the banner title is empty (a hidden banner)

### NOTE-TEXT: Note: the text of a removed `ui_title` differs from the `ui_label` -- 25 place(s)
> D-0409: the removed text is kept nowhere (it is printed in the list of changes).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml:2: analysis_groups.Quality Control.plots.qc_reads_horizontal_barplot.ui_title "Reads Quality & Taxonomy Proportion" is removed; ui_label is "QC Reads Horizontal Barplot"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml:2: analysis_groups.Results.plots.mlst_bar.ui_title "MLST Sequence Type Distribution by Country" is removed; ui_label is "MLST Bar"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml:2: analysis_groups.Quality Control.plots.assembly_quality_dotplot.ui_title "Assembly Quality Metrics (Quast)" is removed; ui_label is "Assembly Quality Dotplot"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:2: analysis_groups.Results.plots.amr_heatmap.ui_title "AMR Genes Presence by Category" is removed; ui_label is "AMR Heatmap"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:2: analysis_groups.Results.plots.virulence_bar.ui_title "Selected Virulence Genes Count" is removed; ui_label is "Virulence Bar"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml:2: analysis_groups.Results.plots.virulence_variants.ui_title "Integrated Virulence & MLST Typing" is removed; ui_label is "Virulence Variants"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml:2: analysis_groups.Cat 🐱.plots.miaou.ui_title "🐱 Miaou — Assembly Metric Distributions by Source" is removed; ui_label is "Miaou 🐈"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml:2: analysis_groups.Curiosity.plots.phenotype_genome_length_fragmentation.ui_title "Phenotype Score correlation with Assembly Metrics" is removed; ui_label is "Phenotype Genome Length Fragmentation"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml:2: analysis_groups.QA Canaries.plots.qa_aggregated_no_key.ui_title "QA: samples per country and year (aggregated, no sample_id)" is removed; ui_label is "QA Aggregated No Key"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml:2: analysis_groups.QA Canaries.plots.qa_amr_genes_per_sample.ui_title "QA: AMR genes per sample" is removed; ui_label is "QA AMR Genes Per Sample"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml:2: analysis_groups.QA Canaries.plots.qa_facet_by_mapping.ui_title "QA: facet_by written in mapping" is removed; ui_label is "QA Facet By Mapping"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml:2: analysis_groups.QA Canaries.plots.qa_fanout_rows_per_sample.ui_title "QA EXHIBIT: rows per sample after joining two long tables" is removed; ui_label is "QA Fanout Rows Per Sample"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml:2: analysis_groups.QA Canaries.plots.qa_l50_integer.ui_title "QA: samples per L50 (integer column)" is removed; ui_label is "QA L50 Integer"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml:2: analysis_groups.QA Canaries.plots.qa_population_zscore.ui_title "QA: N50 z-score per sample (depends on all samples)" is removed; ui_label is "QA Population Zscore"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml:2: analysis_groups.QA Canaries.plots.qa_sequence_type_missing.ui_title "QA: samples per sequence type" is removed; ui_label is "QA Sequence Type Missing"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml:2: analysis_groups.QA Canaries.plots.qa_year_label.ui_title "QA: samples per year (text label)" is removed; ui_label is "QA Year Label"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml:2: analysis_groups.Results.plots.year_distribution.ui_title "Sample Count by Year (T1 = all years, T2 = 2023–2025 only)" is removed; ui_label is "Year Distribution"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml:2: analysis_groups.AMR Integration.plots.plot_a_phenotype_bar.ui_title "Phenotypic Resistance per Antibiotic" is removed; ui_label is "Plot A Phenotype Bar"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml:2: analysis_groups.AMR Integration.plots.plot_b_genotype_bar.ui_title "Resistance Gene Families by Host" is removed; ui_label is "Plot B Genotype Bar"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml:2: analysis_groups.AMR Integration.plots.plot_c_resistance_class.ui_title "Resistance Class by Host Animal" is removed; ui_label is "Plot C Resistance Class"
- config/data_analysis_recipes/templates/audit.yaml:51: analysis_groups.Performance.plots.tat_distribution.ui_title "Turnaround Time by Laboratory" is removed; ui_label is "Tat Distribution"
- config/data_analysis_recipes/templates/audit.yaml:71: analysis_groups.Volumes.plots.submission_status.ui_title "Submissions by Current Status" is removed; ui_label is "Submission Status"
- config/data_analysis_recipes/templates/e_coli.yaml:104: analysis_groups.AMR.plots.serotype_dist.ui_title "Serotype Distribution by Country" is removed; ui_label is "Serotype Dist"
- config/data_analysis_recipes/templates/e_coli.yaml:119: analysis_groups.AMR.plots.growth_rate_by_st.ui_title "Growth Rate by Sequence Type" is removed; ui_label is "Growth Rate By ST"
- config/data_analysis_recipes/templates/simple_template.yaml:80: analysis_groups.Overview.plots.value_by_group.ui_title "Measurement Values by Group" is removed; ui_label is "Value By Group"

64 file(s) read but not examined as a recipe (no spec_version, included by no recipe): config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Bracken_Metadata_wrangling.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Bracken_wrangling.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/FastP_Metadata_wrangling.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/FastP_wrangling.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier1.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier2.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml, config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml ...
