# Leak fix and dev merge (worktree engine-keys, branch task/engine-keys)
Commits: 4bde95ab (test fix), 3dc0cd2e (merge dev, no conflict).
Reproduce: registration file then app/tests/test_engine_registry.py in one process: 1 failed (before fix). After fix: 56 passed. Break-once (fixture no longer restores): 16 failed; restored.
Change: libs/viz_factory/tests/test_registration_errors.py: fixture registries_untouched watches and restores PLOT_COMPONENTS, COMPONENT_SCHEMAS, COMPONENT_ENGINES; the two probe-popping finally blocks also pop COMPONENT_ENGINES. No product code touched.
Other tests with the same gap: none (test_component_engine_field and test_action_engine_field already snapshot-restore all registries; other grep hits are docstrings or scans).
Runs: libs/viz_factory/tests 2210 passed, 27 xfailed; the four-file single process (registration, engine_registry, plot_callers_are_checked, suggestion_label) 71 passed; app import OK. Both dev test files pass on the branch, no window problem.
git diff --stat 5d9d5404..HEAD: tests (test_plot_callers_are_checked, test_suggestion_label, test_registration_errors) and the two record files (tasks.md, handoff_active.md) only. Worktree clean.
