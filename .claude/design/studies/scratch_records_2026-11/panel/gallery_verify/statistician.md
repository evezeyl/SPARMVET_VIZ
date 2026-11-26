# Gallery verification, STATISTICIAN viewpoint (the project has no separate statistician agent; I answer the statistician's question: is this the right plot and the right computation for what the page and the name claim, with these data?)

Labels: RUN = executed (scripts in tmpAI/panel/gallery_verify/statistician_scratch/a.py, b.py, c.py), READ = file read, SEEN = preview_plot.png looked at, REASONED = my inference. Nothing in the repository was changed.
Common fact (RUN b.py, c.py): in the REC_nnn examples (tested on density_simple, histogram_simple, violin_simple, boxplot_simple; the others have the same id pattern and range, READ) the "MIC" or "growth" column is random numbers, near uniform on 0 to 127 (KS test against uniform p 0.20 to 0.82: density_simple, histogram_simple, violin_simple, boxplot_simple), not a MIC series (0.06 to 64 in 2-fold steps). Column species and amr_class are independent of the value. Every comparison between groups in these examples is a comparison of noise; the page must not invite a biological reading.

## Per example

### area_simple: WRONG
- READ page: "cumulative magnitude", "Growing filled area = accumulating resistance burden". The y is a yearly percentage (51.6 to 63.0, 7 points), not a cumulative quantity (RUN a.py). The area under a rate curve has no meaning. The fill adds nothing to geom_line and teaches a false reading.
- No n per year, no uncertainty; "trend" tag on 7 points.
- Suggestion: (a) use line_simple for a rate; (b) if the area must stay, change data to a true cumulative or a count (cases per year) and say so. (a) teaches: a rate is a line. (b) teaches: area is for additive totals. Tag sample_size "small".

### bar_grouped: MINOR
- 15 rates, no n, no interval (READ). E. faecalis x Cephalosporins = 0.0 (RUN a.py): enterococci are intrinsically resistant to cephalosporins (REASONED, external knowledge); a 0.0 resistance rate there is biologically false or means "not tested". A reviewer will see it.
- Page: "Useful for spotting highest" ok. Tag Ranking but the bars are alphabetical, not ranked.
- Suggestion: replace the 0.0 (use a real value or remove the cell); state n per bar; either order the species or change `show` to "comparison".

### bar_horizontal: MINOR
- SEEN: bars in alphabetical order (Aminoglycoside at the bottom), not ranked. The page says "ranking" and "pre-sort data by value": row order does not set the axis order for a text column in plotnine (SEEN: the data are sorted 31.9 to 62.9 and the picture is not). The page advice does not work.
- "Mean resistance (%)": mean of what, with what n and spread? Unstated.
- Suggestion: set the category order from the value (a factor step or reorder) and say it; or drop the word ranking. Show n.

### bar_simple: MINOR
- geom_bar counts rows per species, stacked by class (RUN a.py: counts 23 to 29 per species; cells 2 to 13). The column `value` is unused, so taxonomy pattern "1 Numeric, 1 Categorical" is wrong (it is 2 Categorical, counts). Count differences between species are sampling of a random file, not a finding. Page: "categorical distribution" is vague.
- Suggestion: pattern "2 Categorical"; say that the bars count rows, and that `value` is not drawn.

### beeswarm_sina: WRONG
- SEEN: the 20 to 30 points per species fall on 4 to 5 distinct values (RUN b.py: 4 to 5 unique values; E. faecalis is exactly 5 each of 1, 2, 4, 16, none of 8). Equal values are drawn on top of each other, so E. faecalis looks like 4 dots. Page: "Each dot is one observation. The spread width reflects density" is false here: the width does not open on ties.
- MIC on a linear axis; one 16 compresses the others. Values 0.12 and 0.062 are rounded (true 0.125, 0.0625), so log2 is off by 0.06 to 0.07.
- Suggestion: (a) log2 axis and a stack or count mark for discrete MIC (a dot-count plot, or geom_count); (b) keep sina but use truly continuous data (growth index). (a) teaches MIC is discrete and on a log scale; (b) teaches the sina for continuous values.

### boxplot_faceted: WRONG
- RUN b.py: 16 boxes, per-box n = 2 (S. aureus x Tetracycline), 3, 4, 5 ... 11. Box and whiskers of 2 to 5 points are not quartiles. Tag sample_size "medium+" is the total (100), not the box (SEEN: the picture shows boxes of 2 points as full boxes).
- Facets by species but the page text says nothing about n per box.
- Suggestion: show the points over the boxes (jitter) and n per box, or reduce to groups with n of about 10 or more (a bigger data file). Tag sample_size by box.

### boxplot_simple: WRONG
- x amr_class, fill species: plotnine dodges, so it draws 16 boxes, n 2 to 14 (RUN c.py: K. pneumoniae x Tetracycline 2, P. aeruginosa x Aminoglycoside 2). The page says "median, quartiles, and outliers for numeric distributions" and nothing of a 4 x 4 layout. The two outliers (SEEN) come from boxes of 5 to 9 points, and a 1.5 IQR rule on n of 5 is meaningless.
- Value is random uniform, called MIC on a linear axis.
- Suggestion: (a) one grouping (x = species, fill = same) with n of 20 to 35 each; (b) keep two factors but a data file with at least 10 per cell and the points drawn. Say what the box whiskers are (1.5 IQR).

### bubble: WRONG
- SEEN: legend "% Resistant" with 0.3, 0.4, 0.5, 0.6: a fraction labelled as percent (data 0.26 to 0.68, RUN a.py). Next to it y "Mean Resistance (%)" is 32.7 to 63.3: two different resistance quantities, 0.39 versus 46.7 for E. coli, unexplained.
- x = sample size (collection effort) against resistance: no biological question; page says "Position reveals correlation" on n = 5 points (r = -0.30, RUN, meaningless). Tag family Correlation is wrong.
- Suggestion: (a) x = a real predictor (for example year or consumption) and size = n; (b) fix the fraction (multiply by 100 or label "fraction"). Page: say correlation needs more than 5 points. sample_size "small".

### connected_scatter: WRONG
- READ page: "Use geom_path (not geom_line) to ensure correct temporal ordering." False: geom_path joins in ROW ORDER, not year order; it is correct here only because the file is sorted by year within the class (RUN a.py). A user whose rows are unsorted gets a tangle without warning. The correct statement: sort by year first.
- SEEN: no arrow, no year labels, no start mark (arrow: null), so the direction "moving right = increasing resistance" cannot be read from the picture; the 2020 backward loop is unexplained.
- "feedback loops", "Consumption-resistance" are causal words; two series that rise with time are correlated by time alone (r = 0.64 and 0.86 within class, 8 points, RUN: not independent points).
- Suggestion: sort step before the plot and say it; label first and last year or add an arrow; remove the causal wording. Tag sample_size "small".

### density_2d_bin: MINOR
- SEEN, RUN c.py: 60 rows, 35 occupied bins, maximum 4 per bin. Bins=15 on integer log2 values (bin width 0.53 and 0.60): alternate bins are empty (counts per column 2,5,0,7,0,10,0,...), a stripe artefact of the bin width against the integer lattice. Dark bins "many isolates" mean 1 to 4 isolates.
- Page: "Handles overplotting for large datasets" and tag sample_size "large" are wrong for n = 60. It is a 2D histogram (counts), not a density. r = 0.75, Spearman 0.72 are true, so "diagonal = cross-resistance" is supported, but cross-resistance needs the dilution lattice (bin width 1 per step).
- Suggestion: bins that equal the lattice (one per 2-fold step) or geom_count; tag "small"; rename the claim "joint counts".

### density_simple: WRONG
- SEEN: E. coli (red) is not visible at all: four filled densities with no transparency (geom_density params {}), later groups cover earlier. A reader sees three curves of four species.
- n 20 to 29 per group; uniform data gives broad bumps (K. pneumoniae second mode at 100) that are kernel noise (the bandwidth is the default of the layer; not stated on the page). Page: "smooth distribution" only.
- Suggestion: alpha of about 0.4 (as in ridgeline_advanced) or facets; say the bandwidth is the default rule and that curves of n of 20 show mostly noise.

### dumbbell: MINOR
- SEEN: year_label is Int64, so the colour is a continuous viridis scale with 2015, 2017, 2019, 2021, 2023, where only two values exist. Page says "Categorical".
- Two points per species, no n, no interval; 15 to 20 points change with no uncertainty. Order of species alphabetical. Title fixes the years.
- Suggestion: treat the year as text (a type change) or discrete colour; sort species by change; state n.

### ecdf: MINOR
- Computation right (stat_ecdf, steps 1/10, n = 10 per species, RUN). Page "read %S, %I, %R directly" needs breakpoints drawn; none are. MIC on linear axis: the whole curve is packed into 0 to 4 (SEEN). Page "The step represents one observation" is wrong for tied values (the step is k/n).
- Suggestion: log2 x axis; vertical lines at breakpoints; tag sample_size "small" (n = 10).

### error_bar: MINOR
- RUN a.py: all 8 intervals are symmetric (mean +/- 0.31 to 0.67), so they are mean +/- t*SE, plausible; n, SD, and the method are not in the data, so "95% CI" in the title cannot be checked from the example. Y label "Mean MIC (log2)"; title "Mean MIC" (it is a mean of log2 MIC).
- READ page: "Overlapping bars suggest groups may not differ significantly": overlap of two 95% CIs does not mean no difference (the CIs can overlap by about a quarter and the difference still be p < 0.05); this invites a wrong inference. "Longer bars = more uncertainty" is true only at equal n.
- Suggestion: state in the data n and how the interval was made; replace the overlap sentence ("do not read significance from overlap; compare the interval of the difference"). Order species by mean.

### freqpoly: WRONG
- RUN c.py, SEEN: binwidth 0.5 on RAW MIC (0.06 to 64): 130 bins, 6 to 7 non-empty per species, so the picture is isolated spikes returning to zero. The page says "0.5 for log2 MIC steps": that is true only if the x is log2 MIC, which it is not.
- n = 15 per species. Counts, not proportions, so equal n here only.
- Suggestion: (a) plot log2(MIC) with binwidth 1 (one bin per dilution step); (b) keep raw MIC and use a ECDF (ecdf example). (a) teaches discretisation of MIC; (b) teaches that a cumulative curve needs no bin choice.

### heatmap_correlation: WRONG
- RUN c.py: the diagonal is -0.5, -0.8, -0.1, -0.9 (a correlation of a variable with itself is 1); the matrix is not symmetric (MIC_A,MIC_B = -0.3, MIC_B,MIC_A = 0.85; max asymmetry 1.16); the symmetrised matrix has negative eigenvalues (-1.36), so it is not a correlation matrix of any data. The page says "Displays correlation intensity".
- SEEN: cell labels are tiny white text on a pale tile, unreadable; the colour scale runs -0.9 to 0.85, not fixed to -1..1.
- Suggestion: (a) build the matrix from real isolate-level columns with a correlation step (a tier 2 step) so the symmetric, unit diagonal result is true; (b) if the example only shows a colour map, rename it "heatmap of a value matrix" and use values with no correlation meaning. (a) teaches the computation; (b) removes the false claim. Fix scale limits and label colour in either case. State the method (Pearson or Spearman) and n.

### histogram_simple: MINOR
- 100 values, 30 bins of width 4.0 (RUN c.py: counts 0 to 9, FD rule gives 6 bins, Sturges 9); bar heights of 1 to 4 are noise (SEEN). Stack by amr_class: the stacked classes cannot be compared (only the lowest has a common baseline). Page: "Inventory view" only.
- Suggestion: fewer bins or the page says "bin choice changes the picture"; facets or transparent overlap for the classes.

### jitter_strip: MINOR
- Points per species 18 to 22 (RUN), values continuous, jitter fixed (random_state 0, reproducible): the right plot for this n. Kruskal-Wallis p = 1e-9 (RUN) shows real separation in the data.
- Page: "resistance_pct: one value per isolate". A resistance percentage is not a property of one isolate (an isolate is resistant or not); the meaning of the column is unclear.
- "n < 500 per group" is not a rule; with 20 points "dense clusters reveal the mode" is weak.
- Suggestion: rename the quantity (growth inhibition %, zone) or say what it is; add the group median mark.

### line_grouped: MINOR
- 5 species x 7 years, one mean per point, no n or interval (RUN a.py). Year-to-year jumps are up to 7.4 points for E. coli (42.0 to 34.6), larger than the 7-year drift for most series; sampling noise reads as signal.
- Page: "Species-specific jumps: may indicate clonal spread" and "system-wide pressure" are causal; a line chart cannot show them.
- Tag medium+ is wrong: 7 points per line.
- Suggestion: add n per point or intervals; remove or flag the interpretations as hypotheses.

### line_simple: MINOR
- Data have n_isolates (56 to 116, total 570): binomial standard error 4.6 to 6.6 points, 95% half-width 9 to 13 points (RUN c.py), larger than the 7.8 point rise. A binomial GLM of the year slope: slope 0.049 per year (log-odds), p = 0.22 (RUN c.py; k = round(p*n), independence assumed). So the "key surveillance signal" in the page is not significant in the example data.
- Page: "Flat or declining lines after an intervention suggest treatment policy effectiveness" is a causal claim from a line.
- Suggestion: either draw the interval from n_isolates (teaches uncertainty) or state that no test was done; remove the causal sentence. Tag sample_size small (7 points).

### lollipop_advanced: MINOR
- 4 species, avg_growth 56.0 to 86.2 (RUN a.py), no n or dispersion; a lollipop of a mean carries the same information as a bar. Not sorted (alphabetical, REASONED from the bar_horizontal picture), although tag is Ranking. Page header list omits `y_zero`, which the recipe uses.
- Suggestion: sort by value (and say it), show n, document y_zero.

### point_faceted: WRONG
- READ: date is a text column (String). Axis is categorical: 49 labels, only January 2024 and January 2025 exist (RUN c.py), so months between are not shown and spacing is not time. 16 panels with 2 to 11 points each (RUN). Colour repeats the facet row.
- No relationship exists (random); Spearman date vs value = -0.07, p = 0.49 (RUN, point_simple data).
- Suggestion: type date as Date (a continuous time axis); tag sample_size per panel.

### point_simple: WRONG
- SEEN: x labels are 48 overlapping date strings; text axis, so Jan 2024 and Jan 2025 are shown next to each other with no gap. Page: "Ideal for identifying correlations between two numeric variables or time series": x is not numeric here; the data show none (rho = -0.07, p = 0.49, RUN).
- Suggestion: same as point_faceted: Date type; say correlation requires a test and a stated method.

### proportion_bar: MINOR
- Computation right (position_fill, SEEN y 0 to 1). Page: "what fraction of each species's isolates are resistant to X?" is not what the data hold: these are counts of isolate-class records; an isolate resistant to two classes counts twice, so shares are shares of records, not of isolates (REASONED). Page: "Pair with stacked_bar": the two files hold different numbers (E. coli Tetracycline 48 here, 36 there, RUN), so the pair does not show the same data.
- Equal heights hide n (261 to 3xx per species; no n shown).
- Suggestion: state "share of records"; add n per bar; use the same data in the pair.

### qq_plot: MINOR
- RUN: log_mic = log2(mic_value) exactly (allclose True). Per species n = 15, 8 to 9 distinct values, so the points form steps (SEEN). Shapiro p = 0.64 and 0.54 with n = 15 cannot establish normality (low power).
- Page: "Tests normality" (it is a graphical check, not a test); "Essential for validating assumptions before parametric tests" (the assumption is on the residuals of the model, not on the raw values per group); the page says log2 "computed in T3" while the file already has the column and the recipe has no step; title says log, axis log2.
- Suggestion: "A graphical check of normality"; check residuals; show n; state log2; tag sample_size small.

### ridgeline_advanced: MINOR
- SEEN: four facets, no overlap: not a ridgeline, and facet_grid scales free_y rescales each panel, so a narrow high peak and a broad low one look alike; density integrates to 1, so heights are only comparable on a shared axis. n 45 to 56 per group is fine; E. coli Shapiro p = 0.048 (RUN).
- Page text is the generic boilerplate "Look for peaks (Ridgeline)..." and the Data Schema header list. (name decided in D-0397 to D-0400; the content makes the name wrong, flagged.)
- Suggestion: shared y or real ridges (overlap offset); state the bandwidth rule.

### scatter_smooth: MINOR
- RUN: lm per species n = 9 (2015 to 2023), R^2 0.98 to 0.996, slopes 1.93, 1.99, 1.26 per year, p of 1e-9 to 5e-7. The band is a confidence interval of the mean fit (se = true, plotnine level 0.95), the page says correct "95% CI of the linear fit". It is not a prediction band.
- Rates by year are a time series: autocorrelation makes the interval too narrow; no n per rate; "compare slopes across groups to see which is fastest" without a test of difference; page names LOESS, the recipe uses lm. Data are too clean for real surveillance.
- Suggestion: say "linear fit, band = CI of the mean line, assumes independent points"; do not call it a test of trend.

### stacked_area: MINOR
- 9 years x 3 species (RUN). tag show "proportion" but the picture shows absolute stacks (SEEN); composition shifts are hard to read in stacked areas. Isolate counts follow sampling effort, so "growing total" is not growing burden. Page "Growing total with stable proportions = uniform increase" ok. Pattern "1 Numeric, 2 Categorical" is wrong (year, count, species).
- Suggestion: show = "composition over time" is not what it draws; state counts are submissions; change tag.

### stacked_bar: MINOR
- Page: "Total bar height = overall isolate burden per species". The classes are not exclusive (an isolate can carry several classes), so the total is a sum of records, not isolates (REASONED). Stacked segments after the first have no common baseline (page admits). Data 2 to 78 per cell (RUN).
- Suggestion: state the unit (records), not isolates; sort species by total.

### step_chart: MINOR
- Right plot (geom_step, hv: SEEN the value holds until the next revision). Overplotting: carbapenems are hidden under fluoroquinolones at 0.5 and 0.25 (SEEN), so a series seems missing. Y axis linear for 2-fold values (0.125 to 1.0): equal doublings look unequal.
- Column is called `breakpoint_change` but holds the breakpoint value; rows 2016 (0.5 -> 0.5) and 2021 repeat the same value (RUN) so they are not changes. Title says EUCAST, but EUCAST breakpoints are per agent and species and have S and R values, not one per drug class (REASONED, external); if the numbers are invented the title is a false source claim.
- Suggestion: log2 y axis; offset or facet the lines; rename the column; drop "EUCAST" or give a real source.

### tile_simple: WRONG
- RUN c.py: 100 rows over 16 cells (n 2 to 13 per cell), geom_tile draws one tile per row on top of each other, so the colour seen is the LAST row drawn, not the mean. Last row versus cell mean: correlation 0.47, the largest gap 50.9 (E. coli x Aminoglycoside: mean 50.5, last 27.2). SEEN: no cell labels, the colour legend 0 to 125 reads as a value per cell.
- Page: "Interaction Matrix... relationships between two categories": there is none; taxonomy family Correlation / show relationship are wrong.
- Suggestion: (a) a summarise step (mean per cell) before the tile, with n in the cell; (b) keep tile as is but state the colour is one raw row (it is not a statistic). (a) teaches aggregation before drawing; (b) not recommended as a Gallery example. Change family to Comparison.

### violin_boxplot: WRONG
- SEEN, RUN b.py: n = 10 per species with 6 to 8 distinct values; trim = false extends every violin as a needle up to 64 (S. aureus max is 2); the S. aureus violin is a flat sliver at the bottom; boxes sit over a linear axis where 3 of 4 species fill 0 to 16. The density below 0 (impossible MIC) shows under the axis. Page: "Bimodal distributions appear as double-waisted violins": with n = 10 a kernel wave is not a mode.
- Suggestion: (a) log2 y axis, trim = true, points over the box; (b) use ecdf or sina for n of 10. State n per violin.

### violin_faceted: WRONG
- SEEN, RUN: 16 violins, per-violin n = 2 (K. pneumoniae x Fluoroquinolone: a flat rectangle), 3, 3, 3 ... 12. A density of 2 to 3 values is not a distribution. Violins end at the first and last value (trim default) and look like a real shape.
- Tag sample_size medium+ is the total.
- Suggestion: drop cells under n about 10 or enlarge data, show points and n; same remedy as boxplot_faceted.

### violin_simple: MINOR
- 4 violins with n 20 to 28 (RUN): enough for a rough shape. Uniform random data: the shape differences are noise (SEEN not needed). No points, no n; "mic_value" is not MIC.
- Page: "A hybrid between boxplot and density" with no explanation of bandwidth, trimming or area scaling.
- Suggestion: add points or median; state n; say the width is a kernel estimate.

## Summary table

| # | example | verdict | statistical problem |
|---|---|---|---|
| 1 | area_simple | WRONG | area of a rate read as cumulative burden |
| 2 | bar_grouped | MINOR | no n; 0.0 cephalosporin for E. faecalis is false biology |
| 3 | bar_horizontal | MINOR | not ranked (alphabetical); advice to pre-sort does not work |
| 4 | bar_simple | MINOR | counts of rows; tag says numeric; value unused |
| 5 | beeswarm_sina | WRONG | ties overprint, "each dot" false, MIC linear |
| 6 | boxplot_faceted | WRONG | boxes of n 2 to 5 |
| 7 | boxplot_simple | WRONG | 16 dodged boxes, n 2 to 14, unannounced |
| 8 | bubble | WRONG | fraction labelled percent; "correlation" on 5 points; x = n |
| 9 | connected_scatter | WRONG | geom_path "ensures ordering" false; no direction; causal words |
| 10 | density_2d_bin | MINOR | bins vs integer lattice give stripes; n = 60 not "large" |
| 11 | density_simple | WRONG | E. coli density hidden (no alpha) |
| 12 | dumbbell | MINOR | continuous colour for 2 years; no n |
| 13 | ecdf | MINOR | linear MIC; no breakpoints; n = 10 |
| 14 | error_bar | MINOR | CI not checkable; overlap sentence misleads |
| 15 | freqpoly | WRONG | binwidth 0.5 on raw MIC: spikes |
| 16 | heatmap_correlation | WRONG | not a correlation matrix (diagonal, asymmetry) |
| 17 | histogram_simple | MINOR | 30 bins for 100 values; stacked classes |
| 18 | jitter_strip | MINOR | "resistance % per isolate" undefined |
| 19 | line_grouped | MINOR | no n; noise vs trend; causal text; tag medium+ |
| 20 | line_simple | MINOR | rise p = 0.22 with n; causal text |
| 21 | lollipop_advanced | MINOR | unsorted; no n; y_zero undocumented |
| 22 | point_faceted | WRONG | date as text; 16 panels of 2 to 11 |
| 23 | point_simple | WRONG | date as text; "correlation" with none |
| 24 | proportion_bar | MINOR | shares of records, not isolates; pair data differ |
| 25 | qq_plot | MINOR | "tests normality" wording; n = 15 ties |
| 26 | ridgeline_advanced | MINOR | not a ridgeline; free_y |
| 27 | scatter_smooth | MINOR | n = 9 series, autocorrelation, no test |
| 28 | stacked_area | MINOR | tag proportion vs absolute; counts = effort |
| 29 | stacked_bar | MINOR | records vs isolates |
| 30 | step_chart | MINOR | overplot; linear on 2-fold; EUCAST claim |
| 31 | tile_simple | WRONG | last row drawn, not the mean; no relationship |
| 32 | violin_boxplot | WRONG | n = 10, needles, trim false, linear MIC |
| 33 | violin_faceted | WRONG | violins of 2 to 3 points |
| 34 | violin_simple | MINOR | no n; random data; unexplained kernel |

Totals: WRONG 14, MINOR 20, SOUND 0 (closest to sound: jitter_strip, scatter_smooth, qq_plot, line_grouped, ecdf).

## Taxonomy tags as a statistician would set them (to check, not decided)
- sample_size by group, not total: boxplot_faceted, boxplot_simple, violin_faceted, violin_boxplot (n = 10), ecdf (10), freqpoly (15), qq_plot (15), error_bar, line_simple, line_grouped, area_simple (7 points): "small" or "per cell", not "medium+".
- density_2d_bin: "large" false (n = 60).
- bubble, connected_scatter: small (5 and 8 points).
- family Correlation wrong for tile_simple, bubble (until a real predictor), point_simple and point_faceted (no relation drawn); heatmap_correlation only after the matrix is real.
- stacked_area show "proportion": picture is absolute counts.
- bar_simple pattern "1 Numeric" wrong (counts).

## Fit to show in a demo today (as is, with the claim true and no false teaching)
jitter_strip, scatter_smooth (say "linear fit"), qq_plot (with the wording caveat), ecdf, line_grouped (do not read the jumps), stacked_bar, proportion_bar, step_chart (ignore EUCAST), violin_simple, ridgeline_advanced. Not to be shown: all 14 WRONG.

## The five corrections ranked by harm to a real analysis
1. tile_simple: the colour is the last row drawn, not a statistic; a user copying it reports an arbitrary row as a result. Silent and plausible.
2. heatmap_correlation: a "correlation matrix" that is not one (diagonal not 1, asymmetric); the user learns the format with wrong values and no computation step.
3. boxplot_faceted / boxplot_simple / violin_faceted / violin_boxplot: quartiles and densities from 2 to 10 points drawn as full boxes and violins; hides n, the commonest misreading in AMR papers.
4. freqpoly and beeswarm_sina (and the raw-MIC linear axes): bin and axis choices that do not match 2-fold dilution data; spikes or hidden ties, wrong shape.
5. point_simple/point_faceted date as text, and connected_scatter geom_path "ensures order": time order silently wrong or absent when the user's file is not sorted or typed.
Next: density_simple (hidden group), bubble (fraction as percent), area_simple (area of a rate), error_bar overlap sentence, line_simple (trend p = 0.22 read as signal).

## Not verified
- The Gallery render path (render_example) was not run; pictures are the stored previews (SEEN), not redrawn, so I do not know that the stored picture equals the current render (the data scientists check that).
- Real EUCAST breakpoints and the intrinsic resistance of E. faecalis are external knowledge, not looked up.
- Whether the error_bar intervals come from a real n and SD: not checkable from the file.
- Bandwidth and exact plotnine defaults for density and violin were not read in the library source.
- The line_simple GLM assumes k = round(p*n) and independent isolates.
- lollipop_advanced, area_simple, error_bar, jitter_strip, line_grouped, line_simple, stacked_bar, violin_simple pictures were not looked at; their judgement is from recipe, page and data.
