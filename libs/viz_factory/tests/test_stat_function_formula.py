"""`stat_function` written as text is BLOCKED FOR NOW (Eve, D-0273, D-0274, D-0275): it is refused, never run.

The text of a recipe is not turned into a function by anything. The refusal comes at the check (see
`libs/utils/tests/test_plot_text_check.py`) and at drawing (here, with the same words). A function handed in by Python
code is not a recipe value and still draws.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_stat_function_formula.py -q
"""
import matplotlib
import pandas as pd
import polars as pl
import pytest
from plotnine import aes, geom_point, ggplot

matplotlib.use("Agg")

from utils.errors import VisualizationError
from utils.plot_text_check import STAT_FUNCTION_TEXT_BLOCKED, STAT_FUNCTION_TEXT_SUGGESTION
from viz_factory.geoms.core import handle_stat_function
from viz_factory.registry import COMPONENT_SCHEMAS, get_component
from viz_factory.viz_factory import VizFactory

TEXTS = ["lambda x: x * 2", "sin", "lambda x: np.sqrt(x) + math.pi", "__import__('os').system('echo hacked')", "open", "dnorm"]


def base():
    return ggplot(pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [2.0, 4.0, 6.0]}), aes("x", "y")) + geom_point()


@pytest.mark.parametrize("fun", TEXTS)
def test_the_component_refuses_any_text_with_the_one_message(fun):
    with pytest.raises(VisualizationError) as error:
        handle_stat_function(base(), {"fun": fun, "xlim": (1, 5)})
    text = str(error.value)
    assert STAT_FUNCTION_TEXT_BLOCKED in text and STAT_FUNCTION_TEXT_SUGGESTION in text
    assert "Fix: Suggestion" not in text


def test_drawing_through_the_factory_names_the_plot_and_the_layer():
    recipe = {"plots": {"curve": {"mapping": {"x": "x", "y": "y"}, "layers": [
        {"name": "geom_point"}, {"name": "stat_function", "params": {"fun": "lambda x: x * 2"}}]}}}
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(pl.DataFrame({"x": [1.0, 2.0], "y": [2.0, 4.0]}), recipe, "curve").draw(show=False)
    text = str(error.value)
    assert text.startswith("Plot 'curve', layer 2 (stat_function): " + STAT_FUNCTION_TEXT_BLOCKED)
    assert STAT_FUNCTION_TEXT_SUGGESTION in text


def test_the_component_found_by_name_is_refused_too():
    with pytest.raises(VisualizationError) as error:
        get_component("stat_function")(base(), {"fun": "sin"})
    assert STAT_FUNCTION_TEXT_BLOCKED in str(error.value)


def test_nothing_evaluates_the_text(monkeypatch):
    """A text that would raise a marker error if run is refused with the plain message, not with the marker."""
    import builtins
    calls = []
    real_eval = builtins.eval
    monkeypatch.setattr(builtins, "eval", lambda *a, **k: (calls.append(a), real_eval(*a, **k))[1])
    with pytest.raises(VisualizationError) as error:
        handle_stat_function(base(), {"fun": "(_ for _ in ()).throw(RuntimeError('MARKER_RAN'))"})
    assert "MARKER_RAN" not in str(error.value) and STAT_FUNCTION_TEXT_BLOCKED in str(error.value)
    assert calls == []


def test_the_old_evaluation_is_gone_from_the_module():
    import viz_factory.geoms.core as core
    assert not hasattr(core, "_function_from_string") and not hasattr(core, "function_string_namespace")


def test_a_callable_given_by_python_code_is_not_a_recipe_value_but_is_kept():
    plot = handle_stat_function(base(), {"fun": abs, "xlim": (1, 5)})
    assert len(plot.layers) == 2


def test_a_stat_function_without_a_function_is_not_blocked_here_plotnine_decides():
    """Without `fun` the component passes the parameters on; plotnine then needs no recipe text and decides itself."""
    plot = handle_stat_function(base(), {"xlim": (1, 5)})
    assert len(plot.layers) == 2


def test_the_registered_help_says_it_is_blocked_for_now():
    schema = COMPONENT_SCHEMAS["stat_function"]
    assert "BLOCKED FOR NOW" in schema["description"] and "line layer" in schema["description"]
    assert "Blocked for now" in schema["yaml_example"]
