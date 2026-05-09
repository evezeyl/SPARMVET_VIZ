# libs/utils/tests/debug_gallery_submission.py
import argparse
import polars as pl
from pathlib import Path
from viz_gallery.gallery_manager import GalleryManager


def run_debug(output_root: str):
    """
    Headless Audit for Gallery Submission Logic.
    Satisfies: rules_verification_testing.md CLI Mandate.
    """
    print("🚀 Starting Gallery Submission Headless Audit...")

    # 1. Setup Mock Gallery in tmp
    tmp_gallery = Path(output_root) / "gallery_vault"
    manager = GalleryManager(gallery_dir=str(tmp_gallery))

    # 2. Mock Data
    mock_data = pl.DataFrame({
        "Sample": ["S1", "S2", "S3"],
        "Value": [10.5, 20.1, 15.3],
        "Category": ["A", "B", "A"]
    })

    # 3. Mock Recipe
    mock_recipe = [
        {"action": "filter_eq", "column": "Category",
            "value": "A", "comment": "Audit test filtering"}
    ]

    # 4. Mock Metadata
    mock_meta = """# Recipe Meta: Debug Submission
## Family: Distribution
## Difficulty: Simple
- Tested via debug_gallery_submission.py
"""

    # 5. Execute Submission
    result_path = manager.submit_recipe(
        name="Debug Test Recipe",
        recipe=mock_recipe,
        data=mock_data,
        meta_markdown=mock_meta
    )

    print(f"✅ Materialized bundle to: {result_path}")

    # 6. Verification Trace
    bundle_dir = Path(result_path)
    print("\n📦 Bundle Contents:")
    for f in bundle_dir.iterdir():
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

    print("\n📊 Data Sample Glimpse:")
    saved_data = pl.read_csv(bundle_dir / "example_data.tsv", separator="\t")
    print(saved_data.glimpse())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Audit Gallery Submission Backend.")
    parser.add_argument("--output_root", type=str, default="tmp/Manifest_test/gallery_audit",
                        help="Root directory for materialized test artifacts.")
    args = parser.parse_args()

    Path(args.output_root).mkdir(parents=True, exist_ok=True)
    run_debug(args.output_root)
