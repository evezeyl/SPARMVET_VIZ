# Gallery taxonomy review: data scientist viewpoint (2026-11-21)

Labels: RUN (scratch script `tmpAI/panel/gallery_taxonomy/data_scientist_scratch/derive.py`), READ (file:line), REASONED.

## Summary (6 lines)
1. Derive from the recipe what it states (layers, geoms, facets, mapped columns and their declared types, position, number of layers); let the author type only what the recipe cannot say (the question, the chart-type name, the data shape "one row per observation / already summarised").
2. Replace `pattern` (typed text) by derived facts. RUN: a plain derivation from mapped columns disagrees with the typed pattern in 17 of 34 examples, so today's tag has no stable definition (it is not "columns mapped", not "columns in the file").
3. `family` and `show` are one axis said twice (the user's question vs the message); merge into one typed axis "Question", with the user's own wording.
4. `difficulty` measures nothing fixed (layers? statistics? wrangling?). RUN: all 34 recipes have zero tier1 steps, so "wrangling" never occurs; keep or drop it only after the owner names what it measures. Derived "Layers: 1 / 2+" is the checkable part.
5. `sample_size` mixes a plot requirement and a property of the example data (RUN: rows are 4 to 200; "any" examples have 1 to 2 rows per group). Split or drop; the data can state its own n.
6. Keep `geom_` as derived (decided); add derived "Panels" and typed "Chart type" (D-0398) with the question axis above them.

## The table
| axis | today | problem (evidence) | proposed change | what it gives | what it costs or risks | reconsiders a decision? |
|---|---|---|---|---|---|---|
| family | 6 values: Comparison, Correlation, Distribution, Evolution, Part-to-Whole, Ranking (`recipe_spec.yaml:191`) | Mixed: "Comparison" and "Ranking" are a question, "Evolution" is the x axis (time), "Distribution" is what is shown. Same picture, different family: boxplot_simple Distribution, boxplot_faceted Comparison, jitter_strip Comparison, violin_faceted Comparison, violin_simple Distribution (READ recipes). Tile_simple is Correlation although it shows a grid of group means. | Merge with `show` into one axis "Question" (the user's wording). | One filter the three kinds of user all understand. | Retag 34; the user's question is the author's judgement, not derivable. | D-0397 (names), none otherwise |
| show | 9 values: change, distribution, frequency, normality, proportion, ranking, relationship, trend, uncertainty | Overlaps family 4 times (distribution, proportion, ranking, relationship, trend vs Distribution, Part-to-Whole, Ranking, Correlation, Evolution). "frequency" and "normality" are a statistic, not a question. "change" has one example (dumbbell). connected_scatter is tagged trend but family Correlation (READ). | Fold into "Question" (see proposal). | Drops 9+6 values to one list of about 7. | Same as above. | none |
| pattern | 10 text values | RUN: a derivation from mapped columns and declared types matches the typed value in 17 of 34 only. Causes: x and fill mapped to the same column counted twice or once; `year_label` and `year` are Int64 but are years or labels; point_simple `date` is declared String, so "2 Numeric" is not what the schema says; bar_simple has no numeric column (geom_bar counts) yet is "1 Numeric, 1 Categorical"; a facet column is not mapped. "(Faceted)" is a layout, not a data pattern. | Replace by derived items: columns mapped by role (x, y, colour...) with declared type; "Panels: yes/no" from facet_ layers; "Counts computed by the geom" from geom_bar, geom_histogram, stat_*. Author types nothing. | No wrong tags possible; the checker cannot disagree with itself. | Loses the short human phrase; a new derived display; a definition of the roles to write once in the spec. | D-0402, D-0403 (pattern checked against recipe: the check becomes a derivation) |
| difficulty | Simple / Intermediate / Advanced | Measures nothing fixed. RUN: layers per example 1 or 2; steps 0 in all 34. Advanced = heatmap_correlation (2 layers, 1 geom_text), qq_plot (2 layers), ridgeline_advanced (1 geom + facet + free scales), lollipop_advanced (the name says advanced, tagged Intermediate). | Either drop, or define as a derived count (layers, panels, steps) shown as facts. | No claim that the author must defend. | Loses a beginner's guide. A scientist new to data science will want a "start here" mark. | D-0402/D-0403 (difficulty check) |
| sample_size | any, individual points, medium+, large | Mixes two things. "any" examples have 4 to 25 rows (RUN) because the data are already summarised, so the value says "the data are summaries", not "n does not matter". "individual points" is a legibility limit (n < ~200), "large" a minimum. Per group n is 1 to 2 in many "any" examples. | Two parts: (a) data shape (typed): "one row per observation" or "already summarised" (b) rows and rows per group of the example data, derived, shown as numbers. | Clear for a copy: user knows whether to summarise first. | The data shape is typed by the author; cannot be derived (see point 4 below). | D-0402 |
| geom | derived, first geom/stat layer; D-0398 says all layers | Decided; right. 11 examples have 2 layers (RUN). | Keep derived; list all. | Plotnine/ggplot2 users find by geom_ name. | none | D-0398 (kept) |
| (chart type) | not yet; D-0398 | Draft has 24 words; 13 unknown to the user (draft 9a). | Typed, 1 to 3 words from a closed list; checkable (see below). | The statistician's names. | A closed list needs upkeep. | D-0398 (kept) |
| (panels) | none | Facets exist in 4 of 34 and are today a "(Faceted)" in pattern. | Derived yes/no and the facet function. | Removes "(Faceted)" from pattern. | One more filter. | none |
| (data shape) | none | See sample_size. | New typed axis, 2 values; verified in the checker by a rule (below). | The user knows what to bring. | Retag 34. | none |

## Proposal in full
Axes (T typed by author, D derived by the checker/app):
1. Question (T, one value, user's words): "Compare groups", "Show how values are spread", "Follow over time", "Relate two measurements", "Show parts of a whole", "Show a grid of values". Draft from user 9b. Checkable only in part (REASONED): not "which" but "is a value from the list", and a hint when the layers imply otherwise (see 4).
2. Chart type (T, 1 to 3 values, D-0398): closed list; check against layers where it can be read (violin needs geom_violin, boxplot needs geom_boxplot, bubble needs a mapped size; draft section 5).
3. Geom/stat layers (D): all layers (D-0398). Name for ggplot2: layers, for plotnine: geom_.
4. Data shape (T): "one row per observation" or "already summarised". Checkable as a hint only: a geom that computes (geom_histogram, geom_boxplot, geom_violin, stat_ecdf, geom_density, geom_bar) with "already summarised" is contradictory; geom_col, geom_pointrange with mapped ymin/ymax with "one row per observation" is contradictory. RUN: 4 examples map ymin/ymax or a precomputed mean, so the hint is derivable for them.
5. Panels (D): none / facet_wrap / facet_grid.
6. Layers count (D): 1, 2, 3+. Shown with the layers, not a quality claim.
7. Columns used (D): the list of mapped columns with role and declared type (numeric, categorical, year-like). Not a filter value; it replaces `pattern` as a display and optionally as a filter "number of numeric columns".
8. Rows in the example data (D): shown as a number and a rows-per-group minimum; not a typed band.
Dropped: family, show, pattern, difficulty, sample_size (as typed). Difficulty can stay as a defined derived count if the owner wants a start-here mark.

Value tables for the axes I change (Question; Data shape; derived panels and layers). Chart type is D-0398 and is left to the draft's table.

| example | Question | Data shape | Panels | Layers |
|---|---|---|---|---|
| area_simple | Follow over time | summarised | none | 2 |
| bar_grouped | Compare groups | summarised | none | 1 |
| bar_horizontal | Compare groups | summarised | none | 1 |
| bar_simple | Compare groups, Show parts of a whole | one row per observation | none | 1 |
| beeswarm_sina | Show how values are spread | one row per observation | none | 1 |
| boxplot_faceted | Show how values are spread | one row per observation | facet_wrap | 1 |
| boxplot_simple | Show how values are spread | one row per observation | none | 1 |
| bubble | Relate two measurements | summarised | none | 1 |
| connected_scatter | Relate two measurements, Follow over time | summarised | none | 2 |
| density_2d_bin | Relate two measurements | one row per observation | none | 1 |
| density_simple | Show how values are spread | one row per observation | none | 1 |
| dumbbell | Compare groups | summarised | none | 2 |
| ecdf | Show how values are spread | one row per observation | none | 1 |
| error_bar | Compare groups | summarised | none | 1 |
| freqpoly | Show how values are spread | one row per observation | none | 1 |
| heatmap_correlation | Show a grid of values | summarised | none | 2 |
| histogram_simple | Show how values are spread | one row per observation | none | 1 |
| jitter_strip | Show how values are spread, Compare groups | one row per observation | none | 1 |
| line_grouped | Follow over time | summarised | none | 2 |
| line_simple | Follow over time | summarised | none | 2 |
| lollipop_advanced | Compare groups | summarised | none | 2 |
| point_faceted | Relate two measurements | one row per observation | facet_grid | 1 |
| point_simple | Relate two measurements | one row per observation | none | 1 |
| proportion_bar | Show parts of a whole | summarised | none | 1 (position_fill) |
| qq_plot | Show how values are spread | one row per observation | none | 2 |
| ridgeline_advanced | Show how values are spread | one row per observation | facet_grid | 1 |
| scatter_smooth | Relate two measurements | one row per observation | none | 2 |
| stacked_area | Show parts of a whole, Follow over time | summarised | none | 1 |
| stacked_bar | Show parts of a whole | summarised | none | 1 |
| step_chart | Follow over time | summarised | none | 2 |
| tile_simple | Show a grid of values | one row per observation (a tile per row, 100 rows, but species x amr_class repeats, so colours overdraw: author question) | none | 1 |
| violin_boxplot | Show how values are spread | one row per observation | none | 2 |
| violin_faceted | Show how values are spread | one row per observation | facet_wrap | 1 |
| violin_simple | Show how values are spread | one row per observation | none | 1 |
(Data shape of bubble, connected_scatter, scatter_smooth: REASONED from mapped column names and row counts; connected_scatter 16 rows, bubble 5 rows are summaries; scatter_smooth is 27 rows of per-species per-year rates, may be per observation. An author must confirm.)

## What it costs
34 recipes retagged (two typed axes change, three removed; the `taxonomy` mapping shrinks); spec `gallery.axes` and `terms` (new words and meanings); checker (`recipe_check.py:1250-1283` accepts one string per axis today: `taxonomy[axis] not in terms` is a membership test on the whole value, so a list needs a type check first) plus new derived rules; filter code (`FILTER_AXES` is a second written list per the draft, derive it from the spec); cheatsheet (generated, D-0399). Gives: one axis the user can read, no tag that disagrees with its recipe.

## Which axes typed, which derived, how typed ones are checked (point 4)
- Derived: geom/stat list, number of layers, panels, mapped columns with roles and declared types, positions (stack, dodge, fill), whether a step in `tier1` summarises (steps are 0 for all 34 today, so always "no").
- Typed: Question, Chart type, Data shape.
- Check Question: membership only; a mismatch hint (e.g. a recipe with only geom_histogram tagged "Follow over time") is an advice (D-0403 style).
- Check Chart type: layer presence for most words; not for Dumbbell, Lollipop, Ridgeline (draft 5).
- Check Data shape: contradiction rule above, as an advice.
- Naming (point 7 of my weight): plotnine and ggplot2 call these "layers"; `geom_` is the function, `stat_` is the computation. "Position" (stack, dodge, fill) and "coord_flip" are not layers. A horizontal bar is `coord_flip`, a Lollipop here has the dots at 0 (verified in draft) so it is a bar.

## Filter with more than one value (point 5)
The user must be told: (1) an example sits under every word that fits, so counts add up to more than 34; (2) ticks in one axis mean "either"; across axes "both" (`gallery_listing.py:84-96` per draft); (3) which word is the main one, if any (nothing stores it); (4) a layer in the geom filter may be a helper (text, trend line, reference line); (5) an example with no value on an axis disappears when all boxes are ticked.

## To decide first (ranked)
1. Merge family and show into one "Question" axis, or keep two axes with a clear rule.
2. Replace typed pattern by derived columns-and-roles (needs the role definition).
3. What difficulty measures, or drop it.
4. Split sample_size into data shape (typed) and rows (derived).
5. Main value or no order for several chart-type words.
6. Closed list size (24 or 21) and the question groups on screen.

## Not verified
- The pictures (I read recipes, not images).
- Data shape of bubble, connected_scatter, scatter_smooth, tile_simple (author question).
- That plotnine stacks a geom_bar with a fill colour by default (not run).
- Where else the six axes are read (docs, tests, conversion script).
- The check order claim ("is it a list" before "is it in the list") taken from the draft; I read the checker at lines 1250-1283 and the membership test is as quoted.
- My derivation script is crude (year column named `year`, types Int64/Float64 = numeric); 17 of 34 is a lower-quality measure of the typed tag, not proof that the typed tags are wrong, since the typed meaning is undefined.
