#!/usr/bin/env python3
# @deps
# provides: script:figshare_plot_integration
# consumes: tmp/integration/figshare_join_check.tsv (written by assets/scripts/figshare_triple_integration.py), tmp/integration/ (writes plots)
# doc: assets/test_data/figshare.21737288/README.md
# @end_deps
"""
figshare_plot_integration.py
============================
Stage 3: Generate 3 integration plots from the materialized join.

Default source: tmp/integration/figshare_join_check.tsv

Plots:
  A - Phenotype distribution per antibiotic (R/S/I stacked bar)
  B - Resistance gene family counts per host animal
  C - Resistance class counts per host animal

HALT: Saves plots to --out-dir and awaits @verify.

Usage:
    ./.venv/bin/python assets/scripts/figshare_plot_integration.py
    ./.venv/bin/python assets/scripts/figshare_plot_integration.py \\
        --src-tsv tmp/integration/figshare_join_check.tsv \\
        --out-dir tmp/integration
"""

import argparse
import polars as pl
import pandas as pd
from pathlib import Path
from plotnine import (
    ggplot, aes, geom_bar, geom_col, labs, theme_bw,
    theme, element_text, element_blank,
    scale_fill_manual, scale_fill_brewer,
    coord_flip, facet_wrap, position_stack, position_dodge,
    scale_x_discrete, scale_y_continuous,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(
        description="Generate 3 integration plots from the materialized figshare join."
    )
    parser.add_argument(
        "--src-tsv", type=Path,
        default=PROJECT_ROOT / "tmp" / "integration" / "figshare_join_check.tsv",
        help="Path to the materialized join TSV (output of figshare_triple_integration.py)"
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=PROJECT_ROOT / "tmp" / "integration",
        help="Output directory for PNG plots"
    )
    args = parser.parse_args()

    src_tsv = args.src_tsv
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("STAGE 3: INTEGRATION PLOTS")
    print(f"  Source: {src_tsv}")
    print("="*60)

    # ---------------------------------------------------------------------------
    # Load
    # ---------------------------------------------------------------------------
    print("\n  Loading materialized join ...")
    df_full = pl.read_csv(src_tsv, separator="\t", infer_schema_length=10000)
    print(f"  Loaded: {df_full.shape[0]:,} rows × {df_full.shape[1]} cols")

    # ---------------------------------------------------------------------------
    # PLOT A: Phenotype distribution per antibiotic
    # Deduplicate to unique (sample_id × mic_id) to avoid gene-level explosion
    # ---------------------------------------------------------------------------
    print("\n  [Plot A] Phenotype per antibiotic ...")

    df_pheno = (
        df_full
        .select(["sample_id", "mic_id", "predicted_phenotype"])
        .unique()
        .to_pandas()
    )
    # Order antibiotics by total count for legibility
    mic_order = (
        df_pheno.groupby("mic_id")
        .size()
        .sort_values(ascending=False)
        .index.tolist()
    )
    df_pheno["mic_id"] = pd.Categorical(
        df_pheno["mic_id"], categories=mic_order, ordered=True)
    df_pheno["predicted_phenotype"] = pd.Categorical(
        df_pheno["predicted_phenotype"], categories=["R", "I", "S"], ordered=True)

    PHENO_COLORS = {"R": "#c0392b", "I": "#e67e22", "S": "#27ae60"}

    plot_A = (
        ggplot(df_pheno, aes(x="mic_id", fill="predicted_phenotype"))
        + geom_bar(position=position_stack(), width=0.8)
        + scale_fill_manual(values=PHENO_COLORS, name="Phenotype")
        + coord_flip()
        + labs(
            title="Phenotypic Resistance per Antibiotic",
            subtitle="Figshare AMR – Livestock E. coli (n=991 samples)",
            x="Antibiotic (MIC ID)",
            y="Sample Count",
        )
        + theme_bw()
        + theme(
            figure_size=(10, 7),
            plot_title=element_text(size=13, weight="bold"),
            plot_subtitle=element_text(size=10, color="#555555"),
            axis_text_y=element_text(size=8),
            axis_text_x=element_text(size=9),
            legend_position="right",
        )
    )

    out_A = out_dir / "plot_A_phenotype_per_antibiotic.png"
    plot_A.save(str(out_A), dpi=150, verbose=False)
    print(f"  → Saved: {out_A}")
    print(
        f"    Shape: {df_pheno.shape} | Unique mic_ids: {df_pheno['mic_id'].nunique()}")

    # ---------------------------------------------------------------------------
    # PLOT B: Resistance gene family per host animal
    # Deduplicate to unique (sample_id × gene_name_family × host_animal_common)
    # Filter: exclude empty/null gene_name_family (these are replicons Inc*)
    # ---------------------------------------------------------------------------
    print("\n  [Plot B] Gene family per host animal ...")

    df_geno = (
        df_full
        .select(["sample_id", "host_animal_common", "gene_name_family"])
        .unique()
        .filter(
            pl.col("gene_name_family").is_not_null() &
            (pl.col("gene_name_family").str.len_chars() > 0)
        )
        .to_pandas()
    )

    # Top 12 gene families by count for legibility
    top_families = (
        df_geno.groupby("gene_name_family")
        .size()
        .sort_values(ascending=False)
        .head(12)
        .index.tolist()
    )
    df_geno_top = df_geno[df_geno["gene_name_family"].isin(top_families)].copy()
    df_geno_top["gene_name_family"] = pd.Categorical(
        df_geno_top["gene_name_family"], categories=top_families, ordered=True
    )

    plot_B = (
        ggplot(df_geno_top, aes(x="gene_name_family", fill="host_animal_common"))
        + geom_bar(position=position_stack(), width=0.75)
        + scale_fill_brewer(type="qual", palette="Set2", name="Host Animal")
        + coord_flip()
        + labs(
            title="Top 12 Resistance Gene Families by Host Animal",
            subtitle="Figshare AMR – Livestock E. coli (gene-sample pairs, replicons excluded)",
            x="Gene Family",
            y="Gene–Sample Pair Count",
        )
        + theme_bw()
        + theme(
            figure_size=(10, 6),
            plot_title=element_text(size=13, weight="bold"),
            plot_subtitle=element_text(size=10, color="#555555"),
            axis_text_y=element_text(size=9),
            axis_text_x=element_text(size=9),
            legend_position="right",
        )
    )

    out_B = out_dir / "plot_B_gene_family_per_host.png"
    plot_B.save(str(out_B), dpi=150, verbose=False)
    print(f"  → Saved: {out_B}")
    print(
        f"    Shape: {df_geno_top.shape} | Unique families: {df_geno_top['gene_name_family'].nunique()}")

    # ---------------------------------------------------------------------------
    # PLOT C: Resistance class per host animal
    # Deduplicate to unique (sample_id × resistance_class × host_animal_common)
    # ---------------------------------------------------------------------------
    print("\n  [Plot C] Resistance class per host animal ...")

    df_class = (
        df_full
        .select(["sample_id", "host_animal_common", "resistance_class"])
        .unique()
        .filter(pl.col("resistance_class").is_not_null())
        .to_pandas()
    )

    # Order resistance classes by total count
    rc_order = (
        df_class.groupby("resistance_class")
        .size()
        .sort_values(ascending=False)
        .index.tolist()
    )
    df_class["resistance_class"] = pd.Categorical(
        df_class["resistance_class"], categories=rc_order, ordered=True
    )

    plot_C = (
        ggplot(df_class, aes(x="resistance_class", fill="host_animal_common"))
        + geom_bar(position=position_dodge(width=0.85), width=0.8)
        + scale_fill_brewer(type="qual", palette="Set2", name="Host Animal")
        + coord_flip()
        + labs(
            title="Resistance Class Distribution by Host Animal",
            subtitle="Figshare AMR – Livestock E. coli (unique sample–class pairs)",
            x="Resistance Class",
            y="Sample–Gene Count",
        )
        + theme_bw()
        + theme(
            figure_size=(10, 5),
            plot_title=element_text(size=13, weight="bold"),
            plot_subtitle=element_text(size=10, color="#555555"),
            axis_text_y=element_text(size=9),
            axis_text_x=element_text(size=9),
            legend_position="right",
        )
    )

    out_C = out_dir / "plot_C_resistance_class_per_host.png"
    plot_C.save(str(out_C), dpi=150, verbose=False)
    print(f"  → Saved: {out_C}")
    print(
        f"    Shape: {df_class.shape} | Unique classes: {df_class['resistance_class'].nunique()}")

    # ---------------------------------------------------------------------------
    # Summary glimpse
    # ---------------------------------------------------------------------------
    print("\n" + "="*60)
    print("STAGE 3 COMPLETE — Plots materialized:")
    print(f"  A: {out_A}")
    print(f"  B: {out_B}")
    print(f"  C: {out_C}")
    print("\nGlimpse of deduplicated phenotype data (Plot A source):")
    print(df_pheno.groupby("predicted_phenotype").size().to_string())
    print("\nGlimpse of gene families (Plot B source):")
    print(df_geno_top.groupby(["gene_name_family", "host_animal_common"]).size(
    ).reset_index().head(10).to_string())
    print("\n" + "="*60)
    print("🛑 HALT — Plots ready in:", out_dir)
    print("         Awaiting @verify before proceeding to tasks.md update.")
    print("="*60)


if __name__ == "__main__":
    main()
