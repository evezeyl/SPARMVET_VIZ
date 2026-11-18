"""EXPORT-FLAKE-1: the Export panel is drawn again on every plot tab change, and the box "Also include a reproducibility/reimport
bundle" (`#export_include_reproducibility`, with every other field of the panel) goes back to its default.

Found by running the app (browser probes, 2026-11-16, diagnosis only): `system_tools_ui` in `app/handlers/export_handlers.py` reads
`active_home_subtab` and `active_cfg()`, so Shiny draws the whole panel again each time the plot tab changes, and the checkbox is
drawn with `value=False`. A user who ticks the box and then changes the plot tab finds it unticked; if they do not look, the download
holds `effective_run.yaml` (which says "not attempted") and no `data_analysis_recipes_reproducibility/` folder.

This was a defect a user could meet. The wire log of the failing run of
`test_export_download.py::test_the_export_records_the_seed_...` shows the same redraw (the page sent the box's default again four
seconds after the tick).

Fixed: `system_tools_ui` mounts every field of the panel once and reads the plot tab, the recipe and the session (home_state)
only inside `reactive.isolate()`. (The Scope choice that used to follow the tab is removed, D-0292: every export holds all plots.)

This test needs no browser: it reads the source of `system_tools_ui` and checks that the panel that holds the box does not depend
on the active plot tab or the recipe (outside a `reactive.isolate()` block).

Limit: it checks the dependency, not the behaviour (tick, change the tab, the box stays ticked). The behaviour is tested in the
browser by `test_export_inputs_survive_plot_tab.py`.
"""
import ast
from pathlib import Path

HANDLER = Path(__file__).resolve().parents[1] / "handlers" / "export_handlers.py"
BOX_ID = "export_include_reproducibility"
RERENDER_TRIGGERS = {"active_cfg", "home_state", "_session_key"}


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def _is_isolate(item: ast.withitem) -> bool:
    call = item.context_expr
    return isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "isolate"


def _reads_outside_isolate(func: ast.FunctionDef) -> set:
    """The names of RERENDER_TRIGGERS that the function reads reactively (a call), not counting reads inside `with reactive.isolate():`."""
    found = set()

    def visit(node, isolated):
        if isinstance(node, ast.With) and any(_is_isolate(i) for i in node.items):
            isolated = True
        if not isolated and isinstance(node, ast.Call):
            # a reactive read is a call: `active_cfg()` or `active_home_subtab.get()`; `active_home_subtab is not None`
            # reads nothing reactive
            target = node.func
            if isinstance(target, ast.Attribute) and target.attr == "get":
                target = target.value
            if isinstance(target, ast.Name) and target.id in RERENDER_TRIGGERS:
                found.add(target.id)
        for child in ast.iter_child_nodes(node):
            visit(child, isolated)

    visit(func, False)
    return found


def _mounts_the_box(func: ast.FunctionDef) -> bool:
    return any(isinstance(n, ast.Constant) and n.value == BOX_ID for n in ast.walk(func))


def test_the_panel_that_holds_the_box_reads_what_it_is_not_allowed_to_read_is_found_by_the_check():
    """The check itself can fail: a function that reads the trigger outside isolate is found, inside isolate it is not."""
    src = (
        "def a():\n    x = active_cfg().raw_config\n"
        "def b():\n    with reactive.isolate():\n        x = active_cfg().raw_config\n"
        "def c():\n    return 1\n"
        "def d():\n    return active_cfg is not None\n"
        "def e():\n    return active_cfg().raw_config\n"
        "def f():\n    return _session_key()\n"
        "def g():\n    with reactive.isolate():\n        return _session_key()\n"
        "def h():\n    return home_state.get()\n"
    )
    tree = ast.parse(src)
    assert _reads_outside_isolate(_function(tree, "a")) == {"active_cfg"}
    assert _reads_outside_isolate(_function(tree, "b")) == set()
    assert _reads_outside_isolate(_function(tree, "c")) == set()
    assert _reads_outside_isolate(_function(tree, "d")) == set()   # a comparison with None is not a reactive read
    assert _reads_outside_isolate(_function(tree, "e")) == {"active_cfg"}
    assert _reads_outside_isolate(_function(tree, "f")) == {"_session_key"}    # the session key is a read of home_state
    assert _reads_outside_isolate(_function(tree, "g")) == set()
    assert _reads_outside_isolate(_function(tree, "h")) == {"home_state"}


def test_the_export_panel_exists_and_holds_the_reproducibility_box():
    func = _function(ast.parse(HANDLER.read_text()), "system_tools_ui")
    assert _mounts_the_box(func), "the box is no longer mounted by system_tools_ui: update this test (EXPORT-FLAKE-1)"


def test_the_panel_that_holds_the_reproducibility_box_does_not_depend_on_the_plot_tab():
    func = _function(ast.parse(HANDLER.read_text()), "system_tools_ui")
    assert _mounts_the_box(func)
    assert _reads_outside_isolate(func) == set()
