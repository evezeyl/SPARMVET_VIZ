<!-- copied unchanged on 2026-11-20 from .claude/design/studies/scratch_records_2026-11/panel/blueprint_gap/GAP_REPORT_full_part3.md (not in git); a record of an earlier study, not a decision -->
(i) plot_defaults
- Form: bp_plot_defaults_form_ui (blueprint_handlers.py:1718-1748; read only when no node is selected, :1721-1726). Fields: Palette (bp_pd_palette, free text), Theme (bp_pd_theme, select from _KNOWN_THEMES: theme_light, theme_bw, theme_minimal, theme_classic, theme_dashboard, plus the current value; app/modules/plot_defaults_form.py:22, :34-40), button "Apply to session" (bp_pd_apply, :1741).
- Apply: _bp_apply_plot_defaults (:1751-1772) changes cfg.raw_config in memory and calls merged_plot_defaults (plot_defaults_form.py:43-59), which keeps every other key (seed, layers). The help text on screen says "Changes are session-only. Edit YAML directly to persist." (:1743-1746). Nothing writes the master file in that handler (read). So plot_defaults is persisted only by hand.
- No-theme choice writes no theme (plot_defaults_form.py:11, :21).
- Status: PARTLY (session only; palette and theme only; no font, legend, spacing: the four dead keys are removed in the spec, recipe_spec.yaml:6).
- DEV differs: DEV's apply writes default_font_family, facet_panel_spacing, legend_position, defaults theme to "theme_light" when blank, and replaces the whole block (DEV app/handlers/blueprint_handlers.py:1878-1903). So the bug named in D-0246 is in DEV, and the BRANCH merge fixes it (plot_defaults_form.py:48-59).
- Tests: app/tests/test_blueprint_plot_defaults_form.py (source-text check at :40 plus pure tests). Behaviour test for the seed: not found.
- Gate: registered only with blueprint_agent_enabled (blueprint_handlers.py:1692-1693).

(j) INCLUDES AND FILES
- New tier file: only by "Create branch" (navigator.py:897 wrangling/<id>_wrangling.yaml, :943 assembly/<id>_assembly.yaml), always EMPTY and tier1 only (:917, :949, :795).
- New plot file: "+ Plot" writes <stem>/plots/<id>.yaml (group_plot_manager.py:161-167); branch plot writes <stem>/plots/<id>.yaml (navigator.py:983).
- Basename mirroring: the folder is the master's file stem (group_plot_manager.py:160-161; navigator.py:881, :897). Written relative to the master's folder.
- Master text edits by insertion: _insert_after_top_level_anchor (navigator.py:764-771) and new !include keys; a failed branch writes nothing (docs/workflows/blueprint_architect.qmd:243).
- Save: writes only the loaded file (blueprint_handlers.py:1157-1196). Whole-file rewrite (:112). Comments lost (reasoned: safe_dump of a dict has no "#").
- The master is rewritten in: the info save (:2622-2625, yaml.dump), the branch write (:1658-1683), the group and plot CRUD (group_plot_manager.py:78-83).
- Download bundle: the master and its mirrored folder (blueprint_handlers.py:1396-1415).

(k) A WHOLE NEW RECIPE FROM NOTHING
- "+ New" (btn_bp_new_data_analysis_recipe) -> modal: slug (snake_case), display name, description, author (:2641-2667) -> Create (btn_bp_new_submit :2675-2718) -> file config/data_analysis_recipes/pipelines/<slug>.yaml (:2687-2689) via new_recipe_draft (libs/blueprint_arch/src/blueprint_arch/new_recipe.py:19-35): info (label, description, author, version 1.0.0, created, tags []), schemas {}, joins {}, plots {} (minimal_recipe). No table, no join, no plot.
- After that: "+ Group" works (create_group setdefault, group_plot_manager.py:113-117). Tables: no control. Joins: the Designer needs ingredients, so none. Plots: "+ Plot" works (needs a group). Target: empty.
- Status: PARTLY (stub and groups and plots; no table, no join, no target). Reasoned: the recipe is not "functional" from nothing; no working path in Blueprint.
- Tests: libs/blueprint_arch/tests/test_new_recipe.py (the pure draft). No handler test of the modal.
- Gate: the modal handler is behind blueprint_agent_enabled (:2641 after :1693).

(l) VALIDATE, SAVE, RELOAD, RUN
- Validate: "Run validation" (btn_bp_validate, :2737; handler :2814-2870). Three checks: validate_data_analysis_recipe (check_recipe through data_analysis_recipe_validator.py:299-315, and check_recipe_file :334), the coherence script as a subprocess (comment :2826-2829), and the data check against the declared fields (:2830-2833). Checks read the files; no node is shown inline (ADR-082 #16 "inline surfacing not wired" was the state in May; the BRANCH shows a panel, bp_validate_ui :2727-2814). Status: PARTLY.
- Save: btn_save_internal, loaded files only; an inline component is refused with a warning (wrangle_studio.py:255; blueprint_handlers.py:1163-1168). Save is never blocked by HOME's gate (:1197).
- Reload: Import (btn_import_data_analysis_recipe), a TubeMap click, a rail click; the selector (dataset_pipeline_selector).
- Run: Apply runs the Glimpse (architect_active_table, wrangle_studio.py:749-752) and the plot (not mounted). A full run is HOME's job (BLUEPRINT.md:81). The Glimpse can fall back to HOME's anchor (see Part 2 findings).
- Autosave: draft written (blueprint_handlers.py:351-364), restored on reload (:1008; undo list restored :1105-1107). BUILT.
- Undo: NOT BUILT as a control. _undo (:372-379) has no caller in the BRANCH (grep "_undo(" finds only the definition). No keyboard binding found (grep "undo" in app/src/www: none). ADR-082 says "20-step undo" DONE.
- Tests: no test of _undo (grep app/tests: no match for _undo or undo_stack except test_blueprint_failed_load.py:91 as a stub argument).

FINDINGS OF TODAY, VERIFIED AT THE LINES (BRANCH unless DEV)
F1. The plot preview output is not mounted. Read: wrangle_studio.py:712-716 (@output @render.plot architect_active_plot); no output_plot call anywhere in wrangle_studio.py; tests say so (test_shiny_plot_errors.py:16; test_shiny_smoke_blueprint.py:458). Not checked on DEV.
F2. Tapping a node applies that node's steps to another table's data. Read: the Glimpse falls back from processed_data_surgical (None when no anchor is materialised, wrangle_studio.py:607) to processed_data (:600, :661-663), and architect_active_table uses that fallback (:749-752). The strict xfail that pins it: app/tests/test_shiny_blueprint_known_defects.py:17 (BP-GLIMPSE-ANCHOR-1; its header :1-8 says the glimpse "applies a component's steps to HOME's current anchor, another dataset"). The node-click matching (blueprint_handlers.py:1058-1077) is the same on DEV (:1152-1169). Also on DEV: yes, the same code. Note: the claim about "source table node" is the test's wording; I did not reproduce it.
F3. A Save rewrites the whole file, drops "#" comment lines, and writes "comment: <file name>" into each step. Read: whole-file write (blueprint_handlers.py:1190-1191, safe_dump :112); "#" lines dropped (safe_dump, no comments); the default comment = the source file name on load (:508-510, n.pop("comment", source_name)); written back when truthy (:590-592). Tests: test_blueprint_tier_files.py:54-55 PINS the load default; no test pins what Save writes for it (test_blueprint_save_roundtrip.py uses comment ""). So the injection is tested on load, not on save.
F4. The plot-defaults form is registered only when the AI agent flag is on. Read: blueprint_handlers.py:1692-1693 (BRANCH), :1789-1790 (DEV). Wider than the form: see the gate note above (joint designer, groups, meta, new recipe, validate are behind the same return).
F5. Blueprint reads its recipe list from a fixed folder. Read: blueprint_handlers.py:979, :983 (glob *.yaml, not recursive, relative path); :2687 for new recipes.
F6. A step tagged for the other tier is refused on Save on the BRANCH. Read: blueprint_handlers.py:584-587; test :142-145. DEV has no such check (DEV save takes no tier, DEV blueprint_handlers.py:519 and :1278).
F7. The join click returns early when the recipe text holds an !include. NOT FOUND (see (d)).
F8 (extra, verified). The info form writes "name", not "label" (blueprint_handlers.py:2544, :2611-2612); the spec says label (recipe_spec.yaml:14, :86).
F9 (extra, verified). The join Apply cannot be saved to the join file (blueprint_handlers.py:601-604; test :160-163).
F10 (extra, verified). The Joint Designer, group inventory, info form, new recipe, Validate, plot defaults: all behind the agent flag (see the gate note).
F11 (extra, verified). The undo function has no caller (blueprint_handlers.py:372-379).
F12 (extra, verified). The AI agent has three read tools only (agent_tools.py:356-358); its system prompt names a "propose_data_analysis_recipe_diff" tool (agent_context.py:183-198) that is registered nowhere (grep for propose and data_analysis_recipe_diff in app and libs: only agent_context.py).
F13 (extra, verified). The validate panel runs three checks; none of them shows its result on each node.
F14 (extra, verified). The join key rule is in two copies (libs/blueprint_arch/src/blueprint_arch/join_designer.py:30 and the build's DataAssembler; app/tests/test_join_preview_parity.py:3-4). Ledger D-0065 (<contact>, DECIDED; line 94) says one copy in libs/utils.
F15 (extra, verified). The navigator is not on libs/utils recipe_graph (no such module, Glob found nothing). Ledger D-0031 (line 60) decides the rebuild.

=====================================================================
PART 3. THE LINEAGE RAIL AND THE TUBE MAP
=====================================================================
Tube map (BRANCH, libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py).
- BlueprintMapper.generate_cy_elements (:269-437) returns Cytoscape elements as JSON. The app uses this (ADR-039 / UX spec: blueprint_architect_ux_spec.md:95-98). generate_mermaid (:81-268) exists too; the script at :440-451 prints it. Reasoned: the app uses Cytoscape.
- Nodes: data_schemas "trunk" (tier 0; :323-326), additional_datasets "add" (tier 0; :338-341), metadata "meta" (tier 0; :354-355), a "Wrangle" node per table or metadata only if it has tier1 or tier2 (:329-332, :344-349, :357-363; _has_tier :38-42), joins "branch" (tier 2; :373-376), a join's "Wrangle" node (:391-397), plots "plot" (tier 3 in the rank; :415-420), and an INFO node for a plot with no target (:430-435).
- Edges: source to its Wrangle (:333, :348), upstream to a join (:368-371, :388-389; the upstream is the Wrangle if it exists), join to its Wrangle (:396), target to plot (:422-429; the target is the Wrangle of the target if it exists, else the source id).
- Each node has id, label, role, schema_id, tier, group (:295-310). Clicks send schema_id (comment :289-290).
- One Wrangle node per table: tier 1 and tier 2 of a table are shown as one node. The tier label is not in the map.
- Click (BRANCH, blueprint_handlers.py:1032-1077): ignores "INFO_" ids (:1037). Matches ctx_map entries whose safe(schema_id) equals the clicked id (:1064-1067). Priority: join 0, wrangling 1, plot_spec 2, input_fields 5 (:1058-1060); the first with the lowest priority wins (:1068-1071). Then _do_load_component (:1077). A plot node click loads the plot_spec role (role "plot_spec", navigator.py:188-197).
- The tube map does not show empty slots, nor a recipe with nothing in it (no nodes emitted). The stack shows "No active transformation nodes. Click a TubeMap node to load its wrangling steps." (wrangle_studio.py:1851-1856) only when a file is loaded and empty.
- Test coverage of the map: not found (grep for generate_cy_elements and generate_mermaid in app/tests: no match). libs/blueprint_arch/tests/debug_blueprint_mapper.py is a debug script.

Lineage rail (BRANCH, libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py).
- build_sibling_map (:65-202): parses the master without resolving !include and returns ctx: rel path to {role, schema_id, schema_type, siblings {input_fields, tier1, tier2}, ingredients, tier, group_id} (:134-166, :176-200). Roles: input_fields, wrangling, join, plot_spec. A tier file (tier1 or tier2) is registered only when it is an !include (or the schema id itself when inline, :163-166). An EMPTY or absent tier is not registered (_slot :118-132). Plots: registered by file or by id (:180-200); the plot context does NOT carry target_dataset (:188-195).
- build_lineage_chain (:205-323): chain for input_fields or a wrangling file: [input_fields, tier 1, tier 2, the first join that takes the schema as an ingredient] (:293-310). For a join: [each ingredient's tier-1 wrangling (or its input_fields), the join's tier1 and tier2] (:277-291). For a plot: [the best upstream (join, then wrangling, then input_fields, never tier 2), then the plot] only when a target is given (:254-275); without one the chain is just the plot (:244-245 comment).
- Node dict: {rel, schema_id, role, label, is_active}; label gets " (tier 2)" for a tier-2 file (:219-228). This label is BRANCH only: DEV navigator has no such label (grep: none).
- Rail UI: lineage_rail_ui (wrangle_studio.py:1431); upstream, component and downstream panels (ids at :394-416); buttons dispatch via lineage_node_rel (:388, :1479) to handle_lineage_node_click (:1702-1715) which sets selected_lineage_rel; _load_component_from_selection (blueprint_handlers.py:1099-1119) loads the file (_do_load_component).
- Click on a rail node: loads that file's steps into the stack (tier-1 or tier-2 steps of that file; the role decides; :651, :673-679 for wrangling, :681-704 for join, :706-721 for plot).

What the lineage and the map hold today (for building):
- For each file: role, tier (tier1 or tier2 for a table or a join), schema id, schema type, the rel path, the siblings (input_fields, tier1, tier2), ingredients (navigator.py:134-166). Read.
- For each step: its tier (_tier, set when the file is loaded, :491-515, :650) and its file (active_component_path, :655; the default comment = file name, :508-510). The step's tier is known only after loading. Read.
- The order: rail order input_fields, tier 1, tier 2, join (navigator.py:293-310); join: ingredients' tier 1, then the join's tiers (:277-291). Read.
- Which table feeds which join: the ingredients list (navigator.py:103-116, :164, :178). Read.
- Which join or table feeds which plot: the plot's target_dataset is in the plot file (group_plot_manager.py:165 writes it; mapper reads it at blueprint_mapper.py:422-424). The navigator ctx does not carry it (navigator.py:188-195). Read.
- The plot's group (ctx group_id, navigator.py:192; mapper group, :402-406). Read.

What they do NOT hold (read):
- Empty slots: an empty tier is not registered (navigator.py:118-132, :141-158). A table without tier 1 gets no Wrangle node (blueprint_mapper.py:329-332). Nothing shows "tier 1 empty" or "tier 2 missing".
- A recipe with nothing in it: the map draws nothing; the rail is empty (no code shows a message for an empty recipe, grep "No active" etc. not searched beyond wrangle_studio.py:1851).
- Tier 3: not in the navigator (no tier3 role or sibling; navigator.py:141, :193); not in the map except as the plot's own tier number 3 (blueprint_mapper.py:419).
- Tier 2 of a table as its own node in the map (blueprint_mapper.py:329-332).
- The steps themselves: not in ctx; read only on click.
- A plot's target in the rail without an override (navigator.py:244-245, :256-257).
- A join's tier of the step it writes (no tier key in the stack, blueprint_handlers.py:2259).
- The lineage of a column or of a type across tiers (ledger M190, M191; not decided).

DEV difference (read): DEV's navigator has no "(tier 2)" label, and its branch writes one fragment holding tier1 and tier2 together (DEV libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py:872, :903; DEV blueprint_handlers.py:501-503 reads a "tier3" key into tier 2).
