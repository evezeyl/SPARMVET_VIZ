# Proposal: two helper scripts were removed (D26, 2026-11-15)

Status: PROPOSAL for Eve's double confirmation. No rule file was edited. The scripts `normalize_data_analysis_recipe_fields.py` and `debug_apply_data_analysis_recipe_standards.py` were removed (nothing called them; both read or wrote the removed keys `output_fields` / `final_contract`).

1. `.claude/rules/rules_app_structure.md:79` (directory map, `assets/`): delete the line `├── normalize_data_analysis_recipe_fields.py`.
2. `.claude/rules/rules_asset_scripts.md:26` (section 3 A, example of "apply standards"): delete the clause `or apply standards (\`debug_apply_data_analysis_recipe_standards.py\`)`.
