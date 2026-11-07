# Review gate for the configuration rename (phase 1, task CONFIG-VOCAB-REVIEW-1 and CONFIG-MAPPING-1)

For Eve. Read this page, answer the questions at the end, then the real run can start. The two long files are generated and are only for checking: the inventory (`config_rename_inventory.md`, 60 keys) and the mapping table (`config_rename_mapping.md`, about 500 words and 285 paths). The rules that make the table are in `assets/scripts/rename_vocabulary_rules.yaml`; changing a rule and running `assets/scripts/rename_vocabulary.py --out ...` rebuilds the table.

## 0. Scope rule (Eve, 2026-11-07)

The rename is about the **application configuration and everything in the app that reads, writes or shows it**: YAML keys, environment variables, file and folder names, class and function names that handle them, interface labels, documentation of them. It is **not** about words that belong to something else:

| Rename | Keep |
|---|---|
| a YAML key the app reads, the launch variables, the folders and files of the configuration | a name that belongs to a wrapped Python library or to the data analysis (Polars, plotnine, Shiny, matplotlib API names) |
| the code and tests that handle those | data content and domain terms: column names, `AMR_Profile_Joint`, `amr_profile`, data profiling |
| docs, rules, UI labels that explain them | external tools' own terms: `manifest.json` of Posit Connect (rsconnect), Quarto, Docker, `pyproject.toml` fields |

How this is enforced: (1) the keep list in `rename_vocabulary_rules.yaml` (now also `manifest.json`); (2) the mapping table lists every distinct word, so a wrapped-library or data word shows up and is put on the keep list; (3) the files of `libs/transformer`, `libs/viz_factory` and the other wrapper libraries are reviewed as a diff per file before each commit, never replaced blind; (4) data files (`.tsv`, `.csv`, parquet) are outside the rename; the scan found no hit in them.

## 1. What the inventory found (60 keys)

| Key | Finding | Proposal |
|---|---|---|
| `logic_access` | no code reads it | delete |
| `app_features_name` | only the script `audit_hardcoded_config.py` reads it | delete; update that script |
| `scripts.excel_parser`, `scripts.test_data_gen` | the only reader, `Bootloader.get_script_path()`, has no caller | delete the keys and the method |
| `automation.ghost_save.frequency_minutes` | only `enabled` is read; the docs say "every 2 minutes", which the code does not do | delete the key; correct `user_preferences.qd` |  @eve but means it is not implemented while it should have been - so maybe it should go in the implemented - what is user_preferences.qd ? 
| `blueprint_agent.model`, `.endpoint`, `.api_key_env`, `.gallery_awareness` | no reader yet; kept for the planned `claude_api` backend (ADR-076) | keep as reserved and say so in the file, or delete until that backend exists (your choice) | @eve : keep - put a note it needs to be implemented 
| `data_import_panel_visible` | already removed from the templates (commit `b492de0`); `rules_app_features_flags.md` still describes it | fix the rule text; LEGACY-DATAIMPORT-FLAG-1 can close |
| `sidebar_profile` | exists only in design docs as a placeholder | remove from the docs |
| `default_manifest` (deployment) | read, never used | takes effect (ADR-091) | @eve ok will need t
| `manifest_selector.fixed_manifest` (every features file) | the code uses it; wrong home | removed (ADR-091) |
| `data_ingestion_enabled` (deployment) | a feature switch in the system file | see question 3 |
| `SPARMVET_CONNECTOR` (a third launch variable) | only picks the folder of the development fallback | remove; the fallback becomes `config/deployment/local/local.yaml` | @eve - was connector not the place holder to have the API configuration eg for IRID how to fetch the data

## 2. How the rules work

- One pass over every word, in snake, Camel and UPPER spelling, longest first: `app features`/`app features files` to `app_features`, `profile` to `deployment`, `manifest` to `data_analysis_recipe`, `join_manifests` to `joins`. Examples: `SPARMVET_APP_FEATURES` to `SPARMVET_APP_FEATURES`, `AppFeaturesValidator` to `AppFeaturesValidator`, `ManifestNavigator` to`DataAnalysisRecipeNavigator`, `manifest_sha256` to `data_analysis_recipe_sha256`.
- The old meanings of "recipe" get their own names, listed in the rules file: id reconciliation (`TransformationRecipe` to `IdTransformation`), T3 audit (`t3_recipe_by_plot` to `t3_audit_steps_by_plot`, `make_recipe_node` to `make_audit_step`), step lists (`recipe_tier1` to `steps_tier1`), gallery (`submit_recipe` to `submit_example`, `recipe_meta.md` to `example_meta.md`), filter (`filter_recipe` to `filter_builder`).
- Kept on purpose: `personal*` (a different word), `AMR_Profile_Joint`, `Plasmid_Profile_Joint`, `amr_profile`, profiling words.
- Paths: `config/ui/templates/<x>_template.yaml` to `config/app_features/<x>.yaml`, `config/manifests/` to `config/data_analysis_recipes/`, `assets/template_manifests/` to `assets/template_data_analysis_recipes/`, `config/deployment/local/local_profile.yaml` to `config/deployment/local/local.yaml`, `rules_manifest_structure.md` to `rules_data_analysis_recipe_structure.md`, the gallery bundle file `recipe_manifest.yaml` to `data_analysis_recipe.yaml`.
- Status of the table: 452 tokens decided by the rules, 19 kept, 26 marked CONTEXT (0 unmapped).

## 3. The bare word "recipe" (about 680 uses): decided by area, by hand, in phase 8

The rules cannot know which meaning a sentence has. The area gives the default; the old-words audit is the checklist.

| Area (uses) | Default meaning and new word |
|---|---|
| `app/handlers`, `app/modules` (115) | T3 audit steps: "audit steps"; the filter panel: "filter builder" |
| `libs/transformer`, `config/manifests`, `libs/test_lab`, `libs/blueprint_arch` (130) | a list of wrangling or assembly steps: "steps" | @eve here be carefull what is configuration and what is python wrapers ! always 
| `libs/id_reconciliation` (39) | "id transformation" |
| `libs/viz_gallery`, `assets/gallery_data` (32) | "example" (a gallery bundle) or "data analysis recipe" (its file) |
| `app/tests` (41) | follows the code under test |
| `docs/*` (~85) and `.claude/rules`, `.claude/knowledge` (~93) | per page; "data analysis recipe" for the whole file, "steps" for a list |
| `.claude/design` (141), `.claude/plans`, `.claude/tasks` | see question 5 |

## 4. Decisions I need (the open points of ADR-091 and three new ones)

1. **Key renames inside the files** (open point 1). My proposal: `curated_data` to `cache`, `user_sessions` to `user_data`, `features:` block to `flags:`, `app_features_id` to `name` (and `app_features_name` deleted), `show_app_features_badge` to `show_app_features_badge`, `prefer_discovery` to `data_lookup: by_dataset_id | recipe_paths`. Yes or no for each?
2. **Launcher** (open point 2): I propose a separate small issue after the rename; it adds nothing to the rename. Agree?
3. **Operator lock** (open point 3): I propose moving `data_ingestion_enabled` out of the top level of the deployment file into a block `app_features_override:` (the bootloader reads it at one place). Do it now, since there is no second pass?
4. **Agent role** (open point 4): I propose renaming the two AI agent files and the word to "agent role" (`rules_agent_role_bioscientist.md` to `rules_agent_role_bioscientist.md`, `CLAUDE.md` section 4), so the audit can reach zero with no exclusions for "app features". Yes or no?
5. **Design records** (new): `.claude/design/` has 141 uses of "recipe" and many of the other words. Which of those files are live and which are history? History gets a HISTORICAL banner and stays as it is; live files are rewritten. My guess: `developer_workflow.md`, `functionality_dependency_map.md`, `app_features_*` and `ui_panel_map_current.md` are live; `blueprint_full_feature_set_research.md`, `adr076_mvp.md`, `export_specification.md`, `design_t3_export_threading.md`, `feature_extension/*` are history.
6. **Reserved agent keys** (inventory row above): keep as reserved, or delete until needed?
7. **IRIDA check** (open point 5): issue #28, not blocking.

When you have answered, I record the decisions in ADR-091, finalize the rules file, and start phase 2.


## 5. Round 2: verification and answers to your comments (2026-11-07)

**Verified again, all correct:** `logic_access` read by nothing; `app_features_name` read only by `scripts/audit_hardcoded_config.py` (and used as a test value in `test_ui_scenarios.py`); `get_script_path()` has no caller outside its definition; the four `blueprint_agent.*` keys have no reader, and the agent adapter says "claude_api and local are Phase 2/3" (`libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:399`); `data_import_panel_visible` was removed in `b492de0` while `rules_app_features_flags.md:164` still describes it; `sidebar_profile` exists only in `.claude/design/` documents; `default_manifest` is read at `bootloader.py:103` and never used; no launch variable is read in tests or code other than the three. The scan of the rename found **no hit in data files** and one external-tool term (`manifest.json`, `.gitignore`, rsconnect), now on the keep list.

**Your comments**

1. **`ghost_save.frequency_minutes`** (the file is `user_preferences.qmd`, a Quarto page in `docs/workflows/`; `.qd` was a typo). You are right that this is a promise that was not built. `user_preferences.qmd` says a debounced autosave runs every 2 minutes (`ghost_save_trigger` in `server.py`). There is no such function: `server.py` has none, and nothing reads `frequency_minutes`. What exists is event-driven: the T3 ghost is written on every Apply and when leaving Home, the assembly ghost on assembly (`audit_stack.py`, `blueprint_handlers.py`; the contract says so in `rules_ui_dashboard.md` section 1 and `ui_implementation_contract.md` 12d). Two ways: (a) the event-driven behaviour is the intended design: delete the key and correct the qmd page (my proposal), or (b) you want the timed autosave: it becomes a new task `GHOST-SAVE-TIMER-1`, the key stays with a note "not implemented". **Which do you want?**
2. **Reserved `blueprint_agent.*` keys:** kept, each with a comment "reserved for the claude_api backend, not implemented (ADR-076 phase 2)". Done in the rename run; I also add a task for the backend.
3. **`default_manifest`** (your comment stops at "ok will need t"). **Please finish the sentence**; I assume "will need tests and docs", which are in the plan.
4. **Connector.** You are right to ask, and it showed a second ambiguity. History: before ADR-048 (April 2026) "connector" was the name of the whole configuration file (`config/connectors/local/local_connector.yaml`). Since then the IRIDA/Galaxy API settings live in the deployment file (the `irida:` block, `deployment_type`) and the code that uses them is the library `libs/connector` (`FilesystemConnector`, `IridaConnector`, `GalaxyConnector`). So `SPARMVET_CONNECTOR` is only a vestige (it picks a folder name for the development fallback), and the bootloader still calls the deployment file "connector": `connector_path` (20 uses), `connector_config` (15), `_load_connector_config`, `_connector_cache`, `connector_template.yaml`, `local_connector`. Proposal: the **library keeps its name** (it is the adapter that fetches data), the **deployment-file sense is renamed** (`deployment_path`, `deployment_config`, `deployment_template.yaml`, ...), `SPARMVET_CONNECTOR` is removed. Added to the rules and the mapping table (6 tokens, status auto; `SPARMVET_CONNECTOR` status REMOVE) and to the old-words audit as a fifth word. `docs/workflows/connector.qmd` (a page titled "Deployment Configuration" that also describes the adapters) would be split or renamed `deployment.qmd`. **Agree?**
5. **Libraries row (config versus Python wrappers):** covered by the scope rule above. In the wrapper libraries I change a word only where it names the configuration (for example the `recipe:` step list of a join as the app reads it, the docs of where an action is used in a recipe), never the wrapped API or the data. Reviewed per file.

**New items found while verifying**
- `.claude/settings.json` has 56 hits: allow-list entries for old commands with old paths (many from an earlier project layout). Proposal: remove the stale entries instead of renaming them.
- `.claude/baselines/*.txt` and `.claude/conversations/` are history snapshots: added to the audit exclusions with the logs.
- `config/ui/theme.css` has interface element ids such as `#btn_download_manifest` and `#btn_import_manifest`: renamed together with the code that creates them and the tests that click them.
- `assets/gallery_data/gallery_index.json` stores bundle paths: regenerated.

**Your decisions 1 to 7 of section 4:** I read "all your suggestions appear correct" as accepted for: the key renames of question 1 (`curated_data` to `cache`, `user_sessions` to `user_data`, `features:` to `flags:`, `app_features_id` to `name`, `show_app_features_badge` to `show_app_features_badge`, `prefer_discovery` to `data_lookup`), the launcher as a later issue, the `app_features_override:` block, "agent role" for the two agent files, my guess on live and history design records, and IRIDA as issue #28. Tell me if any of these was not meant that way. They are recorded in ADR-091 once the open items above are answered.
