# Fix report, export-ready (REVIEW fixes A to D)
Commit: 83a0cf4e on task/export-ready (worktree .claude/worktrees/export-ready).
A. export_ready.js: capture-phase `auxclick` guard (same blockIfGrey). Test test_a_middle_click_on_the_grey_button_starts_no_download. Fail-once with the old JS: failed; with the fix: passes.
B. export_ready.js: the MutationObserver compares the panel element with the last one; if different, lastSeen is reset. Test test_the_same_value_set_again_after_a_user_space_switch_greys_the_button_again (label, Blueprint, Home, same label: grey on the input event, ready after the echo). Fail-once with old JS: failed; with the fix: passes.
C. export_handlers.py: plot_warnings wrapped in try/except; the picture is kept, plot id goes to a list; README line and effective_run.yaml key `plot_warnings_unreadable`. Tests (test_export_plot_warnings.py): unreadable case (monkeypatch raise) and the normal case (no line, empty list). Fail-once with the old handler: both failed; fix: pass.
D. ui.py: new function export_ready_script_tags() returns [] when export_enabled is off; app_ui uses it. Tests (new test_export_ready_script_loaded.py): flag on has the tag, off has none. Fail-once (condition forced False): off-test failed; fix: pass.
Counts: test_export_ready_button.py 18 passed (qa, 7 min 25 s); test_export_plot_warnings.py + script_loaded 10 passed; import check OK.
README line (PROVISIONAL): "Plot warnings could not be read for: <plot ids>" (plot ids comma separated, own line before the plot warnings block).
Not checked: pictures with a real failure of plot_warnings (only a monkeypatch); other app features files with export_enabled off in a real browser (headless flag test only); the other browser tests.
Notes: the plot warning exception is not logged anywhere else; the README line and the record are the only trace. The old_code worktree named in progress.md (tmpAI/old_code) was not touched by me. Stray pgrep hits for shiny/pytest belong to other sessions; I left no app running.
git status --short: clean.
