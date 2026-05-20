#!/usr/bin/env python3
# @deps
# provides: script:create_manifest
# consumes: assets/test_data/ (TSV/CSV source files), assets/template_manifests/ (writes scaffolded YAML)
# doc: .claude/knowledge/architecture_decisions.md#ADR-041, docs/reference/wrangling_guide.qmd
# @end_deps
import argparse
import polars as pl
import yaml
import re
from pathlib import Path
from datetime import datetime
import sys
from typing import Any


def represent_include(dumper, data):
    """Custom YAML representer to output !include tags cleanly without quotes."""
    return dumper.represent_scalar('!include', data.path, style='')


class IncludeRef:
    """Wrapper class to hold the !include path."""

    def __init__(self, path):
        self.path = path


yaml.add_representer(IncludeRef, represent_include)


def map_dtype_to_schema(dtype):
    """Maps a Polars dtype to the dashboard schema definitions."""
    if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                 pl.Float32, pl.Float64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
        return "numeric"
    elif dtype in [pl.Date, pl.Datetime, pl.Time]:
        return "date"
    elif dtype in [pl.Boolean]:
        return "boolean"
    else:
        # For String/Utf8, Categorical, Object, etc.
        return "categorical"


def clean_column_name(col_name: str) -> str:
    """Sanitizes a messy TSV column header into a safe, snake_case YAML dictionary key."""
    s = str(col_name).lower()
    # Replace slashes, dots, colons, spaces, hyphens with underscores
    s = re.sub(r'[/.:\s\-]+', '_', s)
    # Remove all other special characters
    s = re.sub(r'[^\w_]', '', s)
    # Deduplicate underscores and strip
    s = re.sub(r'_+', '_', s)
    return s.strip('_')


def scaffold_schema(df, primary_key=None, is_metadata=False):
    """Generates the schema dictionary from a dataframe."""
    schema = {}

    # If it's the metadata section, the top level might be required_id_column or similar,
    # but the instructions say they are listed under metadata_schema.
    # However, based on the implementation plan, metadata_schema looks like:
    # metadata_schema:
    #   isolate_id: { type: "character", label: "Isolate ID", is_primary_key: true }
    #   ...

    for col in df.columns:
        col_type = map_dtype_to_schema(df[col].dtype)
        safe_key = clean_column_name(col)

        # Build field dict
        field_dict: dict[str, Any] = {
            # Keep a record of the raw TSV column name
            "original_name": str(col),
            "type": col_type,
            "label": str(col).replace('_', ' ').title()
        }

        if col == primary_key:
            field_dict["is_primary_key"] = True

        if col_type == "date":
            field_dict["format"] = "%Y-%m-%d"  # Default guess

        if is_metadata and col != primary_key:
            field_dict["mandatory"] = False

        schema[safe_key] = field_dict

    return schema


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a deployment manifest from a dataset.")
    parser.add_argument("--data_dir", required=False,
                        help="Path to a directory containing main data files (*.tsv or *.csv).")
    parser.add_argument("--data_files", nargs='+', required=False,
                        help="Path to main data file(s).")
    parser.add_argument("--metadata_file", required=False,
                        help="Path to metadata file.")
    parser.add_argument("--primary_key_data", nargs='+', required=True,
                        help="Primary key column(s) for main data (checks each file sequentially).")
    parser.add_argument("--primary_key_metadata", required=False,
                        help="Primary key column for metadata.")
    parser.add_argument("--out_file", "--outfile", required=False,
                        help="Path to save the generated manifest YAML. Defaults to assets/template_manifests/template_<timestamp>.yaml.")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Define output file
    if args.out_file:
        out_file = Path(args.out_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = Path("assets/template_manifests")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"template_{timestamp}.yaml"

    # Create the subfolder for modular schema pieces
    schema_dir = out_file.parent / out_file.stem
    schema_dir.mkdir(parents=True, exist_ok=True)

    # Resolve data files
    all_data_files = []

    if args.data_dir:
        dpath = Path(args.data_dir)
        if not dpath.is_dir():
            print(
                f"Error: --data_dir '{args.data_dir}' is not a valid directory.")
            sys.exit(1)

        if args.data_files:
            for f_name in args.data_files:
                all_data_files.append(str(dpath / f_name))
        else:
            found_files = list(dpath.glob("*.tsv")) + list(dpath.glob("*.csv"))
            all_data_files.extend([str(p) for p in found_files])
    else:
        if args.data_files:
            all_data_files.extend(args.data_files)

    if not all_data_files:
        print("Error: You must provide either --data_files or --data_dir.")
        sys.exit(1)

    # Strict File Existence Check
    missing_files = []
    valid_data_files = []

    for f in all_data_files:
        if not Path(f).exists():
            missing_files.append(f)
        else:
            valid_data_files.append(f)

    if missing_files:
        print("\n" + "="*40)
        print("CRITICAL ERROR: FILES NOT FOUND")
        print("="*40)
        print("The following requested data files do not exist at the resolved paths:")
        for mf in missing_files:
            print(f"  - {mf}")
        print("\nPlease check your --data_dir and --data_files arguments.")
        print("="*40 + "\n")
        sys.exit(1)

    # 1. Base Headers
    source_name = f"directory '{Path(args.data_dir).name}'" if args.data_dir else f"{len(valid_data_files)} files"
    manifest: dict[str, Any] = {
        "id": "example_species_template",
        "type": "species",
        "info": {
            "display_name": "Example Species",
            "category": "Auto-generated",
            "tags": ["template", "draft"],
            "description": f"Template manifest generated from {source_name}.",
            "version": "1.0"
        }
    }

    # 2. Main Data Schemas (Nested under data_schemas)
    manifest["data_schemas"] = {}

    for d_file in valid_data_files:
        try:
            df_data = pl.read_csv(
                d_file, separator='\t' if d_file.endswith('.tsv') else ',')

            actual_key = next(
                (k for k in args.primary_key_data if k in df_data.columns), None)
            if not actual_key:
                print(
                    f"Warning: None of the primary keys {args.primary_key_data} found in {d_file}!")

            raw_name = Path(d_file).stem

            # Use Regex to clean the dataset name for the manifest
            # 1. Remove optional "test_data_" prefix
            clean_name = re.sub(r'^test_data_', '', raw_name)
            # 2. Remove standard timestamp suffix "_YYYYMMDD_HHMMSS"
            clean_name = re.sub(r'_\d{8}_\d{6}$', '', clean_name)

            dataset_name = clean_name
            # Generate the schema dictionary for fields
            schema_dict = scaffold_schema(
                df_data, primary_key=actual_key, is_metadata=False)

            # 1. Write the _fields fragment
            fields_frag_file = schema_dir / f"{dataset_name}_fields.yaml"
            with open(fields_frag_file, 'w') as f:
                yaml.dump(schema_dict, f, sort_keys=False,
                          default_flow_style=False)

            # 2. Write an empty _wrangling fragment placeholder
            wrangling_frag_file = schema_dir / f"{dataset_name}_wrangling.yaml"
            with open(wrangling_frag_file, 'w') as f:
                f.write("# Define your Polars wrangling steps here\n[]\n")

            # Add the !include references explicitly isolating fields and wrangling
            fields_rel_path = f"{out_file.stem}/{dataset_name}_fields.yaml"
            wrangling_rel_path = f"{out_file.stem}/{dataset_name}_wrangling.yaml"

            manifest["data_schemas"][dataset_name] = {
                "input_fields": IncludeRef(fields_rel_path),
                "wrangling": IncludeRef(wrangling_rel_path),
                "output_fields": IncludeRef(fields_rel_path)
            }

        except Exception as e:
            print(f"Error reading main data {d_file}: {e}")
            sys.exit(1)

    # 3. Metadata Schema (optional)
    if args.metadata_file and args.primary_key_metadata:
        try:
            df_meta = pl.read_csv(
                args.metadata_file, separator='\t' if args.metadata_file.endswith('.tsv') else ',')
            if args.primary_key_metadata not in df_meta.columns:
                print(
                    f"Warning: Primary key '{args.primary_key_metadata}' not found in metadata columns!")

            meta_schema_dict = scaffold_schema(
                df_meta, primary_key=args.primary_key_metadata, is_metadata=True)

            # Write the individual metadata fragment to the subfolder
            meta_frag_file = schema_dir / "metadata_schema.yaml"
            with open(meta_frag_file, 'w') as f:
                yaml.dump(meta_schema_dict, f, sort_keys=False,
                          default_flow_style=False)

            # Add the !include reference to the master manifest (ADR-013)
            rel_path = f"{out_file.stem}/metadata_schema.yaml"
            manifest["metadata_schema"] = {
                "input_fields": IncludeRef(rel_path),
                "wrangling": None,  # Metadata wrangling is optional
                "output_fields": IncludeRef(rel_path)
            }

        except Exception as e:
            print(f"Error reading metadata: {e}")

    # 4. Standard Plot Archetypes Placeholder
    first_dataset_key = list(manifest["data_schemas"].keys())[
        0] if manifest["data_schemas"] else "unknown_dataset"
    manifest["plot_defaults"] = {
        "height": 450,
        "theme": "theme_minimal",
        "show_legend": True
    }

    manifest["analysis_groups"] = {
        "Example_Group": {
            "description": "Auto-scaffolded plotting group",
            "plots": {
                "demo_bar": {
                    "target_dataset": first_dataset_key,
                    "mapping": {"x": "Replace_Me"},
                    "layers": [{"name": "geom_bar", "params": {}}],
                    "title": "Replace Me Title"
                }
            }
        }
    }

    # Write to file
    with open(out_file, 'w') as f:
        yaml.dump(manifest, f, sort_keys=False, default_flow_style=False)

    print(f"Successfully generated scaffold manifest: {out_file}")
    print("Please review and manually align plotting logic keys before moving to config/manifests/species/")


if __name__ == "__main__":
    main()
