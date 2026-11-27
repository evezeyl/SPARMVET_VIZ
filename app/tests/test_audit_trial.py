"""Trying an audit step before it is applied, and reusing what the trial computed (HOME audit; `app/modules/audit_trial.py`).

What the design expects (ledger D-0656, D-0662, D-0669 to D-0671; `.claude/design/home_audit_what_is_true_now.md`): the effect of a pending step is computed before it is applied; applying reuses that
result, keyed, with no second calculation; a tried step is never taken for an applied one; nothing of a trial is saved or exported (D-0302, D-0327). Run on the demo `1_test_data_ST22_dummy` and its real data.

- A trial has its own folder and its own reader: with a trial open, everything the export reads (the `PlaceAudit` of the applied steps, `AuditRun.audited_frames`, the files of the audit folder, the
  original's folder) is byte for byte what it is with no trial.
- The tried steps are appended LAST in their place's list; the same signature is the same trial; a changed condition, places or applied list is another one and the old trial's folder is emptied.
- The placeholder reason exists only in the trial copy: no file of the original, the audit or the trial folder holds it, nor the list that is returned to be stored.
- Applying: refuses when anything changed since the trial, moves a stored table only when the key in its footer is the key now wanted (never by name), empties the trial folder, returns the list to store
  with `applied_at` set now; after it `PlaceAudit.run_of` builds nothing and every table and every Result data (T3) equals a computation from scratch in empty folders.
- Errors show at the trial, as a plain sentence, not after Apply; the export's "committed at" is the moment of applying.

Mutation index (each seen failing, see the report of the builder): MUTATION T1 the move by key removed (files move by name); MUTATION T2 the signature ignores the applied list; MUTATION T3 the trial shares
the audit folder; MUTATION T4 `applied_at` taken from `created_at`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_trial.py -q
"""
import hashlib
import json
import os
import shutil
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from app.modules.audit_place_view import AUDIT, Readers, table_for, viewed
from app.modules.audit_places import audit_recipe_of, bake_place_steps, place_step_records
from app.modules import audit_trial as audit_trial_module
from app.modules.audit_run import compare_tables, same_table
from app.modules.audit_trial import (NO_ROW_CHANGED, TABLE_CHANGED, TRIAL_FOLDER, TRIAL_REASON, PlaceTrial, TrialRefused, clean_trials, with_applied_at)
from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META
from app.modules.session_manager import make_audit_step
from app.tests.test_audit_view import PIPELINES, RECIPE_ID, World
from transformer.anchor import open_anchor
from utils import recipe_tiers
from utils.lineage_data import lineage_of


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    made = World(tmp_path_factory.mktemp("audit_trial"))
    made.lineage = lineage_of(made.loaded.raw, made.plans)
    yield made
    clear_data_analysis_recipe_cache()


def step(place, column="sample_id", value="no_such_sample", op="ne", na="keep", node_type="filter_row", params=None, node_id=None, reason="", created_at=None):
    """A node as HOME stages it (no reason yet unless given)."""
    params = params if params is not None else {"column": column, "op": op, "value": value, "na": na}
    node = make_audit_step(node_type, params, reason=reason, place=place, started_from="subtab_amr_heatmap", node_id=node_id)
    if created_at:
        node["created_at"] = created_at
    return node


def applied_step(place, reason="applied earlier", **kwargs):
    return step(place, reason=reason, **kwargs)


def fresh(world, tmp_path):
    """A `PlaceAudit` of the applied steps and the `PlaceTrial` beside it, both in folders of this test."""
    audit = PlaceAudit(world.orch, world.anchors, tmp_path / "audit_anchors")
    return audit, PlaceTrial(world.orch, audit, tmp_path / TRIAL_FOLDER)


def hashes(folder: Path):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()} if folder.is_dir() else {}


def frames_of(run):
    return {t: {k: v.to_dict(as_series=False) for k, v in tiers.items()} for t, tiers in run.audited_frames().items()}


def compare_with_scratch(world, tmp_path, audit, stored):
    """Every table (tier 1 and tier 2) and every plot's Result data (T3) of the audit run of `stored` equals a computation from scratch in empty folders (its own original's folder too).
    Returns (tables compared, plots compared)."""
    run = audit.run_of(RECIPE_ID, stored, world.plans)
    scratch = PlaceAudit(world.orch, tmp_path / "scratch_anchors", tmp_path / "scratch_audit").run_of(RECIPE_ID, stored, world.plans)
    tables = plots = 0
    for table in run.tables:
        for tier in ("T1", "T2"):
            mine = run.audited_table_lazy(table, tier)
            theirs = scratch.audited_table_lazy(table, tier)
            mine = run.original_table_lazy(table, tier) if mine is None else mine
            theirs = scratch.original_table_lazy(table, tier) if theirs is None else theirs
            assert mine.collect().equals(theirs.collect()), f"{table} {tier} differs from a computation from scratch"
            tables += 1
    for plot in run.plots:
        mine = run.plot_table(plot)
        theirs = scratch.plot_table(plot)
        mine = run.original_plot_lazy(plot) if mine is None else mine
        theirs = scratch.original_plot_lazy(plot) if theirs is None else theirs
        assert mine.collect().equals(theirs.collect()), f"the Result data (T3) of {plot} differs from a computation from scratch"
        plots += 1
    shutil.rmtree(tmp_path / "scratch_anchors", ignore_errors=True)
    shutil.rmtree(tmp_path / "scratch_audit", ignore_errors=True)
    return tables, plots


# ---------------------------------------------------------------------------------------------------------------------
# A tried step is never an applied one
# ---------------------------------------------------------------------------------------------------------------------


def test_with_a_trial_open_everything_the_export_reads_is_byte_for_byte_what_it_is_without(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    applied = [applied_step("T1:ResFinder", value=world.victim)]
    run = audit.run_of(RECIPE_ID, applied, world.plans)
    audit_files, original_files, frames = hashes(audit.audit_dir), hashes(world.anchors), frames_of(run)
    assert audit_files and frames
    result = trial.try_step(RECIPE_ID, applied, [step("T1:MLST", value=world.ids[1])], world.plans)
    assert result.error is None and any(trial.trial_dir.rglob("*.parquet"))
    assert hashes(audit.audit_dir) == audit_files and hashes(world.anchors) == original_files
    assert audit.run_of(RECIPE_ID, applied, world.plans) is run and frames_of(run) == frames
    assert audit.table_lazy(RECIPE_ID, "MLST", "T1", applied, world.plans) is None        # the audited reader does not see the tried table
    assert all(not Path(t.t1_path).is_relative_to(trial.trial_dir) for t in run.tables.values())
    assert not trial.trial_dir.resolve().is_relative_to(audit.audit_dir.resolve()) and not audit.audit_dir.resolve().is_relative_to(trial.trial_dir.resolve())
    export = audit.run_of(RECIPE_ID, applied, world.plans)        # what an export made now reads
    assert frames_of(export) == frames


def test_the_trial_folder_is_a_sibling_per_session_never_inside_the_audit_or_the_original_folder(world, tmp_path):
    audit, first = fresh(world, tmp_path)
    second = PlaceTrial(world.orch, audit, tmp_path / TRIAL_FOLDER)
    assert first.trial_dir != second.trial_dir and first.trial_dir.parent == second.trial_dir.parent == tmp_path / TRIAL_FOLDER
    assert audit.audit_dir.name == "audit_anchors" and audit.audit_dir.parent == first.trial_root.parent
    first.try_step(RECIPE_ID, [], [step("T1:MLST", value=world.ids[1])], world.plans)
    second.try_step(RECIPE_ID, [], [step("T1:MLST", value=world.ids[2])], world.plans)
    other = hashes(second.trial_dir)
    first.discard()                                      # the other tab's trial is not touched
    assert not first.trial_dir.exists() and hashes(second.trial_dir) == other
    with pytest.raises(ValueError):
        PlaceTrial(world.orch, audit, tmp_path / "not_the_trial_folder")


# ---------------------------------------------------------------------------------------------------------------------
# What a trial says
# ---------------------------------------------------------------------------------------------------------------------


def test_the_trial_says_the_rows_before_and_after_at_each_place_and_what_the_step_reaches(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    original = world.orch.materialize_tier1(RECIPE_ID, "ResFinder", world.anchors / "ResFinder.parquet").collect()
    removed = int((original["sample_id"] == world.victim).sum())
    assert removed > 0
    result = trial.try_step(RECIPE_ID, [], [step("T1:ResFinder", value=world.victim)], world.plans)
    assert result.error is None and len(result.effects) == 1
    effect = result.effects[0]
    assert (effect.place, effect.rows_before, effect.rows_after, effect.rows_removed, effect.state) == ("T1:ResFinder", original.height, original.height - removed, removed, TABLE_CHANGED)
    reached = {item.node: item for item in result.reaches}
    assert "T1:ResFinder" not in reached                                         # the place itself is an effect, not something it reaches
    assert "T1:MLST" not in reached                                               # a table beside the place is not reached
    below = set(world.graph.below("T1:ResFinder"))
    assert set(reached) <= below
    assert "T3:amr_heatmap" in reached and reached["T3:amr_heatmap"].kind == "plot"
    assert all(item.state in (TABLE_CHANGED, NO_ROW_CHANGED) for item in result.reaches)
    assert {n for n, i in reached.items() if i.kind == "plot" and i.state == TABLE_CHANGED} == set(f"T3:{p}" for p in trial._stored.run.affected_plots)
    assert not any(item.node.startswith("T2:") and not world.graph.node(item.node).steps for item in result.reaches)    # a tier 2 with no steps is its tier 1: one line


def test_a_step_that_removes_nothing_is_told_as_no_row_changed_and_still_applies(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:ResFinder", value="no_such_sample")]
    result = trial.try_step(RECIPE_ID, [], tried, world.plans)
    assert result.effects[0].rows_removed == 0 and result.effects[0].state == NO_ROW_CHANGED
    assert all(item.state == NO_ROW_CHANGED for item in result.reaches)
    assert trial.trial_table("ResFinder", "T1") is None and trial.trial_plot("amr_heatmap") is None       # the audited or the original answer stands
    stored = trial.apply_trial(RECIPE_ID, [], tried, "kept for the record", world.plans)
    assert audit.run_of(RECIPE_ID, stored, world.plans).built_tables == []


def test_a_step_at_a_plots_result_data_and_a_step_at_two_independent_graphs_are_told_per_place(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    at_plot = trial.try_step(RECIPE_ID, [], [step("T3:amr_heatmap", column="identity", op="ge", value=0.0, na="remove")], world.plans)
    assert at_plot.error is None and at_plot.reaches == () and at_plot.effects[0].rows_removed > 0
    assert not any(trial.trial_dir.rglob("*.parquet"))                          # a step at a plot builds no table: only the Result data differs
    decision = "decision-with-two-places"
    two = [step("T1:ResFinder", value=world.victim, node_id=decision), step("T1:Bracken", value=world.victim, node_id=decision)]
    both = trial.try_step(RECIPE_ID, [], two, world.plans)
    assert both.error is None and [e.place for e in both.effects] == ["T1:ResFinder", "T1:Bracken"] and all(e.rows_before > 0 for e in both.effects)
    assert "T1:MLST" not in {i.node for i in both.reaches} and "T3:amr_heatmap" in {i.node for i in both.reaches} and "T3:qc_reads_horizontal_barplot" in {i.node for i in both.reaches}


# ---------------------------------------------------------------------------------------------------------------------
# The signature and the order
# ---------------------------------------------------------------------------------------------------------------------


def test_the_same_signature_is_the_same_trial_and_any_change_discards_the_old_folder(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:MLST", value=world.ids[1])]
    first = trial.try_step(RECIPE_ID, [], tried, world.plans)
    marker = trial.trial_dir / "left_by_the_first_trial.txt"
    marker.write_text("x")
    assert trial.try_step(RECIPE_ID, [], [dict(n, reason="another reason does not matter") for n in tried], world.plans) is first
    assert marker.exists()
    changed_condition = [step("T1:MLST", value=world.ids[2])]
    second = trial.try_step(RECIPE_ID, [], changed_condition, world.plans)
    assert second is not first and second.signature != first.signature and not marker.exists()
    marker.write_text("x")
    other_places = [step("T1:ResFinder", value=world.ids[2])]
    assert trial.try_step(RECIPE_ID, [], other_places, world.plans).signature != second.signature and not marker.exists()
    marker.write_text("x")
    with_applied = trial.try_step(RECIPE_ID, [applied_step("T1:MLST", value=world.ids[0])], other_places, world.plans)
    assert with_applied.signature != second.signature and not marker.exists()
    with pytest.raises(ValueError):
        trial.try_step(RECIPE_ID, [], [], world.plans)


def test_the_tried_step_is_appended_last_in_its_places_list_and_the_order_changes_the_key(world, tmp_path):
    a = applied_step("T1:ResFinder", value=world.ids[0])
    b = step("T1:ResFinder", value=world.ids[1])
    audit_1, trial_1 = fresh(world, tmp_path / "one")
    audit_2, trial_2 = fresh(world, tmp_path / "two")
    trial_1.try_step(RECIPE_ID, [a], [b], world.plans)
    trial_2.try_step(RECIPE_ID, [dict(b, reason="r")], [dict(a, reason="")], world.plans)                  # the other order
    key_1 = trial_1._stored.run.tables["ResFinder"].t1_key_audit
    key_2 = trial_2._stored.run.tables["ResFinder"].t1_key_audit
    assert key_1 != key_2
    assert trial_1._stored.signature != trial_2._stored.signature
    stored = trial_1.apply_trial(RECIPE_ID, [a], [b], "second step", world.plans)
    assert [n["id"] for n in stored] == [a["id"], b["id"]]                                           # the tried step is last
    assert audit_1.run_of(RECIPE_ID, stored, world.plans).tables["ResFinder"].t1_key_audit == key_1    # the key of the trial is the key of the applied list


# ---------------------------------------------------------------------------------------------------------------------
# The placeholder reason
# ---------------------------------------------------------------------------------------------------------------------


def test_the_placeholder_reason_is_in_no_file_no_session_no_export_and_the_callers_nodes_are_not_changed(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:ResFinder", value=world.victim)]
    snapshot = json.dumps(tried, sort_keys=True)
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    assert json.dumps(tried, sort_keys=True) == snapshot and tried[0]["reason"] == ""
    needle = TRIAL_REASON.encode("utf-8")
    assert any(trial.trial_dir.rglob("*.parquet"))
    for folder in (trial.trial_dir, audit.audit_dir, world.anchors):
        assert not any(needle in p.read_bytes() for p in folder.rglob("*") if p.is_file()), folder
    stored = trial.apply_trial(RECIPE_ID, [], tried, "removed after the lab notebook", world.plans)
    assert TRIAL_REASON not in json.dumps(stored)                                             # what a session file would hold
    assert [n["reason"] for n in stored] == ["removed after the lab notebook"]
    records = place_step_records(world.graph, stored)                                           # what t3_steps.yaml, the README and the report hold
    assert TRIAL_REASON not in json.dumps(records) and records[0]["reason"] == "removed after the lab notebook"
    assert TRIAL_REASON not in yaml.safe_dump(audit_recipe_of(world.loaded.raw, stored, RECIPE_ID, "2026-11-26"))
    for folder in (trial.trial_root, audit.audit_dir, world.anchors):
        assert not any(needle in p.read_bytes() for p in folder.rglob("*") if p.is_file()), folder


# ---------------------------------------------------------------------------------------------------------------------
# Applying: the reuse, checked against a computation from scratch
# ---------------------------------------------------------------------------------------------------------------------


CASES = {
    "at a tier 1": lambda w: ([], [step("T1:ResFinder", value=w.victim)]),
    "at a tier 2": lambda w: ([], [step("T2:ResFinder", value=w.victim)]),
    "at a plots Result data (T3)": lambda w: ([], [step("T3:amr_heatmap", column="identity", op="ge", value=0.0, na="remove")]),
    "at two places of two independent graphs": lambda w: ([], [step("T1:ResFinder", value=w.victim, node_id="two-graphs"), step("T1:Bracken", value=w.victim, node_id="two-graphs")]),
    "a column drop at a tier 1": lambda w: ([], [step("T1:ResFinder", node_type="drop_column", params={"column": "overlap"})]),
    "a column drop at a plots Result data (T3)": lambda w: ([], [step("T3:amr_heatmap", node_type="drop_column", params={"column": "identity"})]),
    "after two applied steps": lambda w: ([applied_step("T1:ResFinder", value=w.ids[0]), applied_step("T2:ResFinder", value=w.ids[1])], [step("T1:MLST", value=w.ids[2])]),
    "after an applied step at the same place": lambda w: ([applied_step("T1:ResFinder", value=w.ids[0])], [step("T1:ResFinder", value=w.ids[1])]),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_applying_a_trial_builds_nothing_and_every_table_and_result_data_equals_a_computation_from_scratch(world, tmp_path, case, capsys):
    audit, trial = fresh(world, tmp_path)
    applied, tried = CASES[case](world)
    if applied:
        audit.run_of(RECIPE_ID, applied, world.plans)
    result = trial.try_step(RECIPE_ID, applied, tried, world.plans)
    assert result.error is None, result.error
    assert any(e.state == TABLE_CHANGED for e in result.effects), "the case must change something, or it proves nothing"
    stored = trial.apply_trial(RECIPE_ID, applied, tried, "a reason typed at the step bar", world.plans)
    assert stored[:len(applied)] == applied and [n["id"] for n in stored[len(applied):]] == [n["id"] for n in tried]
    assert not trial.trial_dir.exists()                                                       # emptied at apply
    run = audit.run_of(RECIPE_ID, stored, world.plans)
    assert run.built_tables == [], run.built_tables                                           # the reuse: nothing is built at commit
    tables, plots = compare_with_scratch(world, tmp_path, audit, stored)
    assert tables >= 20 and plots >= 10
    with capsys.disabled():
        print(f"\n[trial] {case}: {tables} table readings and {plots} plots equal a computation from scratch; built at commit: {run.built_tables}")


def test_apply_refuses_when_the_applied_list_changed_since_the_trial_and_moves_nothing(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    earlier = applied_step("T1:ResFinder", value=world.ids[0])
    audit.run_of(RECIPE_ID, [earlier], world.plans)
    tried = [step("T1:MLST", value=world.ids[1])]
    trial.try_step(RECIPE_ID, [earlier], tried, world.plans)
    audit_files = hashes(audit.audit_dir)
    with pytest.raises(TrialRefused) as refused:           # the step was removed with the bin between the trial and the apply
        trial.apply_trial(RECIPE_ID, [], tried, "a reason", world.plans)
    assert "Try the step again" in str(refused.value) and "Nothing was applied" in str(refused.value)
    assert hashes(audit.audit_dir) == audit_files and not trial.trial_dir.exists()
    with pytest.raises(TrialRefused):                      # the trial is gone: a second apply has nothing to reuse
        trial.apply_trial(RECIPE_ID, [earlier], tried, "a reason", world.plans)


@pytest.mark.parametrize("change", ["condition", "places", "added applied step"])
def test_apply_refuses_when_the_condition_the_places_or_the_applied_steps_differ(world, tmp_path, change):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:MLST", value=world.ids[1])]
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    live_tried, live_applied = tried, []
    if change == "condition":
        live_tried = [dict(tried[0], params={**tried[0]["params"], "value": world.ids[2]})]
    elif change == "places":
        live_tried = [dict(tried[0], place="T1:ResFinder")]
    else:
        live_applied = [applied_step("T1:ResFinder", value=world.ids[0])]
    with pytest.raises(TrialRefused):
        trial.apply_trial(RECIPE_ID, live_applied, live_tried, "a reason", world.plans)
    assert not trial.trial_dir.exists()


def test_apply_refuses_without_a_trial_without_a_reason_and_after_an_error(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:MLST", value=world.ids[1])]
    with pytest.raises(TrialRefused):
        trial.apply_trial(RECIPE_ID, [], tried, "a reason", world.plans)
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    for empty in ("", "   ", None):
        with pytest.raises(TrialRefused):
            trial.apply_trial(RECIPE_ID, [], tried, empty, world.plans)
    assert any(trial.trial_dir.rglob("*.parquet"))                                           # a missing reason does not throw the trial away
    assert trial.apply_trial(RECIPE_ID, [], tried, "now with a reason", world.plans)[0]["reason"] == "now with a reason"


def test_a_stored_table_moves_only_when_its_key_is_the_key_now_wanted_never_by_name(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:ResFinder", value=world.ids[0])]
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    wrong = PlaceTrial(world.orch, audit, tmp_path / TRIAL_FOLDER)
    wrong.try_step(RECIPE_ID, [], [step("T1:ResFinder", value=world.ids[1])], world.plans)      # another condition: the same file names, another key
    planted = wrong.trial_dir / "ResFinder.parquet"
    shutil.copy(planted, trial.trial_dir / "ResFinder.parquet")                                  # the right name, the wrong key
    stored = trial.apply_trial(RECIPE_ID, [], tried, "kept", world.plans)
    assert not (audit.audit_dir / "ResFinder.parquet").exists()                                  # the planted file did not move
    run = audit.run_of(RECIPE_ID, stored, world.plans)
    assert "ResFinder T1" in run.built_tables                                                    # the planted file was not served: the table was built again
    compare_with_scratch(world, tmp_path, audit, stored)


# ---------------------------------------------------------------------------------------------------------------------
# Errors at the trial
# ---------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("what, params", [("a column that is not there", {"column": "no_such_column", "op": "eq", "value": "a", "na": "keep"}),
                                          ("a value of a type that does not fit", {"column": "identity", "op": "eq", "value": "not a number", "na": "keep"})])
def test_a_step_that_cannot_run_is_told_at_the_trial_as_a_plain_sentence_with_nothing_left(world, tmp_path, what, params):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:ResFinder", params=params)]
    result = trial.try_step(RECIPE_ID, [], tried, world.plans)
    assert result.error and "T1:ResFinder" in result.error and "cannot be applied" in result.error, what
    assert result.effects == () and result.reaches == ()
    assert not trial.trial_dir.exists() and not audit.audit_dir.exists()
    assert trial.trial_table("ResFinder", "T1") is None and trial.trial_plot("amr_heatmap") is None
    assert trial.try_step(RECIPE_ID, [], tried, world.plans) is result                           # the same trial: not run again
    with pytest.raises(TrialRefused) as refused:
        trial.apply_trial(RECIPE_ID, [], tried, "a reason", world.plans)
    assert "cannot be applied" in str(refused.value)
    assert trial.try_step(RECIPE_ID, [], [step("T1:ResFinder", value=world.ids[0])], world.plans).error is None      # a good step after a bad one


# ---------------------------------------------------------------------------------------------------------------------
# Nothing left behind
# ---------------------------------------------------------------------------------------------------------------------


def test_clean_trials_removes_own_folder_or_all_and_a_planted_leftover_of_a_killed_process(world, tmp_path):
    root = tmp_path / TRIAL_FOLDER
    audit, trial = fresh(world, tmp_path)
    trial.try_step(RECIPE_ID, [], [step("T1:MLST", value=world.ids[1])], world.plans)
    leftover = root / "killed_process"                                       # what a process killed in the middle leaves
    leftover.mkdir()
    (leftover / "MLST.parquet").write_bytes(b"half written")
    (root / "stray_file.txt").write_text("x")
    audit_files, original_files = hashes(audit.audit_dir), hashes(world.anchors)
    assert clean_trials(root, trial.token) == [trial.token] and not trial.trial_dir.exists() and leftover.exists()
    assert clean_trials(root, "no_such_token") == []
    assert sorted(clean_trials(root)) == ["killed_process", "stray_file.txt"] and not root.exists()      # the start of the app
    assert clean_trials(root) == []                                                                       # nothing there is not an error
    assert hashes(audit.audit_dir) == audit_files and hashes(world.anchors) == original_files
    with pytest.raises(ValueError):
        clean_trials(tmp_path / "audit_anchors")                                                          # never a recursive delete of another folder
    with pytest.raises(ValueError):
        clean_trials(root, "../audit_anchors")


def test_discard_and_apply_and_a_failed_trial_leave_no_trial_folder(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:MLST", value=world.ids[1])]
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    assert trial.trial_dir.exists()
    trial.discard()
    assert not trial.trial_dir.exists() and trial.trial_table("MLST", "T1") is None
    trial.discard()                                                                                     # idempotent
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    trial.apply_trial(RECIPE_ID, [], tried, "r", world.plans)
    assert not trial.trial_dir.exists() and not list(trial.trial_root.rglob("*.parquet"))


# ---------------------------------------------------------------------------------------------------------------------
# The readers of the one reader
# ---------------------------------------------------------------------------------------------------------------------


def readers_of(world, audit, trial, nodes):
    return Readers(
        source=lambda t: world.orch.read_source(RECIPE_ID, t),
        tier1=lambda t: world.orch.materialize_tier1(RECIPE_ID, t, world.anchors / f"{t}.parquet"),
        tier2=lambda t: world.orch.materialize_tier2(RECIPE_ID, t, world.anchors / f"{t}.parquet"),
        plot=lambda p: world.orch.materialize_tier3(RECIPE_ID, p, world.anchors),
        audited_table=lambda t, tier: audit.table_lazy(RECIPE_ID, t, tier, nodes, world.plans),
        audited_plot=lambda p: audit.plot_lazy(RECIPE_ID, p, nodes, world.plans),
        committed_steps=len(nodes), trial_table=trial.trial_table, trial_plot=trial.trial_plot)


def test_table_for_answers_trial_where_the_tried_step_changes_and_audited_or_original_elsewhere(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    earlier = applied_step("T1:MLST", value=world.ids[0])
    applied = [earlier]
    audit.run_of(RECIPE_ID, applied, world.plans)
    tried = [step("T1:ResFinder", value=world.victim)]
    readers = readers_of(world, audit, trial, applied)
    open_plot = "amr_heatmap"

    def shown(place):
        facts = table_for(viewed(AUDIT, "T3", None, open_plot, [place], world.graph, world.lineage), readers)
        return facts[1].state, facts[0]

    assert shown("T1:ResFinder")[0] == "original"                                                    # no trial yet: the original
    trial.try_step(RECIPE_ID, applied, tried, world.plans)
    state, frame = shown("T1:ResFinder")
    assert state == "trial" and frame.collect().height == trial._stored.result.effects[0].rows_after
    assert shown("T3:amr_heatmap")[0] == "trial"                                                     # a plot built from the place
    assert shown("T1:MLST")[0] == "audited"                                                          # the applied step, not the tried one
    assert shown("T1:Bracken")[0] == "original"                                                      # beside both
    assert shown("T3:virulence_bar")[0] == "trial"                                                   # a plot built from the place, through ST22_Anchor
    assert shown("T3:qc_reads_horizontal_barplot")[0] == "original"                                  # a plot the tried step does not reach
    trial.discard()
    assert shown("T1:ResFinder")[0] == "original" and shown("T1:MLST")[0] == "audited"
    assert trial.trial_table("Nonexistent", "T1") is None and trial.trial_plot("nonexistent") is None


def test_a_tier_2_view_of_a_table_with_no_tier_2_steps_is_its_tier_1_trial(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    trial.try_step(RECIPE_ID, [], [step("T1:MLST", value=world.ids[1])], world.plans)
    t1 = trial.trial_table("MLST", "T1")
    t2 = trial.trial_table("MLST", "T2")
    assert t1 is not None and t2 is not None and t1.collect().equals(t2.collect())


# ---------------------------------------------------------------------------------------------------------------------
# The time of applying
# ---------------------------------------------------------------------------------------------------------------------


def test_applied_at_is_the_moment_of_applying_and_the_export_reads_it_with_a_fallback(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:ResFinder", value=world.victim, created_at="2020-01-01T08:00:00")]
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    stored = trial.apply_trial(RECIPE_ID, [], tried, "a reason", world.plans, when="2026-11-26T11:30:00")
    assert stored[0]["created_at"] == "2020-01-01T08:00:00" and stored[0]["applied_at"] == "2026-11-26T11:30:00"
    assert "applied_at" not in tried[0]                                                              # the caller's node is not changed
    record = place_step_records(world.graph, stored)[0]
    assert record["committed_at"] == "2026-11-26T11:30:00"
    assert "2026-11-26" in recipe_tiers.collection_body(bake_place_steps(world.loaded.raw, stored), "ResFinder")["tier1"]["steps"][-1]["comment"]
    legacy = {k: v for k, v in stored[0].items() if k != "applied_at"}
    assert place_step_records(world.graph, [legacy])[0]["committed_at"] == "2020-01-01T08:00:00"      # a step stored before the key existed
    now = with_applied_at([tried[0]])[0]["applied_at"]
    assert len(now) == 19 and now >= "2026-11-26" and "applied_at" not in tried[0]
    later = [step("T1:MLST", value=world.ids[1])]
    trial.try_step(RECIPE_ID, [], later, world.plans)
    live = trial.apply_trial(RECIPE_ID, [], later, "r", world.plans)[0]      # no `when`: the time of the call
    assert live["applied_at"] >= live["created_at"] and live["applied_at"][:10] == datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------------------------------------------------
# The start of the app
# ---------------------------------------------------------------------------------------------------------------------


def test_the_start_of_the_app_removes_every_trial_folder_a_killed_process_left_and_touches_nothing_else(tmp_path, monkeypatch):
    from app.tests.test_cache_version_6 import REPO, _deployment
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE", "SPARMVET_CONNECTOR", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)
    deployment, anchors = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(deployment))
    user_data = anchors.parent
    leftover = user_data / TRIAL_FOLDER / "killed_process"
    leftover.mkdir(parents=True)
    (leftover / "ResFinder.parquet").write_bytes(b"half written by a process that was killed")
    audit_folder = user_data / "audit_anchors"
    audit_folder.mkdir()
    (audit_folder / "kept.txt").write_text("the applied steps' tables are not scratch")
    from app.src.bootloader import Bootloader
    Bootloader()
    assert not (user_data / TRIAL_FOLDER).exists()
    assert (audit_folder / "kept.txt").read_text() == "the applied steps' tables are not scratch"
    Bootloader()                                       # a start with no trial folder is not an error


def test_after_apply_the_audited_reader_does_not_serve_the_run_of_the_old_list(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    earlier = applied_step("T1:ResFinder", value=world.ids[0])
    old_run = audit.run_of(RECIPE_ID, [earlier], world.plans)
    tried = [step("T1:ResFinder", value=world.ids[1])]
    trial.try_step(RECIPE_ID, [earlier], tried, world.plans)
    stored = trial.apply_trial(RECIPE_ID, [earlier], tried, "second", world.plans)
    assert audit.run_of(RECIPE_ID, [earlier], world.plans) is not old_run          # the memo is gone; the old list is computed again, not served
    compare_with_scratch(world, tmp_path, audit, [earlier])
    compare_with_scratch(world, tmp_path, audit, stored)


# ---------------------------------------------------------------------------------------------------------------------
# Fix round: all or nothing at apply, rows before, clean_trials that cannot hurt, no placeholder in a sentence, a folder emptied by someone else, ids, one read
# ---------------------------------------------------------------------------------------------------------------------


def footer_keys(folder: Path):
    """{file name: the keys in its footer} of every stored table of the folder."""
    found = {}
    for path in sorted(folder.glob("*.parquet")):
        footer = open_anchor(path)[0]
        found[path.name] = {footer.get(TIER1_KEY_META), footer.get(TIER2_KEY_META)} - {None}
    return found


def assert_a_reader_of_the_old_list_sees_only_the_old_list(world, tmp_path, audit, trial, applied):
    """The reader of the list that is still the stored one computes the same as from scratch, nothing of the tried step is on disk and the trial folder is gone."""
    assert not trial.trial_dir.exists()
    run = audit.run_of(RECIPE_ID, applied, world.plans)
    wanted = {k for t in run.tables.values() for k in (t.t1_key_audit, t.t2_key_audit)}
    for name, keys in footer_keys(audit.audit_dir).items():
        assert keys <= wanted, f"{name} holds the key of a step that was never applied"
    compare_with_scratch(world, tmp_path, audit, applied)


def failing_second_replace(real_replace):
    calls = []

    def replace(source, target):
        calls.append(target)
        if len(calls) == 2:
            raise OSError("disk full (made by the test)")
        return real_replace(source, target)
    return types.SimpleNamespace(replace=replace), calls


def prepared(world, tmp_path):
    """A applied at ResFinder (its run held), B tried at MLST and ResFinder's neighbour: B moves several files."""
    audit, trial = fresh(world, tmp_path)
    a = applied_step("T1:ResFinder", value=world.ids[0])
    held = audit.run_of(RECIPE_ID, [a], world.plans)
    tried = [step("T1:ResFinder", value=world.ids[1], node_id="b-1"), step("T1:MLST", value=world.ids[1], node_id="b-1")]
    assert trial.try_step(RECIPE_ID, [a], tried, world.plans).error is None
    return audit, trial, a, held, tried


def test_a_move_that_fails_halfway_leaves_no_mix_the_old_list_is_computed_again_and_nothing_of_the_tried_step_is_on_disk(world, tmp_path, monkeypatch):
    audit, trial, a, held, tried = prepared(world, tmp_path)
    fake, calls = failing_second_replace(os.replace)
    monkeypatch.setattr(audit_trial_module, "os", fake)
    with pytest.raises(TrialRefused) as refused:
        trial.apply_trial(RECIPE_ID, [a], tried, "second", world.plans)
    monkeypatch.undo()
    assert len(calls) == 2 and "could not be added" in str(refused.value) and "Nothing was applied" in str(refused.value) and "Try the step again" in str(refused.value)
    assert audit.run_of(RECIPE_ID, [a], world.plans) is not held                    # the memo was forgotten: no old run is served
    assert_a_reader_of_the_old_list_sees_only_the_old_list(world, tmp_path, audit, trial, [a])
    with pytest.raises(TrialRefused):
        trial.apply_trial(RECIPE_ID, [a], tried, "second", world.plans)               # the trial is gone: try again


def test_a_held_run_never_shows_the_tried_step_after_a_failed_apply(world, tmp_path, monkeypatch):
    audit, trial, a, held, tried = prepared(world, tmp_path)
    expected = held.audited_table_lazy("ResFinder", "T1").collect()
    fake, _ = failing_second_replace(os.replace)
    monkeypatch.setattr(audit_trial_module, "os", fake)
    with pytest.raises(TrialRefused):
        trial.apply_trial(RECIPE_ID, [a], tried, "second", world.plans)
    monkeypatch.undo()
    try:
        seen = held.audited_table_lazy("ResFinder", "T1").collect()
    except (OSError, Exception):                                                       # the file is gone: an error, never another table
        return
    assert seen.equals(expected)


@pytest.mark.parametrize("what", ["the clean-up after the moves", "the memo forgetting at the start"])
def test_a_failure_after_the_moves_or_before_them_is_all_or_nothing_for_the_reader(world, tmp_path, monkeypatch, what):
    audit, trial, a, held, tried = prepared(world, tmp_path)
    boom = {"n": 0}
    if what.startswith("the clean-up"):
        real = PlaceTrial.discard

        def discard(self):
            boom["n"] += 1
            if boom["n"] == 1:
                raise RuntimeError("clean-up failed (made by the test)")
            return real(self)
        monkeypatch.setattr(PlaceTrial, "discard", discard)
    else:
        real_forget = audit.forget

        def forget():
            boom["n"] += 1
            if boom["n"] == 1:
                raise RuntimeError("forget failed (made by the test)")
            return real_forget()
        monkeypatch.setattr(audit, "forget", forget)
    with pytest.raises(TrialRefused) as refused:
        trial.apply_trial(RECIPE_ID, [a], tried, "second", world.plans)
    monkeypatch.undo()
    assert "Nothing was applied" in str(refused.value) and boom["n"] >= 1
    assert audit.run_of(RECIPE_ID, [a], world.plans) is not held                    # the memo was forgotten whatever failed
    assert_a_reader_of_the_old_list_sees_only_the_old_list(world, tmp_path, audit, trial, [a])


def test_rows_before_at_a_place_is_the_audited_state_not_the_original_and_an_identical_step_changes_no_row(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    original = world.orch.materialize_tier1(RECIPE_ID, "ResFinder", world.anchors / "ResFinder.parquet").collect().height
    first = applied_step("T1:ResFinder", value=world.ids[0])
    audited = audit.run_of(RECIPE_ID, [first], world.plans).audited_table_lazy("ResFinder", "T1").collect().height
    assert audited < original
    result = trial.try_step(RECIPE_ID, [first], [step("T1:ResFinder", value=world.ids[1])], world.plans)
    effect = result.effects[0]
    assert effect.rows_before == audited != original and effect.rows_removed == audited - effect.rows_after > 0
    same = trial.try_step(RECIPE_ID, [first], [step("T1:ResFinder", value=world.ids[0])], world.plans)      # the same condition, another id
    assert same.error is None and same.effects[0].state == NO_ROW_CHANGED and same.effects[0].rows_removed == 0 and same.effects[0].rows_before == audited
    assert same.reaches and all(item.state == NO_ROW_CHANGED for item in same.reaches)
    assert trial.trial_table("ResFinder", "T1") is None and trial.trial_plot("amr_heatmap") is None


# -- clean_trials

def test_clean_trials_never_stops_for_an_unreadable_folder_and_the_start_of_the_app_goes_on(tmp_path, monkeypatch):
    root = tmp_path / TRIAL_FOLDER
    (root / "token").mkdir(parents=True)
    root.chmod(0o000)
    try:
        assert clean_trials(root) == []
        assert clean_trials(root, "token") == []                  # cannot be removed or read: not named, not raised
    finally:
        root.chmod(0o755)
    assert (root / "token").exists()
    from app.tests.test_cache_version_6 import REPO, _deployment
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE", "SPARMVET_CONNECTOR", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)
    deployment, anchors = _deployment(tmp_path / "dep")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(deployment))
    unreadable = anchors.parent / TRIAL_FOLDER
    (unreadable / "x").mkdir(parents=True)
    unreadable.chmod(0o000)
    from app.src.bootloader import Bootloader
    try:
        Bootloader()                                                      # the folder cannot be read: the app still starts
        monkeypatch.setattr(audit_trial_module, "clean_trials", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("made by the test")))
        Bootloader()                                                      # whatever clean_trials raises, the app still starts
    finally:
        unreadable.chmod(0o755)


def test_clean_trials_never_follows_a_link(tmp_path):
    target = tmp_path / "important_folder"
    target.mkdir()
    (target / "kept.txt").write_text("not scratch")
    link_root = tmp_path / "linked" / TRIAL_FOLDER
    link_root.parent.mkdir()
    link_root.symlink_to(target, target_is_directory=True)
    assert clean_trials(link_root) == [] and clean_trials(link_root, "kept.txt") == [] and (target / "kept.txt").read_text() == "not scratch"
    real_root = tmp_path / "real" / TRIAL_FOLDER
    real_root.mkdir(parents=True)
    (real_root / "token").symlink_to(target, target_is_directory=True)
    (real_root / "other").mkdir()
    assert clean_trials(real_root, "token") == [] and (target / "kept.txt").read_text() == "not scratch"
    assert clean_trials(real_root) == ["other"] and (target / "kept.txt").exists() and (real_root / "token").is_symlink()


def test_clean_trials_names_only_what_is_really_gone(tmp_path):
    root = tmp_path / TRIAL_FOLDER
    stuck = root / "stuck"
    (stuck / "inner").mkdir(parents=True)
    (stuck / "inner" / "file.parquet").write_bytes(b"x")
    (root / "free").mkdir()
    (stuck / "inner").chmod(0o500)                                         # the file inside cannot be deleted
    try:
        assert clean_trials(root) == ["free"]
        assert stuck.exists()
    finally:
        (stuck / "inner").chmod(0o755)
    assert clean_trials(root) == ["stuck"]


# -- the sentence the user sees

@pytest.mark.parametrize("what, make", [
    ("a column that is not there", lambda w: step("T1:ResFinder", params={"column": "no_such_column", "op": "eq", "value": "a", "na": "keep"})),
    ("a value of a type that does not fit", lambda w: step("T1:ResFinder", params={"column": "identity", "op": "eq", "value": "not a number", "na": "keep"})),
    ("an unknown kind of step", lambda w: step("T1:ResFinder", node_type="not_a_kind", params={"column": "sample_id"})),
    ("a step that lacks what it needs", lambda w: step("T1:ResFinder", params={"column": "sample_id"})),
    ("a key dropped where a later join reads it", lambda w: step("T1:ResFinder", node_type="drop_column", params={"column": "sample_id"})),
    ("a place the recipe does not have", lambda w: step("T1:NoSuchTable", value="a")),
])
def test_the_placeholder_reason_is_never_in_a_sentence_the_user_sees(world, tmp_path, what, make):
    audit, trial = fresh(world, tmp_path)
    result = trial.try_step(RECIPE_ID, [], [make(world)], world.plans)
    assert result.error, what
    assert TRIAL_REASON not in result.error and "Trial: this step" not in result.error, result.error
    with pytest.raises(TrialRefused) as refused:
        trial.apply_trial(RECIPE_ID, [], [make(world)], "a reason", world.plans)
    assert TRIAL_REASON not in str(refused.value)


# -- a folder emptied by someone else

def test_a_trial_whose_folder_was_emptied_by_someone_else_is_no_trial(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:ResFinder", value=world.victim)]
    first = trial.try_step(RECIPE_ID, [], tried, world.plans)
    assert trial.trial_table("ResFinder", "T1") is not None
    clean_trials(trial.trial_root, trial.token)                                  # the owner did not call discard()
    assert trial.trial_table("ResFinder", "T1") is None and trial.trial_plot("amr_heatmap") is None
    with pytest.raises(TrialRefused) as refused:
        trial.apply_trial(RECIPE_ID, [], tried, "a reason", world.plans)
    assert "Try the step again" in str(refused.value)
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    clean_trials(trial.trial_root, trial.token)
    again = trial.try_step(RECIPE_ID, [], tried, world.plans)                    # the same signature: computed again, not the stored result with no files
    assert again is not first and trial.trial_table("ResFinder", "T1").collect().height == again.effects[0].rows_after
    assert trial.apply_trial(RECIPE_ID, [], tried, "a reason", world.plans)


def test_a_trial_one_file_of_which_was_removed_is_no_trial_either(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    tried = [step("T1:MLST", value=world.ids[1])]
    trial.try_step(RECIPE_ID, [], tried, world.plans)
    (trial.trial_dir / "MLST.parquet").unlink()
    assert trial.trial_table("MLST", "T1") is None
    with pytest.raises(TrialRefused):
        trial.apply_trial(RECIPE_ID, [], tried, "r", world.plans)


# -- one id, one step

def test_a_tried_step_with_the_id_of_an_applied_step_is_refused_at_the_trial(world, tmp_path):
    audit, trial = fresh(world, tmp_path)
    earlier = applied_step("T1:ResFinder", value=world.ids[0])
    tried = [step("T1:MLST", value=world.ids[1], node_id=earlier["id"])]
    result = trial.try_step(RECIPE_ID, [earlier], tried, world.plans)
    assert result.error and earlier["id"] in result.error and "removed together" in result.error and result.effects == ()
    assert not trial.trial_dir.exists()
    with pytest.raises(TrialRefused):
        trial.apply_trial(RECIPE_ID, [earlier], tried, "r", world.plans)
    two_places = [step("T1:MLST", value=world.ids[1], node_id="same-decision"), step("T1:Bracken", value=world.ids[1], node_id="same-decision")]
    assert trial.try_step(RECIPE_ID, [earlier], two_places, world.plans).error is None          # one decision at two places is one id and is allowed


# -- one read of each table

class _Counted:
    def __init__(self, frame):
        self.frame, self.collects = frame, 0

    def collect(self):
        self.collects += 1
        return self.frame


def test_two_tables_are_compared_with_one_read_each_and_the_counts_first():
    import polars as pl
    base = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cases = [(base, base.clone(), (3, 3, True)), (base, base.head(2), (3, 2, False)), (base, base.with_columns(a=pl.Series([1, 2, 4])), (3, 3, False)),
             (base, base.select("a"), (3, 3, False)), (base, base.reverse(), (3, 3, False)), (base.head(0), base.head(0), (0, 0, True))]
    for left, right, expected in cases:
        a, b = _Counted(left), _Counted(right)
        assert compare_tables(a, b) == expected and (a.collects, b.collects) == (1, 1)
        assert same_table(_Counted(left), _Counted(right)) is expected[2]
