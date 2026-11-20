"""The lineage walk, structure and identity (LBFB step 1): which places a step on one column can be written at, what each reaches, where the
column is gone, and what stays grey. Cases are named with their number in `tmpAI/panel/lineage_tests/DESIGN.md` (L001 ...); a test that says
`PROVISIONAL` states what the walk does while the owner has not decided (the questions are in the report of the build).

The expected values are written by hand in each test (or counted from the recipe text by `lineage_support.independent_places`), and the oracle
(`lineage_oracle`, plain Polars) supplies the plan of every place and checks where the column really is (the marker check). Nothing here
trusts the walk to say what is true.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_walk.py -q
"""
import copy
import dataclasses

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import independent_places, places, run, setup, ticked

from utils.lineage_records import (
    CHANGE_NOT_FOLLOWED, NOTE_DECLARED_KEY_ONLY, NOTE_UNREAD_STEP_PASSED, PLAN_FAILED, READING_DISAGREES, SEVERAL_COLUMNS, STEP_NOT_READ, Reach,
    Start, GROUPS, JOIN_LINKED, LINEAGE, SAME_KEY)
from utils.lineage_walk import ColumnNotFound, LineageError, LineageIndex, StartPlanFailed
from utils.plan_book import PlanBook

ALL_SCOPES = list(GROUPS)


def line(walk, place):
    return next(x for x in walk.lines if x.place == place)


def reach(line_):
    return (line_.reach.n_tables, line_.reach.n_plots)


def marker_check(recipe, tables, marks, walk):
    """The independent check: the places whose table really holds the marked column (the oracle), against the lines of the walk."""
    holders = O.marker_holders(recipe, tables, marks)
    indep = independent_places(recipe)
    real = {p for p, info in indep.items() if info["last"] in holders and info["plots"]}
    assert set(places(walk)) == real, (sorted(set(places(walk)) ^ real))


# ----------------------------------------------------------------------------------------------------------------------------- A. structure

@pytest.mark.parametrize("scope", ALL_SCOPES)
def test_L001_equal_chain(scope):
    recipe, tables = F.chain()
    walk = run(recipe, tables, "T3:P1", "country", scope)
    assert places(walk) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and ticked(walk) == places(walk)    # no T2 line, no line for B (no `country`)
    assert [reach(x) for x in walk.lines] == [(2, 2), (1, 1), (0, 1), (0, 1)]
    assert line(walk, "T1:A").reach.tables_with_plot == {"T1:A", "T1:J"} and line(walk, "T1:A").reach.plots == {"P1", "P2"}
    assert all(not x.notes and x.reason is None and x.occurrences[0].name == "country" and x.occurrences[0].how == "unchanged" for x in walk.lines)
    assert line(walk, "T1:A").occurrences[0].sources[0].table == "A" and line(walk, "T1:A").covers == ("T1:A", "T2:A")     # an empty tier 2 is not a place
    assert [x.is_start for x in walk.lines] == [False, False, True, False]
    assert walk.gone == () and walk.unread == () and walk.outside == ()
    marker_check(recipe, tables, {"A": ["country"]}, walk)


def test_L001_the_key_is_on_both_ingredients():
    recipe, tables = F.chain()
    walk = run(recipe, tables, "T3:P1", "sample_id")
    assert places(walk) == ["T1:A", "T1:B", "T1:J", "T3:P1", "T3:P2"]
    assert reach(line(walk, "T1:B")) == (2, 1) and line(walk, "T1:B").reach.plots == {"P1"}
    marker_check(recipe, tables, {"A": ["sample_id"], "B": ["sample_id"]}, walk)


def test_L002_collapse_by_steps_counted_from_the_recipe():
    recipe, tables = F.tiers()
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    indep = {p for p, info in independent_places(recipe).items() if info["plots"]}
    assert set(places(walk)) == indep and len(walk.lines) == 13                       # the 13 lines of DESIGN L002, counted from the text
    assert {"T2:S", "T2:J1"} <= set(places(walk)) and not {"T2:E", "T2:M", "T2:J2"} & set(places(walk))     # a tier 2 with steps is a place, an empty one is not
    assert places(walk).count("T3:Pc") == 1 and line(walk, "T3:Pc").covers == ("T3:Pc",)    # a plot with its own steps is ONE line
    assert [x.place for x in walk.unread] == ["T1:JU"]                                 # a join no plot reads is not offered (D-0346), counted apart
    assert reach(line(walk, "T1:S")) == (5, 5) and reach(line(walk, "T1:J1")) == (2, 3) and reach(line(walk, "T2:S")) == (1, 1)
    assert [reach(line(walk, f"T3:{p}")) for p in ("Ps", "Pe", "Pa", "Pb", "Pc", "Pd")] == [(0, 1)] * 6


def test_L005_a_table_no_plot_reads_is_not_a_line_until_a_plot_reads_it():
    recipe, tables = F.tiers()
    assert "T1:JU" not in places(run(recipe, tables, "T3:Pd", "sample_id")) and "T1:U" not in places(run(recipe, tables, "T3:Pd", "sample_id"))
    with_plot = copy.deepcopy(recipe)
    with_plot["analysis_groups"]["g"]["plots"]["Pj"] = F.plot("JU")
    walk = run(with_plot, tables, "T3:Pd", "sample_id")
    assert "T1:JU" in places(walk) and "T3:Pj" in places(walk) and walk.unread == ()
    assert reach(line(walk, "T1:JU")) == (1, 1)
    # the reach of E counts JU either way: it is built from E (it is its own table, apart in `tables_no_plot` while no plot reads it)
    before = run(recipe, tables, "T3:Pd", "sample_id")
    assert line(before, "T1:E").reach.tables_no_plot == {"T1:JU"} and line(walk, "T1:E").reach.tables_no_plot == frozenset()


def test_L006_a_step_at_the_tier_2_of_a_shared_source_does_not_reach_the_joins():
    recipe, tables = F.tiers()
    walk = run(recipe, tables, "T3:Ps", "country")
    assert line(walk, "T2:S").reach.tables_with_plot == {"T2:S"} and line(walk, "T2:S").reach.plots == {"Ps"}      # the joins read the tier 1
    assert {"T1:J1", "T2:J1", "T1:J2"} <= line(walk, "T1:S").reach.tables_with_plot


def test_L006_E_with_an_empty_tier_2_PROVISIONAL_collapses_the_choice_away():
    # PROVISIONAL (question Q4): E has no tier 2 steps, so "the plots that read E directly, but not the joins" is not a place; D-0346 as written.
    recipe, tables = F.tiers()
    walk = run(recipe, tables, "T3:Pe", "sample_id")
    assert "T2:E" not in places(walk) and line(walk, "T1:E").reach.plots == {"Pe", "Pa", "Pb", "Pc"}


def test_L007_several_plots_on_one_table():
    recipe, tables = F.chain(extra_plots={f"P{n}": F.plot("J") for n in range(3, 8)})
    walk = run(recipe, tables, "T1:J", "country")
    assert reach(line(walk, "T1:J")) == (1, 6) and line(walk, "T1:J").reach.plots == {"P1", "P3", "P4", "P5", "P6", "P7"}
    assert [p for p in places(walk) if p.startswith("T3:")] == ["T3:P1", "T3:P2", "T3:P3", "T3:P4", "T3:P5", "T3:P6", "T3:P7"]


def test_L008_a_plot_with_its_own_steps_is_one_line():
    recipe, tables = F.tiers()
    for node in ("T3:Pa", "T3:Pc", "T1:J1"):
        walk = run(recipe, tables, node, "country")
        assert places(walk).count("T3:Pc") == 1 and line(walk, "T3:Pc").reach == Reach(frozenset(), frozenset(), frozenset({"Pc"}))
        assert not any(p.startswith("T2:Pc") for p in places(walk))
        assert {"T2:J1", "T3:Pa", "T3:Pb"} <= set(places(walk))


def test_L009_a_plot_that_reads_a_source_directly_has_its_own_line_besides_the_table():
    # also the edge case of one source and no join: the table line and "only this plot" are both listed, with the same plot
    recipe = F.recipe({"A": F.schema(["sample_id", "country"])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"])}
    walk = run(recipe, tables, "T3:P", "country")
    assert places(walk) == ["T1:A", "T3:P"] and reach(line(walk, "T1:A")) == (1, 1) and reach(line(walk, "T3:P")) == (0, 1)
    assert walk.gone == () and walk.unread == () and walk.outside == ()
    assert places(run(recipe, tables, "DS:A", "country")) == ["T1:A", "T3:P"]


def test_L010_a_source_read_by_two_joins_counts_each_once_and_a_step_at_one_does_not_touch_the_other():
    recipe, tables = F.tiers()
    line_s = line(run(recipe, tables, "T3:Ps", "country"), "T1:S")
    assert line_s.reach.tables_with_plot == {"T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2"} and line_s.reach.tables_no_plot == frozenset()
    after = O.with_audit_filter(recipe, "T1:J1", "country", "XX")
    assert O.changed_nodes(recipe, tables, after) & {"T1:J2", "T2:J2", "T3:Pd"} == set()


def test_L012_the_reach_does_not_depend_on_whether_the_column_survives():
    base, tables = F.tiers()
    dropped = copy.deepcopy(base)
    dropped["joins"]["J2"]["tier1"]["steps"].append(F.select("sample_id", "val", "year"))      # J2 does not keep `country`
    walk, original = run(dropped, tables, "T3:Ps", "country"), run(base, tables, "T3:Ps", "country")
    assert "T1:J2" not in places(walk) and "T3:Pd" not in places(walk)
    assert line(walk, "T1:S").reach == line(original, "T1:S").reach and "T1:J2" in line(walk, "T1:S").reach.tables_with_plot and "Pd" in line(walk, "T1:S").reach.plots
    assert {g.place for g in walk.gone} == {"T1:J2", "T3:Pd"}


def test_L013_the_reach_holds_sets_and_no_stored_count():
    assert [f.name for f in dataclasses.fields(Reach)] == ["tables_with_plot", "tables_no_plot", "plots"]       # a count kept apart could disagree with its set
    recipe, tables = F.chain()
    walk = run(recipe, tables, "T1:A", "sample_id")
    for x in walk.lines:
        assert x.reach.n_plots == len(x.reach.plots) and x.reach.n_tables == len(x.reach.tables_with_plot)
    assert line(walk, "T1:A").reach.plots == {"P1", "P2"}       # P1 is reached through A and through B, counted once


def test_L013_a_table_joined_with_itself_is_one_table_and_its_column_exists_twice_PROVISIONAL():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"])}, {"J": F.join(["A"], [F.join_step("A")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"])}
    walk = run(recipe, tables, "T1:A", "country")
    j = line(walk, "T1:J")
    assert [o.name for o in j.occurrences] == ["country", "country_right"]            # a list: the column is there twice
    assert j.state == "grey" and j.reason.code == SEVERAL_COLUMNS                      # PROVISIONAL (O8): which one a step names is not decided
    assert reach(line(walk, "T1:A")) == (2, 1)                                         # A and J: the self-join is one edge, A is not counted twice
    key = run(recipe, tables, "T1:A", "sample_id")
    assert line(key, "T1:J").state == "tick" and len(line(key, "T1:J").occurrences) == 1      # the key that both sides equate is one column


# ----------------------------------------------------------------------------------------------------------------------------- scopes

KEY_STARTS = ["DS:S", "DS:E", "DS:M", "T1:S", "T2:S", "T1:E", "T1:M", "T1:J1", "T2:J1", "T1:J2", "T3:Ps", "T3:Pe", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"]


def shape(walk):
    """What must not depend on the start: the places, their state, reach and column names. (`is_start` and the scope group are relative to the start.)"""
    return [(x.place, x.state, x.reach, tuple(o.name for o in x.occurrences)) for x in walk.lines], [g.place for g in walk.gone], [u.place for u in walk.unread]


@pytest.mark.parametrize("scope", [JOIN_LINKED, SAME_KEY])
def test_L014_same_places_from_every_start_of_one_key_when_joins_that_equate_it_are_followed(scope):
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    reference = shape(index.walk(Start("T3:Pd", "sample_id")).within(scope))
    for node in KEY_STARTS:
        assert shape(index.walk(Start(node, "sample_id")).within(scope)) == reference, node


def test_L014_PROVISIONAL_the_group_above_and_below_depends_on_where_the_user_looked_from_the_union_does_not():
    # D-0347 as written (back to the sources of the chosen place, then forward) gives other places from Pd than from Pe (question O1). The user chooses the
    # scope by ticking (owner, 2026-11-20): every candidate place is returned, each with its group, so the union is the same from both.
    recipe, tables = F.tiers()
    from_pd, from_pe = run(recipe, tables, "T3:Pd", "sample_id"), run(recipe, tables, "T3:Pe", "sample_id")
    assert shape(from_pd) == shape(from_pe)
    assert set(places(from_pd.within(LINEAGE))) != set(places(from_pe.within(LINEAGE)))
    assert "T1:E" not in places(from_pd.within(LINEAGE)) and "T3:Pe" not in places(from_pd.within(LINEAGE)) and "T1:E" in places(from_pe.within(LINEAGE))
    assert line(from_pd, "T1:E").scope_group == JOIN_LINKED and line(from_pe, "T1:E").scope_group == LINEAGE      # the group is relative to the start
    assert len(from_pd.within(LINEAGE).lines) == 11 and len(from_pd.lines) == 13


def test_the_groups_of_a_key_tell_above_and_below_linked_by_a_join_and_holding_the_key_with_no_join():
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    groups = {x.place: x.scope_group for x in walk.lines}
    assert groups["T1:S"] == groups["T3:Pd"] == groups["T1:M"] == LINEAGE
    assert groups["T1:E"] == groups["T3:Pe"] == JOIN_LINKED
    assert groups["T1:U"] == groups["T3:Pu"] == SAME_KEY
    assert [u.place for u in walk.unread] == ["T1:JU"] and walk.unread[0].scope_group == LINEAGE      # JU is built from M, which the chosen place reads
    assert [x.place for x in walk.within(JOIN_LINKED).lines] == [p for p in places(walk) if groups[p] != SAME_KEY]
    assert all(x.refusal is None for x in walk.lines)                       # the record can carry "refused here, with the reason"; nothing sets it yet (the drop step)


@pytest.mark.parametrize("scope", ALL_SCOPES)
def test_L014_a_column_no_join_equates_gives_the_same_places_from_every_start_under_every_scope(scope):
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    reference = shape(index.walk(Start("T3:Ps", "country")).within(scope))
    for node in ("DS:S", "T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"):
        assert shape(index.walk(Start(node, "country")).within(scope)) == reference, node
    assert places(index.walk(Start("T3:Ps", "country")).within(scope)) == ["T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2", "T3:Ps", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"]


def holders_after(recipe, tables, walk, value):
    """Remove `value` of the key at every line of the walk (an audit filter at the end of each place), replay, and list the nodes whose table still holds it."""
    changed = copy.deepcopy(recipe)
    for x in walk.lines:
        changed = O.with_audit_filter(changed, x.place, x.occurrences[0].name, value)
    result = O.replay(changed, tables)
    return {n for (n, _k) in result.frames if not n.startswith("DS:") and result.end(n) is not None
            and any(result.end(n)[c].dtype.is_(O.pl.String) and (result.end(n)[c] == value).any() for c in result.end(n).columns)}


def forward_of(graph, tables_listed):
    out = set()
    for table in tables_listed:
        out |= {f"T1:{table}"} | set(graph.lineage_forward(f"T1:{table}"))
    return out


def node_place(recipe, node):
    indep = independent_places(recipe)
    return f"T1:{node[3:]}" if node.startswith("T2:") and node not in indep else node


@pytest.mark.parametrize("scope", ALL_SCOPES)
def test_L052_remove_one_sample_in_the_places_ticked_what_is_left_is_offered_in_another_group(scope):
    # "remove sample S3 from all tables": the user ticks the places of a scope; after a filter at every ticked line, every table that still holds S3 is a place
    # that the walk offers in a wider group or as a place no plot reads (I4). What each scope really leaves, written by hand (the nodes that still hold S3):
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    full = run(recipe, tables, "T3:Pd", "sample_id")
    walk = full.within(scope)
    left = holders_after(recipe, tables, walk, "S3")
    e_chain, u_chain = {"T1:E", "T2:E", "T3:Pe", "T1:JU", "T2:JU"}, {"T1:U", "T2:U", "T3:Pu"}
    assert left == {LINEAGE: e_chain | u_chain, JOIN_LINKED: u_chain, SAME_KEY: set()}[scope]
    offered_wider = {x.place for x in full.lines if x not in walk.lines} | {u.place for u in full.unread}
    assert {node_place(recipe, n) for n in left} <= offered_wider                  # nothing is left that the walk did not offer
    assert holders_after(recipe, tables, full, "S3") == set()                      # all the groups ticked: S3 is in no table


def test_L052_a_declared_key_alone_reaches_a_table_no_join_links_PROVISIONAL():
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    walk = run(recipe, tables, "T3:Pd", "sample_id", SAME_KEY)
    assert {"T1:U", "T3:Pu"} <= set(places(walk)) and line(walk, "T1:U").scope_group == "same_key"
    assert [n.code for n in line(walk, "T1:U").notes] == [NOTE_DECLARED_KEY_ONLY] and line(walk, "T1:U").state == "tick"
    assert "never the column name alone" in walk.key_basis                                                    # the record says what it used
    # the same table without a declared key is only listed, never a line
    undeclared = run(*F.tiers(u_declares_key=False, u_plot=True), "T3:Pd", "sample_id", SAME_KEY)
    assert "T1:U" not in places(undeclared) and [(o.table, o.why) for o in undeclared.outside] == [("U", "same_name_not_declared")]


def test_L053_a_table_without_the_key_is_not_a_line_and_is_not_changed():
    recipe, tables = F.chain()
    recipe["data_schemas"]["D"] = F.schema(["code", "desc"])
    recipe["analysis_groups"]["g"]["plots"]["PD"] = F.plot("D")
    tables["D"] = F.table(code=["x", "y"], desc=["p", "q"])
    walk = run(recipe, tables, "T3:P1", "sample_id")
    assert places(walk) == ["T1:A", "T1:B", "T1:J", "T3:P1", "T3:P2"] and walk.outside == ()          # no line for D: it has no such column
    changed = copy.deepcopy(recipe)
    for x in walk.lines:
        changed = O.with_audit_filter(changed, x.place, "sample_id", "S3")
    assert O.changed_nodes(recipe, tables, changed) & {"T1:D", "T2:D", "T3:PD"} == set()


# ----------------------------------------------------------------------------------------------------------------------------- B. identity

def test_L015_a_rename_on_one_path_is_not_followed_yet_and_the_other_table_is_never_offered():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], [F.rename(country="origin")]), "B": F.schema(["sample_id", "country"])},
                      {}, {"Pa": F.plot("A"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(sample_id=["S1"], country=["SE"])}
    here = run(recipe, tables, "T3:Pa", "origin")
    assert places(here) == ["T1:A", "T3:Pa"] and ticked(here) == places(here)                      # B has a `country` of its own: not this column
    assert line(here, "T1:A").occurrences[0].how == "renamed" and line(here, "T1:A").occurrences[0].sources[0].name == "country"
    hop = line(here, "T1:A").occurrences[0].steps[0]
    assert (hop.step.node, hop.step.step, hop.step.action, hop.name_before, hop.name_after) == ("T1:A", 1, "polars_rename", "country", "origin")
    other = run(recipe, tables, "T3:Pb", "country")
    assert places(other) == ["T1:B", "T3:Pb"]                                                      # the plan of A's source also has `country`: still not offered
    from_source = run(recipe, tables, "DS:A", "country")
    assert line(from_source, "T1:A").state == "grey" and line(from_source, "T1:A").reason.code == CHANGE_NOT_FOLLOWED      # PROVISIONAL (step 2 not built)
    assert line(from_source, "T1:A").reason.get("change") == "rename" and line(from_source, "T1:A").occurrences[0].name == "origin"


def test_L016_same_name_and_same_type_is_not_the_same_column():
    recipe = F.recipe({"A": F.schema(["sample_id", "a_year"], [F.rename(a_year="year")]), "B": F.schema(["sample_id", "b_year"], [F.rename(b_year="year")])},
                      {}, {"Pa": F.plot("A"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"], a_year=[2022]), "B": F.table(sample_id=["S1"], b_year=[2022])}
    assert places(run(recipe, tables, "T3:Pa", "year")) == ["T1:A", "T3:Pa"] and places(run(recipe, tables, "T3:Pb", "year")) == ["T1:B", "T3:Pb"]


def test_L017_a_clash_in_a_join_the_right_column_carries_the_suffix_and_is_not_followed_yet():
    recipe = F.recipe({"A": F.schema(["sample_id", "val"]), "B": F.schema(["sample_id", "val"])}, {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], val=[1.0]), "B": F.table(sample_id=["S1"], val=[2.0])}
    left = run(recipe, tables, "T1:J", "val")
    assert places(left) == ["T1:A", "T1:J", "T3:P"] and ticked(left) == places(left)              # A's val; B's val is another column
    right = run(recipe, tables, "T1:J", "val_right")
    assert places(right) == ["T1:B", "T1:J", "T3:P"] and line(right, "T1:B").state == "grey" and line(right, "T1:B").reason.get("change") == "suffix"
    hop = line(right, "T1:J").occurrences[0].steps[0]
    assert (hop.join_how, hop.join_side, hop.name_before, hop.name_after) == ("left", "right", "val", "val_right")


def test_L019_a_swap_by_rename_is_never_ticked():
    recipe = F.recipe({"A": F.schema(["a", "b"], [F.rename(a="b", b="a")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(a=[1], b=[2])}
    walk = run(recipe, tables, "DS:A", "a")                                                       # the plan shows no change when the types are equal
    assert [(x.place, x.state, x.occurrences[0].name) for x in walk.lines] == [("T1:A", "grey", "b"), ("T3:P", "grey", "b")]
    assert line(walk, "T1:A").reason.code == CHANGE_NOT_FOLLOWED


def test_L021_a_key_under_another_name_is_listed_and_grey_not_dropped():
    recipe = F.recipe({"A": F.schema(["sample_id"], keys=["sample_id"]), "B": F.schema(["isolate", "lab"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"))])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"]), "B": F.table(isolate=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T1:J", "sample_id")
    assert places(walk) == ["T1:A", "T1:B", "T1:J", "T3:P", "T3:Pb"]
    assert line(walk, "T1:B").state == "grey" and line(walk, "T1:B").reason.get("change") == "key_other_name" and line(walk, "T1:B").occurrences[0].name == "isolate"
    assert line(walk, "T1:A").state == "tick" and line(walk, "T1:J").state == "tick"


def test_L022_a_full_join_is_not_read_and_what_depends_on_it_is_grey_with_the_reason_PROVISIONAL():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"]), "B": F.schema(["sample_id", "lab"])}, {"J": F.join(["A", "B"], [F.join_step("B", how="full")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(sample_id=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T1:A", "country")
    assert line(walk, "T1:J").state == "tick"                       # `country` passes the unread join by the plan alone (name and type unchanged)
    assert [n.code for n in line(walk, "T1:J").notes] == [NOTE_UNREAD_STEP_PASSED]
    keyed = run(recipe, tables, "T1:B", "lab")
    assert line(keyed, "T1:J").state == "grey" and line(keyed, "T1:J").reason.code == STEP_NOT_READ and "full" in line(keyed, "T1:J").reason.get("why")


def test_L026_a_column_dropped_and_created_again_with_the_same_name_is_a_new_column():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], [F.drop("country"), F.with_columns(country="pl.lit('X')")]), "B": F.schema(["sample_id", "country"])},
                      {}, {"Pa": F.plot("A"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(sample_id=["S1"], country=["SE"])}
    new = run(recipe, tables, "T3:Pa", "country")
    assert places(new) == ["T1:A", "T3:Pa"] and line(new, "T1:A").occurrences[0].how == "re_created"       # per-step plans see the gap: it starts again at step 2
    assert line(new, "T1:A").occurrences[0].sources == ()      # it comes from no source column
    old = run(recipe, tables, "T3:Pb", "country")
    assert places(old) == ["T1:B", "T3:Pb"]                         # A has a `country` of the same type in its plan: not this column
    from_source = run(recipe, tables, "DS:A", "country")
    assert from_source.lines == () and {g.place for g in from_source.gone} == {"T1:A", "T3:Pa"}      # the source column ends at the drop (step 1)
    assert {g.removed_by.step for g in from_source.gone} == {1}
    fresh = F.recipe({"A": F.schema(["sample_id", "year"], [F.with_columns(era="pl.col('year') > 2022")])}, {}, {"P": F.plot("A")})
    created = run(fresh, {"A": F.table(sample_id=["S1"], year=[2023])}, "T3:P", "era")
    assert places(created) == ["T1:A", "T3:P"] and line(created, "T1:A").occurrences[0].how == "created"      # a column made here, never in the file


def test_L027_a_column_dropped_in_the_middle_of_a_tier_is_not_a_place_for_a_step():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.select("sample_id", "year", "val")])
    walk = run(recipe, tables, "DS:A", "country")
    assert walk.lines == () and [g.place for g in walk.gone] == ["T1:A", "T1:J", "T3:P1", "T3:P2"]
    assert all((g.removed_by.node, g.removed_by.step, g.removed_by.action) == ("T1:A", 2, "polars_select") for g in walk.gone)
    assert walk.gone[0].removed_by.step_path == "data_schemas.A.tier1.steps[2]"


def test_L024_the_column_dropped_on_one_path_is_a_note_under_the_lines_that_reach_it():
    recipe, tables = F.tiers()
    recipe["joins"]["J2"]["tier1"]["steps"].append(F.select("sample_id", "val", "year"))
    walk = run(recipe, tables, "T3:Ps", "country")
    assert [(g.place, g.reached_by, g.removed_by.node, g.removed_by.step, g.table_changes) for g in walk.gone] == [
        ("T1:J2", ("T1:S",), "T1:J2", 2, True), ("T3:Pd", ("T1:S",), "T1:J2", 2, True)]      # in the reach of T1:S, the rows change although the column is gone
    drop = run(recipe, tables, "T3:Ps", "country", kind="drop")
    assert [g.table_changes for g in drop.gone] == [False, False] and drop.step_kind == "drop"      # a drop leaves a table that lacks the column as it was
    assert places(drop) == places(walk)                                                              # the lines are the same for a filter and a drop


# ----------------------------------------------------------------------------------------------------------------------------- unread steps

def test_L034_a_cast_changes_the_type_of_the_column_it_names_and_that_is_not_followed_yet():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.cast(["year"], "String")])
    walk = run(recipe, tables, "DS:A", "year")                                       # from the source column, the cast is on the path
    assert [(x.place, x.state) for x in walk.lines] == [("T1:A", "grey"), ("T1:J", "grey"), ("T3:P1", "grey"), ("T3:P2", "grey")]
    reason = line(walk, "T1:A").reason
    assert (reason.code, reason.get("node"), reason.get("step"), reason.get("change")) == (CHANGE_NOT_FOLLOWED, "T1:A", 2, "cast")
    occurrence = line(walk, "T1:A").occurrences[0]
    assert (occurrence.how, occurrence.type, occurrence.steps[0].type_before, occurrence.steps[0].type_after) == ("cast", "String", "Int64", "String")
    after = run(recipe, tables, "T3:P2", "year")                                      # from after the cast it is the same column everywhere downstream
    assert places(after) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and ticked(after) == places(after)
    other = run(recipe, tables, "DS:A", "country")                                    # a column the cast does not name is untouched: no grey, no note
    assert ticked(other) == places(other) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and all(x.notes == () for x in other.lines)


def test_L034_a_step_the_walk_may_not_read_is_grey_unless_the_plan_shows_the_column_unchanged():
    # unpivot is not in the readings: where it removes the column the walk cannot say whether it went on under another name
    recipe = F.recipe({"A": F.schema(["sample_id", "a1", "a2"], [F.unpivot(["a1", "a2"], ["sample_id"])])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1"], a1=[1], a2=[2])}
    walk = run(recipe, tables, "DS:A", "a1")
    assert walk.gone == () and [(x.place, x.state) for x in walk.lines] == [("T1:A", "grey"), ("T3:P", "grey")] and all(x.occurrences == () for x in walk.lines)
    assert (line(walk, "T1:A").reason.code, line(walk, "T1:A").reason.get("action")) == (STEP_NOT_READ, "polars_unpivot")
    key = run(recipe, tables, "DS:A", "sample_id")                                    # the index column passes: name and type unchanged by the plan, with the note
    assert ticked(key) == places(key) == ["T1:A", "T3:P"] and key.lines[0].notes[0].code == NOTE_UNREAD_STEP_PASSED


def test_L030_PROVISIONAL_a_compute_step_names_the_columns_it_writes_the_others_pass_untouched():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.with_columns(year="pl.col('year') + 1")])
    written = run(recipe, tables, "DS:A", "year")                                     # the step writes `year`: the same column, recomputed; not followed yet (the note is a later step)
    assert [(x.place, x.state) for x in written.lines] == [("T1:A", "grey"), ("T1:J", "grey"), ("T3:P1", "grey"), ("T3:P2", "grey")]
    assert (line(written, "T1:A").reason.code, line(written, "T1:A").reason.get("change")) == (CHANGE_NOT_FOLLOWED, "recompute")
    assert line(written, "T1:A").occurrences[0].how == "recomputed"
    other = run(recipe, tables, "DS:A", "country")                                    # not named by the step: untouched, reading and plan agree: no grey, no note
    assert ticked(other) == places(other) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and all(x.notes == () for x in other.lines)
    assert ticked(run(recipe, tables, "T3:P2", "year")) == ["T1:A", "T1:J", "T3:P1", "T3:P2"]      # a start after the step crosses nothing


def test_L030_a_step_the_walk_may_not_read_passes_a_column_the_plan_shows_unchanged_with_a_note():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    walk = run(recipe, tables, "DS:A", "year")
    assert ticked(walk) == places(walk) == ["T1:A", "T1:J", "T3:P1", "T3:P2"]         # name and type unchanged across the step: the plan proves nothing more
    note = line(walk, "T1:A").notes[0]
    assert (note.code, dict(note.params)["action"], dict(note.params)["step"]) == (NOTE_UNREAD_STEP_PASSED, "polars_fill_null", 2)      # the values may have changed
    assert run(recipe, tables, "T3:P2", "year").lines[-1].notes == ()


def test_L031_a_group_by_names_its_group_columns_and_aggregates_so_the_walk_reads_what_it_removes():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.group_by(["sample_id", "year"], val="pl.col('val').mean()")])
    gone = run(recipe, tables, "DS:A", "country")                                     # not a group column and not an aggregate: the reading and the plan agree it is gone
    assert gone.lines == () and [g.place for g in gone.gone] == ["T1:A", "T1:J", "T3:P1", "T3:P2"]
    assert all((g.removed_by.node, g.removed_by.step, g.removed_by.action) == ("T1:A", 2, "polars_group_by") for g in gone.gone)
    key = run(recipe, tables, "DS:A", "year")                                         # a group column passes untouched
    assert ticked(key) == places(key) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and all(x.notes == () for x in key.lines)
    aggregate = run(recipe, tables, "DS:A", "val")                                    # an aggregate under the same name: the same column, changed (not followed yet)
    assert line(aggregate, "T1:A").state == "grey" and line(aggregate, "T1:A").reason.get("change") == "aggregate"
    assert line(aggregate, "T1:A").occurrences[0].how == "recomputed"


def test_L018_a_column_renamed_in_one_tier_and_back_in_a_later_one_is_one_column_named_as_in_each_table():
    # owner 2026-11-20: ONE column, named as in each table. The rename is not followed yet (step 2), but the record already holds the name of each place
    # and the one source; the line of each tier says its own name.
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], [F.rename(country="origin")], [F.rename(origin="country")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"])}
    walk = run(recipe, tables, "T3:P", "country")
    assert places(walk) == ["T1:A", "T2:A", "T3:P"]
    assert [(x.place, x.occurrences[0].name) for x in walk.lines] == [("T1:A", "origin"), ("T2:A", "country"), ("T3:P", "country")]
    assert {(s.table, s.name) for x in walk.lines for o in x.occurrences for s in o.sources} == {("A", "country")}        # one source column
    assert line(walk, "T2:A").state == "tick" and line(walk, "T1:A").state == "grey"           # PROVISIONAL (step 2): the rename of tier 2 is on the way to T1, not followed yet
    assert (line(walk, "T1:A").reason.get("node"), line(walk, "T1:A").reason.get("change")) == ("T2:A", "rename")


def test_L034_a_reading_that_the_plan_contradicts_is_grey_with_the_problem():
    recipe = F.recipe({"A": F.schema(["a", "b"], [F.rename(a="c")])}, {}, {"P": F.plot("A")})
    both = [("a", "Int64"), ("b", "Int64")]
    graph = setup(recipe, {"A": F.table(a=[1], b=[2])})[0]
    plans = PlanBook.of({("DS:A", 0): both, ("T1:A", 0): both, ("T1:A", 1): both, ("T2:A", 0): both, ("T3:P", 0): both})      # the rename did not happen, says the plan
    walk = LineageIndex(graph, plans).walk(Start("DS:A", "a")).within(JOIN_LINKED)
    assert [(x.place, x.state) for x in walk.lines] == [("T1:A", "grey"), ("T3:P", "grey")]
    assert line(walk, "T1:A").reason.code == READING_DISAGREES and "c" in line(walk, "T1:A").reason.get("problem")


# ----------------------------------------------------------------------------------------------------------------------------- failure

def failing(recipe, tables, node, k, sentence="the engine said no"):
    """The plan book of the recipe with a failure from (node, k) on and for every place below it."""
    graph, plans = setup(recipe, tables)
    entries = {}
    below = {node} | set(graph.lineage_forward(node))
    for n in graph.nodes():
        for j in range(len(graph.node(n).steps) + 1):
            entries[(n, j)] = sentence if n in below and (n != node or j >= k) else plans.get(n, j)
    return graph, PlanBook.of(entries), below


def test_L072_one_place_cannot_answer_and_every_other_line_is_as_without_the_failure():
    recipe, tables = F.chain()
    graph, plans = setup(recipe, tables)
    base = LineageIndex(graph, plans).walk(Start("DS:A", "country")).within(JOIN_LINKED)
    assert base.found == 4
    for node in graph.nodes():
        if node.startswith("DS:"):
            continue
        for k in range(len(graph.node(node).steps) + 1):
            g, broken, below = failing(recipe, tables, node, k)
            walk = LineageIndex(g, broken).walk(Start("DS:A", "country")).within(JOIN_LINKED)      # never an exception, never an empty list
            assert set(walk.accounted) == set(base.accounted) and len(walk.lines) == len(base.lines)      # nothing is lost
            for x in base.lines:
                got = line(walk, x.place)
                if x.covers[0] in below:
                    assert got.state == "grey" and got.reason.code == PLAN_FAILED and got.reason.get("sentence") == "the engine said no", (node, k, x.place)
                else:
                    assert got == x, (node, k, x.place)


def test_L070_a_step_that_fails_in_the_engine_greys_its_table_and_what_is_below_only():
    recipe, tables = F.chain(b_steps=[F.drop("nope")])                                 # B's tier 1 names a column that does not exist
    walk = run(recipe, tables, "T1:A", "country")
    assert (line(walk, "T1:A").state, line(walk, "T3:P2").state) == ("tick", "tick")
    for place in ("T1:J", "T3:P1"):
        assert line(walk, place).state == "grey" and line(walk, place).reason.code == PLAN_FAILED
        assert "nope" in line(walk, place).reason.get("sentence")                       # the engine's own sentence, carried as data
    assert walk.found == 2 and walk.grey == 2 and len(walk.lines) == 4


def test_L023_a_clash_the_engine_cannot_build_is_grey_with_its_sentence():
    recipe = F.recipe({"A": F.schema(["sample_id", "val"]), "B": F.schema(["sample_id", "val", "val_right"])}, {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], val=[1.0]), "B": F.table(sample_id=["S1"], val=[2.0], val_right=[3.0])}
    walk = run(recipe, tables, "T1:A", "val")
    assert line(walk, "T1:A").state == "tick" and line(walk, "T1:J").state == "grey" and line(walk, "T1:J").reason.code == PLAN_FAILED
    assert line(walk, "T1:J").reason.get("sentence")


# ----------------------------------------------------------------------------------------------------------------------------- plain errors

def test_a_column_that_exists_nowhere_is_a_plain_error_and_so_is_every_wrong_call():
    recipe, tables = F.chain()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    with pytest.raises(ColumnNotFound) as error:
        index.walk(Start("T3:P1", "nope")).within(LINEAGE)
    assert "nope" in str(error.value) and "T3:P1" in str(error.value)
    with pytest.raises(ColumnNotFound):
        index.walk(Start("T3:P1", "COUNTRY")).within(LINEAGE)                       # names are exact
    with pytest.raises(LineageError):
        index.walk(Start("T3:Nope", "country")).within(LINEAGE)
    with pytest.raises(LineageError):
        index.walk(Start("T3:P1", "country"), kind="rename").within(LINEAGE)
    with pytest.raises(TypeError):
        index.walk(Start("T3:P1", "country"), scope="lineage")                           # no scope is applied: the user ticks (owner, 2026-11-20)
    g, failed, _ = failing(recipe, tables, "T1:A", 0)
    with pytest.raises(StartPlanFailed):
        LineageIndex(g, failed).walk(Start("T3:P2", "country")).within(LINEAGE)
