# Test Lab review: what it does, what is wrong, what to fix

Date: 2026-11-18. Status: exploration. Nothing here is decided and nothing was changed. Request: M271 task 4 (Eve: "we will need to fix the lab anyway and review how its functioning").
Repo commit read: `cd0a11d8` (branch `dev`). Labels: VERIFIED (file:line, or something I ran), INFERRED (my reading, not run), NOT RUN.
Terms: a **key** is the column that matches rows of two tables. A **writer** is code that writes a recipe file. The **checker** is the recipe checker `libs/utils/src/utils/recipe_check.py`. **Format 1** is today's recipe shape.
What I ran (all on small files I made under `tmpAI/panel/test_lab_review/`, nothing started, no test suite): the scaffold function with two uploaded files; the recipe checker and the data check on what it wrote; the synthesizer on a tab file, a comma file and a list of names; the anonymiser on a file with a missing id; the ID reconciliation on a mixed set; the file converter on a tab file read as comma. I did not start the app, so no screen was seen: every statement about "what the user sees" is read from the code.

## 0. The short answer

1. The Test Lab has five tools in the app (ID reconciliation, scaffolding, synthetic data, anonymisation, file reformatting). The sixth tool the design file counts, the Excel extractor, is not in the app (section 1.6).
2. The worst problem is the scaffolding tool. The recipe ZIP it writes does not pass today's checker (it gets F01, J07, S03, J02, E03), it names each table "0", "1" after Shiny's temporary upload names, it points the recipe at a temporary file path, and it writes the join key you typed without checking that it is a column of the files. (VERIFIED by run, section 2.1.)
3. The silent `sample_id` default (`test_lab_handlers.py:422, 424`) is real but small beside point 2: it fires only when the "Join key column" box is empty. The box is pre-filled with `sample_id` (line 340), so most users never see it. The bigger hidden assumption is that any column called `id`, `sample_id` or `isolate_id` is marked as the entity key, by name alone (`scaffolder.py:156`).
4. Four other tools hide what they did: a tab file read as comma gives one column and no message (synthetic data, reformat, scaffold); synthetic data turns date and free-text columns into `value_A/B/C`; the ID cleaning step is applied to the whole column and breaks ids that already matched; the anonymiser crashes on a missing id and cannot keep two files consistent.
5. The right-hand panel and the Info panel say less than the tools do, and some of what they say is not true (section 2.8).
6. Fixing it is mostly [sonnet/medium] work plus a few decisions. The format change (new tier keys, `ui_label`) makes the scaffolder and bootstrapper rewrite anyway: fix them together, once.

## 1. What each tool does

Where it lives: the screen `app/modules/test_lab_studio.py:79-131` (five accordion panels), the wiring `app/handlers/test_lab_handlers.py` (1007 lines), the logic in `libs/test_lab/src/test_lab/*.py` and `libs/id_reconciliation/`. The tools hold no state between runs (ADR-084 point 1, `rules_test_lab.md` section 1). Tests: see each tool. There is no test of a screen function except one: `app/tests/test_click_reads_visible.py:71-97` calls `_scaffold_result` (VERIFIED by grep for `tl_` in `app/tests`). The Playwright smoke file checks only that the right panel shows the tool texts (`test_shiny_smoke.py`, named in `home_theater.py:1954-1957`; not read by me).

### 1.1 ID reconciliation

- Input: two TSV/CSV/TXT files, one id column in each (`test_lab_handlers.py:43-54, 57-110`).
- Output on screen: a pre-check line (overlap count and percent), a table of matches (exact, pattern, fuzzy, unmatched) with certainty, a many-to-many warning, a certainty slider, and a download of an "id transformation" YAML (`:57-312`).
- What it does: exact match first; then the one best pattern (remove prefix, remove suffix, lower case, `_` to `-`) applied to all unmatched ids; then fuzzy matching (rapidfuzz, cutoff 70) for the rest (`libs/id_reconciliation/src/id_reconciliation/core.py:36-80`).
- Works end to end as far as I ran: VERIFIED by run on a small mixed set, the reconcile and the step creation work. The screen was not run.
- Tests: `libs/id_reconciliation/tests/` (55 test functions counted, not run), `app/tests/test_id_cleaning_steps_reach_a_recipe.py`.

### 1.2 Data analysis recipe scaffolding

- Input: a recipe id, one or more data files, an optional metadata file, a "Join key column" box, an optional tick to write the ID cleaning steps of the reconciliation above (`:318-390`).
- Output: a ZIP: a master recipe, per table an `input_fields` file and a `wrangling` file, and, if there are two or more tables, one join file (`scaffolder.py:100-144`). The status line says "Scaffolded 'x' - n data schema(s). Download the ZIP and open in BLUEPRINT to continue." (`:494-520`).
- What was run: VERIFIED by run, section 2.1.
- Tests: `libs/test_lab/tests/test_scaffolder.py` (21), `test_bootstrapper.py` (13), `app/tests/test_id_cleaning_steps_reach_a_recipe.py`, `test_click_reads_visible.py`. These test the shape of the files; none runs the checker on the result (VERIFIED: grep for `check_recipe` in `libs/test_lab/tests` is empty; the class `TestWritersEmitFormatOne` at `test_bootstrapper.py:136-165` says in its docstring that the recipe "must pass the recipe checker" but only reads a few keys).
- The bootstrapper (`bootstrapper.py`) is the first scaffolder without the ZIP and without the join. It is used by the scaffolder for type guesses and by its own tests; no screen calls its `bootstrap()` (VERIFIED by grep).

### 1.3 Synthetic data (AquaSynthesizer)

- Input: a reference file, or a comma-separated list of column names; number of rows (10 to 5000); mode demo or stress test; in stress test, two sliders (missing values rate, duplicate ID rate) (`:539-639`).
- Output: a preview of 10 rows and a TSV download (`:660-686`). The scenario save and load (`save_config`, `load_config`) exist in the library and are not on the screen (VERIFIED: the handler never calls them). The download holds the TSV only, with no config record.
- Tests: `test_synthesizer.py` (21 test functions, not run).

### 1.4 Anonymisation

- Input: one file, the id column, optional personal columns to strip, a pattern (sequential, hash, custom) and a prefix (`:688-720`).
- Output: a ZIP with the anonymised table, a mapping table (original id, new id, personal columns) and a config record (`anonymiser.py:123-141`).
- Tests: `test_anonymiser.py` (22, not run).

### 1.5 File reformatting

- Input: one XLSX/XLS/CSV/TSV/TXT file; for XLSX, a tick list of sheets; for text files, a delimiter (comma, semicolon, tab, pipe) (`:883-940`).
- Output: a TSV (text file) or a ZIP of one TSV per sheet. Text is read with all columns as text (`reformatter.py:113`, `infer_schema_length=0`), which keeps `007` as `007`.
- Tests: `test_reformatter.py` (20, not run).

### 1.6 The Excel extractor (not on any screen)

`libs/test_lab/src/test_lab/extractor.py` reads a config that names sheets and a "primary_key" per sheet, renames that column to `id`, and writes TSVs. It is used only by its test (`consumed_by` in the file header; VERIFIED by grep: no handler or module imports it). `TEST_LAB.md:3-6` says "all six tools are implemented and wired": for this one that is not true. `README.md` of the library lists it as a tool (`libs/test_lab/README.md:15`).

## 2. What is wrong

### 2.1 Scaffolding writes a recipe that does not pass the checker, and its tables are named "0" and "1" (VERIFIED by run)

I called `scaffold_from_uploads` (`test_lab_studio.py:30-76`, the function the screen calls) with two files whose temporary names were `0.tsv` and `1.tsv`. That is how Shiny names uploads: `_fileupload.py:53-55` joins the folder, the running number and the extension (VERIFIED by reading Shiny's source in `.venv`). The scaffolder takes the table name from `Path(datapath).stem` (`scaffolder.py:84-86`), not from the name the user chose. Result:

- **The tables are named "0" and "1"** (`data_schemas: '0': ...`). The user's file names (`isolates.tsv`) appear nowhere in the recipe. Every `!include` file is named `0_input_fields.yaml`, `1_wrangling.yaml`. Tests miss it because their fixtures use real file names (`test_id_cleaning_steps_reach_a_recipe.py` `uploads`; INFERRED from the shape of the test, not read to the end).
- **The recipe points to a temporary file.** `source: path: tmpAI/.../0.tsv` in my run; in the app it would be the Shiny temp folder, which is removed when the session ends (`scaffolder.py:192-196`, `:222`). For the metadata file the path is written absolute. INFERRED for the app (I did not run the app); VERIFIED that the path written is the upload path given.
- **The checker refuses the result.** I ran `validate_data_analysis_recipe(..., "run")` on the written recipe. Problems reported (VERIFIED by run): F01 and J07 (the join file starts with a `steps:` key under `steps:`), S03 (a table has no `label`), J02 (the join has no `label`), E03 (the key is declared `Int64`, a number), T09 (no plot: expected for a scaffold). The loader also prints "Auto-unnesting redundant key 'steps'", a legacy tolerance. The data check cannot load it: "missing the required 'analysis_groups:' block" because the stub is an empty `{}` (`scaffolder.py:230`).
- **The id column becomes `Int64` and loses leading zeros.** The types are guessed from the first 100 rows with Polars' default reader (`scaffolder.py:108, 117`). My ids `007, 008, 009` came out as `Int64`, and the scaffolder marked that column `is_entity_key: true` (by name, `:156`). That is exactly what E03 and D-0225 refuse ("the sample id is a string or a categorical, never a number"). The user gets a recipe that the app's own rule refuses. Measured: yes, VERIFIED. Whether `Int64` would be written for a real id like `S001` is no: text ids give `Categorical` or `String` (`bootstrapper.py:39-58`).
- **What the user sees:** "Scaffolded 'proj' - 2 data schema(s). Download the ZIP and open in BLUEPRINT to continue." No warning. When they open it, the checker lists the problems above. (INFERRED for what Blueprint shows; VERIFIED for the checker output.)

### 2.2 The silent default join key `sample_id` (`test_lab_handlers.py:422, 424`)

- **What falls back, and when (VERIFIED, read).** Line 340: the box "Join key column" starts with the text `sample_id`. Line 422: `join_key = (input.tl_scaffold_join_key() or "sample_id").strip()`. If the user empties the box, the empty text is false, so `sample_id` is used. Line 424: if reading the input fails for any reason, `sample_id` is used. Neither case says anything. The status line never names the key that was used.
- **When the box is not empty**, the typed text is used as written. It is not changed to the column name the recipe gives (`column_slug`: lower case, non-letters to `_`, `scaffolder.py:88-90`). I ran it with the key `Sample ID` on a file whose column is `Sample ID`: the recipe has the field `sample_id` and the join step `on: [Sample ID]` (VERIFIED by run). The join then names a column that does not exist in the recipe. The checker did not report it at the `run` level (it listed other problems only); the engine would stop when the recipe is run (INFERRED: not run through the engine).
- **No check that the key is a column of every file.** `scaffold_from_uploads` checks the column only for the ID cleaning steps (`test_lab_studio.py:65-70`), not for the join key. A file without the key gets a join on a missing column. (VERIFIED by reading; not run with such a file.)
- **What a wrong result looks like:** a recipe that joins every table to the first on `sample_id` with `how: inner` (`scaffolder.py:176-183`), written even when the real key is `isolate`, `strain` or a date. The join step is there and looks plausible. Rows without a partner are dropped by the inner join, and nothing in the recipe or the status says so. Compare the rule files: ADR-084 point 6 and `rules_test_lab.md:131-141` say the scaffold writes only an empty `joins: {}` stub, not a join (see 2.9).
- **The name-based entity key.** `scaffolder.py:156` and `bootstrapper.py:122` mark a column as `is_entity_key` when its slug is `id`, `sample_id` or `isolate_id`, not when it is the key the user typed. A recipe whose join key is `strain` has no marked key. The checker's E02 then complains only if the recipe has an `entity.population` block, which the scaffold never writes (INFERRED from `recipe_check.py:250-262`). The reverse also happens: a table that has an `id` column that is not the sample id gets it marked.

### 2.3 A text file with tabs is read as comma, and a CSV as tab, without a word

- **Scaffolding** reads every file with `separator='\t'` (`scaffolder.py:94, 108, 117`) although the file box accepts `.csv` and `.txt` (`test_lab_handlers.py:326-331`). A comma file gives one column named `a,b,c`. VERIFIED by run for the synthesizer (same pattern, `aqua_synthesizer.py:136`): the reference file `real.csv` gave one column called `sample_id,collected,country,note`. For the scaffolder: INFERRED (same code pattern, not run on a CSV).
- **Reformatting:** a tab file uploaded as `.tsv` while the delimiter box still says "Comma" (the default) is "converted" into the same one-column file. VERIFIED by run: `['a\tb']`. The status says "File ready: x.tsv" and gives no column count (`test_lab_handlers.py:963`). Another trap: the convert function says "Any delimiter is accepted"; the screen does not read the file to guess.
- **ID reconciliation** guesses by the file ending: `.tsv` is tab, everything else comma (`:57-61`). A tab file named `.txt` is read as comma. The column list then shows one name. If reading fails, the function returns an empty list (`except Exception: return []`, `:55-56`) and the screen says "Upload both files to select ID columns." That sentence is wrong when the files are uploaded but could not be read.

### 2.4 Synthetic data: what is made up is not said

All VERIFIED by run unless marked.
- **Date and free-text columns become `value_A`, `value_B`, `value_C`.** My reference file had a date column `collected` with 28 values and a text column `note`. Both came out as `value_A/B/C` (`aqua_synthesizer.py:169-170, 216-217`: a text column with more than 15 values gets no value list, and the generator then falls back to the three placeholders). The status says only "Generated 50 rows x 4 columns" (`test_lab_handlers.py:653`). A real date column can never be reproduced as a date.
- **A list of names gives placeholders.** For `year, country, isolate` every column is `value_A/B/C`; only names that look like a key get ids (`_is_pk_name`, `aqua_synthesizer.py:20-28`: ends with `_id`, `_pk`, `_key`, `_code`, `_num`, `_no`, starts with `id_`, or is `id`, `pk`, `key`, `accession`, `barcode`, `sample`). `isolate` is not recognised: VERIFIED, `primary_key_column` was None.
- **The "Duplicate ID rate" slider does nothing when no key was recognised**, and says nothing (`aqua_synthesizer.py:259`: `if ... and pk_col`). VERIFIED by run: with `primary_key_column` None the table came out without duplicates. The user sees the slider, moves it, downloads a table without duplicates.
- **The error sliders are read inside `except Exception: pass`** (`test_lab_handlers.py:633-637`): if reading fails the stress test runs with the default rate of zero and does not say so. INFERRED (not forced).
- **No seed.** `generate(config)` is called without a seed (`:639`), so two runs differ and a stress-test file cannot be reproduced. The rule file asks for a reproducible record (`rules_test_lab.md:314-316`, named scenario roundtrip) but the screen has no save of the scenario and the download holds no config. VERIFIED by reading.
- **The numbers come from the first 100 rows only** (`aqua_synthesizer.py:136`). A column of ages with an outlier in row 500 is not reproduced. Not said on screen.
- The synthetic keys are named `<column>_0000...` (`:148`). A duplicate-ID run renames them to `<column>_000012` (6 digits, `:263`). The pattern changes inside one file. Harmless for joins, odd to read. INFERRED.

### 2.5 Anonymisation

- **Crash on a missing id (VERIFIED by run).** A file with an empty id in two rows gave `KeyError: None` at `anonymiser.py:303`. In the app the user sees a generic Shiny error, not a sentence (`_anon_result` has no `try`, `test_lab_handlers.py:788-840`; INFERRED for the display).
- **The key column is renamed.** The output column is `anon_<id column>` and moves to the first place (`anonymiser.py:119, 309`). A recipe that reads `sample_id` no longer finds it. The screen does not say so (`:848`).
- **Two related files are anonymised one by one.** The screen takes one file (`:652-655`), so the same original id can get different new ids in each file (the sequential pattern numbers ids in order of first appearance, `anonymiser.py:267-283`). The batch function that keeps ids consistent exists (`anonymise_batch`, `:144-226`) and is not on the screen. The right-hand text promises "consistent synthetic equivalents" (`home_theater.py:1991-1993`) and `TEST_LAB.md:50-54` says the same id always gives the same new id across files. True only inside one file. This is the most serious claim that is not backed by the screen, because a join of two anonymised files silently loses rows.
- **The hash pattern is not secret.** The new id is the first 8 hex characters of the SHA-256 of the id, with no secret added (`anonymiser.py:46-48`). Sample ids are easy to guess, so anyone can recompute the table. Two ids can also give the same 8 characters (collision), and then two samples would share one id with no message. INFERRED (not run).
- **The ZIP holds the mapping with the original ids and the personal columns.** The button says "Download ZIP (anonymised + mapping + config)" (`:717`). Nothing says that the mapping must not be shared. The status does not list which columns were not touched (free text, dates of birth). INFERRED.
- The file reader is also by ending (`.tsv` tab, else comma, `anonymiser.py:254`): a `.txt` with tabs is read as comma, as in 2.3.

### 2.6 ID reconciliation: the cleaning step can break ids that already matched (VERIFIED by run)

- The pattern pass picks the one best pattern and applies it to every unmatched id (`core.py:55-73`). Later, `generate_transformation` turns the pattern into a step for the whole column (`core.py:160-195`, `recipe_steps.py:41-45`). The step is written into `tier1` of the table and runs on every row.
- Run: ids `ISOLATE_1, ISOLATE_2, sample_004, sample_005` against targets `ISOLATE_1, ISOLATE_2, 004, 005`. Four of four matched in the reconcile (two exact, two by pattern). The step "remove the first 7 characters" applied to the whole column gives `_1, _2, 004, 005`: two of four match (VERIFIED). The two ids that matched exactly are now broken, with no message.
- Fuzzy matches are only kept as a text map in the transformation file (`metadata["fuzzy_recode_map"]`, `core.py:185-188`). `recipe_steps` does not write it into the recipe (VERIFIED by reading `recipe_steps.py:104-117`). The scaffold status says "The ID reconciliation gave no cleaning step, so none was written" (`test_lab_handlers.py:506`), which is true; it does not say that fuzzy matches were dropped.
- The many-to-many warning says "A written reason is required before downloading the id transformation" (`:223`), but the download does not check it: it adds the reason if there is one and downloads in any case (`:283-310`, VERIFIED by reading). The sentence is not true.
- `threshold` falls back to 0.7 and the column names to `ref_id`/`target_id` inside `except Exception` (`:290-298`), with no word. The `ref_id` fallback would name a column that does not exist in the written transformation. INFERRED.
- A reconcile with an unreadable file returns `None` and the screen says "Upload both files and select columns first." (`:156, 195`), which is also what it says for a file that is there but failed to read. `_recon_read_ids` itself has no `try` (`:50-54`): an unreadable file raises inside the calculation. INFERRED for the display.

### 2.7 File reformatting

- Deselecting every sheet gives all sheets: `list(input.tl_reformat_sheets()) or None` (`test_lab_handlers.py:979`, VERIFIED by reading). The user asked for none and gets all.
- Two sheets whose names differ only by symbols (`A/B` and `A B`) get the same file name and the second overwrites the first (`reformatter.py:172-175`, `_safe_stem`). INFERRED.
- A sheet name read error is swallowed: `except Exception: return []` and the screen says "Could not read sheets." (`:942`).
- The result says what file is ready, not what was made: no rows or columns count, no list of the written sheets (`:958-966`).
- Types in an XLSX come from the Excel cells; dates become ISO dates in the text. NOT RUN (I did not run an XLSX).
- The header in `reformatter.py:16-21` says the screen is "not yet built". It is built. The same stale line is in `anonymiser.py:27-32`. VERIFIED.

### 2.8 What the panels say versus what the tools do

- **Info panel** (left): "Test Lab tools - instructions coming soon." (`home_theater.py:1666-1670`, VERIFIED). It is a placeholder by Eve's decision of 2026-11-08 (the comment says so).
- **Right-hand panel** (`home_theater.py:1952-2012`, VERIFIED): "Match and align ID columns across related files" (no word on its limits); "Generate boilerplate pipeline data analysis recipe from uploaded files" (it also writes a join); "Replace real IDs with consistent synthetic equivalents. Reversible via BLUEPRINT join" (consistent only inside one file, 2.5; the reversing join is not generated in the screen: `build_deanon_steps` is not called, and it writes the old action name `join`, `anonymiser.py:228-246`); "Convert XLSX (multi-sheet) and CSV files to TSV" (true).
- **Help text** `app/src/help/test_lab.md:6-9`: "One key column per run" (true) and "primary-key candidate hints" (true: a comment line in the wrangling file, `scaffolder.py:166-172`).

### 2.9 Differences between the rule file, the design file and the code

| Where it says | What the code does | Status |
|---|---|---|
| `rules_test_lab.md:149-153` "Known bugs - fix in TL-BOOTSTRAP-FIX-1: writes `plotting` key, hardcodes `metadata_schema`, missing `joins: {}` stub" | The bootstrapper writes `analysis_groups: {}`, `metadata_schema` only with a metadata file, and `joins: {}` (`bootstrapper.py:179-191`) | The three bugs are fixed. The paragraph is stale (VERIFIED). |
| `rules_test_lab.md:131-141` and ADR-084 point 6: the scaffold writes a `joins: {}` stub only; no join steps beyond key cleaning | The scaffolder writes a full join (`how: inner`, `on: [key]`) when there are two or more tables (`scaffolder.py:122-136, 174-187`) | Code is wider than the rule (VERIFIED). Needs a decision (Q3 below). |
| `TEST_LAB.md` (scaffolding section, `:338-352`): the system validates join key uniqueness; the tier1 holds `drop_duplicates`, `null_if`, `drop_nulls` on join keys | None of this is written; `tier1` is empty unless reconciliation steps are given (`scaffolder.py:171`) | Design not built (VERIFIED). |
| `TEST_LAB.md:38`: after reconciling, the user selects which columns are keys | The screen has one free text box "Join key column" | Design differs. |
| `TEST_LAB.md:3-6`: "all six tools are implemented and wired", "94 passing tests" | The extractor is not wired. I counted 103 test functions in `libs/test_lab/tests/` (not run) | Stale (VERIFIED for wiring). |
| `rules_test_lab.md:99-103` the public API lists `PatternSuggestion` re-exported, etc. | Not checked | NOT CHECKED |
| ADR-084 has a "Partly stale" banner for the old manifest words (`architecture_decisions.md:4006`) | The code is already format 1 for the bootstrapper top keys | ADR text is old; code newer. |
| `rules_test_lab.md` section 1: closing a tool panel resets it | Calculations are cached by Shiny until the button is pressed again; no code resets them on panel close | INFERRED; low risk. |

### 2.10 Will the recipes pass after the format change?

The change (facts file `tmpAI/coordinator/briefs/ENGINE_KEYS_facts_2026-11-18.md`, answers 1 to 6, D-0250 to D-0256): the tier keys sit directly in the table, join and plot, with no `wrangling:` container and no outer `steps:`; a tier may be an `!include`; `label` becomes `ui_label`; a plot entry holds its whole content without `spec:`. The brief names every writer of recipes ("Blueprint writes recipes: every writer must write the new shape", `ENGINE_KEYS_brief_draft.md:102`); it does not name the Test Lab writers (VERIFIED by grep: no `test_lab`, `scaffold` or `bootstrap` in the brief draft). My reading (INFERRED):
- The scaffolder writes `wrangling: !include` (`:202-203`) and a fragment `{tier1: [...], tier2: []}` (`:171`), a join `steps: !include` on a file that itself starts with `steps:` (`:186`), and `label` in the fields (`:153`) and `info.label` (`:212`). All of these change.
- Today it already fails (2.1). After the change it fails differently unless rewritten. The test `test_bootstrapper.py:136-165` reads keys by name and would need rewriting, and it should run the checker (the model: `app/tests/test_writers_emit_format_one.py`).
- There is a second recipe writer, `utils.recipe_factory` (`minimal_schema`, `minimal_join`, `recipe_factory.py:61-100`), and a script that uses it. It is tested through the checker (`test_writers_emit_format_one.py:224-237`). The Test Lab scaffolder does not use it. Two writers of the same file is the "two mechanisms" Eve asked not to have (M271, her words on joins). Using the factory in the scaffolder would give one writer; the one thing the factory lacks is the type guessing (kept in the bootstrapper) and the ZIP packaging.

### 2.11 Other findings

- The recipe id typed by the user is not checked: it becomes a folder name and the recipe `id` (`scaffolder.py:101, 207`), and ADR-092 says the id equals the file name. A name with a space or a slash is used as it is. INFERRED (not run).
- Names of the output ZIP and the folder are the recipe id; if two uploaded files have the same stem (`data.tsv` and `data.csv`) they get the same table id and overwrite each other in the ZIP. Today the temp names (`0`, `1`) hide this. INFERRED.
- The handler file has 21 `except Exception` lines (VERIFIED by count); examples with a quiet default: `:43-48, 292, 297, 442, 422-424, 633-637`. Every such default is a place where a wrong state turns into a quiet choice. I counted the pattern by reading; I did not list all.
- The Test Lab files are read in full in memory: `_recon_read_ids` reads the whole file as text. Fine for the sizes here. Not an issue to fix.

## 3. What to fix, in order

The order is: stop the wrong results first, then the hidden choices, then the words, then the format change that rewrites the writers anyway. Each item: what the user sees after it; the decision that covers it, or "needs a decision".

1. **The scaffold uses the file names the user chose, and the recipe holds a real path or none.** After: tables are named after `isolates.tsv`; the status says where the data files must be placed, or the ZIP holds the files. Decision: needs a decision (Q1: the ZIP with the data, or a path the user edits). [sonnet/medium]
2. **The scaffold passes the checker** (no F01, J07, S03, J02; a key that is a String or Categorical, never `Int64`), proved by a test that runs the checker and the loader on the written recipe, like `test_writers_emit_format_one.py`. After: opening the ZIP in Blueprint shows no error. Covered by: D-0067, D-0225 (key not a number), D-0050 ("No silent error that is the rule"), `test_writers_emit_format_one.py` pattern. [sonnet/high] (do it together with item 6; the shape must be the new one)
3. **Read the files with the right delimiter, and say it.** After: the screen shows the delimiter it used and the number of columns found; a one-column result gets a caution ("only one column was found; is the delimiter a tab or a comma?"). Applies to scaffolding, synthetic data, reformatting, anonymisation, reconciliation. Covered by: D-0050. [sonnet/medium]
4. **The join key is a choice from the columns found, never a default.** After: the form lists the columns common to all files and the user picks one (or two for a pair); an empty box blocks "Scaffold" with a plain sentence; the status names the key used and how many rows of each table have a partner. Covered by: D-0050, D-0165 (a decision that is needed and missing is reported to her). Needs a decision on the pair/date case (Q2) and on the join itself (Q3). [sonnet/medium]
5. **The entity key is the one the user names, not a column with a certain name.** After: the key column is marked `is_entity_key`; nothing else is marked by guesswork. Covered by: D-0224/D-0225 (the key is declared; `recipe_check.py:364-379` "nothing is guessed from a column name"). [sonnet/low]
6. **Rewrite the scaffolder and bootstrapper once, for the new format**, using `recipe_factory` for the recipe dictionary (one writer), and add them to the list of writers of the format brief. After: the ZIP holds the new shape; `ui_label` instead of `label`. Covered by: D-0250 to D-0256 (format change) and the "every writer" line of the brief. Needs the brief to name the Test Lab writers (report to Eve: they are missing from it). [sonnet/high]
7. **Make the cleaning step safe.** After: the reconciliation says which ids a step will change that already matched, and refuses or warns; or the step is written only for the ids that need it (a `when/then`). Fuzzy matches are listed as "not written into the recipe" in the status. Covered by: D-0050, "the software informs, the user decides" (D-0015, quoted in the exploration of dates). [sonnet/high] (the second option needs a decision: Q5)
8. **Synthetic data says what it did.** After: the status lists, per column, how it was made (number range, list of values, placeholder, key pattern); date columns are generated as dates; a duplicate slider with no key says "no key column was found, no duplicates were made"; a seed box (shown, default fixed) and a config record in the download ZIP. Covered by: ADR-084 point 4, `rules_test_lab.md` section 9 (config record). The date column and the seed need a decision (Q4). [sonnet/medium]
9. **Anonymisation keeps ids consistent across files, handles a missing id, and says what it did.** After: the tool takes several files (uses `anonymise_batch`), names the new column, lists the columns not touched, warns that the mapping is private; a missing id gives a sentence; the hash pattern needs a secret or is removed. Covered by: `TEST_LAB.md:50-54` (consistent across files). Hash and secret: needs a decision (Q6). [sonnet/high]
10. **Reformatting says what it made, and deselecting all sheets means none.** After: "Wrote 3 sheets: A (120 rows, 7 columns) ..."; the delimiter is guessed and shown. Covered by: D-0050. [sonnet/low]
11. **Replace the silent `except Exception` defaults** (21) by a rule: a missing input is a plain sentence on the screen, never a default. After: nothing is chosen for the user. Covered by: D-0050. [sonnet/medium]
12. **Tests of the screen functions** (like `test_click_reads_visible.py`) for the five tools, with the edge cases of the rule `rules_verification_testing.md` section 9: empty file, one column, missing id, key not in all files, tab read as comma. Covered by: that rule section 9 (Eve's). [sonnet/medium]
13. **Words and records**: the right-hand panel and the Info panel say what the tools do and do not do (consistent ids only inside one file, until item 9); `rules_test_lab.md` known-bugs paragraph removed; `TEST_LAB.md` status line corrected; stale "not yet built" headers removed. Covered by: D-0050, D-0101 (short plain sentences). The Info panel text is Eve's placeholder decision of 2026-11-08: needs her to say the new text. [haiku/low] for the stale headers, [sonnet/low] for the rest
14. **The extractor**: wire it or remove it. Needs a decision (Q7). [haiku/low] to remove, [sonnet/medium] to wire
15. **A design pass** (the open task TESTLAB-REVIEW-1, `tasks.md:347`, `[opus/high]`): what each tool is for in the producer workflow, and the three ideas listed there (pilot recipe, tool-specific recipe, combine recipes). After items 1 to 12, not before. Covered by: Eve 2026-11-13. [opus/high]

Note on the existing task `TESTLAB-EMPTY-KEY-DEFAULT` (`tasks.md:605`, "waits for Eve"): items 3 to 5 cover it; the decision it waits for is Q2 and Q3 below.

## 4. What nothing decides (for Eve)

Each question has my default. Nothing was changed.

1. **Where do the data files live after scaffolding?** Options: (a) the ZIP holds copies of the data files next to the recipe, and the recipe points to them; (b) the recipe points to a folder the user types; (c) the recipe holds a placeholder path the user must edit. Default: (a), so that the ZIP runs as it is.
2. **What may the key of the scaffold be?** Options: one column; one column or a pair of columns; one column, a pair, or a date column. Default: one column, a pair of columns, and a date column of type `Date` (the exploration of dates, `2026-11-18_date_keys_and_joins.md`, recommends allowing typed date keys; the pair needs the join form of Blueprint). This is the same question as question 9 of the dates report; answer it once.
3. **Does the scaffold write a join at all?** The rule and ADR-084 say only an empty stub; the code writes an inner join on one key. Options: (a) empty stub only, the user designs the join in Blueprint; (b) a join that is written but marked "to check", with the report of rows with and without a partner; (c) as today. Default: (b), because Eve said "the joins will need to be done by the recipe" and the Blueprint join designer shows the match preview. If (a), item 4 shrinks.
4. **May synthetic data make dates and free text?** Options: dates as real dates and free text as placeholders (said on screen); everything as placeholders but said on screen; as today. Default: dates as dates, free text as `text_001`, and say it on screen.
5. **How is the ID cleaning step written?** Options: (a) as today for the whole column, but refuse a reconcile where the step would break an exact match; (b) written so that it acts only on ids that do not already match; (c) as today with a warning. Default: (a), the simplest and the most visible.
6. **Hash anonymisation:** keep with a secret the user must keep, or remove it and keep the sequential and custom patterns. Default: remove the unsalted hash; keep sequential and custom.
7. **The Excel extractor:** wire it into the screen, or remove it from the library? Default: remove it; the file reformatter already converts sheets, and a sheet-to-table mapping belongs in a recipe.
8. **Order:** do the Test Lab fixes (items 1 to 12) now, before the big format migration, or after it? Default: after the format change is merged, because items 2 and 6 would be redone; but items 3, 4, 7, 8, 9, 10, 11 do not depend on the format and can start now in a separate worktree. (This does not block the big build, M271.)
9. **The Info panel text:** short text for the five tools (what each does and does not do). Default: I write it from section 1 of this report and she reads it.

## 5. What I could not verify

- The screens: I did not start the app, so every "the user sees" is read from the code, except what I ran on the library functions.
- A scaffold from a real Shiny upload (I used files named `0.tsv`, `1.tsv`, the names Shiny gives, read from its source).
- Scaffolding from a comma file; the scaffold on a file with the key missing; the engine run on a scaffold whose join key does not exist.
- XLSX conversion with real Excel cells (dates, numbers stored as text).
- How Blueprint shows the checker problems of an opened scaffold.
- The test suites: not run; test counts are from `def test` counts.
- Whether the hash anonymiser collides on real ids (reasoned only).
