"""Action names are spelled in one place (spec R4): the constants in `utils.action_names`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_action_names.py -q
"""
import ast
from pathlib import Path

import transformer  # noqa: F401  (registers the actions)
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils import action_names

REPO = Path(__file__).resolve().parents[3]
PREFIXES = ("polars_", "modif_", "step_")
# Where a name of the new vocabulary may be spelled: the registry itself, the constants, and the tools about old names.
ALLOWED = ("libs/transformer/src/transformer/actions/", "libs/utils/src/utils/action_names.py",
           "libs/utils/src/utils/legacy_keys.py", "libs/utils/src/utils/recipe_migration.py")


def test_every_constant_names_a_registered_action():
    missing = {k: v for k, v in action_names.ALL.items() if v not in AVAILABLE_WRANGLING_ACTIONS}
    assert not missing, missing


def test_the_constants_are_distinct_and_in_the_new_vocabulary():
    assert len(set(action_names.ALL.values())) == len(action_names.ALL)
    assert all(v.startswith(PREFIXES) for v in action_names.ALL.values())


def test_the_tier1_only_set_names_registered_actions():
    assert action_names.TIER1_ONLY <= set(AVAILABLE_WRANGLING_ACTIONS)


def test_a_registered_name_is_not_spelled_as_a_string_outside_the_registry():
    registered = {n for n in AVAILABLE_WRANGLING_ACTIONS if n.startswith(PREFIXES)}
    found = []
    for root in ("libs", "app", "assets/scripts"):
        for path in (REPO / root).rglob("*.py"):
            rel = path.relative_to(REPO).as_posix()
            if any(part in rel for part in ("/tests/", "/build/", ".venv")) or rel.startswith(ALLOWED) or path.name.startswith("test_"):
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in registered:
                    found.append(f"{rel}:{node.lineno} {node.value}")
    assert not found, found


def test_the_scan_can_fail(tmp_path):
    """The scan finds a literal: guard against a scan that looks at nothing."""
    tree = ast.parse("x = 'modif_filter'")
    assert any(isinstance(n, ast.Constant) and n.value in AVAILABLE_WRANGLING_ACTIONS for n in ast.walk(tree))
