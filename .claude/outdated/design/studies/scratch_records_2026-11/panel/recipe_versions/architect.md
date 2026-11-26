# Recipe versions: architect and developer viewpoint (2026-11-20)

Evidence labels: READ (file:line), RAN (scratch script `tmpAI/panel/recipe_versions/architect/keys_check.py`), INFERRED (follows from the design, not run). Tags: DECIDED / CONFIRM / OPEN / MINE.
I only recommend. The owner decides.

## 0. Flags first

1. **A silent change of a result or of a figure's origin.** If two contents share one id (V2, V3), "recipe X" in HOME, in an export, in a figure caption and in the report no longer names one recipe. Every place that shows the id must also show "an older version" and the short fingerprint. If one place is missed, a published figure points to a recipe that no longer exists under that name. MINE, INFERRED. This is the main risk of V2 and V3.
2. **A hidden step.** A history store written by the app sees only the versions the app saw. A hand edit (no hook, no check at open: FACTS "Who writes a recipe file"), an operator deployment, or an edit made while the app was closed leaves a version that was never stored. The history looks complete and is not. The user must be told this. READ for the writers (`blueprint_handlers.py:1154-1195`, `ingestion_handlers.py:44-51`); INFERRED for the gap.
3. **Two decided lines that may disagree (CONFIRM).** D-0362 refuses a session when the recipe has "other content". D-0328 and D-0339 give the user three cases: the original has not changed, changed in what it does, changed only in comments. R, the hash that makes the session key, counts the bytes, so a comment-only edit changes R (READ `cache_keys.py:327-338`). RAN: changing `info.version` and `info.description` in six shipped recipes leaves every table key part equal, while R is still a hash of the bytes. So a refusal by R would refuse a session after a typo fix in a comment. Which test does D-0362 use: R (bytes), or the fingerprint of what the recipe does (D-0339 `original_content`, computation not decided)? This must be answered before D-0362 is built.
4. **Does not reconsider a decision by itself:** V0 and V1 (as the audit recipe). V2 and V3 stretch D-0362 ("reconstructing the old recipe is not decided"), D-0186 ("changing a recipe is a failure"), the spec line `recipe_format_spec.md:266` (`info.version` stays the author's own) and ADR-092 (one id per recipe). None of these is contradicted, all are stretched.

## 1. The finding that changes the question

The audit recipe that is already decided is a recipe snapshot:
- D-0332: the file is "written by copying the recipe's files" and adding `audit_steps` after the original block. Comments are kept (D-0320).
- D-0328: "a copy of the original as it was when the audit started"; the user is told if the original "has not changed, has changed in what it does, or has changed only in comments".
- D-0040: "the copy is the source of truth".
- D-0324: the export holds the audit recipe.
- D-0331 and D-0333: a hash of the audit recipe's exact bytes is checked at reopening.

So for every session that has audit steps, the old version of the recipe is already stored, in the session's audit folder (D-0340), once slice C is built. A second store for the same content (V1 as a separate snapshot) would be two copies of the original that can disagree. MINE, INFERRED from the decisions. Nothing of this is built (READ: no code reads `audit_of`; `grep` over `app` and `libs` finds it only in tests of another name and in docs). The audit copy lives in memory only (`audit_copy.py` docstring, `cache_keys.py:408-417` "PROVISIONAL").

What is NOT decided and decides everything: **whether an audit recipe is reopened by itself (from its own file) or re-derived (the session's steps re-applied on the current original).** D-0362 is about the second. D-0328's three sentences only make sense for the first (the audit recipe is opened while the original has changed). This is OPEN, and it is exactly her question.

## 2. V0: no versions (D-0362 as decided)

What it does: refusal with a plain line; the user redoes the audit on the new recipe.

What already works without versions, today (READ, `bundle_importer.py:219-276`, `export_handlers.py:1496-1502`):
- The export bundle (reproducibility mode) holds one recipe, merged and without comments, plus the data. Import writes it as a NEW recipe `<id>_imported_<time>.yaml` with a new id, visible after a restart. It reopens the result, not the session. It is a second recipe, not "the old version of X". If the bundle's recipe uses old action names it is refused (D-0207, "the app converts nothing").
- Publication mode has no recipe.

What will work once slice C is built, IF the owner decides the audit recipe is reopened by itself (INFERRED):
- An old audit reopens on its own file, whatever the original became. Fragments are inside (copied files). The tamper check (D-0331) works. The user reads the D-0328 sentence, which is "an older version" in her words.
- Reproduction: the same data (data hash in the session key) and the same recipe bytes give the same table keys (the keys read the resolved recipe, `cache_keys.py` docstring, READ).

What will NOT work:
- A session with no audit steps: nothing is stored, but nothing needs to be (exploration is not saved).
- An audit recipe of an older FORMAT or with renamed actions: refused (D-0207, D-0354 format 1). No conversion.
- An old original that has no audit (just "open the old version of the recipe"): not stored anywhere except bundles and Blueprint zip downloads.
- An audit whose data changed: the data warning stays (D-0186: changing data is not necessarily a failure).
- The sessions saved today carry no recipe text and no app commit (READ `session_manager.py:370-395`, no commit field). Those cannot be reconstructed, and D-0312 already removes the pre-redesign sessions.
- Sessions in `user_data`, in a multi-user deployment, are not seen by the recipe's author: nobody can count who is affected by an edit.

Pros: no new store, no new vocabulary, nothing to clean beyond sessions (`delete_session` exists, `session_manager.py:770`). Cons: the answer to her need depends on a point not decided (reopen by itself or not). Effort: none for V0 itself.
Cost of the refusal alone: a user loses an audit they cannot recreate if the recipe author edited meanwhile. D-0362 accepted this ("reanalyze"). That cost is information the owner needs.

**V0b (a small addition, MINE):** when an author saves over a recipe (Blueprint) or uploads over it (`ingestion_handlers.py:44-51`, silent overwrite today), the app says plainly that sessions saved against the old content will be refused, and offers "save under a new name". A new name is a new id (ADR-092), and sessions are bound to the id, so the old sessions still open on the old file. This gives "latest proposed, old reopenable" through two files, with no mechanism. The author chooses; the app informs. It cannot count other users' sessions (see above). Hand edits are not covered.

## 3. The options

### V1: the session keeps its own copy of the original file set
- Identity: R of the file set (already the session key's first half, verifiable with `sha256sum`).
- Pros: no change to the recipe folder; works where the recipe folder is read-only (the session folder is in `user_data`, "Must be writable", `deployment_template.yaml` location 4; the template says nothing of the recipe folder being writable: READ; Connect's content folder: I could not verify). Lives and dies with the session (delete, zip export and import already move the whole folder: `session_manager.py:643-660`, so a session zip carries its recipe to another machine, where R never matches today). Storage: 8 to 60 KB per session for the shipped recipes (RAN `stat`).
- Cons: for audited sessions it duplicates the audit recipe's original block (two copies that can disagree) unless it IS the audit recipe. For non-audited sessions it stores something nobody needs. Two sessions of one recipe store the same bytes twice (small).
- Couples: the session record format (`SESSION_FORMAT_VERSION`), the importer's zip checks (D-0283 limits), the loader (needs a way to read a file set from another folder: `ConfigManager(path)` loads by path; `!include` may reach up to `project_root_of(path)`, the nearest folder with a `pyproject.toml`, else the recipe's folder (READ `config_loader.py:44-80`), and there is an `include_root` argument; fragments outside the recipe's folder are possible in principle, none in the shipped recipes (RAN grep), but a copy would have to keep the relative layout).
- The ADR-092 problem: the loader refuses `id:` different from the file stem (`data_analysis_recipe_validator.py:436-442`), so the snapshot file keeps the stem `<id>.yaml` in its own folder. Its id equals the live recipe's id: the same id on two contents, flag 1.
- Effort: M. Risk: low if it is the audit recipe, medium if separate.
- **V1' (MINE): V1 realised as the audit recipe.** No new file. The only new thing is a decision: an audit recipe can be opened by itself and is marked "an older version of this recipe" when `audit_of` says the original has changed. Cost: the identity of an audit recipe written to a file is not decided (`cache_keys.py:408-417`, PROVISIONAL), and the `audit_of` fingerprint is not decided (D-0328, D-0339). Both are needed anyway.

### V2: versions in the recipe folder (history keyed by hash and/or `info.version`)
- Identity: only R is portable and checkable. `info.version` is free text, in 14 of 16 shipped recipes, read by nothing (FACTS), Blueprint writes "1.0.0" at creation and nothing bumps it; the spec says it stays the author's. Two contents with the same string is silent. A counter (v1, v2, v3) differs between two deployments (INFERRED). So: R as the key, `info.version` and the save date shown as labels only.
- Where: the scan reads one folder, `glob("*.yaml")` (`bootloader.py:414-415`), so a history subfolder is not scanned, good. But writing in the recipe folder needs a writable location the deployment does not promise. A history in `user_data` is per deployment and per user space, not with the recipe.
- When: a Blueprint save and an upload are the only moments the app owns. A hand edit or `git pull` is seen only at the next open (the app already reloads an open recipe on change, `cache_keys.py:483-506`), and then the previous bytes are gone. So the store is "versions the app has seen", flag 2. To keep the version before the overwrite, the app must copy at the start of the save. For Blueprint and upload that is possible; for hand edits it is not.
- Fragments: the file set is the `loaded.files` list, hashed as read (`cache_keys.py:327-338`). To be sure the stored bytes are the hashed bytes, the copy must come from the same read, not a second one (INFERRED, a race otherwise).
- Engine: an old version on a newer app is subject to the same gate: format number, renamed actions (D-0207). The app converts nothing. So a stored version is not always openable. The user must be told BEFORE offering it ("made with commit X, cannot be opened by this app"). The history entry should record the app commit at the time (D-0208: the version is the commit); sessions do not record it today.
- Stored tables: keys are per table and content-based (`cache_keys.py` docstring; RAN: a change outside the tables leaves every part equal). Two versions that differ in one table share the other tables' stored tables. Nothing to add. But the cache is swept when the cache version changes (`anchor.remove_tables_of_other_version`), so after an app update an old version is rebuilt from data, not read: reproduction is rebuild plus compare.
- Reproduction of an old result: needs the old file set (V2), the same data (data hash), AND the same app/engine versions (E part of the key). The recipe history gives one of three. The export already writes `git_commit` (`export_handlers.py:214`).
- Hand-edited rule (D-0331): a history in a user-writable folder can be edited. A content-addressed store (key = sha256 of the stored set) lets the app check at read and refuse a mismatch, with the same plain line as the audit recipe. Required, not optional.
- Growth and cleaning: small per version (8 to 60 KB), but nobody owns the cleaning (no sweep for recipes exists; `delete_session` is only for sessions). Needs a rule and a command, or "never delete" stated. Multi-user: a shared recipe folder written by the app at user save time can be written by two users; two writers need a lock (INFERRED).
- Selector: it lists file stems; a "latest + older" choice adds a second dimension to HOME, which is not decided (D-0184: a recipe is checked when selected, not all at start; a history of N versions means N checks if listed).
- Pros: answers her question literally. Cons: flag 1 and 2, the writable-location issue, a new "version" concept next to the git commit (D-0208), and the selector. Reconsiders: the stretch in flag 4. Effort: L (store, loader from store, selector, read-only open, marks everywhere, cleaning, tests). Risk: high.
- Tests without a browser: yes. Store and restore round trip equal R; tamper detection; fragments outside the folder; a missing fragment; the gate refusal of an old format; a hand edit seen as a version at open. All pure Python.

### V3: git as the store
- The app would need the git binary, write access to the recipe folder's `.git`, an author identity, and a commit at each save. Hand edits are in the working tree, not in a commit, so R maps to no commit until the app commits on open (writing on read). Posit Connect and Galaxy deployments are not repositories (INFERRED; the template says nothing). Locks (`index.lock`) with two users.
- It would be a second way to do the same thing beside the app's own R (rule: one authoritative way).
- Pros: authors who already use git keep their habit. Cons: heavy, fragile, not portable. No recommendation. For authors who use git themselves nothing prevents it: the app only has to show R (verifiable with `sha256sum`) so that they can find the file in their own history.

## 4. What an audit or test would not catch
- A place that shows the recipe id without the "older version" mark (flag 1): only a list of all places and a test per place.
- A hand edit never stored (flag 2).
- A fingerprint that changes with a comment while the sentence says "comments only" (flag 3): would be caught only if the test uses a comment-only edit on a real recipe.
- A session zip imported on another machine: the id exists there with other content, the session is refused (D-0362) although the zip could carry its recipe.

## 5. Recommendation

**Not V2 or V3 now. Take V0 plus V1', in this order.**
1. V0 stays as D-0362 decided, after the owner answers flag 3 (which hash decides "other content").
2. The audit recipe (slice C) is the store of the old version for audited sessions. One decision opens her wish without a new store: "an audit recipe can be reopened by itself, marked an older version".
3. V0b: the author is told at save and upload what the edit does to existing sessions, and offered "save under a new name".
4. If after this a real need remains for old versions of recipes without an audit (the owner may say), V2 can be studied with a prototype on a copy (agent principle 10), not decided now.

Smallest useful first step: write down (no code) what D-0362's refusal compares (R or the fingerprint) and whether an audit recipe reopens by itself. These two lines decide whether V1' costs anything.

## 6. What the owner must decide (short sentences, each with one pro and one con)

1. When the recipe was edited, is the session refused by the bytes (R) or by what the recipe does?
   - Bytes: simple, verifiable with `sha256sum`; but a typo fix in a comment refuses an audit.
   - What it does: a comment edit does not refuse; but the fingerprint is not decided and needs a definition.
2. Can an audit recipe be opened by itself, from its own file, when the original has changed?
   - Yes: old audits stay reopenable, marked "an older version", no versions store. Con: the user may work for long on a recipe that is no longer the author's, and exports it.
   - No: the refusal of D-0362 stays total; simpler to explain; old audits are lost unless redone.
3. Should the app say at save and upload that sessions will be refused, and offer "save under a new name"?
   - Yes: no new store; the author chooses. Con: it only covers saves made in the app and cannot count other users' sessions.
   - No: nothing is added; the author learns from a user's complaint.
4. Should a real history of recipe versions (V2) be studied?
   - Yes: it answers her literal question. Con: large, with the risks in flag 1 and 2, and the recipe folder may be read-only.
   - Not now: wait for the audit recipe and see if the need remains.

What the user is to be told in the refusal line (not decided by me): which recipe, the date of the session, that the recipe was edited since, and what to do (open the audit recipe if there is one, otherwise redo the steps on the new recipe).

## 7. What I could not verify
- Whether the recipe folder is writable by the app process on Posit Connect, Galaxy or other deployments (the template is silent; no check in code: READ).
- How an audit recipe will be opened and named when written to a file (ADR-092 file name = id vs a file in an audit folder that is not scanned): not decided, not built.
- The computation of the fingerprint (D-0339): not decided.
- Whether a fragment outside the recipe's folder can be copied faithfully by a snapshot: INFERRED from the loader; not run.
- The behaviour of the cache sweep when an old version is reopened after an app update: READ the function name and its caller only; not run.
