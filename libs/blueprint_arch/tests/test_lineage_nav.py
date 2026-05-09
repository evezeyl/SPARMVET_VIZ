"""
Tests for build_plot_lineage and get_plot_ids_in_group (ADR-074).

Uses the real 1_test_data_ST22_dummy.yaml manifest as the fixture — this is
the canonical reference manifest and is always present in the repo.

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/test_lineage_nav.py -v
"""
import pytest
from pathlib import Path

from blueprint_arch.manifest_navigator import (
    build_plot_lineage,
    get_plot_ids_in_group,
)

MANIFEST = "config/manifests/pipelines/1_test_data_ST22_dummy.yaml"

# Known facts from 1_test_data_ST22_dummy.yaml (stable reference values)
KNOWN_GROUP = "Quality Control"
KNOWN_PLOTS_IN_QC = {"qc_reads_horizontal_barplot", "assembly_quality_dotplot"}
KNOWN_PLOT = "qc_reads_horizontal_barplot"
# Ingredients flowing into the QC join (FastP, Quast, Bracken, metadata)
KNOWN_INGREDIENTS = {"FastP", "Quast", "Bracken", "metadata_schema"}
KNOWN_JOIN_SCHEMA = "QC_Reads_Anchor"


# ── get_plot_ids_in_group ──────────────────────────────────────────────────────

class TestGetPlotIdsInGroup:

    def test_returns_list(self):
        result = get_plot_ids_in_group(KNOWN_GROUP, MANIFEST)
        assert isinstance(result, list)

    def test_known_group_returns_expected_plots(self):
        result = get_plot_ids_in_group(KNOWN_GROUP, MANIFEST)
        assert set(result) == KNOWN_PLOTS_IN_QC

    def test_missing_group_returns_empty(self):
        assert get_plot_ids_in_group("NonExistentGroup_XYZ", MANIFEST) == []

    def test_missing_manifest_returns_empty(self):
        assert get_plot_ids_in_group(KNOWN_GROUP, "/tmp/does_not_exist.yaml") == []

    def test_all_groups_return_non_empty(self):
        """Every real group in the manifest has at least one plot."""
        import yaml
        class _Cap(yaml.SafeLoader): pass
        _Cap.add_constructor("!include", lambda l, n: l.construct_scalar(n))
        tree = yaml.load(Path(MANIFEST).read_text(), Loader=_Cap)
        for gid in (tree.get("analysis_groups") or {}):
            ids = get_plot_ids_in_group(gid, MANIFEST)
            assert len(ids) > 0, f"Group '{gid}' returned no plots"

    def test_plot_ids_are_strings(self):
        for pid in get_plot_ids_in_group(KNOWN_GROUP, MANIFEST):
            assert isinstance(pid, str) and pid


# ── build_plot_lineage ─────────────────────────────────────────────────────────

class TestBuildPlotLineage:

    def test_returns_list(self):
        assert isinstance(build_plot_lineage(KNOWN_PLOT, MANIFEST), list)

    def test_missing_plot_returns_empty(self):
        assert build_plot_lineage("nonexistent_plot_xyz", MANIFEST) == []

    def test_missing_manifest_returns_empty(self):
        assert build_plot_lineage(KNOWN_PLOT, "/tmp/does_not_exist.yaml") == []

    def test_steps_are_1_based_sequential(self):
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        assert len(steps) > 0
        for i, step in enumerate(steps, 1):
            assert step["step"] == i, f"Step numbering broken at position {i}"

    def test_each_step_has_required_keys(self):
        for step in build_plot_lineage(KNOWN_PLOT, MANIFEST):
            for key in ("step", "type", "schema_id", "label", "rel"):
                assert key in step, f"Step {step} missing key '{key}'"

    def test_step_types_are_valid(self):
        valid = {"data_source", "wrangling", "join", "plot_spec"}
        for step in build_plot_lineage(KNOWN_PLOT, MANIFEST):
            assert step["type"] in valid, f"Unknown step type: {step['type']}"

    def test_last_step_is_plot_spec(self):
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        assert steps[-1]["type"] == "plot_spec"
        assert steps[-1]["schema_id"] == KNOWN_PLOT

    def test_plot_spec_label_is_non_empty(self):
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        plot_step = steps[-1]
        assert plot_step["label"]  # label populated from manifest or schema_id

    def test_data_sources_include_known_ingredients(self):
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        source_ids = {s["schema_id"] for s in steps if s["type"] == "data_source"}
        assert source_ids == KNOWN_INGREDIENTS

    def test_join_step_present_with_correct_schema_id(self):
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        join_steps = [s for s in steps if s["type"] == "join"]
        assert len(join_steps) == 1
        assert join_steps[0]["schema_id"] == KNOWN_JOIN_SCHEMA

    def test_wrangling_step_follows_each_data_source(self):
        """Every data_source step must be followed immediately by a wrangling step."""
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        for i, step in enumerate(steps):
            if step["type"] == "data_source":
                assert i + 1 < len(steps), "data_source is last step (no wrangling follows)"
                assert steps[i + 1]["type"] == "wrangling", (
                    f"data_source '{step['schema_id']}' not followed by wrangling"
                )
                assert steps[i + 1]["schema_id"] == step["schema_id"]

    def test_data_source_steps_have_non_empty_rel(self):
        """Source file paths are resolved from the manifest."""
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        for step in steps:
            if step["type"] == "data_source":
                assert step["rel"], (
                    f"data_source '{step['schema_id']}' has no source path"
                )

    def test_wrangling_rel_points_to_yaml(self):
        """Wrangling rel paths end in .yaml."""
        for step in build_plot_lineage(KNOWN_PLOT, MANIFEST):
            if step["type"] == "wrangling" and step["rel"]:
                assert step["rel"].endswith(".yaml"), (
                    f"Wrangling rel path not a YAML file: {step['rel']}"
                )

    def test_ordering_data_before_join_before_plot(self):
        """Pipeline ordering: all data_source steps precede join, join precedes plot_spec."""
        steps = build_plot_lineage(KNOWN_PLOT, MANIFEST)
        types = [s["type"] for s in steps]
        last_source_idx = max((i for i, t in enumerate(types) if t == "data_source"), default=-1)
        join_idx = next((i for i, t in enumerate(types) if t == "join"), None)
        plot_idx = types.index("plot_spec")

        if join_idx is not None:
            assert last_source_idx < join_idx < plot_idx, (
                f"Ordering violated: sources end at {last_source_idx}, "
                f"join at {join_idx}, plot at {plot_idx}"
            )
        else:
            assert last_source_idx < plot_idx

    def test_second_plot_in_same_group(self):
        """assembly_quality_dotplot is a different plot in QC — lineage must work for it too."""
        plot_id = "assembly_quality_dotplot"
        steps = build_plot_lineage(plot_id, MANIFEST)
        assert len(steps) > 0
        assert steps[-1]["schema_id"] == plot_id
        assert steps[-1]["type"] == "plot_spec"
