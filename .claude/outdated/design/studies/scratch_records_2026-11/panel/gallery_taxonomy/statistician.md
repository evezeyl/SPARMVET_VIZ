# Gallery taxonomy review, STATISTICIAN viewpoint

Note: the project has no separate statistician agent yet. This is the statistician viewpoint, written by the panel agent. Labels: RUN, READ (file:line), REASONED. Well-known classifications are named from my own knowledge: REASONED, not looked up.

## Summary (6 lines)
1. Standard practice classifies a chart first by the question asked of the data, then by the variables, then by whether every observation or a summary is drawn (REASONED: e.g. Data-to-Viz decision tree, the Financial Times Visual Vocabulary, Cleveland/Tufte tradition, Wilkinson's grammar). "Family" follows the question; "What it Shows" is a second, overlapping question list. Merge them.
2. "Pattern" can be derived from the mapping and column types. RUN: a crude derivation agrees with the typed tag for 22 of 34 and differs for 12; every difference is informative (a hidden grouping variable, a date typed as text, a matrix typed "3 Numeric").
3. "Sample size" mixes a requirement of the method and a property of the example's data; it is not per group and has no number. It is the axis most likely to make a user pick a wrong plot (violin of 8 points).
4. "Difficulty" measures three different things; split it or derive it.
5. Missing: "what is drawn" (every observation / a summary the plot computes / a summary the file already holds) and "one row per observation or already summarised". Both decide whether the user's data fit.
6. Proposal: 6 axes, 3 derived, 3 typed and checkable (section "Proposal").

## Table
| axis | today | problem (with evidence) | proposed change | what it gives | what it costs or risks | reconsiders a decision? |
|---|---|---|---|---|---|---|
| family | 6 values: Comparison, Correlation, Distribution, Evolution, Part-to-Whole, Ranking (spec yaml, gallery section) | Close to the standard question list but "Ranking" is a way of ordering a comparison, not a question (REASONED). Errors: tile_simple, point_simple, point_faceted tagged Correlation, no relation drawn (statistician.md, gallery_verify); bubble x = n | Rename "Question"; values: Compare groups, Distribution, Relationship, Composition, Change over time. Allow 1 or 2. Ranking becomes the sorted property of a compare (dropped) | One list the statistician knows; no overlap with "show" | 34 recipes re-tagged; spec; cheatsheet; filter label | D-0397 (names) information only |
| show | 9 values: change, distribution, frequency, normality, proportion, ranking, relationship, trend, uncertainty | 6 of 9 repeat a family value (distribution, ranking, proportion, relationship, trend, change); frequency = a histogram computation; normality = a use of Q-Q; uncertainty = a layer property. RUN: in 34 recipes show equals the family in meaning for most (area_simple Evolution/trend, bar_* Ranking/ranking) | Remove. Replace by "What is drawn" (below) and derive "shows uncertainty" from ymin/ymax or se: true | Removes a duplicate axis, adds a distinction that matters | 34 recipes lose a tag; the checker loses one term list | none |
| pattern | 10 typed phrases mixing variable counts, "Year", "(Faceted)", "(Matrix)" | RUN: derived vs typed differ in 12 of 34: bar_simple (counts, no numeric column), density_simple and histogram_simple (fill variable not counted), boxplot_simple (two categories mapped), point_simple/point_faceted (date is String, typed "2 Numeric"), heatmap_correlation (var1, var2 are String, typed "3 Numeric (Matrix)"), dumbbell and step_chart (year typed numeric), bubble (size = 3rd numeric), connected_scatter, stacked_area | Derive: numbers of numeric / categorical / time columns mapped, and panels yes/no, from mapping + input_fields + facet layers. Show as a fact, not a tag | Cannot drift from the recipe; panels become its own filter | Loses the author's intent for stat-computed plots (bar_simple has no y). Needs a rule for count, year, matrix. Checker change | D-0402 (pattern is typed and checked) |
| difficulty | Simple/Intermediate/Advanced | Measures three things: layer count (violin_boxplot 2 layers = Intermediate), data preparation (heatmap_correlation Advanced but only reads a 4-column table), reading skill (qq_plot Advanced, 2 layers, no wrangling). RUN: only 3 of 34 recipes mention any wrangling step | Split: "Layers" (derived number), "Data preparation" (given as is / summarise first / compute a column), drop the single word. If kept: define it as preparation only | A user can tell what they must do before the plot | Re-tag; recipes need a convention for the preparation | D-0403 (difficulty check) |
| sample_size | any / individual points / medium+ / large | "individual points" is not a size. Whole table, not per group: violin_faceted has 100 rows but groups of 2 to 3 (data_scientist verification); violin_boxplot n = 10 tagged medium+. Thresholds only in the cheatsheet (n >= ~50, >= 500) | Rename "Observations needed per group". Four bands with a number: any (every row is drawn), 10+, 30+, 100+, per drawn group (box, violin, curve, colour). A derived second fact: the smallest group in the example data. Mismatch = advice | Prevents the commonest wrong choice; checkable | Thresholds are conventions (REASONED), the owner must set them; 34 re-tags | D-0402, D-0403 |
| geom / chart type | geom derived; Chart type new | Chart type words are the statistician's search term; geom the plotnine user's | Keep both as decided; add checker: layer set compatible with the chart type | Both audiences | none | D-0398 |
| missing: what is drawn | - | A boxplot shows a summary of raw data; a bar of mean_resistance shows a summary already in the file; a jitter shows every row. The user needs to know this to see whether their file fits | New axis, 3 values (several allowed) | Maps to "my data are raw or already summarised" | Derivable for most from layers; the file-side part needs the row check | none |

## Proposal in full
Six axes. A filter ticks values within an axis (union) and across axes (intersection), READ app/modules/gallery_listing.py:81-85.

1. Question (typed, 1 to 2 values). Meaning: what you want to learn. Compare groups; Distribution; Relationship; Composition; Change over time.
2. Chart type (typed, closed list, D-0398). Meaning: what a person would call the picture.
3. What is drawn (derived from layers, advice on the file). Every observation (points, jitter, sina) / A summary computed by the plot (box, violin, density, histogram, ECDF, bin, smooth fit) / A summary already in the file (bar of a mean, pointrange with given limits, line of given means, tile).
4. Variables (derived). "1 numeric, 1 category, panels" as a fact from mapping, types and facet layers.
5. Observations needed per group (typed band, checked against the data). any / 10+ / 30+ / 100+ per drawn group. Thresholds REASONED: a box needs about 5 to 10, a violin or Q-Q about 30, a histogram 100 or more, 2D bins hundreds.
6. Preparation (typed or derived). None, summarise first, compute a column.
Dropped: show, difficulty (as one word). Kept: geom (derived).

Per example under the proposal (axes I change). Min = observations needed per group; Panels derived.
| example | Question | Drawn | Min per group | Panels |
|---|---|---|---|---|
| area_simple | Change over time | in file | any | no |
| bar_grouped | Compare groups | in file | any | no |
| bar_horizontal | Compare groups | in file | any | no |
| bar_simple | Compare groups, Composition | computed (counts) | any | no |
| beeswarm_sina | Distribution, Compare groups | every | any | no |
| boxplot_faceted | Compare groups, Distribution | computed | 10+ | yes |
| boxplot_simple | Compare groups, Distribution | computed | 10+ | no |
| bubble | Relationship | in file | any | no |
| connected_scatter | Relationship, Change over time | in file | any | no |
| density_2d_bin | Relationship | computed | 100+ (whole plot) | no |
| density_simple | Distribution | computed | 30+ | no |
| dumbbell | Compare groups, Change over time | in file | any | no |
| ecdf | Distribution | computed | 10+ | no |
| error_bar | Compare groups | in file (limits given) | any | no |
| freqpoly | Distribution | computed | 100+ | no |
| heatmap_correlation | Relationship | in file | any | no |
| histogram_simple | Distribution | computed | 100+ | no |
| jitter_strip | Compare groups, Distribution | every | any | no |
| line_grouped | Change over time | in file | any | no |
| line_simple | Change over time | in file | any | no |
| lollipop_advanced | Compare groups | in file | any | no |
| point_faceted | Change over time (x = date) | every | any | yes |
| point_simple | Change over time (x = date) | every | any | no |
| proportion_bar | Composition | in file (shares computed) | any | no |
| qq_plot | Distribution | computed | 30+ | no |
| ridgeline_advanced | Distribution, Compare groups | computed | 30+ | yes |
| scatter_smooth | Relationship, Change over time | every + computed fit | 10+ | no |
| stacked_area | Composition, Change over time | in file | any | no |
| stacked_bar | Composition | in file | any | no |
| step_chart | Change over time | in file | any | no |
| tile_simple | Compare groups | MISMATCH: 100 rows, one colour per cell (last row drawn, gallery_verify finding) | any after summarising | no |
| violin_boxplot | Distribution, Compare groups | computed | 30+ | no |
| violin_faceted | Distribution, Compare groups | computed | 30+ | yes |
| violin_simple | Distribution, Compare groups | computed | 30+ | no |
Cost: 34 recipes, spec lists and meanings, checker (new derived checks, one removed term list), filter code (axes), cheatsheet (generated, D-0399). Gain: one question list, honest requirement, a way to match the user's data.
Under this table violin_boxplot (n = 10), violin_faceted (2 to 3 points per group), boxplot_* (2 to 14) would show an advice that the data fall below the band, a true statement today hidden.

## Filter with several values (point 5)
Tell the user: ticking two values in one axis widens the result (union); ticking across axes narrows it (intersection); an example with two values in one axis appears under both, so counts per value add up to more than 34; the first value is not a rank, nothing stores a main one (Q2 draft). "Select all" ticked means no filter on that axis.

## To decide first (ranked)
1. Is sample size a requirement per group, with numbers, and who sets the thresholds.
2. Merge family and show into one Question list; drop or keep Ranking.
3. Derive pattern (and panels) instead of typing it.
4. Split or derive difficulty.
5. Add "what is drawn".

## Not verified
- The thresholds (10, 30, 100) are conventions from my own knowledge, not looked up and not tested on this data.
- The 22 of 34 agreement is from a crude rule (mapped x, y, colour, fill, size, sample, facet columns; Int64 counted numeric), scratch: tmpAI/panel/gallery_taxonomy/statistician_scratch/cmp.py. A better rule would change the number.
- The classifications named (Data-to-Viz, FT Visual Vocabulary, grammar of graphics) are not looked up.
- The "3 of 34 recipes mention wrangling" is a grep for words in the recipes (RUN, crude).
- Which pictures render correctly was not checked.
