# How a formula in a recipe becomes a calculation: the page for Eve to decide

Coordinator, 2026-11-18, 14:59 by the clock. This is the study she asked for on question 18 (D-0267: study option D, build nothing now).
Evidence: `EVIDENCE.md` in this folder (a trial branch, `trial/formula-d`, never merged; each claim there is marked "ran" or "read"). Four viewpoints read it: architect, scientist, user who is not a developer, and a security reading. They recommend. She decides. Nothing is built.

## The question in plain words

A recipe may hold a formula, for example `pl.col('a').str.to_lowercase()` in a `mutate` step.
- **Today:** the app checks the text against a list of allowed names, and then lets Python RUN the text.
- **The other way (option D):** the app reads the text piece by piece and calls only the allowed Polars functions itself. The text is never run.

Her rule, decided: "no code is executed from recipe text" (D-0273). Formulas are not blocked now (D-0274).

## Flagged first

1. **Today her rule holds only because the check holds.** The check is the single barrier. In the trial, with the check switched off, running the text let through 10 of 12 harmless probes (for example reading the process number through the Polars module). The other way refused all 12 without the check. With the check on, both ways refuse them.
2. **Neither way changes the science.** Both pass the same check and call the same Polars functions. Proven on what the recipes use: 113 of 113 formula runs on the real data gave the same calculation and the same column; 102 of 102 tables were identical; 1597 existing tests pass with the other way switched in; the 16 formulas of the demo recipe pass today's check and give the stored tables.
3. **Things that can change a result silently under BOTH ways** (found on the way, not caused by either):
   - `hash()` gives other values after a Polars update: a stored column would shift with no message.
   - In one trial case, taking a single column from a table step that removes duplicates "keeping the order" gave a different row order on every run (10 runs, 10 orders). The whole-table path the app uses was stable. The scientist could not reproduce it on a small table. It is not known whether any shipped recipe or plot takes that path.

## The options

- **K. Keep today's way** (check, then run the text).
- **D2. The other way with two readers:** today's check stays as it is, and a second piece of code builds the calculation. This is what the trial built (269 lines).
- **D1. The other way with one reader:** one piece of code both checks and builds, so the two can never disagree. Not prototyped.

## The viewpoints

| Option | Viewpoint | For | Against | Evidence |
|---|---|---|---|---|
| D1, one reader | Architect (ranks it first) | Makes the decided rule literally true; one source of truth, no drift | Not prototyped; a reader that builds would also compute huge constants at check time and needs a guard first; today's refusal messages must stay exactly as they are (tests pin them) | read: `formula_check.py:300-360, 517` |
| D2, two readers | Architect (second) | Proven by the trial | The two readers drifted once in the trial (a chained "when ... then ... when ... then" formula was refused by the builder); it leans on Polars internals that are not public | ran in the trial |
| D (either) | Security reading | A second, independent barrier: one missed name costs "a listed function is called" instead of "code runs" | Does not make a wrong list entry, a dangerous function, a crash or a huge size safe | ran: 12 of 12 probes refused |
| D (either) | Scientist | Removes the running of text and nothing else | Wants more proof first (below) | 113 of 113, 102 of 102 |
| D (either) | User | The writer sees no change; a formula is written as before | Two refusal messages are not plain | 169 of 169 accepted texts built the same |
| K, keep | all four rank it last | Nothing to build; proven by today's tests | The rule depends on one list being right; two rules of the check fail no test when broken | ran: the underscore rule and the exponent limit each fail 0 tests |

All four recommend the other way. They differ only on one reader or two, and on how much proof comes first.

## What stays true whichever she chooses

- The list of allowed names is the one thing that must be right. An entry that should not be there is equally dangerous in both ways (one such entry was on the list until 2026-11-17).
- One crash is left: a certain type (`pl.Array`) given to `json_decode` stops the app.
- A very large constant calculation (a power of a power of a power) can take minutes or fill memory. Both ways compute it.
- The other way refuses a few odd shapes that today's way lets through and that do nothing useful (a Python method on a plain value, such as sorting a written list). No shipped recipe uses one.

## My recommendation

1. **Yes to the other way, as one reader (D1), built after the big recipe change is merged.** Reason: it is the only option under which her decided rule is true by construction and cannot drift. Build time is information only: the trial reader is 269 lines; two places call it.
2. **Before it replaces today's way, the scientist's proof:** every allowed function and operator run through both ways on a messy table (empty values, not-a-number, ties, an empty table, mixed types), and the results compared. The 17 distinct formulas run on real data so far are the ones in use, not all the ones allowed.
3. **Now, whatever she chooses, small and safe:** a test for each of the two rules that fail no test today (the exponent limit has none at all).
4. The small questions below, each with my suggestion.

## What she decides

1. K, D2 or D1.
2. If D: the scientist's proof first, yes or no. (Suggestion: yes.)
3. `shuffle`, `sample` and a random rank in a formula. They are refused today (her decision of this morning). Keep them refused and point the writer to the step `polars_sample` with a seed, or allow them when a seed is written as a plain number? All four viewpoints: keep refused. (Suggestion: keep refused, and reword the message as the user viewpoint proposes: "shuffle and sample give a different table each run ... use the step polars_sample with seed: 1".)
4. `hash()` in a formula: refuse it, or allow it and write the Polars version into the export so a shift can be traced? (Suggestion: allow and record the version; a scout first checks whether the export already records it.)
5. The remaining crash: refuse `pl.Array` as the type given to `json_decode`, with a plain message? (Suggestion: yes. Catching crashes in general stays "not now", as she decided.)
6. A limit on the size of a constant calculation: yes or no, and it would be a new refusal. (Suggestion: yes, a small fixed depth; the number is hers.)
7. A Python method on a plain value (for example `'abc'.count('a')`): refuse with a message that gives the Polars way? (Suggestion: yes; the other way refuses it anyway.)
8. The underscore refusal message: reword it as the user viewpoint proposes ("'__class__' is a Python internal, not a column function. A recipe formula may only use pl.col, pl.lit, pl.when and the Polars column methods ...")? (Suggestion: yes.)
9. The row-order finding: a scout finds which shipped recipe steps and which plot paths take single columns after a duplicate-removing step, and a test is written for it. This is a check, not a build. (Suggestion: yes, soon: it concerns reproducibility of a figure.)

## Not done in the study

No browser test. The three "size" hostile lines were never run (on purpose: memory). Formulas in the docs pages were not scanned. Crashes were searched only in `json_decode`. The earlier options B and C of question 18 were not prototyped. The one-reader form (D1) is a design, not a prototype.
