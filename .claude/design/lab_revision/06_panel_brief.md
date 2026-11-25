<!-- copied unchanged on 2026-11-21 from .claude/design/studies/scratch_records_2026-11/panel/lab_step4/BRIEF.md of the main tree (not in git; written 2026-11-21 night, step 4 of TESTLAB-REVIEW-1); the coordinator's brief to the four viewpoints: it asks, it decides nothing -->
# Panel: what the Test Lab should be after its rebuild (step 4 of the Test Lab review; coordinator, 2026-11-21 night)

## The owner's order (her words, `.claude/design/lab_revision/ORDER.md`: READ IT FIRST)
"can do the same task for LAB which will be a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format --- same kind of work low priority if nothing else and lab_revision subdirectory - also a preparation without details"
Same rules as for BLUEPRINT: planning only; the viewpoints propose, she decides; no question goes to her now; a guide that puts the larger decisions first and leaves the details out. The ideas already in the task (extract a pilot recipe, tool-specific recipe, combine recipes) are to be placed in the guide by size of decision. This review builds nothing and decides nothing.

## What to read (main tree, `.claude/design/lab_revision/`)
1. `ORDER.md`.
2. `04_what_test_lab_must_be.md`: sections 2, 4, 6 and "To decide" (the five journeys and their files, the tools, the decided rules respected or broken, who the Test Lab is for).
3. `05_three_ideas.md`: section 5 and "To decide" (the three ideas; no source says what they mean, the readings are the review's).
4. `02_planned_vs_existing.md`: the contradictions (section K) and the open choices (section M), as needed.
Only if needed: `03_parked_items_and_known_gaps.md`, `prior_work/`, and for comparison `.claude/design/blueprint_revision/GUIDE.md`.
Do not redo the reading recorded there. A small read-only check is allowed where your proposal depends on a fact (give file:line or the command). Never read `tmp.md`. Do not edit the repository; scratch only under `.claude/design/studies/scratch_records_2026-11/panel/lab_step4/`.

## DECIDED (do not reopen; flag a proposal that reconsiders one). Read the ledger line (`.claude/knowledge/decision_ledger.md`) before you rely on a number.
The recipe format 1; the sample id is a string or a categorical, never a number (D-0225); keys are declared in the recipe, not guessed (D-0082); no silent error (D-0050); full recipe edit exists only in BLUEPRINT (D-0102); a recipe file name is `name_date` and an overwrite control exists only in the user's own directory (D-0390, D-0394; the places study is open, `.claude/design/studies/scratch_records_2026-11/panel/recipe_places/TABLE_FOR_THE_OWNER.md`); user spaces are independent and hand-offs are files; science is transparent and reproducible (every seed that is used is written down); the tool informs and the user chooses; ADR-084 (Test Lab tools are stateless; single-key reconciliation; the bootstrapper writes boilerplate only); ADR-097 point 8 (anonymise before data reaches the app; the key kept outside).

## The question
Her description is "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format". Today (from the review; read from code and small runs, nothing seen in a browser): each of the five Test Lab journeys ends with a file that the next user space mostly cannot open; three decided rules are broken by what the Test Lab writes (a numeric sample id, a key guessed from the column name, silent changes); synthetic data cannot be reproduced (no seed, no record of settings); the Test Lab is shown only in the developer and qa setups.
What should the Test Lab be after the rebuild: which tools, for whom, and what must every file it writes carry, so that a user can take it into BLUEPRINT or HOME without guessing and get the same result again? Where do the three recipe ideas (pilot, tool-specific, combine) belong?

Compare these approaches for the Test Lab as a whole (you may add one, or combine):
- A. A small, safe toolbox for every user: reformatting, anonymisation and reproducible synthetic data, each writing a file plus a record of its settings and seed; shown in the scientist setups; recipe-making (the scaffold, ideas 1 and 3) moves to BLUEPRINT or to scripts.
- B. A file-preparation companion to a chosen recipe: the user picks a recipe; the Test Lab checks or reshapes files against its declared fields, makes synthetic data from those fields with planted errors, and reconciles ids on its keys. This reverses the choice of 2026-11-08 that the Test Lab does not read a recipe.
- C. Keep today's tools, fix the defects, make the hand-offs work: the scaffold writes a loadable recipe with a first plot through the existing recipe factory; the ZIP goes to the user's own recipe place; still developer-only, flags decided per tool; the three ideas deferred.
- D. The Test Lab as the recipe starter: scaffold, tool-specific recipes from per-tool fragments, format detection, extraction of a pilot recipe; it reports what recipes share, and BLUEPRINT edits.

For each approach say, from your viewpoint: what the user sees and leaves with in each journey; what exists, must be extended or is missing (source); pros, cons, pitfalls, and what would change a result silently or hide a step; what it asks of BLUEPRINT and HOME (hand-offs by file); the larger decisions it needs first, ranked; what can wait. Then recommend ONE approach or combination, say why, and say what you could not verify.

## Each viewpoint's own weight
- Scientist and data scientist: is synthetic data a valid test of a recipe (what planted errors prove and do not prove; reproducibility); id reconciliation on messy ids (false matches, a cleaning step that breaks ids that matched, fuzzy thresholds); anonymisation (is a hash of an id anonymous; where the key lives; the way back); type inference from a sample (ids as numbers, dates, decimals with a comma); what a user can defend in a methods section.
- Architect: boundaries (libs without Shiny; `test_lab`, `id_reconciliation`, `utils`; what belongs to BLUEPRINT), one way per job (several recipe writers, Excel paths and synthetic generators exist today), one source of truth for the format a file must have (the recipe's declared fields and the checker), testability, which ADRs and rules each approach would amend (ADR-084, ADR-097, `rules_test_lab.md`).
- Developer: effort, risk, test cost, build order in small working parts, what can run in parallel, what of today's code can be kept. Her rule: build time is no argument against an option and delay is fine; give effort and risk as facts for ordering.
- User who is not a developer: is what each tool did shown in plain words at the moment of the choice; what frightens or misleads (the key in the same ZIP as the anonymised table; "open the ZIP in BLUEPRINT"); the words on screen; what the user must know to take the file to the next space.

## What to return
Save your full text as `.claude/design/studies/scratch_records_2026-11/panel/lab_step4/<viewpoint>.md` if you can write there (a shell redirect), else return it in full. Plain short sentences, tables for comparisons, as long as needed to be clear, no padding. Start with a 6-line summary; end with "To decide first (ranked)" and "Not verified". Name the Test Lab and the tool concerned in every finding.
