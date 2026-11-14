#!/usr/bin/env python3
"""Scaffold a data analysis recipe in recipe format 1 from tab-separated data files.

For every data file the script reads the header and the values, and writes:
  - one recipe file `<out_file>` (its id is the file name without `.yaml`);
  - next to it, in a folder with the same name, two included files per table:
    `<table>_fields.yaml` (one entry per column: its Polars type, a label, the name in the file when it differs)
    and `<table>_wrangling.yaml` (the empty step lists, to fill).
The recipe has one plot (a bar chart of the first column of the first table), so it can be opened at once; the
author then writes the steps, the joins and the plots.

What the script decides, so that it can be checked:
  - the type of a column is the type Polars reads from the whole file (Int64, Float64, Boolean, String, ...);
    review it: a column of codes such as 007 is read as a number;
  - no text is declared as "missing" (`null_values: []`) and no whitespace is stripped (`strip: false`):
    the author states what means missing in each file;
  - a column named by --primary_key_data is marked `is_entity_key: true`; a table without such a column is written
    without a key, and the script says so.

What it refuses, with a message, before anything is written: a file that is not tab-separated (.tsv), a file outside
the project (the folder the script is run from: a recipe names its data by a path relative to the project root), two
files that give the same table id, and a recipe file or an included file that already exists.

The recipe is judged by the recipe checker (`utils.recipe_check`) before it is written.

Examples (from the project root):
  ./.venv/bin/python assets/scripts/create_data_analysis_recipe.py \\
      --data_dir assets/test_data/my_data --primary_key_data sample_id \\
      --out_file config/data_analysis_recipes/pipelines/my_recipe.yaml
  ./.venv/bin/python assets/scripts/create_data_analysis_recipe.py \\
      --data_files assets/test_data/a.tsv assets/test_data/b.tsv --metadata_file assets/test_data/meta.tsv \\
      --primary_key_data sample_id --primary_key_metadata sample_id --out_file tmpAI/scaffold/my_recipe.yaml

# @deps
# provides: script:create_data_analysis_recipe
# consumes: libs/utils/src/utils/recipe_factory.py (minimal_recipe, minimal_schema, minimal_plot, Include, write_recipe, write_fragment), libs/utils/src/utils/recipe_check.py (check_recipe), libs/utils/src/utils/polars_types.py (text_dtype_names)
# consumed_by: app/tests/test_writers_emit_format_one.py
# doc: .claude/design/recipe_format_spec.md (sections 4, 7), .claude/rules/rules_asset_scripts.md, docs/appendix/running_helper_scripts.qmd
# @end_deps
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import polars as pl

from utils.polars_types import text_dtype_names
from utils.recipe_check import check_recipe
from utils.recipe_factory import Include, minimal_plot, minimal_recipe, minimal_schema, write_fragment, write_recipe

METADATA_ID = "metadata_schema"
WRANGLING_COMMENT = ("The steps of this table, in order (recipe format 1).\n"
                     "tier1: applied when the table is read. tier2 is optional.")


class Refused(Exception):
    """The script cannot write a valid recipe from what it was given; the message says why and what to do."""


def clean_column_name(col_name: str) -> str:
    """A column header as a plain lowercase name with underscores (the key of the field in the recipe)."""
    s = str(col_name).lower()
    s = re.sub(r'[/.:\s\-]+', '_', s)
    s = re.sub(r'[^\w_]', '', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_')


def table_id_of(path: Path) -> str:
    """The id of a table from its file name: without a leading `test_data_` and a trailing `_YYYYMMDD_HHMMSS`."""
    name = re.sub(r'^test_data_', '', path.stem)
    return re.sub(r'_\d{8}_\d{6}$', '', name)


def project_path(path: Path) -> str:
    """The path of a data file relative to the project root (the folder the script is run from)."""
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        raise Refused(f"{path} is not inside the project ({Path.cwd()}). A recipe names its data by a path relative to "
                      "the project root: copy the file inside the project and run the script from the project root.")


def read_table(path: Path) -> pl.DataFrame:
    """The whole file, read as Polars reads a tab-separated file; the types fit every row."""
    if path.suffix.lower() != ".tsv":
        raise Refused(f"{path} is not a tab-separated file (.tsv). The recipe format reads tab-separated files and "
                      "parquet files: save the table as tab-separated text first.")
    if not path.is_file():
        raise Refused(f"{path} was not found. Check --data_dir, --data_files and --metadata_file.")
    try:
        return pl.read_csv(path, separator="\t", infer_schema_length=None)
    except Exception as error:
        raise Refused(f"{path} cannot be read as a tab-separated table ({' '.join(str(error).split())[:200]}).")


def fields_of(table: pl.DataFrame, key_columns: Sequence[str], path: Path) -> Tuple[Dict[str, dict], Optional[str]]:
    """One field per column, and the column that is the key (the first of `key_columns` found), or None."""
    key = next((name for name in key_columns if name in table.columns), None)
    allowed = text_dtype_names()
    fields: Dict[str, dict] = {}
    for column in table.columns:
        slug = clean_column_name(column)
        type_name = table.schema[column].base_type().__name__
        if not slug:
            raise Refused(f"{path}: the column header {column!r} has no letter or digit, so it cannot be a field name.")
        if slug in fields:
            raise Refused(f"{path}: the column headers {fields[slug].get('original_name', slug)!r} and {column!r} "
                          f"both give the field name {slug!r}. Rename one of them in the file.")
        if type_name not in allowed:
            raise Refused(f"{path}: the column {column!r} was read as {type_name}, which is not a type a recipe can declare.")
        field: Dict[str, object] = {"type": type_name}
        if slug != column:
            field["original_name"] = str(column)
        field["label"] = str(column).replace('_', ' ').title()
        if column == key:
            field["is_entity_key"] = True
        fields[slug] = field
    return fields, key


def data_files_of(data_dir: Optional[str], data_files: Optional[Sequence[str]]) -> List[Path]:
    """The data files asked for, in a fixed order; says which files of --data_dir are not read."""
    if data_dir:
        folder = Path(data_dir)
        if not folder.is_dir():
            raise Refused(f"--data_dir {data_dir} was not found or is not a folder.")
        if data_files:
            return [folder / name for name in data_files]
        skipped = sorted(p.name for p in folder.iterdir() if p.is_file() and p.suffix.lower() != ".tsv")
        if skipped:
            print("Not read (the recipe format reads tab-separated .tsv files): " + ", ".join(skipped))
        return sorted(folder.glob("*.tsv"))
    return [Path(name) for name in data_files or []]


def build(recipe_id: str, data_files: Sequence[Path], key_columns: Sequence[str],
          metadata_file: Optional[Path], metadata_key: Optional[str]) -> dict:
    """The whole recipe as one dictionary (nothing included yet), in recipe format 1."""
    if not data_files:
        raise Refused("No data file: give --data_files, or a --data_dir that holds .tsv files.")
    schemas: Dict[str, dict] = {}
    origin: Dict[str, Path] = {}
    for path in data_files:
        table_id = table_id_of(path)
        if table_id in schemas:
            raise Refused(f"{origin[table_id]} and {path} give the same table id {table_id!r}. Rename one of the files.")
        fields, key = fields_of(read_table(path), key_columns, path)
        if key is None:
            print(f"Note: none of the key columns {list(key_columns)} is in {path}; the table {table_id!r} is written without a key.")
        schemas[table_id] = minimal_schema(project_path(path), fields, label=table_id.replace('_', ' ').capitalize())
        origin[table_id] = path

    first_table = next(iter(schemas))
    first_column = next(iter(schemas[first_table]["input_fields"]))
    plot_id = re.sub(r'^(?=[^a-z])', 'plot_', clean_column_name(recipe_id)) + "_first_plot"
    plots = {plot_id: minimal_plot(first_table, {"x": first_column}, label=f"Rows per {first_column}")}
    recipe = minimal_recipe(recipe_id, label=recipe_id.replace('_', ' ').capitalize(), schemas=schemas, plots=plots)
    recipe["info"]["description"] = (f"Scaffold written by create_data_analysis_recipe.py from {len(schemas)} data file(s). "
                                     "Review the types, then write the steps, the joins and the plots.")
    recipe["analysis_groups"]["main"]["label"] = "First look"

    if metadata_file is not None:
        fields, key = fields_of(read_table(metadata_file), [metadata_key] if metadata_key else [], metadata_file)
        if metadata_key and key is None:
            print(f"Note: the key column {metadata_key!r} is not in {metadata_file}; the metadata table is written without a key.")
        metadata = minimal_schema(project_path(metadata_file), fields, label="Metadata")
        # the place of metadata_schema is after the data schemas (the order of the specification)
        recipe = {key_: value for key_, value in recipe.items() if key_ != "analysis_groups"} | {
            METADATA_ID: metadata, "analysis_groups": recipe["analysis_groups"]}
    return recipe


def split_into_files(recipe: dict, out_file: Path) -> Dict[Path, object]:
    """Move the fields and the steps of every table to included files; returns {file: its content} and changes `recipe`."""
    folder = out_file.parent / out_file.stem
    fragments: Dict[Path, object] = {}
    tables = list(recipe["data_schemas"].items())
    if METADATA_ID in recipe:
        tables.append((METADATA_ID, recipe[METADATA_ID]))
    for table_id, schema in tables:
        for key, suffix in (("input_fields", "fields"), ("wrangling", "wrangling")):
            name = f"{table_id}_{suffix}.yaml"
            fragments[folder / name] = schema[key]
            schema[key] = Include(f"{out_file.stem}/{name}")
    return fragments


def create(out_file: Path, data_files: Sequence[Path], key_columns: Sequence[str],
           metadata_file: Optional[Path] = None, metadata_key: Optional[str] = None) -> Path:
    """Build, judge and write the recipe; raises `Refused` (and writes nothing) when it cannot be valid."""
    recipe = build(out_file.stem, data_files, key_columns, metadata_file, metadata_key)
    result = check_recipe(recipe, "run", file_stem=out_file.stem)
    if result.errors:
        raise Refused("The recipe would not be valid in recipe format 1:\n" + "\n".join(
            "  " + problem.text(out_file.name) for problem in result.errors))
    fragments = split_into_files(recipe, out_file)
    existing = [path for path in (out_file, *fragments) if path.exists()]
    if existing:
        raise Refused("These files already exist and are not replaced: " + ", ".join(str(p) for p in existing)
                      + ". Choose another --out_file, or remove them first.")
    for path, content in fragments.items():
        write_fragment(path, content, comment=WRANGLING_COMMENT if path.name.endswith("_wrangling.yaml") else None)
    return write_recipe(out_file, recipe)


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description=__doc__.split("# @deps")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data_dir", required=False,
                        help="Folder of the data files. Without --data_files every .tsv file of the folder is read.")
    parser.add_argument("--data_files", nargs='+', required=False,
                        help="Tab-separated data file(s). With --data_dir the names are relative to that folder.")
    parser.add_argument("--metadata_file", required=False,
                        help="Tab-separated metadata file; written as metadata_schema. Optional.")
    parser.add_argument("--primary_key_data", nargs='+', required=True,
                        help="Name(s) of the column that identifies the entity (for example sample_id); in each data "
                             "file the first name found is marked is_entity_key.")
    parser.add_argument("--primary_key_metadata", required=False,
                        help="Name of the key column of the metadata file. Optional.")
    parser.add_argument("--out_file", "--outfile", required=False,
                        help="The recipe file to write; its name without .yaml is the id of the recipe. Default: "
                             "assets/template_data_analysis_recipes/template_<date>_<time>.yaml")
    args = parser.parse_args(argv)

    out_file = Path(args.out_file) if args.out_file else (
        Path("assets/template_data_analysis_recipes") / f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")
    try:
        if not args.data_dir and not args.data_files:
            raise Refused("No data file: give --data_files or --data_dir.")
        written = create(out_file, data_files_of(args.data_dir, args.data_files), args.primary_key_data,
                         Path(args.metadata_file) if args.metadata_file else None, args.primary_key_metadata)
    except Refused as refused:
        print(f"Error: {refused}")
        print("Nothing was written.")
        sys.exit(1)

    print(f"Recipe written (format 1, checked): {written}")
    print(f"Included files: {written.parent / written.stem}/")
    print("Next: review the types of the columns, say which texts mean a missing value (null_values), "
          "then write the steps, the joins and the plots.")


if __name__ == "__main__":
    main()
