"""The semi join is FOLLOWED like inner and left (D-0486; the study of D-0452, `tmpAI/coordinator/lineage_semi_join/REPORT.md`, four additions).

Owner, D-0486: "Well if build and correctly tested then should not the test detect mistakes ? the agents need to build tests - and yes needs own documentation limits. So its A".

What a semi join does (proved here on the real engine, Polars, by the oracle of the lineage tests, never by the reading of the walk): it keeps the rows of the first
table that have a match in the second table, keeps ONLY the first table's columns, never duplicates a row (a key twice in the second table gives the row once), renames
nothing (no suffix). A row removed at the SECOND table removes the matching rows of the result: the opposite of a left join, where the row stays and its copied cells
become empty. So the second table's key is one column with the first table's key (linked both ways, as for an inner join); the second table's other columns do not exist after
the join (they end there as `Gone`, certainly).

The four additions, each seen failing when removed (mutation index in the report):
 1. `step_effects.FOLLOWED_JOINS` holds `semi`;
 2. `step_effects.predict` copies no column of the second table for a join of `NO_COPY_JOINS`;
 3. `LineageIndex._read_links` ends the second table's non-key columns at the join as certainly gone (`Gone`), not as a grey "cannot follow";
 4. the same-name warning (`clash_no_longer`) only for kinds that copy columns.

The limits (`test_the_limits_...`): what the app does NOT follow around a semi join is untraceable with its reason, and the tests say so.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_semi_join.py -q
"""
import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import run, setup

from utils import action_names, step_effects as fx
from utils.lineage_records import CLASH_NO_LONGER, JOIN_NOT_YET_FOLLOWED, Start
from utils.lineage_walk import LineageIndex
from utils.plan_book import Plan, PlanBook

IDS_A = ["S1", "S2", "S2", "S3", "S4"]


def line(walk, place):
    return next(x for x in walk.lines if x.place == place)


def semi(how="semi", b_steps=(), a_steps=(), on="sample_id", **extra):
    """A(sample_id with S2 twice, country, val), B(sample_id with S2 twice and a key A does not have, lab, val); J = A semi B; P reads J and Pb reads B."""
    recipe = F.recipe({"A": F.schema(["sample_id", "country", "val"], a_steps, keys=["sample_id"]), "B": F.schema(["sample_id", "lab", "val"], b_steps, keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=on, how=how, **extra)])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=IDS_A, country=["NO", "SE", "NO", "SE", "NO"], val=["a1", "a2", "a3", "a4", "a5"]),
              "B": F.table(sample_id=["S1", "S2", "S2", "S3", "S9"], lab=["X", "Y", "Z", "Q", "R"], val=["b1", "b2", "b3", "b4", "b5"])}
    return recipe, tables


# ----------------------------------------------------------------------------------------------------------------------------- the engine, not the reading

def test_polars_semi_keeps_only_the_first_tables_columns_never_duplicates_a_row_and_renames_nothing():
    recipe, tables = semi()
    joined = O.replay(recipe, tables).end("T1:J")
    assert joined.columns == ["sample_id", "country", "val"]                               # no `lab`, no `val_right`: the second table's columns are not copied, nothing is renamed
    assert joined["sample_id"].to_list() == ["S1", "S2", "S2", "S3"]                       # S4 has no match; S2 twice in B did not double A's two S2 rows
    assert joined["val"].to_list() == ["a1", "a2", "a3", "a4"]                              # the values are the first table's own


def test_a_row_removed_at_the_second_table_removes_the_matching_rows_of_the_result_unlike_a_left_join():
    recipe, tables = semi(b_steps=[F.keep("sample_id", "ne", "S3")])
    after = O.replay(recipe, tables).end("T1:J")
    assert after["sample_id"].to_list() == ["S1", "S2", "S2"]                              # S3 had its only match in B: its row is gone from the result
    left, _ = semi("left", b_steps=[F.keep("sample_id", "ne", "S3")])
    kept = O.replay(left, tables).end("T1:J")
    assert "S3" in kept["sample_id"].to_list() and kept.filter(kept["sample_id"] == "S3")["lab"].to_list() == [None]      # the opposite: the row stays, its copied cell is empty


def test_one_of_two_matching_rows_removed_at_the_second_table_removes_nothing():
    recipe, tables = semi(b_steps=[F.keep("lab", "ne", "Y")])                                 # S2 keeps its other match (lab Z)
    assert O.replay(recipe, tables).end("T1:J")["sample_id"].to_list() == ["S1", "S2", "S2", "S3"]


def test_a_row_removed_at_the_first_table_removes_it_from_the_result():
    recipe, tables = semi(a_steps=[F.keep("sample_id", "ne", "S1")])
    assert O.replay(recipe, tables).end("T1:J")["sample_id"].to_list() == ["S2", "S2", "S3"]


# ----------------------------------------------------------------------------------------------------------------------------- the walk follows it (addition 1 and 2)

def test_the_semi_join_is_a_read_join_that_copies_nothing():
    effect = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "sample_id", "how": "semi"})
    assert effect.kind == fx.JOIN and effect.how == "semi" and "semi" in fx.FOLLOWED_JOINS and fx.NO_COPY_JOINS == ("semi",)
    before, right = Plan.of([("sample_id", "String"), ("country", "String")]), Plan.of([("sample_id", "String"), ("lab", "String"), ("country", "String")])
    names = [p.name for p in fx.predict(effect, before, right)]
    assert names == ["sample_id", "country"]                                                   # lab and the clashing country of the second table are not copied
    inner = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "sample_id", "how": "inner"})
    assert [p.name for p in fx.predict(inner, before, right)] == ["sample_id", "country", "lab", "country_right"]      # the other followed kinds copy them


def test_a_column_of_the_first_table_is_the_same_column_after_the_join_with_no_note():
    recipe, tables = semi()
    for column in ("country", "val"):
        walk = run(recipe, tables, "T1:A", column)
        assert [(x.place, x.state, x.reason, x.notes) for x in walk.lines] == [("T1:A", "tick", None, ()), ("T1:J", "tick", None, ()), ("T3:P", "tick", None, ())], column
        assert [o.name for x in walk.lines for o in x.occurrences] == [column] * 3 and walk.gone == ()          # val keeps its name: no suffix, no clash


def test_the_key_is_one_column_in_both_tables_linked_both_ways_and_the_hop_says_semi():
    recipe, tables = semi()
    for node in ("T1:A", "T1:B"):
        walk = run(recipe, tables, node, "sample_id")
        assert {x.place: x.state for x in walk.lines} == {"T1:A": "tick", "T1:B": "tick", "T1:J": "tick", "T3:P": "tick", "T3:Pb": "tick"}, node
        hop = line(walk, "T1:J").occurrences[0].steps[0]
        assert (hop.join_how, hop.name_before, hop.name_after) == ("semi", "sample_id", "sample_id") and hop.join_side in ("base", "right")
        assert {s.table for s in line(walk, "T1:J").occurrences[0].sources} == {"A", "B"}              # two source columns met in the key


def test_a_key_under_another_name_in_the_second_table_is_followed_to_its_name():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"]), "B": F.schema(["isolate", "lab"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"), how="semi")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"]), "B": F.table(isolate=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T1:B", "isolate")
    assert [(x.place, x.state, x.occurrences[0].name) for x in walk.lines] == [("T1:A", "tick", "sample_id"), ("T1:B", "tick", "isolate"), ("T1:J", "tick", "sample_id"), ("T3:P", "tick", "sample_id")]


def test_a_composite_key_links_every_key_column():
    recipe = F.recipe({"A": F.schema(["sample_id", "year", "country"], keys=["sample_id"]), "B": F.schema(["sample_id", "year", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=["sample_id", "year"], how="semi")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2"], year=["2022", "2023"], country=["NO", "SE"]), "B": F.table(sample_id=["S1"], year=["2022"], lab=["X"])}
    assert all(x.state == "tick" for x in run(recipe, tables, "T1:B", "year").lines)
    assert all(x.state == "tick" for x in run(recipe, tables, "T1:B", "sample_id").lines)


# ----------------------------------------------------------------------------------------------------------------------------- the second table's columns end there (addition 3)

def test_a_column_of_the_second_table_does_not_exist_after_the_join_and_the_walk_says_where_it_went():
    recipe, tables = semi()
    walk = run(recipe, tables, "T1:B", "lab")
    assert [(x.place, x.state) for x in walk.lines] == [("T1:B", "tick"), ("T3:Pb", "tick")]       # the other table the lab reaches is B's own plot
    assert [g.place for g in walk.gone] == ["T1:J", "T3:P"]
    for gone in walk.gone:
        assert gone.removed_by.action == action_names.JOIN and gone.removed_by.node == "T1:J" and gone.removed_by.step == 1       # certain: "gone at this join step", never "cannot follow"
    assert not any(x.reason is not None and x.reason.code == "cannot_follow" for x in walk.lines)


def test_a_column_of_the_second_table_with_the_same_name_as_one_of_the_first_stays_two_columns():
    recipe, tables = semi()
    from_b = run(recipe, tables, "T1:B", "val")                                              # B's `val` is NOT the `val` of J: J's `val` is A's
    assert [x.place for x in from_b.lines] == ["T1:B", "T3:Pb"] and [g.place for g in from_b.gone] == ["T1:J", "T3:P"]
    from_a = run(recipe, tables, "T1:A", "val")
    assert "T1:B" not in [x.place for x in from_a.lines]                                      # and A's `val` does not reach B


def test_the_marker_put_in_a_column_arrives_where_the_walk_ticks_and_nowhere_else():
    recipe, tables = semi()
    for sid, column in (("A", "country"), ("B", "lab"), ("B", "val")):
        marked = O.replay(recipe, O.marked(tables, {sid: [column]}))
        walk = LineageIndex(*setup(recipe, tables)).walk(Start(f"DS:{sid}", column), levels=("T1", "T2", "T3"))
        ticked = {n for x in walk.lines if x.state == "tick" for n in x.covers}
        holders = {nid for (nid, _k) in marked.frames if not nid.startswith("DS:") and marked.end(nid) is not None and O.holds_mark(marked.end(nid))}
        assert holders == ticked & {nid for (nid, _k) in marked.frames if not nid.startswith("DS:")}, (sid, column, holders, ticked)        # both ways: every ticked table holds it, every table that holds it is ticked
        assert ("T1:J" in holders) == (sid == "A"), (sid, column)                                        # the mark of the second table never reaches the result


# ----------------------------------------------------------------------------------------------------------------------------- the same-name warning (addition 4)

def test_dropping_a_column_that_has_a_namesake_in_the_second_table_warns_of_a_clash_only_for_kinds_that_copy():
    for how, expected in (("inner", True), ("left", True), ("semi", False)):
        recipe, tables = semi(how)
        walk = run(recipe, tables, "T1:A", "val", kind="drop")
        codes = {c.code for x in walk.lines for c in x.consequences}
        assert (CLASH_NO_LONGER in codes) is expected, (how, codes)


# ----------------------------------------------------------------------------------------------------------------------------- the limits: what is NOT followed around a semi join

def test_the_limits_a_semi_join_whose_second_table_is_not_followed_is_red_behind_the_unfollowed_step():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"]), "C": F.schema(["sample_id", "x"], keys=["sample_id"])},
                      {"J2": F.join(["B", "C"], [F.join_step("C", how="anti")]), "J": F.join(["A", "J2"], [F.join_step("J2", how="semi")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"]), "B": F.table(sample_id=["S1", "S2"], lab=["X", "Y"]), "C": F.table(sample_id=["S2"], x=["q"])}
    followed = run(recipe, tables, "T1:A", "country")
    assert [(x.place, x.state) for x in followed.lines] == [("T1:A", "tick"), ("T1:J", "tick"), ("T3:P", "tick")]     # the path of A does not cross the anti join
    walk = run(recipe, tables, "T1:B", "sample_id")
    red = {x.place: x for x in walk.lines if x.state == "grey"}
    assert {"T1:J2", "T1:J", "T1:A", "T3:P"} <= set(red)
    for place in ("T1:J2", "T1:J", "T3:P", "T1:A"):
        reason = red[place].reason
        assert reason.code == JOIN_NOT_YET_FOLLOWED and reason.get("kind") == "anti" and reason.get("node") == "T1:J2"      # the reason is the anti join, not the semi join that follows it


def test_the_limits_a_semi_join_of_a_table_with_itself_is_red():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"])}, {"J": F.join(["A", "A"], [F.join_step("A", how="semi")])}, {"P": F.plot("J")})
    walk = run(recipe, {"A": F.table(sample_id=["S1"], country=["NO"])}, "T1:A", "country")
    reason = line(walk, "T1:J").reason
    assert line(walk, "T1:J").state == "grey" and reason.code == JOIN_NOT_YET_FOLLOWED and reason.get("self_join") is True and reason.get("kind") == "semi"


def test_the_limits_a_semi_join_on_conditions_is_not_read_and_the_second_tables_columns_are_untraceable():
    """`modif_join_where` (a join on conditions, no key equality) is outside the readings, whatever the kind: the walk cannot say what the conditions keep. The columns of the second
    table are grey (`cannot_follow`: no trace is made); a column of the first table passes by the plan alone with the note `unread_step_passed` (the rule for every step the walk does not read; D-0473
    decides later how the dialog treats a value filter there). The plan is written by hand: the oracle runs `polars_join` only."""
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [{"action": action_names.JOIN_WHERE, "right_ingredient": "B", "predicates": ["pl.col('sample_id') == pl.col('sample_id_right')"], "how": "semi"}])},
                      {"P": F.plot("J")})
    both = [("sample_id", "String"), ("country", "String")]
    entries = {("DS:A", 0): Plan.of(both), ("T1:A", 0): Plan.of(both), ("T1:A", 1): Plan.of(both), ("T2:A", 0): Plan.of(both),
               ("DS:B", 0): Plan.of([("sample_id", "String"), ("lab", "String")]), ("T1:B", 0): Plan.of([("sample_id", "String"), ("lab", "String")]),
               ("T1:B", 1): Plan.of([("sample_id", "String"), ("lab", "String")]), ("T2:B", 0): Plan.of([("sample_id", "String"), ("lab", "String")]),
               ("T1:J", 0): Plan.of(both), ("T1:J", 1): Plan.of(both), ("T2:J", 0): Plan.of(both), ("T3:P", 0): Plan.of(both)}
    from utils.recipe_graph import build_graph
    index = LineageIndex(build_graph(recipe), PlanBook.of(entries))
    first = index.walk(Start("T1:A", "country"), levels=("T1", "T3"))
    assert [(x.place, x.state) for x in first.lines] == [("T1:A", "tick"), ("T1:J", "tick"), ("T3:P", "tick")] and line(first, "T1:J").notes[0].code == "unread_step_passed"
    second = index.walk(Start("T1:B", "lab"), levels=("T1", "T3"))
    assert not any(x.state == "tick" for x in second.lines if x.place in ("T1:J", "T3:P"))
    assert all(x.state == "grey" and x.reason.code == "cannot_follow" for x in second.lines if x.place in ("T1:J", "T3:P"))      # no trace is made for the second table of a step the walk does not read


def test_the_limits_a_semi_join_without_readable_keys_is_not_read():
    for step in ({"action": action_names.JOIN, "right_ingredient": "B", "how": "semi"}, {"action": action_names.JOIN, "how": "semi", "on": "k"}):
        effect = fx.effect_of(step)
        assert effect.kind == fx.UNREAD and effect.why
