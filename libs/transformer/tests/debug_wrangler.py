#!/usr/bin/env python3
# @deps
# provides: script:debug_wrangler
# mirrors: app/modules/orchestrator.py (Tier 1 wrangling path)
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py, libs/utils/src/utils/config_loader.py
# consumed_by: libs/transformer/tests/transformer_integrity_suite.py
# doc: .claude/rules/rules_data_engine.md#3
# @end_deps
import argparse
import os
import sys
import polars as pl
from pathlib import Path
from datetime import datetime

# Fix paths to project root for universal execution if not installed globally
# However, ADR-016 relies on editable installs in .venv
project_root = Path(__file__).resolve().parent.parent.parent.parent
# if str(project_root) not in sys.path:
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

try:
    from ingestion.ingestor import DataIngestor
    from utils.config_loader import ConfigManager
    from transformer.data_wrangler import DataWrangler
except ImportError:
    # Manual fallback for robustness if .venv is not yet sync'd
    try:
        from libs.ingestion.src.ingestion.ingestor import DataIngestor
        from libs.utils.src.utils.config_loader import ConfigManager
        from libs.transformer.src.transformer.data_wrangler import DataWrangler
    except ImportError as e:
        print(
            f"❌  ERROR: [Layer 1 Runner] Core imports failed. Ensure libs are in PYTHONPATH or installed. {e}")
        sys.exit(1)


def run_wrangler_debug(manifest_path: str, data_path_override: str = None, output_path: str = None, tier: str = "all"):
    """
    Consolidated Layer 1 Debugger & Universal Runner (ADR 005 / ADR 013-015).
    tier: 'tier1', 'tier2', or 'all' (default).
    """
    print(f"\n[{'='*60}]")
    print(f" 🚀  LAYER 1 WRANGLER DEBUGGER (v2: Consolidated)")
    print(f"[{'='*60}]\n")

    # 1. Load Manifest
    if not os.path.exists(manifest_path):
        print(f"  └── ❌ Manifest Error: File not found: {manifest_path}")
        sys.exit(1)

    try:
        config_manager = ConfigManager(manifest_path)
        manifest = config_manager.raw_config
    except Exception as e:
        print(f"  └── ❌ Load Error: Failed to parse manifest yaml. {e}")
        sys.exit(1)

    # 2. Extract Dataset Blocks
    dataset_blocks = {}
    if "input_fields" in manifest or "wrangling" in manifest:
        # Standalone Manifest
        dataset_id = manifest.get("id") or manifest.get(
            "name") or Path(manifest_path).stem
        dataset_blocks[dataset_id] = manifest
    else:
        # Combined Pipeline Manifest (Searching for data_schemas, metadata_schema, etc.)
        for key in ["data_schemas", "metadata_schema", "additional_datasets_schemas"]:
            group = manifest.get(key, {})
            if isinstance(group, dict) and group:
                if key == "metadata_schema" and "input_fields" in group:
                    dataset_blocks["metadata_schema"] = group
                else:
                    dataset_blocks.update(group)

    if not dataset_blocks:
        print(
            f"  └── ❌ Manifest Error: No valid dataset blocks found in {manifest_path}")
        sys.exit(1)

    print(
        f"  └── Found {len(dataset_blocks)} dataset(s) in manifest definitions.")

    # 3. Initialize Ingestor (for source resolution)
    ingestor = DataIngestor(data_dir=str(project_root / "assets"))

    # 4. Processing Loop
    for dataset_id, schema in dataset_blocks.items():
        if not isinstance(schema, dict) or ("input_fields" not in schema and "wrangling" not in schema):
            continue

        print(f"\n[TARGET: {dataset_id}]")

        # a) Ingestion Resolution (Override vs. Manifest Source)
        try:
            if data_path_override:
                print(
                    f"  └── 📥 Load: CLI Override used -> {data_path_override}")
                # Enforce TSV/CSV fallback detection logic
                separator = '\t' if data_path_override.endswith(
                    '.tsv') else ','
                lf = pl.scan_csv(data_path_override, separator=separator, null_values=[
                                 "null", "NA", ""])
                source_path = data_path_override
            else:
                # Use source block resolution from DataIngestor (ADR-015)
                # This works if the manifest has a 'source' block.
                lf, source_path = ingestor.ingest(dataset_id, schema)
                print(
                    f"  └── 📥 Load: Resolved from manifest source -> {source_path}")
        except Exception as e:
            print(f"  └── ❌ Ingest Error: {e}")
            continue

        # b) Field Schema & Actions Cleanup (handling nested includes)
        input_fields = schema.get("input_fields", {})
        if isinstance(input_fields, dict) and "input_fields" in input_fields:
            input_fields = input_fields["input_fields"]

        wrangling_rules = schema.get("wrangling", [])
        if isinstance(wrangling_rules, dict) and "wrangling" in wrangling_rules:
            wrangling_rules = wrangling_rules["wrangling"]

        output_fields = schema.get("output_fields", {})
        if isinstance(output_fields, dict) and "output_fields" in output_fields:
            output_fields = output_fields["output_fields"]

        # c) Atomic Wrangling (DataWrangler) — resolve tier
        wrangler = DataWrangler(input_fields)
        resolved_rules = DataWrangler._resolve_tier(wrangling_rules, tier)

        if not resolved_rules:
            if not wrangling_rules:
                print(f"  └── ⚡ Identity Mode: Applying zero actions (ADR-014).")
            else:
                print(f"  └── ⚡ Tier '{tier}' has no actions — skipping.")
            transformed_lf = lf
        else:
            print(
                f"  └── 🛠️  Wrangling [{tier}]: Applying {len(resolved_rules)} actions...")
            try:
                transformed_lf = wrangler.run(lf, resolved_rules)
            except Exception as e:
                print(f"      └── ❌ Wrangling Failure: {e}")
                continue

        # d) Contract Guard (ADR-013: output_fields .select() + Casting)
        if not output_fields:
            if "output_fields" in schema:
                print(
                    f"  └── 🛡️  Contract Guard: Output list empty, retaining all columns.")
            else:
                print(f"  └── ℹ️  No output contract defined. Retaining all columns.")
        else:
            target_columns = list(output_fields.keys()) if isinstance(
                output_fields, dict) else output_fields
            print(
                f"  └── 🛡️  Contract Guard: Selecting {len(target_columns)} columns...")
            try:
                # 1. Selection
                transformed_lf = transformed_lf.select(target_columns)

                # 2. Final Casting (Clean-then-Cast)
                # Map YAML types to Polars types
                type_map = {
                    "categorical": pl.Categorical,
                    "utf8": pl.String,
                    "string": pl.String,
                    "numeric": pl.Float64,
                    "float": pl.Float64,
                    "int": pl.Int64,
                    "i64": pl.Int64,
                    "date": pl.Date
                }

                cast_exprs = []
                for col_name, col_props in output_fields.items():
                    if not isinstance(col_props, dict):
                        continue
                    target_type_str = col_props.get("type", "").lower()
                    if target_type_str in type_map:
                        print(
                            f"      └── 🏷️  Cast: {col_name} -> {target_type_str}")
                        cast_exprs.append(pl.col(col_name).cast(
                            type_map[target_type_str]))

                if cast_exprs:
                    transformed_lf = transformed_lf.with_columns(cast_exprs)

            except Exception as e:
                print(f"      └── ❌ Contract Mismatch/Cast Error: {e}")
                continue

        # e) Materialization (ADR-010)
        # Priority: cli override > default tmpAI dated location
        # If output_path is a directory, save per-dataset file inside it.
        if output_path and (os.path.isdir(output_path) or output_path.endswith(os.sep) or output_path.endswith("/")):
            mat_path = os.path.join(output_path.rstrip(
                "/"), f"{dataset_id}_debug.tsv")
        elif output_path:
            mat_path = output_path
        else:
            lineage_id = Path(manifest_path).stem
            date_str = datetime.now().strftime("%Y-%m-%d")
            dated_dir = project_root / f"tmpAI/{date_str}/{lineage_id}"
            dated_dir.mkdir(parents=True, exist_ok=True)
            mat_path = str(dated_dir / f"{dataset_id}_debug.tsv")

        out_dir = os.path.dirname(mat_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        try:
            df = transformed_lf.collect()
            # Enforce TSV output for consistency per ADR-002
            df.write_csv(mat_path, separator='\t')
            print(f"  └── 💾 Materialized resulting LazyFrame to: {mat_path}")

            # f) Inspection
            print(f"\n  [TRANSFORMED DATA GLIMPSE: {dataset_id}]")
            print(df.glimpse())
            print(f"  └── ✅ Final: {len(df.columns)} columns, {len(df)} rows.")

        except Exception as e:
            print(f"  └── ❌ Materialization Error: {e}")
            continue

    print(f"\n[{'='*60}]")
    print(f" ✅ ALL PROCESSING STEPS COMPLETE.")
    print(f"[{'='*60}]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Consolidated Layer 1 Debugger/Runner (ADR 005/013/014/015)")
    parser.add_argument("--manifest", required=True,
                        help="Path to YAML manifest.")
    parser.add_argument("--data", help="Optional CLI override for data path.")
    parser.add_argument(
        "--output", help="Optional CLI override for output path.")
    parser.add_argument(
        "--tier", choices=["tier1", "tier2", "all"], default="all",
        help="Which wrangling tier to execute: tier1, tier2, or all (default: all).")

    args = parser.parse_args()
    run_wrangler_debug(args.manifest, args.data, args.output, args.tier)
