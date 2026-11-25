# Deployments with no user: the viewpoint of a deployer who is not a developer, and of a visitor of the page (panel-user, 2026-11-21; filed by the coordinator from its report)

Labels: RUN = from `RUN_FACTS.md` or a screenshot it looked at; READ = file:line taken from `FACTS.md` (it did not read the code); REASONED = its inference. Screenshots looked at: c2a, c2b, c5_A2, c5d, c6_A3, c7a, c8.

## 1. Summary (what changes a result silently first)
1. RUN: a data file cut in the middle of a line draws the plot from 21 of 42 samples, with no message and "Alerts (0)" (case 7a, `shots/c7a_A_afterF5_broken.png`). REASONED: the same silent short table for a cut at the end of a line. The worst finding.
2. RUN: an open page keeps the old picture after a refresh; only a click on a tab gives a notice that fades (case 5). No date, version or hash of the data is shown anywhere (`c5d_info_panel.png`): a figure cannot be cited.
3. RUN: a column change gives a long text that blames the recipe ("Correct original_name"), with the author's e-mail; it does not say the data file changed, nor which headers the file has now (only the console does). "The cause is my weekly delivery; I cannot fix the recipe."
4. RUN: a user folder that cannot be written gives a blank grey page with no text; the error is only in the console, at each connection; nothing at start. A page that only shows data needs a writable folder and nobody says so.
5. RUN: data absent at start: the visitor gets a white page ("connection refused"); the console text is good.
6. RUN: the page writes 24 tables and a session record with no click; the export says "install Quarto" when the temporary folder is the cause.

## 2. Per question of the brief
| Question | As a deployer | As a visitor |
|---|---|---|
| 1. The app's own place | One place and one sentence: "The working place: the app keeps rebuilt tables and temporary files here. Nobody else uses it. You may delete it; the app rebuilds it." One place with two subfolders the app makes itself (tables, temporary); two separate folders "I would get wrong". The app creates it if the parent exists and can be written; otherwise it stops at start with a plain text. It holds rebuildable tables and temporary files of an export; never my data, my recipes, or anything a person saved. The name `user_data` confuses on a page with no user. A static page should not write the session record at all (its own notice says it "cannot be exported or restored"); that also removes the cause of the blank page. | sees nothing of it, and should not |
| 2. Nothing writable | Stop at start is best: I find the fault before the visitors do. "This session only" works but costs 22 to 31 s at each first opening (RUN), a silent slowness with many visitors. "In memory" is fast after the first opening, with a memory growth I cannot see. Static page: stop at start as the default; the other two only if I choose them in the file, with the consequence written beside the key. Pipeline run: "this session only" is acceptable (one run, one visitor). | must see a plain page, not a white one |
| 3. Refreshed data | I can promise: write to a temporary name, rename, then write last a list of the delivered files with their hashes. The app must check by itself (hash and count against the list) and keep showing the last complete data when a file does not match, with a message. I do not need history, but I must be told it is not kept, and that I must keep last week's data to reproduce last week's figure. | a notice that stays: "The data of this page was updated on [date]. Reload (F5) to see it." |
| 4. What the visitor is told | The date comes from a field I write in the list of delivered files (the time of the file is not reliable); the hash is the proof. | one line, in the Info panel, the export and the report, better in a banner: "Data delivered 2026-11-20, 42 samples in 'QC_Reads', short code 7f3a9c12, from the file 'FastP.tsv'." The number of samples would have shown finding 1 at a glance. |
| 5. Fetching | A step outside the app that I run (a scheduled job, a pipeline step); the app reads a folder. No address and no token in the app. My step records the address, the date and the hash per file in the list of delivered files. | only the date matters |
| 6. Which file for which table | ONE rule: the file named in the deployment's file; else the file with the table's name in the data folder; the screen and the export say "read from: <file>". Danger met in the scratch run: the recipe's own path pointed into the repository, so sample data could be drawn instead of mine with no message. | "read from" shown |
| 7. Two copies, many visitors | The sentence I need: "Several copies may share one working place; tables are rebuilt, never half written." If the page writes no session record, nothing is shared between visitors. | nothing |
| 8. The temporary place | "I do not know the variable `TMPDIR`." A named place in the deployment file that the app applies. When it cannot be written, the export message must not blame a missing Quarto. | a truthful message |

## 3. The sentences wanted (proposals)
On the page, for a visitor:
- Data absent at start: "This page has no data yet. Its operator has been told. Please come back later."
- The working place cannot be written: "This page cannot start. Its operator has been told."
- A refresh with other columns: "The data of this page was updated on 2026-11-20, but the new file does not have the column 'total_reads' the analysis needs (the file has 'total_reads_RENAMED'). The page still shows the data of 2026-11-13. The operator has been told."
- A partial file: "A new data file for 'FastP' was delivered but is not complete (expected 42 samples, found 21). The page still shows the data of 2026-11-13."
- An open page, the data changed: "The data of this page was updated on 2026-11-20. Reload (F5) to see it." (it stays until the reload)
In the console, for the operator:
- "The working place /srv/app_work cannot be written (permission denied). The app cannot start. Make the folder writable for the user that runs the app, then restart. To run without keeping tables, set `on_unwritable: session_only` (every visit then takes 22 to 31 s)."
- Data absent: today's text, plus the exact file name and folder, plus "visitors see 'no data yet'".
- "FastP.tsv does not match the hash in the list of delivered files (expected 3a9..., found 8b1...). It is not shown. The last complete data (2026-11-13) stays."

## 4. Words not understood
anchor; "Tier 1 anchor ... valid (key match)"; stored tables; session record; Session Management panel; ghost save; `data_lookup`, `by_dataset_id`, `data_analysis_recipe_paths`; `user_data` for a page with no user; "opening" of a recipe; gate; refused; HOME; `original_name`; `input_fields`; `TMPDIR`; Quarto; `pipeline-static`.

## 5. The configuration text it could write itself (every key is a proposal)
(a) The weekly page:
```yaml
deployment_type: static
default_data_analysis_recipe: qc_weekly
locations:
  app_work: { path: /srv/qc/work, access: read_write }
  raw_data: { path: /srv/qc/incoming, access: read_only }
  recipes:  { path: /srv/qc/recipes, access: read_only }
data_delivery:
  list_of_delivered_files: delivered.yaml   # written last by my weekly job
```
It prepares: three folders; a weekly job that writes to a temporary name, renames, then writes `delivered.yaml` (date, hash). Checked at start: the folders exist, the working place can be written, the list matches the files.
(b) A pipeline run:
```yaml
deployment_type: galaxy
locations:
  app_work: { path: ${JOB_TMP}/work, access: read_write }
  raw_data: { path: ${JOB_DIR}/inputs, access: read_only }
```
"Only if I am told the variable names of my pipeline."
(c) Several data files:
```yaml
data_files:
  FastP: { path: /srv/qc/incoming/FastP.tsv, sha256: any }
  Quast: { path: /srv/qc/incoming/Quast.tsv, sha256: any }
```
If fetching is meant, the address goes in the same entry and its own step downloads; the token comes from a variable, never from the file.
It could NOT write: the list of access words and their meaning; how a refresh is checked (what "any" means, what a wrong hash does); the variable names of a pipeline; the choice for "nothing writable"; whether two copies may share the working place.

## 6. To decide first (ranked by this viewpoint)
1. What the app does with a partial or damaged file: never a plot from half the samples without telling the visitor.
2. Whether the page shows the date, a short hash and the number of samples of the data.
3. Whether a static page writes a session record at all.
4. The default among the three behaviours for "nothing writable", and whether the deployer may choose another in the file, with the consequence written beside the key.
5. One rule for which file feeds which table, shown on screen.
6. A plain page for the visitor for "cannot start" and "no data yet": no white or grey page.

## 7. Not verified
The code was not read by it. Not run (per the run facts): a container, the Galaxy variables, the IRIDA fetch, a file that disappears after start, a cut exactly at the end of a line, the times on a quiet machine. None of the proposed keys exists.
