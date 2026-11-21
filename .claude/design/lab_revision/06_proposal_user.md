<!-- copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/user.md of the main tree (not in git; written 2026-11-21 night, step 4 of TESTLAB-REVIEW-1); a viewpoint's proposal: it recommends, it decides nothing -->
# Test Lab after its rebuild, step 4: viewpoint of the user who is not a developer (panel-user, 2026-11-21 night; filed by the coordinator from its report; read from the review files, nothing seen on a screen)

References: `04` = `.claude/design/lab_revision/04_what_test_lab_must_be.md`; `H` = `app/handlers/test_lab_handlers.py`; J1 to J5 = the five journeys of `04`.

## Summary
1. Recommended: A, with one addition: every file a Test Lab tool writes comes with a plain-text record, in the download, of what was done.
2. A fits "utilities for the user" (ORDER.md). It removes the two worst traps: the recipe ZIP nobody can open, and synthetic data nobody can make again.
3. B is what a scientist most wants ("is my file right for my recipe?"). It reverses the 2026-11-08 choice, so it comes only as a later, flagged step. The owner decides.
4. C and D keep the Test Lab developer-only, or make it a recipe writer. D asks the user to understand recipe building before they can use a "utility".
5. The ideas: tool-specific is small, pilot is medium, combine is large. In the Test Lab, at most report what recipes share; BLUEPRINT edits (D-0102).
6. Nothing was seen in a browser. All screen statements come from `04`.

## What the user sees and does not know today (`04`)
- J5, Test Lab scaffold: the status line says "Download the ZIP and open in BLUEPRINT to continue" (`H:509-510`). The user cannot do that. BLUEPRINT takes one `.yaml`, and the engine refuses a recipe with no plot. The user thinks they made a recipe and they did not.
- J4, Test Lab anonymisation: the key column is renamed `anon_<column>` and the mapping sits in the same ZIP. The user does not see either fact. Many users will mail that ZIP.
- J3, Test Lab id reconciliation: the cleaning step breaks ids that already matched. Fuzzy matches are dropped, and the screen does not say so.
- J2, Test Lab synthetic data: the user cannot make the file again, and no list of planted errors comes with it.
- J1, Test Lab reformatting: the delimiter is guessed and no row count is shown.

## One sentence and one picture
- A: "A small set of tools; each gives you a file and a note of what was done." Picture: file plus note.
- B: "Pick your recipe, and the tools adapt to it." Picture: recipe, then files. Clear, but the user must trust the check.
- C: needs two sentences: "same tools, repaired, still for developers."
- D: "The Test Lab starts your recipe." Too much for a utility.

| Option | User understands | Stays hidden | Risk of a wrong choice |
|---|---|---|---|
| A | file plus record; safe tools | that BLUEPRINT now makes recipes | low |
| B | "my file fits my recipe" | the rule used (types, missing-value words); a pass may be read as "science is right" | medium: false comfort |
| C | nothing new | scientists still see no Test Lab | low, but half a fix |
| D | "recipe starter" | joins and keys chosen for them (D-0082, D-0225) | high |

## Words the screens must carry (suggested, to adapt, not decided)
- Every download: "This ZIP contains your file and `what_was_done.txt`: tool, date, your file name, settings and seed. Keep both. With the same file and settings you get the same result."
- Synthetic data, seed box: "Seed: 4711. Write it down. The same seed and settings give the same file."
- Planted errors, in the note: "Planted on purpose: 12 missing values in column X, 3 duplicate ids. A recipe that handles these has passed this test. It has not been tested on your real data."
- Anonymisation: "The key file lets anyone restore the real ids. Do not share it with the anonymised table. Store it elsewhere." (ADR-097 point 8.) Also: "Column `sample_id` is now `anon_sample_id`."
- Reconciliation: "142 ids matched exactly, 9 by fuzzy match (not written as steps), 3 not matched."
- Scaffold, if kept: "This is a starting draft. You must choose which column identifies a sample." No guessed key.
- Remove "open the ZIP in BLUEPRINT" until BLUEPRINT can open it.
- Jargon to drop from screens: "tier-1", "scaffold", "reconcile". Say "draft recipe", "match ids".

Would users click through a warning? Yes, the ZIP warning, unless the key file is a separate download. Suggestion: two downloads, not a stronger warning.

## What A asks of BLUEPRINT and HOME
- BLUEPRINT: accept a draft recipe; the empty-draft decision at `tasks.md:220` is shared with it.
- HOME: Data Import already takes a TSV. A renamed key column will be refused (unverified).

## The three ideas, from the user's seat
- Tool-specific recipe (small): "start from ResFinder's known fields." A documented chain or a template.
- Pilot recipe (medium): "give me only the plot I need." This belongs in BLUEPRINT, next to branching.
- Combine (large): wait. A Test Lab report ("these two recipes share table MLST; plot id X clashes") informs without choosing for the user.

What can wait: several tables from one set of ids, dates in synthetic data, the other four error kinds, the extractor.

## To decide first (ranked)
1. Who sees the Test Lab: scientist setups, one flag per tool, or developer-only (`04` To decide 1).
2. What every file carries (the record and the seed) (`04` To decide 3).
3. Whether the scaffold stays in the Test Lab, and how a draft opens (`04` To decide 4 and 5).
4. Whether "correct format" means a TSV only or a recipe's declared fields (this reverses the 2026-11-08 choice).
5. Where the anonymisation key goes.
6. Which of the three ideas are wanted.

## Not verified
Anything on screen. What Data Import does with a renamed key column, a stress file or an Excel number type (`04` V2 to V5). Whether the anonymiser writes the user's file name or Shiny's upload number (`04` V6). Whether a scientist can follow the proposed words: they need a test with a real user.
