# Opus checks the D-0569 additions (B3, her answers) (v1), by reading only

**What I read.**
- `git diff` of `CAUSE_AND_SOLUTIONS_ZEROS.md` and `OVERLAP_AND_POPULATION.md` (main tree).
- The ledger line D-0569, in full.
- Recipe files: `QA_AMR_per_sample_tier2.yaml`; `ResFinder_wrangling_tier1.yaml:2-4`; the ResFinder schema (`null_values: []`, `strip: true`); `demo_abromics.yaml`; the shared `metadata_schema_input_fields.yaml` (`null_values: ["", "-"]` on `sample_id`).
- Code: `libs/ingestion/src/ingestion/declared.py:115-120`; `orchestrator.py:269-283`.
- The metadata file of `demo_abromics`, the generator and the test.
No run.

## 1. The B3 entry

**True:**
- No registered action appends rows.
- `QA_AMR_per_sample` tier 2 counts non-empty genes. Its own comment: "count() counts non-empty values, so a sample without a gene gets 0, not 1". Its tier 1 has 74 rows (70 + 4).
- `ResFinder` tier 2 counts rows: `pl.len().over(['sample_id'])`, so an empty-result line gives 1.
- `ResFinder` tier 1 stamps `status: pl.lit('Detected')`, so an empty-result line would say "Detected".
- A cell with only spaces becomes an empty text after the strip and is not missing with `null_values: []`. The ingestion strips, then applies the null words, then the type [CODE READ `declared.py:115-120`].
- Under B3, with the data first and the metadata second (`left`), a removal at the data table's own place takes the entity out completely [REASONED from RECIPES G5].
- B3 makes B2 and the declared population unnecessary where the files list every analysed entity. They answer the files that cannot be changed: agree.

**Q1, two inexact sentences in (ii).**
1. "a data schema's tier 1 cannot hold a join (ST05, J05: a join step names only the join's own ingredients)". The precise reason for a schema is that its tier 1 runs on its own table only (`prepare_ingredient`) [CODE READ `orchestrator.py:269-283`]. J05 is about joins.
2. "that is candidate (e) or (a2), a join that keeps the metadata's rows". (a2) keeps the rows of a table of the analysed entities, not the metadata's.

Replace the two sentences with: "A recipe step cannot add the rows: a schema's tier 1 runs on its own table only (`prepare_ingredient`, `orchestrator.py:269-283`), and no registered action appends rows. The only recipe routes are joins that keep another table's rows: the metadata's (A, or (e) with `right` or `full`), or a table of the analysed entities ((a2))."

**Q2, missing from (iii) and (iv)** [REASONED]. Add:
- "A count of DISTINCT genes would count the empty value as one value (a null counts in a distinct count), so 1, not 0. The scan found one such count: `2_test_data_ST22_dummy :: AMR_Profile_Joint`."
- "An explicit column in the result file ("analysed: yes"), or a manifest of the analysis, would say "analysed, nothing found" more clearly than a line with an empty gene. An empty gene is read as a hit by every step that counts rows or stamps a value."
- "Her contract becomes two-directional only for the entities that were analysed. The data check can inform in that direction but cannot know which metadata entities were analysed." This is already in (v); keep it.

## 2. The B3 option in the question

It says what B3 is and marks the reading as not confirmed by her. What she would see (42 bars with 4 at 0; 41 after a removal at ResFinder) is marked as reasoned. Nothing is decided for her. One thing it gives up is missing.

**Q3.** Add to option B3: "The recipe's own steps that count rows or stamp a value would read the empty line as a hit: in ResFinder, `total_gene_count` 1 and `status` "Detected". They would need to be adapted, or the file would carry an explicit "analysed" column."

**My lean on B3, as a lean:** B3 where the pipeline that makes a result file knows every entity it analysed and writes that fact into the file, preferably as an explicit "analysed" column that the recipe reads rather than as a line with an empty gene; B2 where the files cannot be changed; A otherwise.

Reason: B3 puts "analysed, nothing found" where it is known (the pipeline), gives her 0 the meaning she wants ("then we would keep the 0 that means eg. no resitance gene was found", D-0569), and makes a removal at the data table complete. But an empty gene is read as a hit by the steps that count rows or stamp a status, so the form of the file must be agreed with the recipe.

## 3. The data check as decided, and the Validate question

- The text says only what she decided: option (b), a new channel, and her words exact.
- The wording of the note is marked as a proposal.
- The Validate question is clear and fair, with what she would see for yes and for no.

**My lean on Validate, as a lean:** yes. The person who can fix the data or the recipe sees the note before anyone relies on the results.

## 4. The dry-run candidates

**(A) `demo_abromics`: the reading is right** [RECIPE FILE; DATA FILE]:
- Three lines have no usable id: line 5 empty, line 6 `-`, line 11 `""`.
- The id field reads `""` and `-` as missing (`null_values: ["", "-"]` in the shared `metadata_schema_input_fields.yaml`).
- The join's tier 1 starts with a visible `polars_drop_nulls` on `sample_id`.
- The descriptions name the removal ("Removed by this recipe, on purpose: the 3 metadata lines that have no sample id").
- The generator writes them (`generate_demo_data.py:47`, `NO_ID_MARKERS = ["", "-", '""']`), and the test asserts them (`test_demo_join_keeps_every_sample.py:38`, and the "no row without a sample id" test).

**Q4.** Add, said plainly (D-0532):

"Your order "remove the null and empty rows from the metadata" meets a recipe that already removes them, visibly, as a lesson about messy exports.
- **Keep:** a user of `demo_abromics` sees the metadata with 30 lines (3 without an id), a visible step that removes those 3, the join with 27 rows, and the description saying so.
- **Remove:** a user sees 27 lines, no removal step, and no example of a messy id; the generator, the step, the descriptions and the test change with it.
Both remove the 3 lines from every result; they differ in whether the recipe shows the problem and its fix."

**(B)** Correct, as read: `2_test_data_ST22_dummy` has a `metadata_schema` block, `amr_data` and `plasmid_data`; `figshare_integration` has `fg_metadata`, `fg_phenotypes`, `fg_genotypes` and no `metadata_schema` block. Neither declares an id. The note that the data check would not find the metadata of `figshare_integration` is right and kept.

## 5. Her words, and the closing line

Her words are exact, compared with the ledger's evidence fields: D-0569 (quoted in full, identical), D-0568, D-0564.

**Q6.** Replace "The Opus agent has not stated a lean on B3." and "The Opus agent has not stated a lean on this question." with my two leans above (section 2 for B3, section 3 for Validate).

**I sign the D-0569 additions with these 5 replacements: Q1 (ii) the route sentences; Q2 the missing points of (iii)/(iv); Q3 what option B3 gives up; Q4 the dry-run choice for `demo_abromics` with what a user sees; Q6 my leans on B3 and on Validate. Nothing else stays open.**
