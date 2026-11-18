"""The export draws each plot with the plot engine its entry or its recipe names, and an engine the app has no library for is
told in the bundle, never drawn by the other engine (D-0219, D-0239, D-0050).

The real generator of `export_bundle_download` runs without a browser (the harness of `test_export_download_path.py`) on a real
orchestrator and a real tiny recipe. A plot whose entry writes `plot_engine: r-ggplot2`, or a recipe that writes it at the top,
is not drawn: the bundle holds `plots/<plot>_ERROR.txt` with the decided words and no picture of that plot. The control draws it.

# @deps
# consumes: app/handlers/export_handlers.py, app/modules/engine_registry.py, app/tests/test_export_download_path.py, app/tests/test_cache_chain.py
# doc: .claude/knowledge/decision_ledger.md (D-0219, D-0239, D-0050)
# @end_deps
"""
import io
import zipfile

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import World
from app.tests.test_export_download_path import _download_function, _fresh_cache, _run  # noqa: F401  (the autouse fixture too)

WORDS = "no library for this engine in this app"


def bundle(tmp_path, monkeypatch, edit=None):
    world = World(tmp_path)
    if edit:
        recipe = world.data_analysis_recipes_dir / "tiny.yaml"
        text = recipe.read_text()
        changed = edit(text)
        assert changed != text, "the edit changed nothing: the test would prove nothing"
        recipe.write_text(changed)
        clear_data_analysis_recipe_cache()
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch))
    archive = zipfile.ZipFile(io.BytesIO(yielded[0]))
    return archive, {n.rsplit("/", 1)[-1]: n for n in archive.namelist()}


def test_the_control_draws_the_plot_with_the_engine_of_the_recipe(tmp_path, monkeypatch):
    archive, names = bundle(tmp_path, monkeypatch)
    assert "p.png" in names and "p_ERROR.txt" not in names


@pytest.mark.parametrize("name, edit", [
    ("the plot entry writes its own engine", lambda text: text.replace("        target_dataset: C\n", "        plot_engine: r-ggplot2\n        target_dataset: C\n")),
    ("the recipe writes it at the top", lambda text: text.replace("plot_engine: python-plotnine\n", "plot_engine: r-ggplot2\n")),
])
def test_a_plot_engine_the_app_has_no_library_for_is_told_in_the_bundle_and_the_plot_is_not_drawn(tmp_path, monkeypatch, name, edit):
    archive, names = bundle(tmp_path, monkeypatch, edit)
    assert "p.png" not in names, "drawn by another engine"
    stub = archive.read(names["p_ERROR.txt"]).decode()
    assert WORDS in stub and "r-ggplot2" in stub and "python-plotnine" in stub and "Plot 'p'" in stub


def test_a_plot_that_names_the_engine_the_recipe_writes_is_drawn(tmp_path, monkeypatch):
    archive, names = bundle(tmp_path, monkeypatch,
                            lambda text: text.replace("        target_dataset: C\n", "        plot_engine: python-plotnine\n        target_dataset: C\n"))
    assert "p.png" in names
