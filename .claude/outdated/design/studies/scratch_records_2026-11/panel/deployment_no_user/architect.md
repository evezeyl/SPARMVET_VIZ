# Architect viewpoint: deployments where no user interacts and the app needs its own place (2026-11-21)

Study only. Nothing built, nothing changed in the repository. Every key name below is a PROPOSAL. Labels: RUN (I ran it; scratch in `tmpAI/panel/deployment_no_user/architect_scratch/`), READ (file:line), REASONED. DECIDED / CONFIRM / OPEN / MINE as in the personas file. "Reconsiders" is information only.

The decision line after D-0428 (the owner's words on users, variables and Connect) is not yet in the ledger (last line is D-0428, READ); I took it from the brief.

## 0. Summary (anything that changes a result silently first)

1. SILENT, any deployment: a data file that is cut or has short rows is read and drawn. RUN (mine, polars as the ingestor calls it, `ingestor.py:200`): a TSV cut mid-line gives 21 of 42 rows, the cut line is filled with nulls (7 of 14 fields); no error. A file cut at a line boundary (19 rows, newline kept) cannot be told from a complete file by any check inside the app. Only "a list of the delivered files with their hashes" (written last by the refresh) catches that.
2. SILENT, refresh of several files in place: files are replaced one by one and nothing ties them together, so a page can join table A of this week with table B of last week (REASONED from `cache_keys.py:139-158` and the lack of any cross-file mechanism; RUN covered one file only). The same list catches it (a mixed state does not match the list).
3. SILENT on screen: nothing says which data or which date is shown, and the pipeline-style lookup reads other files than the recipe declares (`orchestrator.py:172-195`; default-data FACTS). An open page keeps the old figure and is told only at a tab change (RUN 5).
4. A static page writes 24 stored tables and a session record nobody can use, and without a writable user folder the visitor gets a blank grey page (RUN 1, 2a). Recommended: one app-owned place `work` (stored tables + scratch), no user place on a static page, session manager absent (the code already handles `None`, READ 8 guards).
5. Nothing writable: recommended N1 (stop at start) when the place is not declared, N2 as an explicit word (`work: temp`); N3 (memory) is not recommended: export needs disk anyway (RUN 10).
6. Fetch outside the app (a command of the connector library, same code path for cron, pipeline and container), landing into a new delivery folder, list written last, then a pointer flip; the app only reads and verifies.

## To decide first (ranked)

1. Is a delivery list (with hashes, bytes, date) required for a refreshed place, or may the deployer declare `none` with a stated consequence? (items 1, 2, 3 of the summary depend on it)
2. One app-owned place `work` (stored tables and scratch inside), or two (`store`, `scratch`)?
3. Data absent or incomplete at start on a static page: the process exits (today; visitor sees "connection refused"), or the page starts and says why, and heals itself when the delivery completes (RUN 6r shows the healing exists)? Per case: a pipeline run should exit.
4. Nothing writable: N1 for absent, N2 only as the explicit word `temp`?
5. Fetch: outside the app (recommended) or at the app start?

## Q1. The app's own place

Name (proposal): `work`. One place, access fixed by its kind (the app reads, writes and deletes there; a deployer cannot declare it read-only, because a read-only work place is a contradiction the checker would otherwise test). Who creates it: the operator (or the container binding). The app creates only the sub-folders inside, and at start probes write + delete. The app does NOT create the place itself: today `user_data` is made on demand (`filesystem.py` comment, `session_manager.py:274`); a missing bind mount then silently writes into the container's own layer and is lost at restart. D-0417 reading (b): "the app checks at start that each declared place exists and can be used as declared" (CONFIRM).

| | `work` (app's) | `user` (a person's, D-0340, D-0422) |
|---|---|---|
| Content | stored tables (`tables/`), scratch (`tmp/<run>/`), the write probe | sessions, audit folders, imports, Data Import copies, exports saved |
| Rebuildable | yes, always (content keys, `anchor.py:109-114`: never reused by file name alone) | no |
| Tied to a person | no | yes: path from variables of the system the app runs in; one copy per person |
| May be shared by copies | yes (atomic writes, key check on every read) | only if the administrator declares it (her words) |
| Exists on a static page | yes | no: no `user` key, no save control (absent) |
| Lost = result changes? | never; only 22 to 31 s slower (RUN) | yes |

Never in `work`: recipes, sessions, audit files, imports, Data Import copies, anything a person chose to keep. Private data: stored tables are derived from data, so a `work` folder shared between people holds derived copies of private files; the deployment states `work` is private to the running copy, or accepts it (see choice 7 of the deployment study; not decided).

One place or two. Variants:
- V1 (recommended, MINE): one `work`, fixed sub-layout written in the specification (`tables/`, `tmp/`). One thing to declare and bind. Sub-folders keep the two invariants apart (tables may be shared; `tmp/<run>` is private, removed at exit).
- V2: two declared places `store` and `scratch`. Pro: store on a persistent volume, scratch on a tmpfs (container). Con: two keys, two probes, two ways to forget a bind. The need appears only if scratch must be elsewhere; it can be added later as an optional key without breaking V1 (one added key, not a second way).
- V3: keep the stored tables in `user`. Does not work: a static page has no `user` place.

What moves to `work` from today (READ, FACTS B): stored tables (B1, `bootloader.py:204`, `opening_handlers.py:125`, 19 non-test `"anchors"` literals in `app/` and `libs/` by RUN grep, 25 in tests); start clean-up (B2); the write probe (B7, `opening_build.py:166`, moved to start); all `tempfile` uses (B8). Moves out / not written: `_sessions` and `assembly.json` on a page with no `user` place (B3, B4); no `gallery` index refresh unless the Gallery is on.

MINE (architecture): before any move, one accessor (as `get_imports_dir`, `bootloader.py:861`) replaces the 19 hand-joined `get_location("user_data") / "anchors"`. A step that changes no behaviour and leaves the app working; today the same fact is written 19 times.

The dead key `cache` (B10, no reader) is replaced by `work`: the old key is refused with a message naming `work` (ADR-091 point 2 style; no alias). Its template text "written by the DataOrchestrator" is false today.

Configuration text (every key a proposal):
```yaml
places:
  work: {path: /srv/sparmvet/work}      # app-owned; must exist and be writable; or the word  work: temp
```
Reconsiders: ADR-048 sections 3 and 5 (five location keys; already reconsidered by D-0418); the `cache` key.

## Q2. Nothing writable (choice 5)

Cost fact (RUN): first opening 22 to 31 s under load 3 to 10 (not a quiet-machine figure); later visits 2 to 4 s. One process shares tables across visitors (RUN 4: visitor A 31.2 s, B 3.1 s).

| Option | Visitor sees | Operator sees | Cost | Many visitors | Sound for |
|---|---|---|---|---|---|
| N1 stop at start, plain reason | nothing from the app (proxy error / connection refused) | one console block naming the place, the errno, how to fix | none | n/a | pipeline run: yes (job fails, exit code). Local install: yes. Static page: yes for a config error, because the operator must fix it |
| N2 `work: temp`: private temp folder of this run, removed at exit | the page, normal | console line "work place is temporary: stored tables are rebuilt at each start" | 22 to 31 s once per process start; each process of a multi-process host pays its own | first visitor pays, others share (one process) | static page without a bound folder: yes. Pipeline run: yes, natural. Local install: legal but a 30 s cost at each start, the deployer's choice |
| N3 memory | normal | normal | new second storage way in the engine, tested twice | same as N2 | not recommended: export needs a disk scratch anyway (RUN 10: `TMPDIR` read-only gives a smaller export), so "nothing on disk" cannot hold when export is on |
| N4 (better option, MINE) N1 for an absent `work`, N2 only as the explicit word `temp`, and the checker refuses features that need what is missing (export on needs a writable scratch; session management needs `user`) | as N1 or N2 | as N1 or N2 | as N1/N2 | | all three cases |

Rule behind N4: the app never falls back silently to the system temp folder; the system temp folder is used only when the deployment says `temp`. Today it does silently (`TMPDIR`, B8). Reconsiders: none (D-0340 asks only "a plain error when the directory cannot be written"; choice 5 is open). `work: temp` with an unwritable system temp: N1 naming `TMPDIR`.

## Q3. Refreshed data

How the app learns (options):
| Option | How | Pro | Con |
|---|---|---|---|
| L1 at each opening by content (today) | hash all data bytes at the effect (`cache_keys.py:139-148`) | exact | the page already open is told only at a tab change (RUN 5); nothing is polled for an available recipe (FACTS E) |
| L2 poll the list file | the existing 2 s poll (`recipe_gate_handlers.py:25`, `bootloader.py:497-532`, READ via FACTS) also reads the small list and compares its content hash | cheap (no rehash of data), the notice arrives with no click, the list is the delivery identity | needs the list |
| L3 signal file | same as L2 with a name instead of content | simple | a name says "done", not "what"; no hash to verify |
| L4 version folder + pointer | the deployment points at a symlink the refresh flips | immutable deliveries, no half state, history by retention | needs the flip by the pipeline (the helper does it) |

Recommended (MINE): L2 on a list that every refreshed place carries, with L4 as a way to use the same mechanism (the deployment names `/srv/data/current`, a symlink; the app resolves it; no extra app code).

What the refresh must promise: write the data files, THEN run the delivery command (proposal name) that writes the list `delivery.yaml` (proposal) with `delivered` (UTC time stamped by the command), per file `name`, `bytes`, `sha256`, optional `source`, written under a temporary name and renamed. A pipeline that cannot run the command writes the same file itself; the format is in the specification.

What the app checks regardless of the promise (the two sides stay independent):
1. If the list exists: every listed file exists and `bytes` and `sha256` match; no listed file missing, no extra table file the recipe needs that is not listed. The app already reads all bytes to hash them (`cache_keys.py:146`), so the check costs one comparison. A mismatch is "the delivery is not complete": the opening stops with the plain reason and tries again at the next poll (RUN 6r: the page recovers by itself).
2. Always, list or not (a correctness fix in `libs/ingestion`, one place; applies to any file, not only deliveries): the file ends with a newline; every line has the header's number of fields (RUN: the cut line is silently null-filled today). Catches a cut mid-line. Does not catch a cut at a line boundary; says so in the Info panel when no list exists: "completeness of this data was not verified".
3. Mixed state (A new, B old): caught by 1 only.

Stored tables of the previous data: replaced under the same file name, one version (`anchor.py:175`); RUN 5c: 4 of 24 rewritten. Reproducibility does not rest on the store (rebuildable): it rests on the delivered files, kept by the deployer's retention (V4 folders), and on the export the visitor downloaded. Option "content-addressed store" (`tables/<key>.parquet`): copies on different deliveries stop overwriting each other, rollback is instant; new engine work in `anchor.py` plus age-based clean-up; not needed for one copy (OPEN, low rank).

Visitor with the page open (MINE): a persistent banner (not a toast): "New data was delivered on 2026-11-28 06:00 UTC. This page still shows the data of 2026-11-21. Reload the page to see it." No automatic reload; the export is refused until reload, as today ("the export is refused until the page is reloaded", notice text of RUN 5).

Reconsiders: D-0025 and `cache_keys.py:350-351` (data hash "once per session"; the code reads all files each time the effect runs, FACTS correction 3; the poll must not rehash).

## Q4. What the visitor is told about the data

| Where | Content |
|---|---|
| Banner (one line, always visible on a static page) | "Data delivered 2026-11-21 06:00 UTC · id a1b2c3d4e5f6" |
| Info panel, section "Data" | per table: place label, file name (never the server path), rows, short hash; the delivery date; the list's own hash; "completeness verified against the delivery list" or "not verified (no list)" |
| Export and report | `delivered`, list hash, per table: place id, file name, sha256, rows, `source` address (query string removed; never a token); data batch hash (already there, `export_handlers.py:215`) |

Source of the date: the list's `delivered` field. File mtime is not used (copies, `rsync -a`, container layers change it). Without a list no date is shown; the page says so. Short hash length: the session key uses 12 characters (RUN folder `55d26ecb838d:a1ae45bde9f0`), the session list 8 (FACTS E, `session_handlers.py:204`): unify (OPEN, small). This is new display work only; the hash is already computed (`home_theater.py:1528`).

## Q5. Fetching

| Option | What | Pro | Con |
|---|---|---|---|
| F1 outside the app (recommended) | a command of the connector library, `fetch` (proposal), run by cron, the pipeline, CI or a container entrypoint; same code as `fetch_data()`; reads the same table list from the deployment; stages into a new delivery folder; writes the list last; flips the pointer after it verified its own list | the app stays read-only on data (can be `:ro`); no network in the app (ADR-071 kept, "every path returned is a local filesystem path" ADR-048 section 5 kept); a failed fetch leaves the previous delivery in place; testable headless with a local file server | one more command for the deployer; Posit Connect: whether a scheduled job can write a kept folder is NOT VERIFIED |
| F2 at app start | today's `fetch_data()` hook (`bootloader.py:126-134`) | no extra step | a slow or failing network blocks the start; several processes fetch into one folder at once; token inside the app; no scheduled refresh |
| F3 app on a schedule | a thread in the web process | none that F1 lacks | races between copies; half state visible; reject |

Galaxy: files already local in the job folder; `delivery` list written by the tool wrapper's last step, or `none` (job success is the completeness). IRIDA: `irida.py:40-52` is a stub (`NotImplementedError`); the future fetch is the F1 command, not the start hook. Container with bound folders: fetch container binds the data folder `:rw`, the app container `:ro`. Tokens: only environment variables named in the file (`token_env`, proposal), never a value.

Reconsiders: ADR-048 section 11 / the start-time `fetch_data()` call (one way only: the command; the start check only verifies). ADR-071 is kept (information).

Several data files and where each is fetched (case c), proposal:
```yaml
places:
  data:
    - id: weekly
      path: /srv/sparmvet/data/current        # symlink flipped by the fetch command
      access: read
      find: table_name                         # file = <table>.tsv or .parquet
      delivery: required                       # required | none ; no default
      fetch:                                   # read by the fetch command only
        - {table: FastP,  from: "https://example.org/export/fastp.tsv",  sha256: any, token_env: EXPORT_TOKEN}
        - {table: Quast,  from: "/srv/pipeline/out/quast.tsv",           sha256: any}
        - {table: MLST,   from: "https://example.org/export/mlst.tsv",   sha256: "9f2c...e1"}   # a fixed file
```
`sha256: any` records the hash found; a value refuses a different file. The address and hash found go into the list and so into the export.

## Q6. Which file for which table

Today (READ `orchestrator.py:172-195`; default-data FACTS): default mode, a local `source.path` is used and nothing else is tried; `by_dataset_id`, every table is `<table>.tsv` in the data folder and the recipe path is ignored; the screen says neither.

ONE rule (MINE, CONFIRM of D-0425 "the deployment file decides what may be read"): a table is read from one file that lies inside a data place the deployment declares. Each data place says how its files are found: `find: table_name` (file named after the table: pipelines, static pages) or `find: recipe_path` (the recipe's `source.path` must resolve inside this place: the local development deployment declares `assets/test_data/` this way, so the shipped recipes keep their paths, D-0425). No precedence list: if two declared places could supply the same table, the opening is refused naming both (the data analogue of D-0424; not decided for data: OPEN). Per-table override only when needed: `tables: {FastP: {place: weekly, file: fastp_v2.tsv}}` (proposal).

Screen and export: the Info panel "Data" section and the export list, per table, place label + file name + hash + rows (Q4). That answers the finding of the default-data study that the pipeline-style lookup says nothing.

Reconsiders: `data_lookup` (`data_analysis_recipe_paths`, `by_dataset_id`) is replaced by `find` per place; D-0373 not touched; the hashes of the shipped recipes do not change.

## Q7. Two copies and many visitors

Specification states:
- Stored tables may be shared by copies; every read checks the key in the file footer (`anchor.py:109-114`), every write is temp file, fsync, `os.replace` in the same folder (`anchor.py:150-175`); a copy can never be served another copy's table, only a missing one (rebuild). RUN 9: two copies on one folder gave 24 identical tables.
- Two copies on different deliveries overwrite each other's tables and each opening rebuilds (slow, never wrong; REASONED, not run). Unless the content-addressed store (Q3) is built.
- Start clean-up deletes `.tmp` older than 600 s and tables of another cache version (B2): a copy of another app version on the same `work` removes the other's tables; stated, REASONED.
- A per-visitor place does not exist on a static page; per-visitor state is memory only. No session record: the one shared record of RUN 4 disappears because it is not written.
- Not atomic and so not allowed in `work`: `assembly.json`, ghosts (`session_manager.py:392, 539`): they live in `user`.

New work: the accessor (Q1); the start probe; `session_manager` constructed only when a `user` place exists (`server.py:149`); sessions, Data Import, BLUEPRINT drafts (`blueprint_handlers.py:351`) and bundle imports refused by the checker when there is no `user` place (extension of the flag cascade validator).

## Q8. The temporary place

A variable alone is not sound: two sources of truth (file and environment), invisible in the file, not recorded. The app applies it itself (MINE): at start it sets `tempfile.tempdir` and `os.environ["TMPDIR"]` to `work/tmp/<run>` before any export, so Quarto and Deno follow (RUN 10: the folder given by `TMPDIR` is used by the app and by Quarto). If the environment already sets `TMPDIR` differently, the file wins and the console says so. REASONED, not run: the assignment before the first call to `tempfile.gettempdir()`; confirm by a headless test. Polars spill folder (`POLARS_TEMP_DIR`) not checked.

When it cannot be written: with the start probe this cannot happen except a full disk later. Then the export must fail with the true cause, not a smaller bundle with "install Quarto" (RUN 10): classify the Quarto error; a permission or space error names the `work` place.

## Q9. What stops and what warns (proposed sentences)

Principle (MINE): a configuration error stops the process (operator must fix; loud). A state of the data that can heal (absent, incomplete, other columns) keeps the page up with a reason when the deployment says `delivery: required`, because RUN 6r shows the page heals within 5 s; a pipeline run (`delivery: none`) stops. OPEN for her.

| Situation | Visitor reads | Operator reads |
|---|---|---|
| data absent at start (static, `delivery: required`) | "There is no data to show yet. The data for this analysis has not been delivered. Try again later, or contact: <contact>." | "[WARN] Place 'weekly' (/srv/sparmvet/data/current): no delivery list. The page shows 'no data yet' and checks again every 2 s. Run the delivery command after the data files are in place." |
| data absent at start (pipeline, `delivery: none`) | none (process ends) | "[FATAL] Table 'FastP' has no file in place 'job' (/.../inputs). Expected FastP.tsv or FastP.parquet. The run stops." |
| refresh with other columns | "The data delivered on 2026-11-28 does not have the columns this analysis expects, so it cannot be shown. Contact: <contact>." (neutral: not "correct the recipe") | "Table 'FastP': column 'total_reads' declared by the recipe is not in the delivered file; the file has: total_reads_RENAMED, ... Either the data or the recipe is out of date." |
| partial file | "The data is being updated or was not delivered completely, so it is not shown. This page checks again by itself." | "FastP.tsv does not match the delivery list: expected 8346 bytes, found 4179; sha256 differs." (no list: "FastP.tsv ends in the middle of line 22: 7 of 14 fields.") |
| `work` not writable | none from the app (process ends; proxy error) | "[FATAL] The work place (/srv/sparmvet/work) cannot be written: Permission denied. In a container bind a folder with :rw, or declare `work: temp`. The app does not start." |

A page that starts only to say "cannot start" for the `work` case would need a second start mode; not recommended now. No path of the server in the visitor text (RUN 2b shows paths today).

## Q10. Use case templates (every key a proposal)

(a) Static page, one recipe, weekly data:
```yaml
deployment_type: filesystem
default_data_analysis_recipe: weekly_amr_2026-11-20
places:
  recipes: [{id: shipped, path: /srv/sparmvet/recipes, access: read}]
  data:    [{id: weekly,  path: /srv/sparmvet/data/current, access: read, find: table_name, delivery: required}]
  work:    {path: /srv/sparmvet/work}
  # no `user`, no `gallery`: nothing to save, no Gallery
```
Operator prepares: the three folders; recipe folder with the recipe; the refresh job ending with the delivery command. Checked at start: recipes place exists; the recipe passes structure; data place exists and the list matches; `work` exists, probe writes and deletes; no feature that needs `user` is on. Today `gallery` must exist even unused (`filesystem.py` `_REQUIRED_TO_EXIST`, READ): the proposal drops it for a deployment with the Gallery off.

(b) Pipeline run (usegalaxy, IRIDA):
```yaml
deployment_type: filesystem
default_data_analysis_recipe: fixed_recipe
places:
  recipes: [{id: fixed, path: /opt/sparmvet/recipes, access: read}]
  data:    [{id: job, path: "${PIPELINE_JOB_DIR}/inputs", access: read, find: table_name, delivery: none}]
  work:    temp
```
`${...}` expands today (`path_expansion.py:21`, `expandvars`). Operator prepares: the job folder with files named after the tables. Checked at start: each table has a file; `delivery: none` is printed and the Info panel says completeness is not verified; system temp writable (else the N1 text).

(c) Several files fetched (the weekly fetch job, outside the app): the `fetch:` list of Q5 in the `data` place of (a); `work` as in (a). Checked at start by the fetch command: addresses reachable, `token_env` set, hashes; by the app: as (a).

## Decisions table

| point | DECIDED / CONFIRM / OPEN | proposal | reconsiders (info) |
|---|---|---|---|
| one specification, named places with an access word | DECIDED D-0417, D-0418 | `work` is one more place in it | D-0418 asked "where is the cache": this answers |
| no `users:` word; saves only in a user place from system variables; static has no save | DECIDED (her words, brief) | no `user` key on a static page; session manager absent | none |
| the app checks each declared place at start | CONFIRM (D-0417 reading b) | exists + probe write/delete at start | none |
| the app's place: one or two | OPEN | V1 one `work` | ADR-048 s3, s5 |
| `work` access word | OPEN | fixed by kind | none |
| nothing writable | OPEN (choice 5) | N4 | none |
| stop or stay up when data is absent at start | D-0427 DECIDED ("the opening should stop with a plain reason"); process exit vs page: OPEN | page with reason when `delivery: required`; exit otherwise | none |
| delivery list required | OPEN | required for a refreshed place; `none` explicit | none |
| structural check of data files (newline, field count) | MINE (not decided) | in `libs/ingestion`, all files | none |
| fetch outside the app | OPEN | F1 | ADR-048 s11 (start `fetch_data`); ADR-071 kept |
| data lookup rule | D-0425 DECIDED (the deployment decides); form OPEN | `find` per place | `data_lookup` key |
| same data table name in two places | OPEN (D-0424 not asked for data) | refuse, naming both | none |
| data identity on screen and in export | OPEN | Q4 | ADR-097 (export record gains place, hash) |
| TMPDIR | OPEN | applied by the app from `work` | none |
| data hash frequency | DECIDED D-0025 vs code differ | poll must not rehash | D-0025 text |
| no audit on a static page | DECIDED D-0302 | consistent | none |
| build at opening | DECIDED D-0326, D-0335 | the 22 to 31 s is this build, paid at each start under `work: temp` | none |

## What an audit or test would not catch

- A refresh without a list that is cut at a line boundary or mixes weeks: no test of the app can see it; only the list does. A deployer who declares `delivery: none` accepts this; the page must say so.
- A pipeline that writes the list before the files: the list then matches nothing and the page refuses; the failure is loud but looks like a data error.
- `work` shared by two people with private data: derived tables readable by file system access; no check inside the app.
- The listed hashes prove the files are those listed, not that the pipeline produced the right science.

## Testable without a browser

Delivery list read and verify (library); structural TSV check; `work` probe and the TMPDIR application; the `find` rule and the two-places refusal; fetch command against a local file server; the checker refusing flags that need `user`. Needs a browser: the banner, the persistent notice, the refusal page and its self-healing.

## Not verified

Posit Connect: persistence of a kept folder and the number of Shiny processes per content. Whether `os.environ["TMPDIR"]` set at start reaches Quarto in the app's subprocess call (REASONED; RUN 10 covers the variable set before start). Mixed-week state (REASONED, not run). Two copies on different deliveries (REASONED). The Polars spill folder. The ledger line after D-0428 (not in the ledger when I read it). `recipe_gate_handlers.py` poll lines are READ via FACTS, not re-read by me. Container build (does not build today, F16).
