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

Added 2026-11-26 (the owner's test of HOME in Audit mode): the column headings are true for any recipe (a level is not a tier: the demo has joined tables, tier 2 of original tables and plots in
one column), each independent graph has its number at its first dot, the tag "no plot" says it once (the line of a result table no longer repeats it), every dot sits below the headings.

Mutation index (each seen failing): MUTATION V1 `layout` gives every node level 0; MUTATION V2 `around_ids` leaves out the ancestors; MUTATION V3 `view_data` leaves out the `no_plot` mark.
"""
import json
from collections import Counter
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.lineage_view import DX, TOP, around_ids, column_headings, graph_labels, layout, node_detail, view_data
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
    assert plot["choosable"] and plot["built_from"] == [] and plot["line"].endswith(": Plot data, T3")
    assert all(n["line"] and n["detail"] and n["shown"] for n in data["nodes"])


def test_a_place_that_can_be_chosen_says_what_is_built_from_it_and_the_steps_to_each_result(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    res = by["T1:ResFinder"]
    text = "\n".join(res["detail"])
    assert res["choosable"] and "Built from here:" in res["summary"] and "step" in text and " -> " in text
    assert "To AMR Heatmap (plot)" in text
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


# ---------------------------------------------------------------- the column headings and the numbers of the graphs (the owner's items 7 and 8)

def test_the_headings_are_true_in_the_demo_where_a_level_mixes_tiers(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    pos = data["layouts"][""]
    heads = data["heads"][""]
    assert [h["x"] for h in heads] == sorted({p[0] for p in pos.values()}), "one heading for each column, left to right"
    columns = {}
    for i, (x, _y) in pos.items():
        columns.setdefault(x, []).append(by[i])
    for h in heads:
        members = columns[h["x"]]
        kinds = {(n["kind"], n["table_kind"]) for n in members}
        pure_original = all(k in (("T1", "original"), ("result", "original")) for k in kinds)
        if pure_original:
            assert h["text"] == "Original tables"
        else:
            assert h["text"].startswith("Level "), "a column that holds anything but the tier 1 of original tables is not given a tier name"
        assert "Tier" not in h["text"] and "Plot" not in h["text"]
        assert "not a tier" in h["title"]
    assert heads[0]["text"] == "Original tables" and heads[1]["text"] == "Level 1"
    mixed = next(h for h in heads if h["text"] == "Level 1")["title"]
    assert "plots (tier 3)" in mixed and "tier 1 of joined tables" in mixed and "tier 2 of original tables" in mixed, "what the column really holds is listed"
    assert any(len({(n["kind"], n["table_kind"]) for n in ms}) > 1 for ms in columns.values()), "the demo does have a mixed column (the reason for the wording)"


def test_the_headings_of_a_layout_around_a_place_are_true_for_that_layout(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    for place in ("T1:ResFinder", "T3:amr_heatmap"):
        pos = data["layouts"][place]
        for h in data["heads"][place]:
            members = [by[i] for i, p in pos.items() if p[0] == h["x"]]
            kinds = {(n["kind"], n["table_kind"]) for n in members}
            if h["text"] == "Original tables":
                assert all(k in (("T1", "original"), ("result", "original")) for k in kinds)
            else:
                assert h["text"].startswith("Level ")


def test_a_small_recipe_without_a_join_has_two_columns(world):
    book = None
    bare = lineage_of(load_data_analysis_recipe(RECIPES / "3_test_no_joins.yaml").raw, book)
    data = view_data(bare)
    assert [h["text"] for h in data["heads"][""]] == ["Original tables", "Level 1"]
    assert "plot (tier 3)" in data["heads"][""][1]["title"]


def test_column_headings_of_no_dot_are_none():
    assert column_headings([], {}) == []


def test_every_independent_graph_has_its_number_at_its_first_dot(world):
    lin, data = world
    labels = data["glabels"][""]
    assert sorted(labels, key=int) == [str(g["id"] + 1) for g in data["groups"]], "the number is the graph's id plus one, the same as the list heading"
    pos = data["layouts"][""]
    by = {n["id"]: n for n in data["nodes"]}
    for g in data["groups"]:
        lab = labels[str(g["id"] + 1)]
        assert lab["node"] in g["nodes"] and [lab["x"], lab["y"]] == pos[lab["node"]]
        assert (lab["x"], lab["y"]) == min(tuple(pos[i]) for i in g["nodes"]), "the first dot: the lowest x, then the lowest y"
        assert all(by[i]["gnum"] == g["id"] + 1 for i in g["nodes"]), "every line of the list carries the same number"
    # a layout around a place numbers only the graph it shows
    around = data["glabels"]["T1:ResFinder"]
    assert list(around) == [str(by["T1:ResFinder"]["gnum"])]


def test_graph_labels_on_a_small_layout():
    pos = {"a": (22, 60), "b": (100, 48), "c": (22, 44)}
    got = graph_labels(pos, {"a": 0, "b": 0, "c": 1})
    assert got == {"1": {"x": 22, "y": 60, "node": "a"}, "2": {"x": 22, "y": 44, "node": "c"}}
    assert graph_labels({}, {}) == {}


def test_every_dot_sits_below_the_headings_and_inside_the_map(world):
    lin, data = world
    for key, pos in data["layouts"].items():
        w, h = data["sizes"][key]
        assert all(y >= TOP and 0 <= x <= w and y <= h for x, y in pos.values()), key
    assert data["top"] == TOP


def test_the_tag_no_plot_says_it_once(world):
    lin, data = world
    leaves = [n for n in data["nodes"] if n["no_plot"]]
    assert leaves and all("no plot" not in n["line"] for n in leaves), "the repeated sentence is gone from the line; the tag says it"
    text = "\n".join(next(n for n in leaves if n["name"] == "Quality_metrics")["detail"])
    assert "no plot reads it" in text, "the text area explains it once"


# ---------------------------------------------------------------- the names of a line (the owner's item 9, 2026-11-26)

def test_a_line_is_a_plain_name_the_word_table_or_plot_data_and_a_short_tier_tag(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    assert by["T1:Summary_phenotype_length_fragmentation"]["line"] == "Summary phenotype length fragmentation: Table, T1"
    assert by["T3:amr_heatmap"]["line"] == "AMR Heatmap: Plot data, T3"
    assert by["T1:ST22_Anchor"]["line"] == "ST22 Anchor: Table, T1 [+ meta]"
    t2 = next(n for n in data["nodes"] if n["kind"] == "T2")
    assert t2["line"].endswith(": Table, T2")
    for n in data["nodes"]:
        assert n["line"].startswith(n["shown"] + ": ") and "table after its tier" not in n["line"] and "(tier" not in n["line"]
        assert n["line"].split(": ")[1].split(" [")[0] in ("Table, T1", "Table, T2", "Plot data, T3")


def test_the_name_without_a_label_is_the_id_with_spaces_and_the_same_name_is_in_the_text_area(world):
    lin, data = world
    by = {n["id"]: n for n in data["nodes"]}
    node = by["T1:Summary_phenotype_length_fragmentation"]
    assert node["detail"][0] == node["line"], "the text area opens with the same text as the list"
    plot = by["T3:amr_heatmap"]
    text = "\n".join(by["T1:ResFinder"]["detail"])
    assert "AMR Heatmap (plot)" in text and "amr_heatmap" not in text.replace("Id in the recipe", "")
    assert plot["detail"][0] == plot["line"] and "it reads table ResFinder" in "\n".join(plot["detail"])


def test_two_different_tables_with_the_same_label_are_told_apart_by_their_id_and_only_those():
    from utils.display_names import shown_names
    raw = {"data_schemas": {"a_one": {"ui_label": "Results"}, "a_two": {"ui_label": "results"}, "plain": {"ui_label": "Other"}}, "joins": {"j": {"ui_label": "Results"}},
           "analysis_groups": {"g": {"ui_label": "G", "plots": {"p": {"ui_label": "Plot P", "target_dataset": "j"}, "plain": {"target_dataset": "j"}}}}}
    got = shown_names(raw)
    assert got[("table", "a_one")] == "Results (a_one)" and got[("table", "a_two")] == "results (a_two)" and got[("table", "j")] == "Results (j)"
    assert got[("table", "plain")] == "Other" and got[("plot", "p")] == "Plot P"
    assert got[("plot", "plain")] == "plain", "a plot and a table with the same id but other labels stay apart"


def test_a_table_and_a_plot_with_the_same_label_and_id_get_their_kind():
    from utils.display_names import shown_names
    raw = {"data_schemas": {"x": {"ui_label": "Same"}}, "analysis_groups": {"g": {"ui_label": "G", "plots": {"x": {"ui_label": "Same", "target_dataset": "x"}}}}}
    got = shown_names(raw)
    assert got[("table", "x")] == "Same (table x)" and got[("plot", "x")] == "Same (plot x)"


def test_names_without_labels_and_a_recipe_that_is_not_a_mapping():
    from utils.display_names import readable_name, shown_name, shown_names
    assert readable_name(None, "a_b_c") == "a b c" and readable_name("  ", "a_b") == "a b" and readable_name(" Nice ", "x") == "Nice"
    assert shown_names(None) == {} and shown_names({}) == {}
    assert shown_name({}, "table", "gone_table") == "gone table"
