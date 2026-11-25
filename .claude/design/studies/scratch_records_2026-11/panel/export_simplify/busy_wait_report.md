# Busy wait report (export-ready worktree)
See the summary returned to the coordinator; commit: see `git log` of task/export-ready (message "fix(export): the wait for the server's confirmation does not end while the server is still working").
Evidence: shiny-busy covered the server work in the sampled window (no unbusy sample while grey, 0.3 s to 5 s, old code; whole 6.2 s with the fix). Tests: app/tests/test_export_ready_busy_wait.py (2), slow_switch_app.py (test-only app, 7 s switch to 3_test_no_joins).
Runs (qa): race 13 passed; ready_button 18 passed; new test 3x 2 passed (load 3.90, 5.43, 7.28); fields_per_session 3 passed.
Fail-once: counting wall time again -> long-switch test failed (button opened at 5045 ms, notice shown), busy-signal test passed; fix restored.
demo_abromics: scratch runs with warm cache 0.18 to 1.2 s grey; the earlier scratch script (first switch) 5.24 s grey, no fallback possible since busy; notice not checked in that run (the 7 s test covers it).
