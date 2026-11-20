<!-- copied unchanged on 2026-11-20 from tmpAI/panel/blueprint_gap/GAP_DIGEST_for_eve.md (not in git); a record of an earlier study, not a decision -->
# Blueprint gap: digest (phone version)

This page is a short version of the Blueprint gap report. It shows what Blueprint can build today, what is decided, and what is still open.

Nothing was run. Every statement is "read" (seen in the code or the records at a line) or "reasoned" (my own step from lines I read). A separate browser run is testing tier 1 and tier 2 today.

Full report: `tmpAI/panel/blueprint_gap/GAP_REPORT_full_part1.md`, `_part2.md`, `_part3.md`, `_part4.md` (same folder, in order).

## 2. What Blueprint can build today, part by part

"Agent switch" = the setting `blueprint_agent_enabled`. Most controls below answer only when it is on (developer and qa setups). Read.

| Part of the recipe (building order) | Today | What you cannot do |
|---|---|---|
| Info (name, description, author, version) | Partly: form exists; writes "name" and "tags" | Set contact, subtitle, comment, entity or engines |
| Tables and their fields | Not built (a copy of an existing table only; fields by hand) | Add a table; change a field's type, label or entity key |
| Tier 1 steps of a table | Built for an existing file; partly (no reorder, no insert point, no single remove) | Create the file; insert or reorder a step; remove one step (only "clear all") |
| Joins | Partly: the Joint Designer builds the join step in memory | Save the join to its file; choose its tier |
| Tier 2 steps | Partly: edit an existing file from the rail | Create the tier 2 file; a tier 2 step in a tier 1 file is refused (branch) |
| Tier 3 (data steps of one plot) | Not built: Blueprint does not read it; button absent on the branch | Author or see a plot's data steps |
| Groups | Built: add; delete when empty | Rename or reorder; delete a group that has plots |
| Plots: mapping, layers, labels, theme | Mapping and layers built; labels layer addable (reasoned); plot-level theme not built | Set the target table, the title, the plot engine; rename a plot; see its figure (not shown) |
| Plot defaults | Partly: session only, palette and theme | Save it; set font, legend, spacing |
| Files and includes | Partly: new plot file via "+ Plot"; new tier files only by "Create branch", always empty | Create a tier 2 file; keep hand-written "#" comments on Save |
| A whole new recipe | Partly: empty stub, groups and plots; no table, join or target | Build a working recipe from nothing in Blueprint |
| Validate, save, reload | Validate partly (panel, three checks); save and reload built | See errors on each node; undo (no control); save a join |

Where dev differs (read): dev has no tier check on Save; dev shows the "Add plot wrangling" button; dev writes four removed keys into plot defaults and sets the theme to "theme_light" when blank. Both versions have the same agent-switch gate.

## 3. From an empty recipe to a working one

1. Create the stub with "+ New" (name, author). In Blueprint, with the agent switch on.
2. Add the table. Needs Test Lab first (or a table written by hand). Blueprint cannot add a table.
3. Tier 1 steps of the table: add and save them in Blueprint, once the file exists. In Blueprint.
4. Tier 2 steps: by hand only. Blueprint cannot create the tier 2 file.
5. The join step: in Blueprint, in the Joint Designer (needs two tables with fields). In Blueprint.
6. The join file: by hand. Blueprint cannot save a join.
7. The plot: "+ Group", then "+ Plot". Creates an empty plot file. In Blueprint.
8. Plot target table, title, plot engine: no control. By hand.
9. Plot mapping and layers: in Blueprint, then Save. In Blueprint.
10. Validate in Blueprint, then open in HOME to run. The plot figure is not shown in Blueprint.

## 4. The lineage rail and the tube map

The tube map is the picture of the recipe's parts and links. The lineage rail lists the files of the selected part. Read.

They hold (what building needs):
- For each file: its role, its tier (tier 1 or tier 2), its name and its path.
- For each step: its tier and its file, but only after the file is loaded.
- The order: input fields, tier 1, tier 2, then the join.
- Which tables feed which join (the ingredients list).
- The group of each plot. The plot's target is in the plot file, not in the rail.

They do not hold:
- Empty slots: an empty tier is not shown; a table without tier 1 gets no node.
- Tier 2 as its own node on the map (one node per table).
- Tier 3, and the steps themselves (read only on a click).
- A recipe with nothing in it: the map draws nothing.

## 5. What is decided, what is to confirm, what is open

Decided:
- Build order: tier 1, then tier 2, then tier 3, then the plot. [D-0308]
- Blueprint must build the whole recipe, tier 1 and tier 2 included. [D-0306]
- Blueprint may write the tier 3 data steps of one plot, not the plot recipe. [D-0063]
- Tier 3 is data for one plot; the button stays and points to tier 3. [D-0305, D-0306]
- A branch splits one part at a node; the upstream stays shared. [ADR-082]
- The Joint Designer builds the join from two ingredients. [ADR-082]
- The AI assistant only advises; the AI agent never changes the recipe itself. [ADR-082, ADR-076]
- Plot defaults: fix the bug first and alone, then add fields. [D-0246]
- No built-in theme is injected; without a theme, plotnine's default is used. [D-0258]
- One join-key rule, in one place. [D-0065]
- Engines are required; the entity key is declared in the recipe. [D-0029, D-0082]

To confirm:
- Remove and reorder of steps after Apply (the rules file says "edit/remove"). [ADR-075]
- "Blueprint never blocks building", but Save refuses a tier mismatch and a join. [ADR-100]

Open:
- A tier 2 step saved into a tier 1 file. [D-0308]
- How a whole new recipe is built from empty in Blueprint. [D-0306]
- How a table enters a recipe (no number; the design does not describe a control). [ADR-082]
- Plot defaults fields. [D-0246]
- Whether Blueprint finds the branch node itself or the user chooses it. [ADR-082]
- How each step's tier and file are shown, and the lineage view of steps. [D-0308, old A15]
- Column or columns in modif and step actions. [ADR-100]
- The type "Categorical": refuse it, or write it. [ADR-100]
- How the engine reads a plot's tier 3. [DEC17]

## 6. Where the records contradict each other

Each item: the two quotes, as the report gives them.

C1 Tier 3 and Blueprint.
"Blueprint MAY author the plot entry's tier 3" (D-0063) / "BLUEPRINT never authors T3" (rules_ui_dashboard.md:188). The old rule is marked superseded in ADR-082 and ADR-099.

C2 Audit and the plot spec.
"audit never writes a plot spec" (D-0029) / "the audit writes filters and drops" in tier 3 of the plot entry (DEC17).

C3 Comments.
"Hand-written # free-form comments are NOT preserved through a form round-trip" (ADR-082 Q4) / "every writer (Blueprint save, ...) keeps the comments" (format spec, line 922).

C4 Does Blueprint block?
"Blueprint reports and never blocks building" (ADR-100 point 3) / Save refuses a tier mismatch (blueprint_handlers.py:584-587); D-0308 says the refusal "stays (provisional)".

C5 Figure text.
"Plot axis and legend titles default to the field label" (ADR-100 point 9, DEC22) / "The figure text ... is written only in the labs layer" (D-0253).

C6 Info keys.
"info: label" (recipe_spec.yaml:14, pending) / the Blueprint form reads and writes "name" (blueprint_handlers.py:2544).

C7 One join-key rule.
"One pure join-key rule in libs/utils" (D-0065) / "The rule lives twice" (test_join_preview_parity.py:3-4).

C8 The "Add plot wrangling" button.
"the button stays and points the user to tier 3" (D-0305) / absent on the branch; dev still shows it (dev wrangle_studio.py:1615-1617).

C9 Preview and undo marked done.
"Preview results (on-Apply) DONE" and "20-step undo ... DONE" (ADR-082) / the plot preview is not mounted (wrangle_studio.py:712-716) and _undo has no caller (blueprint_handlers.py:372-379).

C11 Agent tool name.
"propose_manifest_diff tool" (ADR-076) / "propose_data_analysis_recipe_diff" (agent_context.py:183-198); registered by no code.

C12 Advise or enforce.
"advise-only, NEVER blocking" (ADR-082 §2a) / "enforces good practices" (BLUEPRINT.md:97-98).

C13 Escape hatch and tier 3.
"BLUEPRINT never authors T3" (rules_ui_dashboard.md:188) / "emits a developer_raw_yaml T3 node on save" (rules_ui_dashboard.md:203).

C14 Developer workflow is out of date.
"final_contract are the developer's job in BLUEPRINT" (developer_workflow.md:89) / "final_contract ... removed" (ADR-100 point 5).

## 7. Known defects met on the way

- The plot figure is not mounted in Blueprint, so it is never shown there. Dev: not checked.
- The preview table can show another table's data when that table has no data loaded. Dev: same code.
- Save drops "#" comments and writes the file name into each step's comment. Dev: not stated.
- The plot-defaults form shows only with the agent switch on. Dev: same gate.
- The info form reads "name" but the stub writes "label". Dev: not stated.
- A join built in the Designer cannot be saved to its file. Dev: not stated.
- The undo function has no button or caller. Dev: not checked.
- The agent's prompt names a tool that is not registered. Dev: not stated.
- The Validate panel shows no result on each node. Dev: not stated.
- The join-key rule exists in two copies. Dev: not stated.
- Save refuses a tier 2 step in a tier 1 file. Branch only; dev has no such check.

## 8. The open choices, with the options the records name

- A tier 2 step saved into a tier 1 file (D-0308). Options named: refuse; two files; no tier picker; guide the order. Pro and con: none in the records.
- Building the whole recipe in Blueprint (D-0306). No options named; the gap report was asked for.
- Label keys (info and plots): keep "label", or rename to "ui_label". Pro as recorded: ui_label is decided for groups and plots. Con: none in the records.
- "columns" or "column" in the modif and step actions. No pro or con in the records.
- "categorical" refused, or "Categorical" written. Pro as recorded: Categorical keeps the level order where order matters. Con as recorded: "String would change the level order of plots."
- Plot defaults fields (D-0246). Option B named: fix the bug first and alone, then add the fields. Pro as recorded: "It will need to be built anyway." Con: none in the records. Option A is not given in the report.
- Branch node: Blueprint finds it automatically, or the user chooses it. No pro or con in the records.
- Pattern helper shared with Test Lab. Your note: "If we can reuse we reuse." No con in the records.
- Showing each step's tier and the lineage of steps: colours, an insertion point, combined lineage. Named as items; no options in the records.
- Whether a join step is a canonical step at all. No options in the records.

No solution is chosen on this page. Next, as decided (D-0309): a global picture of how Blueprint must work, then the evaluation of solutions, then a build plan.
