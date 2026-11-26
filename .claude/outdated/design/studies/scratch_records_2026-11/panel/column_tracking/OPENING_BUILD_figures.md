# "Opening a recipe builds everything": the four figures she asked for before building

For the owner. Written by the coordinator, 2026-11-20, from a measurement a builder RAN in scratch (scripts and outputs: `measure/` in this folder; nothing of the repository was changed). Medians of three runs in fresh processes unless said; the machine was shared with other test runs (load 3.5 to 8), so trust the times to about 20 to 30 percent and the memory to a few percent. Her decision (D-0326): at opening, every tier 1 and tier 2 table, the tier 3 table of every plot and every plot are built and stored by key; a plot is ready when selected; equal keys rebuild nothing. Nothing is built yet.

## What she must know first
1. **The tables are cheap. Drawing the plots is the expensive part.** On the shipped recipes the tables take 0.1 to 3 s; drawing all plots takes about 12 to 13 s. So a first open would take about **13 s (figshare, 3 plots) and 15 s (demo, 17 plots)**, against about 1 s today. A second open with equal keys: 0.01 to 0.1 s for the tables.
2. **A drawn plot is stored nowhere today**, not in a file and not in memory. Only tables are stored. "A plot ready when selected" needs a new thing: storing the picture. That raises one question that is hers (the size of a stored picture, below).
3. **On large data the drawing does not fit.** With the figshare data 30 times larger (62 MB, 6.1 million rows in the joined table) each of the three plots takes 59 to 85 s and 2.4 to 3.4 GB; all three: about 4 minutes and 8.9 GB. At 100 times (206 MB) the first plot went past 9.5 GB and was stopped. This is NOT caused by opening: the same plot costs the same today when its tab is shown. The cause is the plot itself: it hands all 6.1 million rows to the drawing library to count them into bars. Opening would only make her pay for all plots at once.
4. **Three of five staged errors pass today's start check and would be caught by a build at opening** (so her decision does what she wants), but **two of them give a message that names neither the table nor the step** (below). The messages must be made plain before this can "refuse with a plain reason".

## 1. What is built and stored today
- At the start of the app: each source table is read and its tier 1 steps run on one row. When a recipe is opened: ONE table is built (the first join). Every other table is built when a plot that reads it is first shown.
- Stored: the tier 1 table of each table and join that was needed, the tier 2 table when it has steps. Not stored: tier 3 (computed when needed), any picture.
- A plot is drawn each time its tab's picture is made by the screen; the picture is made at the size of the browser window (height 480 px, width the window's). The export draws it again at its own size (300 or 600 dots per inch).
- The drawing is repeatable: each plot drawn twice gave the same picture pixel for pixel (17 of 17 on the demo recipe, 3 of 3 on figshare; same process; not compared across machines).

## 2. Building one table at a time, each stored before the next
| Recipe | Time, first open | Memory at its peak (about 170 MB is the app itself) | Stored on disk |
|---|---|---|---|
| figshare (2 MB) | 0.14 s | 318 MB | 0.14 MB |
| demo (1 MB, 17 tables with plots, 24 files) | 3.3 s (2.65 s when the keys are computed once) | 225 MB | 0.08 MB |
| figshare x30 (62 MB, 6.1 million rows) | 2.05 s | 2,084 MB | 4.5 MB |
| figshare x100 (206 MB, about 20 million rows) | 6.9 s | 6,001 MB | 15.2 MB |

- **Is the 2.1 GB necessary?** Partly not. Today a table is first held whole in memory and then written. Written as a stream instead (tried in scratch, same result file, the key still in it): 1,550 MB at x30 (26 percent less) and 3,815 MB at x100 (36 percent less), and 15 to 25 percent faster. The rest is what the engine needs for the join itself.
- **Second open, everything stored, equal keys:** figshare 0.01 s, demo 0.08 s, x30 0.10 s, x100 0.48 s (at x100 nearly all of it is hashing the 206 MB of data files, once).
- **Two speed faults found on the way** (to repair with this build, no decision needed): (a) when the keys are not handed over, they are recomputed for every table: the demo recipe's second open then takes 1.27 s where 0.08 s is enough (94 percent of the time looks up the versions of two libraries, 1,972 times); HOME hands the keys over, other callers do not; (b) every table build reads ALL source tables of the recipe again (17 tables, 12 sources each time on the demo recipe).

## 3. Tier 3 of every plot, and every plot drawn (pictures 960 x 600 pixels)
| Recipe | Tables | Tier 3, all plots | Drawing all plots to PNG | Total first open | Memory at its peak | Pictures on disk, PNG / SVG |
|---|---|---|---|---|---|---|
| demo (17 plots) | 2.65 s | 0.06 s | 12.6 s | **about 15 s** | 388 MB | 0.95 MB / 3.6 MB |
| figshare (3 plots) | 0.12 s | 0.00 s | 12.8 s | **about 13 s** | 652 MB | 0.29 MB / 0.35 MB |
| figshare x30 (3 plots) | 2.0 s | 0.01 s | 229 s (one run) | **about 3.8 minutes** | 8,948 MB | 0.29 MB / 0.35 MB |
| figshare x100 | 6.9 s | | stopped above 9.5 GB in the first plot | not possible on this machine | | |

- Per plot, demo recipe: 0.46 s in the middle; the slowest 3.1 to 3.4 s. Per plot, figshare: 3.9 s (203,146 rows each). Saving as SVG as well costs about the same again.
- The memory of one plot is not given back before the next: the peak grows with the number of plots drawn in one go.
- No shipped recipe has a tier 3 step, so tier 3 itself costs nothing here.

## 4. Errors during such a build, and what "refused with a plain reason" would show
| Error staged (in copies) | Today's start check | What the build raises | The text names |
|---|---|---|---|
| A join key that does not exist | REFUSED, plain: "a join key column is not declared ... 'sample_idX' is not declared in the left table (fg_metadata)" with a tip | An error naming the recipe, the join, the step number and the columns of the left table | table, step: yes. plot: no. |
| A tier 2 step naming a missing column | NOT refused | The engine's own error: `"no_such_column" not found` and its plan | column only. **No table, no step, no plot.** |
| A plot using a column its table does not have | NOT refused | "Plot 'plot_a_phenotype_bar': the aesthetic 'x' is mapped to the column 'no_such_column', which the data does not have. Fix: ..."; the other plots draw | plot, column: yes. |
| A value in row 9,990 that is not a number, column declared a number | REFUSED, plain: the column, the declared type, the value 'abc', two suggestions | The same text at the table's build | table, column, value: yes. Row number: no. |
| The same value, column declared text, then cast to a number in a tier 1 step | NOT refused | The engine's own error: "conversion from str to f64 failed in column 'value' for 1 out of 6219 values: ["abc"]" | column, value: yes. **No table, no step.** |
- A plot that fails does not stop the others; only what depends on the broken table fails.
- For the refusal to be plain (her decided rule: name the step, the column and a fix), the build at opening must add to the two bare engine errors the table, the tier and the step number (the app knows them: it can run the steps one at a time, as it already does for tier 3).
- Read with her words of today: one plot that cannot be drawn refuses the whole recipe.

## What follows for her decision (nothing is changed by me; these are the points to settle before the build)
1. **The wait at a first open: about 13 to 15 s on the shipped recipes** (against about 1 s today), then nothing on later opens. With a progress line ("building tables 12 of 24 ... drawing plots 5 of 17") this is workable; without it the app looks frozen. A progress line is needed.
2. **What "the plot is ready when selected" means, since no picture is stored today.** Two ways:
   - **(a) Store the pictures.** A selected plot appears at once. But a stored picture has ONE size, while the screen draws at the width of the browser window and the export at its own size and sharpness. Either the picture is stored as SVG (it scales; 3.6 MB for the demo recipe; one plot is 2 MB) and shown at any width, or it is stored at one fixed size. Hers: which, and whether the export may reuse it or always draws its own.
   - **(b) Draw every plot once at opening to PROVE it draws** (her test: "then we are sure that the plot recipe do not fail"), store the tables, and draw the plot again when selected (0.2 to 3.4 s per plot on the demo recipe, about 4 s on figshare). Nothing new to store, the same 13 to 15 s at opening, a short wait at each first selection.
3. **Large data.** At 62 MB the opening would take about 4 minutes and 9 GB because of the three plots, and at 206 MB it cannot finish on this machine. The cause is in the plots (all rows handed to the drawing), and it exists today for each plot singly. Ways: (i) the recipe counts in its tier 2 or the plot's tier 3 and the plot draws the counts (the recipe maker's good practice; the app can warn "this plot receives 6.1 million rows"); (ii) the app refuses or warns above a number of rows per plot; (iii) the plots are drawn after the tables, in the background, each shown when ready. Not a blocker for the shipped recipes; it is a blocker for "everything at opening" on large data unless one of these is chosen.
4. **Memory of the table build:** writing the tables as a stream saves a quarter to a third at no cost in the result. I suggest building it with this piece.
5. **The two speed faults** of part 2 are repaired with this piece (no decision needed).
6. **The messages of two engine errors** are made plain (the table, the tier, the step number, a fix) before a recipe can be refused for them.

My view, as a suggestion only: build the tables and tier 3 at opening as decided, with the stream writing, the two speed repairs and the progress line; draw every plot at opening as the proof (2b) and store the picture only if she chooses (2a) and its size; warn on a plot that receives very many rows (3 ii as a warning, not a refusal), and leave the background drawing (3 iii) for when a real recipe needs it.
