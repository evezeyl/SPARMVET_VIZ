# Steps 6 and 7 controls, and the join-key edge cases (worker report, 2026-11-18)

Worktree `.claude/worktrees/engine-keys`, branch `task/engine-keys`, start head `5456c3ab`, end head `c0512941`. Nothing uncommitted. No process of mine left running (a `shiny run` on port 8795 seen at the end belongs to the `export-ready` worktree, not to me).

## Commits
- 7537bd83 docs(deps): the dependency blocks name the tier-2 key function, the cache version sweep and the engine record (part A; index regenerated)
- a005a6b8 fix(audit): a restored session does not bring back a step that drops a join key (part B: code and tests)
- c0512941 docs(deps): the dependency index names split_key_drops and key_drop_notice

## PART A: controls of steps 6 and 7 (nothing was broken; no code fix needed)
Interpreter: main `.venv`, `utils.__file__` printed: the worktree's `libs/utils/src/utils/__init__.py`. Load was 1.5 to 3.8 before every run.

| Run | Result |
|---|---|
| `libs/utils` | 2125 passed |
| `libs/transformer` | 2270 passed |
| `libs/viz_factory` | 2286 passed, 27 xfailed |
| qa `app/tests/test_export_download.py` (holds the new `engines` assertion, never run before) | 9 passed (358 s) |
| qa `app/tests/test_shiny_smoke.py` | 37 passed, 3 skipped |
| qa `app/tests/test_shiny_session_restore.py` | 1 passed (also re-run after part B: 1 passed) |

Proofs:
- Pictures: `identical: 50`, one `error-changed` row: `test_logic` (the empty orphan `experimental/test_logic.yaml`), stored text "the recipe check did not cover: actions, components", now "... actions, components, engines". This is the expected change since step 5; no other difference. The script prints "PICTURES NOT IDENTICAL" and exits 1 because of that one row.
- Golden: `result-identical` (exit 0). What it compares: per table the row count, the ordered columns with types and a hash of the content; NOT the keys of the stored tables. So step 6 (keys) cannot move it; it did not.
- Gallery previews: `identical: 34; size only: 0; differs: 0; new: 0; error: 0`.
- Output of these: `tmpAI/runs/ctl_*.txt` and `tmpAI/proof_ctl/` in the worktree.

`@deps`: the orchestrator block now names `collection_tier2_key` (and `ENGINE_CACHE_VERSION`); export_handlers names `collection_tier2_key`; bootloader names the cache-version sweep, `remove_tables_of_other_version` and `take_stored_tables_notice`; engines.py and recipe_tiers.py name `engine_record.py` and `cache_keys.py` as consumers; checked_plot.py names `plot_config_resolver` (for `applied_theme`); engine_python_plotnine.py names `checked_plot`; engine_registry names export_handlers as consumer of `record_of`. Index regenerated twice (after A, after B) with `build_dep_graph.py --root <worktree>`.

Not done in part A: nothing of what was asked. Not run (as told): the full `app/tests`.

## PART B: join keys

### Which columns are keys (verified)
`extract_primary_keys` (`session_manager.py`) = the union of `key_columns(step)` over every join step (`polars_join`, `polars_join_asof`, `modif_join_where`) of `joins.*.tier1.steps` and `tier2.steps`. `key_columns` returns `on`, or `left_on` and `right_on`, and the `by` groups of an as-of join. It agrees with section 12g.2 of the contract.
- Join on two columns: both are keys (test).
- `left_on` and `right_on` with different names (demo recipe: `VF_gene` / `Gene_name`): BOTH names are keys, also the name that only the right table has. Demo keys: `Gene_name, VF_gene, sample_id`. A column used in `by` of a group step or `on` of an unpivot is not a key.
- No joins, or no join key known: the list is empty and nothing is refused.

### Table of the places where a column drop is created or enters
| # | Place | Code | Key rule before | Key rule now | Test |
|---|---|---|---|---|---|
| 1 | Column box of the data preview, "drop via audit" | `filter_and_audit_handlers._col_drop_to_audit` (the ONLY place that creates a `drop_column` step; a scan test checks it) | refuses | refuses (unchanged) | `test_audit_join_key_drops.py`, `test_home_join_keys.py` |
| 2 | Propagation dialog ("this plot / all / all except") | `_handle_propagation_confirm` | not applied; carries the steps made at 1, creates none | unchanged: carries (reasoned + test of the carry) | `test_the_dialog_carries_the_non_key_drop...` |
| 3 | Audit panel Apply | `audit_stack.handle_apply` | not applied; commits the pending steps of 2, creates none | unchanged: carries | scan test (no second creator) |
| 4 | RESTORED session | `session_handlers._restore_session` | NOT applied: the stored key drop went into the view and the key was dropped in silence | refused step by step, rest restored, user told (part B fix) | 4 tests on the real session screen |
| 5 | IMPORTED session zip, then restored | `SessionManager.import_session_zip` only unpacks (it refuses unknown step types, not key drops) then place 4 | as 4 | as 4 (the import keeps the file as it is; the refusal happens at Restore) | `test_an_imported_session_zip...` |
| 6 | Imported reproducibility bundle | `bundle_importer.import_bundle` | writes a frozen recipe and an assembly ghost, no audit steps of the app (the audit is already translated into the recipe's tier-2 of a fork, `t3_translator`); refuses unknown step types | unchanged; a drop of a key written into a recipe is a recipe step, the recipe check decides | reasoned (read), not tested |
| 7 | Export | `t3_audit_engine.audited_frame` (and `export_handlers` through it) | applies the steps it is given, no key knowledge | unchanged; after the repair the list cannot hold a key drop (1 and 4 refuse it) | pinned: `test_the_export_and_the_view_apply_the_steps_they_are_given...` |

### Tests (new file `app/tests/test_audit_join_key_drops.py`, 27 tests, all pass; plus the 7 of `test_home_join_keys.py`)
(a) refusal where a drop is created: composite key, either column refused (2); two-name key, each name refused (2); the scan "only one place creates a column drop".
(b) non-key drop still works: next to a composite key it goes to the dialog; several non-key columns at once; the dialog carries it to the pending list of all plots (shared id).
(c) composite key: above. (d) key on one table only (two names): above, also a filter on either name carries the warning, a filter on another column does not.
(e) several columns at once with one key among them: what the code does (NOT changed, reported): the WHOLE drop is refused, the message names only the key, and the non-key columns of that click are not sent to the dialog. Pinned by `test_several_columns_at_once_with_one_key_among_them_refuse_the_whole_drop`.
(f) restored and imported session holding a key drop: see below. Plus 6 tests of the pure `split_key_drops` (order kept, argument unchanged, no keys, propagated copies, a style step kept, a switched-off step also refused).

Break-once (`tmpAI/breakonce_keys.py` in the worktree, edits reversible by writing the saved text back; 7 of 7 caught, output `tmpAI/breakonce_keys_out.txt`):
K1 split keeps key drops (fails `test_split_removes_only...`); K2 Restore does not call the split (fails the restore test: this is the state BEFORE the repair); K3 Restore restores nothing when one step is refused (fails); K4 column box does not refuse (fails the two-column test); K5 keys do not read the right-hand names (fails `test_a_join_with_two_names...`); K6 a second place that creates a drop (fails the scan); K7 the notice leaves out the user's reason (fails).

### A restored or imported session that holds a key drop: before and after
- Before (verified by K2, which restores the old behaviour): the stored `drop_column` on `sample_id` went into `t3_audit_steps_by_plot` as it was; the view applied it (`audited_frame` drops the column); no message. A plot or table that uses the key then fails or shows no key. Silent.
- After: the step is left out for every plot, the other steps (filters, other drops, style steps) are restored in their order, and one warning (15 s) says which step, in which plots, the reason the user wrote and why. The saved file is not changed (test). The keys are those of the open recipe (`home_state["primary_keys"]`); if none is known nothing is refused and nothing is said (pinned, see decisions).
- It is smallest: one pure function `split_key_drops` and one text function `key_drop_notice` in `session_manager.py`, five lines in `_restore_session`. No new dialog, no change of the session format.

### Texts a user sees in these cases (all PROVISIONAL for Eve; none was changed)
1. Column box, key drop (existing, error, 8 s): "Cannot drop join key column(s): <names>. Use a row filter or row exclusion instead." (with a stop-sign icon in front). The contract text (12g.3) is "Column [c] is a join key, cannot be dropped. Use a row filter or row exclusion instead."
2. Propagation dialog, when a FILTER on a key is sent (existing, yellow box): "One or more nodes target a join key. Removing rows here changes which samples appear in joined plots."
3. Audit panel card of a filter on a key (existing): "Primary key - Primary ID/Key alignment" (with a warning icon).
4. NEW, restore (warning, 15 s, with a warning icon): "N step(s) of the saved session were not restored: dropping the column sample_id (plot subtab_p1, subtab_p2, your reason was: "not needed"). A join key column cannot be dropped through the audit, because the tables are joined on it. The other M step(s) were restored. Suggestion: use a row filter or row exclusion instead; the saved file is not changed". Weak points of the wording: plots are shown by their internal id (`subtab_p1`), not their label; "N step(s)" counts decisions, a decision propagated to several plots counts once.
5. Existing after a restore: "Session restored (<time>). K save(s) available for this batch." (unchanged, still shown after text 4).

## What needs a decision (not decided by me)
1. Restore refusal vs the rule "a step the app cannot apply is refused, and the file is refused AS A WHOLE" (`renamed_keys.refused_audit_step_problem`, for unknown types, removed types, missing columns; used for a stored session, an imported zip and a bundle). The brief asked for the other rule for a key drop: tell which step, restore the rest. I built that. The two rules now differ for two kinds of defective step. Options: (a) keep as built; (b) make the key drop a defect of the whole-file kind (needs the keys in `audit_step_defect`, which has none today, and the file is then not restorable at all); (c) change the other defects to the step-by-step way. I recommend (a) for now and a decision before the audit redesign.
2. No key known when restoring (a recipe without joins, or `primary_keys` not read yet): nothing is refused and nothing is said. Pinned by a test so that a change is a decision. Option: refuse to restore key-sensitive steps until the keys are known, or tell the user that the keys could not be checked.
3. The export and the view (`audited_frame`) do not know the keys and apply any `drop_column` they are given. Safe today because nothing can put a key drop in the list any more (places 1 and 4). A defence inside `audited_frame` needs the keys as an argument for all callers (more than small). Not built.
4. Several columns at once with one key (e): the whole drop is refused. Option: send the non-key columns on and refuse only the key; not changed, as asked.
5. The filter on a key stays allowed with a warning (AUDIT-1, existing, not touched).
6. A restore with the recipe changed (the session was saved against another recipe): the keys of the OPEN recipe are used, as the steps are applied to the open recipe. Say if you want the keys of the saved recipe too (not stored in the session).
7. Wording of text 4 and the choice between the two contract texts (point 1 of the list above).

## Not run
Full `app/tests` (as told); the other browser files (`test_shiny_smoke_blueprint.py`, `test_every_app_features_starts.py`, gate gap, filters cleared); `libs/blueprint_arch`, `libs/test_lab`, `libs/viz_gallery` (part A named only utils, transformer, viz_factory). Run after part B: the new file (27), `test_home_join_keys`, `test_session_manager`, `test_session_clicks_once`, `test_session_errors_visible`, `test_session_unreadable_files_told`, `test_home_reads_the_plot_entry` (112 passed together) and 8 files that write or read T3 ghosts and sessions (148 passed), and the browser `test_shiny_session_restore` (1 passed).
