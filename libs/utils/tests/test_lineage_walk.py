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
from lineage_support import TIERS, independent_places, places, run, setup, ticked

from utils.lineage_records import (
    NOTE_AGGREGATED, NOTE_ANOTHER_TYPE, NOTE_ONE_ROW_PER_GROUP, NOTE_RECOMPUTED, NOTE_UNREAD_STEP_PASSED, PLAN_FAILED, READING_DISAGREES, SEVERAL_COLUMNS,
    STEP_NOT_READ, Reach, Start, GROUPS, JOIN_LINKED, LINEAGE, NO_STEP_LIST)
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
    assert walk.gone == () and walk.outside == ()
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
    indep = set(independent_places(recipe)) - {"T1:U"}                                  # U is linked to nothing: the walk does not reach it (D-0415 untouched)
    assert set(places(walk)) == indep and len(walk.lines) == 14                       # the 13 lines of DESIGN L002 plus the join no plot reads (D-0451)
    assert {"T2:S", "T2:J1"} <= set(places(walk)) and not {"T2:E", "T2:M", "T2:J2"} & set(places(walk))     # a tier 2 with steps is a place, an empty one is not
    assert places(walk).count("T3:Pc") == 1 and line(walk, "T3:Pc").covers == ("T3:Pc",)    # a plot with its own steps is ONE line
    # "tick" is the walk's proof that it is the same column, not a default tick of the dialog (not decided: ledger D-0451).
    assert "T1:JU" in places(walk) and line(walk, "T1:JU").state == "tick"            # a join no plot reads is a line, like the others (D-0451, D-0346 changed in this part)
    assert reach(line(walk, "T1:S")) == (5, 5) and reach(line(walk, "T1:J1")) == (2, 3) and reach(line(walk, "T2:S")) == (1, 1)
    assert [reach(line(walk, f"T3:{p}")) for p in ("Ps", "Pe", "Pa", "Pb", "Pc", "Pd")] == [(0, 1)] * 6


def test_L005_a_table_no_plot_reads_that_the_walk_reaches_is_a_line_D_0451():
    recipe, tables = F.tiers()
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    ju = line(walk, "T1:JU")
    assert ju.covers == ("T1:JU", "T2:JU") and ju.tier == "T1" and ju.kind == "table"            # tier 1 of the table; its empty tier 2 is not a place
    assert ju.occurrences[0].name == "sample_id" and ju.occurrences[0].type == "String" and [s.table for s in ju.occurrences[0].sources] == ["E", "M"]
    assert reach(ju) == (0, 0) and ju.reach.tables_no_plot == {"T1:JU"} and ju.reach.n_tables_no_plot == 1 and ju.reach.plots == frozenset()
    assert ju.no_plot_reads is True and all(line(walk, p).no_plot_reads is False for p in places(walk) if p != "T1:JU")
    assert "T1:U" not in places(walk)                                                              # linked to nothing: not reached, so not a line (D-0415 stays)
    # the reach of E counts JU as a table apart while no plot reads it; when a plot reads it, JU is a table with a plot and nothing else changes in the places
    with_plot = copy.deepcopy(recipe)
    with_plot["analysis_groups"]["g"]["plots"]["Pj"] = F.plot("JU")
    after = run(with_plot, tables, "T3:Pd", "sample_id")
    assert set(places(after)) == set(places(walk)) | {"T3:Pj"} and line(after, "T1:JU").no_plot_reads is False and reach(line(after, "T1:JU")) == (1, 1)
    assert line(walk, "T1:E").reach.tables_no_plot == {"T1:JU"} and line(after, "T1:E").reach.tables_no_plot == frozenset()


def test_L005_the_line_of_a_table_no_plot_reads_says_a_column_it_does_not_hold_is_gone_there():
    recipe, tables = F.tiers()
    recipe["joins"]["JU"]["tier1"]["steps"].append(F.select("sample_id", "gene"))                  # JU keeps no `year`: M's year arrives and is selected away
    walk = run(recipe, tables, "T1:M", "year")
    assert "T1:JU" not in places(walk) and "T1:JU" in {g.place for g in walk.gone}                 # a note, not a line: the column is gone there
    gone = next(g for g in walk.gone if g.place == "T1:JU")
    assert gone.removed_by is not None and gone.removed_by.action == "polars_select" and gone.reach.tables_no_plot == {"T1:JU"}
    assert "T1:JU" in walk.accounted                                                              # every place is a line, a note, or accounted for


def test_L005_a_table_no_plot_reads_reached_only_through_another_table_no_plot_reads():
    recipe, tables = F.tiers()
    recipe["joins"]["JV"] = F.join(["JU", "S"], [F.join_step("S")])                              # JV is built from JU, which no plot reads either
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    assert {"T1:JU", "T1:JV"} <= set(places(walk)) and line(walk, "T1:JV").no_plot_reads and line(walk, "T1:JU").no_plot_reads
    assert line(walk, "T1:JU").reach.tables_no_plot == {"T1:JU", "T1:JV"} and line(walk, "T1:JV").reach.tables_no_plot == {"T1:JV"}
    assert reach(line(walk, "T1:JU")) == (0, 0) and line(walk, "T1:E").reach.tables_no_plot == {"T1:JU", "T1:JV"}
    assert len(set(walk.accounted)) == len(walk.accounted)


def test_L005_an_unread_table_reached_through_a_step_the_walk_cannot_follow_is_grey_with_the_reason_D_0460():
    # D-0460: a line the app cannot trace is not ticked and says why; the same for a table no plot reads, and for the table built from it. The step is outside the readings
    # and changes the type of the column (a split makes a list), so the plan alone cannot prove the column the same one.
    recipe = F.recipe({"A": F.schema(["sample_id", "genes"], keys=["sample_id"]), "B": F.schema(["sample_id", "w"], keys=["sample_id"])},
                      {"JA": F.join(["A", "B"], [F.join_step("B"), F.str_split(["genes"], ",")]), "JB": F.join(["JA", "B"], [F.join_step("B")])}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1", "S2"], genes=["a,b", "c"]), "B": F.table(sample_id=["S1"], w=["p"])}
    walk = run(recipe, tables, "T3:P", "genes")
    assert [x.place for x in walk.lines if x.no_plot_reads] == ["T1:JA", "T1:JB"]
    for place in ("T1:JA", "T1:JB"):
        assert line(walk, place).state == "grey" and line(walk, place).reason.code in (STEP_NOT_READ, "cannot_follow"), place
    assert line(walk, "T1:JA").reason.code == STEP_NOT_READ and line(walk, "T1:JA").reason.get("action") == "polars_str_split"
    assert ticked(walk) == ["T1:A", "T3:P"]                                                           # the lines with a plot behave as before
    key = run(recipe, tables, "T3:P", "sample_id")                                                    # a column the step does not touch passes it, ticked
    # "tick" is the walk's proof that it is the same column, not a default tick of the dialog (not decided: ledger D-0451).
    assert [(x.place, x.state) for x in key.lines if x.no_plot_reads] == [("T1:B", "tick"), ("T1:JA", "tick"), ("T1:JB", "tick")]     # B too: only joins no plot reads read it


def test_L005_a_drop_is_offered_at_a_table_no_plot_reads_like_at_any_place():
    recipe, tables = F.tiers()
    walk = run(recipe, tables, "T1:M", "year", kind="drop")
    ju = line(walk, "T1:JU")
    # "tick" is the walk's proof that it is the same column, not a default tick of the dialog (not decided: ledger D-0451).
    assert ju.no_plot_reads and ju.state == "tick" and ju.refusal is None and ju.consequences == ()      # nothing is built from JU and no plot draws it: nothing to break
    assert line(walk, "T1:J1").no_plot_reads is False


def test_L005_nothing_of_the_old_rule_is_left_in_the_records():
    # D-0451: a place no plot reads is no longer "counted apart"; the record and the field that said so are gone, not kept beside the new rule
    import utils.lineage_records as records
    assert not hasattr(records, "Unread") and "unread" not in {f.name for f in dataclasses.fields(records.Walk)} and not hasattr(records.Walk, "unread")
    assert "no_plot_reads" not in {f.name for f in dataclasses.fields(records.Line)}                  # derived from the reach, never stored beside it (D-0195, D-0316)


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
    assert walk.gone == () and walk.outside == ()
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


def test_L013_a_table_joined_with_itself_is_not_followed_YET_and_red_D_0452():
    """Before D-0452 the column was followed into the copy (`country`, `country_right`: grey `several_columns`, PROVISIONAL O8); now the join is one the app cannot YET follow: the
    line is grey with the reason `join_not_yet_followed` (a self-join, kind left), also for the key, and the walk does not list the copy of the column."""
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"])}, {"J": F.join(["A"], [F.join_step("A")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"])}
    walk = run(recipe, tables, "T1:A", "country")
    j = line(walk, "T1:J")
    assert [o.name for o in j.occurrences] == ["country"]
    assert j.state == "grey" and j.reason.code == "join_not_yet_followed" and j.reason.get("self_join") is True and j.reason.get("kind") == "left"
    assert line(walk, "T1:A").state == "tick"
    assert reach(line(walk, "T1:A")) == (2, 1)                                         # A and J: the self-join is one edge, A is not counted twice
    key = run(recipe, tables, "T1:A", "sample_id")
    assert line(key, "T1:J").state == "grey" and line(key, "T1:J").reason.code == "join_not_yet_followed"      # the key too: before, it was ticked


# ----------------------------------------------------------------------------------------------------------------------------- scopes

KEY_STARTS = ["DS:S", "DS:E", "DS:M", "T1:S", "T2:S", "T1:E", "T1:M", "T1:J1", "T2:J1", "T1:J2", "T3:Ps", "T3:Pe", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"]


def shape(walk):
    """What must not depend on the start: the places, their state, reach and column names. (`is_start` and the scope group are relative to the start.)"""
    return [(x.place, x.state, x.reach, tuple(o.name for o in x.occurrences)) for x in walk.lines], [g.place for g in walk.gone]


@pytest.mark.parametrize("scope", [JOIN_LINKED])
def test_L014_same_places_from_every_start_of_one_key_when_joins_that_equate_it_are_followed(scope):
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    reference = shape(index.walk(Start("T3:Pd", "sample_id"), levels=TIERS).within(scope))
    for node in KEY_STARTS:
        assert shape(index.walk(Start(node, "sample_id"), levels=TIERS).within(scope)) == reference, node


def test_L014_PROVISIONAL_the_group_above_and_below_depends_on_where_the_user_looked_from_the_union_does_not():
    # D-0347 as written (back to the sources of the chosen place, then forward) gives other places from Pd than from Pe (question O1). The user chooses the
    # scope by ticking (owner, 2026-11-20): every candidate place is returned, each with its group, so the union is the same from both.
    recipe, tables = F.tiers()
    from_pd, from_pe = run(recipe, tables, "T3:Pd", "sample_id"), run(recipe, tables, "T3:Pe", "sample_id")
    assert shape(from_pd) == shape(from_pe)
    assert set(places(from_pd.within(LINEAGE))) != set(places(from_pe.within(LINEAGE)))
    assert "T1:E" not in places(from_pd.within(LINEAGE)) and "T3:Pe" not in places(from_pd.within(LINEAGE)) and "T1:E" in places(from_pe.within(LINEAGE))
    assert line(from_pd, "T1:E").scope_group == JOIN_LINKED and line(from_pe, "T1:E").scope_group == LINEAGE      # the group is relative to the start
    assert len(from_pd.within(LINEAGE).lines) == 12 and len(from_pd.lines) == 14


def test_the_groups_of_a_key_tell_above_and_below_and_linked_by_a_join_and_nothing_else():
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    groups = {x.place: x.scope_group for x in walk.lines}
    assert set(groups.values()) == {LINEAGE, JOIN_LINKED}                                              # no group for "the same key, no join links it"
    assert groups["T1:S"] == groups["T3:Pd"] == groups["T1:M"] == LINEAGE
    assert groups["T1:E"] == groups["T3:Pe"] == JOIN_LINKED
    assert "T1:U" not in groups and "T3:Pu" not in groups                                               # U declares the key, no join links it: not a line
    assert [(o.table, o.column, o.why) for o in walk.outside] == [("U", "sample_id", "declared_key_not_reached")]      # information only
    assert walk.outside[0].reach.plots == {"Pu"}
    assert groups["T1:JU"] == LINEAGE and line(walk, "T1:JU").no_plot_reads                           # JU is built from M, which the chosen place reads
    assert all(x.refusal is None for x in walk.lines)                       # the record can carry "refused here, with the reason"; nothing sets it yet (the drop step)


@pytest.mark.parametrize("scope", ALL_SCOPES)
def test_L014_a_column_no_join_equates_gives_the_same_places_from_every_start_under_every_scope(scope):
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    reference = shape(index.walk(Start("T3:Ps", "country"), levels=TIERS).within(scope))
    for node in ("DS:S", "T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"):
        assert shape(index.walk(Start(node, "country"), levels=TIERS).within(scope)) == reference, node
    assert places(index.walk(Start("T3:Ps", "country"), levels=TIERS).within(scope)) == ["T1:S", "T2:S", "T1:J1", "T2:J1", "T1:J2", "T3:Ps", "T3:Pa", "T3:Pb", "T3:Pc", "T3:Pd"]


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
def test_L052_remove_one_sample_in_the_places_ticked_what_is_left_is_offered_in_a_wider_group_or_said_as_not_reached(scope):
    # "remove sample S3 from all tables": the user ticks the places of a group; after a filter at every ticked line, every table that still holds S3 is a place
    # that the walk offers in the wider group, a place no plot reads, or a table the walk lists as not reached (declared key, no join). By hand:
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    graph, _ = setup(recipe, tables)
    full = run(recipe, tables, "T3:Pd", "sample_id")
    walk = full.within(scope)
    left = holders_after(recipe, tables, walk, "S3")
    e_chain, u_chain = {"T1:E", "T2:E", "T3:Pe"}, {"T1:U", "T2:U", "T3:Pu"}                  # JU is a line of the lineage group now (D-0451): the step at it takes the sample out
    assert left == {LINEAGE: e_chain | u_chain, JOIN_LINKED: u_chain}[scope]
    offered = {x.place for x in full.lines if x not in walk.lines}
    not_reached = {n for o in full.outside for n in [f"T1:{o.table}"] + graph.lineage_forward(f"T1:{o.table}")}
    assert {n for n in left if node_place(recipe, n) not in offered} == u_chain and u_chain <= not_reached      # nothing is left that the walk neither offered nor listed


def test_L052_a_table_that_declares_the_key_and_no_join_links_is_information_never_a_line():
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    assert "T1:U" not in places(walk) and "T3:Pu" not in places(walk) and "never the column name alone" in walk.key_basis
    # without the declaration the table is not even listed: the name alone never links two columns
    undeclared = run(*F.tiers(u_declares_key=False, u_plot=True), "T3:Pd", "sample_id")
    assert "T1:U" not in places(undeclared) and undeclared.outside == ()


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

def test_L015_a_rename_on_one_path_is_followed_and_the_other_table_is_never_offered():
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
    assert places(from_source) == ["T1:A", "T3:Pa"] and ticked(from_source) == places(from_source)           # the rename is followed: the line carries the name THERE
    assert line(from_source, "T1:A").occurrences[0].name == "origin" and line(from_source, "T1:A").occurrences[0].sources[0].name == "country"
    assert line(from_source, "T1:A").notes == () and line(from_source, "T1:A").occurrences[0].steps[0].how == "renamed"      # a rename is a hop, not a note


def test_L016_same_name_and_same_type_is_not_the_same_column():
    recipe = F.recipe({"A": F.schema(["sample_id", "a_year"], [F.rename(a_year="year")]), "B": F.schema(["sample_id", "b_year"], [F.rename(b_year="year")])},
                      {}, {"Pa": F.plot("A"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"], a_year=[2022]), "B": F.table(sample_id=["S1"], b_year=[2022])}
    assert places(run(recipe, tables, "T3:Pa", "year")) == ["T1:A", "T3:Pa"] and places(run(recipe, tables, "T3:Pb", "year")) == ["T1:B", "T3:Pb"]


def test_L017_a_clash_in_a_join_the_right_column_carries_the_suffix_and_is_followed_to_its_name_in_its_table():
    recipe = F.recipe({"A": F.schema(["sample_id", "val"]), "B": F.schema(["sample_id", "val"])}, {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], val=[1.0]), "B": F.table(sample_id=["S1"], val=[2.0])}
    left = run(recipe, tables, "T1:J", "val")
    assert places(left) == ["T1:A", "T1:J", "T3:P"] and ticked(left) == places(left)              # A's val; B's val is another column
    right = run(recipe, tables, "T1:J", "val_right")
    assert places(right) == ["T1:B", "T1:J", "T3:P"] and ticked(right) == places(right)
    assert [(x.place, x.occurrences[0].name) for x in right.lines] == [("T1:B", "val"), ("T1:J", "val_right"), ("T3:P", "val_right")]      # `val` in B, `val_right` after the join
    hop = line(right, "T1:J").occurrences[0].steps[0]
    assert (hop.join_how, hop.join_side, hop.name_before, hop.name_after) == ("left", "right", "val", "val_right")


def test_L019_a_swap_by_rename_is_followed_by_the_mapping_not_one_rename_after_the_other():
    recipe = F.recipe({"A": F.schema(["a", "b"], [F.rename(a="b", b="a")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(a=["x"], b=["y"])}
    walk = run(recipe, tables, "DS:A", "a")                                                       # Polars renames at once: the old `a` is the new `b`
    assert [(x.place, x.state, x.occurrences[0].name) for x in walk.lines] == [("T1:A", "tick", "b"), ("T3:P", "tick", "b")]
    other = run(recipe, tables, "DS:A", "b")
    assert [(x.place, x.state, x.occurrences[0].name) for x in other.lines] == [("T1:A", "tick", "a"), ("T3:P", "tick", "a")]
    back = run(recipe, tables, "T3:P", "b", levels=("source", "T1", "T2", "T3"))                   # and backwards: the column called `b` at the end was `a` in the file
    assert line(back, "DS:A").occurrences[0].name == "a" and line(back, "T1:A").occurrences[0].name == "b"
    typed = {"A": F.table(a=["x"], b=[1])}                                                        # with two types the plan itself shows the swap: the reading agrees with it
    mixed = run(recipe, typed, "DS:A", "a")
    assert [(x.place, x.state, x.occurrences[0].name, x.occurrences[0].type) for x in mixed.lines] == [("T1:A", "tick", "b", "String"), ("T3:P", "tick", "b", "String")]


def test_L021_a_key_under_another_name_is_followed_to_its_name_in_the_other_table():
    recipe = F.recipe({"A": F.schema(["sample_id"], keys=["sample_id"]), "B": F.schema(["isolate", "lab"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"))])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"]), "B": F.table(isolate=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T1:J", "sample_id")
    assert places(walk) == ["T1:A", "T1:B", "T1:J", "T3:P", "T3:Pb"] and ticked(walk) == places(walk)
    assert line(walk, "T1:B").occurrences[0].name == "isolate" and line(walk, "T1:A").occurrences[0].name == "sample_id"      # the name THERE
    hop = line(walk, "T1:J").occurrences[0].steps[0]
    assert (hop.name_before, hop.name_after, hop.join_side) in {("sample_id", "sample_id", "base"), ("isolate", "sample_id", "right")}


def test_L022_a_full_join_is_not_followed_YET_and_what_depends_on_it_is_red_with_the_join_as_the_reason_D_0452():
    """Before D-0452: a column of the first table was ticked after a full join with the note `unread_step_passed`, and one of the second table was grey `step_not_read`."""
    recipe = F.recipe({"A": F.schema(["sample_id", "country"]), "B": F.schema(["sample_id", "lab"])}, {"J": F.join(["A", "B"], [F.join_step("B", how="full")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(sample_id=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T1:A", "country")
    assert line(walk, "T1:J").state == "grey" and line(walk, "T1:J").reason.code == "join_not_yet_followed" and line(walk, "T1:J").notes == ()
    keyed = run(recipe, tables, "T1:B", "lab")
    assert line(keyed, "T1:J").state == "grey" and line(keyed, "T1:J").reason.code == "join_not_yet_followed" and line(keyed, "T1:J").reason.get("kind") == "full"


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

def test_L034_a_cast_changes_the_type_of_the_column_it_names_the_same_column_is_offered_with_a_note():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.cast(["year"], "String")])
    walk = run(recipe, tables, "DS:A", "year")                                       # from the source column, the cast is on the path
    assert [(x.place, x.state) for x in walk.lines] == [("T1:A", "tick"), ("T1:J", "tick"), ("T3:P1", "tick"), ("T3:P2", "tick")]      # the same column (D-0353, D-0337)
    occurrence = line(walk, "T1:A").occurrences[0]
    assert (occurrence.how, occurrence.type, occurrence.steps[0].type_before, occurrence.steps[0].type_after) == ("cast", "String", "Int64", "String")
    note = line(walk, "T1:A").notes[0]
    assert note.code == NOTE_ANOTHER_TYPE and dict(note.params) == {"node": "T1:A", "step": 2, "action": "polars_cast", "name_before": "year", "name_after": "year",
                                                                  "type_before": "Int64", "type_after": "String", "direction": "forward"}
    assert walk.start_type == "Int64" and line(walk, "T3:P2").occurrences[0].type == "String" and line(walk, "T3:P2").notes[0].code == NOTE_ANOTHER_TYPE
    after = run(recipe, tables, "T3:P2", "year")                                      # from after the cast it is the same column everywhere downstream
    assert places(after) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and ticked(after) == places(after) and all(x.notes == () for x in after.lines)
    back = run(recipe, tables, "T3:P2", "year", levels=("source", "T1", "T2", "T3"))  # from after the cast, back to the file: the source has another type, said as data
    source = line(back, "DS:A")
    assert source.occurrences[0].type == "Int64" and back.start_type == "String" and source.notes[0].code == NOTE_ANOTHER_TYPE
    assert (dict(source.notes[0].params)["direction"], dict(source.notes[0].params)["type_before"], dict(source.notes[0].params)["type_after"]) == ("backward", "Int64", "String")
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
    written = run(recipe, tables, "DS:A", "year")                                     # the step writes `year`: the same column, recomputed (D-0353): offered, ticked, with a note
    assert [(x.place, x.state) for x in written.lines] == [("T1:A", "tick"), ("T1:J", "tick"), ("T3:P1", "tick"), ("T3:P2", "tick")]
    note = line(written, "T1:A").notes[0]
    assert note.code == NOTE_RECOMPUTED and dict(note.params)["step"] == 2 and dict(note.params)["knows_source_of_values"] is False      # PROVISIONAL: names only
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
    key = run(recipe, tables, "DS:A", "year")                                         # a group column passes under its name, the rows after the step are the groups
    aggregate = run(recipe, tables, "DS:A", "val")                                    # an aggregate under the same name: the same column, offered with a note (D-0353)
    assert ticked(aggregate) == places(aggregate) == ["T1:A", "T1:J", "T3:P1", "T3:P2"]
    assert [n.code for n in line(aggregate, "T1:A").notes] == [NOTE_AGGREGATED] and line(aggregate, "T1:A").occurrences[0].how == "aggregated"
    assert [(x.place, x.state) for x in key.lines] == [(p, "tick") for p in ["T1:A", "T1:J", "T3:P1", "T3:P2"]]
    assert [n.code for n in line(key, "T1:A").notes] == [NOTE_ONE_ROW_PER_GROUP] and line(key, "T1:A").occurrences[0].how == "grouped"       # a group key: rows are the groups after the step


def test_L018_a_column_renamed_in_one_tier_and_back_in_a_later_one_is_one_column_named_as_in_each_table():
    # owner 2026-11-20 (D-0357, D-0352): ONE column, named as in each table. A rename in tier 1 and back in tier 2: the tier 1 line shows the tier 1 name.
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], [F.rename(country="origin")], [F.rename(origin="country")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"])}
    walk = run(recipe, tables, "T3:P", "country")
    assert places(walk) == ["T1:A", "T2:A", "T3:P"] and ticked(walk) == places(walk)
    assert [(x.place, x.occurrences[0].name) for x in walk.lines] == [("T1:A", "origin"), ("T2:A", "country"), ("T3:P", "country")]
    assert {(s.table, s.name) for x in walk.lines for o in x.occurrences for s in o.sources} == {("A", "country")}        # one source column
    from_t1 = run(recipe, tables, "T1:A", "origin")
    assert [(x.place, x.occurrences[0].name) for x in from_t1.lines] == [("T1:A", "origin"), ("T2:A", "country"), ("T3:P", "country")]
    hops = line(from_t1, "T3:P").occurrences[0].steps
    assert [(h.step.node, h.name_before, h.name_after) for h in hops] == [("T1:A", "country", "origin"), ("T2:A", "origin", "country")]       # renamed from, to, by which step


def test_L018_a_rename_within_one_tier_and_back_leaves_no_place_with_the_other_name():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], [F.rename(country="origin"), F.rename(origin="country")])}, {}, {"P": F.plot("A")})
    walk = run(recipe, {"A": F.table(sample_id=["S1"], country=["NO"])}, "DS:A", "country")
    assert [(x.place, x.occurrences[0].name) for x in walk.lines] == [("T1:A", "country"), ("T3:P", "country")]               # the tier's table has one name
    assert [h.name_after for h in line(walk, "T1:A").occurrences[0].steps] == ["origin", "country"]                            # the way is still in the hops


def test_L034_a_reading_that_the_plan_contradicts_is_grey_with_the_problem():
    recipe = F.recipe({"A": F.schema(["a", "b"], [F.rename(a="c")])}, {}, {"P": F.plot("A")})
    both = [("a", "Int64"), ("b", "Int64")]
    graph = setup(recipe, {"A": F.table(a=[1], b=[2])})[0]
    plans = PlanBook.of({("DS:A", 0): both, ("T1:A", 0): both, ("T1:A", 1): both, ("T2:A", 0): both, ("T3:P", 0): both})      # the rename did not happen, says the plan
    walk = LineageIndex(graph, plans).walk(Start("DS:A", "a"), levels=TIERS).within(JOIN_LINKED)
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
    base = LineageIndex(graph, plans).walk(Start("DS:A", "country"), levels=TIERS).within(JOIN_LINKED)
    assert base.found == 4
    for node in graph.nodes():
        if node.startswith("DS:"):
            continue
        for k in range(len(graph.node(node).steps) + 1):
            g, broken, below = failing(recipe, tables, node, k)
            walk = LineageIndex(g, broken).walk(Start("DS:A", "country"), levels=TIERS).within(JOIN_LINKED)      # never an exception, never an empty list
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
        index.walk(Start("T3:P1", "nope"), levels=TIERS).within(LINEAGE)
    assert "nope" in str(error.value) and "T3:P1" in str(error.value)
    with pytest.raises(ColumnNotFound):
        index.walk(Start("T3:P1", "COUNTRY"), levels=TIERS).within(LINEAGE)                       # names are exact
    with pytest.raises(LineageError):
        index.walk(Start("T3:Nope", "country"), levels=TIERS).within(LINEAGE)
    with pytest.raises(LineageError):
        index.walk(Start("T3:P1", "country"), levels=TIERS, kind="rename").within(LINEAGE)
    with pytest.raises(TypeError):
        index.walk(Start("T3:P1", "country"), scope="lineage")                           # no scope is applied: the user ticks (owner, 2026-11-20)
    g, failed, _ = failing(recipe, tables, "T1:A", 0)
    with pytest.raises(StartPlanFailed):
        LineageIndex(g, failed).walk(Start("T3:P2", "country"), levels=TIERS).within(LINEAGE)


def test_the_levels_the_user_chooses_decide_the_places_offered_and_must_be_named():
    recipe, tables = F.chain()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    start = Start("T3:P1", "country")
    everything = index.walk(start, levels=("source", "T1", "T2", "T3"))
    assert places(everything) == ["DS:A", "T1:A", "T1:J", "T3:P1", "T3:P2"] and everything.levels == ("source", "T1", "T2", "T3")
    assert places(index.walk(start, levels=("T3",))) == ["T3:P1", "T3:P2"] and places(index.walk(start, levels=("source",))) == ["DS:A"]
    assert places(index.walk(start, levels=("T1",))) == ["T1:A", "T1:J"]
    # an empty tier is no place: the table of A at the tier-2 level is the one place T1:A (it covers both)
    assert places(index.walk(start, levels=("T2",))) == ["T1:A", "T1:J"]
    assert index.walk(start, levels=("T3", "source", "T3")).levels == ("source", "T3")             # any order, each once, in the order of the data flow
    for wrong in ((), ("T4",), ("tier1",)):
        with pytest.raises(LineageError):
            index.walk(start, levels=wrong)
    with pytest.raises(TypeError):
        index.walk(start)                                                                           # the levels are not decided for the user: the caller names them


def test_a_source_table_is_a_line_that_cannot_hold_a_step_PROVISIONAL():
    # a source file holds no list of steps (D-0332): the line is returned, grey with the reason, so the dialog can say it; how a step acts at the source level is not decided
    recipe, tables = F.chain()
    walk = run(recipe, tables, "T3:P1", "sample_id", levels=("source",))
    assert places(walk) == ["DS:A", "DS:B"] and all(x.state == "grey" and x.reason.code == NO_STEP_LIST for x in walk.lines)
    assert line(walk, "DS:A").tier == "DS" and reach(line(walk, "DS:A")) == (2, 2) and line(walk, "DS:A").occurrences[0].name == "sample_id"
    unread = F.recipe({"A": F.schema(["sample_id"]), "Z": F.schema(["sample_id"])}, {"J": F.join(["A", "Z"], [F.join_step("Z")])}, {"P": F.plot("A")})
    alone = run(unread, {"A": F.table(sample_id=["S1"]), "Z": F.table(sample_id=["S1"])}, "T3:P", "sample_id", levels=("source",))
    assert places(alone) == ["DS:A", "DS:Z"] and not line(alone, "DS:A").no_plot_reads and line(alone, "DS:Z").no_plot_reads      # the source of a table no plot reads is a line too (D-0451)
    assert line(alone, "DS:Z").state == "grey" and line(alone, "DS:Z").reason.code == NO_STEP_LIST and line(alone, "DS:Z").duplicates == "T1:Z"


def test_L034_an_unread_step_that_changes_the_type_of_a_column_is_not_proved_the_same():
    recipe = F.recipe({"A": F.schema(["sample_id", "genes"], [F.str_split(["genes"], ",")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1"], genes=["a,b"])}
    walk = run(recipe, tables, "DS:A", "genes")
    assert [(x.place, x.state) for x in walk.lines] == [("T1:A", "grey"), ("T3:P", "grey")]
    assert (line(walk, "T1:A").reason.code, line(walk, "T1:A").reason.get("action")) == (STEP_NOT_READ, "polars_str_split")
    assert line(walk, "T1:A").occurrences[0].type != "String" and line(walk, "T1:A").occurrences[0].how == "unknown"
    assert ticked(run(recipe, tables, "T3:P", "genes")) == ["T1:A", "T3:P"]                  # after the step it is the same column downstream


def test_L006_a_tier_2_no_plot_reads_is_applied_nowhere_and_is_not_a_place():
    recipe, tables = F.tiers()
    recipe["joins"]["JU"]["tier2"] = {"steps": [F.keep("year", "gt", 1)]}                   # JU is read by no plot: its tier 2 runs nowhere
    recipe["data_schemas"]["M"]["tier2"] = {"steps": [F.keep("year", "gt", 1)]}             # M is read by joins only: its tier 2 runs nowhere
    walk = run(recipe, tables, "T3:Pd", "sample_id")
    assert "T2:JU" not in walk.accounted and "T2:M" not in walk.accounted and "T1:JU" in places(walk)      # JU's tier 1 is the line; its tier 2 is no place (the checks S07, J14 refuse it)
    assert places(walk) == places(run(*F.tiers(), "T3:Pd", "sample_id"))


# ----------------------------------------------------------------------------------------------------------------------------- the public accessor of how certain a link is

def test_the_public_accessor_gives_certainty_notes_and_uncertain_ends_of_the_columns_linked_to_seeds():
    """`LineageIndex.certainty_from` and `uncertain_ends` (the questions `utils.remove_from_all` asks; they replace its reading of the walk's protected members): for the
    columns linked to some seeds, how many uncertain links lie on the best path, why, and which notes lie on it; and the columns a step the walk cannot read leaves."""
    tables = {"A": F.table(sample_id=["S1", "S2"], v=["1", "2"])}
    for step, cost, notes in ((F.with_columns(sample_id="pl.col('sample_id').str.to_lowercase()"), 0, ["recomputed_here"]), (F.str_split(["sample_id"], "-"), 1, []), (F.drop("v"), 0, [])):
        recipe = F.recipe({"A": F.schema(["sample_id", "v"], [step], keys=["sample_id"])}, {}, {"P": F.plot("A")})
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        seed = ("DS:A", 0, "sample_id")
        within = index.component([seed])
        result = index.certainty_from([seed], within)
        assert set(result) == within and result[seed].cost == 0 and result[seed].certain and result[seed].notes == ()
        end = ("T1:A", 1, "sample_id")
        if cost == 0:
            assert result[end].certain and [n.code for n in result[end].notes] == notes and result[end].reason is None
            assert index.uncertain_ends(within) == []
        else:
            assert end in result and result[end].cost == 1 and not result[end].certain and result[end].reason.code == STEP_NOT_READ
            assert index.uncertain_ends(within) == [], "the column is still there: its link is uncertain, it did not die"


def test_the_public_accessor_names_the_uncertain_end_when_a_step_the_walk_cannot_read_makes_the_key_leave():
    tables = {"A": F.table(sample_id=["S1", "S2"], v=["1", "2"])}
    recipe = F.recipe({"A": F.schema(["sample_id", "v"], [F.unpivot(["sample_id"], ["v"])], keys=["sample_id"])}, {}, {"P": F.plot("A")})
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    seed = ("DS:A", 0, "sample_id")
    ends = index.uncertain_ends(index.component([seed]))
    assert len(ends) == 1 and ends[0].in_node == "T1:A" and ends[0].reason.code == STEP_NOT_READ and ends[0].occ[2] == "sample_id"


def test_the_public_accessor_with_two_seeds_gives_the_columns_of_each_and_the_best_certainty():
    """Two unlinked tables A and E, one seed in each: the result holds the columns reached from either seed, whatever the order of the seeds; a column the second seed
    reaches certainly is not made uncertain by the first (the fewest uncertain links over the seeds)."""
    tables = {"A": F.table(sample_id=["S1", "S2"], v=["1", "2"]), "E": F.table(sample_id=["S1", "S2"], g=["1", "2"])}
    recipe = F.recipe({"A": F.schema(["sample_id", "v"], [F.str_split(["sample_id"], "-")], keys=["sample_id"]), "E": F.schema(["sample_id", "g"], keys=["sample_id"])}, {}, {"P": F.plot("A"), "Pe": F.plot("E")})
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    seed_a, seed_e = ("DS:A", 0, "sample_id"), ("DS:E", 0, "sample_id")
    within = index.component([seed_a, seed_e])
    both = index.certainty_from([seed_a, seed_e], within)
    assert set(both) == within and {o[0] for o in both} >= {"DS:A", "T1:A", "DS:E", "T1:E"}
    assert both == index.certainty_from([seed_e, seed_a], within), "the order of the seeds does not matter"
    only_a = index.certainty_from([seed_a], within)
    assert ("T1:E", 0, "sample_id") not in only_a and ("T1:A", 1, "sample_id") in only_a, "E is not linked to A: it is reached only from its own seed"
    assert not both[("T1:A", 1, "sample_id")].certain and both[("T1:E", 0, "sample_id")].certain


def test_the_public_accessor_never_leaves_the_set_it_is_given():
    tables = {"A": F.table(sample_id=["S1", "S2"], v=["1", "2"]), "B": F.table(sample_id=["S1", "S2"], w=["3", "4"])}
    recipe = F.recipe({"A": F.schema(["sample_id", "v"], keys=["sample_id"]), "B": F.schema(["sample_id", "w"], keys=["sample_id"])}, {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P": F.plot("J")})
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    seed = ("DS:A", 0, "sample_id")
    full = index.component([seed])
    assert any(o[0] == "T1:J" for o in full)
    limited = {o for o in full if o[0] != "T1:J"}
    unlimited, result = index.certainty_from([seed], full), index.certainty_from([seed], limited)
    assert any(o[0] == "T1:J" for o in unlimited), "without the limit the join's column is reached"
    assert set(result) <= limited and not any(o[0] == "T1:J" for o in result) and seed in result, "with the limit it is not asked about"
    assert index.uncertain_ends(set()) == [], "an empty set holds no end"
