# Actions and Polars: names, steps done at once, the whitelist (2026-11-13)

**Written for:** Eve (decisions) and the recipe session (the policy goes into the spec). Eve asked on 2026-11-13: stay aligned with Polars; check which action names already mean something else in Polars; actions that do several steps at once will go; what is the whitelist; Blueprint is not touched now but what changes must be recorded.

**Evidence labels.** VERIFIED = run by a probe (`tmpAI/architect/polars_names_probe.py`, `polars_wraps_probe.py`, `polars_names_bodies.py`). READ = the body of the action was read (25 of 67 actions: the ones named below). NOT READ = judged from the name only; each package reads the body before it changes the action. Counts of recipes are files that contain the word (`grep -l` in `config/data_analysis_recipes` and `assets/gallery_data`), comments included.

## 1. The whitelist

`final_contract` of a recipe. The rule (`rules_data_analysis_recipe_structure.md` section 5) calls it an exclusive whitelist: a column that is not listed is dropped. In the code it is `Orchestrator._apply_final_contract` (VERIFIED earlier today): it acts on Tier 1 only, a listed column that does not exist only prints a line, the types are not applied, and the order of its keys is the order of the columns (and part of the Tier 1 key). 6 recipe files contain `final_contract`; the Blueprint navigator reads it as a slot (`data_analysis_recipe_navigator.py:134, 456`). It is not `output_fields` of a schema (a second, different field).

## 2. Names against Polars

**Same name, but the action does something else** (VERIFIED by running or READ):

| Action | Polars | The action |
|---|---|---|
| `is_in`, `not_in` | `Expr.is_in` returns a true/false column | filter the rows (a filter, not an expression) |
| `value_counts` | `Expr.value_counts` returns a struct column | returns a new frame (value, count), first-appearance order; collects (not lazy) |
| `coalesce` | `pl.coalesce` returns a column | overwrites the first listed column |
| `percentile` | Polars has `quantile` for percentiles | wraps `Expr.rank`, returns rank / number of rows: the name is misleading |
| `rename` | `LazyFrame.rename(mapping)` | two forms (mapping, or columns + new_name); no `wraps`; a second action `rename_columns` exists |
| `sort` | `sort(by, ...)` | accepts `by` or the alias `columns`; always a stable sort |
| `sample` | no seed by default | seed 0 by default (ADR-090, a declared difference); collects |

**Same name, same meaning** (READ or by `wraps`): `drop_nulls`, `explode`, `unnest`, `unpivot`, `pivot`, `join` (takes a named ingredient instead of a frame), `cast`, `shift`, `interpolate`, `cum_sum`, `cum_count`.

**One Polars method, several actions** (VERIFIED, `wraps`): `LazyFrame.unique` has three (`drop_duplicates`, `unique`, `unique_rows`; the description of `unique` says "alias"); `LazyFrame.filter` has five (`filter_eq`, `filter_ne`, `filter_gt`, `filter_lt`, `filter_range`); `Expr.is_in` two; `Expr.fill_null` two (`fill_nulls`, `fill_nulls_direction`); `Expr.over` two (`count_by_group`, `window_agg`); `LazyFrame.join` two (`join`, `join_filter`).

**Not a Polars name, so no conflict, but not the Polars word** (VERIFIED): `keep_columns` (Polars: `select`), `drop_columns` (`drop`), `drop_duplicates`, `unique_rows` (`unique`), `rename_columns` (`rename`), `fill_nulls` (`fill_null`), `round_numeric` (`round`), `summarize` (`group_by` + `agg`), `mutate` (`with_columns`), `strip_whitespace`, `regex_replace`, `regex_extract`, `null_if`, `replace_values`, `recode_values`, `z_score` and 24 actions in all without `wraps` and without a Polars name. All `wraps` entries resolve (0 broken).

## 3. Actions that do several steps at once (candidates; READ unless marked)

| Action | Steps done at once |
|---|---|
| `split_and_explode` | split a string, then explode to rows (two Polars methods) |
| `split_column` | split, pick parts, join the remainder into the last part, optionally drop the source; **returns the frame unchanged when the source column is absent** |
| `split_column_to_parts` | `split_exact`, rename the fields, unnest (a comment says it casts to Float64; it does not) |
| `top_n_other` | count, rank, join back, label the rest "Other" (about 8 Polars calls) |
| `derive_categories` | reads an external file and maps each row with a Python function (`map_elements`): not a Polars operation |
| `keep_columns` | select **plus** silently put the primary keys first |
| `drop_columns` | drop **plus** silently protect the primary keys **plus** silently ignore a column that does not exist |
| `summarize` | group and aggregate; an unknown `agg` is silently counted |
| `recode_values` | returns the frame unchanged when `column` or `rules` is missing |
| `label_if`, `window_agg`, `count_by_group`, `horizontal_stats`, `date_extract` | NOT READ (judged by size and name) |

## 4. How much would the shipped recipes change

Files that contain the word: `keep_columns` 7, `final_contract` 6, `drop_columns` 3. In the Python of `app/` and `libs/blueprint_arch`: `keep_columns` 0, `drop_columns` 17 (mostly the audit translator, `t3_translator.py:142`, and tests), `final_contract` 37 (the orchestrator, cache keys, export, tests). So the migration of the shipped recipes is small; the tests and the audit translator are the larger part.

## 5. Register: what Blueprint will have to change afterwards (Blueprint is NOT touched now; Eve 2026-11-13)

From grep, not read in full: the action picker and forms are built from `ACTION_SCHEMAS` (`ui_schema`), so renamed or new actions appear by themselves but their `yaml_example`, help and widgets must be right; the `dtype_picker` options list needs the integer type (3 hits of `dtype_picker`); `wrangle_studio.py:1735` checks an inline `final_contract`; the navigator reads `final_contract` as a slot (lines 134, 456); a trailing `select` step would replace the contract panel; the form of an `H1` role (`columns` list, `new_column`) is the widget `column_selector` plus the per-action table; spec-level `filters` of a plot (O9) and the tier-3 container need a form. Each item becomes a task when its recipe change lands.

## 6. Proposed order (a recommendation to Eve; nothing here is decided)

Reason for the order: a rename made before the action is strict would move the silent behaviour to a new name, and a migration made twice rebuilds every stored stage twice (one cache-version bump is the aim).

1. **Now, no recipe change.** Integer type in ingestion and `cast` (Eve decided yes), tests first (me). The checker side and the spec (recipe session).
2. **The step checker** `step_problems` (recipe session) and the table of action names (sections 2 and 3 above are the input). Eve decides the names.
3. **One migration** (recipe session tool, #83; me for the engine side): H1 renames, alias removal, new action names, plain strict `select` and `drop`, shipped recipes and tests adapted first.
4. **Run-time guard** (`ACTION-MUST-ACT-1`) and the `na` parameter on the filters (me), then the two `xfail` marks are removed.
5. **`final_contract` becomes a last `select` step** and is refused by the checker (O27, needs Eve's yes after 3).
6. **Tier-3 container read by the engine** (O9) with the audit build; then spec-level `filters` migrate to it.
7. **Blueprint** after 5, as its own package (section 5).
