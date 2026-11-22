Copied on 2026-11-22 from the panel's scratch folder (D-0419). Answers of the agent in charge of the recipe proposal to the whole-picture agent (D-0526). Not confirmed by the owner.

# The audit dialog walk-through, redone with her default of D-0508 (answer to question 1)

Written 2026-11-22 by the agent in charge of the recipe design proposal, for the whole-picture agent (order D-0526). A study: nothing is built, no recipe or file of the app is changed. NOT confirmed by the owner: the form 3 (D-0496), the two readings of "the earliest place" (D-0509: "NOT decided: which place is the earliest").

Labels: **run** = I ran it with the real engine (`q1_walkthrough.py`, `q1b_where_written.py`, outputs in `out/`); **read** = read at file:line; **reasoned** = my reasoning, not run.

## 0. What was run, and the limit of the run

- Form 3 does not exist in the engine, the check or the audit copy (proved in `q_checks.py`, see ANSWERS.md, question 7). So the data of a derived table is produced by the route the proposal's Part 6 proved equal to plain Polars: the derived table's steps written as the tier 3 of a probe plot on the table it is made from (**run**).
- The audit step is written as an author step at the place, as the proposal's `audit_walk.py` does (the audit file form is not read from a file yet). The data effect is the same as the audit copy's `audit_steps` (**reasoned**, the same engine order: `steps` then `audit_steps`, `recipe_tiers.step_list`).
- The step is the one "remove from all the data" writes: `modif_filter`, `column: <entity key>`, `op: not_in`, `value: [<entity>]`, `na: keep` (read, `libs/utils/src/utils/remove_from_all.py` header, point 4).
- The slice is the proposal's (Part 2.2): the source tables `MLST` and `metadata_schema`, the join `MLST_with_metadata` (tier 1: the left join on the entity key; tier 2: an `era` column and the years 2023 to 2025), the derived table B `MLST_samples_per_country_year` (tier 1: `year_label`, one row per entity; tier 2: the count per country and year), the plot result `mlst_bar` and the two results of B (a plot and a table).
- **An extension that is NOT in the proposal's slice, added by me** so that a derived table is reached through a second join with the metadata: the proposal's own reads summary (Part 2.6): the source table `FastP`, the join `FastP_with_metadata` (left join on the entity key, no tier 2), the derived table R `FastP_reads_summary` (tier 1: `year_label`; tier 2: the count and the means per country and year) and its table result `reads_summary`. Without it the two readings give the same data on the slice (the join has the results table first), and the difference that D-0508 is about does not show.
- Data: the demo files `assets/test_data/1_test_data_ST22_dummy/`. The entity removed: the sample `97991777` (Norway, 2024). It is in `MLST`, in `metadata_schema` and in `FastP` (each of the three tables has 42 rows after its tier 1, and the entity is on one of them). In every general sentence below it is "the entity"; "sample" and the number are only the demo's example (D-0512).

## 1. The two readings

- **Reading A:** the earliest place is tier 1 of each original table. In the lineage of the open result: `MLST` and `metadata_schema`.
- **Reading B:** the earliest place is the end of tier 1 of each table that joins the metadata. In the slice: `MLST_with_metadata` and `FastP_with_metadata`.
- Variants I also ran, to answer the limits that the whole-picture study names (part 6.1): **A+** = A and also the other original table that meets the metadata (`FastP`); **B'** = B restricted to the lineage of the open result (`MLST_with_metadata` only). Whether `FastP` or `FastP_with_metadata` belongs to the lineage of `mlst_bar` is not decided (WHOLE_PICTURE 6.1, "Limits"; D-0451: "basic lineage is up to it can only go backwards when on its way up or forward when on its way backwards").

## 2. What the dialog lists

The same lines whichever result the user starts from (the walk goes back to the sources and forward to everything that depends on them, D-0347). Only distinct tables are lines (D-0346). The entity column must exist at a place for it to be a line (**run**: the columns of each place are in `out/q1_walkthrough.out`).

| Line | Where the entity column exists (run) | Reach (tables, results) | Reading A | A+ | Reading B | B' |
|---|---|---|---|---|---|---|
| `MLST`, end of tier 1 | yes | join, derived B; `mlst_bar`, B plot, B table (3 results) | **ticked** | **ticked** | offered | offered |
| `metadata_schema`, tier 1 (no steps) | yes | both joins, both derived tables; 4 results | **ticked** | **ticked** | offered | offered |
| `FastP`, end of tier 1 | yes | `FastP_with_metadata`, derived R; `reads_summary` (1 result) | offered (in the lineage or not: not decided) | **ticked** | offered | offered |
| `MLST_with_metadata`, end of tier 1 (after the join with the metadata) | yes | derived B; 3 results | offered | offered | **ticked** | **ticked** |
| `MLST_with_metadata`, end of tier 2 (has steps: a distinct place) | yes | derived B; 3 results | offered | offered | offered | offered |
| `FastP_with_metadata`, end of tier 1 (no tier 2: one place) | yes | derived R; `reads_summary` (1 result) | offered | offered | **ticked** | offered |
| derived B `MLST_samples_per_country_year`, end of tier 1 (has a step: a distinct place) | yes | the 2 results of B (plot and table) | offered | offered | offered | offered |
| derived B, end of tier 2 | **NO: one row per country and year** | no line; a "gone here" note (the walk's `Gone`, P5) | | | | |
| derived R `FastP_reads_summary`, end of tier 1 | yes | `reads_summary` | offered | offered | offered | offered |
| derived R, end of tier 2 | **NO** | no line | | | | |
| "this result only": `mlst_bar` | yes (its table has the column) | 1 result | offered | offered | offered | offered |
| "this result only": B plot, B table, `reads_summary` | **NO: the column is gone at their table** | no line | | | | |

"Offered" means a line of the dialog that starts unticked under D-0508. Whether the later places are lines with a tick box or only a drawing under the ticked line is question 3 of the whole-picture design (not decided). The table is the same under both answers to question 3: it only changes how an offered line is drawn.

**Where the derived tables and the results appear:**
- A derived table is one line (its tier 1, where it has steps) and never a ticked one for the entity key, under A, A+, B or B'. Its tier 2 is no line: the entity column is gone there (**run**, columns).
- The two results of a derived table (a plot and a table) are not lines of their own: they appear in the "results that change" list of each line that reaches them, and they have no "this result only" line, because the entity key does not exist at their table. A user who looks at the 6-row table result and wants to remove an entity cannot start there: she must view an earlier stage (the derived table's T1, 33 rows, where the column exists). This is a case of D-0518 ("how to make it navigate"); the dialog can start from a table that has the column, not from the result.
- `mlst_bar` appears both in the reach of the lines and as "this result only".

**Is a derived table ever "the earliest place"?**
- For a removal by the entity key: no, under both readings. A derived table is not an original table (A) and it is not a table that joins the metadata (B): it holds no join step (ANSWERS.md, question 2: join actions are tier 1 of a join only, today `recipe_check.py:714`, `action_names.py:66`) and it is made from a table that already carries the metadata (D-0511). The entity key comes from the tables above it (**run**: the derived tables' tier 1 columns include it, because they inherit it).
- For a column that the derived table makes itself (here `year_label`, created in the tier 1 of derived B and derived R and absent from every table above, **run**): the earliest place where the column exists IS the derived table's tier 1. Neither reading A nor B says what is ticked for such a column ("the earliest place of each branch - which is the original data basically", D-0501, is about original data). NOT decided. The nearest open question of the whole-picture design is question 5 (a place where the key is made again).

## 3. What changes under each tick (run)

Entity: one. "Rows with the entity" is the pair D-0508 leaves open ("rows with this sample: before, after"); here for each place of the lineage.

| Place | Base | A (2 lines) | A+ (3) | B (2 lines) | B' (1 line) |
|---|---|---|---|---|---|
| `MLST` end of tier 1 | 42 rows, 1 with the entity | 41, 0 (**ticked**: 1 removed here) | 41, 0 (ticked) | 42, 1 | 42, 1 |
| `metadata_schema` tier 1 | 42, 1 | 41, 0 (**ticked**) | 41, 0 (ticked) | 42, 1 | 42, 1 |
| `FastP` end of tier 1 | 42, 1 | 42, 1 | 41, 0 (ticked) | 42, 1 | 42, 1 |
| `MLST_with_metadata` end of tier 1 | 42, 1 | 41, 0 | 41, 0 | 41, 0 (**ticked**: 1 removed here) | 41, 0 (ticked) |
| `MLST_with_metadata` end of tier 2 | 33, 1 | 32, 0 | 32, 0 | 32, 0 | 32, 0 |
| `FastP_with_metadata` end of tier 1 | 42, 1 | **42, 1** (the row stays, its metadata columns empty) | 41, 0 | 41, 0 (**ticked**) | 42, 1 |
| derived B end of tier 1 | 33, 1 | 32, 0 | 32, 0 | 32, 0 | 32, 0 |
| `mlst_bar` (result) | 33, 1 | 32, 0 | 32, 0 | 32, 0 | 32, 0 |
| derived R end of tier 1 | 42, 1 | **42, 1** | 41, 0 | 41, 0 | 42, 1 |

The three aggregated results have no entity column: the comparison that D-0477 chose (option B, "before and after comparison of the tables") is what can be shown for them. Run:

| Result (rows, entities counted) | Base | A | A+ | B | B' |
|---|---|---|---|---|---|
| `mlst_bar` | 33 rows | 32 | 32 | 32 | 32 |
| B: samples per country and year (plot and table, 6 rows) | total 33; Norway 2024: 19 | total 32; Norway 2024: 18 | 32; 18 | 32; 18 | 32; 18 |
| `reads_summary` (R) | 9 rows; total 42; Norway 2024: 19 | **10 rows; total 42**: a new group with an EMPTY country and an empty year, holding the entity; Norway 2024: 18 | 9 rows; total 41; Norway 2024: 18 | 9; total 41; 18 | 9; total 42; 19 (unchanged) |
| Results that change | | `mlst_bar`, B, `reads_summary` | the same three | the same three | `mlst_bar`, B only |

- **Under A the reads summary changes in a way that nobody ticked it for**: the entity leaves the metadata (ticked) but not `FastP`; the left join `FastP_with_metadata` keeps the row, with an empty country and year; the derived table counts it in its own empty group (10 rows, total still 42). The entity is "removed" and still counted in a result. This is the left-join effect of the whole-picture part 6.1, now seen through a derived table. The note that D-0477 chose for this case (the left join keeps the rows of the first table, check the table that holds the results) is what the dialog has to say on the line `metadata_schema` (**reasoned**: the words are not decided).
- **Under B** the entity leaves with its metadata: both joins are ticked, nothing is left with empty metadata, and the reads summary loses the entity (total 41).
- **Under B'** the removal reaches only the lineage of the open result: `mlst_bar` and B change, and the reads summary keeps the entity WITH its metadata (the case D-0499 describes: "keep it in the quality results only").
- **A+** is the same as B on these three results.
- The proposal's own three places (the earlier Part 3, run again here): (i) this result only, `mlst_bar`: only `mlst_bar` changes; (ii) end of tier 2 of the shared join: `mlst_bar` and B change; (iii) derived B end of tier 1: only B changes (`mlst_bar` keeps 33 rows). The numbers equal the proposal's `try/out/audit_walk.out` (33 to 32 rows; Norway 2024: 19 to 18).

## 4. What is written into the audit recipe, and at which block

The audit recipe holds each step in the list `audit_steps` of the tier it is written at (D-0332: the author's `steps` are never touched). Run with the library's real audit copy on today's form of the slice (`out/q1b_where_written.out`):

| Choice | Written at (block, tier, list) | Run |
|---|---|---|
| Reading A | `data_schemas.MLST.tier1.audit_steps` and `metadata_schema.tier1.audit_steps` (two steps with the same operation, ids `audit_<id>_1` and `audit_<id>_2`) | place names `T1:MLST`, `T1:metadata_schema`: yes |
| A+ | the two above and `data_schemas.FastP.tier1.audit_steps` | same function: reasoned from A |
| Reading B | `joins.MLST_with_metadata.tier1.audit_steps` and `joins.FastP_with_metadata.tier1.audit_steps` | `T1:MLST_with_metadata`, `T1:FastP_with_metadata`: yes |
| End of tier 2 of the shared join (ii) | `joins.MLST_with_metadata.tier2.audit_steps` | yes |
| This result only (i) | `analysis_groups.Results.plots.mlst_bar.tier3.audit_steps` today; under form 3 `analysis_groups.Results.results.mlst_bar.tier3.audit_steps` | today: yes (`T3:mlst_bar`); form 3: NOT possible yet (the list `results` is not read: ANSWERS.md question 7) |
| Derived B end of tier 1 (iii) | `derived_tables.MLST_samples_per_country_year.tier1.audit_steps` | NOT possible yet: the audit copy knows no derived table (ANSWERS.md question 7) |

For a derived table the step in tier 1 sits after the derived table's own `year_label` step only if the user ticks the line "end of tier 1"; the engine runs `steps` then `audit_steps` of that tier. It cannot be written at the derived table's tier 2: the entity key is gone there.

The record in the audit recipe shows the same operation once per ticked line: two identical steps under A, two under B (D-0508 / D-0509: the audit recipe "shows the same step 13 times" on the whole demo, WHOLE_PICTURE question 1).

## 5. What this walk-through changes for the owner's choice (information, nothing chosen)

- The default tick rule (question 1 of the whole-picture design) is not changed by derived tables: they are never ticked for the entity key, either reading.
- A derived table makes the left-join effect easier to see, not harder: a table result (the reads summary) shows a new empty group under reading A. It adds one more result to the list of results that change.
- The dialog must say, on the line where a result starts, whether the entity column exists at that result; for a table result of an aggregate it does not (the user starts from the derived table's T1 or from another result).
- For a column the derived table makes, the earliest-place rule is not defined (question to put to her if she wants derived tables).
