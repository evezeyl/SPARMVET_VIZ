# id_reconciliation

Headless, Shiny-free Tier 1 domain library for pairwise ID reconciliation.

## Public API

```python
from id_reconciliation import (
    IDReconciliationEngine,
    IDPair,
    MatchResult,
    IdTransformation,
    detect_many_to_many,
    format_match_table,
    apply_recode_step,
    recipe_steps,
)

# PatternSuggestion and pattern primitives live in utils — canonical import:
from utils.id_patterns import PatternSuggestion, detect_patterns, apply_pattern, suggest_regex
```

## Usage

```python
engine = IDReconciliationEngine()
results = engine.reconcile(ref_ids=["ABCD_001", "ABCD_002"], target_ids=["001_ABCD", "ABCD_002"])
df = format_match_table(results)
```

## Two step languages: the library's own, and the recipe's

An `IdTransformation` holds cleaning steps in **this library's own step language**. A step names an action and no
column, because the caller gives the column. `apply_recode_step(df, column, id_transformation)` runs them.

| Step of the library | Parameters | What it does to the column |
|---|---|---|
| `strip_whitespace` | none | removes whitespace at both ends |
| `cast_string` | none | makes the column text |
| `regex_replace` | `pattern`, `replacement` | replaces every match of a regular expression |
| `lowercase` | none | makes the text lower case |
| `mutate` | `expression` | replaces the column by a Polars formula |
| `drop_duplicates` | none | keeps the first row of each ID |
| `null_if` | `value` | makes this value missing |
| `drop_nulls` | none | removes the rows without an ID |

These names are **not** actions of a data analysis recipe. A step of an `IdTransformation` (also the downloaded
`id_transformation.yaml`) cannot be pasted into a recipe: the recipe checker refuses it as an unknown action.

`recipe_steps(id_transformation, column)` is the one place where the steps leave the library for a recipe. It gives
one recipe step (recipe format 1: a registered action with its parameters) per step, on the column the caller names:

```python
transformation = engine.generate_transformation(results, ref_column="Sample ID", target_column="ID")
recipe_steps(transformation, "sample_id")
# [{'action': 'polars_str_replace_all', 'columns': ['sample_id'], 'pattern': '^.{7}', 'value': '', 'literal': False}]
```

| Step of the library | Recipe step |
|---|---|
| `strip_whitespace` | `polars_str_strip_chars` |
| `cast_string` | `polars_cast` with `dtype: String` |
| `regex_replace` | `polars_str_replace_all` (`replacement` is written as `value`, `literal: false`) |
| `lowercase` | `polars_with_columns` with the formula `pl.col('<column>').str.to_lowercase()` |
| `mutate` | `polars_with_columns` with the step's formula |
| `drop_duplicates` | `polars_unique` with `keep: first`, `maintain_order: true` |
| `null_if` | `polars_with_columns` with a `pl.when(...).then(None).otherwise(...)` formula |
| `drop_nulls` | `polars_drop_nulls` |

`recipe_steps` fills nothing in: a step that lacks a parameter, or names an action that is not in the table, is refused
with a `ValueError`. The action names come from `utils.action_names`; this library does not import `transformer`.
The test `app/tests/test_id_cleaning_steps_reach_a_recipe.py` proves, with the real action registry, that every recipe
step passes its action's check and gives the same IDs as `apply_recode_step`.

Known limits of the suggested steps (they wait for a decision; each has a strict `xfail` test in
`libs/id_reconciliation/tests/test_suggested_steps.py`): the delimiter step is always `_` to `-`; a prefix or suffix step empties an ID that
is not longer than the prefix; a step changes the whole column, also the IDs that matched as they were. The fuzzy
matches are kept in `metadata["fuzzy_recode_map"]` and are not steps.

## Dependencies

- `polars >= 1.0`
- `utils` (SPARMVET Tier 1 base)
- `rapidfuzz` (token-set ratio fuzzy matching)

## Rules

- No Shiny imports. No peer domain lib imports. See `rules_test_lab.md §2`.
- All imports resolve via `pip install -e libs/id_reconciliation/`.
