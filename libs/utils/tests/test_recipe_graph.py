"""The recipe graph (ADR-099 point 16(d), 16(i); ADR-101 point 3): every shape of recipe gives the right map.

The graph is built from a resolved recipe (a dictionary) and answers, without reading data: which table feeds which
tier, join and plot; the columns of every node, and where they are not known from the recipe alone; the plots that depend
on a node. The tests cover each recipe shape, the plain errors, the columns, the checker's J08 contract, and every shipped
recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_graph.py -q
"""
import glob
from pathlib import Path

import pytest

from utils.recipe_check import check_recipe
from utils.recipe_graph import RecipeGraphError, build_graph
from utils.recipe_loader import load_recipe

FILTER = {"action": "modif_filter", "column": "a", "op": "eq", "value": "x", "na": "remove"}
SORT = {"action": "polars_sort", "by": ["a"], "maintain_order": True}
JOIN = {"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}


def schema(columns, tier1=None, tier2=None, **extra):
    body = {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": {c: {"type": "String"} for c in columns},
            "tier1": {"steps": list(tier1 or [])}, **extra}
    if tier2 is not None:
        body["tier2"] = {"steps": list(tier2)}
    return body


def join(ingredients, steps=None, tier2=None):
    body = {"ingredients": [{"dataset_id": i} for i in ingredients], "tier1": {"steps": list(steps or [])}}
    if tier2 is not None:
        body["tier2"] = {"steps": list(tier2)}
    return body


def plot(target, tier3=None, **extra):
    entry = {"target_dataset": target, "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}], **extra}
    if tier3 is not None:
        entry["tier3"] = {"steps": list(tier3)}
    return entry


def recipe(schemas=None, joins=None, plots=None, **extra):
    raw = {"id": "r", "data_schemas": schemas if schemas is not None else {"A": schema(["id", "a"])}}
    if joins is not None:
        raw["joins"] = joins
    if plots is not None:
        raw["analysis_groups"] = {"g": {"ui_label": "G", "plots": plots}}
    raw.update(extra)
    return raw


# ---------------------------------------------------------------- the shapes of recipe ------------------------

def test_no_join_one_table_one_plot():
    graph = build_graph(recipe(plots={"p": plot("A")}))
    assert graph.nodes() == ["DS:A", "T1:A", "T2:A", "T3:p"]
    assert graph.edges() == [("DS:A", "T1:A"), ("T1:A", "T2:A"), ("T2:A", "T3:p")]
    assert graph.plots() == ["p"] and graph.plot_target("p") == "A"
    assert graph.collections() == ["A"]


def test_a_recipe_with_no_plot_has_tables_only():
    graph = build_graph(recipe())
    assert graph.nodes() == ["DS:A", "T1:A", "T2:A"] and graph.plots() == []
    assert graph.node("T2:A").read_by_plot is False


def test_an_empty_recipe_gives_an_empty_graph():
    graph = build_graph({})
    assert graph.nodes() == [] and graph.edges() == [] and graph.plots() == [] and graph.collections() == []
    assert graph.nodes_with_column("id") == [] and graph.key_families() == []


def test_a_recipe_that_is_not_a_mapping_is_refused():
    with pytest.raises(RecipeGraphError, match="mapping"):
        build_graph(["not", "a", "recipe"])


def test_one_join_reads_the_tier1_of_each_ingredient_in_the_written_order():
    raw = recipe({"A": schema(["id"]), "B": schema(["id", "b"])}, {"J": join(["B", "A"], [JOIN])}, {"p": plot("J")})
    graph = build_graph(raw)
    assert graph.parents("T1:J") == ["T1:B", "T1:A"]            # the order of the ingredients: the first is the base
    assert graph.parents("T3:p") == ["T2:J"] and graph.plot_target("p") == "J"
    assert graph.collections() == ["A", "B", "J"]
    assert graph.node("T1:J").collection_kind == "join" and graph.node("T1:A").collection_kind == "schema"
    assert graph.source_tables("T3:p") == ["DS:A", "DS:B"]           # graph order, not ingredient order


def test_a_join_of_joins_is_a_chain_of_tier1_nodes():
    """The engine takes schema ingredients only (orchestrator.py, J04); the graph still draws an ingredient that names a join."""
    raw = recipe({"A": schema(["id"]), "B": schema(["id"]), "C": schema(["id"])},
                 {"J1": join(["A", "B"]), "J2": join(["J1", "C"])}, {"p": plot("J2")})
    graph = build_graph(raw)
    assert graph.parents("T1:J2") == ["T1:J1", "T1:C"]
    assert graph.lineage_back("T3:p") == ["DS:A", "T1:A", "DS:B", "T1:B", "DS:C", "T1:C", "T1:J1", "T1:J2", "T2:J2"]
    assert graph.source_tables("T3:p") == ["DS:A", "DS:B", "DS:C"]


def test_a_table_used_in_two_joins_feeds_both_and_every_plot_downstream():
    raw = recipe({"A": schema(["id"]), "B": schema(["id"]), "C": schema(["id"])},
                 {"J1": join(["A", "B"]), "J2": join(["A", "C"])},
                 {"p1": plot("J1"), "p2": plot("J2")})
    graph = build_graph(raw)
    assert graph.children("T1:A") == ["T2:A", "T1:J1", "T1:J2"]
    assert graph.plots_reading("T1:A") == ["p1", "p2"]
    assert graph.plots_reading("T1:B") == ["p1"] and graph.plots_reading("T1:C") == ["p2"]
    assert graph.plots_reading("DS:A") == ["p1", "p2"]
    assert graph.lineage_forward("T1:B") == ["T2:B", "T1:J1", "T2:J1", "T3:p1"]


def test_a_plot_on_a_table_reads_the_tier2_of_that_table_and_the_tier2_list_is_its_own():
    raw = recipe({"A": schema(["id", "a"], tier2=[FILTER])}, plots={"p": plot("A")})
    graph = build_graph(raw)
    assert graph.node("T2:A").steps == (FILTER,) and graph.node("T2:A").read_by_plot is True
    assert graph.plots_reading("T2:A") == ["p"]


def test_a_join_does_not_read_the_tier2_of_its_ingredient():
    raw = recipe({"A": schema(["id", "a"], tier2=[FILTER]), "B": schema(["id"])}, {"J": join(["A", "B"])}, {"p": plot("J")})
    graph = build_graph(raw)
    assert "T2:A" not in graph.lineage_back("T3:p")
    assert graph.plots_reading("T2:A") == []                      # a tier2 list that no plot reads is run nowhere (S07)
    assert graph.node("T2:A").read_by_plot is False


def test_two_plots_on_one_table_share_its_tier2_node():
    graph = build_graph(recipe(plots={"p1": plot("A"), "p2": plot("A")}))
    assert graph.parents("T3:p1") == graph.parents("T3:p2") == ["T2:A"]
    assert graph.plots_reading("T2:A") == ["p1", "p2"]            # the order of the recipe
    assert graph.children("T2:A") == ["T3:p1", "T3:p2"]


def test_a_recipe_with_tier2_and_one_without_have_the_same_nodes():
    with_tier2 = build_graph(recipe({"A": schema(["id"], tier2=[SORT])}, plots={"p": plot("A")}))
    without = build_graph(recipe({"A": schema(["id"])}, plots={"p": plot("A")}))
    assert with_tier2.nodes() == without.nodes() and with_tier2.edges() == without.edges()
    assert with_tier2.node("T2:A").steps == (SORT,) and without.node("T2:A").steps == ()


def test_a_plot_with_tier3_steps_and_without():
    raw = recipe(plots={"p": plot("A", tier3=[FILTER]), "q": plot("A")})
    graph = build_graph(raw)
    assert graph.node("T3:p").steps == (FILTER,) and graph.node("T3:q").steps == ()
    assert graph.node("T3:p").path == "analysis_groups.g.plots.p"


def test_the_metadata_and_additional_schemas_are_tables_too():
    raw = recipe({"A": schema(["id"])}, additional_datasets_schemas={"X": schema(["id"])}, metadata_schema=schema(["id", "m"]))
    graph = build_graph(raw)
    assert graph.collections() == ["A", "X", "metadata_schema"]
    assert "DS:metadata_schema" in graph.nodes() and graph.node("T1:X").collection_kind == "schema"


def test_plots_of_two_groups_keep_the_recipe_order():
    raw = recipe(plots={"p1": plot("A")})
    raw["analysis_groups"]["h"] = {"ui_label": "H", "plots": {"p0": plot("A")}}
    assert build_graph(raw).plots() == ["p1", "p0"]
    assert build_graph(raw).node("T3:p0").path == "analysis_groups.h.plots.p0"


def test_the_order_is_deterministic_and_parents_come_first():
    raw = recipe({"A": schema(["id"]), "B": schema(["id"])}, {"J": join(["B", "A"])}, {"p": plot("J")})
    one, two = build_graph(raw), build_graph(raw)
    assert one.nodes() == two.nodes() and one.edges() == two.edges()
    position = {n: i for i, n in enumerate(one.nodes())}
    assert all(position[a] < position[b] for a, b in one.edges())


# ---------------------------------------------------------------- plain errors ----------------------------------

def problems_of(raw):
    with pytest.raises(RecipeGraphError) as caught:
        build_graph(raw)
    return caught.value


def test_a_join_that_names_an_unknown_ingredient_is_named():
    error = problems_of(recipe(joins={"J": join(["A", "Nope"])}))
    assert [p.path for p in error.problems] == ["joins.J.ingredients[2]"]
    assert "Nope" in str(error) and "joins.J.ingredients[2]" in str(error)


def test_a_cycle_of_joins_is_named():
    raw = recipe({"A": schema(["id"])}, {"J1": join(["A", "J2"]), "J2": join(["A", "J1"])})
    error = problems_of(raw)
    assert "cycle" in str(error) and "J1" in str(error) and "J2" in str(error)


def test_a_join_that_reads_itself_is_a_cycle():
    error = problems_of(recipe({"A": schema(["id"])}, {"J": join(["A", "J"])}))
    assert "cycle" in str(error) and "J" in str(error)


def test_a_plot_whose_target_does_not_exist_is_named():
    error = problems_of(recipe(plots={"p": plot("Nope")}))
    assert error.problems[0].path == "analysis_groups.g.plots.p.target_dataset"
    assert "Nope" in str(error)


def test_a_plot_with_no_target_is_named():
    entry = plot("A")
    del entry["target_dataset"]
    error = problems_of(recipe(plots={"p": entry}))
    assert error.problems[0].path == "analysis_groups.g.plots.p" and "target_dataset" in str(error)


def test_one_id_for_a_schema_and_a_join_is_refused():
    error = problems_of(recipe({"A": schema(["id"]), "B": schema(["id"])}, {"A": join(["B"])}))
    assert "A" in str(error) and "schema" in str(error) and "join" in str(error)


def test_one_plot_id_in_two_groups_is_refused():
    raw = recipe(plots={"p": plot("A")})
    raw["analysis_groups"]["h"] = {"ui_label": "H", "plots": {"p": plot("A")}}
    assert "p" in str(problems_of(raw)) and "twice" in str(problems_of(raw))


def test_an_ingredient_written_as_a_bare_id_is_refused():
    raw = recipe({"A": schema(["id"])}, {"J": {"ingredients": ["A"], "tier1": {"steps": []}}})
    error = problems_of(raw)
    assert error.problems[0].path == "joins.J.ingredients[1]" and "dataset_id" in str(error)


def test_every_problem_is_reported_together():
    raw = recipe(joins={"J": join(["A", "Nope"])}, plots={"p": plot("Gone")})
    assert len(problems_of(raw).problems) == 2


# ---------------------------------------------------------------- queries ---------------------------------------

def three_tables():
    raw = recipe({"A": schema(["id"]), "B": schema(["id"])}, {"J": join(["A", "B"])}, {"p": plot("J")})
    return build_graph(raw)


def test_lineage_back_and_forward_in_graph_order():
    graph = three_tables()
    assert graph.lineage_back("T2:J") == ["DS:A", "T1:A", "DS:B", "T1:B", "T1:J"]
    assert graph.lineage_forward("DS:A") == ["T1:A", "T2:A", "T1:J", "T2:J", "T3:p"]
    assert graph.lineage_forward("T3:p") == [] and graph.lineage_back("DS:A") == []


def test_plots_reading_a_plot_node_is_the_plot_itself():
    assert three_tables().plots_reading("T3:p") == ["p"]


def test_an_unknown_node_is_a_plain_error():
    graph = three_tables()
    with pytest.raises(KeyError, match="T1:Nope"):
        graph.lineage_back("T1:Nope")
    assert graph.has_node("T1:J") and not graph.has_node("T1:Nope")


def test_a_node_hands_out_its_recipe_place():
    graph = three_tables()
    assert graph.node("DS:A").path == "data_schemas.A" and graph.node("T1:J").path == "joins.J"
    assert graph.node("T1:J").kind == "T1" and graph.node("T1:J").name == "J"


# ---------------------------------------------------------------- columns ---------------------------------------

def test_the_source_and_the_tier1_of_a_table_without_steps_have_the_declared_columns():
    graph = build_graph(recipe({"A": schema(["id", "a", "b"])}))
    for node in ("DS:A", "T1:A", "T2:A"):
        assert graph.column_info(node).names == ("id", "a", "b")
    assert graph.column_info("DS:A").how == "declared"
    assert graph.columns_of("A") == ("id", "a", "b")              # a collection id means its tier 1 (the checker's call)
    assert graph.columns_of("T1:A") == ("id", "a", "b")


def test_steps_that_only_choose_or_order_rows_keep_the_columns():
    graph = build_graph(recipe({"A": schema(["id", "a"], tier1=[FILTER, SORT])}))
    assert graph.columns_of("T1:A") == ("id", "a")


def test_a_join_step_leaves_the_columns_unknown_and_says_where():
    raw = recipe({"A": schema(["id", "a"]), "B": schema(["id", "b"])}, {"J": join(["A", "B"], [JOIN])})
    info = build_graph(raw).column_info("T1:J")
    assert info.names is None and info.how == "unknown"
    assert "joins.J.tier1.steps[1]" in info.reason and "polars_join" in info.reason
    assert build_graph(raw).columns_of("J") is None


def test_a_select_at_the_end_of_a_tier_fixes_the_columns_whatever_came_before():
    select = {"action": "polars_select", "exprs": ["b", "id"]}
    raw = recipe({"A": schema(["id", "a"]), "B": schema(["id", "b"])}, {"J": join(["A", "B"], [JOIN, select])})
    info = build_graph(raw).column_info("T1:J")
    assert info.names == ("b", "id") and info.how == "select"       # in the order written (DEC23, DEC37)


def test_a_drop_removes_columns_when_the_ones_before_are_known():
    drop = {"action": "polars_drop", "columns": ["a"]}
    assert build_graph(recipe({"A": schema(["id", "a", "b"], tier1=[drop])})).columns_of("T1:A") == ("id", "b")


def test_a_drop_after_an_unknown_step_stays_unknown():
    drop = {"action": "polars_drop", "columns": ["a"]}
    raw = recipe({"A": schema(["id", "a"], tier1=[{"action": "polars_unpivot", "on": ["a"]}, drop])})
    assert build_graph(raw).columns_of("T1:A") is None


def test_a_select_with_a_pattern_or_a_formula_is_not_a_list_of_names():
    for item in ("^a.*$", "*", {"expr": "x"}):
        select = {"action": "polars_select", "exprs": ["id", item]}
        assert build_graph(recipe({"A": schema(["id", "a"], tier1=[select])})).columns_of("T1:A") is None, item


def test_a_table_without_declared_fields_has_unknown_columns():
    raw = recipe({"A": schema([])})
    info = build_graph(raw).column_info("DS:A")
    assert info.names is None and "input_fields" in info.reason


def test_tier2_and_tier3_flow_on_from_the_node_before():
    select = {"action": "polars_select", "exprs": ["id"]}
    raw = recipe({"A": schema(["id", "a"], tier2=[select])}, plots={"p": plot("A", tier3=[{"action": "polars_drop", "columns": ["id"]}])})
    graph = build_graph(raw)
    assert graph.columns_of("T1:A") == ("id", "a") and graph.columns_of("T2:A") == ("id",) and graph.columns_of("T3:p") == ()


def test_an_id_the_recipe_does_not_have_has_no_columns_and_has_node_tells_it_apart():
    graph = build_graph(recipe())
    assert graph.columns_of("Nope") is None and not graph.has_node("T1:Nope")


def test_a_provider_fills_what_the_recipe_cannot_say_and_the_columns_flow_on():
    raw = recipe({"A": schema(["id", "a"]), "B": schema(["id", "b"])}, {"J": join(["A", "B"], [JOIN], tier2=[FILTER])})
    asked = []

    def provider(node_id):
        asked.append(node_id)
        return ["id", "a", "b"] if node_id == "T1:J" else None

    graph = build_graph(raw, columns_provider=provider)
    info = graph.column_info("T1:J")
    assert info.names == ("id", "a", "b") and info.how == "provider"
    assert graph.columns_of("T2:J") == ("id", "a", "b")           # the filter keeps what the provider said
    assert set(asked) == {"T1:J"}                                 # the provider is asked where the recipe cannot say, never elsewhere


def test_a_provider_that_does_not_know_leaves_it_unknown():
    raw = recipe({"A": schema(["id"]), "B": schema(["id"])}, {"J": join(["A", "B"], [JOIN])})
    assert build_graph(raw, columns_provider=lambda node: None).columns_of("T1:J") is None


def test_nodes_with_column_lists_only_the_nodes_that_certainly_have_it():
    raw = recipe({"A": schema(["id", "a"]), "B": schema(["id", "b"])}, {"J": join(["A", "B"], [JOIN])}, {"p": plot("J")})
    graph = build_graph(raw)
    assert graph.nodes_with_column("a") == ["DS:A", "T1:A", "T2:A"]
    assert graph.nodes_with_column("id") == ["DS:A", "T1:A", "T2:A", "DS:B", "T1:B", "T2:B"]
    assert graph.column_presence("b") == {"DS:A": "no", "T1:A": "no", "T2:A": "no", "DS:B": "yes", "T1:B": "yes", "T2:B": "yes",
                                         "T1:J": "unknown", "T2:J": "unknown", "T3:p": "unknown"}
    assert graph.nodes_with_unknown_columns() == ["T1:J", "T2:J", "T3:p"]


def test_shared_columns_of_two_nodes_in_the_order_of_the_first():
    graph = build_graph(recipe({"A": schema(["id", "a", "z"]), "B": schema(["z", "id", "b"])}))
    assert graph.shared_columns("T1:A", "T1:B") == ("id", "z")
    assert graph.shared_columns("A", "B") == ("id", "z")


def test_shared_columns_is_none_when_one_side_is_unknown():
    raw = recipe({"A": schema(["id"]), "B": schema(["id"])}, {"J": join(["A", "B"], [JOIN])})
    assert build_graph(raw).shared_columns("T1:A", "T1:J") is None


def test_the_columns_a_plot_uses():
    entry = plot("A", mapping={"x": "id", "fill": "a", "y": {"not": "a name"}}, facet_by="b", filters=[{"column": "c", "op": "eq", "value": 1}])
    graph = build_graph(recipe({"A": schema(["id", "a", "b", "c"])}, plots={"p": entry}))
    assert graph.plot_columns("p") == ("id", "a", "b", "c")       # mapping values, facet_by, filters: in that order, once each


# ---------------------------------------------------------------- key families and T1 definitions ------------

def test_key_families_link_the_declared_keys_through_the_join_columns():
    a = schema(["sample_id", "v"])
    a["input_fields"]["sample_id"]["is_entity_key"] = True
    b = schema(["isolate", "w"])
    b["input_fields"]["isolate"]["is_entity_key"] = True
    c = schema(["other", "z"])
    step = {"action": "polars_join", "right_ingredient": "B", "left_on": "sample_id", "right_on": "isolate", "how": "left"}
    graph = build_graph(recipe({"A": a, "B": b, "C": c}, {"J": join(["A", "B"], [step])}))
    assert graph.key_families() == [("isolate", "sample_id")]       # linked by the join; never found from names alone
    assert graph.key_family_of("sample_id") == ("isolate", "sample_id") and graph.key_family_of("v") is None


def test_declared_keys_of_two_unlinked_tables_are_two_families():
    a, b = schema(["ka"]), schema(["kb"])
    a["input_fields"]["ka"]["is_entity_key"] = True
    b["input_fields"]["kb"]["is_entity_key"] = True
    assert build_graph(recipe({"A": a, "B": b})).key_families() == [("ka",), ("kb",)]


def test_a_join_on_an_undeclared_column_makes_no_family():
    step = {"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}
    graph = build_graph(recipe({"A": schema(["id"]), "B": schema(["id"])}, {"J": join(["A", "B"], [step])}))
    assert graph.key_families() == []


def _no_source(columns, **kw):
    body = schema(columns, **kw)
    del body["source"]
    return body


def test_two_tables_with_the_same_tier1_definition_are_recognised_whatever_their_descriptions():
    one = schema(["id", "a"], tier1=[FILTER], label="One", description="first")
    two = schema(["id", "a"], tier1=[FILTER], label="Two", description="second")
    three = schema(["id", "a"], tier1=[SORT])
    graph = build_graph(recipe({"A": one, "B": two, "C": three}))
    assert graph.same_t1_definition("A", "B") is True              # both name the same explicit source path
    assert graph.same_t1_definition("A", "C") is False
    assert graph.same_t1_definition("A", "A") is True


def test_two_tables_with_equal_text_and_no_source_are_not_the_same_definition():
    # the engine finds such a file by the table id: two ids are two files
    graph = build_graph(recipe({"A": _no_source(["id", "a"]), "B": _no_source(["id", "a"])}))
    assert graph.same_t1_definition("A", "B") is False
    assert graph.same_t1_definition("A", "A") is True


def test_a_source_without_a_path_is_not_an_explicit_source():
    one, two = schema(["id"]), schema(["id"])
    one["source"] = two["source"] = {"type": "local_tsv"}
    assert build_graph(recipe({"A": one, "B": two})).same_t1_definition("A", "B") is False


def test_two_tables_with_different_source_paths_are_not_the_same_definition():
    one, two = schema(["id"]), schema(["id"])
    two["source"] = {"type": "local_tsv", "path": "y.tsv"}
    assert build_graph(recipe({"A": one, "B": two})).same_t1_definition("A", "B") is False


def test_a_difference_in_null_values_alone_makes_two_tables_differ():
    one, two = schema(["id"], null_values=["NA"]), schema(["id"], null_values=["NA", "-"])
    graph = build_graph(recipe({"A": one, "B": two, "C": schema(["id"], null_values=["NA"])}))
    assert graph.same_t1_definition("A", "B") is False
    assert graph.same_t1_definition("A", "C") is True


def test_a_join_and_a_schema_never_share_a_definition_and_the_tier2_list_is_not_part_of_it():
    raw = recipe({"A": schema(["id"], tier2=[SORT]), "B": schema(["id"])}, {"J": join(["A", "B"])})
    graph = build_graph(raw)
    assert graph.same_t1_definition("A", "B") is True              # only the tier 2 differs: T1 is the same (same explicit path)
    assert graph.same_t1_definition("A", "J") is False


# ---------------------------------------------------------------- order of columns, select, join steps -------

def test_the_order_of_a_declared_table_is_marked_as_not_known():
    info = build_graph(recipe({"A": schema(["id", "a"])})).column_info("DS:A")
    assert info.how == "declared" and info.order_known is False     # the file's order wins in the engine


def test_the_order_after_a_select_is_known_and_a_drop_after_a_select_keeps_it():
    select = {"action": "polars_select", "exprs": ["b", "id", "a"]}
    drop = {"action": "polars_drop", "columns": ["id"]}
    graph = build_graph(recipe({"A": schema(["id", "a", "b"], tier1=[select, drop])}))
    assert graph.column_info("T1:A").order_known is True and graph.columns_of("T1:A") == ("b", "a")


def test_a_drop_after_declared_columns_keeps_the_order_unknown_and_a_provider_is_a_known_order_of_nothing():
    drop = {"action": "polars_drop", "columns": ["a"]}
    graph = build_graph(recipe({"A": schema(["id", "a", "b"], tier1=[drop])}))
    assert graph.column_info("T1:A").order_known is False


def test_unknown_columns_have_no_order_claim():
    raw = recipe({"A": schema(["id"], tier1=[{"action": "polars_unpivot", "on": ["id"]}])})
    assert build_graph(raw).column_info("T1:A").order_known is False


@pytest.mark.parametrize("item", ["pl.col('a')", "a.b", "a b", "sum(a)", "pl.all()"])
def test_a_select_text_that_is_not_a_plain_column_name_gives_unknown_columns(item):
    select = {"action": "polars_select", "exprs": ["id", item]}
    info = build_graph(recipe({"A": schema(["id", "a"], tier1=[select])})).column_info("T1:A")
    assert info.names is None and info.how == "unknown"


def test_a_select_with_keys_the_engine_does_not_expose_gives_unknown_columns():
    select = {"action": "polars_select", "exprs": ["id"], "named_exprs": {"z": "pl.lit(1)"}}
    assert build_graph(recipe({"A": schema(["id", "a"], tier1=[select])})).columns_of("T1:A") is None


def test_a_plain_select_still_gives_the_names():
    select = {"action": "polars_select", "exprs": ["id", "a_1"]}
    assert build_graph(recipe({"A": schema(["id", "a_1"], tier1=[select])})).columns_of("T1:A") == ("id", "a_1")


def test_a_join_step_that_names_a_table_that_is_not_an_ingredient_is_named():
    step = {"action": "polars_join", "right_ingredient": "C", "on": "id", "how": "left"}
    raw = recipe({"A": schema(["id"]), "B": schema(["id"]), "C": schema(["id"])}, {"J": join(["A", "B"], [step])})
    with pytest.raises(RecipeGraphError) as error:
        build_graph(raw)
    problem = error.value.problems[0]
    assert problem.path == "joins.J.tier1.steps[1]" and "'C'" in problem.message


def test_a_join_step_on_a_listed_ingredient_is_fine():
    step = {"action": "polars_join", "right_ingredient": "B", "on": "id"}
    build_graph(recipe({"A": schema(["id"]), "B": schema(["id"])}, {"J": join(["A", "B"], [step])}))


# ---------------------------------------------------------------- the checker's J08 --------------------------

def test_the_checker_finds_j08_from_the_graph_and_not_when_the_key_is_the_only_shared_column():
    from test_recipe_check import CATALOGS, valid
    raw = valid()
    raw["data_schemas"]["B"]["input_fields"]["v"] = {"type": "Float64"}     # `v` is now in A and in B and is not the key
    result = check_recipe(raw, "run", catalogs=CATALOGS, graph=build_graph(raw))
    assert "J08" in result.codes() and "columns" in result.coverage
    clean = valid()
    assert "J08" not in check_recipe(clean, "run", catalogs=CATALOGS, graph=build_graph(clean)).codes()


# ---------------------------------------------------------------- every shipped recipe -----------------------

ROOT = Path(__file__).resolve().parents[3]
SHIPPED = sorted(
    glob.glob(str(ROOT / "config" / "data_analysis_recipes" / "*" / "*.yaml"))
    + glob.glob(str(ROOT / "assets" / "gallery_data" / "*" / "data_analysis_recipe.yaml"))
    + glob.glob(str(ROOT / "app" / "tests" / "equality" / "recipes" / "*.yaml")))


def test_there_are_shipped_recipes_to_sweep():
    assert len(SHIPPED) >= 40


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_the_graph_builds_over_every_shipped_recipe_and_every_plot_reaches_a_source_table(path):
    raw, problems = load_recipe(path)
    if not raw:
        # `experimental/test_logic.yaml` is an empty file: the loader returns no recipe for it, so there is nothing to draw
        assert path.endswith("experimental/test_logic.yaml"), f"{path} loads as no recipe"
        pytest.skip("the file holds no recipe")
    graph = build_graph(raw)
    for plot_id in graph.plots():
        assert graph.source_tables(f"T3:{plot_id}"), f"plot {plot_id} reaches no source table"
        assert graph.plot_target(plot_id) in graph.collections()
    position = {n: i for i, n in enumerate(graph.nodes())}
    assert all(position[a] < position[b] for a, b in graph.edges())
    for column_node in graph.nodes():
        info = graph.column_info(column_node)
        assert (info.names is None) == (info.how == "unknown")


def test_declared_entity_keys_are_the_declaration_only():
    raw = {"data_schemas": {"A": {**schema(["sample_id", "x"]), "input_fields": {"sample_id": {"type": "String", "is_entity_key": True}, "x": {"type": "String"}}},
                            "B": schema(["id"])},
           "joins": {"J": join(["A", "B"])}, "analysis_groups": {"g": {"plots": {"P": plot("J")}}}}
    graph = build_graph(raw)
    assert graph.declared_entity_keys("A") == ("sample_id",)
    assert graph.declared_entity_keys("B") == () and graph.declared_entity_keys("J") == ()      # a join declares none; a column named like a key is not one
    with pytest.raises(KeyError):
        graph.declared_entity_keys("nope")
