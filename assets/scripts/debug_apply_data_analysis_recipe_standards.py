#!/usr/bin/env python3
# @deps
# provides: script:debug_apply_data_analysis_recipe_standards
# consumes: libs/viz_factory/tests/test_data/ (YAML test data analysis recipes)
# doc: .claude/knowledge/architecture_decisions.md#ADR-041
# @end_deps
"""
debug_apply_data_analysis_recipe_standards.py
==================================
Enforces ADR-041 structure on VizFactory YAML test data analysis recipes:
  - Adds the required header blocks (id, description, input_fields,
    wrangling, output_fields) if missing.

Field format follows the ADR-041 Rich Dictionary standard:
  input_fields: {}    # empty dict, not empty list []
  output_fields: {}   # empty dict, not empty list []
  wrangling:
    tier1: []

Usage:
    ./.venv/bin/python assets/scripts/debug_apply_data_analysis_recipe_standards.py
    ./.venv/bin/python assets/scripts/debug_apply_data_analysis_recipe_standards.py \\
        --test-dir libs/viz_factory/tests/test_data \\
        --dry-run
"""

import argparse
import glob
import os
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "SPARMVET_VIZ Data analysis recipe Standards Enforcer. "
            "Applies ADR-041 header structure to VizFactory YAML test data analysis recipes "
            "that are missing required blocks (id, description, input_fields, "
            "wrangling, output_fields)."
        )
    )
    parser.add_argument(
        "--test-dir",
        default="libs/viz_factory/tests/test_data",
        help="Directory with YAML data analysis recipes (default: libs/viz_factory/tests/test_data)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be changed without writing files.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    yamls = glob.glob(os.path.join(args.test_dir, "*.yaml"))

    patched = 0
    for y in yamls:
        with open(y, "r") as f:
            content = f.read()

        if "input_fields:" not in content:
            stem = Path(y).stem  # e.g. "geom_point_test"
            # ADR-041: input_fields and output_fields must be Rich Dicts ({}),
            # not empty lists ([]). Wrangling must use tiered structure.
            header = (
                f'id: "{stem}"\n'
                f'description: "Test data analysis recipe for {stem}"\n'
                f"input_fields: {{}}\n"
                f"wrangling:\n"
                f"  tier1: []\n"
                f"output_fields: {{}}\n"
            )
            new_content = header + content
            if args.dry_run:
                print(f"[DRY RUN] Would patch: {y}")
            else:
                with open(y, "w") as f:
                    f.write(new_content)
                print(f"[PATCHED] {y}")
            patched += 1

    print(f"\nApplied ADR-041 to {patched}/{len(yamls)} YAML data analysis recipes.")
    if args.dry_run:
        print("(Dry run — no files written.)")


if __name__ == "__main__":
    main()
