"""The option "remove from all the data" writes ONLY at the places the user left ticked, and says nothing about the tables where no step is written
(D-0499, D-0531, D-0501; task REMOVE-FROM-ALL-TICKED-ONLY; a library step, no screen), `utils.remove_from_all.apply(..., ticked=...)`.

What is proved, on the small recipe `fx.tiers(u_declares_key=True)` (tables S, E, M, U and the joins J1, J2, JU; the oracle replays the real tables in plain Polars):
- all places ticked gives the same steps as no list at all (the old result), and the result says whether a list was given;
- one place unticked: no step is written there and the entity is really still in that table; the ticked places are written and replayed without the entity;
- a table no plot reads (U, JU), ticked and unticked;
- a list in another order or with a place twice: the steps are written once each, in the order of the places of the option;
- an empty list, a place that does not exist, a place of the recipe that the option did not reach, a text instead of a list: a plain error, nothing written, not even the counter;
- the library says nothing about an unticked table: `Applied` holds the places written and not written, and nothing more.

Mutation (seen failing, see the report): MUTATION T1 `_chosen_places` returns every place whatever was ticked.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_remove_from_all_ticked.py -q
"""
from __future__ import annotations

import copy
from typing import List

import polars as pl
import pytest

import lineage_fixtures as fx
import lineage_oracle as oracle

from utils import audit_copy, remove_from_all as rfa
from utils.audit_copy import AuditCopyError, start_audit

AUD = "1a2b3c4d"


def setup():
    recipe, tables = fx.tiers(u_declares_key=True)
    plans = oracle.replay(recipe, tables).plans
    return recipe, tables, plans, rfa.describe(recipe, "sample_id", plans=plans)


def folded(recipe):
    out = copy.deepcopy(recipe)
    holders = list((out.get("data_schemas") or {}).values()) + list((out.get("joins") or {}).values())
    for body in holders:
        for tier in ("tier1", "tier2", "tier3"):
            held = body.get(tier)
            if isinstance(held, dict) and "audit_steps" in held:
                held["steps"] = list(held.get("steps") or []) + held.pop("audit_steps")
    return out


def written_places(audit) -> List[str]:
    return [s.place for s in audit_copy.all_audit_steps(audit.recipe)]


def test_every_place_ticked_equals_no_list_and_the_result_says_which_case_it_was():
    recipe, tables, plans, option = setup()
    everything = [p.place for p in option.places]
    a, b = start_audit(recipe, AUD), start_audit(recipe, AUD)
    ticked = rfa.apply(a, option, ["S2"], "r", plans=plans, ticked=everything)
    default = rfa.apply(b, option, ["S2"], "r", plans=plans)
    assert a.recipe == b.recipe and ticked.step_ids == default.step_ids and ticked.written == default.written == tuple(everything)
    assert ticked.ticked_given is True and default.ticked_given is False
    assert ticked.not_written == default.not_written == ()


def test_one_place_unticked_gets_no_step_and_the_entity_really_stays_there():
    recipe, tables, plans, option = setup()
    left_out = "T1:E"
    ticked = [p.place for p in option.places if p.place != left_out]
    audit = start_audit(recipe, AUD)
    applied = rfa.apply(audit, option, ["S2"], "r", plans=plans, ticked=ticked)
    assert left_out not in written_places(audit) and sorted(written_places(audit)) == sorted(ticked)
    assert applied.written == tuple(ticked) and applied.not_written == (left_out,) and len(applied.step_ids) == len(ticked)
    after = oracle.replay(folded(audit.recipe), tables)
    assert "S2" in after.end("T1:E")["sample_id"].to_list(), "nothing was written there: the entity is measured to be there"
    assert "S2" not in after.end("T1:S")["sample_id"].to_list() and "S2" not in after.end("T1:M")["sample_id"].to_list()


def test_a_table_no_plot_reads_ticked_and_unticked():
    recipe, tables, plans, option = setup()
    assert "T1:U" in [p.place for p in option.places] and not [p for p in option.places if p.place == "T1:U"][0].plots
    others = [p.place for p in option.places if p.place != "T1:U"]
    only_u = start_audit(recipe, AUD)
    rfa.apply(only_u, option, ["S2"], "r", plans=plans, ticked=["T1:U"])
    assert written_places(only_u) == ["T1:U"]
    without_u = start_audit(recipe, AUD)
    rfa.apply(without_u, option, ["S2"], "r", plans=plans, ticked=others)
    assert "T1:U" not in written_places(without_u)
    assert "S2" in oracle.replay(folded(without_u.recipe), tables).end("T1:U")["sample_id"].to_list()
    assert "S2" not in oracle.replay(folded(only_u.recipe), tables).end("T1:U")["sample_id"].to_list()


def test_a_list_in_another_order_or_with_a_place_twice_writes_each_place_once_in_the_order_of_the_option():
    recipe, tables, plans, option = setup()
    order = [p.place for p in option.places]
    wanted = [order[3], order[0], order[3], order[1]]
    audit = start_audit(recipe, AUD)
    applied = rfa.apply(audit, option, ["S2"], "r", plans=plans, ticked=wanted)
    assert applied.written == (order[0], order[1], order[3]) and written_places(audit) == list(applied.written)
    assert applied.step_ids == tuple(f"audit_{AUD}_{k}" for k in (1, 2, 3))
    straight = start_audit(recipe, AUD)
    rfa.apply(straight, option, ["S2"], "r", plans=plans, ticked=[order[0], order[1], order[3]])
    assert straight.recipe == audit.recipe


@pytest.mark.parametrize("ticked, text", [
    ([], "No place is ticked"),
    (["T1:Nobody"], "'T1:Nobody' is not one that this option reaches"),
    (["T1:S", "T2:S"], "'T2:S' is not one that this option reaches"),
    (["T1:S", None], "None"),
    ("T1:S", "must be a list"),
])
def test_a_list_that_cannot_be_used_is_a_plain_error_and_nothing_is_written_not_even_the_counter(ticked, text):
    recipe, tables, plans, option = setup()
    audit = start_audit(recipe, AUD)
    before, counter = copy.deepcopy(audit.recipe), audit.created
    with pytest.raises(AuditCopyError) as error:
        rfa.apply(audit, option, ["S2"], "r", plans=plans, ticked=ticked)
    assert text in str(error.value) and "nothing was written" in str(error.value)
    assert audit.recipe == before and audit.created == counter and written_places(audit) == []


def test_a_value_that_does_not_fit_a_ticked_table_refuses_all_and_one_that_does_not_fit_an_unticked_table_does_not():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "N": fx.table(sample_id=[1, 2], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]), "N": fx.schema(["sample_id", "g"], keys=["sample_id"])}, {}, {"P": fx.plot("A"), "Pn": fx.plot("N")})
    plans = oracle.replay(recipe, tables).plans
    option = rfa.describe(recipe, "sample_id", plans=plans)
    audit = start_audit(recipe, AUD)
    with pytest.raises(AuditCopyError):
        rfa.apply(audit, option, ["S2"], "r", plans=plans, ticked=["T1:A", "T1:N"])
    assert written_places(audit) == []
    rfa.apply(audit, option, ["S2"], "r", plans=plans, ticked=["T1:A"])
    assert written_places(audit) == ["T1:A"], "the number table is unticked: its type does not matter"


def test_the_result_holds_only_the_places_written_and_not_written_and_no_text_about_the_unticked_table():
    recipe, tables, plans, option = setup()
    audit = start_audit(recipe, AUD)
    applied = rfa.apply(audit, option, ["S2"], "r", plans=plans, ticked=["T1:S"])
    assert set(applied.__dataclass_fields__) == {"step_ids", "written", "not_written", "ticked_given"}
    assert all(isinstance(x, str) for x in applied.written + applied.not_written)
    for name in ("MayStay", "may_stay_sentence", "not_reached_sentence", "unticked_places", "Unticked", "_flow"):
        assert not hasattr(rfa, name), name


def test_the_option_is_not_changed_by_apply_and_a_second_apply_on_a_fresh_copy_gives_the_same():
    recipe, tables, plans, option = setup()
    before = copy.deepcopy(option)
    rfa.apply(start_audit(recipe, AUD), option, ["S2"], "r", plans=plans, ticked=["T1:S", "T1:E"])
    assert option == before
