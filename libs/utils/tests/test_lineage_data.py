"""The lineage of a recipe as data (`utils.lineage_data.lineage_of`, D-0627, D-0630 to D-0632): nodes, arrows, what is built from each place, the steps on every path.

What is proved, on small recipes made for the purpose and on every shipped recipe:
- the graph starts at tier 1 of the original tables: no file node, no metadata node; a table that takes the metadata in has the tag `brings_metadata` and no arrow from it;
- an empty tier 2 is no node (the arrow goes from the tier 1 on); a tier 2 with steps is a node; one that no plot reads is a node that cannot be chosen, with the reason;
- a joined table has ALL its parents; a table with nothing built from it is a `result` leaf and can be chosen (also an original one);
- for a place: the nodes built from it, the results, and EVERY path to each result with the steps on it (a diamond of joins gives two paths);
- the independent graphs and their original parents (the metadata no longer joins them);
- the columns come from the plan book only: no book, a failure and a missing entry each say so in the node, never a guess;
- D-0632: the metadata is not a place: `places()`, `chosen_places_problem`, `add_step` and `integrity_errors` refuse it with one plain line.

Mutation index (each seen failing): MUTATION L1 the metadata node is drawn; L2 `resolve` does not follow an empty tier 2 (the arrow is lost); L3 only the first path to a result is kept;
L4 `places()` lists the metadata again; L5 the leaf test is dropped (no `result` kind).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_data.py -q
"""
import glob
import json
from pathlib import Path

import pytest

from utils import recipe_tiers
from utils.audit_copy import AuditCopyError, add_step, integrity_errors, start_audit
from utils.lineage_data import lineage_of, step_line
from utils.plan_book import Plan, PlanBook, PlanFailure
from utils.recipe_graph import RecipeGraphError, build_graph
from utils.recipe_loader import load_recipe

META = recipe_tiers.METADATA_SCHEMA
FILTER = {"action": "modif_filter", "column": "a", "op": "eq", "value": "x", "na": "remove"}
SORT = {"action": "polars_sort", "by": ["a"], "maintain_order": True}


def schema(columns=("id", "a"), tier1=None, tier2=None, **extra):
    body = {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": {c: {"type": "String"} for c in columns}, "tier1": {"steps": list(tier1 or [])}, **extra}
    if tier2 is not None:
        body["tier2"] = {"steps": list(tier2)}
    return body


def jn(right, how="left", on="id"):
    return {"action": "polars_join", "right_ingredient": right, "on": on, "how": how}


def join(ingredients, steps=None, tier2=None, **extra):
    body = {"ingredients": [{"dataset_id": i} for i in ingredients], "tier1": {"steps": list(steps or [])}, **extra}
    if tier2 is not None:
        body["tier2"] = {"steps": list(tier2)}
    return body


def plot(target, tier3=None, **extra):
    entry = {"target_dataset": target, "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}], **extra}
    if tier3 is not None:
        entry["tier3"] = {"steps": list(tier3)}
    return entry


def recipe(schemas, joins=None, plots=None, metadata=None):
    raw = {"id": "r", "data_schemas": schemas}
    if metadata is not None:
        raw[META] = metadata
    if joins is not None:
        raw["joins"] = joins
    if plots is not None:
        raw["analysis_groups"] = {"g": {"ui_label": "G", "plots": plots}}
    return raw


def ids(lineage, kind=None):
    return [n.id for n in lineage.nodes if kind is None or n.kind == kind]


def diamond():
    """A and B feed two joins J1 and J2; J3 reads both; a plot reads J3: two paths from A to the plot."""
    return recipe({"A": schema(), "B": schema()},
                  {"J1": join(["A", "B"], [jn("B")]), "J2": join(["A", "B"], [jn("B", "inner")]), "J3": join(["J1", "J2"], [jn("J2")])},
                  {"p": plot("J3")})


# ---------------------------------------------------------------- the nodes and the arrows ---------------------

def test_the_graph_starts_at_tier_1_with_no_file_node():
    lin = lineage_of(recipe({"A": schema()}, plots={"p": plot("A")}))
    assert ids(lin) == ["T1:A", "T3:p"]
    assert lin.edges == (("T1:A", "T3:p"),)               # the empty tier 2 is no node: the arrow goes from the tier 1 on
    assert not any(n.id.startswith("DS:") for n in lin.nodes)
    assert lin.metadata_table is None


def test_a_tier_2_with_steps_is_a_node_and_an_empty_one_is_not():
    lin = lineage_of(recipe({"A": schema(tier2=[SORT]), "B": schema()}, {"J": join(["A", "B"], [jn("B")])}, {"p": plot("A"), "q": plot("J")}))
    assert "T2:A" in ids(lin) and "T2:J" not in ids(lin) and "T2:B" not in ids(lin)
    assert ("T1:A", "T2:A") in lin.edges and ("T2:A", "T3:p") in lin.edges and ("T1:J", "T3:q") in lin.edges
    assert lin.node("T2:A").choosable and lin.node("T2:A").tier == 2 and lin.node("T2:A").n_steps == 1


def test_a_tier_2_that_no_plot_reads_is_drawn_but_cannot_be_chosen():
    lin = lineage_of(recipe({"A": schema(), "B": schema()}, {"J": join(["A", "B"], [jn("B")], tier2=[SORT])}, {"p": plot("A")}))
    t2 = lin.node("T2:J")
    assert not t2.choosable and "no plot reads this tier 2" in t2.not_choosable_reason and "J14" in t2.not_choosable_reason
    assert "T2:J" not in lin.reach and "T1:J" in lin.reach


def test_a_joined_table_has_all_its_parents_and_the_node_says_what_it_is():
    lin = lineage_of(recipe({"A": schema(), "B": schema(), "C": schema()}, {"J": join(["A", "B", "C"], [jn("B"), jn("C")], ui_label="The J", description="Joined.")}, {"p": plot("J")}))
    assert [p for p, c in lin.edges if c == "T1:J"] == ["T1:A", "T1:B", "T1:C"]
    node = lin.node("T1:J")
    assert node.table_kind == "joined" and node.ui_label == "The J" and node.description == "Joined." and "A, B, C" in node.what
    assert lin.node("T1:A").table_kind == "original" and lin.node("T3:p").table_kind == "plot"


def test_the_label_and_the_description_of_a_plot_are_the_recipes_own_words():
    lin = lineage_of(recipe({"A": schema()}, plots={"p": plot("A", ui_label="My plot", description="Shows a.")}))
    assert lin.node("T3:p").ui_label == "My plot" and lin.node("T3:p").description == "Shows a."
    assert lin.node("T1:A").ui_label == ""                # no invention when the recipe gives none


def test_a_table_with_nothing_built_from_it_is_a_result_leaf_that_can_be_chosen():
    lin = lineage_of(recipe({"A": schema(), "B": schema(), "Lonely": schema()}, {"J": join(["A", "B"], [jn("B")]), "K": join(["A", "B"], [jn("B")])}, {"p": plot("J")}))
    assert ids(lin, "result") == ["T1:Lonely", "T1:K"] and lin.node("T1:K").choosable and lin.node("T1:Lonely").table_kind == "original"
    assert lin.node("T1:J").kind == "T1"                  # a plot reads it: not a leaf
    reach = lin.reach["T1:K"]
    assert reach.built_from == () and reach.results == ("T1:K",) and [len(p.steps) for p in reach.paths["T1:K"]] == [0]


# ---------------------------------------------------------------- the metadata ---------------------------------

def metadata_recipe():
    return recipe({"A": schema(), "B": schema()}, {"JA": join(["A", META], [jn(META)]), "JB": join(["B", META], [jn(META)])},
                  {"p": plot("JA"), "q": plot("JB")}, metadata=schema())


def test_the_metadata_is_not_drawn_and_a_joined_table_that_takes_it_in_is_tagged():
    lin = lineage_of(metadata_recipe())
    assert not any(n.name == META for n in lin.nodes) and not any(META in e[0] or META in e[1] for e in lin.edges)
    assert lin.metadata_table == META and META not in " ".join(lin.reach)
    assert lin.node("T1:JA").brings_metadata and lin.node("T1:JB").brings_metadata and not lin.node("T1:A").brings_metadata
    assert [p for p, c in lin.edges if c == "T1:JA"] == ["T1:A"]


def test_without_the_metadata_nothing_splits_two_graphs_apart():
    lin = lineage_of(metadata_recipe())
    assert [(c.parents, c.first_places) for c in lin.components] == [(("T1:A",), ("T1:A",)), (("T1:B",), ("T1:B",))]
    assert [c.nodes for c in lin.components] == [("T1:A", "T1:JA", "T3:p"), ("T1:B", "T1:JB", "T3:q")]


def test_a_table_made_from_the_metadata_alone_is_a_root_with_no_arrow_in():
    lin = lineage_of(recipe({"A": schema()}, {"OnlyMeta": join([META], [])}, {"p": plot("OnlyMeta")}, metadata=schema()))
    assert lin.node("T1:OnlyMeta").brings_metadata and [e for e in lin.edges if e[1] == "T1:OnlyMeta"] == []
    assert any(c.parents == ("T1:OnlyMeta",) for c in lin.components)


# ---------------------------------------------------------------- what is built from a place, the paths --------

def test_every_path_with_its_steps_is_listed_for_a_diamond():
    lin = lineage_of(diamond())
    reach = lin.reach["T1:A"]
    assert reach.built_from == ("T1:J1", "T1:J2", "T1:J3", "T3:p") and reach.results == ("T3:p",)
    paths = reach.paths["T3:p"]
    assert [p.nodes for p in paths] == [("T1:J1", "T1:J3", "T3:p"), ("T1:J2", "T1:J3", "T3:p")]
    assert [[s.text for s in p.steps] for p in paths] == [
        ["polars_join: left with B on id", "polars_join: left with J2 on id"],
        ["polars_join: inner with B on id", "polars_join: left with J2 on id"]]
    assert [s.node for s in paths[0].steps] == ["T1:J1", "T1:J3"] and [s.number for s in paths[0].steps] == [1, 1]
    # the place itself is not on its own path; a place below the fork has one path only
    assert [p.nodes for p in lin.reach["T1:J3"].paths["T3:p"]] == [("T3:p",)] and lin.reach["T1:J3"].paths["T3:p"][0].steps == ()


def test_a_plot_is_its_own_result_and_its_place_has_no_steps_after_it():
    lin = lineage_of(recipe({"A": schema()}, plots={"p": plot("A", tier3=[FILTER])}))
    reach = lin.reach["T3:p"]
    assert reach.built_from == () and reach.results == ("T3:p",) and reach.paths["T3:p"][0].steps == ()
    assert [s.text for s in lin.reach["T1:A"].paths["T3:p"][0].steps] == ["modif_filter: a eq x"]


def test_a_place_reaches_all_results_below_it_and_only_those():
    lin = lineage_of(recipe({"A": schema(), "B": schema(), "Z": schema()}, {"J": join(["A", "B"], [jn("B")]), "L": join(["A", "B"], [jn("B")])}, {"p": plot("J"), "q": plot("Z")}))
    assert lin.reach["T1:A"].results == ("T1:L", "T3:p") and lin.reach["T1:Z"].results == ("T3:q",)
    assert "T3:q" not in lin.reach["T1:A"].built_from


def test_components_hold_the_original_parents_of_each_independent_graph():
    lin = lineage_of(recipe({"A": schema(), "B": schema(), "C": schema()}, {"J": join(["A", "B"], [jn("B")])}, {"p": plot("J"), "q": plot("C")}))
    assert [(c.parents, c.first_places) for c in lin.components] == [(("T1:A", "T1:B"), ("T1:A", "T1:B")), (("T1:C",), ("T1:C",))]


# ---------------------------------------------------------------- the columns ---------------------------------

def test_without_a_plan_book_the_columns_are_not_given_and_the_node_says_so():
    lin = lineage_of(recipe({"A": schema()}, plots={"p": plot("A")}))
    assert all(n.columns is None and "no plan was given" in n.columns_note for n in lin.nodes)


def test_the_columns_are_the_plans_names_and_types_at_the_end_of_the_nodes_steps():
    raw = recipe({"A": schema(tier1=[SORT, SORT], tier2=[SORT])}, plots={"p": plot("A", tier3=[FILTER])})
    book = PlanBook.of({("T1:A", 2): [("id", "String"), ("a", "Int64")], ("T2:A", 1): [("id", "String")], ("T3:p", 1): "the engine said no: a is not there"})
    lin = lineage_of(raw, book)
    assert lin.node("T1:A").columns == (("id", "String"), ("a", "Int64")) and lin.node("T1:A").columns_note == ""
    assert lin.node("T2:A").columns == (("id", "String"),)
    failed = lin.node("T3:p")
    assert failed.columns is None and "the engine said no: a is not there" in failed.columns_note


def test_a_place_missing_from_the_book_is_said_not_guessed():
    lin = lineage_of(recipe({"A": schema(tier1=[SORT])}, plots={"p": plot("A")}), PlanBook.of({("T1:A", 0): [("id", "String")]}))
    assert lin.node("T1:A").columns is None and "no entry" in lin.node("T1:A").columns_note


# ---------------------------------------------------------------- shape of the answer ------------------------

def test_the_answer_is_deterministic_and_json_serialisable():
    first, second = lineage_of(diamond()), lineage_of(diamond())
    assert first == second
    text = json.dumps(first.to_dict())
    assert json.loads(text)["nodes"][0]["id"] == "T1:A" and "T1:A" in json.loads(text)["reach"]


def test_a_recipe_that_cannot_be_drawn_is_refused_with_the_graphs_error():
    with pytest.raises(RecipeGraphError):
        lineage_of(recipe({"A": schema()}, plots={"p": plot("Nope")}))
    with pytest.raises(TypeError):
        lineage_of(build_graph(recipe({"A": schema()})))


def test_a_recipe_with_no_join_and_no_plot_is_tables_only():
    lin = lineage_of(recipe({"A": schema(), "B": schema()}))
    assert ids(lin) == ["T1:A", "T1:B"] and ids(lin, "result") == ["T1:A", "T1:B"] and lin.edges == () and len(lin.components) == 2


def test_step_lines_are_short_and_say_when_a_step_cannot_be_read():
    assert step_line({"action": "polars_join", "right_ingredient": "R", "left_on": ["a"], "right_on": ["b"], "how": "inner"}) == "polars_join: inner with R on a = b"
    assert step_line({"action": "polars_select", "exprs": list("abcdef")}) == "polars_select: keeps a, b, c, d, ..."
    assert step_line({"action": "polars_drop", "columns": ["x"]}) == "polars_drop: removes x"
    assert step_line({"action": "polars_head"}) == "polars_head"
    assert "cannot read" in step_line("not a step") and "cannot read" in step_line({"column": "a"})
    assert len(step_line({"action": "polars_sort", "by": "x" * 200})) < 90


# ---------------------------------------------------------------- D-0632: the metadata is not a place ---------

def test_the_metadata_is_not_a_place_of_the_graph_and_the_refusal_is_one_plain_line():
    graph = build_graph(metadata_recipe())
    assert f"T1:{META}" in graph.nodes() and f"T1:{META}" not in graph.places() and f"T2:{META}" not in graph.places()
    assert graph.chosen_places_problem([f"T1:{META}"]) == recipe_tiers.METADATA_NOT_A_PLACE
    assert graph.chosen_places_problem(["T1:A"]) is None


def test_an_audit_step_at_the_metadata_is_refused_everywhere_it_can_come_from():
    raw = metadata_recipe()
    audit = start_audit(raw, "0a1b2c3d")
    step = {"action": "modif_filter", "column": "a", "op": "eq", "value": "x", "na": "remove"}
    for place in (f"T1:{META}", f"T2:{META}"):
        with pytest.raises(AuditCopyError, match="metadata table is not a place"):
            add_step(audit, place, dict(step), "why")
    assert integrity_errors(audit.recipe, raw) == []
    # a hand-made copy (a stored session or a file) that holds one is refused by the integrity check, with the same line
    forged = json.loads(json.dumps(raw))
    forged[META]["tier1"]["audit_steps"] = [{**step, "id": "audit_0a1b2c3d_1", "audit_comment": "why"}]
    errors = integrity_errors(forged, raw)
    assert any(recipe_tiers.METADATA_NOT_A_PLACE in e for e in errors), errors
    assert add_step(audit, "T1:A", dict(step), "why")      # a real table is still fine


# ---------------------------------------------------------------- every shipped recipe -----------------------

ROOT = Path(__file__).resolve().parents[3]
SHIPPED = sorted(glob.glob(str(ROOT / "config" / "data_analysis_recipes" / "*" / "*.yaml")) + glob.glob(str(ROOT / "assets" / "gallery_data" / "*" / "data_analysis_recipe.yaml"))
                 + glob.glob(str(ROOT / "app" / "tests" / "equality" / "recipes" / "*.yaml")))


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_the_lineage_runs_on_every_shipped_recipe_and_is_whole(path):
    raw, _ = load_recipe(path)
    if not raw:
        pytest.skip("the file holds no recipe")
    lin = lineage_of(raw)
    known = set(ids(lin))
    assert all(a in known and b in known for a, b in lin.edges)                         # every arrow end is a node
    assert not any(i.startswith("DS:") or i.split(":", 1)[1] == META for i in known)    # no file, no metadata
    graph = build_graph(raw)
    assert [n.name for n in lin.nodes if n.kind == "T3"] == graph.plots()               # every plot is a node
    assert set(lin.reach) == {n.id for n in lin.nodes if n.choosable}
    assert set(graph.places()) >= set(lin.reach) - {n.id for n in lin.nodes if n.kind == "T2" and not n.choosable}
    for place, reach in lin.reach.items():
        assert reach.results and all(reach.paths[r] for r in reach.results)             # a place reaches itself or something, by at least one path
    parents_of = {c: [p for p, x in lin.edges if x == c] for c in known}
    for node in lin.nodes:
        if node.kind == "T3" or node.table_kind == "joined":
            expected = [graph.node(p).name for p in graph.parents(node.id) if graph.node(p).name != META]
            assert len(parents_of[node.id]) >= (1 if expected else 0) or node.brings_metadata
    assert sorted(n for c in lin.components for n in c.nodes) == sorted(known)          # the components partition the nodes
    json.dumps(lin.to_dict())
