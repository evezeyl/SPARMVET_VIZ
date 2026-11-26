# Review of the branch task/drop-uncertain-allowed (commit a949faed), 2026-11-21 (reviewer; filed by the coordinator)

VERDICT: FIX FIRST. Not merged. It also waits for the owner's answer: allowed with a warning (D-0449) or red and not tickable (her remark of the evening, not a decision).

Tests: the full headless suite passes on the branch (13966 passed, 0 failed; no browser suite). The new tests can fail (five mutations tried; each fails at least one test).

## Must fix
1. A FALSE sentence in the warning for a same-named column of a join: it says "the plot 'P' draws 'lab': it cannot be drawn" beside "reads the column of B, with no error". In fact the plot IS drawn, with the other table's values. Fix: do not write "cannot be drawn" for such a column; a test asserts it.
## Should fix
2. Stale texts: the test name `..._is_not_refused_PROVISIONAL` (`libs/utils/tests/test_lineage_drop.py:193`; decided by D-0448); `app/modules/plan_composer.py:71`; the generated dependency index.
## Optional
3. A direct test of the one-line error of a failed audit build. 4. The standing sentence should say that ROWS can change too, not only "one column less".

## For the owner: results that change with no error (most serious first)
1. **A same-named column of a join.** The left column is dropped; the plot keeps drawing that name, now with the OTHER table's values. No error. Verified for left, inner, full and right joins. For a drop the app CAN follow there is NO warning at all today. This is not new with D-0449; it exists on dev.
2. **A formula over all columns** (by "all", by type, by position, or a hash of all columns) changes values; a row filter over all columns changes which ROWS survive (3 became 4 in the run). No error. Also on dev today, for any column drop. The app does not read formulas (D-0356).
3. A restored session that holds such a drop restores it with no notice.
4. The dialog line of such a column is grey while the rule would now write the drop.
5. Only the column drop gets a warning. A filter placed after a recode of the value has none ("every audit step" in D-0450 is the review session's reading, not decided).

## What else the branch changes
- Every path that shares the rule now allows a drop the app cannot follow: the audit copy, the recipe check AU04 without a plan, the session restore, HOME's column drop. A join key hidden behind a step the app cannot read is still refused before anything is built, when the audit is run (verified).
- The error of EVERY failed audit step is now one line without the engine's dump (`app/modules/audit_run.py:201`): wider than drops, useful whatever she decides.
- On screen today the warning never appears: 184 columns of the plots of the 5 shipped recipes, 0 warnings, 0 refusals (run).

## Plain-ness of the warning (PROVISIONAL text)
Six sentences; internal words (`T1:T`, `polars_unpivot`, "the build", `pl.all()`); it says where the app lost the column but not what it could follow.
