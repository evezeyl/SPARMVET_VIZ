"""No code of the app reads or writes the two old header choices, and no screen text names them (slice B, point 5 of the brief).

The old choices were "Data to show" (input `tier_toggle`: Raw T1, Result T2, My view T3) and "Plot to show" (input `plot_view`: Result, My view,
Compare). Both are replaced by the mode switch and the data choice (D-0016, D-0310). This test reads every Python file of `app/` that is not a test
and every help text and style rule, and fails on:

- an identifier (a name, an attribute, an argument, a keyword, a function or class name, an imported name) `tier_toggle` or `plot_view`;
- a string literal (not a docstring) or a help text that holds `tier_toggle`, `plot_view`, "My view", "Raw (T1)", "Plot to show" or "Data to show:".

Named exception: Blueprint's own function `plot_view` (`app/modules/blueprint_plot_view.py`, imported and called in
`app/handlers/blueprint_handlers.py`) is another thing: it reads the mapping and layers of a plot node. Only the identifier `plot_view`, and only
in those two files, is allowed. The test of the scanner itself (`test_the_scan_can_fail`) writes a file with each forbidden thing and checks that it
is found.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_no_old_view_readers.py -q
"""
import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1]
REPO = APP.parent
IDENTIFIERS = ("tier_toggle", "plot_view")
TEXTS = ("tier_toggle", "plot_view", "My view", "Raw (T1)", "Plot to show", "Data to show:")
BLUEPRINT_PLOT_VIEW = {"app/modules/blueprint_plot_view.py": {"plot_view"}, "app/handlers/blueprint_handlers.py": {"plot_view"}}


def _docstring_nodes(tree: ast.AST) -> set:
    nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                nodes.add(id(first.value))
    return nodes


def scan_python(source: str, allowed: set = frozenset()) -> list:
    """The forbidden identifiers and string literals of one Python source; `allowed` is the set of identifiers the file may use."""
    tree = ast.parse(source)
    docstrings = _docstring_nodes(tree)
    found = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        elif isinstance(node, ast.keyword) and node.arg:
            names.append(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, ast.alias):
            names.extend([node.name.split(".")[-1], node.asname or ""])
        for name in names:
            if name in IDENTIFIERS and name not in allowed:
                found.append((getattr(node, "lineno", 0), f"identifier {name}"))
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            for text in TEXTS:
                if text in node.value:
                    found.append((node.lineno, f"text {text!r}"))
    return found


def _python_files() -> list:
    return sorted(p for p in APP.rglob("*.py") if "tests" not in p.relative_to(APP).parts and "__pycache__" not in p.parts)


def test_the_scan_covers_the_app_and_finds_files():
    files = _python_files()
    names = {p.relative_to(REPO).as_posix() for p in files}
    assert {"app/handlers/home_theater.py", "app/handlers/filter_and_audit_handlers.py", "app/handlers/export_handlers.py",
            "app/src/server.py", "app/modules/view_badge.py"} <= names
    assert len(files) > 40


def test_no_python_file_of_the_app_reads_or_writes_the_old_choices():
    problems = []
    for path in _python_files():
        relative = path.relative_to(REPO).as_posix()
        for line, what in scan_python(path.read_text(encoding="utf-8"), BLUEPRINT_PLOT_VIEW.get(relative, frozenset())):
            problems.append(f"{relative}:{line}: {what}")
    assert not problems, "the old header choices are still used:\n" + "\n".join(problems)


def test_no_help_text_or_style_rule_names_the_old_choices():
    problems = []
    for path in sorted((APP / "src" / "help").glob("*.md")) + [REPO / "config" / "ui" / "theme.css"]:
        text = path.read_text(encoding="utf-8")
        for needle in TEXTS:
            if needle in text:
                problems.append(f"{path.relative_to(REPO).as_posix()}: {needle!r}")
    assert not problems, "\n".join(problems)


def test_the_blueprint_exception_is_only_the_function_plot_view_in_its_two_files():
    """The exception is narrow: `tier_toggle` is never allowed, and `plot_view` only where Blueprint's own function is."""
    assert set(BLUEPRINT_PLOT_VIEW) == {"app/modules/blueprint_plot_view.py", "app/handlers/blueprint_handlers.py"}
    assert all(names == {"plot_view"} for names in BLUEPRINT_PLOT_VIEW.values())
    for relative in BLUEPRINT_PLOT_VIEW:
        assert not [w for w in scan_python((REPO / relative).read_text(encoding="utf-8"), {"plot_view"}) if "tier_toggle" in w[1]]


@pytest.mark.parametrize("source,expected", [
    ("def f(tier_toggle): return 1", "identifier tier_toggle"),
    ("x = input.plot_view()", "identifier plot_view"),
    ("f(plot_view=1)", "identifier plot_view"),
    ("from m import plot_view", "identifier plot_view"),
    ("x = safe_input(input, 'tier_toggle', 'T2')", "tier_toggle"),
    ("label = 'My view'", "My view"),
    ("label = 'Plot to show:'", "Plot to show"),
    ("label = f'Data to show: {x}'", "Data to show:"),
    ("t = 'Raw (T1) is the table'", "Raw (T1)"),
])
def test_the_scan_can_fail(source, expected):
    """MUTATION S1: a scanner that finds nothing makes every one of these fail."""
    assert any(expected in what for _, what in scan_python(source)), source


def test_a_docstring_and_a_comment_are_not_screen_text():
    assert scan_python('"""The old My view."""\ndef f():\n    """My view"""\n    # tier_toggle\n    return 1') == []


def test_the_blueprint_function_is_allowed_only_where_named():
    assert scan_python("x = plot_view(a)", {"plot_view"}) == []
    assert scan_python("x = plot_view(a)") != []
