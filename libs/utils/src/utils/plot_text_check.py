"""The texts of a plot layer that something evaluates as Python, and the check that keeps a recipe from running code (PS06).

plotnine evaluates three kinds of text that a recipe can write in a layer:
- the `formula` of a smoother or a quantile line (patsy runs it as Python);
- a facet variable (`facets`, `rows`, `cols`) that is not a column: plotnine evaluates it as an expression in its own
  environment (`facet_wrap(facets="len(open('/x').read())")` ran the call);
- the function string of `stat_function` (already turned into a function by `formula_check.function_string_problems`).
Every other text of a layer was tried (a marker file written from inside the text, evidence
`.claude/design/decisions_2026-11-14/evidence/plot_text_code_execution_2026-11-16.md`) and is not evaluated.

`layer_text_problems` is the one check. The recipe checker calls it without the data (a facet variable must then be
written as a plain column name); the plot factory calls it on every layer with the columns of the data (a facet
variable must then be a column, exactly).

# @deps
# provides: function:layer_text_problems, function:facet_variable_problems, function:facet_variables, function:facet_sides, function:facet_wrap_spec, class:FacetTextError, constant:FACET_PARAMETERS
# consumes: libs/utils/src/utils/formula_check.py, libs/utils/src/utils/fix_text.py (split_fix)
# consumed_by: libs/utils/src/utils/recipe_check.py, libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/src/viz_factory/facets/core.py, libs/utils/tests/test_plot_text_check.py
# doc: .claude/design/recipe_format_spec.md (section 15; check PS06)
# @end_deps
"""
import re
from typing import Any, Iterable, List, Optional, Tuple

from utils.fix_text import split_fix
from utils.formula_check import function_string_problems, smoother_formula_problems

# What a facet variable looks like when the columns are not known: a column name written with letters, digits,
# underscore, space, dot or dash. No bracket, quote or operator: nothing in it can call anything.
_PLAIN_NAME = re.compile(r"^[\w .\-]*$")

FACET_PARAMETERS = ("facets", "rows", "cols")

# (parameter, what happened, suggestion)
TextProblem = Tuple[str, str, str]


def _split(message: str) -> Tuple[str, str]:
    what, _, suggestion = message.partition(". Suggestion: ")
    return what, "Suggestion: " + suggestion.rstrip(".")


def _text_pieces(text: str, known: Optional[set]) -> List[str]:
    """The variables a facet text names: the whole text when it is a column, else its parts around `~` and `+`.

    This is our own reader of a facet formula (`a ~ b`, `~ a + b`). plotnine reads the same text with a pattern that
    stops at the first character that is not a letter, digit or underscore, so `~Collection year` became the column
    `Collection` (found 2026-11-16). The names it returns are exact; they are handed to plotnine as a list.
    """
    if known is not None and text in known:
        return [text]
    return [piece.strip() for side in text.split("~") for piece in side.split("+")]


def _pieces(value: Any, known: Optional[set] = None) -> List[Any]:
    """The variables named by a facet value: a text is read by `_text_pieces`, a list entry is one exact name."""
    if isinstance(value, str):
        return _text_pieces(value, known)
    if value is None:
        return []   # no variable on this side of a grid
    if isinstance(value, (list, tuple)):
        found: List[Any] = []
        for item in value:
            found.extend([item] if isinstance(item, str) else _pieces(item, known))
        return found
    return [value]


def facet_variables(value: Any, columns: Optional[Iterable[str]] = None) -> List[str]:
    """The exact column names a facet value names, in order; `.` and empty parts are no variable."""
    known = None if columns is None else set(columns)
    return [piece for piece in _pieces(value, known) if piece not in ("", ".")]


def facet_sides(text: str, columns: Optional[Iterable[str]] = None) -> Tuple[List[str], List[str]]:
    """(rows, columns) of a `facet_grid` formula text: `a + b ~ c` gives (['a', 'b'], ['c']); no `~` means rows only.

    Raises ValueError when the text holds more than one `~`.
    """
    known = None if columns is None else set(columns)
    if known is not None and text in known:
        return [text], []
    parts = text.split("~")
    if len(parts) > 2:
        raise ValueError("a facet formula has one ~, as in rows ~ columns")
    sides = [[piece.strip() for piece in part.split("+") if piece.strip() not in ("", ".")] for part in parts]
    return sides[0], (sides[1] if len(sides) == 2 else [])


class FacetTextError(ValueError):
    """A facet text that cannot be read; `what` says what happened, `suggestion` starts with `Suggestion:`."""

    def __init__(self, what: str, suggestion: str):
        super().__init__(what)
        self.what = what
        self.suggestion = suggestion


def facet_wrap_spec(spec: dict, columns: Optional[Iterable[str]] = None) -> dict:
    """A copy of the parameters of `facet_wrap` with `facets` as a list of exact column names (never as text).

    plotnine cut a text such as `~Collection year` at the space and faceted by `Collection`. Raises `FacetTextError`
    for a formula with a variable on the left of the `~` (facet_wrap takes `~ a + b`).
    """
    if spec.get("facets") is None:
        return dict(spec)
    text = spec["facets"]
    known = None if columns is None else set(columns)
    if isinstance(text, str) and "~" in text and not (known is not None and text in known):
        if text.partition("~")[0].strip() not in ("", "."):
            raise FacetTextError(f"facet_wrap reads `~ a + b`, with nothing on the left of the ~, and the text is {text!r}",
                                 "Suggestion: write the variables on the right of the ~ (~ a + b), or use facet_grid for rows ~ columns")
    return {**spec, "facets": facet_variables(text, columns)}


def facet_variable_problems(value: Any, columns: Optional[Iterable[str]] = None) -> List[str]:
    """The parts of a facet value that are not allowed: each is the text of a variable that is not a column."""
    known = None if columns is None else set(columns)
    refused = []
    for piece in _pieces(value, known):
        if not isinstance(piece, str):
            refused.append(repr(piece))
        elif piece in ("", "."):
            continue
        elif known is not None:
            if piece not in known:
                refused.append(piece)
        elif not _PLAIN_NAME.match(piece):
            refused.append(piece)
    return refused


def layer_text_problems(component: str, params: Any, columns: Optional[Iterable[str]] = None) -> List[TextProblem]:
    """Every text of a layer that something would evaluate as Python and that the check refuses; empty when none.

    `component` is the plot component name, `params` the layer's parameters, `columns` the columns of the plot's data
    (None when they are not known, as in the recipe checker).
    """
    if not isinstance(params, dict):
        return []
    problems: List[TextProblem] = []
    if "formula" in params:
        for message in smoother_formula_problems(params["formula"]):
            what, suggestion = _split(message)
            problems.append(("formula", f"the formula {params['formula']!r} is refused: {what}" if isinstance(params["formula"], str)
                             else f"the formula is refused: {what}", suggestion))
    if component.startswith("facet_"):
        column_list = None if columns is None else list(columns)
        for key in FACET_PARAMETERS:
            if key not in params:
                continue
            refused = facet_variable_problems(params[key], column_list)
            if refused:
                shown = ", ".join(repr(r) for r in refused)
                what = (f"the facet variable {shown} in '{key}' is not a column of the data" if column_list is not None
                        else f"the facet variable {shown} in '{key}' is not a plain column name")
                suggestion = ("Suggestion: write a column of the data" + (": " + ", ".join(column_list[:12]) + (", ..." if len(column_list) > 12 else "")
                              if column_list is not None else " (letters, digits, underscore, space, dot or dash)")
                              + "; to facet by a computed value, add a recipe step that makes the column first")
                problems.append((key, what, suggestion))
    if component == "stat_function" and isinstance(params.get("fun"), str):
        for message in function_string_problems(params["fun"]):
            what, fix = split_fix(message)
            problems.append(("fun", f"the function string is refused: {what}",
                             fix.rstrip(".") if fix.startswith("Suggestion:") else "Suggestion: " + fix.rstrip(".")))
    return problems
