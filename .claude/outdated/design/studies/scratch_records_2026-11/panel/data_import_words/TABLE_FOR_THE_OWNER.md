# HOME, Data Import panel: the messages, old text and proposed text (for the owner; 2026-11-21)

Merged by the coordinator from two viewpoints: the data scientist (ran the ingestion on a test schema) and the user who is not a developer (read the code, saw no screen). They recommend; the owner decides. Nothing is built. Short names of files: `check` = `app/modules/data_import_check.py`, `handler` = `app/handlers/data_import_handlers.py`, `ingestor` = `libs/ingestion/src/ingestion/ingestor.py`, `declared` = `libs/ingestion/src/ingestion/declared.py`.

## 1. First: what is more than wording (found while reading the messages)

These change or hide something for the HOME user. Each needs a decision, not a new sentence. Run by the data scientist viewpoint on a test schema unless marked "read".

| # | What happens in HOME's Data Import today | Where |
|---|---|---|
| S1 | A row with FEWER cells than the heading line is accepted. The missing cells become empty, with no message. The tip says every row must have as many cells as the heading line; that is not what is checked. Rows with MORE cells are refused. | ingestor:117-119 |
| S2 | A file with headings and no rows is accepted. It replaces the table with 0 rows. Nothing says "0 rows". | handler:305 |
| S3 | Columns of the file that the recipe does not use are left out. The warning is only printed in the server log; the user never sees it. | ingestor:63-82 |
| S4 | A date column without a declared format is guessed (day/month or month/day). `03/04/2020` was read as 3 April. | declared (date read) |
| S5 | Words counted as "missing" by the recipe (for example NA) become empty cells with no count shown. "NaN" in a decimal column is kept as a number. | declared |
| S6 | Messages name the recipe's internal column name (`year`), not the heading in the user's file (`Year`). The user searches for a column that is not in the file. The ingestion knows both names. | declared:143,148; ingestor:46 |
| S7 | The missing-headings message sorts the internal names and the headings separately, so the two lists can pair wrongly. It does not show the headings the file does have, although they are available. | ingestor:46-47, 57 |
| S8 | A value problem shows at most 3 different bad values, with no count and no row. The engine gives no row today. | declared:21,142-152 |
| S9 | No refusal says that the old file is still in place. The success notice does not say that the old file is gone for good (no copy, no record of the uploaded name: task DATA-IMPORT-OVERWRITE). | check, handler:305 |
| S10 | After a failed write part-way, the message names the files replaced, not the files NOT replaced. It is the only case where the data is a mix of new and old. | check:271; handler:299 |
| S11 | Errors of the recipe itself ("null_values is missing", "type is missing", "not a Polars dtype") are shown to the HOME user, who cannot repair them. Tips tell the user to change the recipe ("declare String", "add to categories"). | declared:39-62, 101-152 |
| S12 | The file chooser offers .csv and Excel files, which are always refused, and does not offer .parquet, which a table stored as Parquet needs. (read) | handler:150,164 |
| S13 | A good file shows no mark when another file of the same upload is refused; the notice disappears after 8 seconds. (read) | handler:288-290 |
| S14 | The reason and the way out are split at the first " — ". A file name or a value that contains " — " is cut at the wrong place. Low risk. | handler:50 |

## 2. One pattern for every message (both viewpoints agree)

1. What happened: "Nothing was imported." or "Your file was imported."
2. What is wrong and where: file name, table, the heading as written in the file, the value in quotes.
3. One thing to do, or "ask the person who made the recipe" when the user cannot repair it.
4. For a refusal: "Your current data file is unchanged."
5. Last, "Details for your contact:" with the technical text (the engine's own words, the path, the type name).

Where the two viewpoints differ: the data scientist keeps the technical type in brackets in the main sentence, "whole numbers (Int64)", and keeps the engine's text under "Details" because it is the only place that names the column or the broken text. The user viewpoint puts every technical word after "Details for your contact:". Suggestion: plain word in the sentence, technical name only in the details.

## 3. Words to use everywhere

| Today | Proposed | Note |
|---|---|---|
| dataset, data schema, schema | table | one word only |
| candidate, source | your file (uploaded); the data file (the one the app reads) | |
| input_fields, slug, original_name, header | heading (the name in the first line of the file); column | always show the heading of the file |
| Int64, Float64, String, Boolean, Date, Enum, dtype | whole numbers, numbers with decimals (written with a point), text, true/false, dates, "only these values: ..." | technical name in the details |
| null, NA, null_values | empty cell; "a word that means unknown" | |
| deployment, pipeline | this installation; an automatic process; the person who runs this installation | |
| recipe author | the person who made this recipe ("your contact") | |
| bundle | bundle or package: to choose | the user viewpoint proposes "package" |
| Validate & Apply | "Check and import" (user) or "Check and replace" (data scientist) | the button replaces the file for good |

## 4. The messages

A = the user can repair it alone in a spreadsheet. C = the user must ask the contact.

### 4a. Labels of the panel (`handler`)

| Where | Text today | Proposed text | Reason |
|---|---|---|---|
| :91 | "Data location (provided by deployment):" | "The data files of this app come from a folder set by your administrator:" | jargon; does not say upload is off |
| :110-116 | "{id}: {path}" | "Table {name}: your current data file is {path}" | a bare id says nothing |
| :127 | "No source files resolved for this data analysis recipe." | "The app found no data file for this recipe. Ask the person who made the recipe." | jargon |
| :134 | "Data paths are set by the deployment configuration (read-only)." | "You cannot replace data files here. They are set by your administrator." | jargon |
| :154 | "Select a tab-separated (.tsv) file to replace the active data analysis recipe source." | "Choose a tab-separated text file (.tsv). It replaces the metadata table of this recipe." | the list holds only the metadata table |
| :159 | "Data file(s) — assign each file to a dataset below" | "Choose your data file(s). Then say which table each file replaces." | jargon |
| :168-169 | "The file must have the column headers the recipe reads from its data file. CSV and Excel files are refused: convert them to a tab-separated file first." | "Your file must be a tab-separated text file (.tsv). The first line holds the column headings, written exactly as the app expects (capitals count). Excel and CSV files are refused: nothing is converted for you. The whole file is checked before anything is replaced. The file you choose replaces the current data file for good; no copy of the old one is kept." | S9: the truth before the choice |
| :221, :233 | "— select dataset —", "Assign each file to a dataset:" | "— choose a table —", "Which table does each file replace?" | words |
| :237 | "Validate & Apply" (with a green tick) | "Check and import" or "Check and replace" | the tick reads as "already accepted" |
| :267 | "Checking {n} file(s) — please wait…" | "Checking {n} file(s). Nothing is changed yet." | says this step is safe |

### 4b. Notices after the button (`handler`, `check`)

| Where | Text today | Proposed text | Reason |
|---|---|---|---|
| handler:288 | "Nothing was imported: {k} of {n} file(s) cannot be used — see the reasons above. Fix or re-assign the files and apply again." | "Nothing was imported. {k} of your {n} files cannot be used (see below each file). Your current data files are unchanged. All files are imported together, so the other files were not imported either. Fix the files and press the button again." | S9, S13 |
| check:261 | "Nothing was imported: could not write '{file}' to {target}: {error}" | "Nothing was imported. The app could not save '{file}'. Your current data files are unchanged. Try again; if it fails again, ask your contact. Details for your contact: {target}, {error}." | technical text last |
| check:271 | "The import stopped at '{file}' ({target}): {error}. Files already replaced: {paths or none}." | "The import stopped part-way. REPLACED with your new file: {files, tables}. NOT replaced, the old file is still there: {files, tables}. Your tables may not match each other now. Upload the remaining files again, or ask your contact. Details for your contact: {target}, {error}." | S10 |
| handler:305 | "{n} file(s) imported — plots are refreshing now. {file} -> {tables} ({path}); ..." | "Your file was imported: '{file}' is now the data of the table(s) {tables}. The previous data file was replaced and is not kept. The plots are refreshing now. Details for your contact: {path}." Optional, needs code: "{rows} rows read; these columns of your file were not used: {headings}; {m} cells read as empty." | S9; S2, S3, S5 if the owner wants the counts |

### 4c. Refusals written in `check`

| Where | Text today (reason — way out) | Proposed text | Who |
|---|---|---|---|
| :201 | "No dataset selected. — Choose the dataset this file replaces." | "Nothing was imported. For '{file}' you did not say which table it replaces. Choose a table in the list." | A |
| :203 | "The data analysis recipe '{recipe}' has no dataset '{id}'. — Choose one of the datasets of the recipe." | "Nothing was imported. The recipe '{recipe}' has no table '{id}'. Choose one of the tables in the list." | A |
| :205 | "More than one of the files is assigned to the dataset '{id}'. — Assign each dataset one file." | "Nothing was imported. You chose more than one file for the table '{id}': {files}. A table has one data file. Keep one." | A |
| :220-222 | "The datasets 'A', 'B' are read from the same data file ({name}), and more than one of the files of this Apply is assigned to them. — Upload one file for them: they share one data file." | "Nothing was imported. The tables 'A' and 'B' use the same data file ({name}), so one file replaces both. You gave more than one file for them. Keep one." | A |
| :47-49 | "This recipe was imported from a bundle and reads its data from the folder of that import ({folder}); Data Import cannot replace it here. — The data of an import is only what its bundle carried. To use other data, import a bundle that holds it." | "Nothing was imported. This recipe came from an imported bundle that contains its own data. Its data cannot be replaced here. To use other data, import a bundle that contains it. Details for your contact: {folder}." | C; provisional refusal, see the owner's question a |
| :55-56 | "The data of this deployment is delivered by the pipeline and cannot be replaced from here. — To use other data, ask the person who runs this deployment to supply it." | "Nothing was imported. In this installation the data files are delivered by an automatic process and cannot be replaced here. To use other data, ask the person who runs this installation." | C; provisional refusal, see question b |
| :133-134 | "The file of this dataset is a Parquet file ({name}); '{file}' is not, and Data Import does not convert files. — Upload a Parquet file for this dataset." | "Nothing was imported. The data file of the table '{id}' is a Parquet file ({name}), a format a spreadsheet cannot make. '{file}' is not a Parquet file, and nothing is converted for you. Ask your contact for a .parquet file." | C |
| :137-138 | "'{file}' is a comma-separated file / an Excel file. This dataset is read from a tab-separated file ({name}), and Data Import does not convert files. — Convert it to a tab-separated file (.tsv) first, then upload it again." | "Nothing was imported. '{file}' is an Excel file (or: a comma-separated file). The table '{id}' needs a tab-separated text file (.tsv). In Excel: File, Save As, 'Text (Tab delimited)'. Then choose the new file." | A |
| :140-141 | "'{file}' is a Parquet file. This dataset is read from a tab-separated file ... — Convert it to a tab-separated file (.tsv) first ..." | "Nothing was imported. '{file}' is a Parquet file, but the table '{id}' needs a tab-separated text file (.tsv). Ask your contact for the data as a .tsv file." | C |
| :142-143 | "'{file}' is not a file type this dataset can be read from. It is read from a tab-separated file ({name}). — Upload a tab-separated file (.tsv)." | "Nothing was imported. The name of '{file}' does not end in .tsv. If the file is already tab-separated, rename it to end in .tsv. Otherwise, in Excel: Save As, 'Text (Tab delimited)'." | A; true only while a file is refused by its name (provisional) |
| :234 | "This file is also the data file of the table '{other}', and '{other}' cannot read it: {message} — {way out}" | "Nothing was imported. Your file works for the table '{id}', but the same data file is also used by the table '{other}', and '{other}' cannot read it: {the problem, worded for '{other}'}." | A or C; the most surprising refusal |

### 4d. Refusals that come from the ingestion (`ingestor`, `declared`)

| Where | Text today | Proposed text | Who |
|---|---|---|---|
| ingestor:46-56, check:60 | "Column(s) ['id', 'year'] declared in input_fields for 'T' not found in the source file (expected file headers: ['Sample ID', 'Year']). — Correct the column headers of the file so that they are spelled exactly as the expected file headers above (upper and lower case count), then upload it again." | "Nothing was imported. Your file '{file}' has no column with the heading: 'Sample ID', 'Year'. The headings in your file are: {the file's own headings}. Rename the headings in the first line exactly like that (capitals, spaces and punctuation count), save and choose the file again. Details for your contact: table '{T}', names in the recipe: id, year." | A; needs S6 and S7 in code |
| declared:148-152 | "Data schema 'T': values that do not fit the declared type. The column 'year' is declared as Int64. The data holds the values 'abc', '2020a', which cannot be read as that type. — Suggestion: correct the data, or declare the type that column 'year' really has (Float64 for decimals, String if it is text). Suggestion: list the word in null_values if it means missing." | "Nothing was imported. In your file '{file}', the column '{heading}' must hold whole numbers. Some cells hold something else: 'abc', '2020a' (the first 3 different values are shown). Correct these values, or leave the cell empty if the value is unknown. Then choose the file again. Details for your contact: table '{T}', type Int64; if the column really holds text, or a word should count as an empty cell, the recipe must change." For decimals add: "a number with decimals is written with a point, not a comma". | A mostly; no row can be promised (S8) |
| declared:143-146 | "The column 'country' is declared as Enum with the values NO, SE, DK. The data holds the value 'Norway', which is not in that list. — Suggestion: add the value to `categories` of 'country' in the recipe if it is a real level. Suggestion: correct the data if it is a typing error ..." | "Nothing was imported. In your file, the column '{heading}' may only hold these values: NO, SE, DK. It holds 'Norway' (the first 3 are shown). Spelling, capitals and spaces must match exactly. If it is a typing mistake, correct it in the file. If 'Norway' is a real new value, ask your contact to add it to the recipe." | A or C, and the text says how to tell |
| declared:128 | "... a Boolean reads the words true and false (upper or lower case); change the data." | "The column '{heading}' must hold true or false (capitals do not matter). It holds 'yes'." | A |
| declared (date) | only the engine's text | No honest text today: the date order is guessed (S4). A text follows the owner's decision. | decision first |
| ingestor:114-115 | "The file '{file}' is empty: it has no header line and no rows. — Upload a tab-separated file with a header line and the data rows." | "Nothing was imported. '{file}' is empty. Check that you saved the right file, with the headings in the first line and the data below." | A |
| ingestor:117-119 | "The file '{file}' cannot be read in full: {the engine's text, 200 characters}. — Check that every row has as many tab-separated fields as the header line, that every quote is closed, and that the file is saved as UTF-8 text." | "Nothing was imported. The app cannot read all of '{file}'. One of these is the cause: a row with more cells than the first line; a quotation mark that is never closed; the file is not saved as UTF-8 text. In Excel: Save As, 'Text (Tab delimited)'. Details for your contact: {the engine's text}." A separate sentence for a Parquet file: "'{file}' is not a valid Parquet file." | A usually; say "one of", the engine does not name the cause; "more cells", not "as many" (S1) |
| ingestor:100-101 | "Failed to read '{file}': {ErrorName}: {text} — Check that the file is a valid tab-separated file and that the declared fields match it" | "Nothing was imported. The app could not read '{file}' for this table. Check that it is a tab-separated text file with the expected headings. Details for your contact: {ErrorName}: {text}." | rare |
| declared:39-63 | "Data schema 'T': null_values is missing or is not a list of texts — Write null_values on the schema ..." and four alike | "Nothing was imported. The recipe is not complete for the table '{T}', so no file can be checked. This is not a problem with your file. Ask the person who made the recipe. Details for your contact: {today's text}." | C (S11) |
| check:185 | the loader's own text when the recipe cannot be loaded | "Nothing was imported. The app cannot open this recipe, so it cannot check your file. This is not a problem with your file. Ask the person who made the recipe. Details for your contact: {the loader's text}." | C; today's text not read |
| ingestor:28-30 | "Dataset '{id}' has more than one file in {dir}: a.tsv, a.parquet. — Keep one file per dataset id: remove or rename the one that is not the data to read." | "Nothing was imported. The data folder holds two files for the table '{id}' (a.tsv, a.parquet). The app does not know which one to replace. Ask your contact to keep one. Details: {dir}." | C |

Every refusal above ends with "Your current data file is unchanged." (left out of the rows to keep them short).

## 5. To decide (ranked)

1. S1 to S5: accept or refuse a row with fewer cells, a file with no rows, a guessed date; show or not the columns left out and the cells read as empty. These touch the data, not the words.
2. The pattern of section 2 and the words of section 3 ("table", "heading", plain type words; "bundle" or "package"; the name of the button).
3. Show the heading of the file and the file's own headings in the messages (S6, S7): a small code change in the ingestion.
4. Say before the upload and after it that the old file is replaced for good (S9), until DATA-IMPORT-OVERWRITE is decided.
5. Recipe errors shown to a HOME user (S11): one plain text plus details.
6. The file chooser (S12), a mark on accepted files (S13), the count and row of bad values (S8), the split at " — " (S14).

## Not verified

No screen was seen. The data scientist viewpoint ran the ingestion on a test schema, not on a shipped recipe; one case only for rows with fewer cells; no Parquet upload; no long file (the 200-character cut). The recipe loader's own text was not read. Whether a notice of 8 seconds can be read, and how long texts wrap, is not known. Whether "package" and the Excel instruction are understood needs a real user.
