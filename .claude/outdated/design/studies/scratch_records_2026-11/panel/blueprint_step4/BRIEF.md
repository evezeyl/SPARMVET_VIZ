# Panel: how the wrangling engine, the plotting engine and the lineage can help a user write recipes in BLUEPRINT (step 4 of the BLUEPRINT review; coordinator, 2026-11-21 night)

## The owner's order (her words, `.claude/design/blueprint_revision/ORDER.md`: READ IT FIRST)
"it is an ide (visual) that help the user create recipes for production : with the actions and parameters available (depending on the engine used ... now we have only one engine for the data and one engine for the plotting - but the engine "language" will need to be able to selected in the blueprint) and see how it is possible to use the wrangling engine and plotting engine to help a user to write recipes, with the lineage"
"can and must use different agents to propose solutions on how we can do best" (the viewpoints propose, she decides).
"prioritize larger decisions/questions to take first but no details".
This review builds nothing and decides nothing. No question goes to her now: an open choice is written "to decide" with options. It is a fallback task, not an emergency. The rebuild of BLUEPRINT comes AFTER the refactoring of HOME and the Gallery.

## What to read (main tree, `.claude/design/blueprint_revision/`)
1. `ORDER.md`.
2. `04_what_blueprint_must_be.md` (the journey, the parts of the IDE and their state, what a production recipe requires, what must be verified).
3. `05_engines_in_blueprint.md` (what is decided and built about engines, choices E1 to E7).
4. `02_planned_vs_existing.md` section I (facts on the engines and the lineage as helpers) and section L (contradictions between sources: listed, not resolved).
5. `03_parked_items_and_known_gaps.md` (column pickers that follow the lineage, the warning when values are cast to integer, undeclared file columns).
Only if needed: `07_ai_agent_planned_vs_existing.md` (the AI agent is NOT the subject of this panel, except where it touches the same helpers), `prior_work/`.
Do not redo the reading of the code recorded there. A small read-only check is allowed where your proposal depends on a fact (give file:line or the command). Never read `tmp.md`. Do not edit the repository; scratch only under `tmpAI/panel/blueprint_step4/`.

## DECIDED (do not reopen; flag a proposal that reconsiders one). Check the ledger line before you rely on a number.
The recipe format 1 (unknown keys refused; tiers as own keys; the published columns are the last select; prefixed action names; `ui_label`); HOME is the only place that writes an audit, BLUEPRINT never does; user spaces are independent, hand-offs are files; science is transparent and reproducible, nothing changes a result silently; the tool informs and the user chooses; lineage questions use the plan of the engine as the authority for what exists and its type (the walk built for HOME's audit: `app/modules/plan_composer.py`); the engine of a component is a field of its registry entry and an engine without its library is refused.

## The question
What help can BLUEPRINT give a user who writes a production recipe, by USING what the app already has: (a) the wrangling engine (run a step list on real data, lazily: the plan gives the columns and types after every step without reading the data; a collect gives rows), (b) the plotting engine (registry of components and their parameters; a render of the plot from the table it reads), (c) the lineage (which tables feed which join, tier and plot; where a column comes from, where it is renamed, dropped or recomputed; what depends on a step), and (d) the recipe check and the load gate.

Propose 2 to 4 distinct approaches for the whole (not a list of features), for example: forms first with a check on Apply; a live plan after every step (columns and types always current, rows on demand); lineage first (the map is the editor); text first with assistance (the YAML is the editor, the engines validate and complete). For each approach say, from your viewpoint:
1. What the user sees and does at each moment of the journey (new recipe, a table and its fields, a step, a join, a plot, the final check and save).
2. Which engine facility it uses and whether that facility exists today (source), must be extended, or is missing.
3. Pros, cons, the pitfalls for the user, and what would change a result or hide a step.
4. What it means when the engine is selectable (several data or plot engines): what stays generic, what must exist per engine.
5. What must be decided first (the larger decisions only, ranked), and what can wait.
Then recommend ONE approach or combination, say why, and say what you could not verify.

## Each viewpoint's own weight
- Scientist and data scientist: correctness on messy data; that the user sees what a step did to rows and types before saving; reproducibility (what the saved recipe guarantees); what a preview on a sample may hide; discrete against continuous columns in plots; joins (keys, row multiplication).
- Architect: boundaries (libs without Shiny, `blueprint_arch`, `utils`, the app layer), one source of truth for the catalog of actions and components and for the lineage, what is shared with HOME's audit walk, testability, the long-term cost of each approach, which ADRs or rules it would amend.
- Developer: effort, risk, test cost, build order, what can be built and shown in small working parts, what can run in parallel, what of today's BLUEPRINT code can be kept.
- User who is not a developer: is the information needed to choose shown in plain words at the moment of the choice; what frightens or misleads; the words on screen; what a beginner needs against a recipe maintainer.

## What to return
Save your full text as `tmpAI/panel/blueprint_step4/<viewpoint>.md` if you can write there (a shell redirect), else return it in full. Plain short sentences, tables for comparisons, as long as needed to be clear, no padding. Start with a 6-line summary; end with "To decide first (ranked)" and "Not verified". Name BLUEPRINT and the part concerned in every finding.
