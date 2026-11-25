# The names pass and the deployment specification: what can be built without a new answer (scout survey, 2026-11-21 night; filed and shortened by the coordinator)

Rests only on what she decided AND saw (the re-check `tmpAI/coordinator/ledger_words_check/RECHECK_AGAINST_TRANSCRIPT.md`). Read-only; no test run.

## Bottom line
- Nothing that changes the app can be built as a complete step tonight. The names items are ONE migration: the ledger lines say so themselves ("Built with the one pass of D-0407; nothing is built from this decision alone", D-0408 to D-0411). Built alone, each leaves a half state: banners disappear until the recipes are renamed; refusing old keys refuses every shipped recipe; removing the invented names changes every plot with no `ui_label`.
- Buildable tonight, complete, no half state: (1) a test that records what the two customized deployments show today (logo, banner title and line, stylesheet), with no change to the app: it is her own condition ("make sure that the recipe with deployment config with custumization ... work after", D-0411) and no test checks the banner today; (2) a dry run of the renames on a COPY under the scratch folder, nothing applied.
- The deployment pass also is one migration (D-0436: one pass, old location keys refused) and waits.

## A record contradiction to bring to her first
D-0408 says the check "a recipe name is required" GOES. D-0410 says that check BECOMES the check for `info.ui_label`. The re-check shows the first was on her screen and answered; the second was added by the relay (row 11). So: must every recipe have a name in `info.ui_label`, or is it optional, with the file name shown when it is missing?

## The smallest set of answers that unblocks the names migration
1. Must every recipe have a name in `info.ui_label`? (the contradiction above)
2. The internal lists of steps and plot components also use a key `label` (many hundreds of places): renamed to `ui_label` too, or kept as a stated exception?
3. The recipe format number: stays 1 with the old keys refused by name, or becomes 2?
4. Saved sessions that hold an old name key: refused, or converted?
5. What does the Gallery write in a recipe's `info`, and where does a Gallery description live?
6. Customized deployments: is the proposed proof (logo, name, line, stylesheet, contact, HOME shows the recipe name) what she wants, and are the deployment files changed by a script or by hand?
7. A deployment file that still says `deployment_name`: refused at start, or ignored? (the ledger does not say; ignoring would be silent)

## What the migration would touch (counted by search)
- 16 recipe files with an `info` block; 23 recipe files with `ui_title` (17 plots of the demo recipe, 3 of the figshare recipe, 3 templates). The task text says "5 shipped recipes": to recount.
- 7 deployment files with `deployment_name`; 2 with banner keys; 0 app features files set `ui_title`; 8 set `display_name`.
- Code: `libs/utils/src/utils/recipe_spec.yaml`, `recipe_check.py`, `app/handlers/home_theater.py` (the banner chain 1137-1146; invented names at 105, 110, 115), `app/handlers/export_handlers.py:368-373`, `app/src/bootloader.py`, `app/src/ui.py:343-359`, `app/src/server.py:161-162`, `libs/connector/src/connector/base.py:64-66`.
- Tests that assert the old names: 10 files (`test_export_report_names.py`, `test_blueprint_tier_files.py`, `test_no_silent_error.py`, `test_blueprint_plot_open.py`, `test_plot_config_resolver.py`, `test_export_report_texts.py`, `test_home_reads_the_plot_entry.py`, `test_shipped_recipes_hygiene.py`, two in `libs/utils/tests`).
- Docs and rule files: 7 places.
- Migration script patterns exist in `assets/scripts/` (`migrate_recipe_format.py`, `migrate_recipe_engine_keys.py`, `migrate_config_vocabulary.py`); whether they have a dry-run mode was not read.

## The deployment specification
- Can be PREPARED as text only (nothing applied): the rules she decided and saw: the audit folder and its warning (D-0423), the same recipe name in two places (D-0424), selecting data where the default is absent (D-0426), the stop where no selection is possible (D-0427), one copy per person (D-0429, D-0430).
- Waits for her: where the stored tables sit and where the specification lives (row 33); nothing writable; the naming convention as refusal or advice; the upload table; the plain sentence where the default data is absent (row 24); fonts.
- Not in the re-check at all (their shown wording says "to be confirmed"): D-0422, D-0434 to D-0443.

## What I do tonight with this
The before-test of the two customized deployments (no app change). The dry run on a copy waits for answer 1, because a recipe with no name is the first case it meets; the plain renames it would list are counted above.

## Not verified
Whether a migration script has a dry-run mode; the count of the internal `label` keys; where the audit folder is created in code; no test was run.
