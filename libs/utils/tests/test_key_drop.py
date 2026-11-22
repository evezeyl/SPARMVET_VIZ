"""The rule of a key drop, by place (LBFB step 4, D-0358 which modulates D-0297): `utils.key_drop` and the plan the recipe alone can give (`declared_plans`).

The rule is ONE: the lines of a drop walk and the gate that `add_step`, `integrity_errors`, the checker and HOME ask are the same `LineageIndex.drop_facts`; these tests
hold the gate to the walk (same verdict, same joins) on every fixture, and state what the gate does where the recipe alone cannot say (PROVISIONAL).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_key_drop.py -q
"""
import copy

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import setup
from test_lineage_drop import counting_plot, fixtures, other_names

from utils import key_drop
from utils.audit_copy import AuditCopyError, add_step, start_audit
from utils.declared_plans import declared_plan_book
from utils.lineage_records import DropFacts
from utils.plan_book import Plan, PlanFailure
from utils.recipe_graph import build_graph


def needs(facts):
    return sorted((n.step.node, n.step.step, n.side, n.name) for n in facts.needs if n.certain)


# ----------------------------------------------------------------------------------------------------------------------------- the gate

def test_the_gate_refuses_where_a_join_is_later_and_allows_where_it_is_not_with_the_sentence_of_the_rule():
    recipe, _ = F.chain()
    sentence = key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"])
    assert "Cannot drop the column 'sample_id' at T1:A" in sentence and "step 1 of T1:J" in sentence and "is read as a join key by" in sentence
    assert "row filter or a removal by key" in sentence
    for place in ("T1:J", "T2:J", "T2:A", "T3:P1", "T3:P2"):
        assert key_drop.key_drop_problem(recipe, place, ["sample_id"]) is None, place
    assert key_drop.key_drop_problem(recipe, "T1:A", ["val"]) is None
    assert key_drop.key_drop_problem(recipe, "T1:A", ["val", "sample_id"]).count("Cannot drop the column") == 1      # only the key is named


def test_the_gate_names_every_refused_column_of_one_drop():
    recipe, _ = F.chain()
    both = F.chain(keys=("sample_id",))[0]
    both["joins"]["J"]["tier1"]["steps"][0]["on"] = ["sample_id", "country"]
    both["data_schemas"]["B"] = F.schema(["sample_id", "country", "lab"], keys=["sample_id"])
    text = key_drop.key_drop_problem(both, "T1:A", ["sample_id", "country"])
    assert "'sample_id' at T1:A" in text and "'country' at T1:A" in text


def test_the_gate_judges_nothing_it_cannot_judge():
    recipe, _ = F.chain()
    assert key_drop.key_drop_problem(recipe, "T1:NOPE", ["sample_id"]) is None             # no such place: the copy refuses the place itself
    assert key_drop.key_drop_problem(recipe, "T1:A", "sample_id") is None and key_drop.key_drop_problem(recipe, "T1:A", [3, None]) is None
    broken = copy.deepcopy(recipe)
    broken["analysis_groups"]["g"]["plots"]["P1"].pop("target_dataset")
    gate = key_drop.DropGate(broken)
    assert gate.graph is None and gate.error and gate.problem("T1:A", ["sample_id"]) is None and gate.facts("T1:A", "sample_id") is None
    assert key_drop.key_drop_problem("not a recipe", "T1:A", ["sample_id"]) is None


def test_the_rule_reads_the_recipe_the_author_wrote_audit_steps_change_no_verdict():
    recipe, _ = F.chain()
    audit = start_audit(recipe, "1a2b3c4d")
    add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["val"]}, "why")
    add_step(audit, "T3:P2", {"action": "polars_drop", "columns": ["sample_id"]}, "why")                  # allowed: by place
    with pytest.raises(AuditCopyError, match="column 'sample_id' at T1:A"):
        add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["sample_id"]}, "why")
    assert key_drop.key_drop_problem(audit.recipe, "T1:A", ["sample_id"]) == key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"])


def test_a_refused_step_changes_nothing_and_does_not_use_up_a_number():
    recipe, _ = F.chain()
    audit = start_audit(recipe, "1a2b3c4d")
    before = copy.deepcopy(audit.recipe)
    with pytest.raises(AuditCopyError):
        add_step(audit, "T1:B", {"action": "polars_drop", "columns": ["sample_id"]}, "why")
    assert audit.recipe == before and audit.created == 0


def test_the_place_of_a_list_is_found_from_its_path():
    recipe, _ = F.chain()
    gate = key_drop.DropGate(recipe)
    assert [gate.place_of_steps_path(p) for p in ("data_schemas.A.tier1.steps", "joins.J.tier2.steps", "analysis_groups.g.plots.P1.tier3.steps", "joins.NOPE.tier1.steps")] == [
        "T1:A", "T2:J", "T3:P1", None]


# ----------------------------------------------------------------------------------------------------------------------------- the plan the recipe alone gives

def test_the_declared_plan_has_the_columns_of_the_engines_plan_on_every_fixture_whose_steps_are_all_read():
    seen = 0
    for name, recipe, tables in fixtures():
        graph = build_graph(recipe)
        declared, real = declared_plan_book(graph), O.replay(recipe, tables).plans
        for node in graph.nodes():
            for k in range(len(graph.node(node).steps) + 1):
                got, want = declared.get(node, k), real.get(node, k)
                assert isinstance(got, Plan), (name, node, k, got)
                assert isinstance(want, Plan) and sorted(got.names) == sorted(want.names), (name, node, k, got.names, want.names)
                assert {t for _, t in got.columns} == {""}, "types are not known here and are never compared across places"
                seen += 1
    assert seen > 150


def test_a_step_the_recipe_does_not_say_is_a_failure_and_so_is_everything_below_it():
    recipe, _ = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    book = declared_plan_book(build_graph(recipe))
    assert isinstance(book.get("T1:A", 1), Plan) and isinstance(book.get("T1:A", 2), PlanFailure)
    assert "does not say what the step polars_fill_null does" in book.get("T1:A", 2).sentence
    assert all(isinstance(book.get(n, 0), PlanFailure) for n in ("T2:A", "T3:P2", "T1:J"))      # J starts from A, P2 reads A
    assert isinstance(book.get("T1:B", 0), Plan) and isinstance(book.get("T1:B", 0 + len(build_graph(recipe).node("T1:B").steps)), Plan)   # B is untouched


def test_a_source_with_no_declared_columns_has_no_plan():
    recipe, _ = F.chain()
    recipe["data_schemas"]["A"]["input_fields"] = {}
    book = declared_plan_book(build_graph(recipe))
    assert isinstance(book.get("DS:A", 0), PlanFailure) and isinstance(book.get("T1:J", 0), PlanFailure) and isinstance(book.get("DS:B", 0), Plan)


def test_a_join_key_the_table_does_not_have_is_a_failure_like_the_engines():
    recipe, _ = F.chain()
    recipe["joins"]["J"]["tier1"]["steps"][0]["on"] = "nope"
    book = declared_plan_book(build_graph(recipe))
    assert isinstance(book.get("T1:J", 1), PlanFailure) and "nope" in book.get("T1:J", 1).sentence


# ----------------------------------------------------------------------------------------------------------------------------- the gate and the walk are one rule

def test_the_gate_with_the_declared_plan_gives_the_verdict_of_the_walk_with_the_engines_plan_on_every_column_of_every_fixture():
    """The two plans give the same joins for the same drop: the rule does not depend on which plan it is handed, only on the lineage."""
    compared = refused = 0
    for name, recipe, tables in fixtures():
        graph, real = setup(recipe, tables)
        by_declared, by_engine = key_drop.DropGate(recipe), key_drop.DropGate(recipe, real)
        for node in graph.nodes():
            plan = real.get(node, len(graph.node(node).steps))
            if node.startswith("DS:") or not isinstance(plan, Plan):
                continue
            for column in plan.names:
                a, b = by_declared.facts(node, column), by_engine.facts(node, column)
                assert needs(a) == needs(b) and a.refused == b.refused and bool(a.declared) == bool(b.declared), (name, node, column, needs(a), needs(b))
                compared += 1
                refused += b.refused
    assert compared > 150 and refused >= 8


def test_where_the_recipe_cannot_say_what_a_step_does_the_drop_is_refused_in_one_sentence_that_says_the_app_cannot_YET_follow_the_column():
    """D-0460 ("B; if needed we try to find a solution later"; it replaces D-0449, which allowed such a drop with a warning): an unread step (a fill of missing values) between the
    table and the place: the recipe alone cannot say which column is which after it. The gate does not claim the column is a key (it would be a guess: `refused` is False, the facts
    say `uncertain`) but it does NOT write the drop: `problem` is ONE sentence. It names the column and the place, the step where the app loses it and why, says the app cannot YET
    follow it (the capital word is decided for the join, D-0454; the whole wording is PROVISIONAL) and what the user can do instead. It makes no promise about the build.
    With the engine's plan the same rule refuses by the join that needs the key (certain), with the sentence of the key."""
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    blind = key_drop.DropGate(recipe).facts("T1:A", "sample_id")
    assert not blind.refused and blind.uncertain and blind.unfollowed
    said = key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"])
    assert said and said.startswith("The app cannot YET follow the column 'sample_id' at T1:A to the end") and "read as a join key" not in said
    assert "could not work out the columns of T1:A" in said and "polars_fill_null" in said and "the drop is not written" in said      # no engine here: the recipe alone cannot say what the step does
    assert "Suggestion: for 'sample_id' the app finds no place where it can show that this drop works, so none can be written for now." in said and "removes the column for that plot only" not in said   # blind: nothing is offered, nothing is claimed
    assert said.count(". ") == 1 and said.endswith("."), "two short sentences, the second after the label"
    assert "may fail" not in said and "will fail" not in said and "Warning" not in said and "pl.all()" not in said and "Cannot tell" not in said      # no promise, no leftover of the old texts
    _, real = setup(recipe, tables)
    assert key_drop.DropGate(recipe, real).facts("T1:A", "sample_id").refused
    certain = key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"], real)
    assert certain and "it is read as a join key by" in certain and "YET" not in certain
    assert O.replay(O.with_audit_drop(recipe, "T1:A", "sample_id"), tables).failures      # what the engine does with the drop if it were written: an error


def test_the_audit_copy_does_not_write_a_drop_the_walk_cannot_follow_blind_nor_with_the_plan_when_a_join_needs_it():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    audit = start_audit(recipe, "1a2b3c4d")
    with pytest.raises(AuditCopyError, match="cannot YET follow the column 'sample_id' at T1:A"):
        add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["sample_id"]}, "why")      # blind: not written
    assert audit.created == 0 and audit.recipe == recipe
    _, real = setup(recipe, tables)
    with pytest.raises(AuditCopyError, match="read as a join key"):
        add_step(audit, "T1:A", {"action": "polars_drop", "columns": ["sample_id"]}, "why", plans=real)
    assert audit.created == 0 and audit.recipe == recipe


def test_the_refusal_is_none_where_nothing_is_uncertain_and_for_columns_that_are_not_judged():
    recipe, _ = F.chain()
    assert key_drop.key_drop_problem(recipe, "T1:A", ["val"]) is None      # certain: allowed
    assert key_drop.key_drop_problem(recipe, "T1:NOPE", ["val"]) is None and key_drop.key_drop_problem(recipe, "T1:A", "val") is None
    assert key_drop.key_drop_problem("not a recipe", "T1:A", ["val"]) is None
    blind, _ = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    assert key_drop.key_drop_problem(blind, "T3:P2", ["sample_id"]) is None                                    # a plot: nothing is built from it


def test_the_refusal_names_every_column_it_could_not_follow_and_only_those():
    recipe, _ = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    said = key_drop.key_drop_problem(recipe, "T1:A", ["country", "year"])
    assert "'country'" in said and "'year'" in said and said.count("The app cannot YET follow") == 1
    assert "'val'" not in said


def test_a_certain_need_wins_over_an_uncertain_column_in_the_same_drop():
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    _, real = setup(recipe, tables)
    said = key_drop.key_drop_problem(recipe, "T1:A", ["sample_id", "country"], real)
    assert "Cannot drop the column 'sample_id' at T1:A" in said and "YET" not in said


def test_the_refusal_says_a_plot_would_read_the_other_tables_column_under_the_same_name_when_a_join_gave_it_a_suffix():
    """The case that a build does NOT stop on: the dropped column had the same name as a column of the other table of a join, the join had given that one a suffix; with the drop it
    keeps its own name, and a step or a plot that reads the name reads the other table's column. The sentence says it, with the names, and does NOT say that the plot cannot be drawn
    (it is drawn, with the other table's values: the review of 2026-11-21 found that false sentence)."""
    recipe = F.recipe({"A": F.schema(["sample_id", "lab", "x"], [], [F.unpivot(["x"], ["sample_id"])], keys=["sample_id"]), "B": F.schema(["sample_id", "lab"], keys=["sample_id"])},
                      {"J": F.join(["A", "B"], [F.join_step("B")])}, {"P": F.plot("J"), "Q": F.plot("A")})
    tables = {"A": F.table(sample_id=F.IDS, lab=["a1", "a2", "a3", "a4", "a5"], x=["x1", "x2", "x3", "x4", "x5"]), "B": F.table(sample_id=F.IDS, lab=["b1", "b2", "b3", "b4", "b5"])}
    _, real = setup(recipe, tables)
    facts = key_drop.DropGate(recipe, real).facts("T1:A", "lab")
    assert facts.uncertain and not facts.refused
    said = key_drop.key_drop_problem(recipe, "T1:A", ["lab"], real)
    assert said.startswith("The app cannot YET follow the column 'lab' at T1:A")
    assert "'lab_right'" in said and "table B" in said and "step 1 of T1:J" in said and "under the name 'lab'" in said and "a plot" in said
    assert "cannot be drawn" not in said and "no error" not in said and "stop with an error" not in said
    built_before, built_after = O.replay(recipe, tables).end("T1:J"), O.replay(O.with_audit_drop(recipe, "T1:A", "lab"), tables).end("T1:J")
    assert built_before.columns == ["sample_id", "lab", "x", "lab_right"] and built_after.columns == ["sample_id", "x", "lab"]
    assert built_after["lab"].to_list() == ["b1", "b2", "b3", "b4", "b5"], "the column named lab is now the other table's: that is what the sentence says"


def test_the_refusal_names_the_step_and_the_plot_the_walk_reads_downstream_without_promising_a_failure():
    recipe, tables = F.chain()
    recipe["data_schemas"]["A"]["tier2"] = {"steps": [{"action": "polars_select", "exprs": ["sample_id", "year", "val"]}]}
    plots = recipe["analysis_groups"]["g"]["plots"]
    plots["P3"] = {**F.plot("A"), "mapping": {"x": "year"}}
    plots["R"] = F.plot("A", tier3=[F.unpivot(["val"], ["sample_id"])])             # an unpivot the walk does not read: `year` is not named by it, so the app loses it there
    _, real = setup(recipe, tables)
    said = key_drop.key_drop_problem(recipe, "T1:A", ["year"], real)
    assert said and "it reaches step 1 of T3:R (polars_unpivot), a step the app cannot read" in said
    assert "step 1 of T2:A (polars_select) names 'year'" in said and "the plot 'P3' draws 'year'" in said and "'P2'" not in said
    assert "will stop" not in said and "cannot be drawn" not in said and "may fail" not in said and "will fail" not in said


def test_a_plot_is_never_refused_even_when_nothing_is_known_about_its_table():
    """Nothing is built from a plot: the answer does not depend on the plan, so a plan that fails above does not turn the drop into an unknown."""
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    facts = key_drop.DropGate(recipe).facts("T3:P2", "sample_id")
    assert facts == DropFacts("T3:P2", "sample_id") and not facts.refused and not facts.uncertain


def test_the_facts_of_a_column_the_place_does_not_have_are_empty_and_a_drop_of_it_is_not_this_rules_business():
    recipe, _ = F.chain()
    assert key_drop.key_drop_problem(recipe, "T1:B", ["val"]) is None                    # `val` is A's: the engine reports a missing column
    assert key_drop.DropGate(recipe).facts("T1:B", "val") == DropFacts("T1:B", "val")


def test_the_rule_follows_a_key_under_another_name_through_the_declared_plan_too():
    recipe, _ = other_names()
    assert "'isolate' at T1:B" in key_drop.key_drop_problem(recipe, "T1:B", ["isolate"]) and key_drop.key_drop_problem(recipe, "T1:B", ["lab"]) is None
    assert key_drop.key_drop_problem(recipe, "T2:J", ["id"]) is None
    assert key_drop.key_drop_problem(copy.deepcopy(recipe), "T1:A", ["sample_id"]) is not None


def test_a_column_that_is_not_the_one_a_join_reads_is_not_refused_by_its_name():
    """Dropping a column named like a join key but that is a different column is allowed (never by name alone): `sample_id` of a table that no join reads."""
    recipe, _ = counting_plot()
    recipe = copy.deepcopy(recipe)
    recipe["data_schemas"]["Z"] = F.schema(["sample_id", "other"], keys=["sample_id"])
    assert key_drop.key_drop_problem(recipe, "T1:Z", ["sample_id"]) is None and key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"]) is not None
