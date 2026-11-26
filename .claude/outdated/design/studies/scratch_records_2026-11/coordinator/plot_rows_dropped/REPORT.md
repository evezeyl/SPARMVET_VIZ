# Does a plot leave out rows of its table with no word? (check by a reviewer, 2026-11-21; filed by the coordinator)

Nothing edited. Scripts in `scratch/` (r1.py, r1b.py, r4.py, r4b.py). Raised by the data scientist viewpoint of the engine study.

## For the owner
1. YES, in the code. When a NUMBER column that a plot uses for x or y holds an empty value or "not a number", the plot leaves that row out. The only message is a line on the server console ("Removed 1 rows containing missing values"). The user sees nothing: not in HOME, not in Alerts, not in the export, not in the Gallery.
2. This holds for point, column, boxplot and line plots. On y a line plot does not even write the console line: the line shows a break (likely; the pixels were not inspected).
3. On the demo recipe today NO plot loses a row (0 of 18). The empty values of the demo are in TEXT columns, and those rows are kept and shown as "nan" on the axis or as their own group.
4. No other shipped recipe is affected either (about 30 more plots drawn, 0 rows removed).
5. HOME's table for such a plot would show N rows while the plot draws fewer, with nothing saying so. Nothing is decided on telling the user. The nearest decisions point that way: D-0050 ("No silent error that is the rule."), D-0261 (the same case for one layer: a plain warning with the count; not built).

## Evidence
| Plot | Column with the empty value | Rows left out | Console line | Picture |
|---|---|---|---|---|
| point | x or y (number) | 1 | `geom_point : Removed 1 rows containing missing values.` | same as without the row |
| column | x or y (number) | 1 | `position_stack : Removed 1 rows ...` | same |
| boxplot | y | 1 | `stat_boxplot : Removed 1 rows containing non-finite values.` | same |
| line | x | 1 | `geom_path: Removed 1 rows ...` | same |
| line | y | kept | NONE | differs: a break in the line (likely) |
| any | a text column as fill, colour, x or facet | 0 | none | the row is drawn (its own group or panel) |
- Where the two kinds of missing become one: `libs/viz_factory/src/viz_factory/viz_factory.py:267`.
- The only handling of the plot library's warnings in the app silences them: `libs/viz_factory/src/viz_factory/checked_plot.py:202-203` (inside the test "can this plot be drawn").
- HOME sends to Alerts only the app's own build warnings (`app/handlers/home_theater.py:733-734, 798-799`). The export records the same only (`app/handlers/export_handlers.py:1283, 1617`). Gallery pictures and the opening build: no handler (`app/modules/gallery_examples.py:130-132`, `app/modules/opening_build.py:151`).
- The retest recipes named `_dirty` show how it hides: their Year has empty values but is text, so the rows are kept. A numeric Year would lose them with no word.

## Options (no recommendation by the reviewer)
A. Nothing now: no shipped recipe is affected.
B. Catch the plot library's line where the plot is drawn and show a plain notice with the count and the column in HOME (Alerts; the plot badge or the table header could carry "N rows have no value in x and are not drawn").
C. B, and the same line in the export and in the Gallery picture record.
D. The recipe check warns or refuses when a number column used for x or y can hold empty values, so that the recipe states the removal as a visible step. It needs the data, not the recipe alone.
E. B or C, plus a rule for a line plot at an empty y (a gap, with a notice).

## Not verified
The app in a browser; what the console prints in a real run (reasoned: once per place); the break in the line; date, true/false and category columns; other plot kinds (bar by count, smooth, tile, violin); the export itself was read, not run.
