# Panel brief: default for missing values, and formulas (2026-11-14)

You recommend; Eve decides. Principles: `.claude/workflows/agent_principles.md` (among them: inform the user and never choose for them; science transparent and reproducible). Scratch checks only under `tmpAI/panel/`.
Tags: DECIDED / CONFIRM (written, awaiting Eve) / OPEN.

## Q1. Missing values when a filter removes rows: a default, or no default?
Read: `.claude/design/home_audit_steps.md` lines 515-530 and 580-595 (the NA rule and the count message), `.claude/tasks/tasks.md` lines 38, 82, 83, 91.
Facts. CONFIRM (written as confirmed 2026-11-12 in the design file, as waiting in tasks.md): a missing value is a value; `!=` and "none of" keep the rows with a missing value, `==`, "one of" and the comparisons remove them; the count is always shown ("N rows have no value in this column: they are kept / removed"). The records contradict each other on the DEFAULT: `tasks.md:83` (O25) says default keep, set by the recipe maker; `tasks.md:82` and `tasks.md:91` say no default; the design file line 523 says "safe default: keep", needs Eve's default.
Also: NaN in a float column (a failed calculation, not an empty cell): is it a missing value in every operator? (`polars_fill_nan` and `polars_drop_nans` exist as explicit steps.)
Options: A default keep (rows with a missing value stay unless the user removes them), always counted. B default remove, always counted. C no default: the user (HOME filter) or the recipe maker (recipe step) must choose each time, the step is refused without the choice. D the rule by operator as written above, no separate choice, always counted. Say which applies to a HOME filter and which to a recipe step if you would treat them differently, and how NaN is treated.

## Q2. Formulas in recipes (FORMULA-SAFETY-1)
Read: `.claude/design/home_evidence/actions_and_polars_2026-11-13.md` lines 80-96 (options A to D and the recorded recommendation), `.claude/tasks/tasks.md` lines 86, 93, 122. The three places that evaluate a formula text: `libs/transformer/src/transformer/actions/expressions.py:221`, `libs/id_reconciliation/src/id_reconciliation/core.py:239`, `libs/viz_factory/src/viz_factory/geoms/core.py:1335`.
Question: keep formulas with a safe workaround, or block them now and solve later; which of the written options A to D.

## Your answer (at most 200 words per question)
For each option: pro, con, evidence class (RUN / READ / INFERRED). Then your recommended option and its reason. Flag first anything that changes a result silently, hides a step from the user, is a security risk, or reconsiders a decision already taken.
