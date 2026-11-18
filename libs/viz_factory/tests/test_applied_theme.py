"""`applied_theme(plot)`: the theme as it was really drawn, read from the steps the factory applied (D-0248, D-0258).

The export records, per plot, the component names and their values. A plot with no theme in the recipe is drawn with plotnine's own
default (D-0258): the record says so and names the default as plotnine reports it, it does not invent a name. A theme the recipe
writes at several levels is recorded as it survived: the one that was applied.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_applied_theme.py -q
"""
import polars as pl
import pytest
from plotnine import ggplot

from viz_factory.checked_plot import applied_theme
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": ["a", "b", "a"], "y": [1.0, 2.0, 3.0]})
BAR = {"name": "geom_bar", "params": {}}


def draw(spec_extra=None, plot_defaults=None, override=None):
    recipe = {"plot_engine": "python-plotnine", "plots": {"p": {"mapping": {"x": "x"}, "layers": [BAR], **(spec_extra or {})}}}
    if plot_defaults:
        recipe["plot_defaults"] = plot_defaults
    return VizFactory().render(DF, recipe, "p", aesthetic_override=override)


def components(record):
    return [(c["component"], c["params"], c["from"]) for c in record["components"]]


def test_a_plot_with_no_theme_is_drawn_with_the_default_of_plotnine_and_the_record_says_so_without_inventing_a_name():
    record = applied_theme(draw())
    assert record["plotnine_default"] == {"applies": True, "name": "theme_gray"}   # read from plotnine at run time
    assert [c for c in record["components"] if c["component"].startswith("theme")] == []


def test_a_theme_written_on_the_plot_is_recorded_with_its_values_and_where_it_came_from():
    record = applied_theme(draw({"layers": [BAR, {"name": "theme_bw", "params": {"base_size": 14}}]}))
    assert ("theme_bw", {"base_size": 14}, "the plot entry") in components(record)
    assert record["plotnine_default"]["applies"] is False


def test_a_theme_of_the_recipe_defaults_is_recorded_as_such():
    record = applied_theme(draw(plot_defaults={"theme": "theme_minimal"}))
    assert ("theme_minimal", {}, "plot_defaults of the recipe") in components(record)
    assert record["plotnine_default"]["applies"] is False


def test_when_the_plot_and_the_defaults_both_write_a_complete_theme_only_the_one_that_was_applied_is_recorded():
    record = applied_theme(draw({"layers": [BAR, {"name": "theme_bw", "params": {}}]}, plot_defaults={"theme": "theme_minimal"}))
    names = [name for name, _, _ in components(record) if name.startswith("theme")]
    assert names == ["theme_bw"]


def test_a_partial_theme_alone_leaves_the_default_of_plotnine_in_force_and_is_recorded():
    record = applied_theme(draw({"layers": [BAR, {"name": "theme_custom", "params": {"legend_position": "bottom"}}]}))
    assert record["plotnine_default"]["applies"] is True
    assert ("theme_custom", {"legend_position": "bottom"}, "the plot entry") in components(record)


def test_the_theme_of_an_audit_override_is_recorded_from_the_audit():
    record = applied_theme(draw(override={"theme": "theme_classic"}))
    assert ("theme_classic", {}, "the audit override") in components(record)


def test_the_values_are_plain_so_that_they_can_be_written_to_yaml():
    import yaml
    record = applied_theme(draw({"layers": [BAR, {"name": "theme_bw", "params": {"base_size": 14}}]}))
    assert yaml.safe_load(yaml.safe_dump(record)) == record


def test_a_plot_that_the_factory_did_not_build_has_no_record_to_give():
    assert applied_theme(ggplot()) is None


def test_the_name_of_the_default_is_what_plotnine_reports_not_a_name_written_in_the_library(monkeypatch):
    import plotnine

    class theme_other:
        pass

    monkeypatch.setattr(plotnine, "theme_get", lambda: theme_other())
    assert applied_theme(draw())["plotnine_default"]["name"] == "theme_other"
