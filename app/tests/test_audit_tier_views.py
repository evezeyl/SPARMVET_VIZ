"""HOME's T1 and T2 views in Audit mode show the AUDITED tables (D-0622), the same tables the export writes (D-0619).

Proved headless on the demo `1_test_data_ST22_dummy` and its real data (the engine builds the tables), through `PlaceAudit.table_lazy` (the one function HOME's T1 and T2 views call):
- a filter written at the tier 1 of ResFinder: the T1 view of ResFinder is the audited table (the sample is gone, the original has it) and equals what the export writes as `T1_data_audited.tsv`;
  its T2 view is the audited tier 2; a table built from ResFinder (ResFinder_with_metadata, which has no tier-2 steps) shows the audited T1 as its T2 (its T2 is its T1);
- a table no step reaches (MLST, and ResFinder_with_metadata for a step at the tier 2 of ResFinder, which it does not read) is None: the view shows the original, and the badge says so;
- a filter written at the tier 2 of ResFinder: the T1 view stays the original, the T2 view is audited;
- a step at the tier 3 of a plot changes no table: both views are the original;
- nothing committed (Exploration, or no step): None everywhere; a step that cannot run is not the error of a table it does not reach;
- the badge of the view says in words whether the table shown is audited or the original.

Mutation index (each seen failing): MUTATION W1 `table_lazy` returns None (the views show the originals); MUTATION W2 `audited_table_lazy` returns the T1 table for T2 (the T2 view of ResFinder is wrong);
MUTATION W3 `nodes_reaching_node` accepts every place (MLST is not None for a step at ResFinder).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_tier_views.py -q
"""
import polars as pl
import pytest

from app.modules.audit_run import AuditRunError
from app.modules.view_badge import view_badge
from app.tests.test_audit_view import RECIPE_ID, World
from app.modules.cache_keys import clear_data_analysis_recipe_cache


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    yield World(tmp_path_factory.mktemp("audit_tier_views"))
    clear_data_analysis_recipe_cache()


def view(world, table, tier, nodes):
    lazy = world.audit().table_lazy(RECIPE_ID, table, tier, nodes, world.plans)
    return None if lazy is None else lazy.collect()


def test_a_filter_at_tier1_of_resfinder_shows_the_audited_tier1_and_tier2_and_equals_the_export_files(world):
    nodes = [world.node(place="T1:ResFinder", value=world.victim)]
    t1, t2 = view(world, "ResFinder", "T1", nodes), view(world, "ResFinder", "T2", nodes)
    assert world.victim not in t1["sample_id"].to_list() and world.victim not in t2["sample_id"].to_list()
    frames = world.audit().run_of(RECIPE_ID, nodes, world.plans).audited_frames()
    assert t1.equals(frames["ResFinder"]["T1"]) and t2.equals(frames["ResFinder"]["T2"]), "the view is the table the export writes"
    # the original has the sample: the audited view is a different table, and the original is untouched
    assert world.victim in world.orch.materialize_tier1(RECIPE_ID, "ResFinder", world.anchors / "ResFinder.parquet").collect()["sample_id"].to_list()


def test_a_table_built_from_the_place_shows_its_audited_tier1_as_its_tier2_when_it_has_no_tier2_steps(world):
    nodes = [world.node(place="T1:ResFinder", value=world.victim)]
    t1, t2 = view(world, "ResFinder_with_metadata", "T1", nodes), view(world, "ResFinder_with_metadata", "T2", nodes)
    assert t1 is not None and t2 is not None and t1.equals(t2), "no tier-2 steps: the T2 view is the audited T1"
    assert world.victim not in t1["sample_id"].to_list()
    assert "T2" not in world.audit().run_of(RECIPE_ID, nodes, world.plans).audited_frames()["ResFinder_with_metadata"], "the export writes no T2 file for it: its T2 is its T1 file"


def test_a_table_no_step_reaches_shows_the_original(world):
    nodes = [world.node(place="T1:ResFinder", value=world.victim)]
    assert view(world, "MLST", "T1", nodes) is None and view(world, "MLST", "T2", nodes) is None
    at_tier2 = [world.node(place="T2:ResFinder", value=world.victim)]
    assert view(world, "ResFinder", "T1", at_tier2) is None, "a step at tier 2 leaves tier 1 as it is"
    t2 = view(world, "ResFinder", "T2", at_tier2)
    assert t2 is not None and world.victim not in t2["sample_id"].to_list()
    assert view(world, "ResFinder_with_metadata", "T1", at_tier2) is None, "the join reads the tier 1 of ResFinder, which this step does not change"


def test_a_step_at_the_tier3_of_a_plot_changes_no_table_and_nothing_committed_changes_nothing(world):
    own = [world.node(place="T3:amr_heatmap", value=world.victim)]
    for table in ("ResFinder", "ResFinder_with_metadata"):
        assert view(world, table, "T1", own) is None and view(world, table, "T2", own) is None
    assert view(world, "ResFinder", "T1", []) is None and view(world, "ResFinder", "T2", []) is None


def test_a_step_that_cannot_run_is_not_the_error_of_a_table_it_does_not_reach(world):
    broken = [world.node(place="T1:ResFinder", params={"column": "no_such_column", "op": "ne", "value": "x", "na": "keep"})]
    assert view(world, "MLST", "T1", broken) is None, "MLST is not built from ResFinder: the original is shown, the error is not its"
    with pytest.raises(AuditRunError):
        view(world, "ResFinder", "T1", broken)


def test_the_badge_says_whether_the_table_shown_is_audited_or_the_original():
    audited = view_badge("T1", False, False, mode="audit", audit_view=True)
    assert audited.label == "Viewing: T1, audited" and audited.tone == "audited" and any("after the audit steps" in n for n in audited.notes)
    plain = view_badge("T2", True, False, mode="audit", audit_view=False)
    assert plain.label == "Viewing: T2, original" and plain.tone == "plain" and any("no audit step changes this table" in n for n in plain.notes)
    assert view_badge("T1", False, False, mode="exploration").label == "Viewing: T1", "Exploration: the original, said as before"
    assert view_badge("SRC", False, False, mode="audit", audit_view=None, source_table="X").label == "Viewing: Source"
    assert "T2=T1" in view_badge("T2", False, False, mode="audit", audit_view=True).notes, "the equality remark stays"
