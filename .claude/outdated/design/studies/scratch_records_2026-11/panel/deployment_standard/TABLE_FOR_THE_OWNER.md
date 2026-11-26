# The written deployment standard: the structure, in one table for the owner (2026-11-21; your order with decision D-0413)

## 0. How to read this

- Your order (D-0413, your words): "And I think we will need to write a deployment standard as we are doing for recipes if its not done so we can track of the options for deployment". The first step you asked for: a study and a draft of the STRUCTURE of the document, shown to you as a table. No key list is built before you have seen it.
- Done: a scout surveyed every key of every deployment file and app features file (`FACTS.md`). Three viewpoints then proposed a structure: the architect (`architect.md`), the developer (`developer.md`) and a deployer who is not a developer (`deployer.md`). All files are in `tmpAI/panel/deployment_standard/`. I (the writer of this table) merged them and re-checked five facts myself (marked RUN below).
- Nothing is built. Nothing is decided by this table. Everything marked "proposal" is a viewpoint's choice, not a rule.
- Labels: RUN = a command was run and gave this. READ = read at the file and line given. REASONED = a conclusion, not run. When two inputs disagree I show both and say "not settled".
- Your rule is applied: each option is judged on its merit. "Reconsiders a decision?" is its own column, information only, never a reason for or against an option.
- Terms, the first time: the **spec file** is the machine-readable list of keys (a YAML file the checker reads, like `recipe_spec.yaml` for recipes). A **key** is one setting name in a file. **Generated** means a script writes the text from the spec file, so a person never types it twice. **Allowed-key list** is your D-0412: an unknown or old key is refused at start with a plain line.
- The detail stays in the three viewpoint files. This table points to them.

## 0a. Added after your words on one specification for all cases (2026-11-21)

Nothing here is decided. Labels as in section 0: RUN, READ (file:line), REASONED. NOT RUN = I did not run it.

### A. Your words, and what they change for the structure

Your words (verbatim): "Example 2 ok so the user can download eg on local pc ... eg. a read only container we can bind paths so we can make it work so the user can save where the user is allowed ... we just need to have paths within the container to allow the binding. Why should I choose one ? we need a description of how to deploy that can be used in all cases = a deployment specification for me they seem complementary no ? we need to cover all the cases with one unique deployement specification (like we do for the recipes)"

What it changes for the structure, in two sentences:
- The standard does not show designs A, B and C of the deployment study as rivals to pick from. It is one specification; the use cases are a table of options inside it, with one template per use case (part B below).
- In a container the places are paths inside the container; the person who runs it binds host folders to them (part C).

The review session's reading of the structure: the specification is built on named places with an access word (design A of the deployment study); the shortened layouts (design B) are templates of use cases inside it; design C is not a final state. You have since answered "A yes" (your words, 2026-11-21, relayed by the coordinator): design A, named places with an access word, is accepted as the base. Your further words: "we need to have this specification in the design - no document that is permanent should be left in tmp". So the written specification lives in `.claude/design/` (next to `recipe_format_spec.md`) and its machine-readable key list beside `recipe_spec.yaml` in `libs/utils`; this answers section 5 (where things live) and section 8, choices 2 and 11, in principle (marked there). Your question "where is the cache in A? in user? sessions?" is answered in part F.

### B. The use case templates

Each cell comes from the deployment study (`tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md`, tables 3a and 3b and section 5) and its `FACTS.md`. Where the study has not settled a cell I write "open choice N" (N = the number of the study's section 5) and do not choose. The row numbers are the study's rows (your list is in `ORDER.md`; rows 12 to 17 are cases you did not list). Rows 18 and 19 of the study (a list read again; a newer dated recipe) are behaviours, not deployment cases, and are not repeated here.

"Closest shipped file" means the file that comes nearest to the case today. It is not a tested example (READ in `config/deployment/`; the template files are not start-tested, section 7).

| Row | Use case | Where the recipes are read | Where the data is read | Where the user can save | How a result is kept | Closest shipped deployment file | Still open for this case |
|---|---|---|---|---|---|---|---|
| 1 | Consortium recipes, read-only for the user | The consortium place, access read | The consortium place, access read | Nowhere through this app | A download to the user's own computer | `config/deployment/local/local.yaml` (one recipes folder; "read-only" only if the operating system forbids writing) | Choice 1 (named places), choice 3 (same name in two places) |
| 1b | The maintainer of the consortium recipes | The consortium place | The consortium place | The consortium place, new dated files only, in a separate app for the maintainer | A new dated recipe file (D-0390, D-0391) | none | Choice 1; choice 11 (the word `add`); how "only specific users" is done without a login (P2, not numbered) |
| 2 | The user's own directory (own data, export and import of recipes, sessions, audit) | The shared places and the user's own recipes place | The shared places and the user's own data place | The user's own places only | A download to the user's own computer; sessions and the audit folder inside the user's place (D-0340) | `config/deployment/local/local.yaml` (one folder per kind; no second place) | Choices 1, 2, 3, 6, 7, 8, 9 |
| 3 | Static web page: one recipe, one data location updated now and then | One recipe, named by `default_data_analysis_recipe` | One data folder, filled by the pipeline outside the app | Today a writable user folder is still needed (flag F1); for the user: nowhere | A download to the user's own computer (your words) | `config/deployment/demo/web-demo.yaml`, `demo/demo-vetinst.yaml` (both name a default recipe) | Choice 5 (nothing writable), choice 4 (where data may be read) |
| 4 | Web page with exploration, nothing written or saved | As row 3 | As row 3 | As row 3 | A download to the user's own computer | As row 3, with the app features file `pipeline-exploration-simple` (named by the study; not checked by me) | Choices 4, 5 |
| 5 | Static pipeline (Galaxy, IRIDA): recipe fixed, data handed by the pipeline | The recipe fixed at deployment (image or fixed folder) | The pipeline's job folder, found by table name (`data_lookup: by_dataset_id`) | Stored tables in the job's work folder | The pipeline's own output, or a download | `config/deployment/pipeline_test/pipeline_test.yaml`; no Galaxy file exists | Choices 4, 5; the fetch step (point 4 of section 2 of the study, not a numbered choice) |
| 6 | Upload from paths the user may reach: shared consortium data, private metadata, own recipes | The shared place and the user's own place | The shared place and the user's own place | Only the user's own place, never the shared one | Sessions and audit in the user's place; a download | none (today only a browser upload and one `raw_data` folder) | Choices 1, 4, 7 (private mark), 8 (Data Import overwrite) |
| 7 | The same, with the access given by IRIDA | As row 6 | Files fetched from IRIDA into a local read place | As row 6 | As row 6 | none; an IRIDA deployment does not start (`libs/connector/src/connector/irida.py:40-52`, READ by the study) | The fetch step (not numbered); choice 4 |
| 8 | Local install: own user directory plus one or several common directories | Several recipes places, each with its own access word | Several data places, each with its own access word | The own places | A download; sessions and audit in the own place | `config/deployment/local/local.yaml` | Choices 1, 3 |
| 9 | An API gives both data and recipe | A local read place filled by a fetch step before the app starts | The same | Only the fetch step writes there | The fetched files are kept; a download | none (nothing in the app can receive data by API today, FACTS section 1) | The fetch step (not numbered); choice 4 |
| 10 | Shipped in a container (your note) | Paths inside the container: in the image, or a host folder bound to a path | The same | Only a bound folder marked writable | As the case it serves | The comments of `assets/containers/Dockerfile:18-30` (two `docker run` examples); no deployment file for it | Choices 5, 11 (write test at start); the container recipe does not build today (flag F16; D-0263 defers it) |
| 11 | Installed from GitHub, later perhaps PyPI (your note) | The repository checkout | The same | As declared | As the case it serves | `config/deployment/local/local.yaml` | Choice 12 (PyPI) |
| 12 | Several users on one server, no login | The same places for everyone | The same places for everyone | The same user place for everyone | Sessions are shared by everyone of that running copy | none | Choices 6, 7 |
| 13 | Read-only container with one writable bound folder | Image or read-only bound folder | Image or read-only bound folder | Only the writable bound folder | Stored tables and user files in that folder; a download | none (part C below is an example of form) | Choices 5, 11 |
| 14 | Container with nothing writable | The image | The image | Nowhere | A download only; today the opening of a recipe stops (`app/modules/opening_build.py:249-254`) | none | Choice 5 (N1, N2, N3) |
| 15 | A pipeline that hands the data by a job folder or by an API | As rows 5 and 9 | As rows 5 and 9 | As rows 5 and 9 | As rows 5 and 9 | `config/deployment/pipeline_test/pipeline_test.yaml` | As rows 5 and 9 |
| 16 | Offline use | Local places only | Local places only | As declared | As declared | none | none numbered; places that may be absent are shown "not reachable now" (study row 16) |
| 17 | Posit Connect | The content folder or an attached path | The same | Connect's storage, if it keeps files (not verified) | As row 3 or row 12 | `config/deployment/connect/connect_template.yaml` (a template; not start-tested) | Not verified by anyone whether Connect keeps files |

Static case, in your words: the user can download, for example on the local PC; a download keeps a result without any writable place on the server.

### C. A container, as an example (PROVISIONAL, not run)

What I read for this part (READ unless marked):
- `assets/containers/Dockerfile`: `FROM python:3.12-slim` (`:32`), `COPY . .` (`:66`), no `USER`, no `VOLUME`, no default `SPARMVET_DEPLOYMENT`, port 8001 (`:87`), start command (`:89-90`). Two `docker run` examples are only comments (`:18-30`): one binds `/data` and takes the deployment file from it, one binds a pipeline folder read-only. The second example names `/app/config/deployment/pipeline`, a folder that is not in the repository (section 10, point 13).
- The Dockerfile does not build as written: it installs `libs/generator_utils` (`:79`), which does not exist (flag F16 of the deployment study; its build was NOT RUN by me). The container update is deferred by D-0263.
- No other `podman run`, `docker run`, compose or `--mount` example exists in `docs/`, `README.md`, `config/` or `.claude/knowledge` (RUN: a grep for these words; the only other hit is an unrelated Galaxy note in `.claude/knowledge/archive/galaxy_integration_prep.md:163`).
- `config/deployment/pipeline_test/pipeline_test.yaml:14-35` and `config/deployment/templates/deployment_template.yaml:15-37` hold the five `locations` keys and `project_root`.
- How `locations` is resolved: `libs/connector/src/connector/filesystem.py:41-50`. A relative path is joined to `project_root`; without `project_root` it stays relative to the folder where the app starts (in the image: `/app`). An absolute path is used as it is. So in a container the paths should be absolute.
- The app finds the deployment file by the environment variable `SPARMVET_DEPLOYMENT` first (`app/src/bootloader.py:10`, `:67`). An app features name can be a short name (`bootloader.py:361-368`).
- Where each location is used today: stored tables in `user_data/anchors` (`bootloader.py:204`); sessions in `user_data/_sessions` (`app/modules/session_manager.py:270-274`); bundle imports in `user_data/_imports` (`bootloader.py:850-855`); the `cache` key is required to be written in the file (`bootloader.py:342-359`) but no code reads it (study FACTS section 1).
- The system temporary folder is also written: exports and uploads use it (`app/handlers/export_handlers.py:1238, 2043`, from FACTS; not re-read by me). A container started with a read-only image therefore needs a temporary folder (`--tmpfs /tmp` below). Whether the app writes anywhere else under `/app` (for example compiled Python files): NOT VERIFIED.

**An example of form; not run; the paths are made up.** It shows the case of row 13 (read-only container, one writable bound folder). It is not a decision. The keys are TODAY's keys.

(1) The `locations` part of a deployment file, with paths inside the container:

```yaml
# EXAMPLE OF FORM, NOT RUN. Paths are made up and are paths INSIDE the container.
# Named places with an access word are proposed by the deployment study and are not decided; today's keys are used here.
deployment_type: filesystem
data_lookup: by_dataset_id            # data is found by table name in raw_data (today's key; its meaning in a container is open choice 4)
default_data_analysis_recipe: "my_recipe_2026-11-21"   # made-up name
locations:
  raw_data: "/srv/sparmvet/data"                  # bound read-only
  data_analysis_recipes: "/srv/sparmvet/recipes"  # bound read-only
  cache: "/srv/sparmvet/work/cache"               # the key is required today, no code reads it
  user_data: "/srv/sparmvet/work/user"            # bound writable: stored tables, sessions, bundle imports
  gallery: "/app/assets/gallery_data"             # in the image; the gallery index is not rewritten when it cannot be written
```

(2) A `podman run` line that binds host folders to those paths:

```bash
# EXAMPLE OF FORM, NOT RUN. Host paths are made up. :ro = read-only for the app; :rw = the folder where the user may save.
# On a host with SELinux (Fedora) a bind may need the option :Z (NOT VERIFIED).
podman run --rm -p 8001:8001 --read-only --tmpfs /tmp \
  -v /host/consortium/recipes:/srv/sparmvet/recipes:ro \
  -v /host/consortium/data:/srv/sparmvet/data:ro \
  -v /host/me/sparmvet_work:/srv/sparmvet/work:rw \
  -v /host/me/deployment.yaml:/srv/sparmvet/deployment.yaml:ro \
  -e SPARMVET_DEPLOYMENT=/srv/sparmvet/deployment.yaml \
  -e SPARMVET_APP_FEATURES=pipeline-exploration-simple \
  sparmvet-viz:latest
```

What the app checks at start for each place today (READ; nothing run by me unless marked):

| Place | Must exist at start? | Must be writable? | What the app checks today (file:line) | What it does today when the check fails | What the review session's reading asks ("exists and can be used as declared") |
|---|---|---|---|---|---|
| `raw_data` | Yes | No (read) | Presence of the key (`bootloader.py:342-359`); the folder must exist (`filesystem.py:23, 53-66`). Not checked: that it can be read; that it is not writable | The app stops with a message that names the key and the path (`filesystem.py:55-66`, `exit_if_errors`) | Exists and is readable. A place declared read that is in fact writable: not asked in the study, so the standard would have to say if it is told |
| `data_analysis_recipes` | Yes | No (read) | As `raw_data` | As `raw_data` | As `raw_data`. Today BLUEPRINT, the bundle import and the recipe upload can write into it (study flags F3, F6, F7, F4) |
| `gallery` | Yes | No (needed only to refresh the index) | As `raw_data` | If the index cannot be written, a line is printed and the old index is used (`libs/viz_gallery/src/viz_gallery/gallery_manager.py:205-208`) | Exists; writable is not needed |
| `user_data` | No (created on demand, `filesystem.py:21-22` comment) | Yes | The key is present (`bootloader.py:342-359`). The folder is made by the session store when the session starts (`session_manager.py:274`, called at `app/src/server.py:149`). Not checked at start: that it can be written | If it cannot be made: a raw Python error at the first click, in each browser session (flag F11, VERIFIED BY A RUN by the architect of the deployment study; not re-run by me). If it exists but is read-only: the opening of a recipe stops with a message (`opening_build.py:160-167, 249-254`, READ) | Exists, and can be written, checked at start with a plain message that names the folder |
| `cache` | No | No | Only that the key is present (`bootloader.py:342-359`); nothing reads it | Nothing | Today nothing; its fate is open (study FACTS, `locations.cache` is unused) |
| the system temporary folder | Yes | Yes | Nothing | An export or an upload fails when it is used | Not named in the study as a place; the standard would say it is needed (`--tmpfs /tmp` above) |
| the deployment file | Yes | No | Four places are tried in order (`bootloader.py:54, 67`); a named file that is missing stops the app (`bootloader.py:263-277`, READ by the survey) | The app stops with a message | Unchanged |

The one check of "can be written" that exists today is `check_store` (`opening_build.py:160-167`): it makes the folder `user_data/anchors` and writes one temporary file when a recipe is opened, not at start. It does not run for the other places. A container run as root ignores folder permissions (flag F11 of the study); a mount marked `:ro` is still refused by the system, and a write into it fails then (REASONED, not run).

### D. What the app would check at start: what the standard would state per place, and what is new work

The standard would state, for each place: (1) its path inside the container or on the machine; (2) what it is for (recipes, data, user files, stored tables); (3) the access word (read, add, replace: study choice 11); (4) must it exist; (5) must it be writable; (6) what the app checks at start; (7) what the app does when the check fails (stop or warn: question 2 of part E); (8) what the user sees on screen for it (question 3 of part E); (9) who binds it when the container is run.

What exists today: the existence check of three of the five folders (`filesystem.py:53-66`) and a write test at the opening of a recipe only (`opening_build.py:160-167`). New work (not started; each waits for your word):
- a check at start that a place declared writable can be written (a small file made and removed), with a plain message that names the place;
- a check at start that a place declared read exists and can be read;
- a plain message at start for `user_data` that cannot be made, in place of the raw error (study safe step S3);
- a place that is declared read and that the app would write to (BLUEPRINT, bundle import, recipe upload) is refused or not offered: this needs the access words, i.e. study choice 1;
- the standard text and the generated key table say all of this per place. Without the access words, only the first, third and fifth points above can be built with today's keys.

### F. Where the stored tables (the cache) are, today and in the specification

**Today (READ with file:line; nothing run by me).**

| What | Folder it is really written to | Where in the code |
|---|---|---|
| Stored tables (the anchors, T1, T2 and T3 Parquet) | `<user_data>/anchors` | `app/src/bootloader.py:204` (start clean-up); `app/handlers/opening_handlers.py:125`; `app/handlers/home_theater.py:335, 503, 536, 1114, 1488`; `app/handlers/data_import_handlers.py:272`. RUN: a grep of `"anchors"` finds 19 places in 6 files: `bootloader.py`, `blueprint_handlers.py`, `export_handlers.py`, `home_theater.py`, `data_import_handlers.py`, `opening_handlers.py` |
| Sessions (assembly record, audit ghosts) | `<user_data>/_sessions/<key>/` | `app/modules/session_manager.py:270-274`, created at `app/src/server.py:149` |
| Bundle imports | `<user_data>/_imports/` | `app/src/bootloader.py:850-855` (`get_imports_dir`), used at `bootloader.py:436`, `server.py:106`, `app/modules/bundle_importer.py:253` |
| Bundle import session | `<user_data>` through `SessionManager` | `bundle_importer.py:295` |

**Is `locations.cache` used by anything?** No. RUN: a grep for `get_location("cache")`, `locations.cache` and `["cache"]` over `app/`, `libs/`, `assets/` and `scripts/` finds only tests (`app/tests/test_bootloader_launch.py:217`, `app/tests/test_retest_data_analysis_recipes.py:209`, `app/tests/conftest.py:50`, `libs/utils/tests/test_path_expansion.py:27, 35, 36`). No production code reads it. The key is only required to be present in the file (`bootloader.py:342-359`), and every shipped deployment and template writes it (for example `config/deployment/local/local.yaml:21`). The template (`deployment_template.yaml:65-67`) still says the app writes the stored tables there; that is wrong (section 2, row 4).

So today the stored tables are in the user place, in a subfolder of `user_data`, the same folder as the sessions. A read-only `user_data` stops the opening of a recipe (`opening_build.py:160-167, 249-254`).

**In the specification: PROPOSAL (not decided).** The stored tables get a place of their own among the named places (here called `store`, a made-up name), separate from the user place (sessions, audit folders, imports). Reason: stored tables can be rebuilt from the recipe and the data and are keyed by content (D-0025, ADR-089); sessions and audit files cannot be rebuilt. They need different care: a place that may be lost or cleaned (a temporary or fast disk) against a place a person keeps and saves. This is also what the key `cache` was meant to be and is not today.

What happens in a deployment where only one folder is writable (options, none chosen):
- (a) Both places are declared inside that one folder (`store` in one subfolder, the user place in another). Works with today's behaviour; the standard says it plainly. Cost: none new; stored tables and sessions share a disk.
- (b) The deployment declares only the user place; the stored tables are kept inside it, as today, and `store` is optional. Cost: two ways to declare the same thing; the standard must say which wins.
- (c) The app stops at start when `store` is missing or cannot be written (study choice 5, N1).
- (d) The tables live in a temporary folder of the running copy and are rebuilt at each start (study choice 5, N2). Cost: a slow first opening each time; stored tables are lost at exit.

Reconsiders a decision? None of (a) to (d) changes D-0340 (the audit folder stays in the user place). The place of its own follows from design A, which you accepted.

### E. Questions this addition raises, ranked

(Removed: the former question 1, "is design A the base"; you answered "A yes", see part A. The study's choice 2, how D-0340 is read, and its choice 10, the order of the change, remain yours.)

1. [new, from part F] Where do the stored tables belong, and what happens when only one folder is writable? Options: see part F: a place of its own (`store`) or inside the user place; and for one writable folder (a) both places inside it, (b) stored tables inside the user place, (c) stop at start, (d) temporary folder. Reconsiders a decision? None of the options touches D-0340; a place of its own follows from design A, which you accepted. Information only. Needs your decision.
2. When a place that should be writable cannot be written (a bound folder marked `:ro` by mistake, a full disk), does the app refuse to start, or start with a warning on screen? Options: (a) refuse at start, naming the place and the path (study N1); (b) start, and warn at once in the info panel and at each action that needs the place; (c) per place, the deployment file says which (a place the app cannot work without stops the start; another only warns). Reconsiders a decision? no (D-0340 asks only for "a plain error when the directory cannot be written", for the audit folder). Information only.
3. A place that is read: do the screen controls that would write there disappear, or show a plain reason? Options: (a) the control is absent, and a line in the info panel says why (the study's rows 3 and 13); (b) the control is shown greyed with the reason beside it ("this place is read-only; you cannot change these"), as the study proposes for row 1; (c) absent in some user spaces and greyed in others. Reconsiders a decision? no (D-0394 limits only the overwrite control, which must exist only in the user's own place). Information only.

### G. Decided by you since this table was written (2026-11-21), for the content of the specification

- The audit recipe is written in the user's own writable place, inside the session, never in the place of the original; the folder is `audit/`, visible, with a warning file, the same warning on screen, and an explanation in the documentation and the help (ledger D-0422, D-0423).
- The same recipe name in two places: identical content is one entry that lists both places; different content is refused, both places named, with a way out in plain words; the app never picks (ledger D-0424). Open: an offer to rename; the same rule for data tables.
- What a recipe's data path may reach is decided by the deployment file; the shipped recipes keep their paths into the test data as an optional default; the local development deployment declares that place (ledger D-0425). Where the deployment does not hold that default data, the recipe opens and the user selects the data (ledger D-0426). Open: a deployment where the user has no way to select data (a static page, a pipeline) and the declared data is absent: the opening stops with a plain reason (ledger D-0427).
- Ordered by you: a study of deployments where no user interacts and the app needs its own place to read and write (a data folder refreshed every week; a pipeline's temporary place; several data files and where each is fetched). It becomes a section of this structure (ledger D-0428).
- No `users` word in the deployment file. What the app saves for a person is in a user place whose path comes from system variables, with one copy of the app per person; a shared place where people save exists only if the administrator declares it; a static deployment on Connect has no user place and no save control (ledger D-0429). Open: a deployer who shares one copy among several people.
- Data Import writes only into a writable data place and never into a read-only place (ledger D-0432 as corrected by D-0433); an upload with the name of an existing data file replaces it, in the user's writable place only, after a plain confirmation, with no copy and no archive (ledger D-0434). One copy of the app per person is sufficient for now, with a warning in the documentation (D-0430). What a user shares is the user's responsibility (D-0431).
- A bundle import writes the recipe and the data into the user's own places, never a shared place; the user gives the name; a name already used there is refused; the app keeps no old copy (ledger D-0435).
- The change to the named places is made with no temporary reader of the old location keys; the old keys are refused with a message that names the new ones; a script rewrites the shipped deployment files (ledger D-0436).
- Two access words for a place: `read` and `read_write`. No separate word for adding or replacing. Read protects the consortium recipes; read_write is the user's directory (ledger D-0437). Open: the write test at start; for data files, refusal or replacement after a confirmation.
- How data reaches the app is defined by the deployment file: a static deployment has no upload; elsewhere the user has a dedicated directory with read and write access (ledger D-0439). Open: whether the browser upload is off unless declared; the list from which a user picks a file.
- The browser upload is off unless the deployment requires it. The write test at start is accepted with conditions: the test file cannot be tampered with, is not executable, and the test can be deactivated in the deployment file. A recipe whose name does not follow the convention: ask for a renaming (ledger D-0440). Open: the switch's name and default; the content of the test file; whether 'ask for a renaming' blocks the opening.
- The write test at start is off by default; a deployment file switches it on; a security check of the practice comes first (ledger D-0441). The naming convention of recipes must be applied; in the worst case recipes are renamed automatically. PyPI: deferred.
- For an interactive user the list of a place is read when the app starts, and a recipe is checked when it is selected (ledger D-0442). Static pages: to investigate (it joins the study of deployments with no user).
- Fonts: the deployment file names the fonts a deployment needs; the app checks them at start; the container recipe installs them (ledger D-0443). To confirm: a missing font is an advice, not a refusal.
- These answer choices 2, 3, 4, 6 to 10, 13 for an interactive user and 14 of the deployment study (`tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md`), and the access words and the default of the write test of choice 11; choice 12 is deferred; open: choice 5 (nothing writable).

## 1. The answer in short

All three viewpoints recommend **one document with two parts (deployment, app features) and one machine-readable key list (the spec file)**, with the key tables of the document generated from that list. This is true in the files:

| Viewpoint | One document, two parts | One machine-readable key list | Where it says so |
|---|---|---|---|
| Architect | yes (variant 1A) | yes: `deployment_spec.yaml`, one checker `deployment_check.py` | `architect.md` section 1, 2 |
| Developer | yes (variant A) | yes: `deployment_spec.yaml` | `developer.md` section 1, 2 |
| Deployer | yes (variant A, "one document ordered by goal") | the tables are "generated reference tables"; "machine-readable list only" for what a deployer does not need | `deployer.md` "One document or two", "Fields per key", "Variants" |

What "agree" covers, exactly:
- It covers: one document, two parts, generated key tables, the theme stylesheet only as a pointer (architect and developer say so; the deployer puts `branding.theme_css` inside the deployment part, which is the same idea).
- It does NOT cover: where the spec file lives (the architect and the developer say `libs/utils/src/utils/`; the deployer did not take a position), where the written page lives (section 5), whether files carry a format number (section 8), and the order of the table of contents (section 3).
- The two other variants were shown and not recommended: two documents with two spec files (architect 1B, developer B, deployer B), and one document with only deployment and app features (developer C). Their pros and cons are in the viewpoint files.

The strongest reason given for one document (architect, REASONED and READ): keys move between the two files (`theme_css` and `ui_banner` went from app features to the deployment file, `renamed_keys.py:36-37`), and rules cross both files (a hidden recipe selector needs a named recipe, `bootloader.py:617-639`). The strongest reason from the deployer: the two files are written together, so a deployer must read one place.

## 2. Why it is needed: where today's documents, template and code disagree

The documents say one thing, the app does another. A deployer who copies the template can write a file that does not start. 11 of the 18 disagreements of the survey (FACTS section C, the full list is there). "RUN" = I checked it myself; the rest is READ from the survey and the deployer's own reading.

| # | What a deployer reads | What the app does | What goes wrong |
|---|---|---|---|
| 1 | Template `deployment_template.yaml:36-37` (RUN): "If absent: app features selector is shown (or defaults to pipeline-static)". Same idea in `docs/workflows/connector.qmd:92`, `ui_app_features.qmd:340-348`, `deployment_guide.qmd:91` | `bootloader.py:164-178` (RUN): with no app features from the kwarg, the environment variable or the file, the app stops with "No app features configured" | The key is left out; the app does not start |
| 2 | Template `:23` (RUN) "shown in app footer" for `deployment_name`; also `connector.qmd:83`, ADR-048:1077. `deployment_guide.qmd:92` says "Not shown" | No screen shows it (FACTS A1 row 2). Removal decided (D-0411), not built | Two documents disagree; time lost |
| 3 | Template `:96-97`, `rules_runtime_environment.md:88-91`: the python path MUST be in the deployment and read by the bootloader | RUN: the only place that mentions `get_python_path` is its own definition `bootloader.py:905`; nothing calls it. Removal decided (D-0263), not done | A key that does nothing is copied into every file |
| 4 | Template `:65-67`, `connector.qmd:75`: `locations.cache` is "written by the DataOrchestrator" | FACTS A1 row 9: nothing reads `locations.cache`; the tables are written under `user_data`. RUN: only a test calls `get_location("cache")` (`test_bootloader_launch.py:217`) | Disk space and rights planned for the wrong folder |
| 5 | Nothing says it | RUN: `connector/__init__.py:40-45`: `deployment_type` "irida" and "galaxy" route to their classes; any other value, a typo too, silently becomes the filesystem connector | A typo is accepted without a message |
| 6 | ADR-048:1106 and `ui_implementation_contract.md:920`: `project_root` is required | `bootloader.py:117-118` (FACTS): optional; without it the paths start at the working folder | A rule says required, the code says optional |
| 7 | Template `:89-93`, `deployment_guide.qmd:77-81`, `connector.qmd:104-108`: an `irida` block, described as working | `irida.py:48-52`: fetching raises "not implemented"; two of its keys have no reader (FACTS A1 row 16) | A dead block is copied; an IRIDA deployment does not start |
| 8 | `environment_variables.qmd:22` "FileNotFoundError", `:26` "AuthenticationError" | `bootloader.py:263-277` and `irida.py:85-102`: both give a DeploymentError | The error a deployer is told to expect is not the one shown |
| 9 | README `:47`: paths are relative to `project_root`, else "CWD" | `branding.theme_css` is relative to the working folder, not to `project_root` (`bootloader.py:868`) | Two path rules, one stated; "CWD" is a word a deployer may not know |
| 10 | `connector.qmd:213-224`: `app_features_override` locks a flag | `bootloader.py:387-388`: any key name is accepted and merged; a typo is not seen | A flag the deployer thinks is locked is not |
| 11 | Template `:28-36`: five app features names | Eight files exist (`config/app_features/`); `bootloader.py:747-749` also omits two | Three names unknown to the reader |

Two more that the deployer viewpoint stressed: an unknown sidebar panel type only prints a warning that may never be seen in a container (`sidebar_validator.py:165-171`), and three of the five location folders must exist on disk while two are only checked for presence (`filesystem.py:53-66`, `bootloader.py:342-359`) while the README says "five required".

Why a written standard with generated tables helps (architect, REASONED): most of these sentences disappear when the text is generated from one list, because there is no second copy that can drift. Prose that explains stays hand-written.

## 3. The proposed structure: the table of contents

The three proposals merged into one list. Reader: D = deployer, R = author of recipes, V = developer. Where they differ, one column per viewpoint (A = architect, Dv = developer, U = deployer viewpoint). A dash means that viewpoint has no such section.

| # | Section (merged) | What it holds | Reader | A | Dv | U |
|---|---|---|---|---|---|---|
| 0 | How to read / Start here | What a deployment and an app features file are, how the app finds them (the four places in order), the tags DECIDED / NOT DECIDED / AS BUILT, the words | D R V | 0 and 2 | 1 | 0 |
| 1 | Find your case | One entry per use case: one line, the example file, the keys you must write, the keys that do not apply, the open choices that touch it | D | 1 | 2 | 1 and 2 (also "minimal files that start") |
| 2 | The files and the start | File kinds, who writes each, what happens at start, what a refusal looks like | D V | 2 | in 1 | in 0 |
| 3 | The deployment file: the keys | Key tables by group | D V | 3 | 4 | 3 (grouped by what I want to do) |
| 4 | The app features file: the keys | Name keys, flags in groups with cascades, selector, automation, blueprint agent, workspaces | D (little), R, V | 4 | 5 | 4 |
| 5 | Sidebar files | Keys `visible` and `panels`; allowed panel ids, generated from the code's registry | V, D who builds an own app features file | 5 (inside part B) | 6 | short part of its own, panel list in the appendix |
| 6 | The palettes file | Its keys, the three shipped palettes, "you cannot choose another palette file" (the path is fixed in the code, `bootloader.py:946`) | D R | 6 | 7 | part of its own |
| 7 | Environment variables | Each: read where, which key it overrides, secret or not, old names refused | D V | 7 | 8 | 6 (and a table on the start page) |
| 8 | Theme stylesheet | A pointer only | D | 8 | 9 | inside the deployment part at `branding.theme_css` |
| 9 | Rules between keys | Combinations that stop the app (selector hidden needs a named recipe; override against cascades; `data_lookup` and the Data Import screen), each with what the user sees | D V | 9 | in 5 | 5 |
| 10 | When my file is refused | Each refusal text with its cause, how to read one | D | in 10 | 10 | 7 |
| 11 | Check catalogue | One row per check: id, severity, text, who runs it, test name | V | 10 | in 12 | - |
| 12 | Old and removed keys | Replacement table with the decision number; tombstones with expiry | D V | 11 | 11 | in 7 |
| 13 | Use cases: the matrix | Generated table key against case; each cell a value, a dash, or "NOT DECIDED, choice N" | D V | 12 | in 2 | in 1 |
| 14 | Open choices (NOT rules) | The 13 choices and fonts as options with consequences | D, the owner | 13 | 3 | 8 |
| 15 | Worked example files | One file per case that starts; a test starts each | D | via the shipped files | 13 | in 1 |
| 16 | How the standard is kept true; format version | The checks and tests; the number rule | V | 14 | 12 | in the appendix |
| 17 | Appendix | Code readers, tests, decision numbers, history | developers, authors | in the key table | in the key table | 9 |

Where the viewpoints really differ:
- Where "Open choices" sits: architect near the end, developer as section 3 (early), deployer as section 8 (late, boxed). Not settled.
- A section "what the code accepts today and must stop accepting": the architect leaves it out on purpose (it becomes a task list that goes stale; the 18 disagreements go to the task). The others did not propose it either.
- The deployer wants the key tables grouped by what the deployer wants to do (identity, folders, default start, branding, limits, connector, other), the developer by the order of the file. Not settled.

## 4. What is recorded for every key

Her eight fields come first (all three viewpoints keep all eight; for "which code reads it" they differ, see the note). Then the fields the viewpoints added or removed.

| Field | What it is, in plain words | Who needs it | Proposed by |
|---|---|---|---|
| 1. Meaning | One plain sentence: what this key is. The only place the sentence is written | deployer | yours (D-0413); all three |
| 2. Purpose | Why I would set it. Where the key is a name: which kind of name (identity, short name, title, description, help, column name, figure text: the seven kinds of D-0406) | deployer | yours; architect splits it in two (`purpose`, `kind_of_name`); developer uses `kind` (name, description, path, enum, number, flag, secret) |
| 3. Allowed values | For a closed list, each value with what it means and what it costs or changes on screen (for example `by_dataset_id` shows "Data location (provided by deployment)") | deployer, checker | yours; architect adds `means` and `consequence` per value (the standard informs, no preferred option) |
| 4. Default | What happens when the key is absent: a default, a refusal with its check id, or a silent default. Plus "silent: yes or no" | deployer | yours; architect adds `silent`; developer adds `absent_behaviour`; deployer wants the consequence, not only the value |
| 5. Who sets it | Deployer, author of recipes, developer, the pipeline, the container image, an environment variable | deployer | yours; all three |
| 6. Which code reads it | The module that reads the key | developer | yours. NOT SETTLED where it goes: the architect keeps it in the key table as a module name (a test checks the module contains the key); the developer keeps it in the table as module and function; the deployer wants it in the appendix, not in the main table. All three say: no line numbers, because they move |
| 7. Which screen shows it | Screen in user-space words (HOME, BLUEPRINT, Gallery, Test Lab) or "no screen" | deployer | yours; all three. Architect: cannot be tested without a browser, so a reviewer checks it |
| 8. Options per use case | List of {case, value, state: decided / NOT DECIDED choice N / not applicable}; feeds the matrix | deployer | yours; all three |
| Key path and file kind | `branding.banner.ui_label`; deployment, app features, sidebar, palettes, environment | all | architect, developer |
| Type | String, path, number, switch, list, block | checker | architect, developer |
| Required or optional | Required, optional, or required when (with the check id). Today `project_root` is "required" in ADR-048:1106 and optional in code | deployer | architect, developer, deployer |
| Checked how, and the refusal text | Refused / warned / not checked, with the check id and the line the deployer sees. "Not checked: a typo here is accepted and the default is used" is said plainly | deployer | architect (`checked how`), developer (`check`), deployer ("what I see when it is wrong") |
| Path base | For path keys: relative to the project root, the working folder, or the file's own folder (they differ today, row 9 of section 2) | deployer | architect, developer, deployer ("must exist, must be writable") |
| Overridden by | The environment variable or launch argument that overrides the key | deployer | architect, developer, deployer |
| Secret | yes/no. File keys never hold a token | deployer, IT | architect, developer, deployer |
| Status and decision number | As built / reserved, no reader / removal decided (D-0263, D-0411) / NOT DECIDED (choice N). A "removal decided" entry needs a removal task (agent principles rule 4) | deployer, developer | architect, developer. Deployer: a key that does nothing is removed from the standard or marked "no effect today" |
| Result effect | `none`, `which data or recipe is read`, `what the export holds`: which keys can change a result (for example `data_lookup`, the two folder keys, `default_data_analysis_recipe`, `testing_mode`) | deployer, scientist | architect only (proposal; "fits ADR-090: nothing changes a result silently") |
| Open-choice marker | `open_choice: N` on a key that depends on an undecided choice | deployer | architect (`open_choices`), developer (`status: open`), deployer ("depends on open choice N") |
| Example value / template value | The value the generated template uses; `include`, `comment` or `omit` | generator | architect, developer |
| Old names | The old keys this key replaces; the refusal line uses them | checker | developer (`old_names`); architect holds them in a `renamed` table |
| Since which version | NOT SETTLED. Architect: REMOVED as a field, because the app has no version per key; the format number answers "since when". Developer: keeps `since` (format version) and `decision`. Deployer: only for renamed keys, in the appendix | developer | disputed |
| Long note | A longer text, only when needed | developer | developer (`doc_text`). Not proposed by the others |
| Test that proves the key | Developer lists it and does not recommend it (it drifts); the read-test is the proof | developer | developer |

Removed from her list by a viewpoint: nothing as a field, except "since which version" (architect). Not added by anyone: line numbers.

## 5. Where things live and what is generated

| Thing | Where: architect | Where: developer | Where: deployer | Written by hand or generated |
|---|---|---|---|---|
| The spec file (key list) | `libs/utils/src/utils/deployment_spec.yaml`, next to `recipe_spec.yaml`, same `package-data` line | same place | no position | hand-written once; the code reads it |
| The checker | `libs/utils/src/utils/deployment_check.py`, next to `recipe_check.py` (pure; panel types and recipe names injected from `app/`) | same place and name | no position | code |
| The written page | A draft in `.claude/design/` while you review (as the recipe text was); then rules to `.claude/rules/` (only with your confirmation) and the reference to `docs/reference/` | `docs/deployment/deployment_standard.qmd`, because "a deployer is not a developer" | the deployer reads in the user documentation (REASONED from its wish: one entry point, no developer words) | prose hand-written; key tables generated |
| Key tables of the document | generated file with a header "generated, do not edit"; a test fails if the committed file differs (D-0399 wording) | `docs/deployment/_keys_deployment.qmd` and `_keys_app_features.qmd`, committed | generated reference tables inside the document | generated |
| Template file `config/deployment/templates/deployment_template.yaml` | generated from the spec (an app features template does not exist today) | generated (its comments) | no position | generated |
| Environment table (`docs/reference/environment_variables.qmd`) | generated | generated | one table on the start page | generated |
| `config/deployment/README.md` key table | generated; the folder layout text stays hand-written | generated key list | no position | generated part and hand-written part |
| Flag matrix (flag against app features file) | derived from the shipped files only, so it cannot disagree with them | from the spec descriptions plus the shipped files | no position | generated. NOT SETTLED: the sources differ |
| Use-case "keys for my case" and the matrix | generated from `use_cases` and each key's options | matrix generated | matrix generated | generated |
| Refusal texts | NOT written to a file: the checker reads the sentence from the spec at run time; one test per entry | built at run time from the `renamed` table | one source for the standard and the app | generated at run time |
| Worked example files | the shipped files themselves, included in the document; tested | `config/deployment/`, one per case that starts, each started by a test | one per case, each "Use this if ..." | hand-written, tested |
| Sidebar files, palettes file | inside (sidebar in part B; palettes a short part); panel list generated from the registry | short sections of the same spec | parts of their own | as above |
| Theme stylesheet | outside, pointer to `rules_css_style_spec.md` | outside, pointer | pointer at `branding.theme_css` | hand-written |

Answered by your words of 2026-11-21 ("we need to have this specification in the design - no document that is permanent should be left in tmp"): the written specification lives in `.claude/design/` (the architect's place, next to `recipe_format_spec.md`); the key list beside `recipe_spec.yaml` in `libs/utils`. The text below is kept as the record of the three proposals. Whether the page is also published as a user page in `docs/` later is not answered.

Plainly: **the place of the written page is proposed differently**: the architect says a draft in `.claude/design/` (final reference in `docs/reference/`); the developer says `docs/deployment/`. Not settled. The developer's reason: the recipe text sits in `.claude/design/`, but a deployer is not a developer. The architect's reason: the recipe text spread the same way, and it rules only with your confirmation.

Today there is no generator for any of this (FACTS D: no docs, cheatsheet or template is generated from `recipe_spec.yaml`; D-0399 decided it for the Gallery, not built). The architect asks whether the deployment generator and the Gallery cheatsheet should share one helper and one marker line (choice 12 in section 8). The developer notes the generator is new tooling; the first generated template will differ in wording from the hand-written one, and you will see a diff.

## 6. The use cases and the open choices

**How use cases appear.** All three viewpoints propose both a matrix (use case against key, generated) and worked example files. The differences:
- Architect (5C): a `use_cases` list in the spec with stable ids; a generated "keys for my case" view per case; the matrix as an appendix; examples are the real shipped files, so a test checks them. A case with no decided design shows "no example: NOT DECIDED, choice N". The use-case list needs your confirmation (it says which cases are yours from block M430 and which an agent added).
- Developer (variant C): the matrix is generated; an example file exists only for a case with a decided path that STARTS today, and a test starts it. A case with no working path appears in the matrix as "not available" and no file.
- Deployer: both; each example begins "Use this if ..." and "What the user of this deployment can and cannot do". Where there is no example, the standard says "no worked example yet", not a gap.
- Answered in principle by your words of 2026-11-21 (section 0a, parts A and B): the standard covers all cases with one specification, so every use case gets a template row, also a case that does not start today; such a row says "none" for the example file and names the open choice. The developer's line "a case with no working path appears in the matrix as 'not available' and no file" and the architect's line "no example: NOT DECIDED, choice N" are the two ways to write that row; which wording is used is not settled. Not answered: which cases get a tested example file in the first version.

**What exists today** (FACTS E, 19 rows of the deployment study's table): a shipped file that is the closest example exists for cases 2, 3, 4, 5, 11, 15 and 17 (the architect lists exactly these seven; the developer's text says examples exist "for only 5 of them"). NOT SETTLED between 7 and 5; both counts are "closest file", not a tested example. No file exists for the others (1, 1b, 6 to 10, 12 to 14, 16, 18, 19). IRIDA does not start (`irida.py:48-52`); no Galaxy file exists.

**How an open choice is shown** (the 13 choices of `tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md`, plus the font question, which that table lists as choice 14):
- A separate section generated from an `open_choices` part of the spec (architect) or from keys with `status: open` (developer): id, question, options with what each gives and costs, link to the study table. No "recommended" column: the standard informs, the study recommends.
- The checker never reads the open choices, so a key that belongs only to an undecided design is not in the allowed list; a file that uses it is refused with "this key is not decided yet" (architect), or "unknown key" (developer). Proposal of both: refuse until decided. The developer names the other way as a question for you (accept with a printed warning) and says it is "silent-ish".
- A key that exists today and depends on a choice keeps its row, status "as built", and the marker "depends on open choice N" in the key table and in the matrix cells.
- A test (architect) says no key named in an open choice appears in the allowed list.
- When you decide a choice: add the keys with the decision number, add `renamed` entries for what they replace, move the format number if a meaning changed, migrate files by script, remove the choice from the open list.

The deployer wants a box that looks different from a rule. Mock-up (proposal, wording not decided):

```
+--------------------------------------------------------------+
| NOT DECIDED (open choice 5). The standard does not choose    |
| for you.                                                     |
|                                                              |
| Question: what happens when nothing can be written (a static |
| page, a read-only container)?                                |
|                                                              |
|  Option A                      Option B                      |
|  The app stops at start with   The deployment file says      |
|  a plain message.              "this session only"; nothing  |
|                                is kept when the page closes. |
|                                                              |
| For each: what the user sees, what you must prepare, what   |
| cannot be undone.                                            |
|                                                              |
| Until this is decided: no key for it exists. A file that     |
| uses one is refused with "this key is not decided yet".      |
| Study table: tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md |
+--------------------------------------------------------------+
```

The content of option A and B above is taken from choice 5 of the deployment study (its table, row 14: "either the app refuses to start, or the file declares this session only"); I shortened it for the mock-up. The box shows no default in bold and no default value in an example file (deployer).

## 7. How the standard is kept true

| Check | What it catches | Exists today? |
|---|---|---|
| The check at start (D-0412): unknown or old key refused with the new name | A key the standard does not list, a renamed key | NO. Today: only renamed keys (`bootloader.py:114`), `data_lookup` values, `session_import` keys and presence of the folder keys (FACTS A1). Unknown top-level keys, `deployment_type` values and `app_features_override` names are not checked |
| Every shipped file passes the check (7 deployment files, 8 app features, 8 sidebar, palettes, templates: structure group only) | A shipped file with an unlisted or old key; the two customized deployments are included (D-0411 asks for the proof) | PARTLY: `test_shipped_deployments.py` starts the files; the templates are excluded from the start test and get four key assertions (architect, READ) |
| The spec describes itself: every key has all fields, every closed value has its meaning, every decision number exists in the ledger | An incomplete entry | NO |
| Every key in the list is read by the module it names | Keys set and read by nothing (`python_interpreter`, `cache`, `deployment_name`) | NO for deployment; `app/tests/test_dead_config_keys.py` refuses a few dead keys (FACTS D) |
| Every key the code reads is in the list | A key read by code and not written in the standard | NO. NOT SETTLED how (section 8, choice 10): a heuristic scan (small; cannot prove "every key", `assets/scripts/inventory_config_keys.py` says it is heuristic) or one accessor that refuses an unlisted path (exact; large: the developer counts about 27 reads in `bootloader.py` and 13 `.get(...)` outside it, from two greps) |
| No second list of "what is allowed" (a test like `libs/utils/tests/test_engines.py:21-31` for engines) | The lists in the next paragraph coming back | NO for deployment |
| Generated files equal the committed files (D-0399) | The template, tables or environment table drifting from the spec | NO (no generator) |
| Each old or removed key, put in a minimal file, gives the exact refusal line; a tombstone past its expiry fails | A refusal that does not name the new key | NO for deployment |
| Each check in the catalogue has a test that fails when the check is removed | A dead check | NO |
| The wheel contains `deployment_spec.yaml` | The container not finding the spec | NO (the packaging test `libs/utils/tests/test_packaging.py:17-29` covers `recipe_spec.yaml` only) |
| The old-word audit reads the old words from the spec (`assets/scripts/audit_old_words.py --check`) | An old word in docs, templates, comments | YES for its own word list; NOT fed from a deployment spec |
| Every writer of deployment files passes the check (`assets/scripts/create_test_deployment.py` writes `deployment_name` and `python_interpreter`; the test fixture `SPARMVET_TEST_GENERATED_DEPLOYMENT`) | A third writer of the format | NO |

**Several second lists of "what is allowed" exist in the code today** (architect, READ). In plain words: the same list of allowed things is typed in several places, and they can disagree. The architect names: the required flag names (`app_features_validator.py:15-29`), the allowed `data_lookup` values (`orchestrator.py:45`), the connector names typed in the router (`connector/__init__.py:40-45`), the allowed `session_import` keys (`session_manager.py:853`, used at `889-894`), and the app features names typed into a message (`bootloader.py:747-749`, which leaves out two). The old and renamed keys are in at least five places (`app/modules/renamed_keys.py`, `libs/utils/src/utils/legacy_keys.py`, the `renamed` table of `recipe_spec.yaml:83`, `assets/scripts/migrate_config_vocabulary.py`, `assets/scripts/audit_old_words.py`). The architect's point: "an unknown key is refused at start" is ONE code path only if these lists are replaced in the same step as the new check; otherwise the new allowed-key list is one more list that can disagree. (The architect writes "five" in one place and "six places" in another, counting the renamed tables as the sixth: a small inconsistency in the input; the five named above are the lists, the renamed stores are the sixth case.) The developer says the same for `renamed_keys.py`: moved into the spec so that there are not two tables.

The check at start (architect, proposal): ONE call at the head of `Bootloader.__init__`, replacing the line at `bootloader.py:114`; the other start checks stay and are listed in the check catalogue with ids and the same severity words, so the user sees one kind of refusal.

What a deployer must see when a file is refused (deployer, proposal): "Deployment file /path/file.yaml, key `branding.banner.title`: this key was renamed. Use `branding.banner.ui_label`." or "key `deploymet_type`: unknown key. Allowed keys here: ... (closest: deployment_type)." All problems at once, the full path of the file, which of the four places found it, no stack trace, the same text as in the standard.

## 8. The choices for you, ranked

Ranked: first the ones that block writing the structure. For each: the options, what each viewpoint says. "Reconsiders a decision?" is information only.

| # | The question | The options | What each viewpoint says | Reconsiders a decision? |
|---|---|---|---|---|
| 1 | One document with two parts, or two documents? | (a) one document, two parts, one spec file; (b) two documents, two spec files; (c) one document with only deployment and app features, the other files kept where they are | Architect: (a). Developer: (a) (and shows (c) as smaller, with the sidebar, palettes and environment left unchecked). Deployer: (a), with a "start here" page. Cost of (a): longer document, and Tier 1 holds the names of HOME flags (precedent: `recipe_spec.yaml` holds `ui_label` and the Gallery terms) | No. D-0413 itself says "one document with two parts, or two documents (the coordinator proposes, with a reason)" |
| 2 | Where does the spec file live? (Answered by your words of 2026-11-21: beside `recipe_spec.yaml` in `libs/utils`, option (a)) | (a) `libs/utils` next to `recipe_spec.yaml`; (b) `app/`; (c) `config/` | Architect: (a); reason: the check works without `app/`, the connector already imports `utils`, `utils` already ships a data file; (b) needs `package-data` in `app/` and the connector cannot read it; (c) is in no package (FACTS D). Developer: (a), same reasons. Deployer: no position | No. Respects `rules_runtime_environment.md` section 4 (architect) |
| 3 | Does each deployment and app features file carry a format number? | (a) none: the old key is refused by name (D-0412 alone); (b) a number in the spec only; (c) one required key per file kind | Architect: (c), because only a number catches a key that keeps its name and changes its meaning (examples pending: the path base, `data_lookup` under confinement, `testing_mode`); cost: one more key in every file, including users' own. Developer: shows (a) and (c) as information, no pick; cost of (c): 15 shipped files change. Deployer: lists it as its last question | No. D-0412 stands with every option (architect) |
| 4 | How is an open choice shown, and what does the checker do with a key of an undecided design? (Tension with your words of 2026-11-21: if the named places with an access word become the base of the one specification, those keys are its core and cannot be refused as "not decided yet" for ever; this line waits for question 1 of section 0a part E) | (a) a separate section, no recommended option, such a key refused as "not decided yet"; (b) the same, but such a key accepted with a printed warning | Architect: (a). Developer: (a) as its design; names (b) as the question for you (it lets a deployer try, but is "silent-ish"). Deployer: a box, no default, "depends on open choice N" beside the key | No. Keeps D-0413 "WITHOUT deciding the paths and Data Import questions" |
| 5 | The use-case list: which cases, and which get a worked example in the first version? (Answered in principle by your words of 2026-11-21 for the first part: all cases are covered by one specification, with a template row per case, section 0a part B; still open: which cases get a tested example file) | (a) your list (block M430) plus the cases agents added; (b) only cases that start today | Architect: (a), and who may add one is yours (CONFIRM). Developer: examples only for cases that start today. Deployer: asks which cases get an example in the first version | No |
| 6 | A "check my file" command for a deployer, without a running app? | yes / no | Deployer only: its first question, "matters more than anything else for a non-developer"; it found none. Architect and developer do not mention it. The checker is pure code (no app needed), so a command is possible (REASONED); whether one exists today: not verified | No |
| 7 | Keys that do nothing today (set by files, read by nothing): remove first, or list as "no effect"? | (a) remove from the shipped files and template before the standard is written; (b) list them with status "no effect today / removal decided" | Deployer: (a) or "no effect" in the standard, decided before. Architect and developer: (b), a `status` field with the decision number. Two are already decided: `runtime.python_interpreter` (D-0263) and `deployment_name` (D-0411), not built. Not decided: `locations.cache`, `irida.auth`, `irida.data_analysis_recipe_id`, `blueprint_agent.model` and four others, `import_helper_enabled` (no UI reader) | No: removing the two decided keys carries out D-0263 and D-0411 |
| 8 | Severity of each silent behaviour: refused, warning on screen, or advice | the soft cascades, a missing flag (the validator only warns, `app_features_validator.py:99-103`), `testing_mode` and badge defaults, an unknown panel type, a typo in `app_features_override` | Architect: one answer per item is needed before the standard can be written; it is yours (the software informs, the user decides). Deployer: the standard states which keys are checked until D-0412 is built. Developer: the start check will refuse files that run today | No (it applies ADR-077's soft and fatal groups; the architect says the catalogue must use the same classes) |
| 9 | Per flag: required (a missing one is refused) or optional with one written default? | (a) required; (b) optional with a written default | Architect: asks it; today three defaults disagree (the validator says False, `app_features_validator.py:101-103`; the badge says True, `bootloader.py:859-864`; `testing_mode` says True, `bootloader.py:899`). Others: no position | No |
| 10 | "Every key the code reads is in the list": how is it checked? | (a) a heuristic scan (small, cannot prove "every key"); (b) one accessor that refuses an unlisted path (exact, large) | Developer: shows both; (b) is "the only exact one", (a) is "a half fix if sold as every key". Architect: proposes the heuristic test, and names its limit (a key read through a computed name). Deployer: no position | No |
| 11 | Where does the written page live? (Answered by your words of 2026-11-21: in `.claude/design/`, option (a) first; whether it is also published in `docs/reference/` is not answered) | (a) `.claude/design/` first, then `docs/reference/`; (b) `docs/deployment/` | Architect: (a). Developer: (b). Deployer: reads in the user documentation | No. ADR-096 (documentation) is touched only by (b) as a new page (REASONED) |
| 12 | One generator helper for the Gallery cheatsheet (D-0399) and the deployment standard, or two? | one / two | Architect only. Information | No: D-0399 decided the generation, not the helper |
| 13 | Where do "which code reads it" go: main key table or appendix? Module name or file:line? | (a) main table, module name; (b) main table, module and function; (c) appendix | Architect: (a). Developer: (b). Deployer: (c). All three: no line numbers | No |
| 14 | "Since which version": a field per key, or the format number only? | (a) a field; (b) no field | Architect: no field (needs choice 3 (c)). Developer: a field `since`. Deployer: only for renamed keys, in the appendix | No |
| 15 | Facts corrected before the standard copies them | the 11 rows of section 2 and the list of section 10 | Deployer: correct first, "so the standard does not copy a wrong fact". Architect: the generated text removes most of them. Developer: the 18 stale statements are deleted in step 8 of its order | No |
| 16 | One path rule for all path keys | one base for every path key, or the base stated per key | Deployer: asks for one. Architect: records the base per key; the choice belongs to the deployment study (it calls it F14 there) | Not stated by the viewpoints; it touches the deployment study |
| 17 | May a deployer write an own sidebar file and an own palettes file? | yes / no | Deployer: the standard must say. Architect: a palettes path key is OPEN. Developer: no position | No |
| 18 | Is the app features `display_name` a display key that becomes `ui_label` (D-0407: every display key carries `ui_`)? | yes / no | Architect only: D-0411 names `ui_title` and `deployment_name` but not `display_name`. For the key stage, not now | No: asks whether D-0407 reaches it |

## 9. The order of work the developer and the architect propose

Note (2026-11-21): the owner answered choice 10 of the deployment study after this section was written: no temporary reader of the old keys (ledger D-0436). Any step below that reads the old five location keys into the new structure for a few merges is therefore not the way; the steps that change no behaviour (a single function for the app's place with today's defaults) are not a temporary reader of old keys and are not touched by this.

NOT STARTED. Nothing below has begun. Each step leaves a working app (both say so). Model tags are the developer's proposals from `CLAUDE.md` section 2.

| Step | Architect | Developer | Waits for the 13 choices? |
|---|---|---|---|
| 0 | S0: you answer section 8 | 0: you answer; a scribe records | - |
| 1 | S1: spec skeleton (the field schema, `use_cases`, `open_choices`, `format_version`) and its own tests; no code reads it. "Cheapest place to find that the fields are wrong, before 60 keys are typed" | 1: write the spec from the survey, no code reads it yet; settles the 18 disagreements into `status` and `check` fields (`sonnet/high`) | No |
| 2 | S2: key entries "as built" for deployment, app features, sidebar, palettes, environment, with status tags; tests that the shipped files pass | 2: tests first for the loader and the checker (`sonnet/medium`) | No: the open choices are held as "not decided" |
| 3 | S3: the checker wired at start, replacing `renamed_keys.py`, the five duplicate lists in one merge; the format number if chosen; a script that adds it to the shipped files. "One merge, no half state, no alias" | 3: the checker and the bootloader call; the `renamed` tables move into the spec; shipped files fixed in the same pass (`sonnet/high`, 13 importers) | No |
| 4 | S4: the generators and their test; the hand-written copies of the same tables removed in the same merge | 4: the D-0411 renames (banner `title` to `ui_label`, `subtitle` to `description`; remove `deployment_name` and `ui_title`), the migration script, the proof for `demo-vetinst` and `web-demo` (`sonnet/medium`) | No |
| 5 | S5: the D-0407 / D-0411 one pass through the spec | 5: remove `runtime.python_interpreter` (D-0263) (`haiku/low`) | No: both decided |
| 6 | S6: use-case views and the matrix generated | 6: sidebar and palettes sections; allowed panel ids from the registry (`sonnet/medium`) | The palettes path key waits |
| 7 | S7: promote each decided choice, one by one | 7: the generator (template, tables, matrix, README table) and its compare test (`sonnet/high`) | - |
| 8 | - | 8: the written page by hand; delete the 18 stale statements (`sonnet/medium`) | No |
| 9 | - | 9: the "read by" test and, if you choose it, the one accessor (`sonnet/high`) | No |
| 10 | - | 10: use-case section, matrix, example files, only for the decided cases (`sonnet/medium`) | YES for the rest |

Differences in order: the architect puts the generators (S4) before the renames (S5) and says the spec is then the source of the rename script; the developer puts the renames (4) before the generator (7) and runs the generator in parallel with steps 3 and 4 in its own worktree. Not settled.

What waits for the 13 choices (both agree): every key of named places, access words, `users`, the fetch step, the font list; the fate of `locations.cache` and `user_data`; the meaning of `data_lookup` and of relative paths under confinement (choice 4); `project_root`; the `irida` block and the `deployment_type` classes; the palettes path key; the default of `testing_mode` with the Data Import overwrite (choice 8); `session_import` numbers (D-0283); the format of `app_features_override`; the example files for cases with no design. What does not wait: `python_interpreter` and `deployment_name` removal (decided), the renamed banner keys (decided), the start check, the spec for what exists today.

One consequence you should know (developer): until each open choice is decided, the rule "refuse the unknown key" stops a deployer who wants to try it.

## 10. Found on the way

Facts that are defects or stale texts of today. None needs a decision of structure. RUN = I checked; the rest READ by the survey or a viewpoint.

1. REASONED, not run (survey finding 1): `app/handlers/ingestion_handlers.py:51` passes `current_app_features.get()` back to the bootloader; `server.py:161-162` sets that value to the display name ("Workflow Developer"); the loader then looks for a file with that name and stops. A test that runs ingestion with a shipped app features file would show it.
2. RUN: `connector/__init__.py:40-45`: a mistyped `deployment_type` silently becomes the filesystem connector.
3. `docs/workflows/ui_app_features.qmd:198` names `config/ui/agents/blueprint_agent.md`; the shipped file is `blueprint_default.md` (`developer.yaml:57`). Same file, `:208`: "the qa app features always uses backend: disabled"; `qa.yaml:61-63` says to flip it for manual runs.
4. `docs/troubleshooting/index.qmd:93` and `:111`, `bootloader.py:310` and `:688` name `local.yaml.example`; no such file exists.
5. `app/src/ui.py:343` has a stale comment naming a key (`ui_banner` in the app features file) that is now refused.
6. `.claude/design/recipe_format_spec.md:841` says `renamed_keys.py` "names a choice manifest_paths"; `renamed_keys.py:20` names `data_lookup`. Stale.
7. `.claude/knowledge/architecture_decisions.md:2244` cites `docs/user_guide/deployment_personas.qmd`, which does not exist (survey, glob). ADR-048 (`:1113-1130`, `:1236-1250`) names `local_profile.yaml` and `pipeline_test_profile.yaml`; the files are `local.yaml` and `pipeline_test.yaml`.
8. `config/deployment/README.md:54` and `libs/connector/README.md:31` list one Galaxy variable; `galaxy.py:35` also reads `GALAXY_SLOTS_DIR`. The Galaxy variables are not in `environment_variables.qmd`. `GALAXY_URL` and `GALAXY_API_KEY` have no reader. `SPARMVET_IMAGE_REF` is read (`export_handlers.py:186-194`) and not documented.
9. `config/deployment/README.md:9-19` leaves out the `demo/` folder and `retest.yaml` (customized-deployments survey).
10. `docs/workflows/ui_app_features.qmd:479` says the Deployment panel takes `logo`, `contact`, `institution`; the code reads only the banner title and subtitle. `web-demo` has an empty title and subtitle and the panel still renders, blank (`home_theater.py:1969-1971`, REASONED).
11. `config/palettes.yaml`: its three palettes are used by no shipped recipe or deployment; the file path is fixed in the code (`bootloader.py:946`).
12. `assets/scripts/bundle_connect.sh:97-106` deploys `connect_template.yaml` with its placeholder values by default; the template's `:13` says another path (survey, REASONED that the start fails on the placeholders).
13. `assets/containers/Dockerfile` comments name a folder `/app/config/deployment/pipeline` that is not in the repository.
14. `import_helper_enabled` has no reader except the cascade that forces `data_ingestion_enabled` off (`bootloader.py:822-829`); the validator says a missing flag defaults to False (`app_features_validator.py:101-103`) while the badge and `testing_mode` default to True (`bootloader.py:859-864`, `:899`).
15. Cascades are applied to the file's flags before the operator override (`bootloader.py:811-829` before `:387-388`), so an override that switches on `data_ingestion_enabled` while `import_helper_enabled` is false in the file is not suppressed (survey finding 3, REASONED, not run).
16. Several shipped recipes carry a personal e-mail address in `info.contact` (customized-deployments survey, finding 8); not repeated here.
17. `.claude/rules/rules_app_features_flags.md:241` names a "ConfigurationError"; the code raises a DeploymentError (`bootloader.py:631-637`).

## 11. Not verified

- I ran five checks myself (RUN): the template sentences at `:23` and `:36-37`, `bootloader.py:160-180`, `connector/__init__.py:36-48`, the absence of a caller of `get_python_path`, and the only call of `get_location("cache")`. Everything else in section 2 and 10 is READ by the survey or a viewpoint and was not re-read by me.
- Nobody ran the app, the checker, a test or a generator. The survey, the architect and the developer ran nothing except greps.
- Whether a "check my file" command already exists: not verified (the deployer says it found none; it did not read the code).
- The developer's read-site counts (about 27 in `bootloader.py` and 13 outside) come from two greps with different patterns and may miss reads through helper functions.
- Whether `{{< include >}}` of a generated file builds in this repository's Quarto setup: precedent only in `docs/appendix/FAQ.qmd:94`, by grep (architect, developer).
- Whether `deployment_spec.yaml` installs in the container wheel: REASONED from `libs/utils/pyproject.toml` (architect). The packaging test covers `recipe_spec.yaml` only.
- Whether a test enforces "a changed key changes the format version" for the recipe spec (architect).
- The deployer did not read the recipe standard, `ORDER.md`, the deployment study table, the ledger or the docs pages; it relied on the survey for code facts.
- Not read by me: `tmp.md` (never).
- ADR-071, ADR-073, ADR-077, ADR-078, ADR-094 were read by heading or grep only (survey).
- The wording of every new refusal line and of the "NOT DECIDED" box is a proposal.
