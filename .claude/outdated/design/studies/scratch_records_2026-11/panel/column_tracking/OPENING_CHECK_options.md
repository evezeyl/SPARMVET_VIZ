# Should opening a recipe build or check everything? Facts and options

For the owner. Written by the coordinator, 2026-11-20, 08:28 by the clock, from a read of the code on dev `705cf433` (a scout, READ only) and the measurement of today (`measure/` in this folder). Nothing is built. She decides.

Her question: "when a recipe is open should not everything be build? then errors should be detected". Her wish: an error of the original recipe is found at opening, not later.

## What happens today (READ in the code)
**At the start of the app, for every recipe (the load gate):**
- The shape of the recipe is checked (the checker).
- Each SOURCE table is read, and its tier 1 steps are run on ONE row.
- Not run: the joins, tier 2, a plot's tier 3 steps. No plot is drawn. No check compares the columns a plot uses with the columns of its table.
- A recipe that fails is not offered in HOME, with the reason. The gate runs again when a recipe file changes on disk.

**When a recipe is opened in HOME:**
- ONE table is built: the first join of the recipe (or, without joins, the table of the first plot). If it fails, HOME shows "Data Assembly Failed" in place of everything.
- Every other table is built only when a plot that reads it is shown. A plot in a tab she has not opened is not built and not drawn.
- The export builds and draws every plot of its scope; a plot that fails becomes a stub with an error file.

**So an error of the original recipe first shows:**
| Kind of error | First shows |
|---|---|
| Wrong shape of the recipe | At start: the recipe is refused, with the reason. |
| A tier 1 step of a source table names a missing column | At start: refused. |
| The same in a join (a missing key, a step after the join) | At opening only if it is the first join; otherwise when a plot that reads it is first shown, or at export. |
| A tier 2 step | When that table is first built: the first plot shown that reads it, or at export. |
| A plot's own tier 3 step | When that plot is first shown, or at export. |
| A plot uses a column its table does not have | When that plot is first drawn, or at export. |
| A value that only the rows show (a text that cannot become a number, in row 500) | When the table is first built: a plot shown, or at export. The start check reads one row only. |

So today "everything is built at opening" is not true: an error in a plot she never opened can first show in the export.

## The costs measured today (same measurement as the B or C table)
| Recipe | Check every place by the plan (B) | Build every table (C) | Memory of the full build |
|---|---|---|---|
| figshare (2 MB) | 0.03 s | 0.39 s | 462 MB |
| demo (1 MB, 17 plots) | 0.16 s | 3.8 s | 225 MB |
| figshare, 30 times the data (62 MB, 6.1 million rows) | 0.11 s | 2.2 to 2.5 s | 2.1 GB |
Not measured: DRAWING every plot (a plot's drawing was not timed; the picture proof of all 51 shipped plots takes minutes, not seconds, in the test runs).

## Options
| | Option | What she sees | For | Against |
|---|---|---|---|---|
| 1 | **As today** | Errors appear when a plot is first shown, or at export. | Nothing to build. | An error can hide until the export. Against her wish. |
| 2 | **Check every place by the plan, at opening (B).** The app composes the plan of every table, join, tier and plot table, asks the engine for the columns, and checks that every step and every plot finds its columns. | At opening: either the recipe opens, or a list "these plots cannot be built, because ..." naming the table, the step and the column. | Fast (0.03 to 0.16 s measured; 0.11 s at 62 MB), little memory. Finds every error of structure: a missing column in a join, in tier 2, in a plot's tier 3, a join key, a plot that uses a column its table does not have (this last check does not exist anywhere today and would be new). Fails place by place: the plots that are fine stay usable. It is the same mechanism she just chose for the audit, so one mechanism. | Does not find an error that only the rows show (a bad value in row 500; a join that multiplies the rows). Those still appear when the table is built. |
| 3 | **Build every table at opening (C).** | A wait at opening (0.4 to 4 s on the shipped recipes; seconds and gigabytes on large data), then everything is ready or a list of what failed. | Finds also the errors that only the rows show. Every later plot opens at once (its table is stored). | The wait and the memory grow with the data: 2.1 GB at 62 MB of files, for every user at every opening of a changed recipe or new data. Today's build stops at the first failure of a table; "a list of everything that failed" has to be built. Tables no plot reads are built for nothing. |
| 4 | **Both: the plan check at once, the full build after it, in the background.** | The recipe opens at once with the plan check (option 2). A line says "building the tables ... 12 of 28"; she can already work; a row-level error appears as a notice when its table is reached, naming the table and the plots that read it. | Her wish in full: every error of the original is found without her opening every plot, and without a wait before she can work. Plots open at once afterwards. | The most to build: a background build that does not block the screen, shows progress, and can be interrupted when she changes the recipe; memory as option 3. A first design question of its own (what she may do while it runs; what the export does if she asks for it before the build ends). |

Notes for all options:
- An error is shown, never hidden, and never changes a result silently: a plot that cannot be built says why; the others stay usable (her decided rule: plain message, naming the step, the column and a fix).
- Whether a broken plot makes HOME REFUSE the whole recipe (as the gate does for a broken source table) or only marks that plot is a separate point (below).
- Drawing every plot at opening is not in options 2 to 4: the tables are checked or built, the pictures are drawn when shown. A plot whose columns exist can still fail to draw for a reason of its own (a scale, a theme); that would still show when the plot is shown or at export.

## Recommendation of the coordinator
**Option 2 now, with the new check that every plot finds its columns; option 4 as a later step if she wants the row-level errors too.**
- Option 2 answers most of her wish at almost no cost, and it is the mechanism B she already chose: the same code lists the places for the audit and checks the recipe at opening.
- It belongs naturally in the load gate (at start, and when a recipe file or the data changes), so that a recipe with a broken join or a plot without its column is reported before anyone opens it.
- The row-level errors (option 4) need a background build, which is a piece of its own; the speed finding of today (every table build reads all source tables again) should be repaired first, or the background build pays that cost many times.

## Points that are hers
1. Option 1, 2, 3 or 4.
2. When the plan check finds a broken plot or join: refuse the whole recipe in HOME (as today for a broken source table), or open the recipe and mark only the broken plots with the reason. My view: mark the plots; refusing a recipe of 17 plots for one broken plot hides the 16 that work; but the gate's rule today is "a bad recipe is not an option", so this is hers.
3. Whether the check runs at the start of the app for every recipe (as the gate does), or only when a recipe is opened.
