# libs/viz_gallery/tests/debug_gallery_submission.py
import argparse
import subprocess
import polars as pl
import sys
from pathlib import Path
from viz_gallery.gallery_manager import GalleryManager


def run_headless_audit(data_analysis_recipe_path: str, data_dir: str, output_root: str):
    """
    Headless Audit for Gallery Submission (ADR-033).
    Strictly calls other library 'Engines' via CLI to maintain isolation.
    """
    print("Starting Gallery Submission Audit...")
    print(f"  - Data analysis recipe: {data_analysis_recipe_path}")
    print(f"  - Data Dir: {data_dir}")

    # 1. Pipeline Execution (Transformer Engine): debug_pipeline.py processes the data
    tmp_dir = Path(output_root)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    processed_parquet = tmp_dir / "processed_data.parquet"

    python_exe = sys.executable or "./.venv/bin/python"
    pipeline_script = "libs/transformer/tests/debug_pipeline.py"

    cmd = [
        python_exe, pipeline_script,
        "--data-analysis-recipe", data_analysis_recipe_path,
        "--data-dir", data_dir,
        "--output", str(processed_parquet),
        "--glimpse",
    ]

    print(f"Dispatching Transformer Engine: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Transformer Engine failed:\n{result.stderr}")
        sys.exit(result.returncode)

    print(result.stdout)

    # 2. Extract the example from the data analysis recipe (ConfigManager resolves the !include files)
    from utils.config_loader import ConfigManager
    data_analysis_recipe_data = ConfigManager(data_analysis_recipe_path).raw_config

    # Discovery logic for the example (ADR-024): the tier1 steps of the first join, or a
    # top-level 'wrangling' key.
    example = []
    if "wrangling" in data_analysis_recipe_data:
        example = data_analysis_recipe_data["wrangling"]
    elif "joins" in data_analysis_recipe_data:
        first_key = list(data_analysis_recipe_data["joins"].keys())[0]
        example = data_analysis_recipe_data["joins"][first_key].get("steps", [])

    # 3. Load the processed data
    df = pl.read_parquet(processed_parquet)

    # 4. Mock metadata (in the app this comes from the markdown editor)
    meta_md = f"""# Gallery Submission: {Path(data_analysis_recipe_path).stem}
## Automated Audit Trace
- **Source Data analysis recipe:** `{data_analysis_recipe_path}`
- **Source Data:** `{data_dir}`
- **Status:** Verified via debug_gallery_submission.py
"""

    # 5. Persist to the gallery
    gallery_vault = Path(output_root) / "gallery_vault"
    manager = GalleryManager(gallery_dir=str(gallery_vault))

    bundle_path = manager.submit_example(
        name=Path(data_analysis_recipe_path).stem,
        example=example,
        data=df,
        meta_markdown=meta_md,
    )

    print(f"Gallery Bundle materialized: {bundle_path}")

    # 6. Evidence verification
    bundle_dir = Path(bundle_path)
    print("\nBundle Contents Audit:")
    failed = False
    for f in bundle_dir.iterdir():
        status = "PASSED" if f.stat().st_size > 0 else "FAILED"
        failed = failed or status == "FAILED"
        print(f"  - [{status}] {f.name} ({f.stat().st_size} bytes)")

    print("\nGallery Sample Glimpse:")
    sample_tsv = bundle_dir / "example_data.tsv"
    pl.read_csv(sample_tsv, separator="\t").glimpse()
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Headless Gallery Submission Audit.")
    parser.add_argument("--data-analysis-recipe", required=True,
                        help="Path to the source data analysis recipe.")
    parser.add_argument("--data-dir", required=True,
                        help="Directory containing raw data.")
    parser.add_argument(
        "--output_root", default="tmpAI/gallery_audit", help="Results root (agent scratch by default).")

    args = parser.parse_args()
    run_headless_audit(args.data_analysis_recipe, args.data_dir, args.output_root)
