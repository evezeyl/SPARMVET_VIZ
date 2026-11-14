"""The action page of the docs lists exactly the registered actions.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_docs_action_page.py -q
"""
import re
from pathlib import Path

import transformer  # noqa: F401  (registers the actions)
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

PAGE = Path(__file__).resolve().parents[3] / "docs" / "appendix" / "transformer_actions.qmd"
HEADING = re.compile(r"^#### `([^`]+)`\s*$", re.MULTILINE)


def page_actions(text: str) -> set[str]:
    return set(HEADING.findall(text))


def test_page_lists_every_registered_action_and_no_other():
    documented = page_actions(PAGE.read_text(encoding="utf-8"))
    registered = set(AVAILABLE_WRANGLING_ACTIONS)
    assert documented == registered, {"missing_on_page": sorted(registered - documented),
                                      "not_registered": sorted(documented - registered)}


def test_the_check_can_fail_when_a_heading_is_removed():
    text = PAGE.read_text(encoding="utf-8")
    first = next(iter(page_actions(text)))
    broken = text.replace(f"#### `{first}`", "#### removed", 1)
    assert page_actions(broken) != set(AVAILABLE_WRANGLING_ACTIONS)
