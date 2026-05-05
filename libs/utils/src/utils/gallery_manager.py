# libs/utils/src/utils/gallery_manager.py
# @deps
# provides: class:GalleryManager
# consumed_by: app/handlers/gallery_handlers.py, libs/viz_factory/tests/debug_gallery.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-033, .claude/knowledge/architecture_decisions.md#ADR-035
# @end_deps
import yaml
import shutil
from pathlib import Path
from datetime import datetime
import polars as pl


class GalleryManager:
    """
    GalleryManager (gallery_manager.py)
    Handles the persistence of recipes, data samples, and plot evidence 
    to the assets/gallery_data/ directory.

    Architectural Context: ADR-033 / ADR-035.
    """

    def __init__(self, gallery_dir: str = "assets/gallery_data"):
        self.gallery_dir = Path(gallery_dir)
        if not self.gallery_dir.exists():
            # In a real app, this should already exist as per project conventions
            self.gallery_dir.mkdir(parents=True, exist_ok=True)

    def submit_recipe(self,
                      name: str,
                      recipe: list,
                      data: pl.DataFrame,
                      meta_markdown: str,
                      plot_source_path: str = None) -> str:
        """
        Creates a standardized gallery bundle folder.

        Mandatory File Triplet:
        1. recipe_manifest.yaml
        2. example_data.tsv
        3. recipe_meta.md
        (Optional) preview_plot.png

        Returns the path to the created directory.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = name.lower().replace(" ", "_")
        folder_name = f"{ts}_{safe_name}"
        target_dir = self.gallery_dir / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save Recipe (YAML)
        # We wrap the logic stack into a standard manifest structure
        manifest_bundle = {
            "info": {
                "name": name,
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
            },
            "wrangling": {
                "tier3": recipe
            }
        }

        with open(target_dir / "recipe_manifest.yaml", "w") as f:
            yaml.dump(manifest_bundle, f, sort_keys=False)

        # 2. Save Data Sample (TSV) - Max 100 rows for gallery preview
        data.head(100).write_csv(
            target_dir / "example_data.tsv", separator="\t")

        # 3. Save Metadata (MD)
        with open(target_dir / "recipe_meta.md", "w") as f:
            f.write(meta_markdown)

        # 4. Save Plot Preview (PNG)
        if plot_source_path and Path(plot_source_path).exists():
            shutil.copy(plot_source_path, target_dir / "preview_plot.png")

        return str(target_dir)

    def list_submissions(self):
        """Discovers existing gallery bundles."""
        return [d.name for d in self.gallery_dir.iterdir() if d.is_dir()]
