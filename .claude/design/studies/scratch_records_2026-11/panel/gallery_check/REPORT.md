# Gallery check, 2026-11-18, `dev` 32e09107
Run: headless Chromium, 1900 px wide, `developer` (port 8791) and once `standalone`. Scripts and pictures are in this folder (`examples.py`, `filters.py`, `switching.py`, `actions.py`, `links.py`, `shots/`).

## Verdict
YES WITH CAUTIONS. All 34 examples open and look right, the filters give the right lists, and Home is not changed by a visit. Nothing is broken. Cautions: one link in every guidance text takes the user out of the app (F1); the Gallery forgets its filters and selection when the user leaves it (F2); two texts promise things that do not exist (F3, F4); no copy button (F5).

## Findings, the most likely to be met first
Evidence labels: verified = run in the browser or read at file:line.

**F1. A link in the guidance text leaves the app in the same tab.** Every one of the 34 guidance texts ends with an "R Graph Gallery" link (34 of 34 files contain an http link). It has no `target`, so it replaces the app page and the session is lost. Steps: open the Gallery, click the blue link at the bottom of the yellow pane. Verified: `href` set, `target` none, after the click the page is replaced (picture not possible: no internet was allowed to load; the page became `chrome-error`). Code: `app/handlers/gallery_handlers.py:167` (`ui.markdown`). Decision: none found. Options: open links in a new tab, or leave as it is. Suggestion: open in a new tab with `rel="noopener"`. [sonnet/low]

**F2. The Gallery forgets everything when you leave it.** Steps: Gallery, tick only "Distribution", Apply (10 examples), pick the 3rd, open the YAML tab; go to Home (or Blueprint) and come back. Result: all six axes ticked again, 34 examples, first example, Plot Preview tab. Same under `standalone`. Verified (`switching.py`, `switch_dev.json`). Cause: the left sidebar is rebuilt on every workspace change (`rules_ui_dashboard.md` section 2). Rule: `ui_implementation_contract.md` section 13 says "Gallery sub-tab position ... independently preserved". Nothing in the ledger decides it for the Gallery. Options: (a) keep the state of the Gallery, (b) change section 13 to say the Gallery restarts. Suggestion: (b) is the smaller truth today; Eve decides. [sonnet/medium for a, haiku/low for b]

**F3. The right card promises something that was removed.** Text: "Select an example to copy its YAML into the Architect sandbox." There is no such action and no "Architect sandbox". `app/handlers/home_theater.py:1945`. Decided: D-0008 / ADR-093 (no handoff from the Gallery). Suggestion: "Select an example. To reuse its recipe, copy the YAML text by hand." [haiku/low]

**F4. The banner promises a request path that does not exist.** "Did you see a nice figure? Send us a request for example implementation." No button or form; `GALLERY.md` lists "Request an example" as not built. `app/modules/gallery_viewer.py:195`. The header has a GitHub button ("file an issue"), so it is the only way. Decision: none for the request. Options: reword to point to the GitHub button, or build a request button. Suggestion: reword. [haiku/low]

**F5. No copy button for the recipe text.** The YAML tab is plain text. Ctrl+A then Ctrl+C copies the whole page (2404 characters starting "Gallery Inspiration"), not the recipe; only a mouse selection of the pane works (1212 characters verified). The help text says "to copy by hand". `GALLERY.md` lists "Copy example YAML" as a function. Decision: ADR-093 says by hand; a button is not decided. Options: add a copy button (the text stays the user's choice), or keep and say how to select. [sonnet/low]

**F6. Empty result is easy to miss.** Steps: Family "Comparison" and Pattern "1 Numeric" then Apply. The list is empty, the label says "(0 matched)", a warning appears for a few seconds, and the preview pane says "Select an example to view preview." without saying why (`shots/filters_dev_empty_combo.png`). There is no "clear filters" button: the user must tick "Select all" in each of the six panels. Code: `gallery_handlers.py:232-234`, `:97`. Decision: none. Suggestion: one line in the pane "No example matches these filters" and a "Clear filters" button. [sonnet/low]

**F7. Unticking every box of an axis means "no filter", not "nothing".** Family with no box ticked, Apply: 34 shown. Code comment at `gallery_handlers.py:200-204` says it is intended. The user sees "34 matched", so it is not hidden, but it is the opposite of what a tick list suggests. Decision: none. Options: keep, or treat no ticks as zero results with the F6 line. [haiku/low]

**F8. Filters act only on Apply and nothing says so.** Ticking a box changes nothing visible. The "Filtering examples..." notice also appears on every entry into the Gallery, with no filter set (`gallery_handlers.py:171-193`). Low. Suggestion: none needed unless Eve finds it confusing. [haiku/low]

**F9. Dead submission code is still in the app.** `GalleryViewer.submission_modal_ui` (`gallery_viewer.py:24`) and `autofill_meta_from_audit` (`:206`) have no caller; the buttons `btn_confirm_submission` and `btn_autofill_meta` have no handler (grep over `app` and `libs`). The submission form is NOT reachable by a user. `submit_example` stays in `libs/viz_gallery` (D-0046: "submit_example stays, dead submission code goes"). Options: remove the dead modal (as D-0046 says), or keep it for a later form. Suggestion: remove, ask Eve. [haiku/low]

**F10. Rule file is out of date (known).** `rules_gallery_standards.md` section 1 says "exactly" four files; each bundle also has `preview_thumb.png` (34 of 34, `has_thumb` true in the index). Low. [haiku/low]

## 34 examples (developer; standalone gives the same counts and the same text lengths)
Picture = the image the user sees equals the stored `preview_plot.png`, byte for byte. Recipe text = equals `data_analysis_recipe.yaml`. Tags = the strip under the guidance title carries the 6 index values.
| example | picture | recipe text | guidance | tags | data tab | errors |
|---|---|---|---|---|---|---|
| density_2d_bin | yes, 960x600, same bytes as the stored file | yes, same as file (1584 chars) | yes, title "2D Bin Density" (764 chars) | yes, 6 of 6 match the index | yes, 60 rows | none |
| area_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1550 chars) | yes, title "Area Chart" (755 chars) | yes, 6 of 6 match the index | yes, 7 rows | none |
| bar_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1262 chars) | yes, title "Bar Chart" (560 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| beeswarm_sina | yes, 960x600, same bytes as the stored file | yes, same as file (1553 chars) | yes, title "Beeswarm / Sina Plot" (702 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| boxplot_faceted | yes, 960x600, same bytes as the stored file | yes, same as file (1388 chars) | yes, title "Faceted Boxplot" (554 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| boxplot_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1315 chars) | yes, title "Boxplot" (551 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| bubble | yes, 960x600, same bytes as the stored file | yes, same as file (1862 chars) | yes, title "Bubble Chart" (1004 chars) | yes, 6 of 6 match the index | yes, 5 rows | none |
| connected_scatter | yes, 960x600, same bytes as the stored file | yes, same as file (1818 chars) | yes, title "Connected Scatter Plot" (820 chars) | yes, 6 of 6 match the index | yes, 16 rows | none |
| density_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1213 chars) | yes, title "Density Plot" (519 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| dumbbell | yes, 960x600, same bytes as the stored file | yes, same as file (1692 chars) | yes, title "Dumbbell Chart" (801 chars) | yes, 6 of 6 match the index | yes, 12 rows | none |
| ecdf | yes, 960x600, same bytes as the stored file | yes, same as file (1508 chars) | yes, title "ECDF Plot" (693 chars) | yes, 6 of 6 match the index | yes, 30 rows | none |
| error_bar | yes, 960x600, same bytes as the stored file | yes, same as file (1684 chars) | yes, title "Error Bar / Point Range" (800 chars) | yes, 6 of 6 match the index | yes, 8 rows | none |
| freqpoly | yes, 960x600, same bytes as the stored file | yes, same as file (1430 chars) | yes, title "Frequency Polygon" (699 chars) | yes, 6 of 6 match the index | yes, 45 rows | none |
| bar_grouped | yes, 960x600, same bytes as the stored file | yes, same as file (1590 chars) | yes, title "Grouped Bar Chart" (780 chars) | yes, 6 of 6 match the index | yes, 15 rows | none |
| heatmap_correlation | yes, 960x600, same bytes as the stored file | yes, same as file (1558 chars) | yes, title "Correlation Matrix (Heatmap)" (767 chars) | yes, 6 of 6 match the index | yes, 16 rows | none |
| histogram_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1223 chars) | yes, title "Histogram" (511 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| bar_horizontal | yes, 960x600, same bytes as the stored file | yes, same as file (1625 chars) | yes, title "Horizontal Bar Chart" (832 chars) | yes, 6 of 6 match the index | yes, 5 rows | none |
| jitter_strip | yes, 960x600, same bytes as the stored file | yes, same as file (1636 chars) | yes, title "Jitter Strip Plot" (913 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| line_grouped | yes, 960x600, same bytes as the stored file | yes, same as file (1572 chars) | yes, title "Line Chart (Grouped)" (875 chars) | yes, 6 of 6 match the index | yes, 35 rows | none |
| line_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1569 chars) | yes, title "Line Chart (Simple)" (941 chars) | yes, 6 of 6 match the index | yes, 7 rows | none |
| lollipop_advanced | yes, 960x600, same bytes as the stored file | yes, same as file (1547 chars) | yes, title "Lollipop Chart" (744 chars) | yes, 6 of 6 match the index | yes, 4 rows | none |
| point_faceted | yes, 960x600, same bytes as the stored file | yes, same as file (1413 chars) | yes, title "Faceted Scatter" (559 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| point_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1292 chars) | yes, title "Scatter Plot" (547 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| proportion_bar | yes, 960x600, same bytes as the stored file | yes, same as file (1589 chars) | yes, title "Proportion Bar Chart" (1003 chars) | yes, 6 of 6 match the index | yes, 25 rows | none |
| qq_plot | yes, 960x600, same bytes as the stored file | yes, same as file (1623 chars) | yes, title "Q-Q Plot (Quantile-Quantile)" (794 chars) | yes, 6 of 6 match the index | yes, 30 rows | none |
| ridgeline_advanced | yes, 960x600, same bytes as the stored file | yes, same as file (1441 chars) | yes, title "Ridgeline Distribution" (801 chars) | yes, 6 of 6 match the index | yes, 200 rows | none |
| scatter_smooth | yes, 960x600, same bytes as the stored file | yes, same as file (1696 chars) | yes, title "Scatter Plot with Smoother" (752 chars) | yes, 6 of 6 match the index | yes, 27 rows | none |
| stacked_area | yes, 960x600, same bytes as the stored file | yes, same as file (1545 chars) | yes, title "Stacked Area Chart" (742 chars) | yes, 6 of 6 match the index | yes, 27 rows | none |
| stacked_bar | yes, 960x600, same bytes as the stored file | yes, same as file (1566 chars) | yes, title "Stacked Bar Chart" (993 chars) | yes, 6 of 6 match the index | yes, 25 rows | none |
| step_chart | yes, 960x600, same bytes as the stored file | yes, same as file (1641 chars) | yes, title "Step Chart" (801 chars) | yes, 6 of 6 match the index | yes, 15 rows | none |
| tile_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1302 chars) | yes, title "Heatmap (Tile)" (551 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| violin_boxplot | yes, 960x600, same bytes as the stored file | yes, same as file (1553 chars) | yes, title "Violin + Boxplot Overlay" (693 chars) | yes, 6 of 6 match the index | yes, 40 rows | none |
| violin_faceted | yes, 960x600, same bytes as the stored file | yes, same as file (1375 chars) | yes, title "Faceted Violin" (560 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |
| violin_simple | yes, 960x600, same bytes as the stored file | yes, same as file (1248 chars) | yes, title "Violin Plot" (519 chars) | yes, 6 of 6 match the index | yes, 100 rows | none |

Browser console errors: 0 in every run (dev and standalone). Server log: no traceback and no Gallery error (the only warnings are about HOME's recipe columns). Notices seen: only the normal "recipe loaded" and "Filtering examples...". Red output: none.

## What was checked and passed
1. The list: 34 shown = 34 bundles = 34 in `gallery_index.json` (`rejected` is empty). None missing, none without a bundle, no rejected example, so no "left out" block was shown. Verified.
2. All 34 examples, both app features: picture, recipe text, guidance, tags, data tab shown (rows equal the file: 4 to 200, the largest is `ridgeline_advanced`). Pictures: all 960x600.
3. Filters: for each of the six axes, the 2 most common values and 1 rare value: the list equals the examples that carry the value in the index (15 runs, all equal, both app features); two axes combined (5 matched) and three axes (2 matched) equal; the values offered by the panels equal the values used by the examples (no offered value without an example, none missing); the stored pivot equals the examples' own taxonomy. After "Select all" on all axes: 34 again. There is no search box (not built, `GALLERY.md` says so).
4. Switching: Home after a visit to the Gallery and to Blueprint is unchanged (recipe, group tab, plot tab, both view choices "My view"). The Gallery resets (F2).
5. Static pictures: `gallery_preview_img` reads the stored `preview_plot.png` and sends it as base64 (`gallery_handlers.py:103-112`); nothing is drawn at run time. Time from choosing an example to the new picture: 46 to 72 ms (8 examples). A test (`app/tests/test_gallery_app_path.py`) draws each example and compares with the stored picture, so a stale picture can be caught; I did not run it.
6. Help button (?) in the Gallery shows a correct quick reference that says no handoff and "copy by hand". The Full documentation link answers 200.
7. Texts: see F3, F4, F5, F6, F10. Also fine: all example titles and guidance read normally; the guidance tag strip matches the index.
8. Tests (not run): `app/tests/test_gallery_listing.py` (what is listed, rejected lines), `test_gallery_check_at_start.py`, `test_gallery_full_check.py` (every bundle passes the check, index equals the rebuild), `test_gallery_app_path.py` (table and picture through the app path), `test_gallery_viewer_taxonomy.py` (filter terms from the spec data), `test_shiny_gallery_left_out.py` (browser: a broken example is left out with its reason), `libs/viz_gallery/tests/test_gallery_bundle.py` and `test_gallery_examples_are_recipes.py`. Nothing automatic covers: the three tabs showing in the browser, the filters and Apply, the empty result, the reset on leaving (F2), the guidance link (F1), the right card and banner texts.

## What was not checked
- No full test suite (the brief says none). No narrow window, no other browser, no second user at the same time.
- The external R Graph Gallery pages (no internet allowed in the run).
- App features other than `developer` and `standalone` (`qa` and the others gate the Gallery off or on by flag).
- No real submission (none reachable). The community "browse contributions" function of `GALLERY.md` is not built; not looked for.
- HOME was checked only for the recipe, the two tabs and the two view choices. I did not set an exploration filter or an audit step before the visit.

## Left on disk
Only this folder `tmpAI/panel/gallery_check/` (scripts, JSON results, server logs, `shots/`, `sessions_before.txt`). Both servers I started were stopped by PID; port 8791 is free. The deployment's user data folder `tmp/UI_TEST/user/_sessions` was compared before and after: unchanged. No tracked file touched (`git status`: only the ledger and tasks files that another agent changed).
