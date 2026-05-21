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
)

# ── Fixtures ──────────────────────────────────────────────────────────────

_MINIMAL = """\
data_schemas:
  sample:
    source:
      path: data.tsv
analysis_groups:
  GroupA:
    label: "Group A"
    plots:
      plot_one:
        label: "Plot One"
        spec: !include test_manifest/plots/plot_one.yaml
"""


@pytest.fixture
def tmp_manifest(tmp_path):
    m = tmp_path / "test_manifest.yaml"
    m.write_text(_MINIMAL, encoding="utf-8")
    spec_dir = tmp_path / "test_manifest" / "plots"
    spec_dir.mkdir(parents=True)
    (spec_dir / "plot_one.yaml").write_text(
        "spec:\n  target_dataset: ''\n  mapping: {}\n  layers: []\n"
    )
    return str(m)


# ── list_groups_plots ─────────────────────────────────────────────────────

class TestListGroupsPlots:
    def test_returns_groups(self, tmp_manifest):
        groups = list_groups_plots(tmp_manifest)
        assert "GroupA" in groups

    def test_spec_is_include_tag(self, tmp_manifest):
        groups = list_groups_plots(tmp_manifest)
        spec = groups["GroupA"]["plots"]["plot_one"]["spec"]
        assert isinstance(spec, _IncludeTag)
        assert "plot_one.yaml" in spec.path


# ── create_group ──────────────────────────────────────────────────────────

class TestCreateGroup:
    def test_creates_group(self, tmp_manifest):
        ok, _ = create_group(tmp_manifest, "NewGroup", "New Group Label")
        assert ok
        groups = list_groups_plots(tmp_manifest)
        assert "NewGroup" in groups
        assert groups["NewGroup"]["label"] == "New Group Label"

    def test_label_defaults_to_id(self, tmp_manifest):
        ok, _ = create_group(tmp_manifest, "EmptyLabel", "")
        assert ok
        assert list_groups_plots(tmp_manifest)["EmptyLabel"]["label"] == "EmptyLabel"

    def test_rejects_invalid_id(self, tmp_manifest):
        ok, msg = create_group(tmp_manifest, "has space", "label")
        assert not ok
        assert "snake_case" in msg

    def test_rejects_duplicate(self, tmp_manifest):
        ok, _ = create_group(tmp_manifest, "GroupA", "label")
        assert not ok


# ── delete_group ──────────────────────────────────────────────────────────

class TestDeleteGroup:
    def test_blocks_non_empty(self, tmp_manifest):
        ok, msg = delete_group(tmp_manifest, "GroupA")
        assert not ok
        assert "1 plot" in msg

    def test_deletes_empty_group(self, tmp_manifest):
        create_group(tmp_manifest, "Empty", "Empty")
        ok, _ = delete_group(tmp_manifest, "Empty")
        assert ok
        assert "Empty" not in list_groups_plots(tmp_manifest)

    def test_rejects_missing_group(self, tmp_manifest):
        ok, _ = delete_group(tmp_manifest, "NoSuch")
        assert not ok


# ── create_plot ───────────────────────────────────────────────────────────

class TestCreatePlot:
    def test_creates_plot_entry(self, tmp_manifest):
        ok, _ = create_plot(tmp_manifest, "GroupA", "plot_two", "Plot Two")
        assert ok
        groups = list_groups_plots(tmp_manifest)
        assert "plot_two" in groups["GroupA"]["plots"]

    def test_creates_spec_file(self, tmp_manifest):
        create_plot(tmp_manifest, "GroupA", "plot_two", "Plot Two")
        spec_file = (Path(tmp_manifest).parent / "test_manifest" / "plots"
                     / "plot_two.yaml")
        assert spec_file.exists()
        content = yaml.safe_load(spec_file.read_text())
        assert "spec" in content

    def test_include_tag_written(self, tmp_manifest):
        create_plot(tmp_manifest, "GroupA", "plot_two", "Plot Two")
        groups = list_groups_plots(tmp_manifest)
        spec = groups["GroupA"]["plots"]["plot_two"]["spec"]
        assert isinstance(spec, _IncludeTag)
        assert "plot_two.yaml" in spec.path

    def test_round_trip_preserves_existing_include(self, tmp_manifest):
        create_plot(tmp_manifest, "GroupA", "plot_two", "Plot Two")
        groups = list_groups_plots(tmp_manifest)
        assert isinstance(groups["GroupA"]["plots"]["plot_one"]["spec"], _IncludeTag)

    def test_rejects_duplicate_plot(self, tmp_manifest):
        ok, _ = create_plot(tmp_manifest, "GroupA", "plot_one", "dup")
        assert not ok

    def test_rejects_missing_group(self, tmp_manifest):
        ok, _ = create_plot(tmp_manifest, "NoGroup", "p", "label")
        assert not ok

    def test_rejects_invalid_plot_id(self, tmp_manifest):
        ok, msg = create_plot(tmp_manifest, "GroupA", "bad id!", "label")
        assert not ok
        assert "snake_case" in msg

    def test_does_not_overwrite_existing_spec_file(self, tmp_manifest):
        spec_file = (Path(tmp_manifest).parent / "test_manifest" / "plots"
                     / "plot_one.yaml")
        original = spec_file.read_text()
        # plot_one already registered — create_plot returns an error before touching disk
        ok, _ = create_plot(tmp_manifest, "GroupA", "plot_one", "dup")
        assert not ok
        assert spec_file.read_text() == original


# ── delete_plot ───────────────────────────────────────────────────────────

class TestDeletePlot:
    def test_removes_plot(self, tmp_manifest):
        ok, _ = delete_plot(tmp_manifest, "GroupA", "plot_one")
        assert ok
        assert "plot_one" not in list_groups_plots(tmp_manifest)["GroupA"]["plots"]

    def test_rejects_missing_plot(self, tmp_manifest):
        ok, _ = delete_plot(tmp_manifest, "GroupA", "no_such_plot")
        assert not ok

    def test_rejects_missing_group(self, tmp_manifest):
        ok, _ = delete_plot(tmp_manifest, "NoGroup", "plot_one")
        assert not ok


# ── assign_plot ───────────────────────────────────────────────────────────

class TestAssignPlot:
    def test_moves_plot(self, tmp_manifest):
        create_group(tmp_manifest, "GroupB", "Group B")
        ok, _ = assign_plot(tmp_manifest, "plot_one", "GroupA", "GroupB")
        assert ok
        groups = list_groups_plots(tmp_manifest)
        assert "plot_one" not in groups["GroupA"]["plots"]
        assert "plot_one" in groups["GroupB"]["plots"]

    def test_preserves_include_tag_on_move(self, tmp_manifest):
        create_group(tmp_manifest, "GroupB", "Group B")
        assign_plot(tmp_manifest, "plot_one", "GroupA", "GroupB")
        groups = list_groups_plots(tmp_manifest)
        spec = groups["GroupB"]["plots"]["plot_one"]["spec"]
        assert isinstance(spec, _IncludeTag)

    def test_rejects_same_group(self, tmp_manifest):
        ok, _ = assign_plot(tmp_manifest, "plot_one", "GroupA", "GroupA")
        assert not ok

    def test_rejects_missing_plot(self, tmp_manifest):
        create_group(tmp_manifest, "GroupB", "Group B")
        ok, _ = assign_plot(tmp_manifest, "no_plot", "GroupA", "GroupB")
        assert not ok

    def test_rejects_missing_source_group(self, tmp_manifest):
        create_group(tmp_manifest, "GroupB", "Group B")
        ok, _ = assign_plot(tmp_manifest, "plot_one", "NoGroup", "GroupB")
        assert not ok

    def test_rejects_missing_target_group(self, tmp_manifest):
        ok, _ = assign_plot(tmp_manifest, "plot_one", "GroupA", "NoGroup")
        assert not ok
