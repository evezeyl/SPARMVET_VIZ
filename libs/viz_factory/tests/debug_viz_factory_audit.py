#!/usr/bin/env python3
# @deps
# provides: script:debug_viz_factory_audit
# consumes: .claude/tasks/tasks.md, libs/viz_factory/src/, libs/viz_factory/tests/test_data/, tmp/
# doc: .claude/rules/workspace_standard.md#5
# @end_deps
"""
debug_viz_factory_audit.py
==========================
Cross-reference VizFactory task status in tasks.md against:
  - @register_plot_component decorators in libs/viz_factory/src/
  - Test triplet presence in libs/viz_factory/tests/test_data/
  - PNG evidence in tmp/

Reports GHOST TASKs (marked done but unverified) and
UNDER-REPORTED components (implemented but marked [ ]).

Usage:
    ./.venv/bin/python libs/viz_factory/tests/debug_viz_factory_audit.py
    ./.venv/bin/python libs/viz_factory/tests/debug_viz_factory_audit.py --tasks path/to/tasks.md
"""

import argparse
import os
import re
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "SPARMVET_VIZ VizFactory Audit Tool. "
            "Cross-references tasks.md against @register_plot_component decorators "
            "and test triplet evidence on disk."
        )
    )
    parser.add_argument(
        "--tasks",
        default=".claude/tasks/tasks.md",
        help="Path to tasks.md (default: .claude/tasks/tasks.md)",
    )
    parser.add_argument(
        "--src-dir",
        default="libs/viz_factory/src",
        help="VizFactory source directory (default: libs/viz_factory/src)",
    )
    parser.add_argument(
        "--test-dir",
        default="libs/viz_factory/tests/test_data",
        help="VizFactory test data directory (default: libs/viz_factory/tests/test_data)",
    )
    parser.add_argument(
        "--tmp-dir",
        default="tmp",
        help="Directory to check for PNG evidence (default: tmp)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Parse tasks.md for VizFactory component status
    with open(args.tasks, "r") as f:
        lines = f.readlines()

    in_viz = False
    task_components = {}
    for line in lines:
        if "VIZ_FACTORY IMPLEMENTATION" in line:
            in_viz = True
        if not in_viz:
            continue
        m = re.match(r"\s*-\s*\[([ xX])\]\s*`?([a-zA-Z0-9_]+)`?.*", line)
        if m:
            status = m.group(1).lower() == "x"
            comp = m.group(2)
            task_components[comp] = status

    # 2. Parse src for decorators
    registered_components = set()
    for root, _, files in os.walk(args.src_dir):
        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                with open(filepath, "r") as f:
                    content = f.read()
                    matches = re.findall(
                        r'@register_plot_component\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                        content,
                    )
                    registered_components.update(matches)

    # 3. Check test triplets on disk
    test_data_files = set(os.listdir(args.test_dir)) if Path(
        args.test_dir).exists() else set()
    # Flatten all PNGs in tmp/ and subdirs
    tmp_pngs = set()
    if Path(args.tmp_dir).exists():
        for root, _, files in os.walk(args.tmp_dir):
            tmp_pngs.update(files)

    # 4. Report
    report_ghost = []
    report_under = []
    layer_prefixes = (
        "geom_", "scale_", "theme_", "facet_", "coord_",
        "position_", "guide_", "element_", "stat_",
    )

    for comp, is_done in task_components.items():
        if not comp.startswith(layer_prefixes):
            continue

        is_registered = comp in registered_components
        has_yaml = f"{comp}_test.yaml" in test_data_files
        has_png = f"USER_debug_{comp}.png" in tmp_pngs

        if is_done:
            issues = []
            if not is_registered:
                issues.append("Not Registered")
            if not has_yaml:
                issues.append("Missing YAML test")
            if not has_png:
                issues.append("Missing PNG evidence")
            if issues:
                report_ghost.append(f"  GHOST: {comp} — {', '.join(issues)}")
        else:
            if is_registered and has_yaml and has_png:
                report_under.append(
                    f"  UNDER-REPORTED: {comp} — fully implemented but marked [ ]")

    print("\n=== VizFactory Audit Report ===")
    print(f"  Components in tasks.md: {len(task_components)}")
    print(f"  Registered in src/:     {len(registered_components)}")
    print(f"  GHOST TASKs (marked [x] but unverified): {len(report_ghost)}")
    for r in report_ghost:
        print(r)
    print(f"  UNDER-REPORTED (implemented but [ ]): {len(report_under)}")
    for r in report_under:
        print(r)
    print("================================\n")


if __name__ == "__main__":
    main()
