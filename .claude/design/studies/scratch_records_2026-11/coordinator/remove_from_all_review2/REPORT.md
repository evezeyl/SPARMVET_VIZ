# Second review: task/remove-from-all (dfe85e79 on top of 06dde4c9)

Verdict: FIT TO MERGE, with one small wording defect (F-A) the owner or a follow-up can fix, and three points that need the owner (table below). Nothing is wired to HOME yet, so no user sees this code today.

Setup (RUN): PYTHONPATH = worktree root + each `libs/*/src`; `utils.__file__` printed under `.claude/worktrees/remove-from-all`. Load read before every run; `-n 4` at most; full run started at load 4. Scripts and outputs: `tmpAI/coordinator/remove_from_all_review2/` (`repro.py`, `demo6.py`, `baseline.txt`, `oldwords*.txt`).

## 1. F1 of the first review: the one list before and after apply
Read `git diff 06dde4c9..dfe85e79`. `RemoveFromAll.may_stay` (before apply) holds every table where the removal cannot be proved; `Applied.not_written` (nothing written, selection may stay) and `Applied.may_differ` (step written, values may not match) are that same list split by `written`. `KEY_GONE_AT_TIER1` is now a doubt (`UNSURE_CODES`). RUN, my own `repro.py`:
| Case | before apply | after apply | Really in the data after |
|---|---|---|---|
| Key copied (`sid`), `sample_id` dropped | A: `key_gone_at_tier1`, written False, sentence | `not_written ['A']` | S2 still in A (`sid`): the list told the truth |
| Key lowercased under its own name | A: `values_unproved`, written True, sentence | `may_differ ['A']` | s2 still in A: the list told the truth |
| Renamed twice (x then y) | no item, reached | none | S2 gone (correct, no false alarm) |
| Key as an unpivot index | `values_unproved` (unread step) | `may_differ` | S2 gone: a false alarm, the safe side |
| Key as an unpivot value | `not_followed` | apply refuses (nothing reachable) | not touched |
| `str_split` of the key | `uncertain_link` | apply refuses (nothing reachable) | not touched |
| group_by key + mean | no item, reached | none | S2 gone (correct) |
| Table reached by two joins (one by `left_on/right_on`) | no item | none | S2 gone in A, B, C (correct) |
Both reproductions of the first review now name the table, before and after, in a plain sentence. I found no path where a value stays and the caller gets no item, EXCEPT the one that stays information by choice:
- `same_name_not_linked` (a table with a column of the same name, no declaration, no join; code `same_name_not_linked`, RUN on `fx.tiers(u_declares_key=False)`): the sample stays in table U. The caller sees U in `option.not_reached` with that code, but `may_stay` is EMPTY and `Applied` has no item for it. A screen that reads only `may_stay` and `Applied` shows nothing for U. This is the owner's point P7 (below).
- Also not covered by design: a source file no recipe table reads (D-0416 says ask only if the build meets it).

## 2. The honesty cost on the demo recipe (RUN `demo6.py`; demo test 12 passed)
27 of the tables are reached; `may_stay` = 6, all `written` True, code `values_unproved`, none `not_written`: `Summary`, `Summary_quality`, `Detailed_summary`, `Quast_with_metadata`, `Summary_phenotype_length_fragmentation`, `QA_ST_with_NA` (the notes are one to four `unread_step_passed`). The builder's data test shows the sample IS gone in all six. What a HOME user would be told, for each of the six: "In the table 'Summary' the key is passed through a step the app cannot read before the removal is written, so the values given may not match the values there: the selection may stay in this table. Check the table after the removal."
- Does the sentence tell "nothing written here" from "written, cannot prove the values match"? The two kinds have two different sentences (`may_stay_sentence`), and the item has `written` True/False. The "written" sentence says "before the removal is written" and not plainly "a removal IS written in this table". A user can still read it as "nothing is removed". It does not say which step the app cannot read (the notes hold only the code, not the step). So: distinguished in data, only partly in words.
- Honesty cost: 6 of 27 tables (22 %) carry a warning although the removal works, because the app cannot read a step. Safe side, but a warning that is often wrong teaches the user to ignore it.
Options for the screen (not decided here; owner):
| Option | Pro | Con |
|---|---|---|
| (1) One list, as built: all six lines before the confirm and after | honest, simple, no hidden table | 6 lines on the demo recipe, mostly false alarms |
| (2) Two groups: "nothing is written here" (red) and "written, check the table" (amber) | the two facts are not mixed | two parts of the screen; the second is mostly harmless |
| (3) Group (2) shown collapsed with a count, group 1 open | little noise | the user may not open it |
| (4) Name the step the app cannot read in each line | the user can judge | needs the step name added to the data (not there today) |

## 3. F3: public accessor, no behaviour change of the walk
READ `git diff 06dde4c9..dfe85e79 -- lineage_walk.py lineage_records.py`: `lineage_walk.py` gets two new public methods (`certainty_from`, `uncertain_ends`), the import of `Certainty` and the `@deps` lines; 3 lines removed in total (the import line and the two `@deps` lines). No existing function of the walk is touched. `Certainty` (cost, reason, notes, `certain`) is a frozen dataclass with a docstring in `lineage_records.py`. The subclass `_Index` is gone (`describe` uses `LineageIndex` directly). Tests: 2 new tests in `libs/utils/tests/test_lineage_walk.py` (certain/uncertain, a recompute note, a step the app cannot read, a dead end by unpivot). Weak spots (low): no test of two seeds (the best path over seeds), none of the `within` limit; `uncertain_ends` returns the private type `_Dead` in a public signature. The full headless baseline (below) runs every lineage test and every `app/tests` file that imports the lineage modules: no failure caused by the branch.

## 4. `apply` returns `Applied`
RUN grep `remove_from_all` in `app/` and `libs/` (source files): only `libs/utils/src/utils/remove_from_all.py`, its two test files, and the walk/records files that name it in `@deps`. No production caller; the tests were adapted (`demo.applied.step_ids`). A stale copy `libs/utils/build/lib/utils/*` exists in the worktree directory but is not tracked (`git ls-files libs/utils/build` printed nothing).

## 5. My mutations on the fix (RUN, restored, `git status --short` empty at the end)
- M1: `KEY_GONE_AT_TIER1` taken out of the list in `_may_stay`: 3 failed (the copied-key test, the loses-the-key test, the sentences test).
- M2: `apply` returns empty `not_written` and `may_differ`: 3 failed (the copied-key test, the recomputed-key test, the demo list test).
Both restored with `git checkout --`.

## 6. Controls
- `app/tests/test_remove_from_all_demo.py`: 12 passed (5.7 s). The new demo test for the 6 tables is in it.
- Full headless baseline (section 8 of `rules_verification_testing.md`, from the worktree, `-n 4`): `4 failed, 13869 passed, 15 skipped, 33 xfailed, 2 warnings in 2369.67s (0:39:29)` (`baseline.txt`). The 4 failures, none caused by the branch:
  - `app/tests/test_decision_ledger.py::test_real_ledger_header_counts_equal_the_computed_counts` and `::test_mutations_of_a_copy_of_the_ledger_are_caught`: `AssertionError ((400, 393, 1, 2, 4), (416, 409, 1, 2, 4))`. The branch does not touch the ledger; its base (71ab966b) has the bold header "Total 400" and 416 lines. On dev (main tree, header 428, 428 lines) `test_decision_ledger.py` gives 35 passed. They pass once the branch is merged on today's dev.
  - `app/tests/test_panel_widths_browser.py::test_the_handles_cover_no_first_control_in_every_user_space[Blueprint Architect-1100]` and `[Test Lab-1100]`: `TypeError: Cannot read properties of undefined (reading 'top')` under load (the load was 10 to 18 while other runs were active). Re-run alone at load 3 in the worktree: `8 passed` (`-k first_control`, 97 s); on dev, same: `8 passed` (99 s). A load flake, not the branch.
- `audit_old_words.py --check`: exit 1 in the worktree ("CHECK FAILED: retired words remain outside the exclusions", 2422 files, persona 66, manifest 98, recipe 16137, profile 327, project 446 in content). The same on dev (main tree): exit 1, same kinds and nearly the same counts (differences = different file sets). The first review recorded exit code 0; it did not read the output. I cannot tell which word hits the branch adds; the audit fails as a whole on dev too (not attributable to the branch).
- Emoji scan of `git diff 71ab966b...HEAD` (added lines, emoji ranges and the check/cross marks): 0 hits.
- Ledger: `./.venv/bin/python assets/scripts/decision_ledger.py check --decided D-0406 ... D-0424` on the MAIN tree: `OK` for all 19 numbers.
- Merge into dev today: `git merge-tree --write-tree dev task/remove-from-all` exit 0 (no conflict). Dev moved only in record files and two rule files (`.claude/knowledge/decision_ledger.md`, handoff, `rules_runtime_environment.md`, `rules_verification_testing.md`, `tasks.md`); my `comm` of the changed-file lists of dev and the branch against 71ab966b is empty: no overlap.

## Findings
HIGH: none.
MEDIUM:
- F-B. `same_name_not_linked` stays outside `may_stay` and `Applied` (see section 1): a user of a screen that shows only those two sees no hint that the sample stays in such a table. Needs the owner (P7); one line in the screen from `not_reached` would close it.
LOW:
- F-A. Wording: the sentences for the not-written kinds start "In the table 'A' no longer holds ..." / "has a step ..." / "has a column ..." / "has the key ...": the subject is missing, ungrammatical (`may_stay_sentence`, `remove_from_all.py`). Words are PROVISIONAL; fix with the owner's wording.
- F-C. The two "values may differ" and "not written" sentences are not clear enough on "a removal IS written here" (section 2); the step the app cannot read is not named.
- F-D. Weak tests of the accessor (two seeds, the `within` limit); `_Dead` in a public signature.
- F-E (unchanged from the first review, not part of the fix): the two tables that compute across samples (`QA_aggregated_no_key`, `QA_population_zscore`) change other samples' values and are not in `may_stay`; the screen cannot learn it from `describe`.

## For the owner
| # | Point | Options |
|---|---|---|
| P2 | Is the key only the declared column, or also a column a join equates with it and a renamed copy? (the "key family"; nil effect on the 7 shipped recipes) | (a) declared only; (b) declared + join-equated (as built) |
| P7 / F-B | A table with a same-named column, no declaration, no join: reached or only listed? And is it in the "may stay" list? | (a) not reached, shown in the list; (b) not reached, information only (as built); (c) reached by name (D-0416 point 1 literally, with the risk of another meaning of the name) |
| P8 | Can she untick one table of the list in this option? | no (as built) / yes |
| Screen | What does the screen show for "may stay" and how often? (6 of 27 tables on the demo, all "written, cannot prove the values match") | the four options of section 2 |
| F-E | The two tables where other samples' values change: a line on the list? | yes / no |

## Not verified
- The browser tests (smoke, blueprint smoke, export, every-app-features) were not run (outside the headless baseline). Two browser tests of `test_panel_widths_browser.py` were run alone (pass).
- The screen (not built); recipes other than the demo with real data; a key lost by an outer join or created by a step from another column (reasoned only: the removal is written upstream).
- Which words `audit_old_words.py` would flag in the branch's own diff.
- The builder's mutations.
