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


README = Path(__file__).resolve().parents[1] / "README.md"
WORKFLOW_PAGE = Path(__file__).resolve().parents[3] / "docs" / "workflows" / "wrangling.qmd"
STATED_COUNT = re.compile(r"\b(\d+)\s+(?:registered\s+)?(?:atomic\s+)?(?:decorators|actions)\b")


def stated_counts(text: str) -> set[int]:
    return {int(n) for n in STATED_COUNT.findall(text)}


def test_a_number_of_actions_stated_in_the_docs_is_the_registry_count():
    for path in (PAGE, README, WORKFLOW_PAGE):
        wrong = stated_counts(path.read_text(encoding="utf-8")) - {len(AVAILABLE_WRANGLING_ACTIONS)}
        assert not wrong, f"{path.name} states {sorted(wrong)} actions, the registry holds {len(AVAILABLE_WRANGLING_ACTIONS)}"


def test_the_count_check_can_fail():
    assert stated_counts("All 41 registered actions carry") == {41}
    assert stated_counts("no number here") == set()


def test_readme_registry_table_lists_every_registered_action():
    text = README.read_text(encoding="utf-8")
    start = text.index("## Registered Action Registry")
    end = text.index("`sink_parquet`", start)
    listed = set(re.findall(r"`((?:polars|modif|step)_\w+)`", text[start:end]))
    registered = set(AVAILABLE_WRANGLING_ACTIONS)
    assert listed == registered, {"missing": sorted(registered - listed), "not_registered": sorted(listed - registered)}
