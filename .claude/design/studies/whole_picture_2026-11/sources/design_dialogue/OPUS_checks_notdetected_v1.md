# Opus check of SONNET_notdetected_3.md, Part B (the draft for the two study files), case D-0570 (2026-11-23)

**What this is.** My decision on the naming counter (O6), then the check of Part B against its sources: every fact against the file it cites, her words against the channel block "### M624 from sparmvet-viz-cb", the demo numbers, every "what you would see" line, that no option is chosen for her, that cost or effort is no argument, that it is data agnostic. Reading only, NO RUN. No study file is edited. Line numbers "draft N" are lines of `SONNET_notdetected_3.md`; "CAUSE N" and "OVERLAP N" are lines of the committed study files.

**Checked and right as drafted** (no replacement): her words at draft 41 match the channel block exactly, both quotes, character for character (a fixed-string search of each quote in the block); the 38 / 4, 37 / 5 and 41 numbers [ESTABLISHED: OVERLAP section 1; PATHS G8]; fact 1; fact 3's quote "Today an audit step is written at T3 of the plot" [RULE FILE `ui_implementation_contract.md` section 2]; fact 8's code places (`polars_calls.py:60, 85`; `recipe_check.py:714-715, 866-867`; `orchestrator.py:269-294`); the her-words quotes of D-0549 ("some users will have metadata for more samples") and D-0570 ("the metadata itself should have id with non empty lines"), each a substring of the ledger's evidence; the lines B3, B4, B5, C2, D (draft 65 to 69) for their numbers; B2's case of `demo_abromics` (the drop step at `demo_abromics.yaml:45-47`, its metadata tier 1 empty at `:30-31`, 27 rows [RECIPE FILE `demo_abromics.yaml:37`]); no cost or effort argument anywhere; the leans marked as leans.

---

## O6. The naming: ACCEPT its counter

Keep **C** in Part 1 (the old C, with its variants (c), (f3) and (f5) inside it, extended by the labels from the audit record), and call Part 2 **F** and **G**. Reason: she has read "C" in the question (CAUSE 60: "C. The app, not the user, knows that the result is per entity (f5) ..."); keeping the letter avoids a gap or a renaming in what she has seen, and "C1" in another part would read as an earlier version of "C2". One observation, not a block: the option letters are not the catalogue's lowercase letters (option A is catalogue (b), option B is catalogue (a)), so "F" may be read as catalogue "(f)"; replacement R1 adds one sentence that says so.

---

## The replacements (numbered; old text → new text)

**R1. The naming, everywhere in Part B** (mechanical).
- draft 68: "- **C2. The app labels three classes" → "- **C. The app labels three classes"; "with the declaration of C1 below" → "with the declaration of G below"; "Variants kept inside C2:" → "Variants kept inside C:".
- draft 76: "- **C1 (new). F plus the meaning" → "- **G (new). F plus the meaning".
- draft 82: "F or C1 with every form" → "F or G with every form".
- draft 86, 111: "C2" → "C"; "C1" → "G" (draft 86 is replaced whole by R20).
- After draft 58 ("### The question, in two parts (one list, one naming)"), insert one sentence: "(The option letters are not the letters of the catalogue below: option A is catalogue (b), option B catalogue (a), and F is not catalogue (f).)"

**R2. draft 43** (the correction must not say "a row"; my own round-2 sentence had the same fault).
Old: "the metadata never adds a row. An entity with no row in the data table is absent."
New: "the metadata never adds an entity. An entity with no row in the first table is absent."
Why: a left join with the metadata second can multiply rows when the metadata repeats an id (the demo's metadata does not: 42 rows, 42 distinct ids [ESTABLISHED: OVERLAP 42]); and in B2 the first table is the table of the analysed entities, not the counted data table.

**R3. draft 45.**
Old: "(how many entities are not detected: on the demo, 4 of 42 for ResFinder)"
New: "(how many entities are not detected; on the demo, 4 of the 42 entities have no ResFinder line, and the files do not say whether they were analysed)"
Why: facts 1 and 5 of the same draft say the app cannot tell; the 4 are "not detected" only in her route (ii).

**R4. draft 50** (fact 2: ResFinder has no accession column; scope it so it is data agnostic).
Old: "At the ResFinder table every column describes a detection (gene, phenotype, identity, overlap, accession). A filter on values there ("
New: "At a result table whose columns, the entity id aside, all describe a detection (on the demo ResFinder: `gene`, `predicted_phenotype`, `identity`, `overlap`), a filter on values ("
Old: "A removal by key (a list of entities) is the only step"
New: "There, a removal by key (a list of entities) is the only step"
Old: "[RECIPE FILE `input_fields/ResFinder_input_fields.yaml`;"
New: "[RECIPE FILE `input_fields/ResFinder_input_fields.yaml` lines 1, 6, 10, 14, 18: `sample_id`, `gene`, `predicted_phenotype`, `identity`, `overlap`;"

**R5. draft 51** (fact 3, last sentence: what "it" is was unclear).
Old: "It does not hold for a table with no entity id (for example `QA_aggregated_no_key`: a removal by key cannot reach it)."
New: "A removal by key at a plot's own table needs the entity id there: for a plot whose table has none (for example `QA_aggregated_no_key`) it cannot be written at that table [ESTABLISHED: RECIPES G8]."

**R6. draft 52** (fact 4: the same precision as R3).
Old: "On the demo: 38 detected, 4 not detected (42 samples; the bar at 0 holds 4). Remove one detected entity at the ResFinder table: 37 / 5, the new "not detected" never having been shown not detected."
New: "On the demo: 38 samples with a ResFinder line, 4 without (42 samples; the bar at 0 holds 4; in your route (ii) the 4 count as not detected). Write a removal of one detected entity at the ResFinder table: 37 / 5; the removed entity now counts like the 4."
Old: "[ESTABLISHED: PATHS G8; the counts from the files]"
New: "[ESTABLISHED: PATHS G8 (the entity keeps one row, count 0); the counts from the files]"

**R7. draft 53** (fact 5: "no way" is too strong).
Old: "The metadata has no way to say "never analysed"."
New: "Today's metadata says nothing about which analysis ran on which entity (its fields: `sample_id`, `source`, `year`, `country` [RECIPE FILE `input_fields/metadata_schema_input_fields.yaml` lines 1, 7, 11, 15])."

**R8. draft 54** (fact 6: the grouping is Polars semantics; where the drop step stands matters for the third note).
Old: "and the grouping makes one group of the missing ids."
New: "and a grouping by the id makes one group of all the missing ids (Polars semantics, not run)."
Old: "removed by a visible step of the recipe before its join (`demo_abromics.yaml:44-47`)."
New: "removed by the first step of its join's tier 1, before the join step itself; the metadata's own tier 1 is empty, so the table `metadata_schema` still holds them (`demo_abromics.yaml:30-31, 44-47`)."

**R9. draft 55** (fact 7: the context of the 0 and the 1).
Old: "**The aggregate decides 0 or missing.** A count of non-empty values gives 0 (the demo's `QA_AMR_per_sample`). A count of rows (`pl.len()`) gives 1 (the demo's ResFinder tier 2 counts rows)."
New: "**The aggregate decides 0 or missing.** After a left join from the metadata, an entity with no line has one row with empty result columns. A count of non-empty values gives 0 (the demo's `QA_AMR_per_sample`). A count of rows (`pl.len()`) gives 1 (the demo's ResFinder tier 2 counts rows: under B3 an empty-result line would count 1)."
Why: today ResFinder's tier 2 never meets an entity with no line (the entity is absent from the ResFinder table).

**R10. draft 56** (fact 8: two quotes are not her words; the test is not run here).
Old: "the engine builds it (the existing test writes an anti-join, `test_self_join_build.py:34-35`)"
New: "an existing engine test builds one [CODE READ `libs/transformer/tests/test_self_join_build.py:34-43`; not run for this file]"
Old: "would reopen "the join with the metadata must be done at T1" [HER WORDS D-0510]."
New: "would reopen "join with metadata must be done at T1" [HER WORDS D-0510]."
Old: "The audit cannot YET follow an anti-join, and a place it cannot trace is red and not tickable "for now" [HER WORDS D-0460];"
New: "The audit cannot YET follow an anti-join [HER WORDS D-0452: "App cannot YET describe (or follow? )"], and a place it cannot trace is red and not tickable (D-0460; her answer: "B of needed we try to.fimd a.solutiom later");"
Old: "a removal at the ResFinder table ADDS the entity to the list."
New: "a removal at the ResFinder table ADDS the entity to the list. [REASONED]"
Why: her words in D-0510 are "so the join with any metadata must be done at T1" and "join with metadata must be done at T1"; "for now" is the ledger's title of D-0460, not her words.

**R11. draft 60** (the place of the step: a count table made from the same file is not below the ResFinder table).
Old: "before and after you write a step at the ResFinder table for one detected entity (38 / 4, then 37 / 5, or 41 at the join place);"
New: "before and after you write a step for one detected entity at the result table the per-entity join reads (ResFinder, or its count table in the forms that count first) (38 / 4, then 37 / 5, or 41 at the join place); a step at the ResFinder table does not reach a count table made from the same file [ESTABLISHED: RECIPES G6];"
Why: the fragments of B, B2, B4 and E read a count table (`ResFinder_per_entity`), not the ResFinder table.

**R12. draft 62** (A: inform, do not instruct; and the recipe does not say it today).
Old: "Do not fill the gene column itself with a word: a count of genes would count the word."
New: "A word filled into the gene column itself would be counted as a gene by a count of genes (`demo_abromics.yaml:55-57` fills a category column with "Non Determined", which is right for a category)."
Old: "Asks of the files: nothing (the recipe says the file lists findings only)."
New: "Asks of the files: nothing. What a blank means is the author's statement in the recipe; today ResFinder's description reads "AMR gene detection (Gene detection)" and does not say that the file lists findings only [RECIPE FILE `1_test_data_ST22_dummy.yaml:100`]."

**R13. draft 63** (B: the step at the ResFinder table does not reach B's count table).
Old: "As A, with no multiplication of rows. Same numbers, same false result."
New: "As A, with no multiplication of rows: 38 / 4. A step at the count table's own place: 37 / 5 (false). A step at the ResFinder table does not reach the count table [ESTABLISHED: RECIPES G6]."

**R14. draft 65** (B3: a detected entity has no empty-result line).
Old: "After the step at the ResFinder table the entity's lines (the empty one too) are removed:"
New: "After the step at the ResFinder table the entity's lines are removed (for an entity with nothing found, its empty-result line too):"

**R15. draft 71** (E2: how she would see it today).
Old: "You see a table of 4 rows."
New: "The table has 4 rows; today you see it through the data preview of a plot that reads it (a table as a result is decided, D-0485, and not built)."

**R16. draft 75** (F: which step, and the join place).
Old: "After a step: "with a line 37; without 5, of which 1 removed by an audit step"."
New: "After a step at the ResFinder table: "with a line 37; without 5, of which 1 removed by an audit step". After a step at the join place the line must still match the result you see (41 entities); its words are not decided."

**R17. draft 79** (Common: the source of "both directions"; and the reopens line that the question of the study file has for every option).
Old: "The data check's notes (both directions, decided, not built) go with every form."
New: "The data check's notes (both directions; decided, D-0570; not built) go with every form."
Insert after draft 79:
"**Reopens (information).** A, B, B4 and B5 start from the metadata, E keeps its rows and C completes from it: your direction "the join should not start with the medata or we need a solution we do not have yet" [HER WORDS D-0564]; you name the metadata on the left yourself as one route [HER WORDS D-0570]. E and E2 use kinds the audit cannot YET follow [HER WORDS D-0452] and "The documentation should NOT recommend those joins" [HER WORDS D-0486]. A later anti-join with the metadata would reopen "join with metadata must be done at T1" [HER WORDS D-0510]. C adds a new edge in the graph (a completion that reads the population after the join; catalogue (c))."

**R18. draft 83** (my lean: the exact sentence to paste, with the naming of R1).
Old: "- Lean of the Opus agent: B5 where the pipeline can write it, with an explicit column written by the pipeline; where the files cannot change, A (or B4 where a manifest exists) with C1; F or C1 with every form; no lean for E2. [as the Opus agent states them; to be copied from its file]"
New: "- Lean of the Opus agent, as a lean: B5 where the pipeline that makes a result file can write a line for every entity it analysed, with an explicit column that says so; where the files cannot change, A (or B4 where a manifest of the analysis exists) together with G and the default place at the join; F or G with every form; no lean for E2. Reason: B5 is the only form in which the recipe's own table, with the initial population, shows "no result" instead of a false "not detected" after a step at the result table's own place (C does it in a table the app completes, on the promise that every entity was analysed); F and G let the app itself say how many entities have no line, how many of them your own steps removed, and (G) what a missing line means, and you said "information is very important here" [HER WORDS D-0570]; E2 splits the population into two tables, the audit cannot YET follow it, and a step at the result table adds the entity to it."

**R19. draft 82** (the Sonnet agent's lean): only the renaming of R1; nothing else.

**R20. draft 86** (open question 1: G does not separate; B and D were missing).
Old: "(A, C2, E and E2 count it; B2, B4, B3, B5 and C1 separate it.)"
New: "(A, B, C, E and E2 count it; B2, B3, B4, B5 and D leave it out or name it; F and G say how many entities have no line, not which of them were analysed.)"
Why: G declares one meaning for every missing line of a table; it cannot separate one never-analysed entity from the others.

**R21. draft 88** (open question 3: the reading changes C's result).
Old: "It adds no step; it reads."
New: "It adds no step; it reads. In C the result table then depends on that record, so the export must carry the rule."

**R22. draft 90** (open question 5: data agnostic).
Old: "("how many samples carry no gene X")"
New: "("how many entities carry no target X", on the demo: no gene X)"

**R23. draft 92** (open question 7).
Old: "Do you want it as the answer, or the number only?"
New: "Do you want the number, the list, or both?"

**R24. draft 96** (the line-59 replacement must take the whole sentence, or the rest of it dangles after "there is no 0.").
Old: "replace "Then the data first and the metadata second keeps the zeros" with "Then the result file itself has a line for every analysed entity, so a join with the result table first and the metadata second (`left`) keeps those entities and their counted 0: the rows come from the result file, not from the metadata. With today's result files, which list findings only, the result table first and the metadata second keep only the entities that have a line: an entity with nothing found is absent and there is no 0.""
New: "replace "Then the data first and the metadata second keeps the zeros, a removal at the data table's own place removes the entity completely (no false zero), and no join starts from the metadata." with "Then the result file itself has a line for every analysed entity, so a join with the result table first and the metadata second (`left`) keeps those entities and their counted 0: the rows come from the result file, not from the metadata. A removal at the data table's own place then removes the entity completely (no false zero), and no join starts from the metadata. With today's result files, which list findings only, the result table first and the metadata second keep only the entities that have a line: an entity with nothing found is absent, and there is no 0.""

**R25. draft 96** (the clause at CAUSE 58, written as an exact replacement).
Old: "Add one clause at line 58 (B2): "the zeros come from the first table, which lists the analysed entities"."
New: "At line 58 (B2) replace "the counts next, the metadata second (a2). It follows" with "the counts next, the metadata second (a2); the zeros come from the first table, which lists the analysed entities. It follows"."

**R26. draft 97** ("42 bars": its list of lines is right and wider than mine (181 and 202 added); CAUSE 47 also has "38 bars"). Replace the bullet's text with these exact replacements:
- a. CAUSE 47: "in A, B, C and E the plot keeps 42 bars, with 0 for an entity removed at the data table; in D it has 38 bars and no zeros." → "in A, B, C and E the plot keeps counting 42 samples, an entity removed at the data table in the bar at 0; in D it counts 38 samples and has no bar at 0."
- b. CAUSE 53: "the plot of the demo shows the same 42 bars, because" → "the plot of the demo counts the same 42 samples, because"
- c. CAUSE 59: "you would see the same 42 bars with 4 at 0;" → "you would see the same 42 samples counted, 4 of them in the bar at 0;"
- d. CAUSE 59: "a removal of one entity at ResFinder would give 41 bars." → "a removal of one entity at ResFinder would leave 41 samples counted."
- e. CAUSE 62: "so you would see the same as A: 42 bars, and 0 for an entity removed at the data table." → "so you would see the same as A: 42 samples counted, an entity removed at the data table in the bar at 0."
- f. CAUSE 181: "**User sees:** one bar per entity, 42 bars; after a removal at the data table the entity's bar shows 0, like the 4 entities that have no row in the file." → "**User sees:** 42 entities counted by their number of genes, 4 of them in the bar at 0; after a removal at the data table the entity is counted in the bar at 0, like the 4 entities that have no row in the file."
- g. CAUSE 202: "on the demo the same 42 bars as today," → "on the demo the same 42 samples counted as today,"
- h. CAUSE 220: "2. Expected: 42 bars with 4 at 0; a removal at `T1:ResFinder` gives 41;" → "2. Expected: 42 samples counted, 4 in the bar at 0; a removal at `T1:ResFinder` leaves 41;"
- i. CAUSE 291: "User sees: 38 bars, a caption" → "User sees: 38 samples counted, no bar at 0, a caption"
- j. OVERLAP 31: "On the demo you would see the same 42 bars as today," → "On the demo you would see the same 42 samples counted as today,"
Source: the plot counts samples by their number of genes (`x: n_amr_genes`, `geom_bar`) [RECIPE FILE `plots/qa_amr_genes_per_sample.yaml`].

**R27. draft 98** (CAUSE 283, as an exact replacement, so that the line's next sentence, which already says what the old code follows, is not repeated).
Old: the bullet's text.
New: "At line 283 replace "the form of the action lists `right` and `full` [CODE READ `polars_calls.py:85`], and the engine accepts `anti` and `cross` as well. [CODE READ `libs/utils/src/utils/step_effects.py:71-73`]" with "the form of the action lists all seven kinds: `inner`, `left`, `right`, `full`, `semi`, `anti` and `cross` [CODE READ `polars_calls.py:85`]; the old reading code names `anti`, `right`, `full` and `cross` as not YET followed [CODE READ `libs/utils/src/utils/step_effects.py:73`].""

**R28. draft 99-100** (no study-file line says either thing; its own search found none).
Old: the two bullets "A table as a result" and "Question 27".
New: one sentence after the list: "Two corrections concern the two agents' own scratch positions, not these files, and need no edit here: a table as a result is a decided design, not built (D-0485, D-0487); a later anti-join with the metadata meets D-0510, not question 27."

**R29. draft 108** (her own texts use "...", so an inserted ellipsis would read as hers).
Old: ""I think the data check information as suggested. ... 4. yes the validated question - yes . information is very important here.""
New: ""I think the data check information as suggested." and "4. yes the validated question - yes . information is very important here.""

**R30. draft 111** (G is not decided).
Old: "or declare in the recipe what a missing line means (C1)."
New: "or, if you choose G, declare in the recipe what a missing line means (G)."

**R31. draft 114** (the grouping makes ONE group of all missing ids; the list has one row per line).
Old: "a line with no id never matches, so a left join from the metadata keeps it as an entity with no result, and an anti-join lists it; the count of "not detected" grows by one for each such line."
New: "a line with no id never matches, so an anti-join lists each such line, and a left join from the metadata keeps them, where a grouping by the id makes one entity of all the missing ids (Polars semantics, not run): the count of "not detected" grows by one per line in the list of E2, and by one in all in the per-entity count of A."

**R32. draft 115** (the file's lines; the source of "read as missing"; the limit of the match; her order of D-0569).
Old: "Its metadata file has 30 lines; 3 have no usable id (line 5 empty, line 6 `-`, line 11 `""`). They are there on purpose: the id field reads `""` and `-` as missing,"
New: "Its metadata file has 30 data lines under its header; 3 have no usable id (file lines 5, 6 and 11: empty, `-`, `""`) [DATA FILE READ]. They are there on purpose: the id field reads `""` and `-` as missing [RECIPE FILE `demo_abromics.yaml:23`; `input_fields/metadata_schema_input_fields.yaml:4`],"
Old: "(a match on plain text of the step)."
New: "(a match on plain text of the step); a removal written another way (for example a `modif_filter` on the id) is not recognised, and the note then gives the general sentence."
Old: "Whether `demo_abromics` keeps its three lines is hers (dry-run candidate, ledger D-0569)."
New: "Her order of D-0569 reads "remove the null and empty rows from the metadata"; that these three lines are a deliberate lesson was put to her after it (channel block M624): her choice, a dry-run candidate (D-0525)."

---

## Its Part A

Read; no replacement needed for the files (Part A is not pasted). Its answers to O1 to O5 and to my disagreements agree with my round-2 evidence.

## Closing

I sign the draft with these replacements applied.
