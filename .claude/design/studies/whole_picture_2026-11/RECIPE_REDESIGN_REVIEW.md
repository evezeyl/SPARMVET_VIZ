# The recipe redesign, reviewed from the whole picture (2026-11-22)

Your order: "Id like the opus agent that is looking at the whole picture to have a review also at the suggestions for the recipe redesign when it is done as its important for the way the redesign will functione as it can facilitate some steps. This agent is allowed to communicate with the agents that are in charge of the recipe design proposal" (D-0526). The short version for you is part 7 of `WHOLE_PICTURE.md`; this file holds the details and the evidence. I review; I do not choose. The form stays yours (D-0496).

---

## 1. What I read

- The refined proposal, now copied into this folder as `RECIPE_PROPOSAL_refined.md` (from `tmpAI/panel/tables_as_results/refined/PROPOSAL_FOR_THE_OWNER.md` of the main tree, unchanged; D-0419): Parts 0, 1, 2.2 (the form 3 file), 3 (your case), 4 (where the derived table lives), 5 ("Table to view"), 6 (tried against the recipe check), 7 (the forms compared) and 8 (recommendation) in full; Parts 2.3 to 2.7 (the files of forms 4 and 5, the reads summary, the split into files) by their headings and their differences from form 3 only.
- In `tmpAI/panel/tables_as_results/`: `FACTS.md`, `FACTS_2.md`, `TABLE_FOR_THE_OWNER_5.md`, `VIEWPOINTS_5.md`, `PROPOSALS_AFTER_YOUR_ANSWERS.md`, `trials/REPORT.md` in full; `TABLE_FOR_THE_OWNER.md` to `TABLE_FOR_THE_OWNER_4.md` by their flags and options (first 30 lines each); `VIEWPOINTS.md` to `VIEWPOINTS_3.md` by their verdicts and flags (searched, not read line by line).
- Your lines: D-0063, D-0306, D-0344, D-0485, D-0487, D-0488, D-0489, D-0490, D-0492, D-0495, D-0496, D-0514 to D-0518, D-0523 to D-0526.
- Not run by me: none of the proposal's scripts. Its numbers below are its own runs, labelled so.

---

## 2. What you asked of the recipe form, in your words

| Your words | Line |
|---|---|
| "No Tier 3 is not a plot - T3 is the data that goes into a plot ... its still data" | D-0514 |
| "we have to consider that each table Tier can actually lead to information usefull for the user" | D-0514 |
| "when a table is the result it is shown in the highest tier that contains instruction" | D-0515 |
| "that no tier 3 exist today does not mean it can - its still a data table" | D-0515 |
| "so a plot entry actually should be a result_entry with either plot or table no? last tier of entry also can be T3=T2=T1 (so the fall back mechanism)" | D-0485 |
| "yes result is the last stage (the tier that has the latest instructions in the recipe)" | D-0485 |
| "e : we need to follow the recipe --- so do not fix all tiers need to be functional." | D-0485 |
| "1. Export I do not agree all data are exported no ? so we shuold be able to export the table that is as result also" | D-0487 |
| "show is weak we need a good key system that make it clear for the recipe maker" | D-0487 |
| "maybe the result should be the default at opening but the user must still be able to navigate" | D-0487 |
| "but Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before" | D-0516 |
| "I mean I want to see your hierarchy how to define T1, T2, T3, results {table , plots), plot recipe" | D-0516 |
| "I need arguments for good practice and good data science (not economical in term of changes to do - because economy now might need problems later)" | D-0516 |
| "a) well one final result could be used on T2a but T2a could be used to produce one T3a for another final result - what would be done in this case ?" | D-0517 |
| "yes we need the `from:` this clarifies but still the hiearchy is unclear of where to place it." | D-0517 |
| "I want the examples on how it would like like with all the tiers and both plot and data as result" | D-0517 |
| "imaging the case where there is something to remove (filter) that is not seen at the mlst_bar level ... I am just wondering of how to make it navigate. It seems to me to be an interesting solution though" | D-0518 |
| "wait for the panel I just said I might have more questions after" | D-0496 |
| "we need to finalize the recipe design with the from and hyerarchy ... we had that going on - before we can do a big move on all demo recipes" | D-0525 |

As the review session reported it (not your words in a line): you set forms 4 and 5 aside ("we can exclude form 4 and I guess 5") and said of form 3 that it "seems to me to be an interesting solution though" (D-0496; the same words are yours in D-0518).

---

## 3. Does the proposal meet what you asked?

| What you asked | Form 3 | Evidence in the proposal |
|---|---|---|
| Tier 3 is data, not a plot | **Yes.** Every data step is in the data part; a result only names a table. | Part 1 "Form 3: the levels"; Part 2.2 |
| A result is a plot or a table | **Yes.** `result: plot` or `result: table`. | Part 2.2; Part 8 point 3 |
| The result is the last stage | **Yes.** `from:` reads its table "at its last stage: after its tier 2, or after its tier 1 when it has no tier 2". | Part 1, the answer on `from:` |
| Follow the recipe; every tier works | **Yes,** with one change of the check: the tier 2 of a table read only by a derived table is refused today (J14), and the check must count a derived table as a reader. | Part 0 flag 5; Part 6 (c) point 4 |
| Tier 3 defined like tiers 1 and 2 | **In shape yes, in name no.** What you would write as a tier 3 becomes a table of its own (a derived table) with its own tier 1 and tier 2. The author no longer writes a `tier3`; the word is kept only for the audit's "this result only" place. | Part 1 ("In form 3 the reads summary is not a tier 3 any more"); Part 8 point 8 |
| Defined before the results | **Yes.** The file order: source tables, joins, derived tables, `plot_defaults`, results. | Part 1, "The order in which a reader meets things" |
| The place of `from:` | **Yes.** In a derived table after its `label` and `description`, before its `tier1`; in a result in place of `target_dataset` (a suggestion). | Part 1, "Where would be the `from:` located?" |
| Your case: T2a feeds a result and also a T3a for another result | **Yes,** walked through with real numbers on the demo: 42 rows after the join, 33 after its tier 2, 6 in the summary. | Part 3 (run) |
| Complete examples: all tiers, a plot and a table as results | **Yes,** on a slice of the demo; the reads summary in full in 2.6. | Part 2.2, 2.6 |
| Arguments of good practice and data science, not economy | **Yes.** The cost is a row of information. | Part 7 |
| The table result exported | **Not in the proposal.** It rests on your decisions: "Part 1 -A" (D-0490: the file named from the entry's id) and D-0487. | — |
| A good key system | **Partly.** `result:` and `from:` are suggestions; the options K1 to K4 are in `PROPOSALS_AFTER_YOUR_ANSWERS.md`. | Part 8 points 2 to 4 |
| How to navigate to the tables before a result (D-0518) | **Partly.** "Table to view" for a result made from a derived table is left open (s1, s2, s3). | Part 5 |

---

## 4. What form 3 makes easier or harder in the rest of the picture

Consequences for a user, not cost.

### 4.1 The places of an audit step and the default ticks
- A derived table is one more table of the lineage, so one more place: its tier 1, and its tier 2 only while the entity key still exists there (the proposal's Part 3: after the count, `sample_id` is gone, so there is no line).
- For a removal by the entity key, the earliest place is always above the derived table (question 1 of the main document, either reading), so the default ticks do not change.
- New and useful: a step written at a derived table changes only the results made from it (Part 3, place iii: the two results of the summary change, `mlst_bar` does not). Today that choice needs a copy of the steps.
- "This result only" stays: the audit writes in the result's own tier 3, as you decided ("There is also a line for one plot only", D-0346, the review session's reading which you confirmed).
- Harder: a summary that is shared by several results is one place for all of them; the dialog must list every result that reads it before you confirm (Part 0 flag 2, run: one removal at the shared table changed result A and both results of the summary).

### 4.2 The join with the metadata
- It stays a tier 1 step of a join of raw data tables (D-0510, D-0523).
- A derived table is made from a table that already has the metadata: "derived tables should already have the metadata joined" (D-0511). So it never joins the metadata, and the rule of D-0510 does not meet it. Whether a derived table may join anything at all (a look-up table) is not said in the proposal (question 2 to the authors).

### 4.3 The story of the data
- Clearer: every summary gets a name and one definition.
- Longer: one table per derived table.
- A gap: "Table to view" (Source, T1, T2, T3) shows the stages of ONE table. For a result made from a derived table, the derived table's tier 1 and tier 2 are shown, but the tier 2 of the join it is made from is not among the four choices (Part 5). What "Source" means there is open (s1: the files as read; s2: the table it is made from; s3: both, named). This is your question of D-0518. A picker (question 13 of the main document) would answer it; under form 5 the four choices were the whole chain, a merit of form 5 that the proposal names.

### 4.4 A table as a result, and its export by id
- Easier: a table result is the last stage of one table, so the table on screen and the file exported are the same object.
- Open: the proposal does not say how the export names the file of a table result ("Part 1 -A", D-0490: named from the entry's id), nor what happens when a plot result and a table result read the same derived table (the same rows written twice under two ids, or once).
- The "Showing 100 of N rows" sentence matters more for a table result (D-0488; merged on `dev` as `d2e92547`).

### 4.5 The two parts of the reproducibility bundle
- Not changed by the form: "original" and "final_audited" each hold a recipe of the same form, and the data once (D-0490, D-0492).

### 4.6 The comparison of original and audited (D-0489)
- Easier: the pair to compare is the original and the audited result, both at the last stage (the trials showed that comparing T2 with T3 shows rows the audit never removed, `trials/REPORT.md` Part A, run). Under form 3 the last stage is one table for a plot and its table.

### 4.7 The lineage picker
- A derived table has one parent, named by `from:`. In an outline that starts at the original data files ("I like the idea of outline at the base", D-0508) it is one more level, easy to draw.

### 4.8 The names and the one move of the demo recipes (D-0525)
- The form decides which keys every recipe, template and Gallery example gets: a list `results` (or another name), a key `result:`, `from:` in place of `target_dataset`, a block `derived_tables`.
- The one move gathers the names pass, the move of `VirulenceFinder` (D-0523), the label of the QA group, the plot `ui_title`, the derived tables if you confirm the form, and the check of the metadata-join rule on every recipe, as one dry run shown to you (D-0525, the review session's reading).
- No demo plot has tier 3 steps today, and one template has them (`templates/left_join_lesson.yaml`; architect, round 5): moving the data steps out of results touches few files. Renaming the keys touches many: the round 3 user viewpoint counted 251 files with `plots:` (193 test fixtures of the plot library, 34 Gallery files, 16 configuration files). Information only.

### 4.9 BLUEPRINT
- It must write this format: "so we should not replace existing recipes that are production ready by mistake. The possibility of adding comments should exist and they should not be lost." (D-0495).
- Its map knows the roles source, join and plot today (`libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py`, `FACTS.md` section G); a derived table and a table result are two new roles.
- You wrote "For blueprint we will have to look at that later but good to see if solution can work - we will have to refactor blueprint any how" (D-0485).

### 4.10 Tables that no plot reads
- Under form 3, "read" means read by a result or by a derived table. The check's refusals of a tier 2 (S07 for a source table, J14 for a join) must count a derived table as a reader (Part 0 flag 5, run).
- A table that nothing reads keeps the question of its tiers (question 21 of the main document; your words "T1+T2 and T1+T2+T3", D-0451, and "Why Tier 2 refuses ? its still data wrangling", D-0514).

---

## 5. Where the proposal and the whole picture disagree, or leave a hole

1. **The default ticks.** Part 3 lists the dialog lines as "every line is ticked when the dialog opens and you untick (D-0316)". Your later default is "but ok we tick low (early) near the original table" (D-0508), and which place is earliest is open (question 1). The walk-through should be redone with D-0508, under both readings.
2. **The line `metadata_schema`.** Part 3 lists it with the note "the MLST row stays, with an empty year and country, until tier 2 removes it" (marked "reasoned" there). It is the left-join effect of reading A of question 1 (part 6.1 of the main document); the proposal does not connect it to D-0510 and D-0523.
3. **Two reading rules in one recipe.** A join reads its ingredients after tier 1; `from:` reads its table after its last stage. Both are needed: Part 0 flag 3 shows that making joins read tier 2 would change results silently on the demo (`ResFinder` has a tier 2 and is an ingredient of four joins). The recipe documentation must say both rules plainly.
4. **"Table to view" for a result made from a derived table** (4.3): open in the proposal.
5. **The export of a table result by its id** (4.4): not in the proposal.
6. **A result id written in two groups** silently replaces the first (Part 0 flag 6, run). It is a defect of today for plots too (`libs/utils/src/utils/recipe_tiers.py:152-161`, read by me): see `DIFFERENCES.md` A23.
7. **The names in the examples.** Part 2.2 writes `ui_title` in results and `label` on tables; your names decisions remove the plot `ui_title` ("you can remove the ui_title", D-0484) and rename `label` to `ui_label` (D-0468). The final examples should use the decided names.
8. **Data agnostic words.** Part 3 writes "remove sample 97991777" and the derived table's description "one row per sample"; these are the demo's example and fine there. A rule or a screen text drawn from the proposal must say "the entity" (D-0512).
9. **The audit copy.** Under form 3 a result's tier 3 holds only audit steps, in the second list `audit_steps` of D-0332. Whether the library's audit copy (`libs/utils/src/utils/audit_copy.py`, which names the place `T3:<plot>`) writes it unchanged for a table result was not checked by the proposal (question 7 to the authors).

---

## 6. What could be simpler, seen from the whole

- **One level of derived tables for now.** A derived table made from a source table or a join, not from another derived table. The story of the data and the picker then stay at most one table longer than today, and "Table to view" has one extra link at most. The proposal allows chains ("or a derived table written above it", Part 1); your case needs one level. Suggestion: the same "revisit if needed" as for a join of joins (D-0344: "Yes, revisit if needed").
- **No join of a derived table, for now.** A join that takes a derived table as an ingredient would reopen "a named join takes only source tables" (D-0344). The proposal leaves it open (Part 8 point 10); nothing in your case needs it. Information.
- **"Result" on screen instead of "T3".** Under form 3 the author never writes a tier 3. On screen, the last stage of a result could be called "Result", as in the badge you accepted ("I like the badge that says result or earlier stage this is accepted", D-0487). "T3" would then need no explanation, and "tier 3" would be only the audit's place in the audit recipe.

---

## 7. The questions that come after the form (not before)

From the proposal's Part 8 and `PROPOSALS_AFTER_YOUR_ANSWERS.md`. They make sense only once the form is chosen.
1. The list of results: `results` (K1) or another name; the key that says what a result is: `result: plot | table`, required in every entry or a plot when absent (K1 to K4).
2. The key that names the table a result shows: `from:` (the same word as in a derived table), `table:`, `reads:`, or keep `target_dataset`.
3. The block of derived tables: `derived_tables`, a block of its own (Part 4, option b), or inside `joins`, or nested under its source table.
4. What `from:` reads: the last stage of its table (suggested), or a named stage.
5. Form 3 only: confirm that the author never writes steps in a result's `tier3`, and that the audit still writes there ("this result only").
6. Joins: keep "a join reads the tier 1 of its ingredients" (today); the alternative changes results silently in the demo (Part 0 flag 3).
7. May a join take a derived table as an ingredient (reopens D-0344)?
8. "Source" for a derived table in "Table to view": s1, s2 or s3 (Part 5).
9. When a table result opens on the result: each time it is selected (R1) or the first time only (R2); and on leaving it, the earlier choice comes back (P1) or stays on the result (P2).

---

## 8. Assumptions I made while the authors are asked

Marked here and in the main document where they matter. None changes a recommendation.
1. A derived table is never the earliest place for a removal by the entity key (it is always below the tables that hold the entity first).
2. A derived table holds no join step: it is made from ONE table.
3. A table result is exported under its own id, also when another result reads the same table ("Part 1 -A", D-0490).
4. "Table to view" for a derived table follows the proposal's suggestion s3 until you choose.
5. The demo has no case of a derived table made from another derived table.
6. The decided names (D-0468, D-0484) apply to every example of the final proposal.

---

## 9. Questions for the authors of the proposal

The same list is in `tmpAI/questions_for_the_proposal_authors.md` of this worktree, for the coordinator to pass on.
1. Redo Part 3 with your default of D-0508 ("tick low"), under both readings of question 1: from `samples_per_country_year`, which lines start ticked, and what changes?
2. May a derived table's tiers hold a join step (for example with a look-up table)? If yes, how does the rule of D-0510 (the metadata joined only in tier 1 of the join of raw data tables) apply there?
3. When a plot result and a table result read the same derived table, what does the export write: one file per result id, or one file for the table?
4. Which of s1, s2, s3 does the proposal now recommend for "Source" of a derived table, and how does a user see the tier 2 of the join that a derived table reads (D-0518)?
5. Is there, in the demo or in the shipped recipes, a case for a derived table made from another derived table? Would "one level for now" lose anything you asked for?
6. With form 3, does a source table or a join read only by a derived table get its tier 2 built, shown and exported (the check codes S07 and J14)? How does that meet D-0451 and D-0457?
7. Was the form of a result's `tier3` with only `audit_steps` checked against the library's audit copy (`libs/utils/src/utils/audit_copy.py`, the place `T3:<plot>`)?
8. Which files does the one move touch under form 3 (recipes, templates, Gallery examples, test fixtures)? Does the Gallery's format (a plot entry with a taxonomy) change too?
9. Has anyone checked that BLUEPRINT's map and its Save can write a derived table and a table result without losing comments (D-0495)?
10. Will the final examples use the decided names (`ui_label` for tables, no plot `ui_title`)?
11. Is the duplicate result id (Part 0 flag 6) filed as a defect of today, independent of the form?

---

## 10. Recommendation (mine)

Form 3, with one level of derived tables for now, and the dialog walk-through redone with your default of D-0508.
- It meets what you asked on your own criteria: one table, one definition; a definition before its use; a plot and its table show the same numbers by construction; to know which results a step changes you search one name (Part 7).
- "This result only" is kept by your decision of D-0346, so the main argument for form 4 is already answered (Part 8).
- The holes of section 5 are questions of a rule or a word; none of them needs another form.

---

## 11. What I did not check

- I did not run any script of the proposal. Its numbers (42, 33, 6 rows; the place walk-through) are its own runs.
- The forms 4 and 5 files were read by their differences from form 3 only.
- The earlier rounds (tables 1 to 4, viewpoints 1 to 3) were read by their flags, options and verdicts, not line by line; their conclusions are in your lines D-0485 to D-0489.
- Nobody built form 3: the format, the check and the engine do not know it (Part 6).
