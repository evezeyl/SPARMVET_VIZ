# Developer viewpoint: one system for reading and writing recipes and data in every deployment (2026-11-21)

Labels: verified (read or run, file:line), reasoned, assumed. Read-only study; nothing built. The owner decides.

## Summary (6 lines)
1. Recommendation: design A (named places with roles and a provider each), built in small steps that each leave a working app; B is the special case "two places" of A; C leaves the unsafe parts open.
2. The core is ONE pure module (no Shiny, in `libs/connector/`) that reads a `places:` block, checks it at start (including a real write probe) and answers "where, who may read, who may write, from which provider". It is built and tested before any screen.
3. Size: 57 `get_location`/`resolve_paths` call sites in 16 non-test files; 103 `data_analysis_recipes` mentions in 16 files; 116 test files mention them; 7 shipped deployment files. Large but mechanical, and each step can be merged alone.
4. Nothing in the app can receive data or a recipe by API today (FACTS 1). The API and IRIDA providers are a separate, later layer; build the registry first and add a provider only when its use case is specified.
5. Five owner decisions block code (see end): the user's own place without login, the same name in two places, nothing-writable behaviour, what is recorded for data, and the Data Import overwrite.
6. Tests: read-only and two-user cases can be tested without Galaxy; the root-in-container case needs a real container run (podman and docker exist on this machine; whether CI has them is not verified).

## 1. What stays, what must change (verified)
- Stays: the connector factory (`libs/connector/.../__init__.py:31-45`), `FilesystemConnector.resolve_paths` shape (`filesystem.py:28-60`), the tombstone pattern for renamed keys (`app/modules/renamed_keys.py:96-100`: stops the app with a plain message), the load gate, the session key (recipe hash and data hash, `session_manager.py:305-308`).
- Changes: `bootloader.get_location` (`bootloader.py:840-848`) answers by a flat key with no access information. It must answer "place by role", with `readable` and `writable` known. `_REQUIRED_TO_EXIST` (`filesystem.py:24`) is a fixed list of three keys. The five keys have no notion of search order, provider or access.
- Hard-coded paths outside the locations (FACTS 1): BLUEPRINT's folder (`blueprint_handlers.py:975-977, 2685`), `config/...` relative to the working directory, `~/.sparmvet` and `/etc`. These are listed in the table of section 6.
- I checked: `id -u` here is 1000, so `chmod` read-only tests work locally; as root (the container default, FACTS 2) permission bits are ignored, so a test that relies on `chmod` passes on a laptop and is useless in a root container. The registry must probe by really writing a file and removing it, not by `os.access`.

## 2. The three designs, from the build side
Deployment file sketches are given for five cases per design. Names are illustrative.

### Design A: named places with roles
```yaml
places:
  - id: consortium_recipes   # kind: recipes | data | user
    kind: recipes
    access: read            # read | readwrite
    provider: {type: folder, path: /srv/consortium/recipes}
    order: 1
  - id: mine
    kind: user              # holds my recipes, sessions, audit, imports, stored tables
    access: readwrite
    provider: {type: folder, path: "{user_dir}"}   # see identity, section 5
```
- Case 1 consortium read-only plus own directory: the two places above; plus a `data` place per source.
- Case 2 static web page: one recipes place `read`, one data place `read` (updated outside), `user` place `none` (new access value: nothing writable) or a temp place. The app features file already has pipeline-static flags.
- Case 3 static pipeline on Galaxy: data place `provider: {type: job_folder, env: _GALAXY_JOB_HOME_DIR}`; recipe place `provider: {type: file, path: ...}` fixed at deployment. Galaxy variables exist in `galaxy.py:35, 54`; no tool wrapper exists (FACTS 2).
- Case 4 local with user dir and common dir: as case 1, `access: readwrite` on the common place if the maintainer's app.
- Case 5 API: `provider: {type: api, url: ..., token_env: ...}`. Needs a new HTTP client and a cache folder that is writable; no such code exists (FACTS 1). Not building it now.

### Design B: two fixed layers, shared and own
```yaml
shared: {recipes: /srv/c/recipes, data: /srv/c/data, access: read}
own:    {root: "{user_dir}", access: readwrite}
```
Smaller file, smaller registry (two layers by two kinds). It cannot say "three data sources" (the owner's wording: "can be one unique path or several paths", ORDER.md line 14), nor "a pipeline job folder plus an API". Every new case becomes a new key, which is design C by another door.

### Design C: five keys plus what is missing
Add `recipes_extra`, `own_recipes`, `read_only: [..]`. Fast to start. Each added key is one more special case in 57 call sites; no search order; provenance would be added per key. It repeats the problem that the five keys already show (the `cache` key is unused, FACTS 1; BLUEPRINT ignores the recipes key).

## 3. Effort, risk, tests per design (facts for ordering; time is not an argument)
| Item | A | B | C |
|---|---|---|---|
| Effort | large (registry + migration of 57 sites + 7 files) | medium | small first step, large later (repeated) |
| Risk | medium: wide mechanical change; a missed hard-coded path stays on the old way silently | medium: wrong when a third place is needed | high over time: more special cases, silent gaps |
| Fits the owner's wish "one system, deployment file decides" | yes | partly | no |
| Tests needed | registry unit tests (parsing, validation, probe, search order, provenance); one test per call-site class; migration test per shipped file | same for two layers | one per new key |
| New concept for the user | places list (the deployer writes it) | two words | three or four keys |

## 4. Per use case (A): who reads, who writes, what the user sees, what breaks today
| Use case | Reads | Writes | User sees if read-only or missing | Breaks today |
|---|---|---|---|---|
| Consortium read-only + own dir | recipes: consortium, mine; data: consortium, mine | mine only | "Shared recipes (you cannot change these)" / "My recipes"; a refusal line when writing a shared place | no second recipes place; BLUEPRINT and bundle import write into the shared folder (`bundle_importer.py:263`) |
| Static web page | one recipe, one data | nothing | no save controls | session record is written at every opening with no flag (`home_theater.py:1515-1578`); stored tables always written (`opening_build.py:249-254` stops the opening if not writable) |
| Exploration, no save | same | nothing | same | same two writes |
| Static pipeline (Galaxy/IRIDA) | job folder / recipe fixed | job output folder only | n/a | no wrapper; IRIDA `fetch_data` raises (`irida.py:40-52`) |
| Upload of data from paths the user can reach | shared data, own data | own data | place name next to each file | only a browser upload, one `raw_data` (`data_import_handlers.py:131-139`) |
| Local user + common dir | both | own; common if maintainer app | as row 1 | one recipes key |
| API | api provider | cache place | "the source answered / did not answer" | not implemented |
| Read-only container + one writable volume | image places read; volume write | the volume | a line at start naming the unwritable places | root, no `USER`, no `VOLUME` (Dockerfile, FACTS 2) |
| Container, nothing writable | all read | nothing | decision needed (section 8) | opening stops (`opening_build.py:249-254`) |
| Several users on one server, no login | shared | one shared own place | warning "this place is shared by all users of this app" | one `user_data` for everyone (`bootloader.py:1044`) |
| Place changes while running | listing read at start | - | needs a re-list rule | recipes listed once at start (`bootloader.py:404-417`) |
| Offline | vendored assets | local | none | not verified by a run |
| Posit Connect | per template | volume persistence unknown | - | not verified |

## 5. Names, provenance, identity (build facts)
- Resolution: the order of the `places` list decides the search; the same recipe name in two places is refused by default (P3 of the recipe places table: not decided). A silent "first wins" is a silent change of a result and must not be the default.
- Provenance needs one data structure, `ResolvedItem(place_id, provider, path, name, content_hash, resolved_at)`, created by the registry and carried to the export. Today the export records recipe and data hashes; place identity is not in it (reasoned; export code at `export_handlers.py:1496-1502` not run). The place id of a recipe and of every data file goes into `effective_run.yaml` and the audit record.
- Identity without login: the registry takes `{user_dir}` from an environment variable or a path the deployer sets per process (one user per process: local, Galaxy interactive tool). Several users on one server share the place, and the design must say so on screen. A per-user folder needs an identity (ADR-091 `:4438`); that is an authentication task, not part of this system. I do not invent one.
- Sensitive metadata: a `user` place must be marked `private`; the registry refuses to copy from a private place to a shared one (a check in the one copy function). Whether a copy to a shared place is ever allowed is the owner's decision.

## 6. What happens to each (A)
| Item | Result |
|---|---|
| Data Import and its overwrite | writes only to a place with `access: readwrite` and `kind: data` or `user`; never outside (closes `orchestrator.py:209`); the overwrite keeps the old file (`name_date`) or asks; owner decides (OPEN) |
| Bundle import | writes to the `user` place under `imports/`; its recipe name follows the decided rule or the import name (OPEN, P9) |
| Sessions and audit | in the `user` place, `sessions/<key>/audit/` (D-0340: no new variable; the places block replaces "the location of the user's data", which is amended, see Amends) |
| Stored tables, nothing writable | OPEN: stop with a plain line (today) or memory only with a visible notice |
| BLUEPRINT fixed folder | BLUEPRINT reads and writes through the registry; full recipe edit stays in BLUEPRINT (D-0102) |
| Gallery index | a `gallery` place; the index rewrite is a write and needs `readwrite` or is skipped with "not_writable" (already so: `gallery_manager.py:207-209`) |
| Logs | stdout only; unchanged |

Amends or touches: ADR-048 (locations block), ADR-071, ADR-091, ADR-097; D-0340 ("existing location": reinterpreted, to confirm with the owner), D-0263 (the interpreter key, to remove in the same pass). I propose no reversal of D-0390 to D-0394, D-0102 or D-0333.

## 7. Build order, with tags
Model/effort tags follow the CLAUDE.md section 2 table; I did not re-read it, so the tags are labelled "suggested".
| Step | What | Tag (suggested) | Parallel? |
|---|---|---|---|
| 0 | Safe fixes, no decision needed: sort the recipe list and default (`bootloader.py:416-417, 656`); one `recipe_path()` replacing the folder/<id>.yaml sites; BLUEPRINT reads the deployment folder; `create_test_deployment.py:77` `.yaml` suffix; remove `python_interpreter` from the seven files (D-0263) | sonnet / medium | yes, each in its own files |
| 1 | `name_date` module: split, newest per name (decided rule D-0390, D-0391); tests with two keys | sonnet / low | yes |
| 2 | Registry module in `libs/connector/` (pure): parse, validate, probe, search order, `ResolvedItem`; renamed-keys tombstone for the old five keys; plain errors | opus / high (the risky logic) | no: first of the chain |
| 3 | Migrate the 7 shipped deployment files and the template; docs `deployment_guide.qmd`, `connector.qmd` (contradictions in FACTS 8) | sonnet / medium | after 2; the files in parallel |
| 4 | Switch call sites by class: recipes, then data (`orchestrator.py:172-209`), then user (sessions, anchors, imports, audit) | opus / medium per class | one class at a time (shared files: `bootloader`, `home_theater`) |
| 5 | Recipes: two places, refusal of the same name, provenance label | sonnet / high | after 4 |
| 6 | Data: several places, provenance in the export | opus / high | after 4 and the data decisions |
| 7 | Read-only and nothing-writable behaviour (session record flag, stored tables) | opus / high | after the decision |
| 8 | Screens: labels "Shared recipes (you cannot change these)", place names | sonnet / medium | last |
| 9 | Container: `USER`, `VOLUME`, default deployment (D-0263 says the container recipe is deferred) | sonnet / medium | deferred by the owner |
| 10 | Providers: API, IRIDA | opus / high | not before the use case is written and decided |

## 8. Tests (how)
- Registry unit tests with `tmp_path`, no Shiny. Include: empty places list, two places with the same id, a missing path, a path that is a file, search order, the same name in two places, the old five keys (must stop with the tombstone message).
- Read-only: probe-by-write; simulate with a monkeypatched writer when running as root; plus one real run `podman run --read-only --tmpfs /tmp -v ...` (podman and docker are installed here; CI support not verified).
- Two users: two processes with two `{user_dir}` and one shared place; assert that their sessions are not mixed (today they are shared: `session_manager.py:305-308`, not run).
- Break-once checks (agent_principles rule 5): make the probe always true and watch the read-only test fail.
- Galaxy and IRIDA without the platforms: a fake provider class that implements the same interface as `BaseConnector`; the real platform stays NOT VERIFIED.
- Regression: 116 test files reference the old keys; they must be adapted to the design first, not patched after.

## 9. Pitfalls
- A first-wins search order silently changes which recipe or data a figure uses.
- A place that changes while the app runs: the recipe listing is built once at start; data hashed at opening can differ from data at export. Record the hash at opening and compare at export; tell the user if it differs (reasoned; to build).
- Defaults must not decide: an unspecified `access` must be an error, not "readwrite".
- A temp place as fallback for "nothing writable" hides that nothing is saved; show it.
- The `user` place that is "shared by all" must never be called "My" on screen.
- Package data: `config/` and `assets/` are not in a package (`pyproject.toml:1-53`); the PyPI case is not possible before that is settled.

## Recommendation
Design A, with B as a two-place file of the same system. Reason: the only design in which the deployment file says everything the owner asked it to say, and in which each added case is a list entry rather than a new key. Steps 0 and 1 are safe now. Step 2 can be built as a pure module before any decision, but steps 4 to 7 must wait for the decisions below.

## What the user must be told to choose well
- A place is "shared by everyone of this app" when there is no login; "my own" is true only with one person per process.
- What is lost when nothing is writable: sessions, stored tables, audit, import.
- That a same-name conflict is refused, and why a "first wins" rule would hide which recipe was used.
- That the export records the place of each recipe and data file, and not the content of a place that someone changes later.

## To decide first (ranked)
1. What "own place" means without a login (one per process, or shared and named so).
2. The same name in two places: refuse, own wins, or shared wins.
3. What the app does when nothing is writable (stop, or memory with a notice); and whether the session record at opening gets a flag.
4. What is recorded for data in the export (place id and hash at opening, hash at export).
5. The Data Import overwrite (keep old with a date, ask, or refuse) and whether it may write outside a data place.
6. Whether a private place may ever be copied to a shared one.
7. Can wait: API and IRIDA provider details, the container recipe (D-0263 defers it), PyPI package data, the screen words.

## Not verified
Container, Galaxy, IRIDA, Connect and PyPI behaviour; read-only mounts and two users by a run; whether sessions of another user are listed (FACTS 7); CI support for podman or docker; the exact model/effort table of CLAUDE.md (tags are suggested); the export code of recipe and data identity in reproducibility mode.
