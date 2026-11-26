# Sources of GLOBAL_PICTURE.md (for a reviewer)

Roots. DEV = the main folder `SPARMVET_VIZ/`. BRANCH = `.claude/worktrees/engine-keys/` (task/engine-keys). Design files, ADRs and the ledger are read in DEV; `recipe_format_spec.md` and `recipe_spec.yaml` are read on the BRANCH (as the brief asked).
Short names: GAP1..GAP4 = `GAP_REPORT_full_part1.md` .. `_part4.md` (this folder; "part 5" of the brief is at the end of GAP4). PROOF = `tmpAI/engine_keys/BLUEPRINT_T1_T2_PROOF.md`. T3F = `tmpAI/engine_keys/TIER3_facts_2026-11-18.md`. ADR = `.claude/knowledge/architecture_decisions.md`. LEDGER = `.claude/knowledge/decision_ledger.md`. UX = `.claude/knowledge/blueprint_architect_ux_spec.md`. BP = `.claude/design/spaces/BLUEPRINT.md`. DW = `.claude/design/developer_workflow.md`. SPEC = BRANCH `.claude/design/recipe_format_spec.md`. RSPEC = BRANCH `libs/utils/src/utils/recipe_spec.yaml`. PICS = `tmpAI/engine_keys/bp_proof/`.
Code lines are quoted from the gap report and the proof run; I did not re-read the code (the brief: no code reading beyond the sources).

## A
- Her words: LEDGER line 340 (D-0306), 342 (D-0308), 343 (D-0309).

## B. The journey
1. Start. "+ New" stub, no table/join/plot: GAP3 (k) (blueprint_handlers.py:2641-2718, new_recipe.py:19-35). Agent-switch gate: GAP2 general facts (blueprint_handlers.py:1692-1693). No engines/entity/contact control: GAP2 (a). Form reads "name", stub writes "label": GAP2 (a), F8; GAP4 C6, C17. "From scratch" MVP: ADR:3866. "The usual start is a boilerplate template": ADR:3836 (Q3). Engines and entity: LEDGER D-0029 (line 58). Info key PENDING: RSPEC:9-17.
2. Tables. Blueprint writes input_fields: ADR:3892. D-0082 (LEDGER line 111). D-0225 (LEDGER). No add-table, fields read only, branch copy only: GAP2 (b) (navigator.py:884-933). Test Lab writers: GAP2 (b) (bootstrapper.py:106-116); GAP4 part 5 step 2. File handover: DW:167-185 (section 7). No control in any design file: GAP4 R3.
3. Tier 1. D-0306 (LEDGER line 340). Picker, form, Apply: ADR:2841-2850 (ADR-075 section 5), :2882-2887 (section 8), ADR:3834 (Q1). Three correction layers: ADR:2858-2864. Cards "reorder arrows, delete button": UX:133. Run results (apply, edit, save, checker 0/0, HOME 17 of 17, no remove, Clear All only): PROOF table rows 2-4. Hidden Save: PROOF (iv) item 1. Undo no caller: GAP3 (l), F11. Create file only by branch: GAP2 (c), GAP3 (j).
4. Joins. ADR:3838 (Q5); rules_ui_dashboard.md:194. D-0065 (LEDGER line 94). Designer opens a new join, preview "42 / 42", Apply step named `join`, Save refused: PROOF row 8 and (iv) item 8, row 3 ("Save is not supported for component role 'join'"). Gap report's `polars_join` reading: GAP2 (d) (join_designer.py:120-156). Two copies: GAP3 F14; GAP4 C7.
5. Tier 2. Run on branch (rail tab 2, save keeps old steps, HOME Result shows column; map node opens tier 1 only; picker not restricted by the file; join tier 2 refused): PROOF row 5. Dev loses 2 steps, HOME refuses: PROOF row 5 DEV, (iv) DEV items 1-2. No creation: GAP2 (e) (navigator.py:917, :949). Refusal text and its failed exits, no tier on card: PROOF row 6, (iv) item 6. "Provisional" is the review session's reading inside D-0308: LEDGER line 342.
6. Tier 3. D-0063 (LEDGER line 92), D-0305 (339), D-0306 (340). ADR-040 per-plot node and slot: ADR:588-599 (status line ADR:564 "PARTIALLY IMPLEMENTED"; stale note ADR:562 says `pre_plot_wrangling` is an old name). Not read by Blueprint: GAP2 (f) (blueprint_handlers.py:497-502). Checker P05, no code runs it: T3F lines 7-12; GAP2 (f). Branch no button; dev notice: PROOF row 7; T3F lines 29-33.
7. Groups. ADR:3839 (Q6). D-0253 (LEDGER line 282). "+ Group", "Del grp" empty only, Go/Move/Del: GAP2 (g), (h); panel seen in PICS `7_tier3_groups_plots_BRANCH.png`. Not run: PROOF (v). No rename/order, design silent: GAP4 R21.
8. Plots. ADR:3904 (section 5 point 2). D-0253 (LEDGER 282), D-0258 (LEDGER 288). Preview on Apply: ADR:3875. "+ Plot" empty target: GAP2 (h) (group_plot_manager.py:139-172). No target/ui_title/engine/theme control: GAP2 (h); GAP4 R13, R16-R18. Dev opens, branch "Imported 0 steps": PROOF row 7 and (iv) item 3; PICS `7_plot_node_tab1_DEV.png`. Plot output not mounted: GAP3 F1 (wrangle_studio.py:712-716). Gap report's "mapping, layers BUILT": GAP2 (h); GAP4 R14, R15.
9. Defaults. D-0246 (LEDGER line 275). Session-only, palette and theme: GAP3 (i); text "Changes are session-only. Edit YAML directly to persist." seen in PICS `0_blueprint_open_BRANCH.png`. Dev writes removed keys: GAP3 (i).
10. Check. ADR-100 point 3: ADR:5199; SPEC:234. D-0079 (LEDGER line 108). Inline: ADR:3880. A05 asked, not decided: LEDGER line 353. Validate panel, three checks, none per node: GAP3 (l), F13. Not run: PROOF (v).
11. Save. ADR:3881. Comments: ADR:3837 vs ADR:5198 and SPEC:922. Hidden button: PROOF (iv) item 1. Side effects: PROOF row 3 and (iv) item 5. Dev wrong shape: PROOF row 3 DEV. Gap report's "Save BUILT": GAP4 R29.
12. See it run. ADR:3834 (Q1). UX:36 ("visible simultaneously"). BP:81 (non-goal). DW:181. Glimpse "No data loaded" and join glimpse unchanged: PROOF (iv) item 7. Other table's data: GAP3 F2 (xfail test_shiny_blueprint_known_defects.py:17). HOME 17 of 17: PROOF row 3.

## C. Screens
- All panel and tab names, the legend, "Agent unavailable", the Surgeon form: PICS `0_blueprint_open_BRANCH.png`, `2_t1table_apply_BRANCH.png`, `2_t2table_loaded_BRANCH.png`, `7_tier3_groups_plots_BRANCH.png`, `7_plot_node_tab2_DEV.png` (rail, fields in, component, fields out, "Field Gap Analysis"). Map overlap: PROOF (iv) item 9. Layer 1: ADR:3821. Escape hatch: ADR:2864. Design's plot-beside-data: UX:31-36, :239-243.

## D. Map and rail
- Map nodes, edges, one Wrangle node per table, group on each plot node: GAP3 part 3 "Tube map" (blueprint_mapper.py:269-437, :329-332, :402-406). Click opens the file, table opens tier 1: PROOF row 5.
- Rail chain and "(tier 2)" label (branch only): GAP3 part 3 "Lineage rail" (navigator.py:205-323, :219-228). Tables twice: PROOF (iv) item 9; seen in PICS `7_plot_node_tab2_DEV.png` (MLST and metadata_schema twice).
- Step card file name: PICS `2_t2table_loaded_BRANCH.png` (italic "ResFinder_wrangling_tier2.yaml" under each step); default comment = file name on load: GAP3 F3 (blueprint_handlers.py:508-510); written on Save: PROOF (iv) item 5.
- What they do not show: GAP3 "What they do NOT hold".
- Status of ADR-039 "PROPOSED": ADR:523. ADR-040 status: ADR:564. ADR-082 names them owners of layer 1: ADR:3821.
- Quotes: "the exact path that data travels" ADR:574; "Every schema renders as a mini-chain, never as a single node" UX:63-64; "Tier 1 → Tier 2 → Assembly → Plot" ADR:527; "Forward (build): Source → wrangle → assemble → plot" ADR:585; per-plot node and slot ADR:599; "The 'Add node' menu only offers actions valid at the selected insertion point" ADR:2843; "The Rail makes the gap immediately visible" ADR:586; warning node "when target_dataset unset" UX:59 (and today blueprint_mapper.py:430-435, GAP2 (h)); "advise-only, NEVER blocking" ADR:3850; "directly in the DAG" ADR:531; map menu v2 ADR:3839.

## E. What stops a user
1 PROOF (iv) 1. 2 PROOF (iv) 2. 3 PROOF (iv) 3. 4 GAP3 F1; PICS (no plot on branch or dev pictures). 5 PROOF (iv) 4. 6 GAP2 (b); GAP4 R3-R4. 7 GAP3 (j); GAP4 part "NOT CHECKED" (dev one-fragment branch). 8 PROOF row 7; T3F. 9 GAP4 R13, R16, R17. 10 GAP2 general facts; flags in qa/developer only: GAP2 (config/app_features/*.yaml lines). 11 GAP3 (i). 12 PROOF (iv) 5; DEV items 1-2. 13 PROOF (iv) 6. 14 GAP3 F11. 15 GAP3 F5; PROOF setup paragraph.

## F. Open questions: where the named options come from
1 DW:86-95, :180; ADR:3892; ADR:3836. 2 SPEC:230 (profile `build`: empty tiers accepted); D-0250 (LEDGER line 279, "`!include` stays optional, per tier"). 3 ADR:3838; `.claude/rules/rules_data_analysis_recipe_structure.md`:113; GAP4 O12. 4 D-0308 (LEDGER line 342). 5 UX:133; rules_ui_dashboard.md:202; ADR:2862. 6 D-0063, D-0305; ADR:599; SPEC:121 (DEC17); T3F line 33 (an agents' page). 7 ADR:3904; D-0253; ADR:5206 / SPEC:126 (DEC22); D-0258; ADR:3834; GAP4 R13, R18. 8 ADR:3866; ADR:3836; DW:180; ADR-093 via DW:183; ADR:3940 and BP:50. 9 D-0308; LEDGER line 363 (A15). 10 ADR:5199; ADR:3850; ADR:2843; D-0079; D-0308; LEDGER line 353 (A05). 11 ADR:3927 ("All BLUEPRINT capability remains gated by `blueprint_enabled`"); `.claude/rules/rules_app_features_flags.md`:259. 12 ADR:3837; ADR:5198; SPEC:922; SPEC:312 (`sort_keys=False`). 13 GAP4 R1. 14 ADR:3855; GAP4 O7. 15 RSPEC:9-17; GAP4 O3.

## G. Contradictions
- G1 to G13 = GAP4 C1, C2, C3, C4, C5, C6, C7, C8, C9, C11, C12, C13, C14 (same order). G2's sentence on the code writing into a copy at tier 2: T3F line 19 (t3_translator.py:273-284).
- G14 (new): ADR:2843 vs ADR:5199 (and SPEC:234).
- G15 (new): ADR:2848 (row `t2`: "After a join/assembly node, before a plot spec") vs RSPEC:68-70 (`tiers: schema: [tier1, tier2]`) and RSPEC:32-34 (a schema may hold `tier2`).
- G16 (from T3F, not in GAP4): SPEC:7 vs LEDGER line 340 (D-0306) and SPEC:509.
- G17 (new): UX:39 and UX:264 ("Lineage Rail (Right Sidebar)") vs UX:155 (above the tab-2 cards); today: PICS `7_plot_node_tab2_DEV.png` (tab 2).
- G18 (new): ADR:3927 vs the code gate GAP2 general facts (blueprint_handlers.py:1692-1693).

## Picture (GLOBAL_PICTURE.svg)
- States: W only for groups (read, not run). N for tables (GAP2 (b)) and tier 3 (PROOF row 7, T3F). P for the rest, as section B says. Save is P with "button hidden": the save code works when pressed by script (PROOF row 3), but a user cannot reach it (PROOF (iv) 1).
- Tier 3 is marked N with the legend "not in Blueprint: by hand or Test Lab", but today it cannot be done by hand either: the checker refuses a non-empty tier 3 (T3F). The page says so; the three-state legend of the brief has no fourth state.
- The band covers steps 2 to 5 and 7 to 8: GAP3 part 3 (map nodes for tables, wrangle, joins, plots; group on plot nodes; rail chain). Step 6 is shown as "tier 3: not shown" (GAP3 "Tier 3: not in the navigator").
- The file was produced by a small script that writes plain shapes and text (scratchpad `make_svg.py`); label widths were estimated (0.55 x font size per character) and all fit; parsed as valid XML; rendered once with Inkscape to look at it.

## What I could not establish from the sources
- How a Test Lab boilerplate file enters Blueprint today. DW:180 says "open it in BLUEPRINT via BLUEPRINT's normal data analysis recipe load"; Blueprint lists only `config/data_analysis_recipes/pipelines/*.yaml` (GAP2, GAP3 F5). The "Upload (Replace)" and "Upload & Append" buttons exist (GAP2 controls list); what they do is not in my sources.
- Groups and plots actions in a browser (not run, PROOF (v)).
- Any Blueprint behaviour with the AI-agent switch off (read only; the run used qa, switch on).
- Validate's messages in a browser (not run).
- Whether the plot output is mounted on dev in the code (GAP4 "not checked"); the dev pictures show no plot.
- Undo on dev (not checked).
- Whether the map draws the groups as visible boxes today (the mapper sets a group on each plot node; the UX spec's "subgraphs" describe the older Mermaid map).
- Whether ADR-040 counts as "accepted": its status is "partially implemented"; I tagged its texts TO CONFIRM.
- What the owner means by "the order" being guided, warned or enforced: only her principle (D-0308) and the options named there.
