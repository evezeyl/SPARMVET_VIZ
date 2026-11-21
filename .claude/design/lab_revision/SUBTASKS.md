# TESTLAB-REVIEW-1: subtasks (so the work can be parked and resumed)

Parent task: `TESTLAB-REVIEW-1` in `.claude/tasks/tasks.md` (D-0396: "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)"). Order and its addition: `ORDER.md` (same folder).
This file is kept current by whoever works on the review. It builds nothing and decides nothing.
States: done / in work / parked / next.

**Where the steps come from.** The order has her words and the relaying session's text; they are kept apart here.
- Her words (`ORDER.md`): "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format --- same kind of work low priority if nothing else and lab_revision subdirectory - also a preparation without details"; and (M423) "yes it will have to explore what we had planned, what is existing, many things will need to be anyway verified and updated --- ... he can make subtasks for himself so if he starts and needs to park those he can resume later".
- The relaying session's text (not her words): use the panel viewpoints to propose; a guide that puts the larger decisions and questions first and leaves the details out; outputs: the guide, one file per viewpoint with pros and cons, a progress note; the three ideas of the task (extract a pilot recipe, a tool-specific recipe, combine recipes) "are to be placed in the guide by size of decision".
- "Same kind of work" points to the BLUEPRINT review (`../blueprint_revision/`), whose order has steps; steps 2 and 3 below are proposed by analogy where the Test Lab order names none.

| # | Step | From | State | Files it produces | Notes |
|---|---|---|---|---|---|
| 1 | Explore what was PLANNED for the Test Lab against what EXISTS, and note what must be verified and updated; parked items and gaps | her words (M423) | done (2026-11-21, worker run; commits `dcb4a7f4`, `44f4032a`, `b0bfc564`) | `01_sources.md`, `02_planned_vs_existing.md`, `03_parked_items_and_known_gaps.md` | Read, plus two read-only probes under the worktree's `tmpAI/run/` (git-ignored; commands in `02`). Every fact labelled "read", "document", "run" or "reasoned". Builds on the review of 2026-11-18 (`../exploration/2026-11-18_test_lab_review.md`) and says which of its points still hold (`02` section L) |
| 2 | What the Test Lab must be: "a set of utilities for the user", with her two examples (testing from synthetic data; preparing data files in the correct format). The user and the journey (prepare, scaffold, then BLUEPRINT and HOME), each tool's job, what each must do for recipe format 1, the hand-offs by file, the boundaries; the checks before a rebuild; the choices "to decide" | her words (M422); proposed by analogy with BLUEPRINT step 2 | done (2026-11-21, second worker run; commit `1ac74376`) | `04_what_test_lab_must_be.md` | Input: `02` sections I, J, M and `03` 1.11. Open points to carry: who sees it (flags: developer and qa only, `02` K18); "the correct format" = TSV or the format a recipe declares (`03` 1.11); how a scaffold becomes a recipe the app can open (`03` 1.5, the same decision as BLUEPRINT's empty draft) |
| 3 | The three ideas of the task (extract a pilot recipe, a tool-specific recipe, combine recipes) and what already exists that they could use (the recipe graph and lineage walk in `libs/utils`, BLUEPRINT's branch plan, `utils.recipe_factory`) | relaying text (place them by size of decision); the study step is proposed | done (2026-11-21, second worker run; commit `f3f08ece`) | `05_three_ideas.md` | First written on 2026-05-05 as three notes about "manifests" (git `652ee833`); no source says what they mean, so the file gives readings. By size: tool-specific recipe (small to medium), pilot recipe (medium), combine (large) |
| 4 | Proposals by the panel viewpoints (scientist, architect, developer, user), each with pros and cons; one table that flags first what changes a result silently, hides a step or reconsiders a decision | relaying text (M422) | next: needs the coordinator to start the four viewpoints | `06_panel_brief.md`, `06_proposal_scientist.md`, `06_proposal_architect.md`, `06_proposal_developer.md`, `06_proposal_user.md`, `06_proposals_one_table.md` | The viewpoints are dispatched by the coordinator (one round, at most 250 words each, scratch only under `tmpAI/panel/`). They propose; the owner decides |
| 5 | The guide: what the rebuild planning needs, the larger decisions and questions first, no details; the three ideas placed by size | relaying text (M422); her words "a preparation without details" | parked until step 4 | `GUIDE.md` | Same form as `../blueprint_revision/GUIDE.md` |

Step 1 addendum: done (2026-11-21, commit `9fbcc616`). `prior_work/` holds the step 4c report of the big recipe change, the two run scripts of the 2026-11-18 review (its folder has no `.md` file; its inputs and outputs were left out, reasons in `prior_work/README.md`) and this review's two probes; each copy has a first line naming its source and date.

## Resume here

Steps 1, 2 and 3 are done, and the prior work is filed. Next is step 4: the coordinator starts the four panel viewpoints (scientist, architect, developer, user; one round, at most 250 words each, scratch only under `tmpAI/panel/`). A worker cannot start them. Their brief (`06_panel_brief.md`) should take its question and its approaches from the report of the second worker run (2026-11-21) and point the viewpoints at `04` (sections 2, 4, 6 and "To decide") and `05` (section 5 and "To decide"). Then step 5, the guide (`GUIDE.md`), in the form of `../blueprint_revision/GUIDE.md`.

Before relying on any line number: the code moves (the HOME and GALLERY work goes on in `dev`). On 2026-11-21 no Test Lab file differed between `52c4bcfa` and this branch at `9fbcc616` (`git diff --stat` on `libs/test_lab`, `libs/id_reconciliation`, the Test Lab handler and module, `id_patterns.py` and HOME's Data Import handler).

## Things the next worker must not do

- Build or change anything outside `.claude/design/lab_revision/` (and its own `tmpAI/progress.md`).
- Put a question to the owner: a choice that is open goes into the files as "to decide", with its options.
- Resolve a contradiction between two sources, or a contradiction in the records: list it (`02` section K; K13 is the task listed twice in `tasks.md`).
- Present a relaying session's sentence, a reviewer's summary or a worker's default as the owner's words; quote her words from `ORDER.md` or from a ledger line that is DECIDED and taken by EVE.
- Fix a defect found here, even a one-line one: the Test Lab is parked by the order of work (D-0271).
- Re-run the probes outside the worktree's `tmpAI/`, or read the owner's `tmp.md`.
