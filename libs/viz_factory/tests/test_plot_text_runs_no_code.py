"""A text written in a plot of a recipe must not run code (PLOT-TEXT-RUNS-CODE-1; spec section 15, check PS06).

Before: the `formula` of `geom_smooth` / `stat_smooth` and a facet variable were evaluated as Python by plotnine
(patsy, `eval_facet_vars`); a recipe that comes from outside wrote a file with the app's rights (a marker, below).
Every test that offers a text which would write the marker asserts that the plot is refused AND that the marker does
not exist. The marker lives under `tmpAI/` of the repository (git-ignored scratch), never elsewhere.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_plot_text_runs_no_code.py -q
"""
import uuid
from pathlib import Path

import matplotlib
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

from plotnine import aes, geom_point, ggplot
from utils.errors import VisualizationError
from viz_factory.registry import get_component
from viz_factory.viz_factory import VizFactory

MARKER_DIR = Path(__file__).resolve().parents[3] / "tmpAI" / "plot_text_marker"

DF = pl.DataFrame({
    "x": [float(i) + 1 for i in range(30)],
    "y": [float(i) ** 1.3 + (i % 5) + 1 for i in range(30)],
    "g": [["a", "b", "c"][i % 3] for i in range(30)],
    "h": [["u", "v"][i % 2] for i in range(30)],
})


@pytest.fixture
def marker():
    MARKER_DIR.mkdir(parents=True, exist_ok=True)
    path = MARKER_DIR / f"{uuid.uuid4().hex}.txt"
    yield path
    path.unlink(missing_ok=True)


def writes(marker: Path) -> str:
    """A Python expression that would write the marker file when it runs, and that is a number (so it looks like maths)."""
    return f"len(__import__('pathlib').Path({str(marker)!r}).write_text('x')) * 0"


def render_and_draw(layers, mapping=None, data=DF, plot_defaults=None):
    recipe = {"plots": {"p": {"mapping": mapping or {"x": "x", "y": "y"}, "layers": layers}}, "plot_defaults": plot_defaults or {}}
    plot = VizFactory().render(data, recipe, "p")
    return plot.draw(show=False)


def layer(name, **params):
    return {"name": name, "params": params}


POINT = layer("geom_point")


def refused(marker, layers, **kw):
    with pytest.raises(VisualizationError) as error:
        render_and_draw(layers, **kw)
    assert not marker.exists(), "the text ran code"
    return str(error.value)


# ---- the smoother formula -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("component", ["geom_smooth", "stat_smooth"])
@pytest.mark.parametrize("template", [
    "y ~ I({code} + x)",           # inside patsy's I(...)
    "y ~ {code} + x",              # a bare call
    "y ~ x + I({code})",
    "np.log(y) ~ I({code} + x)",   # on the left side
])
def test_a_formula_that_would_write_a_file_is_refused_and_nothing_is_written(marker, component, template):
    text = refused(marker, [POINT, layer(component, method="lm", formula=template.format(code=writes(marker)))])
    assert "Plot 'p', layer 2 (" + component + ")" in text
    assert "Suggestion:" in text and "formula" in text


def test_the_refusal_names_the_plot_the_layer_and_the_offending_part(marker):
    text = refused(marker, [POINT, layer("geom_smooth", method="lm", formula="y ~ I(eval(x))")])
    assert text.startswith("Plot 'p', layer 2 (geom_smooth): the formula 'y ~ I(eval(x))' is refused: the function 'eval' is not allowed")
    assert ". Suggestion: " in text and "Fix:" not in text   # what happened, then the suggestion, with no doubled label


@pytest.mark.parametrize("formula, check", [
    ("y ~ x", None),
    ("y ~ x + I(x**2)", None),
    ("y ~ x - 1", None),
    ("y ~ 0 + x", None),
    ("y ~ I(x**0.5)", None),
    ("y ~ I(1/x)", None),
    ("y ~ bs(x, df=4)", None),
    ("y ~ cr(x, df=4)", None),
    ("y ~ center(x)", None),
    ("y ~ standardize(x)", None),
    ("y ~ np.log(x)", None),
    ("y ~ log(x)", None),
    ("np.log(y) ~ np.log(x)", None),
    ("y ~ I(np.sqrt(x))", None),
    ("y ~ np.exp(x / 30)", None),
    ("y ~ x + I(x * pi)", None),
])
@pytest.mark.parametrize("component", ["geom_smooth", "stat_smooth"])
def test_what_a_scientist_writes_for_a_smoother_still_draws(formula, check, component):
    figure = render_and_draw([POINT, layer(component, method="lm", formula=formula)])
    assert figure is not None


def test_the_smoother_sees_only_the_plotted_variables_not_the_render_locals(marker):
    """Before, the formula was evaluated in the frame of `render`: `df`, `self`, `data_analysis_recipe` were visible."""
    text = refused(marker, [POINT, layer("geom_smooth", method="lm", formula="y ~ df")])
    assert "'df'" in text


def test_a_smoother_with_no_formula_is_unchanged():
    assert render_and_draw([POINT, layer("geom_smooth", method="lm")]) is not None
    assert render_and_draw([POINT, layer("geom_smooth", method="lm", se=False)]) is not None


# ---- facet variables ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("component, key", [
    ("facet_wrap", "facets"), ("facet_grid", "facets"), ("facet_grid", "rows"), ("facet_grid", "cols"),
    ("facet_rows", "facets"), ("facet_cols", "facets"),
])
@pytest.mark.parametrize("shape", ["text", "list", "grid_formula_left", "grid_formula_right", "wrap_formula"])
def test_a_facet_variable_that_would_write_a_file_is_refused_and_nothing_is_written(marker, component, key, shape):
    code = writes(marker)
    value = {"text": code, "list": ["g", code], "grid_formula_left": f"{code} ~ g", "grid_formula_right": f"g ~ {code}",
             "wrap_formula": f"~ {code}"}[shape]
    text = refused(marker, [POINT, layer(component, **{key: value})])
    assert component in text and "facet variable" in text and "Suggestion:" in text


def test_a_facet_from_the_spec_mapping_is_checked_too(marker):
    with pytest.raises(VisualizationError):
        render_and_draw([POINT], mapping={"x": "x", "y": "y", "facet_by": writes(marker)})
    assert not marker.exists()


@pytest.mark.parametrize("component, params", [
    ("facet_wrap", {"facets": "g"}),
    ("facet_wrap", {"facets": "~ g"}),
    ("facet_wrap", {"facets": "~ g + h"}),
    ("facet_wrap", {"facets": ["g", "h"]}),
    ("facet_grid", {"facets": "g ~ h"}),
    ("facet_grid", {"rows": "g", "cols": "h"}),
    ("facet_grid", {"facets": ". ~ h"}),
    ("facet_rows", {"facets": "g"}),
    ("facet_cols", {"facets": "h"}),
])
def test_facets_by_columns_still_draw(component, params):
    assert render_and_draw([POINT, layer(component, **params)]) is not None


def test_a_facet_by_a_column_whose_name_has_odd_characters_still_draws():
    data = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": [1.0, 2.0, 3.0, 4.0], "Sample (n)": ["a", "b", "a", "b"]})
    assert render_and_draw([POINT, layer("facet_wrap", facets="Sample (n)")], data=data) is not None


def test_a_facet_variable_that_is_not_a_column_is_refused_with_the_columns_listed(marker):
    text = refused(marker, [POINT, layer("facet_wrap", facets="continent")])
    assert "'continent'" in text and "not a column" in text and "x, y, g, h" in text


# ---- a component called without the factory, and the registry ----------------------------------------------------

@pytest.mark.parametrize("name, params", [
    ("geom_smooth", {"method": "lm", "formula": "y ~ I(__import__('os').getcwd())"}),
    ("stat_smooth", {"method": "lm", "formula": "y ~ I(__import__('os').getcwd())"}),
    ("facet_wrap", {"facets": "__import__('os').getcwd()"}),
])
def test_the_registered_component_refuses_the_text_when_it_is_called_directly(name, params):
    base = ggplot(pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [2.0, 4.0, 6.0]}), aes("x", "y")) + geom_point()
    with pytest.raises(VisualizationError) as error:
        get_component(name)(base, dict(params))
    assert "Suggestion:" in str(error.value)


# ---- the other sites that were tried and found closed: they stay closed ------------------------------------------

@pytest.mark.parametrize("layers, mapping", [
    ([POINT], {"x": "CODE", "y": "y"}),                                    # a mapping text must be a column
    ([POINT], {"x": "x", "y": "y", "fill": "CODE"}),
    ([layer("geom_point", mapping={"x": "CODE", "y": "y"})], None),        # a mapping given to a layer
    ([POINT, layer("stat_function", fun="CODE")], None),
    ([POINT, layer("stat_summary", fun_data="CODE")], None),
    ([POINT, layer("scale_x_continuous", trans="CODE")], None),
    ([POINT, layer("scale_x_continuous", labels="CODE")], None),
    ([POINT, layer("scale_x_continuous", breaks="CODE")], None),
    ([POINT, layer("facet_wrap", facets="g", labeller="CODE")], None),
    ([POINT, layer("geom_smooth", method="CODE")], None),
    ([layer("geom_point", stat="CODE")], None),
    ([layer("geom_point", position="CODE")], None),
    ([layer("geom_point", data="CODE")], None),
    ([POINT, layer("labs", title="CODE")], None),
])
def test_the_other_texts_of_a_plot_do_not_run_code(marker, layers, mapping):
    code = writes(marker)

    def substitute(value):
        if isinstance(value, str):
            return value.replace("CODE", code)
        if isinstance(value, dict):
            return {k: substitute(v) for k, v in value.items()}
        return value

    layers = [{"name": entry["name"], "params": substitute(entry.get("params", {}))} for entry in layers]
    try:
        render_and_draw(layers, mapping=substitute(mapping) if mapping else None)
    except Exception:
        pass   # an error is fine: refused, or not understood
    assert not marker.exists()


def test_the_plot_defaults_and_the_overrides_do_not_run_code(marker):
    code = writes(marker)
    for plot_defaults in ({"palette": code}, {"theme": code}, {"default_font_family": code}, {"legend_position": code}):
        try:
            render_and_draw([POINT], plot_defaults=plot_defaults)
        except Exception:
            pass
    recipe = {"plots": {"p": {"mapping": {"x": "x", "y": "y"}, "layers": [POINT]}}, "plot_defaults": {}}
    for override in ({"fill_palette": code}, {"color": code}, {"theme": code}, {"shape": code}):
        try:
            VizFactory().render(DF, recipe, "p", aesthetic_override=override).draw(show=False)
        except Exception:
            pass
    assert not marker.exists()
