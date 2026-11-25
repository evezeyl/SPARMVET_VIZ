# Test cases for the audit dialog lineage walk: scientist and data scientist viewpoint

Sources read: ledger D-0022, D-0194, D-0195, D-0197, D-0198, D-0202, D-0203, D-0297, D-0316, D-0318, D-0322, D-0325, D-0332, D-0337, D-0344, D-0346, D-0347; `tmpAI/panel/column_tracking/FACTS.md`. Evidence class: the Polars behaviours quoted in section 0 were RUN (`tmpAI/panel/lineage_tests/scientist/chk.py`); everything else is reasoned from the ledger and is a specification of expected results, not a reading of the code under test (I did not read the walk's code: it does not exist yet).

## 0. Facts the cases rely on (verified by running Polars)

- F1. `filter(col != 2022)` drops the rows where col is missing (`[2021,2022,None,2022]` gives 1 row, not 2). `==` also drops missing. So any filter written as a keep-condition removes missing rows unless the step says "keep the rows with no value". The row count removed is NOT only the matching rows.
- F2. Comparing an integer column with a string (`col == "2022"`) fails at run time ("cannot compare string with numeric type"), and the reverse (text column compared with 2022) fails too. So a value of the wrong type at a place is a hard error, never a silent 0 rows. Comparing a decimal column with `2022.0` works and `cast(Float64) == 2022.0` matches the integer 2022 (2 rows).
- F3. A left join with a clash on a non-key name gives `v` and `v_right` by default (a `suffix` argument renames it); an inner join with a duplicated right key multiplies rows (3 rows stayed 3 here, with one key twice on the right and one missing: 3 = 2 + 1).
- F4. The figshare recipe's sources have `strip: true` and `null_values: []`: whitespace is removed at ingestion, and no text is read as missing. A "place" at a source table sees stripped values; IDs `" S1"` and `"S1"` are one value from tier 1 on. The dialog must not offer a user a distinction that no place has.
- F5. A plan (`collect_schema`) gives names and types only. It cannot see: a value recode, a fill, a rounding, a string change, a row count, a join that creates missing values. Every case marked "plan blind" below needs the rows-affected count (D-0316) to protect the user.

## Notation and common fixture

Place = (table, tier). `T1:A` = end of tier 1 of source A. `T2:J` = end of tier 2 of join J. `T3:P` = the plot's own table. A "line" = place, ticked or grey, reach, note. Reach = number of tables and plots that depend on the place, the place itself counted, written `(tables t, plots p)`. A dependant counts even when the column is absent there (it still receives the removed rows). Statuses: `T` ticked, `G` grey (reason).

Row counts: "before" = baseline build with no audit step; "after" = build of the audit copy.
Columns of the common fixture (change in each case as stated):
- A(sample_id str, year int, country str, val float): rows a1..a6.
- B(sample_id str, lab str, year int): rows b1..b6.
Always build the test recipe as a tiny recipe on stored CSVs; the oracle is a plain Python interpreter written in the test (pure `polars` eager calls on the fixture, no code from the app).

Properties: P1 no place missed, P2 no false place, P3 the reach is right, P4 the note says the truth about type or name, P5 rows affected right per line, P6 nothing changes outside the ticked places, P7 it can fail.

How every case proves P6 and P7 (the common harness, written once, used by all cases):
H1. Baseline: build the recipe unchanged; keep every table and plot table as an eager frame.
H2. For each subset S of the ticked lines (at least: all ticked, each alone, none), build the audit copy.
H3. Oracle: for every table and plot X, expected(X) = baseline recipe replayed by the test's own interpreter with the filter inserted at the ticked places of S. Compare row sets (sorted by all columns) and column names with types. Any table not downstream of a ticked place must equal baseline byte for byte (P6).
H4. A mutation check: the test is run against a deliberately broken walker (e.g. the line list with one line removed, with one line added, a reach off by one, the value not retyped, the step written one tier too early); each must make the test fail (P7). Keep these mutants in the test file as parametrised "must fail" cases.
H5. Files: the original `steps` of every tier are unchanged (compare with the original file); the steps live only in `audit_steps` (D-0332).

---

## 1. Equality along a path

### C01 equal_chain: no step changes the column
Recipe: A(sample_id, year, country, val) with T1 steps that only sort and filter val>0; join J = A with B on sample_id (B has sample_id, lab), no tier 2 steps; plot P1 reads J, no tier 3 steps; plot P2 reads A (T1) directly. Column: `country` chosen in the view of T1:A.
Expected lines (distinct tables only): `T1:A` (reach 2 tables A and J, 2 plots), `T1:J` (J is a different table from A: it has its own join step; reach 1 table, 1 plot), "only P1" (0 tables, 1 plot), "only P2" (0, 1). NOT lines: `T2:J` (J has no tier 2 steps: same table as `T1:J`), `T3:P1` (no tier 3 steps). Exactly 4 lines. All ticked, no type note, no name note.
Expected result when all ticked, filter `country != "NO"` with a6 the only NO row, joined to one B row: A loses 1 row, J loses the joined rows of a6, P1 and P2 each "table changed" and "picture changed" if the plot draws country or the rows. Written steps: one at T1:A, one at T1:J, one at P1, one at P2 (the user has ticked all; the "earlier place covers the later" caution D-0198 applies: see C40).
Wrong implementation: lists T2:J and T3:P1 as extra lines when they have no steps (P2); counts reach as 1 for the shared table (P3); lists one line per tier regardless of emptiness (P2); misses "only P2" because P2 reads T1 directly (P1).
Tests: P1 P2 P3 P6 P7.

### C02 equal_chain_one_line_or_several
Same as C01. Question the test settles: when everything is equal, are `T1:A` and `T1:J` two lines or one? The decided rule (D-0346) is: distinct tables are lines, a step on a shared table reaches everything below it. A and J are distinct tables, so two lines. The test asserts two lines AND that ticking only `T1:A` gives the same final rows at J, P1, P2 as ticking all four (the later places are redundant, not different): expected rows after = identical in the two builds. Wrong: a walker that merges A and J into one line would hide the user's chance to filter only the joined table (P1).
Tests: P1 P3 P5 P6.

## 2. Renames

### C03 rename_one_path
Recipe: A(sample_id, country); B(sample_id, country) both sources carry a `country`. T1:A renames `country` to `origin`; B unchanged. J1 = A join B? No: keep it simple with two plots reading A and B separately; plot Pa reads T1:A, Pb reads T1:B; no join. Column: user views Pa's table and picks `origin`.
Expected: start column is `origin` at T1:A. Lines: `T1:A` (the column is `origin`, original name `country` at the source), plus the line of the source `fg A` before the rename is NOT a separate table (the source table before tier-1 steps is not a place). `T1:B` is NOT a line: `country` of B is a different column that happens to have the old name (P2). Note on the A line: "called `origin` here (renamed in tier 1)" when the user starts from a table where the name is the old one.
Variant C03b: the user starts from Pb's table and picks `country`: lines `T1:B` only, plus `only Pb`. `T1:A` must NOT be offered although A's source has a `country` and its header matches (the plan of T1:A has `origin`, not `country`). Mutants: matching by name over plans offers `T1:A` in C03b? It would not (A plan lacks `country`): correct by plan. The name-matching mutant FAILS C03 instead: starting from `origin` at A it would not find A's source.
Result when applied at `T1:A` with `origin == "NO"` removed: the step at T1:A is written with column `origin`; A loses its NO rows; Pb and T1:B unchanged (P6).
Tests: P1 P2 P4 P6.

### C04 rename_on_all_paths
A(sample_id, country) -> T1 rename country->origin; the join J = A join B (B(sample_id, country) renamed country->origin in its T1); T2:J rename origin->origin_r? Two paths from the column: it is two columns. Make it simple: both A and B rename `country` to `region`; J joins on sample_id with suffix; J has `region` and `region_right`. Plots P1 (reads J). Column: user picks `region` in J.
Expected: ambiguity. `region` at J is A's column; `region_right` is B's. The lines for `region`: `T1:A` (name `region`, original `country`), `T1:J`... and NOT `T1:B`. Lines for `region_right`: `T1:B`, `T1:J`. The test asserts the two choices give different line sets and that a filter written from `region` never reaches B.
Wrong: after a join the walker follows name `region` back into B too (name match) and offers `T1:B`, so B rows vanish where the user meant A's.
Tests: P1 P2 P4 P6.

### C05 rename_on_none
Same as C01; asserts that no note about renaming appears (a note on equal lines would be noise or a false statement) (P4).

### C06 rename_back
A(sample_id, country): T1 renames country->origin; T2 (via the table's tier 2) renames origin->country. Plot P1 reads the T2 table. Column: user views P1's table and picks `country`.
Expected: the walk back follows the identity: P1's `country` came from A's `country` via `origin`. Lines: `T2:A` (called `country`), `T1:A` (called `origin` here, note), source table not a line, "only P1". Reach: T1:A (2 tables, 1 plot) if T2 has steps; T2:A (1 table, 1 plot). Note on the T1 line: "called `origin` here".
Expected result: the step at T1:A is written with `origin`, at T2:A with `country`, at P1 with `country`. All three remove the same rows.
Wrong: the walker believes the name equals the identity and skips T1 (because `origin != country`), missing the line (P1); or treats the T2 `country` as a new column with no origin and offers no earlier line.
Same name does not prove the same column and a different name does not prove a different one: this is the test for it. (Open question OQ1 asks whether the owner considers a rename back "the same column" - the decided walk "back to the source" says yes, so expected = same column.)
Tests: P1 P4 P6.

### C07 two_columns_same_name_two_paths
A(sample_id, a_year int) and B(sample_id, b_year int); T1:A renames a_year->year; T1:B renames b_year->year; plot P1 reads a union-like stack? Use two plots: Pa reads T1:A (has `year`), Pb reads T1:B (has `year`). Column: `year` in Pa.
Expected: lines `T1:A` and "only Pa". `T1:B` NOT offered even though its plan has a column named `year` of the same type (the same name and the same type are not the same column). Note on nothing; P2 is the point. The dialog must say on the A line the source column `a_year`.
Then add a join J = A join B on sample_id with suffix `_b`: J has `year` and `year_b`. Choosing `year` in J: lines `T1:A`, `T1:J` (the A one); choosing `year_b`: `T1:B`, `T1:J`.
Wrong: name-based match at each table offers T1:B for `year`, so the step removes year 2022 rows of B too: B loses rows the user did not mean (P6). The row counts per line (P5) show B rows reduced: the test fails when the line is present.
Tests: P2 P4 P5 P6.

## 3. Casts

Common cast fixture: A(sample_id, year) with year int values 2020, 2021, 2022, 2022, 2023, None; the cast table path: T1:A keeps `year` int; T2 of join J casts `year` to string; plot Pc reads J; plot Pi reads T1:A. Column: user picks `year` in Pi's table (int).

### C08 cast_int_to_text_one_path
Lines: `T1:A` (int; reach 2 tables, 2 plots) with note none (this is the start place type); `T2:J` (year is text there; note "text here, number at your place"; ticked, D-0337); "only Pi", "only Pc" (type text). Value written: user typed 2022. At `T1:A` the step holds `year == 2022` typed integer; at `T2:J` it holds `year == "2022"` typed text; at `T3:Pc` text. The dialog shows the value per line (D-0202). Expected result of removing year 2022 (filter keep `!= 2022`, with the missing row KEPT via the missing tick): A has 6 rows -> 4 (2022 twice removed); J after join: the 2022 rows gone; J's step at T2 removes the same J rows, redundant. All plots match.
Wrong: the same typed 2022 written at the text place gives a hard run error (F2), so the build of the audit copy fails: the test asserts the written file contains `"2022"` at the text place and the build succeeds. A second wrong version writes `"2022"` at the int place.
Tests: P4 P5 P6 P7.

### C09 cast_decimal_to_whole
`val` is decimal at T1:A (values 2.0, 2.5, 3.0); T2:J casts to integer (a lossy cast: 2.5 -> 2). User picks `val` in the T1 view and types 2.5 (filter `val != 2.5`). At T2:J the value 2.5 cannot be written as an integer: D-0202 says "2022.5 to an integer is refused with a plain message".
Expected: the T2:J line stays ticked with the type note (D-0337) AND the value cell for that line shows a plain refusal; the confirm is blocked for that line (OQ2: does the whole dialog block, or only this line, or does it grey?). Row counts: T1 line: 1 row removed; J line: not computable (refusal), so "rows affected" shows the refusal, not 0. Expected test assertion: no step with an invalid typed value is ever written; the number shown is never `0` for a refused line.
Also "two values at T1 become one at T2" (D-0203): values 2.0 and 2.4 both become 2 at T2 after the cast (rounding): typing `val != 2.0` at T1 removes 1 row, at T2 removes 2 rows (2.0 and 2.4). The dialog must warn (D-0203) with the count per line (1 versus 2). The test asserts the warning exists and the counts 1 and 2.
Wrong: silent conversion at the later place that removes 2 rows with no note (P4 P5).
Tests: P4 P5 P7.

### C10 cast_text_to_category
`country` is text at T1:A, cast to categorical at T2 of the table. Filter at the categorical place `country != "NO"` works in Polars; but a category with a value absent from the dictionary (e.g. user types "XX") may raise or match nothing. Test: type a value that exists at T1 and one that does not; expected lines: `T1:A` and `T2:A`, note "category here, text at your place" (type differs). Row counts per line identical for a value in the data (both remove 2 rows); a zero count line for "XX" at both with a "matches no rows" note.
Check also cast text to int where the text holds `"2022 "` or `"abc"`: ingestion strips (F4) so whitespace is not in the data; "abc" cast with non-strict gives missing. Expected: rows with "abc" become missing at the later place: a filter `year != 2022` at the later place KEEPS or REMOVES them according to the missing tick; at the earlier place they are text and are kept (they differ from "2022"). The two lines show different counts when the missing tick differs (P5): documents that a cast creates missing values the earlier place does not have.
Tests: P4 P5.

### C11 cast_number_to_text_then_back
Cast int->text at T1 and text->int at T2 (round trip). The identity is the same column through three types. Lines: T1 (text note), T2 (int, start place). Values written typed per place. Expected rows equal at the end. Wrong: the round trip is seen as "a column that disappears and a new one appears" and the T1 line is missing (P1).
Tests: P1 P4.

### C12 cast_to_date
Text `2022-03-01` cast to date at T2. The user at the date place types a date. The T1 text line needs the text `"2022-03-01"` (typed per place). A user typing `2022` at a date place is refused (not a date). Expected: refusal, never a silent range. Open question OQ3 (are dates allowed values at all in the audit filter).
Tests: P4 P7.

## 4. Drops and re-creation

### C13 drop_on_one_path
A(sample_id, country, val); T1:A keeps all; table A2 is a second tier-1 view? Use: plots Pa (T3 drops `country`) and Pb (no T3 steps); both read T1:A. Column: `country` in the view of T1:A.
Expected: line `T1:A` (reach 1 table, 2 plots), "only Pb" (ticked), "only Pa": the column does not exist at Pa's table (dropped by the recipe) : the plot has its own audit steps at tier 3 appended AFTER the recipe's steps: the column is absent at the place the audit step would be written. Expected: line "only Pa" is GREY ("column dropped in this plot's recipe") or absent. OQ4: grey or absent? Reach of the `T1:A` line counts Pa (Pa depends on A even though it dropped `country`).
Expected result: ticking `T1:A`, filter `country != "NO"`: A rows 6->5, Pa "table changed" (rows differ even though the column is gone) and "picture changed" yes if Pa draws rows; ticking only Pb: A unchanged, Pa unchanged.
Wrong: the walker follows the name to Pa's T3 and offers a tickable line which crashes at build (P2); or drops Pa from the reach (P3) so the plot is not reported as changed, a silent change.
Tests: P2 P3 P5 P6.

### C14 drop_with_new_column_same_name
A(sample_id, country, val): T1 drops `country`, then a new-column step creates `country` as `"X"` constant (or computed from val). Plot P reads T1:A. Column: user at P picks `country`.
Expected: the column the user sees is the NEW one (not the same thing as the source `country`). Lines: the place where it was created is the earliest place of this column: the walk back stops there. If created at the end of T1, `T1:A` is a line; the source table with the original `country` is not a place. A filter on the new column removes rows by its computed values. The test starts from the same name in the same table before and after the drop: before the drop (a view of T1 mid-way is not a place), so test two variants:
 (a) the user picks `country` in a table downstream of the recreation: the line set is the post-recreation tables, with no note "same as the source column".
 (b) a second table B has the ORIGINAL `country` untouched; the user picks `country` in B: A must NOT be a line (A's `country` is a different column), even though its plan has the same name and the same type text (P2).
Wrong: name-based tracking merges the two and offers A's table (P2) so rows removed from A by a source-country rule remove rows that were never source-country-filtered.
Tests: P1 P2 P4.

### C15 audit_step_on_column_dropped_by_recipe_later
T1:A recipe steps: select (drops `country`) in the middle of the tier; audit steps go after steps. Column `country` exists at the source and at the beginning of T1 but not at the end.
Expected: the end-of-tier plan lacks it: no line at T1:A for `country`. But the user could view only tables where it exists, so she starts from a different table (e.g. the raw source in an other table that did keep it). The test: no line is offered where the audit step would run after the drop; if offered, the build of the audit copy would fail (a step that names a column that does not exist, D-0176).
Tests: P2 P7.

### C16 drop_audit_step_on_key
The chosen column is `sample_id` and the user asks to drop (the audit step kind "drop column"): D-0297: a key column cannot be dropped. Expected: with kind "drop column" the lines of tables where `sample_id` is a join key are grey/refused with the plain message; at a table where it is not a key (a leaf with no join below) the drop is allowed. Result check: the drop at a non-key place removes the column from that table and each dependant; dependants that use it later (a join, a plot variable) fail: the dependants are listed as "plot changes: table changed, picture the same / broken"? Open question OQ5: a drop of a column that a plot draws (picture changed) or a later step of the recipe uses (the build breaks): what does the dialog say? The test asserts that the dialog lists those plots before the confirm.
Tests: P2 P3 P7.

## 5. Aggregation that keeps the name

### C17 aggregate_group_keep_name
A(sample_id, country, year, val) 6 rows; T2 group_by country and aggregate: keep `country`, `year` (the group key), `val_mean`. Plot P reads T2. Column: `year`: is it kept as the group key. Rows before aggregation: A 6 rows (country x year: NO 2021, NO 2022, SE 2021, SE 2022, SE 2022, SE 2023). Group_by country, year: 5 groups. Filter `year != 2022`:
 - at T1:A (before): removes 3 rows (NO2022, SE2022 x2); aggregation then has groups NO2021, SE2021, SE2023 (3 groups) and the mean of the remaining rows.
 - at T2 (after): removes 2 groups (NO2022, SE2022); the means of the remaining groups are unchanged from the baseline: here equal. They differ if the group key is only `country` (year as an aggregated max): then the earlier filter changes the means (T1 mean over fewer rows) and the later filter removes a whole country group.
Expected: both lines are listed; row counts per line: T1:A line "3 of 6 rows" with the dependent T2 "5 -> 3 groups"; T2 line "2 of 5 groups" (units: rows versus groups). The line note says "after a grouping: removes groups, not rows" and that the earlier line changes the group values. The plot P is "table changed" and "picture changed" in both, but the values drawn (means) differ in the second variant: assert the means after each build equal the oracle (not equal to each other).
Variant C17b: the column is aggregated away and renamed (`val` -> `val_mean`): `val` is not the same column as `val_mean` (the mean of rows is a new quantity): lines for `val`: `T1:A` only (reach through the group_by, P counted), no line at T2; a line "T2 val_mean" for the user who picks `val_mean` has no earlier place that "the same column" exists at, except as a derived column: expected is NO line at T1:A for `val_mean` (the mean is not a source column) and the dialog must say "computed here". OQ6: whether a derived column is offered back-lines.
Wrong: treats group rows as rows and reports "2 rows" for both (P5); or says the T2 line is the same as the T1 line (P4).
Tests: P3 P4 P5 P6.

### C18 aggregate_count_changes_value_not_rows
Table T1 6 rows; T2 aggregates `n = count()` per country; P draws n. Filter at T1 on `val > 1`: n changes, rows of T2 unchanged. The plot is "table changed" and "picture changed" while the T2 row count is the same. Assert the reported flags come from content comparison (D-0318), not row counts: wrong implementation compares row counts only and reports "unchanged" (P5 and silent).
Tests: P5 P7.

### C19 statistics_before_removal
A step z-scores `val` (value minus mean over the table) at T1 AFTER the audit step position? Audit steps go at the end of tier lists, so a filter at T1 runs after the z-score: the z of the kept rows is the z computed WITH the removed rows (statistics computed before the removal); a filter written at T1 of the SOURCE of the join (before the join) in another table... Case: A has recipe step `zscore val` in T1; audit filter (end of T1) removes the bad sample: rows 6->5, but z-scores of the 5 remaining still include the bad sample's val. Compared to a filter at the source table "before" the z-score: impossible by D-0146 (end of list only).
Expected: the test asserts and DOCUMENTS the outcome: the z-scores of the kept rows equal the baseline z-scores (unchanged). The dialog must say plainly, on the line, that values computed earlier in the tier (a z-score, a mean, a rank) still include the removed rows. OQ7: is this said anywhere? The decided rules do not say. A bad-sample removal that leaves its value inside the normalisation is a scientific pitfall, not a bug.
Tests: P4 P5 (the count is right, the science is not obvious).

## 6. Recode in place, plan blind

### C20 recode_value_before_after
A(sample_id, country): T1 recodes `country` "Norway" -> "NO" (replace). T2 of J (A join B) unchanged. One lineage: S(sample_id, country: Norway x3, Sweden x2, NO x1) -> T1 recode Norway->NO -> T2 join -> plot P.
Column `country`, the user views the table of P (values NO, Sweden) and types "NO".
Lines: `T1:S` (end of tier 1, after the recode: values NO there); the source before the recode is NOT a place (the audit step goes at the end of tier). So no place has "Norway" at all: a user who types "Norway" at any place removes 0 rows. The more dangerous variant: the recode in tier 2 (J) while T1:S holds "Norway": the user views P (value "NO"), types "NO": at `T1:S` the step `country != "NO"` removes 1 row (the original NO), at `T2:J` it removes 4 rows (3 recoded Norway + 1 original NO). Same name, same type: no note possible from the plan (F5).
Expected: both lines ticked; rows affected shown per line: T1:S "1 row", T2:J "4 rows"; plus a note "the number of rows differs between places; the values were changed by a step between" only if the app can know it: it can compare counts of matches. Test: the dialog shows 1 and 4 (counts computed by really evaluating each place's filter, not by a plan). Wrong: shows 4 for both (count at the start place copied), or shows nothing (P5), or shows the same "rows" number for tables. With the table-level count missing the user would believe `T1:S` removes the Norway samples; the test fails when counts are absent.
Also the result: the "after" rows at J when both are ticked = J loses the 4 rows (the T1 removal is a subset): check by H3.
OQ8: warn when counts differ between two places of one chain (the rule "a value that does not correspond one-to-one" D-0203 mentions it only for casts)?
Tests: P4 P5 P6 P7.

### C21 fill_missing_in_place
`val` decimal with 2 missing values; T1 fills them with 0.0 (same name, same type); T2 of a join nothing. The user at T2 (after the fill) types `val != 0.0`: removes the real 0.0 rows AND the filled rows. At T1 (the audit step is after the fill too, because the end of T1 is after the fill): same. So both places agree here. Make a variant where the fill is in a tier 2 step of a downstream table: T1 has missing, T2 has filled zeros. A filter `val != 0.0` at T1 removes 1 real zero (missing rows are dropped by F1 unless "keep missing" is ticked: expected removed = 1 real zero + the 2 missing unless ticked keep), at T2 removes 1 + 2 (filled) = 3. So the counts depend on the missing tick: matrix test: (missing tick on/off) x (place T1/T2): counts 1/3 (tick on), 3/3 (tick off). The test asserts all four.
Tests: P5 P7.

### C22 round_in_place
`val` 2.34, 2.36, 2.41; T2 rounds to 1 decimal: 2.3, 2.4, 2.4. Filter `val != 2.4` at T2 removes 2 rows; at T1 value 2.4 matches 0 rows (none equals 2.4): "matches no rows at this place" shown (not 0 silently ignoring). Float equality caveat: `2.4` typed as decimal at T1 and no row equal. Expected shown count at T1: 0 with the plain statement.
Tests: P5.

### C23 string_change_case_and_whitespace
`sample_id` values "S1", "s1", "S1 " (a stray space is stripped at ingestion with `strip: true` (F4), so only the case differs). T1 lowercases `sample_id`. Plot reads T2. The place before the tier-1 steps is not a place, so use this variant: lower-casing at tier 2 of J, the user views the plot table (lowercase) and types `s1`: T1 has "S1", T2 has "s1": a filter `!= "s1"` at T1 removes 0 rows (the case differs), at T2 removes both. The line at T1 must show 0 and the warning "no row matches here". Also asserts case sensitivity of the comparison (no silent case folding).
Tests: P5 P7.

## 7. Joins

### C24 join_key_one_column
A(sample_id, country), B(sample_id, lab); J = A inner join B on sample_id. Column `sample_id` in J: it is ONE column after the join (key) but exists in A and B. Lines: `T1:A` (reach A, J, plots: ...), `T1:B`, `T1:J`, "only P". A filter removing S3 at `T1:J` only: A and B keep S3; J loses it. At `T1:A` only: A loses S3, J (inner join) loses it too, B keeps it. Expected counts: A 6->5, B 6->6, J (inner) k-1.
Where B has S3 and A has not (a row only in B): the inner join drops it already; a filter at B removes a row that was not in J: the line for B shows "1 row in B, 0 rows in J's result" so the user sees the sample was not in the join.
Wrong: a line only for `T1:J` (P1: the key exists at A and B); or reach of `T1:A` forgets J (P3).
Tests: P1 P3 P5 P6.

### C25 join_clash_non_key_suffix
A(sample_id, val), B(sample_id, val); J = A left join B on sample_id: J has `val` (A) and `val_right` (B). Column `val` in J: back goes to A only. `val_right` back goes to B only. Test both lines sets and that the step written at B uses `val` (B's own name), not `val_right`; at J uses `val_right`. If the join sets `suffix: "_b"` the names change: parametrise the suffix.
Wrong: the line at B writes `val_right` and the build fails, or filters on A's `val`.
Tests: P1 P2 P4.

### C26 left_join_filter_before_versus_after
A: 5 rows sample ids S1..S5; B: S1..S3 with lab values X, X, Y (S4 and S5 have no match, missing lab after the left join). J = A left join B. Column `lab`, filter `lab != "X"` (keep missing: ticked "keep rows with no value" OFF vs ON).
 - Filter at `T1:B` (before the join): B loses 2 rows (S1, S2); J left join: still 5 rows, S1 and S2 now have missing lab. So J = 5 rows (S1 S2 emptied).
 - Filter at `T1:J` (after the join): removes rows with lab X: S1, S2 (2 rows); and with the missing tick OFF also S4, S5 (missing rows dropped by F1): J = 1 row (S3) with tick off; = 3 rows (S3, S4, S5) with tick on.
Expected lines: `T1:B` (reach B, J, plots) and `T1:J` (reach J, plots). Rows affected: B line "2 rows of B removed; J: 0 rows removed, 2 rows emptied" (the dialog must count both removed and emptied; D-0316 says rows affected: the test asserts J shows 5 -> 5), J line "2 rows removed (tick on) or 4 (tick off)". The two lines MUST show different counts. After both ticked (tick on): B 3->1; J: S1 and S2 have a missing lab after B's filter and the join (emptied); J's filter with the tick on keeps missing rows and S3 (Y) passes, so J keeps all 5 rows (tick off: J keeps only S3, 1 row). Expected row counts for all four combinations (B only / J only / both / none) x tick: 12 numbers; the test table is in the test file computed by the oracle.
Wrong: a walker that claims "filter on lab removes 2 rows" at both lines (P5), or says B's removal removes J's rows (P3 right but P5 wrong), or treats J's step as equal to B's (silent differences).
Tests: P3 P5 P6 P7.

### C27 inner_join_multiplies_rows
A 3 rows (S1, S2, S3); B(sample_id, mic) S1 x3 rows, S2 x1, S3 x2 (one sample, several tests, as in phenotypes). J inner = 3 + 1 + 2 = 6 rows. Filter on `sample_id != "S1"`: at `T1:A`: 1 row of A; J loses 3 rows; at `T1:B`: 3 rows of B; J loses 3; at `T1:J`: 3 rows. Rows affected shown per line in the units of that table: A "1", B "3", J "3". Also a filter on `mic` of a row of B: at B removes 1 row of B; J loses 1 row (inner) and A loses 0 rows. The test asserts per-line counts differ in this way. A reviewer question "how many samples" versus "how many rows": the dialog's number is rows of the table of the line; the count of distinct samples is not given (OQ9: should it be, for a long table?).
Wrong: reports "1 sample removed" for J, which is 3 rows.
Tests: P3 P5.

### C28 join_with_missing_keys
A.sample_id has a missing value (a row with no id) and B too. Polars join: missing keys do not match (default); the left join keeps the A row. A filter on `sample_id != "S1"` at J (keep missing off) removes the missing-id row too (F1). The test counts: the row with no id is removed at J, not at A where the same filter also removes it (F1) : consistent; but a "key filter at A" with the missing tick on keeps it.
Tests: P5.

### C29 named_join_takes_only_sources
D-0344: a join of a join is not built. A recipe where J2 lists J1 as an ingredient is refused/ not walked; test that the walker never returns a line for a join-of-a-join and that the load gate gives the plain refusal (not a silent skip of lines). The test builds the recipe with J2 reading J1 and asserts the refusal appears before the dialog is offered; if the recipe is accepted, every line is flagged. Wrong: silently walks only the first level (P1).
Tests: P1 P7.

## 8. Key removal (a sample)

### C30 remove_sample_from_all_tables
Sources: A(sample_id), B(sample_id), C(sample_id) all with S3; join J = A+B+C on sample_id (one join step with three ingredients, or J1 = A+B and a second named join J2 = A+C: allowed since each takes sources); plots P1 (J), P2 (C directly). Column `sample_id` in any view. "Remove from all tables" = automatic placement (D-0022): lines for `T1:A`, `T1:B`, `T1:C`, `T1:J`, `T1:J2`: all ticked. Expected: after, S3 absent from every table and plot table (oracle: no table of H1 contains S3); counts: each table -1 row (or -k rows with several tests).
Wrong: S3 survives in one table not listed (B, because B's key column is named differently, C31), or the reach double-counts C (a source of two joins).
Tests: P1 P3 P6.

### C31 key under another name
B's key is `isolate` renamed to `sample_id` in T1:B (original_name) or the join uses `left_on` = `sample_id`, `right_on` = `isolate_id` (B keeps `isolate_id`). The user picks `sample_id` at J (which has `sample_id` from A and the B key column merged away by the join: a join with left_on/right_on keeps only the left name). Expected: the walk must go back through the join key mapping: `T1:B` is a line with the column `isolate_id` (note "called `isolate_id` here: the join key of B"), ticked. The filter written at `T1:B` is on `isolate_id`. Not offering this line leaves S3 in B and in any plot reading B directly: the user "removed S3 from all tables" but B still has it (silent partial removal, P1).
Variant: B has BOTH `sample_id` (a different field, e.g. a biosample id with the same name) and `isolate_id`, joined on `isolate_id = sample_id of A`: then B's `sample_id` is a different column: not offered (P2).
Test also the case where the key is renamed AFTER the join (J renames sample_id->id): the walk from `id` goes back to `sample_id` at the join key.
Tests: P1 P2 P4 P6.

### C32 key not on every table
D has no sample column (a lookup of antibiotics). The key removal must not touch D; D appears in no line; but plots reading D with the join to A... they read D alone, reach 0. Test that D unchanged (P6) and not in the "remove from all" summary.
Tests: P2 P6.

### C33 key across a pivot/unpivot: see C37.

## 9. Missing values

### C34 missing_tick_matrix
For every operator the audit filter offers (equal, not equal, less than, greater than, in list, not in list, is missing, is not missing, contains) on a column with missing values: expected rows removed with tick on and off, computed by the oracle with explicit null logic. Polars drops missing in `!=` (F1); the tick "keep the rows with no value" must make the generated step `(col != v) | col.is_null()`. Row table: column [1, 2, 3, None, 3] and v = 3: `!=`: tick off removes rows with 3 (2 rows) and the missing row (1) = 3 removed, 2 kept; tick on removes 2, keeps 3. The test is parametrised on each operator and asserts the removed count equals the oracle's.
Wrong: tick ignored; tick default applied silently; the step written without the missing clause when the tick is off yet the dialog's count says "2 rows" (P5).
Tests: P5 P7.

### C35 join_creates_missing_downstream
As C26. A line pair: B has `lab` with no missing values, J has missing `lab` (S4, S5). Filter `lab != "X"`: at B: removes 2 rows with no missing involved; at J: the missing rows depend on the tick. Expected: the line at J shows the number of rows with no value at this place ("2 rows with no value here") because the plan cannot know; test asserts that number is shown (not found in the plan: from counting).
Tests: P5.

### C36 missing at one place, none at another due to fill
As C21. Combined with the tick. Test that the tick is per filter (D-0 tick is per filter, not per line): the same tick applies at every place and the counts differ per line. OQ10: should the tick be per line? The owner decided per filter.
Tests: P5.

## 10. Unpivot and pivot

### C37 unpivot_column_becomes_values
A wide(sample_id, amp, cip, tet) (resistance per antibiotic as columns, 0/1), T1:A unpivot on [amp, cip, tet] to (antibiotic, resistant). Plot P reads the long table. The user picks `antibiotic` and removes "tet" (all tet rows). `antibiotic` is a NEW column: its values were column names of the source. Lines: `T1:A` (the long table; note "created here from the columns amp, cip, tet"), no line before. Filter `antibiotic != "tet"` removes 1/3 of rows. Alternative the user wants to drop the column `tet` from the wide table: at T1 the wide table only exists inside the tier (before the unpivot): the audit step runs after the unpivot where `tet` is gone: no place offers `tet` as a column (grey: "turned into values of antibiotic here" at the long table); the user has to filter `antibiotic`. Test: user starts at the long table with `resistant`: lines: `T1:A` only. User picks `amp` in a view of the wide source? There is no such view at the end of tier 1 (A has only the long table). If the recipe has another plot reading the wide version via another table, `amp` is offered there.
Also sample key: `sample_id` is kept by unpivot; the removal of S3 works at T1:A (long: 3 rows per sample): rows affected = 3 per sample.
Wrong: offers `T1:A` for column `amp` (the plan of the long table has no `amp`: no, plan-based finds none; a rule-based would). Wrong the other way: the long table has `antibiotic` and the walker claims it exists at the wide source (P2).
Tests: P2 P4 P5.

### C38 pivot_values_become_columns
A long(sample_id, antibiotic, resistant) -> T1 pivot index sample_id, columns antibiotic, values resistant: wide with columns `amp`, `cip`, `tet` (names depend on data: engine reads rows). The user at the wide table picks `amp`: back to `resistant` of the long table filtered on antibiotic == amp? There is no single column in the source called `amp`: it is a set of values of `antibiotic`. Expected: the line for `amp` exists only at the wide table (and downstream); the note says "created here by a pivot from the values of `antibiotic`"; the line count for the long source is NOT offered as "amp" (P2). The user picks `antibiotic` at the long table: lines `T1:A` (long) and the wide table (reach through the pivot): at the wide table `antibiotic` does not exist (its values became column names): grey with reason "became the columns amp, cip, tet". The row removal at the long table of `antibiotic != "tet"` makes the pivot lose the `tet` column; the dependants (plot drawing `tet`) fail: the plot must be flagged "broken" before the confirm (plot changed: picture). Cost: the plan of the pivot reads rows: test that the dialog time/behaviour is correct but no other place reads rows (count reads).
Also: a pivot with a new value appearing after a filter removal change (the column set changes). The test asserts that the list of columns at the pivot place is computed on the audit copy too: the plots that used a column that vanished are listed.
Tests: P1 P2 P3 P4.

## 11. Plots

### C39 plot_own_tier3
P1 reads T2:J and has its own tier 3 steps (filter val>0, a rename `country` -> `origin`, a drop of `lab`). P2 reads T2:J, no tier 3 steps. Column `country` chosen in P2's table. Lines: `T2:J` or lower (lowest table with steps: T2:J if it has steps; reach 1 table, 2 plots), `T3:P1` is its own table (distinct since it has steps: the line is `T3:P1` with `origin` and reach (0, 1): note "called `origin` here"); "only P2" (0, 1); "only P1" is the same place as `T3:P1`: the line "only this plot" for a plot with its own tier 3 steps IS the tier 3 line: one line, not two. The test asserts there is no duplicate line for P1. (Decided D-0346: "also a line for one plot only: the audit copy gives the plot its own audit steps at tier 3 even when the recipe has no tier 3 steps": for P1 the audit steps go in the same tier 3 list.)
Expected counts: T2:J step: removes k rows from J, P1 (its steps filter val>0 first, then the audit step on `origin`?), P2. At `T3:P1` the audit step on `origin` removes the same k rows IF the tier 3 steps did not change the rows; with the tier 3 filter `val>0` removing rows with the country first, fewer rows (the rows already gone). Rows affected per line: J line k_J rows; P1 line k_P1 <= k_J; P2 line k_J... Test the numbers by the oracle.
Wrong: the line for P1 is missed because the plot has steps (a plot that has its own tier 3 and also appears in the reach of J); P1's step is written at the start instead of the end of tier 3 (the drop `lab`: no effect).
Tests: P1 P3 P5 P6.

### C40 several_plots_one_table
P1, P2, P3 all read T2:J without tier 3 steps. Lines: `T2:J` (reach 1 table, 3 plots) plus "only P1", "only P2", "only P3". With all four ticked, the step is written once at T2:J and once at each plot: 4 steps; each plot built with two identical filters (redundant); the rows of every plot equal the rows with only `T2:J` ticked. With only "only P2" ticked: J unchanged, P1 and P3 unchanged (P6), P2 loses rows. Flags: "table changed" for P2 only; "picture changed" for P2 if the aesthetics use rows.
D-0198 cautions "an earlier place covers the later ones": the dialog marks the later ticked lines "covered by `T2:J`" only if the column is unchanged between (here the test asserts it is marked; and in C06 where the column is renamed between, the marking is "covered" too (same rows) or not?) OQ11: whether "covered" is shown for the same rows even when the name changes.
Tests: P3 P5 P6.

### C41 plot_reads_t1_directly
A plot of a source table with no join; its table is `T1:A` (reach (1,1)); "only this plot" differs from `T1:A` only if another plot or join reads A. If P is the only reader of A: lines `T1:A` (reach (1,1)) AND "only P" with the same effect: duplicates in effect. Expected: both listed, and a note on `T1:A` "only this plot reads it" is NOT required; test records what is shown and that the ticked result (both ticked) writes two steps whose effect is identical (redundant but harmless). OQ12: should "only this plot" be hidden when it equals the table line in effect?
Tests: P2 P3.

### C42 plot_flags_table_versus_picture
Plot P draws `val` against `year` only; the filter at T1 on `country` removes rows (table changed, picture changed: points disappear); a drop of `lab` (not drawn): table changed, picture the same (D-0318); a filter that removes only rows with `val` missing: the plot's rows change but the picture (a bar of means that skips missing) the same? the "picture changed" must mean what the drawn data would be: compare the plot's own used columns with na dropped or not? OQ13. The test asserts the flags on the three cases and that a case with no change (the filter matches 0 rows here) reports neither.
Tests: P3 P5.

## 12. Order and repetition

### C43 same_step_at_table_and_dependant
Ticked at `T1:A` and `T1:J` and `P` (C40). Result rows equal to `T1:A` only. The count "rows affected" at J when T1:A is also ticked: 0 additional rows; the dialog must show the count per line for the line alone AND the extra rows beyond the lines above it? Test the exact definition: choose "rows affected by this line alone, given the other lines are unticked" and "given the earlier lines ticked": OQ14 (D-0316 does not say which). Assert the numbers are stable when ticking more lines (the number on a line must not change silently when another line is ticked, or it must say that it does).
Wrong: counts added up: total rows removed claims 3+3+3 = 9 (P5).
Tests: P5 P6.

### C44 step_removed_then_added_again
Open the dialog, tick, apply with a reason; a second time the user removes the audit step (from the log), adds it again. Expected: the recipe's `audit_steps` after the second addition equals the first (same step, new audit id? one new id: ids are never reused: assert); the build equals the one of the first time; the original `steps` are byte-identical (H5). Wrong: the duplicate step appears twice; the first step stays after removal; an id collides.
Tests: P6 P7.

### C45 two_audit_steps_same_column_different_places
Step 1: `year != 2022` at `T1:A`; step 2: `year != 2023` at `T2:J`. Final rows by oracle; the dialog of the second action shows lines whose "rows" are counted on the audit copy including step 1 (the second dialog opens on the current audit copy): the counts at J are the ones after step 1. Test: open the second dialog and assert 2023 count excludes rows already removed. And the line list of the second dialog is the same as the first (no new places).
Tests: P5 P6.

### C46 second_step_on_column_dropped_by_first
Step 1 audit: drop `lab` at `T1:B`; step 2 (later dialog): a filter on `lab` at `T1:J` (the user views J: the column exists in the old build but is gone now): the dialog opens on the audit copy: `lab` is absent in J, so no line. A step 2 on `lab` forced from an old view: the build must fail with the plain message (D-0176), not silently pass. Also the reverse: filter on `lab` first, then drop at the same table later: the drop after the filter: allowed, rows as the oracle.
Tests: P2 P7.

### C47 audit_steps_end_of_tier_after_recipe_steps
The recipe's own tier 1 has `head(3)` (keep the first 3 rows), the audit step goes after it: removing S2 (in the head) leaves 2 rows, while the unhead rows are not brought in (the sample removed leaves a hole). A removal at the source before the head is NOT possible (D-0146). Expected: A has 6 -> 3 (baseline) -> 2 (audit). Dependants see 2. Document: a removal of a sample does not "refill" the sample size; the dialog's count says "1 row removed at T1:A" and the final table has 2 rows. A recipe step like `sample(n=3, seed)` or `unique` or `sort + head(3)`: the audit step after them. Document in the list of consequences: the earlier filter would give different rows (the 4th row enters the head): the test asserts and records the wrong expectation "filter before head": it is not offered. OQ15: is this told to the user.
Tests: P4 P5.

## 13. A place the engine cannot answer

### C48 data_file_missing
Two sources: A (file present), B (file renamed away). Lines: `T1:A` ticked and correct, `T1:B` grey "the data file of B is missing", J (A join B) grey ("cannot be built: B missing"), plots reading J grey; "only P" lines for P reading A stay ticked. Reach of `T1:A` still counts J and its plots (the dependants exist even if the app cannot answer for them). The result when ticking only `T1:A`: A changes; J cannot be built, so "rows affected" for J says "not known". Assertions: the lines that are answerable are IDENTICAL to the baseline run when B is present (compare field by field); the grey lines carry a reason; the count of lines found, "N found, M cannot be answered" shown (D-0195 "the dialog says how many nodes were found"). Wrong: the missing file raises and the entire list is empty (silent no list), or the grey place is dropped from the list silently (P1).
Tests: P1 P3 P7.

### C49 step_fails
A tier 1 step fails on the data (e.g. cast of "abc" to int strict, or a step with a column that does not exist): the table fails at that place: lines at and below it grey with the step's name, file and line (D-0342) and the reason; other tables normal. The failing step upstream of the chosen column: the start table cannot exist: the dialog cannot be opened at all (the user views a table that exists, so the failing table is not the start). Test: one table fails, the user starts from a healthy table whose join includes the failing table: the line for the failing table grey; the join J grey; but the other plot reads A only: ticked.
Tests: P1 P2 P7.

### C50 pivot_place_cost
A recipe with one pivot: the plan read rows only there. A test counts file reads: all places not downstream of the pivot are answered without reading rows (a read counter or a poisoned file after the schema read). Tests: P7 (the decided "no rows read" is observable).

## 14. Width: real recipes

### C51 demo_abromics_sample_id
Recipe `config/data_analysis_recipes/pipelines/demo_abromics.yaml` (108 places per the owner's count; the older map said 85 places). Expected line count for `sample_id`, computed independently of the app:
 Method (the oracle, no walker code): (1) run the whole recipe once eagerly (`collect()` of every tier-1 end, every join end, every plot table) and record, for each table, its real column names and types; (2) list the dependency edges by reading the YAML: each join's `ingredients`, each plot's `target`; (3) a candidate place for a table is a line iff the table's final column set contains the column that traces to the origin: for the key `sample_id` use the traced identity (rename-aware) by running a "marker" run: put a unique marker value in the `sample_id` column of each source CSV (copy of the data in a scratch folder: `sample_id` + `__MARK`), re-run, and a table holds the column iff some column of it contains marked values; this finds identity through renames and ignores same-name columns of other origin. (4) distinct tables: group tables by the sequence of the parquet equality (two places with identical content and same lineage collapse); count lines = number of distinct tables with steps + the number of plots (the "only this plot" lines) for tables read by more than one plot; reach = number of downstream tables and plots in the YAML graph that carry the marker.
 Expected numbers are printed by the oracle and stored as a golden file in the test; the test compares the app's lines to the oracle's by place and reach; a list of the places NOT lines (tables where `sample_id` is absent) must also match (P2).
Tests: P1 P2 P3.

### C52 demo_column_of_one_source
A column only in one source (e.g. `sequence_type`, if only one source has it): lines = the tables downstream of that source that carry the marker; the other sources not offered. Same oracle with the marker in that column only; additionally the "drop" variation: a column that is carried by only one source and dropped by one plot's tier 3: reach counts the plot (dependant) but the plot's own line is grey/absent (C13).
Tests: P1 P2 P3.

### C53 figshare_sample_id
`figshare_integration.yaml` with three sources (`fg_metadata`, `fg_phenotypes`, `fg_genotypes`) joined; the long phenotype table has several rows per sample (one row per sample and antibiotic test): the key removal affects many rows: expected rows affected per line = the number of rows with this sample id in each table, computed by the oracle from the TSV (`libs/transformer/tests/data/fg_*.tsv`) with a plain `pl.read_csv(...sep tab)` counts. The test removes one sample and asserts each table, each join and each plot loses exactly its oracle count and no other row. Also source `strip: true` and `null_values: []` are verified: a sample id with no value is the empty string or missing? with `null_values: []` an empty field is the empty string, NOT missing, so the tick "keep rows with no value" does not apply to empty strings: the dialog's missing count says 0 for the text column where the data has empty strings: the user is told "empty text is not missing" (OQ16).
Tests: P1 P3 P5 P6.

### C54 figshare_column_of_one_source
`fg_metadata` host species column: only metadata has it; after the join it exists in J; the reach: plots reading J and plots reading metadata directly; the oracle by the marker method. Filter "remove host == Pig" at each line: the rows of the phenotype long table lose the rows of the pig samples only through the join (when the join is on the sample key: the long phenotype table has no host column: it is not a line (P2) but the J line removes pig rows of J (that includes the phenotype tests): a reviewer asks "how many tests were lost": the line shows J rows (tests), not samples: see C27.
Tests: P1 P2 P5.

## 15. Extra cases found

### C55 reach_counts_dependants_without_the_column
(From C13/C17.) The reach of a line counts tables and plots that depend on the place even if the column is absent there. Check against the YAML graph for an aggregated table (column gone after group_by). Wrong: reach = number of lines (holders only). Tests: P3.

### C56 same_table_read_by_two_joins
A is an ingredient of J1 (with B) and J2 (with C). `T1:A` reach = A, J1, J2 and their plots; J1 and J2 independent: a filter at `T1:J1` does not touch J2 (P6). The reach is a graph count with no double counting (a plot reads one table; a join of joins is not built, C29). Tests: P3 P6.

### C57 empty_result_zero_rows
A filter that removes every row at a place: expected "all rows removed" warning with the table name; the downstream join and plot yield zero rows; flags "picture changed" (empty plot). Plot build of an empty table must not crash the dialog; the line shows "n of n rows". Another: a filter that matches 0 rows (value absent): "no row affected here" shown and nothing is claimed. Wrong: 0 shown as "unchanged" with no explanation, or the dialog lets her confirm an audit step that removes all rows with no warning. OQ17.
Tests: P5 P7.

### C58 ties_and_order_dependent_steps
A step `unique(subset=[country])` keeping the first (or `sort` then `head`) in the recipe with ties in the sort key: the kept row depends on the original row order. A filter at T1 before... audit is after; but a filter at T1 of a SOURCE of a join changes the row order of the join output? Test: a join on a key with ties (two B rows for one A row) with the engine's join order: an audit filter at B changes which of the duplicates remains first for a subsequent `unique`: rows after are determined; the oracle must match including the CHOICE of kept row; the test runs twice and compares (same data and recipe give the same rows). P7 reproducibility: two identical runs give identical tables including the order.
Tests: P6 (determinism).

### C59 sample_ids_case_and_whitespace
Values "S1", "s1", "S1 ". Ingestion `strip: true` removes the space (F4); case stays: "S1" and "s1" are two samples. The dialog value typed "S1" removes 1 row; the user must not be misled that "S1 " matched. Test: the dialog lists the distinct values it matches (exact string comparison), and no silent normalisation (lower or strip) in the written step: the step file holds exactly what was typed. Where a table is read from a stored parquet with unstripped ids (a table cached before a change), a mismatch: the tables are rebuilt by key.
Tests: P5 P6.

### C60 value_list_partial_match
Several values removed (`is_in [S1, S9]`) where S9 exists only at some places: the line says "S9 matches no row here"; no error.
Tests: P5.

### C61 type_float_integer_key
`year` is stored as float 2022.0 in a CSV with `2022` text: the reader makes it int or float depending on the file: the same column is int at A and float at B after the join (a key joined int-to-float fails or casts). Test that the lines note "decimal here, whole number at your place" and the value is written as `2022.0` / `2022`.
Tests: P4.

### C62 walk_idempotence_and_stability
Run the walk twice, and after a no-op round trip (add the step and remove it): same lines, same order, same reach. Run it on a recipe loaded from a session restore: same. Property test: for random small recipes (generated from steps: rename, cast, drop, filter, join, group_by), the walker's lines equal the marker-oracle's lines. This is the fuzz version of everything above; P7 by mutants.
Tests: P1 P2 P3 P7.

---

## Order to build first (the ten that catch a scientifically wrong result)

1. C26 left join filter before versus after (counts differ; removed versus emptied; missing tick).
2. C20 value recode in place (plan blind; counts per line 1 versus 4).
3. C07 and C14 two different columns with one name (false place: a step on the wrong table).
4. C31 key under another name (a sample not removed from all tables, silent partial removal).
5. C08 cast on one path (type per place; build does not fail; value correct).
6. C13 drop on one path plus the reach counting dependants (plot silently unchanged).
7. C17 aggregation keeping the name (rows versus groups; value change).
8. C34 missing-value tick matrix over every operator (F1 drops missing).
9. C48 data file missing (grey lines, the rest identical to the baseline, count shown).
10. C51/C53 real recipes with the independent marker oracle (width, golden counts), run with the mutant checks of H4.

Close behind: C06 rename back, C37/C38 unpivot and pivot, C19 statistics before removal.

## Open questions for the owner (the decided rules do not say)

- OQ1. When a column is renamed and later renamed back to its first name, is it one column with one set of lines (the walk by identity), or does the later same-name column count as new?
- OQ2. When a value cannot be written at one place (2.5 into a whole-number column), is the whole dialog blocked, only that line blocked, or that line turned grey with the reason?
- OQ3. May a filter value be a date, and how is it typed at a place where the column is a date?
- OQ4. A plot whose own recipe dropped the chosen column: is its "only this plot" line grey with the reason, or absent from the list?
- OQ5. When a drop (or a removal) would break a later recipe step or a plot that draws the column, must the dialog list that plot as broken before the confirm?
- OQ6. A computed column (a mean after a grouping, a column created by a new-column step) has no earlier place: does the dialog say "computed here" and offer only places from there down?
- OQ7. Must the line say that a value computed earlier in the tier (z-score, mean, rank) still includes the removed rows, because audit steps go at the end of the tier?
- OQ8. When the same value matches a different number of rows at two places of one chain (a recode between), is a warning required (D-0203 names only casts)?
- OQ9. For a long table (several rows per sample), must the dialog also give the number of distinct samples, besides the number of rows?
- OQ10. Is the "keep the rows with no value" tick one choice per filter (decided) with the same effect at every place, and what is its default?
- OQ11. Is a later line shown as "covered by the earlier place" when the column was renamed between (same rows, other name)?
- OQ12. Is the line "only this plot" shown when it has exactly the same effect as the table line (a plot that is the only reader)?
- OQ13. Does "picture changed" mean a change in the rows the plot draws (after its own handling of missing values), or any change in the plot's table columns it uses?
- OQ14. The rows affected on a line: counted for that line alone, or after the other ticked lines above it, and does it change when another line is ticked?
- OQ15. Must the user be told that a removal after a `head`, `sample` or `unique` of the recipe does not bring other rows in (the recipe's own steps run before)?
- OQ16. An empty field is empty text (not missing) when the source has `null_values: []`: is the "no value" count told to the user as such?
- OQ17. A step that removes every row of a table: warning, block, or just the count?
