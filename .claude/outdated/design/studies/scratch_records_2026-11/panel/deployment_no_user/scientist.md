# Scientist and data scientist viewpoint: deployments with no user interaction (2026-11-21)

Labels: RUN (RUN_FACTS.md, my reading of what was run), READ (file:line), REASONED. I ran nothing new. I read `export_handlers.py:215` and `cache_keys.py:139-158`. Every configuration key is a PROPOSAL.

## 0. The test I apply
A reviewer holds a figure from a page whose data is replaced every week. He asks four things. Which data was this? Is it all of it? Can you rebuild it today? Did anything change under me while I looked? The page must answer all four from the page and the export, with the data of last week gone.

## 1. Things that change a result silently or hide a step (FIRST)

| # | What | Evidence | Why it matters |
|---|---|---|---|
| S1 | A file cut in a line is accepted and 21 of 42 samples are drawn. No message. | RUN case 7a | A wrong figure, with the right title. A cut at a clean line end is the same (REASONED). Only a cut inside a UTF-8 character is refused (7b). |
| S2 | A refresh of SEVERAL files is not one event. File A new, file B old gives a mixed batch that passes every check. The batch hash then names a state that never existed in the pipeline. | REASONED from `cache_keys.py:139-158` (each file read on its own, no file set check) | Samples in table A may not exist in table B. The join drops or fills them. |
| S3 | A page open for days shows old data with no sign. A changed file is noticed only at a tab click, then one toast, and the open plot stays old. | RUN case 5 | The visitor cites a figure that is not the data of the directory. |
| S4 | Nothing on screen gives the date, the hash, the number of rows or the file names of the data. | RUN 5d | A figure cannot be cited. A screenshot cannot be tied to a delivery. |
| S5 | The export holds only one hash for the whole batch (`data_batch_hash`, `export_handlers.py:215`). No file names, no per-file hash, no row counts, no source address, no delivery date. | READ | When last week's data is gone, one hash cannot tell which file differs. It proves identity only if you still own the data. |
| S6 | Per-table file lookup: a file found by the table's name in the deployment's folder, with nothing on screen. The recipe's own path is used first if it exists. The same recipe can read different files in two deployments. | FACTS D; `orchestrator.py:172-188` | The reader cannot know which file fed a table. |
| S7 | Stored tables are replaced under the same name, no history. A key match is the only proof. | READ `anchor.py:175` | Fine for a cache (they are rebuildable). They must never be taken for a record of the data. |
| S8 | A renamed column gives a text that blames the recipe ("Correct original_name"). The page stays wrong until the file is fixed. | RUN case 6 | The visitor or operator may edit a correct recipe to fit a broken delivery. That changes the science. |
| S9 | Static page with session record: 24 tables and one record written, with no save control. One record is shared by all visitors. | RUN case 1, 4 | Not a result change. A write that nobody can use is a hidden step. |
| S10 | D-0025 says "data hash = full content once per session". The code reads all data on each effect run. | FACTS correction 3 | On a refreshing page the hash can change inside one session. This must be settled before the page shows a hash. |

## 2. Answers

### Q1. The app's own place
Recommendation: TWO places, with different promises.
- `work` (rebuildable, tied to no user). Holds stored tables and nothing else. Anything in it may be deleted at any time and the result is the same, only slower. Access word: read-write. Created by the deployer, or by the app if the parent is writable.
- `scratch` (one run or one export). The system temp today. Named in the file and applied by the app. Emptied at the end of the run.
Why two: they have different lifetimes. One place mixes "may delete" with "must keep". A reviewer must be able to say "the work place holds no result, only a cache".
What `work` never holds: a session record, an audit file, a recipe, a copy of the data, anything that cannot be rebuilt from recipe plus data. Those are user place (decided: D-0422, D-0423) or do not exist on a static page.
A static page writes NO session record. The record exists to restore a session for a person. There is no person and no save control (D-0302). Writing it is a hidden step and a shared file (S9). This is a removal, not a move.
Stored tables move from `user_data/anchors` to `work`. Keep the key as proof: a table read from `work` must carry its key (READ `opening_build.py:224-229`).

### Q2. Nothing writable
| Option | Visitor sees | Operator sees | Cost | Science |
|---|---|---|---|---|
| N1 stop at start | "connection refused" today (RUN 8 style). A plain page is needed | One clear line at start | None at the opening | Safest: no half state |
| N2 this session only | The page works, a line "nothing is kept" | A line at start naming the temp folder | 22-31 s on first opening after each start (RUN). A page with many visitors: the first pays, the rest read the tables (RUN case 4: 31 s then 3 s). Cost returns after every restart | Sound if tables are keyed by content. The folder must be private to the running copy, and removed at exit |
| N3 memory | Same as N2 | Same | Rebuild per process, no sharing between copies, memory grows | A second code path to test. I would not choose it before a case needs it |
My ranking on science: a static page: N2 with the line "nothing is kept" visible, or N1. A pipeline run: N2 (the run is short, the tables are built once). A local install: N1 (a person can fix the folder). The choice is hers. The software must say which one it is on in the Info panel.
Never silent: today a read-only user folder gives a blank grey page (RUN 2a). That is the worst option and none of N1-N3.

### Q3. Refreshed data
How the app learns: by content at each opening, as today. Add for the open page a check by content, not by tab click (S3). The open page must say "data changed on <date>, reload", visibly and until reloaded. A poll of a file's size and time is NOT enough: a refresh can keep the size. Use the list of delivered files (below), which is cheap to read.
A partial refresh is never shown. Two layers, both required:
1. The refresh process promises: write each file under a temporary name, rename it; write the list of delivered files LAST (name, size, sha256, rows, the delivery date, the source). The list is the "complete" marker. No list, or a list newer than a file, means "not delivered".
2. The app checks itself, whatever was promised: the sha256 and the size of each file against the list; the file set against the recipe's tables; the header; a count of rows against the list. A mismatch stops the opening with a plain reason (S1, S2). Only the list makes S1 and S2 detectable: without a count or a hash given by the producer, a short but valid file cannot be told from a small dataset.
Without a list (a deployer who cannot write one): the app may still run, but the page says "Data not verified: no list of delivered files". That is a choice for the deployer, shown, never silent.
Version folder per refresh (`data/2026-11-16/`, the deployment points at `current`): the cleanest for reproducibility, because last week's data stays. It needs the deployer to keep disk. The switch of `current` is one atomic rename (a symlink swap). I rank it first for a cited figure, then the list, then in-place replacement.
Stored tables of the old data: replace, keep one version. They are a cache. History belongs to the data folder, not to `work`.

### Q4. What the visitor is told (the minimum to cite)
On the page (banner or a fixed line, not only in the Info panel): the date of the data ("delivered 2026-11-16"), the short hash (12 characters), the number of samples and rows of each table, a mark "data not verified" when there is no list. Beside it a state: "this is the current delivery" or "a newer delivery exists, reload".
Source of the date: the field in the list of delivered files, written by the producer. Not the file time (a copy resets it). The hash is the identity. When the list holds no date, show "date not given", never a file time.
Export and report: the date, the full batch hash, and per file: table name, file name as read, source address if fetched, sha256, rows, size. Plus the app version, the recipe hash, the name of the deployment. Also the line "tables were read from: <place>". Add the number of samples that each table kept. With this, a figure can be tied to a delivery even when the data is gone, provided the producer archives it: say so on the page ("the data is not kept by this page").
Not shown: a stored table's file time as if it were a data date.

### Q5. Fetching
| Option | For | Against |
|---|---|---|
| A step outside the app run by the deployment (cron, pipeline, the container's start) | Simple. The app stays read-only and never needs a token. Works for static, Galaxy, IRIDA, a container with bound folders. One way to deliver | The record of the address and the hash is only as good as the script |
| The app at start through the connector | One place states the address | The connector fetch is a stub (IRIDA) or no-op (READ). The app needs a write place and a token. A failed fetch at start means no page |
| The app on a schedule | Fresh without a restart | A partial state while the app runs. Retry and error cases. A writer in the app. This is the riskiest for science |
I recommend the first. The app reads only a delivered, listed directory. The list carries the address and the date, so the fetch is recorded even though the app did not do it. The app does not fetch (decided today: nothing fetches). If she wants the app to fetch, the fetch must write to the delivery folder with the same list and rename rules.
Several files in the deployment file: a table of `table -> address or path -> expected hash or "any"`. "any" must show on the page as "data not verified" (see Q3). Secrets are named by an environment variable only (the token name, never its value), as `SPARMVET_IRIDA_TOKEN` already is.

### Q6. One rule for which file feeds which table
One rule: the deployment file lists, for each table, the file that feeds it. When it is not listed, the file with the table's name in the deployment's data folder. The recipe's own path is an example that applies only in the local deployment (D-0425). Never a silent order of two lookups.
Screen and export: for each table the file name, the folder, the sha256, the rows, and the rule that selected it ("named in the deployment" or "by the table's name"). The Info panel lists them. A reader must see that the file was not the one the recipe names.

### Q7. Two copies and many visitors
State: stored tables may be shared by copies (identical results, RUN case 9: 24 tables, 0 different). That works because the key is the content and the write is atomic. A visitor has no place of his own. A page with no user place writes no session record. Atomic: stored tables (yes today), the list of delivered files (written by the producer), the switch to a new delivery. New work: remove the start clean-up that may delete the other copy's temp files older than 600 s (REASONED); a file lock or a private temp name per copy.
Two copies reading two deliveries during a switch: possible when the producer does not switch in one rename. Each copy shows its own date and hash, so a visitor can compare. That is a reason for Q4.

### Q8. Temporary place
A named place in the deployment file that the app applies itself (sets the temporary folder for itself and its children, Quarto included). `TMPDIR` as the only way depends on a person remembering a process variable; a named place is one place to read, to check at start and to show. The environment variable may be an overriding source, and then the app shows which one it used.
When it cannot be written: today the export is smaller and the text says "install Quarto" (RUN 10). That is a misleading cause and a changed result (the report is missing). The notice must name the temp folder and say the report is not made. Better: check the folder at start and, where export is on, stop or switch off export with a visible reason.

### Q9. What stops and what warns (sentences are proposals)
| Case | Visitor | Operator |
|---|---|---|
| Data absent at start (D-0427) | "This page cannot show data now: the data files it needs are not available. The operator has been informed. No result is shown." (a real page, not "connection refused"; needs a minimal server answer) | "[FATAL] Table 'FastP': no file at <folder>. The list of delivered files names <file>. Fix the delivery and restart. The page is not started." |
| A refresh with other columns | "The new data does not match the analysis: the column 'total_reads' is no longer in 'FastP'. The previous picture is still shown, from the delivery of <date>." | "Table 'FastP': file <name> has columns [..]. The recipe expects total_reads. Cause: the delivery changed. The recipe was not changed." |
| A partial file | "The latest delivery is incomplete. The page shows the delivery of <date>." Or, if there is no earlier one: "no data can be shown" | "<file>: size 4179, list says 8346; sha256 does not match. Not used." |
| The app's place not writable | per Q2: "Nothing is kept" or a plain stop | "Work place <path> is not writable (<reason>)." |
A new principle here: when a new delivery fails, should the page keep showing the last good one, with its date? That helps the visitor and is honest only if the date is on screen. It is also the version-folder idea. This is a choice for her (OPEN): showing the old figure is safe only with the date; stopping is safer but empties a public page.

### Q10. Templates (proposals; every key is a proposal)

(a) A static page, weekly refresh
```yaml
deployment_type: filesystem                 # proposal: existing key
places:                                     # proposal
  recipes:   {path: /srv/app/recipes,  access: read}
  data:      {path: /srv/delivery/current, access: read, verify: list}
  work:      {path: /srv/app/work,       access: read-write}   # stored tables only
  scratch:   {path: /srv/app/scratch,    access: read-write, scope: run}
delivery:                                   # proposal
  list: delivered.yaml                      # name, size, sha256, rows, date, source
  on_failure: keep_last_good                # or: stop   (OPEN: hers)
```
Prepare: the producer writes files, then `delivered.yaml`, then switches `current`. Checked at start: list present, hashes, rows, columns, work writable, scratch writable.

(b) A pipeline run
```yaml
deployment_type: galaxy
places:
  recipes: {path: ${JOB_DIR}/recipe, access: read}
  data:    {path: ${JOB_DIR}/inputs, access: read, verify: list}
  scratch: {path: ${JOB_DIR}/tmp, access: read-write, scope: run}
  work:    {path: ${JOB_DIR}/tmp/work, access: read-write}
```
Nothing outside the job. The export goes to the job's output. The run records the list and the hashes in the export.

(c) A static deployment with several files fetched
```yaml
data_files:                                 # proposal
  - {table: FastP,  source: "https://host/path/FastP.tsv",  sha256: any}
  - {table: Quast,  source: "https://host/path/Quast.tsv",  sha256: "ab12..."}
fetch: {by: operator}                       # the step is outside the app; the app only reads the delivery
token: {env: SPARMVET_FETCH_TOKEN}          # the name only, never the value
```
Checked at start: each file present, size and hash against the table above or the list, "any" shown on the page as "data not verified".

## 3. Table

| point | DECIDED / CONFIRM / OPEN | proposal | reconsiders |
|---|---|---|---|
| One specification, named places with access word | DECIDED D-0417, D-0418 | `work` and `scratch` are two named places | no |
| Stored tables place | OPEN (D-0418) | `work`, tied to no user | no |
| No session record on a static page | CONFIRM D-0302 (no audit on pipeline static); OPEN for the record | remove the write | no |
| Data absent: stop with a reason | DECIDED D-0427 | a plain page, not "connection refused" | no |
| Nothing writable N1/N2/N3 | OPEN (choice 5) | N1 or N2 shown on screen; not N3 first | no |
| App does not fetch | CONFIRM (code today) | fetch outside the app | no |
| List of delivered files (hash, rows, date, source) | OPEN | required to detect S1/S2 | no |
| Date and hash on screen and in export | OPEN | yes, as in Q4 | no |
| Which file per table | DECIDED D-0425 in part | one rule, shown | no |
| Keep last good delivery on failure | OPEN | her choice | no |
| "Data hash once per session" | DECIDED D-0025; code differs | settle before showing the hash | information: D-0025 |
| Temp place as named place | OPEN | named place, env as override | no |

## 4. To decide first (ranked)
1. A partial or mixed delivery must never be drawn (S1, S2): will she require a list of delivered files with hashes and row counts, and does the app refuse without it or only mark "not verified"?
2. What the page and the export say about the data (date, hash, files, rows): minimum list (Q4).
3. On a failed new delivery: keep the last good one with its date, or stop?
4. Nothing writable: N1, N2 or N3, and the visible line.
5. Stored tables move to a `work` place; no session record on a static page.
6. Version folder per delivery (history kept by the deployer) or in-place replacement.
7. D-0025 against the code (hash per session or per effect).

## 5. Not verified
- No new run. A mixed delivery (S2) is REASONED. A cut at a clean line end is REASONED, not run (RUN_FACTS says so).
- A file replaced while it is being read by the hash (race) not run.
- Whether the open page's data check can be done by content cheaply on large data (the hash reads all bytes: `cache_keys.py:146`; the cost on gigabytes is not measured).
- What the producer on each real system (Galaxy, IRIDA, Connect) can promise: not checked.
- Whether a Connect static page can show a mutable status line: not checked.
