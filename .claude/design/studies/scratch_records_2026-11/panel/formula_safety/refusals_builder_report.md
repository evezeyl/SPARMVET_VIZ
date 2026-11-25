# Refusals builder report (D-0257, D-0259)

Commit: see `git log -1` on branch `task/formula-refusals` (message "feat(utils): refuse set_sorted, search_sorted, pl.Unknown and pl.Binary in formulas").
Files: `libs/utils/src/utils/formula_check.py`, new `libs/utils/tests/test_formula_refusals_2026_11_18.py`, small edits in `test_formula_reads_no_outside_data.py` (two entries removed from the reviewed list, they are refused now) and `test_formula_refuses_object.py` (the list holds three types).

## Mechanism (no second one)
- Members: `REFUSED_BY_NAME` (same table as `inspect`). New table `REFUSED_BY_NAME_SUGGESTION` holds the "Suggestion:" line; `visit_Attribute` passes it to `refuse`.
- Types: `REFUSED_DTYPES` (same table as `pl.Object`). Refusing the name covers `pl.X`, `pl.X()`, inside `pl.List`, `pl.Array`, `pl.Struct`, `cast`, `lit(dtype=)`, `json_decode`.

## Messages (app form: what, then "Suggestion: ...")
- set_sorted: "set_sorted only sets a flag that says the column is sorted, without checking it; if the column is not sorted, later results are wrong with no message, so it is not allowed. Suggestion: sort the table with a sort step before the step that needs sorted data"
- search_sorted: "search_sorted assumes the column is sorted and does not check it; if it is not sorted, the answer is wrong with no message, so it is not allowed. Suggestion: there is no formula for this; use a join step on the key, or ask for the function to be added" (PROVISIONAL wording of the suggestion: I found no formula alternative, the join hint is my choice.)
- Unknown: "pl.Unknown is a type that has no values a table can hold, and decoding to it (or to an array of it) stops the calculation. Suggestion: use a type a table can hold, for example pl.String, ..."
- Binary: "pl.Binary holds raw bytes, which a recipe table does not; decoding to it stops the calculation. Suggestion: use a type a table can hold, ..."

## Facts checked (run, Polars installed)
json_decode panics (PanicException) for pl.Unknown, pl.Array(pl.Unknown, 2) and pl.Binary. `pl.List(pl.Unknown)` and `pl.List(pl.Binary)` give a plain ComputeError, not a panic, but are refused too (name rule, as pl.List(pl.Object)).
PROVISIONAL: the refusal is wider than the crash: `cast(pl.Binary)` is refused too, although it may not panic. Eve's D-0259 says refuse the type, same rule as `pl.Object`.

## Tests
New file: 28 tests (each refusal, one test per type spelling; allowed neighbours `sort`, `sort_by`, `arg_sort`, `top_k`, `pl.String`, `pl.List(pl.Int64)`, `pl.Array(pl.Float64, 3)`, `Struct` of Int64). Run: `libs/utils/tests`, `libs/transformer/tests`, `libs/id_reconciliation/tests`: 4275 passed, 3 xfailed (xfails were there before).

## Break once
Removed each entry in turn from `formula_check.py`: set_sorted: 3 failed; search_sorted: 2 failed; Unknown: 9 failed; Binary: 7 failed. File restored each time.

## Call paths
All formula checks go through `formula_problems`/`evaluate_formula`: recipe check `recipe_check.py:601`, transformer `polars_calls.py:195`, id reconciliation `core.py:254`. The plot text check (`plot_text_check.py:143,162`) uses the other two grammars (`smoother_formula_problems`, `function_string_problems`); they have no `pl.` dtype or `set_sorted` call, so these refusals do not apply there (not changed, not tested for these words).

## Grep of shipped files
Words set_sorted, search_sorted, pl.Unknown, pl.Binary in `config`, `assets`, `docs`, `libs`, `app` (yaml, md, qmd, py): only `formula_check.py` itself and tests. No shipped recipe, gallery bundle or doc uses them. No help text listing allowed members was found in code or docs. `@deps` of `formula_check.py` updated (`REFUSED_BY_NAME_SUGGESTION`).

## Not done
No docs edited (spec text of section 15 may list refused names; rule/design files not touched by order).
