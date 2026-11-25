"""The rule of places (D-0553, D-0555, D-0560): places, below, valid sets of chosen places, derived places. Pure graph, no engine."""
import glob
from pathlib import Path

import pytest

from utils.recipe_graph import build_graph, chosen_places_problem, derived_places, places_of
from utils.recipe_graph import below as below_of
from utils.recipe_loader import load_recipe

ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"
SHIPPED = sorted(
    glob.glob(str(ROOT / "config" / "data_analysis_recipes" / "*" / "*.yaml"))
    + glob.glob(str(ROOT / "assets" / "gallery_data" / "*" / "data_analysis_recipe.yaml"))
    + glob.glob(str(ROOT / "app" / "tests" / "equality" / "recipes" / "*.yaml")))


def small():
    def sch(cols):
        return {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": {c: {"type": "String"} for c in cols}, "tier1": {"steps": []}}
    return {"id": "r",
            "data_schemas": {"A": sch(["id", "a"]), "B": sch(["id", "b"])},
            "joins": {"J": {"ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                            "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]}}},
            "analysis_groups": {"g": {"ui_label": "G", "plots": {
                "P": {"target_dataset": "J", "mapping": {"x": "id"}, "layers": [{"name": "geom_col"}],
                      "tier3": {"steps": [{"action": "polars_sort", "by": ["id"], "maintain_order": True}]}}}}}}


def test_places_are_tier1_of_tables_tier2_read_by_a_plot_and_tier3_of_plots_never_the_files():
    ids = places_of(small())
    assert ids == ["T1:A", "T1:B", "T1:J", "T2:J", "T3:P"]          # T2:A and T2:B are read by no plot; DS nodes never
    assert not any(i.startswith("DS:") for i in ids)


def test_below_follows_join_tier2_and_plot_edges_and_not_the_place_itself():
    assert below_of(small(), "T1:A") == ["T2:A", "T1:J", "T2:J", "T3:P"]
    assert below_of(small(), "T1:J") == ["T2:J", "T3:P"]
    assert below_of(small(), "T3:P") == []
    with pytest.raises(KeyError):
        below_of(small(), "T1:nope")


def test_the_tier1_places_of_the_original_tables_together_are_valid():
    assert chosen_places_problem(small(), ["T1:A", "T1:B"]) is None
    assert chosen_places_problem(small(), []) is None


def test_one_place_below_another_is_refused_with_both_named_in_either_order():
    for chosen in (["T1:A", "T1:J"], ["T1:J", "T1:A"], ["T1:A", "T3:P"], ["T2:J", "T3:P"]):
        sentence = chosen_places_problem(small(), chosen)
        assert sentence and all(f"'{n}'" in sentence for n in chosen)
    assert chosen_places_problem(small(), ["T1:A", "T1:A"]) is None        # the same place twice is one place


def test_an_unknown_id_a_first_node_and_an_unread_tier2_are_refused_in_plain_words():
    assert "not a place of this recipe" in chosen_places_problem(small(), ["T1:zzz"])
    assert "the file as read" in chosen_places_problem(small(), ["DS:A"])
    assert "no plot reads" in chosen_places_problem(small(), ["T2:A"])


def test_derived_places_are_the_places_below_the_chosen_ones():
    assert derived_places(small(), ["T1:A"]) == ["T1:J", "T2:J", "T3:P"]
    assert derived_places(small(), ["T1:A", "T1:B"]) == ["T1:J", "T2:J", "T3:P"]
    assert derived_places(small(), ["T3:P"]) == []
    assert "T2:A" not in derived_places(small(), ["T1:A"])                  # a node that is not a place is not listed


def _load(path):
    raw, _ = load_recipe(path)
    if not raw:
        pytest.skip("the file holds no recipe")
    return raw


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: str(Path(p).relative_to(ROOT)))
def test_the_rule_holds_on_every_shipped_recipe(path):
    graph = build_graph(_load(path))
    ids = graph.places()
    assert not any(graph.node(i).kind == "DS" for i in ids)
    originals = [f"T1:{t}" for t in graph.collections() if graph.node(f"T1:{t}").collection_kind == "schema" and not graph.is_metadata_node(f"T1:{t}")]
    assert chosen_places_problem(graph, originals) is None
    assert not any(graph.is_metadata_node(i) for i in ids)                  # D-0632: the metadata table is never a place
    for place in ids:
        under = graph.below(place)
        assert place not in under
        assert not set(under) & {n for n in graph.lineage_back(place)}      # no cycle: nothing is both above and below
        for other in under:
            if other in ids:
                assert chosen_places_problem(graph, [place, other]), f"{place} with {other} must be refused"
                assert other in graph.derived_places([place])


def test_the_demo_counts_against_the_study():
    graph = build_graph(_load(str(DEMO)))
    assert len(graph.nodes()) == 87   # 85 before the one big move: the two QA tables made data schemas add their source nodes (D-0610)
    # the study counts 58 places by its definition (T1 of 28 tables, T2 of the 13 read by a plot, T3 of 17 plots) and 55 where the engine accepts a step
    assert len(graph.places()) == 57   # 58 by the study's definition, less the metadata table (D-0632: it is not an audit place)
