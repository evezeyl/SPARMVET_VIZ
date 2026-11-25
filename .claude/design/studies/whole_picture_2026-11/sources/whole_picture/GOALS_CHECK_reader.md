# Reader in the owner's place: part 0 and questions 28, 29, 17, 4 of WHOLE_PICTURE.md (branch study/whole-picture-goals, 1f82f3d3), 2026-11-22

Line numbers refer to `.claude/design/studies/whole_picture_2026-11/WHOLE_PICTURE.md` in the worktree `../SPARMVET_VIZ_wt_goals`.

## The five most important changes
1. Part 0 has no "is each goal reached" table. The yes/partly/no marks exist only in GOALS_REVIEW.md:70-110, written as conditions; "Today: no" never says what the user would see (lines 74, 90). Add to part 0 one row per goal G1-G6: "today you see ..." / "after the change you see ..."; say what "partly" means in screens.
2. "How to get there" is the user's path only (0.3). The route of the work is one line (line 94, bare slice numbers). Add a short ordered list of work steps; each says what she can then do on the demo. Point to GOALS_REVIEW 4.11 (the December demo) from the text.
3. Part 0.4 (ii), "the code on dev", is in builders' language ("libraries", "audit nodes applied in memory", "the join fork of the reproducibility bundle", "the drop gate", "t3_steps.yaml", "the load gate"). For each item say what she sees today and what she will see. Say how each ok/adjust/replace/remove claim was checked (part 9, line 960, says part 0 ran nothing new, yet 0.4 reads as fact). 0.4 (iii) "Need not be touched" is not marked as verified or reasoned.
4. Ledger strings and unexplained pointers: lines 90-91, 98, 100 hold 5-8 D-numbers inside sentences. "your case of D-0499" (lines 54, 83, 328, 565) is never said in plain words in part 0: write "keep the entity in the quality plots only". "Reading B" (line 83) and "tier 1" (lines 83, 189) are used before they are explained (line 147; 6.1). "block M593", "the review session", "slices", "the builders" are never explained.
5. Wording that decides for her or reads as reproach: line 576 argues (a) with her own words ("It follows from your passage"); line 572 argues against (b) with her sentence "the user will have to learn a bit of datascience"; line 750 argues (b) with "your two use cases"; line 112 uses her sentence about "complicating" against the decided design; line 106 ("it does not") reads as "your decision was wrong"; line 566 "what is shown is measured, so it cannot be false": the dialog does not exist and the evidence is 3 runs of one entity each.

## Plainer wording offered (meaning kept)
- Line 47: "You say what to remove: one entity, or the rows that meet a condition. You say from which results, and why. The app decides where in the recipe the step goes. Only one case needs you: a step that uses all the observations, such as a mean. Removing an entity before it changes the values of the others; after it, it does not. There you say before or after. Before you confirm, the app shows what the step did to each result."
- Line 106 (last two sentences): "On the demo, if the step is written at the first table, the removed entity still shows in 3 plots, with empty source and country. We saw this in 3 runs, one entity each. Without your 'tick low' choice, the step would go after the join."
- Line 83: "This dialog does not exist yet. 'n' is the number the app will count. On the demo, a step written after the join with the metadata keeps the entity only in the plots you unticked, and its metadata stays."
- Line 98: "Four pieces of code built this month are run only by tests, and no screen reaches them. They follow a table back to its sources, make the audit recipe, run it, and compare two tables. They must be connected to HOME."
- Line 112: "A small correction of observations needs less than points 1 to 4 describe. This is my reading, not a test."

## 1. Can she read part 0 alone in about ten minutes?
(a) How to get there: the user path is clear; the route of the work is missing. (b) What must be modified: lists exist, in builders' words, no "what you will see". (c) What hinders (0.5): clear; point 5 labelled "a builders' strategy, not yours": good. (d) Her questions (0.6): one line each, not self-contained; "Question 4 (in results)" hard to understand; line 120 words Q4 differently from line 739; she must go to part 8 (line 531). 2,300 words at this density is more than ten minutes; goals E1-E7 could be one line each.

## 2. Words and sentences
Used before explained: tier 1 (83); lineage (92), place (105), reach; seed, Reshuffle (91, 98, 100, 109; first explained 946); tick low (91, 105); n removed (64); polars_select (583); the check of key drops (586); audit nodes, the drop gate, the join fork (100); QA_population_zscore (76). Sentences over 25 words: 47, 83 (third), 100, 106, 111, 112.

## 3. Questions
Q28 (560-576): has situation, today, question, options with "What you would see", separate recommendation, option (c) neither. Not self-contained: sends her to the sketches of part 0.3 and part 3 (570): show the two screens side by side. Hides one difference: under (a) she is asked "before or after"; under (b) never (GOALS_REVIEW 103): say so. "Against" of (a) is weak: write "You cannot say: write this step at this table". "One question replaces nine" (566) is an effort argument: remove. "Reopens: nothing" for (b) with "For: it is the design you decided" appeals to the old decision.
Q29 (578-593): no "neither" option. "Today" (580) unreadable ("where the check of a key column can refuse nothing"): say what she sees. "Reopens" is a string of five D-numbers. Recommendation "(a)." has no reason.
Q17 (944-953): options (a), (b) have no "What you would see"; (b) is "my idea, not studied". No "neither". Recommendation (c) at 953 contradicts line 603 ("Questions 15, 17, 26 and 27 have no recommendation"). Line 951 gives file names to a non-developer. (c) "harder to trust": reasoning not shown.
Q4 (736-752): no "neither"; (c) has no "What you would see"; options written in places, line 752 rewrites in results: she must translate. Depends on questions 1 and 3, which may dissolve under 28(a). Recommendation (b) "because it follows both of your use cases" uses her words as the argument.

## 4. Sketch (61-81)
She can picture it; demo values. Unclear: "One line per result and per exported table [ All the data ]"; the radio buttons "before / after" are empty and it is not said that Confirm stays blocked until she answers (step 6: "No default"); the lines promised in step 7 ("still found here", "the values of other observations change here") do not appear; "Written at: end of tier 1 of each table that joins the metadata" is jargon and presumes reading B of question 1, which is open; the text under the sketch is opaque.

## 5. Reproach and "proven" claims
Lines 106, 110, 112. Line 110 "all were false somewhere" rests on two reviews. Line 105 "evidence for a reviewer, not a warning": a design opinion stated as fact. Line 83 "no metadata is emptied": one demo run with places listed by hand. Line 106 stated as fact, not marked as 3 runs.

## Not judged
Parts 1-7 and part 8 outside Q28/29/17/4; accuracy of code or ledger claims; the rest of GOALS_REVIEW.md.
