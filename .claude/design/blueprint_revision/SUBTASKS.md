# BLUEPRINT-REVIEW-1: subtasks (so the work can be parked and resumed)

Parent task: `BLUEPRINT-REVIEW-1` in `.claude/tasks/tasks.md` (D-0395). Order and its addition: `ORDER.md` (same folder).
This file is kept current by whoever works on the review. It builds nothing and decides nothing.
States: done / in work / parked / next.

| # | Step of the order | State | Files it produced | Notes |
|---|---|---|---|---|
| 1 | Find back the information: what was PLANNED for BLUEPRINT against what EXISTS, and what must be verified and updated | done (2026-11-20 night, worker run) | `01_sources.md`, `02_planned_vs_existing.md`, `03_parked_items_and_known_gaps.md` | Read only. Nothing run. Every fact is labelled "read" (code at file:line) or "document" (taken from a text, not re-checked) |
| 2 | Understand BLUEPRINT as the visual IDE that helps a user write recipes for production, with the actions and parameters of the engine in use | next | `04_what_blueprint_must_be.md` (not written) | Start from section A of `02_planned_vs_existing.md` and the prior picture `tmpAI/panel/blueprint_gap/GLOBAL_PICTURE.md` (main tree, git-ignored, dated 2026-11-18, out of date on four points: see `01_sources.md` section 9) |
| 3 | The engine "language" selectable in BLUEPRINT (today one data engine, one plot engine) | next | `05_engines_in_blueprint.md` (not written) | Facts already collected in `02_planned_vs_existing.md` section H (no engine control in BLUEPRINT; the registry already records the engine of each entry) |
| 4 | How the wrangling engine and the plotting engine, with the lineage, can help the user write recipes; proposals by the panel viewpoints (scientist, architect, developer, user), pros and cons, she decides | next | `06_proposal_<viewpoint>.md` one per viewpoint (not written) | Needs a coordinator to start the viewpoints (agents `panel-*`). Facts for them: `02_planned_vs_existing.md` section I |
| 5 | The Claude AI agent: what was planned, what exists; "integrated in CLI and via API" | partly done | facts in `02_planned_vs_existing.md` section J | The options document `.claude/design/adr076_mvp2_backend_options.md` already holds the open choices A to E; step 5 remains: bring them to the guide with the ranking |
| 6 | The guide: what the rebuild planning needs, the larger decisions ranked first, no details | next (last) | `GUIDE.md` (not written) | Inputs: all files above. The ranked list of larger decisions starts from `02_planned_vs_existing.md` section K (open choices, unranked) and `03_parked_items_and_known_gaps.md` |

Step 1 addendum (2026-11-20): the earlier BLUEPRINT studies that were only in the git-ignored `tmpAI/` are now kept in git under `prior_work/` (copies, each with a first header line naming its source; see `prior_work/README.md`). They are sources for the guide, not decisions; where they differ from `02_planned_vs_existing.md`, that file is the newer reading.

## Resume here

Resume at step 2 (nothing of step 2 to 6 is started). First read `01_sources.md` (what exists and how reliable it is), then `02_planned_vs_existing.md` (sections A to K), then `03_parked_items_and_known_gaps.md`. The viewpoint agents of step 4 have not been started. Do not redo the reading of the code: the facts and their file:line are written there. Two things to refresh before relying on any line number: the code moves (the HOME and GALLERY work is still going on in `dev`), and the prior gap report of 2026-11-18 was written before the merge of the recipe format 1 branch.

## Things the next worker must not do

- Build or change anything outside `.claude/design/blueprint_revision/`.
- Put a question to the owner: a choice that is open goes into the guide as "to decide", with its options.
- Resolve a contradiction between two sources: list it (they are listed in `02_planned_vs_existing.md` section L).
