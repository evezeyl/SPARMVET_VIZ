# Axis text and the automatic adjustment: facts for the panel (question 13)

Trial branch `trial/axis-text` (worktree `.claude/worktrees/axis-text`, commits 305b22bb and the one after it). Nothing is merged. No recommendation here.
Labels: verified = run or read at file:line. Line numbers are those of `dev`.
Decisions read: D-0242 ("The automatic axis-text adjustment has no switch of its own; an author overrides it per axis with an `element_text`."), D-0220, D-0258 ("plotnine has a default so if no theme is recorded it falls on plotnine default"), D-0248 (effective_run.yaml holds "the theme as applied per plot"). No decision exists on what wins between the automatic step and `theme_custom`, nor on recording the automatic step. That is reported, as D-0165 asks.

## What I did, in short

- Data: `tmpAI/panel/axis_text/data_10`, `data_100`, `data_500` (main folder). The existing generator `assets/scripts/generate_demo_data.py` makes only 3 tables (metadata, MLST, ResFinder); the recipe needs 11 tables. So: 10 = a seeded pick of 10 of the 42 shipped samples; 100 and 500 = the 42 shipped samples plus copies of whole samples (every row of that sample in every table) under new random 8-digit ids, the last copy partial. Values are copied unchanged, so joins stay consistent. Consequence: counts of non-id categories (sequence types, genes, countries) do NOT grow with the copies; only sample ids and rows do. Script: `scripts/make_data.py`.
- Code: switch `AXIS_TEXT_MODE` in `libs/viz_factory/src/viz_factory/axis_text_trial.py` (new), hooks in `plot_config_resolver.py` and `viz_factory.py`. T today, N none, O1 author wins, O2 automatic wins with a message, O3 author size is a ceiling, O4 "auto" with minimum and maximum. Libraries were imported from the worktree (printed at each run).
- 17 plots x 3 sizes x 6 behaviours at 8 x 5 in, 120 dpi (gallery). 6 plots x 3 x 6 at 10 x 5 in, 96 dpi (my guess of HOME's shape: HOME fixes the height at 480 px, `home_theater.py:793`, 440 px in comparison, and the width follows the screen; 10 in is an assumption). 3 plots x 2 variants x 3 x 6 and the "auto" variant x 3 x 1. 549 pictures, 0 errors. Pictures `pictures/`, sheets `sheets/` (21, listed in `INDEX.md`), measures `measures/measures.tsv`, records `records/*.yaml`, scripts `scripts/`.

## F1. What the automatic step changes today

Where: `compute_optimisation_layer`, `plot_config_resolver.py:429-515`, called always at `:590`. It reads the table the plot is drawn from. verified.

| Axis (the mapped column) | Column kind | Rule (first that matches) | Result |
|---|---|---|---|
| x | text | longest label > 12 characters | size 8, turned 45, hjust right |
| x | text | longest label > 6 | size 9, turned 35, right |
| x | text | more than 12 distinct values | size 8 |
| x | text | more than 6 distinct values | size 9 |
| x | number or date | nothing | nothing |
| y | text | more than 20 values, or longest > 20 | size 7 |
| y | text | more than 12 values, or longest > 12 | size 8 |
| y | number | more than 20 DISTINCT VALUES | size 7 |
| y | number | more than 12 distinct values | size 8 |

Facts that follow from the code and the runs:
- The numeric y rule counts distinct values in the data, not ticks. A y axis with 5 ticks gets size 7 if the data has 21 values. Seen: the numeric counts axis of `qa_*` plots and `phenotype_genome_length_fragmentation` drawn at size 7 (measures.tsv).
- The rule is written on the mapped column (`x`, `y`) and the result goes to the theme target `axis_text_x` / `axis_text_y`. In plotnine with `coord_flip`, `axis_text_x` stays the BOTTOM axis (checked on a small plot: x labels were the numbers, size 14 as set). So in a flipped plot the rule that read the sample ids acts on the bottom axis (the numbers) and the rule that read the numbers acts on the left axis (the sample ids). Seen in `qc_reads_horizontal_barplot` and `qa_fanout_rows_per_sample`: bottom axis (numbers) size 9 turned 35 degrees; left axis (sample ids) size 7 at 100 and 500 samples, 8.8 at 10. The sample id labels got size 7 only because `total_reads` has more than 20 values.
- It sets only: size, rotation, horizontal alignment of the two axis texts. Proof, `scripts/f1_proof.py`, `measures/F1_proof.txt`: for all 17 plots, mode T against mode N: the plot's data frame, the facet, the scales and the labels are identical (17 of 17); the geoms are identical (16 of 17; the 17th differs only by the memory address of a jitter object in my text comparison, not by value); of all themeables of the final theme, the only ones that ever differ are `axis_text_x` (9 plots) and `axis_text_y` (7 plots). So it changes no data, no row, no other plot element.
- It is not a user control: no switch (D-0242). The four old `plot_defaults` keys, among them `optimisation`, are accepted and read by nothing (D-0220).
- Anything else in the app that adjusts a figure from the data: none found. grep over `libs`, `app`, `assets/scripts` for `nunique`, `n_unique`, rotation, `figure_size`: only this function. Figure size is fixed or user-chosen: gallery 8 x 5 in (`gallery_examples.py:35`), export width and height inputs default 8 and 5 (`export_handlers.py:898-899`), HOME 480 px high.

## F2. Who wins today (mode T), size and rotation read from the drawn figure

Test: 40 labels of 15 characters on x, numbers on y, `geom_col`, 8 x 5 in (`scripts/f2_precedence.py`, `measures/F2_T.txt`). x axis shown.

| Case | What the recipe writes | Drawn size | Drawn rotation | Does the user learn anything? |
|---|---|---|---|---|
| a | nothing | 8 | 45 | no (console only, see F3) |
| b | `element_text` axis_text_x size 14 (plot layer) | 14 | 0 | no; the author wins, labels overlap as written |
| c | `theme_custom` axis_text_x size 14 | 8 | 45 | no. 14 becomes 8, turned 45, silently. CONFIRMED |
| d | `theme_bw` with `base_size` 14 (its axis text would be 11.2) | 8 | 45 | no. The size written is replaced |
| e1 | `plot_defaults` layers: `theme_custom` size 14 | 8 | 45 | no |
| e2 | `plot_defaults` layers: `element_text` size 14 | 8 | 45 | no. A default-level `element_text` loses too (tier L2 comes before the automatic tier L3) |
| e3 | `plot_defaults` theme `theme_bw`, no size | 8 | 45 | not applicable |

Why (read in the code, verified): `element_text` is a "batched" component (`plot_config_resolver.py:172`), applied after all other layers (`viz_factory.py:335`). Layers with the same target are merged keeping the last, so a plot-layer `element_text` (L4) replaces the automatic one (L3), and one in `plot_defaults` (L2) is replaced by it. `theme_custom` is a partial theme with no merge key (`:105-140`), it is applied first, and the automatic `element_text` goes on top of it. There is an open strict test for this gap: `libs/viz_factory/tests/test_theme_settings_reach_the_figure.py:245` (`test_a_theme_custom_axis_text_overrides_the_adjustment`, xfail).
Case b also shows: the author's `element_text` with only `size` removes the automatic ROTATION of that axis too (the whole layer is replaced): size 14 stayed unrotated and overlapped.
What the same cases give under each behaviour (`measures/F2_modes.txt`): N: a 8.8/0, b 14, c 14, d 11.2 (plotnine's own). O1: b, c, d, e1, e2 keep what is written (14, 14, 11.2, 14, 14). O2: everything becomes 8, turned 45, and a message is printed for b, c, d, e1, e2. O3: everything 8, turned 45 (14 is a ceiling, 8 is lower). O4: like O1 for written numbers.

## F3. Is the adjustment recorded anywhere today?

Answer: no. verified by reading the writers; I did not build a bundle.
- `effective_run.yaml` (`export_handlers.py:1507-1538`): recipe sha, batch hash, T3 sha, engine fingerprint, versions, source paths, seeds per plot and per layer, translation skipped. No theme, no axis text. (D-0248 adds "the theme as applied per plot"; it is decided and not built in this code.)
- README, `report.qmd`: `grep -i 'axis\|element_text\|rotation' export_handlers.py` on `dev` finds nothing.
- PNG metadata (`export_handlers.py:340-367`): plot id, recipe id and sha, app features, batch hash, decision hash, tier keys, git commit, time. No axis text.
- Processing Issues table (`:1845-1870`): holds only what `on_warning` reports. The automatic step reports nothing. HOME passes `on_warning` (`home_theater.py:521,594`); the export calls `render` without it (`:1214`), so a warning at export time is only printed.
- Console: `viz_factory.py:371` prints `Applied axis text overrides: ['axis_text_x', 'axis_text_y']`. Target names only, no values, and it also prints when the author's own `element_text` is the one applied.
- The exported picture contains the adjusted text; the bundle never says that the app chose it. A reproducibility bundle with the recipe reproduces it only if the data and the code version are the same, because the recipe does not hold the values.

## F4. Option 3 (a maximum): feasible?

- plotnine has no maximum or minimum for text size. verified: `grep -rn 'max_size\|min_size\|size_max\|size_min\|autofit\|auto_size\|shrink'` over `plotnine/themes/` finds nothing; `element_text(size=...)` takes one number. `theme_bw(base_size=14)` gives axis text 11.2 (= 0.8 x base size, seen in mode N case d).
- The app can implement the ceiling itself. Prototype: mode O3 (`axis_text_trial.py`, function `apply`): size = the smaller of the author's size and today's automatic size; rotation applied only when an estimate says the unrotated labels would not fit (0.6 em per character, room from the figure width). It works for `element_text`, `theme_custom` and a named theme `base_size` (read as 0.8 x base): case b, c, d all gave 8, turned 45. Rotation is decided by an ESTIMATE; the drawn figure was measured after (below). A decision by drawing a draft and measuring is possible but costs an extra draw per plot.
- Prototype O4 (author writes `size: auto, size_min, size_max, angle: auto`): largest size in the range that fits at no turn, else 45, else 90, else the minimum.
- Limit found, important: no size or rotation fits many sample ids on an 8 in wide figure. 100 labels at 6 pt turned 90 need about 100 x 7.5 = 750 pt; the room is about 460 pt. About 60 labels is the largest number that can fit at 6 pt on 8 in. Beyond that, text settings alone cannot remove the overlap (see the measures).

## F5. Same recipe, different data size: different axis text? Yes.

Same recipe, mode T, gallery shape (`measures/measures.tsv`, `per_plot_overlap.txt`):
- `mlst_bar`: 10 samples size 9, no turn; 100 and 500 samples size 8 turned 45.
- `qc_reads_horizontal_barplot` left axis (sample ids): size 8.8 at 10, 7 at 100 and 500.
- After a My-view filter on the same table (`scripts/f5_dilemma.py`, `measures/F5.txt`; filter emulated on the table before drawing, as HOME's filters do): left axis size 8.8 with 10 samples, 7.0 with 100, 8.0 with 48 samples left, 8.8 with 8 samples left. Overlapping label pairs on that axis: 0, 197, 47, 0. The bottom axis (numbers) is turned 35 degrees in every case, whatever the size, because the sample ids are 8 characters long.
- So the text does depend on the data, and the user does not see or record why. Under N it does not change (8.8 everywhere), and the figure gets worse.

## Measures (computed from the drawn figure, `scripts/run_axis.py`, function `measure`)

Per picture: size and rotation read from the tick label objects; overlap = pairs of tick labels whose rotated rectangles intersect by more than 0.5 px (separating-axis test); cut off = a label box outside the figure; share = height (x labels) or width (y labels) of the span of the tick labels over the figure. Caveat: in faceted plots the share spans all panels and is not a sum. Cut-off labels: 0 in all 531 pictures, so the table below has no cut-off column.

Plots with any overlapping labels, out of 17 shipped plots, gallery shape (`measures/summary.txt`):

| Behaviour | 10 samples | 100 samples | 500 samples |
|---|---|---|---|
| T today | 0 | 5 | 5 |
| N none | 0 | 6 | 6 |
| O1 | 0 | 5 | 5 |
| O2 | 0 | 5 | 5 |
| O3 | 0 | 5 | 5 |
| O4 | 0 | 5 | 5 |

Home shape, out of 6 plots: T 0/2/3, N 0/3/4, O1 0/2/3, O2 0/3/3, O3 0/2/3, O4 0/2/3 (at 10/100/500).
The five plots that overlap at 100 and 500 in every behaviour are the ones with sample ids on an axis: `qc_reads_horizontal_barplot`, `qa_fanout_rows_per_sample`, `virulence_variants` (left axis), `amr_heatmap` (left axis, author wrote size 4), `virulence_bar` (bottom axis, author wrote size 6 turned 90). Pairs, `virulence_bar`: T 99 at 100 and 2485 at 500; O2 197 and 6895. `amr_heatmap` left axis: T 88 and 2250; O2 175 and 5358. Where the author wrote a value (the two shipped plots `virulence_bar`, `amr_heatmap`), O2 makes the picture worse than the author's own at 100 and 500, because the automatic size 9 turned 35 needs more room than the author's size 6 turned 90.
N overlaps in one more plot (`mlst_bar`, 1 pair) at 100 and 500, because it does not rotate. Nothing was cut off.

Variants (author writes size 14 once, in `variants/`; plots `virulence_bar`, `qc_reads_horizontal_barplot`, `miaou`), plots with overlap out of 3 at 10/100/500:

| Behaviour | `element_text` 14 | `theme_custom` 14 |
|---|---|---|
| T | 2/3/3 (author wins) | 0/2/2 (automatic wins, 14 lost, no message) |
| N | 2/3/3 | 2/3/3 |
| O1 | 2/3/3 | 2/3/3 |
| O2 | 0/2/2 | 0/2/2 |
| O3 | 0/2/2 | 0/2/2 |
| O4 | 2/3/3 (a written number wins) | 2/3/3 |
| O4, `size: auto`, min 7, max 14 | 1/3/3 | |

`miaou` (facets) at size 14 overlaps 6 label pairs at every data size (the 14 pt facet labels do not fit), and under O2 and O3 it is fixed (size 9 and 7). At 10 samples the "auto" prototype keeps 14 where it fits (`qc_reads` 14), and at 100 or 500 gives its minimum 7 and still overlaps (virulence_bar 99 and 3472 pairs).
Reading of the numbers, not a judgement: at 10 samples every behaviour except "author wins with a big number" gives a readable figure; at 100 and 500 samples none of the six behaviours gives a figure without overlapping sample id labels, on 8 x 5 in or on 10 x 5 in.

## The record (option 5), what would be written

For each behaviour and plot: `records/<plot>__<n>__<behaviour>[__variant].yaml`. Per axis: what the author wrote, what the automatic rule proposed, what the step applied, who decided, and a reason with the numbers. Example, O2, `qc_reads_horizontal_barplot`, 100 samples: "x axis text: size 9, turned 35 degrees, because 100 labels, the longest has 8 characters (more than 6: size 9, turned 35)"; "y axis text: size 7, because 42 distinct numeric values in 'total_reads' (rule: more than 12 gives size 8, more than 20 gives size 7)". The second line shows the flipped-axis effect from F1. O2 messages are collected as plot warnings (`plot_warnings`); HOME shows them in the alerts panel, the export does not call with `on_warning`.

## What each behaviour would cost to build for real (estimate, reasoned)

Common to any behaviour that keeps the adjustment: write the record into `effective_run.yaml` per plot (`export_handlers.py`, next to the theme record of D-0248, which is not built either), a test that the record equals the drawn figure; the coord_flip target defect of F1 is a defect in today's rule (reported, not a choice).

| Option | Files | Tests | Recipe format change | Effort tag |
|---|---|---|---|---|
| T keep, add record only | resolver (return the record), `viz_factory.py` (pass it), `export_handlers.py` | record equals drawn size and rotation; edge: no adjustment, filter changes it | no | sonnet/medium |
| N remove the step | delete `compute_optimisation_layer` and its call; docs and ADR text; a migration that writes today's values would depend on data, so shipped pictures change (golden pictures) | remove 2 tests that assert adjustment (`test_theme_settings_reach_the_figure.py:228-243`), add: no automatic change | no; contradicts D-0242 (a new decision is needed) | sonnet/medium; pictures of shipped recipes change |
| O1 author wins | resolver: detect theme_custom, named theme `base_size`, plot_defaults layers (extend `author_values` logic) | open xfail test `:245` passes; cases b to e | no | sonnet/medium |
| O2 automatic wins + message | resolver order, message plumbing, export | message test | no; removes the `element_text` override that D-0242 decided | sonnet/medium |
| O3 ceiling | resolver: min(author, automatic) and a fit test; to be exact, a measured draft | cases b to e, edge: author smaller than automatic, author angle written | no | sonnet/high |
| O4 auto with limits | the same fit logic; `element_text` params `size: auto`, `size_min`, `size_max`, `angle: auto` in the registry (`themes/core.py`), the recipe checker, the Blueprint form, the spec and docs, migration none | checker accepts and refuses, drawn, record | YES (format 1 may still be amended before release, D-0236) | sonnet/high or opus if the format is also redesigned |
Not asked, found: a figure whose width or height follows the number of labels (a visual adjustment of another kind) is not implemented anywhere and was not drawn.

## What I could not do or verify

- The generator cannot make consistent data for this recipe (3 tables of 11), so the 100 and 500 sample data are copies of the 42 shipped samples with new ids. Categories other than sample ids do not grow; a real larger dataset would have more genes, sequence types, countries.
- HOME's real figure width is not known; I used 10 x 5 in at 96 dpi as an assumption.
- The overlap test uses the matplotlib text boxes, rotated about the centre of the aligned box (plotnine's default rotation mode); not checked against another renderer.
- The estimate in the O3 and O4 prototypes (0.6 em per character, 1.6 in of margin) is mine; O3 and O4 are prototypes, not designs.
- No export bundle was built; F3 is from reading the writers.
- Pixel readability by a person was not judged; the sheets are for the panel. In the sheet titles I did not label the figure size per cell.
