<!-- panel-user, 2026-11-21; saved from its report, unchanged; filed for the coordinator -->
# USER viewpoint: where an uploaded data file is saved (2026-11-21)

I read the brief, `agent_principles.md`, `decision_compliance.md`, `orchestrator.py:160-230`, `data_import_handlers.py:70-308`, `data_file_cut/REPORT.md` and `default_data/FACTS_FOR_THE_OWNER.md`.
I did not read the ledger lines themselves. The grep output was too long, so I rely on the brief's quotation of D-0417 to D-0437.
I could not save a file, so the full text is below.

Labels: READ is `file:line`. REASONED follows from what I read. WANT is a proposal.

## 6-line summary (anything that changes a result silently first)

1. **Silent today (READ).** An upload replaces the file the recipe reads (`orchestrator.py:197-209`, `data_import_handlers.py:303`). That file can be a shared file or the repository's test data. Nobody is told that a shared file changed, and no copy of the old file is kept. Another recipe, or another person on a shared deployment, reads the new data without knowing. The old file's figures cannot be redrawn.
2. **Silent today (READ).** With `data_lookup: by_dataset_id`, a recipe reads `<table name>.tsv` in the data folder, not its declared path. No screen says so (`default_data/FACTS` finding 1). The same applies to a cut file, which gives a table with missing values and no message (`data_file_cut/REPORT.md:8`).
3. Today the app does save the upload. It overwrites the recipe's data file in place. It is not saved in "my files".
4. Case 1 (my computer): I want one "my data" place that only I can write to. The old file is never overwritten silently. The screen says "this table is now read from this file".
5. Case 2 (HPC or Galaxy): I want to pick a file from a list of what the app may read. Nothing is uploaded or copied. The pick is recorded. Upload from my computer stays as the other source.
6. Both cases go through one step, "choose the data for this table". The app records the file, its name, its hash and the date, and never reads another file silently.

## Q1. Case 1, upload from my own computer

**What I see today.**
- Upload slots exist only in `testing_mode` (`data_import_handlers.py:131`). Without it I see "Data paths are set by the deployment configuration (read-only)" (`:134-135`).
- The hint says "replace the active data analysis recipe source" (`:154`).
- After Apply I see "N file(s) imported — plots are refreshing now. name -> tables (path)" (`:304-306`). That sentence is the only place the path appears, and it disappears after 10 seconds.

**What I do not know at the moment of upload.**
- Whether the target is a shared file.
- That the previous file is gone.
- That other recipes reading the same table name change too. The code says "replaced for every table that reads it" (`:294`), but I am not told.

**What I want, as proposals.**
- One place "my data", read_write, in my user place (D-0429).
- Name: the uploaded name. A table name is the app's idea and not mine.
- Subfolder per recipe: not needed at first. I understand "my data" better than a folder tree.
- The link "this table reads this file" must be kept for the next opening. I do not care where it is stored, but the recipe, the data and the session must show it. I want the link per recipe and per table. A second recipe with the same table name keeps reading its own file until I choose for it too. I do not want a global effect.
- Same name again: one confirmation (D-0434), with the consequence stated. Old figures and stored tables built on the old file are rebuilt.
- I should be able to see the list of my uploaded files and remove one.

**Sentences I want on screen (all proposals).**
- Before upload: "This file will be saved in your data place, `<path>`. Only you can write there. It stays until you remove it. Nothing in the consortium recipes or the shared data is changed."
- Same name: "A file named `X.tsv` is already in your data place. Replacing it removes the old file; it is not kept. These tables read it: `<table, recipe>`. Their figures will be redrawn from the new file. Replace? [Replace] [Cancel]"
- After upload: "Table `T` of recipe `R` is now read from `<path>` (uploaded `<name>`, `<date>`, content fingerprint `<short hash>`)."
- Sensitive data: "If your data is sensitive, keep it in your own place. This deployment's administrator may be able to see this place."
- Last line: I cannot say if that is true for every deployment. See "To decide first".

**What the export and report must carry (WANT).** Place, uploaded name, hash, date, and "uploaded by the user" versus "default of the recipe". The hash exists today (`data_batch_hash`, per the cut-file report).

**Saved sessions and stored tables.** If I replace a file, a saved session made with the old file must say "built from an earlier version of `X.tsv`". It must not quietly show new numbers. Today's notice only appears "after a tab click" (cut-file report, case 5). That is too weak.

## Q2. Case 2, the file is already on the server

I do not know where the app looks. This is the main user problem.

| Option | What I understand | What stays hidden | Risk of a wrong choice | Large files |
|---|---|---|---|---|
| (a) I put the file in a declared place by my own means | Only if I am told which folder. Otherwise I cannot do it. | Which folder, and the exact file name the recipe expects. | High. A wrong name and the recipe stops, or reads a stale file. | Good |
| (b) The app lists the files of the declared places, I pick one | Best. I see what the app can read, I click. It is the same idea as Galaxy. | Little. The list shows each place and its access word. | Low. The app cannot read outside the list. | Good, no copy |
| (c) Download to my computer and upload again | Understandable. | A copy is made. | Slow, and copies pile up. It works today. | Poor |
| (d) I type a path | Familiar to HPC users. | What "inside a declared place" means. A refusal needs a plain reason. | Security: the app must refuse any path that resolves outside a declared place, including `..` and links. I cannot judge this. | Good |

**Recommendation (WANT): (b), with (c) kept as the upload source.**
- (a) is the pipeline delivery that already exists. It becomes usable once the screen names the place.
- Without the list or the place shown, I fail at (a) and (d).
- With (b) the user sees the data. It also fits "the deployment file decides what may be read" (D-0425): the list is that decision, made visible.

**Sentences I want for (b) (proposals).**
- "These files are in places this deployment lets the app read. Choose the file for table `T`. The file is not copied or changed. The app will read it from where it is."
- After the pick: "Table `T` of recipe `R` is read from `<path>` (`<size>`, changed `<date>`, fingerprint `<short hash>`)."
- Because the file stays where it is, someone else may change it: "This file is in a place you cannot write to, and others may change it. If it changes, the app tells you and the figures are marked as built from the earlier version."

**Where the file stays.** The place may be `read` or `read_write`. The access word says only who may write. Reading from a `read` place is correct.

## Q3. One mechanism or two?

**One step, with two sources.** "Choose the data for this table": from my computer, or from a file in a declared place. This is how I would explain it in one sentence, and it also covers D-0426.

**Where I meet it.**
- At the opening of a recipe whose data is absent. This is where I need it, and it must name the table and the file that is missing.
- In the HOME Data Import panel, to change data on purpose.
- The same screen in both places, so I learn it once.

**What I do not want.** A second screen with different words for the same act.

**Today.** Only the browser upload exists. A file already on the server cannot be picked (brief, READ).

## Q4. "Is the app saving the data uploaded?" Two sentences for the documentation

- **Today:** "Yes. The app writes the uploaded file over the file that the recipe reads, without keeping the old file. That file can be a shared file."
- **Proposed:** "Yes. A file you upload is saved in your own data place and only there. It stays until you remove it. A file you choose from a place of the deployment is not copied, and the app records where it is."

**What I must be told at the upload.**
- Where it goes.
- Who can see it.
- How long it stays.
- That it replaces an earlier file only after my confirmation.
- That sensitive data stays in my own place.

## Q5. The user's business and the app's guarantee

**The user's business.**
- Which file is the right one.
- Whether the data is sensitive.
- Whether the file is complete.

**The app guarantees.**
- It says which file each table was read from.
- It never reads another file silently.
- It never writes into a shared or `read` place.
- It records the hash.
- It refuses a path outside the declared places.
- It says plainly if a file changed after a figure was built.

**What the app cannot guarantee.**
- It cannot know that a file is cut at a line end (`data_file_cut/REPORT.md:50`). It must say so honestly, and not call a file "checked" when it is only readable.
- A check marked "ok" for a cut file would be a false comfort. The words must be "the file can be read", not "the file is complete".

## Q6. Edge cases (what I expect to see)

- **Two tables read the same file.** The screen says "tables A and B read this file". A replacement shows both before I confirm.
- **Same uploaded name for two tables.** Two different files with the same name must not overwrite each other silently. The app asks me. I may need a rule. See "To decide first".
- **Recipe from a bundle.** Its data came with the recipe and no upload place exists (`orchestrator.py:204-205`, `file_place` returns None). I want a plain sentence: "This recipe reads the data that came with it. You cannot replace it here. To use other data, copy the recipe or import it again." If a replace were refused without that sentence I would be lost.
- **Static page or pipeline.** No upload control. The screen says "The data is fixed by the deployment: `<path>`" and shows the fingerprint. Today's lock sentence is a good start (`:134-135`).
- **Cut file or other columns.** Today a file with a short last row is accepted with no message (cut-file report, `:8`). I want at least "N rows have fewer fields than the header; the missing values are read as missing", as in that report's option 2.
- **Very large file.** I need the size shown before upload, and a refusal that names the limit. I do not know the limit. Not verified.

## Words I do not understand

- "read_write" and "read": clear after one line of explanation ("you can write there" and "you can only read there").
- "declared place": whose declaration, and where can I see it?
- "deployment": I need one sentence, "the installation the administrator sets up".
- "hash" or "fingerprint": say "content fingerprint" and show 8 characters.
- "table" versus "file": I upload a file, the recipe reads a table. The screen must name both.
- "anchor" in `user_data / "anchors"` (`data_import_handlers.py:272`): I do not know what it is.
- "testing_mode": it decides whether I may upload at all. As a user I cannot tell why it is off.

## Table: today and wanted

| case | where the file is | who may write there | what the app records | what I see |
|---|---|---|---|---|
| **TODAY, case 1** upload from my PC | Overwrites the recipe's data file: its `source.path`, or the existing file, or `<table>.tsv` in the data folder (`orchestrator.py:197-209`) | Whoever the folder permissions allow; the app does not check that the place is mine | The new file's hash in the keys. No record of the old file, of who uploaded, or of the date. | Upload slot only with `testing_mode`. After Apply, a 10-second message "N file(s) imported ... (path)". |
| **TODAY, case 2** file on HPC or Galaxy | Where it is. The app has no way to pick it (brief, READ). | Not changed by the app unless I upload over it. | Nothing for a read in place. A pipeline deployment reads `<table>.tsv` without saying so. | The locked sentence, and the data location or the file list. |
| **WANT, case 1** | "My data" in my user place, `read_write` | Only me | Place, uploaded name, hash, date, "uploaded by the user", and the link table to file per recipe | Before: where it goes. After: "Table T of recipe R now reads `<path>`". My files can be listed and removed. |
| **WANT, case 2** | Where it is, in a declared place (`read` or `read_write`). No copy. | Not the app. | Path, size, modification date, hash, "chosen by the user from place P", and the link table to file | A list of the readable files with the place and its access word. After the pick, the same sentence as case 1. Later change: "this file changed since the figures were built". |

## To decide first (ranked)

1. **Stop overwriting a file in a shared or `read` place.** Today an upload can overwrite a shared file or the test data silently. This changes results for other people and recipes. Decide this before anything else.
2. **What stays recorded** about "this table of this recipe reads this file": the file, the hash, the date and the source (default, upload, picked). Without it, nothing is traceable.
3. **Is picking from the declared places (option b) wanted?** The alternative for Case 2 is only (a) plus (c), which leaves me not knowing where to put the file.
4. **The one screen sentence "this table is now read from ..."**, always visible, not a message that vanishes after 10 seconds.
5. **Same uploaded name for two tables:** keep the name, ask me, or add the table name to the file name?
6. **A file already changed or cut:** how far does the app inform me? At least a notice that is visible without a click.
7. **Who can see my place?** The sentence about sensitive data depends on the deployment, and I cannot write it without knowing.

## Not verified

- The browser screens. I read only the code that produces the texts.
- Any ledger line. I rely on the brief's quotation of D-0417 to D-0437.
- Whether a "my data" place is already declared for `user_data`. I saw `bootloader.get_location("user_data")` at `:272`, but not what it holds.
- How a file in a `read` place is protected on HPC or Galaxy, and who else can read my place there.
- Any file size limit.
- Whether a path outside the declared places is already refused.
- How `apply_import` and `refresh_replaced` write, and the exact text of the same-name confirmation. I did not read `data_import_check.py`.
- Whether the same notice appears for another person's session on a shared deployment.

Paths read (absolute):
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/modules/orchestrator.py`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/handlers/data_import_handlers.py`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/coordinator/data_file_cut/REPORT.md`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/coordinator/default_data/FACTS_FOR_THE_OWNER.md`
