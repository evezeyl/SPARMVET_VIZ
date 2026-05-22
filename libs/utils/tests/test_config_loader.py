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
    manifest = _write_yaml(tmp_path, "bad_manifest.yaml", """
        id: bad
        data_schemas:
          my_schema:
            source:
              type: local_tsv
              path: fake.tsv
        join_manifests: {}
        plots:
          my_plot:
            mapping:
              x: col_a
            layers:
              - name: geom_bar
                params: {}
        analysis_groups:
          group_a:
            label: Group A
            plots:
              plot_a:
                label: Plot A
                spec:
                  target_dataset: my_schema
                  mapping:
                    x: col_a
                  layers:
                    - name: geom_bar
                      params: {}
    """)
    with pytest.raises(SystemExit) as exc_info:
        ConfigManager(str(manifest))
    assert exc_info.value.code != 0


def test_valid_analysis_groups_no_flat_plots(tmp_path):
    """ConfigManager must succeed when plots are declared only in analysis_groups."""
    manifest = _write_yaml(tmp_path, "good_manifest.yaml", """
        id: good
        data_schemas:
          my_schema:
            source:
              type: local_tsv
              path: fake.tsv
        join_manifests: {}
        analysis_groups:
          group_a:
            label: Group A
            plots:
              plot_a:
                label: Plot A
                spec:
                  target_dataset: my_schema
                  mapping:
                    x: col_a
                  layers:
                    - name: geom_bar
                      params: {}
    """)
    cm = ConfigManager(str(manifest))
    assert "plot_a" in cm.raw_config["plots"]
    assert "group_a" in cm.raw_config["analysis_groups"]
