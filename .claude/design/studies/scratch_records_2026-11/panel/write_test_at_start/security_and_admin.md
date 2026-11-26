# Write test at start: security and system administrator view (2026-11-21)

Seats: security reviewer, system administrator who hosts the app, architect (one source of truth). A study: nothing built, no repository file changed. I recommend; Eve decides.

**This study IS the security check Eve asks for** ("Yes have a security check for the write file practice, off by default", 2026-11-21, after the coordinator's addition; ledger line to be recorded). The check is sections 1 to 3 (threats, recipe, "non executable") with the runs in `scratch/`.

## VERDICT: is the practice, done as recommended (R1), safe to offer?

**YES, WITH THESE CONDITIONS.** The practice is safe to offer if all of these hold. If one is dropped, the verdict becomes NO for that variant.

| # | Condition | Why (evidence) |
|---|---|---|
| 1 | The file is created in ONE call that fails when the name exists (`O_CREAT|O_EXCL`); no "test then create" | RUN: a link planted at the name gave FileExistsError and the victim file stayed; plain `O_CREAT` overwrote the victim |
| 2 | The mode 0600 is passed AT CREATION; never created without a mode; never `chmod` after | RUN: no mode gives 0755 under umask 022; with 0600 the file is 0600 under umask 022, 077, 000, and a default ACL did not widen it |
| 3 | Content is one fixed line, the same on every deployment; nothing from a user, a recipe or the environment; no markup, no shebang | READ/RUN section 2 item 3; a file that survives is identifiable and harmless |
| 4 | Only in a place declared `read_write`; NEVER in a `read` place | D-0437 (`read` protects the consortium recipes); the test proves nothing there and would write where the deployment said not to |
| 5 | The test never creates the place (no `mkdir`); a missing place is reported | `check_store` and `SessionManager` create folders today (READ `opening_build.py:165`, `session_manager.py:274`); a mistyped path would make a new tree silently. Needs Eve's yes (OPEN) |
| 6 | The file is unnamed where the file system allows it, otherwise removed at once; a failed removal is REPORTED with the file name; no sweep by name pattern | RUN: nothing left after success and after a simulated failure; a killed process leaves a named file but no unnamed one; a failed removal leaves the file |
| 7 | The place may be a link: the test follows it (as the real writes do) and REPORTS where it ends; refusing links is a separate policy | RUN: links followed by all variants; legitimate on HPC (REASONED) |
| 8 | The result goes to the console and to memory; no log file in the place | one more unknown file otherwise |
| 9 | The documentation and the console say what the test proves and what it does not: "accepted a create and a small write at this moment"; not space for later tables, not quota, not the mount options (noexec), not other programs that watch the folder | RUN: zero bytes passed on a full file system; inotify sees the events either way; a write test does not see noexec |
| 10 | The test runs as the user the app runs as, with no extra right, and does not touch the process umask | REASONED |
| 11 | The test is OFF by default and the deployment file switches it on; when on, the console says so at start | decided by Eve, 2026-11-21 |
| 12 | Tests of it do not rely on `chmod 555` being read-only (root bypasses it) | RUN: uid 0 in a user namespace wrote into a 555 folder |

What this verdict does NOT cover (see "Not verified"): network and cluster file systems, Galaxy, Posit Connect, a sync client, an antivirus, a second real user. The first start on the real system is the test of those; with the test off by default, the operator who switches it on is the one who sees them.

Labels: RUN (I ran it; scripts and raw output in `tmpAI/panel/write_test_at_start/scratch/`: `wt.py`, `wt_out.txt`, `ns.py`, `ns_out.txt`, `ns2.py`, `ns2_out.txt`), READ (file:line), REASONED (follows, not run), EXTERNAL (known from outside, not checked here). Load was 2.6 to 3.5 before every run. Tags: DECIDED / CONFIRM / OPEN / MINE.

## 0. What is decided, what is read, what is open

| Point | Tag | Source |
|---|---|---|
| A write test at the start of the app, in each place the deployment declares writable, was accepted by Eve with conditions (not tampered with, not executable, what content, a switch to deactivate it, tested in deployment) | DECIDED (her words 2026-11-21; ledger line D-0440 once recorded) | the brief |
| Places have an access word, `read` or `read_write` | DECIDED | D-0417, D-0418, D-0437 |
| "The write test at start in each read_write place" was asked and not answered | was OPEN in D-0437; now answered by her words above | D-0437 text |
| The audit files go through the user place "with a plain error when the directory cannot be written" | DECIDED | D-0340 |
| The user place comes from system variables, one copy of the app per person | DECIDED | D-0429, D-0430 |
| The app checks at start that each declared place "exists and can be used as declared" | OPEN: it is the review session's reading (b) in D-0417, not confirmed by her | D-0417 text |
| Today: no write test at start | READ/RUN: the only write test is `check_store`, `app/modules/opening_build.py:160-167` (makes the folder, opens a `TemporaryFile`), at the opening of a recipe | file |
| Today: a user folder that cannot be written gives a blank grey page; traceback only in the console | RUN (earlier study `tmpAI/panel/deployment_no_user/RUN_FACTS.md` cases 2a, 3); READ: `app/src/server.py:149` makes `SessionManager`, `app/modules/session_manager.py:274` does `mkdir(parents=True)` | files |
| The app already writes and deletes at start inside `anchors/`: it removes stale `.*.parquet.*.tmp` files by name pattern | READ `app/src/bootloader.py:201-206`, `libs/transformer/src/transformer/anchor.py:28-53` | files |
| The two ADR lines "no symlinks" (`architecture_decisions.md` lines 9 and 122) are about the repository layout and the libs, not about places of a deployment | READ. I found no ADR on a place that is a link | file |
| ADR-071: the deployment (the system administrator) gates who may add recipes and which options exist; the app's own checks do not replace it | DECIDED (Eve 2026-11-15) | `architecture_decisions.md` ADR-071 |

## 1. What the risk is (question 1)

The first thing to say. Anyone who can write in a place can already change the stored tables, the session records and the audit files of the app, and any file the app later reads. A test file adds no new power to such a person. So the real protection of a place is its folder rights (owner, mode, ACL, mount). The test file must only not make anything worse: it must not write outside the place, must not overwrite something, must not be left behind, must not be run, must not be wider than the app's own user.

| Threat | Likely here? | What it could cause | Measure | Evidence |
|---|---|---|---|---|
| A link planted AT THE NAME of the test file (the attacker guesses the name) | Low. The name is random and the creation is exclusive | The write lands in another file and overwrites it | Exclusive creation (`O_CREAT|O_EXCL`): it fails with "File exists" even for a link, also a dangling one. A random name of 64 bits (or no name at all, see O_TMPFILE) | RUN: a link planted at the name, pointing to a real file: FileExistsError, victim file unchanged. Without `O_EXCL`, a plain `O_CREAT` followed the link and wrote `OVERWRITTEN` into the victim |
| The PLACE itself is a link (or a part of its path is) | High on HPC and Galaxy, and legitimate: scratch folders are often links. It is the deployer's own declaration | The test and the app write in the real folder, which may be where the deployer did not expect | Do not refuse: report "declared X, resolves to Y". The app already writes its real tables through the same link, so a test that refused would test something else than the real writes | RUN: `os.open` of a name through a link folder works; `tempfile.TemporaryFile(dir=link)` followed the link; a link in the parent path is not seen by `O_NOFOLLOW`, which only looks at the last part |
| A race between check and use (a name tested for absence, then created) | Low. Only exists if the code tests first and creates after | Same as the link at the name | Never test first: make the file in one call that fails if it exists (`O_EXCL`). Never use `os.path.exists` then `open` | RUN case 3 |
| A file left behind after a crash | Very low: the window is microseconds. With a named file it is real; with an unnamed file (`O_TMPFILE`) there is none | One small file named like the app's test, one inode | `O_TMPFILE` leaves nothing; a named file is removed in `finally`. If removal fails, say so and name the file; do not sweep by pattern | RUN: failure after create (simulated ENOSPC) left nothing; a process killed after create left `.sparmvet-wt-killed` (named) and nothing (O_TMPFILE); removal after the folder became read-only: EACCES, the file stays |
| Another process executes or parses it (a pipeline that watches a folder; a Galaxy job folder scanned for outputs; a web-served folder; a backup or sync tool) | Medium for a named file in a shared work folder: an output scanner may pick up a 0-byte or 20-byte file and Galaxy may list it. Low for a place the app owns | A stray "output", a sync of a transient file, an antivirus scan, a log line in an audit tool | Prefer an unnamed file. Put the test only in the declared `read_write` places (never in the data or recipe places the pipeline reads). Content that is harmless if parsed (plain text, no markup). The switch for sites that object | RUN with inotify on the folder: a named file gives CREATE, OPEN, MODIFY, CLOSE_WRITE, DELETE with its name; an `O_TMPFILE` gives no CREATE and no DELETE, but still OPEN, MODIFY, CLOSE_WRITE on a name like `#15759741`. So a watcher is not blind to an unnamed file. I did not run Galaxy, a sync client or an antivirus |
| Quota or inodes filled by repeated starts | Very low if removal works: net zero | One inode per failed removal per start | Remove at once; report a failed removal (the operator sees it at each start) | RUN: 200 runs of each variant, nothing left (folder listing empty after the timing loop, checked by `ls -A` at the end) |
| Permissions wider than intended (umask, default ACL) | The danger is a creation call WITHOUT a mode | An executable or group-readable file | Always give mode 0600 at creation (no `chmod` afterwards). The umask can only remove bits | RUN: mode argument 0600 gives 0600 under umask 022, 077, 000 and 0400 under 277. A creation without mode gives 0755 under umask 022 (executable bit set), and 0700 under 077. `open(p, "x")` gives 0644. `mkstemp` gives 0600. A default ACL (a user with rwx) on the folder did not widen it: the file got mask `---`, mode 0600 |
| Leak by name or content | Low. The name says "sparmvet"; the content would say the same | Tells who lists the folder which app is there. Server paths in the console are for the operator | Fixed content and a fixed prefix, nothing from the user, the recipe or the environment. Do not send server paths to a visitor | READ: today some visitor notices already show server paths and Python error text (RUN_FACTS case 2b). That is a separate fault, see section 7 |
| A shared folder where another user's process sees the file | Low (D-0430: one copy of the app per person; a shared place only if the administrator declares it) | Another user sees a name and a size, not the content (mode 0600) | Unnamed file, or 0600 and a random name. Tell the operator when a place is group or world writable (information line, section 2 item 8) | RUN: the sticky folder `/tmp` (root, 1777) accepted both variants. NOT run: a second user (no sudo here). I could not simulate a file of another uid at the same name; the exclusive creation fails on any existing name by the kernel rule, whoever owns it (RUN case 3 for my own file) |
| A hang: the write blocks (a network file system that does not answer) | Medium on HPC with a stalled mount | The app does not start, and nothing is said | A time limit is an OPEN design point (section 2 item 9) | REASONED, not run |
| The test says OK and a later write fails (quota, space, a place that changed) | Medium | The operator trusts "OK" | The test proves "this folder accepted a create and a small write at start", nothing more; say so in the documentation | RUN: on a full file system (tmpfs of 4 KB, ENOSPC) a ZERO-byte test passed and a 20-byte test failed with ENOSPC |

Non-threats for this app, with the reason: the app never executes the file and never reads it back; the content comes from no user; the file is not served to a browser; there is no privilege boundary crossed (the test runs as the user the app runs as).

## 2. The safe way: the smallest recipe (question 2)

### Recommended recipe R1 (stdlib, one function)

1. Look at the place without changing it: `os.lstat`. Not found: report "does not exist" (see item 9: the test never creates the place). Not a folder: report. A link: remember the link and its target.
2. Open an unnamed file in the place: `tempfile.TemporaryFile(dir=place)`. On Linux with a file system that supports it this is `O_TMPFILE` with mode 0600 (nothing in the folder, nothing left after a kill, no name to guess, no link at the name). When the file system does not support it (the stdlib catches the error and goes on), Python makes a named file: `O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0600, random name, and unlinks it at once. RUN and READ: `tempfile._bin_openflags` holds O_CREAT, O_EXCL, O_NOFOLLOW (output at the end of my run); the stdlib source: `_mkstemp_inner` passes `0o600`, `TemporaryFile` falls back on `OSError`.
3. Write a fixed short text and flush and `fsync`. Content: one line of fixed ASCII, for example `sparmvet write test, safe to delete`, the same bytes on every deployment. Why not zero bytes: a zero-byte file proves "I may create", not "I may store data"; RUN on a full file system: zero bytes passed, 20 bytes failed ENOSPC. Why `fsync`: file systems with delayed allocation (btrfs, ext4, network file systems) report ENOSPC and quota errors late (EXTERNAL; on tmpfs it is immediate, RUN). Why fixed: a file that survives (fallback path, killed process) is identifiable and harmless.
4. Close. The file has no name (or is unlinked in the fallback). Nothing to remove. If the fallback unlink fails, Python closes and raises; report it as "test file could not be removed: name, error" and keep the place as writable (the write worked).
5. Record in memory and write to the console, nothing in a file in the place (a log file there would be one more unknown file): the place name as declared, the declared path, where it resolves (`os.path.realpath`, only a report), the access word, result (passed / failed / skipped), the error text, the time in ms.
6. The mode: never set by the caller. The stdlib passes 0600. Never `open(p, "x")` and never `os.open` without a mode (RUN: 0755 under umask 022).
7. Do not change the process umask (it is process-wide and would change the files other code writes).
8. Information, not a stop (optional, OPEN for Eve): if the place is writable by group or others (`st_mode & 0o022`) or owned by another user, add a line "this place can be changed by other users"; if `os.statvfs(place).f_flag & os.ST_NOEXEC`, add "mounted noexec" (only information; the app never executes anything there).
9. Never create the place in the test. `check_store` today does `mkdir(parents=True)` (READ `opening_build.py:165`) and `SessionManager` the same (READ `session_manager.py:274`). A mistyped path then makes a new tree silently. Whether the app may create a declared place is OPEN (MINE: say it in the deployment specification, per place; D-0417 point (b) says "exists").
10. One function, headless (no Shiny, Two-Category Law, ADR-045), called by the bootloader at start and by `check_store` at the opening. Today there are two ways to ask the same question; there must be one (rule: one authoritative way). The opening still needs it, because a place can fail after the start.

Timing (RUN, 200 runs each, this machine): btrfs scratch: named 20 bytes + fsync + remove 1.14 ms; named without fsync 0.07 ms; named zero bytes 0.05 ms; `O_TMPFILE` 20 bytes + fsync 1.04 ms; plain `TemporaryFile` open and close 0.03 ms; tmpfs: 0.02 ms for all. On a network or Lustre file system I expect tens of ms to seconds (REASONED, not run). One place per start: not a cost.

### Variant R2: the same with an explicit directory handle and a named file

`os.open(place, O_DIRECTORY|O_NOFOLLOW)`, then `os.open(random_name, O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW, 0o600, dir_fd=handle)`, write, fsync, `os.unlink(name, dir_fd=handle)`. What it adds, RUN: the place is a fixed object after the first call (a swap of the link between "check" and "use" cannot move the write); `readlink /proc/self/fd/N` gives the real path of what was really used (Linux only); a link as the last part of the place is refused (Linux gives ENOTDIR, not ELOOP: the message must be written by the app, "is a link to X"); a link in the middle of the path is NOT seen. What it costs: two code paths if you also keep O_TMPFILE, or only the named file (a name visible in the folder, a CREATE and a DELETE for watchers, a crash residue possible); Linux-only reporting. Against an attacker who owns the place it adds nothing (he already controls the files). I would choose it only if Eve wants a "refuse a link" policy.

### Variant R3: R1 plus a refusal of links

R1 and, when step 1 finds a link, stop: "The place is a link; links are refused by this deployment". Needs a decision on HPC scratch links; makes the test disagree with the real writes (they follow the link). Offered only as an option the deployer could switch on, not as the default (informs, does not choose).

### Would `tempfile.mkstemp` in that folder do this?

Almost: RUN: `mkstemp` gives 0600 under every umask I tried (the same 0600 the existing anchor writer relies on, READ `anchor.py:171`), random name, `O_EXCL`, and `O_NOFOLLOW` (stdlib flags). It does not cover: a place that is a link (it follows it); a named file that exists briefly; no fixed content (it writes nothing: zero bytes pass on a full disk); no removal (the caller must unlink); no report of where it resolved; no handle to keep the folder fixed. `TemporaryFile` (what `check_store` uses) covers the same and removes the file, but it also writes nothing and `check_store` makes the folder first. So R1 = what the app already uses + a fixed write + fsync + a report + no `mkdir`.

### Raw cases (RUN, `wt_out.txt`, `ns_out.txt`, `ns2_out.txt`)

| Case | Result |
|---|---|
| Normal folder | passes; mode 0600 under umask 022, 077, 000; 0400 under 277; nothing left |
| The place is a link | `os.open` and `TemporaryFile` follow it; a directory handle with `O_NOFOLLOW` fails with ENOTDIR; `realpath` reports the target; a link in the parent path passes the handle and `/proc/self/fd/N` shows the real folder |
| Name exists (file, dangling link, link to a real file) | exclusive creation: FileExistsError for all three; victim file unchanged |
| Read-only folder (mode 555) | named, `O_TMPFILE` and `TemporaryFile`: PermissionError (EACCES); `os.access(W_OK)` correct here (False) |
| Folder with w but no x (mode 644) | `os.access(W_OK)` says True; the write fails with EACCES (so `os.access` alone is wrong) |
| Read-only mount (tmpfs `ro`, in a user namespace) | all three: EROFS; `os.access` False |
| Root (user namespace uid 0) on a mode 555 folder | `os.access` True and the write succeeds: a mode change does NOT make a place read-only for root |
| Sticky folder of another user (`/tmp`, root, 1777) | both variants pass. Second-user case NOT run |
| Default ACL with a named user | no widening: the file got mask `---` and mode 0600 |
| Full file system (tmpfs 4 KB) | zero bytes: passes; 20 bytes + fsync: ENOSPC; nothing left in the folder after the failure (checked with my own function with `finally`; my first crude one-line version left `.w`: that was my test, not the recipe) |
| After a simulated failure after create | nothing left (named, removed in `finally`) |
| Process killed between create and remove | named: one file stays; `O_TMPFILE`: none |
| Removal fails (folder made read-only after create) | EACCES, the file stays, so the app must say it |
| Time | see above |
| `noexec` mount (user namespace) | exec of a 0755 script on it: EACCES; the same script on a normal folder runs; both create variants worked on that mount (a write test does not see noexec) |
| `nosuid` mount | both pass |

## 3. "Non executable" (question 3)

| Meaning | Can the app promise it? |
|---|---|
| The file's mode has no execute bit | Yes, with an explicit mode 0600 at creation. RUN: exec of the 0600 file: EACCES. A file created without a mode got 0755 (RUN), so the promise holds only if the mode is passed. |
| The file system is mounted `noexec` | No, it is the administrator's. RUN: on a noexec mount a 0755 script gives EACCES. The app can read the flag (`os.statvfs(...).f_flag & os.ST_NOEXEC`) and report it, not set it. A write test does not detect it. |
| The app never executes it | Yes, it is a property of the code: the file is written, never read back, never passed to a program. A test can check that no code path opens it for reading. |
| Zero-byte file | Fine for execution (exec of a 0700 empty file gave ENOEXEC) but a shell can still run an empty or a text file if its exec bit is set; with 0600 nobody can, not the owner either. |
| The content is harmless if some tool parses it | Yes: fixed plain text, no markup, no shebang, no path. |
| Another process of the same user runs it | Cannot be promised; the same user can run anything. With `O_TMPFILE` the file has no path to run (only `/proc/self/fd` of the same process). |

Honest sentence to promise: "The test file is created with permission 600 (no execute right for anyone), holds one fixed line, is never read or run by the app, and is removed at once. The app cannot know about mount options of the file system or about other programs that read the folder."

## 4. Is a write test the right tool? (question 4)

| | (a) no test | (b) `os.access` only | (c) a write test at start in each `read_write` place | (d) a write test only for the places a use case needs at start |
|---|---|---|---|---|
| System administrator | nothing written at start; the first fault shows at the first save | nothing written; but see "wrong" below | one tiny unnamed or removed file per place; can switch off | the least written; needs a map "feature to place" |
| Visitor | blank grey page today (RUN cases 2a, 3) | same | the page does not exist when a place is broken: connection refused, text in the console (RUN case 8 shows the same behaviour for absent data; READ `bootloader.py:617-626` "Deployment failed ... The app cannot start in a contradictory state") | the same for the needed places only, others fail later |
| Operator finding a fault before visitors | no | partly | yes, with the place named | yes for some places only |
| What can be wrong | everything, late | RUN: `os.access` says True for a folder with w and no x while the write fails; it cannot see space, quota, EROFS in some network cases, root squash, or a mount that changed (EXTERNAL for the network cases; not run) | a pass is "accepted a create and a small write at start" | a place not on the map is not tested; the map is a second store that can disagree with the list of features (architect point) |
| Rule fit | D-0340 plain error needs a build anyway | OK for `read` places (read access only) | D-0417 (b) reading; "declared read_write means the app writes there" | none of the decisions says which place a feature needs |

Position (the switch is off by default, decided by Eve): (c) when the deployment file switches it on, with `read` places checked for read access only (never written; `read` protects the consortium recipes, D-0437). (d) needs a second list that can disagree with the declaration; the declaration itself is the list. A place declared `read_write` that nothing needs is a wrong declaration; the operator fixes the declaration or sets the switch. (b) is acceptable as the check of `read` places and as the "switch off" fallback only if the app still tells the operator that nothing was written.

## 5. The switch (question 5)

Name proposals (MINE, not decided): `write_test_at_start: true|false`; or `startup_checks.write_test: on|off`; or `check_places: write|read|none` (three levels: write test, read access only, nothing). The third one fits better with section 4: off still checks the `read` places and the existence of the places without writing.

Scope:

| Scope | Pros | Cons |
|---|---|---|
| One switch for the deployment | Simple; one state to document and test; one line in the console | An administrator who objects for one place (for example an audited scratch file system) switches off all |
| One key on each place (`write_test: false`) | Exact; fits the named places | More keys and states (each place x each access word); a deployer can forget one place; more tests |
| Both (a switch plus an exception per place) | Complete | Two stores that can disagree; does not follow "keep it simple" |

My view: one switch for the whole deployment now; a key per place only if a real case appears (the same stance as D-0430: revisit when needs appear). That is MINE; Eve decides.

Default (DECIDED by Eve, 2026-11-21: OFF; the deployment file switches the test on). The earlier table "on or off" is dropped as a recommendation. In one line, what OFF costs: an operator who does not switch the test on learns of an unwritable place only at the first write, and today that is a blank grey page for the sessions folder and a plain message at the opening of a recipe (`tmpAI/panel/deployment_no_user/RUN_FACTS.md` cases 2 and 3). What the administrator who does not like unknown files gets: the app writes no test file at all unless the deployment file asks for it (but see the note on start-time deletes below).

Two consequences to state in the deployment documentation: (1) "off" does not mean "nothing written at start": at start the bootloader already deletes stale temporary files and tables of another cache version in `anchors/` (READ `app/src/bootloader.py:201-216`, not inside a try; REASONED: an OSError from a delete would stop the start), and the first visit writes the sessions folder and the stored tables (RUN_FACTS case 1: 25 files, 87,966 bytes). The switch controls the test file only. (2) The sentence at start when off (console, one line): `Write test skipped (write_test_at_start is off in the deployment file): the places are not checked until first used. A place that cannot be written will show as an error at the first save.` When on, one line per place (section 7).

### What must be true when the test is OFF: every first write gives the plain error D-0340 asks for

D-0340 (DECIDED): "a plain error when the directory cannot be written". Today, from the facts files (`deployment_no_user/FACTS.md` section B, `RUN_FACTS.md`) and from lines I read now:

| Write site | file:line | What happens today when it cannot write | Plain error today? |
|---|---|---|---|
| Sessions folder, made at EVERY browser connection | `app/src/server.py:149` calls `SessionManager`; `app/modules/session_manager.py:274` (`mkdir(parents=True)` in `__init__`); also `:314-318` | traceback in the console, the visitor gets a blank grey page (RUN_FACTS 2a, 3) | NO. This is the one the switch does not fix |
| Session record `assembly.json` | `app/handlers/home_theater.py:1567-1578` (write `session_manager.py:392`); notice `:1584-1588` | red notice "The record of this session could not be written ... check that the user data folder can be written", with the Python error and the server path (RUN_FACTS 2b) | Plain sentence, but with a raw error and a path |
| Stored tables, the probe and each table | `app/modules/opening_build.py:160-167, 249-254`; `opening_handlers.py:140-145`; `libs/transformer/src/transformer/anchor.py:150-175` | the opening stops with "the computer or its storage failed ... free space or fix the rights of the folder" (RUN_FACTS 2b) | YES (names a path) |
| T3 audit ghost | `app/handlers/audit_stack.py:135-138, 291-296`; writer `session_manager.py:483-540` | warning toast (facts file, READ there; not run) | Probably (not verified by me) |
| Gallery index | `libs/viz_gallery/src/viz_gallery/gallery_manager.py:187-214`; `app/src/bootloader.py:226-241` | printed in the console, old index kept, app continues | Console only: the operator sees it, the visitor does not (not run) |
| Export, report render in the system temp folder | `app/handlers/export_handlers.py:2043-2057` | a notice that says "install Quarto" while the cause is the unwritable temp folder (RUN_FACTS case 10) | NO: the wrong cause |
| Bundle import | `app/modules/bundle_importer.py:261-266` (`mkdir`, `write_bytes`) | the facts file says "a message (not read)"; I read these lines only and saw no try around them | NOT VERIFIED |
| Recipe save in BLUEPRINT | `app/handlers/blueprint_handlers.py:1188-1193` (READ now) | toast "Save failed: <OSError text>" with the raw error and path | Partly: a toast, raw text |
| Recipe copy by "ingest" | `app/handlers/ingestion_handlers.py:50` (`shutil.copy`, READ now) | no try around the copy; an OSError is not turned into a message (REASONED) | NO |
| Audit files in `audit/` (D-0340, D-0423) and the browser upload (D-0438, D-0439) | not built (D-0423 "Not built") | n/a | They must give the plain error when they are built |

So with the test off, the sentence "the first failed write gives the plain error" is NOT true today for: the sessions folder (blank page), the export temp folder (wrong cause), the recipe copy by ingest, and the bundle import (unverified). It is true in part (a message with raw text and a path) for the session record and the recipe save. That is a half fix if the switch ships alone: an OFF default is only safe to ship when those sites give the one plain error. Naming it as a condition of the OFF default.

What the switch alone does not fix: the blank grey page. It comes from `session_manager.py:274` (`mkdir(parents=True)` raises PermissionError inside `server.py:149`) and shows no message (RUN cases 2a and 3). With the test ON, the app stops at start with a sentence, so the page does not exist. With the test OFF (the decided default), the visitor still gets the blank page unless the session folder creation is changed to give the plain error D-0340 asks for. That change is separate, and it must be built or the switch's "off" mode has no safe landing (half fix otherwise).

## 6. "Should be tested in deployment" (question 6)

Headless test (no browser), for one function and for the bootloader call:

| Case | Expected |
|---|---|
| Place writable, test on | passes; nothing left in the folder (listing empty); mode of any file seen is 0600; console line with the declared and resolved path |
| Place read-only | stops with the plain sentence naming the place, the access word, the error and who fixes it; exit code not zero |
| Place missing | stops: "does not exist"; nothing created |
| Place is a link | passes and reports declared and resolved path (or stops, if R3) |
| Switch off | the app starts; the one console line; the first write gives the plain error (D-0340) |
| Place declared `read` | never written (a test lists the folder before and after; or the place is made read-only and still passes) |
| Full file system | the fixed-content test fails with ENOSPC (needs a small tmpfs, root or a user namespace) |
| Removal fails | warning with the file name; the app starts |
| No leftover after success and after failure | listing before and after |

What a test of a deployment shows, for both states of the switch (headless: the bootloader and the one function; no browser):

| State | Place | Expected result (the test fails if it differs) |
|---|---|---|
| ON | `read_write` place, writable | passes; one console line per place (declared path, resolved path, passed); the folder listing is the same before and after |
| ON | `read_write` place, not writable | the start stops with the sentence naming the place, the cause and who fixes it; non-zero exit; no server on the port |
| ON | `read_write` place, missing | stops with "does not exist"; nothing created |
| ON | `read_write` place that is a link | passes and says where it ends |
| ON | `read` place | never written (listing before and after identical; also with the place made unwritable) |
| ON | removal made to fail | warning with the file name; the app starts |
| OFF (default) | any place, writable | the app starts; the console says the test was skipped; no test file event (a watched folder shows no create of the test file) |
| OFF | `read_write` place, not writable | the app STARTS (nothing is checked); the console says the test was skipped; the FIRST write of each kind in section 5 gives the plain error. One test per write site: sessions folder, session record, stored tables, export temp folder, recipe save. Today the sessions folder test fails (blank page, RUN_FACTS 2a, 3), which is the point of that test |
| OFF vs ON | same deployment, same place | the only differences: the start line, and where the error appears (at start vs at first write); a result of data analysis is identical (nothing in the test touches the data) |
| both | the switch value is not a boolean or is misspelled | the deployment file is refused with the key named (no silent default; old and new keys: no shim) |

Traps for the tests (what a test would not catch if written naively): a `chmod 555` folder is not read-only for root, and many CI containers run as root (RUN: uid 0 in a user namespace passed the write on a 555 folder). Use a read-only mount, a monkeypatched error, or skip when `os.geteuid() == 0`, and restore the mode so the temporary folder can be deleted. A test must not use the private `tempfile._O_TMPFILE_WORKS` to force the fallback. Tests that need a mount or a user namespace may not run on every machine.

Cannot be tested without the real system, and the deployment documentation should say so: Galaxy (job folders, how outputs are scanned, which user), an HPC scratch file system (Lustre, GPFS: O_TMPFILE support, fsync time, quota behaviour, a hang), NFS (root squash, `O_TMPFILE` support: EXTERNAL, I believe the Linux NFS client does not support it, so R1 uses the named fallback there; not verified), Posit Connect (no user place by D-0429(4); the test has nothing to write), the owner's cloud-synced folder (sync of a transient file), antivirus, auditd. The operator's first start on the real system is the test of those; the console line is what shows it.

## 7. Sentences (proposals, question 7)

For the operator, in the console. Plain, with the place, the access word, the cause, who fixes it. `<...>` are filled in.

| Outcome | Proposed sentence |
|---|---|
| Passed | `Write test: place '<name>' (read_write) at <declared path> accepted a test file; the file has no name and is gone.` If a link: add `The place is a link: <declared> -> <real>. The app writes in <real>.` |
| Failed, permission | `Deployment failed: place '<name>' (read_write) at <path> cannot be written: Permission denied. The app writes <what: stored tables, session records, audit> there. Fix: give the user that runs the app (<user>) the right to write in this folder, or declare the place read. Who: operator.` |
| Failed, space | `... cannot be written: No space left on device (or quota exceeded). Free space or quota, then restart.` |
| Failed, read-only mount | `... cannot be written: Read-only file system. The folder is mounted read-only; mount it for writing or declare the place read.` |
| Missing | `Deployment failed: place '<name>' at <path> does not exist. Create it or correct the path in the deployment file, then restart. The app does not create it.` (if Eve decides the app creates it, the sentence changes) |
| Removal failed | `Write test: place '<name>' is writable, but the test file <name> could not be removed: <error>. Remove it by hand.` |
| Skipped | `Write test skipped (write_test_at_start is off): places are not checked until first used. A place that cannot be written will show as an error at the first save.` |
| Information (optional) | `Place '<name>' can be written by other users (group or world write).` `Place '<name>' is on a file system mounted noexec.` |

For a visitor: nothing at start when the test passes. When the app has stopped, there is no page: that is the operator's case. When the test is off and the first save fails, the visitor needs one plain sentence on screen: "Your work cannot be saved on this server (the saving place is not writable). Tell the operator." It does not carry a server path or a Python error. Today it does (RUN_FACTS case 2b: paths and `[Errno 13]` in the notices) and in the blank case there is nothing. That is the D-0340 piece, to be built, whatever the switch is.

## 8. Where an option reconsiders a decision (information, never a reason to reject)

| Option | Reconsiders |
|---|---|
| R1 (recommended) | Nothing decided. It changes `check_store` (one function replaces it, MINE) and adds a bootloader call; D-0417 (b) reading is confirmed in practice |
| Refuse a link (R3) | Nothing decided; but it makes the test differ from the real writes and may break legitimate HPC use |
| The test never creates a missing place | Changes today's `mkdir(parents=True)` in `check_store` and `SessionManager` (READ); D-0340's "plain error when the directory cannot be written" is consistent |
| Switch also turns off `check_store` | Changes today's behaviour at the opening (the test at the opening exists today and is on); needs Eve's yes. With OFF as the default this matters more: otherwise "off" still writes an unnamed file at every opening |
| Option (d) | Needs a map of feature to place; reconsiders nothing, adds a second source |
| Test also logs to a file in the place | Not recommended (one more unknown file) |

## 9. What the user must be told to choose well (not what to choose)

1. What the test proves and does not: a create plus a small write accepted at this moment; not space for later tables, not quota, not that the folder will not change, not mount options.
2. The default of the switch is OFF (decided). With it on, a broken place stops the app at start (no page, text in the log). With it off, a broken place shows at the first write, and for the sessions folder today as a blank grey page until the write sites listed in section 5 give the plain error.
3. The test file: unnamed where the file system allows it (nothing in the folder), otherwise a random name removed at once; the watchers of a folder still see events either way (RUN).
4. Links: the test follows a link and reports where it ends; refusing links is possible and has a price (HPC scratch).
5. The scope of the switch (whole deployment or per place) and whether it also turns off the test at the opening of a recipe.
6. Whether the app creates a missing place or only reports it.
7. What cannot be tested here (Galaxy, HPC, NFS, Connect, sync tools) and is left to the first start on the real system.

## Not verified

- A second real user (no sudo): a file of another uid at the same name in a sticky folder; the kernel rule is that `O_EXCL` fails on any name, which I showed with my own file. `fs.protected_regular=1`, `protected_symlinks=1` on this machine (RUN, read from /proc), applies to creation without `O_EXCL`.
- Network file systems (NFS, Lustre, GPFS): `O_TMPFILE` support, `fsync` time, quota errors at close, root squash, hangs. Not run. The statements about them are EXTERNAL or REASONED.
- Galaxy, Posit Connect, a container runtime, a cloud sync client (Insync), an antivirus: not run.
- Windows and macOS (no `O_TMPFILE`, no `/proc`): not checked; the app's targets are Linux (`dasharch.md` section 3).
- That `TemporaryFile` falls back correctly on a file system without `O_TMPFILE`: READ in the stdlib source only; no such file system here.
- That the bootloader's fatal path (`exit_if_errors`) is the right exit for a failed place: READ for absent data (`bootloader.py:610-628`) and RUN in the earlier study (case 8), not run for a place.
- `os.statvfs` flags `ST_NOEXEC` reading: not run.
- The time of the test on a real cluster.
- My test folders were in the owner's synced working tree and one file in `/tmp`; all removed.
