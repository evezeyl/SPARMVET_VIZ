# engine: python-polars (catches Polars errors of a computed table and cuts the query plan from their text)
"""
@deps
provides: function:short_engine_text, function:computed_failure, function:first_failing_step, function:step_failure_error, function:table_failure_error, function:failure_kind, constant:RECIPE_FAULT_TYPES, constant:MACHINE_ERRNOS
consumes: libs/utils/src/utils/errors.py (TransformationError, SPARMVET_Error), libs/utils/src/utils/formula_check.py (FormulaError), libs/utils/src/utils/filter_values.py (FilterValueError), libs/utils/src/utils/plot_text_check.py (FacetTextError), libs/utils/src/utils/signature_params.py (ParameterReadError), libs/utils/src/utils/recipe_graph.py (RecipeGraphError), libs/utils/src/utils/audit_copy.py (AuditCopyError), libs/viz_factory/src/viz_factory/parameters.py (ComponentParameterError), polars
consumed_by: app/modules/orchestrator.py, app/modules/opening_build.py (failure_kind: a fault of the recipe or a failure of the machine), app/tests/test_build_failure_names.py, app/tests/test_opening_failures.py
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

import errno
import re
from typing import Any, Callable, Optional, Sequence

import polars as pl
import yaml

from utils.audit_copy import AuditCopyError
from utils.errors import SPARMVET_Error, TransformationError
from utils.filter_values import FilterValueError
from utils.formula_check import FormulaError
from utils.plot_text_check import FacetTextError
from utils.recipe_graph import RecipeGraphError
from utils.signature_params import ParameterReadError
from viz_factory.parameters import ComponentParameterError

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


# ---------------------------------------------------------------------------------------------------------------------
# Whose fault is a failure: the recipe or its data, or the machine (opening-build fixes, finding 4)
# ---------------------------------------------------------------------------------------------------------------------

RECIPE, MACHINE, UNKNOWN = "recipe", "machine", "unknown"

# PROVISIONAL (no ledger line states the list; the owner's rule is only that the recipe is refused for a fault of the recipe or its data): the error types the
# engine, the checkers and the plot factory raise about a recipe or its data. Written here and read nowhere else (`failure_kind`). A type that is not in this
# list and is not the machine's is UNKNOWN: the opening says it could not finish and refuses nothing.
RECIPE_FAULT_TYPES = (
    SPARMVET_Error,                 # the engine's own errors: ingestion, transformation, visualization (the one form of a plot that cannot be drawn), recipe, load
    pl.exceptions.PolarsError,      # a step Polars cannot run on this data (column, type, value); a failure of the disk written by Polars is the machine's, see below
    FormulaError, FilterValueError, FacetTextError, ParameterReadError, RecipeGraphError, AuditCopyError, ComponentParameterError,   # the checkers' own errors (all ValueError)
    yaml.YAMLError,                 # a recipe file that is not valid text
)

# PROVISIONAL: the operating-system errors that say the machine or the store failed, never the recipe: no space, quota, no right to write or read, read-only
# folder, input/output error, too many open files, no memory. "No such file" is NOT here: a data file the recipe names that is missing is the data's fault
# (the engine says it as an ingestion error); the store folder is made and tested before the opening builds anything (`opening_build.check_store`).
MACHINE_ERRNOS = frozenset({errno.ENOSPC, errno.EDQUOT, errno.EACCES, errno.EPERM, errno.EROFS, errno.EIO, errno.EMFILE, errno.ENFILE, errno.ENOMEM})

_OS_ERROR_TEXT = re.compile(r"\(os error (\d+)\)")   # how Polars (Rust) writes an operating-system error inside its own error text


def _chain(error: BaseException, limit: int = 10):
    """The error and what it was raised from or while handling, nearest first, each once, at most `limit`."""
    seen, queue = [], [error]
    while queue and len(seen) < limit:
        current = queue.pop(0)
        if current is None or any(current is other for other in seen):
            continue
        seen.append(current)
        queue += [current.__cause__, current.__context__]
    return seen


def machine_cause(error: BaseException) -> Optional[BaseException]:
    """The link of the chain that is a failure of the machine (no memory, a disk or rights error), or None. The engine wraps what Polars raised when it wrote a
    table into its own error, so the chain is read and not only the error on top."""
    for link in _chain(error):
        if isinstance(link, MemoryError):
            return link
        if isinstance(link, OSError) and link.errno in MACHINE_ERRNOS:
            return link
        if isinstance(link, pl.exceptions.PolarsError):
            found = _OS_ERROR_TEXT.search(str(link))
            if found and int(found.group(1)) in MACHINE_ERRNOS:
                return link
    return None


def failure_kind(error: BaseException) -> str:
    """MACHINE when the machine or the store failed (no memory, no space, no right), else RECIPE when the recipe or its data is at fault, else UNKNOWN.

    The machine is asked first: a disk that is full while a table is written reaches the app as the engine's own transformation error."""
    if machine_cause(error) is not None:
        return MACHINE
    if isinstance(error, RECIPE_FAULT_TYPES):
        return RECIPE
    return UNKNOWN
