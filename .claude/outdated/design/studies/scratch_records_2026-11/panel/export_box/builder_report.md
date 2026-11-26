REPORT export-box (worktree .claude/worktrees/export-box, branch task/export-box, one commit 2e8a033c)

SUMMARY
- TASK 1 is done. The tick box and every other field of the Export panel now survive a plot-tab change, a filter and a late update. I proved this with a browser test and with a revert check.
- The reproducibility box can still silently read as unticked at download. That is a SECOND defect, not the redraw. It is a race: the download request can reach the server before the box tick and the label that the page sent 0.1 to 0.2 s earlier. It still fails the seed test about 30% of the time with my fix in place. I did not hide it and I did not fix it; it needs a decision (see "Open choices").
- Evidence for the second defect is in the section "20-run result" below.

DECISIONS (read first: decision_compliance.md, agent_principles.md, ledger)
| Decision | How the code complies | Where | Test |
|---|---|---|---|
| D-0050 "No silent error that is the rule." | (a) The README of the bundle records the reproducibility choice and the plot format as the server read them. (b) The notification of a reproducibility export now starts with "Reproducibility part: included (the full recipe and the data files)." (c) A failure to refresh the Scope choices is notified, not swallowed. (d) A scope that is no longer offered is reset to Global with a notice. | export_handlers.py:2026-2029, 1445, 751-775 | test_export_inputs_survive_plot_tab.py (last test) |
| D-0228 (functional demo soon) | Smallest change that applies the repository's own pattern; no change to what the export contains. | | |

WHAT WAS SPLIT AND WHY (app/handlers/export_handlers.py)
- Cause: `system_tools_ui` read `active_home_subtab` and `active_cfg()`. A tab change redrew the whole panel, and every field came back with its default.
- I reproduced this on the old code: label, box, report format, plot width and height all reset after a tab change.
- The panel output `system_tools_ui` (line 591) is now a shell. It reads nothing reactive outside `reactive.isolate()`. It mounts every field once: label, scope, box, quality, plot format, report format, size, download.
- The only part that depends on the tab is the list of Scope choices. It is built by a new pure function, `export_scope_choices(groups, active_subtab)` (line 514), and rendered by `_scope_choice_tags` (line 548).
- A new effect, `_sync_export_scope_choices` (line 751), updates the Scope radio in place with `ui.update_radio_buttons`, so no DOM is redrawn.
  - It keeps the user's selection when it is still offered.
  - If it is not offered, it sets Global and says so: "The export scope '<x>' is not available on this plot tab, so the scope was set back to Global."
  - If the choices cannot be computed (the recipe cannot be read), it tells the user and leaves the choices as they were.
- Input ids, the look and the export content are unchanged. The static check (rule R4, ui_implementation_contract.md section 14) passes.

WHAT THE USER NOW SEES AFTER A DOWNLOAD (TASK 2)
- The existing flow has NO confirmation after a plain successful download (box unticked). It only has notices for failures, blocks, a reproducibility export and unwritten parts. I did not invent one.
- With the box ticked, the existing notification now begins: "Reproducibility part: included (the full recipe and the data files). This reproducibility bundle includes your actual raw data files, not just hashes ..."
- README.txt in every bundle now has two lines:
  - "Plot format      : <png|svg|pdf>"
  - "Reproducibility  : included (the box 'Also include a reproducibility/reimport bundle' was ticked)", or "... not included (... was not ticked when Export was pressed)"
- Verification you asked for: effective_run.yaml does NOT record these choices as read. It has only `t3_translation_skipped` ("not attempted ..." when unticked) and the seeds. I did not add fields to it, because ADR-097 says it is written identically with and without the reproducibility part. So the record is in README.txt.

20-RUN RESULT (test_export_download.py::test_the_export_records_the_seed_..., alone, nothing else running)
- Run with my fix in place: 14 PASS, 6 FAIL out of 20. Every failure is a StopIteration at test line 329: no `data_analysis_recipes_reproducibility/` in the zip. (Before the fix: about 3 of 34.)
- I did NOT change that test.
- I captured the failures with a wire log, the downloaded zip, and temporary debug prints in the handler (reverted; `grep DBG` shows 0 hits).

What the evidence shows
- In a failing zip, the folder is named `_user`, not `_autotest`. So the label was read as the default too, not only the box. The README says "not ticked".
- In a failing run, the page sent `export_include_reproducibility: true` and then the label. There was no redraw, no ERROR.txt, and the wire log of a failing run is identical to a passing one.
- The temporary debug effect printed `DBGIN box=True` only AFTER the whole export computation had run. A raw read at the start of the download returned `''` and `False` with no exception.
- So the HTTP download request is processed before the page's earlier WebSocket input messages. This is the "second, unexplained pattern" of the REPORT, now explained.
- With a 2 s pause between the tick and the download click (a throwaway copy of the test, since deleted): 10 of 10 passed. Without the pause, the failure rate is about 30%.
- It is a real race for users: a human who ticks and presses Export in under about a second, or while the server is busy, gets a bundle with no reproducibility part and nothing on screen says so.
- Saved evidence (in tmpAI, git-ignored):
  - tmpAI/runs_first/ (first 20 runs)
  - tmpAI/runs_instr1/, runs_instr2/ (zips and wire logs)
  - tmpAI/runs_instr3/ (the run with the DBGIN prints)
  - tmpAI/plug/savezip2.py (the capture plugin)

TESTS ADDED OR CHANGED
- app/tests/test_export_box_survives_plot_tab.py: the expected-failure mark is removed; it now passes as a normal test.
  - I made the check more exact: it counts a reactive READ (a call: `active_cfg()` or `.get()`), not a comparison `active_home_subtab is not None`.
  - The checker's own test has new cases for this.
- app/tests/test_export_inputs_survive_plot_tab.py (browser, 4 tests):
  - Every field survives a plot-tab change. The Scope label follows the tab and the selection stays.
  - A chosen group scope follows the group of the open tab.
  - The fields survive an exploration filter.
  - Tick, then change the tab, then download. The recipe and data folders are in the zip, README.txt records the choice, and the notification appears.
  - A 4-test run took 86 s and passed. Its waits are tied to the Scope label (the update's completion signal), not a fixed sleep.
- app/tests/test_export_scope_choices.py (headless, 5 tests): no groups, no tab, a tab, a tab in no group, and a name that is not a plot tab.
- Break check: with the old handler restored, the static test fails. The browser test fails with label, box, report format, plot width and height all reset.

RUN RESULTS (worktree PYTHONPATH, one browser file at a time, qa)
- test_export_download.py: 9 passed (this run the seed test passed, which is consistent with the roughly 70% pass rate above)
- test_shiny_smoke.py: 37 passed, 3 skipped
- test_export_*.py:
  - contact 8, errors_visible 16, failed_plot 5, provenance 14, refusal 6, report_links 5, report_texts 114 passed and 4 skipped, view_consistency 15, download_path 5 (all passed)
  - box_survives_plot_tab 3, scope_choices 5, inputs_survive_plot_tab 4 (all passed)
- test_imports_from_checkout.py: 12 passed
- `python -c "from app.src.main import app"`: import OK

OPEN CHOICES (need Eve; not taken)
1. The download-versus-input race (the second defect), with a recommendation, because this is exactly the silent result D-0050 forbids.
   - A. Show, next to the box, what the SERVER holds ("Reproducibility part: will be included"), and let the test wait for that text before downloading.
     - Pro: the user sees the mismatch before pressing Export; the test is deterministic.
     - Con: a new line in the panel.
   - B. Make the download request carry the choices (query string or JS), so it cannot overtake them.
     - Pro: closes the race at the root.
     - Con: the most work.
   - C. Test only: wait about 2 s after the tick.
     - Pro: simplest.
     - Con: it hides a defect a user can meet; I did not do it.
   - My recommendation: A now (it also informs the user), B later if wanted.
2. There is no success confirmation after a plain download. Optional: one line in the notifier after every export, "Export created. Reproducibility part: not included."

NOT CHECKED
- Switching workspace (Home to Gallery and back): whether the left sidebar rebuild keeps the panel's fields. The shell is not redrawn by tab changes, but I did not test a workspace switch.
- The "Active plot" or "Active group" scope while no plot tab is open: `export_handlers.py:~930` silently exports Global. The README records "Export scope: global", but the choice stays selected and dimmed. This is not from my change; I did not touch it.
- Two browser tabs on the same session.
- The PDF/DOCX report formats at download (the test sets them, but only the png/html and svg paths were downloaded).
- The loop leaves processes: none of mine are left running.

Files changed: app/handlers/export_handlers.py; app/tests/test_export_box_survives_plot_tab.py; new app/tests/test_export_inputs_survive_plot_tab.py; new app/tests/test_export_scope_choices.py. Progress note: tmpAI/progress.md. I did not update @deps or the dependency index, because no provides/consumes changed (the new function `export_scope_choices` is internal to the handler).
