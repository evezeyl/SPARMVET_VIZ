# Panel brief: the HOME view and the export disagree (2026-11-14)

Read first (facts proved by running): `tmpAI/panel/export_value/findings.md` and `tmpAI/panel/step_order/findings.md`.
You recommend; Eve decides. Principles: `.claude/workflows/agent_principles.md`. Scratch checks only under `tmpAI/panel/`.

## Q1. A filter value stored as text (N10, with N9 and N11)
Facts. DECIDED: "no hidden choice" (recipe_format_spec.md:16, DEC33); `t3_translator.py` is frozen (ADR-097, build brief S4), a change needs Eve's yes. OPEN: whether a text value on a number column is refused or converted (FILTER-UNIFY-1, tasks.md:201).
The multi-select box stores text for a number shown as discrete (Year), for Date and Boolean. HOME converts with the real column type; the export writes the text; the re-run stops with an error. No silent difference found in the export. Silent today: the PLOT filter `in` / `not_in` compares as text (N9: `in [90.0]` shows no rows in the plot, the table keeps them).
Options: A do nothing. B the translator writes the value with the type stored in the step (`dtype`). C `modif_filter` converts the value to the column type at run time and fails with a plain message when it cannot (also repairs exports already written and hand-written recipes; changes the engine for every recipe). D the panel stores a typed value at recording. E a check at export time (and in the recipe checker) refuses a value that does not fit the column type. Combinations are allowed. Also say: fix N9 now or with FILTER-DTYPES-1; `between` (N11) translated or refused.

## Q2. A drop and a filter on the same column (N13)
Facts. DECIDED: the export follows "the same steps and order as the HOME data preview" (ui_implementation_contract.md:203). The design says a filter on a dropped column is "not possible" (home_audit_steps.md:326): not built. CONFIRM: stage-2 spec P5 (one audit copy read by every view; v0.1, not confirmed by Eve). OPEN: what the user sees.
Three orders exist: table and TSV run filters then drops; the plot runs drops then filters and SKIPS a filter whose column is gone, silently; the exported recipe runs the recorded order. Result on a shipped plot: "filter n50, then drop n50" gives table 21 rows, plot 42 rows; the results bundle holds a TSV of 21 rows and a plot of 42. "Drop, then filter" gives table 21, plot 42, export re-run error.
Options: A do nothing. B refuse at recording: the filter panel offers only columns still present, and a drop of a column used by a recorded filter is refused or needs a choice. C every view (table, plot, TSV) runs the recorded order, and a step whose column is missing is an error shown to the user, never skipped. D the translator reorders to match the table. E a check at export refuses and names the step. Combinations are allowed. Say separately: must the silent skip in the plot path be removed now (it is independent of the order)?

## Your answer (at most 250 words per question)
For each option: pro, con, evidence class (RUN / READ / INFERRED). Then your recommended option or combination and its reason. Flag first anything that changes a result silently, hides a step from the user, or reconsiders a decision already taken. Say what happens to sessions and exports saved before.
