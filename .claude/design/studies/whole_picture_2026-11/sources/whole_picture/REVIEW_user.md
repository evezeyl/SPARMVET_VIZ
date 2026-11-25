# Review of WHOLE_PICTURE.md by a reader in the owner's place (2026-11-22)

VERDICT: NEEDS REWORDING. Section 1 has the right story but is not readable alone in ten minutes. Section 0 is a dense list of ledger numbers and flags that need terms not yet explained.

## The three most important changes
1. Every term in plain words BEFORE its first use; cut the (D-xxxx) strings out of the sentences of sections 0 and 1: at most one number in brackets after a complete plain sentence.
2. Section 0: three or four plain consequences, each in about three sentences: "what you see today / what you decided / what the difference is". Flags 6 to 9 and the long run details move to section 3 or 4.
3. Each question of section 5 self-contained: the situation in one sentence; what the app does today in one sentence; the options with what she would SEE; then a separate line "Recommendation (mine):". No recommendation that rests on code convenience; no wording that decides for her.

## Sections 0 and 1
- Used before explained: tier, T1, T3, lineage, propagation, place, walk, audit recipe, audit copy, fork, key, entity key, anchor, node, reach, tick line, hash, slice, "the library", "held branch", "run", "reading". Flag 1 uses "T3", "tick lines", "the earliest place" with no gloss; flag 2 uses "tier 1" before section 1 explains it; flag 4 uses "fork of a join", "audit log", "audit record".
- Section 0 "how to read" is a ledger bibliography; the evidence labels ("[collected]", "run", "as built", "read by me", "reading") are not her vocabulary. Say: "Where I only read a file and did not run it, I say so."
- Sentences far over 25 words: flag 2 (about 70), flag 3 (about 55), flag 4 (about 60); section 1 "Three kinds of table" (about 80); story step 2 (about 60); audit step 3 (about 150, a paragraph in one sentence); audit steps 5 and 8; the first sentence of "Looking (Exploration)".
- In the audit steps 1 to 8 of section 1 there are 5 to 12 ledger numbers per step: unreadable as prose.
- Code names with no meaning given: `is_entity_key`, `audit_steps`, `audit_comment`, `1_test_data_ST22_dummy`, `ST22_Anchor`, `miaou`, `qc_reads_horizontal_barplot`. Say "a plot called miaou, which draws the source".
- "Tier" is never explained. Needed once: tier 1 = clean each file and join it with the metadata; tier 2 = compute; tier 3 = steps that belong to one plot.

## The story
- The data story (steps 1 to 5) mostly reads as a story; step 2 is three facts in one sentence; it does not say what the user SEES at each stage.
- The audit story jumps: step 1 has no scene (what did she see in the figure that made her act?); steps 3 and 4 jump from the dialog to the list of places to "remove from all the data".
- The paragraph "A big join tells the same story with more branches" (four table names in one sentence): cut from section 1 or move to section 2.
- Fix: one sentence per step, one picture per stage, no D-numbers inside. Section 1 should have ONE diagram: original file, tier 1 (with the metadata joined), tier 2, tier 3, figure; and one sketch of the audit dialog.
- A recommendation sits INSIDE the story (audit step 3: "my recommendation is the end of tier 1 ..."): move it to question 1.

## Section 5, question by question
- Q1 (earliest place): the only question that blocks the start. Uses unexplained words. "Against (a): the place of the metadata join plays no role" is not something she sees. "Against (b): more steps (13 or 19 against 2 or 11)" is partly a cost argument. Missing: what she would SEE (how many lines ticked, the words beside them). The recommendation is argued from "the only reading in which your rule does what you said": it decides for her by her own words; say "It matches what you wrote; you may have meant otherwise."
- Q2: option (a) states a review finding as a fact; (b) and (c) cannot be pictured without a sketch of the dialog with each option.
- Q3: add the actual line she would see for each option; "your meaning of 0" is a reference she cannot check.
- Q4: "one of your three gotchas" unexplained; "ignores upper and lower case" needs one example.
- Q5: the illustration `{note: left_join_keeps_first_table, ...}` is code. Reword: "The audit log keeps what the user was shown. Should it keep the sentence exactly as shown, the facts behind it (which table, which numbers), or both?"
- Q6: option (c) states a consequence as a rule.
- Q7: mixes two questions (the recipe; the original plot): split, or she cannot say yes to one and no to the other. The recommendation hides that one of the decisions it names is not met.
- Q8: fine and honest.
- Q9: not answerable alone: "form 3, form 4, form 5" are names with no picture. Show each as a short recipe snippet or three plain sentences.
- Q10, Q11, Q13: small and answerable; Q11 uses "Source, T1, T2, T3" without plain words; Q10 recommends "(a) as built": a builder's default carried as a recommendation: say what she would see.
- Q12: "Reshuffle" and "seed" unexplained; the recommended option has no reason given.
- Q14: gloss "tier"; remove "code S07 and J14".
- Q15: reword: "If a look-up table has an entity key column, should the check tell the recipe maker it may be in the wrong block?"
- Several recommendations cite "the review" or "the panel" as authority: she did not choose those. The "Blocks:" lines say "slice 4": say "what cannot be built until you answer".
- Not self-contained as written: Q1, Q2, Q3, Q4, Q5, Q7, Q9, Q14, Q15. Q2 to Q4 depend on the answer to Q1: say so and give the text for each answer. Questions that refer to "your words of D-xxxx" must QUOTE the words.

## Misleading or reproachful
- Flag 2 and Q1 (b): "your case works as you described it" sounds proven: it is one run on one entity; say so.
- Flag 8 reads as a reproach: say "Today the app warns and opens it. You decided it should refuse."
- "Your words support both" can be read as "you contradicted yourself": say "Your two sentences can be read in two ways."
- "Sample" as a general word: flag 2, flag 3, Q1, Q3, 3.10. In general statements "the entity"; on the demo "a sample (the entity of the demo)".
- Cost in arguments: Q1 "the fewest steps", "more steps".

## Length and order
- Sections 3 (3.1 to 3.19), 4.1's table and long paragraph, 4.9, 4.12, 4.13, "examined and dropped", section 2 (it repeats the tables file and section 3), section 6 (build order) and section 7: move to the tables file or a separate file for the builder; keep in the main document two lines on what was not checked ("nobody ran a browser; no screen was seen").
- Repeated: the two readings of "the earliest place" (flag 2, story step 3, 4.1, Q1); the three forms of an audit step (flag 4, 2.6, 3.8, 3.13); the data-agnostic definition (three places).
- Move up: right after section 1, the short list of the questions she must decide first (Q1, Q2, Q3, Q7, Q9); Q10 to Q15 as an annex.

## Plainer wordings offered (meaning kept)
1. Flag 2: "You told me where a removal should be written by default. Your two sentences can be read in two ways. Reading A: in the first cleaning stage of each original file. Reading B: in the first cleaning stage of each table that joins the metadata. On the demo they give different results. Question 1 asks you to choose."
2. Flag 3: "The app cannot say, by reading the recipe, what happens in a table where no step is written. Two checks said 'the entity stays there' and were wrong. Only a real run gives the true answer."
3. Flag 4: "An audit step is stored in three different ways in the code. The way you decided is not the one the screen uses. The export uses an older way. So the export has no original recipe, no audit log and no audit record, which you asked for."
4. Three kinds of table: "A recipe has three blocks. Each block holds one kind of table. 1. The metadata: what we know about each entity (on the demo: source, year, country of each sample). 2. The data tables: analysis results for the entities (on the demo: MLST, FastP, ResFinder). 3. The look-up tables: lists used in later joins (on the demo: the list of virulence genes). You decided that VirulenceFinder belongs to the second kind. It is not moved yet."
5. Story step 2: "Tier 1 cleans each table. Then, still in tier 1, a table is joined with the metadata. On the demo, MLST keeps three columns; then MLST and the metadata are joined on sample_id into MLST_with_metadata. You decided that a join with the metadata is always done in tier 1."
6. Audit step 3, as five sentences: "The dialog lists the tables where the step can be written. Each has a tick box. The first tables are ticked by default. For each ticked table the dialog shows the number of rows concerned and which plots change. It does not warn about what happens further down the chain."
7. Audit step 5: "When she confirms, the step is written into a copy of the recipe, called the audit recipe. The original recipe is never changed. Her reason is saved with the step. Only the tables that change are run again."
8. Flag 1: "Today an audit step can only be written for the table of the open plot. You decided it should be possible at every stage. The dialog with tick boxes for places does not exist on screen yet."
9. 3.3: "The library contains three warnings: 'may stay', 'may differ', 'stays by your choice'. On the demo they were all wrong. You said you do not want warnings about tables further down. They should be removed."

## Not judged
Only the main document was read (and 30 lines of the tables file). No ledger number, file:line or run result was checked. No screen exists, so "what she would see" is described, not shown.
