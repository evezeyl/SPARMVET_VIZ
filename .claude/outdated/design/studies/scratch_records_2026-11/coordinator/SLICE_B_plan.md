# Slice B plan: two modes on screen; Exploration is clean (coordinator, 2026-11-20 07:45 by the clock)

Base: dev `3d4dcdda`. Slice text: `tmpAI/panel/audit_redesign/SLICES_v3_2026-11-18.md` 41-51. Facts: `SLICE_B_facts_view_choices.md` (this folder) and the session survey (below).
Decided (ledger): D-0310 (data choice Source, T1, T2, T3; plot with tier 3 steps drawn from the T3 table), D-0311 and D-0178 (exploration filters reset when the viewed tier changes), D-0312 (old session files refused, removed), D-0018 (audit needs comparison, sessions, export; comparison needs audit), D-0019, D-0179, D-0180 (one plot in Exploration, no "My view", no plot selector), D-0147 (Compare shows original and modified), D-0177, D-0284.

## Pieces
- **B-1a, the Source reader** (builder, sonnet/medium; worktree `slice-b-source`, branch `task/slice-b-source`). `app/modules/orchestrator.py` only (+ tests): read one source table as loaded with its declared types, before any tier-1 step; list the source tables that feed a plot's table (from `utils.recipe_graph`). Nothing stored. No screen.
- **B-1b, flags and sessions** (builder, sonnet/medium; worktree `slice-b-flags-sessions`, branch `task/slice-b-flags-sessions`). (1) The start check refuses audit without comparison, sessions or export, and comparison without audit (D-0018); the shipped setup with that pair is corrected. (2) Session files: a format number written and compared; a file of an older format is refused with a plain line, never converted (D-0312); the view value leaves the session file. Files: `app/modules/app_features_validator.py`, `config/app_features/*.yaml`, `app/modules/session_manager.py`, `app/modules/renamed_keys.py`, `app/handlers/session_handlers.py`, `app/handlers/audit_stack.py` (the one write), `app/modules/bundle_importer.py`, tests, user docs.
- **B-2, the screen** (builder, sonnet/high; worktree `slice-b-home`, after B-1a is merged). `app/handlers/home_theater.py`, `filter_and_audit_handlers.py`, `export_handlers.py`, `app/modules/view_badge.py`, `t3_audit_engine.py`, `orchestrator_helpers.py`, `app/src/server.py`, help text, user docs, the 40 test files. The switch "Exploration | Audit" (only with the audit flag); the data choice of four values with the second list for Source; one plot in Exploration; filters change only the viewed table and reset with a notice; Audit mode with Compare on/off; a test that no code reads the old choices.
- Each piece: a reviewer on the diff. After B-2 merged: full headless once, all browser files, eight setups start, golden, pictures.
- **After the merge: the old session files are removed** by a builder, session files only. The list is below; the owner sees it first (my report of 07:45).

## PROVISIONAL choices of the coordinator (not the owner's; each goes to the questions list)
- P-B1. The data choice starts on T3 (the table the plot shows; HOME design line 37). Today it starts on "Result" = tier 2.
- P-B2. Changing the plot or the Source table also resets the exploration filters (it changes the table viewed; D-0178).
- P-B3. In Audit mode until slice C: "Send to Audit" and the column drop are offered only while T3 is viewed (the old dialog writes at the plot's table only). T1, T2 and Source show the original tables in Audit mode.
- P-B4. In Audit mode the filter form has no preview "Apply"; it only sends to the audit (D-0177: in audit the filters are defined and applied).
- P-B5. The session file no longer holds a view value (the value saved today is not the choice on screen). A restored session with audit steps opens Audit mode.
- P-B6. The export record line "Active tier" becomes the mode and the data choice.
- P-B7. Names in the code: the inputs `home_mode`, `data_view`, `source_table`, `audit_compare`; the reader `read_source`.

## Old session files on disk (scout, READ only; nothing tracked by git; no test fixture)
Hers (the shipped setups' user folders): `tmp/UI_TEST/user/_sessions/` 11 sessions; `tmp/pipeline_test/user/_sessions/` 4; `tmp/DEMO/user/_sessions/` 2.
Agents' scratch under `tmpAI/` (76 sessions): `panel/verification/scratch4b/**/_sessions/` 25; `panel/verification/scratch_h1/copy/tmp/UI_TEST/user/_sessions/` 2; `panel/export_box/worktree_evidence/browser_*/user/_sessions/` 6; `switch_check/review/scratch/copy/tmp/UI_TEST/user/_sessions/` 3; `panel/label_trace/copies/user_*/_sessions/` 9; `engine_keys/bp_proof_dev/root/tmp/user/_sessions/` 8; `browser_{filter_pickers,filter_value_list,plot_errors,plot_warnings,step_order,typed_values}/user/_sessions/` 12; `browser_state/gw{0,1,2}/user/_sessions/` 6; `coordinator/tier3_fix_review/mut/tmpAI/browser_plot_tier3/user/_sessions/` 1.
Held worktree `one-python`: 4 sessions under its `tmp/`: NOT removed (the worktree is held for the owner).
Never touched: `anchors/`, `_blueprint_drafts/`, `_imports/`, `parquet_data/`, recipes, data.
Each session folder holds only `assembly.json` and `t3_*.json`.
