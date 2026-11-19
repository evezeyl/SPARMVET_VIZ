"""BP-SAVE-TUPLE-1: Apply on a multi-select step, then Save, must give a file every reader accepts.

The form hands a multi-select back as a TUPLE; the old save wrote `!!python/tuple`, which `yaml.safe_load` refuses.
The handler functions are run for real (cut out of `define_server`), with a stub of the form input.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_save_roundtrip.py -q
"""
import ast
from pathlib import Path

import yaml

from app.handlers import blueprint_handlers

SOURCE = Path(blueprint_handlers.__file__)


class _Val:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _Ui:
    def __init__(self):
        self.said = []

    def notification_show(self, message, **kwargs):
        self.said.append(message)


def _handlers(input_values, stack):
    from blueprint_arch.schema_registry import register
    from transformer.actions.base import ACTION_SCHEMAS
    from viz_factory.registry import COMPONENT_SCHEMAS
    register(ACTION_SCHEMAS, COMPONENT_SCHEMAS)
    ui = _Ui()
    ws = type("WS", (), {"selected_node_idx": _Val(0), "logic_stack": _Val(stack), "invalidated_from": _Val(None)})()
    ns = dict(vars(blueprint_handlers))
    ns.update(ui=ui, wrangle_studio=ws, _snapshot_state=lambda: None, input=input_values,
              safe_input=lambda i, k, d=None: i.get(k, d))
    define = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    for name in ("_bp_apply_node_handler", "_serialise_component_for_save"):
        fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == name)
        fn.decorator_list = []
        exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
    return ns, ws


def test_apply_with_a_multi_select_then_save_gives_a_file_that_safe_load_reads():
    stack = [{"action": "polars_fill_null", "params": {"columns": ["a"], "value": "x"}, "comment": "", "_tier": "tier1"}]
    chosen = ("sequence_type", "country")   # what the selectize gives back
    ns, ws = _handlers({"bp_form_columns": chosen, "bp_form_value_lit": "x", "bp_form_value_mode": "literal"}, stack)
    ns["_bp_apply_node_handler"]()
    applied = ws.logic_stack.get()[0]["params"]["columns"]
    assert type(applied) is list and applied == list(chosen)

    content = ns["_serialise_component_for_save"]("wrangling", ws.logic_stack.get(), "", "tier1")
    written = blueprint_handlers.safe_dump_recipe(content)           # what the save handler writes
    assert "python" not in written
    loaded = yaml.safe_load(written)
    assert loaded["steps"][0]["columns"] == list(chosen)      # a tier file holds `steps` (D-0250)


def test_the_recipe_writer_keeps_the_order_of_keys_and_writes_a_tuple_as_a_list():
    text = blueprint_handlers.safe_dump_recipe({"z": 1, "a": ("p", "q")})
    assert text.index("z:") < text.index("a:")
    assert yaml.safe_load(text) == {"z": 1, "a": ["p", "q"]}
