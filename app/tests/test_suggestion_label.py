"""A fix that starts with `Suggestion:` is shown without the `Fix:` label, in every place a user reads it (fix round 2026-11-16).

Eve's form for every text a user reads is "what happened, then Suggestion: ...". "Fix: Suggestion: ..." doubled the label in the
plot error (HOME, Blueprint's preview), in the checker's problem text and the upload reports (the load gate and Blueprint's
Validate read the problem and its tip separately, which already followed the rule), and in the Alerts panel of HOME.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_suggestion_label.py -q
"""
import re
from pathlib import Path

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from app.modules.data_analysis_recipe_validator import uploaded_recipe_report, validate_data_analysis_recipe
from app.tests.tiny_recipe import tiny_recipe, write_tiny
from utils.errors import VisualizationError
from utils.fix_text import fix_label
from utils.recipe_check import Problem
from viz_factory.checked_plot import error_figure
from viz_factory.viz_factory import VizFactory

ROOT = Path(__file__).resolve().parents[2]
CODE = "__import__('os').getcwd()"


def test_the_label_is_left_off_a_suggestion_and_kept_on_an_ordinary_fix():
    assert fix_label("Suggestion: write 3") == "Suggestion: write 3"
    assert fix_label("write 3") == "Fix: write 3"
    assert fix_label("write 3", "analyst") == "Fix (analyst): write 3"
    assert fix_label("Suggestion: write 3", "analyst") == "Suggestion: write 3"
    assert fix_label("") == ""


def failing_plot_error(layers):
    data = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1.0, 2.0, 3.0]})
    recipe = {"plots": {"p": {"mapping": {"x": "x", "y": "y"}, "layers": layers}}, "plot_defaults": {}}
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(data, recipe, "p").draw(show=False)
    return error.value


def test_the_plot_error_of_the_factory_has_one_label_not_two():
    """HOME draws this text in the place of the plot and Blueprint's preview shows the same error."""
    error = failing_plot_error([{"name": "geom_point"}, {"name": "geom_smooth", "params": {"formula": "y ~ " + CODE}}])
    text = str(error)
    assert ". Suggestion: " in text and "Fix:" not in text and "Fix: Suggestion" not in text
    assert error.tip.startswith("Suggestion: ")
    assert "Suggestion:" in " ".join(t.get_text() for t in error_figure(error).texts)


def test_an_ordinary_plot_error_keeps_its_fix_label():
    text = str(failing_plot_error([{"name": "geom_point", "params": {"size": "big"}}]))
    assert re.search(r"\. Fix: write a number", text) and "Suggestion" not in text


def test_the_load_gate_and_blueprint_read_one_label(tmp_path):
    recipe = tiny_recipe()
    recipe["analysis_groups"]["g"]["plots"]["p"]["spec"]["layers"] = [
        {"name": "geom_point"}, {"name": "geom_smooth", "params": {"formula": "y ~ " + CODE}}]
    path = write_tiny(tmp_path, recipe)
    problems = [p for p in validate_data_analysis_recipe(path) if "[PS06]" in p.problem]
    assert problems
    for problem in problems:
        assert "Fix: Suggestion" not in str(problem) and "Tip: Suggestion" not in str(problem)
        assert str(problem).count("Suggestion:") == 1
    lines = [l for l in uploaded_recipe_report(recipe, "run") if "[PS06]" in l]
    assert lines and all("Fix: Suggestion" not in l and l.count("Suggestion:") == 1 for l in lines)


def test_the_checker_problem_text_has_one_label():
    advice = Problem("G02", "A", "analysis_groups.g.description", "The group has no description", "Suggestion: write the question")
    assert "Fix: Suggestion" not in advice.text("r") and advice.text("r").count("Suggestion:") == 1
    error = Problem("PS04", "E", "p", "bad", "write geom_col")
    assert error.text("r").endswith("bad. Fix: write geom_col")


def test_home_prints_its_alerts_and_warnings_through_the_same_function():
    """The Alerts panel (audit_stack.py) and the warning line of HOME (home_theater.py) call `fix_label`."""
    audit = (ROOT / "app/handlers/audit_stack.py").read_text()
    home = (ROOT / "app/handlers/home_theater.py").read_text()
    assert "fix_label(fix, who or" in audit and "Fix ({who}): {fix}" not in audit
    assert "{fix_label(warning.fix)}" in home and "Fix: {warning.fix}" not in home
