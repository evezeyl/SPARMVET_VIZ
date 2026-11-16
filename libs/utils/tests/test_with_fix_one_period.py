"""One function writes "what happens. Suggestion: ..." for every reader (D-0099; fix round 2026-11-16).

`utils.fix_text.with_fix` joins a problem and its remedy with exactly one period. The command line (`Problem.text()`) is tested
here for EVERY advice code of the checker (the cases of `test_advice_texts.py`); HOME's gate note and Blueprint's Validate entry,
which read the same two fields, are tested in `app/tests/test_advice_one_sentence.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_with_fix_one_period.py -q
"""
import re

import pytest

from utils.fix_text import with_fix
from utils.recipe_check import Problem
from test_advice_texts import CASES, advices


def one_sentence(text):
    assert re.search(r"[.!?] Suggestion: ", text), text
    assert not re.search(r"[^.!?\s] Suggestion:", text), f"no period before Suggestion: {text}"
    assert not re.search(r"(?<!\.)\.\.(?!\.)", text), f"doubled period: {text}"


@pytest.mark.parametrize("code", sorted(CASES))
def test_the_command_line_text_of_every_advice_has_one_period_before_suggestion(code):
    found = advices(code)
    assert found
    for problem in found:
        one_sentence(problem.text())
        one_sentence(problem.text("r.yaml"))


def test_a_message_that_ends_with_a_period_gets_no_second_one():
    """J13 wrote its own final period; the text had '..' before the suggestion."""
    assert with_fix("It ends here.", "Suggestion: do this.") == "It ends here. Suggestion: do this."


def test_a_message_without_a_period_gets_one():
    assert with_fix("It ends here", "Suggestion: do this.") == "It ends here. Suggestion: do this."


@pytest.mark.parametrize("ending", ["!", "?"])
def test_a_question_or_an_exclamation_is_not_given_a_period(ending):
    assert with_fix(f"Why{ending}", "Suggestion: x") == f"Why{ending} Suggestion: x"


def test_a_trailing_space_is_not_kept():
    assert with_fix("It ends here ", "Suggestion: x") == "It ends here. Suggestion: x"


def test_an_ellipsis_is_left_as_it_is():
    assert with_fix("It goes on...", "Suggestion: x") == "It goes on... Suggestion: x"


def test_an_ordinary_fix_gets_its_label_and_a_suggestion_does_not():
    assert with_fix("Bad", "write 3") == "Bad. Fix: write 3"
    assert with_fix("Bad", "write 3", label="Tip") == "Bad. Tip: write 3"
    assert with_fix("Bad", "Suggestion: write 3", label="Tip") == "Bad. Suggestion: write 3"


def test_no_fix_leaves_the_problem_alone():
    assert with_fix("Bad.", "") == "Bad." and with_fix("Bad", "") == "Bad"


def test_the_problem_text_of_the_command_line_uses_the_one_function():
    problem = Problem("X1", "A", "a.b", "something is off.", "Suggestion: fix it.")
    assert problem.text() == "a.b : [X1] something is off. Suggestion: fix it."
    assert problem.text("r.yaml") == "r.yaml : a.b : [X1] something is off. Suggestion: fix it."
