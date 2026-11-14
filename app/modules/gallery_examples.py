"""Gallery examples in the app layer: check them with the registries, and draw one through the app's own path.

A gallery example is a standard recipe (spec section 9). Two things need the app layer, because only this layer may
combine the libraries (rules_runtime_environment.md, Tier 3):

- `check_gallery`: the full check of every example, with the action and plot-component registries given to
  `check_recipe` as catalogs. It returns the accepted examples and the rejected ones with their reasons. The index
  rebuild, the tests and (decision DEC48) the check at app start call it.
- `render_example`: the picture of an example by the same path as HOME (ConfigManager, DataOrchestrator, VizFactory),
  so an example that the app could not load gets no picture (finding G2).

No Shiny import. App features gate: none here; the Gallery panel itself is gated by `gallery_enabled`.
If deleted: the examples are checked for structure only and the previews cannot be regenerated.

# @deps
# provides: function:recipe_catalogs, function:check_gallery, function:rebuild_gallery_index, function:render_example, function:example_table, constant:PREVIEW_SIZE
# consumes: libs/viz_gallery/src/viz_gallery/gallery_manager.py, app/modules/orchestrator.py, app/modules/cache_keys.py, libs/utils/src/utils/config_loader.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/viz_factory/src/viz_factory/arguments.py, libs/transformer/src/transformer/actions/base.py
# consumed_by: assets/scripts/refresh_gallery.py, assets/scripts/gallery_previews.py, app/tests/test_gallery_app_path.py
# doc: .claude/design/recipe_format_spec.md (section 9: G2, G3, D4, D5; section 14)
# @end_deps
"""
import contextlib
import io
import shutil
from pathlib import Path
from typing import Optional, Tuple, Union

import polars as pl

from viz_gallery.gallery_manager import RECIPE_FILE, Examples, GalleryManager
from viz_gallery.taxonomy import the_plot

# The one standard size of a preview picture (finding G5): 8 x 5 inches at 120 dots per inch, 960 x 600 pixels.
PREVIEW_SIZE = {"width": 8, "height": 5, "dpi": 120}


def recipe_catalogs() -> dict:
    """The registries as plain data for `check_recipe`: the actions, the plot components and their arguments, the themes."""
    import transformer.actions  # noqa: F401  (importing it registers the actions)
    import viz_factory  # noqa: F401  (importing it registers the plot components)
    from transformer.actions.base import ACTION_SCHEMAS
    from viz_factory.arguments import argument_catalog
    from viz_factory.registry import PLOT_COMPONENTS

    arguments = argument_catalog()
    components = set(PLOT_COMPONENTS)
    return {
        "actions": dict(ACTION_SCHEMAS),
        "components": components,
        "component_arguments": {name: (None if arguments.get(name) is None else set(arguments[name])) for name in components},
        "themes": {name for name in components if name.startswith("theme_")},
    }


def check_gallery(gallery_dir: Union[str, Path]) -> Examples:
    """Check every example of a gallery folder with the registries; returns the accepted and the rejected with reasons."""
    return GalleryManager(str(gallery_dir)).check_examples(recipe_catalogs())


def rebuild_gallery_index(gallery_dir: Union[str, Path]) -> dict:
    """Rebuild `gallery_index.json` from the examples that pass the full check; returns the index."""
    return GalleryManager(str(gallery_dir)).rebuild_index(recipe_catalogs())


def _build(example_dir: Path, work_dir: Path, project_root: Path) -> Tuple[dict, str, pl.LazyFrame]:
    """Load the example as the app loads a recipe and build the table its plot reads."""
    from app.modules.cache_keys import clear_data_analysis_recipe_cache
    from app.modules.orchestrator import DataOrchestrator
    from utils.config_loader import ConfigManager

    example_id = example_dir.name
    work_dir.mkdir(parents=True, exist_ok=True)
    # The app finds a recipe as <id>.yaml in its recipes folder; the id of an example is its folder name (GP04).
    recipe_path = work_dir / f"{example_id}.yaml"
    shutil.copyfile(example_dir / RECIPE_FILE, recipe_path)
    clear_data_analysis_recipe_cache()
    try:
        raw = ConfigManager(str(recipe_path)).raw_config
    except SystemExit as stop:
        raise ValueError(f"the app cannot load the recipe of the example {example_id} (the loader stopped with {stop.code})") from None
    plot = the_plot(raw)
    if plot is None:
        raise ValueError(f"the example {example_id} does not hold exactly one plot")
    plot_id, entry = plot
    orchestrator = DataOrchestrator(work_dir, project_root)
    keys = orchestrator.compute_data_analysis_recipe_keys(example_id)
    anchor = work_dir / f"{example_id}.parquet"
    target = entry["spec"]["target_dataset"]
    orchestrator.materialize_tier1(example_id, target, anchor, keys=keys)
    return raw, plot_id, orchestrator.materialize_tier2(example_id, target, anchor, keys=keys)


def example_table(example_dir: Union[str, Path], work_dir: Union[str, Path]) -> pl.DataFrame:
    """The table the plot of an example reads, built by the app's path (the source path is relative to the current folder)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return _build(Path(example_dir), Path(work_dir), Path("."))[2].collect()


def render_example(example_dir: Union[str, Path], work_dir: Union[str, Path], out_path: Union[str, Path],
                   size: Optional[dict] = None) -> Path:
    """Draw the plot of an example by the app's path and save it as a PNG; returns `out_path`.

    Run it from the project root: the data path of a recipe is relative to it. `work_dir` receives the copy of the
    recipe and the stored tables; nothing is written into the example folder unless `out_path` is inside it.
    `size` is `{width, height, dpi}`; without it the picture has the standard size (`PREVIEW_SIZE`). Another size is
    only for comparing with a picture that was drawn at that size.
    """
    import matplotlib
    matplotlib.use("Agg")
    from viz_factory.viz_factory import VizFactory

    out_path = Path(out_path)
    with contextlib.redirect_stdout(io.StringIO()):
        raw, plot_id, table = _build(Path(example_dir), Path(work_dir), Path("."))
        plot = VizFactory().render(table, raw, plot_id)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plot.save(out_path, verbose=False, **(size or PREVIEW_SIZE))
    return out_path
