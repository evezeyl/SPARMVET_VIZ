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
| User does and sees | Upload keeps the file once under its hash; "Update this session / Start a new session" is asked; Restore uses the session's data without any upload | Same buttons; the session folder holds its files; Restore uses them | She names a dataset ("small", "large") at upload and picks it from a list; sessions point to a name | As A or B, and the session also holds the recipe as it was; Restore reads recipe and data from the session | Upload the same files again, then restore; or start anew; no question at upload |
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

## Recommendation

1. **Floor now (built):** E, with the live-view rule of G1 option A (a changed data file with steps in the view: no more Add until a new session, said plainly). It closes the silent mixing and costs about one session.
2. **Then A, reading from the store by hash**, built in slices so that each leaves the app working: (a) record per file name, date and hash in the session (a new field, no format change if it is only added; a session without it is refused on the batch hash alone as today); (b) the two-button choice at upload and the data-change event recorded in the session; (c) the store and the orchestrator reading by hash; (d) the delete rule; (e) the audit log entry (D-0478, later). B is the same with a worse disk rule; C is a naming layer that can be added over A later; D is a separate decision about recipe fixes and should not block A.
3. **Flag first: A reopens D-0434; none of it should start until she says yes to keeping data.** What could change a result silently: re-placing files (not recommended); a name that points to other content (C); a session that keeps an old recipe (D).

## What was not checked

No browser. Disk numbers for a store are from the study's file sizes, not measured in a store. Two tabs on one user place (G8) is a separate gap. The audit log's size warnings (D-0679, D-0682) are not built and not sized here.
