"""
@deps
provides: function:short_engine_text, function:computed_failure, function:first_failing_step, function:step_failure_error, function:table_failure_error
consumes: libs/utils/src/utils/errors.py (TransformationError, SPARMVET_Error), polars
consumed_by: app/modules/orchestrator.py, app/tests/test_build_failure_names.py
doc: .claude/rules/rules_verification_testing.md, .claude/knowledge/decision_ledger.md (D-0176: a step that names a column that does not exist gives a plain message naming the step, the column and a fix)
@end_deps

A build that failed, said in plain words: which table, which tier, which step (opening-build, D-0326, D-0327).

Polars raises its own error when a stored table is computed (a column that is not there, a value that does not fit a cast). That
error names the column and the values but neither the table nor the step, and it carries the plan of the whole query. The app knows
the table, the tier and the steps; so after such a failure it runs the steps again, a prefix at a time, to find the first step that
fails, and says it. This runs only after a failure: a build that works is not run twice.

No Shiny. Pure functions; the orchestrator gives them the way to build a prefix of the steps.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Sequence

import polars as pl

from utils.errors import SPARMVET_Error, TransformationError

# What Polars appends after the sentence that names the problem: the plan of the query. It is long and says nothing a recipe maker can read.
_PLAN_MARKERS = ("Resolved plan until failure", "Error originated just after this operation", "This error occurred with the following context")


def short_engine_text(error: BaseException, limit: int = 400) -> str:
    """The engine's own sentence without its plan, one line, at most `limit` characters."""
    text = str(error)
    for marker in _PLAN_MARKERS:
        at = text.find(marker)
        if at >= 0:
            text = text[:at]
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + " ..."


def computed_failure(lf: pl.LazyFrame) -> Optional[BaseException]:
    """The error this plan gives when it is computed in full, or None. The names are checked first (cheap), then the rows."""
    try:
        lf.collect_schema()
        lf.collect()
    except (pl.exceptions.PolarsError, SPARMVET_Error) as exc:
        return exc
    return None


def first_failing_step(build_prefix: Callable[[int], pl.LazyFrame], count: int) -> Optional[tuple[int, BaseException]]:
    """(the number of the first step whose prefix fails when computed, its error), or None when no prefix fails.

    `build_prefix(k)` is the table after the first k steps (1 <= k <= count). A prefix that fails stays failing for every longer prefix,
    so the first failing one is found by halving: a few runs, not one per step. A step that cannot be built at all (the error is
    raised by `build_prefix` itself) counts as failing.
    """
    def attempt(k: int) -> Optional[BaseException]:
        try:
            return computed_failure(build_prefix(k))
        except (pl.exceptions.PolarsError, SPARMVET_Error) as exc:
            return exc

    if count < 1 or attempt(count) is None:
        return None
    low, high = 1, count
    while low < high:
        middle = (low + high) // 2
        found = attempt(middle)
        if found is None:
            low = middle + 1
        else:
            high = middle
    return low, attempt(low)


def step_failure_error(where: str, steps: Sequence[Any], number: int, error: BaseException, tip: str) -> TransformationError:
    """The plain error for step `number` (1-based) of `steps`: `where` ("The tier 2 of the table 'C'"), the step, the engine's sentence, a fix."""
    step = steps[number - 1] if 0 < number <= len(steps) else None
    action = step.get("action") if isinstance(step, dict) else None
    named = f"step {number} ('{action}')" if action else f"step {number}"
    why = short_engine_text(error)
    extra = getattr(error, "tip", None)
    return TransformationError(f"{where} cannot be built: {named} failed: {why}" + (f" ({extra})" if extra else ""), tip=tip)


def table_failure_error(where: str, error: BaseException, tip: str) -> TransformationError:
    """The plain error when no single step could be named (the failure shows only with the whole table): `where` and the engine's sentence."""
    return TransformationError(f"{where} cannot be built: {short_engine_text(error)}", tip=tip)
