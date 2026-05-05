#!/usr/bin/env python3
# @deps
# provides: script:debug_bootstrap_viz_yamls
# consumes: libs/viz_factory/tests/test_data/ (writes bootstrapped YAML test manifests)
# doc: .claude/knowledge/architecture_decisions.md#ADR-041
# @end_deps
"""
debug_bootstrap_viz_yamls.py
=============================
Bootstraps missing ADR-013 YAML test manifests for VizFactory components.
Each generated manifest references a shared generic data file
(geom_point_test.tsv) and includes a minimal plot definition.

This is the authoritative source for regenerating test scaffolding
if manifests are lost or missing.

Usage:
    ./.venv/bin/python assets/scripts/debug_bootstrap_viz_yamls.py
    ./.venv/bin/python assets/scripts/debug_bootstrap_viz_yamls.py \\
        --test-dir libs/viz_factory/tests/test_data \\
        --dry-run
"""

import argparse
import os
import yaml
from pathlib import Path


# Registry of components requiring bootstrapped manifests.
# Format: {component_name: {mapping: {...}, layers: [...]}}
MISSING_MANIFESTS = {
    "scale_color_cmap": {
        "mapping": {"x": "x", "y": "y", "color": "category"},
        "layers": [{"name": "geom_point"}, {"name": "scale_color_cmap", "params": {"cmap_name": "viridis"}}],
    },
    "element_text": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point"}, {"name": "element_text", "params": {"color": "red", "target": "axis_text_x"}}],
    },
    "element_line": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point"}, {"name": "element_line", "params": {"color": "blue", "target": "panel_grid_major"}}],
    },
    "element_rect": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point"}, {"name": "element_rect", "params": {"fill": "lightgray", "target": "panel_background"}}],
    },
    "facet_labeller": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [
            {"name": "geom_point"},
            {"name": "facet_wrap", "params": {"facets": "~category_col"}},
            {"name": "facet_labeller", "params": {"labeller": "label_both"}},
        ],
    },
    "coord_cartesian": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point"}, {"name": "coord_cartesian", "params": {"xlim": [0, 10], "ylim": [0, 10]}}],
    },
    "coord_equal": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point"}, {"name": "coord_equal", "params": {"ratio": 1}}],
    },
    "position_identity": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point", "params": {"position": "position_identity"}}],
    },
    "guide_title": {
        "mapping": {"x": "x", "y": "y", "color": "category"},
        "layers": [{"name": "geom_point"}, {"name": "guide_title", "params": {"title": "My Title", "target": "color"}}],
    },
    "guide_label": {
        "mapping": {"x": "x", "y": "y", "color": "category"},
        "layers": [{"name": "geom_point"}, {"name": "guide_label", "params": {"label_position": "bottom", "target": "color"}}],
    },
    "guide_direction": {
        "mapping": {"x": "x", "y": "y", "color": "category"},
        "layers": [{"name": "geom_point"}, {"name": "guide_direction", "params": {"direction": "horizontal", "target": "color"}}],
    },
    "guide_reverse": {
        "mapping": {"x": "x", "y": "y", "color": "category"},
        "layers": [{"name": "geom_point"}, {"name": "guide_reverse", "params": {"reverse": True, "target": "color"}}],
    },
    "stat_count": {
        "mapping": {"x": "category"},
        "layers": [{"name": "geom_bar", "params": {"stat": "stat_count"}}],
    },
    "stat_bin": {
        "mapping": {"x": "x"},
        "layers": [{"name": "geom_histogram", "params": {"stat": "stat_bin", "bins": 10}}],
    },
    "stat_identity": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_point", "params": {"stat": "stat_identity"}}],
    },
    "stat_summary": {
        "mapping": {"x": "category", "y": "y"},
        "layers": [{"name": "geom_pointrange", "params": {"stat": "stat_summary"}}],
    },
    "stat_boxplot": {
        "mapping": {"x": "category", "y": "y"},
        "layers": [{"name": "geom_boxplot", "params": {"stat": "stat_boxplot"}}],
    },
    "stat_ydensity": {
        "mapping": {"x": "category", "y": "y"},
        "layers": [{"name": "geom_violin", "params": {"stat": "stat_ydensity"}}],
    },
    "stat_smooth": {
        "mapping": {"x": "x", "y": "y"},
        "layers": [{"name": "geom_smooth", "params": {"stat": "stat_smooth", "method": "lm"}}],
    },
    "stat_density": {
        "mapping": {"x": "x"},
        "layers": [{"name": "geom_density", "params": {"stat": "stat_density"}}],
    },
    "stat_ecdf": {
        "mapping": {"x": "x"},
        "layers": [{"name": "geom_step", "params": {"stat": "stat_ecdf"}}],
    },
    "stat_function": {
        "mapping": {},
        "layers": [{"name": "geom_line", "params": {"stat": "stat_function", "fun": "lambda x: x**2"}}],
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "SPARMVET_VIZ VizFactory Manifest Bootstrap. "
            "Creates missing ADR-013 YAML test manifests for registered components. "
            "Only creates files that do not already exist on disk."
        )
    )
    parser.add_argument(
        "--test-dir",
        default="libs/viz_factory/tests/test_data",
        help="Target directory for YAML manifests (default: libs/viz_factory/tests/test_data)",
    )
    parser.add_argument(
        "--data-path",
        default="./geom_point_test.tsv",
        help="Relative data path for generic manifests (default: ./geom_point_test.tsv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing files.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    created = 0
    skipped = 0

    for name, plot_dict in MISSING_MANIFESTS.items():
        dest = Path(args.test_dir) / f"{name}_test.yaml"
        if dest.exists():
            skipped += 1
            continue

        manifest_data = {
            "id": f"{name}_test",
            "description": f"Auto-bootstrapped test manifest for {name}",
            "input_fields": [],
            "wrangling": [],
            "output_fields": [],
            "data_path": args.data_path,
            "plots": {"test_plot": plot_dict},
        }

        if args.dry_run:
            print(f"[DRY RUN] Would create: {dest}")
        else:
            with open(dest, "w") as f:
                yaml.dump(manifest_data, f, default_flow_style=False)
            print(f"[CREATED] {dest}")
        created += 1

    print(
        f"\nBootstrap complete: {created} created, {skipped} already existed.")
    if args.dry_run:
        print("(Dry run — no files written.)")


if __name__ == "__main__":
    main()
