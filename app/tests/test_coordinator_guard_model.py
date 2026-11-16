"""The decision gate holds when the Agent call names a model (hook rule 5, M150 point 4).

A builder, builder-opus or reviewer started with `model: sonnet` or `model: haiku` passes the model rule of the hook;
it must still pass the decision rule. Same helpers as `test_coordinator_guard.py`.
"""
import pytest

from app.tests.test_coordinator_guard import GATED, ITEM, agent, project  # noqa: F401  (project is a fixture)


@pytest.mark.parametrize("kind", GATED)
@pytest.mark.parametrize("model", ["sonnet", "haiku", "SONNET"])
def test_the_gate_holds_when_the_call_names_a_cheap_model(project, kind, model):
    assert agent(project, kind, "no block here", model=model)[0] == 2
    assert agent(project, kind, f"Decisions\n{ITEM['D-0001']}", model=model)[0] == 0
    assert agent(project, kind, "NONE-CHECKED: tmpAI/scout_report.md", model=model)[0] == 0
    # the decision rule still refuses: a bare number, a number that is not DECIDED, a number that does not exist
    assert agent(project, kind, "Decisions\n- D-0001: x", model=model)[0] == 2
    assert agent(project, kind, f"Decisions\n{ITEM['D-0002']}", model=model)[0] == 2
    assert agent(project, kind, 'Decisions\n- D-0999: "the first decision of the test ledger"', model=model)[0] == 2
