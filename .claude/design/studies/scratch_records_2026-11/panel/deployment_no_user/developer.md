# Deployments with no user: the Developer viewpoint (2026-11-21)

Study only. Nothing built, nothing changed. Labels: RUN (RUN_FACTS.md or my run), READ (file:line), REASONED. I ran nothing myself (load 2.7 at start); I read code and the two fact files. Every key name below is a PROPOSAL. Effort and risk are facts for ordering, not arguments for or against an option.

## 0. Summary (6 lines, silent first)

1. SILENT: a data file cut at a line end is accepted and 21 of 42 samples are drawn with no message (RUN 7a). The app cannot see this alone: a cut file is a valid file. Only a list of the delivered files with their hashes (or size and row count) can show it. A final-newline check catches only a cut inside a line.
2. SILENT: a page already open keeps the old data while a new visitor sees the new data (RUN 5); nothing on screen names the data or its date (RUN 5d). Two visitors can look at two versions at once and nobody is told.
3. SILENT: the data lookup of a pipeline deployment ignores the recipe paths and says nothing on screen (default_data facts).
4. A static page writes 24 stored tables and a session record with no click (RUN 1), and with no writable user folder it shows a blank grey page (RUN 2a, 3): the cause is one line, `SessionManager(...)` built per browser connection (`app/src/server.py:149`).
5. Order: first RUN the unrun facts, then one function for the app's place (about 23 call sites, no behaviour change), then the checks that stop a silent result, then the screen.
6. Recommended shape: two places (a kept place for rebuildable tables, a temporary place for one run), a static page with no user place and no session record, and data given by a list of delivered files with hashes. Eve decides.

## 1. The app's own place

Facts for the build (READ): the stored tables are addressed at ~23 sites by `bootloader.get_location("user_data") / "anchors"` (bootloader.py:204; home_theater.py:335, 503, 536, 1114, 1488; export_handlers.py:1106, 1154, 1257, 1366, 1396, 1430; opening_handlers.py:125; data_import_handlers.py:272; blueprint_handlers.py:701, 738, 849, 876, 2112). 48 test files mention `user_data` or `anchors` (grep). The sessions folder is built at server.py:149 and passed as `session_manager` to home and audit handlers, which already accept `None` (home_theater.py:159, 1567; audit_stack.py:129, 291).

Two places, in my reading (REASONED):

| place (proposal) | access | what it holds | who creates | lost = what |
|---|---|---|---|---|
| `app_store` | read-write | stored tables (rebuildable), one folder, files keyed by content | the deployer creates the folder; the app creates sub-folders | a slow first opening (22 to 31 s, RUN) |
| `app_scratch` | read-write | one export, one report render, one run | the app, removed at the end | nothing |

It is not the user place and not a shared save place. It never holds sessions, audit files, imports, recipes, user choices, or anything a person would want to keep. A static page has no user place at all (decided reading), so it needs no `_sessions` and writes no session record (that is a code change: build `SessionManager` only when a user place exists; today B3/B4 have no flag).

What moves: stored tables to `app_store`; clean-up of orphan temporaries (bootloader.py:204-216) to `app_store`; the system temp folders (export_handlers.py:1238, 2043; test_lab_handlers.py:814, 976; gallery_examples.py:110; opening_build.py:166 probe) to `app_scratch`. The `TemporaryDirectory()` calls take `dir=`. The Quarto render gets the same folder through the environment of the child process the app starts (RUN 10 shows Quarto follows `TMPDIR`), so the app applies it itself and no operator variable is needed.

Configuration (proposal, builds on D-0418 named places):
```yaml
places:                       # PROPOSAL
  app_store:   {path: /srv/app/store,   access: read-write}
  app_scratch: {path: /tmp/sparmvet,    access: read-write, kind: temporary}
```
Default when absent: today's `user_data/anchors` and the system temp (so a local install does not change). Open: whether one place with a sub-folder is enough (simpler; temporary files would then sit with kept ones).

Effort: medium (the function, the keys, 23 sites, ~48 tests adapted). Risk: low if the function lands first with the old defaults.

## 2. Nothing writable (choice 5)

| option | visitor sees | operator sees | cost | static page | pipeline run | local install |
|---|---|---|---|---|---|---|
| N1 stop at start with a plain reason | no page (connection refused today, RUN 8) unless the app serves a plain "this page is not available" page | one clear console reason, exit | none after fix | sound for the operator, poor for the visitor | sound (the pipeline sees the exit) | sound |
| N2 this session only, nothing kept | the page works, a small line "stored tables are not kept" | one line at start | every opening is a first opening: 22 to 31 s (RUN) | works, but each visitor waits; a busy page rebuilds per visitor and the memory and time add up | sound | sound |
| N3 in memory | same as N2 | same | same plus memory for 24 tables; lost at restart | the same load as N2 | sound for a short run | sound |
| N4 (mine): stop at start if no `app_store`, but let a deployment declare `app_store: none` and then work as N3 | as N2 or N1 depending on the declaration | one line | as N3 | the deployer chooses with the cost in front | same | same |

Facts: N2 and N3 are the same code path in my reading: a build that is not stored. The orchestrator already has "not stored" builds (`_unstored_builds`, home_theater.py:536; anchor.py:169-170). It is not tested with all stages and exports, so it is the biggest unknown in the build (effort medium to large, risk medium). N1 is small. Today's read-only-with-tables case (RUN 2b) shows server paths to the visitor: a fix in any case.

## 3. Refreshed data

| way | what it needs | silent failure possible |
|---|---|---|
| A. content hash at each opening (today) | nothing | a half file is a file |
| B. poll (2 s poll exists for refused recipes only, bootloader.py:546-548) | extending the poll to the data of available recipes: reads all bytes every 2 s, heavy for large data | half file, unless C |
| C. a list of the delivered files with their hashes, written by the refresh last, read by the app | the refresh promises it; the app compares each file's hash with the list | none for a listed file; an unlisted file is shown as unchecked |
| D. a folder per refresh, the deployment points at the current one | the refresh changes a pointer atomically | none for a complete folder |

What the app must check regardless of the promise (my minimum, REASONED): (1) the list exists and every file matches its hash, else the opening refuses with the reason and the last good version stays on screen; (2) with no list, a final-newline check and the row count compared with the stored table of the last good run as a notice (not a refusal). The notice says a number of rows fell from 42 to 21. I propose to inform, not to refuse (the user decides).

A page already open: today one yellow notice at a tab change (RUN 5). Proposed: the same effect that exists for refused recipes (RUN 6r recovered in 5 s) extended with the list file check: cheap, because only the small list is read each 2 s. Stored tables of old data: kept by key until a clean-up; the number of versions is open (I would keep the last one so that a rollback is quick; effort small, an open choice).

## 4. What the visitor is told about the data
Show in the Info panel and in the export: the date from the list of delivered files (the file's time is not reliable: copies reset it), the short hash (8 characters, the same as the session list uses, session_handlers.py:204), the number of rows per table. Banner only a short "data of 2026-11-14". Export: `data_batch_hash` exists (export_handlers.py:215, 403, 439): add date and list hash. Effort small to medium, no risk to results.

## 5. Fetching
Options: (i) a step outside the app run by the deployment (cron, pipeline) that writes then renames and then writes the list; (ii) the app fetches at start through the connector (`fetch_data` is a no-op or a stub, IRIDA raises NotImplementedError, irida.py:40-52); (iii) the app on a schedule. Developer reading: (i) has no new code in the app and is testable alone; (ii) means building HTTP, retries, secrets and timeouts in the connector (large; the IRIDA stub shows it was planned as Phase 23-D); (iii) adds a thread to a Shiny process, hard to test. Naming data in the deployment file (proposal):
```yaml
data:                          # PROPOSAL
  - table: FastP
    from: /srv/data/weekly/FastP.tsv
    sha256: any                # or the hash
```
Secrets from the environment only (IRIDA does this: irida.py:85).

## 6. Which file for which table
One rule: the deployment file lists the tables and their files; a table not listed is not read (D-0425 reading). The recipe path is used only when the deployment says so. The screen and export print "table, file, hash" in the Info panel. Effort medium (orchestrator.py:172-193, ingestor.py:198-221, tests for both lookups). Risk medium: it changes which file feeds a figure, so the old tests must be adapted first.

## 7. Two copies and many visitors
Stored tables: atomic (anchor.py:145-175) and content-keyed: two copies give the same tables (RUN 9, 24 equal). New work: `assembly.json` written with a temp name then `os.replace` (session_manager.py:392 is not atomic); on a static page it is not written at all. The 600 s clean-up (anchor.py:27) can delete the other copy's slow write: raise or state it. A per-visitor place does not exist on a static page. Effort small.

## 8. The temporary place
A named place applied by the app is sounder than `TMPDIR`: a deployer who is not a developer does not know the variable, and the file records it. The app sets `tempfile.tempdir` at start and passes the folder to Quarto's child process. If not writable at start: stop with a reason (consistent with N1) or, for export only, tell the cause: today the text says "install Quarto" (RUN 10), a wrong cause; fix is small (check the folder before rendering).

## 9. What stops and what warns (sentences are proposals)
| case | visitor reads | operator reads |
|---|---|---|
| data absent at start (D-0427) | "This page cannot be shown now. The data it needs is not available. Please try later or contact <contact>." The app must serve this page: today the process exits (RUN 8). | "The data file FastP.tsv for table FastP was not found at <folder>. Put it there and restart." |
| refresh with other columns | "The data changed and no longer fits this analysis: column total_reads is missing (the file now has total_reads_RENAMED). The last good data is not shown." | the same with the file name and the recipe line |
| partial file | "The data file FastP.tsv is not complete (the list says 42 rows, 21 are there). The previous data stays." | the hashes |
| app place not writable | none for N2/N3; with N1 the page above | "The folder <path> cannot be written. Fix the rights or declare app_store: none." |

Building a page when the process would exit is the largest item (medium to large: the app must start in a refused state; today `exit_if_errors`, bootloader.py:617-626).

## 10. Templates (all keys proposals)
(a) static, weekly: `places: {app_store, app_scratch}`, `data: [{table, from, sha256: list}]`, `delivered_list: /srv/data/weekly/DELIVERED`. Operator prepares: the folder, the list written last. Checked at start: the places, the list, every hash.
(b) pipeline run: `places: {app_scratch: /job/tmp, app_store: none}`; data from the job folder; checked: scratch writable.
(c) several fetched: as (a) with `fetch: outside` and one `from` per table.

## 11. Table
| point | status | proposal | reconsiders |
|---|---|---|---|
| place of the stored tables | OPEN (D-0418 asks, no answer) | `app_store` | none |
| no session record on a static page | partly DECIDED (D-0302; Eve's reading of 2026-11-21) | gate `SessionManager` on a user place | none |
| nothing writable | OPEN (choice 5) | N4 | none |
| half file | OPEN | list with hashes plus the app's own checks | D-0025 (hash once per session) |
| data on screen | OPEN | date, hash, rows in Info and export | none |
| file for a table | CONFIRM D-0425 | deployment file lists tables | D-0425 detail only |
| fetch | OPEN (D-0428 is an order) | outside the app | none |
| temp place | OPEN | named place applied by the app | D-0340 (no new variable "for now") |

## 12. Order of work (each step leaves a working app) and tests
0. RUN what was not run (Haiku or Sonnet low, parallel, own scratch): read-only `anchors` with writable user folder; data deleted after start; two copies with different data; gallery read-only; the container; the export refusal after a file change; a cut at a line end. Needed before any choice 5 build.
1. One function for the app's place, old defaults, 23 sites, tests adapted first (Sonnet medium). Headless.
2. Gate the session record and the sessions folder on a user place (Sonnet medium). Headless: no `_sessions` created; browser: static page loads with a read-only user folder (fixes RUN 2a).
3. Complete-file check and the list of delivered files (Opus or Sonnet high; riskiest logic; silent-result item). Unit tests with a cut file at a line end, mid-line, mid-character, with and without the list; break the code once and see a test fail. Browser: RUN 7a again.
4. Data on screen and export (Sonnet medium), after 3.
5. Named places in the deployment file (needs the D-0418 specification and her answer on choice 5). Then the scratch place (small) and N2/N3 (medium to large).
6. The page when data is absent at start (medium to large), last, with browser tests.
7. Fetching: outside the app first (documentation and one example script, small); connector fetch only if she wants it.
Parallel: steps 0 and 1; 3 can run beside 2 (own files: cache_keys.py, orchestrator.py; step 2 touches server.py and home_theater.py).

## 13. To decide first
1. Choice 5 (N1, N2/N3, N4).
2. Whether the refresh must deliver a list of files with hashes (the only complete answer to the silent half file).
3. One place or two.
4. Whether the app serves a "not available" page instead of exiting.
5. Whether a notice (not a refusal) is enough when no list is delivered.

## Not verified
Nothing run by me. The `_unstored_builds` path with all stages; whether Shiny runs `server()` once per connection (RUN 2a agrees); the cost of reading all bytes every 2 s on large data; that export works when `SessionManager` is None (export_handlers.py:611 uses it; not read further).
