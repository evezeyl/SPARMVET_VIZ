# The audit folder inside a session: `audit/` or a hidden `.audit/`. Facts for the owner's choice (scout, 2026-11-21; filed by the coordinator)

READ = read at file:line. REASONED = a conclusion; nothing was run. The file meant is `app/modules/session_manager.py` unless another is named.

## In short
For the app as built today, the two names behave the same. The difference is only what the user sees in a file browser.

| Question | `audit/` | `.audit/` | Evidence |
|---|---|---|---|
| Goes into the session zip ("Export Active Session") | yes | yes (REASONED: the code collects every file with `rglob("*")`, which matches names that start with a dot) | :647-656 |
| Accepted when a session zip is imported | yes | yes: a name starting with a dot is refused only for the TOP folder of the zip, not for a folder inside it | :966-1015, :999 |
| Changes the list of sessions | no | no | :611 |
| Removed when the session is deleted | yes | yes (the whole session folder is removed) | :774-778 |
| Read or written by any code today | no | no | grep; `app/modules/audit_run.py:208` writes only a scratch folder |
| Seen by the user in a file browser | yes | usually not (hidden on Linux and macOS; on Windows a leading dot does not hide a folder) | REASONED |

## Other facts
- A session folder is `<user place>/_sessions/<session key>/` (:270-274, :314-318). It holds `assembly.json` and `t3_<time>.json` today, nothing else.
- The session key contains a colon (:306-308). A colon is not allowed in a folder name on Windows. Not part of this choice; noted because the audit folder sits inside that folder.
- The import parses as a session file any file whose name ends with `assembly.json`, or that sits under a path containing `/t3_` and ends with `.json`, at any depth (:695-696, :700-726). An audit file must not be named like that.
- The import limits are 1 MB for the zip and 10 MB unpacked (:850-851). An audit folder that stores tables (`audit_run.py:256-258` writes one Parquet file per table into the folder it is given) could pass these limits. Whether stored tables belong inside the audit folder is not decided here.
- No count limit on the files of an imported zip was found.

## Records
- D-0319: "I think audit/ good" (DECIDED). D-0422 (2026-11-21): the name is reopened by her and not decided. D-0340: the audit folder is inside the session folder.

## Not verified
The behaviour of `rglob` with dot names was not run. `bundle_importer.py` and the copy helpers were not read in full. Windows was not tried.
