# Final check of the whole-picture design, version 2 (2026-11-22)

VERDICT: FIX FIRST: 14 fixes, all text; none changes the picture or a number. The picture, the three runs, her quotes (every quoted run was found in its ledger line) and the set of questions are sound. Scratch: `../SPARMVET_VIZ_wt_whole_picture/tmpAI/final_check/` (`q.py`, `q2.py`).

## A. Her decisions D-0485 to D-0526 in the files
In the document for her as her words: 20 lines (485, 487, 495, 496, 499, 505 to 509, 511 to 514, 516 to 518, 523, 525, 526). Process orders or build tasks, not needed in the design: 7 (493, 494, 502, 519 to 522). Nothing is missing from every file.
- PRESENT BUT WRONG (3): D-0490 (part 4 step 14 says the export holds "the original" although the document's own question 15 is open on the publication part; the two parts and the naming from the id are missing); D-0501 (step 7 gives D-0501 as the source of the red line: that is D-0460; "a note appears where the app can follow a silent case" is D-0508, where she ASKED "could we detect those cases"; "silent case" is never explained; her removal of the count of rows removed at the plot is not in the document); D-0510 (question 1 (b) says the step comes after the join "as you wrote": her words say where the JOIN is done, "that would simplify removing of samples by key"; they do not say where the step is written).
- ONLY IN A BUILDERS' FILE, but they change what she sees or exports: D-0489 (the comparison: three layers, no layer 4, the full-row diff only on request), D-0491 (the report: `# Results` before `# Technical`), D-0492 (the reproducibility bundle: "original" and "final_audited", the data stored once, "really clear which is which"), D-0498 and D-0500 (her rule for recipe making; the entity key is the declared key plus a column a join equates with it; a table that only shares the key's name is listed, not ticked), D-0497 (the app features file shown as "Web Demo (web-demo)"). Also only there: 486, 488, 503, 504, 515, 524.
- STALE in the builders' files: D-0488 is MERGED on dev (`d2e92547`); `PARTS_TABLES.md` row V8, `RECIPE_REDESIGN_REVIEW.md` 4.4 and `BUILD_ORDER.md` slice 11 say "not merged".
- Other statements that are wrong, outside those lines: (i) part 5, last paragraph: "The app refuses a session file of an older form, as you decided for the redesign: 'A - best to clean all old sessions' (D-0312)": D-0312 was about sessions that hold "My view"; it does NOT cover a new form after the audit-recipe change; `BUILD_ORDER.md` slice 3 does the same under "NO ANSWER NEEDED": this is a NEEDED DECISION THAT DOES NOT EXIST: it must be put to her as a question; (ii) question 20: "dates were not named": D-0061 names "a date picker"; (iii) the diagram of part 3: "the join with the metadata is always here": D-0523 says "when necesary".

## B. The three reviews
Applied, with these left: "silent case" (lines 80, 112), "Table to view" (first used at line 327) and "z-score" (line 474) are not explained; "Joined tables" as the word for T1 in question 19 is wrong for `MLST` (its tier 1 only cleans it); question 2 (c) "Against: the one move ... waits" is a timing argument (it rests on D-0525: reword as her own order, not as a drawback); questions 11, 12, 15 (c), 16, 17, 19, 20, 23, 24, 25 give no "what you would see" per option (low).
"Reopens:" lines that are incomplete or wrong: question 2 lists D-0306 and D-0063: ADD D-0237, D-0250 ("tier3 in a plot entry") and D-0485 point 3 ("tier 3 = tier 2 plus the entry's own steps"); question 3 (b) lists D-0093 and D-0355: ADD D-0316 and D-0346 (a tick line per place); question 4 (a) says "nothing": D-0199 ("the filter is at T3 and not at T1") is the case it breaks by default: "D-0199 in part"; question 5 (b) says "nothing": D-0501 "the default will need to include the earliest place of each branch": "D-0501 in part"; question 19 (b) and (c) say "nothing": D-0310 (her "B") fixed the choices Source, T1, T2, T3; "Source/T1/T2/T3 (a builder's choice)" is wrong for the CHOICES: only the words on screen were open: "D-0310 in part". True as written: 1 (a), 1 (b) (honest), 6 (b), 9, 14, 15, 17, 21, 24.

## C. The 25 questions
Genuinely open: 1 to 15, 17 to 19, 21 to 25.
- Question 1: still open after D-0523 (that sentence says where the JOIN is, not where an audit step is ticked): agreed. Her sentences are presented fairly, with two leans to remove: "as you wrote" in (b); the recommendation's "the reading in which your reason of D-0510 holds" (her reason, "simplify removing of samples by key", holds in BOTH readings).
- Question 2: open. Option (b) bundles a second choice ("one level of derived tables") into "do you confirm form 3": split it or say it is an extra choice.
- Question 8: the review session's own reading in D-0501 says point 5 (tables that compute across entities) is "settled": mention it.
- Question 16: PARTLY DECIDED: D-0147: "In the export we need to be able to see original and modified plot.": retitle "WHERE does the export show the original plot?" and cite it as decided.
- Question 17: asks only how (right). Question 20: see the D-0061 correction. Question 21: D-0451 and D-0514 lean to (b); said.
The recipe part: the complete example is there and agrees with `libs/utils/src/utils/recipe_spec.yaml` on the three keys checked. Gaps: the example omits `null_values` and `strip`, which are REQUIRED in every source table (it says only "fewer columns, head left out"): say so; "Form 3 is not confirmed (D-0496)" is not said AT the example; the proposal itself lives only in `tmpAI/panel/...` (scratch): by D-0419 no permanent document stays only there: copy it into the study folder or say where it lives.

## The fixes, most important first
1. Part 5 last paragraph and `BUILD_ORDER.md` slice 3: replace the D-0312 justification by: "You decided this once, for sessions that held 'My view' (D-0312). Whether the same holds for this change is not decided." Slice 3 is NOT "no answer needed": it needs this answer. Add it as a question to her (among the ones that block the audit).
2. One line each, in part 4 (step 14 or beside it) and where they belong, for what she decided today and the document for her does not carry: D-0489, D-0491, D-0492, D-0498 with D-0500, D-0497.
3. Step 14: "the reproducibility part holds the original recipe and the audit recipe, each with the data once (D-0490, D-0492); whether the publication part also holds the original is question 15".
4. Step 7: sources "(D-0501, D-0508, D-0460; decided, not built)"; explain "a silent case"; add her decision that the count of rows removed at the plot is removed.
5. Question 1: delete "as you wrote" and the D-0510 quote in (b) (or use her D-0509 words "modiffy at the join"); delete from the recommendation "It is the reading in which your reason of D-0510 holds"; in 6.1 "The original tables stay as read" becomes "the Source view stays as read in both readings".
6. Question 2: complete the Reopens line; split out "one level".
7. The diagram: "a join with the metadata, when needed, is done here and never in another tier (D-0523)".
8. Question 20: "a date picker was decided (D-0061); comparisons on dates were not named".
9. Question 19: cite D-0310; do not call T1 "Joined tables" (use "Cleaned tables" or keep "T1"); Reopens "D-0310 in part".
10. Question 16: retitle; cite D-0147 as decided.
11. Explain "Table to view", "silent case", "z-score" in part 2.
12. Questions 4 (a) and 5 (b): the Reopens lines above. Question 3 (b): add D-0316, D-0346.
13. 7.3: "Form 3 is not confirmed (D-0496)"; say that `null_values` and `strip` are required and left out; the proposal copied into the study folder or its place named.
14. The stale "not merged" for D-0488 in the three builders' files.

## Not checked
The three builders' files line by line (only grepped); any file:line claim; the 27 differences against the code; the proposal file itself; no test, no browser.
