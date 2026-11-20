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


def test_PROVISIONAL_where_the_recipe_cannot_say_what_a_step_does_the_gate_does_not_refuse_and_says_it_could_not_follow():
    """An unread step (a fill of missing values) between the table and the place: the recipe alone cannot say which column is which after it. The gate does NOT refuse (it
    would refuse by a guess) and the facts say `uncertain`; the engine's plan says the truth and the same rule refuses. The build of the unrefused drop fails at the join
    with an error and never silently (checked with the oracle). PROVISIONAL: the owner has not decided this case."""
    recipe, tables = F.chain(a_steps=[F.keep("val", "gt", 0.0), F.fill_null(["val"], 0.0)])
    blind = key_drop.DropGate(recipe).facts("T1:A", "sample_id")
    assert not blind.refused and blind.uncertain and blind.unfollowed and key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"]) is None
    _, real = setup(recipe, tables)
    assert key_drop.DropGate(recipe, real).facts("T1:A", "sample_id").refused
    assert key_drop.key_drop_problem(recipe, "T1:A", ["sample_id"], real) is not None
    assert O.replay(O.with_audit_drop(recipe, "T1:A", "sample_id"), tables).failures      # what the build does with a drop the blind gate let through: an error


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
