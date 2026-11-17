"""Guard on APP and LIBRARY SOURCE: no code may name `.venv/bin/python` to start a process.

Why: a git worktree, a container or a server install has no `.venv` in the working folder; the interpreter that runs the
app is `sys.executable` (Validate failed silently for this reason). Lines of source that only print or hint a command to
a person are listed in ALLOWED with the reason. Test code is guarded by test_browser_tests_no_venv_path.py.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NEEDLE = ".venv/bin/python"
ALLOWED = {
    # (file, text on the line): reason
    ("libs/viz_gallery/src/viz_gallery/gallery_manager.py", "CONVERT_HINT"): "command text shown to a person",
}


def source_files():
    for root in [REPO / "app", *sorted((REPO / "libs").glob("*/src"))]:
        for p in root.rglob("*.py"):
            rel = p.relative_to(REPO).as_posix()
            if "/tests/" in rel or rel.startswith("app/tests/"):
                continue
            yield rel, p


def offending(rel: str, text: str):
    for n, line in enumerate(text.splitlines(), 1):
        if NEEDLE in line and not any(rel == f and key in line for (f, key) in ALLOWED):
            yield n, line.strip()


def test_no_source_file_names_a_venv_interpreter():
    found = [f"{rel}:{n}: {l}" for rel, p in source_files()
             for n, l in offending(rel, p.read_text(encoding="utf-8"))]
    assert not found, "Start a child with sys.executable, not a path into .venv:\n" + "\n".join(found)


def test_the_guard_sees_the_old_pattern():
    old = 'subprocess.run([".venv/bin/python", "scripts/x.py"])'
    assert list(offending("app/handlers/x.py", old))
    assert not list(offending("app/handlers/x.py", "subprocess.run([sys.executable, 'x'])"))
