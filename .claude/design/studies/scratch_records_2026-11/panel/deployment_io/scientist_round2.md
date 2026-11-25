# Scientist and data scientist, round 2 (2026-11-21)

Read: architect.md, developer.md, user.md, my own scientist.md. Evidence: read only; nothing run in this round. Classes: VERIFIED (from a file I read), REASONED, ASSUMED.

## 1. The same name or table in two places
One rule: the app never picks between two. Same bytes (same sha256) = one object, both places listed, both recorded. Different bytes = not opened by name; the screen shows both with place label, date, first 8 characters of the hash, and says "the app does not choose". The user opens one by an explicit act "open the one in Mine"; the choice is recorded (place id and hash) in the session and the export.
Owner's case: a consortium recipe copied and changed is saved as `name_date` with a new date, so it is another id and there is no conflict (REASONED from D-0390/0391). A conflict only appears if the copy keeps the same name and date but other bytes: then the two are shown, not merged.
I changed my mind in two places. (a) The architect says refuse and open neither; on a shared server the user cannot rename the shared file, so "neither opens" leaves her stuck (REASONED). The user viewpoint's "show both and let her choose" is acceptable only if the choice is an explicit act that is recorded. (b) Identical bytes: the architect refuses this too; I would not, because a clean copy is the normal case and refusing it teaches users to ignore the message. I do NOT accept "the deployment file says which wins": a figure then changes when someone adds a file elsewhere, and the user never chose.
Say in the methods text: identity is by bytes (CRLF versus LF gives another hash; VERIFIED in my first-round run).

## 2. Nothing writable
(a) Stop at start: honest, simple; costs the static page and the read-only container, which are owner cases. (b) Silent memory or system temp: the system temp folder is shared by processes, can hold private tables, and survives the session, so "nothing is saved" would be false (REASONED). Memory means an engine change (architect: tiers cannot be held in memory, REASONED). Worse, the audit of removed samples is lost: a result changes with no record. (c) The deployment file chooses: I support (c) with two values only, no default: `stop` or `session_only`. `session_only` uses a private folder made by the process (mode 0700, deleted at exit), shown on screen as "this session only", and any feature that changes a result (sample removal, edits) either is switched off there or the export must carry its audit and the screen says "export now, nothing is kept". An unset value is an error, not a choice made for the deployer.

## 3. The access words
Smallest set per place: `kind` (recipes | data | user), `provider`, `access` (read | add | replace, no default), `private` (true | false, default false), `required` (default true). Persistence: a place with `kind: session` (or `persistence: none` on the file) = "this session only".
Dropped: `may_export_data`. I fold it into `private`: a private place's data is never copied into an export or another place without a visible choice, default no (this changes my first round; one flag is easier to state and check).
Screen mapping: read and not private = "Shared, locked"; add or replace and private = "Mine"; add or replace and not private = "Saved in this app (everyone who uses it sees it)", never "Mine"; session place = "This session only". `add` versus `replace` is shown only where the overwrite control exists (D-0394).

## 4. Private data
Needed now, because the owner's case is exactly consortium data shared and metadata private. The flag must prevent: (i) stored tables and sessions made from private data being written to a non-private place (derived data keeps the privacy of its source; today all sit in one `user_data`, `bootloader.py:1044`, VERIFIED by my first round); (ii) data files from a private place copied into a reproducibility export without a visible choice (copy at `export_handlers.py:1496ff`, only partly read); (iii) the server path in the session: remove the absolute path for every place (`session_manager.py:386-389`), not only private ones. Least that is safe: the flag on the place, one copy function that checks it, derived files follow their source. Without a login, "private" means private to whoever runs the process; say so.

## 5. Confinement
No. A recipe `source.path` or Data Import outside the declared places makes "read-only" and "private" untrue (architect F7, VERIFIED at `orchestrator.py:172-209`). Refuse at the check, naming the declared places. Shipped recipes with `source.path` into `assets/test_data/`: they must name a dataset id, and the dev deployments declare `assets/test_data` as a read data place. Consequence the owner must be told: the recipe file changes, so its hash changes (the hash includes file content, and the relative path in the earlier study), and every saved session of those recipes stops matching once. One visible, listed change, not a silent one.

## 6. Migration
One order satisfies both, if the middle step is one atomic change.
1. Safe fixes with no decision: sorted recipe list; the absolute path out of the session record. Flag: a sorted default can change which recipe opens (today unsorted glob, `bootloader.py:404-417`); tell the owner.
2. One atomic change: pure places module, the `places` block, scripted migration of the seven files, the old keys refused with the tombstone message, and all call sites through the new resolver, one place per role (behaviour the same). No alias; old keys fail. This is large but mechanical, and it merges alone because the app works the same. The owner must accept that `get_location` disappears in this step, not later.
3. Start validation: required places, write probe by really writing in write places only (root ignores permission bits; developer, VERIFIED reasoning), the nothing-writable value of point 2.
Then: several places and the duplicate rule, the export record, Data Import and bundle import on places.

## 7. API and connectors
It covers "passed by the pipeline" (a job folder, read place) and an API pull into a local read place, if the bytes are kept. Record per file: source id and URL (never the token), request parameters, provider version or release string, fetched_at, sha256 of the bytes, and that the bytes are kept. If the bytes are not kept the figure is not reproducible, and the export must say so. A new fetch with other bytes has another hash and so another key: never silent. Opt-in per deployment; ADR-071 rule 1 (no outbound network) is touched and must be stated.

## 8. D-0340
"The design adds a places block, which reconsiders 'no new configuration variable for now', but the audit folder gets no variable of its own: it stays inside the session folder in the user place."

## 9. Wrong or silent in the others
- Architect: "a shared cache between users is safe by construction". Safe for the result (content keys), not for privacy: a cache made from private data in a shared place leaks it.
- Architect, section 10: the write probe is not proposed ("would touch a folder that someone else maintains"), and the same text admits root ignores permission bits. For a write place the probe is the only honest test; for a read place no probe is needed. Developer is right.
- Architect, duplicates: "Same name and same date in two places = a duplicate id = refused": also refuses identical bytes (point 1).
- User: "the deployment file says which wins and show that": the figure changes when a file is added elsewhere.
- User: "Nothing is saved on this installation. Your session ends when you close the page." Only true in my `session_only` case, and it does not say the audit is lost.
- Developer step 0, sorted default: may change which recipe a user gets today.

## Still open between us
- Identical bytes in two places: one object (me) or refuse (architect).
- A user opening one of two different files by explicit choice (user, me) versus neither opens (architect, developer).
- Whether `session_only` may exist at all (needs an engine or private-folder decision), or only `stop`.
- Private places: one flag (me) versus the data scientist two flags of round 1; also whether any copy from private to shared is ever allowed.
- Whether step 2 may be one large atomic merge (developer prefers small steps).
- Several users, one process, no login: "private" cannot be enforced; accepted as a stated limit or an identity required.
