Written by Opus for D-0586
Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md` (dev 4bd5f2b6). Each anchor below occurs exactly once (checked by fixed-string search). Her words are copied from the channel block M645.

## BLOCK 1. REPLACE `**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).` BY the lines up to END BLOCK 1:
### Added 2026-11-23 (ledger D-0586): recipes do not start from the metadata; the marker column is kept; missing values are treated before a filter; equal id sets as a goal

**Her words, exact.** "A - we agreed that recipes should not start from the metadata - which means that the recipes it appears have to be changed - it means 1. fix the ids missing in both original and metadata 2. original data -> joinleft on metadata - when there is the need for a metadata join - exactly - we need to look at those made from the metadata alone - it is test recipes I think - not mine - so maybe they need to be differently - do they only hold metadata ? - yes flag column kept - can be removed eg. last step for the plots if really  necessary ... after having treated the missing values correctly (depending on the purpose - sorry this is context dependent ) - breaking step - because the treatmenet of the missing data must be defined before the filter likely - is it NA is it 0 ... if treated correctly I hope it will solve this. Also a reason to have recipes where the sets of metadata and original data are equal. Important. A : required meaning." [HER WORDS D-0586]

**Decided in her words.**
- **Question A:** a required meaning for "not in metadata" ("A : required meaning").
- **Recipes should not start from the metadata.** The order: "1. fix the ids missing in both original and metadata"; "2. original data -> joinleft on metadata - when there is the need for a metadata join".
- **The marker column is kept** ("yes flag column kept"). It "can be removed eg. last step for the plots if really  necessary", only "after having treated the missing values correctly"; the treatment is "context dependent".
- **The treatment of the missing data comes before a filter:** "the treatmenet of the missing data must be defined before the filter likely - is it NA is it 0".
- **Equal sets of ids of the metadata and of the original data:** "a reason to have recipes where the sets of metadata and original data are equal. Important."
- **Readings, not her words:** the four demo joins that start from the metadata (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`) are rewritten with the data table first in the one dry run (D-0525; listed only). Her "we agreed" refers to D-0564. Her "breaking step" is read as "the step that removes rows".

**Her question "do they only hold metadata ?": the two tables made from the metadata alone.**
- **Yes.** Each has one ingredient, `metadata_schema` [RECIPE FILE `1_test_data_ST22_dummy.yaml:265-270, 289-295`].
  - `QA_year_types` adds a column `year_label` (the year as text) [RECIPE FILE `wrangling/QA_year_types.yaml`].
  - `QA_aggregated_no_key` adds the same column, then counts `sample_id` per `country` and `year_label` in tier 2 [RECIPE FILE `QA_aggregated_no_key_tier1.yaml`, `_tier2.yaml`].
  - Both are called "QA canary" in their descriptions.
- **The plots that read them** are in the group "QA canaries (not for publication): each plot isolates one failure mode" [RECIPE FILE `1_test_data_ST22_dummy.yaml:337-348`]:
  - `qa_year_label`: the year label has no ".0" and the numeric year stays numeric;
  - `qa_facet_by_mapping`: `facet_by` written in `mapping` must give 3 panels (issue 65);
  - `qa_aggregated_no_key`: an aggregate with no `sample_id`, so a removal by id cannot change it (issue 60).
- **They join nothing,** so "a recipe does not start a join from the metadata" does not touch them, unless she means "no table is made from the metadata at all". An added "not in metadata" line would appear in them: an empty year or country, counted in `qa_aggregated_no_key`.
- **Options (hers), with what she would see:**
  - (a) Leave them as test tables of the QA canaries: the same three plots, made from the metadata.
  - (b) Rebuild the same canaries from a data table joined with the metadata, data first: the same three plots, made the way her rule writes recipes.
  - (c) Remove them: the QA canaries group loses these three plots, and the failure modes they guard are no longer shown.
  - Lean (Opus, as a lean): (b): the shipped demo then shows only the form her rule asks for, and the canaries keep testing what they test.
  - Neither: say what you meant.

**The goal "equal id sets", in the data check.**
- [TODAY] The data check builds each table alone and compares no ids [CODE READ `app/modules/data_analysis_recipe_validator.py:485`; ESTABLISHED: OVERLAP section 2].
- [TO BUILD] One line per result table, words PROVISIONAL: "In <table>: the same ids as the metadata." or "In <table>: N ids are in the metadata only, M in this file only."
- It is shown with the other notes on the ids: the red warning where there is a panel, Data Import after an upload, BLUEPRINT's Validate, the log of the ids and the export.
- On the demo: every result table except ResFinder reads "the same ids"; ResFinder reads "4 in the metadata only, 0 in this file only" [ESTABLISHED: OVERLAP section 1].

**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).
END BLOCK 1

## BLOCK 2. INSERT AFTER the line that begins `4. **A question for her: does the recipe need a stated meaning for "not in metadata"`
`   > **Answered by D-0586 (2026-11-23):** "A : required meaning".`

## BLOCK 3. INSERT AFTER the line that begins `   - **Flag (a result can change with no word in the table):**`
`   > **Answered by D-0586:** "yes flag column kept"; it may be removed as a last step for the plots only after the missing values are treated. Dry-run candidates, listed only: the tables whose tier 1 ends with a fixed column list (`polars_select`) and must keep the marker columns: the data tables `MLST` and `VirulenceFinder`, and the joins `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_ST_with_NA` and `QA_L50_integer` [RECIPE FILE: `polars_select` in their tier-1 files].`

## BLOCK 4. INSERT AFTER the line that begins `**Question 12. The join order: a rule, an advice, or documentation?**`
`> **Changed by D-0586:** the direction is decided in her words ("recipes should not start from the metadata"). How it is enforced (refused by the check, an advice, or documentation) is NOT stated: still hers.`

## BLOCK 5. INSERT AFTER the line that begins `**Question 7. When in the table: before or after the recipe's own tier-1 steps?**`
`> **Added by D-0586:** her sentence "the treatmenet of the missing data must be defined before the filter likely - is it NA is it 0" supports the completion before the recipe's own tier-1 steps: the marked lines exist when the recipe states their treatment, before any filter can remove an entity (on the demo, the 6 entities of `Detailed_summary`). "likely" leaves the question open: still hers.`

## BLOCK 6. INSERT AFTER the line that begins `- It can never be matched. With your purpose (data first, metadata second, `left`) it adds no row`
`- What her rule of D-0586 changes: with no table that starts a join from the metadata, such a line adds no row anywhere, except in the two tables made from the metadata alone (`QA_year_types`, `QA_aggregated_no_key`), where it is one more entity with no id.`
