"""Registry self-consistency for plot components (spec section 8: AR4, AR5, AR6). No recipe needed.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_component_registry_consistency.py -q
"""
import ast
import importlib
from collections import Counter
from pathlib import Path

import pytest
import yaml

import viz_factory  # noqa: F401
from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS

SRC = Path(viz_factory.__file__).parent


@pytest.mark.parametrize("name", sorted(COMPONENT_SCHEMAS))
def test_AR4_every_wraps_resolves_to_an_importable_object(name):
    for wrapped in COMPONENT_SCHEMAS[name].get("wraps") or []:
        obj = importlib.import_module(wrapped["lib"])
        for attr in wrapped["attr_path"]:
            assert hasattr(obj, attr), f"{name}: {wrapped['lib']}.{'.'.join(wrapped['attr_path'])} does not exist"
            obj = getattr(obj, attr)


def test_AR5_every_component_named_by_an_example_is_registered():
    for name, schema in COMPONENT_SCHEMAS.items():
        example = yaml.safe_load(schema["yaml_example"])
        for layer in example.get("layers", []):
            assert layer["name"] in PLOT_COMPONENTS, f"{name}: the example names '{layer['name']}', which is not registered"


def test_AR6_no_component_name_is_registered_twice_in_the_source():
    names = []
    for path in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "register_plot_component" and node.args:
                if isinstance(node.args[0], ast.Constant):
                    names.append(node.args[0].value)
    repeated = [n for n, c in Counter(names).items() if c > 1]
    assert repeated == [], f"registered more than once (the later one silently wins): {repeated}"
    assert len(names) >= len(PLOT_COMPONENTS)
