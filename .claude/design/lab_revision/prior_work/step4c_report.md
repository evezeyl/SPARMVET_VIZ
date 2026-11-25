<!-- copied unchanged on 2026-11-21 from .claude/design/studies/scratch_records_2026-11/engine_keys/step4c_report.md of the main tree (not in git; file dated 2026-11-18); a record of an earlier study, not a decision -->
# Step 4c of the big recipe change: PARTIAL (saved by the coordinator from the builder's last message; the builder ran out of time before saving it)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`. Nothing uncommitted except git-ignored files under `tmpAI/`. No push, no merge of `dev`.
A background run `pytest app/tests` (non-browser) of the builder may still be alive; its output is `tmpAI/runs/app_run_4c.txt` in the worktree (ends with `DONE`). Result unknown.

## Commits (after e0ed4655)
- 7aad8ccd `libs/blueprint_arch`: navigator, tube map, branch plan, group manager, agent tools and prompt.
- d3adf592 `libs/test_lab`: bootstrapper and scaffolder.
- 92af1ed4 Blueprint: `blueprint_handlers.py`, `wrangle_studio.py`, the validator's fragment report, tests.
- f3141210 scaffold scripts.
- 080328cc the rail labels a tier-2 file "(tier 2)".
- cd06d045 scan test; coherence audit; branch plan drops the dead role `output_fields`.

## What changed
- Navigator: `build_sibling_map` registers the `tier1` and `tier2` include files with a `tier` tag; siblings are `input_fields`/`tier1`/`tier2`; a plot is its own entry, inline or included. Nothing reads `wrangling`, `steps`, `spec`, `output_fields`, `pre_plot_wrangling`. `build_plot_lineage` uses the tier-1 file.
- Branch plan: a table and a join get `tier1: !include` with a file `steps: []`; a plot is copied into its own file with `ui_label` "<label> (branch)"; tier2 is not written.
- Tube map and groups: the mapper reads the entry and tiers; the group manager writes `ui_label` and `<plot>: !include` of the whole entry; new `plot_ui_label`.
- Agent: example patch path and prompt rule in the new shape.
- Blueprint handlers: a tier file is loaded as one tier; Save writes `{data_engine kept, steps}`; a step of another tier is refused with a message; Plot Save writes the whole entry; the upload reads `steps` or `tier1`/`tier2` `{steps}`, an old shape is named (`[UP02]`), not read; the inventory reads `ui_label`.
- wrangle_studio: Join click uses `DataWrangler.tier_steps` (it called a function that no longer exists); plot preview reads the entry plus `plot_engine_slot`.
- Test Lab: tables get a label and `tier1`; the metadata table has its two files and a project-relative path; the scaffolded join uses `metadata_schema` as ingredient; the checker accepts what both write.
- Scripts: `create_data_analysis_recipe.py` writes `tier1` as a file and `ui_label`; `SF_create_data_analysis_recipe.py` rewritten through the recipe factory; `scripts/audit_data_analysis_recipe_coherence.py` stops reading `output_fields`.

## What a user sees differently
- TubeMap on 50 shipped recipes: identical to dev (element by element).
- Lineage rail: a table with a tier-2 file now shows it, labelled "<id> (tier 2)"; the selector list shows "<id> — wrangling (tier 2)". 9 chains differ, only by those nodes.
- Saving a step tagged tier 2 into a tier-1 file is refused with a message.
- REMOVED (PROVISIONAL, for Eve): the "Add plot wrangling" button (it told users to write the refused key `pre_plot_wrangling`); the "Forward clear" hint (it always said "clear"); the dead roles `plot_wrangling` and `output_fields`.
- Upload of a fragment: message text changed ([UP01]/[UP02]).

## Tests run (all passed)
`libs/blueprint_arch` 432 (was 9 red); `libs/test_lab` 111; `libs/utils` 2101; `test_writers_emit_format_one` + `test_scripts_need_the_app_path` 38 passed 1 xfailed (was 12 red); `test_wrangler_upload_step_numbering`, `test_blueprint_tier_files` (new), `test_blueprint_save_roundtrip`, `test_blueprint_known_defects`, `test_no_old_recipe_keys_read` (new).
Adapted to the decided shape: `test_branch_plan`, `test_group_plot_manager`, `test_writers_emit_format_one`, `test_blueprint_save_roundtrip`, `test_blueprint_known_defects`, `test_wrangler_upload_step_numbering`, the Test Lab tests. New: `test_navigator_new_shape.py` (23), `test_blueprint_tier_files.py`, `test_no_old_recipe_keys_read.py`.

## NOT run
- The full `app/tests` non-browser run (unfinished).
- Browser files `test_shiny_smoke_blueprint.py`, `test_shiny_gate_gap.py`, `test_every_app_features_starts.py`.
- The three proofs at the last commit (pictures 51, golden, gallery previews 34).

## Break-once
`tmpAI/breakonce4c.py` (output `tmpAI/breakonce4c_out.txt`): 35 breakages, 35 caught. The two `wrangle_studio.py` edits (join click, plot-preview engine) have no headless test and were NOT broken once.

## Remaining old-key hits
- By design (refuse or rewrite the old shape): `recipe_check.py`, `engine_keys_migration.py`, `convert_gallery_examples.py`, `migrate_plot_specs.py`, the validator's refusal message (listed in the scan test with reasons).
- Not recipe reads: role names, lineage step types, `label` of form schemas, session and audit-step labels.
- Not fixed, not decided: `libs/utils/config_loader.py:121` still unwraps an `output_fields` wrapper key; `debug_bootstrap_viz_yamls.py` writes the plot library's own test-data format (the "165 test-data files" open point); `config/ui/agents/blueprint_default.md` teaches `wrangling:`/`steps:` and old action names; `anonymiser.build_deanon_steps` and the coherence audit use the old action name `join` (the audit's join-key check never matches `polars_join`); `info.label`, table/join/field `label` (pending Eve).

## PROVISIONAL choices, with options
1. A tier file holds one tier; a step tagged for the other tier is refused on Save. Options: refuse (built); write two files; drop the T1/T2 picker.
2. Upload: a `steps:` fragment goes to tier 1; `tier3` fragments are ignored.
3. The "Add plot wrangling" button is removed. Option: re-point it to `tier3`.
4. The join "upstream" panel lists ingredients with no fields, as on dev. Option: show the ingredients' `input_fields`.
5. TubeMap node text stays the node id.
6. The rail still lists a table once by its file and once by its id (existing behaviour).
7. Test Lab path fallback to an absolute path for data outside the project is kept (the checker refuses it).
8. SF script: `input_only` writes just the `input_fields` mapping.

## Not checked
Blueprint in a browser (load, save, branch, upload, inventory); the round trip of a real save on shipped recipes.
