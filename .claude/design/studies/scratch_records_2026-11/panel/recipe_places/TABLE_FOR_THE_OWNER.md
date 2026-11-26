# Where recipes live, who may write, names with a date: one table for the owner (coordinator, 2026-11-20 night)

Her order: D-0393, D-0394 (and her words: "I think you can have part b and d also checked by the coordinator agents to be sure"). Sources in this folder: `BRIEF.md` (what is decided, the facts), `architect.md` (ran a recipe with a dated hyphenated name through the checker, the load gate and the build), `scientist.md` (ran the fingerprint of a recipe under two names), `user.md`. Nothing is built or changed. The panel recommends; she decides.

## Flagged first
1. **The app cannot tell users apart.** No login, no identity anywhere in the code; each deployment has ONE user-data folder for everyone. So "only specific users may modify the common recipes" can only mean today: a separate app (its own deployment and app features) for the person who maintains them. And "the user's own directory" is really own only when one person uses the app (a local PC); on a shared server it is a folder shared by everyone of that app. An identity from Galaxy or Posit Connect is "a connector task for later" (ADR-091), not verified on those platforms.
2. **A dated copy of an unchanged recipe is a new recipe for the machine.** The recipe's fingerprint includes its file name (run: same bytes, two names, two fingerprints). A session saved against a draft does not open against its dated final version.
3. **A recipe is several files.** Four shipped recipes include fragments from the demo recipe's folder. A dated version that shares fragments with another recipe changes silently when that folder is edited. A dated version must be self-contained: every file it reads copied with it.
4. **"Remove the old file by hand"** (same-day correction, D-0390) is possible only for someone who reaches the folder: not a normal user on a shared server (reasoned, not verified).
5. **BLUEPRINT ignores the deployment's recipe folder** (a fixed folder of the repository); the recipe upload has code and no control on screen, and would replace silently.
6. **The default recipe is the first of an unsorted list**: with dated names present, the scratch run opened another recipe than the demo. A small fix, needed whatever is chosen.

## Verified
- A hyphen in a recipe name works through discovery, the load gate, the checker, tier 1, a join through the renamed folder, tier 3 and the cache file names. Not run: the browser, session save and restore, the export, the audit folder.
- "Newest per name" can be computed: the date is the ISO date after the last underscore; a name without it is "undated" and is its own name. Sorting needs two keys (name, then date newest first); a plain sort by text gives oldest first.
- Her direction b holds: leaving the demo recipes, the templates and the Gallery examples undated breaks nothing (by reading); the date rule belongs to the ACTIONS (final save, upload into the common place), not to what the app accepts to read.
- Her direction d is coherent: "a dated new file at the final save" and "replace for a typo" are different actions in different places.

## The models
| Model | Where recipes are | Who writes | Pro | Con | Viewpoints |
|---|---|---|---|---|---|
| M1. Common place read-only for the app; own recipes in the user-data folder (`recipes/`) | Both read; each entry marked common or own; the same name in both is refused | The app writes only to the own place; the common place is filled outside the app by the maintainer | Nothing is ever written into the common place; simplest to test; a first part that leaves a working app | The final dated save reaches the common place only by hand, unrecorded; a user cannot correct a typo in a common recipe | Architect: first step |
| M2. Drafts in the own place; "Save final version (dated)" writes `name_<today>` into the common place, only in an app set up for the maintainer | As M1, plus the app writes dated files into the common place | Drafts: anyone of that app; final versions: the maintainer's app | The step from draft to final is recorded ("made from draft with fingerprint H"); dated files in the common place are never replaced; closest to her words ("export for production") | The largest work; the common place becomes writable (documents say read-only today); the list must refresh without a restart; without a login everyone who opens the maintainer's app can publish | Scientist and user: recommended. Architect: second part, after M1 |
| M3. One place only, the user's | One folder | Everyone | Smallest change | On a shared server everyone can overwrite everything: against D-0394 | All: only for one person on a local PC |

All three viewpoints: **M1 first, then M2 on top of it** (M3 is the case where both places are the same folder).

## Her decisions (one at a time, when she asks)
| # | Question | Options | Recommendation |
|---|---|---|---|
| P1 | The model | M1 then M2; M1 only; M3 | M1 then M2 |
| P2 | "Specific users may modify the common recipes" while the app has no login | A a separate maintainer app (deployment and app features) is the only writer; B wait for an identity from Galaxy or Posit Connect (to verify on the platforms); C the operating system's folder permissions decide (the app tries to write and reports a refusal plainly) | A now; C as the safety net; B later |
| P3 | The same name in the common and the own place | refused (neither is picked); own wins; common wins | Refused, with a plain line |
| P4 | Old versions | a subfolder "older versions" filled by the app at the final save, with a switch "Show older versions"; or all versions in one list; a version moves WITH its files; a session made on an old version still opens it and says "older version, the newest is X"; never a silent fall-back to the newest | The subfolder with the switch (her idea), moved by the app |
| P5 | A second correction on the same day in the common place | refused, the maintainer removes the file outside the app (her words); a time added to the name (changes D-0391's form); a suffix (breaks the sort) | As she said; with a written procedure for the maintainer |
| P6 | In the own place: replacing a file | "Replace" with the line "N saved sessions made with it will no longer open; results already exported are not affected"; or the old file goes to older versions instead of being deleted | Replace with the warning (D-0394 allows it there) |
| P7 | What identifies a recipe for the machine | A the fingerprint of the files with their names (as built: exact; a rename or a comment makes a new recipe); B the fingerprint of what the recipe contains once read (ignores names and comments; the audit copy already uses it); both recorded, with the rule named | Both recorded; B decides "the same recipe" for a session (this answers her open point "what counts as modified": steps AND plot settings count, comments and names do not; a steps-only rule would let a published picture change silently) |
| P8 | A dated version is self-contained | every file it reads is copied with it (one shared function for the final save, the copy to the own place and the audit recipe); or fragments may stay shared | Self-contained |
| P9 | The bundle import's own name (`<id>_imported_<timestamp>`) | keeps it (an import is not a production recipe); follows `name_date`; the exported original keeps its dated name and is refused if a different file already holds it | To decide with P3 |
| P10 | A copy of the recipe kept with each session or audit | yes (the session can always show what it was made with); no (the fingerprint only) | Yes (D-0340 already places the audit recipe in the session's folder) |
| P11 | The words on screen | "Save final version (dated)" rather than "export for production" (the app already has an export of results); "Lab recipes" and "Drafts / own recipes" as two headings; "Shared drafts of this app" on a shared server, never "My recipes" | As proposed by the user viewpoint |

## Steps that are safe whatever she chooses (no new decision; can be built first)
1. A small module that splits a name into name and date and gives "newest per name" (tests).
2. The list of recipes and the default sorted (flag 6).
3. One function that gives the path of a recipe, replacing the 13 places that rebuild `folder/<id>.yaml` (needed by every model).
4. BLUEPRINT reads the deployment's recipe folder instead of a fixed one (flag 5).

## Not verified
Posit Connect and Galaxy: whether the recipe folder is writable, whether the user-data folder persists, whether a user identity is supplied; a hyphenated name in the browser, in a session, in an export, in an audit folder; the cost at start of checking every kept old version (the check of a recipe only when it is selected, D-0184, is not built).
