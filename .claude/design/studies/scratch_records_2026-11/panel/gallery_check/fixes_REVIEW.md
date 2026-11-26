# Review of task/gallery-fixes (963644e4), by the reviewer, 2026-11-18

VERDICT: MERGE AFTER A NAMED FIX (three small points, none changes behaviour; the code and the two texts are right).

## Verified
- Browser (worktree, app features developer; port 8741): Gallery has 34 examples. Three examples opened (density_2d_bin, area_simple, bar_simple): each has an R Graph Gallery link with target="_blank" rel="noopener noreferrer". Clicking it opened a NEW tab (context had 2 pages); the app page kept its URL and its example select (1 element). No console error or page error in the whole run. Script: tmpAI/panel/gallery_check/gf_run/f1.py.
- GitHub button: exists under developer, standalone and qa (a.btn with href https://github.com/evezeyl/SPARMVET_VIZ, visible, in the row under the workspace tab pills, left). Code: app/handlers/home_theater.py:1575-1587, built in sidebar_nav_ui, no flag gate. The address is NOT from the deployment: it is the constant `_GITHUB_REPO_URL` (home_theater.py:68), Eve's fork, written in the code.
- Internal anchor and relative link are untouched (test + code, gallery_listing.py external_links_new_tab).
- home_theater.py: the diff has ONE changed line (1945, the card text). Confirmed.
- No caller left of GalleryViewer.submission_modal_ui, autofill_meta_from_audit, #btn_autofill_meta, btn_confirm_submission, check_yaml (grep app, libs, assets, config, docs, scripts, in the worktree: only the new test and one doc line, below). submit_example and its tests untouched (diff stat: no libs/ file).
- Tests (once, worktree): test_gallery_texts_and_links.py + app/tests/test_gallery_*.py + libs/viz_gallery/tests: 148 passed, 1 skipped. Builder's break-once reported (link function unchanged: 2 failures); I did not repeat it.
- git merge-tree --write-tree dev task/gallery-fixes (dev = 6ee76184): clean, no conflict (tree ba624f3d).

## The two texts, for Eve (as shown in the running app)
1. Right card "Gallery Explorer": "Browse visual examples. Select an example to see its picture, its recipe and its guidance. To reuse it, copy the recipe text by hand."
2. Banner "Gallery Inspiration": "Browse visual examples for inspiration. Missing an example? Open an issue with the GitHub button under the workspace tabs on the left."
Both true. Note: text 1 does not name the tabs (Plot Preview, Data Sample, YAML Example); "picture" = Plot Preview, "recipe" = YAML Example; the Data Sample tab is not mentioned. Fine, not wrong.

## Fix first (named)
1. docs/UML/risks_and_technical_debt.md:48: the row "GalleryViewer.submission_modal_ui() is defined but called nowhere ... F-18" (also .claude/tasks/uml_findings.md:26, resolved row saying "not removed") describes code that is now deleted. Remove or mark closed (rules_documentation_aesthetics.md section 1; rules_legacy_management.md: every removal leaves a tombstone/record).
2. .claude/rules/rules_css_style_spec.md:178: lists `#btn_autofill_meta` as an ID of a Type 1 button; the CSS rule and the button are removed. Take it out of the list. (The builder named this and did not edit it.)
3. app/tests/test_gallery_texts_and_links.py:26 (test_every_shipped_guidance_link_is_fixed): the assertion ends with `or "href=\"#" in html`, so any example with one internal anchor passes without the count check; the test cannot fail for that example. Make it strict (count only external links, ignore the anchors).

## Not blocking, for Eve
- Possibly unused imports in gallery_viewer.py (yaml, Path, reactive, render): builder left them. A dead-import cleanup is a separate small task.
- Builder's question: `app/modules/exporter.py` (SubmissionExporter), keep or delete: a decision for Eve (D-0046 says only that submit_example stays and the dead submission code goes; exporter is dead submission code by the same reading, but she has to say).

## What the checks cannot see
Only the three examples I opened were clicked; the other 31 are covered by the pure-function test over all example_meta.md files (which has the weakness in point 3). Network was available, so the external site loaded; with no network the new tab would show the browser's own error, not the app's.
