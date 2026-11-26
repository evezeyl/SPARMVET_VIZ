# Can Blueprint still build tier 1 and tier 2 on the branch? Proof by a run (2026-11-18)

Reviewer run. "ran" = I ran it in a real browser (Chromium headless); "read" = I read the code. BRANCH = `task/engine-keys` head `64d99e3f`, DEV = `dev` in the main folder.
Pictures, scripts, logs and the JSON of each run: `tmpAI/engine_keys/bp_proof/` (file names: `<step>_<what>_<TREE>.png`; `res_*_<TREE>.json` hold the raw results).

## How the run was set up (so you can trust it)
- Code that ran: BRANCH printed `.claude/worktrees/engine-keys/app/src/bootloader.py`, `.../libs/blueprint_arch/...` and `.../libs/transformer/...` (ran). DEV printed the main-folder files (ran).
- Blueprint reads its recipe list from `config/data_analysis_recipes/pipelines` under the folder where the app starts (read: `blueprint_handlers.py` about line 1073 on dev, same on the branch). So each tree got a scratch PROJECT ROOT (BRANCH: `<worktree>/tmpAI/bp_proof/root/`, DEV: `tmpAI/engine_keys/bp_proof_dev/root/`) with a copy of the demo recipe `1_test_data_ST22_dummy` and its folder; the rest (config, data) linked in. The recipe list of Blueprint showed ONLY the scratch recipe (`res_s2_3_BRANCH.json`: one entry), and every Save was read back from the scratch files. `git status --short` is EMPTY in both trees after all runs: no shipped file changed.
- App: `qa` app features, scratch deployment file, no agent started.

## (i) Flags (read from `config/app_features/qa.yaml`, identical in both trees; the Blueprint screen confirmed them)
| flag | value |
|---|---|
| blueprint_enabled | true |
| data_analysis_recipe_edit_enabled | true |
| blueprint_agent_enabled | true (the screen says "Agent unavailable - backend not configured") |
| blueprint_agent.backend | disabled (no external agent started) |
| test_lab_enabled | true |
| testing_mode | true |
| automation.ghost_save.enabled | false |
| interactivity_enabled | true |
| t3_sandbox_enabled | true |

Not covered because of the flags: Blueprint's draft autosave (needs ghost save on, which qa switches off); the AI agent. The plot-defaults form is shown (agent flag on) but I did not use it.

## (ii) Table (rows = your steps; each cell: worked / failed / not covered)
| Step | BRANCH | DEV |
|---|---|---|
| 1 Open Blueprint, load recipe, TubeMap | WORKED (ran): 105 components, map drawn. `1_tubemap_BRANCH.png` | WORKED (ran): 98 components. `1_tubemap_DEV.png` |
| 2 Tier 1: pick action, fill, Apply | WORKED (ran). Picker offers 46 actions for context "T1" (68 all contexts, 65 for T2, 36 assembly, 191 plot). Five: filter rows, all horizontal, any horizontal, bottom k, cast. I applied "with columns" (new column `proof_one` = 1) on table FastP: the step appears in the list. The "filter rows" form opens (column, operator, value, missing values, which ends); I did NOT apply it, and I did not try a rename. Glimpse: on a table it says "No data loaded" but the column list under it gains `proof_one`; on a join (FastP_with_metadata) the glimpse stays 42 rows x 7 columns after Apply. `2_t1table_apply_BRANCH.png`, `2_tier1_apply_BRANCH.png` | WORKED the same (ran): same counts 46/65/68/36/191, same step, same glimpse behaviour. `2_t1table_apply_DEV.png` |
| 3 Save; file; checker; reload; HOME | WORKED for a TABLE (ran): `FastP_wrangling.yaml` = `data_engine: python-polars` + `steps:` with the new step. Checker: 0 structure and 0 data problems. After restart HOME: 17 of 17 plots drawn (baseline before: 17 of 17). The join table downstream now has 8 columns with `proof_one` (`3_glimpse_after_restart_...BRANCH.png`). FAILED for a JOIN file: "Save is not supported for component role 'join'" (nothing written). Side effects of Save (ran): comments of the file are lost, a line `data_engine: python-polars` is added, and each untouched step gets `comment: <file name>` (T2 file). `3_t1table_save_BRANCH.png`, `3_tier1_save_BRANCH.png` | FAILED (ran): Save writes `wrangling:` + `tier1:` (an extra key). The checker gives 3 problems and HOME refuses the recipe: "No data analysis recipes yet ... failed its checks" (0 plots; `home_after_t1_save_DEV.png`). Join file: same refusal as the branch. `3_t1table_save_DEV.png` |
| 4 Edit a value, Save; remove the step, Save | EDIT WORKED (ran): file holds `pl.lit(2)`. REMOVE ONE STEP: no way found (ran: the step card has 0 buttons; read: no delete in the render code). Only "Clear All nodes" exists: it removes every step of the file and Save writes `steps: []`. For the empty tier-1 file of FastP the content is equal except the lost comment and the added `data_engine` line (not byte-identical). `4_t1table_edit_BRANCH.png`, `4_t1table_remove_BRANCH.png` | EDIT WORKED but into a wrongly shaped file (ran). Same "no remove one step; Clear All only". `4_t1table_edit_DEV.png`, `4_t1table_remove_DEV.png` |
| 5 Tier 2 | WORKED for a TABLE (ran): the map node loads the tier-1 file; the tier-2 file ("ResFinder (tier 2)") is reached from tab 2 "Interface (Fields)" -> Lineage Rail button. Same picker (the user chooses "T2 - Branch": 65 actions vs 46 for T1; the file does not restrict it). Add, Apply, Save OK; the 2 old steps kept (plus `comment:` keys added); checker 0/0; HOME 17 of 17; HOME "Result (T2)" data of the AMR heatmap shows the new column `proof_one`, "Raw (T1)" does not (`5_home_data_Result_after_t2_BRANCH.png`, `5_home_data_Raw_after_t2_BRANCH.png`). JOIN tier 2 ("MLST_with_metadata (tier 2)"): its 2 steps load, add/Apply work, Save REFUSED (role join). `2_t2table_*_BRANCH.png`, `2_t2join_*_BRANCH.png` | FAILED (ran): the map node shows only the tier-1 step of ResFinder (1 step); the 2 tier-2 steps are not shown. After my Save the tier-2 block held ONLY my step: the 2 old tier-2 steps (`total_gene_count`, sort) were lost silently, and the file shape is wrong (HOME refuses). Join MLST: only the join step shown, tier-2 steps not shown. `2_t2table_apply_DEV.png`, `3_t2table_save_DEV.png`, `e5_t2probe_MLST_with_metadata__wrn_DEV.png` |
| 6 Refusal (step tagged tier 2 saved into a tier-1 file) | WORKED as designed (ran). Gesture: load a tier-1 file (FastP), set the picker context to "T2 - Branch", Add, fill, Apply (nothing on the card says tier 2), Save. Message: "The step 'polars_with_columns' belongs to tier2, but this file is tier1: nothing was saved. Open the tier2 file of the table to save it there, or remove the step." File unchanged (ran). Way out: click the table node again: the file's steps reload and the wrong step is gone (ran). Weak points: the table FastP has NO tier-2 file, so "Open the tier2 file" cannot be done; and "remove the step" has no button. `6_refusal_BRANCH.png`, `6_refusal_reclick_BRANCH.png` | No refusal (ran): the same gesture is saved as a tier-2 step into the file, in the wrong shape; HOME then refuses the recipe. `6_refusal_DEV.png` |
| 7 Tier 3 (data steps for one plot) | FAILED / nothing offered (ran). Selecting a plot node gives "Imported 0 steps from .../plots/MLST_counts_bar.yaml"; no mapping, no layers, no upstream, no data glimpse; no "Add plot wrangling" button; no word about tier 3 anywhere (tabs 1 to 4 and Groups & Plots searched). So on the branch a plot cannot even be opened for editing in Blueprint. `7_plot_node_tab1_BRANCH.png`, `7_plot_node_tab2_BRANCH.png` | The plot OPENS (ran): mapping (x sequence_type, fill country) and 2 layers shown, glimpse 42 x 6. Tab 2 has the button "Add plot wrangling"; click = a notice only: "To add plot wrangling for 'mlst_bar': create a wrangling YAML and add 'pre_plot_wrangling: !include <path>' to its plot block ... reload". Nothing is built. `7_plot_node_tab1_DEV.png`, `7_plot_add_wrangling_click_DEV.png` |
| 8 Join (Joint Designer tab) | PARTLY (ran, one attempt): opens a form "Creating a new join step" (it does not show the existing join); picking FastP + metadata_schema, key sample_id, left join, text, "Preview key match" works ("42 / 42 left keys matched"); Apply adds a step to the list named `join` (not `polars_join`); Save then REFUSED (role join). Nothing written. `8_joint_preview_BRANCH.png`, `8_joint_apply_BRANCH.png` | Same, step for step (ran). `8_joint_preview_DEV.png`, `8_joint_apply_DEV.png` |
| 9 Other failures | see (iv) | see (iv) |

## (iii) Plain answer
Yes, for tables: on the branch Blueprint can still build tier 1 and tier 2 steps in a table's file, edit them, save them, and the recipe stays valid, HOME draws all 17 plots and the new tier-2 column shows in HOME's Result data (ran). Joins are different: steps can be added in the screen but a join file cannot be saved, on the branch and on dev (ran). The branch is better than dev for saving (dev's Save writes a wrong shape that makes HOME refuse the recipe, and loses tier-2 steps), but it is worse for plots: plots cannot be opened in Blueprint on the branch, and tier 3 cannot be built on either tree.

## (iv) What failed, per tree
BRANCH (ran unless said):
1. There is NO visible Save button: `#btn_save_internal` is inside a hidden box (size 0 x 0, parent `display:none`; read: `wrangle_studio.py` line 253-255). I pressed it by script, as the repo's own tests do (`test_shiny_smoke_blueprint.py` line 413). A real user cannot save a step in Blueprint. Same on dev. NOT a result of the big change.
2. Saving the tier files of JOINS is refused ("Save is not supported for component role 'join'"). Same on dev. So tier 1 and tier 2 of joins cannot be built end to end.
3. Plots do not open in Blueprint: "Imported 0 steps", no mapping and layers, no glimpse. On dev the same click shows mapping, layers and glimpse. This is a difference caused by the branch (the plot spec load takes the other path, `blueprint_handlers.py` line 922 on the branch). The "Add plot wrangling" button is gone (as announced).
4. No way to remove ONE step (only "Clear All nodes", which also removes the old steps). Same on dev.
5. Save rewrites the file: comments lost, `data_engine: python-polars` added, `comment: <file name>` added to every untouched step of a file. It changes file text silently (the steps themselves are unchanged).
6. The refusal text tells the user to "open the tier2 file of the table" or "remove the step": for a table without tier-2 file the first is impossible, the second has no button. The step card does not show its tier.
7. The glimpse of a table says "No data loaded" while showing columns (including the new one) from the last data shown. The glimpse of a join does not change after Apply (it changes only after Save and reload of the data).
8. Joint Designer Apply writes the step name `join`, not `polars_join` (read: `blueprint_handlers.py` line 2259; the constant `action_names.JOIN` is `polars_join`). Same on dev (line 2391). It was never saved, so I did not see what the file would hold.
9. The lineage rail lists some tables twice (MLST, metadata_schema). Same on dev. The map is small: nodes overlap at the default zoom (my first click on the plot "mlst_bar" opened "qa_facet_by_mapping").
10. Console: only deprecation warnings of the date picker and "style property cursor: pointer is invalid" (same on both trees). Server log of the last session: no error line (earlier logs were overwritten when I restarted the app).

DEV (ran):
1. Save of a table file writes `wrangling:` + tier keys: the checker gives 3 problems and HOME refuses the recipe ("No data analysis recipes yet").
2. A table's tier-2 steps are not shown in Blueprint, and Save keeps only the step typed in this session: 2 existing tier-2 steps were lost (silent loss of a result).
3. Items 1, 2, 4, 8, 9, 10 of the branch list also happen on dev.

## (v) What could not be tested, and why
- A rename and a filter step were not applied (I applied "with columns"); the filter form only opened.
- Draft autosave and the AI agent: switched off by the `qa` flags (ghost save off, backend disabled).
- A real user's Save: there is no visible button, so I used the hidden one.
- Editing plot layers on the branch (impossible: plots do not open), groups and plots CRUD, "Create branch", YAML escape hatch, plot-defaults form: not part of the request, not run.
- Joins saved to a file: refused by both trees, so no join file content to check. Tier 1 of the join glimpse after a join-file Save: not possible.
- The test suites, the browser gate and the golden pictures were NOT run (this is a proof run, not the controls).
- One recipe only (the demo ST22), one harmless step (a constant column): other actions, other recipes not checked.
- Earlier server logs were overwritten on each app restart; only the final session's logs were read.

Scratch folders are left in place (recipe files reset to the first copy at the end): BRANCH `.claude/worktrees/engine-keys/tmpAI/bp_proof/`, DEV `tmpAI/engine_keys/bp_proof_dev/`. No app of mine is running.
