"""Registry self-consistency for actions (spec section 8: AR2, AR4, AR5, AR6). No recipe needed.

AR2 is a ratchet: the keys an action's function reads from its step must equal the keys its schema declares. Today
`rename` and `split_column` also read aliases the schema does not declare (spec section 8, R2); they are listed here
with the issue that removes them, so a NEW undeclared read fails the test and removing an alias forces the list to
shrink.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_action_registry_consistency.py -q
"""
import ast
import importlib
import inspect
import textwrap
from collections import Counter
from pathlib import Path

import pytest
import yaml

import transformer
import transformer.actions  # noqa: F401
from transformer.actions.base import ACTION_SCHEMAS, AVAILABLE_WRANGLING_ACTIONS

SRC = Path(transformer.__file__).parent
COMMON = {"action", "id", "comment", "description"}
# Keys the engine adds to a step before it reaches the action (spec section 8, R3: check ST09 refuses them in a recipe).
ENGINE_KEYS = {"__right_df__", "__metadata__"}
# Aliases read by the function but not declared (removed with the recipes that use them: issue #78).
KNOWN_ALIAS_READS = {
    "rename": {"target_column"},
    "split_column": {"separator", "source", "target_column"},
}
# Read only after the action itself wrote it, or declared on an action that delegates the reading.
INTERNAL_WRITES = {"join_filter": {"how"}}
# Actions that read nothing themselves because they hand the step to another function.
DELEGATING = {"unique", "join", "join_filter"}
# Engine-internal actions (spec section 8, R4; open point O11): no schema, no keys to compare.
NO_SCHEMA = {"scan_parquet", "sink_parquet"}


def _spec_reads(fn):
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    reads = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and getattr(node.value, "id", "") == "spec" \
                and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            reads.add(node.slice.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" \
                and getattr(node.func.value, "id", "") == "spec" and node.args \
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            reads.add(node.args[0].value)
    return reads


def test_AR2_an_action_reads_only_what_its_schema_declares():
    problems = {}
    for name, fn in AVAILABLE_WRANGLING_ACTIONS.items():
        if name in NO_SCHEMA or name in DELEGATING:
            continue
        declared = set(ACTION_SCHEMAS[name]["params"])
        extra = _spec_reads(fn) - declared - COMMON - ENGINE_KEYS - INTERNAL_WRITES.get(name, set())
        if extra != KNOWN_ALIAS_READS.get(name, set()):
            problems[name] = {"reads_but_undeclared": sorted(extra), "known": sorted(KNOWN_ALIAS_READS.get(name, set()))}
    assert problems == {}, problems


def test_AR2b_the_actions_without_a_schema_are_exactly_the_two_engine_internal_ones():
    assert set(AVAILABLE_WRANGLING_ACTIONS) - set(ACTION_SCHEMAS) == NO_SCHEMA


@pytest.mark.parametrize("name", sorted(ACTION_SCHEMAS))
def test_AR4_every_wraps_resolves_to_an_importable_object(name):
    for wrapped in ACTION_SCHEMAS[name].get("wraps") or []:
        obj = importlib.import_module(wrapped["lib"])
        for attr in wrapped["attr_path"]:
            assert hasattr(obj, attr), f"{name}: {wrapped['lib']}.{'.'.join(wrapped['attr_path'])} does not exist"
            obj = getattr(obj, attr)


def test_AR5_every_action_named_by_an_example_is_registered():
    for name, schema in ACTION_SCHEMAS.items():
        parsed = yaml.safe_load(schema["yaml_example"])
        for step in parsed if isinstance(parsed, list) else [parsed]:
            assert step["action"] in AVAILABLE_WRANGLING_ACTIONS, f"{name}: the example names '{step['action']}'"


def test_AR6_no_action_name_is_registered_twice_in_the_source():
    names = []
    for path in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "register_action" and node.args \
                    and isinstance(node.args[0], ast.Constant):
                names.append(node.args[0].value)
    repeated = [n for n, c in Counter(names).items() if c > 1]
    assert repeated == [], f"registered more than once (the later one silently wins): {repeated}"
    assert len(names) >= len(AVAILABLE_WRANGLING_ACTIONS)
