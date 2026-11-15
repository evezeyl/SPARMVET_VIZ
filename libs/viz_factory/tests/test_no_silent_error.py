"""A component that cannot act fails, naming the plot, the layer and the fix (VIZ-STANDARD-1, V6).

# @deps
# consumes: libs/viz_factory/src/viz_factory/viz_factory.py (VizFactory.render), libs/viz_factory/src/viz_factory/{guides,positions,themes}/core.py, libs/viz_factory/src/viz_factory/plot_config_resolver.py
# @end_deps

Five paths used to do nothing, silently or with a console line: an `element_*` layer without `target`, a `guide_*`
layer without `mapping`, a `position_*` layer with no layer before it, `annotate` without `geom`, and a mistyped plot
spec key. The two filter paths (unknown column skipped, unknown operator ignored) are not here: they wait for
FILTER-UNIFY-1.
"""
import re

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1, 2, 3, 4], "y": [3, 1, 2, 5], "g": ["a", "b", "a", "b"]})
POINT = {"name": "geom_point"}
# "Plot 'p', layer 2 (guide_legend): what. Fix: how."
FORM = re.compile(r"^Plot 'p', layer (?P<n>\d+) \((?P<name>\w+)\): .+\. Fix: .+\.$", re.S)


def spec(layers, **more):
    return {"target_dataset": "d", "mapping": {"x": "x", "y": "y", "color": "g"}, "layers": layers, **more}


def recipe(layers, **more):
    return {"plots": {"p": spec(layers, **more)}, "plot_defaults": {}}


def refused(layers, **more):
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, recipe(layers, **more), "p")
    return error.value


def assert_form(error, layer_no, name):
    found = FORM.match(str(error))
    assert found, f"not in the one error form: {error}"
    assert (int(found["n"]), found["name"]) == (layer_no, name)
    assert error.tip and error.pipeline_error is not None, "the fix and the structured record travel with the error"
    assert error.pipeline_error.fix == error.tip


# -- 1. element_* without target ---------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["element_text", "element_line", "element_rect", "element_blank"])
def test_an_element_layer_without_target_fails(name):
    error = refused([POINT, {"name": name, "params": {"size": 9} if name == "element_text" else {}}])
    assert_form(error, 2, name)
    assert "target" in str(error)


def test_an_element_text_with_a_target_still_works():
    plot = VizFactory().render(DF, recipe([POINT, {"name": "element_text", "params": {"target": "axis_text_x", "angle": 45}}]), "p")
    plot.draw()


# -- 2. guide_* without mapping ----------------------------------------------------------------------------------

NEEDS_MAPPING_ONLY = ["guide_legend", "guide_colorbar", "guide_colourbar", "guide_none"]
NEEDS_MAPPING_AND_VALUE = {"guide_nrow": "nrow", "guide_ncol": "ncol", "guide_title": "title"}
HAS_DEFAULT = ["guide_label", "guide_direction", "guide_reverse"]


@pytest.mark.parametrize("name", NEEDS_MAPPING_ONLY + list(NEEDS_MAPPING_AND_VALUE) + HAS_DEFAULT)
def test_a_guide_without_mapping_fails(name):
    params = {NEEDS_MAPPING_AND_VALUE[name]: 2} if name in NEEDS_MAPPING_AND_VALUE else {}
    error = refused([POINT, {"name": name, "params": params}])
    assert_form(error, 2, name)
    assert "mapping" in str(error)


@pytest.mark.parametrize("name,missing", list(NEEDS_MAPPING_AND_VALUE.items()))
def test_a_guide_without_its_value_fails(name, missing):
    error = refused([POINT, {"name": name, "params": {"mapping": "color"}}])
    assert_form(error, 2, name)
    assert missing in str(error)


def test_a_guide_with_its_mapping_still_works():
    plot = VizFactory().render(DF, recipe([POINT, {"name": "guide_legend", "params": {"mapping": "color", "nrow": 1}}]), "p")
    plot.draw()


# -- 3. position_* with no layer before it -----------------------------------------------------------------------

POSITIONS = ["position_identity", "position_stack", "position_fill", "position_dodge", "position_dodge2",
             "position_jitter", "position_jitterdodge", "position_nudge"]


@pytest.mark.parametrize("name", POSITIONS)
def test_a_position_with_no_layer_before_it_fails(name):
    error = refused([{"name": name}, POINT])
    assert_form(error, 1, name)
    assert "layer" in str(error).split("Fix:")[0]


@pytest.mark.parametrize("name", POSITIONS)
def test_a_position_after_its_geom_still_works(name):
    geom = {"name": "geom_point" if name in ("position_jitter", "position_jitterdodge", "position_nudge") else "geom_bar"}
    mapping = {"x": "g", "fill": "g"} if geom["name"] == "geom_bar" else {"x": "x", "y": "y", "color": "g"}
    plot = VizFactory().render(DF, {"plots": {"p": {"target_dataset": "d", "mapping": mapping, "layers": [geom, {"name": name}]}}}, "p")
    plot.draw()


# -- 4. annotate without geom ------------------------------------------------------------------------------------

def test_annotate_without_geom_fails():
    error = refused([POINT, {"name": "annotate", "params": {"x": 2, "y": 2, "label": "n"}}])
    assert_form(error, 2, "annotate")
    assert "geom" in str(error)


def test_annotate_with_geom_still_works():
    VizFactory().render(DF, recipe([POINT, {"name": "annotate", "params": {"geom": "text", "x": 2, "y": 2, "label": "n"}}]), "p").draw()


# -- 5. a mistyped plot spec key ----------------------------------------------------------------------------------

def test_a_mistyped_spec_key_fails_and_suggests_the_right_one():
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, recipe([POINT], theem="theme_bw"), "p")
    text = str(error.value)
    assert text.startswith("Plot 'p': "), text
    assert "'theem'" in text and "Fix: write theme" in text
    assert error.value.pipeline_error is not None


def test_an_unknown_spec_key_without_a_close_match_lists_the_keys():
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, recipe([POINT], zzzzzz=1), "p")
    assert "mapping" in str(error.value).split("Fix:")[1]


def test_the_spec_keys_a_plot_may_have_are_still_accepted():
    plot = VizFactory().render(DF, recipe([POINT], theme="theme_light", title="t", labels={"x": "X"}, palette="sparmvet_brand"), "p")
    plot.draw()


def test_an_explicit_meta_block_is_still_accepted():
    VizFactory().render(DF, recipe([POINT], _meta={"family": "Distribution"}), "p").draw()


# -- the layer number is the one the author wrote ---------------------------------------------------------------

def test_the_layer_number_counts_the_layers_of_the_recipe_not_the_defaults():
    error = refused([POINT, POINT, {"name": "element_text", "params": {}}], theme="theme_bw")
    assert_form(error, 3, "element_text")


# -- the example a user copies for these components runs ---------------------------------------------------------

def _example_layers(name):
    import yaml
    from viz_factory.registry import COMPONENT_SCHEMAS
    return yaml.safe_load(COMPONENT_SCHEMAS[name]["yaml_example"])["layers"]


AFFECTED = (["element_text", "element_line", "element_rect", "element_blank", "annotate"]
            + NEEDS_MAPPING_ONLY + list(NEEDS_MAPPING_AND_VALUE) + HAS_DEFAULT + POSITIONS)


# guide_label passes `labels` to plotnine's guide_legend, which has no such argument: it fails whatever the recipe says
# (found while testing V6; the parameter reading is rewritten in branch task/viz-params, so it is left here).
GUIDE_LABEL_BROKEN = pytest.mark.xfail(strict=True, reason="guide_label calls guide_legend(labels=...), which plotnine refuses")


@pytest.mark.parametrize("name", [pytest.param(n, marks=GUIDE_LABEL_BROKEN) if n == "guide_label" else n for n in AFFECTED])
def test_the_yaml_example_of_the_component_renders_and_draws(name):
    layers = _example_layers(name)
    has_geom = any(layer["name"].startswith("geom_") for layer in layers)
    layers = layers if has_geom else [{"name": "geom_point"}] + layers
    only_geom_text = any(layer["name"] == "geom_text" for layer in layers)
    mapping = {"x": "x", "y": "y", "fill": "g", "color": "g"}
    if any(layer["name"] == "geom_bar" for layer in layers):
        mapping = {"x": "g", "fill": "g"}
    if only_geom_text:
        mapping["label"] = "g"
    VizFactory().render(DF, {"plots": {"p": {"target_dataset": "d", "mapping": mapping, "layers": layers}}}, "p").draw()
