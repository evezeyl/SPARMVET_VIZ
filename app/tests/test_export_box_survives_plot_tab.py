"""EXPORT-FLAKE-1: the Export panel is re-mounted on every plot tab change, which unticks "Also include a reproducibility/reimport bundle".

Cause found by running the app (browser probes, 2026-11-16): `system_tools_ui` in `app/handlers/export_handlers.py` reads
`active_home_subtab` (and `active_cfg()`), so Shiny draws the whole panel again each time the user changes the plot tab.
The checkbox is drawn with `value=False`, so a tick made before that re-draw is lost, and the download is then made with
`export_include_reproducibility` False: the zip holds `effective_run.yaml` but no `data_analysis_recipes_reproducibility/`
folder, and nothing on the screen or in the zip says why. This is the failure of
`test_export_download.py::test_the_export_records_the_seed_...` that appears about one run in three to five.

This test needs no browser: it reads the source of `system_tools_ui` and checks that the panel that holds the box does not
depend on the active plot tab or the recipe (outside an `reactive.isolate()` block). It is `xfail(strict=True)`: when the
cause is fixed (the box is mounted by a static element, or by an output that does not read these, or its value is kept), the
test passes, `strict` turns that into a failure, and the mark must be removed.

Limit: the test checks the dependency, not the whole behaviour. The behaviour (tick, change the tab, the box stays ticked and
the download holds the reproducibility folder) is what the probe `PROBE-C` of the diagnosis showed and what `test_export_download.py`
runs with the browser.
"""
import ast
from pathlib import Path

import pytest

HANDLER = Path(__file__).resolve().parents[1] / "handlers" / "export_handlers.py"
BOX_ID = "export_include_reproducibility"
RERENDER_TRIGGERS = {"active_home_subtab", "active_cfg"}


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def _is_isolate(item: ast.withitem) -> bool:
    call = item.context_expr
    return isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "isolate"


def _reads_outside_isolate(func: ast.FunctionDef) -> set:
    """The names of RERENDER_TRIGGERS that the function reads, not counting reads inside `with reactive.isolate():`."""
    found = set()

    def visit(node, isolated):
        if isinstance(node, ast.With) and any(_is_isolate(i) for i in node.items):
            isolated = True
        if not isolated:
            if isinstance(node, ast.Name) and node.id in RERENDER_TRIGGERS:
                found.add(node.id)
        for child in ast.iter_child_nodes(node):
            visit(child, isolated)

    visit(func, False)
    return found


def _mounts_the_box(func: ast.FunctionDef) -> bool:
    return any(isinstance(n, ast.Constant) and n.value == BOX_ID for n in ast.walk(func))


def test_the_panel_that_holds_the_box_reads_what_it_is_not_allowed_to_read_is_found_by_the_check():
    """The check itself can fail: a function that reads the trigger outside isolate is found, inside isolate it is not."""
    src = (
        "def a():\n    x = active_home_subtab.get()\n"
        "def b():\n    with reactive.isolate():\n        x = active_home_subtab.get()\n"
        "def c():\n    return 1\n"
    )
    tree = ast.parse(src)
    assert _reads_outside_isolate(_function(tree, "a")) == {"active_home_subtab"}
    assert _reads_outside_isolate(_function(tree, "b")) == set()
    assert _reads_outside_isolate(_function(tree, "c")) == set()


def test_the_export_panel_exists_and_holds_the_reproducibility_box():
    func = _function(ast.parse(HANDLER.read_text()), "system_tools_ui")
    assert _mounts_the_box(func), "the box is no longer mounted by system_tools_ui: update this test (EXPORT-FLAKE-1)"


@pytest.mark.xfail(
    strict=True,
    reason="EXPORT-FLAKE-1: system_tools_ui mounts the reproducibility box and reads active_home_subtab and active_cfg, so a "
           "plot tab change draws the panel again with the box unticked; a tick made before it is lost without a message",
)
def test_the_panel_that_holds_the_reproducibility_box_does_not_depend_on_the_plot_tab():
    func = _function(ast.parse(HANDLER.read_text()), "system_tools_ui")
    assert _mounts_the_box(func)
    assert _reads_outside_isolate(func) == set()
