# Review gate for the configuration rename (phase 1, task CONFIG-VOCAB-REVIEW-1 and CONFIG-MAPPING-1)

For Eve. Read this page, answer the questions at the end, then the real run can start. The two long files are generated and are only for checking: the inventory (`config_rename_inventory.md`, 60 keys) and the mapping table (`config_rename_mapping.md`, about 500 words and 285 paths). The rules that make the table are in `assets/scripts/rename_vocabulary_rules.yaml`; changing a rule and running `assets/scripts/rename_vocabulary.py --out ...` rebuilds the table.

## 1. What the inventory found (60 keys)

| Key | Finding | Proposal |
|---|---|---|
| `logic_access` | no code reads it | delete |
| `persona_name` | only the script `audit_hardcoded_config.py` reads it | delete; update that script |
| `scripts.excel_parser`, `scripts.test_data_gen` | the only reader, `Bootloader.get_script_path()`, has no caller | delete the keys and the method |
| `automation.ghost_save.frequency_minutes` | only `enabled` is read; the docs say "every 2 minutes", which the code does not do | delete the key; correct `user_preferences.qmd` |
| `blueprint_agent.model`, `.endpoint`, `.api_key_env`, `.gallery_awareness` | no reader yet; kept for the planned `claude_api` backend (ADR-076) | keep as reserved and say so in the file, or delete until that backend exists (your choice) |
| `data_import_panel_visible` | already removed from the templates (commit `b492de0`); `rules_persona_feature_flags.md` still describes it | fix the rule text; LEGACY-DATAIMPORT-FLAG-1 can close |
| `sidebar_profile` | exists only in design docs as a placeholder | remove from the docs |
| `default_manifest` (deployment) | read, never used | takes effect (ADR-091) |
| `manifest_selector.fixed_manifest` (every features file) | the code uses it; wrong home | removed (ADR-091) |
| `data_ingestion_enabled` (deployment) | a feature switch in the system file | see question 3 |
| `SPARMVET_CONNECTOR` (a third launch variable) | only picks the folder of the development fallback | remove; the fallback becomes `config/deployment/local/local.yaml` |

## 2. How the rules work

- One pass over every word, in snake, Camel and UPPER spelling, longest first: `persona`/`personas` to `app_features`, `profile` to `deployment`, `manifest` to `data_analysis_recipe`, `join_manifests` to `joins`. Examples: `SPARMVET_PERSONA` to `SPARMVET_APP_FEATURES`, `PersonaValidator` to `AppFeaturesValidator`, `ManifestNavigator` to `DataAnalysisRecipeNavigator`, `manifest_sha256` to `data_analysis_recipe_sha256`.
- The old meanings of "recipe" get their own names, listed in the rules file: id reconciliation (`TransformationRecipe` to `IdTransformation`), T3 audit (`t3_recipe_by_plot` to `t3_audit_steps_by_plot`, `make_recipe_node` to `make_audit_step`), step lists (`recipe_tier1` to `steps_tier1`), gallery (`submit_recipe` to `submit_example`, `recipe_meta.md` to `example_meta.md`), filter (`filter_recipe` to `filter_builder`).
- Kept on purpose: `personal*` (a different word), `AMR_Profile_Joint`, `Plasmid_Profile_Joint`, `amr_profile`, profiling words.
- Paths: `config/ui/templates/<x>_template.yaml` to `config/app_features/<x>.yaml`, `config/manifests/` to `config/data_analysis_recipes/`, `assets/template_manifests/` to `assets/template_data_analysis_recipes/`, `config/deployment/local/local_profile.yaml` to `config/deployment/local/local.yaml`, `rules_manifest_structure.md` to `rules_data_analysis_recipe_structure.md`, the gallery bundle file `recipe_manifest.yaml` to `data_analysis_recipe.yaml`.
- Status of the table: 452 tokens decided by the rules, 19 kept, 26 marked CONTEXT (0 unmapped).

## 3. The bare word "recipe" (about 680 uses): decided by area, by hand, in phase 8

The rules cannot know which meaning a sentence has. The area gives the default; the old-words audit is the checklist.

| Area (uses) | Default meaning and new word |
|---|---|
| `app/handlers`, `app/modules` (115) | T3 audit steps: "audit steps"; the filter panel: "filter builder" |
| `libs/transformer`, `config/manifests`, `libs/test_lab`, `libs/blueprint_arch` (130) | a list of wrangling or assembly steps: "steps" |
| `libs/id_reconciliation` (39) | "id transformation" |
| `libs/viz_gallery`, `assets/gallery_data` (32) | "example" (a gallery bundle) or "data analysis recipe" (its file) |
| `app/tests` (41) | follows the code under test |
| `docs/*` (~85) and `.claude/rules`, `.claude/knowledge` (~93) | per page; "data analysis recipe" for the whole file, "steps" for a list |
| `.claude/design` (141), `.claude/plans`, `.claude/tasks` | see question 5 |

## 4. Decisions I need (the open points of ADR-091 and three new ones)

1. **Key renames inside the files** (open point 1). My proposal: `curated_data` to `cache`, `user_sessions` to `user_data`, `features:` block to `flags:`, `persona_id` to `name` (and `persona_name` deleted), `show_persona_badge` to `show_app_features_badge`, `prefer_discovery` to `data_lookup: by_dataset_id | recipe_paths`. Yes or no for each?
2. **Launcher** (open point 2): I propose a separate small issue after the rename; it adds nothing to the rename. Agree?
3. **Operator lock** (open point 3): I propose moving `data_ingestion_enabled` out of the top level of the deployment file into a block `app_features_override:` (the bootloader reads it at one place). Do it now, since there is no second pass?
4. **Agent role** (open point 4): I propose renaming the two AI agent files and the word to "agent role" (`rules_persona_bioscientist.md` to `rules_agent_role_bioscientist.md`, `CLAUDE.md` section 4), so the audit can reach zero with no exclusions for "persona". Yes or no?
5. **Design records** (new): `.claude/design/` has 141 uses of "recipe" and many of the other words. Which of those files are live and which are history? History gets a HISTORICAL banner and stays as it is; live files are rewritten. My guess: `developer_workflow.md`, `functionality_dependency_map.md`, `persona_*` and `ui_panel_map_current.md` are live; `blueprint_full_feature_set_research.md`, `adr076_mvp.md`, `export_specification.md`, `design_t3_export_threading.md`, `feature_extension/*` are history.
6. **Reserved agent keys** (inventory row above): keep as reserved, or delete until needed?
7. **IRIDA check** (open point 5): issue #28, not blocking.

When you have answered, I record the decisions in ADR-091, finalize the rules file, and start phase 2.
