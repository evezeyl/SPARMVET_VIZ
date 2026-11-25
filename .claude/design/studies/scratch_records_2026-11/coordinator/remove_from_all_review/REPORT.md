# Review: task/remove-from-all (06dde4c9), AUDIT-REMOVE-FROM-ALL-DATA step 1

Verdict: FIX FIRST (small). The logic is sound and the tests are real. Two points need a change before HOME can use it (F1, F2); the rest is information or needs the owner.

Setup (RUN): `utils` and `app` import from the worktree (`utils/__init__.py` and `app/__init__.py` printed under `.claude/worktrees/remove-from-all`). PYTHONPATH = worktree root + each `libs/*/src`. Load stayed under 7 for all runs. The other reviewer's full run (pid 1728410) was going the whole time, so I did NOT run the full headless baseline.

## 1. Diff (RUN `git diff --name-status 71ab966b...HEAD`)
Only: A app/tests/test_remove_from_all_demo.py, M libs/utils/README.md (1 line), A libs/utils/src/utils/remove_from_all.py, A libs/utils/tests/test_remove_from_all.py. Nothing in app production code, no change to lineage_walk/audit_copy, recipes, spec or pyproject. grep (RUN): the module is referenced only by its tests and the README. Imports of the module (READ lines 54-64): only `utils.*`, dataclasses, typing. No other lib, no Shiny. Complies with rules_runtime_environment.md section 4.
Subclass (READ remove_from_all.py:166-186): `_Index(LineageIndex)` calls `self._costs(...)`, `self._path(...)` and reads `self._dead`. All three are underscore members of lineage_walk.py (`_dead` at :155, `_costs` :393, `_path` :556, a staticmethod).
Finding F3 (medium, not blocking): this is a fragile coupling. A rename or a change of the tuple shape `(cost, link, before)` in the walk breaks this module with no test of the walk noticing, only a test of this module. A small public accessor on `LineageIndex` (the cost-0 certainty of a column and the uncertain ends) would be the sound form. Not decided here; the walk file is outside this task's scope, so it is a follow-up for the owner of the walk.

## 2. Against the decisions
| Point | Result | Evidence |
|---|---|---|
| Only for the entity key, never another column (D-0313, D-0415, D-0416) | COMPLIED, with a width to decide (P2 below) | READ remove_from_all.py:209-231; test `test_not_offered_for_a_column_that_is_not_the_entity_key`; RUN on the demo: `Gene_name`, `VF_gene` (join columns) and a missing column are not offered |
| Reaches every table that holds the key, also one no plot reads (D-0416 1) | COMPLIED for tables that declare the key or are linked to it (P7 below for the rest) | RUN: demo, 27 places of 28 tables; 6 of them have no plot (`Quality_metrics`, `Detailed_summary` ...) |
| Written at tier 1 of each (D-0415) | COMPLIED | RUN: every step has `place` `T1:<table>`, in `audit_steps` (demo test and my script) |
| Off by default (D-0416 2) | COMPLIED, thin | `default_on` is a constant False (:275); `describe` writes nothing (demo test builds nothing). The "off" lives in the future screen; here it means only "nothing happens until `apply` is called" |
| List before anything is applied (D-0416 3) | COMPLIED | `option.places` and `not_reached` come from `describe` alone |
| Warning in one place, data agnostic (D-0416 4) | COMPLIED | `WARNING` (:67) = "This removes your selection from any data that holds it." No word "sample". PROVISIONAL wording (said so) |

P2 (family wider than a strict reading). The module offers a column when it belongs to the "key family": the declared key plus every column a join equates with it. D-0313 says "the entity key (declared in the recipe)" and keeps "columns used to join" as a separate information list. What the family adds:
- (a) a column that is NOT declared but a join equates with the declared key. Example (RUN, `fam_check.py`): A declares `sample_id`; B declares nothing and has `isolate`; a join `left_on sample_id, right_on isolate`. Result: `isolate` is offered too, and B is reached at `T1:B` through `isolate`. A strict reading offers only `sample_id` and reaches A and the join J (B holds no declared key).
- (b) with a place given, a renamed key (`isolate` at `T1:A`, after a rename of `sample_id`) is offered (test `test_the_renamed_name_is_the_key_when_the_user_stands_at_the_place_that_has_it`).
No shipped recipe shows the difference: RUN over the 7 recipes, key families equal the declared keys in all of them (demo: `sample_id` only; stress_test_master: `id`). So today's effect is nil on shipped data; the width matters only for recipes with a differently named key column. The key point: the user did not declare B's `isolate` as a key, and the option removes rows from B because of a join. Needs the owner (table below, P2).

## 3. Correctness of apply on real data (RUN)
- Demo tests: 12 in test_remove_from_all_demo.py, all pass.
- My own script (`demo_check.py`, engine `run_audit`, same functions as the test, my own comparison over ALL 28 tables, tier 1 and tier 2): one sample id taken from the intersection of all reached tables, removed. Result: the id is in no string column of any table at tier 1 or tier 2 (list empty), including tables reached only through a join. Compared with "before minus the victim's rows", every table is equal EXCEPT exactly two: `QA_aggregated_no_key` T2 (9 rows, count per group) and `QA_population_zscore` T2 (41 rows, same height, z-scores of the others move). Builder's claim CONFIRMED: two tables, no more. Affected plots: 17 of 17.
- `na: keep`: test `test_a_row_with_no_key_is_kept` (READ) passes; step shows `na: keep` in the demo test (RUN). A row with an empty key stays.
- All-or-nothing (RUN, `small_check.py`, my mocks): a failure on the LAST of 7 writes leaves the recipe and the counter exactly as before; a KeyboardInterrupt on the second write also. A value that does not fit the type is refused before any write (READ :309-313).
- Originals untouched (RUN): sha256 of every file under `assets/test_data` and `config/data_analysis_recipes/pipelines` equal before and after; the demo test also hashes the stored anchor parquet files (passes).

## 4. The cases marked NOT followed (RUN, `small_check.py`)
Case 4a: table A copies the key (`with_columns sid = pl.col('sample_id')`) and drops `sample_id`. Result: A is NOT reached; it is listed `key_gone_at_tier1`; `option.unsure` is EMPTY. After `apply` for S2: A still holds S2 (`sid` column: S1, S2); only E lost it. So the sample stays in a table, and the code treats this as "information", not a doubt.
Case 4b: table A lowercases the key under its own name. A IS reached (note `recomputed_here`). The step removes "S2" by comparing against the recomputed values 's1','s2': nothing is removed (after: s1, s2 both still there). The note exists in `KeyPlace.notes` but it is information only.
What the user would have to be told: "In table A your selection is not found because the column was changed or copied in this table; the sample is still there." Without this, the user believes the sample is out of every table (a silent wrong result). Severity: HIGH for what the user sees in HOME if the screen shows only `unsure`; MEDIUM as a logic gap in step 1, because the data is available (`not_reached`, `notes`). See F1.

## 5. P7: same column name, no declaration, no join (RUN, `fx.tiers(u_declares_key=False)`)
Table U holds `sample_id`, declares no key, no join reads it. Result: places = S, E, M, J1, J2, JU; U is `same_name_not_linked`, not reached, and `unsure` is empty. In the demo this case does not occur (27 places, `not_reached == ()`).
- Reading 1 (builder): "holds the key column" = linked to the key by a declaration or a join. U stays out; the user sees it listed. Safe against removing from a table that happens to use the same name for another thing (D-0355: the name alone does not make two columns one).
- Reading 2 (by name, as D-0416 point 1 reads literally, "every table that holds the key column"): U is reached. Closer to her use case (a bad sample removed everywhere), but a column of the same name may mean something else.
Needs the owner. Note that either way U should be shown to the user in the list before confirming; the code lists it (`not_reached`) but does not call it a doubt.

## 6. Tests can fail (RUN, own mutations, restored; `git status` empty at the end)
- Mutation A: removed the rollback in `apply` (the `remove_step` loop and counter reset replaced by `pass`). FAILED: `test_a_failure_in_the_middle_takes_back_what_was_written_and_the_counter` (1 failed, 57 passed).
- Mutation B: disabled the stale-option check in `apply` (`if False:`). FAILED: `test_apply_refuses_an_option_that_no_longer_matches_the_recipe` (1 failed).
Both restored with `git checkout -- <file>`. Not tested by me: the builder's five mutations (taken from its note, not re-run).
What the tests cannot see: the screen (not built), real data other than the demo recipe, the data type mix across tables beyond one test, and the oracle replays steps in plain Polars (not the real engine) in the pure tests; the real engine is only used in the demo test.

## 7. Controls (RUN, from the worktree, -n 4)
- `libs/utils/tests` + `app/tests/test_remove_from_all_demo.py`: 2777 passed, 2 skipped (81 s). The 2 skips: one is `test_remove_from_all.py:451` (a recipe broken on purpose does not load); the other is not from this branch's files (not checked).
- The two new test files alone: 69 passed, 1 skipped (-n 4); pure file alone 58 passed, 1 skipped.
- Full headless baseline: NOT run (the other reviewer's full run was active). Instead: 11 `app/tests` files that import `audit_copy`, `lineage_walk`, `key_drop` or `plan_composer` plus `test_imports_from_checkout.py`: 592 passed, 5 skipped. Failures: none, so nothing to compare with dev.
- `assets/scripts/audit_old_words.py --check`: exit code 0 (the tail printed only table rows; I did not read the full output).

## 8. Style
- Emoji ban: grep of the diff for emoji ranges: no hit.
- Comments say why (decisions quoted, PROVISIONAL marked P1-P6). Module docstring is long but useful.
- `@deps` block present, inside the module docstring, the same form as `audit_copy.py`. `dependency_index.md` is auto-generated and was not regenerated in the diff (minor; the scribe step after merge).
- README: one line, correct, says "words are provisional".
- Nit (low): the module docstring says P1 to P6; the builder's note speaks of P1-P9; the numbering is not the same list as the note, so check it against the note when the owner is asked.

## Findings by severity
HIGH (for the user in HOME):
- F1. A table where the key was copied or recomputed is reported as "information" or only as a note, not as a doubt (`key_gone_at_tier1` is not in `UNSURE_CODES`; `recomputed_here` is a note on a reached place). The sample stays in that table and the user can believe it is gone (cases 4a, 4b). Fix first (small, inside this module): count `key_gone_at_tier1` as a doubt (or a separate list the screen must show), and expose "values here are recomputed, the typed id may not match" as a doubt for the reached place, in plain data the screen can print. Without it the step-2 screen can hide it.
MEDIUM:
- F2. "Reached" for P2 widens past the declared key (join-equated undeclared columns; renames). Not a defect against D-0313 if the owner accepts it; otherwise a fix. Needs her.
- F3. Fragile coupling to the protected members of `LineageIndex` (see 1).
- F4. P7 (same name, no declaration) is listed but not called a doubt; D-0416 point 1 can be read both ways. Needs her.
LOW:
- F5. "Off by default" is only a constant here; the real proof belongs to step 2 (screen test).
- F6. `apply` writes the same `not_in` list at every table by the column name there; a table whose key has another type refuses the whole apply (correct, all-or-nothing, but then the user cannot remove from the others: not decided whether she can untick; the module says so).
- F7. Tables that compute across samples (`QA_population_zscore`, `QA_aggregated_no_key`): other samples' VALUES change. This is by nature, not a fault, but the screen must tell the user (it is not in the data of `describe`; the test only names it). Suggestion: the information is not available from `describe`; whether to add it needs the owner.

## For the owner
| # | Point | Options |
|---|---|---|
| P1 | Words of the warning ("This removes your selection from any data that holds it.") and the not-offered sentences are PROVISIONAL. | Keep; change the words. |
| P2 | Is the entity key only the declared column, or also a column a join equates with it (and a renamed copy)? | (a) declared only (B in the example is not reached by `isolate`); (b) declared plus join-equated (as built). |
| P3 | A row with an empty key is kept (`na: keep`) and the operator is `not_in`. | Keep (as the filter dialog does for "none of"); remove rows with no key too. |
| P4 | A table reached only by a link the app cannot prove is not reached but listed as a doubt. | Keep; reach it anyway after a warning. |
| P5 | `apply` describes the option again and refuses a stale list. | Keep. |
| P6 | Without the engine's plan the recipe's declared names are used and types are empty. | Keep (only used when no plan is given). |
| P7 | A table with a same-named column, no declaration, no join: not reached, only listed. | Not reached (as built); reach it by name (D-0416 point 1 literally). |
| P8 | Can the user untick one table of the list in this option? D-0416 shows the list but does not say she can change it. | No (as built); yes. |
| P9 | A source file that no recipe table reads: not reached (D-0416 says asked only if the build meets it). | Ask when it occurs. |
| New | A table where the key was copied or recomputed: the sample STAYS there (cases 4a, 4b). How is she told, and is that a warning she must confirm? | Warning on the list before confirm (suggested); refuse the option for such a recipe. |
| New | The two tables that compute across samples change the other samples' values (RUN). Tell her on the list? | Yes, a line per such table; no. |

## Not verified
- The full headless baseline and all browser tests; the builder's own five mutations; the second skipped test of the 2777 run.
- Only one demo sample id was removed in my script (the first of the intersection); the demo test removes two.
- The output of `audit_old_words.py` beyond the exit code.
- Nothing about the screen (not built). Data of `tmp.md` not read.
- Another recipe with real data (only the demo has data in the repository here; the others used the synthetic oracle of the lineage tests).
