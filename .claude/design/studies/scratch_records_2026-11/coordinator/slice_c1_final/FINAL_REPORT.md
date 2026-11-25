# Slice C piece 1, final review and control of head f3efe931 (worktree slice-c-audit-form)

Scope: `git diff 36943b4b..4836eeff`, `f3efe931`, merge `4fc3df7a`. Python: main `.venv`; pytest uses the worktree libs (proved: `where_pytest.out`);
bare python used `PYTHONPATH=<worktree>:<every worktree libs/*/src>` (`pp.sh`). Dev baseline = `git archive 3bfb0050` extracted to `dev_src/`
(the main checkout is at c59efc43, newer, so it was NOT used as "dev"). All files in this folder.

## VERDICT: merge after fixes (one red test; one low finding, three notes)

### Findings by weight
1. HIGH (gate): headless suite is RED, 1 failed. `app/tests/test_browser_tests_no_venv_path.py::test_no_test_file_builds_a_path_into_venv` fails on
   `app/tests/test_tier_steps_one_reader.py:27: SKIP_PARTS = {"tests", "build", ".venv", "__pycache__", "node_modules"}` (pattern `["']\.venv["']\s*[,/)]`).
   Cause: the guard came in with slice B (dev d2a71f11, in dev 3bfb0050); this piece's new test file was written before that merge and the merge `4fc3df7a` did not
   re-run it. It is a string constant (not a process path); fix in the piece: write the set so that `".venv"` is not followed by `,` `/` `)` (for example put it last,
   `..., ".venv"}`), or ask the owner of the guard. Not fixed here (I do not edit). Output: `headless.out` lines 182-208.
2. LOW (a): the verdict of the engine guard is kept once per copy and NOT invalidated when the copy changes. `a_mutate_after_verdict.py` / `a_mutate.out`:
   sound copy passes; then a `polars_drop` of `sample_id` appended by hand to the same `audit_steps` list (and an author-step injected) still passes
   `refuse_audit_steps_outside_an_audit` ("BUG: mutated copy passes without a new check; verdict cached: {'problems': []}"). In production `audit_run._Run` deep-copies
   the recipe and never changes it after `loaded_from_resolved` (`audit_run.py:128-129`; probes build new copies, `:208`), so no live path reaches it; the claim
   "asked before every build" holds only for a copy that is not changed. A copy built without its original is refused (OK, `a_mutate.out` last line).
   Say so in the docstring or key the verdict on a hash of `raw_config`; the second would remove the gap (not a half fix: the cache is the cause).
3. LOW (b): `test_the_rule_gives_the_join_keys_home_gives_on_every_shipped_recipe` (`test_audit_check_with_registry.py:193`) is now a tautology:
   `session_manager.extract_primary_keys` is `return join_keys.recipe_join_keys(...)` (`session_manager.py:~135`), so both sides are one function; it cannot fail by
   a divergence any more (its docstring admits it). It still guards "nobody writes a second walk" only as long as the function body is not copied back. Real proof
   of "same set as before": I ran the OLD function (dev `3bfb0050`, `dev_src`) and the NEW shared one (head) on 143 recipe/fragment files: 0 differences
   (`b_keys.py`, `b_dev.json`, `b_head.json`); 9 recipes have non-empty join keys; declared entity key found in 6 (`sample_id`, `id`). 
4. NOTE (d): the per-file call-count test `test_tier_steps_one_reader.py` counts NAMES: switching `engine_record.py` to `from ... import author_steps as step_list` leaves
   the count test passing. The behaviour tests caught it: 2 failed, 19 passed (`d_mutation_engine_record.out`:
   `test_the_engine_record_lists_a_tier_2_whose_only_steps_are_audit_steps` and `..._the_tier_3_of_a_plot_...`: `KeyError: 'tier3'`). So the two layers do their job
   together; the count test alone is weak against aliasing.
5. NOTE (f): the three older `read_source` "pinned" tests now hand `dataclasses.replace(original, config=SimpleNamespace(raw_config=raw, loaded_files=()))`
   (`test_read_source.py:224`): they still test what they claim (source path / tables of the handed text, file need not exist), but through a shape that NO production
   code builds: the only builder of a `ResolvedRecipe` is `loaded_from_resolved` (called only by `audit_run.py:129, :208`), and the only production caller of
   `read_source` is `home_theater.py:443`, without `loaded`. How the code tells them apart: `LoadedDataAnalysisRecipe.is_audit_copy` is `isinstance(self.config, ResolvedRecipe)`
   (`cache_keys.py:378-381`); an in-memory recipe with another config class is "not an audit copy" and is refused only if it holds an `audit_steps` key. No existing
   caller is wrongly refused (checked by grep, then by the full suite). A real audit copy that was pinned with a changed source path would now be refused: correct.
6. NOTE (e): Blueprint's writer: wrangling role raises if the tier file holds `audit_steps` (`blueprint_handlers.py:600-602`); an ordinary file is untouched (tests
   of Blueprint save in the suite pass; `test_audit_readers_see_audit_steps.py:98` checks both). I also ran the PLOT writer on a plot tier3 holding `audit_steps`
   (`e_plot_save.py`): the list is kept in the output (second case: `audit_steps` present). Not covered: join/table files saved through any other writer; there is no
   path today that writes an audit recipe to a file (D-0333 not built).
7. NOTE (g): `git diff 3bfb0050...f3efe931 -- .claude CLAUDE.md` is empty. `libs/utils/src/utils/recipe_spec.yaml`: 4 comment lines only; they name `AU01` to `AU03`
   but the check now also has `AU04` (stale by one code; comment only). The merge conflict of `4fc3df7a` in `orchestrator.py` is comment-only (consumed_by line and
   "T3 table" wording), no code; the head has all five guard calls (`orchestrator.py:203, 293, 444, 537` + definition 58).

### Part 1 answers
- a. Engine guard: asks `integrity_errors(copy, original)` in `read_source`, `_materialize_tier1` (293), `materialize_tier2` (444), `materialize_tier3` (537) and the
  variant at 203; copy without original refused with a plain sentence; mutated copy NOT rechecked (finding 2).
- b. Key drop rule: refused in `add_step` ("Cannot drop the key column(s) sample_id: ... Use a row filter or a removal by key instead."), in `integrity_errors`
  (names the audit id and place), and by the check (`AU04`): `b_keydrop.out`. A non-key column is added. Same set as before: finding 3.
- c. Check profiles: `check_recipe` run on 50 recipes (pipelines, templates, experimental, retest, gallery) x 4 profiles (run, build, gallery, audit) = 200 records +1
  load error at both dev `3bfb0050` and head: 0 differences (`c_profiles.py`, `c_compare.out`). What it cannot see: only shipped recipes, none with `audit_steps`
  (the audit-profile behaviour on audit recipes is covered by `test_audit_check_with_registry.py` which I did not mutate).
- d. Finding 4. e. Finding 6. f. Finding 5. g. Finding 7.

## Part 2 runs
| # | command | result | file |
|---|---|---|---|
| 1 | `from app.src.main import app` (worktree libs on PYTHONPATH) | OK | import.out |
| 2 | `pytest libs app/tests -q -n 4`, 30 browser files ignored (slice B list; no new browser file: candidates `browser_candidates.txt`) | 1 failed, 12668 passed, 14 skipped, 31 xfailed in 708 s (slice B on dev: 12551 passed, 13 skipped, 31 xfailed, 0 failed: +117 passed, +1 skipped) | headless.out |
| 2b | `test_export_report_texts.py`: ran inside run 2 (not ignored); 118 tests collected; I did not rerun it (no duplicate run, D-0285); per-file pass count not extracted | all of it passed or skipped (the only failure is finding 1) | export_report_texts.out |
| 3 | 29 browser files, qa, `-n 3 --dist loadfile` (resolved qa flags first: ghost save False, t3 / session / export / blueprint / gallery / test lab True) | 1 failed, 272 passed, 3 skipped, 1 xfailed (slice B: 273 passed, 3 skipped, 1 xfailed) in 1194 s | flags.out, browser.out |
| 3b | failure rerun ALONE: `test_export_download.py::test_exploration_filters_are_never_exported` | passed (179 s alone) | rerun_alone.out |
| 3c | `test_every_app_features_starts.py`, qa variable unset | 9 passed | every_starts.out |
| 4a | golden: baseline written at dev 3bfb0050 (`dev_src`), `--check` at head (PYTHONHASHSEED=0) | `result-identical`, rc 0 | golden_write.out, golden.out |
| 4b | pictures: `--write` at dev, `--check` at head (libs of each checkout first: printed in both outputs) | `identical: 51`, `PICTURES IDENTICAL`, rc 0 (the one known row of slice B did not show as a separate row here; every plot identical) | pictures_write.out, pictures.out |
| 5 | keys of 54 recipes (334 keys), dev vs head, `dumpkeys.py` | `cmp` identical | keys_dev.json, keys_head.json, keys.out |
| 6 | `validate_app_features_config.py --all --strict` | 8 templates, 0 errors, 0 warnings, PASS | validate.out |
| 6 | `audit_old_words.py --check` | CHECK FAILED, as in slice B; counts moved (recipe 111->112 files, 11490->11982 occurrences; profile 208->249: new files of this piece) | old_words.out |
| 6 | `check_doc_links.py` | 13 problems, the same 13 lines as slice B | doc_links.out |
| 6 | `audit_uml_model.py` | rc 1, output identical to slice B apart from the date | uml.out |

### Failures
1. `app/tests/test_browser_tests_no_venv_path.py::test_no_test_file_builds_a_path_into_venv`: `AssertionError ... Found: test_tier_steps_one_reader.py:27: SKIP_PARTS = {"tests", "build", ".venv", "__pycache__", "node_modules"}`.
2. `app/tests/test_export_download.py::test_exploration_filters_are_never_exported`: `wait_for_function ... #fb_op option value 'lt'` timed out (20 s) at `test_export_download.py:180` in the full parallel run (load average 8-13 from other sessions); passes alone. Same family as the flaky browser tests of earlier controls; not caused by the diff as far as I can tell (nothing here touches the filter form), but I did not run it a second time in parallel to prove flakiness.

### NOT covered
- The slice B "one known picture row": 51 identical here, not 50 plus one; I did not investigate the difference of counting (the stored dir of slice B was not compared).
- Which test is the +1 skipped.
- Audit-profile output on a shipped recipe that holds audit steps (none exists); the new test file `test_audit_check_with_registry.py` was read in the diff stat only, its mutation sensitivity was not tested except reader tests (d).
- ADR/rule/UML docs: this piece touches none; whether D-0332 / D-0322 / D-0297 need ADR text is a matter for the scribe step after merge (rule E4). I did not check the decision lines against `decision_ledger.md` (the brief's quoted words were taken as given).
- Browser pictures of the HOME screen (not this piece's scope).

## Last line
Head f3efe931 is NOT fit to be merged as it stands: one headless test fails (finding 1, a one-line change in a test file); with that fixed and the headless suite run again, everything else (browser, golden, pictures, keys, check profiles) is identical to dev.
