Written by Opus for D-0588
Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md` (dev 5887fbff). The anchor occurs exactly once (fixed-string search). Her words are copied from the channel block M648.

## BLOCK 1. REPLACE `**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).` BY the lines up to END BLOCK 1:
### Added 2026-11-23 (ledger D-0588): her view: a table that holds the entity data itself is original data

**Her words, exact (her view, "I think", not a final decision).** "why would you join it to itself ? what is the usage here ? it seems to be a very edge case test ... A note I am not sure that haviing a metadata table schema is good when there is no other data - I think it should be registred as data schema - that would make more sense - the metadata is to add information that is maybe sensitivy - about the entities, here everything is already in one table. That is a good case for a guidelines in the documentation - I think if there is only "metadata" then it should go under the original_data - that will also help for the lineage and it does not makes sense to have metadata without metadata" [HER WORDS D-0588]
The review session's reading, not her words: "metadata without metadata" means "metadata without data".

**Her questions "why would you join it to itself ? what is the usage here ?"**
- **Not a self-join.** Each of the two QA tables is an entry of `joins:` with ONE ingredient, `metadata_schema`, and one step in tier 1 [RECIPE FILE `1_test_data_ST22_dummy.yaml:265-270, 289-295`].
- **`QA_year_types`** guards two things:
  - a year read as a number must be shown as "2024", not "2024.0", and stay a number for range filters (plot `qa_year_label`);
  - facets written in `mapping` must give 3 panels (plot `qa_facet_by_mapping`, issue 65) [RECIPE FILE: their descriptions].
- **`QA_aggregated_no_key`** guards the reach of the audit: its tier 2 counts the samples per country and year, so it holds no `sample_id`, and a removal by id cannot change it (plot `qa_aggregated_no_key`, issue 60) [RECIPE FILE `QA_aggregated_no_key_tier2.yaml`; the plot's description].
- **Do they need the metadata?** Only its columns: `year` and `country` (and `sample_id`, to count). In the demo only the metadata declares `year` and `country` [RECIPE FILE: of the demo's input-field files, only `metadata_schema_input_fields.yaml` has them]. So no data table of the demo could feed these canaries alone; rebuilt elsewhere, each would need a data table joined with the metadata, data first. Otherwise they stay on the metadata.

**Facts for her view (by reading).**
- **The format:** `data_schemas` is required and `metadata_schema` is optional [CODE READ `libs/utils/src/utils/recipe_spec.yaml:23-24`]. So a recipe with only data schemas is legal today, and a recipe with no `data_schemas` is refused by the check. Whether an empty `data_schemas` passes: not read.
- **The recipe check** reads the metadata block only when it is there [CODE READ `recipe_check.py:356-357, 381-384`]; no code found that requires it. E02 (a declared population's table and its id field) and E03 (a number type refused on an id field) apply to any table [CODE READ `recipe_check.py:332-348, 445-458`].
- **With no metadata block,** the two completions have nothing to complete from, and the id check (both directions) has nothing to compare with, unless the recipe declares a population (`entity.population`).
- **The Gallery** registers each bundle's one `example_data.tsv` under `data_schemas` [RECIPE FILE `assets/gallery_data/bar_simple/data_analysis_recipe.yaml:11, 16`].
- **No shipped recipe** has a metadata block and no data table: every recipe with a `metadata_schema` has at least one data schema [READ SCAN of `config/data_analysis_recipes`].

**The point for her (her view; hers to decide).** A recipe whose only real table is "metadata":
- (a) a guideline only (the documentation, D-0583);
- (b) an advice of the recipe check: "this recipe has a metadata table and no data table: register it as data";
- (c) a rule the check refuses.

What she would see: the demo has 9 data tables, so its metadata stays the metadata, and her view does not move the two QA tables by itself (they read the metadata of a recipe that has data). A Gallery bundle is already registered as data, so nothing changes there.

- Lean (Opus, as a lean): (a). The format already requires `data_schemas` and keeps the metadata optional, which is the shape of her view. An advice would need the check to judge what a table holds, which it cannot read from the recipe.
- [Sonnet lean]
- Neither: say what you meant.

**For the held documentation task (D-0583), in her words:** "if there is only "metadata" then it should go under the original_data - that will also help for the lineage".

**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).
END BLOCK 1
