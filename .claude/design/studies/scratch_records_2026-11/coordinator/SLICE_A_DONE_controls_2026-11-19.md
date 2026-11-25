# Slice A of the HOME audit redesign: done and controlled (2026-11-19, 19:58 by the clock)

dev = `a1d79820`, not pushed. Final controls by a reviewer on the content of this head (branch head `a9c20c17`); every output in `tmpAI/coordinator/slice_a_final/`.

## What slice A delivered (nothing a user of the shipped recipes sees changes, except one rebuild of the stored tables)
1. The map of a recipe, one for the whole app (`libs/utils/src/utils/recipe_graph.py`): which source table feeds which table, join and plot; the columns of a table where the recipe says them, "unknown" otherwise, never guessed. Blueprint's navigator, the tube map and the app's recipe check read it.
2. A key per stored table (`app/modules/cache_keys.py`, cache version 6): engine, the table's definition and what it reads, the data files it reads; tier 2 and a plot's own steps add a part each. A change in one table rebuilds only what depends on it.
3. The engine reads a plot's own steps (`tier3: steps` on the plot entry; `DataOrchestrator.materialize_tier3`). The plot, its table in My view and the export read one table. HOME accepts such a recipe and refuses a bad step at load.
4. The audit recipe, in memory, on no screen yet (`libs/utils/src/utils/audit_copy.py`, `app/modules/audit_run.py`): a copy of the recipe; a step added at the end of a tier list and removed again; the copy minus its audit steps must equal the original; the copy's keys carry the audit steps as their own parts (without reasons); a run that reuses every untouched table from the original and builds only the changed ones into the audit's own folder, and says which plots are affected.

## Controls (RAN by the reviewer)
| Run | Result |
|---|---|
| qa flags through the Bootloader | audit, sessions, export, Blueprint, agent switch on (backend disabled), testing mode on, ghost save OFF |
| App import | OK |
| Headless suite, once | 12254 passed, 13 skipped, 31 xfailed, 0 failed |
| 28 browser files, qa, three at a time | 252 passed, 3 skipped, 1 xfailed, 1 failed (a session list test; passed alone, and its whole file passed alone: 37 passed) |
| All eight setups start | 9 passed |
| Golden baseline | identical |
| Pictures | 50 identical, plus the one known row (the empty orphan recipe; its refusal text lists one more check word) |
| Audit run on real data (`1_test_data_ST22_dummy`, one filter at tier 1 of the table `Summary`, keeping 221 of 623 rows) | 26 of 28 tables reused from the original, 2 built; 1 of 17 plots affected (`phenotype_genome_length_fragmentation`); the original's stored tables byte-identical; after removing the step: nothing built, no plot affected, the audit folder empty |

Small audits, compared with before slice A (not gates): old-words exit 1 as before; document links 11 problems as before; UML audit as before (PKG-TIERS edges; one missing test name).

## Not covered
Ghost save (off in the qa setup); setups other than qa only started; the Quarto render of the export; two runs at once on one audit folder; no screen uses the audit recipe yet.

## Left open, small (tasks)
- A refused audit run removes the original's stored tables when the original's folder lies INSIDE the audit folder (only a lost cache, rebuilt from keys; not a layout the app uses): refuse nested folders in both directions.
- One more browser test that fails only under parallel running: `test_shiny_smoke.py::TestSessionListRefresh::test_delete_all_sessions_requires_confirm_then_clears_list`.
- The position of an audit step inside its key part is an addition to the decided key form (marked provisional in the code).
- Texts out of date: `tmpAI/coordinator/STALE_TEXTS_after_slice_A.md`.

## Questions for the owner
`tmpAI/coordinator/QUESTIONS_FOR_THE_STOP.md`: the slice 0 points 1 to 8 and Q-A1 to Q-A17.
