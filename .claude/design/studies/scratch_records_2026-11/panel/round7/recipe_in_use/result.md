# A recipe or data changed while someone works on it (Eve's question, 2026-11-15, M102)

Investigation, no build, no repository file edited. HEAD `dd6a9d2f`. RUN = I ran it (scripts in this folder); READ = I read it at file:line. Words used once: the **view** is what HOME has on screen (tables and plots); a **key** is a fingerprint of the recipe files plus the data files (`app/modules/cache_keys.py`); the **gate** is the check HOME runs on a recipe (ADR-094).

## 0. Short answers

1. Today the app notices a change of the recipe file within 2 seconds (READ `recipe_gate_handlers.py:25,138`). It shows a sentence only when the changed recipe now FAILS its checks. For a valid change HOME shows nothing (RUN `a_valid_change.py`: gate version 0 to 1, recipe still available, notes under the selector are an empty box).
2. Data files are not watched by any timer (READ: only `recipe_gate_handlers` polls, and it reads recipe files only). The app notices a changed data file at one of three moments: at the export (always), at the next change of HOME's state (a warning toast that says "re-assembling", which is untrue, see B), or at once only in the session that did the import.
3. The export check is solid. Everything that is not the export is half-informed: after a valid recipe change HOME shows the NEW layout on OLD stored tables, with no sign, until F5 or the export.
4. Two sessions can crash the app: a stored table file is rewritten in place while another session reads it. RUN: the reader process was killed by the operating system in 3 of 3 runs; with write-to-a-temporary-file-then-rename it was 0 of 1.
5. Nothing is built for S2-3 (re-base): no code, package P10 "NOT BUILT" (`home_stage2_mechanism_spec.md:153`; grep for re-base in `app/` and `libs/` finds nothing).

## A. The recipe: what the app detects today

### A1. The pieces (READ unless marked)
- **Trigger.** Each HOME session runs a poll every 2 s (`recipe_gate_handlers.py:138-139`). Each poll calls `Bootloader.recheck_changed_data_analysis_recipes` (`bootloader.py:456`). It compares the content digest (sha256) of every file of every recipe (the recipe, every `!include`, the mirrored folder) with the digest taken at the last check (`cache_keys.py:115`). Nothing changed: 3 ms, no check runs (RUN `a_gate_time.py`). Changed: the gate runs again on that recipe alone, 0.08 to 0.17 s on the shipped recipes (RUN), and the gate version goes up by 1.
- **Same trigger from Blueprint.** After each save Blueprint calls the same function at once (`blueprint_handlers.py:1279`, also :1609 branch, :2748). The save is never blocked. Blueprint speaks only if the recipe now fails or is repaired (`blueprint_handlers.py:260-275`); for a valid save it says only "Saved to <file>" and nothing about HOME.
- **What Blueprint saves.** The one component file it has loaded (`blueprint_handlers.py:1240-1273`), usually an included fragment, in place with `open(path, "w")`: not atomic, and it never compares the disk with what it loaded (no sha check in that handler; the sha check at :159 is for the autosave draft only).
- **What the user sees.** Only when the gate DROPS the open recipe: the lasting red sentence under the selector "'X' was open and no longer passes its checks: HOME shows 'Y' instead." (`recipe_gate_handlers.py:83`, drawn by `gate_notes`), plus one warning toast and one entry in the Alerts log (`:172`). A recipe that still passes: nothing.
- **Keys of a view.** `data_analysis_recipe_sha256` = hash of the file set (bytes, so a comment-only edit changes it); `data_batch_hash` = hash of the content of every data file; `tier1_key` = hash(engine version, resolved recipe without the plot parts, data hash); `tier2_key` = hash(tier1_key, the table's tier-2 steps) (`cache_keys.py:93-129,160`). HOME computes the keys once (`home_theater.py:246-256`) and recomputes them only when a data import happens (`data_refresh_trigger`, set only at `data_import_handlers.py:365`) or the recipe selector changes. They do NOT depend on the gate version.
- **Export check (DECIDED: Eve 2026-11-06, issue #25; ledger L05; ADR-089 note).** At the export the keys are computed again from the disk and compared with the view's keys (`export_handlers.py:816-833`, `changed_since_view` :205). A difference: no export; a lasting red message (duration None) and an `EXPORT_NOT_CREATED.txt` in the zip with the two sets of keys. It names what changed: the recipe, the data files, or the processing rules.
- **Audit steps.** In memory in HOME's state, saved as "ghost" files by Apply (`audit_stack.py:948-963`). The session folder name is `recipe hash[:12] : data hash[:12]` (`session_manager.py:219`). The recipe hash held by HOME is refreshed within about 2 s of a recipe change (`home_theater.py:1195-1236`, an effect that reads `active_cfg`). So steps made on the OLD recipe are saved at the next Apply under the NEW recipe's session key, with no sign (READ; not run: needs a live session). Restoring a saved session does warn "saved against a different recipe version" (`session_handlers.py:~345-358`).
- **S2-3 (DECIDED, Eve 2026-11-15, ledger N33):** export refused until re-base; re-base marks each step applied / not concerned / broken; a broken step blocks. Built: the refusal on a changed recipe exists (the export check above); re-base does NOT exist; the audit copy it relies on is not built (P5 to P10 NOT BUILT).

### A2. Timeline, situation 1: Blueprint saves a valid change to a recipe HOME has open
| Time | Disk / Blueprint | HOME session (view opened earlier) | What the user sees |
|---|---|---|---|
| 0 s | file written; Blueprint re-runs the gate (0.1 to 0.2 s); gate version +1 | nothing yet | "Saved to <file>" in Blueprint only |
| 2 s at most | - | poll sees the new version; `active_cfg` reloads: plots, labels, step lists come from the NEW recipe (`server.py:88-89`). Keys stay OLD. Session record takes the new recipe hash. | nothing |
| next click | - | tables: a stored Tier 1 whose key equals the OLD key is reused, so OLD table under the NEW layout (RUN case B: view and re-read show s1,s2,s3; a new session shows s3). A Tier-2-only change shows the NEW rows (RUN case A). | nothing |
| a table not stored yet | - | built from the NEW recipe and stored with the OLD key (RUN case C). If the author then reverts the recipe, the old key matches again and the wrong stored table is served as right (RUN case C: s3 served, correct is s1,s2,s3). | nothing, and this is a wrong table served with a valid key |
| export | - | keys recomputed, differ | export refused, lasting message, `EXPORT_NOT_CREATED.txt` (RUN case E: even a comment-only edit is refused) |
| F5 | - | new session, new keys | everything from the new recipe; audit steps in memory are lost; the saved ones sit under the old key |

Unchecked, needs a browser: if the user goes to Blueprint and back in the same tab, the recipe selector is rebuilt (`recipe_gate_handlers.py:59-68`); whether that recomputes HOME's keys (and so removes the old-table-under-new-layout state in that tab) is not known. Ask the browser agent: save a valid tier-1 change in Blueprint, go back to HOME, do not press F5, read a table, export.

### A3. Timeline, situation 2: the file is changed outside the app (editor, pipeline, sync tool)
Same as A2 without the first row: the poll finds it within 2 s (also when no one clicks; the poll runs while the session is open). Blueprint is not told. Added risks (READ; not run): an editor or sync client that writes in two steps can be read half-written, the gate rejects the recipe for one poll, HOME switches to another recipe with the lasting sentence and comes back when the file is whole (`follow_step`, `recipe_gate_handlers.py:44`); a Blueprint session that loaded the file earlier saves over the outside change without any warning (lost update, `blueprint_handlers.py:1272`). A recipe file ADDED or REMOVED on disk: an added one needs a restart (ADR-094; `bootloader.py:370-377`); a removed one leaves the list (test `test_gate_gap.py:179`).

## B. Data files

| What happens | Who notices | When | What the user sees |
|---|---|---|---|
| A data file is replaced on disk while HOME shows it | nobody on a timer | - | nothing |
| the same, at the next change of HOME's state (opening another plot tab, applying a step) | `_sync_session_provenance` hashes all data files and compares (`home_theater.py:1195-1224`; it reads the state without isolating it, so it re-runs on every state change and re-reads every data file each time) | the next such change | a warning toast "Source data files for this project have changed - re-assembling." (8 s; Alerts log). Nothing re-assembles: the keys do not move (RUN case D: re-read gives the old rows). The sentence is wrong. |
| export | key check | at the click | refused, "the data files" (RUN case D) |
| the Data Import panel (the metadata upload or a multi-file upload) in THIS session | the import itself | at once | the panel checks the file against the contract first, copies it over the data file (`data_import_handlers.py:336`, plain copy, not atomic), deletes `anchors/<id>.parquet`, raises `data_refresh_trigger` (:346, :365): this session's keys are recomputed, "plots are refreshing now" |
| the same import, seen from ANOTHER session of the same app | nobody | - | nothing until its export; `data_refresh_trigger` is per session (`server.py:123`) |

Two more findings (READ): (1) the import writes to the recipe's `source.path` when it has one (`:325-336`); on the shipped recipes that is a file under `assets/test_data/`, git-tracked, shared by every user of the deployment. (2) `_sync_session_provenance` ends with `except Exception: pass` around the session-file write: a failed write is invisible, against "no silent error" (ADR-104).

## C. Several sessions and several processes

What is shared (READ):
- the recipe files and the data files (disk);
- inside one process: the Bootloader singleton with its gate state (`bootloader.py:188`), the loaded-recipe memory cache (`cache_keys.py:168`, guarded by a lock), and `data_analysis_recipe_gate_version`. One poll that sees a change updates every session of that process within 2 s;
- on disk, under the user data location of the deployment (one folder for all users: `config/deployment/*/*.yaml`, key `user_data`; `local` uses `tmp/UI_TEST/user/`): `anchors/<table name>.parquet` (Tier 1) and `<table name>__T2.parquet` (Tier 2), `_sessions/<recipe hash : data hash>/`, `_blueprint_drafts/`.

Nothing records which session or process has a recipe open: the Bootloader keeps no session list and the app never uses `session.on_ended` (grep: no hit in `app/`). Two PROCESSES share no memory; they notice each other's saves only through the file digests, within 2 s.

Can two sessions open the same recipe? Yes, nothing prevents it, in one process or two. When one saves in Blueprint, the other follows as in A2.

Writes by two at once, none protected (READ unless marked):
1. **Stored tables**: `write_anchor` calls `write_parquet` straight to the final file (`libs/transformer/src/transformer/anchor.py:37`), no temporary file, no lock. The file is named by table, not by recipe, so two sessions on different keys (an old view and a new one) or two recipes with the same table name rebuild over each other. RUN `c_concurrent_anchor.py`: one process rewriting, one reading (key read, then scan): the reader was killed by the operating system (exit code -7, SIGBUS) in 3 of 3 runs, the Polars error messages "range end index ... out of range" show before. In the app one process serves every session, so that is every user disconnected. With `write to .tmp, then os.replace` (RUN `c_concurrent_anchor_atomic.py`): 1355 good reads, 0 failures. The planned fix is in the records and not built: `home_audit_steps.md:531` row 10 "write to a temporary file and rename ... to build".
2. **Session files**: `assembly.json` (`session_manager.py:279`, rewritten at every state change, label read then rewritten) and the label file (:591) with `write_text`, not atomic, last writer wins. The session folder name does not contain a user: two users with the same recipe and data share the folder and its audit ghosts (`list_t3_ghosts`, restore takes the latest).
3. **The recipe file**: Blueprint's save (`:1272`), the branch write of several files (`:1599-1601`, it removes the fragments it made if a write fails; the master is not restored), an outside editor. Last writer wins, nobody is told.
4. **Data files**: the import (`data_import_handlers.py:336`).
5. The Blueprint draft uses write-then-rename (`blueprint_handlers.py:144-145`), but a fixed temporary name per recipe: two Blueprint sessions on the same recipe can collide on the temporary file (reasoned, rare).

## D. A lock: how, what it costs, what goes wrong

| Way | How here | Costs | What goes wrong |
|---|---|---|---|
| lock in memory, one process | a dictionary in the Bootloader: recipe name to the sessions that have it open; removed when the session ends | small; new state; needs `session.on_ended`, not used today | blind to a second process (a deployment may run several) and to every outside editor; a session that dies without cleanup leaves a lock until restart |
| lock file beside the recipe (a `.lock` flag file) | create the file when HOME or Blueprint opens, delete at close | small code, but a new file in the recipe folder (and in the recipe's mirrored folder watched by `_recipe_files`, `bootloader.py:429`) | RUN `d_locks.py`: after `kill -9` the flag file stays on disk, the lock is stale and someone must clear it (the app would need to know whose it is and whether that process lives). A synchronised folder (the repository lives in one: `Insync/gdrive`) uploads the flag to the other machines as a real lock. |
| operating-system lock (`flock`) on the file | lock held while open | 10 lines | RUN: works here (btrfs, local) and is released by itself when the process is killed (no stale lock). It is advisory: an editor, Excel, a pipeline or a sync tool ignores it. It does not work across machines or reliably on a network or synchronised folder (not tested here: no such mount; known limit, external). |
| a recipe made of many included files | one lock for the recipe is not enough: Blueprint saves a fragment, which may be shared by several recipes (`bootloader.py:429`, a shared fragment outside the mirrored folder is watched, test `test_gate_gap.py:162`) | the lock would have to cover the whole file set, read at lock time, and the set changes with the edit | a lock on the master does not stop a fragment save |
| any lock | refuses the save | - | cannot stop situation 2, only the in-app part of situation 1. A refused Blueprint save cannot be used to fix a failing recipe someone has open (Blueprint is the place to repair, her words 10d, `agent_channel.md:245`). |

## E. The options

Standing rules used: R1 no silent change / science transparent (agent_principles 2, ADR-090, ADR-104); R2 inform, never choose for the user (principle 3); R3 simple (principle 7, `dasharch.md`); R4 one authoritative way.
Already decided (not options): the export is refused when files changed (Eve 2026-11-06, ledger L05); HOME re-checks a recipe when its files change and a failing recipe is dropped with a lasting notice, never silently (GATE-GAP-1, built `c46cd11b`; ADR-104); Blueprint opens a failing recipe (Eve 10d). CONFIRM: that the Blueprint save is never blocked (written in the code and test docstrings as decided 2026-11-15; I find Eve's words only for "Blueprint can open a failing recipe"). S2-3 (a) decided 2026-11-15, not built. Nothing in the records decides a lock or a warning (ledger A11 is this question).

| # | What the user sees | What is built | Cost | Risks | Fit |
|---|---|---|---|---|---|
| 1. No lock; HOME warns | a lasting bar on the table and the plot: "The recipe (or the data) changed at hh:mm. This view was built from the earlier files. Reload." with a Reload button; export stays refused | the recipe side reuses `changed_since_view` (`export_handlers.py:205`) with the gate version as trigger (2 s); the data side needs a cheap trigger (size and time of the files as a trigger only, then the content hash to confirm; ADR-089 point 8 forbids size and time as the KEY, not as a trigger [MINE]); a Reload action | small to medium | the half-new view of A2 stays unless the view is made consistent (see F) | R1 yes, R2 yes, R3 yes. Extends ADR-089 and GATE-GAP-1; reconsiders nothing |
| 2. Blueprint warns before it saves | before the write: "HOME has this recipe open (n views in this app). Saving changes it for them; steps they recorded will need re-base." and the author confirms | a registry of open views per process (new state; `session.on_ended` not used today), a confirmation step in Blueprint | medium | blind to other processes and outside editors; the author is not the one who suffers | R2 yes. Only situation 1, in one process. Adds a second path to the warning of option 1 (R4). Touches the "save is never blocked" CONFIRM only if the confirm can be refused |
| 3. Lock that refuses the save | "This recipe is open in HOME; save refused" | one of the three ways in D | medium; stale locks; sync folder | see D; refused saves; cannot protect against outside edits | R2 no (the app decides); R3 no. Reconsiders GATE-GAP-1 spirit (Blueprint repairs failing recipes) and S2-3's assumption that a change can happen |
| 4. Blueprint saves a new version beside the old | HOME keeps the version it opened until Reload | two readings: (4a) a new file name: a recipe's id is its file name (ADR-092), so it is a second recipe, selector entries double, shipped recipes and sessions point to the old one. (4b) HOME holds a snapshot of the parsed recipe it opened: the orchestrator reads `load_data_analysis_recipe` itself 4 times (`orchestrator.py`), `active_cfg` is read at 25 places in the HOME handlers | 4a large and confusing; 4b medium to large, and the planned audit copy and "view pair" (spec section 3 point 7, P5 and P7) is the same mechanism | 4b is exactly what makes the view consistent; 4a multiplies recipes | 4b: R1 yes, R2 yes, matches S2-3 and ADR-101/ADR-099 point 22 (copy as source of truth). Reconsiders GATE-GAP-1 (HOME follows the live files) in part |
| 5. Nothing more | as today | nothing | none | the old-table-under-new-layout state, the wrong stored table after a revert (RUN case C), the false "re-assembling" sentence, the shared stored file crash | R1 no (silent), R4 no. Not neutral: it leaves verified defects |

## F. Recommendation (mine, not a decision)

**Recommendation: option 1, never a lock; after fixing three defects that exist whatever she picks.** A lock protects nothing in the cases that matter (outside editor, other process, synchronised folder) and refuses the one place built to repair recipes. Option 2 is a second warning path for a subset of situation 1.

**Defects to fix first (reported now, rule 8; each is a bug, not a choice):**
D1. The stored table file must be written to a temporary file and renamed (RUN: crash without it). One function, `write_anchor`; the same for the session files.
D2. A table built with keys that no longer match the recipe in memory must not be stored under those keys (RUN case C). Either the keys follow the recipe or the build uses the recipe the keys were made from.
D3. The sentence "Source data files ... changed - re-assembling" must say what is true.

**Default if she does not choose (recommendation): option 1, with HOME HOLDING the view until the user presses Reload** (variant 4b), because it is the only variant where "inform, never choose for the user", the export refusal and S2-3 say the same thing. Cheaper variant: HOME FOLLOWS (keys follow the gate version, a sentence says the view was rebuilt and how many recorded steps were made on the earlier version); then the export check no longer fires for a valid change, so S2-3 must be triggered by the audit steps' recorded recipe hash, not by the key check.

### Points only she can answer
1. When the recipe changes while a view is open: does HOME (a) HOLD what she opened until she presses Reload, or (b) FOLLOW the new recipe at once and tell her? (a) is consistent with S2-3 and costs more (the audit copy); (b) is smaller, and the view changes under her.
2. Data files: is a warning within about 2 s needed, or is the warning at export (always), at reload, and the one at the next click enough? (A timer on the data costs a cheap size-and-time check per poll.)
3. Blueprint: should the author of a save be told "n views of this recipe are open in this app" (option 2), knowing it covers one process and no outside editor? Yes / no.
4. The CONFIRM: Blueprint's save is never blocked. Does she confirm it as a rule (it excludes option 3)?
5. Two users sharing one app and one user data folder: is that a supported deployment? (Posit Connect and a server can serve several sessions in one process; Galaxy-style deployments are one user per container.) If yes, the shared stored files and the shared session folder (two users with the same recipe and data share audit ghosts) need a rule; if no, say so in the deployment README.
6. Data Import writes into `source.path`, for the shipped recipes a git-tracked test file. Is that intended?

## What an audit or a test would not catch
- The keys Calc not following the gate version (A2) passes every headless test I found: `test_export_view_consistency.py` calls the orchestrator with keys it computes itself and does not simulate "the recipe changed after the view opened, then HOME re-reads". RUN case B/C is such a test; none exists.
- The browser test file `test_shiny_gate_gap.py` covers only a change that FAILS the gate.
- The crash in C needs two processes; no test does that.

## Files
Scripts and outputs: `tmpAI/panel/round7/recipe_in_use/` (`s1_stale_view.py`, `s1_output.txt`, `a_valid_change.py`, `a_gate_time.py`, `c_concurrent_anchor.py`, `c_concurrent_anchor_atomic.py`, `d_locks.py`). Absolute folder: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/round7/recipe_in_use/`.
