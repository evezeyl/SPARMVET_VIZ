# Can recipes be versioned? One table for the owner (coordinator, 2026-11-20)

Her question: "could we track version of the recipes ? that could be a solution then if a recipe is versionned the latest version is proposed but that would allow to reopen a recipe from the old version".
Sources: `FACTS.md` (scout, read from the code), `architect.md` (architect and developer; ran checks), `scientist.md` (ran a small check), `user.md` (read the facts only). Nothing is built. The panel recommends; she decides.

## Flagged first
1. **Today a session saved on a recipe that was edited afterwards opens with a warning**, and the audit steps run on a recipe they were not made on. Her decision (D-0362: refuse) removes this; it is not built yet. All three viewpoints say: build it first.
2. **A recipe can be overwritten with no trace**: the upload of a file with the same name replaces it silently, and Blueprint saves in place. The app keeps no old recipe text anywhere (not in the session folder; a Publication export holds no recipe).
3. **`info.version` is free text that nothing reads.** A screen that shows "version 1.2" would be trusted although the content may have changed. A version shown to the user must come from the content.
4. **"Other content" has two meanings today.** The recipe hash used by sessions is a hash of the file bytes: a corrected typo in a comment changes it. A second hash exists of what the recipe does (comments excluded). With the byte hash, the refusal of D-0362 would refuse a session after a comment-only edit. Her earlier decision (D-0328) already distinguishes "changed in what it does" from "changed only in comments" for the audit recipe.
5. **The main finding of the architect: the decided audit recipe file IS already a stored old version.** It is a full copy of the original as it was, plus the audit steps, with a hash check at reopening (D-0332, D-0328, D-0331, D-0333; decided, not built). Once it is built, the old recipe of every audited session is on disk. What is NOT decided: whether an audit recipe may be reopened on its own copy when the original has changed since.

## The options
| Option | What the user sees on the day she reopens old work | Pro | Con | Evidence | Viewpoints |
|---|---|---|---|---|---|
| V0. No versions. The refusal (decided), with the refusal screen made useful | "The recipe 'X' has been modified since you saved this session. Nothing was deleted: your N audit steps with their reasons are listed below. Save the list, reanalyse with the current recipe and add the steps again." | Decided; simple; no old recipe is ever continued by mistake | She does not see WHAT changed; the figure as it was is lost unless exported; redoing the steps by hand can go wrong silently (a renamed column, a filter that now removes other rows) | Session files hold the steps and hashes, no recipe text (`session_manager.py:374-387, 508-533`) | All three: build first. User and scientist: the list of steps with reasons on the refusal screen is the minimum |
| V1'. The audit recipe file is the stored old version (no new store) | "This audit uses the recipe 'X' as it was on 17 November (an older version). The current recipe is different: it changed in what it does / only in comments." Then: continue on the older version, or move the steps to the current recipe and check them one by one | Uses what is already decided; one copy, hash-checked; works where the recipe folder is read-only (the session folder is the user's own); proves which recipe made a figure | Only audited sessions are covered (a session without audit steps keeps no recipe text, and needs none); a fixed mark "older version" must be on every figure and export; an old copy may not run on a newer app (D-0207: the app converts nothing) | Decided lines above; 8 to 60 KB per session measured by the architect | Architect: recommended, after V0. Scientist: recommends a snapshot per session (the same idea; the audit recipe is its natural home). User: yes as the next step, only with the fixed mark and the statement in the export |
| V0b. Warn the AUTHOR at save and upload | In Blueprint or at upload: "3 saved sessions use this recipe. They will be refused after this change. Save under a new name?" | Cheap; a new name is a new recipe, old sessions keep working on the old file | Does not cover hand edits or the operator replacing files; needs the app to see the sessions of other users | Blueprint saves overwrite in place (`blueprint_handlers.py:1154-1195`); upload overwrites silently (`ingestion_handlers.py:44-51`) | Architect: third step. User: asked for exactly this |
| V2. The app keeps every version of every recipe; the selector offers the latest, an old one can be opened | A selector with "latest" and earlier versions | The full history, for every recipe, also without an audit | Two contents under one name: every place that shows the name must also show "older version", and one missed place makes a published figure point to the wrong recipe; hand edits and operator deployments leave holes while the history looks complete; needs a store, a cleaning rule, a lock for several users; the recipe folder may not be writable for users | The file name is the id (ADR-092); one folder scanned (`bootloader.py:414`) | All three: not now. User: "too complicated for one sentence" |
| V3. Git keeps the versions | Nothing on the user's screen | Standard tool for whoever maintains the recipes | Uncommitted edits are exactly the ones lost; needs git in every deployment; the user cannot reopen anything herself | No doc says a deployment's recipe folder is under git | All three: a good practice for maintainers, not the answer |

## Where the viewpoints agree
- Build the refusal first, with the list of audit steps and reasons on the refusal screen.
- Then the old version lives with the user's work (the audit recipe), not in the recipe folder.
- Not V2, not V3.
- A version shown to the user comes from the content and is said with a date ("as it was on 17 November"), not with the author's free text.

## Where they differ
- Scientist: also record the app version (commit) in the session; sessions record none today. Cite a result by recipe name, `info.version`, a short content hash and the app version; a mismatch between `info.version` and the content is shown as information, never a refusal.
- User: on an older version, a mark that cannot be closed on every figure and on the export; export allowed after a plain confirmation.
- Scientist found (ran): a change of `info.version` alone changes the "what the recipe does" hash, so the `info` block would have to be left out of it, or the sentence over-alarms.

## The coordinator's recommendation
V0 now (decided, D-0362), with the steps and reasons on the refusal screen. V1' when the audit recipe file is built (it is on the build list already). V0b after. V2 and V3 not built.

## What she would decide (when she asks; none blocks a running build)
1. A session is refused when the recipe's BYTES changed, or only when what the recipe DOES changed? (bytes: simple and strict, but a comment typo refuses the session; what it does: fair, needs the content hash to leave out comments and the `info` block)
2. May an audit recipe be reopened on its own copy when the original has changed since? (yes: old work can be finished and reproduced, with a fixed mark "older version"; no: one rule, always redo on the current recipe)
3. Should the app warn the author at save and upload that saved sessions use the recipe? (yes: fewer surprises; no: less to build)
4. Is V2 (a full history) worth a study later? (the panel says only if a need remains after 1 to 3)

## Not verified
Whether the recipe folder is writable on Posit Connect or Galaxy; how an audit recipe will be named and opened; how the content hash is computed for the three-way sentence; an old copy on a changed engine; which YAML loader reads recipes (the scientist saw a possible crash of the content hash on an unquoted `on:` key with plain PyYAML: to check when the hash is built).
