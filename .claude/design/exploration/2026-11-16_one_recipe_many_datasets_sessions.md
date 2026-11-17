Exploration report. Nothing in it is decided unless a ledger number is given. Status: Nothing is decided and nothing is built (as written in the report). Written: 2026-11-16. Source: tmpAI/panel/sessions/PROPOSALS_for_eve.md. Copied here on 2026-11-17.

Paths inside the body that point to tmpAI/ working files are local (not in git) and stay as written.

---

# One recipe, many datasets, several sessions: proposals for Eve

Written 2026-11-16 by the coordinator from three viewpoints (data scientist, architect, user). These are proposals. Nothing is decided and nothing is built. Your request is message M175 of the channel.

The facts the viewpoints started from are in `tmpAI/panel/sessions/scout_what_is_decided.md`.

## Read this first: four things that are wrong or silent today

These were found by reading the code. None is new today.

1. **Uploading data in testing mode overwrites the recipe's own data file.** The Data Import panel copies the uploaded file onto the recipe's source file (`app/handlers/data_import_handlers.py:321-334`). The old session keeps its name, but its data is gone. Your decision of 2026-11-14 says "the recipe's path is not touched" (ledger D-0045). The code does not follow it.
2. **The export would name the wrong data.** The export records the recipe's default data paths (`app/handlers/export_handlers.py:121-128`). Once a user can choose a dataset, a figure made on dataset B would be labelled with dataset A's paths, unless this is changed first. Your decision D-0191 ("always the dataset the user has actually worked with") cannot be met today, because no dataset choice exists.
3. **A session restored on other data only warns.** The warning is a notice that disappears after 8 to 12 seconds. It gives no counts. The restore continues, so audit steps made for one dataset are applied to another, and a step that now matches no row is not reported (`app/handlers/session_handlers.py:353-370`).
4. **A missing data file gives a normal-looking session.** The data hash turns a missing file into a placeholder text and still returns a valid session name (`app/modules/session_manager.py:198-212`).

Suggestion: fix point 1 before anything else is built on the data choice. It needs no new decision; it follows D-0045.

## What already fits your use case

- A session is named by the recipe and the data together (the first characters of both hashes; ledger D-0025). A second dataset therefore already gives a second session. Audit steps of two sessions cannot mix, because each session has its own folder.
- The session list is already grouped by recipe.
- A label can already be typed on each session card. It is stored. It is not exported.

## The seven questions, with the options

"All three" means the three viewpoints agree.

### 1. How the user chooses the dataset

No decision exists on a dataset selector. The review session called it "already decided"; only your words of 2026-11-15 exist ("the user will be able to select data to use - to replace the default data used in the recipe"), quoted in the intent document, with no ledger line.

| Option | Who recommends it | For | Against |
|---|---|---|---|
| A. A dataset is a folder beside the others (one folder per delivery of the pipeline). The user picks one from a list of names; never types a path. Shown only when the deployment switches it on. | Architect, scientist | One function already decides which file is read and hashed, so one more argument is enough. The user sees names and dates. It respects "import only by configuration" (D-0030). | "A folder is a dataset" is a new rule; it needs your yes. |
| B. The operator changes the data location in the deployment file. | (alternative) | Nothing to build. | The user cannot choose in the app. The choice is not recorded per session. |
| C. The Data Import upload creates the dataset folder. | (alternative) | No need for the pipeline to deliver folders. | More to build (the upload, who is allowed). |

Recommendation (the coordinator's, not a decision): A.

### 2. What identifies a session

All three: keep the name as it is (recipe and data, by content). Two files with the same content are the same session; a re-saved file is a new one. What is missing: the session must also remember the dataset's NAME, so the card can show it and a restore can find the data again, or refuse plainly when the data is gone.

### 3. The label and a comment

| Option | Who | For | Against |
|---|---|---|---|
| A. One text per session, longer than today (a comment), editable at any time, stored in one place, written into the export from that one place (the README and a `#` line at the top of the audit_recipe). | All three | One source, so the screen and the export cannot disagree. | None found. |
| B. A short label plus a separate longer note. | Scientist (as an addition) | A title and a reason are different things. | Two fields to keep. |

The user viewpoint adds: pre-fill the comment with the dataset name and the date, so that two cards never look alike.

Recommendation: A, pre-filled.

### 4. Several sessions side by side

| Option | Who | For | Against |
|---|---|---|---|
| A. One session is open at a time. The user switches. The card shows the comment, the dataset name, the date saved, the number of audit steps, and the hash last and small. | All three | Small. Steps cannot mix. | No direct comparison of two datasets. |
| B. Two sessions open and compared. | (later) | Compare two deliveries. | Large: the app holds one state today. |

Recommendation: A now. B is a later feature.

The user viewpoint says plainly: "Batch:" and eight characters of a hash cannot be read by a person. The card needs the dataset name.

### 5. What a data change does to the audit steps

Three records disagree today, and none is your decision for a DATA change:
- the steps stay with the old session (a design note of 2026-11-12);
- the steps are removed (another design file);
- the steps are applied again on the new data, each with a status (the "re-base"; your decision D-0088 names RECIPES: "however unlikely recipes are changed during work").

| Option | Who | For | Against |
|---|---|---|---|
| A. The steps stay with the old session. A new dataset starts a new session with no steps. The user may copy the steps over on request; each step then shows a status that stays on the screen: applied (rows before and after), matches no row, column missing. | Scientist, architect, user | Nothing is lost and nothing changes without the user choosing. It follows from how a session is named. It fits "changing data is not necessarily a failure" (D-0186). | The user must be told clearly that the steps stayed in the other session. The copy on request is a new piece to build. |
| B. The steps are applied again automatically on the new data. | (alternative) | Fast for weekly data. | A result changes on new data without the user choosing. A filter on sample ids that matches nothing does nothing, silently. |
| C. The steps are removed. | Nobody | | It destroys the user's work. |

Recommendation: A. The re-base (D-0088) then covers a changed RECIPE only, as your words say.

Flag: this reconsiders nothing you decided, but it closes a disagreement between records. Two design files would have to change; that needs your yes.

### 6. The check of a dataset

All three: when a dataset is chosen, it is checked against the recipe before any table is built. A missing column or a file that cannot be read is an error that names the file and the column and gives the contact. A dataset that is only different passes. The scientist adds: show the number of rows, samples and missing values per table, so the user sees that this is the data they expect.

The impact report for "a recipe is checked when it is selected" (your decision D-0184) is being written separately and covers the timing.

### 7. What the export records

All three: the dataset's name, its content hash, the row counts, the recipe hash, the session name and the session comment, in `effective_run.yaml` and the README. This follows your decisions D-0187 to D-0193. The architect notes that when the choice of dataset goes through the one function that reads the data, the export names the chosen dataset with no second piece of code.

## The order the architect proposes (nothing half-built)

1. Stop the upload from overwriting the recipe's data file (D-0045).
2. The dataset as an argument of the one function that reads and hashes the data, with tests.
3. A restore finds the dataset again, or refuses plainly.
4. The label becomes a comment and goes to the export from one place.
5. The check when a dataset is selected.
6. The list to choose from, on the screen.
7. The re-base last, for a changed recipe only.

## What you are asked

1. Is a dataset "one folder per delivery, picked from a list" (question 1, option A)?
2. One comment per session, pre-filled with the dataset name and the date, exported (question 3, option A)?
3. After a data change, do the audit steps stay with the old session, with a copy on request that shows a status per step (question 5, option A)?
4. May the overwrite of the recipe's data file by the upload be removed now? It follows D-0045 and needs no new decision; I ask only because it changes what the Data Import panel does in testing mode.

Not checked by the viewpoints: the screens as drawn; whether the raw data copy is in the Reproducibility part of the export; the Blueprint side.
