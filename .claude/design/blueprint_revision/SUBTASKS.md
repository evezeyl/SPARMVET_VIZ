# BLUEPRINT-REVIEW-1: subtasks (so the work can be parked and resumed)

Parent task: `BLUEPRINT-REVIEW-1` in `.claude/tasks/tasks.md` (D-0395). Order and its addition: `ORDER.md` (same folder).
This file is kept current by whoever works on the review. It builds nothing and decides nothing.
States: done / in work / parked / next.

| # | Step of the order | State | Files it produced | Notes |
|---|---|---|---|---|
| 1 | Find back the information: what was PLANNED for BLUEPRINT against what EXISTS, and what must be verified and updated | done (2026-11-20 night, worker run) | `01_sources.md`, `02_planned_vs_existing.md`, `03_parked_items_and_known_gaps.md` | Read only. Nothing run. Every fact is labelled "read" (code at file:line) or "document" (taken from a text, not re-checked) |
| 2 | Understand BLUEPRINT as the visual IDE that helps a user write recipes for production, with the actions and parameters of the engine in use | done (2026-11-21, worker run; commit `39c7bb5e`) | `04_what_blueprint_must_be.md` | The journey, the parts of the IDE with their state (reachable, unreachable, missing), format 1 against the save path, the boundaries, 15 checks before a rebuild (V1 to V15), 14 choices "to decide". New facts: the engine now reads tier 3 (the gap is BLUEPRINT's only); a new recipe passes profile `build` and fails `run`; the info form's `info.name` is accepted silently by the checker; the ingestion already lists undeclared file columns (D-0374) |
| 3 | The engine "language" selectable in BLUEPRINT (today one data engine, one plot engine) | done (2026-11-21, worker run; commit `1a0093da`) | `05_engines_in_blueprint.md` | Decided and built engine layer; BLUEPRINT shows none of it and its catalog does not receive the engine; options per level (recipe, tier, plot) for what the user sees, the picker filter and the steps already written; what cannot be judged with one engine; choices E1 to E7 |
| 4 | How the wrangling engine and the plotting engine, with the lineage, can help the user write recipes; proposals by the panel viewpoints (scientist, architect, developer, user), pros and cons, she decides | next | `06_proposal_<viewpoint>.md` one per viewpoint (not written) | Needs a coordinator to start the viewpoints (agents `panel-*`). Facts for them: `02_planned_vs_existing.md` section I |
| 5 | The Claude AI agent: what was planned, what exists; "integrated in CLI and via API" | done (2026-11-21, worker run; commit `bdc0b1c5`) | `07_ai_agent_planned_vs_existing.md` | Planned against built; the chat cannot work today (wrong call arguments, no session start, instructions passed as the recipe path, `!include` not read, a `--system` flag the CLI does not list; checked without calling a model); choices A to E restated with F to J added and "what blocks what"; eight privacy and security points. The ranking is for the guide (step 6). The file number 06 is left for the viewpoints of step 4 |
| 6 | The guide: what the rebuild planning needs, the larger decisions ranked first, no details | next (last) | `GUIDE.md` (not written) | Inputs: all files above. The ranked list of larger decisions starts from `02_planned_vs_existing.md` section K (open choices, unranked) and `03_parked_items_and_known_gaps.md` |

Step 1 addendum (2026-11-20): the earlier BLUEPRINT studies that were only in the git-ignored `tmpAI/` are now kept in git under `prior_work/` (copies, each with a first header line naming its source; see `prior_work/README.md`). They are sources for the guide, not decisions; where they differ from `02_planned_vs_existing.md`, that file is the newer reading.

## Resume here

Steps 1, 2, 3 and 5 are done. Two steps remain, in this order:

- **Step 4 needs the coordinator**: it starts the viewpoint agents (`panel-scientist`, `panel-architect`, `panel-developer`, `panel-user`), one round each, each writing `06_proposal_<viewpoint>.md` in this folder (they recommend; she decides). The brief should give them: `04` sections 2 to 4 (the journey, the parts, format 1), `05` section 4 (the engine options), `02` sections G and I (the lineage and the shared code), and `03` section 1 (the parked items). The question for them: how the wrangling engine, the plotting engine and the lineage can help a user write a recipe (D-0309 "the lineage and the tube map are also to be leveraged"; the order's step 4).
- **Step 6, the guide** (`GUIDE.md`), after step 4: the larger decisions ranked first, no details. Inputs: the "To decide" tables at the end of `04`, `05`, `07`, section K of `02`, the "what blocks what" table of `07` section 5, and the checks V1 to V15 of `04` section 6.

Before relying on any line number: the code moves (the HOME and GALLERY work goes on in `dev`). On 2026-11-21 the BLUEPRINT files were unchanged since `4bc3ebac` (`git diff --stat 4bc3ebac 8cd699f7` on them was empty).

## Things the next worker must not do

- Build or change anything outside `.claude/design/blueprint_revision/`.
- Put a question to the owner: a choice that is open goes into the guide as "to decide", with its options.
- Resolve a contradiction between two sources: list it (they are listed in `02_planned_vs_existing.md` section L).
