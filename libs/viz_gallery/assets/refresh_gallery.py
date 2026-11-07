#!/usr/bin/env python3
# assets/scripts/refresh_gallery.py
"""
SPARMVET Gallery Refresh & Integrity Suite
ADR-037: Rebuilds the Pivot-Index and runs the Mandatory Triplet Audit.
"""
import sys
import argparse
from pathlib import Path

# Fix path for library access without sys.path.append (rely on editable install)
# But for a script in assets/scripts, we might need a little help if not in venv
from viz_gallery.gallery_manager import GalleryManager


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild SPARMVET Gallery Pivot-Index (Scientific Cookbook Engine)")
    parser.add_argument(
        "--path", default="assets/gallery_data", help="Path to gallery data directory (default: assets/gallery_data)"
    )
    args = parser.parse_args()

    print("--- 🔬 SPARMVET Gallery Integrity Audit ---")
    gallery_path = Path(args.path)
    if not gallery_path.exists():
        print(f"❌ Error: Gallery path '{gallery_path}' not found.")
        sys.exit(1)

    manager = GalleryManager(gallery_dir=str(gallery_path))

    # 1. Rebuild the Pivot-Index
    index = manager.rebuild_index()

    # 2. Report Findings
    print("\n--- 📊 Gallery Statistics ---")
    print(f"Total Valid Examples: {index['metadata']['count']}")

    pivot = index['pivot']
    print("\nTaxonomy Coverage:")
    for axis, groups in pivot.items():
        print(f"  {axis}: {list(groups.keys())}")

    print("\n✅ Refresh Complete. UI ready for Zero-Latency Filtering.")


if __name__ == "__main__":
    main()
