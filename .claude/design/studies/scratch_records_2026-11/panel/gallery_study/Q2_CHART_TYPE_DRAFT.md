# Gallery: the "Chart type" axis and the geom filter, DRAFT for the owner (decision D-0398; 2026-11-21)

Status: a draft to read. Nothing is written into recipes, the spec or the code. First draft by the data scientist viewpoint (filed by the coordinator from its report). The review by the user viewpoint comes next and is added at the end.

How it worked: it read all 34 recipes (layers, mapping, tags) with a script, the gallery part of the spec (`libs/utils/src/utils/recipe_spec.yaml:187-215`), `libs/viz_gallery/src/viz_gallery/taxonomy.py`, the gallery checks (`libs/utils/src/utils/recipe_check.py:1250-1283`), `app/modules/gallery_listing.py`, `gallery_viewer.py`, `gallery_manager.py`, and the draft of the names (Q1). It ran three small simulations of the filter logic on made-up data. "Verified" = read or run; "reasoned"; "assumed".

Facts that frame everything (verified):
- 11 of the 34 examples have several geom or stat layers: area_simple, connected_scatter, dumbbell, heatmap_correlation, line_grouped, line_simple, lollipop_advanced, qq_plot, scatter_smooth, step_chart, violin_boxplot.
- Only `geom_` and `stat_` layers count. Positions, coordinates, facets, scales, labels and themes are not in the geom filter.
- The geom filter has 20 words today. With all layers listed it has 23, and the 34 examples give 45 entries. The new words are `geom_text`, `geom_qq_line` and `geom_smooth`.

## 1. The chart-type words (the closed list for the spec)

Rule applied: a word is in the list when a reader would call the picture by that name without being corrected. An author writes one or two words, rarely three. A layer that only helps (markers, an outline, a label, a reference line, a trend line) gets no word; it is found under its geom in the layer filter.

The filter is a list of tick boxes with no text search (`gallery_viewer.py:87`), so the column "also called" helps only if the screen shows it beside the word. "Check" = a plainer wording not yet seen by the user viewpoint.

| Word | One-line explanation | Also called | Examples today |
|---|---|---|---|
| Bar chart | One bar per category; the length of the bar is a number (a count, a rate, an average). Bars lying sideways are the same chart. | bar graph, column chart | 6 |
| Stacked bar chart | Bars split into parts piled on top of each other, so the top shows the total and the parts the composition. The 100% version scales all bars to the same height and shows shares. | composition bar, 100% stacked bar | 3 |
| Grouped bar chart | For each category, one bar per subgroup side by side, to compare the subgroups. | clustered bar chart, side-by-side bars | 1 |
| Line chart | Points joined by a line, to follow one value over time and see the trend. | line graph, time-series plot | 2 |
| Step chart | A value that stays constant and then jumps, drawn as steps. | step plot, stair-step chart | 1 |
| Area chart | A line chart with the space under the line filled in, so the total amount stands out. | filled line chart | 2 |
| Stacked area chart | Counts of several groups over time, piled up; the top is the total. | stacked area graph | 1 |
| Scatter plot | Each record is one dot placed by two numbers. | scatterplot, scatter diagram, XY plot | 5 |
| Bubble chart | A scatter plot where the size of each dot shows a third number. | bubble plot | 1 |
| Connected scatter plot | Two measurements plotted against each other, the points joined in order. | connected scatterplot, path plot | 1 |
| Histogram | The range of one measurement is cut into slices (bins); each bar counts the records in a slice. | frequency histogram | 1 |
| 2D histogram | Two measurements at once; the plane is cut into rectangles coloured by how many records fall in each. | bivariate histogram, 2D bin plot | 1 |
| Frequency polygon | Like a histogram, but the counts per bin are joined by a line, so several groups can be overlaid. | line histogram | 1 |
| Density plot | A smooth curve, high where many measurements lie; it shows the shape, not how many. (Check) | kernel density plot, density curve | 2 |
| ECDF plot | For each value on the axis, the share of measurements at or below it. | cumulative distribution plot | 1 |
| Q-Q plot | Compares your values with those of a bell-shaped (normal) data set; dots near the diagonal mean roughly normal. (Check) | quantile-quantile plot, normal Q-Q plot | 1 |
| Box plot | A box with the middle half of the values, a line at the median, lines (whiskers) to the typical extremes, dots for very different values. | boxplot, box-and-whisker plot | 3 |
| Violin plot | A mirrored curve per group; wide where many measurements lie. | violin graph | 3 |
| Strip plot | Every measurement is a dot in its group, shifted sideways only so that dots do not overlap; the sideways position means nothing. | jitter plot, jittered dot plot | 1 |
| Beeswarm / sina plot | Every measurement is a dot, spread sideways where many values are close, so each value and the crowding are visible. | swarm plot, sina plot | 1 |
| Error bar plot | An average per group as a dot, with a line for the range around it, as given in the file. | point range, dot-and-whisker plot | 1 |
| Dumbbell chart | Two dots per category joined by a line, showing how far a value moved between two points. | dumbbell plot, barbell chart | 1 |
| Lollipop chart | A bar reduced to a stick with a dot at its value. | lollipop plot | 0 today (see section 2) |
| Heatmap | A grid of coloured squares; the colour carries a number. | heat map, tile plot, colour matrix | 3 |
| Ridgeline plot (only if the example is corrected, Q5) | Overlapping density curves, one per group, stacked vertically. | joy plot | 0 today |

24 words, plus Ridgeline. Twelve are held by one example only. In total 43 entries for 34 examples.

Its view on how fine the words are:
- **"Faceted" is not a chart type.** A facet is a layout that any chart can have: a "faceted violin" is a violin plot in panels. As a chart-type word it would put boxes, violins and scatter plots under one tick. Four examples have a facet (boxplot_faceted, point_faceted, violin_faceted, ridgeline_advanced). Finding panel layouts would be a separate, derived filter, and a separate decision. Side finding: `ridgeline_advanced` has a facet but its pattern tag does not say "(Faceted)".
- **Stacked bar and bar chart:** keep both words and put both on the stacked examples. "Bar chart" finds all six of the family; "stacked" and "grouped" are the names a statistician searches. The same for area and stacked area.
- **2D histogram and heatmap:** both words on `density_2d_bin`. One says what is computed, the other how it looks.
- **Where it departs from the draft of the names (Q1):** the filter word is "Strip plot" where the proposed example name is "Jitter Strip Plot", and "Error bar plot" where the name is "Error Bar / Point Range". The example names stay as in Q1. "Heatmap" and "Matrix Heatmap" fall under the one word "Heatmap".

## 2. The table, 34 examples

Layers are those read in the recipe, in order. "Main" is the viewpoint's reading; nothing stores a main value (your choice 6 below).

| Example | All geom and stat layers | Shown today (the first) | Proposed chart type | Why; main value | Note |
|---|---|---|---|---|---|
| area_simple | geom_area, geom_line | geom_area | Area chart | The line outlines the area. | several layers |
| bar_grouped | geom_col (side by side) | geom_col | Bar chart, Grouped bar chart | Main: Grouped. | - |
| bar_horizontal | geom_col | geom_col | Bar chart | Lying sideways is an orientation, not a type. | - |
| bar_simple | geom_bar | geom_bar | Bar chart, Stacked bar chart | Counts per species, split by drug class. Main: Stacked. | the same picture as stacked_bar |
| beeswarm_sina | geom_sina | geom_sina | Beeswarm / sina plot | - | - |
| boxplot_faceted | geom_boxplot | geom_boxplot | Box plot | Panels are a layout. | - |
| boxplot_simple | geom_boxplot | geom_boxplot | Box plot | - | - |
| bubble | geom_point | geom_point | Bubble chart, Scatter plot | Size is mapped. Main: Bubble. | - |
| connected_scatter | geom_path, geom_point | geom_path | Connected scatter plot, Scatter plot | Main: Connected. | several layers |
| density_2d_bin | geom_bin_2d | geom_bin_2d | 2D histogram, Heatmap | Counts in rectangles. Main: 2D histogram. | FOR THE OWNER: depends on the content correction (Q5) |
| density_simple | geom_density | geom_density | Density plot | - | - |
| dumbbell | geom_line, geom_point | geom_line | Dumbbell chart | The line is the connector, not a helper. | several layers |
| ecdf | stat_ecdf | stat_ecdf | ECDF plot | - | - |
| error_bar | geom_pointrange | geom_pointrange | Error bar plot | The limits come from the file. | - |
| freqpoly | geom_freqpoly | geom_freqpoly | Frequency polygon | - | - |
| heatmap_correlation | geom_tile, geom_text | geom_tile | Heatmap | Coloured squares with the value written in them. The recipe computes no correlation; "correlation" is not a chart type. | several layers; FOR THE OWNER (Q5); the type stays Heatmap whatever you decide |
| histogram_simple | geom_histogram | geom_histogram | Histogram | Stacked by class, still a histogram. | - |
| jitter_strip | geom_jitter | geom_jitter | Strip plot | - | - |
| line_grouped | geom_line, geom_point | geom_line | Line chart | The points are markers on the line. | several layers |
| line_simple | geom_line, geom_point | geom_line | Line chart | The same. | several layers |
| lollipop_advanced | geom_segment, geom_point | geom_segment | Today: Bar chart. After a correction: Lollipop chart, Bar chart. | The dots sit at 0 (verified in the data and the mapping): it is a bar chart drawn with sticks. | several layers; FOR THE OWNER (Q5) |
| point_faceted | geom_point | geom_point | Scatter plot | The facet is a layout. | - |
| point_simple | geom_point | geom_point | Scatter plot | - | - |
| proportion_bar | geom_col (filled to 100%) | geom_col | Bar chart, Stacked bar chart | The 100% version. Main: Stacked. | - |
| qq_plot | geom_qq, geom_qq_line | geom_qq | Q-Q plot | The line is the reference line. | several layers |
| ridgeline_advanced | geom_density | geom_density | Density plot | Four separate panels with no overlap: not a ridgeline. | FOR THE OWNER (Q5) |
| scatter_smooth | geom_point, geom_smooth | geom_point | Scatter plot | The trend line is found in the geom filter. | several layers |
| stacked_area | geom_area (stacked) | geom_area | Area chart, Stacked area chart | Main: Stacked area. | - |
| stacked_bar | geom_col (stacked) | geom_col | Bar chart, Stacked bar chart | Main: Stacked. | - |
| step_chart | geom_step, geom_point | geom_step | Step chart | The points are markers. | several layers |
| tile_simple | geom_tile | geom_tile | Heatmap | - | - |
| violin_boxplot | geom_violin, geom_boxplot | geom_violin | Violin plot, Box plot | Both are drawn; the box is narrow inside the violin. Main: Violin. | several layers; this answers your surprise |
| violin_faceted | geom_violin | geom_violin | Violin plot | The facet is a layout. | - |
| violin_simple | geom_violin | geom_violin | Violin plot | - | - |

## 3. A consequence of listing every layer in the geom filter: helper layers

You decided that every geom and stat layer of an example is listed. What follows (counts verified by script; the sorting into "helper" is the viewpoint's reading and is your call):
- Three layers exist only as helpers: `geom_text` (the value written in the squares of heatmap_correlation), `geom_qq_line` (the reference line of qq_plot), `geom_smooth` (the trend line of scatter_smooth). They become three new filter words, each with one example that is not "about" that word.
- `geom_point` goes from 4 examples to 10. In three of them (line_simple, line_grouped, step_chart) the points are only markers. A user who ticks `geom_point` to find scatter plots gets four line or step charts, a dumbbell and the lollipop among the 10.
- `geom_line` goes from 3 to 4; in area_simple it is only the outline.
- In total seven examples appear under a geom as a helper.

Options (the viewpoint does not choose):
- **A. One flat list of everything**, as decided: 23 words. Simple and complete.
- **B. Everything, with helpers in a second group.** A fixed list of helper names would live in the spec (text, label, horizontal and vertical lines, trend line, Q-Q line, rug). It sorts by name only, so it moves 3 examples; the markers on lines stay in the main group, because the role of a point is not in its name. Sorting those would need a mark on each layer in the recipe: a change of the recipe format, not proposed.

## 4. Counting when an example has several values

What the screen does today (verified):
- No count is shown beside each word. The visible number is "(N matched)", built from a set of examples, so each example is counted once (`gallery_listing.py:87-97`, `gallery_viewer.py:112`). That number stays right.
- What no longer holds: "the words of an axis add up to 34". There will be 43 entries for the chart type and 45 for the geom. Suggestion: if a count is ever shown beside a word, add the line "An example appears under every word that describes it, so the numbers add up to more than 34."

What "tick two words" should mean:
- Today, inside one axis, ticked words combine as "either"; different axes combine as "both" (`gallery_listing.py:84-96`).
- Recommendation of the viewpoint: keep "either" for the new axis and for the geom. Reasons: it is the one rule of every axis; all boxes are ticked at the start (`gallery_viewer.py:88`), so "both" would return no example before the user touches anything; "both" is still possible across two axes.
- The cost: ticking "Violin plot" and "Box plot" gives 5 examples, not only the one that has both. A switch "any / all" would be a new feature beyond your decision.

Two traps found by running:
- An example with no value on an axis disappears when every box of that axis is ticked. The check "at least one value" prevents it for the chart type.
- **The list of filter axes is written a second time by hand in the code** (`FILTER_AXES`, `gallery_listing.py:73`). A filter on an axis that is not in that list silently does nothing: the filter looks as if it works and filters nothing. Whoever builds the new axis must add it there, or better, read the list from the spec.

## 5. The checker

Today, for each of the five typed axes: the axis must be present; its value must be exactly one word of the closed list; a key that is not an axis is refused; `geom` cannot be written because it is derived.

What the new axis needs (the viewpoint's proposal):
- present; written as a list also when it holds one word; at least one word; each word exactly as in the closed list; no word twice.
- The order of the checks matters: the test "is it a list" must come before the test "is the word in the list", or a wrong recipe makes the checker crash instead of giving a message (found by running).

Can a word be checked against the layers? Partly.
- A full check is possible for most words: for example "Violin plot" needs `geom_violin`; "Box plot" needs `geom_boxplot`; "Bubble chart" needs points and a size.
- Only partly for "Stacked" and "Grouped" (stacking is the default, so only "not side by side" can be read).
- Not possible for "Dumbbell" (the same two layers are a line chart or a lollipop), and for "Lollipop" and "Ridgeline" only the presence of the layers can be read: no check can see that the dots sit at the value, or that the curves overlap.
- The reverse check, "this layer is present but its word is missing", would have caught `violin_boxplot` filed under violin only. It is safe for layers that are never helpers. The alternative is a human review of the 34 examples.

## 6. The names of the two filters on screen

- The geom filter is labelled "Primary Geom" today; "Primary" is no longer true. Options: "Plotnine layers (geom_ names)"; "Layers drawn (plotnine geom_ names)"; "Geom and stat layers".
- The new axis: "Chart type"; "Kind of chart"; "Name of the chart".
- Suggestion: show "Chart type" before the layer filter, so that a person without plotnine knowledge meets it first. The new axis also needs an icon, as the others have.
- For the builder: the line of tags on a guidance page prints one value per axis today (`taxonomy.py:84`) and must join several; the stored list of examples changes shape for these two axes.

## 7. To decide (ranked by the viewpoint)

1. Helper layers in the geom filter: one flat list (A), or helpers in a second group (B), knowing that B moves only 3 examples.
2. How far the general word goes: is `density_2d_bin` also a Heatmap; do the stacked and grouped bars also carry "Bar chart"; is a step chart also a line chart. The list can be shortened from 24 to 21 words by merging stacked and grouped into "Bar chart" and stacked area into "Area chart".
3. "Either" or "both" when two words are ticked in one axis. Recommended: either, as for every other axis.
4. The reverse check ("layer present, word missing"), or a human review of the 34.
5. Whether the lollipop is filed under "Bar chart" until Q5 is decided, and whether the word "Ridgeline plot" waits for Q5.
6. Whether a main value is stored (the first of the list) or the order means nothing.
7. The two names on screen and the icon.
8. Whether the "also called" words are shown on screen beside each word; kept only in the spec they help nobody.

## 8. Not verified (data scientist draft)
- The plainer explanations marked "Check" (density, Q-Q, strip, beeswarm) are not yet read by the user viewpoint.
- The look of the pictures: it relied on the draft of the names, and verified the lollipop from the data, not the picture.
- That a bar layer with a fill colour stacks by default in the plotnine used here (not run).
- Other places that read the six axes (the cheatsheet, the docs, tests, the conversion script).
- How the filter panel looks with 24 words.

## 9. Review by the user viewpoint (a scientist who knows the lab, not data science, and does not know plotnine; filed by the coordinator from its report; it read sections 1 to 7 and saw no picture)

### 9a. The words
Recognised as "what I am looking for": Bar chart, Stacked bar chart, Grouped bar chart, Line chart, Area chart, Scatter plot, Bubble chart, Histogram, Box plot, Heatmap; partly: Stacked area chart, Error bar plot.

**Never ticked, because the name means nothing to this user:** Violin, Strip, Beeswarm / sina, Dumbbell, Lollipop, Ridgeline, Step, Connected scatter, 2D histogram, Frequency polygon, ECDF, Q-Q, Density. That is 13 of the 25 words.

Explanations not understood, with a plainer wording ("Check" = to check with the data scientist):
| Word | What stops the reader | Plainer wording |
|---|---|---|
| Histogram | "bins" | The range is cut into slices; each bar counts the records in one slice. |
| 2D histogram | "plane" | Like a histogram for two measurements: small rectangles, coloured by how many records fall in each. (Check) |
| Frequency polygon | "bin" | Like a histogram, but the counts are drawn as a line, so groups can be laid over each other. (Check) |
| Density plot | "shape" | A smooth curve, high at the values where many measurements lie. |
| ECDF plot | the whole sentence | For each value on the axis, the share of your measurements at or below it. It would search "cumulative". |
| Box plot | "whiskers", "typical extremes" | A box for the middle half of the values, a line at the median; dots for very different values. (Check) |
| Error bar plot | "as given in the file" | Add: "the range is not computed here; it comes from your file". |

What would help: a small picture beside each word; the one-line explanation shown beside the word, not only in the spec; the "also called" names shown beside the word, because the filter has no text search.

### 9b. The length of the list, and the "family" filter that already exists
- 24 boxes are too many to read through. Going to 21 is a small gain.
- It prefers groups under headings that ask the user's question, with the words inside: "Compare groups", "Show how values are spread", "Follow over time", "Relate two measurements", "Show a grid of values".
- **Chart type and the existing "family" filter together are confusing.** Family already has Comparison, Distribution, Evolution (`recipe_spec.yaml:191`). "Distribution" in family and "Density plot" in chart type answer nearly the same question. Its reading: family is the question, chart type is the picture. That must be said on screen. If groups are added they repeat family; it would rather keep family as the groups and show the chart types under it.
- No word with 0 examples on screen (Lollipop, Ridgeline): the user ticks Lollipop, gets nothing, and yet an example named "Lollipop Chart" exists.
- All boxes are ticked at the start. To see only violin plots the user must untick 23 boxes. Suggestion: buttons "none" and "all".

### 9c. Helper layers in the geom filter
Not a problem for a user who does not use the geom filter. For a plotnine user it understands option B, if the second group has a title: "Helper layers (drawn to support the main chart, e.g. text, trend line, reference line)". Whichever option: a line on screen, "A layer appears here if the example draws it, even as a helper."

### 9d. Ticking two words
**This user expects only examples with BOTH** ("a screen of ticks reads like a shopping list"). The data scientist recommends "either". "Either" is acceptable to the user if it is said on screen: "Shows examples that match at least one ticked chart type. Violin plot + Box plot: 5 examples (one draws both)."

### 9e. The names of the two filters
Order: chart type first, then the layer filter. "Chart type" is understood; "Kind of chart" is plainer; "Name of the chart" is confusing next to the example name. For the layer filter: "Layers drawn (plotnine geom_ names)". The filter repeating the example name is a help. It is a problem only where the two differ: after Q1 the example "Jitter Strip Plot" would sit under the word "Strip plot", and "Error Bar / Point Range" under "Error bar plot". Suggestion: one word in both places.

### 9f. What would mislead this user
- The lollipop is found under "Bar chart" and not under its own name.
- A user who follows a value over time ticks "Line chart" and misses the step chart and the area chart; a user who ticks "Histogram" misses the frequency polygon.
- An example sits under one to three words with no main word: which word fits best is not shown.
- Content problems (the bubble chart with 5 rows, the heatmap with no valid correlation matrix) are hidden by a filter; they belong to your question on content (Q5).

### 9g. Where the two viewpoints differ (for you)
| Point | Data scientist | User |
|---|---|---|
| Ticking two words | either, as for every other axis | expects both; either only with a sentence on screen |
| The list | 24 conventional words, flat | groups under question headings, or the chart types shown under the existing "family" |
| Words with no example today | in the spec list, not on screen | must not be on screen |
| Step chart, area chart | their own words only | also findable from "Line chart" |
| Example name and filter word | may differ ("Jitter Strip Plot" under "Strip plot") | one word in both places |

Not verified by the user viewpoint: it saw no picture, read no recipe and no code, and took the counts from the draft.
