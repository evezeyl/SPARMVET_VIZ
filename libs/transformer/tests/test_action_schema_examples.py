"""Every action's yaml_example agrees with its own ui_schema: same parameter names, same value shapes.

The schemas feed the Blueprint form and the recipe checker (spec section 8). Before this, eight parameters were declared
`string` while their example writes a list or a dictionary.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_action_schema_examples.py -q
"""
import pytest
import yaml

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.actions.base import ACTION_SCHEMAS
from utils.ui_schema import WIDGETS, expected_shape

SHAPE_OF = {dict: "mapping", list: "list"}
COMMON_KEYS = {"action", "id", "comment"}


def _examples():
    for name, schema in sorted(ACTION_SCHEMAS.items()):
        parsed = yaml.safe_load(schema.get("yaml_example", ""))
        for step in parsed if isinstance(parsed, list) else [parsed]:
            if isinstance(step, dict):
                yield name, schema, step


@pytest.mark.parametrize("name, schema, step", list(_examples()), ids=lambda v: v if isinstance(v, str) else "")
def test_the_example_uses_declared_parameters_with_the_declared_shape(name, schema, step):
    params = schema.get("params") or {}
    for key, value in step.items():
        if key in COMMON_KEYS:
            continue
        assert key in params, f"{name}: the example writes '{key}', which the schema does not declare"
        shape = expected_shape(params[key])
        if isinstance(value, dict):
            assert shape in ("mapping", "any"), f"{name}.{key}: the example writes a mapping, the schema declares {shape}"
        elif isinstance(value, list):
            assert shape in ("list", "list_of_mapping", "any"), f"{name}.{key}: the example writes a list, the schema declares {shape}"
            if shape == "list_of_mapping":
                assert all(isinstance(item, dict) for item in value), f"{name}.{key}: items must be mappings"


def test_every_widget_in_use_is_in_the_vocabulary():
    for name, schema in ACTION_SCHEMAS.items():
        for key, param in (schema.get("params") or {}).items():
            assert param["widget"] in WIDGETS, f"{name}.{key}: widget '{param['widget']}' is not in the vocabulary"
