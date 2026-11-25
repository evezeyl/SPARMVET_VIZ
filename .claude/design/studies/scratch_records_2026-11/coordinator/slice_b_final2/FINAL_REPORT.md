# Slice B, second control, head 1150a405 (fix diff 56448279..1150a405). Reviewer; RAN unless marked READ. PART 1 detail: PART1_review.md

## Verdict: MERGE. No blocking finding.
The first control's regression (zero recipes) and review fixes F1 (Source memo key holds the recipe hash), F3 (filters carry the view key), F4 (one `_in_audit`), F6 (words) are done.

## Findings by weight
1. Low, latent, not a regression: home_theater.py:310 (`_data_analysis_recipe_keys`) passes `bootloader.get_default_data_analysis_recipe()` as the default argument of `safe_input`, evaluated even when the input exists; it raises with zero recipes if ever reached. On the start path it is reached only after the plot/target guard or the zero-recipes early return (test_home_zero_recipes.py passed). Other unguarded calls, none on the start path: home_theater.py:324 and :466 (behind a target dataset), :1074 (after the zero-recipes early return), :1877 (try/except); data_import_handlers.py:83, :269 and export_handlers.py:982 are click handlers in files this diff did not touch. Suggestion: use the `_or_none()` form at :310.
2. Note, Reshuffle (D-0341): in Exploration the whole `t3_plot_overrides[subtab]` entry is withheld (home_theater.py:687), not only the seed: random_state and any fill/colour/alpha/shape of the unmounted Plot Style panel. Fits D-0019/D-0327. Button (:838-839) and click handler (:850) inert outside Audit mode. The fix diff touches no export file; test_export_unchanged_by_the_view.py passed.
3. Restored sessions and filters: nothing is silently dropped. No session code reads or writes `applied_filters` (only orchestrator_helpers.py:34 seeds an empty list). `applied_filters` is filled only by `_filter_apply` from stamped pending rows. `rows_built_on` (t3_audit_engine.py ~590) refuses a row with no key or another key; `_applied_for_view` (home_theater.py:408-410) feeds preview, badge, audited-step line, inventory.
4. Docs texts (cross_cutting_concepts.md, data_lifecycle_theater.qmd) are true to the code; the qmd says its diagram is old. No rule file, ADR, CLAUDE.md, session_manager.py, session_handlers.py, app_features_validator.py or docs/UML/app.mdj touched.

Mutations (scratch copy outside the worktree, deleted; PYTHONPATH=. from the copy; unmutated: 34 passed):
- pin passed in Exploration: FAILED test_reshuffle_audit_only.py::test_with_a_pin_stored_the_exploration_plot_is_drawn_without_it_and_the_audited_plot_with_it and ::test_the_exploration_plot_equals_the_original_pane_of_compare_when_a_pin_exists (2 failed, 3 passed).
- row without a view key applied: FAILED test_home_view_choices.py::test_a_filter_built_on_another_view_is_not_applied_by_the_preview and ::test_the_badge_counts_only_the_filters_of_this_view (2 failed, 49 passed).

## Runs (outputs in tmpAI/coordinator/slice_b_final2/)
| Run | Command | Result | File |
|---|---|---|---|
| App import | PYTHONPATH=. venv python -c "from app.src.main import app" | OK | import.out |
| qa flags | slice_b_final/flags.py, qa, SPARMVET_DEPLOYMENT unset | all audit/comparison/session/export/Blueprint flags True; ghost_save enabled False | flags.out |
| Headless | pytest libs app/tests -q -n 4, 30 browser files ignored | 12551 passed, 13 skipped, 31 xfailed, 0 failed (594 s); first control 12532 | headless.out |
| Browser, qa | 29 browser files, -n 3 --dist loadfile | 273 passed, 3 skipped, 1 xfailed, 0 failed (1020 s); first control 269 passed, 2 failed | browser.out |
| Eight setups | test_every_app_features_starts.py, qa variable unset | 9 passed | every_starts.out |
| Golden | assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json | result-identical, rc 0 | golden.out |
| Pictures | assets/scripts/recipe_pictures.py --check tmpAI/engine_keys/picture_baseline_15394ef5 --allow-outside-checkout | 50 identical + the one known row (test_logic, rejected orphan recipe); rc 1 because of that row, as in the first control | pictures.out |
| Flag files | scripts/validate_app_features_config.py --all --strict | 8 templates, 0 errors, 0 warnings, PASS | validate.out |
| UML audit | assets/scripts/audit_uml_model.py --project-root . | same as the first control (only the Generated line differs) | uml.out |
| Link check | assets/scripts/check_doc_links.py | 13 problems, identical to the first control | doc_links.out |
| Old words | assets/scripts/audit_old_words.py --check | as before (only the scanned-file count 2299 to 2301) | old_words.out |

## Failures
None in headless or browser. The non-zero exit codes (pictures, UML audit, link check, old words) equal the first control.

## Not covered
Ghost save (off in qa); setups other than qa (only started); the Quarto render of the export; two sessions on one audit folder; a hands-on browser walk (the browser tests are the only UI check); Compare's panes pixel by pixel beyond existing tests; no mutation of the view-clearing effect or the Source memo key; :310 not run with zero recipes beyond the tests; link and UML counts compared with the first control, not re-triaged. Libs under pytest were the worktree's (where_pytest.out of the first control); plain scripts resolve some libs from the main checkout; the diff changes only app/ and docs/.

## Last line
Head 1150a405 is fit to be merged into dev.
