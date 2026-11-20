"""The lineage walk follows a column through a change of NAME (step 2) and through a change of TYPE or VALUES under the same name (step 3), and says
what it found when it found nothing (LBFB round 2). Cases are named with their number in `tmpAI/panel/lineage_tests/DESIGN.md`; a test that says
`PROVISIONAL` states what the walk does while the owner has not decided.

The decisive proof is the marker check (`test_the_mark_put_in_a_source_column_arrives_in_the_column_the_walk_names_at_every_ticked_place`): a marked value
put in a source column is replayed by plain Polars, and the column the walk names at a ticked place must hold it. That is what "the same column" means.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_walk_follow.py -q
"""
import copy

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import TIERS, places, run, setup, ticked

from utils.lineage_records import (
    NO_PLACE_AT_THE_LEVELS, NO_STEP_LIST, NOTE_AGGREGATED, NOTE_ANOTHER_TYPE, NOTE_ONE_ROW_PER_GROUP, NOTE_RECOMPUTED, PLAN_FAILED, READING_DISAGREES,
    SEVERAL_COLUMNS, STEP_NOT_READ, VALUE_NOTES, JOIN_LINKED, Reach, SortedSet, Start,
)
from utils.lineage_walk import LineageIndex, _Dead
from utils.plan_book import Plan, PlanBook

ALL = ("source", "T1", "T2", "T3")


def line(walk, place):
    return next(x for x in walk.lines if x.place == place)


def names(walk):
    return [(x.place, x.occurrences[0].name if x.occurrences else None) for x in walk.lines]


# ----------------------------------------------------------------------------------------------------------------------------- B. a change of name

def test_L015_a_rename_in_the_middle_of_a_tier_is_followed_both_ways():
    recipe = F.recipe({"A": F.schema(["sample_id", "country", "lab"], [F.keep("lab", "ne", "Z"), F.rename(country="origin"), F.keep("lab", "ne", "Y")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"], lab=["X"])}
    forward = run(recipe, tables, "DS:A", "country")
    assert names(forward) == [("T1:A", "origin"), ("T3:P", "origin")] and ticked(forward) == places(forward)
    backward = run(recipe, tables, "T3:P", "origin", levels=ALL)
    assert names(backward) == [("DS:A", "country"), ("T1:A", "origin"), ("T3:P", "origin")]
    hop = line(backward, "T1:A").occurrences[0].steps[0]
    assert (hop.step.node, hop.step.step, hop.name_before, hop.name_after, hop.how) == ("T1:A", 2, "country", "origin", "renamed")


def test_L017_a_clash_resolved_by_the_default_suffix_then_renamed_is_one_column_named_as_in_each_table():
    recipe, tables = F.followed()[4][1:]
    walk = run(recipe, tables, "T3:P", "val_b")
    assert names(walk) == [("T1:B", "val"), ("T1:J", "val_b"), ("T3:P", "val_b")] and ticked(walk) == places(walk)
    assert [h.name_after for h in line(walk, "T3:P").occurrences[0].steps] == ["val_right", "val_b"]       # the suffix, then the author's rename: both in the way
    left = run(recipe, tables, "T3:P", "val")
    assert names(left) == [("T1:A", "val"), ("T1:J", "val"), ("T3:P", "val")]                              # A's val: B's is another column


def test_L020_names_are_compared_exactly_a_case_only_difference_is_another_column():
    recipe = F.recipe({"A": F.schema(["sample_id", "Country"]), "B": F.schema(["sample_id", "country"])}, {}, {"Pa": F.plot("A"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"], Country=["NO"]), "B": F.table(sample_id=["S1"], country=["SE"])}
    assert names(run(recipe, tables, "T3:Pa", "Country")) == [("T1:A", "Country"), ("T3:Pa", "Country")]
    assert names(run(recipe, tables, "T3:Pb", "country")) == [("T1:B", "country"), ("T3:Pb", "country")]


def test_L021_a_key_renamed_after_the_join_is_followed_back_to_the_key_of_the_other_table():
    recipe = F.recipe({"A": F.schema(["sample_id"], keys=["sample_id"]), "B": F.schema(["isolate", "lab"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"))], [F.rename(sample_id="id")])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    tables = {"A": F.table(sample_id=["S1"]), "B": F.table(isolate=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T3:P", "id")
    assert names(walk) == [("T1:A", "sample_id"), ("T1:B", "isolate"), ("T1:J", "sample_id"), ("T2:J", "id"), ("T3:P", "id"), ("T3:Pb", "isolate")] and ticked(walk) == places(walk)


def test_L023_the_suffix_the_step_gives_is_the_suffix_followed_not_a_fixed_one():
    recipe, tables = F.followed()[3][1:]
    walk = run(recipe, tables, "T1:J", "val_b")
    assert names(walk) == [("T1:B", "val"), ("T1:J", "val_b"), ("T2:J", "val_b"), ("T3:P", "val_b"), ("T3:Pb", "val")] and ticked(walk) == places(walk)
    default_suffix = copy.deepcopy(recipe)
    default_suffix["joins"]["J"]["tier1"]["steps"][0].pop("suffix")                                       # the same recipe with the default suffix: `val_b` no longer exists
    with pytest.raises(Exception):
        run(default_suffix, tables, "T1:J", "val_b")


def test_L019_the_swap_of_three_names_in_one_step_is_followed_by_the_mapping():
    recipe = F.recipe({"A": F.schema(["a", "b", "c"], [F.rename(a="b", b="c", c="a")])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(a=["x"], b=["y"], c=["z"])}
    assert names(run(recipe, tables, "DS:A", "a")) == [("T1:A", "b"), ("T3:P", "b")]
    assert names(run(recipe, tables, "DS:A", "c")) == [("T1:A", "a"), ("T3:P", "a")]
    replay = O.replay(recipe, tables).end("T1:A")
    assert replay["b"].to_list() == ["x"] and replay["a"].to_list() == ["z"]                               # the oracle agrees: the old `a` is the new `b`


def test_a_reading_the_plan_contradicts_is_grey_with_both_facts_never_followed():
    recipe = F.recipe({"A": F.schema(["a", "b"], [F.rename(a="c")])}, {}, {"P": F.plot("A")})
    both = [("a", "Int64"), ("b", "Int64")]
    graph = setup(recipe, {"A": F.table(a=[1], b=[2])})[0]
    plans = PlanBook.of({("DS:A", 0): both, ("T1:A", 0): both, ("T1:A", 1): both, ("T2:A", 0): both, ("T3:P", 0): both})      # the rename did not happen, says the plan
    walk = LineageIndex(graph, plans).walk(Start("DS:A", "a"), levels=TIERS)
    assert [(x.place, x.state) for x in walk.lines] == [("T1:A", "grey"), ("T3:P", "grey")] and all(x.reason.code == READING_DISAGREES for x in walk.lines)
    problem = line(walk, "T1:A").reason.get("problem")
    assert "['c']" in problem and "['a']" in problem                                                      # the reading expected `c`; the plan has `a` instead


def test_a_join_of_another_kind_is_not_followed_and_says_why_PROVISIONAL():
    recipe = F.recipe({"A": F.schema(["sample_id", "val"]), "B": F.schema(["isolate", "lab"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"), how="right")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], val=["a"]), "B": F.table(isolate=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T3:P", "lab")
    assert [(x.place, x.state) for x in walk.lines] == [("T1:B", "grey"), ("T1:J", "tick"), ("T3:P", "tick")]     # the start is after the join: only the table before it is in doubt
    assert line(walk, "T1:B").reason.code == STEP_NOT_READ and "right" in line(walk, "T1:B").reason.get("why")


def test_a_table_joined_with_itself_keeps_two_columns_grey_PROVISIONAL():
    recipe = F.recipe({"A": F.schema(["sample_id", "val"], keys=["sample_id"])}, {"J": F.join(["A", "A"], [F.join_step("A")])}, {"P": F.plot("J")})
    walk = run(recipe, {"A": F.table(sample_id=["S1"], val=["a"])}, "T3:P", "val")
    assert any(x.reason is not None and x.reason.code == SEVERAL_COLUMNS for x in walk.lines)


# ----------------------------------------------------------------------------------------------------------------------------- C. a change of type or values

def test_L036_a_cast_on_one_path_only_is_offered_with_the_type_before_and_after():
    recipe = F.recipe({"A": F.schema(["sample_id", "year"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B")], [F.cast(["year"], "String")])}, {"Pc": F.plot("J"), "Pi": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1", "S2"], year=[2022, 2023]), "B": F.table(sample_id=["S1", "S2"], lab=["X", "Y"])}
    walk = run(recipe, tables, "T3:Pi", "year")
    assert places(walk) == ["T1:A", "T1:J", "T2:J", "T3:Pc", "T3:Pi"] and ticked(walk) == places(walk)
    assert [(x.place, x.occurrences[0].type) for x in walk.lines] == [("T1:A", "Int64"), ("T1:J", "Int64"), ("T2:J", "String"), ("T3:Pc", "String"), ("T3:Pi", "Int64")]
    assert [n.code for n in line(walk, "T1:A").notes] == [] and [n.code for n in line(walk, "T1:J").notes] == []
    for place in ("T2:J", "T3:Pc"):
        note = line(walk, place).notes[0]
        assert note.code == NOTE_ANOTHER_TYPE and (dict(note.params)["type_before"], dict(note.params)["type_after"], dict(note.params)["node"]) == ("Int64", "String", "T2:J")
    assert walk.start_type == "Int64"


def test_L039_a_round_trip_through_another_type_is_one_column_two_notes():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], [F.cast(["country"], "Categorical")], [F.cast(["country"], "String")], keys=["sample_id"])}, {}, {"P": F.plot("A")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"])}
    walk = run(recipe, tables, "T3:P", "country")
    assert [(x.place, x.occurrences[0].type, x.state) for x in walk.lines] == [("T1:A", "Categorical", "tick"), ("T2:A", "String", "tick"), ("T3:P", "String", "tick")]
    assert [n.code for n in line(walk, "T1:A").notes] == [NOTE_ANOTHER_TYPE] and dict(line(walk, "T1:A").notes[0].params)["direction"] == "backward"
    assert line(walk, "T2:A").notes == () and line(walk, "T3:P").notes == ()


def test_a_cast_to_the_type_the_column_has_gives_the_hop_and_no_note_PROVISIONAL():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.cast(["year"], "Int64")])
    walk = run(recipe, tables, "DS:A", "year")
    assert ticked(walk) == places(walk) and all(x.notes == () for x in walk.lines)
    assert line(walk, "T1:A").occurrences[0].steps[0].how == "cast" and line(walk, "T1:A").occurrences[0].steps[0].type_before == "Int64"


def test_L030_a_compute_step_that_writes_a_new_name_is_a_new_column_and_the_named_one_is_recomputed():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.with_columns(era="pl.col('year') > 2022", year="pl.col('year') + 1")])
    new = run(recipe, tables, "T3:P2", "era")
    assert names(new) == [("T1:A", "era"), ("T1:J", "era"), ("T3:P1", "era"), ("T3:P2", "era")] and line(new, "T1:A").occurrences[0].how == "created"
    assert line(new, "T1:A").occurrences[0].sources == ()                                                    # a column made by the step has no source column
    old = run(recipe, tables, "DS:A", "year")
    assert [n.code for n in line(old, "T1:A").notes] == [NOTE_RECOMPUTED] and "era" not in [o.name for x in old.lines for o in x.occurrences]


def test_L031_the_aggregate_that_changes_its_name_is_a_new_column_and_the_old_one_is_gone():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.group_by(["sample_id", "year"], val_mean="pl.col('val').mean()")])
    mean = run(recipe, tables, "T3:P1", "val_mean")
    assert names(mean) == [("T1:A", "val_mean"), ("T1:J", "val_mean"), ("T3:P1", "val_mean"), ("T3:P2", "val_mean")] and line(mean, "T1:A").occurrences[0].how == "created"
    old = run(recipe, tables, "DS:A", "val")
    assert old.lines == () and {g.place for g in old.gone} == {"T1:A", "T1:J", "T3:P1", "T3:P2"}            # `val` is not a group column and not an aggregate: gone (the filter step before it is above)
    assert {g.removed_by.action for g in old.gone} == {"polars_group_by"}


def test_L031_a_group_key_keeps_its_name_and_says_the_rows_are_groups_after_the_step():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.group_by(["sample_id", "year"], val="pl.col('val').mean()")])
    before = run(recipe, tables, "DS:A", "sample_id")
    assert ticked(before) == places(before)
    note = line(before, "T1:J").notes[0]
    assert note.code == NOTE_ONE_ROW_PER_GROUP and (dict(note.params)["node"], dict(note.params)["step"], dict(note.params)["direction"]) == ("T1:A", 2, "forward")
    after = run(recipe, tables, "T3:P1", "sample_id", levels=ALL)                                           # from after the step, back: the line before it holds rows, not groups
    assert dict(line(after, "DS:A").notes[0].params)["direction"] == "backward" and line(after, "DS:A").notes[0].code == NOTE_ONE_ROW_PER_GROUP


def test_PROVISIONAL_a_value_written_under_its_own_name_from_another_column_cannot_be_told_from_a_recompute_of_itself():
    # `country = lab` (the values of ANOTHER column under the name country): the walk reads names only, so it ticks it like a recompute, and says it does not know
    recipe = F.recipe({"A": F.schema(["sample_id", "country", "lab"], [F.with_columns(country="pl.col('lab')")])}, {}, {"P": F.plot("A")})
    walk = run(recipe, {"A": F.table(sample_id=["S1"], country=["NO"], lab=["X"])}, "DS:A", "country")
    note = line(walk, "T1:A").notes[0]
    assert note.code == NOTE_RECOMPUTED and dict(note.params)["knows_source_of_values"] is False and ticked(walk) == places(walk)
    lab = run(recipe, {"A": F.table(sample_id=["S1"], country=["NO"], lab=["X"])}, "DS:A", "lab")            # the other column is untouched, and the walk does not say it moved into `country`
    assert [x.occurrences[0].name for x in lab.lines] == ["lab", "lab"] and all(x.notes == () for x in lab.lines)


def test_reshapes_stay_unread_and_grey_with_the_reason_PROVISIONAL():
    recipe = F.recipe({"A": F.schema(["sample_id", "a1", "a2"], [F.unpivot(["a1", "a2"], ["sample_id"])])}, {}, {"P": F.plot("A")})
    walk = run(recipe, {"A": F.table(sample_id=["S1"], a1=["x"], a2=["y"])}, "DS:A", "a1")
    assert all(x.state == "grey" and x.reason.code == STEP_NOT_READ for x in walk.lines) and walk.gone == ()


# ----------------------------------------------------------------------------------------------------------------------------- the proof of "the same column"

def _is_key(recipe, node, name):
    """Whether the column is named by a join key anywhere in the recipe (marking it would change the join, not only the column)."""
    for body in (recipe.get("joins") or {}).values():
        for step in (body.get("tier1") or {}).get("steps", []):
            if step.get("action") == "polars_join":
                keys = [step.get("on")] if "on" in step else [step.get("left_on"), step.get("right_on")]
                if any(name in (k if isinstance(k, list) else [k]) for k in keys):
                    return True
    return False


def all_fixtures():
    yield from F.followed()
    yield ("chain",) + F.chain()
    yield ("tiers",) + F.tiers()
    renamed = F.recipe({"A": F.schema(["sample_id", "country"], [F.rename(country="origin")], keys=["sample_id"]), "B": F.schema(["isolate", "country"])},
                       {"J": F.join(["A", "B"], [F.join_step("B", on=("sample_id", "isolate"))])}, {"P": F.plot("J"), "Pb": F.plot("B")})
    yield "renamed", renamed, {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(isolate=["S1"], country=["SE"])}


def test_the_mark_put_in_a_source_column_arrives_in_the_column_the_walk_names_at_every_ticked_place():
    checked = skipped = holders_seen = 0
    for name, recipe, tables in all_fixtures():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        for sid, table in tables.items():
            for column in table.columns:
                if table[column].dtype != O.pl.String or _is_key(recipe, f"DS:{sid}", column):
                    continue
                marked = O.replay(recipe, O.marked(tables, {sid: [column]}))
                walk = index.walk(Start(f"DS:{sid}", column), levels=ALL)
                held = {(x.place, o.name) for x in walk.lines for o in x.occurrences}
                for x in walk.lines:
                    if x.scope_group != "lineage" or x.state != "tick" or x.place.startswith("DS:"):
                        continue
                    value_note = {n.code for n in x.notes} & {NOTE_ANOTHER_TYPE, NOTE_RECOMPUTED, NOTE_AGGREGATED}
                    for occurrence in x.occurrences:
                        end = marked.end(x.covers[0])
                        if value_note or len(occurrence.sources) > 1:                 # the values were rewritten there, or two columns met in a key: the mark need not arrive
                            skipped += 1
                            continue
                        assert end is not None and occurrence.name in end.columns, (name, sid, column, x.place)
                        assert O.holds_mark(end.select(occurrence.name)), (name, sid, column, x.place, occurrence.name)
                        checked += 1
                for node in {n for (n, _k) in marked.frames if not n.startswith("DS:")}:       # the other way: every table that holds the mark is a line or a place no plot reads
                    end = marked.end(node)
                    if end is None:
                        continue
                    for held_column in end.columns:
                        if O.holds_mark(end.select(held_column)):
                            place = index.place_of[node]
                            assert (place, held_column) in held or place in {u.place for u in walk.unread}, (name, sid, column, node, held_column)
                            holders_seen += 1
    assert checked > 60 and holders_seen > 60 and skipped < checked


def test_every_ticked_line_that_changes_the_type_says_so_and_a_type_note_is_a_real_change():
    seen = 0
    for name, recipe, tables in all_fixtures():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        replay = O.replay(recipe, tables)
        for node in sorted({n for (n, _k) in replay.frames}):
            end = replay.end(node)
            if end is None or any(n == node for (n, _k) in replay.failures):
                continue
            for column in end.columns:
                walk = index.walk(Start(node, column), levels=ALL)
                for x in walk.lines:
                    if x.state != "tick":
                        continue
                    types = {o.type for o in x.occurrences}
                    carriers = {n.code for n in x.notes} & {NOTE_ANOTHER_TYPE, NOTE_RECOMPUTED, NOTE_AGGREGATED}
                    if types != {walk.start_type}:
                        assert carriers, (name, node, column, x.place, types, walk.start_type)
                    for n in x.notes:
                        if n.code == NOTE_ANOTHER_TYPE:
                            assert dict(n.params)["type_before"] != dict(n.params)["type_after"]
                        if n.code in VALUE_NOTES:
                            assert {"node", "step", "action", "name_before", "name_after", "type_before", "type_after", "direction"} <= set(dict(n.params))
                    seen += 1
    assert seen > 500


def test_no_line_is_grey_for_a_change_the_walk_reads_on_every_fixture_of_this_step():
    # the 171 lines that were grey for "change not followed" are ticked now: what is grey on these recipes has another, stated reason
    for name, recipe, tables in F.followed():
        graph, plans = setup(recipe, tables)
        index = LineageIndex(graph, plans)
        replay = O.replay(recipe, tables)
        for node in sorted({n for (n, _k) in replay.frames}):
            end = replay.end(node)
            for column in (end.columns if end is not None else ()):
                for x in index.walk(Start(node, column), levels=ALL).lines:
                    if x.state == "grey":
                        assert x.reason.code in (NO_STEP_LIST, SEVERAL_COLUMNS, STEP_NOT_READ, PLAN_FAILED, READING_DISAGREES), (name, node, column, x.place, x.reason)
                        assert x.reason.code != "change_not_followed"


# ----------------------------------------------------------------------------------------------------------------------------- the review's findings

def test_unread_holds_says_whether_the_column_is_in_the_table_no_plot_reads():
    kept, tables = F.tiers()
    walk = run(kept, tables, "T3:Pd", "sample_id")
    assert [(u.place, u.holds) for u in walk.unread] == [("T1:JU", True)]                                    # JU keeps sample_id
    dropped = copy.deepcopy(kept)
    dropped["joins"]["JU"]["tier1"]["steps"].append(F.select("gene", "year"))                                  # JU no longer holds sample_id (and nothing reads JU)
    gone = run(dropped, tables, "T3:Pd", "sample_id")
    assert [(u.place, u.holds) for u in gone.unread] == [("T1:JU", False)]


def test_a_start_that_selects_no_place_says_so_with_the_levels_where_the_column_exists():
    recipe, tables = F.tiers(u_declares_key=False)
    walk = run(recipe, tables, "T1:U", "junk", levels=("T3",))                                              # U is read by no plot: nothing at the plot level
    assert (walk.lines, walk.gone, walk.unread) == ((), (), ())
    reason = walk.nothing
    assert reason.code == NO_PLACE_AT_THE_LEVELS and reason.get("levels") == ("T3",) and reason.get("held_at_levels") == ("source", "T1", "T2")
    anywhere = run(recipe, tables, "T1:U", "junk", levels=("T1",))
    assert anywhere.nothing is None and [u.place for u in anywhere.unread] == ["T1:U"]                       # counted apart is not silence
    full = run(recipe, tables, "T3:Pd", "sample_id")
    assert full.nothing is None and full.lines
    assert full.within("lineage").nothing is None or full.within("lineage").lines == ()


def test_the_levels_where_the_column_exists_do_not_depend_on_the_levels_chosen():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    held = {levels: index.walk(Start("T3:Ps", "country"), levels=levels).held_at_levels for levels in (("T1",), ("T3",), ALL)}
    assert len(set(held.values())) == 1 and set(held[ALL]) >= {"T1", "T2", "T3", "source"}


def test_L024_the_step_named_as_the_removal_is_the_first_in_data_flow_order_PROVISIONAL():
    recipe, tables = F.tiers()
    graph, plans = setup(recipe, tables)
    index = LineageIndex(graph, plans)
    from utils.lineage_records import StepRef
    early = _Dead(("T1:S", 1, "country"), "T1:S", True, None, StepRef("T1:S", 1, "polars_drop", "p[1]"))
    later_same_node = _Dead(("T1:S", 4, "country"), "T1:S", True, None, StepRef("T1:S", 4, "polars_select", "p[4]"))
    downstream = _Dead(("T1:J1", 1, "country"), "T1:J1", True, None, StepRef("T1:J1", 1, "polars_drop", "q[1]"))
    for order in ([early, later_same_node, downstream], [downstream, later_same_node, early], [later_same_node, downstream, early]):
        assert index.first_removal(order).ref.step_path == "p[1]"                                            # the same answer whatever the order they were found in
    assert index.first_removal([downstream, later_same_node]).ref.step_path == "p[4]"                       # the earlier node wins, not the lower step number


def test_the_reach_iterates_prints_and_lists_in_sorted_order_whatever_the_hash_seed():
    reach = Reach(frozenset({"T1:z", "T1:a", "T1:m"}), frozenset({"T1:q", "T1:b"}), frozenset({"p9", "p1"}))
    assert list(reach.tables_with_plot) == ["T1:a", "T1:m", "T1:z"] and list(reach.plots) == ["p1", "p9"] and tuple(reach.tables_no_plot) == ("T1:b", "T1:q")
    assert repr(reach.plots) == "{'p1', 'p9'}" and "T1:a" in reach.tables_with_plot and reach.plots == {"p1", "p9"} and isinstance(reach.plots, SortedSet)
    assert (reach.n_tables, reach.n_tables_no_plot, reach.n_plots) == (3, 2, 2) and hash(reach) == hash(Reach(reach.tables_with_plot, reach.tables_no_plot, reach.plots))
    assert repr(SortedSet()) == "SortedSet()"


def test_a_source_line_next_to_a_tier_1_without_steps_says_which_line_it_duplicates_PROVISIONAL():
    recipe, tables = F.tiers()
    walk = run(recipe, tables, "T3:Pe", "gene", levels=ALL)                                                  # E has no steps at tier 1
    source = line(walk, "DS:E")
    assert source.state == "grey" and source.reason.code == NO_STEP_LIST and source.duplicates == "T1:E" and line(walk, "T1:E").duplicates is None
    steps = run(recipe, tables, "T3:Ps", "country", levels=ALL)                                              # S has a step at tier 1: its source is another table
    assert line(steps, "DS:S").duplicates is None and line(steps, "DS:S").reason.code == NO_STEP_LIST


# ----------------------------------------------------------------------------------------------------------------------------- the two gaps of the second review

def test_the_how_of_an_occurrence_is_the_strongest_kind_of_hop_on_the_path_in_either_order():
    """Two kinds of hop on one path: `how` is the strongest of them (`HOW_PRIORITY`: renamed, then cast, then recomputed), whichever comes first. A walk that took the
    last hop, or the first, gives another word in one of the orders below (second review, mutant Y2)."""
    ids = ["S1", "S2"]
    cases = [
        ("cast then rename", [F.cast(["year"], "Categorical"), F.rename(year="yr")], "yr", "renamed"),
        ("rename then cast", [F.rename(year="yr"), F.cast(["yr"], "Categorical")], "yr", "renamed"),
        ("cast then recompute", [F.cast(["year"], "Categorical"), F.with_columns(year="pl.col('year')")], "year", "cast"),
        ("recompute then cast", [F.with_columns(year="pl.col('year')"), F.cast(["year"], "Categorical")], "year", "cast"),
    ]
    for label, steps, name, expected in cases:
        recipe = F.recipe({"A": F.schema(["sample_id", "year"], steps, keys=["sample_id"])}, {}, {"P": F.plot("A")})
        walk = run(recipe, {"A": F.table(sample_id=ids, year=["2022", "2023"])}, "DS:A", "year")
        occ = line(walk, "T1:A").occurrences[0]
        assert occ.name == name and len(occ.steps) == 2 and occ.how == expected, label
        assert line(walk, "T3:P").occurrences[0].how == expected, label            # the plot that reads the table sees the same path


def test_the_aggregated_note_and_the_unread_step_note_say_the_walk_does_not_know_where_the_values_come_from():
    """An aggregate under the column's own name and a step the walk does not read both ticked the line; names only are read (D-0356), so both notes carry
    `knows_source_of_values` False, like the recompute note (PROVISIONAL, P3). Second review, mutant Y5."""
    aggregated = F.recipe({"A": F.schema(["sample_id", "country", "val"], [F.group_by(["country"], val="pl.col('val').mean()")], keys=["sample_id"])}, {}, {"P": F.plot("A")})
    walk = run(aggregated, {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"], val=[1.0, 2.0])}, "DS:A", "val")
    notes = [n for x in walk.lines for n in x.notes]
    assert [n.code for n in notes] == [NOTE_AGGREGATED] * 2 and all(dict(n.params)["knows_source_of_values"] is False for n in notes)
    unread = F.recipe({"A": F.schema(["sample_id", "val"], [F.fill_null(["val"], 0.0)], keys=["sample_id"])}, {}, {"P": F.plot("A")})
    passed = run(unread, {"A": F.table(sample_id=["S1"], val=[1.0])}, "DS:A", "val")
    from utils.lineage_records import NOTE_UNREAD_STEP_PASSED
    notes = [n for x in passed.lines for n in x.notes]
    assert notes and all(n.code == NOTE_UNREAD_STEP_PASSED and dict(n.params)["knows_source_of_values"] is False for n in notes)
    other = run(unread, {"A": F.table(sample_id=["S1"], val=[1.0])}, "T3:P", "val")      # a start after the step crosses nothing: no note, no flag
    assert [n for x in other.lines for n in x.notes] == []
