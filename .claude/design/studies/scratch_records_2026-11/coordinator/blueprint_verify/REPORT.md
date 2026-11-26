# BLUEPRINT today, on your seven points (read-only check, 2026-11-22)

Your order (ledger D-0493, D-0494). Two scouts read the code; NOTHING was run and nothing in BLUEPRINT was changed. Where a fact could only be proven by a run it is marked "needs a run". Details with file:line: `PART1_points_1_2_3_5.md` (this folder) and section 3 below. The build plan that follows from it: `BUILD_PLAN.md` (this folder).

## 0. PROVEN BY RUNS, later the same day: BLUEPRINT's Apply and Save are not safe on a real recipe today
The "needs a run" items were run headless, in a scratch copy (`runs/REPORT.md`, scripts and outputs beside it). No browser, no real model call. What the reading suspected is confirmed, and it is worse:
1. **Pressing Apply on a step the author did not touch changes the step.** Each action's own example was passed through an untouched Apply: of 68, 21 gain keys, 6 become invalid, 2 lose a key, 6 change a value or its order.
2. **A silent change of a RESULT:** `polars_fill_null` with `value: 0` loses the 0 and becomes `strategy: forward`, which the recipe check accepts. Empty cells are then filled with the previous value instead of 0, with no message.
3. **A list of columns can be emptied:** `polars_drop columns: [hsp_len, total_len]` becomes `columns: []`.
4. **A plot loses its mapping:** the demo plot `miaou` loses `y: value` after Apply and Save (the form offers only declared fields); `group` and `linetype` are lost too.
5. **A real chain on the demo recipe breaks four recipes:** Apply on one step of the MLST table, then Save: the load gate then refuses 4 recipes, because that file is shared. (The gate does run AFTER a save and warns; it never runs before the write.)
6. **Save loses every comment of the file** (all 17 in the demo's file) and writes the file name as the comment of every step; a nested include is written inline; "Clear All" then Save writes an empty step list and says "Saved".
7. **A fresh plot layer written by an untouched Apply** carries values nobody chose (a colour dictionary, switches set to "no"): of 46 geoms and stats that draw on test data, 22 then fail to draw and 11 draw a different picture.
8. **A step that fails in the preview** makes the whole table disappear, with a line on the console only.
9. **Claude by the command line:** all four faults confirmed; a message ends in "[Agent error: ... unexpected keyword argument 'system_prompt']". Building the adapter makes 2 calls of the `claude` command, one of them a real question ("ok"), when the panel is merely shown. No data value of the demo reaches the prompt.
Corrected by the runs: `facet_by` has no conflict (both spellings are accepted and draw the same picture); no form falls back to plain text by accident; the type picker shows 11 of 21 declared types, and a step that holds another type becomes `String` after an untouched Apply.
**Consequence, for you to know now:** BLUEPRINT is shown only with the developer and qa app features. Until its form part is rebuilt, a recipe that matters should not be edited through BLUEPRINT's Apply and Save; edit the file and use Validate. The first slice of the build plan replaces exactly this part.

## 1. The seven verdicts
| Your point | Today | In one sentence |
|---|---|---|
| 1. The engine can be switched | PARTLY | The app can hold two engines and a recipe names them; BLUEPRINT keeps the engine keys on save, but does not show them, does not let the author choose, lists every action whatever the engine, and calls Polars directly in several places. |
| 2. Every Polars action usable, parameters selected or typed | PARTLY | All 68 actions have a form; every parameter of the 65 exact ones has a field; some values are saved as text; a parameter the form does not show is removed on Apply. |
| 3. Every plotnine component usable, parameters selected or typed | PARTLY | All 191 components have a form; almost every field is free text; nested parts cannot be typed; the mapping knows 8 aesthetics. |
| 4. The warnings and guidance as helpers | PARTLY | The app has about 92 check codes, advices, a formula check, step checks and lineage notes, and most can be called without the screens; BLUEPRINT uses them only behind the Validate button. Nothing is checked while a form is filled, on Apply or on Save. |
| 5. Write in all the data tiers | NO | Saved: tier 1 and tier 2 of a table, plot entries, groups, the info block. Not saved: join tiers, tier 3, input fields, new tables and joins, `plot_defaults`. No step reorder, no single-step delete. |
| 6. The lineage to build a plot | PARTLY | The pieces exist (the recipe graph, the lineage walk, the columns and their types at each stage) and HOME uses them; BLUEPRINT does not: its forms offer the columns DECLARED for a table, not the columns that exist after the steps. |
| 7. Claude helps to build recipes | NO, by both ways | Command line: the adapter exists, but the chat panel's send path has four faults and would answer "[Agent error]" (read, needs a run). API: not built. |

## 2. Flags first: what changes an author's work silently today
1. **Apply removes what the form does not show.** A parameter written by hand in the recipe is dropped when the author presses Apply on that step (`app/handlers/blueprint_handlers.py:1255-1346`). The same for a plot's mapping beyond the 8 aesthetics the form knows (`:1219-1238`).
2. **A number typed in a "column or value" field is saved as text** ("10", not 10) (`:1290-1298`).
3. **Save writes with no recipe check**, and the comments of the file are lost (`:1155-1196, 583-608`). Validate is a separate button.
4. **The preview drops a step that fails and goes on** (it prints to the console only): the author sees a table as if the step did not exist (`app/modules/wrangle_studio.py:2325-2328`).
5. **A new recipe gets its engines chosen by the app**, without asking (`libs/utils/src/utils/recipe_factory.py:162-163`).
6. **A recipe name typed in BLUEPRINT does not show in HOME**: the Info form writes `info.name`, HOME reads `info.label` (`blueprint_handlers.py:2543, 2611`; `app/handlers/home_theater.py:1144`).
7. **The chat panel calls the model when it is merely shown.** Building the command-line adapter runs a real `claude` call ("ok") as a probe (`libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:149-192`; triggered at `blueprint_handlers.py:1777`). Nothing tells the user what is sent to the model.
8. **A contradiction with a decision of yours:** the code and BLUEPRINT's design note say BLUEPRINT never writes tier 3; your decision of 15 November (D-0063) says it may author a plot's tier 3.
9. **A mapped column that does not exist is found only when the plot is drawn.** The recipe check does not compare a plot's mapping with the columns of its table (`libs/utils/src/utils/recipe_check.py:1145-1168`).

## 3. Points 4, 6 and 7 in more detail
### Point 4: helpers
- What exists and can be called without a screen: the recipe check (`recipe_check.check_recipe`: each problem is a record with a code, refusal or advice, a place as a path of keys, a message and a fix); the loader's check of a file; the data check; the formula check (`formula_check.formula_problems(text)`); the check of one step against its form (`ui_schema.step_problems`); the column drop gate; the lineage notes.
- What BLUEPRINT shows of it: the Validate button runs three checks and lists the problems (location, problem, tip), not clickable, not grouped by file. Only five advice codes reach any screen; the other advices reach none.
- Not built anywhere: a problem's place as FILE AND LINE (your decision D-0342). The help registry is not wired into the app. BLUEPRINT's own help says Validate reads no data; it does.
### Point 6: lineage
- Two lineage systems live side by side: the recipe graph with the walk and the plan book (`libs/utils`), used by HOME; and BLUEPRINT's own navigator and tube map (`libs/blueprint_arch`), used by BLUEPRINT and by the export's lineage file. The navigator already stands partly on the graph; its own step lists and field resolution do not.
- What a plot builder needs and where it stands: the columns WITH types at a chosen stage: exists for HOME (needs the data), not used by BLUEPRINT; where a column comes from: the walk answers it, not wired; which tables a plot may read: the graph knows, BLUEPRINT has no picker; the steps that feed a plot: shown (tube map, lineage rail), without types; a warning for a mapped column that does not exist: missing (flag 9).
### Point 7: Claude
- Decided (ADR-076): the command line first, the API second, a local model third; the agent never changes a recipe itself; what data it may see has three levels (none, a summary of the schema by default, a sample for developers).
- Built: the command-line adapter (`claude --output-format text -p ...`, no streaming, 120 seconds), three read-only tools (the list of actions, the list of components, the declared fields). Not built: the API adapter (it returns "disabled"), the tools that would propose a change or check a fragment, the data levels, any disclosure to the user.
- Four faults on the send path, by reading (needs a run): the session is never started; the handler passes an argument the adapter does not accept; it hands the wrong kind of object to the parser; the operator's instructions file is passed in the place of the recipe path, so the instructions never reach the model. The record that says this part is "implemented, 14 smoke tests" is not supported for the send path; no test covers it.
- The configuration names a model (`claude-opus-4-7`) that no code reads, and that is no longer the newest model: to choose again when the API path is built.
- What Claude cannot see today, and would need in order to help: the result of the recipe check for the open recipe; the columns at each stage; a Gallery example; a way to return a step or a plot entry that the app CHECKS before the author applies it.

## 4. Needs a run (not done; a reviewer can do each in a scratch copy)
The counts 68 and 191 from the registries; every form rendered headless; the Apply round trip (a number, a literal, a list declared as text, an extra key); what Save does to a file that holds a nested include; the column list of a join tier (by reading: one entry "?"); one send in the chat panel with a stand-in for the `claude` command; whether plotnine accepts text where a list is expected.

## 5. Records found out of date (to correct with the rebuild)
BLUEPRINT's design note on tier 3 (against D-0063); "all 60 actions verified" and "eight widgets" (68 and twelve today); the rule file that calls the save serializer "not yet implemented" (it exists); ADR-076's status line; BLUEPRINT's help text on Validate; one task (the `plot_defaults` form) that no longer matches the code.
