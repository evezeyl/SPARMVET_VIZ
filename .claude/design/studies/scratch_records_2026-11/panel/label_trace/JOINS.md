# How joins work in the app, key by key (asked in the review session's message M301, point 2)

Digest by the coordinator of a scout's survey, 2026-11-18, 12:55 by the clock. The scout READ the code on `dev`; it ran nothing.
Each line below is "read" (seen in the code at the place named) unless it says REASONED (inferred from the code) or TO RUN (a reviewer confirms it in the app). Nothing is decided or changed here.

## The example: the join `FastP_with_metadata` of the demo recipe

Written in `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, lines 162 to 168:

```yaml
FastP_with_metadata:
  label: "FastP with metadata"
  description: "One row per sample: the FastP read-quality values with the sample's source, year and country; a left join on the sample id, so every FastP sample stays."
  ingredients:
  - dataset_id: FastP
  - dataset_id: metadata_schema
  steps: !include '1_test_data_ST22_dummy/wrangling/FastP_Metadata_wrangling.yaml'
```

Its steps file has one step: a left join with `metadata_schema` on `sample_id`.

## Where the joins are done, in plain words

- In the recipe, a join is a block under `joins:`. It names its tables (`ingredients`) and its steps. Tier 1 holds the join steps. Tier 2 holds further steps on the joined table.
- In the app, a join is computed when something asks for it by its ID: a plot (through its `target_dataset`), Blueprint, or the export.
- The app first loads every table of the recipe. Then it takes the FIRST table of `ingredients` as the starting table and runs the tier-1 steps in order. Each join step names its other table with `right_ingredient`.
- The result is stored as a file named after the join's id (`<join id>.parquet`). The tier-2 result is stored as `<join id>__T2.parquet`. Both are recomputed only when the recipe, the data or the engine changed.
- Tier-2 steps run on the stored joined table. They do not join again.

## What each key of a join block is used for

| Key | The checker | The engine (changes the table) | Shown to the user | If it is wrong |
|---|---|---|---|---|
| the join's ID (the name before the colon) | must be unique | names the stored files; plots point at it | YES: Pipeline Audit "Collection: <id>", Blueprint's list "<id> - join", the tube map node, export file names | a plot that names a missing id gets an error listing the known ids |
| `label` | required | NO | NO, nowhere found. Every screen shows the id instead | missing: the checker refuses; a wrong text changes nothing on screen |
| `description` | asked for (a suggestion) | NO | NO, nowhere found | nothing on screen. The text is not compared with the join steps (a description may say "left join" while the step says inner) |
| `comment` | must be text | NO | NO | nothing |
| `labels` (display names of columns; two joins of the demo recipe have it) | must be text to text | NO | NO reader found anywhere | the display names written there are not used |
| `ingredients` | required; each must be a known table; no duplicates | YES: which tables, and their ORDER. The first is the starting table | Blueprint's tube map draws its arrows from it | another order gives another starting table and other rows |
| `steps`, tier 1 | required | YES: the rows of the joined table | NOT listed in the Pipeline Audit panel (it lists tier 2 only) | wrong rows |
| `steps`, tier 2 | optional | YES: the rows of the Result view | the violet "[Tier 2]" lines of the Pipeline Audit; the note "T2=T1" when there is none | wrong rows in Result |

A plot's `target_dataset` may name a join or a single table. The screen shows the plot's own label, never the join's.

## So, for her question "is the join label a UI label?"

Today the join's `label`, `description` and `labels` are written for the person who reads the recipe file. No screen and no report shows them. The app shows the join's ID wherever it names a join. Whether they SHOULD be shown (then `ui_label` fits), or stay reader-only (then another word fits better), is her choice after the screenshots.
One side effect to know (REASONED, to run): these reader-only texts are part of what the app uses to decide whether a stored table is still valid. Changing only a join's label would make the app recompute that join, with identical rows.

## Mismatches found between what the recipe says and what the engine does

1. **The protection of join keys is probably OFF (REASONED; TO RUN first).** The function that lists the join keys to protect in the audit (`app/modules/session_manager.py:119-149`) expects a join's steps as a list. In the recipe they are a mapping (tier 1, tier 2). So it would find no key for any join, and the block "Cannot drop join key column(s)" (`filter_and_audit_handlers.py:741-745`) would never fire. If the run confirms it, this is a defect that touches the science: a user could drop a join key through the audit.
2. An ingredient that no step uses is not noticed. It is loaded, joined to nothing, and no message says so. If its file cannot be read, the whole join fails.
3. The first ingredient is the starting table by position only. Nothing states or checks which table the author meant as the start.
4. The checker refuses an ingredient written as a bare name; the engine and Blueprint would accept it.
5. `labels` is type-checked but read by nothing.
6. A stale comment in the demo recipe (line 160) speaks of `final_contract`, which was removed from the format.
7. Blueprint reads a plot key `join_id` that the checker refuses (`blueprint_mapper.py:447`).
8. A join step written in a join's tier 2 is not refused by the checker; at run time it would fail with an unclear message (REASONED).
9. The caution for a table joined with itself is computed and printed to the console, not shown on screen. There is no warning for a join that multiplies rows, unless the recipe writes `validate`. The demo recipe has a join made to show this (`QA_fanout_exhibit`).

## For the browser run (the reviewer confirms each line and takes the screenshot)

1. HOME, the plot tabs: the plot labels; the join is not named.
2. HOME, "Data to show" and the "Viewing: ..." badge on a plot whose join has no tier 2: the note "T2=T1".
3. HOME, the data preview header on a join plot: join id, join label, or nothing?
4. HOME, Pipeline Audit: "Collection: <join id>"; violet tier-2 lines only; the join's own join step is not listed.
5. HOME, try to drop the column `sample_id` through the audit on a join plot: is it blocked with "Cannot drop join key column(s)"? (Expected from the code: NOT blocked.)
6. HOME, the plot of `QA_fanout_exhibit`: any warning about multiplied rows? (Expected: none.)
7. Blueprint, the join list: "<id> - join", not the label.
8. Blueprint, tube map: the node shows the id; six arrows into `ST22_Anchor`.
9. Blueprint, lineage rail: ids only.
10. Export: files `<join id>_T1.tsv` and `_T2.tsv`; the report names the join by id.
11. On a copy: change only a join's label and reopen: is the join recomputed, and are the rows identical?
12. On a copy: add an ingredient that no step uses: any message?
