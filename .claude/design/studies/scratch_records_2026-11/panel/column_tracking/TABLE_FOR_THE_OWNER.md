# How the audit knows where a column exists: B or C, with measured costs (Q-A4, version 2)

For the owner. Written by the coordinator, 2026-11-20, 08:13 by the clock. Version 2 replaces version 1: she excluded A (rules in the map), D (stored tables only) and E2, and took Blueprint out of the choice. The live options are **B** and **C**. Facts: `FACTS.md`; the measurement, its scripts and outputs: `measure/` in this folder. Nothing is built. She decides.

## The two options
- **B. Ask the engine.** The app composes the plan of the recipe exactly as it does to build the tables, but builds and stores nothing, and asks the engine what each place will contain (names and types).
- **C. Run the recipe.** The app builds every table on the data and reads the columns of each.

## What was measured (a builder RAN it; scripts and outputs in `measure/`; three runs each in a fresh process, medians; the machine was shared with other test runs, load 3 to 6, so trust the times to about 20 to 30 percent)

The real data of the shipped recipes is small: `figshare_integration` 2.0 MB (30,256 rows), the demo recipe 1.0 MB (2,012 rows), the stress recipe 0.5 MB (10,000 rows). So the builder also made copies of the figshare data 30 and 100 times larger (61.6 MB with 6.1 million rows in the joined table; 205.9 MB).

| Recipe | Places | B: every place, also after every single step | C: build everything, nothing stored before | C: memory at its peak | B: memory at its peak |
|---|---|---|---|---|---|
| figshare (2 MB) | 9 | 0.03 s | 0.39 s | 462 MB | 187 MB |
| demo ST22 (1 MB) | 108 | 0.16 s | 3.8 s | 225 MB | 190 MB |
| stress (0.5 MB) | 3 | 0.02 s | 0.08 s | 201 MB | 186 MB |
| figshare x30 (62 MB, 6.1 million rows) | 9 | 0.11 s | 2.2 to 2.5 s | 2,100 MB | 247 MB |
| figshare x100 (206 MB) | 9 | 0.23 s | not run | not run | 360 to 374 MB |

(About 170 MB of each memory number is the app itself, before any data.)
For scale: building the table of ONE plot takes 0.16 s (figshare), 0.4 to 0.5 s (demo), 1.9 s and about 3 GB at 30 times the data. Opening the dialog through B costs less than drawing one plot.

- **Why B grows at all with the data:** the app checks each source file once when it reads it (the declared types against the values). That one read is the whole growing part of B (0.02 s at 2 MB, 0.22 s at 206 MB). Composing the plan and asking for the columns stay at a few thousandths of a second whatever the size.
- **Does B read rows anywhere else?** Measured by counting every read during a full B run: figshare 1 read (the source check), stress 1, demo 11: nine source checks and two reads by the check that refuses a silent loss when a decimal column is cast to whole numbers (it scans that one column; 0.05 s for 6 million rows). No other read.
- **Steps that would make B read rows, not used by these three recipes (READ in the code, not measured):** a pivot, a sample, a describe; a quantile on a table with a date column; the order check of a time join; the row count of a self-join. A recipe that uses one of them costs B a real read up to that step. A pivot is the only one whose columns come from the data values.
- **Do B and C say the same?** Yes, everywhere compared: figshare 5 tables and 70 columns, demo 51 tables and 302 columns, stress 2 tables and 10 columns: 0 differences in names, order and types. And B against the same plan really computed, at every single place: 9 places and 88 columns, 108 places and 799 columns, 3 places and 15 columns: 0 differences.
- **Not measured:** a step at tier 3 (no shipped recipe has one; the code treats it like any step); a recipe with a pivot; the drawing of a plot.

## What breaks each (tried on copies of the data, never the real files)
| Case | B | C |
|---|---|---|
| A data file is missing | The error names the table and the file. The other tables answer. The join and the plots that read the missing table have no answer: they must be shown as "unknown, because table X cannot be read". | Stops at the first table it cannot build. |
| A step names a column that does not exist | The engine's error names the column, not the table or the step number; the app finds the step by asking one step at a time (it already does this for tier 3). Places after it have no answer. | Stops there. |
| A join key that does not exist | A plain error with the recipe, the join, the step number and the columns of the left table. | Stops there. |

## B and C side by side
| | B. Ask the engine | C. Run the recipe |
|---|---|---|
| Exact names and types | Yes (0 differences with C on everything compared). | Yes. |
| Every place, also the middle steps | Yes: 108 of 108 places on the demo recipe. | Only if every middle step is computed too (the times above are for the tier ends); the stored tables cover 20 to 24 of the 57 tier ends of the demo recipe and none of its 51 middle places. |
| Time to open the dialog | 0.02 to 0.25 s on everything measured. | 0.4 to 4 s on the small data; seconds and gigabytes on large data. |
| Memory | About the app's own. | Grows with the data (2.1 GB at 62 MB of files). |
| Works for the audit copy (a recipe in memory) | Yes, the plan is composed from the recipe it is handed. | Yes, slice A built that run. |
| Finds errors that only the rows show | No (it does not compute the rows). They are found when the step is really applied, before she confirms: the dialog must show rows and plots affected anyway (decided), and that part is a real run of the changed tables only. | Yes. |
| A pivot in the recipe | Reads the rows up to the pivot (the engine has no other way); the wait is that table's build. | Same answer, same read. |
| Fails softly | Place by place: only what depends on the broken part is "unknown". | The whole run stops at the first failure. |

## A stored table at the end of tier 3 (her point 4)
- Today the table of a plot with its own tier 3 steps is computed when needed; storing it as a file, with its key, is possible (the question Q-A10).
- What it would give: a faster second draw of that plot, and "did this plot's table change" by comparing two files.
- What it would NOT give the dialog: the dialog needs the places BEFORE the new step is written, most of them in the middle of a tier, and no stored table exists there (51 middle places on the demo recipe, every source table, every table no plot opened yet). A stored tier 3 table adds one place per plot.
- So: a possible addition for speed, to decide apart (Q-A10); not a way to find where a column exists.

## Blueprint (her question: why was it in this choice?)
It should not have been. The audit and its list of places live in HOME only. Blueprint came into version 1 only because it reads the same map of a recipe, and because it starts with no data, where neither B nor C can answer. Checked today: Blueprint uses none of this; its column pickers offer the fields DECLARED for a table and never follow the columns step by step (after a rename the next step still offers the old names). That is a Blueprint improvement of its own (rules per action, which is the excluded option A, with the risk that a wrong rule shows a wrong column and no error). PARKED for the Blueprint design pass; nothing of it is in this decision.

## What stays true for both (from version 1)
- The same name is not always the same thing: on the demo recipe `L50` is a decimal number at 5 places and a whole number at 3. Each line of the dialog should show the type. Both B and C give it.
- A place the app cannot answer for stays in the list, grey, not tickable, with the reason (no silent failure, decided).
- The user viewpoint suggested leaving a place UNTICKED when the type differs there. She decided every place starts ticked. The alternative that keeps her decision: ticked, with the type difference written on the line. Flagged, not chosen.

## Recommendation of the coordinator
**B to list the places; a real run only for what the step changes.**
1. B answers "where does this column exist" for every place, exactly, in a fraction of a second, with little memory, and place by place when something is broken.
2. When she has chosen the places, the app runs the changed tables for real (the audit run of slice A, which reuses every untouched table) to show the rows and the plots affected before she confirms. That is where a row-level error shows. So the real run happens once, on what changes, not on everything to open a dialog.
3. C alone gives nothing more for the list of places, costs 4 to 50 times the time and far more memory, and stops whole on the first failure.

## Points that are hers
1. **B or C** for the list of places.
2. A recipe with a **pivot** (or sample, describe): accept that the dialog reads the rows up to that step, with a line that says so; or show the places after it as "known only after the tables are built".
3. The **type on each line**, and what a place with another type looks like (ticked with the difference written; or unticked, which changes her earlier decision).

## A finding beside the question (a task, no decision needed)
Building the demo recipe's tables takes 3.8 s for 1 MB of data because every table build reads all 12 source tables again; and checking tables that are already stored takes 1.7 s where reading their 24 schemas takes 0.003 s. This goes to the speed study, not to this choice.
