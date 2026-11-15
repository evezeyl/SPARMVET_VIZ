# Proposal: `.claude/rules/rules_asset_scripts.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. Checked: every script named in the file against `ls assets/scripts` (2026-11-15).

## 1. Section 3 B, the example script name (FACT)
Today (line 32, "Suggestive Tools (Test Data / Synthesis)"): `Scripts meant solely to create mock TSVs (\`create_test_data.py\`) or synthetic relational models ...`
Proposed: `... create mock TSVs (\`generate_demo_data.py\`, \`create_import_test_files.py\`) ...`
Why: `assets/scripts/create_test_data.py` does not exist; `generate_demo_data.py` (synthetic TSVs from the ST22 ground truth with AquaSynthesizer) and `create_import_test_files.py` (valid and deliberately broken upload files, docstring read) exist.

## 2. Section 3 A (no change), checked
`create_data_analysis_recipe.py` exists and writes recipe format 1 (docstring: "Scaffold a data analysis recipe in recipe format 1"); `debug_apply_data_analysis_recipe_standards.py` exists; `figshare_triple_integration.py` exists. `migrate_recipe_format.py`, `migrate_plot_specs.py`, `golden_baseline.py`, `gallery_previews.py` are Functional Assistants too and are not listed; optional: add them as examples of type A (they change or record foundational data). Kind: FACT, optional.

## Not settled
None.
