"""The Blueprint AI agent's instruction text teaches only the recipe shape the checker accepts (review of step 4, D-0250, D-0253).

`config/ui/agents/blueprint_default.md` is read by the agent as its rules. If it showed `wrangling:`, a bare `steps:` container,
`spec: !include`, `label` on a group or a plot, `output_fields` or an old action name, the agent would propose recipes that the
checker refuses.

What this test checks, and what it does not. The examples are fragments (a table, a join, a group, a plot, a list of steps): they
have no data and are not a whole recipe, so the full recipe checker cannot run on them. The test therefore checks, for every
```yaml block of the file: it is valid YAML (an `!include` tag is allowed); every key of a table, a join, a group and a plot entry
is a key of that element in `libs/utils/src/utils/recipe_spec.yaml`; no old key of the specification is used; every step
names a registered action and passes the form schema of that action (the check of an upload); every layer is a registered
component. It does not check that the examples draw a figure.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_agent_instructions_shape.py -q
"""
import re
from pathlib import Path

import pytest
import yaml

from app.modules.data_analysis_recipe_validator import checker_catalogs, uploaded_recipe_report
from utils.recipe_check import spec

TEXT = (Path(__file__).resolve().parents[2] / "config/ui/agents/blueprint_default.md").read_text(encoding="utf-8")
BLOCKS = re.findall(r"```yaml\n(.*?)```", TEXT, flags=re.S)


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_multi_constructor("!", lambda loader, suffix, node: None)   # an !include tag is a place, not content


def _keys(element: str) -> set:
    e = spec()["elements"][element]
    return set(e["required"]) | set(e["optional"])


OLD_KEYS = {"wrangling", "spec", "output_fields", "final_contract", "label_of_group"}


def _walk(node, path=()):
    """Every (path, value) of a loaded block."""
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, path + (i,))


def _step_lists(data):
    """Every list of steps in a block: the value of a `steps` key, or the block itself when it is a bare list of steps."""
    found = []
    if isinstance(data, list):
        found.append(data)
    for path, value in _walk(data):
        if path and path[-1] == "steps" and isinstance(value, list):
            found.append(value)
    return found


def test_the_file_has_yaml_examples():
    assert len(BLOCKS) >= 6


@pytest.mark.parametrize("index", range(len(BLOCKS)))
def test_every_yaml_example_is_valid_yaml(index):
    yaml.load(BLOCKS[index], Loader=_Loader)


@pytest.mark.parametrize("index", range(len(BLOCKS)))
def test_no_example_uses_an_old_key(index):
    data = yaml.load(BLOCKS[index], Loader=_Loader)
    for path, _ in _walk(data):
        if path and isinstance(path[-1], str):
            assert path[-1] not in OLD_KEYS, f"old key {path[-1]!r} at {path}"
    # `label` is the old name of `ui_label` on a group and on a plot
    for name, group in (data.get("analysis_groups") or {}).items() if isinstance(data, dict) else []:
        assert "label" not in group, f"group {name}: `label` is `ui_label` now"
    if isinstance(data, dict) and "mapping" in data:
        assert "label" not in data and "title" not in data


@pytest.mark.parametrize("index", range(len(BLOCKS)))
def test_the_structure_keys_are_the_keys_of_the_specification(index):
    data = yaml.load(BLOCKS[index], Loader=_Loader)
    if not isinstance(data, dict):
        return
    for name, table in (data.get("data_schemas") or {}).items():
        assert set(table) <= _keys("schema"), (name, set(table) - _keys("schema"))
        assert set(table.get("source") or {}) <= _keys("source")
        for tier in ("tier1", "tier2"):
            if isinstance(table.get(tier), dict):
                assert set(table[tier]) <= _keys("tier"), (name, tier)
    for name, join in (data.get("joins") or {}).items():
        assert set(join) <= _keys("join"), (name, set(join) - _keys("join"))
        for tier in ("tier1", "tier2"):
            if isinstance(join.get(tier), dict):
                assert set(join[tier]) <= _keys("tier"), (name, tier)
    for name, group in (data.get("analysis_groups") or {}).items():
        assert set(group) <= _keys("group"), (name, set(group) - _keys("group"))
        for plot_id, entry in group["plots"].items():
            assert entry is None or set(entry) <= _keys("plot"), plot_id   # None: an !include of a plot file
    if "mapping" in data or "layers" in data:   # the content of an included plot file
        assert set(data) <= _keys("plot"), set(data) - _keys("plot")
        assert {"ui_label", "target_dataset", "mapping", "layers"} <= set(data)
        components = checker_catalogs()["components"]
        for layer in data["layers"]:
            assert set(layer) <= _keys("layer")
            assert layer["name"] in components, layer["name"]
    if set(data) == {"steps"} or set(data) == {"steps", "data_engine"}:
        assert isinstance(data["steps"], list)


@pytest.mark.parametrize("index", range(len(BLOCKS)))
def test_every_step_names_a_registered_action_and_fits_its_form(index):
    data = yaml.load(BLOCKS[index], Loader=_Loader)
    lists = _step_lists(data)
    for steps in lists:
        assert uploaded_recipe_report({"steps": steps}) == [], uploaded_recipe_report({"steps": steps})


def test_the_examples_hold_steps_of_every_kind_the_text_teaches():
    """A guard on the guard: the blocks hold steps (a tier in place, a tier file, a join), so the step check ran."""
    counts = [len(s) for b in BLOCKS for s in _step_lists(yaml.load(b, Loader=_Loader))]
    assert sum(counts) >= 6
    assert "polars_join" in TEXT and "polars_cast" in TEXT and "modif_filter" in TEXT


def test_the_text_names_no_old_action_and_no_old_plot_component():
    for old in ("bar_logic", "heatmap_logic"):
        assert old not in TEXT
    # the text may warn against old names in a sentence; no example may use one as an action
    assert not re.search(r"action:\s*(cast|join|mutate|filter_range|sort|fill_nulls)\b", TEXT)
