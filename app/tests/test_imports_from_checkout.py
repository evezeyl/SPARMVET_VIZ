"""Every package under test is imported from the checkout this test file lives in (task WORKTREE-TEST-IMPORTS-1).

Why: the shared .venv has editable installs that point at the main folder. In a git worktree the documented
command would test the main folder's code and report on it as if it were the worktree's.
The fix is the `pythonpath` setting of pytest in `pyproject.toml`; the last test keeps its list complete.
"""
import importlib
import importlib.util
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LIB_PACKAGES = sorted(p.name for src in (REPO / "libs").glob("*/src") for p in src.iterdir()
                      if p.is_dir() and not p.name.startswith((".", "_")) and not p.name.endswith(".egg-info"))


def _locations(module) -> list[Path]:
    """Where the package was loaded from.

    A namespace package (no __init__.py, today viz_gallery) has no __file__ and its __path__ also lists the
    main folder's copy through the editable install. Python looks in order, so what matters is the first folder and
    where each module of the checkout's folder resolves; that is what is returned for it.
    """
    if getattr(module, "__file__", None):
        return [Path(module.__file__).resolve()]
    first = Path(list(module.__path__)[0]).resolve()
    found = [first]
    for py in sorted(first.glob("*.py")):
        spec = importlib.util.find_spec(f"{module.__name__}.{py.stem}")
        found.append(Path(spec.origin).resolve())
    return found


def wrong_origin_message(name: str, found: list[Path]) -> str:
    """Plain message: which package, where it came from, what to do."""
    return (f"Package '{name}' was imported from {', '.join(map(str, found))}, outside this checkout ({REPO}). "
            f"The tests would check another copy of the code. Run pytest from the root of this checkout, with the "
            f"documented command; the `pythonpath` setting of `pyproject.toml` must list libs/*/src.")


@pytest.mark.parametrize("name", ["app", *LIB_PACKAGES])
def test_package_comes_from_this_checkout(name):
    found = _locations(importlib.import_module(name))
    assert all(REPO in p.parents for p in found), wrong_origin_message(name, found)


def test_message_names_package_path_and_remedy():
    msg = wrong_origin_message("utils", [Path("/elsewhere/utils/__init__.py")])
    assert "'utils'" in msg and "/elsewhere/utils/__init__.py" in msg and "pythonpath" in msg


def test_pythonpath_setting_lists_every_lib_source_folder():
    cfg = tomllib.loads((REPO / "pyproject.toml").read_text())
    listed = set(cfg["tool"]["pytest"]["ini_options"]["pythonpath"])
    expected = {f"libs/{p.parent.name}/src" for p in (REPO / "libs").glob("*/src")} | {"."}
    assert listed == expected, f"pythonpath differs: missing {expected - listed}, extra {listed - expected}"
