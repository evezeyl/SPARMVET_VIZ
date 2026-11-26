# Where the app reads and writes recipes and data, in every deployment: one table for the owner (2026-11-21)

Written by an agent (builder-opus) from the study files in this folder. Nothing is built. Nothing is decided. The viewpoints recommend; you decide.

## 0. How to read this

1. What was done: a scout read the code and wrote `FACTS.md`. Four viewpoints (architect, scientist and data scientist, developer, a user who is not a developer) each wrote a proposal, then answered each other in one discussion round (`*_round2.md`).
2. What was run: the architect ran one small test (a user folder that cannot be created, under a folder the app may not write). The scientist ran small tests of the hashes and of file names. Everything else was only read in the code.
3. This writer re-read the code lines where two sources differed, and the ledger lines cited. Each claim says VERIFIED BY A RUN, READ (in the code at file:line) or REASONED (follows from the code, not run).
4. Tags: DECIDED (ledger number, who decided), CONFIRM (read from your words, please confirm), OPEN (yours to decide), PROPOSAL OF THE VIEWPOINTS (an agent's idea; never a decision).
5. Words used below: a **place** is a folder that the deployment file names. **One running copy of the app** is one started app; several browsers can use one running copy. A **fetch step** is a small program, run before the app, that copies files from Galaxy, IRIDA or an API into a local folder.

## 1. Flagged first: what changes a result silently or hides a step from the user, today

One line each: the plain statement, then where, then the evidence.

| # | User space or deployment case | What happens today | Where | Evidence |
|---|---|---|---|---|
| F1 | HOME, every deployment, also the static web page | A session record is written at every opening of a recipe, with no setting to stop it. A "static" page is not static: it needs a folder it can write. | `app/handlers/home_theater.py:1515-1578` | READ |
| F2 | HOME, a server used by several people | One shared user folder for everyone: the sessions and stored tables of all users sit together. Nothing knows who the user is. | `session_manager.py:305-308`, `bootloader.py:1044` | READ. That one user sees another's sessions in the list: NOT run |
| F3 | BLUEPRINT | A save replaces the recipe file in place, with no copy of the old one. | `blueprint_handlers.py:1188, 2621, 1517` | READ |
| F4 | BLUEPRINT and HOME | They read two different recipe folders: BLUEPRINT a fixed folder of the repository, HOME the folder of the deployment file. | `blueprint_handlers.py:975-984, 2685` | READ |
| F5 | HOME Data Import (only with `testing_mode`) | An upload replaces the data file with no copy and no record of the original file name. It writes where the recipe's path points, also outside the data folder. With the local deployment it overwrites test data that is in git. | `data_import_check.py:238-272`, `orchestrator.py:204-209`; task DATA-IMPORT-OVERWRITE | READ; the git case found in the review of 2026-11-21 |
| F6 | HOME, recipe upload (`btn_ingest`) | The upload copies a recipe into the recipes folder and replaces a file with the same name silently. No control on screen was found that reaches it. | `ingestion_handlers.py:50` | READ (this writer) |
| F7 | HOME, bundle import | Importing a bundle writes the recipe into the shared recipes folder, under a new name `<id>_imported_<time>`. | `bundle_importer.py:252-276` (write at `:263`) | READ (this writer) |
| F8 | HOME, every deployment without a named default | The default recipe is the first of an unsorted list of files. A new file in the folder can change which recipe opens. | `bootloader.py:416-417, 656` | READ (this writer); in the earlier study a scratch run opened another recipe than the demo |
| F9 | HOME | A data file that has vanished still gives a key that looks valid (`MISSING:<table>`). The stop must come later, from the reader. | `app/modules/cache_keys.py:146` | VERIFIED BY A RUN (scientist); READ (this writer) |
| F10 | HOME sessions | A session stores the full server path of each data file. It names the server layout (and so a user's home folder) and means nothing on another machine. | `session_manager.py:386-389` | READ (this writer) |
| F11 | Every deployment | When the user folder cannot be created, the user gets a raw Python error at the first click, in every browser session, not a message at start for the person who installed the app. | `server.py:149`, `session_manager.py:274` | VERIFIED BY A RUN (architect) |
| F12 | Every deployment with a read-only user folder | The opening of every recipe stops with a message. | `opening_build.py:160-167, 249-254` | READ |
| F13 | HOME, a recipe whose data path points anywhere | With the default way of finding data, a recipe may read (and Data Import may write) any path the recipe names. A place that is meant to be protected is not. | `orchestrator.py:172-188, 204-209` | READ |
| F14 | HOME, the recipe check and the run | The check starts a relative data path from the project folder; the run starts it from the folder where the app was started. The same recipe finds its file, another file, or none. | earlier page `tmpAI/panel/path_use_cases/PANEL_for_eve_2026-11-18.md`, item 2 | VERIFIED BY A RUN (trial of 2026-11-18) |
| F15 | Every deployment | With no deployment named, the app starts the development setup and its demo paths. Only a printed line says so. | `bootloader.py:295-298, 102-105` | READ (architect) |
| F16 | Container | The container recipe cannot build as written: it installs a library that does not exist (`libs/generator_utils`) and leaves out three that the app needs. It runs as the administrator account (root) and declares no folder to keep data. | `assets/containers/Dockerfile:79`, `:89`; `ls libs` | READ (this writer). Build not run. The container update is deferred by you (D-0263) |
| F17 | HOME, a recipe changed between two sessions | A session saved on an older content of the recipe opens with a warning only. You decided it must be refused (D-0362, not built). | `session_handlers.py:597-602` | READ (this writer) |
| F18 | HOME, a recipe list | The list of recipes is read once at start. A recipe added or changed later is not seen until a restart, and the screen does not say when the list was read. | `bootloader.py:404-417` | READ |
| F19 | Posit Connect template | The template says the pipeline fills `inputs/`, but with the default way of finding data the app reads the recipe's own path, not `inputs/`. | `config/deployment/connect/connect_template.yaml`; `orchestrator.py:185-195` | REASONED (ANSWERS_A_AND_B.md) |
| F20 | Test Lab | A recipe made by the Test Lab scaffold may name the temporary upload path as its data path. | `scaffolder.py:194-195`, `test_lab_studio.py:72` | NOT VERIFIED at run time |
| F21 | HOME audit, ghost save off | Audit steps are not kept when ghost save is off. You decided this stays as built, with no notice (D-0302: "There wont be any audit on pipeline static, this is trivial."). | `audit_stack.py:135-136, 291` | READ. Listed only so that the "nothing writable" choice (section 5) keeps it in view |
| F22 | HOME, data changed while a recipe is open | The data hash is read at opening. If the file changes before the figure is read or exported, key and figure can disagree. | `cache_keys.py:146` | REASONED, not run |

## 2. The proposal in one page

**What all four viewpoints agree on (PROPOSAL OF THE VIEWPOINTS, not decided):**

1. **Named places in the deployment file.** The file lists places for recipes, for data, for the user's files (sessions, audit folder, imports) and for the stored tables. Each place says what the app may do there. This replaces today's five location keys. Old keys are refused with a message that names the new ones, as was done for the renamed keys (ADR-091 point 2).
2. **Four words on screen, derived by the app, never typed by the person who deploys:** "Shared (you cannot change these)", "Mine", "Saved in this app (everyone who uses it sees them)", "This session only". The person who deploys gives each place a label; the app adds the words, so a label cannot claim "locked" falsely.
3. **No login system.** Without a login, "Mine" is true only when one person uses one running copy of the app (a local PC, a Galaxy interactive tool, one container per user). On a shared server the screen says "Saved in this app (everyone who uses it sees them)", never "Mine".
4. **A fetch step outside the app.** Galaxy, IRIDA or an API never talk to the app. A fetch step copies the files into a local place first; the app reads that place. The fetched files stay there so their hash can be checked again. It is switched on per deployment, never by default.
5. **Read and write only inside the declared places.** A recipe's data path and Data Import may not reach outside (see choice 4 for what this costs).
6. **Never pick silently between two files of the same name.** Identical files in two places are one entry that lists both places. The rule for different files is still disputed (choice 3).
7. **Record what a figure depends on:** for each recipe and data file, the place, the path inside the place, the hash; for fetched files also the source and the time. Never the full server path, never a token.

**Reconsiders a decision?** (information only; never a reason for or against a point)

| Point | Reconsiders a decision? |
|---|---|
| 1. Named places | ADR-048 sections 3 and 5: five location keys, one path each (`resolve_paths` "returns the five location paths"). How D-0340 is read: "there is no new configuration variable for now" (choice 2). It follows ADR-091 point 2: an old key "stops the app at startup with a message naming the new one. There is no silent alias" |
| 2. Four words on screen | no |
| 3. No login system | no. ADR-091 point 4 already says that path expansion "does not give one web user a folder of their own on a shared server" |
| 4. Fetch step | ADR-071: "the app must function identically with no outbound network access". The fetch step is outside the app and switched on per deployment; the architect calls it a qualification of ADR-071. It keeps ADR-048 section 5: "every path returned is a local filesystem path" |
| 5. Confinement | No ledger line decides the meaning of finding data "by the recipe's path"; this point changes it. D-0373, only if the demo recipe is rewritten (choice 4) |
| 6. No silent pick | ADR-092, only for option R2 of choice 3: "The file name is the identifier of a data analysis recipe everywhere" |
| 7. Record | ADR-097: the export record gains the place and the hash of each file |

**The picture (the same on every deployment; a block that does not exist is absent, not empty):**

```
                                     deployment file
                                           |
   pipeline / Galaxy / IRIDA / API  --(fetch step)-->  local place (read)
                                           |
   +---------------- Recipes ---------------+   +---------------- Data -----------------+
   | Shared (you cannot change these)   3   |   | Shared (you cannot change these)  12  |
   | Mine                               2   |   | Mine                               1  |
   +----------------------------------------+   +---------------------------------------+
   Mine (user files): sessions/<key>/audit/   imports/        Stored tables: rebuilt when needed
   The app writes ONLY into places marked "Mine" (or "This session only").
```

**Sketch of the deployment file for your main case** (consortium recipes read-only, plus the user's own directory). SKETCH ONLY: the key names are not decided, and the four viewpoints use different names.

```yaml
# Sketch, key names not decided.
users: one                  # the person who deploys states: one person per running copy, or several
places:
  recipes:
    - {id: consortium, label: "Consortium recipes", path: /mnt/consortium/recipes, access: read}
    - {id: mine,       label: "My recipes",         path: "${HOME}/sparmvet/recipes", access: replace}
  data:
    - {id: consortium, label: "Consortium data",    path: /mnt/consortium/data, access: read}
    - {id: mine,       label: "My data",            path: "${HOME}/sparmvet/data", access: replace}
  user:   {path: "${HOME}/sparmvet/user",  access: replace}   # sessions, their audit folders (D-0340), bundle imports
  cache:  {path: "${HOME}/sparmvet/cache", access: replace}   # stored tables, can be rebuilt
  gallery: {path: /opt/sparmvet/gallery,   access: read}
```

`access: read` = the app never writes there. `add` = new files only, an existing name is refused. `replace` = new files, and replacing a file is allowed (the overwrite control, D-0394). `${HOME}` is already expanded today (ADR-091 point 4, built).

## 3. THE TABLE

Rows 1 to 11 are your cases, in your order (1b is the maintainer inside your case 1; 10 and 11 are your note on containers and installation). Rows 12 to 19 are cases you did not list. The deployment-file column is a sketch: key names not decided.

### 3a. Reading and writing: who, where, what the file says, what the user sees

| # | Use case | Who reads what, from where | Who may write what, where | What the deployment file would say (sketch) | What the user sees |
|---|---|---|---|---|---|
| 1 | Consortium recipes, read-only for the user | Every user reads the consortium recipes (and consortium data) | Nobody, through this app. The maintainer writes elsewhere (row 1b) | `recipes: [{id: consortium, path: ..., access: read}]` | "Consortium recipes (you cannot change these)"; no save or overwrite control on them, and the reason is shown |
| 1b | The maintainer ("only developers and specific users") | The consortium place | A separate app set up for the maintainer writes new dated files into the consortium place; it never replaces one | The maintainer's own deployment file: `{id: consortium, path: ..., access: add}` | Only in that app: "Save final version (dated)"; an existing name is refused with a plain line |
| 2 | The user's own directory: own data, export and import of recipes, reproducibility, sessions, audit | Own recipes and data, plus the shared places | The user's place: new dated recipes, replacement only here (D-0394), Data Import, sessions, audit folder (D-0340), bundle imports | `recipes: [..., {id: mine, path: "${HOME}/sparmvet/recipes", access: replace}]`; `user: {path: ..., access: replace}` | "My recipes" (only with one person per running copy, row 12); "Saved in My recipes as amr_2026-11-21"; overwrite asks: "Replace X? N saved sessions made with it will no longer open. Results already exported are not changed." |
| 3 | Static web page: one recipe, one data location updated now and then | One recipe; one data folder, refilled by the pipeline outside the app | Only the stored tables; nothing for users | `default_data_analysis_recipe: amr_2026-11-20`; `recipes: [{read}]`; `data: [{read}]`; `cache: {access: replace}`; no `user` place | No save, session or Data Import control (absent, not greyed). "This page shows one analysis. Nothing you do here is saved. Download to keep a result." (only once it is true, see F1) |
| 4 | Web page with exploration: change panels, write or save nothing | As row 3 | As row 3 | As row 3, with the exploration app features | As row 3, plus the panels and the exploration filters (never saved) |
| 5 | Static pipeline (usegalaxy, IRIDA): recipe fixed at deployment, data passed by the pipeline | Recipe from the image or a fixed folder; data from the job folder | Stored tables in the job's work folder | `default_data_analysis_recipe: ...`; `data: [{id: job_input, from: job_folder, path: inputs/, access: read}]`; `cache: {from: job_folder, path: work/}`; data found by table name | "The recipe and data were given by the pipeline. You cannot choose others." |
| 6 | Upload of metadata or new data from paths the user can reach: shared consortium data, sensitive metadata only for the user; own recipes for reproducibility with the audit; sessions kept (usegalaxy grants the paths) | Consortium data and the user's own data | Only the user's place. Never the consortium place | `data: [{id: consortium, access: read}, {id: mine, access: replace}]` (plus, perhaps, a private mark: choice 7) | Each table labelled "Shared" or "Mine". "Save to:" lists only places the user may write. "This table is in your own place only; it is never copied to the shared place." |
| 7 | Same, with the access set at deployment by IRIDA | Files fetched from IRIDA into a local read place | As row 6 | As row 6, the IRIDA data place filled by a fetch step; token only in the environment variable `SPARMVET_IRIDA_TOKEN` | "Given by IRIDA on <date>. It cannot be saved here." |
| 8 | Local install: own user directory, plus one or several common directories | Common places and own places | Own places; a common place only in the maintainer's app (row 1b) | Several entries under `recipes:` and `data:`, each with its access | Two headings: "Shared recipes (you cannot change these)" and "My recipes" |
| 9 | An API gives both data and recipe | A fetch step copies them into a local read place before the app starts reading; the files are kept | Only the fetch step writes there; the app never does | `data: [{id: api_project, from: fetch, path: /var/sparmvet/api, access: read}]`; source and token from environment variables | "Given by <source> on <date>. It cannot be saved here." |
| 10 | Shipped in a container (your note) | Recipes and data inside the image or in folders attached to the container from outside | Only attached folders marked `replace` | As the case it serves, with paths inside the container | Same as the case it serves; at start the app names any place it cannot use |
| 11 | Installed from GitHub; later perhaps PyPI (your note) | The repository checkout | As declared | As the case it serves; the development setup only from a checkout | Same as the case it serves |
| 12 | Several users on one server, no login | Everyone of the running copy reads the same places | Everyone writes the same user place | `users: several` | "Saved in this app (everyone who uses it sees them)", never "Mine"; no sensitive data there |
| 13 | Read-only container with one writable attached folder | Image and attached folders | Only the writable folder: stored tables and user files | `cache` and `user` paths inside the writable folder | At start: which places can be written; a folder that cannot be written stops the start and is named |
| 14 | Container with nothing writable | Image only | Nothing | Disputed (choice 5): either the app refuses to start, or the file declares "this session only" | Either the start stops with a plain message, or "This session only. Nothing is kept when you close the page. Download to keep a result." |
| 15 | A pipeline that hands the data by a job folder, or by an API | Job folder (row 5) or fetched place (row 9) | As rows 5 and 9 | As rows 5 and 9 | As rows 5 and 9; a job folder or a fetch that fails stops the start and names the source |
| 16 | Offline use | Local places only | As declared | No fetch step declared; a place that may be absent is marked "not required" | "Consortium recipes: not reachable now" in the selector and at the opening |
| 17 | Posit Connect | The content folder or an attached path | Stored tables and user files on Connect's storage, if it persists | As row 3 or 12 | As row 3 or 12 |
| 18 | A place that changes while the app runs | The list is read again at a clear moment (a new browser session or a "refresh" button), never on a timer | - | - | "List read at 14:02"; "The folder has changed since you opened the page: reload the list." |
| 19 | A consortium place updated by someone else | A new dated file appears at the next reading of the list | - | - | "A newer version exists: amr_2026-11-21. You are using amr_2026-11-17." A session made on a recipe whose content changed under the same name is refused (D-0362) |

### 3b. Today, options, recommendation (same rows)

The last column is information only: it is never a reason for or against an option.

| # | What breaks today | Options, with pros and cons | Recommendation of the viewpoints (who disagrees) | Reconsiders a decision? |
|---|---|---|---|---|
| 1 | One recipes folder only. "Read-only" holds only if the operating system forbids writing. BLUEPRINT (F4), the bundle import (F7) and the recipe upload (F6) can write into it | (a) A place marked `read`: the app never writes there; pro: the screen can say "you cannot change these" before the user tries; con: the operating system must still protect the folder. (b) Only the operating system's permissions (today): pro: nothing to build; con: the user learns it by a failed save | (a), with the operating system as the safety net. All four | (a): ADR-048 sections 3 and 5 (the five location keys). (b): no |
| 1b | Cannot be done: the app cannot tell the maintainer from other users | (A) a separate app for the maintainer, whose deployment marks the common place `add`; pro: works today without a login; con: anyone who opens that app can publish. (B) wait for a user identity from Galaxy or Posit Connect; con: not verified on those platforms. (C) the operating system's permissions decide; con: refusal comes late | A now, C as the safety net, B later (earlier recipe places study, P2; architect). Developer: would not add the word `add` before a deposit folder is specified | no. All three are ways to carry out D-0393 point 3: "Only specific users may modify the common recipes" |
| 2 | No second recipes place; no per-user place; one user folder for everyone (F2) | Named places (design A); one fixed root with a layout written in the code ("own: root", design B); extra keys beside the five (design C) | Design A, with B as a ready-made template. All four. C rejected as the final state by all four, on merit: it cannot say "read-only" | A and B: ADR-048 sections 3 and 5; how D-0340 is read (choice 2). C: no |
| 3 | The session record and stored tables are always written (F1, F12); a read-only folder stops the opening | (a) stop at start; (b) a temporary folder for the life of the running copy; (c) the deployment file chooses (choice 5). Also: no session record when there is no user place | No silent behaviour. Disputed between (a) and a declared temporary folder: choice 5 | no |
| 4 | As row 3 | As row 3 | As row 3 | no |
| 5 | No Galaxy deployment file. No Galaxy tool wrapper (the file that tells Galaxy how to start the app). The job folder variables are not documented. IRIDA fails at start (`irida.py:40-52`). The container does not build (F16) | Job folder as a read place (no API needed; the Galaxy code already reads the job folder, `galaxy.py:35, 54`); IRIDA through a fetch step later | Job folder as a read place, all four. IRIDA: a fetch step, written only when the use case is written (developer) | no |
| 6 | Browser upload only: the user cannot choose a file on the server. One data folder. Data Import writes where the recipe's path points (F5, F13), with no copy | Writes only into a writable data place (all four). Whether the app should also let the user pick a file from a declared place on the server: none of the viewpoints proposed it; OPEN. Private mark: choice 7. Overwrite: choice 8 | Confine the writes (all four), on merit: otherwise a place called read-only or private is not (F13). Private mark and overwrite: disputed or yours (choices 7, 8) | Confinement: no ledger line decides the meaning of finding data by the recipe's path; this changes it |
| 7 | Does not work: IRIDA's `fetch_data` is not written (`irida.py:40-52`) | (a) A fetch step copies into a local place: the app reads only local folders in every deployment, so one way of reading serves all cases; it can be tested without IRIDA with a stand-in source (developer); the fetched files stay on disk so their hash can be checked again (all four); a failed fetch stops the start and names the source (user). (b) The app calls IRIDA itself: nobody proposes it. No merit argument against (b) was given by any viewpoint; the objection was the two ADRs of the last column | (a), switched on per deployment. All four; developer: only after the use case is written. The rejection of (b) rests on the ADRs, not on a merit argument given by the viewpoints | (a): ADR-071 "the app must function identically with no outbound network access" (qualified: the fetch is outside the app, opt-in). (b): ADR-048 section 5 "every path returned is a local filesystem path", and ADR-071, same words |
| 8 | One recipes key; the selector shows one folder; BLUEPRINT's fixed folder (F4) | Several entries per role (design A) or a fixed "shared" and "own" pair (design B, cannot hold three places) | Design A. All four | ADR-048 sections 3 and 5 |
| 9 | Nothing in the app can receive data or a recipe by an API or a web address (FACTS section 1) | (a) Fetch step before the app; merit as row 7 (all four). (b) The app calling the API itself: nobody proposes it; no merit argument against it was given by any viewpoint | (a); keep the fetched files; record source, time, version if given, hash, place. Never the token. All four. The rejection of (b) rests on the ADRs only | As row 7 |
| 10 | Container cannot build (F16); runs as root, so folder permissions do not stop a write; paths relative to the working folder; test data left out of the image | Repair the recipe, run as a normal user, declare the folders that keep data, stop when no deployment file is named | Repair, on merit: every container case is untestable until the recipe builds (architect). When: yours | D-0263: "The container recipe update is DEFERRED." A repair now would end that deferral |
| 11 | GitHub editable install works. PyPI: the code imports a top-level package named `app` (34 files); `config/` and `assets/` are not in any package; app files are found from the working folder | PyPI as a goal (needs a rename of `app` and package data) or not now (choice 12) | Separate decision; the design does not need PyPI (architect, developer) | no |
| 12 | One shared user folder, no identity (F2) | The person who deploys states one person or several; or a user identity from the platform; or always the "everyone sees them" wording (choice 6) | A statement in the file (architect, user, developer). Scientist: uses a private mark instead | no |
| 13 | No folder declared to keep data in the container recipe; root; the raw error of F11 | A write test at start, a plain message naming the place | All four. Disputed: where the write test may write (choice 11) | no |
| 14 | The opening stops (F12) | Stop at start; temporary folder for the session; memory only (engine change) | Disputed: choice 5 | no |
| 15 | As rows 5 and 9 | As rows 5 and 9 | As rows 5 and 9 | As rows 5 and 9 |
| 16 | Not run; app files are kept locally (ADR-071), so it should work | Places marked "not required" are shown "not reachable now" | All four; the notice must appear in the selector and at the opening (architect, user) | no |
| 17 | The template is not start-tested (`test_shipped_deployments.py` skips templates); F19 | Same start test for the templates | Not verified by anyone whether Connect keeps files or gives a user name | no |
| 18 | List read once (F18); all recipes checked at start (against D-0184; section 7, contradiction 1) | Read the list again at a clear moment; build D-0184 first (check a recipe when it is selected) so a new reading stays fast | Architect: D-0184 first, on merit: re-checking every recipe at each new reading is slow (architect, F8). Others did not object | no; it builds D-0184 (DECIDED, not built) |
| 19 | Warning only (F17) | Dated names make an update a new file; a same-name change is refused (D-0362) | Build D-0362. On merit: a session opened on a recipe whose content changed under the same name applies old audit steps to a different analysis, the silent case (scientist). Dated files in a shared place. All four | no; it builds D-0362 (DECIDED, not built) |

## 4. Your earlier questions, answered inside this design

| Point | Status | How this design answers it | What remains for you | Reconsiders a decision? |
|---|---|---|---|---|
| Recipe file name `name_date` | DECIDED, D-0390 (EVE): "A recipe file name is name_date, exactly."; form ISO, D-0391 (EVE): "the ISO date `YYYY-MM-DD`"; scope production recipes, D-0392 (EVE). Not built | Unchanged. Because the date is in the name, a copy changed on another day is another name: no clash between places | Whether a time is ever part of the name (D-0391: not decided) | no |
| Upload refused when the name exists | DECIDED, D-0390 (EVE): "an upload under a name that already exists is refused with a plain line". Not built | PROPOSAL: the name is checked against every place the user can read, not only the target; identical content says "already present". An old recipe comes back from the export under its own dated name (D-0390; the export always holds the original, D-0389) | Confirm that the check covers all readable places | no |
| The selector shows the newest per name | OPEN (D-0390: "what the recipe selector offers" not decided) | Across places it is a display rule: name first, then date. PROPOSAL (scientist): show "amr, newest 2026-11-17, 2 older"; a session keeps its exact dated name and hash and is never moved to the newer one by itself | Yes or no, and the wording | no |
| The user's own write place | The need is DECIDED, D-0393 point 4 (EVE): "a place where the user can read and write is needed"; the place is OPEN | A place marked `replace` in the deployment file (row 2). Without a login it is only "own" when one person uses one running copy (choice 6) | Choices 1 and 6 | ADR-048 sections 3 and 5 |
| The overwrite control only in the user's own place | DECIDED, D-0394 (EVE): "An overwrite control is wanted only in the user's own directory, never for any user in the common part." Not built | The control exists only where the place is `replace`; so it is a property of the place, and needs no login | The wording of the warning (row 2) | no |
| Data Import overwrite (task DATA-IMPORT-OVERWRITE) | OPEN; no ledger line decides it | Writes only into a writable data place, never outside (all four). The overwrite itself: choice 8 | Choice 8 | No ledger line. The task text says "against D-0045"; contested (section 7, contradiction 4) |
| Recipes imported from a bundle, and their names | OPEN (P9). Data of an import: DECIDED, D-0045 (EVE): "Imported data stored by dataset id in its own folder" | All four: never into the shared recipes place (F7). Name: choice 9 | Choice 9 | See choice 9 |
| Where sessions live | CONFIRM: `user_data/_sessions` today | Inside the user place, which exists only when the file declares it. No user place: no sessions, no session record, the session panel absent | Confirm | no |
| Where the audit copy lives | DECIDED, D-0340 (EVE): "The audit folder sits inside the session's folder, in the user's own directory that the deployment defines"; D-0319 (EVE): "I think audit/ good"; D-0333 (EVE): "an audit record is always written beside the audit recipe". Not built | Unchanged: `<user place>/_sessions/<key>/audit/`. PROPOSAL: the plain error of D-0340 comes from the check at start, not from a crash later | The sentence on D-0340 (choice 2) | How D-0340 is read (choice 2) |
| P1 the model (common place read-only plus own place; then the maintainer's dated save) | OPEN | M1 is the main case sketch (row 1 plus row 2). M2 is row 1b, a separate maintainer app with the common place `add`. M3 is one `replace` place with one person. One mechanism covers all three | Choice 1, then whether row 1b is wanted | ADR-048 sections 3 and 5 |
| P2 "specific users may modify the common recipes" without a login | The rule is DECIDED, D-0393 point 3 (EVE): "Only specific users may modify the common recipes"; the means is OPEN | Row 1b: the maintainer's own app, plus folder permissions as the net | Confirm A now, C as the net, B later | no |
| P3 the same name in the common and the own place | OPEN | Choice 3 | Choice 3 | ADR-092, only for option R2 (choice 3) |
| P4 old versions (subfolder, "show older versions" switch) | OPEN (no number; D-0394) | An "older versions" folder is one more recipes place, read-only, shown by the switch. CHANGE against the earlier table: that table proposed that the app moves old versions; the architect now says the app moves nothing, because a move is a write into a shared place | Who moves old files: the app, or the maintainer outside the app | no |
| P5 a second correction on the same day in the shared place | DECIDED, D-0390 (EVE): "For a same-day correction the user removes the old file by hand." | In an `add` place the app refuses the existing name | Who can remove the file by hand on a shared server: a normal user cannot reach the folder (user, architect; REASONED) | no |
| P6 replacing a file in the own place | The limit is DECIDED (D-0394); the warning is a PROPOSAL | Replace with: "N saved sessions made with it will no longer open; results already exported are not changed" | The wording | no |
| P7 what identifies a recipe for the machine | OPEN (D-0393: "leaning B ... kept open") | Not changed by this design; both hashes recorded | Unchanged | no |
| P8 a dated version holds a copy of every file it reads | PROPOSAL (earlier study) | Not changed: one function for the final save, the copy to the own place and the audit recipe | Unchanged | no |
| P9 the bundle import's own name | OPEN | Choice 9 | Choice 9 | See choice 9 |
| P10 a copy of the recipe kept with each session | CONFIRM: D-0340 already places the audit recipe in the session folder | Needs a user place; without one there is no session | Confirm | no |
| P11 the words on screen | PROPOSAL (user viewpoint) | The four screen words of section 2; the label from the person who deploys, the access words from the app | Accept or change the words | no |

## 5. The choices for you, ranked (larger first)

Your rule, applied in this section (your words, 2026-11-21): "Architect - cannot have decisions that because it reopens decided points - 'lazyness is a bad argument' - we need a sound architecture --- and if its not sound then we need to revise our decisions - sorry but if we are not allowed to learn we should have done better that is bad for the app - not a good architect decision."
So each option is judged on merit (correct, sound, useful to the user); "it reconsiders D-xxxx or ADR-xxx" is shown only in its own column, and never ranks an option lower.

### Choice 1. The model: named places in the deployment file

Question: do you want the deployment file to list named places, each saying what the app may do there, in place of today's five location keys?

| Option | Who supports it after the round | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| A. Named places, each with an access word (sections 2 and 3) | All four | One system for every case; the screen can say "you cannot change these" before a failed save; each place can be checked at start; the export can name places | More keys than today; the seven shipped deployment files are rewritten; 44 to 57 code places that ask for a location change (architect, developer counts); 116 test files name the old keys (developer) | ADR-048 sections 3 and 5 (five location keys, "returns the five location paths"); ADR-097 (the export record gains place and hash); how D-0340 is read (choice 2) |
| B. Two fixed layers, "shared" and "own" | Nobody as the main design; all four as a ready-made template of A | Shortest file; your two words | Cannot hold three places, a job folder, or a fetched place; the layout of "own" is written in the code; grows into A | ADR-048 sections 3 and 5; how D-0340 is read |
| C. Keep the five keys, add keys | Nobody as the final state (scientist: only as a first step) | Smallest change | Cannot say "read-only": the user learns it by failing; each new case is one more special key | no |

What it changes for the user: the headings and labels of section 2. What it blocks: every other choice below.

### Choice 2. D-0340 and "no new configuration variable"

Reconsiders a decision? This choice is itself the question of how D-0340 is read. No viewpoint argues for or against the places block because of D-0340: the merit of the block is choice 1. The positions below are readings of your decision, not merit arguments.

The ledger line (D-0340, EVE): "The audit folder sits inside the session's folder, in the user's own directory that the deployment defines (the location of the user's data); there is no new configuration variable for now". Your words in it: "(no need for a new config variable for now)".

Sentence for you to confirm or refuse (written from the four viewpoints' sentences): **"The audit folder gets no setting of its own; it stays inside the session folder, in the user's place. The new places block replaces the five location keys; it is not a new setting for the audit."**

| Viewpoint | Position (one line) |
|---|---|
| Architect | D-0340 is respected; "the existing location" becomes a named place. If you read D-0340 as forbidding any new block, the design reconsiders it |
| Scientist | The places block reconsiders "no new configuration variable for now"; the audit folder gets no variable of its own |
| Developer | Respected for the audit folder; reconsidered for configuration in general, because the block is new |
| User | Respected; asks you to confirm that the block is not what D-0340 meant |

### Choice 3. The same recipe name or table in two places, with different content

Question: when two places hold a file of the same name but different content, what does the app do?

Agreed by all four after the round: identical content is one entry that lists both places, and both are recorded. A file order, or a setting "this place wins", is not offered (all four, after the round, on merit: a figure would change when someone adds a file elsewhere, and the user never chose). PROPOSAL (architect, developer): when the app saves a recipe it checks the name against every readable place, so the app itself cannot create the clash.

| Option | Who supports it | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| R1. Refuse: neither opens, both places named, with a way out ("Rename the one in My recipes, then reload") | Architect, developer (for recipes), user (changed its mind in the round) | One name always means one file in sessions, stored tables and the export; the methods section names one file (user: "a user who picks cannot tell which file the methods section describes"); a session key needs no place (developer) | On a shared server a normal user may be stuck until someone renames a file (scientist). Architect: the app could offer "rename my copy" (OPEN) | no |
| R2. Show both; the user opens one by an explicit act, and the choice is recorded (place and hash) | Scientist; developer for data tables only | The user is not stuck; the choice is the user's and is written in the session and the export | On merit: every place that knows a recipe by its name (session key, stored tables, export, the 13 places that rebuild a recipe path) must also carry the place (architect); a methods text that says only "recipe X" is ambiguous unless the place is written (user), which the scientist answers by recording place and hash | ADR-092: "The file name is the identifier of a data analysis recipe everywhere". This was the architect's main objection; it is now information only |

Your own case (a consortium `amr_2026-11-17` copied and changed): with `name_date`, a copy saved on another day is `amr_2026-11-21`: no clash, both shown with their labels. Only a copy with the same name and date clashes.

With "it reconsiders ADR-092" removed as an argument: R1 still has merit arguments (developer, user); the architect's objection to R2 reduces to the code cost above. R2 is a sound option on merit; the choice is between "never stuck" (R2) and "one name, one file, no place in the keys" (R1).

### Choice 4. Confinement: may anything be read or written outside the declared places?

Question: may a recipe's data path, or HOME's Data Import, reach outside the places the deployment file names?

All four say no, on merit: otherwise "read-only" and "private" are not true (F13). Information you need:
- The default way of finding data (by the recipe's path) changes meaning: the path must lie inside a declared data place. No ledger line decides this.
- 14 shipped recipes point into `./assets/test_data/`. The demo recipe `1_test_data_ST22_dummy` is one of them (information: D-0373 is in the last column of the table below).
- Your earlier open page on data paths (`tmpAI/panel/path_use_cases/PANEL_for_eve_2026-11-18.md`, question 8 of the recipe-arguments report, your lean "A" with "I need you first to investigate our usage cases") asks the same thing: where the folder check runs, which folders are allowed, where a relative path starts. One answer should cover both pages.

| Option for the 14 shipped recipes | Who | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| Keep the recipes; the development deployments declare `assets/test_data/` as a read data place; a path is accepted if it lies inside a place (relative paths from the code folder) | Architect | No recipe file changes, so no hash changes and no saved session stops matching; one rule (a path must lie inside a place) for every recipe | The shipped recipes keep long paths that depend on the repository layout | no |
| Rewrite the paths by script to a name inside the declared place (scientist: a table name only) | Developer, user, scientist | Recipes no longer depend on the repository layout; a recipe names only what is inside a declared place | Each changed recipe gets a new hash, so its saved sessions stop matching once (scientist). The data files are named `test_data_Summary_20260307_105756.tsv`, not after their table (READ by this writer), so "a table name only" would also need the data files renamed | D-0373: "The demo recipe ... is not changed by agents." Information: no viewpoint argued from D-0373; this writer added it |

No viewpoint's recommendation here depended on keeping a decision.

### Choice 5. Nothing writable (static page, read-only container)

Question: when the deployment has no folder the app can write, what happens?

Agreed: no silent fallback; with no user place there is no session record, no audit and no Data Import control.

| Option | Who supports it | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| N1. Stop at start, naming the missing place | Developer (now); user as the default when nothing is declared; architect when nothing is declared | Honest, simple, testable; no new engine code | Your static page needs the person who deploys to attach a writable folder | no |
| N2. The file declares "this session only": the running copy makes a temporary folder, removes it at exit; screen "This session only" | Architect (`temp`), scientist (`session_only`, the folder private to the running copy; anything that changes a result is switched off, or the export carries its audit and the screen says "export now, nothing is kept"), user | The static page runs without a writable folder; the choice is written in the file | A system temporary folder may be shared by several running copies; on a shared server the audit of removed samples could be lost unless switched off | no |
| N3. Keep everything in memory | Developer, later and only if you want it | Nothing on disk | A second storage way in the engine, tested twice; architect and scientist would not build it before the need is shown | no |

Linked (architect): when an app feature needs a place that is missing, stop at start if it cannot work at all; inform if it works in part. Where "cannot work at all" ends is for you to confirm. Reconsiders a decision? no.

### Choice 6. What "Mine" means without a login

Question: how does the app know whether "Mine" is true?

| Option | Who | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| The person who deploys states it in the file: one person or several per running copy (`users: one` or `users: several`); the app derives the words | Architect, user, developer (as `shared_by_all`) | The screen never says "Mine" on a shared server | The app cannot check the statement | no |
| A user identity from the platform (Galaxy, Posit Connect) | Nobody now | Real per-user places | Not verified on those platforms; a header from a proxy is not a login unless the proxy is the only way in | no. ADR-091 point 4 states the limit today: path expansion "does not give one web user a folder of their own on a shared server" |
| No statement: always "Saved in this app (everyone sees them)" | Nobody | Nothing to state | Untrue for your local single-user case | no |

Scientist: no such key; a private mark (choice 7) means "private to whoever runs this copy", and that limit is said plainly.

### Choice 7. Sensitive data: a "private" mark, and what an export may copy

Question: does a place need a "private" mark now, and what must it stop?

Agreed by all four: the session stores the place, the path inside it and the hash, not the server path (F10). Sensitive metadata can only land in a writable "Mine" place, because the consortium places are read-only. Today the reproducibility export copies the raw data files after a tick and a warning; the code says "Sensitive-data handling is #46, not built here" (`export_handlers.py:1510-1511, 1543-1548`).

| Option | Who | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| No mark now; the export warning lists each data file with its place label; a per-place "may not be exported" waits for task #46 | Architect. His merit argument: a mark cannot check more than the access words do, because the app cannot see whether a folder is shared with another running copy | Nothing that the app cannot check | Stored tables made from private data may sit in a shared folder | no. Part of the architect's "not now" was ADR-091 point 6, "Dead and vestigial keys are deleted, not renamed." (a key with no code yet); shown here as information only |
| One `private: true` mark on a place: stored tables and sessions follow the privacy of their data; nothing private is copied to a shared place or into an export without a visible tick, default no | Scientist; user (allowed only with "one person") | Your case (consortium data shared, metadata private) is protected end to end | One more word; "private" means private to the running copy | no |
| No mark; the user place is private by its kind; one copy function refuses user-to-shared or user-to-export unless chosen on screen | Developer | No new word | Ties privacy to the kind of place, not to what the person who deploys says | no |

### Choice 8. Data Import overwrite (task DATA-IMPORT-OVERWRITE)

Question: when an upload has the name of an existing data file, what happens? No ledger line decides it; the same question is point 3 of your path page.

| Option | Who | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| Replace, with the line "N saved sessions were made with the old file and will no longer match" | Architect (the minimum) | Simple | The old file is gone: a published figure cannot be made again | No ledger line; the task text says "against D-0045", contested (section 7, contradiction 4) |
| Move the old file first to a kept folder, with its hash in the name, then replace | Architect, scientist, developer | Nothing is lost; a published figure can be re-made | The kept folder grows; a naming rule is needed | no |
| Refuse every replacement of data | Scientist (as one option) | Nothing is ever lost | Architect: a corrected file needs a new table name, so the recipe breaks | no |
| Replace / Keep both / Cancel | User (round 1, not repeated in round 2) | A clear question | Architect: the recipe reads a table by its fixed name, so a second copy is never read | no |

Also yours: whether Data Import stays only in `testing_mode` (architect: unchanged until you say).

### Choice 9. Recipes imported from a bundle: name and place

Agreed by all four: never into the shared recipes place (F7), on merit: an import is not a consortium recipe, and it would write into a place meant to be read-only. Question: what name?

| Option | Pro | Con | Reconsiders a decision? |
|---|---|---|---|
| Keep `<id>_imported_<time>` | An import is visibly not a production recipe | Each import of the same content is a new recipe with a new hash (architect) | D-0390: "A recipe file name is name_date, exactly." (whether an import is in its scope: D-0392, "The rule covers real production recipes.") |
| The dated name carried in the bundle; refused if another file holds that name; "already present" if identical | The same bundle imported twice is recognised instead of becoming a second recipe with another hash; the name carries the date of the recipe | A clash with a different file needs the rule of choice 3 | no |

Architect and scientist lean to the second, on the merit argument above (not because it follows D-0390); user and developer leave it to you.

### Choice 10. The order of the change, and whether a temporary reader is a "shim"

Your rule: no half fixes, no shims (a shim is a piece of code that keeps an old way working beside the new one). Question: one large change, or small steps?

| Option | Who | Pro | Con | Reconsiders a decision? |
|---|---|---|---|---|
| One change: the new module, the places block, a script that rewrites the seven shipped deployment files, the refusal of the old keys, all code that reads places, in one merge | Scientist, user | No temporary code at any time; never two formats | One large merge, harder to review | no. Same form as ADR-091 point 7 for the rename of 2026-11-07: "One pass, no hybrid." (precedent) |
| Small steps: for a few merges one function reads the old five keys into the new structure; then the file format changes in one commit, with the refusal of the old keys | Architect, developer | Each merge leaves a working app; smaller reviews | The temporary reader lives for several merges; the architect asks you whether it counts as a shim | Your rule "no shims" (`agent_principles.md` rule 4; not a ledger line): whether the temporary reader falls under it is the question. Precedent ADR-091 point 7: "a half-renamed state ... is not allowed to reach a shared branch" |

Agreed by all four: no alias (two names for one key); the old keys are refused with a message naming the new key; the safe steps of section 6 come first.

### Choice 11. The access words, and the write test at start (smaller)

| Point | Positions | Reconsiders a decision? |
|---|---|---|
| Three words `read`, `add`, `replace` | Architect, scientist, user: yes. Developer: `read` and `write` now; `add` only when a deposit folder is specified (merit: no use case yet) | no |
| A missing access word | All: an error at start, never a default | no |
| Write test at start (write a small file and remove it; needed because a container run as root ignores folder permissions) | All: in the app's own places (user files, stored tables). Developer, scientist, user: also in shared places marked `add` or `replace`. Architect: not there, because other people or tools maintain those folders; the first real write reports plainly | no |

### Choice 12. Is PyPI a goal?

Facts (READ by the architect): 34 files import a top-level package named `app`; a PyPI install would put a package called `app` into Python. `config/` and `assets/` are in no package. App files are found from the working folder (task CONFIG-APP-RESOURCES-1). Options: yes (a scripted rename of `app`, and the files packaged), or not now (GitHub and containers only). The places design does not need PyPI. Linked (architect): outside a repository checkout, a missing deployment file should stop the app instead of starting the development setup (F15). Reconsiders a decision? no.

### Choice 13. When the list of a place is read again

Options: at a new browser session or a "refresh" button, never on a timer (architect; others did not object). Depends on D-0184 (EVE, DECIDED, not built): "A recipe is checked when it is selected, not all recipes at start." Built first, a new reading stays fast. Reconsiders a decision? no; it builds D-0184.

### Choice 14, added on 2026-11-21 after the table was written: fonts (from your answer on the Gallery pictures, D-0400)

The question, as relayed by the review session: "whether fonts should be a named dependency of the deployment or the image (a list in the deployment file and the Dockerfile)".

Why it belongs here: the same recipe and data can give a different picture on another machine if the font used for the text of a plot is not installed there. That concerns every deployment case of section 3, and the proof that a Gallery picture is current (D-0400).

Status: OPEN. The four viewpoints did not study it. The facts below were collected by a scout on 2026-11-21 (read at the lines given; nothing was run). Short file names: `font_check` = `libs/viz_factory/src/viz_factory/font_check.py`; `viz_factory` = `libs/viz_factory/src/viz_factory/viz_factory.py`; `export_handlers` = `app/handlers/export_handlers.py`.

**What happens today**
- The app sets no font itself. A recipe can name a font only in a theme layer. No shipped recipe and no Gallery example names one (read by search).
- With no font named, a picture uses DejaVu Sans. That is the default of the drawing library (matplotlib 3.10.9), and the font file ships inside that library. So today every shipped picture uses a font that travels with the library, not with the machine (read; not run).
- When a recipe names a font that is not installed, the picture falls back to DejaVu Sans, and the user gets a warning: "The font 'X' ... is not installed on this machine; 'DejaVu Sans' is used instead." (`viz_factory:417-431`). Nothing is silent here.
- One gap: the check reads the fonts of the theme only. A font written on a text layer of a plot is not checked (`font_check:48-65`; the text layers are at `libs/viz_factory/src/viz_factory/geoms/core.py:417, 449`).
- The export records the versions of python, polars, shiny and plotnine. It does not record the version of matplotlib, and no font (`export_handlers:120-127, 2155`).
- An SVG picture (the default of the export) holds the letters as shapes, not as a font name. A PDF picture embeds the font. So an exported picture looks the same on the reader's machine, whatever fonts that machine has (read from matplotlib's defaults; not run).
- The container recipe installs no font for the figures. It installs TeX fonts for the PDF report (`assets/containers/Dockerfile:35-51`). It does not pin the version of matplotlib; `pyproject.toml:14` gives plotnine as a range. The Connect requirements file pins both exactly.
- The screen of the app uses no font file of its own, only icon fonts kept inside the app (no outside link).
- The tests that compare pictures draw twice on the same machine. They would not notice a font that differs between two machines.

**What this means for your question**
The risk is small while no recipe names a font: the default font travels with matplotlib, so what can change a picture between two machines is the VERSION of matplotlib, more than the fonts installed. The risk begins when a recipe author names a font (for example Arial) that one machine has and another does not: the app warns, but the two pictures differ.

**Options (not chosen; each on what it gives and costs)**
| Option | What it gives | What it does not give | What it touches | Reconsiders a decision? |
|---|---|---|---|---|
| a. Record the font really used and the matplotlib version, in the export and in the key of a Gallery picture | The user and a reader see what drew the picture; a change of matplotlib triggers a redraw | Does not stop a picture from differing between machines | the export README, the picture key | Extends D-0400 (the key has "the plotnine version"); not a reversal |
| b. Ship font files with the app and register them at start | The same font file on every machine that runs this version | Adds files and a licence per font to the repository | a fonts folder, the start of the app | No |
| c. Name the required fonts in the deployment file and check them at start | A missing font is reported at start, before any picture | Does not install anything; the check must also cover text layers | the deployment files, the loader, `font_check` | No (the deployment file has no font key today) |
| d. Install font packages in the container image | The image has those fonts | Only for containers; versions are those of the system, not pinned by the project | the container recipe | No |
| e. Allow in recipes only the fonts that ship with matplotlib | Every picture uses a font that travels with the library; no install at all | Less choice for a recipe author (no Arial, no house font) | the check of a recipe, the theme parameters, the docs | Narrows D-0242 ("Font, legend and spacing are set through a theme layer"); not a reversal |
| f. Pin matplotlib and plotnine exactly in every way of shipping | The same drawing library everywhere | Says nothing of fonts a recipe names | `pyproject.toml`, the container recipe | No |

These combine. For example a + f + e gives "same picture everywhere, and the proof is recorded" with nothing to install; b or c + d is needed only if recipe authors must be free to name other fonts.

**Not verified:** nothing was run; whether the font warning reaches the list of warnings of the export; the fonts of the PDF report; whether a picture drawn in the container equals one drawn here.

## 6. A first safe step without any of these choices

Each is called safe by the viewpoints named. Each is **not started; waits for your word**.

| # | Step | Who calls it safe | Note | Reconsiders a decision? |
|---|---|---|---|---|
| S1 | Sort the recipe list and the default recipe (F8) | All four | Scientist: a sorted default can change which recipe opens today where no default is named; you are told before | no |
| S2 | One function that gives a recipe's path, in place of the 13 places that rebuild it | Architect, developer | Needed by every option | no |
| S3 | Create the user folder and the stored-table folder at start; a plain message naming the folder when it cannot be made (F11) | Architect, user, scientist, developer | Replaces the raw error at the first click | no |
| S4 | The small module that splits a name into name and date and gives the newest per name | Architect, developer, user | The rule is DECIDED (D-0390, D-0391); its use in the selector is OPEN | no |
| S5 | BLUEPRINT reads the deployment's recipe folder instead of its fixed folder (F4) | Architect, developer; earlier recipe places study | | no |
| S6 | `create_test_deployment.py:77` writes the default recipe with `.yaml`, which the app treats as not found | Developer | NOT VERIFIED by a run | no |
| S7 | Remove the full server path from the session record (F10) | Scientist | Architect ties it to the place names, so it may wait for choice 1; a session format change (format number), so existing sessions would be refused as from an older version | no. Old sessions would be handled as D-0312 does for older files: "is refused with a plain line ... no conversion" |

Already decided separately and not part of this study: the removal of the unused `python_interpreter` key (D-0263, EVE: "the same python should be used for the whole app!").

## 7. Not verified, and contradictions

### Not verified by anyone

- Any run of a container, with a read-only attached folder, or as root.
- Two users on one running copy; whether one user sees another's sessions in the list.
- Galaxy: whether the job folder variables exist in a Galaxy interactive tool; no tool wrapper exists to try.
- IRIDA: nothing to try (`fetch_data` not written).
- Posit Connect: whether files persist; whether a user name is given; whether the template works as its comments say.
- PyPI: no package was built.
- Offline use: not run.
- What the browser shows today in any of these cases; whether users understand "locked" and "shared" (needs real users).
- Whether the export hashes the data again at export time; what the export does with a missing data file (the stored-table key marks it `MISSING:`, F9; the earlier path page says the export's combined hash leaves it out; not checked which applies).
- The order in which the operating system lists the recipe files.
- A disk that ignores upper and lower case (a table `DS1.tsv` against `ds1`).
- Data changing between the hash at opening and the figure (F22).
- The message of a bundle import into a read-only place; the temporary paths of Shiny uploads.

### Contradictions between documents and code (one line each)

1. D-0184 (check a recipe when selected) against `bootloader.py:186-192` (all recipes checked at start).
2. D-0263 says "five deployment files"; FACTS counts the key in seven files.
3. D-0362 cites `session_handlers.py:556` for the warning; the warning is at `:597-602` (READ by this writer).
4. Task DATA-IMPORT-OVERWRITE says the overwrite is "against D-0045"; the path page says D-0045 covers bundle import only. D-0045 reads: "Imported data stored by dataset id in its own folder". Not resolved here.
5. The earlier recipe places table (P4) proposed that the app moves old versions; the architect now proposes that the app moves nothing.
6. `environment_variables.qmd:22` names `FileNotFoundError`; the code raises `DeploymentError` (`bootloader.py:263-281`).
7. `environment_variables.qmd:26` names `AuthenticationError`; IRIDA is a stub (`irida.py:85-102`).
8. `environment_variables.qmd:180` and `connector.qmd:178` describe a `*id*.tsv` search; the code wants the exact name (`ingestor.py:18-31`).
9. `deployment_template.yaml:37` and `connector.qmd:92` say the app falls back to pipeline-static; the code stops (`bootloader.py:159-178`).
10. `connector.qmd:200-205` describes IRIDA in the present tense; it is a stub.
11. The `cache` location is documented (`deployment_guide.qmd:219`, `connector.qmd:131`, `deployment_template.yaml:65-67`) but no code reads it; stored tables go to `user_data/anchors`.
12. `deployment_guide.qmd:223` calls the Gallery folder read-only; the app rewrites its index at start when it can (skipped when it cannot: `gallery_manager.py:209`, `gallery_listing.py:52`; both sources were right).
13. `connector.qmd:196` (Galaxy variables) against `galaxy.py:35, 54`.
14. "BioBlendConnector" is named in `bootloader.py:143-144` and `docs/troubleshooting/index.qmd:172`; no such class exists.
15. `scripts/install_libs.sh:17` names a `requirements.txt` that does not exist.
16. `create_test_deployment.py:77` writes the default recipe with `.yaml` (S6).
17. `assets/containers/Dockerfile:79` installs `libs/generator_utils`, which does not exist (F16).
18. Two lists of required places disagree: three in `filesystem.py` (`_REQUIRED_TO_EXIST`), five in `bootloader.py:342`.
19. The Connect template says the pipeline fills `inputs/`, but its way of finding data reads the recipe's path (F19).
20. `libs/connector/README.md:3` lists four working classes; IRIDA is a stub.
21. ADR-091 gaps (`architecture_decisions.md:4484-4487`) are still open.
22. Not a contradiction, but two counts: the architect counts 44 calls of `get_location` and `get_imports_dir`, the developer 57 calls of `get_location` and `resolve_paths`; they searched different words.
