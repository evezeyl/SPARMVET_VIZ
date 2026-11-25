# Why two tables stayed identical, and solutions for entities that must appear with zero hits (2026-11-23)

Note 2026-11-24: this file still holds quotations of the owner's words from the study rounds. The decisions are written once, in plain words, in the decision ledger; read `WHOLE_PICTURE.md` first.

**What this is.** The cause of the two tables that stayed identical below a step at the ResFinder table (ordered by her, ledger D-0563), and a catalogue of solutions for entities that must still appear with a count of zero without the metadata as the first table of the data join (her direction D-0564). Written by an Opus and a Sonnet design agent who compared their readings and agreed before this text was written (D-0552). It is written by reading and reasoning only. **No run was made for this file**, by her orders: "H1, H2 appear to be a consequence of that - so I think we need to find solution for that and then retest." (D-0565) and "no need to test that now then" (D-0566). The runs it cites were made earlier, under the evidence rules D-0558 to D-0561, and are named where they are used. NOT confirmed by her. Nothing is built; no recipe is edited.

**Where the evidence lives.** The registers `.claude/design/studies/whole_picture_2026-11/sources/design_dialogue/RUN_REGISTER_sonnet_cause.md` (every run of this investigation cancelled before it started), `RUN_REGISTER_sonnet_recipes.md`, `RUN_REGISTER_opus_recipes.md`, `RUN_REGISTER_opus.md`; the earlier runs it cites are in `PATHS_AND_DERIVED_AGREED.md` (G8) and `RECIPES_FROM_THE_MODEL_AGREED.md`. The reads made for this file are in the same scratch folder (not in git): the hand count `cause/hand23.out` (Sonnet), the scan `cause/C6.out` (Sonnet) and the readings RR11 and RR12 of Opus (`RUN_REGISTER_opus_recipes.md`; its stored tables from the earlier run read now, and a scan of the recipes with its own parse).

**The limits.** The demo recipe and, for the numbers, one entity (`10668076`). A hand count from the source files, not an engine run. The feasibility of the solutions is NOT run: it comes after her choice, in the retest described at the end.

Tags: [HER WORDS D-n] / [RECIPE FILE] / [CODE READ file:line] / [HAND COUNT] / [READ SCAN] / [ESTABLISHED: file, point] (a result of earlier runs, rebuilt from scratch, committed) / [STORED TABLES, Opus RR11] (the engine's tables of an earlier run, read now) / [REASONED, not run].

> **Update of 2026-11-23 (ledger D-0568; see `OVERLAP_AND_POPULATION.md`):** a further candidate, (a2), was found after this file was signed: a table of the analysed entities as the first table of the join, the metadata second. It keeps zeros for the analysed entities and follows your direction. The sentences below that say that every form with zeros keeps the metadata as the side whose rows stay, and that only option D follows your direction fully, are corrected where they stand.

> **Update of 2026-11-23 (ledger D-0569):** her answers on the overlap file. She accepts the false zero at the data table's own place: "here 0 means not found in the id ... that is actually maybe why we decided to join with metadata first ... So I think the match between ids in the tables is even more important." And she puts a point to consider: "the ids that are in metadata and not in the results data might require to be added to the results files.... a point to consider. then we would keep the 0 that means eg. no resitance gene was found." A new candidate, **B3**, follows from it (the result files list every analysed entity; the review session's reading of her sentence, NOT confirmed by her). It is added to the question and to the catalogue below. Checked by the Opus agent afterwards (OPUS_checks_b3_v1.md and OPUS_signs_b3_v2.md).

> **Update of 2026-11-23 (ledger D-0570):** her case "a true not-detected is a true result" is studied in the new section "Added 2026-11-23 (ledger D-0570)" below, which holds the ONE two-part list of options (A to E, B2, B3 extended; new B4, B5, E2; information F and G). Three signed sentences were wrong and are corrected where they stand, each with a note: option B3 ("the metadata second keeps the zeros"), the "42 bars" of ten sentences (the plot counts samples by their number of genes), and catalogue (e) (the form lists all seven join kinds).

> **Update of 2026-11-23 (ledger D-0572):** her solution B6 (fill the data tables with the ids of the metadata, with a marker) and her answers on the control of the ids are in the new section "Added 2026-11-23 (ledger D-0572): her solution B6 and the control of the ids". B6 is HER PROPOSAL, not chosen; it is a line of Part 1 of the one list (a pointer is in the list). Nothing of the signed text is changed.

> **Update of 2026-11-23 (ledger D-0573 to D-0582):** her later answers changed the ids section. The metadata is no longer refused and no check blocks: only warnings (red where there is a panel), an automatic completion and an automatic log; with a panel an "I have read this" button that does not block. See the sections "Added 2026-11-23 (ledger D-0573 to D-0579)" and "Added 2026-11-23 (ledger D-0581, D-0582)"; the earlier lines are kept and marked where they stand.

---

## HALF PAGE FOR HER

**What happened.** You remove an entity at the ResFinder table. Two tables below it stay exactly as they were: the table `QA_fanout_exhibit` (its second tier) and its plot `qa_fanout_rows_per_sample`. The number for the entity stays 23.

**What the 23 is.** The entity has 23 virulence genes. They come from the VirulenceFinder table, not from ResFinder, so a step at ResFinder does not touch them. The table counts the genes that are present; it does not count an empty row. Before and after the step the entity has 23 rows in the table, with the virulence gene filled in all 23, and the ResFinder gene is there before and empty after. [HAND COUNT: 1 metadata row, 1 ResFinder row, 23 VirulenceFinder gene rows; 1 x 1 x 23 = 23 before and after] [STORED TABLES, Opus RR11] [RECIPE FILE: `QA_fanout_exhibit` tier 2 counts `VF_gene`]
(An earlier sentence in the review said "a count of rows per entity stays 23". That wording was wrong; the committed paths file now carries a correction at each place.)

**The cause, in plain sentences.**
- The place chosen: the entity's rows in this table come by three paths (the metadata, ResFinder, VirulenceFinder). The first place of ResFinder covers one of them.
- The join direction: the metadata is the first table of the join, so the entity stays in the table with empty ResFinder values. This is the same direction that gives the zeros in the plot `qa_amr_genes_per_sample`, which is built to show every entity, some with 0 genes.
- The recipe: not a mistake of the author. The table is written on purpose as a known defect (its own text says "EXHIBIT of a known defect").
- The app: not at fault in the evidence. The stored tables of the earlier run, read now, hold exactly the rows this reading predicts [applied late 2026-11-23, older R2 of OPUS_checks_cause_v1.md]: the ResFinder column emptied, the 23 virulence genes intact. Twelve of the 14 tables below changed in that run. [STORED TABLES, Opus RR11; ESTABLISHED: PATHS G8]

**Is the unchanged plot right?** It is right for what it counts: the non-empty virulence genes of each entity after the join. On the demo this equals the rows, because every row has a virulence gene. A user who removed the entity at ResFinder and looks at this plot sees the same bar, and could wrongly conclude that the removal did nothing, or that the entity is still in the ResFinder analysis. After a removal at the VirulenceFinder table the entity would keep 1 row (from the metadata) and show 0. [RECIPE FILE; HAND COUNT; REASONED for the last sentence]

**The core fact.** A zero is an entity that has no data row. An entity removed at the data table also has no data row. The two are the same state of the table. So, within your rules (an audit step is a filter, a column drop or a removal by key, written after your steps), no solution can give "entities with no data row appear with 0" and, at the same time, "a removal at the data table takes the entity out completely". Only the path that carries the population, the metadata, tells them apart. [REASONED; her rules D-0322, D-0541]

> **Correction of 2026-11-23:** Only the path that carries the population tells them apart: the metadata, or a table of the analysed entities (a2). (The sentence above says "the metadata"; the Opus agent's replacement of the neighbouring sentences is below.)

> **Answered by her, 2026-11-23 (D-0569):** the false zero at the data table's own place is accepted: "yes because here 0 means not found in the id ... that is actually maybe why we decided to join with metadata first ... So I think the match between ids in the tables is even more important."

**Your direction, and the fact that meets it.** You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564] The fact: to show an entity that has no data row, the table must keep the metadata's rows. In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros. The question is at the end of this half page and in the next section.

> **Corrected 2026-11-23 (the first correction left the wrong sentence in place):** the sentence above is replaced by the agreed one (`OPUS_checks_overlap_v1.md`, O7). The earlier wording, kept as history, read: "So in every form with zeros the metadata is the side whose rows stay. Only the form without zeros follows your direction fully."

---

## THE QUESTION FOR HER, as it would be put

> **Update of 2026-11-23 (ledger D-0570):** the list of options below (A to E, B2, B3) is extended in two parts in the next section "Added 2026-11-23 (ledger D-0570): a true not-detected is a true result"; that section holds the ONE list (new: B4, B5, E2 and the information options F and G). Read it with this question.

**Plainly.** You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564]. Here is what is true. For a result that shows one entry per observation (for example every gene found), the data first and the metadata second works today: a step at the data table or at the join place removes the entity completely; a step at the metadata place only empties its metadata columns. [ESTABLISHED: RECIPES G5] For a result that must show every entity with a zero, there is no way to write it in which the data table's own place also takes the entity out. The zero and the removal are the same state of the table. So the question is about the zero.
Your direction and the zeros cannot both hold. To show an entity that has no data row, the table must keep the metadata's rows. In every form with zeros, a table other than the counted data table must keep all the entities that should appear: the metadata (A, B, C, E), or a table of the analysed entities (a2). Only (a2) and D follow both the order and the reason of your direction (the data first; the metadata's extra entities stay out, D-0549). D has no zeros; (a2) keeps zeros for the analysed entities. The false zero at the counted data table's own place stays in every form with zeros. Why: a row for an entity with no data can only come from the metadata. How you would see it: in A, B, C and E the plot keeps counting 42 samples, an entity removed at the data table in the bar at 0; in D it counts 38 samples and has no bar at 0. (E follows the order in your words, the metadata second, but not the reason you gave in D-0549, that the metadata's extra entities stay out of the table.) [REASONED]

> **Corrected 2026-11-23 (the first correction left the wrong sentence in place):** the sentence above is replaced by the agreed one (`OPUS_checks_overlap_v1.md`, O7). The earlier wording, kept as history, read: "So in every form with zeros (A, B, C, E) the metadata is the kept side: first with a left join, or second with a right or full join. Only D follows your direction fully, and D has no zeros."

**On the demo you would SEE** (the plot `qa_amr_genes_per_sample`: 42 entities in the metadata, 38 with a ResFinder row, so 4 with 0 genes). You remove one entity at the ResFinder table. Today (and with (a), (c), (e)) [today: run; with (a), (c), (e): reasoned] [applied late 2026-11-23, older R14 of OPUS_checks_cause_v1.md] the entity stays in the plot with 0 genes, like the 4 others. With (b) it is the same; if you allow the sentence of PATHS Q6, the dialog says before you apply that the step covers 1 of 2 paths and the entity can remain. With the step written at the join place, or with "Remove from all the data", the entity is gone and the plot shows 41 entities. With (f1) (option D) the plot shows 38 entities and no zeros, and a caption says 4 entities have no ResFinder row. [numbers: raw files and the earlier runs; ESTABLISHED: PATHS G8, RECIPES G6]

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

> **Update of 2026-11-23 (ledger D-0573 to D-0579):** her next answers changed this section. B6 is no longer only her proposal: since D-0574 the completion lives in the recipe and is required on every result table (form open). The marker is called "not in original data" (not "no result in file") and is not a zero. The metadata is refused when its ids are wrong. A confirmation once per data batch is noted in a separate log, also in the export. The ten questions at the end of this section are replaced by the list in the section "Added 2026-11-23 (ledger D-0573 to D-0579)" below; each of the ten has its fate there. The lines below are kept as history, each marked where it is stale. **Applied 2026-11-23, late: the signing line of this file said "R1 to R26 applied" but R2, R4, R5, R6, R7, R8, R9, R10, R11, R13 and R14 of `OPUS_checks_b6_v1.md` were not in the text; they are applied now (a records error of the Sonnet agent: the editing script lost them; found by the Opus review, flag 5).**

**Her words, exact** (channel block M627; ledger D-0572). Her answers to the facts, then her proposal: [applied late 2026-11-23, R2] "2. Yes true but if the sample is bad then no detection can exist because sample is bad in this case it is still good to remove from the analysis and have it rerun in another batch to be analyzed later. So audit can cover this case and justification holds. 3. yes but not so usefull for our case .. because we do not have ids with no values ... 4. this is true that is why the ids of both metadata and data sets should overlapp (or at least all in metadata and included for data sets) 5. true that is why metadata should be clean - all with an id ... 6. I think the solution would be to fill the data tables with the id contained in the metadata and have a "data file has no result" NA ? that can be then processed as a normal recipe - saying how those need to be processed in the recipe. Its a bit weird solution but it would work in all cases forcing the recipe maker to consider this case. and then missing data in the original files need to be processed correctly according to the correct meaning - which only a recipe maker (in collaboration with a real user) can decide. That would remove need for 6 anti join. and make decisions on how to procede with those clearn in the recipe so 7. All is clear and decided." Her answers to the needs: "1. yes we need a control of ids - as we started to implement - warnings in case something was wrong in the metadata so the user can recheck (as was planned recently) - if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done, if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) that would - that would be clear and mentionned both in literature and allerts. for the missing ids - but this might be before T1 a step the app does ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe) 2. we could need good marker convention - short and explicit - and I think it should be a different kind of other "missing value" because then the recipe maker has to consider those cases specifically and the 3. it knows the risk it accepts". [HER WORDS D-0572]

**What is settled, and what is her PROPOSAL.** Settled by her words: a removal because a sample is bad is right, the audit covers it and its justification holds; the ids of the metadata and of the data sets should overlap, or at least all be in the metadata and included in the data sets; the metadata should be clean (an id on every line); the meaning of a missing value is for the recipe maker with a real user; "it knows the risk it accepts" (our reading: "it" is the recipe maker, who "has to consider those cases specifically"; the risk is that the app cannot tell "not analysed" from "analysed, nothing found"). **B6 is HER PROPOSAL, not chosen**: fill the data tables with the ids of the metadata, with a marker "data file has no result".

> **Update of 2026-11-23 (ledger D-0574):** the completion in the recipe, required on every result table, is decided in substance (her words: "I think we need to force"; "the recipe required on every result table"). What is not decided: whether it is a block that the app reads (option i) or a first step the author writes (option ii), the key names, and which tables ("every result table", or those that declare an entity id).

### B6 as a line of Part 1 of the one list

**B6 (new, her proposal). Each result table that has an entity id gets one added line for every id of the metadata that its file does not hold, at the first step (your words: "an automatic completion at (first step)"; question 5 asks whether before or after the recipe's own tier-1 steps) [applied late 2026-11-23, R4]; the added line is marked; the recipe says how marked lines are processed.**
- **What the author writes.** [applied late 2026-11-23, R5] It depends on where the completion lives (question 1). With (i): a key on the data table, for example `complete_from_population` with a marker name and, if the check requires it, a `meaning` (invented; refused today as an unknown key, S01 [CODE READ `recipe_check.py:390`]; the names are provisional). The recipe's own steps then process the marked lines.
- **What you see on `qa_amr_genes_per_sample`** (42 entities; ResFinder 70 lines for 38 entities; 4 without). ResFinder grows from 70 to 74 lines, 4 marked. After a removal by key of one detected entity, written at the end of tier 1 of the ResFinder table:

| | Data first, the metadata second (left) | Metadata first, the marker published and read by the recipe | Metadata first, the recipe counts genes only (today's) |
|---|---|---|---|
| Before any step | 42 samples, 4 in the bar at 0 | 42 samples: 38 detected, 4 "no result in file" | 42 samples, 4 in the bar at 0 |
| Removal at the ResFinder table | 41 samples, 4 in the bar at 0: no false result | 37 detected, 4 "no result in file", 1 "no line": no false result | 42 samples, 5 in the bar at 0: **false** |
| Removal at the join place | 41 samples, 4 in the bar at 0 | 41 samples: 37 / 4 | 41 samples, 4 in the bar at 0 |
| Removal of one of the 4 added entities at the ResFinder table | 41 samples, 3 in the bar at 0 | 38 / 3 / 1 "no line" | 42 samples, 4 in the bar at 0 |

  [REASONED from the engine order (`data_wrangler.py:92`, `orchestrator.py:282-295`) and the join semantics; NEEDS A RUN after your choice]
  Why the middle column has three states: after a left join from the metadata, an entity that has no line in the result table gets one row whose result columns are all empty, the marker included; an added line has the marker set; a file line has it unset. [POLARS SEMANTICS; REASONED] [applied late 2026-11-23, R6]

> **Update of 2026-11-23 (ledger D-0573):** the first column "4 in the bar at 0" holds only if the recipe says that a marked line counts as 0. Her rule: "The marker of "not in original data" is not a zero." The demo's count `pl.col('gene').count()` gives 0 for an added line by itself and `pl.len()` gives 1; both would make a zero or a one without a message. What the plot shows for the 4 is her question (new list, question 5).
- **What stays false.** With the metadata first and a recipe that counts genes only, a removal at the result table still counts as "not detected" (the entity stays by the metadata). B6 removes the false result with the data table first, or with the metadata first if the recipe reads the marker.
- **What it asks.** Nothing of the pipeline. A statement in the recipe of what the marked lines mean. The recipe's steps that stamp a value or count rows must be adapted (flags 1 and 2 below).
- **How it differs from the others.** From B3: B3's lines come from the pipeline, which knows what it analysed, so they mean "analysed, nothing found"; B6's lines come from the metadata, so they mean only "the data file has no result for this id". From B5: B6 works with today's files and gives its column for free. From E: E completes at each join, after the result table's own place; a removal at the result table leaves the metadata's row; B6 completes in the table itself. From E2: no anti-join; the list of the not-detected is the marked lines. From C: C completes late and needs the audit record to name a removal; B6 needs no audit record. From the withdrawn T0 ("no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" [HER WORDS D-0509]): T0 filtered the original data; B6 ADDS marked lines and removes nothing.
- **NEEDS A RUN** (section "Runs after your choice").

### The flags (what would change a result without saying so)

1. **The added lines are stamped "Detected".** ResFinder's tier 1 stamps every line `status: pl.lit('Detected')`; `ST22_Anchor` keeps `status`; the plot `integration_plot` fills its tiles by `status` [RECIPE FILE `ResFinder_wrangling_tier1.yaml`; `ST22_Anchor_wrangling_tier1.yaml:47`; `plots/integration_plot.yaml:9`]. With B6 the 4 entities would show "Detected" with no error.
2. **Tier 2 counts rows.** `total_gene_count: pl.len().over(['sample_id'])` gives 1, not 0, for an added line [RECIPE FILE `ResFinder_wrangling_tier2.yaml`].
3. **A filter in tier 1 and a completion before tier 1 disagree.** `Detailed_summary` has three threshold filters in tier 1 (`Detailed_summary_wrangling.yaml:20, 25, 30`), and no other step of that tier removes rows [RECIPE FILE `Detailed_summary_wrangling.yaml:3-36`]; its file holds 42 ids and its table 36 after tier 1 [ESTABLISHED: RECIPES G12, engine run Opus RR2]. A completion before tier 1 adds nothing there, and the filters then remove all the lines of 6 entities: with the data table first they are absent; [applied late 2026-11-23, R7] a completion after the recipe's tier-1 steps would give those 6 entities a marked line.
4. **If the completion reads the metadata after its tier 1,** ResFinder's first place lies below the metadata's place, and choosing both is refused by "the user chooses at most one place" [HER WORDS D-0553].
5. **B6 alone does not force the recipe maker to consider the case.** A step that stamps or counts rows reads an added line as a line, with no error. The force must come from a required statement of the meaning (a required field, as the project already requires a parameter whose absence would hide a choice that changes the result [CODE READ `polars_calls.py:54-60`]), or from a check.

### Where the completion can live (her open question)

> **Update of 2026-11-23 (ledger D-0574):** (i-a) (a key on each table) and (i-c) (automatic, no key) are void: the block is required, with its meaning required. (iii) outside the recipe and (iv) the audit copy stay as history. What remains open is (i-b) against (ii) (new list, question 6).

The engine order, read: a data table is read by `_read_source` (the declared types, `strip` and `null_values`), then `ingredient_parts` picks the steps of its tier 1 [CODE READ `app/modules/orchestrator.py:264-267, 282-295`]; in an audit copy the steps of a tier are the author's steps, then the audit's [CODE READ `libs/transformer/src/transformer/data_wrangler.py:92`: `return steps + audit_list`]. The Source view reads the same `_read_source` and the plan of every place reads the same lists [CODE READ `orchestrator.py:287-300`]. A completion put in `ingredient_parts`, after `_read_source`, leaves the Source view true to the file and runs BEFORE any audit step. The added lines come in a fixed order (for example the order of the metadata), so that the same data give the same rows in the same order [RULE FILE `rules_data_engine.md` section 2, Determinism, ADR-090]. [applied late 2026-11-23, R8]

| | (i) A read-time option declared in the recipe on the data table | (ii) A new tier-1 action written by the author | (iii) Preparation outside the recipe (pipeline, Data Import helper) | (iv) The app writes a first step into the audit copy only |
|---|---|---|---|---|
| What the author writes | a key on the table (variants: (i-a) on each table; (i-b) every table that declares an entity id is completed and the key states the meaning; (i-c) automatic, no key) | a first step in tier 1 naming the metadata (a new action: none appends rows today; a schema's tier 1 has no ingredient) | nothing; the recipe declares the marker column among the fields | nothing |
| What you see | Source view: the file (70 lines); T1: 74 lines, 4 marked; the alert; the export's T1 file holds the 74 lines and says how they were made | Source: the file; T1: 74; the step is visible | the file already has the lines; the alert | the audit panel shows an extra step |
| "The app never modifies the recipe" | holds in (i-a), (i-b): the recipe states it; in (i-c) the recipe says nothing, so the export must record the app's rule and version | holds | holds for the recipe; the data is changed outside it (the overwrite of a data file with no copy is not decided: DATA-IMPORT-OVERWRITE) | does not fit |
| A step at the end of tier 1 | runs after the completion: no re-adding | runs after if the completion is the first step | runs after | cannot be first: audit steps run after the author's steps (D-0541), and an audit step is a filter, a column drop or a removal by key (D-0322); the result without an audit would differ |
| Keys and graph | the table's key must include the metadata's file and the option (`cache_keys.py:14-20`: `rC` the definition, `dC` the files the table reads): a change of the metadata changes the key of the table and of everything below (D-0560); a new edge into the table | the same, from the step | the file's hash changes; no new edge | not applicable |
| NEEDS A RUN | yes | yes (and an engine change) | yes: run 1 below (the added lines written by hand are the same test) [applied late 2026-11-23, R9] | no |

**Which metadata the completion reads.** (α) as read from its file (its declared `strip` and `null_values`, before its tier 1): the edge comes from the metadata's file; the places stay as they are; a removal at the metadata's place does not remove an added line. (β) after its tier 1, with its audit steps: a removal at the metadata's place removes the added line, but ResFinder's first place lies below the metadata's: two places on one path (flag 4). A third source exists if the recipe declares `entity.population`: with a manifest of the analysis as the population, the marker would mean "analysed, nothing found" (the key exists and is checked, E02 [CODE READ `recipe_check.py:332-348`]; nothing else reads it today [ESTABLISHED: OVERLAP section 3]). [applied late 2026-11-23, R10]
**Position inside the table.** P1, before the author's tier-1 steps: the marker means "the data file has no line for this id" (your words); the author's steps see the added lines (flags 1, 2). P2, after the author's tier-1 steps and before the audit steps: the marker means "no line left after the recipe's rules"; the author's tier-1 steps do not see the added lines, so no tier-1 step can say how to process them. After the audit steps is never right: the completion would add back an entity the user removed.
**Does the completion re-add an entity removed at the result table?** No, in P1 and P2. **Does a removal at the metadata remove it from the completion?** Only in β.

### The marker (short and explicit; a different kind of missing value)

> **Update of 2026-11-23 (ledger D-0573):** the working name `no_result_in_file` and the words "no result in file" are replaced by her name: "not in original data". Everywhere in this section where `no_result_in_file`, "no result in file" or "data file has no result" stands, read "not in original data".

Polars has one missing value (null), and NaN for floats; there is no second kind of null [POLARS SEMANTICS]. A second kind must be carried by something other than the empty cell.
- **m1. A yes/no column** (for example `no_result_in_file`: true on added lines, false on file lines), every result cell of an added line empty. Counts of values stay right (`gene.count()` 0); a step can test the column. After a left join from the metadata an entity with no line has the column empty: a third state, "no line".
- **m2. A sentinel text** in each text column: it counts as a value (`gene.count()` would give 1 for each of the 4); a number column cannot hold it.
- **m3. A marker per column type** (a word, NaN for floats): NaN is a float value, not a missing one; counts and means change in different ways.
- **m4. Empty cells only:** not a different kind of missing.
A cell of only spaces is not the marker: the ingestion strips the text and turns only the listed null words into missing, so with `null_values: []` it stays an empty text [CODE READ `libs/ingestion/src/ingestion/declared.py:115-120`].
What the checks can verify with m1: the recipe check, that the table declares an entity id, that the population exists (E02), and as information whether a step below names the marker (a match on the text of formulas, `polars_calls.py:82`); the data check, how many lines were added and for which ids.

### The control of the ids (hers)

> **Update of 2026-11-23 (ledger D-0573, D-0574; her D-0579):** (a) an id of a result file with no metadata is "check X": inform and list; the user adds the ids to the metadata by hand and uploads it again; an unknown or false id may be added with a dummy fill and a note to remove it; there is no marker "not in metadata". (b) an id of the metadata with no line in a result file is "check Y": warn; the data is completed with the marker "not in original data" after the user's confirmation, once per data batch, noted in a separate log, also in the export. (c) the metadata with no id is refused, not only informed. (d) a repeated id may be an error at the id level (new list, question 2). The correction text of the committed paragraphs is in the new section.

(a) An id in a result file and in no metadata: the data check informs and tells the user to fix it; she prefers the metadata corrected; a marker "not in metadata" is the alternative (a second yes/no column on the lines whose id is in no metadata; no line is added or removed). (b) An id in the metadata and in no line of a result file: the automatic completion at the first step, said in the documentation and in the alerts (what the alert says, words PROVISIONAL [applied late 2026-11-23, R11]: the file, how many lines were added, which ids, the marker, and "the app cannot tell whether they were analysed with nothing found or not analysed; the recipe says how they are counted"). (c) Metadata lines with no id: the metadata should be clean; the completion adds only ids that exist; the third note of the data check stays. (d) An id repeated in the metadata (not raised by you): the completion adds one line per distinct id; a join with the metadata second multiplies the rows of a repeated id; a note covers it. The demo's metadata has 42 rows and 42 distinct ids.

### The risk (your words)

"it knows the risk it accepts" [HER WORDS D-0572] (our reading: "it" is the recipe maker): the app cannot tell "not analysed" from "analysed, nothing found". The recipe maker, with a real user, decides; the alert and the documentation say so. On the demo nothing shows the risk: every metadata id is in every result table except ResFinder, and in `FastP` (42 of 42). A metadata that lists entities never sequenced would add a marked line for each to every result table. A table where absence means something else (an entity with no virulence gene) gets the same marker; the recipe maker reads the pipeline's documentation.

### Her eight questions: settled or not

> **Update of 2026-11-23 (ledger D-0573 to D-0576):** row 1 now reads "the meaning is the recipe maker's"; row 4 is settled (required in the block); row 8 (`demo_abromics`) is settled by her words "remove the null and empty rows from the metadata" and "it must not contain errors nor missing data. A rule". The rows 2, 3, 5, 6, 7 have a new status in the new section.

| Question | Her words settle | Remains |
|---|---|---|
| 1. A never-analysed entity counted as "not detected"? | settled: the meaning is the recipe maker's, "which only a recipe maker (in collaboration with a real user) can decide"; with B6 such an entity would show as "no result in file" (working name; since D-0573 the marker is called "not in original data") [applied late 2026-11-23, R13] | nothing for the app |
| 2. The name of the third class | "short and explicit", "a different kind of other missing value" | the short name |
| 3. May the app read the audit record to name a removal? | not answered; needed only for C and the line F | open, smaller |
| 4. Where the recipe says what a missing value means | "saying how those need to be processed in the recipe" | whether a required statement or only the steps |
| 5. The count per target | not answered | open |
| 6. The threshold in "not detected" | not settled by her exact words (her "3." is relayed by the review session as a filter on values) | open, low priority; flag 3 shows where it matters |
| 7. The number, the list or both | if B6 is chosen, both come from one table ("That would remove need for 6 anti join") [applied late 2026-11-23, R14] | how the list is shown (the key of a table as a result is open, D-0487) |
| 8. `demo_abromics`'s three id-less lines | "metadata should be clean - all with an id" and her order of D-0569 | to confirm in the dry run (D-0525) |

### Leans, as leans (two agents, two sentences)

> **Update of 2026-11-23:** these leans were written before her answers D-0573 to D-0576. They are history. The leans of the two agents on the new list are in the new section.
- Lean of the Sonnet agent, as a lean: (i-b), a read-time option, automatic for every result table that declares an entity id, with a required statement of the meaning, placed before the author's tier-1 steps (P1) so that the recipe's own steps say how the marked lines are processed, and reading the metadata as read from its file (α); the marker m1; with B6 the data table first, and an advice when a completed table is joined with the metadata first.
- Lean of the Opus agent, as a lean: if you choose B6, (i) a read-time option declared on the data table, automatic for every result table that declares an entity id, with its meaning required (variant i-b), done before the recipe's own tier-1 steps (P1, your words "at (first step)"), reading the metadata as read from its file (α), with the marker m1, a yes/no column beside empty cells; and the data table first. Reason: the recipe then states the completion, so the app does not modify the recipe; a removal written at the end of the result table's tier 1 runs after the completion and is complete; with the data table first the result keeps the initial population and its zeros; α keeps the result table's first place a first place (D-0553). What P1 asks of the recipe maker: a filter in that tier 1 that removes every line of an entity leaves it absent (on the demo, 6 entities of `Detailed_summary`); a rule written as a mark instead of a filter keeps it.

### The questions that remain for you, one at a time (each with what you would see on the demo)

> **Update of 2026-11-23 (ledger D-0573 to D-0579):** this list of ten is replaced by the list in the new section. Question 1 (where the completion lives) and questions 2 and 3 are settled in substance; question 8 is settled; question 9 changed (an error at the id level); questions 4, 5, 6, 7 and 10 are rewritten; nine new questions came (1, 2, 3, 4, 6, 9, 10, 11 and 13 of the new list; question 2 holds the old question 9). The ten are kept here as they were asked.

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

> **Update of 2026-11-23 (ledger D-0573):** run 7 (`not_in_metadata`) is void: there is no marker "not in metadata". Run 1 and run 2 use the marker "not in original data". Four runs are added in the new section, to run only after the code exists (D-0580).
1. **The completed table through the demo's chains (the recipe side).** Requirement: a scratch ResFinder file with the 4 added lines and the marker column written by hand (the completion does not exist), the chain of `qa_amr_genes_per_sample` joined data first and metadata first. Expected: `QA_AMR_per_sample` 74 rows, 42 per entity, 4 at 0; `status` "Detected" on the 4 and `total_gene_count` 1 unless the steps are adapted; `ST22_Anchor`'s `status` "Detected" for the 4; row counts of `QA_fanout_exhibit` and `ST22_Anchor` unchanged; the heatmap's handling of an empty gene observed. Independence: a scratch recipe from the demo's schemas, every table rebuilt in its own empty folder, no lineage code.
2. **A removal on the completed table.** Requirement: a removal by key at the end of ResFinder's tier 1 in a scratch audit copy (the step written by hand). Expected: data first 41 samples, 4 at 0; metadata first with the marker read 37 / 4 / 1 "no line"; metadata first, genes only, 42 samples with 5 at 0. Independence: as 1.
3. **The marker forms.** Requirement: the same chain with a marker column and with a sentinel word. Expected: `gene.count()` 0 against 1. Independence: Polars on a scratch table, no recipe code.
4. **P1 against P2 on `Detailed_summary`.** Requirement: the completion by hand before and after its filters. Expected: no added line before; 6 marked lines after. Independence: as 1.
5. **The keys (once (i) or (ii) is built; with (iii) the key moves with the file only).** Requirement: a change in the metadata file changes the key of every completed table and the tables below (D-0560). Expected: every key differs; a stale stored table is not served. Independence: each variant in its own empty folder; the keys from the engine's own key functions on a hand-edited scratch recipe.
6. **The app's completion and the graph** (once built): the same points as 1 on the real option, and the valid sets of places with its new edge (D-0553), α and β.
7. **`not_in_metadata`** (if chosen): the lines of a scratch result file with an id in no metadata.

---

## Added 2026-11-23 (ledger D-0573 to D-0579): her decisions on the ids, the completion and the log; the updated list of what is still hers to answer

Not yet in the signed text above. The text above is kept; where her answers made a part stale, it is marked there. **She wrote, about the code: "the problem is the code is not build yet ...but I guess that helps knowing what needs to be build" [HER WORDS D-0573].** So this section keeps apart what the code does today ([TODAY]) and what has to be built ([TO BUILD]).

### Her words, exact

**Block M629 (ledger D-0573).** "seems opus agent checked against the code .. the problem is the code is not build yet ...but I guess that helps knowing what needs to be build... We need to fix the metadata - it must not contain errors nor missing data. A rule. The marker of "not in original data" is not a zero ... right now our recipe does not say how to process those cases. Not sure the agent have understood the functionning the sets at correction 1. test inclusions : are all original data id included in metadata ? -> yes no problem / no -> warn and include those present in metadata to original data - with the specific marker "not in original data" 2. second test inclusion are all id in metadata included in original data ? -> yes no problem // no - inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start : if the user does not know this id or its false it can add it temporaly and fill with dummy fill and say I need to remove those ids afterwards eg. because eg they are wrong." And her answer to two questions: "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id) - A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)  - yes - can you send again for review ?" [HER WORDS D-0573]

**Block M630 (ledger D-0574).** "yes so it does not record directly in the recipe how many were added because it would modify the recipe and we cannot do that BUT as it reports it in the log then this is transparent correct ? Once per data batch - and yes confirmation and what as added is kept in the session log - I think we need to force - it makes it transparent, it makes thinking about it - and it will avoid problems to the maker when those problem arrise and there ia a clear treatment. I think once per data batch (as recalled by session ?) - the recipe required on every result table - and once for each data batch - the user must only to accept once." [HER WORDS D-0574] (Before that, on seeing option (i) explained: "I would lean also to add this in the recipe", relayed in the channel; it is not in the ledger's exact words.)

> **Changed by D-0581 and D-0582:** with no panel nobody can accept; automatic, logged "automatic, no user". With a panel: a red warning and an "I have read this" button that does not block (her "b) that is good"; the button is the review session's reading of the question she answered).

**Block M631 (ledger D-0575).** "yes that must be in the export - we might need logs for different things - maybe better to keep the id adding in a separate log ? - wait for other questions now we need to get to the bottom of this" [HER WORDS D-0575]

**Block M632 (ledger D-0576).** "yes separate log" [HER WORDS D-0576]

> **Extended by D-0581:** the log is written automatically, in a specific directory, also where no session exists.

**Block M633 (ledger D-0577).** "I think we need them to review their evaluations of what I should answer now that we should have added some solutions to problems" [HER WORDS D-0577]

**Block M634 (ledger D-0578).** "the RECIPES_FROM_THE_MODEL_AGREED.md needs to be reviewed also - we have made significant choices already and found solutions." [HER WORDS D-0578]

**Block M635 (ledger D-0579).** "there are 2 directions in the test - what is missing in one and in other and vis versa - what is test 1 and test 2 - does not really mater however it might be more logical to have test 2 as the first test .... stopping first no ?" [HER WORDS D-0579]

### What is DECIDED in her words, and what is only the review session's reading

| What | Her words | Line |
|---|---|---|
| The metadata is refused when it has errors or missing data at the id level only; true missing data in other columns does not refuse it; the user is responsible | "refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)" | D-0573 |
| The two directions of the check; the numbering does not matter (naming them X and Y by content is the review session's reading) | "there are 2 directions in the test"; "what is test 1 and test 2 - does not really mater" | D-0579 |
| **Check X**: an id of the original data that the metadata lacks: inform, list; the user adds it to the metadata and uploads again; verification starts again; an unknown or false id may be added with a dummy fill and a note to remove it | "no - inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start" | D-0573 (the pairing of her question and her action is the review session's reading, confirmed by her "yes") |
| **Check Y**: an id of the metadata that the original data lacks: warn; include it in the original data with the marker "not in original data"; the user confirms; the confirmation is noted in the log | "warn and include those present in metadata to original data - with the specific marker "not in original data""; "A user confirm is good"; "noted in the log" | D-0573 |
| The marker is called "not in original data" and is not a zero | "The marker of "not in original data" is not a zero" | D-0573 |
| The recipe does not say today how to process those cases | "right now our recipe does not say how to process those cases" | D-0573 |
| The completion is in the recipe, required on every result table, forced | "the recipe required on every result table"; "I think we need to force" | D-0574 |
| The recipe never records how many lines were added | "it does not record directly in the recipe how many were added because it would modify the recipe" | D-0574 |
| Once per data batch; the user accepts once; the acceptance and what was added are in the session log | "Once per data batch ... the user must only to accept once"; "confirmation and what as added is kept in the session log" | D-0574 |
| The record is in the export | "yes that must be in the export" | D-0575 |
| A separate log | "yes separate log" | D-0576 |
| Order check X first, stopping first? | "it might be more logical to have test 2 as the first test .... stopping first no ?" | D-0579 (a question of hers, not a decision) |

> **Changed by D-0581 and D-0582 (2026-11-23):** row 1 ("The metadata is refused ...") becomes a red warning and an automatic handling, not a refusal (the review session's reading); the rule "it must not contain errors nor missing data" stays as the goal. The confirmation in the rows of check Y and of "once per data batch" is replaced: with a panel by a red warning and an "I have read this" button that does not block; with no panel the completion is automatic and the log says "automatic, no user". The row on "stopping first" is answered: both notes at once, never a hard stop.

**The review session's reading, not hers** (D-0573 to D-0576): that the form is "(i-b), a block done by the app when it reads the file"; that the log of the completion is beside the audit log, in the session and in the export; that the acceptance is stored under the session key. **NOT decided** (the ledger says so): the form and key names of the block; the format, name and entries of the log; what the code does with the session key and a deleted session.

### What the code does today, and what has to be built

| Topic | [TODAY] | [TO BUILD] |
|---|---|---|
| Refusal of a metadata with bad ids | Nothing compares or checks ids. The data check builds each table alone after its tier 1 [CODE READ `data_analysis_recipe_validator.py:485-545`]. The gate rejects a recipe on a structure or data problem [CODE READ `bootloader.py:431-459`]. An empty id is missing only through the declared null words (`null_values: ["", "-"]` on the demo's id field [RECIPE FILE]); a cell of spaces stays text [CODE READ `declared.py:115-120`]. E02/E03 check the declared population and a number type on an id [CODE READ `recipe_check.py:332-348, 445-458`] | The check of the metadata's ids as READ (before tier 1), its refusal, with a plain line naming file, lines and ids |
| Checks X and Y | Nothing compares the ids of two tables | both checks; the list of ids shown to the user |
| The completion | no key, no action: no step appends rows; a schema's tier 1 runs on its own table [CODE READ `orchestrator.py:282-295`]; an unknown key is refused (S01) [CODE READ `recipe_check.py:390`] | the block, the completion after `_read_source` (before or after the author's tier-1 steps: question 7), a new edge in the graph, a new part of the table's key |
| The confirmation, once per batch | the session key exists [CODE READ `session_manager.py:10, 305-308`] | the stored acceptance, the dialog |
| The log | on `dev`, the session holds `assembly.json` and `t3_<time>.json` (with a `notification_log`); no audit log; D-0315 and D-0478 are decided, not built | the id log and its writer |
| The data check that only informs | does not exist: the data check returns problems only; advices come from the recipe check [CODE READ `bootloader.py:431-451`] | the new channel (decided, D-0569) |

### The flags (what could change a result without a message, hide a step, or reconsider a decision)

1. **"Not a zero" against today's count steps.** The demo's count of values gives 0 and its count of rows gives 1 for a line with empty cells; the plot says "4 with 0 genes". Her rule cannot hold by default. [RECIPE FILE; POLARS SEMANTICS] (question 5)
2. **The stop at check X may reverse D-0569 (b).** D-0569: the data check only informs. D-0573 and D-0579: refuse; "stopping first". Both are hers. She must say which holds for check X. (question 1)
3. **A refusal at the gate closes the recipe** and, where the selector is hidden (the pipeline profiles), the app stops at start; her loop "re-upload" has no way in for a refused recipe. [CODE READ `bootloader.py:453-459`; RULE FILE `rules_data_analysis_recipe_structure.md` 11a] (question 3)

   > **Changed by D-0581:** no check refuses or closes a recipe; the flag stays as history. The risk that remains is a deployment where nothing can be written (see the new section).
4. **`demo_abromics` is refused as shipped** (3 lines with no id: file lines 5, 6, 11). Her order D-0569 corrects the file in the dry run.
5. **A dummy id does not leave through the metadata.** Check X fires again because the result file still holds the id; it leaves through a removal by key or "remove from all the data" (library built, screen not built), or a new file. (question 11)
6. **"Required on every result table": two readings.** Every result table (then one with no entity id says so), or every one that declares an entity id. (question 6)
7. **No confirmation: what then?** Not said in her words. Each answer closes something (question 4).
8. **The marker and the added lines are visible in the export and the log, not in the recipe.** She asked that the recipe does not record the count. So the figure must carry, in the export, the log and a line in the README and the report, that lines were added. Otherwise a published figure shows 4 entities that were added from the metadata with no sign. Her own check: "then this is transparent, correct?" Only if the same record is in the export (D-0575). [REASONED; her decision D-0575]

### The open points, each with the evidence by reading

**The session key and "once per data batch, as recalled by session ?"** (her question). The key is `recipe hash[:12] : data batch hash[:12]` [CODE READ `session_manager.py:10, 305-308`]. The batch hash covers every dataset of the recipe, the metadata included [CODE READ `session_manager.py:294-299`; `orchestrator.py:793-821`; `cache_keys.py:139-152`]. So a changed metadata or result file asks again; **an edit of the recipe also asks again** (the recipe hash is in the key); a deleted session asks again (`delete_session`, `:774-778`); another machine or user asks again; a session zip carries the log. In the pipeline profiles there is no session [RULE FILE `rules_app_features_flags.md` flag matrix]: no place to store an acceptance. **Fixing the metadata is itself a new batch.** (question 9)

**Where a refusal of the metadata can sit.** [TODAY] three places read a recipe's data: the HOME gate (a problem rejects the recipe), BLUEPRINT's Validate (reports, never blocks) and Data Import (checks a candidate file by the ingestion's own read, all files or none). Seats: (s1) at the gate: the recipe cannot open; (s2) in Data Import: an uploaded metadata with id errors is refused and the old file stays: where her loop lives; (s3) both, with a way in for a refused recipe. A deployment with no upload panel (`metadata_ingestion_enabled` false) cannot re-upload: the fix is upstream and the refusal shows the contact. (question 3)

**The cases around the two checks.** A repeated id in the metadata multiplies the rows of a join with the metadata second [ESTABLISHED: RECIPES G9, G13]; whether a repeat is an error at the id level is her question 2: her approved sentence (D-0567, G4) allows a repeated id in a long table, and nothing yet says that the metadata has one row per entity. A table with no entity id (a look-up such as the APEC list): never checked or completed. A recipe with no metadata block (`figshare_integration`: its metadata is a data schema): the checks cannot run without a table named the metadata (`metadata_schema`, or `entity.population` [CODE READ `recipe_check.py:332-348`]). (questions 2, 13)

**The marker and "not a zero".** Polars has one missing value (null) and NaN for floats [POLARS SEMANTICS]; a second kind must sit beside the empty cells. Forms: (m1a) a yes/no column named after the marker, for example `not_in_original_data`, label "not in original data" (through the join's `labels` mapping, `recipe_spec.yaml:44`); (m1b) a text column whose value is the marker. After a left join from the metadata an entity with no line has the marker empty in both: a third state, "no line". What each aggregate gives for a line whose cells are empty:

| Aggregate | Result for an added line | Compatible with "not a zero"? |
|---|---|---|
| count of values (`pl.col('gene').count()`) | 0 | no, unless the recipe states "nothing found" |
| count of rows (`pl.len()`) | 1 | no |
| sum | 0 | no, unless stated |
| mean, minimum, maximum | missing | yes |
| distinct count | 1 | no |
| a stamp (`status: pl.lit('Detected')`) | "Detected" | no: the demo's ResFinder stamps every line, and `ST22_Anchor` and `integration_plot` carry it |

Ways to keep her rule: (z1) the required meaning is chosen from a few words the check knows ("nothing found", "not analysed", ...), and a count is refused unless the marker is named (a match on the text of the steps, which can miss a case); (z2) the meaning is free text and the data check says how many marked lines each count met; (z3) she says what she meant. (question 5)

**The position.** Her words: "an automatic completion at (first step)"; "this might be before T1 a step the app does". Read as before the recipe's own tier-1 steps (P1). With P1 the recipe's own steps see the added lines (the stamp and the row count must be adapted); a filter that removes every line of an entity leaves it absent (on the demo, 6 entities of `Detailed_summary`: 42 ids in the file, 36 after its three filters [ESTABLISHED: RECIPES G12; engine run RR2; `Detailed_summary_wrangling.yaml:20, 25, 30`]). With P2 (after the author's tier-1 steps and before the audit steps) the author's steps cannot say how to process them, against "processed as a normal recipe". After the audit steps is never right: the completion would add back an entity the user removed [CODE READ `data_wrangler.py:92`]. (question 7)

**Which metadata.** (α) as read from its file, after the id check: the result table's first place stays a first place (D-0553); a step at the metadata's place does not remove an added line. (β) after its tier 1: a step at the metadata removes the added line, but the result table's first place lies below the metadata's: two places on one path, refused by her rule "the user chooses at most one place" [HER WORDS D-0553]. (question 8)

**The join order.** With the completion, a join with the result table first and the metadata second keeps every entity: the added lines are in the result table. Her direction "the join should not start with the medata or we need a solution we do not have yet" [HER WORDS D-0564] can then be followed without losing an entity. A rule, an advice or documentation? (question 12)

### The separate log (her "yes separate log"; format, name and entries open)

[TODAY] On `dev` the session folder holds `assembly.json` and `t3_<time>.json`. Only on the held branch `task/audit-slice1-effects-log` (commit 42d5ae6d) is there `audit_log.py`, writing `audit_log.yaml` with `format: 1`; its keys are provisional [CODE READ `git show task/audit-slice1-effects-log:libs/utils/src/utils/audit_log.py`]. D-0478 (audit log in the bundle) is decided, not built.

| Option | What it is | Pro | Con |
|---|---|---|---|
| L1 | one file of its own for the ids, beside the audit log, in the session and in the export | her "separate"; the audit log is untouched; each file readable by itself | two files to name in the README and the report |
| L2 | one log with entries of several kinds | one story in time | changes the audit log's file; against "separate" |
| L3 | the record only in the export, no file | nothing new in the session | the acceptance is not kept; against D-0574 |

**Both agents recommend L1 (as a recommendation, hers to decide).** The form, in the manner of `audit_log.py` (the same rules, no import): one YAML file in the session folder, starting with `format: 1`; a reader refuses an unknown format; the date and the initials are given by the caller; data only; name PROVISIONAL `id_log.yaml`. Entries (one per event, keys PROVISIONAL): `metadata_refused` (when; the file and its hash; each problem: line, id, why), `ids_not_in_metadata` (check X: the table, the ids), `check_x_stopped`, `completion` (per result table: the file hashes, the ids added, their count, the marker, the meaning the recipe states), `accepted` (who, when, the sentence shown, the session key), `not_confirmed`, `dummy_ids_declared`. In the export: beside the audit log of D-0478, as its own file; the README says in one line what it is; `report.qmd` has a short section per table: the ids added, the marker, the meaning. The acceptance is once per data batch because the session key changes with the batch. A refusal when no session exists yet (a refused recipe never opens): written to the export of the next session, or to a log at the deployment level (question 10). The audit log of D-0478 is unchanged.

### The two checks, their order and the stop (her question D-0579)

> **Answered by D-0581 (2026-11-23):** both notes at once, never a hard stop. The case for and against is history. The reading (c) of "stopping first" is hers; (a) and (b) are void.

She proposes: run check X first and STOP there when it finds ids; check Y only when X passes ("stopping first no ?"). The case for and against, with the evidence:

**For.** (1) A typo shows twice: the data holds `S1`, the metadata `S01`; X lists `S1`, Y lists `S01`. If Y is confirmed first, the user confirms a marked line for `S01`, a false absence. After the fix both lists are empty. (2) Fixing the metadata is a new data batch (new session key), so a confirmation given before the fix is lost and the log holds a confirmation of a list that never became true. (3) The metadata is the reference of both checks and is refused when its own ids are wrong (D-0573). (4) On the demo it costs nothing: X finds 0 ids (every id of every result file is in the metadata [ESTABLISHED: OVERLAP section 1]) and Y finds 4 for ResFinder; `left_join_lesson` has 2 for X (`ACC0001`, `ACC0002`).

**Against, or to qualify.** (1) A user who cannot fix is blocked: with no upload panel (the static, simple, demo-vetinst and web-demo profiles) a stop is a refusal of the recipe and the app stops at start with the cause and the contact. (2) If "stop" means refuse, it reverses D-0569 (b) for X. (3) A result file may legitimately hold an id the metadata lacks (a control sample): the dummy fill is the way out, and it adds a dummy entity to every result until removed. (4) BLUEPRINT's Validate reports and never blocks.

**Three readings of "stopping first".** (a) Refuse: the recipe does not open until the metadata is fixed. (b) Hold Y: the recipe opens with X's note; Y's list is shown as information, nothing is completed or confirmed until X passes. (c) No stop: X and Y are both shown and Y's confirmation is asked at once.

**Lean of the Sonnet agent, as a lean:** (b): it keeps her order and her earlier decision, and nothing is confirmed, completed or logged on a list that will change. (a) follows her words most literally. Whatever she chooses, the order is: (0) the metadata's own ids (refuse); (1) X; (2) Y with the confirmation. **Lean of the Opus agent, as a lean:** (b) as well: it keeps her D-0569 (X informs) and her order (Y waits for X), so nothing is confirmed, completed or logged on a list that the fix of the metadata will change (the typo case); (a) is the more literal reading of "stopping first" and closes the recipe where no one can fix the metadata.

### The updated list of what is still hers to answer (her order M633, M634)

#### (a) The ten questions of the D-0572 section: which are settled by her words

| # | Question | Now | Her line |
|---|---|---|---|
| 1 | Where the completion lives | SETTLED in substance: in the recipe, required on every result table. The form (a block the app reads, or a first step you write) is read as (i-b), not stated | D-0574; relay "I would lean also to add this in the recipe" |
| 2 | One line in the recipe or none | SETTLED: required on every result table | D-0574 "the recipe required on every result table" |
| 3 | The meaning required, or the note enough | SETTLED: required ("force") | D-0574 |
| 4 | The marker: form and name | NAME SETTLED ("not in original data", not a zero). FORM open | D-0573 |
| 5 | Before or after the recipe's tier-1 steps | OPEN (her words read as before) | D-0572 |
| 6 | Which metadata | OPEN | none |
| 7 | The join order | OPEN, narrower | none |
| 8 | The marker "not in metadata" | SETTLED: none; the user corrects the metadata (or adds a dummy) and uploads again | D-0573 (the review session's reading, confirmed "yes") |
| 9 | A note for a repeated id | CHANGED: an error at the id level, or a note | D-0573 |
| 10 | The count per target | OPEN, unchanged | none |

#### (b) The eight questions of the D-0570 section, and Part 1, Part 2

| Item | Now | Line |
|---|---|---|
| 1 A never-analysed entity counted as "not detected" | SETTLED: the meaning is the recipe maker's; the marked line is not "not detected" unless the recipe says so | D-0572, D-0573, D-0574 |
| 2 The name of the third class | SETTLED: "not in original data" | D-0573 |
| 3 The app reads the audit record | NO LONGER NEEDED for the completion; only for the information line F | D-0574 |
| 4 Where the recipe says what a missing value means | SETTLED: in the required block, on each result table | D-0574 |
| 5 The count per target | OPEN | none |
| 6 The threshold in "not detected" | OPEN, low; touched by position (`Detailed_summary`) | none |
| 7 The number, the list or both | SETTLED in substance: both from the completed table (the marked lines); how a table result is shown is the open key of D-0487 | D-0572 ("That would remove need for 6 anti join") |
| 8 `demo_abromics`'s three id-less lines | SETTLED: the metadata must be clean; the file is corrected in the dry run | D-0569, D-0573 |
| Part 1 A, B | still possible spellings, no longer the way to give zeros | |
| Part 1 B2, B3, B4, B5, C, D, E | NO LONGER NEEDED for the zeros (the completion does the job); the agents' reading, not her words; history kept | D-0574 |
| Part 1 E2 (anti-join) | NO LONGER NEEDED by her words: "That would remove need for 6 anti join" | D-0572 |
| Part 1 B6 | DECIDED in substance (form open) | D-0574 |
| Part 2 F | the log and the alerts carry the counts; F as a screen line stays possible | D-0575, D-0576 |
| Part 2 G | ABSORBED by the required meaning; what the meaning may hold is open (question 5, 6) | D-0574 |

To confirm with her in one line at the end: "the candidates that the completion makes unnecessary are kept as history, none is deleted".

#### (c) The new list, one question at a time, in the recommended order

> **Changed by D-0581 and D-0582 (2026-11-23):** (questions 1 and 4 ANSWERED, by D-0581 and D-0582; 2, 3, 9, 10 REWRITTEN.) The list is updated in the table "The updated list" of the section "Added 2026-11-23 (ledger D-0581, D-0582)"; the questions below are kept as they were asked.

Each question is hers. Each says what she would see on the demo. Each ends with "Neither: say what you meant." Leans are the leans of the agents, as leans (where no lean is given, we have none). The first four are the same door: what happens when the ids do not agree.

**Settled, not asked any more:** the names of the two checks (check X, check Y, by content: her D-0579).

**Question 1. When an id of a result file is not in the metadata (check X): stop, or go on?** Your words: "stopping first no ?" (D-0579) and, earlier, "the user should better fix this" (D-0569, option b: inform only). Three ways: (a) the recipe does not open until the metadata is fixed; (b) the recipe opens, X's note is shown, and nothing is completed or confirmed until X passes; (c) both notes are shown at once and the completion is confirmed at once. On the demo: no result file has an id outside the metadata, so you see nothing; on the lesson template `left_join_lesson` you would see 2 ids (`ACC0001`, `ACC0002`) refused (a), noted with nothing completed (b), or noted with the completion asked (c). A typo (`S1` in the data, `S01` in the metadata) shows twice, once in each check; fixing the metadata is also a new data batch, so a confirmation given before the fix is asked again. In a deployment with no upload panel, (a) stops the app at start. Lean (Sonnet and Opus): (b). Neither: say what you meant.

> **Changed by D-0581 and D-0582:** ANSWERED by D-0581 (both notes at once, never a hard stop). See the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581, D-0582)".

**Question 2. Which errors in the ids refuse the metadata?** An id empty after the null words; a cell of spaces; an id repeated. A "false" id (a wrong but well-formed one) cannot be seen by the app. On the demo: the metadata has 42 distinct ids, none empty or repeated: it passes; `demo_abromics` as shipped has 3 lines with no id (file lines 5, 6, 11): refused until its file is corrected (the dry run does it). Lean: refuse the three, say plainly that a false id cannot be seen. Neither: say what you meant.

> **Changed by D-0581 and D-0582:** REWRITTEN: nothing is refused; which id errors raise a red warning, and what happens to the line. See the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581, D-0582)".

**Question 3. Where does the refusal sit, and in which order do the checks run?** At the opening (the recipe is not on HOME's list, with the reason and the contact; in a deployment with no selector the app stops at start); in Data Import (an upload with wrong ids is refused and the old file stays: this is where your "re-upload" loop lives); or both, with a way in for a refused recipe. The order: the metadata's own ids, then check X, then check Y with the confirmation. On the demo (developer profile): a bad upload is refused in Data Import and the old file stays; a bad shipped metadata takes its recipe off HOME's list with the contact; in `pipeline-static` the app stops at start. Lean (both agents): in Data Import and at the opening, and a way in for a refused recipe where the deployment has Data Import. Neither: say what you meant.

> **Changed by D-0581 and D-0582:** REWRITTEN: where the warning is shown and written. See the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581, D-0582)".

**Question 4. If the user does not confirm the completion (or nobody can), what happens?** (a) the recipe does not open; (b) the recipe opens with the table as in the file (no added lines) and a loud standing note on screen, in the export and in the log: "not confirmed"; (c) the recipe completes anyway and the log says "not confirmed". On the demo: (a) the recipe is not on the list, the reason names ResFinder and its 4 ids; (b) ResFinder has 70 lines; the plot shows what today's recipe shows (42 samples, 4 in the bar at 0, because `QA_AMR_per_sample` starts from the metadata; 38 samples where a join starts from ResFinder), with the note; (c) 74 lines, 4 marked. (b) and (c) can change a figure without the user having read the reason; (a) closes the recipe for everyone who cannot confirm. Lean (Opus): (b): nothing is added that the user did not accept, and no one is locked out; the standing note must also say that where a join starts from the metadata the entities with no line may show as 0. Sonnet: no lean, each closes something. Neither: say what you meant.

> **Changed by D-0581 and D-0582:** ANSWERED by D-0581 and D-0582: with a panel, a red warning and an "I have read this" button that does not block; with no panel, "automatic, no user" in the log. See the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581, D-0582)".

**Question 5. The marker and "not a zero".** You said the marker is not a zero. The demo's counts would turn the 4 added lines into a 0 (count of values) or a 1 (count of rows) by themselves. (i) The form: a yes/no column named after the marker, beside empty result cells; or a word in a column. (ii) What the required meaning may be: a few words the check knows ("nothing found", "not analysed"), or free text. On the demo: with the column and the meaning "nothing found", the plot keeps 4 samples in the bar at 0, by the recipe's own statement; with "not analysed", the 4 are shown apart, never as a silent 0; with a word in the gene column, `QA_AMR_per_sample` counts 1 gene for each of the 4 and the bar at 0 is empty. Lean (both agents): the yes/no column; the few words. Neither: say what you meant.

**Question 6. The block in the recipe: its form, the tables it covers, its names.** (i) A block that the app reads (the app adds the lines when it reads the file) or a first step you write in tier 1. (ii) "Every result table": a result table with no entity id says "no entity id" in its block, or must declare one first (your order D-0569: "Have the recipes declaire entity id"). (iii) The key names and what each holds. On the demo: ResFinder carries one block with its meaning; the APEC list has no entity id and is never completed; the 3 tables of `2_test_data_ST22_dummy` have no id today and must declare one. Lean: a block the app reads; declare the id first; the agents propose the key names after your answer. Neither: say what you meant.

**Question 7. When in the table: before or after the recipe's own tier-1 steps?** Your words: "an automatic completion at (first step)"; "this might be before T1 a step the app does". On the demo: before, ResFinder's stamp would read "Detected" on the 4 lines and its row count would give 1 for them (the recipe's steps must change); `Detailed_summary` (42 ids in the file, 36 after its filters) gets no added line and 6 entities are absent. After: the steps do not see the added lines and cannot say how to process them. Lean: before. Neither: say what you meant.
> **Added by D-0586:** her sentence "the treatmenet of the missing data must be defined before the filter likely - is it NA is it 0" supports the completion before the recipe's own tier-1 steps: the marked lines exist when the recipe states their treatment, before any filter can remove an entity (on the demo, the 6 entities of `Detailed_summary`). "likely" leaves the question open: still hers.

**Question 8. Which metadata does the completion read?** As read from its file (after the id check), or after its tier 1? On the demo: remove one of the 4 added entities at the metadata's place: from the file, it stays in ResFinder marked; after tier 1, it is no longer added, but ResFinder's place lies below the metadata's (one place per path: refused). Lean: as read. Neither: say what you meant.

**Question 9. Once per data batch: what asks again, and where there is no session.** Your words: "once per data batch (as recalled by session ?)" and "confirmation and what as added is kept in the session log". The session key holds the recipe too, so an edit of the recipe asks again; a changed metadata or result file asks again; a deleted session asks again; another machine asks again; a session zip carries the acceptance. In a deployment with no session (the pipeline profiles) there is no place: a standing acceptance written by the operator in the deployment and recorded in the export, or a confirmation at each opening recorded in the export only. On the demo: the dialog "4 lines will be added to ResFinder: <ids>. Confirm?" once; a changed metadata file asks again. Two points are yours: should an edit of the recipe (not of the data) ask again, as the session key makes it today; and where does the acceptance go in a deployment with no session. Lean (both): the session key as it is (an edit may change the stated meaning); with no session, a confirmation at each opening recorded in the export. Neither: say what you meant.

> **Changed by D-0581 and D-0582:** REWRITTEN (D-0582): nothing is accepted any more; the click is recorded. See the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581, D-0582)".

**Question 10. The log.** Our recommendation: a file of its own beside the audit log, in the session and in the export, `id_log.yaml`, starting with `format: 1`, the entries above; a refusal when no session exists written to the next export or to a log of the deployment. On the demo: one entry for ResFinder (4 ids, the marker, the meaning, who accepted and when), in the session folder and in the export, with one line in the README. Lean (both): this. Neither: say what you meant.

> **Changed by D-0581 and D-0582:** REWRITTEN: automatic, in a specific directory, also where no session exists; "MUST read that log". See the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581, D-0582)".

**Question 11. A temporary id (an unknown or false id added to the metadata with a dummy fill).** The app cannot tell a dummy from a real id unless it is marked. (a) a note given at upload and kept in the log, with a warning in the export while the log says dummy ids were declared and the data still holds them; (b) a column of the metadata the app reads; (c) nothing: the user's responsibility. It does not leave through the metadata (the result file still holds the id): it leaves through a removal by key, "remove from all the data", or a new file. On the demo: none; a dummy would appear in every plot with its dummy values until removed. Lean (Sonnet and Opus): (a). Neither: say what you meant.

**Question 12. The join order: a rule, an advice, or documentation?** With the completion, a join with the result table first and the metadata second keeps every entity. On the demo: remove one detected entity at ResFinder: result table first, 41 samples; metadata first and the marker read, 42 rows with 1 shown as "no line"; metadata first and genes only, 42 samples with 5 in the bar at 0. Lean (both): an advice. Neither: say what you meant.
> **Changed by D-0586:** the direction is decided in her words ("recipes should not start from the metadata"). How it is enforced (refused by the check, an advice, or documentation) is NOT stated: still hers.

**Question 13. A recipe with no metadata block** (`figshare_integration`: its metadata is a data schema). The checks cannot run. The check says so, or the recipe names its metadata. On the demo: none; `figshare_integration` shows the message. Lean: the recipe names it (in the dry run). Neither: say what you meant.

**Question 14. The count per target** (for each gene, how many entities do not carry it). None of the forms gives it. On the demo, for any one gene, how many of the 42 samples lack it. Unchanged. Neither: say what you meant.

**Question 15 (low). The threshold in "not detected".** Unchanged; touched by question 7. Neither: say what you meant.

(Not a question: `demo_abromics`'s three id-less lines. Your words "remove the null and empty rows from the metadata" (D-0569) and "it must not contain errors nor missing data. A rule" (D-0573); the change is shown in the dry run of the one big move, D-0525.)

#### (d) Runs: named only, to run after the code exists (her order D-0580)

No run is dispatched now: the code of the completion, of the two checks and of the id log is not built, so a run would test the old code and mean nothing. The expectations are written here and registered when the code exists. Runs 1 to 6 of the D-0572 section stand, with the marker "not in original data"; run 7 is void. Added, each "after the code exists": (8) the typo case (the data holds `S1`, the metadata `S01`: the first check lists `S1`, the second lists `S01`; after the fix both lists are empty; the session key changes with the metadata); (9) the id check of the metadata (an empty id, a cell of spaces, a repeated id, as she decides); (10) the session key (a changed metadata file gives another batch hash and key; an edit of one recipe file another recipe hash); (11) no confirmation (the chosen state of question 4). Each keeps its three points (requirement, expected, independence) and is registered before it runs.

---

## Added 2026-11-23 (ledger D-0581, D-0582): no blocking action, only warnings; automatic completion and automatic log; a red warning with a button

Not in the text above. It answers her question 1 and reopens some earlier words; the earlier lines are kept and marked "changed by D-0581" where they stand.

### Her words, exact

"I was looking at what the coordinator has posted about agents review work. I see one point the reviewers are correct : deployement without panel would be blocked so we need them to work without requesting confirmation. The deployement without panel means no user can accept anything - means that the ids missing ids (2 sided) needs to be fed automatically and the recipe needs to tell how those cases must be processed. Deployement without user agreement are expected from pipelines and data that arrives at regular updates - which means that those cases have to be thought before hand to ensure at best that cases of missing data id are limited - and they need to be treated correctly from the recipe at once. Which means that we cannot have blocking actions - only warnings - automatic fixing in the recipes and then ensuring that those cases are handled appropriately. Which means that the logs of the app including also the missing ids must also be written automatically in a specific directory.  This solution also allows the user to fix the metadata, add dummy and can upload again while letting the static deployements work. I think that answers Q1 - Both notes at once - and cannot be a hard stop - so it reopens one of my decision to allow deployements with no panel (static deployements) - But when the user has the panel important to have this warning in RED" [HER WORDS D-0581]

**Block M639 (ledger D-0582), her answer on what the user gets with a panel:** "This is correct - the user / person utilizing the results MUST read that log. b) that is good. And that allows the user to upload if he wants to." [HER WORDS D-0582] (The question she answered, put by the review session: with a panel, (a) a red warning only, or (b) a red warning and an "I have read this" button that does not block, the click recorded in the log; she chose (b).)

### What her words decide

- **No blocking action, only warnings.** "we cannot have blocking actions - only warnings".
- **The missing ids, on both sides, are fed automatically** where no user can accept ("The deployement without panel means no user can accept anything - means that the ids missing ids (2 sided) needs to be fed automatically"; with a panel: D-0582), and "the recipe needs to tell how those cases must be processed"; the cases are "treated correctly from the recipe at once".
- **The logs of the app, the missing ids included, are written automatically in a specific directory.**
- **Question 1 is answered: "Both notes at once - and cannot be a hard stop".** The two checks (ids of a result file not in the metadata; ids of the metadata not in a result file) both show their note, and nothing stops.
- **Where there is a panel, the warning is in RED.**
- **The user can still fix the metadata, add a dummy id and upload again**: "This solution also allows the user to fix the metadata, add dummy and can upload again while letting the static deployements work."
- **Deployments with no panel work without a confirmation**: "no user can accept anything".
- **With a panel: a red warning and a button "I have read this" that does not block; the click goes into the log of the ids; with no panel the log says "automatic, no user".** Her words: "This is correct - the user / person utilizing the results MUST read that log. b) that is good. And that allows the user to upload if he wants to." [HER WORDS D-0582]. (The button and what it records are the review session's question, which she answered with "b) that is good".)

### What this changes in her earlier words (each earlier line is kept)

| Earlier line | Now | Status |
|---|---|---|
| D-0573: "refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)" | a red warning and an automatic handling, not a refusal (the review session's reading; "it must not contain errors nor missing data. A rule" stays as the goal and as the warning) | CHANGED by D-0581 |
| D-0573: "A user confirm is good" and D-0574: "the user must only to accept once" | the confirmation is replaced: with a panel, a red warning and an "I have read this" button that does not block (the completion is applied anyway; the click goes into the log of the ids); with no panel the completion is automatic and the log says "automatic, no user" (the review session's reading of her "b) that is good", D-0582) | CHANGED by D-0581 and D-0582 |
| D-0579 (M635): "stopping first no ?" | answered: no stop, both notes at once | ANSWERED |
| D-0569 (b): the data check only informs | consistent | UNCHANGED |
| D-0574: the completion lives in the recipe, required on every result table; the recipe does not record the count | stays; the recipe states how the marked cases are processed | UNCHANGED |
| D-0575, D-0576: the record is in the export; a separate log | stays; the log is now written automatically, in a specific directory, also where no session exists | EXTENDED |
| "reopens one of my decision to allow deployements with no panel (static deployements)" | **her words say "reopens"; the review session reads that her decision to allow such deployments stands and the new principle is what lets them work** ("letting the static deployements work"). One line to confirm with her | CONFIRMED by D-0584 ("yes that was that") |
| D-0573, the review session's reading confirmed by her "yes" (kept here): "There is NO marker "not in metadata" in her flow" (check X; the earlier note of the D-0573 section) | an id of a result file in no metadata is entered automatically as a line of the metadata table, the other values missing, with a marker column "not in metadata" | CHANGED by D-0585 |

### Where her words do NOT say something (points for her)

1. **Answered by D-0582** ("b) that is good"): with a panel, a red warning and an "I have read this" button that does not block; the user may upload a corrected metadata whenever he wants. Still hers: once per data batch or at each opening; what is recorded with no session; how the user reaches the log and what the export says (questions 9 and 10 below).
2. **"The missing ids, 2 sided, are fed automatically": what is fed for an id of a result file that is not in the metadata?** For the other side (an id of the metadata not in a result file) her earlier words say: a line with the marker "not in original data". For this side her earlier flow had NO marker and the user added the id by hand. Automatic means the app does it. Options: (i) nothing is added to the metadata; the warning is red and logged; a join from the result table keeps the rows with empty metadata values (what the lesson template shows today); (ii) a line is added to the metadata table for the id, every other column empty, with a marker (a second marker, "not in metadata": this reverses the earlier "no marker"); (iii) the recipe says how, with no app default. What she would see: on `left_join_lesson`, 2 ids (`ACC0001`, `ACC0002`) of the file `sequenced` are not in its metadata [ESTABLISHED: OVERLAP section 1]: (i) the 2 rows keep empty metadata and a red warning; (ii) the metadata gains 2 lines marked "not in metadata"; on the demo nothing (0 ids outside the metadata). Lean (Sonnet, as a lean): (ii), because her words say both sides are fed and a recipe that is told how to process "those cases" needs the cases to be marked; to confirm that a second marker is what she means. Lean (Opus, as a lean): (ii) as well, for the same reason. What (ii) changes, said plainly: the entity enters the metadata table, so it enters every table that starts from the metadata with its metadata values empty (a count per entity includes it; a plot by country shows an empty country); with no panel only the log and the export say so. Neither: say what you meant.
   > **Answered by D-0585 (2026-11-23):** option (ii): a line is added to the metadata table with a marker. The earlier "no marker" is changed (see the table above). The lean of the text that follows is history.
3. **A line of the metadata with no usable id** (empty, spaces, `-`). It cannot be matched and cannot be completed. Under "no blocking" what happens to it? (a) kept: it stays in the metadata table, a red warning names the lines, the log records them; the recipe may drop it by a visible step as `demo_abromics` does (`demo_abromics.yaml:44-47`); (b) dropped by the app before the recipe reads, warned and logged; (c) the app does nothing and does not warn. Kept lines count: a grouping by the id makes one entity of all missing ids, an anti-join lists each [POLARS SEMANTICS; ESTABLISHED: CAUSE, D-0570 fact 6]. What she would see: the demo's metadata has none (42 distinct ids); `demo_abromics` as shipped has 3 lines (file lines 5, 6, 11): (a) red warning, 3 lines, then the recipe's own step removes them; (b) the app removes them first. Lean (Sonnet): (a): nothing is changed in the data without the recipe saying so (D-0574: "it would modify the recipe" is her argument for the log). Lean (Opus): (a), and the recipe states how such lines are processed, as for the marked lines, so that no line without an id enters a result without a written rule; a line that stays enters every table that starts from the metadata as one more entity, and with no panel only the log and the export show it. Neither: say what you meant.
   > **ANSWERED by D-0594 (her answer to the review session's question; its reading is in the D-0593 to D-0595 sub-section):** option (a): the line stays and is shown; the app does not remove, fix or convert it; a removal is a visible step the user writes in the recipe (see the D-0593 to D-0598 sub-section).
4. **What happens to an id repeated in the metadata** is not said either; the same options as 3.
   > **The principle of D-0594 (the review session's reading):** the app does not remove a repeated id; it shows it. The rest is kept for after the big line (M659).

### Two cautions (points for her, not corrections)

**1. An unattended pipeline completes a never-analysed entity with only the log as witness.** With no user and no confirmation the 4 added lines of `ResFinder` (on the demo) exist in the table with the marker "not in original data" and nothing on any screen. What must the required meaning say, and where does the reader of a published figure learn it? Her own rule: the same record is in the export (D-0575), which is also written without a user [RULE FILE `rules_app_features_flags.md`: `export_enabled` true in the static profile]. Already decided: the record is in the export ("yes that must be in the export" [HER WORDS D-0575]), and "the user / person utilizing the results MUST read that log" [HER WORDS D-0582]; so the README and the report carry a line such as "N lines were added automatically: read the log" (words PROVISIONAL). Point for her: whether the required meaning is chosen from a few words (so that "analysed, nothing found" is a deliberate statement and not a default) or free text.

**2. A deployment where nothing can be written must still not block.** Read:
- The user folder is the deployment's `user_data` (Location 4): `bootloader.get_location("user_data")` returns the resolved path and raises `KeyError` if the key is not defined [CODE READ `app/src/bootloader.py:846-855`]; the five location keys are required [CODE READ `bootloader.py:348-360`]; `local.yaml:13-26` lists `raw_data`, `data_analysis_recipes`, `cache`, `user_data`, `gallery`.
- Today `SessionManager(bootloader.get_location("user_data"))` is built at `app/src/server.py:150` and its constructor does `self.root.mkdir(parents=True, exist_ok=True)` with no handler [CODE READ `app/modules/session_manager.py:272-274`]: a folder that cannot be created raises at that line. **I found no handler for it by reading** (no try/except around `server.py:150`; I did not search the whole app). The stored tables folder `user_data/anchors` is read at `bootloader.py:204`; what it does when the folder is missing: not read.
- So today a non-writable user folder is not a warning: it ends the session start. That is the opposite of her principle; it is a point for the build, not an answer.
- **What exists for "a specific directory" for logs** (not invented): under `user_data` there are already `_sessions/<session_key>/` [CODE READ `session_manager.py:270, 314-317`], `_imports/<recipe id>/data/` [CODE READ `bootloader.py:857-861`] and `anchors/` [CODE READ `bootloader.py:204`]. Nothing exists for logs. A log directory would be a new sub-folder of `user_data` (next to those), or a place of its own in the deployment file; which, and whether a deployment may name it, is hers. Where the folder cannot be written: the log cannot be kept; to not block, the record goes into the export and the console, and the red warning says "the log could not be written". Points for her: that rule, and whether the export is then the only record.

### The updated list: what her new words do to each of the 15 questions

| # | Question (list of D-0573 to D-0579) | Now | New plain wording, with what she would see |
|---|---|---|---|
| 1 | Result-file ids not in the metadata: stop or go on? | **ANSWERED by D-0581**: both notes at once, never a hard stop | |
| 2 | Which id errors refuse the metadata? | **REWRITTEN**: refuse nothing; which id errors raise a red warning, and what happens to the line (point 3 above). **ANSWERED by D-0594 (her answer to the review session's question; its reading is in the D-0593 to D-0595 sub-section)** for a line with no usable id: kept and shown, never removed by the app | "A line of the metadata with no usable id: kept and warned, dropped and warned, or nothing?" On the demo: none; `demo_abromics`: 3 lines. Lean: kept and warned. Neither: say what you meant |
| 3 | Where does the refusal sit, order of the checks? | **DISSOLVED as a refusal; REWRITTEN**: where is the warning shown and written | "With a panel, the red warning is at the opening of the recipe, in Data Import after an upload, and in BLUEPRINT's check; with no panel, it is in the log and in the export. Is that all the places?" On the demo: a bad upload shows red and the file is taken (no refusal). Lean: those places. Neither: say what you meant |
| 4 | If the user does not confirm | **ANSWERED by D-0582**: with a panel, the red warning and the "I have read this" button that does not block; with no panel, "automatic, no user" in the log | |
| 5 | The marker and "not a zero" | **REWRITTEN** (sharper): unattended, the recipe's required meaning is the only treatment | "Must the required meaning be chosen from a few words, and does the export always say how many lines were added automatically?" (caution 1). Lean (both): few words. Neither: say what you meant |
| 6 | The block: form, tables, names | UNCHANGED | |
| 7 | The position | UNCHANGED | |
| 8 | Which metadata | UNCHANGED | |
| 9 | What asks again; where no session | **REWRITTEN** (D-0582): nothing is accepted any more; the click is recorded | "The red warning and its button "I have read this": once for each data batch (until the data or the recipe change) or at each opening? With no panel: is the log entry "automatic, no user" with the export the whole record?" On the demo with a panel: "4 ids of the metadata have no line in ResFinder: 4 lines added, marked "not in original data". [I have read this]", once per batch or at each opening; in `pipeline-static` no button, and the log says "automatic, no user". Lean: once per data batch (her word "Once per data batch" [D-0574]); with no session, the log in its directory and the export. Neither: say what you meant |
| 10 | The log | **REWRITTEN**: automatic, in a specific directory, also where no session exists; and when nothing can be written | "Where is the log directory (a sub-folder of `user_data`, or a place named in the deployment)? Since the person using the results MUST read it: does the red warning carry a link that opens the log of this data batch, and does the export hold the log, name it in the first line of the README and give it a section of the report?" Today the export has README.txt (a list of its files) and report.qmd with a section "Processing Issues During Session" that says "Review these before publishing results" [CODE READ `export_handlers.py:2012-2024, 2276-2300`]; no log of the ids exists, and the audit log (D-0478) is decided and not built. On the demo the bundle would hold the log with ResFinder's 4 ids, named first in the README. If the directory cannot be written, the export and the console carry the record. Lean: a sub-folder of `user_data`; a link from the warning; the log in the export, named first in the README and in the report. Neither: say what you meant |
| 11 | A dummy id | UNCHANGED (she says the user can still add one) | |
| 12 | The join order | UNCHANGED | |
| 13 | A recipe with no metadata block | UNCHANGED (the checks cannot run: a warning, not a block) | |
| 14 | The count per target | UNCHANGED | |
| 15 | The threshold | UNCHANGED | |
| new A | What is fed for a result-file id not in the metadata | NEW (point 2) | |
| new B | Whether her decision to allow no-panel deployments "reopens" | NEW, one line to confirm | |

### The next order, one at a time

1. **What is fed for a result-file id that is not in the metadata** (new A). ANSWERED by D-0585: a line is entered in the metadata table (the id, the other values missing) with a marker column named "not in metadata" (her "yes"; the name is the review session's suggestion).
2. **A metadata line with no usable id** (rewritten 2). Lean: kept and warned. **ANSWERED by D-0594 (her answer to the review session's question; its reading is in the D-0593 to D-0595 sub-section):** kept and shown; the app does not remove it.
3. **The button "I have read this": once per data batch or at each opening; the record with no session** (rewritten 9; question 4 answered by D-0582). Lean: once per data batch.
4. **Unattended: what the required meaning must say; the marker** (rewritten 5). Lean: few words.
5. **The block: form and tables** (6). Lean: block the app reads; declare the id first.
6. **Position** (7) and **which metadata** (8). Lean: before; as read.
7. **The log: its directory, when nothing can be written, how the user reaches it from the warning, how the export points to it** (rewritten 10; "MUST read that log", D-0582). Lean: a sub-folder of `user_data`; a link from the warning; named first in the README and the report.
8. **Where the red warning shows** (rewritten 3).
9. **A dummy id** (11). Lean: a note in the log.
10. **The join order** (12). Lean: an advice.
11. **A recipe with no metadata block** (13); **count per target** (14); **threshold** (15).
12. **One line to confirm**: her decision to allow no-panel deployments stands (new B). CONFIRMED by D-0584 ("yes that was that").

### Added 2026-11-23 (ledger D-0584, D-0585): her purpose; item 12 confirmed; item 1 answered

**Her words, exact.** "the line to confirm first - yes that was that. After my answer : we have done this mechansism so that the data can always use left joints to join with the metadata - limiting lineages problems. It would enter the id that must be added and the rest as missing values -> or I think there was a column that was added with the marker - so those type of missing values can be treated appropriately by the recipe maker. What is what you meant ?" [HER WORDS D-0584]. "1. yes because it cannot be done if the deployement is  static because there is no user to do the fix - the only fix can happen in there is a person surveilling the logs in the static deployements - this must be clear in the documentation. 2. yes" [HER WORDS D-0585]

**Decided in her words.**
- The decision to allow deployments with no panel stands: "yes that was that" [D-0584].
- **The purpose of the whole mechanism:** "so that the data can always use left joints to join with the metadata - limiting lineages problems" [D-0584].
- **An id of a result file that is in no metadata is entered:** the id, the rest as missing values, with a marker column, "so those type of missing values can be treated appropriately by the recipe maker" [D-0584]. She answered "1. yes" to the review session's question whether this reverses the earlier "no marker" [D-0585]. The name "not in metadata" is the review session's suggestion; she answered "2. yes" [D-0585].
- **The reason, in her words:** a static deployment has no user to do the fix; "the only fix can happen in there is a person surveilling the logs"; "this must be clear in the documentation" [D-0585]. (The held documentation task D-0583 carries it: the guidelines say early that a static deployment needs a person who reads the log of the ids.)
- **Not in her words:** the identifier of the marker column; whether the recipe must state a meaning for this marker; whether the marker column must be kept in the published columns of a table.

**What follows, by reading (no new derivation).**
1. **What a table that starts from the metadata shows for an added line:** one more entity, its metadata values empty (country, source, year), the marker set. A count per entity includes it; a plot by country shows an empty country.
   - On the demo, six tables start from the metadata: four join a data table (`ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`), and two are made from the metadata alone (`QA_year_types`, `QA_aggregated_no_key`) [ESTABLISHED: this file, the line "Joined tables that start from the metadata (first ingredient `metadata_schema`): 7" (6 in the demo recipe); RECIPE FILE `1_test_data_ST22_dummy.yaml:265-270` and `:289-294`: their only ingredient is `metadata_schema`; READ SCAN, both agents]. On the demo no id is added (0 ids outside the metadata).
   - **Flag (a result can change with no word in the table):** in a join with the data table first, the data id already kept its row before the completion, with its metadata values empty. After the completion it matches the added line, and the marker reaches the result only if the join's last `polars_select` keeps the marker column; the demo's joins publish a fixed list of columns [RECIPE FILE, for example `QA_AMR_per_sample_tier1.yaml`]. Otherwise nothing in the table says that the entity has no metadata; only the log and the warning say it.
   > **Answered by D-0586:** "yes flag column kept"; it may be removed as a last step for the plots only after the missing values are treated. Dry-run candidates, listed only: the tables whose tier 1 ends with a fixed column list (`polars_select`) and must keep the marker columns: the data tables `MLST` and `VirulenceFinder`, and the joins `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`, `QA_ST_with_NA` and `QA_L50_integer` [RECIPE FILE: `polars_select` in their tier-1 files].
   > **Her cost note, D-0587:** "then the fixed column list will need to be increased by the column that keeps the markers - or the missing data processed before and T1 and the column that keeps the markers explicitely dropped." Both ways are recipe-side; they go in the dry run (D-0525), listed only.
   - The same holds for the marker "not in original data" in a table that starts from the metadata.
2. **With her purpose, the 4 joins with a data table would be written data first, metadata second, `left`.** A dry-run candidate of the one big move (D-0525), listed only, not applied. The 2 tables made from the metadata alone cannot be written that way (they read no data table), so they always hold an added line. Whether "data first" is a rule, an advice or documentation stays her question 12.
   > **Corrected by D-0587:** "so they always hold an added line" is wrong. A metadata-only table holds a "not in metadata" line only if the line is added to the metadata table itself (placement (i), open) and a result file has an id outside the metadata. Her words: "here there is no original table".
3. **Which completion keeps which rows:**
   - In a join with the data table first and the metadata second, `left`, the completion "not in original data" keeps every metadata id. The completion "not in metadata" adds no row there (a left join from the data already kept the id); it adds the marker.
   - In a table that starts from the metadata, the completion "not in metadata" brings in every data id.
   - So with both completions, a left join loses no row in either direction.
   - What still breaks it:
     - a tier-1 filter that removes every line of an entity (on the demo, 6 entities of `Detailed_summary`);
     - a metadata line with no usable id (it never matches);
     - an id repeated in the metadata (rows multiply [ESTABLISHED: RECIPES G9, G13]);
     - the same id written two ways in the two tables (two entities, one marked on each side).
4. **A question for her: does the recipe need a stated meaning for "not in metadata", as it does for "not in original data"?**
   > **Answered by D-0586 (2026-11-23):** "A : required meaning".
   - On `left_join_lesson`: 2 ids (`ACC0001`, `ACC0002`) of `sequenced` are in no metadata [ESTABLISHED: OVERLAP section 1]; the metadata (10 ids) gains 2 lines with empty values and the marker.
   - With a required meaning, the check asks the recipe to say what such lines are (for example "kept, shown as unknown", or "excluded"). Without it, they pass as entities with empty values and only the log says so. On the demo: none.
   - Lean (Sonnet, as a lean): required, for the same reason as the first marker.
   - Lean (Opus, as a lean): required, for the same reason ("I think we need to force" [D-0574]), and the check advises when a table's published columns drop a marker column, so that the marker reaches the result.
   - Neither: say what you meant.

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
  > **Corrected by D-0587:** "would appear in them" holds only under placement (i) and only when a result file has an id outside the metadata; under (ii) they are untouched.
- **Options (hers), with what she would see:**
  - (a) Leave them as test tables of the QA canaries: the same three plots, made from the metadata.
  - (b) Rebuild the same canaries from a data table joined with the metadata, data first: the same three plots, made the way her rule writes recipes.
  - (c) Remove them: the QA canaries group loses these three plots, and the failure modes they guard are no longer shown.
  - Lean (Opus, as a lean): (b): the shipped demo then shows only the form her rule asks for, and the canaries keep testing what they test.
  - Lean (Sonnet, as a lean): (a): these tables join nothing, so her rule about joins does not touch them, and each exists to isolate one failure mode that needs no data table (the year label without ".0"; an aggregate with no `sample_id`, the fixture of the reach tests of issue 60, `QA_aggregated_no_key_tier1.yaml`). Rebuilding changes a shipped fixture for a rule they do not break. What does change in them is that an added "not in metadata" line enters them (an empty year and country, one more group counted in `qa_aggregated_no_key`): so the required meaning of D-0586 must say how those lines are treated there. (c) loses the three plots.
  > **Her words, D-0587:** "They break no rule to my opinion", and she asks "what to do with the two metadata-only tables?"; whether her "a)" answers the option (a) above is to be confirmed by her (two readings, see the D-0587 sub-section). The sentence of this lean about an added line entering them holds only under placement (i) (see the D-0587 sub-section).
  - Neither: say what you meant.

**The goal "equal id sets", in the data check.**
- [TODAY] The data check builds each table alone and compares no ids [CODE READ `app/modules/data_analysis_recipe_validator.py:485`; ESTABLISHED: OVERLAP section 2].
- [TO BUILD] One line per result table, words PROVISIONAL: "In <table>: the same ids as the metadata." or "In <table>: N ids are in the metadata only, M in this file only."
- It is shown with the other notes on the ids: the red warning where there is a panel, Data Import after an upload, BLUEPRINT's Validate, the log of the ids and the export.
- On the demo: every result table except ResFinder reads "the same ids"; ResFinder reads "4 in the metadata only, 0 in this file only" [ESTABLISHED: OVERLAP section 1].

### Added 2026-11-23 (ledger D-0587): where the "not in metadata" line is added; the two metadata-only tables

**Her words, exact.** "QA_year_types and QA_aggregated_no_key - so they old only metadata - but in the previous chat it said " They cannot be written that way, so they always hold an added line." why - there is no original data - all is metadata so all the ids are considered complete no  ? why should they always hold an added line ? They break no rule to my opinion - the line with "not in metadata" can only be done in an id is missing from the medata and is found in an original table - here there is no original table. Cost for the demo recipe - then the fixed column list will need to be increased by the column that keeps the markers - or the missing data processed before and T1 and the column that keeps the markers explicitely dropped. The goal "equal id sets" is also planned - yes. Question: what to do with the two metadata-only tables? a) this gives us an edge case - is the metadata registred under metadata schema or under dataschema ?" [HER WORDS D-0587]

**What her words say.**
- The two tables break no rule: "They break no rule to my opinion". She asks what to do with them ("Question: what to do with the two metadata-only tables?"); her "a)" has two readings, neither confirmed by her: the review session and the Opus agent read it as her answer, option (a), leave them; the Sonnet agent reads it as the first of her own points (the edge case of where the metadata is registered). One line to confirm with her: did your "a)" mean "leave the two tables as they are"? [two readings; changed in the check, 2026-11-23]
- A "not in metadata" line needs an id that is missing from the metadata AND found in an original table.
- **The cost for the demo:** where a join ends with a fixed column list, either the list gains the marker column, or "the missing data processed before and T1 and the column that keeps the markers explicitely dropped".
- The goal "equal id sets" is planned ("yes").

**Our sentence corrected.** "they always hold an added line" was wrong. A table made from the metadata alone holds a "not in metadata" line ONLY IF the line is added to the metadata table itself (placement (i) below) AND some result file of the recipe has an id outside the metadata. On the demo neither happens (0 ids outside the metadata [ESTABLISHED: OVERLAP section 1]). Under (ii) they never hold one.

**Open, hers: WHERE is the "not in metadata" line added?**
> **ANSWERED by D-0589: recipe-wide**, placement (i) (the review session's reading of her words below): with a metadata file attached, every result table and the metadata receive the ids they lack, with or without a join.
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
- Lean (Opus, as a lean): (ii): it is her reading of the metadata-only tables; the metadata stays one file's content, with no dependency on every data file and no new edge; and it can be written today with visible steps.
  > **Superseded by D-0589** (her words go the other way; kept as history).
- Lean (Sonnet, as a lean): (ii), for the reason of her purpose, fewer lineage problems: (i) adds an edge from every result file into the metadata's first place and makes the metadata's key depend on every data file, which she did not want for the two metadata-only tables; (ii) adds no edge and leaves the metadata exactly the file's content. What she would see on `left_join_lesson`: the metadata keeps its 10 lines and the join shows the 2 rows with empty metadata values and the marker. The price: every join that meets the metadata needs its marker (today written by visible steps; a join option or the app could write it), the metadata table does not hold the equal id sets by itself, and it reopens the placement of her "yes" of D-0585 (information, not an argument).
  > **Superseded by D-0589** (her words go the other way; kept as history).
- Neither: say what you meant.

**Her question: "is the metadata registred under metadata schema or under dataschema ?"**
- **Under its own top-level key `metadata_schema`** [RECIPE FILE `1_test_data_ST22_dummy.yaml:149`], apart from `data_schemas` (line 16) and `additional_datasets_schemas` (line 122).
- `metadata_schema` is a reserved schema id [CODE READ `libs/utils/src/utils/recipe_spec.yaml:80`], and the block is optional [`recipe_spec.yaml:24`]. The completion rule would name it by that id.
- **The edge case she means:** a recipe whose metadata is a data schema (`figshare_integration`). The checks cannot know which table is the metadata unless the recipe names it (the `metadata_schema` block, or `entity.population`): still hers (question 13).

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
- Lean (Sonnet, as a lean): (a) now, and one fact to read first: whether an empty `data_schemas` passes the check (not read). If it does, the case "a metadata block and no data table" is a STRUCTURAL condition the check can see without judging what a table holds, and I would then lean (b), an advice. What she would see: a recipe maker who registers a lone metadata file as the metadata gets a one-line advice at the check instead of a silent oddity; on the demo and in every Gallery bundle nothing changes (no shipped recipe has a metadata block and no data table: my search read the 50 recipe files that have `analysis_groups` under `config`, `assets` and `libs`, 8 with a `metadata_schema`, all 8 with a non-empty `data_schemas`).
- Neither: say what you meant.

**For the held documentation task (D-0583), in her words:** "if there is only "metadata" then it should go under the original_data - that will also help for the lineage".

**Next question (item 2). A line of the metadata with no usable id** (empty, spaces, `-`).
> **ANSWERED by D-0594 (her answer to the review session's question; its reading is in the D-0593 to D-0595 sub-section):** option (a); (b) falls (the app does not remove the line) and (c) falls (the app shows it) (the review session's reading).
- It can never be matched. With your purpose (data first, metadata second, `left`) it adds no row, and nothing in the result shows it; only the red warning and the log name it.
- What her rule of D-0586 changes: with no table that starts a join from the metadata, such a line adds no row anywhere, except in the two tables made from the metadata alone (`QA_year_types`, `QA_aggregated_no_key`), where it is one more entity with no id.
- What placement (i) or (ii) changes for it: nothing. A metadata line with no usable id is in the metadata table either way; neither placement adds or removes it.
- In a table that starts from the metadata, all such lines together make one entity with no id [POLARS SEMANTICS; ESTABLISHED: D-0570 fact 6].
- Should the line:
  - (a) stay in the metadata table, the recipe removing it by a visible step as `demo_abromics` does (`demo_abromics.yaml:44-47`);
  - (b) be removed by the app before the recipe reads, said in the warning and the log;
  - (c) nothing?
- On the demo: none (42 distinct ids). `demo_abromics` as shipped has 3 such lines (file lines 5, 6, 11): (a) a red warning "3 lines have no id", then its own step removes them (27 rows); (b) the app removes them first.
- Lean (Sonnet, as a lean): (a): the app changes no data without the recipe saying so.
- Lean (Opus, as a lean): (a), and the recipe states how such lines are processed, as for the two markers, so that no line without an id enters a table that starts from the metadata without a written rule.
- Neither: say what you meant.

---

### Added 2026-11-23 (ledger D-0589): the completion is recipe-wide, with or without a join; her use case

**Her words, exact.** "yes we should consider results where no metadata is joined - I think that as long as a metadata file is attached then all the original results should received the ids - whether or not the join - Our pipeline is supposed to work on set where ids are identical both between results and metadata - if not we need to add the ids to tables and metadata respectively even in an abscence of join and need clearly to treat what those missing ids mean ... I think that is our use case ..." [HER WORDS D-0589]

**What her words say (she writes "I think": her view of the use case, recorded as she wrote it).**
- "as long as a metadata file is attached then all the original results should received the ids - whether or not the join".
- **The use case:** "Our pipeline is supposed to work on set where ids are identical both between results and metadata".
- **If not:** "add the ids to tables and metadata respectively even in an abscence of join and need clearly to treat what those missing ids mean".
- The review session's reading: this is placement (i) of the D-0587 sub-section; both leans for (ii) are superseded.

**Consequences, by reading and reasoning (no new numbers).**
- **(a) A result table that no join touches still shows the added lines.** On the demo, four plots read a table with no metadata join: `amr_heatmap` (reads `ResFinder`), `phenotype_genome_length_fragmentation` (reads `Summary` and `Summary_quality`), `qa_sequence_type_missing` (reads `QA_ST_with_NA`, made from `Summary_quality`) and `qa_l50_integer` (reads `QA_L50_integer`, made from `Quast`) [READ SCAN of the demo recipe, Sonnet agent in the check; the four are named in `DIFFERENCES.md (removed 2026-11-24 in the cleaning of the studies; see git history):229` and `GOALS_REVIEW_sonnet.md (removed 2026-11-24 in the cleaning of the studies; see git history):412`]. Only ResFinder lacks ids (38 of 42); `Summary`, `Summary_quality` and `Quast` hold all 42 and get nothing [ESTABLISHED: OVERLAP section 1]. So on the demo only `amr_heatmap` gets added lines (4); the other three plots are unchanged. How they are drawn is the run already registered. The recipe's steps must say how the added lines are treated (the required meaning, D-0574, D-0586). [bullet (a) corrected by the Sonnet agent in the check: the plots and the source tag]
- **(b) The two metadata-only tables hold a "not in metadata" line WHENEVER the metadata is completed**, not "always". On the demo: never (0 ids outside the metadata). On `left_join_lesson`: 2 [ESTABLISHED: OVERLAP section 1].
- **(c) Keys and places.** The completed metadata reads every result file, and every completed result table reads the metadata file (a stored table's key holds the files it reads [CODE READ `app/modules/cache_keys.py:14-20`]). So a change in any file rebuilds every table below it ("we need to ensure that everystep after a change in a place is recalculated" [HER WORDS D-0560]): a fact, not a cost argument. Her rule of places (D-0553: at most one chosen place on a path; the original parents may all be chosen) holds in one way and not in the other:
  - **(A) The completion reads the FILES as read**, before any place. The first places stay original parents side by side, no place lies below another, and an audit step never changes what is completed.
  - **(B) The completion follows the places** (it reads the tables after their steps): an entity removed at the metadata is no longer added to the results; but a result table's first place then lies below the metadata's, two places on one path.
  - Which one her use case (her words: "ids are identical both between results and metadata") points to is hers.
- **(d) No cycle** when both completions read the files: the union of the ids is computed once from the files, and each table is completed to it. A cycle appears only if the metadata is completed from completed result tables, which are themselves completed from the completed metadata (both under (B)).
- **(e) "Equal id sets" is the state AFTER the completion**; the data check reports the differences found BEFORE it.
  - Equal in every table only if each result table is completed to the union, and not to the metadata file alone. Otherwise an id found only in another result file reaches the metadata but not the other result tables.
- **(f) "Recipes do not start from the metadata" (D-0586) stands** for the joins.
- **(g) No metadata attached: no completion,** and no id check unless the recipe declares a population. The recipe check reads the metadata block only when present and requires none [CODE READ `libs/utils/src/utils/recipe_check.py:356-357, 381-384`]: today it says nothing there.
  > **CHANGED by D-0590:** with no metadata attached, the original tables complete each other ("Case 1 no metadata -> completions and reverification of test 3"). The sentence above is kept as history.

**What remains hers, one at a time.**
1. **The completion reads the files as read (A), or follows the places (B)?** (This is the earlier question "which metadata", now for both directions.) On the demo, remove at the metadata one of the 4 ids that ResFinder lacks: with (A) ResFinder keeps its added line for it; with (B) it is no longer added, and ResFinder's first place lies below the metadata's. Lean (Opus, as a lean): (A): no cycle, her rule of places holds, and an audit step never changes what is completed.
   Lean (Sonnet, as a lean): (A), for the same reasons; the price is that an entity removed at the metadata alone is still added, marked, to a result table that lacks it, so the removal must be written at every first place ("Remove from all the data"; audit steps run after the completion, `data_wrangler.py:92`), which is what her purpose of one clean left join wants anyway. Neither: say what you meant.
2. **The reference of a result table's completion: the metadata's ids, or the union of all ids (every table identical)?** On the demo: no difference (0 ids outside the metadata). With two result files, an id that only one of them holds: under "the union" it is added, marked, to the other one too. Lean (Opus, as a lean): the union, her use case "ids are identical both between results and metadata".
   Lean (Sonnet, as a lean): the union: only then are the sets identical in every table, as her use case says. On `left_join_lesson` (one result table, `sequenced`) the two references give the same: the metadata gains `ACC0001` and `ACC0002`, `sequenced` gains its 2 missing metadata ids; the difference shows only with two result files. Neither: say what you meant.
   > **ANSWERED by D-0590:** the union ("All should unique ids should be equivalent betwen original data, and metadata"); this is the review session's and the agents' reading of "equivalent", one line to confirm with her.
   > **CONFIRMED by D-0591:** "the union" is now her word: "the unique ids in all datasets + metadata when exist should be the unions of all the unique ids".
3. **Item 2: a line of the metadata with no usable id.** Under the recipe-wide completion it cannot be given to any result table: it has no id to give. Only the metadata holds it, and it never matches. The options (a), (b), (c) of item 2 stand. Neither: say what you meant.
   > **ANSWERED by D-0594 (her answer to the review session's question; its reading is in the D-0593 to D-0595 sub-section):** option (a): the line stays in the metadata and is shown; the app does not remove, fix or convert it.
4. **The rest of the list, by title:** the marker's form and name; the block's form and tables; before or after the recipe's tier-1 steps; the log's directory; where the red warning shows; a dummy id; how "data first" is enforced; a recipe with no metadata block (question 13) and her view of D-0588; the count per target; the threshold; the two QA tables (D-0587, her "a)").

---

### Added 2026-11-23 (ledger D-0590): a third check of the id sets, in all cases; the completion with no metadata

**Her words, exact.** "If no metadata added - and I think that actually should be a 3d step done in all the cases (after having filed ids for tests 1 and 2) that the unique ids of each original data are compared to each other (and to the unique ids of metadata when existing) . Case 1 no metadata -> completions and reverification of test 3. Case 2. metadata existed - All should unique ids should be equivalent betwen original data, and metadata (if not I think we have a bug)." [HER WORDS D-0590]

**What her words say (she writes "I think").**
- A third step "in all the cases", after the ids are filled for her tests 1 and 2: the unique ids of each original table are compared with each other, and with the metadata's when there is one.
- No metadata: "completions and reverification of test 3".
- With a metadata: all unique ids "should be equivalent betwen original data, and metadata (if not I think we have a bug)".
- Readings, not her words:
  - the three checks are named by their content (the ids of a result file not in the metadata; the ids of the metadata not in a result file; the id sets compared);
  - a failed third check is a red warning and a line in the log, never a stop (D-0581).

**Points for her, by reading and reasoning.**
- **(a) Which tables take part when there is no metadata:** those that declare an entity id. A reference table with none stays out: the APEC list (`1_test_data_ST22_dummy.yaml:134`) declares none [RECIPE FILE `input_fields/APEC_STEC_virulence_genes_input_fields.yaml`].
  - Two tables whose ids name DIFFERENT kinds of entity would complete each other wrongly: each would gain the other's ids, marked.
  - How the recipe says that its tables describe one population: the optional `entity.population` names one table [CODE READ `libs/utils/src/utils/recipe_spec.yaml:29-30`], or every table that declares the entity id counts. Hers.
- **(b) What a line added from ANOTHER result table means:** the required meaning per table (D-0574, D-0586) covers "not in original data". With no metadata there is no "not in metadata" marker: there is nothing to add it to.
- **(c) "Unique ids"** are read after the declared strip and null words of the read [CODE READ `libs/ingestion/src/ingestion/declared.py:115-120`]: an id repeated within one table counts once; an empty id is no id only if the declared null words list it (a cell of spaces stays text when `null_values` is empty) [paragraph corrected by the Sonnet agent in the check].
- **(d) The order, once per data batch:** the metadata's own ids (a warning); the two completions; the third check.
- **(e) A failed third check:**
  - a line in the log, words PROVISIONAL: "check of the id sets failed: N ids differ between <tables>", and the red warning where there is a panel; with no panel only the person who reads the log sees it (D-0585);
  - it checks the app's own work ("I think we have a bug"), so when it is built it becomes a test: the expectation is written now and run when the code exists (D-0580).
- **(f)** The "equal id sets" line of the data check (D-0586 sub-section) is the report BEFORE the completion; the third check is the proof AFTER it.
- **(g)** With (A) the third check compares the completed tables as read, before any audit step, so an audit removal never makes it fail. With (B) a removal at one place can make it fail.
- **On the demo (case 2):** after the completion ResFinder holds 38 + 4 = 42 ids, and so does every other table that declares the entity id (nine data tables: `Summary`, `Quality_metrics`, `Detailed_summary`, `FastP`, `Quast`, `Bracken`, `ResFinder`, `MLST`, `VirulenceFinder`; `Summary_quality` is the same file as `Summary`) and the metadata, so the third check passes; the APEC list declares none and stays out [ESTABLISHED: OVERLAP section 1 counts; RECIPE FILE: `is_entity_key` in the nine `input_fields` files; REASONED for the state after the completion; corrected by the Sonnet agent in the check].

**What remains hers, one at a time.**
1. **(A) or (B):** the completion reads the files as read, or follows the places. With (A) the third check never fails after an audit step. Lean (Opus, as a lean): (A).
   Lean (Sonnet, as a lean): (A), as for the completion with a metadata (D-0589): the third check then never fails after an audit step, so a failure means a bug of the app and not a user's removal. Neither: say what you meant.
2. **The population when there is no metadata:** every table that declares an entity id, or the table named by `entity.population`. Lean (Opus, as a lean): the named population when the recipe gives one; with none named, every table that declares the entity id, and the warning says that they are treated as one population. 
   Lean (Sonnet, as a lean): the same as Opus. What she would see: on `figshare_integration` (no metadata block; three tables `fg_metadata`, `fg_phenotypes`, `fg_genotypes`, each with a `sample_id` [ESTABLISHED: OVERLAP, D-0569 dry-run list]) the three tables would complete each other once they declare their ids; on the demo nothing (it has a metadata). Neither: say what you meant.
3. **Item 2: a line of the metadata with no usable id.** It can be given to no table, and the third check ignores it (it has no id). The options (a), (b), (c) of item 2 stand. Neither: say what you meant.
   > **ANSWERED by D-0594 (her answer to the review session's question; its reading is in the D-0593 to D-0595 sub-section):** option (a): the line stays in the metadata and is shown; the app does not remove, fix or convert it.
4. **The rest, by title:** the marker's form and name; the block's form and tables; before or after the recipe's tier-1 steps; the log's directory; where the red warning shows; a dummy id; how "data first" is enforced; a recipe with no metadata block and her view of D-0588; the count per target; the threshold; the two QA tables.

---

### Added 2026-11-23 (ledger D-0591, D-0592): the union confirmed; the size of a mismatch; a simple log

**Her words, exact.** "yes . basically as the reviewer is writing now in his review the unique ids in all datasets + metadata when exist should be the unions of all the unique ids - if there many that do not match it means there is a problem in eg. a pipeline" [HER WORDS D-0591]. "yes it can be a log as simple as : the ids are written differently in the different output of a pipeline eg program1-ID1 program2-ID1 which means some cleaning here would need to be done ... before entering our system (eg. lab)" [HER WORDS D-0592]

**What her words say.**
- After the completion, the unique ids of every dataset, and of the metadata when it exists, are the union of all the unique ids. Many ids that do not match mean a problem upstream ("in eg. a pipeline").
- The log can be simple. Her example: ids written differently by two programs (`program1-ID1`, `program2-ID1`); the cleaning is done "before entering our system (eg. lab)".

**Readings, not her words (to confirm).**
- **No threshold for "many":** the log gives the numbers and the unmatched ids only; her "yes" answered the review session's option "no threshold, the numbers only".
- **Per table, the log lists** how many ids of how many do not match, and the ids themselves, side by side where it can, so that a pattern such as a program prefix is seen at once. The mechanism does not clean; it shows.
- **What it would show, words PROVISIONAL** [ESTABLISHED: OVERLAP section 1]: on the demo, "ResFinder: 4 of 42 ids of the metadata have no line: <ids>"; on `left_join_lesson`, "sequenced: 2 ids are not in the metadata: ACC0001, ACC0002".

**Where the documentation may point for the cleaning (by reading).**
- **What the tool does:** Test Lab's ID Reconciliation compares ONE key column of TWO files per run [RULE FILE `.claude/rules/rules_test_lab.md` section 5]. It finds exact matches, patterns (a prefix or suffix removed, a change of case, a part taken at a delimiter) and fuzzy matches, and writes the fix as a reusable YAML [CODE READ `libs/utils/src/utils/id_patterns.py:25, 103, 120`: `detect_patterns`, `apply_pattern`, `suggest_regex`].
- **What it does not do:** composite keys, three or more files at once, the join.
- **Where it exists:** it is wired in Test Lab [CODE READ `app/handlers/test_lab_handlers.py:135, 147`], which is gated by `test_lab_enabled`, set in the developer and qa profiles only [RULE FILE `rules_test_lab.md` section 7; `rules_app_features_flags.md`]. The documentation may point to it, but must not promise it in every deployment.
  > **CONFIRMED by D-0596:** "exacly cleaning tools live in LAB or other tools on the user side." Reading of the review session, which she confirmed in D-0596: HOME does not clean; the documentation says so, says to clean the data before it enters the app, and may point to the Test Lab where it is switched on.

**For the held documentation task (D-0583):** ids written differently by the programs of a pipeline are cleaned before the data enters the system (her example `program1-ID1`, `program2-ID1`); the log of the ids shows them, and Test Lab's ID Reconciliation can find the pattern (developer and qa profiles).

---

### Added 2026-11-23 (ledger D-0593 to D-0598): the app does no data cleaning (at least not HOME); it makes problems visible; the topic is closed

**Her words, exact.** "ha ,,, well ... again a data cleaning problem  ... user has responsibility of data cleaning correctly. Our app needs to make that visible though if possible" [HER WORDS D-0593]. "our app is not supposed to do data cleaning - it is not done for that ..." [HER WORDS D-0594]. "at least not HOME" [HER WORDS D-0595]. "exacly cleaning tools live in LAB or other tools on the user side." [HER WORDS D-0596]. "Completion 1. yes changes or removes nothing from the user's data. 2. HOME accepts tsv - conversion is done in Excel - handling of pipeline specific data eg "-" whether is missing or not recorded or unknown or other missing data depends on the recipe and the meaning of the results of the pipeline the data come from - we cannot plan for that - this is the recipe and user job. Space trimming can be usefull before and after , and when eg. columns splits ... but this is also in the recipe." [HER WORDS D-0597]. "we have now found a solution to report data that might be "dirty" and ensure that its visible in the ui (because of the log and markers). I think our job here should be complete no ?" [HER WORDS D-0598, in part]. "well it can ask the small ones, but we need to ensure that we have the big line in agreement first ...no ? we need the logic first" [HER WORDS D-0599]

**What her words say.**
- The user is responsible for cleaning the data; the app does no data cleaning, at least not in HOME, and makes the problems visible where it can; the cleaning tools live in the Test Lab or on the user's side [D-0593 to D-0596]. Reading of the review session, not her words: nothing is said about BLUEPRINT or the Gallery, so the principle is not extended to them.
- **The line to confirm is ANSWERED:** "Completion 1. yes changes or removes nothing from the user's data." [D-0597]. The completion changes or removes nothing of the user's data (her words, D-0597); the review session reads this as: it is not cleaning, and it stays as decided (D-0581, D-0589 to D-0591): on the demo ResFinder gains 4 lines marked "not in original data" (38 + 4 = 42 ids), named in the red warning and the log.
- HOME accepts TSV; the user converts in Excel, outside the app; what a symbol such as "-" means, and the trimming of spaces, are the recipe's and the user's job [D-0597]. (Her words do not speak of the Parquet files that Data Import also takes, `ui_implementation_contract.md:289`.)
- She asks whether the topic can be closed (her words, D-0598: "I think our job here should be complete no ?"); the agents' answer is in (d) below; the small questions are asked later, one at a time, once the big line is agreed (M659).

**The line of the metadata with no usable id: ANSWERED by D-0594.** The question she answered (the review session's words): "is my reading of question B right: the metadata line with no usable id stays, the app only shows it, the user decides". Read so (the review session): the app does not remove, fix or convert such a line; it shows it (the red warning, the log, the export); a removal is a visible step the user writes in the recipe, as `demo_abromics` does (`demo_abromics.yaml:44-47`). This is option (a), the lean of both agents. On the demo: none (42 distinct ids); in `demo_abromics`: a red warning that 3 lines of the metadata have no id (words PROVISIONAL), then its own step removes them (27 rows in its join) [ESTABLISHED: OVERLAP, the case of `demo_abromics`]. Marked where it stood open: the D-0581 section (point 3, row 2 of the updated list, next order 2) and the D-0588, D-0589 and D-0590 sub-sections.

**Where the text makes the app clean, convert or normalise data (the search of M653 and M654; reading only), with her answer.**

| Place | What it says | Status | Her words that bear on it, and the agents' reading |
|---|---|---|---|
| CAUSE:202, 213, 226, 339, 818; `ui_implementation_contract.md:288` | the read strips the text, turns the listed null words into missing, then reads the declared type; nothing is guessed [CODE READ `libs/ingestion/src/ingestion/declared.py:6-7, 115-120, 130-153`] | built; `strip` and `null_values` are required names of every data schema in the recipe, with no default [CODE READ `declared.py:36-44`; `recipe_spec.yaml:33`] | fits D-0597 ("this is the recipe and user job"): the recipe's own declaration |
| CAUSE:549, 567, 756-758 | option (b): the app removes a metadata line with no usable id | agents' option | falls (D-0594) |
| CAUSE:331, 535; OVERLAP:236 | "a red warning and an automatic handling, not a refusal" | the review session's reading of D-0581 | the handling is the recipe's ("automatic fixing in the recipes" [D-0581]); the app shows (D-0594) |
| CAUSE:365, 462, 550; OVERLAP:215-216 | a repeated id in the metadata: kept, dropped by the app, or nothing | open; not raised by her | not answered; by the principle the app does not remove it (reading); the rest after the big line |
| CAUSE:510-529, 765-787, 801-811 | the completion adds marked lines on both sides | DECIDED (D-0581, D-0585, D-0589 to D-0591); not built | not cleaning: "changes or removes nothing from the user's data" (D-0597) |
| CAUSE:231, 320, 491; OVERLAP:210, 225, 233 | a dummy fill for an unknown or false id | DECIDED (D-0573, D-0581): the user adds it to the metadata by hand | the user's action; fits |
| CAUSE:252, 353, 440, 502; OVERLAP:179-184, 213, 238 | `demo_abromics`'s 3 lines with no id: removed from the file in the dry run, or kept as a lesson that its own step removes | her order D-0569; a dry-run candidate (D-0525) | user side either way (the file, or a visible step); which one: hers, in the dry run |
| `ui_implementation_contract.md:280` | the user corrects errors in the metadata and uploads it | built | the user cleans; fits |
| `ui_implementation_contract.md:289, 300` | Data Import refuses a comma-separated or Excel file; converting it "is NOT decided and is not built" | built (the refusal) | fits: "HOME accepts tsv - conversion is done in Excel" (D-0597) |
| `ui_implementation_contract.md:304-329` | an Excel to TSV converter in HOME's Data Import, "a practical data preparation step" (:327, "Why here and not Test Lab"); it lists "TSV/CSV" as raw data (:313) | an older design, not in the ledger, "Deferred" (:329); `ExcelHandler` is a command-line script that no app code calls [CODE READ `libs/ingestion/src/ingestion/excel_handler.py:55, 89, 93`]; the Test Lab already converts [CODE READ `app/handlers/test_lab_handlers.py:880-902`] | against D-0597: a point for the rules file (listed, not edited) |
| CAUSE:162-164 | the audit removes a bad sample with a reason: "So audit can cover this case and justification holds." [D-0572] | DECIDED (D-0322) | the user's recorded step, not the app's (reading); unchanged |

**For the held documentation task (D-0583), early in the guidelines, in her words:** "user has responsibility of data cleaning correctly. Our app needs to make that visible though if possible" [D-0593]; "our app is not supposed to do data cleaning - it is not done for that ..." [D-0594]; "HOME accepts tsv - conversion is done in Excel", and the meaning of "-" "depends on the recipe and the meaning of the results of the pipeline the data come from" [D-0597]; "cleaning tools live in LAB or other tools on the user side." [D-0596]. The trimming is a recipe step or the declared `strip` (the review session's reading of D-0597).

**Closing of the topic (her order D-0598).**
- **(a) Decided:** check X and check Y, shown together as warnings, never a stop (D-0569, D-0570, D-0573, D-0579, D-0581); the completion, recipe-wide with or without a join, with the markers "not in original data" (not a zero) and "not in metadata" (D-0573, D-0584, D-0585, D-0589), which changes or removes nothing (D-0597); after it, every table that declares the entity id, and the metadata, hold the union of the ids (D-0590, D-0591); a required meaning for each marker on every result table (D-0574, D-0586); no blocking: a red warning with an "I have read this" button that does not block where there is a panel, "automatic, no user" where there is none (D-0581, D-0582); a separate, simple log, written automatically in a specific directory, in the session and in the export, read by a person in a static deployment (D-0575, D-0576, D-0581, D-0582, D-0585, D-0592); the third check in all cases (D-0590); recipes do not start from the metadata (D-0564, D-0586); the marker column is kept (D-0586); a line with no usable id is kept and shown (D-0594); a lone metadata table is registered as data, at least as a guideline (her view, D-0588); the app does no data cleaning in HOME, the cleaning tools are in the Test Lab or on the user's side (D-0593 to D-0596); HOME accepts TSV, converted by the user; the meaning of "-" and the trimming are the recipe's (D-0597).
- **(b) Needs her before a builder starts the completion** (the two answers give different tables, keys or records, which cannot be changed cheaply later):
  1. The completion reads the files as read (A), or follows the places (B): it sets the edges of the graph, the fingerprints of the stored tables, and whether an audit step can make the third check fail (D-0589, D-0590). Lean of both agents: (A).
  2. The population when there is no metadata: which tables complete each other and gain rows (D-0590). Lean of both agents: the table named by `entity.population`, else every table that declares the entity id, said in the warning.
  3. Where the record goes when the log's directory cannot be written: a static deployment could lose its only record (D-0581, D-0585). Proposal of the D-0581 section: the export and the console, and the red warning says that the log could not be written.
- **(c) After the big line** (M659): kept as a list and asked later, one at a time; meanwhile the agents' lean is taken, marked PROVISIONAL in the code, and shown in the dry run or at build time: the block's form and the names used inside it (lean: a block the app reads); its position (lean: before the recipe's own tier-1 steps, her "likely", D-0586); the marker's form and the words of the required meaning (lean: a yes/no column; a few known words); the log's directory and file name (lean: a sub-folder of `user_data`; `id_log.yaml`); the button's frequency (lean: once per data batch); where the red warning shows; a repeated id (lean: shown, not removed); a dummy id (lean: a note in the log); how "data first" is enforced (lean: an advice); the count per target; the threshold; the two QA tables (her "a)", D-0587); the converter of the rules file, against D-0597.
- **(d) "our job here should be complete no ?"** The two agents' answer to her question, not her decision: Yes, for this topic: the rules are decided in her words (list (a)), and every small question has a PROVISIONAL lean.
  Three answers, (b) 1 to 3, still change what a builder builds; they belong to the lineage, the recipe design and the deployment, so we propose to ask them in the big view, not as more questions on the ids.

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

Her rules this stays inside: every join is in tier 1 [CODE READ `recipe_check.py:715`, `action_names.py:66`]; at most one chosen place on a path [HER WORDS D-0553]; the default place is where the original and the metadata are joined [HER WORDS D-0549]; "we need to ensure that everystep after a change in a place is recalculated" [HER WORDS D-0560] [quote corrected 2026-11-23]. The chain: `qa_amr_genes_per_sample` reads `QA_AMR_per_sample` = metadata, left join ResFinder, select; tier 2 groups by the entity and counts the genes; the plot's own text: "A sample without any AMR gene must appear at 0, not disappear. T1 is long (74 rows), T2 has one row per sample (42)" and "Expect 42 samples: 4 with 0 genes, 70 genes in total". [RECIPE FILE]

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

Her words: "So the ids that are in metadata and not in the results data might require to be added to the results files.... a point to consider. then we would keep the 0 that means eg. no resitance gene was found." [HER WORDS D-0569] Tags: [HER WORDS] / [RECIPE FILE] / [CODE READ] / [REASONED, not run]. Checked by the Opus agent afterwards (OPUS_checks_b3_v1.md and OPUS_signs_b3_v2.md).

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
**What the form can and cannot do.** A derived table reads ONE table and holds no join step: the join with the metadata is written before it, as a join of source tables. [ESTABLISHED: RECIPE_PROPOSAL_answers (removed 2026-11-24 in the cleaning of the studies; see git history), answer 2; her words D-0511 "derived tables should already have the metadata joined"] A derived table moves the aggregation out of the join's tier 2; the table it reads is still the join of the metadata with the data, which must keep the metadata as the retained side to show zeros. Alone, (d) does not remove the pattern. A derived table that reads the data table and the metadata separately would be a join of two tables in a new place: that reopens "a join takes only source tables" [HER WORDS D-0344: "Yes, revisit if needed"] and the rule that every join is in tier 1.
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

> **Correction of 2026-11-23 (records error, Sonnet agent):** the words "all replacements applied" (the first signed line) and "R1 to R26 applied" (the D-0572 additions) were not true. Found by the Opus review (flag 5 of `OPUS_review_1.md`) and by an independent search of every replacement. **Applied late, on 2026-11-23** (each marked "[applied late 2026-11-23, ...]" where it stands): R2, R4, R5, R6, R7, R8, R9, R10, R11, R13 and R14 of `OPUS_checks_b6_v1.md`; O7 of `OPUS_checks_overlap_v1.md` (the two wrong sentences, in the half page and in the question, replaced by the agreed one; the earlier wording is kept in the note beneath each); R2 ("read now") (R2 of the cause round in a variant wording, line 32: 'The stored tables of the earlier run, read now, ...') and R14 (the tag form) of `OPUS_checks_cause_v1.md`. **Found already covered by a later text, left as it was:** R1 of the same file (the half page, "Is the unchanged plot right?" ends with the VirulenceFinder case); the second place of R3 (the list "What she may be missing", item 1, carries "within her rules"); O4 (the entry (a2) of the catalogue and `OVERLAP_AND_POPULATION.md`, the (a2) bullet); Q2 (c) of `OPUS_checks_b3_v1.md` (points (i) and (v) of the B3 entry); P3 (the sentence under "The rule behind all candidates" has its correction beneath). The round D-0570 (R1 to R32) was found fully present.

**D-0573 to D-0579 additions and the review:** Sonnet (this file) and Opus (`OPUS_checks_review_v1.md`, S1 to S18 applied).

**D-0581 and D-0582 additions:** Sonnet (this file) and Opus (`OPUS_checks_noblock_v1.md`, R1 to R20 applied).

**D-0584 and D-0585 additions:** Sonnet (this file) and Opus (OPUS_item1_final.md).

**D-0586 additions:** Opus (OPUS_m645_final.md) and Sonnet (checked and pasted).

**D-0587 additions:** Opus (OPUS_m647_final.md) and Sonnet (checked and pasted).

Note on D-0587: the Sonnet check changed two places of the Opus text: the bullet that read her "a)" as an answer (block 1) and the note under the lean (block 4); her "a)" has two readings (an answer, option (a); or her own point on the edge case), and the options (a) to (c) for the two tables stay open until she confirms.

**D-0588 additions:** Opus (OPUS_m648_final.md) and Sonnet (checked and pasted).

**D-0589 additions:** Opus (OPUS_m649_final.md) and Sonnet (checked and pasted).

**D-0590 additions:** Opus (OPUS_m650_final.md) and Sonnet (checked and pasted).

**D-0591 and D-0592 additions:** Opus (OPUS_m651_final.md) and Sonnet (checked and pasted).

**D-0593 to D-0599 additions and the closing of the ids topic:** Opus (OPUS_m653_final.md) and Sonnet (checked and pasted).
