# Session import: builder report (branch task/session-import, commit 3d8f552e)

## Measurement (PART 0), headless, real SessionManager, real recipe hash and real source-file hashes
Built headless (not through the browser): the session folder holds only what `write_assembly_ghost` and `write_t3_ghost` write, so the files are the same as the app's. Script: worktree `tmpAI/measure/measure.py`. Two audited filters with a reason per save. Scratch folder only; nothing was left in the user data folder.

| session | audit saves | zip bytes | unpacked bytes | files | largest file |
|---|---|---|---|---|---|
| 1_test_data_ST22_dummy | 1 | 1942 | 5005 | 2 | assembly.json 2884 |
| 1_test_data_ST22_dummy | 10 | 9430 | 24094 | 11 | assembly.json 2884 |
| 3_test_no_joins (smallest) | 1 | 1401 | 2804 | 2 | t3_*.json 2114 |

What the size depends on: only small JSON text files. No tables, no parquet (assembly.json holds paths and hashes of the source files, the parquet paths as text). It grows with the number of audit saves (about 0.85 KB zipped per save, one t3 file each; also with the number of audit steps and the notification log in each save), and slightly with the number of datasets in the recipe. It does NOT grow with the data. (My script counted 12 source entries for the demo recipe because it matched every `path:` line, including repeated ones; this adds about 1 KB to assembly.json at most.)

Default taken (PROVISIONAL): zip 1 MB, unpacked 10 MB. Reason: the literal "3 times the measured session" is about 6 KB, and a session with only 10 audit saves already zips to 9.4 KB and would be refused. So I rounded up to a round number far above 3x, still about 500 times a normal session and about 100 times a ten-save one. This departs from the literal "3x": Eve fixes the numbers (D-0283 says so).

## Commits
3d8f552e feat(sessions): ask before an imported session replaces one, check member names, limit the zip size

## Files
app/modules/session_manager.py (import_session_zip, limits, name check), app/handlers/session_handlers.py (the question), app/src/bootloader.py (`get_session_import_limits`, validated at start), config/deployment/templates/deployment_template.yaml and docs/deployment/deployment_guide.qmd (the key), app/tests/test_session_import_safety.py (33 tests). `@deps` updated in the three Python files.

## What the user sees (exact texts)
- Key exists (modal "This session already exists"): "A session with this key already exists. Replace it, keep both, or cancel?" then "Key: <key>" then "Replace: the stored session is replaced by the imported one. Keep both: the imported one is stored next to it and listed as imported. Cancel: nothing is written." Buttons: Cancel, Keep both, Replace. The zip waits in memory only; nothing is written before the choice. Cancel leaves the store byte-identical (tested).
- Replace: "Session imported: <key> (replaced the stored session)". Keep both: "Session imported: <key>~imported-<time> (stored next to the existing one, listed as imported)"; its label reads "Imported <time> UTC (copy of <key>)" plus the old label.
- Bad member: "Import failed: The zip was refused and nothing was written: the member '<name>' is <an absolute path or a drive | a path that goes up with .. | a link or a special file | a path outside the session folder <key> | ...>. A session zip holds only plain files inside one session folder." Names the first bad member.
- File too big: "The file is <size> and the limit for an imported session zip is <limit>. The limit is set by session_import.max_zip_mb and session_import.max_unpacked_mb in the deployment file <path> (a key that is absent uses its default)." (with no key in the file: "... set by the default, because ... are not in the deployment file <path>; set them there to change the limit").
- Unpacked too big: "The zip is <size> but would unpack to <size> and the limit for the unpacked size is <limit>. The limit is set by ...".
- A waiting-zip click with nothing waiting: "No imported zip is waiting; nothing was written. Suggestion: upload the zip again."

## Deployment keys (PROVISIONAL names and unit)
`session_import.max_zip_mb`, `session_import.max_unpacked_mb` (megabytes, number above 0, decimals allowed). Absent key: default 1 and 10 (constants `DEFAULT_SESSION_IMPORT_MAX_ZIP_MB`, `..._UNPACKED_MB`). A wrong value or an unknown key under `session_import` stops the app at start with a deployment error naming the key (D-0050). Used by the import handler; documented in the template and the deployment guide.

## Keep both (built, PROVISIONAL)
Stored in `_sessions/<key>~imported-<YYYYMMDDTHHMMSS...>/`. Its assembly.json and t3 files get the new `session_key` (the list, Restore and Delete find a session by the key inside assembly.json), plus `imported_at` and `imported_from_key`. List shows both; deleting the copy leaves the first (tested). Restore of a copy loads its saves; it can never be the "active" session, because the active key is computed from recipe and data (the original key). Changes to the files of the imported copy: only those fields, in the copy.

## Other behaviour added (follow from "member names checked")
All members must sit under ONE top folder (the key); a key folder name starting with "." is refused; the unpack is staged in `.import_<id>` then renamed; replace moves the old folder away first and puts it back if the rename fails; a failed import removes its staging folder.

## Tests
New: app/tests/test_session_import_safety.py 33 passed. Existing green together: test_session_manager, test_import_errors_visible, test_session_errors_visible, test_legacy_formats, test_audit_step_refused_not_skipped, test_removed_audit_step_type, test_shipped_deployments, test_session_clicks_once, test_bundle_importer (181 + 33), and the browser test test_shiny_session_restore.py (qa) 1 passed. One real failure found and fixed on the way: my drive check refused the key "a:b" of an older test; the check now needs a slash after the letter and colon.
Break-once (each run failed, then restored): M1 no key check (3 failed); M2 `..` not refused (2); M3 link not refused (1); M4 unpacked size not checked (1); M5 zip size not checked (2); M6 limit not read from the file (7); M7 handler imports at once (2); M8 cancel does not stop (1).
Crafted zips contain names only, written under pytest tmp folders; the tests assert nothing appears outside.

## Decisions table
| decision | how | where | test |
|---|---|---|---|
| D-0281 "the app never overwrites silently" | key exists raises SessionKeyExists, asks | session_manager.py import_session_zip; session_handlers.py `_finish_import` | test_a_zip_whose_key_exists_writes_nothing_before_the_choice, test_the_screen_asks_when_the_key_exists_and_writes_nothing, cancel/replace/keep tests |
| D-0281 member names | `_checked_member_names` before any write | session_manager.py | test_a_crafted_member_name_..., test_a_link_member_... |
| D-0283 limit from deployment, default, used and documented, both sizes, plain refusal | `session_import_limits_from`, `get_session_import_limits`, template, guide | session_manager.py, bootloader.py | limit and default tests, unpacked-bomb test |
| D-0050 no silent error | bad value stops start; every refusal is a visible error | bootloader.py `_validate_deployment` | test_a_wrong_value_or_unknown_key_is_refused_naming_the_key |
| D-0101 short plain sentences | texts above | | |
| D-0165 | questions below | | |

## Questions for Eve (D-0165)
1. The numbers: default 1 MB zip and 10 MB unpacked (see measurement; literal 3x would be about 6 KB and refuse a session with 10 saves). Keep, or other numbers? Names and unit of the keys also PROVISIONAL.
2. Keep both: the stored name `<key>~imported-<time>` and the label wording are my choice (PROVISIONAL). OK, or another rule?
3. Not decided and not built: a limit on the number of members in a zip (a zip of thousands of tiny files is under both size limits). Add one?
4. Not touched (outside my files): the "Export Active Session (.zip)" does not check size; the bundle import (`bundle_importer.py`, ADR-097) is another path with its own zip reading and has no member-name check or size limit; it is outside this task. Report only.
