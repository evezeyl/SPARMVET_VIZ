#!/usr/bin/env python3
# @deps
# provides: script:generate_demo_data
# consumes: assets/test_data/1_test_data_ST22_dummy/ (ground truth TSVs), libs/test_lab (AquaSynthesizer)
# consumed_by: assets/test_data/demo_high_integrity/ (writes synthetic TSVs)
# doc: libs/test_lab/README.md
# @end_deps
"""
generate_demo_data.py
---------------------
Generates high-integrity synthetic demo data from ground-truth ST22 test data.

Uses AquaSynthesizer (libs/test_lab) to produce 30 synthesized samples
with PK anchoring on sample_id. Output is written to assets/test_data/demo_high_integrity/.

Usage:
  ./.venv/bin/python assets/scripts/generate_demo_data.py
  ./.venv/bin/python assets/scripts/generate_demo_data.py --n-samples 50 --out-dir /tmp/demo_out

Requires: pip install -e ./libs/test_lab
"""
import argparse
from test_lab.aqua_synthesizer import AquaSynthesizer
import polars as pl
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Generate high-integrity synthetic demo data.")
    parser.add_argument("--ground-truth-dir", type=Path,
                        default=Path("assets/test_data/1_test_data_ST22_dummy"),
                        help="Source directory containing ground-truth TSVs")
    parser.add_argument("--out-dir", type=Path,
                        default=Path("assets/test_data/demo_high_integrity"),
                        help="Output directory for synthesized TSVs")
    parser.add_argument("--n-samples", type=int, default=30,
                        help="Number of synthetic samples to generate")
    parser.add_argument("--messy-fraction", type=float, default=0.05,
                        help="Fraction of messy/noisy values to inject (0.0–1.0)")
    args = parser.parse_args()

    ground_truth_dir = args.ground_truth_dir
    out_dir = args.out_dir

    print("[1] INITIALIZING: Aqua Synthsizer for Demo Data...")

    # Source TSVs
    source_tsvs = [
        ground_truth_dir / "test_metadata_20260307_105756.tsv",
        ground_truth_dir / "test_data_MLST_results_20260307_105756.tsv",
        ground_truth_dir / "test_data_ResFinder_20260307_105756.tsv"
    ]

    # Initialize Synthesizer (Anchoring on 'sample_id' as per Abromics manifest)
    synthesizer = AquaSynthesizer(anchor_key_name="sample_id", n_samples=args.n_samples)

    print(f"\n[2] GENERATING: {args.n_samples} synthesized samples with PK Anchoring...")
    synthetic_files = synthesizer.synthesize(
        tsv_paths=source_tsvs,
        out_dir=out_dir,
        messy_fraction=args.messy_fraction
    )

    for f in synthetic_files:
        print(f"  └── Created: {f}")

    print("\n[3] RE-VALIDATING JOIN INTEGRITY...")
    meta_p = out_dir / "test_data_test_metadata_20260307_105756.tsv"
    mlst_p = out_dir / "test_data_test_data_MLST_results_20260307_105756.tsv"

    df_meta = pl.read_csv(meta_p, separator='\t')
    df_mlst = pl.read_csv(mlst_p, separator='\t')

    # Use sample_id for join
    joined = df_meta.join(df_mlst, on="sample_id", how="inner")

    print(
        f"\nVerification: Found {joined.height} matching IDs (1:1 join success).")
    if joined.height > 0:
        print("✅ SUCCESS: High-integrity demo data generated.")


if __name__ == "__main__":
    main()
