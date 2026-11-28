# A session that brings its data: the options (nothing is built; the owner decides)

Written 2026-11-28 for Eve (channel block M720 and her change of order). Evidence words: READ (file:line), RAN (earlier study `tmpAI/demo_upload_study/`), REASONED.

## Overview first

**What she decided (2026-11-28).** Audit steps must not mix across datasets: fixed, not a limit. A Restore must use the data that were used in that session. A mechanism is needed that allows changing the data and takes the change into account.
**What is built today.** A Restore on other data is refused (G1). That is the floor: the app does not bring the old data back; she must upload the same files again, byte for byte (RAN: one added byte or Windows line ends give another session key).
**What is missing.** (1) The app keeps no copy of the replaced file (D-0434). (2) At an upload the app makes a new session by itself, without asking. (3) While steps are in the view and the data on disk change, the next added step is written under the new data key together with the old steps (RAN, `tmpAI/gaps/g1_live.py`; see G1 on `home_guardrail_gaps.md`).
**First thing to know: every option that keeps data REOPENS D-0434 ("which data is analysed is the user's problem, no copy")**, and touches D-0439 and D-0440 (how data reaches the app is defined by the deployment; upload off unless the deployment asks for it), the session key rule of contract section 12d, and D-0312 (old session files are refused, not converted).

## Facts from the code

- Where a data path is decided: `DataOrchestrator.locate_dataset_file` (`app/modules/orchestrator.py:182-198`) is the one place; `file_place` (`:207-`) is where an upload is written. Three cases: a bundle import (`<imports_dir>/<recipe id>/data/<table>.tsv`, `:169-180`: the data of an import is only what its bundle carried), `by_dataset_id` (`<table>.tsv` in `raw_data`; Data Import refuses it, `data_import_check.py:163,207`), or the recipe's `source.path`. The orchestrator knows the recipe, not the session: nothing reads "the data of this session".
- Where the keys are made: file hashes `dataset_file_hashes` (`app/modules/cache_keys.py:140`), batch hash `batch_hash_of` (`:151`), session key `SessionManager.compute_session_key` (`session_manager.py:373`): first 12 characters of the recipe hash and of the batch hash.
- Where a session records its data: `assembly.json` holds `source_files` = per table `{path, sha256}` (`session_manager.py:456`) and `data_batch_hash`; written by `_sync_session_provenance` (`app/handlers/home_theater.py`, at every data or recipe change). The session format number is 6 (`session_manager.py:215`).
- Stored tables are one file per table NAME, valid while the key in its footer matches (`orchestrator.py:806`, study section 9): they are not per session. After small then large then small, every switch rebuilds the table (RAN, `anchor_swap_run.py`). A store named by key would let two data sets live side by side; today's naming does not.
- A precedent exists: a bundle import keeps its own data folder per recipe id. It is the one place where "the recipe brings its data" already works (`orchestrator.py:55,169-180`).

## The options

Real numbers: her real files are tiny (`real_case/`: small set 322 + 96 bytes; large set 136,677 + 111 bytes, a pair table of 2,212 lines). The synthetic sizes of the earlier study (RAN): 1,000 isolates 22 MB; 2,000 isolates 88 MB tab-separated, the stored table 2.6 MB. Below, "10 sessions" means ten uploads of the 2,000-isolate set.

| | A. Store by content hash (user's place) | B. A copy per session | C. Named datasets per recipe with a selector | D. A snapshot of the recipe in the session too | E. Today plus the guard (built) |
|---|---|---|---|---|---|
| User does and sees | Upload keeps the file once under its hash and starts a new audit on the original recipe; Restore of an earlier audit brings its data back without any upload | Same behaviour; the session folder holds its files; Restore uses them | She names a dataset ("small", "large") at upload and picks it from a list; sessions point to a name | As A or B, and the session also holds the recipe as it was; Restore reads recipe and data from the session | Upload the same files again, then restore; or start anew; no question at upload |
| Pro | Each content kept once; two tabs can read different data; delete rule simple (no session points to it) | Easy to understand; delete a session, its data go | Matches how she thinks (a dataset has a name); a selector is visible | Everything of a session lives inside it; the audit recipe and bundle can be made from it alone | Nothing to build |
| Con | A rule to delete unused data is needed; disk grows with every upload | Same file stored again in each session (10 sessions = 880 MB against 88 MB in A) | A name can point to different content over time unless it is locked; needs a new screen | An old session keeps an old recipe: how a recipe FIX reaches it is a new decision; larger session format change | The replaced file is lost unless she kept it; still no choice at upload |
| Disk | Her real files: 137 KB per dataset; 2,000 isolates: 88 MB per distinct file | 137 KB or 88 MB per session | As A, per name | A plus the recipe file set (kilobytes) | none |
| Deletion | By hash when no session or export names it | With the session | With the name, by hand | With the session | by hand |
| Export bundle and audit log | The bundle's reproducibility part already carries the data; the log can record name, date and hash per file | Same | Same, plus the dataset name | The bundle can be made from the session alone | Unchanged; the log (D-0478) is not built |
| Stored tables | Can be shared across sessions if named by key (a change of `orchestrator.py:806`); today they are rebuilt at each switch | Same | Same | Same | Rebuilt at each switch |
| Two tabs | Each tab can read its own hash | Each tab its own session | Tabs share a selector: one choice moves the other (REASONED) | As A | Tabs share one file: an upload in one changes the other |
| `by_dataset_id` (data from a pipeline) | Uploads refused today and stay refused; a pipeline's file is recorded by hash only (nothing to copy) | Same | Not applicable | Same | Same |
| Imported bundle | Already reads its own folder; same mechanism | Same | Not applicable | The bundle IS a snapshot: precedent | Refused today |
| Build size | 3 to 5 sessions: store, per-file record in the session, Restore re-reads, the two-button choice, the live-view rule | 3 sessions | 4 sessions (new screen) | A plus 2 sessions | 0 |
| Decided lines | REOPENS D-0434; D-0439, D-0440; contract 12d key rule; D-0312 | REOPENS D-0434 | REOPENS D-0434; new naming rule | A or B plus how a recipe fix reaches a session | none |

**Re-place or read from the store (option A).** Re-placing the files at the recipe's declared paths changes what EVERY other session of that recipe reads (a global change, the problem of today). Reading from the store by hash (the orchestrator is told the hashes of the open session) changes nothing for other sessions and needs `locate_dataset_file` to take a "data of this session" argument; this is the sounder one, and it is the shape the bundle import already has. The cost: every reader of a data path (`get_source_files`, hashes, the data check) must take it.

## What an upload does to the session (added after her decision of 2026-11-28)

**Decided (relayed, not edited in the ledger).** An audit is linked to its dataset. Uploading other data creates a NEW audit that starts from the ORIGINAL recipe, never from an audit recipe. Steps are never carried to other data (the idea "carry them, marked made on other data, re-measured" is refused and is not offered below). Restoring an audit session needs ITS data: the refusal built today (G1) is the interim fix; its message names, per recorded file, the table, the original name or path, the date and the short hash.
**Not decided.** What is left of the old choice "Update this session / Start a new session" now that every audit is tied to its data. The proposal under her consideration (the review session's, not hers): at an upload of other data the audit is closed and kept, linked to the old data, and a new empty audit starts. The open point is only whether the session CONTAINER (its label, its settings) continues.

| | One container, several audits, each tied to a data batch | A new session per data batch (today's key already gives this) |
|---|---|---|
| What the panel lists | One card per recipe or per user project, with its audits inside, each with its data names, dates and short hashes; choosing an audit brings its data | One card per recipe and data batch, as today (label, batch hash, saves) |
| Pro | The label and settings survive an upload; the history of one analysis reads as one story; matches "choosing an earlier audit also brings its dataset" | Nothing to build for the container; the key already separates the batches; a card is one audit and one dataset |
| Con | A new level in the panel and in the session format (a format number change, D-0312: older sessions are refused, not converted); more to explain | The label and settings are typed again at each upload; two cards of one analysis look unrelated unless she names them |
| Build | 2 more sessions than the other | 0 for the container |
| Decided lines | contract 12d key rule (the key would no longer be the session) | none |

Either way no step reaches other data, and a Restore of an old audit uses its own data (option A or B above).

## Her mechanism (third and fourth additions, 2026-11-28, relayed) and the points still open

**Decided (relayed; the ledger is not edited here).**
1. Original recipe + an uploaded dataset = one session. Audit mode = one audit session linked to THAT dataset. A DIFFERENT dataset = start again from the ORIGINAL recipe: a new session. Steps are never carried. Restoring an audit session links to the dataset used for it (the guard now; bringing the data back by hash later).
2. THE METADATA IS DIFFERENT: it is the table declared `metadata_schema`; every other source file is data. The metadata is UPDATABLE (completed, more information) in the SAME session: the whole recipe is run again, the audit steps are applied again, the session is updated and saved. So "update this session" exists for the metadata only.
3. **The rule of "update the metadata in the same session" (DECIDED, not built; her answer of block M723).** An update whose file lacks some existing entities is ALLOWED. (a) The id verification is REDONE at every metadata upload: an id of the new metadata that does not exist in the total set of the session (the ids already existing over all original data, after the completion, compared BEFORE the update's own completion) is NOT allowed: the update is refused with a plain sentence that names those ids. (b) Entities of the existing set that the new metadata does not describe are completed with empty values, and the id warning says plainly that the metadata is NOT COMPLETE (N entities without information, which). (c) The user can upload again (another update). Her case: an earlier completion added lines for ids the user forgot; the updated metadata fills them.
**Facts of the code the rule needs.** The set of ids: `utils.id_completion` (`read_ids`, `union_of`, `build_report`: `libs/utils/src/utils/id_completion.py:254-264,363`; the union is taken from the tables as read, so "before the update's own completion" is the state of `read_ids` on the old tables plus the new file's `read_ids`). Where an uploaded file is checked: `app/modules/data_import_check.py` (`check_candidates`, `:172`; the ingestion's own read, all files or none); the id check at upload would be a new step there that reads the ids of the candidate and compares them with the union of the session. The id log and its folder: `<user_data>/_id_logs` (`app/modules/id_check_run.py:26,52`), written at every opening and carried in every export; the "NOT COMPLETE" line is a new line of `report_lines`. The metadata is already told apart in the code (`METADATA_ID = "metadata_schema"`, `id_completion.py:51`). **Size as a slice:** about 4 files (`data_import_check.py`, `id_completion.py`, the upload handler for the plain sentences, the session record for the old and new metadata hash) plus tests, 2 sessions; it needs the session key rule below decided first.
**Built today (interim, PROVISIONAL):** the Restore compares per file; a data file that differs or is missing refuses (nothing applied); when only the metadata differs the session is restored with one notice naming the old and the new metadata hash; the rule above and the explicit act are not built.

**Open points (she answers one at a time; options only).**

| Point | Options | Pro and con |
|---|---|---|
| What the audit link is | (i) the hash of the DATA files only; the metadata a layer recorded beside it (old and new hash, original names, date: a data-change event); (ii) the hash of every file, the metadata included, as today | (i) fits the rule that the metadata may change in one session; the key and the record have two parts. (ii) simpler, but every metadata update looks like new data |
| The key of the session when the metadata changes | (a) the key holds the data files only; the metadata hash is a recorded layer (the session continues under one key); (b) the key still holds every file, a metadata update gives a new key and the session is carried over to it with its history | (a) one session, one key, no carrying; changes the key rule of contract 12d and the format number (D-0312). (b) no change of the rule; a copy of history at every update, and two keys for one analysis |
| Steps that depend on a metadata column that changed or vanished | The step is applied again; a step that cannot run is SHOWN by the audit run's own error, never dropped (this is what the audit already does: it names the step and its place; to be proven by a test of the update slice); rows removed by a step are measured again on the new table | Honest; the user sees what broke. The alternative (drop the step) is refused by D-0050 |
| Ids of the old metadata missing in the new file | Allowed (decided above): completed empty, "metadata NOT COMPLETE" in the id warning | decided |
| A new id that is not among the existing ones | Refused as an update, named (decided above); it is a different dataset: a new session from the original recipe | decided |

## Recommendation

1. **Floor now (built):** E, with the live-view rule of G1 option A (a changed data file with steps in the view: no more Add until a new session, said plainly). It closes the silent mixing and costs about one session.
2. **Then A, reading from the store by hash**, built in slices so that each leaves the app working: (a) record per file name, date and hash in the session (a new field, no format change if it is only added; a session without it is refused on the batch hash alone as today); (b) at upload a new audit starts on the original recipe and the data-change event is recorded (the old audit is kept with its data); (c) the store and the orchestrator reading by hash; (d) the delete rule; (e) the audit log entry (D-0478, later). B is the same with a worse disk rule; C is a naming layer that can be added over A later; D is a separate decision about recipe fixes and should not block A.
3. **Flag first: A reopens D-0434; none of it should start until she says yes to keeping data.** What could change a result silently: re-placing files (not recommended); a name that points to other content (C); a session that keeps an old recipe (D).

## What was not checked

No browser. Disk numbers for a store are from the study's file sizes, not measured in a store. Two tabs on one user place (G8) is a separate gap. The audit log's size warnings (D-0679, D-0682) are not built and not sized here.
