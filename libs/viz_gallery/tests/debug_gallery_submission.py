# libs/viz_gallery/tests/debug_gallery_submission.py
import argparse
import subprocess
import yaml
import polars as pl
import sys
from pathlib import Path
from viz_gallery.gallery_manager import GalleryManager


def run_headless_audit(manifest_path: str, data_dir: str, output_root: str):
    """
    Headless Audit for Gallery Submission (ADR-033).
    Strictly calls other library 'Engines' via CLI to maintain isolation.
    """
    print(f"🚀 Starting Gallery Submission Audit...")
    print(f"  - Manifest: {manifest_path}")
    print(f"  - Data Dir: {data_dir}")


Antigravity Toolkit
# 1. Pipeline Execution (Transformer Engine)
# We call debug_pipeline.py to process the data
tmp_dir = Path("tmp/gallery_audit")
tmp_dir.mkdir(parents=True, exist_ok=True)
processed_parquet = tmp_dir / "processed_data.parquet"

python_exe = sys.executable or "./.venv/bin/python"
pipeline_script = "libs/transformer/tests/debug_pipeline.py"

cmd = [
     python_exe, pipeline_script,
     "--manifest", manifest_path,
      "--data-dir", data_dir,
     "--output", str(processed_parquet),
        "--glimpse"
     ]

 print(f"📡 Dispatching Transformer Engine: {' '.join(cmd)}")
  result = subprocess.run(cmd, capture_output=True, text=True)

   if result.returncode != 0:
        print(f"❌ Transformer Engine failed:\n{result.stderr}")
        return

    print(result.stdout)

    # 2. Extract Recipe from Manifest
    with open(manifest_path, "r") as f:
        manifest_data = yaml.safe_load(f)

    # Discovery logic for recipe (ADR-024)
    # If it's a project manifest, it might be in join_manifests.
    # We'll take the first one found or a 'wrangling' key.
    recipe = []
    if "wrangling" in manifest_data:
        recipe = manifest_data["wrangling"]
    elif "join_manifests" in manifest_data:
        first_key = list(manifest_data["join_manifests"].keys())[0]
        recipe = manifest_data["join_manifests"][first_key].get(
            "recipe", [])

    # 3. Load Processed Data
    df = pl.read_parquet(processed_parquet)

    # 4. Mock Metadata (In actual UI, this is from the MD editor)
    meta_md = f"""# Gallery Submission: {Path(manifest_path).stem}
## Automated Audit Trace
- **Source Manifest:** `{manifest_path}`
- **Source Data:** `{data_dir}`
- **Status:** Verified via debug_gallery_submission.py
"""

    # 5. Persist to Gallery
    gallery_vault = Path(output_root) / "gallery_vault"
    manager = GalleryManager(gallery_dir=str(gallery_vault))

    bundle_path = manager.submit_recipe(
        name=Path(manifest_path).stem,
        recipe=recipe,
        data=df,
        meta_markdown=meta_md
    )

    print(f"✅ Gallery Bundle materialized: {bundle_path}")

    # 6. Evidence Verification
    bundle_dir = Path(bundle_path)
    print("\n📦 Bundle Contents Audit:")
    for f in bundle_dir.iterdir():
        status = "PASSED" if f.stat().st_size > 0 else "FAILED"
        print(f"  - [{status}] {f.name} ({f.stat().st_size} bytes)")

    print("\n📊 Gallery Sample Glimpse:")
    sample_tsv = bundle_dir / "example_data.tsv"
    print(pl.read_csv(sample_tsv, separator="\t").glimpse())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Headless Gallery Submission Audit.")
    parser.add_argument("--manifest", required=True,
                        help="Path to the source manifest.")
    parser.add_argument("--data-dir", required=True,
                        help="Directory containing raw data.")
    parser.add_argument(
        "--output_root", default="tmp/Manifest_test/gallery_audit", help="Results root.")

    args = parser.parse_args()
    run_headless_audit(args.manifest, args.data_dir, args.output_root)
