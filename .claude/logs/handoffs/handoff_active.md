# Handoff — Active State (2026-05-10 continued session)

**Branch:** dev  
**Working tree:** clean (all changes committed)  
**Status:** Session focus: Audit-driven quick wins. Completed 3 library/dependency tasks.

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
