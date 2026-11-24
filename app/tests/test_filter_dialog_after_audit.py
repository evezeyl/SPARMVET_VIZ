"""The filter dialog acts on the table after the audit steps (DECIDED 2026-11-15, Eve, S2-1 (a); since demo step 7 through the audit copy).

A column that an earlier audit step dropped is not offered, on T3 in Audit mode only (T1 and T2 are the tables as they are), and the
values the dialog lists are the rows that are still there. The table the dialog reads is the table of the audit copy (`PlaceAudit`, the same as the
table, the plot and the export: `home_theater._resolve_active_lf` in Audit mode on T3); on any other view it is the table as it is. Real engine, the demo recipe,
steps written at the tier 3 of the plot `amr_heatmap` (table: sample_id, gene, predicted_phenotype, identity, overlap, ...).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_dialog_after_audit.py -q
"""
import pytest

from app.modules.audit_places import PLACES_BUCKET
from app.modules.audit_run import AuditRunError
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.session_manager import make_audit_step
from app.modules.t3_audit_engine import column_types, value_choices
from app.tests.test_audit_view import RECIPE_ID, World

PLOT = "amr_heatmap"


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    yield World(tmp_path_factory.mktemp("dialog_after_audit"))
    clear_data_analysis_recipe_cache()


def drop(column):
    return make_audit_step("drop_column", {"column": column}, plot_scope=PLACES_BUCKET, reason="r", place=f"T3:{PLOT}")


def keep_one_gene(gene):
    return make_audit_step("filter_row", {"column": "gene", "op": "eq", "value": gene, "na": "remove"}, plot_scope=PLACES_BUCKET, reason="r", place=f"T3:{PLOT}")


def audited(world, nodes):
    """The table the dialog reads in Audit mode on T3."""
    lazy = world.audit().plot_lazy(RECIPE_ID, PLOT, nodes, world.plans)
    return lazy if lazy is not None else world.orch.materialize_tier3(RECIPE_ID, PLOT, world.anchors)


def as_it_is(world):
    """The table the dialog reads on any other view (T2: the stored table of the plot's target) and in Exploration."""
    return world.orch.materialize_tier3(RECIPE_ID, PLOT, world.anchors)


def test_a_dropped_column_is_not_offered_in_audit_mode_on_t3(world):
    assert "identity" not in column_types(audited(world, [drop("identity")]))


def test_a_dropped_column_is_still_offered_in_t1_and_t2(world):
    assert "identity" in column_types(as_it_is(world))


def test_the_values_listed_are_the_rows_that_are_still_there(world):
    genes = list(value_choices(as_it_is(world), "gene"))
    assert len(genes) > 1
    kept = list(value_choices(audited(world, [keep_one_gene(genes[0])]), "gene"))
    assert kept == [genes[0]], "the rows with another gene were filtered out by the earlier step"
    assert list(value_choices(as_it_is(world), "gene")) == genes


def test_without_audit_steps_the_dialog_sees_the_table_as_it_is(world):
    assert list(column_types(audited(world, []))) == list(column_types(as_it_is(world)))


def test_two_drops_leave_the_rest(world):
    got = list(column_types(audited(world, [drop("identity"), drop("overlap")])))
    assert "identity" not in got and "overlap" not in got and "gene" in got and "sample_id" in got
    assert got == [c for c in column_types(as_it_is(world)) if c not in ("identity", "overlap")]


def test_a_list_that_cannot_run_raises_in_audit_mode_and_not_elsewhere(world):
    broken = [drop("identity"), make_audit_step("filter_row", {"column": "identity", "op": "ge", "value": 1.0, "na": "remove"}, plot_scope=PLACES_BUCKET, reason="r", place=f"T3:{PLOT}")]
    with pytest.raises(AuditRunError, match=f"T3:{PLOT}"):
        audited(world, broken)
    assert "identity" in column_types(as_it_is(world))
