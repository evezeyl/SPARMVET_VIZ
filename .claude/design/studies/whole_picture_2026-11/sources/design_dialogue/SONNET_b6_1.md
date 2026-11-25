# SONNET position 1 (blind): B6, "fill the data tables with the ids of the metadata", where the completion lives, the marker, the control of the ids (block M627; ledger D-0570 and its continuation)

Written without the Opus agent's text. Reading and reasoning only; NO RUN (D-0566). No study file is edited; `WHOLE_PICTURE.md` untouched. No waiting loop, no process left. Data agnostic: "the entity" (on the demo, a sample). Cost and effort are no argument.

Tags: [HER WORDS M627] / [RECIPE FILE] / [CODE READ file:line] / [RULE FILE] / [ESTABLISHED: file, point] / [POLARS SEMANTICS] (the library's documented behaviour; not run) / [REASONED, not run]. "NEEDS A RUN" marks what can be judged only after her choice.

---

## 0. Her solution B6, in her words

"I think the solution would be to fill the data tables with the id contained in the metadata and have a "data file has no result" NA ? that can be then processed as a normal recipe - saying how those need to be processed in the recipe. Its a bit weird solution but it would work in all cases forcing the recipe maker to consider this case. and then missing data in the original files need to be processed correctly according to the correct meaning - which only a recipe maker (in collaboration with a real user) can decide. That would remove need for 6 anti join." [HER WORDS M627] And: "if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) ... clear and mentionned both in literature and allerts ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe)"; "good marker convention - short and explicit - and I think it should be a different kind of other "missing value" because then the recipe maker has to consider those cases specifically"; "it knows the risk it accepts". [HER WORDS M627]

**B6 in one line.** Each result table that opts in gets one added line for every id of the metadata that has no line in its file, before the table's own steps run; the added line is marked "no result"; the recipe then says how marked lines are processed.

---

## 1. What B6 gives on `qa_amr_genes_per_sample` (42 entities; ResFinder: 70 lines for 38 entities; 4 entities without a line)

The completion adds 4 lines to ResFinder (74 lines, 42 entities), each with the id, the marker, and every other column empty. [REASONED; the 70, 38, 4 from the files, ESTABLISHED: OVERLAP section 1]

**The two ways to join afterwards**
- **Data first: ResFinder (completed), then the metadata second with `left`.** 74 lines, 42 entities; the per-entity count `gene.count()` gives 0 for the 4, so the plot counts 42 samples with 4 in the bar at 0. The join does not start with the metadata (D-0564), and the metadata adds no entity (her reason, D-0549). [REASONED from the join semantics; ESTABLISHED: RECIPES G5]
- **Metadata first (today's `QA_AMR_per_sample`).** Also 74 lines and the same plot: the 4 completed lines replace the 4 empty rows a left join made. The metadata keeps the entity by its own path.

**Before and after a removal by key** (one detected entity; the audit step is written at the end of tier 1 of ResFinder, after the completion, see section 2):

| Case | Samples counted | In the bar at 0 | Is it a false "not detected"? |
|---|---|---|---|
| before any step | 42 | 4 | no |
| removal at the ResFinder table, join data first | 41 | 4 | **no**: the entity's lines are gone from the first table; the metadata second adds nothing |
| removal at the ResFinder table, join metadata first | 42 | 5 | **yes**: the metadata path still holds the entity |
| removal at the join place (either join) | 41 | 4 | no |

So B6 removes the false "not detected" if, and only if, the recipe joins data first. The condition is the author's; the recipe check can advise on the pattern (first ingredient the metadata, a table that opts in). [REASONED]

**How B6 differs from the others**
- **B3:** the same files with a line for every analysed entity, but written by the pipeline, which knows who was analysed. B6 writes the line for EVERY metadata id that is missing, so it cannot tell "not analysed" from "analysed, nothing found"; it marks the line instead, and the recipe maker decides the meaning (her risk, section 5).
- **B5:** B3's files, the metadata first, a "has a line" column. B6 keeps no "analysed" fact, only a marker for what the app added; its join is data first.
- **E (right or full join):** the completion is made in a joined table, after the result table's own place; a removal at the result table does not reach it, so the false "not detected" stays. B6 completes inside the table, before its steps.
- **E2 (anti-join):** a separate table of the entities with no line, a removal at the result table ADDS the entity to it. B6 has no anti-join: the "not detected" list is the lines marked `no_result`, taken by a filter. A removal at the result table removes the entity's marked line too. [REASONED]
- **C (the app labels from the declared population):** C completes after the join and names a removal from the audit record. B6 needs no audit record: the order of the steps does it.
- **The rejected T0 (filters on the original data):** T0 removed or filtered lines of the original files. B6 ADDS lines, marked, and removes nothing.

**What each demo step does with the completed lines** (by reading)
- `ResFinder` tier 1 stamps `status = pl.lit('Detected')` on every line [RECIPE FILE `wrangling/ResFinder_wrangling_tier1.yaml`]: the 4 added lines would read "Detected". The maker must change that step (for example `when(no_result) 'Not detected' else 'Detected'`). This is the case her sentence says B6 forces.
- `ResFinder` tier 2 counts rows: `total_gene_count = pl.len().over(sample_id)` [RECIPE FILE `ResFinder_wrangling_tier2.yaml`]: an added line counts 1, not 0. The maker must count only lines that are not marked.
- `amr_heatmap` reads ResFinder's tier 2 (`x: gene, y: sample_id, fill: predicted_phenotype`) [RECIPE FILE `plots/ResFinder_genes_heatmap.yaml`]: the 4 added lines would be tiles with no gene. The maker filters them or lets them show; the recipe has to say.
- `ResFinder_with_metadata`: tier 1 joins ResFinder (base) with the metadata: 74 lines instead of 70.
- `QA_AMR_per_sample` and its plot: 0 genes for the 4, as today; `gene.count()` ignores the empty gene. [RECIPE FILE `QA_AMR_per_sample_tier2.yaml`]
- `QA_fanout_exhibit` and `ST22_Anchor`: an entity with no ResFinder line already had one empty row after the left join; the completed line gives the same single row, so row counts do not change. [REASONED]
- Tables that already list every entity (FastP, Quast and others with 42 of 42) get no added line. [ESTABLISHED: OVERLAP section 1]

**What cannot be judged without a run:** the whole chain with a marked ResFinder file (NEEDS A RUN, section 7).

---

## 2. Where the completion lives (her open question)

The facts the options rest on:
- A source table is read in ONE place, `_read_source`, "the file ... with the declared types, `strip` and `null_values` the ingestion applies, before any recipe step"; the Source view reads through the same function [CODE READ `app/modules/orchestrator.py:246-249`].
- Then tier 1: `ingredient_parts` returns the table as read and the steps of its tier 1, and `prepare_ingredient` runs them [CODE READ `orchestrator.py:269-294`]. The steps of a tier are the author's `steps`, then the audit's `audit_steps` [CODE READ `libs/transformer/src/transformer/data_wrangler.py:31-35`]. So an audit step at the end of tier 1 runs AFTER anything done at read time or in a step before it.
- The ingestion library reads one file and may not know another table (the libraries do not import each other) [RULE FILE `rules_runtime_environment.md` section 4]; the orchestrator (the app layer) knows all the tables and may read two.
- No registered action appends rows. A schema's tier 1 has no ingredients: a join step there fails ("polars_join needs the resolved right table") [ESTABLISHED: RECIPES G18; CODE READ `recipe_check.py:714-715`].

| | (i) A read-time option declared in the recipe on the data table | (ii) A new tier-1 action written by the author | (iii) Preparation outside the recipe (pipeline, Data Import helper) | (iv) The app writes a first step into the audit copy only |
|---|---|---|---|---|
| What the author writes | one key on the table, for example `complete_from: metadata_schema` and the marker's name, next to `null_values` and `strip` (invented; refused today as an unknown key, S01) | a first step in tier 1, for example `step_complete_ids` naming the metadata; a new action (no action appends rows today) | nothing; the file already holds the lines, and the recipe declares the marker column among its fields | nothing |
| What the user sees | the Source view shows the completed table with the 4 marked lines and a note "4 lines added from the metadata" (the Source view reads through the same function, `orchestrator.py:246-249`); the alert; T1; the export | the Source view shows the file as it is (70); T1 shows 74; the step is visible in BLUEPRINT and in the recipe | a file with 74 lines; the alert from the data check | nothing in the recipe; the audit panel would show an extra step |
| "The app never modifies the recipe" | holds: the declaration is the author's, the app only reads | holds: the step is the author's | holds, but the app changes DATA outside the recipe: the provenance of the added lines is not in the recipe (a silent change unless a record is kept) | does not fit: the audit copy holds only a filter, a column drop and a removal by key (D-0322; `ui_implementation_contract.md` 12a), and a completion adds lines; and without any audit step the recipe would give another result |
| A step at the end of tier 1 | runs after the completion (read time, before tier 1): no re-adding | runs after the completion if the completion is the first step; before it if written later (the author's order) | runs after (the file is what is read) | cannot say |
| Keys and graph | the table's key must include the option and the metadata (the ids): a new dependency; today the key reads "the definition of the table and of what it reads, and the content of the data files" [RULE FILE `rules_data_engine.md` section 1; CODE READ `cache_keys.py:248-276`: `datasets` from `graph.source_tables`]: the graph needs a new edge into the table | the same, from the step's naming of the metadata | the file's content hash changes; the graph is unchanged | not applicable |
| Differs from T0 | adds lines, filters nothing | same | same | not applicable |
| NEEDS A RUN | yes | yes (and an engine change: an ingredient for a schema's tier 1) | no for the recipe side; the helper is a feature | no |

**Which edge, and what a removal at the metadata does.** Two readings of "the ids of the metadata":
- **As read** (the metadata after its declared `strip` and `null_values`, before its tier 1): the edge comes from the metadata's file (`DS:metadata`), not from a place. The places stay as they are; the "first places of all originals are valid together" (D-0553) is unchanged. A removal at the metadata's place does not change the added lines.
- **After the metadata's tier 1** (with its audit steps): the edge comes from `T1:metadata`; a removal at the metadata's place removes the entity from the added lines too; but then every completed table lies BELOW the metadata's place, so the metadata's place and the result table's own place are on one path: not valid together in one step under "at most one chosen place on a path" (D-0553). "Remove from all the data" would need re-reading. [REASONED from `PATHS_AND_DERIVED_AGREED.md` G9, G27]
**Does the completion re-add an entity removed at the result table?** No, in (i) and in (ii) with the completion first: the audit step is after it. [CODE READ `data_wrangler.py:31-35`; REASONED]
**Does the key change when the metadata changes?** Yes: the table depends on the metadata; a new line in the metadata changes the key of every completed table and of everything below (D-0560). [REASONED]

---

## 3. The marker

She wants it short, explicit, and a different kind of missing value so that the recipe maker must consider it.

| Form | What it is | What Polars does | What the demo's steps do | Can the checks verify it |
|---|---|---|---|---|
| **M1. A flag column** (for example boolean `no_result`: true on added lines, false on file lines), with the other cells missing | one extra column; typed; the cells that have no value stay null | a null stays null in a count of values, a sum, a mean; the flag is an ordinary boolean column [POLARS SEMANTICS] | `gene.count()` still gives 0 (good); `pl.len()` counts the line; the `status` stamp says "Detected" unless the maker uses the flag | the recipe check: a table that completes must have a later step whose text names the marker, else an advice (a match on the text of the formulas; the check reads formulas as text, `polars_calls.py:82`); the data check: "4 lines added to ResFinder (marked `no_result`): <ids>" |
| **M2. A sentinel text** in the columns | a word such as "NO_RESULT" in every text column | an ordinary string: `count()` counts it as a value; a number column cannot hold it (type error or a second marker) | `gene.count()` would give 1 for the 4 entities: the plot would show a gene that does not exist | only by reading the word in formulas; a silent wrong count if not adapted |
| **M3. A distinct marker per column type** (text word, NaN for floats) | per type | NaN is a float VALUE, not a missing one: `count()` counts it, `sum` and `mean` give NaN; integers have no NaN [POLARS SEMANTICS] | counts and means change in different ways per column | hard to check; surprising |
| **M4. Null plus the flag (M1)** | "a different kind of missing" built from two things | Polars has one kind of null; a second kind exists only as a column | as M1 | as M1 |

**My lean, as a lean:** M1, a boolean column with a short explicit name (`no_result`; the name is hers), the cells without a value left null, `false` (not null) on the lines of the file. Reason: counts of values keep working, the types are kept, one test in a step says what to do, and the recipe maker sees a column he must handle (her "forcing the recipe maker to consider this case"); a sentinel text counts as a value and can silently show a gene that does not exist. The marker's name must not collide with a declared field (the checks refuse that). [REASONED]
**A cell of only spaces** is not the marker: the ingestion strips the text and turns only the listed null words into missing, so with `null_values: []` it stays an empty text [CODE READ `libs/ingestion/src/ingestion/declared.py:115-120`].

---

## 4. The control of the ids

- **An id in a result file and in no metadata.** The data check warns (it informs, as decided); she prefers the metadata corrected. The alternative she names, a marker "not in metadata": the same read-time option could add a second flag column (`not_in_metadata`) on the lines whose id is in no metadata; the lines stay (no row is added or removed), the maker decides, an audit step can remove them. It costs one more column and one more name; the check is the same set difference. NEEDS A RUN.
- **An id in the metadata and in no line of a result file.** The completion (B6) adds the line, marked. It must be said in the documentation and in the alerts: "4 lines added to ResFinder from the metadata; the app cannot tell whether they were analysed". The alert is the data check's note in the other direction (decided, D-0570); with B6 it says what was ADDED.
- **Metadata lines with no id.** The metadata should be clean (hers). The completion adds only ids that are not missing; a metadata line with no id adds nothing. The data check's third note ("N lines of the metadata have no id") stays. On the demo, `demo_abromics` has 3 such lines on purpose; her sentence 5 reads as "the metadata should be clean" (review session's reading). [RECIPE FILE `demo_abromics.yaml:44-47`]
- **Overlap.** Her sentence 4: the ids of the metadata and the data sets should overlap, "or at least all in metadata and included for data sets": B6 is the way to make the second half true by the app. [HER WORDS M627]

---

## 5. The risk she accepts

The app cannot tell "not analysed" from "analysed, nothing found": B6 adds a line for both. The recipe maker, with a real user, decides what a marked line means. The alerts and the documentation say so; the data check's note says how many lines were added and for which ids. [HER WORDS M627: "it knows the risk it accepts"] A second risk to name: a result table whose absence means something else (an entity with no virulence gene is not the same as one never sequenced) gets the same marker; the recipe maker must read the pipeline's documentation. [REASONED]

---

## 6. Which of her eight questions are settled, which remain

The eight questions at the end of the D-0570 section of `CAUSE_AND_SOLUTIONS_ZEROS.md`:
1. **Never-analysed entity as "not detected"?** Settled in principle by B6: it gets a marked "no result" line, and the recipe maker decides the meaning. Remains only the word.
2. **Name of the third class.** Partly settled: her "data file has no result" and "short and explicit"; the exact name remains (section 3).
3. **May the app read the audit record to say "removed"?** Not answered, and not needed if B6 is chosen (the order of the steps does the work); remains only if C is kept.
4. **Where the recipe says what a missing value means.** Settled in principle: in the recipe, by the steps on the marked lines; remains: per table or once for the recipe (section 2).
5. **Count per target.** Not answered; remains. B6 gives a line per entity, not a grid.
6. **Threshold in the meaning of "not detected".** Settled: a filter on values matters little to her (her 3).
7. **The list as a table result.** Not answered; remains (the list is the lines with `no_result` true, taken by a filter).
8. **The `demo_abromics` lines.** Her sentence 5 ("the metadata should be clean") points to removing them; the review session reads it so; to confirm in the dry run.
Her answer 2 (a bad sample is removed by an audit step, justified, and rerun in another batch) settles that a removal by key is right; with B6 and the data first it leaves no false result.

---

## 7. The questions that remain for her, one at a time, with what she would see

**Question 1. Where does the completion live?** (i) a line in the recipe on each data table, done by the app when it reads the file; (ii) a first step written by the author in tier 1; (iii) done outside the recipe by the pipeline or a Data Import helper; (iv) not a fit (the audit copy cannot add lines). What you would see on the demo: (i) in ResFinder's description in the recipe one line `complete_from: metadata_schema`; the Source view of ResFinder shows 74 lines, 4 of them marked, and a note "4 lines added from the metadata"; (ii) the Source view shows the 70 lines of the file and the step is visible in tier 1, T1 shows 74; (iii) the file already has 74 lines when the app reads it, with an alert. In (i) and (ii) the recipe is never changed by the app.

**Question 2. Which version of the metadata does the completion read?** As read from its file (the places stay as they are) or after its tier 1 (a removal at the metadata's place then removes the entity from the added lines, but the metadata's place and every completed table's place lie on one path). What you would see: remove an entity at the metadata's place: as read, ResFinder's added line for it stays and the metadata second does not add it back; after tier 1, the added line disappears.

**Question 3. What does the marker look like and what is it called?** A column `no_result` (true on the added lines, false on the others), the other cells empty (M1); or a word in the cells (M2: it would count as a value). What you would see: a column `no_result` in the ResFinder table; the 4 lines true.

**Question 4. Which tables are completed: each table that says so, or every data table of the recipe?** What you would see: ResFinder gets 4 lines; FastP, Quast and the others (42 of 42) get none.

**Question 5. In which order may the recipe join?** B6 removes the false "not detected" only with the data table first. May the metadata-first join (today's) stay allowed, with an advice? What you would see: remove one detected entity at the ResFinder table: data first, 41 samples; metadata first, 42 samples with 5 in the bar at 0.

**Question 6. An id in a result file and in no metadata: warn only, or also mark the line `not_in_metadata`?** What you would see: a note with the ids (decided), and, if marked, a second column.

**Question 7. The three lines of `demo_abromics`: remove them from the file?** (her sentence 5.) What you would see: the metadata with 27 lines, no removal step in the recipe, no example of a messy id.

**Question 8. The list and the count per target.** The list of the not-detected as a table result (decided design, not built) and "how many entities carry no target X" (not covered).

---

## 8. Runs needed after her choice (each registered first, three points)

1. **The chain with a hand-written marked file (the recipe side).** 1. Requirement: a scratch ResFinder file with the 4 lines and the marker column written by hand; the chain of `qa_amr_genes_per_sample` joined data first and metadata first. 2. Expected: 42 samples counted, 4 at 0; a removal by key at the end of tier 1 of ResFinder: 41 (data first), 42 with 5 at 0 (metadata first); `status` reads "Detected" on the 4 lines and `total_gene_count` 1 unless the steps are adapted. 3. Independence: a scratch recipe from the demo's schemas, the file written by hand, every variant built from scratch in its own empty folder, no lineage code.
2. **The audit order.** 1. A step at the end of tier 1 runs after what the table did before. 2. The removal takes the marked line too and nothing re-adds it. 3. As 1, with the audit step written by hand into the scratch recipe (no audit code).
3. **The marker in Polars.** 1. M1, M2, M3 on a scratch table: counts, sums, means, a join. 2. M1 keeps `count()` at 0; M2 gives 1; NaN counts. 3. Polars only; no recipe code.
4. **The keys.** 1. A change in the metadata file changes the key of every completed table and of the tables below. 2. Every key differs; a stale stored table is not served (D-0560). 3. Each variant in its own empty folder; the keys read from the engine's own key functions on a hand-edited scratch recipe.
5. **The app's completion** (once built): the same three points as 1 on the real option; and the graph with its new edge for D-0553 (the valid sets of places).
6. **`not_in_metadata`** (if chosen): the lines of a scratch result file with an id in no metadata.

---

## 9. My lean, as a lean

- **Where:** (i), a read-time option declared in the recipe on the data table, with the metadata read AS READ (so that the places stay as they are); (ii) as the second choice (a visible step, no new reading level) if she prefers the completion to be a step in tier 1.
- **Marker:** M1, a boolean column, the other cells left empty.
- **With B6:** the data first, the metadata second, and an advice when a table that opts in is joined with the metadata first.
- Reason: B6 as she describes it removes the false "not detected" without an anti-join, without the audit record and without a second table, and it leaves the recipe the author's. The cost she names ("a bit weird") is the added lines; they are marked, counted in the alert and shown in the Source view, so the change is never silent. Nothing is chosen for her.
