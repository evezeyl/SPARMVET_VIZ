"""The comparisons where the engine and the hand-written side differ TODAY (EQUALITY-CHECK-1, PROVISIONAL).

These tests fail on purpose: a difference is a finding, described in `FINDINGS.md`, not a test to bend. They are not
collected by the default run (`conftest.py`). Run them with:

  EQUALITY_FINDINGS=1 PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/equality/test_findings_open.py -q

When a finding is resolved (engine, recipe or the hand side, decided by Eve), delete its ids from `open_findings.py`:
the same case then runs in `test_recipe_equals_hand_written.py`.
"""
import pytest

from app.tests.equality.checks import all_cases, check
from app.tests.equality.open_findings import OPEN_FINDINGS

CASES = [c for c in all_cases() if c.id in OPEN_FINDINGS]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_open_finding(case):
    check(case)


def test_every_open_finding_names_a_real_case():
    assert OPEN_FINDINGS <= {c.id for c in all_cases()}
