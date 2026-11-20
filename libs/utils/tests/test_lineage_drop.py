"""The lineage walk of a DROP (LBFB step 4, D-0358 which modulates D-0297): the key refusal by place, the consequences, the candidate plans. Cases are named with their
number in `tmpAI/panel/lineage_tests/DESIGN.md`; a test that says `PROVISIONAL` states what the walk does while the owner has not decided.

The proof that does not trust the walk (invariant I6): for every column of every fixture, the recipe with a `polars_drop` written at each place the walk offers is
replayed by plain Polars (`lineage_oracle`, which knows nothing of the walk). A line the walk calls tickable with no reported consequence must build; a line it refuses
must fail at the join that needs the column; a line with a reported consequence must fail or lose the plot's column exactly there. The candidate plans handed to the
walk are the oracle's own replay of the candidate recipe.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_drop.py -q
"""
import copy
from typing import Any, Dict, Iterator, List, Tuple

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import TIERS, places, run, setup, ticked

from utils.lineage_records import (
    BUILD_FAILS, CLASH_NO_LONGER, CONSEQUENCE_DISAGREES, FROM_PLAN, FROM_READING, KEY_NEEDED_LATER, NOTE_DECLARED_ENTITY_KEY, PLAN_FAILED, PLOT_USES_COLUMN, STEP_NAMES_COLUMN, Start,
)
from utils.lineage_walk import LineageError, LineageIndex
from utils.plan_book import PlanBook

ALL = ("source", "T1", "T2", "T3")


def line(walk, place):
    return next(x for x in walk.lines if x.place == place)


def needs(x):
    """The join steps a refusal names: (node, step number, side, the column's name at the join)."""
    return [(n.step.node, n.step.step, n.side, n.name) for n in x.refusal.get("needs")] if x.refusal else []


def candidates(recipe, tables, walk, column_of=lambda x: x.occurrences[0].name):
    """The oracle's plan book of the candidate recipe of every line of a drop walk that holds one column."""
    return {x.place: O.replay(O.with_audit_drop(recipe, x.place, column_of(x)), tables).plans for x in walk.lines if len(x.occurrences) == 1}


def drop_walk(recipe, tables, node, column, with_candidates=False, levels=TIERS):
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    first = index.walk(Start(node, column), levels=levels, kind="drop")
    if not with_candidates:
        return first
    return index.walk(Start(node, column), levels=levels, kind="drop", candidates=candidates(recipe, tables, first))


# ----------------------------------------------------------------------------------------------------------------------------- fixtures

def counting_plot():
    """Her example (D-0358): a plot that only counts, `x` is `country`, on a table whose key `sample_id` is read by a join elsewhere. A(sample_id, country, year); B(sample_id, lab);
    J = A + B on sample_id; P1 reads J and draws `year`; Pc reads A with its own steps and draws only `country`."""
    tables = {"A": F.table(sample_id=F.IDS, country=["NO", "SE", "NO", "SE", "NO"], year=[2022, 2023, 2023, 2024, 2024]), "B": F.table(sample_id=["S1", "S2", "S3"], lab=["X", "Y", "Z"])}
    pc = F.plot("A", [F.keep("country", "ne", "XX")])
    pc["mapping"] = {"x": "country"}
    p1 = F.plot("J")
    p1["mapping"] = {"x": "year"}
    recipe = F.recipe({"A": F.schema(["sample_id", "country", "year"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P1": p1, "Pc": pc})
    return recipe, tables


def other_names():
    """The key under two names: A(sample_id, val), B(isolate, lab), J = A + B with left_on sample_id and right_on isolate, then a rename after the join; plots on J and on B."""
    tables = {"A": F.table(sample_id=F.IDS[:3], val=["a", "b", "c"]), "B": F.table(isolate=F.IDS[:3], lab=["X", "Y", "Z"])}
    recipe = F.recipe({"A": F.schema(["sample_id", "val"], keys=["sample_id"]), "B": F.schema(["isolate", "lab"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"))], [F.rename(sample_id="id")])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    return recipe, tables


def composite():
    """A join on TWO columns: A(sample_id, country, val), B(sample_id, country, lab), J = A + B on [sample_id, country]."""
    ids = F.IDS[:3]
    tables = {"A": F.table(sample_id=ids, country=["NO", "SE", "NO"], val=["a", "b", "c"]), "B": F.table(sample_id=ids, country=["NO", "SE", "NO"], lab=["X", "Y", "Z"])}
    recipe = F.recipe({"A": F.schema(["sample_id", "country", "val"], keys=["sample_id"]), "B": F.schema(["sample_id", "country", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=["sample_id", "country"])])}, {"P": F.plot("J")})
    return recipe, tables


def two_joins():
    """J holds TWO joins: A + B on sample_id, then + C on `lab` (a column that came from B). After the second join nothing reads either key."""
    ids = F.IDS[:3]
    tables = {"A": F.table(sample_id=ids, val=["a", "b", "c"]), "B": F.table(sample_id=ids, lab=["X", "Y", "Z"]), "C": F.table(lab=["X", "Y", "Z"], size=[1, 2, 3])}
    recipe = F.recipe({"A": F.schema(["sample_id", "val"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"]), "C": F.schema(["lab", "size"])},
                      {"J": F.join(["A", "B", "C"], [F.join_step("B"), F.join_step("C", on="lab")])}, {"P": F.plot("J")})
    return recipe, tables


def later_steps(formula=False):
    """A(sample_id, val), B(sample_id, lab), J = A + B, then (in tier 2 of J) a step that names `lab`: a rename, or (formula=True) a compute step that uses `lab` in its formula."""
    ids = F.IDS[:3]
    tables = {"A": F.table(sample_id=ids, val=["a", "b", "c"]), "B": F.table(sample_id=ids, lab=["X", "Y", "Z"])}
    after = [F.with_columns(lab_up="pl.col('lab').str.to_uppercase()")] if formula else [F.rename(lab="lab2")]
    p = F.plot("J")
    p["mapping"] = {"x": "val"}
    recipe = F.recipe({"A": F.schema(["sample_id", "val"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B")], after)}, {"P": p})
    return recipe, tables


def fixtures() -> List[Tuple[str, Any, Any]]:
    """Every fixture of the drop tests, with the recipes of the other lineage tests: each column of each is walked as a drop (invariant I6)."""
    out: List[Tuple[str, Any, Any]] = [("chain", *F.chain()), ("counting_plot", *counting_plot()), ("other_names", *other_names()), ("composite", *composite()),
                                       ("two_joins", *two_joins()), ("later_rename", *later_steps()), ("later_formula", *later_steps(True)),
                                       ("tiers", *F.tiers(u_declares_key=True, u_plot=True))]
    out.extend((f"followed_{name}", r, t) for name, r, t in F.followed())
    return out


# ----------------------------------------------------------------------------------------------------------------------------- the refusal by place (L029, D-0358, D-0297)

def test_L029_a_key_is_refused_where_a_join_still_reads_it_and_allowed_after_it():
    recipe, tables = F.chain()
    walk = run(recipe, tables, "T1:A", "sample_id", kind="drop")
    assert places(walk) == ["T1:A", "T1:B", "T1:J", "T3:P1", "T3:P2"]
    assert needs(line(walk, "T1:A")) == [("T1:J", 1, "base", "sample_id")]            # the join J, its table, its step number and the name it reads
    assert needs(line(walk, "T1:B")) == [("T1:J", 1, "right", "sample_id")]
    for place in ("T1:J", "T3:P1", "T3:P2"):                                           # after the join, and in the plots' own steps: no join step reads the column as a key
        assert line(walk, place).refusal is None and line(walk, place).state == "tick", place
    refused = [x for x in walk.lines if x.refusal]
    assert [x.place for x in refused] == ["T1:A", "T1:B"] and all(x.state == "grey" and x.reason.code == KEY_NEEDED_LATER for x in refused)
    assert walk.refused == 2 and walk.found == 3 and walk.grey == 2


def test_L029_the_same_lines_for_a_filter_are_all_tickable_the_refusal_is_for_a_drop_only():
    recipe, tables = F.chain()
    filt = run(recipe, tables, "T1:A", "sample_id", kind="filter")
    assert ticked(filt) == places(filt) == ["T1:A", "T1:B", "T1:J", "T3:P1", "T3:P2"] and all(x.refusal is None and x.consequences == () for x in filt.lines)


def test_a_non_key_column_is_not_refused_anywhere():
    recipe, tables = F.chain()
    walk = run(recipe, tables, "T1:A", "val", kind="drop")
    assert ticked(walk) == places(walk) == ["T1:A", "T1:J", "T3:P1", "T3:P2"] and walk.refused == 0


def test_a_refusal_carries_the_join_as_data_not_a_sentence():
    recipe, tables = F.chain()
    reason = line(run(recipe, tables, "T1:A", "sample_id", kind="drop"), "T1:A").refusal
    assert reason.code == KEY_NEEDED_LATER and reason.get("column") == "sample_id" and reason.get("place") == "T1:A"
    (need,) = reason.get("needs")
    assert (need.step.node, need.step.step, need.step.action, need.step.step_path, need.side, need.name, need.certain) == (
        "T1:J", 1, "polars_join", "joins.J.tier1.steps[1]", "base", "sample_id", True)


def test_the_same_key_under_another_name_on_the_right_side_is_refused_by_the_walks_own_links():
    recipe, tables = other_names()
    walk = run(recipe, tables, "T3:P", "id", kind="drop")                              # the name after the rename in tier 2 of J
    assert needs(line(walk, "T1:A")) == [("T1:J", 1, "base", "sample_id")]
    assert needs(line(walk, "T1:B")) == [("T1:J", 1, "right", "isolate")]               # B calls it `isolate`: followed by the join's pair, never by the name alone
    assert line(walk, "T1:J").refusal is None and line(walk, "T2:J").refusal is None and line(walk, "T3:P").refusal is None
    other = run(recipe, tables, "T1:B", "lab", kind="drop")                             # a column of B that no join names
    assert other.refused == 0


def test_a_column_named_like_a_key_but_not_the_same_column_is_not_refused():
    """`val` of A and `val` of B are two columns (the suffix of the clash): dropping B's `val` is no drop of A's key, and a column called `isolate` of another table is no key."""
    ids = F.IDS[:3]
    tables = {"A": F.table(sample_id=ids, val=["a", "b", "c"]), "B": F.table(sample_id=ids, val=["x", "y", "z"], isolate=["i", "j", "k"])}
    recipe = F.recipe({"A": F.schema(["sample_id", "val"], keys=["sample_id"]), "B": F.schema(["sample_id", "val", "isolate"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P": F.plot("J")})
    assert run(recipe, tables, "T1:B", "val", kind="drop").refused == 0
    assert run(recipe, tables, "T1:B", "isolate", kind="drop").refused == 0
    assert run(recipe, tables, "T1:B", "sample_id", kind="drop").refused == 2           # the key of A and of B is one column in J: both tables are before the join


@pytest.mark.parametrize("column, refused_places", [("sample_id", ["T1:A", "T1:B"]), ("country", ["T1:A", "T1:B"]), ("val", []), ("lab", [])])
def test_a_composite_key_each_part_is_refused_where_the_join_is_later(column, refused_places):
    recipe, tables = composite()
    node = "T1:B" if column == "lab" else "T1:A"
    walk = run(recipe, tables, node, column, kind="drop")
    assert [x.place for x in walk.lines if x.refusal] == refused_places
    if refused_places:
        assert all(needs(line(walk, p)) == [("T1:J", 1, "base" if p == "T1:A" else "right", column)] for p in refused_places)


def test_a_key_dropped_after_the_last_join_that_reads_it_is_allowed():
    """J holds two joins: A + B on `sample_id`, then + C on `lab`, a column that came from B with the first join. Each key is refused in the tables before its join and allowed at
    the END of J (and in the plot), where no join reads it any more."""
    recipe, tables = two_joins()
    ids = run(recipe, tables, "T1:A", "sample_id", kind="drop")
    assert needs(line(ids, "T1:A")) == [("T1:J", 1, "base", "sample_id")] and needs(line(ids, "T1:B")) == [("T1:J", 1, "right", "sample_id")]
    assert line(ids, "T1:J").refusal is None and line(ids, "T3:P").refusal is None
    lab = run(recipe, tables, "T1:B", "lab", kind="drop")
    assert needs(line(lab, "T1:B")) == [("T1:J", 2, "base", "lab")]                     # B's `lab` goes into J with the first join and is the left key of the second
    assert needs(line(lab, "T1:C")) == [("T1:J", 2, "right", "lab")]                    # C's `lab` is the right key of the second join: one column, followed by the key pair
    assert line(lab, "T1:J").refusal is None and line(lab, "T3:P").refusal is None


def test_L029_a_declared_entity_key_that_no_later_join_reads_is_not_refused_PROVISIONAL():
    """D-0297 names JOIN keys, D-0358 says by place: a key a table declares (`is_entity_key`) is no reason to refuse by itself; the line says it is a declared key (information)."""
    recipe, tables = F.tiers(u_declares_key=True, u_plot=True)
    walk = run(recipe, tables, "T1:U", "sample_id", kind="drop")
    assert line(walk, "T1:U").refusal is None and line(walk, "T1:U").state == "tick"
    note = next(n for n in line(walk, "T1:U").notes if n.code == NOTE_DECLARED_ENTITY_KEY)
    assert (dict(note.params)["table"], dict(note.params)["name"], dict(note.params)["column"]) == ("U", "sample_id", "sample_id")
    undeclared = run(*F.tiers(u_declares_key=False, u_plot=True), "T1:U", "sample_id", kind="drop")
    assert all(n.code != NOTE_DECLARED_ENTITY_KEY for n in line(undeclared, "T1:U").notes)


def test_a_declared_key_that_a_later_join_reads_is_refused_and_says_it_is_declared_too():
    recipe, tables = F.chain()
    x = line(run(recipe, tables, "T1:A", "sample_id", kind="drop"), "T1:A")
    assert x.refusal is not None and any(n.code == NOTE_DECLARED_ENTITY_KEY for n in x.notes)


# ----------------------------------------------------------------------------------------------------------------------------- her example: a plot that only counts

def test_her_example_a_plot_that_only_counts_drops_the_key_in_its_own_steps_and_still_draws():
    """D-0358: "we can have aggregations by count in a plot where the key does not matter". The key `sample_id` is dropped in the plot Pc's own steps (T3:Pc): allowed, and the
    plain-Polars replay builds every table and Pc still has the column it draws."""
    recipe, tables = counting_plot()
    walk = run(recipe, tables, "T3:Pc", "sample_id", kind="drop")
    pc = line(walk, "T3:Pc")
    assert pc.refusal is None and pc.state == "tick" and pc.consequences == ()          # Pc draws `country`, not `sample_id`
    replay = O.replay(O.with_audit_drop(recipe, "T3:Pc", "sample_id"), tables)
    assert replay.failures == {} and "sample_id" not in replay.end("T3:Pc").columns and "country" in replay.end("T3:Pc").columns
    assert replay.end("T3:P1") is not None and replay.end("T1:J").equals(O.replay(recipe, tables).end("T1:J"))     # nothing else moved


def test_the_same_plot_that_draws_the_key_is_told_it_cannot_be_drawn():
    recipe, tables = counting_plot()
    recipe = copy.deepcopy(recipe)
    recipe["analysis_groups"]["g"]["plots"]["Pc"]["mapping"] = {"x": "sample_id"}
    walk = run(recipe, tables, "T3:Pc", "sample_id", kind="drop")
    (c,) = line(walk, "T3:Pc").consequences
    assert (c.code, c.place, c.source, c.get("plot"), c.get("name")) == (PLOT_USES_COLUMN, "T3:Pc", FROM_READING, "Pc", "sample_id")
    replay = O.replay(O.with_audit_drop(recipe, "T3:Pc", "sample_id"), tables)
    assert "sample_id" not in replay.end("T3:Pc").columns                               # the oracle agrees: the column the plot draws is gone


# ----------------------------------------------------------------------------------------------------------------------------- what a drop breaks that is not a key

def test_a_non_key_column_that_a_plot_draws_is_not_refused_and_the_consequence_names_the_plot():
    recipe, tables = counting_plot()
    walk = run(recipe, tables, "T1:A", "country", kind="drop")
    assert walk.refused == 0 and line(walk, "T1:A").state == "tick"
    got = {(c.code, c.get("plot")) for c in line(walk, "T1:A").consequences}
    assert got == {(PLOT_USES_COLUMN, "Pc")}                                           # P1 draws `year`; only Pc draws `country`
    assert all(not x.consequences_checked for x in walk.lines)                          # no candidate plan: stated, never silent
    assert line(walk, "T3:Pc").consequences[0].place == "T3:Pc"


def test_a_non_key_column_that_a_later_step_names_is_not_refused_and_the_consequence_names_the_step():
    recipe, tables = later_steps()
    walk = run(recipe, tables, "T1:B", "lab", kind="drop")
    assert walk.refused == 0
    steps = [(c.code, c.step.node, c.step.step, c.step.action, c.source) for c in line(walk, "T1:B").consequences]
    assert steps == [(STEP_NAMES_COLUMN, "T2:J", 1, "polars_rename", FROM_READING)]
    assert [c.code for c in line(walk, "T1:J").consequences] == [STEP_NAMES_COLUMN] and line(walk, "T2:J").consequences == ()      # after the rename the column is `lab2`: nothing names it
    replay = O.replay(O.with_audit_drop(recipe, "T1:B", "lab"), tables)
    assert ("T2:J", 1) in replay.failures                                              # the oracle: the rename of `lab` fails exactly at that step
    assert not any(k[0] in ("T1:B", "T1:J") for k in replay.failures)


def test_without_a_candidate_plan_a_formula_that_uses_the_column_is_not_seen_and_it_is_said():
    """Only names are read (D-0356): a compute step that uses `lab` inside its formula is invisible to the readings. The line says `consequences_checked` False; the oracle shows
    the build fails (the thing the walk did not see)."""
    recipe, tables = later_steps(formula=True)
    walk = run(recipe, tables, "T1:B", "lab", kind="drop")
    x = line(walk, "T1:B")
    assert x.consequences == () and x.consequences_checked is False
    assert O.replay(O.with_audit_drop(recipe, "T1:B", "lab"), tables).failures                       # it would fail: the stated limit of the readings


def test_with_the_candidate_plan_the_formula_failure_is_found_with_the_engines_sentence():
    recipe, tables = later_steps(formula=True)
    walk = drop_walk(recipe, tables, "T1:B", "lab", with_candidates=True)
    x = line(walk, "T1:B")
    assert x.consequences_checked is True
    found = [(c.code, c.place, c.source) for c in x.consequences]
    assert (BUILD_FAILS, "T2:J", FROM_PLAN) in found                                    # the failing step is the compute step of tier 2 of J: the engine's own sentence is data
    sentence = next(c for c in x.consequences if c.code == BUILD_FAILS).get("sentence")
    assert "lab" in sentence
    assert [c for c in x.consequences if c.code == BUILD_FAILS and c.place == "T3:P"] == []     # the plot below is not listed again: one origin, not one per table below


def test_a_reading_the_candidate_plan_does_not_confirm_is_grey_with_both_facts():
    """A rename of `lab` with `strict: false` does not fail when `lab` is gone: the reading (a step names the column) and the plan (it builds) disagree, so the line is grey
    with the reading and the plan both in the reason (D-0351), never a guess."""
    recipe, tables = later_steps()
    recipe = copy.deepcopy(recipe)
    recipe["joins"]["J"]["tier2"]["steps"][0]["strict"] = False
    walk = drop_walk(recipe, tables, "T1:B", "lab", with_candidates=True)
    x = line(walk, "T1:B")
    assert x.state == "grey" and x.reason.code == CONSEQUENCE_DISAGREES
    assert [c.code for c in x.reason.get("reading")] == [STEP_NAMES_COLUMN] and x.reason.get("plan") == ()
    assert x.refusal is None


def test_a_plot_whose_table_loses_the_column_in_the_candidate_plan_is_reported_from_the_plan():
    """Pc draws `country` and has no step of its own: the candidate builds, the plot's table lacks the column, so the plan says what the reading said (and agrees: nothing grey)."""
    recipe, tables = counting_plot()
    recipe = copy.deepcopy(recipe)
    del recipe["analysis_groups"]["g"]["plots"]["Pc"]["tier3"]
    walk = drop_walk(recipe, tables, "T1:A", "country", with_candidates=True)
    x = line(walk, "T1:A")
    assert x.consequences_checked
    assert {(c.code, c.source, c.get("plot")) for c in x.consequences} == {(PLOT_USES_COLUMN, FROM_READING, "Pc"), (PLOT_USES_COLUMN, FROM_PLAN, "Pc")}
    assert x.state == "tick"                                                            # reading and plan agree: nothing grey


def test_a_step_of_the_plots_own_that_names_the_column_fails_in_the_candidate_plan_and_is_reported_as_a_build_failure():
    """Pc (with its own filter on `country`, a step the readings do not cover): the readings see the plot draw the column; the engine's plan of the candidate fails at the
    plot's own step and says so with its own sentence, and that is a BUILD_FAILS at T3:Pc, from the plan."""
    recipe, tables = counting_plot()
    walk = drop_walk(recipe, tables, "T1:A", "country", with_candidates=True)
    x = line(walk, "T1:A")
    fails = [c for c in x.consequences if c.code == BUILD_FAILS]
    assert [(c.place, c.source, c.get("node"), c.get("step")) for c in fails] == [("T3:Pc", FROM_PLAN, "T3:Pc", 1)] and (fails[0].step.node, fails[0].step.step) == ("T3:Pc", 1)
    assert "country" in fails[0].get("sentence")
    assert x.state == "tick"


def test_a_column_that_made_a_join_give_the_other_tables_column_a_suffix_says_that_column_is_renamed_back():
    """A and B both have `val`; the join calls B's `val_right`; a later step renames `val_right`. Dropping A's `val` makes the join keep B's column as `val`: the rename of
    `val_right` fails. The readings see it by the join's own suffix reading, the candidate plan agrees, the oracle fails exactly at that rename."""
    recipe, tables = next((r, t) for n, r, t in F.followed() if n == "join_default_suffix_then_rename")
    walk = drop_walk(recipe, tables, "T1:A", "val", with_candidates=True)
    x = line(walk, "T1:A")
    clash = [c for c in x.consequences if c.code == CLASH_NO_LONGER]
    assert [(c.source, c.get("name"), c.get("was_called"), c.get("table"), c.step.node, c.step.step) for c in clash] == [(FROM_READING, "val", "val_right", "B", "T1:J", 1)]
    assert x.state == "tick"                                                            # reading and plan agree
    assert any(c.code == BUILD_FAILS and c.get("step") == 2 for c in x.consequences)      # and the rename of `val_right` fails in the candidate plan
    failed, _ = _new_failures(recipe, tables, "T1:A", "val")
    assert ("T1:J", 2) in failed
    without = run(recipe, tables, "T1:B", "val", kind="drop")                           # B's own `val` is the other way round: the rename names its suffixed name
    assert [(c.code, c.step.step) for c in line(without, "T1:B").consequences] == [(STEP_NAMES_COLUMN, 2)]


def test_a_candidate_plan_is_for_a_drop_only():
    recipe, tables = F.chain()
    graph, plans = setup(recipe, tables)
    with pytest.raises(LineageError, match="for a drop"):
        LineageIndex(graph, plans).walk(Start("T1:A", "val"), levels=TIERS, kind="filter", candidates={})


def test_a_candidate_failure_that_the_recipe_already_has_is_not_a_consequence_of_the_drop():
    """The baseline fails at J (a join on a column the table lacks); dropping an unrelated column at A adds no consequence for J: only what the drop newly breaks is listed."""
    recipe, tables = F.chain()
    broken = copy.deepcopy(recipe)
    broken["joins"]["J"]["tier1"]["steps"][0]["on"] = "no_such_column"
    graph, plans = setup(broken, tables)
    first = LineageIndex(graph, plans).walk(Start("T1:A", "val"), levels=TIERS, kind="drop")
    cands = {x.place: O.replay(O.with_audit_drop(broken, x.place, "val"), tables).plans for x in first.lines if len(x.occurrences) == 1}
    walk = LineageIndex(graph, plans).walk(Start("T1:A", "val"), levels=TIERS, kind="drop", candidates=cands)
    assert [x.place for x in walk.lines if x.consequences] == []


# ----------------------------------------------------------------------------------------------------------------------------- places the column is already gone, and plans that fail

def test_a_place_where_the_column_is_already_gone_is_the_gone_note_and_the_table_does_not_change_for_a_drop():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.select("sample_id", "country", "year")])
    drop = run(recipe, tables, "DS:A", "val", kind="drop")
    filt = run(recipe, tables, "DS:A", "val", kind="filter")
    assert [(g.place, g.table_changes, g.step_kind) for g in drop.gone] == [("T1:A", False, "drop")] or all(not g.table_changes and g.step_kind == "drop" for g in drop.gone)
    assert drop.gone and all(g.table_changes for g in filt.gone)                        # a filter still removes rows there; a drop of a column that is not there changes nothing


def test_a_plan_failure_downstream_makes_the_line_grey_and_is_not_a_refusal_PROVISIONAL():
    """The engine could not give the plan of J: the walk cannot say whether a later join needs the column. The line is grey with the engine's sentence; the gate
    (`key_drop`) does not refuse it (the build would say, an error and never a silent result)."""
    recipe, tables = F.chain()
    graph, plans = setup(recipe, tables)
    book = {(n, k): plans.get(n, k) for n in graph.nodes() for k in range(len(graph.node(n).steps) + 1)}
    for k in (1,):
        book[("T1:J", k)] = "the engine could not plan this join"
    for n in ("T2:J", "T3:P1"):
        book[(n, 0)] = "the engine could not plan this join"
    walk = LineageIndex(graph, PlanBook.of(book)).walk(Start("T1:A", "val"), levels=TIERS, kind="drop")
    x = line(walk, "T1:A")
    assert x.state == "grey" and x.refusal is None and x.reason.code == PLAN_FAILED and "could not plan" in x.reason.get("sentence")


# ----------------------------------------------------------------------------------------------------------------------------- I6: the proof against plain Polars, on every column of every fixture

def _new_failures(recipe, tables, place, column):
    base = O.replay(recipe, tables).failures
    after = O.replay(O.with_audit_drop(recipe, place, column), tables)
    return {k: v for k, v in after.failures.items() if k not in base}, after


def _walks() -> Iterator[Tuple[str, str, str, Any, Any, Any]]:
    for name, recipe, tables in fixtures():
        graph, plans = setup(recipe, tables)
        for node in graph.nodes():
            plan = plans.get(node, len(graph.node(node).steps))
            if not hasattr(plan, "names"):
                continue
            for column in plan.names:
                yield name, node, column, recipe, tables, drop_walk(recipe, tables, node, column)


# the actions whose arguments the walk reads (D-0351, `step_effects.READINGS`) and a join (judged by the key rule): a failure the readings did not report is never at one of them
READ_ACTIONS = {"polars_rename", "polars_drop", "polars_select", "polars_cast", "polars_group_by", "polars_join"}


def _origins(recipe, failed):
    """The (node, step) where each failing node first fails (the step that raised, not the nodes below it that inherit the failure)."""
    first = {}
    for (node, k), _ in sorted(failed.items(), key=lambda x: (x[0][0], x[0][1])):
        first.setdefault(node, k)
    return {node: k for node, k in first.items() if k > 0}          # a node that fails from its start inherits the failure of the table above it


def _step_at(recipe, node, k):
    """The step `k` (1-based) of a node of the recipe as written, or None (k = 0: the node's own start, inherited from above)."""
    tier, name = node.split(":", 1)
    if k == 0 or tier == "DS":
        return None
    if tier == "T3":
        body = next(e for g in recipe["analysis_groups"].values() for pid, e in g["plots"].items() if pid == name)
        return body.get("tier3", {}).get("steps", [])[k - 1]
    body = (recipe.get("data_schemas") or {}).get(name) or (recipe.get("joins") or {}).get(name)
    return body.get("tier1" if tier == "T1" else "tier2", {}).get("steps", [])[k - 1]


def test_I6_a_tickable_drop_without_a_reported_consequence_builds_and_a_refusal_fails_at_its_join():
    """For every column of every fixture, with no candidate plan: a line that is tickable (not refused, not grey) and reports no consequence builds when the drop is written
    there, EXCEPT where a later step the readings do not cover names the column (a filter on it, a formula that uses it): then the failure is at such a step and never at a
    step the readings cover, which is the stated limit (`consequences_checked` False; the candidate plan sees it, next test). A refused line fails, at the join it names."""
    checked = refused = built = unseen = 0
    for name, node, column, recipe, tables, walk in _walks():
        for x in walk.lines:
            if len(x.occurrences) != 1 or x.tier == "DS":
                continue
            name_here = x.occurrences[0].name
            failed, after = _new_failures(recipe, tables, x.place, name_here)
            if x.refusal is not None:
                refused += 1
                need_nodes = {n.step.node for n in x.refusal.get("needs")}
                assert any(k[0] in need_nodes for k in failed), (name, x.place, name_here, failed)
            elif x.state == "tick" and not x.consequences:
                if not failed:
                    built += 1
                else:
                    unseen += 1
                    for origin_node, k in _origins(recipe, failed).items():
                        step = _step_at(recipe, origin_node, k)
                        assert step is not None and step["action"] not in READ_ACTIONS, (name, x.place, name_here, origin_node, k, step)
            checked += 1
    assert checked > 150 and refused >= 8 and built > 100 and unseen >= 4, (checked, refused, built, unseen)       # the loop ran, and it met the limit it describes


def test_I6_a_reported_consequence_fails_or_loses_the_plots_column_exactly_there():
    seen = 0
    for name, node, column, recipe, tables, walk in _walks():
        for x in walk.lines:
            if len(x.occurrences) != 1 or x.tier == "DS" or x.refusal is not None:
                continue
            name_here = x.occurrences[0].name
            failed, after = _new_failures(recipe, tables, x.place, name_here)
            for c in x.consequences:
                seen += 1
                if c.code == STEP_NAMES_COLUMN:
                    assert (c.step.node, c.step.step) in failed or any(k[0] == c.step.node for k in failed), (name, x.place, c)
                elif c.code == PLOT_USES_COLUMN:
                    end = after.end(c.get("node"))
                    assert end is None or c.get("name") not in end.columns, (name, x.place, c)
                elif c.code == CLASH_NO_LONGER:
                    columns = after.frames[(c.step.node, c.step.step)].columns         # the table right after the join step: the right table's column keeps its own name
                    assert c.get("name") in columns and c.get("was_called") not in columns, (name, x.place, c)
    assert seen > 20


def test_I6_with_the_candidate_plan_every_tickable_line_builds_and_every_failure_is_reported():
    """The same fixtures with the candidate plans (the oracle's replay of each candidate): now the formula fixture is caught too. Every tickable line without a consequence
    builds; every line whose candidate fails somewhere new reports a BUILD_FAILS or a refusal or a grey; a grey from `consequence_disagrees` carries both facts."""
    lines = silent = 0
    for name, recipe, tables in fixtures():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        for node in graph.nodes():
            plan = plans.get(node, len(graph.node(node).steps))
            if not hasattr(plan, "names"):
                continue
            for column in plan.names[:3]:                                                  # a bounded sample per node keeps the replay count small
                first = index.walk(Start(node, column), levels=TIERS, kind="drop")
                walk = index.walk(Start(node, column), levels=TIERS, kind="drop", candidates=candidates(recipe, tables, first))
                for x in walk.lines:
                    if len(x.occurrences) != 1 or x.tier == "DS":
                        continue
                    failed, _ = _new_failures(recipe, tables, x.place, x.occurrences[0].name)
                    lines += 1
                    assert x.consequences_checked
                    if x.refusal is None and x.state == "tick" and not x.consequences:
                        silent += 1
                        assert not failed, (name, x.place, x.occurrences[0].name, failed)
                    if failed and x.refusal is None:
                        assert any(c.code == BUILD_FAILS for c in x.consequences) or x.state == "grey", (name, x.place, x.occurrences[0].name, failed)
    assert lines > 100 and silent > 50


# ----------------------------------------------------------------------------------------------------------------------------- the walk and the gate are one rule (L029)

def test_L029_the_walk_and_add_step_agree_on_every_place_of_every_fixture():
    """The walk of a drop and the gate of the audit copy (`add_step`, names-only plan) give the same verdict at every place of every column of every fixture whose steps are all
    read: a line is refused exactly when `add_step` refuses its step for the key. A wrong walk that re-implements the rule (a refusal by name, a second rule) fails here."""
    from utils.audit_copy import AuditCopyError, add_step, start_audit
    compared = 0
    for name, node, column, recipe, tables, walk in _walks():
        for x in walk.lines:
            if len(x.occurrences) != 1 or x.tier == "DS":
                continue
            audit = start_audit(recipe, "1a2b3c4d")
            try:
                add_step(audit, x.place, {"action": "polars_drop", "columns": [x.occurrences[0].name]}, "why")
                gate_refuses = False
            except AuditCopyError as error:
                assert "is read as a join key by" in str(error), (name, x.place, str(error))
                gate_refuses = True
            assert gate_refuses == (x.refusal is not None), (name, node, column, x.place, x.occurrences[0].name)
            compared += 1
    assert compared > 150


def test_a_key_that_a_join_reads_only_through_a_link_the_plan_contradicts_is_grey_not_refused_PROVISIONAL():
    """J reads `lab` (which came from B) as the key of its second join. The plan of the first join contradicts the reading (a type differs), so the walk cannot prove that B's
    `lab` is the column the second join reads: the line is grey with the reason, the need is listed as uncertain, and the gate does not refuse (the build would say)."""
    recipe, tables = two_joins()
    graph, plans = setup(recipe, tables)
    book = {(n, k): plans.get(n, k) for n in graph.nodes() for k in range(len(graph.node(n).steps) + 1)}
    after = book[("T1:J", 1)]
    book[("T1:J", 1)] = type(after).of((name, "Int64" if name == "val" else kind) for name, kind in after.columns)      # the plan says `val` is a number: the reading expects a string
    index = LineageIndex(graph, PlanBook(book))
    facts = index.drop_facts("T1:B", "lab")
    maybe = [(n.step.node, n.step.step, n.side, n.certain) for n in facts.needs]
    assert ("T1:J", 2, "base", False) in maybe and not facts.refused and facts.uncertain
    x = line(index.walk(Start("T1:B", "lab"), levels=TIERS, kind="drop"), "T1:B")
    assert x.refusal is None and x.state == "grey" and x.reason.get("node") == "T1:J" and x.reason.get("step") == 2
