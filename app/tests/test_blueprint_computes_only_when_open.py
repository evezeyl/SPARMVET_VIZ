"""BLUEPRINT outputs that read HOME state compute only while BLUEPRINT is the open user space.

Why: a hidden BLUEPRINT output that recomputes on another recipe's table after a HOME recipe change
errors, and its stale error makes the browser drop the whole flush that carries HOME's new screen
(ADR-094, ADR-104; app/tests/test_shiny_gate_gap.py).
"""
import ast
from pathlib import Path

from app.modules import frame_widths
from app.modules.orchestrator_helpers import blueprint_is_open

ROOT = Path(__file__).resolve().parents[2]
FILES = [ROOT / "app/modules/wrangle_studio.py", ROOT / "app/handlers/blueprint_handlers.py"]
# what reads HOME state (or reads something that does): a function that calls one of these is guarded
HOME_READERS = {"get_base_data", "active_cfg", "processed_data"}
GUARD = "blueprint_is_open"


class _Input:
    def __init__(self, nav):
        self._nav = nav

    def sidebar_nav(self):
        if isinstance(self._nav, Exception):
            raise self._nav
        return self._nav


def test_open_only_for_the_blueprint_space():
    assert blueprint_is_open(_Input(frame_widths.BLUEPRINT)) is True


def test_closed_for_home_other_spaces_and_unset():
    for nav in (frame_widths.HOME, "Gallery", "Test Lab", None, RuntimeError("unset")):
        assert blueprint_is_open(_Input(nav)) is False


def test_closed_when_the_input_does_not_exist():
    assert blueprint_is_open(object()) is False


def _is_reactive_function(fn):
    for d in fn.decorator_list:
        text = ast.unparse(d)
        if text.startswith("render.") or text == "reactive.Calc":
            return True
    return False


def _called_names(fn):
    return {n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_every_output_that_reads_home_state_has_the_guard():
    checked = []
    for path in FILES:
        tree = ast.parse(path.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef) or not _is_reactive_function(fn):
                continue
            calls = _called_names(fn)
            if calls & HOME_READERS:
                checked.append(fn.name)
                assert GUARD in calls, f"{path.name}:{fn.lineno} {fn.name} reads HOME state without {GUARD}()"
    # the survey list (a function renamed or removed must be noticed here)
    assert {"processed_data", "_plot_outcome", "architect_active_table", "bp_plot_defaults_form_ui"} <= set(checked)


def test_the_nav_value_is_spelled_in_one_place():
    for path in FILES:
        assert '"Wrangle Studio"' not in path.read_text(), path.name
