#!/usr/bin/env python3
# @deps
# provides: script:debug_audit (viz_factory)
# consumes: libs/viz_factory/src/viz_factory/, libs/viz_factory/tests/test_data/
# consumed_by: manual component audit
# doc: .claude/rules/rules_data_engine.md
# @end_deps
import sys
import os
import argparse
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="""
        📋 VIZ FACTORY AUDIT (ADR-032)
        Cross-references tasks.md against the Artist registry and test triplets.
        Identifies Ghost Tasks (completed in task but missing logic/test) 
        and Under-Reported Tasks (implemented but not marked in task).
        """
    )
    # Use relative paths from project root
    project_root = Path(__file__).resolve().parent.parent.parent.parent

    parser.add_argument("--tasks", default=str(project_root /
                        ".claude/tasks/tasks.md"), help="Path to tasks.md")
    parser.add_argument("--src-dir", default=str(project_root /
                        "libs/viz_factory/src"), help="Source directory for decorators")
    parser.add_argument("--test-dir", default=str(project_root /
                        "libs/viz_factory/tests/test_data"), help="Test data directory")
    parser.add_argument("--report", action="store_true",
                        help="Print report instead of just counts.")

    args = parser.parse_args()

    # 1. Parse tasks.md
    if not os.path.exists(args.tasks):
        print(f"❌ Error: Tasks file not found at {args.tasks}")
        sys.exit(1)

    with open(args.tasks, 'r') as f:
        lines = f.readlines()

    in_viz = False
    task_components = {}
    for line in lines:
        if 'VIZ_FACTORY IMPLEMENTATION' in line:
            in_viz = True
        if not in_viz:
            continue
        m = re.match(r'\s*-\s*\[([ xX])\]\s*`?([a-zA-Z0-9_]+)`?.*', line)
        if m:
            status = m.group(1).lower() == 'x'
            comp = m.group(2)
            task_components[comp] = status

    # 2. Parse src for decorators
    registered_components = set()
    for root, _, files in os.walk(args.src_dir):
        for filename in files:
            if filename.endswith('.py'):
                with open(os.path.join(root, filename), 'r') as f:
                    content = f.read()
                    matches = re.findall(
                        r'@register_plot_component\(\s*[\'"]([^\'"]+)[\'"]\s*\)', content)
                    registered_components.update(matches)

    # 3. Check triplets
    test_data_files = set(os.listdir(args.test_dir)) if os.path.exists(
        args.test_dir) else set()
    tmp_files = set(os.listdir(str(project_root / "tmp"))
                    ) if os.path.exists(str(project_root / "tmp")) else set()

    report = []
    ghosts = 0
    under_reported = 0

    for comp, is_done_in_task in task_components.items():
        if not comp.startswith(('geom_', 'scale_', 'theme_', 'facet_', 'coord_', 'position_', 'guide_', 'element_')):
            continue

        is_registered = comp in registered_components
        has_yaml = f"{comp}_test.yaml" in test_data_files
        has_png = f"USER_debug_{comp}.png" in tmp_files or f"{comp}.png" in tmp_files

        if is_done_in_task:
            issues = []
            if not is_registered:
                issues.append("Not Registered")
            if not has_yaml:
                issues.append("Missing YAML test")
            if issues:
                ghosts += 1
                report.append(
                    f"👻 GHOST TASK: {comp} marked [x] but has issues: {', '.join(issues)}")
        elif is_registered and has_yaml:
            under_reported += 1
            report.append(
                f"📈 UNDER-REPORTED: {comp} marked [ ] but is fully implemented and tested.")

    print(f"--- 📋 Viz Factory Audit Summary ---")
    print(f" Total Identified Components: {len(task_components)}")
    print(f" Registered in Library:      {len(registered_components)}")
    print(f" Ghost Tasks Detected:       {ghosts}")
    print(f" Under-Reported Tasks:       {under_reported}")

    if args.report and report:
        print("\n--- Detailed Audit Observations ---")
        for r in report:
            print(r)


if __name__ == "__main__":
    main()
