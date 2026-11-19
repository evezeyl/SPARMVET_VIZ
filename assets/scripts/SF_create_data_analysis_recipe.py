#!/usr/bin/env python3
"""Simpler variant of create_data_analysis_recipe.py: infer `input_fields` of ONE tab-separated or comma-separated file.

Writes recipe format 1 (D-0250: a table has `label`, `source`, `null_values`, `strip`, `input_fields` and `tier1: {steps: []}`):
  --mode full        a recipe `<output>` (its id is the file name without `.yaml`) with one table named like the file, and no plot yet
                     (a draft: it passes the recipe checker in profile `build`; write the steps and the plots, then it is complete);
  --mode input_only  only the `input_fields` mapping, as an included fields file holds it (no wrapper key).
The type of a column is the Polars type of the first 10 rows (a sample: review it). No text is declared as "missing"
(`null_values: []`) and no whitespace is stripped (`strip: false`): the author states what means missing in the file.

Example (from the project root):
  ./.venv/bin/python assets/scripts/SF_create_data_analysis_recipe.py \\
      --data assets/test_data/figshare.21737288/amr_results.tsv --output config/data_analysis_recipes/pipelines/figshare_amr.yaml

# @deps
# provides: script:SF_create_data_analysis_recipe
# consumes: assets/test_data/ (TSV/CSV source files), libs/utils/src/utils/recipe_factory.py (minimal_recipe, minimal_schema, recipe_text, write_recipe)
# consumed_by: app/tests/test_writers_emit_format_one.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-041, .claude/design/recipe_format_spec.md (sections 4, 7)
# @end_deps
"""
import argparse
import os
from pathlib import Path
from typing import Dict

import polars as pl

from utils.recipe_factory import minimal_recipe, minimal_schema, recipe_text, write_recipe


def input_fields_of(schema) -> Dict[str, dict]:
    """One field per column: its Polars type name, the name in the file and a label."""
    return {
        col_name: {
            "original_name": col_name,
            "type": dtype.base_type().__name__,
            "label": col_name.replace('_', ' ').title(),
        }
        for col_name, dtype in schema.items()
    }


def generate_data_analysis_recipe(data_path: str, output_path: str, mode: str = "full"):
    """Scaffold a draft recipe (or a fields file) from the header and the first rows of a data file."""
    out_p = Path(output_path)
    os.makedirs(out_p.parent, exist_ok=True)

    try:
        separator = '\t' if data_path.endswith('.tsv') else ','
        lf = pl.scan_csv(data_path, separator=separator, n_rows=10)
        schema = lf.collect_schema()
    except Exception as e:
        print(f"Error scanning data: {e}")
        return

    fields = input_fields_of(schema)

    if mode == "input_only":
        out_p.write_text(recipe_text(fields), encoding="utf-8")
    else:
        table = minimal_schema(data_path, fields, label=out_p.stem.replace('_', ' ').capitalize(), null_values=[], strip=False)
        write_recipe(out_p, minimal_recipe(out_p.stem, label=out_p.stem.replace('_', ' ').capitalize(),
                                           schemas={out_p.stem: table}, plots={}))

    print(f"Successfully generated a recipe format 1 ({mode} mode): {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.split("# @deps")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", required=True,
                        help="Path to raw data (TSV/CSV)")
    parser.add_argument("--output", required=True, help="Output YAML path")
    parser.add_argument("--mode", choices=["full", "input_only"], default="full",
                        help="Generation mode: 'full' (a draft recipe with one table) or 'input_only' (the input_fields mapping only)")

    args = parser.parse_args()
    generate_data_analysis_recipe(args.data, args.output, args.mode)


if __name__ == "__main__":
    main()
