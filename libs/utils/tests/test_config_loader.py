"""Tests for ConfigManager structural validation (config_loader.py).

Run with:
    .venv/bin/python -m pytest libs/utils/tests/test_config_loader.py -v
"""
from __future__ import annotations

import textwrap
import pytest
from pathlib import Path

from utils.config_loader import ConfigManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# LEGACY-FLAT-PLOTS-1 error path
# ---------------------------------------------------------------------------

def test_flat_plots_at_root_raises(tmp_path):
    """ConfigManager must exit with error when a root-level 'plots:' key is present.

    Root-level plots: was the deprecated authoring format removed in Phase 21-B
    (LEGACY-FLAT-PLOTS-1). Authors must use analysis_groups: exclusively.
    """
    data_analysis_recipe = _write_yaml(tmp_path, "bad_data_analysis_recipe.yaml", """
        id: bad
        data_schemas:
          my_schema:
            source:
              type: local_tsv
              path: fake.tsv
        joins: {}
        plots:
          my_plot:
            mapping:
              x: col_a
            layers:
              - name: geom_bar
                params: {}
        analysis_groups:
          group_a:
            ui_label: Group A
            plots:
              plot_a:
                ui_label: Plot A
                target_dataset: my_schema
                mapping:
                  x: col_a
                layers:
                  - name: geom_bar
                    params: {}
    """)
    with pytest.raises(SystemExit) as exc_info:
        ConfigManager(str(data_analysis_recipe))
    assert exc_info.value.code != 0


def test_valid_analysis_groups_no_flat_plots(tmp_path):
    """ConfigManager must succeed when plots are declared only in analysis_groups."""
    data_analysis_recipe = _write_yaml(tmp_path, "good_data_analysis_recipe.yaml", """
        id: good
        data_schemas:
          my_schema:
            source:
              type: local_tsv
              path: fake.tsv
        joins: {}
        analysis_groups:
          group_a:
            ui_label: Group A
            plots:
              plot_a:
                ui_label: Plot A
                target_dataset: my_schema
                mapping:
                  x: col_a
                layers:
                  - name: geom_bar
                    params: {}
    """)
    cm = ConfigManager(str(data_analysis_recipe))
    assert "plot_a" in cm.raw_config["plots"]
    assert "group_a" in cm.raw_config["analysis_groups"]


def test_the_plot_entry_is_the_plot_config_and_a_spec_key_is_not_unnested(tmp_path):
    """D-0237: a plot entry holds its content directly. The engine's loader no longer reads a `spec:` key (no shim);
    the strict checker refuses it (P01)."""
    path = _write_yaml(tmp_path, "entry_recipe.yaml", """
        id: entry
        data_schemas:
          my_schema:
            source: {type: local_tsv, path: fake.tsv}
        joins: {}
        plot_defaults: {theme: theme_bw}
        analysis_groups:
          group_a:
            ui_label: Group A
            plots:
              plot_a:
                ui_label: Plot A
                target_dataset: my_schema
                mapping: {x: col_a}
                layers: [{name: geom_bar, params: {}}]
              plot_old:
                ui_label: Plot old
                spec: {target_dataset: my_schema, mapping: {x: col_a}, layers: []}
    """)
    cm = ConfigManager(str(path))
    assert cm.raw_config["plots"]["plot_a"]["target_dataset"] == "my_schema"
    assert cm.raw_config["plots"]["plot_a"]["ui_label"] == "Plot A"
    assert "target_dataset" not in cm.raw_config["plots"]["plot_old"]  # not unnested
    assert cm.get_plot_config("group_a", "plot_a")["theme"] == "theme_bw"  # the defaults are merged under the entry
    assert cm.get_plot_config("group_a", "plot_a")["mapping"] == {"x": "col_a"}


def test_a_tier_file_that_holds_only_steps_is_not_unnested_into_a_bare_list(tmp_path):
    """D-0250: `tier1: !include f.yaml` where f.yaml is `steps: [...]`. The wrapper-key rule of the tolerant loader used to remove a
    root key `steps` (the old join fragment wrapper); now `steps` is the content of the tier, so the tier must keep it (the old
    behaviour gave `tier1: [...]` and the assembler said "No step list and no ingredients"). A fragment of `input_fields` is
    still unwrapped (the strict loader refuses it, F01)."""
    (tmp_path / "t1.yaml").write_text("steps:\n- {action: polars_sort, by: [id]}\n")
    (tmp_path / "fields.yaml").write_text("input_fields:\n  id: {type: String}\n")
    path = _write_yaml(tmp_path, "tier_recipe.yaml", """
        id: tier
        data_schemas:
          my_schema:
            source: {type: local_tsv, path: fake.tsv}
            input_fields: !include fields.yaml
            tier1: !include t1.yaml
        joins: {}
        analysis_groups:
          group_a:
            ui_label: Group A
            plots:
              plot_a: {ui_label: Plot A, target_dataset: my_schema, mapping: {x: id}, layers: [{name: geom_bar}]}
    """)
    schema = ConfigManager(str(path)).raw_config["data_schemas"]["my_schema"]
    assert schema["tier1"] == {"steps": [{"action": "polars_sort", "by": ["id"]}]}
    assert schema["input_fields"] == {"id": {"type": "String"}}
