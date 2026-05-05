#!/usr/bin/env python3
# @deps
# provides: script:SF_create_manifest
# consumes: assets/test_data/ (TSV/CSV source files), assets/template_manifests/ (writes scaffolded YAML)
# doc: .claude/knowledge/architecture_decisions.md#ADR-041
# @end_deps
import argparse
import polars as pl
import yaml
import os
from pathlib import Path
from typing import Any, Dict


def map_dtype_to_schema(dtype) -> str:
    """Maps a Polars dtype to the dashboard schema definitions."""
    if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                 pl.Float32, pl.Float64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
        return "numeric"
    elif dtype in [pl.Date, pl.Datetime, pl.Time]:
        return "date"
    elif dtype in [pl.Boolean]:
        return "boolean"
    else:
        return "categorical"


def generate_manifest(data_path: str, output_path: str, mode: str = "full"):
    """
    Improved Asset Generator (ADR-013 compliant).
    Uses Polars LazyFrames to infer schema and scaffold a manifest.
    """
    # 1. Directory Guard
    out_p = Path(output_path)
    os.makedirs(out_p.parent, exist_ok=True)

    # 2. Polars Integration (Scan first 10 rows for schema inference)
    try:
        # Per ADR-002: Default to TSV
        separator = '\t' if data_path.endswith('.tsv') else ','
        lf = pl.scan_csv(data_path, separator=separator, n_rows=10)
        schema = lf.collect_schema()
    except Exception as e:
        print(f"Error scanning data: {e}")
        return

    # 3. Scaffold Fields (input_fields)
    input_fields = {}
    for col_name, dtype in schema.items():
        input_fields[col_name] = {
            "original_name": col_name,
            "type": map_dtype_to_schema(dtype),
            "label": col_name.replace('_', ' ').title()
        }

    # 4. Construct Manifest based on Mode
    if mode == "input_only":
        manifest: Dict[str, Any] = {
            "input_fields": input_fields,
            "wrangling": [],
            "output_fields": []
        }
    else:
        # ADR-013 Manifest with ID and schemas block
        manifest: Dict[str, Any] = {
            "id": out_p.stem,
            "data_schemas": {
                out_p.stem: {
                    "input_fields": input_fields,
                    "wrangling": [],
                    "output_fields": []
                }
            }
        }

    # 5. Write to YAML
    with open(out_p, 'w') as f:
        yaml.dump(manifest, f, sort_keys=False, default_flow_style=False)

    print(
        f"Successfully generated ADR-013 manifest ({mode} mode): {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Asset Generator v2 (ADR-013)")
    parser.add_argument("--data", required=True,
                        help="Path to raw data (TSV/CSV)")
    parser.add_argument("--output", required=True, help="Output YAML path")
    parser.add_argument("--mode", choices=["full", "input_only"], default="full",
                        help="Generation mode: 'full' (with data_schemas) or 'input_only' (flat blocks)")

    args = parser.parse_args()
    generate_manifest(args.data, args.output, args.mode)


if __name__ == "__main__":
    main()
