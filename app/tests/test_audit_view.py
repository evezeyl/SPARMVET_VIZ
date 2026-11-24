"""The audit of steps written at a place upstream of a plot, run by the engine (HOME audit, demo step 2): `app/modules/audit_view.py`, `audit_places.audit_copy_for`.

Proved on the demo `1_test_data_ST22_dummy` and its real data (the engine builds the tables):
- a filter written at the tier 1 of ResFinder (a sample removed) reaches the plots that are built from ResFinder and no plot beside them: those read their original table
  (`plot_table` is None) and are not affected; the table a plot below reads in the copy is its original table without the sample;
- the original's stored tables are byte for byte what they were (nothing is overwritten, nothing is served as audited);
- a filter at the tier 2 of ResFinder rebuilds only that tier 2 (the tier 1 table of the copy is the original's);
- removing the step gives the original back: the audit folder is gone, every plot reads its original table;
- the same steps run once (the run is kept), the same steps with another reason do not run again, other parameters do;
- a step the engine cannot apply is refused naming its id and its place, never skipped; a key dropped where a later join reads it, a place that does not exist and a step without a
  reason are refused in plain words and nothing is built.

Mutation index (each seen failing): MUTATION V1 `AuditRun.plot_table` returns None for every plot (the audited table is never read); MUTATION V2 `run_of` ignores the nodes
(always None); MUTATION V3 `nodes_signature` leaves the parameters out (the memo serves the old run).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_view.py -q
"""
import hashlib
from pathlib import Path
from unittest import mock

import polars as pl
import pytest

from app.modules.audit_places import PLACES_BUCKET, audit_copy_for, place_nodes
from app.modules.audit_run import AuditRunError, run_audit
from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from app.modules.session_manager import make_audit_step
from blueprint_arch.t3_translator import UntranslatableNode
from utils.audit_copy import AuditCopyError, start_audit
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
RECIPE_ID = "1_test_data_ST22_dummy"
PIPELINES = ROOT / "config" / "data_analysis_recipes" / "pipelines"


class World:
    def __init__(self, root: Path):
        clear_data_analysis_recipe_cache()
        self.orch = DataOrchestrator(PIPELINES, ROOT / "assets" / "test_data")
        self.loaded = load_data_analysis_recipe(PIPELINES / f"{RECIPE_ID}.yaml")
        self.graph = build_graph(self.loaded.raw)
        self.plans = compose_plan_book(self.orch, RECIPE_ID, self.loaded, self.graph)
        self.anchors, self.audit_dir = root / "anchors", root / "audit_anchors"
        base = run_audit(self.orch, RECIPE_ID, start_audit(self.loaded.raw, "1a2b3c4d").recipe, self.anchors, root / "audit_none")
        self.ids = sorted(pl.read_parquet(base.tables["ResFinder"].t1_path)["sample_id"].drop_nulls().unique().to_list())
        self.victim = self.ids[0]
        self.below = {p for p in self.graph.plots() if f"T3:{p}" in self.graph.below("T1:ResFinder")}

    def stored(self):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(self.anchors.glob("*.parquet"))}

    def audit(self):
        return PlaceAudit(self.orch, self.anchors, self.audit_dir)

    def node(self, place="T1:ResFinder", value=None, column="sample_id", reason="the sample was resequenced", node_type="filter_row", params=None):
        params = params if params is not None else {"column": column, "op": "ne", "value": value or self.victim, "na": "keep"}
        return make_audit_step(node_type, params, plot_scope=PLACES_BUCKET, reason=reason, place=place, started_from="subtab_amr_heatmap")

    def original_table(self, plot_id):
        return self.orch.materialize_tier3(RECIPE_ID, plot_id, self.anchors).collect()


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    yield World(tmp_path_factory.mktemp("audit_view"))
    clear_data_analysis_recipe_cache()


def test_a_filter_at_tier1_of_resfinder_reaches_the_plots_below_it_and_no_plot_beside_it(world):
    audit = world.audit()
    nodes = [world.node()]
    before = world.stored()
    affected = set(audit.affected_plots(RECIPE_ID, nodes, world.plans))
    assert "amr_heatmap" in affected and affected <= world.below, (affected, world.below)
    beside = [p for p in world.graph.plots() if p not in world.below]
    assert beside and all(audit.plot_lazy(RECIPE_ID, p, nodes, world.plans) is None for p in beside), "a plot beside the place reads its original table"
    assert "mlst_bar" in beside
    audited = audit.plot_lazy(RECIPE_ID, "amr_heatmap", nodes, world.plans).collect()
    original = world.original_table("amr_heatmap")
    assert world.victim in original["sample_id"].to_list() and world.victim not in audited["sample_id"].to_list()
    assert audited.height < original.height
    assert audited.equals(original.filter(pl.col("sample_id") != world.victim)), "the audited table is the original without the sample, nothing else changed"
    assert world.stored() == before, "the original's stored tables are byte-identical: nothing was overwritten"
    # every plot below the place has a key of its own (the plot_table of a plot whose key equals the original's is None)
    run = audit.run_of(RECIPE_ID, nodes, world.plans)
    assert all(run.plots[p].reused is False for p in affected)


def test_a_filter_at_tier2_of_resfinder_rebuilds_only_that_tier2(world):
    audit = world.audit()
    nodes = [world.node(place="T2:ResFinder")]
    run = audit.run_of(RECIPE_ID, nodes, world.plans)
    table = run.tables["ResFinder"]
    assert table.t1 == "original" and table.t2 == "built"
    assert audit.affected_plots(RECIPE_ID, nodes, world.plans) == ["amr_heatmap"]
    assert world.victim not in audit.plot_lazy(RECIPE_ID, "amr_heatmap", nodes, world.plans).collect()["sample_id"].to_list()


def test_removing_the_step_gives_the_original_back_and_leaves_no_file(world):
    audit = world.audit()
    nodes = [world.node()]
    assert audit.run_of(RECIPE_ID, nodes, world.plans) is not None and world.audit_dir.exists()
    assert audit.run_of(RECIPE_ID, [], world.plans) is None
    assert not world.audit_dir.exists(), "what the audit built is removed with the last step"
    assert audit.plot_lazy(RECIPE_ID, "amr_heatmap", [], world.plans) is None
    assert audit.affected_plots(RECIPE_ID, [], world.plans) == []


def other_id(audit):
    return audit._memo[0][3][0][0]


def test_the_same_steps_run_once_a_new_reason_does_not_run_again_other_parameters_do(world):
    audit = world.audit()
    node = world.node()
    with mock.patch("app.modules.audit_view.run_audit", wraps=run_audit) as run:
        first = audit.run_of(RECIPE_ID, [node], world.plans)
        assert audit.run_of(RECIPE_ID, [node], world.plans) is first and run.call_count == 1
        again = audit.run_of(RECIPE_ID, [{**node, "reason": "another reason, same data"}], world.plans)
        assert again is first and run.call_count == 1, "the reason changes no data"
        other = audit.run_of(RECIPE_ID, [world.node(value=world.ids[1])], world.plans)
        assert other is not first and run.call_count == 2
        edited = audit.run_of(RECIPE_ID, [{**world.node(value=world.ids[1]) | {"id": other_id(audit)}, "params": {**node["params"], "value": world.ids[2]}}], world.plans)
        assert edited is not other and run.call_count == 3, "the same id with another value is another audit"


def test_two_steps_at_two_places_apply_in_order_each_after_the_author_steps(world):
    audit = world.audit()
    nodes = [world.node(place="T1:ResFinder", value=world.ids[0]), world.node(place="T2:ResFinder", value=world.ids[1])]
    got = audit.plot_lazy(RECIPE_ID, "amr_heatmap", nodes, world.plans).collect()
    gone = {world.ids[0], world.ids[1]}
    assert not gone & set(got["sample_id"].to_list())
    assert got.equals(world.original_table("amr_heatmap").filter(~pl.col("sample_id").is_in(list(gone))))


def test_a_step_the_engine_cannot_apply_is_refused_with_its_id_and_its_place_never_skipped(world):
    audit = world.audit()
    audit.run_of(RECIPE_ID, [], world.plans)         # an empty audit folder to begin with: what an earlier run left is kept by a refused one, it is not what this run built
    bad = world.node(column="no_such_column", params={"column": "no_such_column", "op": "eq", "value": "x", "na": "remove"})
    with pytest.raises(AuditRunError) as excinfo:
        audit.run_of(RECIPE_ID, [bad], world.plans)
    assert "T1:ResFinder" in str(excinfo.value) and "audit_" in str(excinfo.value)
    assert not world.audit_dir.exists() or not any(world.audit_dir.rglob("*.parquet")), "a run that failed leaves nothing it built"


def test_a_key_dropped_where_a_later_join_reads_it_a_missing_place_and_a_missing_reason_are_refused_before_anything_is_built(world):
    audit = world.audit()
    audit.run_of(RECIPE_ID, [], world.plans)
    drop_key = world.node(node_type="drop_column", params={"column": "sample_id"})
    with pytest.raises(AuditCopyError, match="sample_id"):
        audit.run_of(RECIPE_ID, [drop_key], world.plans)
    with pytest.raises(AuditCopyError, match="no table or join"):
        audit.run_of(RECIPE_ID, [world.node(place="T1:no_such_table")], world.plans)
    with pytest.raises(AuditCopyError, match="reason"):
        audit.run_of(RECIPE_ID, [world.node(reason="")], world.plans)
    assert not world.audit_dir.exists() or not any(world.audit_dir.rglob("*.parquet"))


def test_a_node_with_no_registered_action_is_refused_in_plain_words(world):
    with pytest.raises(UntranslatableNode):
        audit_copy_for(world.loaded.raw, [world.node(node_type="aesthetic_override", params={"fill": "red"})], world.plans)


def test_place_nodes_are_the_active_nodes_of_the_bucket_in_commit_order():
    a, b = {"id": "a", "place": "T1:X"}, {"id": "b", "place": "T1:Y", "active": False}
    plain = {"id": "c"}
    assert place_nodes({PLACES_BUCKET: [a, b, plain], "subtab_p": [{"id": "z", "place": "T1:X"}]}) == [a]
    assert place_nodes({}) == [] and place_nodes(None) == []
