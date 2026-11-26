# Gallery fixes (F1, F3, F4, F9) - branch task/gallery-fixes
Commit 963644e4 (from dev cce86d55). No push, no merge.

## New texts for Eve to approve (PROVISIONAL)
- F3 (home_theater.py:1945): "Select an example to see its picture, its recipe and its guidance. To reuse it, copy the recipe text by hand." The tabs are "Plot Preview", "Data Sample", "YAML Example"; the data tab is not named in the text.
- F4 (gallery_viewer.py banner): "Browse visual examples for inspiration. Missing an example? Open an issue with the GitHub button under the workspace tabs on the left."
  Evidence: the button is built in home_theater.py:1575-1587 in the left navigation stack, not gated by a flag, address hardcoded `_GITHUB_REPO_URL` (home_theater.py:68), not from the deployment branding. So it exists under every app features (developer, standalone, qa too). Not verified in a browser. The address is Eve's fork, fixed in code.

## F1
`external_links_new_tab(html)` (pure, app/modules/gallery_listing.py) adds target="_blank" rel="noopener noreferrer" to every http/https `<a>` (replacing any target/rel already there); `#anchor` and relative links untouched. Used in `gallery_md_content` (gallery_handlers.py) on the HTML from `ui.markdown`. Tested on all 34 shipped example_meta.md.

## F9 removed (grep over app, libs, assets, config, docs, scripts: no caller, no handler, no test)
- `GalleryViewer.submission_modal_ui` (ids check_yaml, check_tsv, check_png, check_md, check_supp, btn_autofill_meta, btn_confirm_submission).
- `GalleryViewer.autofill_meta_from_audit`.
- CSS rule `#btn_autofill_meta` in config/ui/theme.css.
- Kept: `GalleryManager.submit_example` and its tests.
- Rule file still naming a removed id (not edited): `.claude/rules/rules_css_style_spec.md:178` (`#btn_autofill_meta`).
- Possibly now-unused imports in gallery_viewer.py (yaml, Path, reactive, render): not touched.

## Question for Eve
`app/modules/exporter.py` (`SubmissionExporter`): not removed. Keep or delete?

## Tests
New `app/tests/test_gallery_texts_and_links.py` (5 pass). Ran app/tests/test_gallery_*.py, test_shiny_gallery_left_out.py (the browser Gallery test, once), libs/viz_gallery/tests: 151 passed, 1 skipped. App import OK.
Break-once: link function returned unchanged: 2 tests failed; restored.

## Not done
F2, F5-F8, F10. No browser click of the link or look at the button. `@deps` provides of gallery_listing updated.
