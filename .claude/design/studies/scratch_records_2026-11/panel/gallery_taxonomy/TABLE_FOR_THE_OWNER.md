# Gallery: review of the taxonomy itself. One table for the owner (2026-11-21)

Status: a study. Nothing is decided here. No recipe, no spec and no code was changed. Her decision D-0404 asked for it: "a review of the taxonomy itself by the agents".

## 0. How to read this

- Three viewpoints reviewed the six axes of the Gallery filters. They are the data scientist (`data_scientist.md`), the statistician (`statistician.md`) and a user new to data science (`user_new_to_data_science.md`).
- No statistician agent exists yet. The statistician text was written by the data scientist agent, briefed with the statistician's question. It is a second look by the same kind of agent, not an independent person.
- RUN: the data scientist and the statistician each ran a derivation script on the 34 recipes (`data_scientist_scratch/derive.py`, `statistician_scratch/cmp.py`). I re-ran both and got the same numbers. I also counted the values per axis in the 34 recipes myself.
- REASONED: every chart classification named from memory (Data-to-Viz, Financial Times Visual Vocabulary, Wilkinson's grammar), the statistician's thresholds 10 / 30 / 100, and all "what the user would understand". Nobody looked these up. The user viewpoint ran nothing and saw no picture.
- Nothing is a decision. Where the viewpoints differ, I show each in one line and do not settle it.
- Her rule: an option is judged on merit. The column "Reconsiders a decision?" is information only. It is never an argument for or against an option.

## 1. The taxonomy today in one table

Source of the axes: `libs/utils/src/utils/recipe_spec.yaml:188-206` (READ). Counts of examples per value: RUN by me on the `taxonomy` mapping of the 34 recipes. They add up to 34 on each typed axis.

| axis (label on screen) | question it answers for the user | values and examples per value | typed by the author or read from the recipe |
|---|---|---|---|
| family ("Family (Purpose)") | What is the purpose of the chart? | Distribution 10, Correlation 7, Comparison 6, Evolution 5, Ranking 4, Part-to-Whole 2 | typed, one value |
| pattern ("Data Pattern") | What does my table look like? | 1 Numeric, 1 Categorical 14; 1 Numeric, 2 Categorical 6; 2 Numeric 3; 1 Numeric 2; 1 Year, 1 Numeric 2; 1 Numeric, 2 Categorical (Faceted) 2; 2 Numeric, 1 Categorical 2; 3 Numeric (Matrix) 1; 1 Year, 1 Numeric, 1 Categorical 1; 2 Numeric, 1 Categorical (Faceted) 1 | typed, one value; checked against the recipe since D-0402 |
| difficulty ("Difficulty") | How hard is it to reproduce? | Intermediate 17, Simple 14, Advanced 3 | typed, one value; checked against the number of layers since D-0402 |
| geom ("Primary Geom") | Which plotnine layer draws it? | 20 words today, 23 when every layer is listed (draft `Q2_CHART_TYPE_DRAFT.md`, section 0 facts, RUN by the data scientist) | read from the recipe: the first `geom_` or `stat_` layer; D-0398 says all layers |
| show ("What it Shows") | What message does the chart carry? | distribution 10, relationship 7, trend 5, ranking 4, proportion 3, frequency 2, change 1, uncertainty 1, normality 1 | typed, one value |
| sample_size ("Sample Size") | How much data does it need? | medium+ 15, any 13, individual points 5, large 1 | typed, one value; checked against the real number of rows since D-0402 |

How the filter combines (READ, `app/modules/gallery_listing.py:81-96`): inside one axis the ticked values mean "either"; across axes they mean "both". An axis with nothing ticked does not filter.

## 2. THE TABLE: one row per axis today, then one row per new axis

Who gave the evidence is in brackets: DS data scientist, ST statistician, US user. Evidence labels: RUN, READ, REASONED.

| axis | today | problem (evidence, who) | proposed change, per viewpoint where they differ | what it gives the user | what it costs or risks | reconsiders a decision? (information only) |
|---|---|---|---|---|---|---|
| family | 6 values, one per example | Mixes a question (Comparison), a time axis (Evolution) and a shape (Distribution). The same kind of picture has two families: boxplot_simple is Distribution, boxplot_faceted and jitter_strip are Comparison (READ recipes; DS, US). Tile, point_simple and point_faceted are Correlation but draw no relation (READ; ST, DS). "Ranking" is a way of ordering a comparison, not a question (REASONED; ST, US). | All three: merge with "show" into one question list, in the user's own words. DS: one value, in 6 words. ST: one or two values, in 5 words, "Ranking" dropped. US: five words as "My question" with a one-line meaning each; "Ranking" folded into "Compare groups". | One filter that the three kinds of user all read. | 34 recipes retagged. The author's judgement stays unchecked: the question cannot be read from the recipe (DS, ST). | D-0397 touches names only; none otherwise |
| show | 9 values | Six of 9 repeat a family value (READ spec; ST, DS). "frequency" and "normality" name a statistic, not a question. "change" and "uncertainty" have one example each (RUN by me). connected_scatter is "trend" with family Correlation (READ; DS). The word "comparison" does not exist in `show` (DS in the verification file). "Frequency" against "distribution" is a trap for a novice (REASONED; US). | All three: remove and fold into the question list. ST: derive "shows uncertainty" from ymin/ymax or an `se` setting. | Fewer boxes, no duplicate. | 34 recipes lose a tag; one term list less in the checker. | none |
| pattern | 10 phrases | A derivation from the mapped columns and their declared types disagrees with the typed value in 17 of 34 (DS, RUN) or in 12 of 34 (ST, RUN). Reason for the two numbers: different rules, see section 3. Cases: bar_simple has no numeric column; error_bar and bubble have three; point_simple's `date` is declared String; heatmap_correlation's `var1` and `var2` are String but the tag says "3 Numeric (Matrix)"; dumbbell and step_chart use a year typed Int64; a facet column is not mapped. "(Faceted)" is a layout, not a data pattern (DS). No word exists for count-only plots, dates, three numbers, a number used as a category (READ, verification file section 5.5). | DS and ST: derive the number of numeric, categorical and time columns and "panels yes or no" from the recipe; show them as facts, not as a tag. US: replace by "What my table looks like" in two values (see next row), with the columns shown as a tag, not a filter. | A tag that cannot disagree with its recipe. | The author's short phrase is lost for plots that compute (bar_simple: counts, no y). Rules for counts, years and matrices must be written once in the spec (DS, ST). | D-0402 (the pattern is one of the three checked tags). D-0403 (a mismatch is an advice) |
| difficulty | Simple / Intermediate / Advanced | Measures no fixed thing: layers, data preparation or reading skill (ST; READ `TAXONOMY_CHEATSHEET.md:49-51` per US). In the 34 recipes the `tier1` step lists are empty (DS, RUN), so "wrangling" never occurs, and no one agrees how a facet or a `stat_` layer counts (READ, verification file 5.5). Examples: line_simple (Simple) and line_grouped (Intermediate) have the same two layers; the example named lollipop_advanced is tagged Intermediate. | DS: drop, or show a derived count (layers, panels, steps) as facts. ST: drop the single word; give two facts instead: "layers" (derived number) and "preparation" (none / summarise first / compute a column). US: drop as a filter and show "Needs a summary step first: yes or no" on the example page. | No claim for the author to defend. | A new reader loses a "start here" mark. DS and US both warn about this. | D-0402, D-0403 (the difficulty check, by number of geom layers) |
| sample_size | any / individual points / medium+ / large | Mixes a requirement of the plot with a property of the example's data. "any" examples have 1 to 25 rows, because the data are already summarised (DS, RUN). It counts the whole table, not the drawn groups: violin_faceted has 100 rows but violins of 2 to 12 values (RUN; DS, ST). The thresholds exist only as "about 50 / 200 / 500" in the cheatsheet and are not exact (READ, verification file 5.5). "medium+" is never explained to a novice (US). | DS: two separate facts: the data shape (typed) and the number of rows and the smallest group (derived, shown as numbers). ST: "Observations needed per group" in 4 bands with numbers (any, 10+, 30+, 100+), checked against the smallest group of the example data; a mismatch is an advice. US: drop as a filter; put a warning on the example, for example "Needs about 10 or more values per group". | The commonest wrong choice (a violin of 8 points) becomes visible. | The bands 10 / 30 / 100 are the statistician's own convention (REASONED, not looked up); the owner would set them. 34 retags (ST). | D-0402 |
| geom | derived, first layer (D-0398: all layers) | 11 examples have several `geom_` or `stat_` layers (RUN, DS in the draft). Three layers are only helpers: `geom_text`, `geom_qq_line`, `geom_smooth`. `geom_point` goes from 4 to 10 examples, 7 of them as a marker (RUN, draft section 3). The name "Primary Geom" is no longer true. | All: keep, derived, all layers. US: collapse it under "Advanced: layers (geom_ names)" and show it after the chart type. DS: call it "layers", since in ggplot2 `geom_` is the function and `stat_` the computation. | plotnine and ggplot2 users find an example by the names they know. | Helper layers appear as words. The draft offers a second group for helpers; it is not part of this review. | D-0398 (kept) |
| NEW chart type | not yet; D-0398 | The draft has 24 words; the user did not know 13 of 25 (draft section 9a). "Family" and "chart type" together confuse the user (draft 9b). | All: keep, typed, closed list, several values (D-0398). US: show the words under the question headings, so "family" and "chart type" are one panel. DS: the check against the layers works for most words, not for Dumbbell, Lollipop or Ridgeline (draft section 5). | The statistician's names. | A closed list needs upkeep. 34 recipes get the field (already decided). | D-0398 (kept) |
| NEW panels | none | Facets exist in 4 of 34: boxplot_faceted, point_faceted, violin_faceted, ridgeline_advanced (RUN). Today "(Faceted)" sits inside the pattern; ridgeline_advanced has a facet but no "(Faceted)" in its pattern (DS). | All three: a derived yes or no (DS: none, `facet_wrap`, `facet_grid`). US: collapsed at first. | Removes "(Faceted)" from the pattern; a user who wants panels finds them. | One more filter. | none |
| NEW data shape ("what my table looks like") | none | Whether the user's file must be one row per observation or already summarised decides whether an example fits. No axis says it; sample_size and difficulty carry it badly (DS, ST, US). | DS and US: typed, two values: "one row per measurement" and "already summarised". ST: an axis "what is drawn" in three values, mostly derived from the layers: every observation / a summary computed by the plot / a summary already in the file. | The user knows what to bring. | DS and US: a typed field, 34 retags, checkable only as a contradiction rule (below). ST: needs a rule per geom. | none |
| NEW question | none; replaces family and show | See the rows family and show. | See there. | See there. | See there. | none |
| NEW rows and smallest group | none | The example's real number of rows and its smallest drawn group can be read from the data (DS, ST, RUN). | DS: derived, shown as numbers. ST: derived and compared with the typed band. US: not named. | The user sees n before copying. | A rule for what "a group" is (mapped categories, facets). | D-0402 (sample size checked against the real number of rows) |

## 3. Where the three viewpoints agree

| point | evidence |
|---|---|
| Family and "what it shows" are one axis said twice. Merge them into the question the user asks. | Six of 9 `show` values repeat a family value (READ spec; ST). The user could not tell them apart (READ `recipe_spec.yaml:209-213`; US). Same picture, different family: boxplot_simple, boxplot_faceted, jitter_strip (READ recipes; DS, US). |
| "Ranking" is not a question of its own. | ST and US say so. DS leaves it out of its list. Only 4 examples carry it today. At least one is not ranked: bar_horizontal draws the bars alphabetically (verification file, SEEN); DS says nothing is ranked in bar_simple (verification file 5.4). |
| The pattern should be read from the recipe, not typed as a phrase. | DS and ST each ran a derivation: it disagrees with the typed tag in 17 (DS) or 12 (ST) of 34. US wants it replaced by a plainer axis. The two counts differ because the rules differ: the DS script counts only the aesthetic columns x, y, colour, fill, size, group and others, excludes facet columns and counts a column named `year` as "Year". The ST script counts only x, y, colour, fill, size and sample, includes facet columns and counts a year as numeric. I re-ran both: DS 17 differ, 17 agree; ST 12 differ, 22 agree. |
| Difficulty measures nothing fixed. | In the 34 recipes the `tier1` step lists are empty (DS, RUN). ST says it measures three different things (layers, preparation, reading skill) and found only 3 of 34 recipes that mention preparation in their text (a grep, crude). |
| Sample size mixes two things: a requirement of the plot and a fact of the data. | "any" examples have 1 to 25 rows (RUN; DS). ST: the table has 100 rows, the groups have 2 to 12 (RUN). US: "medium+" is not understood. |
| Keep the geom filter, derived and listing all layers; keep the typed chart type. | D-0398; no viewpoint argued against it. |
| Panels (facets) should be a derived property. | All three. |
| The data shape (raw or summarised) is missing. | DS and US as a typed axis, ST as "what is drawn". |
| An example sits under several values, so the counts add up to more than 34. The user must be told. | All three; section 5. |

## 4. Where they differ

| point | data scientist | statistician | user |
|---|---|---|---|
| The list of questions and its words | 6 questions: Compare groups; Show how values are spread; Follow over time; Relate two measurements; Show parts of a whole; Show a grid of values. The text says "one value" but its own table gives two values to 4 of 34 examples: bar_simple, connected_scatter, jitter_strip, stacked_area (internal contradiction, not settled). | 5 questions: Compare groups; Distribution; Relationship; Composition; Change over time. One or two values. No "grid". | 5 questions as headings: Compare groups; Show how values are spread; Follow over time; Relate two measurements; Show parts of a whole. Its chart-type review (draft 9b) names a sixth heading "Show a grid of values"; its own proposal and table use five and have no grid. |
| "Distribution" or "See how values are spread" | plain words | the statistical word | plain words; "distribution" is not clear to it |
| Drop "Ranking" | not listed | dropped | folded into "Compare groups" |
| Difficulty | drop, or a derived count of layers, panels and steps | drop the word; derive "layers"; "preparation" typed or derived in 3 values | drop as a filter; "needs a summary step first" on the example page |
| Sample size | drop as typed; show rows and the smallest group as derived numbers | keep as a typed requirement per drawn group in bands 10 / 30 / 100 with numbers; compare with the data; mismatch is an advice | drop as a filter; a warning on the example |
| Which numbers for the bands | none | 10 / 30 / 100, REASONED, its own convention, "not looked up and not tested on this data" | "about 10 or more per group" as one sentence |
| "What my table looks like" against "what is drawn" | 2 values, typed ("one row per observation" or "already summarised") | 3 values, mostly derived from the layers: every observation / computed by the plot / already in the file | 2 values, typed, named "What my table looks like", shown second |
| Which filters come first | Question, then chart type, then the derived ones | Question, chart type, what is drawn, variables, requirement, preparation | My question; What my table looks like; Chart type; then Panels and Layers, both collapsed |
| Is the number of observations derived and shown | yes: rows and smallest group, as numbers | yes: the smallest group, beside the typed band | no: a warning text |
| Meaning of the question for the point_ examples | point_simple and point_faceted: "Relate two measurements" | "Change over time (x = date)"; no relation is drawn (verification file 3.9, 3.10) | "Relate two measurements" |
| heatmap_correlation, tile_simple | "Show a grid of values" | heatmap: "Relationship"; tile: "Compare groups" | "Relate two measurements" for the heatmap; "Compare groups" for the tile |
| Data shape of tile_simple and scatter_smooth | raw (tile: 100 rows, 2 to 13 per cell, the colour is the last row); scatter_smooth "may be per observation", to be confirmed by the author | tile: a mismatch noted ("in file", 100 rows) | "already summarised" for both (the user did not read the data) |

## 5. One combined proposal, to read as a whole

This is a proposal of the three viewpoints. The owner decides. Where they differ I give the variants side by side and choose none. The order is what a user would see. The one-line meaning is shown on hover or click (D-0404: "Option C"); I took the lines from the user viewpoint, which wrote them.

| # | filter on screen | typed by the author or read from the recipe | values | meaning shown on hover or click | how it can be checked |
|---|---|---|---|---|---|
| 1 | My question | typed, 1 or 2 values (ST, US; DS says 1 but gives 2 in its table) | Variant A (US, DS): Compare groups; Show how values are spread; Follow over time; Relate two measurements; Show parts of a whole. DS adds a sixth: Show a grid of values. Variant B (ST): Compare groups; Distribution; Relationship; Composition; Change over time. | Compare groups: "Is one group higher or lower than another?" Spread: "Where most of my measurements lie, how far they stretch." Time: "Does a value go up or down over years or dates?" Relate: "Does one number go up when another goes up?" Parts: "How a total is split, for example the share of each AMR class." (US) | The value must be one of the list. An advice when the layers contradict it, for example a histogram tagged "Follow over time" (DS). The question itself is the author's judgement. |
| 2 | What my table looks like | Variant A (DS, US): typed, 2 values. Variant B (ST): "what is drawn", 3 values, read from the layers, with an advice on the file | A: One row per measurement; Already summarised. B: Every observation; A summary computed by the plot; A summary already in the file. | A, summarised: "Each row is a group or a year with a computed number. The chart draws it as given. Wrong numbers in, wrong picture out." (US) | A: a contradiction rule as an advice. A computing layer (`geom_histogram`, `geom_boxplot`, `geom_violin`, `stat_ecdf`, `geom_density`, `geom_bar`) with "already summarised" is contradictory. A `geom_col` or a `geom_pointrange` with mapped ymin and ymax with "one row per measurement" is contradictory (DS). B: derived from the layers; the file side needs the row check (ST). |
| 3 | Chart type | typed, closed list, several values (D-0398) | The 24 words of the draft (`Q2_CHART_TYPE_DRAFT.md` section 1), with "also called" beside each word (US). Variant A (DS): a flat list. Variant B (US): the words under the question headings of filter 1. | The one-line explanations of the draft; the user asked for plainer wording for 7 of them (draft 9a). | Layer presence for most words; not for Dumbbell, Lollipop, Ridgeline; only part for Stacked and Grouped (draft section 5). |
| 4 | Panels | derived | none; panels (`facet_wrap` or `facet_grid`) | "The picture is split into small panels, one per group." (wording mine, as an example) | derived, nothing to check |
| 5 | Layers drawn (geom_ names) | derived; all layers (D-0398). US: collapsed, shown after the chart type | the 23 `geom_` and `stat_` words | "A layer appears here if the example draws it, even as a helper." (US) | derived, nothing to check |
| 6 | Group size | Variant A (ST): typed band per drawn group, checked. Variant B (DS): derived numbers, rows and smallest group. Variant C (US): not a filter; a warning on the example | A: any; 10+; 30+; 100+. B: numbers. C: none. | A: "Observations needed per drawn group (box, violin, curve, colour)." (ST) | A: against the smallest group in the data; a mismatch is an advice (D-0403). B: derived. C: text only. |
| 7 | What it takes to build | Variant A (DS): derived number of layers, panels and steps, shown, not a filter. Variant B (ST): "preparation" none / summarise first / compute a column. Variant C (US): the yes or no "Needs a summary step first" on the page. Variant D: drop (DS and ST name it as an option; US drops it as a filter) | see variants | "The number of layers is a count, not a quality claim." (DS) | The number of layers is derived; the preparation is typed or derived by the author's convention. |
| 8 | Columns used | derived (DS, ST). US: a tag, not a filter | the mapped columns with their role and declared type | "The columns this example needs." | derived |

Dropped by all three: family and show as they are, and the pattern as a typed phrase. Variant D under 7 drops difficulty; ST and DS also drop sample size as a typed word (variants B and C under 6).

One sentence each filter must say, in the screen text (all three agree on the content, section 3): an example appears under every word that fits, so the numbers add up to more than 34; ticks within a filter mean "either"; ticks across filters mean "both" (verified in `gallery_listing.py:81-96`); no word is "the main one", because nothing stores a main value (draft section 4); an example with no value on an axis disappears when every box is ticked.

## 6. The 34 examples under the proposal

Key. Question: Cmp = Compare groups, Spr = spread, Time = over time, Rel = relate, Part = parts of a whole, Grid = a grid of values. D = data scientist, S = statistician, U = user; "all" when the three give the same. Shape: raw = one row per measurement, sum = already summarised; for S: every / computed / in file. Chart type: the proposed words of the draft `Q2_CHART_TYPE_DRAFT.md` section 2 (these are the data scientist's words as of the draft). Layers: `geom_` and `stat_` layers (RUN, draft). Panels: RUN. Rows and smallest group: RUN, `derive.py`, grouped by the mapped categorical columns without the facet; where verification found the cells of a faceted or tile plot I give them with the source. S band = the statistician's group-size band. "VERIF" = this example was judged WRONG or MISLEADING by a viewpoint in the verification (`gallery_verify/TABLE_FOR_THE_OWNER.md` section 3, 18 examples); its value may change when it is corrected. D-0401 names three examples to correct first: heatmap_correlation, tile_simple, dumbbell. Dumbbell was MINOR in the verification (a legend problem).

| example | question(s) | shape / drawn | chart type(s) | panels | geom and stat layers | rows; smallest group | S band | flag |
|---|---|---|---|---|---|---|---|---|
| area_simple | all: Time | D, U: sum. S: in file | Area chart | none | geom_area, geom_line | 7; no groups | any | VERIF |
| bar_grouped | all: Cmp | all: sum / in file | Bar chart, Grouped bar chart | none | geom_col | 15; 1 | any | |
| bar_horizontal | all: Cmp | all: sum / in file | Bar chart | none | geom_col | 5; 1 | any | VERIF |
| bar_simple | all: Cmp, Part | D, U: raw. S: computed (counts) | Bar chart, Stacked bar chart | none | geom_bar | 100; 2 per segment (verification: 2 to 13) | any | |
| beeswarm_sina | D: Spr. S, U: Spr, Cmp | all: raw / every | Beeswarm / sina plot | none | geom_sina | 100; 20 | any | VERIF |
| boxplot_faceted | D: Spr. S: Cmp, Distribution. U: Spr, Cmp | all: raw / computed | Box plot | facet_wrap | geom_boxplot | 100; 21 per class, cells 2 to 11 (verification: statistician, RUN) | 10+ | VERIF |
| boxplot_simple | D: Spr. S: Cmp, Distribution. U: Spr, Cmp | all: raw / computed | Box plot | none | geom_boxplot | 100; 2 (verification: cells 2 to 14) | 10+ | VERIF |
| bubble | all: Rel | all: sum / in file | Bubble chart, Scatter plot | none | geom_point | 5; 1 | any | VERIF |
| connected_scatter | all: Rel, Time | all: sum / in file | Connected scatter plot, Scatter plot | none | geom_path, geom_point | 16; 8 | any | VERIF |
| density_2d_bin | all: Rel | all: raw / computed | 2D histogram, Heatmap | none | geom_bin_2d | 60; no groups | 100+ (whole plot) | VERIF |
| density_simple | all: Spr | all: raw / computed | Density plot | none | geom_density | 100; 20 | 30+ | VERIF |
| dumbbell | D: Cmp. S, U: Cmp, Time | all: sum / in file | Dumbbell chart | none | geom_line, geom_point | 12; 2 | any | D-0401 first pass |
| ecdf | all: Spr | all: raw / computed | ECDF plot | none | stat_ecdf | 30; 10 | 10+ | |
| error_bar | all: Cmp | all: sum / in file (limits given) | Error bar plot | none | geom_pointrange | 8; 1 | any | |
| freqpoly | all: Spr | all: raw / computed | Frequency polygon | none | geom_freqpoly | 45; 15 | 100+ | VERIF |
| heatmap_correlation | D: Grid. S, U: Rel | all: sum / in file | Heatmap | none | geom_tile, geom_text | 16; 1 | any | VERIF; D-0401 first pass |
| histogram_simple | all: Spr | all: raw / computed | Histogram | none | geom_histogram | 100; 19 | 100+ | |
| jitter_strip | all: Spr, Cmp | all: raw / every | Strip plot | none | geom_jitter | 100; 18 | any | |
| line_grouped | all: Time | all: sum / in file | Line chart | none | geom_line, geom_point | 35; 7 | any | |
| line_simple | all: Time | all: sum / in file | Line chart | none | geom_line, geom_point | 7; no groups | any | |
| lollipop_advanced | all: Cmp | all: sum / in file | Bar chart (Lollipop chart and Bar chart after correction) | none | geom_segment, geom_point | 4; 1 | any | VERIF |
| point_faceted | D, U: Rel. S: Time (x = date) | D, U: raw. S: raw / every | Scatter plot | facet_grid | geom_point | 100; cells 2 to 11 (verification: DS2 and ST) | any | VERIF |
| point_simple | D, U: Rel. S: Time (x = date) | D, U: raw. S: raw / every | Scatter plot | none | geom_point | 100; 1 (date and species) | any | VERIF |
| proportion_bar | all: Part | all: sum / in file | Bar chart, Stacked bar chart | none | geom_col (position fill) | 25; 1 | any | |
| qq_plot | all: Spr | all: raw / computed | Q-Q plot | none | geom_qq, geom_qq_line | 30; 15 | 30+ | |
| ridgeline_advanced | D, U: Spr. S: Distribution, Cmp | all: raw / computed | Density plot (Ridgeline only after correction) | facet_grid | geom_density | 200; 45 | 30+ | |
| scatter_smooth | D, U: Rel. S: Rel, Time | D: raw (to confirm). U: sum. S: every + computed fit | Scatter plot | none | geom_point, geom_smooth | 27; 9 | 10+ | |
| stacked_area | all: Part, Time | all: sum / in file | Area chart, Stacked area chart | none | geom_area | 27; 9 | any | |
| stacked_bar | D: Part. S: Part. U: Part, Cmp | all: sum / in file | Bar chart, Stacked bar chart | none | geom_col | 25; 1 | any | |
| step_chart | all: Time | all: sum / in file | Step chart | none | geom_step, geom_point | 15; 5 | any | VERIF |
| tile_simple | D: Grid. S, U: Cmp | D: raw (100 rows, colour = last row). U: sum. S: "mismatch", any after summarising | Heatmap | none | geom_tile | 100; 2 per cell (verification: 2 to 13) | any after summarising | VERIF; D-0401 first pass |
| violin_boxplot | D: Spr. S, U: Spr, Cmp | all: raw / computed | Violin plot, Box plot | none | geom_violin, geom_boxplot | 40; 10 | 30+ | VERIF |
| violin_faceted | D: Spr. S, U: Spr, Cmp | all: raw / computed | Violin plot | facet_wrap | geom_violin | 100; 22 per species, cells 2 to 12 (verification) | 30+ | VERIF |
| violin_simple | D: Spr. S, U: Spr, Cmp | all: raw / computed | Violin plot | none | geom_violin | 100; 20 | 30+ | |

Check on the table: under the statistician's bands, violin_boxplot (10 per species), violin_faceted (2 to 12), boxplot_faceted and boxplot_simple (2 to 14) fall below their band. Today this is hidden by the tag "medium+" (ST; RUN on the same numbers). The band 30+ for the violins is the statistician's own convention.

## 7. What it would change (facts, not a plan she must accept)

| place | what changes | where it is written today |
|---|---|---|
| the 34 recipes | the `taxonomy` mapping of each plot: fields added (question, data shape or what is drawn, chart type), fields removed or renamed (family, show, pattern, difficulty, sample_size, depending on her answer) | `assets/gallery_data/<example>/data_analysis_recipe.yaml`; the rule for the 6 axes is in `.claude/rules/rules_gallery_standards.md` section 2 |
| the spec | `gallery.axes`, `gallery.terms`, `gallery.display` (label and icon) and, for D-0399, the meaning of each word | `libs/utils/src/utils/recipe_spec.yaml:188-206` |
| the cheatsheet and the documentation | generated from the spec (D-0399: a test fails if a generated file differs); the rules and thresholds written there today (difficulty, sample size) go | `assets/gallery_data/TAXONOMY_CHEATSHEET.md` |
| the checker | it accepts one string per axis: `taxonomy[axis] not in terms` is a test on the whole value, so a list needs a type check first; new derived checks for the three tags of D-0402 as advices (D-0403) | `libs/utils/src/utils/recipe_check.py:1250-1283` (READ) |
| the filter code | the list of filter axes is written a second time by hand: `FILTER_AXES = ("family", "pattern", "difficulty", "geom", "show", "sample_size")`. A filter on an axis missing there silently does nothing. Read it from the spec instead (the draft found this) | `app/modules/gallery_listing.py:73` (READ) |
| the tag strip of the guidance pages | prints one value per axis today and must join several values; the strip has icons per axis | `libs/viz_gallery/src/viz_gallery/taxonomy.py:84` (READ); `rules_gallery_standards.md` section 3 |
| the stored list of examples | `gallery_index.json` pivots by axis (`by_<axis>`); its shape changes for every axis that changes. I did not find the code that writes it in `libs` or `app`; not verified | `gallery_listing.py:78-89` reads `by_<axis>` (READ) |
| the screen | the order of the filters, the names, the hover mark of D-0404, the "none" and "all" buttons (US) | `app/modules/gallery_viewer.py` (not read by me) |

Order of work if she agrees (my reading of D-0399, D-0401 and D-0404, not hers):
1. The taxonomy itself: her answers to section 8.
2. The spec text: the words and the one-line meanings (D-0399, D-0404), and the counting rules for the checked tags (D-0402).
3. The checker and the filter code, then the generated cheatsheet and documentation.
4. The 34 recipes, in the same pass as the content corrections, so that each example is written once (D-0401: "so that each example is written once").

## 8. To decide, ranked (larger first)

| # | question in one plain sentence | options | supported by | main gain | main cost | reconsiders a decision? (information only) |
|---|---|---|---|---|---|---|
| 1 | Do family and "what it shows" become one list of questions? | A: yes, 5 or 6 words in the user's language. B: keep two axes with a clear rule | A: DS, ST, US. B: nobody | one filter every user reads | the question stays the author's judgement | D-0397 touches names only; none |
| 2 | Is the pattern typed, or read from the recipe? | A: read from the recipe and shown as facts (DS, ST). B: replaced by a typed "what my table looks like" (US). C: kept as typed and checked | A: DS, ST. B: US. C: nobody | a tag that cannot disagree with its recipe | A: rules for counts, years and matrices. B: typed field | D-0402 (pattern typed and checked) |
| 3 | Is "what my table looks like" a new axis, and in how many values? | A: 2 typed values (DS, US). B: 3 values "what is drawn", mostly derived (ST). C: none | A: DS, US. B: ST | the user knows whether the example fits the file | A: typed, checked as a contradiction. B: a rule per geom | none |
| 4 | What happens to sample size? | A: a typed band per drawn group, with numbers (ST). B: derived numbers, no band (DS). C: a warning on the example, no filter (US) | each as listed | prevents a violin of 8 points | A: numbers are the statistician's convention; 34 retags. B: the user must read numbers. C: not filterable | D-0402 |
| 5 | What happens to difficulty? | A: drop. B: derived number of layers, panels, steps. C: split into layers and preparation (ST). D: "summary step first, yes or no" (US) | A, B: DS. C: ST. D: US | no claim to defend | a beginner loses a "start here" mark | D-0402 (difficulty checked against geom layers) |
| 6 | One main chart-type word per example, or no order? | A: store the first value as the main one. B: no order, as the draft's section 4 says | not given by the viewpoints; draft question 6 | a user sees which word fits best | A: the author must choose; B: none | D-0398 does not say |
| 7 | Chart types: a flat list, or under the question headings? | A: flat (DS). B: under the headings (US) | DS; US | B: no confusion between "family" and "chart type" | B: one place depends on the other | none |
| 8 | Which question words, and are 5 or 6 questions enough? ("grid"; "Distribution" against "spread") | see section 4 | DS, ST, US as listed | plain words | a word with no example | none |
| 9 | Is the geom filter collapsed for a first-time user? | A: shown. B: collapsed under "Advanced" (US) | US for B | less noise | a plotnine user must open it | D-0398 (kept, only the place changes) |

## 9. Not verified (the three lists merged)

- The pictures: DS read recipes, not images; ST and US saw none for this review. The verification already says which pictures are wrong (18).
- The data shape of bubble, connected_scatter, scatter_smooth and tile_simple: reasoned from names and row counts (DS). An author must confirm. The user viewpoint did not read the data files.
- The three derivation numbers (17 differ, 12 differ, 17 or 22 agree) come from crude scripts. A better rule changes them. They are not proof that the typed tags are wrong, because the typed meaning is undefined.
- The statistician's thresholds 10 / 30 / 100: not looked up, not tested on these data.
- The named classifications (Data-to-Viz, FT Visual Vocabulary, grammar of graphics): not looked up (ST).
- "3 of 34 recipes mention wrangling" (ST): a grep for words in the texts, crude. DS counted the `tier1` steps and got zero. The two are different measurements.
- That plotnine stacks a `geom_bar` with a fill colour by default: not run (DS).
- The check order claim (the "is it a list" test before the "is it in the list" test): taken from the draft; the membership test itself I read at `recipe_check.py:1259-1260`.
- How the "either" rule works on the new axes: the filter loop reads `FILTER_AXES`; a new axis needs an entry in that tuple (READ).
- The code that writes `gallery_index.json`, other places that read the six axes (docs, tests, the conversion script), and the look of the filter panel with 24 or more words: not read.
- The Gallery screen: nobody looked at it. The user viewpoint ran nothing and read no recipe or code.
- The statistician is a role played by the data scientist agent. Its agreement with the data scientist is therefore weaker evidence than three independent people.
