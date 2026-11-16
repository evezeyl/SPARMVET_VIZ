"""The anti-join of a table with itself on the same key is an error (D-0078, D-0050); every other self-join stays an advice.

"Only the anti-join of a table with itself on the same key is an error; every other self-join is a warning with the row
numbers" (Eve). Such a join keeps the rows of a table whose key is not in the same table: no row that has a key
remains, and the recipe used to run and give an empty table without a word. The rule is one pure function
(`utils.join_keys.anti_join_with_itself`), asked by the checker (J15) and by the build (DataAssembler); the build test is
`libs/transformer/tests/test_anti_join_with_itself_build.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_anti_join_with_itself.py -q
"""
import pytest

from utils import action_names
from utils.join_keys import anti_join_with_itself
from test_recipe_check import check, valid


def join(right="A", how="anti", **keys):
    return {"action": action_names.JOIN, "right_ingredient": right, "how": how, **({"on": ["id"]} if not keys else keys)}


# -- the rule itself ----------------------------------------------------------------------------

def test_the_anti_join_of_the_base_table_on_the_same_key_is_the_case():
    found = anti_join_with_itself("A", [], join())
    assert found == {"table": "A", "keys": ["id"]}


@pytest.mark.parametrize("step", [
    join(how="left"), join(how="inner"), join(how="semi"), join(how="full"), join(how="cross"),     # another kind of join: advice only
    {k: v for k, v in join().items() if k != "how"},                                                # the default kind is left
    join(right="B"),                                                                                # another table
    join(left_on=["parent"], right_on=["id"]),                                                       # other keys: a normal self-join
    {"action": action_names.JOIN_ASOF, "right_ingredient": "A", "how": "anti", "on": ["id"]},        # not the join action
])
def test_every_other_self_join_is_not_the_case(step):
    assert anti_join_with_itself("A", [], step) is None


def test_the_same_key_written_as_left_on_and_right_on_is_the_case():
    assert anti_join_with_itself("A", [], join(left_on="id", right_on="id")) == {"table": "A", "keys": ["id"]}


def test_an_unquoted_on_is_read_like_the_checker_reads_it():
    step = {"action": action_names.JOIN, "right_ingredient": "A", "how": "anti", True: ["id"]}
    assert anti_join_with_itself("A", [], step) == {"table": "A", "keys": ["id"]}


def test_a_table_joined_before_does_not_change_the_rule_when_the_rows_stay_in_the_base():
    before = [join(right="B", how="left"), {"action": action_names.FILTER}]
    assert anti_join_with_itself("A", before, join()) is not None


@pytest.mark.parametrize("before", [
    [join(right="B", how="full")],      # a full or right join can bring keys that the base table does not have
    [join(right="B", how="right")],
    [{"action": action_names.WITH_COLUMNS}],   # a step that may change the key
    ["not a step"],
])
def test_when_the_left_table_may_hold_other_keys_it_is_not_the_case(before):
    assert anti_join_with_itself("A", before, join()) is None


def test_the_anti_join_of_a_table_joined_before_is_a_normal_question():
    """A left-joined with B, then anti with B: the rows of A that have no partner in B. This is useful, never an error."""
    before = [join(right="B", how="left")]
    assert anti_join_with_itself("A", before, join(right="B")) is None


# -- the checker ----------------------------------------------------------------------------------

def codes(raw, code):
    return [p for p in check(raw).problems if p.code == code]


def recipe(**step):
    raw = valid()
    raw["joins"]["AB"]["steps"]["tier1"][0].update(right_ingredient="A", how="anti", **step)
    return raw


def test_the_checker_refuses_the_anti_join_of_a_table_with_itself_with_what_happens_then_a_suggestion():
    result = check(recipe())
    problems = codes(recipe(), "J15")
    assert len(problems) == 1 and problems[0].severity == "E" and problems[0].path == "joins.AB.steps.tier1[1]"
    message, fix = problems[0].message, problems[0].fix
    assert "'A'" in message and "['id']" in message and "no row" in message
    assert fix.startswith("Suggestion:") and fix.count("Suggestion:") == 2
    assert not result.ok


def test_the_anti_join_is_not_advised_twice():
    assert codes(recipe(), "J12") == []


def test_the_checker_still_only_advises_the_other_self_joins():
    for how in ("left", "inner"):
        raw = valid()
        raw["joins"]["AB"]["steps"]["tier1"][0].update(right_ingredient="A", how=how)
        assert codes(raw, "J15") == []
        assert [p.severity for p in codes(raw, "J12")] == ["A"]
        assert check(raw).ok


def test_the_checker_does_not_refuse_the_anti_join_with_another_table():
    raw = valid()
    raw["joins"]["AB"]["steps"]["tier1"][0].update(how="anti")
    assert codes(raw, "J15") == []


# -- a step before that does not make the left table another table (round 2026-11-16) -------------------------------

@pytest.mark.parametrize("before", [
    {"action": action_names.HEAD, "n": 3},
    {"action": action_names.REMOVE, "predicates": ["pl.col('v') < 2"]},
    {"action": action_names.WITH_COLUMNS, "named_exprs": {"double": "pl.col('v') * 2"}},
    {"action": action_names.RENAME, "mapping": {"v": "value"}},
], ids=["head", "remove", "with_columns another column", "rename another column"])
def test_a_step_that_removes_rows_or_writes_other_columns_keeps_the_table_itself(before):
    assert anti_join_with_itself("A", [before], join()) == {"table": "A", "keys": ["id"]}


@pytest.mark.parametrize("before", [
    {"action": action_names.WITH_COLUMNS, "named_exprs": {"id": "pl.col('id').str.to_uppercase()"}},   # writes the key
    {"action": action_names.RENAME, "mapping": {"id": "key"}},                                         # renames the key away
    {"action": action_names.RENAME, "mapping": {"other": "id"}},                                       # writes the key by a rename
    {"action": action_names.WITH_COLUMNS, "named_exprs": "not a mapping"},                             # cannot be read
    {"action": action_names.RENAME},                                                                    # cannot be read
])
def test_a_step_that_writes_or_renames_the_key_or_cannot_be_read_is_every_other_self_join(before):
    assert anti_join_with_itself("A", [before], join()) is None


@pytest.mark.parametrize("before,expected", [
    ({"action": action_names.WITH_COLUMNS, "named_exprs": {"id": "pl.col('id')"}}, (0, 1)),   # writes the key: J12
    ({"action": action_names.UNIQUE}, (1, 0)),                                                 # only removes rows: J15
])
def test_the_checker_gives_j15_or_j12_never_neither(before, expected):
    raw = recipe()
    raw["joins"]["AB"]["steps"]["tier1"].insert(0, before)
    assert (len(codes(raw, "J15")), len(codes(raw, "J12"))) == expected
