"""Guard on TEST CODE: no test file may build a path into `.venv` to start a process.

Why: a git worktree has no `.venv`, so a test that starts the app (or any process) from `REPO / ".venv/bin/..."`
cannot run there, and a reviewer cannot run it on a change before it is merged. A test starts the app with
`app.tests.subprocess_env.app_command(port)` (the running interpreter, `-m shiny run`) and `app_env(...)`.
This test reads the source of `app/tests/*.py`; it does not check the app.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_browser_tests_no_venv_path.py -q
"""
import re
from pathlib import Path

TESTS = Path(__file__).resolve().parent
# a path join or Path() that names .venv. Plain strings (a docstring "Run:" line, a command text given to the
# hook test) are not paths that start a process, so they are not matched.
PATTERNS = [re.compile(p) for p in (
    r"""/\s*["']\.?/?\.venv""",          # REPO / ".venv/bin/shiny", REPO / ".venv"
    r"""Path\(\s*["']\.?/?\.venv""",     # Path(".venv/bin/python")
    r"""["']\.venv["']\s*[,/)]""",        # Path(..., ".venv", "bin")
)]


def offending_lines(source: str) -> list:
    return [(n, line.strip()) for n, line in enumerate(source.splitlines(), 1)
            if any(p.search(line) for p in PATTERNS)]


def test_no_test_file_builds_a_path_into_venv():
    found = []
    for path in sorted(TESTS.glob("*.py")):
        if path.name == Path(__file__).name:
            continue
        for n, line in offending_lines(path.read_text(encoding="utf-8")):
            found.append(f"{path.name}:{n}: {line}")
    assert not found, (
        "A test must not start a process from a path into .venv (a git worktree has no .venv). "
        "Use app.tests.subprocess_env.app_command(port) and app_env(...). Found:\n" + "\n".join(found))


def test_the_guard_sees_the_old_pattern():
    old = '''proc = subprocess.Popen([str(REPO / ".venv/bin/shiny"), "run"])'''
    assert offending_lines(old)
    assert offending_lines('x = Path(REPO, ".venv", "bin", "python")')
    assert offending_lines('p = REPO / ".venv"')
    assert not offending_lines("Run: PYTHONPATH=. ./.venv/bin/python -m pytest x -q")
    assert not offending_lines("Popen(app_command(port), env=app_env())")
