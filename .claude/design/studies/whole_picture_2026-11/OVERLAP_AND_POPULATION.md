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
- `templates/left_join_lesson`: 2 ids of the `sequenced` file are not in the metadata (`ACC0001`, `ACC0002`). This lesson is written on purpose to show what a left join does when ids do not match (its description says so).
- `2_test_data_ST22_dummy` and `figshare_integration` declare no entity id. Read by the column name `sample_id` (not declared), their result files are all inside the metadata too.
- Two templates (`e_coli`, `simple_template`) have no data file in the repository; the other recipes have no metadata table.
- All counts are on the FILES, before the recipe's tier-1 steps; a tier-1 step that removes rows can change the ids of a table.

**The data check you approved** ("yes the app check could be good - to identify those that have no metadata - good idea"). The data check that exists already reads each table, but only one table at a time; it never compares two tables. A new part would list, for each result file, the ids that have no row in the metadata, with their count and the ids, and name your two remedies: upload the complete metadata again, or remove those ids from the data tables by an audit step. What it needs from the recipe: the entity id declared in both tables, and the metadata table. Your choices: does a violation refuse the recipe or only inform; where it is shown. Options (a) to (d) are in section 2, with what you would see. **One thing to know before you choose: if a violation refuses the recipe (option (a)), your second remedy cannot be used.** A refused recipe does not open in HOME, so the ids cannot be deleted there by an audit step. Nothing is chosen.

**Is the declared population a lever for the zeros? Partly.**
- **(a2) needs no new key; its parts run today, the whole chain is not run yet.** A table of the entities that were ANALYSED as the first table of the join (a data table), the counts next, the metadata second. Zeros appear for the analysed entities with no hit, the metadata's extra entities stay out (your reason in D-0549: "some users will have metadata for more samples so that will allow to join what really is in T1 without the extra in metadata"), and the join does not start with the metadata (D-0564: "the join should not start with the medata"). On the demo you would see the same 42 bars as today, because every metadata id is in `FastP` (42 of 42); the difference appears only with an entity that was never analysed.
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

## Open between the two agents

None.

**Signed by both agents: Sonnet (this file) and Opus (OPUS_checks_overlap_v1.md and OPUS_signs_overlap_v2.md, replacements O1 to O7 and P1 to P4: O1 option (a) blocks her second remedy, O2 D-0050, D-0568 and D-0543 quoted where they bear, O3 D-0564 exact, O4 (a2) and (c) named apart, O5 "analysed" is relative to one analysis, O6 the retest needs a never-analysed entity, O7 the correction of the committed cause file; all replacements applied)**
