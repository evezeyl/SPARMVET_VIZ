#!/usr/bin/env python3
# @deps
# provides: script:debug_gallery
# consumes: libs/transformer/tests/debug_assembler.py (output: tmp/EVE_contracted_*.parquet), libs/viz_factory/src/viz_factory/viz_factory.py
# consumed_by: config/manifests/pipelines/*/README.md, assets/scripts/materialize_manifest_plots.py
# doc: .claude/rules/rules_persona_bioscientist.md#7
# @end_deps
"""
debug_gallery.py — Headless Art Audit for manifest-driven plots (ADR-032).

Pipeline:
  1. Run debug_assembler.py to materialise assembled data into tmp/.
  2. Run this script to render all plots from a manifest's analysis_groups.

Data lookup (in order):
  1. tmp/EVE_contracted_{target_dataset}.parquet  — contracted assembly output
  2. tmp/EVE_assembly_{target_dataset}.parquet    — pre-contract intermediate
  TSV fallbacks are not used for rendering; they exist only for human audit.

Output: PNG files in --output_root/{manifest_id}/{group_id}/{plot_id}.png
"""
import sys
import argparse
import polars as pl
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use('Agg')

try:
    from viz_factory.viz_factory import VizFactory
    from utils.config_loader import ConfigManager
except ImportError as e:
    print(f"❌ ERROR: Core imports failed. Check .venv install. {e}")
    sys.exit(1)

project_root = Path(__file__).resolve().parent.parent.parent.parent


def resolve_data(target_dataset: str, tmp_root: Path) -> pl.LazyFrame | None:
    """
    Locate contracted or intermediate parquet for a target dataset.
    Returns a LazyFrame or None if not found.
    """
    for stem in (f"EVE_contracted_{target_dataset}", f"EVE_assembly_{target_dataset}"):
        path = tmp_root / f"{stem}.parquet"
        if path.exists():
            print(f"      └── 📂 Data: {path.name}")
            return pl.scan_parquet(path)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Headless Art Audit — render all plots from a manifest (ADR-032)."
    )
    parser.add_argument("--manifest", type=str, required=True,
                        help="Path to the pipeline manifest (.yaml)")
    parser.add_argument("--output_root", type=str,
                        default=None,
                        help="Root directory for output PNGs (default: tmpAI/YYYY-MM-DD/<manifest>/plots/)")
    parser.add_argument("--tmp", type=str,
                        default=None,
                        help="Directory containing EVE_contracted_*.parquet files (default: tmpAI/YYYY-MM-DD/<manifest>/)")
    args = parser.parse_args()

    # Derive dated defaults from manifest stem — mirrors debug_assembler.py convention
    lineage_id = Path(args.manifest).stem
    date_str = datetime.now().strftime("%Y-%m-%d")
    dated_root = project_root / f"tmpAI/{date_str}/{lineage_id}"
    if args.tmp is None:
        args.tmp = str(dated_root)
    if args.output_root is None:
        args.output_root = str(dated_root / "plots")

    print(f"\n{'='*60}")
    print(f" 🖼️  DEBUG GALLERY — Headless Art Audit")
    print(f"{'='*60}\n")
    print(f"  Manifest : {args.manifest}")
    print(f"  Data root: {args.tmp}")
    print(f"  Output   : {args.output_root}\n")

    try:
        cm = ConfigManager(args.manifest)
        config = cm.raw_config
        manifest_id = config.get("id", "unknown_manifest")
    except Exception as e:
        print(f"❌ [FATAL] Failed to load manifest: {e}")
        sys.exit(1)

    factory = VizFactory()
    tmp_root = Path(args.tmp)
    output_root = Path(args.output_root)

    analysis_groups = config.get("analysis_groups", {})
    if not analysis_groups:
        print("⚠️  No 'analysis_groups' found in manifest. Nothing to render.")
        sys.exit(0)

    total = 0
    ok = 0
    failed = 0

    for group_id, group_config in analysis_groups.items():
        print(f"\n📂 [GROUP] {group_id}")
        plots = group_config.get("plots", {})
        group_dir = output_root / manifest_id / group_id
        group_dir.mkdir(parents=True, exist_ok=True)

        for plot_id, plot_entry in plots.items():
            total += 1
            spec = plot_entry.get("spec", {})
            target_dataset = spec.get("target_dataset")

            if not target_dataset:
                print(f"  └── ⚠️  {plot_id}: no target_dataset in spec, skipping.")
                failed += 1
                continue

            lf = resolve_data(target_dataset, tmp_root)
            if lf is None:
                print(
                    f"  └── ❌ {plot_id}: no data for '{target_dataset}' in {tmp_root}. "
                    f"Run debug_assembler.py first."
                )
                failed += 1
                continue

            print(f"  └── 🖌️  Rendering {plot_id}...")
            try:
                # Build a synthetic manifest fragment the VizFactory expects
                synthetic = {
                    "plots": {plot_id: spec},
                    "plot_defaults": config.get("plot_defaults", {})
                }
                p = factory.render(lf, synthetic, plot_id)
                out_path = group_dir / f"{plot_id}.png"
                p.save(out_path, width=10, height=6, dpi=150, verbose=False)
                print(f"      ✅ Saved: {out_path}")
                ok += 1
            except Exception as e:
                print(f"      ❌ {plot_id}: {e}")
                failed += 1

    print(f"\n{'='*60}")
    print(f" GALLERY COMPLETE — {ok}/{total} rendered, {failed} failed.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
