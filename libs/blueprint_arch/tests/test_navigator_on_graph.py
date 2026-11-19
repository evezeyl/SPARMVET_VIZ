"""Blueprint's navigator and tube map take the structure of a recipe from the one recipe graph (`utils.recipe_graph`), D-0031.

What is held here:
- on every shipped recipe, what the navigator and the tube map say about the structure (the ingredients of a join, the table a plot
  reads, the sources of a plot) equals what the recipe graph says; the two cannot drift apart because the navigator asks the graph;
- a recipe the graph cannot draw (an ingredient that is no table, a plot with no table, a cycle of joins, a repeated id, a file that is not
  a recipe) still opens: the rest of the map is given, what was left out is listed with its place, nothing is hidden and nothing crashes
  (Blueprint reports and never crashes, D-0029);
- the navigator and the mapper keep no description of their own of what feeds what.

One-time comparison with the code before this change (scratch, not a test): the five navigator functions, `resolve_fields_for_schema`,
the cytoscape and the mermaid maps were dumped for the 54 recipes of the project that have an `analysis_groups` key before the
change and after it: byte-identical (2.7 MB of JSON).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_navigator_on_graph.py -q

# @deps
# consumes: libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py, libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py, libs/utils/src/utils/recipe_graph.py, libs/utils/src/utils/recipe_factory.py, libs/utils/src/utils/recipe_loader.py
# doc: .claude/knowledge/architecture_decisions.md#adr-099, .claude/knowledge/decision_ledger.md (D-0031, D-0029)
# @end_deps
"""
import copy
import glob
import json
import re
from pathlib import Path

import pytest

from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_recipe
from utils.recipe_graph import build_graph
from utils.recipe_loader import load_recipe

from blueprint_arch import blueprint_mapper, data_analysis_recipe_navigator as navigator
from blueprint_arch.blueprint_mapper import BlueprintMapper
from blueprint_arch.data_analysis_recipe_navigator import (
    build_lineage_chain, build_plot_lineage, build_schema_registry, build_sibling_map, get_plot_ids_in_group, recipe_structure,
    recipe_structure_of_file)

ROOT = Path(__file__).resolve().parents[3]
SHIPPED = sorted(
    glob.glob(str(ROOT / "config" / "data_analysis_recipes" / "*" / "*.yaml"))
    + glob.glob(str(ROOT / "assets" / "gallery_data" / "*" / "data_analysis_recipe.yaml"))
    + glob.glob(str(ROOT / "app" / "tests" / "equality" / "recipes" / "*.yaml")))
SHIPPED = [p for p in SHIPPED if "analysis_groups" in Path(p).read_text(encoding="utf-8", errors="replace")]
STEP = {"action": "polars_select", "exprs": ["sample_id"]}


def safe(text):
    return re.sub(r"[^A-Za-z0-9_]", "_", text)


def cy(raw):
    return json.loads(BlueprintMapper(raw).generate_cy_elements())


def node_ids(elements):
    return {e["data"]["id"] for e in elements if "source" not in e["data"]}


def edges(elements):
    return {(e["data"]["source"], e["data"]["target"]) for e in elements if "source" in e["data"]}


# ---------------------------------------------------------------- every shipped recipe, against the graph ----------------------

def test_there_are_shipped_recipes_to_sweep():
    assert len(SHIPPED) >= 40


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_the_navigator_and_the_map_say_what_the_graph_says(path):
    raw, _ = load_recipe(path)
    graph = build_graph(raw)
    structure = recipe_structure_of_file(path)
    assert structure.left_out == () and structure.graph.nodes() == graph.nodes(), "a shipped recipe must be drawn whole"

    ctx = build_sibling_map(path)
    registry = build_schema_registry(path, {})
    for table in graph.collections():
        if graph.node(f"T1:{table}").collection_kind != "join":
            continue
        expected = [graph.node(parent).name for parent in graph.parents(f"T1:{table}")]
        assert registry[table]["ingredients"] == expected
        assert {entry["schema_id"]: entry["ingredients"] for entry in ctx.values() if entry["role"] == "join"}[table] == expected
    for plot in graph.plots():
        assert registry[plot]["target_dataset"] == graph.plot_target(plot)
        steps = build_plot_lineage(plot, path)
        assert steps[-1]["type"] == "plot_spec" and steps[-1]["schema_id"] == plot
        sources = [s["schema_id"] for s in steps if s["type"] == "data_source"]
        assert sources == [graph.node(n).name for n in graph.source_tables(f"T3:{plot}")] or set(sources) == {
            graph.node(n).name for n in graph.source_tables(f"T3:{plot}")}, "the sources of a plot are the graph's source tables"
        assert [s["schema_id"] for s in steps if s["type"] == "join"] == (
            [graph.plot_target(plot)] if graph.node(f"T1:{graph.plot_target(plot)}").collection_kind == "join" else [])
    for group in {e["group_id"] for e in ctx.values() if e.get("group_id")}:
        assert get_plot_ids_in_group(group, path) == [p for p in graph.plots() if registry[p]["group_id"] == group]


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_the_tube_map_has_the_edges_of_the_graph(path):
    from utils.config_loader import ConfigManager
    raw = ConfigManager(path).raw_config
    graph = build_graph(raw)
    elements = cy(raw)
    found_edges, found_nodes = edges(elements), node_ids(elements)
    for plot in graph.plots():
        target = graph.plot_target(plot)
        upstream = {f"{safe(target)}__wrn", safe(target)} & found_nodes
        incoming = {source for source, sink in found_edges if sink == safe(plot)}
        assert incoming and incoming <= upstream, f"plot {plot} must be fed by its table {target}"
    for table in graph.collections():
        if graph.node(f"T1:{table}").collection_kind == "join":
            incoming = [e for e in elements if "source" in e["data"] and e["data"]["target"] == safe(table)]
            assert len(incoming) == len(graph.parents(f"T1:{table}")), f"join {table} must have one edge per ingredient"


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_on_every_shipped_recipe_the_lineage_rail_of_a_join_names_the_tables_the_graph_says_it_reads(path):
    raw, _ = load_recipe(path)
    graph = build_graph(raw)
    ctx = build_sibling_map(path)
    for table in graph.collections():
        if graph.node(f"T1:{table}").collection_kind != "join":
            continue
        rel = next(r for r, e in ctx.items() if e["schema_id"] == table and e["role"] == "join" and e.get("tier") != "tier2")
        chain = build_lineage_chain(rel, ctx)
        shown = list(dict.fromkeys(n["schema_id"] for n in chain if n["role"] == "wrangling"))      # a table with a file and an id entry shows twice
        assert shown == [graph.node(p).name for p in graph.parents(f"T1:{table}")]
        assert any(n["is_active"] and n["schema_id"] == table for n in chain)


# ---------------------------------------------------------------- a recipe the graph cannot draw still opens ------------------------

def two_tables():
    a = minimal_schema("data/a.tsv", {"sample_id": "String", "v": "Float64"}, entity_key="sample_id", tier1=[dict(STEP)])
    b = minimal_schema("data/b.tsv", {"sample_id": "String", "w": "Float64"}, tier1=[dict(STEP)])
    step = {"action": "polars_join", "right_ingredient": "B", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}
    return minimal_recipe("r", schemas={"A": a, "B": b}, joins={"AB": minimal_join(["A", "B"], [step], tier2=[dict(STEP)])},
                          plots={"p": minimal_plot("AB", {"x": "sample_id"}), "q": minimal_plot("A", {"x": "sample_id"})})


def write(tmp_path, raw):
    return write_recipe(tmp_path / "r.yaml", raw)


def test_a_good_recipe_is_drawn_whole_and_the_graph_is_the_graph_of_the_recipe():
    raw = two_tables()
    structure = recipe_structure(raw)
    assert structure.left_out == () and structure.graph.nodes() == build_graph(raw).nodes()
    assert structure.ingredients("AB") == ["A", "B"] and structure.ingredients("A") == [] and structure.ingredients("nope") == []
    assert structure.target_of("p") == "AB" and structure.target_of("q") == "A" and structure.target_of("nope") is None


def test_a_recipe_that_is_not_a_mapping_has_no_graph_and_says_so():
    structure = recipe_structure(["a"])
    assert structure.graph is None and structure.left_out and structure.ingredients("AB") == [] and structure.target_of("p") is None


def test_the_recipe_that_is_given_is_never_changed_by_leaving_something_out():
    raw = two_tables()
    raw["joins"]["AB"]["ingredients"].append({"dataset_id": "NOPE"})
    before = copy.deepcopy(raw)
    structure = recipe_structure(raw)
    assert raw == before and structure.graph is not None and structure.left_out


def test_an_ingredient_that_is_no_table_is_left_out_listed_and_the_rest_is_drawn(tmp_path):
    raw = two_tables()
    raw["joins"]["AB"]["ingredients"].append({"dataset_id": "NOPE"})
    structure = recipe_structure(raw)
    assert structure.ingredients("AB") == ["A", "B"]
    assert [p.path for p in structure.left_out] == ["joins.AB.ingredients[3]"] and "NOPE" in structure.left_out[0].message
    path = write(tmp_path, raw)
    assert build_sibling_map(str(path))["AB"]["ingredients"] == ["A", "B"]
    assert build_schema_registry(str(path), {})["AB"]["ingredients"] == ["A", "B"]
    elements = cy(raw)
    assert edges(elements) >= {("A__wrn", "AB"), ("B__wrn", "AB"), ("AB__wrn", "p")} and not any("NOPE" in a + b for a, b in edges(elements))
    assert json.loads(BlueprintMapper(raw).generate_cy_elements()) == elements         # drawing twice gives the same map


def test_a_plot_that_reads_no_table_is_left_out_and_gets_the_warning_node_and_no_target(tmp_path):
    raw = two_tables()
    raw["analysis_groups"]["main"]["plots"]["q"]["target_dataset"] = "NOPE"
    structure = recipe_structure(raw)
    assert structure.target_of("q") is None and structure.target_of("p") == "AB"
    assert [p.path for p in structure.left_out] == ["analysis_groups.main.plots.q.target_dataset"]
    elements = cy(raw)
    assert "INFO_q" in node_ids(elements) and ("A__wrn", "p") not in edges(elements) and ("AB__wrn", "p") in edges(elements)
    path = write(tmp_path, raw)
    assert build_schema_registry(str(path), {})["q"]["target_dataset"] is None and build_schema_registry(str(path), {})["p"]["target_dataset"] == "AB"
    assert [s["type"] for s in build_plot_lineage("q", str(path))] == ["plot_spec"]
    assert get_plot_ids_in_group("main", str(path)) == ["p", "q"], "the group still lists the plot: Blueprint shows what is written"


def test_a_join_step_that_names_a_table_the_join_does_not_list_leaves_out_the_step_and_keeps_the_ingredients():
    raw = two_tables()
    raw["joins"]["AB"]["tier1"]["steps"].append({"action": "polars_join", "right_ingredient": "ZZ", "on": ["sample_id"]})
    structure = recipe_structure(raw)
    assert structure.ingredients("AB") == ["A", "B"] and [p.path for p in structure.left_out] == ["joins.AB.tier1.steps[2]"]


def test_a_cycle_of_joins_is_drawn_without_looping_and_listed():
    raw = two_tables()
    raw["joins"]["J2"] = minimal_join(["A", "AB"], [])
    raw["joins"]["AB"]["ingredients"].append({"dataset_id": "J2"})
    structure = recipe_structure(raw)
    assert structure.graph is not None and structure.left_out and "cycle" in structure.left_out[0].message
    assert len(cy(raw)) > 0 and "graph LR" in BlueprintMapper(raw).generate_mermaid()


def test_an_id_written_twice_leaves_out_the_second_and_the_map_is_still_drawn():
    raw = two_tables()
    raw["additional_datasets_schemas"] = {"A": minimal_schema("data/other.tsv", {"sample_id": "String"})}
    structure = recipe_structure(raw)
    assert structure.graph is not None and [p.path for p in structure.left_out] == ["additional_datasets_schemas.A"]
    assert len(cy(raw)) > 0


def test_several_things_the_graph_refuses_at_once_are_all_listed_and_the_rest_drawn():
    raw = two_tables()
    raw["joins"]["AB"]["ingredients"].append({"dataset_id": "NOPE"})
    raw["analysis_groups"]["main"]["plots"]["q"]["target_dataset"] = "NOPE"
    raw["data_schemas"]["Z"] = 3
    raw["analysis_groups"]["other"] = 5
    structure = recipe_structure(raw)
    assert structure.graph is not None and structure.ingredients("AB") == ["A", "B"] and structure.target_of("p") == "AB"
    assert {p.path for p in structure.left_out} == {"joins.AB.ingredients[3]", "analysis_groups.main.plots.q.target_dataset",
                                                   "data_schemas.Z", "analysis_groups.other"}


def test_two_ingredients_that_are_bad_in_one_list_are_both_left_out():
    raw = two_tables()
    raw["joins"]["AB"]["ingredients"][1:1] = [{"dataset_id": "X1"}]            # in the middle, before B
    raw["joins"]["AB"]["ingredients"].append("not a mapping")
    structure = recipe_structure(raw)
    assert structure.ingredients("AB") == ["A", "B"] and len(structure.left_out) == 2


def test_a_file_with_a_repeated_key_has_no_structure_but_the_files_still_open(tmp_path):
    path = write(tmp_path, two_tables())
    path.write_text(path.read_text(encoding="utf-8") + "data_engine: python-polars\n", encoding="utf-8")   # `data_engine` is now written twice
    structure = recipe_structure_of_file(str(path))
    assert structure.graph is None and structure.left_out
    ctx = build_sibling_map(str(path))
    assert ctx["AB"]["role"] == "wrangling" or ctx["AB"]["role"] == "join"      # the elements are listed, from the text
    assert ctx["AB"]["ingredients"] == [] and ctx["p"]["role"] == "plot_spec"
    assert build_schema_registry(str(path), {})["p"]["target_dataset"] is None
    assert [s["type"] for s in build_plot_lineage("p", str(path))] == ["plot_spec"]


def test_a_file_that_is_not_a_recipe_or_is_missing_gives_the_empty_answers(tmp_path):
    (tmp_path / "bad.yaml").write_text("- a\n- b\n", encoding="utf-8")
    for name in ("bad.yaml", "missing.yaml"):
        path = str(tmp_path / name)
        assert build_sibling_map(path) == {} and build_schema_registry(path, {}) == {}
        assert build_plot_lineage("p", path) == [] and get_plot_ids_in_group("g", path) == []
        assert recipe_structure_of_file(path).graph is None


def test_a_missing_plot_file_is_one_plot_without_a_table_and_not_an_error(tmp_path):
    raw = two_tables()
    from utils.recipe_factory import Include
    raw["analysis_groups"]["main"]["plots"]["q"] = Include("r/plots/q.yaml")
    path = write(tmp_path, raw)                                               # the file r/plots/q.yaml does not exist
    structure = recipe_structure_of_file(str(path))
    assert structure.graph is not None and structure.target_of("q") is None and structure.target_of("p") == "AB"
    assert build_schema_registry(str(path), {})["q"]["target_dataset"] is None


# ---------------------------------------------------------------- no second description of the structure -----------------------

@pytest.mark.parametrize("module", [navigator, blueprint_mapper], ids=lambda m: m.__name__)
def test_the_navigator_and_the_mapper_do_not_read_the_ingredients_or_the_target_of_a_plot_themselves(module):
    """`dataset_id` (the ingredient key) and `target_dataset` / `join_id` (the plot's table) are read by the graph only.

    (`_places` of the navigator reads the lists of a recipe to find what the graph's own error names; it decides nothing about the structure.)"""
    source = Path(module.__file__).read_text(encoding="utf-8")
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    code = re.sub(r'""".*?"""', "", code, flags=re.S)
    for word in ("dataset_id", '"join_id"', 'get("target_dataset")'):
        assert word not in code, f"{module.__name__} reads {word} itself: ask the recipe graph"
