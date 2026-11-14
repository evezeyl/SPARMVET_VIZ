"""The steps of an IdTransformation, written as steps of a data analysis recipe (recipe format 1).

This library has its own small step language, run by `apply_recode_step`: `lowercase`, `regex_replace`,
`strip_whitespace`, ... A step of that language names no column, because the caller gives the column. Those names are
not registered actions, so such a step cannot be written into a data analysis recipe as it is.

`recipe_steps` is the one place where a step leaves this library for a recipe. Each step becomes one registered action
with exactly that action's parameters, on the column the caller names. The action names come from
`utils.action_names`, because this library may not import `transformer`. That the result passes each action's own
check and gives the same IDs as `apply_recode_step` is tested in
`app/tests/test_id_cleaning_steps_reach_a_recipe.py`, where the action registry is available.

Nothing is filled in: a step without a parameter it needs is refused, where `apply_recode_step` would use an empty
text. An unknown action is refused, where `apply_recode_step` skips it.

# @deps
# provides: recipe_steps
# consumes: libs/utils/src/utils/action_names.py,
#           libs/id_reconciliation/src/id_reconciliation/data_structures.py
# mirrors: libs/id_reconciliation/src/id_reconciliation/core.py (apply_recode_step: same actions, same result)
# consumed_by: libs/id_reconciliation/src/id_reconciliation/__init__.py, app/modules/test_lab_studio.py
# doc: .claude/design/recipe_format_spec.md (7.5, 7.5.1)
# @end_deps
"""
from __future__ import annotations

import math

from utils import action_names

from .data_structures import IdTransformation


def _need(step: dict, name: str):
    """The value of a parameter the step must carry."""
    if step.get(name) is None:
        raise ValueError(f"the ID cleaning step {step['action']} needs {name}: write {name} in the step")
    return step[name]


def _strip_whitespace(step: dict, column: str) -> dict:
    # No `characters`: Polars then strips whitespace, which is what apply_recode_step does.
    return {"action": action_names.STR_STRIP_CHARS, "columns": [column]}


def _cast_string(step: dict, column: str) -> dict:
    return {"action": action_names.CAST, "columns": [column], "dtype": "String"}


def _regex_replace(step: dict, column: str) -> dict:
    # `literal: False` is the Polars default; it is written so that a reader sees the pattern is a regular expression.
    return {"action": action_names.STR_REPLACE_ALL, "columns": [column], "pattern": _need(step, "pattern"),
            "value": _need(step, "replacement"), "literal": False}


def _lowercase(step: dict, column: str) -> dict:
    # There is no lower case action: a formula does it (spec 7.5.1, `polars_with_columns`).
    return {"action": action_names.WITH_COLUMNS, "named_exprs": {column: f"pl.col({column!r}).str.to_lowercase()"}}


def _mutate(step: dict, column: str) -> dict:
    return {"action": action_names.WITH_COLUMNS, "named_exprs": {column: _need(step, "expression")}}


def _drop_duplicates(step: dict, column: str) -> dict:
    # apply_recode_step keeps the first row of each ID and promises no row order; the recipe step keeps the order
    # of the file as well, so that the same file always gives the same table (ADR-090).
    return {"action": action_names.UNIQUE, "subset": [column], "keep": "first", "maintain_order": True}


def _null_if(step: dict, column: str) -> dict:
    value = _need(step, "value")
    writable = isinstance(value, (str, bool, int)) or (isinstance(value, float) and math.isfinite(value))
    if not writable:
        raise ValueError(f"the ID cleaning step null_if has the value {value!r}, which cannot be written in a formula: "
                         "write a text or a number")
    formula = f"pl.when(pl.col({column!r}) == {value!r}).then(None).otherwise(pl.col({column!r}))"
    return {"action": action_names.WITH_COLUMNS, "named_exprs": {column: formula}}


def _drop_nulls(step: dict, column: str) -> dict:
    return {"action": action_names.DROP_NULLS, "subset": [column]}


# One entry per action of apply_recode_step (core.py). A new action there needs its entry here and its example in
# the tests; a step that names anything else is refused.
_TRANSLATORS = {
    "strip_whitespace": _strip_whitespace,
    "cast_string": _cast_string,
    "regex_replace": _regex_replace,
    "lowercase": _lowercase,
    "mutate": _mutate,
    "drop_duplicates": _drop_duplicates,
    "null_if": _null_if,
    "drop_nulls": _drop_nulls,
}


def recipe_steps(id_transformation: IdTransformation, column: str) -> list[dict]:
    """The cleaning steps of an ID transformation as steps for a `tier1` list of a data analysis recipe.

    `column` is the name the recipe gives the ID column (the field slug, not always the header of the file). One step
    of the transformation gives one recipe step, in the same order. Raises ValueError for a step that names no known
    action or lacks a parameter: nothing is written for a transformation that cannot be written whole.
    """
    if not isinstance(column, str) or not column:
        raise ValueError(f"the column that the ID cleaning steps act on must be a name, got {column!r}")
    out = []
    for step in id_transformation.steps:
        action = step.get("action")
        if action is None:
            raise ValueError(f"an ID cleaning step has no action: {step!r}")
        if action not in _TRANSLATORS:
            raise ValueError(f"{action!r} is not an ID cleaning action. The actions are: "
                             + ", ".join(sorted(_TRANSLATORS)))
        out.append(_TRANSLATORS[action](step, column))
    return out
