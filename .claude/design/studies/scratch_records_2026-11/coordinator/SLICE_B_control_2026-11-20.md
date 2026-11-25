# Slice B: the full control of head `56448279` (reviewer RAN; digest by the coordinator, 2026-11-20 10:00 by the clock)

Outputs: `tmpAI/coordinator/slice_b_final/`. Verdict: FIX FIRST (one regression); everything the slice must not change is intact.

| Run | Result |
|---|---|
| qa flags through the Bootloader | audit, comparison, sessions, export, Blueprint and the others on; ghost save OFF |
| App import | OK |
| Headless suite, once, 30 browser files left out | 12532 passed, 13 skipped, 31 xfailed, 0 failed (slice A: 12254) |
| 29 browser files, qa, three at a time | 269 passed, 3 skipped, 1 xfailed, 2 failed |
| The two failures, each alone | the seed-places test PASSED alone (a parallel-only fault); the zero-recipes test FAILED alone (real) |
| All eight setups start | 9 passed |
| Golden baseline | identical |
| Pictures of the shipped recipes | 50 identical, plus the one known row (the empty orphan recipe) |
| Flag files check | 8 files, 0 errors, 0 warnings |
| Small audits | old words as before; document links 13 problems (11 before; two new at `tasks.md:438`, cause not found); UML audit 9 (8 before; one tag points at a function renamed by this piece) |

## The regression (real; passes on dev)
`app/tests/test_empty_data_analysis_recipe_startup.py::test_zero_recipes_renders_empty_state_without_server_error`: with no recipe at all the page works, but the server log holds a Traceback: `_dialog_table_identity` (`home_theater.py:~460`) calls `bootloader.get_default_data_analysis_recipe()` unguarded (ADR-094 point 6 forbids it on the start path). The user sees no crash. Sent to the builder with the review's fixes.

## The walk on the demo recipe (plot "MLST Bar"), in a browser under qa
- Source offers 'MLST' (10 columns, 42 rows) and 'metadata_schema' (4 columns, 42 rows). T1: 6 columns, 42 rows. T2: 7 columns, 33 rows. T3 in Exploration: the same as T2 (7 columns, 33 rows).
- A filter year > 2023 on T1: the table goes from 42 to 25 rows; the plot picture is the same pixels before and after.
- Changing the view to T2 removes the filter, with the notice.
- Audit mode, one step sent on T3 with a reason and applied: the audited plot differs from the original; T3 (audited) has 25 rows; T1 (42) and T2 (33) unchanged. Compare shows two panes that differ.
- The export with the audit step: the plot's data file has 25 rows; the steps file holds the reason; no filter file. A second export made with an exploration filter that empties the table: the data and all 17 pictures are identical to the first. So an exploration filter is not exported and changes nothing of the export.

## Not covered
Ghost save (off in qa); setups other than qa only started; the Quarto render of the export; two sessions on one audit folder; the picture of Compare's panes pixel by pixel (another test does it and passed).
