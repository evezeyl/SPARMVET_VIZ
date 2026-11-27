"""An audit step error names the step and its place (a plot's own tier 3 names the plot), and the audit names EVERY plot it cannot build, not only the first
(PLOT-TABLE-ORDER-1, review point 4; since the third tier went through the audit copy, demo step 7).

Two plots whose steps at their own tier 3 cannot run give ONE error that names both (the step id and `T3:<plot>` of each), `AuditRunError.step_id` and `.place` are those of
the first, and `EXPORT_NOT_CREATED.txt` carries the whole text. The same step that breaks several plots is told once. Real engine, real recipe (the demo).

Mutation index (seen failing): MUTATION E1 `_Run.run` raises at the first failing plot (the second plot is not named).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_error_names_the_plot.py -q
"""
import pytest

from app.handlers.export_handlers import blocked_audit_notice
from app.modules.audit_run import AuditRunError
from app.tests.test_audit_view import RECIPE_ID, World
from app.modules.session_manager import make_audit_step


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    from app.modules.cache_keys import clear_data_analysis_recipe_cache
    yield World(tmp_path_factory.mktemp("error_names_the_plot"))
    clear_data_analysis_recipe_cache()


def broken(plot, column="year"):
    """A step at the plot's own tier 3 that cannot run: the column is dropped by the step before it."""
    drop = make_audit_step("drop_column", {"column": column}, reason="r", place=f"T3:{plot}")
    use = make_audit_step("filter_row", {"column": column, "op": "ge", "value": 2000.0, "na": "remove"}, reason="r", place=f"T3:{plot}")
    return [drop, use]


def test_the_error_names_the_step_and_the_plot_in_its_place(world):
    with pytest.raises(AuditRunError) as caught:
        world.audit().run_of(RECIPE_ID, broken("mlst_bar"), world.plans)
    assert "at T3:mlst_bar" in str(caught.value) and caught.value.place == "T3:mlst_bar" and caught.value.step_id.endswith("_2")


def test_two_failing_plots_are_both_named_in_one_error_with_the_first_as_its_step_and_place(world):
    nodes = broken("mlst_bar") + broken("assembly_quality_dotplot", "value")
    with pytest.raises(AuditRunError) as caught:
        world.audit().run_of(RECIPE_ID, nodes, world.plans)
    text = str(caught.value)
    assert "at T3:mlst_bar" in text and "at T3:assembly_quality_dotplot" in text, text
    assert caught.value.place == "T3:assembly_quality_dotplot", "step_id and place are those of the first failure, in the order of the recipe"


def test_a_plot_that_reads_the_same_table_but_has_no_broken_step_is_not_named(world):
    with pytest.raises(AuditRunError) as caught:
        world.audit().run_of(RECIPE_ID, broken("mlst_bar"), world.plans)
    assert "year_distribution" not in str(caught.value), "year_distribution reads the same table and has no step of its own"


def test_the_refusal_text_carries_the_whole_error_and_the_plot_whose_table_showed_it(world):
    with pytest.raises(AuditRunError) as caught:
        world.audit().run_of(RECIPE_ID, broken("mlst_bar") + broken("assembly_quality_dotplot", "value"), world.plans)
    text = blocked_audit_notice([("mlst_bar", caught.value)])
    assert text.startswith("EXPORT NOT CREATED") and "'mlst_bar'" in text
    assert "T3:mlst_bar" in text and "T3:assembly_quality_dotplot" in text and "nothing was exported" in text
