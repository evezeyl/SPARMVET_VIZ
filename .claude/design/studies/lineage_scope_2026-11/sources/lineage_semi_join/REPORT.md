# Can the lineage follow a semi join? (study ordered in D-0452; builder, 2026-11-21; filed and shortened by the coordinator)

Nothing in the repository was changed. RUN = run on the real engine (Polars 1.40.1; scripts in `scratch/`). READ = file:line. REASONED = inferred. Frames of 5 rows with a duplicate key on both sides, a key on one side only, a null key on both.

## Summary for the owner
1. YES: a semi join can be followed with the rules the app already has. It needs four small additions (about 10 lines) and its tests. A trial in memory gave the same lines as the equivalent inner join.
2. Why: a semi join keeps the rows of the first table that have a match in the second, and copies no column of the second. A removal on either table can only REMOVE rows. That is an inner join minus the copied columns.
3. Anti, right, full and as-of joins CANNOT be followed with these rules. A removal on one table can ADD rows (anti), EMPTY cells instead of removing the row (right, full), or CHANGE the values of kept rows to those of another row (as-of).
4. A join on conditions is not followed (the app does not read the conditions). A cross join cannot be written at all today.
5. Self-join: the columns are already followed; the line is grey on purpose, because one column exists twice.
6. Today the documentation RECOMMENDS semi and anti joins in 5 places, and BLUEPRINT's join designer offers two join kinds the engine refuses.

## Flag first: what changes a result with no word TODAY
1. **A left join, today.** A removal on the second table of a left join does not remove the row at the join: it empties the copied cells and keeps the row (RUN). The dialog's reach says "tables and plots built from it", never "the row is kept". The planned note for this is not built (`libs/utils/src/utils/lineage_records.py:143-152`).
2. **An anti join written by hand** (a left join, a marker column, a filter on the marker, a drop of the marker) gives the same table as an anti join (RUN). The app follows it as a left join and ticks the second table. If the user unticks the other places, a removal at the second table ADDS rows and nothing says so. With every place ticked it is safe.
3. **Right and full joins:** a step on the first table shows ticked at the join with the note "values may have changed"; the row is NOT removed there (RUN).
4. **As-of:** a removal on the second table makes kept rows take another row's values (RUN). The second table's columns are grey today, so this case is stopped.

## The effect of ONE audit step on ONE input (RUN)
Legend: -n rows removed, +n rows added, ~n rows kept with emptied cells.
| Step on one input | inner | left | semi | anti | right | full |
|---|---|---|---|---|---|---|
| first table: remove row A | -1 | -1 | -1 | 0 | ~1 | ~1 |
| second table: remove row A | -1 | ~1 | -1 | **+1** | -1 | ~1 |
| second table: remove one of two rows B | -2 | -2 | 0 | 0 | -2 | -2 |
| second table: remove key B (both rows) | -4 | -2 and ~2 | -2 | **+2** | -4 | -2 and ~2 |
| removal of key A on BOTH tables | -1 | -1 | -1 | 0 | -1 | -1 |
| first table: drop a column the second also has | the second table's values take the name | same | column lost only | column lost only | as inner | as inner |
| second table: drop a non-key column | column lost | column lost | no effect | no effect | column lost | column lost |
| drop of the key, either table | the join fails with "unable to find column" in all six kinds | | | | | |
A removal on both tables is safe for every kind: this is why "remove from all the data" is correct for all kinds.
Output columns: semi and anti give the first table's columns only; a right join takes the key from the second table; a full join holds the key twice (`k`, `k_right`).

## Verdict per kind
| Kind | Verdict | What is missing |
|---|---|---|
| semi | YES with 4 additions | see below |
| anti | NO | a rule of direction (a removal adds rows) |
| right | NO as the rules are | the rule "which table keeps its rows", which the left join also lacks |
| full | NO | the same rule; the key in two columns |
| as-of | NO | values of kept rows change |
| on conditions | NO for now | the app does not read conditions (D-0356) |
| self-join | columns followed; grey by choice | her decision: which of the two columns a step names |
| cross | cannot be written | nothing |

## The four additions for the semi join
| # | Change | Where |
|---|---|---|
| 1 | add "semi" to the followed kinds | `libs/utils/src/utils/step_effects.py:64` |
| 2 | for a semi join, do not copy the second table's columns | `step_effects.py:200-205` |
| 3 | the second table's non-key columns end at the join as "gone" (a note), not as a grey "cannot follow" | `libs/utils/src/utils/lineage_walk.py:257-279` |
| 4 | the same-name warning only for kinds that copy columns | `lineage_walk.py:683` |
Plus texts (`step_effects.py:29-30`, `lineage_walk.py:35, 40`) and two tests that list semi as not read (`libs/utils/tests/test_step_effects.py:30-31`). Side effect (REASONED): for a semi join the join table leaves the "may stay" list of "remove from all the data".
Proposed tests: the columns are the first table's; the second table's columns are "gone", not grey; the key is linked both ways; no same-name warning; on the real engine no step adds a row or changes a value; the equivalent inner form gives the same table; every shipped recipe uses only followed join kinds.

## Shipped recipes (RUN, grep)
`how:` is `left` in 201 steps and `inner` in 92. No semi, anti, right, full or cross anywhere; no self-join. As-of and the join on conditions occur only in two test recipes of the transformer. So a red warning, or following the semi join, changes no shipped recipe.

## Records that say the opposite of D-0452 (READ)
They recommend semi or anti joins: `docs/workflows/wrangling.qmd:92, 261`; `docs/reference/development_rules.qmd:140`; `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:230-231`; `docs/appendix/Standards_yaml.qmd:208`; `.claude/design/recipe_format_spec.md:773`.
Also: `libs/blueprint_arch/src/blueprint_arch/join_designer.py:27` and `docs/workflows/blueprint_architect.qmd:309` offer inner, left, outer, semi, anti, cross. RUN: `outer` is refused by the engine, `cross` cannot be written, `right` and `full` are not offered.

## Proposed warning sentences per kind (PROPOSALS; each true by a run; YET in capitals per D-0454)
- anti: "This table keeps the rows of the first table whose key is NOT in the second table. A step on the second table can ADD rows here. The app cannot YET follow this. Check the rows before you confirm."
- right: "This table keeps every row of the second table. A step on the first table empties the first table's columns here and does not remove the row. The app cannot YET follow this."
- full: "This table keeps the rows of both tables and holds the key twice. A step on one table empties the other table's columns and does not remove the row. The app cannot YET follow this."
- as-of: "Each row of the first table takes the nearest row of the second table. A step on the second table can CHANGE values of rows here. The app cannot YET follow this."
- on conditions: "This table holds every pair of rows that meet your conditions. The app does not read conditions and cannot YET follow this."

## For recipe authors: what to write instead (PROPOSALS)
| Kind | Instead | Run? |
|---|---|---|
| semi (until followed) | an inner join with a table that holds only the distinct keys of the second table | RUN: same table, followed |
| right | a left join with the two tables swapped | RUN: same rows, other column order |
| full | a left join of the table whose rows must be kept; two tables and two plots if both are needed | RUN: no action appends rows |
| anti | none that the audit can follow; prefer a prepared column "has no X" in one table | RUN (the hand-made form, see flag 2) |
| as-of, on conditions | prepare the table outside the app | not run |
| self-join | give the second copy its own table with renamed columns | not run |

## For the owner to decide
1. Build the semi join now? (A) yes, the four additions and the tests; (B) no, keep it red and tell authors the inner form; (C) A, plus the note for the left join (flag 1).
2. Which kinds are red: anti, right, full, as-of, on conditions (and semi until built). Self-join: grey as today, or red?
3. The hand-made anti join (flag 2): not mentioned in the docs; mentioned with its warning; or followed by a new rule (not studied).
4. The five documentation places and BLUEPRINT's join designer: changed in the same step as the red warning?
5. The left join (flag 1): a note "the row is kept, its cells are emptied", or leave it to the count of rows shown per line?
6. Self-join: stays grey, or a step at the join names one of the two columns.

## Not verified
As-of and the join on conditions in the walk with the engine's plan (read, not run). The `coalesce` parameter. The semi trial ran only on small recipes; the full test suite was not run with the additions. Polars 1.40.1 only. The alternatives for self-join, as-of and on conditions. The dialog is not built: "what the user sees" is the walk's output, not a screen.

## Her remarks of 2026-11-21 evening (channel block M501; NOT decisions, the review session asks her again)
Her words: "1..maybe export should export all the tables if there are included in a recipe even if no plot..3. maybe because the scoping of where the removal of the second table has been done ? Of we remove in the origin of the second table it will follow all no.?. O thought a refused line was because could not trace and we do not know the effects where a red warning should be and if where red warning then we cannot thick ... Also if we have no good way to guide the user and are usure of our effects we should consider not allowing those changes or at least Warm in red ...i do not think we get that complicated cases and as we wait our use case is to remove bad samples but from the quality Insurance but who knows..."

Her lean, as the review session reads it (not her words): (1) the export could write ALL the tables of a recipe, also those no plot reads; (2) for the left join the scope explains the effect, and the dialog must say it before she confirms; (3) a line the app cannot trace is a RED warning and CANNOT be ticked; when unsure of the effects, do not allow the change, or at least warn in red. Point (3) CONFLICTS with ledger D-0449 (an uncertain drop is allowed with a warning) and with the branch task/drop-uncertain-allowed built from it: that branch is NOT merged and waits for her answer. Her use case: removing bad samples found by quality control; she does not expect complicated cases.
