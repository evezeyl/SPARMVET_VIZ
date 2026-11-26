# Slice B, the screen piece (builder report, digest by the coordinator, 2026-11-20 09:06 by the clock)

Branch `task/slice-b-home`, worktree `.claude/worktrees/slice-b-home`. Builder's head `53ff8b60`; with dev merged in: `56448279` (the head under review and control). 56 files, about 2200 lines added against dev `89e19e61`.

## What the user sees
- Header strip (only with interactivity): **Mode: Exploration | Audit** (only with the audit flag), **Table to view: Source | T1 | T2 | T3** (starts on T3), **Source table** (a list, only while Source is chosen), and in Audit mode a **Compare** switch and the line "Audit steps apply to the plot's table (T3) for now."
- Exploration: one plot per tab, the Result, never changed by a filter. The data table shows the chosen table. Filters are built on that table, change only it, and are removed with a notice when the table viewed changes (data choice, source table, plot tab, mode, recipe). No "Send to Audit", no column drop.
- Audit mode: the audited plot; Compare on = "Original" and "Audited" side by side; T3 = the audited table; Source, T1, T2 = the originals; no preview Apply; "Send to Audit" and the column drop only while T3 is viewed ("To create an audit step, view T3."). The dialog, the pending steps, the reason gate and Apply are as before.
- Setups: developer, qa, standalone, advanced: data choice and mode switch. simple, web-demo: data choice, no switch. static, demo-vetinst: no strip.
- A restored session with audit steps opens Audit mode (limit: restoring the SAME file twice does not switch again; a one-line hook in `session_handlers.py` near 642 would make it exact).
- Export: content unchanged; README line `Screen view      : Exploration mode, data view T3` replaces `Active tier      : ...`.

## Texts a user reads (provisional; for the owner in the app)
Labels "Mode:", "Table to view:", "Source table:", "Compare:" ("the original and the audited plot side by side"); mode sub-labels "look at the data; nothing is saved" / "create audit steps"; data sub-labels "as read from the file", "after tier 1", "after tier 2", "the table the plot shows"; Filters panel "Exploration: filters change this table only, never a plot. Nothing here is exported." / "Audit: a step you send changes the plot and is exported."; badges "Viewing: Source | T1 | T2 | T3 | T3 (audited)", "Plot: Result", "Plot: Audited"; the clearing notice "The filters were removed because {cause}. A filter is built on the table you view, so it is not kept when that table changes. Audited steps are kept." with five causes; the old-session notice "This session cannot be recorded yet: an older session with the same recipe and data is stored. Open the Session panel and delete the session marked as saved by an older version, then change the recipe or data box again."

## Provisional choices (P-B1 to P-B7 of the plan, built as written) and the builder's own
1 `audit_compare` kept in a value local to the handler; 2 source reads remembered (8 entries) per recipe, table and data hash; 3 the form's identity for a source table; 4 "Table to view:" replaces "Data to show:"; 5 Audit mode with the audit flag off behaves as Exploration; 6 a Source error shows plain text and an Alerts entry; 7 two causes at once: the notice names the first of recipe, mode, data, source table, plot; 8 **the static setup (no strip) shows T3 in the data table where it showed T2** (same table unless a plot has its own tier 3 steps); 9 staged rows in Audit mode wait to be sent; a mode switch removes them with the notice.

## Tests (builder RAN)
New headless: `test_home_view_choices.py` 25, `test_filters_cleared_on_view_change.py` 13, `test_view_change_clears_filters.py` 12, `test_export_unchanged_by_the_view.py` 3, `test_no_old_view_readers.py` 15, `test_session_record_notice.py` 2; new browser `test_home_modes_browser.py` 7. Adapted: about 20 files. Removed: three old "My view" badge cases and two badge tests whose subject is gone (replaced). Headless set of 49 files: 1500 passed, 4 skipped, 1 failed then fixed. Browser files run one by one under qa: all passed (smoke 37 passed, 3 skipped). Twelve breaks seen failing. NOT run by the builder: the whole headless suite, all browser files.

## Findings of the builder, not decided
- The right sidebar's "Active Filters" list shows exploration filters beside audit steps; in Exploration the heading over-promises.
- A docstring in `orchestrator.py:486` and a comment in `session_manager.py:513` still say "My view" / `tier_toggle` (not its files).
- `docs/appendix/data_lifecycle_theater.qmd:24`: a caption from a UML diagram says "My view" (needs the diagram redone).
- Out-of-date sentences: `ui_implementation_contract.md` (about 40 lines listed), `rules_ui_dashboard.md:72`, `rules_app_features_flags.md` 41-60, `rules_app_structure.md:92`, `rules_verification_testing.md:165`, ADR text 4090-4222 and 5022-5083 and others, the HOME design files, and the UML wireframe UI-HOME and SEQ-AUDIT. All need the owner's yes (rule and ADR) or a UML pass.
