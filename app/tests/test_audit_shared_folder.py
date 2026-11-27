"""Two sessions on one audit folder never serve each other's audited table (FLOW-2, the key check of a stored audited table).

Why: the audit folder (`audit_anchors`) is one per recipe and data, so two browser tabs on the same recipe and data share it. A tab keeps the run it made (`PlaceAudit` memo, `AuditRun`); the
other tab's apply can replace the stored file of a table with its own. Plot tables are read through the engine with their keys (`materialize_tier3`); the T1 and T2 views and the export read the
stored file of a table through `AuditRun.audited_table_lazy` and `audited_frames`, which therefore compare the key in the footer with the key their run wants and build the table again for their
own steps when it differs (`AuditRun._stored_scan`).

Mutation index (seen failing): MUTATION K1 `_stored_scan` returns `scan_parquet(path)` with no key check.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_shared_folder.py -q

# @deps
# consumes: app/modules/audit_run.py (AuditRun._stored_scan), app/modules/audit_view.py (PlaceAudit), app/tests/test_audit_view.py (World)
# doc: .claude/rules/rules_data_engine.md, .claude/knowledge/decision_ledger.md (D-0312, D-0622)
# @end_deps
"""
import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_audit_view import RECIPE_ID, World


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    yield World(tmp_path_factory.mktemp("audit_shared"))
    clear_data_analysis_recipe_cache()


def _ids(frame: pl.DataFrame) -> set:
    return set(frame["sample_id"].drop_nulls().to_list())


def test_session_b_never_reads_the_table_session_a_stored_in_the_shared_folder(world):
    session_a, session_b = world.audit(), world.audit()          # two PlaceAudit on ONE folder: two tabs of one recipe and one set of data
    step_a, step_b = world.node(value=world.ids[0]), world.node(value=world.ids[1])
    run_b = session_b.run_of(RECIPE_ID, [step_b], world.plans)    # B's table is stored: it lacks ids[1]
    assert world.ids[1] not in _ids(run_b.audited_table_lazy("ResFinder", "T1").collect())
    session_a.run_of(RECIPE_ID, [step_a], world.plans)            # A applies a step of its own: the SAME file now holds A's table
    on_disk = pl.read_parquet(run_b.tables["ResFinder"].t1_path)
    assert world.ids[0] not in _ids(on_disk) and world.ids[1] in _ids(on_disk), "the shared file now holds A's table (the premise of the test)"
    # B reads again through the run it remembers, by every way the app reads a stored audited table
    got = run_b.audited_table_lazy("ResFinder", "T1").collect()
    assert world.ids[1] not in _ids(got) and world.ids[0] in _ids(got), "B gets B's table: without ids[1], with ids[0], never A's"
    assert world.ids[1] not in _ids(session_b.table_lazy(RECIPE_ID, "ResFinder", "T1", [step_b], world.plans).collect())
    frames = run_b.audited_frames()["ResFinder"]
    assert world.ids[1] not in _ids(frames["T1"]) and world.ids[0] in _ids(frames["T1"]), "the export's read is checked too"
    # and A, which asks again, gets A's own table back (the shared file is rebuilt for each: correct, if it costs time)
    again = session_a.table_lazy(RECIPE_ID, "ResFinder", "T1", [step_a], world.plans).collect()
    assert world.ids[0] not in _ids(again) and world.ids[1] in _ids(again)


def test_a_table_that_was_not_replaced_is_served_without_a_rebuild(world):
    session = world.audit()
    step = world.node(value=world.ids[2])
    run = session.run_of(RECIPE_ID, [step], world.plans)
    path = run.tables["ResFinder"].t1_path
    before = path.stat().st_mtime_ns
    assert world.ids[2] not in _ids(run.audited_table_lazy("ResFinder", "T1").collect())
    assert path.stat().st_mtime_ns == before, "a table whose key is the one wanted is read as it is: nothing is built again"


def test_a_table_that_is_the_originals_has_no_audited_table(world):
    session = world.audit()
    run = session.run_of(RECIPE_ID, [world.node(place="T2:ResFinder", value=world.ids[0])], world.plans)
    assert run.audited_table_lazy("ResFinder", "T1") is None, "a step at tier 2 leaves tier 1 as the original's"
