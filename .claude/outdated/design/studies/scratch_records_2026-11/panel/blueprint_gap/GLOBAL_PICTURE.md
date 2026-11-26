# Blueprint: the global picture (how it must work as a whole)

Picture: `GLOBAL_PICTURE.svg` (same folder). Sources line by line: `GLOBAL_PICTURE_sources.md`.

## A. What this page is

1. Blueprint is "the ui ide for building our recipes"; "It needs to be able to build the whole recipe." [DECIDED: D-0306]
2. The building order is "start by t1 then T2 then T3 then plot", and the tool advises the user against mistakes. [DECIDED: D-0308]
3. This page is the "global clear picture of how it need to work" that comes before any build. [DECIDED: D-0309]
4. It puts side by side what the design says and what the app does today: the gap report (read) and the browser proof run of 2026-11-18 (run). Where they disagree, the run wins and the page says so.
5. It chooses nothing. The panel weighs the options next; the owner decides. [DECIDED: D-0309]

Tags: [DECIDED] = a ledger line taken by the owner or an accepted ADR. [TO CONFIRM] = written only in a design file. [OPEN] = nobody decided, or the sources contradict. [TODAY] = the app now, on the branch of the big recipe change unless "dev" is said; "run" = seen in the browser, "read" = read in the code. A "Wants" line restates the step in plain words; it decides nothing.

## B. The journey: from an empty recipe to a working one

### 1. Start a recipe
- Wants: a new recipe with a name, a description, its engines and its entity (what one row is about).
- Design: "Create new manifest from scratch" is in the first version. [DECIDED: ADR-082] The engines and the entity are written in the recipe. [DECIDED: D-0029] "The usual start is a boilerplate template". [DECIDED: ADR-082 Q3 text]
- Today: "+ New" writes an empty stub: info only, no table, no join, no plot. It answers only when the AI-agent switch is on. [TODAY: partly, read] No control for engines, entity or contact. [TODAY: not built, read]
- Open: how a whole recipe is started and filled. [OPEN] The info form reads "name"; the stub writes "label". [TODAY: read] [OPEN]

### 2. Tables and their fields
- Wants: add a table (its file), declare each field and its type, mark the sample key.
- Design: Blueprint writes the fields (`input_fields`). [DECIDED: ADR-082] Keys are declared in the recipe. [DECIDED: D-0082] The sample id is text, never a number. [DECIDED: D-0225] No design text describes the control. [OPEN]
- Today: no control adds a table or edits a field. A table can only be copied from an existing one ("Create branch"). [TODAY: not built, read] So a table comes from Test Lab's boilerplate file or is written by hand. [TODAY: by hand or Test Lab, read] User spaces hand over through files. [TO CONFIRM: developer_workflow.md]
- Open: how a table enters a recipe. [OPEN]

### 3. Tier 1 of each table (the cleaning steps)
- Wants: add, change, move and remove the steps of one table.
- Design: tier 1 must be buildable. [DECIDED: D-0306] Pick an action, fill its form, Apply, see the data. [DECIDED: ADR-075, ADR-082] Correct by editing, by a 20-step undo, or in the YAML view. [DECIDED: ADR-075] Each step card has "reorder arrows, delete button". [TO CONFIRM: blueprint_architect_ux_spec.md]
- Today: on an existing tier-1 file, pick, fill, Apply and edit work; the saved file passes the checker and HOME draws 17 of 17 plots. [TODAY: built, run] No visible Save button; no remove of one step (only "Clear All nodes"); no move. [TODAY: run] No undo button. [TODAY: read] A new tier-1 file only by an empty branch copy. [TODAY: read]
- Open: creating the file; removing or moving one step. [OPEN]

### 4. The joins
- Wants: join two tables on a key, check the match, keep the join in the recipe.
- Design: the Joint Designer: both tables side by side, a key-match preview on real data, Apply with a reason. [DECIDED: ADR-082 Q5] One join-key rule, in one place. [DECIDED: D-0065]
- Today: the Designer opens an empty new join, not the existing one; the preview works ("42 / 42 left keys matched"); Apply adds a step; Save is refused ("Save is not supported for component role 'join'"), on the branch and on dev. [TODAY: partly, run] The key rule exists in two copies. [TODAY: read]
- Run against read: the report read that Apply writes `polars_join`; the run shows the step named `join`. The run wins.
- Open: saving a join; editing an existing join; the tier of the join step. [OPEN]

### 5. Tier 2 (reshaping)
- Wants: reshape or summarise a table or a join after tier 1.
- Design: tier 2 must be buildable. [DECIDED: D-0306]
- Today: an existing tier-2 file of a table is reached from the lineage rail (tab 2), changed and saved; old steps are kept; HOME's "Result (T2)" shows the new column. [TODAY: built for an existing file, run] The map node of a table opens tier 1 only. [TODAY: run] No tier-2 file can be created. [TODAY: read] A join's tier 2 loads; Save is refused. [TODAY: run] On dev, Save lost two tier-2 steps silently and HOME refused the recipe. [TODAY: run, dev only]
- A tier-2 step saved into a tier-1 file is refused, with a message; this refusal is provisional. [DECIDED: D-0308, reading of the review session in that line] Its two ways out fail: that table has no tier-2 file, and no button removes one step. Nothing on the step card says tier 2. [TODAY: run]
- Open: creating a tier-2 file; what happens to a step made for another tier. [OPEN]

### 6. Tier 3 (data steps for one plot)
- Wants: steps that only one plot needs, before that plot.
- Design: "The T3 is the data that goes to the plot BUT not the plot recipe"; Blueprint may write it. [DECIDED: D-0063] "T3 : data plot specific". [DECIDED: D-0306] The button "Add plot wrangling" stays and points to tier 3. [DECIDED: D-0305] In the rail, a per-plot node; when empty, an "Add plot wrangling" slot. [TO CONFIRM: ADR-040, status "partially implemented", old key name]
- Today: Blueprint does not read tier 3. [TODAY: not built, read] The checker refuses a non-empty tier 3 and no code runs it. [TODAY: read] Branch: no button, nothing about tier 3. Dev: the button shows only a notice to write a key that no code reads. [TODAY: run]
- Open: how tier 3 is written in Blueprint and read by the app. [OPEN]

### 7. The groups (the HOME tabs)
- Design: a sidebar list to create, delete and assign; a map menu later (v2). [DECIDED: ADR-082 Q6] Short name `ui_label`. [DECIDED: D-0253]
- Today: "+ Group" adds; "Del grp" deletes an empty group only; each plot has Go, Move, Del. [TODAY: built, read; panel seen in the run, not used]
- Open: renaming and ordering groups: the design says nothing. [OPEN]

### 8. The plots (target table, mapping, layers, labels)
- Wants: choose the table a plot reads, map columns, add layers (geoms, labels, theme), name it, and see the picture.
- Design: plot parts use the same form builder. [DECIDED: ADR-082] Figure text only in the `labs` layer. [DECIDED: D-0253] No theme added by the app. [DECIDED: D-0258] Plot preview on Apply. [DECIDED: ADR-082]
- Today: "+ Plot" writes a plot file with an empty target, no mapping, no layers. [TODAY: partly, read] No control for the target, `ui_title`, the plot engine or a plot theme. [TODAY: not built, read] Dev: a plot opens with its mapping and layers. Branch: it opens with "Imported 0 steps", nothing to edit. [TODAY: run] No plot picture in Blueprint. [TODAY: read; run shows the data only]
- Run against read: the report read the mapping and layer forms as built; the run shows that on the branch a plot cannot be opened. The run wins.
- Open: target, names, theme, the picture. [OPEN]

### 9. Plot defaults
- Design: fix the form's bug first, alone; then fields for the common theme settings, after the owner sees the snippet design. [DECIDED: D-0246]
- Today: palette and theme, "Apply to session"; the screen says "Changes are session-only. Edit YAML directly to persist." [TODAY: partly, read; text seen in the run]
- Open: saving to the file; the fields. [OPEN]

### 10. Check
- Design: one checker; "Blueprint reports and never blocks building". [DECIDED: ADR-100] "Blueprint shows all warnings"; error and warning look distinct. [DECIDED: D-0079] Errors shown inline. [DECIDED: ADR-082] Open a failing recipe, each failing point shown to fix. [OPEN: asked, not decided]
- Today: "Run validation" runs three checks in a panel; no result on each node. [TODAY: partly, read; not run]

### 11. Save
- Design: Save writes the recipe to disk. [DECIDED: ADR-082] Hand-written `#` comments: lost, or kept? [OPEN: G3]
- Today: no visible Save button; a user cannot save. [TODAY: run, also dev] Pressed by script, a table file is written right, but comments are lost, a `data_engine` line is added and `comment: <file name>` goes on untouched steps. [TODAY: run] Joins are refused. [TODAY: run] Dev writes a wrong shape that HOME refuses. [TODAY: run, dev only]
- Run against read: the report read Save as built; the run found no visible button. The run wins.
- Open: what Save may change in a file. [OPEN]

### 12. See it run
- Design: data and plot preview on Apply. [DECIDED: ADR-082 Q1] Plot and data "visible simultaneously". [TO CONFIRM: blueprint_architect_ux_spec.md] The full run is HOME's job. [TO CONFIRM: BLUEPRINT.md] The saved file is picked up by HOME. [TO CONFIRM: developer_workflow.md]
- Today: a data glimpse shows; a table's says "No data loaded" while showing columns; a join's does not change after Apply. [TODAY: partly, run] It can show another table's data (a known defect, pinned by a test). [TODAY: read] HOME ran the saved recipe: 17 of 17 plots. [TODAY: run]
- Missing: the plot picture in Blueprint (decided, not built).

## C. The screens

- Left side: recipe list and "+ New"; Info; Groups & Plots; Recipe File Exchange; Validate; YAML Escape Hatch; Alerts. Steps 1, 7, 10, 11. [TODAY: seen in the run]
- Top: the map (TubeMap), collapsible, legend Source, Wrangle, Join, Plot, Add, Meta. Navigation for steps 2 to 8. [DECIDED: ADR-082, layer 1] Dense: nodes overlap at the default zoom. [TODAY: run]
- Tab 1 "Focus (Logic)": action search, context (All, T1, T2, Assembly, Plot), "Add Node", help; the step list and "Clear All nodes". Steps 3, 5, 8. [TODAY: run]
- Tab 2 "Interface (Fields)": the lineage rail, fields in, the component, fields out, a field search. Reading for steps 2 to 8; the only way to a tier-2 file. [TODAY: run]
- Tab 3 "YAML (Raw Source)": read-only; editable with the edit switch. [DECIDED: ADR-075] Tab 4 "Joint Designer": step 4. [TODAY: run]
- Bottom: "Live Data Glimpse". The design puts the plot picture beside it; only the data shows. [TO CONFIRM: blueprint_architect_ux_spec.md] [TODAY: run]
- Right side: "Blueprint Surgeon" (the form of the selected step, a comment, Apply), Action Help, Plot Defaults, Branch Node, Blueprint Agent ("Agent unavailable" in the run). Steps 3, 5, 8, 9. [TODAY: run]

## D. The map and the rail as the backbone

What they tell the user today:
- The map: one node per table, one "Wrangle" node per table (tier 1 and tier 2 together), one per join, one per plot; arrows table to wrangle to join to plot; each plot node carries its group. [TODAY: read] A click opens that node's file. [TODAY: run]
- The rail: the chain of the selected part: fields, tier 1, tier 2 (labelled "(tier 2)"), the join, the plot. [TODAY: read, branch only label] Some tables appear twice. [TODAY: run]
- A step card shows its file name in its comment line: the file name is the default comment set on load, and Save writes it into the file. No tier word on the card. [TODAY: run picture, read]

What they do not show [TODAY: read]: empty places (an empty tier, a table without tier 1); anything for an empty recipe; tier 3; a table's tier 2 as its own map node; the tier on a step; a plot's target in the rail; the steps (only after a click).

What the owner's principle asks, and what the existing design texts say could carry it (nothing chosen). Note: ADR-039 has the status "PROPOSED" and ADR-040 "partially implemented"; ADR-082 (accepted) names both as the owners of the map and the rail.
- "see for each step where it sits" [DECIDED: D-0308]
  - the rail shows "the exact path that data travels" [TO CONFIRM: ADR-040]
  - "Every schema renders as a mini-chain, never as a single node" [TO CONFIRM: blueprint_architect_ux_spec.md]
  - a tier on each step: the design texts say nothing on this. [OPEN]
- "the order tier 1, tier 2, tier 3, plot" [DECIDED: D-0308]
  - the map shows "Tier 1 → Tier 2 → Assembly → Plot" [TO CONFIRM: ADR-039]
  - "Forward (build): Source → wrangle → assemble → plot" [TO CONFIRM: ADR-040]
  - a per-plot node "between the assembly output and the plot spec", with an "Add plot wrangling" slot when absent [TO CONFIRM: ADR-040]
- "advise user of not doing stupid things" [DECIDED: D-0308]
  - "The 'Add node' menu only offers actions valid at the selected insertion point" [DECIDED: ADR-075] (see G14)
  - "The Rail makes the gap immediately visible" [TO CONFIRM: ADR-040]
  - a map warning node "when target_dataset unset" [TO CONFIRM: blueprint_architect_ux_spec.md]
  - the assistant is "advise-only, NEVER blocking" [DECIDED: ADR-082]
- Empty places shown: only the "Add plot wrangling" slot [TO CONFIRM: ADR-040]. For other tiers, tables and an empty recipe: the design texts say nothing on this. [OPEN]
- Building from the map: start a branch "directly in the DAG" [TO CONFIRM: ADR-039]; a map menu for groups and plots, later [DECIDED: ADR-082 Q6, v2]. Adding a table or a tier from the map: the design texts say nothing on this. [OPEN]

## E. What stops a user today

1. No visible Save button. [run, also dev]
2. A join cannot be saved to its file. [run, also dev]
3. A plot does not open for editing ("Imported 0 steps"). [run, branch only]
4. No plot picture in Blueprint. [read; run shows data only, also on dev]
5. One step cannot be removed; only "Clear All nodes". [run, also dev]
6. No table can be added; no field can be edited. [read, dev not checked]
7. No tier file can be created, except an empty branch copy. [read, branch; dev's branch differs]
8. Tier 3 cannot be built, and the app refuses a non-empty tier 3. [run and read, also dev]
9. A plot's target table, title and engine have no control. [read, dev not checked]
10. Most controls (Joint Designer, groups, info, "+ New", Validate, plot defaults) answer only when the AI-agent switch is on; it is on only in the developer and qa setups. [read, also dev; not run with the switch off]
11. Plot defaults are not saved to the file. [read, branch; dev writes removed keys]
12. Save changes the file text without saying so (comments, added lines). [run, branch] Dev's Save breaks the recipe and drops tier-2 steps. [run, dev only]
13. The refusal message for a step of the wrong tier proposes two ways out that do not exist. [run, branch only]
14. No undo button. [read, branch; dev not checked]
15. Blueprint lists recipes from one fixed folder only. [read, also dev]

## F. Open questions for the evaluation

Every question below is [OPEN]. Options are only those the records name; no pro, no con, no order.

1. How a table enters a recipe. Records name: a Test Lab boilerplate opened in Blueprint; Blueprint writes the fields; a branch copy of a table. No option for a control.
2. How a tier file is created (table and join, tier 1 and tier 2). Records: empty tiers are accepted while building; `!include` is optional per tier. No option for a control.
3. How a join is saved to its file. Records: the Designer makes a standard join step; the save must quote `on`. No option in the records.
4. What happens to a step made for another tier. Options named (D-0308): refuse; two files; no tier picker; guide the order.
5. How one step is removed or moved. Records: arrows and a delete button on each card; "edit/remove after Apply"; a 20-step undo. No other option.
6. How tier 3 is written and read. Records: Blueprint may write it; the button points to it; a rail node with an empty slot; the engine "must read" it, order open. The tier-3 facts page names two ways for the button: build the reader and lift the refusal, or say tier 3 is not read yet (agents' page, not a decision).
7. How a plot is built: target, mapping, layers, labels, theme, picture. Records: the shared form builder; figure text in `labs` (see G5); no injected theme; preview on Apply. Target, title, engine: no option in the records. Theme and labels as layers or plot keys: not stated.
8. How a whole recipe is started. Records: "+ New"; a boilerplate template; the Test Lab file; Gallery text copied by hand; whole-recipe copy (later, rare).
9. Where the user sees each step's tier and file. Records: the principle (D-0308); for HOME's view, colours, insertion point, combined lineage (asked, not decided). No option.
10. How the tool advises: warn, block or guide the order. Records: never blocks building; the assistant advises only; invalid positions blocked (see G14); warnings shown, distinct from errors; "guide the order" (D-0308); open a failing recipe (asked).
11. Which controls depend on the AI-agent switch. Records: Blueprint capability gated by `blueprint_enabled`; the chat by the agent switch. No other option.
12. What Save does to the file. Records: `#` comments lost (accepted) or kept by every tool (see G3); file order kept. On the added lines: no option in the records.
13. Where Blueprint finds recipes. No option in the records.
14. The branch node: Blueprint finds it, or the user chooses it. No pro or con in the records.
15. The info name key: keep `label` or rename `ui_label`. Pending with the owner.

## G. Contradictions to settle first

Every item below is [OPEN]: two sources say different things. G1 to G13 are in the gap report; "New" = found while writing this page.

- G1 Tier 3 in Blueprint. D-0063: "Blueprint MAY author the plot entry's tier 3". Against rules_ui_dashboard.md, BLUEPRINT.md, the user doc blueprint_architect.qmd and a code comment: "never authors T3".
- G2 Audit and plot. D-0029: "audit never writes a plot spec". The format spec (DEC17): the audit writes at the plot's tier 3; the code writes into a copy at tier 2.
- G3 Comments. ADR-082 Q4: `#` comments "NOT preserved ... accepted limitation". ADR-100 point 2 and the format spec: kept "by every tool".
- G4 Blocking. ADR-100 point 3: "never blocks building". Save refuses a wrong-tier step and joins; D-0308 keeps the refusal, provisional.
- G5 Figure text. ADR-100 point 9: axis titles "default to the field label". D-0253: "written only in the labs layer".
- G6 Info keys. recipe_spec.yaml: `label` (pending). The Blueprint form: `name`; the stub writes `label`.
- G7 Join rule. D-0065: "One pure join-key rule". The code: two copies.
- G8 The button. D-0305: it "stays". Branch: gone; dev: shown, and dev still shows the "Forward clear" hint that D-0307 removes.
- G9 Done or not. ADR-082: preview and undo "DONE". Code: plot preview not mounted; undo has no caller.
- G10 Agent tool. ADR-076: "propose_manifest_diff". The prompt: another name; no code registers either.
- G11 Advise or enforce. ADR-082: "advise-only, NEVER blocking". BLUEPRINT.md: "enforces good practices".
- G12 Escape hatch. rules_ui_dashboard.md: it "emits a developer_raw_yaml T3 node"; the same file: "never authors T3"; the branch removed it.
- G13 Old key. developer_workflow.md: `final_contract` is "the developer's job". ADR-100 point 5: removed.
- G14 New. ADR-075: "Invalid positions are blocked at authoring time". ADR-100 point 3: "never blocks building".
- G15 New. ADR-075: tier 2 sits "After a join/assembly node". The format: a table has a tier 2 too (recipe_spec.yaml).
- G16 Not in the gap report's list (from the tier-3 facts page). The format spec, line 7: tiers "build, reshape and finally audit a table". D-0306: "T3 : data plot specific".
- G17 New. The UX spec puts the lineage rail in the right sidebar (sections 1, 7) and above the tab-2 cards (section 4). Today: in tab 2.
- G18 New. ADR-082: "All BLUEPRINT capability remains gated by blueprint_enabled". The code: most controls also need the AI-agent switch.

## H.

Nothing is chosen here. Next, as decided: the evaluation of solutions by a panel of viewpoints, then the build plan.
