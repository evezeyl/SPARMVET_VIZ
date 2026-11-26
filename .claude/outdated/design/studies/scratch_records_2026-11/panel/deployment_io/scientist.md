# One system for places of recipes and data: scientist and data scientist viewpoint (2026-11-21)

Evidence classes: VERIFIED (read at file:line or run), REASONED, ASSUMED. Scratch run: `tmpAI/panel/deployment_io/scientist_scratch/t.py`.

## Summary (6 lines)
1. Recommend design A (named places with kind, access, provider, privacy, export policy), with B as two ready-made presets of A. C cannot say "private" or "may not be copied", so it cannot protect sensitive metadata.
2. The science risk is not where a file is read from. It is a name or a dataset found in two places and one silently chosen ("first in the search order wins"). Today the app already refuses the same case inside one folder (`ingestor.py:18-31`, .tsv and .parquet: run, it raises). Extend that rule across places.
3. Every recipe and every dataset an export names must carry: logical place name, content hash, and how it arrived. Today a session stores an absolute server path plus a sha256 for data (`session_manager.py:386-389`) and a recipe hash that includes the file's relative path (`:281-287`, verified by the earlier study). No place name is recorded.
4. Sensitive metadata: stored tables (`user_data/anchors`) and sessions are derived from the data and today sit in ONE shared folder (`bootloader.py:1044`). The reproducibility export copies data files. Each place needs a flag "private: never copied to another place or into a bundle without a visible choice".
5. Without a login the "own directory" is only own when one person uses the process. A methods section may not claim authenticated authorship (initials in the log, D-0315, are self-declared).
6. Nothing in the code receives data or recipes by API (`FACTS.md` section 1); the design must record arrival (source id, time, hash) or an API case is not reproducible.

## 1. A walk through one real job (consortium recipe plus the user's private metadata)
| Step | What a reviewer asks | What the app tells today | Gap |
|---|---|---|---|
| Pick the recipe | Which file, which version, who maintains it | Name only; recipes found by an unsorted glob (`bootloader.py:404-417, 646-656`, FACTS flag 6) | No place, no date, no hash on screen |
| Load data | Which files, from where, which version | Data found by exact `<id>.tsv/.parquet` or the recipe's `source.path` (`orchestrator.py:172-188`) | Two places = one silently used, once more than one place exists |
| Open | Was the data the same as last time | Hash of file bytes, same bytes in two places give the same hash (run: True); CRLF vs LF gives another (run: True) | Hash is by bytes, not content: say so in methods |
| A file is missing | Is the run valid | A missing file gets the hash `MISSING:<id>` (`cache_keys.py:146`, run) | A vanished dataset gives a valid looking key; the stop must come from the loader, and a missing place must stop the start |
| Remove samples, audit | Which, why | Decided (D-0102, D-0315) | Audit lost when nothing is writable (FACTS flag 11) |
| Export | What can a reader redo | Hashes in provenance (`export_handlers.py:214-226`) | No place, no way of arrival, absolute paths leak the server layout |

## 2. The three designs
### Design A: named places with roles
Each place has an id (a name a person can read), a kind (recipes, data, user), an access (ro or rw), a provider (folder, volume, api, galaxy, irida), a `private` flag, a `may_export_data` flag, and `required: true|false`. A recipe never holds a place path; it holds dataset ids. A resolution rule is in the file.

```yaml
# 1. consortium read-only recipes + user's own directory
places:
  consortium: {kind: recipes, access: ro, provider: {folder: /mnt/consortium/recipes}, required: true}
  own:        {kind: user,    access: rw, provider: {folder: ~/sparmvet}, private: true}
  own_data:   {kind: data,    access: rw, provider: {folder: ~/sparmvet/data}, private: true}
  common_data:{kind: data,    access: ro, provider: {folder: /mnt/consortium/data}}
resolution: {same_name_in_two_places: refuse_unless_identical}
```
```yaml
# 2. static web page
places:
  recipe: {kind: recipes, access: ro, provider: {folder: /app/recipes}, required: true}
  data:   {kind: data,    access: ro, provider: {folder: /app/data}, required: true}
persistence: none      # no session, no audit, no stored tables; told on screen
```
```yaml
# 3. static pipeline on Galaxy
places:
  recipe: {kind: recipes, access: ro, provider: {folder: /app/recipes}}
  job_in: {kind: data, access: ro, provider: {job_folder: {env: _GALAXY_JOB_HOME_DIR}}}
  job_out:{kind: user, access: rw, provider: {job_folder: {env: _GALAXY_JOB_HOME_DIR, sub: out}}}
```
```yaml
# 4. local install, user and common directory
places:
  mine:   {kind: recipes, access: rw, provider: {folder: ~/sparmvet/recipes}, private: true}
  common: {kind: recipes, access: ro, provider: {folder: /srv/lab/recipes}}
  data_mine:   {kind: data, access: rw, provider: {folder: ~/sparmvet/data}, private: true}
  data_common: {kind: data, access: ro, provider: {folder: /srv/lab/data}}
```
```yaml
# 5. recipe and data by API
places:
  recipe_api: {kind: recipes, access: ro, provider: {api: {url_env: X, token_env: Y}}, record: [source_id, fetched_at, sha256]}
  data_api:   {kind: data,    access: ro, provider: {api: {...}}, record: [source_id, fetched_at, sha256]}
  scratch:    {kind: user,    access: rw, provider: {folder: /tmp/sparmvet}}   # received bytes kept here so the hash can be re-checked
```
Pros: one mechanism; privacy, export policy and arrival record are first class (REASONED); a deployer sees the whole picture. Cons: largest change; touches `bootloader.get_location`, `connector.resolve_paths`, 13 recipe-path places (recipe_places study), amends ADR-091 and D-0340 ("no new configuration variable for now": FLAG, the design reconsiders it).

### Design B: two fixed layers, shared and own
Each layer has recipes, data and providers. Simple to explain to users ("shared, you cannot change" and "mine"). Pros: matches the owner's first two cases; easy words. Cons (REASONED): cannot express three places (consortium, lab, user), a private data place beside a shared one on the same layer, an API read-only recipe plus a writable scratch, or a place that is not writable and not shared (job folder). It does not say what is private. Treated as a preset of A, it loses nothing.

### Design C: keep the five location keys and add what is missing
Pros: smallest change; `locations` exist (`bootloader.py:185, 431`). Cons (VERIFIED): `raw_data` is ONE place (`bootloader.py:431`); `user_data` is shared by all users and holds sessions and stored tables of all (`session_manager.py:305-308`); no per-place access or privacy flag. A second recipes key and a second data key is design A written badly, with no common rule for names in two places.

## 3. Per use case (design A; what breaks today from FACTS.md)
| Case (deployment) | Reads | May write | Screen when read-only or missing | Breaks today |
|---|---|---|---|---|
| Consortium ro + own dir (local or Galaxy interactive) | consortium recipes and data, own | own only | "Shared (cannot change)" and "Mine"; a missing required place stops the start and names it | No second place; BLUEPRINT and bundle import write into the shared folder (`bundle_importer.py:263`) |
| Static page | one recipe, one data place | nothing | "Nothing is saved in this app" | App still writes record and tables (`home_theater.py:1515-1578`) |
| Exploration page | same | nothing | same, plus panel switching | same |
| Static pipeline (Galaxy, IRIDA) | job in | job out | Run record says which input ids | Galaxy file absent; IRIDA fails (`irida.py:40-52`) |
| Upload from a path with shared plus private data | both | private only | Place shown beside each file | Only browser upload; no path choice |
| Local user plus common | both | user | as row 1 | one recipes key |
| API | api | scratch | "Fetched <time> from <source>" | not implemented |
| Container read-only with one volume | image and volume | volume | Writable place named at start | root user, no volume (`Dockerfile:66,89`) |
| Container with nothing writable | image | nothing | persistence none, told | opening stops when `user_data` read-only (`opening_build.py:249-254`) |
| Several users, one server, no login | shared | shared only | "Shared by everyone using this app", never "My" | no identity; sessions of one visible to another (not run) |
| Offline | local | local | none | not run |
| Posit Connect | app bundle | unknown | not verified | not verified |
| A place changes while running | see section 5 | | | recipes listed once at start |
| Consortium place updated by another person | see section 5 | | | |

## 4. Names in two places, and what is recorded
- Today: a recipe id is the file name (ADR-092), dataset found by exact id. Two places with one id collide in session keys and caches (REASONED).
- Rule I would defend: the same recipe or dataset id in two readable places is REFUSED with both places and both hashes named, unless the bytes are identical (then it is one object, both places are shown). Never "first in the search order wins": that is the software choosing, and the figure changes when someone adds a file elsewhere. A search order is allowed only to LIST places, not to pick between equal ids. The user, shown both, may pick by place name and the pick is recorded.
- Selector "newest per name": a choice made for the user. If kept, it must show "name, newest 2026-11-17, 2 older" and a session records the exact dated name plus hash; a session is never moved to the newer one by itself (D-0362 refuses; built today only as a warning, `session_handlers.py:597-602`).
- Recorded per item in the session and in the export: place id, kind, provider, name, sha256, how it arrived (folder, import bundle hash, api source id and time). Not the absolute server path: it leaks layout and is not reproducible elsewhere. Today the path is stored (`session_manager.py:386-389`): VERIFIED, and a case for change.
- A methods section can then state: "recipe `name_2026-11-17`, sha256 H1, from place consortium; data files D1..Dn with sha256, from places A and B; app version/commit". It cannot state who ran it (see section 6).
- Bundle-imported recipes: their data is "only what the bundle carried" (`orchestrator.py:165-170`, good: no mixing). Recommend a name rule consistent with `name_date` and the same collision rule; a re-import of identical bytes is a no-op reported to the user. OPEN for the owner.

## 5. Changes under a running app, and updates by others
- Recipes are listed once at start (`bootloader.py:404-417`): a consortium update after start is invisible, and a file edited in place under the app is detected only by hash at the next opening. A dated-name rule makes an update a new name (good). An in-place edit by someone else with the same name is the silent case: the hash differs, the session key differs, the old session is not found; D-0362 says refuse, built today as a warning only.
- Data: the hash is computed by reading all bytes at opening (`cache_keys.py:146`). If the file changes between the hash read and the later read for the figure, key and figure disagree (REASONED, not run). Fix to study: read once into the kept copy, or re-hash at export and compare with the opening hash; if they differ, the export says so.
- Large data on a remote place: a full read for each opening (`read_bytes`): cost, REASONED.
- A place that vanishes (unmounted volume): the loader must stop with the place name; a falling back to another place is a silent change. An optional place that is absent is recorded as absent.

## 6. Identity
- One user per process (local, Galaxy interactive tool, container per user): "own" is the deployment's own place; honest and enough.
- Several users, one process, no login: there is no "own". Say "shared by everyone using this app" on screen. Content keys (recipe hash, data hash) mean two users writing the same session key write the same content, so results cannot be corrupted (REASONED); but sessions, stored tables and audit reasons are readable by all (VERIFIED single `user_data`). Private data must not live there.
- An identity (Galaxy environment, Posit Connect header) is a real design need for "own" on a shared server; it is authentication in the part of the design that depends on it. It is not verified on either platform. I do not propose it; I say plainly that "own directory for several users" requires it.
- The audit's who and initials are self-declared (D-0315); a methods section says "initials as typed".

## 7. The remaining items
| Item | Proposal (consequence shown to the user) |
|---|---|
| Data Import and its overwrite | OPEN. Never overwrite without a copy: today copy then `os.replace` with no old copy (`data_import_check.py:238-272`) and the write can leave `raw_data` (`orchestrator.py:209`). Write only to an rw place of kind data; refuse an existing name, or keep the old in "previous" with its hash recorded. The screen says: "sessions made with the old file will not open; exported results are not affected". Default private place for new metadata, never the shared one. |
| Bundle import | to the user's own recipes place, never the shared one (today into the shared folder, flag 9) |
| Sessions, audit folder | In the user's place (D-0340, D-0319). Nothing writable: say at start "audit steps and sessions will not be kept: export them now"; do not silently continue (flag 11) |
| Stored tables | Cache, keyed by content: no result change, only time. Nothing writable: compute in memory and say so. In a shared place they inherit the privacy of their data: a private flag applies |
| BLUEPRINT fixed folder (`blueprint_handlers.py:975-984, 2685`) | becomes an rw recipes place; writing in a ro place refused with the place name (D-0393) |
| Gallery index | a derived file, not science: skip when ro (already, `gallery_manager.py:207`) |
| Exports | Browser download only today (VERIFIED). Reproducibility export copies data (`export_handlers.py:1496ff`): per place `may_export_data`; private default no, with a visible choice |

## 8. Pitfalls (flagged first)
1. First place wins on equal names: changes a figure silently.
2. Search order as default in a selector that picks "newest": the software chooses.
3. Private metadata copied by the reproducibility export, by a shared anchors folder, or by a bundle import into a shared place.
4. Absolute paths in recipes (`source.path`) or in sessions: not reproducible, leak server layout; a scaffolded recipe may name a temp path (not verified).
5. A required place absent -> fallback to another place.
6. API-fetched bytes not kept: hash cannot be re-checked.
7. "Nothing writable" continuing with the audit lost.
8. Case and whitespace: an id is exact and case sensitive (run: `ds1` found, `ds 1` not; on a case-insensitive disk `DS1.tsv` may match: not run). A place-id or dataset id with spaces must be refused, not trimmed.

## 9. Recommendation
Design A with B and today's local file as presets; C only as the migration first step (its keys become named places of A). Why: only A holds the facts a figure depends on (place, privacy, arrival, hash) and lets each deployer say "ro", "private" and "not exportable". Reconsiders: D-0340's "no new configuration variable for now" (flag). Does not reconsider D-0333, D-0390 to D-0394, D-0102, D-0263.

## To decide first (ranked)
1. Same name or dataset id in two places: refuse unless identical (my proposal), or another rule (owner decides).
2. Do private places exist, and may an export copy data from them (a flag with a visible choice)?
3. What is recorded per file: place id, hash, arrival; absolute path removed from the record.
4. Identity: accept "shared by everyone" on a shared server with no private data, or require an identity from the platform.
5. Required place absent: stop at start (proposed), or continue and record absence.
6. Data Import overwrite: refuse, or keep the old with its hash.
7. Amend D-0340 for new configuration.
Can wait: selector newest-per-name wording, Gallery index, offline, Connect.

## Not verified
Run-time behaviour of containers, read-only mounts, Galaxy, IRIDA, Connect, two users, sessions listed across users; whether data can change between the hash read and the figure read; case-insensitive disks; what the reproducibility export does with data from a place that is not copyable (`export_handlers.py:1496ff`, read only in part); the API providers (nothing exists to test).
