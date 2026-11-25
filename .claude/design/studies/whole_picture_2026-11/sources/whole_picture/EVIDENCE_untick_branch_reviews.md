# Evidence for the whole-picture design: what two reviews of the untick branch found (2026-11-22)

Branch `task/remove-from-all-ticked` (worktree `../SPARMVET_VIZ_wt_remove_ticked`, commits `07b8a9f1`, `95b6285e`). ON HOLD by the owner's order (ledger D-0507): reviewed, NOT merged, not fixed further. Probes: that worktree's `tmpAI/review2/`.

## What holds (verified by runs)
- `apply(..., ticked=...)` writes the removal only at the ticked places (127 subsets of a test recipe; the demo). A place not offered is refused, nothing written. All ticked = byte-identical to before. Full headless suite on `07b8a9f1`: 14500 passed, 0 failed.
- A table that only shares the key's name is listed, unticked, tickable (D-0498).

## What does NOT hold: a statement about a table where NO step is written cannot be read from the recipe
The library tried to say, for each table the user unticked, whether the sample "stays" or is "removed upstream", by reading the join kinds of the recipe (`_flow`, `libs/utils/src/utils/remove_from_all.py:455-466` on that branch). Two reviews found false statements each time:
1. First version (`stays_by_choice`): every unticked table was told "stays". False whenever the table is built from a ticked table. Demo, real engine: untick `FastP_with_metadata` alone: told "stays", the sample is gone. 64 of 315 statements false on a test recipe.
2. Second version (three kinds: stays, removed upstream, cannot say):
   - FALSE "stays" on the demo with the real engine: untick `ST22_Anchor` and `metadata_schema`, everything else ticked. `ST22_Anchor` = `metadata_schema` left-joined with FastP, ResFinder, MLST, VirulenceFinder, then an INNER join on `VF_gene` against a whitelist (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:26-35`). Told "stays"; the two samples are gone (2 rows before, 0 after): the later step drops rows by a column that came from a ticked table. Same on a small recipe: a left join, then a filter on a joined column.
   - FALSE "removed upstream": an inner join on a column that is not the sample key: told "gone here too", the sample is still there.
   - It was a SECOND reading of joins beside the lineage walk's (`libs/utils/src/utils/step_effects.py:57-73`: left, inner, semi followed; anti, right, full, cross not yet), with its own strings and another default.
3. The tests could not see either: no test compared a statement with the data for a recipe that has a row-dropping step after a join.

## What it means for the design (facts, not a decision)
- A recipe can only be READ for where a step is WRITTEN and what it removes THERE. What happens in a later table depends on every step after it; only a RUN of the candidate recipe can say it truthfully (a measured count), and then only for values that are not rewritten.
- This agrees with the owner's words of the same day (D-0508): "Id rather the check is more where you apply it - knowing it will affect the downward recipe than actually trying to capture the removal of something that by default should not exist"; "the user will have to learn that its not the sample that stays but where the change is applied".
- The reviewers' options, not decided: say "cannot say" for any table with a later row-dropping step (honest, but most demo tables); or a measured recount instead of a reading; or say nothing about tables where no step is written, and show the propagation (original, T1, T2) so that the user sees what a step affects.
- Her case "keep the poor quality sample in the quality results" (D-0499) needs a true answer to "where does the sample stay": to be designed with the above.
