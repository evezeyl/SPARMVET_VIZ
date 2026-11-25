# Opus check of SONNET_review_2.md, Part B (drafts B1 to B4), case D-0573 to D-0579 (2026-11-23)

Reading only. "draft N" = line N of `SONNET_review_2.md`.

**Checked and right:**
- Her words of M629 to M635: every long quote is exact (fixed-string searches against the blocks, including the 1023-byte quote of M629 and the 629-byte quote of M630). The relay "I would lean also to add this in the recipe" is indeed not in the evidence of D-0574.
- B1.1: each of the 11 anchors is found exactly once in the committed `CAUSE_AND_SOLUTIONS_ZEROS.md`. The replacement texts are the signed R2, R4 to R11, R13 and R14 of `OPUS_checks_b6_v1.md`; R13 adds only the D-0573 name.
- The code facts (`session_manager.py`, `orchestrator.py`, `bootloader.py`, `recipe_check.py`, `data_wrangler.py:92`); the TODAY / TO BUILD split; the log options; the typo argument for the order.
- I accept its A3: in her words the FORM of the block (option i or ii) is not decided. My position over-read D-0574.

## Replacements (old → new)

**S1. draft 326** (her quote not exact: her text has " - " before "does"; naming by content is the review session's reading).
Old: `| The two directions of the check, named by content | "there are 2 directions in the test ... what is test 1 and test 2 does not really mater" | D-0579 |`
New: `| The two directions of the check; the numbering does not matter (naming them X and Y by content is the review session's reading) | "there are 2 directions in the test"; "what is test 1 and test 2 - does not really mater" | D-0579 |`

**S2. Ellipses inserted into her quotes** (her own texts use "...").
- a. draft 325: `(at the id level only ...)"` → `(at the id level only - there can be true metadata that is missing but not in the id)"`
- b. draft 328: `"A user confirm is good ... noted in the log"` → `"A user confirm is good"; "noted in the log"`
- c. draft 517: the same change as (a).

**S3. draft 346** (the position is her open question 7).
Old: ``the block, the completion after `_read_source` and before the author's steps, a new edge``
New: ``the block, the completion after `_read_source` (before or after the author's tier-1 steps: question 7), a new edge``

**S4. draft 368** (answers question 2 for her, on a basis G4 does not give).
Old: `the entity id of the metadata is also the key of its table (G4), so a repeat is an error at the id level.`
New: `whether a repeat is an error at the id level is her question 2: her approved sentence (D-0567, G4) allows a repeated id in a long table, and nothing yet says that the metadata has one row per entity.`

**S5. draft 411** (my lean, exact).
Old: `(Opus to check.)`
New: `**Lean of the Opus agent, as a lean:** (b) as well: it keeps her D-0569 (X informs) and her order (Y waits for X), so nothing is confirmed, completed or logged on a list that the fix of the metadata will change (the typo case); (a) is the more literal reading of "stopping first" and closes the recipe where no one can fix the metadata.`

**S6. draft 457** (question 1).
Old: `Lean (Sonnet): (b). Neither: say what you meant.`
New: `Lean (Sonnet and Opus): (b). Neither: say what you meant.`

**S7. draft 463** (question 4: what she would see under (b) was wrong for the demo, whose `QA_AMR_per_sample` starts from the metadata; and my lean).
Old: `(b) ResFinder has 70 lines and the plot counts 38 samples, with the note;`
New: ``(b) ResFinder has 70 lines; the plot shows what today's recipe shows (42 samples, 4 in the bar at 0, because `QA_AMR_per_sample` starts from the metadata; 38 samples where a join starts from ResFinder), with the note;``
Old: `No lean: each closes something. Neither: say what you meant.`
New: `Lean (Opus): (b): nothing is added that the user did not accept, and no one is locked out; the standing note must also say that where a join starts from the metadata the entities with no line may show as 0. Sonnet: no lean, each closes something. Neither: say what you meant.`

**S8. draft 473** (question 9: "stored where" is answered by her words "kept in the session log").
Old: `**Question 9. Once per data batch: stored where?** Your words: "once per data batch (as recalled by session ?)".`
New: `**Question 9. Once per data batch: what asks again, and where there is no session.** Your words: "once per data batch (as recalled by session ?)" and "confirmation and what as added is kept in the session log".`
Old: `Lean: in the session, under the session key. Neither: say what you meant.`
New: `Two points are yours: should an edit of the recipe (not of the data) ask again, as the session key makes it today; and where does the acceptance go in a deployment with no session. Lean (both): the session key as it is (an edit may change the stated meaning); with no session, a confirmation at each opening recorded in the export. Neither: say what you meant.`

**S9. draft 291** (count).
Old: `four new questions came.`
New: `nine new questions came (1, 2, 3, 4, 6, 9, 10, 11 and 13 of the new list; question 2 holds the old question 9).`

**S10. draft 521** (the same point as S4).
Old: `a repeated id may be an error at the id level, and the entity id of the metadata is also the key of its table [ESTABLISHED: RECIPES G4]. Refuse or note: her question 2 of the new list.`
New: `a repeated id may be an error at the id level (her question 2 of the new list: refuse or note); her approved sentence (D-0567, RECIPES G4) allows a repeated id in a long table, and nothing yet says that the metadata has one row per entity.`

**S11. draft 527.**
Old: `**Not yet seen by the Opus agent.**`
New: `Checked by the Opus agent (\`OPUS_checks_review_v1.md\`).`

**S12. draft 538** (the seat of the refusal is her question 3).
Old: `| **refuses** the metadata; the old file stays; the loop: correct and upload again |`
New: `| **refuses** the metadata (where: at the opening, in Data Import, or both: question 3); the loop: correct and upload again |`

**S13. draft 540** (what happens without a confirmation is her question 4).
Old: `completes only after the confirmation |`
New: `completes after the confirmation (without one: question 4) |`

**S14. draft 546** (the example is wrong: in `demo_abromics` the step is in the join's tier 1, and the metadata's own tier 1 is empty; "must" is the agents' proposal).
Old: ``(2) The read must be of the metadata AS READ (before its tier 1): a tier-1 step such as `polars_drop_nulls` on `sample_id` in `demo_abromics.yaml:44-47` would hide the error from a check run after tier 1.``
New: ``(2) The agents propose to check the metadata as read (before its tier 1): a step in the metadata's own tier 1 (for example a `polars_drop_nulls` on the id) would hide the error from a check run after it. In `demo_abromics` that step is in its join's tier 1 (`demo_abromics.yaml:44-47`; the metadata's own tier 1 is empty, `:30-31`), so it would not hide it.``

**S15. draft 635** ((ii) is still hers, narrower).
Old: `(viii), (i), (vii), (vi), (v), and narrower (iii) and (iv).`
New: `(viii), (i), (vii), (vi), (v), and narrower (ii), (iii) and (iv).`

**S16. draft 660.**
Old: `Her new decisions touch four of them.`
New: `Her new decisions touch five of them (Q1, Q3, Q5, Q6, Q7).`

**S17. draft 670** (consistency with (iii), which is only partly settled).
Old: `The entity key: SETTLED, the recipes declare their ids and the block needs a declared id`
New: `The entity key: CHANGED, partly settled: the shipped recipes declare their ids (D-0569) and the block needs a declared id (D-0574); whether the format requires it is the recipes file's (iii) and the new question 6`

**S18. draft 477** (question 11).
Old: `Lean (Sonnet): (a). Neither: say what you meant.`
New: `Lean (Sonnet and Opus): (a). Neither: say what you meant.`

**Leans on the other questions:** Opus agrees with the leans as written for questions 2, 3, 5, 6, 7, 8, 10, 12 and 13.

## Closing

I sign the drafts with these replacements applied.
