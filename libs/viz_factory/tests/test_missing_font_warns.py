"""A font family that is not installed is replaced by another font when the picture is drawn; the author is told (D-0050).

# @deps
# consumes: libs/viz_factory/src/viz_factory/font_check.py (missing_fonts), libs/viz_factory/src/viz_factory/viz_factory.py (VizFactory.render), libs/viz_factory/src/viz_factory/checked_plot.py (plot_warnings)
# @end_deps

The check asks matplotlib's font manager directly (`findfont(..., fallback_to_default=False)`), it does not read a log text.
The plot still draws: the warning is not an error. DejaVu Serif ships inside matplotlib, so it is installed on every machine.
"""
import matplotlib
import polars as pl

matplotlib.use("Agg")

from viz_factory.checked_plot import plot_warnings
from viz_factory.font_check import missing_fonts
from viz_factory.viz_factory import VizFactory, draw_checked

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [3.0, 1.0, 2.0]})
MISSING = "NoSuchFontXyz"


def render(*layers):
    spec = {"target_dataset": "d", "mapping": {"x": "x", "y": "y"}, "layers": [{"name": "geom_point"}, *layers]}
    return VizFactory().render(DF, {"plots": {"p": spec}, "plot_defaults": {}}, "p")


def font_warnings(plot):
    return [w for w in plot_warnings(plot) if "font" in w.problem]


def test_a_missing_base_family_is_a_warning_with_the_font_asked_for_and_the_font_used():
    plot = render({"name": "theme_bw", "params": {"base_family": MISSING}})
    found = font_warnings(plot)
    assert len(found) == 1 and found[0].severity == "warning"
    assert MISSING in found[0].problem and "DejaVu Sans" in found[0].problem and found[0].problem.startswith("Plot 'p': ")
    assert found[0].fix.startswith("Suggestion:")
    draw_checked(plot)   # the plot still draws


def test_a_missing_family_in_an_element_text_of_theme_custom_is_a_warning():
    plot = render({"name": "theme_custom", "params": {"axis_text_x": {"name": "element_text", "params": {"family": MISSING}}}})
    found = font_warnings(plot)
    assert len(found) == 1 and MISSING in found[0].problem and "axis_text_x" in found[0].problem
    draw_checked(plot)


def test_an_installed_font_is_no_warning():
    assert font_warnings(render({"name": "theme_bw", "params": {"base_family": "DejaVu Serif"}})) == []


def test_no_theme_setting_is_no_warning():
    assert font_warnings(render()) == []


def test_the_same_missing_font_in_two_places_is_reported_once_per_place_and_not_for_installed_ones():
    plot = render({"name": "theme_bw", "params": {"base_family": MISSING}},
                  {"name": "theme_custom", "params": {"axis_text_x": {"name": "element_text", "params": {"family": "DejaVu Serif"}}}})
    found = font_warnings(plot)
    assert len(found) == 1 and MISSING in found[0].problem


def test_a_list_of_families_with_one_installed_is_no_warning():
    # matplotlib takes the first family it has, so the list is fine; only a list with none of them is told
    assert missing_fonts(["NoSuchOne", "DejaVu Serif"]) is None
    assert missing_fonts(["NoSuchOne", "NoSuchTwo"]) is not None


def test_a_missing_font_is_found_without_reading_any_log():
    requested, used = missing_fonts(MISSING)
    assert requested == MISSING and used == "DejaVu Sans"
