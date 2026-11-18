"""Every place of the app that draws a factory plot draws it through a checked call (VIZ-STANDARD-1, V7).

# @deps
# consumes: app/handlers/home_theater.py, app/modules/wrangle_studio.py, app/handlers/export_handlers.py, app/modules/gallery_examples.py, libs/viz_factory/src/viz_factory/checked_plot.py
# @end_deps

`VizFactory.render` returns a plot that plotnine draws later; a draw error then names no layer and, on a screen, escapes
the handler's `try`. A screen shows the error in the plot's place (`show_draw_errors`); a file is saved through
`plot.save`, which a factory plot already checks. A new caller of `render` that does neither fails here.
"""
import re
from pathlib import Path

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from app.modules.gallery_examples import render_example
from utils.errors import VisualizationError

ROOT = Path(__file__).resolve().parents[2]
CALL = re.compile(r"(viz_factory|VizFactory\(\))\.render\(")
SCREENS = ["app/handlers/home_theater.py", "app/modules/wrangle_studio.py"]
FILES = ["app/handlers/export_handlers.py", "app/modules/gallery_examples.py"]


def _calls(path: str):
    lines = (ROOT / path).read_text().splitlines()
    return [(i, lines) for i, line in enumerate(lines) if CALL.search(line) and not line.lstrip().startswith("#")]


@pytest.mark.parametrize("path", SCREENS)
def test_a_screen_shows_a_draw_error_in_the_plots_place(path):
    calls = _calls(path)
    assert calls, f"{path} no longer draws a factory plot: update this test"
    for i, lines in calls:
        assert "show_draw_errors(" in " ".join(lines[max(0, i - 2): i + 1]), f"{path}:{i + 1} draws a plot without show_draw_errors"


@pytest.mark.parametrize("path", FILES)
def test_a_file_is_saved_from_the_checked_plot(path):
    calls = _calls(path)
    assert calls, f"{path} no longer draws a factory plot: update this test"
    for i, lines in calls:
        assigned = re.match(r"\s*(\w+)\s*=\s*" + CALL.pattern, lines[i])
        assert assigned, f"{path}:{i + 1} does not keep the rendered plot in a variable"
        name = assigned.group(1)
        # WHY: other steps (the warnings of D-0269) may stand between render and save, so the window is 25 lines and the
        # property is that the SAME variable is saved: `<name>.save(`
        window = " ".join(lines[i: i + 25])
        assert f"{name}.save(" in window, f"{path}:{i + 1} renders a plot and does not save it with {name}.save"


def test_a_gallery_example_that_cannot_be_drawn_fails_in_the_one_form_and_leaves_no_picture(tmp_path, monkeypatch):
    import shutil

    work = tmp_path / "project"
    (work / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "gallery_data" / "bar_simple", work / "assets" / "gallery_data" / "bar_simple")
    for folder in ("config", "libs"):
        (work / folder).symlink_to(ROOT / folder)
    recipe = work / "assets" / "gallery_data" / "bar_simple" / "data_analysis_recipe.yaml"
    text = recipe.read_text()
    assert "{name: geom_bar, params: {}}" in text
    recipe.write_text(text.replace("{name: geom_bar, params: {}}", "{name: geom_bar, params: {size: big}}"))
    monkeypatch.chdir(work)
    with pytest.raises(VisualizationError) as error:
        render_example(Path("assets/gallery_data/bar_simple"), tmp_path / "work", tmp_path / "out.png")
    assert "layer " in str(error.value) and "(geom_bar)" in str(error.value) and "Fix:" in str(error.value)
    assert not (tmp_path / "out.png").exists()
