# `.claude` map: what is recent, what is in force, what is old

**Written 2026-11-13 (cleanup).** The status words: **RECENT (redesign)** = written since 2026-11-11, the HOME and recipe redesign; **IN FORCE** = rules, decisions and workflows that agents obey (change them only with Eve's double confirmation); **AS BUILT / reference** = describes the app as it is today or an earlier decision still valid; it changes when the redesign is built; **ON HOLD / PAUSED / ROADMAP before the redesign** = read the note; **HISTORY** = kept for the record in an `outdated/`, `archive/` or `archives/` subfolder of the same directory; **LOG** = dated records, append-only. 'Last change' is the last commit date that is not a bulk rename or move (many files show 2026-11-07 only because of the vocabulary rename).

## Start here

1. `CLAUDE.md` (project root, Eve's file) and `.claude/rules/workspace_standard.md`: the rules.
2. `.claude/tasks/tasks.md`: the **ACTIVE MAP** at its top: what is current, superseded and older.
3. `.claude/design/home_audit_reading_guide.md`: the HOME redesign: order of work, decision register, reading list.
4. `.claude/design/spaces/HOME.md`: the whole of HOME in one place (built or target).
5. `.claude/design/home_stage2_mechanism_spec.md`: the build plan P0-P12.
6. `.claude/design/recipe_format_spec.md`: the recipe format (the recipe session).


## `.claude/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `settings.json` | IN FORCE (settings) | 2026-11-07 |  |

## `.claude/baselines/outdated/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `audit_2026-05-03_known_failures.txt` | HISTORY |  | Known Failures — Audit Remediation Baseline (2026-05-03) |
| `audit_2026-05-03_pre.txt` | HISTORY |  |  |
| `phase24_pre.txt` | HISTORY |  |  |
| `phase25_pre.txt` | HISTORY |  |  |

## `.claude/conversations/archive/`

HISTORY: 7 files kept for the record (`.claude/conversations/archive/`). Task archives are listed at the bottom of `tasks.md`.


## `.claude/design/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `adr076_mvp.md` | AS BUILT / reference | 2026-11-07 | ADR-076 MVP-1 Scope — BLUEPRINT AI Agent Helper |
| `adr076_mvp2_backend_options.md` | AS BUILT / reference | 2026-11-09 | ADR-076 MVP-2 Options — API Backend, Sandboxing, and Instructions Content |
| `app_features_capability_matrix.md` | AS BUILT / reference | 2026-11-07 | Deployment Configuration Matrix |
| `app_features_scoping_guide.md` | AS BUILT / reference | 2026-11-07 | Deployment Configuration Guide |
| `design_t3_export_threading.md` | AS BUILT, partly superseded by the audit redesign (ADR-099); not moved because CLAUDE.md lists it | 2026-11-07 | Design: T3 Export Threading + Lineage Audit trail |
| `developer_workflow.md` | AS BUILT / reference | 2026-11-08 | Developer Workflow — End-to-End Producer Journey |
| `export_specification.md` | AS BUILT, the export contents are extended by ADR-099 and the audit design; not moved because CLAUDE.md lists it | 2026-11-07 | Export Specification |
| `functionality_dependency_map.md` | AS BUILT / reference | 2026-11-07 | Functionality Dependency Map |
| `home_audit_reading_guide.md` | RECENT (redesign) | 2026-11-13 | HOME filters and audit: reading guide (start here) |
| `home_audit_steps.md` | RECENT (redesign) | 2026-11-13 | HOME: audit steps and audit mode |
| `home_observations_and_future.md` | RECENT (redesign) | 2026-11-12 | HOME redesign: am I blocked? Observations on the model, and the future (2026-11-12) |
| `home_preview_filters.md` | RECENT (redesign) | 2026-11-13 | HOME: Exploration (preview filters and column choices) |
| `home_stage2_mechanism_spec.md` | RECENT (redesign) | 2026-11-13 | HOME audit: the mechanism and the build plan (stage 2, draft v0.1, 2026-11-13) |
| `maps_advanced_geo.md` | AS BUILT / reference | 2026-05-22 | Advanced Geospatial Visualization — Solution B (Real Geo) |
| `plot_authoring_model.md` | AS BUILT / reference | 2026-11-07 | Design: Canonical Plot Model & BLUEPRINT Authoring Seam |
| `plot_config_cascade.md` | AS BUILT / reference | 2026-11-07 | Design: Plot Configuration Priority Cascade |
| `recipe_format_gallery_options_2026-11-13.md` | RECENT (redesign) | 2026-11-13 | Gallery examples as standard recipes: what must change, options, plan (2026-11-13, version |
| `recipe_format_review_2026-11-13.md` | RECENT (redesign) | 2026-11-13 | Recipe format: the decisions, the current state, the plan and the questions (2026-11-13) |
| `recipe_format_spec.md` | RECENT (redesign) | 2026-11-13 | Recipe format specification (draft v0.8, 2026-11-13) |
| `recipe_format_st22_draft.yaml` | RECENT (redesign) | 2026-11-13 | DRAFT, not loadable: the main file of 1_test_data_ST22_dummy written in the format of reci |
| `recipe_review_st22_2026-11-11.md` | RECENT (redesign): the test recipe review, with the AMR proposals R1-R4 | 2026-11-12 | Recipe review (data scientist): 1_test_data_ST22_dummy |
| `reproducible_export_design.md` | AS BUILT / reference | 2026-11-09 | Reproducible export & import — design discussion (2026-11-09) |
| `ui_panel_map_current.md` | AS BUILT / reference | 2026-11-09 | SPARMVET_VIZ — UI Panel Map & CSS Selector Reference (CURRENT STATE) |
| `ui_reachability_map.md` | AS BUILT / reference | 2026-11-08 | UI reachability map: where is a cross-cutting surface guaranteed to exist? |
| `uml_model_plan.md` | AS BUILT / reference | 2026-11-12 | UML model of SPARMVET_VIZ: plan (TOOLS-UML-3) |

## `.claude/design/feature_extension/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `bioinformatics_viz.md` | AS BUILT / reference | 2026-11-07 | Bioinformatics Visualization via R (ggtree & friends) — Possibilities |
| `composite_dashboard_home2.md` | AS BUILT / reference | 2026-11-07 | Composite Dashboard ("HOME2") — Mixed-Data Bioinformatics Views |
| `dashboard_frontend_topology.md` | AS BUILT / reference | 2026-11-07 | Second Frontend ("app2") vs. New Space ("HOME2") — Application Topology |
| `r_backend.md` | AS BUILT / reference | 2026-11-07 | R / ggplot2 Rendering Backend — Possibilities |
| `sankey_flow_geoms.md` | AS BUILT / reference | 2026-05-22 | Custom Flow & Network Geoms — plotnine Extension (GALLERY-FLOW) |

## `.claude/design/home_evidence/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `home_attrition_report_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | Attrition per step and the figure caption (proposal, 2026-11-12) |
| `home_audit_architect_review_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | The app and the audit plan seen by a software architect |
| `home_audit_forensics_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | HOME audit: forensics of the current design, and options for what is still undecided |
| `home_audit_view_from_copy_2026-11-13.md` | RECENT (redesign) | 2026-11-13 | How audit mode shows data and plots from a copy of the recipe (investigation, 2026-11-13) |
| `home_design_review_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | Independent review of the decided HOME design (one pass before Eve reviews it) |
| `home_gating_and_test_configs_2026-11-12.md` | PAUSED (input of the configuration stage) | 2026-11-12 | HOME: gating of filters by configuration, and configurations for automatic tests (decision |
| `home_hash_model_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | The hash model: what exists, what each hash answers, what the redesign needs (2026-11-12) |
| `home_uml_review_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | Review of the HOME UML diagrams against the latest decisions (2026-11-12) |
| `home_where_to_remove_data_science_2026-11-12.md` | RECENT (redesign) | 2026-11-12 | Where in the data processing must a removal happen? How a data scientist answers (P5 inves |

## `.claude/design/outdated/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `blueprint_full_feature_set_research.md` | HISTORY |  | BLUEPRINT Architect — Full Feature Set ADR Research & Discussion Prep |
| `home_audit_first_cut.md` | HISTORY |  | A smaller first audit version (PROPOSAL, not decided) |
| `home_audit_review_agenda_2026-11-12.md` | HISTORY |  | Audit planning review: agenda for 2026-11-12 |
| `home_design_first_roadmap_2026-11-12.md` | HISTORY |  | HOME: design first, then mechanism, then code (roadmap and the design to agree) |
| `home_filter_scoping_concept.md` | HISTORY |  | HOME filter scoping: concept, diagrams and test plan (DRAFT, thinking stage) |
| `id_reconciliation_module_sketch.md` | HISTORY |  | ID Reconciliation Library — Module Structure Sketch |

## `.claude/design/spaces/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `BLUEPRINT.md` | AS BUILT / reference | 2026-11-07 | BLUEPRINT — Visual Data Analysis Recipe IDE |
| `FUTURE_SPACES.md` | AS BUILT / reference | 2026-11-07 | Future User Spaces — Forward Notes |
| `GALLERY.md` | AS BUILT / reference | 2026-11-08 | GALLERY — Example Inspiration & Community Browser |
| `HOME.md` | RECENT (redesign) | 2026-11-13 | HOME — Main Analysis Space |
| `TEST_LAB.md` | AS BUILT / reference | 2026-11-08 | TEST_LAB — Data Utility & Testing Suite |

## `.claude/knowledge/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `app_features_traceability_matrix.md` | IN FORCE | 2026-11-07 | App features Traceability Matrix (Component Masking) |
| `architecture_decisions.md` | IN FORCE | 2026-11-12 | Architecture Decisions (SPARMVET_VIZ) |
| `blueprint_architect_ux_spec.md` | IN FORCE | 2026-11-07 | Blueprint Architect — UX & Visual Specification |
| `changelog.md` | IN FORCE | 2026-11-07 | SPARMVET-VIZ Changelog |
| `data_analysis_recipe_data_contract_rules.md` | IN FORCE | 2026-11-07 | Data analysis recipe Data Contract — Structure, Inheritance & Resolution Rules |
| `dependency_index.md` | IN FORCE | 2026-11-09 | Dependency Index (AUTO-GENERATED — do not edit by hand) |
| `project_conventions.md` | IN FORCE | 2026-11-08 | Project Conventions & Quick Reference (Combat Log) |
| `protocol_tiered_data.md` | IN FORCE | 2026-05-05 | Architecture Decision Record: Tiered Data Lifecycle (ADR-024) |

## `.claude/knowledge/archive/`

HISTORY: 6 files kept for the record (`.claude/knowledge/archive/`). Task archives are listed at the bottom of `tasks.md`.


## `.claude/logs/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `audit_2026-05-09.md` | LOG (append-only) | 2026-05-09 | Session Log — 2026-05-09 |
| `audit_2026-05-11.md` | LOG (append-only) | 2026-05-12 | Audit Log — 2026-05-11 |
| `audit_2026-05-20.md` | LOG (append-only) | 2026-05-20 | Audit Log — 2026-05-20 |
| `audit_2026-05-21.md` | LOG (append-only) | 2026-05-21 | Session — BP-JOINT-1 follow-up + YAML Boolean Trap prevention |
| `audit_2026-05-22.md` | LOG (append-only) | 2026-05-22 | Session audit — 2026-05-22 |
| `audit_2026-11-05.md` | LOG (append-only) | 2026-11-05 |  |
| `audit_2026-11-11.md` | LOG (append-only) | 2026-11-11 | Session log 2026-11-11 (recipe review, canaries, preparation for the builders) |
| `audit_2026-11-12.md` | LOG (append-only) | 2026-11-12 | Session log 2026-11-12 (the cheaper engine, one more canary, architect review) |

## `.claude/logs/handoffs/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `handoff_active.md` | LOG (append-only) | 2026-11-13 | Handoff — Active State (2026-05-10 continued session) |

## `.claude/plans/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `implementation_plan_master.md` | ROADMAP before the redesign (the HOME plan is in the stage-2 spec) | 2026-11-08 | Implementation Plan Master: Dashboard Core & Plugin Validation |

## `.claude/prompts/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `prompt_templates.md` | IN FORCE | 2026-11-07 | To give to gemini |

## `.claude/rules/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `dasharch.md` | IN FORCE | 2026-11-07 | Dashboard Architect (ASA-Bio) Protocol |
| `rules_agent_role_bioscientist.md` | IN FORCE | 2026-11-09 | Bio-Scientist Agent Role: Data Analysis Recipe Design Authority |
| `rules_app_features_flags.md` | IN FORCE | 2026-11-07 | App features Feature Flags — Authoritative Reference |
| `rules_app_structure.md` | IN FORCE | 2026-11-09 | App Structure Rules (ADR-045) |
| `rules_asset_scripts.md` | IN FORCE | 2026-11-07 | Asset Scripts & Execution Governance (rules_asset_scripts.md) |
| `rules_code_quality.md` | IN FORCE | 2026-11-07 | Code Quality Standards (rules_code_quality.md) |
| `rules_css_style_spec.md` | IN FORCE | 2026-11-07 | SPARMVET CSS Style Specification (rules_css_style_spec.md) |
| `rules_data_analysis_recipe_structure.md` | IN FORCE | 2026-11-09 | Data analysis recipe Structural Standard (rules_data_analysis_recipe_structure.md) |
| `rules_data_engine.md` | IN FORCE | 2026-11-07 | Data Engine & Transformation Protocols (rules_data_engine.md) |
| `rules_documentation_aesthetics.md` | IN FORCE | 2026-11-07 | Documentation & Aesthetics Standards (rules_documentation_aesthetics.md) |
| `rules_gallery_standards.md` | IN FORCE | 2026-11-07 | Gallery Asset Standards (rules_gallery_standards.md) |
| `rules_legacy_management.md` | IN FORCE | 2026-05-20 | Legacy & Deprecation Management (rules_legacy_management.md) |
| `rules_runtime_environment.md` | IN FORCE | 2026-11-12 | Runtime & Environment Authority (rules_runtime_environment.md) |
| `rules_test_lab.md` | IN FORCE | 2026-11-07 | TEST_LAB Rules (rules_test_lab.md) |
| `rules_toolchain.md` | IN FORCE | 2026-11-07 | Toolchain (rules_toolchain.md) |
| `rules_ui_dashboard.md` | IN FORCE | 2026-11-08 |  |
| `rules_verification_testing.md` | IN FORCE | 2026-11-07 | Verification & Testing Protocols (rules_verification_testing.md) |
| `rules_viz_factory.md` | IN FORCE | 2026-11-07 | Viz Factory & Artist Pillar Protocols (rules_viz_factory.md) |
| `ui_implementation_contract.md` | IN FORCE | 2026-11-12 | UI Implementation contract |
| `workspace_standard.md` | IN FORCE | 2026-11-08 | Antigravity Workspace Standard (v1.20.0) |

## `.claude/tasks/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `home_exploration_build_brief.md` | ON HOLD (detail input; the plan is the stage-2 spec) | 2026-11-12 | Build brief: HOME Exploration and engine fixes (start here in a new session) |
| `retest_procedure_2026-11-06.md` | HISTORY-like: one-off retest of 2026-11-06; kept in place because a test and a script use it | 2026-11-07 | Retest procedure, 2026-11-06 |
| `tasks.md` | RECENT (redesign) | 2026-11-13 | Tasks (SOLE SOURCE OF TRUTH) |
| `test_plan_2026-06.md` | AS BUILT: the live manual test plan for Blueprint, Gallery and Test Lab; its HOME part is superseded by test_plan_home_2026-11.md | 2026-11-09 | SPARMVET_VIZ — Live App Test Plan |
| `test_plan_home_2026-11.md` | AS BUILT: valid for HOME as built today; rewritten after the redesign (TEST-ADAPT-1) | 2026-11-12 | SPARMVET_VIZ — HOME Test Plan (Phase 1 of the split) |
| `uml_findings.md` | AS BUILT / reference: differences found between the UML model and the repository | 2026-11-08 | UML model: findings register |

## `.claude/tasks/archives/`

HISTORY: 19 files kept for the record (`.claude/tasks/archives/`). Task archives are listed at the bottom of `tasks.md`.


## `.claude/tasks/outdated/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `20260810_testing_part1.md` | HISTORY |  | Testing notes — 2026-08-10 (part 1) |
| `audit_findings_2026-11-07.md` | HISTORY |  | Audit findings of 2026-11-07 that the rename did not cause (CONFIG-AUDIT-FIXES-1) |
| `config_rename_inventory.md` | HISTORY |  | Configuration key inventory |
| `config_rename_mapping.md` | HISTORY |  | Rename mapping table (generated) |
| `config_rename_review.md` | HISTORY |  | Review gate for the configuration rename (phase 1, task CONFIG-VOCAB-REVIEW-1 and CONFIG-M |
| `config_rename_strategy.md` | HISTORY |  | Strategy: the configuration rename (ADR-091, issue evezeyl/SPARMVET_VIZ#27) |
| `next_session_start.md` | HISTORY |  | Start here (2026-11-12): builders and the design review side by side |
| `project_word_mapping.md` | HISTORY |  | Mapping: the word "project" (CONFIG-PROJECT-WORD-1) |
| `tasks_test_ui_current.md` | HISTORY |  | Live-UI Test Checklist — Current Dashboard |

## `.claude/workflows/`

| File | Status | Last change | What it is |
|---|---|---|---|
| `audit_exclusions.yaml` | IN FORCE | 2026-11-07 | Audit Known Exclusions |
| `audit_routine_registry.md` | IN FORCE | 2026-11-08 | Audit Routine Registry |
| `audit_triage_protocol.md` | IN FORCE | 2026-11-08 | Audit Triage Protocol |
| `design_review_personas.md` | IN FORCE | 2026-11-11 | Design review by personas (reusable method) |
| `implementation_workflow_transformer.md` | IN FORCE | 2026-11-07 | ⚙️ Transformer Implementation Workflow |
| `ingestion_testing.md` | IN FORCE | 2026-11-07 | 📥 Ingestion Testing Workflow |
| `schedule_commands.md` | IN FORCE | 2026-11-08 | Audit Routine Execution Guide |
| `transformer_testing.md` | IN FORCE | 2026-11-07 | ⚙️ Transformer Testing Workflow |
| `ui_data_analysis_recipe_integration_testing.md` | IN FORCE | 2026-11-07 | 🖥️ UI Data Analysis Recipe Integration Testing (The Master Gate) |
| `verification_protocol.md` | IN FORCE | 2026-11-07 | Workflow: Manual Data Verification (@verify) |
| `viz_factory_implementation.md` | IN FORCE | 2026-11-07 | 🎨 Viz Factory Implementation Workflow |
| `viz_factory_testing.md` | IN FORCE | 2026-11-07 | 🎨 Viz Factory Testing Workflow |

## `.claude/logs/audits/`

LOG: 395 files, the scheduled audit reports (`audit_triage_protocol.md`); triage the new ones with the command in `CLAUDE.md` 3.1. Dated, append-only; do not move or delete.

