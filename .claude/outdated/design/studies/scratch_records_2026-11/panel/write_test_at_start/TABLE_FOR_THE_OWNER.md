# The write test at start: security check, one table for the owner (2026-11-21; your orders D-0440 and D-0441)

## 0. How to read this
- You asked for a security check of "the write file practice": a small test file that the app writes at start in each place the deployment declares as writable. You decided: the test is OFF by default (D-0441); the file must not be tampered with and must not be executable (D-0440).
- RUN = I ran it. READ = read in the code (file:line). REASONED = follows, not run. Every key name and sentence below is a PROPOSAL, nothing is decided or built. The full check is in `security_and_admin.md` (same folder); the raw outputs are in `scratch/`.
- Only ONE viewpoint did this check (a security reviewer and a system administrator, one reader in two seats). A second pair of eyes should look at: the code of the test function once it exists, the links case, and the real file systems of section 9.
- **Verdict: the practice is safe to offer, with conditions.** It is safe if the file is made in a careful way (section 2). It is NOT a complete protection of a place; the folder rights are.

## 1. Your three questions
**"Can the file be tampered with?"**
- Anyone who can write in a place can already change the stored tables, the session records and the audit files. A test file gives such a person no new power. The real protection of a place is its folder rights, set by the administrator.
- So the test file only has to avoid making things worse. The runs found two real dangers, both from careless code:
  - A file made with the default permissions is executable. RUN: created without a mode, it got 0755 (the "x" bit is set). Created with mode 0600 it was 0600 under every system setting I tried.
  - A planted link. A link is a file name that points to another file. If an attacker puts a link at the name the app will use, a careless write goes to the other file and overwrites it. RUN: with a plain create, the other file was overwritten. With exclusive creation (the file is made only if no file of that name exists) the create failed and the other file stayed unchanged.
- Suggestion: use exclusive creation and give the mode 0600 at creation (never change it afterwards).

**"Non-executable?"**
- What can be promised: the file has no execute right for anyone (RUN: running it gave "permission denied"), holds one fixed line, is never read or run by the app, and is removed at once.
- What cannot be promised: that the file system is not mounted to allow running programs (the administrator's setting; the app can only read it and report it), and that no other program on the server will read the folder. RUN: a write test does not see a "noexec" mount.

**"What content?"**
- Zero bytes is a weak test. RUN on a full file system: the zero-byte test passed; a 20-byte test failed with "No space left on device". A test that passes where a real write fails is worse than none.
- Suggestion: one short fixed line, the same on every deployment, plain text, nothing from a user, a recipe or the environment. For example `sparmvet write test, safe to delete`. A file that survives is then easy to recognise and harmless.

## 2. The recommended way (recipe "R1", all in the Python standard library)
1. Look at the place without changing it. If it does not exist, report it; the test never creates a place (see section 8, choice 3).
2. Open an unnamed file in the place (`tempfile.TemporaryFile`). On Linux this makes a file with no name in the folder (mode 0600), so there is nothing to find, nothing to leave behind after a crash, and no name to attack. Why: this removes both dangers at once. Where the file system cannot do it, the standard library makes a named file with a random name by exclusive creation and mode 0600, and removes it at once.
3. Write the fixed line and force it to disk (`fsync`). Why: a full disk or a quota shows up at this moment, not later.
4. Close. Nothing to remove. If a named file cannot be removed, say so and name the file; do not sweep the folder by name pattern. Why: a sweep could delete a file that is not ours.
5. Report to the console and keep the result in memory; write no log file in the place. Why: a log file is one more unknown file.
6. Never change the process setting that removes permissions from new files (umask). Why: it is process-wide and would change files that other code writes.
7. Only in places declared `read_write`. A `read` place is never written (D-0437). Why: `read` protects the consortium recipes.
8. A place that is a link is followed and its end is reported ("declared X, ends at Y"). Why: the app's real writes follow it too; a test that refused would test something else.

Two variants, one line each:
- Variant 2: the same with a named file and an open folder handle; it adds a fixed folder object and a real-path report, costs a visible file name and two code paths. Only worth it if you want links refused.
- Variant 3: recipe R1 plus a refusal of links. It makes the test disagree with the real writes, and may break scratch folders on a cluster that are links on purpose. Offer it only as an option the deployer switches on.

## 3. What was run (all RUN, this machine, Linux)
| case | result | what it shows |
|---|---|---|
| Default permissions | file made without a mode: 0755; with mode 0600: 0600 under three different system settings; a default folder ACL did not widen it | pass the mode at creation, always |
| A link planted at the file name | exclusive creation failed, victim file unchanged; plain create overwrote the victim | exclusive creation is the key protection |
| A name that already exists (file, dangling link, link to a real file) | exclusive creation failed for all three | no "test then create" |
| A read-only folder (mode 555) | create refused (permission denied) | the test sees it |
| A full file system (4 KB) | 0 bytes: passed; 20 bytes + fsync: failed | a fixed line, not an empty file |
| A folder watcher (inotify) | a named file shows create, write, delete with its name; an unnamed file shows no create and no delete, but still the open and write | a watcher is not blind to either; say so to administrators |
| The place is a link | followed by the real writes and by the test; the real end can be read | report, do not refuse |
| `os.access` (the permission check without writing) | said "writable" for a folder with write but no search right, where the real write failed; also: a folder with mode 555 is NOT read-only for the superuser | never use it alone; tests must not rely on `chmod 555` |
| Time | 0.03 to 1.1 ms per place on this disk (1.1 ms with fsync); on a network or cluster file system tens of ms to seconds (REASONED, not run) | not a cost here |
| Nothing left behind | after success, after a simulated failure: empty folder; after a killed process: a named file stays, an unnamed file leaves nothing; if removal fails the file stays and must be reported | report a failed removal |

## 4. "Off by default": what it costs and what must then be true
- Off means: a place that cannot be written is found only at the first real write. Today that first write often gives no plain error (D-0340 asks for "a plain error when the directory cannot be written").
- **Without the fixes below, "off" leaves a blank grey page** for the visitor (RUN, earlier study cases 2a and 3). That would be a half fix.
- Off does NOT mean nothing is written at start. At start the app already deletes old temporary files and old-version tables in the stored-tables folder (READ `app/src/bootloader.py:201-216`, not inside a try: a failed delete could stop the start), and the first visit writes the sessions folder and the stored tables (RUN: 25 files, 87,966 bytes). The switch controls the test file only. This must be said in the deployment documentation.

| where the app first writes | what the visitor or operator sees today when it cannot write | a plain error? | file:line |
|---|---|---|---|
| the sessions folder, at every browser connection | blank grey page; traceback only in the console (RUN) | NO. This is the main gap | `app/src/server.py:149`, `app/modules/session_manager.py:274` |
| the session record | red notice with a plain sentence, but with a raw Python error and a server path (RUN) | partly | `app/handlers/home_theater.py:1567-1588` |
| the stored tables at the opening of a recipe | stops with "the computer or its storage failed ... fix the rights of the folder" (RUN) | YES (it shows a path) | `app/modules/opening_build.py:160-167, 249-254` |
| the export's temporary folder | a notice that says "install Quarto" while the cause is the folder (RUN) | NO: wrong cause | `app/handlers/export_handlers.py:2043-2057` |
| the recipe save in BLUEPRINT | toast "Save failed" with the raw error text | partly | `app/handlers/blueprint_handlers.py:1188-1193` |
| the recipe copy by "ingest" | no try around the copy; the error is not turned into a message (REASONED) | NO | `app/handlers/ingestion_handlers.py:50` |
| the bundle import | I saw no try around the writes (READ, not run) | NOT VERIFIED | `app/modules/bundle_importer.py:261-266` |
| the clean-up at start | not inside a try (READ) | NO (can stop the start) | `app/src/bootloader.py:201-216` |

Suggestion: the "off" default ships together with one plain sentence at each of these places. Not built; it is a separate piece of work.

## 5. The switch (names and scope are proposals; the default, off, is decided)
Names (not decided): `write_test_at_start: true|false`; or `startup_checks.write_test: on|off`; or `check_places: write|read|none` (three levels; "read" still checks that the places exist and can be read, without writing; this fits best with section 4).

| scope | for a deployer | for a system administrator |
|---|---|---|
| one switch for the whole deployment | simple, one line in the console | cannot object to one place only; switches all off |
| one key on each place | exact | more keys; a place can be forgotten; more to test |
| both | complete | two stores that can disagree; not simple |

My view (MINE): one switch for the deployment now; a key per place only when a real case appears.

## 6. What a test of a deployment would show
| switch | place | the test must find |
|---|---|---|
| on | writable | passes; one console line per place; the folder listing is the same before and after |
| on | not writable | the start stops with a sentence naming the place, the cause and who fixes it; non-zero exit; no page |
| on | missing | stops with "does not exist"; nothing created |
| on | a link | passes and says where it ends |
| on | `read` place | never written |
| on | removal made to fail | warning with the file name; the app starts |
| off | any | the app starts; one console line says the test was skipped; no test file at all |
| off | not writable | the app starts; the FIRST write at each place of section 4 gives the plain error (today the sessions folder fails this test: that is the point) |
| both | the switch value is misspelled | the deployment file is refused with the key named; no silent default |

What cannot be tested without the real system: Galaxy, a cluster scratch file system, a network file system, Posit Connect, a sync client, an antivirus (section 9). The first start on the real system is that test; with the switch on, the console line is what shows it. Trap: many test machines run as the superuser, for whom a read-only folder is not read-only; tests must use a read-only mount or skip.

## 7. The sentences for the operator's console (proposals)
- Passed: `Write test: place '<name>' (read_write) at <path> accepted a test file; the file has no name and is gone.` For a link: add `The place is a link: <declared> -> <real>. The app writes in <real>.`
- Cannot be written: `Deployment failed: place '<name>' (read_write) at <path> cannot be written: <cause>. The app writes <what> there. Fix: give the user that runs the app (<user>) the right to write in this folder, or declare the place read. Who: operator.` Causes: permission denied; no space or quota; read-only file system.
- Missing: `Deployment failed: place '<name>' at <path> does not exist. Create it or correct the path in the deployment file, then restart. The app does not create it.`
- Removal failed: `Write test: place '<name>' is writable, but the test file <name> could not be removed: <error>. Remove it by hand.`
- Skipped: `Write test skipped (write_test_at_start is off): places are not checked until first used. A place that cannot be written will show as an error at the first save.`
- Information, optional: `Place '<name>' can be written by other users.` `Place '<name>' is on a file system mounted noexec.`
- For the visitor, when a first save fails with the test off (this is the plain error D-0340 asks for): `Your work cannot be saved on this server (the saving place is not writable). Tell the operator.` No server path, no Python error. Today the notices carry both.

## 8. The choices for you, ranked
| # | the question | the options | what the check recommends | reconsiders a decision? |
|---|---|---|---|---|
| 1 | Does "off by default" ship together with the fixes of section 4? | (a) together; (b) the switch first, the fixes later | (a). With (b) the default "off" leaves the blank page: a half fix | no |
| 2 | Does the switch also cover the write test that already happens at every opening of a recipe? | (a) yes, one switch for both; (b) no, the opening keeps its test | (a) is consistent, otherwise "off" still writes at each opening; (b) is safer for the stored tables. One function must serve both either way | changes today's behaviour at the opening (`opening_build.py:160-167`), not a ledger line |
| 3 | Does the app ever create a missing place? | (a) only report it; (b) create it | (a): a mistyped path would otherwise silently make a new tree. Today the app creates (`session_manager.py:274`) | touches D-0417 reading (b) ("exists"), which you did not confirm |
| 4 | A place that is a link | (a) followed and reported; (b) refused | (a); (b) only as an option the deployer switches on | no |
| 5 | Name and scope of the switch | section 5 | one switch for the deployment, three levels (write, read, none) | no |
| 6 | When a tested place fails | (a) stop the start; (b) warn and go on | (a) when the test is on; the operator asked to test it | no |
| 7 | Optional information lines (other users can write; noexec) | (a) include; (b) leave out | (a): information only, no stop | no |
| 8 | A time limit for a network file system that does not answer | (a) none; (b) a limit, then "did not answer" | (b) is useful, but I could not measure a real one; open until tested on a cluster | no |

## 9. Not verified
- Network and cluster file systems (NFS, Lustre, GPFS): support for unnamed files, the fsync time, quota errors at close, hangs. Not run.
- Galaxy, Posit Connect, a container runtime, the cloud sync client (Insync), an antivirus: not run.
- A second real user (no administrator rights here): a file of another user at the same name. The kernel rule (exclusive creation fails on any existing name) was shown with my own file only.
- Windows and macOS: not checked; the app's targets are Linux.
- That the standard library falls back correctly where unnamed files are not supported: read in its source only.
- That the bootloader's fatal path is the right exit for a failed place: seen for absent data, not run for a place.
- Only one viewpoint did this check. A second look should read the test function when it is written and run it on a real shared system.
