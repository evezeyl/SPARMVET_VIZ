# Verification results (all RUN; scripts in .claude/design/studies/scratch_records_2026-11/panel/verify/)

## 1. Plot path, filter then drop (v1.py) - TRUE (with a number correction)
RUN v1.py: 100 rows, column n50 dropped on the frame, then VizFactory.render with filter n50 < 42.
- Today: the filter is skipped (viz_factory.py ~173), the plot collects 100 rows (not 42; 42 appears only when the column is NOT dropped first).
- Code order: home_theater.py ~528-533 drops the column from lf BEFORE render; filters reach render in plot_spec["filters"] (~483-497).
- If the skip raised: n50 is absent from the schema at that point -> yes, it would raise. So "filter n50, then drop n50" would become an error.

## 2. modif_filter value conversion (v2.py, v2b.py) - PARTLY
Matrix (7 column types x 6 value kinds x eq/ne/gt/in) is in the output of v2.py. Summary:
- Int64/Float64 with text of a number ("90"): ERROR today for all four ops. Conversion would make them run (new runs only).
- Int64 with float 90.5: RUNS today, eq=0 rows, gt=2 rows (compared as numbers, not cut). coerce_filter_value(90.5, Int64) = 90.5, same rows. No change.
- Int/Float with int/float values: conversion returns the same number; same rows.
- Int/Float with bool True: RUNS today (True acts as 1). Conversion gives 1 / 1.0; rows identical (v2b.py).
- Non-numeric columns (String, digits-string, Boolean, Date, Categorical): coerce_filter_value returns the value unchanged, so no change. (Note: String column with int value: ERROR today; digits-String with text "90" runs and stays the same.)
- Cells that RUN today and would give DIFFERENT rows: none found (v2.py DIFF list is empty).
Limit: coerce_filter_value only touches numeric columns; claim holds for it as it is written today. A conversion for Date/Boolean/String would be new code and was not tested.

## 3. stat_function text (v3.py) - restricted today
- lambda x: x**2 : evaluated (callable built).
- __import__('os').getcwd() : refused ("the function 'getcwd' is not allowed").
- x.__class__.__mro__ : refused ("the attribute '__mro__' is not allowed").
- open('/nonexistent_marker') : refused ("the function 'open' is not allowed").
Only the harmless text was evaluated. Not tested: other bypass tricks (checker is an AST allow-list in utils/formula_check.py, not audited here).

## Correction on the row numbers of claim 1
v1.py used NO shipped recipe: a synthetic 100-row frame (columns g, n50=0..99, y), one invented plot spec, filter n50 < 42, no tier-2 steps.
Its 100 = total of that synthetic table (filter skipped); its 42 = n50<42 on range(100), a coincidence with the 42 in the findings file.
Not comparable with QA_population_zscore (n50 >= 324189: table 21 rows, plot 42 rows, table total 42). v1.py did not reproduce that plot or its row count.
What v1.py does show: same skip behaviour (dropped column -> filter skipped, all rows kept) and that raising would hit an absent column.
