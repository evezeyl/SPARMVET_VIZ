"""HOME's load gate and Blueprint's Validate refuse a plot text that would run code (PLOT-TEXT-RUNS-CODE-1, check PS06).

The gate is `validate_data_analysis_recipe` (the strict checker with the registries as catalogues); a recipe it refuses is
never offered to the user (ADR-094). The texts are the ones that wrote a marker file through the plot factory before the fix
(`libs/viz_factory/tests/test_plot_text_runs_no_code.py`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_plot_text_gate.py -q
"""
import pytest

from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
from app.tests.tiny_recipe import tiny_recipe, write_tiny

CODE = "__import__('os').getcwd()"


def spec_of(recipe):
    return recipe["analysis_groups"]["g"]["plots"]["p"]["spec"]


def problems(tmp_path, layers=None, mapping=None):
    recipe = tiny_recipe()
    if layers is not None:
        spec_of(recipe)["layers"] = layers
    if mapping is not None:
        spec_of(recipe)["mapping"] = mapping
    return validate_data_analysis_recipe(write_tiny(tmp_path, recipe))


@pytest.mark.parametrize("layer", [
    {"name": "geom_smooth", "params": {"method": "lm", "formula": "y ~ I(" + CODE + ")"}},
    {"name": "stat_smooth", "params": {"method": "lm", "formula": "y ~ " + CODE}},
    {"name": "facet_wrap", "params": {"facets": CODE}},
    {"name": "facet_grid", "params": {"rows": "a", "cols": CODE}},
    {"name": "stat_function", "params": {"fun": CODE}},
])
def test_a_plot_text_that_runs_code_is_refused_with_ps06(tmp_path, layer):
    found = problems(tmp_path, layers=[{"name": "geom_point"}, layer])
    assert [p for p in found if "[PS06]" in p.problem], [str(p) for p in found]
    assert all("Suggestion:" in p.tip for p in found if "[PS06]" in p.problem)


def test_a_facet_by_in_the_mapping_is_refused_with_ps06(tmp_path):
    found = problems(tmp_path, mapping={"x": "a", "facet_by": CODE})
    assert [p for p in found if "[PS06]" in p.problem]


def test_what_a_scientist_writes_is_not_refused(tmp_path):
    layers = [{"name": "geom_point"}, {"name": "geom_smooth", "params": {"method": "lm", "formula": "y ~ x + I(x**2)"}},
              {"name": "facet_wrap", "params": {"facets": "~ a"}}]
    assert [p for p in problems(tmp_path, layers=layers) if "[PS06]" in p.problem] == []
