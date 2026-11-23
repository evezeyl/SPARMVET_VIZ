# Her contract on the ids and the metadata, the data check, and the declared population (2026-11-23)

**What this is.** Her contract and order of ledger D-0568: "the metadata is supposed to cover all the ids of the result files", and "yes the app check could be good - to identify those that have no metadata - good idea". It holds three things: (1) a count of the data files of the demo and the other shipped recipes, to see whether her contract holds; (2) the data check she approves, by reading the code; (3) whether the declared population (`entity.population`) can be the source of the zeros, by reading and reasoning. Made by an Opus and a Sonnet design agent who agreed before it was written (D-0552). **The count** was made by a read-only script (registered first with its three points: `tmpAI/coordinator/design_dialogue/RUN_REGISTER_sonnet_overlap.md`, run O1) and cross-checked by a second independent count (`RUN_REGISTER_opus_recipes.md`, RR13): the two agree number for number on the demo. **The data check and the population were done by reading and reasoning, with NO engine run**, by her orders D-0565 and D-0566. NOT confirmed by her. Nothing is built; no recipe is changed.

**The limits.** The counts are on the FILES, before the recipe's tier-1 steps (the tier-1 steps need the engine). The demo recipe is counted by both agents; the other shipped recipes only by the Sonnet agent. The demo cannot show the gain of the population pattern: every metadata id is in `FastP`, `Quast` and `Summary` (42 of 42). Feasibility of any new check or pattern is NOT run; it comes after her choice, in the retest described at the end.

Tags: [HER WORDS D-n] / [DATA FILE COUNT, script] (`overlap/sonnet_O1.py`, `overlap/O1.out`; Opus RR13, `opus3_rr13.out`) / [RECIPE FILE] / [CODE READ file:line] / [REASONED, not run]. The scratch folder `tmpAI/coordinator/design_dialogue/` is not in git.

---

## HALF PAGE FOR HER

**Does your contract hold on the demo files?** Your contract: "the metadata is supposed to cover all the ids of the result files" [HER WORDS D-0568]. It is one-directional: the ids of each result file are in the metadata. **Yes, it holds on every result file of the demo recipe**, with no exception. [DATA FILE COUNT; Opus RR13 agrees number for number]
- Per file: `Summary`, `Summary_quality`, `Quality_metrics`, `Detailed_summary`, `FastP`, `Quast`, `Bracken`, `MLST`, `VirulenceFinder` and `ResFinder`: 0 ids outside the metadata. The full table is in section 1.
- Every result file has 0 ids that are absent from the metadata. The metadata has 42 ids.
- The other direction is as you expect: `ResFinder` has lines for 38 of the 42 ids, so 4 metadata ids have no line there (the 4 entities with 0 genes). Every other result file has all 42.
- The form of the ids is not a problem: the counts on the raw text, after the strip the recipe declares, and after strip and lower case are the same in every file. No id is empty.
- So the datasets are not incorrect on the demo: there is no id in a result file without a row in the metadata.

**Beyond the demo** (the other recipes whose data is in the repository):
- `demo_abromics`: its metadata file has 30 rows: 28 real ids, one row with a missing id (null) and one row with an empty id. Its MLST file has 15 ids, all in the metadata (13 of the 28 real metadata ids have no line there). The two rows with no id are a data problem the check should report. [DATA FILE COUNT]
  > **Correction of 2026-11-23 (D-0569):** it is three lines, not two (empty, `-`, and two quote marks), and they are there on purpose; see "Her answers of 2026-11-23".
- `templates/left_join_lesson`: 2 ids of the `sequenced` file are not in the metadata (`ACC0001`, `ACC0002`). This lesson is written on purpose to show what a left join does when ids do not match (its description says so).
- `2_test_data_ST22_dummy` and `figshare_integration` declare no entity id. Read by the column name `sample_id` (not declared), their result files are all inside the metadata too.
- Two templates (`e_coli`, `simple_template`) have no data file in the repository; the other recipes have no metadata table.
- All counts are on the FILES, before the recipe's tier-1 steps; a tier-1 step that removes rows can change the ids of a table.

**The data check you approved** ("yes the app check could be good - to identify those that have no metadata - good idea"). The data check that exists already reads each table, but only one table at a time; it never compares two tables. A new part would list, for each result file, the ids that have no row in the metadata, with their count and the ids, and name your two remedies: upload the complete metadata again, or remove those ids from the data tables by an audit step. What it needs from the recipe: the entity id declared in both tables, and the metadata table. Your choices: does a violation refuse the recipe or only inform; where it is shown. Options (a) to (d) are in section 2, with what you would see. **One thing to know before you choose: if a violation refuses the recipe (option (a)), your second remedy cannot be used.** A refused recipe does not open in HOME, so the ids cannot be deleted there by an audit step. Nothing is chosen.

**Is the declared population a lever for the zeros? Partly.**
- **(a2) needs no new key; its parts run today, the whole chain is not run yet.** A table of the entities that were ANALYSED as the first table of the join (a data table), the counts next, the metadata second. Zeros appear for the analysed entities with no hit, the metadata's extra entities stay out (your reason in D-0549: "some users will have metadata for more samples so that will allow to join what really is in T1 without the extra in metadata"), and the join does not start with the metadata (D-0564: "the join should not start with the medata"). On the demo you would see the same 42 samples counted as today, because every metadata id is in `FastP` (42 of 42); the difference appears only with an entity that was never analysed.
- **(c) with the declared population as its source does not exist.** Today `entity.population` is read by the recipe check only (the table exists and has an entity id); the app does nothing with it, and no demo recipe declares it.
- **What stays false.** The false zero at the data table's own place: an entity removed at ResFinder stays in the first table and shows 0. And "analysed" is relative to ONE analysis: a read-quality table lists the sequenced entities, but an AMR run can fail for one of them, and its 0 would again mean "not analysed". The right table is a manifest of the analysis, or one of its own result files with one row per analysed entity.
Section 3.

---

## 1. TASK 1, the overlap on the demo files

Registered first: `RUN_REGISTER_sonnet_overlap.md`, O1, with its three points. The script reads the source files with a plain reader (polars) and the recipe's own declarations (the field marked `is_entity_key`, its `original_name`, the file path, `strip`, the type) from my own YAML parse. No engine, no lineage code, no stored table. Load 3.3. The result agrees with the expectation. [DATA FILE COUNT]

**The demo recipe `1_test_data_ST22_dummy`.** The metadata file `test_metadata_20260307_105756.tsv`: id column `sample_id`, 42 rows, 42 distinct ids, strip on, type String, no empty id.

| Table (block) | File | Rows | Distinct ids | Ids NOT in the metadata (raw / strip / strip + lower case) | Metadata ids NOT in the file |
|---|---|---|---|---|---|
| `Summary` (data) | `test_data_Summary_...tsv` | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `Summary_quality` (data; the same file as `Summary`) | the same | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `Quality_metrics` (data) | `test_data_Quality_metrics_...tsv` | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `Detailed_summary` (data) | `test_data_Detailed_Summary_...tsv` | 280 | 42 | 0 / 0 / 0 | 0 of 42 |
| `FastP` (data) | `test_data_FastP_...tsv` | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `Quast` (data) | `test_data_Quast_...tsv` | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `Bracken` (data) | `test_data_Bracken_...tsv` | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `ResFinder` (data) | `test_data_ResFinder_...tsv` | 70 | 38 | 0 / 0 / 0 | **4 of 42** |
| `MLST` (data) | `test_data_MLST_results_...tsv` | 42 | 42 | 0 / 0 / 0 | 0 of 42 |
| `VirulenceFinder` (additional) | `2_VIGAS-P_ST22_dummy/test_data_VIGAS_VirulenceFinder_...tsv` | 1315 | 42 | 0 / 0 / 0 | 0 of 42 |
| `APEC_STEC_virulence_genes` (additional) | `Virulence_genes_APEC.tsv` | (a reference list) | no declared entity id | not checked | not applicable |

**Per file: does the contract hold? Yes, for the ten files with a declared entity id.** The only table with no declared entity id is the reference list of virulence genes, which holds no entities.
**The form of the ids:** raw, stripped and lower-cased counts are equal in every file, so no mismatch comes from spaces, case or empty values. A number read as a number is not tested: every id column is declared `String`, and the demo ids are numbers written as text (for example `10668076`); a declared number type for these ids would remove leading zeros, and the recipe check refuses a number type on an entity id (E03). [DATA FILE COUNT; RECIPE FILE]
**Not counted here:** the ids after the recipe's tier-1 steps (these need the engine). The data check of section 2 would read them after tier 1.

**The other recipes** [DATA FILE COUNT, `overlap/O1.out`]:

| Recipe | What was found |
|---|---|
| `1_Abromics_general_pipeline` | metadata and `MLST` and `VirulenceFinder`: 0 ids outside the metadata; the reference list has no entity id |
| `demo_abromics` | metadata 30 rows: 28 real ids, **1 null id and 1 empty id**; `MLST` 15 ids, all in the metadata; 13 of the 28 real metadata ids have no line in `MLST` |
| `templates/complex_template` | `genomics` (id column `Accession`) against the metadata (id column `ID`): 0 outside, 0 absent |
| `templates/left_join_lesson` | `sequenced` (`Accession`): **2 ids not in the metadata** (`ACC0001`, `ACC0002`), 2 of the 10 metadata ids not in the file; by design of the lesson |
| `2_test_data_ST22_dummy` (no declared id; by the column `sample_id`) | `amr_data` 70 rows, 38 ids, 0 outside, 4 metadata ids with no line; `plasmid_data` 163 rows, 41 ids, 0 outside, 1 metadata id with no line |
| `figshare_integration` (no declared id; by `sample_id`) | `fg_phenotypes` and `fg_genotypes` 980 ids each, 0 outside `fg_metadata`, 0 absent (its metadata is a data schema, not a `metadata_schema`) |
| `templates/e_coli`, `templates/simple_template` | the data file is not in the repository |
| the other recipes (gallery bundles, retest, equality, stress test) | no `metadata_schema`; the gallery bundles are one table with no entity id |

**Tables with no declared entity id:** `APEC_STEC_virulence_genes` (demo, `1_Abromics_general_pipeline`), all three tables of `2_test_data_ST22_dummy`, all three of `figshare_integration`, and the one table of each of the 34 gallery bundles. [DATA FILE COUNT]
**A finding of the count, apart from the contract:** a null or empty id in the metadata (`demo_abromics`: two rows) is invisible to the left join (it matches no entity) and is not an id of any result file. Her contract does not cover it; a check on the metadata itself (no empty id) would. [REASONED]

---

## 2. TASK 2, the data check she approves

**What exists today** [CODE READ]:
- `validate_data_analysis_recipe_data` (`app/modules/data_analysis_recipe_validator.py:485`) builds each table of the recipe on its own (`prepare_ingredient`: the file, the input contract, the tier-1 steps) and reports a dataset that cannot be loaded or a step that cannot run (lines 520-545). It never puts two tables side by side: no id is compared with another table.
- The HOME load gate (`app/src/bootloader.py:431-451`) runs the structure check, then this data check. A problem from either rejects the recipe: it goes to HOME's refused list with its contact. "Advices never reject a recipe; HOME lists them" (lines 432-436, 444-449), but the advices come from the recipe check only (`checker_advices`), which reads no data. So today the data check has no way to inform without refusing.
- BLUEPRINT's Validate runs the same two checks (`app/handlers/blueprint_handlers.py:2850, 2892`) and only reports.
- The Data Import panel checks a candidate file (`app/modules/data_import_check.py`, `ingest_file`, lines 178-231): the ingestion's own read of the candidate for its dataset; all files or none. It compares no ids with the metadata.

**Where a check that reads the data could list the ids with no metadata** (a reading, nothing built) [REASONED]:
1. In the data check, after each table is built: for every table that declares the entity id, the set of its ids minus the metadata's ids. The tables are read after their tier-1 steps (`prepare_ingredient`), the same tables the joins read. This differs from the files (my count): a tier-1 step that removes rows or changes the id can change the result.
2. In the Data Import panel: when a file replaces a data file, compare its ids with the current metadata; when the metadata file is replaced (the case "upload the complete metadata again"), compare the ids of every result table with the new metadata.
3. In BLUEPRINT's Validate: the same function as the gate.

**What it needs from the recipe:** (a) the entity id declared in both tables (her renamed `is_entity_id`): two shipped recipes declare no entity id at all (`2_test_data_ST22_dummy`, `figshare_integration`), so the check could not run there and should say so plainly; (b) which table is the metadata: the `metadata_schema` block (optional in the recipe format: `recipe_spec.yaml:24`), or the table that `entity.population` names. [CODE READ]

**What it would say** (a plain line; the words are not decided): "In the table `ResFinder`, 3 ids have no row in the metadata: <the ids, up to 20>. Either upload the complete metadata again, or remove these ids from the tables where they have no metadata by an audit step." For the demo it would say nothing: no violation. [REASONED; DATA FILE COUNT]
It informs and does not choose: the two remedies are named; the user picks.

**Options that are hers** (nothing chosen):
- **Does a violation refuse the recipe or only inform?**
  - (a) Refuse at the load gate: the recipe goes to HOME's refused list with the line above and its contact. She would SEE the recipe missing from the selector with the reason. Today this is the only mode of the data check. **Under (a), your second remedy cannot be used:** a refused recipe does not open in HOME, so no audit step can delete the ids ("OR delete the id where there is no metadata in the respective parent tables via audit", [D-0568]). (a) also refuses, at its next opening, a recipe whose metadata is replaced later by an incomplete file. [CODE READ `bootloader.py:431-451`: a rejected recipe is not in the available list]
  - (b) Only inform (her words: "No silent error that is the rule." [D-0050]; "an inner join would hide this" [D-0568]): HOME lists the line as an advice and the recipe opens; the left join (data first, metadata second) shows the entities with empty metadata columns, as she described. Needs a new channel for data advices (today advices come only from the recipe check).
  - (c) Refuse in the Data Import panel (a file that breaks the contract is not written) and only inform at the gate. She would SEE the panel refuse the replacement with the line.
  - (d) Neither: say what you meant.
- **Where it is shown** (not exclusive): HOME's refused list or advices list; the Data Import panel after a replace; BLUEPRINT's Validate.
**Lean (as a lean):** inform at the gate and in Validate, and refuse in the Data Import panel only a metadata replacement that would make a result file's ids fall outside it. Reason: an inner join would hide the violation, a refusal at the gate would remove one of her two remedies, and her words say what the job is: "Our job is to try to give as clear information as possible - so the user has elements it needs to be able to make a good decision" [D-0543]. [REASONED]

---

## 3. TASK 3, is `entity.population` the lever for the zeros?

**What the recipe declares today** [RECIPE FILE; CODE READ]:
- The format: `entity: {noun, plural, population}`, optional; `population` is "the id of the table with one row per unit" (`recipe_format_spec.md:378`; `recipe_spec.yaml:29-31`). The example in the specification reads `population: Anchor` (line 35): it is an example in the text, not a declaration of the demo. **No demo recipe declares an `entity` block.** The only shipped recipe that does is the template `left_join_lesson`: `noun: sample`, `plural: samples`, `population: sequenced`, and `sequenced` is the DATA table (the left table of the lesson), not the metadata.
- The check: E01 (an unknown or missing key of `entity`), E02 (`population` is not a table of the recipe, or its table has no entity id) (`recipe_check.py:333-348`).
- The app: nothing else. A search of `libs/` and `app/` for `population`, `noun`, `plural` and the `entity` block finds only that check. The words of the screens are not taken from it today.

**Could a completion of the zeros come from the declared population instead of the metadata?** [REASONED, not run]
- **Two different things, named apart.**
  - **(a2) A table of the analysed entities as the BASE of the join.** Candidate (a) of `CAUSE_AND_SOLUTIONS_ZEROS.md` with the table of (f2) as its first table; the `entity` block is optional and only checked. It needs no new key; its parts run today, the whole chain is not run yet.
  - **(c) with the declared population as its SOURCE.** A completion read from `entity.population`, so that the app knows which zeros are filled. This does not exist.
- **What it needs.**
  1. A population table that lists the entities that were analysed. That can be a result file with one row per analysed entity (on the demo `Summary`, `FastP`, `Quast`, `Quality_metrics` each have 42), a manifest of the pipeline, or a table of its own. Who writes it: the pipeline that produced the results, or the recipe maker who chooses the file. The metadata is not it when the metadata holds entities that were never analysed.
  2. When the metadata holds more entities than were analysed, the metadata cannot tell "analysed, zero hits" from "never analysed": both are 0 when the metadata is the base. With the population as the base, an entity of the metadata that is not in the population does not appear, and an entity in the population with no ResFinder row shows 0 and means "analysed, zero hits". This is the real gain over the metadata.
  3. For (a2), nothing is declared: the author puts the table first. For (c), the recipe says which table is the population: that exists as `entity.population`, read by the check only, and the completion step itself does not exist.
  4. **"Analysed" is relative to one analysis.** The population must list the entities that THIS analysis ran on. A read-quality table such as `FastP` lists the sequenced entities; an AMR run can fail for a sequenced entity, and its 0 would then mean "not analysed" again. The right table is a manifest of the analysis, or one of its own result files with one row per analysed entity. [REASONED]
- **Does it keep her direction (the data first, the metadata second)?** If the population is a result file, the join starts from a DATA table: population (a data table) first, the counts of ResFinder next (left), the metadata second (left). Her words "the join should not start with the medata" [D-0564] are then followed to the letter, and her reason in D-0549 as well (the metadata's extra entities stay out), and her contract (every result file is inside the metadata) keeps the metadata second from adding entities. Needing no new key (its parts run today, the whole chain is not run yet): the base is a result table that has one row per analysed entity. [REASONED from her contract and the join semantics; the base table is the choice of the author]
- **How the audit treats a removal.** At the population table's own first place: the entity leaves the base and everything below (the join, the plot): gone. At the data table's first place (ResFinder): the entity is still in the population, so the table shows it with a filled 0: the false zero remains, as in every candidate with zeros. At the join place or with "Remove from all the data": gone. Paths covered at the ResFinder place: 1 of 3 (population, ResFinder, metadata). [REASONED; ESTABLISHED: PATHS G8]
- **What the check could verify.** (1) The population table exists and has an entity id (E02, today). (2) By the data check: every id of every result file is in the population. This is checkable in one direction: an entity that has a line in a result file was analysed, so it must be in the population; an id in a result file but not in the population means the population is incomplete. The other direction (population ids with no line in a file) is normal. (3) By the data check: the population's ids are in the metadata (her contract). It cannot verify that the population is the set of analysed entities: a population that misses an analysed entity loses its zero without a message. [REASONED; CODE READ for what exists]
- **What cannot be judged without a run** (after her choice; each registered first):
  1. Requirement: build (a2): a per-entity result with a table of the analysed entities (a result file) as the base, ResFinder counts left, metadata second, on a scratch copy of the chain of `qa_amr_genes_per_sample`. **The demo cannot show the gain:** every metadata id is in `FastP`, `Quast` and `Summary` (42 of 42) [Opus RR13]; the scratch copy needs one entity in the metadata that was never analysed. Expected: with (a2) that entity is absent from the result; with the metadata as the base (option A) it shows 0. For the other entities: 42 minus that one, with 4 at 0; a removal at `T1:ResFinder`: false zero; at the base's first place: gone; at the join place: gone. Independence: a scratch recipe from the demo's own schemas, hand-written steps, each table rebuilt in its own empty folder, no lineage code.
  2. Requirement: a completion step that reads `entity.population` after tier 2 (candidate (c) with the declared population as its source). Expected: not buildable today, since tier 2 receives its table and not the population; to be confirmed. Same independence.
- **Answer: partly.** Yes as a pattern that needs no new key and whose parts run today (the whole chain is not run yet), (a2): the table of analysed entities as the base of the per-entity join (it follows the order and the reason of her direction and separates "analysed, zero hits" from "never analysed", for ONE analysis). No as a lever of the app: nothing reads `population` today, a completion from it is candidate (c) and does not exist, and the false zero at the data table's place stays.

**The answer in five lines**
1. `entity.population` is read by the recipe check only (the table exists and has an entity id); the app does nothing with it, and no demo recipe declares it (the specification's `Anchor` is an example).
2. A table of the entities that were analysed, named as the population, can be the base of the per-entity join: the zeros then mean "analysed, zero hits", and entities of the metadata that were never analysed do not appear.
3. If that table is a result file, the join starts from a data table and the metadata comes second, which follows her direction; no new key is needed, and the whole chain is not run yet.
4. The false zero at the data table's place remains; the join place, the population's own place and "Remove from all the data" remove the entity.
5. What cannot be judged without a run: whether a completion from the declared population can be built in tier 2; and the retest above, with its three points, after her choice.

---

## Where this goes in the catalogue (`CAUSE_AND_SOLUTIONS_ZEROS.md`)

Candidate **(a2)** is added there as its own entry and as option B2 of the question, with a correction of the sentences that said every form with zeros keeps the metadata as the side whose rows stay. **(c) with the declared population as its source** stays under (c). The fragment of (a2), not run:
```yaml
data_schemas:
  FastP: {...}                      # one row per analysed entity (here a stand-in: a manifest of the analysis is the right table)
joins:
  AMR_per_entity:
    ingredients: [{dataset_id: FastP}, {dataset_id: ResFinder_per_entity}, {dataset_id: metadata_schema}]   # a data table first, the metadata last
    tier1:
      steps:
        - {action: polars_join, right_ingredient: ResFinder_per_entity, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_join, right_ingredient: metadata_schema, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_fill_null, columns: [n_amr_genes], value: 0}
```
What the audit does: default place the join place (gone); first place of ResFinder: false zero (1 of 3 paths covered); first place of the base table: gone. What it prevents: the metadata's never-analysed entities appearing as zeros; the join starting from the metadata. What it does not: the false zero at the data table's own place; "analysed" relative to one analysis. Today its parts are accepted by the check and run by the engine (a data table first, left joins, a fill; the `entity` block optional); the whole chain is not run. [REASONED from the established runs; the combination is not run: the retest above, with its three points]

## Her answers of 2026-11-23 (ledger D-0569)

Added after the file was signed; the signed text above is kept. Checked by the Opus agent afterwards (OPUS_checks_b3_v1.md and OPUS_signs_b3_v2.md). Her words, exact (one passage; the quotation marks inside are hers): "ok other recipes - remove the null and empty rows from the metadata. Have the recipes declaire entity id. Ok for the population anchor - as long as we can compute its fine - we can revisit if we see it is necessary. Data check from the code - ok we need the new chanel - for the blueprint validate I am not sure what the questions implies it is unclear. Choice for data check - b: and inform that the user should better fix this otherwise it will could lead to problems like imparing the relevance of information provided by the app. Would that be ok ? "false zero at the data table's own place stays" yes because here 0 means not found in the id ... that is actually maybe why we decided to join with metadata first ... So I think the match between ids in the tables is even more important. So the ids that are in metadata and not in the results data might require to be added to the results files.... a point to consider. then we would keep the 0 that means eg. no resitance gene was found." [HER WORDS D-0569]

**What each part decides**
1. **Other recipes.** "remove the null and empty rows from the metadata. Have the recipes declaire entity id." Both are changes to shipped recipes or data: dry-run candidates, below. Nothing is edited now.
2. **The population.** "Ok for the population anchor - as long as we can compute its fine - we can revisit if we see it is necessary." The declared population is accepted as a lever for the zeros if it can be computed; to revisit if needed. Which table is not decided. [Reading of the review session; the Sonnet agent reads it the same way]
3. **The data check: option (b), only inform, through a new channel.** "ok we need the new chanel"; "Choice for data check - b: and inform that the user should better fix this otherwise it will could lead to problems like imparing the relevance of information provided by the app." DECIDED by her words. So the recipe is NOT refused (her second remedy stays possible: the id is removed by an audit step). How it works, read from the code:
   - The channel: at the gate the two checks return problems (which refuse) and advices (which never refuse; they come only from the recipe check, which reads no data) [CODE READ `bootloader.py:431-451`]. The new channel is a data advice list next to them: the data check reports what it measured and the recipe opens.
   - Where it runs: after the tables are built in the data check (HOME's gate and BLUEPRINT's Validate use the same function) and in Data Import after a replace. [CODE READ `data_analysis_recipe_validator.py:485`, `data_import_check.py`]
   - What it says (a proposal of wording, hers to change): "In the table <name>, N ids have no row in the metadata: <the ids, up to 20>. It is better to fix this: otherwise the information the app gives may be less reliable. Either upload the complete metadata again, or remove these ids from the data tables by an audit step. The recipe still opens."
   - The other direction (for B3): "N entities of the metadata have no line in this result file: <ids up to 20>. If they were analysed and nothing was found, the file should hold a line with an empty result for each; if they were not analysed, leave them out. The app cannot tell which."
4. **The false zero at the data table's own place stays: accepted.** "yes because here 0 means not found in the id ... that is actually maybe why we decided to join with metadata first ... So I think the match between ids in the tables is even more important."
5. **A point to consider, not decided.** "the ids that are in metadata and not in the results data might require to be added to the results files.... a point to consider. then we would keep the 0 that means eg. no resitance gene was found." The review session's reading, NOT confirmed by her: candidate B3, evaluated in `CAUSE_AND_SOLUTIONS_ZEROS.md` (entry (B3) and option B3 of the question).

**The question on BLUEPRINT's Validate, written again in one plain sentence** (she found the first one unclear):
> When you check a recipe you are building in BLUEPRINT, should the same note about ids with no metadata appear there too, so that the person who writes the recipe sees it before the recipe is used?
What she would see: with **yes**, the person who presses the check button in BLUEPRINT gets the same note as HOME's data check would show, with the table, the number of ids, the ids and the two remedies; with **no**, the note appears only when the recipe is opened in HOME and in Data Import. **Neither: say what you meant.** (Lean of the Sonnet agent, as a lean: yes, because the author can fix the data or the recipe before anyone uses it. Lean of the Opus agent, as a lean: yes; the person who can fix the data or the recipe sees the note before anyone relies on the results.)

**The dry-run candidates from her answers** (the one dry run shown to her before anything is applied, D-0525; no file is edited here). [DATA FILE COUNT; RECIPE FILE; CODE READ]
- **(A) "remove the null and empty rows from the metadata", the recipe that has them: `demo_abromics`** (`config/data_analysis_recipes/pipelines/demo_abromics.yaml`; the data file `assets/test_data/demo_high_integrity/test_data_test_metadata_20260307_105756.tsv`, 31 lines with the header). **Three lines have no usable id** (my first report said two; the third is the quote marks, which a plain reader reads as an empty text):
  - line 5: an empty id; the line holds `Parent`, `2024`, `France`;
  - line 6: the id `-`; `Broiler`, `2024`, `Norway`;
  - line 11: the id `""` (two quote marks); `Layer`, `2024`, `Norway`.
  Said plainly: your order "remove the null and empty rows from the metadata" meets a recipe that already removes them, visibly, as a lesson about messy exports. If it is kept, a user of `demo_abromics` sees the metadata with 30 lines (3 without an id), a visible step that removes those 3, the join with 27 rows, and the description saying so. If the lines are removed, a user sees 27 lines, no removal step, and no example of a messy id; the generator, the step, the descriptions and the test change with it. Both remove the 3 lines from every result; they differ in whether the recipe shows the problem and its fix. [REASONED from the recipe, the generator and the test, as below]
  These lines are there ON PURPOSE. The recipe reads `""` and `-` as missing (`null_values: ["", "-"]` on the id field) and removes the missing ids by a visible step in its join (`polars_drop_nulls` on `sample_id`, with the comment "a metadata line without a sample id cannot be linked to an MLST result: it is removed here (3 lines in this demo data)"). Its description says so. The generator `assets/scripts/generate_demo_data.py` writes them (line 47, `NO_ID_MARKERS = ["", "-", '""']`), and the test `app/tests/test_demo_join_keeps_every_sample.py` asserts 3 lines without an id (line 82) and the recipe's wording about them (lines 150 and 161). So the choices for the dry run are: remove the three lines from the file (and the generator default, the step, the description, the test); or keep them as the demo of a data problem that the recipe removes visibly, and let the new data check inform about them (the three lines read as missing ids, not as ids outside the metadata). Hers to choose in the dry run.
  A correction of an earlier count of mine, `demo_abromics`: the metadata has 30 data lines: 27 lines with an id and the 3 lines above (my plain count of "28 real ids, 1 null, 1 empty" took `-` for an id).
- **(B) "Have the recipes declaire entity id": the two recipes that declare none.**
  - `2_test_data_ST22_dummy` (`config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`): `metadata_schema` (file `assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv`; its input_fields file `2_test_data_ST22_dummy/input_fields/metadata_schema.yaml`, field `sample_id`, `original_name sample_id`); `amr_data` (the ResFinder file; `input_fields/amr_data.yaml`, field `sample_id`); `plasmid_data` (the PlasmidFinder file; `input_fields/plasmid_data.yaml`, field `sample_id`). Each would carry the id marker on `sample_id` (after the rename, `is_entity_id`).
  - `figshare_integration` (`config/data_analysis_recipes/pipelines/figshare_integration.yaml`): `fg_metadata`, `fg_phenotypes`, `fg_genotypes` (files `libs/transformer/tests/data/fg_*.tsv`; the input_fields files `figshare_integration/input_fields/fg_metadata_input_fields.yaml`, `fg_phenotypes_input_fields.yaml`, `fg_genotypes_input_fields.yaml`, field `sample_id` in each). It has no `metadata_schema` block: its metadata is a data schema, so a data check that looks for "the metadata" would not find it unless the recipe is given one (or the check is told which table). [CODE READ: the metadata block is optional, `recipe_spec.yaml:24`] The three files are test data of the transformer library.

## Her answers of 2026-11-23, second part (ledger D-0570)

Added after the file was signed; the signed text above is kept.

**Her words, exact** (channel block M624): "I think the data check information as suggested." and "4. yes the validated question - yes . information is very important here." [HER WORDS D-0570]

**What each decides** (readings of the review session, kept as such)
1. **The data check informs in BOTH directions.** In one direction: "N ids of this file have no row in the metadata" (the contract of D-0568). In the other, as information: "N entities of the metadata have no line in this file" (on the demo, 4 of 42 for ResFinder). The app cannot tell "not analysed" from "analysed, nothing found"; the note says so and says what the user can do: if they were analysed and nothing was found, the file should hold a line with an empty result for each (B3); if they were not analysed, leave them out; or, if you choose G, declare in the recipe what a missing line means (G). It informs through the new channel; it does not refuse (D-0569). It goes with every form of the list in `CAUSE_AND_SOLUTIONS_ZEROS.md`.
2. **The same note appears in BLUEPRINT's Validate: yes.** The person who writes the recipe sees it before the recipe is used.

**A third note, proposed from her sentence "the metadata itself should have id with non empty lines" (not decided).** "N lines of the metadata have no id." Why it matters: a line with no id never matches, so an anti-join lists each such line, and a left join from the metadata keeps them, where a grouping by the id makes one entity of all the missing ids (Polars semantics, not run): the count of "not detected" grows by one per line in the list of E2, and by one in all in the per-entity count of A. [CODE READ `libs/transformer/tests/test_self_join_build.py:169`]

**The case of `demo_abromics`.** Its metadata file has 30 data lines under its header; 3 have no usable id (file lines 5, 6 and 11: empty, `-`, `""`) [DATA FILE READ]. They are there on purpose: the id field reads `""` and `-` as missing [RECIPE FILE `demo_abromics.yaml:23`; `input_fields/metadata_schema_input_fields.yaml:4`], and the recipe removes the missing ids by a visible step at the start of its join (`polars_drop_nulls` on `sample_id`, [RECIPE FILE `demo_abromics.yaml:44-47`]), so its join has 27 rows. The metadata's own tier 1 is empty, so the table `metadata_schema` still holds the 3 lines. So the note has two cases: where the recipe removes them by such a step it says "3 lines of the metadata have no id; the recipe removes them in <join>, step 1" (information); where it does not, it says "It is better to fix this: otherwise they count as entities with no result." The check finds the step by reading the recipe for a `polars_drop_nulls` with the id in `subset` (a match on plain text of the step); a removal written another way (for example a `modif_filter` on the id) is not recognised, and the note then gives the general sentence. Her order of D-0569 reads "remove the null and empty rows from the metadata"; that these three lines are a deliberate lesson was put to her after it (channel block M624): her choice, a dry-run candidate (D-0525).

## Her answers of 2026-11-23, third part (ledger D-0572): the control of the ids

**Her words, exact** (channel block M627): "1. yes we need a control of ids - as we started to implement - warnings in case something was wrong in the metadata so the user can recheck (as was planned recently) - if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done, if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) that would - that would be clear and mentionned both in literature and allerts. for the missing ids - but this might be before T1 a step the app does ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe)". [HER WORDS D-0572] And, on the facts: "4. this is true that is why the ids of both metadata and data sets should overlapp (or at least all in metadata and included for data sets) 5. true that is why metadata should be clean - all with an id ...".

**The control, as she said it, with the data check's note for each.**
- **(a) An id in a result file and in no metadata.** The data check informs, through the new channel, and tells the user to fix it ("the user must add the ID and update metadata"); she prefers the metadata corrected. The alternative she names, a marker "not in metadata": the lines stay, a yes/no column marks them; the note is the same. On the demo: none (0 in every file); the template `left_join_lesson` has 2, by design.
  > **Update of 2026-11-23 (ledger D-0573; her D-0579):** this is check X. Her flow: inform, list the ids; the user adds them to the metadata by hand and uploads it again; the verification starts again; an unknown or false id may be added with a dummy fill and a note to remove it afterwards. There is no marker "not in metadata" in her flow (the review session's reading, confirmed by her "yes"). Whether X stops the recipe (refuse) or only informs (D-0569 (b)) is her question 1 of the new list. The sentence "she prefers the metadata corrected; the alternative she names, a marker "not in metadata"" is history.
- **(b) An id in the metadata and not in a result file.** An automatic completion at the first step, said in the documentation and in the alerts (words PROVISIONAL): "N lines added to <table> from the metadata (ids ...), marked <marker>. The app cannot tell whether they were analysed with nothing found or not analysed; the recipe says how they are counted." On the demo: 4 lines added to ResFinder. This is her proposal B6; where the completion lives is her open question (see `CAUSE_AND_SOLUTIONS_ZEROS.md`, the section of D-0572). Until B6 is chosen the note is the one decided before: "N entities of the metadata have no line in this file".
  > **Update of 2026-11-23 (ledger D-0573, D-0574, D-0575, D-0576):** this is check Y. Her words: "warn and include those present in metadata to original data - with the specific marker "not in original data"", with the user's confirmation noted in the log, once per data batch, in a separate log, also in the export. The completion lives in the recipe, required on every result table (D-0574). The marker is called "not in original data" and is not a zero. The alert words below are provisional and are replaced by a confirmation dialog (words open).
- **(c) Metadata lines with no id.** The metadata should be clean ("all with an id"): the third note, "N lines of the metadata have no id", stays; the completion adds only ids that exist. On `demo_abromics` the three lines are there on purpose; her sentence points to a clean metadata, to confirm in the dry run (D-0525).
  > **Update of 2026-11-23 (ledger D-0573):** "informs" is replaced by "refuses". Her words: "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)".
- **(d) An id repeated in the metadata** (proposed, not raised by her): "an id is repeated in the metadata: <ids>". It multiplies the rows of a join with the metadata second. The demo's metadata has none (42 rows, 42 distinct ids).
  > **Update of 2026-11-23 (ledger D-0573):** a repeated id may be an error at the id level (her question 2 of the new list: refuse or note); her approved sentence (D-0567, RECIPES G4) allows a repeated id in a long table, and nothing yet says that the metadata has one row per entity.
**The risk:** "it knows the risk it accepts" [HER WORDS D-0572] (our reading: "it" is the recipe maker): the app cannot tell "not analysed" from "analysed, nothing found"; the notes say so.

## Her answers of 2026-11-23, fourth part (ledger D-0573 to D-0576, her D-0579): the two checks, the refusal of the metadata, the confirmation

Added after the file was signed; the signed text above is kept. Checked by the Opus agent (`OPUS_checks_review_v1.md`). Her words are in the section "Added 2026-11-23 (ledger D-0573 to D-0579)" of `CAUSE_AND_SOLUTIONS_ZEROS.md`; the lines this file needs are:

- "We need to fix the metadata - it must not contain errors nor missing data. A rule." [HER WORDS D-0573]
- "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id) - A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)" [HER WORDS D-0573]
- Check Y: "warn and include those present in metadata to original data - with the specific marker "not in original data"". Check X: "inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start : if the user does not know this id or its false it can add it temporaly and fill with dummy fill and say I need to remove those ids afterwards" [HER WORDS D-0573]
- "it might be more logical to have test 2 as the first test .... stopping first no ?" [HER WORDS D-0579]

**The control of the ids, as she said it, with the data check's note for each** (words of the notes PROVISIONAL). The order, whatever she decides on the stop (her question 1): (0), then X, then Y.

| Step | What it checks | What the user sees | What the check does |
|---|---|---|---|
| (0) The metadata's own ids | an id empty (after the null words), a cell of spaces, a repeated id (question 2) | "The metadata file <name> has N lines with a missing id (file lines <...>)" | **refuses** the metadata (where: at the opening, in Data Import, or both: question 3); the loop: correct and upload again |
| X | ids of the original data that are not in the metadata | "In <table>, N ids have no row in the metadata: <the ids, up to 20>. Add them to the metadata and upload it again. If you do not know an id, or it is false, you may add it for now with a dummy fill and note that it must be removed afterwards." | informs, or stops (her question 1); no marker "not in metadata" |
| Y | ids of the metadata that are not in the original data | "N ids of the metadata have no line in <table>: <the ids>. They will be added to <table>, marked "not in original data". The app cannot tell whether they were analysed with nothing found or not analysed. Confirm?" | asks the user's confirmation, once per data batch; records it in the log; completes after the confirmation (without one: question 4) |

**On the demo.** (0): the metadata has 42 lines and 42 distinct ids, none empty: it passes; `demo_abromics` as shipped has 3 lines with no id (file lines 5, 6, 11): refused until its file is corrected by the dry run (D-0525). X: 0 ids in every demo result file; `left_join_lesson` has 2 (`ACC0001`, `ACC0002`). Y: ResFinder has lines for 38 of the 42 metadata ids, so 4 have none; every other result file has all 42 [ESTABLISHED: OVERLAP section 1].

**What the code does today and what has to be built.** [TODAY] Nothing compares the ids of two tables; the data check builds each table alone after tier 1 [CODE READ `data_analysis_recipe_validator.py:485-545`]; Data Import checks a candidate file by the ingestion's own read, all files or none, and compares no ids [CODE READ `data_import_check.py`]; the gate rejects on a problem and never on an advice [CODE READ `bootloader.py:431-451`]. [TO BUILD] the check of the metadata's ids as read, the refusal, checks X and Y, the confirmation, the log. She wrote "the code is not build yet" [HER WORDS D-0573].

**Two points that concern this file.** (1) D-0569 chose option (b), "only inform", for the ids of a result file with no metadata row. Her new rule refuses a metadata with errors at the id level, and D-0579 asks "stopping first". If X stops the recipe, D-0569 (b) is reversed for X: her question 1. (2) The agents propose to check the metadata as read (before its tier 1): a step in the metadata's own tier 1 (for example a `polars_drop_nulls` on the id) would hide the error from a check run after it. In `demo_abromics` that step is in its join's tier 1 (`demo_abromics.yaml:44-47`; the metadata's own tier 1 is empty, `:30-31`), so it would not hide it.

## Open between the two agents

None.

**Signed by both agents: Sonnet (this file) and Opus (OPUS_checks_overlap_v1.md and OPUS_signs_overlap_v2.md, replacements O1 to O7 and P1 to P4: O1 option (a) blocks her second remedy, O2 D-0050, D-0568 and D-0543 quoted where they bear, O3 D-0564 exact, O4 (a2) and (c) named apart, O5 "analysed" is relative to one analysis, O6 the retest needs a never-analysed entity, O7 the correction of the committed cause file; all replacements applied)**; D-0569 section checked by the Opus agent (OPUS_checks_b3_v1.md, replacements Q1 to Q6); D-0570 additions: Sonnet (this file) and Opus (OPUS_checks_notdetected_v1.md, replacements R1 to R32 applied); D-0572 additions: Sonnet (this file) and Opus (OPUS_checks_b6_v1.md, R1 to R26 applied)

**D-0573 to D-0579 additions and the review:** Sonnet (this file) and Opus (`OPUS_checks_review_v1.md`, S1 to S18 applied).
