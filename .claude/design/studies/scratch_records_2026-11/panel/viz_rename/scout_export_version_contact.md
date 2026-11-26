Read-only report, repo /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ (branch dev). tmp.md not read. Labels: verified (read) = I read the line; reasoned = my inference. Note: the brief I received has no "Decisions" block, so I have no decision numbers to check against; I did read .claude/workflows/agent_principles.md and decision_compliance.md.

1. Version and commit in the bundle: YES, verified (read).
- git commit: export_handlers.py:85-93 runs `git rev-parse --short HEAD`, "n/a" if it fails (reasoned: a containerised run without .git would give "n/a").
- release: export_handlers.py:94-100 runs `git describe --tags --always`, "n/a" on failure.
- software: export_handlers.py:103-109 writes python, polars, shiny, plotnine versions.
- engine_fingerprint: cache_keys.py:70-72 = ENGINE_CACHE_VERSION ("4", cache_keys.py:47) + polars + transformer versions. Not commit-based; it changes only when that constant is bumped or those packages change (verified read). There is no separate "app version" field.
- Also in the provenance dict: containerized, image_ref (env SPARMVET_IMAGE_REF), uv_lock_sha256 (None today, per comment export_handlers.py:171-174), export_handlers.py:201-211.
- Written to:
  * effective_run.yaml, unconditionally: export_handlers.py:1438-1477 (git_commit 1465, release_version 1466, software_versions 1467, engine_fingerprint 1461, containerized 1462, image_ref 1463, uv_lock_sha256 1464).
  * README.txt: export_handlers.py:1984-1988 (Versions, Git commit, Release version), inside the README writer starting at 1933.
  * report.qmd: export_handlers.py:1673-1679 ("## Provenance": Git commit, Release, Software).
  * Plot images: PNG iTXt (export_handlers.py:350-361) and SVG <metadata> (385-396) carry sparmvet:git_commit and created_at only, no engine fields.
- app/assets/report_template.qmd (verified read): front matter params are recipe id, recipe SHA, audit SHA, deployment, timestamp. No commit or version field. I did not verify whether this template is what the live export renders; the provenance section is written in code at export_handlers.py:1673.

2. Contact: recipe contact and deployment contact are NOT written into the bundle (verified: grep for "contact" in export_handlers.py finds no match; bundle_importer.py does not read contact).
- resolve_contact: data_analysis_recipe_validator.py:428-435 returns info.contact, else the deployment contact, else None.
- Its only call is bootloader.py:404 (verified read), which stores the result as "contact" in rejected_data_analysis_recipes (bootloader.py:424, 485).
- On screen only: home_theater.py:883 via rejected_recipe_text (data_analysis_recipe_validator.py:438-448, "Contact: ..."), and recipe_gate_handlers.py:101.
- Deployment contact = bootloader.py:497-499 (branding.contact of deployment config).
- Reasoned: the Mode 2 recipe copy (export_handlers.py:1379-1385) is dumped from cfg.raw_config, so info.contact may sit inside data_analysis_recipes_reproducibility/. Not verified.

3. Import (bundle_importer.py, verified read):
- Legs in _verify, bundle_importer.py:119-195: data (hash of carried data files, :128-134); engine (engine_fingerprint and git_commit against the bundle, :136-154); recipe (against the original recipe found locally by id, :156-183, else not_checked); t3_steps (always not_checked, :185-193).
- Mismatch never refuses the import (bundle_importer.py:23-24).
- Refusals (BundleImportError), with the text:
  * :205-206 "No effective_run.yaml found — this is not a SPARMVET_VIZ export bundle."
  * :224-229 "This bundle has no reproducibility recipe (data_analysis_recipes_reproducibility/) — it was exported without 'Also include a reproducibility/reimport bundle' checked. ..."
  * :246-249 data_reproducibility/ empty or missing.
  * :284-287 "The reproducibility recipe inside this bundle could not be loaded: " + problems (engine_load_problems, bundle_importer.py:282). I did not verify the wording of the problems for a renamed component.
  * :215-216 refused_audit_step_problem text.
- Recipe-leg problem (bundle_importer.py:330-333): "The recipe with the id '...' on this machine (...) could not be read, so the recipe leg was not checked", with the remedy "repair or remove that recipe (Blueprint shows what is wrong with it) and import the bundle again".
- Engine-mismatch text (bundle_importer.py:150-152): "...If recipe/data/T3-steps all otherwise match, a results difference is more likely a software change than an analysis change (ADR-097)."
- Shown in the UI: export_handlers.py:755-762 "❌ Import failed: {e}" / "Import failed unexpectedly"; :766-775 "N leg(s) mismatch — see the report below." and the problems list.

4. Migration and conversion scripts (read the docstrings and write calls):
- assets/scripts/migrate_plot_specs.py (docstring 1-24): converts factory_id to an explicit geom_* layer, flat aes to mapping:, heatmap color to fill. --dry-run lists only; --apply writes (writes at :236-243, :285).
- assets/scripts/rename_vocabulary.py (docstring 1-16): config vocabulary rename (ADR-091). Writes a mapping table (:169, :659). --apply rewrites (:238, :436, :550); --dry-run at :591.
- assets/scripts/viz_rename_table.py (docstring 1-36): plot component rename table and counts. States it changes nothing. No write call found (verified by grep). Shows the 2026-11-15 naming decision (plotnine_/modif_/step_ prefixes) at lines 3-6.
- assets/scripts/migrate_config_vocabulary.py (docstring 1-17): converts pre-ADR-091 recipes, sessions and gallery files to new names. Writes only with --apply (:69, :78, :86).
- assets/scripts/migrate_recipe_format.py (docstring 1-16): format 0 to format 1 (spec_version, engine lines, renames display_name, is_primary_key, source_name). Writes only with --apply (flag :61). Write call not re-checked by me.
- assets/scripts/convert_gallery_examples.py (docstring 2-24): old compact gallery form to standard recipes. Writes only with --apply (:198, :200).
- scripts/migrate_data_analysis_recipes.py (docstring 2-17): the Polars-action / component rename, --old X --new Y across recipes (example rename_column to rename_columns). Writes unless --dry-run (:124-125). Factory IDs are not renamed (docstring 37-38).
- app/modules/renamed_keys.py (verified read by grep): refuses old names with "must fail loudly"; it converts nothing.
- Not inspected: assets/scripts/gallery_previews.py, retest_walkthrough.py, audit_old_words.py, inventory_config_keys.py, create_import_test_files.py, check_doc_links.py, audit_uml_model.py. Each matched the migrate/convert/rename grep; I did not read them.
- Finding: no script converts plot component names in a recipe except scripts/migrate_data_analysis_recipes.py (verified from its docstring). Not run.

5. Audit steps readable by hand: YES, verified (read).
- t3_steps.yaml, written by export_handlers.py:1329-1364 only when there are audited steps or aesthetic overrides (:1331). Top-level keys: generated, export_scope, t3_steps (per plot id: a list of entries with action, the step's params, reason, committed_at), and t3_aesthetic_overrides when present (:1334-1358).
- The action value is the internal node type (filter_row, exclusion_row, drop_column, aesthetic_override, random_seed; see renamed_keys.py:184).
- The README lists t3_steps.yaml (export_handlers.py:2017) and the step count per plot (:2008). report.qmd has a T3 audit table and Methods prose (export_handlers.py:1682 area, 1878).
- Reasoned: the steps record column, op, value and reason, not plot component names. The plot names live in the recipe, which is only in the Mode 2 bundle.
