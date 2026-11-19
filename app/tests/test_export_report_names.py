"""The name of a plot in the export report (D-0253): `ui_title`, else `ui_label`, never the figure text.

The report headings, captions, the audit prose and the T3 heading all take the name from `plot_report_name`. The text on the
figure is written only in the `labs` layer and is not read here. The recipes the app ships keep the report names they had before
the change: a plot that had a `title:` reports the same text (it is now `ui_title`), a plot that had none reports its `ui_label`
(before it reported its id in title case).

# @deps
# consumes: app/handlers/export_handlers.py (plot_report_name, plot_report_lines, _build_methods_section), app/modules/cache_keys.py (load_data_analysis_recipe), app/tests/data/report_names_before_engine_keys.yaml
# @end_deps
"""
from pathlib import Path

import pytest
import yaml

from app.handlers.export_handlers import _build_methods_section, plot_report_name
from app.modules.cache_keys import load_data_analysis_recipe

ROOT = Path(__file__).resolve().parents[2]
BEFORE = yaml.safe_load((Path(__file__).parent / "data" / "report_names_before_engine_keys.yaml").read_text(encoding="utf-8"))["plots"]


def test_the_name_is_ui_title_then_ui_label_then_the_id_in_title_case():
    assert plot_report_name({"ui_title": "Long name", "ui_label": "Short"}, "my_plot") == "Long name"
    assert plot_report_name({"ui_label": "Short"}, "my_plot") == "Short"
    assert plot_report_name({"ui_title": "", "ui_label": "Short"}, "my_plot") == "Short"
    assert plot_report_name({}, "my_plot") == "My Plot"
    assert plot_report_name(None, "my_plot") == "My Plot"


def test_a_title_written_in_the_plot_content_is_not_a_report_name_any_more():
    # `title` is not a key of a plot entry (D-0253); a stray one must not become the name silently
    assert plot_report_name({"title": "Old way", "ui_label": "Short"}, "p") == "Short"


def test_the_methods_text_and_the_t3_prose_use_the_report_name():
    methods = _build_methods_section(
        all_plots=[("p", {"ui_label": "Short", "ui_title": "The long name of the plot"})],
        t3_by_plot={"p": [{"node_type": "drop_column", "params": {"column": "c"}, "reason": "r"}]},
        ds_to_plots={}, tiers_exported=["T1"], t3_aesthetic_overrides={"p": {"alpha": 0.5}})
    joined = "\n".join(methods)
    assert "plot: *The long name of the plot*" in joined and "plot *The long name of the plot*" in joined
    assert "Short" not in joined


def _plots_of(recipe_rel: str):
    raw = load_data_analysis_recipe(ROOT / "config" / "data_analysis_recipes" / recipe_rel).config.raw_config
    return {pid: entry for group in raw["analysis_groups"].values() for pid, entry in group["plots"].items()}


@pytest.mark.parametrize("recipe", sorted({r["recipe"] for r in BEFORE}))
def test_a_shipped_recipe_reports_the_same_names_as_before(recipe):
    plots = _plots_of(recipe)
    expected = {r["plot"]: r for r in BEFORE if r["recipe"] == recipe}
    assert set(plots) == set(expected), "the plots of the recipe changed: the pin must be remade on purpose"
    for pid, was in expected.items():
        entry = plots[pid]
        name = plot_report_name(entry, pid)
        if was["old_title"] is not None:
            assert name == was["old_title"], f"{recipe}:{pid} reported {was['old_title']!r} before"
            assert entry.get("ui_title") == was["old_title"] or entry.get("ui_label") == was["old_title"]
        else:
            assert name == entry["ui_label"], f"{recipe}:{pid} had no title: it reports its ui_label"


def test_the_demo_recipe_has_the_same_report_names_for_all_its_titled_plots():
    titled = [r for r in BEFORE if r["recipe"] == "pipelines/1_test_data_ST22_dummy.yaml"]
    assert len(titled) == 17 and all(r["old_title"] for r in titled)
    plots = _plots_of("pipelines/1_test_data_ST22_dummy.yaml")
    assert {pid: plot_report_name(e, pid) for pid, e in plots.items()} == {r["plot"]: r["old_title"] for r in titled}


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
