"""The lineage walk, properties that must hold for every start (LBFB step 1): nothing is lost, every line can be written, the same input gives the
same output, the walk reads nothing and changes nothing. Invariants I1, I3 and I8 of the logic review, and the cases L069, L075 to L078 and L087 of
`tmpAI/panel/lineage_tests/DESIGN.md`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_walk_properties.py -q
"""
import builtins
import copy
import os
import random
import subprocess
import sys
import time
from typing import Any, Dict, Iterator, Tuple

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import TIERS, independent_places, places, setup

from utils import audit_copy
from utils.lineage_records import GROUPS, JOIN_LINKED, LINEAGE, Start, Walk
from utils.lineage_walk import LineageIndex
from utils.plan_book import PlanBook, Plan


def fixtures() -> Iterator[Tuple[str, Any, Any]]:
    yield ("chain",) + F.chain()
    yield ("chain_dropped",) + F.chain(a_steps=[F.keep("val", "gt", 0.0), F.select("sample_id", "year", "val")])
    yield ("chain_cast",) + F.chain(a_steps=[F.keep("val", "gt", 0.0), F.cast(["year"], "String")])
    yield ("chain_recompute",) + F.chain(a_steps=[F.keep("val", "gt", 0.0), F.with_columns(year="pl.col('year') + 1")])
    yield ("chain_failed",) + F.chain(b_steps=[F.drop("nope")])
    yield ("tiers",) + F.tiers()
    yield ("tiers_u",) + F.tiers(u_declares_key=True, u_plot=True)
    recipe, tables = F.tiers()
    recipe["joins"]["J2"]["tier1"]["steps"].append(F.select("sample_id", "val", "year"))
    yield ("tiers_select", recipe, tables)
    renamed = F.recipe({"A": F.schema(["sample_id", "country"], [F.rename(country="origin")], keys=["sample_id"]), "B": F.schema(["isolate", "country"])},
                       {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"))])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    yield "renamed", renamed, {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(isolate=["S1"], country=["SE"])}
    for name, recipe, tables in F.followed():
        yield name, recipe, tables


def all_starts(recipe, tables) -> Iterator[Tuple[str, str]]:
    replay = O.replay(recipe, tables)
    for node in sorted({n for (n, _k) in replay.frames}):
        end = replay.end(node)
        if end is not None and not any(n == node for (n, _k) in replay.failures):       # the table of a failed place cannot be looked at
            for column in end.columns:
                yield node, column


def all_walks() -> Iterator[Tuple[str, Any, Any, str, str, str, Walk]]:
    for name, recipe, tables in fixtures():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        for node, column in all_starts(recipe, tables):
            for scope in GROUPS:
                yield name, recipe, tables, node, column, scope, index.walk(Start(node, column), levels=TIERS).within(scope)


def test_I1_every_line_can_be_written_and_names_a_column_the_plan_has_at_the_end_of_the_place():
    seen = 0
    replays = {name: O.replay(recipe, tables) for name, recipe, tables in fixtures()}
    for name, recipe, tables, node, column, scope, walk in all_walks():
        replay = replays[name]
        for x in walk.lines:
            copy_ = audit_copy.start_audit(recipe)
            audit_copy.add_step(copy_, x.place, F.keep(x.occurrences[0].name if x.occurrences else column, "ne", "S3"), "a reason")      # add_step accepts the place
            last = x.covers[0]
            end = replay.end(last)
            for occurrence in x.occurrences:
                assert end is not None and occurrence.name in end.columns and occurrence.type == str(end.schema[occurrence.name]), (name, node, column, x.place)
            seen += 1
    assert seen > 500                                                                                  # the property is run on every column of every table of every fixture


def test_I3_nothing_is_lost_every_place_of_the_reach_is_a_line_or_a_note():
    seen = 0
    indeps = {name: independent_places(recipe) for name, recipe, tables in fixtures()}
    for name, recipe, tables, node, column, scope, walk in all_walks():
        indep = indeps[name]
        accounted = list(walk.accounted)
        assert len(accounted) == len(set(accounted)), (name, node, column, scope)                       # each place once
        assert set(accounted) <= set(indep), (name, node, column, scope)
        assert walk.found + walk.grey == len(walk.lines) and walk.found == sum(1 for x in walk.lines if x.state == "tick")
        assert all(x.state == "grey" and x.reason is not None or x.state == "tick" and x.reason is None for x in walk.lines)      # a grey line always says why
        assert all(len(set(a.reach.tables_with_plot) & set(a.reach.tables_no_plot)) == 0 for a in walk.lines)
        for x in walk.lines:
            assert x.no_plot_reads == (not indep[x.place]["plots"]), (name, node, column, scope, x.place)      # a place no plot reads is a line, flagged as such (D-0451)
        for x in walk.lines:
            assert indep[x.place]["plots"] == set(x.reach.plots), (name, node, column, scope, x.place)      # the reach of a line is the plots below it, counted from the text
        seen += 1
    assert seen > 500


def test_I3_every_place_the_lineage_reaches_is_accounted_also_a_table_no_plot_reads_D_0451():
    """The accounting property, counted another way: from the graph, not from the walk. Every table (a place at its tier 1, tier 2 or tier 3) built from a table that holds
    the column, in the linked component of the start, is in `accounted` (a line, or a note when the column is gone); the places the walk does not account for are exactly
    those no such table reaches (a table that no join links to the lineage)."""
    seen = reached_no_plot = 0
    for name, recipe, tables in fixtures():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        for node, column in all_starts(recipe, tables):
            walk = index.walk(Start(node, column), levels=TIERS)
            begin = (node, *index.end(node)[1:], column)
            holders = {occ[0] for occ in index.component([begin])}
            reached = {index.place_of[n] for h in holders for n in [h] + index.forward(h) if not n.startswith("DS:")}
            assert set(walk.accounted) == reached, (name, node, column, sorted(set(walk.accounted) ^ reached))
            reached_no_plot += sum(1 for x in walk.lines if x.no_plot_reads)
            seen += 1
    assert seen > 100 and reached_no_plot > 20                                    # the property is run on many starts, and on lines of tables no plot reads


def test_I3_with_the_source_level_every_source_table_in_the_lineage_is_a_grey_line():
    seen = 0
    for name, recipe, tables in fixtures():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        sources = {f"DS:{n}" for n in graph.collections() if graph.node(f"T1:{n}").collection_kind == "schema"}
        for node, column in all_starts(recipe, tables):
            walk = index.walk(Start(node, column), levels=("source", "T1", "T2", "T3"))
            accounted = list(walk.accounted)
            assert len(accounted) == len(set(accounted)) and set(accounted) <= set(independent_places(recipe)) | sources, (name, node, column)
            assert not any(x.state == "tick" for x in walk.lines if x.place.startswith("DS:"))             # a source holds no list of steps: never ticked
            assert {x.place for x in walk.lines if x.place.startswith("DS:")} <= sources
            seen += 1
    assert seen > 100


def test_L087_the_places_of_the_reach_counted_from_the_recipe_text():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    indep = set(independent_places(recipe))
    assert set(index.walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED).accounted) == indep - {"T1:U"}         # every place but the unlinked source
    assert set(index.walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(LINEAGE).accounted) == indep - {"T1:E", "T3:Pe", "T1:U"}
    assert set(index.walk(Start("T3:Ps", "country"), levels=TIERS).within(LINEAGE).accounted) == {"T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2", "T3:Ps", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"}


def test_L069_walking_again_gives_the_same_and_a_recipe_rebuilt_from_a_copy_gives_the_same():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    first = index.walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED)
    assert index.walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED) == first
    again = F.tiers()
    assert run_again(*again) == first
    round_trip = copy.deepcopy(recipe)                                                                  # a step added and taken out again
    round_trip["joins"]["J1"]["tier2"]["steps"].append(F.keep("year", "gt", 1))
    round_trip["joins"]["J1"]["tier2"]["steps"].pop()
    assert run_again(round_trip, tables) == first


def run_again(recipe, tables):
    graph, plans = setup(recipe, tables)
    return LineageIndex(graph, plans).walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED)


class CountingEntries(dict):
    def __init__(self, entries):
        super().__init__(entries)
        self.reads: Dict[Tuple[str, int], int] = {}

    def __getitem__(self, key):
        self.reads[key] = self.reads.get(key, 0) + 1
        return super().__getitem__(key)


def test_L075_the_plan_is_read_once_per_place_and_never_again_by_the_walks():
    recipe, tables = F.tiers()
    graph = setup(recipe, tables)[0]
    entries = CountingEntries(O.replay(recipe, tables).plans._entries)       # type: ignore[attr-defined]
    index = LineageIndex(graph, PlanBook(entries))
    assert set(entries.reads) == {(n, k) for n in graph.nodes() for k in range(len(graph.node(n).steps) + 1)}
    assert max(entries.reads.values()) == 1
    before = dict(entries.reads)
    for node, column in list(all_starts(recipe, tables))[:60]:
        index.walk(Start(node, column), levels=TIERS).within(JOIN_LINKED)
    assert entries.reads == before                                                                       # the walks ask nothing: starting from every column adds no read


def test_L076_the_walk_reads_no_file_no_clock_no_random_and_changes_nothing(monkeypatch):
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    raw_before, plans_before = copy.deepcopy(recipe), copy.deepcopy(plans._entries)       # type: ignore[attr-defined]
    nodes_before = graph.nodes()
    index = LineageIndex(graph, plans)

    def refuse(*_args, **_kwargs):
        raise AssertionError("the walk must not read a file, the clock or a random number")

    for module, name in ((builtins, "open"), (os, "stat"), (time, "time"), (time, "perf_counter"), (random, "random")):
        monkeypatch.setattr(module, name, refuse)
    try:
        walk = index.walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED)
    finally:
        monkeypatch.undo()                    # also when the walk raises: pytest needs the file system to report the failure
    assert walk.lines and recipe == raw_before and plans._entries == plans_before and graph.nodes() == nodes_before    # type: ignore[attr-defined]


def test_L076_the_walk_modules_import_no_polars_no_app_no_shiny():
    code = ("import sys, utils.lineage_walk, utils.lineage_records, utils.plan_book, utils.step_effects;"
            "print(sorted(m for m in sys.modules if m.split('.')[0] in ('polars', 'app', 'shiny', 'transformer', 'ingestion', 'pandas')))")
    out = subprocess.run([sys.executable, "-c", code], env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"


SNIPPET = """
import lineage_fixtures as F
from lineage_support import TIERS, setup
from utils.lineage_walk import LineageIndex
from utils.lineage_records import GROUPS, Start
recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
graph, plans = setup(recipe, tables)
index = LineageIndex(graph, plans)
for n, c in (("T3:Pd", "sample_id"), ("T1:J1", "country"), ("DS:E", "gene")):
    for s in GROUPS:
        walk = index.walk(Start(n, c), levels=TIERS).within(s)
        print(repr(walk))
        print([(list(x.reach.tables_with_plot), list(x.reach.tables_no_plot), list(x.reach.plots)) for x in walk.lines + walk.gone])
"""


def raw_output():
    """What a caller can print or iterate in order, RAW (no sorting here): the repr of every walk and the reach of every place as lists."""
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    out = []
    for n, c in (("T3:Pd", "sample_id"), ("T1:J1", "country"), ("DS:E", "gene")):
        for s in GROUPS:
            walk = index.walk(Start(n, c), levels=TIERS).within(s)
            out.append(repr(walk))
            out.append(str([(list(x.reach.tables_with_plot), list(x.reach.tables_no_plot), list(x.reach.plots)) for x in walk.lines + walk.gone]))
    return "\n".join(out)


def test_I8_L077_the_same_input_gives_the_same_raw_output_in_other_processes_with_other_hash_seeds():
    here = raw_output()
    assert "frozenset" not in here                                                                           # no plain set in anything a caller can print
    for seed in ("0", "1", "2", "3", "77"):
        out = subprocess.run([sys.executable, "-c", SNIPPET], capture_output=True, text=True, check=True,
                             env={**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": os.pathsep.join(sys.path)})      # the tests directory is already on the path of this process
        assert out.stdout.strip() == here, seed


def test_L078_the_lines_follow_the_order_of_the_graph_and_the_order_of_columns_changes_nothing():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    walk = LineageIndex(graph, plans).walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED)
    order = {n: i for i, n in enumerate(graph.nodes())}
    assert [order[x.covers[0]] for x in walk.lines] == sorted(order[x.covers[0]] for x in walk.lines)                 # graph order, never alphabetical
    assert places(walk) != sorted(places(walk))
    assert sum(1 for x in walk.lines if x.is_start) == 1 and next(x for x in walk.lines if x.is_start).place == "T3:Pd"      # PROVISIONAL (Q11): marked, not moved first
    reordered = copy.deepcopy(recipe)
    reordered["data_schemas"]["S"]["tier1"]["steps"].append(F.select("val", "country", "sample_id"))                  # the same columns in another order
    again = LineageIndex(*setup(reordered, tables)).walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(JOIN_LINKED)
    assert places(again) == places(walk)


def test_the_walk_asks_nothing_of_a_plan_it_was_not_given():
    recipe, tables = F.chain()
    graph = setup(recipe, tables)[0]
    with pytest.raises(KeyError) as error:
        LineageIndex(graph, PlanBook.of({("DS:A", 0): [("a", "String")]}))
    assert "no entry" in str(error.value)                                                                          # absence is a bug of the caller, never a silent grey
    assert Plan.of([]).names == ()
