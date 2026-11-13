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


def string_columns_at(types, keys, prior_steps):
    """Which columns are Strings after the old steps `prior_steps` ran on a schema with these declared types.

    The old `strip_whitespace` without columns acted on every String column of the moment, including the ones that
    earlier steps created (a split gives Strings). The real engine answers it on an EMPTY frame built from the declared
    types: no data is read, the plan's schema is.
    """
    import polars as pl
    from transformer.data_wrangler import DataWrangler
    from utils.step_migration import NotConvertible, convert_step

    dtypes = {"categorical": pl.Categorical, "utf8": pl.String, "string": pl.String, "character": pl.String, "numeric": pl.Float64,
              "float": pl.Float64, "integer": pl.Int64, "int": pl.Int64, "date": pl.Date, "bool": pl.Boolean, "boolean": pl.Boolean}
    columns = {}
    for slug, declared in types.items():
        if declared in dtypes:
            columns[slug] = dtypes[declared]
        elif declared is None:
            columns[slug] = pl.Categorical                    # the old default type was categorical
        else:
            columns[slug] = getattr(pl, declared)               # a Polars name already written
    lf = pl.DataFrame({slug: pl.Series(slug, [], dtype=dtype) for slug, dtype in columns.items()}).lazy()
    steps = []
    for old in prior_steps:
        try:
            steps += convert_step(dict(old), strings=[], keys=keys, run="B")
        except NotConvertible:
            continue                                          # a removed action cannot run here; the rest still can
    lf = DataWrangler().run(lf, steps)
    return [name for name, dtype in lf.collect_schema().items() if dtype == pl.String]


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
        report = migrate_recipe_file(path, apply=args.apply, run=args.run, string_columns_at=string_columns_at)
        for line in report.lines:
            print(line)
        changed += len(report.changed_files)
    print(f"{'changed' if args.apply else 'would change'} {changed} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
