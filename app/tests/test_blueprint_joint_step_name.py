"""The Joint Designer writes the registered name of the join action, never the old name `join`.

`build_join_step` already emitted `polars_join` (`utils.action_names.JOIN`), but `_jd_apply` rebuilt the node with the literal
`"join"`. The Joint Designer works on whatever stack is open, and a stack opened from a table's tier file (role "wrangling") can be
saved: the file then held `action: join`, a name the checker refuses (a writer of the old shape). The tap on such a step in the
stack also never reopened the Designer (`_jd_load_for_edit` compares with the registered name).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_joint_step_name.py -q
"""
import ast
from pathlib import Path

from app.handlers import blueprint_handlers
from app.tests.test_blueprint_failed_load import Val, _closure
from utils.action_names import JOIN
from utils.recipe_factory import minimal_join, minimal_recipe, minimal_schema, write_recipe
from app.modules.data_analysis_recipe_validator import checker_problems

SOURCE = Path(blueprint_handlers.__file__)


class Ui:
    def __init__(self):
        self.said = []

    def notification_show(self, message, **kwargs):
        self.said.append((kwargs.get("type"), message))


def apply_a_join(**form):
    ui = Ui()
    ws = type("WS", (), {"logic_stack": Val([]), "joint_edit_idx": Val(None)})()
    values = {"joint_left_ingredient": "samples", "joint_right_ingredient": "reads", "joint_left_keys": ["sample_id"],
              "joint_right_keys": ["sample_id"], "joint_how": "left", "joint_comment": "why", **form}
    ns = dict(vars(blueprint_handlers))
    ns.update(ui=ui, wrangle_studio=ws, input=values, safe_input=lambda i, k, d=None: i.get(k, d), _snapshot_state=lambda: None)
    fn = _closure(ast.parse(SOURCE.read_text()), "_jd_apply")
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "_jd_apply", "exec"), ns)
    ns["_jd_apply"]()
    return ws.logic_stack.get(), ui


def test_the_applied_join_step_has_the_registered_action_name():
    stack, ui = apply_a_join()
    assert [n["action"] for n in stack] == [JOIN] == ["polars_join"], ui.said
    assert stack[0]["params"]["right_ingredient"] == "reads" and stack[0]["params"]["on"] == ["sample_id"]


def test_the_step_is_tier_1_and_the_save_writes_the_registered_name():
    stack, _ = apply_a_join()
    from app.handlers.blueprint_handlers import safe_dump_recipe  # noqa: F401  (the writer of Save)
    ns = dict(vars(blueprint_handlers))
    fn = _closure(ast.parse(SOURCE.read_text()), "_serialise_component_for_save")
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "s", "exec"), ns)
    saved = ns["_serialise_component_for_save"]("wrangling", stack, "steps: []\n", "tier1")
    assert saved["steps"][0]["action"] == "polars_join"


def _recipe_with_join_step(tmp_path, action):
    samples = minimal_schema("data/samples.tsv", {"sample_id": "String"}, entity_key="sample_id", label="Samples")
    reads = minimal_schema("data/reads.tsv", {"sample_id": "String"}, label="Reads")
    step = {"action": action, "right_ingredient": "reads", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}
    recipe = minimal_recipe("r", schemas={"samples": samples, "reads": reads}, joins={"J": minimal_join(["samples", "reads"], [step])})
    return write_recipe(tmp_path / "r.yaml", recipe)


def test_the_checker_refuses_the_old_name_and_accepts_the_registered_one(tmp_path):
    """The reason for the correction: a file that holds `action: join` is refused (ST02), the registered name is accepted."""
    old = checker_problems(_recipe_with_join_step(tmp_path, "join"), "run")
    new = checker_problems(_recipe_with_join_step(tmp_path, JOIN), "run")
    assert old and "ST02" in str(old[0]) and "polars_join" in str(old[0])
    assert new == []
