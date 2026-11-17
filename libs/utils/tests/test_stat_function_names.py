"""The names of a `stat_function` string, per module: the check accepts a name only when the module has it (D-0232).

Before (2026-11-17, found by the review session): `lambda x: math.arcsin(x)` passed the check and failed at drawing
(`module 'math' has no attribute 'arcsin'`: Python's `math` has `asin`), `lambda x: numpy.arcsin(x)` passed and failed with
a NameError (the drawing namespace had `np` and `math` only), and `math.abs`, `math.sign` passed and failed the same way.
A function written as a value (`lambda x: sin`), or called with the wrong number of numbers, passed and failed late too.
Eve (D-0232): "I mean that was an idea for a fix - it might not be the fix... But it need to be fixed".

The drawing side of the same rule (every accepted name really evaluates) is in
`libs/viz_factory/tests/test_stat_function_names_drawn.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_stat_function_names.py -q
"""
import importlib
import math

import numpy as np
import pytest

from utils.formula_check import (
    MATH_CONSTANTS,
    MATH_FUNCTIONS,
    PLOT_FUNCTION_MODULES,
    PLOT_FUNCTION_NAMES,
    PYTHON_MATH_FUNCTIONS,
    function_string_problems,
)
from utils.plot_text_check import layer_text_problems


# ---- the table is true: every entry exists in the real module --------------------------------------------------

@pytest.mark.parametrize("prefix", sorted(PLOT_FUNCTION_MODULES))
def test_every_name_of_the_table_exists_in_the_module_of_its_prefix(prefix):
    module = importlib.import_module(PLOT_FUNCTION_MODULES[prefix])
    names = PLOT_FUNCTION_NAMES[PLOT_FUNCTION_MODULES[prefix]]
    missing = sorted(n for n in list(names) + list(MATH_CONSTANTS) if not hasattr(module, n))
    assert not missing, (prefix, missing)


def test_the_math_names_are_real_functions_of_pythons_math_that_take_a_number():
    for name in PYTHON_MATH_FUNCTIONS:
        assert callable(getattr(math, name)), name
        assert getattr(math, name)(0.5) is not None


def test_the_facts_that_started_this_are_in_the_table_as_they_are():
    """Python's math has asin and fabs; numpy has arcsin and abs; math has no sign. If one of these changes, read this."""
    assert not hasattr(math, "arcsin") and hasattr(math, "asin")
    assert not hasattr(math, "abs") and hasattr(math, "fabs")
    assert not hasattr(math, "sign")
    assert hasattr(np, "arcsin") and hasattr(np, "abs") and hasattr(np, "sign")
    assert not hasattr(np, "asin") or np.asin is np.arcsin  # numpy 2 has both spellings; the table keeps numpy's own


# ---- accepted: every (prefix, name) of the table -----------------------------------------------------------------

def accepted_strings():
    for prefix, module in sorted(PLOT_FUNCTION_MODULES.items()):
        for name in sorted(PLOT_FUNCTION_NAMES[module]):
            yield f"lambda x: {prefix}.{name}(x)"
        for constant in sorted(MATH_CONSTANTS):
            yield f"lambda x: {prefix}.{constant} * x"
    for name in sorted(MATH_FUNCTIONS):
        yield f"lambda x: {name}(x)"
        yield name


@pytest.mark.parametrize("text", list(accepted_strings()))
def test_a_name_of_the_table_is_accepted(text):
    assert function_string_problems(text) == []


def test_numpy_is_a_prefix_like_np():
    assert function_string_problems("lambda x: numpy.arcsin(x)") == []
    assert function_string_problems("lambda x: np.arcsin(x)") == []


def test_math_log_takes_a_base_and_numpy_log_does_not():
    assert function_string_problems("lambda x: math.log(x, 10)") == []
    assert function_string_problems("lambda x: np.log(x, 10)")


# ---- refused: a name the module of that prefix does not have --------------------------------------------------------

@pytest.mark.parametrize("name,equal", [("arcsin", "asin"), ("arccos", "acos"), ("arctan", "atan"), ("abs", "fabs")])
def test_a_numpy_name_on_math_says_what_math_has(name, equal):
    [message] = function_string_problems(f"lambda x: math.{name}(x)")
    assert f"math.{name} does not exist: math has {equal}, not {name}" in message
    assert f"Suggestion: write math.{equal}, or np.{name}" in message


def test_a_name_math_has_no_equal_for_says_so():
    [message] = function_string_problems("lambda x: math.sign(x)")
    assert "math.sign does not exist: math has no sign" in message
    assert "Suggestion: write np.sign" in message


def test_check_and_table_agree_for_every_numpy_name_on_every_prefix():
    for name in sorted(MATH_FUNCTIONS):
        for prefix in sorted(PLOT_FUNCTION_MODULES):
            problems = function_string_problems(f"lambda x: {prefix}.{name}(x)")
            in_module = name in PLOT_FUNCTION_NAMES[PLOT_FUNCTION_MODULES[prefix]]
            assert (problems == []) == in_module, (prefix, name, problems)
            if not in_module:
                assert prefix in problems[0] and name in problems[0], problems


@pytest.mark.parametrize("text", [
    "lambda x: np.asin(x)",       # a spelling numpy 2 has but the table does not list
    "lambda x: np.fabs(x)",
    "lambda x: math.asinh(x)",    # math has it, the table does not list it
    "lambda x: math.copysign(x, 1)",
    "lambda x: numpy.load('/tmp/x.npy')",
    "lambda x: np.random.rand(1)",
    "lambda x: os.sqrt(x)",
    "lambda x: scipy.sqrt(x)",
    "lambda x: np.pi(x)",
    "lambda x: math.pi(x)",
    "lambda x: np.sqrt",
    "lambda x: sin",
    "lambda x: pi(x)",
])
def test_other_names_are_refused_with_a_message_that_names_the_function(text):
    problems = function_string_problems(text)
    assert problems, text
    assert all("Fix:" in p for p in problems)


def test_a_function_that_is_not_called_is_refused():
    """It returned a function and the drawing failed late ('Discrete value supplied to continuous scale')."""
    for text in ("lambda x: sin", "lambda x: np.sin", "lambda x: math.sin", "lambda x: x * np.cos"):
        [message] = function_string_problems(text)
        assert "is a function and is not called" in message and "Suggestion: write" in message, message


@pytest.mark.parametrize("text,count", [
    ("lambda x: sin()", "0"), ("lambda x: sin(x, x)", "2"), ("lambda x: np.exp(x, 2)", "2"),
    ("lambda x: math.sqrt(x, 2)", "2"), ("lambda x: math.log(x, 2, 3)", "3"),
])
def test_a_call_with_the_wrong_number_of_numbers_is_refused(text, count):
    [message] = function_string_problems(text)
    assert f"not {count}" in message and "takes" in message, message


def test_the_message_for_an_unknown_module_lists_the_modules():
    [message] = function_string_problems("lambda x: os.sqrt(x)")
    assert "the module 'os' is not allowed" in message and "math, np, numpy" in message


# ---- what the user reads at the checker --------------------------------------------------------------------------

def test_the_checker_shows_one_suggestion_label_and_the_function_and_module():
    [(key, what, suggestion)] = layer_text_problems("stat_function", {"fun": "lambda x: math.arcsin(x)"})
    assert key == "fun"
    assert "math.arcsin does not exist: math has asin, not arcsin" in what
    assert suggestion == "Suggestion: write math.asin, or np.arcsin"


def test_old_generic_refusals_still_show_a_fix():
    [(_, _, suggestion)] = layer_text_problems("stat_function", {"fun": "lambda x: x ** 1000000"})
    assert suggestion.startswith("Suggestion: ") and "Suggestion: Suggestion" not in suggestion
