"""GalleryManager: checks the gallery examples, builds the index the viewer reads, and writes a new example.

A gallery example is a folder of `assets/gallery_data/` holding a standard recipe (`data_analysis_recipe.yaml`, format
1), its data (`example_data.tsv`), its teaching text (`example_meta.md`) and its picture (`preview_plot.png`).

Every example is judged by the one checker of the format, `check_recipe` in the profile `gallery` (spec section 9,
DEC47 and DEC48). An example that fails is left out of the index and its reasons are returned and recorded in the
index, never dropped silently. The registries (actions, plot components) are not imported here: the caller passes them
as `catalogs`; without them only the structure is checked, and the coverage says so.

Consumed by: app/modules/gallery_examples.py (which passes the catalogs), assets/scripts/refresh_gallery.py.
No Shiny import. If deleted: `gallery_index.json` cannot be rebuilt and the gallery has no list of examples.

# @deps
# provides: class:GalleryManager (check_examples, rebuild_index, sync_index, submit_example (no screen or script calls it; only libs/viz_gallery/tests/test_gallery_bundle.py does, and example_recipe.py shares its form with convert_gallery_examples.py), list_submissions), class:Examples, constant:RECIPE_FILE
# consumes: libs/utils/src/utils/recipe_loader.py (check_recipe_file, load_recipe), libs/utils/src/utils/recipe_check.py (check_recipe), libs/utils/src/utils/legacy_keys.py, libs/viz_gallery/src/viz_gallery/taxonomy.py, libs/viz_gallery/src/viz_gallery/example_recipe.py
# consumed_by: app/modules/gallery_examples.py, assets/scripts/gallery_previews.py, assets/scripts/convert_gallery_examples.py, libs/viz_gallery/tests/test_gallery_bundle.py
# doc: .claude/design/recipe_format_spec.md (section 9)
# @end_deps
"""
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple

import polars as pl

from utils.legacy_keys import LEGACY_GALLERY_FILES
from utils.recipe_check import check_recipe
from utils.recipe_loader import check_recipe_file, load_recipe
from viz_gallery.example_recipe import DATA_FILE, data_contract, data_summary, dump_example, example_recipe, plot_summary
from viz_gallery.taxonomy import display_axes, example_taxonomy, tag_strip, with_tag_strip

RECIPE_FILE = "data_analysis_recipe.yaml"
META_FILE = "example_meta.md"
PREVIEW_FILE = "preview_plot.png"
THUMB_FILE = "preview_thumb.png"
INDEX_FILE = "gallery_index.json"
CONVERT_HINT = "python assets/scripts/convert_gallery_examples.py --only {name} --apply"


@dataclass(frozen=True)
class Examples:
    """What the check of a gallery folder found: the accepted examples and the rejected ones with their reasons."""
    accepted: Dict[str, dict]          # example id (the folder name) -> its recipe
    rejected: Dict[str, List[str]]     # example id -> why it is not shown, one text per problem
    coverage: FrozenSet[str]           # the groups of checks that ran: structure, actions, components


class GalleryManager:
    """GalleryManager (gallery_manager.py): the examples of one gallery folder."""

    def __init__(self, gallery_dir: str = "assets/gallery_data"):
        self.gallery_dir = Path(gallery_dir)
        self.gallery_dir.mkdir(parents=True, exist_ok=True)

    def list_submissions(self) -> List[str]:
        """The folder names of the gallery, sorted (every folder is an example, accepted or not)."""
        return sorted(d.name for d in self.gallery_dir.iterdir() if d.is_dir())

    def check_examples(self, catalogs: Optional[dict] = None) -> Examples:
        """Judge every example folder with `check_recipe` in the profile `gallery`; nothing is written.

        `catalogs` are the registries as plain data (see `utils.recipe_check`). Without them the actions and the
        plot components are not checked and `coverage` holds `structure` only.
        """
        accepted: Dict[str, dict] = {}
        rejected: Dict[str, List[str]] = {}
        coverage = {"structure"} | ({"actions"} if catalogs and "actions" in catalogs else set()) \
            | ({"components"} if catalogs and "components" in catalogs else set())
        for name in self.list_submissions():
            folder = self.gallery_dir / name
            recipe_path = folder / RECIPE_FILE
            if not recipe_path.is_file():
                if (folder / LEGACY_GALLERY_FILES[0]).exists():
                    rejected[name] = [f"the folder uses the old file names ({', '.join(LEGACY_GALLERY_FILES)}). "
                                      "Fix: python assets/scripts/migrate_config_vocabulary.py --gallery <folder> --apply"]
                else:
                    rejected[name] = [f"the folder has no {RECIPE_FILE}. Fix: add the recipe of the example, or remove the folder"]
                continue
            result = check_recipe_file(recipe_path, "gallery", file_stem=name, catalogs=catalogs)
            if "V01" in result.codes():
                rejected[name] = ["the example is in the old gallery form (no spec_version). Fix: "
                                  + CONVERT_HINT.format(name=name)]
            elif result.errors:
                rejected[name] = [problem.text() for problem in result.errors]
            else:
                accepted[name] = load_recipe(recipe_path)[0]
        return Examples(accepted=accepted, rejected=rejected, coverage=frozenset(coverage))

    def rebuild_index(self, catalogs: Optional[dict] = None) -> dict:
        """Check the examples and write `gallery_index.json`: the accepted examples and the pivot of the six axes.

        A rejected example is not in the registry; its reasons are in `metadata.rejected` and printed.
        """
        examples = self.check_examples(catalogs)
        registry: Dict[str, dict] = {}
        pivot: Dict[str, Dict[str, List[str]]] = {f"by_{item['axis']}": {} for item in display_axes()}
        for name, recipe in examples.accepted.items():
            folder = self.gallery_dir / name
            taxonomy = example_taxonomy(recipe)
            registry[name] = {
                "name": recipe["info"]["label"],
                "path": str(folder / RECIPE_FILE),
                "has_preview": (folder / PREVIEW_FILE).exists(),
                "has_thumb": (folder / THUMB_FILE).exists(),
                "taxonomy": taxonomy,
            }
            for axis, term in taxonomy.items():
                pivot[f"by_{axis}"].setdefault(term, []).append(name)
        index = {
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(registry),
                "coverage": sorted(examples.coverage),
                "rejected": examples.rejected,
            },
            "registry": registry,
            "pivot": pivot,
        }
        # Atomic write: a reader (or a second process starting) sees the old index or the new one, never half of it.
        target = self.gallery_dir / INDEX_FILE
        temporary = self.gallery_dir / f".{INDEX_FILE}.{os.getpid()}.tmp"
        try:
            with open(temporary, "w", encoding="utf-8") as handle:
                json.dump(index, handle, indent=2, ensure_ascii=False)
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()
        for name, reasons in examples.rejected.items():
            for reason in reasons:
                print(f"[gallery] {name} is left out of the index: {reason}")
        print(f"[gallery] index rebuilt: {len(registry)} example(s), {len(examples.rejected)} left out.")
        return index

    def sync_index(self, catalogs: Optional[dict] = None) -> Tuple[Examples, str]:
        """The check at app start (spec section 9, DEC48): the same check as the rebuild, the index rewritten only if it differs.

        Returns the check result and what happened to the index: `unchanged` (it already lists exactly the accepted
        examples and records the same rejections; the file is not touched), `rewritten` (by `rebuild_index`, the one
        function) or `not_writable` (the folder cannot be written, the old index stays and the caller must not trust it).
        """
        examples = self.check_examples(catalogs)
        index_path = self.gallery_dir / INDEX_FILE
        try:
            current = json.loads(index_path.read_text(encoding="utf-8"))
            if set(current["registry"]) == set(examples.accepted) and current["metadata"]["rejected"] == examples.rejected:
                return examples, "unchanged"
        except (OSError, ValueError, KeyError, TypeError):
            pass
        try:
            self.rebuild_index(catalogs)
        except OSError as error:
            print(f"[gallery] the index cannot be written ({error}); the gallery keeps the old list.")
            return examples, "not_writable"
        return examples, "rewritten"

    def submit_example(self, name: str, data: pl.DataFrame, meta_markdown: str, taxonomy: Dict[str, str],
                       plot_spec: dict, preview_path: str, description: str = "") -> str:
        """Write a new example folder as a standard recipe and return its path.

        The recipe is checked before anything is written: a wrong taxonomy term or plot specification raises
        `ValueError` with the reasons and leaves no folder. `taxonomy` holds the five typed axes; the geom is read
        from the layers. `preview_path` is the picture of the plot (rendered by the caller through the app's path);
        it is required because an example without its picture is not shown.
        """
        if not Path(preview_path).is_file():
            raise ValueError(f"the preview picture {preview_path} does not exist. Fix: render the plot and pass its PNG file")
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        if not slug or not slug[0].isalpha():
            raise ValueError(f"the name {name!r} gives no usable id. Fix: start the name with a letter")
        folder_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{slug}"
        target = self.gallery_dir / folder_name
        if self.gallery_dir.is_absolute():
            raise ValueError("the gallery folder is an absolute path, so the recipe could not name its data file. "
                             "Fix: give the gallery folder relative to the project root")
        sample = data.head(100)
        staging = self.gallery_dir / f".{folder_name}.writing"
        staging.mkdir(parents=True)
        try:
            sample.write_csv(staging / DATA_FILE, separator="\t")
            fields, _ = data_contract(staging / DATA_FILE)
            recipe = example_recipe(
                example_id=folder_name, label=name, description=description,
                data_path=f"./{(target / DATA_FILE).as_posix()}", fields=fields, taxonomy=taxonomy,
                plot_id=slug, plot_spec=plot_spec, data_description=data_summary(staging / DATA_FILE),
                plot_description=plot_summary(plot_spec), submission_date=datetime.now().strftime("%Y-%m-%d"))
            errors = check_recipe(recipe, "gallery", file_stem=folder_name).errors
            if errors:
                raise ValueError("the example is not a valid gallery recipe:\n" + "\n".join(problem.text() for problem in errors))
            (staging / RECIPE_FILE).write_text(dump_example(recipe), encoding="utf-8")
            (staging / META_FILE).write_text(with_tag_strip(meta_markdown, tag_strip(example_taxonomy(recipe))), encoding="utf-8")
            shutil.copy(preview_path, staging / PREVIEW_FILE)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        staging.rename(target)
        return str(target)
