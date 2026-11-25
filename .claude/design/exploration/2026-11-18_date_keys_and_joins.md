# Date and time keys in joins: research and a safe design

Date: 2026-11-18. Status: exploration. Nothing here is decided. Request: M271 (Eve, question 9, key types).
Labels: VERIFIED (source given), REASONED (my inference). Polars installed here: 1.40.1 (`.venv`, `polars/` docstrings and runs). Repo commit read: `cd0a11d8`.
Terms: a **key** is the column that matches rows of two tables. An **exact join** matches equal keys. An **as-of join** (nearest-in-time join) matches each row with the closest earlier, later or nearest row of the other table. A **dtype** is the stored type of a column (text, whole number, date...).

## 0. The short answer

1. The app already has more than question 9 assumed. It declares `Date`, `Datetime`, `Time` types with a written `format`, it fails loudly on a value that does not fit, and it has an as-of join with a sortedness check and a tolerance check. (VERIFIED, section 3.)
2. The assembler does NOT cast join keys to String today. It refuses a join whose key types differ. The brief's premise is out of date. (VERIFIED, `data_assembler.py:68-120`, ADR-102, D-0044.)
3. The checker rule E03 refuses only numeric entity keys. A Date or true/false entity key is NOT refused today. Option A of question 9 would be a new, wider refusal. (VERIFIED, `recipe_check.py:364-379`, run: `Date.is_numeric()` is False.)
4. My recommendation: option "C, typed keys with a short allowed list" (section 5). Allow String, Categorical, Date, Datetime (as exact keys, and as the sorted key of an as-of join). Keep refusing numbers, true/false and decimals as entity keys. Add a join report (rows matched, unmatched, duplicates). Do not build a second join mechanism.

## 1. How people join on dates (research)

### 1.1 Python

- **pandas `merge`**. Exact match on equal keys. Keys with null match each other, unlike SQL. `validate="1:1"|"m:1"|...` checks duplicates. `indicator=True` adds a column `left_only / right_only / both`. VERIFIED: https://pandas.pydata.org/docs/reference/api/pandas.merge.html (the page does not say what happens with different key dtypes or time zones; not checked by me: NOT VERIFIED).
- **pandas `merge_asof`**. `direction` is `backward` (default: last right row with key <= left key), `forward`, or `nearest`. `tolerance` drops matches that are too far (result is NaN). `by` matches groups first and needs no sorting by itself. `allow_exact_matches=False` makes the comparison strict. Both tables "must be first sorted by the merge key in ascending order". The key must be numeric or datetime-like. The tolerance must fit the key (e.g. a `Timedelta`). VERIFIED: https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html (pandas 3.1.1 docs; what happens on unsorted input is not written on that page: NOT VERIFIED).
- **pandas `merge_ordered`**. Outer join on ordered keys, optional forward fill (`fill_method="ffill"`), per group with `left_by`. Typical use: align two series with different time points. VERIFIED: https://pandas.pydata.org/docs/reference/api/pandas.merge_ordered.html
- **Polars exact `join`**. If the key dtypes differ it raises `SchemaError`. VERIFIED by run (1.40.1): Date vs Datetime, Datetime[ms] vs Datetime[us], naive vs UTC-aware: all three raise "datatypes of join keys don't match". So Polars is loud on a mismatch here.
- **Polars `join_asof`**. `strategy` backward/forward/nearest. `tolerance`: a number, or for Date/Datetime/Duration/Time a `timedelta` or text such as `3d12h`. "1d" means a calendar day (may not be 24 hours with daylight saving). `check_sortedness`: "If the keys are not sorted Polars will error. Currently, sortedness cannot be checked if 'by' groups are provided." VERIFIED: `LazyFrame.join_asof` docstring in the installed 1.40.1. VERIFIED by run: unsorted key without `by` raises `InvalidOperationError`; with `by` and unsorted data Polars returned a result and only a warning "Sortedness of columns cannot be checked when 'by' groups provided" (the result for group `a` took the right row for t=2 from an unsorted left: the join ran, no error). This is a silent-risk place; the app already closes it (section 3).
- **Polars `join_where`**: join on conditions (for example `date >= start & date <= end`), so a window join. The app wraps it as `modif_join_where` and fixes the row order. VERIFIED: `polars_time_joins.py:11-16`.
- **Polars `group_by_dynamic`, `rolling`**: windows over a sorted time column; the app registers both and refuses unsorted or null index. VERIFIED: `polars_time_joins.py:11-20`.

### 1.2 R

- **dplyr `join_by()`**. `closest(sale_date >= promo_date)` = rolling join to the nearest earlier row. `between()`, `within()`, `overlaps()` match a value inside a range, a range inside a range, or ranges that touch. Inequality joins can match one row to many rows: "check results carefully". VERIFIED: https://dplyr.tidyverse.org/reference/join_by.html
- **data.table rolling joins**. `roll=TRUE/Inf` carries the last observation forward; `roll=-Inf` carries the next backward; a finite number limits the distance (a tolerance); `roll="nearest"`. `rollends` controls the ends of each group. Non-equi joins use `on=` with `>=, >, <=, <`. Tables are normally keyed (sorted) with `setkey`. VERIFIED: https://rdrr.io/cran/data.table/man/data.table.html
- **tsibble**. A time table has an **index** (the time column: Date, POSIXct, yearmonth...) and a **key** (what identifies each series). Key plus index identify each row. VERIFIED: https://tsibble.tidyverts.org/reference/tsibble.html. The page does not describe the duplicate error or `has_gaps/fill_gaps`: NOT VERIFIED here.
- **lubridate**. `ymd()`, `dmy()`, `mdy()` name the order of parts. Values that fail to parse become `NA` with a warning. With mixed formats the guess may fail ("All formats failed to parse"); the docs then point to `parse_date_time()`. `tz=` returns a time with a zone, otherwise a plain Date. VERIFIED: https://lubridate.tidyverse.org/reference/ymd.html. Note the R default is a warning, not an error.

### 1.3 What data scientists need (examples from lab or surveillance data)

The first column is fact from the sources above (the tools exist for it). The examples are mine (REASONED).

| Need | Example | Tool in the sources |
|---|---|---|
| Exact date key | Daily weather joined to samples collected the same day | `merge`, `join` |
| Calendar table | Sample date joined to a table of epidemiological weeks (start, end) | window join: `join_where`, `between()` |
| Nearest earlier | A measurement joined to the latest earlier calibration of the instrument, per instrument | `merge_asof(backward, by=)`, `join_asof`, `closest()`, `roll=TRUE` |
| Nearest, with a limit | Match a lab result to the nearest sampling within 3 days; beyond that, no match | `tolerance`, finite `roll` |
| Events in a window | Cases in the 14 days before a sample | `join_where`, `rolling`, `group_by_dynamic` |
| Daily counts with missing days | Counts per day with no row for days with zero cases | gaps: `fill_gaps` (tsibble), `merge_ordered`; not covered by a join alone |
| Several date formats | `02/01/2026` from one lab, `2026-01-02` from another | parse first, with a written format |
| Time zones | Timestamps of an instrument in UTC, of a clinic in local time | explicit zone on both sides |
| Missing times | Samples with a date but no time of day | a Date key, not a Datetime key |
| Same time twice | Two readings at the same second | duplicates: `validate=`, `indicator=` |

### 1.4 Known pitfalls

- **Time unit or zone mismatch.** Polars refuses (VERIFIED by run). pandas: not verified here.
- **Text dates sort wrongly.** VERIFIED by run: the texts `2026-1-10, 2026-1-2, 2026-1-9` sort as `2026-1-10, 2026-1-2, 2026-1-9` (alphabetical). An as-of join on text would be wrong. The app's as-of check can only compare real dates or numbers (REASONED, from the `_not_ascending` code which compares values).
- **Excel serial dates.** Excel stores dates as day counts: serial 40729 is 5 July 2011 in the 1900 system and 39267 in the 1904 system, always 1462 days apart. VERIFIED: https://support.microsoft.com/en-us/office/date-systems-in-excel-e7fe7167-48a9-4b96-bb53-5612a800b487. VERIFIED by run: text `45000` read as a Date gives null (loud with strict parse), but the whole number 45000 cast to a Date gives 2093-03-16 (silent and wrong: Polars counts days from 1970). Consequence (REASONED): a number column must never be turned into a date by a plain cast.
- **Floating point keys.** VERIFIED by run: `0.1+0.2` is not equal to `0.3`, and prints as `0.30000000000000004`. A decimal number is not a safe key.
- **Unsorted input to an as-of join.** See 1.1. VERIFIED.
- **Daylight saving.** VERIFIED by run: the local time `2026-10-25 02:30` in Europe/Oslo (it happens twice) and `2026-03-29 02:30` (it does not exist) both raise a Polars error, even with `strict=False`. Through the app's ingestion this would come out as a raw Polars error, not the plain message (REASONED: `declared.py:111-135` collects and does not catch this error; not run through ingestion).
- **Different date formats in one column.** VERIFIED by run: with `strict=False` and no format, only `2026-01-02` parsed; `03/04/2026` and `45000` became null. Day-month versus month-day (`03/04/2026`) cannot be told apart by any parser (REASONED).
- **Null keys.** pandas lets null keys match each other (VERIFIED, merge page). Polars: the earlier scratch run in `.claude/design/studies/scratch_records_2026-11/panel/key_types/` reports a null boolean key matching itself (that run's output, not re-run by me).

### 1.5 What must come first if time series come later (fact vs judgement)

Fact: the three tools people reach for first are the exact join, the as-of join (with `by` and a tolerance) and window joins. All three exist in Polars and are already registered in the app (section 3).
Judgement (REASONED):
- **First:** exact date key; parse with a written format; refuse mixed types; as-of join with direction and tolerance written in the recipe; a join report.
- **Second:** window joins and calendar tables (`modif_join_where`), `group_by_dynamic`, `rolling` (registered; need help texts and examples for dates).
- **Can wait:** time zones other than "none or UTC", Excel serial dates, filling missing days, irregular-interval series, fiscal or ISO-week rules.

## 2. Today's code, as fact

- **Join key types.** `_check_join_key_types` fails the build when two key columns differ in type, with a plain message; the engine changes no type (`data_assembler.py:68-120`, uses `utils/join_keys.py` `join_key_problem`, one rule for build, Blueprint preview and checker). Two date columns of different types (Date and Datetime) therefore stop with "The join key types differ ... Declare the same type for this field in input_fields of both tables." There is no String cast. The old sentence "String is the safe common denominator" survives in `.claude/knowledge/data_analysis_recipe_data_contract_rules.md:518` and is wrong (found by the scientist viewpoint note, `.claude/design/studies/scratch_records_2026-11/panel/key_types/viewpoint_scientist.md`; I confirm the code).
- **Declared types and parsing.** A field may be `Date`, `Datetime` (`format`, `time_unit`, `time_zone`) or `Time`. The text is parsed at ingestion; a value that does not fit stops the load with the column and up to a few values named, and a suggestion to write `format` (`ingestion/declared.py:66-110, 128-135`).
- **E03.** Refuses a field marked `is_entity_key: true` whose declared type is numeric (`recipe_check.py:364-379`). Date, Datetime, Boolean, String, Categorical are not refused (VERIFIED by run). The message text says "sample id" and "loses leading zeros", which would be wrong for a date.
- **J13.** Advice (never blocks) when a join key is declared as a float (`recipe_check.py:720-760`).
- **Where `is_entity_key` is read.** Written by `recipe_factory.py:79`, `test_lab/bootstrapper.py:123`, `test_lab/scaffolder.py:157`; read by the checker (E02 at `recipe_check.py:261`, E03, FD05) and shown in Blueprint (`wrangle_studio.py:1327`). The audit does not read it.
- **Audit protection of join keys.** `extract_primary_keys` (`session_manager.py:119-146`) collects every name used as `on`, `left_on`, `right_on` in the join steps (text or list). It looks at names only, not at types. It is called at `home_theater.py:1248-1253`. It does not read `by` of an as-of join (REASONED from the code: only the three names are read), so a group column of an as-of join is not protected. This is a small gap.
- **Registered time actions.** `polars_join_asof` (strategy required; keys sorted in both tables and within each `by` group, else a plain error; tolerance checked: positive, a duration text only for date or time keys, no finer than a day on a Date key, a bare number refused on a date key), `modif_join_where`, `polars_group_by_dynamic`, `polars_rolling` (`polars_time_joins.py`), `polars_dt_truncate` (`polars_calls.py:415`). A parse step as an action does not exist: parsing is only the declared `type` and `format` (grep `to_date`, `strptime` in `libs`: only `declared.py` and `filter_values.py`). A recipe could parse in a `polars_with_columns` formula (REASONED; not run).
- **Join report.** The build says nothing about rows matched, unmatched or duplicates, except a caution for a self-join with numbers (`data_assembler.py` `_self_join_caution`). Blueprint's join designer has a key-match preview on real data (`blueprint_arch/join_designer.py:98`, matched and only-left and only-right samples). The build has no such report (grep `unmatched` in `libs`/`app`: none in the assembler).
- **Test Lab.** `test_lab_handlers.py:422, 424` falls back silently to `sample_id` when the join key field is empty (VERIFIED, read). Out of scope here (task 4 of M271 is separate).

## 3. What is already safe, what is not

Already loud (VERIFIED): different key types; different date unit or zone (via the type check, Polars level); unsorted as-of keys (also within `by`); a date text that does not fit the written format; a bad tolerance.
Not covered:
- No report after a join (rows matched, unmatched, duplicates). A date join that matches 2 % of rows is silent. (VERIFIED: nothing in the build.)
- Audit key protection ignores the `by` columns of an as-of join (REASONED).
- An as-of join that matches the wrong direction is the recipe's choice; the app records it in the recipe but I did not check that the export prints direction and tolerance (NOT VERIFIED).
- Raw Polars error for a daylight-saving time with a zone (REASONED).
- Audit row filters on a date key: the values the user types are text; Polars refuses Date vs text (scratch run, not re-run). `utils/filter_values.py` is the typed path (it handles dates as year-month-day text); I did not test a date entity key through the audit (NOT VERIFIED).
- E03 text and the rule sentence say "sample id" and a number story.

## 4. Safe-design building blocks (what each means)

1. **Declared type of a key** in `input_fields` (exists).
2. **One canonical form per type.** Date = year-month-day (ISO), Datetime = microseconds, with a zone or none (not both across tables). Text = the text as written, trimmed. Reasoned choice: the app stores the declared type, shows the canonical form in the audit and export.
3. **Mixed types refused** with a plain message (exists for build and Blueprint and checker through `join_keys`).
4. **Explicit parse** = `type: Date` plus `format: '%d/%m/%Y'` (exists), one format per column. Different formats in one column: the load stops and names the values (exists). Two labs, two formats: two tables each with its own `format`, joined after (REASONED).
5. **Exact joins on dates**: `polars_join` with Date keys of the same type (works today, REASONED from the type rule; not run through the app).
6. **Nearest-in-time**: `polars_join_asof` (exists), `strategy` and `tolerance` written in the step. The recipe is part of the export, so direction and tolerance are recorded there (REASONED; to check, see section 3).
7. **Join report**: after each join, counts of rows in, rows out, left rows without a partner, right rows never used, keys repeated (new).
8. **Stays refused as an entity key**: decimal numbers (not exactly equal: `0.1+0.2`), whole numbers (lose leading zeros: `007` and `7` are one key, VERIFIED by the scientist note run), true/false (two values only, identifies nothing; null matches null). Note: whole numbers and decimals stay allowed as ordinary columns and as the sorted key of an as-of join (REASONED: an as-of key is not an identity).

## 5. Options for question 9 and the key mechanism

Common baseline: nothing in the engine changes the type of a key (already decided and built, D-0044).

### Option A: strict. A key is text or a category only.
- User sees: a Date entity key is refused by E03 with a message; to join by date the user declares the date as String in ISO form, or parses in a step.
- Checker: E03 widens from "numeric" to "not String/Categorical". Message rewritten for date and true/false. Join key rule (`join_keys`) unchanged.
- Join code: none. Tests: E03 cases for Date, Datetime, Boolean (about 3 tests).
- Docs: `rules_data_analysis_recipe_structure.md` section 9 line 214, `recipe_format_spec.md` (E03 row 608), `recipe_check.py:364-379`.
- Pro: simple; no new date logic. Con: a text date joins only when written the same way; text dates sort wrongly (VERIFIED), so the as-of join on such a key is impossible; the user is pushed to write dates as text, which is the pitfall of 1.4. It blocks future time series.
- Silent-change risk: medium. Text keys written differently (`2026-1-3` vs `2026-01-03`) do not match and nothing says so, unless the join report exists.
- Effort: [sonnet/low].

### Option B: everything allowed (no E03 limit on type).
- User sees: any type as key. Con: decimal and whole-number keys come back, silently merging or missing samples. Contradicts D-0067 and D-0225 (her decisions). Not recommended. Effort [sonnet/low]; risk high.

### Option C (recommended): typed keys with a short allowed list.
- Allowed as entity key: String, Categorical, Date, Datetime (no zone or one zone; same on both sides). Refused: numbers, true/false.
- User sees: for a Date entity key, nothing changes except the checker accepts it. For a number or true/false key: the message names what is wrong for THAT type (numbers: leading zeros and decimals; true/false: two values identify nothing). The audit shows a date key in year-month-day.
- Checker: E03 becomes an allow-list with one message per refused type (today's text says "sample id" and "leading zeros" for every type); the checker gains advice "J14: a Datetime key with a time zone on one side only" is not needed because the type check already stops it (VERIFIED by run); so no new join rule. Optional advice: an as-of join whose `by` or key column is declared as text (not sortable as dates), as advice (REASONED).
- Join code: no new join. Add the join report (section 6). Add `by` columns to the protected audit keys (`extract_primary_keys`).
- Tests: E03 per type (Date ok, Datetime ok, Boolean refused, Float refused, Int refused); an exact join on two Date columns; Date vs Datetime stops with the plain message (exists for the type rule, add the date case); as-of with `by` gets its columns protected; audit filter on a Date key (type-aware value, `filter_values`); the report counts.
- Docs: `rules_data_analysis_recipe_structure.md` section 9 line 214; `recipe_format_spec.md` E03 row 608 and 370-377; `recipe_check.py:364-379`; the `.qmd` pages that say "primary key is sample_id" (`docs/user_guide/audit_pipeline.qmd:121-135`); wording pass held by Eve.
- Pro: keeps her two decisions (sample id never a number, D-0225) and opens the road to time series. Uses the loud type rule already there. Con: audit and export must show dates in one form; a Datetime with a time zone is allowed only if both tables have the same zone, so a hard-to-read message may appear (the current message names both types, e.g. `datetime[us, UTC]`).
- Silent-change risk: low if the report is built; medium without it.
- Effort: [sonnet/medium] for E03 + audit `by` + tests; the report is [sonnet/medium] separately.

### Option D: C plus a recipe-written time key for series ("index" as in tsibble).
- Declares in the recipe which column is the time column of a table (separate from the entity key). Use for as-of, windows and gap checks. Con: a new concept now, before any time series recipe exists; more to learn. Defer: build only when the first time series recipe exists. Effort [opus/high] (design) later.

### 5.1 One mechanism for keys (M271 task 3)

Today two sources: the audit protects names found in join steps (`session_manager.py:119-146`), the checker uses `is_entity_key`. Options:
- **K1: keep two sources, make them agree by a checker rule.** Every column that is `is_entity_key` must appear as a key in at least one join of the recipe, or the table is a lookup. Con: still two lists. [sonnet/medium].
- **K2 (my pick): the recipe declares the entity key (`is_entity_key`); the audit protects the entity keys plus every column used in a join step (`on`, `left_on`, `right_on`, `by`), all read through one function in `utils` (like `join_keys`).** The audit reads the recipe only; the join steps stay written by the recipe (so the join mechanism does not change, which Eve asked: no second mechanism). Pro: one function, one test, joins stay in the recipe. Con: the audit list changes for old recipes (more protected columns); a changed protection must be said to the user (D-0050). Files: `session_manager.py`, `home_theater.py:1248`, `utils/join_keys.py`, tests under `app/tests/`. [sonnet/medium].
- **K3: derive the join keys from `is_entity_key` only (joins stop naming keys).** Con: breaks joins on non-entity keys (gene id in long tables, D-0223) and as-of joins. Not recommended.

## 6. The join report (all options)

After every join step the build records and the user sees (Blueprint preview and the run log): rows of the left table, rows of the right table, rows in the result, left rows with no partner, right rows never used, number of keys that appear more than once on each side. A big mismatch is a caution, never an error (D-0015: the software informs, the user decides). It is also written in the export (D-0050: no silent error). Existing pieces: Blueprint preview counts (`join_designer.py`), self-join caution numbers (`data_assembler.py`). New: one shared function in `utils/join_keys.py`, called by the build. Files: `data_assembler.py`, `join_designer.py`, tests. [sonnet/medium].

## 7. What nothing decides (for Eve)

1. May a Date or Datetime be an entity key? Options: yes (C, recommended); no (A); anything (B). My default: C.
2. A date written as text in the data: should the app help (a `format` is written in the recipe, exists) or refuse text dates as keys? Default: the user writes `type: Date` and `format`; the app stops and names bad values.
3. Time zones: allow only "no zone" or "UTC" for keys at first? Default: yes; other zones later. (REASONED: zones add the daylight-saving errors of 1.4.)
4. Nearest-in-time joins: must the recipe always write `strategy` (already required) and `tolerance`? Default: `strategy` required (already); `tolerance` optional but the join report shows the largest distance used. Alternative: also require `tolerance`.
5. After a join, show the report always, or only when something is unmatched? Default: always in the run log; on screen only when unmatched rows exist.
6. One source for audit keys: K2 (entity keys plus every join column, read in one function)? Default: K2.
7. Do whole numbers stay refused as entity keys even for ids like a plate number or a year? Default: yes (D-0225), the user writes them as String.
8. Is a time column kept separate from the entity key (Option D)? Default: not now; revisit when the first time series recipe exists.
9. The words "primary key" and "entity key" (task 5): held by Eve; this report only says that E03 and the docs speak of the "sample id" and the new rule must speak of "entity key".

## 8. What I could not verify

- pandas behaviour on key dtype or time zone mismatch, and on unsorted `merge_asof` input (the official pages do not say it; pandas not run).
- tsibble duplicate error text and gap functions; data.table behaviour on unsorted input; lubridate time zone details beyond the page.
- Whether the export prints the direction and the tolerance of an as-of join.
- Whether the audit filter works on a Date entity key (not run).
- That an exact join on two Date columns works through the whole app (REASONED from the type rule and Polars; not run through `DataAssembler`).
- The raw error on a daylight-saving time through ingestion (run only on Polars).
- The row-count claim for the `by`-unsorted as-of run is from my small test, not from documentation.
