# Review of task/filter-column-reset (082b0869, 593aac0d, 55bcc486 on dev c21fbdc3), 2026-11-19

Digest by the coordinator of the reviewer's hand-back. Labels of the reviewer: READ, RAN, REASONED.

## Verdict: MERGE AFTER A NAMED FIX

1. HIGH. `dialog_rows_signature` (`app/modules/t3_audit_engine.py:720-733`) = `(lf.explain(optimized=False), table_key)` with `table_key` = tier1_key (`home_theater.py:2273`). Two different tables can give the same signature, so the value list of the form can stay old (RAN, scratch `tmpAI/coordinator/filter_reset_check/`):
   - (a) Polars prints a long list literal truncated: `is_in(["s0", "s1", … "s99"])`, no count. Two audit steps that differ only in a middle value or in length give equal signatures (from 4 values up). Real tables then held 8 and 5 rows.
   - (b) A stored table rewritten at the same path with the same row count (tier-2 edit): same plan; tier1_key excludes tier-2 steps.
   - (c) In-memory frames: plan `DF ["x"]` is the same for other rows.
   - Mitigation that exists: at Add, `dialog_value` reads the fresh table and refuses a value that is gone, with a plain error. A value missing from the list gives no message.
   - Tests miss: truncated list, same-path rewrite, in-memory; no browser test changes the rows with the same columns.
   - Options named: build the signature from the inputs (canonical JSON of the audit nodes, the tier, the tier-2 key or a row count), or hash what the widget would show.
2. MEDIUM. The Effect `_signal_dialog_table` (`filter_and_audit_handlers.py:302`) runs always: no gate on `interactivity_enabled`, runs with the panel closed. Exceptions are caught, logged, turned into an "error" signature. No loop (guards, isolate).
3. LOW. `git diff --check`: trailing whitespace at `app/tests/test_shiny_apply_blocked.py:34`.
4. Reactive discipline R1, R3, R4 and tier isolation: complied (READ). `_filter_add_row` still reads the table fresh.
5. Tests can fail (identity of the select element, render counters, kept values). Reviewer ran the new file: 20 passed; headless filter files: 350 passed; import OK.
6. Dependency index commit `55bcc486`: generated content only; the ONE conflict with `task/engine-keys` (merge-tree). Advice: drop it, regenerate after both merges. The three code files merge cleanly with `task/engine-keys`.
7. The remaining race (a pick lost after a REAL change of columns while the server draws the plots): the builder's explanation holds. Shiny handles one message at a time and sends all outputs of a flush in ONE message; the plot renders are synchronous (`home_theater.py:419`, `:546`). No server-side fix without a design choice. Options: A accept and document; B shorten the busy time (plots off the event loop, or the form sent first): performance task, narrows only; C a notice (a guess); D a small client-side hold of the choice (excluded by the present rule).

## For the owner
Repaired: a change of "Data to show" between views with the same columns no longer rebuilds the form; column, operator and value stay.
Still possible: (1) the pick lost right after a change of plot tab or a real change of columns (15 of 15 in the builder's probe); (2) until the named fix: a value list that stays old in a rare case.
Nothing in the filters applied to plots, tables or export was changed.
