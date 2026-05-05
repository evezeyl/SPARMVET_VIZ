from test_lab.reconciler import KeyReconciler
import polars as pl
from pathlib import Path
import os
import sys
import argparse
import re

# Ensure we can import from src
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.


def main():
    parser = argparse.ArgumentParser(
        description="Demo script for Key Reconciler with evidence materialization.")
    parser.add_argument("--output_dir", default="tmp/reconciler",
                        help="Directory to save evidence TSVs.")
    args = parser.parse_args()

    print("[1] SETUP: Creating mock assets for reconciliation...")
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_file = out_dir / "metadata_ref.tsv"
    target_file = out_dir / "fastq_noisy.tsv"

    # Reference (Metadata)
    ref_df = pl.DataFrame({
        "sample_id": ["SAM001", "SAM002", "SAM003", "SAM004", "SAM005"],
        "species": ["E. coli", "E. coli", "S. enterica", "K. pneumoniae", "E. coli"]
    })
    ref_df.write_csv(ref_file, separator='\t')

    # Target (Noisy Analytical Data)
    target_df = pl.DataFrame({
        "sample_id": [
            "SAM001_L001_R1_001.fastq.gz",
            "SAM002_L001_R1_001.fastq.gz",
            "SAM003_L002_R1_001.fastq.gz",
            "UNKN_L001_R1_001.fastq.gz",
            "SAM005_v2.fastq.gz"
        ],
        "read_count": [1500000, 2100000, 500000, 1000000, 3000000]
    })
    target_df.write_csv(target_file, separator='\t')

    # [2] EXECUTING RECONCILER
    print("\n[2] EXECUTING RECONCILER...")

    reconciler = KeyReconciler()
    report = reconciler.reconcile(ref_df, target_df, ["sample_id"])

    regex = report["sample_id"]["suggested_regex"]
    print(f"  Generated Regex: {regex}")

    # [3] MATERIALIZE MATCH RESULTS
    print("\n[3] MATERIALIZING MATCH STATUS...")

    # Prepare match results table
    match_list = []
    ref_keys = set(ref_df["sample_id"].to_list())

    for original in target_df["sample_id"].to_list():
        # Apply the suggested regex
        match = re.search(regex, original)
        extracted = match.group(1) if match else "ID_NOT_FOUND"
        status = "MATCH" if extracted in ref_keys else "MISS"
        match_list.append({
            "Original_Key": original,
            "Extracted_Key": extracted,
            "Match_Status": status
        })

    results_df = pl.DataFrame(match_list)
    results_file = out_dir / "match_results.tsv"
    results_df.write_csv(results_file, separator='\t')

    # [4] OUTPUT SUMMARY
    print("\n" + "="*60)
    print("      RECONCILIATION EVIDENCE (PREVIEW)")
    print("="*60)
    print(results_df.head(5))
    print("="*60)

    print(f"\nEvidence files materialized in: {out_dir}")
    print(f"  └── {ref_file.name}")
    print(f"  └── {target_file.name}")
    print(f"  └── {results_file.name}")

    # [5] PROVE SUCCESS
    print("\n[4] RE-VALIDATING JOIN INTEGRITY...")
    clean_target = target_df.with_columns(
        pl.col("sample_id").str.extract(regex).alias("sample_id")
    )
    joined = ref_df.join(clean_target, on="sample_id", how="inner")

    print(f"Final Join Match Rate: {joined.height} / {ref_df.height} samples.")
    if joined.height >= 4:
        print("✅ RECONCILIATION HOMOGENIZATION SUCCESSFUL.")


if __name__ == "__main__":
    main()
