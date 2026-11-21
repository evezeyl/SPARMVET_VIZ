"""The option "remove from all the data" of the HOME audit, step 1: the pure logic (D-0415 part B, D-0416, D-0313), `utils.remove_from_all`.

What is proved, on small recipes with their real tables replayed in plain Polars by the oracle of the lineage tests (nothing of the walk is used to say what is
expected):
- the option is offered only for the ENTITY KEY, the key a recipe declares (`is_entity_key`, D-0313, D-0082): never for another column, also when that column is
  used to join; a recipe that declares no entity key gets "not offered" with a plain reason;
- it reaches EVERY table that holds the key at the end of its tier 1, whatever the lineage: also a table no plot reads, a table no join links (it declares the same
  key), a join, and a table that holds the key under another name; a table that does not hold it is not reached; what the app cannot follow is listed, never guessed;
- each place is written at tier 1 (`T1:<table>`) with the column name and the type THERE, the plots that read the table (possibly none), in graph order;
- the option is OFF by default and `describe` applies nothing and changes nothing; the list of tables is known before anything is applied (D-0416 points 2 and 3);
- applied to the audit copy, the sample is gone from every reached table and from every table built from them, and nothing else changed ("resequenced sample");
  `apply` is all or nothing; a value that does not fit the key's type in one table refuses the whole apply;
- every shipped recipe: the function returns "not offered" with a reason, or a list; it never crashes.

Mutation index (each seen failing, see the report): MUTATION M1 the column is not checked (offered for any column); MUTATION M2 a table no plot reads is left out;
MUTATION M3 `apply` writes at tier 1 of the first place only; MUTATION M4 the removal keeps `na` as remove (rows with no key are lost).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_remove_from_all.py -q
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest import mock

import polars as pl
import pytest

import lineage_fixtures as fx
import lineage_oracle as oracle

from utils import audit_copy, remove_from_all as rfa
from utils.audit_copy import AuditCopyError, add_step, start_audit
from utils.recipe_graph import build_graph
from utils.recipe_loader import load_recipe

ROOT = Path(__file__).resolve().parents[3]
AUD = "1a2b3c4d"


def describe(recipe, tables, column="sample_id", place: Optional[str] = None) -> rfa.RemoveFromAll:
    return rfa.describe(recipe, column, plans=oracle.replay(recipe, tables).plans, place=place)


def folded(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """The recipe with each `audit_steps` list appended to its `steps` (what the engine runs, in that order): the oracle runs `steps` only."""
    out = copy.deepcopy(recipe)
    holders: List[dict] = list((out.get("data_schemas") or {}).values()) + list((out.get("joins") or {}).values())
    for group in (out.get("analysis_groups") or {}).values():
        holders.extend((group.get("plots") or {}).values())
    for body in holders:
        for tier in ("tier1", "tier2", "tier3"):
            held = body.get(tier)
            if isinstance(held, dict) and "audit_steps" in held:
                held["steps"] = list(held.get("steps") or []) + held.pop("audit_steps")
    return out


def places_of(option: rfa.RemoveFromAll) -> List[str]:
    return [p.place for p in option.places]


def not_reached(option: rfa.RemoveFromAll) -> Dict[str, str]:
    return {n.table: n.code for n in option.not_reached}


# =====================================================================================================================
# What is offered, and for which column
# =====================================================================================================================


def test_offered_for_the_declared_key_with_the_warning_and_off_by_default():
    recipe, tables = fx.tiers(u_declares_key=True)
    option = describe(recipe, tables)
    assert option.offered and option.not_offered is None
    assert option.default_on is False, "an explicit act (D-0416 point 2)"
    assert option.warning == "This removes your selection from any data that holds it."
    assert "sample" not in option.warning.lower(), "the warning is data agnostic (D-0416 point 4)"
    assert option.column == "sample_id"


def test_it_reaches_every_table_that_holds_the_key_also_one_no_plot_reads_in_graph_order():
    recipe, tables = fx.tiers(u_declares_key=True)       # U: nothing reads it, no join links it, it declares the key; JU: a join no plot reads
    option = describe(recipe, tables)
    expected = [f"T1:{t}" for t in build_graph(recipe).collections()]
    assert places_of(option) == expected and sorted(expected) == sorted(f"T1:{t}" for t in ("S", "E", "M", "U", "J1", "J2", "JU"))
    by_table = {p.table: p for p in option.places}
    assert by_table["U"].plots == () and by_table["JU"].plots == (), "a table no plot reads is reached (D-0416 point 1)"
    assert by_table["S"].plots == ("Ps", "Pa", "Pb", "Pc", "Pd") and by_table["E"].plots == ("Pe", "Pa", "Pb", "Pc")
    assert all(p.tier == "T1" and p.column == "sample_id" and p.type == "String" for p in option.places)
    assert option.not_reached == () and option.types == ("String",) and option.types_differ is False


def test_a_table_with_the_same_column_name_that_declares_no_key_and_no_join_links_is_not_reached_but_listed():
    recipe, tables = fx.tiers(u_declares_key=False)      # U holds `sample_id`, declares nothing, no join reads it
    option = describe(recipe, tables)
    assert "T1:U" not in places_of(option)
    assert not_reached(option) == {"U": rfa.SAME_NAME_NOT_LINKED}, "told to the user, never written on the name alone (D-0355)"
    assert option.unsure == (), "that is information, not a doubt"


def test_not_offered_for_a_column_that_is_not_the_entity_key():
    recipe, tables = fx.tiers(u_declares_key=True)
    for column in ("country", "val", "gene", "year", "no_such_column"):
        option = describe(recipe, tables, column)
        assert not option.offered and option.not_offered.code == rfa.NOT_THE_ENTITY_KEY, column
        assert option.places == () and option.not_reached == ()
        assert option.not_offered.get("declared") == ("sample_id",), "the reason names the declared key"


def test_not_offered_for_a_column_used_to_join_that_is_not_declared_the_key():
    tables = {"A": fx.table(sample_id=["S1", "S2"], code=["c1", "c2"]), "B": fx.table(code=["c1", "c2"], w=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "code"], keys=["sample_id"]), "B": fx.schema(["code", "w"])},
                       {"J": fx.join(["A", "B"], [fx.join_step("B", on="code")])}, {"P": fx.plot("J")})
    assert describe(recipe, tables, "sample_id").offered
    option = describe(recipe, tables, "code")
    assert not option.offered and option.not_offered.code == rfa.NOT_THE_ENTITY_KEY, "a join column is information, not the entity key (D-0313)"
    assert "code" in __import__("utils.join_keys", fromlist=["x"]).recipe_join_keys(recipe)


def test_a_recipe_that_declares_no_entity_key_is_not_offered_with_a_plain_reason():
    recipe, tables = fx.chain(keys=())
    option = describe(recipe, tables)
    assert not option.offered and option.not_offered.code == rfa.NO_ENTITY_KEY_DECLARED
    assert option.places == () and option.warning == rfa.WARNING, "the warning text exists, nothing is offered"
    assert "entity key" in rfa.not_offered_sentence(option.not_offered), "the plain words name what is missing"


def test_a_recipe_that_cannot_be_drawn_is_not_offered_with_the_sentence():
    option = rfa.describe({"data_schemas": {}, "joins": {"J": {"ingredients": [{"dataset_id": "nobody"}], "tier1": {"steps": []}}}, "analysis_groups": {}}, "sample_id")
    assert not option.offered and option.not_offered.code == rfa.RECIPE_CANNOT_BE_DRAWN and option.not_offered.get("sentence")


def test_a_column_that_is_not_at_the_place_asked_is_not_offered():
    recipe, tables = fx.tiers(u_declares_key=True)
    for place, code in (("T1:S", rfa.COLUMN_NOT_AT_PLACE), ("T1:nowhere", rfa.UNKNOWN_PLACE)):
        option = describe(recipe, tables, "gene", place)
        assert not option.offered and option.not_offered.code == code, place


def test_describe_changes_nothing_and_the_audit_steps_of_a_copy_are_not_read():
    recipe, tables = fx.tiers(u_declares_key=True)
    audit = start_audit(recipe, AUD)
    add_step(audit, "T1:E", fx.keep("gene", "ne", "g1"), "a step that is already there")
    before_original, before_recipe, before_counter = copy.deepcopy(audit.original), copy.deepcopy(audit.recipe), audit.created
    plans = oracle.replay(recipe, tables).plans
    on_copy = rfa.describe(audit.recipe, "sample_id", plans=plans)
    on_original = rfa.describe(recipe, "sample_id", plans=plans)
    assert on_copy == on_original, "the plan is the original's: an audit step never changes which tables hold the key"
    assert audit.original == before_original and audit.recipe == before_recipe and audit.created == before_counter, "describe applies nothing"


def test_the_option_is_the_same_every_time_it_is_asked():
    recipe, tables = fx.tiers(u_declares_key=True)
    assert describe(recipe, tables) == describe(recipe, tables)
    assert repr(describe(recipe, tables)) == repr(describe(recipe, tables))


def test_without_the_engine_the_recipe_declares_the_names_and_the_types_are_unknown():
    recipe, _ = fx.chain()
    option = rfa.describe(recipe, "sample_id")
    assert option.offered and places_of(option) == ["T1:A", "T1:B", "T1:J"]
    assert [p.type for p in option.places] == ["", "", ""], "no engine, no types: said, never invented"


# =====================================================================================================================
# What it reaches: tables that do not hold the key, a key that is gone, a key under another name, what cannot be followed
# =====================================================================================================================


def test_a_table_that_does_not_hold_the_key_is_not_reached_and_not_listed():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "W": fx.table(code=["x", "y"], w=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]), "W": fx.schema(["code", "w"])}, {}, {"P": fx.plot("A"), "Pw": fx.plot("W")})
    option = describe(recipe, tables)
    assert places_of(option) == ["T1:A"] and option.not_reached == ()


def test_a_table_that_loses_the_key_in_its_tier_1_is_not_reached_and_the_reason_is_listed():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "G": fx.table(sample_id=["S1", "S2"], n=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]),
                        "G": fx.schema(["sample_id", "n"], [fx.group_by(["n"], c="pl.col('sample_id').count()")], keys=["sample_id"])}, {}, {"P": fx.plot("A"), "Pg": fx.plot("G")})
    option = describe(recipe, tables)
    assert places_of(option) == ["T1:A"] and not_reached(option) == {"G": rfa.KEY_GONE_AT_TIER1}


def test_a_key_that_a_rename_changes_is_followed_and_each_place_has_its_own_name():
    tables = {"A": fx.table(sample_id=["S1", "S2", "S3"], v=[1, 2, 3]), "B": fx.table(sample_id=["S1", "S2", "S3"], w=[4, 5, 6])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], [fx.rename(sample_id="isolate")], keys=["sample_id"]), "B": fx.schema(["sample_id", "w"], keys=["sample_id"])},
                       {"J": fx.join(["A", "B"], [fx.join_step("B", on=("isolate", "sample_id"))])}, {"P": fx.plot("J")})
    option = describe(recipe, tables)
    assert {p.table: p.column for p in option.places} == {"A": "isolate", "B": "sample_id", "J": "isolate"}, "the plan and the rename mapping give the name at each place"
    assert option.offered and not_reached(option) == {}


def test_the_renamed_name_is_the_key_when_the_user_stands_at_the_place_that_has_it():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "E": fx.table(sample_id=["S1", "S2"], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], [fx.rename(sample_id="isolate")], keys=["sample_id"]), "E": fx.schema(["sample_id", "g"], keys=["sample_id"])},
                       {}, {"P": fx.plot("A"), "Pe": fx.plot("E")})                         # no join equates `isolate` with `sample_id`: only the rename links them
    by_name = describe(recipe, tables, "isolate")
    assert not by_name.offered and by_name.not_offered.code == rfa.NOT_THE_ENTITY_KEY, "by name alone `isolate` is not declared anywhere"
    at_place = describe(recipe, tables, "isolate", "T1:A")
    assert at_place.offered and {p.table: p.column for p in at_place.places} == {"A": "isolate", "E": "sample_id"}, "E declares the key and no join links it: reached by the declaration"
    elsewhere = describe(recipe, tables, "isolate", "T1:E")
    assert not elsewhere.offered, "E has no `isolate`"


def test_a_key_recreated_under_another_name_by_a_computed_column_is_not_followed_and_is_listed():
    """What the walk can know: a rename mapping is read (D-0351), the values a computed column takes are not. A key copied to a new column and the old one dropped is
    therefore NOT followed: the table is not reached, it is listed with the reason, so the user is told that the sample stays there."""
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "E": fx.table(sample_id=["S1", "S2"], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], [fx.with_columns(isolate="pl.col('sample_id')"), fx.drop("sample_id")], keys=["sample_id"]),
                        "E": fx.schema(["sample_id", "g"], keys=["sample_id"])}, {}, {"P": fx.plot("A"), "Pe": fx.plot("E")})
    option = describe(recipe, tables)
    assert places_of(option) == ["T1:E"] and not_reached(option) == {"A": rfa.KEY_GONE_AT_TIER1}


def test_a_table_the_engine_cannot_plan_is_listed_as_unsure_never_guessed():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "E": fx.table(sample_id=["S1", "S2"], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]), "E": fx.schema(["sample_id", "g"], [fx.keep("nothing_here", "eq", 1)], keys=["sample_id"])},
                       {}, {"P": fx.plot("A"), "Pe": fx.plot("E")})
    option = describe(recipe, tables)
    assert places_of(option) == ["T1:A"]
    assert [u.table for u in option.unsure] == ["E"] and option.unsure[0].code == rfa.PLAN_FAILED and option.unsure[0].reason.get("sentence")


def _with_one_step_in_a(steps):
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=["1", "2"]), "E": fx.table(sample_id=["S1", "S2"], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], steps, keys=["sample_id"]), "E": fx.schema(["sample_id", "g"], keys=["sample_id"])}, {}, {"P": fx.plot("A"), "Pe": fx.plot("E")})
    return describe(recipe, tables)


def test_a_step_the_app_cannot_read_that_leaves_the_name_but_changes_the_type_is_unsure_with_the_walks_reason():
    option = _with_one_step_in_a([fx.str_split(["sample_id"], "-")])         # the key becomes a list of parts: same name, other type, a step that is not read
    assert places_of(option) == ["T1:E"] and {n.table: n.code for n in option.unsure} == {"A": rfa.UNCERTAIN_LINK}
    assert option.unsure[0].reason.code == "step_not_read" and option.unsure[0].reason.get("action") == "polars_str_split"


def test_a_step_the_app_cannot_read_that_makes_the_key_leave_the_table_is_unsure_not_gone():
    option = _with_one_step_in_a([fx.unpivot(["sample_id"], ["v"])])          # the key's values move into a `value` column: where it went is not read
    assert places_of(option) == ["T1:E"] and {n.table: n.code for n in option.unsure} == {"A": rfa.NOT_FOLLOWED}
    assert option.unsure[0].reason.code == "step_not_read"


def test_steps_that_keep_the_key_under_its_name_and_type_do_not_hide_it():
    for step in (fx.fill_null(["sample_id"], "x"), fx.cast(["sample_id"], "String"), fx.with_columns(sample_id="pl.col('sample_id').str.to_uppercase()"),
                 fx.group_by(["sample_id"], n="pl.col('v').count()")):
        option = _with_one_step_in_a([step])
        assert places_of(option) == ["T1:A", "T1:E"] and option.not_reached == (), step["action"]


def test_a_table_that_recomputes_the_key_carries_the_note_so_the_user_knows_the_values_there_may_differ():
    """A column a step writes under its own name is the same column (D-0353), ticked; the values there may not be the ones in the file, so the place carries the walk's note."""
    option = _with_one_step_in_a([fx.with_columns(sample_id="pl.col('sample_id').str.to_uppercase()")])
    by_table = {p.table: p for p in option.places}
    assert [n.code for n in by_table["A"].notes] == ["recomputed_here"] and by_table["E"].notes == ()
    grouped = _with_one_step_in_a([fx.group_by(["sample_id"], n="pl.col('v').count()")])
    assert [n.code for n in {p.table: p for p in grouped.places}["A"].notes] == ["one_row_per_group_after_this_step"]


def test_a_key_in_two_columns_of_one_table_is_unsure_never_guessed():
    """B declares `sample_id` as its key and a join equates A's key with B's `ref`: the key family has two columns in B, and in the join (`sample_id`, `sample_id_right`).
    Which one a removal should name is not decided by the recipe: both tables are listed as unsure and not written."""
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "B": fx.table(ref=["S1", "S2"], sample_id=["S1", "S2"], w=[4, 5])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]), "B": fx.schema(["ref", "sample_id", "w"], keys=["sample_id"])},
                       {"J": fx.join(["A", "B"], [fx.join_step("B", on=("sample_id", "ref"))])}, {"P": fx.plot("J")})
    option = describe(recipe, tables)
    assert places_of(option) == ["T1:A"] and {n.table: n.code for n in option.unsure} == {"B": rfa.SEVERAL_COLUMNS, "J": rfa.SEVERAL_COLUMNS}
    assert option.unsure[0].reason.get("names") == ("ref", "sample_id")


def test_a_key_of_another_type_in_one_table_is_reported_in_the_place():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "N": fx.table(sample_id=[1, 2], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]), "N": fx.schema(["sample_id", "g"], keys=["sample_id"])}, {}, {"P": fx.plot("A"), "Pn": fx.plot("N")})
    option = describe(recipe, tables)
    assert {p.table: p.type for p in option.places} == {"A": "String", "N": "Int64"}
    assert option.types == ("Int64", "String") and option.types_differ is True


# =====================================================================================================================
# Applying it to the audit copy: "resequenced sample"
# =====================================================================================================================


def _resequenced(recipe, tables, ids=("S2",), comment="resequenced: results come later"):
    option = describe(recipe, tables)
    audit = start_audit(recipe, AUD)
    written = rfa.apply(audit, option, list(ids), comment, plans=oracle.replay(recipe, tables).plans)
    return option, audit, written


def test_a_resequenced_sample_is_gone_from_every_reached_table_and_every_table_built_from_them_and_nothing_else_changed():
    recipe, tables = fx.tiers(u_declares_key=True)
    option, audit, written = _resequenced(recipe, tables)
    assert written == tuple(f"audit_{AUD}_{k}" for k in range(1, len(option.places) + 1))
    before, after = oracle.replay(recipe, tables), oracle.replay(folded(audit.recipe), tables)
    nodes = sorted({n for (n, _) in before.frames if not n.startswith("DS:")})
    assert nodes, "the oracle replayed tables"
    for node in nodes:
        was, now = before.end(node), after.end(node)
        assert was is not None and now is not None, node
        if "sample_id" in was.columns:
            assert "S2" not in now["sample_id"].to_list(), f"S2 is gone from {node}"
            assert now.equals(was.filter(pl.col("sample_id") != "S2")), f"{node}: the other samples' rows are unchanged, in the same order"
        else:
            assert now.equals(was), f"{node} does not hold the key and did not change"
    assert "S2" in tables["U"]["sample_id"].to_list() and "S2" not in after.end("T1:U")["sample_id"].to_list(), "the table no plot reads"
    assert "S2" not in after.end("T1:JU")["sample_id"].to_list(), "the join no plot reads"
    assert before.end("T1:S").height == 4 and after.end("T1:S").height == 3, "the source frames of the oracle are untouched by the audit"


def test_every_step_is_written_at_tier_1_of_its_table_with_the_name_there_and_the_audit_list_form():
    recipe, tables = fx.tiers(u_declares_key=True)
    option, audit, written = _resequenced(recipe, tables, ("S2", "S3"))
    steps = {s.place: s for s in audit_copy.all_audit_steps(audit.recipe)}
    assert sorted(steps) == sorted(places_of(option)) and all(place.startswith("T1:") for place in steps)
    for place in option.places:
        step = steps[place.place].step
        assert step["action"] == "modif_filter" and step["column"] == place.column and step["op"] == "not_in" and step["value"] == ["S2", "S3"]
        assert step["na"] == "keep", "a row with no key is not the sample removed (the rule of the filter dialog for not-in)"
        assert step["audit_comment"] == "resequenced: results come later"
    assert audit.recipe["data_schemas"]["S"]["tier1"]["steps"] == recipe["data_schemas"]["S"]["tier1"]["steps"], "the author's list is untouched"
    assert audit_copy.integrity_errors(audit.recipe, recipe) == []


def test_a_row_with_no_key_is_kept():
    tables = {"A": pl.DataFrame({"sample_id": ["S1", None, "S2"], "v": [1, 2, 3]})}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"])}, {}, {"P": fx.plot("A")})
    audit = start_audit(recipe, AUD)
    rfa.apply(audit, describe(recipe, tables), ["S2"], "r", plans=oracle.replay(recipe, tables).plans)
    assert oracle.replay(folded(audit.recipe), tables).end("T1:A")["v"].to_list() == [1, 2]


def test_the_key_under_another_name_is_removed_by_the_name_it_has_there():
    tables = {"A": fx.table(sample_id=["S1", "S2", "S3"], v=[1, 2, 3]), "B": fx.table(sample_id=["S1", "S2", "S3"], w=[4, 5, 6])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], [fx.rename(sample_id="isolate")], keys=["sample_id"]), "B": fx.schema(["sample_id", "w"], keys=["sample_id"])},
                       {"J": fx.join(["A", "B"], [fx.join_step("B", on=("isolate", "sample_id"))])}, {"P": fx.plot("J")})
    _, audit, _ = _resequenced(recipe, tables)
    after = oracle.replay(folded(audit.recipe), tables)
    assert after.end("T1:A")["isolate"].to_list() == ["S1", "S3"] and after.end("T1:B")["sample_id"].to_list() == ["S1", "S3"] and after.end("T1:J")["isolate"].to_list() == ["S1", "S3"]


def test_it_does_nothing_by_itself_describe_then_nothing_applied():
    recipe, tables = fx.tiers(u_declares_key=True)
    audit = start_audit(recipe, AUD)
    describe(recipe, tables)
    assert audit_copy.all_audit_steps(audit.recipe) == [] and audit.recipe == recipe and audit.created == 0


# ---- apply is all or nothing ----


def _unchanged(audit, before_recipe, before_created):
    assert audit.recipe == before_recipe and audit.created == before_created


@pytest.mark.parametrize("values, comment, why", [
    ([], "r", "no value"), (None, "r", "no values at all"), (["S2", None], "r", "a missing value is not a sample"),
    (["S2"], "", "no reason"), (["S2"], "   ", "a reason of spaces"), ("S2", "r", "a text is not a list of values"), ([["S2"]], "r", "a list inside the list"),
])
def test_a_refused_apply_changes_nothing_not_even_the_counter(values, comment, why):
    recipe, tables = fx.tiers(u_declares_key=True)
    option, audit = describe(recipe, tables), start_audit(recipe, AUD)
    before, created = copy.deepcopy(audit.recipe), audit.created
    with pytest.raises(AuditCopyError):
        rfa.apply(audit, option, values, comment, plans=oracle.replay(recipe, tables).plans)
    _unchanged(audit, before, created)


def test_a_value_that_does_not_fit_the_type_of_the_key_in_one_table_refuses_the_whole_apply_and_names_the_place():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2]), "N": fx.table(sample_id=[1, 2], g=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"]), "N": fx.schema(["sample_id", "g"], keys=["sample_id"])}, {}, {"P": fx.plot("A"), "Pn": fx.plot("N")})
    option, audit = describe(recipe, tables), start_audit(recipe, AUD)
    before, created = copy.deepcopy(audit.recipe), audit.created
    with pytest.raises(AuditCopyError) as error:
        rfa.apply(audit, option, ["S2"], "r", plans=oracle.replay(recipe, tables).plans)
    assert "T1:N" in str(error.value) and "Int64" in str(error.value), "the plain sentence names the table and its type"
    _unchanged(audit, before, created)


def test_apply_refuses_an_option_that_is_not_offered():
    recipe, tables = fx.tiers(u_declares_key=True)
    option, audit = describe(recipe, tables, "country"), start_audit(recipe, AUD)
    with pytest.raises(AuditCopyError, match="not offered"):
        rfa.apply(audit, option, ["x"], "r", plans=oracle.replay(recipe, tables).plans)
    assert audit.recipe == recipe


def test_apply_refuses_an_option_that_no_longer_matches_the_recipe():
    recipe, tables = fx.tiers(u_declares_key=True)
    option = describe(recipe, tables)
    other, other_tables = fx.chain()
    audit = start_audit(other, AUD)
    with pytest.raises(AuditCopyError, match="no longer"):
        rfa.apply(audit, option, ["S2"], "r", plans=oracle.replay(other, other_tables).plans)
    assert audit.recipe == other


def test_a_failure_in_the_middle_takes_back_what_was_written_and_the_counter():
    recipe, tables = fx.tiers(u_declares_key=True)
    plans = oracle.replay(recipe, tables).plans
    option, audit = describe(recipe, tables), start_audit(recipe, AUD)
    before, created = copy.deepcopy(audit.recipe), audit.created
    real, calls = audit_copy.add_step, []

    def flaky(*args, **kwargs):
        calls.append(1)
        if len(calls) == 3:
            raise AuditCopyError("the third step fails")
        return real(*args, **kwargs)

    with mock.patch.object(rfa.audit_copy, "add_step", flaky):
        with pytest.raises(AuditCopyError, match="third"):
            rfa.apply(audit, option, ["S2"], "r", plans=plans)
    assert len(calls) == 3
    _unchanged(audit, before, created)


def test_apply_twice_gives_two_sets_of_steps_with_their_own_ids_never_a_silent_merge():
    recipe, tables = fx.chain()
    plans = oracle.replay(recipe, tables).plans
    option, audit = describe(recipe, tables), start_audit(recipe, AUD)
    first = rfa.apply(audit, option, ["S2"], "r1", plans=plans)
    second = rfa.apply(audit, option, ["S3"], "r2", plans=plans)
    assert len(first) == len(second) == 3 and set(first).isdisjoint(second)
    assert len(audit_copy.all_audit_steps(audit.recipe)) == 6


def test_a_single_table_recipe():
    tables = {"A": fx.table(sample_id=["S1", "S2"], v=[1, 2])}
    recipe = fx.recipe({"A": fx.schema(["sample_id", "v"], keys=["sample_id"])}, {}, {"P": fx.plot("A")})
    option, audit, written = _resequenced(recipe, tables, ("S1",))
    assert places_of(option) == ["T1:A"] and len(written) == 1
    assert oracle.replay(folded(audit.recipe), tables).end("T1:A")["sample_id"].to_list() == ["S2"]


# =====================================================================================================================
# Every shipped recipe
# =====================================================================================================================


def _shipped():
    base = ROOT / "config" / "data_analysis_recipes"
    return sorted(p for folder in ("pipelines", "templates", "retest", "experimental") for p in (base / folder).glob("*.yaml"))


@pytest.mark.parametrize("path", _shipped(), ids=lambda p: f"{p.parent.name}/{p.name}")
def test_on_every_shipped_recipe_the_option_is_a_list_or_not_offered_with_a_reason(path):
    raw, _problems = load_recipe(path)
    if raw is None:
        pytest.skip("the recipe does not load (a recipe that is broken on purpose)")
    for column in ("sample_id", "id", "no_such_column"):
        option = rfa.describe(raw, column)
        if option.offered:
            assert option.not_offered is None and (option.places or option.unsure), "offered: a list of tables, or the doubts that stop one (names only, no engine)"
            assert all(p.place == f"T1:{p.table}" and p.column for p in option.places)
            assert [p.place for p in option.places] == sorted({p.place for p in option.places}, key=[p.place for p in option.places].index), "no table twice"
        else:
            assert option.not_offered is not None and option.not_offered.code in rfa.NOT_OFFERED_CODES and option.places == ()
            assert rfa.not_offered_sentence(option.not_offered)


def test_the_demo_recipe_without_the_engine_reaches_what_the_names_prove_and_lists_the_rest_as_unsure():
    """Names only (no engine plan): 17 of the 27 tables that hold the key are proved by the declared columns and the steps the walk reads; the 10 behind a step it does not
    read are listed as unsure with the engine's missing plan as the reason, never guessed (the engine's plan reaches all 27: `app/tests/test_remove_from_all_demo.py`).
    The 28th table (`APEC_STEC_virulence_genes`) has no sample column and is not mentioned."""
    raw, _ = load_recipe(ROOT / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml")
    option, graph = rfa.describe(raw, "sample_id"), build_graph(raw)
    assert option.offered and len(graph.collections()) == 28
    assert len(option.places) == 17 and len(option.unsure) == 10 and {n.code for n in option.unsure} == {rfa.PLAN_FAILED}
    assert {p.table for p in option.places} | {n.table for n in option.not_reached} == set(graph.collections()) - {"APEC_STEC_virulence_genes"}
    assert not rfa.describe(raw, "Gene_name").offered and not rfa.describe(raw, "VF_gene").offered, "join columns that are not the declared key are not offered"
