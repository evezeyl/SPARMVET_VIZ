# EXPORT-FILTER-VALUE-1: root cause (findings)
Labels: RUN = I ran it (scripts `matrix.py`, `extra.py` in this folder, `PYTHONPATH=. ./.venv/bin/python`), READ = read in code/doc, INFERRED.

## 1. Cause chain: one value, panel to exported recipe
1. Panel (READ `app/handlers/filter_and_audit_handlers.py:195-300`): the widget depends on the column.
   A numeric column with a one-value operator gets `input_numeric`: the value is a real number. A column that is not Int/Float
   (text, date, true/false), or a numeric column named as a discrete axis of the plot, gets a multi-select box: values are TEXT (`str(v)`, line 200).
   `between` gets two number boxes. If no sample could be read, a text box (text).
2. Row stored (READ :380-418): `{column, op, value, dtype}`. The dtype is read from the real frame when the row is added (`str(sample[col].dtype)`, :387).
   A number stays a number (:407); text stays text (:413-415, comment "downstream coercion if needed").
3. Sent to audit (READ :478-483): `params = {column, op, value}` plus `dtype`. So the dtype IS carried in the audit node and in the session file.
4. Export (READ `app/handlers/export_handlers.py:1223`, `t3_translator.py:104-127`): the translator reads `column`, `op`, `value` ONLY. It never reads `dtype`.
   It writes `value` as it is: a number stays a number, text stays text (RUN: `'90'` stays `'90'` in the YAML, `90` stays `90`). THE DTYPE IS LOST HERE.
5. Re-run (READ `libs/transformer/src/transformer/actions/modified.py:52-70,82`): `modif_filter` builds `pl.col(c) >= value` / `is_in(value)` with the value as written.
   No coercion, no look at the column type (the action only reads the column NAMES, :78). Polars then refuses (RUN: `ComputeError: cannot compare string with numeric type (i64)`; for in/not_in `InvalidOperationError ... cannot check for List(String) values in Int64`).
6. The HOME view works because `t3_audit_engine._apply_filter_rows` (READ :92-158, RUN) re-reads the real column type at each call and coerces through `coerce_filter_value`. The export does not.
Correction to the task line: the panel does NOT always store text. On a plain numeric column with `>`, `<`, `=`, the value is a number and the export works (RUN, all "native" rows SAME). Text reaches the export from the multi-select box: a numeric column used as a discrete axis (a Year as Int), a date, a true/false column; and from hand-written values.

## 2. "Are the types not defined in the recipe?"
- Declared types exist (READ `recipe_format_spec.md:124,373` DEC27: `type` is required on every field, any Polars dtype). The data is read with them, so at re-run the column type is known and correct. `modif_filter` just does not use it.
- `modif_filter` compares the YAML value with the column as written, no coercion (READ modified.py:52-70; RUN). A recipe author who writes `value: "90"` on an Int column gets the same failure (RUN: `ComputeError cannot compare string with numeric type (i64)`). The checker does not catch it either: `step_problems` checks shapes only and returns `[]` for it (RUN).
- Is the refusal decided? NOT a written decision for the value type. Facts:
  - DECIDED: no hidden choice, every choice written in the recipe (`recipe_format_spec.md:16`, DEC33 :135); `modif_filter` shares the audit's vocabulary (DEC39 :141).
  - OPEN, named by the team: `app/tests/test_modif_filter_vs_home_filter.py:65-70` "Difference to decide: the panel sends text, so HOME casts it; a recipe writes the right type"; tasks.md:201 FILTER-UNIFY-1 lists "a text value is coerced to the column's number" as a silent difference, "Design decision for Eve".
  - OPEN: tasks.md:44 FILTER-DTYPES-1 (one conversion table per column type, tests first). tasks.md:38 NA-RULE-63 is about missing values only; not this.
  - No ADR-097/098/099 text about the type of a filter value (grep of the three: no hit). `home_audit_steps.md` section 19: nothing on value types.
  - FROZEN: `t3_translator.py` (build brief S4, `.claude/tasks/home_exploration_build_brief.md:13`), also `export_handlers.py`; registered actions in `libs/transformer` change "only" with Eve's yes (same line).
  So: INFERRED accident, written as "difference to decide", not a decided rule.

## 3. Operator x column type (value as the panel stores it; HOME view vs export re-run) RUN
Native = a number from the number box. Text = from the multi-select / text box. "Export" = translator then `modif_filter` on the same frame.
| Operator | Int / Float, native | Int / Float, text | Date (text) | Boolean (text) | String holding digits (text) |
|---|---|---|---|---|---|
| eq ne gt ge lt le | SAME | FAILS (ComputeError) | both HOME and export FAIL (the panel gives a list, so it becomes in/not_in) | SAME, but both WRONG (see below) | SAME |
| in, not_in | SAME | FAILS (InvalidOperationError) | HOME works; export FAILS | HOME gives no rows ("True" vs "true"); export FAILS | SAME |
| between | export refuses at export time: UntranslatableNode (not a type problem; tasks.md:42 N11) | same | HOME fails (ColumnNotFound) | same | same |
- Different rows silently: NONE found in the 63 cases of matrix.py and the 12 of extra.py (RUN). Every difference is a loud error or a refusal; no case where the export runs and returns other rows than HOME.
- But loud only at RE-RUN: the export itself never runs the steps (READ export_handlers.py:1223-1226 only builds the recipe), so a bad export is written without a warning (INFERRED from reading; not run end to end).
- Not an export problem, but found: Boolean. A scalar `== "True"` (text) gives NO rows in HOME and in the export (same), and `in ["True"]` gives no rows in HOME (the column is cast to "true"). The multi-select offers "True" (`str(True)`). A real number box value `True` works. Date scalar ops with text fail in HOME as well. These are FILTER-DTYPES-1 material.
- Also same in both: native `90.5` on an Int column, `eq` gives no rows, `ge` keeps 91 (RUN; #62 is fixed).
- `UInt`, `Decimal`, `Datetime`, `Categorical`: not run.

## 4. Where a fix could live (facts only)
| Place | What it would change | Old sessions and old exports |
|---|---|---|
| Panel, when it stores the row (`filter_and_audit_handlers.py:407-418`) | new rows hold typed values (the dtype is known there) | Old session files and old audit nodes keep text. Nothing is rewritten. Exports made from them stay as written. Frozen file (S4). |
| Translator at export (`t3_translator.py:127`; has `params["dtype"]` for nodes sent since the dtype was recorded; no frame at hand) | every future export writes typed values, also from old session files that carry `dtype` | Exports already written stay broken. Nodes without `dtype` cannot be fixed here. Frozen file. Cannot fix a hand-written recipe. |
| `modif_filter` at run time (`modified.py:82`; the frame schema is at hand, `lf.collect_schema()`) | one place: every recipe, hand-written or exported, old or new, runs. Changes the meaning of the action: today a text value on a number is refused | Old exports start to run. Hand-written `"90"` stops failing. It decides FILTER-UNIFY-1 (open). Needs Eve's yes (S4). Hash/key of recipes unaffected only if the YAML text is unchanged (INFERRED). |
| Checker (`step_problems`, `utils.ui_schema`) | a text value on a declared number column is reported before the run (needs the declared types, which the checker does not get today: it receives the action schema only, RUN) | Old exports are reported, not repaired. |
| Session file / audit node | already holds `dtype` (:482-483); a migration could add typed values | Would rewrite saved sessions; no migration exists. |
Shared fact: `coerce_filter_value(value, dtype)` (`libs/utils/src/utils/filter_values.py`) takes the dtype as text or a Polars dtype and returns the value unchanged when it is not a number, so a bad text still fails visibly. It does not handle Date, Boolean.
Tests that record the defect: `app/tests/test_filter_int_equivalence.py` (12 strict xfail; the file passes today: 87 passed, 16 xfailed, RUN).
