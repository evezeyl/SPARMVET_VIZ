# Report: the rows signature of the filter form (review finding 1, plus findings 2, 3, 6)

Worktree `.claude/worktrees/filter-column-reset`, branch `task/filter-column-reset`, from dev `c21fbdc3`. Head `d7c25828`. Clean, no app running.
New commits on top of `55bcc486`: `d89757ac` fix, `e81a9cde` tests, `15198fd8` whitespace, `d7c25828` dependency index back to dev.
Labels: read = read in the code; ran = I ran it; reasoned = from reading only.

## 1. What decides the rows of the dialog's table (all read)
The form's table is `_dialog_table()` (`filter_and_audit_handlers.py:272`) = `_active_frame()` (`:513`) = the table of the plot, then `dialog_frame` (audited steps in My view only).
1. The collection of the plot: `spec["target_dataset"]` (`home_theater.py:303-323`, `_resolve_active_lf`). No collection: the table is the app's open anchor (`tier1_anchor`, `server.py:153`), which no key of this view describes.
2. The view: Raw reads the stored tier-1 file; Result and My view read `materialize_tier2` (stored tier-2 file; the tier-1 file when the collection has no tier-2 steps) (`home_theater.py:303-323`; `orchestrator.py:324`).
3. The recipe id (input `data_analysis_recipe_id`) and the tier-1 key the open view holds (`_data_analysis_recipe_keys`, `home_theater.py:259-269`).
4. The content key written in the footer of each stored file (`orchestrator.py:21-26`, `anchor.py` `write_anchor`).
5. A table built and returned without being stored (inputs changed during the build): no file carries a key for it (`orchestrator.py` `tell_inputs_changed`, `anchor.py` `still_valid`).
6. The audited steps of the plot, in full and in order, in My view only (`_active_frame` `:524`, `audited_frame`; the function is pure in the nodes: `plot_id` is only used in error text).
7. Exploration filters: NOT an input. `_active_frame` and `_dialog_table` never read `applied_filters` (grep of the handler: only the Apply/Reset/clear code reads it). So I did not add them; the rule of the dialog (rows after audited steps in My view, S2-1 (a)) is unchanged.

## 2. What the signature holds now
- `stored_key(path, meta_key)` (`t3_audit_engine.py:722`): the key from the parquet footer, now, from the file. None if missing, unreadable or without the key.
- `stored_table_identity(tier, collection, recipe_id, view_key, tier1_path, unstored_builds)` (`:732`): `(collection, recipe_id, tier-1 key of the view, tier-1 footer key, tier-2 footer key (T2/T3 only, None when no tier-2 file), count of unstored builds)`. None when there is no collection or no tier-1 key.
- `dialog_rows_signature(table_identity, audit_nodes)` (`:756`): `("rows", identity, canonical JSON of every node)` (sorted keys, list order kept; the whole value list, `na`, `closed`, reason). An identity None, or nodes that cannot be written, gives `("uncovered", object())`: never equal to another call.
- The text of the Polars plan is no longer read at all. The old function is removed (one mechanism). `dialog_schema_signature` is unchanged.
- Handler Effect `_signal_dialog_table` (`filter_and_audit_handlers.py:304`) builds the signature from the identity of the open plot and view (new kwarg `_table_identity(spec, tier)`, replaces `_table_key`) and `_audit_nodes_of(subtab) if tier == "T3" else []`, the same condition as `_active_frame`.
- `home_theater.py:326` `_dialog_table_identity` gathers the pieces; `home_theater.py:177-183` `_unstored_builds` counter, raised in `_tell_inputs_changed`.
- Choice made: I did NOT compute the tier-2 key (`tier2_key(...)`). I read the key from the file footer. Reason (read): `task/engine-keys` changes `tier2_key` to take an engine argument and adds `collection_tier2_key`; a computed key here would break or differ after that merge. The footer is the key the file really carries, whatever the formula. `git merge-tree` of my branch with `task/engine-keys`: no conflict (ran). The constants `TIER1_KEY_META`, `TIER2_KEY_META`, `tier2_path_for` exist there with the same names (read).
- The sentence "never a stale list" is removed. The docstring of `dialog_rows_signature` now says what it does not cover (below).

## 3. Cases a to c, each with its test (ran; all in `app/tests/test_filter_form_survives_rerender.py`)
- (a) Truncated list. `TestRowsSignatureOfTheAuditedSteps`: `test_two_steps_that_differ_only_in_a_middle_value...`, `..._in_the_length_of_the_list...` (first two and last equal; the test first checks that the rows really differ AND that the old plan-text signature is equal, so the defect is reproduced in the test), `na` or `closed` changed, other order, step added or removed. Same steps twice: equal. Raw/Result/My view without steps: equal (the first fix still works).
- (b) Stored table rewritten at the same path. `TestRowsSignatureOfTheStoredTable`: `test_a_changed_tier_2_key_with_the_same_tier_1_key...` (same path, same row count, plan text equal, shown), and the same for a tier-1 footer.
  When it can happen in the app (reasoned from read code): a tier-2 step of the recipe is edited (Blueprint saves the recipe file). The tier-1 key does not contain tier-2 steps (`cache_keys.py` `tier1_material` -> `without_tier2`), so the tier-1 key stays; `materialize_tier2` recomputes and writes `<name>__T2.parquet` at the same path under a new tier-2 key; the row count can stay. Also after a data import or a tier-1 rebuild, the file is rewritten under a new key. The footer key tells in both.
- (c) In-memory frames. `test_in_memory_tables_have_no_identity_so_two_of_them_are_never_equal`, and a table with no key (missing file, file without key, no collection) is never equal to itself. A table returned and not stored: `test_a_table_built_and_returned_without_being_stored_makes_a_new_identity`.
- Also: Raw against Result with tier-2 steps (not equal); Raw and Result without tier-2 steps (equal); changed key of the open view; unreadable footer gives None, no error; steps that cannot be written as text (mixed keys) never equal.
- Real handler, defined with stand-ins (`TestTheFormsEffectInTheRealHandler`): the Effect builds no table and asks for no identity without interactivity; with it, it asks for the identity of the open plot and view; the audited steps are in the signature in T3 only (T1, T2: empty).

## 4. Browser test (qa), `TestTheValueWidgetFollowsTheRows` (ran, passes)
Staged recipe of `test_shiny_step_order.py` (30 rows). The column stays, the rows change:
- list: audit step `score >= 16`; choose `sample_id`: `s1` is not offered, `s30` is, 15 options. Delete the step with its trash button: the same column stays chosen, 30 options, `s1` is back.
- number box: `score` and `>=` stay chosen; the box minimum is 16 with the step, 1 after the delete.
qa flags (read, `config/app_features/qa.yaml:22,35,49`): interactivity_enabled true, t3_sandbox_enabled true, ghost_save off.

## 5. Break-once evidence (ran, all restored; the files are as committed)
- Audited steps ignored in the signature: 5 tests fail (middle value, length, na/closed, order, step added).
- Footer keys not read (constants): 3 tests fail (Raw vs Result with tier-2, tier-2 key changed, tier-1 file rewritten).
- Rows signal frozen in the Effect (`rows = ("frozen",)`): both new browser tests fail (list stays old, box minimum stays 1).
- Gate removed from the Effect: the "no interactivity" test fails. Nodes passed in every view: the "My view only" test fails.
- The old plan-text signature is kept inside the test file only as `_old_plan_signature`, and tests assert it is EQUAL for the three defect cases; so a return to the old method fails the new tests.

## 6. Other findings of the review
- Finding 2 (read, `filter_and_audit_handlers.py:306`): the Effect returns at once when `bootloader.is_enabled("interactivity_enabled")` is off, as `sidebar_filters` and `filter_rows_ui` do. Not changed otherwise (it still runs with the panel closed; cost not measured).
- Finding 3: trailing space removed (`15198fd8`). `git diff --check c21fbdc3..HEAD`: clean (ran).
- Finding 6: `d7c25828` restores `.claude/knowledge/dependency_index.md` to dev's content (no history rewriting; `git diff c21fbdc3..HEAD --stat` no longer lists it). The `@deps` blocks in the code are updated. **The index must be regenerated once after the merges.**

## 7. Runs (ran; one process at a time; load 0.4 to 2.8 before each)
- Headless: 28 files that import `t3_audit_engine`, the handlers or `home_theater` without a browser, plus `test_filter_operators`: 1065 passed (includes `test_dialog_mirror_window`, `test_filter_dialog_after_audit`, `test_filter_dialog_values`, `test_filter_defects`, `test_filter_schema_dtype_wins`, `test_filter_four_way_pickers`). List: `tmpAI/headless_list.txt` in the worktree.
- `test_filter_form_survives_rerender.py`: 37 passed (29 headless, 8 in the browser).
- Browser, qa, once each: `test_filters_cleared_on_recipe_change` 13 passed; `test_shiny_apply_blocked` 1 passed; `test_shiny_filter_value_list` 2 passed; `test_shiny_filter_pickers` 43 passed.
- Ten runs in a row of the race test (`test_the_column_chosen_right_after_a_change_of_view_is_not_put_back`): 10 of 10 passed (19.3 to 21.1 s). The reset did not come back.
- `python -c "from app.src.main import app; print('OK')"`: OK.

## 8. What is not proven or not done
1. Not covered by the signature (also in the docstring): a stored file that another process replaces between the build of the table and the read of its footer (the lazy table keeps the old file open, the footer read sees the new key: the next signature is then different and the form is built once more; the first one can be one render late); and a file edited outside the app that still carries its old key (the key says what the file was built from, not what is in it; the export check works on the same keys). Reasoned, not run.
2. A plot with no `target_dataset` (reads the app's open anchor): identity None, so the signature is never equal and the form is built on every recompute, as before the first fix. I found no shipped plot without it (the recipe rules require it); not searched across all recipes.
3. `_unstored_builds` also rises when a plot (not the dialog) builds an unstored table. The effect is one more render of the form, never a stale list. Reasoned.
4. The remaining race of the first fix (a pick lost right after a REAL change of columns while the server is busy with the plots) is unchanged and not touched; the choice A to D of the earlier report stays open for the owner.
5. I did not run the other browser files, `docs/UML/app.mdj`, or the ADR/UML sync check (a behaviour change for a scribe: checkpoint E4). The rule text `ui_implementation_contract.md` section 14 has no line on the two signals; rule files were not edited.
6. The Effect still computes the table with the Filters panel closed (interactivity on). Not measured.

## 9. Decisions table
| Decision | How the code complies | Where / test |
|---|---|---|
| D-0050 "No silent error: that is the rule" | A doubt gives a never-equal signature (one more render), never a silently old list; an identity that cannot be read is logged and never equal; the docstring says what is not covered. | `t3_audit_engine.py:722-780`; `filter_and_audit_handlers.py:304-330`; the tests of section 3 |
| D-0285 "do not run the same tests that also cost time" | Each file once; repeated only the race test 10 times, as asked. | section 7 |
