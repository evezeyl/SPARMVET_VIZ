"""The audit steps written at a place (HOME audit): `app/modules/audit_places.py`.

FLOW-3 (2026-11-27): the dialog that listed the places of a step as tick lines is gone (D-0662, D-0675), and so are its tests (`place_lines`, `path_rows`, `choice_problem`, `line_label`,
`reach_sentence`, `own_place_line`: the 17 tests of the lines, the path and the choice). What they protected is protected where it lives now: the rule of places (at most one place on a
path, the first places of several original tables together, a table and the plot below it together) is `RecipeGraph.chosen_places_problem` (`libs/utils/tests/test_rule_of_places.py` and the test
below), the choice of the places of a trial is `audit_try.trial_places` (`test_audit_try.py`), the metadata is never a place (`test_lineage_data_demo.py`).

What is proved here (pure, no screen):
- the third tier is the same mechanism: the place of a plot's own tier 3 is `T3:<plot>`; a plot is reached by a step at its own tier 3 and by a step at a table above it and by no other; the rule
  of places covers a table and a plot below it together; a step at a plot is baked into the plot's own `tier3.steps`; the words and the records name it;
- `plots_below` lists each plot once, in the order of the recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_places.py -q
"""

import pytest

from app.modules.audit_places import bake_place_steps, nodes_reaching_plot, own_plot_place, place_step_records, place_words, plots_below
from utils.recipe_graph import build_graph



def sch(cols):
    return {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": {c: {"type": "String"} for c in cols}, "tier1": {"steps": []}}


def small():
    return {"id": "r",
            "data_schemas": {"A": sch(["id", "a"]), "B": sch(["id", "b"]), "X": sch(["id", "x"])},
            "joins": {"J": {"ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                            "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]},
                            "tier2": {"steps": [{"action": "polars_sort", "by": ["id"], "maintain_order": True}]}}},
            "analysis_groups": {"g": {"ui_label": "G", "plots": {
                "P": {"target_dataset": "J", "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}]},
                "Q": {"target_dataset": "X", "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}]}}}}}


def test_plots_below_lists_each_plot_once_in_the_order_of_the_recipe():
    graph = build_graph(small())
    assert plots_below(graph, ["T1:A", "T1:B"]) == ["P"]
    assert plots_below(graph, ["T1:X"]) == ["Q"]
    assert plots_below(graph, []) == []
    with pytest.raises(KeyError):
        plots_below(graph, ["T1:nope"])


# -- the third tier: a step at a plot is a step at a place, like a step at a table (demo step 7) ----------------------------------

def _node(place, node_type="filter_row", column="id", node_id=None):
    params = {"column": column, "op": "ne", "value": "s1", "na": "keep"} if node_type == "filter_row" else {"column": column}
    return {"id": node_id or f"n_{place}", "node_type": node_type, "place": place, "params": params, "reason": "r", "created_at": "t", "active": True}


def test_a_plot_is_reached_by_a_step_at_its_own_tier3_and_by_a_step_at_a_table_above_it_and_by_no_other():
    graph = build_graph(small())
    nodes = [_node("T3:P"), _node("T1:A"), _node("T3:Q"), _node("T1:X"), _node("T2:J")]
    assert [n["place"] for n in nodes_reaching_plot(graph, nodes, "P")] == ["T3:P", "T1:A", "T2:J"]
    assert [n["place"] for n in nodes_reaching_plot(graph, nodes, "Q")] == ["T3:Q", "T1:X"]
    assert nodes_reaching_plot(graph, [_node("T1:nope")], "P") == [], "a place the recipe does not have reaches no plot"
    assert nodes_reaching_plot(graph, [], "P") == []


def test_the_plot_of_a_tier3_place_is_built_from_it_and_no_other_plot_is():
    graph = build_graph(small())
    assert plots_below(graph, ["T3:P"]) == ["P"]
    assert plots_below(graph, ["T3:Q", "T1:A"]) == ["P", "Q"]
    assert plots_below(graph, ["T3:P", "T3:P"]) == ["P"]
    assert own_plot_place("P") == "T3:P"


def test_the_rule_of_places_covers_a_table_and_the_plot_below_it_together():
    graph = build_graph(small())
    assert graph.chosen_places_problem(["T3:P"]) is None, "the plot's own place alone is a valid choice"
    for chosen in (["T1:A", "T3:P"], ["T3:P", "T2:J"], ["T1:J", "T3:P"]):
        sentence = graph.chosen_places_problem(chosen)
        assert sentence and all(f"'{n}'" in sentence for n in chosen), (chosen, sentence)
    assert own_plot_place("P") == "T3:P"


def test_two_plots_on_one_table_are_two_separate_places_and_may_be_chosen_together():
    raw = small()
    raw["analysis_groups"]["g"]["plots"]["P2"] = {"target_dataset": "J", "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}]}
    graph = build_graph(raw)
    assert graph.chosen_places_problem(["T3:P", "T3:P2"]) is None
    assert graph.chosen_places_problem(["T3:P", "T1:X"]) is None, "a plot and a table that is not above it are separate decisions' places"
    assert plots_below(graph, ["T3:P"]) == ["P"], "a step at P does not reach P2, which reads the same table"


def test_the_words_and_the_records_name_the_plot_place():
    graph = build_graph(small())
    assert place_words("T3:P") == "Plot P (tier 3)" and place_words("T1:A") == "Table A (tier 1)"
    nodes = [_node("T3:P", node_id="x1"), _node("T1:A", node_id="x2")]
    records = place_step_records(graph, nodes)
    assert [(r["id"], r["place_words"], r["plots"]) for r in records] == [("x1", "Plot P (tier 3)", ["P"]), ("x2", "Table A (tier 1)", ["P"])]


def test_a_step_at_a_plot_is_baked_into_the_tier3_of_that_plot_and_nowhere_else_and_the_original_is_untouched():
    raw = small()
    before = repr(raw)
    baked = bake_place_steps(raw, [_node("T3:P", column="id", node_id="a1"), _node("T1:A", column="id", node_id="a2"), _node("T3:P", "drop_column", "a", "a3")])
    assert repr(raw) == before, "the argument is not changed"
    plot = baked["analysis_groups"]["g"]["plots"]["P"]
    assert [s["action"] for s in plot["tier3"]["steps"]] == ["modif_filter", "polars_drop"], "in the order the nodes were written"
    assert "a1" in plot["comment"] and "a3" in plot["comment"] and "a2" not in plot["comment"]
    assert "tier3" not in baked["analysis_groups"]["g"]["plots"]["Q"], "another plot is not touched"
    assert baked["data_schemas"]["A"]["tier1"]["steps"][-1]["action"] == "modif_filter", "the step at the table is still baked at the table"
    with pytest.raises(KeyError, match="no plot 'nope'"):
        bake_place_steps(raw, [_node("T3:nope")])
