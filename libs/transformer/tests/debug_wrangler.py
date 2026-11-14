#!/usr/bin/env python3
# @deps
# provides: script:debug_wrangler
# mirrors: app/modules/orchestrator.py (Tier 1 wrangling path)
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py
# consumed_by: libs/transformer/tests/test_debug_wrangler.py
# doc: .claude/rules/rules_data_engine.md#3
# @end_deps
"""Run the wrangling steps of one format 1 recipe on its data and write the result as a TSV (the @verify evidence).

The recipe is a standalone data schema (keys `source`, `null_values`, `strip`, `input_fields`, `wrangling` at the top
level, like the test pairs in libs/transformer/tests/data/) or a pipeline recipe whose `data_schemas` hold them.
The data is read exactly as the app reads it (declared types, `null_values`, `strip`); nothing is cast or selected
afterwards, because the recipe states what it wants as steps.

Example:
  ./.venv/bin/python libs/transformer/tests/debug_wrangler.py \\
      --data-analysis-recipe libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml --output tmpAI/cast.tsv
"""
import argparse
import sys
from pathlib import Path

import yaml

from ingestion.ingestor import DataIngestor
from transformer.data_wrangler import DataWrangler

SCHEMA_GROUPS = ("data_schemas", "metadata_schema", "additional_datasets_schemas")


def dataset_blocks(recipe: dict, fallback_id: str) -> dict:
    """The data schemas of a recipe by dataset id: the recipe itself when it is standalone."""
    if "input_fields" in recipe or "wrangling" in recipe:
        return {recipe.get("id") or fallback_id: recipe}
    blocks = {}
    for key in SCHEMA_GROUPS:
        group = recipe.get(key) or {}
        if key == "metadata_schema" and "input_fields" in group:
            blocks["metadata_schema"] = group
        else:
            blocks.update(group)
    return blocks


def wrangle(dataset_id: str, schema: dict, tier: str, data_dir: str, data_override: str | None = None):
    """Ingest one data schema and run its wrangling tier; return the collected DataFrame."""
    if data_override:
        schema = {**schema, "source": {"type": "local_tsv", "path": data_override}}
    lf, _ = DataIngestor(data_dir).ingest(dataset_id, schema)
    steps = DataWrangler._resolve_tier(schema.get("wrangling"), tier)
    return (DataWrangler().run(lf, steps) if steps else lf).collect()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-analysis-recipe", required=True, help="Path to the YAML data analysis recipe.")
    parser.add_argument("--data", help="Read this TSV instead of the one the recipe names.")
    parser.add_argument("--output", required=True, help="TSV file to write (one dataset), or a folder (one file per dataset).")
    parser.add_argument("--data-dir", default=".", help="Folder searched when a schema names no source (default: the current folder).")
    parser.add_argument("--tier", choices=["tier1", "tier2", "all"], default="all", help="Wrangling tier to run (default: all).")
    args = parser.parse_args(argv)

    path = Path(args.data_analysis_recipe)
    recipe = yaml.safe_load(path.read_text()) or {}
    blocks = dataset_blocks(recipe, path.stem)
    if not blocks:
        print(f"No data schema found in {path}", file=sys.stderr)
        return 1
    out = Path(args.output)
    for dataset_id, schema in blocks.items():
        df = wrangle(dataset_id, schema, args.tier, args.data_dir, args.data)
        target = out / f"{dataset_id}_debug.tsv" if (out.is_dir() or str(args.output).endswith("/")) else out
        target.parent.mkdir(parents=True, exist_ok=True)
        df.write_csv(target, separator="\t")
        print(f"[{dataset_id}] {len(df.columns)} columns, {len(df)} rows -> {target}")
        print(df.glimpse())
    return 0


if __name__ == "__main__":
    sys.exit(main())
