"""The place reader (`app/modules/audit_place_view.py`) walked over every place of every shipped recipe that builds with its shipped data, with NO audit step (HOME audit, demo slice 2).

What this tests (the design expects: the one reader gives, for every place the lineage panel offers, the table the orchestrator builds for that place, and nothing else; with no audit step it is
the original and it says so; a place that cannot be chosen is refused with a reason and the default is shown):
- every choosable node of `lineage_of` of the seven recipes of the golden baseline (`app/tests/golden/baseline.json`, the recipes that build with `assets/test_data`): `viewed` names that place,
  `table_for` returns exactly what the orchestrator gives for it (same columns, same rows in the same order), the facts say "original, no audit step yet";
- the same tables equal the golden baseline's record of the table's tier 1 and tier 2 (rows, ordered columns with types, content hash) where the baseline holds the table: a check that does not depend on the reader or the orchestrator
  call written here;
- the columns of the table equal the engine's plan that the lineage holds for the node (D-0630: what the screen can be told about a place is what the place holds);
- Exploration, for every plot of every recipe and each data choice (T1, T2, T3): the original of that choice, as HOME reads it today (a table with no tier-2 steps gives its tier 1 at T2);
- the nodes that are not places (a tier 2 no plot reads) are refused with their reason and the default is shown.
Nodes and recipes that are skipped are printed with the reason (`-s`); nothing is skipped silently.

Mutation index (each seen failing): MUTATION P1 `table_for` reads the tier-2 reader for a T1 place; P2 `table_for` ignores the audited reader's answer (always the original); P3 `viewed` ignores the first chosen
place (always the default). See test_audit_place_view.py for the others.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_place_view_walk.py -q -s
"""
import importlib.util
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.audit_place_view import AUDIT, EXPLORATION, NO_SOURCE_NOTE, Readers, table_for, view_identity, viewed
from app.modules.audit_view import PlaceAudit
from app.modules.session_manager import make_audit_step
from app.tests.test_export_unread_tables import Wide, _source
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from utils.lineage_data import lineage_of
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))
RECIPES, RAW = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]


def _golden():
    spec = importlib.util.spec_from_file_location("golden_baseline", ROOT / "assets" / "scripts" / "golden_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GOLDEN = _golden()


class Walk:
    """One recipe built for the walk: the orchestrator, the graph, the plan book, the lineage and the readers with no audit."""

    def __init__(self, recipe_id: str, anchors: Path):
        clear_data_analysis_recipe_cache()
        self.recipe_id = recipe_id
        self.anchors = anchors
        self.orch = DataOrchestrator(RECIPES, RAW)
        self.loaded = load_data_analysis_recipe(RECIPES / f"{recipe_id}.yaml")
        self.graph = build_graph(self.loaded.raw)
        self.plans = compose_plan_book(self.orch, recipe_id, self.loaded, self.graph)
        self.lineage = lineage_of(self.loaded.raw, self.plans)
        self.readers = Readers(
            source=lambda t: self.orch.read_source(recipe_id, t),
            tier1=lambda t: self.orch.materialize_tier1(recipe_id, t, anchors / f"{t}.parquet"),
            tier2=lambda t: self.orch.materialize_tier2(recipe_id, t, anchors / f"{t}.parquet"),
            plot=lambda p: self.orch.materialize_tier3(recipe_id, p, anchors),
            audited_table=lambda t, tier: None,
            audited_plot=lambda p: None,
            committed_steps=0)

    def expected(self, node):
        """What the orchestrator gives for a node, written here and not through the reader under test."""
        if node.kind == "T3":
            return self.orch.materialize_tier3(self.recipe_id, node.name, self.anchors).collect()
        if node.kind == "T2":
            return self.orch.materialize_tier2(self.recipe_id, node.name, self.anchors / f"{node.name}.parquet").collect()
        return self.orch.materialize_tier1(self.recipe_id, node.name, self.anchors / f"{node.name}.parquet").collect()


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    made = {}

    def get(recipe_id):
        if recipe_id not in made:
            made[recipe_id] = Walk(recipe_id, tmp_path_factory.mktemp(recipe_id) / "anchors")
        return made[recipe_id]

    yield get
    clear_data_analysis_recipe_cache()


@pytest.mark.parametrize("recipe_id", sorted(BASELINE["recipes"]))
def test_every_place_of_the_lineage_gives_the_table_the_orchestrator_builds_and_says_it_is_the_original(recipe_id, worlds):
    walk = worlds(recipe_id)
    golden = BASELINE["recipes"][recipe_id]
    walked, refused = 0, 0
    for node in walk.lineage.nodes:
        shown = viewed(AUDIT, "T3", None, None, [node.id], walk.graph, walk.lineage)
        if not node.choosable:
            assert shown.is_default and shown.place is None and [p for p, _ in shown.refused] == [node.id], node.id
            assert shown.refused[0][1] == node.not_choosable_reason
            refused += 1
            continue
        assert shown.place == node.id and not shown.is_default and shown.mode == AUDIT and shown.refused == (), node.id
        assert shown.tier == f"T{node.tier}", node.id
        assert shown.table == (walk.graph.plot_target(node.name) if node.kind == "T3" else node.name)
        frame, facts = table_for(shown, walk.readers)
        got = frame.collect()
        want = walk.expected(node)
        assert got.equals(want) and got.schema == want.schema, f"{recipe_id} {node.id}: not the table the orchestrator builds"
        assert facts.state == "original" and "No audit step has been added yet" in facts.why_original and facts.place == node.id
        if node.columns is not None:     # the engine's plan: what the lineage says the place holds is what it holds
            assert [(n, str(t)) for n, t in got.schema.items()] == list(node.columns), f"{recipe_id} {node.id}: the plan and the table differ"
        # the golden baseline, written before this reader existed: the same rows, columns with types and content hash
        record = GOLDEN.table_record(got)
        # (the baseline's plot records hold the data after the plot engine's conversion, not the table the plot reads: they are not compared here)
        if node.kind in ("T1", "result") and node.name in golden["t1"]:
            assert record == golden["t1"][node.name], (recipe_id, node.id)
        elif node.kind == "T2" and node.name in golden["t2"]:
            assert record == golden["t2"][node.name], (recipe_id, node.id)
        walked += 1
    print(f"\n{recipe_id}: {walked} places walked, {refused} nodes refused as not places, {len(walk.lineage.nodes)} nodes in the lineage")
    assert walked + refused == len(walk.lineage.nodes) and walked > 0


@pytest.mark.parametrize("recipe_id", sorted(BASELINE["recipes"]))
def test_exploration_reads_the_original_of_each_data_choice_for_every_plot(recipe_id, worlds):
    walk = worlds(recipe_id)
    golden = BASELINE["recipes"][recipe_id]
    for plot in walk.graph.plots():
        target = walk.graph.plot_target(plot)
        for choice, want_frame in (("T1", lambda: walk.orch.materialize_tier1(recipe_id, target, walk.anchors / f"{target}.parquet")),
                                   ("T2", lambda: walk.orch.materialize_tier2(recipe_id, target, walk.anchors / f"{target}.parquet")),
                                   ("T3", lambda: walk.orch.materialize_tier3(recipe_id, plot, walk.anchors))):
            shown = viewed(EXPLORATION, choice, None, plot, [f"T1:{target}"], walk.graph, walk.lineage)
            assert shown.place is None and not shown.is_default and shown.tier == choice and shown.table == target and shown.from_open_plot is True
            frame, facts = table_for(shown, walk.readers)
            assert frame.collect().equals(want_frame().collect()), (recipe_id, plot, choice)
            assert facts.state == "original" and facts.mode == EXPLORATION
        assert GOLDEN.table_record(table_for(viewed(EXPLORATION, "T1", None, plot, [], walk.graph, walk.lineage), walk.readers)[0].collect()) == golden["t1"][target]
        assert GOLDEN.table_record(table_for(viewed(EXPLORATION, "T2", None, plot, [], walk.graph, walk.lineage), walk.readers)[0].collect()) == golden["t2"][target]


def test_the_source_choice_reads_the_file_as_read(worlds):
    walk = worlds("1_test_data_ST22_dummy")
    table = walk.graph.source_tables("T3:amr_heatmap")
    names = [walk.graph.node(n).name for n in table]
    assert names
    shown = viewed(EXPLORATION, "SRC", names[0], "amr_heatmap", [], walk.graph, walk.lineage)
    frame, facts = table_for(shown, walk.readers)
    assert shown.tier == "Source" and shown.table == names[0] and facts.state == "original"
    assert frame.collect().equals(walk.orch.read_source(walk.recipe_id, names[0]).collect())


@pytest.mark.parametrize("recipe_id", sorted(BASELINE["recipes"]))
def test_every_place_is_shown_with_no_plot_open_and_says_whether_a_plot_reads_it(recipe_id, worlds):
    """The place alone drives the view in Audit mode (owner, 2026-11-26): no open plot is needed."""
    walk = worlds(recipe_id)
    walked = 0
    for node in walk.lineage.nodes:
        if not node.choosable:
            continue
        shown = viewed(AUDIT, "T3", None, None, [node.id], walk.graph, walk.lineage)
        assert shown.place == node.id and shown.plot is None and shown.from_open_plot is None and not shown.nothing_chosen and shown.refused == ()
        assert shown.no_plot_reads is (walk.graph.plots_reading(node.id) == []), node.id
        frame, facts = table_for(shown, walk.readers)
        assert frame.collect().equals(walk.expected(node)) and facts.state == "original" and facts.no_plot_reads is shown.no_plot_reads, node.id
        key = view_identity(shown, recipe_id)
        assert key == view_identity(viewed(AUDIT, "T3", None, None, [node.id], walk.graph, walk.lineage), recipe_id) and key[1] == "audit"
        walked += 1
    assert walked > 0
    nothing = viewed(AUDIT, "T3", None, None, [], walk.graph, walk.lineage)
    assert nothing.nothing_chosen and table_for(nothing, walk.readers)[0] is None
    print(f"\n{recipe_id}: {walked} places shown with no plot open")


class NoPlot(Wide):
    """A made-up recipe with tables and NO plot: T (read by the join C), U (read by nothing) and V (read by the join D); D (a join nothing reads)."""

    def write_data_analysis_recipe(self, **_ignored) -> None:
        super().write_data_analysis_recipe()
        entry = self.data_analysis_recipes_dir / "tiny.yaml"
        text = entry.read_text()
        # `analysis_groups: {}` is refused by ConfigManager (config_loader.py:193); a group with no plot loads, which is the nearest the loader allows to a recipe with no plot
        entry.write_text(text[:text.index("analysis_groups:")] + "analysis_groups:\n  g:\n    ui_label: G\n    plots: {}\n")


def audit_step(place, column="group", op="eq", value="A", dtype="String"):
    return make_audit_step("filter_row", {"column": column, "op": op, "value": value, "dtype": dtype, "na": "remove"}, reason="keep it", place=place, started_from="none")


@pytest.mark.parametrize("label", ["no step", "a step at T", "a step at the join D nothing reads", "a step at U", "steps at T and U"])
def test_a_recipe_with_no_plot_shows_every_table_in_audit_mode_and_the_exploration_says_there_is_nothing(tmp_path, label):
    nodes = {"no step": [], "a step at T": [audit_step("T1:T")], "a step at the join D nothing reads": [audit_step("T1:D", "color", "eq", "red")],
             "a step at U": [audit_step("T1:U", "weight", "gt", 2, "Float64")], "steps at T and U": [audit_step("T1:T"), audit_step("T1:U", "weight", "gt", 2, "Float64")]}[label]
    clear_data_analysis_recipe_cache()
    world = NoPlot(tmp_path)
    loaded = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml")
    graph = build_graph(loaded.raw)
    assert graph.plots() == [], "the made-up recipe has no plot"
    plans = compose_plan_book(world.orch, "tiny", loaded, graph)
    lineage = lineage_of(loaded.raw, plans)
    anchors = world.root / "user" / "anchors"
    audit = PlaceAudit(world.orch, anchors, world.root / "user" / "audit_anchors")
    readers = Readers(
        source=lambda t: world.orch.read_source("tiny", t),
        tier1=lambda t: world.orch.materialize_tier1("tiny", t, anchors / f"{t}.parquet"),
        tier2=lambda t: world.orch.materialize_tier2("tiny", t, anchors / f"{t}.parquet"),
        plot=lambda p: world.orch.materialize_tier3("tiny", p, anchors),
        audited_table=lambda t, tier: audit.table_lazy("tiny", t, tier, nodes, plans),
        audited_plot=lambda p: audit.plot_lazy("tiny", p, nodes, plans),
        committed_steps=len(nodes))
    run = audit.run_of("tiny", nodes, plans)
    frames = run.audited_frames() if run is not None else {}
    assert [n.id for n in lineage.nodes if n.choosable] == ["T1:T", "T1:U", "T1:V", "T1:C", "T1:D"]
    for node in lineage.nodes:
        shown = viewed(AUDIT, "T3", None, None, [node.id], graph, lineage)
        assert shown.place == node.id and shown.no_plot_reads is True and shown.from_open_plot is None, "no plot reads any table of this recipe"
        frame, facts = table_for(shown, readers)
        original = world.orch.materialize_tier1("tiny", node.name, anchors / f"{node.name}.parquet").collect()
        expected = frames.get(node.name, {}).get("T1")
        if expected is None:
            assert frame.collect().equals(original) and facts.state == "original", (label, node.id)
        else:
            assert frame.collect().equals(expected) and facts.state == "audited" and not expected.equals(original), (label, node.id)
        assert facts.no_plot_reads is True
    assert sum(1 for t in frames if "T1" in frames[t]) == len(frames)
    if nodes:
        assert frames, "a step that changes no table proves nothing"
    # with no place chosen and no plot, nothing is chosen for the user, in Audit mode; in Exploration nothing can be shown
    assert viewed(AUDIT, "T3", None, None, [], graph, lineage).nothing_chosen
    for choice in ("SRC", "T1", "T2", "T3"):
        state = viewed(EXPLORATION, choice, "T", None, [], graph, lineage)
        assert state.nothing_chosen and "no plot" in state.note and table_for(state, readers)[0] is None, choice
    clear_data_analysis_recipe_cache()


def test_the_source_choice_with_no_source_table_is_a_value_not_an_exception(worlds):
    """A plot that reads no source table (reproduced on `3_test_no_joins`): HOME says so in plain words today; the reader gives the nothing-to-show value with its own note."""
    walk = worlds("3_test_no_joins")
    plot = walk.graph.plots()[0]
    for source in (None, ""):
        shown = viewed(EXPLORATION, "SRC", source, plot, [], walk.graph, walk.lineage)
        assert shown.nothing_chosen and shown.table is None and shown.tier == "Source" and shown.note == NO_SOURCE_NOTE and shown.from_open_plot is True
        frame, facts = table_for(shown, walk.readers)
        assert frame is None and facts.state == "original" and facts.why_original == NO_SOURCE_NOTE
    assert "no source table" in NO_SOURCE_NOTE
    # with a source table the view is as before
    assert not viewed(EXPLORATION, "SRC", "MLST", plot, [], walk.graph, walk.lineage).nothing_chosen
