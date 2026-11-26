# Blueprint: a plot node opens again, and the refusal message is true (report, 2026-11-18)

Branch `task/engine-keys`, worktree `.claude/worktrees/engine-keys`. Start head `64d99e3f`, end head `fa7f856b`. All committed, nothing left uncommitted.

## Commits
| hash | what |
|---|---|
| `5892a872` | A: `fix(blueprint)`: a plot node opens again; includes read as YAML |
| `ade69f0b` | B: `fix(blueprint)`: the refusal of Save tells what is true (PROVISIONAL wording) |
| `b6b40c40` | `fix(blueprint)`: the Joint Designer writes `polars_join`, not `join` (found while answering the question; see below) |
| `fa7f856b` | `test(blueprint)`: the browser tests tap a node only when the map holds it (a plain evaluate hung twice) |

## A. The regression

### Cause (verified by reading and by a run)
Not the plot loader (the loader reads the new shape fine). The file of the plot never reached it.
- Blueprint builds its map of the recipe's files (`includes_map`) with a scan of the recipe text for `!include '...'` that REQUIRES QUOTES: `app/handlers/blueprint_handlers.py` line 420 (`_do_refresh_blueprint`) and line ~1050 (the tap handler), and `libs/blueprint_arch/src/blueprint_arch/agent_tools.py:274`. Before: `re.findall(r"!include\s+['\"]([^'\"]+)['\"]", raw_text)`.
- The migrated demo recipe writes the include of a plot UNQUOTED (`mlst_bar: !include 1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml`). On `dev` a plot was `spec: !include '...'`, quoted.
- Run on the demo recipe text: the quoted scan finds 44 includes; the unquoted-tolerant scan finds 61. The 17 missing are exactly the 17 plot files.
- The plot file is then not in the map. The tap picks the right file name, but `selected in inc_map` is false, so the code goes to the fallback "Mode B" (`blueprint_handlers.py` about line 806 on the branch; the line 922 of the proof run is its "Imported N steps" message). Mode B finds no steps for a plot: "Imported 0 steps".

### Repair
- `libs/blueprint_arch/.../data_analysis_recipe_navigator.py`: new `include_paths(raw_text)`. It reads the YAML with a loader that records every `!include` (quoted or not, a comment or a string is not an include, each file once, in file order; text that is not YAML raises). Used at the three places above.
- `app/modules/blueprint_plot_view.py` (new, pure): `plot_view(entry)` gives the target table and the nodes (mapping first, then each layer) of a plot entry. Used by the file path (Mode A) and by the inline path (Mode B).
- One small reading beyond dev, same screen: a plot written INLINE in the recipe now also shows its mapping and layers (on `dev` an inline plot opened with 0 steps too; I asked for no new control, this is not a control). Nothing can be saved from it (no file), as before.
- Nothing added to Blueprint otherwise: no tier 3 editing, no "Add plot wrangling".

### What a user sees now
For all 17 plots of `1_test_data_ST22_dummy`: the stack shows "mapping (aes)" and every layer, with the mapping columns; the selector holds the plot's own file; the glimpse line shows rows; no "Imported 0 steps". Browser run (qa): 17 of 17 open (selected by node id, the opened file asserted equal to the file asked for). Mapping form of `mlst_bar`: `x` = sequence_type, `fill` = country. Layers on this branch's file: 3 (`geom_bar`, `scale_x_discrete`, `labs`), so 4 cards with the mapping (the brief said 2: that was the dev file).

### Tests (written before the browser run; the code edit was made before the tests, so the break-once is the proof)
- `libs/blueprint_arch/tests/test_include_paths.py`: 6 tests (quoted, plain, double, in a list, duplicates, comment and string are not includes, not YAML is refused, every file the map registers is in the includes, the 17 plot files of the demo).
- `app/tests/test_blueprint_plot_open.py`: 32 tests. Real closures of `define_server` (cut out by `ast`, as the repo's other tests do): the tap of EACH of the 17 demo plots (file, mapping, layers, table asked from the orchestrator, `active_viz_id`); an inline plot; the same plot in its own file with a quoted and with an unquoted include; the pure `plot_view`; round trip on a copy of the demo recipe in a scratch project root: save unchanged (equal values, checker accepts), change one layer value (only that value differs, no `spec` key, checker accepts), change a mapping value through the real Apply form handler then Save (only that value differs, checker accepts).
- `app/tests/test_shiny_smoke_blueprint.py`, class `TestBlueprintPlotOpen` (qa): all 17 plots (stack, layers, mapping columns, opened file equals the file asked for, rows in the glimpse line, no "Imported 0 steps"), and the mapping form of `mlst_bar` with its field values and the card count.
- Break once (reversible edits, restored): old quoted scan put back at line 420 -> 21 of 32 headless tests fail and both new browser tests fail; `plot_view` made empty -> 24 fail; old regex inside `include_paths` -> 4 of 6 fail.
- Round trip note (not a defect of mine, from the existing writer): the save writes keys in the order of the specification (`mapping` before `layers`), not the order of the old file; the values are equal. Comments of a file are lost (already in the proof).

### Why the earlier controls missed it (the 19 Blueprint browser tests passed)
Two missing things, both checked:
1. The click test (`TestBlueprintNodeClick`) asserted only that the data status line shows "N rows" and that no error text is on the page. That line is filled by another function (`wrangle_studio.handle_node_selection`), which reads the recipe by itself and does not use the map of files. So it was green while the stack of the plot was empty. I ran it with the old scan put back: 2 passed. No assertion looked at the stack, the opened file or the mapping form.
2. The headless tests build recipes with the factory (`yaml.dump`), which QUOTES the include path; the demo recipe, written by the migration tool, does not. The one form that failed was in no test input. (`test_blueprint_failed_load.py` also writes quoted includes.) The new tests write both forms.

## B. The refusal message (PROVISIONAL, goes to the owner)
Code: `app/modules/blueprint_tier_refusal.py` (`other_tier_refusal`), called from `_serialise_component_for_save`, which now also receives the tier files of the table and the open file name. Marked PROVISIONAL in the code (the module docstring and the call). The refusal itself is unchanged.

Text, a table WITH a tier-2 file (ResFinder, a tier-2 step into the tier-1 file):
> The step 'polars_with_columns' was made for tier 2, but the file that is open (ResFinder_wrangling_tier1.yaml) is tier 1: nothing was saved. This table has a tier 2 file, ResFinder_wrangling_tier2.yaml: open it from the lineage rail and add the step there. To drop the unsaved step from this screen, click the table node again: the steps of the open file are loaded again.

Text, a table with NO tier-2 file (FastP):
> The step 'polars_with_columns' was made for tier 2, but the file that is open (FastP_wrangling.yaml) is tier 1: nothing was saved. This table has no tier 2 file yet. Blueprint cannot create one: add `tier2:` with its file to the table in the recipe by hand. To drop the unsaved step from this screen, click the table node again: the steps of the open file are loaded again.

A third case exists in the data: a tier written INSIDE the recipe (no file). Text: "This table writes its tier N inside the recipe, not in a file, and Blueprint saves into files only: change it in the recipe by hand."
The wording names no control that does not exist ("lineage rail" exists: the proof run reached the tier-2 file through it).
"Click the table node again drops the step": verified by the proof run (ran) and now by a test (the stack after the second tap equals the file's steps; the file is unchanged).
Tests (`app/tests/test_blueprint_tier_refusal.py`, 16): the helper in all cases (file exists, none, inline, other direction, no information, words that must not appear), and the save closure on a copy of the demo recipe: FastP (none) and ResFinder (exists), the file text is identical after the refusal, a step of the right tier is still saved, a second tap removes the unsaved step. Break once (old message put back): 3 tests fail. `test_blueprint_tier_files.py` had its match string adapted to the new text.

## Answers on the older findings (not fixed, except the join name)
- Hidden Save. `btn_save_internal` is inside `#blueprint_hidden_controls`, `style="display:none"` (`app/modules/wrangle_studio.py` lines 253-255; comment: "kept in DOM so Shiny bridge can programmatically..."). A real user sees NO Save button for component steps; nothing in the screen saves the steps of a tier file or a plot. Visible controls that write to disk are different things: "Save to data analysis recipe" (the info block of the recipe, `btn_bp_meta_save`), Create (new recipe), group and plot CRUD, branch write. "Download/Export" gives a download. The YAML escape hatch "save" only changes the session view. So no visible control saves a tier file or a plot. The repo's own test presses the hidden button by script.
- Join files cannot be saved: `_serialise_component_for_save` raises "Save is not supported for component role 'join'" (unchanged).
- Joint Designer step name: `_jd_apply` (`blueprint_handlers.py` about line 2250) rebuilt the node with the literal `"join"`, although `build_join_step` already emitted `polars_join`. Would it be SAVED on this branch? Yes: the Designer works on whatever stack is open; a stack opened from a table's tier file has role "wrangling" and CAN be saved, so the file would hold `action: join`. The checker refuses it: `ST02 'join' is not a registered action (removed: an action of the old recipe format). Suggestion: use polars_join.` (shown by a test). So it was a writer of the old shape: corrected to the constant `JOIN` (commit `b6b40c40`), with `app/tests/test_blueprint_joint_step_name.py` (3 tests; failed before the fix, pass after). Also, the step could not be reopened in the Designer before (the reopen compares with the registered name).
- Not fixed: no way to remove one step; glimpse of a table says "No data loaded".

## The flags (qa, read from `config/app_features/qa.yaml`)
`blueprint_enabled: true`; `data_analysis_recipe_edit_enabled: true`; `blueprint_agent_enabled: true`; `blueprint_agent.backend: "disabled"`; `testing_mode: true`; `automation.ghost_save.enabled: false`.
Not covered: the draft autosave (ghost save is off). A setup with the agent switch OFF: in `blueprint_handlers.py` line 1683 the function returns when `blueprint_agent_enabled` is off, so everything after it is not registered then (the Joint Designer, groups and plots CRUD, branch, create). The tap, the load and the Save of a component are registered BEFORE that line and so work in both setups, but my browser tests ran only with the switch on. The Joint Designer name fix lives after that line.

## Test counts and runs (one at a time, load under 4)
- `libs/blueprint_arch`: 438 passed.
- Blueprint headless files of `app/tests` (agent_instructions_shape, failed_load, handlers_names, known_defects, node_selection, plot_defaults_form, plot_preview_engine, save_roundtrip, tier_files, widget_forms, wrangler_upload_step_numbering) plus mine (plot_open, tier_refusal, joint_step_name): 167 passed.
- Browser, `app/tests/test_shiny_smoke_blueprint.py`, qa: 21 passed (76 s).
- Picture proof: `error-changed: 1, identical: 50`. The one row is the known `test_logic.yaml` rejection text (it now also names "engines" in the text of the fault), not a picture.

## What I did not check / open
- HOME drawing after a Blueprint plot Save was not run in a browser; the checker AND the engine load accept the saved copy (`validate_data_analysis_recipe`), headless. The refusal was tested headless, not in a browser (the proof run saw the old message in the browser).
- Taps were fired as the page's own event on the node id (nodes overlap at the default zoom); a real mouse click was not repeated.
- The first two browser runs of the 17-plot test did not finish (more than 15 minutes, no result) while the machine ran other sessions' tests; the cause was an `evaluate` on a map that the server was redrawing (a tap makes the server redraw the map). The helper `_tap_node` waits for the map to hold the node; later runs finished (whole file 76 s). I did not find which line blocked, only that this wait removed it; it is a defect of the test, not seen in the app.
- Rule file `rules_app_structure.md` lists the files of `app/modules/`; the two new modules are not in it (I may not touch rule files). The dependency index (`dependency_index.md`) was not regenerated.
- The wording of B is PROVISIONAL and goes to the owner with the texts to approve. The three cases of B, and the question of what Blueprint should do when a tier-2 step meets a tier-1 file, stay open (D-0308).
- Other sessions' test servers were running on the machine; I started and stopped only mine.
