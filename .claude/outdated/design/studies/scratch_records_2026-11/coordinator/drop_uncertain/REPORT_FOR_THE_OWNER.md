# HOME, audit column drop where the app cannot follow the column: what the build found (coordinator, 2026-11-21)

Decisions: D-0449 ("Right now od go for B"), D-0450 ("do not get wrong results because we did not select the correct scope"). Branch `task/drop-uncertain-allowed`, commit `a949faed`, NOT merged. Source: the builder's report; a review is running.

## First: two ways a column drop still changes a result with no error
1. **A formula that takes "all columns" or columns by type** (`pl.all()`, `pl.exclude(..)`, `pl.col(pl.Int64)`). After ANY drop upstream it computes on one column less. Test: a total of 111 becomes 101, no error. The app does not read formulas (D-0356), so it cannot see this. It is NOT new: a drop the app can follow does the same today. The new warning names it in a standing sentence. That is a word of caution, not detection.
2. **A join where both tables have a column of the same name.** The join renamed the right one (`lab_right`). Drop `lab` on the left: the right one keeps the name `lab`, and a plot that reads `lab` draws the other table's values, no error. For a drop the app cannot follow, the warning now says so. For a drop the app CAN follow, there is no warning today (not changed).

## What the tests show (24 new tests on the real engine)
| Case | Outcome |
|---|---|
| Drop after an unpivot (the column is not a column there) | plain error: column not found, step named |
| Drop before an unpivot that names the column | allowed with warning; then a plain error at the unpivot |
| Drop before an unpivot that does not name it | the intended table; other columns unchanged |
| Reshape back to wide, drop at the end | the intended table |
| A later formula or select needs the column | plain error, step named |
| A join key hidden behind a step the app cannot read | refused before anything is built, plain sentence |
| The shipped recipes: 8 such join-key places (the review of 2026-11-20 counted 5) | each refused, plain |
| The demo recipe: 15 places uncertain even with the engine's plan | 6 give the intended table, 9 a plain error |
| Formula over "all columns" | DIFFERENT TABLE, NO ERROR (point 1) |
| Same-named column of a join | different table, WITH the warning (point 2) |

Also fixed: the error of a failed audit build carried a raw engine dump; it is now one line that names the step, the table and the column.

On screen today the warning never appears: HOME writes a drop only at the plot's own table. It becomes live when the dialog offers T1 and T2 places.

## The warning, as written (PROVISIONAL, yours to read)
"Warning: the app cannot follow the column 'lab' at T1:A to the end. 'lab': it reaches step 1 of T2:A (polars_unpivot), a step the app cannot read. [what the app can read about it] If you confirm, the step is written and the app does not know what the tables after that step do with the column. If a later step needs it, the build may fail: the error names the step, and removing the audit step gives the recipe back unchanged. A formula is not read: one that takes columns by type or all of them (for example pl.all()) will compute on one column less, with no error. Check the tables after the drop."

## Yours to decide
A. Point 1 (formula over all columns), options:
   - a1: accept the standing sentence in the warning (as built);
   - a2: detect such formulas (the app would read formulas: reconsiders D-0356, information only);
   - a3: keep refusing a drop the app cannot follow (back to before D-0449). Note: a1 to a3 do not cover a drop the app CAN follow, which has the same effect today.
   - a4: show the sentence, or a check of the tables before and after, for EVERY column drop.
B. Point 2: show the same-name warning also for a drop the app can follow? (yes / no)
C. The dialog line of such a column is grey today. Make it selectable with the warning, or keep grey until the dialog is built?
D. A restored session that holds such a drop: a notice at restore, or nothing?
E. Later: let the app try the build before confirming, so that "this drop will fail" is said before, not after.

## Her remarks of 2026-11-21 evening (channel block M501; NOT decisions, the review session asks her again)
Her words: "1..maybe export should export all the tables if there are included in a recipe even if no plot..3. maybe because the scoping of where the removal of the second table has been done ? Of we remove in the origin of the second table it will follow all no.?. O thought a refused line was because could not trace and we do not know the effects where a red warning should be and if where red warning then we cannot thick ... Also if we have no good way to guide the user and are usure of our effects we should consider not allowing those changes or at least Warm in red ...i do not think we get that complicated cases and as we wait our use case is to remove bad samples but from the quality Insurance but who knows..."

Her lean, as the review session reads it (not her words): (1) the export could write ALL the tables of a recipe, also those no plot reads; (2) for the left join the scope explains the effect, and the dialog must say it before she confirms; (3) a line the app cannot trace is a RED warning and CANNOT be ticked; when unsure of the effects, do not allow the change, or at least warn in red. Point (3) CONFLICTS with ledger D-0449 (an uncertain drop is allowed with a warning) and with the branch task/drop-uncertain-allowed built from it: that branch is NOT merged and waits for her answer. Her use case: removing bad samples found by quality control; she does not expect complicated cases.
