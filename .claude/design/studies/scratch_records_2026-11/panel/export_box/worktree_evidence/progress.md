# progress export-box
started; reading code
- code split done in export_handlers (export_scope_choices, effect _sync_export_scope_choices); next: task2 README/notification, tests
- tests written: test_export_inputs_survive_plot_tab.py (browser), test_export_scope_choices.py, AST test unxfailed; README line + notification done; next: run tests
- 20-run loop running (tmpAI/run20.sh, out tmpAI/run20.out); no other browser test meanwhile. Break check done (old code fails box test). Remaining: run the 4 required suites after loop, commit
- FIRST 20-run (fix in place): PASS=14 FAIL=6, all failures StopIteration at test line 329 (no reproducibility recipe in zip). Not fixed by the redraw fix: second cause. Diagnosing with wire log (tmpAI/plug/savezip2.py)
- instrumented loop (is_checked before click): 12/12 pass; suspect race tick-WS vs download-GET; running 16 with no extra roundtrip
- TEMP debug print DBGREAD in export_handlers (backup scratchpad/export_handlers.fixed2.py) MUST BE REVERTED
- debug prints REVERTED. FINDING: in failing runs the server's stdout shows the whole export run BEFORE DBGIN box=True: the download GET is processed before the WS tick/label messages (sent 0.1-0.2 s earlier). Race page-WS vs download-HTTP. Not the redraw. Next: experiment with wait after tick (test copy tmpAI)
- wait-2s experiment: 10/10 pass vs ~35% fail without => race page-input vs immediate download click (separate from redraw). test_export_download.py NOT changed. Next: run suites one by one, commit
- DONE: committed 2e8a033c; suites passed; report next

## Review
- started: read report and diff; running headless baseline next
- review: Part 1 read done (static check slips, scratch break of static test confirmed fail); headless suite running (log tmpAI/review_export_box/headless.log); next: browser suites one at a time, window test (tmpAI/review_export_box/test_window.py), dev vs branch seed-test rates.
- review: headless 10464/5/32xf done; browser qa started
- review: browser qa 140 passed/3 skipped/1 xfailed; every_app_features started
- review: every_app_features 9 passed; golden identical; alternating dev/branch seed test dev 2/12 fail, branch 3/12 fail; window (warm session) 1 lost in 24 at pause 0; scratch option E (download waits for reactive lock) still lost 2/12; fresh-app pause runs in progress (seq3)
- review: REPORT.md written (both locations); done
- fixes 1-3 done + tests (test_export_readme_reproducibility, test_export_scope_notices); headless OK; browser tests running (tmpAI/br1.log br2.log); next: commit, report
