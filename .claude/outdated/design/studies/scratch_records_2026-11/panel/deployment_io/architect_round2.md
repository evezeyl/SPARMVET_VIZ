# Architect, round 2 (2026-11-21)

Read: the three other first-round texts in full. Checked again in code: `orchestrator.py` (`locate_dataset_file`, `_declared_path`, `file_place`), `bootloader.py:121` (default `data_lookup`), `export_handlers.py:1496-1560`, `session_manager.py:380-392`, the ledger line D-0340, the shipped recipes. I recommend; the owner decides.

New fact that changes point 5: `data_lookup` has two modes. `by_dataset_id` (production) ignores a recipe's `source.path` (`orchestrator.py` docstring, V). `data_analysis_recipe_paths` (the DEFAULT, `bootloader.py:121`, V) reads it as written. Only `pipeline_test.yaml` sets `by_dataset_id` (grep over `config/deployment`). 14 shipped recipes name `./assets/test_data/...` (grep).

## 1. The same name in two places
Position: ONE rule. Refuse, name both places, no search order, with one exception taken from the data scientist: if the bytes are identical (same file-set hash, ADR-089), it is one object, both places are shown, nothing is refused. I change my mind on that exception only: nothing changes silently when the bytes are equal.

Why I do not support "show both and the user picks" or "the deployment file says which wins":
- ADR-092 makes the recipe id the stem and unique. A pick by the user makes the identity a pair (place, id) in the session key, the cache, the export and 13 recipe-path sites. That is a decision that reconsiders ADR-092; nobody has asked for it.
- "The deployment file says which wins" is a search order with a label. It is shown, but the user did not choose and the same name means different files on two servers. A methods sentence "recipe X" is then ambiguous.
- The developer writes: "the order of the `places` list decides the search; the same recipe name in two places is refused by default". "By default" implies a setting where order picks. I would not offer that setting.

The owner's case: a consortium `amr_2026-11-17` copied into the own place and changed.
- Made inside the app: the save checks the name against ALL readable places, not only the target. A name that exists anywhere is refused with the next free name proposed (`name_date`, D-0390). So the collision cannot be created by the app.
- Made by hand (a file copied with the same name) or a place added later: the user sees "Not available: `amr_2026-11-17` exists in 'Consortium recipes' and in 'My recipes' with different content. Rename the file in 'My recipes'." Both rows stay listed, neither opens.
- The cost, to tell her: a normal user must rename a file by hand, or the app must offer "rename my copy" (a write in a `replace` place; MINE, to confirm). The app does not delete (D-0390).

## 2. Nothing writable
- (a) Stop at start with a plain message. Cost: no static page on a fully read-only host. Risk: none for results. Simple. Honest.
- (b) Keep tables and session in memory or system temp, say "nothing is saved". Memory: an engine change (the plot readers read stored parquet; the audit copy in memory exists, the tiers do not). Not built; I would not build it for a case not shown. System temp chosen by the app: a write outside every declared place (breaks L12), shared by all users of the process, and it can fail too (read-only `/tmp`).
- (c) The deployment file chooses. Risk: a second mode to test.

I support (a) and (c) as ONE rule, without new engine code: the app needs a writable `cache`. The deployer declares it as a `folder`, a `job_dir`, or `provider: temp` (the app makes a folder under the system temp for the life of the process and removes it at exit). With nothing declared, the app stops at start naming the missing `cache`. "This session only" on screen = `provider: temp`. I change my mind a little: in round 1 I said "tmpfs declared as cache"; `provider: temp` is the same thing declared in the file, with the screen words attached. No `user_data` declared: no session record, no audit, no Data Import control (the controls are absent). Today the record is written at every opening with no flag (`home_theater.py:1515-1578`); that needs a small flag in the app features, not a memory engine. Tell her: sessions and audit are lost on a temp or absent `user_data`; the user must export (browser download) to keep anything.

## 3. The access words
Smallest set in the file:
- `access: read | add | replace` per place. No default: a missing `access` is a start error (developer is right: "an unspecified access must be an error").
- `provider: folder | job_dir | temp` (`irida`, `url` later).
- ONE deployment-level key for the question the app cannot answer itself: `process_users: one | several` (MINE; no default). Without a login the app cannot tell whether "mine" is true.
Mapping to the screen words (the user's three):
| File | Screen |
|---|---|
| `read` | "Shared (you cannot change these)" |
| `add` | "Shared (you can add files; existing ones stay)" |
| `replace`, `process_users: one` | "Mine" |
| `replace`, `process_users: several` | "Saved in this app (everyone who uses it sees them)" never "Mine" |
| `provider: temp` | "This session only" |
Not in the file: `private`, `may_export_data` (point 4). The deployer's label stays free text; the app adds the access words, so a label cannot claim "locked" falsely.

## 4. Private data
Position: not needed now. Not changed by reading the scientist.
- Stored tables: they go in `cache` and are keyed by content. Sessions and audit go in `user_data`. Both are per process. With `process_users: one` they are the user's. With `several` the screen says "everyone sees these" and the deployment info says: no sensitive data here. A `private` flag could not verify more than this: the app cannot see whether a folder is shared with another process.
- Data Import and bundle import write only into a place with `add` or `replace` of that role. In the owner's case the consortium places are `read`, so sensitive metadata can only land in "Mine". This is the whole protection and it follows from `access`.
- Export: what exists today is a user tick-box plus a warning (`export_handlers.py:1512, 1544`: "includes your actual raw data"); the code comment says "Sensitive-data handling is #46, not built". The least safe change now: the warning lists each data file with its place label. A per-place `export_data: never` is a DEPLOYER restriction (the consortium may forbid redistribution), a different thing from `private`; it belongs to task #46, built when #46 is. A reserved key with no code is the dead key ADR-091 point 6 deletes.
- Session stores the server path (`session_manager.py:386-389`, V): replace it with place id plus relative path plus hash (the scientist's finding; I agree).
What a test would not catch: a cache folder that two processes share.

## 5. Confinement
Position: no. Reads and writes only inside declared places, in both lookup modes. It is already true in `by_dataset_id`. It is false in the default `data_analysis_recipe_paths`: `Path(source["path"])` is read and also WRITTEN by Data Import (`file_place`, `_declared_path`).
- The shipped recipes are not rewritten. The development deployments (`local`, `retest`) declare `assets/test_data/` as a data place (`read`, or `replace` where Data Import is tested). A `source.path` is accepted if its resolved real path (symlinks and `..` resolved; relative paths against the code root, not the working folder) lies inside a declared data place; otherwise the check refuses it and names the place list. Absolute paths into a home folder in a recipe are refused: a recipe that reads outside the declared places cannot be shared.
- `data_lookup`'s meaning changes (a path must lie in a place). No ledger line decides it. Name it to her.

## 6. Migration
Position: yes, one order satisfies both. The owner's "no shim" is about reading two FILE formats. A change of the internal API, done before the file format changes, is not that, provided it is one-way and deleted.
1. Fixes that every design needs, no new concept: sorted discovery and default; the pure `name_date` module (D-0390, D-0391); ONE recipe-path function for the 13 rebuild sites; fail-fast at start for `user_data` and `cache` (created at start, not per browser session: F1); BLUEPRINT's folder from the deployment.
2. A `Places` object in `libs/connector/` (pure, no Shiny): roles, ids, access, provider, validation, the real-write probe for the app's own places, tests with `tmp_path`. Its first consumer is switched in the same merge (the `SessionManager` line), so there is no dead code. For these few merges ONE parser function builds the object from the five keys. It is the only code that knows the file format; it is replaced at step 4, not extended.
3. Switch consumers class by class (user, then data, then recipes) from the string `get_location` to the object. Each merge leaves a working app. The last one adds the architecture test: no string-key `get_location` outside the parser.
4. The one flag day: the `places` block, the migration script for the seven files, the old keys refused with a message naming the new one (ADR-091 point 2), docs, tests. Only here does the file change.
What to tell her: the parser at steps 2 and 3 is an adapter that lives for several merges. If she rules it a shim, steps 2 to 4 become one large merge. This is the one point where "no half fixes" and "each step works" pull apart; she decides.

## 7. API and connectors
Yes, it covers both cases.
- "Data passed directly from the pipeline": a `job_dir` or `folder` place with `read`. No API needed; it exists in the Galaxy connector.
- "API gives data and recipe": a provider (in `libs/connector/`, not in the handlers) writes the files into a local place before the app reads them. Opt-in per deployment, never a default (ADR-071 rule 1, qualified).
A point I had not stated: the provider WRITES into a place the app calls `read`. So there are two writers: the app's write functions and the provider. The provider is the one named exception to the write rule, listed in the architecture test.
Recorded per file (scientist's list, which I adopt): source id (host, project or dataset id), the provider's version string if it gives one, fetched_at, the content hash, the place id, and the relative path. The fetched bytes STAY in the local place so the hash can be re-checked (a hash of bytes that are gone proves nothing). Never recorded: the token, the absolute server path. A recipe pulled from an API is identified by its `name_date` and hash. A pull that fails stops the start (`required`), naming the source.
Not caught by any test: the provider's version string is only as good as the source.

## 8. D-0340
"The audit folder still has no setting of its own and stays inside the session folder of the `user_data` place, so D-0340 is respected; what the design changes is that 'the existing location' becomes a named place in a new `places` block, which Eve confirms or refuses." (The line also says "no new configuration variable for now". The places block is new configuration for another decision. If she reads D-0340 as forbidding any new block, the design reconsiders it.)

## 9. Wrong, or would change a result silently
- Developer: "The registry must probe by really writing a file and removing it, not by `os.access`." Right for root in a container, which I had flagged as a limit. I concede it for `user_data` and `cache` (the app's own places). I do not do it for a recipes or data place with `add`: the probe would drop a file into a folder that another person or a sync tool maintains. There the first real write reports plainly, and the start notes "not probed".
- Developer: `provider: {type: folder, path: "{user_dir}"}`. This is a second expansion syntax beside `~` and `${VAR}` (ADR-091 point 4, built in `path_expansion.py`). Use `${HOME}` or `${USER}`.
- User: "A name in two places ... Choose which one you want; the app does not pick one." Sound as a sentence. It needs the identity pair of point 1.
- User: "Data Import overwrite: Replace / Keep both / Cancel." A recipe reads a table by its fixed id. A "kept" second copy under another name is never read by the recipe. "Keep both" has no name rule and does nothing useful. The honest options are replace (with the count of sessions that stop matching), replace after moving the old file with its hash, or refuse.
- User: "Nothing you do here is saved on the server." False today (the session record and stored tables are written at every opening). The sentence must not ship before the behaviour (points 2).
- Scientist: "Stored tables ... Nothing writable: compute in memory and say so." Not built; it presumes an engine that holds tiers in memory. See point 2.
- Scientist: "recipe never holds a place path". Today's default mode lets it (point 5). True after confinement, not before.
- Scientist (I withdraw my own item): the Gallery index write is already skipped when the folder is not writable (`gallery_listing.py:52`, status `not_writable`, tests exist). My "write into a place declared read" is only a documentation matter.

## Still open between us
1. Point 1: whether "the user picks between two" is wanted by the owner at all. It reconsiders ADR-092. It is her decision, and the user viewpoint and I do not agree.
2. Point 4: private flag now (scientist, developer) or after #46 (me).
3. Point 2: `provider: temp` accepted, or stop at start for every deployment without a declared writable `cache`.
4. Point 6: is the temporary one-way parser a shim.
5. `process_users` key: one more deployer statement the app cannot verify. Is the screen wording worth the key?
6. Data Import overwrite and bundle import name: still the owner's.
7. Recipe collision made by hand: the app offers "rename my copy" (a write) or tells the user to do it outside.
8. Not verified by anyone: containers, a read-only mount, two users, Galaxy and Connect identity, whether the export re-hashes the data at export.
