# Gallery: names and headings of the 34 examples, DRAFT for the owner (decision D-0397; 2026-11-21)

Status: a draft to read. Nothing in the Gallery is changed. First draft by the data scientist viewpoint (filed by the coordinator from its report); the review by the user viewpoint (a person not so good in data science) comes next and is added at the end.

Evidence of the draft: all 34 folders of `assets/gallery_data/` were read (the recipe: plot `ui_label`, layers, mapping, tags, fields; `example_meta.md`; the head and row count of the data file). Six pictures were looked at (lollipop, dumbbell, point_simple, ridgeline, density_2d_bin, tile_simple).

How your rule was applied:
- For the 13 examples whose name differs from the heading, the name takes the words of today's heading.
- For the other 21 the name is kept, with one exception (`density_2d_bin`).
- THREE names depart from your rule and are yours to judge, because your wording would be wrong for what the recipe draws: `density_2d_bin`, `heatmap_correlation`, `ridgeline_advanced`. They are marked "FOR THE OWNER".
- No two proposed names are equal. Two pairs are close: "Heatmap" and "Matrix Heatmap"; "Bar Chart" and "Stacked Bar Chart".

## 1. The table

| Example folder | Name today | Heading today | Proposed name | Proposed heading (a real description) | Terms to explain | Note on the example itself |
|---|---|---|---|---|---|---|
| area_simple | Area Chart | Area Chart | Area Chart | Area chart: one measurement followed over time, with the area under the line filled in so the total amount stands out. | area under the curve | 7 rows but tagged `medium+`. An area and a line are both drawn. |
| bar_grouped | Grouped Bar Chart | Grouped Bar Chart | Grouped Bar Chart | Grouped bar chart: compares a value across one category, with side-by-side bars for each subgroup inside it. | dodge, categorical | Tagged "Ranking", but it compares groups and does not rank them. |
| bar_horizontal | Horizontal Bar Chart | Horizontal Bar Chart | Horizontal Bar Chart | Horizontal bar chart: one bar per category with the bars lying sideways, so long category names stay readable. | categorical | The page says to sort the bars; the recipe does not sort them. |
| bar_simple | Bar Simple | Bar Chart | Bar Chart | Bar chart: counts how many records fall in each category, with each bar split by a second category. | categorical, stacked | F1 |
| beeswarm_sina | Beeswarm / Sina Plot | Beeswarm / Sina Plot | Beeswarm / Sina Plot | Beeswarm (sina) plot: every measurement is drawn as its own dot, spread sideways in proportion to how crowded the values are. | distribution, density | The seed is fixed, so the picture is reproducible. |
| boxplot_faceted | Boxplot Faceted | Faceted Boxplot | Faceted Boxplot | Faceted boxplot: boxplots of one measurement for each category, in a separate panel for each species. | boxplot, median, quartile, outlier, facet | 16 cells for 100 rows, at least 2 points per cell; a box of 2 points means little. |
| boxplot_simple | Boxplot Simple | Boxplot | Boxplot | Boxplot: summarises one measurement per group as the median, the middle half of the values and unusual values. | median, quartile, outlier | F2 |
| bubble | Bubble Chart | Bubble Chart | Bubble Chart | Bubble chart: a scatter plot where the size of each dot shows a third number. | scatter plot | F3 |
| connected_scatter | Connected Scatter Plot | Connected Scatter Plot | Connected Scatter Plot | Connected scatter plot: two measurements plotted against each other, with the points joined in order to show how they move together over time. | scatter plot | The line follows the order of the rows in the file, not the `year` column. Tagged "Correlation"; nothing is correlated. |
| density_2d_bin | 2D Bin Density | 2D Bin Density | **2D Histogram** (FOR THE OWNER) | 2D histogram: two measurements at once, with the plane cut into rectangles coloured by how many records fall in each. | bin, overplotting | F4. Rectangles of counts are a 2D histogram, not a smoothed density. Tagged "large" with 60 rows. |
| density_simple | Density Simple | Density Plot | Density Plot | Density plot: a smooth curve showing where the values of one measurement are concentrated, one curve per species. | distribution, density | The curves are not transparent, so one can hide another. |
| dumbbell | Dumbbell Chart | Dumbbell Chart | Dumbbell Chart | Dumbbell chart: two dots per category joined by a line, showing how far a value moved between two time points. | categorical | F5 |
| ecdf | ECDF Plot | ECDF Plot | ECDF Plot (cumulative distribution) | Cumulative distribution (ECDF): for each value on the axis, the share of measurements at or below it. | ECDF, distribution | The page reads shares of susceptible and resistant off the curve; that needs breakpoints, and the recipe draws none. |
| error_bar | Error Bar / Point Range | Error Bar / Point Range | Error Bar / Point Range | Error bar (point range): an average per group drawn as a dot, with a line showing the range it probably lies in. | confidence interval, mean | It only draws the limits given in the file; "95%" is in the title, not computed. |
| freqpoly | Frequency Polygon | Frequency Polygon | Frequency Polygon | Frequency polygon: like a histogram, but the counts per bin are joined by a line so several groups can be overlaid. | bin, histogram | The bin width suits log2 steps, but the data look like raw MIC values. |
| heatmap_correlation | Heatmap Correlation | Correlation Matrix (Heatmap) | **Matrix Heatmap** (FOR THE OWNER; your rule gives "Correlation Matrix (Heatmap)") | Matrix heatmap: a grid with one coloured, labelled square for each pair of variables, coloured by the value given for that pair. | heatmap, correlation | F6 |
| histogram_simple | Histogram Simple | Histogram | Histogram | Histogram: splits the range of one measurement into bins and counts how many records fall in each. | bin, distribution | Filled by drug class, so the bars are stacked by class. |
| jitter_strip | Jitter Strip Plot | Jitter Strip Plot | Jitter Strip Plot | Jitter strip plot: every measurement as a dot in its group, shifted a little sideways so dots do not hide each other. | jitter, distribution | The page recommends a boxplot on top; the recipe has none. |
| line_grouped | Line Chart (Grouped) | Line Chart (Grouped) | Line Chart (Grouped) | Grouped line chart: one line per group over time, to compare trends. | trend, categorical | - |
| line_simple | Line Chart (Simple) | Line Chart (Simple) | Line Chart (Simple) | Line chart: one measurement over time, points joined by a line to show the trend. | trend | A column `n_isolates` is in the file and not shown. |
| lollipop_advanced | Lollipop Advanced | Lollipop Chart | Lollipop Chart | Lollipop chart: a bar reduced to a stick and a dot, to compare values across categories. | categorical | F7 |
| point_faceted | Point Faceted | Faceted Scatter | Faceted Scatter Plot | Faceted scatter plot: a scatter plot split into a grid of panels, one for each species and drug class. | scatter plot, facet | `date` is text, so the axis is a list of labels. Tagged "2 Numeric". |
| point_simple | Point Simple | Scatter Plot | Scatter Plot | Scatter plot: each record is a dot placed by two values, to see how they relate. | scatter plot, correlation | `date` is text: the axis lists 48 dates as labels (seen on the picture), not a time axis. |
| proportion_bar | Proportion Bar Chart | Proportion Bar Chart | Proportion Bar Chart | Proportion bar chart: all bars scaled to the same height, so you see the share of each class and not the totals. | stacked, categorical | The plot turns counts into shares, which hides the totals (the page says so). |
| qq_plot | Q-Q Plot (Quantile-Quantile) | Q-Q Plot (Quantile-Quantile) | Q-Q Plot (Quantile-Quantile) | Q-Q plot: compares your measurements with the values a normal distribution would give, to check whether the data are roughly normal. | quantile, normal distribution | `log_mic` is given in the file; the page says it is computed. |
| ridgeline_advanced | Ridgeline Advanced | Ridgeline Distribution | **Stacked Density Panels** (FOR THE OWNER; your rule gives "Ridgeline Distribution") | Stacked density panels: one density curve per species, each in its own row, to compare the shapes of the distributions. | density, distribution, facet | F8 |
| scatter_smooth | Scatter Plot with Smoother | Scatter Plot with Smoother | Scatter Plot with Smoother | Scatter plot with a fitted line: the dots plus a straight line and a shaded band showing the trend and its uncertainty. | linear fit, confidence interval | The page says "linear model (or LOESS)"; the recipe uses the straight line only. |
| stacked_area | Stacked Area Chart | Stacked Area Chart | Stacked Area Chart | Stacked area chart: counts per group over time, piled up, so the top shows the total. | stacked | Tagged "proportion" but it shows counts. |
| stacked_bar | Stacked Bar Chart | Stacked Bar Chart | Stacked Bar Chart | Stacked bar chart: one bar per category, split into parts, so the top shows the total and the parts show the composition. | stacked | Close to `bar_simple` (F1). |
| step_chart | Step Chart | Step Chart | Step Chart | Step chart: a value that stays constant and then jumps, drawn as steps, for example a breakpoint revised in a given year. | breakpoint | The column is named `breakpoint_change` but holds the breakpoint value. |
| tile_simple | Tile Simple | Heatmap (Tile) | Heatmap | Heatmap: a grid with one coloured square for each combination of two categories, coloured by a number. | heatmap | F9 |
| violin_boxplot | Violin + Boxplot Overlay | Violin + Boxplot Overlay | Violin + Boxplot Overlay | Violin with boxplot: the shape of the distribution with the median and middle half of the values drawn inside it. | density, median, quartile | The violins reach beyond the range of the data (`trim: false`). |
| violin_faceted | Violin Faceted | Faceted Violin | Faceted Violin Plot | Faceted violin plot: violins of one measurement for each species, in a separate panel for each drug class. | density, facet | 16 cells for 100 rows; a violin of 2 points means little. |
| violin_simple | Violin Simple | Violin Plot | Violin Plot | Violin plot: the shape of a distribution drawn as a mirrored curve, one for each group. | density, distribution | Groups of 20 to 28 values. |

## 2. Flags on the content of the examples (for your later question on content, Q5; nothing changed)

- **F1 `bar_simple`.** The bars count rows per species, stacked by drug class. The column `value` is not used. The tag "1 Numeric" is wrong (two categories, no number). It differs from `stacked_bar` only in that the plot does the counting.
- **F2 `boxplot_simple`.** Boxes stand side by side per species inside each drug class. The tag says one categorical column; the plot uses two. `mic_value` runs to about 117, which is not an MIC scale.
- **F3 `bubble`.** `pct_resistant` holds fractions (0.39, 0.49) but the legend says "% Resistant". With 5 rows no relation can be judged.
- **F4 `density_2d_bin`.** The page says "Dark bins = many isolates". The picture shows the opposite: yellow is 4, dark purple is 1 (seen on the picture).
- **F5 `dumbbell`.** The year is a whole number, so the legend is a continuous colour bar from 2015 to 2023, though there are only two years (seen on the picture).
- **F6 `heatmap_correlation`.** The data are not a valid correlation matrix: the diagonal is not 1 (A,A is -0.5) and it is not symmetric (A,B is -0.3, B,A is 0.85) (read in the file). The recipe computes nothing. "Correlation" in the name would claim a computation that does not exist.
- **F7 `lollipop_advanced`.** The picture shows the dots at 0, not at the value (seen on the picture). Only the end of the stick carries the value. The axis label reads "y_zero". The plot is wrong for its name.
- **F8 `ridgeline_advanced`.** Four panels in a stack with no overlap, each with its own height scale. A ridgeline has overlapping curves; here heights cannot be compared between panels (seen on the picture).
- **F9 `tile_simple`.** 100 rows for 16 squares (2 to 13 rows each), but one colour per square. The squares are drawn over each other, so the colour is the last row drawn, not a mean (reasoned, not tested). A reader may take it for an average.
- **General.** The test data do not look like real MIC values. A sentence pasted on many pages ("Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap)") is wrong for most of them.

## 3. One explanation per technical term (to use everywhere)

- **distribution**: how often each value occurs among the measurements: where they pile up and how far they spread.
- **density**: a smooth curve showing where the measurements are concentrated. The area under it is 1, so it compares shapes, not counts.
- **bin, histogram**: a bin is a range of values. A histogram counts the measurements in each bin.
- **median**: the middle value. Half of the measurements are below it and half above.
- **quartile**: one of three cut points that split the sorted measurements into four equal parts. The box of a boxplot runs from the first to the third quartile, so it holds the middle half of the data.
- **boxplot**: a box (the middle half of the values) with a line at the median and lines ("whiskers") reaching to the typical extremes.
- **outlier**: a measurement far from the others (in a boxplot, beyond 1.5 box-lengths from the box). It can be an error or a real rare case. The plot does not remove it.
- **facet**: the picture split into small panels, one per group, with the same axes.
- **correlation**: a number between -1 and 1 telling how closely two measurements rise and fall together. It does not show that one causes the other.
- **jitter**: a small random sideways shift so that dots with equal values do not hide each other. The sideways position has no meaning.
- **dodge**: bars or boxes of the subgroups placed side by side inside each category.
- **stacked**: parts piled on top of each other, so the top shows the total.
- **overplotting**: so many dots in the same place that you cannot see how many there are.
- **categorical, numeric**: a category is a label (species, drug class); a numeric column is a measured number.
- **mean**: the sum of the values divided by their number.
- **confidence interval**: a range in which the true average probably lies; a wider range means less certainty.
- **linear fit**: the straight line that best follows the dots; the shaded band shows how uncertain it is.
- **ECDF (cumulative distribution)**: for each value on the axis, the share of measurements at or below that value.
- **quantile, Q-Q plot**: a quantile is a cut point (the median is the 50% one). A Q-Q plot compares your cut points with those of a normal distribution.
- **normal distribution**: the symmetric bell-shaped pattern that many statistical tests assume.
- **scatter plot**: each record is one dot placed by two numbers.
- **heatmap, tile**: a grid of coloured squares; the colour carries a number.
- **trend**: the overall direction of a value over time (rising, falling or flat).
- **MIC**: the smallest drug concentration that stops the growth of the bacteria; a lower value means a more susceptible isolate.
- **log2**: the number of times a value is doubled, so each step of 1 on the axis means twice the concentration.
- **breakpoint**: the MIC threshold used to classify an isolate as susceptible or resistant.
- **area under the curve**: the filled space between the line and the axis; it represents a total.

## 4. Not verified (data scientist draft)
- What else a rename touches (the list of examples, the cheatsheet).
- Only 6 of 34 pictures were looked at; the rest is from the recipe and the data.
- F9 (squares drawn over each other) is reasoned, not tested.
- Whether a person not trained in data science understands the sentences: the review below.

## 5. Review by the user viewpoint (a scientist who knows the lab and the bacteria, not statistics; filed by the coordinator from its report; it read the draft and two guidance pages, saw no picture)

Its test for a heading: "without statistics, can I say what I will see, and when I would pick this plot for my data?" Verdict: only a few headings pass. Most say WHAT is drawn, not WHEN to choose it. "Check" = the rewording must be checked by the data scientist before use.

### 5a. Headings: understood or not, and a plainer wording

| Example folder | Name | Heading | Plainer heading proposed by the user viewpoint |
|---|---|---|---|
| area_simple | clear | understood | - |
| bar_grouped | clear | not understood ("subgroup inside it" is vague) | Grouped bar chart: for each category (e.g. species), one bar per subgroup (e.g. drug class) side by side, to compare the subgroups. |
| bar_horizontal | clear | understood | - |
| bar_simple | clear but too general | partly ("split by a second category") | Bar chart: counts the records per category (e.g. isolates per species); each bar is divided by a second category (e.g. drug class). Check: the same picture as the stacked bar chart. |
| beeswarm_sina | not clear (unknown words) | not understood ("in proportion to how crowded") | Beeswarm (sina) plot: every measurement is one dot; dots are spread sideways where many values are close, so you see each value and where they pile up. |
| boxplot_faceted | "Faceted" is jargon | not understood | Boxplots in separate panels: for each species a panel, in it one box per category summarising the measurement (median, middle half of the values). Check. |
| boxplot_simple | clear | not understood ("median", "unusual values") | Boxplot: for each group, a box showing the typical value and how spread out the measurements are, plus dots for very different values. Check. |
| bubble | clear | understood | Bubble chart: dots placed by two numbers; the size of each dot shows a third number. |
| connected_scatter | not clear | partly | Connected scatter plot: two measurements plotted against each other, points joined in the order of the file, to follow the path over time. Check. |
| density_2d_bin | for the owner | not understood ("plane") | 2D histogram: the picture is cut into small rectangles; the colour of a rectangle tells how many records have those two values. |
| density_simple | not clear | not understood ("density") | Density plot: a smooth curve showing at which values most measurements lie, one curve per species. It compares the shape, not the number of records. |
| dumbbell | clear only with the picture | understood | - |
| ecdf | not clear | not understood | Cumulative curve (ECDF): for each value on the axis, the proportion of your measurements at or below that value. Use it to read "what share is under X". |
| error_bar | partly ("Point Range" no) | not understood ("the range it probably lies in") | Error bar: an average per group as a dot, with a line for the range around it (as given in your file). Check. |
| freqpoly | not clear | not understood ("bin") | Frequency polygon: counts of records in value ranges, drawn as a line instead of bars, so several groups can be laid over each other. |
| heatmap_correlation | for the owner | not understood ("pair of variables") | Matrix heatmap: a grid, one coloured square for each pair of items (rows and columns); the colour is the number your table gives for that pair. |
| histogram_simple | clear | not understood ("bins") | Histogram: the range of the measurement is cut into slices; each bar counts the records in a slice. It shows how the values are spread. |
| jitter_strip | not clear | not understood ("jitter") | Dot plot per group: every measurement is one dot; dots are moved a little sideways only so that they do not overlap (the sideways position means nothing). |
| line_grouped | partly | understood | Line chart with one line per group: to compare how groups change over time. |
| line_simple | partly ("Simple" means nothing) | understood | - |
| lollipop_advanced | clear only with the picture | partly, "a bar reduced to a stick and a dot" is good | - |
| point_faceted | not clear | not understood | Scatter plot in panels: dots placed by two numbers, one panel for each species and drug class. |
| point_simple | clear | understood | - |
| proportion_bar | clear | understood | - |
| qq_plot | not clear | not understood ("normal distribution") | Q-Q plot: checks whether your measurements are roughly bell-shaped (normal); dots near the diagonal line mean yes. Check. |
| ridgeline_advanced | for the owner | partly | One curve per species, each in its own row, to compare where the values lie. |
| scatter_smooth | clear | partly ("fitted line") | Scatter plot with a trend line: dots, plus a straight line through them and a shaded band showing how sure the line is. |
| stacked_area | clear | understood | - |
| stacked_bar | clear | understood | - |
| step_chart | clear with the picture | understood | - |
| tile_simple | clear | partly | Heatmap: a grid, one square for each combination of two categories (e.g. species and drug class); the colour shows a number. |
| violin_boxplot | not clear | not understood | Violin with box: a mirrored curve showing the spread of values, with the box (typical value and middle half) inside. |
| violin_faceted | not clear | not understood | Violin plots in panels: one panel per drug class, in it one violin per species. |
| violin_simple | not clear | not understood | Violin plot: for each group, a mirrored curve; it is wide where many measurements lie. |

### 5b. The term explanations
- Not understood as written: **density** ("the area is 1"; plainer: "a smooth curve, high where many measurements lie; it shows the shape, not how many", Check); **quartile** (say "the box holds the middle half of the values"; keep the word out of headings); **quantile, Q-Q** (plainer: "compares your values with what a bell-shaped data set would give", Check).
- Partly: **confidence interval** (plainer: "a range around the average; wider means less sure", Check); **boxplot** ("typical extremes" is vague); **mean** (say "average").
- "dodge" is understood but is jargon and should not be in a heading.
- Missing from the list, though they are names or words of headings: ridgeline, violin, lollipop, beeswarm, sina, dumbbell, step, Q-Q, smoother, error bar, point range, proportion, variable, share, uncertainty. The shape names need one sentence each.

### 5c. The names (one line in the list)
- From the name alone this user cannot choose: Beeswarm / Sina, Violin Plot, Jitter Strip, anything "Faceted", Q-Q, ECDF, Frequency Polygon, Lollipop, Dumbbell, Density, Step. Its remark: the name says the shape, not the task.
- Names it would confuse: Heatmap and Matrix Heatmap; Bar Chart and Stacked Bar Chart; Line Chart (Simple) and (Grouped); the three boxplots; the three violins; the five scatter plots; Histogram, Frequency Polygon, 2D Histogram and Density Plot; Jitter Strip and Beeswarm.
- The three names for you (it does not choose):
  - `density_2d_bin`: "2D Histogram" is understood better if one knows "histogram"; "Density" misleads (a smooth map is expected).
  - `heatmap_correlation`: "Correlation Matrix" tells what to do with the plot; "Matrix Heatmap" tells nothing of the use and is confused with "Heatmap". But "Correlation" may promise something the recipe does not do.
  - `ridgeline_advanced`: "Ridgeline" is unknown; "Stacked Density Panels" describes the picture, with "density" to explain.

### 5d. Suggestion beyond your decision: the same lines on every guidance page, in this order
1. Use it when: one question I can ask of my data.
2. Do not use it when: for example too few records per group.
3. Your data needs: which columns, numbers or labels.
4. What you will see: what each axis and the colour mean.
5. Hidden by this plot: for example the totals, the single values.
6. Terms: only the terms of this page, one sentence each.

### 5e. Where the two viewpoints differ (for you)
- The data scientist keeps the conventional names of the charts (your rule: "more scientific"). The user says a conventional name alone does not help to choose. Both can hold: the name stays conventional and the heading carries the "when to use it".
- The data scientist's headings say what is drawn; the user's rewordings add an example in brackets ("e.g. isolates per species") and drop the statistical words. Every rewording marked "Check" still needs the data scientist's yes.

Not verified by the user viewpoint: it saw no picture and opened 2 of the 34 folders.
