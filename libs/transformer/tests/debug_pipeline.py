#!/usr/bin/env python3
# @deps
# provides: script:debug_pipeline
# consumes: libs/transformer/src/transformer/pipeline.py, libs/ingestion/src/ingestion/ingestor.py
# consumed_by: manual pipeline executor testing
# doc: .claude/rules/rules_data_engine.md#3
# @end_deps
from transformer.pipeline import PipelineExecutor
from ingestion.ingestor import DataIngestor
import sys
import os
import argparse
import polars as pl
from pathlib import Path

# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.


def main():
    parser = argparse.ArgumentParser(
        description="""
        🛡️ PIPELINE DEBUGGER (ADR-032)
        Executes an end-to-end data pipeline (Ingestion -> Wrangling -> Assembly)
        based on a YAML manifest and materializes the result for verification.
        """
    )
    parser.add_argument("--manifest", required=True,
                        help="Path to the YAML pipeline manifest.")
    parser.add_argument("--data-dir", required=True,
                        help="Directory containing raw data files.")
    parser.add_argument(
        "--assembly", help="Specific assembly ID to execute (optional).")
    parser.add_argument(
        "--output", help="Path to sink the result as Parquet (optional).")
    parser.add_argument("--glimpse", action="store_true",
                        help="Print a glimpse of the final dataframe.")

    args = parser.parse_args()

    print(f"--- 🔍 Starting Pipeline Debug Run ---")
    print(f" Manifest: {args.manifest}")
    print(f" Data Dir: {args.data_dir}")

    ingestor = DataIngestor(data_dir=str(Path(args.data_dir)))
    executor = PipelineExecutor(ingestor=ingestor)

    try:
        final_lf = executor.run_pipeline(
            manifest_path=Path(args.manifest),
            assembly_id=args.assembly
        )

        if args.output:
            print(f"💾 Materializing to: {args.output}")
            final_lf.sink_parquet(args.output)

        if args.glimpse:
            print("\n📊 Data Glimpse:")
            df = final_lf.collect() if isinstance(final_lf, pl.LazyFrame) else final_lf
            print(df.glimpse())

        print("\n✅ Pipeline Debug Run Successful.")

    except Exception as e:
        print(f"\n❌ Pipeline Debug Run Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
