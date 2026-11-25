# Handoff: active state (last update 2026-11-25)

Branch `dev`, not pushed; the owner pushes. Start here: the section OPEN STATE below; one-screen state in `tmpAI/coordinator/progress_2026-11-25.md`; older blocks in `.claude/logs/handoffs/archive/handoff_archive_2026-11-25.md` (a local file: that folder is git-ignored).

## OPEN STATE 2026-11-25, at the close of coordinator session sparmvet-viz-98 (3ce2c163) — READ THIS FIRST

1. **Git.** `dev` head is the closing record commit after `09db4e42`. Not pushed; the owner pushes. Agents never push. Ledger runs to D-0637.
2. **Done 2026-11-24 and 2026-11-25** (merges `80443853` and `578d69d2`, decisions D-0618 to D-0637):
   - typed values trimmed (D-0626); NOT DETECTED in `amr_heatmap` (D-0623); id-less lines removed from `demo_abromics` (D-0624); `left_join_lesson` deleted (D-0625);
   - T1 and T2 views show the audited tables in Audit mode; the audit recipe runs on its own (D-0622);
   - lineage data function `libs/utils/src/utils/lineage_data.py` and the panel "Path of the data" in HOME, Audit mode (list plus dots, mock-up G; D-0629 to D-0631; PROVISIONAL words and colours);
   - the metadata is not an audit place (D-0632); recipe checks J16, J17, S10 (D-0633, D-0636, D-0637); `figshare_integration` declares `metadata_schema`.
   - Records: `406c1bbc`, `09db4e42`; the lineage research in `.claude/design/studies/lineage_scope_2026-11/`.
3. **Running:** nothing.
4. **Branches not merged (parked):** `study/whole-picture-goals`; `task/audit-slice1-effects-log` (wip `42d5ae6d`, partly superseded by the places build); `task/blueprint-duplicate-id` (BLUEPRINT held); `task/one-python`; `task/plot-id-across-recipes`; `task/remove-from-all-ticked`; `trial/axis-text`, `trial/default-ticks`, `trial/formula-d`, `trial/path-check`, `trial/stat-function-polars`. Whether each is still wanted: not checked.
5. **Waits for the owner, in this order:**
   1. Her manual test of HOME (the panel "Path of the data"; screenshots in `tmp/2026-11-25/lineage_view_G/`) and her push of `dev`.
   2. Open points (tasks in `tasks.md`): LINEAGE-OLD-SESSION-META-STEP; LINEAGE-STEP-AT-TABLE-NO-PLOT-LISTING; LINEAGE-SMALL-FORM-TYPES; LINEAGE-INCOMPARABLE-PLACES; HOME-MODE-SWITCH-SCROLL; METADATA-NO-JOIN-LISTS-IT (not decided, D-0637); EQUALITY-DIRTY-DATA-GENERATOR; the panel's words and three tier colours (PROVISIONAL); row order of `figshare_integration` (to confirm).
   3. The files she changed herself, still uncommitted (she decides): `CLAUDE.md`, `.claude/hooks/coordinator_guard.py`, `.claude/agents/panel-*.md`, `.claude/workflows/agent_dispatch_howto.md`, `.vscode/extensions.json`.
   4. Older: HOME-TABS-DRAWN-TWICE; AUDIT-ONE-FAILING-STEP-BREAKS-ALL-PLOTS; REMOVE-FROM-ALL-MISSES-TABLES; AUDIT-RECIPE-BESIDE-ORIGINAL; DATA-IMPORT-OVERWRITE.
6. **Next step for a new session:** UML: the 5 stale tags of `audit_uml_model.py` and the new panel (LINEAGE-UML-SYNC). Then the open points above, as she decides. BLUEPRINT held. Test Lab left alone (D-0637).
7. **Standing notes:**
   - BLUEPRINT held; Test Lab left alone (D-0637).
   - Incident: one builder ran `pkill -f "shiny run app/src/main.py"` once; it may have stopped another session's app; no file affected. Briefs must forbid `pkill -f` and `pgrep -f`.
   - Test state at close: app headless 5959 passed, 0 failed; browser run before the last three commits 534 passed, 3 failed (two load-sensitive, passing alone; one fixed in `25b5116c`), not rerun in full. `audit_uml_model.py` FAILS (5 stale tags). `audit_old_words.py --check` fails since before.

## EVERYTHING STILL OPEN at the close of 2026-11-25 (one list; each item says where its detail lives)

1. The owner's manual test of HOME: the panel "Path of the data" (Audit mode). Screenshots: `tmp/2026-11-25/lineage_view_G/`; mock-ups: `tmp/2026-11-24/lineage_mockups/`.
2. The owner's push of `dev` (agents never push).
3. Four tasks that say they wait for the owner while a ledger line names them (detail: `tmpAI/records/possible_contradictions.md`). Each: decided by a ledger line; task to close or reword; the owner to confirm. Only the titles were read, nothing more is judged:
   - DATA-IMPORT-OVERWRITE: decided by ledger lines D-0432 (HOME Data Import: replacing a data file, option B) and D-0434 (same subject, "decided"); task to close or reword; the owner to confirm.
   - TESTLAB-REVIEW-1: decided by ledger line D-0396 (TEST_LAB: a review to plan its rebuild); task to close or reword; the owner to confirm. Note: D-0637 says Test Lab is left alone.
   - BLUEPRINT-REMOVED-BUTTON-AND-HINT-1: decided by ledger line D-0305 (the button "Add plot wrangling" points to tier 3); task to close or reword; the owner to confirm. Note: BLUEPRINT is held (D-0636).
   - AUDIT-REMOVE-FROM-ALL-DATA: decided by ledger lines D-0498 to D-0501 (HOME audit, "remove from all the data": the table with a column of the key's name, untick and responsibility, what counts as the key, no warnings about natural consequences); task to close or reword; the owner to confirm.
4. 80 items marked done whose own text says something is open: `tmpAI/records/done_but_not_finished.md`.
5. 44 open tasks without a model/effort tag: `tmpAI/records/open_items.md` (lines marked `tag=NO`).
6. Eleven parked branches, to keep or delete (the owner decides; not checked which are still wanted): study/whole-picture-goals, task/audit-slice1-effects-log, task/blueprint-duplicate-id, task/one-python, task/plot-id-across-recipes, task/remove-from-all-ticked, trial/axis-text, trial/default-ticks, trial/formula-d, trial/path-check, trial/stat-function-polars. Worktrees (`git worktree list`, 2026-11-25): `.claude/worktrees/formula-d`, `.claude/worktrees/one-python`, `.claude/worktrees/path-check` (inside the main tree); beside it `../SPARMVET_VIZ_wt_audit_s1`, `../SPARMVET_VIZ_wt_bp_dup`, `../SPARMVET_VIZ_wt_goals`, `../SPARMVET_VIZ_wt_id_across`, `../SPARMVET_VIZ_wt_remove_ticked`, `../SPARMVET_VIZ_wt_ticks_trial`; and `/home/evezeyl/work/SPARMVET_VIZ_retest` (detached HEAD e509c330). Another session may be cleaning branches (order M690).
7. Two failing audits: `assets/scripts/audit_uml_model.py --project-root .` (5 stale tags: 3 cite ADR-098; `_clear_filters_on_recipe_change`; `test_audited_rows_and_drops_are_exported`) and `assets/scripts/audit_old_words.py --check` (fails since before merge 578d69d2).
8. The table `figshare_triple_join` of `figshare_integration`: same content, other column and row order after D-0636 (golden records renewed, commit f47d52bc in merge 578d69d2); accepted by the coordinator; the owner to confirm.
9. The lineage tasks in `tasks.md`: LINEAGE-OLD-SESSION-META-STEP, LINEAGE-STEP-AT-TABLE-NO-PLOT-LISTING, LINEAGE-SMALL-FORM-TYPES, LINEAGE-INCOMPARABLE-PLACES, LINEAGE-UML-SYNC, HOME-MODE-SWITCH-SCROLL, METADATA-NO-JOIN-LISTS-IT, EQUALITY-DIRTY-DATA-GENERATOR; the words and the three tier colours of the panel are PROVISIONAL.
10. Files changed by the owner, not committed, hers to decide: `CLAUDE.md`, `.claude/hooks/coordinator_guard.py`, `.claude/agents/panel-*.md`, `.claude/workflows/agent_dispatch_howto.md`, `.vscode/extensions.json`.
11. Older open tasks (in `tasks.md`): HOME-TABS-DRAWN-TWICE, AUDIT-ONE-FAILING-STEP-BREAKS-ALL-PLOTS, REMOVE-FROM-ALL-MISSES-TABLES, AUDIT-RECIPE-BESIDE-ORIGINAL, DATA-IMPORT-OVERWRITE.
12. The scratch sort of 2026-11-25: `tmpAI/trash_2026-11-25/TRASH_LIST.md` (the owner empties the trash), `tmpAI/KEEP_LIST.md` (what stays and what is unclear).
13. The handoff archive folder is git-ignored (`.gitignore` line 71): to track it or not is the owner's choice.
14. One test failed once while agents changed files in the tree: `app/tests/test_migrate_display_names.py::test_the_dry_run_on_the_real_tree_changes_no_file`; a reviewer reruns it on the quiet tree at the end of this round (the result is in the coordinator's closing message).
15. `tasks.md` is about 494 KB with 483 open items: a full pass needs a session with the owner (task RECORDS-TASKS-FULL-PASS).


**Weekly line (coordinator, week of 2026-11-23):** coordinator model Fable; quota at start and end: not known. Work: merges `80443853` and `578d69d2`, and the records. Mistakes the checks caught: golden records not renewed after a recipe change (caught by the reviewer's full run); a browser test that compared a screenshot cut by the scroll position (caught by the browser run); 28 failing tests after the metadata stopped being a place (caught by the first review); a headless run that ignored too many files (caught, rerun after the merge).

**The older blocks (everything dated before 2026-11-25) were moved unchanged on 2026-11-25 to `.claude/logs/handoffs/archive/handoff_archive_2026-11-25.md`.**

- 2026-11-25, after merge 578d69d2 (detail): on `dev` now: the lineage data function `libs/utils/src/utils/lineage_data.py`; the panel "Path of the data" in HOME, Audit mode, collapsed, list plus dots (`app/modules/lineage_view.py`, `lineage_step.py`, `app/handlers/lineage_handlers.py`, `app/src/www/lineage_view.js`); the metadata is not an audit place (D-0632); recipe checks J16, J17, S10 (D-0633, D-0636, D-0637); `figshare_integration` declares `metadata_schema`, its table has the same content with another column and row order, golden records renewed; remove-from-all leaves the metadata alone. `dev` is NOT pushed (the owner pushes). Screenshots for her: `tmp/2026-11-25/lineage_view_G/`. All words and the three tier colours of the panel are PROVISIONAL. Open tasks: LINEAGE-OLD-SESSION-META-STEP, LINEAGE-STEP-AT-TABLE-NO-PLOT-LISTING, LINEAGE-SMALL-FORM-TYPES, LINEAGE-INCOMPARABLE-PLACES, LINEAGE-UML-SYNC, HOME-MODE-SWITCH-SCROLL, METADATA-NO-JOIN-LISTS-IT, EQUALITY-DIRTY-DATA-GENERATOR. Load-sensitive browser tests (pass alone): `test_opening_browser.py::test_while_a_recipe_opens_the_previous_recipe_is_not_on_the_screen`, `test_shiny_step_order.py`, two tests of `test_shiny_seed_places.py`. `assets/scripts/audit_old_words.py --check` fails on `dev` since before this merge; `app/src/server.py` is above its line limit since before.
- 2026-11-25: after the build for the demo (NEWEST; RESTART FROM HERE): dev head `80443853`, NOT pushed (the owner pushes). The ledger runs to D-0628 (commit `f3b9298e`).
  A. Merged 2026-11-24/25 (merge `80443853`). Review: non-browser app suite 5775 passed; 4 browser files 20 passed. The builder's run: libs 8780; all 52 browser files 528 passed.
  - Typed values trimmed (D-0626).
  - The category NOT DETECTED in `amr_heatmap`, as a tier-3 step of the plot (D-0623).
  - The three lines with no usable id removed from the metadata of `demo_abromics` (D-0624).
  - The template `left_join_lesson`, its data and its test deleted (D-0625).
  - In Audit mode the T1 and T2 views show the audited tables (D-0622).
  - An export made in Audit mode writes `audit_recipe/<id>_audited.yaml`: the original recipe with every audit step at its place and its reason in the step's comment; it runs on its own (D-0622).
  - A plot whose recipe has its own tier-3 steps gets its `T3_data_<plot>.tsv` in every export. README and report say whether a file is after the recipe's own steps or after the audit steps (D-0623).
  B. RESEARCH DONE, waiting for the owner: the complete lineage in HOME, to choose the scope of an audit step. Files in `tmpAI/panel/lineage_scope/`: `01_architect.md`, `02_data_scientist.md` (its headline is withdrawn by `05_review_of_test_logic.md`), `03_user.md`, `04_possibilities.md` (package survey; licences and sizes NOT verified online), `05_review_of_test_logic.md`, `TABLE_FOR_THE_OWNER.md`. Eight clickable mock-ups: `tmp/2026-11-24/lineage_mockups/index.html`. She looks at the mock-ups and chooses the skeleton. Nothing is built. These files are scratch: they move to `.claude/design/studies/lineage_scope_2026-11/` when she has chosen.
  C. Findings of `05_review_of_test_logic.md` that stay open: (1) the library option "remove from all the data" (`libs/utils/src/utils/remove_from_all.py`), run without the engine's plan, reaches only 17 places and misses MLST, VirulenceFinder, Summary and Detailed_summary; its own list breaks the rule of places; it is on no screen today. (2) The lineage must show each parent's role in a join (starting table, right-hand side, look-up); the graph does not hold it. (3) After a removal at ResFinder, a figure that left-joins ResFinder shows the entity with an empty status, while a completed entity shows "Not Found".
  D. WAITING for her choice of the lineage: an audit step at a result table with no plot (D-0627).
  E. For the owner (provisional choices of this merge, her decision):
    1. the NOT DETECTED tiles are grey, with a legend entry "nan" (the fill is the predicted phenotype, empty for them);
    2. the audit recipe is one file, `<id>_audited`, written only in an export made in Audit mode;
    3. a step that removes nothing still makes its table count as audited in the view badge;
    4. the reason typed in the audit panel is not trimmed;
    5. no notice yet when a step removes no row or every row;
    6. "fill empty values" is not added to the closed list of step readings (D-0351): her choice;
    7. dropping `<id>_audited.yaml` beside the original in the recipes folder gives two recipes with the same plot ids, and the app does not warn (the rule file says plot ids are unique across recipes);
    8. a failing tier-3 step shows its error also in the T1 and T2 views of the plot's table.
  F. Not built, decided earlier: the original recipe beside the audit recipe in the bundle; the audit log beside it (D-0478); the hash of the audit recipe in the run file.
  G. Worktrees merged and removable: `../SPARMVET_VIZ_wt_names`, `wt_entity_id`, `wt_ids`, `wt_warn`, `wt_audit_places`, `wt_dialog_path`, `wt_small`. Held, not used: `wt_audit_s1`.

Older blocks are in this archive file: .claude/logs/handoffs/archive/handoff_archive_2026-11-25.md
