# Gallery verification, data scientist, part 2 (17 examples, jitter_strip to violin_simple)

Labels: RUN = executed; READ = file read; SEEN = I looked at the PNG; REASONED = inference.
Scratch: tmpAI/panel/gallery_verify/data_scientist_2_scratch/ (prof.py profiles data, render.py draws by render_example, cmp.py compares, PNGs of all 17, `ex/` and `*_try.png` = two trial recipes on copies). Nothing in assets/ was changed.

## Common results (RUN)
- All 17 examples draw by `render_example`, and all 17 are pixel-identical (0.000 percent differ, 960x600) to the stored preview_plot.png. So the pictures are current; what is below is about what they teach.
- No missing values, no duplicate keys (id or species-year or species-class), no whitespace/case variants of group names in any of the 17 data files. Declared types equal the types polars reads. No recipe has steps (`tier1: {steps: []}`): the plot shows the raw table; "Transformation Logic (Tier 2)" text in the guidance pages talks about steps that do not exist in the recipe.
- Pasted boilerplate in the guidance pages (READ): "Visualize categorical patterns and distributions within your scientific datasets." in point_simple, point_faceted, tile_simple, violin_faceted, violin_simple; "Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap)" in lollipop_advanced and ridgeline_advanced; "This example utilizes advanced layer stacking and coordinate manipulation" in ridgeline_advanced (no coordinate layer) and lollipop_advanced (it has coord_flip, so there it is true).
- Recurrent issue: the colour legend titles that come from the column name in lower case (species, drug_class, amr_class, growth_index) while other examples set labs.

## 1. jitter_strip  -- SOUND
1 Data (RUN): 100 rows, id/species/resistance_pct = String/String/Float64; 18-22 isolates per species (5 species); ids unique; resistance 7.3-87.9 (plausible for a percentage).
2 Recipe (READ): all columns exist, types fit; random_state 0 so the jitter is reproducible (picture identical on re-render).
3 Plot (SEEN): five columns of points, y 0-90, points spread within +-0.2 of the category, alpha 0.6; colour = species duplicates the x axis, legend is redundant but harmless; no summary line, which is the stated purpose.
4 Tags: Comparison / 1 Numeric, 1 Categorical / Simple / geom_jitter / distribution / individual points: all fit (20 per group).
5 Guidance: facts fit. "see boxplot_simple" exists. "Dense clusters reveal the mode" with 20 points per group is optimistic but not false.
Suggestion (optional): none needed. If wanted, drop `color` or say in the text that colour repeats the x axis.

## 2. line_grouped  -- MINOR
1 Data: 35 rows = 5 species x 7 years (2018-2024), complete grid, no duplicates, mean_resistance 28.4-68.3 (%). Year is Int64 and mapped as a number, not as a category: correct.
2 Recipe: geom_line joins points in x order (plotnine sorts by x within a group); the file is year-major so row order does not matter here. Fine.
3 Plot (SEEN): five coloured lines with points, x ticks every two years (2018, 2020 ... 2024) while there is a point every year (grid lines at odd years are faint), y from about 26 to 70 (not zero). K. pneumoniae and S. aureus cross at 2019 (50.3 vs 50.6, RUN) and the points overlap there.
4 Tags: Evolution / 1 Year, 1 Numeric, 1 Categorical / Intermediate / geom_line / trend / medium+. Pattern and family fit. `sample_size: medium+` does not fit: the table has 35 summary values, 7 per line, and says nothing about how many isolates stand behind each mean.
5 Guidance: "Parallel rising lines: system-wide pressure (e.g. broad antibiotic use)" and "may indicate clonal spread" are causal readings that nothing in the data supports; the lines are not parallel in the picture (K. pneumoniae, P. aeruginosa and E. coli move differently). "Requires one row per (year, species): pivot or group-aggregate" is correct and does not exist in the recipe. `mean_resistance` has no n and no interval: nothing tells the reader how stable a mean is.
Suggestions: (a) tag sample_size to what is true (the plotted points are 35 summaries) or add an n column and say so; (b) rewrite the two causal sentences as "what to look for" (diverging, converging, crossing); (c) the picture does not need to change.

## 3. line_simple  -- MINOR
1 Data: 7 rows (2018-2024), mean_resistance 37.7-45.5, n_isolates 56-116 (Int64, not mapped). No duplicates.
2 Recipe: fits. The data are a yearly mean; they are not the mean of line_grouped (for 2018 the species means give 46.2, the line here 37.7, RUN), so the two examples do not describe one dataset (not a fault if never shown together).
3 Plot (SEEN): black line with 7 dots, title "AMR Trend Over Time", y axis starts at 38 (not zero) so the rise 37.7 to 45.5 fills the plot height; the 2021 peak and 2022 dip look large. n_isolates varies by a factor of two (56 in 2021 and 2022, 116 in 2024) but is not shown, so a reader cannot judge the 2021 peak, which rests on the smallest year.
4 Tags: Evolution / 1 Year, 1 Numeric / Simple / geom_line / trend / medium+. All fit except sample_size: 7 points are not "medium+" (REASONED; same remark as for line_grouped).
5 Guidance: "A rising slope indicates increasing resistance" is a reading, fine for a pooled mean. "Flat or declining lines after an intervention suggest treatment policy effectiveness" is a causal claim the plot cannot support. "n_isolates ... (for reference, not mapped)" is true and is the very number the plot hides.
Suggestions: (a) say in the text that the y axis does not start at zero and that years with few isolates carry less weight; (b) drop or soften the intervention sentence; (c) consider mapping n_isolates (point size) so the picture carries it (a picture change, she decides).

## 4. lollipop_advanced  -- WRONG
1 Data: 4 rows (E. coli, K. pneumoniae, S. aureus, P. aeruginosa), avg_growth 56.0-86.2, y_zero = 0 for all (a helper column that holds a constant). Unique species. "avg_growth" is called "average" but no n or spread; E. faecalis (in other examples) absent: harmless.
2 Recipe (READ): mapping y = y_zero, yend = avg_growth, then geom_point uses the global mapping, so the point is drawn at y_zero.
3 Plot (SEEN): F1 CONFIRMED. All four dark-red dots sit at 0; the grey sticks run from the dots to the value with nothing at the end. The emphasised mark (the dot) carries the value 0 for every species. x axis (after coord_flip) is labelled `y_zero`, a helper column name, and the 4 category rows are in alphabetical order, not by value; the numeric tick labels are rotated 45 degrees. The reader gets the right lengths from the sticks but the picture is not a lollipop chart.
   RUN of a fix on a copy (`ex/lollipop_advanced`, picture `lollipop_advanced_try.png`): mapping {x: species, y: avg_growth, xend: species, yend: y_zero} puts the dots at 63.0, 64.7, 86.2 and 56.0 with sticks to 0; axis then reads `avg_growth`. It renders with no other change.
4 Tags: Ranking / 1 Numeric, 1 Categorical / Intermediate / geom_segment / ranking / any. `ranking` is not what the picture shows: the species are not sorted by value, so no rank is read off. Difficulty Intermediate is high for one table with one geom and a flip (REASONED).
5 Guidance: title "Lollipop Chart" vs example name "Lollipop Advanced". "Assumes data is already summarized (Tier 2)": no Tier 2 exists. "Headers: id, species, avg_growth" omits y_zero. The Interpretations line is pasted (Ridgeline/Heatmap). Does not say the y_zero column must be 0 or why it is there.
Suggestions: (a) recipe: swap y and yend as in the trial (dot at the value); (b) set the species as Enum ordered by avg_growth (or say the example is unsorted) so "ranking" is true; (c) label the axis with labs (y: "Average growth"); (d) rewrite the Interpretations and Data Schema text. New picture: yes.

## 5. point_faceted  -- WRONG
1 Data: 100 rows, `date` is String, values 2024-01-01 to 2025-01-28; ALL dates are in January 2024 (48 rows) or January 2025 (52 rows) (RUN). 49 distinct dates. growth_index 0.57-127.9 (22 values above 100 for an "index" of unknown scale). The 16 species x amr_class cells hold 2 to 11 points each (RUN).
2 Recipe: `date` declared String and mapped to x, so plotnine draws a discrete axis with one slot per distinct date, in alphabetical (= date) order. facet_grid(cols amr_class, rows species) plus colour = species (redundant with the row facet).
3 Plot (SEEN): the x axis labels of the four columns are printed over each other and are unreadable (a black smear of dozens of rotated labels). Dates are equally spaced on the axis whatever the gap, so the 11 months between the two January blocks do not exist in the picture. Points in cells of 2-11 give no pattern. The strip text "K. pneumoniae" is cut in the right strips.
4 Tags: Comparison / "2 Numeric, 1 Categorical (Faceted)" / Intermediate / geom_point / relationship / individual points. The pattern is wrong: the two facet variables are two categoricals and `date` is a time axis (not a numeric pair). `relationship` is not read from this picture: growth_index against date, correlation about 0.04 (RUN).
5 Guidance: "High-dimensional comparison using a grid. The 'Multi-Course' view." is a slogan; the Interpretations line is pasted boilerplate; no text says the plot is date by growth_index, nor the date issue.
Suggestions: (a) recipe: `date: {type: Date}` (type exists in recipe_spec; RUN on point_simple copy works, see below), remove the x-axis label clutter with a date format or fewer breaks; (b) data: spread the dates over a real range, or say they are two sampling windows; (c) drop colour or the species row facet; (d) fix pattern and tags; (e) text. New picture: yes.

## 6. point_simple  -- WRONG
1 Data: as point_faceted (100 rows; date String; 50 in January 2024, 50 in January 2025; 48 distinct dates, ids unique; species 21-32 rows; growth_index 0.65-125.1, 20 values above 100).
2 Recipe: `date` String mapped to x. Declared type is the cause.
3 Plot (SEEN): x axis has 48 rotated overlapping labels; the first and last day of each January are neighbours on the axis, so the one-year gap is invisible; the reader sees a continuous series. RUN of a copy with `date: {type: Date}` (`point_simple_try.png`): two clouds, January 2024 and January 2025, with an empty gap; the labels read 2024-01-01 ... 2025-01-01. So the example teaches "time series" while the data are two month-long snapshots; correlation of growth_index with date is -0.13 (RUN), no visible trend.
4 Tags: Correlation / 2 Numeric / Simple / geom_point / relationship / individual points. Pattern `2 Numeric` is false as drawn (x is text) and, even typed Date, x is time: the right pattern is closer to "1 Year ... " than "2 Numeric"; `Correlation` over the date axis is a stretch.
5 Guidance: "Ideal for identifying correlations between two numeric variables or time series": true in general, but this example has no second numeric variable and no time series of any length. Interpretations pasted.
Suggestions: (a) `date: {type: Date}`; (b) choose data with a numeric x (or a spread of dates); (c) fix tags and text. New picture: yes.

## 7. proportion_bar  -- MINOR
1 Data: 25 rows = 5 species x 5 AMR classes, complete, no duplicates; totals per species 190-287 (RUN); counts Int64 16-80.
2 Recipe: geom_col + position_fill: heights computed by plotnine. Check (RUN): E. coli Tetracycline 48/287 = 0.167 and the picture shows the bottom E. coli segment ending at 0.167. Correct.
3 Plot (SEEN): five bars filled to 1.0, five AMR class colours, axis "Proportion" 0-1, classes alphabetical (Aminoglycoside on top), legend title "AMR Class". The picture is right and legible.
4 Tags: Part-to-Whole / 1 Numeric, 2 Categorical / Intermediate / geom_col / proportion / any. Fit. Intermediate is high for the same recipe as stacked_bar plus one layer (REASONED).
5 Guidance: "what fraction of each species's isolates are resistant to X?": the data are "count" per (species, class); if one isolate can be resistant to several classes, the share is the share of resistance records, not the fraction of isolates (the data file does not say what a count counts). "Same data structure as stacked_bar": true for the structure; the numbers differ (E. coli total 287 here, 254 in stacked_bar, RUN). "y-axis shows 0-1 (or 0-100%)" is right for this one (0-1).
Suggestions: say what a count counts (isolates or resistance records) in the data schema; remove "or 0-100%". Picture unchanged.

## 8. qq_plot  -- MINOR
1 Data: 30 rows, 2 species (E. coli, K. pneumoniae) x 15; mic_value is a 2-fold dilution series (0.125 ... 128), log_mic = log2(mic_value) exactly (max deviation 0.0, RUN); log_mic takes integer values with ties (2 per level, uniform). Shapiro-Wilk p 0.64 and 0.54 (RUN, scipy).
2 Recipe: mapping sample = log_mic, colour = species; geom_qq plus geom_qq_line, both by species. mic_value is declared but not used.
3 Plot (SEEN): two sets of 15 points with a line each; points in a staircase (ties), follow the lines closely: this is a clean example of "approximately normal". Title says log(MIC) (it is log2), y axis says "Sample Quantiles" without saying log2, legend title lower case "species". The lines are drawn per species through quartiles (plotnine default), so each species is judged against its own line, which is the correct use.
4 Tags: Distribution / 1 Numeric, 1 Categorical / Advanced / geom_qq / normality / medium+. `medium+` is wrong: 15 per group. Everything else fits.
5 Guidance (statistics): "S-curves indicate skewness. Points diverging at both ends indicate heavy tails." Wrong: skewness shows as a one-sided curve (banana), heavy tails as an S-shape. "Tests normality": a Q-Q plot judges normality by eye, it is not a test. "Essential for validating statistical assumptions before parametric tests": the assumption is on the residuals or the group, and 15 points give a weak check. "log_mic computed in T3": log_mic is a stored column and there is no step. "mic_value | Numeric" and "species | Categorical" differ from declared Float64 / String. The statement "log-transformation is typically applied to MIC data" is right and is the lesson.
Suggestions: correct the S-curve sentence; say "assess normality" not "test"; label the axis "log2(MIC)"; set sample_size to what is true; either compute log_mic as a step in the recipe (the better teaching of "computed") or remove "T3". Picture: new only if the axis label changes.

## 9. ridgeline_advanced  -- MINOR
1 Data: 200 rows, ids unique, species E. coli 56, K. pneumoniae 54, P. aeruginosa 45, S. aureus 45 (RUN); growth_index 8.6-91.9; no missing.
2 Recipe: geom_density + facet_grid(rows species, scales free_y), fill = species.
3 Plot (SEEN): F2 CONFIRMED and made precise: four stacked panels, one density each, no overlap, no vertical offset: it is a faceted density, not a ridgeline. The y axis is free per panel (tick sets 0-0.02 differ per panel: three labels in one, seven in another), so equal heights do not mean equal densities across panels. All curves are cut at the global data range (8.6 to 91.9): K. pneumoniae, P. aeruginosa and S. aureus have non-zero density at the right edge (about 0.002), the curve is cut. E. coli shows a shoulder (bimodal look) from 56 points: sampling noise. x axis title `growth_index`, legend duplicates the panel strips.
4 Tags: Distribution / 1 Numeric, 1 Categorical / Advanced / geom_density / distribution / medium+. Fit except Advanced (one geom plus facets; REASONED) and the example name "Ridgeline Advanced" promises a ridgeline.
5 Guidance: "Excellent for comparing distributions side-by-side using vertical faceting": true for the picture (faceting). "Requires 'Long Format' ... Headers: id, growth_index, species": order differs from the file (id, species, growth_index). "advanced layer stacking and coordinate manipulation" does not fit (no coordinate layer). Interpretations pasted.
Suggestions: rename or describe as "faceted density" (or build an overlapping ridgeline; decision for her); keep `scales` fixed so heights compare (a decision shown in the text); note that curves are cut at the data range; fix the pasted lines. New picture: only if the scale or the type changes.

## 10. scatter_smooth  -- SOUND (with notes)
1 Data: 27 rows = 3 species x 9 years (2015-2023), complete, no duplicates, rates 8.5-31.5; per-species fit slopes (RUN): E. coli +1.93 per year, K. pneumoniae +1.99, S. aureus +1.26; r about 0.99 for all (synthetic, almost exactly linear).
2 Recipe: year Int64 mapped as a number; geom_point plus geom_smooth(method lm, se true): fits per species. Correct.
3 Plot (SEEN): three coloured point clouds with a fitted line and a grey 95 percent band, band narrow, K. pneumoniae line steepest (matches the slopes), title "Resistance Rate Trend with Linear Fit", legend title lower case.
4 Tags: Correlation / 2 Numeric, 1 Categorical / Simple / geom_point / relationship / individual points. Fit (a trend over time could also be Evolution; a naming choice, not a fault).
5 Guidance: "Adds a linear model (or LOESS)": the example uses only lm. "95% CI of the linear fit": correct for plotnine's default (confidence band of the mean line). "Compare slopes across groups to see which species shows fastest trend change": right here (K. pneumoniae), but the band ignores that years of one series are not independent, and nine points per species is a small base: one sentence of caution would help a new user. Does not say the lines are not tested against each other.
Suggestions: text only: say lm is used (LOESS is an option), say the band is the 95 percent interval of the mean line for 9 points per species. Picture unchanged.

## 11. stacked_area  -- MINOR
1 Data: 27 rows = 3 species x 9 years, complete; counts 78-251; yearly totals 315, 345, 361, 398, 431, 422, 467, 504, 538 (RUN).
2 Recipe: geom_area position stack, year numeric. Right.
3 Plot (SEEN): three bands, top edge = total; matches the totals computed above (538 in 2023). E. coli on top, S. aureus at the bottom (legend order = top to bottom). Y axis labelled "Total Isolate Count" with ticks 0, 200, 400. Bands bounded by straight lines between years: interpolation. The reader sees growth in total and composition drift but cannot read a band's value except the bottom one.
4 Tags: Evolution / "1 Numeric, 2 Categorical" / Intermediate / geom_area / proportion / medium+. Pattern wrong: x is a Year, the right word is "1 Year, 1 Numeric, 1 Categorical" (the vocabulary has it). `proportion` is not what a count stack shows (a 100 percent stack would); `change` or `trend` fits the picture (REASONED).
5 Guidance: facts fit: "The top shows the total; each band height is the group's contribution." "Growing total with stable proportions" is something a stacked count area hides; the reader cannot judge shares by eye. "count | Numeric": declared Int64.
Suggestions: pattern to the Year pattern; show to trend or change; one sentence that shares are hard to read in a stacked area (use position fill or proportion_bar). Picture unchanged.

## 12. stacked_bar  -- SOUND (with notes)
1 Data: 25 rows = 5 species x 5 classes, complete; totals per species 254, 232, 214, 282, 212 (RUN).
2 Recipe: geom_col with position_stack (the same result as the default; the layer is accepted).
3 Plot (SEEN): bar heights match the sums (E. coli 254, P. aeruginosa 282). Order alphabetical; legend "AMR Class"; y "Isolate Count". Colours, legend and axes readable.
4 Tags: Part-to-Whole / 1 Numeric, 2 Categorical / Intermediate / geom_col / proportion / any. Fit; as for proportion_bar, Intermediate is high.
5 Guidance: "Total bar height = overall isolate burden": true only if each isolate is counted in one class (the data does not say what a count counts). "Ordering species by total count (reorder) makes the chart easier to read": advice, not applied in this picture (bars are alphabetical). "Use group-count from isolate data": no step exists in the recipe.
Suggestions: add the line on what a count is (isolates vs resistance calls); optionally order species by total (Enum) so the picture shows the advice. Picture unchanged unless ordered.

## 13. step_chart  -- MINOR
1 Data: 15 rows = 3 drug classes x 5 years (2014, 2016, 2019, 2021, 2023), breakpoint values 0.125-1.0. Column named `breakpoint_change` holds the breakpoint VALUE, not a change (the meta says "Breakpoint value at that time"). Several rows repeat the previous value (e.g. Carbapenems 2016 and 2019 both 0.5), so a dot is drawn where nothing changed.
2 Recipe: geom_step default direction "hv": horizontal first, then the vertical jump at the next row's year. So a jump appears at the year of the new value: right for "value in force from this year" (check: Cephalosporins drops to 0.5 at 2019, the row says 2019 = 0.5). Year numeric: fine.
3 Plot (SEEN): three step lines and dots. Carbapenems (red) is drawn first and the other two lie on top of it: the red horizontal parts from 2014 to 2016 (under green at 1.0) and the red at 0.5 from 2016 to 2019 (under blue) and the red 0.25 (under blue) are hidden; you see only red verticals at 2016 and 2021. A reader cannot recover the carbapenem history from the picture. y axis is linear (0.25, 0.50, 0.75, 1.00) for values that are 2-fold steps, so 0.125 is not labelled; a log2 scale is the usual one for MIC breakpoints.
4 Tags: Evolution / "1 Numeric, 1 Categorical" / Simple / geom_step / trend / any. Pattern should be the Year pattern; `change` is a closer word than `trend`.
5 Guidance: title "EUCAST Breakpoint Changes Over Time" and y "MIC Breakpoint (mg/L)" present the values as EUCAST data per drug CLASS; EUCAST publishes breakpoints per drug and organism, so a single value per class is not an EUCAST value (EXTERNAL knowledge, not checked against EUCAST tables, say so). No sentence says the values are illustrative. "Downward steps = tightened breakpoints": right. "Use geom_step not geom_line": right.
Suggestions: (a) mark the data as illustrative, or use a real, referenced table; (b) avoid hiding series (offset, linetype or facet; she decides); (c) rename column to `breakpoint`; (d) y on a log2 scale; (e) tags. New picture: yes (b, d).

## 14. tile_simple  -- WRONG
1 Data: 100 rows, 4 species x 4 AMR classes = 16 cells, all 16 occupied, with 2 to 13 rows per cell (RUN): E. coli x Aminoglycoside 13, P. aeruginosa x Beta-lactam 2. growth_index 0.68-127.6 (a "growth index" above 100 occurs for 22 rows).
2 Recipe (READ): mapping fill = growth_index, x = species, y = amr_class, one layer geom_tile, no steps, no aggregation.
3 Plot (SEEN and RUN): F3 CONFIRMED and tested. Many tile rectangles are drawn on the same cell; the last drawn covers the others. I read the pixel colour at the centre of each of the 16 cells, inverted the viridis scale (range 0.68-127.6) and compared with the first, last, mean, median, min, max of the rows of that cell: in 16 of 16 cells the colour equals the LAST row of the cell in file order (within 2 index units); the mean matched 0 cells, the median 1. Examples: E. coli x Tetracycline shows 31.0 (last row 31.2; the cell mean is 56.4 and median 46.0); K. pneumoniae x Aminoglycoside shows 85.0 (last 85.5; mean 42.2). The picture therefore depends on row order: shuffle the file and the picture changes (REASONED from the result; the cell colour is the last record by file order). Nothing in the figure or text says so. A heatmap of "growth index by species and class" is read as a mean; it is one arbitrary record.
4 Tags: Correlation / 1 Numeric, 2 Categorical / Simple / geom_tile / relationship / any. `relationship` and `Correlation` do not fit a heatmap of a summary per category pair (nothing is correlated); the data hold 100 isolates, `sample_size: any` hides that the cells hold 2-13.
5 Guidance: "Visualizes relationships between two categories using color intensity": the colour is one record, not a relationship; "Interaction Matrix" is a slogan; no mention of aggregation; Interpretations pasted.
Suggestions: (a) recipe: add an explicit step that makes one row per cell with the mean (or median) and n, then map fill to it (a step the user can see and audit); until then do not show it. (b) legend title "Mean growth index"; (c) say n per cell (the 2-row cells are weak); (d) tags: Comparison or a part of the Matrix pattern (the vocabulary has "3 Numeric (Matrix)"; decision for her). New picture: yes.

## 15. violin_boxplot  -- WRONG
1 Data: 40 rows, 4 species x 10 (E. coli, E. faecalis, K. pneumoniae, S. aureus); mic_value takes only the dilution values 0.062, 0.125 ... 64 (11 distinct values, RUN). 0.062 is a rounded 0.0625 (ratio to 0.125 is 2.016, not 2). So MIC is an ordered, discrete, log-scale measurement; the guidance calls it "Numeric (continuous)".
2 Recipe: geom_violin(trim false) + geom_boxplot(width 0.1); fill = species. Linear y axis.
3 Plot (SEEN): everything is squeezed into 0-10 on a 0-64 axis: S. aureus and E. coli are flat shapes at the bottom; the violins of E. faecalis and K. pneumoniae are thin needles; a black vertical line runs from 0 to 64 above every species, including S. aureus whose largest value is 2.0 (RUN): the reader takes it for data up to 64 (it is the zero-density tail of the violin with trim false, REASONED). Boxes are drawn but the violins are almost invisible. The outlier dots at 64 are flagged by the boxplot for two species (one value of 10). Legend shows box icons for species, redundant.
4 Tags: Distribution / 1 Numeric, 1 Categorical / Intermediate / geom_violin / distribution / medium+. `medium+` is wrong: 10 per group; a density estimate from 10 values is not stable.
5 Guidance: "The violin width represents data density": true; "Bimodal distributions appear as double-waisted violins": with 10 points and discrete data, small waists are noise. "MIC or measurement value | Numeric (continuous)": wrong for MIC. "whiskers (1.5xIQR)": the whisker is to the last point within 1.5 IQR, a small precision point.
Suggestions: (a) recipe: y on a log2 scale (scale_y_continuous trans log2, or a log2 column made by a step) so the dilution steps are equal; (b) trim true so the needle disappears (or say what it is); (c) larger n per group or a lower sample_size tag; (d) text: MIC is discrete and ordinal. New picture: yes.

## 16. violin_faceted  -- WRONG
1 Data: 100 rows, species 22-27 per species, amr_class 21-30 per class; per cell (species x class) only 2 to 12 rows (RUN): K. pneumoniae x Fluoroquinolone 2, P. aeruginosa x Tetracycline 3, S. aureus x Fluoroquinolone 3, S. aureus x Tetracycline 3. mic_value 1.87-127.2, continuous and spread evenly over 0-128 (mean 66.5, std 39.4: the std of a uniform 0-128 variable is 37): not a MIC (MIC values sit on dilution steps and are skewed), so the "MIC" claim does not hold.
2 Recipe: fill = x = species, geom_violin default (trim true), facet_wrap(amr_class). Fits the data.
3 Plot (SEEN): 4 panels of 4 violins; violins built from 2-12 points show rounded shapes, waists and bulges that are noise (the K. pneumoniae Fluoroquinolone violin is drawn from 2 values). Violin bottoms and tops are flat (cut at the data). Colour = species repeats the x axis, legend redundant, y axis is shared and starts below zero. No count is shown.
4 Tags: Comparison / "1 Numeric, 2 Categorical (Faceted)" / Intermediate / geom_violin / distribution / medium+. Pattern and show fit; `medium+` does not fit cells of 2-12 (the family could also be Distribution).
5 Guidance: "Advanced architectural partitioning" vs difficulty Intermediate; "Distribution across species, split by AMR class": matches the recipe. Interpretations pasted.
Suggestions: (a) more rows per cell (or fewer facets); (b) put the points (jitter) over the violin, or show n; (c) tag sample_size as what is true; (d) MIC data on dilution values or call the column something else. New picture: yes.

## 17. violin_simple  -- MINOR
1 Data: 100 rows, 4 classes 20-28 rows each (RUN); mic_value 1.99-127.0 continuous, uniform-like, same issue as violin_faceted (not dilution steps, "mic_value" label).
2 Recipe: fill = x = amr_class, geom_violin, nothing else. Fits.
3 Plot (SEEN): four violins with wide wavy outlines, flat tops and bottoms (cut at the data); shapes look "bimodal" (Beta-lactam, Fluoroquinolone, Tetracycline have two bulges) from about 26 points drawn from a flat distribution: the picture teaches bimodality that is noise. No median, no points, no n: nothing tells the reader how few points back each shape. Legend repeats the x axis; legend title lower case.
4 Tags: Distribution / 1 Numeric, 1 Categorical / Simple / geom_violin / distribution / medium+. Fit (20-28 per group is at the lower edge of medium+).
5 Guidance: "A hybrid between boxplot and density. The 'Gourmet' distribution view": slogan; "Transformation Logic: This is a basic demonstration of geom_violin mapping": fine; Interpretations is pasted boilerplate and says nothing about the plot. No sentence on how to read a violin.
Suggestions: add a median or the points (a second layer) and a text line on how to read a violin and on noise at n about 25; MIC values on dilution steps or a different column name. Picture: yes if a layer is added.

## Summary table

| example | verdict | the problems in a few words | needs a new picture |
|---|---|---|---|
| jitter_strip | SOUND | redundant colour only | no |
| line_grouped | MINOR | causal text, sample_size medium+ for 35 summaries, no n | no |
| line_simple | MINOR | y not from zero, n hidden, causal intervention sentence, medium+ | no |
| lollipop_advanced | WRONG | dots at 0 (F1 confirmed), axis y_zero, unsorted vs ranking tag, pasted text | yes |
| point_faceted | WRONG | date as String: unreadable x axis, one-year gap invisible, cells of 2-11, wrong pattern tag | yes |
| point_simple | WRONG | date as String; data are two January snapshots; 2 Numeric tag false | yes |
| proportion_bar | MINOR | what a count counts is not said; "or 0-100%" | no |
| qq_plot | MINOR | wrong S-curve/skew sentence, "tests", log2 not labelled, medium+ for n=15, "T3" | only if axis label changes |
| ridgeline_advanced | MINOR | faceted density not ridgeline (F2 confirmed), free_y, cut at range, pasted text | optional |
| scatter_smooth | SOUND | notes: lm only, band caution at n=9 | no |
| stacked_area | MINOR | pattern tag should be Year pattern, show: proportion vs counts | no |
| stacked_bar | SOUND | notes: what a count counts, unordered | no |
| step_chart | MINOR | carbapenems drawn under the others, "EUCAST" values unverified, linear scale, column name | yes |
| tile_simple | WRONG | colour = last row of each cell (16 of 16, F3 confirmed and tested), no aggregation | yes |
| violin_boxplot | WRONG | linear MIC axis crushes shapes, needle to 64, n=10, "continuous" | yes |
| violin_faceted | WRONG | violins from 2-12 points, uniform non-MIC data | yes |
| violin_simple | MINOR | noise looks bimodal, no n/median, non-MIC data | yes (if layer added) |

## Fit to show in a demo today
jitter_strip, scatter_smooth, stacked_bar, proportion_bar, stacked_area, line_grouped, qq_plot (say the n and read the text with the S-curve sentence removed), line_simple (with the caution about the axis). Not today: tile_simple, lollipop_advanced, point_simple, point_faceted, violin_boxplot, violin_faceted (the picture teaches something false or unreadable). With a spoken caveat only: ridgeline_advanced (call it a faceted density), step_chart (illustrative values, hidden carbapenems), violin_simple.

## Check of earlier flags concerning my examples
- F1 lollipop dots at 0: confirmed, and the fix (swap y and yend) rendered on a copy.
- F2 ridgeline as separate panels: confirmed, more precise: free y scales per panel, curves cut at the global data range.
- F3 tile squares: confirmed and tested; the colour shows the last row by file order in 16 of 16 cells; the mean matched 0.

## Not verified
- Whether `Date` typed x axes work for every recipe path in the app (I rendered it only on a scratch copy of point_simple, one example); no existing gallery recipe uses type Date.
- Whether the EUCAST values in step_chart are real (not checked against the EUCAST tables).
- What "count" counts in proportion_bar and stacked_bar and the unit of growth_index / avg_growth (the files do not say).
- The cause of the black line to 64 in violin_boxplot is reasoned from plotnine's trim=false, not isolated by a run.
- The statistician's opinion on the lm band and the Q-Q wording is mine as a data scientist; I used scipy only for Shapiro-Wilk on 15 values.
- Thumbnails (preview_thumb.png) and the Gallery page layout were not looked at.
- Taxonomy words of other examples were not compared.

## TAG TABLE (added for D-0402): pattern, sample_size, difficulty

Method: READ the recipe `mapping`, `layers`, `input_fields` and `taxonomy` of each example (yaml parsed, RUN) and the cheatsheet definitions (`assets/gallery_data/TAXONOMY_CHEATSHEET.md` lines 46-52 and 74-80: Simple = single geom, direct mapping, no wrangling; Intermediate = multiple geoms or position adjustments, may need pre-aggregation; Advanced = non-trivial wrangling, derived columns or specialised geoms; `any` = aggregated data, n does not matter; `individual points` = n < ~200 with visible dots; `medium+` = n >= ~50 recommended; `large` = n >= 500). Row counts per group from RUN (polars). "Aggregated" means one row per drawn element. Geom/stat layers are the layers named geom_* or stat_* (labs, theme, facet, coord, position are not counted).

| example | tag | value as written | value found | evidence |
|---|---|---|---|---|
| jitter_strip | pattern | 1 Numeric, 1 Categorical | 1 Numeric (y resistance_pct, Float64), 1 Categorical (x species, String; colour = same column) | READ mapping x species, y resistance_pct, color species. Fits |
| jitter_strip | sample_size | individual points | 100 rows, 18-22 per species (5 groups), raw isolates | RUN. Fits (n < 200, dots visible) |
| jitter_strip | difficulty | Simple | 1 geom layer (geom_jitter), no steps | READ. Fits |
| line_grouped | pattern | 1 Year, 1 Numeric, 1 Categorical | year Int64 used as numeric time, y Float64, colour species | READ. Fits |
| line_grouped | sample_size | medium+ | 35 rows, exactly 7 per species line; summary means, no n column | RUN. Does not fit: aggregated data is `any`; 7 per group is below ~50 |
| line_grouped | difficulty | Intermediate | 2 geom layers (geom_line, geom_point), no steps | READ. Fits the cheatsheet (multiple geoms) |
| line_simple | pattern | 1 Year, 1 Numeric | year Int64 + y Float64 (n_isolates declared, not mapped) | READ. Fits |
| line_simple | sample_size | medium+ | 7 rows, one per year; summary means (n_isolates 56-116 behind each, not shown) | RUN. Does not fit: `any` (aggregated) |
| line_simple | difficulty | Simple | 2 geom layers (geom_line, geom_point) | READ. Cheatsheet says multiple geoms = Intermediate; the same two layers give Intermediate in line_grouped. Inconsistent |
| lollipop_advanced | pattern | 1 Numeric, 1 Categorical | x species (cat); y y_zero and yend avg_growth: 2 numeric columns mapped, one is a constant 0 helper; no numeric variable besides avg_growth | READ + RUN (y_zero = 0 in 4 of 4 rows). Fits in meaning (1 real numeric); the mapping uses 2 numeric columns |
| lollipop_advanced | sample_size | any | 4 rows, 1 per species, aggregated | RUN. Fits |
| lollipop_advanced | difficulty | Intermediate | 2 geom layers (geom_segment, geom_point) + coord_flip | READ. Fits the cheatsheet |
| point_faceted | pattern | 2 Numeric, 1 Categorical (Faceted) | y numeric; x `date` declared String (a date as text, drawn as categories); colour species; facets amr_class (cols) and species (rows): 1 numeric, 1 date, 2 categorical (species used for colour and row facet) | READ + RUN (dates all in Jan 2024 / Jan 2025). Does not fit: no 2 numeric; vocabulary has no date + 2 categorical faceted word |
| point_faceted | sample_size | individual points | 100 rows; per species 23-31; per facet cell (16 cells) min 2, max 11 | RUN. Fits for the whole (n < 200) but cells of 2-11 are very thin |
| point_faceted | difficulty | Intermediate | 1 geom layer (geom_point) + facet_grid (2 variables), no steps | READ. Cheatsheet: single geom = Simple; facet is not a geom or position. Does not fit by the written rule |
| point_simple | pattern | 2 Numeric | y numeric; x `date` declared String (text, categorical axis of 48 values); colour species: 1 numeric, 1 date-as-text, 1 categorical | READ + RUN. Does not fit: only one numeric column is mapped; a date used as text |
| point_simple | sample_size | individual points | 100 rows; per species 21-32 | RUN. Fits |
| point_simple | difficulty | Simple | 1 geom layer (geom_point) | READ. Fits |
| proportion_bar | pattern | 1 Numeric, 2 Categorical | y count (Int64, a count only), x species, fill amr_class | READ. Fits (count-only plot: the numeric is a pre-made count) |
| proportion_bar | sample_size | any | 25 rows = 5 x 5 cells, 1 row per cell; counts 16-80, totals per species 190-287 | RUN. Fits (aggregated) |
| proportion_bar | difficulty | Intermediate | 1 geom layer (geom_col) + position_fill | READ. Fits (position adjustment) |
| qq_plot | pattern | 1 Numeric, 1 Categorical | sample log_mic (Float64), colour species; no x or y mapped (theoretical quantiles computed by the stat) | READ. Fits |
| qq_plot | sample_size | medium+ | 30 rows, 15 per species | RUN. Does not fit: 15 is far below ~50; `individual points` fits (n < 200, dots) |
| qq_plot | difficulty | Advanced | 2 stat/geom layers (geom_qq, geom_qq_line); log_mic is a ready column in the file, no step | READ. Advanced needs derived columns or wrangling; none exists in the recipe. Arguably Intermediate (two layers); the "specialised geom" reading could justify Advanced: her choice |
| ridgeline_advanced | pattern | 1 Numeric, 1 Categorical | x growth_index numeric, fill species; same species also the row facet | READ. Fits |
| ridgeline_advanced | sample_size | medium+ | 200 rows; per species 45-56 | RUN. Fits (about 50) |
| ridgeline_advanced | difficulty | Advanced | 1 geom layer (geom_density) + facet_grid with free_y, no steps | READ. Does not fit: single geom, no wrangling = Simple (or Intermediate for the facet) |
| scatter_smooth | pattern | 2 Numeric, 1 Categorical | x year Int64 (numeric), y resistance_rate, colour species | READ. Fits as written; but the same year-as-x structure is written "1 Year, ..." in line_grouped: the two examples use different words for the same structure |
| scatter_smooth | sample_size | individual points | 27 rows, 9 per species, yearly values | RUN. Fits (n < 200, dots visible); `any` also defensible |
| scatter_smooth | difficulty | Simple | 2 layers (geom_point, geom_smooth with lm and se) | READ. Cheatsheet: multiple geoms = Intermediate. Does not fit |
| stacked_area | pattern | 1 Numeric, 2 Categorical | x year Int64 (a time axis), y count, fill species: 1 year, 1 numeric (count), 1 categorical | READ. Does not fit: only 1 categorical column; the vocabulary word "1 Year, 1 Numeric, 1 Categorical" is the match |
| stacked_area | sample_size | medium+ | 27 rows, 9 per species; counts 78-251, aggregated | RUN. Does not fit: aggregated = `any` |
| stacked_area | difficulty | Intermediate | 1 geom layer (geom_area) + position stack | READ. Fits (position adjustment) |
| stacked_bar | pattern | 1 Numeric, 2 Categorical | y count (count-only plot), x species, fill amr_class | READ. Fits |
| stacked_bar | sample_size | any | 25 rows = 5 x 5 cells, 1 row per cell; totals 212-282 | RUN. Fits |
| stacked_bar | difficulty | Intermediate | 1 geom layer (geom_col) + position_stack | READ. Fits as position adjustment; it is the default position, so Simple is equally defensible |
| step_chart | pattern | 1 Numeric, 1 Categorical | x year Int64 (time), y breakpoint_change, colour drug_class: 1 year, 1 numeric, 1 categorical | READ. Does not fit: year axis; should be the Year pattern |
| step_chart | sample_size | any | 15 rows, 5 per drug class, aggregated list of values | RUN. Fits |
| step_chart | difficulty | Simple | 2 geom layers (geom_step, geom_point) | READ. Cheatsheet: multiple geoms = Intermediate. Does not fit by the written rule |
| tile_simple | pattern | 1 Numeric, 2 Categorical | fill growth_index numeric, x species, y amr_class | READ. Fits (the numeric is raw, not aggregated: see the colour finding) |
| tile_simple | sample_size | any | 100 raw rows in 16 cells, 2-13 rows per cell, not aggregated | RUN. Does not fit: `any` means aggregated data; here the cell has several rows and the plot shows one of them |
| tile_simple | difficulty | Simple | 1 geom layer (geom_tile), no steps | READ. Fits the layer rule, but "no wrangling" is false: the plot needs an aggregation step that is missing |
| violin_boxplot | pattern | 1 Numeric, 1 Categorical | y mic_value, x species, fill species (same column) | READ. Fits |
| violin_boxplot | sample_size | medium+ | 40 rows, 10 per species | RUN. Does not fit: 10 per group, below ~50; `individual points` fits |
| violin_boxplot | difficulty | Intermediate | 2 geom layers (geom_violin, geom_boxplot) | READ. Fits |
| violin_faceted | pattern | 1 Numeric, 2 Categorical (Faceted) | y mic_value, x species (fill species), facet amr_class | READ. Fits |
| violin_faceted | sample_size | medium+ | 100 rows; per species 22-27; per facet cell (16 violins) min 2, max 12 | RUN. Does not fit at the level of the drawn violin (2-12 each) |
| violin_faceted | difficulty | Intermediate | 1 geom layer (geom_violin) + facet_wrap | READ. Cheatsheet: single geom = Simple; facet is not counted. Does not fit by the written rule |
| violin_simple | pattern | 1 Numeric, 1 Categorical | y mic_value, x amr_class (fill same column) | READ. Fits |
| violin_simple | sample_size | medium+ | 100 rows; per class 20-28 | RUN. Does not fit: below ~50 per violin; `individual points` fits |
| violin_simple | difficulty | Simple | 1 geom layer (geom_violin) | READ. Fits |

Counts of mismatches (RUN of the table above, my reading of the cheatsheet): pattern wrong in 5 (point_faceted, point_simple, stacked_area, step_chart, plus scatter_smooth as an inconsistency of words with line_grouped); sample_size wrong in 8 (line_grouped, line_simple, qq_plot, stacked_area, tile_simple, violin_boxplot, violin_faceted, violin_simple); difficulty wrong by the written rule in 6 (line_simple, point_faceted, ridgeline_advanced, scatter_smooth, step_chart, plus qq_plot unclear). The cheatsheet rule for difficulty does not say how a facet, a stat or a computed column counts: she may want to say it before the tags are changed. Nothing was changed.
