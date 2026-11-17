"""Every `stat_function` string that passes the check evaluates and draws: check and drawing agree (D-0232).

The names the check accepts are read from the tables of `utils.formula_check` (`PLOT_FUNCTION_MODULES`,
`PLOT_FUNCTION_NAMES`); the drawing namespace is built from the same tables (`function_string_namespace`). These tests
close the loop on the real thing: each accepted spelling is evaluated in that namespace and called, and a few are drawn
with plotnine; a refused one stops early with a plain message and never reaches the drawing.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_stat_function_names_drawn.py -q
"""
import matplotlib
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

matplotlib.use("Agg")

from utils.errors import VisualizationError
from utils.formula_check import (
    MATH_CONSTANTS,
    MATH_FUNCTIONS,
    PLOT_FUNCTION_MODULES,
    PLOT_FUNCTION_NAMES,
    PYTHON_MATH_FUNCTIONS,
    function_string_problems,
)
from viz_factory.geoms.core import _function_from_string, function_string_namespace, handle_stat_function


def base():
    return ggplot(pd.DataFrame({"x": [0.1, 0.5, 0.9], "y": [1.0, 2.0, 3.0]}), aes("x", "y")) + geom_point()


def accepted_spellings():
    for prefix, module in sorted(PLOT_FUNCTION_MODULES.items()):
        for name in sorted(PLOT_FUNCTION_NAMES[module]):
            yield f"lambda x: {prefix}.{name}(x)"
        for constant in sorted(MATH_CONSTANTS):
            yield f"lambda x: {prefix}.{constant} * x"
    for name in sorted(MATH_FUNCTIONS):
        yield f"lambda x: {name}(x)"


@pytest.mark.parametrize("text", list(accepted_spellings()))
def test_every_accepted_spelling_evaluates_in_the_drawing_namespace(text):
    assert function_string_problems(text) == []
    function = _function_from_string(text)
    assert function(0.5) is not None  # 0.5 is inside the domain of every listed function


def test_the_namespace_has_every_bare_name_and_every_prefix():
    namespace = function_string_namespace()
    assert set(MATH_FUNCTIONS) | set(MATH_CONSTANTS) | set(PLOT_FUNCTION_MODULES) <= set(namespace)
    assert namespace["numpy"] is namespace["np"]
    assert namespace["math"].asin(0.5) > 0


def test_a_candidate_matrix_check_and_drawing_agree_both_ways():
    """For every name of every module (the table and neighbours that exist in a module but are not listed): whatever the
    check accepts must evaluate. (Names the check refuses are free to evaluate or not; the other direction is the point.)"""
    import importlib
    namespace = function_string_namespace()
    disagreements = []
    for prefix, module_name in sorted(PLOT_FUNCTION_MODULES.items()):
        module = importlib.import_module(module_name)
        candidates = set(MATH_FUNCTIONS) | set(PYTHON_MATH_FUNCTIONS) | {"asinh", "acosh", "atanh", "gamma", "erf", "trunc", "load"}
        for name in sorted(candidates):
            text = f"lambda x: {prefix}.{name}(x)"
            accepted = function_string_problems(text) == []
            try:
                value = eval(compile(text, "<t>", "eval"), {"__builtins__": {}, **namespace})(0.5)
                works = value is not None
            except Exception:
                works = False
            if accepted and not works:
                disagreements.append((text, "accepted but fails"))
    assert not disagreements, disagreements


@pytest.mark.parametrize("fun", ["lambda x: math.asin(x)", "lambda x: numpy.arcsin(x)", "lambda x: math.fabs(x - 0.5)",
                                 "lambda x: math.log(x, 10)", "lambda x: np.sign(x - 0.5)"])
def test_the_spellings_that_failed_or_were_new_now_draw(fun):
    plot = handle_stat_function(base(), {"fun": fun, "xlim": (0.1, 0.9), "n": 5})
    plot.draw()


@pytest.mark.parametrize("fun,words", [
    ("lambda x: math.arcsin(x)", ["math.arcsin does not exist", "math has asin, not arcsin", "math.asin, or np.arcsin"]),
    ("lambda x: math.abs(x)", ["math.abs does not exist", "math has fabs, not abs"]),
    ("lambda x: math.sign(x)", ["math.sign does not exist", "math has no sign", "np.sign"]),
    ("lambda x: sin", ["sin is a function and is not called"]),
    ("lambda x: sin(x, x)", ["sin takes 1 number, not 2"]),
])
def test_a_refused_string_stops_before_drawing_with_a_plain_message(fun, words):
    with pytest.raises(VisualizationError) as error:
        handle_stat_function(base(), {"fun": fun})
    text = str(error.value)
    assert all(w in text for w in words), text
    assert "Fix: Suggestion" not in text and "Suggestion:" in text


def test_the_namespace_stops_with_the_name_when_a_table_entry_is_missing_in_the_module(monkeypatch):
    """If someone adds a name to the table that the module does not have, the failure names it, not an AttributeError later."""
    import utils.formula_check as fc
    monkeypatch.setitem(fc.PLOT_FUNCTION_NAMES, "math", frozenset(fc.PYTHON_MATH_FUNCTIONS | {"arcsin"}))
    with pytest.raises(VisualizationError) as error:
        function_string_namespace()
    assert "math has no arcsin" in str(error.value)
