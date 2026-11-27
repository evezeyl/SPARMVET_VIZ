"""The lineage data function on the demo recipe `1_test_data_ST22_dummy`, with the engine's plan (LINEAGE-DATA-FUNCTION, D-0627, D-0630 to D-0632).

What is proved (the design expects: the data function gives the lineage of the real recipe, the columns are the engine's plan and equal the table really built, and the metadata is
no place anywhere a place is offered or written):
- the demo's counts: nodes per kind, no file node, no metadata node, the eleven tables that take the metadata in are tagged, every joined table has all its ingredient parents;
- the six tables nobody reads are leaves, they can be chosen as a place and have no step after them;
- the independent graphs and their original parents (the metadata no longer joins them: six graphs);
- two plots read ResFinder through different tables (its tier 2, and the joins that read its tier 1): the paths and their steps are listed for each result;
- the columns of a node are the plan's names and types at the end of its steps and equal the table really built (ResFinder with its marker column, a join, a table with tier-2 steps);
- D-0632: the metadata is never a place: it cannot be shown or tried (`request_to_show`, `trial_places` say it in one line, FLOW-3: the dialog's `place_lines` and `choice_problem` are gone);
  an audit step at the metadata is refused by the audit copy (this is what a stored session meets: Restore puts a stored step into the view and the first read of the copy refuses it, never skipping it).

Mutation index (each seen failing): MUTATION A1 `lineage_of` reads the columns at the start of the node (k = 0); A2 `request_to_show` allows the metadata again.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_lineage_data_demo.py -q
"""
import json
from collections import Counter
from pathlib import Path

import pytest

from app.modules.audit_places import audit_copy_for
from app.modules.audit_shown import request_to_show
from app.modules.audit_try import trial_places
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from app.modules.session_manager import make_audit_step
from utils import recipe_tiers
from utils.audit_copy import AuditCopyError
from utils.lineage_data import lineage_of
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))
RECIPES, RAW = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]
DEMO = "1_test_data_ST22_dummy"
META = recipe_tiers.METADATA_SCHEMA


@pytest.fixture(scope="module")
def world():
    clear_data_analysis_recipe_cache()
    orch = DataOrchestrator(RECIPES, RAW)
    loaded = load_data_analysis_recipe(RECIPES / f"{DEMO}.yaml")
    graph = build_graph(loaded.raw)
    book = compose_plan_book(orch, DEMO, loaded, graph)
    yield orch, loaded, graph, book, lineage_of(loaded.raw, book)
    clear_data_analysis_recipe_cache()


def test_the_demo_has_the_expected_nodes_and_no_file_and_no_metadata(world):
    _, _, graph, _, lin = world
    assert Counter(n.kind for n in lin.nodes) == {"T1": 21, "T3": 17, "T2": 7, "result": 6}
    assert not any(n.id.startswith("DS:") or n.name == META for n in lin.nodes)
    assert lin.metadata_table == META and len(lin.edges) == 48
    assert [n.name for n in lin.nodes if n.kind == "T3"] == graph.plots()
    tagged = [n.name for n in lin.nodes if n.brings_metadata]
    assert len(tagged) == 11 and "ST22_Anchor" in tagged and "ResFinder" not in tagged


def test_every_joined_table_has_all_its_ingredients_as_parents_except_the_metadata(world):
    _, _, graph, _, lin = world
    for n in lin.nodes:
        if n.kind in ("T1", "result") and n.table_kind == "joined":
            expected = {f"T1:{graph.node(p).name}" for p in graph.parents(n.id) if graph.node(p).name != META}
            have = {p for p, c in lin.edges if c == n.id}
            assert have == expected, n.id
    assert [p for p, c in lin.edges if c == "T1:ST22_Anchor"] == [f"T1:{t}" for t in ("FastP", "ResFinder", "MLST", "VirulenceFinder", "APEC_STEC_virulence_genes")]


def test_the_six_tables_nobody_reads_are_leaves_that_can_be_chosen(world):
    lin = world[4]
    leaves = [n for n in lin.nodes if n.kind == "result"]
    assert [n.name for n in leaves] == ["Quality_metrics", "Detailed_summary", "FastP_with_metadata", "Bracken_with_metadata", "ResFinder_with_metadata", "AR1_MLST_Serotype_Virulence"]
    for n in leaves:
        assert n.choosable and lin.reach[n.id].results == (n.id,) and lin.reach[n.id].built_from == ()
        assert [len(p.steps) for p in lin.reach[n.id].paths[n.id]] == [0]


def test_the_independent_graphs_and_their_original_parents(world):
    lin = world[4]
    assert [len(c.nodes) for c in lin.components] == [6, 1, 1, 37, 3, 3]
    big = lin.components[3]
    assert big.parents == tuple(f"T1:{t}" for t in ("FastP", "Quast", "Bracken", "ResFinder", "MLST", "VirulenceFinder", "APEC_STEC_virulence_genes")) and big.first_places == big.parents
    assert lin.components[0].parents == ("T1:Summary", "T1:Summary_quality")
    assert sorted(n for c in lin.components for n in c.nodes) == sorted(n.id for n in lin.nodes)


def test_a_place_reaches_each_result_by_its_paths_with_the_steps_on_them(world):
    lin = world[4]
    reach = lin.reach["T1:ResFinder"]
    assert reach.results == ("T1:ResFinder_with_metadata", "T3:amr_heatmap", "T3:virulence_bar", "T3:virulence_variants", "T3:qa_amr_genes_per_sample", "T3:qa_fanout_rows_per_sample")
    heat = reach.paths["T3:amr_heatmap"]
    assert [p.nodes for p in heat] == [("T2:ResFinder", "T3:amr_heatmap")] and [s.node for s in heat[0].steps][:2] == ["T2:ResFinder", "T2:ResFinder"] and heat[0].steps[-1].node == "T3:amr_heatmap"
    via_join = reach.paths["T3:virulence_bar"]
    assert via_join[0].nodes == ("T1:ST22_Anchor", "T2:ST22_Anchor", "T3:virulence_bar")
    assert "polars_join: left with ResFinder on sample_id" in [s.text for s in via_join[0].steps]
    # the step lines carry the join kind and the other table
    assert all(s.text for p in via_join for s in p.steps)


def test_the_columns_are_the_engines_plan_and_equal_the_table_really_built(world, tmp_path):
    orch, loaded, _, book, lin = world
    for table in ("ResFinder", "MLST_with_metadata", "ST22_Anchor"):
        node = lin.node(f"T1:{table}")
        built = orch.materialize_tier1(DEMO, table, tmp_path / f"{table}.parquet").collect_schema()
        assert node.columns == tuple((n, str(t)) for n, t in built.items()) and node.columns_note == ""
        assert node.columns == book.get(node.id, node.n_steps).columns          # the plan itself, at the end of the node's steps
    marker = [n for n, _ in lin.node("T1:ResFinder").columns if n.endswith("_not_in_original_data")]
    assert marker == ["ResFinder_not_in_original_data"]                      # a marker column of the completion is a column like another
    assert lin.node("T2:ResFinder").columns == book.get("T2:ResFinder", 2).columns


def test_without_the_book_no_column_is_given(world):
    lin = lineage_of(world[1].raw)
    assert all(n.columns is None and n.columns_note for n in lin.nodes)


def test_the_metadata_is_never_offered_as_a_place(world):
    _, _, graph, book, lin = world
    holds = [c for c, _ in book.get(f"T1:{META}", 0).columns if c == "sample_id"]
    assert holds                                                              # the metadata does hold the column the step is about
    for place in (f"T1:{META}", f"T2:{META}"):
        outcome = request_to_show(place, [], graph, lin)
        assert outcome.place is None and recipe_tiers.METADATA_NOT_A_PLACE in outcome.problem, outcome
        places, problem = trial_places("T1:ResFinder", [place], graph, lin)
        assert places == () and problem, "a trial is never written at the metadata"
    assert request_to_show("T1:ResFinder", [], graph, lin).place == "T1:ResFinder"
    assert trial_places("T1:ResFinder", [], graph, lin) == (("T1:ResFinder",), "")


def test_a_stored_step_at_the_metadata_is_refused_by_the_audit_copy_with_the_plain_line(world):
    raw = world[1].raw
    node = make_audit_step("filter_row", {"column": "sample_id", "op": "ne", "value": "x", "na": "keep"}, plot_scope="__places__", reason="why", place=f"T1:{META}")
    with pytest.raises(AuditCopyError, match="metadata table is not a place"):
        audit_copy_for(raw, [node])
    ok = make_audit_step("filter_row", {"column": "sample_id", "op": "ne", "value": "x", "na": "keep"}, plot_scope="__places__", reason="why", place="T1:ResFinder")
    assert audit_copy_for(raw, [ok]).created == 1
