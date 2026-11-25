# Architect viewpoint: one system for reading and writing recipes and data in every deployment (2026-11-21)

Role: software architect (`dasharch`: smart simplicity, decoupled, audit-ready) and the Checker persona. I recommend; the owner decides. Nothing in the repository was edited. Scratch: `tmpAI/panel/deployment_io/architect_scratch/probe.py` (one run, see flag F1).

Labels: **V** verified (read at file:line, or run); **R** reasoned; **E** external, not checked; **A** assumed. Tags: **DECIDED / CONFIRM / OPEN / MINE** (MINE = my proposal, nobody decided it).

## Summary (6 lines)
1. Recommended: **Design A, named places in a closed set of roles** (recipes, data, user data, cache, gallery). Each place has an id, a label, a path or a provider, an access (`read`, `add`, `replace`) and `required`. It replaces the five `locations` keys in ONE pass with a migration script and a refusal of the old keys (the ADR-091 precedent); no alias. B ("shared" / "own") becomes the words on screen and the shipped templates, not a second syntax. C (keep five keys) cannot say "read-only", so the user learns it by failing.
2. Kept from ADR-048 section 5: after the connector has run, everything is a local path; the app never talks to Galaxy, IRIDA or an API; no inbound API. An "API" is a provider that pulls into a local read place; this is OPEN and does not exist today (`irida.py:40-52`).
3. **No search order.** A recipe id or a table found in two places is refused and both places are named; nothing is resolved silently. A name found twice and picked by order would make a methods section false.
4. **No identity system is proposed.** Without a login "my own directory" is a folder of the process; on a shared server it is shared by everyone of that process and the screen must say so. A per-user place on one server needs an identity from the platform (ADR-091 point 4: "a connector task for later"): not part of this design.
5. Verified problems that bind the order: a missing or unwritable `user_data` crashes per browser session, not at start (F1); the Dockerfile names a library that does not exist (F4); 34 modules import a top-level package called `app` (F5, blocks PyPI); a changing place needs D-0184 first (F8).
6. Decide first: (1) the three access words and the "no search order, refuse a duplicate" rule; (2) whether the app may read or write outside the declared places (recipe `source.path`); (3) what the app does when nothing is writable; (4) whether PyPI is a goal (it needs a rename of `app`).

## 1. Flagged first (new, beyond FACTS.md section 6)

| # | Finding | Evidence | Why it matters |
|---|---|---|---|
| F1 | **No fail-fast on places.** `SessionManager(bootloader.get_location("user_data"))` is built inside `server(input, output, session)` (`server.py:49`, `:149`), so once per browser session, and it does `mkdir` (`session_manager.py:274`). Ran: a `user_data` that does not exist under a read-only parent gives a raw `PermissionError` at every browser session (`probe.py`, user id 1000). If the folder exists but is read-only the construction passes and the opening stops later (FACTS section 1). | V (run + read) | A read-only container fails at the user's first click, with a traceback, not at start with a message to the operator. |
| F2 | **Two lists of "required" that disagree.** `FilesystemConnector._REQUIRED_TO_EXIST = ("raw_data", "data_analysis_recipes", "gallery")` (`filesystem.py`, comment: cache and user_data are created on demand) against `Bootloader._validate_deployment` which requires five keys (`bootloader.py:342`). Nothing creates `cache` (unused); `user_data` is created per session (F1). | V (read) | Two stores that can disagree; each says a different thing about what must exist. |
| F3 | **Places are per process by construction.** `bootloader = Bootloader()` at import (`bootloader.py:1044`), class-level `_resolved_locations_cache` keyed by deployment path (`:77`). 44 calls of `get_location`/`get_imports_dir` in `app` and `libs` (non-test), 23 of them for `user_data`. | V (grep) | This is the cost of any per-user place later: the string-key lookup would have to become a per-session object. A design that introduces ONE object handed to the handlers now makes that later step small; it is not needed for the identity-free design. |
| F4 | **The Dockerfile cannot build as written.** It runs `pip install ... libs/generator_utils` (`Dockerfile` RUN block); `libs/` has no `generator_utils` (V, `ls libs`). It also installs neither `blueprint_arch`, `id_reconciliation` nor `test_lab`, which the app imports (`server.py`, `bootloader.py` deferred import, `test_lab_studio.py`). Build not run. | V (ls, grep); R (the build error) | Every container use case below is untestable until this is repaired. D-0263 defers the container recipe; this is a reason to schedule it. |
| F5 | **The import name is `app`.** 34 non-test files import `app.modules...` or `app.handlers...`; the root `pyproject.toml` lists no packages (`:1-53`). A wheel would install a top-level package called `app` into site-packages. | V (grep, read) | PyPI needs a scripted rename of the top package (an ADR-091 style pass). Not needed for GitHub or a container (`PYTHONPATH=/app`). |
| F6 | **The fallback is a demo deployment, silently.** With no variable and no file, level 4 is `config/deployment/local/local.yaml` (`bootloader.py:295-298`); only a `print` says which level was used (`:102-105`). It names relative paths such as `tmp/UI_TEST/user/`, relative to the current folder. | V (read) | A forgotten `SPARMVET_DEPLOYMENT` in a container or an installed copy starts a development setup instead of stopping. In a container it fails by luck (the demo data is in `.dockerignore`). |
| F7 | **The declared perimeter is not the real one.** A recipe's `source.path` is read as written (`orchestrator.py:_declared_path`, `:172-188`), and HOME Data Import writes to the same place (`file_place`, `:197-209`), also outside `raw_data`. | V (read) | A place declared read-only does not protect a path a recipe names. "Read-only consortium place" is only true if reading and writing are confined to declared places. |
| F8 | **A place that changes while the app runs is not seen.** Discovery runs once per process (`bootloader.py:404-415`, the docstring says so); the load gate checks every recipe at start (D-0184 says only when selected; contradicted, FACTS section 8). A rescan today would re-check all recipes. | V (read) | "A consortium place updated by someone else" needs D-0184 built first, or each refresh is slow and every new recipe is gated again. |
| F9 | **`deployment_type` has one use.** It only picks the connector class (`connector/__init__.py:40`); the bootloader stores it and reads it nowhere else (`bootloader.py:123`; grep over `app`). | V (grep) | With a provider per place, `deployment_type` becomes redundant: a Galaxy deployment is places with provider `job_dir`. Removing it follows the "one authoritative way" rule. |

## 2. What every design must keep (so the tags are clear)

| # | Line | Tag | Source |
|---|---|---|---|
| L1 | After the connector ran, everything is a local path; the app never knows the source system. | DECIDED | ADR-048 section 5 |
| L2 | No Shiny in `libs/connector/`; handlers and modules stay thin. | DECIDED | `dasharch.md` section 4, Clear Lines |
| L3 | Hand-offs between user spaces are files; no space writes into another space's state. | DECIDED | ADR-093; ADR-099 point 6 (`:4975`) |
| L4 | The audit recipe and its record live in an audit folder inside the session's folder, in the user's own directory of the deployment; no new configuration variable for it. | DECIDED | D-0333, D-0340, D-0319 |
| L5 | A recipe file is `name_date`; an upload under an existing name is refused; an overwrite control exists only in the user's own place; only specific users modify common recipes. | DECIDED (rule), not built | D-0390 to D-0394 |
| L6 | Full recipe edit exists only in BLUEPRINT. | DECIDED | D-0102 |
| L7 | One interpreter: the Python that runs the app. | DECIDED, not done | D-0263 |
| L8 | `~` and `${VAR}` are expanded in deployment paths; an unset variable stops the app. | DECIDED, built | ADR-091 point 4; `libs/utils/src/utils/path_expansion.py:19-33` (V) |
| L9 | No secrets in source: the IRIDA token only in `SPARMVET_IRIDA_TOKEN`. | DECIDED | ADR-048 section 8; `irida.py` (V) |
| L10 | Old keys fail loudly with a message that names the new one; no alias. | DECIDED | ADR-091 point 2; `app/modules/renamed_keys.py` (V) |
| L11 | The deployment says what is intended; the operating system says what is possible. The app applies the stricter and tells the user which. | MINE (consistent with ADR-071 layer 2 and D-0394) | - |
| L12 | Everything the app reads or writes lies inside a declared place. | MINE (fixes F7) | - |

## 3. The common vocabulary of the designs

A place answers five questions. A design differs in how the deployment file says them.
1. **Role**: what the app puts there (recipes, data, user data, cache, gallery).
2. **Access**: what the app may do there.
3. **Reach**: how its local folder comes to exist (a folder, a mounted volume, a job folder, a connector, an API pull).
4. **Name rule**: what happens when the same name is in two places.
5. **Record**: what is written into an export so that a figure can be reproduced.

## 4. The three designs

### Design A: named places, closed set of roles (recommended)

Idea. Five fixed role keys (the code knows what each is for; a deployer cannot invent a role). `data_analysis_recipes` and `raw_data` are lists, the others one place. Each place:

| key | meaning |
|---|---|
| `id` | short name, unique in the file; used in messages and in the export record |
| `label` | the words the user sees ("Consortium recipes"); the app adds the access words itself, so a label cannot claim "read-only" falsely |
| `path` | a folder (expanded as today, L8) |
| `provider` | how the folder is made: `folder` (default), `job_dir` (relative to the platform's job folder; today `_GALAXY_JOB_HOME_DIR`, `GALAXY_SLOTS_DIR`, `galaxy.py:35,54`), `irida` (stub today). `url` or API pull: OPEN, does not exist |
| `access` | `read`; `add` (new files only, the app never changes or removes an existing one); `replace` (may also overwrite). `user_data` and `cache`: only `replace` or absent. `gallery`: `read` |
| `required` | default `true`: missing at start stops the app with a message naming the place; `false`: the place is listed as "not reachable now" (offline use, a share that is down) |

`deployment_type` is removed (F9). `cache` is the key that already exists, unused (F14 of the UML findings, task CONFIG-CACHE-LOCATION-1, `tasks.md:200`): stored tables move there, so the cache is rebuildable and user data is not. `locations`, `project_root` stay or go as a separate decision (see section 9, relative paths).

**Sketches (five of her cases).**

1. Consortium read-only recipes plus the user's own directory (also the local install with a user and a common directory; for a common directory where people deposit, set `access: add`):
```yaml
default_app_features: standalone
places:
  data_analysis_recipes:
    - {id: consortium, label: "Consortium recipes", path: /mnt/consortium/recipes, access: read}
    - {id: mine,       label: "My recipes",         path: "${HOME}/sparmvet/recipes", access: replace}
  raw_data:
    - {id: consortium, label: "Consortium data",   path: /mnt/consortium/data, access: read}
    - {id: mine,       label: "My data",            path: "${HOME}/sparmvet/data", access: replace}
  user_data: {path: "${HOME}/sparmvet/user",  access: replace}   # sessions, audit folders (D-0340), imports
  cache:     {path: "${HOME}/sparmvet/cache", access: replace}   # stored tables, rebuildable
  gallery:   {path: /opt/sparmvet/gallery,    access: read}
```
2. Static web page (one recipe, data replaced now and then, nothing saved):
```yaml
default_app_features: pipeline-static
default_data_analysis_recipe: amr_2026-11-20
places:
  data_analysis_recipes: [{id: published, path: /srv/sparmvet/recipes, access: read}]
  raw_data:              [{id: pipeline,  path: /srv/pipeline/output,   access: read}]
  cache: {path: /var/cache/sparmvet, access: replace}
  # no user_data: nothing is saved. The start refuses app features that need it (see section 9)
```
3. Static pipeline on Galaxy (one container per job, data handed in the job folder):
```yaml
default_app_features: pipeline-static
default_data_analysis_recipe: amr_2026-11-20
data_lookup: by_dataset_id
places:
  data_analysis_recipes: [{id: baked, path: /app/recipes, access: read}]
  raw_data:              [{id: job_input, provider: job_dir, path: inputs/, access: read}]
  cache: {provider: job_dir, path: work/, access: replace}
```
4. Local install, a user directory and a common directory: sketch 1 with `consortium` renamed `common`, `access: add` if the lab deposits there.
5. Recipe and data given by an API (target only; no code exists):
```yaml
places:
  data_analysis_recipes: [{id: baked, path: /app/recipes, access: read}]
  raw_data:              [{id: irida_project, provider: irida, path: /var/sparmvet/irida_cache, access: read}]
irida: {base_url: "https://irida.example.org", project_id: 42}   # token only in SPARMVET_IRIDA_TOKEN
```
Pros: one structure for every case; a place says its own access, so the screen can say "you cannot change these" BEFORE the user tries; each place can be probed at start (F1); the export can name places; tests are parametrized over place sets with `tmp_path`. Cons: more keys than today; two writable places of one role mean the user is asked where to save (informs, does not choose; see section 7); `access` is the app's statement, the operating system decides (section 10).

### Design B: two fixed layers, "shared" and "own"

Idea. `shared` is read-only for the app and lists several paths for recipes and data; `own` is one root with a layout fixed in the code (`recipes/ data/ sessions/ stored/ imports/`), created by the app.
```yaml
shared: {recipes: [/mnt/consortium/recipes], data: [/mnt/consortium/data]}
own:    {root: "${HOME}/sparmvet"}
```
Static page: `shared` only, `own: none`. Galaxy: `shared` from the job folder and `own: none` plus a `work:` entry for the stored tables (B needs a third layer for the stored tables the moment nothing is writable, so "two layers" is not enough). API: a `provider` per list entry, which turns the lists into objects: B grows into A.
Pros: shortest file; the owner's two words are the keys; one root matches D-0340's "inside the user's own directory". Cons: the layout of `own` is hard-coded in code (more fixed names, the opposite of what F2 and F7 call for); a deposit directory needs a third kind (`shared` with `add`); per-place provider and per-place access need A's objects anyway; a read-only container with the recipes baked in and the data mounted is awkward.

### Design C: keep today's five keys and add only what is missing

Idea. Keep `locations.*`. Add `locations.own_recipes`, make `raw_data` a list, add `locations.common_data`. Nothing says access.
Case 1: `data_analysis_recipes` (read by the operating system's permissions), `own_recipes`, `raw_data: [common, mine]`. Static page and Galaxy: as today. API: not expressible.
Pros: smallest diff; the seven files change little. Cons: **access cannot be said**, so the app learns it by failing (against "informs the user"); every addition is one more ad-hoc key with its own rules (the "half fix" the rules forbid); no provider per place; the user cannot be told which place a file came from unless a label key is added, which is A.

### Comparison

| | A named places | B two layers | C five keys plus |
|---|---|---|---|
| Says read / add / replace per place | yes | only for the whole layer | no |
| Says how a place is reached | per place | per layer | per deployment (`deployment_type`) |
| Hard-coded layout in code | none new | the `own` layout | none new, existing ones stay |
| Several shared places | yes | yes (lists) | only if each key becomes a list |
| Nothing writable | `cache`/`user_data` absent or `job_dir` | needs a third layer | not expressible |
| Teachable in one sentence | "a list of places, each with what you may do" | "shared and mine" | "five folders" |
| Amends | ADR-048 sec. 3 and 5, ADR-091 gaps 1 and 2 | same, plus the `own` layout | ADR-048 sec. 3 lightly |
| Migration of the seven files | scripted, one pass | scripted, one pass | by hand, small |

## 5. Per use case (design A; where B or C differ, noted)

"Today" is from FACTS.md sections 3 and 4. User space or deployment case is named in each row.

| Case | Who reads what from where | Who may write what where | What the user sees when a place is read-only or missing | What breaks today |
|---|---|---|---|---|
| Consortium recipes + own directory (local PC, one user per process) | Everyone reads `consortium` and `mine` | Only `mine` (replace); the consortium folder is filled outside the app | Heading "Consortium recipes (you cannot change these)" and "My recipes"; the save and overwrite controls exist only for `mine`; a missing optional place shows "Consortium recipes: not reachable now" | One recipes folder; BLUEPRINT and bundle import write into it (FACTS 3, 4) |
| Same on a shared server, no login | Everyone of the process reads both | `mine` is shared by all users of this process (L-identity, section 8) | Heading "Drafts of this app (shared by everyone who uses it)", never "My recipes" | Same, plus sessions of all users listed together (FACTS flag 2) |
| Web page, static | The one recipe from `published`; data from `pipeline` | Only `cache`; nothing for users | No save, no session panel, no Data Import: the controls are absent, not greyed with no reason | The record is written at every opening and a writable `user_data` is needed (FACTS flag 1) |
| Web page, exploration | As static; user switches panels | Only `cache` | As static | Same |
| Static pipeline on Galaxy | Recipe in the image; data in the job folder | `cache` in the job folder | No user places: the app features hide what needs them; start refuses a flag that needs a missing place | No Galaxy deployment file; no tool wrapper; the job folder variable is undocumented (FACTS 2, 7) |
| Pipeline hands the data by job folder | As above | As above | A job folder that does not exist at start stops the app naming the place and the operator | Works only through `project_root` or the Galaxy variable |
| Pipeline hands the data by API (IRIDA, a URL) | Provider pulls to a local read place at start | Nothing in the fetched place (always `read`) | A pull that fails stops the app (required place) naming the source; the token never appears in a message | Not implemented; IRIDA stub fails at start (`irida.py:40-52`) |
| User uploads data from a path they can reach (Galaxy or IRIDA paths, shared and private) | `consortium` and `mine` data | Data Import writes only into a data place with `add` or `replace`; private metadata goes to `mine`, never to `consortium` unless that place is `add` and the user picks it | "Save to:" lists only the places the user may write, each with its label; none = no Data Import control and one line saying why | One `raw_data`; no path choice; a recipe's `source.path` decides where it writes (F7) |
| Several users on one server without login | All read the same places | Whatever the places allow; `mine` is common | Labels say "shared by everyone using this app" | One `user_data` for all; nothing keyed by a user |
| Read-only container with one writable volume | Recipes and data baked in or mounted read | Only the volume: `cache`, `user_data` | Start probes each place (section 10); a volume that is not writable stops the app naming it | No `VOLUME`, paths relative to `/app`, root, F1, F4 |
| Container with nothing writable | Recipes and data read | None | Start refuses: the app needs `cache` (stored tables) at least (section 7) | Opening stops with a message today (`opening_build.py:249-254`); tiers cannot be kept in memory (R) |
| Offline use | Folders only; assets vendored (ADR-071 rule 1) | As the folders allow | Places with `required: false` are shown "not reachable now"; network providers are not declared | Not run (FACTS 7) |
| Posit Connect | Content folder or a mounted path | `cache` and `user_data` on Connect's app storage if it persists (E, not verified) | Same start probe | `connect_template.yaml` is not start-tested (excluded by name in `test_shipped_deployments.py`, V) |
| A place changes while the app runs | New recipe files appear only after a rediscovery at an explicit event (new browser session or a "refresh" action; never a poll) | - | The list says when it was read ("read at 14:02") | Once per process (F8) |
| A consortium place updated by someone else | A recipe changed between two sessions has another hash: the session is refused or warned (D-0362, not built); an added dated file appears at the next refresh | - | "Recipe X changed since this session was saved" | Warning only (`session_handlers.py:597-602`) |
| Maintainer who publishes a dated recipe to the common place | Reads the common place | A separate app (its own deployment file) where the common place is `add` | Only that app shows "Save final version (dated)" | Cannot be done |

## 6. Names, order, display, record

**Search order: none (MINE, to confirm).** Each role lists places only for display order and for the preselected "save to". The app never picks between two places by order.
- A recipe id (the stem, ADR-092, DECIDED) found in two places: both files are listed as "not available: name X exists in 'Consortium recipes' and 'My recipes'", neither is opened. Not a start error unless it is the default recipe of a static deployment.
- A table `<id>.tsv|.parquet` in two data places: the opening is refused for that table, both places named. A user with her own metadata and the consortium's data has different table ids, so nothing collides.
- `name_date` (D-0390, D-0391): the id includes the date, so `amr_2026-11-17` and `amr_2026-11-20` are two ids and can sit in different places without collision. "Newest per name" (OPEN) is then a presentation rule across places: the name before the date; the pure function proposed in `recipe_places/architect.md` section 2 (`split_name_date`, `newest_per_name`) applies unchanged. Same name and same date in two places = a duplicate id = refused.
- If the owner prefers "own shadows shared", the consequence to tell her: a user's file with the same id replaces the consortium recipe on that user's screen, and a methods section that says "recipe X" is then false unless the hash is stated.

**What the user sees.** Each recipe and data file carries its place label and the access words in the selector, in the Data panel and in the opening line ("recipe X from 'Consortium recipes', data T from 'My data'"). The same text goes into the export.

**What is recorded (MINE; needs an ADR-097 amendment, the export format version changes).** For every recipe and data file used: the place id and label, the path inside the place (never the absolute server path: it names a user and means nothing elsewhere), the content hash (the recipe file-set hash of ADR-089, the data file hash), and for a pulled place its source (host, project, version string if the provider gives one). The identity for reproduction is the hash plus the original recipe, which the export always carries (M417 point 1: "yes must"). The place id is provenance, text only; on import into another deployment it is shown and never matched (ADR-097 point 7: verification warns, never blocks). Not caught by any audit: a file in a place changed by hand after the opening and before the export, between the hash and the use; only a re-hash at export would show it (not verified whether the export re-hashes: `export_handlers.py:1496-1502` not read).

## 7. Writes: where, and what the user is told

One rule (L12): the only code that writes is a small number of functions that take a place and refuse unless the place's access allows. An architecture test lists them; any other `open(..., "w")`, `shutil` copy or `os.replace` in `app/` fails the test.
- **Save target.** The places with `add` or `replace` of the role. One: no question. More than one: "Save to:" with the labels, the first preselected; the user changes it. The deployer's order is the preselection, shown, not a hidden default.
- **Overwrite control (D-0394).** Shown only when the target place is `replace`. In an `add` place an existing name is refused with a plain line (D-0390). So "only in the user's own place" is a property of the place, not of the user, and needs no identity.
- **Deletion.** The app deletes nothing in a recipes or data place; a same-day correction is removed by hand (D-0390). CONFIRM, because "remove it manually" is not possible for a normal user on a shared server (R; FACTS 6 recipe_places flag 4).
- **Nothing writable.** Stored tables need `cache` today (FACTS section 1). A container with a read-only root and no volume therefore needs a tmpfs declared as `cache` (`provider: folder`, the deployer's choice, recorded). A real "nothing at all" needs an app mode that keeps tiers in memory: engine change, OPEN, not proposed here, and I would not build it before the need is shown.

## 8. Identity: what "the user's own directory" means

| Case | Own directory is | Verified |
|---|---|---|
| Local PC, one person | Her `${HOME}` folder. Truly own. | V (L8) |
| Galaxy interactive tool, IRIDA launch | One container per launch, so the job folder is private to the launcher; the user directory is what the platform mounts for her (the paths she has read/write to) | E, not verified |
| Several users on one server, no login | One folder of the process, shared by all. The labels say so | V (no identity in the code: FACTS section 1; grep for `os.access`/`W_OK` over `app` and `libs` finds none; the earlier recipe-places study found no user header either, not re-run) |
| Posit Connect | A username exists in the Shiny session (ADR-091 point 4) | E, not verified |

**No authentication is proposed.** A per-user place needs the platform to supply the user (a header behind a reverse proxy, Connect's session user, Galaxy's user id). A header is not authentication unless the proxy is the only way in; that is a deployment security statement. Under this design the deployer who wants separation runs one process per user (one deployment file each, `${USER}` in the paths) or accepts the shared label. If the owner later wants one process for many users, the change is: `server()` resolves the user place per browser session, and the 23 `user_data` calls and the `SessionManager` line (F1, F3) take the resolved place; the file would gain one key then, not now (a reserved but unused key is the dead key ADR-091 point 6 deletes). "Only specific users may modify common recipes" (D-0393 point 3) is met today only as "only the app whose deployment lists the place as `add` or `replace`", plus the operating system's permissions (P2 of the recipe places table, option A with C as a net).

## 9. Data Import, bundle import, sessions, audit, BLUEPRINT, Gallery, stored tables

| Item | Under design A | Tag |
|---|---|---|
| **Data Import** (user space HOME) | Writes only into a data place with `add` or `replace`; never to a recipe's `source.path` outside a place (F7: a `source.path` outside every declared data place is refused at the check, with the place list in the message). In an `add` place an existing file is refused; in a `replace` place the overwrite is allowed (today's `os.replace`, `data_import_check.py:238-272`). The control stays under `testing_mode` as today until the owner says otherwise. | MINE; the overwrite itself OPEN |
| **Data Import overwrite** (task DATA-IMPORT-OVERWRITE, no ledger line) | The point of no return is the replace; what checks it today is the verdict stage before it, which does not keep the old file or count the sessions that used it. Options for the owner: (a) replace, with the line "N saved sessions were made with the old file and will no longer match"; (b) replace but move the old file to `<place>/_replaced/<name>_<hash8>` first (never lost; a write, and the folder grows); (c) refuse replace everywhere for data (a corrected file is a new table id: breaks the recipe). (a) is the minimum for transparency; (b) is the one that keeps a published figure re-creatable. | OPEN |
| **Bundle import** (HOME) | Writes the recipe into a recipes place with `add` or `replace` and the data into `user_data/_imports` as today (`bundle_importer.py:252-276`, V per FACTS). No such place: the import is refused with one line naming what is missing. Its name `<id>_imported_<time>` is not `name_date` and is a NEW id on each import of identical content, so two imports of the same bundle are two recipes with different hashes (the file name is in the fingerprint, recipe_places flag 2). The alternative: import under the dated name carried in the bundle, refuse when it exists and say "the same content is already present". | OPEN (P9) |
| **Sessions** | `user_data/_sessions` as today (CONFIRM); present only when `user_data` is declared; the session panel flag with no `user_data` stops the app at start. Identity: section 8. | CONFIRM |
| **Audit folder** | Inside the session folder (L4); needs `user_data` with `replace`; the plain error when it cannot be written (D-0340) comes from the place probe at start and from the write function, not from a traceback. Ghost save on with no `user_data` is a start error. | DECIDED + MINE (start check) |
| **Stored tables** | In `cache`, rebuildable; keys are content keys (ADR-089), so a shared cache between users is safe by construction (R; the keys cover recipe and data hashes, V by FACTS 3). Moving them out of `user_data/anchors` is CONFIG-CACHE-LOCATION-1. | MINE (decision of that task) |
| **BLUEPRINT's fixed folder** (user space BLUEPRINT) | Removed (`blueprint_handlers.py:975-977`, `:2685`). BLUEPRINT lists the recipes places like HOME and saves into a writable one; "new recipe" asks the target when there are several. With no writable recipes place it opens read-only and the save control is absent with the reason. This answers ADR-091 gap 1; its target design (draft in user data, explicit publish) fits: a draft is a recipes place with `replace`, publish is a copy into a place with `add` (an `add` place refuses an existing dated name). | MINE; touches D-0102 not at all |
| **Gallery index** | Rewritten at start only when the Gallery is on (`bootloader.py:226-237`), which is a write into a place declared `read`. Either the index is built at release time and shipped, or it moves to `cache`. Until then the `gallery` role is documented as "the app may write its index here". | CONFIRM (the doc says read-only, `deployment_guide.qmd:223`) |
| **Feature against place** | Fail at start when a flag cannot work at all (session management or ghost save with no `user_data`; ingestion on with no writable data place and `testing_mode`); inform, do not stop, when it is partial (BLUEPRINT with only read recipe places; the deployment info panel says so). | MINE; the owner should confirm where "cannot work at all" ends |

## 10. Validation at start, packaging, testability, migration

**Start (fail fast, all problems in one message, `exit_if_errors` as today).** Closed role keys; the old `locations` and `deployment_type` keys refused with the new names (L10); ids unique; each path expanded (L8); each required place exists and is a folder; each `add`/`replace` place passes `os.access(W_OK)` (a probe with a real file would touch a folder that someone else maintains, so I do not propose it: the first real write failing is reported plainly); each `read` place that the process CAN write is noted in the deployment info panel ("declared read-only; the operating system would allow this app to write", an inform, not a refusal); `user_data` and `cache` created here if declared and missing (not per browser session: F1); duplicate recipe ids; the default recipe resolves; the flags against the places (section 9). Limit, reasoned and not run: as root (the Dockerfile has no `USER`) the permission bits do not stop a write, only a read-only mount does; the probe I ran was as a normal user.

**Packaging (what is package data).** Two kinds, never mixed.
- Code-owned resources, found from the code root and not from the current folder: `config/app_features/*.yaml`, `config/ui/theme.css` and `config/ui/sidebars/`, `config/palettes.yaml`, `config/deployment/templates`, the vendored `app/src/www` (already beside `main.py`, `main.py:15`). The relative reads are at `bootloader.py:295, 375-376, 868, 946`, `ui.py:22-23` (V). This is CONFIG-APP-RESOURCES-1 (`tasks.md:199`, ADR-091 gap 2).
- Operator-owned content: everything in places. Shipped demo recipes, test data and gallery examples are content, not code: in the repository checkout and in a container they are baked places; in a PyPI install they would be an optional content package or not shipped.
- The dev fallback (F6) should only apply from a repository checkout; elsewhere a missing deployment stops the app with the path of the template. MINE, to confirm.
- PyPI needs the `app` rename (F5) and the nine libs published or merged: a separate decision; the design above does not need it.
- Container: repair the Dockerfile (F4), declare `VOLUME`s for `user_data` and `cache`, set a non-root `USER` (then the permission probe is honest), no default deployment inside the image that points at demo data.

**Testable without a browser (V where an equivalent test exists, otherwise R).**
1. Parse and validate the places block: `tmp_path`, pure functions, including every refusal (no `cache`, duplicate id, unknown role, `read` on `user_data`, old keys).
2. Access: chmod 555 folders for `read` and refusal paths (skipped when the test runs as root; document it), write functions refuse `read`, refuse an existing name in `add`.
3. Discovery over two `tmp_path` places: duplicates refused, newest per name, an absent optional place.
4. Two users: two `Bootloader` objects on two deployment files sharing a common `add` place; second add of a name refused.
5. Galaxy: `_GALAXY_JOB_HOME_DIR` set to a `tmp_path` (the connector tests already do this style, `libs/connector/tests/test_connectors.py`, 27 tests, V by count). IRIDA: a local HTTP stub, once the pull exists.
6. A "nothing written outside" test: run opening, export, Data Import and bundle import on a tree where only declared writable places exist and compare the tree before and after.
7. Architecture tests: no `get_location(` string keys outside the resolver; no literal `config/data_analysis_recipes`.
8. `test_shipped_deployments.py` already starts every shipped file (V) but skips `*_template.yaml` (`:14`); the two templates need the same start check or they rot (the contradictions of FACTS section 8 are that rot).
Not testable without the real thing: a container with `--read-only` (CI with podman or docker), Posit Connect storage, Galaxy's variables, ACLs, NFS timing, root bypassing chmod.

**Migration of the seven shipped files (one pass, scripted, no alias).** `locations` becomes `places`; each path gets an `access` that the script cannot know, so it proposes and the owner or deployer confirms: `local`, `retest`, `pipeline_test` (development: recipes and data `replace`, `user_data` and `cache` `replace`, gallery `replace` for the index), `web-demo` and `demo-vetinst` (static: recipes and data `read`, no `user_data`, `cache` `replace`; to confirm against their app features), `connect_template` and `deployment_template` (rewritten as commented templates, one per case of section 4, start-tested). `deployment_type` and `runtime.python_interpreter` (D-0263, still in seven files) go in the same pass: two decided changes on one script (CONFIRM). The docs of FACTS section 8 (`deployment_guide.qmd`, `connector.qmd`, `environment_variables.qmd`, `docs/troubleshooting`) are corrected in the same change.

## 11. The recipe places table, P1 to P11, answered inside this design

| P | Answer in design A | Tag |
|---|---|---|
| P1 model | M1 is design A with two recipes places (`read` and `replace`); M2 adds the maintainer app whose common place is `add`; M3 is one place with `replace` and one user per process. One mechanism covers all three; no model is built into code. | OPEN for the owner |
| P2 specific users | Only through the deployment (a separate maintainer app) and the operating system; no identity | CONFIRM |
| P3 same name in two places | Refused, both named (section 6) | MINE |
| P4 old versions | Not a place feature. An "older versions" folder is another recipes place with `read` and `required: false`, switched on by the user's selector switch; the app moves nothing into it (the move would be a write into a shared place) | OPEN |
| P5 same-day second correction in a shared place | Refused by `add`; the maintainer removes it outside the app | DECIDED (D-0390) |
| P6 replace in own place | The overwrite control, only in a `replace` place, with the "N sessions will no longer open" line | MINE |
| P7 recipe identity | Unchanged by this design; the record carries both fingerprints | OPEN (D-0393 open point) |
| P8 self-contained dated version | A copy into any place takes every file it reads (one function for final save, copy to own place, audit recipe) | MINE |
| P9 bundle import name | Section 9 | OPEN |
| P10 copy of the recipe in the session | Yes; D-0340 puts the audit recipe in the session folder; this design needs `user_data` | CONFIRM |
| P11 words | Labels come from the deployer; access words from the app: "you cannot change these", "you can add files", "you can add and replace". On a shared process: "shared by everyone using this app" | MINE (user viewpoint decides the wording) |

## 12. Pitfalls and silent changes

1. A duplicate resolved by order (rejected above): silent change of which recipe runs.
2. A recipe `source.path` outside the places (F7): reads or writes beyond the perimeter. Fix by refusing it.
3. A `read` label on a folder the operating system lets the process write: the user trusts a protection that is not there. Inform in the info panel; the real protection is a read-only mount.
4. A consortium recipe updated in place between two sessions with the same id: the hash differs; today only a warning (`session_handlers.py:597-602`); D-0362 not built. A consortium place that updates in place breaks "same recipe, same result" unless dated files are the rule there.
5. Data replaced under a running app: stored tables are keyed by content, sessions by recipe and data hash (`session_manager.py:305-308`), so a replaced file makes old sessions not match; whether the user is told is not verified.
6. A pulled place (API) that changes between two starts: the record carries the content hash, but a version string is only as good as the provider's.
7. `required: false` hides a missing place from the list: the "not reachable now" line must be in the selector and in the opening line, otherwise a run on partial recipes looks complete.
8. A network provider conflicts in spirit with ADR-071 rule 1 (the app must work with no outbound network): it is opt-in per deployment and must never be a default. Flag for the owner; the rule's text was about assets.
9. Two decisions in one script (places and D-0263): if one is reconsidered the script is shared.
10. What an audit or test would NOT catch: root bypassing chmod, ACLs, a share that is writable only on some runs, a hand edit after the hash, a header-based identity that a client can forge, the real behaviour of Galaxy, IRIDA and Connect.

## 13. Recommendation

**Design A**, with the first steps shared by every design so each leaves a working app:
1. The pure name module and the sorted discovery and default (recipe_places steps 1 and 2; F8 of the old study).
2. One recipe-path function replacing the 13 rebuild sites, and the places object replacing the string `get_location` keys (F3).
3. The start validation and the creation of `user_data` and `cache` at start (F1, F2), on the existing five keys still.
4. Code resources from the code root; Dockerfile repaired (F4).
5. The `places` block, the migration of the seven files, the `access` words, the duplicate refusal, BLUEPRINT on the places.
6. Write functions with access, Data Import and bundle import on places; the export record.
7. Rediscovery after D-0184 is built.
Why A and not B: B needs a hard-coded `own` layout and a third layer the moment nothing is writable, and grows into A when a provider or a deposit directory is needed. Why not C: it cannot say read-only, which is the first thing the owner asked for. The effort is information only (principle 10).

Where it reconsiders a decision: ADR-048 section 3 (five required location keys, a single path per key) and section 5 (`resolve_paths` returns five paths); ADR-091 gaps 1 and 2 (answered, not reconsidered); ADR-071 layer 2 (consistent) and rule 1 (qualified by an optional network provider); ADR-097 (the export format gains place and hash fields); ADR-092 (unique id now spans places). It does not reconsider D-0333, D-0340, D-0390 to D-0394, D-0102, D-0263. It changes the meaning of `data_lookup: data_analysis_recipe_paths` (a recipe path must lie in a declared data place), which no ledger line decides.

## 14. To decide first (ranked)

1. **The model and its words**: places with three access words (`read`, `add`, `replace`), a duplicate is refused, there is no search order (section 6). Everything else follows from this.
2. **Confinement**: may a recipe's `source.path`, and Data Import, reach outside the declared places? (F7). Today they can; the design says no.
3. **Nothing writable**: is a deployment with no writable place a supported case, which would mean tiers in memory (engine change), or does the app require a writable `cache` and say so?
4. **Data Import overwrite** (a, b or c, section 9) and **bundle import naming**: these two touch what is recorded for a published figure.
5. **Who may write the common place**: the maintainer app only, the operating system as the net, no identity (P2).
6. **A place that changes while running** (rediscovery events) and whether D-0184 is built first.
7. **Fail or inform** for a flag that needs a missing place (section 9, last row).
8. **Whether PyPI is a goal** (needs the rename of `app`), and whether the dev fallback may exist outside a checkout.
Can wait: the provider `url`/API pull (no code exists, no platform verified), identity per user, old-versions switch, the Gallery index move, a `VOLUME` set-up for each platform.

What the owner must be told to choose well: the app cannot tell users apart, so "own" is shared on a shared server; `access` is the app's rule and only a read-only mount is enforcement; a name in two places is refused and what she gives up by letting order decide; a pulled place is a new dependency and a new network use; Data Import overwrite loses the old file today; a container does not build as written.

## Not verified
Any run of a container, Galaxy, IRIDA, Posit Connect, PyPI, two users, a read-only mount, root and `os.access`; whether the Galaxy job variables exist in GxIT; whether Connect supplies a user name; whether the export re-hashes data at export; whether a session of old data is told it no longer matches after a replace; the build error of the Dockerfile (read only); the order of `glob`; that `web-demo` and `demo-vetinst` need no `user_data` (their app features not read); the exact text of the docs I name as contradictory (taken from FACTS section 8, not re-read).
