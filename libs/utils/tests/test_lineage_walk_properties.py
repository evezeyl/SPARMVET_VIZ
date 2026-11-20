"""The lineage walk, properties that must hold for every start (LBFB step 1): nothing is lost, every line can be written, the same input gives the
same output, the walk reads nothing and changes nothing. Invariants I1, I3 and I8 of the logic review, and the cases L069, L075 to L078 and L087 of
`tmpAI/panel/lineage_tests/DESIGN.md`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_walk_properties.py -q
"""
import builtins
import copy
import dataclasses
import json
import os
import random
import subprocess
import sys
import time
from typing import Any, Dict, Iterator, Tuple

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import independent_places, places, setup

from utils import audit_copy
from utils.lineage_records import GROUPS, JOIN_LINKED, LINEAGE, SAME_KEY, Start, Walk
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
                yield name, recipe, tables, node, column, scope, index.walk(Start(node, column)).within(scope)


def test_I1_every_line_can_be_written_and_names_a_column_the_plan_has_at_the_end_of_the_place():
    seen = 0
    replays = {name: O.replay(recipe, tables) for name, recipe, tables in fixtures()}
    for name, recipe, tables, node, column, scope, walk in all_walks():
        replay = replays[name]
        for x in walk.lines:
            copy_ = audit_copy.audit_recipe_of(recipe)
            audit_copy.add_step(copy_, x.place, F.keep(x.occurrences[0].name if x.occurrences else column, "ne", "S3"), "audit_1a2b3c4d_1")      # add_step accepts the place
            last = x.covers[0]
            end = replay.end(last)
            for occurrence in x.occurrences:
                assert end is not None and occurrence.name in end.columns and occurrence.type == str(end.schema[occurrence.name]), (name, node, column, x.place)
            seen += 1
    assert seen > 500                                                                                  # the property is run on every column of every table of every fixture


def test_I3_nothing_is_lost_every_place_of_the_reach_is_a_line_a_note_or_counted_apart():
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
        for u in walk.unread:
            assert not indep[u.place]["plots"]                                                          # a place no plot reads
        for x in walk.lines:
            assert indep[x.place]["plots"] == set(x.reach.plots), (name, node, column, scope, x.place)      # the reach of a line is the plots below it, counted from the text
        seen += 1
    assert seen > 500


def test_L087_the_places_of_the_reach_counted_from_the_recipe_text():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    indep = set(independent_places(recipe))
    assert set(index.walk(Start("T3:Pd", "sample_id")).within(JOIN_LINKED).accounted) == indep - {"T1:U"}         # every place but the unlinked source
    assert set(index.walk(Start("T3:Pd", "sample_id")).within(LINEAGE).accounted) == indep - {"T1:E", "T3:Pe", "T1:U"}
    assert set(index.walk(Start("T3:Ps", "country")).within(LINEAGE).accounted) == {"T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2", "T3:Ps", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"}
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    graph, plans = setup(recipe, tables)
    assert set(LineageIndex(graph, plans).walk(Start("T3:Pd", "sample_id")).within(SAME_KEY).accounted) == set(independent_places(recipe))
    assert "T1:U" in places(LineageIndex(graph, plans).walk(Start("T3:Pd", "sample_id")).within(SAME_KEY))


def test_L069_walking_again_gives_the_same_and_a_recipe_rebuilt_from_a_copy_gives_the_same():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    first = index.walk(Start("T3:Pd", "sample_id")).within(JOIN_LINKED)
    assert index.walk(Start("T3:Pd", "sample_id")).within(JOIN_LINKED) == first
    again = F.tiers()
    assert run_again(*again) == first
    round_trip = copy.deepcopy(recipe)                                                                  # a step added and taken out again
    round_trip["joins"]["J1"]["tier2"]["steps"].append(F.keep("year", "gt", 1))
    round_trip["joins"]["J1"]["tier2"]["steps"].pop()
    assert run_again(round_trip, tables) == first


def run_again(recipe, tables):
    graph, plans = setup(recipe, tables)
    return LineageIndex(graph, plans).walk(Start("T3:Pd", "sample_id")).within(JOIN_LINKED)


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
        index.walk(Start(node, column)).within(SAME_KEY)
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
    walk = index.walk(Start("T3:Pd", "sample_id")).within(SAME_KEY)
    monkeypatch.undo()
    assert walk.lines and recipe == raw_before and plans._entries == plans_before and graph.nodes() == nodes_before    # type: ignore[attr-defined]


def test_L076_the_walk_modules_import_no_polars_no_app_no_shiny():
    code = ("import sys, utils.lineage_walk, utils.lineage_records, utils.plan_book, utils.step_effects;"
            "print(sorted(m for m in sys.modules if m.split('.')[0] in ('polars', 'app', 'shiny', 'transformer', 'ingestion', 'pandas')))")
    out = subprocess.run([sys.executable, "-c", code], env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"


def plain(value: Any) -> Any:
    """A walk as JSON data: sets become sorted lists, so that nothing depends on the order of a set."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, (set, frozenset)):
        return sorted(plain(v) for v in value)
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value.value if hasattr(value, "value") and not isinstance(value, (str, int, float)) else value


SNIPPET = """
import json, sys
sys.path.insert(0, {tests!r})
import lineage_fixtures as F
from lineage_support import setup
from test_lineage_walk_properties import plain
from utils.lineage_walk import LineageIndex
from utils.lineage_records import GROUPS, Start
recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
graph, plans = setup(recipe, tables)
index = LineageIndex(graph, plans)
out = [plain(index.walk(Start(n, c)).within(s)) for n, c in (("T3:Pd", "sample_id"), ("T1:J1", "country"), ("DS:E", "gene")) for s in GROUPS]
print(json.dumps(out, sort_keys=True))
"""


def test_I8_L077_the_same_input_gives_the_same_output_in_other_processes_with_other_hash_seeds():
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    here = json.dumps([plain(index.walk(Start(n, c)).within(s)) for n, c in (("T3:Pd", "sample_id"), ("T1:J1", "country"), ("DS:E", "gene")) for s in GROUPS], sort_keys=True)
    for seed in ("0", "1", "2", "3"):
        out = subprocess.run([sys.executable, "-c", SNIPPET.format(tests=os.path.dirname(__file__))], capture_output=True, text=True, check=True,
                             env={**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": os.pathsep.join(sys.path)})
        assert out.stdout.strip() == here, seed


def test_L078_the_lines_follow_the_order_of_the_graph_and_the_order_of_columns_changes_nothing():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    walk = LineageIndex(graph, plans).walk(Start("T3:Pd", "sample_id")).within(JOIN_LINKED)
    order = {n: i for i, n in enumerate(graph.nodes())}
    assert [order[x.covers[0]] for x in walk.lines] == sorted(order[x.covers[0]] for x in walk.lines)                 # graph order, never alphabetical
    assert places(walk) != sorted(places(walk))
    assert sum(1 for x in walk.lines if x.is_start) == 1 and next(x for x in walk.lines if x.is_start).place == "T3:Pd"      # PROVISIONAL (Q11): marked, not moved first
    reordered = copy.deepcopy(recipe)
    reordered["data_schemas"]["S"]["tier1"]["steps"].append(F.select("val", "country", "sample_id"))                  # the same columns in another order
    again = LineageIndex(*setup(reordered, tables)).walk(Start("T3:Pd", "sample_id")).within(JOIN_LINKED)
    assert places(again) == places(walk)


def test_the_walk_asks_nothing_of_a_plan_it_was_not_given():
    recipe, tables = F.chain()
    graph = setup(recipe, tables)[0]
    with pytest.raises(KeyError) as error:
        LineageIndex(graph, PlanBook.of({("DS:A", 0): [("a", "String")]}))
    assert "no entry" in str(error.value)                                                                          # absence is a bug of the caller, never a silent grey
    assert Plan.of([]).names == ()
