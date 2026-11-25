Written by Opus for D-0587
Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md` (dev e926c4e2). Each anchor occurs exactly once (fixed-string search). Her words are copied from the channel block M647.

## BLOCK 1. REPLACE `**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).` BY the lines up to END BLOCK 1:
### Added 2026-11-23 (ledger D-0587): where the "not in metadata" line is added; the two metadata-only tables

**Her words, exact.** "QA_year_types and QA_aggregated_no_key - so they old only metadata - but in the previous chat it said " They cannot be written that way, so they always hold an added line." why - there is no original data - all is metadata so all the ids are considered complete no  ? why should they always hold an added line ? They break no rule to my opinion - the line with "not in metadata" can only be done in an id is missing from the medata and is found in an original table - here there is no original table. Cost for the demo recipe - then the fixed column list will need to be increased by the column that keeps the markers - or the missing data processed before and T1 and the column that keeps the markers explicitely dropped. The goal "equal id sets" is also planned - yes. Question: what to do with the two metadata-only tables? a) this gives us an edge case - is the metadata registred under metadata schema or under dataschema ?" [HER WORDS D-0587]

**What her words say.**
- The two tables break no rule. Her answer for them is a), leave them.
- A "not in metadata" line needs an id that is missing from the metadata AND found in an original table.
- **The cost for the demo:** where a join ends with a fixed column list, either the list gains the marker column, or "the missing data processed before and T1 and the column that keeps the markers explicitely dropped".
- The goal "equal id sets" is planned ("yes").

**Our sentence corrected.** "they always hold an added line" was wrong. A table made from the metadata alone holds a "not in metadata" line ONLY IF the line is added to the metadata table itself (placement (i) below) AND some result file of the recipe has an id outside the metadata. On the demo neither happens (0 ids outside the metadata [ESTABLISHED: OVERLAP section 1]). Under (ii) they never hold one.

**Open, hers: WHERE is the "not in metadata" line added?**
- **(i) In the metadata table itself, for the whole recipe,** whenever some result file has an id outside it.
  - Every table that reads the metadata inherits the line, the two metadata-only tables included.
  - The metadata table's key then depends on every result file (a stored table's key holds the content of the files it reads [CODE READ `app/modules/cache_keys.py:14-20`]): a change in any data file rebuilds the metadata and everything below it.
  - The graph gains an edge from every result file into the metadata's first place. The places themselves stay as they are (under D-0553 the first places remain separate).
  - The Source view still shows the file; the metadata's T1 shows the added lines, marked. Static deployment: automatic, written in the log. "Equal id sets": every table then carries the union of the ids.
  - The format needs a block on `metadata_schema` (or one for the whole recipe), and the app builds the metadata after reading every result file.
- **(ii) Only where a data table meets the metadata.** With the data first, a left join already keeps the data row, with empty metadata values. The marker means "the metadata had no line for this id" and is computed at the join.
  - The metadata table, its key, its Source view and its T1 stay exactly the metadata; there is no new edge.
  - The two metadata-only tables are untouched (her reading).
  - It can be written TODAY by the author, in visible steps: `in_metadata: pl.lit(True)` in the metadata's tier 1, then a fill of the empty values after the join. Or the join step (or the app) writes the marker: a new join option.
  - Static deployment and the log: the data check's note lists the ids, as decided; nothing is added to a table. "Equal id sets": the joined tables hold every data id; the metadata holds its own ids.
  - **Reopens (information):** her "yes" of D-0585 was to "a line of the metadata table"; (ii) moves the marker to the join.
- **A join of TWO data tables, then the metadata** (data first): under (i) each row finds a metadata line or an added, marked line; under (ii) a row whose id is not in the metadata gets empty metadata values and the marker from that join.
- **What she would see on `left_join_lesson`** (2 ids, `ACC0001` and `ACC0002`, of `sequenced` are in no metadata of 10 ids [ESTABLISHED: OVERLAP section 1]):
  - (i): the metadata table has 12 lines, 2 of them marked, in every table that reads it;
  - (ii): the metadata keeps its 10 lines, and the join `sequenced` + metadata shows the 2 rows with empty metadata values and the marker.
  - On the demo: nothing either way.
- Lean (Opus, as a lean): (ii): it is her reading of the metadata-only tables; the metadata stays one file's content, with no dependency on every data file and no new edge; and it can be written today with visible steps. [Sonnet lean]
- Neither: say what you meant.

**Her question: "is the metadata registred under metadata schema or under dataschema ?"**
- **Under its own top-level key `metadata_schema`** [RECIPE FILE `1_test_data_ST22_dummy.yaml:149`], apart from `data_schemas` (line 16) and `additional_datasets_schemas` (line 122).
- `metadata_schema` is a reserved schema id [CODE READ `libs/utils/src/utils/recipe_spec.yaml:80`], and the block is optional [`recipe_spec.yaml:24`]. The completion rule would name it by that id.
- **The edge case she means:** a recipe whose metadata is a data schema (`figshare_integration`). The checks cannot know which table is the metadata unless the recipe names it (the `metadata_schema` block, or `entity.population`): still hers (question 13).

**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).
END BLOCK 1

## BLOCK 2. INSERT AFTER the line that begins `2. **With her purpose, the 4 joins with a data table would be written data first, metadata second, `left`.**`
`   > **Corrected by D-0587:** "so they always hold an added line" is wrong. A metadata-only table holds a "not in metadata" line only if the line is added to the metadata table itself (placement (i), open) and a result file has an id outside the metadata. Her words: "here there is no original table".`

## BLOCK 3. INSERT AFTER the line that begins `- **They join nothing,** so "a recipe does not start a join from the metadata" does not touch them`
`  > **Corrected by D-0587:** "would appear in them" holds only under placement (i) and only when a result file has an id outside the metadata; under (ii) they are untouched.`

## BLOCK 4. INSERT AFTER the line that begins `  - Lean (Sonnet, as a lean): (a): these tables join nothing`
`  > **Answered by D-0587:** a), leave them: "They break no rule to my opinion". The sentence of this lean about an added line entering them holds only under placement (i) (see the D-0587 sub-section).`

## BLOCK 5. INSERT AFTER the line that begins `   > **Answered by D-0586:** "yes flag column kept"`
`   > **Her cost note, D-0587:** "then the fixed column list will need to be increased by the column that keeps the markers - or the missing data processed before and T1 and the column that keeps the markers explicitely dropped." Both ways are recipe-side; they go in the dry run (D-0525), listed only.`

## BLOCK 6. INSERT AFTER the line that begins `- What her rule of D-0586 changes: with no table that starts a join from the metadata`
`- What placement (i) or (ii) changes for it: nothing. A metadata line with no usable id is in the metadata table either way; neither placement adds or removes it.`
