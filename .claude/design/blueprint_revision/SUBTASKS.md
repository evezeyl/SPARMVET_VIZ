# BLUEPRINT-REVIEW-1: subtasks (so the work can be parked and resumed)

Parent task: `BLUEPRINT-REVIEW-1` in `.claude/tasks/tasks.md` (D-0395). Order and its addition: `ORDER.md` (same folder).
This file is kept current by whoever works on the review. It builds nothing and decides nothing.
States: done / in work / parked / next.

| # | Step of the order | State | Files it produced | Notes |
|---|---|---|---|---|
| 1 | Find back the information: what was PLANNED for BLUEPRINT against what EXISTS, and what must be verified and updated | done (2026-11-20 night, worker run) | `01_sources.md`, `02_planned_vs_existing.md`, `03_parked_items_and_known_gaps.md` | Read only. Nothing run. Every fact is labelled "read" (code at file:line) or "document" (taken from a text, not re-checked) |
| 2 | Understand BLUEPRINT as the visual IDE that helps a user write recipes for production, with the actions and parameters of the engine in use | done (2026-11-21, worker run; commit `39c7bb5e`) | `04_what_blueprint_must_be.md` | The journey, the parts of the IDE with their state (reachable, unreachable, missing), format 1 against the save path, the boundaries, 15 checks before a rebuild (V1 to V15), 14 choices "to decide". New facts: the engine now reads tier 3 (the gap is BLUEPRINT's only); a new recipe passes profile `build` and fails `run`; the info form's `info.name` is accepted silently by the checker; the ingestion already lists undeclared file columns (D-0374) |
| 3 | The engine "language" selectable in BLUEPRINT (today one data engine, one plot engine) | done (2026-11-21, worker run; commit `1a0093da`) | `05_engines_in_blueprint.md` | Decided and built engine layer; BLUEPRINT shows none of it and its catalog does not receive the engine; options per level (recipe, tier, plot) for what the user sees, the picker filter and the steps already written; what cannot be judged with one engine; choices E1 to E7 |
| 4 | How the wrangling engine and the plotting engine, with the lineage, can help the user write recipes; proposals by the panel viewpoints (scientist, architect, developer, user), pros and cons, she decides | done (2026-11-21; proposals written by the viewpoints in the night, filed in commit `e1ca3d30`; one table in commit `a357e3be`) | `06_panel_brief.md`, `06_proposal_scientist.md`, `06_proposal_architect.md`, `06_proposal_developer.md`, `06_proposal_user.md`, `06_proposals_one_table.md` | The proposals are copied unchanged with one header line. The one table flags first what changes a result silently, hides a step or reconsiders a decision, each fact labelled "read now" or "as reported". All four recommend the live plan after every step as the spine, forms to write a step, the map as a view, the YAML read-only |
| 5 | The Claude AI agent: what was planned, what exists; "integrated in CLI and via API" | done (2026-11-21, worker run; commit `bdc0b1c5`) | `07_ai_agent_planned_vs_existing.md` | Planned against built; the chat cannot work today (wrong call arguments, no session start, instructions passed as the recipe path, `!include` not read, a `--system` flag the CLI does not list; checked without calling a model); choices A to E restated with F to J added and "what blocks what"; eight privacy and security points. The ranking is for the guide (step 6). The file number 06 is left for the viewpoints of step 4 |
| 6 | The guide: what the rebuild planning needs, the larger decisions ranked first, no details | done (2026-11-21; commit `8499ffd9`) | `GUIDE.md` | One page; twelve larger decisions ranked by what they block; checks before a rebuild; a proposed build order (not decided); defects found; contradictions; parked items; not verified |

Step 1 addendum (2026-11-20): the earlier BLUEPRINT studies that were only in the git-ignored `tmpAI/` are now kept in git under `prior_work/` (copies, each with a first header line naming its source; see `prior_work/README.md`). They are sources for the guide, not decisions; where they differ from `02_planned_vs_existing.md`, that file is the newer reading.

## Resume here

The review is complete: steps 1 to 6 are done (step 5 was done before step 4; the file number 06 belongs to step 4).

What remains is not work of this review:

- **The owner's reading** of `GUIDE.md` (start there), then the decisions she takes for the BLUEPRINT design pass, when she chooses. No question was put to her.
- **The checks of section 3 of the guide**, before any rebuild. Several need a browser (what works with the agent switch off and on, what a save changes in a file, what the data glimpse shows) and one calls a model (the agent wiring; it needs her yes). The others need the HOME refactoring first (what HOME's new design gives BLUEPRINT).
- The rebuild itself starts only after the refactoring of HOME and the Gallery (D-0348).

Before relying on any line number: the code moves (the HOME and GALLERY work goes on in `dev`). On 2026-11-21 the BLUEPRINT files were unchanged since `4bc3ebac`.

## Things the next worker must not do

- Build or change anything outside `.claude/design/blueprint_revision/`.
- Put a question to the owner: a choice that is open goes into the guide as "to decide", with its options.
- Resolve a contradiction between two sources: list it (they are listed in `02_planned_vs_existing.md` section L).
