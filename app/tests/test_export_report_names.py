"""The name of a plot in the export report (D-0409, D-0484): its `ui_label`, the same text as its tab in HOME, never the figure text.

The report headings, captions, the audit prose and the T3 heading all take the name from `plot_report_name`. The text on the
figure is written only in the `labs` layer and is not read here. Before the names pass the report named a plot by its `ui_title`
(17 of the 17 plots of the demo recipe: a longer text than the tab); `ui_title` is removed and the report shows what the user saw in HOME.

# @deps
# consumes: app/handlers/export_handlers.py (plot_report_name, plot_report_lines, _build_methods_section), app/modules/cache_keys.py (load_data_analysis_recipe)
# @end_deps
"""
from pathlib import Path

import pytest

from app.handlers.export_handlers import _build_methods_section, plot_report_name
from app.handlers.home_theater import plot_tab_label
from app.modules.cache_keys import load_data_analysis_recipe

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ["pipelines/1_test_data_ST22_dummy.yaml", "pipelines/3_test_no_joins.yaml"]


def test_the_name_is_the_ui_label_and_nothing_else():
    assert plot_report_name({"ui_label": "Short"}, "my_plot") == "Short"
    assert plot_report_name({"ui_title": "Long name", "ui_label": "Short", "name": "x", "description": "d"}, "my_plot") == "Short"


def test_no_name_is_made_from_the_id():
    assert plot_report_name({}, "my_plot") == "my_plot"          # a plot the recipe does not have: its id as written
    assert plot_report_name(None, "my_plot") == "my_plot"


def test_a_title_written_in_the_plot_content_is_not_a_report_name():
    # `title` is not a key of a plot entry (D-0253); a stray one must not become the name silently
    assert plot_report_name({"title": "Old way", "ui_label": "Short"}, "p") == "Short"


def test_the_methods_text_and_the_t3_prose_use_the_report_name():
    methods = _build_methods_section(
        all_plots=[("p", {"ui_label": "Short name"})],
        t3_by_plot={"p": [{"node_type": "drop_column", "params": {"column": "c"}, "reason": "r"}]},
        ds_to_plots={}, tiers_exported=["T1"], t3_aesthetic_overrides={"p": {"alpha": 0.5}})
    joined = "\n".join(methods)
    assert "plot: *Short name*" in joined and "plot *Short name*" in joined


def test_the_methods_text_names_a_plot_the_recipe_no_longer_has_by_its_id():
    methods = _build_methods_section(
        all_plots=[], t3_by_plot={"gone_plot": [{"node_type": "drop_column", "params": {"column": "c"}, "reason": "r"}]},
        ds_to_plots={}, tiers_exported=["T1"], t3_aesthetic_overrides=None)
    assert "plot: *gone_plot*" in "\n".join(methods) and "Gone Plot" not in "\n".join(methods)


def _plots_of(recipe_rel: str):
    raw = load_data_analysis_recipe(ROOT / "config" / "data_analysis_recipes" / recipe_rel).config.raw_config
    return {pid: entry for group in raw["analysis_groups"].values() for pid, entry in group["plots"].items()}


@pytest.mark.parametrize("recipe", SHIPPED)
def test_a_shipped_recipe_reports_the_name_that_home_shows(recipe):
    plots = _plots_of(recipe)
    assert plots
    for pid, entry in plots.items():
        assert plot_report_name(entry, pid) == plot_tab_label(pid, entry) == entry["ui_label"], f"{recipe}:{pid}"
        assert "ui_title" not in entry


# ---- the plots an export draws are the plot entries --------------------------------------------------------------------

def test_the_export_draws_the_plot_entries_with_their_content():
    from app.handlers.export_handlers import export_plot_entries
    raw = load_data_analysis_recipe(ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml").config.raw_config
    entries = export_plot_entries(raw)
    assert len(entries) == 17 and len({p for p, _ in entries}) == 17
    for p_id, entry in entries:
        assert "spec" not in entry and entry["target_dataset"] and entry["layers"] and entry["ui_label"], p_id


def test_an_empty_plot_entry_is_not_a_plot_and_an_empty_recipe_has_none():
    from app.handlers.export_handlers import export_plot_entries
    raw = {"analysis_groups": {"g": {"plots": {"a": {"ui_label": "A", "target_dataset": "T"}, "b": {}, "c": None}}}}
    assert [p for p, _ in export_plot_entries(raw)] == ["a"]
    assert export_plot_entries({}) == [] and export_plot_entries({"analysis_groups": {}}) == []


def test_a_plot_written_the_old_way_has_no_content_in_the_export():
    """A `spec` key is not read: the entry has no `target_dataset`, so the check that refuses the recipe is the place that tells it."""
    from app.handlers.export_handlers import export_plot_entries
    raw = {"analysis_groups": {"g": {"plots": {"a": {"label": "A", "spec": {"target_dataset": "T"}}}}}}
    (p_id, entry), = export_plot_entries(raw)
    assert p_id == "a" and entry.get("target_dataset") is None
