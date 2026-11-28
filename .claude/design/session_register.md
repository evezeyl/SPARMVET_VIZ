# A session is a register (design, NOT built)

**Status:** DESIGN for the owner's decision of 2026-11-28 (channel blocks M721 to M726, her TOP PRIORITY: "yes we do that, we need to change how the session works; do not keep A, just do the changes. Priority."). Nothing here is built. The ledger lines for M721 to M726 are not written yet; this page cites the blocks.
**Tags:** DECIDED (her block named), PROVISIONAL (mine, she may change it), OPEN (hers to decide, section 9). **Evidence words:** READ (file:line), REASONED. Nothing was run for this page.
**Replaces in the plans:** the "carried steps" idea of D-0700, the option "E, today plus the guard" as the end state, and the key-named session of the contract section 12d. **Reopens:** D-0434 (no copy of replaced data), by her M721 point 2. **Untouched:** D-0302 (only applied steps are saved), D-0312 (older session files refused, never converted), D-0317.

## 1. Overview (ten lines)

1. A **session** is no longer a key (first 12 characters of the recipe hash and of the data hash, `session_manager.py:331-336`). It is a **register**: a file with a **stable id** that never changes, which holds the keys and **updates** them: the recipe, the versions of the main data, the versions of the metadata, the audit sessions, the history of events.
2. An **audit session** is linked to ONE data version, fixed when the audit is made. Steps are saved into the audit by its id, never into "the session of the data now on disk". So steps cannot reach other data: there is no path for it (section 4).
3. **New main data** (an upload, or a file replaced by hand): a new data version, and a new **empty** audit on the ORIGINAL recipe. The audit on the earlier data stays, linked to the earlier data. Steps are never carried (M722).
4. **Restore** of an audit uses ITS data (M721 point 2): the data is brought back from a kept copy; if the copy is not there, Restore is refused and names the data it needs.
5. **New metadata** is an update of the SAME session (M723, M724, M725): the ids are checked again, a new id is refused and named, missing entities are completed empty with a "not complete" warning, every step is applied again and shown with its rows removed, a step that cannot run is shown in red and set aside. The update never blocks.
6. What the user sees changes at three places: the Data Import dialog says what an upload starts; the session panel lists one card per register with its audits and data names; a data or metadata change is a visible event, never silent.
7. What does NOT change: stored tables are keyed by content (`cache_keys.py`); the audit copy and the trial engine; the export's key check; exploration filters (never saved, D-0327).
8. Format number 7. Older session files are refused as a whole (D-0312). No migration.
9. Cost of keeping data: disk (her real files are 137 KB per set; 2,000 isolates are 88 MB, `OPTIONS.md`), and a rule for deleting (section 5).
10. **One reading of her blocks differs from my brief's summary** (section 9, point 1): the register holds SEVERAL data versions (M726), so "new main data" adds a version and a new audit inside the register, it does not create a second register.

## 2. The register file

One file per session, `<user_data>/_sessions/<session id>/session.json` (JSON, as today's files). The audit saves are files beside it, `audits/<audit id>/<time>.json` (today's `t3_<time>.json`, one per applied step list; the snapshots stay, Restore reads the newest, `session_manager.py:565-606`). Realistic example, her demo (cgMLST recipe, a small data version, then a large one, a metadata update, two audits; hashes shortened):

```json
{
  "format": 7,                                   // the session format number (D-0312)
  "session_id": "s-20261128T100215-4f9c1a",       // STABLE: made once from the creation time and 6 random hex, never from content; also the folder name
  "revision": 9,                                  // +1 at every write; a write on a stale revision is refused (two tabs, section 4)
  "label": "cgMLST Streptococcus dysgalactiae",   // typed by the user, kept across data versions
  "recipe": {"id": "cgmlst_demo", "sha256": "ed455052e7ba...", "seen_sha256": ["ed455052e7ba..."]},
                                                  // the hash of the recipe file set now; every hash seen is kept. NO copy of the recipe (OPEN, section 9 point 3)
  "data_versions": [
    {"id": "d1", "added": "2026-11-28T10:02:15", "source": "found-on-disk", "data_hash": "775f2013ce39...",
     "files": {"hamming_distance": {"original_name": "hamming_distance.tsv", "date": "2026-11-27", "sha256": "9c1e...", "size": 322, "bytes": "store"}}},
    {"id": "d2", "added": "2026-11-28T10:41:07", "source": "upload", "data_hash": "6102f4cd751f...",
     "files": {"hamming_distance": {"original_name": "2026-11-27_Sdys_hamming_distance.tsv", "date": "2026-11-27", "sha256": "b47a...", "size": 136677, "bytes": "live"}}}
  ],
  "current_data_version": "d2",
  "metadata_versions": [
    {"id": "m1", "data_version": "d1", "added": "2026-11-28T10:02:15", "original_name": "additional_information.tsv", "sha256": "e51d...", "size": 96, "bytes": "store"},
    {"id": "m2", "data_version": "d2", "added": "2026-11-28T10:41:07", "original_name": "Sdys_additional_information.tsv", "sha256": "0a77...", "size": 111, "bytes": "store"},
    {"id": "m3", "data_version": "d2", "added": "2026-11-28T11:20:40", "original_name": "Sdys_additional_information_v2.tsv", "sha256": "d3b2...", "size": 148, "bytes": "live"}
  ],
  "current_metadata_version": "m3",
  "audits": [
    {"id": "a1", "name": "Audit 1 on d1 (2026-11-28)", "data_version": "d1", "started": "2026-11-28T10:09:00", "closed": "2026-11-28T10:41:07", "closed_by": "e4",
     "metadata_version_applied": "m1", "saves": ["audits/a1/20261128T103300.json"], "set_aside": []},
    {"id": "a2", "name": "Audit 2 on d2 (2026-11-28)", "data_version": "d2", "started": "2026-11-28T10:41:07", "closed": null, "closed_by": null,
     "metadata_version_applied": "m3", "saves": ["audits/a2/20261128T111203.json", "audits/a2/20261128T112551.json"],
     "set_aside": [{"step_id": "9be1...", "since": "e7", "reason": "the step filters the column 'host' of the metadata; the metadata version m3 has no such column"}]}
  ],
  "current_audit": "a2",
  "events": [
    {"id": "e1", "at": "2026-11-28T10:02:15", "who": null, "kind": "created", "data_version": "d1", "metadata_version": "m1"},
    {"id": "e2", "at": "2026-11-28T10:09:00", "who": null, "kind": "audit_started", "audit": "a1", "data_version": "d1"},
    {"id": "e4", "at": "2026-11-28T10:41:07", "who": null, "kind": "data_change", "from": "d1", "to": "d2", "how": "upload", "audit_closed": "a1", "audit_started": "a2"},
    {"id": "e6", "at": "2026-11-28T11:20:40", "who": null, "kind": "metadata_update", "from": "m2", "to": "m3", "old_sha256": "0a77...", "new_sha256": "d3b2...",
     "ids_refused": [], "entities_not_complete": ["SD-0417", "SD-0418"], "steps_applied": 4, "steps_set_aside": 1, "rows_removed": {"s_41ac...": [212, 207]}},
    {"id": "e8", "at": "2026-11-28T12:05:00", "who": null, "kind": "restore", "audit": "a1", "result": "refused", "reason": "its data (d1) is not on disk and its copy is missing"},
    {"id": "e9", "at": "2026-11-28T12:20:11", "who": null, "kind": "export", "audit": "a2", "bundle": "20261128_122011_demo_results.zip", "data_hash": "6102f4cd751f..."}
  ]
}
```

| Field | Meaning (one line each) | State |
|---|---|---|
| `session_id` | The identity of the session. Time plus random, **not derived from content**, so a data or metadata change never renames the session, and no recomputed key can point to it by accident. No colon in it (the old key had one, `session_manager.py:336`). | PROVISIONAL (form) |
| `revision` | Write counter. A write that read revision N is refused if the file is at N+1 (another tab wrote): the writer reads again and says so. Writes are atomic (temp file, then rename). | PROVISIONAL |
| `label` | Free text, as today (`set_session_label`, `:833`); continues across data versions. | DECIDED idea of the register, PROVISIONAL detail |
| `recipe` | `id` and the file-set hash now (`compute_data_analysis_recipe_sha256`, `:306`), plus every hash seen. The optional copy of the recipe: absent in format 7 unless she says yes (section 9). | PROVISIONAL |
| `data_versions[]` | One entry per version of the MAIN data (every table except `metadata_schema`, `METADATA_ID`, `id_completion.py:51`): version id (`d1`, `d2`, counter, never reused), when added, how it came (`found-on-disk`, `upload`, `bundle`, `pipeline`), and per table the original file name, the file date, the sha256, the size, and `bytes`: `live` (the file at the declared place is this one), `store` (a kept copy), `not-kept` (no copy: pipeline data, section 5). `data_hash` is the hash of these files only (`batch_hash_of` over the main tables), so a metadata update does not change it. | DECIDED (M726, D-0699: name, date, hash) |
| `current_data_version` | The version the open view reads; marked, updated at an upload or when the file on disk is found to differ. | DECIDED (M726 "the current one marked") |
| `metadata_versions[]` | Same, for the metadata file (`metadata_schema`). Each is linked to the data version it describes. | DECIDED (M726) |
| `audits[]` | An audit session: `data_version` (set when started, **immutable**), `metadata_version_applied` (the metadata the steps were last applied on), `saves` (the files that hold the step lists, today's `audit_pipeline` with `place`, marks and reasons, `session_manager.py:536-549`), `closed` (set when the data changes: the audit is kept, linked to its data, no more steps), `set_aside` (steps that could not run after a metadata update: red, not applied, until the user removes or fixes them, M725). | DECIDED (M722, M723, M725) |
| `events[]` | The history, append only: data change, metadata update (old and new hash, ids refused, entities not complete, steps applied and set aside, rows removed before and after per step), restore (also refused ones), export, delete of a data version, import. `who` is always null until the audit log is built (D-0677 decided, not built). | DECIDED (M726 "the events") |

**Deliberately NOT in the register:** exploration filters (never saved, D-0327), a trial and a staged step (D-0302), the shown item and the open mode (not saved today either, contract 12d), the parquet paths (always `{}` today, `home_theater.py:2035`: dead, removed), the stored tables (keyed by content, section 6).

## 3. The index

- **Where:** `<user_data>/_sessions/index.json`. **What it maps:** recipe id to its register ids; `(recipe id, data_hash)` to the registers and data versions that hold it; per register a summary for the panel (label, current data version, number of audits, last event time). It is the lookup the app uses at open ("which register did this recipe and this data belong to") and the panel's list, so the panel does not open every register.
- **It is never the truth.** The registers are. At start, and whenever a register's `revision` differs from the index's copy, the index is rebuilt by scanning `_sessions/*/session.json` (the same scan `scan_sessions` does today, `:612-657`). A lost or damaged index costs one scan, nothing else. PROVISIONAL.
- **At open of a recipe with data:** the app looks for a register of that recipe whose `current_data_version` has the data now on disk; found: continue it; not found but a register of the recipe was used last: the data on disk is a NEW data version of that register (event `data_change`, a new empty audit, a plain notice); no register: create one. Which register is "used last" per recipe is kept in the index. PROVISIONAL (section 9 point 5: several registers per recipe).
- **The panel** lists one card per register, grouped by recipe as today (`session_handlers.py:200-262`): label, the data names and dates of the current version, then its audits (name, data version names and short hash, number of saves, last save, closed or open) each with Restore and Delete; the card has Export and Delete session. A register of an older format shows as today's refused card with Delete (`session_handlers.py:208-216`).

## 4. The audit link and the rules (state table)

**Why steps cannot mix, by construction.** (1) An audit has `data_version`, written once. (2) Every write of steps takes the AUDIT ID and goes to `audits/<audit id>/`; no function takes a recipe hash and a data hash and returns a destination (today `compute_session_key(msig, dbh)` is called from seven places (`audit_session_save.py:40`, `home_theater.py:2028`, `session_handlers.py:119,384`, `export_handlers.py:673`, `bundle_importer.py:318`, `session_manager.py:478`), and that is how a changed data hash sent old steps to a new folder: RAN by the other branch, `test_steps_stay_when_data_changes_known_gap.py`). (3) Before a step is added, the open audit's data version must equal the register's `current_data_version` AND the hash of the files on disk must equal that version's `data_hash`; otherwise Add is refused with the reason. (4) When the data on disk change, the app does not move the audit: it closes it and starts a new one. (5) Restore of an audit compares ITS data version with the files on disk, the same check.

| Event | The register records | The user sees | Refused | Tag |
|---|---|---|---|---|
| Open a recipe with data, first time | New register; `d1` (`found-on-disk`), `m1`, event `created`; no audit yet | Nothing new; the session panel has a card | - | PROVISIONAL |
| Open a recipe again, same data | Nothing (no event for a plain open); `current_audit` unchanged | The card continues; the last audit is NOT restored by itself (as today) | - | PROVISIONAL |
| Upload other MAIN data (Data Import, Apply) | New data version `d2` with the original names, dates, hashes; the replaced files are kept first (section 5); `a1` closed, new empty `a2` on the original recipe; event `data_change` | Before Apply: a line says "this replaces the data of recipe X. Your audit 'Audit 1' (N steps) stays, linked to the earlier data, and can be restored. A new empty audit starts on the new data" ; after: one notice | A file that fails the check writes nothing, as today (`data_import_check.py`) | DECIDED (M722, M723); wording PROVISIONAL |
| The data file changes on disk outside the app, or in another tab | The same as the upload, after the fact (`found-on-disk` or `upload`); event says which | One notice: the data changed, the steps stay in audit A, a new audit started; Add was refused until it did | Add to audit pipeline on the closed audit | DECIDED (M721 point 1) |
| Upload a metadata update | Section 7 of the slices; new `m` version; event `metadata_update`; the SAME session and audit | The result of the update in plain words: ids refused (named), entities not complete (count, named), steps applied again with rows removed before and after, steps in red | A new id not in the session's total set: update refused, the ids named, nothing written | DECIDED (M723 to M725) |
| Switch to Audit mode | If there is no open audit on the current data version, `audit_started` (event) when the first step is added, not at the switch | As today | - | PROVISIONAL |
| Add or remove a step | A new save in the open audit; `revision` +1 | As today | Add refused when the data on disk differ from the audit's data version (check 3) | DECIDED (M721 point 1) |
| Restore audit whose data version IS the current one | Event `restore` ok | Steps in the view, as today | - | DECIDED |
| Restore audit whose data version is NOT current, copy kept | The data of that version put back on disk (explicit act, section 5), current version set to it, event `restore` | Before the act: which files will be replaced, that the current files are kept first, and that other tabs read the new files too | Cancel at the dialog leaves everything | PROVISIONAL (form: OPEN, section 9 point 2) |
| Restore audit whose data bytes are not available (`not-kept`, deleted, zip from another machine) | Event `restore`, `result: refused`, reason | An error that names the audit, its data (table, original name, date, short hash) and the way out: upload files that are identical, or start a new audit | Always: nothing applied, nothing changed | DECIDED (M721 point 2; the text is the interim guard's, `session_data_refusal`, on branch `task/guardrail-gaps`) |
| Restore a session of another recipe | Event `restore`, refused | As today (D-0317) | Yes | DECIDED |
| Export | Event `export` with the bundle name, hashes, audit and data version | The bundle also holds `session_id`, `audit_id`, data and metadata version, the events of the audit's data version (PROVISIONAL) | The export's key check as today (`export_handlers.py:278`) | PROVISIONAL |
| Delete a session | The folder; its kept data copies if no other register names them | A confirm that says what is deleted, including the data copies and their size | - | PROVISIONAL |
| Delete one data version | Its kept bytes go; the audits linked to it stay and show "data not available" | A confirm with the size; the audits that depend on it are named | The current version cannot be deleted | PROVISIONAL (OPEN: retention, section 9 point 4) |
| Change of recipe in the view | Nothing in the old register; the other recipe's register is opened or created. The set-aside of steps in memory (`home_theater.py:1834-1853`) goes: the steps are in their register | As today, minus the in-memory notice | - | PROVISIONAL |
| The recipe file of the same name was edited | `recipe.sha256` updated, old hash kept in `seen_sha256`, event `recipe_change`; the audit's steps are applied again by the machinery of the metadata update (red when they cannot run) | A notice, and the same result report | Never blocked | OPEN (section 9 point 3; today a warning only, `session_handlers.py:612-620`) |

## 5. Where the bytes of a data version live (her question; the five options are in `studies/sessions_bring_their_data/OPTIONS.md`, not redone)

**Flag first: keeping data reopens D-0434** ("which data is analysed is the user's problem, no copy"), by her M721 point 2. It touches D-0439 and D-0440 (the deployment defines how data reaches the app).

**My recommendation (five lines, REASONED from OPTIONS.md and the code):**
1. **Option A, a store by content hash**, `<user_data>/_data_store/<sha[:2]>/<sha>.<ext>`, in the user's own place (writable, D-0434), one copy per distinct file whatever the number of registers (her 2,000-isolate case: 88 MB per distinct file, not per session).
2. **Keep on replace:** a file is copied into the store at the moment an upload (or the metadata update) is about to overwrite it, not at open. So disk grows only when something is superseded, and the exact loss point of today (`data_import_check.store_all`: copy next to, then `os.replace`, no copy of the old) is closed. A version still `live` has no copy yet (`bytes: "live"`).
3. **Bringing a version back = an explicit, lossless re-place**, with the same all-or-none writer as the upload (`store_all`): the current files are kept first, then the files of the audit's version are written at the declared place. The cost I accept: it changes what every other tab of that recipe reads (the one-file-per-recipe fact that exists today, `orchestrator.py:182-219`); the dialog says so. The sounder form, reading from the store by hash with a "data of this session" argument through `locate_dataset_file` (the shape of the bundle import, `orchestrator.py:175-180`), changes every reader of a data path; I would build it only if two tabs on different data become a real need (G8). Choosing one reading rule, not both: this one.
4. **Deployment with a pipeline** (`data_lookup: by_dataset_id`, uploads refused, `data_import_check.py:55,163`): the register records the hashes and original names found, `bytes: "not-kept"`; nothing is copied (the data is the pipeline's, and could be large). An audit linked to a version that the pipeline has since replaced cannot be restored: the refusal names the files. **Imported bundle:** its data is already in its own folder (`bytes: "bundle"`); no store copy.
5. **Deletion:** a data version may be deleted by the user (section 4); a store file is deleted when no register names its hash; the panel shows the size of what a register keeps. No automatic expiry.

The register works with this form AND without the bytes (a zip from another machine, a pipeline): the guard compares hashes, and a version with no bytes refuses plainly. That is the one place the two meet.

## 6. What stays unchanged

- **Stored tables keyed by content:** `cache_keys.py` (`dataset_file_hashes :140`, `batch_hash_of :151`, `engine_fingerprint`); the cache version does not change. The old session key is not in any table key.
- The audit copy, the places, the trial engine and its folder (`audit_trial.py`: one folder per view, a token, not a session id), the audit folder `audit_anchors`.
- The export's key check and the keys it records (`export_handlers.py:278`): they compare content hashes of the view and of now.
- Exploration filters, the id completion, the id log (`<user_data>/_id_logs/<recipe id>`, `id_check_run.py:26,52`; one log per RECIPE today: OPEN, section 9 point 8).
- The panel's Delete-all, import limits and clash handling (`session_input_id_parts`, `:951`): they take the new id.

## 7. Migration: none

- `SESSION_FORMAT_VERSION` goes from 6 to 7 (`session_manager.py:215`). A folder named by the old key (`<12>:<12>`) holds `assembly.json` of format 6 or less: it is listed as today's refused card, "saved by an older version of the app and cannot be opened. Delete it and start a new session" (`session_format_problem :218`), nothing converted. The new code writes only `session.json` registers; it never writes into an old folder (the old key, containing a colon, is not a valid new id).
- **What the user must do:** delete the old sessions from the panel (each card has Delete; Delete all exists, HOM-54) and, if she wants the old audit steps, export the bundle from the old version first (the bundle carries the steps and data, ADR-097). The list of what is removed is stated before it is removed (D-0312).
- **An exported session zip of format 6:** refused at import with the same plain line (the import reads the member `assembly.json` and its format). **A bundle of an older version:** unaffected, the bundle has its own format; the import writes a new register for it (a recipe copy, one data version `bytes: "bundle"`, event `imported_from_bundle` with the four legs, no audit; today it writes an assembly record under the key, `bundle_importer.py:317-329`).

## 8. The build slices

Each leaves the app working; each removes what it replaces (no shims). Sizes in builder sessions. Tests are named; each must be shown to fail once with the code broken (rules_verification_testing.md section 9).

| # | Slice | Files | Tests that can fail | Size | Her decision first? |
|---|---|---|---|---|---|
| **S1** | **The register core and the link; closes the gap.** New pure module `app/modules/session_register.py` (create, read, atomic write with `revision`, stable id, data version and audit entries, events). The save path takes the AUDIT ID. `_sync_session_provenance` on a data change adds a version, closes the audit, starts a new empty one. Add is refused when the data differ. Restore compares the audit's data version with the files (replaces the interim `session_data_refusal`). Format 7. The key-named writers are removed (`write_assembly_ghost`, `write_t3_ghost` by key). | `session_register.py` (new), `session_manager.py`, `audit_session_save.py`, `session_handlers.py`, `home_theater.py` (sync, restore, the set-aside), `trial_handlers.py`, `audit_stack.py` | **`test_steps_cannot_mix_restore.py`** (an audit made on d1, files changed to d2: Restore refused, nothing in the view; the successor of `test_restore_on_other_data_refused.py`); **`test_steps_cannot_mix_live.py`** (steps in the view, data file changed: the next save writes NOTHING under the new data, the audit is closed and kept with its steps, a new audit is empty; the successor of `test_steps_stay_when_data_changes_known_gap.py`, which is deleted: its assertion is inverted); `test_register_has_no_content_key_destination.py` (no function maps recipe and data hashes to a session destination: a source scan); `test_register_revision.py` (stale write refused; atomic write survives a kill between files); `test_register_format7.py` (format 6 refused as a whole); `test_session_id_stable_across_changes.py` | 3 | One line: open point 1 (version inside the register or a register per data) |
| S2 | **The index and the panel.** `index.json`, rebuild, last used per recipe; the panel with registers, audits, data names; Restore and Delete per audit; label per register. | `session_register.py`/`session_index.py`, `session_handlers.py`, `session_manager.py` (scans) | `test_index_rebuilt_when_lost.py`, `test_index_never_the_truth.py` (a register edited behind the index wins), `test_panel_lists_audits_with_their_data.py` (browser, `qa`) | 2 | No |
| S3 | **Data versions with their records.** At open and at upload: original name, date, hash, size, source; events; the "found on disk" detection (D-0699). | `session_register.py`, `data_import_check.py`/`data_import_handlers.py` (the upload hands the names), `home_theater.py` | `test_upload_records_name_date_hash.py`, `test_found_on_disk_is_a_new_version.py` (a file replaced by hand), `test_upload_refused_leaves_register_unchanged` | 2 | No |
| S4 | **Keep and bring back the data.** The store, keep on replace, the explicit re-place at Restore, delete a data version, the plain refusal when bytes are missing; pipeline and bundle forms. | `data_import_check.py` (store_all), `session_register.py`, new `data_store.py`, `session_handlers.py`, `orchestrator.py` (only if she picks read-by-hash) | `test_replace_keeps_the_old_bytes.py`, `test_restore_brings_back_the_data_by_hash.py`, `test_restore_without_bytes_is_refused_and_named.py`, `test_pipeline_data_not_copied.py`, `test_delete_data_version_marks_audits.py` | 3 | **Yes: open point 2 (reopens D-0434)** |
| S5 | **Upload of other main data = new version + new audit on the original recipe,** with the informing line before Apply (section 4). | `data_import_handlers.py`, `session_register.py`, `home_theater.py` | `test_upload_starts_an_empty_audit_on_the_original_recipe.py`, `test_upload_dialog_names_the_audit_that_stays.py` (browser) | 2 | No (after S1 and S3) |
| S6 | **The metadata update (the largest).** The ids checked again against the session's total set (`id_completion.read_ids`, `union_of`, `:254-264`, compared before the update's own completion); a new id refused and named; missing entities completed empty and "not complete" in the id warning; every step applied again, rows removed re-measured before and after; steps that cannot run in red and set aside (`set_aside`), never applied, never dropped; events; the update never blocks. | `data_import_check.py`, `id_completion.py`, `id_check_run.py`, `session_register.py`, `audit_run.py`/`audit_copy.py` (the re-apply), the audit panel (red steps, remove or fix) | `test_metadata_update_refuses_a_new_id_and_names_it.py`, `test_metadata_update_completes_missing_entities_and_warns.py`, `test_metadata_update_reapplies_every_step_and_measures_rows.py`, `test_step_on_a_vanished_column_is_red_and_set_aside.py`, `test_metadata_update_never_blocks.py`, `test_data_hash_unchanged_by_a_metadata_update.py` | 3 | No (decided, M723 to M725); the wording of the messages is PROVISIONAL |
| S7 | **Export, import, bundle.** Provenance fields (`session_id`, audit, versions), the session zip (register and saves, no data bytes), session import, bundle import writes a register, `ExportFieldsStore` keyed by the session id. | `export_handlers.py`, `export_fields_store.py`, `session_manager.py` (zip), `bundle_importer.py` | `test_export_records_the_register_ids.py`, `test_session_zip_roundtrip_register.py`, `test_zip_of_format6_refused.py`, `test_bundle_import_writes_a_register.py` | 2 | No |
| S8 | **What the register replaces is removed; the records follow.** `restore_t1t2` (the app never calls it: only its definition and tests, grep), `compute_session_key` and every caller left, the interim `session_data_refusal` and `session_metadata_change`, `data_batch_hash` as a session key in `home_state`; the contract sections 7.1, 9 and 12d, `home_guardrails.md` section 6 (G1 closed), `current_limits.md` (the upload and session rows), the ADR and the UML sync (workspace_standard section 3), `@deps`. | the files named, docs | `test_no_session_key_left.py` (a scan: `compute_session_key` and `restore_t1t2` do not exist), the existing doc-link and audit scripts | 1 to 2 | No |

Order: S1, then S3 and S2 (independent), S5, then S4 (her decision), S6, S7, S8. **S1 is the one that closes the silent mixing;** S4 is the only one that waits on her.

## 9. Open points for her (fewest first; each with options and my recommendation)

1. **Does "new main data" add a version to the register, or create a new register?** Her M722/M723 say "a new session / a new audit session"; her M726 says the register holds "the main data versions" (plural, the current marked), each audit linked to one. I read it as: one register per analysis, several data versions, a new audit per version (this page). The alternative, a register per main data version, makes the label and the settings start again at each upload and puts two cards of one analysis side by side. **Recommend: version inside the register** (the label and the history read as one story). Needed before S1.
2. **Bringing data back (section 5):** (a) store by hash, explicit lossless re-place at Restore (recommended); (b) store by hash, read by hash through a session argument (sounder for two tabs, changes every reader of a data path); (c) a copy per session (simple delete, same file stored again per session: 10 sessions of 2,000 isolates = 880 MB); (d) keep nothing and refuse (E, today). **Recommend (a).** Reopens D-0434.
3. **Recipe in the session:** keep no copy (recommended: the audit recipe and the bundle already carry the recipe an audit ran on); or keep a copy of the recipe file set in the register (kilobytes; an old audit then runs on the recipe it was made on, but a recipe fix never reaches it, which is its own decision, OPTIONS option D). **And an edited recipe of the same name:** continue the register, re-apply the steps by the metadata machinery and say so (recommended, as the table), or refuse and ask for a new session.
4. **How long are data versions kept, and who deletes them?** Recommend: kept until the user deletes them (a data version, or the session), the panel shows the size; no expiry.
5. **One register per recipe, or several (projects)?** Recommend: several allowed; a button "New session" makes another register of the same recipe; at open the one used last.
6. **`who` in the events:** reserve the key now, null (recommended: no new format number later), or add it with the audit log (D-0677).
7. **Name of an audit on screen:** default "Audit 2 on d2 (the original file name of the main table, the date)", editable by the user; her word is "audit session". Recommend this.
8. **The id log (`_id_logs/<recipe id>`) per recipe or per register and data version:** per recipe overwrites at each opening and cannot say which data it concerns. Recommend per register and data version (the log is also exported).

## 10. What I did not verify

- Nothing was run; nothing was built. The interim guard (`session_data_refusal`, `session_metadata_change`) and `test_steps_stay_when_data_changes_known_gap.py` are on branch `task/guardrail-gaps` (another worktree); I read their code, not on this branch.
- The seven call sites of `compute_session_key` are a grep of `app` and `libs` (no test); a sixth in a script or a browser test was not looked for.
- Whether `_sync_session_provenance` can tell, at open, a file replaced by hand from an upload in another tab: it sees only the hash; the `how` of the event is then `found-on-disk`.
- The size of S6 (the red steps in the audit panel and the re-measure of rows) is an estimate: the audit run already names a step that cannot run, but no run of a metadata change through a whole audit was made.
- The atomicity and `revision` rule is my design; two processes on one user place (G8) are not solved by it beyond refusing a stale write.
- The interaction of the register with the tier-3 table store of an audit copy (`audit_anchors`, one file per table) when two audits of one recipe differ: unchanged by this design and not studied.
