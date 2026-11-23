# Why two tables stayed identical, and solutions for entities that must appear with zero hits (2026-11-23)

**What this is.** The cause of the two tables that stayed identical below a step at the ResFinder table (ordered by her, ledger D-0563), and a catalogue of solutions for entities that must still appear with a count of zero without the metadata as the first table of the data join (her direction D-0564). Written by an Opus and a Sonnet design agent who compared their readings and agreed before this text was written (D-0552). It is written by reading and reasoning only. **No run was made for this file**, by her orders: "H1, H2 appear to be a consequence of that - so I think we need to find solution for that and then retest." (D-0565) and "no need to test that now then" (D-0566). The runs it cites were made earlier, under the evidence rules D-0558 to D-0561, and are named where they are used. NOT confirmed by her. Nothing is built; no recipe is edited.

**Where the evidence lives.** The registers `tmpAI/coordinator/design_dialogue/RUN_REGISTER_sonnet_cause.md` (every run of this investigation cancelled before it started), `RUN_REGISTER_sonnet_recipes.md`, `RUN_REGISTER_opus_recipes.md`, `RUN_REGISTER_opus.md`; the earlier runs it cites are in `PATHS_AND_DERIVED_AGREED.md` (G8) and `RECIPES_FROM_THE_MODEL_AGREED.md`. The reads made for this file are in the same scratch folder (not in git): the hand count `cause/hand23.out` (Sonnet), the scan `cause/C6.out` (Sonnet) and the readings RR11 and RR12 of Opus (`RUN_REGISTER_opus_recipes.md`; its stored tables from the earlier run read now, and a scan of the recipes with its own parse).

**The limits.** The demo recipe and, for the numbers, one entity (`10668076`). A hand count from the source files, not an engine run. The feasibility of the solutions is NOT run: it comes after her choice, in the retest described at the end.

Tags: [HER WORDS D-n] / [RECIPE FILE] / [CODE READ file:line] / [HAND COUNT] / [READ SCAN] / [ESTABLISHED: file, point] (a result of earlier runs, rebuilt from scratch, committed) / [STORED TABLES, Opus RR11] (the engine's tables of an earlier run, read now) / [REASONED, not run].

> **Update of 2026-11-23 (ledger D-0568; see `OVERLAP_AND_POPULATION.md`):** a further candidate, (a2), was found after this file was signed: a table of the analysed entities as the first table of the join, the metadata second. It keeps zeros for the analysed entities and follows your direction. The sentences below that say that every form with zeros keeps the metadata as the side whose rows stay, and that only option D follows your direction fully, are corrected where they stand.

> **Update of 2026-11-23 (ledger D-0569):** her answers on the overlap file. She accepts the false zero at the data table's own place: "here 0 means not found in the id ... that is actually maybe why we decided to join with metadata first ... So I think the match between ids in the tables is even more important." And she puts a point to consider: "the ids that are in metadata and not in the results data might require to be added to the results files.... a point to consider. then we would keep the 0 that means eg. no resitance gene was found." A new candidate, **B3**, follows from it (the result files list every analysed entity; the review session's reading of her sentence, NOT confirmed by her). It is added to the question and to the catalogue below. Not yet seen by the Opus agent.

> **Update of 2026-11-23 (ledger D-0570):** her case "a true not-detected is a true result" is studied in the new section "Added 2026-11-23 (ledger D-0570)" below, which holds the ONE two-part list of options (A to E, B2, B3 extended; new B4, B5, E2; information F and G). Three signed sentences were wrong and are corrected where they stand, each with a note: option B3 ("the metadata second keeps the zeros"), the "42 bars" of ten sentences (the plot counts samples by their number of genes), and catalogue (e) (the form lists all seven join kinds).

> **Update of 2026-11-23 (ledger D-0572):** her solution B6 (fill the data tables with the ids of the metadata, with a marker) and her answers on the control of the ids are in the new section "Added 2026-11-23 (ledger D-0572): her solution B6 and the control of the ids". B6 is HER PROPOSAL, not chosen; it is a line of Part 1 of the one list (a pointer is in the list). Nothing of the signed text is changed.

---

## HALF PAGE FOR HER

**What happened.** You remove an entity at the ResFinder table. Two tables below it stay exactly as they were: the table `QA_fanout_exhibit` (its second tier) and its plot `qa_fanout_rows_per_sample`. The number for the entity stays 23.

**What the 23 is.** The entity has 23 virulence genes. They come from the VirulenceFinder table, not from ResFinder, so a step at ResFinder does not touch them. The table counts the genes that are present; it does not count an empty row. Before and after the step the entity has 23 rows in the table, with the virulence gene filled in all 23, and the ResFinder gene is there before and empty after. [HAND COUNT: 1 metadata row, 1 ResFinder row, 23 VirulenceFinder gene rows; 1 x 1 x 23 = 23 before and after] [STORED TABLES, Opus RR11] [RECIPE FILE: `QA_fanout_exhibit` tier 2 counts `VF_gene`]
(An earlier sentence in the review said "a count of rows per entity stays 23". That wording was wrong; the committed paths file now carries a correction at each place.)

**The cause, in plain sentences.**
- The place chosen: the entity's rows in this table come by three paths (the metadata, ResFinder, VirulenceFinder). The first place of ResFinder covers one of them.
- The join direction: the metadata is the first table of the join, so the entity stays in the table with empty ResFinder values. This is the same direction that gives the zeros in the plot `qa_amr_genes_per_sample`, which is built to show every entity, some with 0 genes.
- The recipe: not a mistake of the author. The table is written on purpose as a known defect (its own text says "EXHIBIT of a known defect").
- The app: not at fault in the evidence. The stored tables of the earlier run hold exactly the rows this reading predicts: the ResFinder column emptied, the 23 virulence genes intact. Twelve of the 14 tables below changed in that run. [STORED TABLES, Opus RR11; ESTABLISHED: PATHS G8]

**Is the unchanged plot right?** It is right for what it counts: the non-empty virulence genes of each entity after the join. On the demo this equals the rows, because every row has a virulence gene. A user who removed the entity at ResFinder and looks at this plot sees the same bar, and could wrongly conclude that the removal did nothing, or that the entity is still in the ResFinder analysis. After a removal at the VirulenceFinder table the entity would keep 1 row (from the metadata) and show 0. [RECIPE FILE; HAND COUNT; REASONED for the last sentence]

**The core fact.** A zero is an entity that has no data row. An entity removed at the data table also has no data row. The two are the same state of the table. So, within your rules (an audit step is a filter, a column drop or a removal by key, written after your steps), no solution can give "entities with no data row appear with 0" and, at the same time, "a removal at the data table takes the entity out completely". Only the path that carries the population, the metadata, tells them apart. [REASONED; her rules D-0322, D-0541]

> **Correction of 2026-11-23:** Only the path that carries the population tells them apart: the metadata, or a table of the analysed entities (a2). (The sentence above says "the metadata"; the Opus agent's replacement of the neighbouring sentences is below.)

> **Answered by her, 2026-11-23 (D-0569):** the false zero at the data table's own place is accepted: "yes because here 0 means not found in the id ... that is actually maybe why we decided to join with metadata first ... So I think the match between ids in the tables is even more important."

**Your direction, and the fact that meets it.** You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564] The fact: to show an entity that has no data row, the table must keep the metadata's rows. So in every form with zeros the metadata is the side whose rows stay. Only the form without zeros follows your direction fully. The question is at the end of this half page and in the next section.

> **Correction of 2026-11-23:** In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros.

---

## THE QUESTION FOR HER, as it would be put

> **Update of 2026-11-23 (ledger D-0570):** the list of options below (A to E, B2, B3) is extended in two parts in the next section "Added 2026-11-23 (ledger D-0570): a true not-detected is a true result"; that section holds the ONE list (new: B4, B5, E2 and the information options F and G). Read it with this question.

**Plainly.** You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564]. Here is what is true. For a result that shows one entry per observation (for example every gene found), the data first and the metadata second works today: a step at the data table or at the join place removes the entity completely; a step at the metadata place only empties its metadata columns. [ESTABLISHED: RECIPES G5] For a result that must show every entity with a zero, there is no way to write it in which the data table's own place also takes the entity out. The zero and the removal are the same state of the table. So the question is about the zero.
Your direction and the zeros cannot both hold. To show an entity that has no data row, the table must keep the metadata's rows. So in every form with zeros (A, B, C, E) the metadata is the kept side: first with a left join, or second with a right or full join. Only D follows your direction fully, and D has no zeros. Why: a row for an entity with no data can only come from the metadata. How you would see it: in A, B, C and E the plot keeps counting 42 samples, an entity removed at the data table in the bar at 0; in D it counts 38 samples and has no bar at 0. (E follows the order in your words, the metadata second, but not the reason you gave in D-0549, that the metadata's extra entities stay out of the table.) [REASONED]

> **Correction of 2026-11-23:** In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros.

**On the demo you would SEE** (the plot `qa_amr_genes_per_sample`: 42 entities in the metadata, 38 with a ResFinder row, so 4 with 0 genes). You remove one entity at the ResFinder table. Today [run] and with (a), (c), (e) [reasoned] the entity stays in the plot with 0 genes, like the 4 others. With (b) it is the same; if you allow the sentence of PATHS Q6, the dialog says before you apply that the step covers 1 of 2 paths and the entity can remain. With the step written at the join place, or with "Remove from all the data", the entity is gone and the plot shows 41 entities. With (f1) (option D) the plot shows 38 entities and no zeros, and a caption says 4 entities have no ResFinder row. [numbers: raw files and the earlier runs; ESTABLISHED: PATHS G8, RECIPES G6]

> **Correction of 2026-11-23:** **With (a2) (option B2)** the plot of the demo counts the same 42 samples, because every metadata id is in `FastP` (42 of 42), the table that stands for the analysed entities in this example. The difference appears only with an entity of the metadata that was never analysed: it is absent with (a2) and shows 0 with A.

**Options** (what each means is in the catalogue below; none is chosen)
- **A.** Keep the zeros; the default place for a removal is the join; the dialog says how many paths a step covers (b). "Remove from all the data" stays a choice (f4). The pattern goes on the good-practice page. Nothing to change in the recipe.
- **B.** Keep the zeros and write the data per entity first (a), so that long tables do not weigh the entity. It needs a second table on the same file. The false zero stays when the data table's place is chosen; the dialog says so.
- **B2.** Keep the zeros with a table of the analysed entities as the FIRST table of the join, the counts next, the metadata second (a2); the zeros come from the first table, which lists the analysed entities. It follows the order of your direction (the data first) and its reason (the metadata's extra entities stay out). It needs no new key; its parts run today, the whole chain is not run yet. The false zero stays when the counted data table's place is chosen, and "analysed" is relative to one analysis. [added 2026-11-23]
- **B3.** (The review session's reading of her last sentences; NOT confirmed by her.) The result files list EVERY ANALYSED ENTITY, with an empty result when nothing was found (for ResFinder, the 4 entities with no gene would each have one line with an empty gene), so that a 0 means "analysed, nothing found". Then the result file itself has a line for every analysed entity, so a join with the result table first and the metadata second (`left`) keeps those entities and their counted 0: the rows come from the result file, not from the metadata. A removal at the data table's own place then removes the entity completely (no false zero), and no join starts from the metadata. With today's result files, which list findings only, the result table first and the metadata second keep only the entities that have a line: an entity with nothing found is absent, and there is no 0. The rows are added by whoever makes the file (the pipeline or the user), not by the recipe. Risk: the app cannot know whether an id missing from a result file means "not analysed" or "analysed, nothing found"; adding all the metadata ids would mix the two. On the demo [reasoned, not run] you would see the same 42 samples counted, 4 of them in the bar at 0; the ResFinder table would show 4 more lines with an empty gene; a removal of one entity at ResFinder would leave 41 samples counted. **What it gives up:** the recipe's own steps that count rows or stamp a value would read the empty line as a hit (in `ResFinder`: `total_gene_count` 1 and `status` "Detected"); they would need to be adapted, or the file would carry an explicit "analysed" column that the recipe reads. [added 2026-11-23]

> **Correction of 2026-11-23 (ledger D-0570):** the sentence of option B3 about "the data first and the metadata second" was wrong as written: the metadata never adds an entity when it is second in a left join; the zeros come from the result file's own lines. It is replaced above by the sentence that names the result file as the source.
- **C.** The app, not the user, knows that the result is per entity (f5), or also which zeros are filled: the recipe declares the completion of the population (c), or the app completes it at the plot (f3). Needs a new key or an app behaviour.
- **D.** No zeros: data first, metadata second, and a caption states the population (f1). Removal is complete everywhere. The plot `qa_amr_genes_per_sample` changes its meaning.
- **E.** A right or full join, so that the metadata is written second (e). It still keeps the metadata's rows, so you would see the same as A: 42 samples counted, an entity removed at the data table in the bar at 0. Your graph model follows such a join like any other (its parents are the same tables). The old reading code does not follow these kinds (D-0452); the new one is not built. Whether the engine builds it as expected is a run after your choice.
- **Neither: say what you meant.**

**My lean, as a lean:** A for the default and the information, B for the demo tables that multiply rows (`QA_fanout_exhibit`, `ST22_Anchor`), D for results that do not need zeros (`QA_population_zscore`). Reason: at the default place it removes the entity completely; it tells the user the one thing that can surprise (the false zero at the data table); and it keeps the zeros the plot is written to show. `QA_fanout_exhibit` is a deliberate exhibit of a defect: changing it changes its purpose. C stays open if you want the app, not the user, to know which zeros are filled; E changes only the order in the file. [REASONED]

> **Correction of 2026-11-23:** Lean of the Sonnet agent with (a2) added: B2 where the recipe has a table that lists the entities this analysis ran on, A otherwise; B for the demo tables that multiply rows; D for results without zeros. Lean of the Opus agent, as a lean: the same as the Sonnet agent. B2 where the recipe has a table that lists the entities this analysis ran on, A otherwise; in both, the default place at the join and the dialog's information on the false zero. Reason: B2 is the only form with zeros that follows both the order and the reason of your direction, and its zeros mean "analysed, zero hits" for that analysis. The false zero at the counted table's own place remains in every form with zeros, so the default at the join and the information stay needed.

> **Added 2026-11-23 (ledger D-0569):** lean of the Sonnet agent on B3, as a lean, changed after reading the Opus agent's reason: B3 where the pipeline that makes a result file knows every entity it analysed and can list it, in a form that the recipe's steps read correctly (an explicit "analysed" column rather than a line with an empty gene, because the demo's own steps count rows and stamp "Detected"); B2 where the files cannot be changed; A otherwise. Reason: with B3 a 0 means "analysed, nothing found" and a removal at the data table is complete; but the app cannot check that the rows are right, and the pipeline or the user decides.

> **Added 2026-11-23 (ledger D-0569):** lean of the Opus agent on B3, as a lean: B3 where the pipeline that makes a result file knows every entity it analysed and writes that fact into the file, preferably as an explicit "analysed" column that the recipe reads rather than as a line with an empty gene; B2 where the files cannot be changed; A otherwise. Reason: B3 puts "analysed, nothing found" where it is known (the pipeline), gives her 0 the meaning she wants ("then we would keep the 0 that means eg. no resitance gene was found", D-0569), and makes a removal at the data table complete; but an empty gene is read as a hit by the steps that count rows or stamp a status, so the form of the file must be agreed with the recipe.
**Reopens (information):** D changes the purpose written in the plot itself (a sample without a gene must appear at 0); it reopens no decision of yours. E asks the audit to follow right and full joins (D-0452, D-0460 "B; if needed we try to find a solution later"). C touches the same question as her question 27 (a step reading another table in tier 2).
**Links:** Q6 of `PATHS_AND_DERIVED_AGREED.md` (the sentence "can remain"; its use depends on her answer to that question); (iv) the side of the metadata and (ii) the result with zeros of `RECIPES_FROM_THE_MODEL_AGREED.md`; both are answered, in part, by this choice.

---

## Added 2026-11-23 (ledger D-0570): a true not-detected is a true result

Not yet in the signed text above. This section holds the ONE list of options for the zeros, in two parts; the earlier list (A to E, B2, B3 in "THE QUESTION FOR HER") is extended here, not replaced.

**Her words, exact** (channel block M624): "I think there is a bit of logical problem and that will depend on the join type we use with the metadata AND what a no result means. I do not understand what you mean by "metadata second keeps the zeros" the metadata itself should have id with non empty lines. But if results are 0 as no gene found for example then we should be able to complete the table - this can be done in the recipe but the problem we need the ids that were in metadata and are not in the data table - where we go back to your population example. So we need to have results for the initial population and information about what 0 or missing means." Then: "I think the data check information as suggested. And true not detect is a true result - So if we need eg. to see how many samples are not detected I need to make a later anti-join (which I would avoid as much as possible) or a join where metadata is on the left side ...and fill the blanks in the recipe ... can we investigate possible solutions for this case ? 4. yes the validated question - yes . information is very important here." [HER WORDS D-0570]

**Correction first.** The sentence "metadata second keeps the zeros" was wrong as written. With the data table first and the metadata second (`left`), the metadata never adds an entity. An entity with no row in the first table is absent. A zero stays only where the first table already has a row for the entity: a result file that lists every analysed entity (B3), or a table of the analysed entities used as the first table (B2).

**What is asked.** Two outputs: the number (how many entities are not detected; on the demo, 4 of the 42 entities have no ResFinder line, and the files do not say whether they were analysed) and the list (which ones). And, beside them, the information about what a 0 or a missing value means.

### The facts

1. **The states of an entity, for one result table.** Detected. Analysed, nothing found (your "true not-detected"). Not analysed (or the analysis failed for it). Removed by key at the result table's own place (an audit step: the entity is excluded; it is not a result). Gone (removed at the join place, or everywhere with "Remove from all the data"). [REASONED]
2. **A filter on values or a removal by key.** At a result table whose columns, the entity id aside, all describe a detection (on the demo ResFinder: `gene`, `predicted_phenotype`, `identity`, `overlap`), a filter on values ("nothing found at identity 90 or more") leaves an entity with no line that is truly "not detected under that rule". There, a removal by key (a list of entities) is the only step that makes a false "not detected". The rule of the filter belongs to the meaning of "not detected". [RECIPE FILE `input_fields/ResFinder_input_fields.yaml` lines 1, 6, 10, 14, 18: `sample_id`, `gene`, `predicted_phenotype`, `identity`, `overlap`; RULE FILE `ui_implementation_contract.md` 12a: the audit steps are a filter, a column drop and a removal by key]
3. **Today no false "not detected" shows yet.** HOME writes the audit step at the plot's own table [RULE FILE `ui_implementation_contract.md` section 2: "Today an audit step is written at T3 of the plot"]. For `qa_amr_genes_per_sample` that is the per-entity table (one row per sample, no tier-3 steps): a removal by key takes the row out, 41 samples. The false "not detected" comes with the earlier places (decided, not built: D-0316 to D-0318, D-0337), which let you write the step at the ResFinder table. A removal by key at a plot's own table needs the entity id there: for a plot whose table has none (for example `QA_aggregated_no_key`) it cannot be written at that table [ESTABLISHED: RECIPES G8].
4. **A removal at the result table's own place changes the number.** On the demo: 38 samples with a ResFinder line, 4 without (42 samples; the bar at 0 holds 4; in your route (ii) the 4 count as not detected). Write a removal of one detected entity at the ResFinder table: 37 / 5; the removed entity now counts like the 4. At the join place (your default, D-0549): 41 samples, 37 / 4. [ESTABLISHED: PATHS G8 (the entity keeps one row, count 0); the counts from the files]
5. **An entity never analysed counts as not detected** when the metadata comes first. Your own reason in D-0549: "some users will have metadata for more samples". Today's metadata says nothing about which analysis ran on which entity (its fields: `sample_id`, `source`, `year`, `country` [RECIPE FILE `input_fields/metadata_schema_input_fields.yaml` lines 1, 7, 11, 15]).
6. **A metadata line with no id counts as an entity with no result** in both of your routes. A missing key never matches, so an anti-join keeps it, and a left join from the metadata keeps it, and a grouping by the id makes one group of all the missing ids (Polars semantics, not run). Your sentence: "the metadata itself should have id with non empty lines". On the demo the metadata has no empty id; `demo_abromics` has 3 id-less lines on purpose, removed by the first step of its join's tier 1, before the join step itself; the metadata's own tier 1 is empty, so the table `metadata_schema` still holds them (`demo_abromics.yaml:30-31, 44-47`). [CODE READ `libs/transformer/tests/test_self_join_build.py:169`; ESTABLISHED: OVERLAP section 1]
7. **The aggregate decides 0 or missing.** After a left join from the metadata, an entity with no line has one row with empty result columns. A count of non-empty values gives 0 (the demo's `QA_AMR_per_sample`). A count of rows (`pl.len()`) gives 1 (the demo's ResFinder tier 2 counts rows: under B3 an empty-result line would count 1). A sum gives 0. A mean, minimum, maximum or standard deviation gives missing. A fill of 0 on a mean writes a value that was never measured. [RECIPE FILE `QA_AMR_per_sample_tier2.yaml`, `ResFinder_wrangling_tier2.yaml`; the others: Polars semantics, not run]
8. **What can and cannot be written as an anti-join today.** The kind `anti` is in the join step's form (seven kinds: inner, left, right, full, semi, anti, cross) [CODE READ `polars_calls.py:85`], and `maintain_order` is required in the step [CODE READ `polars_calls.py:60`]; an existing engine test builds one [CODE READ `libs/transformer/tests/test_self_join_build.py:34-43`; not run for this file]. It can be written as the tier-1 step of a joined table of its own. It cannot be written "later": a join is refused outside tier 1 (ST05, [CODE READ `recipe_check.py:714-715`]) and a join of a join is refused (J04, [CODE READ `recipe_check.py:866-867`]); a join reads the tier 1 of each ingredient only [CODE READ `orchestrator.py:269-294`], so it cannot see a detection rule written in a result table's tier 2. A join with the metadata after tier 1 would reopen "join with metadata must be done at T1" [HER WORDS D-0510]. The audit cannot YET follow an anti-join [HER WORDS D-0452: "App cannot YET describe (or follow? )"], and a place it cannot trace is red and not tickable (D-0460; her answer: "B of needed we try to.fimd a.solutiom later"); whether the new graph model traces it, with its inverted effect, is open. An anti-join INVERTS a removal: a removal at the ResFinder table ADDS the entity to the list. [REASONED]

### The question, in two parts (one list, one naming)

(The option letters are not the letters of the catalogue below: option A is catalogue (b), option B catalogue (a), and F is not catalogue (f).)

**Part 1: the form of the result (one choice).** For each: what the author writes; what you would see on the demo before and after you write a step for one detected entity at the result table the per-entity join reads (ResFinder, or its count table in the forms that count first) (38 / 4, then 37 / 5, or 41 at the join place); a step at the ResFinder table does not reach a count table made from the same file [ESTABLISHED: RECIPES G6]; what stays false; what it asks of the files. "NEEDS A RUN" marks what can be judged only after your choice.

- **A. The metadata first, the blanks filled in the recipe, the meaning named in a column** (your route (ii); today's demo, plus a status column). The author keeps today's `QA_AMR_per_sample` and adds a column that says what a blank means (for example `detection`: "detected" or "not detected"), published by the last `polars_select`. A word filled into the gene column itself would be counted as a gene by a count of genes (`demo_abromics.yaml:55-57` fills a category column with "Non Determined", which is right for a category). You see 38 detected, 4 not detected. After the step at the ResFinder table: 37 / 5 (false: the entity was never shown not detected). At the join place: 41 samples, 37 / 4. Asks of the files: nothing. What a blank means is the author's statement in the recipe; today ResFinder's description reads "AMR gene detection (Gene detection)" and does not say that the file lists findings only [RECIPE FILE `1_test_data_ST22_dummy.yaml:100`]. NEEDS A RUN for the whole chain with the status column.
- **B. Count per entity first, then the metadata first.** As A, with no multiplication of rows: 38 / 4. A step at the count table's own place: 37 / 5 (false). A step at the ResFinder table does not reach the count table [ESTABLISHED: RECIPES G6].
- **B2. A table of the analysed entities first, the metadata second** (the analysed population). On the demo `FastP` stands for that table (42 of 42): same as A. After the step: 37 / 5 (false). Asks: a table that lists the entities THIS analysis ran on. The metadata's never-analysed entities stay out. NEEDS A RUN with one never-analysed entity.
- **B3. The result files list every analysed entity** (an explicit mark, an empty gene for nothing found), the data first, the metadata second (the analysed population). You see 38 / 4, the 4 counted from their own lines. After the step at the ResFinder table the entity's lines are removed (for an entity with nothing found, its empty-result line too): 41 samples, 37 / 4 (no false result). Asks: the pipeline (or the user) writes the lines; the recipe's steps that count rows or stamp "Detected" must be adapted. NEEDS A RUN (empty cells read as missing).
- **B4 (new). The metadata first and a table of the analysed entities: the initial population in three states** (detected, not detected, not analysed). You see 38 / 4 / 0 not analysed. After the step: 37 / 5 / 0 (false). It separates the entities never analysed. Asks: a manifest of the analysis. NEEDS A RUN with one never-analysed entity.
- **B5 (new). B3's files, the metadata first, a column "has a line", no fill: three states** (detected, not detected, no result). You see 38 / 4 / 0. After the step at the ResFinder table: 37 / 4 / 1 no result (no false result). Asks: B3's files. The ResFinder steps that stamp "Detected" change with it. NEEDS A RUN.
- **C. The app labels three classes, from the declared population** (the old C, extended). The recipe or the app completes the per-entity result from the declared population; with the declaration of G below and the record of your audit steps, the app labels detected, not detected and removed. Variants kept inside C: the recipe completes (catalogue (c), not buildable today), the app completes at the plot (f3), the recipe says the result is per entity (f5). You see 38 / 4. After the step: 37 / 4 / 1 removed. Asks: the promise that every entity of the population was analysed. NEEDS A RUN and a decision (a new key, a new edge in the graph; the export must carry the rule).
- **D. No zeros.** The not-detected only in words (a caption, the data check's note). You see 38 samples and no bar at 0. After the step: the entity is gone.
- **E. A right or full join, the metadata written second** (its rows kept). Same as A on the demo (38 / 4; after the step 37 / 5, false). Not followed by the audit yet. NEEDS A RUN.
- **E2 (new). An anti-join as a table of its own: the LIST of the entities with no line** (your route (i)). The author writes a joined table of the metadata and ResFinder with `how: anti` and `maintain_order: left_right`. The table has 4 rows; today you see it through the data preview of a plot that reads it (a table as a result is decided, D-0485, and not built). After the step at the ResFinder table: 5 rows (the entity is ADDED: false). Not "later": a table of its own, next to the per-entity table. The audit cannot yet follow it (red, not tickable). NEEDS A RUN.
- **B6 (new, HER PROPOSAL; ledger D-0572). Fill the data tables with the ids of the metadata, with a marker "data file has no result"; the recipe says how marked lines are processed.** Not chosen. Its line (what the author writes, what you would see before and after a removal for each join direction, what stays false, what it asks) is in the section "Added 2026-11-23 (ledger D-0572)" below, with the questions that remain.
- **Neither: say what you meant.**

**Part 2: the information about what a 0 or a missing value means (with any form, or none).**
- **F (new). A line with the result from the declared population:** "population 42; with a line in ResFinder 38; without a line 4". After a step at the ResFinder table: "with a line 37; without 5, of which 1 removed by an audit step". After a step at the join place the line must still match the result you see (41 entities); its words are not decided. It needs only the existing optional `entity.population` and the entity id; it is written into the export too (what you see is what is exported). Needs an app feature; NEEDS A RUN once built.
- **G (new). F plus the meaning, declared by the recipe for each result table** ("no line here means: nothing found"), repeated by the data check, the dialog and the report. A new key in the format; the population is taken from `entity.population` (one place). It cannot check that the statement is true.
- **Neither: say what you meant.**

**Common to every form.** The default place at the join (D-0549) and "Remove from all the data" (D-0416) take the entity out. The data check's notes (both directions; decided, D-0570; not built) go with every form.

**Reopens (information).** A, B, B4 and B5 start from the metadata, E keeps its rows and C completes from it: your direction "the join should not start with the medata or we need a solution we do not have yet" [HER WORDS D-0564]; you name the metadata on the left yourself as one route [HER WORDS D-0570]. E and E2 use kinds the audit cannot YET follow [HER WORDS D-0452] and "The documentation should NOT recommend those joins" [HER WORDS D-0486]. A later anti-join with the metadata would reopen "join with metadata must be done at T1" [HER WORDS D-0510]. C adds a new edge in the graph (a completion that reads the population after the join; catalogue (c)).

**Leans, as leans (two agents, two sentences).**
- Lean of the Sonnet agent, as a lean: B5 where the pipeline can write explicit lines for the entities it analysed; where the files cannot change, A with F and the default place at the join (B4 where a manifest of the analysis exists); F or G with every form; no lean on E2.
- Lean of the Opus agent, as a lean: B5 where the pipeline that makes a result file can write a line for every entity it analysed, with an explicit column that says so; where the files cannot change, A (or B4 where a manifest of the analysis exists) together with G and the default place at the join; F or G with every form; no lean for E2. Reason: B5 is the only form in which the recipe's own table, with the initial population, shows "no result" instead of a false "not detected" after a step at the result table's own place (C does it in a table the app completes, on the promise that every entity was analysed); F and G let the app itself say how many entities have no line, how many of them your own steps removed, and (G) what a missing line means, and you said "information is very important here" [HER WORDS D-0570]; E2 splits the population into two tables, the audit cannot YET follow it, and a step at the result table adds the entity to it.

**Open and yours (plain questions).**
1. Do you want an entity of the metadata that was never analysed to count as "not detected"? (A, B, C, E and E2 count it; B2, B3, B4, B5 and D leave it out or name it; F and G say how many entities have no line, not which of them were analysed.)
2. What should the third class be called: "no result", "removed", "not analysed"?
3. May the app read the record of your audit steps to say "removed by your step"? It adds no step; it reads. In C the result table then depends on that record, so the export must carry the rule.
4. Where should the recipe say what a missing value means: once for each result table, for each column, or only through the population?
5. Do you want the count per target too ("how many entities carry no target X", on the demo: no gene X)? No form above covers it.
6. Should the recipe say at which threshold "not detected" holds (for example identity 90)?
7. The list of the not-detected as a result: a table as a result is your decided design (D-0485, D-0487, not built). Do you want the number, the list, or both?
8. `demo_abromics`: keep its three id-less lines (a lesson, removed by a visible step) or remove them from the file?

**Corrections made in this file by this section** (each also marked where it stands):
- Option B3 (the sentence about the data first and the metadata second) and a clause at option B2.
- "42 bars": the plot `qa_amr_genes_per_sample` counts samples by their number of genes (`x: n_amr_genes`, `geom_bar`): "42 samples counted, 4 of them in the bar at 0" [RECIPE FILE `plots/qa_amr_genes_per_sample.yaml`]. Ten places in this file and one in `OVERLAP_AND_POPULATION.md`.
- Catalogue (e): the form of the join step lists all seven kinds.
- Two corrections concern the two agents' own scratch positions, not these files, and need no edit here: a table as a result is a decided design, not built (D-0485, D-0487); a later anti-join with the metadata meets D-0510, not question 27.

---

## Added 2026-11-23 (ledger D-0572): her solution B6 and the control of the ids

**Her words, exact** (channel block M627). Her answers to the facts: "2. Yes true but if the sample is bad then no detection can exist because sample is bad in this case it is still good to remove from the analysis and have it rerun in another batch to be analyzed later. So audit can cover this case and justification holds. 3. yes but not so usefull for our case .. because we do not have ids with no values ... 4. this is true that is why the ids of both metadata and data sets should overlapp (or at least all in metadata and included for data sets) 5. true that is why metadata should be clean - all with an id ... 6. I think the solution would be to fill the data tables with the id contained in the metadata and have a "data file has no result" NA ? that can be then processed as a normal recipe - saying how those need to be processed in the recipe. Its a bit weird solution but it would work in all cases forcing the recipe maker to consider this case. and then missing data in the original files need to be processed correctly according to the correct meaning - which only a recipe maker (in collaboration with a real user) can decide. That would remove need for 6 anti join. and make decisions on how to procede with those clearn in the recipe so 7. All is clear and decided." Her answers to the needs: "1. yes we need a control of ids - as we started to implement - warnings in case something was wrong in the metadata so the user can recheck (as was planned recently) - if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done, if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) that would - that would be clear and mentionned both in literature and allerts. for the missing ids - but this might be before T1 a step the app does ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe) 2. we could need good marker convention - short and explicit - and I think it should be a different kind of other "missing value" because then the recipe maker has to consider those cases specifically and the 3. it knows the risk it accepts". [HER WORDS D-0572]

**What is settled, and what is her PROPOSAL.** Settled by her words: a removal because a sample is bad is right, the audit covers it and its justification holds; the ids of the metadata and of the data sets should overlap, or at least all be in the metadata and included in the data sets; the metadata should be clean (an id on every line); the meaning of a missing value is for the recipe maker with a real user; "it knows the risk it accepts" (our reading: "it" is the recipe maker, who "has to consider those cases specifically"; the risk is that the app cannot tell "not analysed" from "analysed, nothing found"). **B6 is HER PROPOSAL, not chosen**: fill the data tables with the ids of the metadata, with a marker "data file has no result".

### B6 as a line of Part 1 of the one list

**B6 (new, her proposal). Each result table that has an entity id gets one added line for every id of the metadata that its file does not hold, before the recipe's steps; the added line is marked; the recipe says how marked lines are processed.**
- **What the author writes.** A key on the data table, for example `complete_from_population` with a marker name and, if the check requires it, a `meaning` (invented; refused today as an unknown key, S01 [CODE READ `recipe_check.py:390`]; the names are provisional). The recipe's own steps then process the marked lines.
- **What you see on `qa_amr_genes_per_sample`** (42 entities; ResFinder 70 lines for 38 entities; 4 without). ResFinder grows from 70 to 74 lines, 4 marked. After a removal by key of one detected entity, written at the end of tier 1 of the ResFinder table:

| | Data first, the metadata second (left) | Metadata first, the marker published and read by the recipe | Metadata first, the recipe counts genes only (today's) |
|---|---|---|---|
| Before any step | 42 samples, 4 in the bar at 0 | 42 samples: 38 detected, 4 "no result in file" | 42 samples, 4 in the bar at 0 |
| Removal at the ResFinder table | 41 samples, 4 in the bar at 0: no false result | 37 detected, 4 "no result in file", 1 "no line": no false result | 42 samples, 5 in the bar at 0: **false** |
| Removal at the join place | 41 samples, 4 in the bar at 0 | 41 samples: 37 / 4 | 41 samples, 4 in the bar at 0 |
| Removal of one of the 4 added entities at the ResFinder table | 41 samples, 3 in the bar at 0 | 38 / 3 / 1 "no line" | 42 samples, 4 in the bar at 0 |

  [REASONED from the engine order (`data_wrangler.py:92`, `orchestrator.py:282-295`) and the join semantics; NEEDS A RUN after your choice]
- **What stays false.** With the metadata first and a recipe that counts genes only, a removal at the result table still counts as "not detected" (the entity stays by the metadata). B6 removes the false result with the data table first, or with the metadata first if the recipe reads the marker.
- **What it asks.** Nothing of the pipeline. A statement in the recipe of what the marked lines mean. The recipe's steps that stamp a value or count rows must be adapted (flags 1 and 2 below).
- **How it differs from the others.** From B3: B3's lines come from the pipeline, which knows what it analysed, so they mean "analysed, nothing found"; B6's lines come from the metadata, so they mean only "the data file has no result for this id". From B5: B6 works with today's files and gives its column for free. From E: E completes at each join, after the result table's own place; a removal at the result table leaves the metadata's row; B6 completes in the table itself. From E2: no anti-join; the list of the not-detected is the marked lines. From C: C completes late and needs the audit record to name a removal; B6 needs no audit record. From the withdrawn T0 ("no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" [HER WORDS D-0509]): T0 filtered the original data; B6 ADDS marked lines and removes nothing.
- **NEEDS A RUN** (section "Runs after your choice").

### The flags (what would change a result without saying so)

1. **The added lines are stamped "Detected".** ResFinder's tier 1 stamps every line `status: pl.lit('Detected')`; `ST22_Anchor` keeps `status`; the plot `integration_plot` fills its tiles by `status` [RECIPE FILE `ResFinder_wrangling_tier1.yaml`; `ST22_Anchor_wrangling_tier1.yaml:47`; `plots/integration_plot.yaml:9`]. With B6 the 4 entities would show "Detected" with no error.
2. **Tier 2 counts rows.** `total_gene_count: pl.len().over(['sample_id'])` gives 1, not 0, for an added line [RECIPE FILE `ResFinder_wrangling_tier2.yaml`].
3. **A filter in tier 1 and a completion before tier 1 disagree.** `Detailed_summary` has three threshold filters in tier 1 (`Detailed_summary_wrangling.yaml:20, 25, 30`); its file holds 42 ids and its table 36 after tier 1 [ESTABLISHED: RECIPES G12]. A completion before tier 1 adds nothing there, and the filters then remove all the lines of 6 entities; a completion after the recipe's tier-1 steps would give those 6 entities a marked line.
4. **If the completion reads the metadata after its tier 1,** ResFinder's first place lies below the metadata's place, and choosing both is refused by "the user chooses at most one place" [HER WORDS D-0553].
5. **B6 alone does not force the recipe maker to consider the case.** A step that stamps or counts rows reads an added line as a line, with no error. The force must come from a required statement of the meaning (a required field, as the project already requires a parameter whose absence would hide a choice that changes the result [CODE READ `polars_calls.py:54-60`]), or from a check.

### Where the completion can live (her open question)

The engine order, read: a data table is read by `_read_source` (the declared types, `strip` and `null_values`), then `ingredient_parts` picks the steps of its tier 1 [CODE READ `app/modules/orchestrator.py:264-267, 282-295`]; in an audit copy the steps of a tier are the author's steps, then the audit's [CODE READ `libs/transformer/src/transformer/data_wrangler.py:92`: `return steps + audit_list`]. The Source view reads the same `_read_source` and the plan of every place reads the same lists [CODE READ `orchestrator.py:287-300`]. A completion put in `ingredient_parts`, after `_read_source`, leaves the Source view true to the file and runs BEFORE any audit step.

| | (i) A read-time option declared in the recipe on the data table | (ii) A new tier-1 action written by the author | (iii) Preparation outside the recipe (pipeline, Data Import helper) | (iv) The app writes a first step into the audit copy only |
|---|---|---|---|---|
| What the author writes | a key on the table (variants: (i-a) on each table; (i-b) every table that declares an entity id is completed and the key states the meaning; (i-c) automatic, no key) | a first step in tier 1 naming the metadata (a new action: none appends rows today; a schema's tier 1 has no ingredient) | nothing; the recipe declares the marker column among the fields | nothing |
| What you see | Source view: the file (70 lines); T1: 74 lines, 4 marked; the alert; the export's T1 file holds the 74 lines and says how they were made | Source: the file; T1: 74; the step is visible | the file already has the lines; the alert | the audit panel shows an extra step |
| "The app never modifies the recipe" | holds in (i-a), (i-b): the recipe states it; in (i-c) the recipe says nothing, so the export must record the app's rule and version | holds | holds for the recipe; the data is changed outside it (the overwrite of a data file with no copy is not decided: DATA-IMPORT-OVERWRITE) | does not fit |
| A step at the end of tier 1 | runs after the completion: no re-adding | runs after if the completion is the first step | runs after | cannot be first: audit steps run after the author's steps (D-0541), and an audit step is a filter, a column drop or a removal by key (D-0322); the result without an audit would differ |
| Keys and graph | the table's key must include the metadata's file and the option (`cache_keys.py:14-20`: `rC` the definition, `dC` the files the table reads): a change of the metadata changes the key of the table and of everything below (D-0560); a new edge into the table | the same, from the step | the file's hash changes; no new edge | not applicable |
| NEEDS A RUN | yes | yes (and an engine change) | no for the recipe side | no |

**Which metadata the completion reads.** (α) as read from its file (its declared `strip` and `null_values`, before its tier 1): the edge comes from the metadata's file; the places stay as they are; a removal at the metadata's place does not remove an added line. (β) after its tier 1, with its audit steps: a removal at the metadata's place removes the added line, but ResFinder's first place lies below the metadata's: two places on one path (flag 4).
**Position inside the table.** P1, before the author's tier-1 steps: the marker means "the data file has no line for this id" (your words); the author's steps see the added lines (flags 1, 2). P2, after the author's tier-1 steps and before the audit steps: the marker means "no line left after the recipe's rules"; the author's tier-1 steps do not see the added lines, so no tier-1 step can say how to process them. After the audit steps is never right: the completion would add back an entity the user removed.
**Does the completion re-add an entity removed at the result table?** No, in P1 and P2. **Does a removal at the metadata remove it from the completion?** Only in β.

### The marker (short and explicit; a different kind of missing value)

Polars has one missing value (null), and NaN for floats; there is no second kind of null [POLARS SEMANTICS]. A second kind must be carried by something other than the empty cell.
- **m1. A yes/no column** (for example `no_result_in_file`: true on added lines, false on file lines), every result cell of an added line empty. Counts of values stay right (`gene.count()` 0); a step can test the column. After a left join from the metadata an entity with no line has the column empty: a third state, "no line".
- **m2. A sentinel text** in each text column: it counts as a value (`gene.count()` would give 1 for each of the 4); a number column cannot hold it.
- **m3. A marker per column type** (a word, NaN for floats): NaN is a float value, not a missing one; counts and means change in different ways.
- **m4. Empty cells only:** not a different kind of missing.
A cell of only spaces is not the marker: the ingestion strips the text and turns only the listed null words into missing, so with `null_values: []` it stays an empty text [CODE READ `libs/ingestion/src/ingestion/declared.py:115-120`].
What the checks can verify with m1: the recipe check, that the table declares an entity id, that the population exists (E02), and as information whether a step below names the marker (a match on the text of formulas, `polars_calls.py:82`); the data check, how many lines were added and for which ids.

### The control of the ids (hers)

(a) An id in a result file and in no metadata: the data check informs and tells the user to fix it; she prefers the metadata corrected; a marker "not in metadata" is the alternative (a second yes/no column on the lines whose id is in no metadata; no line is added or removed). (b) An id in the metadata and in no line of a result file: the automatic completion at the first step, said in the documentation and in the alerts (what the alert says: the file, how many lines were added, which ids, the marker, and "the app cannot tell whether they were analysed with nothing found or not analysed; the recipe says how they are counted"). (c) Metadata lines with no id: the metadata should be clean; the completion adds only ids that exist; the third note of the data check stays. (d) An id repeated in the metadata (not raised by you): the completion adds one line per distinct id; a join with the metadata second multiplies the rows of a repeated id; a note covers it. The demo's metadata has 42 rows and 42 distinct ids.

### The risk (your words)

"it knows the risk it accepts" [HER WORDS D-0572] (our reading: "it" is the recipe maker): the app cannot tell "not analysed" from "analysed, nothing found". The recipe maker, with a real user, decides; the alert and the documentation say so. On the demo nothing shows the risk: every metadata id is in every result table except ResFinder, and in `FastP` (42 of 42). A metadata that lists entities never sequenced would add a marked line for each to every result table. A table where absence means something else (an entity with no virulence gene) gets the same marker; the recipe maker reads the pipeline's documentation.

### Her eight questions: settled or not

| Question | Her words settle | Remains |
|---|---|---|
| 1. A never-analysed entity counted as "not detected"? | settled: the marker says "no result"; "only a recipe maker (in collaboration with a real user) can decide" | nothing for the app |
| 2. The name of the third class | "short and explicit", "a different kind of other missing value" | the short name |
| 3. May the app read the audit record to name a removal? | not answered; needed only for C and the line F | open, smaller |
| 4. Where the recipe says what a missing value means | "saying how those need to be processed in the recipe" | whether a required statement or only the steps |
| 5. The count per target | not answered | open |
| 6. The threshold in "not detected" | not settled by her exact words (her "3." is relayed by the review session as a filter on values) | open, low priority; flag 3 shows where it matters |
| 7. The number, the list or both | B6 gives both from one table | how the list is shown |
| 8. `demo_abromics`'s three id-less lines | "metadata should be clean - all with an id" and her order of D-0569 | to confirm in the dry run (D-0525) |

### Leans, as leans (two agents, two sentences)
- Lean of the Sonnet agent, as a lean: (i-b), a read-time option, automatic for every result table that declares an entity id, with a required statement of the meaning, placed before the author's tier-1 steps (P1) so that the recipe's own steps say how the marked lines are processed, and reading the metadata as read from its file (α); the marker m1; with B6 the data table first, and an advice when a completed table is joined with the metadata first.
- Lean of the Opus agent, as a lean: if you choose B6, (i) a read-time option declared on the data table, automatic for every result table that declares an entity id, with its meaning required (variant i-b), done before the recipe's own tier-1 steps (P1, your words "at (first step)"), reading the metadata as read from its file (α), with the marker m1, a yes/no column beside empty cells; and the data table first. Reason: the recipe then states the completion, so the app does not modify the recipe; a removal written at the end of the result table's tier 1 runs after the completion and is complete; with the data table first the result keeps the initial population and its zeros; α keeps the result table's first place a first place (D-0553). What P1 asks of the recipe maker: a filter in that tier 1 that removes every line of an entity leaves it absent (on the demo, 6 entities of `Detailed_summary`); a rule written as a mark instead of a filter keeps it.

### The questions that remain for you, one at a time (each with what you would see on the demo)

1. **Where does the completion live?** (i) a key in the recipe on the data table, done by the app when it reads the file; (ii) a first step you write in tier 1; (iii) outside the recipe (the pipeline or a Data Import helper). On the demo with (i): the ResFinder Source view shows the file's 70 lines; T1 shows 74, 4 marked; the recipe holds one line (or none in (i-c)). Neither: say what you meant.
2. **You said the completion is automatic ("an automatic completion at (first step)"). Should the recipe still carry one line that states it and its meaning, or nothing at all, the documentation and the alerts saying it?** On the demo both give the same 4 lines on ResFinder; with one line the recipe shows them; with none only the alert and the export's report do. The APEC reference list has no entity id and is never completed. Neither: say what you meant.
3. **You said the recipe says how those lines are processed, "forcing the recipe maker to consider this case". Must the recipe state what the marked lines mean** (the check refuses the completion without it), or is the data check's note enough? On the demo: the check would ask ResFinder's meaning before the recipe opens; or the note would say "4 lines added to ResFinder; the recipe does not say what they mean". Neither: say what you meant.
4. **The marker (you asked for one "short and explicit", "a different kind of other "missing value""): a yes/no column beside empty cells, or a word in the cells, and its name.** On the demo: with the column, the plot keeps 4 samples in the bar at 0; with a word in the gene column, `QA_AMR_per_sample` counts 1 gene for each of the 4 and the bar at 0 is empty. Neither: say what you meant.
5. **When in the table? Your words: "this might be before T1 a step the app does". Before the recipe's own tier-1 steps (they see the added lines), or after them?** On the demo: ResFinder's stamp would read "Detected" on the 4 lines before; `Detailed_summary` (42 ids in the file, 36 after its filters) gets no added line before, and 6 entities with a marked line after. Neither: say what you meant.
6. **Which metadata: as read from its file, or after its tier 1?** On the demo: remove one of the 4 added entities at the metadata's place: from the file, it stays in ResFinder, marked; after tier 1, it is no longer added, but ResFinder's place lies below the metadata's (one place per path). Neither: say what you meant.
7. **The order of the join: data first only, or may the metadata-first join stay (with an advice)?** On the demo: remove one detected entity at the ResFinder table: data first, 41 samples; metadata first with the marker read, 42 rows with 1 shown as "no line"; metadata first and genes only, 42 samples with 5 in the bar at 0. Neither: say what you meant.
8. **An id in a result file and in no metadata: you prefer the metadata corrected. Should the app also offer the marker "not in metadata" (you said it "could be done"), or the note only?** The demo has none; the template `left_join_lesson` has 2. Neither: say what you meant.
9. **An id repeated in the metadata: a note?** The demo's metadata has none. Neither: say what you meant.
10. **The count per target: for each target (on the demo, each gene), how many entities do not carry it?** None of the forms above gives it: it needs one line per entity and target. On the demo you would see, for any one gene, how many of the 42 samples lack it. Neither: say what you meant.

(Not a question any more: the three id-less lines of `demo_abromics`. Your words "metadata should be clean - all with an id" and your order "remove the null and empty rows from the metadata" (D-0569); the change is shown in the dry run of the one big move, D-0525.)

### Runs after your choice (each registered before it runs; three points)
1. **The completed table through the demo's chains (the recipe side).** Requirement: a scratch ResFinder file with the 4 added lines and the marker column written by hand (the completion does not exist), the chain of `qa_amr_genes_per_sample` joined data first and metadata first. Expected: `QA_AMR_per_sample` 74 rows, 42 per entity, 4 at 0; `status` "Detected" on the 4 and `total_gene_count` 1 unless the steps are adapted; `ST22_Anchor`'s `status` "Detected" for the 4; row counts of `QA_fanout_exhibit` and `ST22_Anchor` unchanged; the heatmap's handling of an empty gene observed. Independence: a scratch recipe from the demo's schemas, every table rebuilt in its own empty folder, no lineage code.
2. **A removal on the completed table.** Requirement: a removal by key at the end of ResFinder's tier 1 in a scratch audit copy (the step written by hand). Expected: data first 41 samples, 4 at 0; metadata first with the marker read 37 / 4 / 1 "no line"; metadata first, genes only, 42 samples with 5 at 0. Independence: as 1.
3. **The marker forms.** Requirement: the same chain with a marker column and with a sentinel word. Expected: `gene.count()` 0 against 1. Independence: Polars on a scratch table, no recipe code.
4. **P1 against P2 on `Detailed_summary`.** Requirement: the completion by hand before and after its filters. Expected: no added line before; 6 marked lines after. Independence: as 1.
5. **The keys (once (i) or (ii) is built; with (iii) the key moves with the file only).** Requirement: a change in the metadata file changes the key of every completed table and the tables below (D-0560). Expected: every key differs; a stale stored table is not served. Independence: each variant in its own empty folder; the keys from the engine's own key functions on a hand-edited scratch recipe.
6. **The app's completion and the graph** (once built): the same points as 1 on the real option, and the valid sets of places with its new edge (D-0553), α and β.
7. **`not_in_metadata`** (if chosen): the lines of a scratch result file with an id in no metadata.

---

## THE CAUSE, AND WHAT WAS FOUND

### The 14 tables below the ResFinder table: not classified, by order

Not done (D-0565: "the solution first"; D-0566: no run on the cause). What exists is kept as it stands: the list of the 14 tables and which two stayed identical [ESTABLISHED: PATHS G8]. The 14 are `T2:ResFinder`, `T1` and `T2` of `ResFinder_with_metadata`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `ST22_Anchor`, and the plots `amr_heatmap`, `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `virulence_bar`, `virulence_variants`. [my own graph of the demo recipe]

### What the "23" is

[HAND COUNT, `cause/hand23.out`; the steps are those of `wrangling/VirulenceFinder_wrangling.yaml` written again by hand with polars on the raw file; compared with the stored tables of the earlier run, [STORED TABLES, Opus RR11]]
- The entity has 1 metadata row, 1 ResFinder row (gene `blaTEM-1C`) and 29 raw lines in the VirulenceFinder file. After the tier-1 steps of VirulenceFinder (one row per virulence gene, strip, unique) it has 23 rows, 23 distinct `VF_gene`, none empty.
- `QA_fanout_exhibit` tier 1: metadata (1 row) left join ResFinder (1 row) left join VirulenceFinder (23 rows) = 23 rows. After a step that removes the entity at ResFinder: metadata (1) left join ResFinder (no row, so one row with empty columns) left join VirulenceFinder (23) = 23 rows. The 23 is VirulenceFinder's gene rows, multiplied by 1 ResFinder row (before) or by one row with empty ResFinder columns (after).
- Tier 2: `rows_per_sample = pl.col('VF_gene').count()`, a count of non-empty virulence genes: 23 before and after. It is not a count of rows with empty data values. [RECIPE FILE `QA_fanout_exhibit_tier2.yaml`]
- The stored tables of the earlier run show the same rows: before, the entity has 23 rows with `VF_gene` non-empty in all 23 and `gene` = `blaTEM-1C` in all 23; after the step at `T1:ResFinder`, 23 rows, `VF_gene` non-empty in all 23, `gene` empty in all 23. [STORED TABLES, Opus RR11]
- Not established without a new run: that a rebuilt engine table today holds exactly these rows. The equality of the number and the stored tables are the evidence.
- `QA_AMR_per_sample` tier 2: `n_amr_genes = pl.col('gene').count()`, 1 before the step and 0 after; the entity's one row stays (it comes from the metadata). [HAND COUNT; RECIPE FILE]

### Is the unchanged plot wrong or right?

[RECIPE FILE: the plot's own text] The plot `qa_fanout_rows_per_sample` is titled "QA EXHIBIT: rows per sample after joining two long tables"; its description says "EXHIBIT of a known defect (issue 68) - rows are inflated on purpose ... a sample with no AMR gene hit counts as one hit, so a sample with more hits weighs more. The defect is shown on purpose." The tier-1 file says "Do not copy this pattern".
- **Right for what it counts.** It counts the non-empty virulence genes of each sample after the join. On the demo this equals the rows, because every row has a virulence gene. The entity's virulence genes did not change, so its count does not change. [HAND COUNT; STORED TABLES]
- **Possibly wrong for a user.** A user who removed the entity at ResFinder and looks at this plot sees the same bar as before, and could wrongly conclude that the removal did not work, or that the entity is still in "the ResFinder analysis". The ResFinder columns of its 23 rows are empty; the plot does not show them. [REASONED]
- The plot is a deliberate exhibit, not a result for a scientist. The same behaviour in a real recipe (a count that comes from another original than the one the user removed) would be the problem. This is for you to decide.

### The scan of the demo and the shipped recipes for the same patterns

[READ SCAN, Sonnet `cause/C6.out` and Opus RR12, two parses that agree: 14 recipes with joins, 31 joined tables; no engine.] Cause class: H1 a count of rows after a join (empty data rows counted), H2 the join direction keeps the entity (by the population), H4 rows that come by another path than the place, other. Effect on an audit: from the established runs where there is one, otherwise "reasoned".

**Joined tables that start from the metadata (first ingredient `metadata_schema`): 7** (6 in the demo recipe; 1 in `demo_abromics`).

| Recipe :: table | Ingredients (first = base) | Aggregate after the join | Cause class | What it does to an audit |
|---|---|---|---|---|
| demo :: `QA_AMR_per_sample` | metadata, ResFinder | tier 2 `gene.count()` (non-empty values) | H2 by design: the plot expects the 4 entities with 0 genes | A step at `T1:ResFinder` leaves the entity with 1 row and count 0 (a false zero); at the join place the entity is gone [ESTABLISHED: PATHS G8; RECIPES G6] |
| demo :: `QA_fanout_exhibit` | metadata, ResFinder, VirulenceFinder | tier 2 `VF_gene.count()` | H4 (rows from another original) and H2; an exhibit | A step at ResFinder: the count does not change (the 23); at VirulenceFinder the count would fall to 0 and the entity would stay by the metadata [HAND COUNT; REASONED] |
| demo :: `ST22_Anchor` | metadata, FastP, ResFinder, MLST, VirulenceFinder, APEC list (inner) | tier 2 `pl.len().over(sample_id)`, a ROW count | H1 in form (a row count where a count of values may be meant; the plot says "counting table rows ... a sample with more AMR hits weighs more") and H4; the inner join with the APEC list drops the rows with no virulence match, including the metadata-only row | A step at ResFinder: the entity's 7 rows stay with the ResFinder columns empty [ESTABLISHED: PATHS G8]. The metadata being first does NOT keep an entity with no matching virulence gene here: the inner join removes it [RECIPE FILE; REASONED] |
| demo :: `QA_population_zscore` | metadata, Quast | tier 2 z-score over all rows (`mean`, `std`) | H2: the entity stays with an empty n50; `mean` and `std` ignore empty values | A step at Quast removes the entity's n50 and changes the z-score of every other entity (the plot's purpose). The entity stays with an empty z-score [REASONED] |
| demo :: `QA_year_types`, `QA_aggregated_no_key` | metadata only (no data join) | `QA_aggregated_no_key`: count of `sample_id` per country and year | none | A step by the entity at the metadata place removes it; `QA_aggregated_no_key` tier 2 has no `sample_id`, so a removal cannot reach it [RECIPE FILE; ESTABLISHED: RECIPES G8] |
| `demo_abromics` :: `demo_join` | metadata, MLST | none | H2 | not run |

**Other aggregates after a join (the table does not start from the metadata):** `Summary_phenotype_length_fragmentation` (sum of `resistance_points` per sample and sequence type, base `Summary`, 623 rows at tier 1 for 42 entities [ESTABLISHED: RECIPES G12]); `2_test_data_ST22_dummy` :: `AMR_Profile_Joint` (a distinct count per sample, inner join with the metadata). [READ SCAN]
**Inner joins (they can remove entities without a step): 5:** the two joins with the APEC list in the demo (`ST22_Anchor`, `AR1_MLST_Serotype_Virulence`; 1114 of 1731 rows leave in `ST22_Anchor` [ESTABLISHED: RECIPES G14, Sonnet's run only]), the same join in `1_Abromics_general_pipeline`, and two joins with the metadata in `2_test_data_ST22_dummy`. [READ SCAN]
**A right side that repeats the entity id before an aggregate:** `ResFinder` and `VirulenceFinder` on the right of a metadata-first join in `QA_fanout_exhibit` and `ST22_Anchor` (rows multiply, 42 to 1731 and 617) [ESTABLISHED: RECIPES G9]; whether the right tables of the other recipes repeat the entity id is not established (it needs their data).
**Counts of the scan:** 31 joined tables; 7 start from the metadata; 5 of them have an aggregate; 7 joined tables in all have an aggregate (3 count values, 1 counts rows (`ST22_Anchor` is the only one), 1 distinct, 1 sum, 1 mean); 5 have an inner join. In the shipped recipes the pattern "metadata first, then an aggregate" is only in the demo recipe. [READ SCAN]

### What the author could write instead, and what can be checked

None of it was run (D-0566), so none is "verified on a scratch copy": the candidates are in the catalogue below.
- **The check could verify (reading the recipe only):** that the first ingredient of a join is the metadata and that a later step counts rows (`pl.len()`) or windows over the entity id: an advice "this counts rows, not values; the table starts from the metadata". [CODE READ: the check already gives advices of this kind, J12, J13, S04] It could name two data tables in one join (the multiplication) as an advice. It cannot know that a table repeats the entity id: that needs the data (the data check). [CODE READ `recipe_check.py` takes the recipe dictionary; `validate_data_analysis_recipe_data` reads the files]
- **Only the good-practice page can say:** that a result per observation is written with the data first and the metadata second, and that a result per entity with zeros keeps the metadata as the side whose rows stay, with the join place as the place of a removal. [HER WORDS D-0547, D-0549]

> **Correction of 2026-11-23:** a result per entity with zeros keeps all the entities that should appear in one table that is not the counted data table: the metadata, or a table of the analysed entities (a2).

### What she may be missing

1. **The zero and the removal are the same state.** Why: a table cannot hold "no data row" and "removed" as two different things unless a column records it, and, within her rules (a filter, a column drop or a removal by key, written after the author's steps), no step can write that mark. How you see it: the same bar of 0. Alternatives: write the step at the join place or use "Remove from all the data" (both remove the entity from the population path); let the dialog say how many paths a step covers; add a column that records "had a data row". [REASONED; D-0322, D-0541]
2. **In this data, "analysed, nothing found" is not in the file.** The ResFinder file lists only the genes found: an entity analysed with no gene and an entity not analysed are both absent. So the zeros of `qa_amr_genes_per_sample` already mean "not in the file", and the plot's subtitle says "4 with 0 genes" by hand. [RECIPE FILE; HAND COUNT: 1 row of the entity in 70 rows of ResFinder] To tell the two apart, a second table that lists the analysed entities is needed, and the recipe has to say so. [REASONED]
3. **"Metadata second" is not the point; "which side is kept" is.** A join with the data first and the metadata second but of kind `right` or `full` keeps the metadata's rows, so the entity stays by the population exactly as with the metadata first. [REASONED from the join semantics]
4. **The inner join with the APEC list loses the population too.** In `ST22_Anchor` the metadata is first, but the inner join with a reference list removes every entity with no matching virulence gene, so there the metadata-first direction gives no zeros and still leaves the entity in rows from VirulenceFinder. [RECIPE FILE; ESTABLISHED: PATHS G8]
5. **A multi-grain table.** `ST22_Anchor` joins tables that have one row per entity (FastP, MLST) with long tables (ResFinder, VirulenceFinder). Its row count weighs an entity by the product of its ResFinder rows and its VirulenceFinder rows (the plot description says so). Counting per entity first is the way to avoid it, candidate (a). [RECIPE FILE; ESTABLISHED: RECIPES G9]
6. **The retest is cheap to prepare and must follow her choice.** It is described at the end.

---

## THE CATALOGUE OF SOLUTIONS

Her rules this stays inside: every join is in tier 1 [CODE READ `recipe_check.py:715`, `action_names.py:66`]; at most one chosen place on a path [HER WORDS D-0553]; the default place is where the original and the metadata are joined [HER WORDS D-0549]; every table below a change is recalculated [HER WORDS D-0560]. The chain: `qa_amr_genes_per_sample` reads `QA_AMR_per_sample` = metadata, left join ResFinder, select; tier 2 groups by the entity and counts the genes; the plot's own text: "A sample without any AMR gene must appear at 0, not disappear. T1 is long (74 rows), T2 has one row per sample (42)" and "Expect 42 samples: 4 with 0 genes, 70 genes in total". [RECIPE FILE]

**The rule behind all candidates.** To show an entity with no data row, the table must take the entity from a table that holds all entities. That table is the retained side of a join. Written first with `left`, or second with `right` or `full`, the audit sees the same thing: a table that reads the metadata as one of its incoming paths. A removal that covers only the data original cannot remove the entity from the population path (k of n paths, k < n). [REASONED; ESTABLISHED: PATHS G8 "~ means below, not gone"]

> **Correction of 2026-11-23:** the table that keeps all the rows is the metadata, or a table of the analysed entities (a2). In (a2) the joined table still reads the metadata as one of its incoming paths, but the metadata is not the side whose rows are all kept: it is joined second with `left` and adds no entity.

For each candidate: what the author writes; what the audit would do (default place; removal at the data table's first place; removal at the join place); what it prevents and what it does not; what the user sees; whether today's check and engine accept it (code read); whether a zero "analysed, nothing found" can be told from "removed by an audit step"; whether it can be judged without a run.

### (a) Count per entity first, then join with the metadata

**Author writes** (a fragment, not run). A second table on the same file (her reimport idea, D-0556) that counts per entity, and a join with the metadata:
```yaml
data_schemas:
  ResFinder_per_entity:             # same file and input_fields as ResFinder
    tier1:
      steps:
        - action: polars_group_by
          by: [sample_id]
          maintain_order: true
          named_aggs: {n_amr_genes: "pl.col('gene').count()"}
joins:
  AMR_per_entity:
    ingredients: [{dataset_id: metadata_schema}, {dataset_id: ResFinder_per_entity}]
    tier1:
      steps:
        - action: polars_join
          right_ingredient: ResFinder_per_entity
          'on': [sample_id]
          how: left
          maintain_order: left_right
        - action: polars_fill_null
          columns: [n_amr_genes]
          value: 0
```
One row per entity on each side: no multiplication. The per-observation table stays as it is (`ResFinder_with_metadata`, data first, metadata second).
**Which side the metadata must be on:** the retained side. With `left` it is the first table; with the data first it would have to be `right` or `full` (candidate (e)). With the data first and `left`, the 4 entities with no ResFinder row are not in the table and there are no zeros. Plainly: yes, it is again "metadata first" for the audit. [ESTABLISHED: RECIPES G5, G6; REASONED]

> **Correction of 2026-11-23:** with (a2) the retained side is the table of the analysed entities, and the metadata is second with `left`: the 4 entities with no ResFinder row stay (they are in the base) and the metadata adds no entity.
**Audit.** Default place (D-0549): the join place `T1:AMR_per_entity`: the entity is gone from the table and the plot. First place of the data table, `T1:ResFinder_per_entity`: the entity has no row on the data side, the left join keeps the metadata row, the zero is filled: the entity stays with 0, a **false zero** [ESTABLISHED: Opus RR4 (2 genes to 0), Sonnet `world2.full` (3 to 0)]. A step at `T1:ResFinder` does not reach this table at all (a second table on the same file is not below the first) [ESTABLISHED: RECIPES G6]. Paths covered at the data first place: 1 of 2.
**Prevents:** row multiplication; the long table's rows no longer weigh the entity (it fixes the `ST22_Anchor` pattern when applied to its long tables). **Does not prevent:** the false zero.
**User sees:** 42 entities counted by their number of genes, 4 of them in the bar at 0; after a removal at the data table the entity is counted in the bar at 0, like the 4 entities that have no row in the file.
**Today:** accepted by the check and run by the engine (a second table on the same file and a left join with a fill). [ESTABLISHED: RECIPES G18; Opus RR4]
**Zero "nothing found" vs "removed":** not distinguishable in the table. They differ in the audit record. A column "had a data row" written before the fill would tell "no data row" from "0 found", not "removed" from "never there". [REASONED]
**Judged without a run?** Yes for the above (established runs). Run after her choice: see the retest.

### (a2) A table of the analysed entities as the FIRST table of the join, the metadata second (added 2026-11-23, after this file was signed; ledger D-0568, `OVERLAP_AND_POPULATION.md`)

**Author writes** (a fragment, not run). Candidate (a) with the table of (f2) as its base: a data table that has one row per entity the analysis ran on is the first table; the counts come next (left); the metadata is second (left):
```yaml
joins:
  AMR_per_entity:
    ingredients: [{dataset_id: FastP}, {dataset_id: ResFinder_per_entity}, {dataset_id: metadata_schema}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: ResFinder_per_entity, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_join, right_ingredient: metadata_schema, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: polars_fill_null, columns: [n_amr_genes], value: 0}
```
(`FastP` stands for the table of the analysed entities; a manifest of the analysis is the right table, see below.)
**Audit (reasoned).** Default place: the join place: the entity is gone. First place of ResFinder (or of the counts): the entity is still in the first table, so it shows 0, a false zero; 1 of 3 paths covered. First place of the base table: the entity leaves the base and everything below: gone. [REASONED; ESTABLISHED: RECIPES G6]
**Prevents:** the join starts from a data table (the order of D-0564) and the metadata's extra entities stay out (the reason of D-0549); zeros for the entities that were analysed with no hit; the entities of the metadata that were never analysed do not appear. **Does not prevent:** the false zero at the counted data table's own place; and "analysed" is relative to ONE analysis: a read-quality table lists the sequenced entities, but an AMR run can fail for one of them, and its 0 would then mean "not analysed" again. The right first table is a manifest of the analysis, or one of its own result files with one row per analysed entity.
**User sees:** on the demo the same 42 samples counted as today, because every metadata id is in `FastP`, `Quast` and `Summary` (42 of 42). The difference appears only with an entity of the metadata that was never analysed: it is absent with (a2), and shows 0 with the metadata as the base.
**Today:** its parts are accepted by the check and run by the engine (a data table first, left joins, a fill); the whole chain is not run; the `entity` block is optional and only checked (E02). [CODE READ `recipe_check.py:333-348`]
**Zero distinction:** "analysed, zero hits" against "never analysed": yes, for one analysis. Against "removed at the data table": no.
**Judged without a run?** The parts, yes (established runs); the combination, no: the retest with one never-analysed entity (see `OVERLAP_AND_POPULATION.md`).


### (B3) The result files list every analysed entity (added 2026-11-23; ledger D-0569; the review session's reading of her last sentences, NOT confirmed by her)

Her words: "So the ids that are in metadata and not in the results data might require to be added to the results files.... a point to consider. then we would keep the 0 that means eg. no resitance gene was found." [HER WORDS D-0569] Tags: [HER WORDS] / [RECIPE FILE] / [CODE READ] / [REASONED, not run]. Not yet seen by the Opus agent.

**(i) What changes in her contract.** Today: the ids of each result file are in the metadata, one direction [HER WORDS D-0568]. With B3, for the entities that were analysed, the other direction holds too: the result file and the metadata cover the same ids. It holds in full only when the metadata lists exactly the analysed entities; where the metadata holds entities never analysed, those must stay out of the file. [REASONED]
**(ii) Who writes the rows.** The pipeline that makes the file (it knows what it analysed); a helper in Data Import; or the user. **A recipe step cannot add the rows:** a schema's tier 1 runs on its own table only (`prepare_ingredient`, `orchestrator.py:269-283`), and no registered action appends rows (no concat or union: the 68 actions of `rules_agent_role_bioscientist.md` section 8). The only recipe routes are joins that keep another table's rows: the metadata's (A, or (e) with `right` or `full`), or a table of the analysed entities ((a2)). [CODE READ] The rows are then made AFTER the result file's first place, so a removal at that place would not reach them: the false zero comes back. So B3 means the rows are in the FILE. [REASONED]
**(iii) What a count then counts.** A line with an empty gene: a count of ROWS gives 1; a count of the non-empty genes gives 0. The demo: `QA_AMR_per_sample` tier 2 counts non-empty genes (`gene.count()`): 0 for the 4 entities, as the plot says ("4 with 0 genes"); its table keeps 74 rows (70 + 4) as today. [RECIPE FILE] `ResFinder` tier 2 counts ROWS (`total_gene_count = pl.len().over(sample_id)`): an empty-result line gives 1, not 0. `ResFinder` tier 1 stamps every line `status = Detected` (`pl.lit('Detected')`): an empty-result line would say "Detected". The heatmap `amr_heatmap` (x gene, y sample) would meet a line with no gene. The left joins that read ResFinder (`QA_fanout_exhibit`, `ST22_Anchor`, `ResFinder_with_metadata`) treat an empty-result line like the empty line a left join makes today (the multiplier is 1); an inner look-up join BY GENE would drop that line again (the demo has none on ResFinder; its inner joins are by virulence gene on `VirulenceFinder`). [RECIPE FILE; REASONED] An empty cell must be a truly empty cell: a cell with only spaces becomes an empty text after the strip, which `null_values: []` does not turn into missing. [DATA FILE COUNT: the plain read of my overlap count showed the empty id as missing and a whitespace one as a blank text]
**More on what a count does (added after the Opus agent's check):** a count of DISTINCT genes counts an empty value as one value (in Polars a missing value counts as a distinct value), so 1, not 0, unless the empty values are dropped first. The same holds for a cell of only spaces: the ingestion strips the text and then turns the listed null words into missing (`declared.py:115-120`), so with `null_values: []` it stays an empty text, not a missing value. [REASONED; CODE READ] An explicit column in the result file ("analysed: yes"), or a manifest of the analysis, says "analysed, nothing found" more clearly than a line with an empty gene, which every step that counts rows or stamps a value reads as a hit. [REASONED]
**(iv) The risk she must see.** The app cannot know whether an id absent from a result file means "not analysed" or "analysed, nothing found": the pipeline or the user decides. Adding ALL the metadata ids to a file would mix the two, and would turn the data check's note into a way to write false "analysed, nothing found" lines. [REASONED]
**(v) What the data check (her choice (b): only inform) says in the other direction.** "N entities of the metadata have no line in this result file: <ids up to 20>. If they were analysed and nothing was found, the file should hold a line with an empty result for each; if they were not analysed, leave them out. The app cannot tell which." On the demo: `ResFinder`, 4 of 42. [REASONED; DATA FILE COUNT]
**(vi) What the audit does under B3.** Default place: the join place: gone. A removal at the data table's own first place: the entity's lines, including the empty-result line, are removed from the table; the join is data first, metadata second, with `left`, so the metadata adds no entity: the entity is gone from the table and the plot: **no false zero**, 1 of 1 data path covered. At the join place: gone. The entity stays in the metadata and in the other tables; that is the audit's reach as for any original. [REASONED from `PATHS_AND_DERIVED_AGREED.md` G8 and RECIPES G5]
**(vii) B2 and the declared population.** B3 makes B2 unnecessary where every result file used as a base lists every analysed entity. They answer different cases: B3 when the pipeline can be changed or the file written; B2 when the files cannot be changed or no file lists the analysed entities. The declared population (c) is not needed under B3. [REASONED]
**(viii) What cannot be judged without a run** (after her choice; registered first): 1. Requirement: a scratch copy of the ResFinder file with 4 added lines with an empty gene, and the chain of `qa_amr_genes_per_sample` with the data first and the metadata second. 2. Expected: 42 samples counted, 4 in the bar at 0; a removal at `T1:ResFinder` leaves 41; the 4 lines read as missing gene (not as an empty text); `status` reads "Detected" on those lines and `total_gene_count` 1 (what the recipe's own steps do); the heatmap behaviour is unknown. 3. Independence: a scratch recipe, the file written by hand, each table rebuilt in its own empty folder, no lineage code.

### (b) Keep the metadata first, write the step at the join place, show "k of n paths covered", and put the pattern on the good-practice page

**Author writes:** today's recipe, unchanged (`QA_AMR_per_sample`). [RECIPE FILE]
**Audit.** Default place: the join place `T1:QA_AMR_per_sample` (D-0549): the entity leaves the table and the plot. First place of ResFinder: the entity stays with 0, because the metadata path is not covered: **1 of 2 incoming paths covered** [ESTABLISHED: PATHS G8: "1 row"]. The app can say this before Apply if she allows the sentence "can remain" (PATHS Q6). Join place: gone.
**Prevents:** nothing in the table. It makes the false zero visible and puts the default where it does not arise. **Does not prevent:** the false zero when the user chooses the data place.
**User sees:** in the dialog, the place with "covers 1 of 2 paths: the entity can remain in this table with empty values" and the default ticked at the join (words PROVISIONAL, hers); in the plot, a 0.
**Today:** the recipe is accepted; the sentence "can remain" is an open question (PATHS Q6), not built.
**Zero distinction:** the dialog's sentence and the audit record. The table cannot.
**Judged without a run?** Yes (established runs); nothing to change in the recipe or the engine.

### (c) A completion of the population declared in the recipe

**What it would be (does not exist today).** A way to say, in the recipe, "this result is per entity; complete it with the entities of the population, with 0 for the counts". The key `entity.population` (a table that holds the entities) exists, but it is only checked (E02): it completes nothing. [CODE READ `recipe_check.py:341-348`, `recipe_spec.yaml:30`] A possible form (invented, refused today as an unknown key, J01 or T03):
```yaml
joins:
  QA_AMR_per_sample:
    ingredients: [{dataset_id: ResFinder}]     # the data first, no metadata join
    tier1: {steps: []}
    tier2:
      steps:
        - action: polars_group_by
          by: [sample_id]
          named_aggs: {n_amr_genes: "pl.col('gene').count()"}
    complete_population: {fill: {n_amr_genes: 0}}      # NEW: uses entity.population
```
**Audit (reasoned).** The completion reads the population after the aggregation, so there is an edge from the population's tier 1 into this table's tier 2: a new kind of edge (the same question as a look-up join in tier 2, her question 27). The default place: the join place or the population's place. A removal at the first place of the data table: the entity is still in the population, so it is completed with 0: a false zero again, unless the app is made to remove the entity from the population when a removal is written for "a result per entity" (a rule that does not exist). [REASONED]
**Prevents:** the metadata as a visible first table; the author states the intent in one line. **Does not prevent:** the false zero. What it adds: the app would KNOW which rows come from the completion, so the dialog could say so and the table could carry a mark. (c) and (f3) are the candidates in which the app itself can tell a filled zero from a counted zero. [REASONED]
**Today:** not accepted (unknown key); the engine has no such step.
**Judged without a run?** No: whether a tier-2 completion can be built in the engine (tier 2 receives the table, not the population). The run after her choice: requirement, build the completion on a scratch copy and read the entity's rows after a removal at the data place; expected, false zero unless the rule above is added; independence, scratch copy, hand-written steps, engine from scratch.

### (d) A derived table that reads the data table and the metadata separately (her words D-0514 to D-0518; form 3 not confirmed, D-0496)

**Author writes** (invented; form 3 is refused today with T03 for `derived_tables` and J01 for `from:`, [ESTABLISHED: RECIPES G11, G18]):
```yaml
derived_tables:
  AMR_counts:
    from: QA_AMR_per_sample        # ONE table; D-0517 "yes we need the from:"
    tier1: {steps: [polars_group_by by [sample_id, country] ... gene.count()]}
```
**What the form can and cannot do.** A derived table reads ONE table and holds no join step: the join with the metadata is written before it, as a join of source tables. [ESTABLISHED: RECIPE_PROPOSAL_answers, answer 2; her words D-0511 "derived tables should already have the metadata joined"] A derived table moves the aggregation out of the join's tier 2; the table it reads is still the join of the metadata with the data, which must keep the metadata as the retained side to show zeros. Alone, (d) does not remove the pattern. A derived table that reads the data table and the metadata separately would be a join of two tables in a new place: that reopens "a join takes only source tables" [HER WORDS D-0344: "Yes, revisit if needed"] and the rule that every join is in tier 1.
**Audit.** One more node in the graph (the derived table, one parent). Where the metadata is first in the join it reads, the result is that of (b). [REASONED]
**Today:** not accepted. **Judged without a run?** Yes, it does not give zeros alone; it can carry (a) or (b) with a clearer hierarchy. A run after her choice would test the form itself (fact F1 of the recipes file).

### (e) A right or full join kind; an anti-join then a union

**Author writes** (a fragment, not run), the data first and the metadata second with the retained side the metadata:
```yaml
joins:
  AMR_per_entity_right:
    ingredients: [{dataset_id: ResFinder_per_entity}, {dataset_id: metadata_schema}]
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: right
          maintain_order: left_right
        - action: polars_fill_null
          columns: [n_amr_genes]
          value: 0
```
**Followed and allowed today? (code read).** The join action passes `how` to Polars: the form of the action lists all seven kinds: `inner`, `left`, `right`, `full`, `semi`, `anti` and `cross` [CODE READ `polars_calls.py:85`]; the old reading code names `anti`, `right`, `full` and `cross` as not YET followed [CODE READ `libs/utils/src/utils/step_effects.py:73`]. The old reading code (D-0452; `step_effects.py:68`) follows only `left`, `inner` and `semi`: a description of old code only. Whether the check accepts `how: right` without a message, and whether the engine builds it with `maintain_order: left_right` and which key column it keeps, cannot be judged without a run.

> **Correction of 2026-11-23 (ledger D-0570):** the form of the join step lists all seven kinds (`polars_calls.py:85`); the sentence above said it lists `right` and `full` and that the engine accepts the others.
**An anti-join then a union:** an anti join of the metadata against the data gives the entities with no data row (`how: anti`). A union (appending rows) has no registered action: the 68 registered actions have no concat or union. [CODE READ `rules_agent_role_bioscientist.md` section 8; `libs/transformer/src/transformer/actions/`] So the union cannot be written today.
**Audit.** Her graph model (D-0553) follows a right or full join like any join: its parents are its ingredients, whatever `how` says, so the places, "below" and the rule of one place on a path are unchanged. What `how` changes is the kept side, which the display must name from `how` (right: the second table; full: both), not from the first ingredient. A removal at the first place of the data table: the right join keeps the metadata row, the entity stays with an empty value, filled 0: the same false zero as (a). [REASONED from the model; checked by Opus]
**Prevents:** it writes "the metadata second" literally (D-0549, "the metadata should be the right table"). **Does not prevent:** the false zero; and the retained side is still the metadata, so the population effect is the same as metadata first. [REASONED]
**Judged without a run?** No: the engine's build of `how: right` and `how: full`. Run after her choice: requirement, D-0564 with option E; expected, 42 rows, 4 at 0 after the fill, the key column present once, the order kept with `maintain_order: left_right`; independence, a scratch recipe, hand-written steps, the engine in empty folders.

### (f) Others

**(f1) No zeros: say the population in words.** The plot counts only the entities that have a data row and the recipe states the population ("Expect 42 samples: 4 with 0 genes" is already written by hand in the plot's subtitle). [RECIPE FILE] Audit: the data first, the metadata second (left): a removal at the data table or at the join removes the entity completely; no false zero. User sees: 38 samples counted, no bar at 0, a caption "4 of 42 entities have no ResFinder row" written by the author. Prevents the false zero. Does not give the zeros of `qa_amr_genes_per_sample`, which the plot is built to show. Today: accepted. Zero distinction: there is no zero.
**(f2) A table of the analysed entities.** A table (for example one row per analysed entity in a quality table) joined with the metadata gives a column "analysed" next to the count. The zero then reads "analysed, 0 genes" or "not analysed". A removal at the data table leaves "analysed, 0 genes": it still looks like "nothing found". [REASONED] Today: accepted (a join of source tables). It tells "nothing found" from "not analysed"; it does not tell "removed". It needs a table of the analysed entities in the recipe (the demo has tables with one row per entity, [ESTABLISHED: RECIPES G12]).
**(f3) The app completes at the plot, not the recipe.** HOME shows the entities of `entity.population` that have no row of a per-entity result as 0, with a mark. Audit: a removal at the data place leaves the entity in the population: false zero, but the app KNOWS the zero is filled and can mark it. Today: not built; it is an app behaviour, not a recipe form. [REASONED]
**(f4) "Remove from all the data" as the default for a result per entity.** The audit writes the removal at every place that carries the entity when the user removes an entity for a result per entity. The entity is gone from the population path as well; no false zero. [HER WORDS D-0416] This is what the dialog offers, not a recipe form. Today: decided as an option (D-0416). As one step, its 27 places are not valid under D-0553 (35 pairs). Writing them in two steps is option (a) of PATHS Q5, hers to choose. [ESTABLISHED: PATHS G9]
**(f5) The recipe says that a result is per entity** (a new key; today refused as unknown, J01 or S01). The app then knows that a removal for this result must cover the population path: it offers the join place and warns at the data place. It does not prevent the false zero; it lets the app say it. Today: not accepted. [REASONED]

---

## THE DEMO'S TABLES THAT START FROM THE METADATA: the candidate that would apply (for the one big move only; D-0525; no edit)

| Table | Cause class | Candidate that would apply | Why |
|---|---|---|---|
| `QA_AMR_per_sample` | H2, by design (the plot expects 0) | (b), or (a) if the author wants the multiplication gone and the data table's own place separate | The plot needs zeros: the metadata must be the retained side. |
| `QA_fanout_exhibit` | H4 and H2, an exhibit of a known defect | (a) applied to each long table (aggregate each before the join), or leave it as an exhibit with a caption | It is written to show the multiplication. If it stays, nothing changes. |
| `ST22_Anchor` | H1 (row count), H4, inner join with the APEC list | (a) for ResFinder and VirulenceFinder (aggregate before), and a decision on the inner join (see RECIPES (vii)) | A multi-grain table: counting rows weighs an entity by the product of two long tables. |
| `QA_population_zscore` | H2, only an empty value for the entity with no Quast row | data first and the metadata second, `left`, or (b) | No zeros are expected; the z-score of an entity with no n50 is empty. |
| `QA_year_types`, `QA_aggregated_no_key` | none (no data table) | none | They are made from the metadata alone. |

The four tables with a data join that start from the metadata are exactly `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; two more demo tables start from the metadata alone. [READ SCAN, both agents]

---

## THE RETEST AFTER HER CHOICE (described, NOT run)

One entry per candidate: the same step on the adapted chain, in a scratch copy (the demo changes only in the one big move, D-0525). Each run is registered before it runs (D-0561); the three points are written now:

| Candidate | 1. Requirement | 2. Result expected if the candidate works as described | 3. Independence |
|---|---|---|---|
| (a) | A removal at each place of the adapted chain (first place of the data table, join place, metadata, `T1:ResFinder`) | first place of the data table: false zero; join place: gone; metadata: gone; `T1:ResFinder`: no change in the per-entity table | scratch recipe from the demo's ResFinder and metadata schemas, hand-written steps, every table rebuilt in its own empty folder, no lineage code |
| (b) | The same removals on the unchanged chain, and the "k of n" read from my own graph | first place of ResFinder: false zero, 1 of 2; join place: gone, 2 of 2; the 4 entities with no row keep 0 | as (a) |
| (c) | Build the completion on a scratch copy and remove at the data place | false zero, unless the rule that removes from the population is added; whether tier 2 can read the population is the thing asked | as (a); the completion written by hand as a join in tier 1 first, then as the new step |
| (d) | Build a derived table from the join that holds the metadata | as (b) for the same removals; the check refuses the form (T03/J01) | as (a); the engine's reading of the `from:` key is unknown (fact F1 of the recipes file) |
| (e) | Build the chain with `how: right` and with `how: full` and remove at each place | 42 rows with 4 at 0; false zero at the data place; the key column present once | as (a) |
| (f1) | Data first, metadata second, `left`; remove at each place | 38 entities, entity gone at every place, no zeros | as (a) |
| (f2) | A join with a table of analysed entities, plus a column "analysed" | zero with "analysed" after a removal at the data place (still looks like nothing found) | as (a) |
| (f5) | The recipe key that says the result is per entity, on a scratch copy | the app side cannot be run before it exists; the recipe side: accepted or refused by the check | as (a) |

---

## Open between the two agents

None.

**Signed by both agents: Sonnet (this file) and Opus (OPUS_checks_cause_v1.md and OPUS_signs_cause_v2.md; all replacements applied)**; updated 2026-11-23 with candidate (a2), both agents (OPUS_checks_overlap_v1.md and OPUS_signs_overlap_v2.md); D-0569 additions signed by both agents (OPUS_checks_b3_v1.md and OPUS_signs_b3_v2.md; replacements Q1 to Q6 applied, the example of Q2 dropped); D-0570 additions: Sonnet (this file) and Opus (OPUS_checks_notdetected_v1.md, replacements R1 to R32 applied; the naming C, F and G as the Sonnet agent proposed and the Opus agent accepted); D-0572 additions: Sonnet (this file) and Opus (OPUS_checks_b6_v1.md, R1 to R26 applied)
