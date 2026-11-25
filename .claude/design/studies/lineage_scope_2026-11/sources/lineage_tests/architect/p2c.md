### C. Types along a path

### L036 cast_on_one_path
- From: sci C08; user A4, chk C10; D-0337, D-0347 (required: "cast to another type on one path only"), D-0202. Fixture FX-TYPES. Levels PURE, ENGINE. Wave 1 (lines), wave 2 (value, rows). Props P4 P5 P6 P7.
- Recipe: A(sample_id, year: Int64); J = A join B; `T2:J` casts `year` to String; plot Pc reads J, plot Pi reads A. Start `year` at Pi (whole number). Lines: `T1:A` (Int64, no note, reach (3, 2)), `T1:J` (Int64, no note, (2, 1)), `T2:J` tick (1, 1), here `year`, type_note "text here, whole number at the place you chose" (D-0337: ticked, the difference written), "only Pc" (String, same note), "only Pi". 
- Value: the user typed 2022. At `T1:A` the written step holds the integer 2022, at `T2:J` and `T3:Pc` the text `"2022"` (D-0202: written in the type of THAT place, per line); the dialog shows the value per line. The build of the audit copy succeeds (comparing a whole number with text FAILS at run time, verified in the scientist file F2).
- Rows: removing 2022 at A removes 2 rows of 6; the later steps are redundant. Compare O1.
- Wrong: the same typed value written at every line (a hard error at the text place, M20); the line missing for the text place; a note with no type.

### L037 cast_lossy
- From: sci C09; user A4b, chk C12; D-0202, D-0203. Fixture FX-TYPES (L50 Float64 values 2.0, 2.4, 2.5, 3.0; `T2:J` casts to Int64 by rounding down). Levels PURE, ENGINE. Wave 1 (type note), wave 2 (value, rows). Props P4 P5 P7. Partly BLOCKED by Q12 (section 5).
- Lines: `T1:A` (decimal), `T1:J` (decimal), `T2:J` (whole number, note "decimals were cut off by a step of the recipe: the same condition can keep different rows here"). Typing 2.0 removes 1 row at the decimal place and 2 at the whole-number place (2.0 and 2.4 both become 2): D-0203's warning with the count per line. Typing 2.5 cannot be written as a whole number: refused with a plain sentence for that line (D-0202); the number shown for that line is the refusal, never 0.
- Rows: user's `L50 >= 8.5` on the demo: the rows kept at the decimal place and at the whole-number place are both reported (R-DEMO, `QA_L50_integer`: decimal at 5 places, whole at 3).
- Wrong: silent conversion with no count (M10); a refused value written as 0 rows.

### L038 cast_to_category_and_missing
- From: sci C10. Fixture FX-TYPES. Levels PURE, ENGINE. Wave 2. Props P4 P5.
- Text cast to categorical at T2: the lines are `T1:A` and `T2:A` with the type note; a value that exists gives the same count at both; a value absent from the data gives a plain "no row matches here" at both. A text-to-number cast of a non-number makes missing values at the later place and none at the earlier: the two lines show different counts when the missing tick differs (the cast creates missing values the earlier place does not have).

### L039 cast_round_trip
- From: sci C11. Fixture FX-TYPES (T1 int to text, T2 text to int). Levels PURE. Wave 1. Props P1 P4.
- One column through three types: lines `T1:` (text note), `T2:` (the start's type). Wrong: the round trip is read as "a column disappears and a new one appears" and the T1 line is missed.

### L040 cast_to_date
- From: sci C12; OQ3. Fixture FX-TYPES (d: String "2022-03-01" cast to Date at T2). Levels PURE, ENGINE. Wave 2. BLOCKED by Q13. Props P4 P7.
- A value typed at the date place must be a date (refusal otherwise, never a silent range); at the text place it is the text. Whether a date is an allowed audit value at all is Q13.

### L041 float_and_integer_key
- From: sci C61. Fixture FX-TYPES (`year` read as Float64 from one file and Int64 from another, joined). Levels PURE. Wave 1. Props P4.
- Note "decimal here, whole number at your place" and the value written as `2022.0` or `2022` per place (L036's rule); a join on mixed key types is the engine's own matter, the walk reports the two types.

### D. Values changed without a change of the plan (ENGINE: only the rows tell)

All cases here assert the same thing from the other side: the PURE walk says "same column" (the plan is blind, F5 of the scientist file), so the ONLY protection is the count of rows affected per line (D-0316), measured on the audit copy. The tests prove the count, and prove that the walk does not claim more than the plan shows.

### L042 recode_in_place
- From: sci C20; OQ8. Fixture FX-VALUES (S(sample_id, country: Norway x3, Sweden x2, NO x1); T1 keeps; `T2:J` recodes Norway to NO; plot P reads J). Levels ENGINE. Wave 2. BLOCKED by Q20 (partly answered by D-0203). Props P4 P5 P6 P7.
- Start `country` at P (values NO, Sweden), type NO. Lines `T1:S` and `T2:J`, both tick, no type or name note (the plan is blind). Typing `"NO"`: `T1:S` removes 1 row, `T2:J` removes 4 (3 recoded plus the original). The dialog shows 1 and 4 (counts by really evaluating each place's filter on the audit copy). A user who types "Norway" removes 0 rows everywhere and is told "no row matches here".
- Wrong: the same count copied to both lines; no count (P5); the count read from the start place only.

### L043 fill_in_place_and_the_missing_tick
- From: sci C21, C36; D-0042 (every filter step states `na: keep|remove`, no default; HOME may preselect with a visible tick and a count). Fixture FX-VALUES (val Float64 with 2 missing; a fill with 0.0 at T1 of one table and in a downstream T2 of another). Levels ENGINE. Wave 2. Props P5 P7.
- Matrix (tick on/off) x (place before the fill / after the fill) for `val != 0.0`: counts 1 and 3 with the tick "keep missing", 3 and 3 without (Polars drops missing rows in `!=`, verified F1); asserts all four. The tick is a property of the step (D-0042), the counts differ per line.

### L044 round_in_place
- From: sci C22. Fixture FX-VALUES (val 2.34, 2.36, 2.41; `T2` rounds to 1 decimal). Levels ENGINE. Wave 2. Props P5.
- `val != 2.4` removes 2 rows after the round and 0 before: "no row matches here" at the earlier line, not a silent 0.

### L045 string_case
- From: sci C23, C59, C60. Fixture FX-VALUES (sample_id S1, s1; `T2` lowercases). Levels ENGINE. Wave 2. Props P5 P6.
- `"s1"` removes 0 rows before the lowercase and 2 after; the comparison is exact (no silent folding) and the written step holds exactly what was typed (no strip, no lower). A list of values with one absent here ("S9 matches no row here") gives a line note, not an error.

### L046 count_changes_value_not_rows
- From: sci C18. Fixture FX-VALUES (T2 `group_by country` with `n = count()`; plot draws `n`). Levels ENGINE. Wave 2. Props P5 P7.
- A filter at T1 on `val > 1` leaves the T2 row count unchanged and changes `n`: flags "table changed" and "picture changed" come from comparing CONTENT (D-0318), not row counts. Wrong: an implementation that compares counts reports "unchanged".

### L047 statistics_before_removal
- From: sci C19; OQ7. Fixture FX-VALUES (T1 step `z-score of val`; audit filter at the end of T1). Levels ENGINE. Wave 2. BLOCKED by Q23 (words). Props P4 P5.
- Audit steps go at the end of the tier (D-0146, D-0332), so the kept rows keep the z-scores computed WITH the removed rows: the test asserts the baseline z-scores of the kept rows are unchanged, and that the line carries a structured fact "a step before this place computes over the whole column (z-score, mean, rank)". Whether and how it is said is Q23.

### E. Joins and removal by key (ENGINE for the counts; the lines are PURE)

### L048 join_key_one_column
- From: sci C24. Fixture FX-ROWS. Levels PURE, ENGINE. Wave 1 (lines), wave 2 (rows). Props P1 P3 P5 P6.
- A(S1..S5), B(S1..S5 or fewer), J inner on sample_id. Start `sample_id` at J: lines `T1:A`, `T1:B`, `T1:J`, "only P". A filter removing S3 at `T1:J` only: A and B keep S3. At `T1:A` only: J loses S3, B keeps it. A row only in B that the inner join already dropped: the B line says "1 row in B, 0 in the join's result".
- Wrong: only `T1:J` (the key exists at A and B: P1); reach of `T1:A` forgets J.

### L049 left_join_before_after
- From: sci C26, C35, A3 of the user. Fixture FX-ROWS (A: S1..S5; B: S1..S3 with lab X, X, Y; J = A left join B). Levels PURE, ENGINE. Wave 2 (counts). Props P3 P5 P6 P7.
- Start `lab` at J: lines `T1:B` (reach B, J, plots) and `T1:J`. Filter `lab != "X"`: at `T1:B` it removes 2 rows of B and J keeps 5 rows with 2 EMPTIED (S1, S2 lab missing); at `T1:J` it removes 2 rows (tick "keep missing") or 4 (without: S4, S5 have missing lab after the join, F1). Counts for (B only, J only, both, none) x tick: 12 numbers computed by O1 and fixed in the test. The count shows "removed" and "emptied" (rows kept but the value became missing).
- Wrong: both lines announce "2 rows"; reach read as rows lost (user pitfall P1); the missing tick ignored.

### L050 inner_join_multiplies_rows
- From: sci C27. Fixture FX-ROWS (A 3 rows; B S1 x3, S2 x1, S3 x2; inner J = 6 rows). Levels ENGINE. Wave 2. Props P3 P5.
- `sample_id != "S1"`: A line 1 row, B line 3 rows, J line 3 rows; the unit of each number is the rows of that table. Distinct samples are not given unless Q21 says so.

### L051 join_with_missing_keys
- From: sci C28. Fixture FX-ROWS. Levels ENGINE. Wave 2. Props P5.
- A row with no sample id: missing keys do not match; a left join keeps the A row; a filter on the key removes it or not by the tick, at A and at J alike.

### L052 remove_sample_from_all_tables
- From: sci C30; user A1; D-0022 (the one automatic placement, "remove from all tables"). Fixtures FX-ROWS (three sources, two joins), R-DEMO, R-FIG. Levels PURE, ENGINE. Wave 1 (lines), wave 2 (rows), wave 3 (real). Props P1 P3 P6.
- Every table that holds the key (by identity) is a line, all ticked; after the step S3 is absent from every table and plot table (O1: no table contains S3), each table loses its own S3 rows; a source of two joins is not double counted. This is the case the others protect.

### L053 key_not_on_every_table
- From: sci C32. Fixture FX-ROWS (a lookup table D without a sample column; plot reads D). Levels PURE, ENGINE. Wave 1. Props P2 P6.
- D appears in no line and is unchanged (O1); it is not in the "remove from all" summary.

### F. Missing values

### L054 missing_tick_matrix
- From: sci C34; D-0042. Fixture FX-MISSING (v = [1, 2, 3, None, 3] and a text column with an empty string). Levels ENGINE. Wave 2. Props P5 P7.
- For every operator the dialog offers (equal, not equal, less, greater, in list, not in list, is missing, is not missing, contains) the removed count with the tick on and off equals O1's explicit null logic: `!=` 3 with `v = 3` and the tick off (the two 3s and the missing one), 2 with it on. The written step carries `na` explicitly (no default).
- Wrong: tick ignored; the step written without the missing clause while the count says 2.

### L055 empty_text_is_not_missing
- From: sci C53 (OQ16). Fixture R-FIG (`strip: true`, `null_values: []`), FX-MISSING. Levels ENGINE. Wave 2. BLOCKED by Q18. Props P5.
- With `null_values: []` an empty field is the empty text, not missing: the "no value" count is 0 and the dialog does not offer a distinction that no place has (stripped ids `" S1"` and `"S1"` are one value from T1 on).

### G. Plots, flags, the counts, redundancy

### L056 plot_flags_table_versus_picture
- From: sci C42; D-0318. Fixtures FX-CHAIN, R-DEMO. Levels ENGINE. Wave 2. Props P3 P5.
- Plot draws `val` against `year`: a filter on `country` removes rows (table changed, picture changed); a drop of an undrawn `lab` (table changed, picture the same); a filter that matches no row here (neither). NA handling of the picture is Q22's remainder.

### L057 earlier_place_covers_later
- From: sci C40, C43 (part), C02; user A12, chk C14 (part), P6; D-0198 (the three cautions are part of the tests), D-0194 (all ticked at opening). Fixtures FX-CHAIN, FX-REN. Levels ENGINE, BROWSER. Wave 2. BLOCKED by Q15. Props P5 P6.
- Default all ticked writes the same step at a table and at its dependants. Three cautions as tests: (1) an earlier place covers a later one in the SAME chain only; (2) only when the column is unchanged in between (a rename or cast between: not covered); (3) other chains are not covered. Count per line "removes 0 rows here that the ticked place above does not already remove". Results of "all ticked" and "earliest only" are identical rows (O1).
- Wrong: counts added up (3+3+3 = 9); "covered" shown across a rename.

### L058 rows_affected_definition_and_stability
- From: sci C43 (OQ14); user chk C2; D-0316. Fixture FX-CHAIN. Levels ENGINE, BROWSER. Wave 2. BLOCKED by Q16. Props P5.
- For each line ticked ALONE the rows that disappear from that table equal the announced count; the number on a line does not change when another line is ticked, or the dialog says which definition it shows ("alone" or "after the lines above"). The reach is never shown as a row count.

### L059 empty_result
- From: sci C57 (OQ17). Fixture FX-CHAIN. Levels ENGINE. Wave 2. BLOCKED by Q19. Props P5 P7.
- A step that removes every row, and one that matches none: "n of n rows" and "no row affected here" shown; the plot of an empty table does not crash the dialog.

### L060 ties_and_order_determinism
- From: sci C58. Fixture FX-ROWS (ties; `unique` or `sort then head` after a join). Levels ENGINE. Wave 2. Props P6.
- Two identical runs give identical tables including row order; the oracle matches including WHICH of the tied rows is kept.

### L061 audit_after_head_sample_unique
- From: sci C47 (OQ15). Fixture FX-ROWS (T1 `head(3)`). Levels ENGINE. Wave 2. BLOCKED by Q24. Props P4 P5.
- The audit step runs after the recipe's steps (D-0146): 6 rows, 3 after the head, 2 after removing S2; the 4th row does not come in. A filter before the head is not offered. The line carries the structured fact "a position step (head, sample, unique) comes before"; wording is Q24.

### L062 the_recipe_already_removes
- From: user A4, P7. Fixture R-DEMO (`MLST_with_metadata`: T2 keeps year 2023 to 2025). Levels ENGINE. Wave 2. Props P5.
- A filter `year > 2022` written at T1 removes 0 more rows at T2: "your step removes 0 more rows here"; and `era` (built from `year` at T2) changes legends when a T1 filter changes years: "picture changed".

### L063 one_plot_only
- From: user A2, chk C8. Fixture FX-TIERS (Pa, Pb on J1). Levels ENGINE, BROWSER. Wave 2. Props P3 P6.
- Untick all but "only Pa": Pb (same table) and J1 stay the same row for row; the summary says so. "Only this plot" appears for every plot and reaches exactly 1.

### L064 same_step_twice
- From: user A13, chk C14; Q17. Fixture FX-CHAIN. Levels ENGINE, BROWSER. Wave 2. BLOCKED by Q17. Props P5 P6.
- The same step added a second time: refused, warned, or finds nothing ("already in your audit steps (step 2); writing it again removes 0 rows"); the result in rows is the same as once.

### L065 nothing_ticked
- From: user A11, chk C11. Levels BROWSER. Wave 4. Props P6.
- No line ticked: "Nothing is ticked, so this step would change nothing. Tick at least one place." The confirmation is blocked; all lines start ticked (D-0194).

