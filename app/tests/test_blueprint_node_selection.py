"""Blueprint: what a click on a join node shows (D-0250), and what happens when the join is in an old shape.

`handle_node_selection` (`app/modules/wrangle_studio.py`) reads the steps of a join through `DataWrangler.tier_steps(join, "tier1")`.
The closure of `define_server` is cut out by `ast` and run with small stand-ins (as in `test_blueprint_tier_files.py`):
`define_server` needs a session. A join in the old shape (`steps:` as a container of the join, or tier1 written as a list) is
refused by `tier_steps`; the click must tell the user in plain words and must not raise inside the reactive effect (a raise there
ends the effect and the user sees nothing).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_node_selection.py -q
"""
import ast
from pathlib import Path
from types import SimpleNamespace

import yaml

from app.modules import wrangle_studio

SOURCE = Path(wrangle_studio.__file__)


class Val:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeUi:
    def __init__(self):
        self.shown = []

    def notification_show(self, message, **kwargs):
        self.shown.append((str(message), kwargs.get("type")))


def click(recipe_text: str, node_id: str = "J"):
    """Run the node-selection closure for a click on `node_id`; returns (the stack the user sees, the notifications)."""
    ns = dict(vars(wrangle_studio))
    cls = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "WrangleStudio")
    define = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == "handle_node_selection")
    fn.decorator_list = []
    ui = FakeUi()
    ns.update(ui=ui)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "handle_node_selection", "exec"), ns)
    studio = SimpleNamespace(active_raw_yaml=Val(recipe_text), active_viz_id=Val("a plot"), logic_stack=Val(["stale"]))
    ns["self"] = studio
    ns["input"] = SimpleNamespace(blueprint_node_clicked=lambda: node_id)
    ns["handle_node_selection"]()
    return studio, ui


NEW_JOIN = """
id: r
joins:
  J:
    ingredients: [{dataset_id: A}, {dataset_id: B}]
    tier1:
      steps:
        - {action: polars_join, right_ingredient: B, 'on': [sample_id], how: left, maintain_order: left_right}
        - {action: modif_filter, column: reads, op: ge, value: 15, na: remove, comment: low reads}
    tier2:
      steps: []
"""


def test_a_click_on_a_join_in_the_new_shape_shows_the_steps_of_its_tier_1():
    studio, ui = click(NEW_JOIN)
    stack = studio.logic_stack.get()
    assert [n["action"] for n in stack] == ["polars_join", "modif_filter"]
    assert stack[0]["params"]["right_ingredient"] == "B" and stack[1]["comment"] == "Inherited from Data analysis recipe"
    assert studio.active_viz_id.get() is None            # a join is not a plot
    assert not [m for m in ui.shown if m[1] == "error"]


def test_a_join_with_no_tier_1_steps_gives_an_empty_stack_and_no_error():
    studio, ui = click("id: r\njoins:\n  J:\n    ingredients: []\n    tier1:\n      steps: []\n")
    assert studio.logic_stack.get() == []
    assert not [m for m in ui.shown if m[1] == "error"]


def test_a_click_on_a_node_that_is_not_a_join_leaves_the_stack_empty():
    studio, _ = click(NEW_JOIN, node_id="not_a_join")
    assert studio.logic_stack.get() == []


def test_a_join_in_the_old_shape_is_told_in_plain_words_and_does_not_raise():
    """Old shape: the steps in a `steps:` container of the join. `tier_steps` refuses it (DataAnalysisRecipeError)."""
    old = "id: r\njoins:\n  J:\n    ingredients: []\n    steps:\n      - {action: join, right_ingredient: B}\n"
    studio, ui = click(old)                                  # must not raise
    errors = [m for m in ui.shown if m[1] == "error"]
    assert len(errors) == 1
    text = errors[0][0]
    assert "J" in text and "not a key of a table or a join any more" in text and "migrate_recipe_engine_keys" in text
    assert studio.logic_stack.get() == []                   # nothing stale is left on screen
    assert studio.active_viz_id.get() is None


def test_a_join_with_tier_1_written_as_a_list_is_told_too():
    old = "id: r\njoins:\n  J:\n    ingredients: []\n    tier1:\n      - {action: polars_join, right_ingredient: B}\n"
    studio, ui = click(old)
    assert any(m[1] == "error" and "not as a mapping with steps" in m[0] for m in ui.shown)
    assert studio.logic_stack.get() == []
