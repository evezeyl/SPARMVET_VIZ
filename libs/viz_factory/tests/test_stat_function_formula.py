"""`stat_function` takes a function string from the recipe: it is checked, never run as Python (spec section 15).

Before, `eval(fun)` ran anything, and an unknown name printed a warning and left the layer out silently.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_stat_function_formula.py -q
"""
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

from utils.errors import VisualizationError
from viz_factory.geoms.core import handle_stat_function


def base():
    return ggplot(pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [2.0, 4.0, 6.0]}), aes("x", "y")) + geom_point()


def test_a_lambda_over_numbers_adds_the_layer():
    plot = handle_stat_function(base(), {"fun": "lambda x: x * 2", "xlim": (1, 5)})
    assert len(plot.layers) == 2


def test_a_math_function_name_adds_the_layer():
    plot = handle_stat_function(base(), {"fun": "sin", "xlim": (0, 3)})
    assert len(plot.layers) == 2


def test_a_math_lambda_with_numpy_names_runs():
    plot = handle_stat_function(base(), {"fun": "lambda x: np.sqrt(x) + math.pi", "xlim": (1, 5)})
    assert len(plot.layers) == 2


@pytest.mark.parametrize("fun", [
    "__import__('os').system('echo hacked')",
    "lambda x: __import__('os')",
    "lambda x: x.__class__",
    "open",
    "lambda x: np.load('/etc/passwd')",
    "dnorm",
])
def test_anything_else_is_refused_with_an_error_not_a_warning(fun):
    with pytest.raises(VisualizationError) as error:
        handle_stat_function(base(), {"fun": fun})
    assert "Fix:" in str(error.value)


def test_a_callable_given_by_python_code_is_not_a_recipe_value_but_is_kept():
    """The component can still be called from Python with a real function (the plot library's own use)."""
    plot = handle_stat_function(base(), {"fun": abs, "xlim": (1, 5)})
    assert len(plot.layers) == 2
