# Every name and description of the demo recipe: where you write it, who reads it, what the user sees (asked in M300 and M301)

Digest by the coordinator of a scout's trace, 2026-11-18, 13:05 by the clock. The scout READ the recipe and the code; it ran nothing.
"Read" = seen in the code at the place named. REASONED = inferred. TO RUN = the browser run confirms it (pictures will be in this folder, index page `INDEX.md`).
Recipe: `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` and the files it includes. Joins have their own page: `JOINS.md`.
Nothing is renamed or decided here.

## In one page: you write it here, the app shows it there

| What you write | Where (lines of the main file unless said) | How many | Where the app shows it | If it is missing, the app shows |
|---|---|---|---|---|
| The recipe's name: `info.label` ("ST22 Dummy Dataset") | 6 | 1 | The title at the top of HOME (the banner). Also a line "label: ..." in the Info panel | no banner |
| `info.subtitle` | 8 | 1 | The line under the banner; the Info panel | nothing |
| `info.contact` | 7 | 1 | The Info panel; the export README; the export's run record; the notice when a recipe is refused | the contact of the deployment |
| `info.description`, `info.version` | 10-12 | 1 each | The Info panel; Blueprint's info form | "-" in Blueprint |
| `info.category` | 9 | 1 | The Info panel only. The checker does not know this key and says nothing | nothing |
| A GROUP's `label` ("Quality Control", "Cat", ...) | 302, 317, 326, 356, 366 | 5 | The group tab in HOME; Blueprint's group cards | the group's description, then the group's id |
| A group's `description` | 303 ... | 5 | Only when the label is missing | - |
| A PLOT's `label` ("QC Reads Horizontal Barplot", ...) | 306 ... 405 | 17 | The plot tab in HOME; the "Apply to" list of the audit dialog; Blueprint's plot rows; the lineage of a plot in the export | tab: the plot id in title case; dialog: the raw id |
| A plot's `description` | 308 ... | 17 | NOWHERE (the checker only suggests writing one) | - |
| A plot's `taxonomy` | 307 ... | 16 | NOWHERE for a pipeline recipe (the gallery of examples uses it) | - |
| The plot's `title:` in its plot file | first lines of 17 plot files | 17 | The title ON the picture; the heading and caption of that plot in the export report; the audit text of the report | report: the plot id in title case; no title on the picture |
| `labs` subtitle, x, y in a plot file | 8 and 10 plot files | - | On the picture (subtitle, axis titles), as typed by hand | the column names |
| A TABLE's `label` (raw tables, the two additional tables, the metadata table) | 18 ... 109; 124, 135; 150 | 9 + 2 + 1 | NOWHERE. The tube map and the lineage show the table's ID | (the id is shown already) |
| A table's `description` | 19 ... | 12 | NOWHERE | - |
| A table's `comment` | 55, 137 | 2 | NOWHERE (only in the recipe file itself) | - |
| A JOIN's `label` and `description` | 163 ... 292 | 16 each | NOWHERE. Every screen shows the join's ID | (the id is shown already) |
| A join's `labels` (display names of columns) | 231, 242 | 2 lists | NOWHERE | the columns show their names |
| An INPUT COLUMN's `label` ("Sample ID", "Total Reads", ...) | the `input_fields` files | 70 of 74 columns | Blueprint's field cards (a line "label: ...") and the text given to the AI helper. NOT the data preview, NOT the column list, NOT the filter box, NOT the plot axes, NOT the export | Blueprint shows the column name |

The recipe selector of HOME shows the FILE name (`1_test_data_ST22_dummy`), not `info.label`. The export report is titled with the file name too.

## What this means for her words

- "data_schema ... labels are ui_label because its what is shown in the ui": today a table's label is shown in NO screen. The app shows the table's id. If she wants the label shown (in the tube map, the lineage, "Data to show"), that is a new behaviour to build; then `ui_label` fits. If not, the key is text for the reader of the recipe only.
- "the joins are also ui_labels": same finding. Shown nowhere today (details in `JOINS.md`).
- "column_label is fine - its what is seen when data is previewed": there is no key called `column_label` anywhere. The key she most likely means is the `label` of an input column. The data preview does NOT show it: the preview's headers are the column names (`sample_id`, not "Sample ID") (`home_theater.py:1403-1409`). TO RUN.
- A record that disagrees with her words, to settle with her: the format text (its decision "DEC22", recorded as decided on 2026-11-13) says "HOME table headers keep the column name", and also says that plot axis and legend titles default to the column's label. The first is what the code does. The second is NOT built: no code gives a plot the column labels; axis titles are the column names unless typed by hand in `labs`.

## Texts that nobody shows on screen (in this recipe)

Table labels (12), table descriptions (12), table comments (2), join labels (16), join descriptions (16), the two `labels` lists of joins, plot descriptions (17), plot taxonomy (16), group descriptions (5, shown only if the label is missing). The checker REQUIRES the label of a table and of a join although nothing shows it.
What the user would lose if they were removed: nothing on screen. What the recipe reader would lose: the explanation beside each table and join in the file.

## Other things found on the way

1. Blueprint's info form has a field "Name" that reads and saves `info.name`. The banner reads `info.label`. So a name typed in Blueprint does not change the banner (REASONED; TO RUN).
2. `ui_title` already exists as a key of the app features files (a text that replaces the banner title). The new recipe key `ui_title` (the longer name of a plot or group) would be the same word for another thing.
3. The audit stack's own "Apply to" choices show the plot id in title case, not the plot's label, while the filter dialog shows the label (TO RUN).
4. Four files in the recipe's folder are included by nothing: `plots/FastP_reads_boxplot.yaml`, `wrangling/PlasmidFinder_wrangling.yaml`, `wrangling/ResFinder_Abromics_wrangling.yaml`, `wrangling/Detailed_Summary_assembly_wrangling.yaml`.
5. Four columns of the `Summary` table have no label (`genotype`, `phenotype`, `cge_phenotype`, `plasmid`).

## On the branch of the big recipe change (state today, before its readers are done)

The rewrite renamed `label` to `ui_label` at groups and plots (decided, D-0253) and moved each plot's whole entry into its plot file. The app's screens on that branch still read the old words in about ten places (step 4 of the build, in work: 4a the engine path, then 4b HOME and Export, then 4c Blueprint). Until 4b is done, HOME on the branch would show the group's description as tab text and the plot id as plot tab, and may show no plot. This is known, it is the reason the branch is not merged, and the picture comparison and the browser tests guard it. The other label places (recipe name, tables, joins, input columns) are untouched on the branch and wait for her decision.

## The browser run (TO RUN: 32 checks; each gets "seen" or "not seen" and a picture)

HOME: the banner and its subtitle; the recipe selector (file name); the five group tabs; the 17 plot tabs; "Data to show"; the data preview title and its column headers (names or labels?); the column list; the filter box; the picture titles, subtitles and axis titles of four named plots; the "Apply to" lists of the filter dialog and of the audit stack; the Info panel. Blueprint: groups and plots lists; the info form (and whether saving a Name changes the banner); the tube map; the lineage rail; the field cards. Export: the report headings and captions; the README; the run record; the lineage file; the column names of the exported tables. Three tests on a copy: remove `info.label`; change one plot label; remove one plot title.
