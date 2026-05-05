#!/usr/bin/env python3
# @deps
# provides: script:debug_assembler
# mirrors: app/modules/orchestrator.py
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/transformer/src/transformer/metadata_validator.py
# consumed_by: libs/viz_factory/tests/debug_gallery.py
# doc: .claude/rules/rules_persona_bioscientist.md#7
# @end_deps
import argparse
import os
import sys
import polars as pl
from pathlib import Path
from typing import Dict

# ADR-016: Use Package-First Authority (Editable Installs)
# Ensure project root is in sys.path for fallback
project_root = Path(__file__).resolve().parent.parent.parent.parent
# if str(project_root) not in sys.path:
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

try:
    from ingestion.ingestor import DataIngestor
    from utils.config_loader import ConfigManager
    from transformer.data_wrangler import DataWrangler
    from transformer.data_assembler import DataAssembler
    from transformer.metadata_validator import MetadataValidator
except ImportError as e:
    print(
        f"❌  ERROR: [Layer 2 Runner] Core imports failed. Check .venv install. {e}")
    sys.exit(1)


def run_assembler_debug(manifest_path: str, data_dir_override: str = None, tmp_dir: str = None):
    """
    Consolidated Assembly Layer Debugger (ADR 012 / ADR 018).
    Orchestrates Layer 1 (Wrangler) and Layer 2 (Assembler) execution.
    """
    print(f"\n[{'='*60}]")
    print(f" 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)")
    print(f"[{'='*60}]\n")

    # 1. Load Manifest
    try:
        config_manager = ConfigManager(manifest_path)
        manifest = config_manager.raw_config
    except Exception as e:
        print(f"  └── ❌ Manifest Error: Failed to load {manifest_path}. {e}")
        sys.exit(1)

    assemblies = manifest.get("join_manifests", {})
    if not assemblies:
        print("  └── ❌ Error: No 'join_manifests' found in manifest.")
        return

    # 2. Initialize Ingestor
    # Default search directory for mock assets per Project Conventions
    default_data_dir = str(project_root / "assets/test_data")
    data_dir = data_dir_override or default_data_dir

    if not os.path.exists(data_dir):
        print(
            f"  └── ⚠️  Warning: Data directory '{data_dir}' not found. Falling back to project assets.")
        data_dir = default_data_dir

    ingestor = DataIngestor(data_dir)
    print(f"  └── 📥 Ingestion Base: {data_dir}")

    # 3. Identify all available schemas in manifest
    all_schemas = {}
    all_schemas.update(manifest.get("data_schemas", {}))
    # metadata_schema is a single block
    if "metadata_schema" in manifest:
        all_schemas["metadata_schema"] = manifest["metadata_schema"]
    all_schemas.update(manifest.get("additional_datasets_schemas", {}))

    # Global cache for all materialized assemblies in this run (ADR-024)
    assembly_results_cache: Dict[str, pl.LazyFrame] = {}
    validator = MetadataValidator()

    # 4. Ingest all schemas upfront (mirrors orchestrator pattern)
    ingredients: Dict[str, pl.LazyFrame] = {}
    for ds_id, ds_schema in all_schemas.items():
        try:
            lf, _ = ingestor.ingest(ds_id, ds_schema)

            # ADR-034: Malformed Data Gatekeeping (same as orchestrator)
            input_contract = ds_schema.get("input_fields", {})
            validator.validate(lf, input_contract, context=f"Dataset [{ds_id}]")
            lf = validator.enforce_schema(lf, input_contract)

            wrangling_raw = ds_schema.get("wrangling", [])
            rules = DataWrangler._resolve_tier(wrangling_raw, "tier1")
            wrangler = DataWrangler(data_schema=input_contract)
            lf = wrangler.run(lf, rules)

            ingredients[ds_id] = lf
        except Exception as e:
            print(f"⚠️ Ingestion Error in '{ds_id}': {str(e)}")
            continue

    # 5. Assembly Execution Loop
    for assembly_id, assembly_info in assemblies.items():
        print(f"\n[ASSEMBLY: {assembly_id}]")

        # a) Build ordered ingredient dict from assembly's ingredients list
        ingredients_list = assembly_info.get("ingredients", [])
        ingredient_ids = [
            item.get("dataset_id") if isinstance(item, dict) else item
            for item in ingredients_list
            if (item.get("dataset_id") if isinstance(item, dict) else item)
        ]
        assembly_ingredients = {
            ds_id: ingredients[ds_id]
            for ds_id in ingredient_ids
            if ds_id in ingredients
        }
        if not assembly_ingredients:
            assembly_ingredients = ingredients

        # b) Execute Assembly (Layer 2: Relational recipe)
        # Use _resolve_tier to handle tiered recipe format (same as orchestrator)
        recipe_raw = assembly_info.get("recipe", [])
        recipe = DataWrangler._resolve_tier(recipe_raw, "tier1")

        if not recipe and recipe_raw:
            print(f"  └── ⚠️  Warning: No tier1 steps resolved from recipe.")

        # Normalise join key dtypes across all ingredients before assembling.
        # Mirrors orchestrator.py join dtype normalisation logic exactly.
        per_ingredient_cast: dict = {ds_id: set() for ds_id in assembly_ingredients}
        base_cast: set = set()

        for step in recipe:
            right_id = step.get("right_ingredient")
            sym = step.get("on")
            left_on = step.get("left_on")
            right_on = step.get("right_on")

            if sym:
                cols = [sym] if isinstance(sym, str) else sym
                base_cast.update(cols)
                if right_id and right_id in per_ingredient_cast:
                    per_ingredient_cast[right_id].update(cols)

            if left_on:
                cols = [left_on] if isinstance(left_on, str) else left_on
                base_cast.update(cols)
            if right_on and right_id and right_id in per_ingredient_cast:
                cols = [right_on] if isinstance(right_on, str) else right_on
                per_ingredient_cast[right_id].update(cols)

        normalised: dict = {}
        for ds_id, lf in assembly_ingredients.items():
            schema_names = set(lf.collect_schema().names())
            cols_to_cast = per_ingredient_cast.get(ds_id, set())
            if ds_id == next(iter(assembly_ingredients)):
                cols_to_cast = cols_to_cast | base_cast
            cast_exprs = [
                pl.col(col).cast(pl.String)
                for col in cols_to_cast
                if col in schema_names
            ]
            normalised[ds_id] = lf.with_columns(cast_exprs) if cast_exprs else lf
        assembly_ingredients = normalised

        # Filter steps referring to missing ingredients
        filtered_recipe = []
        for step in recipe:
            right_id = step.get("right_ingredient")
            if right_id and right_id not in assembly_ingredients:
                print(f"  └── ⚠️  Skipping step '{step.get('action')}' — missing ingredient '{right_id}'")
                continue
            filtered_recipe.append(step)

        # Inject sink_parquet into the recipe — assembler handles content-hash
        # short-circuit internally. This parquet captures the full pre-contract
        # intermediate result (all columns), consistent with orchestrator behaviour.
        tmp_root = Path(tmp_dir) if tmp_dir else project_root / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        intermediate_parquet = str(tmp_root / f"EVE_assembly_{assembly_id}.parquet")

        filtered_recipe.append({
            "action": "sink_parquet",
            "path": intermediate_parquet,
            "force_recompute": False
        })

        print(f"  └── 🏗️  Assembling using recipe: {len(filtered_recipe)} steps.")

        assembler = DataAssembler(assembly_ingredients)
        try:
            consolidated_lf = assembler.assemble(filtered_recipe)
        except Exception as e:
            print(f"  └── ❌ Assembly Error: {e}")
            continue

        # c) Final Assembly Contract Guard (ADR-013)
        # Uses dict-based final_contract — same format as orchestrator.py.
        # Contract is applied AFTER the assembler returns (post-assembly select),
        # matching orchestrator.py behaviour exactly.
        final_contract = assembly_info.get("final_contract", {})
        if final_contract and isinstance(final_contract, dict):
            keep = list(final_contract.keys())
            schema_names = set(consolidated_lf.collect_schema().names())
            missing = [c for c in keep if c not in schema_names]
            if missing:
                print(f"  └── ⚠️  final_contract references missing columns: {missing}")
                keep = [c for c in keep if c in schema_names]
            if keep:
                print(f"  └── 🛡️  final_contract: projecting to {len(keep)} contracted columns.")
                consolidated_lf = consolidated_lf.select(keep)

        # d) Collect and persist the contracted result for downstream use.
        # - Parquet: consumed by debug_gallery.py (viz rendering audit)
        # - TSV:     human-readable audit export (open in spreadsheet)
        # Both use the contracted schema (final_contract applied above).
        contracted_parquet = str(tmp_root / f"EVE_contracted_{assembly_id}.parquet")
        contracted_tsv = str(tmp_root / f"EVE_contracted_{assembly_id}.tsv")

        try:
            df = consolidated_lf.collect()
            df.write_parquet(contracted_parquet)
            df.write_csv(contracted_tsv, separator="\t")

            print(f"  └── 💾 Contracted parquet: {contracted_parquet}")
            print(f"  └── 📄 Contracted TSV (audit): {contracted_tsv}")

            # Cache contracted result for downstream assemblies in this run
            assembly_results_cache[assembly_id] = df.lazy()

            # e) Inspection
            print(f"\n  [ASSEMBLY PREVIEW: {assembly_id}]")
            print(f"  └── Final Schema: {df.schema}")
            print(df.head(5))
            print(f"  └── ✅ Final: {len(df.columns)} columns, {len(df)} rows.")

        except Exception as e:
            print(f"  └── ❌ Materialization Error: {e}")
            continue

    print(f"\n[{'='*60}]")
    print(f" ✅ ALL ASSEMBLY STEPS COMPLETE.")
    print(f"[{'='*60}]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Consolidated Assembly Layer Debugger (ADR 012/018)")
    parser.add_argument("--manifest", required=True,
                        help="Path to pipeline manifest YAML.")
    parser.add_argument(
        "--data", help="Optional override for source data directory.")
    parser.add_argument(
        "--tmp", default=None,
        help="Output directory for parquet/TSV files (default: <project_root>/tmp/).")
    parser.add_argument(
        "--output", default=None,
        help="Output path (file or directory). If a file path is given, the parent "
             "directory is used as the output directory. Overrides --tmp.")

    args = parser.parse_args()
    # --output takes precedence; resolve to directory if a file path was given
    out = args.output or args.tmp
    if out:
        p = Path(out)
        out = str(p.parent) if p.suffix else str(p)
    run_assembler_debug(args.manifest, args.data, out)
