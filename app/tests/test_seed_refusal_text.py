"""A refused seed is told to the user in the one error form, with the fix, where the user looks (SEED-HOLDS-1, S1).

`random_state: null`, the word random and any text that is not a whole number are refused (Eve, 2026-11-15: every seed
that is used is written). Three places show it, and each must say the problem AND the fix:

- the plot factory raises one `VisualizationError` built by `plot_failure()`: "Plot 'p', layer 1 (geom_point): ... Fix: ...";
- HOME draws "Render error:" + that message in the plot's place, and the Blueprint preview shows "Render error: " + the same
  message (both handlers interpolate the exception text; a test below reads them so a change of that line is seen);
- a recipe that writes it does not pass the load gate: HOME lists it among the rejected recipes with the checker's problem
  and its tip (`rejected_recipe_text`), and Blueprint's Validate shows the same problems.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_seed_refusal_text.py -q
"""
import re
from pathlib import Path

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from app.modules.data_analysis_recipe_validator import rejected_recipe_text, validate_data_analysis_recipe
from app.tests.tiny_recipe import tiny_recipe, write_tiny
from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory

ROOT = Path(__file__).resolve().parents[2]
TABLE = pl.DataFrame({"g": ["a", "b", "a", "b"], "v": [1.0, 2.0, 3.0, 4.0]})


def refusal(layers, plot_defaults=None) -> VisualizationError:
    recipe = {"plots": {"p": {"mapping": {"x": "g", "y": "v"}, "layers": layers}}, "plot_defaults": plot_defaults or {}}
    with pytest.raises(VisualizationError) as raised:
        VizFactory().render(TABLE, recipe, "p")
    return raised.value


@pytest.mark.parametrize("written", [None, "random", "abc", 1.5])
def test_the_factory_says_plot_layer_problem_and_fix_in_the_one_form(written):
    error = refusal([{"name": "geom_point", "params": {"position": "jitter", "random_state": written}}])
    text = str(error)
    assert re.match(r"^Plot 'p', layer 1 \(geom_point\): random_state is .*, but a seed is a number\. Fix: write a number: random_state: 0", text), text
    assert error.tip.startswith("write a number: random_state: 0") and "Fix:" not in error.tip
    assert error.pipeline_error.who == "data_analysis_recipe_author" and error.pipeline_error.surface == "plot_overlay"


def test_the_layer_is_named_by_its_place_in_the_recipe():
    layers = [{"name": "geom_point"}, {"name": "geom_sina", "params": {"random_state": None}}]
    assert "layer 2 (geom_sina)" in str(refusal(layers))


def test_a_refused_recipe_default_names_plot_defaults():
    text = str(refusal([{"name": "geom_point", "params": {"position": "jitter"}}], {"random_state": None}))
    assert text.startswith("Plot 'p', plot_defaults: random_state is None, but a seed is a number. Fix: write a number")


def screen_text(source: Path, marker: str) -> str:
    """The lines of a screen handler around the text it draws for a render error."""
    lines = source.read_text().splitlines()
    i = next(n for n, line in enumerate(lines) if marker in line)
    return "\n".join(lines[max(0, i - 6): i + 3])


def test_home_and_blueprint_show_the_whole_message_of_a_render_error():
    """Both screens draw the exception text itself (`{e}` / `str(e)`), so the problem and the fix reach the user."""
    home = screen_text(ROOT / "app/handlers/home_theater.py", 'f"Render error:\\n{e}"')
    assert "{e}" in home
    blueprint = screen_text(ROOT / "app/modules/wrangle_studio.py", 'return None, f"Render error: {msg}"')
    assert "msg = str(e)" in blueprint
    message = str(refusal([{"name": "geom_point", "params": {"position": "jitter", "random_state": None}}]))
    for shown in (f"Render error:\n{message}", f"Render error: {message}"):          # what each screen draws
        assert "Plot 'p', layer 1 (geom_point)" in shown and "Fix: write a number: random_state: 0" in shown


def test_a_recipe_that_writes_it_is_rejected_by_the_gate_with_the_problem_and_the_tip(tmp_path):
    recipe = tiny_recipe()
    recipe["analysis_groups"]["g"]["plots"]["p"]["spec"]["layers"] = [
        {"name": "geom_bar", "params": {}}, {"name": "geom_point", "params": {"position": "jitter", "random_state": None}}]
    problems = [str(p) for p in validate_data_analysis_recipe(write_tiny(tmp_path, recipe))]
    seed_problems = [p for p in problems if "a seed is a number" in p]
    assert len(seed_problems) == 1 and "write random_state: 0" in seed_problems[0], problems
    home_says = rejected_recipe_text("m", {"problems": problems, "contact": "the maker"})
    assert "a seed is a number" in home_says and "write random_state: 0" in home_says and "the maker" in home_says
