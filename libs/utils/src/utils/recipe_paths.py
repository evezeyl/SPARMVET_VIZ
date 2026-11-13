"""The paths a recipe may name: shape (PA01) and containment (PA02), pure functions.

A development path (`source.path`, `reference_file`) is read by the engine from wherever the recipe says. A recipe from
outside could name `/etc/passwd` or `../../secrets.tsv`. The shape rule refuses an absolute path, a parent folder, a
home folder and a URL; containment refuses a path that resolves outside the roots the caller allows. The checker is
pure: the caller (the app, a test) passes the roots, this module never reads the deployment.

# @deps
# provides: function:shape_problems, function:containment_problems
# consumed_by: libs/utils/tests/test_recipe_paths.py
# doc: .claude/design/recipe_format_spec.md (section 15; checks PA01, PA02; decision DEC30)
# @end_deps
"""
import os
import re
from pathlib import Path, PureWindowsPath
from typing import Iterable, List, Optional, Union

_URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*://")


def shape_problems(path) -> List[str]:
    """Why a development path is refused, as 'what is wrong. Fix: what to write'; an empty list means the shape is fine."""
    if not isinstance(path, str) or not path.strip():
        return ["the path is empty or is not text. Fix: write a path relative to the project root, for example assets/test_data/a.tsv"]
    if "\x00" in path:
        return ["the path contains a null character. Fix: write a plain path"]
    if _URL.match(path):
        return [f"{path!r} is a URL. Fix: a recipe names a file of the project, not an address"]
    if path.startswith("~"):
        return [f"{path!r} starts with ~ (a home folder). Fix: write a path relative to the project root"]
    windows = PureWindowsPath(path)
    if path.startswith("/") or path.startswith("\\") or windows.is_absolute() or windows.drive:
        return [f"{path!r} is an absolute path. Fix: write a path relative to the project root"]
    parts = re.split(r"[\\/]+", path)
    if ".." in parts:
        return [f"{path!r} goes to a parent folder (..). Fix: write a path that stays inside the project"]
    return []


def containment_problems(path: str, roots: Optional[Iterable[Union[str, Path]]], *, base: Union[str, Path]) -> List[str]:
    """Why `path` (relative to `base`) does not lie inside one of `roots`; no roots means no containment was asked for."""
    if roots is None:
        return []
    allowed = [Path(os.path.realpath(r)) for r in roots]
    resolved = Path(os.path.realpath(Path(base) / path))
    for root in allowed:
        if resolved == root or root in resolved.parents:
            return []
    return [f"{path!r} resolves outside the folders this deployment allows. Fix: put the file under one of: "
            + ", ".join(str(r) for r in allowed)]
