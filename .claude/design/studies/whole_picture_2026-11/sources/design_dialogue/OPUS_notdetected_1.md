# Opus blind position: "a true not-detected is a true result" (ledger D-0570), 2026-11-23

**What this is.** My position on the owner's order relayed in channel block M624 and recorded as ledger D-0570, written BLIND: I have not opened the Sonnet agent's file. Reading and reasoning only, NO RUN (D-0566; the bracket of D-0570: "the investigation is reading and reasoning only, no run"). The case: count the entities of the population that have no detection, as a true result. It is to be merged, after the two agents agree (D-0552), into the ONE list of the question A to E + B2/B3 of `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md`. Nothing is chosen for her; leans are marked as leans. Data agnostic: "the entity" (the sample on the demo), "result table" (a table of analysis results, for example ResFinder).

**Tags.** [HER WORDS D-n] / [RECIPE FILE] / [RULE FILE] / [CODE READ file:line] / [ESTABLISHED: file, point] (earlier runs or counts, committed in the study files) / [HAND COUNT] (CAUSE file) / [POLARS SEMANTICS] (the library's documented behaviour as I know it; not run here) / [REASONED, not run].

**Flags first (her rule: anything that changes a result without saying so).**
- In her two routes, a removal of an entity BY KEY written at the result table's own place makes that entity count as "not detected": with D-0570 this is no longer only a false zero, it is a false RESULT (one more entity "not detected"), and today no sentence warns (the sentence "can remain" is PATHS Q6, not built). Section 1 F1, sections 3 A and E2.
- With an anti-join, a removal at the result table ADDS the entity to the table of the not-detected. Section 3 E2.
- With the metadata first, an entity of the metadata that was never analysed for this result counts as "not detected", without a message (the data check's note is decided, not built). This is the risk she gave herself as the reason for "the metadata should be the right table" [HER WORDS D-0549: "some users will have metadata for more samples"]. Section 3 A.

---

## 0. Her words, and my reading

Her words [HER WORDS D-0570], exactly: "I think there is a bit of logical problem and that will depend on the join type we use with the metadata AND what a no result means. I do not understand what you mean by "metadata second keeps the zeros" the metadata itself should have id with non empty lines. But if results are 0 as no gene found for example then we should be able to complete the table - this can be done in the recipe but the problem we need the ids that were in metadata and are not in the data table - where we go back to your population example. So we need to have results for the initial population and information about what 0 or missing means." and "I think the data check information as suggested. And true not detect is a true result - So if we need eg. to see how many samples are not detected I need to make a later anti-join (which I would avoid as much as possible) or a join where metadata is on the left side ...and fill the blanks in the recipe ... can we investigate possible solutions for this case ? 4. yes the validated question - yes . information is very important here."

My reading (mine, not hers):
- **R1, results for the initial population:** one result line for every entity of the initial population. In her words the population is "the ids that were in metadata"; "the metadata itself should have id with non empty lines" [HER WORDS D-0570], which I read as one non-empty id per metadata line (as her order of D-0569: "remove the null and empty rows from the metadata").
- **R2, what 0 or missing means:** for every 0 and every missing value of a result, the information of what it means.
- **The case:** a non-detection is a result and must be countable ("how many samples are not detected").
- **Her two routes:** (i) a later anti-join, to avoid as much as possible; (ii) the metadata on the left side and the blanks filled in the recipe.
- **Open in D-0570:** "NOT decided: which solution; what 0 or missing means per result table and where it is declared."

---

## 1. Five facts that frame every candidate

**F1. A "not detected" is a result only for an entity that was analysed.** For ONE result table an entity of the population is in one of these states [REASONED]:
- s1 detected;
- s2 analysed, nothing found: her true not-detected;
- s3 not analysed (or the analysis failed for it);
- s4 removed BY KEY by an audit step written at the result table's own place (not a result: the user excluded the entity);
- s5 removed at the join place or everywhere ("Remove from all the data", D-0416): gone from the result.
A filter ON VALUES (for example a stricter identity threshold, by the recipe or by an audit step with its reason) that leaves an entity with no line makes it s2 under that threshold: a true not-detected, by the definition of the analysis. Only the removal by key (s4) is a false not-detected. [REASONED]

**F2. In the demo files a result table lists findings only.** ResFinder: 70 lines for 38 entities; 4 entities of the metadata (42) have no line. [ESTABLISHED: OVERLAP_AND_POPULATION.md task 1] So "no line" is s2, s3 or s4, and neither the table nor the app can tell which: the core fact of the zeros [ESTABLISHED: CAUSE_AND_SOLUTIONS_ZEROS.md, "The core fact"]. Who can tell: the pipeline that made the file (s2 against s3: B3); a table that lists the analysed entities (s2 against s3: B2); the author, for a whole table at once (C1, new, section 3); the audit record (s4: the app wrote the step).

**F3. The demo already answers "how many samples are not detected", by her route (ii).** The plot `qa_amr_genes_per_sample` counts the 42 samples by their number of AMR genes (`x: n_amr_genes`, `geom_bar`); the bar at 0 holds 4. [RECIPE FILE `plots/qa_amr_genes_per_sample.yaml`: subtitle "Expect 42 samples: 4 with 0 genes, 70 genes in total"; description "T2 has one row per sample (42)"] Its 4 are "no line in ResFinder": s2 or s3; the plot does not say which.

**F4. Where today's audit writes.** HOME writes an audit step at the plot's own table (T3) [RULE FILE `ui_implementation_contract.md` section 2: "Today an audit step is written at T3 of the plot"]. For this plot T3 equals T2 of `QA_AMR_per_sample` (the plot has no tier-3 steps; D-0343). A removal by key there takes the entity's line out of the per-entity result: no false not-detected. The false not-detected comes with the earlier places (decided, not built: D-0316 to D-0318, D-0337) when the user picks the result table's own place. [REASONED]

**F5. The aggregate decides whether an entity with no line gets 0 or missing.** After a left join from the metadata, an entity with no line has one row with empty result columns:
- a count of non-empty values (`pl.col('gene').count()`) gives 0 [RECIPE FILE `QA_AMR_per_sample_tier2.yaml`, its comment "a sample without a gene gets 0, not 1"; ESTABLISHED: 4 at 0];
- a count of rows (`pl.len()`) gives 1 [ESTABLISHED: CAUSE (iii)]; the demo's `ResFinder_wrangling_tier2.yaml` uses `pl.len()` [RECIPE FILE];
- a sum gives 0; a mean, minimum, maximum or standard deviation gives missing [POLARS SEMANTICS];
- so one absent entity is 0 in one column and missing in another, and a fill of 0 on a mean writes a value that was never measured. [REASONED]

---

## 2. The join kind changes the result (her words: "that will depend on the join type")

M = the metadata (42 entities), R = ResFinder (70 lines, 38 entities). "B3 files" = R with 4 more lines, one per entity analysed with nothing found, gene empty (the catalogue's B3). Rows marked ESTABLISHED were counted; the others are [REASONED from the join's semantics, not run].

| The join (first table, kind) | What the result holds, today's files | Not detected countable? | With B3 files | Followed by the audit today |
|---|---|---|---|---|
| M left R | 74 rows, 42 entities; the 4 come from M with empty R columns [ESTABLISHED: 74 rows] | yes (0), but s2 = s3 = s4 | 74 rows; the 4 come from their own lines; s2 against s3 needs a column that says "has a line" (B3P) | yes (left) |
| R left M (data first) | 70 rows, 38 entities | no: the 4 are absent | 74 rows, 42 entities; the 0 is counted from the lines; s3 and s4 are absent | yes (left) |
| M inner R, R inner M | 70 rows, 38 entities | no: "an inner join would hide this" [HER WORDS D-0568] | 74 rows, 42 entities | yes (inner) |
| R right M | as M left R (M is the kept side); the key column and the order not judged [catalogue (e)] | yes, as M left R | as M left R | no: not YET followed (D-0452) |
| M full R, R full M | as M left R while R is inside M (her contract, D-0568); Polars keeps both key columns for a full join unless told to merge them [POLARS SEMANTICS] | yes | as M left R | no: not YET followed |
| M semi R | 38 rows: the detected entities, M's columns only | the complement only (42 minus 38 is not a recipe step) | 42 rows: semi then means "has a line" | yes (semi, D-0486) |
| M anti R | 4 rows: the entities with no line, M's columns only [POLARS SEMANTICS] | yes, in a table of its own | 0 rows on the demo: it then lists s3 (not analysed), not s2 | no: not YET followed |
| a cross join (entity x target) | the full grid for "not detected per target" (for example per gene) | per target | per target | no: not YET followed |

What this shows: the same files give 0, 1, missing, absent or a separate table, depending on the join kind and the aggregate; and with B3 files the anti-join changes meaning (from "no line" to "not analysed").

---

## 3. The candidates (one list; old letters kept, new ones marked NEW)

Each entry: the author writes; the user sees (on the demo, by reading); the audit (default place at the join, D-0549; the result table's own place; the metadata's place; today's T3); prevents and does not; the check that would help; the false not-detected; what it asks of the pipeline or the files; today; reopens (information); a run after her choice.

The entity used in the examples: `10668076`, 1 ResFinder line (gene `blaTEM-1C`) [HAND COUNT, CAUSE file].

### A. Her route (ii): the metadata on the left, the blanks filled in the recipe (today's demo)

**The author writes.** Today's `QA_AMR_per_sample`: the metadata first, a left join with ResFinder, tier 2 groups by the entity and counts the non-empty genes [RECIPE FILE]. With a count of non-empty values no fill is needed: the 0 is counted (F5). A fill is needed when the per-entity value comes from elsewhere (a count made before the join, option B) or for a label. To count the not-detected as a result, one step (fragment, not run):
```yaml
# tier 2 of QA_AMR_per_sample, after the group_by
- action: polars_with_columns
  named_exprs:
    detected: "pl.col('n_amr_genes') > 0"
```
and a plot with `x: detected` and `geom_bar` (two bars). The existing plot already shows the 4 as its bar at 0.
**The user sees.** 4 not detected. What the 4 mean (s2 or s3) only in the author's words; today's subtitle says "4 with 0 genes", not "not detected".
**The audit.** At the join place `T1:QA_AMR_per_sample` (the default, D-0549): `10668076` is gone [ESTABLISHED: PATHS G8, RECIPES G6]; 41 samples, the bar at 0 still 4 [REASONED: the entity had 1 gene]. At `T1:ResFinder` (the result table's own place): it stays with 0; the bar at 0 holds 5: a false not-detected [ESTABLISHED: PATHS G8 "1 row"; HAND COUNT 1 to 0]. At the metadata's place: gone. At T3 (today): gone.
**Prevents:** an entity with no line disappearing. **Does not prevent:** s3 counted as not detected; s4 counted as not detected.
**Check that would help** (none built): an advice of the recipe check when a per-entity value after a left join from the metadata counts rows (`pl.len()` gives 1 for an entity with no line, F5), and when a fill of 0 targets a column made by a mean, minimum or maximum [REASONED]; the data check's note in the other direction (decided, not built: D-0569, D-0570): "4 entities of the metadata have no line in ResFinder: <ids>. The app cannot tell whether they were analysed."
**False not-detected:** yes, at the result table's own place (she accepted the false zero in D-0569; with D-0570 it is counted as a result).
**Asks of the pipeline or files:** nothing; it assumes that every entity of the metadata was analysed for this result, which only the pipeline knows.
**Today:** accepted and run (the demo).
**Reopens (information):** D-0564 ("the join should not start with the medata or we need a solution we do not have yet"); she names this route herself in D-0570.
**Run after her choice:** none for the chain (established). For the `detected` column and its plot: 1. requirement: the step and the plot on a scratch copy of the chain; 2. expected: 38 true, 4 false; after a removal of `10668076` at `T1:ResFinder`: 37 true, 5 false; at the join place: 37 true, 4 false; 3. independence: a scratch recipe from the demo's schemas, steps written by hand, every table rebuilt in its own empty folder, no lineage code.

### E2 (NEW as its own line; was a sentence of (e)). Her route (i): an anti-join

**The author writes** (fragment, not run). A joined table of its own; a plot counts its rows:
```yaml
joins:
  QA_AMR_not_detected:
    ingredients: [{dataset_id: metadata_schema}, {dataset_id: ResFinder}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: ResFinder, 'on': [sample_id], how: anti}
```
**What it needs today.** The kind `anti` is in the action's list [CODE READ `polars_calls.py:85`: inner, left, right, full, semi, anti, cross]. A join is allowed only in tier 1 [CODE READ `recipe_check.py:714-715`, ST05] and a join reads the tier 1 of each ingredient [CODE READ `orchestrator.py:269-294`, `prepare_ingredient` takes the schema's `tier1` steps]. So a LATER anti-join cannot be written: not after an aggregation, and not against a result table's tier 2 (for example a threshold applied there). With the metadata, a join after tier 1 goes against D-0510 ("join with metadata must be done at T1"); with any other table it is her question 27. No action appends rows (no union or concat) [ESTABLISHED: catalogue (e)]: the not-detected stay in a table of their own, and the detected and the not-detected cannot become ONE result for the initial population (R1).
**The user sees.** A table of 4 entities with the metadata's columns only [POLARS SEMANTICS: an anti join keeps the first table's columns].
**The audit.** The audit cannot YET follow an anti join [HER WORDS D-0452: "App cannot YET describe (or follow? )"; CODE READ `step_effects.py:73` `NOT_YET_FOLLOWED_JOINS`]; a place behind it is red and not tickable [D-0460]. And it INVERTS a removal: a removal of `10668076` at `T1:ResFinder` ADDS it to this table (5 rows) [REASONED]. At the metadata's place or at this table's place: removed. The sentence "covers k of n paths: the entity can remain" (PATHS Q6) would be wrong here; the dialog would have to name the kind.
**Prevents:** a fill; a per-entity table that starts from the metadata. **Does not prevent:** s2 = s3 = s4. With B3 files it lists s3 (not analysed), not s2: its meaning changes with the files.
**Check that would help:** an advice that the audit cannot YET follow this kind (decided as an advice in D-0452; no such text in `recipe_check.py` today [CODE READ]).
**False not-detected:** yes, and by addition.
**Asks of the pipeline or files:** nothing.
**Today:** the step's form accepts the kind (`polars_calls.py:85`); not run here.
**Reopens (information):** D-0452, D-0460, D-0486 ("The documentation should NOT recommend those joins"); for "later": D-0510 and question 27.
**Run after her choice:** 1. requirement: the table above on a scratch recipe; 2. expected: the recipe check passes it; 4 rows, the metadata's columns only; after a removal of `10668076` at `T1:ResFinder`, 5 rows; 3. independence: as A.

### B. Count per entity first, then the metadata first (unchanged)

For this case: as A (42 entities, 4 at 0 after `polars_fill_null`), with no multiplication of rows. Same false not-detected at the result table's own place (here the count table's place) [ESTABLISHED: Opus RR4]. Nothing new.

### B2. A table of the analysed entities first, the metadata second (a2; unchanged)

For this case: the not-detected are counted among the analysed entities only (s2 for that analysis); s3 is absent. R1 is met only when every entity of the metadata was analysed. False not-detected at the result table's place: yes (the base still holds the entity). Asks a table that lists the entities of THIS analysis (a manifest). On the demo the same 4 (`FastP` holds 42 of 42) [ESTABLISHED: Opus RR13].

### B2P (NEW as an option; was (f2)). The metadata first, then a table of the analysed entities: the initial population in three states

**The author writes** (fragment, not run; `AMR_manifest` is a table with one row per entity the analysis ran on; its tier 1 stamps `analysed: pl.lit(True)`; `ResFinder_per_entity` is the count table of option B):
```yaml
joins:
  AMR_per_entity:
    ingredients: [{dataset_id: metadata_schema}, {dataset_id: AMR_manifest}, {dataset_id: ResFinder_per_entity}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: AMR_manifest, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_join, right_ingredient: ResFinder_per_entity, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_fill_null, columns: [analysed], value: false}
        - action: polars_with_columns
          named_exprs:
            amr_result: "pl.when(~pl.col('analysed')).then(pl.lit('not analysed')).when(pl.col('n_amr_genes').fill_null(0) == 0).then(pl.lit('not detected')).otherwise(pl.lit('detected'))"
```
**The user sees.** Three bars: detected 38, not detected 4, not analysed 0 on the demo (with `FastP` as the stand-in manifest, 42 of 42). An entity of the metadata never analysed would be "not analysed", not "not detected".
**The audit.** A removal at ResFinder's (or the count table's) place: the manifest still says "analysed": "not detected" (false). At the manifest's place: "not analysed" (s4 shown as s3). At the join place: gone.
**Prevents:** s3 counted as not detected. **Does not prevent:** s4 at the result table's place.
**Check that would help:** the data check: every entity with a line in a result table is in the manifest (an entity with a line but not in the manifest means the manifest is incomplete) [as OVERLAP task 3].
**Asks:** a manifest of the analysis; a status column in it (ok, failed) would add the state "analysis failed".
**Today:** its parts are accepted and run (left joins, a fill, `polars_with_columns`); the whole chain is not run.
**Reopens (information):** D-0564 (the metadata first).
**Run after her choice:** 1. requirement: a scratch metadata with one entity that is in no manifest, and the chain above; 2. expected: detected 38, not detected 4, not analysed 1; after a removal of `10668076` at the count table's place: not detected 5; 3. independence: as A.

### B3. The result files list every analysed entity; the data first, the metadata second (unchanged, read for this case)

For this case: the not-detected are COUNTED from the file (an entity whose lines all have an empty result: `gene.count()` 0), with no fill; a removal at the result table's own place removes the entity's lines, also the empty-result line: gone, no false not-detected [ESTABLISHED: catalogue B3 (vi)]. R1 is met only when every entity of the metadata was analysed; the others (s3) are absent, which the data check's note says. The not-detected count as its own result: the same `detected` step as A, in the per-entity table. Asks: the files, with an explicit mark read by the recipe (both agents' lean in D-0569's round); the recipe's own steps that stamp or count rows must be adapted [ESTABLISHED: catalogue B3 (iii)].

### B3P (NEW). The same files, the metadata first, a column that says "has a line", and NO fill for an entity with no line

**The author writes** (fragment, not run). The demo already stamps every ResFinder line (`status: pl.lit('Detected')` [RECIPE FILE `ResFinder_wrangling_tier1.yaml`]); with B3 lines the stamp says what the line holds. (An explicit column written by the pipeline can replace the stamp.)
```yaml
# ResFinder tier 1
- action: polars_with_columns
  named_exprs:
    status: "pl.when(pl.col('gene').is_null()).then(pl.lit('Not detected')).otherwise(pl.lit('Detected'))"
# QA_AMR_per_sample tier 1: unchanged (the metadata first, a left join), its polars_select keeps `status`
# QA_AMR_per_sample tier 2
- action: polars_group_by
  by: [sample_id, country]
  maintain_order: true
  named_aggs:
    n_amr_genes: "pl.col('gene').count()"
    has_line: "pl.col('status').is_not_null().any()"
- action: polars_with_columns
  named_exprs:
    amr_result: "pl.when(~pl.col('has_line')).then(pl.lit('no result')).when(pl.col('n_amr_genes') == 0).then(pl.lit('not detected')).otherwise(pl.lit('detected'))"
```
The plot must show the state (`x: amr_result`), or the count must be made missing for "no result"; otherwise the histogram puts a removed entity at 0 again (F5).
**The user sees** (B3 files with the 4 empty-result lines): detected 38, not detected 4, no result 0. After a removal of `10668076` at `T1:ResFinder`: detected 37, not detected 4, no result 1. At the join place: 41 entities.
**Prevents:** s4 counted as not detected: the only form with the initial population in which a removal at the result table's own place gives "no result", not a false result. s3 counted as not detected: s3 is "no result".
**Does not prevent:** s3 and s4 look the same ("no result"); the audit record can name s4 (C1).
**With today's files (no B3):** detected 38, not detected 0, no result 4: honest, but the 4 true not-detected (if they were analysed) are not counted; turning "no result" into "not detected" is a statement of the author (C1) or a fill, and the fill brings the false not-detected back.
**Check that would help:** the data check counts, per result table, the entities whose lines all have an empty result, and the entities of the population with no line.
**Asks:** B3 files. The other tables that read ResFinder's `status` change with it (as B3 already says).
**Today:** its parts are accepted and run (a `when` expression, a group_by, a left join); the whole chain is not run.
**Reopens (information):** D-0564 (the metadata first), as A.
**Run after her choice:** 1. requirement: a scratch ResFinder file with the 4 empty-gene lines, the chain above; 2. expected: 38 / 4 / 0; after a removal of `10668076` at `T1:ResFinder`: 37 / 4 / 1; the empty cells read as missing, not as an empty text (CAUSE (iii)); `is_not_null().any()` accepted in `named_aggs`; 3. independence: as A.

### C1 (NEW form of C). The recipe says, for each result table, what an entity with no line means

**The author writes** (invented; refused today as an unknown key, D-0033; the name and the words are placeholders):
```yaml
data_schemas:
  ResFinder:
    absent_entity_means: nothing_found    # or: not_analysed (B3 files); unknown when not written
```
A per-column form for an empty cell (`input_fields: gene: {..., empty_means: nothing_found}`, invented) would cover "what missing means" inside a line.
**What the app could do with it** (none built):
1. The data check's note (D-0570, in HOME, Data Import and BLUEPRINT's Validate): "4 entities of the metadata have no line in ResFinder: <ids>. The recipe says this means: nothing found."
2. The recipe check: `not_analysed` with a fill of 0 on a count made from that table: an advice ("these zeros are entities the recipe declares not analysed"); `nothing_found` with a per-entity result that starts from the data table: an advice ("the entities with nothing found will not appear").
3. The audit dialog, at the result table's own place: "After this step, `10668076` counts as nothing found (0) in `QA_AMR_per_sample` and stays in the plot `qa_amr_genes_per_sample`. To take it out of the result, write the step at `QA_AMR_per_sample`." (information; the default place of D-0549).
4. **A filled zero against a counted zero (the order's question): yes, per entity, as information.** The app computes which entities of the population have no line in the result table (the data check's set) and knows the removals it wrote (the audit record); so for each 0 it can say "counted from lines", "no line: nothing found, as the recipe says", or "removed by your step at ResFinder". The TABLE still cannot carry it (core fact) unless a column does (B3P), and the plot still shows the removed entity at 0.
5. The export report: a methods sentence ("entities with no line in ResFinder are counted as nothing found, as the recipe states").
**What it cannot do:** check that the statement is true; change the table. A rule that would also write the removal at the join place puts two places on one path [against HER WORDS D-0553: "the user chooses at most one place"].
**Asks:** the author must know what absence means (from the pipeline's documentation).
**Reopens (information):** no decision; a new key of the format. It answers the open point of D-0570: "what 0 or missing means per result table and where it is declared".
**Run after her choice:** the recipe side, once the key exists: a check run on a scratch copy; the app side cannot run before it is built. No run now.

### C2 (was C). The recipe or the app completes from the declared population

As the catalogue's (c) and (f3). With C1 the app would know which rows it completed and could mark them; keeping removed entities out of the completion would be a new rule (hers). The population: `entity.population`, today only checked (E02) [CODE READ `recipe_check.py:332-348`]; `population: metadata_schema` would pass E02 on the demo, because the check counts the metadata among the tables [CODE READ `recipe_check.py:351-358`] and the demo's metadata marks its key [RECIPE FILE `input_fields/metadata_schema_input_fields.yaml` line 6: `is_entity_key: true`]. No demo recipe declares an `entity` block [ESTABLISHED: OVERLAP task 3].

### The declared population, in her frame

"The initial population" is what `entity.population` names: "the id of the table with one row per unit" [ESTABLISHED: OVERLAP task 3]. It is the reference of R1 in every form and of the data check's note in the other direction. If it is the metadata (her words: "we need the ids that were in metadata"), the forms that meet R1 are A, B, B2P, B3P, C2, E. If it is a manifest of the analysis, B2 and B3 meet it. The declaration itself completes nothing. [HER WORDS D-0569: "Ok for the population anchor - as long as we can compute its fine"]

### D and E (unchanged), read for this case

- **D (no zeros):** the not-detected cannot be counted in a table; only in words (a caption, or the data check's note).
- **E (a right or full join, the metadata second):** the same results as A (the metadata's rows are kept), the same false not-detected; not YET followed by the audit (D-0452). A full join may keep two key columns [POLARS SEMANTICS; to check in its run].

### Other forms found

- **Per target** ("how many samples carry no `blaTEM-1C`"): another result; it needs the grid entity x target (a cross join, not YET followed, or a pivot of the table that starts from the metadata). Not studied here.
- **A manifest with a status column** (ok, failed): adds "analysis failed" as a state (B2, B2P).
- **The thresholds:** a not-detected is relative to the analysis and its thresholds; the demo writes such thresholds in a comment of `Detailed_summary` ("Filtered by % identity > 90 and % overlap > 85") [RECIPE FILE, recipe line 56]. A label or description can say it: part of R2.
- **A second reading of the metadata file as a "population" data table** (her reimport rule, D-0556): not a solution; it is the metadata under another name.
- **A semi join** gives the detected list (38); the not-detected count as 42 minus 38 is not a recipe step.

---

## 4. The one list (my proposal for the merge)

The question becomes two parts: the FORM of the result (one choice), and whether the recipe DECLARES what "no line" means (C1, with any form).

| Option | Who says what "no line" means | Population shown | Not detected counted in the result | A removal by key at the result table's own place | Asks of the files | Today | Run after her choice |
|---|---|---|---|---|---|---|---|
| A (her route ii) | the author's words only | initial (metadata) | yes, 0 (s2 = s3) | counted as not detected (false) | nothing | runs (demo) | only the `detected` column |
| B | the author's words only | initial | yes, after the fill | counted as not detected (false) | nothing | parts run | as catalogue |
| B2 | a manifest | analysed only | yes, for the analysed | counted as not detected (false) | a manifest | parts run | as catalogue |
| B2P (NEW) | a manifest | initial, 3 states | yes | counted as not detected (false) | a manifest | parts run | yes |
| B3 | the files | analysed only | yes, counted from lines | gone (no false) | files with every analysed entity | parts run | as catalogue |
| B3P (NEW) | the files | initial, 3 states | yes, counted from lines | "no result" (no false) | the same files | parts run | yes |
| C1 (NEW, with any form) | the recipe, read by the app | as its form | as its form | as its form; the app NAMES it | nothing | not built | after it exists |
| C2 | the recipe or the app | initial | yes, completed | counted as not detected unless a new rule | nothing | not built | as catalogue |
| D | nobody | entities with a line | no (words only) | gone | nothing | runs | as catalogue |
| E | the author's words only | initial | yes | counted as not detected (false) | nothing | not run | as catalogue |
| E2 (her route i) | nobody | the not-detected only, separate table | yes, as rows of another table | ADDED to the table (false) | nothing | form accepts it | yes |
| Neither | | | | | | | |

---

## 5. "Metadata second keeps the zeros": where it stands, and the correction

- **What she quotes** is the review session's sentence to her; the bracket of D-0570 records that it "was wrong as written".
- **In the study files** the nearest sentence is option B3 of the question, `CAUSE_AND_SOLUTIONS_ZEROS.md` line 59: "Then the data first and the metadata second keeps the zeros, a removal at the data table's own place removes the entity completely (no false zero), and no join starts from the metadata." It holds only under the condition stated just before it (B3: the result file has a line for every analysed entity); read alone it says the opposite of what a left join does. The same idea is correct as written in B3 (vi) (line 218) and in (a2) (`OVERLAP_AND_POPULATION.md` lines 31 and 125: there the first table is the table of the analysed entities).
- **Proposed replacement at line 59:** "Then the result file itself has a line for every analysed entity, so a join with the result table first and the metadata second (`left`) keeps those entities and their counted 0: the rows come from the result file, not from the metadata. Without B3, the result table first and the metadata second keep only the entities that have a line: an entity with no line is absent, and there is no 0."
- **For her half page, one sentence:** "Correction: 'metadata second keeps the zeros' was wrong as written. With the data table first, an entity with no row in the data table is absent; a zero stays only if the result file already has a row for it (B3). The metadata never adds a row when it is second in a left join."

## 6. Other corrections found while reading (for the merge)

- **"42 bars".** `CAUSE_AND_SOLUTIONS_ZEROS.md` lines 47, 53, 59, 62, 220, 291 and `OVERLAP_AND_POPULATION.md` line 31 count the plot's "bars". The plot counts samples by their number of genes (`x: n_amr_genes`, `geom_bar`) [RECIPE FILE]: "42 bars" should read "42 samples counted, 4 of them in the bar at 0"; "41 bars" should read "41 samples"; "38 bars" (line 291) should read "38 samples, no bar at 0".
- **The join kinds in the step's form.** Catalogue (e), line 283, says the form lists `right` and `full` and the engine accepts `anti` and `cross` as well. The form lists all seven: inner, left, right, full, semi, anti, cross [CODE READ `polars_calls.py:85`]; `step_effects.py:73` names anti, right, full and cross as not YET followed.

---

## 7. What she may be missing (each with why, how she would see it, the alternatives)

1. **Her acceptance of the false zero (D-0569) and her new rule (D-0570) meet.** With "a true not-detected is a true result", a removal by key at the result table's own place turns an excluded entity into a result ("not detected") in A, B, B2, B2P, C2, E and E2. How she would see it: the bar at 0 grows by one. Alternatives: the default place at the join (D-0549); "Remove from all the data" (D-0416); the dialog's information (C1); or B3 / B3P, where the table itself avoids it.
2. **The metadata as the population assumes that every metadata entity was analysed.** Her contract (D-0568) is one direction (the result ids are in the metadata); the other direction is exactly s3. How she would see it: an entity never analysed shows "0 genes". Alternatives: B2P or B3P (a source that knows who was analysed), or C1 (the author states it, the app repeats it).
3. **A "later" anti-join is impossible today and, with the metadata, goes against D-0510.** It also splits the initial population into two tables (no union), the audit cannot YET follow it, and a removal at the result table ADDS the entity.
4. **The aggregate decides 0 or missing** (F5): a fill of 0 on a mean, minimum or maximum writes a value that was never measured; `pl.len()` counts an entity with no line as 1 (the demo's `ResFinder` tier 2 uses it).
5. **Per target is a different result** ("how many samples carry no gene X"): it needs the full grid, not covered by any form above.

## 8. Leans (as leans; nothing chosen)

- **Where the pipeline can write it: B3P**, with an explicit column written by the pipeline. Reason: it gives R1 (the initial population), a not-detected counted from the file (R2 for s2 against s3), and a removal at the result table's own place shows "no result", not a false result.
- **Where the files cannot change: A, or B2P where a manifest exists, together with C1**, and the default place at the join. Reason: C1 is the only form in which the app itself can say what each 0 or missing means, and name a zero made by the user's own removal.
- **C1 with every form**, because D-0570 leaves "what 0 or missing means per result table and where it is declared" open, and "information is very important here" [HER WORDS D-0570].
- **No lean for E2**, for the reasons of section 7 point 3; her own stance is to avoid it.

## 9. Runs after her choice (each registered before it runs, D-0561)

The three points are written in each entry: A (the `detected` column), E2, B2P, B3P; B, B2, B3, C2, D and E keep the catalogue's retest lines. Common independence: a scratch recipe from the demo's own schemas, steps written by hand, every table rebuilt in its own empty folder (D-0560), no lineage code (D-0558).

## 10. Open for the Sonnet agent

None yet: this position is blind. To compare: the states s1 to s5 and the value-filter note (F1); the join table (section 2); B2P, B3P, C1 and E2 as their own lines; the corrections of sections 5 and 6.
