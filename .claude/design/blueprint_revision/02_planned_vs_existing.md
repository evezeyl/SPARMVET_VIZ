# BLUEPRINT-REVIEW-1, step 1b: what was planned against what exists

Written 2026-11-20 night by a worker of BLUEPRINT-REVIEW-1. It builds nothing and decides nothing (D-0395). Nothing was run: the machine was loaded and the order is a reading task. The tree read is `dev` at `4bc3ebac` (the HOME and GALLERY work of that day included).

**Labels.** `[R]` = I read the code at the file:line given, in this tree. `[D]` = taken from a document and not re-checked against the code. "works with format 1 (read, not run)" means: the code uses the keys and names of recipe format 1 as far as reading shows; it has not been run in this review. One browser run exists (2026-11-18, branch before its merge): `01_sources.md` section 9; I name it where it applies.

**Line numbers** are of the files in this branch. `H` = `app/handlers/blueprint_handlers.py` (2941 lines), `W` = `app/modules/wrangle_studio.py` (2328 lines), `N` = `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py`, `M` = `blueprint_mapper.py`.

Sections: A how BLUEPRINT is mounted and gated; B layer L1 navigation; C layer L2 forms; D layer L3 data glimpse; E layer L4 helpers; F the four workflows (new recipe, saving, plot defaults, validation); G the lineage today and the shared graph; H the engines; I what the shared code could give the user (facts for step 4); J the AI agent; K the open choices, unranked; L contradictions between sources; M statements of the 2026-11-18 reports that are out of date.

---

## A. How BLUEPRINT is mounted and gated (a finding that touches everything)

| Fact | Evidence | Label |
|---|---|---|
| BLUEPRINT is the nav item "Blueprint Architect" (value `"Wrangle Studio"`), created only when `blueprint_enabled` is on | `app/handlers/home_theater.py:1811`, `:1871`, `:2319`; ADR-092 | [R] |
| `blueprint_enabled` is on in `developer`, `qa`, `standalone` only; the agent flag only in `developer`, `qa`; the editable escape hatch and the branch editor (`data_analysis_recipe_edit_enabled`) only in `developer`, `qa` | `config/app_features/*.yaml` (a grep of the three flags); the flag table of `rules_app_features_flags.md` says the same | [R] |
| **In `define_server` of the handler, everything after line 1690 is registered only when `blueprint_agent_enabled` is on**: the line `if not bootloader.is_enabled("blueprint_agent_enabled"): return` stops the function. After it come: the plot-defaults form and its Apply (`:1716`, `:1750`), the agent chat, the whole Joint Designer (`:1924` to `:2277`), the groups and plots inventory and its effects (`:2280` to `:2523`), the info form (`:2528`), the "new recipe" dialog (`:2638` to `:2722`), the Validate panel (`:2727`, `:2812`), the draft status (`:2920`) and the import error panel (`:2933`) | `H:1690-1691`; the later definitions are indented at the same level (inside `define_server`) | [R] |
| In `standalone` (BLUEPRINT on, agent off) the left sidebar of `W` still mounts `ui.output_ui("bp_meta_form_ui")`, `bp_groups_inventory_ui`, `bp_validate_ui` and the Joint Designer outputs, but no code renders them: the panels are empty | `W:200`, `:205`, `:238`, `:451` mount; `H:1690` stops the registration | [R] (not seen on a screen with the flag off) |
| The rule says the opposite: "All BLUEPRINT capability remains gated by `blueprint_enabled`" (ADR-082 consequences); the agent flag is to gate the chat only | `architecture_decisions.md` ADR-082 "Persona" line; `rules_app_features_flags.md` Group D | [D] against [R]: contradiction L18 |
| Size: the handler is one function `define_server` from line 310 to the end of the file (about 2630 lines); `W.define_server` runs from line 543 to 1929 (about 1390 lines) | `grep -n '^def \|^    def '` | [R] |
| Naming: three words for one thing: the user space BLUEPRINT, the nav value and the class "Wrangle Studio" / `WrangleStudio`, the title "Blueprint Architect". The rules say to keep user-space and code-module words apart (CLAUDE.md section 1) | `H:972`, `W:114`, `home_theater.py:1811` | [R] |

---

## B. Layer L1: navigation (TubeMap, lineage rail, contract viewer)

| Item | Planned (source) | Exists (file:line) | Format 1 (read, not run) | To verify | Out of date |
|---|---|---|---|---|---|
| The TubeMap: an interactive DAG as the main way to move; click a node to focus | ADR-039 (proposed), ADR-082 L1 "DONE", ux spec zone A | `BlueprintMapper.generate_cy_elements` (`M:265`), Cytoscape.js; click handler `H:1029-1075` picks the node and loads its file `_do_load_component` (`H:627`) [R] | Yes: the structure comes from the recipe graph (`M:62`, `N:114`); a table is drawn only when it writes a tier (`M:41-45`) [R] | A click on a source table loads another table's data (task BLUEPRINT-NODE-CLICK-WRONG-TABLE-1, run 2026-11-18, not re-checked) | The ux spec names Mermaid colours; ADR-039 still "PROPOSED" |
| One node per table plus one "Wrangle" node per table (tier 1 and tier 2 together), one per join, one per plot, plot nodes carry the group | ux spec 2.2; ADR-040 (a per-plot node "between the assembly output and the plot spec") | `M:90-436` [R, header and `_has_tier`] | Draws nothing for an empty recipe or an empty tier (`M:41`) [R] | The empty places are not shown: the owner's principle "see for each step where it sits" (D-0308) asks for it | The "Add plot wrangling" slot of ADR-040 is absent (see C) |
| The lineage rail: the chain of the selected part, from source to plot, clickable | ADR-040; ux spec section 7 (right sidebar) | `W:1431` `lineage_rail_ui` in the tab "2. Interface (Fields)", not in the right sidebar; chain from `build_lineage_chain` (`N:360`) [R] | The chain is built from the sibling map of the recipe (`N:225`), which takes its structure from the recipe graph [R] | Some tables appear twice on the rail (run 2026-11-18) | Contradiction with the ux spec: L17 |
| The three-column contract viewer (upstream, active component, downstream) | ADR-040; ADR-082 L1 | `W:385-437` (the tab shows three stacked cards: upstream, component, downstream) [R] | Planned columns show `output_fields` and `final_contract`, both removed (ADR-100). In the handler the downstream is set to `[]` in every branch I read (`H:679`, `:687`, `:695`, `:727`, `:755`); the card then says "No downstream contract." (`W:1612-1615`) [R] | The second load path (`H:845-894`) was not read in detail | ADR-040 and the ux spec: stale. Result: the viewer is in practice an upstream and a component view |
| Field Gap Analysis: trace a field name through the loaded tiers | ADR-082 (BP-FIELD-GAP-1) | `W:1621` `field_gap_ui`, `W:429` | Reads the loaded fields [R, header only] | Not examined | - |
| Forward-propagation hint ("Forward clear") | ADR-082 (BP-FWD-HINT-1) | Removed (2026-11-17); D-0307: "stays removed" | - | - | `spaces/BLUEPRINT.md` states the removal; ADR-082 still lists it as done |
| Lineage isolation (hide unrelated nodes) | ADR-082 v2 | Not built [R: no such control in `W`] | - | - | - |
| Contract viewer and the new recipe graph: which columns exist at each node | ADR-099 16(i): "the recipe graph knows the columns of every node" | The picker and the viewer use the declared `input_fields` of the table (`H:677-759`, `W:1979-2003`), not the graph's columns or the engine's plan (see G) [R] | A column made by an earlier step (a `polars_with_columns`, a join) is not offered to a later step in a column picker | Parked item "column pickers that follow the lineage" (`03`) | - |

---

## C. Layer L2: forms (picker, form renderer, Join Designer)

| Item | Planned | Exists | Format 1 (read, not run) | To verify | Out of date |
|---|---|---|---|---|---|
| A searchable action picker, filtered by context and category, "shows only valid choices for the current node type" | ADR-075 §3 and §5; ADR-082 #12 "DONE" | `W:333-359`: a search box, a context list (all / t1 / t2 / assembly / plot), "Select action", "Add Node" [R]; catalog `schema_registry.get_actions_for_context`, `search_actions` (`schema_registry.py:82`, `:116`) [R] | The catalog is read from the registry, which holds the prefixed names (`polars_`, `modif_`, `step_`) [R: tests and the agent text use them; `docs/appendix/transformer_actions.qmd` exists] | Whether every action carries a `ui_schema` with a context (ADR-075 says "all 60 actions verified" for May; the registry now has 68, `rules_agent_role_bioscientist.md` §8) | ADR-082's "60 actions"; the picker is not filtered by the recipe's engine (see H) |
| Position rules: the picker offers only actions valid at the selected position; "Invalid positions are blocked" | ADR-075 §5 | No position check beyond the context list; the tier of a new step comes from that list: "T2" gives `tier2`; "assembly", "plot" and empty give `tier1` (`W:802-808`) [R] | A step made under "plot" goes to tier 1. A step for the wrong file is refused on Save (`H:592`, `blueprint_tier_refusal.py`) [R] | The refusal is a provisional rule (D-0308, "stays (provisional)"); ADR-100 says BLUEPRINT "never blocks building" (contradiction L4) | - |
| Add equals Edit: adding a node opens the same form as editing | ADR-082 §5 mandate, task BP-FORMS-UNIFY-1 | `W:807-812`: "Add" appends a stub `{"action", "params": {}, "comment": "", "_tier"}` and selects it; the text says "Click Add, then configure the step in the form on the right and press Apply" (`W:352-353`) [R] | - | Not run | The ADR still calls the primitive add UI a gap |
| The form renderer: eight widgets from `ui_schema` (`column_selector`, `string`, `enum`, `number`, `column_or_literal`, `dtype_picker`, `expression`, `bool`) | ADR-075 §2, ADR-082 §5 | `W:2006` `_render_action_form`; two more widgets for lists and mappings (`list`, `mapping`): `widget_text.py:22-46` [R] | The `list` and `mapping` widgets were built after format 1 (spec section 8, RG1) [R] | The widget vocabulary of the registry: "enum visual preview" (BP-ENUM-PREVIEW-1) is built (`W:56`, `_enum_preview_legend`) [R]; the expression code editor with autocomplete (BP-EXPR-EDITOR-1): not found [R: no such code in `W`, grep for "autocomplete"] | The ADR's widget list |
| Component (plot layer) forms | ADR-082 §5 point 2, BP-COMPONENT-SCHEMA-1 and -FORMS-1; "7 of 191 components have a schema" | The node discriminator `{"component": ...}` and the `__mapping__` node are handled (`W:1`-header, `H:540-570`) [R] | 193 registered components; how many carry a `ui_schema` was not counted | **Count the components with a `ui_schema`** (the ADR number 7 is of May) | The component names have no prefix yet; the rename `plotnine_` / `modif_` / `step_` is decided and not built (D-0091, D-0210 to D-0218): the forms, the agent text, the docs and every recipe name them with the old names |
| Parameters that are library objects (`{name, params}`) | D-0277 | Not built: no widget for a typed value [R: widget list above] | - | Task TYPED-VALUE-FORM-1 | - |
| The Joint Designer: a dedicated pane, two ingredient schemas side by side, composite key pickers, a real-data key-match preview, an audit-gated Apply that emits a canonical join step | ADR-082 Q5, BP-JOINT-1; ux spec 5b | `H:1924-2277` (outputs and effects) and `libs/blueprint_arch/src/blueprint_arch/join_designer.py` (`check_join_keys`, `compute_key_match`, `build_join_step`, `parse_join_step`) [R] | The key check calls `utils.join_keys.join_key_problem`, the one rule that the build also calls (`join_designer.py:50`, `data_assembler.py:84`) [R]. The step name is the registered `polars_join` (fix `b6b40c40`) [D: commit message; not re-read] | The join Apply puts the step on the in-memory logic stack (`H:2266`); a join file cannot be saved from BLUEPRINT: the serialiser refuses the role `join` (`H:609-611`: "Editable roles: plot_spec, wrangling") [R] | The test file `app/tests/test_join_preview_parity.py` says the rule "lives twice"; the code has one function. The earlier digest (C7) is out of date (see M) |
| Group and plot creation: an inventory list with create, delete, move | ADR-082 Q6, BP-GROUPS-1; `group_plot_manager.py` | `H:2280-2523` (inventory and effects); `group_plot_manager.py` (pure CRUD, writes through `_IncludeDumper`) [R] | Uses `ui_label` (`group_plot_manager.py:95`) [R] | Whether a write through the include dumper keeps comments: not checked; delete refused for a group with plots (digest, not re-checked) | The inventory exists only with the agent flag (see A) |
| Info or metadata form for the recipe | ADR-082 #7 BP-META-1 | `H:2528-2636` | The form reads and writes `info.name` (`H:2544`, `:2606-2609`); format 1 uses `info.label`, and the new-recipe draft writes `label` (`new_recipe.py:23`) [R]. It saves with `yaml.dump` through `_IncludeDumper` and no backup (`H:2630-2634`) [R] | Whether the checker refuses `info.name` (spec: "pending"; `01_sources.md`) | Contradiction L6 |
| Comment field on each node (`comment:`) with a good-practice hover | ADR-082 Q4, BP-COMMENTS-1 | A `comment` key per step exists in the stub and in the serialiser (`H:594-597`, `W:807`) [R]. A tooltip: not searched | A step's comment is set on load from the file name (the digest reports "the file name is the default comment set on load", run 2026-11-18; not re-checked) | Whether a save writes `comment: <file name>` into each step (BLUEPRINT-SAVE-COMMENTS-1 says so) | - |
| Pattern helper shared with Test Lab; "pattern matching escalation" | BLUEPRINT.md; ADR-082 #14 "v2, deferred" | Not built [R: no such module in `blueprint_arch`]. The shared primitives exist in `libs/utils/src/utils/id_patterns.py` (rules_test_lab.md 2c) [D] | - | - | - |

---

## D. Layer L3: the live data glimpse and the plot preview

| Item | Planned | Exists | Format 1 (read, not run) | To verify | Out of date |
|---|---|---|---|---|---|
| Preview on Apply: the glimpse and the plot recompute when the user presses Apply | ADR-082 Q1 (ratified), L3 "DONE (glimpse only, Q7)" | Apply handler `_bp_apply_node_handler` `H:1199-1385` [R]; the glimpse data comes from the orchestrator (`H:750` "Surgical materialization") [R header] | Reads tiers through the orchestrator (read, not run) | The click on a node loads the data of another table (task BLUEPRINT-NODE-CLICK-WRONG-TABLE-1) | - |
| Zone C: the plot preview and the data, always visible | ux spec section 6 | The plot output `architect_active_plot` is defined (`W:713-716`) but **no `ui.output_plot` mounts it anywhere**: `output_plot` appears only in `home_theater.py` for HOME's plots [R] | The preview dict takes the recipe's `plot_engine` through `plot_engine_slot` (`W:689`) [R] | - | ADR-082 states "DONE" for preview: contradiction L9. Task BLUEPRINT-PLOT-PREVIEW-NOT-MOUNTED-1 waits for the owner |
| Data inspection: glimpse only, no profiler | ADR-082 Q7 | A data grid [D] | - | - | - |

---

## E. Layer L4: helpers (AI agent, YAML escape hatch, undo, branching)

| Item | Planned | Exists | Format 1 (read, not run) | To verify | Out of date |
|---|---|---|---|---|---|
| YAML escape hatch: always visible (read only); editable with `data_analysis_recipe_edit_enabled` | ADR-075 §7; rules_ui_dashboard.md:203 | Tab "3. YAML (Raw Source)" (`W:439`); the editable text and its Save: `H:1424-1462` [R] | The Save of the hatch parses the text (`yaml.safe_load`, which does not read `!include`), then sets `active_raw_yaml` and a signal; **it writes nothing to disk** [R]. Saving a component (`btn_save_internal`) writes the nodes of the logic stack (steps) and takes only the other keys from the raw text (`H:530-614`) [R] | Whether a YAML edit of steps in the hatch reaches the logic stack (not traced) | Rule text says the hatch "emits a `developer_raw_yaml` T3 node on save": the node type is removed (task AUDIT-RAWYAML-REMOVE-1, done 2026-11-15 [D]) |
| Undo: a 20-step session undo | ADR-075, BP-UNDO-1; rules_ui_dashboard.md:202 "(2) 20-step session undo deque"; ADR-082 "implemented" | `_snapshot_state` fills the stack at three places (`H:370`, calls at `:1227`, `:1356`, `:2259`); `_undo` (`H:376-383`) has no caller anywhere in `app/` (`grep '_undo()'`) [R] | - | Task UNDO-WIRE-1 (the owner decides where the trigger goes) | Rule text, the in-app help (`blueprint.md`, "Undo") and ADR-082 say it exists |
| Remove one step; reorder steps | ADR-075 "edit/remove after Apply"; ADR-040 "arrows and a delete button on each card" | The stack view has one control: "Clear All nodes" (`W:379`) [R]; per-step controls not found by reading | - | Whether the stack cards have a remove and arrows (the digest of 2026-11-18 says "only clear all"; run) | The rule text says "edit in place + re-Apply" is layer one |
| Branching: split a lineage at a node, upstream shared, the divergent downstream as new `!include` fragments | ADR-082 Q3 (LOCKED), BP-BRANCH-NODE-1; BLUEPRINT.md terminology | `H:1470-1665` (preview and write, only with `data_analysis_recipe_edit_enabled`); the pure part `generate_branch_plan` (`N:933`) edits the master by text insertion; the divergent fragments are written empty [R header and `N:914`] | Writes `tier1` only; "Tier 2 is not written: an absent tier 2 means the table of tier 2 equals the table of tier 1" (`N:914`) [R] | Open design question: does BLUEPRINT find the branch node or the user choose it (ADR-082 §2a: "decided at task time") | The creation of a tier 2 file is possible only through a branch (digest, not re-checked) |
| Autosave of the draft (restore after reload) | ADR-082 §2a (DECIDED, BP-AUTOSAVE-1) | `H:126-190` (`_write_bp_draft`, `_read_bp_draft`), the effect `H:354-367`, the restore `H:1004-1012` [R]; gated on `automation.ghost_save.enabled` | Keyed by a hash of the recipe file (`H:126`) [R header] | The `qa` setup turns it off | - |
| The AI agent | see J | see J | see J | see J | see J |

---

## F. The four workflows

### F1. Creating a new recipe

| | Planned | Exists | Format 1 | To verify |
|---|---|---|---|---|
| A new recipe from scratch | ADR-082 #2, BP-NEW-1; BLUEPRINT.md "Open/create"; ADR-082 §2 text "The usual start is a boilerplate template" | A dialog asks id, name, description, author (`H:2638-2722`); `new_recipe_draft` (`new_recipe.py:19-35`) builds a recipe through `utils.recipe_factory.minimal_recipe` with `info.label`, no table, no join, no plot, and `write_recipe` writes it [R]. It writes into the fixed folder `config/data_analysis_recipes/pipelines` (`H:2685`) [R] | Valid in profile `build` only (docstring) [R]. The slug must match `^[a-zA-Z_][a-zA-Z0-9_]*$` (`H:2636`): a hyphen is refused [R] | A fresh draft has no plot and the app's loader refuses a recipe without a plot, so it cannot be opened in HOME (task line 220, "one strict xfail test records it") [D]; whether BLUEPRINT's own open works on it was not checked |
| What is missing for a whole recipe | D-0306: "It needs to be able to build the whole recipe"; D-0308: tier 1, then tier 2, then tier 3, then the plot | No control: add a table (its file, its fields and types, the entity key); create a tier 1 or tier 2 file except through a branch; choose a join's tier; the plot's target table, title, `plot_engine`; the recipe's `entity`; the engines [R by absence; the 2026-11-18 report lists the same] | - | This list is the "gap report" of D-0306 for the space; it was written on 2026-11-18 on the branch (`01_sources.md` section 9) |
| The name of the file | D-0390 to D-0392: `name_date`, ISO date, for production recipes | The new-recipe dialog does not add a date; it refuses a hyphen | - | The study `.claude/design/studies/scratch_records_2026-11/panel/recipe_places` recommends that the app add `_YYYY-MM-DD` itself at the final save and that the typed slug may stay as it is |

### F2. Saving: what is written, where

| Action | Writes what | Where | Backup | Keeps comments | Evidence |
|---|---|---|---|---|---|
| Save (`btn_save_internal`, a button in a hidden box) of a plot or a tier file | The steps (or mapping and layers) of the logic stack, as a block `{data_engine?, steps}` or the plot entry; other keys of a plot entry kept | The component file itself, opened with `"w"` (overwrite in place) | None | No: `yaml` dump through `safe_dump_recipe` (`H:114`); the 2026-11-18 run: comment lines 14 to 2 | `H:1152-1195`; `H:530-614` [R] |
| Info save | `info` keys (`name`, `description`, `author`, `version`, `tags`) | The recipe master file | None | No (`yaml.dump`) | `H:2586-2636` [R] |
| Group and plot CRUD | Groups and plot entries | The master file (and a new plot file) | None found | Not checked | `group_plot_manager.py` [R, header] |
| Branch write | New empty fragments and text insertion in the master | The recipe folder | None | Text insertion leaves other lines unchanged (header of `generate_branch_plan`) [R] | `H:1600-1640`, `N:933` |
| New recipe | A new file | `config/data_analysis_recipes/pipelines/<slug>.yaml`, refused if it exists | n/a | n/a | `H:2685-2697` [R] |
| Download | A zip of the recipe tree | The browser | n/a | n/a | `H:1386-1421` [R] |
| Upload (replace / append) | The uploaded recipe files | The recipe folder; "would replace silently" (the study) | - | - | `H:1117-1150`; `ingestion_handlers.py:44-51` [D] |

Plan against fact: D-0174 "A Blueprint save keeps the comments of the recipe file (option a)" is decided and not built (BP-COMMENTS-1 "not started"; waits for a library question). ADR-091 gap 1 and CONFIG-STEPS-WRITE-1 plan "a timestamped backup, then a draft copy in the user's data location, then an explicit publish"; none exists. D-0393 and D-0394 add: a dated file for the final save, replace allowed only in the user's own place. After each save the app re-runs HOME's gate for the changed recipe and tells the author (`tell_save_outcome`, `H:279-293`, called at `:1195`) [R].

Also found: Save is refused for a step whose tier differs from the file's tier (`H:592`); a file that holds audit steps is refused (`H:600-601`); a join file and any other role are refused (`H:609-611`). The Save button itself sits in a `display:none` box (`W:248-258`); the tests click it by script (`app/tests/test_shiny_smoke_blueprint.py:413`) [R]. The 2026-11-18 run found "no visible Save button" on both trees; I did not find another mount of `btn_save_internal` [R].

### F3. The plot defaults form

| | Planned | Exists | Out of date |
|---|---|---|---|
| A form for `plot_defaults` at the recipe root | VIZFAC-BLUEPRINT-FORM-1 (`plot_config_cascade.md:302`); D-0246: fix the bug first and alone, then add fields for common theme settings | `H:1716-1771`: palette (text) and theme (list) only; "Apply to session" writes `plot_defaults` into the in-memory config and says "Changes are session-only. Edit YAML directly to persist." [R]. The fix `ea8c1738` keeps the seed and the layers (`app/modules/plot_defaults_form.py:43`) [R] | The tasks BP-FORM-FIX and BLUEPRINT-PLOT-DEFAULTS-FORM-1 still say "open". The in-app help still lists font, facet spacing and legend (removed keys). The form is saved nowhere (not written to the file). It needs the agent flag (A) |

### F4. Validation ("Validate")

| | Planned | Exists | To verify |
|---|---|---|---|
| Validate: errors and warnings inline before saving | ADR-082 #16, BP-VALIDATE-1; ADR-094: manual and advisory for BLUEPRINT; ADR-100: BLUEPRINT uses the profile `build` and "never blocks building" | `H:2727-2916`: one button, three checks merged into one pass/fail: (1) `validate_data_analysis_recipe(path)` (`H:2844`) with the **default profile `run`** (`data_analysis_recipe_validator.py:401`), not `build` [R]; (2) a child process of the script `audit_data_analysis_recipe_coherence` whose markdown output is parsed by the text "## Result: ✅ PASS" (`H:2866`), counting "factory_id key" violations among others [R]; (3) the data against the declared contract (`H:2884-2893`) [R]. Advices (J12, J13) are shown, never blocking [R, `H:2900`] | The results show no mark on each node of the map (the 2026-11-18 digest, not re-checked). Whether the `run` profile is intended for BLUEPRINT is open: the spec says `build` for BLUEPRINT (`recipe_format_spec.md:230`). The upload report uses `build` (`data_analysis_recipe_validator.py:295`) |
| Open a recipe that fails; show each failing point as a point to fix | The owner's wish (ledger "asked, not decided", line 440; task BP-STALE-VIEW-1: options A, B, C) | On a failed load the view is blanked and the problems are shown (`H:389-400`, `:249-256`); no fix list from the checker per problem | The owner's choice among A, B, C was not made |
| Warnings and errors look different; all warnings shown in BLUEPRINT | D-0059, D-0079; WARNINGS-LOOK-1 | Not checked | - |

---

## G. The lineage: what BLUEPRINT uses today against the shared graph and the walk

| Piece | Where | Used by | Used by BLUEPRINT? |
|---|---|---|---|
| `N` `recipe_structure`, `build_sibling_map`, `build_lineage_chain`, `build_schema_registry`, `resolve_fields_for_schema`, `generate_branch_plan`, `build_plot_lineage` | `libs/blueprint_arch` | BLUEPRINT, the export | Yes [R]. Since slice A (commit `fb37c514`, merge `ecd09fbd`) the structure (which table feeds which join, which plot reads which table) comes from `utils.recipe_graph.build_graph` (`N:79`, `:114-135`); what the graph cannot draw is listed in `left_out` [R]. The fields come from `load_fields_file` (declared `input_fields`) and the sibling map, as before |
| `utils.recipe_graph` (672 lines): nodes `DS:`, `T1:`, `T2:`, `T3:`, the steps of each node, the columns of a node when a `columns_provider` is given | `libs/utils` | HOME's audit, the checker, the cache keys, BLUEPRINT's navigator | Structure only. BLUEPRINT passes no `columns_provider` [R: `build_graph(work)` in `N:122`] |
| `utils.lineage_walk` (775 lines): for a column, the places where a step can be written (back, forth, back again) | `libs/utils` | HOME's audit (`home_theater.py`, `filter_and_audit_handlers.py`, `session_handlers.py`) | **No** [R: grep of `lineage_walk`, `plan_composer`, `plan_book`, `step_effects` finds none in `app/handlers/blueprint_handlers.py`, `wrangle_studio.py` or `blueprint_arch`] |
| `utils.plan_book`, `utils.step_effects`, `app/modules/plan_composer.py`: the plan (column names and types) of every place of a recipe, composed from the build's own lazy frames, nothing built or stored | `libs/utils`, `app` | HOME's audit | **No**. A column picker in BLUEPRINT is filled from the declared fields of the table (`W:1979-2003`), not from the plan |

Plan (ADR-099 16(d), D-0031): "Blueprint's navigator is rebuilt on [the graph] so there is one source of truth". Fact: built for the structure; not for the columns. The decided answer to "how does the app know which columns a table has at each place" is the plan of every place (D-0325); the ledger says "Blueprint is out of this choice", so whether BLUEPRINT uses it is open.

---

## H. The engines

| Question | Plan | Fact |
|---|---|---|
| Where is the engine written in a recipe | D-0029, D-0219, D-0236: `data_engine` and `plot_engine` required at the top; a tier or a plot entry may override (D-0250: a tier is its own key with an optional `data_engine`; D-0252: a plot entry may hold `plot_engine`) | `libs/utils/src/utils/engines.py`: `ENGINE_TABLE` has two rows: `python-polars` (key `data_engine`, library `transformer`, prefix `polars_`) and `python-plotnine` (key `plot_engine`, library `viz_factory`, prefix `plotnine_`) (`engines.py:45-48`) [R]. A new recipe gets the first engine of each list (`recipe_factory.py:161-162`) [R] |
| What the registry records per entry | D-0238: a field `engine` on every action and component | `ACTION_ENGINES` and `COMPONENT_ENGINES` (`base.py:26`, `registry.py:27`, `:49-81`) [R]. `engine_registry.engine_tables()` hands them to the checker, which refuses a step under another engine's block [R] |
| Where the engine is chosen at run time | D-0219: "The code MUST choose the engine" | `app/modules/engine_registry.py`: `data_entry`, `plot_entry`; an engine with no library is refused with the words of D-0239 [R] |
| Does BLUEPRINT let the user choose an engine | The owner (order): "the engine 'language' will need to be able to be selected in the blueprint" | **No control**. In `W` and `H` the engine appears only in three places: the plot preview passes the recipe's `plot_engine` (`W:688-689`), the tier file keeps its own `data_engine` on save (`H:604-605`), and the plot entry's `plot_engine` is kept as a key (`H:535`) [R]. The action picker (`schema_registry.py`) does not read the `engine` field: it lists all actions and all components whatever the engine of the recipe [R: grep "engine" in `schema_registry.py` is empty] |
| What the app has | D-0252: "No new engine is added now" | One data engine and one plot engine. The exploration notes name R with ggplot2 and dplyr as options (not decided; a survey: "an engine per plot: sound; per data tier: large and risky; per step: no") [D] |
| What a second engine would change in BLUEPRINT | not written | By reading: the picker would have to filter by the engine of the tier or plot being edited (the field exists in the registry); the new-recipe form would have to offer the engine list; the form widgets are built from `ui_schema`, which each engine's entries would have to carry; the help and the agent text name Polars and plotnine objects. Open: where in the screen the engine of a tier or a plot is shown and changed [reasoned] |

---

## I. What the shared code could give the user (facts for step 4, not proposals)

- The recipe graph knows, for each table and each plot, its tiers and what feeds what (`recipe_graph.py`). The map and the rail could show empty tiers and tier 3 from it (the owner's principle D-0308 asks the user to see where each step sits).
- The plan composer returns the column names and types after each step of every place, without building or storing a table (`plan_composer.py:1-30`), with a failure as a value. A form could offer, for a step at tier 2 or tier 3, the columns that really exist there, with their types, and could warn when a cast turns decimals into integers (the parked items of D-0376 and D-0374 need the same knowledge).
- The lineage walk lists, for a column, the places a filter or drop can be written and what each reaches. HOME uses it for audit steps; BLUEPRINT has no such need stated, but the owner wrote (D-0309) that the lineage and the tube map are "also to leverage".
- The checker (`check_recipe`, profile `build`) gives coded problems with the place and the fix; BLUEPRINT's Validate shows them as a list (F4) and not on the nodes.
- The engine registry knows the engine of each action and component; a picker could show only what the engine of the part being edited can run.
- What the shared code does not give: a way to propose a step; the rules of "good practice" for the order tier 1, tier 2, tier 3 (D-0308) exist as text in `config/ui/agents/blueprint_default.md` and in `rules_agent_role_bioscientist.md`, not as code.

---

## J. The AI agent: planned against built

Her words (order, step 5): "We had only planned to add - not all was build - will be integrated in CLI and via API".

| Part | Planned (ADR-076, `adr076_mvp.md`, `adr076_mvp2_backend_options.md`) | Exists | Label |
|---|---|---|---|
| Adapter protocol | `AgentAdapter` with `start_session`, `send_message`, `end_session` | `agent_adapter.py:59-74` | [R] |
| Backend `claude_cli` | Subprocess `claude -p` in an isolated directory `agent_sessions/{uuid}/`, POSIX lock, an authentication probe at start | `ClaudeCliAdapter` (`agent_adapter.py:117-340`): the command line uses `--output-format text`, `--system`, `-p`, `--continue` (`:272-280`); no `--disallowedTools` or `--allowedTools` flag anywhere in the file [R] | [R] |
| Hidden native tools of the CLI | The MVP-2 note (§3b): `claude -p` runs Claude Code with its own Read, Write, Edit, Bash; nothing restricts them; options B1 (use the API), B2 (add the flags), B3 (a test that tries to write outside) | Not done (above) [R]. The note says the flags may not hold in all versions [D] | [R] |
| Backend `claude_api` | Phase 2: the `anthropic` SDK, `ANTHROPIC_API_KEY`; the config keys `model`, `api_key_env` exist in `developer.yaml`/`qa.yaml` (`model: "claude-opus-4-7"`, noted stale in the options note: current models are `claude-sonnet-5-5`, `claude-opus-5-5`) | `make_adapter` returns `DisabledAdapter("... not implemented in Phase 1")` for `claude_api` and `local` (`agent_adapter.py:398-403`) [R]. Task BLUEPRINT-AGENT-API-1 "reminder for about 2026-11-14" | [R] |
| Backend `local` (Ollama-like, air-gapped) | Phase 3 | Not built | [R] |
| Tools | Three read-only in MVP-1 (`get_available_actions`, `get_available_components`, `get_field_contract`); MVP-2 adds `propose_data_analysis_recipe_diff` plus an apply gate and others | The three exist (`agent_tools.py`); `get_field_contract` now returns the `input_fields` and the tiers, no `output_fields` (`agent_tools.py:1-8`, D-0075) [R]. The diff tool and the apply gate do not exist [R: the only occurrences of `propose_data_analysis_recipe_diff` are text in `agent_context.py:183-198`] | [R] |
| The system prompt names a tool that does not exist | - | `agent_context.py:183-198` tells the agent that all changes go through `propose_data_analysis_recipe_diff` ("THE ONLY PATH to propose changes"): no code registers it; ADR-076 names the tool `propose_manifest_diff` | [R] contradiction L10 |
| Tool-call mechanism | Fenced JSON blocks, a parser, at most 3 rounds | `agent_tool_parser.py`; `H:1861-1897` (`for _round in range(3)`) | [R] |
| Instructions file | One file, editable (`config/ui/agents/blueprint_default.md`); MVP-2 §5 proposes role files (`config/ui/agents/roles/recipe_builder.yaml`) for what the agent may do | The one markdown file exists, 202 lines, with prefixed action names and unprefixed plot names; no role file; no `allowed_tools` check in `call_tool` [R: `agent_tools.py:370`] | [R] |
| The chat panel | A conversation, an input, one request at a time, a greeting, a status banner | `H:1774-1920`; mounted in the right sidebar through the `blueprint_agent_chat` panel (`config/ui/sidebars/blueprint_standard_right.yaml`) [R] | [R] |
| Start-up cost | - | A probe at start can wait up to 40 seconds with no message (task AGENT-PROBE-1, "to confirm with the owner") [D] | [D] |
| Where the agent may write | The owner (2026-11-09): only the one recipe of the session; read the app's code, never write it | The agent writes nothing today (read-only tools). The rule is not enforced in code for the CLI backend (hidden native tools) | [R] |
| Report of a session | BP-AGENT-REPORT-1 | Dropped from MVP-1 (`adr076_mvp.md`); a `conversation.jsonl` is written by the adapter (`_append_conversation_log`, `agent_adapter.py:362`) | [R] |
| Advise or enforce | ADR-082 §2a: "advise-only, NEVER blocking", Socratic; BLUEPRINT.md says "advises and enforces good practices" | The text is in the instructions file | contradiction L11 |
| Switch off | The owner asked that the feature be fully switchable off with no effect on BLUEPRINT | The options note §7: "already built, confirmed" [D]. What I found in the code is the opposite for the other controls: with the agent switched off, the groups, the new-recipe dialog, Validate, the Joint Designer and the plot defaults also vanish (A) | [D] against [R] |
| Her wish for "CLI and API" | The two backends side by side, chosen in the app features file | CLI built, API not; the choice is `blueprint_agent.backend` in the app features file | [R] |
| The recipe-to-Python research (PY-RESEARCH) | A research item "recipe to Python and back, and the BLUEPRINT AI agent"; "start only after the visualisation library is done" | Not read in full | - |

---

## K. The open choices (unranked; the ranking is the work of the guide)

Each is open or only proposed. I list the choice and where its options are written; I do not rank or recommend.

1. **The order of the whole work.** BLUEPRINT after HOME (D-0348) and after the big recipe change; a minimal BLUEPRINT only where forced (D-0271). What "minimal" covers is not written.
2. **What BLUEPRINT is as a whole**: the global picture (D-0309): the 2026-11-18 picture holds 15 open questions (`GLOBAL_PICTURE.md` section F) and 18 contradictions (section G).
3. **How a whole recipe is built from empty**: how a table enters a recipe (a Test Lab boilerplate, a field editor, a branch copy), how tier files are created, how a join is saved, how the plot's target, title and engine are set (D-0306).
4. **The engine "language" in the screen** (H): where it is shown and changed (recipe, tier, plot), whether the picker filters by it, what happens to a form when a second engine exists.
5. **Whether and how BLUEPRINT uses the lineage and the plan**: the map and the rail as the backbone (D-0309), columns from the plan in the pickers, empty places shown, the tier shown on each step (D-0308 "see for each step where it sits").
6. **What a step in the wrong tier does** (D-0308): refuse, two files, no tier picker, guide the order (the four options the records name); the refusal is provisional today.
7. **Does BLUEPRINT ever block**: ADR-100 "never blocks building", the Save refusal, the ADR-075 "invalid positions blocked", the agent "never blocking".
8. **Tier 3**: BLUEPRINT may author it (D-0063); the button "Add plot wrangling" must come back with the text of D-0305; whether the engine reads a plot's tier 3 and how (open in the records; the 2026-11-18 tier-3 facts page is in `.claude/design/studies/scratch_records_2026-11/engine_keys/TIER3_facts_2026-11-18.md`, not read).
9. **Where recipes are read and written**: the deployment's place against the fixed folder; common against own place; the final dated save; overwrite control; who may write (the study `recipe_places`, 11 decisions P1 to P11).
10. **What a save does to the file**: comments kept (D-0174, decided, library question open), backup, the `comment:` written on each step, the file name rule.
11. **The AI agent**: the API adapter and its model (A), what protects the app from the CLI's native tools (B), where the best-practice text lives (C), one file for the agent's role and rights (D), the key (E), and whether the apply gate is built before the agent is shown to scientists.
12. **The agent flag and the other controls** (A): which controls must not depend on it.
13. **The plot recipe in BLUEPRINT**: mapping, layers, labels, theme, defaults, typed values `{name, params}` (D-0277), the rename of the components (decided, not built), the theme fields (D-0246, after the demo), where the plot figure is shown.
14. **Information to the user** parked for BLUEPRINT: undeclared file columns (D-0374), a warning when values are cast to integer (D-0376), join counts (JOIN-COUNTS-1), warnings distinct from errors (D-0059, D-0079).
15. **The label key**: `info.name` against `info.label` against `ui_label` (D-0253 decided it for groups and plots).
16. **The state of the old tasks and the documents**: which of the old ADR-082 tasks are now done (see M and `03`) and which texts to correct (the help, the user doc, the rule file).

---

## L. Contradictions between sources (listed, not resolved)

Numbers L1 to L18 follow the global picture of 2026-11-18 (`G1` to `G18` there) where it already lists the item; "new" marks what I found.

- **L1 Tier 3 in BLUEPRINT.** D-0063 and the note of 2026-11-15 in ADR-100: "Blueprint MAY author the plot entry's tier 3". `rules_ui_dashboard.md:188` and `:13`, `spaces/BLUEPRINT.md` ("BLUEPRINT never authors T3"), ADR-082 Q2 and §4 (marked "superseded 2026-11-15"), and `docs/workflows/blueprint_architect.qmd:146` ("a hard invariant", not updated), and a code comment `H:1157` ("BLUEPRINT never authors T3") say the opposite. Fact: the app does not read or write `tier3` of a plot except to pass it through (`H:574-579`) [R].
- **L2** audit and the plot spec: D-0029 "audit never writes a plot spec" against DEC17 of the spec (a recipe maker may write any action at the plot's tier 3). [D]
- **L3 Comments.** ADR-082 Q4: `#` comments "NOT preserved ... accepted limitation". D-0174 and ADR-100 point 2: kept "by every tool". Fact: not kept (`H:1188`: the file is rewritten from the logic stack) [R].
- **L4 Blocking.** ADR-100 point 3 "never blocks building" against the Save refusal (`H:592`) kept provisionally (D-0308).
- **L5 Figure text.** ADR-100 point 9 (axis titles default to the field label) against D-0253 (figure text only in `labs`). [D]
- **L6 Info keys.** The format and the new-recipe draft: `label`; the info form: `name`. [R]
- **L7 One join-key rule.** D-0065 and the code (one function `utils.join_keys.join_key_problem`) against the test file docstring "The rule lives twice" (`app/tests/test_join_preview_parity.py:3-4`) and the 2026-11-18 digest C7. The code is right; the sentence is stale [R].
- **L8 The "Add plot wrangling" button.** D-0305 "stays"; the tree has no such button [R].
- **L9 Done or not.** ADR-082 "Preview DONE" and "20-step undo DONE" against: the plot output is not mounted, `_undo` has no caller [R].
- **L10 Agent tool name.** ADR-076 `propose_manifest_diff`; the prompt `propose_data_analysis_recipe_diff`; no code registers either [R].
- **L11 Advise or enforce.** ADR-082 §2a "advise-only, NEVER blocking" against `spaces/BLUEPRINT.md:97-98` "enforces good practices".
- **L12 Escape hatch and tier 3.** `rules_ui_dashboard.md:203` ("emits a `developer_raw_yaml` T3 node on save") against `:188`; the node type is removed.
- **L13 Old key.** `developer_workflow.md:89` ("`final_contract` ... the developer's job in BLUEPRINT") against ADR-100 point 5 (removed).
- **L14 Invalid positions.** ADR-075 §5 "blocked at authoring time" against ADR-100 point 3.
- **L15 Tier 2.** ADR-075 puts tier 2 "after a join/assembly node"; the format gives every table a tier 2.
- **L16 What tier 3 is.** Spec line 7 ("build, reshape and finally audit a table") against D-0306 ("T3 : data plot specific").
- **L17 Where the rail is.** The ux spec (right sidebar, sections 1 and 7) against the code (tab 2, `W:1431`).
- **L18 What the agent flag gates.** ADR-082 and the flag rule: the chat only; the code: the chat and most of the other controls (A).
- **L19 (new) Which profile BLUEPRINT's Validate uses.** The spec and ADR-100: `build`; the code: the default `run` (`H:2844`, `data_analysis_recipe_validator.py:401`) [R].
- **L20 (new) The agent can be switched off "with no effect on BLUEPRINT".** The options note §7 says "already built, confirmed"; the code (A) shows an effect on the other controls [D] against [R].
- **L21 (new) The in-app help and the code.** The help (`blueprint.md`) lists plot-default keys that were removed, an undo that has no control, and an agent that "requests changes".
- **L22 (new) The state of tasks.** `tasks.md` lists BP-FORM-FIX and BLUEPRINT-PLOT-DEFAULTS-FORM-1 as open; the code and a test show the fix (commit `ea8c1738`, `app/tests/test_blueprint_plot_defaults_form.py`). BLUEPRINT-GLOBAL-PICTURE-1 and BLUEPRINT-PLOT-RECIPE-BUILDER-STUDY-1 are open in the file; their products exist in `tmpAI`.
- **L23 (new) The size of the numbers in the rules.** ADR-082's "all 60 actions"; today 68 actions (`rules_agent_role_bioscientist.md` §8) and 193 plot components registered; the "7 of 191 components have a schema" of May is not updated.

---

## M. Statements of the 2026-11-18 reports (gap digest, global picture) that no longer hold

I compared them with the tree of 2026-11-20. Each is [R] unless noted.

1. "BRANCH = `task/engine-keys`; dev differs." The branch is merged into `dev` (`feat/recipe-format-1` is in the history of `HEAD`; `app/modules/blueprint_tier_refusal.py` exists). The differences "branch only / dev only" no longer apply: today dev has the tier refusal on Save, no "Add plot wrangling" button, no "Forward clear" hint.
2. "The plot does not open for editing ('Imported 0 steps'), branch only" (run). Fixed by `5892a872` (the includes are read as YAML, quoted or not) and by the test changes `fa7f856b`, `4d2aeaef`, `d740c217`, `84762c12`. Not re-run in this review.
3. "The join rule exists in two copies." Now one function (L7).
4. "Plot defaults: dev writes four removed keys; the form drops the seed." Fixed by `ea8c1738`.
5. "The navigator draws structure itself." Now it takes the structure from the recipe graph (G; `fb37c514`, `ecd09fbd`); a further change (`c76f906a`) makes the export and BLUEPRINT's refresh read the recipe once.
6. "A join built in the Designer writes the wrong step name." Fixed (`b6b40c40`, a commit message; not re-read).
7. "The agent flag gates the Joint Designer, the groups, Validate ..." Still true (A); the digest's statement "not run with the switch off" is still true: no run was made here either.

Not re-checked in this review (taken from the 2026-11-18 run, so possibly changed): no per-step remove or reorder; the file name written as the default comment of each step; the nodes of some tables appear twice on the rail; the Validate result is not shown on the nodes; a join file cannot be saved (this I confirmed by reading, section C).

---

## What this file does not do

It does not check the recipe-handling code paths by running them; it does not count how many components have a `ui_schema`; it does not read the second load path (`H:845-894`), the Apply handler body (`H:1199-1385`) or the Joint Designer preview in detail. These are listed in the "to verify" columns.
