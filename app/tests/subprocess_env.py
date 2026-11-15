"""The environment for a subprocess that must run the sources of THIS checkout.

Why: the shared `.venv` has editable installs of `libs/*` that point at the main checkout. In a git worktree a
subprocess started with `PYTHONPATH="."` would import `utils`, `transformer`... from the main checkout, so the app under
test is not the code of the worktree. The path is built from the location of the tests, never by changing `sys.path`
in the test process (`rules_runtime_environment.md` section 3).
"""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def source_path() -> str:
    """Repository root followed by every `libs/*/src` of this checkout, joined as a PYTHONPATH."""
    return os.pathsep.join([str(REPO), *(str(p) for p in sorted((REPO / "libs").glob("*/src")))])


def app_env(**extra: str) -> dict:
    """os.environ with PYTHONPATH set to this checkout's sources (a caller's PYTHONPATH is kept after them)."""
    inherited = os.environ.get("PYTHONPATH")
    path = source_path() + (os.pathsep + inherited if inherited else "")
    return {**os.environ, "PYTHONPATH": path, **extra}
