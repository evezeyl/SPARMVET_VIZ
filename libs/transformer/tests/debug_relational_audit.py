#!/usr/bin/env python3
# @deps
# provides: script:debug_relational_audit
# consumes: libs/transformer/tests/data/relational_audit.yaml, libs/transformer/src/transformer/data_assembler.py
# consumed_by: manual relational join testing
# doc: .agents/rules/rules_data_engine.md#3
# @end_deps
import argparse
import os
import sys
import polars as pl
from pathlib import Path
from typing import Dict, List

# ADR-016: Use Package-First Authority
project_root = Path(__file__).resolve().parent.parent.parent.parent
# if str(project_root) not in sys.path:
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

try:
    from ingestion.ingestor import DataIngestor
    from utils.config_loader import ConfigManager
    from transformer.data_wrangler import DataWrangler
    from transformer.data_assembler import DataAssembler
except ImportError as e:
    print(f"❌ ERROR: [Relational Audit] Core imports failed. {e}")
    sys.exit(1)


def perform_relational_audit(manifest_path: str, output_dir: str):
    print(f"\n{'='*80}")
    print(f" 🛡️  RELATIONAL ROW-EXPLOSION AUDIT")
    print(f" Target: {manifest_path}")
    print(f"{'='*80}\n")

    # 1. Load Manifest
    cm = ConfigManager(manifest_path)
    manifest = cm.raw_config

    # 2. Setup Components
    data_dir = str(project_root / "assets/test_data")
    ingestor = DataIngestor(data_dir)

    all_schemas = {}
    all_schemas.update(manifest.get("data_schemas", {}))
    if "metadata_schema" in manifest:
        all_schemas["metadata_schema"] = manifest["metadata_schema"]
    all_schemas.update(manifest.get("additional_datasets_schemas", {}))

    assemblies = manifest.get("join_manifests", {})

    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "relational_audit_report.txt")

    with open(report_path, "w") as report:
        report.write(f"Relational Row-Explosion Audit Report\n")
        report.write(f"Manifest: {manifest_path}\n")
        report.write(f"{'-'*40}\n\n")

        for assembly_id, info in assemblies.items():
            print(f"🔎 Auditing Assembly: {assembly_id}")
            report.write(f"ASSEMBLY: {assembly_id}\n")

            # Prepare Ingredients
            ingredient_dfs = {}
            for ing in info.get("ingredients", []):
                ds_id = ing.get("dataset_id")
                schema = all_schemas.get(ds_id)
                if not schema:
                    continue

                # Ingest & Wrangle (Layer 1)
                lf, _ = ingestor.ingest(ds_id, schema)
                wrangling = schema.get("wrangling", [])
                resolved = DataWrangler._resolve_tier(wrangling, "all")
                if resolved:
                    wrangler = DataWrangler(schema.get("input_fields", {}))
                    lf = wrangler.run(lf, resolved)

                df_ing = lf.collect()
                ingredient_dfs[ds_id] = df_ing.lazy()

                report.write(
                    f"  - Ingredient '{ds_id}': {len(df_ing)} rows, {len(df_ing.columns)} cols\n")
                if "sample_id" in df_ing.columns:
                    unique_samples = df_ing.select(
                        pl.col("sample_id").n_unique()).item()
                    report.write(f"    (Unique samples: {unique_samples})\n")

            # Execute Assembly (Layer 2)
            assembler = DataAssembler(ingredient_dfs)
            recipe = info.get("recipe", [])
            # Handle tiered recipe
            if isinstance(recipe, dict):
                recipe = recipe.get("tier1", []) + recipe.get("tier2", [])

            try:
                lf_result = assembler.assemble(recipe)
                df_result = lf_result.collect()

                report.write(
                    f"  => RESULT: {len(df_result)} rows, {len(df_result.columns)} cols\n")

                # Check for row-explosion
                if "sample_id" in df_result.columns:
                    unique_samples = df_result.select(
                        pl.col("sample_id").n_unique()).item()
                    ratio = len(df_result) / \
                        unique_samples if unique_samples > 0 else 0
                    report.write(
                        f"  => Expansion Ratio: {ratio:.2f} rows per sample\n")

                    if ratio > 100:  # Heuristic threshold for "explosion"
                        print(
                            f"  ⚠️  WARNING: High expansion ratio detected in {assembly_id}: {ratio:.2f}")
                        report.write(
                            f"  ⚠️  WARNING: Potential Cartesian product or massive expansion detected.\n")

                # Materialize sample
                sample_file = os.path.join(
                    output_dir, f"{assembly_id}_audit_view.tsv")
                df_result.head(10).write_csv(sample_file, separator='\t')

                print(
                    f"  ✅ Audit for {assembly_id} complete. Ratio: {len(df_result)/unique_samples:.1f} r/s\n")
                report.write(f"  ✅ Status: OK\n\n")

                # Glimpse output for logs
                print(f"  Glimpse of {assembly_id}:")
                print(df_result.glimpse(return_as_string=True))

            except Exception as e:
                print(f"  ❌ Error in {assembly_id}: {e}")
                report.write(f"  ❌ ASSEMBLY ERROR: {e}\n\n")

    print(f"\n🏁 Audit report saved to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Relational Audit Tool")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="tmp/Manifest_test/ST22_audit/")
    args = parser.parse_args()
    perform_relational_audit(args.manifest, args.output)
