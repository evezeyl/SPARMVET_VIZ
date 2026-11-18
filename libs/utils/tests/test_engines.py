"""The names of the engines are stated in one place (ADR-106 V8): the checker's allowed list, the specification data and
the visualisation library all read `utils.engines`.

# @deps
# consumes: libs/utils/src/utils/engines.py, libs/utils/src/utils/recipe_check.py, libs/utils/src/utils/recipe_spec.yaml
# @end_deps
"""
from importlib import resources

import yaml

from utils import engines
from utils.recipe_check import check_recipe, spec


def test_the_engines_are_the_two_built_ones():
    assert engines.DATA_ENGINE == "python-polars" and engines.PLOT_ENGINE == "python-plotnine"
    assert engines.ENGINES == {"data_engine": (engines.DATA_ENGINE,), "plot_engine": (engines.PLOT_ENGINE,)}


def test_the_specification_data_has_no_second_list_of_engines():
    raw = yaml.safe_load(resources.files("utils").joinpath("recipe_spec.yaml").read_text(encoding="utf-8"))
    assert "engines" not in raw, "the engine names live in utils.engines only"


def test_the_checker_reads_the_same_names():
    assert {k: tuple(v) for k, v in spec()["engines"].items()} == engines.ENGINES


def test_the_checker_refuses_what_the_module_does_not_name():
    recipe = {"id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-ggplot2"}
    found = [p for p in check_recipe(recipe, "build").problems if p.code == "T06"]
    assert found and "python-plotnine" in found[0].fix


def test_the_message_for_a_plot_engine_that_is_not_built_says_what_and_how_to_fix():
    what, fix = engines.engine_problem("plot_engine", "python-ggplot2")
    assert "python-ggplot2" in what and "plot_engine" in what
    assert fix == "write plot_engine: python-plotnine"
    assert engines.engine_problem("plot_engine", engines.PLOT_ENGINE) is None
    assert engines.engine_problem("data_engine", "python-pandas")
    assert engines.engine_problem("plot_engine", None)


def test_plot_engine_slot_entry_value_wins_over_the_recipe():
    entry, recipe = {"plot_engine": "python-other"}, {"plot_engine": engines.PLOT_ENGINE}
    assert engines.plot_engine_slot(entry, recipe) == {"plot_engine": "python-other"}


def test_plot_engine_slot_falls_back_to_the_recipe_then_to_nothing():
    assert engines.plot_engine_slot({"ui_label": "P"}, {"plot_engine": engines.PLOT_ENGINE}) == {"plot_engine": engines.PLOT_ENGINE}
    assert engines.plot_engine_slot({"ui_label": "P"}, {}) == {}
    assert engines.plot_engine_slot(None, None) == {}


def test_plot_engine_slot_keeps_an_empty_value_so_the_library_can_refuse_it():
    # a key written with no value is not "absent": the library must see it and refuse it (no silent fall back to the recipe)
    assert engines.plot_engine_slot({"plot_engine": None}, {"plot_engine": engines.PLOT_ENGINE}) == {"plot_engine": None}
