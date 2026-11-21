#!/usr/bin/env python3
# engine: python-polars (a script that reads and joins downloaded tables with Polars)
# @deps
# provides: script:figshare_triple_integration
# consumes: assets/test_data/figshare.21737288/csv/, libs/transformer/tests/data/ (writes TSVs), tmp/integration/ (writes join output)
# doc: assets/test_data/figshare.21737288/README.md
# @end_deps
"""
figshare_triple_integration.py
==============================
Stage 1 + Stage 2 of the Figshare AMR Triple-Source Integration pipeline.

Stage 1: Converts CSV sources to TSV and moves to transformer test data dir.
Stage 2: Performs a 3-way left join (metadata anchor → phenotypes → genotypes)
         and materializes the joined LazyFrame to tmp/ for @verify.

The join uses sample_id as the key. host_animal_common is pre-dropped from
genotypes to prevent column collision with metadata.

Usage:
    ./.venv/bin/python assets/scripts/figshare_triple_integration.py
    ./.venv/bin/python assets/scripts/figshare_triple_integration.py \\
        --csv-dir assets/test_data/figshare.21737288/csv \\
        --tsv-dir libs/transformer/tests/data \\
        --out-dir tmp/integration
"""

import argparse
import polars as pl
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "SPARMVET_VIZ Figshare Triple-Source Integration (Stages 1+2). "
            "Converts fg_metadata.csv, fg_phenotypes.csv, fg_genotypes.csv to TSV, "
            "then performs a 3-way left join on sample_id. "
            "Materializes the join to tmp/integration/figshare_join_check.tsv for @verify."
        )
    )
    parser.add_argument(
        "--csv-dir",
        default="assets/test_data/figshare.21737288/csv",
        help="Directory containing source CSV files (default: assets/test_data/figshare.21737288/csv)",
    )
    parser.add_argument(
        "--tsv-dir",
        default="libs/transformer/tests/data",
        help="Destination directory for normalized TSV files (default: libs/transformer/tests/data)",
    )
    parser.add_argument(
        "--out-dir",
        default="tmp/integration",
        help="Output directory for the join check TSV (default: tmp/integration)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    csv_dir = Path(args.csv_dir)
    tsv_dest = Path(args.tsv_dir)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    tsv_dest.mkdir(parents=True, exist_ok=True)

    sources = {
        "fg_metadata":   "fg_metadata.csv",
        "fg_phenotypes": "fg_phenotypes.csv",
        "fg_genotypes":  "fg_genotypes.csv",
    }

    # ---------------------------------------------------------------------------
    # STAGE 1: CSV → TSV
    # ---------------------------------------------------------------------------
    print("\n" + "="*60)
    print("STAGE 1: CSV → TSV NORMALIZATION")
    print("="*60)

    lazy_frames = {}
    for key, fname in sources.items():
        src = csv_dir / fname
        dst = tsv_dest / fname.replace(".csv", ".tsv")
        print(f"\n  [{key}] Reading {src.name} ...")
        df = pl.scan_csv(src, separator=",",
                         infer_schema_length=5000).collect()
        df.write_csv(dst, separator="\t")
        print(f"  → Written: {dst} ({df.shape[0]} rows × {df.shape[1]} cols)")
        lazy_frames[key] = pl.scan_csv(
            dst, separator="\t", infer_schema_length=5000)

    print("\n  [DONE] TSV files in:", tsv_dest)

    # ---------------------------------------------------------------------------
    # STAGE 1b: Column pre-processing & collision guard
    # ---------------------------------------------------------------------------
    print("\n" + "="*60)
    print("STAGE 1b: PRE-PROCESSING & COLLISION GUARD")
    print("="*60)

    lf_meta = (
        lazy_frames["fg_metadata"]
        .with_columns([
            pl.col("host_animal_common").cast(pl.Categorical),
            pl.col("animal_infection_site_uti").cast(pl.Categorical),
        ])
        .select(["sample_id", "host_animal_common", "specimen_source_tissue", "animal_infection_site_uti"])
    )

    lf_pheno = lazy_frames["fg_phenotypes"].with_columns([
        pl.col("mic_id").cast(pl.Categorical),
        pl.col("breakpoint").cast(pl.Categorical),
        pl.col("phenotype").cast(pl.Categorical),
    ])

    lf_geno = (
        lazy_frames["fg_genotypes"]
        # Collision guard: comes from metadata after join
        .drop("host_animal_common")
        .with_columns([
            pl.col("gene_name_family").str.strip_chars().cast(pl.Categorical),
            pl.col("resistance_class").str.strip_chars().cast(pl.Categorical),
        ])
        .select(["sample_id", "gene", "gene_name_family", "resistance_class"])
    )

    print(f"  Genotype columns after drop: {lf_geno.columns}")

    # ---------------------------------------------------------------------------
    # STAGE 2: 3-WAY LEFT JOIN
    # ---------------------------------------------------------------------------
    print("\n" + "="*60)
    print("STAGE 2: 3-WAY LEFT JOIN")
    print("  Anchor: fg_metadata → fg_phenotypes → fg_genotypes ON sample_id")
    print("="*60)

    lf_joined = lf_meta.join(lf_pheno, on="sample_id", how="left")
    lf_joined = lf_joined.join(lf_geno, on="sample_id", how="left")

    print("\n  Collecting join...")
    df_full = lf_joined.collect()

    out_path = out_dir / "figshare_join_check.tsv"
    df_full.write_csv(out_path, separator="\t")

    print(
        f"\n  Total shape: {df_full.shape[0]:,} rows × {df_full.shape[1]} cols")
    print(f"  Written to:  {out_path}\n")

    for col in df_full.columns:
        s = df_full[col]
        sample = s.drop_nulls().head(3).to_list()
        print(
            f"  {col:<35} dtype={str(s.dtype):<20} n_null={s.null_count():<5} sample={sample}")

    print(f"\n  Unique sample_ids:       {df_full['sample_id'].n_unique()}")
    print(
        f"  Unique host_animal:      {df_full['host_animal_common'].n_unique()}")
    if 'mic_id' in df_full.columns:
        print(f"  Unique mic_ids:          {df_full['mic_id'].n_unique()}")
    if 'resistance_class' in df_full.columns:
        print(
            f"  Unique resistance_class: {df_full['resistance_class'].n_unique()}")

    print("\n" + "="*60)
    print(f"🛑 HALT — Data ready at: {out_path}")
    print("         Waiting for @verify before proceeding to Stage 3 (plots).")
    print("="*60)


if __name__ == "__main__":
    main()
