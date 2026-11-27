# Implementation Plan Master: the roadmap in one page

**Authority:** @dasharch. **Last cleaned:** 2026-11-13. This file is the short current roadmap. The history of phases 3 to 34 (all complete) is in `outdated/implementation_plan_master_phases_19-34.md`; the live task list is `.claude/tasks/tasks.md`; the decisions are the ADR log (`.claude/knowledge/architecture_decisions.md`).

## 1. Vision
A modular, multi-species dashboard for bacterial genomics: a **recipe** (YAML) defines how data becomes plots; the app lets a scientist explore the result (Exploration) and, when allowed, record audited decisions about the data behind a figure (Audit), with a reproducible export. Guiding principle: smart simplicity (decoupled, metadata-driven, audit-ready).

## 2. Architectural principles (unchanged)
- **Decorator-first:** wrangling actions with `@register_action`, plot components with `@register_plot_component`.
- **YAML data contract:** `input_fields`, tiered `wrangling`, `output_fields` (ADR-013/014/024/041); the recipe format is being specified (`.claude/design/recipe_format_spec.md`).
- **Polars-first:** LazyFrames for the heavy work; materialise at presentation or export. **Plotnine** for plots.
- **Modular libraries:** every `libs/*` package is independent and installed editable; `libs/utils` is the shared base (`rules_runtime_environment.md`); `app/` and `assets/scripts/` orchestrate. One interpreter: `./.venv/bin/python`.
- **CLI-first tests:** scripts take their inputs from `argparse`; no hardcoded paths.
- **Software informs, the user decides; fail instead of warn** for anything declared but not applied (ADR-099).

## 0. State of 2026-11-26 (read this first; the sections 3 and 4 below are History)
HOME, the audit and the lineage: the page to trust is `.claude/design/home_audit_what_is_true_now.md` (the model in six sentences: a step is applied in data at a place, T1, T2 or the Result data (T3) of a plot, chosen in "Path of the data"; never by plot). Built on `dev`: audit steps at any tier, the lineage panel, the audit copy and its tables, the recipe checks for the metadata. Decided, not built: the toggle beside the recipe title, "Show selection", no plot tabs in Audit mode, the step bar as the single entry (D-0652 to D-0657, D-0663). Built since: slices 1, 2, 3a, 3b, the trial (FLOW-1), the marks and "Add to audit pipeline" (FLOW-2), and the removal of the old way (FLOW-3: the pop-up, Send to Audit, the staged cards, the separate Apply, the Plot Style authoring; the stored names renamed once with a new session format number). Next: the step bar (the single entry), the audit log. The demo is about ten days from 2026-11-26 (`tmpAI/status/DEMO_BUILD_PLAN_2026-11-26.md`, not in git). Tasks: `.claude/tasks/tasks.md`; decisions: `.claude/knowledge/decision_ledger.md` (D-0638 to D-0667).

## History (the roadmap as it stood on 2026-11-13; kept, not current)

### 3. Where we were (2026-11-13)
Phases up to 34 are complete: Home theater, tiers and filters, Blueprint IDE and AI agent, Gallery, Test Lab, sidebar slot registry, configuration vocabulary (ADR-091), reproducible export and import (ADR-097), UML model. The headless baseline is 1652 tests.

### 4. The roadmap then (2026-11-13, in this order)
| Stage | What | Where it is written | State |
|---|---|---|---|
| 1 | HOME design: Exploration and Audit modes | `design/spaces/HOME.md`, `design/home_audit_reading_guide.md`, ADR-099 | agreed; Eve reads and confirms |
| 2 | Mechanism and build plan | `design/home_stage2_mechanism_spec.md` section 5 (packages P0-P12; first milestone M1 = P5, the walking skeleton) | drafted; waits for Eve |
| 3 | Recipe format and checker (parallel session, issue #73) | `design/recipe_format_spec.md` | in progress |
| 4 | Build: tests adapted first, then code, one package per commit | `tasks/tasks.md` groups 1 and 2; protocol `tasks/home_exploration_build_brief.md` | after 1-3 |
| 5 | Configuration, gating, gating tests | `tasks/tasks.md` group 3 | last |
| 6 | Pre-deployment: documentation tiers (`rules_code_quality.md`), security review (`SECURITY-DEPLOY-1`), container (`DOCKER-RELEASE-1`), Galaxy and IRIDA (23-C, 23-D, 23-E) | `tasks/tasks.md` group 4 | later |

Order of work (Eve): design first (science and software), review and agree, mechanism and build plan, code with tests adapted first, configuration and gating last; one problem at a time.

## 5. Open tombstones (expire in Phase 36; delete then)
`LEGACY-FLAT-WRANGLING-1` (`docs/appendix/Standards_yaml.qmd`, `rules_data_engine.md` section 3); `LEGACY-AUDIT-FLAG-1` (`ui_implementation_contract.md` sections 7.2 and 12f, `rules_app_features_flags.md` Group A); `LEGACY-TYPE-ALIASES-1` (`rules_data_analysis_recipe_structure.md` section 9).

## 6. Governing authority
- Rules: `.claude/rules/` (master index `workspace_standard.md`; tests `rules_verification_testing.md`; data engine `rules_data_engine.md`; environment `rules_runtime_environment.md`).
- Decisions: `.claude/knowledge/architecture_decisions.md` (an ADR is never violated without a superseding one).
- Tests and verification commands: `rules_verification_testing.md` section 8 (headless baseline and browser gate).
- Map of every file of `.claude`: `.claude/INDEX.md`.
