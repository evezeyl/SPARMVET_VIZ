#!/usr/bin/env python3
# @deps
# provides: script:debug_assembler
# mirrors: app/modules/orchestrator.py
# consumes: libs/ingestion/src/ingestion/ingestor.py, libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py, libs/utils/src/utils/config_loader.py (full-pipeline data analysis recipes only)
# consumed_by: libs/viz_factory/tests/debug_gallery.py, libs/transformer/tests/test_debug_assembler.py
# doc: .claude/rules/rules_agent_role_bioscientist.md#7
# @end_deps
import argparse
import os
import sys
import yaml
import polars as pl
from pathlib import Path
from typing import Dict
from datetime import datetime

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
except ImportError as e:
    print(
        f"❌  ERROR: [Layer 2 Runner] Core imports failed. Check .venv install. {e}")
    sys.exit(1)


def run_assembler_debug(data_analysis_recipe_path: str, data_dir_override: str = None, tmp_dir: str = None):
    """
    Consolidated Assembly Layer Debugger (ADR 012 / ADR 018).
    Orchestrates Layer 1 (Wrangler) and Layer 2 (Assembler) execution.
    """
    print(f"\n[{'='*60}]")
    print(f" 🏗️  LAYER 2 ASSEMBLY DEBUGGER (Consolidated)")
    print(f"[{'='*60}]\n")

    # 1. Load Data Analysis Recipe
    # Full pipeline data analysis recipes use !include directives → require ConfigManager.
    # Partial test data analysis recipes (no !include) use yaml.safe_load directly.
    try:
        data_analysis_recipe_text = Path(data_analysis_recipe_path).read_text(encoding="utf-8")
        if "!include" in data_analysis_recipe_text:
            config_manager = ConfigManager(data_analysis_recipe_path)
            data_analysis_recipe = config_manager.raw_config
        else:
            data_analysis_recipe = yaml.safe_load(data_analysis_recipe_text) or {}
    except Exception as e:
        print(f"  └── ❌ Data analysis recipe Error: Failed to load {data_analysis_recipe_path}. {e}")
        sys.exit(1)

    assemblies = data_analysis_recipe.get("joins", {})
    if not assemblies:
        print("  └── ❌ Error: No 'joins' found in data analysis recipe.")
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

    # 3. Identify all available schemas in data analysis recipe
    all_schemas = {}
    all_schemas.update(data_analysis_recipe.get("data_schemas", {}))
    # metadata_schema is a single block
    if "metadata_schema" in data_analysis_recipe:
        all_schemas["metadata_schema"] = data_analysis_recipe["metadata_schema"]
    all_schemas.update(data_analysis_recipe.get("additional_datasets_schemas", {}))

    # Global cache for all materialized assemblies in this run (ADR-024)
    assembly_results_cache: Dict[str, pl.LazyFrame] = {}

    # 4. Ingest all schemas upfront (mirrors the orchestrator: the declared types, `strip` and `null_values` are applied
    #    by the ingestion itself, then the tier-1 steps of the dataset). A failure stops the run: nothing is skipped.
    ingredients: Dict[str, pl.LazyFrame] = {}
    for ds_id, ds_schema in all_schemas.items():
        lf, _ = ingestor.ingest(ds_id, ds_schema)
        rules = DataWrangler._resolve_tier(ds_schema.get("wrangling", []), "tier1")
        ingredients[ds_id] = DataWrangler().run(lf, rules)

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

        # b) Execute Assembly (Layer 2: Relational step list)
        # Use _resolve_tier to handle tiered steps format (same as orchestrator)
        steps_raw = assembly_info.get("steps", [])
        steps = DataWrangler._resolve_tier(steps_raw, "tier1")

        if not steps and steps_raw:
            print(f"  └── ⚠️  Warning: No tier1 steps resolved from step list.")

        # Normalise join key dtypes across all ingredients before assembling.
        # Mirrors orchestrator.py join dtype normalisation logic exactly.
        per_ingredient_cast: dict = {ds_id: set() for ds_id in assembly_ingredients}
        base_cast: set = set()

        for step in steps:
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

        # A step that names an ingredient the join does not hold fails in the assembler (no step is skipped).
        filtered_steps = steps

        if tmp_dir:
            tmp_root = Path(tmp_dir)
        else:
            lineage_id = Path(data_analysis_recipe_path).stem
            date_str = datetime.now().strftime("%Y-%m-%d")
            tmp_root = project_root / f"tmpAI/{date_str}/{lineage_id}"
        tmp_root.mkdir(parents=True, exist_ok=True)
        intermediate_parquet = str(tmp_root / f"EVE_assembly_{assembly_id}.parquet")

        print(f"  └── 🏗️  Assembling using step list: {len(filtered_steps)} steps.")

        assembler = DataAssembler(assembly_ingredients)
        consolidated_lf = assembler.assemble(filtered_steps)
        # the Tier 1 result, before the tier-2 steps and the contract
        consolidated_lf.collect().write_parquet(intermediate_parquet)
        tier2 = DataWrangler._resolve_tier(assembly_info.get("steps"), "tier2")
        if tier2:
            print(f"  └── 🌿 Tier 2: {len(tier2)} steps.")
            consolidated_lf = DataWrangler().run(consolidated_lf, tier2)

        # d) Collect and persist the contracted result for downstream use.
        # - Parquet: consumed by debug_gallery.py (viz rendering audit)
        # - TSV:     human-readable audit export (open in spreadsheet)
        # Both hold the published columns: the last step of tier 1 is the polars_select of the join.
        contracted_parquet = str(tmp_root / f"EVE_contracted_{assembly_id}.parquet")
        contracted_tsv = str(tmp_root / f"EVE_contracted_{assembly_id}.tsv")

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


    print(f"\n[{'='*60}]")
    print(f" ✅ ALL ASSEMBLY STEPS COMPLETE.")
    print(f"[{'='*60}]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Consolidated Assembly Layer Debugger (ADR 012/018)")
    parser.add_argument("--data-analysis-recipe", required=True,
                        help="Path to pipeline data analysis recipe YAML.")
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
    run_assembler_debug(args.data_analysis_recipe, args.data, out)
