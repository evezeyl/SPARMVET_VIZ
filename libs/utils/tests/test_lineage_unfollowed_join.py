"""A line that crosses a join the app cannot YET follow is red and cannot be ticked (D-0452, D-0454, D-0460; the semi join is FOLLOWED, D-0486: `test_lineage_semi_join.py`).

The decisions, in the owner's words:
- D-0452: "The app cannot YET follow these joins": anti, right, full and self-joins. A column behind them is not traceable.
- D-0460: "B; if needed we try to find a solution later": a line the app cannot trace is red and not tickable.
- D-0454: "she wants the full sentence, with YET in capital letters": the warning is one full sentence that holds the word YET in capitals.

What the library returns (no colour, no HTML: the dialog is not built): the line's state is `grey` with the reason `join_not_yet_followed`; the reason carries
the join kind, the place of the join (node and step), the table the join reads and whether it is a self-join, as data. Before this change the walk said "tick,
with the note unread_step_passed" for a column of the first table behind such a join (it did not say it could not follow it).

The rule built: a line is untraceable when the best path from the place the user looks at to it crosses a step of such a join (the links of the walk are
the same in both directions, as for every uncertain link, P9). So the places BEFORE the join, seen from a start before it, are unchanged; the places after it are red;
seen from a start AFTER the join, the places before it are red (the path crosses the join backwards). The second reading (only the places after the join are red) is a
question to the owner, not built.

Left, inner and semi joins stay followed (the semi join since D-0486).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_unfollowed_join.py -q
"""
import inspect

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import run, setup

from utils import action_names, key_drop, remove_from_all as rfa, step_effects as fx
from utils import lineage_sentences
from utils.lineage_records import JOIN_NOT_YET_FOLLOWED, NOTE_UNREAD_STEP_PASSED, REASON_CODES, STEP_NOT_READ

NOT_YET = ["anti", "right", "full"]
FOLLOWED = ["left", "inner", "semi"]


def line(walk, place):
    return next(x for x in walk.lines if x.place == place)


def two(how, **extra):
    """A(sample_id, country) and B(sample_id, lab); J = A with B (kind `how`); a plot P reads J. sample_id is the declared key of both."""
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B", how=how, **extra)])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2", "S3"], country=["NO", "SE", "NO"]), "B": F.table(sample_id=["S1", "S2", "S4"], lab=["X", "Y", "Z"])}
    return recipe, tables


def selfjoin(how):
    """J = A with A itself (the same table on both sides)."""
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"])}, {"J": F.join(["A", "A"], [F.join_step("A", how=how, suffix="_r")])}, {"P": F.plot("J")})
    return recipe, {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"])}


def is_red(x, kind=None, self_join=False):
    assert x.state == "grey" and x.reason.code == JOIN_NOT_YET_FOLLOWED, (x.place, x.state, x.reason)
    assert x.reason.get("self_join") is self_join
    if kind is not None:
        assert x.reason.get("kind") == kind
    assert all(n.code != NOTE_UNREAD_STEP_PASSED for n in x.notes)           # the old answer was "tick with a note"; there is no tick to carry a note
    return x.reason


# ----------------------------------------------------------------------------------------------------------------------------- the readings

def test_the_kinds_not_yet_followed_are_named_in_one_place_and_never_overlap_the_followed_ones():
    assert set(fx.NOT_YET_FOLLOWED_JOINS) == {"anti", "right", "full"} and "semi" in fx.FOLLOWED_JOINS
    assert not set(fx.NOT_YET_FOLLOWED_JOINS) & set(fx.FOLLOWED_JOINS)
    for how in NOT_YET:
        effect = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "k", "how": how})
        assert effect.kind == fx.UNREAD and effect.how == how and effect.right == "B" and fx.not_yet_followed(effect) == how
    for how in FOLLOWED:
        assert fx.not_yet_followed(fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "k", "how": how})) is None
    assert fx.not_yet_followed(fx.effect_of({"action": action_names.DROP, "columns": ["a"]})) is None
    assert fx.not_yet_followed(fx.effect_of({"action": action_names.WITH_COLUMNS})) is None


def test_any_other_kind_is_not_followed_either():
    effect = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "k", "how": "cross"})
    assert effect.kind == fx.UNREAD and fx.not_yet_followed(effect) == "cross"


# ----------------------------------------------------------------------------------------------------------------------------- the first table

@pytest.mark.parametrize("how", NOT_YET)
def test_a_column_of_the_first_table_is_red_after_the_join_and_the_places_before_it_stay_as_they_are(how):
    recipe, tables = two(how)
    for column in ("country", "sample_id"):                               # a plain column and the join key
        walk = run(recipe, tables, "T1:A", column)
        start = line(walk, "T1:A")
        assert start.state == "tick" and start.reason is None and start.notes == ()
        for place in ("T1:J", "T3:P"):
            reason = is_red(line(walk, place), how)
            assert (reason.get("node"), reason.get("step"), reason.get("action"), reason.get("right")) == ("T1:J", 1, action_names.JOIN, "B")
        assert walk.gone == ()


@pytest.mark.parametrize("how", NOT_YET)
def test_a_column_of_the_second_table_is_red_after_the_join_with_the_join_as_the_reason(how):
    recipe, tables = two(how)
    for column in ("lab", "sample_id"):
        walk = run(recipe, tables, "T1:B", column)
        assert line(walk, "T1:B").state == "tick"
        for place in ("T1:J", "T3:P"):
            is_red(line(walk, place), how)                                  # before: grey with the reason step_not_read; the reason is the join now
        assert not any(x.reason is not None and x.reason.code == STEP_NOT_READ for x in walk.lines)


@pytest.mark.parametrize("how", NOT_YET)
def test_seen_from_after_the_join_the_places_before_it_are_red_too_PROVISIONAL_reading(how):
    recipe, tables = two(how)
    walk = run(recipe, tables, "T3:P", "country")
    assert line(walk, "T3:P").state == "tick" and line(walk, "T1:J").state == "tick"          # between the start and the join: nothing is crossed
    is_red(line(walk, "T1:A"), how)                                                           # the path to A crosses the join backwards (the other reading is a question to the owner)


def test_the_places_before_the_join_are_unchanged_when_the_table_has_its_own_steps():
    recipe, tables = two("anti")
    recipe["data_schemas"]["A"]["tier2"] = {"steps": [F.keep("country", "ne", "XX")]}
    recipe["analysis_groups"]["g"]["plots"]["Pa"] = F.plot("A")                          # a plot that reads A directly: A has a tier 2 place
    walk = run(recipe, tables, "T1:A", "country")
    assert {x.place: x.state for x in walk.lines} == {"T1:A": "tick", "T2:A": "tick", "T3:Pa": "tick", "T1:J": "grey", "T3:P": "grey"}


@pytest.mark.parametrize("how", FOLLOWED)
def test_left_inner_and_semi_joins_are_followed_as_before(how):
    recipe, tables = two(how)
    walk = run(recipe, tables, "T1:A", "country")
    assert [(x.place, x.state, x.reason, x.notes) for x in walk.lines] == [("T1:A", "tick", None, ()), ("T1:J", "tick", None, ()), ("T3:P", "tick", None, ())]
    key = run(recipe, tables, "T1:A", "sample_id")
    assert {x.place: x.state for x in key.lines} == {"T1:A": "tick", "T1:B": "tick", "T1:J": "tick", "T3:P": "tick"}


# ----------------------------------------------------------------------------------------------------------------------------- the self-join

@pytest.mark.parametrize("how", ["left", "inner", "anti", "semi"])
def test_a_table_joined_with_itself_is_red_after_the_join_whatever_its_kind(how):
    recipe, tables = selfjoin(how)
    for column in ("country", "sample_id"):
        walk = run(recipe, tables, "T1:A", column)
        assert line(walk, "T1:A").state == "tick"
        for place in ("T1:J", "T3:P"):
            reason = is_red(line(walk, place), how, self_join=True)
            assert (reason.get("node"), reason.get("step"), reason.get("right")) == ("T1:J", 1, "A")


def test_a_second_step_that_reads_a_table_the_join_already_holds_is_a_self_join_and_the_first_step_is_not():
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B"), F.join_step("B", suffix="_2")])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1"], country=["NO"]), "B": F.table(sample_id=["S1"], lab=["X"])}
    walk = run(recipe, tables, "T1:A", "country")
    reason = is_red(line(walk, "T1:J"), "left", self_join=True)
    assert reason.get("step") == 2                                       # the first step (A with B) is followed; the first uncertain link is the second step
    clean = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"]), "C": F.schema(["sample_id", "note"], keys=["sample_id"])},
                     {"J": F.join(["A", "B", "C"], [F.join_step("B"), F.join_step("C")])}, {"P": F.plot("J")})
    more = {**tables, "C": F.table(sample_id=["S1"], note=["n"])}
    assert all(x.state == "tick" for x in run(clean, more, "T1:A", "country").lines)


# ----------------------------------------------------------------------------------------------------------------------------- the sentence

@pytest.mark.parametrize("how", NOT_YET)
def test_the_warning_is_a_full_sentence_with_YET_in_capitals_that_names_the_kind_and_the_place(how):
    recipe, tables = two(how)
    reason = line(run(recipe, tables, "T1:A", "country"), "T1:J").reason
    sentence = lineage_sentences.join_not_yet_followed_sentence(reason)
    assert sentence.count("YET") == 1 and "yet" not in sentence                 # her words: "the full sentence but YET in capital Letters"
    assert how in sentence and "T1:J" in sentence and "step 1" in sentence and "'B'" in sentence
    assert sentence.endswith(".") and sentence.count(".") >= 2                  # more than a label: full sentences
    assert "PROVISIONAL" in inspect.getsource(lineage_sentences)                # the wording beyond the capital YET is not decided


def test_the_sentence_of_a_self_join_says_so_and_the_sentence_of_an_anti_join_says_rows_may_be_added():
    recipe, tables = selfjoin("left")
    self_text = lineage_sentences.join_not_yet_followed_sentence(line(run(recipe, tables, "T1:A", "country"), "T1:J").reason)
    assert "self-join" in self_text and "YET" in self_text and "left" in self_text
    recipe, tables = two("anti")
    anti = lineage_sentences.join_not_yet_followed_sentence(line(run(recipe, tables, "T1:A", "country"), "T1:J").reason)
    assert "rows may be added instead of removed" in anti and "Check them before you confirm" in anti


def test_the_reason_code_is_in_the_closed_list_of_reasons():
    assert JOIN_NOT_YET_FOLLOWED in REASON_CODES


# ----------------------------------------------------------------------------------------------------------------------------- the callers that use certainty

@pytest.mark.parametrize("how", NOT_YET)
def test_a_drop_whose_column_goes_through_such_a_join_is_refused_with_the_plain_sentence(how):
    recipe, tables = two(how)
    plans = O.replay(recipe, tables).plans
    sentence = key_drop.key_drop_problem(recipe, "T1:A", ["country"], plans)
    assert sentence is not None and "YET" in sentence and how in sentence and "T1:J" in sentence and "the drop is not written" in sentence
    assert key_drop.key_drop_problem(recipe, "T1:J", ["country"], plans) is None            # after the join nothing crosses it (the gate judges forward from the place)
    assert key_drop.key_drop_problem(recipe, "T3:P", ["country"], plans) is None
    refused = key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"], plans)               # the key itself: refused as before, by the join that reads it
    assert refused is not None and "is read as a join key" in refused


@pytest.mark.parametrize("how", FOLLOWED)
def test_the_same_drop_before_a_followed_join_is_allowed(how):
    recipe, tables = two(how)
    plans = O.replay(recipe, tables).plans
    assert key_drop.key_drop_problem(recipe, "T1:A", ["country"], plans) is None


def test_a_drop_walk_marks_the_places_the_gate_refuses():
    recipe, tables = two("anti")
    walk = run(recipe, tables, "T1:A", "country", kind="drop")
    start = line(walk, "T1:A")
    assert start.state == "grey" and start.reason.code == JOIN_NOT_YET_FOLLOWED          # the gate refuses it, so the line is red and cannot be ticked (line and gate agree)


@pytest.mark.parametrize("how", NOT_YET)
def test_remove_from_all_the_data_does_not_write_behind_such_a_join_and_lists_the_table_with_the_sentence(how):
    recipe, tables = two(how)
    option = rfa.describe(recipe, "sample_id", plans=O.replay(recipe, tables).plans)
    assert option.offered and [p.table for p in option.places] == ["A", "B"]             # the tables before the join are reached (each holds the key at its own start)
    stays = {m.table: m for m in option.may_stay}
    assert set(stays) == {"J"} and stays["J"].code == rfa.UNCERTAIN_LINK and stays["J"].reason.code == JOIN_NOT_YET_FOLLOWED
    said = rfa.may_stay_sentence(stays["J"])
    assert said.startswith("In the table 'J'") and "YET" in said and how in said and said.rstrip().endswith("The selection may stay there.")


@pytest.mark.parametrize("how", FOLLOWED)
def test_remove_from_all_the_data_reaches_the_table_behind_a_followed_join(how):
    recipe, tables = two(how)
    option = rfa.describe(recipe, "sample_id", plans=O.replay(recipe, tables).plans)
    assert [p.table for p in option.places] == ["A", "B", "J"] and not any(m.table == "J" for m in option.may_stay)
