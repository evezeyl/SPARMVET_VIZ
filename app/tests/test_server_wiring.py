"""server.py hands each handler exactly the keyword arguments that handler accepts.

The configuration rename (ADR-091) renames names in many files at once; a keyword that was
renamed in the caller but not in the handler fails only when a browser opens the app, so this
test checks the wiring without a browser.
"""
import ast
import importlib
import inspect
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "src" / "server.py"


def _imports():
    """Map the local name of every imported `define_*` function to its callable."""
    tree = ast.parse(SERVER.read_text())
    funcs = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app."):
            module = importlib.import_module(node.module)
            for alias in node.names:
                obj = getattr(module, alias.name, None)
                if callable(obj) and "define" in alias.name:
                    funcs[alias.asname or alias.name] = obj
    return tree, funcs


def test_every_keyword_server_passes_exists_on_the_handler():
    tree, funcs = _imports()
    assert funcs, "no define_* handler found in server.py"
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in funcs:
            params = inspect.signature(funcs[node.func.id]).parameters
            accepts_any = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())
            for kw in node.keywords:
                if kw.arg and kw.arg not in params and not accepts_any:
                    problems.append(f"{node.func.id}() got unexpected keyword '{kw.arg}'")
            required = [n for n, p in params.items()
                        if p.default is inspect.Parameter.empty and p.kind is inspect.Parameter.KEYWORD_ONLY]
            given = {kw.arg for kw in node.keywords}
            for n in required:
                if n not in given:
                    problems.append(f"{node.func.id}() lacks required keyword '{n}'")
    assert not problems, problems
