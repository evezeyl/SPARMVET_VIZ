# Where a data file that the user gives to the app is saved: the architect viewpoint (developer view merged), 2026-11-21

Study only. Nothing in the repository was changed. Scratch: `tmpAI/panel/uploaded_data_place/architect_scratch/` (`confine.py`, `confine_out.txt`).
Labels: RUN = I ran it; READ = read at file:line; REASONED = follows, not run. Tags: DECIDED (ledger number) / CONFIRM (her words read one way, she confirms) / OPEN (hers) / MINE (my proposal, never a decision). Every key name and screen sentence is a PROPOSAL.
Her rule applied: an option is judged on merit; "reconsiders a decision" is information in its own column.

## 0. Summary (6 lines; what changes a result silently first)

1. SILENT TODAY: a Data Import upload overwrites the file the recipe reads (a shared file, or a test file tracked in git), keeps no copy, and records neither the uploaded name nor the date (READ `orchestrator.py:197-209`, `data_import_check.py` `store_all`). The upload control shows whenever `testing_mode` is true, and `testing_mode` is true when the key is absent (READ `bootloader.py:903-905`; 4 of the 8 shipped app features files that set it have it true).
2. SILENT TODAY: a saved session restored on other data gives only a warning (READ `session_handlers.py:607-616`); the sentence "N saved sessions will no longer open" (D-0434 relay, deployment_io row 2) is not what the code does, so the confirmation text must be written from the real behaviour. A cut file is accepted without a word (RUN, `data_file_cut/REPORT.md`).
3. RISK IN ANY DESIGN: a data choice that falls back to the recipe's default when the chosen file is missing would run another dataset without telling. Rule proposed: a chosen file that is missing stops the opening with a plain reason, never a fallback (MINE).
4. RECOMMENDATION (MINE): ONE mechanism, "set the data of a table", with two sources (the browser upload copies the bytes into the user's `read_write` data place; a file of a declared place is only linked); both write ONE small link record per recipe in the user place; `locate_dataset_file` (`orchestrator.py:172`) is the only reader of it, so reading, hashing, keys, sessions and export follow it.
5. CASE 2: (b) the app lists the files of the declared places and the user picks one, no copy, no typed path; (a) is what the user does before, (c) stays only as the browser source, (d) is not recommended (second way, a security burden, no gain over (b)).
6. D-0426 cannot be reached today: the load gate reads the data once at start and rejects a recipe whose data is absent, so it never reaches the selector (READ `bootloader.py:431-447`; RUN case 6 of `deployment_no_user/RUN_FACTS.md`); the gate's data check must be split from the recipe check.

## 1. Facts I verified (the ones my answer rests on)

| # | Fact | Label | Where |
|---|---|---|---|
| F1 | The Data Import upload control appears only when `testing_mode` is true; otherwise a read-only list of paths. | READ | `data_import_handlers.py:83, 131-139, 162` |
| F2 | `testing_mode` defaults to True when the key is missing. Shipped features: true in developer, qa, standalone, pipeline-exploration-advanced; false in web-demo, demo-vetinst, pipeline-static, pipeline-exploration-simple. | READ | `bootloader.py:903-905`; `config/app_features/*.yaml` |
| F3 | The target of an upload is `file_place`: the file `locate_dataset_file` finds, else the recipe's `source.path`, else `<table>.tsv` in the deployment's data folder; None for a recipe imported from a bundle. A relative `source.path` is used as written (relative to where the app was started). | READ | `orchestrator.py:172-209`, `:193-194` |
| F4 | The write: copy to `<target>.import-tmp`, then `os.replace` over the target. No copy of the old file, no record of the uploaded name. The success notice (10 s) shows the file name and the full server path. | READ | `data_import_check.py` `store_all`; `data_import_handlers.py:303-308` |
| F5 | `locate_dataset_file` is the one place that decides the file; `_read_source`, `get_source_files` (hashes, session, export, Source view) and `file_place` all call it. | READ | `orchestrator.py:172, 249, 817, 206` |
| F6 | `DataOrchestrator(...)` is built in four non-test places: `server.py:102`, `bundle_importer.py:299`, `gallery_examples.py:90`, `data_analysis_recipe_validator.py:506`; 66 constructions in tests. Anything the orchestrator needs (a link store) must reach all four. | RUN (grep) | grep of `DataOrchestrator(` |
| F7 | The load gate (`_gate_one`) reads every recipe's data once at start with the deployment's data folder and the imports folder; a recipe that fails is rejected and never reaches `available_data_analysis_recipes`. A user's choice does not exist at that time. | READ | `bootloader.py:431-447, 449-470` |
| F8 | A recipe imported from a bundle reads only `<user_data>/_imports/<recipe id>/data/<table>.<ext>`; the folder's existence is the record. The refusal of a replacement is an agent's PROVISIONAL choice. | READ | `orchestrator.py:156-186`; `data_import_check.py:40-49`; `ANSWERS_A_AND_B.md` a |
| F9 | The keys of stored tables hold the content hash of the files they read; a changed file gives other keys, so a stale stored table is not used. `refresh_replaced` additionally deletes the stored anchor and the in-memory cached asset of each replaced table. | READ | `cache_keys.py:462-474`; `data_import_check.py` `refresh_replaced` |
| F10 | The data hash is `sha256(path.read_bytes())`: the whole file in memory, at every call, no cache by size or time. Called by the keys, by the provenance effect at each opening, and again by the session ghost (`_file_sha256`). A missing file gives `MISSING:<id>` as a key. | READ | `cache_keys.py:139-147`; `session_manager.py:1053-1057`; `home_theater.py:1528-1530` |
| F11 | `ingest_file` (the Data Import check) reads the whole file once (`lf.collect()`). A row with fewer fields than the header is accepted (null fill). | READ + RUN | `ingestor.py:~153`; `data_file_cut/REPORT.md` |
| F12 | The session record stores per file the full server path and sha256. The export records `data_batch_hash` and `data_source_paths` (full paths); no per-file place, no uploaded name. | READ | `session_manager.py:~382-389`; `export_handlers.py:141-146, 215, 223` |
| F13 | A session restored on another data hash opens with a warning, not a refusal. The session list shows all sessions with the short data hash. | READ | `session_handlers.py:607-616, 204` |
| F14 | The reproducibility bundle contains the raw data files, named `<table><ext>`; a warning ("anyone who gets the bundle gets the data") is shown after the export; the handling of sensitive data is "#46, not built". | READ | `export_handlers.py:1511-1545` |
| F15 | In a deployment that finds data by table name, the Data Import panel shows only the folder, not the file of each table. | READ | `data_import_handlers.py:86-97` |
| F16 | Shiny keeps an upload in a temporary file (`datapath`, folder given by `TMPDIR`: RUN case 10 of `RUN_FACTS.md` saw `fileupload-*` there). | RUN (earlier) | `RUN_FACTS.md` case 10 |
| F17 | A path check by resolved path refuses `..`, an absolute path, a symlink that leaves the place and a sibling folder with a similar name; a string-prefix check accepts the sibling. A NUL byte raises. | RUN | `architect_scratch/confine_out.txt` |

## 2. Answers per question

### Q1. Case 1, the user uploads from the own computer

Review session's reading (only in a `read_write` data place, never in a `read` place, never at the recipe's own `source.path` in a `read` place): CONFIRM, and I strengthen it (MINE): never at `source.path` at all. After D-0425 a recipe's path is a default to read, not a place to write; it can be relative to the working folder (F3) or lie in git. The app chooses the write target, not the recipe.

| Point | Proposal | Tag |
|---|---|---|
| Which place | The user's `read_write` data place named in the deployment file; if the deployment has none, there is no upload control (absent, not greyed). | DECIDED in substance: D-0417, D-0418, D-0429 (4), D-0434 ("writes are done where a user can write"). The control gated by "a writable data place exists", not by `testing_mode`: MINE |
| Subfolder | One subfolder per recipe: `<my data>/<recipe id>/`. Why: the same uploaded name for two recipes then never meets; a replacement can only change the recipe it is made in (blast radius one recipe). | MINE; OPEN for her |
| File name | The uploaded name, kept. Names with a separator, `..`, NUL, control characters, empty or too long are REFUSED with the reason, never renamed (a rename is a hidden step). The "name exists" test is the file system's own (a case-insensitive disk is then right). | MINE; D-0434 says "name already exists", so a name stays the name. Whether the dated name rule (D-0390, D-0437) applies to data files is OPEN |
| Replacement | Same name in the same recipe folder: replaced after a plain confirmation that says which tables of which recipes read it and how many saved sessions were made with it; no copy, no archive. | DECIDED: D-0434. The words of the confirmation: MINE (see below, the session sentence must be true) |
| The link "this table reads this file" | One link record per recipe in the USER place (not in the data place): `<user place>/data_links/<recipe id>.json` (proposal). Entry per table: source kind (`uploaded`, `selected`, `bundle`), place id, path inside the place, uploaded name, date (UTC), sha256 at that moment. Written atomically (temp file then `os.replace`, as `store_all` does today). | MINE |
| Where it is read | In ONE place: `locate_dataset_file`, order: (1) the link of this recipe and table; (2) the declared path or table name (today). A link beats the default; the screen says so per table. Because F5 holds, `get_source_files`, the keys, the session, the export and the Source view follow without a second rule. | MINE |
| A linked file that is missing | The opening stops with a plain reason that names the table, the file and the date of the choice, and offers "choose again" or "use the recipe's default again". NEVER a fallback to the default. | MINE; consistent with D-0427 and her "nothing changes a result silently" |
| A second recipe with a table of the same name | Reads its own link, else its own default. Nothing is inherited between recipes. (Per recipe id: a new dated recipe starts with no link; the user chooses again, with the old choice shown in the old recipe's record.) | MINE |
| What the screen says after the upload | Per table, one line: "Table 'X' is now read from your file 'name.tsv' (My data / recipe / name.tsv), uploaded 2026-11-21 14:02, content hash ab12cd34. The earlier data file of this table was replaced and is not kept." Not only a toast of 10 s: the same line stays in the Data Import panel as the "source of each table". | MINE (proposal text) |
| Recorded for export and report | Per table: source kind, place label, path inside the place (never the absolute server path), file name, date of the choice, sha256 of the content now (computed at export) and at the choice. Replaces `data_source_paths` (full paths). | CONFIRM/OPEN; it is point 7 of `deployment_io` "PROPOSAL OF THE VIEWPOINTS", not decided |
| Stored tables | Rebuilt at the next opening: the keys hold the content (F9). `refresh_replaced` stays only for what is NOT keyed by content (the in-memory cached asset by recipe and table); the file deletion is a second mechanism beside the keys: to re-check, not assume. | READ + REASONED |
| Saved sessions made on the earlier file | The session key holds the data hash, so they stay in the list; restoring one gives only a warning (F13). So the confirmation must say "restoring them will show a warning; their steps may match other rows", NOT "will no longer open". Whether a session on other data should be REFUSED (as D-0362 does for a changed recipe, not built) is OPEN. | READ; OPEN |
| Kept after the session? | Yes: the sessions and keys depend on the same bytes; a file kept only for the session would make every saved session unreadable. It stays until the user deletes it. | MINE |
| Remove it from the app? | No delete control (D-0437: "the user deletes the file in his own file system"; D-0434: no copy, no archive). The app gives the path and the button "use the recipe's default again" (removes the link, never the file). Consequence to say: where the user cannot reach the folder (an unbound container folder, a Galaxy job folder) the user cannot delete it. | CONFIRM + MINE; OPEN |

### Q2. Case 2, the data is already where the app runs (HPC, Galaxy)

What all four options share: the deployment file names the places (D-0425, D-0417); a file outside them is never read. On a per-person copy the person is also the one who declares the places.

| | (a) the user puts the file in a declared place and the recipe reads it by path or table name | (b) the app lists the files of the declared places; the user picks | (c) download, then browser upload | (d) the user types a path |
|---|---|---|---|---|
| Today | by path: only if the recipe's own path points there; by table name: only in a pipeline deployment, with the upload refused (`BY_DATASET_ID_REFUSAL`) and no per-table file on screen (F15) | does not exist | works where `testing_mode` is true; overwrites (F3, F4) | does not exist |
| For a user who does not know where the app looks | Bad: nothing says where to put it. The panel today shows the folder of the deployment or the paths of the recipe. | Good: the screen lists the declared places with their label, path and access word, and what is in them. | Fine for the user, absurd on HPC (down, then up) | Bad: the user must know the exact path |
| Large files | No copy | No copy, no upload; the reads of the app remain (F10, F11: the whole file in memory for the hash, a whole read for the check) | Three transient copies (temp, `.import-tmp`, final) plus the whole read; upload limit of Shiny NOT verified | No copy; same reads |
| D-0425 (the deployment decides what may be read) | Implements it, but a recipe's own path can still point anywhere (`orchestrator.py:193`; not confined today) | Implements it: the choices come from a listing of the declared places only | Writes only where the deployment says (new rule for the target) | Needs a confinement check on every typed path (below) |
| Security | Unchanged | The client sends back a choice; the server accepts only a place id plus a path that resolves INSIDE that place (F17); it never takes a raw path from the browser | Name of the upload sanitized (Q1) | Typed text is the most hostile input: absolute paths, `..`, symlinks, a sibling folder with a similar name, NUL. A resolved-path check (F17) is needed, and a symlink into another declared place is refused unless that target is itself declared |
| Screen | no per-file line | list, per table the chosen file and place; a filter box (a filter of the listing, never a typed path) | as Q1 | a text box |
| Recorded | nothing | the link (source kind `selected`, place, path, date, hash at the choice); no bytes copied | the link (source kind `uploaded`) | as (b) |

Recommendation (MINE, on merit): (b), with (a) as what the user does before it. (c) is not another mechanism but the browser as one source of the same step. (d) is not recommended: it is (b) plus the typed-path attack surface and no discovery; "one way to do each thing". A caution on (b): the check I ran refuses a symlink that leaves the place (F17); on HPC a data folder is often a symlink to a project area, so the user (or administrator) declares that real folder as the place. That is a documentation sentence, not a bug.
What the user must know and do: (a) the folder to use and its access word; (b) nothing but the choice. In (b) only `.tsv` and `.parquet` are listed (what the ingestion reads, `file_kind`); the list shows size and time, not a hash (a hash of a large file costs a whole read).

### Q3. One mechanism or two?

ONE (MINE): "set the data of a table". Sources: (1) the browser upload, which first copies the bytes into my data and then links them; (2) a file of a declared place, which only links. Both call the same pure function and write the same link; the difference is whether bytes are copied. D-0426's "the user selects the data" is the same step, not a second one.
Where the user meets it: BOTH, one component. (i) At the opening of a recipe whose data is absent (D-0426), only where the deployment lets the user choose; where it does not (static page, pipeline) the opening stops with the reason (D-0427). (ii) In HOME's Data Import panel, at any time, to change a table. The panel always lists, per table, the source today (default, uploaded, selected, bundle).
A real consequence (READ F7): today a recipe with absent data is rejected by the load gate at start and never reaches the selector, so (i) cannot happen. The data check of the gate must become a question of the user's choice (the gate checks the recipe; data availability is checked at the opening, per user and per link). This reconsiders ADR-094 ("a recipe failing either check never reaches available"); D-0426 already implies it. Not built.

### Q4. "Is the app saving the data uploaded?" (two sentences for the documentation)

Today: "Yes. A file uploaded in Data Import is written over the data file that the recipe reads, which can be a shared file or a test file of the repository; the old file is not kept and the name of your file is not recorded."
Under the proposal: "Yes, in your own data folder only (the path is shown), under the name you gave it, in a folder for the recipe; the app records which table reads it, the date and its content hash, keeps it until you delete it in your own file system, and never writes into a shared (read) place."
Told at the moment of upload (MINE; proposal text): where it will be saved (the path); that an existing file of the same name in that folder is replaced after your confirmation, with no copy; that everyone who can open that folder can read it, and where one running copy of the app is used by several people, everyone using that copy can use it (D-0429, F2 of `deployment_io`); how long it stays (until you delete it yourself); that it is not copied to a shared place by the app, but that a reproducibility export includes the file itself (F14, today the warning comes after the export); that the app does not delete your files.

### Q5. The user's own business and what the app guarantees

| The user's business (her words, D-0434) | The app guarantees |
|---|---|
| Which file is the right one; keeping the earlier copy elsewhere; deleting a file; choosing another name to keep two versions; anonymising sensitive data; putting files in a declared place by own means | Says, per table, which file is read, from which place, chosen when, its hash; reads nothing outside the declared places; reads no other file silently (no fallback to the default when the chosen file is gone); writes only into a `read_write` place of the user and only after confirmation when it replaces; refuses a name it cannot keep as it is; checks the file with the recipe's reader before any write (`apply_import`); tells before the upload the consequences of Q4; records place, name, date and hash for export and session |
| What the app does not do | compares no content, keeps no copy, offers no "already present" answer (D-0435), deletes nothing, judges nothing about whether data is cut or right (see 6.4) |

### Q6. Edge cases

| Case | What happens today | Under the proposal |
|---|---|---|
| 1. Two tables read the same file | One upload for both is checked for both (`shared`, `data_import_check.py` `_check_one`) | A link entry per table; one file may be linked to several tables; replacement names every table (and recipe) that reads it |
| 2. Recipe imported from a bundle | Upload refused (PROVISIONAL, F8); reads only its import folder | D-0435 puts the data in the user's data place. The same link (source kind `bundle`, bundle hash result kept) replaces the "folder exists = record" rule and removes one special branch from `locate_dataset_file` and the refusal. Whether the user may then re-link a table of an imported recipe (it would no longer be what the bundle verified; the screen would say it) is OPEN |
| 3. Static page or pipeline | No control (F1, F2); by table name the screen shows no file per table (F15) | No control (D-0429 4, D-0427). A link record is not consulted where the deployment lets the user choose nothing; a link found there is told, not silently ignored (OPEN, small) |
| 4. A cut file or other columns | Accepted without a word (RUN); fewer fields accepted; other columns left out with a log line only | Unchanged by this study. The choice (refuse, warn, a delivered row count or hash) is a separate open decision (`data_file_cut/REPORT.md` options 1 to 5). It applies the same to uploaded and selected files, and to a selected file again at each opening |
| 5. Same uploaded name for two tables | The second upload replaces the file of the first | Per-recipe folder: across recipes they never meet. Inside one recipe it is one file read by both tables, and the confirmation says so. A user who means two files renames one on the own side (his business) |
| 6. Very large file | READ: three transient copies, a whole read for the check, `read_bytes()` for each hash at each call (F10, F11); upload limit NOT verified | (b) removes the copies, not the reads. The hash read is the limit and is not caused by the proposal; it is better known before the first HPC file. NOT measured |

## 3. Two or three variants for the link (the real choice)

| | V1 position is the choice | V2 a link record per recipe (recommended, MINE) | V3 the data choice written into a dated copy of the recipe |
|---|---|---|---|
| Idea | The file `<my data>/<recipe id>/<table>.tsv` exists, so it wins over the default (as `_imports/<recipe>/data/` does today) | As described in Q1; a file of any declared place can be linked | The chosen path goes into a new recipe file `name_date`; the recipe and its data are one hashed document |
| Pros | No record store; the bundle import already works this way; nothing to keep in step | One mechanism for upload, selection and bundle; explicit and visible; the record carries name, date, hash; no copy needed for case 2 | The choice is part of the scientific document; no second store |
| Cons | A file left in the folder silently wins at the next opening (presence = choice); no uploaded name, date or hash without a sidecar (which is a record again); case 2 impossible without a copy, so TWO mechanisms; the file name is the table name, so D-0434's "name exists" means a table name and every re-upload asks | A second store beside the files: it can disagree with them (a deleted or edited file); solved by the rule "missing file stops, changed content is shown by the hash", and by one reader (`locate_dataset_file`); small new pure module | A new recipe file for every data choice (D-0390: dated names, refusal of an existing name); the `read` recipe place is not the user's; hashes of recipes change with the data; the Gallery and the recipe selector fill with copies |
| Touches | D-0434 reads differently (table name) | D-0434, D-0435, D-0437 consistent; D-0425 implemented; ADR-094 gate (also needed for D-0426); ADR-097 record | D-0390, D-0391, ADR-092 (the file name is the identifier) |
| Where it reconsiders a decision | no | no decision is reconsidered by the link itself; ADR-094 and the role of `testing_mode` are touched (information) | D-0390 naming in practice |

## 4. Table: case, where the file is, who may write there, what the app records, what the user sees

TODAY (READ unless marked)

| Case | Where the file is | Who may write there | What the app records | What the user sees |
|---|---|---|---|---|
| 1 upload, `testing_mode` true | The file the recipe reads (`orchestrator.py:197-209`): a shared file, a test file of git, or `<table>.tsv` in the data folder | Anyone with the control; nothing checks the access of the place; the operating system only | Nothing about the upload (no name, no date). The new content hash enters keys and session record | A toast of 10 s with the file name and the full server path; the panel text before the upload does not say that the old file is lost (S9 of `data_import_words`) |
| 1 upload, `testing_mode` false | No upload | Nobody | Nothing | "Data paths are set by the deployment configuration (read-only)" and a list of paths (a folder only, by table name) |
| 2a file put in place by own means | Where the recipe's path or the table name points | The user, by the operating system | The data hash enters keys, session and export | Nothing says where to put it; a change is noticed by the data-change notice only when a page is open and a tab is clicked (RUN case 5) |
| 2b listing | does not exist | | | |
| 2c download then upload | as case 1 | as case 1 | as case 1 | as case 1 |
| 2d typed path | does not exist | | | |

PROPOSAL (MINE)

| Case | Where the file is | Who may write there | What the app records | What the user sees |
|---|---|---|---|---|
| 1 upload | `<my data>/<recipe id>/<uploaded name>` in the user's `read_write` data place | The app, only there, only after a confirmation when the name exists; never a `read` place, never `source.path` | The link (kind `uploaded`, path in the place, uploaded name, date, hash at the choice) in the user place; export and session: place label, path in the place, hash | Before: where, for how long, who can see, no copy of the old file, the export carries the data. After: one line per table with the source; the same line stays in the panel |
| 2a put in place by own means | Any declared place | The user, by the operating system | Nothing until the user selects it | The screen lists the declared places and says "put the file there, then choose it" |
| 2b select | Any file in a declared place (a `read` place too) | The app writes only the link, in the user place | The link (kind `selected`) | The list of files per place with size and time; the choice per table; the source line |
| 2c browser upload | as case 1 | as case 1 | as case 1 | as case 1; the screen says it is a copy |
| 2d typed path | not offered | | | |

## 5. What is DECIDED, what only CONFIRMS, what is OPEN, where it reconsiders

| Point | Tag | Note |
|---|---|---|
| Data written only where the user can write; no copy, no archive, replace after confirmation | DECIDED D-0434 | |
| `read` and `read_write` words; the user's directory is `read_write` | DECIDED D-0437 | |
| The deployment file decides what may be read and written; select the data where the default is absent; stop where the user cannot select | DECIDED D-0425, D-0426, D-0427 | |
| What the app saves for a person is in a user place; no control where there is no user place | DECIDED D-0429 | |
| Bundle import writes into the user's own places | DECIDED D-0435 | how the orchestrator finds it afterwards is not decided (MINE: the link) |
| One mechanism with two sources | MINE | follows from D-0426 and D-0434 |
| Link record per recipe in the user place | MINE | |
| Never a write at the recipe's `source.path` | MINE (strengthens the review session's reading) | |
| A missing linked file stops, no fallback | MINE | consistent with D-0427 and her principle; CONFIRM |
| Per-recipe subfolder; the uploaded name kept; refusal of bad names | MINE / OPEN | |
| Dated name rule for data files | OPEN | D-0437 names recipes; D-0434 mentions "the rule of the dated file name" |
| Session on other data: warn (today) or refuse | OPEN | D-0362 is for a recipe |
| No delete control; "use the default again" only | CONFIRM (her words D-0437) + OPEN | |
| Re-link of a bundle-imported recipe | OPEN | PROVISIONAL refusal today |
| (b) listing in case 2; (d) not offered | MINE | |
| Export record without absolute paths, with place and hash | OPEN | `deployment_io` proposal 7 |

Reconsiders (information only): ADR-094 (the gate checks data at start; needed for D-0426 anyway); the meaning of `testing_mode` (it gates the upload control today; D-0429 4 gates by the existence of a place); ADR-097 (what the export records about data); ADR-048 five location keys (D-0436 already). Not reconsidered: ADR-089, ADR-101 (keys by content), D-0425, D-0434, D-0435, ADR-045 (pure module with a thin handler, the same split as `data_import_check.py`).

## 6. Developer view: order, steps, tests, risk

Order (effort is information, not an argument): the link module needs the named places of D-0436, which is one merge. Before that there is nothing small and whole to build; a stop-gap on Data Import would be a half fix. The facts of 0.1 stay true until then, and the documentation sentence for TODAY in Q4 can be written now.

| Step | What | Size and risk |
|---|---|---|
| 1 | Her answers to section 7 | |
| 2 | Pure module (proposal name `data_links`): read and write the record atomically; list a place; `confine(place, relative)` by resolved path; refuse bad names. No Shiny (ADR-045). | Small; low risk |
| 3 | `DataOrchestrator` gets the link store (four construction sites, F6; optional because a static deployment has no user place: a real state, not a shim). `locate_dataset_file` consults the link first; a missing linked file raises the plain error. | Medium; the risk is a second reader somewhere, check by grep that nothing reads `source.path` outside `locate_dataset_file` (libs `recipe_check`, `recipe_graph`, `blueprint_arch` read the path for display or checks: to verify) |
| 4 | Split the gate: recipe check at start, data availability at the opening, per user. `reject_after_opening`, `recheck_changed_data_analysis_recipes` follow. | Largest; touches ADR-094, the recipe selector (a recipe with absent data now appears) |
| 5 | Data Import handler: the target is the my-data place, the confirmation (Shiny modal with the counts), the per-table source line, "use the default again", the listing for (b). | Medium |
| 6 | Export and session: place, path in the place, hash, no absolute path. | Medium; changes a recorded format (versioned record) |
| 7 | Bundle import writes data into the user's data place and its link (D-0435), the special folder branch goes. | Medium |

Tests without a browser (all on the pure module and the orchestrator): (1) confinement: `..`, absolute, symlink out, sibling folder with similar name, NUL, case variants; (2) with a link, `locate_dataset_file`, `get_source_files`, `_read_source`, the keys and the export record name the SAME file (the one-path claim as a test); (3) a link to a missing file raises, and the default is NOT read; (4) a second recipe with a table of the same name keeps its default; (5) replacement: the counts of readers and sessions come from the real records; the sentence says "warning", not "no longer open", as the code does; (6) replacing under a write failure leaves the link and the file as they were (as `store_all` tests today); (7) a name with a separator is refused, not renamed; (8) break the code once (let the missing-file case fall back) and see test 3 fail.
What an audit or a test would NOT catch: the screen wording and whether a person reads it; real permissions on HPC or an unbound container folder; symlinked data folders; the cost of a hash of a large file; two copies of the app on one folder (last write wins; the record is atomic, so not torn; NOT run); the Shiny upload limit and the space of `TMPDIR`; a user who edits a linked file in place (shown by the hash, not prevented).

## 7. To decide first (ranked)

1. Is the data choice a link record per recipe (V2), the position of a file (V1) or part of a dated recipe copy (V3)? Everything else follows from it. I recommend V2 on merit.
2. Where the bytes go and under which name: a subfolder per recipe in the user's data place, the uploaded name kept, bad names refused. Does the dated name rule apply to data files?
3. Confirm: a chosen file that is missing stops the opening, never a fallback to the recipe's default.
4. A saved session restored on other data: keep the warning, or refuse as D-0362 does for a recipe. The confirmation text depends on it.
5. Case 2: confirm (b), the listing of declared places with a choice, and that a typed path is not offered.
6. No delete control in the app, only "use the default again", and the user told where the file is; accepted where the user cannot reach the folder?
7. A recipe imported from a bundle: may the user re-link its tables?
8. What the export records about each data file (place, path inside, name, date, hash; no absolute path).

## 8. Not verified

- No app was started, no browser seen; every screen sentence is a proposal, not tested with a user.
- The Shiny upload size limit and the behaviour of a multi-GB upload; the time and memory of `read_bytes()` on a large file (read in code, not measured).
- Whether anything outside `locate_dataset_file` reads a recipe's `source.path` to open data (`recipe_check.py`, `recipe_graph.py`, `data_analysis_recipe_navigator.py` read it; I did not check whether any opens the file).
- Whether `refresh_replaced`'s deletion of the stored anchor is still needed beside the content keys (REASONED: the in-memory asset is not keyed by content).
- Whether the per-file hash is in the standard (non-bundle) export; I read only `data_batch_hash`, `data_source_paths` and the stage keys.
- Galaxy, IRIDA, Posit Connect: nothing run; what a Galaxy job folder lets a user delete is not known.
- The behaviour of two copies of the app on one data folder (D-0428 case, run in `deployment_no_user` only for stored tables).
