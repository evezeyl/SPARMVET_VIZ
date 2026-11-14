"""Convert data analysis recipes from format 0 (unversioned) to format 1 (spec_version: 1), run A.

What run A does: adds spec_version and the engine lines; renames display_name, is_primary_key and source_name;
turns every field type into its Polars name; writes the old sanitiser's settings (null_values, strip) into every schema;
unwraps input_fields fragments. It edits the text, so every comment stays. Run B turns keep_columns and
drop_columns into polars_select and polars_drop; run C removes final_contract and the schema output_fields (the
columns become a polars_select, the display texts become labels). Run D gives the recipes the strict form that the
checker asks for: a label on every schema, join, group and plot (the text the app showed), description instead of the
old info blocks, taxonomy on the plot entry, no wrapper line in a fragment.

Without --apply nothing is written: the script lists what it would change. Safe to run twice.

Examples:
  .venv/bin/python assets/scripts/migrate_recipe_format.py config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml
  .venv/bin/python assets/scripts/migrate_recipe_format.py --apply config/data_analysis_recipes/pipelines
"""
import argparse
import sys
from pathlib import Path

from utils.contract_migration import migrate_contracts
from utils.recipe_migration import migrate_recipe_file
from utils.strict_form_migration import migrate_strict_form


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
    parser.add_argument("--run", choices=["A", "B", "C", "D"], default="A",
                        help="A: format, types, missing values, action names (default). B: keep_columns and drop_columns to polars_select and polars_drop. C: final_contract and the schema output_fields removed (a polars_select as the last step of tier1, labels). D: the strict form of the checker (a label everywhere, the old info blocks, the taxonomy keys of a plot spec, wrapper lines in fragments)")
    args = parser.parse_args(argv)
    files = []
    for item in map(Path, args.paths):
        files += sorted(item.rglob("*.yaml")) if item.is_dir() else [item]
    changed = 0
    for path in files:
        if not path.read_text(encoding="utf-8").lstrip().startswith(("id:", "#")) and "\nid:" not in path.read_text(encoding="utf-8"):
            continue
        if args.run == "C":
            report = migrate_contracts(path, apply=args.apply)
        elif args.run == "D":
            report = migrate_strict_form(path, apply=args.apply)
        else:
            report = migrate_recipe_file(path, apply=args.apply, run=args.run, string_columns_at=string_columns_at)
        for line in report.lines:
            print(line)
        changed += len(report.changed_files)
    print(f"{'changed' if args.apply else 'would change'} {changed} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
