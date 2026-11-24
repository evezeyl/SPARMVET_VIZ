"""The places of an audit step for an open plot (HOME audit, demo step 1): `app/modules/audit_places.py`.

What is proved (pure, no screen):
- on a small recipe (two source tables A and B, a join J with tier-2 steps read by a plot P, a table X read by a plot Q): the lines for P and a column
  are the tier 1 of A, B and J and the tier 2 of J (it has steps), each with the other tables and the plots below it; the plot's own place is not a line;
- a table that does not hold the column at the end of the place is not a line; a place whose plan failed is not a line and is listed apart (never guessed);
- a tier 2 with no steps is not a second line (D-0346: only distinct tables are lines);
- the check of a choice: the first places of several original tables together are valid; one place below another is refused with both named; a place that is not
  a line, an empty choice and a place of another plot are refused in plain words;
- on the demo `1_test_data_ST22_dummy` with its real engine plan: for `amr_heatmap` and `sample_id` the lines are the tier 1 and tier 2 of ResFinder;
  `T1:ResFinder` reaches the 5 plots that the graph says (a plot beside it is not in the list); a column no table holds gives no line.

Mutation index (each seen failing): MUTATION P1 the filter on `node.steps` for a tier 2 is removed (a tier 2 with no steps becomes a line); MUTATION P2 `_holds` always
answers yes (a table without the column becomes a line); MUTATION P3 `choice_problem` skips `chosen_places_problem`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_places.py -q
"""
from pathlib import Path

import pytest

from app.modules.audit_places import choice_problem, line_label, place_lines, plots_below, reach_sentence
from utils.plan_book import PlanBook
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]


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


def book(graph, columns_of):
    """A plan book where each node holds `columns_of(node_id)` (a list of names, or a string = a failure) after every step."""
    entries = {}
    for nid in graph.nodes():
        for k in range(len(graph.node(nid).steps) + 1):
            entries[(nid, k)] = [(c, "String") for c in columns_of(nid)] if not isinstance(columns_of(nid), str) else columns_of(nid)
    return PlanBook.of(entries)


def all_have_id(nid):
    return ["id", "a", "b", "x"]


def test_the_lines_for_a_plot_are_the_tables_upstream_with_the_tables_and_plots_below_each():
    graph = build_graph(small())
    found = place_lines(graph, book(graph, all_have_id), "P", ["id"])
    assert [line.place for line in found.lines] == ["T1:A", "T1:B", "T1:J", "T2:J"]
    by = {line.place: line for line in found.lines}
    assert by["T1:A"].other_tables == ("J",) and by["T1:A"].plots == ("P",) and by["T1:A"].kind == "original"
    assert by["T1:J"].other_tables == () and by["T1:J"].plots == ("P",) and by["T1:J"].kind == "joined"
    assert by["T2:J"].tier == "T2" and by["T2:J"].plots == ("P",)
    assert "T3:P" not in [line.place for line in found.lines], "the plot's own place is 'This plot only', not a line"
    assert all(line.place != "T1:X" for line in found.lines), "X is not upstream of P"
    assert found.unknown == ()


def test_a_tier2_with_no_steps_is_not_a_second_line():
    raw = small()
    del raw["joins"]["J"]["tier2"]
    graph = build_graph(raw)
    found = place_lines(graph, book(graph, all_have_id), "P", ["id"])
    assert [line.place for line in found.lines] == ["T1:A", "T1:B", "T1:J"]


def test_a_table_that_does_not_hold_the_column_is_not_a_line_and_a_failed_plan_is_listed_apart():
    graph = build_graph(small())
    only_b = lambda nid: ["id", "b"] if nid in ("T1:B",) else ["id"]
    found = place_lines(graph, book(graph, only_b), "P", ["b"])
    assert [line.place for line in found.lines] == ["T1:B"], "A, J and J's tier 2 do not hold 'b' in this book"
    failing = lambda nid: "the engine could not read the file" if nid == "T1:A" else ["id", "b"]
    found = place_lines(graph, book(graph, failing), "P", ["b"])
    assert "T1:A" not in [line.place for line in found.lines]
    assert found.unknown == (("T1:A", "the engine could not read the file"),), "a failed plan is said, never guessed"


def test_several_columns_must_all_be_held_at_the_place():
    graph = build_graph(small())
    cols = lambda nid: ["id", "a"] if nid == "T1:A" else ["id"]
    assert [l.place for l in place_lines(graph, book(graph, cols), "P", ["id", "a"]).lines] == ["T1:A"]
    assert [l.place for l in place_lines(graph, book(graph, cols), "P", ["id"]).lines] == ["T1:A", "T1:B", "T1:J", "T2:J"]


def test_the_sentences_say_built_from_it_never_changed():
    graph = build_graph(small())
    by = {l.place: l for l in place_lines(graph, book(graph, all_have_id), "P", ["id"]).lines}
    assert line_label(by["T1:A"]) == "Table A (tier 1)" and line_label(by["T2:J"]) == "Table J (tier 2)"
    assert reach_sentence(by["T1:A"]) == "1 other table and 1 plot are built from it."
    assert reach_sentence(by["T1:J"]) == "1 plot is built from it."
    assert "changed" not in reach_sentence(by["T1:A"])


def test_the_first_places_of_several_original_tables_are_valid_together_and_one_below_another_is_refused():
    graph = build_graph(small())
    offered = place_lines(graph, book(graph, all_have_id), "P", ["id"]).lines
    assert choice_problem(graph, offered, ["T1:A", "T1:B"]) is None
    assert choice_problem(graph, offered, ["T1:J"]) is None
    for chosen in (["T1:A", "T1:J"], ["T1:J", "T1:A"], ["T1:J", "T2:J"]):
        sentence = choice_problem(graph, offered, chosen)
        assert sentence and all(f"'{n}'" in sentence for n in chosen), sentence
    assert "Choose at least one" in choice_problem(graph, offered, [])
    assert "not one of the places offered" in choice_problem(graph, offered, ["T1:X"])


def test_a_place_that_is_not_offered_for_this_step_is_refused_even_when_it_is_a_place_of_the_recipe():
    graph = build_graph(small())
    cols = lambda nid: ["id", "a"] if nid == "T1:A" else ["id"]
    offered = place_lines(graph, book(graph, cols), "P", ["a"]).lines
    assert "not one of the places offered" in choice_problem(graph, offered, ["T1:B"])


def test_plots_below_lists_each_plot_once_in_the_order_of_the_recipe():
    graph = build_graph(small())
    assert plots_below(graph, ["T1:A", "T1:B"]) == ["P"]
    assert plots_below(graph, ["T1:X"]) == ["Q"]
    assert plots_below(graph, []) == []
    with pytest.raises(KeyError):
        plots_below(graph, ["T1:nope"])


def test_the_plot_must_exist():
    graph = build_graph(small())
    with pytest.raises(KeyError):
        place_lines(graph, book(graph, all_have_id), "nope", ["id"])


# ------------------------------------------------------------------ the demo, with the engine's real plan
@pytest.fixture(scope="module")
def demo():
    from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
    from app.modules.orchestrator import DataOrchestrator
    from app.modules.plan_composer import compose_plan_book
    pipelines = ROOT / "config" / "data_analysis_recipes" / "pipelines"
    clear_data_analysis_recipe_cache()
    orch = DataOrchestrator(pipelines, ROOT / "assets" / "test_data")
    loaded = load_data_analysis_recipe(pipelines / "1_test_data_ST22_dummy.yaml")
    graph = build_graph(loaded.raw)
    yield graph, compose_plan_book(orch, "1_test_data_ST22_dummy", loaded, graph)
    clear_data_analysis_recipe_cache()


def test_demo_amr_heatmap_offers_resfinder_tier1_and_tier2_and_its_reach_is_the_graphs(demo):
    graph, plans = demo
    found = place_lines(graph, plans, "amr_heatmap", ["sample_id"])
    assert [line.place for line in found.lines] == ["T1:ResFinder", "T2:ResFinder"]
    first = found.lines[0]
    assert first.kind == "original" and first.plots == tuple(p for p in graph.plots() if f"T3:{p}" in graph.below("T1:ResFinder"))
    assert "amr_heatmap" in first.plots and "mlst_bar" not in first.plots, "a plot beside it is not below it"
    assert found.lines[1].other_tables == () and found.lines[1].plots == ("amr_heatmap",)


def test_demo_a_column_that_no_table_upstream_holds_gives_no_line(demo):
    graph, plans = demo
    assert place_lines(graph, plans, "amr_heatmap", ["no_such_column"]).lines == ()
    assert place_lines(graph, plans, "amr_heatmap", ["sample_id"]).unknown == ()


def test_demo_the_marker_column_of_resfinder_is_held_by_the_resfinder_tables_and_by_nothing_beside_it(demo):
    """The marker column that the completion adds (D-0586, D-0613) is a column of the table at its tier 1: the line the marker case of the demo uses."""
    graph, plans = demo
    found = place_lines(graph, plans, "amr_heatmap", ["ResFinder_not_in_original_data"])
    assert [line.place for line in found.lines] == ["T1:ResFinder", "T2:ResFinder"], found
    assert place_lines(graph, plans, "mlst_bar", ["ResFinder_not_in_original_data"]).lines == (), "MLST's plot does not read ResFinder"
