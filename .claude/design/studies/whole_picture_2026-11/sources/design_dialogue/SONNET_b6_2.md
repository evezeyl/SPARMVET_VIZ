# SONNET round 2 on B6: answers to `OPUS_b6_1.md`, then the FULL DRAFT for the two study files (ledger D-0572)

Reading only, no run (D-0566). No study file is edited; `WHOLE_PICTURE.md` untouched; no waiting loop. Tags: [HER WORDS M627] / [CODE READ file:line] / [RECIPE FILE] / [RULE FILE] / [ESTABLISHED: file, point] / [POLARS SEMANTICS] / [REASONED, not run].

---

# PART A. Answers, point by point

**A1. Flag 1: the 4 added lines are stamped "Detected" and the stamp reaches `ST22_Anchor` and `integration_plot`.** AGREE; MISSING in mine (I stopped at ResFinder). Checked: `ResFinder_wrangling_tier1.yaml` stamps every line `status: pl.lit('Detected')`; `ST22_Anchor_wrangling_tier1.yaml:47` keeps `status` in its published columns; `plots/integration_plot.yaml:9` fills its tiles by `status` [RECIPE FILE]. Today the 4 entities have an empty `status` there; with B6 they show "Detected", with no error.

**A2. Flag 2: tier 2 counts rows.** AGREE (same as mine): `total_gene_count: pl.len().over(['sample_id'])` [RECIPE FILE `ResFinder_wrangling_tier2.yaml`].

**A3. Flag 3: a threshold filter in tier 1 and a completion before tier 1 disagree.** AGREE, and the demo has the case, which neither position had. `Detailed_summary_wrangling.yaml:20, 25, 30` holds three `modif_filter` steps (its thresholds); its file holds all 42 ids and its tier-1 table 36 [ESTABLISHED: RECIPES G12; RECIPE FILE]. With the completion BEFORE tier 1 (P1) the file already has 42 ids, nothing is added, and the filters then remove all the lines of 6 entities: they are absent. With the completion AFTER the author's tier-1 steps (P2) those 6 entities would each get a marked line. So P1 and P2 give different tables on the demo's own `Detailed_summary`. This makes Opus's P1/P2 question concrete and hers (draft question 5).

**A4. Flag 4 and α against β (the metadata as read from its file, or after its tier 1; D-0553).** AGREE; the same reading as mine. With β the completed table's first place lies below the metadata's place, so choosing both is two places on one path [HER WORDS D-0553]. With α the edge comes from the metadata's file and the places stay as they are.

**A5. The three outcomes after a removal at the ResFinder table.** AGREE with all three; the middle one is MISSING in mine. Data first: 41 samples, 4 in the bar at 0. Metadata first with the marker published and read: 37 detected / 4 "no result in file" / 1 "no line": after a left join from the metadata, an entity with no line in ResFinder has an EMPTY marker (not true, not false), so three states exist [POLARS SEMANTICS; REASONED]. Metadata first counting genes only: 42 samples, 5 in the bar at 0: false. Note kept from it: `QA_AMR_per_sample`'s tier-1 `polars_select` drops the marker unless the author adds it [RECIPE FILE `QA_AMR_per_sample_tier1.yaml`: `exprs: [sample_id, country, source, year, gene, predicted_phenotype]`].

**A6. "B6 alone does not force the recipe maker."** AGREE; it corrects my section 1, where I wrote that B6 "forces" the maker. Naive steps (a stamp `pl.lit`, a row count `pl.len`) read an added line as a line with no error (A1, A2). The force must be a written statement. Its proposal, a REQUIRED `meaning` on the completion, follows a pattern the project already has: parameters "whose absence would hide a choice that changes the result" are required [CODE READ `polars_calls.py:54-60`, `REQUIRED`]. I take it as an option for her (draft question 3).

**A7. The variants of placement (i): (i-a) written per table; (i-b) automatic for every table that declares an entity id, with a key for the meaning; (i-c) automatic with no key.** AGREE; mine had "per table" and "once for the recipe" only. Its objection to (i-c) holds: with no key the recipe says nothing, so the result depends on app behaviour that the export must record, against "nothing changes a result silently". I move to (i-b) in my lean.

**A8. Position P1 (before the author's tier-1 steps) against P2 (after them, before the audit steps).** AGREE; MISSING in mine. A third place is wrong in both: after the audit steps the completion would add back an entity the user removed at that table [CODE READ `data_wrangler.py:92`: `return steps + audit_list`]. P1 is her wording ("the data file has no result") and lets the recipe's own steps process the marked lines ("processed as a normal recipe" [HER WORDS M627]), at the price of flag 1. P2 hides the added lines from the author's tier-1 steps (no stamp, no count) but then a tier-1 step cannot say how to process them; and its marker means "no line left after the rules", not "the file has no line". Hers (draft question 5).

**A9. (ii) as a joined table works, but J04 stops any other join from reading it.** AGREE; the same evidence as mine (`recipe_check.py:866-867`, an ingredient must be a schema); a new action in a schema's tier 1 needs an ingredient the engine does not give it (`orchestrator.py:282-295`: tier 1 runs on the table alone).

**A10. (d) an id repeated in the metadata.** AGREE; MISSING in mine. The completion adds one line per distinct id; a join with the metadata second multiplies the rows of a repeated id; a note covers it. The demo's metadata has 42 rows and 42 distinct ids [ESTABLISHED: OVERLAP section 1].

**A11. The keys (`cache_keys.py:14-20`).** AGREE; same as my reading of `table_key_parts` (`:248-276`). The key line `T1 key = E . rC . dC . [a1]` has `dC` "the content of the data files THIS table reads (the source tables of the graph)": with the completion the metadata's file must enter ResFinder's `dC` and the completion's definition its `rC`. A change of the metadata then changes ResFinder's key and everything below (D-0560).

**A12. Engine-order lines: whose are right?** Both. Mine (`orchestrator.py:246-249`; `data_wrangler.py:31-35`) are the doc text of `_read_source` and of `tier_steps`; its (`orchestrator.py:264-267, 282-295`; `data_wrangler.py:92`) are the code: `_read_source` returns the table as read (264-267), `ingredient_parts` reads it then picks the tier-1 steps (282-295), and `tier_steps` ends with `return steps + audit_list` (92). Its lines are the exact ones and I will cite them. One DISAGREEMENT with my own text: I put the completion inside `_read_source`, so that the Source view showed the completed table. Its place, in `ingredient_parts` after `_read_source`, is better: the Source view then stays "a source table as read from the file" [RULE FILE `ui_implementation_contract.md` section 2; `read_source` doc, `orchestrator.py:297-300`], and the plan of every place reads the same lists as the build (`orchestrator.py:287-291`), so the plan sees the added lines. I take its place: Source shows the 70 lines of the file; T1 shows 74.

**A13. The eight questions: which are settled (resolve by her exact words).** The two readings differ on Q1, Q4, Q6, Q7 and Q8. By her words:
- **Q1 settled** (both): "missing data in the original files need to be processed correctly according to the correct meaning - which only a recipe maker (in collaboration with a real user) can decide" [HER WORDS M627].
- **Q4 partly** (Opus): "saying how those need to be processed in the recipe" settles that the recipe says it; whether a required statement or only the steps say it remains. I withdraw my "settled".
- **Q6 not settled by her exact words** (mine retracted; Opus said open): her answer "3. yes but not so usefull for our case .. because we do not have ids with no values" does not name a threshold; that it is about a filter on values is the review session's reading. Keep open, low priority.
- **Q8 settled in direction** (both): "5. true that is why metadata should be clean - all with an id" and her order of D-0569; confirm in the dry run.
- **Q2 partly** (both): "short and explicit", "different kind of other missing value"; the name remains. **Q3, Q5 open** (both). **Q7 partly** (Opus): B6 gives the number and the list from one table ("That would remove need for 6 anti join"); how the list is shown remains.

**A14. Its leans (section 10).** Its lean is mine except for the placement of the key (it says i-b, mine said per table, now i-b) and P1 (I agree). Both stay as separate sentences in the draft.

**MISSING in its file, from mine** (to carry into the merge):
- The marker forms m1 to m4 are the same as my M1 to M4; mine adds that a cell of only spaces is not missing (`declared.py:115-120`).
- Mine names one more thing in the table of ways: (iv) the audit copy: both say it does not fit; same evidence.
- My point that the data first AND the metadata second only keeps the zeros because the FIRST table is complete: the same as its "key property" (section 1).

---

# PART B. THE DRAFT TEXT (ready to paste, after the Opus check)

## B1. For `CAUSE_AND_SOLUTIONS_ZEROS.md`: a new section after the D-0570 section

---

## Added 2026-11-23 (ledger D-0572): her solution B6 and the control of the ids

**Her words, exact** (channel block M627). Her answers to the facts: "2. Yes true but if the sample is bad then no detection can exist because sample is bad in this case it is still good to remove from the analysis and have it rerun in another batch to be analyzed later. So audit can cover this case and justification holds. 3. yes but not so usefull for our case .. because we do not have ids with no values ... 4. this is true that is why the ids of both metadata and data sets should overlapp (or at least all in metadata and included for data sets) 5. true that is why metadata should be clean - all with an id ... 6. I think the solution would be to fill the data tables with the id contained in the metadata and have a "data file has no result" NA ? that can be then processed as a normal recipe - saying how those need to be processed in the recipe. Its a bit weird solution but it would work in all cases forcing the recipe maker to consider this case. and then missing data in the original files need to be processed correctly according to the correct meaning - which only a recipe maker (in collaboration with a real user) can decide. That would remove need for 6 anti join. and make decisions on how to procede with those clearn in the recipe so 7. All is clear and decided." Her answers to the needs: "1. yes we need a control of ids - as we started to implement - warnings in case something was wrong in the metadata so the user can recheck (as was planned recently) - if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done, if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) that would - that would be clear and mentionned both in literature and allerts. for the missing ids - but this might be before T1 a step the app does ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe) 2. we could need good marker convention - short and explicit - and I think it should be a different kind of other "missing value" because then the recipe maker has to consider those cases specifically and the 3. it knows the risk it accepts". [HER WORDS M627]

**What is settled, and what is her PROPOSAL.** Settled by her words: a removal because a sample is bad is right, the audit covers it and its justification holds; the ids of the metadata and of the data sets should overlap, or at least all be in the metadata and included in the data sets; the metadata should be clean (an id on every line); the meaning of a missing value is for the recipe maker with a real user; the app accepts the risk. **B6 is HER PROPOSAL, not chosen**: fill the data tables with the ids of the metadata, with a marker "data file has no result".

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

### The risk you accept

"it knows the risk it accepts" [HER WORDS M627]: the app cannot tell "not analysed" from "analysed, nothing found". The recipe maker, with a real user, decides; the alert and the documentation say so. On the demo nothing shows the risk: every metadata id is in every result table except ResFinder, and in `FastP` (42 of 42). A metadata that lists entities never sequenced would add a marked line for each to every result table. A table where absence means something else (an entity with no virulence gene) gets the same marker; the recipe maker reads the pipeline's documentation.

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
- Lean of the Opus agent, as a lean: (i), a read-time option declared on the data table, automatic for every result table that declares an entity id (variant i-b), placed before the tier-1 steps (P1). The source: (α), the metadata as read from its file. The marker: m1, a yes/no column, with its meaning required by the completion. With B6 the data table first keeps the initial population and the zeros, and a removal at the result table is complete. [as the Opus agent states them]

### The questions that remain for you, one at a time (each with what you would see on the demo)

1. **Where does the completion live?** (i) a key in the recipe on the data table, done by the app when it reads the file; (ii) a first step you write in tier 1; (iii) outside the recipe (the pipeline or a Data Import helper). On the demo with (i): the ResFinder Source view shows the file's 70 lines; T1 shows 74, 4 marked; the recipe holds one line (or none in (i-c)). Neither: say what you meant.
2. **Automatic for every result table that has an entity id, or only where the recipe names it?** On the demo both give the same 4 lines on ResFinder; the APEC reference list has no entity id and is never completed. Neither: say what you meant.
3. **Must the recipe state what the marked lines mean** (the check refuses the completion without it), or is the data check's note enough? On the demo: the check would ask ResFinder's meaning before the recipe opens; or the note would say "4 lines added to ResFinder; the recipe does not say what they mean". Neither: say what you meant.
4. **The marker: a yes/no column or a word in the cells, and its name.** On the demo: with the column, the plot keeps 4 samples in the bar at 0; with a word in the gene column, `QA_AMR_per_sample` counts 1 gene for each of the 4 and the bar at 0 is empty. Neither: say what you meant.
5. **When in the table: before the recipe's own tier-1 steps (they see the added lines) or after them?** On the demo: ResFinder's stamp would read "Detected" on the 4 lines before; `Detailed_summary` (42 ids in the file, 36 after its filters) gets no added line before, and 6 entities with a marked line after. Neither: say what you meant.
6. **Which metadata: as read from its file, or after its tier 1?** On the demo: remove one of the 4 added entities at the metadata's place: from the file, it stays in ResFinder, marked; after tier 1, it is no longer added, but ResFinder's place lies below the metadata's (one place per path). Neither: say what you meant.
7. **The order of the join: data first only, or may the metadata-first join stay (with an advice)?** On the demo: remove one detected entity at the ResFinder table: data first, 41 samples; metadata first and genes only, 42 samples with 5 in the bar at 0. Neither: say what you meant.
8. **An id in a result file and in no metadata: the note only, or also the marker "not in metadata"?** The demo has none; the template `left_join_lesson` has 2. Neither: say what you meant.
9. **An id repeated in the metadata: a note?** The demo's metadata has none. Neither: say what you meant.
10. **The three id-less lines of `demo_abromics`: remove them from the file?** On the demo recipe `demo_abromics`: 27 lines, no removal step, no example of a messy id; or keep them as a lesson. Neither: say what you meant.
11. **The list of the not-detected and the count per target.** The list is the marked lines, shown as a table result (decided design, not built, D-0485, D-0487); the count per target ("how many entities carry no gene X") is not covered. Neither: say what you meant.

### Runs after your choice (each registered before it runs; three points)
1. **The completed table through the demo's chains (the recipe side).** Requirement: a scratch ResFinder file with the 4 added lines and the marker column written by hand (the completion does not exist), the chain of `qa_amr_genes_per_sample` joined data first and metadata first. Expected: `QA_AMR_per_sample` 74 rows, 42 per entity, 4 at 0; `status` "Detected" on the 4 and `total_gene_count` 1 unless the steps are adapted; `ST22_Anchor`'s `status` "Detected" for the 4; row counts of `QA_fanout_exhibit` and `ST22_Anchor` unchanged; the heatmap's handling of an empty gene observed. Independence: a scratch recipe from the demo's schemas, every table rebuilt in its own empty folder, no lineage code.
2. **A removal on the completed table.** Requirement: a removal by key at the end of ResFinder's tier 1 in a scratch audit copy (the step written by hand). Expected: data first 41 samples, 4 at 0; metadata first with the marker read 37 / 4 / 1 "no line"; metadata first, genes only, 42 samples with 5 at 0. Independence: as 1.
3. **The marker forms.** Requirement: the same chain with a marker column and with a sentinel word. Expected: `gene.count()` 0 against 1. Independence: Polars on a scratch table, no recipe code.
4. **P1 against P2 on `Detailed_summary`.** Requirement: the completion by hand before and after its filters. Expected: no added line before; 6 marked lines after. Independence: as 1.
5. **The keys.** Requirement: a change in the metadata file changes the key of every completed table and the tables below (D-0560). Expected: every key differs; a stale stored table is not served. Independence: each variant in its own empty folder; the keys from the engine's own key functions on a hand-edited scratch recipe.
6. **The app's completion and the graph** (once built): the same points as 1 on the real option, and the valid sets of places with its new edge (D-0553), α and β.
7. **`not_in_metadata`** (if chosen): the lines of a scratch result file with an id in no metadata.

## B2. For `OVERLAP_AND_POPULATION.md`: a new dated section

---

## Her answers of 2026-11-23, third part (ledger D-0572): the control of the ids

**Her words, exact** (channel block M627): "1. yes we need a control of ids - as we started to implement - warnings in case something was wrong in the metadata so the user can recheck (as was planned recently) - if id present in data and in no metadata then the user must add the ID and update metadata (Id prefer the metadata corrected but a marker eg. "not in metadata" could be done, if id present in metadata and not in the data but is in the metadata an automatic completion at (first step) that would - that would be clear and mentionned both in literature and allerts. for the missing ids - but this might be before T1 a step the app does ... (not sure how the app could write the T1 first step recipe otherwise because then its a modification of the recipe)". [HER WORDS M627] And, on the facts: "4. this is true that is why the ids of both metadata and data sets should overlapp (or at least all in metadata and included for data sets) 5. true that is why metadata should be clean - all with an id ...".

**The control, as she said it, with the data check's note for each.**
- **(a) An id in a result file and in no metadata.** The data check informs, through the new channel, and tells the user to fix it ("the user must add the ID and update metadata"); she prefers the metadata corrected. The alternative she names, a marker "not in metadata": the lines stay, a yes/no column marks them; the note is the same. On the demo: none (0 in every file); the template `left_join_lesson` has 2, by design.
- **(b) An id in the metadata and not in a result file.** An automatic completion at the first step, said in the documentation and in the alerts: "N lines added to <table> from the metadata (ids ...), marked <marker>. The app cannot tell whether they were analysed with nothing found or not analysed; the recipe says how they are counted." On the demo: 4 lines added to ResFinder. This is her proposal B6; where the completion lives is her open question (see `CAUSE_AND_SOLUTIONS_ZEROS.md`, the section of D-0572). Until B6 is chosen the note is the one decided before: "N entities of the metadata have no line in this file".
- **(c) Metadata lines with no id.** The metadata should be clean ("all with an id"): the third note, "N lines of the metadata have no id", stays; the completion adds only ids that exist. On `demo_abromics` the three lines are there on purpose; her sentence points to a clean metadata, to confirm in the dry run (D-0525).
- **(d) An id repeated in the metadata** (proposed, not raised by her): "an id is repeated in the metadata: <ids>". It multiplies the rows of a join with the metadata second. The demo's metadata has none (42 rows, 42 distinct ids).
**The risk she accepts:** the app cannot tell "not analysed" from "analysed, nothing found"; the notes say so. [HER WORDS M627: "it knows the risk it accepts"]
