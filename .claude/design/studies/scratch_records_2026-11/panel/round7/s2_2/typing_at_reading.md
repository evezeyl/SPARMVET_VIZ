# S2-2: values that cannot be typed, and what reading does (investigation, 2026-11-16)

Nothing was built or changed. Evidence marks: **RUN** = I ran it on the code at HEAD `3d69e14f`. **READ** = I read it in the code or a record.
Scripts and raw outputs: `tmpAI/panel/round7/s2_2/` (`a_reading.py`, `a_more.py`, `a_checker.py`, `a_parquet.py`, `b_scan.py`, `b_matrix.py`, `b_real.py`, with `.out` files).

Words used once: "reader" = `apply_declared` in `libs/ingestion/src/ingestion/declared.py`; the file is read as text, then each column is converted to its declared type. "Checker" = `check_recipe`, which judges the recipe file. READ: the checker never opens a data file (its own header says so, `recipe_check.py` line 3).

## Short answer to Eve's question

- A text such as `ABC` in a column declared `Int64` (a Year) cannot get past reading. RUN: the build stops and names the column and the value. So "the value is ABC at a Year column" cannot happen.
- What CAN happen is different: the recipe itself changes the type of a column between two tables. Then a value typed for one table (the number 2022) does not fit the other table (the text "2022"). RUN on shipped recipes: this exists in 2 of the 43 recipes that build (section B).
- The rule S2-2 is still needed, but only for that case, and it is small (section C).

## A. What reading does with a cell that does not fit (RUN, through `DataIngestor.ingest`, the engine's reader)

### A.0 SILENT conversions (reading accepts, no message). Most serious first.

| # | What the data holds | Declared | What you get, silently | Does the checker catch the declaration? |
|---|---|---|---|---|
| 1 | `1.234` | `Decimal` with no `precision`/`scale` | `1` (scale 0: rounded to a whole number; `2022.7` gives `2023`) | No (RUN: "NO PROBLEM") |
| 2 | `1.234`, `1.235`, `-1.235` | `Decimal` precision 5, scale 2 | `1.23`, `1.24`, `-1.24` (digits beyond the scale are rounded away) | not applicable (valid declaration) |
| 3 | `1e400`, `1e40`, `70000` | `Float64`, `Float32`, `Float16` | `inf` (a number too large becomes infinity, not an error) | No |
| 4 | `0.1234567890123`, `123456789` | `Float32` | `0.12345679104...`, `123456792` (about 7 digits kept) | No |
| 5 | `9007199254740993` | `Float64` | `9007199254740992` (whole numbers above 2^53 lose the last digit) | No |
| 6 | `1e-400`, `1e-9` | `Float64`, `Float16` | `0.0` (underflow to zero) | No |
| 7 | `03/05/2022` | `Date` with no `format` | 3 May 2022 (day first is guessed: a month-first file is read wrongly, with no message, when every date in it is ambiguous. If the first value is `12/31/2022` the guess fails and the value is named) | No: `format` is optional |
| 8 | `01/01/68`, `01/01/69` with `%d/%m/%y` | `Date` | 2068 and 2069 (two-digit years read as 20xx) | No |
| 9 | `2022-03-06` | `Datetime` | `2022-03-06 00:00:00` (midnight added) | not applicable |
| 10 | `10:00:00.123456789` / `.123456` | `Datetime` unit `us` / `ms` | `.123456` / `.123` (digits beyond the unit are cut) | No |
| 11 | `2022-03-05T10:00:00Z` | `Datetime` with `time_zone: Europe/Oslo` | `11:00` Oslo (converted; right in itself, but the file text is not what you see) | not applicable |
| 12 | `007`, `0100`, `+5`, `-0` | `Int64` | `7`, `100`, `5`, `0` (leading zeros are lost: an ID kept as a number) | not applicable |
| 13 | `nan`, `NaN`, `inf`, `Infinity` (any case) | `Float64` | read as the numbers NaN and infinity (not missing, not refused) | not applicable |
| 14 | a cell with one space, `strip: true` | `String` | empty text `''`, while a truly empty cell is a missing value: two kinds of "empty" in one column | not applicable |
| 15 | the word `NA`, level of the Enum | `Enum` with a level `NA` and `null_values: [NA]` | the level is read as MISSING; the level `NA` is lost | No |
| 16 | `NA ` (trailing space), `strip: true`, `null_values: [NA]` | `String` | missing (strip runs first; by design, listed so it is known) | not applicable |

Notes on the table. #7 and #8 follow Polars' own date guessing; the module text says "nothing is hidden: no guessed type" (READ, `declared.py` lines 3 to 6), but a missing `format` is a guess. #1 is the worst because the declaration is valid Polars and reads as a plain whole-number column.

By design and documented (READ, `declared.py` lines 5 to 6): an empty cell is a missing value in every type (RUN: `Int64`, `Float64`, `Boolean`, `String`, `Categorical` all give a missing value).

### A.1 Cases that STOP the build, and what the message says (RUN)

The usual message (quoted exactly):
`Data schema 't': values that do not fit the declared type: column 'x' (Int64): 'ABC'`
Tip: `Correct the data, declare the type the data really has (Float64 for decimals), or list the word in null_values if it means missing.`

What it names: the schema id, the column, the declared type, up to 3 different bad values. What it does NOT name: the file, the row numbers, how many cells are bad (RUN: 5000 bad cells give the same 3-value message). The tip is the same for every type ("Float64 for decimals" is also said for a Date).

| Cell | Declared | Result |
|---|---|---|
| `ABC` | `Int64`, `Float64`, `Decimal` | message above, value named |
| `2.5`, `2022.0`, `1e3`, `1,5`, `1,000` | `Int64` | message above, value named |
| `1,5` | `Float64`, `Decimal` | message above, value named (comma is not a decimal sign) |
| `99999999999999999999`, `300` in `Int8`, `32768` in `Int16`, `3000000000` in `Int32`, `-1` in `UInt8/64/128` | integer types | message above, value named (a number too large is an ERROR for integers; for decimals it is the silent #3) |
| `1234.5` | `Decimal` precision 5 scale 2 | message above, value named |
| `NA`, `n/a`, `-` | `Int64` | message above, value named, unless listed in `null_values` (then missing) |
| a space | `Int64` | message above; the value shown is `''` (strip on) or `' '` (strip off) |
| `yes`, `1`, `0`, `T`, `F` | `Boolean` | message above, value named; only `true`/`false` in any case are accepted |
| a value not in the list | `Enum` | message above, value named. `r` for level `R` is refused (case matters) |
| a date in another format | `Date` with `format` | message above, value named |
| `2023-02-30` as the FIRST non-empty value | `Date` | raw Polars text only: `Failed to read 't.tsv': ComputeError: could not find an appropriate format to parse dates, please define a format` and the tip "Check that the file is a valid tab-separated file". No column, no value, no row. The same value after a good one gives the normal message with the value named |
| `2022` or `2022-03-05 10:00:00` (Date), `ABC` (Datetime), `25:00:00` or `24:00:00` (Time), as the first value | `Date` / `Datetime` / `Time` | the same raw text |
| `2022-03-05T10:00:00Z` | `Datetime` with no `time_zone` | raw Polars text ("a time zone is part of the data ... Give a format s..."), no column named |
| `2022-03-27 02:30:00` | `Datetime` zone Europe/Oslo | raw Polars text (that time does not exist), no column named |
| a file in `.parquet` with an `Int64` column | any declared type | raw `SchemaError: expected String, got i64` (a typed Parquet column cannot be read by the reader) |
| a declared column missing from the file | any | a clear message: names the dataset, the column, the headers expected, what to do (this one is good) |

Parameter mistakes the checker does NOT catch (RUN: `a_checker.py` says "NO PROBLEM", then `a_more.py` shows the engine):
`Date` with `format: %Q` -> the engine says the DATE does not fit (misleading: the format is wrong); `format: 123` -> raw `TypeError`; `time_zone: Mars/Base` -> raw Polars text with a hint; `time_unit: x` -> raw `ValueError`; `Decimal` `precision: a` -> raw `TypeError`; `precision: 100` -> raw error; `scale` larger than `precision` -> raw error; `Enum` with a repeated level -> raw `ValueError`.
Caught by the checker (RUN): a wrong type name (`Year` gives FD02 and lists the allowed names; `Integer` says "write Int64"; `int64` lower case lists the names without saying which), an `Enum` with no levels, a `null_values` that is not a list.

### A.2 What the checker says about data (RUN + READ)
Nothing. A recipe whose data holds `ABC` in an `Int64` column passes the checker with no message, and fails only when the data is read. This is by design (the checker "never reads the data files").

### A.3 One record is out of date (READ)
`recipe_format_spec.md` section 7.4 says the declared type is "given to the reader (`schema_overrides`), which fails strictly". The code reads everything as text first and converts with its own check (`declared.py`). The messages differ from the ones in the spec ("could not parse `2022.0` as dtype `i64`").

## B. The case S2-2 was written for

### B.1 Can it happen with a recipe that passes the checker? Yes, when the recipe changes a column's type between tables.

I built every table (tier 1 and tier 2) of all 50 shipped recipes with the engine and compared the type of same-named columns (RUN, `b_scan.py`). The 50 are 34 gallery examples and 16 recipes in `config/data_analysis_recipes` (7 pipelines, 4 templates, 4 retest, 1 experimental). 43 built; 7 did not (2 are broken on purpose, 3 templates need data that is not shipped, 1 empty, 1 whose include path my scan could not follow: `1_Abromics_general_pipeline`, which has no `polars_cast` step, READ).

The 34 gallery examples have one table each: no case.

Same name, different declared or resulting type, in tables of ONE lineage (one table feeds the other):

| Recipe | Column | Where it is what | Why |
|---|---|---|---|
| `2_test_data_ST22_dummy` | `Year` | `metadata_schema`: Float64 -> `AMR_Profile_Joint` and `Plasmid_Profile_Joint`: String | the join does `polars_cast` Float64 to Int64 to String, to get "2022" on a discrete axis (comment in the recipe says so) |
| `demo_abromics` | `year` | `metadata_schema`: Float64 -> `demo_join`: String | the same two casts |
| `1_test_data_ST22_dummy` | `L50` | `Quast` and `QC_Reads_Anchor`: Float64 -> `QA_L50_integer`: Int64 | `polars_cast` to Int64 (a test table). Number to number: a number value is accepted on both (below) |

Not one lineage (so not this case): `1_test_data_ST22_dummy` `value` is Float64 in `Quast_with_metadata` and String in `Summary` (no table feeds the other).

So: 3 of 43 recipes. 2 of them (`Year` / `year`, both written by the maker on purpose) are the number-to-text case that fails. READ: the shipped `Year` is declared `Float64`, a year as a decimal; that is why the maker needs the two casts.

### B.2 What the engine does today with one small example (RUN, `b_real.py`, real recipe `2_test_data_ST22_dummy`)

The audit step `modif_filter` on `Year` equal to 2022, written at different nodes:

| Value | Node | Result |
|---|---|---|
| number 2022 | `metadata_schema` (Float64) | applied: 9 rows |
| number 2022 | `AMR_Profile_Joint` (String, after the casts) | REFUSED: `step modif_filter, column 'Year': The value 2022 is a number, but this column holds text (String)`; tip "write the value as text, in quotes"; the message does not name the table |
| text "2022" | `AMR_Profile_Joint` | applied: 13 rows |
| text "2022" | `metadata_schema` (Float64) | REFUSED: `The value '2022' is text, but this column holds decimal numbers (Float64)`, wrapped as "Dataset 'metadata_schema' could not be loaded" |

The recipe checker (RUN): it judges a wrong-typed value at the table that declares the column (code ST12 on the text "2022" at `metadata_schema`) but says nothing for a step written AFTER a `polars_cast` (it stops judging after a step that can change a column; READ `recipe_check.py` `filter_value_problems`). So the second row passes the checker and fails when the data is built.

### B.3 The filter functions, value type against column type (RUN, `b_matrix.py`, full table in `b_matrix.out`)

`modif_filter` (the recipe action) is strict. In short for `eq`:
- number on a number column (`Int64` or `Float64`): applied. A decimal on a whole-number column is accepted: `8.5` on `Int64` keeps no row and says nothing (RUN: 0 rows, no message).
- text, date or true/false on a number column: refused in plain words with a fix.
- number, date or true/false on a text column (`String`, `Enum`, `Categorical`): refused in plain words.
- text on a date or true/false column: refused.

But the two other callers do NOT pass `strict` (READ: `viz_factory.py` line 258 and `app/modules/t3_audit_engine.py` line 325, the HOME plot and table). RUN of the same function without strict:
- text "2022" on a number column: CONVERTED and applied (silent conversion, which ADR-104 point 7 says the engine does not do).
- number 2022 on a text column: raw Polars error `ComputeError: cannot compare string with numeric type (i32)`.
- true/false on a text column: applied, keeps 0 rows, no message.
- date on a text column: raw `InvalidOperationError`.
So the "plain error for a value of another type" of ADR-104 point 7 holds in the recipe action and the checker, not yet in the HOME plot and table paths (the records say the typed-values work was built on a branch; at HEAD these two calls are still without `strict`; whether HOME's panel stops such a value before this point I did not run).

## C. My answer to her question, in plain words

1. **When can it happen?** Only when the recipe itself changes the type of a column along a lineage (a cast, or a column rebuilt by a step), and the user ticks two nodes where the column has a different type. It cannot happen inside one table, because reading refuses a cell that does not fit its declared type (A.1). The value `ABC` on a Year column cannot happen at all.
2. **How often in shipped recipes?** 2 of 43 recipes that build (`Year` in `2_test_data_ST22_dummy`, `year` in `demo_abromics`), plus 1 number-to-number case that is harmless. It is rare but it is the main example of a year, a column that audit filters will use.
3. **Is S2-2 still needed once reading captures every type error?** Yes, but only for that case. Reading cannot decide it, because both tables are read correctly; the difference comes from the recipe's own cast. The rule is small: for each candidate node, take the column's type from that node's table, and if the value does not fit it, show the line with the error ("the value 2022 is a number but this column holds text at AMR_Profile_Joint") and do not allow the tick. The code for the test exists (`check_filter`).
4. **What reading still owes her instruction ("capture the errors of Polars and the type errors at reading").** The ones in the first part of A.0 (silent) and the raw Polars texts of A.1 with no column named.

## D. Points for Eve (only what no record answers)

Records checked: ADR-103, ADR-104 (point 1 "no silent error", point 7 typed values), `home_audit_steps.md` 5a, `tasks.md` sections 5 to 7 (S2-2 is OPEN, M101), DEC49 (a cast never loses information silently: it covers `polars_cast`, not reading). No record decides what reading does about the silent cases or the raw messages.

1. **Keep S2-2 (a line with the error, not tickable, for a node where the value cannot be typed)?** Options: (a) keep; (b) offer only nodes whose column has the same type as where the value was typed; (c) drop it. Default: (a). Reason: ADR-104 point 7 already says "no silent conversion, plain error"; (a) shows the reason per node and lets the user write at the other nodes.
2. **Reading: one error form for every type.** Name the file, the column, the number of bad cells and the first 3 file line numbers with their values; wrap every raw Polars text (Date/Datetime/Time/Decimal, `format`, zone, Parquet) in the same form with a tip that fits the type. Default: yes (her instruction of M101). No question on whether, only whether to also stop at the first bad column or list every bad column (default: list every bad column).
3. **Silent conversions (A.0): which ones stop the build?** Rule proposed as the default, one sentence: "a value is kept exactly, or the read stops". It would refuse: #3 overflow to infinity and #6 underflow to zero; #1 and #2 a `Decimal` that rounds a digit away (and refuse a `Decimal` without `precision` and `scale` in the checker); #10 digits cut from a Datetime; #7 and #8 a `Date`/`Datetime`/`Time` with no `format` (the checker would require `format`, a change of the recipe format). Not refused but shown as a count/advice: #4 and #5 (Float32, Float16 and huge whole numbers: the user chose a narrow type), #9, #11, #12 (leading zeros: advice "declare it String if it is an ID"), #13 (a count of NaN, ADR-103 point 5 already treats NaN apart), #14 (strip a space to a missing value or keep `''`: pick one), #15 (the checker refuses an `Enum` level that is also a null word). Default: as listed. This is a change of the recipe format for #7, so it needs her yes.
4. **Checker: judge the declaration without data.** `format`, `time_zone`, `time_unit`, `precision`, `scale` (and scale at most precision), repeated `Enum` levels, an `Enum` level that is a null word. Default: yes (same principle as the "no silent error" rule; no data needed).
5. **HOME plot and table paths pass no `strict`.** Make them strict like the recipe action (then 'text 2022 on a number column' is refused everywhere)? Default: yes; it follows ADR-104 point 7 as written. A reviewer should check what HOME's panel sends first.
