"""No global name used in app/handlers/blueprint_handlers.py is undefined (JOIN-PREVIEW-STRICT-1 follow-up).

A missing import (check_join_keys) was hidden by an `except Exception` in the join preview and shown to the
user as "Preview failed". This test reads the module with `ast` and checks that every name that is loaded
somewhere is bound somewhere in the file (import, assignment, def/class, parameter, loop/with/except target,
comprehension) or is a builtin. It is a coarse check: it ignores scopes, so it cannot see a name that is bound
only in another function; it never flags a name that is bound somewhere.
"""
import ast
import builtins
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "handlers" / "blueprint_handlers.py"


def _bound_names(tree):
    bound = set(dir(builtins)) | {"__file__", "__name__"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                bound.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)
    return bound


def _loaded(tree):
    return {n.id: n.lineno for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def test_every_loaded_name_is_bound_somewhere():
    tree = ast.parse(SOURCE.read_text())
    undefined = {n: l for n, l in _loaded(tree).items() if n not in _bound_names(tree)}
    assert not undefined, f"undefined names in blueprint_handlers.py (name: first line): {undefined}"


def test_the_join_preview_names_come_from_join_designer():
    tree = ast.parse(SOURCE.read_text())
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "blueprint_arch.join_designer" for a in n.names}
    assert {"check_join_keys", "compute_key_match", "build_join_step", "parse_join_step"} <= imported
