# Developer viewpoint, round 2 (2026-11-21)

Labels: verified (run or grep today), reasoned. Read-only; nothing built.
Checked today: 14 files under `config/data_analysis_recipes` contain `source.path` values that start with `./assets/test_data/` (relative to the working folder, not to a place). No `os.access` or `W_OK` exists in `app` or `libs` (grep, non-test).

## 1. Same name in two places
Position: one rule, REFUSE, with both places and both hashes named, neither opened. I drop my "unless identical" doubt and I do NOT support "identical bytes are fine" from the data scientist as a silent merge: if identical, show it as ONE entry that lists both places (the user sees it, nothing is chosen). Reason from the build side: a session key is the recipe hash plus data hash (`session_manager.py:305-308`), so identical bytes give the same key by construction; different bytes with one name cannot be keyed by name alone. I reject "the deployment file says which wins" (user, second option) as the default: it is a search order written in a file. If the owner wants it, it must be a visible per-place word, and the screen and the export must show which place won.
The owner's case: the consortium `amr_2026-11-17` and the user's copy changed. Under `name_date` the copy is a NEW name if the date is new (`amr_2026-11-21`): no conflict, both listed, each with its place label. A copy changed on the same date keeps the same id: refused, and the screen says "Rename or change the date of your copy" (the save refuses to write a same-name file in the own place when the name exists in another readable place: one check in the one save function, so the conflict is caught at the write and never reaches the selector). The user's "show both and let the user choose" is then not needed for recipes; the choice is made by the name, which the user owns. For data tables I support the user's pick by place only if the pick is recorded in the session; otherwise refuse. Changed my mind: yes, moved from "refuse" to "refuse at the write, and at the read show both".

## 2. Nothing writable
(a) Require one writable place, stop at start with a plain message. Cost: small (one probe at start, one message). Risk: a static web page or a read-only container cannot run without a tmpfs declared by the deployer; the owner's static-page case then needs a deployer step. Honest and testable.
(b) Memory or temp for the session, "nothing is saved here". Cost: large. Verified: stored tables and the session record are written at every opening (`opening_build.py:249-254`, `home_theater.py:1515-1578`); a memory mode means a second storage path in the engine, tested in both modes. Risk: the audit (D-0102, D-0315) is lost while the user continues; the system temp folder is shared on a shared server (reasoned).
(c) The deployment file chooses. Cost: (a) and (b) together plus the word. Risk: two behaviours to keep correct for every later feature.
I support (a) first and (b) later only if the owner wants the static page without a volume; then (c) is not needed: (b) becomes a declared place `provider: memory`, so there is still one mechanism and the file says it. If (b) is built, the screen shows "nothing is kept" and the audit panel is absent, not greyed. Changed: I had left it open; now (a).

## 3. The access words
Smallest set in the file: `read` and `write` per place, plus a place KIND (`recipes`, `data`, `user`, `cache`). Not three words: `add` versus `replace` is a rule about names, and it is covered by the same-name refusal plus the owner's separate overwrite decision (D-0394: overwrite exists only in the own place); the overwrite control exists only where the place is `write` and kind `user` or `recipes` of the own place. Keep `add` out of the file now; add it when a deposit directory is specified (a place nobody may overwrite), as a new word then, not a reserved key now.
Mapping to the screen (derived by the app, never written by the deployer, so a label cannot lie):
- `read` -> "Shared (you cannot change these)".
- `write`, one person per process -> "Mine".
- `write` on a shared server -> "Saved in this app (everyone who uses it sees them)", chosen by a file setting `shared_by_all: true` that the deployer must state (see 4); never "Mine".
- no writable place (point 2b) -> "This session only".
The app also probes by writing a file and removing it at start; it states "allowed / not allowed" per place on screen (user's pitfall). Root defeats `chmod`, so the probe must write (verified: no `os.access` exists, so this is new code, not a change).
Disagreement with the architect: he rejects a write probe because it would touch a folder someone else maintains. A probe in a place declared `read` is not made; the probe is only in places declared `write`. Reply: so the objection does not apply.

## 4. Private data
A `private` mark is NOT needed as a mechanism now; a smaller thing is. The least that makes the owner's case safe: (i) the registry has one copy function, and it refuses to copy from a place of kind `user` into a place declared shared or into an export unless the user chose it on screen; (ii) stored tables of data from a user place go under that place (they are derived from the data); (iii) the session stores place id plus relative path, not the server path. That is a kind-based rule (`user` is private by kind), so no flag. `may_export_data` I would add only when the export code is read: I did not verify what `export_handlers.py:1496` does with data (not run). Open: whether the owner wants the choice per export or per place.

## 5. Confinement
No. Read and write only inside declared places (rule L12 of the architect, which I accept). For the 14 shipped recipes with `./assets/test_data/...`: today the path is resolved relative to the working folder. Complete fix, no shim: a test-data place declared in the development deployment files (`kind: data`, `read`), and the 14 recipes change `source.path` to a name inside that place (a scripted pass, with a test that every recipe resolves in the shipped deployment). A recipe that names a path outside every data place is refused at the check with the place list. Risk: the recipes are also read by people outside the repository; the scripted pass is large but mechanical.

## 6. Migration
Yes, one order satisfies both rules if the steps change the INSIDE first and the FILE last. The old five keys stay valid until the last step, then are refused in one scripted pass, no alias and no shim at any point because the registry is built first and the old keys are ONE of its inputs only inside one step, then removed (the pass migrates the 7 files in the same commit as the refusal).
First three steps:
1. Safe, independent fixes: sorted recipe list, `recipe_path()` replacing the rebuild sites, `name_date` module, `python_interpreter` removed (D-0263). No new concept.
2. The pure registry module in `libs/connector/` with its tests (parse, validate, write probe, refusal of duplicates, `ResolvedItem`), not yet used by the app. A tested unit that nothing calls is not a half fix: it is a step.
3. One object `places` handed to handlers instead of `get_location("key")` (44 non-test calls per the architect; 57 in my count, by pattern), reading the OLD five keys through the registry. Then step 4: the `places` block, migration of the 7 files, refusal of the old keys, all in one commit.
Between 3 and 4 the app works and no alias exists (the registry reads the old keys as its input format until step 4 replaces the format; the refusal arrives with it).

## 7. API and connectors
The architect's rule covers "the data is passed directly from the pipeline" (a job folder, a local read place) and does not yet cover "API gives the data and the recipe" (no code exists, `irida.py:40-52`). It is acceptable only as: the provider is a separate step that writes bytes into a local place and records a source record; the app never calls out. Needs recording for reproducibility: source id (host, project, dataset), time fetched, content hash of what was received, and the bytes themselves kept in the place so the hash can be rechecked. Without the kept bytes an API figure cannot be reproduced. I do not support building it before the use case is written.

## 8. D-0340
Respected for the audit folder (it stays inside the session folder in the user place); reconsidered for configuration in general, because the places block is a new configuration. One sentence for the owner: "D-0340 keeps the audit folder without a new variable; the places block is the one new configuration structure, and it replaces the five location keys rather than adding to them. Confirm or refuse."

## 9. What I think is wrong or silent
- Architect: "`user_data` and `cache`: only `replace` or absent" together with "Stored tables ... In `cache`, ... a shared cache between users is safe by construction". Safe for keys, not for privacy: a shared cache of tables derived from private data is a copy of private data in a shared place (see 4).
- Architect: "A user's file with the same id replaces the consortium recipe on that user's screen" is correctly refused; my point 1 adds the write-time check.
- Data scientist: "same_name_in_two_places: refuse_unless_identical". Identical bytes still give two place ids; if the export records one of them silently it changes provenance. It must record both.
- User: "Nothing is saved on this installation. Your session ends when you close the page." True only under (b); under (a) the app does not start. The sentence depends on the point-2 decision.
- User: "the deployment file says which wins" (first-wins by file): a silent change if not shown on every entry and recorded.
- My own first round: I said a `user` place "must be marked private" (flag). I now prefer a kind rule (point 4).

## Still open between us
- Whether (b) memory mode is built at all, or (a) only (owner's static-page case decides).
- `add` as a third word: architect keeps it, I defer it to the first deposit-directory use case.
- Write probe: architect refuses it; I probe only `write` places.
- `private` flag versus a kind rule, and `may_export_data`, until the export code at `export_handlers.py:1496` is read.
- Whether the registry may read the old keys for one step (my step 3) or the owner counts that as a shim.
- Who may choose between two data tables of the same name (user pick recorded, or refuse).
