# Which data files may a recipe read, and what happens on an upload: the page for Eve to decide

Coordinator, 2026-11-18, about 14:51 by the clock. This is question 8 of the recipe-arguments report (her lean: A, after a study of her usage cases) plus the block on the file type she asked for.
Evidence: `FACTS.md` (read in the code) and `TRIAL.md` (run for real on a trial branch that is never merged) in this folder. Three viewpoints read both pages: scientist, user who is not a developer, architect. They recommend. She decides. Nothing is built.

## Flagged first: three things that change a result in silence today (all run in the trial)

1. **An upload replaces the file a recipe reads, and says only "imported".** The recipe text is unchanged, the data is not, and the old content is gone. No option below fixes this. It contradicts her rule that nothing is replaced silently (the architect names D-0050; her decision on bundles, D-0045, covers bundle import only).
2. **The check and the run start a relative path from two different folders.** The check starts from the project root. The run starts from the folder the app was started in. The same recipe finds its file, another file, or none, depending on where the app was started. A lookup table written as `lookup.tsv` beside its recipe passes the check and is then "not found" when the app is started from the project root.
3. **A file is "imported" and never found.** A `.csv` or a spreadsheet upload is accepted, its bytes are written as they are, and the table breaks later or the app keeps the older data.

## What the user sees today, and what each option changes

| | Today | Folder check at the check only | Folder check at the check AND when a file is opened | File-type layer |
|---|---|---|---|---|
| A path with `..` or an absolute path | The check refuses. Blueprint only reports, so the file is still read | same | the file is not read | - |
| A link in the data folder to a file elsewhere | read | the check refuses; still read in Blueprint | not read | - |
| A `.txt` or `.yaml` named as data | read as data, or "wrong columns" | same | same | refused with a plain message that names the fix |
| A `.csv` or spreadsheet upload | "imported", never found | same | same | refused at the upload |
| Shipped recipes refused that work today | 0 | 9 (12 with three test recipes that already fail) | same | 0 |

## The three choices

**Choice 1: where the folder check runs.**
- 1a. Nowhere (today).
- 1b. At the recipe check only.
- 1c. At the check and at the moment a file is opened, as one function used at both moments.

**Choice 2: which folders are allowed.**
- 2a. The deployment's folders (raw data, recipes, gallery, user data).
- 2b. The recipe's own folder.
- 2c. Both.

**Choice 3: the file-type layer** (only `.tsv` and `.parquet`): yes or no.

## The viewpoints

| Option | Viewpoint | For | Against | Evidence |
|---|---|---|---|---|
| 1c, check and open | Scientist | A check-only rule can be walked around in Blueprint | - | trial cases A2, A3 (ran) |
| 1c | Architect | One function, two moments; put the open check where the app picks the file, so reading and hashing both pass through it | The checker files collide with the big recipe change: build after it merges | read: `orchestrator.locate_dataset_file` |
| 1c | User | Same answer at both moments | A false refusal teaches users to click through | 12 refused today |
| 1b, check only | all three | less to build | does not stop the read | A2, A3 |
| 2a, deployment folders | User | One place to say "your data goes here" | Refuses 12 shipped recipes; refuses a lookup table beside its recipe | trial section 4 |
| 2b, recipe's folder | all | - | Refuses 23 shipped recipes, among them every normal recipe whose data is in the raw data folder | case 1a |
| 2c, both | Scientist | The recipe's folder is the only base that travels with the recipe | Still refuses 12 | section 4 |
| 2a with a NEW "reference data" folder | Architect | Default lookup tables get a declared home | The deployment has five folder keys today; a sixth is a new decision | read: ADR-048 |
| 3, type layer yes | all three | Refuses nothing shipped; cheap; tells the user the fix | A tab-separated `.txt` is refused; compressed files stay unread (not read today either) | section 4, case A4b |

Points every viewpoint made, whatever she chooses:
- The check must not judge a path the run ignores. When a pipeline deposits tables by their id, or a bundle is imported, the recipe's path is not used; today's trial refuses all 16 recipes of the pipeline test deployment for that reason alone.
- A refusal must say in plain words which folder is meant. Today it prints long absolute paths and names no table.
- The upload notice must say which file was replaced, or that the file was not imported.

## What is decided, and what is not (the architect checked the records)

- DECIDED: the shape rule (no `..`, no absolute path, no `~`) and "no change of the path engine" for the lookup by id (D-0035).
- NOT decided: the folder check itself. It stands in the specification as a recommendation with no ledger line. So choice 1 and 2 are open, and her lean (A) is the first word on them.
- The specification already says "relative to the project root" in two places. Only the run does otherwise.
- Not decided: where an upload writes, and what it does when the file exists.

## My recommendation

1. **1c**: the folder check at the check and at the open, one function. Reason: a rule that Blueprint can walk around protects nothing.
2. **Fix the starting folder first, as its own small step**: the run uses the project root, as the specification already says and the check already does. This is a confirmation of a written rule, not a new one, and it removes silent behaviour 2 at once.
3. **Allowed folders: 2a, and she chooses between two ways for the lookup tables**: a new "reference data" folder in the deployment file, or moving the default tables into the raw data folder. I do not recommend 2c: the scientist's reason for it (the recipe travels) is a real one, but a recipe folder that also holds data mixes two things her rules keep apart, and it still refuses the same 12.
4. **3 yes**: the file-type layer.
5. **The upload**: never replaces a file without asking, and says what it did. This needs her decision (question 3 below).
6. Order: the shared functions and their tests, the type list, the upload first; the checker last, after the big recipe change is merged.

## What she decides

1. Choice 1: 1a, 1b or 1c.
2. Choice 2: 2a, 2b or 2c; and for the default lookup tables: a new "reference data" folder, or move them into the raw data folder.
3. An upload onto an existing file: ask (replace or cancel), refuse, or keep both under a new name. And whether a replaced file is kept somewhere.
4. Confirm: a relative path in a recipe starts from the project root, at the check and at the run. (The scientist prefers the recipe's own folder; the specification says the project root.)
5. Choice 3: the file-type layer yes or no. If yes: is a tab-separated `.txt` refused (suggestion: yes, with the message "rename it to .tsv"), and is a `.csv` or spreadsheet upload refused or converted in a visible step (suggestion: refused for now; conversion is a separate decision).
6. The 9 shipped recipes that work today and would be refused: correct them (move their data), which is what her rule on wrong recipes says. Confirm.
7. What the export records about the data file (checked by a scout after this page was written, read in the code, not run; `EXPORT_RECORD_facts.md`): the real path of the file that was read is written in the README and in `effective_run.yaml`. NOT written: a hash per file (only one combined hash), and where the file came from (the recipe's path, an upload, a deposit by id, an imported bundle), with no upload time and no uploaded file name. A table with no file found is left out of the combined hash instead of being marked missing. Does she want the origin and a hash per file in the export? Suggestion: yes, as part of the upload fix; it is what makes "same recipe, same data" checkable after an upload.

## Not covered by the two evidence pages (the architect's note)

The history of the recommendation in the specification; that the check should be switched by the lookup mode; the tests. The API and pipe ways of getting data are not built at all, so nothing was tried for them.
