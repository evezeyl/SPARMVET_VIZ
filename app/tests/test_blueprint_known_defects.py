"""Defects found while building GATE-GAP-1, each pinned by a strict xfail until its own task fixes it (not fixed here).

BP-SAVE-TUPLE-1 (fixed, the test below is a normal test now)  Blueprint's step save writes a multi-select parameter as `- !!python/tuple` and the file no longer loads.
Steps: Blueprint, open a recipe with a `polars_fill_null` step, click the step, press Apply (the form re-reads `columns`
from the selectize, which Shiny returns as a TUPLE), press Save. `_bp_apply_node_handler` keeps `[tuple]` for `columns`
(`val if isinstance(val, list) else [val]`) and `_handle_data_analysis_recipe_save_internal` writes it with the default
`yaml.dump`, which emits the tuple tag; `yaml.safe_load` (HOME's loader) refuses it: HOME rejects the recipe.

BP-GLIMPSE-ANCHOR-1  (browser, test_shiny_blueprint_known_defects.py)
"""
import ast
from pathlib import Path

import pytest
import yaml

from app.handlers import blueprint_handlers
from app.tests.test_blueprint_failed_load import Ui, Val

SOURCE = Path(blueprint_handlers.__file__)


def test_a_multi_select_parameter_is_saved_as_a_plain_list(monkeypatch):
    from blueprint_arch.schema_registry import register
    from transformer.actions.base import ACTION_SCHEMAS
    from viz_factory.registry import COMPONENT_SCHEMAS
    register(ACTION_SCHEMAS, COMPONENT_SCHEMAS)
    ui = Ui()
    monkeypatch.setattr(blueprint_handlers, "ui", ui)
    ws = type("WS", (), {
        "selected_node_idx": Val(0),
        "logic_stack": Val([{"action": "polars_fill_null", "params": {"columns": ["sequence_type"], "value": "x"},
                             "comment": "", "_tier": "tier1"}]),
        "invalidated_from": Val(None),
    })()
    ns = dict(vars(blueprint_handlers))
    ns.update(ui=ui, wrangle_studio=ws, _snapshot_state=lambda: None,
              input={"bp_form_columns": ("sequence_type",), "bp_form_value_lit": "x", "bp_form_value_mode": "literal"},
              safe_input=lambda i, k, d=None: i.get(k, d))
    tree = ast.parse(SOURCE.read_text())
    define = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    for name in ("_bp_apply_node_handler", "_serialise_component_for_save"):
        fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == name)
        fn.decorator_list = []
        exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)

    ns["_bp_apply_node_handler"]()
    nodes = ws.logic_stack.get()
    content = ns["_serialise_component_for_save"]("wrangling", nodes, "", "tier1")
    written = yaml.dump(content, default_flow_style=False, sort_keys=False)   # what the save handler does

    loaded = yaml.safe_load(written)                                          # what HOME's loader does
    assert loaded["steps"][0]["columns"] == ["sequence_type"]       # a tier file holds `steps` (D-0250)
