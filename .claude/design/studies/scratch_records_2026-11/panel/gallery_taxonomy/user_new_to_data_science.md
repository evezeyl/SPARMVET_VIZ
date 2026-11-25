# Gallery taxonomy review: the user new to data science (panel-user, 2026-11-21; filed by the coordinator from its report)

Evidence: READ = read at the file and line cited (the brief, `libs/utils/src/utils/recipe_spec.yaml`, `assets/gallery_data/TAXONOMY_CHEATSHEET.md`, the user verification file, the chart type draft). RUN = nothing. REASONED = its judgement from the user's seat.

## Summary
1. "I arrive with a question (is resistance rising?) and a table (isolates, species, MIC, year). Today's filters ask me what the chart is called and what the table looks like, in the author's words."
2. It would use none of the six axes without help. It cannot tell "Family (Purpose)" from "What it Shows" (`recipe_spec.yaml:209-213`).
3. Proposed set, three filters in this order: **My question**, **What my table looks like**, **Chart type**. Two more, hidden at first: **Layers (geom)** for plotnine users, and **Panels**.
4. "Sample Size" and "Difficulty" are dropped as filters; their content moves to the text of the example.
5. "Primary Geom" is jargon; "Data Pattern" counts "Numeric / Categorical", words by which this user does not know its columns.

## The table by axis
| Axis | Today | What this user understands, and would tick wrongly | Proposed change | Reconsiders a decision? (information only) |
|---|---|---|---|---|
| Family (Purpose) | Comparison, Correlation, Distribution, Evolution, Part-to-Whole, Ranking (`recipe_spec.yaml:191`) | Understands "Comparison" and "Ranking". Not "Evolution" (a biology word) nor "Correlation" as a family. Would tick "Comparison" for species differences, but `boxplot_simple` is tagged "Distribution" and `jitter_strip` "Comparison": the same kind of picture under two families. | Replace by "My question"; merge with "What it Shows". | no |
| Data Pattern | ten combinations such as "1 Numeric, 2 Categorical (Faceted)" | Cannot map its MIC table to it. Would tick "1 Numeric, 1 Categorical" for MIC per species and miss the faceted examples. | Replace by "What my table looks like". Show the columns an example needs as a tag, not a filter. | D-0402 (pattern is one of the three tags checked) |
| Difficulty | Simple, Intermediate, Advanced | Would tick "Simple" and miss the most useful example. The cheatsheet mixes layers, data preparation and "specialised geoms" (`TAXONOMY_CHEATSHEET.md:49-51`). | Remove as a filter. Show "Needs a summary step first: yes / no" on the example page. | D-0402 |
| Primary Geom | `geom_area`, `geom_bin_2d`, ... | Unknown words. | Keep for plotnine users, collapsed under "Advanced: layers". | no (D-0398 keeps it) |
| What it Shows | change, distribution, frequency, normality, proportion, ranking, relationship, trend, uncertainty | "Frequency" against "distribution" is a trap (histogram is one, density the other). "Change" against "trend" (dumbbell against line). "Uncertainty" matches one example. | Merge into "My question". | no |
| Sample Size | any, individual points, medium+, large | "medium+" is never explained. It does not know its own n against it and would not filter on it. | Remove as a filter. Show a warning on the example: "Needs about 10 or more values per group." | D-0402 |

## The proposed filters, with the one-line meaning to show when the user points at a word
**1. My question** (an example appears under every question it answers; ticking two means "either")
- Compare groups: "Is one group higher or lower than another? (species, drug class, year A against year B)."
- See how values are spread: "Where most of my measurements lie, how far they stretch, whether they are bell-shaped."
- Follow over time: "Does a value go up or down over years or dates?"
- Relate two measurements: "Does one number go up when another goes up?"
- Show parts of a whole: "How a total is split, for example the share of each AMR class."
"Ranking" is folded into "Compare groups" (sorting is a property of the recipe, not a question); "uncertainty" too.

**2. What my table looks like**
- One row per measurement: "Each row is one isolate or one reading. The chart will count or summarise for you."
- Already summarised: "Each row is one group or one year with a computed number (a rate, a mean, a count). The chart draws it as given."
- A tag, not a filter: "Needs a summary step first": "Your table must be counted or averaged before this chart."

**3. Chart type**: plain names as in the chart type draft, "also called" shown on hover.

Order on screen: My question; What my table looks like; Chart type; then Panels and Layers (geom), both collapsed.

Two cautions: say on screen "An example appears under every question it answers, so the lists overlap. Ticking two boxes shows examples that match either." The hover text should state the consequence, for example on "Already summarised": "The chart will not compute anything. Wrong numbers in, wrong picture out."

## The 34 examples under this proposal
Q: Cmp = compare groups, Spr = spread, Time = follow over time, Rel = relate two measurements, Part = parts of a whole. T: Raw = one row per measurement, Sum = already summarised. Not checked against the data files by this viewpoint.

| Example | Q | T |
|---|---|---|
| area_simple | Time | Sum |
| bar_grouped | Cmp | Sum |
| bar_horizontal | Cmp | Sum |
| bar_simple | Cmp, Part | Raw (counts rows) |
| beeswarm_sina | Spr, Cmp | Raw |
| boxplot_faceted | Spr, Cmp | Raw |
| boxplot_simple | Spr, Cmp | Raw |
| bubble | Rel | Sum |
| connected_scatter | Rel, Time | Sum |
| density_2d_bin | Rel | Raw |
| density_simple | Spr | Raw |
| dumbbell | Cmp, Time | Sum |
| ecdf | Spr | Raw |
| error_bar | Cmp | Sum |
| freqpoly | Spr | Raw |
| heatmap_correlation | Rel | Sum |
| histogram_simple | Spr | Raw |
| jitter_strip | Spr, Cmp | Raw |
| line_grouped | Time | Sum |
| line_simple | Time | Sum |
| lollipop_advanced | Cmp | Sum |
| point_faceted | Rel | Raw |
| point_simple | Rel | Raw |
| proportion_bar | Part | Sum (to check) |
| qq_plot | Spr | Raw |
| ridgeline_advanced | Spr | Raw |
| scatter_smooth | Rel | Sum (9 years per species) |
| stacked_area | Time, Part | Sum |
| stacked_bar | Part, Cmp | Sum |
| step_chart | Time | Sum |
| tile_simple | Cmp | Sum |
| violin_boxplot | Spr, Cmp | Raw |
| violin_faceted | Spr, Cmp | Raw |
| violin_simple | Spr, Cmp | Raw |

## Cost and gain
Cost: the 34 recipes (two new typed fields, or one derived), the spec, the checker (it cannot verify "my question": the author types it), the filter code, the cheatsheet (generated). Gain: a user finds an example by its question, without jargon; the two typed tags with the most overlap and error (family and show) become one.

## To decide first (ranked by this viewpoint)
1. Merge Family and What it Shows into "My question"?
2. Replace Data Pattern by "What my table looks like", derived or typed?
3. Drop Difficulty and Sample Size as filters, and move their content to the hover text and the example page?
4. Hide the geom filter under "Advanced"?

## Not verified
The raw-or-summarised value of each example against its data; row counts; the checker and the filter code; the statistician's remarks and the data scientists' tag tables; how "either" works on new axes.
