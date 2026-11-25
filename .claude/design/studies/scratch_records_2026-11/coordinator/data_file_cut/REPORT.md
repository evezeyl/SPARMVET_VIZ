# A data file cut in the middle of a line: why nothing is said (2026-11-21)

Study only. Nothing in the repository was changed. Scratch: `tmpAI/coordinator/data_file_cut/` (scripts `cut.py`, `nulls.py`, `tiny.py`; results `cut_results.txt`, `cut_raw.log`).
Decision used: D-0427 ("If that data is absent, the opening should stop with a plain reason.").
Labels: RUN = I ran it; READ = read in code; REASONED = follows, not run.

## What the user sees first
A data file with a short last row (cut in the middle of a line) is read as a normal file. No error, no warning. The plot is drawn from the rows that are there. The missing values of the cut row become "missing" (null) with no message. A file cut exactly at the end of a line is also accepted: it is only a shorter file.

## The cause (RUN, READ)
1. The app reads a tab-separated file with `pl.scan_csv(path, separator="\t", infer_schema=...)` and nothing else: `libs/ingestion/src/ingestion/ingestor.py:141` (Data Import check), `:200` and `:211` (the build, `DataIngestor._open`, called by `read_source`). The arguments `truncate_ragged_lines`, `ignore_errors`, `missing_utf8_is_empty_string` are not given, so they have Polars' defaults (RUN: polars 1.40.1; `truncate_ragged_lines=False`, `ignore_errors=False`).
2. Polars' default for a row with FEWER fields than the header: it fills the missing fields with null, without error (RUN, `tiny.py`: `4\t5` under a 3-column header gives `('4','5',None)`). There is no argument of `scan_csv` that makes this an error (RUN: the signature has `truncate_ragged_lines`, which only cuts extra fields; no argument for missing fields). To refuse it, the app would have to count the fields of every row itself.
3. The ingestion then keeps only the declared columns (`ingestor.py:65`, `lf.select(...)`). A cut row that still has all the declared fields is therefore a normal row. A cut row that lacks a declared field gets null in it (RUN: cut after 2 fields: `q30_rate: None, gc_content: None`), and the declared type check accepts null (`libs/ingestion/src/ingestion/declared.py`, casts are `strict=False`).
4. Even a row with MORE fields than the header is not always refused (RUN, new finding). Polars refuses it only when the extra field lies in a column that is read. The ingestion selects only declared columns, so Polars skips the rest and does not check it (RUN: `tiny.py`, "long row": ERROR when all columns are read; accepted when `select(['a','b'])`; the same on the demo file FastP: `h row with MORE fields` accepted by Data Import and by the load gate, although the plain read of all columns fails). So the sentence in `ui_implementation_contract.md` section 9 point 2 ("a row with more fields than the header ... is refused") is true only when the row's extra field falls in a column that is read, or when the file has no undeclared columns. Not covered by a test that I found (not searched).

## Table (RUN on a copy of the demo `FastP.tsv`: 14 header fields, 42 rows, 4 declared fields)

| how the file is cut | the reader (`scan_csv`, declared) | Data Import's check (`ingest_file`) | the load gate (`validate_data_analysis_recipe_data`) | what the plot would show |
|---|---|---|---|---|
| (a) last row cut in the middle: 7 of 14 fields (no line end) | accepted, 21 rows; last row: 7 nulls in the file columns | accepted | 0 problems | 21 of 42 samples; no message |
| (a2) the same, cut after 2 fields (a declared field missing) | accepted, 21 rows; declared `q30_rate`, `gc_content` = null | accepted | no problem (not run for this variant; REASONED from (a), the gate reads one row) | 21 samples; the cut sample has missing values |
| (b) cut exactly at the end of a line (20 rows left) | accepted, 20 rows, all complete | accepted | 0 problems | 20 of 42 samples; no message |
| (c) last field cut inside a value, all fields present (`0.9235...` became `0.91`) | accepted, 21 rows; last value `0.91` | accepted | 0 problems | 21 samples; the last value is wrong, no message |
| (d) cut inside a quoted field (the demo files have no quotes: I opened a quote in the last row) | ERROR "could not parse ..." | REFUSED ("cannot be read in full") | 1 problem ("wrangling cannot run on this dataset") | the recipe is refused with a reason |
| (e) last line complete but with no line end | accepted, 42 rows | accepted | 0 problems | all 42 samples (correct) |
| (f) two rows with the last 3 values empty, tabs kept | accepted, 42 rows | accepted | 0 problems | 42 (correct; empty values are missing values) |
| (g) two rows where a spreadsheet left out the last 3 empty fields (no tabs) | accepted, 42 rows; those fields null | accepted | 0 problems | 42 (correct and identical to f) |
| (h) one row with MORE fields (extra value at the end) | plain read of all columns: ERROR; read with declared columns: accepted | accepted | 0 problems | all 42 samples; extra value ignored |

Note the last rows: (a), (a2), (g) are the same thing for the reader: "a row with fewer fields". It cannot tell a cut file from a spreadsheet that left out empty trailing fields.

The earlier run (case 7a) shows the same: 21 of 42 rows, no message. The cut inside a 2-byte character (case 7b) was refused because Polars refuses invalid UTF-8; it is a different check.

## Answers to the questions
- Q2, Data Import: it accepts (a), (a2), (b), (c), (e), (f), (g) and also (h). It refuses only (d). So a row with fewer fields than the header is accepted everywhere, also by the check built this week. `ingest_file` reads the whole file (`ingestor.py:153`, `lf.collect()`), but whole file read is not the same as every row complete.
- Q3, the load gate: it reads `frame.head(1).collect()` (`app/modules/data_analysis_recipe_validator.py:535`) after `collect_schema()`. It checks the first row only for wrangling problems. That is why it never sees a short last row. A full read at the opening exists (`opening_build`, DECIDED/built partly), but Polars also accepts the short row there, so a full read would not help either (RUN: `orchestrator.read_source` collects all rows: 21, no error).
- Q4, Polars itself: see the cause above (null fill, no argument to refuse).
- Q7, since when: the plain `scan_csv(..., separator="\t")` is from 2026-04-07 (`4ae002a1`, `92f074b4`); the declared-columns read (`as_text`, `infer_schema=not as_text`) from 2026-11-13 (`f2ecfbb7`, "declared Polars types and explicit missing values"); `ingest_file` from 2026-11-21 (`41c656cc`). `truncate_ragged_lines` and `ignore_errors` were never used (`git log -S`: nothing in the ingestion). The behaviour is old (the Polars default); it was never decided.

## What is decided, what is not (ledger)
- D-0034 (DEC24, "strict import"): "only the `input_fields` that are written are read; a declared column missing from the file fails; `original_name` matches exactly; the import reports ... not imported" (`recipe_format_spec.md:128`). It speaks about COLUMNS of the header. Nothing about rows.
- D-0035 / D-0057: the types follow Polars; the value that does not fit fails and is named (`rules_data_analysis_recipe_structure.md` section 9). It speaks about VALUES, and null is accepted as a missing value. Nothing about a row with fewer fields.
- D-0364: only about carriage returns inside two test files (not related).
- D-0050 ("No silent error: that is the rule"), D-0168 ("Nothing should vanish silently in the audit"): general principles. A cut file giving a table with missing values and no message is a silent result; this is what D-0050 forbids, but no decision applies it to a short row.
- I found no ledger line (grep: strict, ragged, "fields than the header", truncat, "fewer fields") about a row with fewer fields than the header. Conclusion: NOT covered. The contract text of Data Import section 9 point 2 names only "a row with more fields than the header" and, as shown, that is also not fully true (point 4 above); it is the builder's wording, not her decision.
- D-0427 covers a file that is ABSENT at the opening. It does not cover a file that is present and cut.

## What can and cannot be detected (fact)
- A row with fewer fields than the header CAN be detected by the reader: count the fields of each row. Polars has no argument for it, so the app would write its own check (an extra read of the lines).
- A file cut exactly at the end of a line CANNOT be detected from the file alone: every row is complete and the file is valid. To detect it one needs something delivered with the file: a row count, or a hash/size of the whole file, or an end marker, written by the sender and compared by the app.
- Hashes that exist: `data_batch_hash` (hash of the contents of all source files: `session_manager.py:294`, used in the session key `:306`, in the keys of the stored tables, and in the export). A cut file gives another hash. What they do today: compare the hash of the file now with the hash of what an open page was built on (`data_change_notice.py`) and tell "a source data file changed" (RUN, case 5: the notice appears after a tab click). They do not compare with an hash expected from the sender, so they cannot say "this file is incomplete". The run showed: no notice in an open page without a click, and the visitor sees no hash or date (case 5d). So none of them would have told the visitor that the file is cut.

## Options for her

| option | what it means | messy but honest file: last line has no line end (e) | spreadsheet leaves out empty trailing fields (g) | cut file (a), (a2), (c) | cut exactly at a line end (b) |
|---|---|---|---|---|---|
| 1. A row with fewer fields than the header is refused everywhere (reader, Data Import, load gate, opening), as a row with more fields should be | needs the app's own field count per row; one plain sentence names the row number | accepted (all rows complete) | refused: the user must save the file with all tabs (a spreadsheet export often fails) | (a) and (a2) refused; (c) NOT detected (all fields present) | not detected |
| 2. A warning instead of a refusal: the table is shown with a plain notice "N rows have fewer fields than the header; the missing values are read as missing" | same field count, nothing is refused | accepted | accepted with a warning at each opening (noise for a normal spreadsheet export) | (a), (a2) warned; (c) not detected | not detected |
| 3. Option 1 for rows cut in a declared column, option 2 elsewhere | the app checks only the fields it reads | accepted | accepted when the left-out fields are not declared; refused/warned only when a declared field is missing | (a2) refused; (a) accepted | not detected |
| 4. Nothing (as today) | the reader's default stays | accepted | accepted | accepted silently, the table has missing values | accepted silently |
| 5. In addition: the sender delivers a row count or a hash with the file, and the app compares | a new file or recipe key; needs a decision about the format and who writes it | accepted | accepted | detected | detected |

Whatever she chooses for rows, only option 5 can catch (b) and (c).

Suggestion: option 1 as an opt-in for the recipe author is not needed to start; I find sound: (i) decide that a row with fewer fields than the header is reported in plain words with the row number, refusing at the opening and in Data Import for a missing DECLARED field (it changes a result: null in a column the plot reads), and a notice for left-out undeclared fields; (ii) fix at the same time the claim for "more fields" so that it is really checked (a row with more fields is refused whatever columns are declared), or change the contract wording; (iii) keep option 5 as a separate decision for deployments whose data arrives by a pipeline (the case of this study), since only it protects against a cut at a line end. The choice is hers.

## Not verified
- I used the demo `FastP.tsv` only; the other tables are read by the same call (READ), not run one by one.
- Quotes: the demo data has none; (d) is a made-up case; whether a quote cut inside a value of a real file is detected depends on where the quote falls (not tested).
- (a2) at the load gate: not run separately (REASONED from (a) and `head(1)`).
- Whether a test exists for "more fields than the header" with undeclared columns: not searched.
- Windows line ends (`\r\n`), a header cut in the middle, and an empty trailing line were not tested.
- The exact commit dates come from `git log -S` on two strings; an earlier version of the ingestor may have read differently in between (not checked).
- Load was 2.5 to 3 during the runs (limit respected); no app was started.
