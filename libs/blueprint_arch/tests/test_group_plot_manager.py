"""test_group_plot_manager.py — unit tests for group_plot_manager CRUD functions."""

from pathlib import Path

import pytest
import yaml

from blueprint_arch.group_plot_manager import (
    _IncludeTag,
    assign_plot,
    create_group,
    create_plot,
    delete_group,
    delete_plot,
    list_groups_plots,
    plot_ui_label,
)

# ── Fixtures ──────────────────────────────────────────────────────────────

_MINIMAL = """\
data_schemas:
  sample:
    source:
      path: data.tsv
analysis_groups:
  GroupA:
    ui_label: "Group A"
    plots:
      plot_one: !include test_data_analysis_recipe/plots/plot_one.yaml
      plot_inline:
        ui_label: "Inline plot"
        target_dataset: sample
        mapping: {x: a}
        layers: [{name: geom_bar}]
"""


@pytest.fixture
def tmp_data_analysis_recipe(tmp_path):
    m = tmp_path / "test_data_analysis_recipe.yaml"
    m.write_text(_MINIMAL, encoding="utf-8")
    spec_dir = tmp_path / "test_data_analysis_recipe" / "plots"
    spec_dir.mkdir(parents=True)
    (spec_dir / "plot_one.yaml").write_text(
        "ui_label: Plot One\ntarget_dataset: ''\nmapping: {}\nlayers: []\n"
    )
    return str(m)


# ── list_groups_plots ─────────────────────────────────────────────────────

class TestListGroupsPlots:
    def test_returns_groups(self, tmp_data_analysis_recipe):
        groups = list_groups_plots(tmp_data_analysis_recipe)
        assert "GroupA" in groups

    def test_a_plot_in_its_own_file_is_an_include_tag_and_an_inline_plot_is_a_dict(self, tmp_data_analysis_recipe):
        plots = list_groups_plots(tmp_data_analysis_recipe)["GroupA"]["plots"]
        assert isinstance(plots["plot_one"], _IncludeTag)
        assert "plot_one.yaml" in plots["plot_one"].path
        assert isinstance(plots["plot_inline"], dict)


class TestPlotUiLabel:
    def test_reads_the_name_of_an_inline_plot(self, tmp_data_analysis_recipe):
        plots = list_groups_plots(tmp_data_analysis_recipe)["GroupA"]["plots"]
        assert plot_ui_label(tmp_data_analysis_recipe, plots["plot_inline"], "plot_inline") == "Inline plot"

    def test_reads_the_name_from_the_file_of_the_plot(self, tmp_data_analysis_recipe):
        plots = list_groups_plots(tmp_data_analysis_recipe)["GroupA"]["plots"]
        assert plot_ui_label(tmp_data_analysis_recipe, plots["plot_one"], "plot_one") == "Plot One"

    def test_the_id_when_the_file_is_missing_or_has_no_name(self, tmp_data_analysis_recipe):
        plots = list_groups_plots(tmp_data_analysis_recipe)["GroupA"]["plots"]
        plot_file = Path(tmp_data_analysis_recipe).parent / "test_data_analysis_recipe" / "plots" / "plot_one.yaml"
        plot_file.write_text("target_dataset: sample\n", encoding="utf-8")
        assert plot_ui_label(tmp_data_analysis_recipe, plots["plot_one"], "plot_one") == "plot_one"
        plot_file.unlink()
        assert plot_ui_label(tmp_data_analysis_recipe, plots["plot_one"], "plot_one") == "plot_one"
        assert plot_ui_label(tmp_data_analysis_recipe, None, "plot_one") == "plot_one"


# ── create_group ──────────────────────────────────────────────────────────

class TestCreateGroup:
    def test_creates_group(self, tmp_data_analysis_recipe):
        ok, _ = create_group(tmp_data_analysis_recipe, "NewGroup", "New Group Label")
        assert ok
        groups = list_groups_plots(tmp_data_analysis_recipe)
        assert "NewGroup" in groups
        assert groups["NewGroup"]["ui_label"] == "New Group Label"
        assert "label" not in groups["NewGroup"]

    def test_label_defaults_to_id(self, tmp_data_analysis_recipe):
        ok, _ = create_group(tmp_data_analysis_recipe, "EmptyLabel", "")
        assert ok
        assert list_groups_plots(tmp_data_analysis_recipe)["EmptyLabel"]["ui_label"] == "EmptyLabel"

    def test_rejects_invalid_id(self, tmp_data_analysis_recipe):
        ok, msg = create_group(tmp_data_analysis_recipe, "has space", "label")
        assert not ok
        assert "snake_case" in msg

    def test_rejects_duplicate(self, tmp_data_analysis_recipe):
        ok, _ = create_group(tmp_data_analysis_recipe, "GroupA", "label")
        assert not ok


# ── delete_group ──────────────────────────────────────────────────────────

class TestDeleteGroup:
    def test_blocks_non_empty(self, tmp_data_analysis_recipe):
        ok, msg = delete_group(tmp_data_analysis_recipe, "GroupA")
        assert not ok
        assert "2 plot" in msg

    def test_deletes_empty_group(self, tmp_data_analysis_recipe):
        create_group(tmp_data_analysis_recipe, "Empty", "Empty")
        ok, _ = delete_group(tmp_data_analysis_recipe, "Empty")
        assert ok
        assert "Empty" not in list_groups_plots(tmp_data_analysis_recipe)

    def test_rejects_missing_group(self, tmp_data_analysis_recipe):
        ok, _ = delete_group(tmp_data_analysis_recipe, "NoSuch")
        assert not ok


# ── create_plot ───────────────────────────────────────────────────────────

class TestCreatePlot:
    def test_creates_plot_entry(self, tmp_data_analysis_recipe):
        ok, _ = create_plot(tmp_data_analysis_recipe, "GroupA", "plot_two", "Plot Two")
        assert ok
        groups = list_groups_plots(tmp_data_analysis_recipe)
        assert "plot_two" in groups["GroupA"]["plots"]

    def test_creates_the_file_of_the_plot_that_holds_the_whole_entry(self, tmp_data_analysis_recipe):
        create_plot(tmp_data_analysis_recipe, "GroupA", "plot_two", "Plot Two")
        plot_file = (Path(tmp_data_analysis_recipe).parent / "test_data_analysis_recipe" / "plots"
                     / "plot_two.yaml")
        assert plot_file.exists()
        content = yaml.safe_load(plot_file.read_text())
        assert content == {"ui_label": "Plot Two", "target_dataset": "", "mapping": {}, "layers": []}
        assert not {"spec", "label", "title"} & set(content)

    def test_the_label_defaults_to_the_id(self, tmp_data_analysis_recipe):
        create_plot(tmp_data_analysis_recipe, "GroupA", "plot_two", "  ")
        plots = list_groups_plots(tmp_data_analysis_recipe)["GroupA"]["plots"]
        assert plot_ui_label(tmp_data_analysis_recipe, plots["plot_two"], "plot_two") == "plot_two"

    def test_include_tag_written_as_the_entry_itself(self, tmp_data_analysis_recipe):
        create_plot(tmp_data_analysis_recipe, "GroupA", "plot_two", "Plot Two")
        groups = list_groups_plots(tmp_data_analysis_recipe)
        entry = groups["GroupA"]["plots"]["plot_two"]
        assert isinstance(entry, _IncludeTag)
        assert "plot_two.yaml" in entry.path
        assert "plot_two: !include" in Path(tmp_data_analysis_recipe).read_text()

    def test_round_trip_preserves_existing_include(self, tmp_data_analysis_recipe):
        create_plot(tmp_data_analysis_recipe, "GroupA", "plot_two", "Plot Two")
        groups = list_groups_plots(tmp_data_analysis_recipe)
        assert isinstance(groups["GroupA"]["plots"]["plot_one"], _IncludeTag)

    def test_rejects_duplicate_plot(self, tmp_data_analysis_recipe):
        ok, _ = create_plot(tmp_data_analysis_recipe, "GroupA", "plot_one", "dup")
        assert not ok

    def test_rejects_missing_group(self, tmp_data_analysis_recipe):
        ok, _ = create_plot(tmp_data_analysis_recipe, "NoGroup", "p", "label")
        assert not ok

    def test_rejects_invalid_plot_id(self, tmp_data_analysis_recipe):
        ok, msg = create_plot(tmp_data_analysis_recipe, "GroupA", "bad id!", "label")
        assert not ok
        assert "snake_case" in msg

    def test_does_not_overwrite_existing_spec_file(self, tmp_data_analysis_recipe):
        spec_file = (Path(tmp_data_analysis_recipe).parent / "test_data_analysis_recipe" / "plots"
                     / "plot_one.yaml")
        original = spec_file.read_text()
        # plot_one already registered — create_plot returns an error before touching disk
        ok, _ = create_plot(tmp_data_analysis_recipe, "GroupA", "plot_one", "dup")
        assert not ok
        assert spec_file.read_text() == original


# ── delete_plot ───────────────────────────────────────────────────────────

class TestDeletePlot:
    def test_removes_plot(self, tmp_data_analysis_recipe):
        ok, _ = delete_plot(tmp_data_analysis_recipe, "GroupA", "plot_one")
        assert ok
        assert "plot_one" not in list_groups_plots(tmp_data_analysis_recipe)["GroupA"]["plots"]

    def test_rejects_missing_plot(self, tmp_data_analysis_recipe):
        ok, _ = delete_plot(tmp_data_analysis_recipe, "GroupA", "no_such_plot")
        assert not ok

    def test_rejects_missing_group(self, tmp_data_analysis_recipe):
        ok, _ = delete_plot(tmp_data_analysis_recipe, "NoGroup", "plot_one")
        assert not ok


# ── assign_plot ───────────────────────────────────────────────────────────

class TestAssignPlot:
    def test_moves_plot(self, tmp_data_analysis_recipe):
        create_group(tmp_data_analysis_recipe, "GroupB", "Group B")
        ok, _ = assign_plot(tmp_data_analysis_recipe, "plot_one", "GroupA", "GroupB")
        assert ok
        groups = list_groups_plots(tmp_data_analysis_recipe)
        assert "plot_one" not in groups["GroupA"]["plots"]
        assert "plot_one" in groups["GroupB"]["plots"]

    def test_preserves_include_tag_on_move(self, tmp_data_analysis_recipe):
        create_group(tmp_data_analysis_recipe, "GroupB", "Group B")
        assign_plot(tmp_data_analysis_recipe, "plot_one", "GroupA", "GroupB")
        groups = list_groups_plots(tmp_data_analysis_recipe)
        assert isinstance(groups["GroupB"]["plots"]["plot_one"], _IncludeTag)

    def test_rejects_same_group(self, tmp_data_analysis_recipe):
        ok, _ = assign_plot(tmp_data_analysis_recipe, "plot_one", "GroupA", "GroupA")
        assert not ok

    def test_rejects_missing_plot(self, tmp_data_analysis_recipe):
        create_group(tmp_data_analysis_recipe, "GroupB", "Group B")
        ok, _ = assign_plot(tmp_data_analysis_recipe, "no_plot", "GroupA", "GroupB")
        assert not ok

    def test_rejects_missing_source_group(self, tmp_data_analysis_recipe):
        create_group(tmp_data_analysis_recipe, "GroupB", "Group B")
        ok, _ = assign_plot(tmp_data_analysis_recipe, "plot_one", "NoGroup", "GroupB")
        assert not ok

    def test_rejects_missing_target_group(self, tmp_data_analysis_recipe):
        ok, _ = assign_plot(tmp_data_analysis_recipe, "plot_one", "GroupA", "NoGroup")
        assert not ok
