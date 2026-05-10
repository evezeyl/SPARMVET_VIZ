#!/usr/bin/env python3
"""
generate_previews.py — Headless gallery preview generator.

Reads each recipe_manifest.yaml + example_data.tsv under assets/gallery_data/
and renders a preview_plot.png using VizFactory.

Usage (from project root, with .venv active):
    .venv/bin/python libs/viz_gallery/assets/generate_previews.py
    .venv/bin/python libs/viz_gallery/assets/generate_previews.py --only beeswarm_sina ecdf
    .venv/bin/python libs/viz_gallery/assets/generate_previews.py --skip bar_simple

The first plot_id found in each manifest is rendered (should be one per recipe).
"""
import argparse
import sys
import matplotlib
matplotlib.use("Agg")

from pathlib import Path

import polars as pl
import yaml
from PIL import Image

project_root = Path(__file__).resolve().parent.parent.parent.parent

try:
    from viz_factory.viz_factory import VizFactory
except ImportError as e:
    print(f"❌ Cannot import VizFactory: {e}")
    print("   Run from project root with .venv active.")
    sys.exit(1)


def render_recipe(recipe_dir: Path, factory: VizFactory) -> bool:
    manifest_path = recipe_dir / "recipe_manifest.yaml"
    data_path = recipe_dir / "example_data.tsv"
    out_path = recipe_dir / "preview_plot.png"

    if not manifest_path.exists() or not data_path.exists():
        print(f"  ⚠️  {recipe_dir.name}: missing manifest or data — skipped")
        return False

    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        plots = manifest.get("plots", {})
        if not plots:
            print(f"  ⚠️  {recipe_dir.name}: no plots key in manifest — skipped")
            return False

        plot_id = next(iter(plots))
        df = pl.read_csv(data_path, separator="\t").lazy()

        p = factory.render(df, manifest, plot_id)
        p.save(out_path, width=8, height=5, dpi=120, verbose=False)

        thumb_path = recipe_dir / "preview_thumb.png"
        with Image.open(out_path) as img:
            img.thumbnail((100, 75), Image.LANCZOS)
            img.save(thumb_path)

        print(f"  ✅ {recipe_dir.name} → preview_plot.png + preview_thumb.png")
        return True

    except Exception as e:
        print(f"  ❌ {recipe_dir.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate gallery preview PNGs.")
    parser.add_argument("--gallery", default=str(project_root / "assets/gallery_data"),
                        help="Path to gallery_data directory (default: assets/gallery_data)")
    parser.add_argument("--only", nargs="+", metavar="RECIPE",
                        help="Only render these recipe names")
    parser.add_argument("--skip", nargs="+", metavar="RECIPE",
                        help="Skip these recipe names")
    parser.add_argument("--force", action="store_true",
                        help="Re-render even if preview_plot.png already exists")
    args = parser.parse_args()

    gallery_dir = Path(args.gallery)
    if not gallery_dir.exists():
        print(f"❌ Gallery directory not found: {gallery_dir}")
        sys.exit(1)

    factory = VizFactory()

    dirs = sorted([d for d in gallery_dir.iterdir() if d.is_dir()])
    if args.only:
        dirs = [d for d in dirs if d.name in args.only]
    if args.skip:
        dirs = [d for d in dirs if d.name not in args.skip]

    print(f"\n🖼️  Gallery Preview Generator")
    print(f"   Gallery : {gallery_dir}")
    print(f"   Recipes : {len(dirs)}\n")

    ok = failed = skipped = 0
    for d in dirs:
        out = d / "preview_plot.png"
        thumb = d / "preview_thumb.png"
        if out.exists() and thumb.exists() and not args.force:
            print(f"  ⏭️  {d.name}: already has preview_plot.png + preview_thumb.png (--force to overwrite)")
            skipped += 1
            continue
        # Re-render full plot if missing, or just generate thumb from existing full plot
        if out.exists() and not thumb.exists() and not args.force:
            with Image.open(out) as img:
                img.thumbnail((100, 75), Image.LANCZOS)
                img.save(thumb)
            print(f"  🖼️  {d.name}: generated missing preview_thumb.png from existing preview_plot.png")
            ok += 1
            continue
        if render_recipe(d, factory):
            ok += 1
        else:
            failed += 1

    print(f"\n{'='*50}")
    print(f"  Done: {ok} rendered, {failed} failed, {skipped} skipped")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
