"""Convert data analysis recipes from format 0 (unversioned) to format 1 (spec_version: 1), run A.

What run A does: adds spec_version and the engine lines; renames display_name, is_primary_key and source_name;
turns every field type into its Polars name; writes the old sanitiser's settings (null_values, strip) into every schema;
unwraps input_fields fragments. It edits the text, so every comment stays. The action names and run B
(final_contract, keep_columns, drop_columns) come in later parts of the migration.

Without --apply nothing is written: the script lists what it would change. Safe to run twice.

Examples:
  .venv/bin/python assets/scripts/migrate_recipe_format.py config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml
  .venv/bin/python assets/scripts/migrate_recipe_format.py --apply config/data_analysis_recipes/pipelines
"""
import argparse
import sys
from pathlib import Path

from utils.recipe_migration import migrate_recipe_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="recipe files, or folders searched for *.yaml recipes (files with an id: line)")
    parser.add_argument("--apply", action="store_true", help="write the changes (default: only list them)")
    parser.add_argument("--run", choices=["A", "B"], default="A",
                        help="A: format, types, missing values, action names (default). B: keep_columns and drop_columns to polars_select and polars_drop")
    args = parser.parse_args(argv)
    files = []
    for item in map(Path, args.paths):
        files += sorted(item.rglob("*.yaml")) if item.is_dir() else [item]
    changed = 0
    for path in files:
        if not path.read_text(encoding="utf-8").lstrip().startswith(("id:", "#")) and "\nid:" not in path.read_text(encoding="utf-8"):
            continue
        report = migrate_recipe_file(path, apply=args.apply, run=args.run)
        for line in report.lines:
            print(line)
        changed += len(report.changed_files)
    print(f"{'changed' if args.apply else 'would change'} {changed} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
