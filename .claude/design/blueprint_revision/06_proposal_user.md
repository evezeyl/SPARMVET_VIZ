<!-- copied unchanged on 2026-11-21 from .claude/design/studies/scratch_records_2026-11/panel/blueprint_step4/user.md (not in git), written 2026-11-21 night in step 4 of the BLUEPRINT review; a viewpoint's proposal: it recommends, it decides nothing -->
# BLUEPRINT recipe help, step 4: viewpoint of the user who is not a developer (panel-user, 2026-11-21 night; filed by the coordinator from its report; read from the review files, nothing seen on a screen)

References: `H` = `app/handlers/blueprint_handlers.py`, `W` = `app/modules/wrangle_studio.py`, `02`/`03`/`04`/`05` = the files of `.claude/design/blueprint_revision/`.

## Summary
1. Recommended: a combination with approach B (the live table after every step) as the backbone. The map (approach C) is only the way to move around. The forms (approach A) sit underneath. The YAML text (approach D) is read-only.
2. After each step the user must see in plain words what the step did: the columns added, removed, renamed or changed in type. Rows are shown on request, with a label stating how many rows were read.
3. The two checks, "Can HOME open it?" (`run`) and "Is it well built so far?" (`build`), must be shown apart. Today Validate gives one pass or fail with `run` (`H:2843-2845`, `04` section 3), so a new recipe fails from its first minute.
4. Today most controls vanish when the agent switch is off (`H:1690-1691`, `02` A). A beginner in `standalone` sees empty panels and cannot tell why.
5. Engine: show the engine as a plain label now. When the user changes an engine, show the consequences and keep the steps already written, marked. Never translate steps silently (`05` R4 and P4).
6. Every message must say what changed, where, and what the user can do. Few messages, each with its consequence.

## What the user cannot see today
- Columns after a step (BLUEPRINT, step forms). Pickers offer only the declared `input_fields` (`W:1979-2003`, `H:683-697`). A column made by an earlier step cannot be picked. After a join the user gets no fields (`H:691-697`).
- Where a step sits (BLUEPRINT, step cards). The card does not show its tier. A step in the wrong tier is refused only at Save (`H:589-592`). D-0308 asks the user to "see, for each step of the recipes, where it sits".
- What a Save changes (BLUEPRINT, save). A Save drops comments and overwrites the file with no backup (`H:1188`). The user is not told.
- Which controls need the agent (BLUEPRINT, whole space). A missing control looks like a missing feature.
- The plot (BLUEPRINT, plot preview). The preview exists but is not mounted (`W:714`, `04` section 3). The user writes a plot without seeing it.

## Approaches, from the user's seat
| | What the user understands | What stays hidden | Risk of a wrong choice |
|---|---|---|---|
| A. Forms, check on Apply or Save (today) | "I fill a form and press Apply." | Columns after earlier steps, rows lost, row multiplication in a join, what Save rewrites | High. The error comes after the work, with a coded message. The user learns of a lost sample at HOME. |
| B. Live table after every step | One sentence: "After each step, here is your table." One picture: a list of columns with type, new ones marked, removed ones struck through | Row counts, unless asked for. A sample can hide a rare value or a late NA. A cast to integer is visible only with data (`03` 1.2). | Lower. The user sees the consequence at the moment of choice. The risk is false comfort from a sample. |
| C. Map first (the lineage is the editor) | "I click a box on the map." Good for seeing what feeds what. | Step-level effects are too small a view. A beginner meets the map before knowing what a tier is. | Medium. A good map, but one picture cannot carry a recipe of many tables and plots. |
| D. YAML first with help | Fine for a recipe maintainer who already knows the format. | Everything is in the maintainer's head. A beginner meets `'on'` quoting, prefixed names and `ui_label` unaided. | Highest for beginners. Each unknown key is refused (format 1), and refusal text is jargon. |

For B, the plan gives column names and types without reading data (`02` I, `plan_composer.py:1-30`). This needs the data files and a recipe that runs up to that step (`03` 1.1). When a step fails, the screen must say "The columns after step 3 cannot be shown because step 3 has an error: <reason>". It must not show a stale list.

## Warnings: few, each with its consequence
- One line per step, always the same place: "Step 4 removed 2 columns and renamed 1."
- Interrupt only for what changes a result: rows lost, a cast of decimals to integer, a join that multiplies rows, unknown columns left out of the recipe (the parked D-0374 and D-0376 items).
- Never interrupt for a stage the user has not reached yet. A recipe that lacks a plot is not an error while the user is building (`04` section 4, T09).
- Show warnings and errors in different colours. Today an error row and an advice row use the same yellow box (`03` 1.8, not rechecked).

## Words the screen must carry (suggested, not decided)
- Under each step: "This step: 120 columns before, 118 after. Removed: A, B. Renamed: X to Y. Type changed: Z from text to integer."
- On a sample: "Rows shown: the first 100 of the file. Rare values or missing values further down may not appear. [Count all rows]"
- After a join: "Left table 40 rows, right table 40 rows, result 52 rows. 12 rows were added because the same key appears twice in the right table."
- On a cast: "Z is turned from decimal to integer. Values like 2.7 become 2. Check the data before keeping this step."
- On each step card: "Tier 1: clean this table." Say "tier" once, with the plain words beside it.
- On Validate, two separate lines: "Ready to build (steps are correct so far): yes. Ready for HOME (every table has a plot): no, the recipe has no plot yet."
- On Save: "This will rewrite <file>. Comments in the file will be lost. A copy of the old file: [none / kept]." (until D-0174 is built).
- When controls are disabled: "This control needs the AI agent switch. In this setup it is off." No panel may stay empty without a reason.
- Engine, with one engine only: "Data engine: python-polars (the only one in this app)", as text, not as a one-item selector.
- On changing an engine: "5 steps are written for python-polars. They will not run in <other engine>. They are kept and marked. Nothing runs until you fix them or revert."

## Beginner against maintainer
- Beginner: needs B with plain sentences and no coded messages; the order of the journey: tables, tier 1, tier 2, tier 3, plots, check, save (D-0308). Does not need the engine choice or the YAML.
- Maintainer: needs D (read-only is enough), the lineage for "what breaks if I change this?", and the separate `build` and `run` checks. A maintainer editing a recipe in use must be told that HOME may have it open (`03` 1.8).

## Engines, from the user's seat
- The picker and the forms must filter by the engine of the part being edited. The catalog does not carry the engine today (`05` section 3). The user sees all 68 actions whatever the engine.
- Widgets and help are Polars-specific (expression text, type names, `05` section 5). A second engine means a second set of forms and help texts.

## To decide first (ranked)
1. Is the column list after each step (B) the backbone of BLUEPRINT? It needs the plan, which needs the data files (`04` To decide 6).
2. Which check BLUEPRINT shows: `build`, `run`, or both apart (`04` To decide 3). Suggestion: both apart.
3. Which controls may depend on the agent switch (`04` To decide 2). Suggestion: only the chat.
4. What a Save may change, and whether the user is told first: comments, backup, the dated final file (`04` To decide 9 and 8).
5. What a step in the wrong tier does (`04` To decide 4).
6. Where the engine is shown now (E1), and what happens to written steps when it changes (E3). Suggestion: keep and mark.
7. The wording and place of the undeclared-columns note and the integer-cast note (`04` To decide 13).

## Not verified
Nothing seen on a screen. The plan on a failing recipe or a large table (how long the live list would take). Whether a sample row limit exists. How warnings and errors look in Validate today (D-0079). `plan_composer.py` not read (the claim that a plan failure comes back as a value rests on `02` I). How the checker treats `data_engine` on `tier3`.
