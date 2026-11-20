# BLUEPRINT-REVIEW-1, step 1a: the sources on BLUEPRINT

Written 2026-11-20 night by a worker of BLUEPRINT-REVIEW-1 (D-0395: "it builds nothing and decides nothing; it produces a guide for the rebuild of BLUEPRINT after the planned refactoring, with the larger decisions ranked first"). Read only; nothing was run.

How to read it. Every source has a path, a date if the text states one, a status and three lines. Status words: **decided** (the owner or an accepted ADR), **proposed** (waits for her), **design note** (analysis, nothing decided), **built** (the code does it), **superseded** or **stale** (a later text replaces it, or it names removed things). The status is what the text says about itself, plus a note where I read the code and found a different state ("read": I read the code at that line; "document": I took it from a text and did not re-check).

Where the sources contradict each other, the contradiction is listed in `02_planned_vs_existing.md` section L. It is not resolved here.

---

## 1. The design files of the user space

| Path | Date | Status | What it says (three lines) |
|---|---|---|---|
| `.claude/design/spaces/BLUEPRINT.md` | last updated 2026-05-20 | design file, "Build (feature set locked by ADR-082)"; stale in places | BLUEPRINT is a click-button IDE that builds a recipe visually (nodes, forms, DAG, lineage) with no code; the output is a valid recipe that HOME loads. It lists 15 user functionalities, the non-goals, the design constraints (library-aware, TubeMap is the main navigation, positive inclusion, AI advises and never blocks) and a "Current State (verified 2026-05-20)" that is out of date (it still lists the removed forward-propagation hint as done). The open questions are answered inline by the owner (preview on push, branches as separate fragments, escape hatch yes, undo and autosave, same libraries as HOME, AI advises only with a definition file) |
| `.claude/knowledge/blueprint_architect_ux_spec.md` | last updated 2026-05-02 | design file, "Partially implemented"; stale in places | The screen: a three-zone "Flight Deck" (zone A TubeMap, zone B tabs Focus / Interface / YAML / Joint Designer, zone C plot preview and live data, always visible), the node colours, the lineage rail in the right sidebar, the click bridge. It still shows `output_fields` and `final_contract` columns (removed by ADR-100) |
| `.claude/design/adr076_mvp.md` | status "SCOPED 2026-05-09" | design note (what MVP-1 contains) | Narrows ADR-076 to a read-only conversation: the `claude_cli` adapter and a disabled fallback, three read-only tools, a system prompt file, a chat panel, the flag `blueprint_agent_enabled`. Out of scope: the diff tool and apply gate, the API and local adapters, the data tool. Promotion criteria from MVP-1 to MVP-2 (a real session, a parse-error rate below 1 in 20, acceptable tempo) |
| `.claude/design/adr076_mvp2_backend_options.md` | "OPTIONS FOR REVIEW (2026-11-09)" | design note; nothing decided, nothing built | Status check of ADR-076 against the code, then five decisions for the owner: A how to build the API adapter (SDK, agent SDK, or harden the CLI), B how to enforce "the agent may not touch app code" (propose-before-apply, the hidden native tools of the CLI), C where the best-practice knowledge lives, D one file for what the agent may do and its role, E where the API key is stored. Her follow-up of 2026-11-09 is recorded (only the recipe of the session, read the code never write it, one file to adjust the agent) |
| `.claude/design/outdated/blueprint_full_feature_set_research.md` | prepared 2026-05-09, resolved 2026-05-20, moved here 2026-11-12 | superseded by ADR-082 (kept for history) | The research draft with the seven open questions of the feature set. Every question was answered in ADR-082 |
| `.claude/design/plot_authoring_model.md` | 2026-05-20 | design, accepted through ADR-083; partly stale | One canonical plot model (mapping and ordered layers) shared by the renderer and by BLUEPRINT's forms, with a normalise and a serialise function. The key `factory_id` is removed. Parts of it name keys the format 1 amended (`spec:`, `label`) |
| `.claude/design/developer_workflow.md` | last updated 2026-05-22 | design; stale in places | The producer's journey TEST_LAB, BLUEPRINT, GALLERY, HOME. Names BLUEPRINT's hand-offs (a recipe is saved to disk and HOME picks it up; no in-app crossing, ADR-093). Line 89 still says `final_contract` is "the developer's job in BLUEPRINT" |
| `.claude/design/plot_config_cascade.md` | accepted 2026-05-10 | design; built except the BLUEPRINT form task | The five-level cascade of the plot configuration. Names the task VIZFAC-BLUEPRINT-FORM-1 (a plot-defaults editor in BLUEPRINT). It lists keys that were later removed (see D-0236, D-0242) |
| `.claude/design/recipe_format_spec.md` | "DRAFT, cleaned on 2026-11-13" (943 lines) | the specification of recipe format 1; mostly decided | What BLUEPRINT must write: the key `info`, the tier keys (`tier1`, `tier2`, `tier3`), the engines `data_engine` and `plot_engine`, `ui_label` and `ui_title`, the registry fields, the profiles of the checker (`build` for BLUEPRINT, which "reports and never blocks building"), section 8 on the form schema (RG1: no widget for a list or a dictionary, built as `widget_text.py`), the note of 2026-11-15 "Blueprint MAY author the plot entry's tier 3". Line 322: one adapter serves HOME's gate and Blueprint's Validate |
| `.claude/design/exploration/2026-11-17_engines_default_and_override.md` and `2026-11-17_engine_fields_plan.md` | 2026-11-17 | design notes; the plan was decided in part (D-0219, D-0236 to D-0240, D-0247, D-0248) | An engine per recipe, per tier and per plot; R with ggplot2 as a second plot engine is "a sound feature to plan", an engine per data tier is "large and risky for correctness", an engine per step "no". The plan's finding 5 is a bug in BLUEPRINT's plot-defaults form (fixed, see section 5) |
| `.claude/design/exploration/2026-11-17_theme_snippets_design_note.md`, `2026-11-17_recipe_arguments_without_code.md` | 2026-11-17 | design notes | Named themes copied into the recipe (a list in BLUEPRINT, preview, two copy buttons: new); how arguments that are library objects are written (D-0277: `{name, params}`); both name work for BLUEPRINT's forms that is not built |
| `.claude/design/exploration/2026-11-18_test_lab_review.md` and `2026-11-17_author_manifest.md` | 2026-11-17, 2026-11-18 | design notes | Mention BLUEPRINT only in passing (a contact field, the Test Lab to BLUEPRINT hand-off) |
| `.claude/design/ui_reachability_map.md` | 2026-11-08 | design | Where a cross-cutting surface is guaranteed to exist; alerts moved to the left sidebar of every space |
| `.claude/design/feature_extension/` (`r_backend.md`, `bioinformatics_viz.md`, ...) | not stated | design notes, "survey-gated, nothing scheduled" (from the project memory) | Possibility documents for an R backend, trees, maps, a second dashboard. Not read in detail; they matter for the engine "language" question |
| `.claude/design/uml_model_plan.md` | not stated | design | The plan of the UML model; see section 8 |

## 2. The ADRs that name BLUEPRINT

Source: `.claude/knowledge/architecture_decisions.md` (5390 lines; I read only the sections named). The "stale" notes below are the ones the file itself carries (ADR-SYNC-1, 2026-11-14).

| ADR | Date, status | What it decides for BLUEPRINT | State |
|---|---|---|---|
| ADR-039 The Blueprint Architect Workflow and TubeMap (line 521) | April 2026, "PROPOSED" | The "Flight Deck": a TubeMap at the top (Tier 1, Tier 2, Assembly, Plot), click a node to focus, a right sidebar with the logic steps, a live viewer, visual forking | still "PROPOSED" in its header although ADR-082 calls it the owner of the map; built (Cytoscape instead of Mermaid) |
| ADR-040 Bidirectional Lineage Navigation and Interface Fields (line 560) | 2026-04-20, "PARTIALLY IMPLEMENTED" | A lineage rail (the chain of one component) and a three-column contract viewer (upstream, active, downstream). Forward build and backward trace | stale: the columns show `output_fields` and `final_contract` (removed, ADR-100) |
| ADR-067 Extract `libs/blueprint_arch/` (line 2100) | 2026-05-05, implemented | The pure logic of BLUEPRINT lives in `libs/blueprint_arch`; Shiny wiring stays in `app/handlers/blueprint_handlers.py` | partly stale: the navigator is rebuilt on the shared recipe graph in `libs/utils` (ADR-099 point 16(d)); built in slice A (see `02_planned_vs_existing.md` section G) |
| ADR-073 Configurable Sidebar Slot Registry (line 2380) | 2026-05-09 | BLUEPRINT's left and right sidebars come from the slot registry (`blueprint_main` freestanding, `blueprint_surgeon`, `blueprint_action_help`, `blueprint_plot_defaults`, `blueprint_branch_node`, `blueprint_agent_chat`) | built (read: `config/ui/sidebars/blueprint_standard_*.yaml`) |
| ADR-074 Lineage Infrastructure as Shared Provision (line 2602) | 2026-05-09, "DECIDED, implementation pending" | `build_plot_lineage` and `get_plot_ids_in_group` serve HOME's export and BLUEPRINT | partly stale (placement superseded in part by the shared graph) |
| ADR-075 BLUEPRINT IDE Build Mode (line 2714) | 2026-05-09, "DECIDED, implementation pending (Phase 31+)" | The `ui_schema` embedded in the registering decorators; the eight widgets; position rules (the picker offers only valid actions at the selected insertion point); help from the docstrings and `wraps`; a colour model; the escape hatch; undo | partly built; stale: action names (now `polars_`, `modif_`, `step_`) |
| ADR-076 BLUEPRINT AI Agent Helper (line 2911) | 2026-05-09, "MVP-1 IMPLEMENTED" | An adapter protocol with three backends (CLI, API, local) and a disabled one; the agent never changes the recipe itself (every change through a diff tool and the user's Apply); subprocess isolation; the flag `blueprint_agent_enabled` | MVP-1 built; the API and local adapters and the diff tool are not built (read: `agent_adapter.py:398-403`); stale: the tool `get_field_contract` and `final_contract` |
| ADR-077 Configuration Validation Discipline (line 3233) | 2026-05-09 | Fatal cascade: `blueprint_agent_enabled` and `data_analysis_recipe_edit_enabled` need `blueprint_enabled` | built |
| ADR-081 Deployment Palette Registry and Palette Injection (line 3725) | 2026-05-09 | The palette of a recipe; the plot-defaults form of BLUEPRINT reads it | built; the `plot_defaults` schema was later reduced |
| ADR-082 BLUEPRINT Full Feature Set and Build-Mode Contract (line 3803) | 2026-05-20, "ACCEPTED, decided with Eve" | The umbrella: four layers L1 to L4, the answers to seven questions (preview on Apply, T3 never in BLUEPRINT, branch = bifurcation at a node, `comment:` keys, a dedicated Joint Designer, group and plot inventory in the sidebar, glimpse only), 18 functionalities with MVP / v2 / out of scope, the form unification mandate (Add equals Edit, components too), the implementation order | header notes: "Partly stale (2026-11-14)": the three-column viewer shows `output_fields`; Q2 and section 4 "BLUEPRINT never authors T3" are superseded on 2026-11-15 by D-0063. Its state column is out of date (see `02_planned_vs_existing.md`) |
| ADR-083 Canonical Plot Model and BLUEPRINT Authoring Seam (line 3944) | 2026-05-20, accepted | One plot model; `factory_id` and flat aesthetics removed; plot forms use `normalise_plot_spec` and `serialise_plot_spec` | built; its `_meta` passthrough is retired (unknown keys fail) |
| ADR-091 Final configuration names (line 4396), ADR-092 One flag for the Blueprint Architect (line 4512) | 2026-11-07 | `blueprint_enabled` alone controls BLUEPRINT; the recipe `id:` equals the file name. ADR-091 gap 1: BLUEPRINT writes into the recipes location although the guide says it is read-only; interim: warn and keep a timestamped backup, target: a draft copy in the user's data location | built for the flag; the gap 1 interim is not built (read: no backup in the save, `blueprint_handlers.py:1152-1195`) |
| ADR-093 Remove Gallery's T3 clone (line 4531) | 2026-11-08 | No space writes into another's state; no GALLERY to BLUEPRINT hand-off | built; its rule "BLUEPRINT never authors tier 3" is superseded by D-0063 |
| ADR-094 HOME gates automatically; BLUEPRINT stays manual (line 4580) | 2026-11-08 | HOME checks each recipe at start; BLUEPRINT's "Validate" is manual and advisory, never blocks | HOME part changed later by D-0184 (a recipe is checked when it is selected) |
| ADR-099 Exploration and audit mode (line 5055), point 16 | 2026-11-11 | (d) the recipe graph is new shared code in `libs/utils` and BLUEPRINT's navigator is rebuilt on it; (j) the recipe declares `data_engine` and `plot_engine`; (i) one mechanism for every removal, the graph knows the columns of every node | (d) built in slice A (read); the column knowledge is not used by BLUEPRINT (read) |
| ADR-100 Recipe format version 1 (line 5201) | 2026-11-12 to 2026-11-14 | One checker with profiles; BLUEPRINT reports and never blocks building; `output_fields` and `final_contract` removed; prefixes `polars_`, `modif_`, `step_`; note of 2026-11-15: BLUEPRINT may author the plot entry's tier 3 | the checker is built; BLUEPRINT's save still refuses a wrong-tier step (see contradictions) |
| ADR-104 No silent error (line 5318), ADR-105 Audit acts along the lineage (line 5345), ADR-106 The visualisation library follows the recipe standard (line 5366) | 2026-11-14 | Plot components judged as strictly as the gallery; every silent path becomes an error; the names `plotnine_`, `modif_`, `step_` for plot components (note of 2026-11-15, D-0091) | ADR-106 V5 built; the rename NOT built (read: 193 registered components, none with a prefix) |

## 3. Rule files

| Path | Date | What it says about BLUEPRINT | State |
|---|---|---|---|
| `.claude/rules/rules_ui_dashboard.md` section 7 (line 175) | file changed 2026-11-20 (the section text is from May) | "The Blueprint Architect Invariants": the four layers, branching as bifurcation, the central vertical stack (TubeMap, live visualisation, glimpse), the Joint Designer, IDE Build Mode (forms from `ui_schema`, action picker by context, apply gate, edit/remove in three layers incl. a 20-step undo), the YAML escape hatch (editable only with `data_analysis_recipe_edit_enabled`) | stale: line 188 "BLUEPRINT never authors T3" against D-0063; line 203 says the editable escape hatch "emits a `developer_raw_yaml` T3 node on save" (that node type was removed, AUDIT-RAWYAML-REMOVE-1) |
| `.claude/rules/rules_app_features_flags.md` Group D (line 85) | not dated | `blueprint_enabled` gates the space; `data_analysis_recipe_edit_enabled` the editable escape hatch and the branch editor; `blueprint_agent_enabled` the chat; both child flags are fatal without `blueprint_enabled`. Flag matrix: BLUEPRINT is on in `standalone`, `developer`, `qa` only (read: the same in `config/app_features/*.yaml`) | current; the matrix says nothing of the fact that many BLUEPRINT controls need the agent flag (see `02_planned_vs_existing.md` section A) |
| `.claude/rules/ui_implementation_contract.md` (section 11d, line 400 to 409) | updated 2026-11-20 | The sidebar panel types of BLUEPRINT and the freestanding panel concept | current |
| `.claude/rules/rules_app_structure.md` section 2 | not dated | Lists `blueprint_handlers.py` as "~2800 lines" and `wrangle_studio.py` as "~2360 lines, the largest module" | the numbers are about right today (2941 and 2328, read: `wc -l`); no hard limit is written for them (the hard limit of about 250 lines is for `server.py`) |
| `.claude/rules/rules_agent_role_bioscientist.md` | not dated | The agent role of the "@bioscientist": what a recipe must look like. Not BLUEPRINT's agent, but the source of the best-practice text that the agent instructions copy | current in the names (prefixed actions) |
| `.claude/rules/rules_viz_factory.md` section 1a | decided 2026-11-15, 2026-11-17 | The plot component names `plotnine_`, `modif_`, `step_`: "The rename is NOT built" | accurate (read) |

## 4. The decisions of the owner that name BLUEPRINT (ledger)

Source: `.claude/knowledge/decision_ledger.md`. Number, date, one line. Only lines taken by the owner are decisions; where a line is a reading of the review session the ledger says so, and I note it.

**The space and its order of work**
- D-0007, 2026-11-07: one flag `blueprint_enabled`; the recipe `id` equals the file name; no top-level `type:`.
- D-0048, 2026-11-14: order of work: HOME, then Gallery, Blueprint and Test Lab last.
- D-0271, 2026-11-18: order of work: HOME and GALLERY first; Blueprint and Test Lab only where the big recipe change forces it.
- D-0272, 2026-11-18: the demo comes after the big recipe change.
- D-0348, 2026-11-20: "Blueprint is taken after HOME: when the HOME design is finished it is known what Blueprint can reuse from it and what must be built new." (the coordinator's wording)
- D-0381, 2026-11-20: BLUEPRINT, GALLERY and TEST_LAB use the same width and drag mechanism for their side panels as HOME; their side panels are likely always visible (working direction).
- D-0395, 2026-11-20: this review (fallback task BLUEPRINT-REVIEW-1). D-0396: the same kind of review for the Test Lab.

**What BLUEPRINT must be and build**
- D-0306, 2026-11-18: BLUEPRINT is "the ui ide for building our recipes" and "needs to be able to build the whole recipe"; tier 1 and tier 2 must be buildable; the gap report is asked for.
- D-0307, 2026-11-18: the "Forward clear" hint stays removed; she wants to be sure BLUEPRINT can still build tier 1 and tier 2 (a proof by a run; its order later set by M336: HOME and GALLERY first, then this check; the entry `BLUEPRINT-TIER1-TIER2-PROOF-AFTER-HOME-GALLERY`).
- D-0308, 2026-11-18: her principle: build as the specification says; the normal order is tier 1, tier 2, tier 3, the plot; the tool builds a functional recipe and advises the user against mistakes; the user sees for each step where it sits.
- D-0309, 2026-11-18: the BLUEPRINT design is revisited before it is built: the lineage and the tube map are to be leveraged; a global clear picture first, then the evaluation of solutions, then the build plan.
- D-0063, 2026-11-15: BLUEPRINT MAY author the plot entry's tier 3; tier 3 is a data step, not the plot recipe.
- D-0305, 2026-11-18: the button "Add plot wrangling" stays and points to tier 3; a way to build the plot recipe in BLUEPRINT is a need.
- D-0029, 2026-11-12: `data_engine` and `plot_engine` required; audit never writes a plot spec; HOME rejects, BLUEPRINT reports.
- D-0031, 2026-11-12: the recipe graph is in `libs/utils`; BLUEPRINT's navigator is rebuilt on it; no shim, no half fix.
- D-0079, 2026-11-15: BLUEPRINT shows all warnings; errors and warnings look different. D-0059: row order and ties: warnings distinct in the checker, HOME and BLUEPRINT.
- D-0065, 2026-11-15: one pure join-key rule in `libs/utils`, called by the build, the BLUEPRINT preview and the checker. D-0068: the BLUEPRINT join preview catches only expected errors. D-0075: `get_field_contract` stops returning `output_fields`.
- D-0174, 2026-11-16: a BLUEPRINT save keeps the comments of the recipe file (option a).
- D-0143, 2026-11-16: BLUEPRINT edits recipes for creation; the audit adds steps to a copy named `audit_recipe`.
- D-0374, 2026-11-20: informing the user about file columns the recipe does not declare belongs to BLUEPRINT (decided, not built).
- D-0376, 2026-11-20: note for BLUEPRINT: when values of a file are cast to integer, the recipe maker gets at least a warning (not built).

**The engines and the names (what BLUEPRINT must follow)**
- D-0036, 2026-11-13: prefixes `polars_`, `modif_`, `step_` for actions; a `polars_` action is exactly Polars.
- D-0091, 2026-11-15; D-0210 to D-0214, D-0218, 2026-11-17: the plot components follow the same procedure (`plotnine_`, `modif_`, `step_`); shortcut components removed; full parity of 30 objects; both spellings registered; names written as values stay plotnine's; the rule goes into `rules_viz_factory.md`. Not built.
- D-0219, 2026-11-17: the engine fields are used, not kept as placeholders; the top of the recipe gives the default engines, a tier or a plot may override.
- D-0236, 2026-11-17: format 1 is amended before its first release; no format 2. D-0238: every registry entry carries a field `engine`. D-0239: the engine names are an open list; an app without the library refuses with "no library for this engine in this app". D-0240: cache keys and the engine. D-0247, D-0248: the entry file of each engine library; `effective_run.yaml` records engines. D-0250: a tier is its own key with optional `data_engine`. D-0252: a plot in its own file holds the whole entry; "No new engine is added now."
- D-0253, 2026-11-18: figure text only in the `labs` layer; `label` becomes `ui_label`, a new `ui_title`.
- D-0243, D-0244, D-0246, D-0256, 2026-11-17 and 2026-11-18: named themes are copied (D-0243) but "Themes are code" (D-0256: no theme folder, no theme file, a registered component); D-0246: fix the plot-defaults form first and alone, then add the theme fields.
- D-0277, 2026-11-18: a typed value is written `{name, params}`; the form follows.

**Where recipes are written and how they are named**
- D-0390, 2026-11-20: a recipe file name is `name_date`; an upload under an existing name is refused. D-0391: the date is ISO `YYYY-MM-DD`; to verify: a hyphen in a recipe name. D-0392: the rule covers production recipes only. D-0393: the dated file is for a final save; a typo edit may replace the previous file; only specific users may modify the common recipes; a place the user can read and write is needed. D-0394: an overwrite control only in the user's own directory; one study of the places (the file `tmpAI/panel/recipe_places/TABLE_FOR_THE_OWNER.md` is its result; see section 9). D-0184, 2026-11-16: a recipe is checked when it is selected.
- D-0102, 2026-11-15: two recipes: the original and the audit copy; BLUEPRINT edits the original.

**The agent and the tests**
- D-0263, 2026-11-18: every child process uses `sys.executable`. D-0303, 2026-11-18: a review of the configuration files waits until just before her own testing of HOME and BLUEPRINT.

**Asked, not decided** (the section at the end of the ledger, lines 436, 440, 500, 510): the seed field linked to the steps that use jitter, changed only in audit and BLUEPRINT (open); BLUEPRINT must open a recipe that fails and show each failing point as a point to fix ("investigate, no build yet"); named default themes with a form beyond the copied block (open); how the app knows which columns a table has at each place (Q-A4, since decided as D-0325: the plan of every place; BLUEPRINT is out of that choice).

## 5. The tasks in `.claude/tasks/tasks.md` that name BLUEPRINT

State as the file says; where I read the code and the file is out of date, the second column says so. (913 lines; line numbers are of the file in this branch.)

| Task | Line | State in the file | Check |
|---|---|---|---|
| BLUEPRINT-REVIEW-1 | 678 | open (this task) | - |
| BLUEPRINT-TIER1-TIER2-PROOF-AFTER-HOME-GALLERY | 752 | open; supersedes the gate of BLUEPRINT-T1-T2-PROOF-1 | a proof run exists for the branch of 2026-11-18 (`tmpAI/engine_keys/BLUEPRINT_T1_T2_PROOF.md`); the merge happened without a gate |
| BLUEPRINT-T1-T2-PROOF-1 | 723 | marked superseded | - |
| BLUEPRINT-GLOBAL-PICTURE-1 | 721 | open in the file | the picture was written 2026-11-18 (`tmpAI/panel/blueprint_gap/GLOBAL_PICTURE.md`): the entry is stale |
| BLUEPRINT-PLOT-RECIPE-BUILDER-STUDY-1 | 720 | open; corrected to a gap report | the gap report exists (`tmpAI/panel/blueprint_gap/GAP_REPORT_full_part1..4.md`): stale |
| BLUEPRINT-DESIGN-FINDINGS-1 | 750 | findings, not a build task | lists the known defects (see `03`) |
| BLUEPRINT-AFTER-RECIPE-1 | 125 | open: "records what will have to change afterwards" | the register it points to ("evidence file, section 5") is not in this tree; not found |
| BLUEPRINT-CHECK-RECIPE-1 | 127 | open: a "Check recipe" action later (W14) | the "Fix Format" button is removed (read: no such control); the later action is not built (read) |
| BP-FORM-FIX | 598 | open | built: commit `ea8c1738` (read: `app/modules/plot_defaults_form.py`, `merged_plot_defaults`): the entry is stale |
| BLUEPRINT-PLOT-DEFAULTS-FORM-1 | 553 | open ("defect, waits for Eve's yes") | fixed by `ea8c1738` (read): stale |
| BP-FORM-THEME-FIELDS | 599 | open, after the demo | not built (read: the form has palette and theme only) |
| THEME-BUILDER-PROPOSAL-1, PROPOSAL-NAMED-THEMES-BLUEPRINT | 566, 594 | proposals | not built; D-0256 says themes are code |
| BLUEPRINT-HELP-STEP-MODIF-1 | 586 | deferred by the owner | the help of `step_` and `modif_` is not written (read: `app/src/help/blueprint.md`) |
| BLUEPRINT-REMOVED-BUTTON-AND-HINT-1 | 718 | the button must come back with the text of D-0305 | not back (read: no "Add plot wrangling" in `wrangle_studio.py`) |
| BLUEPRINT-TIER-REFUSAL-MESSAGE-1 | 725 | open (wording to be approved) | the refusal exists (`app/modules/blueprint_tier_refusal.py`); commit `ade69f0b` changed the wording |
| BLUEPRINT-PLOT-PREVIEW-NOT-MOUNTED-1 | 713 | open, waits for the owner | confirmed (read: `architect_active_plot` has no `output_plot`) |
| BLUEPRINT-NODE-CLICK-WRONG-TABLE-1 | 714 | open | not re-checked |
| BLUEPRINT-SAVE-COMMENTS-1 | 697 | open; extended 2026-11-18 | D-0174 decided that a save keeps the comments; not built (BP-COMMENTS-1, line 474, "not started"; needs a library question for the owner: ruamel.yaml) |
| BLUEPRINT-RECIPE-LOCATION | 646 | waits for the owner | confirmed (read: fixed folder at `blueprint_handlers.py:975`, `:2685`) |
| BLUEPRINT-RECIPES-FOLDER-IGNORES-DEPLOYMENT | 751 | "for the owner; the Blueprint pass" | the same fact as the line above (two entries for one subject) |
| BLUEPRINT-UNDECLARED-COLUMNS | 880 | not started (D-0374) | not built |
| BLUEPRINT-CAST-TO-INTEGER-WARNING | 885 | not built (note of D-0376) | not built |
| UNDO-WIRE-1 | 261 | open: `_undo()` has no button | confirmed (read: no caller of `_undo`, `blueprint_handlers.py:376`) |
| BP-STALE-VIEW-1 | 266 | open: after a failed load only a console line; options A, B, C for a fix list; the owner's choice not made | the code now blanks the view and shows the problems (`_fail_load`, `blueprint_handlers.py:389-400`): partly addressed (read); the "fix list" is not built |
| BP-COMMENTS-1 | 474 | not started | see BLUEPRINT-SAVE-COMMENTS-1 |
| CONFIG-STEPS-WRITE-1 | 201 | open: BLUEPRINT writes into the recipes location and overwrites in place | confirmed (read: `open(comp_path, "w")` at `blueprint_handlers.py:1188`; no backup) |
| BLUEPRINT-AGENT-API-1 | 278 | open, "reminder for about 2026-11-14" | `make_adapter` still degrades `claude_api` and `local` to the disabled adapter (read: `agent_adapter.py:398-403`) |
| AGENT-PROBE-1 | 436 | to confirm with the owner | not re-checked |
| PY-RESEARCH | 411 | research, not a decision: recipe to Python and back, and the BLUEPRINT AI agent | not read in full |
| WARNINGS-LOOK-1 | 358 | open: all warnings shown in BLUEPRINT; error and warning look distinct | not re-checked |
| JOIN-COUNTS-1 | 136 | provisional: rows in/out per join shown to the user (BLUEPRINT among them) | not built (read: no such text in the Joint Designer code) |
| GATE-GAP-1 | 134 | defect: a recipe saved from BLUEPRINT is not checked again by HOME | addressed: `tell_save_outcome` re-runs HOME's gate after a save (read: `blueprint_handlers.py:279-293`) |
| TYPED-VALUE-FORM-1 | 388 | open (D-0277) | not built |
| V1-B-RENAME | 387 | decided in principle; not built | confirmed (read) |
| S2-3-Q | 399 | investigation only: a recipe changed while in use (BLUEPRINT saves during a HOME session) | not built |
| EXPORT-TUBEMAP, UX-PLOTSTYLE-1 | 342, 344 | deferred | not built |

The older BP-* tasks of ADR-082 (BP-FORMS-UNIFY-1, BP-COMPONENT-FORMS-1, BP-JOINT-1, BP-GROUPS-1, BP-META-1, BP-NEW-1, BP-VALIDATE-1, BP-AUTOSAVE-1, BP-BRANCH-NODE-1, BP-COMMENTS-1 and others) are not open entries in this `tasks.md` any more (grep finds only the entries above); their state is in `02_planned_vs_existing.md`, taken from the code.

## 6. User documentation, in-app help, library readme

| Path | Last commit date | Status | Note |
|---|---|---|---|
| `docs/workflows/blueprint_architect.qmd` (392 lines) | 2026-11-18 | stale in places (read) | Eight sections: the four layers, the surfaces, the workflow Open to Save, branching, the plot model, the Joint Designer, the agent, the other surfaces. Section "BLUEPRINT never writes Tier 3" (line 146) states "a hard invariant" against D-0063. No `polars_` name in it (a count of 0); it names `mutate.expression` (line 104) and the removed `factory_id` (as history) |
| `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd` (471 lines) | 2026-11-18 | current in the names (16 uses of `polars_` / `modif_`) | The user's steps: define a data schema, join, plots, the form against YAML, branching, validation, examples. Still uses unprefixed plot names (`geom_bar`), as the rename is not built |
| `app/src/help/blueprint.md` (46 lines) | 2026-11-15 | stale (read) | The "Plot Defaults" paragraph lists "Default font family", "Facet panel spacing", "Legend position" (removed keys, D-0220, D-0242); the "Undo" paragraph says to use the undo stack but no control exists; the "AI Agent" paragraph says "request changes" but the agent has no tool to change anything |
| `libs/blueprint_arch/README.md` (240 lines) | 2026-11-18 | current (read: says "format 1 has no `output_fields`") | The public API of the library |
| `config/ui/agents/blueprint_default.md` (202 lines) | not dated | partly stale (read) | The agent's instructions. Uses the prefixed action names (current). Uses the unprefixed plot name `geom_bar` (line 162). The prompt built in `agent_context.py:183-198` names a tool `propose_data_analysis_recipe_diff` that no code registers |
| other `docs/**` that mention BLUEPRINT | | | `docs/workflows/ui_app_features.qmd`, `docs/workflows/developer_workflow.qmd`, `docs/foundations/core_architecture*.qmd`, `docs/deployment/deployment_guide.qmd` (says the recipes location is read-only, ADR-091 gap 1), `docs/UML/risks_and_technical_debt.md`, others. Not read line by line |

## 7. The code (pointers; the facts are in `02`)

`app/handlers/blueprint_handlers.py` (2941 lines), `app/modules/wrangle_studio.py` (2328 lines), `app/modules/blueprint_plot_view.py`, `app/modules/blueprint_tier_refusal.py`, `app/modules/plot_defaults_form.py`, `libs/blueprint_arch/src/blueprint_arch/` (4631 lines in 14 files), `config/ui/sidebars/blueprint_standard_{left,right}.yaml`, the shared `libs/utils/src/utils/recipe_graph.py` (672 lines), `lineage_walk.py` (775), `plan_book.py` (96), `step_effects.py` (242) and `app/modules/plan_composer.py` (369). Tests: `app/tests/test_blueprint_*.py` (13 files), `app/tests/test_shiny_smoke_blueprint.py`, `test_shiny_blueprint_known_defects.py`, `test_agent_adapter_at_startup.py`, `libs/blueprint_arch/tests/` (13 test files).

## 8. The UML model (`docs/UML/app.mdj`, names only; the file is 3.1 MB)

Elements named for BLUEPRINT (found by reading the names in the file, not by running the audit): the model package `BLUEPRINT`; the diagrams `UC-BLUEPRINT What a user does`, `COM-REACTIVE-BLUEPRINT Reactive wiring of BLUEPRINT`, `UI-BLUEPRINT The screen`, `C4-COMP-BLUEPRINT Inside BLUEPRINT` (pictures in `docs/UML/diagrams/`); the use cases "Navigate the lineage via the TubeMap", "Design a join in the Joint Designer pane", "Copy an example YAML by hand for BLUEPRINT"; the components `BLUEPRINT handlers`, `blueprint_arch`, `blueprint_handlers`, `blueprint_mapper`; the processes `blueprint_agent_panel_ui`, `joint designer handlers (x5)`, `joint designer panels (x5)`, `_autosave_blueprint_draft`; the package `blueprint_arch` and the flag attributes. Not checked: whether these diagrams still match the code (the rule `workspace_standard.md` asks for the check after a change; `audit_uml_model.py` was not run).

## 9. Prior work in the main tree (git-ignored, not in git: it can be lost)

These files were written before this review. They are in `tmpAI/` of the main tree `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/`, which git ignores. Recommendation to the coordinator: have a scribe copy the two that the guide will quote into this folder.

| Path | Date | What it is | How far it still holds |
|---|---|---|---|
| `tmpAI/panel/blueprint_gap/GAP_DIGEST_for_eve.md` and `GAP_REPORT_full_part1..4.md` | 2026-11-18 | The gap report of D-0306: the recipe part by part (what BLUEPRINT builds today, what it cannot), the rail and the map, decided / to confirm / open, 14 contradictions, known defects. "Nothing was run" | Written on the branch `task/engine-keys` before its merge. Four of its statements are out of date (see `02`, section M): the branch is merged into `dev`; the navigator is now on the recipe graph; the plot-open regression is fixed; the plot-defaults form no longer writes removed keys |
| `tmpAI/panel/blueprint_gap/GLOBAL_PICTURE.md`, `GLOBAL_PICTURE.svg`, `GLOBAL_PICTURE_sources.md`, `progress_global_picture.md` | 2026-11-18 | D-0309 step 2: the global picture (the journey from an empty recipe to a working one in 12 stations, the screens, the map and the rail, what stops a user, 15 open questions, 18 contradictions G1 to G18). Chooses nothing | Same limits as above. The best single source for step 2 of the order |
| `tmpAI/engine_keys/BLUEPRINT_T1_T2_PROOF.md` and `tmpAI/engine_keys/bp_proof/` | 2026-11-18 | A browser run (Chromium, `qa` app features) of BLUEPRINT on the branch and on `dev`: what could be built, what not (no visible Save button, a join cannot be saved, plots do not open on the branch) | The only evidence of a RUN. Two of its findings were fixed afterwards (plot open: `5892a872`; join step name: `b6b40c40`) |
| `tmpAI/panel/recipe_places/TABLE_FOR_THE_OWNER.md`, `architect.md`, `scientist.md`, `user.md`, `BRIEF.md`, `M418_owner_answers_and_study_order.md` | 2026-11-20 night | The study of D-0394: three models M1, M2, M3 for where recipes live and who writes; 11 decisions P1 to P11 for the owner; four safe steps; one of them is "BLUEPRINT reads the deployment's recipe folder" | Current. Nothing decided |
| `tmpAI/engine_keys/step4_REVIEW.md`, `step4_fixes_report.md`, `TIER3_facts_2026-11-18.md`, `blueprint_plot_open_report.md` | 2026-11-18 | Evidence for the BLUEPRINT tasks of section 5 | Not read in this step |

## 10. What I did not find

- The "register" that BLUEPRINT-AFTER-RECIPE-1 points to (`evidence file, section 5`): not in this tree.
- The old (pre-ADR-082) user-space specification beyond `spaces/BLUEPRINT.md` and the UX spec: `.claude/conversations/archive/` holds one 2026-03-08 file on "Agent stop" that I did not open; no other earlier BLUEPRINT specification was found by name.
- Any audit log that is a design review of BLUEPRINT: the audit logs (`.claude/logs/audits`, 406 files) that mention BLUEPRINT are the routine audits (dependency checks, template checks, code checks) and name BLUEPRINT only as a file or a flag; I found none that is a review of the space. Not all 406 were read.
