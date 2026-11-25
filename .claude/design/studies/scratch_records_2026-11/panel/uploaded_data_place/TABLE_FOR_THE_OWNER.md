# Where are the uploaded data files saved? One table for the owner (2026-11-21; your question after D-0438)

## 0. How to read this
- Your question: "where are the data files saved? 2 cases ... Is the app saving the data uploaded?" You also said "yes, replace after confirmation" (D-0438).
- Two viewpoints answered: the architect (developer view merged in), `architect.md`, and a user who is not a developer, `user.md`. Both in `tmpAI/panel/uploaded_data_place/`. The detail is there.
- Nothing is built. Nothing is decided by this table. Every key name and every screen sentence is a PROPOSAL.
- Labels: RUN = run and seen. READ = read in the code at file:line. REASONED = a conclusion. Your rule: each option is judged on merit; "reconsiders a decision?" is its own column, information only.

Added 2026-11-21 after this table was written: you said that how data reaches the app is defined by the configuration of the deployment (ledger D-0439): a static deployment has no upload; elsewhere the user has a dedicated directory to read and write, and another way of transferring data. So choice 4 below (picking a file from the places the deployment declares) is the base, and the browser upload is something a deployment switches on. Still yours: whether the upload is off unless the deployment file declares it; how the list of files looks and which places it lists; where an upload is written (choice 1); the record of which file a table reads (choice 2). Checked in the code and in the git history (`tmpAI/coordinator/home_data_picker/GIT_FACTS.md`): a control that lets a user pick a DATA file or folder from a declared place was never built in HOME; what exists is the recipe selector, which lists the recipes of the one declared recipes folder since April 2026. So picking data from a declared place is new work that can follow the recipe selector as its model.

## 1. Your question, answered for TODAY
**Is the app saving the data uploaded? Yes.** It writes the uploaded file over the file the recipe reads. It keeps no copy of the old file. It does not record the uploaded name or the date. (READ `app/modules/orchestrator.py:197-209`; `app/handlers/data_import_handlers.py:303-308`.)
That file can be a shared file, or a test file of the repository.

- **Case 1, upload from the own computer.** The browser sends the file. The app puts it where the recipe reads that table: the file the recipe names, or else `<table name>.tsv` in the deployment's data folder. After the upload the user sees a message for 10 seconds with the file name and the server path. Then it is gone. (READ)
- **Case 2, the data is already on the server (HPC, Galaxy).** The app has no way to pick a file that is already on the server. Only the browser upload exists. The user must download the file and upload it again, or put it where the recipe already reads. (READ, brief)
- **When is the upload control shown?** Only when `testing_mode` is true. If the key is missing it counts as true (READ `app/src/bootloader.py:903-905`, `get_testing_mode`). All 8 shipped app features files set it. True in 4: `developer`, `qa`, `standalone`, `pipeline-exploration-advanced`. False in 4: `web-demo`, `demo-vetinst`, `pipeline-static`, `pipeline-exploration-simple`. (READ `config/app_features/*.yaml`.) The architect's statement is confirmed. The key is named "testing", but it decides whether an upload may overwrite data. Suggestion: the control should depend on "a place where this user may write exists" (D-0429), not on `testing_mode`.

## 2. FIRST: what changes a result silently today
| # | What happens | Who is affected | Evidence |
|---|---|---|---|
| 1 | **An upload overwrites a shared file or a test file.** No copy, no record of the uploaded name or date. Other recipes or other people reading that file get the new data and are not told. The old figures cannot be redrawn. | Anyone reading that file | READ `orchestrator.py:197-209`; `data_import_check.py` `store_all` |
| 2 | **A saved session restored on other data gives only a warning.** The code shows a yellow notice for 8 s: "Session was saved against a different data batch. Row filters and exclusions may match different or no rows." Then it restores the session anyway. | The user who restores | READ `app/handlers/session_handlers.py:607-616` (no `return` after the notice) |
| 3 | **The confirmation sentence of the earlier relay does not match the code.** "N saved sessions made with it will no longer open" is NOT what happens. The sessions stay in the list and open, with the warning of row 2. The confirmation must say that. | The user who confirms a replacement | READ, same lines. Both viewpoints agree (architect F13; the user wants "built from an earlier version" shown clearly). |
| 4 | **A pipeline-style deployment reads files named after the tables, not the recipe's path.** No screen says so. | Anyone on such a deployment | READ `orchestrator.py:172-195`; `tmpAI/coordinator/default_data/FACTS_FOR_THE_OWNER.md` finding 1 |
| 5 | **A cut file is accepted.** A file cut in the middle of a line or at the end of a line is read as a normal file. The plot shows 21 or 20 of 42 samples, no message. | Anyone who uploads or receives a file | RUN, `tmpAI/coordinator/data_file_cut/REPORT.md` |
| 6 | **Risk in any design:** if the user chose a file and that file is later missing, the app must NOT fall back to the recipe's default file. That would run other data without a word. | Any user, in the new design | REASONED (architect) |

## 3. The two cases, one table
| Case | Where the file is | Who may write there | What the app records | What the user sees |
|---|---|---|---|---|
| **1 today** | Over the file the recipe reads (shared or test file possible) | Whoever the operating system allows; the app does not check the place | Only the new content code (hash) in keys and session. No uploaded name, no date. | A 10-second message with the path. Before the upload, nothing says the old file will be lost. |
| **2 today** | Where it is. The app cannot pick it. | The user, by own means | Nothing for a read in place | A read-only list of paths, or the folder (pipeline style) |
| **1 proposed, architect** | `<my data>/<recipe id>/<uploaded name>`, in the user's `read_write` place | The app, only there, only after confirmation if the name exists. Never a `read` place. Never the recipe's own `source.path`. | A small record "this table of this recipe reads this file": kind, place, path inside the place, uploaded name, date, hash. In the user place. | Before: where, how long, who can see. After: one line per table, kept in the panel. |
| **1 proposed, user** | One place "my data" that only I can write to | Only me | Place, uploaded name, hash, date, "uploaded by the user". The link per recipe and table. | Same two sentences. Also a list of my uploaded files, with a remove control. |
| **2 proposed, architect** | Where it is, in a declared place (`read` or `read_write`). No copy. | Not the app. It writes only the small record. | Record, kind "selected" | The app lists files of the declared places; the user picks; same source line |
| **2 proposed, user** | Where it is. No copy. | Not the app | Path, size, date, hash, "chosen from place P" | Same list and pick; a notice when the file changed later |

Where they differ: the architect puts a subfolder per recipe and has no delete control in the app (D-0437: the user deletes in the own file system). The user wants a flat "my data" and a remove control. The user does not mind where the record is stored.

## 4. Options for case 2 (the data is already on the server)
| Option | What the user must know and do | Large files | Safety | What the screen shows | Who recommends | Reconsiders a decision? |
|---|---|---|---|---|---|---|
| **(a)** The user puts the file in a declared place by own means; the recipe reads it by path or table name | Which folder, and the exact name the recipe expects. Nothing on screen says it today. | No copy | As today | Nothing per file today | Neither alone. The architect: (a) is what the user does before (b). The user: only usable once the place is named. | No |
| **(b)** The app lists the files of the declared places; the user picks one | Nothing but the choice | No upload, no copy. The app still reads the whole file for its check and hash. | The browser sends back only a place and a path inside it; the server accepts it only if it resolves inside that place | List with place, access word, size, date; per table the chosen file | **Both** | Touches ADR-094 (see section 7), `testing_mode` role; D-0426 implies it anyway |
| **(c)** Download to the own computer, then upload through the browser | Understandable, but absurd on HPC | Three temporary copies plus a whole read. Upload size limit not verified. | Name of the upload must be checked | As case 1 | Both: keep it, but as one source of the same step | No |
| **(d)** The user types a path | The exact path | No copy | Weakest: typed text is the most hostile input (`..`, links, a folder with a similar name). A resolved-path check is needed. | A text box | Architect: not recommended (second way, security burden, no gain over b). User: cannot judge the security; does not need it if (b) exists. | No |

Suggestion (both viewpoints): (b), with the browser upload as the other source. Why, in short: the user sees what the app may read; the deployment file decides the list (D-0425); nothing is copied.
A caution from the architect (RUN, `architect_scratch/confine_out.txt`): a link that leaves a declared place is refused. On HPC a data folder is often a link to a project area. The real folder must then be declared as the place.

## 5. The mechanism both viewpoints propose
- **One step, "choose the data for this table", with two sources.** Source 1: a file from the own computer (the app copies it into the user's data place, then links it). Source 2: a file of a declared place (the app only links it). D-0426 ("the user selects the data") is this same step, not a second one.
- **Where the user meets it.** Both: (i) when a recipe is opened and its data is absent (D-0426), only where the deployment lets the user choose; where not, the opening stops with a plain reason (D-0427). (ii) In HOME's Data Import panel, at any time. One screen, one set of words.
- **The small record.** "This table of this recipe reads this file." Kept in the user's place (proposal: `<user place>/data_links/<recipe id>.json`). The file reader has one place (`locate_dataset_file`, `orchestrator.py:172`) that reads it first, so keys, hashes, sessions and the export follow it. A second recipe with a table of the same name reads its own record, else its own default. Nothing is inherited.
- **A missing file stops the opening** with a plain reason (table, file, date of the choice). It offers "choose again" or "use the recipe's default again". Never a silent fallback.
- **Stored tables and saved sessions.** Stored tables are keyed by file content, so a new file gives new keys and they are rebuilt (READ `cache_keys.py:462-474`). Saved sessions stay in the list; restoring shows the warning of row 2. Whether it should refuse is a choice in section 9.

The architect names three variants for the record:
| Variant | What it means for the user |
|---|---|
| **V1 the position of a file** (a file in `<my data>/<recipe>/<table>.tsv` wins) | No extra record. But a file left in the folder wins silently at the next opening. No name, date or hash without a second record. Case 2 would need a copy, so two mechanisms. |
| **V2 a record per recipe** (recommended by the architect) | Explicit and visible per table. One mechanism for upload, selection and bundle. A second store beside the files; it must not disagree with them (missing file stops, changed content shows by hash). |
| **V3 part of a dated copy of the recipe** | The data choice is in the scientific document. But every data choice makes a new recipe file; the recipe place is not the user's; hashes of recipes change with data; the selector fills with copies. |

## 6. What stays the user's business and what the app guarantees
**The user's business** (your words, D-0434):
- Which file is the right one.
- Whether the data is sensitive, and keeping it in the own place.
- Keeping an earlier copy elsewhere; choosing another name to keep two versions.
- Deleting a file in the own file system (D-0437).
- Putting a file in a declared place by own means.

**The app guarantees:**
- It says, per table, which file is read, from which place, chosen when, with its content code.
- It reads nothing outside the declared places, and no other file silently (no fallback).
- It writes only into a `read_write` place of the user, and only after a confirmation when it replaces. Never a `read` place.
- It checks the file with the recipe's own reader before it writes anything.
- It records place, name, date and hash for the session and the export.
- It says plainly when a file changed after a figure was built.

**The honest limit:** the app can say "the file can be read". It cannot say "the file is complete". A file cut at the end of a line looks complete (RUN, cut-file report). The words on screen must never promise more than "can be read".

## 7. What must change before "the user selects the data" (D-0426) can exist
Today a recipe whose data is absent never reaches the selector. At start, the load gate reads every recipe's data once. A recipe that fails is rejected and never listed (READ `app/src/bootloader.py:431-447`, `_gate_one`; RUN case 6 of `tmpAI/panel/deployment_no_user/RUN_FACTS.md`). So the user cannot be offered a choice for it. To make D-0426 possible:
- The gate must check the recipe's shape at start, and the availability of the data later, at the opening, per user and per chosen file.
- This touches the recipe selector (a recipe with absent data now appears), the rejected-recipe list, and the rule of ADR-094 ("a recipe failing either check never reaches the list").
- It is the largest step of the architect's build order. Nothing small and whole can be built before it and before the named places (D-0436); a stop-gap on Data Import would be a half fix.

## 8. Sentences proposed (all PROPOSALS, none tested with a user)
**Is the app saving the data uploaded? Today:** "Yes. A file uploaded in Data Import is written over the data file that the recipe reads. That file can be a shared file. The old file is not kept, and the name of your file is not recorded."
**Under the proposal:** "Yes, in your own data folder only (the path is shown). The app records which table reads it, the date and its content code. It stays until you delete it in your own file system. The app never writes into a shared (read) place."

**Before an upload:** "This file will be saved in your data folder `<path>`. Everyone who can open that folder can read it. It stays until you delete it yourself. Nothing in the shared or consortium data is changed. If your data is sensitive, keep it in your own place."
**Same name exists** (written from what the code does): "A file named `X.tsv` is already in your data folder. Replacing it removes the old file; it is not kept. These tables read it: `<table, recipe>`. N saved sessions were made with it. They will still open, with a warning that the data differs and that their steps may match other rows. Replace? [Replace] [Cancel]"
**After an upload (stays in the panel, not 10 s):** "Table `T` of recipe `R` is now read from your file `<name>` (`<path inside the folder>`), uploaded `<date>`, content code `<8 characters>`. The earlier file of this table was replaced and is not kept."
**File picked on the server:** "Table `T` of recipe `R` is read from `<path>` in place `<label>` (`read` or `read_write`), `<size>`, changed `<date>`, content code `<8 characters>`. The file is not copied. If it changes, the app tells you."
**A chosen file is missing:** "The file you chose for table `T` is not there: `<path>`, chosen `<date>`. Choose again, or use the recipe's default file again."

## 9. The choices for you, ranked
| # | The question | The options | What each viewpoint says | Reconsiders a decision? |
|---|---|---|---|---|
| 1 | **Stop the silent overwrite.** An upload must never write over a shared, `read` or test file. Where does it go instead? | (a) always the user's `read_write` data place; (b) the recipe's own path when the user may write there; (c) no upload control where there is no such place | Architect: (a), never at the recipe's `source.path`. User: "my data", only me. Both agree. | Strengthens D-0434/D-0429; changes the role of `testing_mode` (information) |
| 2 | **The record of which file a table reads** | V1 position; V2 record per recipe; V3 dated recipe copy | Architect: V2. User: wants the link per recipe and table recorded; does not care where. | V3 touches D-0390 naming in practice; V2 touches ADR-094 gate and ADR-097 record (information) |
| 3 | **A chosen file that is missing** | stop with a plain reason; or fall back to the default | Architect: stop. User: wants "never reads another file silently". | No |
| 4 | **Case 2:** is picking from the declared places wanted? | (a)+(c) only; (b) plus the browser upload; (d) typed path | Both: (b). Architect: not (d). | The gate change of section 7 (information) |
| 5 | **A subfolder per recipe** | one folder per recipe; one flat "my data" | Architect: per recipe (same name in two recipes never meets). User: flat, "I understand my data better than a tree". | No |
| 6 | **Keep the uploaded name?** Bad names (`..`, separators, empty) | keep and refuse bad ones; rename; add the table name | Architect: keep, refuse bad ones, never rename silently. User: keep the name; asks what happens with the same name for two tables. | No |
| 7 | **A date rule for data file names** (D-0437 names recipes; D-0434 mentions the dated name) | applies to data files; does not | Architect: open. User: not addressed. | Reads D-0434 and D-0437 together |
| 8 | **A session restored on other data** | keep the warning; refuse, as D-0362 does for a changed recipe (not built) | Architect: open; the confirmation sentence depends on it. User: a restored session must say "built from an earlier version", visible without a click. | D-0362 is for a recipe |
| 9 | **A delete control in the app** | none, only "use the default again" and the path shown; or a remove control | Architect: none (D-0437 and D-0434). Caution: where the user cannot reach the folder (a container folder, a Galaxy job folder) the user cannot delete. User: wants to list and remove. | A remove control reconsiders D-0434/D-0437 wording (information) |
| 10 | **A recipe imported from a bundle** | the user may re-link its tables; or not | Architect: open; D-0435 puts the data in the user place, the record can say "bundle". Today the refusal is an agent's provisional choice. User: wants a plain sentence "this recipe reads the data that came with it". | D-0435 |
| 11 | **What the export records about each data file** | place, path inside the place, name, date, hash (no absolute path); or as today (full paths) | Architect: the first. User: place, name, hash, date, "uploaded by the user". | No |
| 12 | **Who can see the user's place** | tell what is known per deployment; say nothing | User: cannot write the sensitive-data sentence without knowing. Architect: the sentence says "everyone who can open that folder; where one running copy is shared, everyone using that copy" (D-0429). | No |

## 10. Not verified
- No app started, no browser seen. All screen sentences are proposals. The user viewpoint read only the code that produces the texts, not the ledger lines.
- The upload size limit of the app, and the time and memory of the whole-file read for the hash on a large file.
- Whether anything besides `locate_dataset_file` opens a recipe's `source.path` (the checkers read it; not checked whether they open it).
- Whether the user place is already declared for `user_data` and what is in it (the user viewpoint did not check it).
- Who else can read a user's place on HPC or Galaxy; what a Galaxy job folder lets a user delete.
- Two copies of the app on one folder; whether the standard export holds a hash per file.
- Whether `refresh_replaced` is still needed beside the content keys.
- I checked myself: `get_testing_mode` and the 8 shipped files; `_gate_one` at `bootloader.py:431-447`; the restore notice at `session_handlers.py:607-616`. The rest is taken from the two viewpoint files and the earlier reports.
