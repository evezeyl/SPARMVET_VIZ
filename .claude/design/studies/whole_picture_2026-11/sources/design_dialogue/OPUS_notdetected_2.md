# Opus round 2 on "a true not-detected is a true result" (D-0570): answers to SONNET_notdetected_1.md, one merged list, corrections, open points (2026-11-23)

**What this is.** My answer, point by point, to the Sonnet agent's blind position `SONNET_notdetected_1.md` (its candidates N1 to N6), set against my blind position `OPUS_notdetected_1.md` (my A, E2, B, B2, B2P, B3, B3P, C1, C2, D, E). Reading only, NO RUN (D-0566). No study file is edited. For each point: AGREE, DISAGREE (with file:line) or MISSING (in mine or in its). Then ONE list of options for her, with ONE naming that continues A to E, B2, B3 of `CAUSE_AND_SOLUTIONS_ZEROS.md`, the corrections both agents found, and what is still open between us.

Tags as in round 1: [HER WORDS D-n] / [RECIPE FILE] / [RULE FILE] / [CODE READ file:line] / [ESTABLISHED: file, point] / [POLARS SEMANTICS] / [REASONED, not run].

---

## 0. The coordinator's check: "a later anti-join is impossible" (mine) against "ST05 refuses an anti-join after the aggregation; `how: anti` is accepted by the engine" (its)

**AGREE: the two readings say the same thing.** Evidence:
1. **`how: anti` is accepted.** The step's form lists it [CODE READ `polars_calls.py:85`: inner, left, right, full, semi, anti, cross]. An existing engine test builds an anti join and keeps "the rows whose key is missing" [CODE READ `libs/transformer/tests/test_self_join_build.py:34-35, 43`, the step written with `maintain_order: "left_right"`]. So an anti-join can be written TODAY, as the tier-1 step of a joined table of its own. Both positions write it that way (its N2, my E2).
2. **Any join after tier 1 is refused, whatever its kind.** ST05 refuses every join action (`polars_join`, `polars_join_asof`, `modif_join_where`) in tier 2 or tier 3 [CODE READ `recipe_check.py:714-715`; `action_names.py:66` `TIER1_ONLY`]. It is not specific to an aggregation or to `anti`; "after the aggregation" (its words) and "later" (mine) are the same case.
3. **The engine could not run it either.** A join reads the tier 1 of each ingredient [CODE READ `orchestrator.py:269-294`]; tier 2 receives its table, not the ingredients [ESTABLISHED: RECIPES (vi)].
4. **A join whose ingredient is a join is refused too** (its point; MISSING in mine). An ingredient must be a schema of the recipe [CODE READ `recipe_check.py:866-867`, J04]. So an anti-join against the per-entity result (a join's output) cannot be written either.

**Two nuances, one each way.**
- (Mine, corrected.) I wrote: "with any other table it is her question 27". For her case the population is the metadata, so a later anti-join is a join with the metadata after tier 1: the decision it meets is D-0510 [HER WORDS D-0510: "join with metadata must be done at T1"], not question 27. I take its sentence "Her question 27 (a join after tier 1) is not needed for this case" [SONNET N2] and add D-0510 as the decision a later anti-join with the metadata would reopen. (Question 27 is framed for look-up joins in `RECIPES_FROM_THE_MODEL_AGREED.md:121-125`, and as the breadth of ST05 in `GOALS_REVIEW_sonnet.md:473`; neither is this case.)
- (Its, MISSING.) Because a join reads only the tier 1 of its ingredients, even a tier-1 anti-join cannot see a detection rule written in the result table's tier 2 (for example a threshold). The demo has none on ResFinder [RECIPE FILE `ResFinder_wrangling_tier2.yaml`: a count of rows and a sort].

---

## 1. Point by point on SONNET_notdetected_1.md

### Its section 0 (her case, what is asked, the facts)

- **"Two outputs: the number and the list", and beside them the information.** AGREE. MISSING in mine as an explicit distinction (I had it only implicitly: E2 gives the list, A the number). It is a good frame for her and goes into the merged list (section 3).
- **Facts 1 to 3.** AGREE (the same as my F2 and the core fact).
- **Fact 4 (38 / 4 becomes 37 / 5 after a removal of a detected entity at `T1:ResFinder`; 37 / 4 of 41 at the join place).** AGREE: the same numbers as my A [OPUS_notdetected_1 section 3 A, "Run after her choice"]. Its last sentence ("the number is stable only if the removal is written where the population path is covered, or if the app can name the third class") is right; B3 and B5 (my B3P) should be added: there the file itself keeps the number stable (the removed entity leaves, or shows "no result").
- **Fact 5 ("metadata second keeps the zeros" wrong as worded).** AGREE, the same reading as mine; its version adds B2 ("or a table of the analysed entities"), which mine had only for B3. I take it.

### N1 (= my A; her route ii)

- (a) the status column `detection` written in the join's tier 1 and taken per entity with `first()`. AGREE as a fragment. MISSING detail in its fragment: today's `QA_AMR_per_sample` tier 1 ends with a `polars_select` that lists the published columns [RECIPE FILE `QA_AMR_per_sample_tier1.yaml`]; `detection` must be added to it (the last `polars_select` of tier 1 publishes the columns [RULE FILE `rules_data_analysis_recipe_structure.md` section 5]).
- **The pitfall: a word filled into the counted column is counted.** AGREE; MISSING in mine. The precedent is real: `demo_abromics` fills `sequence_type` with "Non Determined" after a left join from the metadata [RECIPE FILE `demo_abromics.yaml:55-57`, with the comment "a sample that has no MLST result is not a missing value: its result is not determined"]. There the column is a category counted per bar, so it is right for that plot; for a COUNT of genes the word would count as 1. It joins my F5 (the aggregate decides 0 or missing).
- (b) the audit. AGREE.
- (c) AGREE.
- **(d) "The recipe check could say ... that a result per entity written from a left join with the metadata first has no step that names what a blank means (it reads the steps)."** DISAGREE in part. The check reads a formula only as text [CODE READ `polars_calls.py:82`: `named_exprs` is "a Polars expression as text"]; to judge whether a formula "names what a blank means" it would have to read intent from that text: a guess. What the check can read without guessing: the first ingredient is the metadata and the kind is `left`; a tier-2 `polars_group_by` follows; a `pl.len()` in its aggregations (an entity with no line counts as 1, F5 of my position). The advice can be written on that pattern: "This result per entity starts from the metadata. Say in its description what an entity with no line in <table> means." (words PROVISIONAL).
- (e), (f), (g). AGREE (my A gives the same).

### N2 (= my E2; her route i)

- (a) the fragment with `maintain_order: left_right`. AGREE. MISSING in MINE: my E2 fragment had no `maintain_order`, which `polars_join` REQUIRES [CODE READ `polars_calls.py:54-60`, `REQUIRED`; a missing required parameter fails the step, `polars_calls.py:18-19`]. The existing engine test writes an anti join with `left_right` [CODE READ `test_self_join_build.py:35`]. Correction taken.
- "What 'later' costs today": AGREE (section 0 above), with D-0510 added.
- (b) the inversion (a removal at ResFinder makes the entity APPEAR in the list). AGREE; the same as mine.
- (c) AGREE, except **"the output of a table as a result is a direction, not confirmed (D-0487, D-0496)"**: DISAGREE. A table as a result is her design, DECIDED and not built: "A plot entry should be a result entry with either a plot or a table" [HER WORDS D-0485; ledger status DECIDED, "Not built"]; D-0487 completes it and leaves the KEY open ("show is weak we need a good key system"). D-0496 is about the form of derived tables (form 3), not about a table as a result. Two facts to add: today a joined table that no plot reads is exported as its tier-1 file [RULE FILE `ui_implementation_contract.md` section 7.2 rule 7, D-0457, built], but how a user views it in HOME is not decided; so today the list of the not-detected is seen through the data preview of a plot that reads it.
- **MISSING in its: what the user of HOME meets.** The audit cannot YET follow an anti join (D-0452), and a place the app cannot trace is red and not tickable [HER WORDS D-0460: "B of needed we try to.fimd a.solutiom later", the reading "B red and not tickable"]. Whether the new walk (her graph model, not built) traces an anti join with its inverted effect is open.
- **MISSING in both: a metadata line with no id is listed as "not detected".** "A missing key never matches" [CODE READ `test_self_join_build.py:169`], so an anti join keeps a metadata line with an empty id as an entity with no ResFinder line. The same holds for A: the left join keeps that line with empty results, the group-by makes one group of the missing ids [POLARS SEMANTICS], and the count of not-detected grows by one. This is why her sentence "the metadata itself should have id with non empty lines" [HER WORDS D-0570] matters for both of her routes. On the demo the metadata has no empty id [ESTABLISHED: OVERLAP_AND_POPULATION.md line 42]; `demo_abromics` removes its 3 id-less lines by a visible step before its join [RECIPE FILE `demo_abromics.yaml:45-47`].
- (d) an advice that an anti step has the population as its first ingredient. AGREE as information (an anti join can have another first table legitimately, so an advice, not a rule). The advice decided in D-0452 (the kind is not YET followed) is not in `recipe_check.py` today [CODE READ: no such text].
- "NEEDS A RUN". AGREE; the same three points as mine.

### N3 (the recipe declares; the app completes and labels; a form of C)

- (a) the declaration `absence: {population: metadata_schema, means: not_detected}`, refused today as S01. AGREE [CODE READ `recipe_check.py:390`, unknown keys of a schema are S01]. Its form names the population inside the declaration; mine names only the meaning and takes the population from `entity.population`. Both work; one place for the population is simpler (open, section 5 O5).
- (b) the app completes from the population and labels three classes, "removed (audit step)" read from the audit record. AGREE as a candidate; it is my C2 with my C1 and the audit record, and it adds what I had only as "a rule, hers": the COMPLETED table itself carries the class. It writes no step at a second place, so it does not meet D-0553.
- **(e) "it is the only form where the three classes can be told apart."** DISAGREE in part. My B3P (B5 in the merged list) tells three classes in the recipe's own table: detected, not detected (from the file), no result; with the audit record the app can then name "removed" among "no result" (my C1 point 4). The two differ in where "analysed" is known: N3 by the author's promise (so "not analysed" cannot appear), B5 by the file (so "not analysed" and "removed" are both "no result" in the table and told apart only by the app's record).
- **MISSING in its (c) and (f):**
  1. A completed row needs the metadata's columns (the plot `qa_amr_genes_per_sample` fills by `country` [RECIPE FILE]); so the app's completion is the metadata join done by the app instead of the author. It is a new edge in the graph (catalogue (c): "the same question as a look-up join in tier 2").
  2. The result then depends on the audit record in a new way (a reading, not a step). The export must carry the declaration and the rule of the completion, or the same data and recipe would not give the same result [HER WORDS D-0108: "correct and reproducible science"; RULE FILE `rules_verification_testing.md` section 9: "what the user sees and does is what the export contains"].
- NEEDS A RUN and a decision. AGREE.

### N4 (= B2) and N5 (= B3)

AGREE with both, number for number. Its N4 (d) ("N entities of the metadata have no line in the base table is exactly 'not analysed'") is right when the base is the manifest of THIS analysis [ESTABLISHED: OVERLAP section 3, point 4]. MISSING in its: the forms with the INITIAL population in three states, B4 (my B2P: the metadata first plus a manifest) and B5 (my B3P: B3's files, the metadata first, a column "has a line", no fill). Its section 3 says that N4 and N5 report "not analysed" as a second number; B4 and B5 put it in the same table.

### N6 (an information line from the declared population)

AGREE. MISSING in mine as a line of its own: my C1 point 1 is the same note with the meaning added, and needs a new key; N6 needs none (`entity.population` exists, checked by E02 [CODE READ `recipe_check.py:332-348`]). Its (c) "not exported unless the export writes it": AGREE, and the rule says it must be: what the user sees is what the export contains [RULE FILE `rules_verification_testing.md` section 9].

### "Also considered"

AGREE. The table result ("detected 38, not detected 4" as a two-row table) is D-0485's design (decided, not built; see N2 above), not only a direction.

### Its section 2 (the table) and section 3 (the initial population)

AGREE with the populations of section 3. In its table, the line N2 lacks the user-visible limit (red, not tickable, D-0460); the line N3 "removed class shown" holds only with the audit record read by the app (as its text says).

### Its section 4 (where "metadata second keeps the zeros" must be corrected)

- `CAUSE_AND_SOLUTIONS_ZEROS.md` line 59: AGREE, it must change: it makes the order the subject ("the data first and the metadata second keeps the zeros").
- Lines 58, 186, 218 (B3 (vi)), 220 and `OVERLAP_AND_POPULATION.md` lines 31, 125, 129: DISAGREE that they are wrong; each names the table that keeps the rows. Line 58: "a table of the analysed entities as the FIRST table of the join"; line 186: the same heading; line 218 is inside "(vi) What the audit does under B3" and says "the metadata adds no entity"; line 220 requires "a scratch copy of the ResFinder file with 4 added lines"; OVERLAP 31 and 125 name the first table ("population (a data table) first"); OVERLAP 129 is the retest of (a2) with the analysed table as the base. Proposal: change 59; add one clause at 58, because it stands next to 59 in her half page; leave the others. OPEN (section 5 O3).
- Its replacement sentence: AGREE; merged with mine in section 4 below.

### Its section 5 (the data check)

- Both directions; BLUEPRINT's Validate yes. AGREE [HER WORDS D-0570: "4. yes the validated question - yes . information is very important here"].
- **A third note: "N lines of the metadata have no id".** AGREE as a proposal (not decided), and the null-id point above is a reason for it: such a line becomes a "not detected" entity in both of her routes. OPEN detail: what the note says when the recipe removes these lines on purpose (`demo_abromics.yaml:45-47`, a step in the JOIN's tier 1, so the metadata's own tier 1 still holds them); D-0569's message tells the user "to better fix this", which would contradict a deliberate lesson; whether `demo_abromics` keeps its three lines is hers (M624 point 5).

### Its section 6 (runs) and section 7

AGREE with the runs 1 to 6. Its section 7 states no lean ("the Opus agent's reading comes first"): my leans of round 1 stand, as leans (section 6 below).

---

## 2. What is MISSING in its position, from mine (proposed for the merge)

1. **The states of an entity** (detected; analysed, nothing found; not analysed; removed by key at the result table; gone), and **a filter on values** (a threshold) that leaves an entity with no line gives a TRUE not-detected under that threshold: only a removal by key gives a false one [OPUS_notdetected_1 F1].
2. **Today HOME writes the audit step at the plot's own table (T3)**: there is no false not-detected yet; it comes with the earlier places, decided and not built [RULE FILE `ui_implementation_contract.md` section 2; D-0316 to D-0318, D-0337].
3. **The aggregate decides 0 or missing** (a count of values or a sum gives 0; `pl.len()` gives 1; a mean, minimum or maximum gives missing; a fill of 0 on a mean writes a value never measured) [OPUS_notdetected_1 F5].
4. **The join-kind table** (her words "that will depend on the join type"), including: with B3 files the anti-join lists the NOT ANALYSED entities, not the not-detected; a semi join gives the detected list only.
5. **B4 and B5**: the initial population in three states.
6. **The risk of D-0549 under A**: a metadata entity never analysed counts as "not detected" ("some users will have metadata for more samples" [HER WORDS D-0549]).
7. **D-0510** for a later anti-join with the metadata; **D-0460** (red, not tickable) for the anti-join's places.
8. **Corrections:** "42 bars" and catalogue (e) line 283 (section 4).

## 3. What is MISSING in mine, from its position (taken)

1. The number and the list as two outputs.
2. The pitfall of a word filled into a counted column (`demo_abromics.yaml:55-57`).
3. J04: a join of a join is refused (`recipe_check.py:866-867`).
4. `maintain_order` is required in my E2 fragment (`polars_calls.py:60`).
5. N6 as a line of its own (no new key).
6. N3's completed table with the class "removed" (my C2 had it only as "a rule, hers").
7. The third note of the data check.
8. My sentence "with any other table it is her question 27" is withdrawn (section 0).

---

## 4. ONE merged list for her (one naming; old letters kept; new lines marked NEW)

**The question has two parts.** Part 1: the FORM of the result (one choice). Part 2: the INFORMATION about what a 0 or a missing value means (F or C1, with any form; or nothing).

| Letter | In plain words | The same as | On the demo, by reading (42 entities; 38 with a ResFinder line) | A removal of a detected entity at the result table's own place |
|---|---|---|---|---|
| **A** | The metadata first, the blanks filled in the recipe, the meaning named in a column (her route ii; today's demo) | my A = its N1 = catalogue (b) | 38 detected, 4 not detected (the bar at 0) | 37 / 5: counted as not detected (false) |
| **B** | Count per entity first, then the metadata first | catalogue (a) | 38 / 4 | 37 / 5 (false) |
| **B2** | A table of the analysed entities first, the metadata second: the analysed population | my B2 = its N4 = catalogue (a2) | 38 / 4 (`FastP` holds 42 of 42) | 37 / 5 (false) |
| **B3** | The result files list every analysed entity (with an explicit mark); the data first, the metadata second: the analysed population | my B3 = its N5 | 38 / 4, the 0 counted from the file | gone: 37 / 4 of 41 |
| **B4** NEW | The metadata first and a table of the analysed entities: the initial population in three states (detected, not detected, not analysed) | my B2P = catalogue (f2) | 38 / 4 / 0 not analysed | 37 / 5 / 0 (false) |
| **B5** NEW | B3's files, the metadata first, a column that says "has a line", no fill: three states (detected, not detected, no result) | my B3P | 38 / 4 / 0 no result | 37 / 4 / 1 no result (no false result) |
| **C2** (C extended) | The app completes the per-entity result from the declared population and, with C1 and the audit record, labels three classes (detected, not detected, removed); variants: the recipe completes (catalogue (c), not buildable today), the recipe says the result is per entity (f5) | its N3 = my C2 (with C1) = old C | 38 / 4 | 37 / 4 / 1 removed |
| **D** | No zeros; the count of not-detected only in words | unchanged | 38 entities, no bar at 0 | gone |
| **E** | A right or full join (the metadata second, its rows kept) | unchanged | 38 / 4 (not run) | 37 / 5 (false) |
| **E2** NEW | An anti-join as a table of its own: the LIST of the entities with no line (her route i) | my E2 = its N2 | 4 rows | 5 rows: the entity is ADDED (false) |
| **F** NEW (part 2) | An information line with the result, from the declared population: "population 42; with a line in ResFinder 38; without 4 (of which N removed by an audit step)"; written in the export too | its N6 | the line 42 / 38 / 4 | "with a line 37; without 5, of which 1 removed by an audit step" |
| **C1** NEW (part 2) | F plus the meaning, declared by the recipe for each result table ("no line here means: nothing found"); repeated by the app in the data check, the dialog and the report | my C1; the declaration of its N3 | as F, with "nothing found" | as F, with the meaning |
| **Neither** | Say what you meant | | | |

Notes for the merge:
- In every form, the default place at the join (D-0549) removes the entity (41 entities), and "Remove from all the data" (D-0416) too.
- The data check's notes (both directions, and the third note if she agrees) go with every form [HER WORDS D-0570].
- Today (T3 writing, built) no form shows a false not-detected (section 2 point 2).

## 5. The corrections both agents found (for the study files; not edited here)

1. **"Metadata second keeps the zeros"** (both): `CAUSE_AND_SOLUTIONS_ZEROS.md` line 59 must change. Merged replacement sentence (a proposal): "With a data table first and the metadata second (`left`), the table holds exactly the entities of the first table: the metadata never adds one. A zero stays only where the first table already has a row for the entity: a result file that lists every analysed entity (B3), or a table of the analysed entities used as the first table (B2). With today's result files, which list findings only, an entity with nothing found is absent." One sentence for her half page: "Correction: 'metadata second keeps the zeros' was wrong as written: the metadata never adds a row when it is second in a left join; a zero stays only where the first table already has a row for the entity (B3, B2)." Which other lines get a clause: OPEN (O3).
2. **"42 bars"** (mine): `CAUSE_AND_SOLUTIONS_ZEROS.md` lines 47, 53, 59, 62, 220, 291 and `OVERLAP_AND_POPULATION.md` line 31: the plot counts samples by their number of genes; "42 samples counted, 4 in the bar at 0".
3. **Catalogue (e), line 283** (mine): the step's form lists all seven join kinds [CODE READ `polars_calls.py:85`].
4. **A table as a result** (mine, against its text): DECIDED as a design and not built (D-0485, D-0487; the key open); D-0496 concerns derived tables.
5. **My E2 fragment** (its find): `maintain_order` is required (`polars_calls.py:60`).
6. **My question-27 sentence** (its find): withdrawn; D-0510 is the decision a later anti-join with the metadata meets.

## 6. Open between the two agents

- **O1.** Its "N3 is the only form where the three classes can be told apart" against my B5 with the audit record (section 1, N3 (e)).
- **O2.** The recipe check's advice for A: on the pattern (metadata first, a per-entity aggregation, a `pl.len()`), or on whether a step "names what a blank means" (section 1, N1 (d)).
- **O3.** Which lines besides `CAUSE` 59 get a clause (mine: 58 only; its: 58, 186, 218, 220, OVERLAP 31, 125, 129).
- **O4.** The third note: its wording when the recipe removes the id-less lines on purpose (`demo_abromics.yaml:45-47`).
- **O5.** C1's form: the population named inside the declaration (its N3) or taken from `entity.population` (mine).
- **O6.** The naming of section 4 (B4, B5, C2 extended, E2, F, C1) and the two-part question.

**Leans (as leans, unchanged from round 1):** where the pipeline can write it, B5 with an explicit column written by the pipeline; where the files cannot change, A (or B4 where a manifest exists) with C1; F or C1 with every form; no lean for E2. The Sonnet agent stated none yet.
