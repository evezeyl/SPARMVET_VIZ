"""BLUEPRINT outputs that read HOME state compute only while BLUEPRINT is the open user space.

Why: a hidden BLUEPRINT output that recomputes on another recipe's table after a HOME recipe change
errors, and its stale error makes the browser drop the whole flush that carries HOME's new screen
(ADR-094, ADR-104; app/tests/test_shiny_gate_gap.py).
"""
import ast
from pathlib import Path
from types import SimpleNamespace

from app.handlers import blueprint_handlers
from app.modules import frame_widths, wrangle_studio
from app.modules.orchestrator_helpers import blueprint_is_open, safe_input

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


def _functions(path):
    return [fn for fn in ast.walk(ast.parse(path.read_text())) if isinstance(fn, ast.FunctionDef)]


def _calls_with_line(fn):
    out = []
    for stmt in fn.body:
        for n in ast.walk(stmt):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                out.append((n.lineno, n.func.id))
    return out


def test_every_output_that_reads_home_state_has_the_guard_before_the_first_read():
    checked = []
    for path in FILES:
        for fn in _functions(path):
            if not _is_reactive_function(fn):
                continue
            calls = _calls_with_line(fn)
            reads = [ln for ln, name in calls if name in HOME_READERS]
            if not reads:
                continue
            checked.append(fn.name)
            guards = [ln for ln, name in calls if name == GUARD]
            assert guards, f"{path.name}:{fn.lineno} {fn.name} reads HOME state without {GUARD}()"
            assert min(guards) < min(reads), f"{path.name}:{fn.lineno} {fn.name} reads HOME state before {GUARD}()"
    # the survey list (a function renamed or removed must be noticed here)
    assert {"processed_data", "_plot_outcome", "architect_active_table", "bp_plot_defaults_form_ui"} <= set(checked)


def test_the_two_effects_that_read_the_selector_start_with_the_guard():
    found = set()
    for path in FILES:
        for fn in _functions(path):
            if fn.name in {"sync_blueprint_mapper", "_init_wrangle_data_analysis_recipes"}:
                found.add(fn.name)
                calls = _calls_with_line(fn)
                assert calls and min(calls)[1] == GUARD, f"{fn.name}: the first call must be {GUARD}()"
    assert found == {"sync_blueprint_mapper", "_init_wrangle_data_analysis_recipes"}


# ---- behaviour: the function is cut out of its source, stripped of its decorators and run on stand-ins ----

class _Val:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value


def _run(path, module, name, nav, **stubs):
    """Run the nested function `name` with the nav input at `nav`; returns (result, names of the HOME readers called)."""
    fn = next(f for f in _functions(path) if f.name == name)
    fn.decorator_list = []
    ns = dict(vars(module))
    called = []

    def reader(label, value):
        def _read(*a, **k):
            called.append(label)
            if isinstance(value, Exception):
                raise value
            return value
        return _read

    for label, value in stubs.items():
        ns[label] = reader(label, value)
    ns.setdefault("safe_input", safe_input)
    ns.update(input=SimpleNamespace(sidebar_nav=lambda: nav),
              self=SimpleNamespace(active_viz_id=_Val("p1"), active_data_analysis_recipe_path=_Val("x.yaml")),
              wrangle_studio=SimpleNamespace(active_viz_id=_Val(None)))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
    return ns[name](), called


WS = FILES[0]
BH = FILES[1]
CASES = {
    "processed_data": (WS, wrangle_studio, {"get_base_data": None}, None),
    "_plot_outcome": (WS, wrangle_studio, {"processed_data_surgical": None, "processed_data": None}, (None, "")),
    "architect_active_table": (WS, wrangle_studio, {"processed_data_surgical": None, "processed_data": None}, None),
    "bp_plot_defaults_form_ui": (BH, blueprint_handlers, {"active_cfg": RuntimeError("stop")}, "div"),
}


def _closed_value(result, expected):
    if expected == "div":
        return result is not None and "<div" in str(result) and "plot_defaults" not in str(result)
    return result == expected


def test_closed_the_home_reader_is_not_called_and_the_no_data_value_is_returned():
    for name, (path, module, stubs, expected) in CASES.items():
        result, called = _run(path, module, name, frame_widths.HOME, **stubs)
        assert called == [], f"{name} read HOME state while BLUEPRINT was closed: {called}"
        assert _closed_value(result, expected), f"{name} returned {result!r}"


def test_open_the_home_reader_is_called():
    for name, (path, module, stubs, _expected) in CASES.items():
        _result, called = _run(path, module, name, frame_widths.BLUEPRINT, **stubs)
        assert called, f"{name} did not read HOME state while BLUEPRINT was open"


def test_the_nav_value_is_spelled_in_one_place():
    app = ROOT / "app"
    allowed = {app / "modules/frame_widths.py"}  # the one place that defines it
    for path in app.rglob("*.py"):
        if "tests" in path.relative_to(app).parts or path in allowed:
            continue
        assert '"Wrangle Studio"' not in path.read_text(), path.relative_to(ROOT)


def _run_effect(name, nav):
    """Run the effect `name`; returns what it did past the guard: the selector reads and the update_select calls."""
    fn = next(f for f in _functions(BH) if f.name == name)
    fn.decorator_list = []
    ns = dict(vars(blueprint_handlers))
    done = []

    class _In:
        def sidebar_nav(self):
            return nav

        def stored_data_analysis_recipe_selector(self):
            done.append("selector read")
            return None

    ns.setdefault("safe_input", safe_input)
    ns.update(input=_In(), ui=SimpleNamespace(update_select=lambda *a, **k: done.append("update_select")))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
    ns[name]()
    return done


def test_the_two_effects_do_nothing_while_closed_and_work_while_open():
    for name in ("sync_blueprint_mapper", "_init_wrangle_data_analysis_recipes"):
        assert _run_effect(name, frame_widths.HOME) == [], f"{name} worked while BLUEPRINT was closed"
        assert _run_effect(name, frame_widths.BLUEPRINT), f"{name} did nothing while BLUEPRINT was open"
