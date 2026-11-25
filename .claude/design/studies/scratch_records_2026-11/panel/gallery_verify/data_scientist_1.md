# Gallery verification, data scientist 1 (17 examples, area_simple to histogram_simple)

Labels: RUN = executed; READ = file read; SEEN = looked at the picture; REASONED = not tested.
Scratch: tmpAI/panel/gallery_verify/data_scientist_1_scratch/ (prof.py, bins.py, dens.py, pics/, cs/, cs_shuffled.png).
Nothing in the repository was changed. `git status` shows only a ledger change that is not mine.

## General (RUN)
- Every one of the 17 pictures, drawn by `assets/scripts/gallery_previews.py --out <scratch>` (app path, `render_example`), is "identical" to the stored `preview_plot.png`. So what I describe is what the Gallery shows.
- No example has missing values, whitespace in text, or a duplicated key. Declared types in `input_fields` match what polars reads (all 17 recipes use `steps: []`, so there is no transformation to check; the picture is the raw table).
- Cheatsheet rule (TAXONOMY_CHEATSHEET.md lines 77-80, READ): `any` = summary data; `individual points` n < ~200; `medium+` n >= ~50; `large` n >= ~500. I use it for the sample_size checks.
- Pattern across the examples: "mic_value" in 4 examples (boxplot_simple, boxplot_faceted, histogram_simple, and growth_index in density_simple) is a uniform-looking number 3 to 127, not an MIC (real MIC: 0.06 to 64 in two-fold steps, as in ecdf, freqpoly, beeswarm_sina). Rounding of the same dilution differs between files: 0.12 (beeswarm_sina, freqpoly), 0.125 (ecdf), 0.062 (ecdf).
- Pasted boilerplate on 5 pages: "Visualize categorical patterns and distributions within your scientific datasets." and "This is a basic demonstration of `geom_X` mapping." (bar_simple, boxplot_simple, boxplot_faceted, density_simple, histogram_simple), and "Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap)" (heatmap_correlation).

---
## 1. area_simple - MINOR
- Data (RUN): 7 rows; year Int64 2018-2024, resistance_pct 51.6-63.0; no NA, no duplicate year; rows in year order.
- Recipe (READ): year Int64 is a number used as x on a continuous axis: fine for an area. geom_area sorts by x, so order is not a problem.
- Plot (SEEN): blue area from 0 to the line, axis 0-60, ticks 2018, 2020, 2022, 2024 only. Honest baseline 0. Same as stored.
- Tags: family Evolution, pattern 1 Year 1 Numeric, show trend: right. difficulty Simple: right. sample_size `medium+` is wrong: 7 summary rows is `any` (cheatsheet: medium+ is n >= 50). First layer geom_area: matches.
- Text: "Emphasises the cumulative magnitude of a metric over time" and "Growing filled area = accumulating resistance burden": not true for this data. The y value is a yearly percentage (a rate), not a running total; the area under a rate has no unit meaning. "Cumulative cases" or "total resistance burden" would need a count. A reader is told the area means something it does not.
- Suggestion: change sample_size to `any`. Rewrite the Interpretation: the area is the same information as the line; the height is a yearly resistance percentage; the area under a percentage is not a total. Keep the 0 baseline. Picture unchanged. Optionally add ticks for every year (7 points).

## 2. bar_grouped - MINOR (data question)
- Data (RUN): 15 rows, 5 species x 3 drug classes, complete, no NA, no duplicate (species, drug_class). resistance_rate 0.0-42.1.
- Recipe (READ): types fit; mapping x species, y resistance_rate, fill drug_class; geom_col with dodge.
- Plot (SEEN): 5 clusters of up to 3 bars. E. faecalis has NO cephalosporin bar: the value is 0.0 (RUN), drawn as nothing, which a reader reads as "missing". Species and legend are alphabetical (String type), not by value. Legend title is the raw column name `drug_class`. Same as stored.
- Science: E. faecalis cephalosporin resistance 0.0 % is biologically false (enterococci are intrinsically resistant to cephalosporins). A microbiologist in a demo will see it. The picture invites "no resistance". REASONED/external knowledge, not a repository fact.
- Tags: family Ranking and show ranking do not fit: bars are not ordered by value; the aim is to compare drug classes within species (family Comparison). The allowed `show` words have no "comparison"; the owner may need to choose (REASONED). pattern 1 Numeric 2 Categorical: right. sample_size any: right.
- Text (READ): "Useful for spotting which drug-species combinations have highest resistance": true. Column types "Categorical" in the page vs `String` in the recipe: consistent in meaning.
- Suggestion: replace the 0.0 by a plausible value (or remove that row and say a missing combination shows as a gap); family to Comparison; label legend "Drug class"; if ranking is wanted, order species by value (Enum with categories in that order, a user choice).

## 3. bar_horizontal - MINOR (the example does not do what it says; needs a new picture)
- Data (RUN): 5 rows, one per class, mean_resistance 31.9-62.9; file is sorted ascending by value (Macrolide first, Beta-lactam last). No NA.
- Recipe (READ): x amr_class (String), y mean_resistance, geom_col + coord_flip.
- Plot (SEEN): bars are NOT in value order. From bottom: Aminoglycoside, Beta-lactam, Fluoroquinolone, Macrolide, Tetracycline = alphabetical (String sorts alphabetically; the file order is ignored). So the pre-sorted file has no effect, and the picture is no ranking. Value axis ticks are rotated 45 degrees (axis text of the flipped axis), odd for a number axis.
- Tags: family Ranking, show ranking, title "Rank categories by a numeric value": contradicted by the picture.
- Text: "Pre-sort data by value before plotting, or use `reorder(amr_class, mean_resistance)`": the first advice does not work (RUN/SEEN: the file is pre-sorted and the picture is alphabetical). The `reorder` call: I did not find or test such a function in the recipe format; NOT verified. "Longest bar = highest resistance - immediate visual ranking": the longest bar is second from the bottom, not at an end, so the ranking is not immediate. "Consider geom_vline threshold": fine.
- Suggestion: either type amr_class as Enum with `categories` in value order (user's choice, explained in the page) and redraw, or drop the ranking claim. New picture needed.

## 4. bar_simple - MINOR (F1 confirmed, more precise)
- Data (RUN): 100 rows, unique id, species 4 (23/25/29/23), amr_class 4, value Float 0.99-125.5. No NA.
- Recipe (READ): mapping fill amr_class, x species, geom_bar (counts). `value` and `id` are declared but unused.
- Plot (SEEN): stacked counts per species; y axis says "count", x "species", legend title "amr_class" (raw names). Bar totals 23, 25, 29, 23 = 100 (RUN, agree with the picture). Segments above the bottom one have no common baseline, so they cannot be compared across species. Same as stored.
- F1: confirmed. Tag `1 Numeric, 1 Categorical` is wrong: no number is plotted (counting rows); it is 2 Categorical (species, amr_class). More precise: also `Ranking`/`ranking` is wrong: bars are alphabetical, nothing is ranked; closer is Part-to-Whole (stacked composition) or Comparison.
- Text: "Essential for comparing counts across categories ... 'Staple' for categorical distribution": about counts: ok. Page never says the bars are stacked or that rows are counted, nor that `value` is not used.
- Suggestion: pattern to a two-categorical pattern (the allowed list has `1 Numeric, 2 Categorical` only; none with 0 numeric: the vocabulary has no word; flag to owner); remove the `value` column or say it is unused; page: "one bar per species, height = number of records, split by drug class"; give y and legend labels. No new picture needed unless labels are changed.

## 5. beeswarm_sina - WRONG (hidden counts); needs a new picture
- Data (RUN): 100 rows, 4 species (30/20/25/25). Only 18 distinct (species, value) pairs: every value occurs exactly 5 times (10 for two). All 100 rows are duplicate rows (no key) - normal for MIC but here artificial. Values are two-fold dilutions 0.12-16.
- Recipe (READ): types fit; x species, y mic_value, color species; geom_sina with random_state 0 (reproducible).
- Plot (SEEN): points at identical y and almost identical x overlap. E. faecalis shows 4 dots for 20 points: the dot at 16 is 5 observations (25 % of the species) but looks like a single outlier. Y axis is linear 0-16: all the information is in 0-4, the 16 compresses everything. Legend duplicates the x axis. Same as stored.
- Text: "Each dot is one observation" - false here (5 dots are on top of each other). "The spread width reflects density - denser regions widen" - the spread is small and the dots do not widen visibly.
- Tags: Distribution, distribution, `individual points`, 1 Numeric 1 Categorical: right for the intent; the picture does not deliver "individual points".
- Suggestion: either more varied, non-tied values (so dots separate), or log2 y axis, or a smaller alpha plus wider sina; page: say ties (MIC values are discrete) hide points and what to do. Remove the colour legend (redundant). Use 0.125 not 0.12.

## 6. boxplot_faceted - MINOR (small cells; data not MIC)
- Data (RUN): 100 rows, species x amr_class cells with n = 2 to 11 (S. aureus Tetracycline n=2, S. aureus Beta-lactam n=4, E. coli Fluoroquinolone n=3). mic_value 3.6-126.5, continuous (100 distinct values).
- Recipe (READ): x amr_class, fill amr_class, y mic_value, facet_wrap species ncol 2: columns exist, types fit.
- Plot (SEEN): 4 panels (E. coli, K. pneumoniae, P. aeruginosa, S. aureus), 4 boxes each, shared y axis, x labels only on the bottom row, outlier dots 5 in all. Fill repeats the x axis (legend redundant). Boxes from n=2 or 3 look like boxes from n=30; nothing shows n. Y label is raw `mic_value`. Same as stored.
- Tags: Comparison, `1 Numeric, 2 Categorical (Faceted)`, Intermediate, distribution: right. sample_size `medium+`: total 100 but cells 2-11; by cell it is not medium+. First layer geom_boxplot: right.
- Text: "Breaking down distribution by species using facets": right. "basic demonstration of `geom_boxplot` mapping": the example also uses facet_wrap; pasted. Interpretation boilerplate does not fit.
- Suggestion: bigger data (>= 10 per cell) or say n per box in the page; rename column/range (values up to 127 are not an MIC); remove the pasted sentence.

## 7. boxplot_simple - MINOR (F2 confirmed; plus small cells)
- Data (RUN): same shape as boxplot_faceted: 100 rows; cells n = 2 (P. aeruginosa Aminoglycoside, K. pneumoniae Tetracycline) to 14; mic_value 4.3-127.4 (F2: confirmed, 127, not an MIC scale; values continuous).
- Recipe (READ): x amr_class, fill species, y mic_value.
- Plot (SEEN): 4 clusters of 4 boxes (dodge), box width differs from box to box without any legend for width (not explained by n: n=2 box is wide), 2 outlier dots. Legend `species`. Same as stored.
- F2: confirmed: tag `1 Categorical` wrong, the plot uses two categoricals (amr_class, species). Precisely: `1 Numeric, 2 Categorical` is the allowed word.
- Tags: sample_size medium+ (cells 2-14: boxes on 2 values draw a "box"); Simple: ok.
- Text: "The 'Quality Control' plot" - not true of this example (a boxplot summarises a measurement; "QC" is not what is shown); Interpretations boilerplate.
- Suggestion: pattern to `1 Numeric, 2 Categorical`; data with >= 8 per cell and a real MIC range, or a note on n; page: say what box, line and dots mean.

## 8. bubble - WRONG (F3 confirmed, more precise)
- Data (RUN): 5 rows, one per species; sample_size 106-367 (Int64); mean_resistance 32.7-63.3; pct_resistant 0.26-0.68: a FRACTION named percent (F3 confirmed).
- Recipe (READ): x sample_size, y mean_resistance, size pct_resistant, color species; scale_size name '% Resistant'.
- Plot (SEEN): 5 bubbles; size legend title "% Resistant" with entries 0.3, 0.4, 0.5, 0.6 (reads as 0.3 %); the y axis says "Mean Resistance (%)" with 33-63 for the same species. Two columns describe resistance with different units and unexplained difference (P. aeruginosa: 63.3 and 0.68). The size ties to pct_resistant but E. faecalis (lowest) is tiny and bottom right. Same as stored.
- More precise than F3: besides the unit, the x axis is sample size (collection effort). Plotting resistance against the number of isolates invites a "relationship"; with 5 points none can be judged; the page says "Position reveals correlation between x and y".
- Tags: Correlation/relationship with 5 species: sample_size `any` ok; pattern `2 Numeric, 1 Categorical`: actually 3 numeric + 1 categorical; the allowed list has no such word.
- Text: "(e.g. sample size, % resistant, confidence)" as the THIRD quantity: here sample size is x. "Requires pre-aggregation": ok.
- Suggestion: data pct_resistant in percent (26-68) or label "Fraction resistant"; drop or explain mean_resistance vs pct_resistant; put sample size as bubble size (its usual role) and a meaningful x; remove "correlation" text. New picture.

## 9. connected_scatter - MINOR (order silently depends on the file; no time cue)
- Data (RUN): 16 rows, 2 classes x 8 years (2015-2022), complete; rows are in year order inside each class; resistance 5.2-21.2, consumption 1.12-2.74 (plausible).
- Recipe (READ): geom_path, group drug_class, no sort step, `arrow: null`.
- RUN test: I shuffled the rows into a copy (cs/), same recipe: the path zigzags (cs_shuffled.png). So the path follows the ROW ORDER of the file, not `year`. The page says "year: Year (determines path order)" - FALSE; the data file order does. Order is not in the recipe (a silent dependency).
- Plot (SEEN): two coloured paths with points; no year labels, no arrows, so a reader cannot tell which end is 2015; the title says "(Connected by Year)" but year is shown nowhere. The Fluoroquinolone path has a back-step (2020), looks like a zigzag. Legend raw `drug_class`. Same as stored.
- Tags: pattern `2 Numeric` omits drug_class (categorical) and year (path order): should be `2 Numeric, 1 Categorical`. show trend, Correlation: acceptable.
- Text: "Moving right = increasing resistance" ok. "Use geom_path (not geom_line) to ensure correct temporal ordering": geom_path does NOT order in time, it orders as the rows are (RUN above); the sentence is the wrong way round.
- Suggestion: add an explicit sort by drug_class, year in the recipe; label the points with the year or add arrows; rewrite the sentence on geom_path; pattern to `2 Numeric, 1 Categorical`. New picture.

## 10. density_2d_bin - WRONG (F4 confirmed; more); needs a new picture
- Data (RUN): 60 rows, two columns of integer log2 MIC values (-3 to 5 and -3 to 6); 38 rows are duplicates of another row; 35 distinct cells, max 4 per cell. Correlation 0.75 (so the "diagonal" claim is true).
- Recipe (READ): geom_bin_2d bins 15, x log_mic_drug_a, y log_mic_drug_b.
- Plot (SEEN, RUN of the bins in bins.py): 35 rectangles, colour = count: yellow 4, green 3, blue 2, dark purple 1. F4 confirmed: "Dark bins = many isolates" is the opposite (dark purple = 1). More: 15 bins of width 0.533 (x) and 0.6 (y) do not align with the integer values; the rectangle for value x=0 spans 0 to 0.53, for y=0 spans -0.6 to 0: the data value sits on the EDGE (the edge is -8.9e-16, a floating point accident, RUN). So a bin is drawn to the right/below the value it counts. Rectangles are not square and some touch, some leave gaps. Total counts 60 = 60 rows (RUN), so no row is lost.
- Tags: sample_size `large` is wrong (60 rows; cheatsheet: large benefits from n >= 500); the name "2D Bin Density": it is a 2D histogram (counts), not a smoothed density (consistent with the draft).
- Text: "Handles overplotting better than raw scatter for large datasets" fine in general, not true of 60 rows with 35 cells. "isolates resistant to one drug tend to be resistant to the other": ok for the diagonal.
- Suggestion: bin width 1 centred on integers (or a tile/count plot of the 35 cells), fix legend text to "yellow = 4 isolates, dark = 1", sample_size to `medium+`, rename to 2D histogram (owner). New picture.

## 11. density_simple - WRONG (one species is invisible); needs a new picture
- Data (RUN): 100 rows, 4 species (E. coli 23, K. pneumoniae 20, P. aeruginosa 28, S. aureus 29); growth_index 1.5-127.1, close to uniform; no NA.
- Recipe (READ): geom_density, fill species, params {} (no alpha, no position).
- Plot (SEEN + RUN in dens.py): the four filled curves are opaque and overlap. E. coli (red) cannot be seen at all: in dens.py its density is below the maximum of the other curves at 100 % of the x values. The legend lists E. coli, the plot does not show it. Y label raw "density".
- Tags: pattern `1 Numeric` wrong: fill by species makes it `1 Numeric, 1 Categorical`. sample_size medium+: 100 total, 20-29 per curve: borderline.
- Text: "The 'Flavor Profile'": decoration; "Shows the smooth distribution of a single numeric variable" - it shows four, one hidden; interpretations pasted.
- Suggestion: alpha 0.4 (recipe param) or facets; pattern fix; page text about reading overlapping densities. New picture.

## 12. dumbbell - MINOR (F5 confirmed, more precise)
- Data (RUN): 12 rows, 6 species x 2 years (2015, 2023), complete; resistance 8.5-47.6; year_label Int64; all species increase.
- Recipe (READ): geom_line (grey, size 1.5) then geom_point; color year_label; group species.
- Plot (SEEN): 6 dumbbells, dark purple 2015 and yellow 2023, grey bar. F5 confirmed: legend is a continuous colour bar with ticks 2015, 2017, 2019, 2021, 2023 although only two years exist. More precise: the page table says `year_label` is `Categorical`, the recipe says Int64, which causes the continuous scale: the recipe contradicts its own page (REASONED: typing it as String would give a two-entry legend; not run). Species in alphabetical order bottom to top, not by size of change. The title "(2015 vs 2023)" is typed text, not derived. Same as stored.
- Tags: pattern `1 Numeric, 2 Categorical`: ok (year is the second category); Comparison/change: right. first layer geom_line: matches the recipe, readers see points. sample_size any: ok.
- Text: "Longer = bigger change", "consistent rightward shift = universal increase": right for this data. Link text "R Graph Gallery - Dumbbell Chart" points to `lollipop-plot.html` (not verified externally).
- Suggestion: change year_label type to match the page (String) or Enum; give legend title "Year"; optionally sort species by change (user choice). New picture.

## 13. ecdf - MINOR
- Data (RUN): 30 rows, 3 species x 10; 8 distinct dilution values per species, 14 rows duplicate (ties); mic_value 0.062-64.
- Recipe (READ): stat_ecdf, x mic_value, color species.
- Plot (SEEN): three step curves on a LINEAR x axis -3 to 67: the doubling dilutions are squeezed into 0-4, the curves of E. coli and S. aureus overlap for x < 1 and the red line is partly hidden under the blue one. Curves start at 0 on the left of the data (flat before the first value). Y "Cumulative Proportion" 0-1. Same as stored.
- Tags: sample_size `medium+` wrong: 10 per curve (30 total); reading proportions at steps of 0.1. Others right.
- Text: "The step at each x value represents one observation": wrong with ties (the step height is the proportion at that value; the E. coli steps at 0.25, 0.5 are 2 of 10). "allows reading off %S, %I, %R directly from breakpoints": no breakpoint is drawn, no x log axis. "Read vertically at any MIC breakpoint to get cumulative % susceptible": true only for MIC <= S breakpoint.
- Suggestion: log2 x axis (a recipe layer or a log2 step: check what the format offers), 30+ per species, sample_size to `individual points` or `any`; correct the step sentence; optionally a vertical line at a breakpoint.

## 14. error_bar - MINOR
- Data (RUN): 8 rows, one per species, mean_mic 0.62-4.12, ci_low/ci_high symmetric around the mean (checked on E. coli, S. aureus), always ci_low < mean < ci_high. No NA.
- Recipe (READ): geom_pointrange, x species, y mean_mic, ymin ci_low, ymax ci_high, color species; label "Mean MIC (log2)".
- Plot (SEEN): 8 dots with vertical lines, alphabetical order, y axis 0.3-5, legend duplicates the x axis. Same as stored.
- The title says "95% Confidence Interval": nothing in the data or recipe states the level or n (the table holds only the bounds). The claim is asserted, not derived (page: "confidence intervals or SD"). The y label says log2 but the column is named mean_mic.
- Tags: Comparison, uncertainty, any, `1 Numeric, 1 Categorical`: three numeric columns are used; acceptable.
- Text: "Overlapping bars suggest groups may not differ significantly": a common misreading (overlap of two 95 % CIs does not mean non-significance); this is a statistical claim the statistician viewpoint should rule on. "use a T3 `summarize` step": "T3" is not explained here (only qq_plot uses it too); I could not verify that a `summarize` step exists by that name here.
- Suggestion: state "95 % CI of the mean log2 MIC, n = ..." in the page or give n in the data; drop the "non-significant" sentence or replace it; remove the colour legend; explain T3 or name the step as in the recipe spec.

## 15. freqpoly - WRONG (recipe does not fit data); needs a new picture
- Data (RUN): 45 rows, 3 species x 15; raw MIC values 0.12-64 in doubling steps (10 distinct values); 42 rows are ties.
- Recipe (READ): geom_freqpoly, binwidth 0.5, x mic_value.
- Plot (SEEN): a flat zero line with thin spikes at 0.25, 1, 2, 4, 8, 16, 32, 64 (sharp peaks of 1-5). The x axis is 0-67 linear. The page says binwidth 0.5 is "for log2 MIC steps": the data are NOT log2 (raw MIC), so 0.5 is 1/128 of the range and every value is an isolated spike. A reader sees comb-like noise and K. pneumoniae spikes at 32 and 64 as separate peaks. Same as stored.
- Tags: sample_size `medium+`: 45 total, 15 per curve (< 50). Simple: ok.
- Text: "Peaks indicate the most common values": the spikes are bins with 2-3 isolates, no mode. "Connects bin midpoints": fine. "Choose binwidth to match the scale of the data (e.g., 0.5 for log2 MIC steps)": the example does the opposite.
- Suggestion: data in log2 (or a step computing log2(mic_value)) and binwidth 1; more rows (>= 50 per species); correct the page. New picture.

## 16. heatmap_correlation - WRONG (F6 confirmed, more); needs a new picture
- Data (RUN): 16 rows = a 4x4 long table, id is the constant "CORR" for all rows (not a key); correlation -0.9 to 0.85.
- F6 confirmed: diagonal is -0.5, -0.8, -0.1, -0.9 (a correlation matrix has 1); not symmetric (A,B = -0.3 but B,A = 0.85; A,D = -0.11 but D,A = -0.9). Not a valid correlation matrix. The recipe computes nothing: it only draws the numbers given.
- Recipe (READ): geom_tile + geom_text (white, size 3) + scale_fill_gradient2 (blue-white-red, midpoint 0).
- Plot (SEEN): 4x4 tiles. The number labels are white, about 5 pixels high: not legible, and invisible on the pale tiles. The scale limits follow the data (-0.9 to 0.85), not -1 to 1. Axes are the raw names var1/var2; MIC_A is at the bottom.
- Tags: pattern `3 Numeric (Matrix)`: two categorical (var1, var2) and one numeric. Advanced: the recipe is the simplest tile.
- Text: "advanced layer stacking and coordinate manipulation": false (tile + text); "Look for peaks (Ridgeline), magnitudes (Lollipop), or clusters (Heatmap)": pasted from other examples; "ADR-002" reference: not verified.
- Suggestion: real correlation data (symmetric, diagonal 1, within -1..1) or a different example name (owner decision on "Matrix Heatmap"); readable labels (dark text, larger, rounded); fixed scale -1..1; page text rewritten. New picture.

## 17. histogram_simple - MINOR
- Data (RUN): 100 rows, unique id, mic_value 6.8-126.9 continuous (not an MIC), amr_class 4 (19/34/24/23). No NA.
- Recipe (READ): geom_histogram bins 30, x mic_value, fill amr_class.
- Plot (SEEN): 30 stacked bars (bin width about 4), stacking by amr_class with Tetracycline at the bottom; heights 1-7; gaps where a bin is empty. Y label count; x raw. Same as stored.
- Tags: pattern `1 Numeric` wrong (fill by amr_class makes it `1 Numeric, 1 Categorical`). sample_size medium+ (100): right. show frequency: right.
- Text: "The 'Inventory' view" (decorative); the page does not say that bars are stacked by class, nor how many bins; interpretation boilerplate (does not fit).
- Suggestion: fix the pattern or drop the fill; rename column or use real MIC data; page: "bars stacked by class, 30 bins, count of isolates".

---
## Check of earlier flags (my examples)
| flag | example | verdict | detail |
|---|---|---|---|
| F1 | bar_simple | confirmed, more precise | counts per species, `value` unused; also Ranking is wrong (alphabetical) |
| F2 | boxplot_simple | confirmed, more precise | 2 categoricals; mic_value up to 127.4; cells n = 2 to 14 |
| F3 | bubble | confirmed, more precise | legend 0.3-0.6 under "%"; y in % for the same species; x is the sample size, 5 points |
| F4 | density_2d_bin | confirmed, more precise | dark = 1, yellow = 4; also bins offset from the integer values; sample_size large with 60 rows |
| F5 | dumbbell | confirmed, more precise | cause: year_label Int64 while page says Categorical |
| F6 | heatmap_correlation | confirmed, more precise | also not symmetric (A,B -0.3 / B,A 0.85); labels unreadable |

## Summary table
| example | verdict | the problems in a few words | needs a new picture |
|---|---|---|---|
| area_simple | MINOR | "cumulative/area = burden" text wrong for a rate; sample_size medium+ with 7 rows | no |
| bar_grouped | MINOR | E. faecalis cephalosporin 0.0 shows as a gap and is biologically false; Ranking tag, unsorted | yes if the data value changes |
| bar_horizontal | MINOR | not sorted although the example is "ranking"; file order is ignored; page advice does not work | yes |
| bar_simple | MINOR | pattern tag wrong (F1); Ranking wrong; `value` unused; raw labels | no |
| beeswarm_sina | WRONG | 5 identical points stacked: the 16 outlier is 25 % of the species; "each dot is one observation" false; linear MIC axis | yes |
| boxplot_faceted | MINOR | boxes from n = 2 to 4; MIC up to 126; pasted text; redundant fill | no (yes if data change) |
| boxplot_simple | MINOR | F2: tag says 1 categorical, uses 2; n = 2 boxes; MIC to 127; "QC" text | no (yes if data change) |
| bubble | WRONG | F3: fractions labelled %; x is sample size; 5 points "correlation" | yes |
| connected_scatter | MINOR | path follows file order, not year (RUN shuffle); no time cue; page sentence wrong | yes |
| density_2d_bin | WRONG | page says dark = many (opposite); bins offset from integer values; large with 60 rows | yes |
| density_simple | WRONG | E. coli curve completely hidden (opaque fill); pattern tag 1 Numeric | yes |
| dumbbell | MINOR | F5: continuous year legend (type Int64 vs page "Categorical") | yes |
| ecdf | MINOR | linear MIC axis; "step = one observation" wrong; medium+ with n = 10 per curve | optional |
| error_bar | MINOR | "95 %" not in the data; overlap sentence; T3 unexplained | no |
| freqpoly | WRONG | binwidth 0.5 on raw MIC: comb of spikes; "log2" advice contradicted; 15 per curve | yes |
| heatmap_correlation | WRONG | not a correlation matrix (diagonal not 1, asymmetric); labels unreadable; false "advanced" text | yes |
| histogram_simple | MINOR | pattern 1 Numeric but fill by class; MIC-like values to 127; pasted text | no |

## Fit to show in a demo today
- Fit as they are: area_simple (after fixing the text it teaches the right thing; the picture is honest), bar_simple, error_bar, histogram_simple, dumbbell (the legend is awkward but the message is right), ecdf (works; say it is a linear axis).
- Fit with caution (a scientist will ask): bar_grouped (E. faecalis 0.0), boxplot_simple and boxplot_faceted (n = 2 boxes; "MIC" up to 127), connected_scatter (do not say year orders the path), bar_horizontal (do not call it a ranking).
- Not fit: beeswarm_sina, bubble, density_2d_bin, density_simple, freqpoly, heatmap_correlation.

## Not verified
- I did not look at the Gallery panel in the running app, only the pictures drawn by `render_example` (identical to the stored ones).
- `reorder(...)` in a mapping, a `summarize` step called T3, the effect of typing year_label as String, and the external links (r-graph-gallery pages, ADR-002 text) were not checked.
- The biology of E. faecalis and the overlap-of-CI rule are my own domain knowledge (not from the repository).
- Box width differences in boxplot_simple were seen, not explained.
- Statistics sentences (95 % CI, overlap, significance) are for the statistician viewpoint to confirm.

---
## TAG TABLE (D-0402): pattern, sample_size, difficulty
Sources: recipes READ (mapping, layers, input_fields), group sizes RUN (prof.py and the group counts above), rules READ in TAXONOMY_CHEATSHEET.md lines 46-51 (difficulty: Simple = single geom, direct mapping, no wrangling; Intermediate = multiple geoms or position adjustments, may need pre-aggregation; Advanced = non-trivial wrangling, derived columns, specialised geoms) and 77-80 (sample_size). Mapped columns are counted as the picture uses them; "N" = numeric, "C" = categorical, "Y" = year (Int64 used as a number).

| example | tag | value as written | value found | evidence |
|---|---|---|---|---|
| area_simple | pattern | 1 Year, 1 Numeric | same | x year (Int64, used as a number), y resistance_pct (Float64): 1 Y + 1 N. |
| area_simple | sample_size | medium+ | any | 7 rows, one per year, summary data; medium+ means n >= ~50. |
| area_simple | difficulty | Simple | Intermediate by the rule | 2 geom layers (geom_area, geom_line); rule says Simple = single geom. |
| bar_grouped | pattern | 1 Numeric, 2 Categorical | same | x species (String), fill drug_class (String), y resistance_rate (Float64). |
| bar_grouped | sample_size | any | any | 15 rows; 3 per species, 5 per drug class, 1 per cell (summary values). |
| bar_grouped | difficulty | Intermediate | Intermediate | 1 geom + position dodge (a position adjustment). |
| bar_horizontal | pattern | 1 Numeric, 1 Categorical | same | x amr_class (String), y mean_resistance; coord_flip only turns it. |
| bar_horizontal | sample_size | any | any | 5 rows, 1 per class. |
| bar_horizontal | difficulty | Simple | Simple | 1 geom (geom_col) + coord_flip (not a geom); borderline, no position adjustment. |
| bar_simple | pattern | 1 Numeric, 1 Categorical | 2 Categorical, count only (no numeric mapped) | x species, fill amr_class, no y; geom_bar counts rows; `value` and `id` unused. The vocabulary has no word for "0 Numeric, 2 Categorical". |
| bar_simple | sample_size | any | medium+ (rows are isolates, not summaries) | 100 rows; species 23-29 per bar, amr_class 22-28; segments (cells) 2-13 (counts read from the picture). |
| bar_simple | difficulty | Simple | Simple | 1 geom; the count and the stack are the defaults of geom_bar. |
| beeswarm_sina | pattern | 1 Numeric, 1 Categorical | same | x species, color species (same column twice), y mic_value: 1 N + 1 C. |
| beeswarm_sina | sample_size | individual points | individual points, but 100 rows show as ~18 dots (ties) | 100 rows; per species min 20, max 30; 18 distinct (species, value) pairs. |
| beeswarm_sina | difficulty | Intermediate | Simple by the rule, Advanced if "specialised geom" counts | 1 geom (geom_sina), direct mapping; sina is a specialised geom (rule line 51). Unclear: the rule contradicts itself here. |
| boxplot_faceted | pattern | 1 Numeric, 2 Categorical (Faceted) | same | x amr_class, fill amr_class (same column), facet species, y mic_value: 1 N + 2 C. |
| boxplot_faceted | sample_size | medium+ | medium+ for 100 rows, but cells are not | 100 rows; per species 18-29; per box (species x class) min 2, max 11. |
| boxplot_faceted | difficulty | Intermediate | Intermediate | 1 geom + facet_wrap. |
| boxplot_simple | pattern | 1 Numeric, 1 Categorical | 1 Numeric, 2 Categorical | x amr_class, fill species, y mic_value: 2 C. |
| boxplot_simple | sample_size | medium+ | medium+ for 100 rows, but boxes are not | 100 rows; per amr_class 20-30; per species 14-35; per box min 2, max 14. |
| boxplot_simple | difficulty | Simple | Simple (dodge is the default) | 1 geom, direct mapping. |
| bubble | pattern | 2 Numeric, 1 Categorical | 3 Numeric, 1 Categorical (no such word) | x sample_size (Int64), y mean_resistance, size pct_resistant, color species: 3 N + 1 C. |
| bubble | sample_size | any | any | 5 rows, 1 per species (summary); too few for "relationship". |
| bubble | difficulty | Intermediate | Intermediate | 1 geom + size scale, 4 aesthetics. |
| connected_scatter | pattern | 2 Numeric | 2 Numeric, 1 Categorical (+ implicit year order) | x resistance_rate, y consumption_ddd, group and color drug_class (String): 2 N + 1 C; year (Int64) not mapped, only the row order. Written word omits the categorical. |
| connected_scatter | sample_size | any | any | 16 rows; 8 per class (2015-2022); summary values. |
| connected_scatter | difficulty | Intermediate | Intermediate | 2 geoms (geom_path, geom_point). |
| density_2d_bin | pattern | 2 Numeric | same | x log_mic_drug_a, y log_mic_drug_b: 2 N, no categorical. |
| density_2d_bin | sample_size | large | medium+ (60 rows) | 60 rows, one group; 35 occupied bins, 1-4 per bin; large needs ~500. |
| density_2d_bin | difficulty | Intermediate | Simple by the rule | 1 geom (geom_bin_2d), direct mapping, no wrangling. |
| density_simple | pattern | 1 Numeric | 1 Numeric, 1 Categorical | x growth_index, fill species. |
| density_simple | sample_size | medium+ | medium+ in total; borderline per curve | 100 rows; per species min 20, max 29 (cheatsheet ~50). |
| density_simple | difficulty | Simple | Simple | 1 geom. |
| dumbbell | pattern | 1 Numeric, 2 Categorical | 1 Numeric, 2 Categorical by intent; as typed: 2 Numeric + 1 Categorical | x resistance_rate, y species, color year_label (Int64, treated as a number by the picture; two time points). The type, not the word, is the problem. |
| dumbbell | sample_size | any | any | 12 rows; 2 per species (one per time point). |
| dumbbell | difficulty | Intermediate | Intermediate | 2 geoms (geom_line, geom_point). |
| ecdf | pattern | 1 Numeric, 1 Categorical | same | x mic_value, color species; stat_ecdf makes y. |
| ecdf | sample_size | medium+ | any or individual points | 30 rows; 10 per species (min 10, max 10); ~50 asked for medium+. |
| ecdf | difficulty | Intermediate | Simple by the rule | 1 stat layer, direct mapping, no wrangling. |
| error_bar | pattern | 1 Numeric, 1 Categorical | 3 Numeric, 1 Categorical (no such word) | x species, color species, y mean_mic, ymin ci_low, ymax ci_high: 3 N + 1 C. |
| error_bar | sample_size | any | any | 8 rows, 1 per species (summary); n behind the means not in the data. |
| error_bar | difficulty | Intermediate | Simple by the geometry; Intermediate only because the data are pre-aggregated | 1 geom (geom_pointrange); rule line 50 mentions "may need pre-aggregation". |
| freqpoly | pattern | 1 Numeric, 1 Categorical | same | x mic_value, color species. |
| freqpoly | sample_size | medium+ | any / individual points (45 rows) | 45 rows; 15 per species (min 15, max 15); medium+ is ~50. |
| freqpoly | difficulty | Simple | Simple | 1 geom; but binwidth must fit the data (see item 15). |
| heatmap_correlation | pattern | 3 Numeric (Matrix) | 2 Categorical, 1 Numeric | x var1 (String), y var2 (String), fill and label correlation (Float64): 1 N + 2 C. The vocabulary has `3 Numeric (Matrix)` only for a numeric matrix. |
| heatmap_correlation | sample_size | any | any | 16 rows, one per pair (summary). |
| heatmap_correlation | difficulty | Advanced | Intermediate | 2 geoms (geom_tile, geom_text) + a fill scale; no derived column, no wrangling (`steps: []`, nothing computed). |
| histogram_simple | pattern | 1 Numeric | 1 Numeric, 1 Categorical | x mic_value, fill amr_class. |
| histogram_simple | sample_size | medium+ | medium+ in total; borderline per class | 100 rows; per class min 19, max 34 (cheatsheet ~50). |
| histogram_simple | difficulty | Simple | Simple (stack is the default) | 1 geom, bins 30. |

Not counted as a date: no example maps a date column. Year (Int64) is used as a number on x in area_simple, and as a colour number in dumbbell (the cause of F5); in connected_scatter year is not mapped at all.
