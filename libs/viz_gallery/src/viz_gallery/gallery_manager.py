# @deps
# provides: GalleryManager class — submit_recipe(), list_submissions(), rebuild_index(); manages gallery bundle persistence and Pivot-Index generation to assets/gallery_data/
# consumes: yaml, shutil, pathlib.Path, datetime, polars, json, hashlib
# consumed_by: app/handlers/gallery_handlers.py
# @end_deps
# libs/viz_gallery/src/viz_gallery/gallery_manager.py
import yaml
import shutil
from pathlib import Path
from datetime import datetime
import polars as pl
import json
import hashlib


class GalleryManager:
    """
    GalleryManager (gallery_manager.py) – part of the viz_gallery library.
    Handles persistence of a recipe, data sample, and metadata to the
    assets/gallery_data directory.
    """

    def __init__(self, gallery_dir: str = "assets/gallery_data"):
        self.gallery_dir = Path(gallery_dir)
        self.gallery_dir.mkdir(parents=True, exist_ok=True)

    def submit_recipe(self, name: str, recipe: list, data: pl.DataFrame,
                      meta_markdown: str, family: str = "Distribution",
                      pattern: str = "1 Numeric", difficulty: str = "Simple",
                      geom: str = "", show: str = "", sample_size: str = "any",
                      plot_config: dict = None,
                      plot_source_path: str = None) -> str:
        """Create a standardized gallery bundle.
        Returns the absolute path to the created bundle directory.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = name.lower().replace(" ", "_")
        folder_name = f"{ts}_{safe_name}"
        target_dir = self.gallery_dir / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save recipe manifest (YAML)
        manifest_bundle = {
            "info": {
                "name": name,
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "family": family,
                "pattern": pattern,
                "difficulty": difficulty,
                "geom": geom,
                "show": show,
                "sample_size": sample_size,
            },
            "data_path": "example_data.tsv",
            "plots": {
                safe_name: plot_config or {}
            },
            "wrangling": {
                "tier1": [],
                "tier2": [],
                "tier3": recipe
            }
        }
        with open(target_dir / "recipe_manifest.yaml", "w") as f:
            yaml.dump(manifest_bundle, f, sort_keys=False)

        # 2. Save data sample (TSV) – limit to 100 rows for preview
        data.head(100).write_csv(
            target_dir / "example_data.tsv", separator="\t")

        # 3. Save metadata markdown
        with open(target_dir / "recipe_meta.md", "w") as f:
            f.write(meta_markdown)

        # 4. Optional plot preview
        if plot_source_path and Path(plot_source_path).exists():
            shutil.copy(plot_source_path, target_dir / "preview_plot.png")

        return str(target_dir)

    def list_submissions(self):
        """Return a list of existing gallery bundle folder names."""
        return [d.name for d in self.gallery_dir.iterdir() if d.is_dir()]

    def rebuild_index(self) -> dict:
        """
        Scans all gallery bundles, performs the "Scientific Triplet" check,
        and generates a Pivot-Index (Cross-Reference Matrix).
        Saves to assets/gallery_data/gallery_index.json.
        """
        index_path = self.gallery_dir / "gallery_index.json"
        registry = {}
        pivot = {
            "by_family": {},
            "by_pattern": {},
            "by_difficulty": {},
            "by_geom": {},
            "by_show": {},
            "by_sample_size": {},
        }

        folders = [d for d in self.gallery_dir.iterdir() if d.is_dir()]
        for d in folders:
            manifest_path = d / "recipe_manifest.yaml"
            if not manifest_path.exists():
                continue

            # Integrity Check (ADR-037): manifest + data + meta required;
            # preview_plot.png is optional (gallery UI shows a placeholder when absent)
            required = {
                "manifest": manifest_path.exists(),
                "data": (d / "example_data.tsv").exists(),
                "meta": (d / "recipe_meta.md").exists(),
            }

            if not all(required.values()):
                print(f"⚠️ Skipping {d.name}: Missing required files {required}")
                continue

            if not (d / "preview_plot.png").exists():
                print(f"ℹ️  {d.name}: no preview_plot.png — will show placeholder in gallery")

            with open(manifest_path, "r") as f:
                try:
                    manifest = yaml.safe_load(f)
                    info = manifest.get("info", {})
                    recipe_id = d.name

                    # Store in Registry
                    registry[recipe_id] = {
                        "name": info.get("name", d.name),
                        "path": str(manifest_path),
                        "has_preview": (d / "preview_plot.png").exists(),
                        "has_thumb": (d / "preview_thumb.png").exists(),
                        "taxonomy": {
                            "family": info.get("family", "Unknown"),
                            "pattern": info.get("pattern", "Unknown"),
                            "difficulty": info.get("difficulty", "Simple"),
                            "geom": info.get("geom", ""),
                            "show": info.get("show", ""),
                            "sample_size": info.get("sample_size", "any"),
                        }
                    }

                    # Update Pivot Sets
                    f_val = info.get("family", "Unknown")
                    p_val = info.get("pattern", "Unknown")
                    d_val = info.get("difficulty", "Simple")
                    g_val = info.get("geom", "")
                    s_val = info.get("show", "")
                    ss_val = info.get("sample_size", "any")

                    pivot["by_family"].setdefault(f_val, []).append(recipe_id)
                    pivot["by_pattern"].setdefault(p_val, []).append(recipe_id)
                    pivot["by_difficulty"].setdefault(d_val, []).append(recipe_id)
                    if g_val:
                        pivot["by_geom"].setdefault(g_val, []).append(recipe_id)
                    if s_val:
                        pivot["by_show"].setdefault(s_val, []).append(recipe_id)
                    if ss_val:
                        pivot["by_sample_size"].setdefault(ss_val, []).append(recipe_id)

                except Exception as e:
                    print(f"❌ Failed to parse {d.name}: {e}")
                    continue

        full_index = {
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(registry)
            },
            "registry": registry,
            "pivot": pivot
        }

        with open(index_path, "w") as f:
            json.dump(full_index, f, indent=2)

        print(f"✅ Pre-Computed Pivot-Index rebuilt: {len(registry)} items.")
        return full_index
