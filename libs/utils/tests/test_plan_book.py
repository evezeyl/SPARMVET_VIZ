"""The plan book (LBFB step 0a): the engine's plan of every place as a value; a failure is data, a missing place is a bug of the caller."""
import pytest

from utils.plan_book import Plan, PlanBook, PlanBookIncomplete, PlanFailure


def test_plan_has_names_types_and_exact_lookup():
    plan = Plan.of([("sample_id", "String"), ("Year", "Int64")])
    assert plan.names == ("sample_id", "Year")
    assert plan.has("Year") and not plan.has("year")          # names are exact: Polars is case sensitive
    assert plan.type_of("Year") == "Int64" and plan.type_of("year") is None


def test_book_of_literals_failure_and_missing_place():
    book = PlanBook.of({("T1:A", 0): [("a", "Int64")], ("T1:A", 1): "the engine said no"})
    assert book.get("T1:A", 0).names == ("a",)
    failure = book.get("T1:A", 1)
    assert isinstance(failure, PlanFailure) and failure.sentence == "the engine said no" and (failure.node, failure.step) == ("T1:A", 1)
    assert book.has("T1:A", 1) and not book.has("T1:A", 2)
    with pytest.raises(PlanBookIncomplete) as error:
        book.get("T1:A", 2)
    assert "T1:A" in str(error.value) and error.value.step == 2     # absence is named, never read as a failure
