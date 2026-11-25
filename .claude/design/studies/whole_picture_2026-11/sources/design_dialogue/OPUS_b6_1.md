# Opus blind position: her solution B6 (complete the data tables from the metadata, with a marker) and the control of the ids (channel block M627), 2026-11-23

**What this is.** My position on the owner's new answers relayed in the channel block "### M627 from sparmvet-viz-cb", written BLIND (I have not opened the Sonnet agent's file). Reading and reasoning only, NO RUN (D-0566). No study file is edited. The signed D-0570 section of `CAUSE_AND_SOLUTIONS_ZEROS.md` (commit 33e01ee0) is read in the main tree. Nothing is chosen for her; leans are marked as leans; data agnostic ("the entity", "the result table", "the population"; "samples" only for the demo's numbers).

**Tags.** [HER WORDS M627] (her words in the block, exact; no ledger number yet) / [HER WORDS D-n] / [RECIPE FILE] / [RULE FILE] / [CODE READ file:line] / [ESTABLISHED: file, point] / [POLARS SEMANTICS] (the library's documented behaviour; not run here) / [REASONED, not run].

**Flags first (things that would change a result without saying so).**
1. **With B6 and the demo's own steps unchanged, the 4 added entities become "Detected".** ResFinder's tier 1 stamps every line `status: pl.lit('Detected')` [RECIPE FILE `wrangling/ResFinder_wrangling_tier1.yaml`]; `ST22_Anchor` keeps `status` [RECIPE FILE `wrangling/ST22_Anchor_wrangling_tier1.yaml:11-14, 46-47`]; the plot `integration_plot` fills its tiles by `status` [RECIPE FILE `plots/integration_plot.yaml:5, 9`]. Today the 4 entities have an empty `status` there; with B6 they would show "Detected", with no error. [REASONED]
2. **ResFinder's tier 2 counts rows** (`total_gene_count: pl.len().over(['sample_id'])` [RECIPE FILE `wrangling/ResFinder_wrangling_tier2.yaml`]): an added line counts 1, not 0. [REASONED]
3. **A filter of the recipe in the result table's tier 1 and the completion before tier 1 do not agree.** An entity whose every file line is removed by a threshold filter of tier 1 has no line after it, while an entity with no file line at all keeps its added line: with the data table first, the first is absent and the second is "no result in file". [REASONED; section 3, P1 and P2]
4. **If the completion reads the metadata after its tier 1, the data table's first place lies below the metadata's place**: choosing both is then refused by her rule "the user chooses at most one place" [HER WORDS D-0553]. [REASONED; section 3, α and β]

---

## 0. Her words, and my reading

Her words, exact [HER WORDS M627]: "6. I think the solution would be to fill the data tables with the id contained in the metadata and have a "data file has no result" NA ? that can be then processed as a normal recipe - saying how those need to be processed in the recipe. Its a bit weird solution but it would work in all cases forcing the recipe maker to consider this case. and then missing data in the original files need to be processed correctly according to the correct meaning - which only a recipe maker (in collaboration with a real user) can decide. That would remove need for 6 anti join. and make decisions on how to procede with those clearn in the recipe so 7. All is clear and decided." Then: "1. yes we need a control of ids - as we started to implement - warnings in case something was wrong in the metadata so the user can recheck (as was planned recently) - if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done, if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) that would - that would be clear and mentionned both in literature and allerts. for the missing ids - but this might be before T1 a step the app does ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe) 2. we could need good marker convention - short and explicit - and I think it should be a different kind of other "missing value" because then the recipe maker has to consider those cases specifically and the 3. it knows the risk it accepts". Her answers to the facts (her points 2 to 5) are quoted where they are used.

My reading (mine, not hers):
- **B6:** every result table that has an entity id gets one line for each id of the metadata that the file does not hold; each added line carries a marker that says "the data file has no result for this id", a missing value of its own kind; the recipe then says how the marked lines are processed.
- **The completion is automatic** ("an automatic completion at (first step)"), and said in the documentation and in the alerts.
- **Where it lives is open** ("not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe").
- **The meaning of the marked lines is the recipe maker's**, with a real user; the app accepts the risk that it cannot tell "not analysed" from "analysed, nothing found" ("it knows the risk it accepts").

---

## 1. B6 on the demo, against the other options

**The demo.** The metadata holds 42 entities; every result table holds all 42 except ResFinder (38; 4 absent) [ESTABLISHED: OVERLAP_AND_POPULATION.md section 1, lines 46-55]. So B6 adds lines to ResFinder only: 4 lines, one per absent id, marked, with every result column empty. ResFinder grows from 70 to 74 lines. [REASONED from the counts]

**What she would see on `qa_amr_genes_per_sample`** (the entity used: `10668076`, 1 ResFinder line [HAND COUNT, CAUSE file]):

| Situation | Data table first, metadata second (`left`) | Metadata first (today's `QA_AMR_per_sample`), the marker kept and read by the recipe | Metadata first, the recipe counts genes only (today's tier 2) |
|---|---|---|---|
| Before any step | 42 samples, 4 in the bar at 0 | 42 samples: 38 detected, 4 "no result in file" | 42 samples, 4 in the bar at 0 (as today) |
| A removal by key of `10668076` at the ResFinder table (end of its tier 1) | 41 samples, 4 in the bar at 0: **no false not-detected** | 42 rows: 37 detected, 4 "no result in file", 1 "no line" (the entity removed): **no false not-detected** | 42 samples, 5 in the bar at 0: **false** (as A today) |
| The same removal at the join place (D-0549) | 41 samples, 4 in the bar at 0 | 41 samples, 37 / 4 | 41 samples, 4 in the bar at 0 |
| A removal of one of the 4 added entities at the ResFinder table | 41 samples, 3 in the bar at 0 | 38 / 3 / 1 "no line" | 42 samples, 4 in the bar at 0 |

[REASONED from the engine order of section 3 and the join semantics; NEEDS A RUN after her choice, section 9]

Why the middle column has a third state: after a left join from the metadata, an entity that has no line in the result table gets one row whose result columns are all empty, the marker column included; an added line has the marker set; a file line has it unset. Three values: set, unset, empty. [POLARS SEMANTICS; REASONED]

**What B6 changes in the list of options** (the two-part list of the D-0570 section):
- **Against B3** (the result files list every analysed entity): B3's lines come from the pipeline that knows what it analysed, so they mean "analysed, nothing found"; B6's lines come from the metadata, so they mean only "the data file has no result for this id" (analysed or not: the risk she accepts). Both put the lines in the result table itself, so a removal at the result table is complete with the data table first.
- **Against B5** (B3's files, the metadata first, a column "has a line"): B6 gives the column for free (the marker) and works with today's files; B5 needs the pipeline's lines.
- **Against E** (a right or full join, the metadata's rows kept at the join): E completes at each join; the result table itself stays incomplete, so a removal at the result table leaves the metadata's row (false 0). E's kinds are not YET followed by the audit [HER WORDS D-0452].
- **Against E2** (an anti-join, a table of its own): B6 puts the entities with no result in the result table itself, marked, so the number and the list come from one table; her words: "That would remove need for 6 anti join" [HER WORDS M627].
- **Against C** (the app completes the RESULT from the population and labels "removed" from the audit record): C completes late (after the aggregation; a new edge into tier 2) and needs the audit record to name a removal; B6 completes early (before tier 1), and a removal is a plain state ("no line") without reading the audit record.
- **Against A** (the metadata first, the blanks filled in the recipe): A cannot tell "no line in the file" from "removed by a step"; B6 with its marker can.
- **The key property:** with B6 the data table first keeps the initial population (every id of the metadata is in the table), which is her direction "the join should not start with the medata or we need a solution we do not have yet" [HER WORDS D-0564], with the zeros. [REASONED]

---

## 2. What each demo step would do with the added lines (by reading; today's steps unchanged)

| Table, step | What it does with the 4 added lines | Right or wrong for her meaning |
|---|---|---|
| ResFinder tier 1: `status: pl.lit('Detected')` [RECIPE FILE] | stamps "Detected" on them | wrong: they have no detection |
| ResFinder tier 2: `total_gene_count: pl.len().over(['sample_id'])`, then a sort by it [RECIPE FILE] | 1 for each of the 4 (one row each); they sort among the entities with one gene | wrong: 0 genes |
| `ResFinder_genes_heatmap` (reads ResFinder; `x: gene`, `y: sample_id`, `fill: predicted_phenotype`, `geom_tile`) [RECIPE FILE `plots/ResFinder_genes_heatmap.yaml:5, 7, 28-30`] | 4 rows with an empty gene | unknown: whether plotnine drops them with a warning or draws an empty category; NEEDS A RUN |
| `ResFinder_with_metadata` (ResFinder first, metadata second; its description: "a sample with no hit has no row") [RECIPE FILE recipe lines 188-194] | 70 to 74 rows: each sample now has a row | its description no longer holds; no plot reads this table (a table no plot reads is exported, D-0457) |
| `QA_AMR_per_sample` (metadata first, left join; tier 2 `pl.col('gene').count()`) [RECIPE FILE] | each of the 4 matches its added line instead of getting an empty row: 74 rows, as today; the count is 0 | right; the plot is unchanged (42, 4 at 0). The tier-1 `polars_select` drops the marker unless the author adds it |
| `QA_fanout_exhibit` (metadata, ResFinder, VirulenceFinder; tier 2 counts `VF_gene`) [ESTABLISHED: CAUSE] | one added line replaces one empty row: rows and counts unchanged | unchanged |
| `ST22_Anchor` (metadata, FastP, ResFinder, MLST, VirulenceFinder, inner join with the APEC list; tier 2 `virulence_count: pl.len().over(['sample_id'])`) [RECIPE FILE `ST22_Anchor_wrangling_tier1.yaml`, `_tier2.yaml:7`] | rows unchanged (one added line replaces one empty row); `status` becomes "Detected" for the 4 | the row count unchanged; `status` wrong (flag 1) |
| `integration_plot` (reads `ST22_Anchor`; `fill: status`) | the 4 samples' tiles change from empty to "Detected" | wrong unless ResFinder's stamp is adapted |

**So B6 does not, by itself, force the recipe maker to consider the case:** the steps that stamp a value (`pl.lit`) or count rows (`pl.len`) read an added line as a line, with no error. The force must come from the recipe check, the data check or a required statement of the meaning (section 4). [REASONED]

---

## 3. Where the completion lives (her open question)

**The engine order, verified by reading.** A data table is read by `_read_source` (the ingestion applies the declared types, `strip` and `null_values`), then the steps of its tier 1 are run [CODE READ `app/modules/orchestrator.py:264-267, 282-295`]. In an audit copy the steps of a tier are the author's `steps`, then its `audit_steps` [CODE READ `libs/transformer/src/transformer/data_wrangler.py:92`: `return steps + audit_list`; `app/modules/audit_run.py` module text: "the engine runs the author's `steps`, then the `audit_steps` of the tier"]. The Source view of HOME uses the same `_read_source` [CODE READ `orchestrator.py:298-300`], and the plan of every place reads the same lists [CODE READ `orchestrator.py:287-291`].

**Two positions of the completion inside a table, and what the marker then means.**
- **P1, before the steps of tier 1** (after `_read_source`): the marker means "the data FILE has no line for this id", her words. An audit step at the end of tier 1 runs after it: a removal by key removes the entity's file lines and its added line alike; nothing adds it back in that table. A threshold filter written by the author in tier 1 can leave an entity with no line (flag 3).
- **P2, after the author's steps of tier 1 and before the audit steps:** the marker means "no line left after the recipe's tier-1 rules" (it also covers an entity whose lines a threshold removed); the audit steps still run after it. It is not her wording ("data file has no result").
- **Never after the audit steps:** the completion would then add back an entity the user removed at that table.

### (i) A read-time option declared in the recipe on the data table (like `null_values` and `strip`)

**The author writes** (invented; refused today as an unknown key of a schema, S01 [CODE READ `recipe_check.py:390`]; names PROVISIONAL):
```yaml
data_schemas:
  ResFinder:
    source: {type: local_tsv, path: ...}
    null_values: []
    strip: true
    complete_from_population: {marker: no_result_in_file, meaning: nothing_found}
```
Three variants: (i-a) the key is written on each table to complete; (i-b) every data table that declares an entity id is completed, and the key only states the meaning or turns it off; (i-c) every such table is completed and no key exists (documented app behaviour). Her words point to (i-b) or (i-c) ("an automatic completion at (first step)", "mentionned both in literature and allerts" [HER WORDS M627]).
**What the app does:** in `ingredient_parts`, after `_read_source` and before the tier-1 steps (P1): one line per population id absent from the file, the marker set, every other column empty, appended in a fixed order (for example the order of the population) so that the same data give the same rows in the same order [RULE FILE `rules_data_engine.md` section 2, Determinism, ADR-090]. [REASONED; not built]
**What the user sees:** the Source view of ResFinder shows the file (70 lines), true to "a source table as read from the file" [RULE FILE `ui_implementation_contract.md` section 2]; the T1 view shows 74 lines, 4 marked; the alert (section 5) names the 4 ids and the marker; the export's T1 file holds the 74 lines, and README and report must state the completion (the rule, the count, the marker), because what the user sees is what the export contains [RULE FILE `rules_verification_testing.md` section 9].
**"The app never modifies the recipe":** holds. In (i-a) and (i-b) the recipe states it and the app executes it, as for `strip`; in (i-c) the recipe text says nothing and the completion is app behaviour: reproducible only if the export records the app's rule and version.
**The audit place:** P1 runs before the author's and the audit's steps of tier 1: a removal by key at the end of tier 1 is complete in that table.
**The keys:** the key of a stored table holds the definition of the table and of everything upstream (rC) and the content of the data files it reads (dC) [CODE READ `app/modules/cache_keys.py:14-20`]. With the completion the data table also reads the population: its definition and its file must enter ResFinder's key, so a change of the metadata changes ResFinder's key and the keys of every table below it. [REASONED; not built]
**The graph and her rule of one place per path (D-0553), two readings of "the population":**
- **(α) the metadata as read from its file** (its declared reading, before its tier-1 steps): a new edge from the metadata's FILE into ResFinder's first place. ResFinder's first place stays a first place after original data, so it can still be chosen together with the metadata's (her exception for the original parents [HER WORDS D-0553]; "the original T1 steps of independent histories" [HER WORDS D-0549]). A removal at the metadata's place does NOT remove an added line: with the data table first, the entity stays with empty metadata values, exactly as an entity with file lines does today [ESTABLISHED: RECIPES G5]. The key of ResFinder does not move when the user writes a step at the metadata.
- **(β) the metadata after its tier 1** (with its audit steps): a new edge from the metadata's T1 into ResFinder's T1. ResFinder's first place then lies BELOW the metadata's place: choosing both is two places on one path (refused by D-0553), and "Remove from all the data" (D-0416, written at tier 1 of every table that holds the key) meets that rule. A removal at the metadata's place also removes the added line of that entity (not its file lines): the two kinds of entity behave differently.
**Against the withdrawn T0:** T0 was filters on the original data before tier 1, as audit steps; she withdrew it: "no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" [HER WORDS D-0509]. B6 removes nothing: it ADDS lines, each marked; it is not an audit step; the recipe (or the documented app rule) states it; the file stays unchanged.

### (ii) A new tier-1 step written by the author

**Today:** no action appends rows (no union or concat) [ESTABLISHED: CAUSE catalogue (e)]. A data table's tier-1 steps run on its own table only [CODE READ `orchestrator.py:282-295`], so a step there cannot read the metadata: the action would be a new kind of step that reads a second table outside a join (refused today as an unknown action).
**Written as a joined table** ("ResFinder completed": ResFinder with a `right` or `full` join of the metadata's ids and a marker): possible with today's kinds, but no other join can read it: an ingredient must be a schema [CODE READ `recipe_check.py:866-867`, J04]. Every join below would have to repeat it.
**The rule holds:** the author writes the step; the app does not touch the recipe. But it is not automatic: each recipe must write it on each table.
**The audit place, the keys, the graph:** as (i) with the step first in tier 1; a step reads a table, so its natural source is the metadata's T1 (β).

### (iii) Preparation outside the recipe (the pipeline, a Data Import helper)

**The file itself gains the lines** (with the marker column), written by the pipeline or by a helper. Nothing in the recipe; the Source view shows them (they are in the file); the key moves with the file's content, as for any file; no new edge (the dependency on the metadata is outside the app, so the file goes stale when the metadata changes: the data check's note would show it).
**The rule holds** for the recipe; but a helper that writes a data file meets the Data Import rules: the overwrite of a recipe's data file with no copy of the old one and the record of what was uploaded are NOT decided (task DATA-IMPORT-OVERWRITE) [RULE FILE `ui_implementation_contract.md` section 9, step 5 and "Provenance obligation"].
**Against B3:** B3's lines say "analysed, nothing found" (the pipeline knows); a helper's lines say only "no result in the file for this metadata id".

### (iv) A first step written by the app into the audit copy only

**Does not fit.** The audit copy holds audit steps only, and an audit step is a filter, a column drop or a removal by key [HER WORDS D-0322: "A : for now yes only filter and drops"]; a completion adds lines. Audit steps run AFTER the author's steps of their tier [HER WORDS D-0541: "audit steps can be written at each tier after the original tier block"; CODE READ `data_wrangler.py:92`], so it could not be first. The Result (Exploration, no audit copy) would not have it: the Result and the audited plot would differ by something the user did not decide.

### Other ways found

- **(v) At each join** (the app completes when a join reads a result table and the metadata): this is E done by the app; the result table itself stays incomplete; a removal there leaves the metadata's row (false 0).
- **(vi) At the result** (C, or the app at the plot, (f3)): late; it needs the audit record to name a removal.
- **(vii) The source of the completion is `entity.population`** (default the metadata): with a manifest of the analysis as the population, the marker means "analysed, nothing found" (B3 done by the app from the manifest). The key exists and is checked (E02) [CODE READ `recipe_check.py:332-348`]; her words: "Ok for the population anchor - as long as we can compute its fine" [HER WORDS D-0569].

---

## 4. The marker (her point 2: "short and explicit", "a different kind of other missing value")

**Polars has one missing value (null), plus NaN for floating-point numbers; there is no second kind of null** [POLARS SEMANTICS]. (Statistical packages such as SAS, Stata or SPSS have several kinds of missing value; Polars, like a plain data frame, does not.) So "a different kind of missing" must be carried by something other than the empty cell.

| Form | What Polars does with it | What the demo's steps do | What a check can see |
|---|---|---|---|
| **m1. A marker column** added by the completion (for example `no_result_in_file`: true on the added lines, false on the file's lines), every result cell of an added line empty | the result cells are ordinary nulls: `count()` gives 0, a mean gives missing; the marker is a boolean; after a left join from the metadata an entity with no line has the marker empty (a third state); `when(pl.col(marker))` sends an empty marker to `otherwise` [POLARS SEMANTICS] | stamps and row counts read the added lines as lines (section 2); `gene.count()` is right | the recipe check can see whether any step below names the column (a text match); the data check can count the marked lines |
| **m2. A sentinel text** in each text result column (for example gene = "no result in file") | a normal value: `count()` gives 1, `n_unique` counts it, a join on that column would match it as a value [POLARS SEMANTICS] | `QA_AMR_per_sample` would count 1 gene; the heatmap would show a "gene" named by the sentinel | a text match on the sentinel |
| **m3. A marker per column type** (text: a sentinel; floating-point numbers: NaN) | NaN is not null: `count()` counts it, a mean becomes NaN, `fill_null` does not touch it; integers, booleans and dates cannot hold it [POLARS SEMANTICS] | mixed: counts wrong, means NaN | type by type |
| **m4. Empty cells only** (no marker) | the added lines look like any line with empty cells | as m1 | nothing: it does not meet her "different kind" |

**What the checks can verify with m1:** the recipe check: the completion's key is well formed, the table declares an entity id (`is_entity_key`), the population exists (E02), and, as information, whether a step below the table names the marker column; a stamp (`pl.lit`) or a row count (`pl.len`) on a completed table (both text matches, never a refusal). The data check: for each completed table, how many lines were added and which ids (section 5).
**The name:** short and explicit, from her words "data file has no result": `no_result_in_file` (a yes/no column). PROVISIONAL.
**How "forcing the recipe maker to consider" can be done** (her words "forcing the recipe maker to consider this case" [HER WORDS M627]): no marker form makes a naive step fail; the force is a statement the recipe must write. Two ways: (1) the completion REQUIRES its meaning (a required field, as the project already requires a parameter whose absence would hide a choice that changes the result [CODE READ `polars_calls.py:54-60`, `REQUIRED`]); the recipe check refuses the completion without it; (2) the data check informs, for every table that received lines, that the recipe does not say what they mean (only informs, D-0569). The recipe check reads the recipe only, so it cannot know which tables will receive lines; in variant (i-b) it would ask the meaning of every table that declares an entity id.

**My lean, as a lean:** m1, a marker column named `no_result_in_file` (PROVISIONAL), every result cell of an added line empty, with its meaning required by the completion. Reason: it is the only form that is the same for every column type, keeps the counts of values right (`count()` 0, as the demo's plot expects), gives the third state "no line" after a join for free, and can be named by the recipe and the checks.

---

## 5. The control of the ids (her point 1)

- **(a) An id in a result file and in no metadata.** Her words: "if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done" [HER WORDS M627]. Decided: the data check informs, through the new channel, and tells the user to fix it [HER WORDS D-0569: "Choice for data check - b"; D-0568]. On the demo: 0 such ids in every file; the template `left_join_lesson` has 2 (`ACC0001`, `ACC0002`), by design [ESTABLISHED: OVERLAP lines 53-55, 69]. Her alternative, a marker "not in metadata": the author can already write it today for a join with the data table first (stamp `in_metadata: pl.lit(True)` in the metadata's tier 1, fill the empty values with false after the join) [REASONED]; with the metadata first, such an id is dropped by the left join, silently (as an inner join hides it [HER WORDS D-0568: "an inner join would hide this"]). B6 with the data table first keeps these ids with empty metadata values: the problem stays visible in the result.
- **(b) An id in the metadata and not in a result file.** B6: the completion adds it, marked; the alert says so, and the documentation states the rule ("clear and mentionned both in literature and allerts" [HER WORDS M627]). Alert, words PROVISIONAL: "4 entities of the metadata have no line in ResFinder: <ids>. They were added to ResFinder with the mark no_result_in_file. The app cannot tell whether they were analysed with nothing found or not analysed; the recipe says how they are counted." Where: as decided for the data check (the new channel; Data Import after a replace; BLUEPRINT's Validate) [HER WORDS D-0570: "4. yes the validated question - yes . information is very important here"].
- **(c) Metadata lines with no id.** Her words: "5. true that is why metadata should be clean - all with an id ..." [HER WORDS M627]. The completion skips them (an empty id cannot be added); a join with the data table first never matches them; a join with the metadata first keeps them as one more entity with no result [ESTABLISHED: the D-0570 section, fact 6]. The third note of the data check ("N lines of the metadata have no id", proposed, not decided) applies.
- **(d) An id repeated in the metadata** (not raised by her): the completion adds one line per distinct id; a join with the metadata second multiplies the rows of that id. A note "an id is repeated in the metadata" would cover it. [REASONED]

## 6. The risk she accepts

"it knows the risk it accepts" [HER WORDS M627]: the marker says only that the file has no result for the id. The app cannot tell "not analysed" from "analysed, nothing found"; the recipe maker, with a real user, decides; the alert and the documentation say so. On the demo nothing shows the risk: every metadata id is in every result table except ResFinder, and every metadata id is in `FastP` (42 of 42) [ESTABLISHED: Opus RR13]. A metadata that lists entities never sequenced would add a marked line for each of them to every result table.

---

## 7. Her eight questions (end of the D-0570 section): settled or not

| Question | What her M627 words settle | What remains |
|---|---|---|
| 1. A never-analysed entity counted as "not detected"? | B6 marks it "no result in file"; the recipe maker decides its meaning, the risk is accepted | nothing for the app; the rule goes in the documentation and the alerts |
| 2. The name of the third class | the meaning: "data file has no result", a missing value of its own kind, short and explicit | the short name of the marker |
| 3. May the app read the record of the audit steps? | not answered; with B6 a removal is a plain state ("no line"), so it is needed only for C and for the line F ("of which 1 removed by an audit step") | open, smaller |
| 4. Where the recipe says what a missing value means | "saying how those need to be processed in the recipe" | whether the completion requires a stated meaning, or only the steps say it |
| 5. The count per target | not answered | open |
| 6. The threshold of "not detected" | her point 3 (the review session's reading: a filter on values is not so useful for her case) | can wait; flag 3 shows where it matters with B6 |
| 7. The number, the list or both | B6 gives both from the same table; no anti-join | how the list is shown (a table as a result: decided, not built, D-0485, D-0487) |
| 8. `demo_abromics`'s three id-less lines | "metadata should be clean - all with an id" and her earlier order "remove the null and empty rows from the metadata" [HER WORDS D-0569] | to confirm in the dry run of the one big move (D-0525) |

---

## 8. The questions that remain for her, one at a time (each with what she would see on the demo)

1. **Where does the completion live?** (i) an option the recipe declares on the data table, done by the app when it reads the file; (ii) a first step the author writes (a new action); (iii) outside the recipe (the pipeline or a Data Import helper). (iv), the audit copy, does not fit (section 3). On the demo with (i): the ResFinder Source view shows the file's 70 lines; its T1 shows 74 lines, 4 marked; the recipe holds one line, or none if the completion is automatic.
2. **Automatic for every result table that declares an entity id, or only where the recipe names it?** On the demo either gives the same 4 lines on ResFinder (every other result table already holds 42 of 42); the look-up table (APEC list) has no entity id and is never completed.
3. **The marker:** a yes/no column (`no_result_in_file`, PROVISIONAL) with the result cells empty, or a word written in the cells? On the demo: with the column, the plot keeps 4 samples in the bar at 0; with a word in the gene column, `QA_AMR_per_sample` counts 1 gene for each of the 4 and the bar at 0 is empty.
4. **Must the recipe state what the marked lines mean** (the check refuses the completion without it), or is the data check's note enough? On the demo: the check would ask ResFinder's meaning before the recipe opens; the note would say "4 lines added to ResFinder; the recipe does not say what they mean".
5. **The completion reads the metadata as read from its file, or after its tier 1?** On the demo: remove one of the 4 added entities at the metadata's place. As read from the file: it stays in ResFinder, marked, and in a result that starts from ResFinder with empty metadata values (as an entity with results does today). After tier 1: it is no longer added, but ResFinder's place then lies below the metadata's place (one place per path).
6. **A filter of the recipe in the result table's tier 1 that removes every line of an entity:** complete before the recipe's steps (the marker means "the file has no line"; the filtered entity has no line at all) or after them (the marker means "no line left after the recipe's rules")? The demo has no such filter on ResFinder.
7. **An id in a result file and in no metadata:** the note only (decided, D-0569), or also the marker "not in metadata"? The demo has none; the template `left_join_lesson` has 2.

## 9. Runs after her choice (each registered before it runs, D-0561)

1. **The completed table through the demo's chains.** Requirement: B6 (i), P1, on a scratch copy: the ResFinder file with the 4 added lines and the marker column written by hand into an empty folder (the completion does not exist yet). Expected: ResFinder T1 74 lines; `status` "Detected" on the 4 unless the stamp is adapted; `total_gene_count` 1 for the 4; `ResFinder_with_metadata` 74 rows; `QA_AMR_per_sample` 74 rows, 42 per entity, 4 at 0; `QA_fanout_exhibit` and the row counts of `ST22_Anchor` unchanged; `ST22_Anchor`'s `status` "Detected" for the 4; the heatmap's handling of an empty gene: observed. Independence: a scratch recipe from the demo's own schemas, steps written by hand, every table rebuilt in its own empty folder (D-0560), no lineage code (D-0558).
2. **A removal on the completed table.** Requirement: a removal by key of `10668076` in the audit list at the end of ResFinder's tier 1 of a scratch audit copy. Expected: data first: 41 samples, 4 at 0; metadata first with the marker read: 37 / 4 / 1 no line; metadata first counting genes only: 42, 5 at 0. Independence: as 1; the audit step written by hand (no HOME code).
3. **The marker forms.** Requirement: the same chain with a marker column and with a sentinel word. Expected: `gene.count()` 0 against 1; the heatmap with an empty cell against a category named by the word. Independence: as 1.

## 10. Leans (as leans; nothing chosen)

- **Where:** (i), a read-time option declared on the data table, automatic for every result table that declares an entity id (variant i-b), placed before the tier-1 steps (P1). Reason: one place per table; the audit's removal at the end of tier 1 is complete; the recipe shows it, so the app does not modify the recipe; the Source view stays true to the file.
- **The source:** (α), the metadata as read from its file. Reason: the result table's place stays a first place after original data (her exception of D-0553), and an added entity behaves at the metadata exactly as an entity with results does (G5).
- **The marker:** m1, a yes/no column, with its meaning required by the completion.
- **The join direction it allows:** with B6 the data table first keeps the initial population and the zeros, and a removal at the result table is complete.

## 11. For the merge

B6 goes into Part 1 of the list (beside A to E2) as her candidate; the control of the ids (a) to (d) goes into the data check's text (both directions and the third note); her eight questions get the settled / remaining column of section 7.
