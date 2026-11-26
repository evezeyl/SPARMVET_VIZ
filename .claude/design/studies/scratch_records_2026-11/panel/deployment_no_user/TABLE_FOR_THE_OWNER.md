# Deployments where no user interacts: one table for the owner (2026-11-21; your order D-0428)

## 0. How to read this

- Your order (D-0428, your words): "we need a way for static deployment to put several data files and where to be fetch". Your cases: a recipe that shows data refreshed every week and pushed into a folder; a pipeline that needs a temporary place the app can read and write and the user cannot; a static deployment with several data files and where each is fetched. The place must be stated "without being associated to a specific user", as a configuration specification. The output you asked for: this table, plus the configuration text, as a section of the structure of the one deployment specification (D-0417, D-0418).
- What you decided while this was written: D-0429 (what is saved is user associated; a common place only if the system administrator declares it; a static deployment on Connect has no user place and no save control) and D-0430, D-0431 (one copy of the app per person is enough for now; sharing is the user's responsibility).
- What was done: a scout surveyed the code (`FACTS.md`). A reviewer ran ten cases on a scratch static page in a browser (`RUN_FACTS.md`, screenshots in `run_scratch/shots/`). A second run cut a data file in several ways (`tmpAI/coordinator/data_file_cut/REPORT.md`). Four viewpoints then answered the ten questions: the architect (`architect.md`), the scientist and data scientist (`scientist.md`), the developer (`developer.md`) and a deployer who is not a developer together with a visitor of the page (`deployer_and_visitor.md`). All in `tmpAI/panel/deployment_no_user/`.
- Nothing is built. Nothing is decided by this table. Every key name and every sentence for a screen below is a proposal. I say whose proposal each point is: A = architect, S = scientist, D = developer, V = deployer and visitor.
- Labels: RUN = it was run and seen. READ = read in the code at file:line. REASONED = a conclusion, not run.
- Your rule is applied: each option is judged on its merit. "Reconsiders a decision?" is its own column, information only.
- Words, the first time. **Stored tables**: the tables the app has already built and keeps so the next opening is fast (called "anchors" in the code; they can always be rebuilt). **Session record**: a small file the app writes for one session so it can be restored (`assembly.json`). **List of delivered files**: a small file, written last by whoever refreshes the data, that names every data file with its size and its hash (a short code that changes when one byte changes), and the date of the delivery. It is my plain name for what the briefs call a list; it is not a word of yours.
- Detail stays in the five files above. This table points to them.

Added 2026-11-21 after this table was written: you chose two access words for a place, `read` and `read_write` (ledger D-0437). Where an example below shows `read_only`, `add`, `replace` or `write`, read `read` or `read_write`. You also chose that the change to the named places is made with no temporary reader of the old keys (ledger D-0436), and that a bundle import writes into the user's own places (ledger D-0435).

Added 2026-11-21: you asked to investigate how new data and a new recipe reach a static page (ledger D-0442), and thought Posit Connect redeploys an app when data or recipes change. Checked against Connect's own documentation: it does not, except for content backed by a git repository (a fetch about every 15 minutes). The report, with the quoted sentences and five options for a static page, is `PLATFORMS_REFRESH.md` in this folder; read it with question 3 of section 5 (refreshed data) and question 5 (fetching).

## 1. FIRST: what changes a result silently today

Read this section before the rest. Each row says what the visitor sees, the evidence, and which proposal below would close it.

| # | What happens | What the visitor sees | Evidence | Closed by (section) |
|---|---|---|---|---|
| 1 | **A data file cut in the middle of a line is accepted.** The plot is drawn from the rows that are there. | Nothing. No message, "Alerts (0)". The plot shows 21 of 42 samples. | RUN, case 7a (`shots/c7a_A_afterF5_broken.png`); cause READ `libs/ingestion/src/ingestion/ingestor.py:141, 200, 211` (Polars fills a missing field with "missing" and gives no error) | The list of delivered files (5.3) catches it. A field count per row catches part of it (table below). |
| 2 | **A refresh of several files is not one event.** File A of this week can be joined with file B of last week; every check passes. | Nothing. A table that mixes two weeks. | REASONED from `app/modules/cache_keys.py:139-158` (each file is read on its own, nothing ties the files together). RUN covered one file only. | The list of delivered files, or a version folder per delivery (5.3). |
| 3 | **An open page keeps old data.** | The picture does not change for at least 60 s. After a click on another plot tab: one yellow notice that fades ("reload the page (F5)"); the open plot stays the old one. A new visitor sees the new data. | RUN, case 5 | A persistent notice and a check of the list of delivered files (5.3, 5.4). |
| 4 | **Nothing on screen says which data is shown.** No date, no hash, no file name, no number of samples. | Only the recipe's own `info` block (its version, for example 1.8). | RUN, case 5d (`shots/c5d_info_panel.png`) | 5.4 |
| 5 | **The pipeline-style lookup reads other files than the recipe declares, and says nothing.** | Nothing. | READ `app/modules/orchestrator.py:172-195`; `tmpAI/coordinator/default_data/FACTS_FOR_THE_OWNER.md` (finding 1, RUN there) | One rule, shown on screen (5.6) |
| 6 | **A changed data file is blamed on the recipe.** A renamed column gives "Correct original_name, or remove the declaration", and the recipe author's e-mail. It does not say that the data file changed or which headers it has now (only the console does). | A page "No data analysis recipes yet" and the long reason. Someone may edit a correct recipe to fit a broken delivery, which changes the science. | RUN, case 6; READ `libs/ingestion/src/ingestion/ingestor.py:50-51` | The sentences of 5.9 |
| 7 | **A write nobody can use.** A static page writes 24 stored tables and a session record with no click, and the session record is shared by all visitors. | Nothing on the page; the record cannot be restored by anyone. | RUN, cases 1 and 4; READ `app/handlers/home_theater.py:1567` (no flag stops it) | 5.1 |
| 8 | **The date of the data could change inside one session.** Your decision D-0025 says "data hash = full content once per session". The code reads all data files each time the effect runs. | If a hash is shown on screen, it could change while the page is open. | READ `app/handlers/home_theater.py:1528-1529`, `app/modules/orchestrator.py:809-820` against `app/modules/cache_keys.py:350-351` (the docstring repeats "once per session") | 5.10: settle before a hash is shown |

### What the cut-file study found, in short (RUN on a copy of the demo `FastP.tsv`: 14 header fields, 42 rows)

Detail: `tmpAI/coordinator/data_file_cut/REPORT.md`. The reader, Data Import's check and the load gate all behave the same.

| How the file is cut | Accepted? | The plot shows |
|---|---|---|
| (a) last row cut in the middle (7 of 14 fields, no line end) | yes, no message | 21 of 42 samples |
| (b) cut exactly at the end of a line | yes | 20 of 42 samples; every row looks complete |
| (c) last value cut inside the value, all fields present (0.9235 became 0.91) | yes | 21 samples; the last value is wrong |
| (e) last line complete but with no line end | yes (correct) | all 42 |
| (g) a spreadsheet left out the last empty fields of two rows | yes (correct) | 42, same as with the tabs kept |
| (d) cut inside an open quote | refused with a reason | the recipe is refused |
| cut inside a 2-byte character (RUN, case 7b) | refused with a reason | the recipe is refused |

What follows (facts of the cut-file report):
- A file cut at the end of a line cannot be told from a complete file by any check inside the app: every row is complete (b). A cut file with all fields present (c) cannot either. Only something delivered with the file (a row count, a size, a hash) catches them.
- A row with fewer fields than the header cannot be told from a spreadsheet export that left out empty fields (a against g). A field count per row would refuse (g), which is a normal file. A "file ends with a line end" check would refuse (e), which is a correct file.
- Today no decision covers a row with fewer fields (D-0034 is about header columns; D-0035 and D-0057 about values; D-0427 about a file that is absent). The sentence of `ui_implementation_contract.md` section 9 point 2, "a row with more fields than the header is refused", is also only partly true (a row with more fields is accepted when the extra field is in a column that is not read; RUN in the report).
- The options of the cut-file report (1 refuse a short row, 2 only warn, 3 refuse only when a declared field is missing, 4 nothing, 5 add a count or hash delivered with the file) are not repeated here; they are choice 1 in section 7.

## 2. What a static page does today (RUN, scratch static page, `pipeline-static` app features)

Times: from the page request to the plot. The load of the machine was 3 to 10 during the runs, so the 22 to 31 s first-opening figure is not a quiet-machine figure.

| Case | What the visitor sees | What the operator sees | Evidence |
|---|---|---|---|
| 1 baseline | The recipe opens, four group tabs, a plot and a table. First opening on an empty user folder: 30.7 s; later visits 2 to 4 s. No date, no data version. | Normal lines, warnings that columns of 7 tables are not declared. The page wrote 25 files (24 stored tables, 1 session record) with no click. | `shots/c1_baseline.png` |
| 2a user folder empty and read-only | A blank grey page, no text, the grey "disconnected" overlay | The app starts. At every connection a Python error `PermissionError ... _sessions` from `app/src/server.py:149` and `app/modules/session_manager.py:274`. Nothing at start. | `shots/c2a_readonly_empty.png` |
| 2b user folder read-only but already holding the stored tables | The plot is shown from the stored tables (5.4 s). Two red notices that name server paths and show a Python error text. | no error trace | `shots/c2b_readonly_stored.png` |
| 3 user folder missing, parent read-only | Same blank grey page | `FileNotFoundError` then `PermissionError` | `shots/c3_no_user_folder.png` |
| 4 two visitors | Both work. First visitor 31.2 s, second 3.1 s. Both share one session record. | no error | `shots/c4_visitorA.png`, `c4_visitorB.png` |
| 5 a data file replaced while the page is open (5 rows fewer) | Nothing changes for 60 s. After a click on another plot tab: a yellow notice "A source data file of this project changed ... reload the page (F5)"; the open plot stays old. After F5 (22.1 s): the new picture. A new visitor (2.2 s): the new data, no notice. | no line says a file changed. After F5, 4 of 24 stored tables were rewritten under the same names, no history. | `shots/c5_*.png`, `logs/case5.out` |
| 5d is the data or its date told | No. Nothing on the page shows a date, a hash, a file name or a file time. | | `shots/c5d_info_panel.png` |
| 6 a refreshed file with another column name | After a click: the same fading notice. After F5 and for a new visitor, no plot within 60 s: a light-blue page "No data analysis recipes yet" with a long reason that says "Correct original_name" and the author's contact. The wrong page stays as long as the file is wrong. | the console says which headers the file has now | `shots/c6_A3_afterF5.png` |
| 6r the good file put back | Without a click or a reload, within 5 s, the page returns to the plot and shows "A source data file of this project changed. The tables and plots are rebuilt from the new files." | | `shots/c6r_A_after60s.png` |
| 7a file cut in the middle of a line (4179 of 8346 bytes) | No message. The plot is drawn from 21 of 42 samples. After the full file is back, an open page shows nothing until F5. | no error or warning | `shots/c7a_A_afterF5_broken.png` |
| 7b file cut inside a 2-byte character | The "No data analysis recipes yet" page with "invalid utf-8 sequence". Good file back: the page recovers by itself within 5 s. | an error line per table | `shots/c7b_A_afterF5_broken.png` |
| 8 data file absent at start, selector hidden | No page: "connection refused" (the process has exited). | The process prints "Deployment failed - 1 fatal error(s)", names the recipe and the table, "Who: operator", and exits. READ `app/src/bootloader.py:617-626`. | `shots/c8_absent_visitor.png`, `logs/w8_8741.log` |
| 9 two copies on the same folders, opened together | Both show the plot after 22.5 s | no error | 24 stored tables of each copy compared one by one with a clean run: 0 different |
| 10 `TMPDIR` (the system variable that names the temporary folder) not writable, export | The export downloads (smaller, 488 KB) and a notice says Quarto could not render the report and "install Quarto". The cause is the temporary folder. | | `shots/c10ro_after.png` |
| 10 `TMPDIR` writable | The export is complete (2.5 MB), no notice. The folder named by `TMPDIR` is used by the app and by Quarto (the report renderer). | | `logs/c10rw2.out` |

What a static page needs today to work (RUN): a user folder that the app can write, although the page only shows data; read access to the recipe and the data; a recipe that passes the check at start; a reload by the visitor to see new data; a writable temporary folder for the export.

## 3. What is decided already, what only confirms a reading, what is open

CONFIRM means: the code shows it today, no decision of yours says it.

| Point | Status | Source |
|---|---|---|
| One deployment specification for all cases, built on named places with an access word | DECIDED | D-0417, D-0418 |
| What a person saves is in a user place whose path comes from variables of the system; the app runs once per person; a common saving place only if the system administrator declares it; a static deployment on Connect has no user place and no save control (absent, not greyed) | DECIDED (the numbered points are the review session's reading) | D-0429, D-0430, D-0431 |
| No audit on a static pipeline page | DECIDED | D-0302 |
| The audit folder `audit/` is inside the session folder in the user's place; a deployment with no writable user place: not decided | DECIDED, with that point open | D-0422, D-0423, D-0340 |
| The same recipe name in two places: identical content is one entry, different content is refused | DECIDED (for recipes; for data tables not asked) | D-0424 |
| The deployment file decides what a recipe's data path may reach; shipped recipes keep their paths; the local deployment declares `assets/test_data/` | DECIDED | D-0425 |
| Where the user can select data, the user selects; never a silent run on other data | DECIDED | D-0426 |
| Where the user cannot select data and the declared data is absent, "the opening should stop with a plain reason" | DECIDED; whether the whole process exiting is that "opening" is not stated | D-0427 |
| Data Import replaces a file only in the user's own place, with a dated copy | DECIDED | D-0432 |
| Where the stored tables are among the named places | OPEN (you asked "where is the cache in A?"; not answered) | D-0418; today `<user_data>/anchors` (READ `app/src/bootloader.py:204`) |
| What the app does when no place can be written (choice 5: stop, this session only, memory) | OPEN | deployment study choice 5; D-0340 only asks "a plain error when the directory cannot be written" |
| The data hash "once per session" | DECIDED, and the code reads the files at every effect run | D-0025; READ `home_theater.py:1528-1529` |
| The key of a Gallery picture; whether fonts are a named dependency of the deployment | OPEN (goes to the deployment study) | D-0400 |
| The app fetches nothing today | CONFIRM (READ: no download code in `app/` or `libs/`; `libs/connector/src/connector/irida.py:40-52` is a stub that raises `NotImplementedError`) | FACTS D |
| The `cache` key of the deployment file is read by nothing | CONFIRM (READ `app/src/bootloader.py:348` only checks it exists) | FACTS B10 |
| A row with fewer fields than the header | OPEN: no decision covers it | cut-file report |

## 4. The answer in short: what the four viewpoints agree on

"Agree" below means: I checked the claim in each of the four files, and each recommends it, possibly in other words. Where a viewpoint differs, I say so.

1. **The app fetches nothing itself; a step outside the app delivers the data** (A: a command of the connector library; S: a step run by the deployment; D: cron or a pipeline step, a connector fetch only if you want it; V: a scheduled job or a pipeline step). All four. Their reasons: the app stays read-only on data, holds no token, and a failed fetch leaves the previous data in place.
2. **A static page has no user place and writes no session record** (A, S, D; V says it should not write one at all). All four. This also removes the cause of the blank grey page (RUN 2a, 3). It is a code change: today the session folder is built for every browser connection (READ `app/src/server.py:149`).
3. **The stored tables leave the user folder for a place that is tied to no user** (A, S, D, V). All four. They differ on one place or two (below).
4. **A list of delivered files with hashes, written last by the refresh, is the only complete answer to a cut file and a mixed delivery** (A, S, D, V all propose it; the cut-file report reaches the same fact for a cut at a line end). They differ on whether it is required (below).
5. **The app checks by itself against that list, whatever was promised** (A, S, D, V). The check of a file without a list differs (below).
6. **The date of the data comes from the list, not from the file time** (A, S, D, V). A copy or a container layer changes the file time.
7. **The page and the export show the date, a short hash and the number of rows or samples** (A, S, D, V). They differ on where (banner, Info panel, both).
8. **The temporary place is a named place of the deployment that the app applies itself** (A, S, D, V). `TMPDIR` alone is a process variable that a deployer must remember and that no file records. S would keep the variable as an override that the app reports; A says the file wins.
9. **For "nothing writable" the safe default is to stop with a plain reason, and any other behaviour is chosen in the file with its cost written beside it** (A, D, V). S leans to the same for a local install but would accept "this session only, with a visible line" for a static page. None recommends "in memory" first.
10. **One rule for which file feeds which table, shown on screen** (A, S, D, V). They differ on the rule (below).
11. **The export notice that blames a missing Quarto when the temporary folder is the cause is wrong** (A, S, D, V).
12. **Two copies on one folder are safe for the stored tables** (A, S, D): they are written by temporary name then rename, and keyed by content (RUN case 9: 24 tables identical). The session record is not written atomically (READ `app/modules/session_manager.py:392`), which does not matter on a page that does not write it.

Where the viewpoints differ (these are choices in section 7):
- One place or two for the app: A and V say one (with sub-folders); S and D say two (kept tables; temporary place). D says "one place with a sub-folder is enough" is an open alternative.
- Is the list of delivered files required: A required, with an explicit `none` the deployer must write; S required, or the page says "not verified"; D preferred, with a notice and not a refusal when missing; V "I can promise it".
- What a failed delivery does to a page that is up: S, D, V keep showing the last complete data, with its date and a message; A refuses the new delivery with a reason and checks again by itself (the page heals; RUN 6r shows it can). A does not say the old picture stays.
- Data absent at start: all four want a plain page for the visitor, not "connection refused". A wants it only where the deployer wrote `delivery: required`; a pipeline run should exit. D says serving such a page is the largest item of work (the process exits today, `bootloader.py:617-626`).
- A table that the deployment does not list: D says it is not read; S and V say it falls back to the file with the table's name in the data folder; A says each data place declares how its files are found.
- A place key that is absent: D says default to today's behaviour (user folder, system temporary folder) so a local install does not change; A says refuse the old `cache` key and require the new place.

## 5. The proposals, question by question

Columns: option | what the visitor sees | what the deployer must do | what it costs or risks | who proposes it | reconsiders a decision? (information only).

### 5.1 The app's own place

Fact (RUN 1, READ FACTS B): with no click the static page writes stored tables under `<user_data>/anchors` (every opening: `app/handlers/opening_handlers.py:124-127`), a session folder at each browser connection (`server.py:149`), a session record per recipe and data state (`home_theater.py:1515-1578`), and temporary files in the system temporary folder for export and report (`app/handlers/export_handlers.py:970, 1238, 2043-2057`). The deployment key `cache` is read by nothing, although `docs/workflows/connector.qmd:131, 137` and `config/deployment/templates/deployment_template.yaml:65-67` say the engine writes it.

| Option | What the visitor sees | What the deployer must do | Cost or risk | Proposed by | Reconsiders? |
|---|---|---|---|---|---|
| P1. One place `work` of the app. Holds the stored tables and the scratch folders of one run (sub-folders `tables/`, `tmp/<run>/`). Access fixed by its kind: the app reads, writes and deletes there. | Nothing. | Creates the folder (or binds it in a container). The app makes the sub-folders and, at start, writes and deletes one test file. | Stored tables and scratch share one disk. A `work` place shared by two people holds derived copies of their private data (A flags it: no check inside the app). | A (the key name `work` is A's), V (`app_work`) | The old key `cache` is replaced and refused with a message naming the new key (A). Five location keys of ADR-048 are already reconsidered by D-0418. |
| P2. Two places: a kept place for the stored tables (`app_store`, S: `work`) and a temporary place for one run or one export (`app_scratch`, S: `scratch`). | Nothing. | Creates and binds two folders. | Two keys, two tests at start, two ways to forget a bind (A). Gain: tables on a persistent disk, scratch on a temporary disk in a container. A says this can be added later as one optional key without breaking P1. | S, D | none |
| P3. Keep the stored tables in the user place (as today). | A static page needs a user folder it cannot use. Blank page when it is not writable (RUN 2a). | Gives a writable user folder to a page with no user. | Contradicts D-0429 for a static page. | nobody | Conflicts with D-0429 point (4) (information). |

What the place never holds (A, S, D, V agree): sessions, audit files, imports, recipes, a copy of the data, anything a person chose to keep or that cannot be rebuilt from the recipe and the data. S: "a reviewer must be able to say that the work place holds no result, only a cache". Who creates it: A says the operator creates it (a missing bind in a container would otherwise write into the container's own layer and be lost at restart); V says the app may create it when the parent exists and can be written.

What a static page should NOT write: the session folder and the session record (A, S, D, V). Also no Gallery index unless the Gallery is on (A; READ `bootloader.py:226-231`).

Preparation before any move (A, a small step): replace the ~19 hand-written `get_location("user_data") / "anchors"` by one function (D counts ~23 places). It changes no behaviour.

Configuration text: section 6.

### 5.2 Nothing writable (choice 5)

| Option | Visitor sees | Operator sees | Cost | Sound for | Proposed by | Reconsiders? |
|---|---|---|---|---|---|---|
| N1 stop at start with a plain reason | Nothing from the app ("connection refused", unless the app serves a plain page, 5.9) | One console block: the place, the error, how to fix | none | A: pipeline run, local install, a static page with a configuration error. S: local install, static page. D, V: yes | A, S, D, V | none (D-0340 asks only for a plain error) |
| N2 "this session only": the app works in a private temporary folder of this run, removed at exit; the deployer writes it as an explicit word | The page, plus a line "nothing is kept" (S) | A line at start naming the folder | The first opening after each start takes 22 to 31 s (RUN, under load). Many visitors: the first pays, the others share the tables (RUN 4: 31 s, then 3 s). Each process of a multi-process host pays its own. | static page without a bound folder; a pipeline run (short, natural) | A (as `work: temp`), S, D, V | none |
| N3 in memory | as N2 | as N2 | A second storage way in the engine, tested twice; memory grows; lost at restart. D says the code path is the same as N2 ("a build that is not stored", READ `home_theater.py:536`, `anchor.py:169-170`), but it is not tested with all stages and exports. | a short run (D) | nobody recommends it first. A: the export needs a disk anyway (RUN 10). | none |
| N4 (A and D): N1 when the place is absent or unwritable; N2 (or N3) only when the deployer writes it as an explicit word; the checker refuses features that need what is missing (export needs a writable scratch; session management needs a user place) | as N1 or N2 | as N1 or N2 | the cost of the word the deployer chose | all three cases | A, D (D's word: `app_store: none`) | none |

Rule behind N4 (A): the app never falls back silently to the system temporary folder; today it does (`TMPDIR`). RUN: today a read-only user folder gives a blank grey page with no text (RUN 2a), which is none of N1 to N3 and the worst of all (S).

### 5.3 Refreshed data and the list of delivered files

**How the app learns that the data changed.**

| Option | How | Pro | Con | Proposed by |
|---|---|---|---|---|
| L1 at each opening, by content (today) | hash all data bytes | exact | an open page learns only at a tab click (RUN 5); the poll (every 2 s, READ `app/handlers/recipe_gate_handlers.py:25`) watches only refused recipes (READ `app/src/bootloader.py:546-548`) | today |
| L2 the existing 2 s poll also reads the small list of delivered files and compares its content | one small file read, no rehash of the data; the notice arrives with no click | needs the list | A, D (extension of the poll), S |
| L3 a signal file | the name says "done" | says nothing about what was delivered; no hash | A (not recommended) |
| L4 a version folder per delivery and a pointer (`current`) that the refresh flips in one rename | last week's data stays; no half state | the deployer must keep disk; the refresh must flip the pointer | S ranks it first for a cited figure; A uses it as a way to use the same list; D lists it |

**What the refresh promises** (A, S, D, V): write each file under a temporary name, rename it, and write the list LAST (also under a temporary name, then rename). The list holds the date of the delivery, and per file: name, size in bytes, hash; optionally the number of rows and the source address. Form: section 6, block 4. A pipeline that cannot run a helper writes the same file itself.

**What the app checks regardless of the promise.**

| Check | Catches | Costs | Proposed by |
|---|---|---|---|
| Every listed file exists; size and hash match; no table the recipe needs is unlisted | cut file at any place, mixed delivery (a mixed state does not match the list) | one comparison; the app already reads all bytes to hash them (`cache_keys.py:146`) | A, S, D, V |
| Row count compared with the list (S) or with the stored table of the last good run, as a notice (D) | a short file | small | S, D |
| Without a list: the file ends with a line end and every row has the header's number of fields | a file cut in the middle of a line (a, a2) | refuses file (e) (correct, no line end at the end) and file (g) (a normal spreadsheet export): see section 1. Does not catch (b) or (c). | A (applies to any file); D proposes only a line-end check and a notice |
| Without a list: the page says "completeness of this data was not verified" | nothing is caught; the visitor is told | none | A, S, D |

Which of the no-list checks is sound is not settled: the cut-file report shows that the field-count check refuses a normal spreadsheet export. It is choice 1a in section 7.

**What happens to the open page** (A, V: a banner that stays, not a fading notice; D: the poll, which recovers in 5 s as in RUN 6r): "New data was delivered on 2026-11-28 06:00 UTC. This page still shows the data of 2026-11-21. Reload the page to see it." No automatic reload; the export stays refused until the reload, as today (the notice of RUN 5 says so; the export refusal itself was not clicked).

**Stored tables of the old data.** Replaced under the same names, one version (RUN 5c: 4 of 24 files rewritten; READ `libs/transformer/src/transformer/anchor.py:175`). A, S, D, V agree that reproducibility does not rest on the stored tables (they are a cache) but on the delivered files and on the export. Option: a store keyed by content, so that two deliveries do not overwrite each other and a return to last week is instant (A, low rank, new engine work). OPEN.

**Several refreshed folders** (a case you did not name): each data place has its own list and its own check (A). Not run.

### 5.4 What the visitor is told about the data

| Where | Content | Proposed by |
|---|---|---|
| A banner or a fixed line, always visible | "Data delivered 2026-11-21 06:00 UTC, id a1b2c3d4e5f6". S and D: also a state "this is the current delivery" or "a newer delivery exists, reload". V: also the number of samples in the line ("42 samples in 'QC_Reads', short code 7f3a9c12, from the file 'FastP.tsv'"): it would have shown case 7a at a glance. | A, S, V (banner); D (a short "data of 2026-11-14" in the banner) |
| The Info panel, a section "Data" | per table: file name (never the server path), rows, short hash; the delivery date; whether completeness was checked against the list | A, D, V |
| The export and the report | the date; the full batch hash (it exists: READ `export_handlers.py:215, 403, 439`); per file: table, file name as read, size, hash, rows, and the source address (never a token); the list's own hash; the line "tables were read from: <place>". S adds the app version, the recipe hash and the name of the deployment. | A, S, D, V |

Source of the date: the list's `delivered` field. Not the file time. With no list, no date is shown and the page says "date not given" (S) or "completeness not verified" (A). Short hash length: the session key uses 12 characters (RUN: `55d26ecb838d:a1ae45bde9f0`), the session list 8 (READ `app/handlers/session_handlers.py:204`); D proposes 8, A proposes unifying, S proposes 12. OPEN, small.

One limit to say on the page (S): "the data is not kept by this page". A figure can be rebuilt only if the producer archives the delivery. The hashes prove the files are the listed ones, not that the pipeline produced right science (A).

### 5.5 Fetching

| Option | What it is | Pro | Con | Proposed by | Reconsiders? |
|---|---|---|---|---|---|
| F1 outside the app | A command (A: of the connector library, the same code for cron, a pipeline, a container start) or a script run by the deployment writes into a delivery folder, writes the list last, flips the pointer | The app stays read-only on data and holds no token. Works for static, Galaxy, IRIDA and bound folders. A failed fetch leaves the previous delivery. | One more step for the deployer. Whether a scheduled job on Posit Connect can write a kept folder is not verified (A). | A (recommended), S, D, V | The start-time `fetch_data()` call of the connector (A, information); ADR-071 is kept |
| F2 the app at start through the connector | The existing hook (READ `bootloader.py:126-134`) | no extra step | A slow or failing network blocks the start; several processes fetch into one folder; the token is inside the app. The connector fetch is a stub for IRIDA and a no-op for others (READ FACTS D). | nobody | |
| F3 the app on a schedule | a thread in the web process | none that F1 lacks | races between copies; a half state visible while the app runs | nobody (S: "the riskiest for science") | |

Where fetched files land and how the app knows they are complete: the delivery folder and the list, as in 5.3. What is recorded for reproducibility: the address, the date and the hash found, written into the list and so into the export. Secrets: only the name of an environment variable (`token_env`, a proposal), never a value, as `SPARMVET_IRIDA_TOKEN` already works (READ `libs/connector/src/connector/irida.py:85`). Galaxy: files are already local in the job folder; the list is written by the last step of the tool wrapper, or the deployer declares no list (A). IRIDA: the future fetch is the F1 command, not the start hook.

The deployment names several files and where each comes from as a table: the recipe's table name, the address or the path, the expected hash or "any". "any" records the hash found and refuses nothing; a value refuses a different file. S: "any" must show on the page as "data not verified". Form: section 6, block 3.

### 5.6 Which file for which table

Today (READ `orchestrator.py:172-195`; RUN in the default-data study): a recipe imported from a bundle reads only its bundle's data; otherwise a table with a declared path reads that file, and if it is missing nothing else is read; a table with no declared path reads `<table name>.tsv` (or `.parquet`) in the data folder; a deployment with `data_lookup: by_dataset_id` ignores the declared paths. The screen says none of this. A wrong tip: the refusal text for the pipeline-style lookup tells the user to check the recipe's `source.path`, which that deployment ignores.

| Option | The rule | What the visitor sees | What the deployer writes | Proposed by | Reconsiders? |
|---|---|---|---|---|---|
| R1 each data place declares how its files are found: `find: table_name` (pipelines, static pages) or `find: recipe_path` (the recipe's path must fall inside this place; the local development deployment uses it for `assets/test_data/`). If two declared places could supply the same table, the opening is refused, naming both. Optional per-table override. | one rule, no order | In the Info panel and the export, per table: place, file name, hash, rows | One line per data place | A | `data_lookup` is replaced by `find` (A). The refusal for two places is D-0424's rule applied to data, which you have not asked for (D-0424 says so). |
| R2 the deployment lists, per table, the file that feeds it; a table not listed is not read; the recipe's own path is used only when the deployment says so | explicit | as R1, plus the rule that selected the file ("named in the deployment") | a list of tables with files | D | D-0425 detail only (D) |
| R3 the deployment lists the tables that need another file; a table not listed reads the file with the table's name in the data folder | as R2 | as R2 | only the exceptions | S, V | none |

All four: the screen and the export say which file each table was read from; never a silent order of two lookups. D flags it as medium risk: it changes which file feeds a figure, so old tests must be adapted first. V names a danger met in the scratch run: the recipe's own path pointed into the repository, so sample data could be drawn instead of the deployer's, with no message.

### 5.7 Two copies and many visitors

| Point | What the specification states | Evidence | Proposed by |
|---|---|---|---|
| Stored tables may be shared by copies of the app | every write is a temporary file, a flush, then a rename in the same folder; every read checks the key stored in the file | RUN 9: two copies on one folder, 24 identical tables, no leftover temporary files; READ `anchor.py:145-175` | A, S, D |
| Two copies on two different deliveries overwrite each other's tables; every opening rebuilds (slow, never wrong) | stated | REASONED, not run | A |
| The start clean-up deletes temporary files older than 600 s; a slow write of the other copy is at risk. A copy of another app version on the same place deletes the other's tables of another cache version. | stated, or raised, or a private temporary name per copy | READ `bootloader.py:204-216`, `anchor.py:27`; REASONED | A, D, S |
| A visitor has no place of his own on a static page; per-visitor state lives in memory only; no session record | stated | RUN 4 (the shared record) | A, S, D, V |
| Not atomic, so not allowed in the app's place: the session record, the audit ghosts | they live in the user place | READ `session_manager.py:392, 539` | A, D |
| Two copies reading two deliveries during a switch (producer does not switch in one rename): each copy shows its own date and hash, so a visitor can see it | stated | | S |

New work: the one function (5.1); the start test; the session manager built only when a user place exists; sessions, Data Import, BLUEPRINT drafts and bundle imports refused by the checker when there is no user place (A).

### 5.8 The temporary place

| Option | Sound? | Proposed by |
|---|---|---|
| T1 only the system variable `TMPDIR` (today) | Two sources of truth, invisible in the file, not recorded; a deployer who is not a developer does not know it (V: "I do not know the variable `TMPDIR`") | nobody |
| T2 a named place in the deployment file that the app applies itself: at start it sets the temporary folder for itself and for the Quarto child process (RUN 10: Quarto follows the variable) | one place to read, check at start and show | A, S, D, V |
| T2a the same, and an environment variable may still override; the app reports which was used | S | S |
| T2b the same, the file always wins; the console says when the environment differs | A | A |

When it cannot be written: with a test at start this should not happen except a full disk later. Then the export must fail with the true cause: a permission or space error names the temporary place; it says the report is not made (A, S, D). Today it says "install Quarto" and the bundle is smaller (RUN 10). S: that is a changed result (the report is missing) with a wrong cause. Not verified: that setting the variable inside the app reaches Quarto's child process (A: REASONED; RUN 10 only set the variable before start). The Polars spill folder was not checked.

### 5.9 What stops and what warns: the sentences

All sentences are proposals. The visitor never reads a server path (RUN 2b shows paths today). A configuration error stops the process; a state of the data that can heal keeps the page up (A, V, D) or keeps the last good data (S, D, V).

| Situation | The visitor reads | The operator reads | Proposed by |
|---|---|---|---|
| Data absent at start, a static page | "There is no data to show yet. The data for this analysis has not been delivered. Try again later, or contact: <contact>." (V: "This page has no data yet. Its operator has been told. Please come back later.") S's wording ("... No result is shown") is the same idea. | A: "[WARN] Place 'weekly' (<folder>): no list of delivered files. The page shows 'no data yet' and checks again every 2 s. Run the delivery step after the data files are in place." D: "The data file FastP.tsv for table FastP was not found at <folder>. Put it there and restart." | A, S, D, V |
| Data absent at start, a pipeline run | none (the process ends) | "[FATAL] Table 'FastP' has no file in place 'job' (<folder>). Expected FastP.tsv or FastP.parquet. The run stops." | A |
| A refresh with other columns | A: "The data delivered on 2026-11-28 does not have the columns this analysis expects, so it cannot be shown." (neutral, not "correct the recipe") S, V, D: the same plus "The page still shows the data of 2026-11-21" and the column names found. | "Table 'FastP': column 'total_reads' declared by the recipe is not in the delivered file; the file has: total_reads_RENAMED ... Either the data or the recipe is out of date. The recipe was not changed." | A, S, D, V |
| A partial file | "The data is being updated or was not delivered completely, so it is not shown. This page checks again by itself." / "The latest delivery is incomplete. The page shows the delivery of <date>." / "expected 42 samples, found 21" | "FastP.tsv does not match the list of delivered files: expected 8346 bytes, found 4179; hash differs." With no list: "FastP.tsv ends in the middle of line 22: 7 of 14 fields." | A, S, D, V |
| The app's place cannot be written | N1: "This page cannot start. Its operator has been told." N2: the page works with the line "nothing is kept". | "[FATAL] The work place (<folder>) cannot be written: Permission denied. In a container bind a folder with write rights, or write `work: temp`. The app does not start." (V adds the cost sentence: "every visit then takes 22 to 31 s".) | A, V, S |
| An open page, the data changed | "The data of this page was updated on 2026-11-20. Reload (F5) to see it." It stays until the reload. | | V, A |

A page that exists only to say "this page cannot start" needs a second start mode in the app (A does not recommend it for the unwritable place; D says it is the largest item: medium to large).

D-0427 and the process exit: D-0427 says "the opening should stop with a plain reason". Today the whole process exits and the visitor gets "connection refused" (RUN 8). Whether that is what you meant is not stated in the line. It is choice 5 in section 7.

### 5.10 The data hash decided "once per session" (D-0025) against the code

- Your decision: "data hash = full content once per session" (D-0025; READ `cache_keys.py:350-351` repeats it).
- The code: the effect that writes the session record reads all data files each time it runs (READ `home_theater.py:1528-1529` and `orchestrator.py:809-820`). The scout lists this as a correction to earlier surveys; the scientist (S10) says it must be settled before the page shows a hash.
- Options (information): (i) keep "once per session" and make the code follow it (the hash is fixed at the first opening; a change of the data is told by the poll of the list and a reload); (ii) change the decision to "at each opening" because the data refreshes during a session; (iii) a hash of the list of delivered files for the page, and the full content hash only at an opening.
- A: the poll must not rehash the data. D: reading all bytes every 2 s is heavy on large data (not measured).
- Reconsiders: D-0025 in (ii) (information).

## 6. The configuration text

Every key name and value below is a PROPOSAL. Nothing exists in the app. The form follows D-0418 (named places with an access word). The deployment file keeps the keys it has today where it can (`deployment_type`, `default_data_analysis_recipe`); `${...}` is expanded today (READ `libs/utils/src/utils/path_expansion.py:21`, `expandvars`). No `users:` key (D-0429).

### Block 1. Case (a): a static page, one recipe, weekly data

The shape most viewpoints share: no user place, no save control; one data place with the list required; the app's own place.

```yaml
# PROPOSAL, every key
deployment_type: filesystem
default_data_analysis_recipe: weekly_amr_2026-11-20
places:
  recipes: [{id: shipped, path: /srv/sparmvet/recipes, access: read}]
  data:    [{id: weekly,  path: /srv/sparmvet/data/current, access: read,
             find: table_name,          # file = <table>.tsv or <table>.parquet
             delivery: required}]       # required | none ; no default (A)
  work:    {path: /srv/sparmvet/work}   # the app's own place (A, V). No `user` key. No `gallery` key.
```

Variant (S and D): two places, and what to do when a delivery fails.

```yaml
# PROPOSAL, variant of block 1
places:
  recipes: {path: /srv/app/recipes,      access: read}
  data:    {path: /srv/delivery/current, access: read, verify: list}
  work:    {path: /srv/app/work,         access: read-write}        # stored tables only (S)
  scratch: {path: /srv/app/scratch,      access: read-write, scope: run}   # emptied at the end of the run (S)
delivery:
  list: delivered.yaml
  on_failure: keep_last_good           # or: stop   (OPEN: yours, choice 4 of section 7)
```

What the operator prepares on disk: the three folders (or four); the recipe in the recipes folder; a weekly job that writes each data file under a temporary name, renames it, then writes `delivered.yaml` last (and, if a version folder is used, flips `current` in one rename). A (and V) add: the app's own folder must exist and be writable by the user that runs the app.

What the app checks at start (A, S): the recipes folder exists; the recipe passes its structure check; the data folder exists and the list matches (size, hash, the tables the recipe needs); the app's own place exists and the app can write and delete a test file there; no feature that needs a user place is switched on (session management, audit, Data Import, BLUEPRINT drafts, bundle imports). With `delivery: required` and no list yet, the page starts and says "no data yet" and checks again every 2 s (A). With a failing check of the app's own place the process stops (N1).

What the visitor sees: the page with the banner "Data delivered <date>, id <short hash>" and the Info section "Data"; no save, no session panel, no audit (absent); an open page after a refresh shows "New data was delivered ... Reload".

### Block 2. Case (b): a pipeline run (usegalaxy, IRIDA, any workflow)

```yaml
# PROPOSAL, every key
deployment_type: filesystem
default_data_analysis_recipe: fixed_recipe
places:
  recipes: [{id: fixed, path: /opt/sparmvet/recipes, access: read}]
  data:    [{id: job, path: "${PIPELINE_JOB_DIR}/inputs", access: read,
             find: table_name, delivery: none}]      # the run's success is the proof of completeness (A)
  work:    temp                                      # a private temporary folder of this run, removed at exit (A)
```

Variant (D, S, V): the pipeline names the places.

```yaml
# PROPOSAL, variant of block 2 (V: "only if I am told the variable names of my pipeline")
places:
  recipes: {path: "${JOB_DIR}/recipe", access: read}
  data:    {path: "${JOB_DIR}/inputs", access: read, verify: list}   # S: the list is recorded in the export
  scratch: {path: "${JOB_DIR}/tmp",    access: read-write, scope: run}
  work:    {path: "${JOB_DIR}/tmp/work", access: read-write}
```

What the operator prepares: the job folder with files named after the tables. The variable names (`PIPELINE_JOB_DIR`, `JOB_DIR`) are made up; Galaxy's real names in the code are `_GALAXY_JOB_HOME_DIR` and `GALAXY_SLOTS_DIR`, read only as a project root (READ `libs/connector/src/connector/galaxy.py:35-46`), and no Galaxy tool wrapper exists in the repository.

What the app checks at start (A): each table the recipe needs has a file; `delivery: none` is printed and the Info panel says completeness is not verified; the temporary folder is writable, else the N1 text. A missing file stops the process with the operator sentence of 5.9 (fatal).

What the visitor (the person who started the run) sees: the page, with "data not verified: no list of delivered files" in the Info panel; the export goes to the job's output and records the files read.

### Block 3. Case (c): a static deployment with several data files and where each is fetched

The fetching is done outside the app (all four). The deployment states the table of files; the delivery command and the app both read it.

```yaml
# PROPOSAL, every key. Shape A: files belong to the data place.
places:
  data:
    - id: weekly
      path: /srv/sparmvet/data/current        # a pointer that the fetch step flips
      access: read
      find: table_name
      delivery: required
      fetch:                                   # read by the fetch step only, never by the app (A)
        - {table: FastP, from: "https://example.org/export/fastp.tsv", sha256: any, token_env: EXPORT_TOKEN}
        - {table: Quast, from: "/srv/pipeline/out/quast.tsv",           sha256: any}
        - {table: MLST,  from: "https://example.org/export/mlst.tsv",   sha256: "9f2c...e1"}  # a fixed file
```

```yaml
# PROPOSAL. Shape S/V/D: one list of tables at the top.
data_files:
  - {table: FastP, source: "https://host/path/FastP.tsv", sha256: any}
  - {table: Quast, source: "https://host/path/Quast.tsv", sha256: "ab12..."}
fetch: {by: operator}                          # the step is outside the app; the app only reads the delivery (S)
token: {env: SPARMVET_FETCH_TOKEN}             # the name of the variable only, never its value
```

`sha256: any` records the hash found and refuses nothing; a value refuses a different file; with "any" the page shows "data not verified" (S). The address and the hash found go into the list and so into the export. For the app's own place use block 1.

What the operator prepares: the data place and the app's own place; a fetch step (cron, pipeline step, container entry) that downloads each file to a temporary name, checks the hash when one is given, renames, writes the list last, flips the pointer. A fetch container binds the data folder with write rights and the app container binds it read-only (A).

What is checked: by the fetch step (A): the addresses answer, the token variable is set, the hashes agree. By the app (A, S): as block 1. No token is ever in the file.

What the visitor sees: as block 1; the Info section "Data" lists each table with the file name and the hash (and the source address, without its query string, in the export).

### Block 4. The form of the list of delivered files (PROPOSAL: name `delivered.yaml`, every key)

```yaml
# PROPOSAL. Written LAST by the refresh, under a temporary name, then renamed.
delivered: 2026-11-21T06:00:00Z        # written by the delivery step; never taken from file times
files:
  - name: FastP.tsv
    bytes: 8346
    sha256: 3a9f...c2                  # hash of the whole file
    rows: 42                           # optional (S: yes; A: optional); shown on the page
    source: "https://example.org/export/fastp.tsv"   # optional; no token, no query string in the export
  - name: Quast.tsv
    bytes: 5120
    sha256: 8b1e...07
```

Open (section 7): is `rows` required; is `delivered` required; may a deployment declare the list `none`. The app computes the list's own hash itself (it is not written in the file).

## 7. The choices for you, ranked

First what protects the result; then the place and "nothing writable"; then the rest. "Reconsiders?" is information only.

| # | The question | The options | What each viewpoint says | Reconsiders? |
|---|---|---|---|---|
| 1a | What does the app do with a row that has fewer fields than the header, in a file with no list? | (1) refuse everywhere, with the row number; (2) refuse only when a declared field is missing, notice otherwise; (3) notice only; (4) nothing, as today | The cut-file report's suggestion: refuse for a missing declared field, a notice for left-out undeclared fields, and also make "more fields" really checked. A: field count and line-end check on any file. D: line-end check and a notice. S: check against the list. V: never a plot from half the samples without telling the visitor. | None decides it. The cut-file report shows the field count refuses a normal spreadsheet export. |
| 1b | What does the app do with an incomplete or mixed delivery when the list exists? | refuse the opening and say why (A); keep the last complete data with its date and say why (S, D, V) | See section 4. Keeping the last data is safe only with its date on screen (S). Not verified: whether the app can show last week's table once the new file is on disk; the stored tables are keyed by content, so it would need the old table kept (REASONED). | none |
| 2 | Is the list of delivered files required for a refreshed place? | required, the deployer may write `none` as an explicit word with its consequence (A); required, else the page says "not verified" (S); preferred, with a notice when missing (D); promised by the refresh (V) | Only the list catches a cut at a line end and a mixed delivery (A, S, D, V and the cut-file report). | none |
| 3 | What must the page and the export say about the data? | the minimum: the date of the delivery, a short hash, the rows or samples, the file names; where: banner, Info panel, export | Section 5.4. All four agree on the content; S wants it in the banner; A wants both. | none |
| 4 | When the new delivery fails: show the last good one or stop? | `keep_last_good` or `stop` | S: hers to choose, safe only with the date. D, V: the last good stays, with a message. A: refuse the new one and check again. | none |
| 5 | Data absent at start where nobody can select data (D-0427): the whole process exits, or the page starts and says why? And for a pipeline run? | exit (today); a plain page for a static page and exit for a pipeline run (A); a plain page always (S, D, V) | D: building the page is the largest item (medium to large). | D-0427's wording "the opening should stop" is information: both readings stop the opening of the recipe. |
| 6 | Does a static page write a session record, and is the session manager built at all? | no (A, S, D, V) | D-0429 point (4) and D-0302 point the same way; the code change remains. | none |
| 7 | One place for the app, or two? | P1 one (A, V); P2 two (S, D) | Section 5.1. | none |
| 8 | Nothing writable: what is the default and what can the deployer choose? | N1 default; N2 or N3 only by an explicit word with its cost beside it (A, D, V); N1 or N2 shown on screen for a static page (S) | Section 5.2. Run fact: a first opening takes 22 to 31 s under load. | none |
| 9 | When a place key is absent: refuse, or default to today's behaviour? | refuse with a message (A); default to the user folder and the system temporary folder so a local install does not change (D) | | `cache` key replaced (A) |
| 10 | Who creates the app's own place? | the operator (A); the app when the parent can be written (V) | A's reason: a missing bind in a container otherwise writes into the container's layer and is lost at restart. | none |
| 11 | Fetch outside the app? | yes (A, S, D, V); the app at start (no one) | Section 5.5. | start-time `fetch_data()` (information) |
| 12 | Which file feeds which table: the one rule | R1 `find` per place (A); R2 the deployment lists each table (D); R3 exceptions listed, else by name (S, V) | Section 5.6. | `data_lookup` (R1); D-0425 detail (R2) |
| 13 | Two places that could supply the same table of data | refuse, naming both (A) | D-0424 says data tables were not asked to you. | D-0424 (information) |
| 14 | Is the app's own place private to the running copy, or may people share it? | private; or declared shared with the consequence stated | A: derived tables of private data sit in it; the app has no check. D-0431 makes sharing the user's responsibility for what a user shares; here the app writes the derived copies itself. | D-0431 (information) |
| 15 | The temporary place | named in the file and applied by the app (A, S, D, V); the environment variable as override (S) or the file always wins (A) | Section 5.8. | D-0340 "no new variable for now" is about the audit folder (information) |
| 16 | Version folder per delivery, or replacement in place? Stored tables: one version, or kept by content? | S: version folder first; A: a list plus a pointer is one way, a store keyed by content is low rank; D: keep the last stored table so a return is quick | The deployer keeps disk for history (S, V: "I must keep last week's data to reproduce"). | none |
| 17 | The data hash: once per session (D-0025) or at each opening? | section 5.10 | | D-0025 |
| 18 | The length of the short hash on screen: 8 or 12 characters | 8 (D); unify (A); 12 (S) | | none |
| 19 | The Gallery folder must exist even when the Gallery is off | drop the requirement for a deployment with the Gallery off (A) | READ by A in `libs/connector/src/connector/filesystem.py` (`_REQUIRED_TO_EXIST`); I did not read it. | none |

## 8. The order of work the developer and the architect propose

Not started. Each step leaves a working app (D). Effort and risk are facts for ordering, not arguments against an option.

| Step | What | Waits for your answer? | Who |
|---|---|---|---|
| 0 | RUN what was not run (section 10): a read-only `anchors` folder with a writable user folder; a data file that disappears after start; two copies with different data; the container; the export refusal after a file change; a cut exactly at a line end; the gallery with a read-only folder | No | D (Haiku or Sonnet, in parallel, each in its own scratch folder) |
| 1 | One function for the app's place (about 19 to 23 call sites) with today's defaults, tests adapted first; no behaviour change | No (it changes nothing; the later name of the place waits) | A, D |
| 1b | Make the misleading texts true (section 9): the export notice, the start-time message that names things that do not exist, the documents about the `cache` key | No (they need no design decision) | by the findings of this study |
| 2 | Build the session manager only when a user place exists; no session record on a static page | Mostly decided (D-0429 point 4, D-0302); the sentence for a missing user place waits | D |
| 3 | The structural check of data files and the reading of the list of delivered files, with tests: cut at a line end, in the middle of a line, in a character, with and without the list; break the code once and see a test fail | Yes: choices 1a, 1b, 2 | D (Opus or Sonnet high; the riskiest logic) |
| 4 | Date, hash and rows on screen and in the export | Yes: choice 3; and 17 first | D |
| 5 | Named places in the deployment file; the temporary place; N1 and, if chosen, N2 or N3 | Yes: choices 7, 8, 9, 10, 15; and the written deployment specification | A, D |
| 6 | The page for "no data yet" and "cannot start" | Yes: choice 5 | D (medium to large) |
| 7 | Fetching outside the app: documentation and one example script first; a connector command only if you want it | Yes: choice 11 | D |

Parallel (D): steps 0 and 1; step 3 beside step 2 (different files: `cache_keys.py` and `orchestrator.py` against `server.py` and `home_theater.py`). Order of the file for which table (5.6) goes after step 1 and after its tests are adapted, because it changes which file feeds a figure (D: medium risk).

## 9. Found on the way: defects and stale texts that need no design decision

READ unless marked. I read these lines myself in this run unless a source is named.

| # | What | Where | Evidence |
|---|---|---|---|
| 1 | The export notice says "install Quarto (quarto.org) if it is missing" although the cause can be the temporary folder | `app/handlers/export_handlers.py:2070-2076` | RUN 10 |
| 2 | The refusal text for a changed data file says "Correct original_name, or remove the declaration" and "Fix the recipe or its data"; it does not name the data file as a possible cause or the headers it now has | `libs/ingestion/src/ingestion/ingestor.py:50-51`; `app/modules/data_analysis_recipe_validator.py:619` | RUN 6 |
| 3 | The refusal tip for the pipeline-style lookup tells the user to check the recipe's `source.path`, which that lookup ignores | source: `tmpAI/coordinator/default_data/FACTS_FOR_THE_OWNER.md` finding 4 | RUN there |
| 4 | A blank grey page when the user folder cannot be written, because `SessionManager(bootloader.get_location("user_data"))` is built at each browser connection and raises | `app/src/server.py:149`; `app/modules/session_manager.py:274` (FACTS) | RUN 2a, 3 |
| 5 | Two red notices name server paths and a Python error text to the visitor | RUN 2b | `shots/c2b_readonly_stored.png` |
| 6 | The message at a failed fetch at start names `BioBlendConnector`, `GALAXY_URL` and `GALAXY_API_KEY`, which do not exist in the code | `app/src/bootloader.py:143-144` | FACTS (earlier), read again here |
| 7 | The documents say the engine writes the `cache` place and that it is safe to delete; no code reads or writes it | `docs/workflows/connector.qmd:75, 131, 137`; `config/deployment/templates/deployment_template.yaml:65-67` | READ; the grep of FACTS B10 and of the deployment-standard study (part F) found only tests |
| 8 | The docstring says "The data files are large and are hashed once per session instead" while the code reads them at each effect run | `app/modules/cache_keys.py:350-351` against `app/handlers/home_theater.py:1528-1529` | FACTS correction 3; see 5.10 |
| 9 | The start-time check does not catch what the visitor meets when a file is replaced while the page is open (the poll watches refused recipes only) | `app/src/bootloader.py:546-548` (FACTS E) | RUN 5 |
| 10 | The sentence of the contract "a row with more fields than the header is refused" is true only when the extra field falls in a column that is read | `.claude/rules/ui_implementation_contract.md` section 9 point 2 | cut-file report, RUN |
| 11 | The deployment-standard table says the stored tables are "the same folder as the sessions"; they are siblings: `anchors` and `_sessions` under `user_data` | `tmpAI/panel/deployment_standard/TABLE_FOR_THE_OWNER.md` part F; `bootloader.py:204`; `session_manager.py:270-273` | FACTS correction 4 |
| 12 | An earlier survey says a vanished data file gets `MISSING:<table>`: it is left out of the batch hash instead; `MISSING:` appears only for a file that vanishes between two calls | `app/modules/orchestrator.py:815-819`, `cache_keys.py:146` | FACTS correction 1 |
| 13 | The IRIDA fetch is written in the present tense in `docs/workflows/connector.qmd:146-154, 204` while `docs/deployment/deployment_guide.qmd:139-141` says "Not implemented yet" and the code is a stub | | FACTS G (EARLIER, not re-read) |
| 14 | The start-time clean-up of stored tables is not inside a try block; a delete error would stop the start | `app/src/bootloader.py:203-216` | REASONED (FACTS B2), not run |

## 10. Not run and not verified

Not run (stated in the run facts and by the viewpoints):
- A read-only `anchors` folder with a writable user folder (case 2b had both read-only).
- A data file that disappears after start (case 8 is the start only).
- Two copies of the app on two different deliveries (case 9 used the same data); a mixed delivery of several files (S2 in section 1 is REASONED).
- A file cut exactly at the end of a line in the browser (the cut-file report ran it on the reader, Data Import and the load gate, not in the app page).
- The container build and run (the image does not build today per an earlier survey), the Galaxy job variables, the IRIDA fetch (a stub), the gallery with a read-only gallery folder, fonts on a second machine.
- The export refusal after a file change ("the export is refused until the page is reloaded", from the notice text): not clicked.
- Setting the temporary folder from inside the app so that Quarto's child process follows it (A: REASONED).
- Whether the start-time clean-up fails the start on a delete error.

Not verified:
- Posit Connect: whether a scheduled job can write a kept folder, how many Shiny processes a content has, whether a static page there can show a status line that changes (A, S).
- The cost of reading all bytes of large data files every 2 s (D) and at each opening (S); the first-opening time on a quiet machine.
- Whether the app can show last week's picture once the new file is on disk (choice 1b): no stored table of the old data is kept under that name today.
- What the real producers (Galaxy, IRIDA, Connect) can promise about writing a list last.
- A, D and S gave different counts for the stored-table call sites (19 or 23); I did not recount.
- Item 19 of section 7 (the Gallery folder that must exist) is A's reading and I did not read `filesystem.py`.
- The ledger line of A's note "not yet in the ledger" for D-0429 is now recorded (D-0429 to D-0431); A read the brief's text instead.

Disagreements between the inputs, and how I wrote them:
- The developer's summary says "a data file cut at a line end ... 21 of 42 samples" (RUN 7a). The run (RUN_FACTS case 7a, 4179 of 8346 bytes) cut the file in the middle of a line, and the cut-file report ran both: mid-line gives 21 rows, a cut exactly at the end of a line gives 20 rows. Both are accepted with no message. I wrote it as mid-line for 7a and as a separate row for a cut at a line end.
- The architect writes a cut at a line boundary leaves 19 rows; the cut-file report on the demo file gives 20. Not important and not re-run; I used the report's number.
- The architect's "always" check (line end and field count) was not set against the cut-file report's cases (e) and (g), which a plain check would refuse. I show both and mark it not settled.
- The deployment-standard table says the stored tables are in "the same folder as the sessions"; the code puts them side by side (item 11 of section 9).
