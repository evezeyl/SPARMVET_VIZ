"""The data the lineage panel hands to the browser: layout, subsets, words (LINEAGE-VIEW-G, D-0629, D-0634).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_lineage_view.py -q

What is proved (the design expects: one dot and one list line for every node, the list is the text twin of the map; no two dots share a place; an arrow always runs forward; "around my
selection" keeps exactly the lineage back and forward of the place and has its own compact layout; the metadata is never drawn; what cannot be chosen says why; the data is plain JSON):
- `layout` on small graphs: a chain, a diamond, two independent graphs (kept apart), an empty input, the same input twice;
- the demo `1_test_data_ST22_dummy`: 51 nodes, 6 independent graphs, every node placed, no shared position, every arrow goes right, the metadata is not a node, 11 tables carry "[+ meta]",
  the six result tables no plot reads are marked, the layout of "around my selection" holds exactly the ancestors, the place and what is built from it;
- the text of a place that can be chosen says what is built from it and lists the steps between it and each result; the text of one that cannot says why; the data survives
  `json.dumps` and equals itself on a second call (deterministic);
- the largest shipped recipe (the demo) stays small enough to hand to the browser (a bound on the size of the JSON).

Mutation index (each seen failing): MUTATION V1 `layout` gives every node level 0; MUTATION V2 `around_ids` leaves out the ancestors; MUTATION V3 `view_data` leaves out the `no_plot` mark.
"""
import json
from collections import Counter
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.lineage_view import DX, around_ids, layout, node_detail, view_data
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from utils.lineage_data import lineage_of

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))
RECIPES, RAW = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]
DEMO = "1_test_data_ST22_dummy"


# ---------------------------------------------------------------- the layout on small graphs

def _no_shared_position(pos):
    return len(set(pos.values())) == len(pos)


def test_a_chain_goes_right_and_a_diamond_puts_the_two_branches_in_one_level():
    pos, size = layout(["a", "b", "c"], [("a", "b"), ("b", "c")])
    assert pos["a"][0] < pos["b"][0] < pos["c"][0] and _no_shared_position(pos)
    pos, size = layout(["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    assert pos["b"][0] == pos["c"][0] and pos["b"][1] != pos["c"][1] and pos["d"][0] == pos["a"][0] + 2 * DX


def test_two_independent_graphs_do_not_mix_inside_a_level():
    ids = ["a1", "b1", "a2", "b2"]
    edges = [("a1", "a2"), ("b1", "b2")]
    pos, _ = layout(ids, edges, {"a1": 0, "a2": 0, "b1": 1, "b2": 1})
    level0 = sorted(["a1", "b1"], key=lambda i: pos[i][1])
    assert level0 == ["a1", "b1"] and sorted(["a2", "b2"], key=lambda i: pos[i][1]) == ["a2", "b2"]


def test_an_empty_input_gives_an_empty_map_and_the_same_input_gives_the_same_map():
    assert layout([], []) == ({}, (0, 0))
    a = layout(["a", "b", "c"], [("a", "c"), ("b", "c")])
    assert a == layout(["a", "b", "c"], [("a", "c"), ("b", "c")])
    assert layout(["x"], [])[0]["x"][0] == layout(["x"], [])[0]["x"][0]
    assert layout(["a", "b"], [("a", "zzz")])[0]["a"] != layout(["a", "b"], [("a", "zzz")])[0]["b"], "an arrow to a node that is not shown is ignored"


# ---------------------------------------------------------------- the demo

@pytest.fixture(scope="module")
def world():
    clear_data_analysis_recipe_cache()
    orch = DataOrchestrator(RECIPES, RAW)
    loaded = load_data_analysis_recipe(RECIPES / f"{DEMO}.yaml")
    book = compose_plan_book(orch, DEMO, loaded)
    lin = lineage_of(loaded.raw, book)
    yield lin, view_data(lin)
    clear_data_analysis_recipe_cache()


def test_the_demo_has_one_dot_and_one_line_for_every_node_and_the_map_is_sound(world):
    lin, data = world
    ids = [n["id"] for n in data["nodes"]]
    assert len(ids) == 51 and len(set(ids)) == 51 and ids == [n.id for n in lin.nodes]
    assert len(data["groups"]) == 6 and sum(len(g["nodes"]) for g in data["groups"]) == 51, "every node is in the list once, under its independent graph"
    pos = {i: tuple(p) for i, p in data["layouts"][""].items()}
    assert set(pos) == set(ids) and _no_shared_position(pos)
    for parent, child in data["edges"]:
        assert pos[parent][0] < pos[child][0], (parent, child)
    w, h = data["sizes"][""]
    assert all(0 <= x <= w and 0 <= y <= h for x, y in pos.values())
    assert not any(n["name"] == data["metadata_table"] or n["id"].startswith("DS:") for n in data["nodes"]), "the metadata and the files are not drawn"


def test_the_words_of_the_nodes(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    assert sum(n["meta"] for n in data["nodes"]) == 11 and by["T1:ST22_Anchor"]["line"].endswith("[+ meta]") and "[+ meta]" not in by["T1:ResFinder"]["line"]
    leaves = sorted(n["name"] for n in data["nodes"] if n["no_plot"])
    assert leaves == sorted(["Quality_metrics", "Detailed_summary", "FastP_with_metadata", "Bracken_with_metadata", "ResFinder_with_metadata", "AR1_MLST_Serotype_Virulence"])
    assert Counter(n["cls"] for n in data["nodes"]) == {"tier1": 21, "tier2": 7, "result": 23}
    plot = next(n for n in data["nodes"] if n["kind"] == "T3")
    assert plot["choosable"] and plot["built_from"] == [] and "plot" in plot["tier_word"]
    assert all(n["line"] and n["detail"] and n["tier_word"] for n in data["nodes"])


def test_a_place_that_can_be_chosen_says_what_is_built_from_it_and_the_steps_to_each_result(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    res = by["T1:ResFinder"]
    text = "\n".join(res["detail"])
    assert res["choosable"] and "Built from here:" in res["summary"] and "step" in text and " -> " in text
    assert "To amr_heatmap (plot)" in text
    leaf = "\n".join(by["T1:Quality_metrics"]["detail"])
    assert "result table of its own" in leaf and "no figure changes" in leaf


def test_a_tier2_no_plot_reads_cannot_be_chosen_and_says_why(world):
    lin, data = world
    blocked = [n for n in lin.nodes if not n.choosable]
    for n in blocked:
        shown = next(x for x in data["nodes"] if x["id"] == n.id)
        assert "Cannot be chosen:" in "\n".join(shown["detail"]) and shown["reason"] and shown["id"] not in data["layouts"]
    assert set(data["layouts"]) == {""} | {n.id for n in lin.nodes if n.choosable}


def test_around_my_selection_keeps_the_lineage_back_and_forward_and_has_its_own_compact_layout(world):
    lin, data = world
    place = "T1:ResFinder"
    keep = around_ids(lin, place)
    back = {p for p, c in lin.edges if c == place}
    assert place in keep and set(lin.reach[place].built_from) <= set(keep)
    assert keep == [n.id for n in lin.nodes if n.id in set(keep)], "graph order"
    # the parents of every shown node (except the place's own parents, none here) are shown: ancestors are complete
    for plot in [n for n in lin.nodes if n.kind == "T3"]:
        keep_plot = set(around_ids(lin, plot.id))
        assert plot.id in keep_plot
        for p, c in lin.edges:
            if c in keep_plot and (c == plot.id or c in set(lin.reach[plot.id].built_from) | {plot.id}):
                assert p in keep_plot, (plot.id, p, c)
    sub = data["layouts"][place]
    assert set(sub) == set(keep) and len(sub) < 51 and _no_shared_position({k: tuple(v) for k, v in sub.items()})
    assert data["sizes"][place][0] <= data["sizes"][""][0]
    assert next(n for n in data["nodes"] if n["id"] == place)["around"] == keep
    with pytest.raises(KeyError):
        around_ids(lin, "T1:nothing")
    assert back == set()      # an original table has no parent


def test_the_data_is_plain_json_and_the_same_on_a_second_call(world):
    lin, data = world
    text = json.dumps(data)
    assert text == json.dumps(view_data(lin))
    assert len(text) < 250_000, "the largest shipped recipe stays small for the browser"
    assert "</script" not in text.lower()


def test_node_detail_of_a_node_without_plan_says_why(world):
    bare = lineage_of(load_data_analysis_recipe(RECIPES / f"{DEMO}.yaml").raw, None)
    node = bare.node("T1:ResFinder")
    lines = node_detail(bare, node)
    assert any("not known" in ln or "never guessed" in ln or "no plan" in ln for ln in lines)
