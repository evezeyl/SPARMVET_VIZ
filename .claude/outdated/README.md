# Outdated files (kept for history only)

**Nothing in this folder is a rule, a plan or an instruction.** These files were moved here on 2026-11-12 (Eve: "move all outdated plans, testing and so on to a subdirectory with outdated; we only keep them for history; flag them as outdated"). Each file carries an OUTDATED banner with the reason and what replaced it.
Do not follow, update or build on them. If something in them is still needed, copy the needed part into a live file and say where it came from.

| Now at | Was at | Why outdated | Replaced by |
|---|---|---|---|
| `.claude/outdated/tasks/tasks_test_ui_current.md` | `.claude/tasks/tasks_test_ui_current.md` | superseded on 2026-06-19 by the live test plans; pinned to the Phase 26 baseline | `.claude/tasks/test_plan_2026-06.md` and `.claude/tasks/test_plan_home_2026-11.md` |
| `.claude/outdated/tasks/20260810_testing_part1.md` | `.claude/tasks/20260810_testing_part1.md` | raw evidence and fix log of the 2026-08-10 testing round (console pastes); the fixes are done | nothing; the test plans keep one line per item and link here for the history |
| `.claude/outdated/tasks/config_rename_strategy.md` | `.claude/tasks/config_rename_strategy.md` | plan of the configuration rename, implemented on the branch `rename/config-vocabulary` (merged into `dev`) | ADR-091 and `app/modules/renamed_keys.py` |
| `.claude/outdated/tasks/config_rename_mapping.md` | `.claude/tasks/config_rename_mapping.md` | generated mapping table of the configuration rename, which is done | ADR-091 and `app/modules/renamed_keys.py` |
| `.claude/outdated/tasks/config_rename_review.md` | `.claude/tasks/config_rename_review.md` | review gate of the configuration rename, which is done | ADR-091 |
| `.claude/outdated/tasks/config_rename_inventory.md` | `.claude/tasks/config_rename_inventory.md` | key inventory made for the configuration rename, which is done | ADR-091 |
| `.claude/outdated/tasks/project_word_mapping.md` | `.claude/tasks/project_word_mapping.md` | mapping of the word "project" for the configuration rename, which is done | ADR-091 |
| `.claude/outdated/design/home_filter_scoping_concept.md` | `.claude/design/home_filter_scoping_concept.md` | first concept of HOME filter scoping, already marked HISTORICAL | `.claude/design/home_preview_filters.md`, `.claude/design/home_audit_steps.md` and ADR-099 |
| `.claude/outdated/design/id_reconciliation_module_sketch.md` | `.claude/design/id_reconciliation_module_sketch.md` | sketch of a library that was built on 2026-05-22 (already marked HISTORICAL) | `libs/id_reconciliation/README.md` and `.claude/rules/rules_test_lab.md` |
| `.claude/outdated/design/blueprint_full_feature_set_research.md` | `.claude/design/blueprint_full_feature_set_research.md` | research draft, status RESOLVED on 2026-05-20 | ADR-082 |

**Not moved, although they look old (they are tied to something live):** `.claude/tasks/retest_procedure_2026-11-06.md` (a test and a script use it), `.claude/tasks/test_plan_2026-06.md` and `.claude/tasks/test_plan_home_2026-11.md` (valid for the app as built today; the HOME plan is flagged for rewriting after the redesign), `.claude/design/design_t3_export_threading.md` (listed in CLAUDE.md), `.claude/tasks/home_exploration_build_brief.md` (GitHub issues link to it; flagged ON HOLD).
Older task archives stay where they are, in `.claude/tasks/archives/`.
