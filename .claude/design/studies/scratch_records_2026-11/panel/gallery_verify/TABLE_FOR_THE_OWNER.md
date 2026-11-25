# Gallery: the critical check of all 34 examples, one table for the owner (D-0401, D-0402, D-0403)

Date: 2026-11-21. Status: for you to read. Nothing in the Gallery, the recipes, the data, the texts or the pictures is changed. Every "Suggestion:" is a viewpoint's proposal, not a decision.

## 0. How to read this

- Four viewpoints checked the 34 examples: data scientist 1 (17 examples, area_simple to histogram_simple), data scientist 2 (17 examples, jitter_strip to violin_simple), a statistician (all 34), a user new to data science (all 34).
- The statistician's answers came from the data scientist agent, briefed with the statistician's question, because no statistician agent exists. It is a second look by the same kind of agent, not an independent person.
- RUN = a program was run. READ = a file was read. SEEN = the picture was looked at. REASONED = a conclusion without a test. The name after each label is who gave it.
- RUN, all 34 (data scientists 1 and 2): each example was redrawn with the app's own function. All 34 pictures are identical to the stored `preview_plot.png` (data scientist 2: 0.000 percent of pixels differ). The statistician and the user looked at the stored pictures only.
- Only READ or SEEN: the guidance pages (all 34 by the user, the others by the data scientists), the claims about biology, EUCAST and statistics (section 8).
- Nothing was changed. A picture changes only after you have seen it.

Words used in this file:
- **geom**: a layer that draws the marks (points, bars, lines).
- **facet**: the picture split into small panels, one per group.
- **cell**: one panel, or one species-and-class pair of a table.
- **bin**: a slice of values that are counted together.
- **kernel**: the smoothing rule behind a density curve or a violin.
- **dodge**: bars or boxes of subgroups placed side by side.
- **IQR**: the spread of the middle half of the values.
- **CI**: confidence interval, a range around an average.
- **ties**: several rows with exactly the same value.
- **T3**: an extra step list for one plot. The pages mention it. No example has one.
- **tag**: a typed label on the example (family, pattern, sample size, difficulty, what it shows).

## 1. Facts common to many examples

1. **No example has a step.** All 34 recipes have `steps: []`. The picture shows the raw table. Several pages talk about "Tier 2", "T3" or a `summarize` step that does not exist (RUN/READ, data scientists 1 and 2; the user lists "T3, Tier 2" as jargon).
2. **Ten examples use a table of random numbers, not MIC values.** The columns `mic_value`, `growth_index` and `value` run from about 0 to 128, evenly spread. Real MIC values sit on doubling steps (0.06, 0.125, 0.25 ... 64).
   - The ten (READ by me, first lines and ranges of the data files; ids `REC_nnn`): bar_simple (`value` 0.99 to 125.5), boxplot_faceted (3.6 to 126.5), boxplot_simple (4.3 to 127.4), density_simple (1.5 to 127.1), histogram_simple (6.8 to 126.9), point_faceted (0.6 to 127.9), point_simple (0.6 to 125.1), tile_simple (0.7 to 127.6), violin_faceted (1.9 to 127.2), violin_simple (2.0 to 127.0).
   - Evidence: RUN by the statistician: a test against an even spread gave p 0.20 to 0.82 on four of them (density_simple, histogram_simple, violin_simple, boxplot_simple). Species and class are independent of the value (statistician, RUN). For the other six the statistician READ the same id pattern and range. Data scientist 1 and 2 reached the same reading for their examples (RUN).
   - Consequence (statistician, REASONED): every comparison between groups in these examples compares noise. The pages must not invite a biological reading.
   - ridgeline_advanced has ids `REC_0..` too but its `growth_index` runs 8.6 to 91.9 (READ by me, same as data scientist 2): not the same range.
3. **Five examples hold real-looking MIC values on doubling steps**: beeswarm_sina, ecdf, freqpoly, violin_boxplot, qq_plot (READ by me; data scientists RUN). The same dilution is written differently: 0.12 (beeswarm_sina, freqpoly), 0.125 (ecdf, violin_boxplot, qq_plot), 0.062 (ecdf, violin_boxplot). The true values are 0.125 and 0.0625 (data scientist 2: ratio 2.016 instead of 2).
4. **No example shows n (how many values stand behind a mean, a box or a violin).** The summary tables hold no n column, except line_simple (`n_isolates`, not drawn).
5. **Cells with very few values.** Five examples draw 16 cells from 100 rows. The cells hold 2 to 14 values (RUN): boxplot_faceted 2 to 11, boxplot_simple 2 to 14, violin_faceted 2 to 12, point_faceted 2 to 11, tile_simple 2 to 13. I recounted point_faceted: 16 cells, 2 to 11 (READ).
6. **Sentences pasted on many pages** (READ by data scientists 1 and 2 and the user; the lists agree):
   - "This is a basic demonstration of `geom_X` mapping" and "Visualize categorical patterns and distributions within your scientific datasets": bar_simple, boxplot_faceted, boxplot_simple, density_simple, histogram_simple, violin_simple, tile_simple, violin_faceted, point_simple, point_faceted (10 pages; wrong for density, histogram and point).
   - "Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap)": heatmap_correlation, ridgeline_advanced, lollipop_advanced.
   - "advanced layer stacking and coordinate manipulation": the same three pages. False for heatmap_correlation (tile and text) and ridgeline_advanced (no coordinate layer). Partly true for lollipop_advanced (it has a flip of the axes; data scientist 2).
   - A list "contains headers: ..." instead of a description (user: 13 pages).
   - Slang headings (user): 'Staple', 'Quality Control', 'Flavor Profile', 'Inventory', 'Gourmet', 'Trace', 'Multi-Course', 'Interaction Matrix', 'Comparative'.
7. **Linear axes for doubling values.** ecdf, freqpoly, beeswarm_sina, violin_boxplot (MIC) and step_chart (breakpoints) use a linear axis. The doubling steps crowd into the lowest part of the picture (SEEN, data scientists and statistician).
8. **Colour legend that repeats the x axis**: jitter_strip, beeswarm_sina, boxplot_faceted, error_bar, ridgeline_advanced, violin_faceted, violin_simple, violin_boxplot (SEEN). Legend titles are raw column names in lower case (species, drug_class, amr_class) in many examples.
9. **"What does one count count?"** proportion_bar and stacked_bar: the data do not say whether a count is an isolate or a resistance record. If an isolate can carry several classes, shares are shares of records (data scientist 2 and statistician, REASONED; the user asks the same).
10. **Paired examples that do not share data.** proportion_bar and stacked_bar: E. coli total 287 against 254; E. coli Tetracycline 48 against 36 (data scientist 2 and statistician, RUN; I recomputed the totals from the files, READ). line_simple and line_grouped: the 2018 value is 37.7 in one and 46.2 as the mean of the species in the other (data scientist 2, RUN).
11. **Causal sentences a chart cannot support**: line_grouped ("system-wide pressure", "clonal spread"), line_simple ("treatment policy effectiveness"), connected_scatter ("feedback loops"), error_bar ("overlapping bars suggest ... not differ significantly").

## 2. The verdict table, 34 examples, alphabetical

Verdict words are each viewpoint's own. Data scientist and statistician: SOUND, MINOR, WRONG. User: CLEAR (can act), UNCLEAR (something stops me), MISLEADING (I would believe something false). "New picture" is what the data scientists said. The statistician gave no view on pictures.

| example | data scientist | statistician | user | main problem in one plain sentence | strongest evidence | needs a new picture | fit for a demo today |
|---|---|---|---|---|---|---|---|
| area_simple | MINOR (1) | WRONG | MISLEADING | The page says the area is a running total, but the data are a yearly percentage, so the filled area means nothing. | READ page; RUN data: 7 rows, 51.6 to 63.0 (all three) | no | no as written (statistician, user). Data scientist 1: yes after the text is fixed |
| bar_grouped | MINOR (1) | MINOR | CLEAR | E. faecalis cephalosporin is 0.0, drawn as an empty space; it looks missing and is doubtful biology. | RUN: value 0.0 (data scientists, statistician); SEEN; I READ the file | yes, only if the value changes | with a caveat: the E. faecalis gap (data scientist 1, statistician) |
| bar_horizontal | MINOR (1) | MINOR | MISLEADING | The page promises a ranking, but the bars are alphabetical, and "pre-sort the file" does not work. | SEEN: file sorted 31.9 to 62.9, picture alphabetical (all three); data scientist 1 RUN | yes | with a caveat: do not call it a ranking (data scientist 1) |
| bar_simple | MINOR (1) | MINOR | UNCLEAR | Bars count rows (the `value` column is unused), but the tag says a number is plotted. | RUN: counts 23, 25, 29, 23 (data scientist 1, statistician); READ recipe | no | statistician silent; data scientist 1: yes. Caveat: say that bars count rows |
| beeswarm_sina | WRONG (1) | WRONG | UNCLEAR | Five equal values are drawn on one spot, so "each dot is one observation" is false. | RUN: 18 distinct (species, value) pairs for 100 rows (data scientist 1); statistician RUN: 4 to 5 values per species | yes | no (data scientist 1, statistician) |
| boxplot_faceted | MINOR (1) | WRONG | UNCLEAR | Boxes made from 2 to 11 values look as solid as boxes from 30; no n is shown. | RUN: cells 2 to 11 (data scientist 1, statistician) | no (yes if the data change) | data scientist 1: with caution. Statistician: no |
| boxplot_simple | MINOR (1) | WRONG | UNCLEAR | The page does not say the picture has 16 boxes (4 by 4); cells hold 2 to 14 values; the tag says one category. | RUN: cells 2 to 14 (data scientist 1, statistician) | no (yes if the data change) | data scientist 1: with caution. Statistician: no |
| bubble | WRONG (1) | WRONG | MISLEADING | Fractions (0.26 to 0.68) are labelled "% Resistant"; the x axis is the sample size; only 5 points. | SEEN legend 0.3 to 0.6; RUN: values (all three) | yes | no (all) |
| connected_scatter | MINOR (1) | WRONG | UNCLEAR | The path follows the row order of the file, not the year, and no year is shown; the page says the opposite. | RUN by data scientist 1: shuffled copy makes a zigzag | yes | data scientist 1: with caution. Statistician: no |
| density_2d_bin | WRONG (1) | MINOR | MISLEADING | The page says dark rectangles mean many isolates; dark is 1, yellow is 4. | RUN, SEEN: dark purple 1, yellow 4 (data scientist 1, user); tag "large" for 60 rows | yes | no (data scientist 1, user) |
| density_simple | WRONG (1) | WRONG | MISLEADING | The E. coli curve is hidden behind the others, though the legend lists it. | RUN: its density is under the others at 100 percent of x (data scientist 1); SEEN (all) | yes | no (all) |
| dumbbell | MINOR (1) | MINOR | UNCLEAR | The legend is a colour bar from 2015 to 2023 although only two years exist. | SEEN; READ: `year_label` typed Int64 while the page says Categorical (all three) | yes | with a caveat: the legend (data scientist 1) |
| ecdf | MINOR (1) | MINOR | CLEAR | The linear axis squeezes the doubling values into 0 to 4; "one step = one observation" is false with ties. | SEEN; RUN: 8 distinct values, 14 tied rows (data scientist 1) | optional | yes, saying the axis is linear (data scientist 1, statistician) |
| error_bar | MINOR (1) | MINOR | UNCLEAR | The title says "95% CI" but nothing in the data says so; the overlap sentence leads to a wrong inference. | READ; statistician RUN: intervals symmetric around the mean | no | data scientist 1: yes. Caveat: the overlap sentence |
| freqpoly | WRONG (1) | WRONG | MISLEADING | A bin width of 0.5 on raw MIC gives isolated spikes; the page advice contradicts the example. | RUN, SEEN: 130 bins, 6 to 7 filled per species (statistician); 45 rows, 42 ties (data scientist 1) | yes | no (all) |
| heatmap_correlation | WRONG (1) | WRONG | MISLEADING | It is not a correlation matrix: the diagonal is not 1 and the matrix is not symmetric; labels are unreadable. | READ by me: diagonal -0.5, -0.8, -0.1, -0.9; A,B -0.3 but B,A 0.85 | yes | no (all) |
| histogram_simple | MINOR (1) | MINOR | UNCLEAR | The page does not say the bars are stacked by class; 30 bins for 100 random values show noise. | RUN: bin width 4, heights 1 to 7 (data scientist 1, statistician) | no | data scientist 1: yes. Caveat: noise and the stacking |
| jitter_strip | SOUND (2) | MINOR | CLEAR | Nothing is wrong in the picture; "a percentage per isolate" is unclear and colour repeats the x axis. | RUN: 100 rows, 18 to 22 per species (data scientist 2); SEEN | no | yes (data scientist 2, statistician) |
| line_grouped | MINOR (2) | MINOR | CLEAR | Two causal sentences; 7 means per line with no n; the tag says medium+. | RUN: 35 rows, 7 per line (data scientist 2); statistician: jumps up to 7.4 points | no | yes (data scientist 2). Statistician: yes, do not read the jumps |
| line_simple | MINOR (2) | MINOR | UNCLEAR | The y axis starts at 38, n per year is hidden, and the rise is not significant (p = 0.22). | RUN: statistician's model on n_isolates 56 to 116; READ data | no | data scientist 2: yes with a caution. Statistician did not list it |
| lollipop_advanced | WRONG (2) | MINOR | MISLEADING | The dots sit at 0 and the stick carries the value; the axis is named `y_zero`. | SEEN (data scientist 2, user); RUN: a fix on a copy puts dots at 63.0, 64.7, 86.2, 56.0. Statistician did not look at the picture | yes | no (data scientist 2) |
| point_faceted | WRONG (2) | WRONG | MISLEADING | The date is typed as text: an unreadable x axis, equal spacing, and all dates are in two Januaries. | RUN: dates in Jan 2024 or Jan 2025 only (data scientist 2, statistician); SEEN | yes | no (all) |
| point_simple | WRONG (2) | WRONG | MISLEADING | Same cause: two January snapshots look like one continuous series. | RUN on a copy with type Date: two clouds with a gap (data scientist 2) | yes | no (all) |
| proportion_bar | MINOR (2) | MINOR | CLEAR | The page says "fraction of isolates"; the data count records; the pair stacked_bar holds other numbers. | RUN: 48/287 = 0.167 matches the picture (data scientist 2); READ totals 190 to 287 | no | yes (data scientist 2, statistician) |
| qq_plot | MINOR (2) | MINOR | UNCLEAR | The page is wrong on S-curves and skew, says "tests", and the title says log where the data are log2. | RUN: log_mic = log2(mic_value) exactly (data scientist 2, statistician) | only if the axis label changes | with a caveat: remove the S-curve sentence (data scientist 2, statistician) |
| ridgeline_advanced | MINOR (2) | MINOR | UNCLEAR | It is four separate panels, not a ridgeline, and each panel has its own height scale. | SEEN; RUN (data scientist 2: curves cut at 8.6 and 91.9) | optional | with a caveat: call it a faceted density (data scientist 2). Statistician: yes |
| scatter_smooth | SOUND (2) | MINOR | CLEAR | Right plot; the page names LOESS but only a straight line is drawn; 9 points per species. | RUN: slopes 1.93, 1.99, 1.26 (data scientist 2, statistician) | no | yes, saying "linear fit" (data scientist 2, statistician) |
| stacked_area | MINOR (2) | MINOR | CLEAR | The tags say proportion and a wrong pattern; shares are hard to read in a stack of counts. | RUN: yearly totals 315 to 538 match the picture (data scientist 2) | no | data scientist 2: yes. Statistician did not list it. Caveat: the tags |
| stacked_bar | SOUND (2) | MINOR | CLEAR | Right plot; the unit of a count is not said; the bars are alphabetical. | RUN: totals 254, 232, 214, 282, 212 match (data scientist 2); READ | no | yes (data scientist 2, statistician) |
| step_chart | MINOR (2) | MINOR | MISLEADING | The Carbapenems line is hidden under the others, and "EUCAST" values are not shown to be real. | SEEN; READ data: 6 of 15 rows repeat the previous value | yes | with a caveat: say the values are illustrative (data scientist 2). Statistician: yes, ignore EUCAST |
| tile_simple | WRONG (2) | WRONG | UNCLEAR | The colour of each square is the last row of that cell in the file, not an average. | RUN: 16 of 16 cells match the last row; the mean matched 0 (data scientist 2) | yes | no (all) |
| violin_boxplot | WRONG (2) | WRONG | UNCLEAR | The linear axis squeezes the shapes; a needle runs to 64; n is 10 per species. | SEEN; RUN: S. aureus maximum is 2.0 (data scientist 2); needle cause REASONED | yes | no (all) |
| violin_faceted | WRONG (2) | WRONG | UNCLEAR | Violins are drawn from 2 to 12 values; a violin of 2 values is a flat rectangle. | RUN: cells 2 to 12 (data scientist 2, statistician) | yes | no (all) |
| violin_simple | MINOR (2) | MINOR | UNCLEAR | Random data show two bulges that look like two groups; no n and no median. | RUN: 20 to 28 per class; KS test: even spread (statistician) | yes, if a layer is added | with a caveat (data scientist 2). Statistician: yes |

(1) = data scientist 1. (2) = data scientist 2.

**Counts per viewpoint** (my count of the table above):

| viewpoint | worst | middle | best |
|---|---|---|---|
| data scientists 1 and 2 together | WRONG 12 (6 and 6) | MINOR 19 (11 and 8) | SOUND 3 (jitter_strip, scatter_smooth, stacked_bar) |
| statistician | WRONG 14 | MINOR 20 | SOUND 0 |
| user | MISLEADING 11 | UNCLEAR 15 | CLEAR 8 |

The user's own report says MISLEADING 10, UNCLEAR 15, CLEAR 9. I recounted its table: 11, 15 and 8 (CLEAR: bar_grouped, ecdf, jitter_strip, line_grouped, proportion_bar, scatter_smooth, stacked_area, stacked_bar). I use my count.

**Examples where the viewpoints DISAGREE on the verdict** (one viewpoint says WRONG or MISLEADING, another does not). Read the user's UNCLEAR as the "middle" class.

| example | data scientist | statistician | user |
|---|---|---|---|
| area_simple | MINOR: the area has a wrong meaning, but the text can be fixed | WRONG: a rate read as a total | MISLEADING |
| bar_horizontal | MINOR | MINOR | MISLEADING: a user who follows the advice still gets an unranked chart |
| beeswarm_sina | WRONG | WRONG | UNCLEAR: sees the overlap, not a false teaching |
| boxplot_faceted | MINOR | WRONG: quartiles from 2 to 5 values | UNCLEAR |
| boxplot_simple | MINOR | WRONG | UNCLEAR |
| connected_scatter | MINOR | WRONG: "geom_path ensures order" is false | UNCLEAR |
| density_2d_bin | WRONG | MINOR | MISLEADING |
| lollipop_advanced | WRONG: dots at 0 (SEEN) | MINOR: the picture was not looked at | MISLEADING |
| step_chart | MINOR | MINOR | MISLEADING: reads real EUCAST numbers |
| tile_simple | WRONG | WRONG | UNCLEAR: it did not know that the colour is one row |
| violin_boxplot | WRONG | WRONG | UNCLEAR |
| violin_faceted | WRONG | WRONG | UNCLEAR |

Smaller differences (best against middle class): jitter_strip, scatter_smooth and stacked_bar are SOUND for data scientist 2, MINOR for the statistician, CLEAR for the user. bar_grouped, ecdf, line_grouped, proportion_bar and stacked_area are MINOR for both technical viewpoints and CLEAR for the user.

Why they differ (my reading, REASONED): the user did not run anything, so it sees what the text and picture show but not that a colour is one row, or that a box holds 2 values. The statistician did not look at 8 pictures, among them lollipop_advanced, so the dots at 0 were not seen. The statistician judges what a plot teaches about a real analysis, so it rates a text that misleads as WRONG where the data scientists rate it as a text fix.

## 3. Examples judged WRONG or MISLEADING by any viewpoint (18)

Order: I took the statistician's ranking "by harm to a user's real analysis" as the start (its five groups, then its "next" list), then added the four examples it did not rank. The order of the last four (lollipop_advanced, density_2d_bin, bar_horizontal, step_chart) is mine and is not a ranking of harm. Every correction is a "Suggestion:" of a viewpoint.

### 3.1 tile_simple (statistician rank 1)
- **What the user of the Gallery sees:** a 4 by 4 grid of coloured squares, "growth index by species and class", read as a mean per square.
- **What is wrong:** the table has 100 rows for 16 cells. The plot draws one tile per row on top of each other. The visible colour is the last row of the cell in the file (RUN, data scientist 2: 16 of 16 cells within 2 index units; the mean matched 0 cells, the median 1). The statistician found the same (RUN: correlation of last row and mean 0.47; E. coli by Aminoglycoside: mean 50.5, last row 27.2). Shuffle the file and the picture changes (data scientist 2, REASONED from the result). Nothing in the page says so. The tags (family Correlation, show relationship) do not fit (statistician, data scientist 2).
- **Suggestion (data scientist 2, statistician):** add a visible step that makes one row per cell with the mean (or median) and n, then map the colour to it. Changes: recipe (a step), picture, legend title ("Mean growth index"), page text, tags. Teaches: aggregate before you draw.
- **Suggestion (statistician, option b):** keep it and state that the colour is one raw row. The statistician does not recommend it for a Gallery example. Teaches: nothing useful.
- **Suggestion (user):** the page says "each tile must have exactly one value; if you have several, summarise first".
- **Tried:** the pixel test on the stored picture (RUN). **Not tried:** the correction itself. Whether the recipe format offers a mean-per-cell step by name was not checked by any report. The rules file lists `polars_group_by` and `polars_mean` as registered actions (READ by me, not tested).

### 3.2 heatmap_correlation (rank 2)
- **What the user sees:** a "correlation" grid with white numbers about 5 pixels high, unreadable on pale squares; axes `var1` and `var2`.
- **What is wrong:** the diagonal is -0.5, -0.8, -0.1, -0.9 and the matrix is not symmetric (A,B -0.3; B,A 0.85) (READ by me; RUN by the statistician: largest asymmetry 1.16, and the symmetrised matrix has a negative eigenvalue, so it is not a correlation matrix of any data). The recipe computes nothing. The colour scale follows the data (-0.9 to 0.85), not -1 to 1. The page text on layers and the "Look for peaks" sentence are pasted (section 1). The user's report gives the diagonal as "-0.5, 0.0, -0.1, -0.9"; the file says -0.8 for the second value.
- **Suggestion (statistician a, data scientist 1):** build the matrix from real isolate-level columns with a correlation step, so it is symmetric with a diagonal of 1. Changes: data, recipe, page, picture. Teaches the computation.
- **Suggestion (statistician b, data scientist 1):** rename it "heatmap of a value matrix" and use values with no correlation meaning. Changes: name, data, page. Removes the false claim. The name is yours to choose (Q1 draft).
- **Suggestion (all):** readable labels (dark text, larger, rounded), a fixed scale -1 to 1, state the method and n.
- **Tried:** nothing. **Not tried:** both corrections.

### 3.3 boxplot_faceted (rank 3)
- **What the user sees:** four panels, four boxes each, from 100 random "MIC" values (4 to 127).
- **What is wrong:** cells hold 2 to 11 values (RUN, data scientist 1 and statistician); S. aureus by Tetracycline has 2. A box of 2 to 5 values is not a quartile estimate. The tag `medium+` counts the total. The page says nothing about n per box. The values are not MIC (section 1).
- **Suggestion (statistician, data scientist 1):** show the points over the boxes and n per box, or use a bigger file with at least 10 per cell. Changes: recipe (a layer), data, page, picture. Teaches: boxes need enough values.
- **Suggestion (user):** say what box, line and dot are, and how many values a box needs.
- **Tried:** nothing. **Not tried:** a points layer.

### 3.4 boxplot_simple (rank 3)
- **What the user sees:** four clusters of four boxes. The page never says there are 16 boxes. The box width differs without a legend (data scientist 1: SEEN, not explained).
- **What is wrong:** cells hold 2 to 14 values (RUN). The two outlier dots come from boxes of 5 to 9 values, where the 1.5 IQR rule is meaningless (statistician). The tag says one category; the plot uses two (data scientist 1, statistician). The page calls it a "Quality Control" plot (data scientist 1, user).
- **Suggestion (statistician a):** one grouping with n of 20 to 35 each. **(b):** keep two groupings, at least 10 per cell, and draw the points. **(data scientist 1):** pattern tag to `1 Numeric, 2 Categorical`, which exists.
- **Tried / not tried:** nothing was tried.

### 3.5 violin_faceted (rank 3)
- **What the user sees:** 16 violins in four panels. K. pneumoniae by Fluoroquinolone is a flat rectangle.
- **What is wrong:** each violin is built from 2 to 12 values (RUN, data scientist 2, statistician). Rounded waists and bulges are noise. Colour repeats the x axis. The values are not MIC. The page says "advanced architectural partitioning" for a Simple recipe.
- **Suggestion (statistician, data scientist 2):** drop cells under about 10 or enlarge the data; show the points and n.
- **Tried / not tried:** nothing was tried.

### 3.6 violin_boxplot (rank 3)
- **What the user sees:** shapes squeezed into 0 to 10 on a 0 to 64 axis. A thin black line runs up to 64 over every species, also S. aureus whose maximum is 2.0.
- **What is wrong:** MIC is on a linear axis. n is 10 per species with 6 to 8 distinct values (RUN, statistician). The line is the empty tail of the violin because `trim` is false (REASONED, data scientist 2 and statistician; not isolated by a run). The density below 0 shows under the axis. The page calls MIC "Numeric (continuous)"; it is discrete and on a doubling scale. "Bimodal = double waist" is noise at n = 10.
- **Suggestion (data scientist 2, statistician a):** log2 y axis, `trim` true, points over the box. **(statistician b):** use the ecdf or the sina for n of 10. A tag `individual points` would then be true.
- **Tried / not tried:** nothing was tried. The log2 axis layer was not checked in the format.

### 3.7 freqpoly (rank 4)
- **What the user sees:** a flat line with thin spikes at 0.25, 1, 2, 4, 8, 16, 32, 64.
- **What is wrong:** bin width 0.5 on raw MIC makes 130 bins with 6 to 7 filled per species (RUN, statistician). The page says 0.5 is for log2 steps; the x is not log2. n is 15 per species, counts not shares. K. pneumoniae spikes at 32 and 64 read as two peaks (data scientist 1).
- **Suggestion (statistician a, data scientist 1):** plot log2(MIC) with bin width 1 (one bin per step); more rows (at least 50 per species). **(statistician b):** keep raw MIC and use the ecdf, which needs no bin choice. The page must be corrected in both.
- **Tried:** the bins were computed (RUN). **Not tried:** a log2 step or a new picture.

### 3.8 beeswarm_sina (rank 4)
- **What the user sees:** points in four narrow stacks. E. faecalis shows 4 dots for 20 values.
- **What is wrong:** every value occurs 5 times (10 for two) (RUN, data scientist 1). The dot at 16 is 25 percent of that species but looks like one outlier. "Each dot is one observation" is false. The linear axis puts all information into 0 to 4. The legend repeats the x axis.
- **Suggestion (statistician a):** log2 axis and a count mark (`geom_count`) for discrete MIC. Teaches: MIC is discrete and logarithmic. **(statistician b):** keep the sina but use truly continuous data (growth index). Teaches: the sina is for continuous values. **(data scientist 1):** more varied values, or a log2 axis, or smaller alpha; remove the colour legend; write 0.125, not 0.12.
- **Tried / not tried:** nothing was tried.

### 3.9 point_simple (rank 5)
- **What the user sees:** 48 overlapping rotated date labels; one cloud of points that looks like a continuous time series.
- **What is wrong:** `date` is typed String, so the axis has one slot per date, equally spaced. The data are two blocks: 50 rows in January 2024, 50 in January 2025 (RUN, data scientist 2). The one-year gap is invisible. No trend: correlation -0.13 (data scientist 2) or Spearman -0.07, p = 0.49 (statistician); both RUN, on slightly different measures.
- **Suggestion (data scientist 2, statistician):** type the date as Date. **Tried (RUN, data scientist 2):** a scratch copy with `date: {type: Date}` renders two clouds with an empty gap and labels from 2024-01-01 to 2025-01-01. **Not tried:** whether a Date axis works in every recipe path of the app; no existing Gallery recipe uses a Date.
- **Suggestion (data scientist 2):** also use data with a numeric x or a real spread of dates, and fix tags and text. Teaches: type your dates.

### 3.10 point_faceted (rank 5)
- **What the user sees:** four columns by four rows of panels; the x labels print over each other as a black smear; strip text is cut.
- **What is wrong:** same date typing and two-January data as point_simple (RUN, data scientist 2, statistician). Cells hold 2 to 11 points (RUN; the user reports "1 to 8", which my recount of the file does not support). Colour repeats the row facet. The tag `2 Numeric, 1 Categorical (Faceted)` is wrong (section 5). `relationship` is not read from the picture: correlation 0.04.
- **Suggestion (data scientist 2):** date as Date, fewer axis labels, spread dates, drop colour or the row facet, fix tags and text. **(statistician):** Date type, and a tag per panel.
- **Tried:** the Date type on point_simple only. **Not tried:** on this example.

### 3.11 connected_scatter (rank 5)
- **What the user sees:** two coloured paths with dots; no year labels, no arrows. The Fluoroquinolone path has a back-step in 2020.
- **What is wrong:** `geom_path` joins in row order, not year order. The page says "Year (determines path order)" and "use geom_path ... to ensure correct temporal ordering": false (RUN, data scientist 1: a shuffled copy draws a zigzag). It works only because the file is sorted. A user with an unsorted file gets a tangle without warning (statistician). The title says "(Connected by Year)" but no year is shown. Causal words ("feedback loops"): two series that rise with time correlate by time alone (statistician RUN: r 0.64 and 0.86 within class, 8 points).
- **Suggestion (data scientist 1, statistician):** add an explicit sort by class and year in the recipe; label the first and last year or add an arrow; rewrite the geom_path sentence; remove causal wording; pattern tag to `2 Numeric, 1 Categorical`. Changes: recipe, page, picture, tag.
- **Tried:** the shuffled copy (RUN). **Not tried:** the sort step or the labels.

### 3.12 density_simple (statistician "next" list)
- **What the user sees:** three filled curves and a legend with four species.
- **What is wrong:** the fills are opaque (`params: {}`), so E. coli is covered at 100 percent of the x values (RUN, data scientist 1: `dens.py`). The page says it shows "a single numeric variable". n is 20 to 29 per curve; the bumps are kernel noise from random data (statistician). The y label "density" is not explained.
- **Suggestion (data scientist 1, statistician):** alpha about 0.4 (a recipe parameter) or one panel per species; a page text on overlapping curves, and that the area of each curve is 1.
- **Tried:** the density comparison was computed (RUN). **Not tried:** the alpha.

### 3.13 bubble (next list)
- **What the user sees:** five bubbles; size legend "% Resistant" with 0.3 to 0.6; y axis "Mean Resistance (%)" 33 to 63 for the same species.
- **What is wrong:** `pct_resistant` is a fraction (0.26 to 0.68) labelled as percent. Two resistance numbers per species are never told apart (E. coli: 0.39 and 46.7). The x axis is the sample size (collection effort). With 5 points no correlation can be judged (statistician RUN: r = -0.30); the page says "position reveals correlation".
- **Suggestion (data scientist 1, statistician):** data in percent or the label "Fraction resistant (0 to 1)"; explain or drop one of the two resistance columns; put sample size as the bubble size and a meaningful predictor (for example year or consumption) on x; remove the word "correlation". Changes: data, recipe, labels, page, picture.
- **Tried / not tried:** nothing was tried.

### 3.14 area_simple (next list; statistician WRONG, data scientist MINOR)
- **What the user sees:** a blue filled area from 0, titled "Resistance Burden Over Time", described as "accumulating resistance burden".
- **What is wrong:** the y value is a yearly percentage (7 points, 51.6 to 63.0). The area under a rate has no unit meaning. The fill adds nothing to a line.
- **Suggestion (statistician a):** use a line chart for a rate (line_simple already is one). **(statistician b):** change the data to a true cumulative count and say so. Teaches: an area is for additive totals. **(data scientist 1):** keep the 0 baseline; rewrite the interpretation text; title "Resistance rate over time". **(user):** "use this only when the area is a quantity you can add up".
- **Tried / not tried:** nothing was tried.

### 3.15 lollipop_advanced
- **What the user sees:** four dark-red dots all sitting at 0; grey sticks run from the dots to the value; the axis is named `y_zero`; the numbers are turned 45 degrees.
- **What is wrong:** the mapping puts the dot at the helper column `y_zero` (a constant 0) (SEEN, data scientist 2 and user; READ recipe). The sticks carry the right lengths, so it is not a lollipop chart. The tag says ranking, but the species are alphabetical. The page does not list `y_zero`.
- **Suggestion (data scientist 2):** swap `y` and `yend` in the mapping. **Tried (RUN, scratch copy):** the mapping `{x: species, y: avg_growth, xend: species, yend: y_zero}` renders with dots at 63.0, 64.7, 86.2 and 56.0 and sticks to 0; the axis then reads `avg_growth`. Also: species as an ordered type by value, or say the example is unsorted; `labs` for the axis; rewrite the pasted text. **(statistician):** sort by value, show n, document `y_zero`. A lollipop of a mean carries the same information as a bar (statistician).
- **Not tried:** the sorting.

### 3.16 density_2d_bin
- **What the user sees:** about 35 rectangles coloured by count; the page says dark means many isolates.
- **What is wrong:** yellow is 4, dark purple is 1 (RUN, SEEN; data scientist 1 and user). 15 bins of width 0.53 and 0.60 do not fit the integer log2 values: each value sits on the edge of a bin (an edge of -8.9e-16, data scientist 1, RUN), and alternate columns are empty (statistician RUN: 2, 5, 0, 7, 0, 10, 0). Total counts equal 60, so no row is lost. The tag says `large` for 60 rows. It is a 2D histogram, not a density.
- **Suggestion (data scientist 1):** bin width 1 centred on the integers, or a tile or count plot of the 35 cells; correct the colour sentence; tag `medium+`. **(statistician):** bins equal to the dilution steps, or `geom_count`; page "joint counts". **(user):** "bright (yellow) bins hold the most isolates"; drop "independent resistance mechanisms".
- **Tried:** the bin arithmetic (RUN). **Not tried:** a new binning.

### 3.17 bar_horizontal
- **What the user sees:** five bars in alphabetical order (Aminoglycoside at the bottom) under a page that promises a ranking.
- **What is wrong:** the file is sorted from 31.9 to 62.9 but the order of the file does not set the bar order for a text column (SEEN, all three). The longest bar is second from the bottom. The value axis ticks are rotated 45 degrees. "Mean resistance (%)": mean of what and with what n is unstated (statistician). Data scientist 1 did not test the `reorder` call on the page.
- **Suggestion (data scientist 1, user):** type `amr_class` as an ordered type in value order and redraw, or drop the ranking claim; if kept, say that the file order does not set the bar order. **(statistician):** a factor step or reorder; show n.
- **Tried / not tried:** nothing was tried.

### 3.18 step_chart
- **What the user sees:** three step lines. The Carbapenems (red) line shows only its vertical jumps.
- **What is wrong:** it is drawn first and the others lie on top (SEEN). I read the data: Carbapenems 2014 to 2016 (1.0) equals Cephalosporins; 2016 to 2019 (0.5) and 2021 to 2023 (0.25) equal Fluoroquinolones. So data scientist 2 (hidden under the green and blue lines) and the statistician (under Fluoroquinolones at 0.5 and 0.25) are each partly right. Six of the 15 rows repeat the previous value. The column `breakpoint_change` holds the breakpoint, not a change. The title says EUCAST, but EUCAST publishes breakpoints per drug and species, so one value per class is not an EUCAST value (data scientist 2, statistician: external knowledge, not looked up). The y axis is linear for doubling values, so 0.125 is not labelled.
- **Suggestion (data scientist 2, statistician):** mark the values as illustrative or use a referenced table; avoid hiding a line (offset, line type or facet); rename the column `breakpoint`; log2 y axis. **(user):** say "these numbers are made up for the example", if so.
- **Tried / not tried:** nothing was tried.

## 4. Examples judged MINOR or UNCLEAR only (16)

These examples have no WRONG or MISLEADING verdict from any viewpoint. The text corrections follow the viewpoints' own proposals.

| example | what to correct | who found it | Suggestion |
|---|---|---|---|
| bar_grouped | E. faecalis by Cephalosporins is 0.0 (READ by me), drawn as no bar; doubtful biology (external knowledge); tag Ranking; legend `drug_class`. | data scientist 1, statistician, user (the gap) | Replace the 0.0 or remove the row and say a missing combination is a gap; family Comparison; legend "Drug class". The user's sentence "a missing bar means no value in the data, not zero" would be false here, because the file holds 0.0. |
| bar_simple | Tag pattern (counts only); `value` unused; legend and axis labels; pasted sentences. | all three | Page: "one bar per species, height = number of records, split by drug class". Tag: section 5. |
| dumbbell | Continuous legend; `year_label` typed Int64 while the page says Categorical; species alphabetical; link text points to the lollipop page (not checked). | all three | Type the year as text or discrete colour; legend title "Year"; optionally sort species by change. |
| ecdf | Linear axis; no breakpoints drawn; "one step = one observation" false with ties; "read %S, %I, %R" needs breakpoints; n = 10 per curve. | all three | Log2 x axis; a vertical line at a breakpoint; correct the step sentence; tag sample size. |
| error_bar | "95% CI" is not in the data; the overlap sentence; "T3 summarize" unexplained; title says "Mean MIC", y says log2; colour repeats x. | all three | State the level, n and method in the page or the data; replace the overlap sentence with "do not read significance from overlap; compare the interval of the difference" (statistician); order species by mean. |
| histogram_simple | Stacking by class not said; 30 bins for 100 values (statistician: the Freedman-Diaconis rule gives 6 bins, Sturges 9); values not MIC. | data scientist 1, statistician, user | Say "bars stacked by class, 30 bins"; fewer bins or a note that bin choice changes the picture. |
| jitter_strip | "One percentage value per isolate" is unclear; "pairs well with boxplot_simple" but that example draws no points; colour repeats x. | statistician, user, data scientist 2 | Rename the quantity or say what it is; fix the reference; optionally add a median mark. |
| line_grouped | Two causal sentences; the lines are not parallel; no n; tag medium+. | all three | Rewrite as "what to look for" (diverging, crossing); add n or intervals; fix the tag. |
| line_simple | y axis starts at 38; n hidden; causal sentence; tag medium+. | all three | Say the axis does not start at zero; soften the sentence; optionally map `n_isolates`, or draw intervals from it. |
| proportion_bar | "Fraction of isolates" against records; pair data differ; "or 0-100%". | data scientist 2, statistician, user | Say "share of records"; add n per bar; use the same data in the pair; remove "or 0-100%". |
| qq_plot | "S-curves indicate skewness" is wrong (skew shows as a one-sided curve, heavy tails as an S); "tests normality" (it is a graphical check); n = 15 gives a weak check; log2 not labelled; "computed in T3" but the column is stored. | data scientist 2, statistician, user | "A graphical check of normality"; label "log2(MIC)"; compute `log_mic` in a step, or remove "T3". |
| ridgeline_advanced | Four panels, not a ridgeline; free y scale per panel; curves cut at the data range; pasted sentences. | all three | Call it a faceted density, or build real overlapping ridges (yours; the name is decided by D-0397 to D-0400); fix the scale or say so. |
| scatter_smooth | Page names LOESS but only a straight line is drawn; the band assumes independent points; 9 points per species. | all three | Say "linear fit; the band is the 95 percent interval of the mean line; assumes independent points"; do not call it a test of trend. |
| stacked_area | Tag pattern and `show: proportion`; shares hard to read in a stack of counts; counts follow sampling effort. | data scientist 2, statistician, user | Year pattern; show `trend` or `change`; one sentence that shares are hard to read (use `position_fill` or proportion_bar). |
| stacked_bar | Unit of a count; bars alphabetical while the page advises ordering. | data scientist 2, statistician, user | State the unit (records or isolates); optionally order species by total. |
| violin_simple | Random data look bimodal; no median, no points, no n; "A hybrid between boxplot and density" with no explanation. | all three | Add a median or the points; one line on how to read a violin and on noise at n about 25; MIC on doubling steps or another column name. |

## 5. THE TABLE OF ADVICES ON TAGS (D-0402, D-0403)

D-0403 says a tag mismatch is an advice, not an error: shown, the example stays. Here are the advices. The data scientists compared the tags with the recipe and the data. The cheatsheet rules used (READ, `assets/gallery_data/TAXONOMY_CHEATSHEET.md`): Simple = single geom, direct mapping, no wrangling; Intermediate = multiple geoms or position adjustments, may need pre-aggregation; Advanced = non-trivial wrangling, derived columns or specialised geoms. `any` = aggregated data; `individual points` = n under about 200 with visible dots; `medium+` = n about 50 or more; `large` = n about 500 or more.

### 5.1 Pattern

| example | tag | as written | found | evidence | what blocks a simple correction |
|---|---|---|---|---|---|
| bar_simple | pattern | 1 Numeric, 1 Categorical | 2 Categorical, counts only | READ: x species, fill amr_class, no y; `value` and `id` unused (data scientist 1, statistician) | No word exists for zero numeric columns |
| boxplot_simple | pattern | 1 Numeric, 1 Categorical | 1 Numeric, 2 Categorical | READ: x amr_class, fill species, y mic_value (data scientist 1) | none; the word exists |
| bubble | pattern | 2 Numeric, 1 Categorical | 3 Numeric, 1 Categorical | READ: x sample_size, y mean_resistance, size pct_resistant, colour species (data scientist 1) | No word for three numbers and a category |
| connected_scatter | pattern | 2 Numeric | 2 Numeric, 1 Categorical (plus year as the path order) | READ: colour and group drug_class; year is not mapped (data scientist 1) | none for the category; the row order is outside any word |
| density_simple | pattern | 1 Numeric | 1 Numeric, 1 Categorical | READ: x growth_index, fill species (data scientist 1) | none |
| dumbbell | pattern | 1 Numeric, 2 Categorical | 1 Numeric, 2 Categorical by intent; as typed 2 Numeric, 1 Categorical | READ: colour `year_label` is Int64, so the picture treats it as a number (data scientist 1) | The word depends on the type of `year_label`. A number used as a category has no rule |
| error_bar | pattern | 1 Numeric, 1 Categorical | 3 Numeric, 1 Categorical | READ: y mean_mic, ymin ci_low, ymax ci_high (data scientist 1; its summary calls the written tag "acceptable") | No word; unclear whether ymin and ymax count as numbers |
| heatmap_correlation | pattern | 3 Numeric (Matrix) | 2 Categorical, 1 Numeric | READ: x var1 and y var2 are String, fill correlation Float64 (data scientist 1) | The cheatsheet defines `3 Numeric (Matrix)` as "(e.g. var1, var2, value)", so it calls var1 and var2 numeric; the recipe types them as text |
| histogram_simple | pattern | 1 Numeric | 1 Numeric, 1 Categorical | READ: fill amr_class (data scientist 1) | none |
| point_faceted | pattern | 2 Numeric, 1 Categorical (Faceted) | one date, one number, two categories (species twice) | READ and RUN: `date` is text, dates in two Januaries (data scientist 2) | No word for a date with categories in panels; the answer depends on whether the date is typed Date |
| point_simple | pattern | 2 Numeric | one date (typed as text), one number, one category | READ and RUN (data scientist 2) | No word for date plus number plus category; typing the date as Date changes the answer |
| stacked_area | pattern | 1 Numeric, 2 Categorical | 1 Year, 1 Numeric, 1 Categorical | READ: x year, y count, fill species (data scientist 2, statistician) | none; the word exists |
| step_chart | pattern | 1 Numeric, 1 Categorical | 1 Year, 1 Numeric, 1 Categorical | READ: x year Int64 (data scientist 2) | none; the word exists |
| scatter_smooth | pattern | 2 Numeric, 1 Categorical | same structure as line_grouped, which is written `1 Year, 1 Numeric, 1 Categorical` | READ (data scientist 2: two examples use different words for the same structure) | The rule does not say when a year is a "Year" and when a number |

### 5.2 Sample size

| example | tag | as written | found | evidence | what blocks a simple correction |
|---|---|---|---|---|---|
| area_simple | sample size | medium+ | any | RUN: 7 summary rows (data scientist 1; statistician says "small") | none for the word; "small" is not an allowed word |
| bar_simple | sample size | any | medium+ (rows are isolates) | RUN: 100 rows, 2 to 13 per segment (data scientist 1) | Does the tag count the table or what a bar shows? |
| density_2d_bin | sample size | large | medium+ | RUN: 60 rows, 35 filled bins, 1 to 4 per bin (data scientist 1; statistician says "small") | none |
| ecdf | sample size | medium+ | any or individual points | RUN: 30 rows, 10 per curve (data scientist 1; statistician "small") | Two words fit; the rule says nothing about which |
| freqpoly | sample size | medium+ | any or individual points | RUN: 45 rows, 15 per curve (data scientist 1) | same |
| line_grouped | sample size | medium+ | any | RUN: 35 rows, 7 per line, summaries (data scientist 2; statistician: 7 points per line) | none |
| line_simple | sample size | medium+ | any | RUN: 7 summary rows (data scientist 2) | none |
| qq_plot | sample size | medium+ | individual points | RUN: 15 per species (data scientist 2) | none |
| stacked_area | sample size | medium+ | any | RUN: 27 summary rows (data scientist 2) | none |
| tile_simple | sample size | any | not `any`: raw rows, 2 to 13 per cell | RUN (data scientist 2) | `any` is defined as aggregated data, but this table is raw; the picture shows one raw row |
| violin_boxplot | sample size | medium+ | individual points | RUN: 10 per species (data scientist 2) | none |
| violin_simple | sample size | medium+ | individual points (its table); "lower edge of medium+" (its text) | RUN: 20 to 28 per class (data scientist 2). Data scientist 2 says both | its own two statements disagree |
| boxplot_faceted | sample size | medium+ | medium+ for the 100 rows; not for the boxes | RUN: boxes 2 to 11 (data scientist 1, statistician) | The rule does not say total, per group or per drawn element |
| boxplot_simple | sample size | medium+ | same; boxes 2 to 14 | RUN | same |
| violin_faceted | sample size | medium+ | same; violins 2 to 12 | RUN (data scientist 2, statistician) | same |
| point_faceted | sample size | individual points | fits for the whole (100 rows); panels of 2 to 11 are thin | RUN (data scientist 2) | same |
| density_simple, histogram_simple | sample size | medium+ | fits in total; borderline per group (20 to 29; 19 to 34) | RUN (data scientist 1) | same |
| bubble, connected_scatter | sample size | any | the statistician proposes "small" (5 and 8 points) | RUN (statistician) | "small" is not an allowed word |

### 5.3 Difficulty

| example | tag | as written | found | evidence | what blocks a simple correction |
|---|---|---|---|---|---|
| area_simple | difficulty | Simple | Intermediate | READ: 2 layers, `geom_area` and `geom_line` (data scientist 1) | none by the written rule |
| beeswarm_sina | difficulty | Intermediate | Simple by the rule; Advanced if "specialised geom" counts | READ: 1 layer, `geom_sina` (data scientist 1) | The rule contradicts itself here |
| density_2d_bin | difficulty | Intermediate | Simple | READ: 1 layer, direct mapping (data scientist 1) | none |
| ecdf | difficulty | Intermediate | Simple | READ: 1 `stat_ecdf` layer (data scientist 1) | Does a `stat_` layer count as a specialised geom? |
| error_bar | difficulty | Intermediate | Simple by the geometry; Intermediate only because the data are pre-aggregated | READ (data scientist 1) | "May need pre-aggregation" is not a rule |
| heatmap_correlation | difficulty | Advanced | Intermediate | READ: 2 layers and a fill scale, no derived column (data scientist 1) | none |
| line_simple | difficulty | Simple | Intermediate | READ: 2 layers (data scientist 2) | line_grouped has the same two layers and is written Intermediate |
| point_faceted | difficulty | Intermediate | Simple by the written rule | READ: 1 geom plus `facet_grid` (data scientist 2) | The rule does not say how a facet counts. Data scientist 1 counted a facet as Intermediate in boxplot_faceted |
| violin_faceted | difficulty | Intermediate | Simple by the written rule | READ: 1 geom plus `facet_wrap` (data scientist 2) | same; data scientist 1 accepted the same structure in boxplot_faceted |
| qq_plot | difficulty | Advanced | Intermediate, or Advanced if a "specialised geom" counts | READ: 2 layers; `log_mic` is a ready column, no step (data scientist 2) | yours to choose |
| ridgeline_advanced | difficulty | Advanced | Simple (or Intermediate for the facet) | READ: 1 `geom_density` plus a facet (data scientist 2) | same facet question |
| scatter_smooth | difficulty | Simple | Intermediate | READ: 2 layers (data scientist 2) | none by the written rule |
| step_chart | difficulty | Simple | Intermediate | READ: 2 layers (data scientist 2) | none |
| tile_simple | difficulty | Simple | Simple by layers; "no wrangling" is false, because an aggregation step is missing | READ (data scientist 2) | The rule says "no wrangling"; the example needs some and has none |

Counts (my count of the three tables, not the reports'): 14 pattern rows, 18 sample size rows (11 firm: area_simple, bar_simple, density_2d_bin, ecdf, freqpoly, line_grouped, line_simple, qq_plot, stacked_area, tile_simple, violin_boxplot; plus violin_simple, and 6 rows about cells or total against group), 14 difficulty rows. Data scientist 2's own count in its report is 5, 8 and 6 (it counts differently).

Where the tags matched and the picture still does not deliver: beeswarm_sina is tagged `individual points`, but 100 rows draw about 18 dots (data scientist 1). lollipop_advanced and tile_simple are tagged `any` and `Simple` and match the rule's words.

### 5.4 Family and what it shows (the author's judgement under D-0402; these are only proposals)

D-0402 keeps family, "what it shows" and the guidance text as the author's judgement, checked as reasoning only. The viewpoints propose:

| example | tag | as written | proposal | who |
|---|---|---|---|---|
| bar_grouped | family and show | Ranking, ranking | Comparison; the allowed `show` words have no "comparison" | data scientist 1 |
| bar_simple | family and show | Ranking, ranking | Part-to-Whole or Comparison; nothing is ranked | data scientist 1 |
| bar_horizontal | family and show | Ranking, ranking | stays true only if the bars are ordered by value | data scientist 1, statistician |
| lollipop_advanced | show | ranking | not what the picture shows | data scientist 2 |
| tile_simple | family and show | Correlation, relationship | Comparison | statistician, data scientist 2 |
| bubble | family | Correlation | wrong until a real predictor is on x | statistician |
| point_simple, point_faceted | family and show | Correlation, relationship | no relation is drawn | statistician; data scientist 2 |
| heatmap_correlation | family | Correlation | only after the matrix is real | statistician |
| connected_scatter | family | Correlation | acceptable (data scientist 1); nothing is correlated beyond time (statistician) | disagree |
| stacked_area | show | proportion | `trend` or `change`; the picture shows counts | data scientist 2, statistician |
| step_chart | show | trend | `change` | data scientist 2 |
| scatter_smooth | family | Correlation | could be Evolution; a naming choice | data scientist 2 |
| violin_faceted | family | Comparison | could be Distribution | data scientist 2 |

### 5.5 What the rules do not say today; you must read this before the rules are written in the spec

Each point is open. The options come from the reports. Where a report only names the gap, the options say "not given".

1. **Pattern words that do not exist.**
   - Count-only plot (no number mapped; bar_simple). Option (data scientist 1): add a word for two categories with no numeric column. Another reading (data scientist 2): a pre-made count (proportion_bar, stacked_bar) counts as the numeric column.
   - A date (point_simple, point_faceted): add a date word, or reuse the `1 Year` words for any time axis (data scientist 2: the Year pattern exists for stacked_area and step_chart).
   - A number used as a category (dumbbell: year as colour; Int64 typed): fix the type of the column, or add a rule. Reports give the type fix only (data scientist 1).
   - Three numbers and a category (bubble, error_bar): add a word, or say that ymin and ymax are not counted as numeric. Not given.
   - The matrix pattern: the cheatsheet calls var1 and var2 numeric; the recipe types them as text. Options not given.
   - Year as a number against `Year` (scatter_smooth against line_grouped): say which word applies (data scientist 2).
2. **Sample size.**
   - Per group, per drawn element, or for the whole table: not said (data scientists 1 and 2, statistician). The statistician proposes by group ("small" or "per cell").
   - The thresholds are written "about 50", "about 200", "about 500" and are not exact.
   - `any` means aggregated data; whether a raw table with few rows per cell counts (tile_simple) is not said.
   - The statistician uses the word "small", which is not allowed. Data scientists 1 and 2 map small tables to `any` or `individual points`.
3. **Difficulty.**
   - How a facet counts: data scientist 1 counted it as Intermediate, data scientist 2 did not. This is a difference between two viewpoints that use the same rule.
   - How a `stat_` layer, a default position (stack), a flipped axis, a scale, or the number of aesthetics count (bubble).
   - How a computed column already in the file counts (qq_plot `log_mic`).
   - What "specialised geom" means (sina, violin, qq): the rule contradicts itself for beeswarm_sina (data scientist 1).
   - Whether a missing step counts against "no wrangling" (tile_simple).
   - Data scientist 2: "she may want to say it before the tags are changed".
4. **The `show` words have no "comparison"** (data scientist 1). The words `Comparison` and `Ranking` are family words; `show` has `ranking` only.

## 6. For the demo

This is the viewpoints' reading. It is yours to change. "Fit" means: no viewpoint says the picture or page teaches something false.

**Fit as they are** (data scientist and statistician both list them, no WRONG verdict, only text notes):
- jitter_strip
- scatter_smooth (say "linear fit")
- stacked_bar (say what a count counts)
- proportion_bar (say what a count counts)

**Fit with a spoken caveat:**

| example | caveat | who |
|---|---|---|
| ecdf | the axis is linear | data scientist 1; statistician lists it fit |
| line_grouped | do not read the year-to-year jumps | data scientist 2, statistician |
| line_simple | the y axis does not start at zero; the rise is not significant | data scientist 2 |
| qq_plot | remove the S-curve sentence; say n = 15 | data scientist 2, statistician |
| ridgeline_advanced | call it a faceted density | data scientist 2 |
| step_chart | the values are illustrative; the Carbapenems line is hidden (the user says MISLEADING) | data scientist 2; statistician: ignore EUCAST |
| violin_simple | the bulges are noise | data scientist 2 |
| bar_grouped | the E. faecalis gap | data scientist 1, statistician |
| bar_horizontal | do not call it a ranking (the user says MISLEADING) | data scientist 1 |
| dumbbell | the legend | data scientist 1 |
| error_bar | the overlap sentence | data scientist 1 |
| histogram_simple | noise, and the stacking | data scientist 1 |
| stacked_area | the tags | data scientist 2 |
| bar_simple | bars count rows | data scientist 1 |

**Not fit** (WRONG from at least one technical viewpoint, or MISLEADING from the user, and no one gives a caveat that removes the false teaching):
- area_simple (data scientist 1: fit after a text fix)
- beeswarm_sina, bubble, density_2d_bin, density_simple, freqpoly, heatmap_correlation
- lollipop_advanced, point_faceted, point_simple, tile_simple, violin_boxplot, violin_faceted
- boxplot_faceted, boxplot_simple, connected_scatter (data scientist 1: with caution; statistician: not)

## 7. What a correction pass would have to do, in order

This is a proposal, not a plan you approved. D-0401 leaves the choice of one pass or two to the coordinator; D-0397 to D-0400 already fix names, headings, chart types and the picture key.

1. **Wait for your remaining Gallery answers first.** The tag rules and the new pattern words of section 5.5 are to be proposed to you and written in the spec before they are built (D-0402). The Q1 names, headings and Q2 chart-type words follow your decisions. Each example is then written once (D-0401).
2. **Text only, no new picture:** area_simple, bar_simple (page), error_bar, histogram_simple, jitter_strip, line_grouped, line_simple, proportion_bar, qq_plot, scatter_smooth, stacked_area, stacked_bar, and the pasted sentences of section 1 (10 pages, 3 pages and 13 header lists). Also the pages that talk about steps that do not exist. These can go first and need no data.
3. **Recipe change with a new picture, using the data as it is:** lollipop_advanced (the swap was tried on a copy), dumbbell (type the year), density_simple (alpha), connected_scatter (a sort step and year labels), density_2d_bin (bin width), step_chart (hidden line; log2 axis), point_simple and point_faceted (Date type tried on one copy; the data are still two Januaries). These pictures are shown to you before they replace the stored ones.
4. **Corrections that need new data.** If you want the Gallery to teach MIC properly, the data must then be realistic MIC values in doubling steps, as in ecdf, freqpoly, qq_plot, beeswarm_sina, violin_boxplot, and with a log2 axis or a log2 column.
   - The ten random-number tables (section 1, point 2).
   - Cells with at least 10 values (statistician, data scientist 1) for boxplot_faceted, boxplot_simple, violin_faceted.
   - A real, symmetric correlation matrix for heatmap_correlation, or a rename.
   - A real predictor and a percent column for bubble.
   - A plausible E. faecalis cephalosporin value in bar_grouped.
   - Real or marked illustrative values in step_chart.
   - A real spread of dates in point_simple and point_faceted.
   - A mean-per-cell step in tile_simple (a recipe change; the data stay).
5. **Tag edits** come last, after the rules of section 5.5 are written and you have read them. Each is an advice in the check report (D-0403). The advice table you read in section 5 would be regenerated after the corrections.
6. **Every changed picture is shown to you before it replaces the stored one.** All 34 current pictures are identical to a redraw (section 0), so a check after the pass can compare each new redraw with the picture you approved.

## 8. Not verified (the four lists merged)

- The running Gallery screen: nobody looked at it. Data scientist 1 and 2 saw the pictures drawn by the app's own function (identical to the stored ones). The statistician and the user saw only the stored pictures; the statistician did not look at 8 pictures (lollipop_advanced, area_simple, error_bar, jitter_strip, line_grouped, line_simple, stacked_bar, violin_simple). Thumbnails (`preview_thumb.png`) and the page layout around the picture were not looked at.
- EUCAST values in step_chart: not checked against EUCAST tables. The claim that EUCAST publishes breakpoints per drug and species is external knowledge (data scientist 2, statistician).
- The biology claim that E. faecalis is intrinsically resistant to cephalosporins (bar_grouped): the agents' own knowledge, not looked up (data scientist 1, statistician).
- The error-bar intervals (error_bar): whether they come from a real n and standard deviation cannot be checked from the file. The statistician checked only that they are symmetric.
- The overlap-of-intervals rule and other statistical sentences (95 percent CI, Q-Q plot reading, S-curves) are the knowledge of the agents, not repository facts. The statistician's answers came from a data scientist agent.
- Whether the `reorder` call named on the bar_horizontal page exists in the recipe format; whether a `summarize` step called T3 exists; whether a log2 axis or a log2 step exists in the format; whether a mean-per-cell step exists by name (the rules file lists registered actions, not tested here).
- The Date type: tried on one scratch copy (point_simple). No existing Gallery recipe uses it. Not tried for every recipe path of the app.
- The cause of the black line to 64 in violin_boxplot is reasoned from the layer setting `trim: false`, not isolated by a run.
- Box width differences in boxplot_simple were seen, not explained (data scientist 1).
- The effect of typing `year_label` as String in dumbbell: reasoned, not run (data scientist 1).
- What "count" counts in proportion_bar and stacked_bar, and the unit of growth_index and avg_growth: the files do not say.
- Bandwidth and plotnine defaults for density and violin (statistician): not read in the library source.
- The line_simple model (statistician) assumes k = round(p times n) and independent isolates.
- The external links of the pages (the R Graph Gallery link on dumbbell, the ADR-002 text) were not followed.
- Whether numbers in step_chart, bubble and heatmap_correlation are invented: not stated by the files (user).
- The user viewpoint ran nothing: row counts and whether recipes sort rows were not checked by it.
- Taxonomy words of other examples were not compared; family and `show` words are reasoning only.

### Contradictions between the reports (what I read, and which report is right)

| point | reports | what I read | right |
|---|---|---|---|
| User's count of verdicts | CLEAR 9, MISLEADING 10 | its table: 8 and 11 | the table (my count) |
| heatmap_correlation diagonal | user: -0.5, 0.0, -0.1, -0.9; data scientist 1 and statistician: -0.5, -0.8, -0.1, -0.9 | the file: B,B = -0.8 | data scientist 1 and statistician |
| point_faceted cells | user: 1 to 8 points; data scientist 2 and statistician: 2 to 11 | I counted 16 cells, 2 to 11 | data scientist 2 and statistician |
| proportion_bar totals | statistician: "261 to 3xx per species"; data scientist 2: 190 to 287 | file totals 190, 217, 237, 264, 287 | data scientist 2 |
| line_simple n | user: 56 to 114; data scientist 2: 56 to 116 | file: 56 to 116 | data scientist 2 |
| step_chart: which line hides Carbapenems | data scientist 2: under the green and blue; statistician: under Fluoroquinolones | the data fit both, partly | both partly (section 3.18) |
| how a facet counts for difficulty | data scientist 1: Intermediate fits (boxplot_faceted); data scientist 2: not counted (point_faceted, violin_faceted) | the rule is silent | unsettled; section 5.5 |
| violin_simple sample size | data scientist 2: table "does not fit", text "lower edge of medium+" | 20 to 28 per class | unsettled; it is the report's own |
| lollipop_advanced verdict | statistician: MINOR; data scientist 2 and user: dots at 0 | I did not open the picture; two viewpoints SAW the dots at 0 and data scientist 2 ran the fix | data scientist 2 and user |
| bar_grouped sentence | user suggests "a missing bar is not zero" | file holds 0.0 for E. faecalis by Cephalosporins | the user's suggested sentence would be false here |
