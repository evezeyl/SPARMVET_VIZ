"""The lineage walk on the shipped recipes: a table that no plot reads but that the walk reaches is a line (D-0451; D-0346 changed in the part "a join that no plot reads is not
offered"). The plan of every place is the engine's (`compose_plan_book`), the same as the dialog will use.

What is proved:
- the demo recipe (`1_test_data_ST22_dummy`), the column `sample_id` looked at from a plot: the four joins that no plot reads and that the metadata reaches
  (FastP_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, AR1_MLST_Serotype_Virulence) are lines of tier 1 that say no plot reads them, ticked like the others (PROVISIONAL, see
  `libs/utils/src/utils/lineage_walk.py` P4); every line the walk gave before is still there, unchanged (the number of lines goes from 37 to 41 at the levels T1, T2, T3 and from 44 to 48
  with the source level);
- the sources that no join links to the lineage (Quality_metrics, Detailed_summary, and Summary, Summary_quality that declare the key) are not lines and are listed as `outside`, as before (D-0415);
- on every shipped recipe and every plot and declared key: the accounting property holds (each place once; every table the lineage reaches is a line or a note; the places not accounted for are
  exactly those no linked table reaches); the numbers of the tables no plot reads are counted so that an empty check cannot pass.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_lineage_unread_tables_demo.py -q
"""
import json
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from utils.lineage_records import Start
from utils.lineage_walk import LineageIndex
from utils.plan_book import Plan
from utils.recipe_graph import build_graph

ROOT = Path(__file__).resolve().parents[2]
BASELINE = json.loads((ROOT / "app" / "tests" / "golden" / "baseline.json").read_text(encoding="utf-8"))
RECIPES, RAW = ROOT / BASELINE["recipes_dir"], ROOT / BASELINE["raw_data"]
DEMO = "1_test_data_ST22_dummy"
NO_PLOT_READS = ["T1:FastP_with_metadata", "T1:Bracken_with_metadata", "T1:ResFinder_with_metadata", "T1:AR1_MLST_Serotype_Virulence"]
TIERS, WITH_SOURCE = ("T1", "T2", "T3"), ("source", "T1", "T2", "T3")


def index_of(recipe_id):
    clear_data_analysis_recipe_cache()
    orch = DataOrchestrator(RECIPES, RAW)
    loaded = load_data_analysis_recipe(RECIPES / f"{recipe_id}.yaml")
    graph = build_graph(loaded.raw)
    return graph, LineageIndex(graph, compose_plan_book(orch, recipe_id, loaded, graph))


@pytest.fixture(scope="module")
def demo():
    yield index_of(DEMO)
    clear_data_analysis_recipe_cache()


def test_the_four_joins_no_plot_reads_are_lines_of_the_sample_id_and_the_other_lines_are_the_same(demo):
    _graph, index = demo
    for levels, before in ((TIERS, 37), (WITH_SOURCE, 44)):
        walk = index.walk(Start("T3:miaou", "sample_id"), levels=levels)
        no_plot = [x for x in walk.lines if x.no_plot_reads]
        assert [x.place for x in no_plot] == NO_PLOT_READS, levels
        assert len(walk.lines) == before + 4, levels                                                    # 37 -> 41 and 44 -> 48
        assert all(x.tier == "T1" and x.kind == "table" and x.state == "tick" and x.reason is None for x in no_plot)
        assert all(x.occurrences[0].name == "sample_id" and x.occurrences[0].type == "String" for x in no_plot)
        assert all(x.reach.plots == frozenset() and x.reach.n_tables == 0 and x.reach.n_tables_no_plot >= 1 for x in no_plot)
        assert sum(1 for x in walk.lines if not x.no_plot_reads) == before


def test_the_sources_no_join_links_are_not_lines_and_are_listed_as_outside_as_before(demo):
    _graph, index = demo
    walk = index.walk(Start("T3:miaou", "sample_id"), levels=TIERS)
    assert sorted(o.table for o in walk.outside) == ["Detailed_summary", "Quality_metrics", "Summary", "Summary_quality"]
    assert not {"T1:Quality_metrics", "T1:Detailed_summary"} & set(walk.accounted)


@pytest.mark.parametrize("recipe_id", sorted(p.stem for p in RECIPES.glob("*.yaml")))
def test_the_accounting_property_holds_on_every_shipped_recipe_for_every_plot_and_declared_key(recipe_id):
    graph, index = index_of(recipe_id)
    keys = sorted({name for table in graph.collections() for name in graph.declared_entity_keys(table)})
    walked = no_plot = 0
    for node in (n for n in graph.nodes() if graph.node(n).kind == "T3"):
        for column in keys:
            plan = index.plan_end(node)
            if not isinstance(plan, Plan) or not plan.has(column):                                       # a plot that does not carry the column cannot be the place the user looks from
                continue
            walk = index.walk(Start(node, column), levels=TIERS)
            begin = (node, *index.end(node)[1:], column)
            holders = {occ[0] for occ in index.component([begin])}
            reached = {index.place_of[n] for h in holders for n in [h] + index.forward(h) if not n.startswith("DS:")}
            assert len(walk.accounted) == len(set(walk.accounted)) and set(walk.accounted) == reached, (recipe_id, node, column)
            no_plot += sum(1 for x in walk.lines if x.no_plot_reads)
            walked += 1
    if recipe_id == DEMO:
        assert walked == 16 and no_plot == 14 * 4                                                        # 16 plots hold sample_id; 14 of them reach the 4 joins, 2 do not
    else:
        assert walked > 0 or recipe_id == "stress_test_master"                                          # that recipe declares no key its plots carry
