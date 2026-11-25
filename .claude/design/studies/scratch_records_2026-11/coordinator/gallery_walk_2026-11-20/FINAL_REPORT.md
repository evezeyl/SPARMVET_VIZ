# Gallery walk, 2026-11-20 (GALLERY-CHECK-1). App from main checkout, branch dev, qa app features, local deployment, port 8123, headless Chromium, 1600x1000. Server stopped by PID. No tracked file changed.

Scripts: walk.py (steps 1-3), walk2.py (steps 4-7), walk3.py (checks), walk4.py (help); raw data: walk_seq.json, walk2.json, walk3.json, links_status.json; server.log.

## Numbers
- Listed in the dropdown: 34. Folders under assets/gallery_data/: 34. gallery_index.json count: 34 (rejected: none). Left out: none; the "left out" notice is absent, correctly.
- Opened without a problem: 34 of 34 (picture is the exact file of the example, guidance and recipe text show, data tab shows rows, no red text, no console error, no Traceback in the server log). Time until the picture is there: 0.02 to 0.04 s (local, files read from disk).
- Switching (34 in order, 34 back, then 10 random jumps): picture, title and selection always belonged together; no stale content found.
- Filters: 52 single-value filters checked against the index: 51 equal the index, 1 anomaly (finding 9).

## Table of the 34 examples
| # | example id | dropdown name | guidance title | picture (exact file, s) | guidance chars | recipe chars | data rows | error/console/traceback | link 404 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | density_2d_bin | 2D Bin Density | 2D Bin Density | ok 0.03 | 757 | 1588 | 60 | SEE JSON |  |
| 2 | area_simple | Area Chart | Area Chart | ok 0.08 | 750 | 1522 | 7 | none |  |
| 3 | bar_simple | Bar Simple | Bar Chart | ok 0.06 | 555 | 1276 | 100 | none |  |
| 4 | beeswarm_sina | Beeswarm / Sina Plot | Beeswarm / Sina Plot | ok 0.08 | 695 | 1557 | 100 | none |  |
| 5 | boxplot_faceted | Boxplot Faceted | Faceted Boxplot | ok 0.06 | 549 | 1400 | 100 | none |  |
| 6 | boxplot_simple | Boxplot Simple | Boxplot | ok 0.07 | 546 | 1329 | 100 | none |  |
| 7 | bubble | Bubble Chart | Bubble Chart | ok 0.07 | 999 | 1826 | 5 | none |  |
| 8 | connected_scatter | Connected Scatter Plot | Connected Scatter Plot | ok 0.07 | 809 | 1820 | 16 | none |  |
| 9 | density_simple | Density Simple | Density Plot | ok 0.05 | 514 | 1227 | 100 | none |  |
| 10 | dumbbell | Dumbbell Chart | Dumbbell Chart | ok 0.08 | 792 | 1694 | 12 | none |  |
| 11 | ecdf | ECDF Plot | ECDF Plot | ok 0.08 | 686 | 1512 | 30 | none | YES |
| 12 | error_bar | Error Bar / Point Range | Error Bar / Point Range | ok 0.06 | 789 | 1688 | 8 | none |  |
| 13 | freqpoly | Frequency Polygon | Frequency Polygon | ok 0.06 | 692 | 1440 | 45 | none | YES |
| 14 | bar_grouped | Grouped Bar Chart | Grouped Bar Chart | ok 0.07 | 771 | 1594 | 15 | none | YES |
| 15 | heatmap_correlation | Heatmap Correlation | Correlation Matrix (Heatmap) | ok 0.07 | 764 | 1530 | 16 | none |  |
| 16 | histogram_simple | Histogram Simple | Histogram | ok 0.07 | 506 | 1237 | 100 | none |  |
| 17 | bar_horizontal | Horizontal Bar Chart | Horizontal Bar Chart | ok 0.07 | 827 | 1591 | 5 | none |  |
| 18 | jitter_strip | Jitter Strip Plot | Jitter Strip Plot | ok 0.32 | 908 | 1612 | 100 | none | YES |
| 19 | line_grouped | Line Chart (Grouped) | Line Chart (Grouped) | ok 0.06 | 870 | 1546 | 35 | none |  |
| 20 | line_simple | Line Chart (Simple) | Line Chart (Simple) | ok 0.07 | 936 | 1541 | 7 | none |  |
| 21 | lollipop_advanced | Lollipop Advanced | Lollipop Chart | ok 0.07 | 741 | 1521 | 4 | none |  |
| 22 | point_faceted | Point Faceted | Faceted Scatter | ok 0.07 | 554 | 1425 | 100 | none | YES |
| 23 | point_simple | Point Simple | Scatter Plot | ok 0.07 | 542 | 1306 | 100 | none | YES |
| 24 | proportion_bar | Proportion Bar Chart | Proportion Bar Chart | ok 0.06 | 998 | 1563 | 25 | none |  |
| 25 | qq_plot | Q-Q Plot (Quantile-Quantile) | Q-Q Plot (Quantile-Quantile) | ok 0.07 | 785 | 1625 | 30 | none | YES |
| 26 | ridgeline_advanced | Ridgeline Advanced | Ridgeline Distribution | ok 0.07 | 798 | 1417 | 200 | none |  |
| 27 | scatter_smooth | Scatter Plot with Smoother | Scatter Plot with Smoother | ok 0.06 | 743 | 1698 | 27 | none |  |
| 28 | stacked_area | Stacked Area Chart | Stacked Area Chart | ok 0.08 | 733 | 1549 | 27 | none |  |
| 29 | stacked_bar | Stacked Bar Chart | Stacked Bar Chart | ok 0.06 | 988 | 1540 | 25 | none |  |
| 30 | step_chart | Step Chart | Step Chart | ok 0.06 | 792 | 1643 | 15 | none |  |
| 31 | tile_simple | Tile Simple | Heatmap (Tile) | ok 0.1 | 546 | 1316 | 100 | none |  |
| 32 | violin_boxplot | Violin + Boxplot Overlay | Violin + Boxplot Overlay | ok 0.05 | 686 | 1561 | 40 | none |  |
| 33 | violin_faceted | Violin Faceted | Faceted Violin | ok 0.07 | 555 | 1387 | 100 | none |  |
| 34 | violin_simple | Violin Simple | Violin Plot | ok 0.07 | 514 | 1262 | 100 | none |  |

## Findings, in the order a demo user notices them
1. **Return to the Gallery after Home: selection and filters are gone.** Seen: I chose "Ridgeline Advanced" with Difficulty = Advanced (3 matched), went to Home, came back: list shows 34 again, all boxes ticked, the dropdown shows the first example (2D Bin Density) instead of Ridgeline. Screenshots 09_gallery_before_leaving.png, 11_gallery_back.png. Reproduce: Gallery, tick Advanced only, Apply, pick an example, click Home, click Gallery. Place: gallery_handlers.py:171-172 (effect fires on sidebar_nav and rebuilds the choices, `selected=None` at :230); the sidebar is rebuilt on a workspace change. Suggestion: keep the example and the ticks when the user returns, or say plainly on screen that they are reset.
2. **Apply always drops the current selection.** Seen: with a filter that removes the example I was looking at, the dropdown jumps to the first remaining example (screenshot 08_selection_after_filter.png: violin_simple was open, area_simple shown after Evolution + Apply). That case is natural; I read, but did not run, the case where the example is still in the filtered list: `selected=None` at gallery_handlers.py:230 suggests it also jumps. Suggestion: keep the current example when it is still in the list.
3. **13 examples have one name in the dropdown and another title in the guidance.** Seen: dropdown "Violin Simple", guidance title "Violin Plot"; also Bar Simple / Bar Chart, Tile Simple / Heatmap (Tile), Point Simple / Scatter Plot, Ridgeline Advanced / Ridgeline Distribution, and 8 more (table above). Screenshot 13_width_1100.png (Ridgeline). Place: dropdown name = `info.label` of the recipe (libs/viz_gallery/src/viz_gallery/gallery_manager.py:107), title = first heading of example_meta.md. Suggestion: one name for both.
4. **7 examples carry guidance links that answer 404 today** (checked with curl, 2026-11-20): ecdf, freqpoly, bar_grouped, jitter_strip, qq_plot, point_simple, point_faceted (URLs on r-graph-gallery.com: ecdf.html, frequency-polygon.html, grouped-barplot.html, jitter.html, qqplot-with-r-and-ggplot2.html, scatter-plot.html). All 37 links in the 34 texts have target=_blank and rel="noopener noreferrer" (D-0271 holds); 27 distinct URLs, 21 answer 200. Three examples also link the bare http://r-graph-gallery.com (not https). No dead link inside the app. The tests check the attributes, not that the page exists. Suggestion: replace the six URLs.
5. **A filter panel with no box ticked means "no filter".** Seen: untick Select all in Family, Apply: "Visual Gallery (34 matched)" (screenshot 05b_family_none_ticked.png), not 0. A user who unticks everything gets everything, with no word about it. Place: gallery_handlers.py:201-203 (documented there as intended). Suggestion: say so on screen, or treat nothing ticked as nothing matched.
6. **No match: only a toast that disappears.** Seen: Family = Evolution + Pattern = "1 Numeric, 2 Categorical (Faceted)": 0 examples, the toast "No matches found for these filters." for a few seconds, the list empty, the main pane "Select an example to view preview." (screenshot 07_combo_empty.png). The count "Visual Gallery (0 matched)" sits at the top of the left panel, scrolled out of sight when the six filter panels are open. Place: gallery_handlers.py:232-235. Suggestion: a standing line in the main pane ("0 examples match these filters").
7. **Filters act only after Apply; nothing says so.** The help page and the panel do not mention the Apply button (app/src/help/gallery.md "Browsing"). Ticking a box changes nothing visible. Suggestion: one sentence in the help and the panel.
8. **At opening, for about a second, the dropdown shows "2D Bin Density" while the picture pane says "Select an example to view preview."** Screenshot 01_gallery_open.png; after 1.5 s the picture is there (walk3.json: the input value is already density_2d_bin). The first example is chosen without the user choosing; no stale content, only a flash. Place: gallery_handlers.py:76-82 and :171.
9. **Unexplained, not reproduced:** in the first filter pass, Geom = geom_line gave 34 instead of 3 (walk2.json). Repeated twice alone: 3 both times (walk3.json). Likely my script clicking before the checkbox change reached the server, but a real race (Apply read before the tick arrives) is not excluded; I could not tell.

Fine, checked: 1100 px and 1600 px: no sideways scroll (scrollWidth = clientWidth), no overlap seen in 13_width_*.png (the right info panel narrows the centre at 1100 px, still readable). Help (14_help_open.png): no "Send to Blueprint" remains; the text matches the screen except the missing Apply (finding 7). HOME after a Gallery visit: demo recipe 1_test_data_ST22_dummy opens, first plot draws, no Render error (12_home_after_gallery.png). Console errors: none in the whole walk; server log: no Traceback.

## What no existing test would catch
Reviewed names only (app/tests/test_gallery_*.py, test_shiny_gallery_left_out.py, test_convert_gallery_examples.py): they check the check at start, the listing without rejected examples, link attributes, the taxonomy panels' source, the pictures drawn from data. None drives the filters, the selection or the return from another space in a browser, so findings 1, 2, 5, 6, 7, 8 are uncaught; finding 3 (two names) and 4 (404) no test compares; the one browser test (left_out) covers a broken example only.

## Not covered
Real-user mouse paths on the native dropdown (I used select_option); the data-sample tab beyond row counts and two screenshots; the right info panel text; behaviour with SPARMVET_APP_FEATURES other than qa or a deployment with the gallery off; slow disks; the page in other browsers; the picture compared pixel by pixel (I compared the exact bytes of the file with the image src); whether the examples' recipe text is correct science (the full check is the existing test). Pytest skip reasons for part 1.
