"""The rule of a join's keys (utils.join_keys): length, then missing, then type; unknown types are no difference.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_join_keys.py -q
"""
from utils.join_keys import join_key_problem, key_length_problem

S = {"id": "String", "k": "Int64"}


def test_equal_types_and_names_are_accepted():
    assert join_key_problem(S, S, ["id"], ["id"]) is None


def test_unequal_lengths_come_first_even_when_columns_are_missing():
    got = join_key_problem(S, S, ["id", "nope"], ["id"])
    assert got == {"kind": "length", "left_keys": ["id", "nope"], "right_keys": ["id"]}


def test_two_empty_lists_are_a_problem_only_when_asked():
    assert join_key_problem(S, S, [], []) is None
    assert join_key_problem(S, S, [], [], empty_is_problem=True)["kind"] == "length"
    assert key_length_problem([], []) is None
    assert key_length_problem([], [], empty_is_problem=True)["kind"] == "length"


def test_missing_columns_are_listed_per_side_and_come_before_types():
    got = join_key_problem({"id": "String"}, {"id": "Int64"}, ["id", "x"], ["id", "y"])
    assert got == {"kind": "missing", "missing_left": ["x"], "missing_right": ["y"]}


def test_every_differing_pair_is_reported_in_order():
    got = join_key_problem({"a": "String", "b": "Int64", "c": "Int64"}, {"a": "Int64", "b": "Int64", "c": "String"}, ["a", "b", "c"], ["a", "b", "c"])
    assert got["kind"] == "type"
    assert [p["left_column"] for p in got["differing"]] == ["a", "c"]
    assert [p["same"] for p in got["pairs"]] == [False, True, False]


def test_an_unknown_type_is_never_a_difference():
    assert join_key_problem({"id": None}, {"id": "Int64"}, ["id"], ["id"]) is None
    assert join_key_problem({"id": "String"}, {"id": None}, ["id"], ["id"]) is None


def test_keys_are_paired_by_position_and_may_have_different_names():
    assert join_key_problem({"a": "String"}, {"b": "String"}, ["a"], ["b"]) is None
    assert join_key_problem({"a": "String"}, {"b": "Int64"}, ["a"], ["b"])["differing"][0]["right_column"] == "b"
