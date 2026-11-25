# Review 2 of task/export-box, head 4dec6348 (fix commit on 2e8a033c)

## Verdict: MERGE

dev 252fb7b5 is an ancestor of the branch (git merge-base, ran). Tree clean.

## Part 1: the fix commit (git diff 2e8a033c 4dec6348, 3 files: export_handlers.py + 2 new tests; nothing else, nothing beyond the three fixes)
1. reactive.effect -> reactive.Effect (export_handlers.py ~754). Headless run: no "is_enabled" in the log (grep count 0), warnings 2 (ran). The four files that showed it before: three call define_export_server; the fourth is the browser file test_export_inputs_survive_plot_tab.py, which the documented headless command also collects; all clean now.
2. README and notice, four cases (export_handlers.py ~1413-1490, ~2042):
   - built: "included (the full recipe and the data files)". True: no missing file.
   - build raised: except branch writes data_analysis_recipes_reproducibility/ERROR.txt (real path, read at ~1480) and sets repro_status="failed"; README says "requested ... NOT built", points to that ERROR.txt. True.
   - data file not copied: loop writes data_reproducibility/<id>_ERROR.txt (read) and appends to repro_missing_files; README and notice say INCOMPLETE and name the ids. True.
   - not ticked: unchanged text.
   - Minor, reasoned: if the exception comes after the recipe yaml was already written (e.g. in the notify), the README says NOT built while a recipe file exists beside ERROR.txt. It errs on the safe side (tells the user not to rely on it); not a blocker.
   - Nothing else in the bundle changed (diff read: only status variables and text).
   - Break once (ran, on a scratch copy of app/ outside the worktree with the handler from 2e8a033c): test_export_readme_reproducibility.py -> 2 failed (raised case, incomplete case), 2 passed (built, not ticked: unchanged behaviour, as expected). test_export_scope_notices.py: collection fails on the old handler (no SCOPE_LABELS); with that import stubbed, all 3 tests fail (lowercase effect is not registered by the Effect stub, and old text). So the tests can fail.
3. Notices: SCOPE_LABELS = {"global":"Global","group":"Active group","plot":"Active plot"} is the single source used by export_scope_choices for the radio labels (read); resulting labels are character-identical to 2e8a033c ("Global", "Active group (<gid>)", "Active group", "Active plot (<pid>)", "Active plot"). Reset notice uses SCOPE_LABELS.get(current, current); choices-error notice uses what_failed(...), no suggestion (read, and test asserts the plain form and "(ValueError: no recipe)").
   - Small point: the reset notice shows 'Active group' without the group id; fine.

Decision compliance: D-0050 (no silent error): the README no longer says "included" when it is not; D-0101: notices are short plain sentences. No decision reconsidered.

## Part 2: controls on 4dec6348 (logs in tmpAI/review_export_box_2/)
| Control | Result | Last run | Difference |
|---|---|---|---|
| test_imports_from_checkout.py | 12 passed | 12 | same |
| headless (section 8 command) | 10471 passed, 5 skipped, 32 xfailed, 2 warnings, 30m46 | 10464/5/32/3 | +7 = 4 in test_export_readme_reproducibility.py + 3 in test_export_scope_notices.py; warnings 3 -> 2 (the ReactiveWarning is gone) |
| browser qa (15 test_shiny_*.py, test_export_download.py, test_empty_data_analysis_recipe_startup.py, test_export_inputs_survive_plot_tab.py) | 140 passed, 3 skipped, 1 xfailed, 22m38 | 140/3/1 | same; the seed test passed, no rerun needed |
| test_every_app_features_starts.py (no app features set) | 9 passed | 9 | same |
| golden_baseline.py --check | result-identical, rc 0 | identical | same |
| assets/scripts/gallery_previews.py (no --apply) | identical 34, size only 0, differs 0, new 0, error 0, rc 0 | 34 identical | same |

## Not checked
Break-once was done against the previous handler, not by disabling each branch one at a time; the "stays" test (no notice) is covered only through the old-code failure. audit_old_words and doc-link checks not run (not asked). Doc/UML/ADR drift for the new README wording not checked. No process left running.
