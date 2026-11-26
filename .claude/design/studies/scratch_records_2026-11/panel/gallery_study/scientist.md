# Gallery study: scientist and data scientist viewpoint (2026-11-20)
Evidence: V = run or read, R = reasoned. Scratch: tmpAI/panel/gallery_study/sci/ (dump.py, dump.txt, chk.py, prev/). No repository file changed. The preview compare was run without --apply.

## 0. Verdict
No example can be trusted for its tags today as a matter of rule: the tags are author's words that nothing checks against the recipe or the data. The pictures can be trusted today (V: 34 of 34 identical to a fresh render), but nothing makes this stay true. Three examples teach something scientifically wrong (section 1.3).

## 1. Taxonomy as a classification
### 1.1 Are the axes well defined? (V: cheatsheet, spec lists, 34 recipes and TSVs)
- Family (6): defined by the question asked. Not derivable. Overlaps in use: same plot kind gets different families (boxplot_simple Distribution vs boxplot_faceted Comparison; violin_simple Distribution vs violin_faceted Comparison; jitter_strip Comparison vs beeswarm_sina Distribution, both show=distribution). Family and show overlap (show=distribution under family=Comparison).
- Pattern (10 values): the only axis that is a function of the recipe plus the declared types, but the definition is loose. "Numeric/Categorical" is counted as what? Columns in mapping, columns in facets, columns in the file? The authors counted inconsistently (1.2). The list has no "date" kind: "1 Year" is used for a numeric year, while two examples plot a String date.
- Difficulty (3): the cheatsheet says Simple = single geom, Intermediate = multiple geoms or position adjustment, Advanced = wrangling. The data break it: area_simple, line_simple, step_chart, scatter_smooth are Simple with 2 geoms (V); lollipop_advanced is named "Advanced" and tagged Intermediate; heatmap_correlation Advanced vs tile_simple Simple with the same geom. Partly derivable (count of geom layers) but the rule is not applied.
- Show (9): author's claim about the message. Wrong in places (1.2). Not derivable.
- Sample size (4): defined by n (any, <200, >=50, >=500) but n of what (rows, per group, per point)? The examples use row count of the file, which is the wrong denominator for grouped plots (1.2). Checkable by a number if the definition is made exact.
- Geom: derived = first geom_/stat_ layer (taxonomy.py:33-40). Not in a list (B5). The cheatsheet list of 20 holds for the 34 only because they were written to match.
- The five-axis mapping per plot entry is clear; the cheatsheet is stale (old `info.` form) and is read by no code (B3, B4).

### 1.2 Doubtful values (sampled all 34; each reason checked in the recipe mapping and the data)
- bar_simple: pattern "1 Numeric, 1 Categorical", but mapping is x=species, fill=amr_class, geom_bar counts rows; the numeric `value` column is unused. It is 2 categorical, no numeric. show=ranking: stacked counts, bars not ordered.
- bar_grouped: show=ranking; a dodged bar over species x drug_class is a comparison, no ordering is applied.
- boxplot_simple: pattern says 1 categorical; mapping has x=amr_class and fill=species (2 categorical). 16 boxes of median 6 obs (min 2) but sample_size medium+ (cheatsheet: n>=50).
- boxplot_faceted, violin_faceted, point_faceted: 16 cells, median 6 and 7 observations (min 2); sample_size medium+ / individual points. Pattern ok for boxplot/violin; point_faceted is "2 Numeric, 1 Categorical (Faceted)" but the plot has x=date (String), colour and two facet variables.
- bubble: pattern "2 Numeric, 1 Categorical", mapping has x, y and size numeric (3 numeric) plus colour.
- connected_scatter: pattern "2 Numeric" but group and colour are categorical (drug_class). show=trend while family=Correlation. `year` is not mapped, so order comes from file order (R).
- density_2d_bin: sample_size=large (cheatsheet n>=500), the file has 60 rows (V). geom_bin_2d with 15 bins on 60 points is mostly empty cells.
- density_simple, histogram_simple: pattern "1 Numeric", but fill=species / amr_class (1 numeric + 1 categorical).
- dumbbell: pattern "1 Numeric, 2 Categorical"; the second "categorical" is year_label, typed Int64, so the picture has a continuous colour bar 2015..2023 for two values (V picture). The geom tag geom_line hides that the plot is a line + two points.
- ecdf (10 per species), violin_boxplot (10 per species), qq_plot (15 per species), freqpoly (15 per species): sample_size medium+ although the groups are below the cheatsheet n>=50 (V: chk.py). ecdf Intermediate, freqpoly Simple: one geom each.
- error_bar: pattern "1 Numeric, 1 Categorical", mapping has y, ymin, ymax (3 numeric).
- heatmap_correlation: pattern "3 Numeric (Matrix)", but var1 and var2 are text names (1 numeric + 2 categorical, the same as tile_simple which is tagged "1 Numeric, 2 Categorical"). See 1.3 for the data.
- point_simple, point_faceted: pattern "2 Numeric", x=date declared String in the recipe (V: input_fields type String, 48 distinct dates), so the x axis is categorical text, not numeric. family Correlation / show relationship for a date axis is a time series, not a correlation.
- scatter_smooth: Simple, with two geoms.
- stacked_area: show=proportion, but position stack of counts, y axis "Total Isolate Count": absolute composition, not a proportion. Pattern "1 Numeric, 2 Categorical" while year is a time axis (line_grouped is "1 Year, ..."). Same for stacked_bar (counts, not shares); proportion_bar is the only one that normalises (V picture, position_fill).
- step_chart: pattern "1 Numeric, 1 Categorical" with year and drug_class and breakpoint (should be "1 Year, 1 Numeric, 1 Categorical" as line_grouped).
- ridgeline_advanced: the plot is geom_density with facet_grid rows (panels), not overlapping ridges; geom tag geom_density, the same as density_simple. The name promises something the recipe does not draw (R, from the layers).
- lollipop_advanced: needs a helper column `y_zero` = 0.0 in the data; 4 rows. Name "Advanced", difficulty Intermediate.
- area_simple, line_simple: sample_size medium+, 7 rows (a series of 7 points). medium+ speaks of observations; for a time series n is the number of points.

### 1.3 Scientific defects (a reviewer would stop the example)
1. heatmap_correlation is not a correlation matrix: the diagonal is -0.5, -0.8, -0.1, -0.9 (must be 1) and the matrix is not symmetric (MIC_A vs MIC_B = -0.3, MIC_B vs MIC_A = 0.85) (V: chk.py output). The example teaches how to draw a correlation heatmap from data that cannot be one.
2. tile_simple draws 100 rows into 16 tiles (2 to 13 per tile, median 6) with no aggregation: each tile shows one of the values (the last drawn), not a mean, silently (V picture and counts). The meta text presumably says a heatmap of the mean.
3. dumbbell: year_label (two values) shown with a continuous colour scale with ticks 2017, 2019, 2021 that do not exist.
These are not tag questions; they are examples whose recipe or data teach a wrong practice. No check can find them (the checker never sees the data, G2).

### 1.4 Is "data pattern" derivable?
- Partly. From mapping and facets and the declared types in input_fields (String/Float64/Int64/Date) one can compute: n numeric and n categorical columns used by aesthetics, whether a date column is present, whether a facet is present. Rule needed first: which aesthetics count (x, y, colour, fill, size, group, facet; are ymin/ymax/xend counted; is a numeric used as category counted as categorical).
- Not derivable from types alone: a numeric that stands for a category (year_label Int64), a year (Int64) versus a measure, a helper column (y_zero), a pre-aggregated table. These need a declared role or the author.
- What shows the limit: a derived value would give heatmap_correlation (text, text, numeric), tile_simple identical, which is right and would correct an inconsistency; it would give bar_simple "2 categorical", which has no value in the list, so the list would need a new value (the list is incomplete for count plots).

### 1.5 Checker versus author (proposal for the owner to weigh)
- The checker should: (a) check the five typed values and the geom against a list that lives in the spec; (b) compute the pattern from the mapping, facets and declared types and compare it with the author's value (error or advice; the Gallery would then show an author value that was proven, not asserted); (c) compare sample_size with the real n, per group when the plot is grouped, using the exact definition in the spec; (d) count geom layers against difficulty when the rule is exact; (e) check that every mapped column exists in the file and that the declared type fits the file (today only the preview script does, G2); (f) require that the tag strip equals the taxonomy at start, not only in a test.
- The author keeps: family, show, difficulty (judgement), the text of the guidance, the choice of the example data. These stay tagged as author's claim.
- What the checker cannot check: that the data are plausible for the story (1.3 point 1), that no aggregation is hidden (point 2). Those need a review of the data and one line in the guidance. Suggestion: a statement in the data description of how the table was made (simulated, summarised) because every example here is synthetic (R: REC_000 ids, round numbers).

## 2. Reproducibility of the picture
- How the preview is made (V): assets/scripts/gallery_previews.py draws through the app path (ConfigManager, DataOrchestrator, PlotEngines) at 960x600, 120 dpi, and compares pixel by pixel with the committed PNG. The app does not re-draw; it shows the file (gallery_handlers.py:165-170).
- Result today (V, run 2026-11-20, 34 s): identical 34, size only 0, differs 0, new 0, error 0. So today each picture is the plot of the shown recipe on the shown data, including the two seeded ones (beeswarm_sina and jitter_strip both write random_state: 0).
- What proves it stays current: nothing at run time. No hash of recipe, data, engine version or library version is stored; the start check does not look at the picture (G3, B6). The PNG metadata records only "Software: Matplotlib 3.10.9" (V). The committed pictures date from 2026-05-03 and the recipes from 2026-11-18 (git log, V): the match was proven only by the run above, by a person. A plotnine or matplotlib update, a font change, or an edit of a recipe or TSV makes the picture silently old; a font or version difference would also make the comparison fail for no scientific reason (R: pixel equality across machines is fragile).
- Seeds: only layers that draw random numbers need one (sina, jitter: present). geom_smooth lm, density, ecdf, qq, binning are deterministic (R). A shipped test says each gallery recipe writes its seeds (test_shipped_recipes_write_their_seeds.py, by name); a new random layer without a seed would be caught only if that test lists it.
- Data Sample tab versus picture: the tab reads the TSV plainly, the picture uses the typed contract (G5). Equal today; latent.
- Proposal (rule, not code): store with the index entry a fingerprint (hash of the recipe, the data file, the engine and library versions, the picture size) written when the picture is made; the start check compares and reports "picture out of date" in the same notice as a rejected example; the check must be exact on content, tolerant of nothing else. The user then knows the figure is of the shown recipe on the shown data, or is told it is not. Show the date or fingerprint status on the screen.

## 3. Several layers and the single `geom` tag
- 11 of 34 recipes have 2 or more geom/stat layers: area_simple, connected_scatter, dumbbell, heatmap_correlation, line_grouped, line_simple, lollipop_advanced, qq_plot, scatter_smooth, step_chart, violin_boxplot (V: dump.txt). The tag keeps the first.
- Consequences for a user who filters by "Primary Geom" (R): violin_boxplot is found under geom_violin and not under geom_boxplot, although the boxplot is half of what it teaches; dumbbell is found under geom_line though the key geometry is the point pair; lollipop under geom_segment; qq_plot under geom_qq (geom_qq_line not found); heatmap under geom_tile; line_simple under geom_line (the points are lost). proportion_bar and stacked_bar are geom_col and their meaning is in position_fill / position_stack, which are not geoms and not in the tag. geom_col serves Ranking, Part-to-Whole and Comparison examples: the geom does not discriminate.
- "First" is an order of writing, not a statement of importance; moving a line in the recipe changes the tag. It is derived, hence reproducible, but its meaning is thin.
- Options (the owner decides): (A) keep the first and say so on the label ("first geom layer"), accept the loss; (B) derive all geom layers and filter on any (a list per example; the pivot becomes many-to-many; this is what a user who looks for "boxplot" expects); (C) author names the primary geom in the taxonomy and the checker verifies it is one of the layers (this reverses D-0034/D-0039 "derived", flag to the owner). B keeps the derived principle and changes the index shape (flag: reopens a detail of D-0039).
- One plot per example is required (GP01). Keep it: a second plot would have its own taxonomy and the tag strip, the index and the picture assume one.

## 4. Pitfalls and tests
- Tags cannot be right if the data are not the data of the story; test that every example's n and group sizes are computed and compared with its sample_size.
- Test: a recipe whose mapping column is not in the TSV must be rejected at start, not only by the script.
- Test: an edit of a recipe or TSV makes the index report a stale picture.
- Test: a taxonomy change rewrites the index (B6), then the filter shows the new value.
- Test for the derived pattern: a fixture with a numeric year, a String date, a numeric coded category, a helper column, to show where derivation and author disagree.
- Not verified: the text of the guidance files against their plots (only 3 read in part), the dead links, the behaviour on another machine (fonts), whether the pattern rule I suggest fits all 34 (not run; I counted by hand from the mapping).
