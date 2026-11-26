# Deployment study: viewpoint of the user who is not a developer, and of the person who deploys (panel-user, 2026-11-21; filed by the coordinator as a faithful digest of its full report; it read the brief, ORDER, FACTS, the recipe places table and the ledger lines; no code read by itself)

## Summary
1. A person at the screen needs three ideas only: a place is "shared" (read, not change), "mine" (read and change), or "this session only" (nothing is kept). The deployment file must produce exactly these words on screen.
2. Design B (two layers, shared and own) can be said in one sentence and one picture. Design A (a list of named places) is more general but shows the user too many places unless the screen folds it into the same three words.
3. Design C (keep the five keys) hides the most: a locked place is locked only by the operating system, and the person gets no reason when a save fails.
4. Without a login, "mine" is false on a shared server. The screen must say "shared by everyone who uses this app", and the deployment file must force that wording.
5. Two things break the person's work today and come first: a read-only place stops the opening of recipes (`opening_build.py:249-254`), and a session record is written at every opening (`home_theater.py:1515-1578`).
6. Recommendation: B on the screen, built on A's list underneath, with a small fixed set of roles: "shared, locked"; "own, open"; "this session only"; and for data "given by the pipeline or API".

## The picture, the same on every deployment
```
Recipes                          Data
 [Shared - locked]      3 files   [Shared - locked]        12 tables
 [Mine - you can change]   2      [Mine - private to you]    1
```
A block that does not exist in a deployment is absent, never empty and unexplained.

## Sketches of the deployment file (key names are the viewpoint's, to show the look)
Design A:
```yaml
places:
  - {name: lab-recipes, holds: recipes, access: read, path: /srv/consortium/recipes, shown_as: "Shared recipes (you cannot change these)"}
  - {name: mine, holds: [recipes, data, sessions, audit], access: write, path: ~/sparmvet, shown_as: "My files"}
# static page:   site (recipes, data; read) + scratch (sessions, tables; temporary)
# Galaxy:        job-data (data; read; from: galaxy_job_folder) + job-out (sessions, audit; write)
# API:           from-pipeline (recipes, data; read; from: api, token from the environment) + scratch (temporary)
```
Design B:
```yaml
shared: {recipes: /srv/consortium/recipes, data: /srv/consortium/data, access: read}
own:    {path: ~/sparmvet}     # recipes, data, sessions, audit under it;  "own: none" for a static page
```

## What the screen must say (sentences proposed, not decided)
| Where | Sentence |
|---|---|
| A locked group of recipes | "Shared recipes (you cannot change these)" |
| An open place, one user | "My recipes" |
| A shared server without login | "Recipes saved in this app (everyone who uses this app sees them)", never "My recipes" |
| Save on a locked recipe | button shown disabled with the reason: "This recipe is shared and locked. Save a copy in My recipes." |
| A save refused by the system | "Could not save: the folder <name> does not allow it. Ask the person who installed the app. Nothing was changed." |
| After any save | "Saved in <place name> as <name_date>." |
| A name in two places | "A recipe named <name> exists in Shared and in Mine. Choose which one you want; the app does not pick one." |
| On every recipe and data file | a quiet label: Shared / Mine / Given by the pipeline, plus the file date |
| Nothing writable | "Nothing is saved on this installation. Your session ends when you close the page." |
| Overwrite (own place only, D-0394) | "Replace <name>? <N> saved sessions made with it will no longer open. Results you already exported are not changed." |
| Data Import overwrite (OPEN) | "A table named <name> is already in <place>. Replacing it deletes the old one; there is no copy. Replace / Keep both / Cancel." |
| Private data | "This table comes from your private place. It is not part of the shared place." |
Words to avoid on screen: provider, connector, volume, mount, read-only, writable, path, API.
Only three messages interrupt the user: replace, a name in two places, "cannot save". Everything else is a quiet label.

## Per use case: what the person must be told
- Static web page and web page with exploration: "This page shows one analysis. Nothing you do here is saved on the server. Download to keep a result."
- Pipeline on Galaxy: "The recipe and data were given by the pipeline. You cannot choose others."
- Shared and private data: "This file is in your private place only. It is never copied to the shared place."
- API: "Given by <source> on <date>. It cannot be saved here."
- A place changed while the app runs: "The folder has changed since you opened the page: reload the list."
- A consortium recipe updated by someone else: "A newer version of this recipe exists: <name_date>. You are using <name_date>."
- Exports are browser downloads and work in every deployment: say so on screen.

## What the person who deploys must tell users (one page)
Which places exist and whether each is locked or open; whether anything is kept after the page closes; whether others can see your saved files (yes on a shared server); whom to ask when a save is refused (a contact in the deployment file, shown in the message); how a locked recipe gets updated. Suggestion: the deployment file carries one line per place, "what users are told", written by the deployer.

## Pitfalls
A silent pick when a name is in two places; "mine" on a shared server (sensitive metadata seen by others); private data going into an export unnoticed; a bundle import writing into the shared folder (`bundle_importer.py:263`); a stale list when a place changes; too many places on screen; a typo that makes a place writable (check at start and show "Writing to <place>: allowed / not allowed").

## Decisions touched
D-0340 says "no new configuration variable for now": designs A and B add configuration, so they reconsider that line (flagged). D-0390 to D-0394 and D-0102 are respected.

## To decide first (ranked)
1. What a deployment with nothing writable does: keep results for the session only and say so, or refuse.
2. The meaning of "mine" with no login.
3. The same name in two places: show both (its recommendation), or the deployment file says which wins.
4. Where a bundle import and Data Import write: only the own place, never the shared one.
5. Names of imported recipes and "newest per name" in the selector.
6. How much the deployment file says to the user (a line per place).
Can wait: the API source, offline copies, the platform identity for Galaxy and Posit Connect, the Gallery index.

## Not verified
Every code fact is from FACTS.md. What the browser shows today; whether an export includes private data; whether Galaxy, IRIDA or Posit Connect supply an identity or a writable folder; whether users understand "locked" and "shared" (needs real users).
